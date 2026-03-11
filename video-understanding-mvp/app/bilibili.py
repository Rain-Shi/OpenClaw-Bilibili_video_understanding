from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from .asr_adapter import shutil_which


class BilibiliIngestError(RuntimeError):
    pass


def is_bilibili_url(url: str) -> bool:
    return 'bilibili.com' in url or 'b23.tv' in url


def extract_bilibili_id(url: str) -> str | None:
    match = re.search(r'(BV[0-9A-Za-z]+)', url)
    if match:
        return match.group(1)
    parsed = urlparse(url)
    if parsed.netloc.endswith('b23.tv'):
        slug = parsed.path.strip('/').split('/')[0]
        return slug or None
    return None


def _pick_media_file(source_dir: Path) -> Path:
    candidates = [
        path for path in sorted(source_dir.glob('*'))
        if path.is_file() and path.suffix.lower() in {'.mp4', '.mkv', '.webm', '.mov'}
    ]
    if not candidates:
        raise BilibiliIngestError('yt-dlp completed but no playable media files were found')
    return max(candidates, key=lambda p: p.stat().st_size)


def resolve_bilibili_to_local(url: str, run_dir: Path) -> Dict[str, Any]:
    if not shutil_which('yt-dlp'):
        raise BilibiliIngestError(
            'yt-dlp is not installed. Install yt-dlp to enable direct Bilibili URL ingestion.'
        )

    source_dir = run_dir / 'source'
    source_dir.mkdir(parents=True, exist_ok=True)
    out_tpl = str(source_dir / '%(title)s [%(id)s].%(ext)s')

    probe = subprocess.run(
        ['yt-dlp', '--dump-single-json', url],
        check=True,
        capture_output=True,
        text=True,
    )
    meta = json.loads(probe.stdout)
    meta_path = run_dir / 'bilibili_meta.json'
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

    subprocess.run(
        [
            'yt-dlp',
            '-o', out_tpl,
            '--merge-output-format', 'mp4',
            url,
        ],
        check=True,
    )

    media_file = _pick_media_file(source_dir)
    bvid = meta.get('id') or extract_bilibili_id(url)
    uploader = meta.get('uploader') or meta.get('channel')
    description = meta.get('description')
    subtitle_info = meta.get('subtitles') or {}

    return {
        'title': meta.get('title') or media_file.stem,
        'video_path': str(media_file),
        'metadata_path': str(meta_path),
        'source': 'bilibili',
        'web_url': meta.get('webpage_url') or url,
        'bvid': bvid,
        'uploader': uploader,
        'description': description,
        'duration': meta.get('duration'),
        'thumbnail': meta.get('thumbnail'),
        'tags': meta.get('tags') or [],
        'subtitle_languages': sorted(subtitle_info.keys()),
    }
