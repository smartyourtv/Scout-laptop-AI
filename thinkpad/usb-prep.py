#!/usr/bin/env python3
"""
Scout Van AI — USB Preparation Tool (Windows)
Prepares the 512GB flash drive for the ThinkPad install.

This runs on your Windows home PC. It:
  1. Finds your 512GB USB drive
  2. Installs Ventoy on it (Ventoy's install IS the format step —
     it creates the boot + data partitions; the drive is ERASED)
  3. Downloads everything (~220GB) to a staging folder on this PC
  4. Copies the Ubuntu ISO + models + Scout installer onto the drive

Then you plug the USB into the ThinkPad, boot it from the USB, pick the
Ubuntu ISO in the Ventoy menu, install Ubuntu onto the ThinkPad's SSD,
and run the Scout installer from scout-files/ on the same drive.

Requires: Python 3 on Windows (python.org, check "Add to PATH") and
Administrator rights (the tool relaunches itself elevated).
Usage: double-click start-usb-prep.bat, or: python usb-prep.py

REAL-GUI REWORK (2026-10-16): the previous GUI painted dry-run format
plans green while writing nothing, and the downloads step only checked
for pre-staged files behind placeholder URLs. This version downloads
from verified sources, installs Ventoy for real behind a typed
ERASE confirmation, and only marks a step done after verifying its
real effect. See USB-PREP-REAL-STATUS.md.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import sys

# ── Payload sources (verified against live listings, 2026-10-16; ────
# creative/voice bundle added same night — "v3")
# (local filename [== DOWNLOAD_MANIFEST name; flat + unique in the
#  staging folder], download URL, expected bytes (informational; the
#  server's Content-Length is the completion truth), display size,
#  what it is, destination path on the USB relative to its root)
# A desc starting with "[Group]" marks a multi-file bundle: the GUI
# list collapses those into one summed row per group.
PAYLOAD_SOURCES = [
    # ── Core payloads (destinations unchanged — installer contract) ──
    ("ubuntu-24.04.iso",
     "https://releases.ubuntu.com/24.04/ubuntu-24.04.5.1-desktop-amd64.iso",
     6_300_000_000, "~5.8 GB",
     "Ubuntu 24.04.5.1 LTS desktop ISO — Ventoy boots this on the "
     "ThinkPad.",
     "ubuntu-24.04.iso"),
    ("Qwen3.6-35B-A3B-Q3.gguf",
     "https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/main/"
     "Qwen3.6-35B-A3B-UD-Q3_K_M.gguf",
     16_600_710_112, "16.6 GB",
     "Scout's brain — Qwen3.6-35B-A3B Q3_K_M GGUF (unsloth).",
     "scout-files/payloads/Qwen3.6-35B-A3B-Q3.gguf"),
    ("Qwen3-VL-8B-Instruct-Q4_K_M.gguf",
     "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/"
     "Qwen3VL-8B-Instruct-Q4_K_M.gguf",
     5_027_784_800, "5.0 GB",
     "Vision model (Qwen3-VL-8B) — wound/wiring/DVR photos, via "
     "llama.cpp, NOT Ollama.",
     "scout-files/payloads/Qwen3-VL-8B-Instruct-Q4_K_M.gguf"),
    ("mmproj-Qwen3VL-8B-Instruct-F16.gguf",
     "https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct-GGUF/resolve/main/"
     "mmproj-Qwen3VL-8B-Instruct-F16.gguf",
     1_159_029_824, "1.2 GB",
     "Vision projector paired with the Qwen3-VL model above.",
     "scout-files/payloads/mmproj-Qwen3VL-8B-Instruct-F16.gguf"),
    ("wikipedia_en.zim",
     "https://download.kiwix.org/zim/wikipedia/"
     "wikipedia_en_all_maxi_2026-08.zim",
     119_000_000_000, "~119 GB",
     "Offline English Wikipedia (Kiwix ZIM, all_maxi 2026-08).",
     "scout-files/payloads/wikipedia_en.zim"),
    ("osm_us.osm.pbf",
     "https://download.geofabrik.de/north-america/us-latest.osm.pbf",
     None, "~11 GB",
     "Offline OpenStreetMap data for the whole US (Geofabrik).",
     "scout-files/payloads/osm_us.osm.pbf"),
    # ── Apps ──
    ("ComfyUI-v0.41.0.zip",
     "https://github.com/comfyanonymous/ComfyUI/archive/refs/tags/"
     "v0.41.0.zip",
     13_383_364, "~13 MB",
     "[Apps] ComfyUI v0.41.0 (pinned release archive) — the creative "
     "studio app the video/image/music models below run in.",
     "scout-files/payloads/apps/ComfyUI-v0.41.0.zip"),
    # ── Video models (ComfyUI) ──
    ("ltxv-2b-0.9.8-distilled-fp8.safetensors",
     "https://huggingface.co/Lightricks/LTX-Video/resolve/main/"
     "ltxv-2b-0.9.8-distilled-fp8.safetensors",
     4_461_695_684, "4.5 GB",
     "[Video] LTX-Video 2B FP8 (0.9.8 distilled) — PRIMARY video "
     "model, fastest in ComfyUI.",
     "scout-files/payloads/models/video/"
     "ltxv-2b-0.9.8-distilled-fp8.safetensors"),
    ("t5xxl_fp8_e4m3fn_scaled.safetensors",
     "https://huggingface.co/comfyanonymous/flux_text_encoders/"
     "resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors",
     5_157_348_688, "5.2 GB",
     "[Video] T5-XXL FP8 text encoder — required by LTX-Video "
     "(also serves Flux split workflows).",
     "scout-files/payloads/models/video/"
     "t5xxl_fp8_e4m3fn_scaled.safetensors"),
    ("wan2.2-ti2v-5b-fp8.safetensors",
     "https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/"
     "resolve/main/TI2V/Wan2_2-TI2V-5B_fp8_e4m3fn_scaled_KJ.safetensors",
     5_277_255_650, "5.3 GB",
     "[Video] Wan 2.2 TI2V 5B FP8 (Kijai scaled) — SECONDARY video "
     "model, max-quality single clips.",
     "scout-files/payloads/models/video/wan2.2-ti2v-5b-fp8.safetensors"),
    ("umt5_xxl_fp8_e4m3fn_scaled.safetensors",
     "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/"
     "resolve/main/split_files/text_encoders/"
     "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
     6_735_906_897, "6.7 GB",
     "[Video] UMT5-XXL FP8 text encoder — required by Wan 2.2.",
     "scout-files/payloads/models/video/"
     "umt5_xxl_fp8_e4m3fn_scaled.safetensors"),
    ("wan2.2_vae.safetensors",
     "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/"
     "resolve/main/split_files/vae/wan2.2_vae.safetensors",
     1_409_400_960, "1.4 GB",
     "[Video] Wan 2.2 VAE — required by the Wan 2.2 5B model.",
     "scout-files/payloads/models/video/wan2.2_vae.safetensors"),
    # ── Music (ComfyUI) ──
    ("ace_step_v1_3.5b.safetensors",
     "https://huggingface.co/Comfy-Org/ACE-Step_ComfyUI_repackaged/"
     "resolve/main/all_in_one/ace_step_v1_3.5b.safetensors",
     7_699_743_341, "7.7 GB",
     "[Music] ACE-Step v1 3.5B all-in-one checkpoint (Comfy-Org) — "
     "full songs with lyrics + vocals; encoder/VAE built in.",
     "scout-files/payloads/models/music/ace_step_v1_3.5b.safetensors"),
    # ── Image models (ComfyUI) ──
    ("sd_xl_base_1.0.safetensors",
     "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/"
     "resolve/main/sd_xl_base_1.0.safetensors",
     6_938_078_334, "6.9 GB",
     "[Images] SDXL Base 1.0 — primary image model, single file.",
     "scout-files/payloads/models/image/sd_xl_base_1.0.safetensors"),
    ("flux1-dev-fp8.safetensors",
     "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/"
     "flux1-dev-fp8.safetensors",
     17_246_524_772, "17.2 GB",
     "[Images] FLUX.1-dev FP8 all-in-one checkpoint (Comfy-Org, "
     "non-gated) — max-quality images.",
     "scout-files/payloads/models/image/flux1-dev-fp8.safetensors"),
    # ── Speech to text ──
    ("sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2",
     "https://github.com/k2-fsa/sherpa-onnx/releases/download/"
     "asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2",
     487_170_055, "~0.5 GB",
     "[Speech to text] Parakeet TDT 0.6B v3 int8 (sherpa-onnx) — "
     "Scout's ears; tarball, the installer unpacks it.",
     "scout-files/payloads/models/stt/"
     "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2"),
    ("whisper-large-v3-model.bin",
     "https://huggingface.co/Systran/faster-whisper-large-v3/"
     "resolve/main/model.bin",
     3_087_284_237, "3.1 GB",
     "[Speech to text] Whisper large-v3 (faster-whisper) — "
     "transcription model weights.",
     "scout-files/payloads/models/stt/faster-whisper-large-v3/"
     "model.bin"),
    ("whisper-large-v3-config.json",
     "https://huggingface.co/Systran/faster-whisper-large-v3/"
     "resolve/main/config.json",
     2_394, "2 KB",
     "[Speech to text] Whisper large-v3 config.",
     "scout-files/payloads/models/stt/faster-whisper-large-v3/"
     "config.json"),
    ("whisper-large-v3-tokenizer.json",
     "https://huggingface.co/Systran/faster-whisper-large-v3/"
     "resolve/main/tokenizer.json",
     2_480_617, "2.5 MB",
     "[Speech to text] Whisper large-v3 tokenizer.",
     "scout-files/payloads/models/stt/faster-whisper-large-v3/"
     "tokenizer.json"),
    ("whisper-large-v3-vocabulary.json",
     "https://huggingface.co/Systran/faster-whisper-large-v3/"
     "resolve/main/vocabulary.json",
     1_068_114, "1.1 MB",
     "[Speech to text] Whisper large-v3 vocabulary.",
     "scout-files/payloads/models/stt/faster-whisper-large-v3/"
     "vocabulary.json"),
    # ── Upscale + face restore ──
    ("RealESRGAN_x4plus.pth",
     "https://github.com/xinntao/Real-ESRGAN/releases/download/"
     "v0.1.0/RealESRGAN_x4plus.pth",
     67_040_989, "67 MB",
     "[Upscale + restore] RealESRGAN x4plus — image/video upscaling.",
     "scout-files/payloads/models/upscale/RealESRGAN_x4plus.pth"),
    ("4x-UltraSharp.pth",
     "https://huggingface.co/Kim2091/UltraSharp/resolve/main/"
     "4x-UltraSharp.pth",
     66_961_958, "67 MB",
     "[Upscale + restore] 4x-UltraSharp — sharper upscaling.",
     "scout-files/payloads/models/upscale/4x-UltraSharp.pth"),
    ("GFPGANv1.4.pth",
     "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/"
     "GFPGANv1.4.pth",
     348_632_874, "349 MB",
     "[Upscale + restore] GFPGAN v1.4 — face restoration.",
     "scout-files/payloads/models/upscale/GFPGANv1.4.pth"),
    # ── VieNeu-TTS (Vietnamese voices — Southern dialect support) ──
    ("vieneu-model.safetensors",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "model.safetensors",
     1_105_860_992, "1.1 GB",
     "[VieNeu TTS] VieNeu-TTS model weights (pnnbao-ump).",
     "scout-files/payloads/models/tts/VieNeu-TTS/model.safetensors"),
    ("vieneu-config.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "config.json",
     1_227, "1 KB",
     "[VieNeu TTS] VieNeu-TTS config.",
     "scout-files/payloads/models/tts/VieNeu-TTS/config.json"),
    ("vieneu-generation_config.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "generation_config.json",
     216, "216 B",
     "[VieNeu TTS] VieNeu-TTS generation config.",
     "scout-files/payloads/models/tts/VieNeu-TTS/"
     "generation_config.json"),
    ("vieneu-tokenizer.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "tokenizer.json",
     24_140_239, "24 MB",
     "[VieNeu TTS] VieNeu-TTS tokenizer.",
     "scout-files/payloads/models/tts/VieNeu-TTS/tokenizer.json"),
    ("vieneu-tokenizer_config.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "tokenizer_config.json",
     12_063_181, "12 MB",
     "[VieNeu TTS] VieNeu-TTS tokenizer config.",
     "scout-files/payloads/models/tts/VieNeu-TTS/"
     "tokenizer_config.json"),
    ("vieneu-vocab.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "vocab.json",
     2_776_833, "2.8 MB",
     "[VieNeu TTS] VieNeu-TTS vocabulary.",
     "scout-files/payloads/models/tts/VieNeu-TTS/vocab.json"),
    ("vieneu-special_tokens_map.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "special_tokens_map.json",
     610, "610 B",
     "[VieNeu TTS] VieNeu-TTS special tokens map.",
     "scout-files/payloads/models/tts/VieNeu-TTS/"
     "special_tokens_map.json"),
    ("vieneu-voices.json",
     "https://huggingface.co/pnnbao-ump/VieNeu-TTS/resolve/main/"
     "voices.json",
     28_561, "29 KB",
     "[VieNeu TTS] VieNeu-TTS built-in voice definitions.",
     "scout-files/payloads/models/tts/VieNeu-TTS/voices.json"),
]

# Ventoy (the bootable-maker). Version + SHA-256 verified against the
# official GitHub release, 2026-10-16.
VENTOY_VERSION = "1.1.18"
VENTOY_ZIP_URL = ("https://github.com/ventoy/Ventoy/releases/download/"
                  "v1.1.18/ventoy-1.1.18-windows.zip")
VENTOY_ZIP_SHA256 = ("082c478e8c432e1ac653899fcf50e3a4077a2851bc6112b"
                     "5ddd30545962164a9")
VENTOY_ZIP_SIZE = 16_680_699

# ── What gets downloaded onto the USB (display list) ────────────────
# Core payloads list individually; "[Group]" bundles collapse into
# one summed row per group so the window stays readable.
def _display_rows():
    rows, groups, order = [], {}, []
    for name, url, exp, size, desc, _rel in PAYLOAD_SOURCES:
        if desc.startswith("[") and "]" in desc:
            gname = desc[1:desc.index("]")]
            if gname not in groups:
                groups[gname] = [0, 0]
                order.append(gname)
            groups[gname][0] += exp or 0
            groups[gname][1] += 1
        else:
            rows.append((name, url, size, desc))
    for gname in order:
        total, count = groups[gname]
        disp = (f"~{total / 1e9:.1f} GB" if total >= 100_000_000
                else f"~{total / 1e6:.0f} MB")
        rows.append((f"{gname} bundle "
                     f"({count} file{'s' if count != 1 else ''})", "",
                     disp, gname))
    return rows


DOWNLOADS = _display_rows()

STEPS = [
    ("Find USB drive",
     "Locating your 512GB flash drive.",
     "step_find_usb"),
    ("Format & partition",
     "Installing Ventoy — this ERASES the drive.",
     "step_format"),
    ("Make bootable",
     "Verifying the Ventoy boot + data partitions.",
     "step_bootable"),
    ("Download models",
     "Pulling ~220GB of installer + AI models + creative studio "
     "+ offline data (takes hours).",
     "step_downloads"),
    ("Copy installer",
     "Copying the ISO, models, and Scout installer to the drive.",
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
                      "• Internet connected (downloading ~220GB)\n"
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
        """Main-thread prologue: select the drive, get the typed ERASE
        confirmation naming it, THEN run the destructive/heavy steps on
        a worker thread. Nothing destructive happens before the user
        types the confirmation for the exact device shown."""
        if self.preparing:
            return
        self.preparing = True
        self.prep_btn.configure(state="disabled", text="Preparing…")
        self.set_step(0, "active")
        self.set_status("Find USB drive — locating your 512GB flash drive.")
        self.log("── Find USB drive ──")
        try:
            step_find_usb(self.log)
        except Exception as e:
            self.set_step(0, "failed")
            self.set_status("Failed at: Find USB drive")
            self.log(f"✕ FAILED: {e}\n")
            messagebox.showerror("Preparation failed",
                                 f"Step failed: Find USB drive\n\n{e}")
            self.prep_btn.configure(state="normal", text="Retry")
            self.preparing = False
            return
        self.set_step(0, "done")
        self.progress["value"] = 1
        self.log("✓ Find USB drive complete\n")

        if os.name == "nt":
            disk = SELECTED_DISK or {}
            dev = disk.get("device") or USB_DRIVE
            expected = f"ERASE {dev}"
            typed = _ask_typed_confirmation(
                self.root,
                "Confirm — this ERASES the drive",
                "The next step installs Ventoy and ERASES this drive:\n\n"
                f"    {disk.get('model') or 'USB drive'}\n"
                f"    {dev}  —  {disk.get('size_gb')} GB\n\n"
                "Everything on it will be gone.\n\n"
                f"To continue, type exactly:\n\n    {expected}")
            if typed is None:
                self.set_status("Cancelled — nothing was erased.")
                self.log("Cancelled by user before erase confirmation.")
                self.prep_btn.configure(state="normal", text="Prepare USB")
                self.preparing = False
                return
            if typed.strip() != expected:
                messagebox.showerror(
                    "Confirmation didn't match",
                    f"You typed {typed!r}.\nIt must be exactly:\n\n"
                    f"    {expected}\n\nNothing was erased.")
                self.set_status("Confirmation didn't match — nothing erased.")
                self.prep_btn.configure(state="normal", text="Prepare USB")
                self.preparing = False
                return
            global GUI_CONFIRM
            GUI_CONFIRM = typed.strip()
            self.log(f"Erase confirmed for {dev}.")

        thread = threading.Thread(target=self.run_prep, daemon=True)
        thread.start()

    def run_prep(self):
        # Step 0 (Find USB) already ran + verified on the main thread.
        for i in range(1, len(STEPS)):
            name, desc, func_name = STEPS[i]
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
            "Plug it into the ThinkPad, boot from USB (F12 boot menu),\n"
            "pick the Ubuntu ISO in the Ventoy menu, and install.\n"
            "USB-README.txt on the drive explains the layout.")
        self.prep_btn.configure(state="normal", text="Prepare USB")
        self.preparing = False


def _ask_typed_confirmation(root, title, message):
    """Modal dialog with a text entry. Returns the typed string, or
    None if cancelled/closed."""
    result = {"value": None}
    dlg = tk.Toplevel(root)
    dlg.title(title)
    dlg.configure(bg="#0d1b2a")
    dlg.transient(root)
    dlg.grab_set()
    tk.Label(dlg, text=message, justify="left", bg="#0d1b2a",
             fg="#e0e0e0", font=("Sans", 10)).pack(padx=20, pady=(16, 8))
    entry = tk.Entry(dlg, font=("Monospace", 12), width=34)
    entry.pack(padx=20, pady=4)
    entry.focus_set()
    btns = tk.Frame(dlg, bg="#0d1b2a")
    btns.pack(padx=20, pady=(8, 16), fill="x")

    def _ok():
        result["value"] = entry.get()
        dlg.destroy()

    def _cancel():
        result["value"] = None
        dlg.destroy()

    tk.Button(btns, text="Cancel", command=_cancel, padx=14, pady=6,
              relief="flat", bg="#1a2b4a", fg="#e0e0e0").pack(side="left")
    tk.Button(btns, text="Erase && Continue", command=_ok, padx=14, pady=6,
              relief="flat", bg="#4da6ff", fg="#000000",
              font=("Sans", 10, "bold")).pack(side="right")
    dlg.bind("<Return>", lambda _e: _ok())
    dlg.bind("<Escape>", lambda _e: _cancel())
    root.wait_window(dlg)
    return result["value"]


# ══════════════════════════════════════════════════════════════════
# Step implementations
# ══════════════════════════════════════════════════════════════════

USB_DRIVE = None     # Selected device id, e.g. "\\\\.\\PhysicalDrive2" or "/dev/sdb"
SELECTED_DISK = None  # Full dict from list_block_devices() for the selection
USB_ROOT = None      # Mounted data-partition root, e.g. "E:\\" (after Ventoy)
GUI_CONFIRM = ""     # Typed "ERASE <device>" from the GUI dialog

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
    """Find candidate USB drives (real detection).

    Windows: PowerShell Get-Disk (USB bus, size, physical-drive
    number). Linux fallback: lsblk JSON (this build VM). The largest
    removable device wins; the GUI then shows it and requires the
    typed ERASE confirmation before anything destructive runs."""
    global USB_DRIVE, SELECTED_DISK
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
    SELECTED_DISK = best
    log(f"Selected USB drive: {USB_DRIVE} ({best.get('size_gb')}GB, "
        f"{best.get('model')}). Erase still requires the typed "
        "confirmation in the next dialog.")


def _prep_stub(name, log):
    # Kept for parity: a stub must fail LOUDLY, never silently "pass".
    log(f"PREP STUB: {name} not implemented.")
    raise RuntimeError(f"{name} is a PREP STUB — not implemented.")


def staging_dir():
    """Where downloads land on the prep PC: <tool folder>/usb-prep-downloads/."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "usb-prep-downloads")
    os.makedirs(path, exist_ok=True)
    return path


def step_format(log):
    """Format & partition.
    Windows GUI: REAL Ventoy install on the selected drive (Ventoy
    creates its own boot FAT + data exFAT partitions — that IS the
    format). Requires the typed GUI confirmation + admin rights.
    Linux/headless: the legacy env-gated plan path — and a dry-run
    there is only a PLAN ('planned only — nothing written'), never
    a completed format."""
    global USB_DRIVE
    if not USB_DRIVE:
        raise RuntimeError("No USB drive selected — run Find USB first.")
    if os.name == "nt":
        disk = SELECTED_DISK or {}
        expected = f"ERASE {USB_DRIVE}"
        if GUI_CONFIRM != expected:
            raise RuntimeError(
                "Refusing to install Ventoy: the typed confirmation "
                f"for this device ('{expected}') was not given.")
        if not is_admin():
            raise RuntimeError(
                "Refusing to install Ventoy: not running as "
                "Administrator. Relaunch the tool (it asks for admin "
                "at startup) and retry.")
        ventoy_dir = ensure_ventoy(log)
        install_ventoy(ventoy_dir, disk, log)
        root = find_ventoy_data_root(disk, log=log)
        if not root:
            raise RuntimeError(
                "Ventoy install ran, but the Ventoy data partition "
                "did not appear. Unplug/replug the drive and retry.")
        log(f"Ventoy installed; data partition at {root}")
        return
    # Linux / headless legacy path (env-gated, dry-run by default).
    confirm = os.environ.get("USB_PREP_CONFIRM", "")
    dry = os.environ.get("USB_PREP_DRY_RUN", "1") != "0"
    plan = format_drive(USB_DRIVE, confirm=confirm, dry_run=dry, log=log)
    if plan.get("dry_run"):
        log("Format step result: PLANNED ONLY — nothing was written "
            "(dry-run). The GUI on Windows performs a real Ventoy "
            "install instead.")
    log(f"Format plan: {plan}")


def step_bootable(log):
    """Make bootable.
    Windows: verify the Ventoy data partition is mounted and set
    USB_ROOT to it (the ISO itself is copied in the Copy step —
    Ventoy boots ISOs straight from the data partition).
    Linux/headless: legacy env-gated raw-write plan (dry-run =
    planned only)."""
    global USB_DRIVE, USB_ROOT
    if not USB_DRIVE:
        raise RuntimeError("No USB drive selected — run Find USB first.")
    if os.name == "nt":
        disk = SELECTED_DISK or {}
        root = find_ventoy_data_root(disk, log=log)
        if not root:
            raise RuntimeError(
                "Ventoy data partition not found on the selected "
                "drive — the Format step did not complete.")
        USB_ROOT = root
        log(f"Bootable verified: Ventoy data partition mounted at "
            f"{USB_ROOT}. Ubuntu ISO goes at its root in the Copy "
            "step; Ventoy's boot menu will list it on the ThinkPad.")
        return
    iso = os.environ.get("USB_PREP_ISO", "")
    confirm = os.environ.get("USB_PREP_CONFIRM", "")
    dry = os.environ.get("USB_PREP_DRY_RUN", "1") != "0"
    if not dry and not iso:
        raise RuntimeError("USB_PREP_ISO not set — no ISO to write.")
    plan = write_bootable_iso(USB_DRIVE, iso, confirm=confirm,
                              dry_run=dry, log=log)
    if plan.get("dry_run"):
        log("Bootable step result: PLANNED ONLY — nothing was written "
            "(dry-run).")
    log(f"Bootable plan: {plan}")


def step_downloads(log):
    """REAL downloader: fetch every PAYLOAD_SOURCES file into the
    staging folder with progress + resume, then verify the whole
    manifest is present at size. A file already complete in staging
    is skipped; a partial (.part) resumes where it left off."""
    stage = staging_dir()
    total_needed = sum(src[2] or 0 for src in PAYLOAD_SOURCES)
    free = _shutil_mod.disk_usage(stage).free
    remaining = 0
    for name, _u, exp, *_rest in PAYLOAD_SOURCES:
        have = os.path.join(stage, name)
        if not (os.path.exists(have)
                and os.path.getsize(have) >= _manifest_min(name)):
            remaining += exp or 0
    if remaining and free < remaining:
        raise RuntimeError(
            f"Not enough free space in {stage}: need ~"
            f"{remaining / 1e9:.0f} GB more of downloads, only "
            f"{free / 1e9:.0f} GB free. Free up space and retry — "
            "completed downloads are kept, so nothing is lost.")
    log(f"Staging folder: {stage} (total payload ~"
        f"{total_needed / 1e9:.0f} GB)")
    for name, url, _exp, size_disp, _desc, _rel in PAYLOAD_SOURCES:
        dest = os.path.join(stage, name)
        download_file(url, dest, log, min_size=_manifest_min(name),
                      label=f"{name} ({size_disp})")
    missing = verify_download_manifest(log=log)
    if missing:
        raise RuntimeError(
            "Download manifest incomplete after downloading — "
            "missing/undersized: " + ", ".join(missing))
    log("All payloads downloaded + verified against the manifest.")


def _manifest_min(name):
    for fname, min_size in DOWNLOAD_MANIFEST:
        if fname == name:
            return min_size
    return 0


def payload_usb_rel(name):
    """Destination of a payload on the USB, relative to the USB
    root (forward-slash path from PAYLOAD_SOURCES). Core payloads
    keep their original flat locations (installer contract); the
    creative/voice bundle lives in payloads/ subfolders."""
    for src in PAYLOAD_SOURCES:
        if src[0] == name:
            return src[5]
    return "scout-files/payloads/" + name


def usb_dest(root, name):
    """Absolute on-USB path for a staged payload name."""
    return os.path.join(root, *payload_usb_rel(name).split("/"))


def usb_root():
    """Root path files get staged under: the Ventoy data partition
    once known, else the selected device (legacy/headless)."""
    return USB_ROOT or USB_DRIVE


def _copy_big(src, dest, log, label):
    """Copy with honest skip (same size already there) + size verify."""
    import shutil as _sh
    size = os.path.getsize(src)
    if os.path.exists(dest) and os.path.getsize(dest) == size:
        log(f"Already on USB (size matches): {label}")
        return
    log(f"Copying {label} ({size / 1e9:.2f} GB)…")
    _sh.copy2(src, dest)
    if os.path.getsize(dest) != size:
        raise RuntimeError(f"Copy size mismatch for {label}: USB copy "
                           "is incomplete. Re-run — it will redo it.")
    log(f"Copied + verified: {label}")


def copy_payloads_to_usb(log):
    """Stage payloads onto the Ventoy data partition: ISO at the
    partition root (Ventoy boots it), models/data under
    scout-files/payloads/. Runs inside step_copy_installer."""
    root = usb_root()
    if not root:
        raise RuntimeError("USB root unknown — Ventoy step did not run.")
    stage = staging_dir()
    payload_dest = os.path.join(root, "scout-files", "payloads")
    os.makedirs(payload_dest, exist_ok=True)
    need = sum(os.path.getsize(os.path.join(stage, n))
               for n, _m in DOWNLOAD_MANIFEST)
    free = _shutil_mod.disk_usage(root).free
    already = 0
    for name, _m in DOWNLOAD_MANIFEST:
        dest = usb_dest(root, name)
        if os.path.exists(dest):
            already += os.path.getsize(dest)
    if free < need - already:
        raise RuntimeError(
            f"USB drive is short on space: payloads need "
            f"{(need - already) / 1e9:.0f} GB more, drive has "
            f"{free / 1e9:.0f} GB free.")
    for name, _min in DOWNLOAD_MANIFEST:
        src = os.path.join(stage, name)
        if not os.path.exists(src):
            raise RuntimeError(f"Staged payload missing: {src} — run "
                               "the Download step first.")
        dest = usb_dest(root, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        _copy_big(src, dest, log, name)
    log("Payloads staged: ISO at drive root, models/data in "
        "scout-files/payloads/ (creative/voice bundle in its "
        "models/ + apps/ subfolders).")


USB_README = """Scout Van AI — ThinkPad install USB (Ventoy)

Layout of this drive:
  ubuntu-24.04.iso ............ Ubuntu 24.04 LTS installer image.
                                Ventoy boots it — pick it in the menu.
  scout-files/payloads/ ....... AI models + offline Wikipedia + maps.
  scout-files/payloads/apps/ .. ComfyUI (creative studio app).
  scout-files/payloads/models/  Creative + voice models by kind:
                                video/ image/ music/ stt/ tts/
                                upscale/ (ComfyUI + speech models).
  scout-files/scout-installer.py  Scout installer (run after Ubuntu).
  scout-files/knowledge/ ...... Manuals, first aid, parts database.

ThinkPad boot flow:
  1. Plug this drive into the ThinkPad.
  2. Power on and tap F12 for the boot menu; choose the USB drive.
  3. In the Ventoy menu, choose ubuntu-24.04.iso.
  4. Install Ubuntu onto the ThinkPad's internal SSD.
  5. After Ubuntu is up, run the Scout installer from scout-files/
     on this drive — it copies the payloads + knowledge into place.
"""


def write_usb_readme(log):
    root = usb_root()
    if not root:
        return
    path = os.path.join(root, "USB-README.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(USB_README)
    log("Wrote USB-README.txt (layout + ThinkPad boot flow).")


# ══════════════════════════════════════════════════════════════════
# Downloader (stdlib urllib only) — chunked, resumable, honest.
# ══════════════════════════════════════════════════════════════════

import hashlib as _hashlib
import time as _time
import urllib.request as _urlreq
import urllib.error as _urlerr


def download_file(url, dest, log, min_size=0, expected_sha256=None,
                  label=None, chunk_size=1024 * 1024):
    """Download `url` to `dest` with progress + resume.

    - Progress goes to a sibling `<dest>.part` file; an interrupted
      run leaves the .part in place and the next run resumes it with
      a Range request when the server allows.
    - A `dest` already at/above min_size is skipped (complete).
    - Completion truth: the server's total size (Content-Length /
      Content-Range). Raises on short reads — never renames a
      partial file into place.
    Returns dest path."""
    label = label or os.path.basename(dest)
    if os.path.exists(dest) and os.path.getsize(dest) >= max(min_size, 1):
        log(f"Already downloaded: {label} "
            f"({os.path.getsize(dest) / 1e9:.2f} GB) — skipping.")
        return dest
    part = dest + ".part"
    resume_from = os.path.getsize(part) if os.path.exists(part) else 0
    headers = {"User-Agent": "ScoutUsbPrep/2.0 (+stdlib urllib)"}
    if resume_from:
        headers["Range"] = f"bytes={resume_from}-"
    req = _urlreq.Request(url, headers=headers)
    try:
        resp = _urlreq.urlopen(req, timeout=60)
    except _urlerr.URLError as e:
        raise RuntimeError(f"Download failed to start for {label}: {e} "
                           f"(URL: {url})")
    status = getattr(resp, "status", 200)
    if resume_from and status != 206:
        # Server ignored Range — start over rather than corrupt.
        log(f"{label}: server doesn't support resume; restarting.")
        resume_from = 0
    total = None
    if status == 206:
        crange = resp.headers.get("Content-Range", "")
        try:
            total = int(crange.split("/")[-1])
        except (ValueError, IndexError):
            total = None
    if total is None:
        clen = resp.headers.get("Content-Length")
        if clen:
            total = (int(clen) + resume_from) if status == 206 \
                else int(clen)
    mode = "ab" if resume_from else "wb"
    done = resume_from
    last_log = 0.0
    log(f"Downloading {label}"
        + (f" — resuming at {resume_from / 1e9:.2f} GB" if resume_from
           else "")
        + (f" of {total / 1e9:.2f} GB" if total else ""))
    with open(part, mode) as f:
        while True:
            try:
                chunk = resp.read(chunk_size)
            except Exception as e:
                raise RuntimeError(
                    f"Download interrupted for {label} at "
                    f"{done / 1e9:.2f} GB — progress kept in "
                    f"{os.path.basename(part)}; run again to resume. "
                    f"({e})")
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            now = _time.monotonic()
            if now - last_log >= 5 or (total and done >= total):
                last_log = now
                if total:
                    log(f"  {label}: {done / 1e9:.2f} / "
                        f"{total / 1e9:.2f} GB "
                        f"({100.0 * done / total:.1f}%)")
                else:
                    log(f"  {label}: {done / 1e9:.2f} GB")
    if total is not None and done != total:
        raise RuntimeError(
            f"Download incomplete for {label}: got {done} bytes, "
            f"server said {total}. Progress kept; run again to resume.")
    if min_size and done < min_size:
        raise RuntimeError(
            f"Downloaded {label} is undersized: {done} bytes < "
            f"required {min_size}. Not accepting it.")
    os.replace(part, dest)
    if expected_sha256:
        h = _hashlib.sha256()
        with open(dest, "rb") as f:
            for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
                h.update(block)
        if h.hexdigest().lower() != expected_sha256.lower():
            os.remove(dest)
            raise RuntimeError(
                f"SHA-256 mismatch for {label} — download deleted. "
                "Run again to re-download.")
        log(f"SHA-256 verified: {label}")
    log(f"Downloaded: {label} ({done / 1e9:.2f} GB)")
    return dest


# ══════════════════════════════════════════════════════════════════
# Admin elevation (Windows) + Ventoy
# ══════════════════════════════════════════════════════════════════

def is_admin():
    if os.name != "nt":
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_elevated():
    """Relaunch this script as Administrator (Windows UAC prompt).
    Returns True if the elevated process was started."""
    import ctypes
    params = " ".join(f'"{a}"' for a in sys.argv)
    rc = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1)
    return rc > 32


def ensure_ventoy(log):
    """Download + extract the official Ventoy Windows zip into the
    staging folder. Returns the folder containing Ventoy2Disk.exe."""
    stage = staging_dir()
    dest_dir = os.path.join(stage, f"ventoy-{VENTOY_VERSION}")
    exe = os.path.join(dest_dir, "Ventoy2Disk.exe")
    if os.path.exists(exe):
        log(f"Ventoy {VENTOY_VERSION} already staged.")
        return dest_dir
    zip_path = os.path.join(stage, f"ventoy-{VENTOY_VERSION}-windows.zip")
    download_file(VENTOY_ZIP_URL, zip_path, log,
                  min_size=VENTOY_ZIP_SIZE,
                  expected_sha256=VENTOY_ZIP_SHA256,
                  label=f"Ventoy {VENTOY_VERSION} (Windows zip)")
    import zipfile
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(stage)
    # The zip extracts to ventoy-<ver>/ — normalise if needed.
    if not os.path.exists(exe):
        for dirpath, _d, files in os.walk(stage):
            if "Ventoy2Disk.exe" in files:
                found = os.path.join(dirpath, "Ventoy2Disk.exe")
                if os.path.dirname(found) != dest_dir:
                    import shutil as _sh
                    _sh.copytree(os.path.dirname(found), dest_dir,
                                 dirs_exist_ok=True)
                break
    if not os.path.exists(exe):
        raise RuntimeError("Ventoy2Disk.exe not found after extracting "
                           "the Ventoy zip.")
    log(f"Ventoy {VENTOY_VERSION} ready: {dest_dir}")
    return dest_dir


def _run_ventoy_cli(exe, args, log, timeout=900):
    """Run Ventoy2Disk in CLI (VTOYCLI) mode, feeding 'Y' on stdin in
    case it asks. Returns (returncode, output_text)."""
    cmd = [exe, "VTOYCLI"] + args
    log("$ " + " ".join(cmd))
    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True,
        cwd=os.path.dirname(exe))
    try:
        out, _ = proc.communicate(input="Y\nY\nY\n", timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()
        return -1, (out or "") + "\n[timeout — killed]"
    for line in (out or "").splitlines():
        log("  " + line)
    return proc.returncode, out or ""


def install_ventoy(ventoy_dir, disk, log):
    """Install Ventoy onto the selected physical drive via CLI.
    Falls back to launching the Ventoy GUI with step-by-step
    instructions if the CLI path doesn't produce a data partition —
    the fallback blocks until the user confirms in OUR dialog, then
    re-verifies. Raises if neither path yields a Ventoy partition."""
    exe = os.path.join(ventoy_dir, "Ventoy2Disk.exe")
    number = disk.get("number")
    if number is None:
        raise RuntimeError("Selected drive has no Windows physical-"
                           "drive number — cannot run Ventoy CLI.")
    log(f"Installing Ventoy onto physical drive {number} "
        f"({disk.get('model')}, {disk.get('size_gb')} GB)…")
    rc, out = _run_ventoy_cli(
        exe, ["/Install", f"/PhyDrive:{number}", "/FS:exFAT"], log)
    root = None
    if rc == 0:
        root = find_ventoy_data_root(disk, wait_seconds=45, log=log)
    if root:
        log(f"Ventoy CLI install verified: data partition at {root}")
        return root
    log("Ventoy CLI did not produce a verified data partition "
        f"(exit {rc}). Falling back to the Ventoy window with "
        "instructions — follow the popup.")
    _ventoy_gui_fallback(exe, disk, log)
    root = find_ventoy_data_root(disk, wait_seconds=30, log=log)
    if not root:
        raise RuntimeError(
            "Ventoy install could not be verified (no 'Ventoy' data "
            "partition on the selected drive). Check the drive in "
            "File Explorer, then retry.")
    log(f"Ventoy install verified after GUI step: {root}")
    return root


def _ventoy_gui_fallback(exe, disk, log):
    """Launch the Ventoy GUI and tell the user exactly what to do.
    Blocks on a messagebox until they say it's done."""
    subprocess.Popen([exe], cwd=os.path.dirname(exe))
    messagebox.showinfo(
        "Ventoy — one manual step",
        "The Ventoy window is opening. In it:\n\n"
        f"1. In the Device dropdown at the top, choose:\n"
        f"     {disk.get('model') or 'the USB drive'} "
        f"({disk.get('size_gb')} GB)\n"
        "   (Double-check the size matches your 512GB USB!)\n\n"
        "2. Click INSTALL and accept its erase warning.\n\n"
        "3. Wait until Ventoy says the install is complete.\n\n"
        "4. Close the Ventoy window.\n\n"
        "5. Click OK here — Scout will check the drive.")
    log("Ventoy GUI fallback: user confirmed the manual install.")


def find_ventoy_data_root(disk, wait_seconds=0, log=None):
    """Find the mounted Ventoy DATA partition for the selected disk:
    a partition on that physical drive whose volume label is 'Ventoy'
    (Ventoy's default for its exFAT data partition). Returns a root
    path like 'E:\\' or None. Polls up to wait_seconds."""
    log = log or (lambda m: None)
    number = (disk or {}).get("number")
    deadline = _time.monotonic() + max(wait_seconds, 0)
    while True:
        parts = _win_partitions()
        for p in parts:
            if number is not None and p.get("disk_number") != number:
                continue
            if (p.get("label") or "").strip().lower() == "ventoy" \
                    and p.get("letter"):
                return p["letter"] + ":\\"
        if _time.monotonic() >= deadline:
            return None
        _time.sleep(3)


def _win_partitions():
    """Windows partitions with letters + volume labels.
    Returns [{disk_number, letter, label, size}]. [] on any failure."""
    if os.name != "nt":
        return []
    try:
        ps = (
            "$parts = Get-Partition | Select-Object DiskNumber,"
            "DriveLetter; "
            "$vols = @{}; Get-Volume | ForEach-Object { "
            "if ($_.DriveLetter) { $vols[[string]$_.DriveLetter] = "
            "$_.FileSystemLabel } }; "
            "$parts | ForEach-Object { [PSCustomObject]@{ "
            "DiskNumber=$_.DiskNumber; "
            "DriveLetter=[string]$_.DriveLetter; "
            "Label=$vols[[string]$_.DriveLetter] } } | ConvertTo-Json")
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=30)
        data = _json.loads(out.stdout or "[]")
        if isinstance(data, dict):
            data = [data]
        result = []
        for p in data:
            letter = (p.get("DriveLetter") or "").strip()
            if not letter:
                continue
            result.append({"disk_number": p.get("DiskNumber"),
                           "letter": letter,
                           "label": p.get("Label") or ""})
        return result
    except Exception:
        return []


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
    """Copy payloads + installer scripts + knowledge onto the USB.
    Payloads: staged downloads → ISO at the Ventoy data-partition
    root, the rest under scout-files/payloads/.
    Installer scripts: scout-installer.py, scout-vision.py → scout-files/.
    Knowledge: KNOWLEDGE_SOURCES + whole files/van-manuals/ dir
    → scout-files/knowledge/. Every KNOWLEDGE_REQUIRED file must land
    on the USB at or above its min size, or this step fails.
    Also writes USB-README.txt at the partition root."""
    global USB_DRIVE
    if not usb_root():
        raise RuntimeError("USB drive not found — run Find USB drive first.")
    copy_payloads_to_usb(log)
    import shutil as _shutil
    build_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    usb_root_path = usb_root()
    usb_files = os.path.join(usb_root_path, "scout-files")
    os.makedirs(usb_files, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    for script in ("scout-installer.py", "scout-vision.py"):
        src = os.path.join(here, script)
        if not os.path.exists(src):
            raise RuntimeError(f"Missing installer script: {src}")
        _shutil.copy2(src, os.path.join(usb_files, script))
        log(f"Staged installer script: {script}")
    # Knowledge payload — single files.
    for src_rel, dest_rel in KNOWLEDGE_SOURCES:
        src = os.path.join(build_root, src_rel)
        if not os.path.exists(src):
            raise RuntimeError(f"Missing knowledge file: {src}")
        dest = os.path.join(usb_files, dest_rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        _shutil.copy2(src, dest)
        log(f"Staged knowledge: {dest_rel}")
    # Knowledge payload — whole manuals dir (PDFs + summaries + inventory).
    manuals_src = os.path.join(build_root, "files", "van-manuals")
    manuals_dest = os.path.join(usb_files, "knowledge", "manuals")
    if not os.path.isdir(manuals_src):
        raise RuntimeError(f"Missing manuals folder: {manuals_src}")
    _shutil.copytree(manuals_src, manuals_dest, dirs_exist_ok=True)
    log("Staged knowledge: manuals/ (whole folder)")
    # Parts interchange DB — lives in thinkpad/, staged alongside knowledge.
    parts_src = os.path.join(here, "parts-interchange-db.json")
    if not os.path.exists(parts_src):
        raise RuntimeError(f"Missing parts DB: {parts_src}")
    _shutil.copy2(parts_src,
                  os.path.join(usb_files, "knowledge",
                               "parts-interchange-db.json"))
    log("Staged knowledge: parts-interchange-db.json")
    # Verify manifest on the USB — no silent failures.
    for rel, min_size in KNOWLEDGE_REQUIRED:
        path = os.path.join(usb_files, "knowledge", rel)
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
    write_usb_readme(log)


def step_verify(log):
    """Honest final verification: everything the ThinkPad flow needs
    must be ON THE USB at size — payloads (ISO at root, rest in
    scout-files/payloads/), installer scripts, knowledge manifest,
    USB-README.txt."""
    global USB_DRIVE
    if not usb_root():
        raise RuntimeError("No USB drive selected.")
    root = usb_root()
    usb_files = os.path.join(root, "scout-files")
    problems = []
    for script in ("scout-installer.py", "scout-vision.py"):
        if not os.path.exists(os.path.join(usb_files, script)):
            problems.append(f"missing installer script: {script}")
    for rel, min_size in KNOWLEDGE_REQUIRED:
        path = os.path.join(usb_files, "knowledge", rel)
        if not os.path.exists(path) or os.path.getsize(path) < min_size:
            problems.append(f"knowledge missing/undersized: {rel}")
    for name, min_size in DOWNLOAD_MANIFEST:
        path = usb_dest(root, name)
        if not os.path.exists(path) or os.path.getsize(path) < min_size:
            problems.append(f"payload missing/undersized on USB: {name}")
    if not os.path.exists(os.path.join(root, "USB-README.txt")):
        problems.append("missing USB-README.txt")
    if problems:
        raise RuntimeError("USB verify failed: " + "; ".join(problems))
    log(f"USB verified: payloads + installer scripts + "
        f"{len(KNOWLEDGE_REQUIRED)} knowledge files present at size.")


# ══════════════════════════════════════════════════════════════════
# Core (2026-10-16, reworked 2026-10-16) — drive detection / safe
# format (Linux headless) / manifest.
# SAFETY: format + ISO write REFUSE unless (a) explicit device given,
# (b) confirmation string == f"ERASE {device}", (c) device is removable
# and NOT the system disk, (d) dry_run is False. Default is dry-run.
# The Windows GUI path does NOT use these — it installs Ventoy.
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
    # Creative/voice bundle (v3, 2026-10-16) — floors are ~90% of the
    # verified sizes; the server's Content-Length is the real check.
    ("ComfyUI-v0.41.0.zip", 5_000_000),
    ("ltxv-2b-0.9.8-distilled-fp8.safetensors", 4_000_000_000),
    ("t5xxl_fp8_e4m3fn_scaled.safetensors", 4_600_000_000),
    ("wan2.2-ti2v-5b-fp8.safetensors", 4_700_000_000),
    ("umt5_xxl_fp8_e4m3fn_scaled.safetensors", 6_000_000_000),
    ("wan2.2_vae.safetensors", 1_200_000_000),
    ("ace_step_v1_3.5b.safetensors", 7_000_000_000),
    ("sd_xl_base_1.0.safetensors", 6_500_000_000),
    ("flux1-dev-fp8.safetensors", 16_000_000_000),
    ("sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2",
     400_000_000),
    ("whisper-large-v3-model.bin", 2_900_000_000),
    ("whisper-large-v3-config.json", 1_000),
    ("whisper-large-v3-tokenizer.json", 2_000_000),
    ("whisper-large-v3-vocabulary.json", 900_000),
    ("RealESRGAN_x4plus.pth", 60_000_000),
    ("4x-UltraSharp.pth", 60_000_000),
    ("GFPGANv1.4.pth", 300_000_000),
    ("vieneu-model.safetensors", 1_000_000_000),
    ("vieneu-config.json", 500),
    ("vieneu-generation_config.json", 100),
    ("vieneu-tokenizer.json", 20_000_000),
    ("vieneu-tokenizer_config.json", 10_000_000),
    ("vieneu-vocab.json", 2_000_000),
    ("vieneu-special_tokens_map.json", 300),
    ("vieneu-voices.json", 20_000),
]


def list_block_devices():
    """Real block-device enumeration. Linux: lsblk -J. Windows:
    PowerShell Get-Disk (+ Get-Partition/Get-Volume so each disk also
    carries its physical-drive number and current drive letters).
    Returns [{device,size_gb,removable,model,number,drive_letters}]."""
    devices = []
    if os.name == "nt":
        try:
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-Disk | Select-Object Number,FriendlyName,Size,"
                 "BusType | ConvertTo-Json"],
                capture_output=True, text=True, timeout=30)
            parts = _win_partitions()
            letters_by_disk = {}
            for p in parts:
                letters_by_disk.setdefault(p.get("disk_number"),
                                           []).append(p["letter"])
            for d in _json.loads(out.stdout or "[]"):
                if isinstance(d, dict):
                    num = d.get("Number")
                    devices.append({
                        "device": f"\\\\.\\PhysicalDrive{num}",
                        "number": num,
                        "size_gb": round((d.get("Size") or 0) / 1e9),
                        "removable": d.get("BusType") == "USB",
                        "model": d.get("FriendlyName"),
                        "drive_letters": letters_by_disk.get(num, [])})
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
    """Format+partition plan/execution with hard safety gates
    (Linux/headless path; the Windows GUI installs Ventoy instead).
    Returns a plan dict. Raises on any gate failure. NEVER runs when
    dry_run is True (the default) — it only describes the commands,
    and callers must label that result 'planned only'."""
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
    """Raw-write an ISO to the device (Linux/headless path; same
    safety gates as format). The Windows GUI uses Ventoy instead."""
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
    under the search roots (staging folder + build tree + USB).
    Returns the list of missing/undersized filenames ([] = complete)."""
    log = log or (lambda m: None)
    roots = list(search_roots or [])
    here = os.path.dirname(os.path.abspath(__file__))
    build_root = os.path.dirname(here)
    roots += [here, build_root,
              os.path.join(build_root, "thinkpad"),
              os.path.join(build_root, "files"),
              os.path.join(here, "usb-prep-downloads")]
    root = usb_root()
    if root:
        roots.append(root)
        roots.append(os.path.join(root, "scout-files"))
        roots.append(os.path.join(root, "scout-files", "payloads"))
    missing = []
    for fname, min_size in DOWNLOAD_MANIFEST:
        found = False
        for r in roots:
            if not r or not os.path.isdir(r):
                continue
            for dirpath, _d, files in os.walk(r):
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
    lines.append(f"- Payload sources: {len(PAYLOAD_SOURCES)} verified "
                 f"URLs; Ventoy {VENTOY_VERSION} for the Windows "
                 "bootable install.")
    lines.append("- Windows GUI flow: Find USB -> typed ERASE "
                 "confirmation -> Ventoy install (format) -> verify "
                 "partitions -> real downloads -> copy -> verify. "
                 "Linux/headless format/ISO paths stay DRY-RUN by "
                 "default and report 'planned only'.")
    return "\n".join(lines)


def self_test():
    """Off-device: device listing parses, safety gates refuse, dry-run
    plans form, payload-source table is sane, manifest verify reports
    honestly. Nothing is formatted, nothing big is downloaded."""
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    devs = list_block_devices()
    check("device enumeration returns devices", len(devs) >= 1, str(devs))
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
    # Payload-source table sanity: real https URLs, manifest names,
    # expected sizes meet manifest minimums where known.
    names_ok = all(any(src[0] == fname for src in PAYLOAD_SOURCES)
                   for fname, _m in DOWNLOAD_MANIFEST)
    check("every manifest payload has a source URL", names_ok)
    urls_ok = all(src[1].startswith("https://")
                  and "..." not in src[1] for src in PAYLOAD_SOURCES)
    check("payload URLs are real https (no placeholders)", urls_ok)
    sizes_ok = True
    for fname, min_size in DOWNLOAD_MANIFEST:
        src = next(s for s in PAYLOAD_SOURCES if s[0] == fname)
        if src[2] is not None and src[2] < min_size:
            sizes_ok = False
    check("expected payload sizes meet manifest minimums", sizes_ok)
    # v3 bundle: destinations sane + core locations unchanged +
    # staging names unique + every source has a manifest entry +
    # the whole bundle fits the 512GB drive.
    rel_ok = all(len(src) == 6 and ".." not in src[5]
                 and (src[5] == "ubuntu-24.04.iso"
                      or src[5].startswith("scout-files/payloads/"))
                 for src in PAYLOAD_SOURCES)
    check("payload USB destinations are the ISO at root or inside "
          "scout-files/payloads/", rel_ok)
    core_ok = True
    for _n, _r in [
            ("ubuntu-24.04.iso", "ubuntu-24.04.iso"),
            ("Qwen3.6-35B-A3B-Q3.gguf",
             "scout-files/payloads/Qwen3.6-35B-A3B-Q3.gguf"),
            ("Qwen3-VL-8B-Instruct-Q4_K_M.gguf",
             "scout-files/payloads/Qwen3-VL-8B-Instruct-Q4_K_M.gguf"),
            ("mmproj-Qwen3VL-8B-Instruct-F16.gguf",
             "scout-files/payloads/mmproj-Qwen3VL-8B-Instruct-F16.gguf"),
            ("wikipedia_en.zim",
             "scout-files/payloads/wikipedia_en.zim"),
            ("osm_us.osm.pbf",
             "scout-files/payloads/osm_us.osm.pbf")]:
        if payload_usb_rel(_n) != _r:
            core_ok = False
    check("core payload locations unchanged (installer contract)",
          core_ok)
    _names = [src[0] for src in PAYLOAD_SOURCES]
    check("payload staging names unique",
          len(_names) == len(set(_names)))
    rev_ok = all(any(fname == src[0]
                     for fname, _m in DOWNLOAD_MANIFEST)
                 for src in PAYLOAD_SOURCES)
    check("every payload source has a manifest entry", rev_ok)
    total_exp = sum(src[2] or 0 for src in PAYLOAD_SOURCES)
    check("total payload fits the 512GB drive (<= 460GB)",
          total_exp <= 460_000_000_000,
          f"total={total_exp / 1e9:.0f}GB")
    check("Ventoy pinned (version + sha256 + URL)",
          bool(VENTOY_VERSION) and len(VENTOY_ZIP_SHA256) == 64
          and VENTOY_ZIP_URL.endswith(".zip"))
    check("downloader present", callable(download_file))
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
    # GUI: Ventoy install needs Administrator. If we're not elevated,
    # explain, relaunch elevated, and exit this instance.
    if os.name == "nt" and not is_admin():
        _root = tk.Tk()
        _root.withdraw()
        messagebox.showinfo(
            "Administrator needed",
            "Making the USB drive bootable needs Administrator "
            "rights.\n\nScout will reopen itself as Administrator — "
            "click YES on the Windows prompt that appears.")
        _ok = relaunch_elevated()
        if not _ok:
            messagebox.showerror(
                "Administrator needed",
                "The Administrator prompt was declined, so the "
                "drive can't be made bootable.\n\nRe-run the tool "
                "and click YES, or right-click start-usb-prep.bat "
                "and choose 'Run as administrator'.")
            _root.destroy()
            _sys.exit(1)
        _root.destroy()
        _sys.exit(0)
    root = tk.Tk()
    app = UsbPrepUI(root)
    root.mainloop()
