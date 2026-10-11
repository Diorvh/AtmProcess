from __future__ import annotations

import os
from functools import partial
from pathlib import Path

import cv2 as cv
import numpy as np

from AtmProcess.core.image_io import read_image, write_tiff
from AtmProcess.core.parallel import split_sequence
from AtmProcess.core.progress import ProgressCallback, map_with_progress, report_worker_progress
from AtmProcess.lib.lib_Angle import (
    calc_Rparameter_flamedirection,
    calc_angle,
    calc_intensty,
    calc_theta,
    calc_y,
)


def scissor(image: np.ndarray, cut: list[int]) -> np.ndarray:
    return image[cut[0]:image.shape[0] - cut[1], cut[2]:image.shape[1] - cut[3]]


def draw_line(image: np.ndarray, originx: int, originy: int, angle: float, color=(255, 255, 255), length: int = 1000) -> None:
    x2 = int(originx - length * np.cos(angle / 180 * np.pi))
    y2 = int(originy + length * np.sin(angle / 180 * np.pi))
    cv.line(image, (originx, originy), (x2, y2), color, 1)


def _frame_path(folder: str | Path, frame_no: int) -> Path:
    return Path(folder) / f"{frame_no}.tif"


def _cut_settings(settings: dict) -> list[int]:
    return [
        settings["ScissorUp"],
        settings["ScissorDown"],
        settings["ScissorLeft"],
        settings["ScissorRight"],
    ]


def process_with_marked_images(folder: str | Path, settings: dict, save_images: bool, chunk: list[int]) -> list[list[float]]:
    results = []
    save_dir = Path(folder) / "\u4f2a\u5f69\u56fe"

    for frame_no in chunk:
        image = read_image(_frame_path(folder, frame_no))
        image_calc = scissor(image, _cut_settings(settings))

        row = [frame_no]
        theta = calc_theta(image_calc, settings["ImpactX"], settings["ImpactY"], settings["Threshold"])
        theta.append(theta[2] - theta[1])
        row.extend(theta)

        y_range = calc_y(image_calc, settings["Threshold"])
        y_range.append(y_range[2] - y_range[1])
        row.extend(y_range)

        intensity = calc_intensty(
            image_calc,
            settings["ImpactX"],
            settings["ImpactY"],
            theta[1],
            theta[2],
            y_range[1],
            y_range[2],
        )
        row.extend(intensity)
        results.append(row)

        if save_images:
            _save_marked_image(save_dir, frame_no, image, settings, theta, y_range)
        report_worker_progress()

    return results


def _save_marked_image(save_dir: Path, frame_no: int, image: np.ndarray, settings: dict, theta: list[float], y_range: list[float]) -> None:
    if image.dtype == "uint16":
        image_show = np.array(np.round(image / (2 ** 8)), dtype="uint8")
    else:
        image_show = np.array(image, dtype="uint8")

    image_show = (image_show * settings["Gain"]).astype("uint8")
    image_show = cv.applyColorMap(image_show, cv.COLORMAP_JET)
    image_show = cv.cvtColor(image_show, cv.COLOR_BGR2RGB)
    image_show = scissor(image_show, _cut_settings(settings))

    height, width = image_show.shape[0], image_show.shape[1]
    x1, y1 = settings["ImpactX"], settings["ImpactY"]
    draw_line(image_show, x1, y1, -settings["AngleO"] - 90, (0, 0, 255))
    draw_line(image_show, x1, y1, settings["AngleF"] - 90, (0, 0, 255))
    draw_line(image_show, x1, y1, -settings["AngleCalc"] + 90, (0, 0, 255))
    draw_line(image_show, x1, y1, theta[1], (255, 0, 0))
    draw_line(image_show, x1, y1, theta[2], (255, 0, 0))
    draw_line(image_show, x1, y1, theta[0], (0, 255, 0))
    cv.line(image_show, (0, y_range[1]), (width - 1, y_range[1]), (255, 0, 0), 1)
    cv.line(image_show, (0, y_range[2]), (width - 1, y_range[2]), (255, 0, 0), 1)
    cv.line(image_show, (0, y_range[0]), (width - 1, y_range[0]), (0, 255, 0), 1)

    save_file = cv.cvtColor(image_show, cv.COLOR_RGB2BGR)
    write_tiff(save_dir / f"{frame_no}.tif", save_file)


def calc_flame_angle_with_marked_images(
    folder: str | Path,
    frame_numbers: list[int],
    num_processes: int,
    settings: dict,
    save_images: bool,
    progress_callback: ProgressCallback | None = None,
) -> list[list[float]]:
    chunks = split_sequence(frame_numbers, num_processes)
    if save_images:
        os.makedirs(Path(folder) / "\u4f2a\u5f69\u56fe", exist_ok=True)

    chunk_results = map_with_progress(
        partial(process_with_marked_images, folder, settings, save_images),
        chunks,
        len(chunks),
        len(frame_numbers),
        progress_callback,
    )

    results = []
    for chunk_result in chunk_results:
        results.extend(chunk_result)
    return results


def process_lightweight(folder: str | Path, settings: dict, chunk: list[int]) -> list[list[float]]:
    results = []
    for frame_no in chunk:
        image = read_image(_frame_path(folder, frame_no))
        image_calc = scissor(image, _cut_settings(settings))

        row = [frame_no]
        theta = calc_theta(image_calc, settings["ImpactX"], settings["ImpactY"], settings["Threshold"])
        theta.append(theta[2] - theta[1])
        row.extend(theta)

        r_parameter = calc_Rparameter_flamedirection(
            image_calc,
            settings["ImpactX"],
            settings["ImpactY"],
            settings["Threshold"],
            theta[0],
        )
        r_parameter.append(r_parameter[1] - r_parameter[0])
        row.extend(r_parameter)
        results.append(row)
        report_worker_progress()
    return results


def calc_flame_angle_lightweight(
    folder: str | Path,
    frame_numbers: list[int],
    num_processes: int,
    settings: dict,
    progress_callback: ProgressCallback | None = None,
) -> list[list[float]]:
    chunks = split_sequence(frame_numbers, num_processes)
    chunk_results = map_with_progress(
        partial(process_lightweight, folder, settings),
        chunks,
        len(chunks),
        len(frame_numbers),
        progress_callback,
    )

    results = []
    for chunk_result in chunk_results:
        results.extend(chunk_result)
    return results


__all__ = [
    "calc_Rparameter_flamedirection",
    "calc_angle",
    "calc_flame_angle_lightweight",
    "calc_flame_angle_with_marked_images",
    "calc_intensty",
    "calc_theta",
    "calc_y",
    "draw_line",
    "process_lightweight",
    "process_with_marked_images",
    "scissor",
]
