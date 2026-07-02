from __future__ import annotations

from pathlib import Path

import cv2 as cv
import numpy as np


def read_image(path: Path | str, flags: int = cv.IMREAD_UNCHANGED) -> np.ndarray:
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    data = np.fromfile(str(image_path), dtype=np.uint8)
    image = cv.imdecode(data, flags)
    if image is None:
        raise ValueError(f"Failed to decode image: {image_path}")
    return image


def write_tiff(path: Path | str, image: np.ndarray) -> None:
    image_path = Path(path)
    image_path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv.imencode(".tif", image)
    if not ok:
        raise ValueError(f"Failed to encode TIFF image: {image_path}")
    encoded.tofile(str(image_path))
