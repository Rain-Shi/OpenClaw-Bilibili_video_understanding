from __future__ import annotations

from pathlib import Path

from .config import MVPConfig
from .pipeline import run_offline_video_mvp
from .vidove_bridge import run_vidove_bridge


class UnsupportedEngineError(RuntimeError):
    pass


def run_with_engine(input_value: str, config: MVPConfig) -> Path:
    engine = getattr(config, 'engine', 'mvp')
    if engine == 'mvp':
        return run_offline_video_mvp(input_value, config)
    if engine == 'vidove':
        return run_vidove_bridge(input_value, config)
    raise UnsupportedEngineError(f'Unsupported engine: {engine}')
