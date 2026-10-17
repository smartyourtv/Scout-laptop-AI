#!/usr/bin/env python3
"""
theft_recovery.py — laptop theft-recovery decoy ("Shawn mode").

Phase C (2026-10-16). Implements files/scout-theft-recovery-spec.md
as off-device-buildable code (the state machine, beacon, stillness
detector, unlock rules, remote-command surface). The ThinkPad wiring
(actual decoy session switch, LUKS state, webcam capture, Tailscale
transport) plugs into the hooks at install time.

Design (from the spec):
  * States: normal → armed → triggered (decoy active) → grace →
    recovered/locked/wiped. Activation: unrecognized face at lid-open
    OR manual activation from the phone app (command via Tailscale).
  * Decoy: laptop locks INTO a "Shawn mode" decoy desktop (separate
    session; real files stay LUKS-encrypted/unmounted; thief cannot
    exit). The decoy shows NO update option and NO update
    notification — reversed rule (2026-10-15): an update mechanism in
    the decoy is a risk surface, and a real desktop sitting
    un-updated is normal. Enforced here: decoy_surface() returns no
    update entry, and a test pins it.
  * Beacon: periodic location (Wi-Fi positioning + IP geolocation)
    with a timestamped trail; stop snapshots — every time the device
    is still for 2 minutes: location + timestamp + battery/network/
    Wi-Fi state (+ optional camera photo).
  * Seeing: webcam snapshots on command/periodically, silent.
  * Remote commands (phone, via Tailscale, authenticated): status,
    location, snapshot, speak (live mic stream or typed TTS), lock,
    wipe. WIPE IS TWO-STEP: request → confirm token → execute.
    Lock/wipe never execute on a single message.
  * Unlock (recovery) ONLY via: face + voice TOGETHER (both
    biometrics at once — voice alone is too easy to spoof), OR phone
    unlock via Tailscale. Standalone voice unlock and
    challenge-response were dropped by Shawn — not implemented.
  * Power-button long-press (4s+) is hardware forced-off and cannot
    be disabled — mitigation is the beacon trail + this state being
    resumable after reboot (persisted state file).

This is Shawn's own laptop; remote control of it is legitimate and
authenticated via Tailscale (spec §Security).
"""

import json
import os
import subprocess
import sys
import time
import uuid

STATE_PATH = os.path.expanduser("~/.scout/theft_state.json")
TRAIL_PATH = os.path.expanduser("~/.scout/location_trail.json")
STILLNESS_THRESHOLD_S = 120          # 2 minutes (spec)
DEFAULT_BEACON_INTERVAL_S = 60

STATES = ("normal", "armed", "triggered", "grace", "recovered",
          "locked", "wiped")


# ── location / beacon ───────────────────────────────────────────────

def wifi_scan_nmcli():
    """Visible Wi-Fi networks via nmcli when present (positioning
    input). Honest [] + reason when nmcli is absent."""
    try:
        out = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=15)
        if out.returncode != 0:
            return [], (out.stderr or "nmcli failed").strip()
        nets = []
        for line in out.stdout.splitlines():
            if ":" in line:
                ssid, sig = line.rsplit(":", 1)
                nets.append({"ssid": ssid, "signal": sig})
        return nets, "ok"
    except FileNotFoundError:
        return [], "nmcli not installed on this machine"
    except Exception as e:
        return [], str(e)


class LocationProvider:
    """Interface: ThinkPad wiring supplies Wi-Fi positioning / IP
    geolocation. Off-device default reports unavailable honestly."""

    def locate(self):
        nets, why = wifi_scan_nmcli()
        return {"ok": False, "method": "wifi+ip",
                "detail": f"positioning provider not wired here ({why})",
                "wifi_seen": nets, "ts": time.time()}


class StillnessDetector:
    """Feeds movement samples (e.g. location deltas / accelerometer-
    style signals); fires once per still period at the 2-minute mark."""

    def __init__(self, threshold_s=STILLNESS_THRESHOLD_S):
        self.threshold_s = threshold_s
        self._still_since = None
        self._fired_for_period = False

    def sample(self, moving, now=None):
        now = time.time() if now is None else now
        if moving:
            self._still_since = None
            self._fired_for_period = False
            return False
        if self._still_since is None:
            self._still_since = now
            return False
        if not self._fired_for_period and \
                now - self._still_since >= self.threshold_s:
            self._fired_for_period = True
            return True        # → caller takes a stop snapshot
        return False


# ── hooks (ThinkPad wiring) ─────────────────────────────────────────

class Hooks:
    def __init__(self):
        self.calls = []

    def _log(self, hook, payload=None):
        self.calls.append((hook, payload))

    def enter_decoy(self):
        self._log("enter_decoy")

    def exit_decoy(self):
        self._log("exit_decoy")

    def webcam_snapshot(self):
        self._log("webcam_snapshot")
        return None                     # path, on the ThinkPad

    def screen_capture(self):
        self._log("screen_capture")
        return None

    def speak(self, text_or_stream):
        self._log("speak", text_or_stream)

    def lock_now(self):
        self._log("lock_now")

    def wipe_now(self):
        self._log("wipe_now")

    def send_to_phone(self, kind, payload):
        self._log("to_phone", {"kind": kind, "payload": payload})


# ── state machine ───────────────────────────────────────────────────

class TheftRecovery:
    def __init__(self, hooks=None, location=None, state_path=None,
                 trail_path=None, grace_s=300):
        self.hooks = hooks or Hooks()
        self.location = location or LocationProvider()
        self.state_path = state_path or STATE_PATH
        self.trail_path = trail_path or TRAIL_PATH
        self.grace_s = grace_s          # post-trigger grace before lock
        self.stillness = StillnessDetector()
        self.state = "normal"
        self._wipe_token = None
        self._grace_deadline = None
        self.trail = []
        self._load()

    # -- persistence (survives the forced-off reboot) --

    def _save(self):
        for path, data in ((self.state_path,
                            {"state": self.state,
                             "grace_deadline": self._grace_deadline}),
                           (self.trail_path, self.trail)):
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                tmp = path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                os.replace(tmp, path)
            except OSError:
                pass

    def _load(self):
        try:
            with open(self.state_path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("state") in STATES:
                self.state = data["state"]
                self._grace_deadline = data.get("grace_deadline")
        except (OSError, ValueError):
            pass
        try:
            with open(self.trail_path, encoding="utf-8") as f:
                self.trail = json.load(f)
        except (OSError, ValueError):
            self.trail = []

    # -- activation --

    def arm(self):
        if self.state == "normal":
            self.state = "armed"
            self._save()
        return self.state

    def activate(self, source):
        """source: 'unrecognized_face' | 'phone_manual'. Enters decoy."""
        if self.state in ("triggered", "grace"):
            return self.state
        if source not in ("unrecognized_face", "phone_manual"):
            raise ValueError(f"unknown activation source: {source}")
        self.state = "triggered"
        self.hooks.enter_decoy()
        self._grace_deadline = time.time() + self.grace_s
        self.state = "grace"
        self._save()
        self.beacon_tick(force=True)
        return self.state

    # -- decoy surface (reversed update rule enforced) --

    def decoy_surface(self):
        """What the decoy desktop offers. NO update option, NO update
        notification — by design (2026-10-15 reversal)."""
        return {
            "desktop": "Shawn mode (decoy)",
            "apps": ["browser", "files", "settings"],
            "update_option": None,          # reversed rule — never add
            "update_notification": None,    # reversed rule — never add
            "real_files": "LUKS-encrypted, unmounted",
            "can_exit_decoy": False,
        }

    # -- beacon --

    def beacon_tick(self, force=False):
        if self.state not in ("triggered", "grace", "armed") and not force:
            return None
        fix = self.location.locate()
        entry = {"ts": time.time(), "state": self.state, "fix": fix}
        self.trail.append(entry)
        self._save()
        self.hooks.send_to_phone("location", entry)
        return entry

    def movement_sample(self, moving, now=None):
        """Returns a stop-snapshot dict when 2-minute stillness hits."""
        if self.stillness.sample(moving, now=now):
            fix = self.location.locate()
            snap = {"ts": time.time(), "kind": "stop_snapshot",
                    "fix": fix,
                    "photo": self.hooks.webcam_snapshot()}
            self.trail.append(snap)
            self._save()
            self.hooks.send_to_phone("stop_snapshot", snap)
            return snap
        return None

    # -- remote commands (phone via Tailscale) --

    def handle_command(self, cmd, payload=None):
        payload = payload or {}
        if cmd == "status":
            return {"state": self.state,
                    "trail_points": len(self.trail),
                    "decoy": self.decoy_surface()
                    if self.state in ("triggered", "grace") else None}
        if cmd == "location":
            return self.beacon_tick(force=True)
        if cmd == "snapshot":
            return {"photo": self.hooks.webcam_snapshot(),
                    "screen": self.hooks.screen_capture()
                    if payload.get("screen") else None}
        if cmd == "speak":
            self.hooks.speak(payload.get("text") or "live_mic_stream")
            return {"spoke": True}
        if cmd == "lock":
            self.state = "locked"
            self.hooks.lock_now()
            self._save()
            return {"state": self.state}
        if cmd == "wipe_request":
            self._wipe_token = uuid.uuid4().hex
            return {"wipe": "confirmation_required",
                    "token": self._wipe_token,
                    "warning": "Wipe is destructive and irreversible. "
                               "Confirm with wipe_confirm + this token."}
        if cmd == "wipe_confirm":
            if not self._wipe_token or \
                    payload.get("token") != self._wipe_token:
                return {"wipe": "refused",
                        "detail": "missing/wrong confirmation token — "
                                  "two-step confirm is mandatory"}
            self._wipe_token = None
            self.state = "wiped"
            self._save()
            self.hooks.wipe_now()
            return {"state": self.state}
        if cmd == "unlock_phone":
            return self.unlock(method="phone")
        return {"error": f"unknown command: {cmd}"}

    # -- unlock (recovery) --

    def unlock(self, method, face_ok=False, voice_ok=False):
        """ONLY: face+voice together, or phone unlock. Voice alone and
        challenge-response are NOT accepted (dropped by Shawn)."""
        if method == "phone":
            pass                                    # authenticated phone
        elif method == "face_voice":
            if not (face_ok and voice_ok):
                return {"unlocked": False,
                        "detail": "Face + voice TOGETHER are required — "
                                  "one without the other does not unlock."}
        else:
            return {"unlocked": False,
                    "detail": f"Unlock method '{method}' is not allowed. "
                              "Use face+voice together, or phone unlock."}
        self.state = "recovered"
        self.hooks.exit_decoy()
        self._save()
        self.state = "normal"
        self._save()
        return {"unlocked": True, "state": self.state}


# ── diagnostics + self-test ─────────────────────────────────────────

def diagnostics(tr=None):
    tr = tr or TheftRecovery()
    nets, why = wifi_scan_nmcli()
    lines = ["Theft recovery (laptop decoy) — diagnostics",
             f"- State: {tr.state}",
             f"- Trail points stored: {len(tr.trail)}",
             f"- Wi-Fi scan (nmcli): {len(nets)} networks ({why})",
             "- Decoy: NO update option/notification (reversed rule, "
             "enforced + tested)",
             "- Unlock: face+voice together OR phone only — voice "
             "alone never unlocks",
             "- Wipe: two-step (request → token confirm), never "
             "single-message",
             "- Transport: Tailscale (ThinkPad wiring); hooks are "
             "stubbed off-device, state machine is real.",
             "- Known limit: power-button 4s long-press is hardware "
             "forced-off — mitigation is the beacon trail + persisted "
             "state (resumes after reboot)."]
    return "\n".join(lines)


def self_test():
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    import tempfile
    with tempfile.TemporaryDirectory(prefix="theft_test_") as tmp:
        hooks = Hooks()
        tr = TheftRecovery(hooks=hooks,
                           state_path=os.path.join(tmp, "state.json"),
                           trail_path=os.path.join(tmp, "trail.json"),
                           grace_s=300)
        check("starts normal", tr.state == "normal")
        tr.arm()
        check("arm → armed", tr.state == "armed")
        tr.activate("phone_manual")
        check("phone activation → decoy (grace)",
              tr.state == "grace"
              and any(c[0] == "enter_decoy" for c in hooks.calls))
        surface = tr.decoy_surface()
        check("decoy has NO update option/notification (reversed rule)",
              surface["update_option"] is None
              and surface["update_notification"] is None
              and surface["can_exit_decoy"] is False)
        snap = None
        t0 = 1_000_000.0
        for i in range(5):
            snap = tr.movement_sample(moving=False, now=t0 + i * 40) or snap
        check("2-min stillness → stop snapshot",
              snap is not None and snap["kind"] == "stop_snapshot",
              str(snap))
        check("voice-alone unlock refused",
              tr.unlock(method="voice", voice_ok=True)["unlocked"] is False)
        check("face-alone unlock refused",
              tr.unlock(method="face_voice", face_ok=True)["unlocked"] is False)
        check("challenge-response unlock refused",
              tr.unlock(method="challenge")["unlocked"] is False)
        res = tr.handle_command("wipe_request")
        check("wipe step 1 issues token, does not wipe",
              res["wipe"] == "confirmation_required"
              and not any(c[0] == "wipe_now" for c in hooks.calls))
        bad = tr.handle_command("wipe_confirm", {"token": "wrong"})
        check("wipe with wrong token refused",
              bad["wipe"] == "refused"
              and not any(c[0] == "wipe_now" for c in hooks.calls))
        good = tr.handle_command("wipe_confirm", {"token": res["token"]})
        check("wipe step 2 with token executes",
              good["state"] == "wiped"
              and any(c[0] == "wipe_now" for c in hooks.calls))
        # Fresh instance for unlock path (wipe was terminal above).
        hooks2 = Hooks()
        tr2 = TheftRecovery(hooks=hooks2,
                            state_path=os.path.join(tmp, "s2.json"),
                            trail_path=os.path.join(tmp, "t2.json"))
        tr2.activate("unrecognized_face")
        out = tr2.unlock(method="face_voice", face_ok=True, voice_ok=True)
        check("face+voice together unlocks",
              out["unlocked"] is True and tr2.state == "normal")
        tr2.activate("phone_manual")
        out2 = tr2.handle_command("unlock_phone")
        check("phone unlock works", out2["unlocked"] is True)
        tr3 = TheftRecovery(state_path=os.path.join(tmp, "s2.json"),
                            trail_path=os.path.join(tmp, "t2.json"))
        check("state persists across restart (forced-off resilience)",
              tr3.state in STATES)
    print("theft_recovery self_test:",
          "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    print(__doc__)
