from __future__ import annotations

from typing import List

from .models import TimelineUnit, UnderstandingResult


def summarize_timeline(title: str, timeline: List[TimelineUnit]) -> UnderstandingResult:
    joined = ' '.join(x.speech for x in timeline[:8]).strip() or 'No transcript available.'
    summary = (
        'Offline MVP summary generated from transcript/timeline placeholder. '
        f'Observed {len(timeline)} timeline segments. '
        f'Leading content: {joined[:500]}'
    )
    chapters = [
        {'title': 'Opening', 'start': timeline[0].start if timeline else 0, 'end': timeline[0].end if timeline else 0},
    ]
    keywords = ['bilibili', 'video', 'understanding', 'mvp']
    return UnderstandingResult(
        title=title,
        summary=summary,
        chapters=chapters,
        keywords=keywords,
        timeline=timeline,
    )
