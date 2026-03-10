from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional

from .models import TranscriptChunk


class ASRAdapterError(RuntimeError):
    pass


def _seconds_to_srt_time(secs: float) -> str:
    if secs < 0:
        secs = 0.0
    total_ms = int(round(secs * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _parse_srt(srt_text: str) -> List[TranscriptChunk]:
    blocks = [b.strip() for b in srt_text.split('\n\n') if b.strip()]
    out: List[TranscriptChunk] = []
    for block in blocks:
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        if not lines:
            continue
        if '-->' in lines[0]:
            time_line = lines[0]
            text_lines = lines[1:]
        elif len(lines) >= 2 and '-->' in lines[1]:
            time_line = lines[1]
            text_lines = lines[2:]
        else:
            continue
        start_raw, end_raw = [x.strip() for x in time_line.split('-->')]

        def to_seconds(tc: str) -> float:
            hh, mm, rest = tc.replace('.', ',').split(':')
            ss, ms = rest.split(',')
            return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0

        out.append(TranscriptChunk(start=to_seconds(start_raw), end=to_seconds(end_raw), text=' '.join(text_lines)))
    return out


def transcribe_with_whisper_cli(
    audio_path: str,
    run_dir: Path,
    model: str = 'base',
    language_hint: Optional[str] = None,
) -> List[TranscriptChunk]:
    if not shutil_which('whisper'):
        raise ASRAdapterError('whisper CLI not found in PATH')
    out_dir = run_dir / 'asr'
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        'whisper', audio_path,
        '--model', model,
        '--output_format', 'srt',
        '--output_dir', str(out_dir),
    ]
    if language_hint:
        cmd.extend(['--language', language_hint])
    subprocess.run(cmd, check=True)
    srt_path = out_dir / (Path(audio_path).stem + '.srt')
    if not srt_path.exists():
        raise ASRAdapterError(f'Expected transcript not found: {srt_path}')
    return _parse_srt(srt_path.read_text())


def load_mock_or_existing_transcript(run_dir: Path) -> List[TranscriptChunk]:
    mock_path = run_dir / 'mock_transcript.json'
    if mock_path.exists():
        data = json.loads(mock_path.read_text())
        return [TranscriptChunk(**x) for x in data]
    transcript_json = run_dir / 'transcript.json'
    if transcript_json.exists():
        data = json.loads(transcript_json.read_text())
        return [TranscriptChunk(**x) for x in data]
    return [TranscriptChunk(start=0.0, end=30.0, text='MVP placeholder transcript. Install ffmpeg + whisper to enable real ASR.')]


def persist_transcript(run_dir: Path, transcript: List[TranscriptChunk]) -> None:
    payload = [vars(x) for x in transcript]
    (run_dir / 'transcript.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    srt_lines = []
    for i, chunk in enumerate(transcript, start=1):
        srt_lines.append(str(i))
        srt_lines.append(f"{_seconds_to_srt_time(chunk.start)} --> {_seconds_to_srt_time(chunk.end)}")
        srt_lines.append(chunk.text)
        srt_lines.append('')
    (run_dir / 'transcript.srt').write_text('\n'.join(srt_lines))


def shutil_which(binary: str) -> str | None:
    import shutil
    return shutil.which(binary)
