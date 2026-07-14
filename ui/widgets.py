from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable


def labeled_entry(parent, row: int, column: int, label: str, variable: tk.Variable, width: int = 10) -> ttk.Entry:
    ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=(0, 4), pady=2)
    entry = ttk.Entry(parent, textvariable=variable, width=width)
    entry.grid(row=row, column=column + 1, sticky="w", padx=(0, 8), pady=2)
    return entry


def short_path(path: str | Path, max_length: int = 68) -> str:
    text = str(path)
    if len(text) <= max_length:
        return text
    return "..." + text[-(max_length - 3):]


@dataclass(frozen=True)
class FormField:
    name: str
    label: str
    variable_type: type[tk.Variable]
    width: int = 10


class BoundForm:
    def __init__(self, owner, model, fields: list[FormField]) -> None:
        self.owner = owner
        self.model = model
        self.fields = fields
        for field in fields:
            setattr(owner, field.name, field.variable_type(value=getattr(model, field.name)))

    def grid(self, parent, start_row: int = 0, pairs_per_row: int = 2) -> int:
        for index, field in enumerate(self.fields):
            row = start_row + index // pairs_per_row
            column = (index % pairs_per_row) * 2
            labeled_entry(parent, row, column, field.label, getattr(self.owner, field.name), field.width)
        return start_row + (len(self.fields) + pairs_per_row - 1) // pairs_per_row

    def load(self) -> None:
        for field in self.fields:
            getattr(self.owner, field.name).set(getattr(self.model, field.name))

    def save(self) -> None:
        for field in self.fields:
            setattr(self.model, field.name, getattr(self.owner, field.name).get())

    def variables(self) -> list[tk.Variable]:
        return [getattr(self.owner, field.name) for field in self.fields]


class ActionFrame(ttk.Frame):
    def __init__(self, master, apply_context: Callable[[], None]) -> None:
        super().__init__(master, padding=10)
        self.apply_context = apply_context
        self.status = tk.StringVar(value="就绪")

    def add_status(self, row: int, columnspan: int = 8) -> None:
        ttk.Label(self, textvariable=self.status).grid(row=row, column=0, columnspan=columnspan, sticky="w", pady=(8, 0))

    def run_action(self, title: str, apply_page: Callable[[], None], action: Callable[[], object]) -> object | None:
        try:
            self.apply_context()
            apply_page()
            self.status.set(f"{title} 正在执行...")
            self.update_idletasks()
            result = action()
            self.status.set(f"{title} 完成：{result}" if result is not None else f"{title} 完成")
            return result
        except Exception as exc:
            self.status.set(f"{title} 失败：{exc}")
            messagebox.showerror(title, str(exc))
            return None
