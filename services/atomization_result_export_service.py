from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import openpyxl
from openpyxl.chart import LineChart, Reference

from ImageProcessv2.core.excel_io import write_matrix
from ImageProcessv2.lib.dft import dft


@dataclass(frozen=True)
class AtomizationPostprocessConfig:
    data_root: Path
    summary_path: Path
    max_freq: int
    experiment_name: str
    result_csv: Path
    output_dir: Path | None = None
    open_workbooks: bool = False

    @property
    def experiment_dir(self) -> Path:
        return self.data_root / self.experiment_name

    @property
    def result_workbook(self) -> Path:
        if self.output_dir is None:
            return self.experiment_dir / "雾化锥角批处理结果.xlsx"
        return self.output_dir / f"{self.experiment_name}_雾化锥角批处理结果.xlsx"


class AtomizationResultExportService:
    def export_from_csv(self, config: AtomizationPostprocessConfig) -> Path:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        self._append_csv(sheet, config.result_csv)
        angle_data = self._read_angle_columns(sheet)
        angle_mid = (angle_data[:, 0] + angle_data[:, 1]) / 2
        self._write_angle_mid(sheet, angle_mid)
        self._write_frequency_data(sheet, np.column_stack((angle_data, angle_mid)), config.max_freq)
        self._add_charts(sheet, config.max_freq)

        config.result_workbook.parent.mkdir(parents=True, exist_ok=True)
        result_workbook = self._save_result_workbook(workbook, config.result_workbook)

        if config.summary_path.exists():
            self._update_summary(config.summary_path, config.experiment_name, sheet)

        if config.open_workbooks:
            os.startfile(result_workbook)
            if config.summary_path.exists():
                os.startfile(config.summary_path)

        return result_workbook

    def _save_result_workbook(self, workbook, path: Path) -> Path:
        try:
            workbook.save(path)
            return path
        except PermissionError:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_path = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")
            workbook.save(fallback_path)
            return fallback_path

    def _append_csv(self, sheet, csv_path: Path) -> None:
        with csv_path.open("r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                sheet.append([self._convert_to_number(cell) for cell in row])

    def _read_angle_columns(self, sheet, start_row: int = 7) -> np.ndarray:
        rows = []
        for row in sheet.iter_rows(min_row=start_row, min_col=2, max_col=4):
            rows.append([float(cell.value) if cell.value is not None else None for cell in row])
        return np.array(rows)

    def _write_angle_mid(self, sheet, angle_mid: np.ndarray) -> None:
        write_matrix(sheet, [["AngleM"]], row_start=3, col_start=5)
        write_matrix(sheet, [[np.mean(angle_mid)]], row_start=4, col_start=5)
        write_matrix(sheet, [[np.std(angle_mid, ddof=1)]], row_start=5, col_start=5)
        write_matrix(sheet, [[np.std(angle_mid, ddof=1) / sheet.cell(row=4, column=4).value]], row_start=6, col_start=5)
        for row_index, value in enumerate(angle_mid):
            sheet.cell(row=row_index + 7, column=5, value=value)

    def _write_frequency_data(self, sheet, result_matrix: np.ndarray, max_freq: int) -> None:
        dft_result = (
            dft(result_matrix[:, 0], 40000),
            dft(result_matrix[:, 1], 40000),
            dft(result_matrix[:, 2], 40000),
            dft(result_matrix[:, 3], 40000),
        )
        freq_matrix = np.column_stack((
            dft_result[0][0],
            dft_result[0][1],
            dft_result[1][1],
            dft_result[2][1],
            dft_result[3][1],
        ))[:len(dft_result[0][0]) // 2, :]

        write_matrix(sheet, [["f/Hz", "左边界角幅值/°", "右边界角幅值/°", "雾化锥角幅值/°", "锥角中心线幅值/°"]], row_start=3, col_start=6)
        write_matrix(sheet, [["最大值"] + list(np.max(freq_matrix[1:, :], axis=0))[1:]], row_start=4, col_start=6)
        write_matrix(sheet, freq_matrix[:max_freq], row_start=5, col_start=6)

    def _add_charts(self, sheet, max_freq: int) -> None:
        legend_names = ["左锥角", "右锥角", "雾化锥角"]

        chart1 = LineChart()
        chart1.title = "时域信号"
        chart1.y_axis.title = "角度/°"
        chart1.x_axis.title = "帧数"
        chart1.add_data(Reference(sheet, min_col=2, min_row=7, max_col=5, max_row=sheet.max_row), titles_from_data=True)
        for index, name in enumerate(legend_names):
            chart1.series[index].name = name
        chart1.set_categories(Reference(sheet, min_col=1, min_row=7, max_row=sheet.max_row))
        chart1.width = 28
        chart1.height = 10
        sheet.add_chart(chart1, "K3")

        max_freq_row = max(5, min(max_freq, sheet.max_row))
        chart2 = LineChart()
        chart2.title = "频域信号：DFT分解"
        chart2.y_axis.title = "幅值/°"
        chart2.x_axis.title = "频率"
        chart2.add_data(Reference(sheet, min_col=7, min_row=5, max_col=10, max_row=max_freq_row), titles_from_data=True)
        for index, name in enumerate(legend_names):
            chart2.series[index].name = name
        chart2.set_categories(Reference(sheet, min_col=6, min_row=5, max_row=max_freq_row))
        chart2.width = 28
        chart2.height = 10
        sheet.add_chart(chart2, "K22")

        chart3 = LineChart()
        chart3.title = "频域信号：DFT分解"
        chart3.y_axis.title = "幅值/°"
        chart3.x_axis.title = "频率"
        chart3.add_data(Reference(sheet, min_col=7, min_row=5, max_col=10, max_row=max(5, sheet.max_row // 2)), titles_from_data=True)
        for index, name in enumerate(legend_names):
            chart3.series[index].name = name
        chart3.set_categories(Reference(sheet, min_col=6, min_row=5, max_row=max(5, sheet.max_row // 2)))
        chart3.width = 28
        chart3.height = 10
        sheet.add_chart(chart3, "K42")

    def _update_summary(self, summary_path: Path, experiment_name: str, source_sheet) -> None:
        experiment_no = self._extract_last_int(experiment_name)
        if experiment_no is None:
            return

        workbook = openpyxl.load_workbook(summary_path)
        sheet = workbook.active
        target_row = experiment_no + 2

        for source_col in range(1, 15):
            source_title = source_sheet.cell(row=1, column=source_col).value
            for target_col in range(1, sheet.max_column + 1):
                if source_title == sheet.cell(row=1, column=target_col).value:
                    sheet.cell(target_row, target_col, source_sheet.cell(row=2, column=source_col).value)

        for target_col in range(1, sheet.max_column + 1):
            title = sheet.cell(row=1, column=target_col).value
            if title == "AngleL":
                sheet.cell(target_row, target_col, source_sheet.cell(row=4, column=2).value)
                sheet.cell(target_row, target_col + 1, source_sheet.cell(row=5, column=2).value)
            if title == "AngleR":
                sheet.cell(target_row, target_col, source_sheet.cell(row=4, column=3).value)
                sheet.cell(target_row, target_col + 1, source_sheet.cell(row=5, column=3).value)
            if title == "AtmAngle":
                sheet.cell(target_row, target_col, source_sheet.cell(row=4, column=4).value)
                sheet.cell(target_row, target_col + 1, source_sheet.cell(row=5, column=4).value)
            if title == "AngleM":
                sheet.cell(target_row, target_col, source_sheet.cell(row=4, column=5).value)
                sheet.cell(target_row, target_col + 1, source_sheet.cell(row=5, column=5).value)

        workbook.save(summary_path)

    def _convert_to_number(self, value: str):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    def _extract_last_int(self, value: str) -> int | None:
        digits = "".join(filter(str.isdigit, value[::-1]))[::-1]
        return int(digits) if digits else None


def load_legacy_input(input_path: str | Path, result_csv: str | Path, open_workbooks: bool = False) -> AtomizationPostprocessConfig:
    lines = Path(input_path).read_text(encoding="utf-8").splitlines()
    return AtomizationPostprocessConfig(
        data_root=Path(lines[0].strip()),
        summary_path=Path(lines[1].strip()),
        max_freq=int(lines[2].strip()),
        experiment_name=lines[3].strip(),
        result_csv=Path(result_csv),
        output_dir=None,
        open_workbooks=open_workbooks,
    )
