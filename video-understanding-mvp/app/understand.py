from __future__ import annotations

from collections import Counter
from typing import List

from .models import TimelineUnit, UnderstandingResult


def summarize_timeline(title: str, timeline: List[TimelineUnit]) -> UnderstandingResult:
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
    chapters = []
    if timeline:
        for idx, unit in enumerate(timeline[:5], start=1):
            chapters.append({
                'title': f'Chapter {idx}',
                'start': unit.start,
                'end': unit.end,
                'scene_id': unit.scene_id,
            })
    keywords = ['bilibili', 'video', 'understanding', 'mvp'] + top_ocr[:6]
    return UnderstandingResult(
        title=title,
        summary=summary,
        chapters=chapters,
        keywords=keywords,
        timeline=timeline,
    )
