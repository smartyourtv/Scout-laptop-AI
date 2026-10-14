@echo off
REM Scout Van AI — USB Prep Launcher (Windows)
REM Double-click this file to start the USB preparation tool.
REM It checks for Python, and guides you to install it if missing.

title Scout Van AI - USB Prep

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python is not installed.
    echo.
    echo Opening the Python download page...
    echo Please install Python, making sure to check
    echo "Add python.exe to PATH" during setup.
    echo.
    echo After installing, double-click this file again.
    echo.
    start https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

echo Python found. Starting USB prep tool...
echo.
python "%~dp0usb-prep.py"
if %errorlevel% neq 0 (
    echo.
    echo The tool exited with an error. See above for details.
    pause
)
