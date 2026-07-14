from __future__ import annotations

from pathlib import Path


def experiment_dir(data_dir: str | Path, exp_no: int) -> Path:
    return Path(data_dir) / f"实验编号{exp_no}"


def image_path(folder: str | Path, frame_no: int) -> Path:
    return Path(folder) / f"{frame_no}.tif"


def result_workbook_path(folder: str | Path, prefix: str, class_name: str) -> Path:
    return Path(folder) / f"{prefix}{class_name}.xlsx"


def folder_name(path: str | Path) -> str:
    return Path(path).name
