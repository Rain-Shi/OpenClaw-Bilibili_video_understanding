from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

from .models import TranscriptChunk


def extract_audio(video_path: str, output_audio: str) -> None:
    subprocess.run(
        [
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-ac', '1', '-ar', '16000', output_audio,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def load_mock_transcript(run_dir: Path) -> List[TranscriptChunk]:
    mock_path = run_dir / 'mock_transcript.json'
    if mock_path.exists():
        data = json.loads(mock_path.read_text())
        return [TranscriptChunk(**x) for x in data]
    return [
        TranscriptChunk(start=0.0, end=30.0, text='MVP placeholder transcript. Replace with ASR integration.'),
    ]
