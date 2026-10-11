from __future__ import annotations

import tkinter as tk
from tkinter import filedialog as _files, messagebox as _messages

from AtmProcess.ui.localization import language_for


def _file_dialog(name, options):
    parent = options.get("parent") or tk._default_root
    if parent is not None:
        language = language_for(parent)
        default_title = "选择文件夹" if name == "askdirectory" else "选择文件"
        options["title"] = language.text(options.get("title", default_title))
        if "filetypes" in options:
            options["filetypes"] = [(language.text(label), *rest) for label, *rest in options["filetypes"]]
    return getattr(_files, name)(**options)  # Native dialogs retain paths, patterns and returned filenames.


def askdirectory(**options):
    return _file_dialog("askdirectory", options)


def askopenfilename(**options):
    return _file_dialog("askopenfilename", options)


def showerror(title, message, **options):
    parent = options.get("parent") or tk._default_root
    if parent is not None:
        language = language_for(parent)
        title, message = language.text(title), language.text(message)
    return _messages.showerror(title, message, **options)
