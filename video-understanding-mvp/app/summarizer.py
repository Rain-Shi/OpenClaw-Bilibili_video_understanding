from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import List

from .models import SummaryResult, TimelineUnit, TranscriptChunk, UnderstandingResult


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
        chapter_preview = '\n'.join(
            f'- Chapter {idx + 1}: {chapter.title} | {chapter.summary or ""}'
            for idx, chapter in enumerate(heuristic_result.chapters[:8])
        )[:2200]
        suspect_hits = sorted({frag for frag in SUSPECT_FRAGMENTS if any(frag in chunk.text for chunk in transcript)})
        chapter_count = len(heuristic_result.chapters)

        prompt = f"""
You are summarizing a Chinese video understanding run.

Title: {title}

Grounded transcript evidence:
{transcript_preview}

Heuristic chapter draft:
{chapter_preview}

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
- Keep short_summary to 2-4 sentences.
- Keep highlights concise.
- Chapter titles should be short, human-readable topic labels.
- Chapter summaries should be one concise sentence each.
- Return exactly {chapter_count} chapter_titles and exactly {chapter_count} chapter_summaries.
- Ground every claim in the transcript evidence above.
- Do not "fix" unclear facts by inventing details.
- If a phrase looks noisy, avoid elevating it into the main summary.
- Put suspicious or low-confidence material into uncertain_points instead of stating it as fact.
- If evidence is weak, prefer broader wording like “视频围绕……展开” rather than specific factual claims.
""".strip()

        response = client.responses.create(
            model=self.model,
            input=prompt,
        )
        text = getattr(response, 'output_text', '') or ''
        if not text:
            raise SummaryAgentError('OpenAI summary agent returned empty output')
        data = _parse_json_payload(text)

        return SummaryResult(
            title=title,
            short_summary=data.get('short_summary') or heuristic_result.summary,
            long_summary=data.get('long_summary'),
            keywords=heuristic_result.keywords[:10],
            highlights=list(data.get('highlights') or [])[:5],
            extra={
                'chapter_titles': _fit_length(list(data.get('chapter_titles') or []), chapter_count),
                'chapter_summaries': _fit_length(list(data.get('chapter_summaries') or []), chapter_count),
                'source': 'openai',
                'status': 'success',
                'model': self.model,
                'grounding_notes': list(data.get('grounding_notes') or [])[:6],
                'uncertain_points': list(data.get('uncertain_points') or [])[:6],
                'suspect_fragments': suspect_hits,
            },
        )


def _is_suspect_text(text: str) -> bool:
    stripped = (text or '').strip()
    if not stripped:
        return True
    if len(stripped) <= 2:
        return True
    return any(fragment in stripped for fragment in SUSPECT_FRAGMENTS)


def _build_grounded_transcript_preview(transcript: List[TranscriptChunk]) -> str:
    strong = [chunk.text.strip() for chunk in transcript if chunk.text.strip() and not _is_suspect_text(chunk.text)]
    weak = [chunk.text.strip() for chunk in transcript if chunk.text.strip() and _is_suspect_text(chunk.text)]
    selected = strong[:18] + weak[:4]
    return '\n'.join(f'- {text}' for text in selected)[:4200]


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
    (run_dir / 'agent_summary.json').write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
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
        },
        'heuristic_summary': heuristic_result.summary,
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
