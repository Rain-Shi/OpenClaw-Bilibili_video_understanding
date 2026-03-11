from __future__ import annotations

import json
from pathlib import Path

from .models import UnderstandingResult


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def write_outputs(run_dir: Path, result: UnderstandingResult) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_block = result.summary
    summary_agent = (result.metadata or {}).get('summary_agent') or {}
    uncertain_points = summary_agent.get('uncertain_points') or []
    if uncertain_points:
        summary_block += '\n\n## Low-confidence / needs review\n\n' + '\n'.join(f'- {item}' for item in uncertain_points)

    (run_dir / 'summary.md').write_text(f'# {result.title}\n\n{summary_block}\n')
    _write_json(run_dir / 'chapters.json', [x.__dict__ for x in result.chapters])
    _write_json(run_dir / 'result.json', result.to_dict())
    _write_json(run_dir / 'raw_transcript.json', [x.__dict__ for x in result.raw_transcript])
    _write_json(run_dir / 'refined_transcript.json', [x.__dict__ for x in result.refined_transcript])

    manifest = {
        'title': result.title,
        'refinement': (result.metadata or {}).get('refinement'),
        'summary_agent': (result.metadata or {}).get('summary_agent'),
        'artifacts': {
            'summary_md': str(run_dir / 'summary.md'),
            'chapters_json': str(run_dir / 'chapters.json'),
            'result_json': str(run_dir / 'result.json'),
            'transcript_json': str(run_dir / 'transcript.json') if (run_dir / 'transcript.json').exists() else None,
            'raw_transcript_json': str(run_dir / 'raw_transcript.json') if (run_dir / 'raw_transcript.json').exists() else None,
            'refined_transcript_json': str(run_dir / 'refined_transcript.json') if (run_dir / 'refined_transcript.json').exists() else None,
            'transcript_srt': str(run_dir / 'transcript.srt') if (run_dir / 'transcript.srt').exists() else None,
            'audio_wav': str(run_dir / 'audio.wav') if (run_dir / 'audio.wav').exists() else None,
            'frames_dir': str(run_dir / 'frames') if (run_dir / 'frames').exists() else None,
            'agent_summary_json': str(run_dir / 'agent_summary.json') if (run_dir / 'agent_summary.json').exists() else None,
        },
    }
    (run_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
