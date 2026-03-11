# Entity Graph Ablation — 2026-03-11

## Context

We evaluated whether adding a lightweight `entity graph` layer improves long-form Bilibili video summarization quality enough to justify further investment.

The motivating question was **not** whether entity extraction itself looks elegant, but whether adding a graph-like intermediate representation materially improves the final summary.

## Hypothesis

A lightweight entity/relationship layer might help with:

- entity consistency
- identity / alias tracking
- relation grounding
- reducing summary drift in long narrative videos
- future live/streaming memory design

However, there was also a clear risk:

- if the graph is noisy, it may push the model toward more confident but less reliable summaries

## Scope

This experiment used a single existing sample:

- Bilibili video: `BV1odNgzpEm3`

We compared two runs with the **same base structured inputs**:

- grounded transcript preview
- chapter preview
- story beats
- narrative skeleton

The **only variable** was:

- **baseline**: no entity graph context
- **graph**: adds lightweight `entity graph context`

## Files

Ablation outputs were written to:

- `runs/ablation-baseline-vs-graph/baseline/`
- `runs/ablation-baseline-vs-graph/graph/`
- `runs/ablation-baseline-vs-graph/comparison.json`

Implementation files added/modified during this exploration:

- `app/entity_graph.py`
- `app/narrative_skeleton.py`
- `app/summarizer.py`
- `app/outputs.py`

## Lightweight Entity Graph v1

The first graph layer was intentionally lightweight and local-only:

- extracted candidate entities from timeline text
- built a small set of entity nodes
- added lightweight relation edges
- surfaced `open_questions`
- exposed graph context to the summary prompt
- wrote `entity_graph.json` when available

This was **not** a full knowledge graph system, and **not** intended as a production-quality extractor.

## Result Summary

### Baseline result

The baseline summary was relatively conservative and structurally stable.

It still had entity/identity confusion, but it did not over-commit too aggressively.

### Graph result

The graph-assisted summary became **more assertive** and produced more relation-heavy claims, but it also showed a higher tendency to:

- over-infer
- over-specify relationships
- add more brittle or risky claims
- amplify noisy structure in the graph layer

## Main conclusion

### Current verdict

**The current lightweight graph layer did not provide a stable enough improvement to justify deep investment in fine-grained entity extraction right now.**

A more precise way to state it:

> The graph direction remains promising, but this first coarse graph did not produce reliable enough gains in summary quality.

## Practical takeaway

At this stage:

- **worth keeping the idea alive**: yes
- **worth making entity extraction much more elaborate right now**: no

The current mainline should remain focused on:

1. narrative structure / skeleton quality
2. long-form summary quality
3. live-summary chunk / rolling-state design

The graph branch should be treated as a promising optional enhancement, especially for future live session memory.

## Why this still matters for live systems

Even though the current offline ablation did not justify deep immediate investment, the graph idea is still strategically useful for future live summarization because live systems need:

- persistent entity memory across time
- relation continuity
- open-question tracking
- mid-stream context recovery

So the decision is **not** “graph is useless.”

It is:

> "A rough graph does not yet improve offline summaries enough to justify detailed extraction work at this stage, but graph-style memory is still likely valuable later in live/streaming mode."

## Next-step recommendation recorded here

For now, prefer:

- continue improving narrative skeleton / summary quality
- defer heavy investment in graph extraction detail
- revisit graph memory when moving deeper into live rolling summarization

## One-line conclusion

**Entity graph as a concept is promising, but the current baseline-vs-graph experiment suggests it is not yet worth heavy extraction investment in the offline summarization path.**
