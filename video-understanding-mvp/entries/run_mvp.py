from __future__ import annotations

import argparse
from pathlib import Path

from app.config import MVPConfig
from app.pipeline import run_offline_video_mvp


def main() -> None:
    parser = argparse.ArgumentParser(description='Offline video understanding MVP')
    parser.add_argument('--video_file', help='Path to local video file')
    parser.add_argument('--bilibili_url', help='Bilibili video URL')
    parser.add_argument('--workdir', default='./runs', help='Output working directory')
    parser.add_argument('--frame-interval', type=int, default=15)
    parser.add_argument('--max-frames', type=int, default=24)
    parser.add_argument('--asr-provider', default='auto', choices=['auto', 'whisper-cli'])
    args = parser.parse_args()

    input_value = args.video_file or args.bilibili_url
    if not input_value:
        raise SystemExit('Provide either --video_file or --bilibili_url')

    cfg = MVPConfig(
        workdir=Path(args.workdir),
        frame_interval_sec=args.frame_interval,
        max_frames=args.max_frames,
        asr_provider=args.asr_provider,
    )
    run_dir = run_offline_video_mvp(input_value, cfg)
    print(f'MVP finished. Outputs in: {run_dir}')


if __name__ == '__main__':
    main()
