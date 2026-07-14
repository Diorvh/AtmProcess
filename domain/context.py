from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FrameSelection:
    start: int = 0
    end: int = 0
    current: int = 0
    decimate: int = 1

    def as_range(self) -> range:
        return range(self.start, self.end + 1, self.decimate)


@dataclass
class ExperimentContext:
    data_root: Path = Path()
    experiment_no: int = 0
    core_num: int = 4
    direct_folder: Path | None = None
    direct_image: Path | None = None
    image_label: str = ""
    result_summary: Path | None = None
    impact_x: int = 0
    impact_y: int = 0
    pixel_size_um: float = 0.0
    frames: FrameSelection = field(default_factory=FrameSelection)

    @property
    def image_folder(self) -> Path:
        if self.direct_image:
            return self.direct_image.parent
        if self.direct_folder:
            return self.direct_folder
        return self.data_root / f"实验编号{self.experiment_no}"

    @property
    def current_image_path(self) -> Path:
        if self.direct_image:
            return self.direct_image
        return self.image_folder / f"{self.frames.current}.tif"

    @property
    def image_name(self) -> str:
        if self.direct_image:
            return self.image_label or self.direct_image.stem
        if self.direct_folder:
            return self.direct_folder.name
        return f"实验编号{self.experiment_no}"
