from __future__ import annotations

from pathlib import Path

from .audio import build_transcript
from .config import MVPConfig
from .fusion import build_timeline
from .ingest import resolve_input
from .outputs import write_outputs
from .scene import build_simple_scenes
from .understand import summarize_timeline
from .vision import sample_frames


def run_offline_video_mvp(input_value: str, config: MVPConfig) -> Path:
    source = resolve_input(input_value, config.workdir)
    run_dir = Path(source['run_dir'])
    video_path = source['video_path']
    title = source.get('title') or Path(video_path).name

    audio_path = run_dir / 'audio.wav'
    frames_dir = run_dir / 'frames'

    transcript = build_transcript(video_path, run_dir, audio_path, config.asr_provider)
    frames = sample_frames(video_path, frames_dir, config.frame_interval_sec, config.max_frames)
    scenes = build_simple_scenes(frames)
    timeline = build_timeline(transcript, frames, scenes)
    result = summarize_timeline(title, timeline)
    write_outputs(run_dir, result)
    return run_dir
