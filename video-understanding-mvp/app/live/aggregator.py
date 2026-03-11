from __future__ import annotations

from collections import Counter

from .contracts import ChunkSummary, LiveChunk, RollingSummary


def _clean(text: str) -> str:
    return ' '.join((text or '').split()).strip()


def _pick_focus_points(texts: list[str], limit: int = 3) -> list[str]:
    points: list[str] = []
    for text in texts:
        text = _clean(text)
        if not text:
            continue
        if text not in points:
            points.append(text)
        if len(points) >= limit:
            break
    return points


def build_chunk_summaries(chunks: list[LiveChunk]) -> list[ChunkSummary]:
    summaries: list[ChunkSummary] = []
    for chunk in chunks:
        focus = _pick_focus_points(chunk.timeline_texts or chunk.transcript_texts, limit=3)
        if focus:
            micro = f"这一段先讲了{focus[0]}。"
            if len(focus) > 1:
                micro += f" 后面又提到{focus[1]}。"
        else:
            micro = '这一段没有抽到稳定内容。'
        summaries.append(
            ChunkSummary(
                stream_id=chunk.stream_id,
                chunk_id=chunk.chunk_id,
                seq=chunk.seq,
                start=chunk.start,
                end=chunk.end,
                micro_summary=micro,
                focus_points=focus,
            )
        )
    return summaries


def build_rolling_summary(stream_id: str, chunk_summaries: list[ChunkSummary], window_size: int = 5) -> RollingSummary:
    window = chunk_summaries[-window_size:]
    all_points: list[str] = []
    for item in window:
        all_points.extend(item.focus_points)
    counts = Counter(all_points)
    top_points = [text for text, _ in counts.most_common(5)]
    if top_points:
        parts = [f'过去一段时间里，主要围绕{top_points[0]}展开。']
        if len(top_points) > 1:
            parts.append(f'期间还反复提到{top_points[1]}。')
        if len(top_points) > 2:
            parts.append(f'当前讨论也涉及{top_points[2]}。')
        summary = ''.join(parts)
    else:
        summary = '过去一段时间里没有抽到稳定的讨论焦点。'
    return RollingSummary(
        stream_id=stream_id,
        upto_seq=window[-1].seq if window else 0,
        window_size=window_size,
        summary=summary,
        chunk_ids=[item.chunk_id for item in window],
        focus_points=top_points,
    )
