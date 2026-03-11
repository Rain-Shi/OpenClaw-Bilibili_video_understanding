from __future__ import annotations

from dataclasses import dataclass


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


def _clean(text: str) -> str:
    return ' '.join((text or '').split()).strip()


def _tokenize(text: str) -> list[str]:
    text = ''.join(ch if ch.isalnum() else ' ' for ch in text.lower())
    return [tok for tok in text.split() if len(tok) >= 2]


def build_narrative_skeleton(texts: list[str]) -> NarrativeSkeleton:
    cleaned = [_clean(t) for t in texts if _clean(t)]
    if not cleaned:
        return NarrativeSkeleton([], [], [], [], [], [])
    setup = cleaned[:3]
    developments = cleaned[3:6]
    turning = [t for t in cleaned if any(k in t for k in ('原来', '其实', '后来', '警方', '调查', '结果', '但', '不过'))][:3]
    open_q = [t for t in reversed(cleaned) if any(k in t for k in ('吗', '呢', '是否', '究竟', '谁', '怎么', '？', '?'))][:2]
    windows = [
        SkeletonWindow(
            start=float(i),
            end=float(i + 1),
            texts=[text],
            token_set=set(_tokenize(text)),
            novelty=1.0,
            density=float(len(text)),
            transition=1.0 if i else 0.0,
            unresolved=1.0 if text in open_q else 0.0,
            mainline=1.0 if text in setup or text in turning else 0.5,
            score=1.0 if text in turning else 0.5,
        )
        for i, text in enumerate(cleaned[:8])
    ]
    return NarrativeSkeleton(
        setup=setup[:3],
        developments=developments[:3],
        turning_points=turning[:3],
        identity_or_goal_shift=turning[:3],
        current_open_question=open_q[:2],
        debug_windows=windows,
    )
