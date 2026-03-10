from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MVPConfig:
    workdir: Path
    frame_interval_sec: int = 15
    max_frames: int = 24
    use_llm: bool = False
    asr_provider: str = 'auto'
