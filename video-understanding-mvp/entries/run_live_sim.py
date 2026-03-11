from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.live.aggregator import build_chunk_summaries, build_rolling_summary
from app.live.contracts import LiveChunk
from app.live.state_store import LiveStateStore
from app.models import TimelineUnit


def _load_timeline(path: Path) -> list[TimelineUnit]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    return [TimelineUnit(**item) for item in payload]


def _chunk_timeline(stream_id: str, timeline: list[TimelineUnit], chunk_seconds: int) -> list[LiveChunk]:
    if not timeline:
        return []
    duration = max(unit.end for unit in timeline)
    chunks: list[LiveChunk] = []
    seq = 1
    start = 0.0
    while start < duration:
        end = min(duration, start + chunk_seconds)
        units = [u for u in timeline if ((u.start + u.end) / 2) >= start and ((u.start + u.end) / 2) < end]
        chunks.append(
            LiveChunk(
                stream_id=stream_id,
                chunk_id=f'chunk_{seq:04d}',
                seq=seq,
                start=start,
                end=end,
                transcript_texts=[u.speech for u in units if u.speech],
                timeline_texts=[u.speech for u in units if u.speech],
                metadata={'unit_count': len(units)},
            )
        )
        seq += 1
        start = end
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description='Pseudo-live runner using an existing offline timeline.')
    parser.add_argument('--timeline-json', required=True, help='Path to result.json or timeline json file')
    parser.add_argument('--workdir', required=True, help='Output directory for live simulation artifacts')
    parser.add_argument('--stream-id', default='live-sim', help='Logical stream id')
    parser.add_argument('--chunk-seconds', type=int, default=60, help='Window size in seconds')
    parser.add_argument('--rolling-window', type=int, default=5, help='Number of chunks for rolling summary')
    args = parser.parse_args()

    timeline_path = Path(args.timeline_json)
    payload = json.loads(timeline_path.read_text(encoding='utf-8'))
    timeline_payload = payload['timeline'] if isinstance(payload, dict) and 'timeline' in payload else payload
    timeline = [TimelineUnit(**item) for item in timeline_payload]

    run_dir = Path(args.workdir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / 'chunks').mkdir(exist_ok=True)
    (run_dir / 'summaries').mkdir(exist_ok=True)

    chunks = _chunk_timeline(args.stream_id, timeline, args.chunk_seconds)
    chunk_summaries = build_chunk_summaries(chunks)
    rolling = build_rolling_summary(args.stream_id, chunk_summaries, window_size=args.rolling_window)

    for chunk in chunks:
        (run_dir / 'chunks' / f'{chunk.chunk_id}.json').write_text(json.dumps(chunk.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    for item in chunk_summaries:
        (run_dir / 'summaries' / f'{item.chunk_id}.summary.json').write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    (run_dir / 'summaries' / 'rolling_summary.json').write_text(json.dumps(rolling.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')

    state_store = LiveStateStore(run_dir)
    state_store.save({
        'stream_id': args.stream_id,
        'chunk_seconds': args.chunk_seconds,
        'chunk_count': len(chunks),
        'rolling_window': args.rolling_window,
        'latest_rolling_summary': rolling.to_dict(),
    })

    print(f'Pseudo-live simulation complete. Outputs in: {run_dir}')


if __name__ == '__main__':
    main()
