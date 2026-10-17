# Universal Outpost v2.8 — Design

One Outpost APK for every TV box and stick Shawn might plug in, a shared
device registry so Scout can target boxes by name, and graceful
degradation where a device can't do everything.

Phase B deliverables (this document's scope):

| Piece | File |
|---|---|
| Runtime device detection | `ai-assistant-android/outpost/.../DeviceProfile.kt` (new) |
| Registry model (Android side) | `ai-assistant-android/outpost/.../DeviceRegistry.kt` (new) |
| Setup wizard spec + data | `ai-assistant-android/outpost/.../SetupWizardSteps.kt` (new) |
| Registry (laptop side) | `thinkpad/device_registry.py` (new) |
| Client integration hook | `thinkpad/outpost_client.py` — one additive function, `clients_for_voice_command()` |

Phase A (concurrent workstream) owns the v2 API, the accessibility
navigation service, guided-setup UI wiring and MainActivity. Phase B
deliberately produces data and models only; nothing here edits Phase A
files.

## One APK, detection flow

There is no per-brand build. The single Outpost APK detects its device at
runtime (`DeviceProfile.detect(context)`):

1. Read `Build.MANUFACTURER / MODEL / DEVICE / BRAND`, `VERSION.SDK_INT`,
   `VERSION.RELEASE`.
2. Ask PackageManager for system features: `FEATURE_TELEVISION`,
   `FEATURE_LEANBACK`, `FEATURE_TOUCHSCREEN`.
3. Classify the brand from the Build strings (lowercased substring match;
   Fire TV checked first, then Shield, BuzzTV, Homatics, Mecool, Xiaomi,
   Onn, Google TV Streamer). Unknown hardware falls back to `GENERIC_TV`
   or `GENERIC_PHONE_OS` according to form factor.
4. Form factor: television or leanback feature present → `TV`; otherwise
   `PHONE_OS`.
5. Derive the capability tier (below) and the concrete capability set
   from tier + API level only — never from brand alone — so unrecognized
   firmware still degrades predictably.

Detection never throws; on any failure Outpost falls back to a generic
profile and the HTTP command server still runs.

## Capability tiers

| Tier | Meaning |
|---|---|
| `FULL` | TV + leanback. D-pad focus, accessibility steering and gestures expected to work. |
| `STANDARD` | TV device without full leanback, or unknown TV firmware. Core commands work; in-app steering best-effort; background-start exemption not promised. |
| `PROBLEM_CHILD` | Fire TV (see below). |
| `PHONE_OS` | Phone Android on a box/stick. No D-pad focus assumption; tap + type interaction. |

Version gates apply on top of the tier: accessibility gestures need
API 24+, accessibility screenshots need API 30+. A capability is only
advertised when both the tier and the API level support it.

### Per brand

- **Full tier (expected):** NVIDIA Shield, Onn (Google TV models),
  BuzzTV, Google TV Streamer, Xiaomi (Mi TV / TV Stick), Mecool,
  Homatics — all stock Android TV / Google TV devices with leanback.
  Which tier a specific unit lands in is decided by its reported
  features at runtime, not by this list.
- **Fire TV — problem child.** Fire OS is an Amazon fork, and it shows:
  - Accessibility services can be switched off by the system and their
    behavior differs from stock Android TV → steering/typing are
    attempted, never guaranteed; the profile advertises neither
    `ACCESSIBILITY_NAV` nor `GESTURES`/`SCREENSHOT` as reliable.
  - The "Display over other apps" exemption does not behave like stock
    Android → background app-opening is best-effort; `OVERLAY_BACKGROUND_START`
    is not advertised.
  - Settings intents are unreliable → the setup wizard gives manual
    menu paths for Fire TV instead of intent buttons.
  - Sideload/update flow differs (Downloader app / manual reinstall;
    "Apps from Unknown Sources" lives in Developer options).
  - What always works: the HTTP command server itself — launch, media,
    volume, power, typed text (v1 protocol).
- **Phone-OS boxes.** Cheap sticks/boxes running phone Android: no
  leanback, no D-pad focus model. Scout interacts the way a finger
  would — accessibility **taps at coordinates** and typed text. The
  v1 `dpad` command is meaningless on these and the registry/profile
  lets callers know (`TAP_INPUT` present, `DPAD_NAVIGATION` absent).

## Degradation matrix (feature × tier)

| Feature | FULL | STANDARD | PROBLEM_CHILD (Fire TV) | PHONE_OS |
|---|---|---|---|---|
| HTTP command server (launch/media/volume/power) | ✅ | ✅ | ✅ | ✅ |
| Typed text into focused field | ✅ | ✅ | ✅ | ✅ |
| D-pad navigation commands | ✅ | ✅ | ⚠️ sent, focus behavior varies | ❌ no focus model |
| Accessibility in-app steering | ✅ | ✅ best-effort | ⚠️ may be revoked by Fire OS | ✅ (drives taps) |
| Coordinate tap / swipe gestures (API 24+) | ✅ | ✅ | ❌ not advertised | ✅ primary input |
| Background app open via overlay exemption | ✅ | ⚠️ not promised | ❌ not advertised | ⚠️ not promised |
| Screenshot (API 30+) | ✅ | ✅ | ❌ not advertised | ✅ |
| ADB / network debugging setup | ✅ Shield: Settings → Device Preferences → Developer options → Network debugging | ✅ Wireless debugging on Android 11+ units | ⚠️ ADB Debugging under My Fire TV → Developer options | ✅ USB/Wireless debugging |

✅ = advertised in `DeviceProfile.capabilities()` · ⚠️ = attempted or
available with caveats · ❌ = not advertised; callers must not offer it.

## Registry + voice targeting

One registry concept, two implementations with identical semantics:

- **Android:** `DeviceRegistry.kt` — pure-Kotlin model (no Android
  imports), persistence left to the caller (SharedPreferences in the
  phone app's device screen, per `V2.8-DEVICE-DESIGN.md`).
- **Laptop:** `device_registry.py` — same rules, persisted as JSON at
  `~/.scout/tv-devices.json` (path configurable via constructor or the
  `SCOUT_TV_REGISTRY` environment variable). Stdlib only.

Entry fields: `id` (UUID), `displayName` ("living room box"), profile
summary, brand, tier, `ip`, `port` (8087), `apiVersion` ("v1"/"v2"),
capabilities, `ssid` (when known), `isDefault`, `lastSeen`.

Resolution rules (`resolve` / `resolve_target`):

1. Broadcast words — "all", "everywhere", "both", "all devices" —
   anywhere in the query → **all** devices.
2. Exact name match (case-insensitive) beats everything else.
3. Case-insensitive substring match ("living room" matches "living
   room box"; also the reverse — the spoken phrase contains the name).
   One hit → that device. Several → **ambiguous**: Scout asks which one.
   Zero → **not found**.
4. Bare command (no target) → the default device; if no default, the
   only device; if several and no default → ambiguous (ask).

Voice parsing on the laptop (`parse_voice_target`): finds "on the …",
"on my …", "on both", "to the …" at the end of the command and hands
the remainder to the resolver. "Open Netflix on the living room box"
→ `living room box`; "pause on both" → broadcast; "play some music"
→ no target → default device. Leading filler ("on the", "my", "to")
is stripped before matching on both implementations.

Laptop integration: `outpost_client.clients_for_voice_command(text)`
returns the `ResolveResult` plus ready `OutpostClient` objects for the
resolved IPs — Scout's command router calls it, then sends the v1/v2
command to each client. Existing single-host `OutpostClient` usage is
unchanged.

## Setup wizard flow

Data lives in `SetupWizardSteps.kt` (step definitions only — Phase A
renders them in MainActivity later). Every device gets the common
steps, then brand-specific steps:

1. **Start Outpost listening** (all devices).
2. **Steering + typing** — enable "Outpost navigation helper" in
   Settings → Device Preferences → Accessibility. *(optional)*
3. **Open apps any time** — "Display over other apps" for Outpost.
   *(optional; noted as unreliable on Fire TV)*
4. **Brand step(s):**
   - *Shield:* Network debugging (Developer options; note it resets on
     reboot).
   - *Fire TV:* ADB Debugging + unknown-sources under My Fire TV →
     Developer options, plus a "Fire TV differences" explainer step.
   - *Other Android TV brands:* USB/Wireless debugging under Device
     Preferences → Developer options (menu names vary slightly).
   - *Phone-OS:* tap-mode explainer (accessibility helper is required,
     not optional, on these) + USB debugging under About phone.
5. **Install updates permission** step is defined for when the updater
   path needs it (Fire TV keeps this under Developer options).

Each step carries a `verificationKey` — `accessibility`, `overlay`,
`install`, `adb` — matching the fields of Phase A's setup-status, so
the wizard UI can tick steps off automatically once Phase A exposes
that status, plus an optional settings intent action string where a
reliable one exists (none on Fire TV).

## Integration points with Phase A (v2 API)

- Phase A's `/status` / v2 setup-status should include the
  `DeviceProfile` summary (brand, tier, capabilities) so the phone and
  laptop can register a box with accurate fields instead of guessing.
  Registry `register()` already accepts `brand`, `tier`,
  `api_version`, `capabilities` for exactly this.
- Wizard `verificationKey`s are Phase A's setup-status field names;
  when Phase A publishes the status shape, the wizard UI binds
  step-done state to those fields with no data changes here.
- Broadcast/ambiguous resolution happens **before** any command is
  sent; Phase A's auth and v2 endpoints are per-device, so a broadcast
  is N independent authenticated calls — partial failure (one box
  offline) must be reported per device, not as a total failure.

## What's NOT done

- **No UI wiring.** MainActivity, layouts and the guided-setup screens
  belong to Phase A; `SetupWizardSteps` is data waiting for that UI.
- **No APK build.** The Gradle lock is held by Build 1; the new Kotlin
  files are compile-plausible (framework-only, no new dependencies) but
  unverified by a build. First post-lock build must compile the outpost
  module and fix anything that surfaces.
- **No persistence on the Android side yet** — by design; the registry
  model is storage-agnostic until the phone's Devices screen lands.
- **No live-device verification.** Brand classification strings and
  per-brand settings paths are from vendor documentation/known device
  behavior; each physical box still needs one on-device pass (Shawn,
  per device, same session as Phase A's on-device steps).
- **No mDNS auto-discovery wiring** — Phase A owns discovery; when it
  lands, discovered boxes should be fed into this registry rather than
  a parallel list.
