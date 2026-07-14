from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SheetMeasurementResult:
    width_px: int
    width_mm: float
    length_px: int
    length_mm: float


def calculate_sheet_measurement(
    left_px: int,
    right_px: int,
    up_px: int,
    down_px: int,
    pixel_size_um: float,
) -> SheetMeasurementResult:
    width_px = right_px - left_px
    length_px = down_px - up_px
    return SheetMeasurementResult(
        width_px=width_px,
        width_mm=width_px * pixel_size_um / 1000,
        length_px=length_px,
        length_mm=length_px * pixel_size_um / 1000,
    )
