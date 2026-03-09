from __future__ import annotations

from typing import List

from .models import TranscriptChunk, FrameEvent, TimelineUnit


def build_timeline(transcript: List[TranscriptChunk], frames: List[FrameEvent]) -> List[TimelineUnit]:
    timeline: List[TimelineUnit] = []
    for chunk in transcript:
        visual_notes = [f.frame_path for f in frames if chunk.start <= f.timestamp <= chunk.end]
        timeline.append(
            TimelineUnit(
                start=chunk.start,
                end=chunk.end,
                speech=chunk.text,
                visual_notes=visual_notes,
                ocr=[],
                importance=0.5,
            )
        )
    return timeline
