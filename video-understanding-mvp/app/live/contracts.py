from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LiveChunk:
    stream_id: str
    chunk_id: str
    seq: int
    start: float
    end: float
    transcript_texts: list[str] = field(default_factory=list)
    timeline_texts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChunkSummary:
    stream_id: str
    chunk_id: str
    seq: int
    start: float
    end: float
    micro_summary: str
    focus_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RollingSummary:
    stream_id: str
    upto_seq: int
    window_size: int
    summary: str
    chunk_ids: list[str] = field(default_factory=list)
    focus_points: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
