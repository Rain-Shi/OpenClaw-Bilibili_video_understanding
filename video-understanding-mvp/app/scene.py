from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .models import FrameEvent


@dataclass
class SceneSegment:
    scene_id: str
    start: float
    end: float
    key_frames: List[str]


def build_simple_scenes(frames: List[FrameEvent], default_window_sec: int = 60) -> List[SceneSegment]:
    if not frames:
        return []
    scenes: List[SceneSegment] = []
    bucket = []
    scene_idx = 1
    bucket_start = frames[0].timestamp
    last_ts = frames[0].timestamp
    for frame in frames:
        if frame.timestamp - bucket_start >= default_window_sec and bucket:
            scenes.append(
                SceneSegment(
                    scene_id=f'scene_{scene_idx:03d}',
                    start=bucket_start,
                    end=last_ts,
                    key_frames=[x.frame_path for x in bucket[:4]],
                )
            )
            scene_idx += 1
            bucket = []
            bucket_start = frame.timestamp
        bucket.append(frame)
        last_ts = frame.timestamp
    if bucket:
        scenes.append(
            SceneSegment(
                scene_id=f'scene_{scene_idx:03d}',
                start=bucket_start,
                end=last_ts,
                key_frames=[x.frame_path for x in bucket[:4]],
            )
        )
    return scenes
