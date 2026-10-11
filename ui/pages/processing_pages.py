from __future__ import annotations

import tkinter as tk

import cv2 as cv
import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.signal import savgol_filter

from AtmProcess.application.actions import ProcessingActions
from AtmProcess.application.app_state import AppState
from AtmProcess.core.image_io import read_image
from AtmProcess.lib.lib_AtmAngle import build_sampling_geometry, calculate_grayavg_byangle, find_last_greater_equal
from AtmProcess.services.atomization_preview_export_service import AtomizationPreviewExportService
from AtmProcess.ui import localized_dialogs as filedialog, localized_widgets as ttk
from AtmProcess.ui.localization import language_for
from AtmProcess.ui.preview.image_preview_pane import ImagePreviewPane, draw_angle_line
from AtmProcess.ui.widgets import ActionFrame, BoundForm, FormField, labeled_entry


mpl.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "Arial Unicode MS", "DejaVu Sans"]
mpl.rcParams["axes.unicode_minus"] = False


class ProcessingPages(ttk.Notebook):
    def __init__(
        self,
        master,
        state: AppState,
        actions: ProcessingActions,
        apply_context,
        sync_experiment_views,
        preview: ImagePreviewPane,
    ) -> None:
        super().__init__(master)
        self.state = state
        self.preview = preview  # 所有页面共用右侧预览窗格
        self.page_titles = ["液膜测量", "平均图", "火焰锥角", "雾化锥角"]
        self.pages = [
            MeasurementPage(self, state, actions, apply_context, sync_experiment_views, preview),
            AveragePage(self, state, actions, apply_context, sync_experiment_views, preview),
            FlameBatchPage(self, state, actions, apply_context, sync_experiment_views, preview),
            AtomizationPage(self, state, actions, apply_context, sync_experiment_views, preview),
        ]
        for page, title in zip(self.pages, self.page_titles):
            self.add(page, text=title)
        self._restore_active_page()
        self.bind("<<NotebookTabChanged>>", self._activate_current_page)  # 切页后更换预览逻辑
        self.after(0, self._activate_current_page)  # 首次显示时 Notebook 还没有选中事件

    def _activate_current_page(self, *_):
        self.state.settings.active_page = self.page_titles[self.index(self.select())]
        page = self.nametowidget(self.select())
        page.activate_preview()

    def _restore_active_page(self) -> None:
        if self.state.settings.active_page in self.page_titles:
            self.select(self.page_titles.index(self.state.settings.active_page))

    def handle_shortcut(self, event) -> bool:
        page = self.nametowidget(self.select())
        if hasattr(page, "handle_shortcut"):
            return page.handle_shortcut(event)
        return False

    def handle_experiment_context_changed(self) -> None:
        for page in self.pages:
            handler = getattr(page, "handle_experiment_context_changed", None)
            if handler is not None:
                handler()

    def handle_playback_changed(self, running: bool) -> None:
        page = self.nametowidget(self.select())
        handler = getattr(page, "handle_playback_changed", None)
        if handler is not None:
            handler(running)


# 各功能页只定义自己的参数、按钮、预览图层和取点逻辑；右侧预览窗格由基类统一注册。
class PreviewActionFrame(ActionFrame):
    def __init__(self, master, state: AppState, actions: ProcessingActions, apply_context, sync_experiment_views, preview: ImagePreviewPane) -> None:
        super().__init__(master, apply_context)
        self.state = state
        self.actions = actions
        self.sync_experiment_views = sync_experiment_views
        self.preview = preview

    def activate_preview(self) -> None:
        self.preview.set_renderer(self.render_preview)  # 当前页决定图上画什么
        self.preview.set_click_handler(self.handle_preview_click)  # 当前页决定鼠标点击修改什么参数
        self.preview.set_filename_provider(self.preview_filename)
        self.preview.set_click_modes(self.click_modes())  # 取点动作单选
        self.preview.set_overlay_options(self.overlay_options())  # 显示图层多选
        self.preview.refresh()

    def click_modes(self) -> list[tuple[str, str]]:
        return []

    def preview_filename(self) -> str:
        return f"{self.state.experiment.image_name}_{self.state.experiment.frames.current}_预览图.tif"

    def overlay_options(self) -> list[tuple[str, str] | tuple[str, str, bool]]:
        return []

    def handle_preview_click(self, x: int, y: int, mode: str) -> None:
        return None

    def render_preview(self, image: np.ndarray, _source: np.ndarray | None = None) -> np.ndarray:
        self.apply_context()  # 渲染前先把上方实验参数写回 AppState
        return image

    def bind_preview_refresh(self, variables: list[tk.Variable]) -> None:
        for variable in variables:
            variable.trace_add("write", lambda *_: self.preview.refresh())  # 仅用于 checkbox 等明确控件，不绑定普通 Entry 变量


class MeasurementPage(PreviewActionFrame):
    def __init__(self, master, state: AppState, actions: ProcessingActions, apply_context, sync_experiment_views, preview: ImagePreviewPane) -> None:
        super().__init__(master, state, actions, apply_context, sync_experiment_views, preview)
        measurement = state.settings.measurement
        self.mode = tk.StringVar(value=measurement.mode)
        self.export_dir = tk.StringVar(value=measurement.export_dir)
        self.left_px = tk.IntVar(value=measurement.left_px)
        self.right_px = tk.IntVar(value=measurement.right_px)
        self.up_px = tk.IntVar(value=measurement.up_px)
        self.down_px = tk.IntVar(value=measurement.down_px)
        self.breakup_px = tk.IntVar(value=measurement.breakup_px)
        self.sheet_result_text = tk.StringVar(value="")
        self.breakup_result_text = tk.StringVar(value="")
        self.result_text = tk.StringVar(value="")
        self.record_stats_text = tk.StringVar(value="已记录 0 点")
        self.sheet_records: list[list] = []
        self.breakup_records: list[list] = []
        self._records_context_key = self._measurement_context_key()
        self._last_synced_breakup_frame: int | None = None
        self.table_display_width = 620
        self.table_height = 205
        self._resize_start_y = 0
        self._resize_start_height = self.table_height

        ttk.Radiobutton(self, text="液膜边界测量", variable=self.mode, value="sheet", command=self._mode_changed).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self, text="破碎长度测量", variable=self.mode, value="breakup", command=self._mode_changed).grid(row=0, column=1, sticky="w")

        labeled_entry(self, 1, 0, "左边界 px", self.left_px)
        labeled_entry(self, 1, 2, "右边界 px", self.right_px)
        labeled_entry(self, 2, 0, "上边界 px", self.up_px)
        labeled_entry(self, 2, 2, "下边界 px", self.down_px)
        ttk.Label(self, textvariable=self.sheet_result_text, wraplength=self.table_display_width).grid(row=3, column=0, columnspan=6, sticky="w", pady=(4, 0))

        labeled_entry(self, 4, 0, "破碎位置 px", self.breakup_px)
        ttk.Label(self, textvariable=self.breakup_result_text, wraplength=self.table_display_width).grid(row=4, column=2, columnspan=4, sticky="w", pady=(4, 0))

        ttk.Label(self, text="导出目录").grid(row=5, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(self, textvariable=self.export_dir, width=120).grid(row=5, column=1, columnspan=4, sticky="w", padx=(4, 4), pady=(8, 0))
        ttk.Button(self, text="浏览", command=self._choose_export_dir).grid(row=5, column=5, sticky="w", pady=(8, 0))

        ttk.Button(self, text="记录并下一帧 (3)", command=self._record_and_next).grid(row=6, column=0, sticky="w", pady=(8, 0))
        ttk.Button(self, text="删除当前记录并上一帧 (9)", command=self._delete_and_previous).grid(row=6, column=1, sticky="w", pady=(8, 0))
        ttk.Button(self, text="导出当前数据", command=self._export_records).grid(row=6, column=2, sticky="w", pady=(8, 0))
        ttk.Button(self, text="读取已有数据", command=self._read_records).grid(row=6, column=3, sticky="w", pady=(8, 0))

        self.table_frame = ttk.Frame(self, width=self.table_display_width, height=self.table_height)
        self.table_frame.grid(row=7, column=0, columnspan=8, sticky="w", pady=(8, 0))
        self.table_frame.grid_propagate(False)
        self.table = ttk.Treeview(self.table_frame, show="headings", height=8)
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table_scroll_x = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.table.xview)
        self.table_scroll_x.grid(row=1, column=0, sticky="ew")
        self.table_scroll_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.table_scroll_y.grid(row=0, column=1, sticky="ns")
        self.table.configure(xscrollcommand=self.table_scroll_x.set, yscrollcommand=self.table_scroll_y.set)
        self.table_frame.columnconfigure(0, weight=1)
        self.table_frame.rowconfigure(0, weight=1)

        self.table_resize_handle = ttk.Label(self, text="拖动这里调整表格高度", anchor="center", cursor="sb_v_double_arrow")
        self.table_resize_handle.grid(row=8, column=0, columnspan=8, sticky="ew")
        self.table_resize_handle.bind("<ButtonPress-1>", self._start_table_resize)
        self.table_resize_handle.bind("<B1-Motion>", self._resize_table)

        ttk.Label(self, textvariable=self.record_stats_text, wraplength=self.table_display_width, justify="left").grid(row=9, column=0, columnspan=8, sticky="w", pady=(6, 0))
        self.add_status(10)
        self._bind_measurement_state()
        self._update_results()
        self._mode_changed()

    def _bind_measurement_state(self) -> None:
        self.mode.trace_add("write", lambda *_: self._mode_changed())

    def handle_experiment_context_changed(self) -> None:
        context_key = self._measurement_context_key()
        if context_key == self._records_context_key:
            return
        self._records_context_key = context_key
        self.sheet_records.clear()
        self.breakup_records.clear()
        self._last_synced_breakup_frame = None
        self._refresh_table()
        self.status.set("已切换实验数据，已清空液膜与破碎长度记录")

    def _measurement_context_key(self) -> tuple:
        experiment = self.state.experiment
        return (
            experiment.experiment_no,
            str(experiment.data_root),
            str(experiment.direct_folder or ""),
            str(experiment.direct_image or ""),
        )

    def _measurement_changed(self) -> None:
        self.apply_to_state()
        self._update_results()
        self.preview.refresh()

    def apply_to_state(self) -> None:
        measurement = self.state.settings.measurement
        measurement.mode = self.mode.get()
        measurement.click_mode = self.preview.click_mode.get()
        measurement.export_dir = self.export_dir.get()
        measurement.left_px = self.left_px.get()
        measurement.right_px = self.right_px.get()
        measurement.up_px = self.up_px.get()
        measurement.down_px = self.down_px.get()
        measurement.breakup_px = self.breakup_px.get()

    def click_modes(self) -> list[tuple[str, str]]:
        if self.mode.get() == "breakup":
            return [("breakup", "破碎位置")]
        return [("left", "左边界"), ("right", "右边界"), ("up", "上边界"), ("down", "下边界")]

    def preview_filename(self) -> str:
        suffix = "破碎长度测量预览" if self.mode.get() == "breakup" else "液膜边界测量预览"
        return f"{self.state.experiment.image_name}_{self.state.experiment.frames.current}_{suffix}.tif"

    def overlay_options(self) -> list[tuple[str, str] | tuple[str, str, bool]]:
        return [
            ("sheet", "液膜边界"),
            ("breakup", "破碎位置"),
        ]

    def handle_preview_click(self, x: int, y: int, mode: str) -> None:
        if mode == "left":
            self.left_px.set(x)  # x 类边界取横坐标
        elif mode == "right":
            self.right_px.set(x)
        elif mode == "up":
            self.up_px.set(y)  # y 类边界取纵坐标
        elif mode == "down":
            self.down_px.set(y)
        elif mode == "breakup":
            self.breakup_px.set(y)

    def render_preview(self, image: np.ndarray, source: np.ndarray | None = None) -> np.ndarray:
        super().render_preview(image, source)
        self._sync_breakup_position_for_current_frame()
        self.apply_to_state()
        self._update_results()
        height, width = image.shape[:2]
        if self.preview.overlay_enabled("sheet"):
            _draw_vertical(image, self.left_px.get(), (255, 0, 0), width, height)  # 液膜左右边界
            _draw_vertical(image, self.right_px.get(), (255, 0, 0), width, height)
            _draw_horizontal(image, self.up_px.get(), (0, 255, 0), width, height)  # 液膜上下边界
            _draw_horizontal(image, self.down_px.get(), (0, 255, 0), width, height)
        if self.preview.overlay_enabled("breakup"):
            _draw_horizontal(image, self.breakup_px.get(), (255, 255, 0), width, height)  # 破碎位置
        return image

    def handle_shortcut(self, event) -> bool:
        if self.mode.get() == "sheet":
            if event.char in {"2", "4", "6", "8"}:
                mode = {"2": "down", "4": "left", "6": "right", "8": "up"}[event.char]
                self.preview.click_mode.set(mode)
                self.apply_to_state()
                return True
            if event.keysym in {"Left", "Right", "Up", "Down"}:
                self._nudge_sheet_boundary(event.keysym)
                return True
        else:
            if event.keysym == "Up":
                self.breakup_px.set(self.breakup_px.get() - 1)
                return True
            if event.keysym == "Down":
                self.breakup_px.set(self.breakup_px.get() + 1)
                return True
        if event.char == "3":
            self._record_and_next()
            return True
        if event.char == "9":
            self._delete_and_previous()
            return True
        return False

    def _mode_changed(self) -> None:
        self.apply_to_state()
        self.preview.set_click_modes(self.click_modes())
        preferred = self.state.settings.measurement.click_mode
        valid = {mode for mode, _ in self.click_modes()}
        if preferred in valid:
            self.preview.click_mode.set(preferred)
        elif self.mode.get() == "breakup":
            self.preview.click_mode.set("breakup")
        else:
            self.preview.click_mode.set("left")
        self._refresh_table()
        self.preview.refresh()

    def _update_results(self) -> None:
        sheet = self._sheet_result()
        breakup = self._breakup_result()
        self.sheet_result_text.set(
            f"液膜宽度：{sheet.width_px} pix / {sheet.width_mm:.4g} mm；液膜长度：{sheet.length_px} pix / {sheet.length_mm:.4g} mm"
        )
        self.breakup_result_text.set(f"破碎长度：{breakup.length_px} pix / {breakup.length_mm:.4g} mm")

    def _sheet_result(self):
        return self.actions.calculate_sheet(self.left_px.get(), self.right_px.get(), self.up_px.get(), self.down_px.get())

    def _breakup_result(self):
        return self.actions.calculate_breakup(self.breakup_px.get())

    def _nudge_sheet_boundary(self, key: str) -> None:
        mode = self.preview.click_mode.get()
        if mode in {"left", "right"} and key in {"Left", "Right"}:
            variable = self.left_px if mode == "left" else self.right_px
            variable.set(variable.get() + (-1 if key == "Left" else 1))
        elif mode in {"up", "down"} and key in {"Up", "Down"}:
            variable = self.up_px if mode == "up" else self.down_px
            variable.set(variable.get() + (-1 if key == "Up" else 1))

    def _record_current(self) -> None:
        if self.mode.get() == "breakup":
            row = self._breakup_row()
            self._upsert_record(self.breakup_records, row)
        else:
            row = self._sheet_row()
            self._upsert_record(self.sheet_records, row)
        self._refresh_table()
        self.status.set(f"已记录当前帧：{self.state.experiment.frames.current}")

    def _record_and_next(self) -> None:
        self._record_current()
        self._step_frame(1)

    def _delete_and_previous(self) -> None:
        records = self.breakup_records if self.mode.get() == "breakup" else self.sheet_records
        current = self.state.experiment.frames.current
        records[:] = [row for row in records if row[1] != current]
        self._refresh_table()
        self._step_frame(-1)

    def _step_frame(self, delta: int) -> None:
        frames = self.state.experiment.frames
        frames.move_current(delta)
        self.sync_experiment_views()
        self.preview.refresh()

    def _sheet_row(self) -> list:
        result = self._sheet_result()
        experiment = self.state.experiment
        return [
            experiment.current_image_path.stem,
            experiment.frames.current,
            self.left_px.get(),
            self.right_px.get(),
            self.up_px.get(),
            self.down_px.get(),
            result.width_px,
            result.width_mm,
            result.length_px,
            result.length_mm,
        ]

    def _breakup_row(self) -> list:
        result = self._breakup_result()
        experiment = self.state.experiment
        return [
            experiment.current_image_path.stem,
            experiment.frames.current,
            self.breakup_px.get(),
            result.length_px,
            result.length_mm,
        ]

    def _sync_breakup_position_for_current_frame(self) -> None:
        current_frame = self.state.experiment.frames.current
        if current_frame == self._last_synced_breakup_frame:
            return
        self._last_synced_breakup_frame = current_frame
        for row in self.breakup_records:
            if row[1] == current_frame:
                self.breakup_px.set(row[2])  # 破碎记录保存的是黄线对应的 y 坐标。
                return

    def _upsert_record(self, records: list[list], row: list) -> None:
        current = row[1]
        for index, existing in enumerate(records):
            if existing[1] == current:
                records[index] = row
                break
        else:
            records.append(row)
        records.sort(key=lambda item: item[1])

    def _refresh_table(self) -> None:
        headings = self.actions.measurement_export_service.breakup_headers if self.mode.get() == "breakup" else self.actions.measurement_export_service.sheet_headers
        records = self.breakup_records if self.mode.get() == "breakup" else self.sheet_records
        display_headings = headings  # 内部记录仍保留图名称，GUI 和 Excel 均不显示该列
        self.table["columns"] = display_headings
        for heading in display_headings:
            self.table.heading(heading, text=heading)
            self.table.column(heading, width=72, minwidth=56, anchor="center", stretch=False)
        self.table.delete(*self.table.get_children())
        for row in records:
            self.table.insert("", "end", values=row[1:])
        self._refresh_record_stats()

    def _start_table_resize(self, event) -> None:
        self._resize_start_y = event.y_root
        self._resize_start_height = self.table_frame.winfo_height()

    def _resize_table(self, event) -> None:
        height = max(120, min(520, self._resize_start_height + event.y_root - self._resize_start_y))
        self.table_frame.configure(height=height)

    def _choose_export_dir(self) -> None:
        path = filedialog.askdirectory(title="选择导出目录", initialdir=self.export_dir.get() or None)
        if path:
            self.export_dir.set(path)
            self._measurement_changed()

    def _refresh_record_stats(self) -> None:
        records = self.breakup_records if self.mode.get() == "breakup" else self.sheet_records
        if not records:
            self.record_stats_text.set("已记录 0 点")
            return
        if self.mode.get() == "breakup":
            lengths = np.array([row[4] for row in records], dtype=float)
            self.record_stats_text.set(f"已记录 {len(records)} 点；破碎长度平均值：{np.mean(lengths):.4g} mm；标准差：{_std(lengths):.4g} mm")
            return
        widths = np.array([row[7] for row in records], dtype=float)
        lengths = np.array([row[9] for row in records], dtype=float)
        self.record_stats_text.set(
            f"已记录 {len(records)} 点；液膜宽度平均值：{np.mean(widths):.4g} mm；标准差：{_std(widths):.4g} mm；"
            f"液膜长度平均值：{np.mean(lengths):.4g} mm；标准差：{_std(lengths):.4g} mm"
        )

    def _export_records(self) -> None:
        records = self.breakup_records if self.mode.get() == "breakup" else self.sheet_records
        if not records:
            self.status.set("没有可导出的记录")
            return
        output_dir = self.export_dir.get()
        if not output_dir:
            self.status.set("请先选择导出目录")
            return
        if self.mode.get() == "breakup":
            path = self.actions.export_breakup_records(records, output_dir)
        else:
            path = self.actions.export_sheet_records(records, output_dir)
        self.status.set(f"导出完成：{path}")

    def _read_records(self) -> None:
        path = filedialog.askopenfilename(
            title="选择液膜或破碎长度结果文件",
            filetypes=[("Excel 表格", "*.xlsx"), ("全部文件", "*.*")],
        )
        if not path:
            return
        result = self.run_action("读取已有数据", self.apply_to_state, lambda: self.actions.read_measurement_records(path))
        if result is None:
            return

        self.sheet_records.clear()
        self.breakup_records.clear()
        records = self.breakup_records if result.mode == "breakup" else self.sheet_records
        records.extend(result.rows)
        self._records_context_key = self._measurement_context_key()
        self._last_synced_breakup_frame = None
        self.mode.set(result.mode)
        self._refresh_table()
        mode_name = "破碎长度" if result.mode == "breakup" else "液膜尺寸"
        self.status.set(f"已读取 {len(result.rows)} 条{mode_name}记录")


class AveragePage(PreviewActionFrame):
    def __init__(self, master, state: AppState, actions: ProcessingActions, apply_context, sync_experiment_views, preview: ImagePreviewPane) -> None:
        super().__init__(master, state, actions, apply_context, sync_experiment_views, preview)
        ttk.Label(self, text="帧范围、实验目录和进程数使用上方实验参数面板。右侧显示当前帧或刚生成的平均图。", wraplength=620, justify="left").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Button(self, text="彩色转灰度", command=self._convert_gray).grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Button(self, text="计算并保存平均图", command=self._save_average).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        self.add_status(2)

    def preview_filename(self) -> str:
        return f"{self.state.experiment.image_name}_{self.state.experiment.frames.current}_平均图预览.tif"

    def _save_average(self) -> None:
        result = self.run_progress_action("计算平均图", lambda: None, self.actions.save_average_image)
        if result is not None:
            from AtmProcess.core.image_io import read_image
            from AtmProcess.ui.preview.image_preview_pane import to_rgb8

            image = read_image(result)
            self.preview.show_array(to_rgb8(image), result, source=image)  # 平均图生成后直接显示结果图

    def _convert_gray(self) -> None:
        self.run_progress_action("彩色转灰度", lambda: None, self.actions.convert_color_to_gray)
        self.preview.refresh()


class AtomizationProfilePanel(ttk.Frame):
    titles = ("左侧原始", "右侧原始", "左侧滤波", "右侧滤波")

    def __init__(self, master, export_command) -> None:
        super().__init__(master)
        self.export_command = export_command
        self.data: dict[str, tuple[np.ndarray, np.ndarray, float | None]] = {}
        self.figure = Figure(figsize=(5.6, 4.0), dpi=100)
        self.axes = self.figure.subplots(2, 2).ravel()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.artists = {}
        self._backgrounds = []
        self._initialized = False
        self._language = language_for(self)
        self._language.register(self)

        for title, axis in zip(self.titles, self.axes):
            axis.set_title(self._language.text(title), fontsize=9)
            axis.set_xlabel(self._language.text("角度/°"), fontsize=8)
            axis.set_ylabel(self._language.text("灰度"), fontsize=8)
            axis.tick_params(labelsize=7)
            line, = axis.plot([], [], linewidth=1, animated=True)
            angle_line = axis.axvline(0, color="red", linestyle="--", linewidth=1, animated=True)
            gray_line = axis.axhline(0, color="red", linestyle="--", linewidth=1, animated=True)
            self.artists[title] = (line, angle_line, gray_line)

        self.figure.tight_layout(pad=0.6)
        self.canvas.mpl_connect("draw_event", self._handle_canvas_draw)
        self.canvas.draw()
        self.status = tk.StringVar(value="")
        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, sticky="ew")
        for title in self.titles:
            ttk.Button(bottom, text=f"导出{title}", command=lambda title=title: self._export(title)).pack(side="left", padx=(0, 4))
        ttk.Label(self, textvariable=self.status).grid(row=2, column=0, sticky="w")
        self.columnconfigure(0, weight=1)

    def refresh_language(self) -> None:
        for title, axis in zip(self.titles, self.axes):
            axis.set_title(self._language.text(title))
            axis.set_xlabel(self._language.text("角度/°"))
            axis.set_ylabel(self._language.text("灰度"))
        self._backgrounds.clear()  # 曲线数据、坐标范围和采样缓存不变，只重建含新文字的绘图背景。
        self.figure.tight_layout(pad=0.6)
        self.canvas.draw_idle()

    def update_data(self, profile: dict) -> None:
        needs_rescale = not self._initialized
        for title, axis in zip(self.titles, self.axes):
            x_values, y_values, angle = profile[title]
            x_values = np.asarray(x_values, dtype=float)
            y_values = np.asarray(y_values, dtype=float)
            self.data[title] = (x_values, y_values, angle)
            line, angle_line, gray_line = self.artists[title]
            line.set_data(x_values, y_values)
            angle_line.set_xdata([angle, angle])
            index = int(np.abs(x_values - angle).argmin())
            gray_line.set_ydata([y_values[index], y_values[index]])

            if not self._initialized:
                axis.set_xlim(float(np.min(x_values)), float(np.max(x_values)))
                self._set_y_limits(axis, y_values)
            else:
                lower, upper = axis.get_ylim()
                needs_rescale |= float(np.min(y_values)) < lower or float(np.max(y_values)) > upper

        if needs_rescale:
            for title, axis in zip(self.titles, self.axes):
                self._set_y_limits(axis, self.data[title][1])
            self.canvas.draw()
            self._initialized = True
        self._blit()

    def _set_y_limits(self, axis, y_values: np.ndarray) -> None:
        minimum, maximum = float(np.min(y_values)), float(np.max(y_values))
        margin = max((maximum - minimum) * 0.05, 1.0)
        axis.set_ylim(minimum - margin, maximum + margin)

    def _capture_backgrounds(self) -> None:
        self._backgrounds = [self.canvas.copy_from_bbox(axis.bbox) for axis in self.axes]

    def _handle_canvas_draw(self, _event) -> None:
        self._capture_backgrounds()
        if self._initialized:
            self.after_idle(self._blit)  # 窗口缩放导致完整重绘后，把动态曲线贴回新背景。

    def _blit(self) -> None:
        if len(self._backgrounds) != len(self.axes):
            self.canvas.draw()
        for axis, background, title in zip(self.axes, self._backgrounds, self.titles):
            self.canvas.restore_region(background)
            for artist in self.artists[title]:
                axis.draw_artist(artist)
        self.canvas.blit(self.figure.bbox)

    def _export(self, title: str) -> None:
        if title not in self.data:
            self.status.set("没有可导出的数据")
            return
        x_values, y_values, angle = self.data[title]
        path = self.export_command(title, x_values, y_values, angle)
        self.status.set(f"已导出：{path.name}")


class FlameBatchPage(PreviewActionFrame):
    def __init__(self, master, state: AppState, actions: ProcessingActions, apply_context, sync_experiment_views, preview: ImagePreviewPane) -> None:
        super().__init__(master, state, actions, apply_context, sync_experiment_views, preview)
        flame = state.settings.flame
        self.form = BoundForm(
            self,
            flame,
            [
                FormField("gain", "增益", tk.DoubleVar),
                FormField("threshold", "阈值", tk.DoubleVar),
                FormField("angle_oxidizer", "氧化剂夹角", tk.DoubleVar),
                FormField("angle_fuel", "燃料夹角", tk.DoubleVar),
                FormField("angle_momentum", "合成动量夹角", tk.DoubleVar),
                FormField("scissor_up", "上裁剪", tk.IntVar),
                FormField("scissor_down", "下裁剪", tk.IntVar),
                FormField("scissor_left", "左裁剪", tk.IntVar),
                FormField("scissor_right", "右裁剪", tk.IntVar),
            ],
        )
        self.save_marked_images = tk.BooleanVar(value=flame.save_marked_images)

        next_row = self.form.grid(self, pairs_per_row=3)
        ttk.Checkbutton(self, text="保存标记图", variable=self.save_marked_images).grid(row=next_row, column=0, sticky="w", pady=(6, 0))
        ttk.Button(self, text="完整批处理", command=self._run_batch).grid(row=next_row + 1, column=0, sticky="w", pady=(8, 0))
        ttk.Button(self, text="轻量批处理", command=self._run_lightweight).grid(row=next_row + 1, column=1, sticky="w", pady=(8, 0))
        self.add_status(next_row + 2)
        self.bind_preview_refresh([self.save_marked_images])

    def click_modes(self) -> list[tuple[str, str]]:
        return [("impact", "撞击点")]

    def preview_filename(self) -> str:
        return f"{self.state.experiment.image_name}_{self.state.experiment.frames.current}_火焰锥角预览.tif"

    def overlay_options(self) -> list[tuple[str, str] | tuple[str, str, bool]]:
        return [
            ("scissor", "裁剪框"),
            ("impact", "撞击点"),
            ("flame_angle", "火焰角"),
            ("momentum_angle", "动量角"),
        ]

    def handle_preview_click(self, x: int, y: int, mode: str) -> None:
        if mode == "impact":
            self.state.experiment.impact_x = x
            self.state.experiment.impact_y = y
            self.sync_experiment_views()  # 取点结果统一回写到顶部实验参数输入框。

    def apply_to_state(self) -> None:
        flame = self.state.settings.flame
        self.form.save()
        flame.save_marked_images = self.save_marked_images.get()

    def render_preview(self, image: np.ndarray, source: np.ndarray | None = None) -> np.ndarray:
        super().render_preview(image, source)
        self.apply_to_state()  # 渲染时使用输入框中的最新火焰参数
        experiment = self.state.experiment
        flame = self.state.settings.flame
        height, width = image.shape[:2]
        left = _clamp(flame.scissor_left, 0, width - 1)
        right = _clamp(width - flame.scissor_right - 1, 0, width - 1)  # 旧参数含义是“距右边裁掉多少”
        top = _clamp(flame.scissor_up, 0, height - 1)
        bottom = _clamp(height - flame.scissor_down - 1, 0, height - 1)
        if self.preview.overlay_enabled("scissor"):
            cv.rectangle(image, (left, top), (right, bottom), (255, 255, 0), 1)
        if self.preview.overlay_enabled("impact"):
            cv.circle(image, (experiment.impact_x, experiment.impact_y), 4, (0, 255, 0), -1)
        if self.preview.overlay_enabled("flame_angle"):
            draw_angle_line(image, experiment.impact_x, experiment.impact_y, -flame.angle_oxidizer - 90, (255, 0, 0))  # 氧化剂边界
            draw_angle_line(image, experiment.impact_x, experiment.impact_y, flame.angle_fuel - 90, (255, 0, 0))
        if self.preview.overlay_enabled("momentum_angle"):
            draw_angle_line(image, experiment.impact_x, experiment.impact_y, -flame.angle_momentum + 90, (0, 0, 255))  # 合成动量方向
        return image

    def _run_batch(self) -> None:
        self.run_progress_action("火焰锥角完整批处理", self.apply_to_state, self.actions.calculate_flame_batch)

    def _run_lightweight(self) -> None:
        self.run_progress_action("火焰锥角轻量批处理", self.apply_to_state, self.actions.calculate_flame_lightweight_batch)


class AtomizationPage(PreviewActionFrame):
    def __init__(self, master, state: AppState, actions: ProcessingActions, apply_context, sync_experiment_views, preview: ImagePreviewPane) -> None:
        super().__init__(master, state, actions, apply_context, sync_experiment_views, preview)
        atom = state.settings.atomization
        self.form = BoundForm(
            self,
            atom,
            [
                FormField("binary_threshold", "二值化阈值=", tk.IntVar, width=7),
                FormField("x_left", "左点 X", tk.IntVar),
                FormField("x_right", "右点 X", tk.IntVar),
                FormField("y", "Y", tk.IntVar),
                FormField("r_max", "Rmax=", tk.IntVar),
                FormField("theta_left", "ThetaLeft=", tk.IntVar),
                FormField("theta_right", "ThetaRight=", tk.IntVar),
                FormField("window_length", "window_length=", tk.IntVar),
                FormField("polyorder", "polyorder=", tk.IntVar),
                FormField("num_avg_left", "NumAvgL=", tk.IntVar),
                FormField("r_start_left", "RStartL=", tk.IntVar),
                FormField("num_avg_right", "NumAvgR=", tk.IntVar),
                FormField("r_start_right", "RStartR=", tk.IntVar),
                FormField("thres_ratio_left", "ThresRatioL=", tk.DoubleVar),
                FormField("thres_ratio_right", "ThresRatioR=", tk.DoubleVar),
                FormField("max_freq", "频域最大行数=", tk.IntVar),
                FormField("frame_rate_hz", "图像帧率/Hz=", tk.DoubleVar),
            ],
        )
        self.save_marked_images = tk.BooleanVar(value=atom.save_marked_images)
        self.export_dir = tk.StringVar(value=atom.export_dir)
        self.angle_left_text = tk.StringVar(value="-")
        self.angle_right_text = tk.StringVar(value="-")
        self.angle_text = tk.StringVar(value="-")
        self.profile_export_service = AtomizationPreviewExportService()
        self.profile_panel = None
        self._last_profile_key: tuple | None = None
        self._playback_active = False
        self._sampling_geometry = None
        self._sampling_geometry_key: tuple | None = None

        self._build_form()
        self.bind_preview_refresh([self.save_marked_images])

    def click_modes(self) -> list[tuple[str, str]]:
        return []

    def preview_filename(self) -> str:
        return f"{self.state.experiment.image_name}_{self.state.experiment.frames.current}_雾化锥角预览.tif"

    def overlay_options(self) -> list[tuple[str, str] | tuple[str, str, bool]]:
        return [
            ("atom_invert", "颜色反转", False),
            ("atom_binary", "二值化处理", False),
            ("atom_calc_area", "计算区域", False),
            ("atom_angle_line", "锥角线", False),
        ]

    def apply_to_state(self) -> None:
        atom = self.state.settings.atomization
        self.form.save()
        atom.export_dir = self.export_dir.get()
        atom.save_marked_images = self.save_marked_images.get()

    def render_preview(self, image: np.ndarray, source: np.ndarray | None = None) -> np.ndarray:
        super().render_preview(image, source)
        self.apply_to_state()  # 渲染时使用输入框中的最新雾化参数
        atom = self.state.settings.atomization
        if self.preview.overlay_enabled("atom_invert"):
            image = 255 - image
        if self.preview.overlay_enabled("atom_binary"):
            _, image = cv.threshold(image, atom.binary_threshold, 255, cv.THRESH_BINARY)
        if self.preview.overlay_enabled("atom_calc_area"):
            cv.ellipse(image, (atom.x_left, atom.y), (atom.r_max, atom.r_max), 0, 90, 180 - atom.theta_left * 0.1, (255, 0, 0), 1)  # theta 参数以 0.1 deg 存储
            cv.ellipse(image, (atom.x_right, atom.y), (atom.r_max, atom.r_max), 0, 180 - atom.theta_right * 0.1, 90, (255, 0, 0), 1)
        if self.preview.overlay_enabled("atom_angle_line"):
            self._draw_angle_lines(image, source)
        else:
            self._set_angle_result(None)
        return image

    def _run_batch(self) -> None:
        self.run_progress_action("雾化锥角批处理", self.apply_to_state, self.actions.run_atomization_batch)

    def _build_form(self) -> None:
        ttk.Label(self, text="图像预处理：").grid(row=0, column=0, sticky="w", pady=2)
        self._field(0, 1, "二值化阈值=", self.binary_threshold, width=7)

        ttk.Label(self, text="锥角起点：").grid(row=1, column=0, sticky="w", pady=2)
        self._field(1, 1, "左点X=", self.x_left)
        self._field(1, 2, "右点X=", self.x_right)
        self._field(1, 3, "Y=", self.y)

        ttk.Label(self, text="计算区域：").grid(row=2, column=0, sticky="w", pady=2)
        self._field(2, 1, "Rmax=", self.r_max)
        self._field(2, 2, "ThetaLeft=", self.theta_left, suffix="*0.1°")
        self._field(2, 3, "ThetaRight=", self.theta_right, suffix="*0.1°")

        ttk.Label(self, text="滤波参数：").grid(row=3, column=0, sticky="w", pady=2)
        self._field(3, 1, "window_length=", self.window_length)
        self._field(3, 2, "polyorder=", self.polyorder)

        ttk.Label(self, text="锥角提取参数：").grid(row=4, column=0, sticky="w", pady=2)
        self._field(4, 1, "NumAvgL=", self.num_avg_left)
        self._field(4, 2, "RStartL=", self.r_start_left)
        self._field(4, 3, "NumAvgR=", self.num_avg_right)
        self._field(4, 4, "RStartR=", self.r_start_right)
        self._field(4, 5, "ThresRatioL=", self.thres_ratio_left, width=7)
        self._field(4, 6, "ThresRatioR=", self.thres_ratio_right, width=7)

        ttk.Label(self, text="锥角提取结果：").grid(row=5, column=0, sticky="w", pady=2)
        self._result_field(5, 1, "左边界角=", self.angle_left_text)
        self._result_field(5, 2, "右边界角=", self.angle_right_text)
        self._result_field(5, 3, "雾化锥角=", self.angle_text)
        ttk.Button(self, text="刷新灰度曲线", command=self._refresh_profiles).grid(row=5, column=4, sticky="w", padx=(8, 0), pady=2)

        ttk.Label(self, text="保存目录").grid(row=6, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(self, textvariable=self.export_dir, width=120).grid(row=6, column=1, columnspan=5, sticky="w", padx=(4, 4), pady=(8, 0))
        ttk.Button(self, text="浏览", command=self._choose_export_dir).grid(row=6, column=6, sticky="w", pady=(8, 0))

        ttk.Label(self, text="批量处理：").grid(row=7, column=0, sticky="w", pady=(8, 0))
        batch_controls = ttk.Frame(self)
        batch_controls.grid(row=7, column=1, columnspan=6, sticky="w", pady=(8, 0))
        ttk.Label(batch_controls, text="图像帧率/Hz=").pack(side="left")
        ttk.Entry(batch_controls, textvariable=self.frame_rate_hz, width=8).pack(side="left", padx=(0, 8))
        ttk.Label(batch_controls, text="频域最大行数=").pack(side="left")
        ttk.Entry(batch_controls, textvariable=self.max_freq, width=8).pack(side="left", padx=(0, 8))
        ttk.Button(batch_controls, text="从汇总表读取参数", command=self._load_from_summary).pack(side="left")
        ttk.Button(batch_controls, text="批量处理雾化锥角", command=self._run_batch).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(batch_controls, text="运算时保存标记图片", variable=self.save_marked_images).pack(side="left", padx=(8, 0))
        self._build_profile_area(8)
        self.add_status(10)

    def _field(self, row: int, column: int, label: str, variable: tk.Variable, width: int = 8, suffix: str = "") -> None:
        frame = ttk.Frame(self)
        frame.grid(row=row, column=column, sticky="w", padx=(0, 8), pady=2)
        ttk.Label(frame, text=label).pack(side="left")
        ttk.Entry(frame, textvariable=variable, width=width).pack(side="left")
        if suffix:
            ttk.Label(frame, text=suffix).pack(side="left")

    def _result_field(self, row: int, column: int, label: str, variable: tk.StringVar) -> None:
        frame = ttk.Frame(self)
        frame.grid(row=row, column=column, sticky="w", padx=(0, 8), pady=2)
        ttk.Label(frame, text=label).pack(side="left")
        ttk.Label(frame, textvariable=variable, width=8).pack(side="left")
        ttk.Label(frame, text="°").pack(side="left")

    def _draw_angle_lines(self, image: np.ndarray, source: np.ndarray | None = None) -> None:
        profile = self._calculate_current_profiles(source=source)
        if profile is None:
            self._set_angle_result(None)
            return
        angle_left, angle_right = profile["angle_left"], profile["angle_right"]
        atom = self.state.settings.atomization
        draw_angle_line(image, atom.x_left, atom.y, angle_left, (255, 0, 0))
        draw_angle_line(image, atom.x_right, atom.y, angle_right, (255, 0, 0))
        self._set_angle_result((angle_left, angle_right))
        self._update_profile_plots(profile)

    def _set_angle_result(self, angles: tuple[float, float] | None) -> None:
        if angles is None:
            self.angle_left_text.set("-")
            self.angle_right_text.set("-")
            self.angle_text.set("-")
            return
        angle_left, angle_right = angles
        self.angle_left_text.set(f"{angle_left:.4g}")
        self.angle_right_text.set(f"{angle_right:.4g}")
        self.angle_text.set(f"{angle_right - angle_left:.4g}")

    def _load_from_summary(self) -> None:
        loaded: dict[str, object] = {}

        def read_parameters() -> None:
            loaded.update(self.actions.read_atomization_parameters_from_summary())

        self.run_action("从汇总表读取雾化参数", lambda: None, read_parameters)
        result = loaded
        if not result:
            return
        variable_map = {
            "x_left": self.x_left,
            "x_right": self.x_right,
            "y": self.y,
            "r_max": self.r_max,
            "theta_left": self.theta_left,
            "theta_right": self.theta_right,
            "window_length": self.window_length,
            "polyorder": self.polyorder,
            "num_avg_left": self.num_avg_left,
            "r_start_left": self.r_start_left,
            "num_avg_right": self.num_avg_right,
            "r_start_right": self.r_start_right,
            "thres_ratio_left": self.thres_ratio_left,
            "thres_ratio_right": self.thres_ratio_right,
        }
        for key, value in result.items():
            variable = variable_map.get(key)
            if variable is not None:
                variable.set(value)
        self.apply_to_state()
        self.preview.refresh()
        self.status.set("从汇总表读取雾化参数完成")

    def _choose_export_dir(self) -> None:
        path = filedialog.askdirectory(title="选择雾化锥角结果保存目录", initialdir=self.export_dir.get() or None)
        if path:
            self.export_dir.set(path)
            self._atomization_changed()

    def _atomization_changed(self) -> None:
        self.apply_to_state()

    def _build_profile_area(self, row: int) -> None:
        frame = ttk.LabelFrame(self, text="面积加权平均灰度值", padding=6)
        frame.grid(row=row, column=0, columnspan=7, sticky="nw", pady=(8, 0))
        self.profile_panel = AtomizationProfilePanel(frame, self._export_profile)
        self.profile_panel.grid(row=0, column=0, sticky="nsew")

    def _refresh_profiles(self) -> None:
        self.apply_to_state()
        profile = self._calculate_current_profiles(force=True)
        if profile is None:
            self.status.set("灰度曲线刷新失败")
            return
        self._set_angle_result((profile["angle_left"], profile["angle_right"]))
        self._update_profile_plots(profile)
        self.status.set("灰度曲线已刷新")

    def _calculate_current_profiles(self, force: bool = False, source: np.ndarray | None = None) -> dict | None:
        atom = self.state.settings.atomization
        key = (
            self.state.experiment.current_image_path,
            atom.x_left,
            atom.x_right,
            atom.y,
            atom.r_max,
            atom.theta_left,
            atom.theta_right,
            atom.num_avg_left,
            atom.r_start_left,
            atom.num_avg_right,
            atom.r_start_right,
            atom.thres_ratio_left,
            atom.thres_ratio_right,
            atom.window_length,
            atom.polyorder,
        )
        if not force and self._last_profile_key == key and hasattr(self, "_last_profile"):
            return self._last_profile
        try:
            if source is None:
                source = read_image(self.state.experiment.current_image_path)
            if source.ndim == 3:
                source = cv.cvtColor(source, cv.COLOR_BGR2GRAY)
            if self._playback_active:
                geometry_key = (
                    source.shape,
                    atom.x_left,
                    atom.x_right,
                    atom.y,
                    atom.r_max,
                    atom.theta_left,
                    atom.theta_right,
                    atom.num_avg_left,
                    atom.r_start_left,
                    atom.num_avg_right,
                    atom.r_start_right,
                )
                if self._sampling_geometry_key != geometry_key:
                    self._sampling_geometry = build_sampling_geometry(source.shape, *geometry_key[1:])
                    self._sampling_geometry_key = geometry_key
                res_left, res_right = self._sampling_geometry.calculate_profiles(source)
            else:
                max_value = 65535 if source.dtype == np.uint16 else 255
                res_left, res_right = calculate_grayavg_byangle((
                    max_value - source,
                    atom.x_left,
                    atom.x_right,
                    atom.y,
                    atom.r_max,
                    (899, atom.theta_left),
                    (900, atom.theta_right),
                    atom.num_avg_left,
                    atom.r_start_left,
                    atom.num_avg_right,
                    atom.r_start_right,
                ))
            res_left_sg = [res_left[0], savgol_filter(res_left[1], atom.window_length, atom.polyorder)]
            res_right_sg = [res_right[0], savgol_filter(res_right[1], atom.window_length, atom.polyorder)]
            angle_left = res_left[0][self._angle_position(res_left, res_left_sg, atom.num_avg_left, atom.thres_ratio_left)]
            angle_right = res_right[0][self._angle_position(res_right, res_right_sg, atom.num_avg_right, atom.thres_ratio_right)]
        except Exception:
            return None
        self._last_profile_key = key
        self._last_profile = {
            "左侧原始": (res_left[0], res_left[1], angle_left),
            "右侧原始": (res_right[0], res_right[1], angle_right),
            "左侧滤波": (res_left_sg[0], res_left_sg[1], angle_left),
            "右侧滤波": (res_right_sg[0], res_right_sg[1], angle_right),
            "angle_left": float(angle_left),
            "angle_right": float(angle_right),
        }
        return self._last_profile

    def handle_playback_changed(self, running: bool) -> None:
        self._playback_active = running
        if not running:
            self._sampling_geometry = None
            self._sampling_geometry_key = None

    def _angle_position(self, raw_profile, filtered_profile, num_avg: int, thres_ratio: float) -> int:
        cache_max = np.average(raw_profile[1][:num_avg])
        cache_min = np.average(raw_profile[1][-num_avg:])
        threshold = cache_min + (cache_max - cache_min) * thres_ratio
        return find_last_greater_equal(np.asarray(filtered_profile[1]), threshold)

    def _update_profile_plots(self, profile: dict) -> None:
        self.profile_panel.update_data(profile)

    def _export_profile(self, title: str, x_values, y_values, angle: float | None):
        self.apply_to_state()
        output_dir = self.export_dir.get()
        if not output_dir:
            output_dir = str(self.state.experiment.image_folder)
        return self.profile_export_service.export_profile(
            output_dir,
            self.state.experiment.image_name,
            self.state.experiment.frames.current,
            title,
            x_values,
            y_values,
            angle,
        )


def _draw_vertical(image: np.ndarray, x: int, color: tuple[int, int, int], width: int, height: int) -> None:
    if 0 <= x < width:
        cv.line(image, (x, 0), (x, height - 1), color, 1)


def _draw_horizontal(image: np.ndarray, y: int, color: tuple[int, int, int], width: int, height: int) -> None:
    if 0 <= y < height:
        cv.line(image, (0, y), (width - 1, y), color, 1)


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def _std(values: np.ndarray) -> float:
    return float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
