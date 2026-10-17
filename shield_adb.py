#!/usr/bin/env python3
"""
Shield ADB control for van Scout (ThinkPad) — Phase A.

Stdlib-only wrapper around the `adb` command-line tool for driving the
Nvidia Shield TV over the LAN (Network Debugging, port 5555). This is the
laptop half of the Shield full-control stack; the on-device half is the
Outpost v2 API (see OUTPOST-API-V2.md in this folder).

Design rules:
  - NO root commands, ever. Everything here runs as the unprivileged ADB
    `shell` user or through public adb subcommands. If something needs
    more than that, this module says so instead of trying.
  - Honest reporting: diagnostics() / self_test() say plainly when adb is
    missing, when no device is configured, when a device is unreachable,
    and when it is reachable but NOT authorized (RSA prompt not accepted
    on the TV yet). Nothing is faked or assumed.
  - Config-driven: devices come from shield-devices.json (see
    load_config) so an IP change is a one-line edit, not a code change.
    Give the Shield a DHCP reservation anyway.

shield-devices.json format (next to this file, or --config PATH):
    {
      "devices": [
        {"name": "shield-van", "ip": "192.168.1.50", "port": 5555}
      ]
    }
Port defaults to 5555 (Shield Network Debugging).

Setup on the Shield (one time, Shawn):
  Settings > Device Preferences > About > tap Build 7 times, then
  Device Preferences > Developer options > Network Debugging ON.
  First `connect` shows an RSA authorization prompt on the TV — accept it
  and tick "always allow" so reconnects are silent.

Usage as a library:
    from shield_adb import ShieldAdb, load_config
    adb = ShieldAdb(load_config()[0])
    print(adb.diagnostics())
    adb.connect()
    adb.launch("com.netflix.ninja")
    adb.keyevent("DPAD_CENTER")
    adb.screencap("/tmp/shield.png")
    tree = adb.ui_dump()          # nested dicts, UIAutomator hierarchy
    print(adb.find(tree, text="Settings"))

CLI:
    python3 shield_adb.py diagnostics
    python3 shield_adb.py self-test
    python3 shield_adb.py discover
    python3 shield_adb.py connect [--name shield-van]
    python3 shield_adb.py launch com.netflix.ninja
    python3 shield_adb.py keyevent HOME
    python3 shield_adb.py screencap /tmp/shield.png
    python3 shield_adb.py ui-dump [--find-text Settings]
    python3 shield_adb.py install app.apk / uninstall com.example.app
    python3 shield_adb.py settings-get global adb_enabled
    python3 shield_adb.py settings-put secure screensaver_enabled 0
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

DEFAULT_PORT = 5555
DEFAULT_CONFIG_NAME = "shield-devices.json"
ADB_TIMEOUT = 20          # seconds per adb invocation
CONNECT_BACKOFFS = (0, 2, 5, 10)   # delays between connect attempts

# Friendly key names -> Android keyevent names (KEYCODE_ prefix optional).
KEY_ALIASES = {
    "up": "DPAD_UP", "down": "DPAD_DOWN", "left": "DPAD_LEFT",
    "right": "DPAD_RIGHT", "ok": "DPAD_CENTER", "select": "DPAD_CENTER",
    "enter": "DPAD_CENTER", "back": "BACK", "home": "HOME",
    "menu": "MENU", "play": "MEDIA_PLAY", "pause": "MEDIA_PAUSE",
    "playpause": "MEDIA_PLAY_PAUSE", "stop": "MEDIA_STOP",
    "next": "MEDIA_NEXT", "previous": "MEDIA_PREVIOUS",
    "rewind": "MEDIA_REWIND", "ff": "MEDIA_FAST_FORWARD",
    "volup": "VOLUME_UP", "voldown": "VOLUME_DOWN", "mute": "VOLUME_MUTE",
    "power": "POWER", "wake": "WAKEUP", "sleep": "SLEEP",
    "search": "SEARCH", "settings": "SETTINGS", "tv": "TV",
    "channelup": "CHANNEL_UP", "channeldown": "CHANNEL_DOWN",
}

SETTINGS_NAMESPACES = ("system", "secure", "global")


class AdbError(Exception):
    """adb is missing, or a command failed in a way the caller must see."""


class DeviceConfig:
    """One Shield from shield-devices.json."""

    def __init__(self, name, ip, port=DEFAULT_PORT):
        self.name = str(name)
        self.ip = str(ip)
        self.port = int(port)

    @property
    def serial(self):
        return "{}:{}".format(self.ip, self.port)

    def __repr__(self):
        return "DeviceConfig({!r}, {})".format(self.name, self.serial)


def default_config_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        DEFAULT_CONFIG_NAME)


def load_config(path=None):
    """Load devices from shield-devices.json. Returns [] if none exists."""
    candidates = []
    if path:
        candidates.append(path)
    candidates.append(os.path.join(os.getcwd(), DEFAULT_CONFIG_NAME))
    candidates.append(default_config_path())
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            devices = []
            for entry in data.get("devices", []):
                ip = entry.get("ip")
                if not ip:
                    continue
                devices.append(DeviceConfig(
                    entry.get("name", ip), ip, entry.get("port", DEFAULT_PORT)))
            return devices
    return []


def write_example_config(path=None):
    """Write a starter shield-devices.json if none exists. Returns path."""
    target = path or default_config_path()
    if os.path.exists(target):
        return target
    example = {
        "devices": [
            {"name": "shield-van", "ip": "192.168.1.50", "port": 5555}
        ]
    }
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(example, fh, indent=2)
        fh.write("\n")
    return target


def parse_mdns_services(text):
    """Parse `adb mdns services` output into [(name, service, endpoint)]."""
    found = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.lower().startswith("list of discovered"):
            continue
        # Format: name \t service \t ip:port
        parts = [p.strip() for p in line.split("\t") if p.strip()]
        if len(parts) >= 3:
            found.append((parts[0], parts[1], parts[2]))
        elif len(parts) == 1 and ":" in parts[0]:
            found.append(("", "", parts[0]))
    return found


def parse_devices(text):
    """Parse `adb devices` output into {serial: state}."""
    devices = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices[parts[0]] = parts[1]
    return devices


def parse_bounds(text):
    """'[x1,y1][x2,y2]' -> (x1, y1, x2, y2) or None."""
    if not text:
        return None
    nums = re.findall(r"-?\d+", text)
    if len(nums) != 4:
        return None
    return tuple(int(n) for n in nums)


def _bool(text):
    return str(text).lower() == "true"


def node_from_element(elem):
    """Convert one UIAutomator <node> element into a plain dict."""
    a = elem.attrib
    bounds = parse_bounds(a.get("bounds", ""))
    node = {
        "index": int(a.get("index", 0) or 0),
        "text": a.get("text", ""),
        "resourceId": a.get("resource-id", ""),
        "class": a.get("class", ""),
        "package": a.get("package", ""),
        "contentDesc": a.get("content-desc", ""),
        "clickable": _bool(a.get("clickable")),
        "enabled": _bool(a.get("enabled")),
        "focusable": _bool(a.get("focusable")),
        "focused": _bool(a.get("focused")),
        "selected": _bool(a.get("selected")),
        "scrollable": _bool(a.get("scrollable")),
        "checkable": _bool(a.get("checkable")),
        "checked": _bool(a.get("checked")),
        "bounds": bounds,
        "center": ((bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2)
                  if bounds else None,
        "children": [node_from_element(child) for child in elem
                     if child.tag == "node"],
    }
    return node


class ShieldAdb:
    """ADB operations against one configured Shield."""

    def __init__(self, device, adb_path=None):
        self.device = device
        self.adb = adb_path or shutil.which("adb")

    # ---- low level ----

    def _run(self, args, timeout=ADB_TIMEOUT, binary=False):
        """Run adb; returns (returncode, stdout, stderr). Raises AdbError
        only when adb itself is missing — callers judge the rest."""
        if not self.adb:
            raise AdbError(
                "adb is not installed (or not on PATH). "
                "Install it with: sudo apt install adb")
        cmd = [self.adb] + list(args)
        try:
            if binary:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, timeout=timeout)
                return proc.returncode, proc.stdout, proc.stderr.decode(
                    "utf-8", "replace")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=timeout)
            return proc.returncode, proc.stdout.decode(
                "utf-8", "replace"), proc.stderr.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            raise AdbError("adb timed out after {}s: {}".format(
                timeout, " ".join(args)))

    def _shell(self, args, timeout=ADB_TIMEOUT):
        return self._run(["-s", self.device.serial, "shell"] + list(args),
                         timeout=timeout)

    # ---- discovery / connection ----

    @staticmethod
    def mdns_discover(adb_path=None):
        """Ask adb's built-in mDNS what ADB endpoints are on the LAN.
        Returns [(name, service, 'ip:port'), ...]; [] if unsupported."""
        adb = adb_path or shutil.which("adb")
        if not adb:
            return []
        try:
            proc = subprocess.run([adb, "mdns", "services"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=10)
            return parse_mdns_services(
                proc.stdout.decode("utf-8", "replace"))
        except (subprocess.TimeoutExpired, OSError):
            return []

    def discover(self):
        """Everything we can learn without connecting: mDNS sightings,
        configured devices, and a raw TCP reachability probe per device."""
        sightings = self.mdns_discover(self.adb)
        return {
            "mdns": [
                {"name": n, "service": s, "endpoint": e}
                for (n, s, e) in sightings
            ],
            "configured_reachable": self.tcp_reachable(),
        }

    def tcp_reachable(self, timeout=2.0):
        """True if something answers TCP on the device's ADB port.
        Reachable != authorized; see device_state()."""
        try:
            with socket.create_connection(
                    (self.device.ip, self.device.port), timeout=timeout):
                return True
        except OSError:
            return False

    def device_state(self):
        """adb's view of this device: 'device' (ready), 'unauthorized'
        (accept the RSA prompt on the TV), 'offline', or None (not listed)."""
        code, out, _ = self._run(["devices"])
        if code != 0:
            return None
        return parse_devices(out).get(self.device.serial)

    def is_connected(self):
        """True only when adb lists the device in the ready state."""
        return self.device_state() == "device"

    def connect(self, attempts=None):
        """Connect with reconnect/backoff. Returns (ok, last_message).
        Retries because a just-woken Shield can refuse the first attempt,
        and because the connection does not survive a Shield reboot — call
        this again after reboots instead of assuming."""
        delays = CONNECT_BACKOFFS if attempts is None else \
            CONNECT_BACKOFFS[:max(1, attempts)]
        last = ""
        for i, delay in enumerate(delays):
            if delay:
                time.sleep(delay)
            code, out, err = self._run(
                ["connect", self.device.serial], timeout=15)
            last = (out or err or "").strip()
            if self.is_connected():
                return True, last or "connected"
            # 'unauthorized' will never fix itself from here — stop early
            # and let diagnostics explain the TV-side prompt.
            if self.device_state() == "unauthorized":
                return False, ("unauthorized — accept the RSA prompt on "
                               "the TV (tick 'always allow') and retry")
        return False, last or "connect failed"

    def disconnect(self):
        code, out, err = self._run(["disconnect", self.device.serial])
        return code == 0, (out or err).strip()

    def ensure_connected(self):
        """Connect if needed; returns (ok, message)."""
        if self.is_connected():
            return True, "already connected"
        return self.connect()

    # ---- app management ----

    def install(self, apk_path, replace=True):
        """Install an APK (no root; the system installer rules apply)."""
        if not os.path.isfile(apk_path):
            return False, "APK not found: {}".format(apk_path)
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        args = ["-s", self.device.serial, "install"]
        if replace:
            args.append("-r")
        args.append(apk_path)
        code, out, err = self._run(args, timeout=180)
        text = (out + err).strip()
        return (code == 0 and "Success" in text), text or "install failed"

    def uninstall(self, package):
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, out, err = self._run(
            ["-s", self.device.serial, "uninstall", package], timeout=60)
        text = (out + err).strip()
        return (code == 0 and "Success" in text), text or "uninstall failed"

    def launch(self, package):
        """Launch an app's main/leanback activity via monkey, with an
        `am start` fallback. Honest failure if neither works."""
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, out, err = self._shell(
            ["monkey", "-p", package, "-c",
             "android.intent.category.LAUNCHER", "1"])
        text = out + err
        if code == 0 and "No activities found" not in text \
                and "monkey aborted" not in text.lower():
            return True, "launched {}".format(package)
        code, out, err = self._shell(
            ["am", "start", "-a", "android.intent.action.MAIN",
             "-c", "android.intent.category.LEANBACK_LAUNCHER",
             "-p", package])
        text = (out + err).strip()
        if code == 0 and "Error" not in text:
            return True, "launched {}".format(package)
        return False, text or "could not launch {}".format(package)

    def force_stop(self, package):
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, _, _ = self._shell(["am", "force-stop", package])
        return code == 0, "force-stopped {}".format(package)

    # ---- input ----

    def keyevent(self, key):
        """Send one key: friendly name ('ok', 'volup'), KEYCODE name
        ('KEYCODE_HOME' / 'HOME'), or a numeric keycode."""
        name = KEY_ALIASES.get(str(key).lower(), str(key))
        if name.isdigit():
            keycode = name
        elif name.upper().startswith("KEYCODE_"):
            keycode = name.upper()
        else:
            keycode = "KEYCODE_" + name.upper()
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, _, _ = self._shell(["input", "keyevent", keycode])
        return code == 0, "sent {}".format(keycode)

    def tap(self, x, y):
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, _, _ = self._shell(["input", "tap", str(int(x)), str(int(y))])
        return code == 0, "tapped {},{}".format(x, y)

    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, _, _ = self._shell(
            ["input", "swipe", str(int(x1)), str(int(y1)),
             str(int(x2)), str(int(y2)), str(int(duration_ms))])
        return code == 0, "swiped"

    def type_text(self, text):
        """Type text via `input text` (spaces as %s). ASCII-safe path;
        for rich text prefer Outpost's accessibility type or ADB IME."""
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        safe = text.replace("%", "").replace(" ", "%s")
        code, _, _ = self._shell(["input", "text", safe])
        return code == 0, "typed"

    # ---- screen ----

    def screencap(self, local_path):
        """Save a PNG of the current screen to local_path.
        DRM/secure surfaces come back black — that is the platform, not
        a failure of this call."""
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, data, err = self._run(
            ["-s", self.device.serial, "exec-out", "screencap", "-p"],
            timeout=30, binary=True)
        if code != 0 or not data:
            return False, (err or "screencap failed").strip()
        with open(local_path, "wb") as fh:
            fh.write(data)
        return True, "saved {} ({} bytes)".format(local_path, len(data))

    def ui_dump(self):
        """Dump the UI hierarchy via uiautomator and parse it into nested
        dicts (see node_from_element). Returns the root node dict, or
        raises AdbError with the honest reason. Screen text in the dump
        is the caller's data — this module never logs it anywhere."""
        ok, msg = self.ensure_connected()
        if not ok:
            raise AdbError(msg)
        remote = "/sdcard/window_dump.xml"
        code, out, err = self._shell(["uiautomator", "dump", remote])
        if code != 0:
            raise AdbError("uiautomator dump failed: {}".format(
                (out + err).strip()))
        code, data, err = self._run(
            ["-s", self.device.serial, "exec-out", "cat", remote],
            timeout=30, binary=True)
        if code != 0 or not data:
            raise AdbError("could not read the UI dump from the device")
        try:
            root_elem = ET.fromstring(data.decode("utf-8", "replace"))
        except ET.ParseError as exc:
            raise AdbError("UI dump was not valid XML: {}".format(exc))
        # <hierarchy> wraps the real root <node>.
        top = root_elem
        if top.tag == "hierarchy":
            children = [c for c in top if c.tag == "node"]
            if not children:
                raise AdbError("UI dump contained no nodes")
            top = children[0]
        return node_from_element(top)

    @staticmethod
    def walk(node):
        """Yield every node in a ui_dump() tree, depth-first."""
        yield node
        for child in node.get("children", []):
            yield from ShieldAdb.walk(child)

    @staticmethod
    def find(root, text=None, resource_id=None, class_name=None,
             content_desc=None):
        """All nodes matching every given criterion (exact match;
        text/content_desc also match as substrings, case-insensitive)."""
        matches = []
        for node in ShieldAdb.walk(root):
            if text is not None and text.lower() not in node["text"].lower() \
                    and text.lower() not in node["contentDesc"].lower():
                continue
            if resource_id is not None and node["resourceId"] != resource_id:
                continue
            if class_name is not None and node["class"] != class_name:
                continue
            if content_desc is not None and \
                    content_desc.lower() not in node["contentDesc"].lower():
                continue
            matches.append(node)
        return matches

    # ---- settings ----

    def settings_get(self, namespace, key):
        if namespace not in SETTINGS_NAMESPACES:
            raise AdbError("namespace must be one of {}".format(
                ", ".join(SETTINGS_NAMESPACES)))
        ok, msg = self.ensure_connected()
        if not ok:
            raise AdbError(msg)
        code, out, _ = self._shell(["settings", "get", namespace, key])
        value = out.strip()
        return None if value in ("", "null") else value

    def settings_put(self, namespace, key, value):
        if namespace not in SETTINGS_NAMESPACES:
            raise AdbError("namespace must be one of {}".format(
                ", ".join(SETTINGS_NAMESPACES)))
        ok, msg = self.ensure_connected()
        if not ok:
            return False, msg
        code, out, err = self._shell(
            ["settings", "put", namespace, key, str(value)])
        return code == 0, (out + err).strip() or \
            "set {} {}={}".format(namespace, key, value)

    # ---- diagnostics ----

    def diagnostics(self):
        """Plain-language health report. Returns (report_text, all_ready).
        Honest by construction: every line is a check that actually ran."""
        lines = []
        all_ready = True
        if not self.adb:
            return ("ADB tool: NOT FOUND on this laptop. "
                    "Install it with: sudo apt install adb\n"
                    "Nothing else can be checked until adb exists."), False
        code, out, err = self._run(["version"])
        version_line = (out or err).strip().splitlines()[0] if (out or err) \
            else "unknown version"
        lines.append("ADB tool: found ({})".format(version_line))

        dev = self.device
        lines.append("Device '{}': {} (from shield-devices.json)".format(
            dev.name, dev.serial))
        reachable = self.tcp_reachable()
        lines.append("Network: {} port {} is {}".format(
            dev.ip, dev.port,
            "answering" if reachable else "NOT answering"))
        if not reachable:
            all_ready = False
            lines.append(
                "  -> The Shield may be off/asleep, on a different IP, or "
                "Network Debugging may be off. Check: Shield Settings > "
                "Device Preferences > Developer options > Network "
                "Debugging ON, and confirm the Shield's IP in Settings > "
                "Network. Update shield-devices.json if the IP changed.")
            return "\n".join(lines), all_ready

        state = self.device_state()
        if state == "device":
            lines.append("ADB state: connected and authorized — ready.")
            model = self.settings_get("global", "device_name") \
                if self.is_connected() else None
            if model:
                lines.append("Shield reports its name as: {}".format(model))
        elif state == "unauthorized":
            all_ready = False
            lines.append(
                "ADB state: UNAUTHORIZED — the Shield is reachable but "
                "has not approved this laptop. Look at the TV: an RSA "
                "prompt should be showing. Accept it and tick 'always "
                "allow from this computer'. If no prompt shows, toggle "
                "Network Debugging off/on on the Shield and reconnect.")
        elif state == "offline":
            all_ready = False
            lines.append(
                "ADB state: OFFLINE — the Shield answered but the "
                "connection is stuck. Try `shield_adb.py connect` again, "
                "or toggle Network Debugging on the Shield.")
        else:
            lines.append(
                "ADB state: not connected yet (port answers, adb has not "
                "connected). Run `shield_adb.py connect` — the first "
                "connect triggers the RSA prompt on the TV.")
            ok, msg = self.connect()
            lines.append("Connect attempt: {}".format(
                "succeeded" if ok else "failed — " + msg))
            if not ok:
                all_ready = False
        return "\n".join(lines), all_ready

    def self_test(self):
        """One-shot pass/fail summary for a human or a Scout health card.
        Reports exactly what diagnostics found — no device, no pass."""
        report, ready = self.diagnostics()
        header = "Shield ADB self-test: {}".format(
            "PASS — Shield reachable and authorized" if ready
            else "NOT READY — see below")
        return header + "\n" + report, ready


# ----------------------------------------------------------------------
# CLI — thin wrapper so Scout (or Shawn) can drive everything above from
# a shell. Kept in this one file on purpose: a second shield_control.py
# would only re-export these same functions.
# ----------------------------------------------------------------------

def _pick_device(devices, name):
    if not devices:
        return None
    if name:
        for dev in devices:
            if dev.name == name:
                return dev
        return None
    return devices[0]


def _cli(argv=None):
    p = argparse.ArgumentParser(
        description="Drive the Shield TV over ADB (LAN, no root).")
    p.add_argument("--config", help="path to shield-devices.json")
    p.add_argument("--name", help="device name from the config (default: first)")
    p.add_argument("--ip", help="one-off device IP (overrides config)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("diagnostics", help="plain-language health report")
    sub.add_parser("self-test", help="PASS / NOT READY summary")
    sub.add_parser("discover", help="mDNS sightings + config reachability")
    sub.add_parser("connect", help="connect (with backoff) and report state")
    sub.add_parser("disconnect")
    sub.add_parser("init-config", help="write an example shield-devices.json")

    sp = sub.add_parser("install"); sp.add_argument("apk")
    sp = sub.add_parser("uninstall"); sp.add_argument("package")
    sp = sub.add_parser("launch"); sp.add_argument("package")
    sp = sub.add_parser("force-stop"); sp.add_argument("package")
    sp = sub.add_parser("keyevent"); sp.add_argument("key")
    sp = sub.add_parser("tap"); sp.add_argument("x", type=int)
    sp.add_argument("y", type=int)
    sp = sub.add_parser("swipe")
    for arg in ("x1", "y1", "x2", "y2"):
        sp.add_argument(arg, type=int)
    sp.add_argument("--duration", type=int, default=300)
    sp = sub.add_parser("type"); sp.add_argument("text", nargs="+")
    sp = sub.add_parser("screencap"); sp.add_argument("path")
    sp = sub.add_parser("ui-dump")
    sp.add_argument("--find-text", help="only print nodes matching this text")
    sp = sub.add_parser("settings-get")
    sp.add_argument("namespace", choices=SETTINGS_NAMESPACES)
    sp.add_argument("key")
    sp = sub.add_parser("settings-put")
    sp.add_argument("namespace", choices=SETTINGS_NAMESPACES)
    sp.add_argument("key")
    sp.add_argument("value")

    ns = p.parse_args(argv)

    if ns.cmd == "init-config":
        path = write_example_config(ns.config)
        print("Config ready at {} — edit the IP to match your Shield, "
              "then run `shield_adb.py diagnostics`.".format(path))
        return 0

    if ns.ip:
        device = DeviceConfig(ns.name or "shield", ns.ip, ns.port)
    else:
        device = _pick_device(load_config(ns.config), ns.name)
    if device is None:
        if ns.cmd == "discover":
            # Discovery is still useful with no config: show mDNS only.
            for name, service, endpoint in ShieldAdb.mdns_discover():
                print("{}  {}  {}".format(name, service, endpoint))
            print("No shield-devices.json found — run "
                  "`shield_adb.py init-config` and set the Shield's IP.")
            return 0
        print("No device configured. Run `shield_adb.py init-config`, "
              "edit the Shield's IP into shield-devices.json, and retry — "
              "or pass --ip.", file=sys.stderr)
        return 2

    adb = ShieldAdb(device)
    try:
        if ns.cmd == "diagnostics":
            report, ready = adb.diagnostics()
            print(report)
            return 0 if ready else 1
        if ns.cmd == "self-test":
            report, ready = adb.self_test()
            print(report)
            return 0 if ready else 1
        if ns.cmd == "discover":
            print(json.dumps(adb.discover(), indent=2))
            return 0
        if ns.cmd == "connect":
            ok, msg = adb.connect()
            print(msg)
            return 0 if ok else 1
        if ns.cmd == "disconnect":
            ok, msg = adb.disconnect()
            print(msg or "disconnected")
            return 0 if ok else 1
        if ns.cmd == "install":
            ok, msg = adb.install(ns.apk)
        elif ns.cmd == "uninstall":
            ok, msg = adb.uninstall(ns.package)
        elif ns.cmd == "launch":
            ok, msg = adb.launch(ns.package)
        elif ns.cmd == "force-stop":
            ok, msg = adb.force_stop(ns.package)
        elif ns.cmd == "keyevent":
            ok, msg = adb.keyevent(ns.key)
        elif ns.cmd == "tap":
            ok, msg = adb.tap(ns.x, ns.y)
        elif ns.cmd == "swipe":
            ok, msg = adb.swipe(ns.x1, ns.y1, ns.x2, ns.y2, ns.duration)
        elif ns.cmd == "type":
            ok, msg = adb.type_text(" ".join(ns.text))
        elif ns.cmd == "screencap":
            ok, msg = adb.screencap(ns.path)
        elif ns.cmd == "ui-dump":
            tree = adb.ui_dump()
            if ns.find_text:
                for node in adb.find(tree, text=ns.find_text):
                    print(json.dumps({
                        "text": node["text"],
                        "contentDesc": node["contentDesc"],
                        "resourceId": node["resourceId"],
                        "class": node["class"],
                        "clickable": node["clickable"],
                        "focused": node["focused"],
                        "center": node["center"],
                    }, indent=2))
            else:
                print(json.dumps(tree, indent=2))
            return 0
        elif ns.cmd == "settings-get":
            value = adb.settings_get(ns.namespace, ns.key)
            print(value if value is not None else "(not set)")
            return 0
        elif ns.cmd == "settings-put":
            ok, msg = adb.settings_put(ns.namespace, ns.key, ns.value)
        else:  # pragma: no cover - argparse restricts cmd
            return 2
        print(msg)
        return 0 if ok else 1
    except AdbError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_cli())
