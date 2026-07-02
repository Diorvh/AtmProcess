from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrameRange:
    start: int
    end: int

    def validate(self) -> None:
        if self.start > self.end:
            raise ValueError("frame range start must be <= end")
