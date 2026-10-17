# Scout's Home — ThinkPad Spec (DRAFT — brainstorming)

## The machine
- ThinkPad P1 Gen 5 — 16GB VRAM GPU, 32GB DDR5 (one slot free), Ubuntu 24.04 LTS
- **Role:** Scout's home ~95% of the time. Shawn's occasional browsing/minor use — a guest, not the owner.
- **Power:** van's 500Ah LiFePO4 bank. Power efficiency is NOT the priority; responsiveness is.

## Design principles
1. **Scout owns the machine by default.** Human desktop is a mode you enter, not the baseline.
2. **Latency is the metric.** Voice is real-time; every 100ms of pipeline delay is felt.
3. **Everything supervised.** Every stage is a systemd service: auto-restart, health checks, watchdog. No silent deaths.
4. **No fragility in the voice path.** If the LLM is down, Scout still hears and says so — the pipeline degrades, it doesn't vanish.
5. **Mirror the phone app globally.** The laptop Scout is the same Scout as the Android app — one assistant, two bodies. Every behavior, fix, and refinement that lands in the app gets ported to the laptop wherever it applies (different code, same behavior). The app is the reference implementation; the parity checklist below is kept current, and nothing ships on the laptop behaving worse than the phone in an area the checklist covers.

### Future-proofing rules (standing — added 2026-10-14, Shawn: "bake these in")
Every design choice must survive its own dependencies failing. A single hidden dependency with no fallback is a future breakage.
1. **Bundle, don't fetch.** Everything the van needs rides on the USB / lives on the device. Install and runtime never depend on a live download.
2. **Local-first, cloud as enhancement.** The van works fully offline. Groq/cloud only add capability, never required.
3. **Versioned contracts.** The app↔laptop protocol carries a version number. Old client + new server negotiate instead of hard-failing on mismatch.
4. **Pin everything.** Model versions, dependency versions, API versions. Never pull "latest" at install time.
5. **Snapshot + self-test + rollback on every update.** Applies to stack updates, app updates, and model swaps — snapshot first, health self-test after, rollback on failure. Never auto-update mid-drive.
6. **Graceful degradation tiers.** Every feature has fallbacks (e.g., interpreter cascade: van → Groq → on-device). Nothing has a single point of failure.
7. **Identity decoupled from infrastructure.** Names are settings; connections use device IDs + a stable network address (`scout-van.local`). Renaming never breaks anything.
8. **Nothing hard-coded.** URLs, ports, limits, names — all settings.
9. **Diagnostics everywhere.** Every service gets a plain-language health card + one-tap self-test, so breakage shows up immediately instead of becoming a mystery.
10. **Home PC is staging.** Nothing reaches the van until it already works on the home PC.
11. **Backup before change.** Personality, memory, and database backed up before any update, with one-tap restore.
12. **Scoped credentials with a reconnection path.** Each token has minimal permissions and is documented; when one dies, the refresh path gets it back without bricking updates.
13. **Public/private separation.** No secrets in public repos, ever. Private repos hold the sensitive stuff.

### Build discipline — minimize bugs and conflicts (standing — added 2026-10-16, Shawn)
This build is big. Complexity is where bugs and conflicts breed, so the build fights complexity directly:
1. **One stack per job.** One serving runtime (llama.cpp), one audio system (PipeWire), one automation layer. Never run two tools that do the same job — the Ollama-vs-llama.cpp vision catch (2026-10-16) is the example: a second runtime would have meant a second failure surface plus a crashing model. When a new need appears, the first question is "does something already here do this?"
2. **Resource ownership map.** Every shared resource has exactly one owner. Nothing grabs a port, the GPU, or the audio device without being on this map. New service = new row in this map before it ships.

| Resource | Owner | Rule |
|---|---|---|
| Port 8080 | Main brain (llama-server) | Main model only |
| Port 8081 | Vision (llama-server) | Vision model only, only during a swap |
| GPU / 16GB VRAM | One model at a time | Swap, never coexist — scout-vision.py enforces it. GPU-heavy creative jobs (ComfyUI/video) queue behind voice: voice always wins the GPU |
| Mic + speakers | Scout in Scout mode; Shawn in Shawn mode | Scout yields audio in Shawn mode; never both |
| `~/scout/models/` | Installer | Only the installer writes here |
| `~/scout/knowledge/` | Libraries (first aid, troubleshooting, manuals, meds) | Only curated library files; no module writes here at runtime |
| `~/scout/memory/` | Memory system | Only the memory system writes here |
| Van Wi-Fi / Tailscale | Network services | LAN/Tailscale-only; no public exposure |

3. **Install order + verify after every step.** The installer already fails fast per step — extend that to verification: each step proves it works (model loads, service answers health check, audio loopback passes) before the next step starts. No step proceeds on a failed verification, ever.
4. **One change at a time in production.** Never stack two untested changes on the van. Change → test → next change. If two changes interact, that's a design failure to fix first.
5. **Minimal surface.** Install only what's needed. No extra services, no extra ports, no extra background daemons. Default-deny: a port is closed unless this spec opens it.
6. **Contract-first between modules.** talk.py, scout-vision.py, outpost_client, name_sync, and every skill talk through documented, versioned interfaces. No module reaches into another module's internals or files. If the interface changes, the version bumps.
7. **Audits are part of the build, not extra.** Change-impact audit before implementing any change; pre-build audit before every build (both already standing). Neither replaces on-device testing + the diagnostics card.
8. **Staging gate.** Home PC first, van second — nothing reaches the van untested (future-proofing rule 10, restated here because it is the single highest-leverage bug filter).
9. **Deterministic builds.** Pinned versions, no "latest", no ambient auto-updates. The same installer run on the same inputs produces the same system.
10. **No silent failures.** Every service logs to one place with timestamps. A failure that isn't logged is treated as a bug in the logging, not just in the service.

## OS layer
- **Minimal install.** No GNOME. Lightweight window manager at most; Scout runs headless by default.
- **Two modes:**
  - *Scout mode* (default at boot): no desktop, just the service stack. Lowest RAM/CPU footprint, fastest boot.
  - *Shawn mode* (on demand): starts a lightweight desktop session for browsing/minor tasks. Scout quiets itself — stops active listening or drops to low priority, yields the audio device.
- **CPU governor: performance.** Tuned sleep states. Stock Ubuntu optimizes for battery; the van has 500Ah — wake latency matters more.
- **PipeWire low-latency audio.** Small buffers (128–256 frames) for the voice path.
- **ZRAM swap.** Keeps things snappy if RAM gets tight with the model loaded.
- **Ordered boot.** Audio → noise suppression → wake word → STT → brain → TTS → skills. Each waits for its dependency.

## The stack (all systemd-supervised)
| # | Stage | Tech | Notes |
|---|-------|------|-------|
| 1 | Audio I/O | PipeWire | Low-latency config; shared device arbitration with Shawn mode |
| 2 | Noise suppression | RNNoise (or similar) | **Tuned for van acoustics** — road noise, fan hum, inverter whine. Biggest accuracy win available. |
| 3 | Wake word | openWakeWord | "hey scout" (custom). Thresholds auto-tuned against ambient noise level. |
| 4 | STT | Sherpa-ONNX / Parakeet | On-device, streaming |
| 5 | Brain | llama.cpp server | Qwen3.6-35B-A3B MoE @ Q3, full GPU offload, flash attention. Context sized for conversation + skills. |
| 6 | TTS | Kokoro (af_heart) | The auditioned voice. Piper as fallback. |
| 6b | TTS text normalizer | Python port of the Android `TtsTextNormalizer` | **Queued 2026-10-12 (Shawn: fold into ThinkPad build):** port the phone app's hard-won TTS fixes so the laptop never has these problems — currency words ("$1.30" → "one dollar thirty cents"), Dr.=doctor/drive context disambiguation, dashes→commas (Kokoro rushes through " - "), abbreviation expansion, pronunciation map, probabilistic varied breaths (optional — laptop currently inserts no breaths). Voice choice still open: spec says af_heart (feminine) but Scout on the phone is masculine (am_adam) — settle with Shawn before build. |
| 7 | Skills API | Python/FastAPI (local) | The hands: USB relays (lights/fan/inverter), sensor reads. Turns Scout from chatbot into the van's nervous system. |
| 7b | Shield control | `thinkpad/outpost_client.py` (done 2026-10-11) | Zero-dependency Python client for Outpost on the Shield — same protocol as the phone app. Van Scout controls the TV directly, no phone needed. CLI + importable. |
| 8 | Solar logger | Python (bleak + victron-ble) | Victron SmartSolar + Orion-Tr Smart DC-DC over BLE, passive advertisements, decrypted with the sticker key → SQLite. |
| 9 | Memory | Portable files | System prompt, memory, voice/wake settings — model-independent by design, syncable. |

## App parity checklist (principle 5 — keep current as the app evolves)

Each row: the phone app's behavior → what the laptop must do. "Done" only when Shawn confirms it by ear/use.

| # | Area | Phone app behavior (reference) | Laptop port |
|---|------|-------------------------------|-------------|
| P1 | Persona | Scout's persona: always honest, never fabricates ("either he knows or he doesn't"), sarcastic humor welcome, human-sounding | Same system prompt / persona file. Portable by design — one source of truth. |
| P2 | Voice identity | Masculine default (am_adam); rename-anytime | Masculine Kokoro voice on laptop (voice choice still open — spec said af_heart, needs Shawn's call). Same name handling. |
| P3 | TTS normalization | `TtsTextNormalizer`: currency words, Dr.=doctor/drive, dashes→commas, abbreviations, pronunciation map (see 6b) | Python port (6b). Same mispronunciations will occur on the same engine — port the map too, and keep both maps in sync going forward. |
| P4 | Breath sounds | Probabilistic, varied breaths (v2.7.40+) | Optional — laptop inserts no breaths today. If added, use the improved version, never the every-sentence one. |
| P5 | Wake word | "hey scout", sensitivity setting, self-restart on death (v2.7.41), diagnostics | openWakeWord with own `hey_scout` model (talk.py still loads `hey_tiara.onnx` — must be replaced). Same watchdog/restart discipline; same sensitivity vocabulary. |
| P6 | Memory | 'Remember that…' → durable memory | Same portable memory files. What the phone remembers, the laptop knows (syncable, model-independent). |
| P7 | Cloud escalation | 'Ask the Cloud' → Groq when local can't handle it | Same: local Qwen first, Groq escalation on demand. (Van offline = local only; escalation when connected.) |
| P8 | Diagnostics | Every service: plain-language health card + one-tap self-test (standing directive) | Same for every pipeline stage: `scout status` CLI (and/or local web card) showing each systemd service, mic liveness, last-heard, counters, one-tap self-test per stage. |
| P9 | Settings vocabulary | Plain-word levels: ear sensitivity, end-of-speech pause, personality strength | Same words in the laptop config — no raw dB/ms/temperature values exposed. |
| P10 | Translator | Phone interpreter mode **QUEUED 2026-10-14** (reverses the 2026-10-12 park): conversation mode (Bluetooth speaker + headset, phone fallback) + ambient mode; three-tier cascade — van Scout first when reachable, Groq, ML Kit offline fallback; timeouts, tier indicator, per-conversation TTS choice. Build after week reset Oct 17. Future: standalone translator app. | **Van flagship:** Universal Translator with dialects (spec'd 2026-10-12) — Qwen3.6-35B dialect-aware translation, VieNeu-TTS Southern/Northern voices, per-conversation dialect selector, interpreter + one-shot modes, all offline. Acceptance: Lien Pham real-conversation test. |
| P11 | Startup | ~30s Parakeet warmup → needs 'warming up…' indicator (open item on phone) | Same: model-load indicator, no silent deaf period. |
| P12 | Interruptions | Cut-off response marked in history; LLM stays in context (v2.7.42); 3+ interruptions in 5 min → Scout good-naturedly calls it out — **phone side confirmed by Shawn 2026-10-12** | Same behavior on laptop: mark truncated replies, same system guidance, same callout threshold. |
| P13 | Multi-instance sessions | App sends a per-device session ID with every request; each device's conversation stays isolated | ThinkPad keeps one session per device ID — contexts never interleave; memory scoped per device/user; GPU shared with graceful slowdown; connection limit is a setting. |
| P14 | Per-user wake word | Wake word picker in Settings, stored per device (default "hey scout"); pick from available openWakeWord models | ThinkPad registers each device's chosen wake word; same-word detections form a fair FIFO queue (first to detect gets the floor). |
| P15 | Queue status | Queued device shows position on screen ("Waiting — 2nd in line"); clear cue (on-screen + short chime) when its turn comes; cue stays on the queued device only | ThinkPad arbitrates the queue: grants turns in FIFO order, expires claims on silence/walkaway so the queue never stalls. |
| P16 | Rename | Rename-anytime name field (app already has this) | Laptop Scout's display name is a setting, not hard-coded. Renaming never breaks app↔laptop interaction: the protocol uses device IDs and the network address (`scout-van.local`), never the display name. Persona prompt updates to the new name. Wake word follows the name only if an openWakeWord model exists for it (custom-trained wake words are future). |
| P17 | Name sync | Change the name on either body → pushes to the other, both always share one name | ThinkPad holds the canonical name. Implemented 2026-10-14: `thinkpad/name_sync.py` (stdlib-only server, port 8091, store `~/.scout/name.json`) + app `van/NameSyncClient.kt` + `thinkpad/NAME-SYNC-PROTOCOL.md`. Endpoints: `GET /name` (long-poll `?since=&wait=` = live push), `POST /name` (last-write-wins by parsed timestamp; 409 returns the winning record), `POST /register`, `GET /health`. App reconciles on foreground (`MainActivity.onResume` → `SettingsViewModel.syncNameWithVan`); long-poll loop is foreground-only (stopped on pause). Rename while apart queues (one slot, SharedPreferences) and flushes on next contact; both-changed-while-apart → last-write-wins by timestamp; stale pushes never clobber (last-applied watermark). Name validated 1–40 chars, no control chars. Wake word follows the name only when a `hey_<slug>.onnx` model exists; if none, name changes but wake word stays, and Scout says so. |

Phone-only (no laptop equivalent): home-screen mic widget, launcher label. Laptop-only (no phone equivalent): van skills (relays, solar, cameras), XFCE handoff.

## Data Scout will have
- **Solar/battery:** Victron BLE → SQLite (voltage, current, PV watts, charge state, daily yield — SmartSolar AND Orion-Tr Smart DC-DC). Voice: "how are my batteries doing?" / "is the alternator charging?"
- **Cameras:** JOINLGO DVR (van unit: J2-4GW-AF, login KNOWN; test spare: G2-WS 4CH Mobile DVR, Code G2-WS, Admin password reset + forgotten — JOINLGO contacted for reset). RTSP output UNVERIFIED — spec lists no RTSP server. DVR backend test folded into pull-it-together (Shawn 2026-10-16, "Fold"): G2-WS = observational only until JOINLGO replies (port scan, outbound traffic watch, unauthenticated stream check). Settings-change tests (server re-pointing, menu options) need a login — if JOINLGO replies, they run on the G2-WS; if not, they run on the live van DVR only with Shawn's explicit go-ahead (risk of disturbing the working security system). **Backend switch (approved 2026-10-16):** prove Traccar (phone GPS client) + Frigate (test stream) FIRST, then cut the live van DVR over: record all current settings (server 47.88.8.31), change server address, verify GPS + video + alerts; revert to 47.88.8.31 if anything fails. Switch replaces CMSV7 (app remote viewing stops); if no RTSP, remote live video is gone until the AHD capture path. Frigate/Traccar backend builds only if those tests pass; otherwise the DVR stays a local-only recorder and the fallback is an AHD capture card + PC. **Test plan document (prep, 2026-10-16): `thinkpad/DVR-BACKEND-TEST-PLAN.md`** — Phase 1 (prove Traccar/Frigate with non-DVR sources), Phase 1b (observational tests on G2-WS: port scan, traffic watch, unauth stream check, menu reads), Phase 2 cutover with rollback, fallbacks. Spare needs power + network only (done 2026-10-16); no cameras for tests.
- **God's Eye:** see §God's Eye — unified world view (approved 2026-10-15). Private van layers (DVR, GPS, battery/solar, interior cam) alongside public layers.
- **Alerts:** no solar by mid-morning, overnight voltage sag, DVR motion while away (sentry).

## Full capability plan (locked 2026-10-11)

Brainstormed and approved with Shawn 2026-10-11. Everything installs during "pull it together"
(planned for the week after the Sat 2026-10-17 weekly build-budget reset). Install method: **staged
scripts, one per layer** (base system → LLM → ComfyUI → video models → music → images → finishing
touches → Scout wiring); each script verifies the previous layer before continuing. No manual
47-step checklist.

### Creative studio (all offline, all through Scout)
- **Video:** LTX-Video 2B (FP8, ~5GB) PRIMARY — fastest, fits 16GB easily; Wan 2.2 (FP8, ~5GB)
  SECONDARY for max-quality single clips. Both run in ComfyUI. Scout picks by request ("make me a
  video" → LTX; "make me the best quality video" → Wan) or asks when ambiguous.
  **Stitching workflow:** Scout splits long videos into 5s segments, feeds the last frame of clip N
  as the first frame of clip N+1 (continuity), stitches with ffmpeg → any length.
  (Correction, owned: the earlier "LTX-Video 13B" recommendation was wrong — 13B FP8 is ~24GB,
  too big for 16GB. 2B is the practical pick.)
- **Music:** ACE-Step 1.5 (Apache 2.0, commercial use OK) — full songs with lyrics + vocals up to
  10 min, ~4GB VRAM, 50+ languages for lyrics, ~10GB storage. In ComfyUI. Runner-up MiniMax Music 3
  rejected (heavier, shorter songs).
- **Images:** SDXL (primary) + Flux (optional, max quality), ~27GB. ComfyUI.
- **Polish:** Real-ESRGAN (upscaling), RIFE (frame interpolation → 60fps), Whisper (transcription),
  ~10GB.

### Van hardware adds (approved — "ALDL and SDR definitely include")
- **Engine diagnostics:** the van is OBD1 ('92 GMC G2500 Vandura, 5.7L TBI V8), but it streams live
  ALDL data at 8192 baud: RPM, coolant temp, speed, MAP, TPS, O2 voltage, spark advance, fuel trim,
  IAC, battery voltage. **Bluetooth ALDL adapter** (ALDL-specific, e.g., Red Devil River Bluetooth adapter — NOT an OBD2/ELM327 adapter, which does not work on OBD1) + TunerPro RT (free) on the ThinkPad → Scout does
  "how's my engine running?" in plain English. (No CAN bus on OBD1.) **Laptop always has priority over phone** for the Bluetooth connection (Shawn 2026-10-16; Bluetooth serial is one-consumer-at-a-time): the ThinkPad holds the connection; the phone connects only when the laptop isn't using it, or reads engine data via Scout. Phone gauges via ALDLdroid + the same adapter when the laptop isn't connected. Needs the ADX file for his ECM (same file the ThinkPad TunerPro setup needs).
  **ALDL prep checklist (2026-10-16):** (1) Adapter = ALDL-specific Bluetooth (12-pin ALDL plug, 8192-baud ALDL, Bluetooth serial/SPP bridge, powered from the ALDL port). OBD2/ELM327 adapters do NOT fit the 12-pin port and cannot speak ALDL — an OBD2-to-OBD1 cable does not fix this (pins only, wrong protocol). A purchasable source (Red Devil River or equivalent) still needs to be found — Amazon is OBD2-dominated. (2) Priority arbitration: ThinkPad pairs and holds the SPP connection at Scout start; phone (ALDLdroid) may connect only when the ThinkPad releases it; if both want it, ThinkPad wins and the phone reads engine data via Scout instead. (3) ADX definition file for this van's ECM is required by both TunerPro RT (ThinkPad) and ALDLdroid (phone) — obtain once, keep with the install files. (4) Van-systems-watch alerts (protection pick, approved 2026-10-15) read from this feed: voltage drop, coolant spike, abnormal drain.
- **SDR dongle (~$30):** NOAA weather satellite images (actual satellite photos), aircraft ADS-B
  (feeds God's Eye), emergency frequencies, amateur radio.
- **Sensors (later, DIY):** Bluetooth temp/humidity, TPMS tire-pressure-by-voice, ESP32 custom
  sensors (van door sensor, water tank level, ~$5 each) via Node-RED + MQTT + ESPHome.
- **Off-grid comms:** Meshtastic — LoRa text messaging with no cell signal.

### Eyes and security
- **Frigate** NVR with AI object detection on the JOINLGO DVR cameras — "person at the side door"
  instead of dumb motion alerts. Gated on the DVR backend test (streams must exist); if no streams, fallback is an AHD capture card + PC.
- Facial recognition (him vs. stranger approaching); license plate logging of vehicles near the van.
- Geofencing: van moves without his phone nearby → instant alert. Unknown-device-joins-van-WiFi
  alerts.

### Deterrence (approved 2026-10-15 — protection picks + Bluetooth speakers, Shawn: "Make it so")

When Sentry is armed and cameras detect a human approaching the van:
- **Classify first:** person detection (Frigate) → facial recognition against the familiar gallery (Shawn + Lien Pham + others Shawn adds). No human (animal/shadow) → ignore. Familiar face → no deterrence, just log + notify. Unfamiliar / can't tell → deter immediately (fail-secure).
- **Deter immediately** (no alert-first, no cancel window): voice + lights + recording + alert to Shawn, all in parallel.
  - **Voice:** Scout speaks through strategically placed Bluetooth speakers (TWS stereo pair, USB-powered, inside the van front + rear, kept awake by a continuous near-silent keep-alive stream) at loud volume during deterrence (max/near-max, restored after stand-down). Firm, human, varied lines — not a looped recording: "Hey! You're on camera. This van is monitored. Leave now." / "Step away from the van. You are being recorded, and the owner has been alerted." Never claim police were notified (not true). ThinkPad built-in speakers are the fallback if Bluetooth drops. NOT the BCPA9 (off when parked). Scout uses the Bluetooth speakers ONLY during deterrence or when Shawn explicitly requests it — never for normal voice output.
  - **Lights:** flash the van lights.
  - **Recording:** cameras record (Frigate clips + snapshots).
  - **Alert to Shawn:** notification + snapshot / live view. Shawn can take over live (speak through the speakers).
- **Monitor:** if the person leaves → stand down, log, notify ("Person left. Clip saved."). If they stay / try a handle → escalate (firmer lines, keep recording, urgent alert). If a face is positively recognized as familiar after deterrence started → stand down (+ brief apology). If entry succeeds → hands off to the theft-recovery playbook.
- **Horn:** BACKBURNER, not a priority (no horn relay for now).

### Theft recovery — laptop decoy (spec: `files/scout-theft-recovery-spec.md`)
- Full spec lives in `files/scout-theft-recovery-spec.md` — current as of 2026-10-15 (decoy update reversal applied). Summary: on theft (unrecognized face at lid-open OR manual activation from the phone app) the laptop LOCKS INTO "Shawn mode" decoy desktop (separate session; real files stay LUKS-encrypted/unmounted; thief cannot exit). Background beacon: live location + trail, stop snapshots (location + timestamp + battery/network/WiFi + optional camera photo each time the device is still for 2 minutes), webcam snapshots, usage logs — all via Tailscale to Shawn's phone. Silent commands from phone; remote lock/wipe (wipe = two-step confirm); speak via Shawn's live mic stream or Scout TTS (typed text). **Unlock only via face + voice TOGETHER, or phone unlock via Tailscale** (standalone voice + challenge-response dropped). Decoy shows NO update option/notification (reversed 2026-10-15 — update mechanism is a risk surface). Power-button long-press (4s+) is hardware EC forced-off and cannot be disabled — mitigation is the beacon trail + dead-man's-switch logic. Queued for pull-it-together; when "pull it together" is triggered, raise theft recovery explicitly if Shawn doesn't mention it first. Phone mirror feature is a separate spec (`files/scout-phone-theft-recovery-spec.md`), DEFERRED to Sat Oct 24, 2026.

### Knowledge (all offline)
- **RAG over van manuals:** "Scout, how do I reset the Victron?" answered from the actual manual,
  not a guess. Full document library searchable by conversation.
- **Offline Wikipedia via Kiwix** (~100GB). US offline maps (~50GB).
- **Van knowledge base:** `thinkpad/van-knowledge-base.md` — repair/maintenance/troubleshooting, Tiara Executive Edition, TMC, cross-compat parts, VIN decode + plate. Offline reference for van Scout.
- **How knowledge gets on the laptop (implemented 2026-10-16):** usb-prep.py stages the payload into `scout-files/knowledge/` on the USB (manuals folder + first aid, troubleshooting, repair, field repairs, medication reference, van knowledge base); the installer's **Knowledge libraries** step copies it to `~/scout/knowledge/` and verifies every file against a manifest (sizes + PDF magic bytes). Missing file = install fails loudly, never silently. New manuals land by adding them to the manuals folder — the step copies the whole folder, the manifest guarantees the core files.

### Parts interchange + online search (added 2026-10-15, Shawn: "with certainty"; clarified 2026-10-15; database wired in 2026-10-15)
- **Authoritative database:** `thinkpad/parts-interchange-db.json` — 697 entries (541 VERIFIED, 156 CANDIDATE) as of 2026-10-15. This JSON file is the parts database the laptop build installs and Scout queries. It rides the USB to the ThinkPad. The van knowledge base (`thinkpad/van-knowledge-base.md`) is the narrative companion (repair/maintenance/troubleshooting); the JSON file is the authoritative parts table.
- **Installer wiring (prep, 2026-10-16):** usb-prep.py stages the DB into `scout-files/knowledge/parts-interchange-db.json` on the USB (part of the knowledge manifest in both scripts — keep them in sync); scout-installer.py's Knowledge libraries step copies it to `~/scout/knowledge/parts-interchange-db.json` and verifies it parses as JSON with all 697 entries. Missing/corrupt DB = install fails loudly, never silently.
- **Offline = the data itself.** The verified interchange table (in `thinkpad/parts-interchange-db.json`) holds the actual parts data: GM part number(s), compatible make/model/year(s), and confidence for each part. NOT just pointers to where to find it (no "go look at RockAuto"). Sources are cited for verification, but the data lives in the table, available offline.
- Scout answers a parts-compat question ONLY from a verified table entry OR from a live online search with a cited source. Never guesses. If neither exists, he says so: "I don't have a verified interchange for that part."
- **Online search (when online + asked):** for what is NOT in the table (or to verify/expand a table entry) — "Search online for [part]" → Scout searches the web (RockAuto, Hollander, parts catalogs, forums) and returns the answer WITH its source. If the result is verified, he offers to add it (the data) to the offline table.
- **Offline:** table only. No web, no guessing.
- **Links deferred (2026-10-15):** no source URLs/links in the offline table for now — data only. Links added later.
- **Lower control arms (Shawn's example) — DONE 2026-10-15:** arm assemblies + shaft kits verified with machine-readable `pairs_with` links, lower washer GM 7832666 VERIFIED, shaft-kit contents items 84–86 confirmed kit-only, and lower shims/spacers confirmed NOT APPLICABLE (no such part exists by design — GM catalog lists SHIM/SPACER only under Upper Control Arm). All 4 original gaps closed.

### Self-hosted services (all on the ThinkPad)
- **Immich** (own Google Photos, AI-tagged), **Jellyfin** (media server, streams to the Shield),
  **Paperless** (scan + OCR receipts/documents, ask Scout to find them), **SearXNG** (private
  metasearch when online), network-wide ad-blocking, **VPN server** (secure tunnel back to the van
  from anywhere).
- **Automation:** changedetection.io (deal watches run locally), n8n (visual workflow automation).
- Also in scope: Plex control + auto-download for binge nights, calendar/reminders/alarms, SMS via
  paired phone, email read/send/draft, push notifications, GPS logging ("where did I park?", trip
  history), Wake-on-LAN for the home PC, Bluetooth audio routing.

### Vision (implemented 2026-10-16, Shawn: "Make it so")
- **Model:** Qwen3-VL-8B-Instruct, GGUF Q4_K_M (~5GB) + mmproj F16 projector (~1.2GB), from `Qwen/Qwen3-VL-8B-Instruct-GGUF`. Rides the USB (usb-prep.py), lands in `~/scout/models/`.
- **Serving:** llama.cpp `llama-server --mmproj` — the same stack as the brain. NOT Ollama: Ollama has a known crash bug with Qwen3-VL, and this build's stack is llama.cpp.
- **Swap:** 16GB VRAM can't hold the main model + vision at once. `thinkpad/scout-vision.py` orchestrates: stop main server → start vision server on port 8081 → describe → stop vision → restart main. Vision calls are rare/on-demand, so seconds of swap time are fine.
- **Pipeline:** vision model DESCRIBES only (bleeding, depth, foreign object, surrounding skin, location — prompts in scout-vision.py). The main model + the relevant library (first aid, troubleshooting) does the reasoning and speaks the answer. Vision never gives advice.
- **Uses:** wound photos (first aid), wiring photos (troubleshooting), DVR camera frames (Scout's eyes) — same mechanism, different prompt. Photo arrives via laptop camera or phone app over van Wi-Fi / Tailscale.

### Dual Voice Mode — DVM (approved 2026-10-16, Shawn: "Make it so")
- **User-facing: one switch — DVM on or off.** No mode picking. DVM on = Scout sounds like two people having a conversation; DVM off = normal single-voice Scout. The configurations below are internal build breakdowns, never user choices.
- **Auto-selection:** DVM uses whatever devices are present. Phone + laptop connected → each speaks its lines (two-device). Laptop only → laptop renders both voices. Phone only → phone renders both voices. Scout detects what's connected and runs the matching configuration — the user never picks one.
- **DVM is a feature of both Scouts:** laptop Scout runs the laptop-alone + two-device configurations; phone Scout runs the phone-alone configuration and joins the two-device configuration as the second speaker. Same name, same rules, both Scouts.
- **Configurations (internal, build order):**
  - **Laptop alone (build first):** talk.py dialogue mode. Scripted or Qwen-generated dialogue with Speaker A / Speaker B lines. Each line renders in its speaker's Kokoro voice (two distinct voices, e.g. masculine + feminine), played sequentially through the van speakers. Scripted + pre-rendered = smooth playback; live generation = pauses between turns. Single device = no mic/wake-word issues (pure playback).
  - **Two-device (builds on laptop-alone):** phone speaks its lines, laptop speaks its lines, alternating. Lines pass as text between instances (ThinkPad multi-instance sessions), mics muted — never over the air (avoids wake-word firing + interruption spirals). Distinct voices per device + distinct personas. FIFO queue orders turns if both hear a wake word.
  - **Phone alone (rides Saturday's app build):** phone-app dialogue mode. Scripted or LLM-generated dialogue with Speaker A / Speaker B lines, each in a distinct voice (Kokoro voice A + Kokoro voice B, or Kokoro + Edge), played sequentially through the phone speaker / Bluetooth. Scripted mode works fully offline (pre-written lines, local TTS); generated mode uses the configured LLM endpoint. Same participation rules as the other configurations.
- **Rules:** voices MUST differ (same voice = one person talking to themselves). Personas differ (speaking style, vocabulary, opinions). Delivery differs (pace, formality). Pre-render scripted dialogue to audio for smooth playback.
- **Shawn participates (added 2026-10-16):** he joins as a third participant, two styles: (a) **director** — pause via "hey scout" or an app button, speak, dialogue resumes; (b) **character** — Shawn takes one role, Scout plays the other(s). The dialogue loop listens between lines (brief mic window / wake-word armed); an interruption pauses playback, routes Shawn's turn, then resumes. In the two-device configuration, Shawn joins via either device.
- **Uses:** two characters telling a story, two-host podcast segment, language-practice dialogues, rehearsing a conversation, simulated radio show.
- **Gating:** laptop-alone configuration built at pull-it-together (talk.py doesn't exist yet); two-device configuration after laptop-alone + multi-instance text handoff; **phone-alone configuration rides Saturday's app build.** Change-impact audit before implementing (touches talk.py TTS pipeline + multi-instance protocol).

### AI extras (doors left open, not day-one)
- Voice cloning / video narration, dream journal, mood-aware responses.
- Translation: multi-language pairs with **Southern Vietnamese dialect support = hard requirement**
  (ML Kit's single Vietnamese won't cut it for speech) — finding engines with real dialect options
  is the first research job.
- **vLLM serving (evaluated 2026-10-13, NOT adopted):** assessed via Alex Ziskind's agent-speed video. Considered replacing LM Studio to avoid a future migration — rejected on net-benefit grounds: the "problems down the road" (concurrency limits, long-context degradation) only materialize with the agent layer, which is still on watch; the migration itself would be low-cost (OpenAI-compatible API); while vLLM brings certain present costs (Python+CUDA setup complexity, safetensors re-download, compatibility risk — the video showed a Qwen3 model failing on vLLM). Original plan stands: talk.py + LM Studio. Revisit if the agent layer demands it.

### Storage math (~280GB of 1TB — comfortable)
- AI models ~80GB: 35B ~20GB · video ~10GB · ACE-Step ~10GB · SDXL+Flux ~27GB · Whisper/upscalers ~10GB
- Big data ~150GB: offline Wikipedia ~100GB · US offline maps ~50GB
- Apps + system ~50GB: Ubuntu, ComfyUI, Frigate, Immich, Jellyfin, the rest
- **Headroom:** Frigate recordings, media library, years of growth. Drive: **WD Green SN3000 1TB
  (ordered 2026-10-10, arrives Oct 17)** — it goes in the ThinkPad. Local sub-$80 watch continues
  through the Amazon return window.

## Network
- Van LAN via **built-in hotspot within SafeLink's 10 GB hotspot cap** (REVISED 2026-10-16 — supersedes EasyTether, decided 2026-10-11): a **dedicated van phone** (BLU View Speed Ultra 5G, SafeLink Lifeline, Verizon network — NOT Shawn's personal phone) broadcasts van Wi-Fi via its own hotspot; ThinkPad + Shield + DVR join the phone's hotspot. SafeLink benefits: Unlimited Talk & Text, 25 GB high-speed on-device data, **10 GB hotspot data** — hotspot is separately capped. **EasyTether is OUT** (Shawn 2026-10-16) — it would bypass the 10 GB hotspot cap by masking tethered traffic as on-device data. Scout + DVR GPS fit easily in 10 GB; DVR video stays local, no streaming / big downloads over hotspot. Because the van phone stays in the van, the van has independent internet even when Shawn walks away with his personal phone.
- **Remote access (added 2026-10-14):** Tailscale on the ThinkPad → Shawn's personal phone reaches van Scout from anywhere with internet. Same Tailscale account already on his phone + home PC. This makes "Scout everywhere" work: in the van = direct LAN (offline-capable); away = via Tailscale through the van phone's connection.
- **Remote maintenance access (added 2026-10-14, Shawn: "Yes"):** Scout (the Muse agent, not the van voice assistant) gets SSH access to the ThinkPad over Tailscale for remote maintenance — check services, pull logs, update code, restart services — so van Scout can be looked after without Shawn being at the laptop. Key-based SSH only, no passwords. Same Tailscale account/tailnet; the agent's VM joins it. LAN/Tailscale-only, no public exposure. Shawn can revoke anytime by removing the VM from the tailnet or disabling SSH. Same approval rules as always: no irreversible actions without his say-so.
- Supporting pieces: dedicated van phone stays on a charger; Plex on the ThinkPad + download-ahead for binge nights so big numbers never hit the carrier; monitor hotspot usage against the 10 GB cap (check SafeLink account / text HELP to 611611).
- Franklin T10 is OUT (decided 2026-10-11 — Shawn: "T10 is out, I like the phone tether idea"). T-Mobile Mobile Internet plans researched 2026-10-11: top tier is 100GB/$50/mo, then throttled to 2G — NOT true unlimited. SIM-in-T10 rejected (IMEI mismatch gets flagged).
- Caveats: stay within the 10 GB hotspot cap — Scout + DVR GPS are light, video streaming / big downloads over hotspot are what blow it; van phone must stay on + charged as the router.
- ThinkPad: static IP on the van LAN; mDNS `scout-van.local`.
- Scout binds localhost-first; LAN sharing explicit per service. Nothing exposed to the internet by default.
- **Multiple app instances (future-proofed 2026-10-14):** the ThinkPad accepts connections from multiple Scout app instances (multiple phones/devices), not just one. Each instance gets its own conversation session — contexts never interleave. Memory is scoped per device/user, not shared across instances (two people on two phones don't read each other's memory). GPU is shared: simultaneous requests queue and responses slow gracefully; no hard failure. **Per-user wake word (added 2026-10-14):** each app instance chooses its own wake word, stored per device — not global. Users pick from available openWakeWord models (e.g., one device on "hey scout," another on a different phrase). Different wake words per device eliminates most collision. **Same wake word (added 2026-10-14):** when multiple devices hear the same wake word, they form a fair FIFO queue coordinated by the ThinkPad — first to detect gets the floor, the rest wait in order. No device is left out: each queued device gets its turn when the device ahead finishes (or its claim expires). **Queued device is informed (added 2026-10-14):** a waiting device shows its queue status on screen ("Waiting — 2nd in line") so the user isn't confused by the silence; when its turn comes, it gives a clear cue (on-screen + short chime) that it's now listening. The waiting cue stays on the queued device only — it never speaks over the active device's conversation. Claims expire if the user doesn't speak within a short window after getting the floor (so a false trigger or walkaway doesn't stall the queue), and a queued device that gets the floor listens briefly — silence means it releases and goes back to sleep. Custom-trained wake words (record-your-own) are a future option, not day-one — training a model per arbitrary phrase is heavy. Connection limit is a setting, not a constant. Bluetooth device limit: up to 10 paired/connected devices on the laptop, and up to 10 on the app (each) — a setting, not hard-coded. Access stays LAN/Tailscale-only (no public exposure).

## Open questions (brainstorm)
1. **Desktop for Shawn mode:** ✅ XFCE (decided 2026-10-11) — most "regular desktop" feel (taskbar, app menu, tray, desktop icons) at ~500MB RAM. MATE was runner-up; Cinnamon/KDE too heavy for Scout's machine.
2. **Handoff:** ✅ voice handoff, zero teardown (decided 2026-10-11) — "Hey Scout, I need the laptop" → starts XFCE, Scout mutes its own voice output and drops to wake-word-only listening (no unprompted speech, no skill actions); "Hey Scout, I'm done with the laptop" → kills the desktop session, full mode resumes. Model stays loaded in VRAM throughout, conversation context untouched, all services keep running — only behavior flags change. Short voice confirmations on each transition ("All yours." / "I'm back."). Idle policy (decided 2026-10-11): 10 min with no input in Shawn mode → Scout asks "still need the laptop?"; no response within 1 min → Scout reclaims the machine (ends desktop session, resumes full mode).
3. **Lid behavior:** lid closed most of the time? External display via Shield for God's Eye?
4. **Backups:** personality/memory/SQLite synced where? (USB stick? Phone? Encrypted cloud?)
5. **Stack updates:** ✅ All three modes (decided 2026-10-14 — Shawn: "All"). One updater, three triggers: (a) **Manual pull** — `git pull` on the ThinkPad, or re-run the installer; full user control. (b) **Voice-triggered** — "Hey Scout, update yourself" → Scout pulls latest from GitHub, applies, restarts affected services; asks for confirmation first ("This will restart me for a minute — go ahead?"). (c) **Scheduled auto-update with rollback** — laptop checks GitHub on a schedule, snapshots the current working state first, applies, runs a health self-test, rolls back to the snapshot if the test fails. Safety rules shared by all three: never auto-update mid-drive — scheduled updates only apply when parked/idle (or in a user-set window); snapshot-before-apply always; rollback on failed health check. **Update notification (standing 2026-10-15):** when an update is available, Scout gives one subtle one-time notification per version (voice mention) — dismiss it and it doesn't repeat until the next version; the user applies via the voice-triggered path (the update button).
6. **Second RAM stick:** 32GB is plenty today (model lives in VRAM), but a matching stick is cheap future-proofing — worth it?
7. **SSD:** ✅ WD Green SN3000 1TB ordered 2026-10-10, arrives Oct 17 — it goes in the ThinkPad (resolved; local sub-$80 watch continues through the Amazon return window).
8. **LUKS encryption:** full-disk encryption was in the anti-theft plan. Passphrase strategy for a headless van machine? (TPM + PIN? USB key?)
9. **Sentry integration:** phone-leaves-LAN → arm; which signals does Scout watch?

## Universal Translator (van flagship — spec'd 2026-10-12, Shawn's call)

Shawn redirected the translator effort from the phone to the van: "make something good for the van. A universal translator with dialects." The phone keeps its existing one-shot hooks parked (not shipped); the ThinkPad gets the real thing.

### Why the van wins here
- **Brain:** Qwen3.6-35B-A3B translates with dialect awareness no phrasebook model (ML Kit) can match — it understands Southern vs Northern Vietnamese in *text*, not just word swaps.
- **Voice:** VieNeu-TTS — explicit Southern voices (male: Nguyên, Sơn, Vĩnh; female: Đoan, Dung), Northern voices too, on-device, Apache 2.0, real-time on CPU, `pip install vieneu`. No contest.
- **Ears:** Southern Vietnamese STT is the open hard problem — no benchmarked winner. Real-world test with Lien Pham is the acceptance gate.

### Design
- **Languages:** English ↔ Vietnamese (Southern / Northern / Central dialect selector) at launch; architecture open for more pairs (Spanish, Mandarin, etc.) — user picks, nothing hard-coded.
- **Dialect selector:** per-conversation setting ("talking to a Southerner today") — TTS voice + translation tone follow it. Not a global default; people differ.
- **Modes:**
  - *Interpreter mode* (voice): "interpreter mode" → everything either person says is translated aloud to the other side; "stop translating" exits. Hands-free, for travel and the van.
  - *One-shot*: "translate X" / "how do you say X in Vietnamese."
- **Pipeline:** mic → STT → Qwen translates (dialect-aware) → VieNeu-TTS (dialect voice) → speaker. All on-device, all offline.
- **Text path:** written Vietnamese is dialect-neutral — shown as-is; dialect only affects speech in/out.
- **Acceptance:** Lien Pham (Southern speaker) holds a real conversation through it. If she says it sounds wrong, it's wrong.

## God's Eye — unified world view (approved 2026-10-15, Shawn: "Make it so")

God's Eye (Bilawal Sidhu's God's Eye View) is the van AI's unified world view. It runs on the ThinkPad, on demand, and Scout answers most God's Eye-capability questions from data alone — the 3D view loads only when Shawn wants to SEE something.

### How it runs: on-demand, never 24/7
- Hosted version runs in a browser on the ThinkPad. Loads only when Scout needs it (a voice command, or a question needing world data); idles/closes when not in use.
- Never runs 24/7 at full render — no sustained GPU contention with the LLM (which fills most of the 16GB VRAM).
- God's Eye URL is a setting, filled in when the hosted version launches (Monday watch tracks the launch; Shawn chose to wait for hosted, not the DIY Termux route).

### Data-first answering (no 3D view needed)
Scout answers God's Eye-capability questions by querying the data sources directly — lightweight calls, no GPU, no 3D view:
- Map / place / distance / route → OSM maps on the ThinkPad (offline).
- Weather / traffic → weather/traffic feeds when online.
- "That plane overhead" → ADS-B (OpenSky Network, free). Uses Shawn's GPS location, finds the aircraft nearest to directly overhead: airline, flight number, aircraft type, altitude, speed, heading. Coverage is strong (ADS-B required in US controlled airspace).
- "That boat in the bay" → AIS (AISHub / MarineTraffic). Nearest vessel in the bay: name, type, flag, speed, heading, destination. Coverage is partial — small private boats often don't broadcast AIS, so an unlisted boat is invisible to the data; Scout says so honestly rather than guessing.
- Live feeds need internet. Offline, Scout answers from local data only (OSM maps, GPS).
- Exceptions: a live feed only God's Eye has with no API, and inherently visual requests.

### Voice commands (two display paths)
- "Show God's Eye" → opens on the laptop screen.
- "Show God's Eye on the TV" → Scout wakes the Shield/TV (Outpost power wake + CEC) and opens the God's Eye URL in Outpost's WebView, full-screen on the TV.
- "Hide God's Eye" / "Close God's Eye" → returns to the previous app or home.
- Fallback: if Outpost's WebView doesn't render God's Eye's WebGL well, launch it in a full browser app on the Shield instead (Outpost can launch apps by package name).

### Gating
- Gated on the God's Eye hosted launch (Monday watch notifies when live) + the pull-it-together build. The voice intents and data-feed clients are part of the laptop Scout build.

## Route planning — God's Eye data → Google Maps → BCPA9 (approved 2026-10-15, Shawn: "Make it so")

Scout plans driving routes from God's Eye data (live traffic + road conditions) and OSM maps, then hands the route to Google Maps on the phone, which Android Auto projects onto the BCPA9 dash display.

### Flow
1. Shawn: "Take me to [destination]" / "Navigate to [destination], avoid traffic."
2. Scout plans the route: OSM maps on the ThinkPad + live traffic feed (God's Eye data) when online. Picks the route (e.g., "I-5 is jammed, taking the 99 instead").
3. Scout opens Google Maps on the phone with the destination + waypoints pinning its planned route. Google Maps navigates; Android Auto shows it on the BCPA9.
4. "What's the traffic to [destination]?" → Scout checks traffic and answers without navigating.

### Constraining Google Maps (waypoints)
- Scout places a waypoint at every decision point on its planned route (highway fork, entrance, key turn). Google Maps MUST route through waypoints in order — this pins Scout's route. Not a hack; it's the documented waypoints feature.
- Free URL/Intent path: max 9 waypoints (+ origin + destination). Covers most real drives; for long multi-leg trips, Scout picks the 9 most important forks.
- Google Maps can still re-route BETWEEN waypoints if traffic changes mid-drive, but must hit the next waypoint — it can't abandon Scout's route entirely.
- No full polyline injection: even the paid Directions API (25 waypoints) can't push an arbitrary turn-by-turn polyline into the Google Maps app for navigation. Waypoints are the mechanism.
- Avoid preferences: Scout can add avoid=tolls|highways|ferries to the URL when Shawn asks.

### Display: BCPA9 via Android Auto
- The BCPA9 doesn't run Google Maps itself — it's a display for the phone. Scout opens Google Maps on the phone; Android Auto projects it onto the dash. Scout can't push video directly to the BCPA9 (no HDMI input, Bluetooth is audio-only).
- This is launching an app on the phone (which AA then mirrors), NOT Scout driving Android Auto's UI (ruled out — AA template restrictions).

### Offline fallback
- No internet: Scout routes from OSM on the ThinkPad; Google Maps navigates on downloaded offline maps (if downloaded). Live traffic unavailable offline.

### Phone-side work
- Small addition to a future phone-app build: construct the Google Maps dir URL (origin + up to 9 waypoints + destination + avoid params) and open it. The app can already launch apps / open URLs.

### Gating
- Part of the laptop Scout build (pull-it-together). Phone-side URL construction rides in a future app build. No Directions API key needed (free URL/Intent path).

## Queued, not yet spec'd
- Screen-off wake-word foreground service (phone Scout; end-of-week per 2026-10-11)
- Universal Outpost v2.8 (deferred to Sat Oct 24, 2026)
- Slimming pass (~60MB target, nothing cut)
