from __future__ import annotations

from pathlib import Path

from .connectors import MediaSession, choose_connector
from .models import MediaRequest


def prepare_run_dir(input_value: str, workdir: Path) -> Path:
    stem = Path(input_value).stem if '://' not in input_value else 'remote_input'
    run_dir = workdir / stem
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_input(input_value: str, workdir: Path) -> MediaSession:
    run_dir = prepare_run_dir(input_value, workdir)
    connector = choose_connector(input_value)
    return connector.resolve(input_value, run_dir)


def build_request_for_input(input_value: str, language_hint: str | None = None) -> MediaRequest:
    if 'bilibili.com/video/' in input_value:
        source_type = 'bilibili_video'
    elif 'live.bilibili.com/' in input_value:
        source_type = 'bilibili_live'
    else:
        source_type = 'local_file'
    return MediaRequest(
        source_type=source_type,
        task_type='offline_understanding',
        input_value=input_value,
        language_hint=language_hint,
    )
