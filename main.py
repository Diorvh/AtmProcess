from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ImageProcessv3.application.app_state import AppState
from ImageProcessv3.ui.app_window import AppWindow


def main() -> None:
    root = tk.Tk()
    root.title("ImageProcess v3")
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
