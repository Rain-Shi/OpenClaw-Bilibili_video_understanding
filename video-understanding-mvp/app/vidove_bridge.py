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


_TRAD_TO_SIMP = {
    '這': '这', '於': '于', '產': '产', '還': '还', '網': '网', '擁': '拥', '與': '与', '點': '点',
    '臨': '临', '搗': '捣', '裏': '里', '現': '现', '鏽': '锈', '蒼': '苍', '圍': '围', '這批': '这批',
    '劣質': '劣质', '瓊': '琼', '個': '个', '獲': '获', '顯': '显', '過': '过', '萬': '万', '幣': '币',
    '買': '买', '賣': '卖', '連同': '连同', '押': '押', '達': '达', '牽': '牵', '廣': '广', '竇': '窦',
    '拘捕': '拘捕', '仍在逃': '仍在逃', '聲稱': '声称', '創辦': '创办', '現場': '现场', '號': '号',
    '臺': '台', '灣': '湾', '價': '价', '體': '体', '們': '们', '對': '对', '為': '为', '廣東': '广东',
    '浙江臨海警方近日搗破這批化妝品的生產基地': '浙江临海警方近日捣破这批化妆品的生产基地',
}


def _normalize_script(text: str) -> str:
    s = (text or '').strip()
    for trad, simp in _TRAD_TO_SIMP.items():
        s = s.replace(trad, simp)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


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


def _is_mostly_ascii(text: str) -> bool:
    t = (text or '').strip()
    if not t:
        return False
    ascii_chars = sum(1 for c in t if ord(c) < 128)
    return ascii_chars / max(len(t), 1) > 0.8


def _contains_cjk(text: str) -> bool:
    return any('\u4e00' <= ch <= '\u9fff' for ch in (text or ''))


def _clean_translated_segments(transcript, translated):
    cleaned = []
    cleaning_notes = []
    for idx, seg in enumerate(translated):
        original_text = seg.text
        replacement = transcript[idx].text if idx < len(transcript) else None

        if _looks_like_editorial_leak(original_text):
            if replacement and not _looks_like_editorial_leak(replacement):
                seg.text = _normalize_script(replacement)
                cleaning_notes.append({
                    'index': idx,
                    'action': 'replaced_editorial_leak_with_transcribed_text',
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
        elif _is_mostly_ascii(original_text):
            if replacement and _contains_cjk(replacement):
                seg.text = _normalize_script(replacement)
                cleaning_notes.append({
                    'index': idx,
                    'action': 'replaced_mostly_english_segment_with_transcribed_text',
                    'original': original_text,
                    'replacement': replacement,
                })
            else:
                cleaning_notes.append({
                    'index': idx,
                    'action': 'kept_mostly_english_segment_no_better_replacement',
                    'original': original_text,
                })
        seg.text = _normalize_script(seg.text)
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
