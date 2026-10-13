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
    ("Downloading extras",
     "Fetching Wikipedia and offline maps (needs internet).",
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
        root.geometry("640x520")
        root.resizable(False, False)

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
                      "• Internet is connected (for Wikipedia + maps)\n"
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


def step_system_check(log):
    # Disk space: need ~300GB free on the target drive
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (1024 ** 3)
    log(f"Free disk: {free_gb}GB")
    if free_gb < 280:
        raise RuntimeError(
            f"Need at least 280GB free, found {free_gb}GB.")
    # TODO: check RAM, GPU during pull-it-together
    log("System check passed.")


def step_system_packages(log):
    run("sudo apt-get update", log)
    run("sudo apt-get install -y python3 python3-venv python3-pip "
        "portaudio19-dev ffmpeg git curl", log)


def step_python_env(log):
    home = os.path.expanduser("~")
    venv = os.path.join(home, "scout", "venv")
    os.makedirs(os.path.dirname(venv), exist_ok=True)
    if not os.path.exists(venv):
        run(f"python3 -m venv {venv}", log)
    # TODO: pip install list finalized at pull-it-together
    log("Python environment ready.")


def step_scout_files(log):
    # TODO: copy from USB — paths finalized at pull-it-together
    log("Scout files copied.")


def step_models(log):
    # TODO: copy models from USB — paths finalized at pull-it-together
    log("AI models in place.")


def step_downloads(log):
    # TODO: Kiwix Wikipedia + OSM maps download URLs at pull-it-together
    log("Downloads complete.")


def step_services(log):
    # TODO: systemd units for wake word, auto-start, van Wi-Fi
    log("Services configured.")


def step_self_test(log):
    # TODO: verify models load, mic works, wake word responds
    log("Self-test passed.")


# ── Entry ──
if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerUI(root)
    root.mainloop()
