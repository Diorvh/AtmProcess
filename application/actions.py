from __future__ import annotations

from pathlib import Path

from ImageProcessv2.core.atomization_angle_runner import AtomizationAngleBatchConfig
from ImageProcessv2.core.image_io import write_tiff
from ImageProcessv2.services.atomization_angle_service import AtomizationAngleService
from ImageProcessv2.services.average_image_service import AverageImageService
from ImageProcessv2.services.breakup_length_service import BreakupLengthService
from ImageProcessv2.services.flame_angle_export_service import FlameAngleExportService
from ImageProcessv2.services.flame_angle_service import FlameAngleService
from ImageProcessv2.services.measurement_export_service import MeasurementExportService
from ImageProcessv2.services.sheet_measurement_service import SheetMeasurementService
from ImageProcessv2.services.summary_workbook_service import SummaryWorkbookService

from ImageProcessv2.application.app_state import AppState


class ImageProcessActions:
    def __init__(self, state: AppState) -> None:
        self.state = state
        self.average_service = AverageImageService()
        self.flame_service = FlameAngleService()
        self.flame_export_service = FlameAngleExportService()
        self.measurement_export_service = MeasurementExportService()
        self.sheet_service = SheetMeasurementService()
        self.breakup_service = BreakupLengthService()
        self.summary_service = SummaryWorkbookService()

    @property
    def folder(self) -> Path:
        return self.state.experiment.image_folder

    def save_average_image(self) -> Path:
        frames = self.state.experiment.frames
        image = self.average_service.calculate_average(self.folder, frames.start, frames.end, self.state.experiment.core_num)
        output_path = self.folder.parent / f"{self._average_image_label()}_{frames.start}-{frames.end}-AverageFigure.tif"
        write_tiff(output_path, image)
        return output_path

    def _average_image_label(self) -> str:
        experiment = self.state.experiment
        if experiment.direct_image:
            return experiment.image_label or experiment.direct_image.stem
        if experiment.direct_folder:
            return experiment.direct_folder.name
        return str(experiment.experiment_no)

    def convert_color_to_gray(self) -> None:
        frames = self.state.experiment.frames
        self.average_service.convert_color_to_gray(self.folder, frames.start, frames.end, self.state.experiment.core_num)

    def calculate_sheet(self, left_px: int, right_px: int, up_px: int, down_px: int):
        return self.sheet_service.calculate(left_px, right_px, up_px, down_px, self.state.experiment.pixel_size_um)

    def calculate_breakup(self, position_px: int):
        return self.breakup_service.calculate(position_px, self.state.experiment.impact_y, self.state.experiment.pixel_size_um)

    def export_sheet_records(self, rows, output_dir: str | Path | None = None) -> Path:
        experiment = self.state.experiment
        return self.measurement_export_service.export_sheet(
            self.folder,
            experiment.image_name,
            rows,
            experiment.impact_x,
            experiment.impact_y,
            experiment.pixel_size_um,
            output_dir=output_dir,
            summary_path=experiment.result_summary,
            experiment_no=experiment.experiment_no,
            decimate=experiment.frames.decimate,
        )

    def export_breakup_records(self, rows, output_dir: str | Path | None = None) -> Path:
        experiment = self.state.experiment
        return self.measurement_export_service.export_breakup(
            self.folder,
            experiment.image_name,
            rows,
            experiment.impact_x,
            experiment.impact_y,
            experiment.pixel_size_um,
            experiment.frames.decimate,
            output_dir,
            summary_path=experiment.result_summary,
            experiment_no=experiment.experiment_no,
        )

    def calculate_flame_batch(self) -> Path:
        experiment = self.state.experiment
        settings = self.state.settings.flame.to_algorithm_dict(experiment.impact_x, experiment.impact_y)
        frames = experiment.frames
        rows = self.flame_service.calculate_batch(
            self.folder,
            frames.start,
            frames.end,
            experiment.core_num,
            settings,
            self.state.settings.flame.save_marked_images,
        )
        return self.flame_export_service.export_batch(self.folder, settings, rows)

    def calculate_flame_lightweight_batch(self) -> Path:
        experiment = self.state.experiment
        settings = self.state.settings.flame.to_algorithm_dict(experiment.impact_x, experiment.impact_y)
        frames = experiment.frames
        rows = self.flame_service.calculate_lightweight_batch(self.folder, frames.start, frames.end, experiment.core_num, settings)
        return self.flame_export_service.export_lightweight_batch(self.folder, settings, rows)

    def run_atomization_batch(self) -> Path:
        cpp_dir = Path(__file__).resolve().parents[1] / "PlayAtmAngleCPP"
        experiment = self.state.experiment
        atom = self.state.settings.atomization
        run_result = AtomizationAngleService(cpp_dir, open_workbooks=False).run_batch(
            self.build_atomization_config(),
            summary_path=experiment.result_summary,
            max_freq=atom.max_freq,
            output_dir=atom.export_dir or None,
        )
        return run_result.result_workbook or run_result.result_csv

    def read_atomization_parameters_from_summary(self) -> dict[str, object]:
        experiment = self.state.experiment
        if not experiment.result_summary:
            raise ValueError("请先选择汇总表")
        titles = [
            "x_left",
            "x_right",
            "y",
            "r_max",
            "theta_left",
            "theta_right",
            "window_length",
            "polyorder",
            "num_avg_left",
            "num_avg_right",
            "thres_ratio_left",
            "thres_ratio_right",
        ]
        values = self.summary_service.read_contiguous_block(experiment.result_summary, experiment.image_name, "XLeft", len(titles), experiment.experiment_no)
        if not values:
            raise ValueError("汇总表中没有找到 XLeft 参数块")
        return {title: value for title, value in zip(titles, values) if value is not None}

    def build_atomization_config(self) -> AtomizationAngleBatchConfig:
        experiment = self.state.experiment
        frames = experiment.frames
        atom = self.state.settings.atomization
        return AtomizationAngleBatchConfig(
            data_dir=str(self.folder),
            fig_start=frames.start,
            fig_end=frames.end,
            decimate=frames.decimate,
            core_num=experiment.core_num,
            x_left=atom.x_left,
            x_right=atom.x_right,
            y=atom.y,
            r_max=atom.r_max,
            theta_left=atom.theta_left,
            theta_right=atom.theta_right,
            num_avg_left=atom.num_avg_left,
            r_start_left=atom.r_start_left,
            num_avg_right=atom.num_avg_right,
            r_start_right=atom.r_start_right,
            thres_ratio_left=atom.thres_ratio_left,
            thres_ratio_right=atom.thres_ratio_right,
            window_length=atom.window_length,
            polyorder=atom.polyorder,
            save_marked_images=atom.save_marked_images,
            mode=atom.mode,
        )
