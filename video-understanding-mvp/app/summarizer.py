from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import List

from .models import ChapterSegment, SummaryResult, TimelineUnit, TranscriptChunk, UnderstandingResult


class SummaryAgentError(RuntimeError):
    pass


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
        chapter_titles = [chapter.title for chapter in heuristic_result.chapters[:5]]
        highlights = [unit.speech for unit in timeline[:5] if unit.speech][:5]
        return SummaryResult(
            title=title,
            short_summary=heuristic_result.summary,
            long_summary=None,
            keywords=heuristic_result.keywords[:10],
            highlights=highlights,
            extra={
                'chapter_titles': chapter_titles,
                'source': 'heuristic_passthrough',
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
        transcript_preview = '\n'.join(
            f'- {chunk.text}' for chunk in transcript[:24] if chunk.text.strip()
        )[:4000]
        chapter_preview = '\n'.join(
            f'- {chapter.title}: {chapter.summary or ""}' for chapter in heuristic_result.chapters[:8]
        )[:2000]

        prompt = f"""
You are summarizing a Chinese video understanding run.

Title: {title}

Transcript preview:
{transcript_preview}

Heuristic chapter draft:
{chapter_preview}

Return strict JSON with this schema:
{{
  "short_summary": "string",
  "long_summary": "string",
  "highlights": ["string", "string", "string"],
  "chapter_titles": ["string", "string", "string"]
}}

Rules:
- Write natural Chinese.
- Do not mention pipeline internals.
- Keep short_summary to 2-4 sentences.
- Keep highlights concise.
- Chapter titles should be short, human-readable topic labels.
""".strip()

        response = client.responses.create(
            model=self.model,
            input=prompt,
        )
        text = getattr(response, 'output_text', '') or ''
        if not text:
            raise SummaryAgentError('OpenAI summary agent returned empty output')
        try:
            data = json.loads(text)
        except Exception as exc:
            raise SummaryAgentError(f'OpenAI summary agent returned non-JSON output: {text[:400]}') from exc

        return SummaryResult(
            title=title,
            short_summary=data.get('short_summary') or heuristic_result.summary,
            long_summary=data.get('long_summary'),
            keywords=heuristic_result.keywords[:10],
            highlights=list(data.get('highlights') or [])[:5],
            extra={
                'chapter_titles': list(data.get('chapter_titles') or [])[:8],
                'source': 'openai',
                'model': self.model,
            },
        )


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
    agent = build_summary_agent(summary_engine)
    result = agent.summarize(
        title=title,
        transcript=transcript,
        timeline=timeline,
        heuristic_result=heuristic_result,
    )
    payload = asdict(result)
    payload['engine'] = getattr(agent, 'name', summary_engine)
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
            'highlights': agent_result.highlights,
            'chapter_titles': agent_result.extra.get('chapter_titles', []),
        },
        'heuristic_summary': heuristic_result.summary,
    }
    heuristic_result.summary = agent_result.short_summary or heuristic_result.summary
    chapter_titles = list(agent_result.extra.get('chapter_titles') or [])
    for idx, chapter in enumerate(heuristic_result.chapters):
        if idx < len(chapter_titles) and chapter_titles[idx]:
            chapter.title = chapter_titles[idx]
    return heuristic_result
