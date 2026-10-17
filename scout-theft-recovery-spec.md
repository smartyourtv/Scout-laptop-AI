# Scout Theft Recovery — Feature Spec

**Requested by Shawn, 2026-10-14.** Queued for ThinkPad "pull it together" phase.

## Overview

A theft-recovery system in the Scout phone app that takes control of a stolen ThinkPad. When activated, the laptop switches to "Shawn mode" (decoy desktop) and the phone becomes a remote command center.

## Activation

- **Automatic**: Unrecognized face opens the laptop → locks INTO "Shawn mode" (decoy desktop)
- **Manual**: Shawn opens Scout app → Theft Recovery → Activate
- Command sent via Tailscale to the laptop's Scout agent
- Laptop switches to "Shawn mode" decoy desktop (if not already in it)
- Real files stay LUKS-encrypted and unmounted
- **Locked in**: The thief cannot exit the decoy — no user switching, no access to the real account, no escape to the real system

## Decoy facade — no updates (reversed 2026-10-15)

- The decoy ("Shawn mode") shows NO update option and NO update notification. A manual update mechanism in the decoy was considered and rejected (Shawn: "scratch that") — it is a risk surface: the thief could probe it, and a fake update could break the illusion or the beacon. A real desktop sitting un-updated is normal, so the facade does not need it.
- The real updater never runs in decoy mode. The real laptop's manual update option + notification still stands; only the decoy has none.

## Tracking

- **Live location**: WiFi positioning + IP geolocation, sent periodically
- **Location trail**: Every ping timestamped and recorded — shows the laptop's path on a map
- **Moving track**: Updates as the laptop moves (new WiFi networks = new location)

## Seeing

- **Webcam snapshots**: Periodic photos from the laptop's camera, sent to the phone
- **Screen capture** (optional): What the thief sees/does on screen
- **Silent**: No visible indication on the laptop that it's being watched

## Silent Communication with Laptop Scout

- Phone sends commands via Tailscale (encrypted tunnel, authenticated)
- Laptop Scout executes silently — nothing visible on screen
- Commands: status check, location request, camera snapshot, screen capture, speak, lock, wipe

## Remote Control

- **Lock down**: Instantly locks the laptop (exits decoy mode, locks screen)
- **Wipe**: Secure erase of the drive (TWO-STEP CONFIRMATION required — destructive, irreversible)

## Unlock (Recovery)

When the laptop is recovered, Shawn unlocks it out of "Shawn mode" by one of these:

- **Face + voice together**: Laptop sees Shawn's face AND hears his voice simultaneously → both biometrics must match → unlocks. (Shawn's choice: voice alone is too easy to spoof, so face + voice together is required.)
- **Phone unlock**: Shawn taps Unlock in the Scout app → remote command via Tailscale → unlocks. (Strongest layer — requires authenticated phone.)

After unlock, the laptop returns to normal mode with the real desktop and files.
- **Speak**: Two voice options:
  - **Shawn's voice**: Phone mic → streamed to laptop speakers (live)
  - **Scout's voice**: Text typed on phone → TTS on laptop → played through speakers

## Architecture

```
Phone (Scout app)                Laptop (ThinkPad Scout)
┌──────────────────┐            ┌──────────────────────────┐
│ Theft Recovery   │  Tailscale │ Scout Agent (background) │
│ Dashboard        │◄──────────►│ - Beacon (location)      │
│ - Live map       │  (encrypted│ - Camera capture         │
│ - Camera feed    │   tunnel)  │ - Decoy desktop ("Shawn   │
│ - Controls       │            │   mode")                 │
│ - Voice          │            │ - Remote command handler │
└──────────────────┘            └──────────────────────────┘
```

## Security

- Only Shawn's phone (authenticated via Tailscale) can send commands
- Wipe requires two-step confirmation in the app
- All communication encrypted via Tailscale
- This is Shawn's own laptop — remote control is legitimate

## Out of Scope (v1)

- Real-time video streaming (snapshots are more practical for bandwidth)
- Remote control of the thief's other devices
- Automatic theft detection (Shawn activates manually)

---

## ⚠️ REMINDER (Shawn's request, 2026-10-14)

Shawn asked to be reminded about this feature if he forgets when it's time to build it. Theft recovery (laptop + phone mirror) is on the "pull it together" checklist. When Shawn says "pull it together," bring this up explicitly if he doesn't mention it first.
