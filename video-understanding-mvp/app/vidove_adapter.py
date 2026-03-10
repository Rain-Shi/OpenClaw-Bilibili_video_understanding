from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ViDoveRunResult:
    ok: bool
    task_dir: Optional[Path]
    stdout: str = ''
    stderr: str = ''
    note: str = ''


class ViDoveAdapterError(RuntimeError):
    pass


class ViDoveAdapter:
    def __init__(self, repo_dir: str | Path):
        self.repo_dir = Path(repo_dir)
        self.entry = self.repo_dir / 'entries' / 'run.py'
        self.launch_cfg = self.repo_dir / 'configs' / 'local_launch.yaml'
        self.task_cfg = self.repo_dir / 'configs' / 'task_config.yaml'
        self.python_bin = self._choose_python_bin()

    def is_available(self) -> bool:
        return self.repo_dir.exists() and self.entry.exists()

    def run_video(self, video_file: str, output_root: str | Path) -> ViDoveRunResult:
        if not self.is_available():
            raise ViDoveAdapterError(f'ViDove repo not ready: {self.repo_dir}')

        output_root = Path(output_root)
        output_root.mkdir(parents=True, exist_ok=True)
        launch_cfg = output_root / 'vidove_local_launch.yaml'
        launch_cfg.write_text(
            f'local_dump: {output_root.as_posix()}\n'
            'environ: local\n'
            'api_source: openai\n'
        )
        task_cfg = self._make_local_task_cfg(output_root)

        cmd = [
            str(self.python_bin), str(self.entry),
            '--video_file', video_file,
            '--launch_cfg', str(launch_cfg),
            '--task_cfg', str(task_cfg),
        ]

        proc = subprocess.run(
            cmd,
            cwd=str(self.repo_dir),
            capture_output=True,
            text=True,
        )

        task_dir = self._latest_task_dir(output_root)
        return ViDoveRunResult(
            ok=proc.returncode == 0,
            task_dir=task_dir,
            stdout=proc.stdout,
            stderr=proc.stderr,
            note='ViDove run completed' if proc.returncode == 0 else 'ViDove run failed',
        )

    def _choose_python_bin(self) -> Path:
        candidates = [
            self.repo_dir / '.venv' / 'bin' / 'python',
            self.repo_dir / '.venv310' / 'bin' / 'python',
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return Path('python3')

    def _make_local_task_cfg(self, output_root: Path) -> Path:
        output_root.mkdir(parents=True, exist_ok=True)
        raw = self.task_cfg.read_text(encoding='utf-8')
        raw = raw.replace('audio_agent: GeminiAudioAgent # clip or other vLLMs', 'audio_agent: WhisperAudioAgent # clip or other vLLMs')
        raw = raw.replace('src_lang: en', 'src_lang: zh')
        raw = raw.replace('target_lang: ZH', 'target_lang: ZH')
        patched = output_root / 'vidove_task_config.local.yaml'
        patched.write_text(raw, encoding='utf-8')
        return patched

    def _latest_task_dir(self, output_root: Path) -> Optional[Path]:
        candidates = sorted(
            [p for p in output_root.glob('task_*') if p.is_dir()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return candidates[0] if candidates else None

    def export_debug_manifest(self, dest: Path, run_result: ViDoveRunResult) -> None:
        payload = {
            'ok': run_result.ok,
            'task_dir': str(run_result.task_dir) if run_result.task_dir else None,
            'note': run_result.note,
            'stdout_tail': run_result.stdout[-4000:],
            'stderr_tail': run_result.stderr[-4000:],
        }
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
