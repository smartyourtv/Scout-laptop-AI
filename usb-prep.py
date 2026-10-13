#!/usr/bin/env python3
"""
Scout Van AI — USB Preparation Tool (Windows)
Prepares the 256GB flash drive for the ThinkPad install.

This runs on your Windows home PC. It:
  1. Finds your 256GB USB drive
  2. Formats it and makes it bootable with Ubuntu 24.04
  3. Downloads all AI models (~150GB) onto it
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
    ("Vision model (Qwen3-VL)", "huggingface://...",
     "~8 GB", "God's Eye camera understanding."),
    ("Other tools & models", "various",
     "~12 GB", "Document AI, 3D, utilities."),
    # Wikipedia (100GB) and maps (50GB) download during ThinkPad install,
    # not onto the USB — keeps the USB at ~150GB on a 256GB drive.
]

STEPS = [
    ("Find USB drive",
     "Locating your 256GB flash drive.",
     "step_find_usb"),
    ("Format & partition",
     "Setting up the drive (this erases it!).",
     "step_format"),
    ("Make bootable",
     "Writing the Ubuntu installer.",
     "step_bootable"),
    ("Download models",
     "Pulling ~150GB of AI models (takes hours).",
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
        root.geometry("640x560")
        root.resizable(False, False)

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
        tk.Label(header, text="Loads the 256GB flash drive for the ThinkPad install.",
                 font=("Sans", 11), bg=bg, fg="#888888").pack(anchor="w")

        # ── Instructions ──
        instr = tk.Frame(root, bg=bg)
        instr.pack(fill="x", padx=24, pady=8)
        tk.Label(instr, font=("Sans", 10), bg=bg, fg=fg, justify="left",
                 text="Before you start:\n"
                      "• Plug in the 256GB USB flash drive\n"
                      "• Back up anything on it — it will be erased\n"
                      "• Internet connected (downloading ~150GB)\n"
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
                "the Scout Van AI installer (~150GB).\n\n"
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
    """Find the 256GB USB drive."""
    global USB_DRIVE
    # TODO: enumerate removable drives via wmic/powershell,
    # pick the ~256GB one, confirm with user.
    # Placeholder — filled at pull-it-together.
    log("TODO: USB detection — fill at pull-it-together.")
    raise RuntimeError("USB detection not yet implemented.")


def step_format(log):
    log("TODO: format — fill at pull-it-together.")


def step_bootable(log):
    log("TODO: write Ubuntu ISO — fill at pull-it-together.")


def step_downloads(log):
    log("TODO: model downloads — fill at pull-it-together.")


def step_copy_installer(log):
    log("TODO: copy scout-installer.py — fill at pull-it-together.")


def step_verify(log):
    log("TODO: verify — fill at pull-it-together.")


if __name__ == "__main__":
    root = tk.Tk()
    app = UsbPrepUI(root)
    root.mainloop()
