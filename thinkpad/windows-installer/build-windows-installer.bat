@echo off
REM ══════════════════════════════════════════════════════════════
REM build-windows-installer.bat — build UsbPrep-Setup.exe on Windows.
REM
REM This is the DEVELOPER build script (the GitHub Actions workflow
REM .github/workflows/build-usbprep-setup.yml does the same steps).
REM Run from anywhere; it locates the repo root relative to itself.
REM
REM Prerequisites (developer machine only — NOT for the end user):
REM   - Python 3.11+ with PyInstaller:  pip install pyinstaller
REM   - Inno Setup 6 (iscc.exe on PATH or in the default folder)
REM ══════════════════════════════════════════════════════════════
setlocal
cd /d "%~dp0..\.."
set "ROOT=%CD%"
echo Repo root: %ROOT%

echo.
echo [1/5] usb-prep self-tests (must pass before packaging)...
python thinkpad\usb-prep.py --self-test
if errorlevel 1 (
    echo SELF-TESTS FAILED — not packaging.
    exit /b 1
)

echo.
echo [2/5] Staging the installer data tree...
if exist build\installer-data rmdir /s /q build\installer-data
mkdir build\installer-data\thinkpad
mkdir build\installer-data\files
copy /y thinkpad\scout-installer.py  build\installer-data\thinkpad\ >nul
copy /y thinkpad\van-knowledge-base.md build\installer-data\thinkpad\ >nul
copy /y scout-vision.py              build\installer-data\thinkpad\ >nul
copy /y parts-interchange-db.json    build\installer-data\thinkpad\ >nul
if not exist files (
    echo ERROR: no files\ knowledge tree in this checkout — cannot stage.
    exit /b 1
)
xcopy /e /i /y files build\installer-data\files >nul
if not exist build\installer-data\files\van-manuals\giandel-ps-1500sar-ps-2000sar-manual.pdf (
    echo WARNING: manual PDFs not in files\van-manuals — fetch them first
    echo          with files\van-manuals\download-manuals.sh, or the copy
    echo          step will fail loudly on the prep PC. Continuing anyway.
)

echo.
echo [3/5] PyInstaller — building UsbPrep.exe (single file, windowed)...
pyinstaller thinkpad\windows-installer\UsbPrep.spec --noconfirm --distpath dist --workpath build\pyinstaller
if errorlevel 1 (
    echo PYINSTALLER FAILED.
    exit /b 1
)

echo.
echo [4/5] Locating Inno Setup compiler...
set "ISCC=iscc"
where iscc >nul 2>&1
if errorlevel 1 (
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
        set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    ) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
        set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    ) else (
        echo Inno Setup 6 not found. Install it from https://jrsoftware.org/isdl.php
        exit /b 1
    )
)

echo.
echo [5/5] Inno Setup — building UsbPrep-Setup.exe...
"%ISCC%" /DDataDir=build\installer-data thinkpad\windows-installer\UsbPrep-Setup.iss
if errorlevel 1 (
    echo INNO SETUP FAILED.
    exit /b 1
)

echo.
echo DONE: dist-installer\UsbPrep-Setup.exe
endlocal
