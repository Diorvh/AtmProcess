from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from AtmProcess.application.actions import ProcessingActions
from AtmProcess.application.app_state import AppState
from AtmProcess.ui.experiment_panel import ExperimentPanel
from AtmProcess.ui.pages.processing_pages import ProcessingPages
from AtmProcess.ui.preview import ImagePreviewPane


class AppWindow(ttk.Frame):
    def __init__(self, master: tk.Tk, state: AppState) -> None:
        super().__init__(master, padding=8)
        self.state = state
        self.actions = ProcessingActions(state)
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
            self._sync_experiment_views_from_state,
            self.preview,
        )
        self.content.add(self.pages, weight=1)
        self.content.add(self.preview, weight=3)  # 预览区域更宽，方便调参时看图
        self.experiment_panel.bind_change(self._handle_experiment_panel_changed)
        self.experiment_panel.bind_playback(self.pages.handle_playback_changed)
        master.bind_all("<Return>", self._commit_entry, add="+")  # Entry 中按回车立即提交并刷新当前预览
        master.bind_all("<Key>", self._handle_page_shortcut, add="+")

    def _sync_experiment_views_from_state(self) -> None:
        self.experiment_panel.refresh_from_state()  # 功能页改状态后，顶部输入框和帧信息统一回写。
        self.pages.handle_experiment_context_changed()

    def _handle_experiment_panel_changed(self) -> None:
        self.pages.handle_experiment_context_changed()
        self.preview.refresh()  # 顶部面板提交后立即更新当前页预览，不对普通输入过程做延迟刷新。

    def save(self) -> None:
        self.experiment_panel.stop_playback()
        self.experiment_panel.apply_to_state()
        self.state.save()

    def _commit_entry(self, event) -> None:
        if event.widget.winfo_class() not in {"Entry", "TEntry"}:
            return
        self.after_idle(lambda widget=event.widget: self._commit_entry_now(widget))

    def _commit_entry_now(self, widget) -> None:
        self.experiment_panel.commit_entry(widget)
        self.preview.focus_for_shortcuts()  # 回车提交后无需再点击图像即可使用小键盘快捷键。

    def _handle_page_shortcut(self, event) -> str | None:
        if event.widget.winfo_class() in {"Entry", "TEntry"}:
            return None
        if self.pages.handle_shortcut(event):
            self.preview.refresh()
        return None
