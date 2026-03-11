# Live Summary MVP

A separate MVP track for **real-time / pseudo-live stream summarization**.

This directory is intentionally split from `video-understanding-mvp/` so live work can evolve independently without cluttering the offline Bilibili video understanding product.

## Current goal

Build a practical live-summary loop focused on what viewers actually need:

- current state
- recent recap
- highlight candidates
- stage-level summary later

## Current MVP scope

- pseudo-live simulation from an existing offline timeline/result
- chunking an existing timeline into fixed windows
- chunk-level micro summaries
- rolling summary over recent chunks
- state file output for later live session memory

## Run pseudo-live simulation

```bash
cd live-summary-mvp
PYTHONPATH=. python3 entries/run_live_sim.py \
  --timeline-json ../video-understanding-mvp/runs/test-direct-bili-url/BV1odNgzpEm3/result.json \
  --workdir runs/bv1od-live-sim \
  --stream-id bili-bv1od \
  --chunk-seconds 300 \
  --rolling-window 3
```

## Output layout

```text
runs/<name>/
  chunks/
  summaries/
  state/
```

## Design note

This is **not** the same as the offline long-video understanding stack.

Offline VOD and live summary are related, but not identical:
- offline focuses on deeper full-video understanding
- live focuses on current state, recent recap, highlights, and continuity
