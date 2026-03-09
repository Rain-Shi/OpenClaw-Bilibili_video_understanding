from __future__ import annotations

from pathlib import Path


def prepare_run_dir(video_path: str, workdir: Path) -> Path:
    video = Path(video_path)
    run_dir = workdir / video.stem
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
