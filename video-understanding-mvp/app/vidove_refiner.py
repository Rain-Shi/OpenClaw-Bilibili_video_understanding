from __future__ import annotations

from pathlib import Path

from .asr_adapter import _parse_srt
from .refinement import RefinementInput, RefinementOutput
from .vidove_adapter import ViDoveAdapter, ViDoveAdapterError
from .vidove_bridge import export_vidove_into_mvp_outputs


class ViDoveTextRefiner:
    def __init__(self, repo_dir: str | Path):
        self.repo_dir = Path(repo_dir)
        self.adapter = ViDoveAdapter(self.repo_dir)

    def refine(self, payload: RefinementInput) -> RefinementOutput:
        if not self.adapter.is_available():
            raise ViDoveAdapterError(f'ViDove repo not available: {self.repo_dir}')

        output_root = payload.run_dir / 'vidove_refinement'
        result = self.adapter.run_video(payload.source_video, output_root)
        debug_path = output_root / 'vidove_debug_manifest.json'
        self.adapter.export_debug_manifest(debug_path, result)

        if not result.ok or result.task_dir is None:
            raise ViDoveAdapterError(f'ViDove refinement failed. See: {debug_path}')

        export_vidove_into_mvp_outputs(result.task_dir)

        translated_json = result.task_dir / 'translated_transcript.json'
        transcript = []
        if translated_json.exists():
            import json
            data = json.loads(translated_json.read_text(encoding='utf-8'))
            from .models import TranscriptChunk
            transcript = [TranscriptChunk(**item) for item in data]
        else:
            zh_srt = next((result.task_dir / 'results').glob('*_ZH.srt'), None)
            if zh_srt:
                transcript = _parse_srt(zh_srt.read_text(encoding='utf-8'))

        return RefinementOutput(
            engine='vidove',
            transcript=transcript,
            notes=['ViDove refinement applied.'],
            artifacts={
                'vidove_task_dir': str(result.task_dir),
                'vidove_debug_manifest': str(debug_path),
            },
            metadata={
                'vidove_task_dir': str(result.task_dir),
            },
        )
