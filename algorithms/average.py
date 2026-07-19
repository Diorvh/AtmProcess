from __future__ import annotations

from functools import partial
from pathlib import Path

import cv2 as cv
import numpy as np

from ImageProcessv3.core.image_io import read_image, write_tiff
from ImageProcessv3.core.parallel import split_sequence
from ImageProcessv3.core.progress import ProgressCallback, map_with_progress, report_worker_progress


def _image_path(folder: str | Path, frame_no: int) -> Path:
    return Path(folder) / f"{frame_no}.tif"


def calculate_sum(folder: str | Path, chunk: list[int]) -> np.ndarray:
    total = np.zeros(read_image(_image_path(folder, chunk[0])).shape, dtype="uint64")
    for frame_no in chunk:
        total += read_image(_image_path(folder, frame_no))
        report_worker_progress()
    return total


def calculate_average_image(folder: str | Path, frame_numbers: list[int], num_processes: int, progress_callback: ProgressCallback | None = None) -> np.ndarray:
    chunks = split_sequence(frame_numbers, num_processes)
    results = map_with_progress(partial(calculate_sum, folder), chunks, len(chunks), len(frame_numbers), progress_callback)
    return (np.sum(results, axis=0, dtype="uint64") / len(frame_numbers)).astype(np.uint16)


def process(folder: str | Path, chunk: list[int]) -> None:
    for frame_no in chunk:
        image_path = _image_path(folder, frame_no)
        image = read_image(image_path)
        write_tiff(image_path, cv.cvtColor(image, cv.COLOR_BGR2GRAY))
        report_worker_progress()


def process_color_to_gray(folder: str | Path, frame_numbers: list[int], num_processes: int, progress_callback: ProgressCallback | None = None) -> None:
    chunks = split_sequence(frame_numbers, num_processes)
    map_with_progress(partial(process, folder), chunks, len(chunks), len(frame_numbers), progress_callback)


__all__ = [
    "calculate_average_image",
    "calculate_sum",
    "process",
    "process_color_to_gray",
]
