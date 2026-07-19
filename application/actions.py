from __future__ import annotations

from pathlib import Path

from ImageProcessv3.core.excel_workbook_coordinator import ExcelWorkbookCoordinator
from ImageProcessv3.core.image_io import write_tiff
from ImageProcessv3.core.progress import ProgressCallback
from ImageProcessv3.services.atomization_angle_service import AtomizationAngleService
from ImageProcessv3.services.atomization_result_export_service import AtomizationExportConfig, AtomizationResultExportService
from ImageProcessv3.services.average_image_service import AverageImageService
from ImageProcessv3.services.breakup_length_service import BreakupLengthService
from ImageProcessv3.services.flame_angle_export_service import FlameAngleExportService
from ImageProcessv3.services.flame_angle_service import FlameAngleService
from ImageProcessv3.services.measurement_export_service import MeasurementExportService
from ImageProcessv3.services.sheet_measurement_service import SheetMeasurementService
from ImageProcessv3.services.summary_workbook_service import SummaryWorkbookService

from ImageProcessv3.application.app_state import AppState


class ImageProcessActions:
    def __init__(self, state: AppState) -> None:
        self.state = state
        self.workbook_coordinator = ExcelWorkbookCoordinator()
        self.average_service = AverageImageService()
        self.flame_service = FlameAngleService()
        self.flame_export_service = FlameAngleExportService(self.workbook_coordinator)
        self.summary_service = SummaryWorkbookService(self.workbook_coordinator)
        self.measurement_export_service = MeasurementExportService(self.summary_service, self.workbook_coordinator)
        self.sheet_service = SheetMeasurementService()
        self.breakup_service = BreakupLengthService()
        self.atomization_service = AtomizationAngleService()
        self.atomization_export_service = AtomizationResultExportService(self.workbook_coordinator)

    @property
    def folder(self) -> Path:
        return self.state.experiment.image_folder

    def save_average_image(self, progress_callback: ProgressCallback | None = None) -> Path:
        frames = self.state.experiment.frames
        image = self.average_service.calculate_average(self.folder, frames.frame_numbers(), self.state.experiment.core_num, progress_callback)
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

    def convert_color_to_gray(self, progress_callback: ProgressCallback | None = None) -> None:
        frames = self.state.experiment.frames
        self.average_service.convert_color_to_gray(self.folder, frames.frame_numbers(), self.state.experiment.core_num, progress_callback)

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

    def read_measurement_records(self, file_path: str | Path):
        return self.measurement_export_service.read_records(file_path)

    def calculate_flame_batch(self, progress_callback: ProgressCallback | None = None) -> Path:
        experiment = self.state.experiment
        settings = self.state.settings.flame.to_algorithm_dict(experiment.impact_x, experiment.impact_y)
        frames = experiment.frames
        rows = self.flame_service.calculate_batch(
            self.folder,
            frames.frame_numbers(),
            experiment.core_num,
            settings,
            self.state.settings.flame.save_marked_images,
            progress_callback,
        )
        return self.flame_export_service.export_batch(self.folder, settings, rows)

    def calculate_flame_lightweight_batch(self, progress_callback: ProgressCallback | None = None) -> Path:
        experiment = self.state.experiment
        settings = self.state.settings.flame.to_algorithm_dict(experiment.impact_x, experiment.impact_y)
        frames = experiment.frames
        rows = self.flame_service.calculate_lightweight_batch(self.folder, frames.frame_numbers(), experiment.core_num, settings, progress_callback)
        return self.flame_export_service.export_lightweight_batch(self.folder, settings, rows)

    def run_atomization_batch(self, progress_callback: ProgressCallback | None = None) -> Path:
        experiment = self.state.experiment
        frames = experiment.frames
        atom = self.state.settings.atomization
        result = self.atomization_service.run_batch(
            self.folder,
            frames.frame_numbers(),
            experiment.core_num,
            atom,
            progress_callback,
        )
        export_config = AtomizationExportConfig(
            data_root=self.folder.parent,
            summary_path=experiment.result_summary or Path("__no_summary_workbook__.xlsx"),
            max_freq=atom.max_freq,
            experiment_name=experiment.image_name,
            output_dir=Path(atom.export_dir) if atom.export_dir else None,
        )
        return self.atomization_export_service.export(export_config, atom, result)

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
