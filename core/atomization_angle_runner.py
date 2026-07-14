from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4


@dataclass(frozen=True)
class AtomizationAngleBatchConfig:
    data_dir: str
    fig_start: int
    fig_end: int
    decimate: int
    core_num: int
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
    save_marked_images: bool
    mode: int = 1

    def validate(self) -> None:
        if self.fig_start > self.fig_end:
            raise ValueError("fig_start must be <= fig_end")
        if self.decimate <= 0:
            raise ValueError("decimate must be > 0")
        if self.core_num <= 0:
            raise ValueError("core_num must be > 0")
        if self.window_length <= 0:
            raise ValueError("window_length must be > 0")
        if self.polyorder < 0:
            raise ValueError("polyorder must be >= 0")

    def to_legacy_lines(self) -> list[str]:
        """Return the line-based input format expected by the C++ program."""
        values: Iterable[object] = (
            self.data_dir,
            self.fig_start,
            self.fig_end,
            self.decimate,
            self.core_num,
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
            self.thres_ratio_left,
            self.thres_ratio_right,
            self.window_length,
            self.polyorder,
            int(self.save_marked_images),
            self.mode,
        )
        return [str(value) for value in values]


@dataclass(frozen=True)
class AtomizationAngleRunResult:
    process: subprocess.CompletedProcess
    work_dir: Path
    input_path: Path
    result_csv: Path
    result_workbook: Path | None = None


class AtomizationAngleCppRunner:
    def __init__(self, runtime_dir: Path | str, run_root: Path | str | None = None) -> None:
        self.runtime_dir = Path(runtime_dir)
        self.exe_path = self.runtime_dir / "main.exe"
        self.run_root = Path(run_root) if run_root is not None else self.runtime_dir / "runs"

    def run_batch(self, config: AtomizationAngleBatchConfig) -> AtomizationAngleRunResult:
        config.validate()
        self._validate_runtime()
        work_dir = self._create_work_dir(config)
        staged_exe = self._stage_runtime(work_dir)
        input_path = work_dir / "inputcpp.txt"
        result_csv = work_dir / "result.csv"
        self._write_input(input_path, config)

        process = subprocess.run(
            [str(staged_exe)],
            cwd=str(work_dir),
            check=True,
        )
        if config.mode == 1 and not result_csv.exists():
            raise FileNotFoundError(f"C++ result file not found: {result_csv}")
        return AtomizationAngleRunResult(
            process=process,
            work_dir=work_dir,
            input_path=input_path,
            result_csv=result_csv,
        )

    def _validate_runtime(self) -> None:
        if not self.runtime_dir.exists():
            raise FileNotFoundError(f"C++ runtime directory not found: {self.runtime_dir}")
        if not self.exe_path.exists():
            raise FileNotFoundError(f"C++ executable not found: {self.exe_path}")

    def _create_work_dir(self, config: AtomizationAngleBatchConfig) -> Path:
        experiment_name = self._ascii_path_part(Path(config.data_dir).name or "experiment")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = self.run_root / f"{timestamp}_{experiment_name}_{config.fig_start}-{config.fig_end}_{uuid4().hex[:8]}"
        work_dir.mkdir(parents=True, exist_ok=False)
        return work_dir

    def _ascii_path_part(self, value: str) -> str:
        safe = "".join(char if char.isascii() and (char.isalnum() or char in "-_") else "_" for char in value)
        return safe.strip("_") or "experiment"

    def _stage_runtime(self, work_dir: Path) -> Path:
        runtime_files = [self.exe_path, *self.runtime_dir.glob("*.dll")]
        for source in runtime_files:
            self._link_or_copy(source, work_dir / source.name)
        return work_dir / self.exe_path.name

    def _link_or_copy(self, source: Path, target: Path) -> None:
        try:
            os.link(source, target)
        except OSError:
            shutil.copy2(source, target)

    def _write_input(self, input_path: Path, config: AtomizationAngleBatchConfig) -> None:
        tmp_path = input_path.with_suffix(".txt.tmp")
        tmp_path.write_text("\n".join(config.to_legacy_lines()) + "\n", encoding="utf-8")
        tmp_path.replace(input_path)
