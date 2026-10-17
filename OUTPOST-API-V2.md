# Outpost API v2 — versioned contract

Status: implemented in the Outpost Android module (Phase A, 2026-10-16).
**Compile status: NOT yet compiled** — written while Build 1 owned Gradle;
first build must still pass the standing pre-build audit. Treat this doc as
the contract the code was written to; if the first build forces a change,
update this doc in the same commit.

Base URL: `http://<shield-ip>:8087` (plain HTTP, **trusted LAN only** —
never port-forward). The Shield advertises itself via mDNS as service type
`_outpost._tcp`, name `Outpost-<model>`, with TXT records `device`,
`model`, `manufacturer`, `api=2`, `appVersion`, `pkg`.

## Versioning & negotiation

- v1 (legacy, unchanged): `GET /status`, `GET /apps`, `POST /command`.
  **Unauthenticated** — kept so existing clients (Build 1 phone app,
  laptop `outpost_client.py`) keep working. New work must use v2; v1 will
  be token-gated or retired in a later phase, with client migration first.
- v2: all paths under `/v2/`. Clients should call `GET /v2/status` first
  and gate features on its `capabilities` list — never assume.

## Auth

Every `/v2/*` request requires the header:

```
X-Outpost-Token: <pairing token>
```

- The token is generated on the Shield at first run (48 hex chars,
  SecureRandom) and shown in full on the Outpost main screen ("Pairing
  code for Scout (v2)"). The user reads it off the TV and enters it into
  the client once; clients store it locally (never commit it to a repo).
- Comparison is constant-time on the device.
- Missing/wrong token → `401` with the standard error shape (below).
  The check runs before routing: unknown `/v2/*` paths without a token
  also return 401.
- The token is never logged by the app and never leaves the device except
  in this header. Uninstalling Outpost wipes it; a reinstall pairs fresh.

## Error shape (all v2 endpoints)

```json
{ "ok": false, "error": "<machine_code>", "message": "<plain language for the user>" }
```

HTTP codes: `200` ok · `400` bad request / refused action · `401`
unauthorized · `404` unknown endpoint, or node gone (`error` field says
which) · `501` unsupported on this device · `503` a needed on-device
helper is off or a capture failed (`error` field says which).

Machine codes in use: `bad_json`, `missing_node_id`,
`node_not_found_or_not_clickable`, `missing_coordinates`, `tap_failed`,
`swipe_failed`, `missing_action`, `unknown_or_failed_action`,
`nav_service_off`, `no_active_window`, `unsupported_api_level`,
`secure_window`, `rate_limited`, `screenshot_failed`,
`screenshot_timeout`, `unauthorized`.

## Endpoints

### GET /v2/status
Capability negotiation. No body.

```json
{
  "ok": true, "apiVersion": 2,
  "app": "outpost", "appVersion": "1.5",
  "package": "com.app.assistant.outpost",
  "device": { "manufacturer": "NVIDIA", "model": "SHIELD Android TV", "apiLevel": 30 },
  "capabilities": ["status", "ui-tree", "click-node", "global",
                   "setup-status", "tap", "swipe", "screenshot", "mdns"]
}
```

`capabilities` is device-dependent: `tap`/`swipe` appear only when the
navigation helper (AccessibilityService) is enabled; `screenshot` only
when it is enabled **and** API ≥ 30. Absence means "don't offer it",
not "broken".

### GET /v2/setup-status
Same data the Outpost main screen checklist shows (single source:
`SetupStatus.kt`).

```json
{
  "ok": true, "apiVersion": 2,
  "accessibilityEnabled": true,
  "navServiceRunning": true,
  "overlayGranted": false,
  "installAllowed": true,
  "networkDebugging": "unknown_on_device_check_from_laptop",
  "device": { "manufacturer": "...", "model": "...", "device": "...",
              "androidRelease": "11", "apiLevel": 30,
              "package": "com.app.assistant.outpost", "appVersion": "1.5" },
  "capabilities": [ "..." ]
}
```

Field notes for consumers (including the Universal Outpost setup wizard,
whose step keys are `accessibility` / `overlay` / `install` / `adb`):
- wizard `accessibility` ⇐ `accessibilityEnabled`
- wizard `overlay` ⇐ `overlayGranted`
- wizard `install` ⇐ `installAllowed`
- wizard `adb` ⇐ `networkDebugging` — an app cannot read the Shield's
  Network Debugging state; the string value is always
  `unknown_on_device_check_from_laptop`. Verify ADB from the laptop with
  `shield_adb.py diagnostics` instead.

### GET /v2/ui-tree
Accessibility tree of the active window (requires the navigation helper).

Response (truncated here for readability):

```json
{
  "ok": true, "apiVersion": 2,
  "nodeCount": 42, "truncated": false,
  "focusedPackage": "com.netflix.ninja",
  "tree": {
    "id": "0",
    "text": null, "contentDescription": null,
    "className": "android.widget.FrameLayout",
    "viewIdResourceName": null, "packageName": "com.netflix.ninja",
    "bounds": { "left": 0, "top": 0, "right": 1920, "bottom": 1080,
                "width": 1920, "height": 1080, "centerX": 960, "centerY": 540 },
    "clickable": false, "longClickable": false,
    "focusable": false, "focused": false, "accessibilityFocused": false,
    "selected": false, "checkable": false, "checked": false,
    "scrollable": false, "editable": false,
    "enabled": true, "visibleToUser": true,
    "children": [ { "id": "0/0", "...": "..." } ]
  }
}
```

Node fields: `text`, `contentDescription` are `null` (not `""`) when
absent. `bounds` are screen pixels; `centerX/centerY` are the tap point
if a gesture fallback is needed.

**Node-id scheme:** a node's `id` is its child-index path from the root:
root = `"0"`, its child #2 = `"0/2"`, that child's child #1 = `"0/2/1"`.
Ids are **snapshot-scoped**: they identify a node in the tree you just
fetched. If the screen changes, ids can point elsewhere — on a
`node_not_found_or_not_clickable` error, re-fetch the tree; do not retry
the same id blindly.

**Caps:** at most 2,000 nodes / depth 64; `truncated: true` means the
caps cut the tree (the visible, focusable part of a TV screen is
practically never near this).

**Privacy:** the tree contains on-screen text. It is returned only to the
token holder and is never logged or stored by Outpost. Clients must treat
it the same way (no logging screen text).

### POST /v2/click-node
```json
{ "nodeId": "0/2/1" }
```
Clicks that node, or its nearest clickable ancestor (TV OK semantics).
→ `200 {"ok":true,"apiVersion":2,"nodeId":"0/2/1"}` or 404 error shape.

### POST /v2/tap
```json
{ "x": 960, "y": 540 }
```
`dispatchGesture` tap at screen pixels. TV caveat: a tap is a touch, not
a focus move; focus-driven TV UIs may ignore it. Prefer click-node;
tap is the fallback (and the primary path on phone-OS boxes).

### POST /v2/swipe
```json
{ "x1": 960, "y1": 800, "x2": 960, "y2": 300, "durationMs": 300 }
```
`durationMs` optional (default 300, clamped 50–5000).

### POST /v2/global
```json
{ "action": "home" }
```
Actions: `home`, `back`, `recents`, `notifications`, `quickSettings`.

### GET /v2/screenshot
One frame of the default display (API 30+; Shield on Android 11 qualifies).

```json
{ "ok": true, "apiVersion": 2, "format": "png", "encoding": "base64",
  "image": "<base64 PNG, no line wraps>" }
```

Failures: `secure_window` (FLAG_SECURE screens — passwords, DRM video —
cannot be captured; expect black/failed captures of protected video in
ADB screencap too), `rate_limited` (platform throttles screenshots —
wait and retry once), `screenshot_timeout`, `screenshot_failed`.
Screenshots are single-shot; there is no streaming endpoint (use scrcpy
over ADB for live mirror — see phone-parity note).

## Phone-parity note (for Build 1, when it consumes v2)

Design rules the phone UI should follow (decided in the Shield deep-dive,
2026-10-15):

1. **Element-list-first UI.** The phone's Shield screen should be built on
   `/v2/ui-tree`: show the on-screen elements as a tappable list (text /
   description / focused state), and tap = `/v2/click-node`. This works
   with gloves, from another room, and without looking at the TV.
2. **Mirror on demand, not by default.** A "see the TV" button fetches
   `/v2/screenshot` (single frame, refresh on tap). No continuous mirror
   over HTTP — for a live mirror, the laptop path is scrcpy over ADB.
3. **D-pad fallback stays.** Keep the existing v1 `dpad` commands in the
   UI for apps whose accessibility tree is empty (games, some video
   players, WebView canvases). If ui-tree returns few/no nodes, the UI
   should fall back to D-pad + `/v2/global` rather than showing a dead
   screen.
4. **ADB relay via laptop.** Things Outpost can never do (install APKs,
   change system settings, read logs) go through the ThinkPad:
   phone → laptop Scout → `shield_adb.py` (ADB over LAN) → Shield.
   The phone never speaks ADB directly.

## Security summary

Plain HTTP + bearer-style token on a trusted LAN. The token stops casual
LAN access to the screen-aware controls (tree/screenshot/click); it is
not transport security. v1 remains unauthenticated by design during
migration (accepted risk, LAN-only, same as the shipped baseline).
Never expose port 8087 to the internet; never log the token, tree text,
or screenshots on any client.
