from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .bilibili import is_bilibili_url, resolve_bilibili_to_local


def prepare_run_dir(input_value: str, workdir: Path) -> Path:
    stem = Path(input_value).stem if '://' not in input_value else 'remote_input'
    run_dir = workdir / stem
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_input(input_value: str, workdir: Path) -> Dict[str, Any]:
    run_dir = prepare_run_dir(input_value, workdir)
    if is_bilibili_url(input_value):
        payload = resolve_bilibili_to_local(input_value, run_dir)
        payload['run_dir'] = str(run_dir)
        return payload
    payload = {
        'title': Path(input_value).name,
        'video_path': input_value,
        'source': 'local_file',
        'run_dir': str(run_dir),
    }
    return payload
