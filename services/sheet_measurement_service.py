from __future__ import annotations

from algorithms.sheet import SheetMeasurementResult, calculate_sheet_measurement


class SheetMeasurementService:
    def calculate(
        self,
        left_px: int,
        right_px: int,
        up_px: int,
        down_px: int,
        pixel_size_um: float,
    ) -> SheetMeasurementResult:
        return calculate_sheet_measurement(left_px, right_px, up_px, down_px, pixel_size_um)
