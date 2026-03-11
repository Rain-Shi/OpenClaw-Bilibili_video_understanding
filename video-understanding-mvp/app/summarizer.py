from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import List

from .entity_graph import build_entity_graph
from .models import SummaryResult, TimelineUnit, TranscriptChunk, UnderstandingResult
from .narrative_skeleton import build_narrative_skeleton
from .vidove_cleaner import looks_like_editorial_leak


class SummaryAgentError(RuntimeError):
    pass


SUSPECT_FRAGMENTS = (
    '口渴得不行',
    '饮食和记忆',
    '红叶前景',
    '刷一个666',
    '地图攻略',
)


class BaseSummaryAgent:
    name = 'base'

    def summarize(
        self,
        *,
        title: str,
        transcript: List[TranscriptChunk],
        timeline: List[TimelineUnit],
        heuristic_result: UnderstandingResult,
    ) -> SummaryResult:
        raise NotImplementedError


class HeuristicSummaryAgent(BaseSummaryAgent):
    name = 'heuristic'

    def summarize(
        self,
        *,
        title: str,
        transcript: List[TranscriptChunk],
        timeline: List[TimelineUnit],
        heuristic_result: UnderstandingResult,
    ) -> SummaryResult:
        chapter_titles = [chapter.title for chapter in heuristic_result.chapters]
        chapter_summaries = [chapter.summary or '' for chapter in heuristic_result.chapters]
        highlights = [unit.speech for unit in timeline[:5] if unit.speech][:5]
        return SummaryResult(
            title=title,
            short_summary=heuristic_result.summary,
            long_summary=None,
            keywords=heuristic_result.keywords[:10],
            highlights=highlights,
            extra={
                'chapter_titles': chapter_titles,
                'chapter_summaries': chapter_summaries,
                'source': 'heuristic_passthrough',
                'status': 'success',
                'grounding_notes': ['Heuristic summary uses local deterministic rules only.'],
                'uncertain_points': [],
            },
        )


class OpenAISummaryAgent(BaseSummaryAgent):
    name = 'openai'

    def __init__(self, model: str = 'gpt-4.1-mini'):
        self.model = model
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise SummaryAgentError('OPENAI_API_KEY is required for OpenAISummaryAgent')

    def summarize(
        self,
        *,
        title: str,
        transcript: List[TranscriptChunk],
        timeline: List[TimelineUnit],
        heuristic_result: UnderstandingResult,
    ) -> SummaryResult:
        try:
            from openai import OpenAI
        except Exception as exc:
            raise SummaryAgentError(f'openai package is not available: {exc}') from exc

        client = OpenAI(api_key=self.api_key)
        transcript_preview = _build_grounded_transcript_preview(transcript)
        chapter_preview = _build_chapter_preview(heuristic_result)
        story_beats = _build_story_beats(transcript, timeline, heuristic_result)
        narrative_skeleton_obj = build_narrative_skeleton(timeline)
        narrative_skeleton = narrative_skeleton_obj.to_prompt_text()
        entity_graph_obj = build_entity_graph(heuristic_result)
        entity_graph = entity_graph_obj.to_prompt_text()
        suspect_hits = sorted({frag for frag in SUSPECT_FRAGMENTS if any(frag in chunk.text for chunk in transcript)})
        chapter_count = len(heuristic_result.chapters)

        prompt = f"""
You are summarizing a Chinese long-form narrative/explainer video.

Title: {title}

Grounded transcript evidence (sampled across beginning, middle, and end):
{transcript_preview}

Heuristic chapter draft:
{chapter_preview}

Potential story beats extracted from the full run:
{story_beats}

Narrative skeleton candidates:
{narrative_skeleton}

Entity graph context:
{entity_graph}

Potentially noisy transcript fragments to treat with caution:
{json.dumps(suspect_hits, ensure_ascii=False)}

Return strict JSON with this schema:
{{
  "short_summary": "string",
  "long_summary": "string",
  "highlights": ["string", "string", "string"],
  "chapter_titles": ["string", "string"],
  "chapter_summaries": ["string", "string"],
  "grounding_notes": ["string", "string"],
  "uncertain_points": ["string", "string"]
}}

Rules:
- Write natural Chinese.
- Do not mention pipeline internals.
- Keep short_summary to 4-6 sentences.
- short_summary must explicitly cover four parts in order: ①开场人设/设局 ②关键反转或案件出现 ③调查/真相推进 ④本期停在什么悬念或阶段。
- Prefer describing plot progression over repeating only the opening character setup.
- If the video is a story recap / case breakdown, mention the key turning point(s), identity reversal(s), and later revelations when supported.
- Use the narrative skeleton candidates as a guide for plot structure, but only keep items that are supported by the evidence.
- Use the entity graph context to keep entity references consistent; avoid merging different entities unless evidence strongly supports it.
- Keep highlights concise, but make them span different phases of the video rather than clustering at the beginning.
- Chapter titles should be short, human-readable topic labels.
- Chapter summaries should be one concise sentence each.
- Return exactly {chapter_count} chapter_titles and exactly {chapter_count} chapter_summaries.
- Ground every claim in the transcript evidence above.
- Do not fix unclear facts by inventing details.
- If a phrase looks noisy, avoid elevating it into the main summary.
- Put suspicious or low-confidence material into uncertain_points instead of stating it as fact.
- If evidence is weak, prefer broader wording like “视频围绕……展开” rather than specific factual claims.
- Avoid ending the summary with generic uploader outro/call-to-action language.
""".strip()

        response = client.responses.create(
            model=self.model,
            input=prompt,
            text={"format": {"type": "json_object"}},
        )
        text = getattr(response, 'output_text', '') or ''
        if not text:
            raise SummaryAgentError('OpenAI summary agent returned empty output')
        data = _parse_json_payload(text)

        short_summary = data.get('short_summary') or heuristic_result.summary
        chapter_titles = _fit_length(list(data.get('chapter_titles') or []), chapter_count)
        chapter_summaries = _fit_length(list(data.get('chapter_summaries') or []), chapter_count)
        uncertain_points = list(data.get('uncertain_points') or [])[:6]
        long_summary = _build_safe_long_summary(
            short_summary,
            chapter_summaries,
            uncertain_points,
            raw_long_summary=data.get('long_summary'),
        )

        return SummaryResult(
            title=title,
            short_summary=short_summary,
            long_summary=long_summary,
            keywords=heuristic_result.keywords[:10],
            highlights=list(data.get('highlights') or [])[:5],
            extra={
                'chapter_titles': chapter_titles,
                'chapter_summaries': chapter_summaries,
                'source': 'openai',
                'status': 'success',
                'model': self.model,
                'grounding_notes': list(data.get('grounding_notes') or [])[:6],
                'uncertain_points': uncertain_points,
                'suspect_fragments': suspect_hits,
                'narrative_skeleton': narrative_skeleton.splitlines(),
                'entity_graph': entity_graph_obj.to_dict(),
                'narrative_skeleton_debug': [
                    {
                        'start': w.start,
                        'end': w.end,
                        'novelty': w.novelty,
                        'density': w.density,
                        'score': w.score,
                        'texts': w.texts,
                    }
                    for w in narrative_skeleton_obj.debug_windows
                ],
                'long_summary_mode': 'safe_rebuilt',
                'raw_long_summary': data.get('long_summary'),
            },
        )


def _is_suspect_text(text: str) -> bool:
    stripped = (text or '').strip()
    if not stripped:
        return True
    if len(stripped) <= 2:
        return True
    return any(fragment in stripped for fragment in SUSPECT_FRAGMENTS)


def _pick_representative_units(timeline: List[TimelineUnit], start_ratio: float, end_ratio: float, limit: int = 3) -> list[str]:
    if not timeline:
        return []
    duration = max((unit.end for unit in timeline), default=0.0)
    start_t = duration * start_ratio
    end_t = duration * end_ratio
    selected: list[str] = []
    for unit in timeline:
        text = (unit.speech or '').strip()
        if not text or _is_suspect_text(text) or looks_like_editorial_leak(text):
            continue
        center = (unit.start + unit.end) / 2
        if start_t <= center <= end_t and text not in selected:
            selected.append(text)
        if len(selected) >= limit:
            break
    return selected


def _build_grounded_transcript_preview(transcript: List[TranscriptChunk]) -> str:
    strong = [chunk.text.strip() for chunk in transcript if chunk.text.strip() and not _is_suspect_text(chunk.text)]
    weak = [chunk.text.strip() for chunk in transcript if chunk.text.strip() and _is_suspect_text(chunk.text)]
    if not strong:
        return '\n'.join(f'- {text}' for text in weak[:8])[:4200]

    bucket_count = min(4, max(1, len(strong) // 12 + 1))
    bucket_size = max(1, len(strong) // bucket_count)
    sampled: list[str] = []
    for idx in range(bucket_count):
        start = idx * bucket_size
        end = len(strong) if idx == bucket_count - 1 else min(len(strong), (idx + 1) * bucket_size)
        bucket = strong[start:end]
        if not bucket:
            continue
        head = bucket[:3]
        mid = bucket[max(0, len(bucket) // 2 - 1): max(0, len(bucket) // 2 - 1) + 2]
        tail = bucket[-2:]
        for text in head + mid + tail:
            if text and text not in sampled:
                sampled.append(text)
    selected = sampled[:24] + [text for text in weak[:4] if text not in sampled]
    return '\n'.join(f'- {text}' for text in selected)[:5200]


def _build_chapter_preview(heuristic_result: UnderstandingResult) -> str:
    lines = []
    for idx, chapter in enumerate(heuristic_result.chapters[:12]):
        lines.append(f'- Chapter {idx + 1}: {chapter.title} | {chapter.summary or ""} | {chapter.start:.1f}-{chapter.end:.1f}s')
    return '\n'.join(lines)[:3200]


def _build_story_beats(
    transcript: List[TranscriptChunk],
    timeline: List[TimelineUnit],
    heuristic_result: UnderstandingResult,
) -> str:
    duration = 0.0
    if transcript:
        duration = max(chunk.end for chunk in transcript)
    elif timeline:
        duration = max(unit.end for unit in timeline)

    anchors = [0.1, 0.3, 0.5, 0.7, 0.9]
    beats: list[str] = []
    for anchor in anchors:
        target = duration * anchor
        best = None
        best_dist = None
        for unit in timeline:
            text = (unit.speech or '').strip()
            if not text or _is_suspect_text(text) or looks_like_editorial_leak(text):
                continue
            center = (unit.start + unit.end) / 2
            dist = abs(center - target)
            if best is None or dist < best_dist:
                best = unit
                best_dist = dist
        if best:
            beats.append(f'- Around {best.start:.0f}-{best.end:.0f}s: {best.speech}')

    for chapter in heuristic_result.chapters[:8]:
        summary = (chapter.summary or '').strip()
        if summary and summary not in ''.join(beats):
            beats.append(f'- Chapter beat: {chapter.title} => {summary}')

    deduped: list[str] = []
    seen = set()
    for beat in beats:
        if beat not in seen:
            deduped.append(beat)
            seen.add(beat)
    return '\n'.join(deduped)[:3200]


def _parse_json_payload(text: str) -> dict:
    raw = text.strip()
    candidates = [raw]
    if raw.startswith('```'):
        lines = raw.splitlines()
        if len(lines) >= 3:
            inner = '\n'.join(lines[1:-1]).strip()
            candidates.append(inner)
            if inner.startswith('json'):
                candidates.append(inner[4:].strip())
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidates.append(raw[start:end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except Exception:
            continue
    raise SummaryAgentError(f'OpenAI summary agent returned non-JSON output: {text[:400]}')


def _fit_length(values: list[str], desired: int) -> list[str]:
    values = [str(v).strip() for v in values if str(v).strip()]
    if len(values) >= desired:
        return values[:desired]
    return values + [''] * (desired - len(values))


def _clean_summary_sentence(text: str) -> str:
    text = ' '.join(str(text or '').split()).strip()
    for fragment in SUSPECT_FRAGMENTS:
        text = text.replace(fragment, '')
    text = text.replace('“”', '')
    text = text.strip('，。；,; ')
    return text


def _build_safe_long_summary(
    short_summary: str,
    chapter_summaries: list[str],
    uncertain_points: list[str],
    raw_long_summary: str | None = None,
) -> str:
    pieces: list[str] = []
    clean_short = _clean_summary_sentence(short_summary)
    if clean_short:
        if not clean_short.endswith(('。', '！', '？')):
            clean_short += '。'
        pieces.append(clean_short)

    raw_long = _clean_summary_sentence(raw_long_summary or '')
    if raw_long and raw_long not in ''.join(pieces):
        if not raw_long.endswith(('。', '！', '？')):
            raw_long += '。'
        pieces.append(raw_long)

    chapter_bits = []
    for summary in chapter_summaries[:4]:
        cleaned = _clean_summary_sentence(summary)
        if cleaned and cleaned not in chapter_bits:
            chapter_bits.append(cleaned)
    if chapter_bits:
        pieces.append('分段来看：' + '；'.join(chapter_bits) + '。')

    cleaned_uncertain = [_clean_summary_sentence(item) for item in uncertain_points if _clean_summary_sentence(item)]
    if cleaned_uncertain:
        pieces.append('需要谨慎看待的内容包括：' + '；'.join(cleaned_uncertain) + '。')

    return ''.join(pieces)[:1100]


def build_summary_agent(summary_engine: str):
    if summary_engine == 'openai':
        return OpenAISummaryAgent()
    return HeuristicSummaryAgent()


def apply_summary_agent(
    *,
    run_dir: Path,
    title: str,
    transcript: List[TranscriptChunk],
    timeline: List[TimelineUnit],
    heuristic_result: UnderstandingResult,
    summary_engine: str,
) -> SummaryResult:
    try:
        agent = build_summary_agent(summary_engine)
        result = agent.summarize(
            title=title,
            transcript=transcript,
            timeline=timeline,
            heuristic_result=heuristic_result,
        )
    except Exception as exc:
        fallback = HeuristicSummaryAgent().summarize(
            title=title,
            transcript=transcript,
            timeline=timeline,
            heuristic_result=heuristic_result,
        )
        fallback.extra = {
            **fallback.extra,
            'status': 'failed_fallback',
            'requested_engine': summary_engine,
            'failure_stage': 'summary_agent_exception',
            'failure_reason': str(exc),
        }
        result = fallback

    payload = asdict(result)
    payload['engine'] = payload.get('extra', {}).get('source', summary_engine)
    (run_dir / 'agent_summary.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


def merge_agent_summary(heuristic_result: UnderstandingResult, agent_result: SummaryResult) -> UnderstandingResult:
    heuristic_result.metadata = {
        **(heuristic_result.metadata or {}),
        'summary_agent': {
            'engine': agent_result.extra.get('source', 'unknown'),
            'status': agent_result.extra.get('status', 'success'),
            'highlights': agent_result.highlights,
            'chapter_titles': agent_result.extra.get('chapter_titles', []),
            'chapter_summaries': agent_result.extra.get('chapter_summaries', []),
            'grounding_notes': agent_result.extra.get('grounding_notes', []),
            'uncertain_points': agent_result.extra.get('uncertain_points', []),
            'suspect_fragments': agent_result.extra.get('suspect_fragments', []),
            'failure_stage': agent_result.extra.get('failure_stage'),
            'failure_reason': agent_result.extra.get('failure_reason'),
            'requested_engine': agent_result.extra.get('requested_engine', agent_result.extra.get('source')),
            'long_summary_mode': agent_result.extra.get('long_summary_mode'),
            'entity_graph': agent_result.extra.get('entity_graph'),
        },
        'heuristic_summary': heuristic_result.summary,
        'entity_graph': agent_result.extra.get('entity_graph'),
    }
    heuristic_result.summary = agent_result.short_summary or heuristic_result.summary
    chapter_titles = list(agent_result.extra.get('chapter_titles') or [])
    chapter_summaries = list(agent_result.extra.get('chapter_summaries') or [])
    for idx, chapter in enumerate(heuristic_result.chapters):
        if idx < len(chapter_titles) and chapter_titles[idx]:
            chapter.title = chapter_titles[idx]
        if idx < len(chapter_summaries) and chapter_summaries[idx]:
            chapter.summary = chapter_summaries[idx]
    return heuristic_result
