#!/usr/bin/env python3
"""
Scout Van AI - Graphical Installer
ThinkPad P1 Gen 5 "pull it together" installer.

A nice, intuitive UI that walks through the full van Scout setup:
Ubuntu already installed, this sets up everything else automatically.

Usage: python3 scout-installer.py
    (or double-click in Files)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import shutil
import os
import sys
import time

# ── Installer steps ──────────────────────────────────────────────
# Each step: (display name, description, function name)
# Functions are defined below; they raise on failure.

STEPS = [
    ("System check",
     "Verifying disk space, memory, and GPU.",
     "step_system_check"),
    ("System packages",
     "Installing Python, audio libraries, and tools via apt.",
     "step_system_packages"),
    ("Python environment",
     "Creating virtual environment and installing Python packages.",
     "step_python_env"),
    ("Scout brain",
     "Copying talk.py, configs, wake-word, and voice files.",
     "step_scout_files"),
    ("AI models",
     "Copying Qwen, Parakeet, and voice models from USB.",
     "step_models"),
    ("Creative bundle",
     "Unpacking ComfyUI; linking video, image, music, and voice models.",
     "step_creative_bundle"),
    ("Knowledge libraries",
     "Copying manuals + first aid, troubleshooting, repair guides.",
     "step_knowledge"),
    ("Offline extras",
     "Copying Wikipedia and offline maps from the USB.",
     "step_downloads"),
    ("Services",
     "Setting up auto-start, wake word, and van Wi-Fi.",
     "step_services"),
    ("Self-test",
     "Verifying the install works.",
     "step_self_test"),
]


class InstallerUI:
    def __init__(self, root):
        self.root = root
        root.title("Scout Van AI — Installer")
        root.geometry("680x680")
        root.resizable(True, True)
        root.minsize(560, 460)

        # Dark theme to match Scout's vibe
        bg = "#0d1b2a"
        fg = "#e0e0e0"
        accent = "#4da6ff"
        root.configure(bg=bg)

        self.bg, self.fg, self.accent = bg, fg, accent

        # ── Header ──
        header = tk.Frame(root, bg=bg)
        header.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(header, text="Scout Van AI", font=("Sans", 22, "bold"),
                 bg=bg, fg=fg).pack(anchor="w")
        tk.Label(header, text="ThinkPad setup — everything installs automatically.",
                 font=("Sans", 11), bg=bg, fg="#888888").pack(anchor="w")

        # ── Instructions ──
        instr = tk.Frame(root, bg=bg)
        instr.pack(fill="x", padx=24, pady=8)
        tk.Label(instr, font=("Sans", 10), bg=bg, fg=fg, justify="left",
                 text="Before you start:\n"
                      "• Ubuntu 24.04 is installed on the ThinkPad\n"
                      "• This USB drive is plugged in\n"
                      "• Wikipedia + maps ride this USB — no big downloads\n"
                      "• About 45 minutes — mostly copying files").pack(anchor="w")

        # ── Progress list ──
        self.step_frame = tk.Frame(root, bg=bg)
        self.step_frame.pack(fill="both", expand=True, padx=24, pady=8)

        self.step_labels = []
        for i, (name, desc, _) in enumerate(STEPS):
            row = tk.Frame(self.step_frame, bg=bg)
            row.pack(fill="x", pady=2)
            dot = tk.Label(row, text="○", font=("Sans", 12), bg=bg, fg="#555555",
                           width=3)
            dot.pack(side="left")
            lbl = tk.Label(row, text=name, font=("Sans", 11), bg=bg, fg="#777777",
                           anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            self.step_labels.append((dot, lbl))

        # ── Progress bar ──
        self.progress = ttk.Progressbar(root, mode="determinate",
                                        maximum=len(STEPS))
        self.progress.pack(fill="x", padx=24, pady=(4, 4))

        # ── Status line ──
        self.status_var = tk.StringVar(value="Ready. Click Install to begin.")
        tk.Label(root, textvariable=self.status_var, font=("Sans", 10),
                 bg=bg, fg="#aaaaaa").pack(pady=(0, 8))

        # ── Log (collapsible) ──
        self.log_visible = False
        self.log_widget = scrolledtext.ScrolledText(
            root, height=8, bg="#111111", fg="#cccccc",
            font=("Monospace", 9), state="disabled")
        # hidden until "Details" clicked

        # ── Buttons ──
        btn_frame = tk.Frame(root, bg=bg)
        btn_frame.pack(fill="x", padx=24, pady=(0, 20))

        self.details_btn = tk.Button(btn_frame, text="Details",
                                     command=self.toggle_log,
                                     bg="#1a2b4a", fg=fg, relief="flat",
                                     padx=16, pady=8)
        self.details_btn.pack(side="left")

        self.install_btn = tk.Button(btn_frame, text="Install",
                                     command=self.start_install,
                                     bg=accent, fg="#000000", relief="flat",
                                     font=("Sans", 12, "bold"),
                                     padx=32, pady=8)
        self.install_btn.pack(side="right")

        self.installing = False

    # ── UI helpers ──

    def toggle_log(self):
        if self.log_visible:
            self.log_widget.pack_forget()
        else:
            self.log_widget.pack(fill="x", padx=24, pady=(0, 8),
                                 before=self.install_btn.master)
        self.log_visible = not self.log_visible

    def log(self, msg):
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", msg + "\n")
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    def set_step(self, index, state):
        """state: pending | active | done | failed"""
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

    # ── Install flow ──

    def start_install(self):
        if self.installing:
            return
        if not messagebox.askyesno(
                "Confirm",
                "This will install Scout Van AI on this ThinkPad.\n"
                "It takes about 45 minutes.\n\nContinue?"):
            return
        self.installing = True
        self.install_btn.configure(state="disabled", text="Installing…")
        thread = threading.Thread(target=self.run_install, daemon=True)
        thread.start()

    def run_install(self):
        for i, (name, desc, func_name) in enumerate(STEPS):
            self.set_step(i, "active")
            self.set_status(f"{name} — {desc}")
            self.log(f"── {name} ──")
            try:
                func = globals()[func_name]
                func(self.log)
                self.set_step(i, "done")
                self.progress["value"] = i + 1
                self.log(f"✓ {name} complete\n")
            except Exception as e:
                self.set_step(i, "failed")
                self.set_status(f"Failed at: {name}")
                self.log(f"✕ FAILED: {e}\n")
                messagebox.showerror(
                    "Install failed",
                    f"Step failed: {name}\n\n{e}\n\n"
                    "Check Details for the full log.")
                self.install_btn.configure(state="normal", text="Retry")
                self.installing = False
                return
        self.set_status("Done! Reboot and say \"hey scout\".")
        self.log("── All done ──")
        messagebox.showinfo(
            "Install complete",
            "Scout Van AI is installed!\n\n"
            "Reboot the ThinkPad, then say \"hey scout\" to test.")
        self.install_btn.configure(state="normal", text="Install")
        self.installing = False


# ══════════════════════════════════════════════════════════════════
# Install step implementations
# (Filled in during the "pull it together" phase.)
# ══════════════════════════════════════════════════════════════════

def run(cmd, log):
    """Run a shell command, streaming output to the log."""
    log(f"$ {cmd}")
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        log("  " + line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed (exit {proc.returncode}): {cmd}")


def _capture(cmd):
    """Run a command, return (returncode, combined output)."""
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def step_system_check(log):
    # Disk space, recomputed 2026-10-17 from usb-prep.py
    # PAYLOAD_SOURCES (the old "≥280GB / ~300GB" figures predated the
    # corrected manifest). Payload bytes landing on this drive:
    # core ≈152.8GB (main model 16.6 + vision 5.0 + mmproj 1.2 +
    # Wikipedia 119 + OSM ~11) + v3 creative ≈60.1GB (video 23.0 +
    # image 24.2 + music 7.7 + STT 3.6 + TTS 1.15 + upscale 0.5 +
    # ComfyUI 0.01) ≈ 213GB installed. Threshold: 240GB = the payload
    # + headroom for the venv, package installs, and ComfyUI's
    # extracted tree.
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (1024 ** 3)
    log(f"Free disk: {free_gb}GB")
    if free_gb < 240:
        raise RuntimeError(
            f"Need at least 240GB free, found {free_gb}GB.")
    # RAM + GPU — REAL checks (2026-10-17 dry-run audit). This step's
    # label promises disk + memory + GPU, but it used to verify disk
    # only and still log "System check passed" — a partial check
    # painted as a full pass. Now every promised item is verified, and
    # anything that cannot be verified FAILS the step loudly instead.
    mem_total_kb = None
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total_kb = int(line.split()[1])
                    break
    except OSError:
        mem_total_kb = None
    if not mem_total_kb:
        raise RuntimeError(
            "System check INCOMPLETE: could not read /proc/meminfo — "
            "RAM NOT verified, refusing to report a pass.")
    ram_gb = mem_total_kb // (1024 * 1024)
    log(f"RAM: {ram_gb}GB")
    if ram_gb < 16:
        raise RuntimeError(f"Need at least 16GB RAM, found {ram_gb}GB.")
    if not shutil.which("nvidia-smi"):
        raise RuntimeError(
            "System check INCOMPLETE: nvidia-smi not found — GPU NOT "
            "verified, refusing to report a pass. Install the NVIDIA "
            "driver, then re-run.")
    rc, out = _capture(
        "nvidia-smi --query-gpu=name,memory.total "
        "--format=csv,noheader,nounits")
    if rc != 0 or not out.strip():
        raise RuntimeError(
            f"System check INCOMPLETE: nvidia-smi failed "
            f"({out.strip()}) — GPU NOT verified, refusing to report "
            "a pass.")
    gpu_line = out.strip().splitlines()[0]
    try:
        gpu_name, gpu_mem_raw = gpu_line.rsplit(",", 1)
        gpu_mem_mib = int(gpu_mem_raw.strip())
        gpu_name = gpu_name.strip()
    except (ValueError, IndexError):
        raise RuntimeError(
            f"System check INCOMPLETE: could not parse GPU info "
            f"({gpu_line!r}) — refusing to report a pass.")
    log(f"GPU: {gpu_name}, {gpu_mem_mib} MiB VRAM")
    if gpu_mem_mib < 15000:
        raise RuntimeError(
            f"Need ~16GB VRAM for the main model, found "
            f"{gpu_mem_mib} MiB.")
    log("System check passed (disk + RAM + GPU all verified).")


def step_system_packages(log):
    run("sudo apt-get update", log)
    run("sudo apt-get install -y python3 python3-venv python3-pip "
        "portaudio19-dev ffmpeg git curl", log)


def _find_requirements(log):
    """Locate a requirements.txt for the venv: beside this installer
    (it rides the USB inside scout-files/) or at the root of the USB
    scout-files tree. Returns a path or None."""
    here = os.path.dirname(os.path.abspath(__file__))
    beside = os.path.join(here, "requirements.txt")
    if os.path.isfile(beside):
        return beside
    try:
        usb_tree = find_usb_dir(log, "scout-files")
    except RuntimeError:
        return None
    cand = os.path.join(usb_tree, "requirements.txt")
    return cand if os.path.isfile(cand) else None


def step_python_env(log):
    # DRY-RUN AUDIT FIX (2026-10-17): this step used to create the
    # venv, skip the package install entirely (it was a TODO), and
    # still log "Python environment ready" — the GUI then painted it
    # green for work that never ran (same class as the usb-prep
    # dry-run bug). Now: packages install for real from a staged
    # requirements.txt and are verified with pip check; with no
    # requirements file the step FAILS LOUDLY instead of claiming
    # ready.
    home = os.path.expanduser("~")
    venv = os.path.join(home, "scout", "venv")
    os.makedirs(os.path.dirname(venv), exist_ok=True)
    if not os.path.exists(venv):
        run(f"python3 -m venv {venv}", log)
    venv_python = os.path.join(venv, "bin", "python")
    if not os.path.isfile(venv_python):
        raise RuntimeError(
            f"venv python missing after create: {venv_python}")
    req = _find_requirements(log)
    if not req:
        raise RuntimeError(
            "Python packages NOT installed — PLANNED ONLY: no "
            "requirements.txt found beside the installer or in the "
            "USB scout-files/ tree. Stage one (usb-prep) and re-run; "
            "this step refuses to report 'ready' without a real "
            "install.")
    log(f"Installing Python packages from {req} …")
    run(f'"{venv_python}" -m pip install -r "{req}"', log)
    run(f'"{venv_python}" -m pip check', log)
    rc, out = _capture(f'"{venv_python}" -m pip freeze')
    n_pkgs = len([ln for ln in out.splitlines() if "==" in ln])
    log(f"Python environment ready: venv verified, {n_pkgs} packages "
        f"installed from {os.path.basename(req)}, pip check clean.")


def _prep_stub(name, log):
    # PREP (2026-10-16): step not implemented yet. Fail LOUDLY instead
    # of logging success — a stub marked "done" is a silent failure.
    # Full logic lands at pull-it-together (gated on phone-app lessons).
    log(f"PREP STUB: {name} not implemented yet (pull-it-together).")
    raise RuntimeError(
        f"{name} is a PREP STUB — not implemented yet. "
        "The installer does NOT work end-to-end until pull-it-together.")


def step_scout_files(log):
    # Phase C (2026-10-16): REAL logic. Copies the Scout brain payload
    # (talk.py, persona, configs, wake-word + voice files) from the USB
    # scout-files/ tree to ~/scout/ with size verification + a written
    # manifest. Build 1 interim lessons folded in as documented patterns
    # in the copied code's home (see scout_lessons.py notes in the
    # manifest): EmotionEngine semantics, EnergyVad 80ms gate,
    # AlwaysListen diagnostics, TTS stop counters, BCPA9 connection
    # reuse, UX explain+confirm+feedback. FINAL Build 1 lessons must be
    # re-checked when Build 1 completes.
    src = find_usb_dir(log, "scout-files")
    dest = os.path.join(os.path.expanduser("~"), "scout")
    # Issue A fix (2026-10-17): exclude payloads/ + knowledge/ — both
    # subtrees have their own dedicated copy steps (models/offline
    # pull from payloads/; step_knowledge copies knowledge/). Copying
    # them here too duplicated ~219GB of payload data into ~/scout/
    # (dead weight + roughly double the big-file copy time).
    manifest = copy_tree_verified(src, dest, log, subdir=None,
                                  exclude=("payloads", "knowledge"))
    # DRY-RUN AUDIT FIX (2026-10-17): an empty (or brain-less) source
    # tree used to sail through — zero files copied, step still green.
    if not manifest:
        raise RuntimeError(
            "Scout brain copy copied NOTHING — the USB scout-files/ "
            "tree is empty. Refusing to report success.")
    if not any(e["path"] == "talk.py" for e in manifest):
        raise RuntimeError(
            "Scout brain copy has no talk.py — the USB scout-files/ "
            "tree is not the Scout brain payload. Refusing to report "
            "success.")
    write_manifest(dest, manifest, log)
    log(f"Scout brain in place: {len(manifest)} files copied+verified.")


def step_models(log):
    # VISION MODEL — implemented 2026-10-16 (Shawn: "Make it so").
    # MAIN MODEL copy is implemented further down in this function
    # (Phase C) — an earlier comment here claimed it was still a TODO;
    # removed 2026-10-17 so the comments stop lying about the code.
    # Qwen3-VL-8B-Instruct GGUF + mmproj projector, served by llama.cpp
    # (llama-server --mmproj). NOT Ollama: Ollama has a known crash bug
    # with Qwen3-VL, and this build's stack is llama.cpp (see spec).
    # Files ride the USB (usb-prep.py DOWNLOADS) and land in ~/scout/models/.
    home = os.path.expanduser("~")
    models_dir = os.path.join(home, "scout", "models")
    os.makedirs(models_dir, exist_ok=True)
    vision_files = [
        ("Qwen3-VL-8B-Instruct-Q4_K_M.gguf", 4_500_000_000),
        ("mmproj-Qwen3VL-8B-Instruct-F16.gguf", 1_000_000_000),
    ]
    # USB mount: try the usual locations; installer runs from the USB.
    usb_roots = ["/media", "/mnt", os.path.join(home, "usb")]
    found = {}
    for fname, _min_size in vision_files:
        for root in usb_roots:
            for dirpath, _dirs, files in os.walk(root):
                if fname in files:
                    found[fname] = os.path.join(dirpath, fname)
                    break
                if dirpath.count(os.sep) - root.count(os.sep) > 4:
                    _dirs[:] = []
            if fname in found:
                break
    for fname, min_size in vision_files:
        dest = os.path.join(models_dir, fname)
        if os.path.exists(dest) and os.path.getsize(dest) >= min_size:
            log(f"Vision model already in place: {fname}")
            continue
        src = found.get(fname)
        if not src:
            raise RuntimeError(
                f"Vision model file not found on USB: {fname}\n"
                "usb-prep.py must download it from "
                "huggingface://Qwen/Qwen3-VL-8B-Instruct-GGUF first.")
        log(f"Copying {fname} from USB…")
        shutil.copy2(src, dest)
        if os.path.getsize(dest) < min_size:
            raise RuntimeError(f"Copied {fname} looks truncated "
                               f"({os.path.getsize(dest)} bytes).")
        log(f"Vision model in place: {fname}")
    # Phase C (2026-10-16): MAIN model copy — real logic.
    # Qwen3.6-35B-A3B (Q3 GGUF, ~20GB) rides the USB under scout-files/
    # models/ (or any models/ dir on the USB) and lands in ~/scout/models/.
    main_name, main_min = MAIN_MODEL_FILE
    dest_main = os.path.join(models_dir, main_name)
    if os.path.exists(dest_main) and os.path.getsize(dest_main) >= main_min:
        log(f"Main model already in place: {main_name}")
    else:
        src_main = find_file_on_usb(main_name, log)
        if not src_main:
            raise RuntimeError(
                f"Main model file not found on USB: {main_name}\n"
                "usb-prep.py must stage it (scout-files/models/) first.")
        log(f"Copying main model {main_name} from USB (large, be patient)…")
        shutil.copy2(src_main, dest_main)
        if os.path.getsize(dest_main) < main_min:
            raise RuntimeError(f"Copied {main_name} looks truncated "
                               f"({os.path.getsize(dest_main)} bytes).")
        log(f"Main model in place: {main_name}")
    log("AI models step complete (vision + main verified).")


# ── v3 creative bundle ────────────────────────────────────────────
# usb-prep v3 stages the creative/voice payloads under
# scout-files/payloads/ (apps/ + models/{video,image,music,stt,tts,
# upscale}/). Before this step existed the installer never referenced
# them at all — ComfyUI and ~60GB of models would have sat on the
# stick unused. This step copies them to canonical homes under
# ~/scout/models/ (mirroring the USB models/ layout), unpacks ComfyUI
# to ~/scout/apps/ComfyUI, extracts the Parakeet tarball in place,
# and symlinks the ComfyUI-consumed files into ComfyUI's own models/
# tree (one canonical copy on disk; links, not duplicates).
# Minimum sizes sit just under usb-prep's verified expected bytes —
# prep already size-verified the downloads; anything missing or
# truncated here FAILS the step loudly, never a silent skip.
CREATIVE_PAYLOAD_FILES = [
    # (path under payloads/, min bytes)
    ("apps/ComfyUI-v0.41.0.zip", 13_000_000),
    ("models/video/ltxv-2b-0.9.8-distilled-fp8.safetensors", 4_400_000_000),
    ("models/video/t5xxl_fp8_e4m3fn_scaled.safetensors", 5_100_000_000),
    ("models/video/wan2.2-ti2v-5b-fp8.safetensors", 5_200_000_000),
    ("models/video/umt5_xxl_fp8_e4m3fn_scaled.safetensors", 6_700_000_000),
    ("models/video/wan2.2_vae.safetensors", 1_400_000_000),
    ("models/music/ace_step_v1_3.5b.safetensors", 7_600_000_000),
    ("models/image/sd_xl_base_1.0.safetensors", 6_900_000_000),
    ("models/image/flux1-dev-fp8.safetensors", 17_200_000_000),
    ("models/stt/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2",
     480_000_000),
    ("models/upscale/RealESRGAN_x4plus.pth", 60_000_000),
    ("models/upscale/4x-UltraSharp.pth", 60_000_000),
    ("models/upscale/GFPGANv1.4.pth", 340_000_000),
]
CREATIVE_PAYLOAD_TREES = [
    # (dir under payloads/, [(file, min bytes), ...]) — multi-file
    # sets that must stay together in their named subfolder.
    ("models/stt/faster-whisper-large-v3", [
        ("model.bin", 3_000_000_000), ("config.json", 1_000),
        ("tokenizer.json", 2_000_000), ("vocabulary.json", 1_000_000)]),
    ("models/tts/VieNeu-TTS", [
        ("model.safetensors", 1_100_000_000), ("config.json", 500),
        ("generation_config.json", 100), ("tokenizer.json", 20_000_000),
        ("tokenizer_config.json", 10_000_000), ("vocab.json", 2_000_000),
        ("special_tokens_map.json", 100), ("voices.json", 10_000)]),
]
# ComfyUI model-tree links: ComfyUI models/<subdir> gets a symlink to
# the canonical file at ~/scout/<path>.
COMFYUI_LINKS = [
    ("checkpoints", "models/video/ltxv-2b-0.9.8-distilled-fp8.safetensors"),
    ("checkpoints", "models/video/wan2.2-ti2v-5b-fp8.safetensors"),
    ("checkpoints", "models/image/sd_xl_base_1.0.safetensors"),
    ("checkpoints", "models/image/flux1-dev-fp8.safetensors"),
    ("checkpoints", "models/music/ace_step_v1_3.5b.safetensors"),
    ("text_encoders", "models/video/t5xxl_fp8_e4m3fn_scaled.safetensors"),
    ("text_encoders", "models/video/umt5_xxl_fp8_e4m3fn_scaled.safetensors"),
    ("vae", "models/video/wan2.2_vae.safetensors"),
    ("upscale_models", "models/upscale/RealESRGAN_x4plus.pth"),
    ("upscale_models", "models/upscale/4x-UltraSharp.pth"),
    ("upscale_models", "models/upscale/GFPGANv1.4.pth"),
]


def _require_payload(payloads_root, rel, min_size):
    """Verify one expected payload exists at a sane size; return its
    path. Missing/truncated = loud failure, never a silent skip."""
    path = os.path.join(payloads_root, rel)
    if not os.path.isfile(path):
        raise RuntimeError(
            f"Creative bundle payload MISSING on USB: payloads/{rel}\n"
            "usb-prep v3 must stage the full creative bundle first.")
    size = os.path.getsize(path)
    if size < min_size:
        raise RuntimeError(
            f"Creative bundle payload too small: payloads/{rel} "
            f"({size} bytes, expected >= {min_size}).")
    return path


def _link_into(link_path, target, log):
    """Symlink link_path -> target and verify the link resolves.
    Re-runs are idempotent; a real file in the way is never clobbered."""
    os.makedirs(os.path.dirname(link_path), exist_ok=True)
    if os.path.islink(link_path):
        if os.path.realpath(link_path) == os.path.realpath(target):
            log(f"Link already in place: {link_path}")
            return
        os.unlink(link_path)
    elif os.path.exists(link_path):
        raise RuntimeError(
            f"Refusing to replace a real file with a link: {link_path}")
    os.symlink(target, link_path)
    if not os.path.exists(link_path):
        raise RuntimeError(
            f"Link does not resolve: {link_path} -> {target}")
    log(f"Linked: {link_path} -> {target}")


def step_creative_bundle(log):
    # v3 creative bundle wiring (2026-10-17). Every expected payload
    # is verified BEFORE anything is copied, so a short stick fails
    # fast instead of half-installing.
    home = os.path.expanduser("~")
    scout = os.path.join(home, "scout")
    tree = find_usb_dir(log, "scout-files")
    payloads = os.path.join(tree, "payloads")
    if not os.path.isdir(payloads):
        raise RuntimeError(
            f"No payloads/ folder in the USB scout-files tree "
            f"({tree}) — usb-prep v3 stages the creative bundle there.")
    for rel, min_size in CREATIVE_PAYLOAD_FILES:
        _require_payload(payloads, rel, min_size)
    for tree_rel, members in CREATIVE_PAYLOAD_TREES:
        for fname, min_size in members:
            _require_payload(
                payloads, os.path.join(tree_rel, fname), min_size)
    log(f"Creative bundle verified on USB: "
        f"{len(CREATIVE_PAYLOAD_FILES)} files + "
        f"{len(CREATIVE_PAYLOAD_TREES)} model sets.")
    # Single model files -> canonical homes under ~/scout/models/.
    for rel, _min_size in CREATIVE_PAYLOAD_FILES:
        if not rel.startswith("models/"):
            continue  # the ComfyUI zip is unpacked below, not copied
        src = os.path.join(payloads, rel)
        dest = os.path.join(scout, rel)
        if (os.path.exists(dest) and
                os.path.getsize(dest) == os.path.getsize(src)):
            log(f"Creative payload already in place: {rel}")
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        log(f"Copying creative payload {rel} from USB…")
        shutil.copy2(src, dest)
        if os.path.getsize(dest) != os.path.getsize(src):
            raise RuntimeError(f"Copied {rel} size mismatch.")
    # Multi-file sets copied as trees (their files stay together).
    for tree_rel, _members in CREATIVE_PAYLOAD_TREES:
        manifest = copy_tree_verified(payloads, scout, log,
                                      subdir=tree_rel)
        if not manifest:
            raise RuntimeError(
                f"Creative model set copied NOTHING: {tree_rel}")
    # Parakeet tarball: extract in place under models/stt/.
    stt_dir = os.path.join(scout, "models", "stt")
    os.makedirs(stt_dir, exist_ok=True)
    parakeet_dir = os.path.join(
        stt_dir, "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
    if not (os.path.isdir(parakeet_dir) and any(
            f.endswith(".onnx") for f in os.listdir(parakeet_dir))):
        tar_path = os.path.join(
            payloads, "models", "stt",
            "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2")
        log("Extracting Parakeet STT tarball…")
        with tarfile.open(tar_path, "r:bz2") as tf:
            tf.extractall(stt_dir, filter="data")
    if not (os.path.isdir(parakeet_dir) and any(
            f.endswith(".onnx") for f in os.listdir(parakeet_dir))):
        raise RuntimeError(
            "Parakeet extraction produced no model folder with .onnx "
            f"files at {parakeet_dir}.")
    log(f"Parakeet STT in place: {parakeet_dir}")
    # ComfyUI: unpack payloads/apps/ zip -> ~/scout/apps/ComfyUI.
    comfy_root = os.path.join(scout, "apps", "ComfyUI")
    if not os.path.isfile(os.path.join(comfy_root, "main.py")):
        apps_dir = os.path.join(scout, "apps")
        os.makedirs(apps_dir, exist_ok=True)
        zip_path = os.path.join(payloads, "apps", "ComfyUI-v0.41.0.zip")
        log("Unpacking ComfyUI…")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(apps_dir)
        extracted = os.path.join(apps_dir, "ComfyUI-0.41.0")
        if os.path.isdir(extracted) and not os.path.isdir(comfy_root):
            os.rename(extracted, comfy_root)
    if not os.path.isfile(os.path.join(comfy_root, "main.py")):
        raise RuntimeError(
            f"ComfyUI unpack did not produce {comfy_root}/main.py.")
    log(f"ComfyUI in place: {comfy_root}")
    # Link the ComfyUI-consumed models into ComfyUI's models/ tree.
    for subdir, canonical_rel in COMFYUI_LINKS:
        _link_into(
            os.path.join(comfy_root, "models", subdir,
                         os.path.basename(canonical_rel)),
            os.path.join(scout, canonical_rel), log)
    log("Creative bundle step complete (ComfyUI unpacked, models "
        "in place + linked).")


# ── Knowledge libraries ───────────────────────────────────────────
# Everything Scout answers from offline: manuals (PDFs + summaries)
# + first aid, troubleshooting, repair, field repairs, medication
# reference, van knowledge base. Staged on the USB under
# scout-files/knowledge/ by usb-prep.py; this step copies the tree to
# ~/scout/knowledge/ and verifies it. Keep in sync with usb-prep.py
# KNOWLEDGE_REQUIRED. Missing/under-size/non-PDF = fail loudly.
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
    # Parts interchange DB — wired in 2026-10-16 (prep). Keep in sync
    # with usb-prep.py KNOWLEDGE_REQUIRED. Verified as JSON below.
    ("parts-interchange-db.json", 500_000),
]


def find_usb_knowledge(log):
    """Locate scout-files/knowledge/ on the USB. Returns its path."""
    home = os.path.expanduser("~")
    for root in ("/media", "/mnt", os.path.join(home, "usb")):
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, _files in os.walk(root):
            if os.path.basename(dirpath) == "knowledge" and os.path.isdir(
                    os.path.join(dirpath, "manuals")):
                log(f"Found knowledge on USB: {dirpath}")
                return dirpath
            if dirpath.count(os.sep) - root.count(os.sep) > 4:
                _dirs[:] = []
    raise RuntimeError(
        "Knowledge folder not found on USB.\n"
        "usb-prep.py step_copy_installer must stage scout-files/knowledge/.")


def step_knowledge(log):
    home = os.path.expanduser("~")
    dest_root = os.path.join(home, "scout", "knowledge")
    src = find_usb_knowledge(log)
    log(f"Copying knowledge libraries to {dest_root}…")
    shutil.copytree(src, dest_root, dirs_exist_ok=True)
    for rel, min_size in KNOWLEDGE_REQUIRED:
        path = os.path.join(dest_root, rel)
        if not os.path.exists(path):
            raise RuntimeError(f"Knowledge file missing after copy: {rel}")
        size = os.path.getsize(path)
        if size < min_size:
            raise RuntimeError(
                f"Knowledge file too small: {rel} ({size} bytes, "
                f"expected >= {min_size}).")
        if rel.endswith(".pdf"):
            with open(path, "rb") as f:
                if f.read(4) != b"%PDF":
                    raise RuntimeError(
                        f"Knowledge file is not a PDF: {rel}")
        if rel.endswith(".json"):
            import json
            with open(path) as f:
                data = json.load(f)
            entries = data.get("entries") if isinstance(data, dict) else None
            if not entries:
                raise RuntimeError(
                    f"Parts DB has no entries after copy: {rel}")
            log(f"Parts DB verified: {len(entries)} entries ({rel}).")
    log(f"Knowledge libraries in place: {len(KNOWLEDGE_REQUIRED)} files "
        f"verified.")


def step_downloads(log):
    # Phase C: Kiwix Wikipedia + OSM maps copy from USB (512GB drive
    # holds everything — no downloading during install). Large ZIM/map
    # files are copied with verification; missing payload = loud fail.
    home = os.path.expanduser("~")
    dest = os.path.join(home, "scout", "offline-data")
    os.makedirs(dest, exist_ok=True)
    copied = 0
    for fname, min_size in OFFLINE_DATA_FILES:
        target = os.path.join(dest, fname)
        if os.path.exists(target) and os.path.getsize(target) >= min_size:
            log(f"Offline data already in place: {fname}")
            copied += 1
            continue
        src = find_file_on_usb(fname, log)
        if not src:
            raise RuntimeError(
                f"Offline data file not found on USB: {fname}\n"
                "usb-prep.py must stage Kiwix/OSM payload first.")
        log(f"Copying {fname} from USB (large)…")
        shutil.copy2(src, target)
        if os.path.getsize(target) < min_size:
            raise RuntimeError(f"Copied {fname} looks truncated.")
        copied += 1
    log(f"Offline data in place: {copied} files (Kiwix + OSM).")


def step_services(log):
    # Phase C: GENERATE systemd unit files (artifacts) and, when run on
    # the target with root, install+enable them. Generation is fully
    # off-device.
    # DRY-RUN AUDIT FIX (2026-10-17): this step used to return normally
    # — GUI green "done" — even when it had ONLY generated files: the
    # non-root path installed and enabled nothing, and even the root
    # path never ran `systemctl enable`, yet the installer still ended
    # with "Install complete". Now: the root path copies + daemon-
    # reloads + enables + verifies each unit; the non-root path logs
    # PLANNED ONLY and FAILS the step instead of painting it green.
    out_dir = generate_systemd_units(log=log)
    log(f"Systemd units generated under {out_dir}")
    units = sorted(f for f in os.listdir(out_dir)
                   if f.endswith(".service"))
    if os.geteuid() == 0 and os.path.isdir("/etc/systemd/system"):
        for unit in units:
            shutil.copy2(os.path.join(out_dir, unit),
                         os.path.join("/etc/systemd/system", unit))
        run("systemctl daemon-reload", log)
        for unit in units:
            run(f"systemctl enable {unit}", log)
            rc, out = _capture(f"systemctl is-enabled {unit}")
            if out.strip() != "enabled":
                raise RuntimeError(
                    f"Service {unit} copied but NOT enabled "
                    f"(is-enabled says: {out.strip() or 'no output'}).")
        log(f"Services installed + enabled + verified: "
            f"{', '.join(units)}")
    else:
        raise RuntimeError(
            "Services NOT installed — PLANNED ONLY: unit files were "
            f"generated under {out_dir}, but this run is not root (or "
            "has no /etc/systemd/system), so nothing was copied or "
            "enabled and this step must not show as done. Re-run the "
            "installer as root, or by hand: copy the units to "
            "/etc/systemd/system/, systemctl daemon-reload, then "
            "systemctl enable each one.")


def step_self_test(log):
    # Phase C: real self-test — files present, ports free, imports OK.
    # Mic/model-load checks need the laptop (reported, not faked).
    results = run_install_self_test(log=log)
    failures = [r for r in results if not r[1] and not r[2]]
    for name, ok, needs_laptop, detail in results:
        tag = "PASS" if ok else ("NEEDS-LAPTOP" if needs_laptop else "FAIL")
        log(f"[{tag}] {name}: {detail}")
    if failures:
        raise RuntimeError(
            "Self-test failures: " + ", ".join(f[0] for f in failures))


# ══════════════════════════════════════════════════════════════════
# Phase C core (2026-10-16) — off-device-buildable real logic.
# Headless-testable: python3 scout-installer.py --self-test
#                    python3 scout-installer.py --generate-systemd [dir]
# ══════════════════════════════════════════════════════════════════

import hashlib
import json as _json
import socket as _socket
import tarfile
import zipfile

MAIN_MODEL_FILE = ("Qwen3.6-35B-A3B-Q3.gguf", 15_000_000_000)
OFFLINE_DATA_FILES = [
    ("wikipedia_en.zim", 50_000_000_000),
    ("osm_us.osm.pbf", 5_000_000_000),
]

# systemd units generated by generate_systemd_units():
# name -> (description, exec, restart)
SYSTEMD_SERVICES = {
    "scout-brain": ("Scout brain (llama-server, main model, port 8080)",
                    "{home}/scout/venv/bin/python {home}/scout/talk.py",
                    "on-failure"),
    "scout-name-sync": ("Scout name sync (canonical name, port 8091)",
                        "{home}/scout/venv/bin/python {home}/scout/name_sync.py serve --host 0.0.0.0",
                        "on-failure"),
    "scout-vision": ("Scout vision swap helper (on-demand, port 8081)",
                     "{home}/scout/venv/bin/python {home}/scout/scout-vision.py --serve-stub",
                     "on-failure"),
    "scout-victron": ("Victron BLE listener (SmartSolar + Orion)",
                      "{home}/scout/venv/bin/python {home}/scout/victron_listener.py",
                      "always"),
    "scout-deterrence": ("Scout deterrence engine (Frigate events)",
                         "{home}/scout/venv/bin/python {home}/scout/deterrence.py --serve",
                         "always"),
}


def _sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def find_usb_dir(log, dirname):
    """Locate a named directory on a mounted USB. NEEDS-LAPTOP at run
    time (a real USB must be mounted); the search logic itself is real."""
    home = os.path.expanduser("~")
    for root in ("/media", "/mnt", os.path.join(home, "usb")):
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, _files in os.walk(root):
            if os.path.basename(dirpath) == dirname:
                log(f"Found {dirname} on USB: {dirpath}")
                return dirpath
            if dirpath.count(os.sep) - root.count(os.sep) > 4:
                _dirs[:] = []
    raise RuntimeError(f"{dirname} not found on USB (is it mounted?).")


def find_file_on_usb(fname, log):
    home = os.path.expanduser("~")
    for root in ("/media", "/mnt", os.path.join(home, "usb")):
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            if fname in files:
                return os.path.join(dirpath, fname)
            if dirpath.count(os.sep) - root.count(os.sep) > 5:
                _dirs[:] = []
    return None


def copy_tree_verified(src_root, dest_root, log, subdir=None,
                       exclude=()):
    """Copy a tree file-by-file, verifying size after each copy.
    Returns a manifest list of {path, size, sha256} (sha256 only for
    files < 200MB — hashing 20GB models at install time is wasteful;
    size + load-test is the check there). `exclude` names top-level
    subdirectories of the copied tree to skip entirely (used by
    step_scout_files for payloads/ + knowledge/, which have their
    own dedicated copy steps)."""
    base = os.path.join(src_root, subdir) if subdir else src_root
    manifest = []
    for dirpath, _dirs, files in os.walk(base):
        if not subdir and os.path.abspath(dirpath) == os.path.abspath(base):
            _dirs[:] = [d for d in _dirs if d not in exclude]
        for fname in files:
            src = os.path.join(dirpath, fname)
            rel = os.path.relpath(src, src_root)
            dest = os.path.join(dest_root, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            size = os.path.getsize(dest)
            if size != os.path.getsize(src):
                raise RuntimeError(f"Copy size mismatch: {rel}")
            entry = {"path": rel, "size": size}
            if size < 200_000_000:
                entry["sha256"] = _sha256(dest)
            manifest.append(entry)
            log(f"Copied+verified: {rel} ({size} bytes)")
    return manifest


def write_manifest(dest_root, manifest, log):
    path = os.path.join(dest_root, "install-manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        _json.dump({"files": manifest,
                    "build1_lessons": "INTERIM — re-check when Build 1 "
                                      "completes (EmotionEngine, EnergyVad "
                                      "80ms, AlwaysListen diagnostics, TTS "
                                      "stop counters, BCPA9 reuse, UX "
                                      "explain+confirm+feedback)."},
                   f, indent=2)
    log(f"Manifest written: {path} ({len(manifest)} files)")
    return path


def generate_systemd_units(out_dir=None, log=None):
    """Write systemd unit files as generated artifacts. Default output:
    thinkpad/systemd/ next to this script (in the build tree)."""
    log = log or (lambda msg: None)
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "systemd")
    os.makedirs(out_dir, exist_ok=True)
    home = os.path.expanduser("~")
    for name, (desc, exec_tmpl, restart) in SYSTEMD_SERVICES.items():
        unit = (
            "[Unit]\n"
            f"Description={desc}\n"
            "After=network.target sound.target\n\n"
            "[Service]\n"
            "Type=simple\n"
            f"User={os.environ.get('USER', 'scout')}\n"
            f"WorkingDirectory={home}/scout\n"
            f"ExecStart={exec_tmpl.format(home=home)}\n"
            f"Restart={restart}\n"
            "RestartSec=3\n\n"
            "[Install]\n"
            "WantedBy=multi-user.target\n")
        path = os.path.join(out_dir, f"{name}.service")
        with open(path, "w", encoding="utf-8") as f:
            f.write(unit)
        log(f"Generated unit: {path}")
    return out_dir


def _port_free(port):
    s = _socket.socket()
    try:
        s.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def run_install_self_test(scout_home=None, log=None):
    """Returns [(name, ok, needs_laptop, detail), ...]. Honest states:
    hardware/model-load checks are needs_laptop=True, never fake-passed."""
    log = log or (lambda msg: None)
    home = scout_home or os.path.join(os.path.expanduser("~"), "scout")
    results = []
    for rel in ("models", "knowledge", "install-manifest.json"):
        p = os.path.join(home, rel)
        results.append((f"scout tree: {rel}", os.path.exists(p), False,
                        p if os.path.exists(p) else "missing (install first)"))
    for port, label in ((8080, "brain"), (8081, "vision"), (8091, "name-sync")):
        results.append((f"port {port} ({label}) free-or-serving",
                        _port_free(port) or _port_in_use_by_scout(port),
                        False, "checked via bind probe"))
    for mod in ("json", "os", "shutil", "subprocess"):
        try:
            __import__(mod)
            results.append((f"python import {mod}", True, False, "ok"))
        except Exception as e:  # noqa: BLE001
            results.append((f"python import {mod}", False, False, str(e)))
    units_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "systemd")
    n_units = len([f for f in os.listdir(units_dir)
                   if f.endswith(".service")]) if os.path.isdir(units_dir) else 0
    results.append(("systemd units generated", n_units >= 5, False,
                    f"{n_units} unit files in {units_dir}"))
    results.append(("microphone present", False, True,
                    "NEEDS-LAPTOP: check with arecord -l on the ThinkPad"))
    results.append(("main model loads (llama-server /health)", False, True,
                    "NEEDS-LAPTOP: needs GPU + installed model"))
    return results


def _port_in_use_by_scout(port):
    # A bound port is fine if it is Scout already serving (post-install).
    try:
        with _socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def diagnostics():
    """Plain-language health card for the installer itself."""
    lines = ["Scout installer — diagnostics"]
    results = run_install_self_test()
    for name, ok, needs, detail in results:
        state = "OK" if ok else ("WAITS FOR LAPTOP" if needs else "NOT READY")
        lines.append(f"- {name}: {state} ({detail})")
    return "\n".join(lines)


def self_test():
    """Off-device self-test: systemd generation + manifest round-trip
    in a temp dir. Prints PASS/FAIL lines; returns True if all pass."""
    import tempfile
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    with tempfile.TemporaryDirectory(prefix="scout_installer_test_") as tmp:
        out = generate_systemd_units(out_dir=os.path.join(tmp, "systemd"))
        units = sorted(f for f in os.listdir(out) if f.endswith(".service"))
        check("systemd: 5 units generated", len(units) == 5, str(units))
        brain = open(os.path.join(out, "scout-brain.service")).read()
        check("systemd: brain unit has ExecStart + Restart",
              "ExecStart=" in brain and "Restart=" in brain)
        src = os.path.join(tmp, "usb", "scout-files")
        os.makedirs(os.path.join(src, "sub"))
        with open(os.path.join(src, "talk.py"), "w") as f:
            f.write("# talk stub\n")
        with open(os.path.join(src, "sub", "cfg.json"), "w") as f:
            f.write("{}")
        dest = os.path.join(tmp, "scout")
        manifest = copy_tree_verified(src, dest, lambda m: None)
        check("brain copy: 2 files verified", len(manifest) == 2)
        check("brain copy: sha256 recorded for small files",
              all("sha256" in e for e in manifest))
        mp = write_manifest(dest, manifest, lambda m: None)
        # Real assertion — this check used to end in `or True`, so it
        # could never fail (fixed in the 2026-10-17 dry-run audit).
        parsed_paths = {e["path"] for e in _json.load(open(mp))["files"]}
        check("manifest written + parses",
              parsed_paths == {"talk.py", os.path.join("sub", "cfg.json")},
              str(parsed_paths))
        check("port probe runs", isinstance(_port_free(59999), bool))
    print("installer self_test:", "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


# ── Entry ──
if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    if "--generate-systemd" in sys.argv:
        idx = sys.argv.index("--generate-systemd")
        target = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else None
        print("Units in:", generate_systemd_units(
            out_dir=target, log=lambda m: print(m)))
        sys.exit(0)
    root = tk.Tk()
    app = InstallerUI(root)
    root.mainloop()
