from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import openpyxl
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.series import SeriesLabel

from AtmProcess.core.excel_io import write_matrix
from AtmProcess.core.excel_workbook_coordinator import ExcelWorkbookCoordinator
from AtmProcess.domain.settings import AtomizationSettings
from AtmProcess.lib.dft import dft
from AtmProcess.services.atomization_angle_service import AtomizationBatchResult
from AtmProcess.services.summary_workbook_service import SummaryWorkbookService


ATOMIZATION_PARAMETER_FIELDS = (
    ("XLeft", "x_left"), ("XRight", "x_right"), ("Y", "y"), ("Rmax", "r_max"),
    ("ThetaLeft", "theta_left"), ("ThetaRight", "theta_right"),
    ("window_length", "window_length"), ("polyorder", "polyorder"),
    ("NumAvgL", "num_avg_left"), ("RStartL", "r_start_left"),
    ("NumAvgR", "num_avg_right"), ("RStartR", "r_start_right"),
    ("ThresRatioL", "thres_ratio_left"), ("ThresRatioR", "thres_ratio_right"),
)


@dataclass(frozen=True)
class AtomizationExportConfig:
    data_root: Path
    summary_path: Path
    max_freq: int
    experiment_name: str
    output_dir: Path | None = None
    experiment_no: int | None = None

    @property
    def experiment_dir(self) -> Path:
        return self.data_root / self.experiment_name

    @property
    def result_workbook(self) -> Path:
        if self.output_dir is None:
            return self.experiment_dir / "雾化锥角批处理结果.xlsx"
        return self.output_dir / f"{self.experiment_name}_雾化锥角批处理结果.xlsx"


class AtomizationResultExportService:
    def __init__(
        self,
        workbook_coordinator: ExcelWorkbookCoordinator | None = None,
        summary_service: SummaryWorkbookService | None = None,
    ) -> None:
        self.workbook_coordinator = workbook_coordinator or ExcelWorkbookCoordinator()
        self.summary_service = summary_service or SummaryWorkbookService(self.workbook_coordinator)

    def export(self, config: AtomizationExportConfig, settings: AtomizationSettings, result: AtomizationBatchResult) -> Path:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        self._write_batch_data(sheet, settings, result)
        angle_data = result.rows[:, 1:4]
        angle_mid = (angle_data[:, 0] + angle_data[:, 1]) / 2
        self._write_angle_mid(sheet, angle_mid)
        frequency_count = self._write_frequency_data(sheet, np.column_stack((angle_data, angle_mid)), config.max_freq, settings.frame_rate_hz)
        self._add_charts(sheet, len(result.rows), frequency_count)

        config.result_workbook.parent.mkdir(parents=True, exist_ok=True)
        result_workbook = self.workbook_coordinator.save_and_open(workbook, config.result_workbook)

        if config.summary_path.exists():
            self._update_summary(config, sheet)

        return result_workbook

    def _write_batch_data(self, sheet, settings: AtomizationSettings, result: AtomizationBatchResult) -> None:
        headers = [title for title, _field in ATOMIZATION_PARAMETER_FIELDS] + ["num_processes", "compute_time"]
        values = [getattr(settings, field) for _title, field in ATOMIZATION_PARAMETER_FIELDS]
        values.extend((result.process_count, result.compute_time))
        angle_data = result.rows[:, 1:4]
        means = np.mean(angle_data, axis=0)
        standard_deviations = np.std(angle_data, axis=0, ddof=1) if len(angle_data) > 1 else np.zeros(3)
        relative_deviations = standard_deviations / means[2]

        sheet.append(headers)
        sheet.append(values)
        sheet.append(["Frame", "AngleL", "AngleR", "AtmAngle"])
        sheet.append(["Average", *map(float, means)])
        sheet.append(["StDev", *map(float, standard_deviations)])
        sheet.append(["RelativeStDev", *map(float, relative_deviations)])
        for frame, angle_left, angle_right, atomization_angle in result.rows:
            sheet.append([int(frame), float(angle_left), float(angle_right), float(atomization_angle)])

    def _write_angle_mid(self, sheet, angle_mid: np.ndarray) -> None:
        standard_deviation = np.std(angle_mid, ddof=1) if len(angle_mid) > 1 else 0.0
        write_matrix(sheet, [["AngleM"]], row_start=3, col_start=5)
        write_matrix(sheet, [[np.mean(angle_mid)]], row_start=4, col_start=5)
        write_matrix(sheet, [[standard_deviation]], row_start=5, col_start=5)
        write_matrix(sheet, [[standard_deviation / sheet.cell(row=4, column=4).value]], row_start=6, col_start=5)
        for row_index, value in enumerate(angle_mid):
            sheet.cell(row=row_index + 7, column=5, value=value)

    def _write_frequency_data(self, sheet, result_matrix: np.ndarray, max_freq: int, frame_rate_hz: float) -> int:
        dft_result = (
            dft(result_matrix[:, 0], frame_rate_hz),
            dft(result_matrix[:, 1], frame_rate_hz),
            dft(result_matrix[:, 2], frame_rate_hz),
            dft(result_matrix[:, 3], frame_rate_hz),
        )
        freq_matrix = np.column_stack((
            dft_result[0][0],
            dft_result[0][1],
            dft_result[1][1],
            dft_result[2][1],
            dft_result[3][1],
        ))[:len(dft_result[0][0]) // 2, :]

        write_matrix(sheet, [["f/Hz", "左边界角幅值/°", "右边界角幅值/°", "雾化锥角幅值/°", "锥角中心线幅值/°"]], row_start=3, col_start=6)
        max_amplitudes = np.max(freq_matrix[1:, 1:], axis=0) if len(freq_matrix) > 1 else np.zeros(4)
        write_matrix(sheet, [["最大值", *max_amplitudes]], row_start=4, col_start=6)
        exported_frequencies = freq_matrix[:max(0, max_freq)]
        write_matrix(sheet, exported_frequencies, row_start=5, col_start=6)
        return len(exported_frequencies)

    def _add_charts(self, sheet, frame_count: int, frequency_count: int) -> None:
        self._add_line_chart(
            sheet, "时域信号", x_title="帧数", y_title="角度/°",
            x_column=1, first_row=7, count=frame_count, anchor="K3",
        )
        for anchor in ("K22", "K42"):
            self._add_line_chart(
                sheet, "频域信号：DFT分解", x_title="频率/Hz", y_title="幅值/°",
                x_column=6, first_row=5, count=frequency_count, anchor=anchor,
            )

    def _add_line_chart(
        self, sheet, title: str, *, x_title: str, y_title: str,
        x_column: int, first_row: int, count: int, anchor: str,
    ) -> None:
        if count == 0:
            return
        last_row = first_row + count - 1  # 横轴和四组数值共用实际数据范围，不从工作表总行数推算
        chart = LineChart()
        chart.title = title
        chart.x_axis.title = x_title
        chart.y_axis.title = y_title
        chart.add_data(Reference(sheet, min_col=x_column + 1, max_col=x_column + 4, min_row=first_row, max_row=last_row))
        for series, name in zip(chart.series, ("左锥角", "右锥角", "雾化锥角", "锥角中心线")):
            series.tx = SeriesLabel(v=name)  # 显式写入 Excel 系列标题，不消耗第一行数值
        chart.set_categories(Reference(sheet, min_col=x_column, min_row=first_row, max_row=last_row))
        chart.width = 28
        chart.height = 10
        sheet.add_chart(chart, anchor)

    def _update_summary(self, config: AtomizationExportConfig, source_sheet) -> None:
        parameters = {
            source_sheet.cell(1, column).value: source_sheet.cell(2, column).value
            for column in range(1, source_sheet.max_column + 1)
        }
        blocks = {}
        for column in range(2, 6):
            title = source_sheet.cell(3, column).value
            blocks[title] = [source_sheet.cell(row, column).value for row in (4, 5)]
        self.summary_service.update_parameters(
            config.summary_path,
            config.experiment_name,
            "XLeft",
            parameters,
            config.experiment_no,
            result_blocks=blocks,
        )
