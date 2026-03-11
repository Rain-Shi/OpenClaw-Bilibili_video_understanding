# Video Understanding MVP (based on ViDove)

A practical **offline Bilibili / long-video understanding MVP** that has already moved beyond placeholder structure and into a usable product-style prototype.

This project is the **VOD / offline understanding track**.
A separate live track now exists at the repo root as `live-summary-mvp/`.

---

## What this project already achieved

### Core pipeline is real and runnable
- local video input
- Bilibili URL input path via `yt-dlp`
- connector abstraction layer
- audio extraction
- Whisper ASR integration
- optional ViDove refinement
- optional summary-agent layer
- timeline / chapters / summary / result artifacts

### Recent validated results
- Bilibili URL ingestion works end-to-end
- ViDove refinement works on real Chinese Bilibili samples
- summary-agent works with OpenAI after environment fixes
- narrative skeleton improves long-form summary structure
- baseline vs graph ablation was completed and documented

### Product-level conclusion so far
This is already a **satisfying Bilibili video understanding product direction**:
- worth keeping
- worth upgrading later
- should remain the offline/VOD foundation

---

## Current product structure

```text
Bilibili URL / local file
        ↓
connector layer
        ↓
normalized media session
        ↓
audio extraction + ASR
        ↓
optional ViDove refinement
        ↓
frame sampling + OCR hook
        ↓
scene grouping + timeline
        ↓
summary / chapters / result JSON
        ↓
optional summary-agent rewrite
```

---

## Architecture flowchart

```text
[Input]
  ├─ Local video file
  └─ Bilibili URL
        ↓
[Connector Layer]
        ↓
[Normalized Media Session]
        ↓
[Audio + ASR]
  ├─ Whisper CLI
  └─ fallback path
        ↓
[Refinement Layer]
  ├─ none
  └─ ViDove refinement
        ↓
[Understanding Layer]
  ├─ timeline building
  ├─ scene grouping
  ├─ heuristic chapters
  └─ structured summary draft
        ↓
[Summary Agent Layer]
  ├─ heuristic passthrough
  └─ OpenAI summary agent
        ↓
[Artifacts]
  ├─ raw_transcript.json
  ├─ refined_transcript.json
  ├─ summary.md
  ├─ chapters.json
  ├─ result.json
  ├─ manifest.json
  └─ agent_summary.json
```

---

## Highlighted experiment results

### 1. Bilibili + ViDove path
We validated that the following path works on real Bilibili content:

```text
Bilibili URL
  → yt-dlp ingest
  → Whisper ASR
  → ViDove refinement
  → summary / chapter generation
```

That means this is no longer just a local-file toy skeleton.

### 2. Summary-agent direction
We improved the summary path with:
- transcript coverage beyond the opening only
- long-form narrative skeleton
- stronger stopping-point handling
- grounding / uncertainty notes

### 3. Entity graph ablation
We also tested whether a lightweight graph layer materially improves long-form summary quality.

**Result:** promising idea, but not yet strong enough to justify heavy extraction investment on the offline path.

#### Short conclusion
- keep the idea alive
- do **not** over-invest in fine-grained graph extraction right now
- keep mainline focus on summary quality and live-summary evolution

#### Baseline vs Graph snapshot

**Baseline short summary**
> 故事开头描述了一位衣着邋遢的女人莎拉·金，在奢侈品店随意挑选价值动辄相当于一套房子的名牌包。随后警方调查发现她其实是韩国某国产化妆品品牌总经理郑汝珍，且她涉及一宗身份复杂的死亡案件。随着调查深入，发现所谓的欧洲王室御用贡品实际上是莎拉自创的山寨品牌，牵扯出穆加希自杀案，两案疑似关联。视频最后以警方决定将两案并案调查为悬念，揭示莎拉真实身份和背后秘密尚未揭开。

**Graph short summary**
> 故事开场于一家金碧辉煌的奢侈品店，一位衣着邋遢的女人莎拉·金随意挑选价值动辄相当于一套房子的名牌包，引起关注。随后案件反转，警方发现莎拉疑似身份造假，她实为虚构人物，涉足以150亿投资金额打造的山寨奢侈品品牌“巴杜奥”，而郑汝珍被牵涉其中，面临严重困境。随着警方深入调查，发现郑汝珍与莎拉的关系极为复杂，背后牵扯绑架、勒索等罪案以及身份盗用，真相比表面惊悚。现阶段，警方决定将穆加希与莎拉案合案调查，悬念在于两人竟是同一人，引发对整个事件的新一轮疑问和推理。

**Interpretation:** graph made the model more assertive, but not more reliably correct.

Detailed note:
- `docs/ENTITY_GRAPH_ABLATION_2026-03-11.md`
- `runs/ablation-baseline-vs-graph/`

---

## MVP status

This is now a **real runnable MVP path**, stronger than the original placeholder-only skeleton.

### Works today in structure
- pipeline execution
- local video processing flow
- Bilibili URL processing flow
- result generation
- fallback behavior when dependencies are missing
- raw vs refined transcript recording
- benchmark report generation

### Becomes truly useful when these are installed
- `ffmpeg`
- `yt-dlp`
- `whisper` CLI
- local ViDove repo + required API keys
- OCR stack later (optional)

---

## Run with local file
```bash
PYTHONPATH=. python3 entries/run_mvp.py --video_file /path/to/video.mp4
```

## Run with Bilibili URL
```bash
PYTHONPATH=. python3 entries/run_mvp.py \
  --bilibili_url "https://www.bilibili.com/video/BV..." \
  --asr-provider whisper-cli \
  --refinement-engine vidove \
  --summary-engine openai \
  --vidove-repo ../ViDove
```

Recommended strongest path today:
- Whisper ASR
- ViDove refinement
- grounded summary agent

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

Current benchmark tracks:
- Plain MVP
- MVP + Refinement
- MVP + Refinement + Summary Agent

---

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

---

## Design choice
This project is intentionally moving toward a **connector-first design** rather than a brittle anti-bot-centric design.

That means:
- offline URL ingest
- browser-session ingest
- future live observation
all normalize into the same internal media session contract.

---

## Key docs
- `RUNBOOK.md`
- `BILIBILI_CONNECTOR_DESIGN.md`
- `adapter/VIDOVE_REUSE_MAP.md`
- `runs/benchmarks/vidove-refinement-v1.md`
- `docs/ENTITY_GRAPH_ABLATION_2026-03-11.md`

---

## Why ViDove is still a good base
ViDove already gives us:
- pipeline orchestration ideas
- audio abstraction
- vision abstraction
- memory / retrieval abstractions

We are replacing its translation-centered middle stages with understanding-centered modules.
