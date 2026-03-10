from __future__ import annotations

from pathlib import Path

from .config import MVPConfig
from .vidove_adapter import ViDoveAdapter, ViDoveAdapterError


def run_vidove_bridge(input_value: str, config: MVPConfig) -> Path:
    repo_dir = Path(config.vidove_repo_dir or '')
    if not repo_dir:
        raise ViDoveAdapterError('No ViDove repo configured.')

    adapter = ViDoveAdapter(repo_dir)
    if not adapter.is_available():
        raise ViDoveAdapterError(f'ViDove entry not found under: {repo_dir}')

    bridge_root = config.workdir / 'vidove_runs'
    bridge_root.mkdir(parents=True, exist_ok=True)
    result = adapter.run_video(input_value, bridge_root)

    debug_path = bridge_root / 'vidove_debug_manifest.json'
    adapter.export_debug_manifest(debug_path, result)

    if not result.ok:
        raise ViDoveAdapterError(
            f'ViDove run failed. See debug manifest: {debug_path}'
        )

    if result.task_dir is None:
        raise ViDoveAdapterError('ViDove run succeeded but no task_* directory was found.')

    return result.task_dir
