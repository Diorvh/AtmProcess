# ImageProcess

Tkinter desktop tools for impinging-jet image processing.

Current tools:

- sheet size measurement
- breakup length measurement
- flame angle measurement and batch processing
- average image generation and image preprocessing
- atomization angle preview and C++ accelerated batch processing

The induction length tool has been removed.

## Run

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python main.py
```

## Architecture

The code is being refactored toward four layers:

- `ui` / existing Tkinter page classes: user input and display
- `services`: workflow orchestration for each tool
- `algorithms`: calculation entry points
- `core`: shared configuration, paths, image IO, Excel IO, and C++ runners

The atomization angle batch path still uses the existing `PlayAtmAngleCPP/main.exe`
runtime for performance. Python writes the legacy input file through
`core.atomization_angle_runner.AtomizationAngleCppRunner` and executes the C++
program with explicit error handling.

## Validation

Run lightweight checks:

```powershell
python -B -m compileall .
python -B -m unittest discover -s tests
```
