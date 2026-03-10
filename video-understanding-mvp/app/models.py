from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Literal, Any


SourceType = Literal['local_file', 'bilibili_video', 'bilibili_live']
TaskType = Literal['offline_understanding', 'live_summary', 'benchmark_eval']


@dataclass
class MediaRequest:
    source_type: SourceType
    task_type: TaskType
    input_value: str
    title_hint: Optional[str] = None
    language_hint: Optional[str] = None
    options: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class TranscriptChunk:
    start: float
    end: float
    text: str
    speaker: Optional[str] = None
    confidence: Optional[float] = None
    language: Optional[str] = None


@dataclass
class FrameEvent:
    timestamp: float
    frame_path: str
    visual_tags: List[str] = field(default_factory=list)
    ocr: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class TimelineUnit:
    start: float
    end: float
    speech: str
    visual_notes: List[str] = field(default_factory=list)
    ocr: List[str] = field(default_factory=list)
    scene_id: Optional[str] = None
    scene_type: Optional[str] = None
    importance: Optional[float] = None


@dataclass
class ChapterSegment:
    title: str
    start: float
    end: float
    scene_id: Optional[str] = None
    summary: Optional[str] = None
    importance: Optional[float] = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class SummaryResult:
    title: str
    short_summary: str
    long_summary: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaSession:
    session_id: str
    source: str
    mode: str
    title: str
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    subtitle_path: Optional[str] = None
    danmaku_path: Optional[str] = None
    web_url: Optional[str] = None
    run_dir: Optional[str] = None
    source_type: SourceType = 'local_file'
    language: Optional[str] = None


@dataclass
class UnderstandingResult:
    title: str
    summary: str
    chapters: List[ChapterSegment]
    keywords: List[str]
    timeline: List[TimelineUnit]
    transcript: List[TranscriptChunk] = field(default_factory=list)
    raw_transcript: List[TranscriptChunk] = field(default_factory=list)
    refined_transcript: List[TranscriptChunk] = field(default_factory=list)
    frames: List[FrameEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return {
            'title': self.title,
            'summary': self.summary,
            'chapters': [asdict(x) for x in self.chapters],
            'keywords': self.keywords,
            'timeline': [asdict(x) for x in self.timeline],
            'transcript': [asdict(x) for x in self.transcript],
            'raw_transcript': [asdict(x) for x in self.raw_transcript],
            'refined_transcript': [asdict(x) for x in self.refined_transcript],
            'frames': [asdict(x) for x in self.frames],
            'metadata': self.metadata,
            'artifacts': self.artifacts,
        }
