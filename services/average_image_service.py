from __future__ import annotations

from pathlib import Path

import numpy as np

from ImageProcessv2.algorithms.average import calculate_average_image, process_color_to_gray


class AverageImageService:
    def calculate_average(self, folder: str | Path, start: int, end: int, core_num: int) -> np.ndarray:
        return calculate_average_image(str(folder), start, end, core_num)

    def convert_color_to_gray(self, folder: str | Path, start: int, end: int, core_num: int) -> None:
        process_color_to_gray(str(folder), start, end, core_num)
