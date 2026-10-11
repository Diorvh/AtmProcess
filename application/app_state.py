from __future__ import annotations

from pathlib import Path

from AtmProcess.core.config import SettingsStore
from AtmProcess.application.frame_catalog import FrameCatalog
from AtmProcess.domain.settings import AppSettings


class AppState:
    def __init__(self, settings_path: str | Path | None = None) -> None:
        if settings_path is None:
            settings_path = Path(__file__).resolve().parents[1] / "settings.json"
        self.settings_store = SettingsStore(settings_path)
        self.settings = AppSettings.from_dict(self.settings_store.load())
        self.frame_catalog = FrameCatalog()

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
