from __future__ import annotations

import json
from pathlib import Path

from .audio import build_transcript
from .config import MVPConfig
from .fusion import build_timeline
from .ingest import resolve_input
from .models import MediaRequest
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

    transcript = build_transcript(
        video_path,
        run_dir,
        audio_path,
        config.asr_provider,
        config.asr_model,
        config.language_hint,
    )
    frames = sample_frames(video_path, frames_dir, config.frame_interval_sec, config.max_frames)
    scenes = build_simple_scenes(frames)
    timeline = build_timeline(transcript, frames, scenes)
    result = summarize_timeline(title, timeline, transcript=transcript, frames=frames, metadata=session.metadata)
    result.artifacts = {
        'summary_md': str(run_dir / 'summary.md'),
        'chapters_json': str(run_dir / 'chapters.json'),
        'result_json': str(run_dir / 'result.json'),
        'transcript_json': str(run_dir / 'transcript.json'),
        'transcript_srt': str(run_dir / 'transcript.srt'),
        'audio_wav': str(audio_path),
        'frames_dir': str(frames_dir),
    }
    write_outputs(run_dir, result)
    write_run_request(run_dir, input_value, config)
    return run_dir


def write_run_request(run_dir: Path, input_value: str, config: MVPConfig) -> None:
    payload = {
        'input_value': input_value,
        'config': {
            'frame_interval_sec': config.frame_interval_sec,
            'max_frames': config.max_frames,
            'use_llm': config.use_llm,
            'asr_provider': config.asr_provider,
            'asr_model': config.asr_model,
            'language_hint': config.language_hint,
        },
    }
    (run_dir / 'request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2))
