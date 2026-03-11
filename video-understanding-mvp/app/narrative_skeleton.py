from __future__ import annotations

from dataclasses import dataclass

from .models import TimelineUnit
from .vidove_cleaner import looks_like_editorial_leak


@dataclass
class SkeletonWindow:
    start: float
    end: float
    texts: list[str]
    token_set: set[str]
    novelty: float
    density: float
    transition: float
    unresolved: float
    mainline: float
    score: float


@dataclass
class NarrativeSkeleton:
    setup: list[str]
    developments: list[str]
    turning_points: list[str]
    identity_or_goal_shift: list[str]
    current_open_question: list[str]
    debug_windows: list[SkeletonWindow]

    def to_prompt_text(self) -> str:
        lines: list[str] = [
            'Setup:',
            *[f'- {x}' for x in self.setup],
            'Developments:',
            *[f'- {x}' for x in self.developments],
            'Turning points:',
            *[f'- {x}' for x in self.turning_points],
            'Identity/goal shifts:',
            *[f'- {x}' for x in self.identity_or_goal_shift],
            'Current open questions / stopping point:',
            *[f'- {x}' for x in self.current_open_question],
        ]
        return '\n'.join(lines)[:3600]


def _is_valid_text(text: str) -> bool:
    text = (text or '').strip()
    if not text or len(text) <= 4:
        return False
    if looks_like_editorial_leak(text):
        return False
    return True


def _tokenize(text: str) -> list[str]:
    text = ''.join(ch if ch.isalnum() else ' ' for ch in text.lower())
    return [tok for tok in text.split() if len(tok) >= 2]


def _windowize(timeline: list[TimelineUnit], max_windows: int = 12) -> list[SkeletonWindow]:
    valid = [u for u in timeline if _is_valid_text(u.speech)]
    if not valid:
        return []
    duration = max(u.end for u in valid)
    window_count = min(max_windows, max(5, len(valid) // 20 + 1))
    span = max(duration / window_count, 1.0)
    windows: list[SkeletonWindow] = []
    for idx in range(window_count):
        start = idx * span
        end = duration if idx == window_count - 1 else (idx + 1) * span
        texts: list[str] = []
        for u in valid:
            center = (u.start + u.end) / 2
            if start <= center <= end:
                t = u.speech.strip()
                if t not in texts:
                    texts.append(t)
        joined = ' '.join(texts)
        token_set = set(_tokenize(joined))
        density = len(joined) / max(end - start, 1.0)
        windows.append(SkeletonWindow(start, end, texts[:6], token_set, 0.0, density, 0.0, 0.0, 0.0, 0.0))

    prev_tokens: set[str] = set()
    for idx, w in enumerate(windows):
        if w.token_set:
            new_tokens = w.token_set - prev_tokens
            w.novelty = len(new_tokens) / max(len(w.token_set), 1)
        if idx > 0:
            prev = windows[idx - 1]
            union = len(w.token_set | prev.token_set) or 1
            overlap = len(w.token_set & prev.token_set)
            w.transition = 1.0 - (overlap / union)
        prev_tokens |= w.token_set

    return windows


def _attach_future_resolution_scores(windows: list[SkeletonWindow]) -> None:
    for idx, w in enumerate(windows):
        future = windows[idx + 1:]
        if future and w.token_set:
            future_union = set().union(*(fw.token_set for fw in future))
            resolved_overlap = len(w.token_set & future_union) / max(len(w.token_set), 1)
            w.unresolved = 1.0 - resolved_overlap
        else:
            w.unresolved = 1.0


def _attach_mainline_scores(windows: list[SkeletonWindow]) -> None:
    if not windows:
        return
    setup_tokens = set().union(*(w.token_set for w in windows[:2]))
    turning_seed = sorted(windows[1:-1] or windows, key=lambda w: (w.transition, w.novelty, w.density), reverse=True)[:3]
    turning_tokens = set().union(*(w.token_set for w in turning_seed))
    mainline_seed = setup_tokens | turning_tokens
    for w in windows:
        if not w.token_set:
            w.mainline = 0.0
            continue
        overlap = len(w.token_set & mainline_seed)
        w.mainline = overlap / max(len(w.token_set), 1)
        w.score = (
            w.novelty * 0.22
            + w.transition * 0.28
            + min(w.density / 120.0, 1.0) * 0.08
            + w.unresolved * 0.12
            + w.mainline * 0.30
        )


def _pick_texts_from_windows(windows: list[SkeletonWindow], limit: int, exclude: set[str] | None = None) -> list[str]:
    exclude = exclude or set()
    chosen: list[str] = []
    for w in windows:
        for text in w.texts:
            if text not in chosen and text not in exclude:
                chosen.append(text)
            if len(chosen) >= limit:
                return chosen
    return chosen[:limit]


def _best_turning_windows(windows: list[SkeletonWindow]) -> list[SkeletonWindow]:
    core = windows[1:-1] or windows
    return sorted(core, key=lambda w: (w.transition, w.mainline, w.score), reverse=True)[:3]


def _best_open_question_windows(windows: list[SkeletonWindow]) -> list[SkeletonWindow]:
    tail = windows[max(0, len(windows) - 5):]
    ranked = sorted(tail, key=lambda w: (w.mainline, w.unresolved, w.transition, w.score), reverse=True)
    return ranked[:2]


def build_narrative_skeleton(timeline: list[TimelineUnit]) -> NarrativeSkeleton:
    windows = _windowize(timeline)
    if not windows:
        return NarrativeSkeleton([], [], [], [], [], [])

    _attach_future_resolution_scores(windows)
    _attach_mainline_scores(windows)

    setup_windows = windows[:2]
    turning_windows = _best_turning_windows(windows)
    open_windows = _best_open_question_windows(windows)

    setup = _pick_texts_from_windows(setup_windows, 4)
    turning_points = _pick_texts_from_windows(turning_windows, 5, exclude=set(setup))

    developments_pool = sorted(
        [w for w in windows[1:-1] if w not in turning_windows],
        key=lambda w: (w.mainline, w.score, w.density),
        reverse=True,
    )
    developments = _pick_texts_from_windows(developments_pool, 5, exclude=set(setup) | set(turning_points))

    identity_or_goal_shift = _pick_texts_from_windows(turning_windows, 4, exclude=set(setup))
    current_open_question = _pick_texts_from_windows(open_windows, 3, exclude=set(setup) | set(turning_points[:2]))
    if not current_open_question:
        current_open_question = _pick_texts_from_windows(open_windows, 3)

    return NarrativeSkeleton(
        setup=setup,
        developments=developments,
        turning_points=turning_points,
        identity_or_goal_shift=identity_or_goal_shift,
        current_open_question=current_open_question,
        debug_windows=windows,
    )
