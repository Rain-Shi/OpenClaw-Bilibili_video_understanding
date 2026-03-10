from __future__ import annotations

from pathlib import Path

from .audio import build_transcript
from .config import MVPConfig
from .fusion import build_timeline
from .ingest import prepare_run_dir
from .outputs import write_outputs
from .scene import build_simple_scenes
from .understand import summarize_timeline
from .vision import sample_frames


def run_offline_video_mvp(video_path: str, config: MVPConfig) -> Path:
    run_dir = prepare_run_dir(video_path, config.workdir)
    audio_path = run_dir / 'audio.wav'
    frames_dir = run_dir / 'frames'

    transcript = build_transcript(video_path, run_dir, audio_path, config.asr_provider)
    frames = sample_frames(video_path, frames_dir, config.frame_interval_sec, config.max_frames)
    scenes = build_simple_scenes(frames)
    timeline = build_timeline(transcript, frames, scenes)
    result = summarize_timeline(Path(video_path).name, timeline)
    write_outputs(run_dir, result)
    return run_dir
