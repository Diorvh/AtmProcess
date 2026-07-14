from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ImageProcessv2.application.actions import ImageProcessActions
from ImageProcessv2.application.app_state import AppState
from ImageProcessv2.ui.experiment_panel import ExperimentPanel
from ImageProcessv2.ui.pages.processing_pages import ProcessingPages
from ImageProcessv2.ui.preview import ImagePreviewPane


class AppWindow(ttk.Frame):
    def __init__(self, master: tk.Tk, state: AppState) -> None:
        super().__init__(master, padding=8)
        self.state = state
        self.actions = ImageProcessActions(state)
        self.grid(sticky="nsew")  # AppWindow 自己填满 Tk 根窗口
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.experiment_panel = ExperimentPanel(self, state)
        self.experiment_panel.grid(row=0, column=0, sticky="nw")

        self.content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)  # 左侧参数页，右侧共享预览
        self.content.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.preview = ImagePreviewPane(self.content, state)
        self.pages = ProcessingPages(
            self.content,
            state,
            self.actions,
            self.experiment_panel.apply_to_state,
            self.experiment_panel.refresh_from_state,
            self.preview,
        )
        self.content.add(self.pages, weight=1)
        self.content.add(self.preview, weight=3)  # 预览区域更宽，方便调参时看图
        self.experiment_panel.bind_change(self.preview.refresh)  # 明确提交或按钮操作后立即刷新，不再对输入过程做延迟刷新
        master.bind_all("<Return>", self._commit_entry, add="+")  # Entry 中按回车立即提交并刷新当前预览
        master.bind_all("<Key>", self._handle_page_shortcut, add="+")

    def save(self) -> None:
        self.experiment_panel.apply_to_state()
        self.state.save()

    def _commit_entry(self, event) -> None:
        if event.widget.winfo_class() not in {"Entry", "TEntry"}:
            return
        self.after_idle(lambda widget=event.widget: self._commit_entry_now(widget))

    def _commit_entry_now(self, widget) -> None:
        self.experiment_panel.commit_entry(widget)

    def _handle_page_shortcut(self, event) -> None:
        if event.widget.winfo_class() in {"Entry", "TEntry"}:
            return
        if self.pages.handle_shortcut(event):
            self.preview.refresh()
