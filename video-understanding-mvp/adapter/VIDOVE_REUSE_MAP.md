# ViDove Reuse Map

## Strong reusable parts

### 1. Pipeline orchestration
- ViDove file: `src/task.py`
- Reuse idea: keep staged pipeline execution model
- New meaning:
  - VAD / ASR stays useful
  - visual cue extraction stays useful
  - translation stage becomes understanding stage

### 2. Audio abstraction
- ViDove files:
  - `src/audio/audio_agent.py`
  - `src/audio/ASR.py`
  - `src/audio/VAD.py`
- Reuse idea:
  - keep audio segmentation and transcription hooks
  - replace translation-specific assumptions with transcript output only

### 3. Vision abstraction
- ViDove files:
  - `src/vision/vision_agent.py`
  - `src/vision/gpt_vision_agent.py`
- Reuse idea:
  - keep frame extraction + visual description hooks
  - output visual events instead of translation hints

### 4. Memory / retrieval
- ViDove files:
  - `src/memory/basic_rag.py`
  - `src/memory/direct_search_RAG.py`
- Reuse idea:
  - index transcript chunks + OCR + scene notes
  - power later QA and retrieval

## Weakly reusable / should be replaced
- `src/translators/*` -> replace with understanding/summarization modules
- `src/editorial/*` -> replace with chapter/highlight/critic modules
- SRT rendering -> replace with summary/timeline output

## Suggested migration approach
1. Keep ViDove as upstream reference codebase
2. Build a new understanding-oriented app alongside it
3. Copy or wrap only the abstractions that clearly fit
4. Avoid forcing translation-centric classes into the MVP
