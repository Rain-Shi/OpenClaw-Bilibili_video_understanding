from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from .bilibili import extract_bilibili_id, is_bilibili_url, resolve_bilibili_to_local


@dataclass
class MediaSession:
    source: str
    mode: str
    title: str
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    subtitle_path: Optional[str] = None
    danmaku_path: Optional[str] = None
    web_url: Optional[str] = None
    session_id: Optional[str] = None
    run_dir: Optional[str] = None


class BaseConnector(ABC):
    @abstractmethod
    def resolve(self, input_value: str, run_dir: Path) -> MediaSession:
        raise NotImplementedError


class LocalFileConnector(BaseConnector):
    def resolve(self, input_value: str, run_dir: Path) -> MediaSession:
        path = Path(input_value)
        return MediaSession(
            source='local_file',
            mode='offline',
            title=path.name,
            video_path=str(path),
            metadata={
                'source_type': 'local_file',
                'input_value': input_value,
            },
            run_dir=str(run_dir),
        )


class BilibiliURLConnector(BaseConnector):
    def resolve(self, input_value: str, run_dir: Path) -> MediaSession:
        payload = resolve_bilibili_to_local(input_value, run_dir)
        return MediaSession(
            source='bilibili',
            mode='offline',
            title=payload['title'],
            video_path=payload['video_path'],
            metadata={
                'source_type': 'bilibili_video',
                'input_value': input_value,
                'metadata_path': payload.get('metadata_path'),
                'bvid': payload.get('bvid'),
                'uploader': payload.get('uploader'),
                'description': payload.get('description'),
                'duration': payload.get('duration'),
                'thumbnail': payload.get('thumbnail'),
                'tags': payload.get('tags') or [],
                'subtitle_languages': payload.get('subtitle_languages') or [],
            },
            web_url=payload.get('web_url'),
            session_id=payload.get('bvid') or extract_bilibili_id(input_value),
            run_dir=str(run_dir),
        )


class BrowserSessionConnector(BaseConnector):
    def resolve(self, input_value: str, run_dir: Path) -> MediaSession:
        return MediaSession(
            source='bilibili',
            mode='browser_session',
            title='browser_session',
            metadata={
                'source_type': 'browser_session',
                'input_value': input_value,
            },
            web_url=input_value,
            run_dir=str(run_dir),
        )


def choose_connector(input_value: str) -> BaseConnector:
    if is_bilibili_url(input_value):
        return BilibiliURLConnector()
    return LocalFileConnector()
