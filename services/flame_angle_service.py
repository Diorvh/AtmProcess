from __future__ import annotations

from pathlib import Path

from ImageProcessv3.algorithms.flame import calc_flame_angle_lightweight, calc_flame_angle_with_marked_images
from ImageProcessv3.core.progress import ProgressCallback


class FlameAngleService:
    def calculate_batch(
        self,
        folder: str | Path,
        frame_numbers: list[int],
        core_num: int,
        settings: dict,
        save_images: bool = False,
        progress_callback: ProgressCallback | None = None,
    ):
        return calc_flame_angle_with_marked_images(str(folder), frame_numbers, core_num, settings, save_images, progress_callback)

    def calculate_lightweight_batch(
        self,
        folder: str | Path,
        frame_numbers: list[int],
        core_num: int,
        settings: dict,
        progress_callback: ProgressCallback | None = None,
    ):
        return calc_flame_angle_lightweight(str(folder), frame_numbers, core_num, settings, progress_callback)
