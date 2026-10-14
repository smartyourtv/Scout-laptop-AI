# Name Sync Protocol — One Name, Two Bodies

The phone app and the ThinkPad share ONE assistant name. The ThinkPad holds
the canonical name. Change it on either body and the other picks it up —
live when connected, on next contact when apart.

- Server: `name_sync.py` (ThinkPad, stdlib-only, port **8091**)
- Client: `NameSyncClient` (Android app, `com.app.assistant.van`)
- Spec: P16 (rename) / P17 (name sync) in `scout-thinkpad-home-spec.md`

## Design rules

1. **ThinkPad is canonical.** The server's store is the source of truth.
   The app never treats its local name as authoritative over the server's.
2. **Identity is never the name.** Sessions, memory, and the wake-word queue
   key off device IDs + the network address (`scout-van.local`). Renaming
   cannot break app↔laptop interaction.
3. **Persona prompt follows the name.** Both sides compose the prompt as
   `"Your name is <name>."` + the stored system prompt at prompt-build
   time (app: `MainViewModel`; laptop: `talk.py` via `persona_prefix()`).
   The persona file itself never hard-codes a name.
4. **Timestamps are parsed, never string-compared.** ISO-8601 UTC on the
   wire; receivers parse to epoch millis / `Instant` / `datetime`.
   `"Z"` vs `"+00:00"` and fractional digits make string comparison wrong.

## Name record (JSON)

The exact shape served by `GET /name` and returned in `POST /name`:

```json
{
  "name": "Scout",
  "updated_at": "2026-10-14T16:00:00.123456+00:00",
  "updated_by": "android-7f3a9c2e",
  "wake_word_available": true,
  "persona_prefix": "Your name is Scout."
}
```

| Field | Meaning |
|---|---|
| `name` | Display name. 1–40 chars, no newlines/control chars, trimmed. |
| `updated_at` | ISO-8601 UTC timestamp of this version. Drives last-write-wins. |
| `updated_by` | Device id that authored this version (`android-<ANDROID_ID>` on the app, `laptop` on the ThinkPad). |
| `wake_word_available` | Whether an openWakeWord model file exists for this name (server-side check). Informational — the name still changes when false. |
| `persona_prefix` | `"Your name is <name>."` — what both sides prepend to the system prompt. |

## Endpoints

Base URL: `http://scout-van.local:8091` (LAN/Tailscale only; the server
binds `127.0.0.1` by default, `0.0.0.0` for LAN sharing).

### `GET /name[?since=<iso>&wait=<secs>]` → 200 + name record

Fetch the canonical record.

- **Long-poll (live push):** with `wait > 0` (cap 60s) and a `since`
  timestamp, the server holds the request until the record is newer than
  `since`, or `wait` seconds pass. This is how the app gets near-live
  pushes without running a listener on the phone.
- `since` MUST be URL-encoded (`+` in `+00:00` → `%2B`); an unencoded
  `+` arrives as a space and the timestamp fails to parse.
- Without `wait` (or without `since`), returns the current record at once.

### `POST /name` → 200 or 409 + `{applied, reason, record}`

Submit a name change. Body:

```json
{"name": "Buddy", "updated_at": "2026-10-14T16:05:00.000Z", "updated_by": "android-7f3a9c2e"}
```

- `updated_at` missing → server stamps now. `updated_by` missing → `"unknown"`.
- **200** `applied: true` — the change won; `record` is the new canonical.
- **409** `applied: false, reason: "stale: …"` — the server holds a newer
  or equal record; `record` is the winning record so the caller can
  converge without another round trip.
- **400** — invalid JSON body, or the name fails validation (blank,
  over 40 chars, newlines/control chars). Nothing is stored.

### `POST /register` → 200 + `{ok: true}`

Register a connected app: `{"device_id": "…", "role": "app"}`. Diagnostics
only (who is connected); it does not affect sync. `device_id` is required.

### `GET /health` → 200 + `{status, record, registered_devices}`

Server status, the current record, and the device registry.

## Conflict rule — last-write-wins by timestamp

- A proposal applies only when its parsed `updated_at` is **strictly newer**
  than the stored record's. Equal timestamps lose (the stored record stands
  — ties are not a coin flip).
- A stale rejection returns the winning record so the loser converges.
- Clients apply a pushed record only when it is strictly newer than their
  `last_applied_at` watermark, so a stale push can never clobber a
  fresher local rename.

## Offline / queue behavior

- **App apart from the van:** a rename is saved locally immediately, then
  the submit attempt fails → the change is queued (one slot: the latest
  unsent rename, persisted in SharedPreferences as
  `name_sync_pending_json`). On the next `reconcileOnConnect`, the queue
  flushes first, then the canonical record is fetched.
- **Flush outcomes:** applied → watermark advances, queue clears.
  Stale (409) → the queued change is obsolete; queue clears and the
  server's newer record is applied locally. Network failure → the change
  stays queued, nothing is lost.
- **ThinkPad side:** the server IS the store, so it needs no queue for
  itself. `NameSyncClient` (Python) has the same queue/flush pair for
  laptop-side tools that submit while the server is down.
- **Both changed while apart:** whoever reconnects second loses —
  last-write-wins by timestamp. The loser converges to the winner.
- **Sync-on-reconnect is the honest guarantee.** A device that cannot
  reach the other cannot know about its changes yet.

## Wake-word rule

The wake word follows the name **only if** an openWakeWord model file
exists for it: `hey_<slug>.onnx` in the wake-word dir
(`~/.scout/wakewords`, overridable via `SCOUT_WAKEWORD_DIR`).
Slug: lowercase, non-alphanumerics → `_` (`"Mary Jane"` → `hey_mary_jane.onnx`).

- Model exists → the wake word follows the new name.
- No model → the name still changes, but the wake word stays on the old
  name, and the response (`wake_word_available: false`) tells the caller
  to say so — Scout must tell the user instead of going silently deaf.
- Custom-trained (record-your-own) wake words are a future option, not
  part of this protocol.

## Security posture

LAN/Tailscale-only. No auth on the endpoints (same trust model as the
Outpost protocol on the van LAN: physical/network access = authority).
Nothing is exposed to the internet; the server binds localhost-first.
