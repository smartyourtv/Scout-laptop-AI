#!/usr/bin/env python3
"""
scout-vision.py — on-demand vision for laptop Scout.

Model: Qwen3-VL-8B-Instruct (GGUF Q4_K_M + mmproj F16 projector),
served by llama.cpp's llama-server with --mmproj. NOT Ollama: Ollama has
a known crash bug with Qwen3-VL, and this build's serving stack is
llama.cpp (see the ThinkPad spec).

Why a swap: the ThinkPad has 16 GB VRAM. The main model (Qwen3.6-35B-A3B)
fills most of it, so the vision model cannot run alongside it. Vision
calls are rare and on-demand (a photo, a camera frame), so talk.py does:
    1. stop the main llama-server (frees VRAM)
    2. start the vision llama-server on VISION_PORT
    3. send the image + a structured prompt, get a plain description back
    4. stop the vision server, restart the main server
    5. the MAIN model (with the first-aid library / knowledge base) does
       the reasoning and speaks the answer — the vision model only
       describes what it sees, it never gives advice.

Usage from talk.py:
    from scout_vision import describe_image
    description = describe_image("/path/to/photo.jpg", WOUND_PROMPT)
    # description is plain text, e.g. "Cut on the left forearm, about 4 cm,
    # edges slightly gaping, steady oozing, no visible foreign object..."

Requires: llama-server on PATH, model files in ~/scout/models/:
    Qwen3-VL-8B-Instruct-Q4_K_M.gguf
    mmproj-Qwen3VL-8B-Instruct-F16.gguf
"""

import base64
import json
import os
import subprocess
import time
import urllib.request

HOME = os.path.expanduser("~")
MODELS_DIR = os.path.join(HOME, "scout", "models")
VISION_MODEL = os.path.join(MODELS_DIR, "Qwen3-VL-8B-Instruct-Q4_K_M.gguf")
MMPROJ = os.path.join(MODELS_DIR, "mmproj-Qwen3VL-8B-Instruct-F16.gguf")

MAIN_PORT = 8080      # main brain llama-server (talk.py's server)
VISION_PORT = 8081    # vision llama-server (this module)
MAIN_MODEL = os.path.join(MODELS_DIR, "Qwen3.6-35B-A3B-Q3.gguf")
MAIN_START_CMD = ["llama-server", "-m", MAIN_MODEL, "--port", str(MAIN_PORT)]

VISION_CTX = 4096     # plenty for one image + a short description
START_TIMEOUT = 90    # seconds to wait for a server to answer /health
REQUEST_TIMEOUT = 120

# ── Prompts ────────────────────────────────────────────────────────
# Each prompt asks for OBSERVATION ONLY. The main model reasons from it.

WOUND_PROMPT = (
    "Describe this wound in plain, factual detail for a first-aid decision. "
    "Cover exactly these points, one line each: "
    "1) body location; "
    "2) bleeding: none, oozing, steady flow, or spurting/pooling; "
    "3) size estimate; "
    "4) depth: surface scrape, gaping edges, or visible fat/tissue/bone; "
    "5) foreign object visible (dirt, gravel, embedded object) or none; "
    "6) surrounding skin: normal, redness, swelling, warmth, streaking. "
    "Do NOT diagnose, do NOT suggest treatment, do NOT say what it is. "
    "If you cannot see a wound clearly, say so."
)

WIRING_PROMPT = (
    "Describe this wiring/electrical setup in plain, factual detail. Cover: "
    "what components and wires are visible, wire colors and where each wire "
    "goes, any labels or markings you can read, and anything that looks "
    "loose, burnt, corroded, melted, or incorrectly connected. "
    "Do NOT diagnose or suggest fixes — describe only what you see. "
    "If text/labels are unclear, say which ones you could not read."
)

GENERAL_PROMPT = (
    "Describe this image in plain, factual detail: what is visible, any "
    "text or labels you can read, and anything unusual. "
    "Do NOT guess at things you cannot see."
)


# ── Server management ──────────────────────────────────────────────

def _health_ok(port):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def _wait_for_server(port, timeout=START_TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _health_ok(port):
            return True
        time.sleep(1)
    return False


def _stop_server(port):
    """Stop whatever is listening on `port` (picks the llama-server PID)."""
    try:
        out = subprocess.run(
            ["fuser", "-k", f"{port}/tcp"],
            capture_output=True, text=True, timeout=10)
        return out.returncode == 0
    except FileNotFoundError:
        return False


def _start_vision_server():
    for path in (VISION_MODEL, MMPROJ):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Vision model file missing: {path}\n"
                "Run the Scout installer (step: AI models) first.")
    cmd = [
        "llama-server",
        "-m", VISION_MODEL,
        "--mmproj", MMPROJ,
        "--port", str(VISION_PORT),
        "-c", str(VISION_CTX),
        "-ngl", "999",
        "--host", "127.0.0.1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not _wait_for_server(VISION_PORT):
        proc.terminate()
        raise RuntimeError("Vision server did not come up on port "
                           f"{VISION_PORT} within {START_TIMEOUT}s.")
    return proc


def _start_main_server():
    if _health_ok(MAIN_PORT):
        return None
    proc = subprocess.Popen(
        MAIN_START_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not _wait_for_server(MAIN_PORT):
        proc.terminate()
        raise RuntimeError("Main server did not come back up after vision.")
    return proc


# ── Image analysis ─────────────────────────────────────────────────

def _analyze_with_vision_server(image_path, prompt):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(image_path)[1].lower().lstrip(".") or "jpeg"
    if ext == "jpg":
        ext = "jpeg"
    payload = {
        "model": "qwen3-vl-8b-instruct",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/{ext};base64,{b64}"}},
            ],
        }],
        "temperature": 0.0,
        "max_tokens": 600,
    }
    req = urllib.request.Request(
        f"http://127.0.0.1:{VISION_PORT}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def describe_image(image_path, prompt=GENERAL_PROMPT):
    """
    Full swap: stop main server → vision server → describe → restore main.
    Returns the vision model's plain-text description. Raises on failure;
    always attempts to restore the main server before returning/raising.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No such image: {image_path}")
    main_was_running = _health_ok(MAIN_PORT)
    if main_was_running:
        _stop_server(MAIN_PORT)
        time.sleep(2)
    try:
        _start_vision_server()
        try:
            return _analyze_with_vision_server(image_path, prompt)
        finally:
            _stop_server(VISION_PORT)
            time.sleep(1)
    finally:
        if main_was_running:
            _start_main_server()


if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    prompt = WOUND_PROMPT if len(sys.argv) < 3 else {
        "wound": WOUND_PROMPT,
        "wiring": WIRING_PROMPT,
        "general": GENERAL_PROMPT,
    }.get(sys.argv[2], GENERAL_PROMPT)
    print(describe_image(path, prompt))
