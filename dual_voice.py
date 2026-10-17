#!/usr/bin/env python3
"""
dual_voice.py — Dual Voice Mode (DVM) for laptop Scout.

Phase C (2026-10-16). DVM (approved 2026-10-16): ONE user switch —
DVM on = Scout sounds like two people having a conversation; off =
normal single voice. Configurations are internal, auto-selected by
what's connected; the user never picks one:

  * Laptop alone (built first): this module renders both voices —
    two distinct Kokoro voice ids, lines played sequentially through
    the van speakers.
  * Two-device: phone + laptop connected → each speaks its own lines.
    Lines pass as TEXT between instances (never over the air — avoids
    wake-word firing + interruption spirals), via a name-sync-style
    protocol stub here; full transport rides the multi-instance
    session protocol on the ThinkPad.
  * Phone alone: the phone app's build (Build 1's DualVoiceEngine).

Semantics mirror Build 1's phone DualVoiceEngine (interim lesson,
re-check at Build 1 completion): scripts use "A:" / "B:" line
prefixes; A and B alternate speaker ids; the two voices MUST differ
(same voice = one person talking to themselves — rejected in code).

Rules (spec): personas differ (style/vocabulary), delivery differs
(pace/formality), scripted dialogue can be pre-rendered to audio for
smooth playback; live generation pauses between turns.

Shawn participates as a third participant:
  * Director: pause via "hey scout" or an app button → Shawn speaks →
    dialogue resumes (pause/resume hooks here).
  * Character: Shawn takes one role; Scout plays the other(s). In
    character mode Shawn's lines are NOT rendered by TTS — the player
    waits for his spoken turn via the turn hook.

TTS itself is a hook (ThinkPad: Kokoro via talk.py; off-device: a
recording stub) so parsing/splitting/direction are testable here.
"""

import sys

DEFAULT_VOICES = {"A": "am_adam", "B": "af_heart"}   # MUST differ
DEFAULT_PERSONAS = {
    "A": {"name": "A", "style": "dry, direct", "pace": 1.0},
    "B": {"name": "B", "style": "warm, curious", "pace": 0.95},
}


class DvmError(ValueError):
    pass


# ── script parsing (mirrors Build 1 DualVoiceEngine semantics) ──────

def parse_script(text):
    """Parse 'A: ...' / 'B: ...' dialogue into [(speaker, line)].
    Unprefixed lines continue the previous speaker; a script that
    starts unprefixed defaults to A. Blank lines are skipped."""
    turns = []
    current = "A"
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if len(line) >= 2 and line[1] == ":" and line[0] in ("A", "B"):
            current = line[0]
            spoken = line[2:].strip()
            if spoken:
                turns.append((current, spoken))
        else:
            turns.append((current, line))
    return turns


# ── TTS hook ────────────────────────────────────────────────────────

class TtsHook:
    """Off-device: records renders. ThinkPad: Kokoro render+play."""

    def __init__(self):
        self.rendered = []              # (voice_id, line, device)

    def render(self, voice_id, line, device="laptop"):
        self.rendered.append((voice_id, line, device))
        return {"voice": voice_id, "line": line, "device": device,
                "audio": None}          # ThinkPad fills audio bytes/path

    def prerender(self, turns, voices, device_map=None):
        """Scripted dialogue → audio up front for smooth playback."""
        out = []
        for speaker, line in turns:
            device = (device_map or {}).get(speaker, "laptop")
            out.append(self.render(voices[speaker], line, device))
        return out


# ── configurations ──────────────────────────────────────────────────

class LaptopAlonePlayer:
    """One device renders both voices sequentially."""

    def __init__(self, voices=None, tts=None, personas=None):
        self.voices = dict(voices or DEFAULT_VOICES)
        if self.voices["A"] == self.voices["B"]:
            raise DvmError("DVM voices MUST differ — same voice is one "
                           "person talking to themselves.")
        self.tts = tts or TtsHook()
        self.personas = personas or DEFAULT_PERSONAS
        self.paused = False
        self._director_interrupt = None

    def play(self, script_text, on_turn=None):
        turns = parse_script(script_text)
        played = []
        for i, (speaker, line) in enumerate(turns):
            if self.paused:
                played.append(("paused_before", i))
                break
            if on_turn is not None:
                on_turn(speaker, line, i)
            played.append(self.tts.render(self.voices[speaker], line,
                                          device="laptop"))
        return played

    # Director hooks: Shawn interrupts, speaks, dialogue resumes.
    def director_pause(self):
        self.paused = True
        return "paused — Shawn has the floor"

    def director_resume(self):
        self.paused = False
        return "resumed"


class TwoDeviceSplitter:
    """Splits lines by device: laptop speaks its speaker's lines, the
    phone speaks the other's. Lines pass as TEXT via the handoff stub
    (name-sync-style: versioned JSON messages, FIFO turn order)."""

    PROTOCOL_VERSION = 1

    def __init__(self, local_speaker="A", remote_speaker="B",
                 voices=None, tts=None):
        if local_speaker == remote_speaker:
            raise DvmError("Two-device split needs distinct speakers "
                           "per device.")
        self.local_speaker = local_speaker
        self.remote_speaker = remote_speaker
        self.voices = dict(voices or DEFAULT_VOICES)
        if self.voices["A"] == self.voices["B"]:
            raise DvmError("DVM voices MUST differ.")
        self.tts = tts or TtsHook()
        self.outbox = []                # messages for the remote device

    def split(self, script_text):
        """Returns (local_renders, remote_messages). Remote lines are
        queued as protocol messages — text only, never audio over air."""
        turns = parse_script(script_text)
        local, remote = [], []
        for seq, (speaker, line) in enumerate(turns):
            if speaker == self.local_speaker:
                local.append(self.tts.render(self.voices[speaker], line,
                                             device="laptop"))
            else:
                msg = {"protocol": self.PROTOCOL_VERSION,
                       "type": "dvm_line", "seq": seq,
                       "speaker": speaker, "voice": self.voices[speaker],
                       "line": line}
                remote.append(msg)
                self.outbox.append(msg)
        return local, remote

    def receive(self, message):
        """Handle an incoming dvm_line for THIS device (when the
        laptop is the remote side of someone else's split)."""
        if message.get("protocol") != self.PROTOCOL_VERSION:
            raise DvmError(f"DVM protocol mismatch: got "
                           f"{message.get('protocol')}, want "
                           f"{self.PROTOCOL_VERSION} (versioned "
                           "contracts negotiate, never hard-fail silently)")
        return self.tts.render(message["voice"], message["line"],
                               device="laptop")


# ── Shawn as third participant ──────────────────────────────────────

class DirectorSession:
    """Wraps a player with director + character participation."""

    def __init__(self, player, shawn_role=None):
        self.player = player
        self.shawn_role = shawn_role    # None=director, "A"/"B"=character
        self.shawn_turns = []           # lines Shawn spoke (director) —
                                        # routed back into the dialogue

    def interrupt(self):
        return self.player.director_pause()

    def resume(self):
        return self.player.director_resume()

    def play_with_participation(self, script_text, shawn_turn_hook=None):
        """Character mode: Shawn's role lines are NOT TTS-rendered —
        the hook is called and playback waits for his spoken turn.
        Director mode (shawn_role None): all lines render; Shawn
        interrupts via interrupt() between lines."""
        turns = parse_script(script_text)
        played = []
        for speaker, line in turns:
            if self.shawn_role is not None and speaker == self.shawn_role:
                if shawn_turn_hook is not None:
                    spoken = shawn_turn_hook(speaker, line)
                else:
                    spoken = None       # ThinkPad: mic window / wake word
                played.append({"speaker": speaker, "line": line,
                               "by": "shawn", "heard": spoken})
            else:
                played.append(self.player.tts.render(
                    self.player.voices[speaker], line, device="laptop"))
        return played


# ── auto-selection (the only user-facing decision: DVM on/off) ──────

def auto_config(phone_connected):
    """DVM uses whatever devices are present — the user never picks."""
    return "two-device" if phone_connected else "laptop-alone"


# ── diagnostics + self-test ─────────────────────────────────────────

def diagnostics():
    return "\n".join([
        "Dual Voice Mode (DVM) — diagnostics",
        f"- Voices: A={DEFAULT_VOICES['A']}, B={DEFAULT_VOICES['B']} "
        "(must differ — enforced)",
        "- Configs: laptop-alone (both voices here) / two-device "
        "(lines split by device, text handoff, protocol v"
        f"{TwoDeviceSplitter.PROTOCOL_VERSION}) / phone-alone (app build)",
        "- Auto-selection: phone connected → two-device, else "
        "laptop-alone. User switch is only DVM on/off.",
        "- Shawn: director (pause/speak/resume) or character (takes a "
        "role, lines not TTS-rendered).",
        "- TTS: hook — Kokoro via talk.py on the ThinkPad; recording "
        "stub off-device.",
    ])


SAMPLE_SCRIPT = """A: We made it to the lake just before sunset.
B: And the water went completely still.
A: That's when the loons started calling.
B: Best sound in the world.
"""


def self_test():
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    turns = parse_script(SAMPLE_SCRIPT)
    check("sample script parses to 4 alternating turns",
          turns == [("A", "We made it to the lake just before sunset."),
                    ("B", "And the water went completely still."),
                    ("A", "That's when the loons started calling."),
                    ("B", "Best sound in the world.")], str(turns))
    cont = parse_script("A: First line.\nstill A talking.\nB: Now B.")
    check("unprefixed line continues previous speaker",
          cont[1] == ("A", "still A talking."), str(cont))
    tts = TtsHook()
    player = LaptopAlonePlayer(tts=tts)
    played = player.play(SAMPLE_SCRIPT)
    check("laptop-alone renders both voices, differing ids",
          len(played) == 4
          and played[0]["voice"] != played[1]["voice"], str(played))
    try:
        LaptopAlonePlayer(voices={"A": "same", "B": "same"})
        check("identical voices rejected", False)
    except DvmError:
        check("identical voices rejected", True)
    pre = tts.prerender(turns, DEFAULT_VOICES)
    check("prerender covers all turns", len(pre) == 4)
    splitter = TwoDeviceSplitter(local_speaker="A", remote_speaker="B")
    local, remote = splitter.split(SAMPLE_SCRIPT)
    check("two-device split: A local, B as text messages",
          len(local) == 2 and len(remote) == 2
          and all(m["type"] == "dvm_line" for m in remote),
          f"local={len(local)} remote={len(remote)}")
    back = splitter.receive(remote[0])
    check("remote line renders on receipt with its voice",
          back["voice"] == DEFAULT_VOICES["B"], str(back))
    try:
        splitter.receive({"protocol": 99, "voice": "x", "line": "y"})
        check("protocol mismatch raises (versioned contract)", False)
    except DvmError:
        check("protocol mismatch raises (versioned contract)", True)
    check("director pause/resume hooks",
          player.director_pause().startswith("paused")
          and player.director_resume() == "resumed")
    session = DirectorSession(LaptopAlonePlayer(tts=TtsHook()),
                              shawn_role="B")
    heard = session.play_with_participation(
        SAMPLE_SCRIPT, shawn_turn_hook=lambda s, l: f"<shawn said: {l}>")
    shawn_lines = [h for h in heard if h.get("by") == "shawn"]
    check("character mode: Shawn's lines wait for him, not TTS",
          len(shawn_lines) == 2
          and all(h["heard"] for h in shawn_lines), str(heard))
    check("auto-config: phone → two-device, none → laptop-alone",
          auto_config(True) == "two-device"
          and auto_config(False) == "laptop-alone")
    print("dual_voice self_test:", "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    print(__doc__)
