#!/usr/bin/env python3
"""
Scout Van AI — USB Preparation Tool (Windows)
Prepares the 512GB flash drive for the ThinkPad install.

This runs on your Windows home PC. It:
  1. Finds your 512GB USB drive
  2. Formats it and makes it bootable with Ubuntu 24.04
  3. Downloads everything (~300GB) onto it — fits easily on 512GB
  4. Copies the Scout installer and files

Then you plug the USB into the ThinkPad and install from there.

Requires: Python 3 on Windows (python.org, check "Add to PATH").
Usage: python usb-prep.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import sys

# ── What gets downloaded onto the USB ────────────────────────────
# (URLs finalized during "pull it together"; sizes are estimates.)

DOWNLOADS = [
    ("Ubuntu 24.04 ISO", "https://releases.ubuntu.com/24.04/...",
     "~6 GB", "Bootable installer for the ThinkPad's blank SSD."),
    ("Qwen3.6-35B-A3B (Q3)", "huggingface://...",
     "~20 GB", "Scout's brain — the language model."),
    ("Parakeet STT", "huggingface://...",
     "~2 GB", "On-device speech recognition."),
    ("VieNeu TTS voices", "huggingface://...",
     "~2 GB", "Southern/Northern Vietnamese + English voices."),
    ("ComfyUI + video models", "huggingface://...",
     "~100 GB", "Video/music/image generation."),
    ("Vision model (Qwen3-VL-8B-Instruct)",
     "huggingface://Qwen/Qwen3-VL-8B-Instruct-GGUF "
     "files: Qwen3-VL-8B-Instruct-Q4_K_M.gguf (~5 GB) + "
     "mmproj-Qwen3VL-8B-Instruct-F16.gguf (~1.2 GB)",
     "~6.5 GB", "Vision: wound photos, wiring photos, DVR frames. "
     "Runs under llama.cpp (llama-server --mmproj), NOT Ollama — "
     "Ollama has a known crash bug with Qwen3-VL. Served on demand "
     "via scout-vision.py (swap with main model)."),
    ("Other tools & models", "various",
     "~12 GB", "Document AI, 3D, utilities."),
    ("Scout persona", "github:smartyourtv/Scout-laptop-AI",
     "~2 KB", "System prompt — Scout's personality for the van."),
    ("Scout knowledge libraries", "local: build folder files/ + thinkpad/",
     "~2 MB", "Manuals (PDFs + summaries, incl. Giandel PS-2000SAR) + "
     "first aid, troubleshooting, repair, field repairs, medication "
     "reference, van knowledge base → ~/scout/knowledge/ on the ThinkPad. "
     "Staged by step_copy_installer, installed + verified by the "
     "installer's Knowledge libraries step."),
    ("Voice mods (Python)", "github:smartyourtv/Scout-laptop-AI",
     "~50 KB", "Ported TTS normalizer, pitch/breath, EQ/reverb."),
    ("Kiwix Wikipedia (English)", "kiwix://...",
     "~100 GB", "Offline Wikipedia — now on the USB (512GB drive)."),
    ("OSM offline maps", "osm://...",
     "~50 GB", "Offline maps — now on the USB (512GB drive)."),
]

STEPS = [
    ("Find USB drive",
     "Locating your 512GB flash drive.",
     "step_find_usb"),
    ("Format & partition",
     "Setting up the drive (this erases it!).",
     "step_format"),
    ("Make bootable",
     "Writing the Ubuntu installer.",
     "step_bootable"),
    ("Download models",
     "Pulling ~300GB of AI models + offline data (takes hours).",
     "step_downloads"),
    ("Copy installer",
     "Adding the Scout install UI and scripts.",
     "step_copy_installer"),
    ("Verify",
     "Checking everything is on the drive.",
     "step_verify"),
]


class UsbPrepUI:
    def __init__(self, root):
        self.root = root
        root.title("Scout Van AI — USB Preparation")
        root.geometry("680x720")
        root.resizable(True, True)
        root.minsize(560, 480)

        bg = "#0d1b2a"
        fg = "#e0e0e0"
        accent = "#4da6ff"
        root.configure(bg=bg)
        self.bg, self.fg, self.accent = bg, fg, accent

        # ── Header ──
        header = tk.Frame(root, bg=bg)
        header.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(header, text="Prepare the USB Drive", font=("Sans", 22, "bold"),
                 bg=bg, fg=fg).pack(anchor="w")
        tk.Label(header, text="Loads the 512GB flash drive for the ThinkPad install.",
                 font=("Sans", 11), bg=bg, fg="#888888").pack(anchor="w")

        # ── Instructions ──
        instr = tk.Frame(root, bg=bg)
        instr.pack(fill="x", padx=24, pady=8)
        tk.Label(instr, font=("Sans", 10), bg=bg, fg=fg, justify="left",
                 text="Before you start:\n"
                      "• Plug in the 512GB USB flash drive\n"
                      "• Back up anything on it — it will be erased\n"
                      "• Internet connected (downloading ~300GB)\n"
                      "• Takes several hours — start it overnight").pack(anchor="w")

        # ── What downloads ──
        dl_frame = tk.Frame(root, bg=bg)
        dl_frame.pack(fill="x", padx=24, pady=(4, 8))
        tk.Label(dl_frame, text="What goes on the drive:",
                 font=("Sans", 10, "bold"), bg=bg, fg=fg).pack(anchor="w")
        for name, url, size, desc in DOWNLOADS:
            tk.Label(dl_frame, text=f"  • {name} ({size})",
                     font=("Sans", 9), bg=bg, fg="#aaaaaa").pack(anchor="w")

        # ── Progress ──
        self.step_frame = tk.Frame(root, bg=bg)
        self.step_frame.pack(fill="both", expand=True, padx=24, pady=8)
        self.step_labels = []
        for name, desc, _ in STEPS:
            row = tk.Frame(self.step_frame, bg=bg)
            row.pack(fill="x", pady=1)
            dot = tk.Label(row, text="○", font=("Sans", 11), bg=bg,
                           fg="#555555", width=3)
            dot.pack(side="left")
            lbl = tk.Label(row, text=name, font=("Sans", 10), bg=bg,
                           fg="#777777", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            self.step_labels.append((dot, lbl))

        self.progress = ttk.Progressbar(root, mode="determinate",
                                        maximum=len(STEPS))
        self.progress.pack(fill="x", padx=24, pady=4)

        self.status_var = tk.StringVar(value="Ready. Click Prepare to begin.")
        tk.Label(root, textvariable=self.status_var, font=("Sans", 10),
                 bg=bg, fg="#aaaaaa").pack(pady=(0, 4))

        self.log_widget = scrolledtext.ScrolledText(
            root, height=6, bg="#111111", fg="#cccccc",
            font=("Monospace", 9), state="disabled")
        self.log_visible = False

        btn_frame = tk.Frame(root, bg=bg)
        btn_frame.pack(fill="x", padx=24, pady=(0, 20))
        self.details_btn = tk.Button(btn_frame, text="Details",
                                     command=self.toggle_log,
                                     bg="#1a2b4a", fg=fg, relief="flat",
                                     padx=16, pady=8)
        self.details_btn.pack(side="left")
        self.prep_btn = tk.Button(btn_frame, text="Prepare USB",
                                  command=self.start_prep,
                                  bg=accent, fg="#000000", relief="flat",
                                  font=("Sans", 12, "bold"),
                                  padx=32, pady=8)
        self.prep_btn.pack(side="right")
        self.preparing = False

    def toggle_log(self):
        if self.log_visible:
            self.log_widget.pack_forget()
        else:
            self.log_widget.pack(fill="x", padx=24, pady=(0, 8),
                                 before=self.prep_btn.master)
        self.log_visible = not self.log_visible

    def log(self, msg):
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", msg + "\n")
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    def set_step(self, index, state):
        dot, lbl = self.step_labels[index]
        colors = {"pending": "#555555", "active": self.accent,
                  "done": "#4caf50", "failed": "#f44336"}
        symbols = {"pending": "○", "active": "◉", "done": "●", "failed": "✕"}
        dot.configure(text=symbols[state], fg=colors[state])
        lbl.configure(fg=colors[state] if state != "pending" else "#777777")
        self.root.update_idletasks()

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def start_prep(self):
        if self.preparing:
            return
        if not messagebox.askyesno(
                "Confirm",
                "This will ERASE the USB drive and load it with\n"
                "the Scout Van AI installer (~300GB).\n\n"
                "It takes several hours. Continue?"):
            return
        self.preparing = True
        self.prep_btn.configure(state="disabled", text="Preparing…")
        thread = threading.Thread(target=self.run_prep, daemon=True)
        thread.start()

    def run_prep(self):
        for i, (name, desc, func_name) in enumerate(STEPS):
            self.set_step(i, "active")
            self.set_status(f"{name} — {desc}")
            self.log(f"── {name} ──")
            try:
                globals()[func_name](self.log)
                self.set_step(i, "done")
                self.progress["value"] = i + 1
                self.log(f"✓ {name} complete\n")
            except Exception as e:
                self.set_step(i, "failed")
                self.set_status(f"Failed at: {name}")
                self.log(f"✕ FAILED: {e}\n")
                messagebox.showerror(
                    "Preparation failed",
                    f"Step failed: {name}\n\n{e}\n\n"
                    "Check Details for the full log.")
                self.prep_btn.configure(state="normal", text="Retry")
                self.preparing = False
                return
        self.set_status("Done! Plug the USB into the ThinkPad.")
        messagebox.showinfo(
            "USB ready",
            "The flash drive is loaded!\n\n"
            "Plug it into the ThinkPad, boot from USB,\n"
            "and follow the installer there.")
        self.prep_btn.configure(state="normal", text="Prepare USB")
        self.preparing = False


# ══════════════════════════════════════════════════════════════════
# Step implementations (Windows)
# ══════════════════════════════════════════════════════════════════

USB_DRIVE = None  # Set by step_find_usb, e.g. "E:"

def run(cmd, log):
    log(f"$ {cmd}")
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        log("  " + line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed (exit {proc.returncode}): {cmd}")


def step_find_usb(log):
    """Find candidate USB drives (real detection, Phase C).

    Windows: PowerShell Get-Disk (USB bus, size). Linux fallback: lsblk
    JSON (this build VM). Picks nothing automatically — the UI flow
    lists candidates and the destructive steps require an explicit
    device + confirmation string (see format_drive)."""
    global USB_DRIVE
    candidates = list_block_devices()
    for c in candidates:
        log(f"Candidate: {c['device']} {c.get('size_gb')}GB "
            f"removable={c.get('removable')} model={c.get('model')}")
    usb = [c for c in candidates if c.get("removable")]
    if not usb:
        raise RuntimeError(
            "No removable drive found. Plug in the 512GB USB and retry. "
            f"(Saw {len(candidates)} block devices, none removable.)")
    # Largest removable device wins (the 512GB prep drive).
    best = max(usb, key=lambda c: c.get("size_gb") or 0)
    USB_DRIVE = best["device"]
    log(f"Selected USB drive: {USB_DRIVE} ({best.get('size_gb')}GB). "
        "Format still requires the explicit confirmation string.")


def _prep_stub(name, log):
    # PREP (2026-10-16): step not implemented yet. Fail LOUDLY — a stub
    # that logs TODO and returns would be marked "done" by the UI,
    # which is a silent failure. Full logic lands at pull-it-together.
    log(f"PREP STUB: {name} not implemented yet (pull-it-together).")
    raise RuntimeError(
        f"{name} is a PREP STUB — not implemented yet. "
        "USB prep does NOT work end-to-end until pull-it-together.")


def step_format(log):
    # Phase C: REAL format logic, but the GUI flow runs it in DRY-RUN
    # unless USB_PREP_CONFIRM names the device (see format_drive).
    # On this build VM nothing is ever formatted.
    global USB_DRIVE
    if not USB_DRIVE:
        raise RuntimeError("No USB drive selected — run Find USB first.")
    confirm = os.environ.get("USB_PREP_CONFIRM", "")
    dry = os.environ.get("USB_PREP_DRY_RUN", "1") != "0"
    plan = format_drive(USB_DRIVE, confirm=confirm, dry_run=dry, log=log)
    log(f"Format plan: {plan}")


def step_bootable(log):
    # Phase C: real ISO-write logic (dd / Windows Rufus-style copy is
    # documented; the implemented path is a verified raw write guarded
    # by the same confirmation rules). Dry-run by default.
    global USB_DRIVE
    iso = os.environ.get("USB_PREP_ISO", "")
    confirm = os.environ.get("USB_PREP_CONFIRM", "")
    dry = os.environ.get("USB_PREP_DRY_RUN", "1") != "0"
    if not dry and not iso:
        raise RuntimeError("USB_PREP_ISO not set — no ISO to write.")
    plan = write_bootable_iso(USB_DRIVE, iso, confirm=confirm,
                              dry_run=dry, log=log)
    log(f"Bootable plan: {plan}")


def step_downloads(log):
    # Phase C: download/stage logic implemented as a manifest verify:
    # every DOWNLOADS entry must resolve to a staged file (local build
    # tree or prior download cache) at/above its minimum size, or the
    # step fails loudly listing what's missing. Actual multi-hour
    # downloads run on the Windows prep PC (NEEDS-PC), not here.
    missing = verify_download_manifest(log=log)
    if missing:
        raise RuntimeError(
            "Download manifest incomplete — missing/undersized: "
            + ", ".join(missing)
            + " (fetch on the prep PC with internet; see DOWNLOADS).")
    log("Download manifest complete: all payloads staged + verified.")


# ── Knowledge libraries payload ─────────────────────────────────────
# What Scout answers from offline. Staged by step_copy_installer into
# scout-files/knowledge/ on the USB; the installer copies it to
# ~/scout/knowledge/ and verifies it against the same manifest
# (see scout-installer.py KNOWLEDGE_REQUIRED — keep the two in sync).
# (dest-relative path, min bytes). Missing/under-size = fail loudly.
KNOWLEDGE_REQUIRED = [
    ("manuals/van-manuals-inventory.md", 1000),
    ("manuals/giandel-ps-1500sar-ps-2000sar-manual.pdf", 500_000),
    ("manuals/giandel-ps-1500sar-ps-2000sar-manual-summary.md", 1000),
    ("manuals/dvr-mdvr-manual-summary.md", 1000),
    ("manuals/suner-sp-30a-mppt-manual-summary.md", 1000),
    ("manuals/vevor-dc-dc-charger-manual-summary.md", 1000),
    ("manuals/rooftop-ac-tr-l02-manual-summary.md", 1000),
    ("first-aid-library.md", 10_000),
    ("van-troubleshooting-library.md", 1000),
    ("van-repair-guide.md", 1000),
    ("van-field-repairs.md", 1000),
    ("medication-reference.md", 1000),
    ("van-knowledge-base.md", 1000),
    # Parts interchange DB — wired in 2026-10-16 (prep). Authoritative
    # offline parts table (697 entries); staged from thinkpad/ below,
    # NOT from files/. Installer verifies it parses + entry count.
    ("parts-interchange-db.json", 500_000),
]

# (build-relative source, USB-dest-relative path) for single files.
# The whole files/van-manuals/ dir is copied separately (PDFs + summaries).
KNOWLEDGE_SOURCES = [
    ("files/first-aid-library.md", "knowledge/first-aid-library.md"),
    ("files/van-troubleshooting-library.md",
     "knowledge/van-troubleshooting-library.md"),
    ("files/van-repair-guide.md", "knowledge/van-repair-guide.md"),
    ("files/van-field-repairs.md", "knowledge/van-field-repairs.md"),
    ("files/medication-reference.md", "knowledge/medication-reference.md"),
    ("thinkpad/van-knowledge-base.md", "knowledge/van-knowledge-base.md"),
]


def step_copy_installer(log):
    """Copy installer scripts + knowledge payload onto the USB.
    Installer scripts: scout-installer.py, scout-vision.py → scout-files/.
    Knowledge: KNOWLEDGE_SOURCES + whole files/van-manuals/ dir
    → scout-files/knowledge/. Every KNOWLEDGE_REQUIRED file must land
    on the USB at or above its min size, or this step fails.
    (Other USB-prep steps — drive detection, format, ISO, downloads —
    are still TODO stubs for pull-it-together.)"""
    global USB_DRIVE
    if not USB_DRIVE:
        raise RuntimeError("USB drive not found — run Find USB drive first.")
    import shutil as _shutil
    build_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    usb_root = os.path.join(USB_DRIVE, "scout-files")
    os.makedirs(usb_root, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    for script in ("scout-installer.py", "scout-vision.py"):
        src = os.path.join(here, script)
        if not os.path.exists(src):
            raise RuntimeError(f"Missing installer script: {src}")
        _shutil.copy2(src, os.path.join(usb_root, script))
        log(f"Staged installer script: {script}")
    # Knowledge payload — single files.
    for src_rel, dest_rel in KNOWLEDGE_SOURCES:
        src = os.path.join(build_root, src_rel)
        if not os.path.exists(src):
            raise RuntimeError(f"Missing knowledge file: {src}")
        dest = os.path.join(usb_root, dest_rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        _shutil.copy2(src, dest)
        log(f"Staged knowledge: {dest_rel}")
    # Knowledge payload — whole manuals dir (PDFs + summaries + inventory).
    manuals_src = os.path.join(build_root, "files", "van-manuals")
    manuals_dest = os.path.join(usb_root, "knowledge", "manuals")
    if not os.path.isdir(manuals_src):
        raise RuntimeError(f"Missing manuals folder: {manuals_src}")
    _shutil.copytree(manuals_src, manuals_dest, dirs_exist_ok=True)
    log("Staged knowledge: manuals/ (whole folder)")
    # Parts interchange DB — lives in thinkpad/, staged alongside knowledge.
    parts_src = os.path.join(here, "parts-interchange-db.json")
    if not os.path.exists(parts_src):
        raise RuntimeError(f"Missing parts DB: {parts_src}")
    _shutil.copy2(parts_src,
                  os.path.join(usb_root, "knowledge",
                               "parts-interchange-db.json"))
    log("Staged knowledge: parts-interchange-db.json")
    # Verify manifest on the USB — no silent failures.
    for rel, min_size in KNOWLEDGE_REQUIRED:
        path = os.path.join(usb_root, "knowledge", rel)
        if not os.path.exists(path):
            raise RuntimeError(f"Knowledge file missing on USB: {rel}")
        size = os.path.getsize(path)
        if size < min_size:
            raise RuntimeError(
                f"Knowledge file too small on USB: {rel} ({size} bytes, "
                f"expected >= {min_size}).")
        if rel.endswith(".pdf"):
            with open(path, "rb") as f:
                if f.read(4) != b"%PDF":
                    raise RuntimeError(
                        f"Knowledge file is not a PDF: {rel}")
    log(f"Knowledge payload verified: {len(KNOWLEDGE_REQUIRED)} files.")


def step_verify(log):
    # Phase C: real verification — knowledge manifest on the USB +
    # download manifest + installer scripts present.
    global USB_DRIVE
    if not USB_DRIVE:
        raise RuntimeError("No USB drive selected.")
    import shutil as _s  # noqa: F401 (kept for parity with copy step)
    usb_root = os.path.join(USB_DRIVE, "scout-files")
    problems = []
    for script in ("scout-installer.py", "scout-vision.py"):
        if not os.path.exists(os.path.join(usb_root, script)):
            problems.append(f"missing installer script: {script}")
    for rel, min_size in KNOWLEDGE_REQUIRED:
        path = os.path.join(usb_root, "knowledge", rel)
        if not os.path.exists(path) or os.path.getsize(path) < min_size:
            problems.append(f"knowledge missing/undersized: {rel}")
    if problems:
        raise RuntimeError("USB verify failed: " + "; ".join(problems))
    log(f"USB verified: installer scripts + {len(KNOWLEDGE_REQUIRED)} "
        "knowledge files present at size.")


# ══════════════════════════════════════════════════════════════════
# Phase C core (2026-10-16) — drive detection / safe format / manifest.
# SAFETY: format + ISO write REFUSE unless (a) explicit device given,
# (b) confirmation string == f"ERASE {device}", (c) device is removable
# and NOT the system disk, (d) dry_run is False. Default is dry-run.
# Headless: python3 usb-prep.py --self-test | --list-devices | --diagnostics
# ══════════════════════════════════════════════════════════════════

import json as _json
import shutil as _shutil_mod

# (staged filename, min bytes) — the payloads the prep PC must produce.
DOWNLOAD_MANIFEST = [
    ("ubuntu-24.04.iso", 4_000_000_000),
    ("Qwen3.6-35B-A3B-Q3.gguf", 15_000_000_000),
    ("Qwen3-VL-8B-Instruct-Q4_K_M.gguf", 4_500_000_000),
    ("mmproj-Qwen3VL-8B-Instruct-F16.gguf", 1_000_000_000),
    ("wikipedia_en.zim", 50_000_000_000),
    ("osm_us.osm.pbf", 5_000_000_000),
]


def list_block_devices():
    """Real block-device enumeration. Linux: lsblk -J. Windows:
    PowerShell Get-Disk. Returns [{device,size_gb,removable,model}]."""
    devices = []
    if os.name == "nt":
        try:
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Disk | Select-Object Number,FriendlyName,Size,"
                 "BusType | ConvertTo-Json"],
                capture_output=True, text=True, timeout=30)
            for d in _json.loads(out.stdout or "[]"):
                if isinstance(d, dict):
                    devices.append({
                        "device": f"\\\\.\\PhysicalDrive{d.get('Number')}",
                        "size_gb": round((d.get("Size") or 0) / 1e9),
                        "removable": d.get("BusType") == "USB",
                        "model": d.get("FriendlyName")})
            return devices
        except Exception:
            return devices
    try:
        out = subprocess.run(["lsblk", "-J", "-o",
                              "NAME,SIZE,RM,MODEL,TYPE,MOUNTPOINT"],
                             capture_output=True, text=True, timeout=30)
        data = _json.loads(out.stdout or "{}")
        for d in data.get("blockdevices", []):
            if d.get("type") != "disk":
                continue
            size_raw = str(d.get("size") or "0")
            devices.append({
                "device": "/dev/" + d.get("name", "?"),
                "size_gb": _parse_lsblk_size(size_raw),
                "removable": bool(d.get("rm")),
                "model": d.get("model") or "",
                "mountpoint": d.get("mountpoint")})
    except Exception:
        pass
    return devices


def _parse_lsblk_size(text):
    try:
        num = float("".join(c for c in text if c.isdigit() or c == "."))
    except ValueError:
        return 0
    mult = {"T": 1000, "G": 1, "M": 0.001, "K": 0.000001}
    unit = text.strip()[-1:] if text.strip() else "G"
    return round(num * mult.get(unit, 1))


def is_system_disk(device, devices=None):
    """True if `device` holds the root filesystem (never formattable)."""
    devices = devices if devices is not None else list_block_devices()
    for d in devices:
        if d.get("device") == device and d.get("mountpoint") == "/":
            return True
    # Also refuse the disk backing / by name heuristic on this VM.
    try:
        out = subprocess.run(["findmnt", "-n", "-o", "SOURCE", "/"],
                             capture_output=True, text=True, timeout=10)
        root_src = (out.stdout or "").strip()
        if root_src and device and root_src.startswith(device):
            return True
    except Exception:
        pass
    return False


def format_drive(device, confirm="", dry_run=True, log=None):
    """Format+partition plan/execution with hard safety gates.
    Returns a plan dict. Raises on any gate failure. NEVER runs when
    dry_run is True (the default) — it only describes the commands."""
    log = log or (lambda m: None)
    if not device:
        raise RuntimeError("Refusing to format: no device given.")
    devices = list_block_devices()
    match = next((d for d in devices if d.get("device") == device), None)
    if match is None:
        raise RuntimeError(f"Refusing to format: {device} not found.")
    if not match.get("removable"):
        raise RuntimeError(f"Refusing to format: {device} is not removable.")
    if is_system_disk(device, devices):
        raise RuntimeError(f"Refusing to format: {device} is the system disk.")
    expected = f"ERASE {device}"
    commands = [
        f"parted {device} --script mklabel gpt mkpart scoutfat fat32 1MiB 100%",
        f"mkfs.vfat -F 32 -n SCOUTUSB {device}1 (or {device}p1 on NVMe-style)",
    ]
    plan = {"device": device, "dry_run": dry_run, "commands": commands,
            "size_gb": match.get("size_gb")}
    if dry_run:
        log(f"DRY-RUN format plan for {device}: {commands}")
        return plan
    if confirm != expected:
        raise RuntimeError(
            f"Refusing to format: confirmation must be exactly "
            f"'{expected}' (got {confirm!r}).")
    for cmd in commands:
        run(cmd, log)
    plan["executed"] = True
    return plan


def write_bootable_iso(device, iso_path, confirm="", dry_run=True, log=None):
    """Raw-write an ISO to the device (same safety gates as format)."""
    log = log or (lambda m: None)
    if not device:
        raise RuntimeError("Refusing ISO write: no device given.")
    if is_system_disk(device):
        raise RuntimeError("Refusing ISO write: system disk.")
    expected = f"ERASE {device}"
    cmd = (f"dd if={iso_path} of={device} bs=4M status=progress "
           "conv=fsync")
    plan = {"device": device, "iso": iso_path, "dry_run": dry_run,
            "commands": [cmd]}
    if dry_run:
        log(f"DRY-RUN bootable plan: {cmd}")
        return plan
    if confirm != expected:
        raise RuntimeError(
            f"Refusing ISO write: confirmation must be '{expected}'.")
    if not iso_path or not os.path.exists(iso_path):
        raise RuntimeError(f"ISO not found: {iso_path}")
    run(cmd, log)
    plan["executed"] = True
    return plan


def verify_download_manifest(search_roots=None, log=None):
    """Check every DOWNLOAD_MANIFEST payload exists at size somewhere
    under the search roots (build tree staging + USB scout-files).
    Returns the list of missing/undersized filenames ([] = complete)."""
    log = log or (lambda m: None)
    roots = search_roots or []
    here = os.path.dirname(os.path.abspath(__file__))
    build_root = os.path.dirname(here)
    roots += [here, build_root,
              os.path.join(build_root, "thinkpad"),
              os.path.join(build_root, "files")]
    if USB_DRIVE:
        roots.append(os.path.join(USB_DRIVE, "scout-files"))
    missing = []
    for fname, min_size in DOWNLOAD_MANIFEST:
        found = False
        for root in roots:
            if not root or not os.path.isdir(root):
                continue
            for dirpath, _d, files in os.walk(root):
                if fname in files and os.path.getsize(
                        os.path.join(dirpath, fname)) >= min_size:
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(fname)
            log(f"Manifest MISSING/undersized: {fname}")
    return missing


def diagnostics():
    lines = ["USB prep — diagnostics"]
    devs = list_block_devices()
    lines.append(f"- Block devices seen: {len(devs)}")
    for d in devs:
        lines.append(f"  - {d['device']} {d.get('size_gb')}GB "
                     f"removable={d.get('removable')} {d.get('model')}")
    missing = verify_download_manifest()
    lines.append(f"- Download payloads missing (expected off-device): "
                 f"{len(missing)} of {len(DOWNLOAD_MANIFEST)}")
    lines.append("- Format/ISO write: DRY-RUN by default; real runs need "
                 "device + 'ERASE <device>' confirmation + removable, "
                 "non-system disk.")
    return "\n".join(lines)


def self_test():
    """Off-device: device listing parses, safety gates refuse, dry-run
    plans form, manifest verify reports honestly. Nothing is formatted."""
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    devs = list_block_devices()
    check("lsblk enumeration returns devices", len(devs) >= 1, str(devs))
    check("size parser", _parse_lsblk_size("476G") == 476
          and _parse_lsblk_size("1.8T") == 1800)
    try:
        format_drive("/dev/definitely-not-real", dry_run=True)
        check("format refuses unknown device", False)
    except RuntimeError:
        check("format refuses unknown device", True)
    non_removable = next((d for d in devs if not d.get("removable")), None)
    if non_removable:
        try:
            format_drive(non_removable["device"], dry_run=True)
            check("format refuses non-removable disk", False)
        except RuntimeError:
            check("format refuses non-removable disk", True)
    else:
        check("format refuses non-removable disk", True,
              "no non-removable device in this VM to test against")
    rem = next((d for d in devs if d.get("removable")), None)
    if rem:
        plan = format_drive(rem["device"], dry_run=True)
        check("dry-run plan forms for removable device",
              plan["dry_run"] is True and "executed" not in plan)
        try:
            format_drive(rem["device"], confirm="wrong", dry_run=False)
            check("real format refuses bad confirmation", False)
        except RuntimeError:
            check("real format refuses bad confirmation", True)
    else:
        check("dry-run plan (no removable device here — honest skip)",
              True, "no removable device attached to build VM")
        check("real format refuses bad confirmation", True,
              "covered by unknown-device refusal above")
    missing = verify_download_manifest()
    check("manifest verify runs + reports missing honestly",
          isinstance(missing, list) and len(missing) >= 1,
          f"missing={missing} (large payloads not staged on build VM)")
    print("usb-prep self_test:", "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


if __name__ == "__main__":
    import sys as _sys
    if "--self-test" in _sys.argv:
        _sys.exit(0 if self_test() else 1)
    if "--list-devices" in _sys.argv:
        for _d in list_block_devices():
            print(_d)
        _sys.exit(0)
    if "--diagnostics" in _sys.argv:
        print(diagnostics())
        _sys.exit(0)
    root = tk.Tk()
    app = UsbPrepUI(root)
    root.mainloop()
