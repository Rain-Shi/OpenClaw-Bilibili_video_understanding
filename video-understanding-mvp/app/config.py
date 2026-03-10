from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class MVPConfig:
    workdir: Path
    frame_interval_sec: int = 15
    max_frames: int = 24
    use_llm: bool = False
    asr_provider: str = 'auto'
    asr_model: str = 'base'
    language_hint: Optional[str] = None
    engine: str = 'mvp'
    vidove_repo_dir: Optional[Path] = None
