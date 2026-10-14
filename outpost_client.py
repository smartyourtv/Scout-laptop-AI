#!/usr/bin/env python3
"""
Outpost client for van Scout (ThinkPad).

Lets the van AI talk directly to the Outpost companion app on the Shield
over the van LAN — no phone required. Outpost is just an HTTP server;
this module speaks its command protocol.

Protocol (mirrors the Scout Android app's OutpostCommander):
  GET  /status   -> {"version": "1.x", "device": "<model>"}
  GET  /apps     -> [{"name": "...", "package": "..."}, ...]
  POST /command  -> JSON body, always with an "action" key:
    {"action":"launch","package":"com.netflix.ninja"}
    {"action":"openUrl","url":"https://..."}
    {"action":"media","key":"play|pause|stop|next|previous"}
    {"action":"volume","direction":"up|down"}
    {"action":"setVolume","level":0..15}
    {"action":"dpad","key":"up|down|left|right|ok|back|home"}
    {"action":"power","state":"sleep|wake"}
    {"action":"type","text":"hello world"}
    {"action":"searchApp","package":"...","query":"..."}

Usage as a library:
    from outpost_client import OutpostClient
    tv = OutpostClient("192.168.1.50")
    tv.launch_app("com.netflix.ninja")
    tv.media("pause")

Quick CLI for testing:
    python3 outpost_client.py --host 192.168.1.50 status
    python3 outpost_client.py --host 192.168.1.50 launch com.netflix.ninja
    python3 outpost_client.py --host 192.168.1.50 apps
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

OUTPOST_PORT = 8087
STATUS_TIMEOUT = 3.0    # /status and /apps are quick probes
COMMAND_TIMEOUT = 5.0   # commands get a generous window (Wi-Fi hiccups)


class OutpostError(Exception):
    """The Shield couldn't be reached or refused the command."""


class OutpostClient:
    def __init__(self, host, port=OUTPOST_PORT, timeout=COMMAND_TIMEOUT):
        self.base = "http://{}:{}".format(host, port)
        self.timeout = timeout

    # ---- low level ----

    def _get(self, path):
        url = self.base + path
        try:
            with urllib.request.urlopen(url, timeout=STATUS_TIMEOUT) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raise OutpostError("Shield answered {} on {}".format(e.code, path))
        except urllib.error.URLError as e:
            raise OutpostError("Could not reach the Shield ({}): {}".format(path, e.reason))
        except (TimeoutError, OSError) as e:
            raise OutpostError("Could not reach the Shield ({}): {}".format(path, e))

    def _post(self, payload):
        url = self.base + "/command"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200]
            raise OutpostError(
                "Shield said no (HTTP {}){}".format(e.code, ": " + detail if detail else "")
            )
        except urllib.error.URLError as e:
            raise OutpostError("Could not reach the Shield: {}".format(e.reason))
        except (TimeoutError, OSError) as e:
            raise OutpostError("Could not reach the Shield: {}".format(e))

    # ---- queries ----

    def status(self):
        """Returns (version, device_name). Raises OutpostError if unreachable."""
        code, body = self._get("/status")
        try:
            info = json.loads(body)
            return info.get("version", "?"), info.get("device", "Shield")
        except (json.JSONDecodeError, AttributeError):
            return "?", "Shield"  # alive, but unexpected body

    def list_apps(self):
        """Returns [(name, package), ...]. Empty list if Outpost is too old."""
        try:
            code, body = self._get("/apps")
            return [(a.get("name", "?"), a.get("package", "?"))
                    for a in json.loads(body)
                    if a.get("package")]
        except OutpostError:
            return []
        except (json.JSONDecodeError, AttributeError, TypeError):
            return []

    # ---- commands ----

    def launch_app(self, package):
        """Launch any installed app by package name (sideloaded apps included)."""
        return self._post({"action": "launch", "package": package})

    def open_url(self, url):
        """Open a URL in Outpost's WebView (e.g. a God's Eye share-link view)."""
        return self._post({"action": "openUrl", "url": url})

    def media(self, key):
        """key: play | pause | stop | next | previous"""
        if key not in ("play", "pause", "stop", "next", "previous"):
            raise ValueError("media key must be play|pause|stop|next|previous")
        return self._post({"action": "media", "key": key})

    def volume(self, direction):
        """direction: up | down (one step)"""
        if direction not in ("up", "down"):
            raise ValueError("volume direction must be up|down")
        return self._post({"action": "volume", "direction": direction})

    def set_volume(self, level):
        """Absolute volume level, 0..15."""
        level = max(0, min(15, int(level)))
        return self._post({"action": "setVolume", "level": level})

    def dpad(self, key):
        """key: up | down | left | right | ok | back | home"""
        if key not in ("up", "down", "left", "right", "ok", "back", "home"):
            raise ValueError("dpad key must be up|down|left|right|ok|back|home")
        return self._post({"action": "dpad", "key": key})

    def power(self, state):
        """state: sleep | wake"""
        if state not in ("sleep", "wake"):
            raise ValueError("power state must be sleep|wake")
        return self._post({"action": "power", "state": state})

    def type_text(self, text):
        """Type into whatever field is focused on the Shield."""
        return self._post({"action": "type", "text": text})

    def app_search(self, package, query):
        """Ask an app to run its own search; falls back to opening the app."""
        return self._post({"action": "searchApp", "package": package, "query": query})


def _cli():
    p = argparse.ArgumentParser(description="Talk to Outpost on the Shield.")
    p.add_argument("--host", required=True, help="Shield IP on the van LAN")
    p.add_argument("--port", type=int, default=OUTPOST_PORT)
    p.add_argument("cmd", choices=[
        "status", "apps", "launch", "url", "media", "volume",
        "setvolume", "dpad", "power", "type", "search"])
    p.add_argument("args", nargs="*", help="command arguments")
    ns = p.parse_args()

    tv = OutpostClient(ns.host, ns.port)
    try:
        if ns.cmd == "status":
            ver, dev = tv.status()
            print("Outpost {} on {}".format(ver, dev))
        elif ns.cmd == "apps":
            for name, pkg in tv.list_apps():
                print("{}  ({})".format(name, pkg))
        elif ns.cmd == "launch":
            tv.launch_app(ns.args[0]); print("launched")
        elif ns.cmd == "url":
            tv.open_url(ns.args[0]); print("opened")
        elif ns.cmd == "media":
            tv.media(ns.args[0]); print("ok")
        elif ns.cmd == "volume":
            tv.volume(ns.args[0]); print("ok")
        elif ns.cmd == "setvolume":
            tv.set_volume(ns.args[0]); print("ok")
        elif ns.cmd == "dpad":
            tv.dpad(ns.args[0]); print("ok")
        elif ns.cmd == "power":
            tv.power(ns.args[0]); print("ok")
        elif ns.cmd == "type":
            tv.type_text(" ".join(ns.args)); print("typed")
        elif ns.cmd == "search":
            tv.app_search(ns.args[0], " ".join(ns.args[1:])); print("ok")
    except OutpostError as e:
        print("error: {}".format(e), file=sys.stderr)
        sys.exit(1)
    except (IndexError, ValueError) as e:
        print("usage error: {}".format(e), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    _cli()
