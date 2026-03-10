from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from .asr_adapter import shutil_which
from .models import FrameEvent


class VisionDependencyError(RuntimeError):
    pass


def sample_frames(video_path: str, frames_dir: Path, interval_sec: int = 15, max_frames: int = 24) -> List[FrameEvent]:
    if not shutil_which('ffmpeg'):
        return []
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / 'frame_%04d.jpg')
    subprocess.run(
        [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f'fps=1/{interval_sec}',
            '-frames:v', str(max_frames),
            pattern,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    events: List[FrameEvent] = []
    for idx, frame in enumerate(sorted(frames_dir.glob('frame_*.jpg'))):
        ts = float(idx * interval_sec)
        events.append(FrameEvent(timestamp=ts, frame_path=str(frame), visual_tags=['frame_sample']))
    return events
