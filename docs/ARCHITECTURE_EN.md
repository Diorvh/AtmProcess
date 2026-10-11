# AtmProcess Architecture

[中文详细文档](ARCHITECTURE_CN.md) · [User guide](../README_EN.md)

## 1. Purpose

AtmProcess is a desktop application for research image processing. It provides liquid-sheet width, length and breakup-length measurement; image averaging and grayscale conversion; flame and atomization cone-angle extraction; preview-image and grayscale-curve export; and experiment-summary parameter readback and result updates.

The design prioritizes readable, maintainable code for trained researchers. Validation is limited to basic checks that prevent clearly invalid application states. GUI code, algorithms and utilities reside in this directory. Atomization calculations use Python and do not require a separate executable or communication files.

## 2. Entry Points

On Windows, `setup_env.bat` creates a project-local `.venv` and installs `requirements.txt` using an existing 64-bit Python 3.10 or newer installation. It does not install system Python or change global dependencies. `start.bat` launches the application using that local environment and retains console errors on failure.

With dependencies already available, run from the application directory:

```powershell
python main.py
```

If the directory is named exactly `AtmProcess`, the parent directory also supports:

```powershell
python -m AtmProcess.main
```

For direct execution, `main.py` registers the local package so that extracted names such as `AtmProcess-main` work. It creates the Tk root, loads state, constructs the main window, and saves configuration on close.

## 3. Layers and Dependencies

```text
AtmProcess/
  main.py
  setup_env.bat
  start.bat
  settings.example.json
  settings.json                 # Generated local configuration
  requirements.txt
  domain/                      # Context and parameter models
  application/                 # State, actions and frame catalog
  ui/                          # Pages, controls and shared preview
  services/                    # Processing and export workflows
  algorithms/                  # Array-oriented calculations
  core/                        # I/O, configuration and parallel support
  lib/                         # Numerical helpers
  sample_data/                 # Images and summary template
  tests/
```

```text
UI -> Application -> Services -> Algorithms / Core / Lib
                  -> Domain
```

Lower layers do not traverse GUI widgets. Algorithms, exports and state management can therefore be exercised without constructing the full interface.

## 4. Responsibilities

### Domain

`domain/context.py` defines image-source paths, experiment identifiers, frame selection, impingement point and pixel calibration. `domain/settings.py` defines `FlameSettings`, `AtomizationSettings`, `MeasurementSettings`, `PreviewSettings`, and the aggregate `AppSettings` with JSON conversion.

These models store data. They do not access Tkinter, read images, or write Excel files.

### Application

`application/app_state.py` owns the current `AppSettings`, configuration loading and saving, first-run summary preparation, and frame-range rescanning. `application/frame_catalog.py` manages available frames.

`application/actions.py` exposes operations such as `save_average_image()`, `export_breakup_records()`, `calculate_flame_batch()`, and `run_atomization_batch()`. Actions assemble parameters and invoke services; they do not implement the mathematical algorithms.

### UI

`ui/app_window.py` places experiment controls at the top, processing pages on the left, and a shared preview on the right. `ui/pages/processing_pages.py` manages each page's inputs, commands, status text and overlay behavior. `ui/preview/image_preview_pane.py` owns image display, scaling, cursor coordinates and intensity, point selection, overlays and preview-image saving.

Ordinary text input does not schedule delayed recalculation. Enter commits values to state and refreshes the current page. State changes made by page actions also update the shared experiment controls.

Liquid-sheet records belong to the current experimental context. Changing the experiment, data root or direct image source clears both measurement modes and their statistics to prevent mixing conditions. Exported records can be loaded again explicitly.

The local language catalog changes interface presentation. It does not translate user-entered paths, identifiers, persisted field names or scientific data, and language switching does not require a new calculation.

### Services

Services organize complete operations: batch calculations, statistics, workbook generation, summary updates and output paths.

`measurement_export_service.py` exports and reloads liquid-sheet and breakup-length records. Readback skips the parameter and header area, restores per-frame values, selects the measurement mode from the workbook headers, and lets the page recompute means and standard deviations.

Atomization responsibilities are split among:

- `atomization_angle_service.py`: selected frames, worker configuration, calculation and timing.
- `atomization_result_export_service.py`: parameter and result tables, statistics, frequency data, charts and summary updates.
- `atomization_preview_export_service.py`: single-frame grayscale-curve export.
- `summary_workbook_service.py`: workbook-header and experiment-identifier lookup, parameter readback and result writes.

### Algorithms

Algorithms accept arrays and numerical parameters, without knowledge of widgets or workbook layouts. `algorithms/atomization.py` defines `AtomizationParameters`, `calculate_atomization_batch()`, per-worker processing and optional marked-image output.

### Core and Numerical Helpers

`core/` provides image I/O, configuration persistence, Excel matrix writing, path handling, progress counters and task splitting. `lib/` contains interpolation, filtering and frequency-analysis helpers. The area-weighted angular grayscale calculation is implemented with NumPy in `lib_AtmAngle.py`.

`core/excel_workbook_coordinator.py` coordinates workbook writes. It matches open Excel workbooks by full path and attempts to save and close only the target before writing. It reopens the written file without quitting Excel or intentionally modifying other open workbooks. WPS and other applications cannot be controlled through this Excel COM path; their target-file locks require manual intervention.

## 5. Atomization Processing

### Single-Frame Preview

```text
Edit parameters and press Enter
  -> Commit entries to AtomizationSettings
  -> Refresh the current image
  -> Compute left/right area-weighted grayscale curves
  -> Apply Savitzky-Golay filtering
  -> Extract boundary angles from threshold ratios
  -> Update overlays, numerical results and four curves
```

The page keeps a complete-result cache keyed by image path and calculation parameters. An unchanged key reuses the previous result; changing an input recalculates it.

Playback advances through `FrameSelection`, respecting the range and sampling interval, and stops at the last selected frame. A Tk `after()` timer schedules updates; no background thread manipulates widgets.

### Vectorized Sampling and Playback Cache

Angles and radii form two-dimensional coordinate arrays. NumPy processes sampling coordinates, valid-area masks, bilinear interpolation and area-weighted sums in blocks.

Ordinary parameter adjustment uses block vectorization. Playback creates a temporary `AtomizationSamplingGeometry` containing pixel indices, interpolation weights and area weights. Later frames reuse the geometry; pausing releases the playback cache. Mathematical definitions, angular resolution and interpolation remain unchanged.

The four curves share one Matplotlib figure with four axes. Curves and angle markers are created once, then updated through `set_data()` and blitting. A full draw occurs when needed, such as when values exceed the current vertical limits, instead of clearing axes and repeating layout on every frame.

### Batch Processing

```text
Batch command
  -> ProcessingActions.run_atomization_batch()
  -> AtomizationAngleService.run_batch()
  -> Generate the selected start/end/interval frame list
  -> Split frames among workers
  -> Build sampling geometry once per worker chunk
  -> Calculate each frame with the shared numerical method
  -> Merge [Frame, AngleL, AngleR, AtmAngle]
  -> Export the batch workbook and update the summary
```

Playback and batch workers use the same sampling-geometry implementation. Workers do not share NumPy cache objects; each builds its own geometry and rebuilds it if image dimensions change.

Average-image, grayscale, flame and atomization workflows receive the same selected frame list. Navigation buttons and measurement shortcuts also move through that set.

Worker startup has a fixed cost on Windows. The service's current heuristic recommends 1, 2, 4 and 6 processes for up to 250, 750, 2000 and 5000 images, and 8 processes above that, bounded by the configured process limit. This is an empirical rule, not a universal optimum. Exported `compute_time` includes worker startup, image reading and calculation, but excludes subsequent Excel export.

### Progress

The batch workflows use `core/progress.py`. Workers increment a shared counter after completing each frame; the main process samples it approximately every 100 ms and updates completed count, percentage and a determinate progress bar. Completion reports 100%.

Batch processing remains blocking. Only necessary GUI redraws occur while the task runs; there is no additional background-task lifecycle or cancellation framework.

## 6. Workbooks and Statistics

The standalone atomization workbook uses:

| Row or region | Content |
| --- | --- |
| 1 | Parameter headers |
| 2 | Parameter values, process count and computation time |
| 3 | `Frame`, `AngleL`, `AngleR`, `AtmAngle`, `AngleM` |
| 4 | Arithmetic means |
| 5 | Sample standard deviations; zero for a single frame |
| 6 | Relative standard deviations, normalized by mean atomization angle |
| 7 onward | Per-frame values |
| Right-hand region | Frequency data and time/frequency charts |

`AngleM` is the arithmetic mean of the left and right boundary angles for each frame. Frequency analysis uses the explicitly entered sampling frequency; it is not automatically adjusted again for subsampling.

`SummaryWorkbookService` locates columns by first-row headers and records by their experiment identifiers. If a writable record does not exist, it appends one. The identifier is not an Excel row number. Atomization parameter lookup starts at `XLeft`, avoiding unrelated duplicate headers such as another region's `Y`.

The bundled summary retains only experiment 29 from the April 15, 2023 source workbook. It preserves the header row, units/calibration/correction row, experimental conditions and their formulas, but removes the breakup-length area and other experiments. `RStartL` and `RStartR` follow their corresponding radial-averaging fields. Old angle results, process count and time are blank before the demonstration runs. Legacy relative-deviation columns remain in the template but are not populated by the current summary writer; the standalone workbook contains those statistics.

All output writes use the workbook coordinator. A locked file is not silently redirected to a timestamped name. An error opening a just-saved workbook can interrupt later summary operations; a default `.xlsx` application is therefore part of the desktop workflow.

## 7. Configuration and First Run

`settings.json` resides beside the program. Closing saves paths, experiment identifier, frame selection, page parameters, measurement state, active page, preview overlays, output directories and preview filename. It is local state and is excluded from Git, as are environments, caches and generated sample results.

When no local configuration exists, `SettingsStore` loads `settings.example.json`. `AppState` copies `sample_data/atomization_summary_template.xlsx` to the configured result path only if that target does not exist. Existing personal settings and result copies are preserved.

The default page is atomization, using experiment 29 and frames 8000–8019. The summary's left-hand source-condition range is 21000–21520, explicitly distinguished from this demonstration selection. Actual processed frame numbers are exported in the standalone batch workbook.

Relative paths are resolved against the configuration directory and saved as relative paths where possible. Source code and sample files are relocatable; `.venv` should be recreated at the destination rather than distributed as a portable runtime.

## 8. Where to Make Changes

| Change | Owning layer |
| --- | --- |
| Layout, labels or preview controls | `ui/` |
| Command orchestration | `application/actions.py` |
| Batch organization | Relevant service |
| Mathematical definitions | `algorithms/` or `lib/` |
| Workbook layouts and summary behavior | Export services and summary service |
| Persisted parameters | Domain settings, then UI bindings |

Keep algorithms independent of Tkinter variables and keep workbook manipulation out of page widgets. This boundary maintains readability as features evolve.
