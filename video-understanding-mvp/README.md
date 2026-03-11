# Video Understanding MVP (based on ViDove)

This MVP is designed for **offline video understanding first**, with an upgrade path toward **real-time multi-agent video watching** later.

## What it can do now
- local video input
- Bilibili URL input path (when `yt-dlp` is installed)
- connector abstraction layer
- audio extraction hook
- real ASR adapter hook with fallback
- optional ViDove refinement layer
- optional summary-agent layer after refinement
- grounding / anti-hallucination guardrails for agent summaries
- frame sampling
- OCR adapter hook with fallback
- simple scene grouping
- timeline output
- heuristic summary / chapter draft output
- lightweight benchmark reporting for plain MVP / refinement / summary-agent three-track comparisons

## MVP status
This is now a **real runnable MVP path**, and the current state is stronger than the original placeholder-only skeleton.

### Works today in structure
- pipeline execution
- local video processing flow
- result generation
- fallback behavior when dependencies are missing
- connector abstraction for future Bilibili live/browser modes
- raw vs refined transcript recording
- basic benchmark report generation

### Recently validated
- ViDove refinement successfully improved a Chinese news clip transcript
- ViDove refinement successfully improved a Bilibili tutorial clip transcript
- adapter path handling was fixed so local ViDove runs can complete when keys are available in the active shell

### Becomes truly useful when these are installed
- `ffmpeg`
- `yt-dlp` (for direct Bilibili URL ingestion)
- `whisper` CLI (for real transcript generation)
- ViDove local repo + required API keys for refinement mode
- OCR stack later (optional)

## Run with local file
```bash
PYTHONPATH=. python3 entries/run_mvp.py --video_file /path/to/video.mp4
```

## Run with Bilibili URL
```bash
PYTHONPATH=. python3 entries/run_mvp.py --bilibili_url "https://www.bilibili.com/video/BV..."
```

## Run with ViDove refinement
```bash
PYTHONPATH=. python3 entries/run_mvp.py \
  --video_file samples/hkcnews_china_20210203_clip120.mp4 \
  --workdir runs/test-refine-manual \
  --asr-provider whisper-cli \
  --asr-model base \
  --language zh \
  --engine mvp \
  --refinement-engine vidove \
  --summary-engine heuristic \
  --vidove-repo ../ViDove
```

## Run with summary agent
```bash
PYTHONPATH=. python3 entries/run_mvp.py \
  --video_file samples/bilibili/BV1Nb421H77B_p1_clip300.mkv \
  --workdir runs/test-bili-summary-agent \
  --asr-provider whisper-cli \
  --asr-model base \
  --language zh \
  --engine mvp \
  --refinement-engine vidove \
  --summary-engine openai \
  --vidove-repo ../ViDove
```

## Regenerate benchmark report
```bash
PYTHONPATH=. python3 entries/run_benchmark.py \
  --manifest runs/benchmark_manifest.bilibili.v1.json \
  --out-dir runs/benchmarks/bilibili-v2-status
```

当前 benchmark 默认比较三条链：
- Plain MVP
- MVP + Refinement
- MVP + Refinement + Summary Agent

## Output files
Inside the run directory:
- `bilibili_meta.json` (if Bilibili URL ingestion is used)
- `audio.wav`
- `transcript.json`
- `transcript.srt`
- `raw_transcript.json`
- `refined_transcript.json`
- `summary.md`
- `chapters.json`
- `result.json`
- `manifest.json`
- `agent_summary.json`
  - includes grounding notes, uncertain points, full chapter titles, and chapter summaries when summary-agent mode is used

## Current summary/chapter behavior
The current summary/chapter layer is still heuristic, but it is no longer just the first few lines glued together blindly.

It now:
- builds a structured summary from opening / midpoint / ending transcript regions
- groups nearby timeline units into larger chapter segments
- emits chapter titles derived from the local topic text

This is still an MVP, but it is a better base for later model-based summarization.

## OCR sidecar trick (works now)
Even without OCR installed, you can attach mock OCR per frame later by creating sidecar files like:

```text
frame_0001.jpg
frame_0001.ocr.json
```

Example:
```json
["Transformer", "Self-Attention", "Q K V"]
```

## Connector-oriented architecture
```text
Bilibili URL / local video / browser session
  -> connector layer
  -> normalized media session
  -> audio extraction + ASR
  -> optional ViDove refinement
  -> frame sampling + OCR hook
  -> scene grouping
  -> multimodal fusion
  -> summary / chapters / result JSON
```

## Important design choice
This project is intentionally moving toward a **connector-first design** rather than a brittle anti-bot-centric design.

That means:
- offline URL ingest
- browser-session ingest
- future live observation
all normalize into the same internal media session contract.

## Key docs
- `RUNBOOK.md`
- `BILIBILI_CONNECTOR_DESIGN.md`
- `adapter/VIDOVE_REUSE_MAP.md`
- `runs/benchmarks/vidove-refinement-v1.md`

## Why ViDove is still a good base
ViDove already gives us:
- pipeline orchestration ideas
- audio abstraction
- vision abstraction
- memory / retrieval abstractions

We are replacing its translation-centered middle stages with understanding-centered modules.
