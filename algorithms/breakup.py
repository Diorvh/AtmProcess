from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BreakupLengthResult:
    position_px: int
    length_px: int
    length_mm: float


def calculate_breakup_length(position_px: int, impact_y_px: int, pixel_size_um: float) -> BreakupLengthResult:
    length_px = position_px - impact_y_px
    return BreakupLengthResult(
        position_px=position_px,
        length_px=length_px,
        length_mm=length_px * pixel_size_um / 1000,
    )
