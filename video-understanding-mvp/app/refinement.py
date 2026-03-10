from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Optional, Any

from .models import TranscriptChunk


@dataclass
class RefinementInput:
    source_video: str
    run_dir: Path
    transcript: list[TranscriptChunk] = field(default_factory=list)
    language_hint: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementOutput:
    engine: str
    status: str = 'success'
    transcript: list[TranscriptChunk] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    failure_stage: Optional[str] = None


class TextRefiner(Protocol):
    def refine(self, payload: RefinementInput) -> RefinementOutput: ...


class NoOpRefiner:
    def refine(self, payload: RefinementInput) -> RefinementOutput:
        return RefinementOutput(
            engine='noop',
            status='skipped',
            transcript=payload.transcript,
            notes=['No text refinement applied.'],
            metadata={'mode': 'raw_transcript'},
        )
