from __future__ import annotations

import json
import re
from pathlib import Path

from .asr_adapter import _parse_srt
from .config import MVPConfig
from .models import TimelineUnit
from .outputs import write_outputs
from .understand import summarize_timeline
from .vidove_adapter import ViDoveAdapter, ViDoveAdapterError


def run_vidove_bridge(input_value: str, config: MVPConfig) -> Path:
    repo_dir = Path(config.vidove_repo_dir or '')
    if not repo_dir:
        raise ViDoveAdapterError('No ViDove repo configured.')

    adapter = ViDoveAdapter(repo_dir)
    if not adapter.is_available():
        raise ViDoveAdapterError(f'ViDove entry not found under: {repo_dir}')

    bridge_root = config.workdir / 'vidove_runs'
    bridge_root.mkdir(parents=True, exist_ok=True)
    result = adapter.run_video(input_value, bridge_root)

    debug_path = bridge_root / 'vidove_debug_manifest.json'
    adapter.export_debug_manifest(debug_path, result)

    if not result.ok:
        raise ViDoveAdapterError(
            f'ViDove run failed. See debug manifest: {debug_path}'
        )

    if result.task_dir is None:
        raise ViDoveAdapterError('ViDove run succeeded but no task_* directory was found.')

    export_vidove_into_mvp_outputs(result.task_dir)
    return result.task_dir


def _looks_like_editorial_leak(text: str) -> bool:
    t = (text or '').strip()
    if not t:
        return True
    patterns = [
        r'^The translated text is already in Chinese',
        r'^No revision is needed\.?$',
        r'^A total of \d+ people were arrested\.?$',
        r'^The other \d+ are still at large\.?$',
        r'^The amount involved reached over',
    ]
    return any(re.search(p, t, re.IGNORECASE) for p in patterns)


def _clean_translated_segments(transcript, translated):
    cleaned = []
    cleaning_notes = []
    for idx, seg in enumerate(translated):
        original_text = seg.text
        if _looks_like_editorial_leak(original_text):
            replacement = None
            if idx < len(transcript):
                replacement = transcript[idx].text
            if replacement and not _looks_like_editorial_leak(replacement):
                seg.text = replacement
                cleaning_notes.append({
                    'index': idx,
                    'action': 'replaced_with_transcribed_text',
                    'original': original_text,
                    'replacement': replacement,
                })
            else:
                cleaning_notes.append({
                    'index': idx,
                    'action': 'dropped_editorial_leak',
                    'original': original_text,
                })
                continue
        cleaned.append(seg)
    return cleaned, cleaning_notes


def export_vidove_into_mvp_outputs(task_dir: Path) -> None:
    results_dir = task_dir / 'results'
    if not results_dir.exists():
        raise ViDoveAdapterError(f'ViDove results dir missing: {results_dir}')

    transcribed_srt = next(results_dir.glob('*_transcribed.srt'), None)
    zh_srt = next(results_dir.glob('*_ZH.srt'), None)
    if not transcribed_srt or not zh_srt:
        raise ViDoveAdapterError('Expected ViDove SRT outputs not found.')

    transcript = _parse_srt(transcribed_srt.read_text(encoding='utf-8'))
    translated = _parse_srt(zh_srt.read_text(encoding='utf-8'))
    translated_clean, cleaning_notes = _clean_translated_segments(transcript, translated)

    timeline = [
        TimelineUnit(
            start=seg.start,
            end=seg.end,
            speech=seg.text,
            visual_notes=[],
            ocr=[],
            scene_id=None,
            scene_type='vidove_segment',
            importance=0.7,
        )
        for seg in translated_clean
    ]

    title = task_dir.name
    result = summarize_timeline(
        title,
        timeline,
        transcript=transcript,
        frames=[],
        metadata={
            'engine': 'vidove',
            'vidove_task_dir': str(task_dir),
            'transcribed_srt': str(transcribed_srt),
            'translated_srt': str(zh_srt),
        },
    )
    result.artifacts = {
        'summary_md': str(task_dir / 'summary.md'),
        'chapters_json': str(task_dir / 'chapters.json'),
        'result_json': str(task_dir / 'result.json'),
        'transcript_json': str(task_dir / 'transcript.json'),
        'transcript_srt': str(transcribed_srt),
        'translated_srt': str(zh_srt),
        'vidove_task_dir': str(task_dir),
    }
    write_outputs(task_dir, result)

    translated_payload = [vars(x) for x in translated_clean]
    (task_dir / 'translated_transcript.json').write_text(
        json.dumps(translated_payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    comparison_summary = {
        'engine': 'vidove',
        'notes': [
            'Mapped ViDove SRT outputs into MVP summary/result/chapters structure.',
            'Timeline currently uses cleaned translated ZH subtitles as speech units.',
            'Applied a lightweight cleaner for obvious editorial leakage in final subtitles.',
            'Further work: fuse ViDove proofreader/editor outputs more cleanly and normalize bilingual leakage.',
        ],
        'cleaning_notes': cleaning_notes,
    }
    (task_dir / 'vidove_mapping_notes.json').write_text(
        json.dumps(comparison_summary, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
