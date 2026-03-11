from __future__ import annotations

import argparse
import json
from pathlib import Path


ENGINE_SLOTS = [
    ('plain_mvp', 'plain_mvp_dir', 'Plain MVP'),
    ('refinement', 'refinement_dir', 'MVP + Refinement'),
    ('summary_agent', 'summary_agent_dir', 'MVP + Refinement + Summary Agent'),
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def summarize_result(result: dict | None) -> dict:
    result = result or {}
    timeline = result.get('timeline') or []
    chapters = result.get('chapters') or []
    transcript = result.get('transcript') or []
    summary = result.get('summary') or ''
    refined = result.get('refined_transcript') or []
    raw = result.get('raw_transcript') or []
    metadata = result.get('metadata') or {}
    summary_agent = metadata.get('summary_agent') or {}
    return {
        'title': result.get('title'),
        'timeline_count': len(timeline),
        'chapter_count': len(chapters),
        'transcript_count': len(transcript),
        'raw_transcript_count': len(raw),
        'refined_transcript_count': len(refined),
        'summary_preview': summary[:240],
        'timeline_preview': [x.get('speech', '') for x in timeline[:3]],
        'chapter_preview': [x.get('title', '') for x in chapters[:3]],
        'summary_agent_status': summary_agent.get('status'),
        'uncertain_points': summary_agent.get('uncertain_points') or [],
        'grounding_notes': summary_agent.get('grounding_notes') or [],
    }


def infer_status(case: dict, engine_key: str, dir_key: str, result_path: Path) -> tuple[str, str | None, list[str]]:
    notes = []
    declared = ((case.get('status') or {}).get(engine_key))
    if declared:
        return declared, (case.get('failure_stage') or {}).get(engine_key), notes
    if result_path.exists():
        return 'success', None, notes
    raw_dir = case.get(dir_key)
    if not raw_dir:
        notes.append(f'{dir_key} is not set yet')
        return 'missing', 'unconfigured_case', notes
    engine_dir = Path(raw_dir)
    if engine_dir.exists():
        notes.append(f'{engine_key} directory exists but result.json is missing')
        return 'partial', 'result_export', notes
    return 'failed', 'missing_output_dir', notes


def compare_case(case: dict) -> dict:
    compared = {}
    statuses = {}
    failure_stage = {}
    notes = {}
    dirs = {}

    for engine_key, dir_key, _label in ENGINE_SLOTS:
        engine_dir = Path(case[dir_key]) if case.get(dir_key) else Path('.')
        result_path = engine_dir / 'result.json' if case.get(dir_key) else Path(f'__missing_{engine_key}__/result.json')
        status, failure, engine_notes = infer_status(case, engine_key, dir_key, result_path)
        compared[engine_key] = summarize_result(load_json(result_path))
        statuses[engine_key] = status
        failure_stage[engine_key] = failure
        notes[engine_key] = engine_notes
        dirs[engine_key] = str(engine_dir)

    base = compared['plain_mvp']
    refinement = compared['refinement']
    summary_agent = compared['summary_agent']
    return {
        'sample_name': case['sample_name'],
        'dirs': dirs,
        'status': statuses,
        'failure_stage': failure_stage,
        'notes': notes,
        'plain_mvp': base,
        'refinement': refinement,
        'summary_agent': summary_agent,
        'initial_judgment': {
            'refinement_timeline_delta': (refinement.get('timeline_count') or 0) - (base.get('timeline_count') or 0),
            'summary_agent_timeline_delta': (summary_agent.get('timeline_count') or 0) - (refinement.get('timeline_count') or 0),
            'refinement_chapter_delta': (refinement.get('chapter_count') or 0) - (base.get('chapter_count') or 0),
            'summary_agent_chapter_delta': (summary_agent.get('chapter_count') or 0) - (refinement.get('chapter_count') or 0),
        },
        'score_template': {
            'transcript_quality': {'winner': '', 'notes': ''},
            'summary_quality': {'winner': '', 'notes': ''},
            'chapter_quality': {'winner': '', 'notes': ''},
            'grounding_and_uncertainty': {'winner': '', 'notes': ''},
            'overall_winner': '',
            'human_notes': '',
        },
    }


def _add_engine_block(lines: list[str], label: str, data: dict, status: str, failure: str | None, notes: list[str]) -> None:
    lines.append(f'**{label}**')
    lines.append('')
    lines.append(f'- status: {status}')
    if failure:
        lines.append(f'- failure stage: {failure}')
    lines.append(f'- timeline: {data.get("timeline_count")}')
    lines.append(f'- chapters: {data.get("chapter_count")}')
    lines.append(f'- transcript: {data.get("transcript_count")}')
    if data.get('summary_agent_status'):
        lines.append(f'- summary-agent status: {data.get("summary_agent_status")}')
    lines.append('')
    lines.append('summary preview:')
    lines.append(data.get('summary_preview') or '(empty)')
    lines.append('')
    lines.append('chapter preview:')
    for item in data.get('chapter_preview') or []:
        lines.append(f'- {item}')
    lines.append('')
    lines.append('timeline preview:')
    for item in data.get('timeline_preview') or []:
        lines.append(f'- {item}')
    if data.get('grounding_notes'):
        lines.append('')
        lines.append('grounding notes:')
        for item in data.get('grounding_notes')[:3]:
            lines.append(f'- {item}')
    if data.get('uncertain_points'):
        lines.append('')
        lines.append('uncertain points:')
        for item in data.get('uncertain_points')[:3]:
            lines.append(f'- {item}')
    if notes:
        lines.append('')
        lines.append('execution notes:')
        for item in notes:
            lines.append(f'- {item}')
    lines.append('')


def _add_score_template(lines: list[str]) -> None:
    lines.append('Human-readable scoring template:')
    lines.append('')
    lines.append('- Transcript quality winner: ______')
    lines.append('  - Notes: ______')
    lines.append('- Summary quality winner: ______')
    lines.append('  - Notes: ______')
    lines.append('- Chapter quality winner: ______')
    lines.append('  - Notes: ______')
    lines.append('- Grounding / uncertainty winner: ______')
    lines.append('  - Notes: ______')
    lines.append('- Overall winner: ______')
    lines.append('- Human notes: ______')
    lines.append('')


def build_markdown(report: dict) -> str:
    lines = []
    lines.append('# Benchmark Report')
    lines.append('')
    lines.append(f"Cases: {len(report['cases'])}")
    lines.append('')
    lines.append('## Comparison axes')
    lines.append('')
    lines.append('- Plain MVP')
    lines.append('- MVP + Refinement')
    lines.append('- MVP + Refinement + Summary Agent')
    lines.append('')
    for case in report['cases']:
        lines.append(f"## {case['sample_name']}")
        lines.append('')
        _add_engine_block(lines, 'Plain MVP', case['plain_mvp'], case['status']['plain_mvp'], case['failure_stage']['plain_mvp'], case['notes']['plain_mvp'])
        _add_engine_block(lines, 'MVP + Refinement', case['refinement'], case['status']['refinement'], case['failure_stage']['refinement'], case['notes']['refinement'])
        _add_engine_block(lines, 'MVP + Refinement + Summary Agent', case['summary_agent'], case['status']['summary_agent'], case['failure_stage']['summary_agent'], case['notes']['summary_agent'])
        lines.append('Delta notes:')
        lines.append(f"- refinement timeline delta vs plain: {case['initial_judgment']['refinement_timeline_delta']}")
        lines.append(f"- summary-agent timeline delta vs refinement: {case['initial_judgment']['summary_agent_timeline_delta']}")
        lines.append(f"- refinement chapter delta vs plain: {case['initial_judgment']['refinement_chapter_delta']}")
        lines.append(f"- summary-agent chapter delta vs refinement: {case['initial_judgment']['summary_agent_chapter_delta']}")
        lines.append('')
        _add_score_template(lines)
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Run a lightweight benchmark report over plain/refinement/summary-agent result triples')
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
        'engines': ['plain_mvp', 'refinement', 'summary_agent'],
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
