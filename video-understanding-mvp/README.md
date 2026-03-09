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
    vision.py
    fusion.py
    understand.py
    outputs.py
  entries/
    run_mvp.py
```

## MVP pipeline steps
1. `ingest.py`
   - accept local file path
   - prepare working directory
2. `audio.py`
   - extract audio via ffmpeg
   - provide transcript placeholder / ASR hook
3. `vision.py`
   - sample frames at interval
   - produce simple visual events
4. `fusion.py`
   - align transcript chunks and frame events
5. `understand.py`
   - generate summary / chapter suggestions / keywords
6. `outputs.py`
   - write `summary.md`, `timeline.json`, `chapters.json`

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
