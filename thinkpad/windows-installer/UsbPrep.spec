# -*- mode: python ; coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════
# UsbPrep.spec — PyInstaller build for the Scout USB Prep tool.
#
# Produces ONE windowed executable: UsbPrep.exe (single-file).
# Run from the REPO ROOT (paths below are repo-root relative):
#   pyinstaller thinkpad\windows-installer\UsbPrep.spec --noconfirm
# Output: dist\UsbPrep.exe  (the .iss then wraps it + the data tree)
#
# PyInstaller does NOT cross-compile: build on Windows only
# (the GitHub Actions windows-latest workflow does exactly this).
#
# Runtime data (installer scripts, knowledge files, manuals) is NOT
# baked into the exe — Inno Setup installs the data tree next to the
# exe and usb-prep.py resolves it there (see _module_dir/_build_root
# in usb-prep.py; frozen layout = <install>/thinkpad + <install>/files).
# ══════════════════════════════════════════════════════════════════

import os

REPO_ROOT = os.path.abspath(os.getcwd())

a = Analysis(
    [os.path.join(REPO_ROOT, "thinkpad", "usb-prep.py")],
    pathex=[os.path.join(REPO_ROOT, "thinkpad")],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="UsbPrep",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # GUI tool: windowed, no console window.
    console=False,
    windowed=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=os.path.join(REPO_ROOT, "thinkpad", "windows-installer",
                         "UsbPrep-version-info.txt"),
)
