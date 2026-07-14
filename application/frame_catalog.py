from __future__ import annotations

from pathlib import Path


class FrameCatalog:
    def scan_tif_numbers(self, folder: str | Path) -> list[int]:
        folder_path = Path(folder)
        if not folder_path.exists():
            return []
        frame_numbers = []
        for path in folder_path.glob("*.tif"):
            if path.stem.isdigit():
                frame_numbers.append(int(path.stem))
        return sorted(frame_numbers)
