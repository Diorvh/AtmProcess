[中文使用说明](README.md)

# AtmProcess User Guide

AtmProcess is a Windows desktop application for research image processing. It supports liquid-sheet dimensions and breakup-length measurement, image averaging, color-to-grayscale conversion, flame cone angles, and atomization cone angles. The interface supports Chinese and English.

The download includes 20 images from experiment 29, extraction settings, and a demonstration summary workbook. You can adjust parameters and export results before preparing your own data. The short sample demonstrates the workflow; it is not a complete experimental dataset or a reproduction of all published results.

## 1. Download and Prerequisites

1. Download the repository ZIP and **extract the entire archive** to a writable local folder. Do not run files inside the ZIP. A folder name such as `AtmProcess-main` is supported.
2. Install a 64-bit release of Python 3.10 or later, including pip and Tcl/Tk. See the [Python downloads for Windows](https://www.python.org/downloads/windows/). The `py` launcher or `python` command must be available.
3. Dependency installation requires internet access. Automatically opening results requires a default application for `.xlsx` files. Automatically saving and closing an already-open target workbook requires desktop Microsoft Excel.

The scripts do not install Python or Excel. Not every Python and dependency combination has been tested. Dependencies are listed in [requirements.txt](requirements.txt).

## 2. Setup and Launch

**First use: double-click `setup_env.bat`.** It creates a project-local `.venv` and installs dependencies. Close the console after it reports `Setup complete`.

**Subsequent use: double-click `start.bat`.** It always uses this folder's `.venv`; manual activation is unnecessary. The console closes after a normal exit and remains open if startup fails.

Dependencies are isolated from other Python projects. Setup can be rerun after resolving an installation error and does not clear settings or experimental data. See the [Python venv documentation](https://docs.python.org/3/library/venv.html) for environment behavior.

Users with an existing suitable environment can instead run these commands in the application directory:

```powershell
python -m pip install -r requirements.txt
python main.py
```

## 3. Try the Atomization Sample

### Single-Frame Adjustment

1. On first launch, the atomization page opens with experiment 29 and frames 8000–8019.
2. The right pane shows the current image. The left pane contains parameters, angle results, and four area-weighted grayscale curves.
3. After editing a parameter, **press Enter** to commit it and recalculate. Typing alone does not schedule a delayed calculation.
4. Use `-` and `+` beside the current frame to navigate, or set a playback rate and press Play. Actual playback speed is limited by processing speed.
5. Calculation-region and angle-line overlays can be enabled independently or together. Display inversion and display binarization do not change the calculation parameters.

### Batch Processing and Summary Update

1. Keep the default 20-frame range and sampling interval of 1.
2. Click the atomization batch-processing button and wait for completion.
3. The application exports per-frame results, statistics, and frequency-domain data, then writes extraction parameters, angle means, and standard deviations to the summary record whose **experiment identifier is 29**.

Default outputs, relative to the application directory:

| Output | Location |
| --- | --- |
| Batch workbook | `sample_data/results/实验编号29_雾化锥角批处理结果.xlsx` |
| Demonstration summary | `sample_data/results/atomization_summary.xlsx` |
| Preview images | `sample_data/results/preview/` |

Each grayscale curve can also be exported to Excel using the atomization page's result directory. Preview images use the directory and filename configured in the right pane. Switching the interface language does not translate output filenames or spreadsheet fields.

### Understanding the Summary Workbook

The demonstration retains the layout of the original April 15, 2023 experimental summary: injector, pressure, flow, image-range fields, and associated formulas on the left; atomization parameters and results on the right. The breakup-length section, unrelated sheets, and other experimental records have been removed.

- Row 1 contains field names. Row 2 retains units, calibration, and correction information. Row 3 contains the only experimental record, number 29.
- Records are located by identifier and parameters by header, not by Excel row 29 or fixed column letters.
- The original condition record covers frames 21000–21520, whereas the included demonstration processes frames 8000–8019. A note distinguishes them. The batch result workbook lists the frames actually processed.
- Historical angle results are blank to avoid confusing them with statistics for the 20 sample images. Legacy `*RevStd` columns are retained but not populated by the current summary writer; relative standard deviations are available in the separate batch workbook.
- `RStartL` and `RStartR` follow their corresponding `NumAvgL` and `NumAvgR` fields.

On first launch, the bundled template is copied to the result directory. Only that writable copy is updated; the template and any existing result copy are preserved. Single-frame preview does not write to the summary on every refresh.

## 4. Process Your Own Images

1. Select a data root containing experiment subfolders such as `实验编号29` and `实验编号30`, with recognizable frame-number filenames. Direct image-source selection is also available in the interface.
2. Enter the experiment number, press Enter, and check the image source, frame range, and current frame.
3. Set the sampling interval. Starting at 202 with an interval of 2 selects 202, 204, 206, and so on. Navigation and batch tasks use the same selected set.
4. Select the processing page, configure calibration and extraction parameters, and inspect a single frame before processing a batch.
5. Select dedicated output directories and a summary workbook for your experiment. Do not use the demonstration summary as your research summary.

Use the demonstration layout as a reference for your own workbook: recognized field names in the first row and unique experiment identifiers in the data rows. The parameter-reading button restores atomization parameters for the current experiment from the selected summary. Leaving the summary path empty still allows calculations and independent result exports, but disables summary updates and parameter readback.

Frequency analysis uses the image sampling rate entered on the page. Enter the **effective sampling frequency of the processed sequence**. If frames were subsampled, account for that yourself; the application does not divide this value by the sampling interval again.

## 5. Other Pages

| Page | Use |
| --- | --- |
| Liquid-sheet measurement | Choose dimensions or breakup-length mode, select boundaries in the preview, inspect live measurements, record frames, export Excel data, or reload previously exported records. |
| Average image | Average the selected frames or convert color images to grayscale. |
| Flame cone angle | Inspect a frame, adjust parameters, and extract angles in a batch. |
| Atomization cone angle | Adjust parameters, inspect grayscale curves, process batches, and read/write the summary. |

Changing the experiment or image source clears the current liquid-sheet measurement records. Export them first if needed. Averaging and conversion operations may create or overwrite output images; retain original-image backups before processing your own data.

## 6. Settings and Troubleshooting

- **Will every launch reset to the sample?** No. Closing the application saves `settings.json`; subsequent launches restore the previous page, paths, parameters, and preview options.
- **How do I repeat the first-run experience?** Extract a fresh copy. Alternatively, close the application and back up and move away `settings.json`. Existing result workbooks are not erased.
- **Setup failed.** Keep the error message, check network access, Python availability, and folder permissions, then rerun setup. Avoid protected directories requiring administrator access.
- **Start asks for setup.** Run `setup_env.bat`. Installing packages in a system Python environment does not configure this folder's `.venv`.
- **The folder was moved.** Code and settings can be moved, but virtual environments should be recreated at the destination. Close the application, move aside the old `.venv`, and rerun setup; retain settings and results.
- **A workbook is locked.** Only Excel workbooks matching the full target path are saved and closed. Other workbooks are not intentionally modified or closed. If WPS or another application holds the file, save and close that target manually before retrying.
- **A saved workbook cannot open automatically.** Configure a default `.xlsx` application. An opening error can interrupt the subsequent summary update; check the summary and rerun after fixing the association.
- **Does the sample contain all paper data?** No. See the [sample description and provenance](sample_data/README.md) for source, bit depth, and checksums.

## Detailed Documentation

- [中文详细文档：架构、计算与导出流程](docs/ARCHITECTURE_CN.md)
- [English documentation: architecture, computation and export](docs/ARCHITECTURE_EN.md)
