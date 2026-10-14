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
- **Cameras:** JOINGLO DVR via RTSP (unconfirmed — needs model/firmware check at install time).
- **God's Eye:** private van layers (DVR, GPS, battery/solar, interior cam) alongside public layers — longer term.
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
  IAC, battery voltage. USB ALDL cable (~$60–80) + TunerPro RT (free) on the ThinkPad → Scout does
  "how's my engine running?" in plain English. (No CAN bus on OBD1; no Bluetooth OBD2 dongle.)
- **SDR dongle (~$30):** NOAA weather satellite images (actual satellite photos), aircraft ADS-B
  (feeds God's Eye), emergency frequencies, amateur radio.
- **Sensors (later, DIY):** Bluetooth temp/humidity, TPMS tire-pressure-by-voice, ESP32 custom
  sensors (van door sensor, water tank level, ~$5 each) via Node-RED + MQTT + ESPHome.
- **Off-grid comms:** Meshtastic — LoRa text messaging with no cell signal.

### Eyes and security
- **Frigate** NVR with AI object detection on the JOINGLO DVR cameras — "person at the side door"
  instead of dumb motion alerts.
- Facial recognition (him vs. stranger approaching); license plate logging of vehicles near the van.
- Geofencing: van moves without his phone nearby → instant alert. Unknown-device-joins-van-WiFi
  alerts.

### Knowledge (all offline)
- **RAG over van manuals:** "Scout, how do I reset the Victron?" answered from the actual manual,
  not a guess. Full document library searchable by conversation.
- **Offline Wikipedia via Kiwix** (~100GB). US offline maps (~50GB).

### Self-hosted services (all on the ThinkPad)
- **Immich** (own Google Photos, AI-tagged), **Jellyfin** (media server, streams to the Shield),
  **Paperless** (scan + OCR receipts/documents, ask Scout to find them), **SearXNG** (private
  metasearch when online), network-wide ad-blocking, **VPN server** (secure tunnel back to the van
  from anywhere).
- **Automation:** changedetection.io (deal watches run locally), n8n (visual workflow automation).
- Also in scope: Plex control + auto-download for binge nights, calendar/reminders/alarms, SMS via
  paired phone, email read/send/draft, push notifications, GPS logging ("where did I park?", trip
  history), Wake-on-LAN for the home PC, Bluetooth audio routing.

### AI extras (doors left open, not day-one)
- Qwen3-VL vision (photo of his wiring → what's wrong), voice cloning / video narration,
  dream journal, mood-aware responses.
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
- Van LAN via **EasyTether** (decided 2026-10-11, clarified 2026-10-14): a **dedicated van phone** (separate device that lives in the van, active SIM, unlimited plan — NOT Shawn's personal phone) USB-tethers to the ThinkPad with tethering disguised as on-phone data — $9.99 one-time, no new line, no monthly fee, no hotspot-GB drain. ThinkPad broadcasts the van Wi-Fi; Shield and everything else join it. (PdaNet rejected: no official Linux client.) Because the van phone stays in the van, the van has independent internet even when Shawn walks away with his personal phone.
- **Remote access (added 2026-10-14):** Tailscale on the ThinkPad → Shawn's personal phone reaches van Scout from anywhere with internet. Same Tailscale account already on his phone + home PC. This makes "Scout everywhere" work: in the van = direct LAN (offline-capable); away = via Tailscale through the van phone's connection.
- Supporting pieces: dedicated van phone stays on a charger; VPN on the van phone defeats the 480p video throttle (hides traffic type, not volume); Plex on the ThinkPad + download-ahead for binge nights so big numbers never hit the carrier; deprioritization past ~50GB only bites on congested towers.
- Franklin T10 is OUT (decided 2026-10-11 — Shawn: "T10 is out, I like the phone tether idea"). T-Mobile Mobile Internet plans researched 2026-10-11: top tier is 100GB/$50/mo, then throttled to 2G — NOT true unlimited. SIM-in-T10 rejected (IMEI mismatch gets flagged).
- Supporting pieces: VPN on the phone defeats the 480p video throttle (hides traffic type, not volume); Plex on the ThinkPad + download-ahead for binge nights so big numbers never hit the carrier; deprioritization past ~50GB only bites on congested towers.
- Caveats: ToS gray area (heavy sustained abuse is what gets accounts reviewed); laptop must stay awake to be the router.
- ThinkPad: static IP on the van LAN; mDNS `scout-van.local`.
- Scout binds localhost-first; LAN sharing explicit per service. Nothing exposed to the internet by default.
- **Multiple app instances (future-proofed 2026-10-14):** the ThinkPad accepts connections from multiple Scout app instances (multiple phones/devices), not just one. Each instance gets its own conversation session — contexts never interleave. Memory is scoped per device/user, not shared across instances (two people on two phones don't read each other's memory). GPU is shared: simultaneous requests queue and responses slow gracefully; no hard failure. **Per-user wake word (added 2026-10-14):** each app instance chooses its own wake word, stored per device — not global. Users pick from available openWakeWord models (e.g., one device on "hey scout," another on a different phrase). Different wake words per device eliminates most collision. **Same wake word (added 2026-10-14):** when multiple devices hear the same wake word, they form a fair FIFO queue coordinated by the ThinkPad — first to detect gets the floor, the rest wait in order. No device is left out: each queued device gets its turn when the device ahead finishes (or its claim expires). **Queued device is informed (added 2026-10-14):** a waiting device shows its queue status on screen ("Waiting — 2nd in line") so the user isn't confused by the silence; when its turn comes, it gives a clear cue (on-screen + short chime) that it's now listening. The waiting cue stays on the queued device only — it never speaks over the active device's conversation. Claims expire if the user doesn't speak within a short window after getting the floor (so a false trigger or walkaway doesn't stall the queue), and a queued device that gets the floor listens briefly — silence means it releases and goes back to sleep. Custom-trained wake words (record-your-own) are a future option, not day-one — training a model per arbitrary phrase is heavy. Connection limit is a setting, not a constant. Access stays LAN/Tailscale-only (no public exposure).

## Open questions (brainstorm)
1. **Desktop for Shawn mode:** ✅ XFCE (decided 2026-10-11) — most "regular desktop" feel (taskbar, app menu, tray, desktop icons) at ~500MB RAM. MATE was runner-up; Cinnamon/KDE too heavy for Scout's machine.
2. **Handoff:** ✅ voice handoff, zero teardown (decided 2026-10-11) — "Hey Scout, I need the laptop" → starts XFCE, Scout mutes its own voice output and drops to wake-word-only listening (no unprompted speech, no skill actions); "Hey Scout, I'm done with the laptop" → kills the desktop session, full mode resumes. Model stays loaded in VRAM throughout, conversation context untouched, all services keep running — only behavior flags change. Short voice confirmations on each transition ("All yours." / "I'm back."). Idle policy (decided 2026-10-11): 10 min with no input in Shawn mode → Scout asks "still need the laptop?"; no response within 1 min → Scout reclaims the machine (ends desktop session, resumes full mode).
3. **Lid behavior:** lid closed most of the time? External display via Shield for God's Eye?
4. **Backups:** personality/memory/SQLite synced where? (USB stick? Phone? Encrypted cloud?)
5. **Stack updates:** ✅ All three modes (decided 2026-10-14 — Shawn: "All"). One updater, three triggers: (a) **Manual pull** — `git pull` on the ThinkPad, or re-run the installer; full user control. (b) **Voice-triggered** — "Hey Scout, update yourself" → Scout pulls latest from GitHub, applies, restarts affected services; asks for confirmation first ("This will restart me for a minute — go ahead?"). (c) **Scheduled auto-update with rollback** — laptop checks GitHub on a schedule, snapshots the current working state first, applies, runs a health self-test, rolls back to the snapshot if the test fails. Safety rules shared by all three: never auto-update mid-drive — scheduled updates only apply when parked/idle (or in a user-set window); snapshot-before-apply always; rollback on failed health check.
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

## Queued, not yet spec'd
- Screen-off wake-word foreground service (phone Scout; end-of-week per 2026-10-11)
- Universal Outpost v2.8 (monthly nudge active)
- Slimming pass (~60MB target, nothing cut)
