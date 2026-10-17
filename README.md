# Scout Laptop AI

Van Scout — the big brain that runs on the ThinkPad in the van (Qwen3.6-35B-A3B).
The phone app (Scout Android) is the face; this repo is the laptop side.

## USB Prep on Windows — install (the user path)

**Download `UsbPrep-Setup.exe` from this repo's Releases and run it.**
That's the whole install:

- Per-user install — **no Administrator rights and no Python needed**.
- You get **Scout USB Prep** in the Start Menu and on the Desktop.
- Uninstall any time in **Windows Settings → Apps**.

The installer is not code-signed, so Windows SmartScreen will warn the
first time you run it. That is expected — click **More info**, then
**Run anyway**.

When the app itself opens it **will** ask for Administrator (a Windows
prompt — click Yes): making the USB drive bootable requires it. That
prompt comes from the app, not the installer.

The exe is built by GitHub Actions on a Windows runner
(`.github/workflows/build-usbprep-setup.yml`) — the usb-prep self-tests
run there first, and packaging only happens if they pass.
(Note: the workflow file is staged at
`thinkpad/windows-installer/build-usbprep-setup.yml` — the API
credential can't write to `.github/workflows/`, so it needs one manual
move on the GitHub website to activate.)

### Developer fallback (not the user path)

Running from source still works and is kept for development only:

- `start-usb-prep.bat` — checks for Python, then launches `usb-prep.py`.
- Requires Python 3 (python.org, tick **"Add python.exe to PATH"**).
- To rebuild the installer yourself on a Windows PC, see
  `thinkpad/windows-installer/` (PyInstaller spec + Inno Setup script +
  `build-windows-installer.bat`).

## Files

- `UsbPrep-Setup.exe` (Releases) — The Windows installer for the USB prep tool (see above).
- `start-usb-prep.bat` — DEVELOPER FALLBACK: double-click on the Windows home PC to launch the USB prep tool from source.
- `usb-prep.py` — Prepares the 512GB flash drive: Ubuntu installer + ~300GB of models/maps/data + the installer below.
- `thinkpad/windows-installer/` — Installer packaging: `UsbPrep.spec` (PyInstaller, single-file windowed exe), `UsbPrep-Setup.iss` (Inno Setup, per-user), `build-windows-installer.bat` (local Windows build).
- `.github/workflows/build-usbprep-setup.yml` — Builds `UsbPrep-Setup.exe` on windows-latest; self-tests gate the build; attaches the installer to a release when tagged `usbprep-v*`. (Staged copy: `thinkpad/windows-installer/build-usbprep-setup.yml` — see the note above.)
- `files/` — The knowledge tree the prep tool stages onto the USB (libraries + `files/van-manuals/`; the manual PDFs themselves are fetched by `files/van-manuals/download-manuals.sh`, never stored in this repo).
- `scout-installer.py` — Runs on the ThinkPad from the prepared USB; sets up Ubuntu + Scout + all models.
- `scout-persona.txt` — Scout's system prompt / personality for the van.
- `outpost_client.py` — Python client for Outpost (Shield/TV-box control) from the ThinkPad.
- `scout-thinkpad-home-spec.md` — The living spec: architecture, network, multi-instance, wake words, queue, and the app-parity checklist.
- `name_sync.py` — ThinkPad-side name sync: canonical name store + HTTP sync API (port 8091). Change the name on either body, both share one name. Run `python3 name_sync.py --self-test` to verify.
- `NAME-SYNC-PROTOCOL.md` — The name-sync wire protocol: message format, endpoints, conflict rule, offline/queue behavior, wake-word rule.
- `parts-interchange-db.json` — Authoritative offline parts table (697 entries). Wired into usb-prep + installer (knowledge manifest) 2026-10-16.
- `DVR-BACKEND-TEST-PLAN.md` — JOINLGO → Traccar/Frigate test plan: prove backend first, G2-WS observational tests, gated cutover.
- `PREP-STATUS.md` — ThinkPad prep checkpoint (2026-10-16): what prep is done, what the full build still needs, blockers.

## Status

PREP done 2026-10-16 (see `PREP-STATUS.md`). Install chain is still shells with
stubs — unimplemented steps now fail loudly as PREP STUBs instead of silently
passing. Real logic lands at "pull it together," gated on phone-app lessons
(Scout-first plan). See `scout-thinkpad-home-spec.md` for the full plan.
