from __future__ import annotations

import json
from pathlib import Path

from .audio import build_transcript
from .config import MVPConfig
from .fusion import build_timeline
from .ingest import resolve_input
from .outputs import write_outputs
from .refinement import NoOpRefiner, RefinementInput, RefinementOutput
from .scene import build_simple_scenes
from .understand import summarize_timeline
from .vidove_refiner import ViDoveTextRefiner
from .vision import sample_frames


def run_offline_video_mvp(input_value: str, config: MVPConfig) -> Path:
    session = resolve_input(input_value, config.workdir)
    run_dir = Path(session.run_dir or config.workdir)

    if not session.video_path:
        raise RuntimeError('This connector did not provide a local video_path. Offline MVP currently requires local media.')

    video_path = session.video_path
    title = session.title or Path(video_path).name

    audio_path = run_dir / 'audio.wav'
    frames_dir = run_dir / 'frames'

    transcript = build_transcript(
        video_path,
        run_dir,
        audio_path,
        config.asr_provider,
        config.asr_model,
        config.language_hint,
    )

    refiner = build_text_refiner(config)
    refinement = run_refinement_with_fallback(
        refiner,
        RefinementInput(
            source_video=video_path,
            run_dir=run_dir,
            transcript=transcript,
            language_hint=config.language_hint,
            metadata=session.metadata,
        )
    )
    refined_transcript = refinement.transcript or transcript

    frames = sample_frames(video_path, frames_dir, config.frame_interval_sec, config.max_frames)
    scenes = build_simple_scenes(frames)
    timeline = build_timeline(refined_transcript, frames, scenes)
    result = summarize_timeline(title, timeline, transcript=refined_transcript, frames=frames, metadata={
        **session.metadata,
        'refinement': {
            'engine': refinement.engine,
            'status': refinement.status,
            'failure_stage': refinement.failure_stage,
            'notes': refinement.notes,
            **refinement.metadata,
        },
        'refinement_engine': refinement.engine,
    })
    result.artifacts = {
        'summary_md': str(run_dir / 'summary.md'),
        'chapters_json': str(run_dir / 'chapters.json'),
        'result_json': str(run_dir / 'result.json'),
        'transcript_json': str(run_dir / 'transcript.json'),
        'transcript_srt': str(run_dir / 'transcript.srt'),
        'audio_wav': str(audio_path),
        'frames_dir': str(frames_dir),
        **refinement.artifacts,
    }
    write_outputs(run_dir, result)
    write_run_request(run_dir, input_value, config)
    return run_dir


def build_text_refiner(config: MVPConfig):
    if config.refinement_engine == 'vidove':
        return ViDoveTextRefiner(config.vidove_repo_dir or '../ViDove')
    return NoOpRefiner()


def run_refinement_with_fallback(refiner, payload: RefinementInput) -> RefinementOutput:
    try:
        output = refiner.refine(payload)
        if output.status == 'skipped':
            return output
        if not output.transcript:
            return RefinementOutput(
                engine=output.engine,
                status='partial',
                transcript=payload.transcript,
                notes=output.notes + ['Refinement returned no transcript; fell back to raw transcript.'],
                artifacts=output.artifacts,
                metadata=output.metadata,
                failure_stage='empty_refinement_output',
            )
        return output
    except Exception as exc:
        return RefinementOutput(
            engine=getattr(refiner, '__class__', type(refiner)).__name__,
            status='failed',
            transcript=payload.transcript,
            notes=[f'Refinement failed; fell back to raw transcript: {exc}'],
            metadata={'fallback': 'raw_transcript'},
            failure_stage='refinement_exception',
        )


def write_run_request(run_dir: Path, input_value: str, config: MVPConfig) -> None:
    payload = {
        'input_value': input_value,
        'config': {
            'frame_interval_sec': config.frame_interval_sec,
            'max_frames': config.max_frames,
            'use_llm': config.use_llm,
            'asr_provider': config.asr_provider,
            'asr_model': config.asr_model,
            'language_hint': config.language_hint,
            'refinement_engine': config.refinement_engine,
        },
    }
    (run_dir / 'request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2))
