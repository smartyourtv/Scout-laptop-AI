# DVR Backend Test Plan — JOINLGO → Self-Hosted (Traccar + Frigate)

**Status: DESIGN / PREP ONLY (2026-10-16).** Tests run during the ThinkPad
pull-it-together build, which is gated on phone-app lessons (Scout-first plan).
Switch approved by Shawn 2026-10-16: "Switch it to the self-hosted backend."
Rule: **prove the backend FIRST, cut over SECOND.**

## Units

| Unit | Role | Login |
|---|---|---|
| Van DVR — JOINLGO 4CH, Code **J2-4GW-AF**, 12V/24V (installed, live) | The working security system. Observational only until cutover. | Admin password **KNOWN** (Shawn has it) |
| Spare DVR — 4CH Mobile DVR, Code **G2-WS**, 8-36V | Test target (more similar to van unit). Powered + on network since 2026-10-16. | Admin password was reset + forgotten, but **JOINLGO replied 2026-10-16 (19:05 PDT)**: menu login via the **"super" account**, password provided to Shawn via his Amazon seller messages (**value deliberately NOT stored in any file**). **Observational only until Shawn verifies the super login works on the spare** — then settings-change tests are unlocked (see gate below). |

Both are provisioned to CMSV7 server **47.88.8.31**.
Do NOT publish or repeat label credentials / IMEI anywhere.

## What the test unit needs

- Powered on (main power **and** YELLOW ACC wire) + on the network. **Done 2026-10-16 for G2-WS.**
- SD card inserted, SD door latched (unlatched door can stop power-on).
- **No cameras needed** for any test below. Cameras only matter later, to confirm a
  stream carries real video — one camera is enough then.
- For menu checks: a display. A spare Boss BCPA10 works as the monitor via its
  **A/V input** (any RCA cable, DVR video-out → BCPA10 A/V video-in). The BCPA10's
  light-green parking-brake wire must be grounded (battery negative or the head
  unit's black ground wire) or it blocks video with the safety warning.
  Touchscreen does not control the DVR — menu needs the DVR's own remote/buttons.

## Phase 1 — Prove the backend (NO DVR changes)

Goal: Traccar + Frigate proven working on the ThinkPad with non-DVR sources,
so the live DVR is never the first test subject.

1. **Traccar** installed on ThinkPad; proven with a **phone GPS client**
   (position appears in Traccar, updates while moving).
2. **Frigate** installed on ThinkPad; proven with a **test stream**
   (any known RTSP test source / local camera) — live view + recording work.
3. Only when both pass does Phase 2 become eligible — and only with Shawn's
   explicit go-ahead at the time.

## Phase 1b — Observational tests on the G2-WS spare (no login needed)

1. **Port scan** the spare's LAN IP: look for 554 (RTSP), 80/8080 (local web),
   JT808 listener behaviour, any other open services. Record every open port.
2. **Outbound traffic watch**: does the unit connect to 47.88.8.31? On what
   port/protocol? (Tells us what a re-point would have to speak.)
3. **Unauthenticated stream check**: try RTSP URLs on any open 554 port
   without credentials; note result either way.
4. **Menu checks (display only, no changes)**: is there a server-address
   field? RTSP / local-web toggles? Protocol selection (JT808)?
   Reading menus needs no password change; *changing* settings does — see gate.

**Settings-change gate:** re-pointing / protocol changes need a menu login.
- **JOINLGO replied 2026-10-16 (19:05 PDT)** — after first answering with the
  CMSV7 platform account (17:41 PDT, a misunderstanding of the request), they
  clarified the DVR *menu* login: use the **"super" account**; the password
  was provided to Shawn in his Amazon seller messages and is **not stored in
  any file/report/memory**.
- **Status: settings-change tests (server re-pointability, protocol changes)
  are READY to run on the G2-WS spare as soon as Shawn confirms the super
  login works on the unit.** No agent attempts the login (no value held here,
  no LAN access).
- Only if the super login turns out not to work does the old fallback apply:
  settings tests on the **live van DVR only with Shawn's explicit go-ahead**
  (risk: disturbing the working security system). Default is NO. The Phase 2
  cutover gate is unchanged — it still needs Shawn's explicit go-ahead at
  the time.

## Platform + local path status — 2026-10-16 evening (Shawn-invited poke-around)

**Platform path (CMSV7 server 47.88.8.31): NOT COMPLETED — no login was submitted.**
Shawn provided platform credentials Oct 16 for a single normal login attempt
(credentials are transient — never stored in any file; they live only in the
chat message he sent). One fetch of the vendor-pattern `808gps` login page on
that server was attempted from the agent VM and was **blocked by the browser
tool's domain policy for bare-IP addresses** — the login page never loaded, so
no username/password was ever sent and the credentials are **neither confirmed
nor rejected**. Not retried (policy denial is a hard stop; no bypass via other
tools). What would complete this test: Shawn (or any normal browser on his
phone/PC) opens the CMSV7 portal for 47.88.8.31, signs in with the credentials
he sent Oct 16, and reports/screenshots only: does the G2-WS spare show
online, its status, and any GPS position shown. The CMSV7 phone app with the
same account is an equally valid surface. **These platform credentials are
NOT the G2-WS OSD Admin password** — that password is different and was
forgotten; JOINLGO has since replied with the **"super" account menu login**
(see the settings-change gate above — password held by Shawn only, stored
nowhere here). Platform login (if it works) does not itself unlock local
settings changes; settings changes ride on the super-account login once
Shawn verifies it on the spare.

**Local path: NOT RUN — no local address, no LAN vantage. Nothing claimed.**
We still have no 192.168.x.x address for the G2-WS spare, and the agent VM is
not on the van/home LAN (the paired phone exposes no LAN-scan command), so no
port scan has been run and no local results exist. Ready to run the moment
BOTH exist — (a) the spare's local IP (from the router's client list, the
CMSV7 app's device details, or the DVR's own network menu on a BCPA10
monitor) and (b) a LAN-side machine to run from (ThinkPad when installed, or
Shawn's home PC on the same network).
**Update 2026-10-16, 19:32 PDT:** Shawn confirmed the CMSV7 web portal DOES
load from his phone — http://47.88.8.31/808gps/login.html ("Active Security
Cloud Platform," after Chrome's "not secure" interstitial; login has a
4-digit CAPTCHA field; footer: platform version 7.37.2_20260710). So the
portal is alive and only the agent-browser route is blocked. Shawn logging
in himself + reporting whether the G2-WS spare shows online is the working
platform-check path. (Do NOT tell JOINLGO the portal is down — it isn't.)
1. `nmap -sV -p 554,80,8080,808gps-range <spare-ip>` — full: `nmap -sV <spare-ip>`
   (record every open port; 554 = RTSP candidate, 80/8080 = local web).
2. RTSP probe on any open 554: `ffprobe rtsp://<spare-ip>/` plus the common
   vendor path variants — unauthenticated first, result recorded either way.
3. Outbound watch from the router/PC: does the spare hold a connection to
   47.88.8.31, on which port (the re-point target protocol).
4. Menu reads via BCPA10 A/V monitor (no changes): server-address field?
   RTSP/local-web toggles? JT808 protocol selection?
Phase C's DVR harness (traccar_frigate.py, in the expanded-queue build)
covers the Phase 1 backend proof independently of these DVR-side unknowns.

## Phase 2 — Cutover (live van DVR, only after Phase 1 passes + go-ahead)

1. Record **all** current settings first (server 47.88.8.31 + everything else) —
   the recorded settings are the rollback.
2. Change server address to the self-hosted Traccar.
3. Verify: GPS position in Traccar, video in Frigate (if streams exist), alerts.
4. **Any failure → revert server to 47.88.8.31 immediately.**

**Trade-off (told to Shawn, accepted):** the switch *replaces* CMSV7 — the
vendor app's remote viewing stops. If the DVR exposes no RTSP, remote live
video is gone until the AHD capture path exists; GPS still moves to Traccar
and local recording keeps working regardless.

## Fallbacks if tests fail

- No RTSP / no re-pointable server → DVR stays a **local-only recorder**
  (recording/playback/USB backup survive any vendor failure). Eventual
  migration path: AHD capture card + PC, or a replacement AHD DVR.
  Cameras + wiring are standard AHD on 4-pin aviation connectors and are
  reusable with any AHD DVR/capture card — they are the durable asset.
- JT808 to Traccar unverified until tested (protocol variant + whether the
  server address is re-pointable are the two unknowns).

## Known unknowns (do not guess)

- RTSP output: **UNVERIFIED** for this DVR class (spec lists no RTSP server;
  ONVIF mentions in this class usually mean IP-camera *ingest*, not output).
- JT808 dialect spoken by JOINLGO units: unverified.
- Whether the server address is a changeable menu field: the separate
  brighter-white server sticker on the label suggests provisioning, not
  hard-coding — plausible, not proven.
