# ThinkPad Build — PREP Status

**Prep run: Fri 2026-10-16 (started early per Shawn: "Begin now instead of tomorrow").**
Scope: PREP ONLY. No full pull-it-together, no install/test phase, and **no shared
voice/emotion/protocol code** — that is gated on phone-app lessons from Build 1
(Scout-first plan: Phone app → Laptop → Nuri full).

## Change-impact audit (done before changes)

- **Blast radius:** `usb-prep.py`, `scout-installer.py`,
  `files/scout-thinkpad-home-spec.md`, `thinkpad/van-knowledge-base.md` (count fix),
  + 2 new docs. No phone-app code touched. No shared voice/emotion/protocol code touched.
- **Regression risk:** knowledge manifests in usb-prep.py and scout-installer.py are a
  synced pair — the parts-DB entry was added to BOTH. Installer knowledge step gained a
  JSON-validation branch for `.json` entries (PDF branch untouched).
- **Behavior change (intentional):** previously, unimplemented installer/usb-prep steps
  logged a TODO and were marked "done" by the UI — a silent failure. They now raise a
  `PREP STUB` error and fail loudly. This means neither tool runs end-to-end until
  pull-it-together, which is the truth.
- **Rollback:** all changes are in the local git working tree of `thinkpad/`
  (uncommitted, as before); revert per-file if needed. No data migrated.

## Completed this prep run

1. **Parts-interchange DB wired in** (was: spec pointed to the DB, scripts ignored it).
   - DB verified: `parts-interchange-db.json` = 697 entries (541 VERIFIED, 156 CANDIDATE).
   - usb-prep.py: DB added to the knowledge manifest + `step_copy_installer` stages it
     from `thinkpad/` into `scout-files/knowledge/` on the USB.
   - scout-installer.py: DB added to the installer's manifest; Knowledge step copies it
     to `~/scout/knowledge/parts-interchange-db.json` and verifies it parses with all
     entries present.
   - Spec: "Installer wiring" line added under Parts interchange.
   - van-knowledge-base.md header count corrected 480 → 697.
2. **Stub steps made honest** in both scripts (see audit above): usb-prep
   format/bootable/downloads/verify + installer Scout-brain/downloads/services/self-test
   now fail loudly as PREP STUBs. Installer AI-models step: vision-model copy is real,
   but it now raises after vision verification because the main-model copy is not
   implemented (previously reported success with the brain missing).
3. **DVR backend test plan documented**: `thinkpad/DVR-BACKEND-TEST-PLAN.md`
   (Phase 1 prove Traccar with phone GPS + Frigate with test stream; Phase 1b
   observational tests on G2-WS — port scan, traffic watch, unauth stream check,
   menu reads; settings-change gate; Phase 2 cutover with rollback to 47.88.8.31;
   fallbacks). Spec Cameras bullet now points to it.
4. **ALDL via Bluetooth**: prep checklist added to the spec (ALDL-specific SPP adapter,
   NOT OBD2/ELM327; ThinkPad priority arbitration; ADX file needed for TunerPro +
   ALDLdroid; van-systems-watch reads this feed).
5. **Deterrence spec**: verified current in the ThinkPad spec (approved 2026-10-15
   design, Bluetooth TWS speakers + keep-alive, no BCPA9, horn backburner) — no changes needed.
6. **God's Eye + route planning specs**: verified current in the ThinkPad spec
   (data-first answering, on-demand rendering, waypoint-pinned Google Maps handoff) — no changes needed.
7. **Theft-recovery decoy**: summary + pointer to `files/scout-theft-recovery-spec.md`
   added to the ThinkPad spec (it previously appeared only as a deterrence hand-off line).

## Verification (this run)

- `python3 -m py_compile` on both scripts: PASS.
- Parts-DB JSON validation logic exercised against the real DB: 697 entries parse.
- USB knowledge-manifest check simulated against the local build tree: all manifest
  files present at/above minimum size, incl. the newly wired parts DB.

## Remaining for FULL build (gated — do not start)

- usb-prep: USB detection, format/partition, bootable-ISO write, ~300GB downloads, final verify.
- installer: Scout-brain copy — **includes shared voice/emotion/protocol code, gated on
  phone-app lessons** — main-model (Qwen3.6-35B-A3B) copy, Kiwix/OSM copy, systemd
  services, self-test.
- DVR: Phase 1 backend proof + G2-WS observational tests (run at pull-it-together;
  settings-change tests gated on JOINLGO reply or Shawn's explicit go-ahead).
- ALDL: find a purchasable ALDL Bluetooth adapter (Amazon is OBD2-dominated);
  obtain the ECM's ADX file.
- Install/test phase requires the ThinkPad itself; prep did not.

## Blockers

- G2-WS Admin password: forgotten; JOINLGO contacted — no reply recorded yet.
  Observational tests unaffected.
- ALDL adapter sourcing + ADX file: open (see above).
- Full build gate: phone app Build 1 lessons must land first (by design, not a failure).
