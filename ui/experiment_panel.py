from __future__ import annotations

from pathlib import Path
from time import perf_counter
import tkinter as tk

from AtmProcess.application.app_state import AppState
from AtmProcess.ui import localized_dialogs as filedialog, localized_widgets as ttk
from AtmProcess.ui.localization import language_for
from AtmProcess.ui.widgets import short_path


class ExperimentPanel(ttk.LabelFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, text="实验参数", padding=8)
        self.state = state
        self.context = state.experiment
        self._change_callbacks = []  # 外部组件可订阅实验参数变化，例如右侧预览刷新
        self._playback_callbacks = []
        self._playback_job = None
        self._playback_running = False
        self._next_frame_deadline = 0.0
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
        self.playback_fps = tk.IntVar(value=self.state.settings.preview.playback_fps)
        self.playback_text = tk.StringVar(value="播放")
        self.frame_text = tk.StringVar(value="")

    def _create_widgets(self) -> None:
        process_row = ttk.Frame(self)
        process_row.pack(fill="x")
        ttk.Label(process_row, text="进程数").pack(side="left")
        self._pack_entry(process_row, self.core_num, width=8)
        ttk.Button(process_row, text="English / 中文", command=self._toggle_language).pack(side="right")

        path_group = ttk.Frame(self)
        path_group.pack(anchor="w", pady=(4, 0))
        self._entry_row(path_group, 0, "数据根目录", self.data_root, self._choose_data_root, role="image_source")
        self._entry_row(path_group, 1, "直接图像目录", self.direct_folder, self._choose_direct_folder, role="image_source")
        self._entry_row(path_group, 2, "直接图像文件", self.direct_image, self._choose_direct_image, role="image_source")
        self._entry_row(path_group, 3, "汇总表", self.result_summary, self._choose_summary)

        frame_row = ttk.Frame(self)
        frame_row.pack(anchor="w", pady=(6, 0))
        ttk.Label(frame_row, text="实验编号").pack(side="left")
        self._pack_stepper(frame_row, self.experiment_no, lambda: self._step_experiment(-1), lambda: self._step_experiment(1), "image_source")
        ttk.Label(frame_row, text="帧范围").pack(side="left", padx=(10, 4))
        self._pack_entry_group(frame_row, [self.frame_start, self.frame_end], 8, "frame_range")
        ttk.Label(frame_row, text="当前帧").pack(side="left", padx=(10, 4))
        frame_controls = self._pack_stepper(frame_row, self.frame_current, lambda: self.step_current_frame(-1), lambda: self.step_current_frame(1), "frame_range")
        ttk.Button(frame_controls, textvariable=self.playback_text, width=5, command=self.toggle_playback).pack(side="left", padx=(4, 0))
        ttk.Label(frame_controls, text="帧率").pack(side="left", padx=(6, 2))
        fps_entry = ttk.Entry(frame_controls, textvariable=self.playback_fps, width=5)
        fps_entry.pack(side="left")
        ttk.Label(frame_controls, text="fps").pack(side="left", padx=(2, 0))
        self._entry_roles[str(fps_entry)] = "playback"
        ttk.Label(frame_row, text="抽帧间隔").pack(side="left", padx=(10, 4))
        decimate_entry = ttk.Entry(frame_row, textvariable=self.decimate, width=8)
        decimate_entry.pack(side="left")
        self._entry_roles[str(decimate_entry)] = "frame_range"
        ttk.Label(frame_row, textvariable=self.frame_text).pack(side="left", padx=(10, 0))

        calibration_row = ttk.Frame(self)
        calibration_row.pack(anchor="w", pady=(6, 0))
        ttk.Label(calibration_row, text="撞击点").pack(side="left")
        self._pack_entry_group(calibration_row, [self.impact_x, self.impact_y], 8, "context", padx=(4, 0))
        ttk.Label(calibration_row, text="像素尺寸 um").pack(side="left", padx=(12, 4))
        self._pack_entry(calibration_row, self.pixel_size_um, width=8)

    def _entry_row(self, parent, row: int, label: str, variable: tk.StringVar, command, role: str = "context") -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        self._grid_entry(parent, row=row, column=1, variable=variable, width=120, padx=(4, 4), role=role)
        ttk.Button(parent, text="浏览", command=command).grid(row=row, column=2, sticky="w")

    def _grid_entry(
        self,
        parent,
        row: int,
        column: int,
        variable: tk.Variable,
        width: int,
        padx=0,
        pady=0,
        role: str = "context",
    ) -> ttk.Entry:
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column, sticky="w", padx=padx, pady=pady)
        self._entry_roles[str(entry)] = role
        return entry

    def _pack_entry(self, parent, variable: tk.Variable, width: int, role: str = "context") -> ttk.Entry:
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.pack(side="left", padx=(4, 0))
        self._entry_roles[str(entry)] = role
        return entry

    def _pack_stepper(self, parent, variable, minus_command, plus_command, role: str) -> ttk.Frame:
        frame = ttk.Frame(parent)
        frame.pack(side="left", padx=(4, 0))
        entry = ttk.Entry(frame, textvariable=variable, width=8)
        entry.pack(side="left")
        ttk.Button(frame, text="-", width=3, command=minus_command).pack(side="left")
        ttk.Button(frame, text="+", width=3, command=plus_command).pack(side="left")
        self._entry_roles[str(entry)] = role
        return frame

    def _pack_entry_group(self, parent, variables: list[tk.Variable], width: int, role: str, padx=0) -> ttk.Frame:
        frame = ttk.Frame(parent)
        frame.pack(side="left", padx=padx)
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
        self.state.settings.preview.playback_fps = max(1, self.playback_fps.get())
        self._normalize_frame_context(update_vars=False)

    def _toggle_language(self) -> None:
        language = language_for(self)
        selected = "en" if language.language == "zh" else "zh"
        language.set_language(selected)  # 只更新显示文字，不提交输入框、不重算、不刷新图像。
        self.state.settings.language = selected

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
        self._update_frame_text_from_context()  # 当前帧等状态由功能页修改时，派生的帧信息也必须同步。

    def commit_entry(self, widget) -> None:
        role = self._entry_roles.get(str(widget))
        if role == "playback":
            self._commit_playback_fps()
            return
        self.stop_playback()
        self.apply_to_state()
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

    def bind_playback(self, callback) -> None:
        self._playback_callbacks.append(callback)

    def _notify_change(self) -> None:
        for callback in self._change_callbacks:
            callback()

    def _notify_playback(self) -> None:
        for callback in self._playback_callbacks:
            callback(self._playback_running)

    def _refresh_frame_info(self) -> None:
        self.stop_playback()
        self.apply_to_state()  # 扫描帧范围前先使用界面上的最新目录和实验编号
        frames = self.state.refresh_frame_selection(reset_current=True)  # 切换实验编号或图像来源后从第一帧开始。
        if frames:
            self.frame_start.set(self.context.frames.start)
            self.frame_end.set(self.context.frames.end)
            self.frame_current.set(self.context.frames.current)
            selected_count = len(self.context.frames.frame_numbers())
            self.frame_text.set(f"帧范围：{frames[0]} - {frames[-1]}，共 {len(frames)} 张，抽帧后 {selected_count} 张，当前帧 {self.context.frames.current}")
        else:
            self.frame_text.set(f"未找到按数字命名的 tif 文件：{short_path(self.context.image_folder)}")
        self._notify_change()

    def _update_frame_text_from_context(self) -> None:
        frames = self.context.frames
        self.frame_text.set(f"帧范围：{frames.start} - {frames.end}，抽帧后 {len(frames.frame_numbers())} 张，当前帧 {frames.current}")

    def _normalize_frame_context(self, update_vars: bool) -> None:
        frames = self.context.frames
        if frames.start > frames.end:
            frames.start, frames.end = frames.end, frames.start  # 允许手动输入时顺序写反，内部保持 start <= end
        frames.normalize_current()  # 当前帧始终属于 start/end/decimate 定义的有效帧集合。
        if update_vars:
            self.frame_start.set(frames.start)
            self.frame_end.set(frames.end)
            self.frame_current.set(frames.current)

    def _step_experiment(self, delta: int) -> None:
        self.experiment_no.set(self.experiment_no.get() + delta)
        self._refresh_frame_info()

    def step_current_frame(self, delta: int) -> None:
        self.apply_to_state()
        self.context.frames.move_current(delta)
        self.refresh_from_state()
        self._notify_change()

    def toggle_playback(self) -> None:
        if self._playback_running:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self) -> None:
        self._commit_playback_fps()
        if self.context.frames.current == self.context.frames.frame_numbers()[-1]:
            return
        self._playback_running = True
        self.playback_text.set("暂停")
        self._next_frame_deadline = perf_counter()
        self._notify_playback()
        self._playback_tick()

    def stop_playback(self) -> None:
        if self._playback_job is not None:
            self.after_cancel(self._playback_job)
            self._playback_job = None
        if not self._playback_running:
            return
        self._playback_running = False
        self.playback_text.set("播放")
        self._notify_playback()

    def _playback_tick(self) -> None:
        if not self._playback_running:
            return
        self._playback_job = None
        previous = self.context.frames.current
        self.step_current_frame(1)
        if self.context.frames.current == previous:
            self.stop_playback()
            return
        interval = 1.0 / self.playback_fps.get()
        self._next_frame_deadline += interval
        now = perf_counter()
        if self._next_frame_deadline < now:
            self._next_frame_deadline = now
        delay_ms = max(1, round((self._next_frame_deadline - now) * 1000))
        self._playback_job = self.after(delay_ms, self._playback_tick)

    def _commit_playback_fps(self) -> None:
        fps = max(1, self.playback_fps.get())
        self.playback_fps.set(fps)
        self.state.settings.preview.playback_fps = fps

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
