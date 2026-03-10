from __future__ import annotations

from collections import Counter
from typing import List

from .models import ChapterSegment, SummaryResult, TimelineUnit, UnderstandingResult, TranscriptChunk, FrameEvent


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

    joined = ' '.join(x.speech for x in timeline[:8]).strip() or 'No transcript available.'
    all_ocr = []
    for unit in timeline:
        all_ocr.extend(unit.ocr)
    top_ocr = [x for x, _ in Counter([x.strip() for x in all_ocr if x.strip()]).most_common(8)]
    summary = (
        'Offline MVP summary generated from transcript/timeline. '
        f'Observed {len(timeline)} timeline segments. '
        f'Leading spoken content: {joined[:400]} '
        + (f'OCR hints: {", ".join(top_ocr[:5])}.' if top_ocr else '')
    )
    chapters: list[ChapterSegment] = []
    if timeline:
        for idx, unit in enumerate(timeline[:5], start=1):
            chapters.append(
                ChapterSegment(
                    title=f'Chapter {idx}',
                    start=unit.start,
                    end=unit.end,
                    scene_id=unit.scene_id,
                )
            )
    keywords = ['bilibili', 'video', 'understanding', 'mvp'] + top_ocr[:6]
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
