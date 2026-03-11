# Runbook

## 1. For local file
```bash
PYTHONPATH=. python3 entries/run_mvp.py --video_file /path/to/video.mp4
```

## 2. For Bilibili URL
Requires `yt-dlp`.

```bash
PYTHONPATH=. python3 entries/run_mvp.py --bilibili_url "https://www.bilibili.com/video/BV..."
```

## 3. To unlock real transcript generation
Requires:
- `ffmpeg`
- `whisper` CLI

Suggested install:
```bash
sudo apt-get install ffmpeg
pip install yt-dlp openai-whisper
```

## 4. To test ViDove refinement manually
If OpenClaw service environment is not inheriting your keys yet, run from the same shell where your keys are exported.

```bash
export PATH="/home/rainshi/.openclaw/workspace/.local/ffmpeg:/home/rainshi/.local/bin:$PATH"
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

## 5. To test the summary agent layer
```bash
export PATH="/home/rainshi/.openclaw/workspace/.local/ffmpeg:/home/rainshi/.local/bin:$PATH"
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

## 6. To regenerate benchmark report
```bash
PYTHONPATH=. python3 entries/run_benchmark.py \
  --manifest runs/benchmark_manifest.bilibili.v1.json \
  --out-dir runs/benchmarks/bilibili-v2-status
```

默认会比较三条链：
- Plain MVP
- MVP + Refinement
- MVP + Refinement + Summary Agent

## 7. Outputs
Check the generated run directory for:
- `summary.md`
- `chapters.json`
- `result.json`
- `transcript.srt`
- `transcript.json`
- `raw_transcript.json`
- `refined_transcript.json`
- `manifest.json`
- `agent_summary.json`
  - includes grounding notes / uncertain points and full chapter title/summary rewrites when using `--summary-engine openai`

## 8. Current known limitations
- If dependencies are not installed, the app still runs but falls back to placeholder transcript / OCR hooks.
- ViDove refinement may require API keys in the same shell/session if the background service environment is not configured yet.
- The OpenAI summary agent is now grounded more tightly to transcript evidence, but it can still inherit upstream transcript noise if the source text is poor.
- Summary/chapter quality is now better than the original MVP template, but should still be benchmarked on real Bilibili samples.
