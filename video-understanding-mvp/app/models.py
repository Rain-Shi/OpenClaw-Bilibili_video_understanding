from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class TranscriptChunk:
    start: float
    end: float
    text: str
    speaker: Optional[str] = None
    confidence: Optional[float] = None


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
    importance: Optional[float] = None


@dataclass
class UnderstandingResult:
    title: str
    summary: str
    chapters: List[dict]
    keywords: List[str]
    timeline: List[TimelineUnit]

    def to_dict(self):
        return {
            'title': self.title,
            'summary': self.summary,
            'chapters': self.chapters,
            'keywords': self.keywords,
            'timeline': [asdict(x) for x in self.timeline],
        }
