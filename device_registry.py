#!/usr/bin/env python3
"""
TV device registry for van Scout (ThinkPad) — Universal Outpost v2.8.

Mirror of the Kotlin DeviceRegistry (outpost module, DeviceRegistry.kt).
Same semantics on both sides so the phone, the laptop and Outpost itself
all resolve a spoken target the same way:

  - "all" / "everywhere" / "both" / "all devices" -> every device
  - exact name match (case-insensitive) wins over substring matches
  - otherwise a case-insensitive substring match: one hit resolves,
    several hits are AMBIGUOUS (ask the user), zero hits is NOT_FOUND
  - a bare command (no target) -> the default device, else the only
    device, else AMBIGUOUS

Persistence: a single JSON file, stdlib only.
Default path: ~/.scout/tv-devices.json (override with the `path`
argument or the SCOUT_TV_REGISTRY environment variable).

Voice-target parsing (parse_voice_target) pulls the target phrase out of
a full command sentence:
    "open Netflix on the living room box" -> "living room box"
    "pause on both"                       -> "both" (broadcast)
    "play some music"                     -> None (bare -> default)

Usage as a library:
    from device_registry import DeviceRegistry
    reg = DeviceRegistry()
    reg.register("living room box", ip="192.168.1.50")
    result = reg.resolve_target("living room box")
    if result.kind == "single":
        tv = OutpostClient(result.entries[0]["ip"])

Self-test:
    python3 device_registry.py --self-test
"""

import json
import os
import sys
import tempfile
import time
import uuid

DEFAULT_PORT = 8087

_BROADCAST_PHRASES = (
    "all", "everywhere", "both", "all devices", "every device",
    "all shields", "all tvs", "all boxes",
)

_FILLER_PREFIXES = ("on the ", "on my ", "on ", "the ", "my ", "to the ", "to ")

# Phrases that introduce a device target in a spoken command, longest first.
_TARGET_MARKERS = (" on the ", " on my ", " on both ", " on all ", " on ")


class ResolveResult:
    """Result of resolve_target(). kind: single | all | ambiguous | not_found."""

    def __init__(self, kind, entries):
        self.kind = kind
        self.entries = entries  # list of entry dicts

    def __repr__(self):
        names = [e.get("display_name", "?") for e in self.entries]
        return "ResolveResult(kind={!r}, entries={!r})".format(self.kind, names)


def _is_broadcast_query(q):
    q = q.strip().lower()
    for phrase in _BROADCAST_PHRASES:
        if q == phrase or q.startswith(phrase + " ") or q.endswith(" " + phrase) \
                or (" " + phrase + " ") in q:
            return True
    return False


def _strip_target_filler(q):
    out = q.strip().lower()
    changed = True
    while changed:
        changed = False
        for prefix in _FILLER_PREFIXES:
            if out.startswith(prefix) and len(out) > len(prefix):
                out = out[len(prefix):].strip()
                changed = True
                break
    return out


def parse_voice_target(command_text):
    """
    Extract the device-target phrase from a spoken command, or None if the
    command names no device (bare command -> caller uses the default).

    Handles: "on the living room box", "on my shield", "on both",
    "on all the boxes" loosely, "to the bedroom shield".
    A trailing "shield"/"tv"/"box" is kept — names usually include it.
    """
    if not command_text:
        return None
    text = " " + command_text.strip().lower().rstrip(".!?") + " "
    for marker in _TARGET_MARKERS:
        idx = text.rfind(marker)
        if idx >= 0:
            tail = text[idx + len(marker):].strip()
            if tail:
                return tail
    if " to the " in text:
        tail = text.rsplit(" to the ", 1)[1].strip()
        if tail:
            return tail
    # Whole-command broadcast, e.g. the routed remainder was just "both".
    bare = text.strip()
    if _is_broadcast_query(bare):
        return bare
    return None


class DeviceRegistry:
    def __init__(self, path=None):
        self.path = path or os.environ.get(
            "SCOUT_TV_REGISTRY",
            os.path.join(os.path.expanduser("~"), ".scout", "tv-devices.json"),
        )
        self._entries = []
        self.load()

    # ---- persistence ----

    def load(self):
        """(Re)load from disk. A missing or corrupt file means an empty
        registry — never raises, so Scout starts cleanly on a new laptop."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("devices", [])
            self._entries = [e for e in data if isinstance(e, dict)]
        except (OSError, json.JSONDecodeError, TypeError):
            self._entries = []
        return self._entries

    def save(self):
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        payload = {"version": 1, "devices": self._entries}
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, self.path)

    # ---- CRUD ----

    def register(self, display_name, ip="", port=DEFAULT_PORT, profile_summary="",
                 brand="", tier="", api_version="v1", capabilities=None,
                 ssid=None, is_default=False, entry_id=None, save=True):
        """
        Add or update a device. Re-registering the same name (any case) or
        the same id updates the existing row. A new default clears the old
        one. Returns the stored entry dict.
        """
        now = int(time.time() * 1000)
        entry = {
            "id": entry_id or str(uuid.uuid4()),
            "display_name": display_name,
            "profile_summary": profile_summary,
            "brand": brand,
            "tier": tier,
            "ip": ip,
            "port": int(port),
            "api_version": api_version,
            "capabilities": sorted(capabilities or []),
            "ssid": ssid,
            "is_default": bool(is_default),
            "last_seen": now,
        }
        if entry["is_default"]:
            for e in self._entries:
                e["is_default"] = False
        for i, e in enumerate(self._entries):
            if e.get("id") == entry["id"] or \
                    e.get("display_name", "").lower() == display_name.lower():
                entry["id"] = e.get("id", entry["id"])
                self._entries[i] = entry
                if save:
                    self.save()
                return entry
        self._entries.append(entry)
        if save:
            self.save()
        return entry

    def remove(self, entry_id):
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.get("id") != entry_id]
        if len(self._entries) != before:
            self.save()
            return True
        return False

    def list(self):
        return list(self._entries)

    def default_entry(self):
        for e in self._entries:
            if e.get("is_default"):
                return e
        return None

    def touch(self, entry_id):
        for e in self._entries:
            if e.get("id") == entry_id:
                e["last_seen"] = int(time.time() * 1000)
                self.save()
                return e
        return None

    # ---- lookup / targeting (mirrors DeviceRegistry.kt) ----

    def find_by_name(self, query):
        """Best matches first: exact, then name-contains-query, then
        query-contains-name. Empty list when nothing matches."""
        q = (query or "").strip().lower()
        if not q:
            return []
        exact, contains, contained_by = [], [], []
        for e in self._entries:
            name = e.get("display_name", "").lower()
            if name == q:
                exact.append(e)
            elif q in name:
                contains.append(e)
            elif name and name in q:
                contained_by.append(e)
        return exact + contains + contained_by

    def resolve_target(self, query):
        """
        Resolve a target phrase (already extracted, or a raw name) to a
        ResolveResult. Pass None / "" for a bare command (smart default).
        """
        if not self._entries:
            return ResolveResult("not_found", [])
        q = (query or "").strip().lower()
        if not q:
            default = self.default_entry()
            if default is not None:
                return ResolveResult("single", [default])
            if len(self._entries) == 1:
                return ResolveResult("single", list(self._entries))
            return ResolveResult("ambiguous", list(self._entries))
        if _is_broadcast_query(q):
            return ResolveResult("all", list(self._entries))
        cleaned = _strip_target_filler(q)
        matches = self.find_by_name(cleaned)
        if not matches:
            return ResolveResult("not_found", [])
        if len(matches) == 1:
            return ResolveResult("single", matches)
        for m in matches:
            if m.get("display_name", "").lower() == cleaned:
                return ResolveResult("single", [m])
        return ResolveResult("ambiguous", matches)

    def resolve_voice_command(self, command_text):
        """Full pipeline: parse the target out of a spoken command, then
        resolve it. Returns a ResolveResult."""
        return self.resolve_target(parse_voice_target(command_text))

    # ---- diagnostics ----

    def diagnostics(self):
        """Plain status dict for Scout's diagnostics card / logs."""
        return {
            "registry_path": self.path,
            "file_exists": os.path.exists(self.path),
            "device_count": len(self._entries),
            "default": (self.default_entry() or {}).get("display_name"),
            "devices": [
                {
                    "name": e.get("display_name"),
                    "ip": e.get("ip"),
                    "api_version": e.get("api_version"),
                    "tier": e.get("tier"),
                    "last_seen": e.get("last_seen"),
                }
                for e in self._entries
            ],
        }


def self_test():
    """Round-trip + targeting checks in a temp dir. Returns (ok, lines)."""
    lines = []
    ok = True

    def check(label, cond):
        nonlocal ok
        lines.append("{} — {}".format("PASS" if cond else "FAIL", label))
        if not cond:
            ok = False

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "nested", "tv-devices.json")
        reg = DeviceRegistry(path=path)
        check("empty registry resolves not_found",
              reg.resolve_target("anything").kind == "not_found")

        reg.register("living room box", ip="192.168.1.50", is_default=True,
                     brand="SHIELD", tier="FULL", api_version="v2")
        reg.register("bedroom shield", ip="192.168.1.51", brand="SHIELD",
                     tier="FULL")
        check("two devices registered", len(reg.list()) == 2)
        check("file written", os.path.exists(path))

        reg2 = DeviceRegistry(path=path)
        check("round-trip save/load keeps both devices", len(reg2.list()) == 2)
        check("default survives round-trip",
              (reg2.default_entry() or {}).get("display_name") == "living room box")

        r = reg2.resolve_target("living room box")
        check("exact name resolves single", r.kind == "single"
              and r.entries[0]["ip"] == "192.168.1.50")
        r = reg2.resolve_target("LIVING ROOM")
        check("case-insensitive substring resolves single", r.kind == "single")
        r = reg2.resolve_target(None)
        check("bare command resolves the default", r.kind == "single"
              and r.entries[0]["display_name"] == "living room box")
        r = reg2.resolve_target("on both")
        check("'on both' broadcasts", r.kind == "all" and len(r.entries) == 2)
        r = reg2.resolve_target("everywhere")
        check("'everywhere' broadcasts", r.kind == "all")
        r = reg2.resolve_target("kitchen")
        check("unknown name is not_found", r.kind == "not_found")

        reg2.register("living room shield", ip="192.168.1.52")
        r = reg2.resolve_target("living room")
        check("two substring hits are ambiguous", r.kind == "ambiguous"
              and len(r.entries) == 2)
        r = reg2.resolve_target("living room box")
        check("exact match wins over ambiguity", r.kind == "single"
              and r.entries[0]["ip"] == "192.168.1.50")

        r = reg2.resolve_voice_command("open Netflix on the living room box")
        check("voice parse: 'on the living room box'", r.kind == "single"
              and r.entries[0]["display_name"] == "living room box")
        r = reg2.resolve_voice_command("pause on both")
        check("voice parse: 'on both' broadcasts", r.kind == "all")
        r = reg2.resolve_voice_command("play some music")
        check("voice parse: no target -> default", r.kind == "single"
              and r.entries[0]["display_name"] == "living room box")

        reg2.register("living room box", ip="192.168.1.99")
        check("re-register same name updates, no duplicate",
              len(reg2.list()) == 3
              and reg2.find_by_name("living room box")[0]["ip"] == "192.168.1.99")

        diag = reg2.diagnostics()
        check("diagnostics reports 3 devices", diag["device_count"] == 3)
    return ok, lines


def _cli(argv):
    if "--self-test" in argv:
        ok, lines = self_test()
        for line in lines:
            print(line)
        print("self_test:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    reg = DeviceRegistry()
    if "--list" in argv:
        for e in reg.list():
            print("{}  {}:{}{}".format(
                e.get("display_name"), e.get("ip"), e.get("port"),
                "  (default)" if e.get("is_default") else ""))
        return 0
    if "--diagnostics" in argv:
        print(json.dumps(reg.diagnostics(), indent=2))
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
