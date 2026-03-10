from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from .asr_adapter import shutil_which


class BilibiliIngestError(RuntimeError):
    pass


def is_bilibili_url(url: str) -> bool:
    return 'bilibili.com' in url or 'b23.tv' in url


def resolve_bilibili_to_local(url: str, run_dir: Path) -> Dict[str, Any]:
    """Download or inspect a Bilibili video into local files.

    Current strategy:
    - if yt-dlp exists, use it as the practical downloader layer
    - otherwise raise a helpful error that tells the user what is missing
    """
    if not shutil_which('yt-dlp'):
        raise BilibiliIngestError(
            'yt-dlp is not installed. Install yt-dlp to enable direct Bilibili URL ingestion.'
        )

    source_dir = run_dir / 'source'
    source_dir.mkdir(parents=True, exist_ok=True)
    out_tpl = str(source_dir / '%(title)s [%(id)s].%(ext)s')

    # First collect metadata.
    probe = subprocess.run(
        ['yt-dlp', '--dump-single-json', url],
        check=True,
        capture_output=True,
        text=True,
    )
    meta = json.loads(probe.stdout)
    (run_dir / 'bilibili_meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    # Then download the best practical MP4-ish asset.
    subprocess.run(
        [
            'yt-dlp',
            '-o', out_tpl,
            '--merge-output-format', 'mp4',
            url,
        ],
        check=True,
    )

    candidates = sorted(source_dir.glob('*'))
    if not candidates:
        raise BilibiliIngestError('yt-dlp completed but no media files were found')

    media_file = candidates[0]
    return {
        'title': meta.get('title') or media_file.stem,
        'video_path': str(media_file),
        'metadata_path': str(run_dir / 'bilibili_meta.json'),
        'source': 'bilibili',
        'web_url': url,
    }
