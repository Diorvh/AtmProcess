from __future__ import annotations

import importlib.util
import sys
import tkinter as tk
from pathlib import Path

if __package__ in (None, "") and "AtmProcess" not in sys.modules:
    package_root = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "AtmProcess", package_root / "__init__.py", submodule_search_locations=[str(package_root)],
    )
    package = importlib.util.module_from_spec(spec)
    sys.modules["AtmProcess"] = package  # GitHub ZIP 的解压目录可带有 -main 等后缀。
    spec.loader.exec_module(package)

from AtmProcess.application.app_state import AppState
from AtmProcess.ui.app_window import AppWindow


def main() -> None:
    root = tk.Tk()
    root.title("AtmProcess")
    root.state("zoomed")
    state = AppState()
    app = AppWindow(root, state)

    def close_window() -> None:
        app.save()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)
    root.mainloop()


if __name__ == "__main__":
    main()
