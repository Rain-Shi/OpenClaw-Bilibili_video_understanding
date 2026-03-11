from __future__ import annotations

import re
from pathlib import Path

from .bilibili import extract_bilibili_id
from .connectors import MediaSession, choose_connector
from .models import MediaRequest


_SANITIZE_RE = re.compile(r'[^0-9A-Za-z._-]+')


def _safe_stem(name: str) -> str:
    cleaned = _SANITIZE_RE.sub('_', name).strip('._')
    return cleaned or 'input'


def prepare_run_dir(input_value: str, workdir: Path) -> Path:
    if '://' in input_value:
        bili_id = extract_bilibili_id(input_value)
        stem = bili_id or 'remote_input'
    else:
        stem = Path(input_value).stem
    run_dir = workdir / _safe_stem(stem)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_input(input_value: str, workdir: Path) -> MediaSession:
    run_dir = prepare_run_dir(input_value, workdir)
    connector = choose_connector(input_value)
    return connector.resolve(input_value, run_dir)


def build_request_for_input(input_value: str, language_hint: str | None = None) -> MediaRequest:
    if 'bilibili.com/video/' in input_value or 'b23.tv/' in input_value:
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
