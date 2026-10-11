from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path


_PATH_FIELDS = {
    "experiment": ("data_root", "direct_folder", "direct_image", "result_summary"),
    "measurement": ("export_dir",),
    "preview": ("save_dir",),
    "atomization": ("export_dir",),
}


class SettingsStore:
    def __init__(self, path: str | Path = "settings.json") -> None:
        self.path = Path(path).resolve()

    @property
    def has_local_settings(self) -> bool:
        return self.path.exists() and self.path.stat().st_size > 0

    def load(self) -> dict:
        source = self.path
        if not self.has_local_settings:
            source = self.path.with_name("settings.example.json")  # 首次启动使用随程序附带的样例设置。
        if not source.exists() or source.stat().st_size == 0:
            return {}
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Settings file must contain a JSON object: {source}")
        return self._convert_paths(data, relative=False)

    def save(self, data: dict) -> None:
        self.path.write_text(
            json.dumps(self._convert_paths(data, relative=True), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _convert_paths(self, data: dict, *, relative: bool) -> dict:
        result = deepcopy(data)
        root = self.path.parent
        for section, fields in _PATH_FIELDS.items():
            values = result.get(section, {})
            for field in fields:
                if not values.get(field):
                    continue
                path = Path(values[field])
                if relative:
                    try:
                        path = path.relative_to(root)  # 内置样例及其输出保存为相对路径，移动程序后仍可使用。
                    except ValueError:
                        pass  # 外部实验数据继续保留其真实路径。
                elif not path.is_absolute():
                    path = (root / path).resolve()
                values[field] = str(path) if path.is_absolute() else path.as_posix()
        return result
