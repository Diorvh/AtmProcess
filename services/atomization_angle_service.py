from __future__ import annotations

from pathlib import Path

from ImageProcessv2.core.atomization_angle_runner import (
    AtomizationAngleBatchConfig,
    AtomizationAngleCppRunner,
    AtomizationAngleRunResult,
)
from ImageProcessv2.services.atomization_result_export_service import AtomizationPostprocessConfig, AtomizationResultExportService


class AtomizationAngleService:
    def __init__(self, cpp_dir: str | Path, open_workbooks: bool = True) -> None:
        self.cpp_dir = Path(cpp_dir)
        self.open_workbooks = open_workbooks
        self.runner = AtomizationAngleCppRunner(cpp_dir)
        self.export_service = AtomizationResultExportService()

    def run_batch(
        self,
        config: AtomizationAngleBatchConfig,
        summary_path: str | Path | None = None,
        max_freq: int = 100,
        output_dir: str | Path | None = None,
    ) -> AtomizationAngleRunResult:
        run_result = self.runner.run_batch(config)
        result_workbook = None
        if config.mode == 1:
            result_workbook = self.export_service.export_from_csv(self._postprocess_config(config, run_result, summary_path, max_freq, output_dir))
        return AtomizationAngleRunResult(run_result.process, run_result.work_dir, run_result.input_path, run_result.result_csv, result_workbook)

    def _postprocess_config(
        self,
        config: AtomizationAngleBatchConfig,
        run_result: AtomizationAngleRunResult,
        summary_path: str | Path | None,
        max_freq: int,
        output_dir: str | Path | None = None,
    ) -> AtomizationPostprocessConfig:
        data_dir = Path(config.data_dir)
        return AtomizationPostprocessConfig(
            data_root=data_dir.parent,
            summary_path=Path(summary_path) if summary_path else Path("__no_summary_workbook__.xlsx"),
            max_freq=max_freq,
            experiment_name=data_dir.name,
            result_csv=run_result.result_csv,
            output_dir=Path(output_dir) if output_dir else None,
            open_workbooks=self.open_workbooks,
        )
