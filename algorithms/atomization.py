from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import cv2 as cv
import numpy as np

from AtmProcess.core.image_io import read_image, write_tiff
from AtmProcess.core.parallel import split_sequence
from AtmProcess.core.progress import ProgressCallback, map_with_progress, report_worker_progress
from AtmProcess.lib.lib_AtmAngle import build_sampling_geometry, calculate_atm_angle_thres_p2


@dataclass(frozen=True)
class AtomizationParameters:
    x_left: int
    x_right: int
    y: int
    r_max: int
    theta_left: int
    theta_right: int
    num_avg_left: int
    r_start_left: int
    num_avg_right: int
    r_start_right: int
    thres_ratio_left: float
    thres_ratio_right: float
    window_length: int
    polyorder: int

    def build_geometry(self, image_shape: tuple[int, int]):
        return build_sampling_geometry(
            image_shape,
            self.x_left,
            self.x_right,
            self.y,
            self.r_max,
            self.theta_left,
            self.theta_right,
            self.num_avg_left,
            self.r_start_left,
            self.num_avg_right,
            self.r_start_right,
        )


def calculate_atomization_batch(
    folder: str | Path,
    frame_numbers: list[int],
    process_count: int,
    parameters: AtomizationParameters,
    save_marked_images: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> np.ndarray:
    if not frame_numbers:
        return np.empty((0, 4), dtype=float)

    chunks = split_sequence(frame_numbers, process_count)
    worker_args = [(Path(folder), chunk, parameters, save_marked_images) for chunk in chunks]
    chunk_results = map_with_progress(_calculate_atomization_chunk, worker_args, len(chunks), len(frame_numbers), progress_callback)

    rows = [row for chunk in chunk_results for row in chunk]
    return np.asarray(rows, dtype=float)


def _calculate_atomization_chunk(args) -> list[tuple[int, float, float, float]]:
    folder, frame_numbers, parameters, save_marked_images = args
    result_dir = folder / "处理结果"
    rows = []
    geometry = None

    for frame_no in frame_numbers:
        image = read_image(folder / f"{frame_no}.tif")
        calculation_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY) if image.ndim == 3 else image
        if geometry is None or geometry.image_shape != calculation_image.shape:
            geometry = parameters.build_geometry(calculation_image.shape)
        res_left, res_right = geometry.calculate_profiles(calculation_image)
        angle_left, angle_right = calculate_atm_angle_thres_p2((
            res_left,
            res_right,
            parameters.num_avg_left,
            parameters.num_avg_right,
            parameters.thres_ratio_left,
            parameters.thres_ratio_right,
            parameters.window_length,
            parameters.polyorder,
        ))
        rows.append((frame_no, float(angle_left), float(angle_right), float(angle_right - angle_left)))

        if save_marked_images:
            _save_atomization_mark(image, result_dir, frame_no, parameters, angle_left, angle_right)
        report_worker_progress()

    return rows


def _save_atomization_mark(
    image: np.ndarray,
    result_dir: Path,
    frame_no: int,
    parameters: AtomizationParameters,
    angle_left: float,
    angle_right: float,
) -> None:
    if image.ndim == 2:
        image = cv.cvtColor(image, cv.COLOR_GRAY2RGB)
    max_value = int(np.iinfo(image.dtype).max)
    cv.ellipse(image, (parameters.x_left, parameters.y), (parameters.r_max, parameters.r_max), 0, 90, 180 - parameters.theta_left * 0.1, (0, 0, max_value), 1)
    cv.ellipse(image, (parameters.x_right, parameters.y), (parameters.r_max, parameters.r_max), 0, 180 - parameters.theta_right * 0.1, 90, (0, 0, max_value), 1)
    _draw_line(image, parameters.x_left, parameters.y, angle_left, (max_value, 0, 0))
    _draw_line(image, parameters.x_right, parameters.y, angle_right, (max_value, 0, 0))
    os.makedirs(result_dir, exist_ok=True)
    write_tiff(result_dir / f"{frame_no}.tif", image)


def _draw_line(image: np.ndarray, origin_x: int, origin_y: int, angle: float, color, length: int = 1000) -> None:
    x_end = int(origin_x - length * np.cos(np.deg2rad(angle)))
    y_end = int(origin_y + length * np.sin(np.deg2rad(angle)))
    cv.line(image, (origin_x, origin_y), (x_end, y_end), color, 1)


__all__ = ["AtomizationParameters", "calculate_atomization_batch"]
