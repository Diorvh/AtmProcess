from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from AtmProcess.domain.context import ExperimentContext, FrameSelection


@dataclass
class FlameSettings:
    gain: float = 1.0
    threshold: float = 0.1
    angle_oxidizer: float = 0.0
    angle_fuel: float = 0.0
    angle_momentum: float = 0.0
    scissor_up: int = 0
    scissor_down: int = 0
    scissor_left: int = 0
    scissor_right: int = 0
    save_marked_images: bool = False

    def to_algorithm_dict(self, impact_x: int, impact_y: int) -> dict:
        return {
            "Gain": self.gain,
            "Threshold": self.threshold,
            "AngleO": self.angle_oxidizer,
            "AngleF": self.angle_fuel,
            "AngleCalc": self.angle_momentum,
            "ScissorUp": self.scissor_up,
            "ScissorDown": self.scissor_down,
            "ScissorLeft": self.scissor_left,
            "ScissorRight": self.scissor_right,
            "ImpactX": impact_x,
            "ImpactY": impact_y,
        }


@dataclass
class AtomizationSettings:
    binary_threshold: int = 0
    x_left: int = 0
    x_right: int = 0
    y: int = 0
    r_max: int = 1000
    theta_left: int = -1
    theta_right: int = 1801
    num_avg_left: int = 100
    r_start_left: int = 0
    num_avg_right: int = 100
    r_start_right: int = 0
    thres_ratio_left: float = 0.5
    thres_ratio_right: float = 0.5
    window_length: int = 100
    polyorder: int = 2
    max_freq: int = 100
    frame_rate_hz: float = 40000.0  # 直接作为频谱采样率，不再按抽帧间隔换算
    export_dir: str = ""
    save_marked_images: bool = False


@dataclass
class MeasurementSettings:
    mode: str = "sheet"
    click_mode: str = "left"
    export_dir: str = ""
    left_px: int = 0
    right_px: int = 0
    up_px: int = 0
    down_px: int = 0
    breakup_px: int = 0


@dataclass
class PreviewSettings:
    save_dir: str = ""
    filename: str = ""
    overlay_values: dict[str, bool] = field(default_factory=dict)
    playback_fps: int = 15


@dataclass
class AppSettings:
    experiment: ExperimentContext = field(default_factory=ExperimentContext)
    measurement: MeasurementSettings = field(default_factory=MeasurementSettings)
    preview: PreviewSettings = field(default_factory=PreviewSettings)
    flame: FlameSettings = field(default_factory=FlameSettings)
    atomization: AtomizationSettings = field(default_factory=AtomizationSettings)
    active_page: str = "液膜测量"
    language: str = "zh"

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment": self._context_to_dict(self.experiment),
            "measurement": asdict(self.measurement),
            "preview": asdict(self.preview),
            "flame": asdict(self.flame),
            "atomization": asdict(self.atomization),
            "active_page": self.active_page,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(
            experiment=cls._context_from_dict(data.get("experiment", {})),
            measurement=cls._dataclass_from_dict(MeasurementSettings, data.get("measurement", {})),
            preview=cls._dataclass_from_dict(PreviewSettings, data.get("preview", {})),
            flame=cls._dataclass_from_dict(FlameSettings, data.get("flame", {})),
            atomization=cls._dataclass_from_dict(AtomizationSettings, data.get("atomization", {})),
            active_page=data.get("active_page", "液膜测量"),
            language=data.get("language", "zh"),
        )

    @staticmethod
    def _context_to_dict(context: ExperimentContext) -> dict[str, Any]:
        frames = asdict(context.frames)
        return {
            "data_root": str(context.data_root),
            "experiment_no": context.experiment_no,
            "core_num": context.core_num,
            "direct_folder": str(context.direct_folder) if context.direct_folder else "",
            "direct_image": str(context.direct_image) if context.direct_image else "",
            "image_label": context.image_label,
            "result_summary": str(context.result_summary) if context.result_summary else "",
            "impact_x": context.impact_x,
            "impact_y": context.impact_y,
            "pixel_size_um": context.pixel_size_um,
            "frames": frames,
        }

    @staticmethod
    def _context_from_dict(data: dict[str, Any]) -> ExperimentContext:
        frames_data = data.get("frames", {})
        return ExperimentContext(
            data_root=Path(data.get("data_root", "")),
            experiment_no=int(data.get("experiment_no", 0)),
            core_num=int(data.get("core_num", 4)),
            direct_folder=Path(data["direct_folder"]) if data.get("direct_folder") else None,
            direct_image=Path(data["direct_image"]) if data.get("direct_image") else None,
            image_label=data.get("image_label", ""),
            result_summary=Path(data["result_summary"]) if data.get("result_summary") else None,
            impact_x=int(data.get("impact_x", 0)),
            impact_y=int(data.get("impact_y", 0)),
            pixel_size_um=float(data.get("pixel_size_um", 0.0)),
            frames=FrameSelection(
                start=int(frames_data.get("start", 0)),
                end=int(frames_data.get("end", 0)),
                current=int(frames_data.get("current", 0)),
                decimate=int(frames_data.get("decimate", 1)),
            ),
        )

    @staticmethod
    def _dataclass_from_dict(model, data: dict[str, Any]):
        allowed = {field.name for field in model.__dataclass_fields__.values()}
        return model(**{key: value for key, value in data.items() if key in allowed})
