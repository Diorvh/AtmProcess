from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

import cv2 as cv
import numpy as np
from PIL import Image, ImageTk

from ImageProcessv3.application.app_state import AppState
from ImageProcessv3.core.image_io import read_image, write_tiff
from ImageProcessv3.ui.widgets import short_path


PreviewRenderer = Callable[[np.ndarray, np.ndarray], np.ndarray]  # 页面接收显示图和原始图，避免算法再次读取文件。
ClickHandler = Callable[[int, int, str], None]  # 页面负责解释一次鼠标点击的含义
FilenameProvider = Callable[[], str]
OverlayOption = tuple[str, str] | tuple[str, str, bool]  # key、显示名、可选默认勾选状态


class ImagePreviewPane(ttk.LabelFrame):
    def __init__(self, master, state: AppState) -> None:
        super().__init__(master, text="图像预览", padding=8)
        self.state = state
        self.renderer: PreviewRenderer | None = None  # 当前页面注册的绘图函数
        self.click_handler: ClickHandler | None = None  # 当前页面注册的取点函数
        self.filename_provider: FilenameProvider | None = None
        self.click_mode = tk.StringVar(value="")  # 取点模式是单选，没有模式时点击只显示坐标
        self.path_text = tk.StringVar(value="")
        self.coord_text = tk.StringVar(value="")
        self.status_text = tk.StringVar(value="就绪")
        self.save_dir = tk.StringVar(value=state.settings.preview.save_dir)
        self.filename = tk.StringVar(value=state.settings.preview.filename)
        self._overlay_vars: dict[str, tk.BooleanVar] = {}  # 当前页面可见的显示图层
        self._overlay_values: dict[str, bool] = dict(state.settings.preview.overlay_values)  # 跨页面、跨启动保留用户勾选状态
        self._photo = None
        self._display_origin = (0, 0)  # 图像在 canvas 中的左上角
        self._display_scale = 1.0  # canvas 坐标到原图像素坐标的缩放比例
        self._image_size = (0, 0)
        self._source_image: np.ndarray | None = None  # 用原始图像读灰度，避免叠加线条影响数值
        self._display_image: np.ndarray | None = None
        self._refresh_job = None  # after 任务句柄，用于合并频繁刷新

        self.toolbar = ttk.Frame(self)
        self.toolbar.grid(row=0, column=0, sticky="w")
        ttk.Button(self.toolbar, text="刷新图像", command=self.refresh).pack(side="left")
        ttk.Label(self.toolbar, text="取点：").pack(side="left", padx=(10, 0))
        self.mode_frame = ttk.Frame(self.toolbar)
        self.mode_frame.pack(side="left")

        self.overlay_bar = ttk.Frame(self)
        self.overlay_bar.grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(self.overlay_bar, text="显示：").pack(side="left")
        self.overlay_frame = ttk.Frame(self.overlay_bar)
        self.overlay_frame.pack(side="left")

        self.save_bar = ttk.Frame(self)
        self.save_bar.grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(self.save_bar, text="保存目录").pack(side="left")
        ttk.Entry(self.save_bar, textvariable=self.save_dir, width=120).pack(side="left", padx=(4, 4))
        ttk.Button(self.save_bar, text="浏览", command=self._choose_save_dir).pack(side="left")

        self.filename_bar = ttk.Frame(self)
        self.filename_bar.grid(row=3, column=0, sticky="w", pady=(4, 0))
        ttk.Label(self.filename_bar, text="文件名").pack(side="left")
        ttk.Entry(self.filename_bar, textvariable=self.filename, width=42).pack(side="left", padx=(4, 4))
        ttk.Button(self.filename_bar, text="生成文件名", command=self.generate_filename).pack(side="left")
        ttk.Button(self.filename_bar, text="保存预览图", command=self.save_preview_image).pack(side="left", padx=(6, 0))

        ttk.Label(self, textvariable=self.path_text).grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.canvas = tk.Canvas(self, width=760, height=620, background="#222222", highlightthickness=0)
        self.canvas.grid(row=5, column=0, sticky="nsew", pady=(6, 0))
        self.canvas.bind("<Button-1>", self._handle_click)
        self.canvas.bind("<Motion>", self._handle_motion)
        ttk.Label(self, textvariable=self.coord_text).grid(row=6, column=0, sticky="w", pady=(6, 0))
        ttk.Label(self, textvariable=self.status_text).grid(row=7, column=0, sticky="w", pady=(4, 0))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)
        self.save_dir.trace_add("write", lambda *_: self._save_settings())
        self.filename.trace_add("write", lambda *_: self._save_settings())
        self.set_click_modes([])
        self.set_overlay_options([])

    def set_renderer(self, renderer: PreviewRenderer | None) -> None:
        self.renderer = renderer

    def set_click_handler(self, handler: ClickHandler | None) -> None:
        self.click_handler = handler

    def set_filename_provider(self, provider: FilenameProvider | None) -> None:
        self.filename_provider = provider
        self.generate_filename()

    def set_click_modes(self, modes: list[tuple[str, str]]) -> None:
        for child in self.mode_frame.winfo_children():
            child.destroy()
        if not modes:
            self.click_mode.set("")
            ttk.Label(self.mode_frame, text="无").pack(side="left")
            return
        values = {value for value, _ in modes}
        if self.click_mode.get() not in values:
            self.click_mode.set(modes[0][0])
        for value, label in modes:
            ttk.Radiobutton(self.mode_frame, text=label, value=value, variable=self.click_mode).pack(side="left")

    def set_overlay_options(self, options: list[OverlayOption]) -> None:
        for child in self.overlay_frame.winfo_children():
            child.destroy()
        self._overlay_vars = {}  # 切换页面时只重建当前页面需要的 checkbox
        for option in options:
            key, label = option[:2]
            default_checked = bool(option[2]) if len(option) == 3 else True
            checked = self._overlay_values.get(key, default_checked)  # 优先恢复用户上次选择
            variable = tk.BooleanVar(value=checked)
            variable.trace_add("write", lambda *_args, key=key, variable=variable: self._overlay_changed(key, variable))
            self._overlay_vars[key] = variable
            ttk.Checkbutton(self.overlay_frame, text=label, variable=variable).pack(side="left")
        if not options:
            ttk.Label(self.overlay_frame, text="原图").pack(side="left")

    def _overlay_changed(self, key: str, variable: tk.BooleanVar) -> None:
        self._overlay_values[key] = variable.get()
        self.state.settings.preview.overlay_values = dict(self._overlay_values)
        self.refresh()

    def overlay_enabled(self, key: str) -> bool:
        variable = self._overlay_vars.get(key)
        return bool(variable.get()) if variable is not None else False

    def schedule_refresh(self, delay_ms: int = 180) -> None:
        if self._refresh_job is not None:
            self.after_cancel(self._refresh_job)  # 参数连续输入时只保留最后一次刷新
        self._refresh_job = self.after(delay_ms, self.refresh)

    def refresh(self) -> None:
        if self._refresh_job is not None:
            try:
                self.after_cancel(self._refresh_job)
            except tk.TclError:
                pass
        self._refresh_job = None
        try:
            path = self.state.experiment.current_image_path
            image = read_image(path)
            self._source_image = image
            display = to_rgb8(image)
            if self.renderer is not None:
                display = self.renderer(display.copy(), image)  # renderer 可以在显示副本上画线，并用原始位深图计算。
            self.show_array(display, path)
            self.status_text.set("预览已刷新")
        except Exception as exc:
            self.status_text.set(f"预览失败：{exc}")

    def show_array(self, image: np.ndarray, path: str | Path | None = None, source: np.ndarray | None = None) -> None:
        if source is not None:
            self._source_image = source
        if image.dtype != np.uint8 or image.ndim == 2:
            image = to_rgb8(image)  # 外部直接显示灰度图或 16 bit 图时统一转 RGB8
        self._image_size = (image.shape[1], image.shape[0])
        self._display_image = image.copy()
        self._draw_image(Image.fromarray(image))
        if path is not None:
            self.path_text.set(short_path(path))

    def generate_filename(self) -> None:
        if self.filename_provider is not None:
            self.filename.set(self.filename_provider())

    def _choose_save_dir(self) -> None:
        path = filedialog.askdirectory(title="选择预览图保存目录", initialdir=self.save_dir.get() or None)
        if path:
            self.save_dir.set(path)

    def save_preview_image(self) -> None:
        if self._display_image is None:
            self.status_text.set("没有可保存的预览图")
            return
        save_dir = self.save_dir.get()
        filename = self.filename.get()
        if not save_dir:
            self.status_text.set("请先选择预览图保存目录")
            return
        if not filename:
            self.generate_filename()
            filename = self.filename.get()
        path = Path(save_dir) / filename
        write_tiff(path, cv.cvtColor(self._display_image, cv.COLOR_RGB2BGR))
        self.status_text.set(f"预览图已保存：{short_path(path)}")

    def _save_settings(self) -> None:
        self.state.settings.preview.save_dir = self.save_dir.get()
        self.state.settings.preview.filename = self.filename.get()
        self.state.settings.preview.overlay_values = dict(self._overlay_values)

    def _draw_image(self, image: Image.Image) -> None:
        canvas_width = max(self.canvas.winfo_width(), 760)
        canvas_height = max(self.canvas.winfo_height(), 620)
        scale = min(canvas_width / image.width, canvas_height / image.height, 1.0)
        display_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))  # 只缩小不放大
        image = image.resize(display_size, Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(image)  # Tk 需要持有引用，否则图像会被回收
        x0 = (canvas_width - display_size[0]) // 2
        y0 = 0  # 图像上边贴住预览框顶部，下方空白可用于点击图像外破碎位置
        self._display_origin = (x0, y0)
        self._display_scale = scale
        self.canvas.delete("all")
        self.canvas.create_image(x0, y0, anchor="nw", image=self._photo)

    def _handle_click(self, event) -> None:
        self.focus_for_shortcuts()
        point = self._event_to_image_point(event)
        if point is None:
            return
        x, y = point
        mode = self.click_mode.get()
        mode_text = f"，模式：{mode}" if mode else ""
        self.coord_text.set(f"{self._format_pixel_info(x, y)}{mode_text}")
        if self.click_handler is not None and mode:
            self.click_handler(x, y, mode)
            self.refresh()

    def focus_for_shortcuts(self) -> None:
        self.canvas.focus_set()  # 焦点离开 Entry 后，小键盘按键由页面快捷键处理。

    def _handle_motion(self, event) -> None:
        point = self._event_to_image_point(event)
        if point is None:
            return
        x, y = point
        self.coord_text.set(self._format_pixel_info(x, y))

    def _event_to_image_point(self, event) -> tuple[int, int] | None:
        if self._image_size == (0, 0) or self._display_scale <= 0:
            return None
        x0, y0 = self._display_origin
        x = int(round((event.x - x0) / self._display_scale))
        y = int(round((event.y - y0) / self._display_scale))  # 鼠标坐标还原到原图像素坐标
        return x, y  # 允许图像外坐标，破碎位置超出画幅时仍可记录

    def _format_pixel_info(self, x: int, y: int) -> str:
        value = self._gray_value_at(x, y)
        return f"坐标：x={x}, y={y}，灰度：{value}"

    def _gray_value_at(self, x: int, y: int) -> str:
        if self._source_image is None:
            return "-"
        if x < 0 or y < 0 or y >= self._source_image.shape[0] or x >= self._source_image.shape[1]:
            return "图像外"
        pixel = self._source_image[y, x]
        if np.isscalar(pixel):
            return str(int(pixel))
        values = np.asarray(pixel, dtype=float)
        if values.size < 3:
            return str(int(values[0]))
        gray = int(round(0.114 * values[0] + 0.587 * values[1] + 0.299 * values[2]))  # OpenCV 彩色图按 BGR 转灰度
        return str(gray)


def to_rgb8(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint16:
        image = np.array(np.round(image / 256), dtype=np.uint8)  # TIFF 常见 16 bit，预览压到 8 bit
    else:
        image = np.array(image, dtype=np.uint8)
    if image.ndim == 2:
        return cv.cvtColor(image, cv.COLOR_GRAY2RGB)
    if image.shape[2] == 3:
        return cv.cvtColor(image, cv.COLOR_BGR2RGB)  # OpenCV 读入通常是 BGR，Tk/PIL 显示需要 RGB
    return image


def draw_angle_line(image: np.ndarray, x: int, y: int, angle: float, color: tuple[int, int, int], length: int = 1200) -> None:
    x2 = int(x - length * np.cos(angle / 180 * np.pi))
    y2 = int(y + length * np.sin(angle / 180 * np.pi))
    cv.line(image, (x, y), (x2, y2), color, 1)
