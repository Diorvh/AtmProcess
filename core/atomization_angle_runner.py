from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


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
        """Return the line-based input format expected by PlayAtmAngleCPP/main.cpp."""
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


class AtomizationAngleCppRunner:
    def __init__(self, cpp_dir: Path | str) -> None:
        self.cpp_dir = Path(cpp_dir)
        self.input_path = self.cpp_dir / "inputcpp.txt"
        self.exe_path = self.cpp_dir / "main.exe"

    def run_batch(self, config: AtomizationAngleBatchConfig) -> subprocess.CompletedProcess:
        config.validate()
        self._validate_runtime()
        self._write_input(config)
        return subprocess.run(
            [str(self.exe_path)],
            cwd=str(self.cpp_dir),
            check=True,
        )

    def _validate_runtime(self) -> None:
        if not self.cpp_dir.exists():
            raise FileNotFoundError(f"C++ runtime directory not found: {self.cpp_dir}")
        if not self.exe_path.exists():
            raise FileNotFoundError(f"C++ executable not found: {self.exe_path}")

    def _write_input(self, config: AtomizationAngleBatchConfig) -> None:
        tmp_path = self.input_path.with_suffix(".txt.tmp")
        tmp_path.write_text("\n".join(config.to_legacy_lines()) + "\n", encoding="utf-8")
        tmp_path.replace(self.input_path)
