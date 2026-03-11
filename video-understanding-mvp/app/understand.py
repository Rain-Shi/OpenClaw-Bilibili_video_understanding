from __future__ import annotations

from collections import Counter
from typing import List

from .models import ChapterSegment, TimelineUnit, UnderstandingResult, TranscriptChunk, FrameEvent


STOPWORDS = {
    '的', '了', '呢', '啊', '吗', '呗', '就', '都', '和', '是', '在', '与', '也', '很', '这', '那',
    '一个', '一种', '我们', '你们', '他们', '然后', '因为', '所以', '这个', '那个', '就是', '如果',
    '可以', '已经', '进行', '开始', '之前', '之后', '视频', '内容', '真的', '还是', '不会', '没有',
}


def _normalize_text(text: str) -> str:
    return ' '.join((text or '').strip().split())


def _segment_topic_key(text: str) -> str:
    text = _normalize_text(text)
    if not text:
        return 'empty'
    condensed = text.replace(' ', '')
    if len(condensed) <= 12:
        return condensed
    return condensed[:12]


def _build_keywords(transcript: List[TranscriptChunk], top_ocr: List[str]) -> list[str]:
    tokens: list[str] = []
    for chunk in transcript:
        text = _normalize_text(chunk.text).replace('，', ' ').replace('。', ' ').replace('、', ' ')
        for token in text.split():
            token = token.strip()
            if len(token) < 2 or token in STOPWORDS:
                continue
            tokens.append(token)
    ranked = [token for token, _ in Counter(tokens).most_common(12)]
    keywords = ['bilibili', 'video', 'understanding', 'mvp']
    for item in ranked + top_ocr[:6]:
        if item not in keywords:
            keywords.append(item)
    return keywords[:14]


def _build_chapters(timeline: List[TimelineUnit]) -> list[ChapterSegment]:
    if not timeline:
        return []

    chapters: list[ChapterSegment] = []
    current_units: list[TimelineUnit] = [timeline[0]]
    current_scene = timeline[0].scene_id
    current_key = _segment_topic_key(timeline[0].speech)

    for unit in timeline[1:]:
        unit_key = _segment_topic_key(unit.speech)
        same_scene = unit.scene_id == current_scene
        small_gap = unit.start - current_units[-1].end <= 4.0
        same_topic = unit_key[:6] == current_key[:6]

        if len(current_units) < 4 and (same_scene or same_topic or small_gap):
            current_units.append(unit)
            if len(unit_key) > len(current_key):
                current_key = unit_key
            continue

        chapters.append(_chapter_from_units(len(chapters) + 1, current_units))
        current_units = [unit]
        current_scene = unit.scene_id
        current_key = unit_key

    chapters.append(_chapter_from_units(len(chapters) + 1, current_units))
    return chapters[:8]


def _chapter_from_units(index: int, units: List[TimelineUnit]) -> ChapterSegment:
    first = units[0]
    last = units[-1]
    summary = ' '.join(_normalize_text(unit.speech) for unit in units[:3]).strip()
    title_source = _normalize_text(first.speech).replace(' ', '')[:18] or f'Chapter {index}'
    return ChapterSegment(
        title=f'{index:02d}. {title_source}',
        start=first.start,
        end=last.end,
        scene_id=first.scene_id,
        summary=summary or None,
        importance=max((unit.importance or 0.5) for unit in units),
        extra={'unit_count': len(units)},
    )


def _build_summary(title: str, timeline: List[TimelineUnit], transcript: List[TranscriptChunk], top_ocr: List[str]) -> str:
    if not timeline:
        return f'{title}: no transcript or timeline content was produced.'

    opening = ' '.join(_normalize_text(unit.speech) for unit in timeline[:4]).strip()
    middle_start = max(0, len(timeline) // 2 - 1)
    middle = ' '.join(_normalize_text(unit.speech) for unit in timeline[middle_start:middle_start + 3]).strip()
    closing = ' '.join(_normalize_text(unit.speech) for unit in timeline[-3:]).strip()

    lines = [
        f'This run produced {len(timeline)} timeline segments and {len(transcript)} transcript chunks.',
        f'Opening focus: {opening[:220] or "(empty)"}.',
    ]
    if middle:
        lines.append(f'Midpoint content: {middle[:220]}.')
    if closing and closing != middle:
        lines.append(f'Ending content: {closing[:220]}.')
    if top_ocr:
        lines.append(f'OCR hints: {", ".join(top_ocr[:5])}.')
    return ' '.join(lines)


def summarize_timeline(
    title: str,
    timeline: List[TimelineUnit],
    transcript: List[TranscriptChunk] | None = None,
    frames: List[FrameEvent] | None = None,
    metadata: dict | None = None,
) -> UnderstandingResult:
    transcript = transcript or []
    frames = frames or []
    metadata = metadata or {}

    all_ocr = []
    for unit in timeline:
        all_ocr.extend(unit.ocr)
    top_ocr = [x for x, _ in Counter([x.strip() for x in all_ocr if x.strip()]).most_common(8)]

    summary = _build_summary(title, timeline, transcript, top_ocr)
    chapters = _build_chapters(timeline)
    keywords = _build_keywords(transcript, top_ocr)

    return UnderstandingResult(
        title=title,
        summary=summary,
        chapters=chapters,
        keywords=keywords,
        timeline=timeline,
        transcript=transcript,
        frames=frames,
        metadata=metadata,
        artifacts={},
    )
