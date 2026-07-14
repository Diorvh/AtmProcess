from __future__ import annotations

import os
from multiprocessing import Pool
from pathlib import Path

import cv2 as cv
import numpy as np

from ImageProcessv2.core.image_io import read_image, write_tiff
from ImageProcessv2.core.parallel import split_frame_range
from ImageProcessv2.lib.lib_AtmAngle import calculate_atm_angle_thres, calculate_grayavg_byangle


def draw_line(image: np.ndarray, originx: int, originy: int, angle: float, color=(255, 255, 255), length: int = 1000) -> None:
    x2 = int(originx - length * np.cos(angle / 180 * np.pi))
    y2 = int(originy + length * np.sin(angle / 180 * np.pi))
    cv.line(image, (originx, originy), (x2, y2), color, 1)


def _frame_path(folder: str | Path, frame_no: int) -> Path:
    return Path(folder) / f"{frame_no}.tif"


def process_calculate_atmangle(args):
    (
        folder,
        frame_numbers,
        x_left,
        x_right,
        y,
        r_max,
        theta_left,
        theta_right,
        num_avg_left,
        r_start_left,
        num_avg_right,
        r_start_right,
        thres_ratio_left,
        thres_ratio_right,
        window_length,
        polyorder,
        save_images,
    ) = args

    left_angles = []
    right_angles = []
    result_dir = Path(folder) / "\u5904\u7406\u7ed3\u679c"

    for frame_no in frame_numbers:
        image = read_image(_frame_path(folder, frame_no))
        angle_left, angle_right = calculate_atm_angle_thres(
            (
                65535 - image,
                x_left,
                x_right,
                y,
                r_max,
                theta_left,
                theta_right,
                num_avg_left,
                r_start_left,
                num_avg_right,
                r_start_right,
                thres_ratio_left,
                thres_ratio_right,
                window_length,
                polyorder,
            )
        )
        left_angles.append(angle_left)
        right_angles.append(angle_right)

        if save_images:
            _save_atomization_mark(image, result_dir, frame_no, x_left, x_right, y, r_max, theta_left, theta_right, angle_left, angle_right)

    return left_angles, right_angles


def _save_atomization_mark(
    image: np.ndarray,
    result_dir: Path,
    frame_no: int,
    x_left: int,
    x_right: int,
    y: int,
    r_max: int,
    theta_left: int,
    theta_right: int,
    angle_left: float,
    angle_right: float,
) -> None:
    if len(image.shape) == 2:
        image = cv.cvtColor(image, cv.COLOR_GRAY2RGB)
    max_value = 65535 if np.max(image) > 255 else 255
    image = cv.ellipse(image, (x_left, y), (r_max, r_max), 0, 90, 180 - theta_left * 0.1, (0, 0, max_value), 1)
    image = cv.ellipse(image, (x_right, y), (r_max, r_max), 0, 180 - theta_right * 0.1, 90, (0, 0, max_value), 1)
    draw_line(image, x_left, y, angle_left, (max_value, 0, 0))
    draw_line(image, x_right, y, angle_right, (max_value, 0, 0))
    os.makedirs(result_dir, exist_ok=True)
    write_tiff(result_dir / f"{frame_no}.tif", image)


def mul_calculate_atmangle(
    folder,
    start,
    end,
    num_processes,
    x_left,
    x_right,
    y,
    r_max,
    theta_left,
    theta_right,
    num_avg_left,
    r_start_left,
    num_avg_right,
    r_start_right,
    thres_ratio_left,
    thres_ratio_right,
    window_length,
    polyorder,
    save_images,
):
    frame_numbers = np.array(list(range(start, end + 1)))
    chunks = split_frame_range(start, end, num_processes)
    args_in = [
        (
            folder,
            chunk,
            x_left,
            x_right,
            y,
            r_max,
            theta_left,
            theta_right,
            num_avg_left,
            r_start_left,
            num_avg_right,
            r_start_right,
            thres_ratio_left,
            thres_ratio_right,
            window_length,
            polyorder,
            save_images,
        )
        for chunk in chunks
    ]

    with Pool(processes=len(chunks)) as pool:
        results = pool.map(process_calculate_atmangle, args_in)

    left_angles = []
    right_angles = []
    for result in results:
        left_angles += result[0]
        right_angles += result[1]
    return np.column_stack((frame_numbers, np.array(left_angles), np.array(right_angles), np.array(right_angles) - np.array(left_angles)))


def mul_calculate_grayavg_byangle(
    image,
    num_processes,
    x_left,
    x_right,
    y,
    r_max,
    theta_left,
    theta_right,
    num_avg_left,
    r_start_left,
    num_avg_right,
    r_start_right,
):
    num_processes = 6
    chunk_size_left = int(899 - theta_left) // num_processes
    chunk_size_right = int(theta_right - 900) // num_processes

    chunks_left = []
    chunks_right = []
    for index in range(num_processes - 1):
        chunks_left.append((899 - index * chunk_size_left, 899 - (index + 1) * chunk_size_left + 1))
        chunks_right.append((900 + index * chunk_size_right, 900 + (index + 1) * chunk_size_right))
    chunks_left.append((899 - (num_processes - 1) * chunk_size_left, theta_left))
    chunks_right.append((900 + (num_processes - 1) * chunk_size_right, theta_right))

    args_in = [
        (image, x_left, x_right, y, r_max, chunks_left[index], chunks_right[index], num_avg_left, r_start_left, num_avg_right, r_start_right)
        for index in range(num_processes)
    ]
    with Pool(processes=num_processes) as pool:
        results = pool.map(calculate_grayavg_byangle, args_in)

    left_x, left_y = results[0][0][0], results[0][0][1]
    right_x, right_y = results[0][1][0], results[0][1][1]
    for index in range(1, num_processes):
        left_x = np.concatenate((left_x, results[index][0][0]))
        left_y = np.concatenate((left_y, results[index][0][1]))
        right_x = np.concatenate((right_x, results[index][1][0]))
        right_y = np.concatenate((right_y, results[index][1][1]))
    return [left_x, left_y], [right_x, right_y]


__all__ = [
    "calculate_atm_angle_thres",
    "calculate_grayavg_byangle",
    "draw_line",
    "mul_calculate_atmangle",
    "mul_calculate_grayavg_byangle",
    "process_calculate_atmangle",
]
