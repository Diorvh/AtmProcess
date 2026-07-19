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
        if self.start > self.end:
            raise ValueError("起始帧不能大于结束帧")
        if self.decimate <= 0:
            raise ValueError("抽帧间隔必须大于 0")
        return range(self.start, self.end + 1, self.decimate)

    def frame_numbers(self) -> list[int]:
        return list(self.as_range())

    def normalize_current(self) -> int:
        frame_numbers = self.frame_numbers()
        self.current = min(frame_numbers, key=lambda frame: (abs(frame - self.current), frame))
        return self.current

    def move_current(self, offset: int) -> int:
        frame_numbers = self.frame_numbers()
        current = self.normalize_current()
        index = frame_numbers.index(current)
        self.current = frame_numbers[max(0, min(index + offset, len(frame_numbers) - 1))]
        return self.current


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
