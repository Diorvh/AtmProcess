from __future__ import annotations

import json
from pathlib import Path


class SettingsStore:
    def __init__(self, path: str | Path = "settings.json") -> None:
        self.path = Path(path)

    def load(self) -> dict:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Settings file must contain a JSON object: {self.path}")
        return data

    def save(self, data: dict) -> None:
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
