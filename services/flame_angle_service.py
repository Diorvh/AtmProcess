from __future__ import annotations

from pathlib import Path

from CalcFlameAngle.CalcFlameAngle import calc_flame_angle as calc_flame_angle_with_images
from MeasureFlameAngle.MeasureFlameAngle import calc_flame_angle as calc_flame_angle_lightweight


class FlameAngleService:
    def calculate_batch(
        self,
        folder: str | Path,
        start: int,
        end: int,
        core_num: int,
        settings: dict,
        save_images: bool = False,
    ):
        return calc_flame_angle_with_images(str(folder), start, end, core_num, settings, save_images)

    def calculate_lightweight_batch(
        self,
        folder: str | Path,
        start: int,
        end: int,
        core_num: int,
        settings: dict,
    ):
        return calc_flame_angle_lightweight(str(folder), start, end, core_num, settings)
