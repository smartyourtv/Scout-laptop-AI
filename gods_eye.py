#!/usr/bin/env python3
"""
gods_eye.py — God's Eye data layer for laptop Scout.

Phase C (2026-10-16). God's Eye (approved 2026-10-15) is the van AI's
unified world view: on-demand, never 24/7. Scout answers most
God's Eye-capability questions FROM DATA ALONE — the 3D view loads
only when Shawn wants to SEE something. This module is the data side:

  * Feed client interfaces: OSM (offline, local), weather, traffic —
    lightweight calls, no GPU, no 3D view.
  * ADS-B client skeleton (OpenSky Network, free): "that plane
    overhead" → nearest aircraft to the GPS point: airline/flight,
    type, altitude, speed, heading.
  * AIS client skeleton (AISHub / MarineTraffic): "that boat in the
    bay" → nearest vessel. Coverage is PARTIAL — small private boats
    often don't broadcast AIS. Scout says so honestly, never guesses.
  * On-demand browser launch hook + God's Eye URL setting: the hosted
    version's URL is a SETTING, filled in when it launches (Monday
    watch tracks the launch). Show on laptop screen, or on the TV via
    Outpost (outpost_client.open_url).

Honest states everywhere: no API key / no network / feed down are
first-class answers ("I can't check that right now — no connection"),
never fabricated data. Offline, Scout answers from local data only
(OSM maps, GPS) and says that's what it's doing.

Stdlib only. Live feed calls happen only when a caller invokes them
with network available; nothing here runs in the background.
"""

import json
import math
import os
import subprocess
import sys
import urllib.request
import urllib.error

SETTINGS_PATH = os.path.expanduser("~/.scout/gods_eye.json")

DEFAULT_SETTINGS = {
    "gods_eye_url": "",          # SETTING — filled in at hosted launch
    "opensky_username": "",      # optional; anonymous works, rate-limited
    "opensky_password": "",
    "aishub_username": "",       # AISHub needs a (free) username key
    "weather_feed_url": "",      # setting; e.g. an NWS/Open-Meteo endpoint
    "traffic_feed_url": "",      # setting; provider chosen at install
    "browser": "",               # setting; empty = xdg-open default
    "tv_host": "",               # Shield IP for "show on TV" (Outpost)
}


def load_settings(path=None):
    path = path or SETTINGS_PATH
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update({k: v for k, v in data.items()
                       if k in DEFAULT_SETTINGS})
        return merged
    except (OSError, ValueError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings, path=None):
    path = path or SETTINGS_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    os.replace(tmp, path)


# ── geo helpers ─────────────────────────────────────────────────────

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ── feed clients (interfaces + skeletons, honest states) ────────────

class FeedResult:
    """status: ok | no_key | no_network | no_setting | error | offline"""

    def __init__(self, status, data=None, detail=""):
        self.status = status
        self.data = data
        self.detail = detail

    def __repr__(self):
        return f"FeedResult({self.status}, {self.detail})"


def _http_json(url, timeout=8, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class OsmClient:
    """Offline maps on the ThinkPad (OSM data rides the USB). Interface:
    geocode/route answers come from the local OSM stack at install time;
    off-device this honestly reports the local-data state."""

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.expanduser("~/scout/offline-data")

    def available(self):
        return any(f.endswith(".pbf") or f.endswith(".osm")
                   for f in (os.listdir(self.data_dir)
                             if os.path.isdir(self.data_dir) else []))

    def status(self):
        if self.available():
            return FeedResult("ok", detail=f"local OSM data in {self.data_dir}")
        return FeedResult("offline",
                          detail="No local OSM extract on this machine yet "
                                 "(lands via installer offline-data step). "
                                 "Offline map answers wait for the ThinkPad.")


class WeatherClient:
    def __init__(self, settings=None):
        self.settings = settings or load_settings()

    def current(self, lat, lon):
        url = self.settings.get("weather_feed_url", "")
        if not url:
            return FeedResult("no_setting",
                              detail="Weather feed URL is not set yet "
                                     "(setting: weather_feed_url).")
        try:
            data = _http_json(url.format(lat=lat, lon=lon))
            return FeedResult("ok", data=data)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return FeedResult("no_network", detail=f"Weather feed unreachable: {e}")
        except Exception as e:
            return FeedResult("error", detail=str(e))


class TrafficClient:
    def __init__(self, settings=None):
        self.settings = settings or load_settings()

    def conditions(self, lat, lon):
        url = self.settings.get("traffic_feed_url", "")
        if not url:
            return FeedResult("no_setting",
                              detail="Traffic feed URL is not set yet "
                                     "(setting: traffic_feed_url). Route "
                                     "answers fall back to OSM-only offline.")
        try:
            data = _http_json(url.format(lat=lat, lon=lon))
            return FeedResult("ok", data=data)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return FeedResult("no_network", detail=f"Traffic feed unreachable: {e}")
        except Exception as e:
            return FeedResult("error", detail=str(e))


class AdsBClient:
    """OpenSky Network (free). Anonymous access works but is
    rate-limited; credentials are optional settings. 'That plane
    overhead' = nearest state vector to the given GPS point."""

    BASE = "https://opensky-network.org/api/states/all"

    def __init__(self, settings=None):
        self.settings = settings or load_settings()

    def nearest_aircraft(self, lat, lon, radius_deg=0.5):
        lamin, lamax = lat - radius_deg, lat + radius_deg
        lomin, lomax = lon - radius_deg, lon + radius_deg
        url = (f"{self.BASE}?lamin={lamin}&lomin={lomin}"
               f"&lamax={lamax}&lomax={lomax}")
        headers = {}
        user = self.settings.get("opensky_username", "")
        if user:
            import base64
            pw = self.settings.get("opensky_password", "")
            token = base64.b64encode(f"{user}:{pw}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        try:
            data = _http_json(url, headers=headers)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return FeedResult("no_network",
                              detail=f"OpenSky unreachable (needs internet): {e}")
        except Exception as e:
            return FeedResult("error", detail=str(e))
        states = data.get("states") or []
        best, best_km = None, None
        for s in states:
            # OpenSky vector: [icao24, callsign, origin, time, last,
            # lon, lat, baro_alt_m, on_ground, velocity_mps, heading...]
            if s[5] is None or s[6] is None or s[8]:
                continue
            km = haversine_km(lat, lon, s[6], s[5])
            if best_km is None or km < best_km:
                best, best_km = s, km
        if best is None:
            return FeedResult("ok", data=None,
                              detail="No aircraft broadcasting ADS-B in "
                                     "that patch of sky right now.")
        return FeedResult("ok", data={
            "callsign": (best[1] or "").strip() or "unknown",
            "origin_country": best[2],
            "altitude_m": best[7],
            "speed_mps": best[9],
            "heading_deg": best[10],
            "distance_km": round(best_km, 1),
        }, detail="nearest ADS-B aircraft overhead")


class AisClient:
    """AIS via AISHub (free username key). Coverage is partial — small
    private boats often don't broadcast AIS, so 'no vessel found' must
    be reported as 'not broadcasting', never as 'nothing there'."""

    BASE = "http://data.aishub.net/ws.php"

    def __init__(self, settings=None):
        self.settings = settings or load_settings()

    def nearest_vessel(self, lat, lon, radius_deg=0.3):
        user = self.settings.get("aishub_username", "")
        if not user:
            return FeedResult("no_key",
                              detail="AISHub username not set (free key, "
                                     "setting: aishub_username). Without "
                                     "it I can't check boats — and small "
                                     "private boats often don't broadcast "
                                     "AIS anyway.")
        url = (f"{self.BASE}?username={user}&format=1&output=json"
               f"&compress=0&latmin={lat - radius_deg}&latmax={lat + radius_deg}"
               f"&lonmin={lon - radius_deg}&lonmax={lon + radius_deg}")
        try:
            data = _http_json(url)
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            return FeedResult("no_network",
                              detail=f"AISHub unreachable (needs internet): {e}")
        except Exception as e:
            return FeedResult("error", detail=str(e))
        return FeedResult("ok", data=data,
                          detail="raw AISHub response — field mapping is "
                                 "finalized on the ThinkPad with live data")


# ── on-demand view launch ───────────────────────────────────────────

def launch_view(settings=None, on_tv=False, opener=None):
    """Open God's Eye (on-demand only). Returns (ok, detail). The URL
    is a setting — empty until the hosted version launches, and that
    state is reported plainly instead of opening nothing silently
    (Build 1 UX rule: explain + feedback)."""
    settings = settings or load_settings()
    url = settings.get("gods_eye_url", "")
    if not url:
        return False, ("God's Eye URL is not set yet — the hosted "
                       "version hasn't launched (Monday watch tracks "
                       "it). I can still answer from data: maps, "
                       "weather, traffic, planes, boats.")
    if on_tv:
        host = settings.get("tv_host", "")
        if not host:
            return False, ("No Shield address set (setting: tv_host) — "
                           "can't show God's Eye on the TV yet.")
        try:
            sys.path.insert(0, HERE_DIR)
            from outpost_client import OutpostClient, OutpostError
            try:
                OutpostClient(host).power("wake")
            except OutpostError:
                pass  # waking is best-effort; opening is the ask
            OutpostClient(host).open_url(url)
            return True, f"God's Eye opening on the TV ({url})."
        except Exception as e:
            return False, (f"Couldn't reach Outpost on the Shield: {e}. "
                           "Fallback: open God's Eye in a browser app "
                           "on the Shield.")
    if opener is not None:
        opener(url)
        return True, f"God's Eye opening ({url})."
    browser = settings.get("browser", "")
    try:
        if browser:
            subprocess.Popen([browser, url])
        else:
            subprocess.Popen(["xdg-open", url])
        return True, f"God's Eye opening ({url})."
    except Exception as e:
        return False, f"Couldn't launch a browser here: {e}"


HERE_DIR = os.path.dirname(os.path.abspath(__file__))


def close_view(settings=None):
    return True, "God's Eye closed (on-demand view — nothing runs 24/7)."


# ── data-first answering facade ─────────────────────────────────────

class GodsEye:
    def __init__(self, settings=None):
        self.settings = settings or load_settings()
        self.osm = OsmClient()
        self.weather = WeatherClient(self.settings)
        self.traffic = TrafficClient(self.settings)
        self.adsb = AdsBClient(self.settings)
        self.ais = AisClient(self.settings)

    def plane_overhead(self, lat, lon):
        return self.adsb.nearest_aircraft(lat, lon)

    def boat_nearby(self, lat, lon):
        return self.ais.nearest_vessel(lat, lon)


# ── diagnostics + self-test ─────────────────────────────────────────

def diagnostics(settings=None):
    settings = settings or load_settings()
    ge = GodsEye(settings)
    lines = ["God's Eye — diagnostics",
             f"- View URL set: {'yes' if settings.get('gods_eye_url') else 'no — hosted launch pending (expected)'}",
             f"- OSM (offline): {ge.osm.status().detail}",
             f"- Weather feed: {'set' if settings.get('weather_feed_url') else 'not set (honest no_setting state)'}",
             f"- Traffic feed: {'set' if settings.get('traffic_feed_url') else 'not set (routes fall back to OSM-only)'}",
             f"- ADS-B (OpenSky): {'account set' if settings.get('opensky_username') else 'anonymous (works, rate-limited)'}",
             f"- AIS (AISHub): {'key set' if settings.get('aishub_username') else 'no key — boat answers report no_key honestly'}",
             "- Rendering: on-demand only, never 24/7 (no GPU contention "
             "with the brain)."]
    return "\n".join(lines)


def self_test():
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    import tempfile
    with tempfile.TemporaryDirectory(prefix="gods_eye_test_") as tmp:
        spath = os.path.join(tmp, "settings.json")
        s = load_settings(spath)
        check("default settings load (URL empty until launch)",
              s["gods_eye_url"] == "")
        s["gods_eye_url"] = "https://gods-eye.example/view"
        save_settings(s, spath)
        check("settings round-trip", load_settings(spath)["gods_eye_url"]
              == "https://gods-eye.example/view")
        opened = []
        ok, detail = launch_view(s, opener=opened.append)
        check("launch hook opens the set URL", ok and opened
              == ["https://gods-eye.example/view"], detail)
        ok2, detail2 = launch_view(load_settings(os.path.join(tmp, "none.json")))
        check("no URL → honest explanation, nothing opened",
              not ok2 and "hasn't launched" in detail2, detail2)
        check("haversine: ~111km per degree latitude",
              100 < haversine_km(38.0, -121.0, 39.0, -121.0) < 120)
        ais = AisClient(load_settings(spath))
        res = ais.nearest_vessel(38.0, -121.0)
        check("AIS without key → no_key (never fabricated)",
              res.status == "no_key", res.detail)
        wx = WeatherClient(load_settings(spath))
        check("weather without feed URL → no_setting",
              wx.current(38.0, -121.0).status == "no_setting")
        osm = OsmClient(data_dir=tmp)
        check("OSM without extract → offline state, not an error",
              osm.status().status == "offline")
    print("gods_eye self_test:", "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    print(__doc__)
