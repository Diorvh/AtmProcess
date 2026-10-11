@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if not exist ".venv\Scripts\python.exe" (
    echo Run setup_env.bat first to configure the local Python environment.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "main.py"
if errorlevel 1 (
    echo.
    echo AtmProcess could not finish normally. Keep the error above for diagnosis.
    echo If dependencies are missing, run setup_env.bat again.
    pause
    exit /b 1
)
exit /b 0
