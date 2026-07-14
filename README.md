# ImageProcess v2

This folder is intended to run independently from the legacy ImageProcess GUI.

## Run

From the parent folder:

```powershell
python -m ImageProcessv2.main
```

Or run the script directly:

```powershell
python ImageProcessv2\main.py
```

Install dependencies if needed:

```powershell
python -m pip install -r ImageProcessv2\requirements.txt
```

## Structure

- `domain/`: plain data models and settings.
- `application/`: app state and GUI actions.
- `ui/`: Tkinter windows and pages.
- `ui/preview/`: shared right-side image preview pane used by each processing page.
- `core/`: image IO, Excel IO, settings, path helpers, C++ runner.
- `algorithms/`: calculation entry points.
- `services/`: workflow services used by the GUI.
- `lib/`: numerical helper functions required by the algorithms.
- `PlayAtmAngleCPP/`: C++ atomization-angle runtime used by v2.
- `sample_data/atomization/实验编号55/`: small atomization-angle TIFF sample copied from a real experiment for smoke tests.
- `docs/ARCHITECTURE_CN.md`: detailed Chinese architecture guide.
- `docs/GUI_REFACTOR_GUIDE_CN.md`: reusable guide for refactoring similar research GUI programs.
