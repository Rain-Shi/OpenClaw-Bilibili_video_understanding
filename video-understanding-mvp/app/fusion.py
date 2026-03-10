from __future__ import annotations

from typing import List

from .models import TranscriptChunk, FrameEvent, TimelineUnit
from .scene import SceneSegment


def _scene_for_timestamp(scenes: List[SceneSegment], ts: float) -> SceneSegment | None:
    for scene in scenes:
        if scene.start <= ts <= scene.end:
            return scene
    return None


def build_timeline(transcript: List[TranscriptChunk], frames: List[FrameEvent], scenes: List[SceneSegment] | None = None) -> List[TimelineUnit]:
    scenes = scenes or []
    timeline: List[TimelineUnit] = []
    for chunk in transcript:
        matched_frames = [f for f in frames if chunk.start <= f.timestamp <= chunk.end]
        visual_notes = [f.frame_path for f in matched_frames]
        ocr = []
        for f in matched_frames:
            ocr.extend(f.ocr)
        scene = _scene_for_timestamp(scenes, chunk.start)
        timeline.append(
            TimelineUnit(
                start=chunk.start,
                end=chunk.end,
                speech=chunk.text,
                visual_notes=visual_notes,
                ocr=ocr,
                scene_id=scene.scene_id if scene else None,
                scene_type='sampled_scene' if scene else None,
                importance=0.5,
            )
        )
    return timeline
