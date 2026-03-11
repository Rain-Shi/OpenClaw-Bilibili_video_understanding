from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.aggregator import build_chunk_summaries, build_current_state, build_recent_recap, build_rolling_summary
from app.contracts import LiveChunk
from app.state_store import LiveStateStore


def _chunk_timeline(stream_id: str, timeline: list[dict], chunk_seconds: int) -> list[LiveChunk]:
    if not timeline:
        return []
    duration = max(item['end'] for item in timeline)
    chunks: list[LiveChunk] = []
    seq = 1
    start = 0.0
    while start < duration:
        end = min(duration, start + chunk_seconds)
        units = [u for u in timeline if ((u['start'] + u['end']) / 2) >= start and ((u['start'] + u['end']) / 2) < end]
        chunks.append(
            LiveChunk(
                stream_id=stream_id,
                chunk_id=f'chunk_{seq:04d}',
                seq=seq,
                start=start,
                end=end,
                transcript_texts=[u.get('speech', '') for u in units if u.get('speech')],
                timeline_texts=[u.get('speech', '') for u in units if u.get('speech')],
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
    timeline = payload['timeline'] if isinstance(payload, dict) and 'timeline' in payload else payload

    run_dir = Path(args.workdir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / 'chunks').mkdir(exist_ok=True)
    (run_dir / 'summaries').mkdir(exist_ok=True)

    chunks = _chunk_timeline(args.stream_id, timeline, args.chunk_seconds)
    chunk_summaries = build_chunk_summaries(chunks)
    current_state = build_current_state(args.stream_id, chunk_summaries)
    recent_recap = build_recent_recap(args.stream_id, chunk_summaries, window_size=args.rolling_window)
    rolling = build_rolling_summary(args.stream_id, chunk_summaries, window_size=args.rolling_window)

    for chunk in chunks:
        (run_dir / 'chunks' / f'{chunk.chunk_id}.json').write_text(json.dumps(chunk.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    for item in chunk_summaries:
        (run_dir / 'summaries' / f'{item.chunk_id}.summary.json').write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    (run_dir / 'summaries' / 'current_state.json').write_text(json.dumps(current_state.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    (run_dir / 'summaries' / 'recent_recap.json').write_text(json.dumps(recent_recap.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
    (run_dir / 'summaries' / 'rolling_summary.json').write_text(json.dumps(rolling.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')

    state_store = LiveStateStore(run_dir)
    state_store.save({
        'stream_id': args.stream_id,
        'chunk_seconds': args.chunk_seconds,
        'chunk_count': len(chunks),
        'rolling_window': args.rolling_window,
        'latest_current_state': current_state.to_dict(),
        'latest_recent_recap': recent_recap.to_dict(),
        'latest_rolling_summary': rolling.to_dict(),
    })

    print(f'Pseudo-live simulation complete. Outputs in: {run_dir}')


if __name__ == '__main__':
    main()
