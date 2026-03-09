from __future__ import annotations

import json
from pathlib import Path

from .models import UnderstandingResult


def write_outputs(run_dir: Path, result: UnderstandingResult) -> None:
    (run_dir / 'summary.md').write_text(f'# {result.title}\n\n{result.summary}\n')
    (run_dir / 'chapters.json').write_text(json.dumps(result.chapters, ensure_ascii=False, indent=2))
    (run_dir / 'result.json').write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
