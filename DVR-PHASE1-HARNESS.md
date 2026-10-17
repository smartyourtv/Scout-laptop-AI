# DVR Backend — Phase 1 Harness (Phase C, 2026-10-16)

Companion to `DVR-BACKEND-TEST-PLAN.md`. The test plan says *what* must be
proven; this harness is the *runnable off-device part* of it, delivered in
`traccar_frigate.py`. Nothing here touches the van DVR. **Cutover stays
gated on Shawn's explicit go-ahead at the time.**

## What was built (off-device, this run)

| Piece | Where | State |
|---|---|---|
| Config generation | `traccar_frigate.py --generate` → `thinkpad/dvr-backend/` (`docker-compose.yml`, `traccar.xml`, `frigate-config/config.yml`) | Built + validated |
| Config validation | `python3 traccar_frigate.py --validate` (XML parse, YAML parse via PyYAML when present, `docker compose config` when docker exists — skipped honestly when it doesn't) | Built |
| Status / diagnostics | `python3 traccar_frigate.py --diagnostics` — ports 8082/5055/7017/5000/8554, Traccar `/api/health`, Frigate `/api/stats`, honest "not installed on this machine" states | Built |
| Self-test (smoke) | `python3 traccar_frigate.py --self-test` — generates into a temp dir, validates syntax, checks honest status reporting | Built, run on the build VM |

## Phase 1 proof RUN — waits for the ThinkPad

Run on the ThinkPad, in order (from the test plan — prove backend FIRST):

1. `cd thinkpad/dvr-backend && docker compose up -d`
2. **Traccar proof (no DVR):** install a phone GPS client (OsmAnd protocol,
   port 5055) on a phone, point it at the ThinkPad, walk/drive — position
   must appear in Traccar (http://scout-van.local:8082) and update.
3. **Frigate proof (no DVR):** replace the `test_stream` camera's
   placeholder path in `frigate-config/config.yml`
   (`rtsp://127.0.0.1:8554/test_stream_PLACEHOLDER`) with a real local
   test source (USB camera via go2rtc, or any known RTSP test stream) —
   live view + recording + snapshot must work at http://scout-van.local:5000.
4. Only when both pass: Phase 1b observational tests on the G2-WS spare
   (port scan, outbound traffic watch to 47.88.8.31, unauthenticated RTSP
   check, menu reads). Settings changes stay gated (G2-WS login forgotten;
   JOINLGO contacted).

## Phase 2 cutover — NOT part of this harness

Record all live-DVR settings → change server to Traccar → verify GPS +
video + alerts → any failure reverts to **47.88.8.31** immediately.
Requires Shawn's go-ahead at the time. Trade-off stands: CMSV7 app remote
viewing stops; if no RTSP exists, remote live video is gone until the AHD
capture path — GPS still moves, local recording keeps working.

## Pip deps

None required. PyYAML (already common) improves validation fidelity;
without it the validator falls back to structural checks and says so.
Docker + Docker Compose are needed on the ThinkPad for the proof run —
installed there, not by this module.
