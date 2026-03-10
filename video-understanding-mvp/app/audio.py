from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

from .asr_adapter import (
    ASRAdapterError,
    load_mock_or_existing_transcript,
    persist_transcript,
    shutil_which,
    transcribe_with_whisper_cli,
)
from .models import TranscriptChunk


class AudioDependencyError(RuntimeError):
    pass


def extract_audio(video_path: str, output_audio: str) -> None:
    if not shutil_which('ffmpeg'):
        raise AudioDependencyError('ffmpeg not found in PATH')
    subprocess.run(
        [
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-ac', '1', '-ar', '16000', output_audio,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def build_transcript(
    video_path: str,
    run_dir: Path,
    audio_path: Path,
    asr_provider: str = 'auto',
    asr_model: str = 'base',
    language_hint: Optional[str] = None,
) -> List[TranscriptChunk]:
    try:
        extract_audio(video_path, str(audio_path))
    except AudioDependencyError:
        transcript = load_mock_or_existing_transcript(run_dir)
        persist_transcript(run_dir, transcript)
        return transcript

    transcript: List[TranscriptChunk]
    try:
        if asr_provider in ('auto', 'whisper-cli'):
            transcript = transcribe_with_whisper_cli(
                str(audio_path),
                run_dir,
                model=asr_model,
                language_hint=language_hint,
            )
        else:
            raise ASRAdapterError(f'Unsupported ASR provider: {asr_provider}')
    except ASRAdapterError:
        transcript = load_mock_or_existing_transcript(run_dir)

    persist_transcript(run_dir, transcript)
    return transcript
