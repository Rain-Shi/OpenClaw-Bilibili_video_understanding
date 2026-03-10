# Video Understanding MVP (based on ViDove)

This MVP is designed for **offline video understanding first**, with an upgrade path toward **real-time multi-agent video watching** later.

## What it can do now
- local video input
- Bilibili URL input path (when `yt-dlp` is installed)
- audio extraction hook
- real ASR adapter hook with fallback
- frame sampling
- OCR adapter hook with fallback
- simple scene grouping
- timeline output
- summary / chapter draft output

## MVP status
This is now a **real runnable MVP path**, but some capabilities depend on local tools:

### Works today in structure
- pipeline execution
- local video processing flow
- result generation
- fallback behavior when dependencies are missing

### Becomes truly useful when these are installed
- `ffmpeg`
- `yt-dlp` (for direct Bilibili URL ingestion)
- `whisper` CLI (for real transcript generation)
- OCR stack later (optional)

## Run with local file
```bash
python3 video-understanding-mvp/entries/run_mvp.py --video_file /path/to/video.mp4
```

## Run with Bilibili URL
```bash
python3 video-understanding-mvp/entries/run_mvp.py --bilibili_url "https://www.bilibili.com/video/BV..."
```

## Recommended install for a truly usable offline MVP
```bash
sudo apt-get install ffmpeg
pip install yt-dlp openai-whisper
```

## Output files
Inside the run directory:
- `bilibili_meta.json` (if Bilibili URL ingestion is used)
- `audio.wav`
- `transcript.json`
- `transcript.srt`
- `summary.md`
- `chapters.json`
- `result.json`

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

## Why ViDove is still a good base
ViDove already gives us:
- pipeline orchestration ideas
- audio abstraction
- vision abstraction
- memory / retrieval abstractions

We are replacing its translation-centered middle stages with understanding-centered modules.

## Current architecture
```text
Bilibili URL / local video
  -> ingest
  -> local media file
  -> audio extraction + ASR
  -> frame sampling + OCR hook
  -> simple scene grouping
  -> multimodal fusion
  -> summary / chapters / result JSON
```

## Next upgrades
- real OCR backend
- better scene detection
- Bilibili subtitle / danmaku ingestion
- QA/search over transcript + visual timeline
- multi-agent planner/fusion layer
