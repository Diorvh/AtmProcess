from __future__ import annotations

from pathlib import Path

from lib.lib_json import read_json, write_json


class SettingsStore:
    def __init__(self, path: str | Path = "settings.json") -> None:
        self.path = Path(path)

    def load(self) -> dict:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return {}
        data = read_json(str(self.path))
        if not isinstance(data, dict):
            raise ValueError(f"Settings file must contain a JSON object: {self.path}")
        return data

    def save(self, data: dict) -> None:
        write_json(str(self.path), data)
