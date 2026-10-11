@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
echo AtmProcess - environment setup
echo.
if exist ".venv\Scripts\python.exe" goto install

py -3 -c "import sys, struct, tkinter; sys.exit(sys.version_info < (3, 10) or struct.calcsize('P') != 8)" >nul 2>&1
if not errorlevel 1 goto create_with_launcher
python -c "import sys, struct, tkinter; sys.exit(sys.version_info < (3, 10) or struct.calcsize('P') != 8)" >nul 2>&1
if not errorlevel 1 goto create_with_python
echo No suitable Python installation was found.
echo Install 64-bit Python 3.10 or newer, including pip and Tcl/Tk.
echo Enable the Python launcher or add Python to PATH, then run this file again.
echo https://www.python.org/downloads/windows/
goto failed

:create_with_launcher
py -3 -m venv --copies ".venv"
if errorlevel 1 goto failed
goto install

:create_with_python
python -m venv --copies ".venv"
if errorlevel 1 goto failed

:install
".venv\Scripts\python.exe" -c "import sys, struct, tkinter; sys.exit(sys.version_info < (3, 10) or struct.calcsize('P') != 8)"
if errorlevel 1 goto failed
echo Installing dependencies into the local .venv directory...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto failed
echo.
echo Setup complete. Double-click start.bat to open AtmProcess.
pause
exit /b 0

:failed
echo.
echo Setup failed. Read the error above and see README.md for help.
echo Your settings and experimental data have not been changed.
pause
exit /b 1
