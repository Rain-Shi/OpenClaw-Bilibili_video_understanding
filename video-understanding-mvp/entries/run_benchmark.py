from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def summarize_result(result: dict | None) -> dict:
    result = result or {}
    timeline = result.get('timeline') or []
    chapters = result.get('chapters') or []
    transcript = result.get('transcript') or []
    summary = result.get('summary') or ''
    return {
        'title': result.get('title'),
        'timeline_count': len(timeline),
        'chapter_count': len(chapters),
        'transcript_count': len(transcript),
        'summary_preview': summary[:240],
        'timeline_preview': [x.get('speech', '') for x in timeline[:3]],
    }


def infer_status(case: dict, engine_name: str, result_path: Path) -> tuple[str, str | None, list[str]]:
    notes = []
    declared = (case.get('status') or {}).get(engine_name)
    if declared:
        return declared, case.get('failure_stage'), notes
    if result_path.exists():
        return 'success', None, notes
    raw_dir = case.get(f'{engine_name}_dir')
    if not raw_dir:
        notes.append(f'{engine_name}_dir is not set yet')
        return 'missing', 'unconfigured_case', notes
    engine_dir = Path(raw_dir)
    if engine_dir.exists():
        notes.append(f'{engine_name} directory exists but result.json is missing')
        return 'partial', 'result_export', notes
    return 'failed', 'missing_output_dir', notes


def compare_case(case: dict) -> dict:
    name = case['sample_name']
    mvp_dir = Path(case['mvp_dir']) if case.get('mvp_dir') else Path('.')
    vidove_dir = Path(case['vidove_dir']) if case.get('vidove_dir') else Path('.')

    mvp_result_path = mvp_dir / 'result.json' if case.get('mvp_dir') else Path('__missing_mvp__/result.json')
    vidove_result_path = vidove_dir / 'result.json' if case.get('vidove_dir') else Path('__missing_vidove__/result.json')

    mvp_status, mvp_failure_stage, mvp_notes = infer_status(case, 'mvp', mvp_result_path)
    vidove_status, vidove_failure_stage, vidove_notes = infer_status(case, 'vidove', vidove_result_path)

    mvp = summarize_result(load_json(mvp_result_path))
    vidove = summarize_result(load_json(vidove_result_path))
    return {
        'sample_name': name,
        'mvp_dir': str(mvp_dir),
        'vidove_dir': str(vidove_dir),
        'status': {
            'mvp': mvp_status,
            'vidove': vidove_status,
        },
        'failure_stage': {
            'mvp': mvp_failure_stage,
            'vidove': vidove_failure_stage,
        },
        'notes': {
            'mvp': mvp_notes,
            'vidove': vidove_notes,
        },
        'mvp': mvp,
        'vidove': vidove,
        'initial_judgment': {
            'timeline_delta': (vidove.get('timeline_count') or 0) - (mvp.get('timeline_count') or 0),
            'chapter_delta': (vidove.get('chapter_count') or 0) - (mvp.get('chapter_count') or 0),
        },
    }


def build_markdown(report: dict) -> str:
    lines = []
    lines.append('# Benchmark Report')
    lines.append('')
    lines.append(f"Cases: {len(report['cases'])}")
    lines.append('')
    lines.append('## Overview')
    lines.append('')
    for case in report['cases']:
        lines.append(f"### {case['sample_name']}")
        lines.append('')
        lines.append(f"- MVP status: {case['status']['mvp']}")
        lines.append(f"- ViDove status: {case['status']['vidove']}")
        if case['failure_stage']['mvp']:
            lines.append(f"- MVP failure stage: {case['failure_stage']['mvp']}")
        if case['failure_stage']['vidove']:
            lines.append(f"- ViDove failure stage: {case['failure_stage']['vidove']}")
        lines.append(f"- MVP timeline: {case['mvp']['timeline_count']}")
        lines.append(f"- ViDove timeline: {case['vidove']['timeline_count']}")
        lines.append(f"- MVP chapters: {case['mvp']['chapter_count']}")
        lines.append(f"- ViDove chapters: {case['vidove']['chapter_count']}")
        lines.append('')
        lines.append('**MVP summary preview**')
        lines.append('')
        lines.append(case['mvp']['summary_preview'] or '(empty)')
        lines.append('')
        lines.append('**ViDove summary preview**')
        lines.append('')
        lines.append(case['vidove']['summary_preview'] or '(empty)')
        lines.append('')
        lines.append('**MVP timeline preview**')
        for item in case['mvp']['timeline_preview'] or []:
            lines.append(f'- {item}')
        lines.append('')
        lines.append('**ViDove timeline preview**')
        for item in case['vidove']['timeline_preview'] or []:
            lines.append(f'- {item}')
        lines.append('')
        if case['notes']['mvp'] or case['notes']['vidove']:
            lines.append('**Execution notes**')
            for item in case['notes']['mvp']:
                lines.append(f'- MVP: {item}')
            for item in case['notes']['vidove']:
                lines.append(f'- ViDove: {item}')
            lines.append('')
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Run a lightweight benchmark report over multiple MVP/ViDove result pairs')
    parser.add_argument('--manifest', required=True, help='Path to benchmark manifest json')
    parser.add_argument('--out-dir', required=True, help='Directory for benchmark outputs')
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(manifest_path)
    if not manifest or 'cases' not in manifest:
        raise SystemExit('Manifest must be JSON with a top-level "cases" array.')

    cases = [compare_case(case) for case in manifest['cases']]
    report = {
        'manifest': str(manifest_path),
        'case_count': len(cases),
        'cases': cases,
    }

    (out_dir / 'benchmark_report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    (out_dir / 'benchmark_report.md').write_text(
        build_markdown(report), encoding='utf-8'
    )
    print(f'Benchmark report written to: {out_dir}')


if __name__ == '__main__':
    main()
