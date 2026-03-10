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
    session = resolve_input(input_value, config.workdir)
    run_dir = Path(session.run_dir or config.workdir)

    if not session.video_path:
        raise RuntimeError('This connector did not provide a local video_path. Offline MVP currently requires local media.')

    video_path = session.video_path
    title = session.title or Path(video_path).name

    audio_path = run_dir / 'audio.wav'
    frames_dir = run_dir / 'frames'

    transcript = build_transcript(video_path, run_dir, audio_path, config.asr_provider)
    frames = sample_frames(video_path, frames_dir, config.frame_interval_sec, config.max_frames)
    scenes = build_simple_scenes(frames)
    timeline = build_timeline(transcript, frames, scenes)
    result = summarize_timeline(title, timeline)
    write_outputs(run_dir, result)
    return run_dir
