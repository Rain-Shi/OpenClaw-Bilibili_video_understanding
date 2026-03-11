from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LiveStateStore:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.state_dir = run_dir / 'state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.state_dir / 'rolling_state.json'

    def save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding='utf-8'))
