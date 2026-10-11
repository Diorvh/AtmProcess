from __future__ import annotations

from AtmProcess.algorithms.breakup import BreakupLengthResult, calculate_breakup_length


class BreakupLengthService:
    def calculate(self, position_px: int, impact_y_px: int, pixel_size_um: float) -> BreakupLengthResult:
        return calculate_breakup_length(position_px, impact_y_px, pixel_size_um)
