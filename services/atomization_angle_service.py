from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np

from ImageProcessv3.algorithms.atomization import AtomizationParameters, calculate_atomization_batch
from ImageProcessv3.core.progress import ProgressCallback
from ImageProcessv3.domain.settings import AtomizationSettings


_PROCESS_COUNT_BY_BATCH_SIZE = (
    (250, 1),
    (750, 2),
    (2000, 4),
    (5000, 6),
    (10000, 8),
)


@dataclass(frozen=True)
class AtomizationBatchResult:
    rows: np.ndarray
    compute_time: float
    process_count: int


class AtomizationAngleService:
    def run_batch(
        self,
        folder: str | Path,
        frame_numbers: list[int],
        process_count: int,
        settings: AtomizationSettings,
        progress_callback: ProgressCallback | None = None,
    ) -> AtomizationBatchResult:
        if process_count <= 0:
            raise ValueError("进程数必须大于 0")
        if not frame_numbers:
            raise ValueError("没有可处理的图像帧")
        actual_process_count = select_atomization_process_count(process_count, len(frame_numbers))
        parameters = AtomizationParameters(
            x_left=settings.x_left,
            x_right=settings.x_right,
            y=settings.y,
            r_max=settings.r_max,
            theta_left=settings.theta_left,
            theta_right=settings.theta_right,
            num_avg_left=settings.num_avg_left,
            r_start_left=settings.r_start_left,
            num_avg_right=settings.num_avg_right,
            r_start_right=settings.r_start_right,
            thres_ratio_left=settings.thres_ratio_left,
            thres_ratio_right=settings.thres_ratio_right,
            window_length=settings.window_length,
            polyorder=settings.polyorder,
        )

        start_time = perf_counter()
        rows = calculate_atomization_batch(
            folder,
            frame_numbers,
            actual_process_count,
            parameters,
            settings.save_marked_images,
            progress_callback,
        )
        return AtomizationBatchResult(rows=rows, compute_time=perf_counter() - start_time, process_count=actual_process_count)


def select_atomization_process_count(requested_count: int, frame_count: int) -> int:
    """根据任务规模限制进程数，避免缓存构建成本超过并行收益。"""
    recommended_count = _PROCESS_COUNT_BY_BATCH_SIZE[-1][1]
    for maximum_frames, process_count in _PROCESS_COUNT_BY_BATCH_SIZE:
        if frame_count <= maximum_frames:
            recommended_count = process_count
            break
    return min(requested_count, frame_count, recommended_count)
