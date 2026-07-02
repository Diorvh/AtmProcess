from __future__ import annotations

from pathlib import Path

import numpy as np

from algorithms.average import calculate_average_image, mul_process_DAVIS_images, process_color_to_gray


class AverageImageService:
    def calculate_average(self, folder: str | Path, start: int, end: int, core_num: int) -> np.ndarray:
        return calculate_average_image(str(folder), start, end, core_num)

    def convert_color_to_gray(self, folder: str | Path, start: int, end: int, core_num: int) -> None:
        process_color_to_gray(str(folder), start, end, core_num)

    def remove_davis_prefix(self, folder: str | Path, core_num: int) -> None:
        mul_process_DAVIS_images(str(folder), core_num)
