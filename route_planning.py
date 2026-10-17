#!/usr/bin/env python3
"""
route_planning.py — Scout-planned routes → Google Maps → BCPA9.

Phase C (2026-10-16). Approved design (ThinkPad spec §Route planning):
Scout plans the route from God's Eye data (live traffic when online) +
OSM maps on the ThinkPad, then hands it to Google Maps on the phone,
which Android Auto projects onto the BCPA9. Scout constrains Google
Maps with WAYPOINTS: a waypoint at every decision point pins the
planned route — Maps must route through waypoints in order.

Free URL path limits (the mechanism this module builds):
  * origin + destination + AT MOST 9 waypoints
  * avoid=tolls|highways|ferries when Shawn asks
  * travelmode=driving
No Directions API key needed. No full-polyline injection exists —
waypoints are the mechanism (documented limit, not a hack).

Offline fallback: no internet → Scout routes from OSM on the ThinkPad;
Google Maps navigates on downloaded offline maps if present. Live
traffic is unavailable offline — this module says so via the
traffic-check hook result instead of pretending.

The traffic-check hook is an interface: ThinkPad wiring passes the
God's Eye TrafficClient (gods_eye.TrafficClient) or any callable
(origin, destination) -> FeedResult-like. Off-device, the default hook
reports "no_setting" honestly.
"""

import sys
import urllib.parse

MAX_WAYPOINTS = 9
VALID_AVOID = ("tolls", "highways", "ferries")
MAPS_DIR_BASE = "https://www.google.com/maps/dir/"


class RouteError(ValueError):
    pass


def build_maps_url(origin, destination, waypoints=None, avoid=None):
    """Build a Google Maps directions URL.

    origin/destination/waypoints are address or "lat,lng" strings.
    At most 9 waypoints are used; extras raise RouteError (the caller
    — Scout's planner — must pick the 9 most important forks, per
    spec) rather than silently dropping pins that hold the route.
    avoid: iterable subset of {tolls, highways, ferries}.
    """
    if not origin or not str(origin).strip():
        raise RouteError("origin is required")
    if not destination or not str(destination).strip():
        raise RouteError("destination is required")
    waypoints = list(waypoints or [])
    if len(waypoints) > MAX_WAYPOINTS:
        raise RouteError(
            f"Too many waypoints: {len(waypoints)} > {MAX_WAYPOINTS}. "
            "Pick the 9 most important decision points (highway forks, "
            "entrances, key turns) — extra pins cannot be carried by "
            "the free Maps URL path.")
    avoid = list(avoid or [])
    bad = [a for a in avoid if a not in VALID_AVOID]
    if bad:
        raise RouteError(f"Unknown avoid values: {bad} "
                         f"(valid: {', '.join(VALID_AVOID)})")
    q = urllib.parse.quote(str(origin), safe=",")
    d = urllib.parse.quote(str(destination), safe=",")
    url = f"{MAPS_DIR_BASE}{q}/{d}"
    params = {"travelmode": "driving"}
    if waypoints:
        params["waypoints"] = "|".join(
            urllib.parse.quote(str(w), safe=",") for w in waypoints)
    if avoid:
        params["avoid"] = "|".join(avoid)
    return url + "/?" + "&".join(f"{k}={v}" for k, v in params.items())


def pin_decision_points(candidate_points, limit=MAX_WAYPOINTS):
    """Given more candidate decision points than the cap, keep the
    first, last, and an even spread between — deterministic, and the
    caller is told points were dropped (never silent). Returns
    (kept, dropped_count)."""
    points = list(candidate_points)
    if len(points) <= limit:
        return points, 0
    step = (len(points) - 1) / (limit - 1)
    kept = [points[round(i * step)] for i in range(limit)]
    # de-dup while preserving order (rounding can collide)
    seen, out = set(), []
    for p in kept:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out, len(points) - len(out)


class TrafficChecker:
    """Interface wrapper: wraps a callable or a gods_eye.TrafficClient.
    check() returns (status, detail) — status mirrors FeedResult:
    ok | no_setting | no_network | error."""

    def __init__(self, source=None):
        self.source = source

    def check(self, origin, destination):
        if self.source is None:
            return ("no_setting",
                    "No traffic source wired — route will be planned "
                    "from OSM only (offline behaviour). Live traffic "
                    "joins when the God's Eye traffic feed is set.")
        try:
            if callable(self.source):
                result = self.source(origin, destination)
            else:  # TrafficClient-like: conditions(lat, lon) — needs coords
                return ("error",
                        "TrafficClient needs coordinates; pass a "
                        "callable(origin, destination) hook instead.")
            status = getattr(result, "status", "ok")
            detail = getattr(result, "detail", "") or str(result)
            return status, detail
        except Exception as e:
            return "error", str(e)


def plan_route(origin, destination, waypoints=None, avoid=None,
               traffic_checker=None):
    """Plan + package a route for hand-off. Returns a dict:
    {url, waypoints_used, traffic: (status, detail), summary}.
    The phone-side piece (future app build) opens `url`; Android Auto
    projects it to the BCPA9."""
    kept, dropped = pin_decision_points(waypoints or [])
    url = build_maps_url(origin, destination, kept, avoid)
    checker = traffic_checker or TrafficChecker()
    t_status, t_detail = checker.check(origin, destination)
    summary_bits = [f"Route to {destination} via {len(kept)} pinned "
                      f"waypoint(s)"]
    if dropped:
        summary_bits.append(f"({dropped} candidate pin(s) dropped over "
                            f"the {MAX_WAYPOINTS}-waypoint cap)")
    if t_status == "ok":
        summary_bits.append(f"traffic checked: {t_detail}")
    else:
        summary_bits.append(f"traffic not checked ({t_status}): {t_detail}")
    return {"url": url, "waypoints_used": kept, "dropped": dropped,
            "traffic": (t_status, t_detail),
            "summary": ". ".join(summary_bits)}


# ── diagnostics + self-test ─────────────────────────────────────────

def diagnostics():
    return "\n".join([
        "Route planning — diagnostics",
        f"- Maps URL path: free dir URL, max {MAX_WAYPOINTS} waypoints "
        "+ origin + destination",
        f"- Avoid options: {', '.join(VALID_AVOID)}",
        "- Traffic hook: interface only off-device (no_setting is the "
        "honest default); ThinkPad wires gods_eye.TrafficClient.",
        "- Display: Google Maps on the phone → Android Auto → BCPA9. "
        "Scout launches the URL on the phone; it does not drive AA's UI.",
        "- Offline: OSM-planned route + phone's downloaded offline "
        "maps; no live traffic offline.",
    ])


def self_test():
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    url = build_maps_url("Sacramento, CA", "Lake Tahoe, CA")
    check("basic URL builds",
          url.startswith(MAPS_DIR_BASE) and "travelmode=driving" in url, url)
    url9 = build_maps_url("A", "B", waypoints=[f"W{i}" for i in range(9)],
                          avoid=["tolls", "ferries"])
    check("9 waypoints + avoid accepted",
          url9.count("W") >= 9 and "avoid=tolls|ferries" in url9, url9)
    try:
        build_maps_url("A", "B", waypoints=[f"W{i}" for i in range(10)])
        check("10th waypoint raises (cap is real)", False)
    except RouteError:
        check("10th waypoint raises (cap is real)", True)
    try:
        build_maps_url("A", "B", avoid=["bridges"])
        check("unknown avoid raises", False)
    except RouteError:
        check("unknown avoid raises", True)
    try:
        build_maps_url("", "B")
        check("empty origin raises", False)
    except RouteError:
        check("empty origin raises", True)
    kept, dropped = pin_decision_points([f"P{i}" for i in range(20)])
    check("pin spread keeps 9, reports 11 dropped",
          len(kept) == 9 and dropped == 11, f"kept={kept} dropped={dropped}")
    kept2, dropped2 = pin_decision_points(["only"])
    check("under-cap pins pass through", kept2 == ["only"] and dropped2 == 0)
    plan = plan_route("Sacramento, CA", "Reno, NV",
                      waypoints=["Auburn, CA"])
    check("plan_route packages URL + honest traffic state",
          plan["url"].startswith(MAPS_DIR_BASE)
          and plan["traffic"][0] == "no_setting", str(plan))
    enc = build_maps_url("38.58,-121.49", "39.32,-120.18")
    check("lat,lng coordinates survive quoting",
          "38.58,-121.49" in enc and "39.32,-120.18" in enc, enc)
    print("route_planning self_test:",
          "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    print(__doc__)
