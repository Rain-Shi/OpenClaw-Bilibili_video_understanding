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


def compare_case(case: dict) -> dict:
    name = case['sample_name']
    mvp_dir = Path(case['mvp_dir'])
    vidove_dir = Path(case['vidove_dir'])
    mvp = summarize_result(load_json(mvp_dir / 'result.json'))
    vidove = summarize_result(load_json(vidove_dir / 'result.json'))
    return {
        'sample_name': name,
        'mvp_dir': str(mvp_dir),
        'vidove_dir': str(vidove_dir),
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
