from __future__ import annotations

from pathlib import Path

import numpy as np

from ImageProcessv3.algorithms.average import calculate_average_image, process_color_to_gray
from ImageProcessv3.core.progress import ProgressCallback


class AverageImageService:
    def calculate_average(self, folder: str | Path, frame_numbers: list[int], core_num: int, progress_callback: ProgressCallback | None = None) -> np.ndarray:
        return calculate_average_image(str(folder), frame_numbers, core_num, progress_callback)

    def convert_color_to_gray(self, folder: str | Path, frame_numbers: list[int], core_num: int, progress_callback: ProgressCallback | None = None) -> None:
        process_color_to_gray(str(folder), frame_numbers, core_num, progress_callback)
