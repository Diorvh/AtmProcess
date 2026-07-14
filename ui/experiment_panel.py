from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

from ImageProcessv2.application.app_state import AppState
from ImageProcessv2.ui.widgets import short_path


class ExperimentPanel(ttk.LabelFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, text="实验参数", padding=8)
        self.state = state
        self.context = state.experiment
        self._change_callbacks = []  # 外部组件可订阅实验参数变化，例如右侧预览刷新
        self._entry_roles: dict[str, str] = {}  # 记录 Entry 类型，回车提交时判断是否需要重扫帧范围
        self._create_vars()
        self._create_widgets()
        self._refresh_frame_info()

    def _create_vars(self) -> None:
        self.data_root = tk.StringVar(value=str(self.context.data_root))
        self.experiment_no = tk.IntVar(value=self.context.experiment_no)
        self.core_num = tk.IntVar(value=self.context.core_num)
        self.direct_folder = tk.StringVar(value=str(self.context.direct_folder or ""))
        self.direct_image = tk.StringVar(value=str(self.context.direct_image or ""))
        self.result_summary = tk.StringVar(value=str(self.context.result_summary or ""))
        self.impact_x = tk.IntVar(value=self.context.impact_x)
        self.impact_y = tk.IntVar(value=self.context.impact_y)
        self.pixel_size_um = tk.DoubleVar(value=self.context.pixel_size_um)
        self.frame_start = tk.IntVar(value=self.context.frames.start)
        self.frame_end = tk.IntVar(value=self.context.frames.end)
        self.frame_current = tk.IntVar(value=self.context.frames.current)
        self.decimate = tk.IntVar(value=self.context.frames.decimate)
        self.frame_text = tk.StringVar(value="")

    def _create_widgets(self) -> None:
        ttk.Label(self, text="进程数").grid(row=0, column=0, sticky="w")
        self._grid_entry(row=0, column=1, variable=self.core_num, width=8)

        self._entry_row(1, "数据根目录", self.data_root, self._choose_data_root, role="image_source")
        self._entry_row(2, "直接图像目录", self.direct_folder, self._choose_direct_folder, role="image_source")
        self._entry_row(3, "直接图像文件", self.direct_image, self._choose_direct_image, role="image_source")
        self._entry_row(4, "汇总表", self.result_summary, self._choose_summary)

        row = 5
        ttk.Label(self, text="实验编号").grid(row=row, column=0, sticky="w", pady=(6, 0))
        self._grid_stepper(row=row, column=1, variable=self.experiment_no, minus_command=lambda: self._step_experiment(-1), plus_command=lambda: self._step_experiment(1), pady=(6, 0), role="image_source")
        ttk.Label(self, text="帧范围").grid(row=row, column=2, sticky="e", padx=(12, 4), pady=(6, 0))
        self._grid_entry_group(row=row, column=3, variables=[self.frame_start, self.frame_end], width=8, pady=(6, 0), role="frame_range")
        ttk.Label(self, text="当前帧").grid(row=row, column=4, sticky="e", padx=(12, 4), pady=(6, 0))
        self._grid_stepper(row=row, column=5, variable=self.frame_current, minus_command=lambda: self._step_current_frame(-1), plus_command=lambda: self._step_current_frame(1), pady=(6, 0), role="frame_range")
        ttk.Label(self, text="抽帧间隔").grid(row=row, column=6, sticky="e", padx=(12, 4), pady=(6, 0))
        self._grid_entry(row=row, column=7, variable=self.decimate, width=8, pady=(6, 0))
        ttk.Label(self, textvariable=self.frame_text).grid(row=row, column=8, sticky="w", padx=(12, 0), pady=(6, 0))

        ttk.Label(self, text="撞击点").grid(row=6, column=0, sticky="w")
        self._grid_entry_group(row=6, column=1, variables=[self.impact_x, self.impact_y], width=8)

        ttk.Label(self, text="像素尺寸 um").grid(row=6, column=2, sticky="e", padx=(12, 4))
        self._grid_entry(row=6, column=3, variable=self.pixel_size_um, width=8)

    def _entry_row(self, row: int, label: str, variable: tk.StringVar, command, start_column: int = 0, role: str = "context") -> None:
        ttk.Label(self, text=label).grid(row=row, column=start_column, sticky="w")
        self._grid_entry(row=row, column=start_column + 1, variable=variable, width=120, columnspan=4, padx=(4, 4), role=role)
        ttk.Button(self, text="浏览", command=command).grid(row=row, column=start_column + 5, sticky="w")

    def _grid_entry(
        self,
        row: int,
        column: int,
        variable: tk.Variable,
        width: int,
        columnspan: int = 1,
        padx=0,
        pady=0,
        role: str = "context",
    ) -> ttk.Entry:
        entry = ttk.Entry(self, textvariable=variable, width=width)
        entry.grid(row=row, column=column, columnspan=columnspan, sticky="w", padx=padx, pady=pady)
        self._entry_roles[str(entry)] = role
        return entry

    def _grid_stepper(
        self,
        row: int,
        column: int,
        variable: tk.Variable,
        minus_command,
        plus_command,
        pady=0,
        role: str = "context",
    ) -> ttk.Frame:
        frame = ttk.Frame(self)
        frame.grid(row=row, column=column, sticky="w", pady=pady)
        entry = ttk.Entry(frame, textvariable=variable, width=8)
        entry.pack(side="left")
        ttk.Button(frame, text="-", width=3, command=minus_command).pack(side="left")
        ttk.Button(frame, text="+", width=3, command=plus_command).pack(side="left")
        self._entry_roles[str(entry)] = role
        return frame

    def _grid_entry_group(
        self,
        row: int,
        column: int,
        variables: list[tk.Variable],
        width: int,
        pady=0,
        role: str = "context",
    ) -> ttk.Frame:
        frame = ttk.Frame(self)
        frame.grid(row=row, column=column, sticky="w", pady=pady)
        for variable in variables:
            entry = ttk.Entry(frame, textvariable=variable, width=width)
            entry.pack(side="left")
            self._entry_roles[str(entry)] = role
        return frame

    def apply_to_state(self) -> None:
        context = self.context  # Tk 变量只属于界面层，业务层统一读取 dataclass
        context.data_root = Path(self.data_root.get())
        context.experiment_no = self.experiment_no.get()
        context.core_num = self.core_num.get()
        context.direct_folder = Path(self.direct_folder.get()) if self.direct_folder.get() else None
        context.direct_image = Path(self.direct_image.get()) if self.direct_image.get() else None
        context.result_summary = Path(self.result_summary.get()) if self.result_summary.get() else None
        context.impact_x = self.impact_x.get()
        context.impact_y = self.impact_y.get()
        context.pixel_size_um = self.pixel_size_um.get()
        context.frames.start = self.frame_start.get()
        context.frames.end = self.frame_end.get()
        context.frames.current = self.frame_current.get()
        context.frames.decimate = self.decimate.get()
        self._normalize_frame_context(update_vars=False)

    def refresh_from_state(self) -> None:
        context = self.context  # 取点等操作先改 AppState，再回填到输入框
        self.data_root.set(str(context.data_root))
        self.experiment_no.set(context.experiment_no)
        self.core_num.set(context.core_num)
        self.direct_folder.set(str(context.direct_folder or ""))
        self.direct_image.set(str(context.direct_image or ""))
        self.result_summary.set(str(context.result_summary or ""))
        self.impact_x.set(context.impact_x)
        self.impact_y.set(context.impact_y)
        self.pixel_size_um.set(context.pixel_size_um)
        self.frame_start.set(context.frames.start)
        self.frame_end.set(context.frames.end)
        self.frame_current.set(context.frames.current)
        self.decimate.set(context.frames.decimate)

    def commit_entry(self, widget) -> None:
        self.apply_to_state()
        role = self._entry_roles.get(str(widget))
        if role == "image_source":
            self._refresh_frame_info()  # 实验编号或图像目录变化后，必须重新扫描可用帧
        elif role == "frame_range":
            self._normalize_frame_context(update_vars=True)
            self._update_frame_text_from_context()  # 手动改帧范围时不重扫，避免覆盖用户输入
            self._notify_change()
        else:
            self._notify_change()

    def bind_change(self, callback) -> None:
        self._change_callbacks.append(callback)

    def _notify_change(self) -> None:
        for callback in self._change_callbacks:
            callback()

    def _refresh_frame_info(self) -> None:
        self.apply_to_state()  # 扫描帧范围前先使用界面上的最新目录和实验编号
        frames = self.state.refresh_frame_selection()
        if frames:
            self.frame_start.set(self.context.frames.start)
            self.frame_end.set(self.context.frames.end)
            self.frame_current.set(self.context.frames.current)
            self.frame_text.set(f"帧范围：{frames[0]} - {frames[-1]}，共 {len(frames)} 张，当前帧 {self.context.frames.current}")
        else:
            self.frame_text.set(f"未找到按数字命名的 tif 文件：{short_path(self.context.image_folder)}")
        self._notify_change()

    def _update_frame_text_from_context(self) -> None:
        frames = self.context.frames
        self.frame_text.set(f"帧范围：{frames.start} - {frames.end}，当前帧 {frames.current}")

    def _normalize_frame_context(self, update_vars: bool) -> None:
        frames = self.context.frames
        if frames.start > frames.end:
            frames.start, frames.end = frames.end, frames.start  # 允许手动输入时顺序写反，内部保持 start <= end
        if frames.current < frames.start or frames.current > frames.end:
            frames.current = frames.start
        if update_vars:
            self.frame_start.set(frames.start)
            self.frame_end.set(frames.end)
            self.frame_current.set(frames.current)

    def _step_experiment(self, delta: int) -> None:
        self.experiment_no.set(self.experiment_no.get() + delta)
        self._refresh_frame_info()

    def _step_current_frame(self, delta: int) -> None:
        self.frame_current.set(self.frame_current.get() + delta)
        self.apply_to_state()
        self._normalize_frame_context(update_vars=True)
        self._update_frame_text_from_context()
        self._notify_change()

    def _choose_data_root(self) -> None:
        path = filedialog.askdirectory(title="选择数据根目录")
        if path:
            self.data_root.set(path)
            self._refresh_frame_info()

    def _choose_direct_folder(self) -> None:
        path = filedialog.askdirectory(title="选择直接图像目录")
        if path:
            self.direct_folder.set(path)
            self._refresh_frame_info()

    def _choose_direct_image(self) -> None:
        path = filedialog.askopenfilename(title="选择图像文件", filetypes=[("TIFF 图像", "*.tif"), ("全部文件", "*.*")])
        if path:
            self.direct_image.set(path)
            self._refresh_frame_info()

    def _choose_summary(self) -> None:
        path = filedialog.askopenfilename(title="选择汇总表", filetypes=[("Excel 表格", "*.xlsx"), ("全部文件", "*.*")])
        if path:
            self.result_summary.set(path)
