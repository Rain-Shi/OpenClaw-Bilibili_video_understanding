from __future__ import annotations

import argparse
from pathlib import Path

from app.config import MVPConfig
from app.pipeline import run_offline_video_mvp


def main() -> None:
    parser = argparse.ArgumentParser(description='Offline video understanding MVP')
    parser.add_argument('--video_file', required=True, help='Path to local video file')
    parser.add_argument('--workdir', default='./runs', help='Output working directory')
    parser.add_argument('--frame-interval', type=int, default=15)
    parser.add_argument('--max-frames', type=int, default=24)
    args = parser.parse_args()

    cfg = MVPConfig(
        workdir=Path(args.workdir),
        frame_interval_sec=args.frame_interval,
        max_frames=args.max_frames,
    )
    run_dir = run_offline_video_mvp(args.video_file, cfg)
    print(f'MVP finished. Outputs in: {run_dir}')


if __name__ == '__main__':
    main()
