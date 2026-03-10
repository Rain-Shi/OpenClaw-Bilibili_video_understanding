# Video Understanding MVP (based on ViDove)

This MVP is designed for **offline video understanding first**, with an upgrade path toward **real-time multi-agent video watching** later.

## Why build on ViDove
ViDove already provides several reusable foundations:

- `src/task.py` — pipeline orchestration pattern
- `src/audio/` — audio extraction / VAD / ASR agent abstraction
- `src/vision/` — frame analysis / vision agent abstraction
- `src/memory/` — memory and retrieval abstractions
- `src/translators/` and `src/editorial/` — LLM reasoning / refinement patterns
- `entries/run.py` — CLI-style task entrypoint

ViDove is translation-oriented. This MVP repurposes the same structure for **understanding** instead of translation.

## MVP goal
Input: local video file (offline first)

Output:
- transcript
- scene/frame notes
- summary
- chapter suggestions
- timeline JSON for later QA/search

## Current status
This repo now has a **real ASR adapter hook** with graceful fallback:
- if `ffmpeg` and `whisper` CLI are installed, it can produce a real transcript
- otherwise it falls back to `mock_transcript.json` / placeholder transcript

## Run
```bash
python3 video-understanding-mvp/entries/run_mvp.py --video_file /path/to/video.mp4
```

Optional:
```bash
python3 video-understanding-mvp/entries/run_mvp.py --video_file /path/to/video.mp4 --asr-provider whisper-cli
```

## Output files
Inside the run directory:
- `audio.wav` (if ffmpeg available)
- `transcript.json`
- `transcript.srt`
- `summary.md`
- `chapters.json`
- `result.json`

## Dependencies to unlock real processing
### Minimum for real offline MVP
- `ffmpeg`
- `whisper` CLI

Example future setup:
```bash
sudo apt-get install ffmpeg
pip install openai-whisper
```

## Suggested architecture

```text
Local video
  -> ingest
  -> audio extraction + ASR
  -> frame sampling + OCR/vision notes
  -> multimodal fusion
  -> understanding outputs (summary / chapters / timeline)
```

## What to reuse from ViDove

### Reuse directly or conceptually
- Audio agent abstraction from `src/audio/audio_agent.py`
- Vision agent abstraction from `src/vision/vision_agent.py`
- Pipeline coordinator pattern from `src/task.py`
- Memory abstraction from `src/memory/`
- CLI entry style from `entries/run.py`

### Replace / simplify
- Translation stage -> Understanding stage
- Proofreader / Editor -> Summary / Chapter / Highlight reasoning
- Subtitle rendering -> JSON / markdown report output

## Proposed new modules

```text
video-understanding-mvp/
  README.md
  ROADMAP.md
  adapter/
    VIDOVE_REUSE_MAP.md
  app/
    __init__.py
    config.py
    models.py
    pipeline.py
    ingest.py
    audio.py
    asr_adapter.py
    vision.py
    fusion.py
    understand.py
    outputs.py
  entries/
    run_mvp.py
```

## Bilibili support path
For now: offline local video first.
Later:
- add Bilibili URL resolver/downloader layer
- then feed local media into the same pipeline

## Future multi-agent path
Later, split `understand.py` into:
- speech agent
- vision agent
- fusion agent
- planner agent
- critic agent

That way the MVP stays compatible with a multi-agent future.
