from __future__ import annotations

import json
from pathlib import Path

from .models import UnderstandingResult


def write_outputs(run_dir: Path, result: UnderstandingResult) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / 'summary.md').write_text(f'# {result.title}\n\n{result.summary}\n')
    (run_dir / 'chapters.json').write_text(
        json.dumps([x.__dict__ for x in result.chapters], ensure_ascii=False, indent=2)
    )
    (run_dir / 'result.json').write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

    manifest = {
        'title': result.title,
        'refinement': (result.metadata or {}).get('refinement'),
        'artifacts': {
            'summary_md': str(run_dir / 'summary.md'),
            'chapters_json': str(run_dir / 'chapters.json'),
            'result_json': str(run_dir / 'result.json'),
            'transcript_json': str(run_dir / 'transcript.json') if (run_dir / 'transcript.json').exists() else None,
            'transcript_srt': str(run_dir / 'transcript.srt') if (run_dir / 'transcript.srt').exists() else None,
            'audio_wav': str(run_dir / 'audio.wav') if (run_dir / 'audio.wav').exists() else None,
            'frames_dir': str(run_dir / 'frames') if (run_dir / 'frames').exists() else None,
        },
    }
    (run_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
