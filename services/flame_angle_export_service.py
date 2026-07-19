from __future__ import annotations

from pathlib import Path

import numpy as np
import openpyxl

from ImageProcessv3.core.excel_io import write_matrix
from ImageProcessv3.core.excel_workbook_coordinator import ExcelWorkbookCoordinator


class FlameAngleExportService:
    batch_headers = [
        "帧数",
        "中心线角",
        "左边界角",
        "右边界角",
        "火焰锥角",
        "火焰中心",
        "火焰起始",
        "火焰结束",
        "火焰长度",
        "火焰区平均强度",
        "火焰区最大强度",
    ]

    lightweight_headers = [
        "帧数",
        "中心线角",
        "左边界角",
        "右边界角",
        "火焰锥角",
        "火焰起始",
        "火焰结束",
        "火焰长度",
    ]

    def __init__(self, workbook_coordinator: ExcelWorkbookCoordinator | None = None) -> None:
        self.workbook_coordinator = workbook_coordinator or ExcelWorkbookCoordinator()

    def export_batch(self, folder: str | Path, settings: dict, rows) -> Path:
        return self._export(
            folder=folder,
            filename_suffix="火焰锥角批处理结果.xlsx",
            settings=settings,
            headers=self.batch_headers,
            rows=rows,
            include_std=False,
        )

    def export_lightweight_batch(self, folder: str | Path, settings: dict, rows) -> Path:
        return self._export(
            folder=folder,
            filename_suffix="火焰信息批处理结果.xlsx",
            settings=settings,
            headers=self.lightweight_headers,
            rows=rows,
            include_std=True,
        )

    def _export(self, folder: str | Path, filename_suffix: str, settings: dict, headers: list[str], rows, include_std: bool) -> Path:
        folder_path = Path(folder)
        save_path = folder_path / f"{folder_path.name}{filename_suffix}"
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        write_matrix(sheet, list(zip(*settings.items())))
        write_matrix(sheet, [headers], append=True)
        write_matrix(sheet, [["平均值"] + list(np.mean(rows, axis=0))[1:]], append=True)
        if include_std:
            write_matrix(sheet, [["标准差"] + list(np.std(rows, axis=0, ddof=1))[1:]], append=True)
        write_matrix(sheet, rows, append=True)

        return self.workbook_coordinator.save_and_open(workbook, save_path)
