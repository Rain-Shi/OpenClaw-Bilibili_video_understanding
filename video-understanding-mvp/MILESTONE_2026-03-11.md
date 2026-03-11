# Milestone Summary — 2026-03-11

## What was completed in this phase

This phase moved the project from a rough offline MVP into a more credible Bilibili-oriented video-understanding prototype.

### 1. ViDove refinement was made runnable locally
- Fixed local adapter path issues so ViDove refinement can run end-to-end in the workspace layout.
- Confirmed the refined transcript can be produced after Whisper-base ASR rather than falling back immediately.
- Preserved fallback behavior when refinement fails, so the pipeline still completes with raw transcript.

### 2. Transcript quality gains were validated on real Chinese samples
Two concrete validation tracks were completed:

- **Chinese news clip**
  - `未容產品` → `美容产品`
  - `元鳥` → `原料`
  - obvious noisy phrases were normalized into much more readable Chinese

- **Bilibili tutorial clip**
  - `短期视频` → `本期视频`
  - `请问门先给个三连吗` → `请问能先给个三连吗`
  - `言言下日来` → `炎炎夏日来临`

This established that ViDove refinement is not just a one-off improvement on a single sample; it transfers into a realistic Bilibili scenario.

### 3. Benchmark flow was formalized
- Added a benchmark report path for MVP vs ViDove result comparisons.
- Recorded a dedicated refinement benchmark note: `runs/benchmarks/vidove-refinement-v1.md`
- Improved the benchmark output so it includes summary previews, chapter previews, and transcript count deltas.

### 4. Summary/chapter generation was upgraded beyond the original placeholder style
- Replaced the original summary template that mostly echoed the first few transcript lines.
- Added stronger heuristic chapter grouping and better chapter labeling.
- Reduced obviously noisy chapter titles such as filler fragments or malformed ASR leftovers.

### 5. A dedicated summary-agent layer was added after refinement
A new summarizer stage now sits after ViDove refinement and heuristic structuring.

Current summary-agent responsibilities:
- write a human-readable short summary
- generate a long summary
- generate highlights
- rewrite the full chapter title set
- rewrite the full chapter summary set

### 6. Grounding / anti-hallucination controls were added
The summary agent is no longer allowed to freely “smooth over” transcript noise.

Added controls include:
- suspect fragment filtering
- grounded transcript preview construction
- `uncertain_points` output
- `grounding_notes` output
- safe rebuilding of `long_summary` from short summary + chapter summaries + uncertainty notes
- agent fallback to heuristic mode if parsing or generation fails

This is important because the system now distinguishes between:
- what it believes is the main narrative
- what is still ambiguous or noisy in the transcript

## Current architecture at the end of this phase

```text
video input / bilibili clip
  -> Whisper-base ASR
  -> ViDove refinement
  -> timeline + heuristic chapter skeleton
  -> grounded summary agent
  -> final summary / chapters / result artifacts
```

## Validation outcome

### Bilibili tutorial sample
The pipeline now produces:
- a much cleaner refined transcript
- human-readable short summary
- full chapter title rewrite
- full chapter summary rewrite
- explicit uncertain points for noisy transcript fragments

### Bilibili commentary sample
The same architecture also worked well on a narration-heavy commentary clip:
- the main story arc was captured correctly
- chapter titles became presentation-quality
- uncertain identity/background claims were marked as uncertain rather than stated as fact

This is the strongest evidence in the phase because it shows the design generalizes beyond the tutorial case.

## What is now considered working

### Strong enough to keep as the main line
- ViDove refinement after Whisper-base ASR
- benchmark-oriented comparison workflow
- grounded summary agent
- full chapter rewrite via summary agent
- uncertainty surfacing in output artifacts

### Still rough / not final
- keyword extraction is still relatively shallow
- OCR is still mostly a hook rather than a mature integrated signal
- long-summary formatting needed polish and should still be watched on new samples
- fully automated quantitative scoring is not in place yet
- Bilibili URL / browser / live ingestion is not yet the default path for this improved summarization stack

## Recommended next phase

### Phase A — Stabilize this milestone
1. Push the current local commits to GitHub.
2. Re-run one tutorial case and one commentary case after the last safe-long-summary formatting change.
3. Update benchmark notes so they explicitly mention:
   - summary-agent status
   - uncertain-points quality
   - chapter-title / chapter-summary coverage

### Phase B — Move from local clips toward real Bilibili ingestion
1. Connect the improved pipeline to the Bilibili URL ingestion path.
2. Normalize metadata/subtitle/danmaku inputs into the same run contract.
3. Compare:
   - plain MVP
   - MVP + ViDove refinement
   - MVP + ViDove refinement + grounded summary agent

### Phase C — Prepare for the longer-term target
The end goal remains:
- Bilibili video understanding as a productizable pipeline
- then migration toward Bilibili live / rolling summarization

The right direction still looks like:
- **OpenClaw** for orchestration / automation / browser / scheduling
- **ViDove** for transcript and understanding-strengthening layers
- **summary agents** for human-readable outputs with grounding controls

## Final judgment for this phase

This phase successfully changed the project from:
- “a rough offline skeleton with noisy outputs”

into:
- “a layered prototype that can already produce usable summaries and chapter structures on real Chinese Bilibili-style content, while exposing uncertainty instead of hiding it.”
