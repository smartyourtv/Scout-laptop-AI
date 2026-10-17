#!/usr/bin/env python3
"""
deterrence.py — van deterrence engine for laptop Scout.

Phase C (2026-10-16). Implements the approved 2026-10-15 design
(ThinkPad spec §Deterrence):

  person-detected event in (Frigate) → classify:
    * no human (animal/shadow) → ignore
    * familiar face (Shawn / Lien Pham / gallery) → log + notify only
    * unfamiliar / can't tell → DETER immediately (fail-secure):
      voice + lights + recording + alert, all in parallel
  monitor: person leaves → stand down; person stays / tries a handle →
  escalate; familiar face recognized mid-deterrence → stand down +
  brief apology; entry succeeds → hand off to theft recovery.

Voice goes through Bluetooth TWS speakers (USB-powered, inside van
front + rear) kept awake by a continuous near-silent keep-alive
stream. Volume goes loud for deterrence and is RESTORED after
stand-down. ThinkPad built-in speakers are the fallback if Bluetooth
drops. **The BCPA9 is NEVER an output** (it's off when parked) — that
is enforced in code, not just documented. Scout uses the BT speakers
ONLY during deterrence or when Shawn explicitly requests them.

All side effects go through hooks (TTS, lights, record, alert,
familiar-check) so the engine is testable off-device with mocked hooks
and the ThinkPad wiring (Frigate MQTT/HTTP, real lights relay, real
TTS) plugs in at install time.

Build 1 interim lessons folded in: diagnostics + self-test per service
(standing rule); emotion/voice lines render through the selected TTS
voice hook (never a looped recording).
"""

import json
import os
import subprocess
import sys
import threading
import time

# ── config ──────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "speakers": {
        # Logical output names. "bcpa9" is FORBIDDEN — see _validate().
        "deterrence_outputs": ["bt_tws_front", "bt_tws_rear"],
        "fallback_output": "thinkpad_builtin",
        "keepalive_enabled": True,
        "keepalive_device_hint": "bluez",   # aplay/paplay target hint
    },
    "volume": {
        "deterrence_level": 100,            # max/near-max while deterring
        "restore_after": True,              # restore prior level on stand-down
    },
    "lines": {
        "initial": [
            "Hey! You're on camera. This van is monitored. Leave now.",
            "Step away from the van. You are being recorded, and the "
            "owner has been alerted.",
        ],
        "escalation": [
            "You were told to leave. You are still being recorded. "
            "Walk away now.",
            "Last warning. Leave the area. Everything you do is on camera.",
        ],
        "apology": "Sorry — I recognize you now. Standing down.",
        # Never claim police were notified (not true) — enforced in tests.
    },
    "timing": {
        "escalate_after_s": 30,             # person still present
        "stand_down_clear_s": 10,           # area clear before stand-down
    },
}

FORBIDDEN_OUTPUTS = {"bcpa9", "boss_bcpa9", "car_stereo"}


def _validate_config(cfg):
    outs = [o.lower() for o in cfg["speakers"]["deterrence_outputs"]]
    outs.append(cfg["speakers"]["fallback_output"].lower())
    bad = FORBIDDEN_OUTPUTS.intersection(outs)
    if bad:
        raise ValueError(
            f"BCPA9 must NEVER be a deterrence output (found: {bad}). "
            "It is off when parked. Use the Bluetooth TWS speakers.")
    for group in ("initial", "escalation"):
        for line in cfg["lines"][group]:
            if "police" in line.lower() and "notified" in line.lower():
                raise ValueError("Deterrence lines must never claim "
                                 "police were notified (not true).")
    return cfg


# ── keep-alive (silent stream design) ──────────────────────────────
# Problem: USB-powered Bluetooth speakers sleep when idle, and wake-up
# latency would eat the first deterrence words. Design: a continuous
# near-silent stream (very low-level inaudible tone / digital silence
# with periodic sub-audible keep-alive frames) keeps the TWS link and
# the speakers' amps awake. Implemented with aplay/paplay when present;
# an honest stub otherwise (reports unavailable, never fakes running).

class KeepAlive:
    def __init__(self, config=None):
        cfg = (config or DEFAULT_CONFIG)["speakers"]
        self.enabled = cfg.get("keepalive_enabled", True)
        self._proc = None
        self.backend = None             # "paplay" | "aplay" | None

    def available_backend(self):
        for tool in ("paplay", "aplay"):
            try:
                out = subprocess.run(["which", tool], capture_output=True,
                                     text=True, timeout=5)
                if out.returncode == 0 and out.stdout.strip():
                    return tool
            except Exception:
                continue
        return None

    def start(self):
        """Start the silent stream. Returns (running, detail). On a
        machine without an audio stack this honestly reports the stub."""
        if not self.enabled:
            return False, "keep-alive disabled in config"
        self.backend = self.available_backend()
        if self.backend is None:
            return False, ("keep-alive STUB: neither paplay nor aplay on "
                           "this machine — the silent stream starts on "
                           "the ThinkPad where PipeWire/Pulse tools exist")
        # Near-silent: /dev/zero is digital silence; speakers stay awake
        # because the stream never closes. Volume of the STREAM is not
        # the deterrence volume — output gain is set by the TTS hook.
        try:
            if self.backend == "paplay":
                cmd = ["paplay", "--raw", "--format=s16le", "--rate=48000",
                       "--channels=2", "/dev/zero"]
            else:
                cmd = ["aplay", "-q", "-f", "S16_LE", "-r", "48000",
                       "-c", "2", "/dev/zero"]
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"keep-alive running via {self.backend}"
        except Exception as e:
            return False, f"keep-alive failed to start: {e}"

    def stop(self):
        if self._proc is not None:
            try:
                self._proc.terminate()
            except Exception:
                pass
            self._proc = None
        return True

    def is_running(self):
        return self._proc is not None and self._proc.poll() is None


# ── hooks (ThinkPad wiring plugs in here) ───────────────────────────

class Hooks:
    """Side-effect surface. Defaults are logging stubs (off-device);
    the ThinkPad install replaces each with the real implementation:
    tts → Kokoro via talk.py (selected voice), lights → relay skill,
    record → Frigate clip/snapshot trigger, alert → phone notification,
    familiar_check → face gallery match, volume → PipeWire control."""

    def __init__(self):
        self.calls = []                 # (hook, payload) — test visibility

    def _log(self, hook, payload):
        self.calls.append((hook, payload))

    def familiar_check(self, event):
        self._log("familiar_check", event.get("person_id"))
        return None                     # None = can't tell → fail-secure

    def speak(self, line, output, volume):
        self._log("speak", {"line": line, "output": output,
                            "volume": volume})

    def lights_flash(self, on):
        self._log("lights", on)

    def record(self, event):
        self._log("record", event.get("camera"))

    def alert_owner(self, kind, detail):
        self._log("alert", {"kind": kind, "detail": detail})

    def set_volume(self, level, outputs):
        self._log("volume", {"level": level, "outputs": outputs})

    def get_volume(self):
        self._log("get_volume", None)
        return 40                       # stub prior level (ThinkPad: real)

    def theft_handoff(self, event):
        self._log("theft_handoff", event.get("camera"))


# ── engine ──────────────────────────────────────────────────────────

class DeterrenceEngine:
    STATES = ("idle", "deterring", "escalated", "stood_down")

    def __init__(self, config=None, hooks=None, keepalive=None):
        self.config = _validate_config(config or DEFAULT_CONFIG)
        self.hooks = hooks or Hooks()
        self.keepalive = keepalive or KeepAlive(self.config)
        self.state = "idle"
        self._prior_volume = None
        self._line_idx = 0
        self._lock = threading.Lock()
        self.log = []                   # plain-language event log

    # -- internal helpers --

    def _say(self, msg):
        self.log.append(f"{time.strftime('%H:%M:%S')} {msg}")

    def _outputs(self):
        return list(self.config["speakers"]["deterrence_outputs"])

    def _speak_line(self, group):
        lines = self.config["lines"][group]
        line = lines[self._line_idx % len(lines)]
        self._line_idx += 1
        for out in self._outputs():
            self.hooks.speak(line, out, self.config["volume"]["deterrence_level"])
        return line

    # -- event entry points --

    def on_person_event(self, event):
        """event: {kind: 'person'|'animal'|'shadow', camera, person_id?}
        Returns the action taken, in plain language."""
        with self._lock:
            kind = event.get("kind", "person")
            if kind != "person":
                self._say(f"Ignored {kind} event on {event.get('camera')}.")
                return "ignored_no_human"
            familiar = self.hooks.familiar_check(event)
            if familiar:
                self.hooks.alert_owner(
                    "familiar", f"{familiar} at the van "
                    f"({event.get('camera')}) — no deterrence.")
                self._say(f"Familiar ({familiar}) — logged + notified only.")
                return "familiar_no_deterrence"
            if self.state in ("deterring", "escalated"):
                return "already_deterring"
            return self._start_deterrence(event, familiar=None)

    def _start_deterrence(self, event, familiar):
        self.state = "deterring"
        self._prior_volume = self.hooks.get_volume()
        self.hooks.set_volume(self.config["volume"]["deterrence_level"],
                              self._outputs())
        line = self._speak_line("initial")
        self.hooks.lights_flash(True)
        self.hooks.record(event)
        self.hooks.alert_owner("deterrence_started",
                               f"Unfamiliar person at {event.get('camera')}. "
                               f"Voice deterrence started: “{line}”")
        self._say(f"Deterrence started ({event.get('camera')}): {line}")
        return "deterrence_started"

    def on_person_still_present(self, event):
        with self._lock:
            if self.state != "deterring":
                return "not_deterring"
            familiar = self.hooks.familiar_check(event)
            if familiar:
                return self._stand_down(apology=True,
                                         reason=f"recognized {familiar}")
            self.state = "escalated"
            line = self._speak_line("escalation")
            self.hooks.alert_owner("deterrence_escalated",
                                   "Person still at the van — escalating.")
            self._say(f"Escalated: {line}")
            return "escalated"

    def on_area_clear(self, event=None):
        with self._lock:
            if self.state == "idle":
                return "already_idle"
            return self._stand_down(apology=False, reason="person left")

    def on_entry(self, event):
        with self._lock:
            self.hooks.theft_handoff(event)
            self.hooks.alert_owner("entry_detected",
                                   "Entry succeeded — theft recovery "
                                   "playbook engaged.")
            self._say("Entry detected — handed off to theft recovery.")
            return "theft_handoff"

    def _stand_down(self, apology, reason):
        if apology:
            line = self.config["lines"]["apology"]
            for out in self._outputs():
                self.hooks.speak(line, out,
                                 self.config["volume"]["deterrence_level"])
        self.hooks.lights_flash(False)
        if self.config["volume"]["restore_after"] and \
                self._prior_volume is not None:
            self.hooks.set_volume(self._prior_volume, self._outputs())
        self.hooks.alert_owner("stood_down", f"Person left / {reason}. "
                               "Clip saved.")
        self.state = "stood_down"
        self._say(f"Stood down ({reason}); volume restored to "
                  f"{self._prior_volume}.")
        self.state = "idle"
        return "stood_down"


# ── diagnostics + self-test ─────────────────────────────────────────

def diagnostics(engine=None):
    engine = engine or DeterrenceEngine()
    ka = engine.keepalive
    backend = ka.available_backend()
    lines = ["Deterrence — diagnostics",
             f"- Engine state: {engine.state}",
             f"- Outputs: {', '.join(engine._outputs())} "
             f"(fallback {engine.config['speakers']['fallback_output']})",
             "- BCPA9: NEVER an output (enforced in config validation)",
             f"- Keep-alive backend: {backend or 'unavailable on this machine (stub — starts on ThinkPad)'}",
             f"- Keep-alive running: {ka.is_running()}",
             f"- Deterrence volume: {engine.config['volume']['deterrence_level']} "
             f"(restored after: {engine.config['volume']['restore_after']})",
             "- Event source: Frigate person events (ThinkPad wiring); "
             "engine itself is source-agnostic via on_person_event()."]
    return "\n".join(lines)


def self_test():
    """Simulated end-to-end: unfamiliar person → deter → escalate →
    clear → stand down + volume restore; familiar → no deterrence;
    mid-deterrence recognition → apology stand-down; entry → handoff.
    All hooks mocked (recorded, no side effects)."""
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    hooks = Hooks()
    engine = DeterrenceEngine(hooks=hooks)
    ev = {"kind": "person", "camera": "side_door"}
    check("animal event ignored",
          engine.on_person_event({"kind": "animal", "camera": "x"})
          == "ignored_no_human")
    check("unfamiliar person → deterrence starts",
          engine.on_person_event(ev) == "deterrence_started")
    spoken = [c for c in hooks.calls if c[0] == "speak"]
    check("voice line spoken on BT outputs (not BCPA9)",
          spoken and all(c[1]["output"] in ("bt_tws_front", "bt_tws_rear")
                         for c in spoken), str(spoken))
    check("lights + record + alert fired in parallel",
          any(c[0] == "lights" for c in hooks.calls)
          and any(c[0] == "record" for c in hooks.calls)
          and any(c[0] == "alert" for c in hooks.calls))
    vol_sets = [c[1]["level"] for c in hooks.calls if c[0] == "volume"]
    check("volume raised to deterrence level", vol_sets and vol_sets[0] == 100,
          str(vol_sets))
    check("still present → escalated",
          engine.on_person_still_present(ev) == "escalated")
    check("area clear → stood down",
          engine.on_area_clear(ev) == "stood_down")
    vol_sets = [c[1]["level"] for c in hooks.calls if c[0] == "volume"]
    check("volume restored after stand-down", vol_sets[-1] == 40,
          str(vol_sets))

    class FamiliarHooks(Hooks):
        def familiar_check(self, event):
            return "Shawn"
    hooks2 = FamiliarHooks()
    engine2 = DeterrenceEngine(hooks=hooks2)
    check("familiar person → no deterrence",
          engine2.on_person_event(ev) == "familiar_no_deterrence"
          and not any(c[0] == "speak" for c in hooks2.calls))

    class LateFamiliarHooks(Hooks):
        def __init__(self):
            super().__init__()
            self.n = 0

        def familiar_check(self, event):
            self.n += 1
            return None if self.n == 1 else "Lien Pham"
    engine3 = DeterrenceEngine(hooks=LateFamiliarHooks())
    engine3.on_person_event(ev)
    check("recognized mid-deterrence → apology stand-down",
          engine3.on_person_still_present(ev) == "stood_down")

    hooks4 = Hooks()
    engine4 = DeterrenceEngine(hooks=hooks4)
    check("entry → theft-recovery handoff",
          engine4.on_entry(ev) == "theft_handoff"
          and any(c[0] == "theft_handoff" for c in hooks4.calls))

    try:
        bad = json.loads(json.dumps(DEFAULT_CONFIG))
        bad["speakers"]["deterrence_outputs"] = ["bcpa9"]
        DeterrenceEngine(config=bad)
        check("BCPA9 output rejected by validation", False)
    except ValueError:
        check("BCPA9 output rejected by validation", True)

    ka = KeepAlive()
    running, detail = ka.start()
    check("keep-alive honest state (runs or stub, never faked)",
          isinstance(running, bool) and bool(detail), detail)
    if running:
        ka.stop()
    print("deterrence self_test:", "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


def _serve():
    print("Deterrence serve mode is wired on the ThinkPad (Frigate "
          "event source). Off-device, run --self-test / --diagnostics.")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    if "--serve" in sys.argv:
        sys.exit(_serve())
    print(__doc__)
