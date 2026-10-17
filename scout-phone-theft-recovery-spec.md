# Scout Phone Theft Recovery — Feature Spec

**Requested by Shawn, 2026-10-14.** Queued for ThinkPad "pull it together" phase (phone-side work in a later app build).

## Overview

Mirror of the laptop theft recovery, but for the phone. If Shawn's phone is stolen, it can be tracked and controlled from two places:
- **The ThinkPad** (laptop Scout)
- **Another designated phone** (trusted device with Scout installed + authorized)

## Activation

- **Automatic**: Unrecognized face unlock attempt → phone locks into decoy mode
- **Manual**: From the ThinkPad (laptop Scout dashboard) or the designated phone → Theft Recovery → Activate
- Command sent via Tailscale to the stolen phone's Scout agent

## Tracking

- **Live location**: GPS + WiFi positioning, sent periodically
- **Location trail**: Timestamped pings on a map — shows the phone's path as it moves
- **Moving track**: Updates as the phone moves

## Seeing

- **Camera snapshots**: Front/back camera photos, sent to the controller (laptop or designated phone)
- **Screen capture** (optional): What the thief sees/does
- **Silent**: No visible indication on the stolen phone

## Decoy Mode ("Shawn mode" for phone)

- Phone shows a convincing fake home screen / lock screen that looks normal
- Thief can "use" the phone — opens apps, browses — all logged
- Real data (messages, photos, accounts) stays locked/encrypted and inaccessible
- Background beacon + logging runs silently

## Remote Control (from laptop or designated phone)

- **Lock down**: Instantly locks the phone, exits decoy mode
- **Wipe**: Factory reset (TWO-STEP CONFIRMATION required — destructive, irreversible)
- **Speak**: Text typed on controller → Scout's voice on the stolen phone's speaker
- **Ring**: Force the phone to ring loudly (find it nearby)

## Unlock (Recovery)

- **Face + voice together**: Phone sees Shawn's face AND hears his voice simultaneously → both must match → unlocks
- **Controller unlock**: From the ThinkPad or designated phone → tap Unlock → remote command via Tailscale → unlocks

## Designated Phone Setup

- In Scout app Settings → Theft Recovery → Designated Controllers
- Add a phone by Tailscale device / Scout account
- That phone's Scout app gets a "Track Shawn's phone" view
- Revocable at any time from the ThinkPad or Shawn's phone

## Architecture

```
Stolen Phone (Scout app)         Controllers
┌──────────────────────┐        ┌──────────────────────┐
│ Scout Agent (bg svc) │        │ ThinkPad (laptop     │
│ - Beacon (location)  │ Tailscale│  Scout dashboard)    │
│ - Camera capture     │◄────────►│                      │
│ - Decoy mode         │ (encrypted│ Designated Phone     │
│ - Remote commands    │  tunnel) │ (Scout app, authorized│
└──────────────────────┘        └──────────────────────┘
```

## Security

- Only authorized controllers (ThinkPad + designated phone) can send commands
- Wipe requires two-step confirmation
- All communication encrypted via Tailscale
- Designated phone authorization is revocable

## Out of Scope (v1)

- Real-time video streaming (snapshots are more practical)
- Automatic theft detection (Shawn or controller activates manually)
- Tracking if phone is powered off (same limitation as laptop)

---

## ⚠️ REMINDER (Shawn's request, 2026-10-14)

Shawn asked to be reminded about this feature if he forgets when it's time to build it. Phone theft recovery is on the future app-build checklist (after the ThinkPad phase). When the phone-side build work starts, bring this up explicitly if he doesn't mention it first.
