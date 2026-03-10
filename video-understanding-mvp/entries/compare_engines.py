from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def load_text(path: Path) -> str:
    return path.read_text(encoding='utf-8') if path.exists() else ''


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
        'summary_preview': summary[:300],
        'timeline_preview': [x.get('speech', '') for x in timeline[:5]],
    }


def build_markdown(sample_name: str, mvp_summary: dict, vidove_summary: dict) -> str:
    lines = []
    lines.append(f'# Engine Comparison - {sample_name}')
    lines.append('')
    lines.append('## Quick stats')
    lines.append('')
    lines.append(f'- MVP timeline segments: {mvp_summary.get("timeline_count")}')
    lines.append(f'- MVP chapters: {mvp_summary.get("chapter_count")}')
    lines.append(f'- ViDove timeline segments: {vidove_summary.get("timeline_count")}')
    lines.append(f'- ViDove chapters: {vidove_summary.get("chapter_count")}')
    lines.append('')
    lines.append('## MVP summary preview')
    lines.append('')
    lines.append(mvp_summary.get('summary_preview') or '(empty)')
    lines.append('')
    lines.append('## ViDove summary preview')
    lines.append('')
    lines.append(vidove_summary.get('summary_preview') or '(empty)')
    lines.append('')
    lines.append('## MVP timeline preview')
    lines.append('')
    for item in mvp_summary.get('timeline_preview') or []:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## ViDove timeline preview')
    lines.append('')
    for item in vidove_summary.get('timeline_preview') or []:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('## Initial judgment')
    lines.append('')
    lines.append('- Use this file as a first-pass qualitative comparison on the same sample.')
    lines.append('- Check the paired `comparison.json` for machine-readable fields.')
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare MVP and ViDove outputs on the same sample')
    parser.add_argument('--sample-name', required=True)
    parser.add_argument('--mvp-dir', required=True)
    parser.add_argument('--vidove-dir', required=True)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()

    mvp_dir = Path(args.mvp_dir)
    vidove_dir = Path(args.vidove_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mvp_result = load_json(mvp_dir / 'result.json')
    vidove_result = load_json(vidove_dir / 'result.json')
    mvp_summary = summarize_result(mvp_result)
    vidove_summary = summarize_result(vidove_result)

    comparison = {
        'sample_name': args.sample_name,
        'mvp_dir': str(mvp_dir),
        'vidove_dir': str(vidove_dir),
        'mvp': mvp_summary,
        'vidove': vidove_summary,
    }
    (out_dir / 'comparison.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding='utf-8')
    (out_dir / 'comparison.md').write_text(build_markdown(args.sample_name, mvp_summary, vidove_summary), encoding='utf-8')

    print(f'Comparison written to: {out_dir}')


if __name__ == '__main__':
    main()
