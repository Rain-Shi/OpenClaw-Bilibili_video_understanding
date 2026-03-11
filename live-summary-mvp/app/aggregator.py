from __future__ import annotations

from collections import Counter

from .contracts import ChunkSummary, CurrentState, LiveChunk, RecentRecap, RollingSummary
from .narrative_skeleton import build_narrative_skeleton

STOPWORDS = {'这个', '那个', '这里', '那里', '我们', '他们', '你们', '然后', '因为', '所以', '就是', '一个', '一种'}
EDITORIAL_MARKERS = ('帮大家', '详细理清', '不必太纠结', '这部剧', '整个剧集', '下期', '下一期', '点赞', '漏洞')
QUESTION_MARKERS = ('吗', '呢', '是否', '究竟', '为什么', '怎么', '谁', '哪', '?', '？')
TRANSITION_MARKERS = ('原来', '其实', '后来', '随后', '与此同时', '结果', '但', '不过', '然而', '警方', '调查')


def _clean(text: str) -> str:
    return ' '.join((text or '').split()).strip()


def _looks_weak(text: str) -> bool:
    text = _clean(text)
    if not text or len(text) <= 4:
        return True
    if text in STOPWORDS:
        return True
    if any(marker in text for marker in EDITORIAL_MARKERS):
        return True
    return False


def _pick_focus_points(texts: list[str], limit: int = 4) -> list[str]:
    points: list[str] = []
    for text in texts:
        text = _clean(text)
        if _looks_weak(text):
            continue
        if text not in points:
            points.append(text)
        if len(points) >= limit:
            break
    return points


def _chunk_transition_signal(texts: list[str]) -> float:
    score = 0.0
    for text in texts[:6]:
        if any(marker in text for marker in TRANSITION_MARKERS):
            score += 0.35
    return min(score, 1.0)


def _local_open_question(texts: list[str]) -> str | None:
    for text in reversed(texts):
        text = _clean(text)
        if not text or _looks_weak(text):
            continue
        if any(marker in text for marker in QUESTION_MARKERS):
            return text[:120]
    return None


def _build_chunk_micro_summary(focus: list[str], transition_signal: float, local_open_question: str | None, local_skeleton: dict) -> str:
    setup = local_skeleton.get('setup') or []
    developments = local_skeleton.get('developments') or []
    turning_points = local_skeleton.get('turning_points') or []
    current_open = local_skeleton.get('current_open_question') or []

    if setup:
        parts = [f'这一段先围绕{setup[0]}展开。']
    elif focus:
        parts = [f'这一段主要围绕{focus[0]}展开。']
    else:
        return '这一段没有抽到稳定内容。'

    if turning_points:
        parts.append(f'局部转折点更像是{turning_points[0]}。')
    elif developments:
        parts.append(f'随后推进到{developments[0]}。')
    elif len(focus) > 1:
        parts.append(f'随后提到{focus[1]}。')

    if transition_signal >= 0.5 and not turning_points:
        parts.append('这一段看起来像一个明显的推进或转折。')

    if current_open:
        parts.append(f'当前块里仍悬着的问题是：{current_open[0]}。')
    elif local_open_question:
        parts.append(f'局部未解点是：{local_open_question}。')
    return ''.join(parts)


def build_chunk_summaries(chunks: list[LiveChunk]) -> list[ChunkSummary]:
    summaries: list[ChunkSummary] = []
    for chunk in chunks:
        source_texts = chunk.timeline_texts or chunk.transcript_texts
        focus = _pick_focus_points(source_texts, limit=4)
        transition_signal = _chunk_transition_signal(source_texts)
        local_open_question = _local_open_question(source_texts)
        local_skeleton_obj = build_narrative_skeleton([text for text in source_texts if not _looks_weak(text)])
        local_skeleton = {
            'setup': local_skeleton_obj.setup[:3],
            'developments': local_skeleton_obj.developments[:3],
            'turning_points': local_skeleton_obj.turning_points[:3],
            'identity_or_goal_shift': local_skeleton_obj.identity_or_goal_shift[:3],
            'current_open_question': local_skeleton_obj.current_open_question[:2],
        }
        micro = _build_chunk_micro_summary(focus, transition_signal, local_open_question, local_skeleton)
        summaries.append(
            ChunkSummary(
                stream_id=chunk.stream_id,
                chunk_id=chunk.chunk_id,
                seq=chunk.seq,
                start=chunk.start,
                end=chunk.end,
                micro_summary=micro,
                focus_points=focus,
                transition_signal=transition_signal,
                local_open_question=local_open_question,
                local_skeleton=local_skeleton,
            )
        )
    return summaries


def build_current_state(stream_id: str, chunk_summaries: list[ChunkSummary]) -> CurrentState:
    if not chunk_summaries:
        return CurrentState(stream_id=stream_id, chunk_id='', summary='当前没有可用内容。')
    current = chunk_summaries[-1]
    mode = 'transition' if current.transition_signal >= 0.5 else 'ongoing'
    focus = current.focus_points[:3]
    if focus:
        summary = f'现在主要在讲{focus[0]}。'
        if len(focus) > 1:
            summary += f' 同时也提到{focus[1]}。'
    else:
        summary = '当前块没有抽到稳定焦点。'
    if current.local_open_question:
        summary += f' 当前悬着的问题是：{current.local_open_question}。'
    return CurrentState(
        stream_id=stream_id,
        chunk_id=current.chunk_id,
        summary=summary,
        focus_points=focus,
        mode=mode,
        open_question=current.local_open_question,
    )


def build_recent_recap(stream_id: str, chunk_summaries: list[ChunkSummary], window_size: int = 3) -> RecentRecap:
    window = chunk_summaries[-window_size:]
    all_points: list[str] = []
    transitions = 0
    local_questions: list[str] = []
    for item in window:
        all_points.extend(item.focus_points)
        if item.transition_signal >= 0.5:
            transitions += 1
        if item.local_open_question:
            local_questions.append(item.local_open_question)
    counts = Counter(all_points)
    top_points = [text for text, _ in counts.most_common(4)]
    if top_points:
        parts = [f'刚刚这几段主要围绕{top_points[0]}展开。']
        if len(top_points) > 1:
            parts.append(f'随后又转到{top_points[1]}。')
        if transitions:
            parts.append('期间出现了明显的阶段推进。')
        if local_questions:
            parts.append(f'最近留下的未解点是：{local_questions[-1]}。')
        summary = ''.join(parts)
    else:
        summary = '最近几段没有抽到稳定的 recap 焦点。'
    return RecentRecap(
        stream_id=stream_id,
        upto_seq=window[-1].seq if window else 0,
        summary=summary,
        chunk_ids=[item.chunk_id for item in window],
        focus_points=top_points,
        transitions_seen=transitions,
    )


def build_rolling_summary(stream_id: str, chunk_summaries: list[ChunkSummary], window_size: int = 5) -> RollingSummary:
    recap = build_recent_recap(stream_id, chunk_summaries, window_size=window_size)
    return RollingSummary(
        stream_id=stream_id,
        upto_seq=recap.upto_seq,
        window_size=window_size,
        summary=recap.summary,
        chunk_ids=recap.chunk_ids,
        focus_points=recap.focus_points,
    )
