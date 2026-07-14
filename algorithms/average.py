from __future__ import annotations

from functools import partial
from multiprocessing import Pool
from pathlib import Path

import cv2 as cv
import numpy as np

from ImageProcessv2.core.image_io import read_image, write_tiff
from ImageProcessv2.core.parallel import split_frame_range


def _image_path(folder: str | Path, frame_no: int) -> Path:
    return Path(folder) / f"{frame_no}.tif"


def calculate_sum(folder: str | Path, chunk: list[int]) -> np.ndarray:
    total = np.zeros(read_image(_image_path(folder, chunk[0])).shape, dtype="uint64")
    for frame_no in chunk:
        total += read_image(_image_path(folder, frame_no))
    return total


def calculate_average_image(folder: str | Path, start: int, end: int, num_processes: int) -> np.ndarray:
    chunks = split_frame_range(start, end, num_processes)
    with Pool(processes=len(chunks)) as pool:
        results = pool.map(partial(calculate_sum, folder), chunks)
    return (np.sum(results, axis=0, dtype="uint64") / (end - start + 1)).astype(np.uint16)


def process(folder: str | Path, chunk: list[int]) -> None:
    for frame_no in chunk:
        image_path = _image_path(folder, frame_no)
        image = read_image(image_path)
        write_tiff(image_path, cv.cvtColor(image, cv.COLOR_BGR2GRAY))


def process_color_to_gray(folder: str | Path, start: int, end: int, num_processes: int) -> None:
    chunks = split_frame_range(start, end, num_processes)
    with Pool(processes=len(chunks)) as pool:
        pool.map(partial(process, folder), chunks)


__all__ = [
    "calculate_average_image",
    "calculate_sum",
    "process",
    "process_color_to_gray",
]
