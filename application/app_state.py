from __future__ import annotations

import shutil
from pathlib import Path

from AtmProcess.core.config import SettingsStore
from AtmProcess.application.frame_catalog import FrameCatalog
from AtmProcess.domain.settings import AppSettings


class AppState:
    def __init__(self, settings_path: str | Path | None = None) -> None:
        if settings_path is None:
            settings_path = Path(__file__).resolve().parents[1] / "settings.json"
        self.settings_store = SettingsStore(settings_path)
        first_run = not self.settings_store.has_local_settings
        self.settings = AppSettings.from_dict(self.settings_store.load())
        if first_run:
            self._prepare_sample_summary()
        self.frame_catalog = FrameCatalog()

    def _prepare_sample_summary(self) -> None:
        summary_path = self.experiment.result_summary
        if summary_path is None or summary_path.exists():
            return  # 不覆盖已有的样例计算结果。
        template = self.settings_store.path.parent / "sample_data" / "atomization_summary_template.xlsx"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(template, summary_path)  # 只写结果副本，保留随程序发布的原始模板。

    @property
    def experiment(self):
        return self.settings.experiment

    def save(self) -> None:
        self.settings_store.save(self.settings.to_dict())

    def refresh_frame_selection(self, reset_current: bool = False) -> list[int]:
        frames = self.frame_catalog.scan_tif_numbers(self.experiment.image_folder)
        if frames:
            self.experiment.frames.start = frames[0]
            self.experiment.frames.end = frames[-1]
            if reset_current or self.experiment.frames.current not in frames:
                self.experiment.frames.current = frames[0]
        return frames
