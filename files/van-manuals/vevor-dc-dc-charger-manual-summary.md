# VEVOR DC-DC Battery Charger Manual — Transcribed Summary

> **⚠️ UNIT REMOVED — NO LONGER IN THE VAN (Shawn, 2026-10-16: "I got rid of the VEVOR DC to DC").**
> This summary is kept for reference only. The van's DC-DC charger is the **Victron Orion-Tr Smart** (see inventory). Do not answer questions about the van's charging system as if the VEVOR were installed.

**Source:** Paper manual photographed by Shawn, 2026-10-16 (12 photos). Summary for the manuals library — not a copy of the manual.
**Applies to:** VEVOR DC To DC Battery Charger, family of 4 models: **C40A, C30AMPPT, C40AMPPT, C50AMPPT**.
**⚠️ WHICH MODEL IS INSTALLED IS NOT YET CONFIRMED.** The manual covers all four. Read the label on the installed unit to identify it. See "Open question" at the bottom.

## Identification

- **Brand:** VEVOR
- **Family:** DC To DC Battery Charger — charges a house/auxiliary battery from the starter battery / alternator; MPPT models also accept solar input; all models support **reverse charging** (house → starter).
- **Models:**
  | Model | Max charge current | MPPT solar | Rated max power |
  |---|---|---|---|
  | C40A | 40A @ 12V / 20A @ 24V | **None** | 520W |
  | C30AMPPT | 30A @ 12V / 15A @ 24V | 350W, 10–50V | 350W |
  | C40AMPPT | 40A @ 12V / 20A @ 24V | 520W, 10–50V | 520W |
  | C50AMPPT | 50A @ 12V / 25A @ 24V | 650W, 10–50V | 650W |
- **Reverse charging current:** same as forward (C40A 40A/20A, C30AMPPT 30A/15A, C40AMPPT 40A/20A, C50AMPPT 50A/25A). Reverse charging voltage 14.4V / 28.8V.
- **Input battery voltage range:** 12V: 10V–15V · 24V: 20V–31V.
- **Max efficiency:** 93%.
- **Overvoltage protection:** 16V / 31V. **Undervoltage protection:** 10V / 20V.
- **No-load power consumption:** < 0.2A.
- **Startup voltage:** 12V / 24V.
- **Operating temp:** −20 °C to +50 °C (−4 °F to 122 °F). **OTP** value in the printed table is unclear in the photo — do not rely on a transcribed number.
- **Dimensions / weight:** C30A / C30AMPPT / C40AMPPT: 215 × 108 × 60 mm, 0.91–0.97 kg. C50AMPPT: 235 × 145 × 70 mm, 1.41 kg.
- **Terminals:** M6, torque 2.2–2.6 lbf·in / 24.5–29.4 N·cm.
- **Certification:** CE, FCC, RoHS.
- **Package:** charger ×1, XT60 cable ×1 (C40A) or ×2 (MPPT models), XT60 female connector ×1 (MPPT models), user manual ×1, copper terminals ×4, DIP key tool ×2.

## Compatible battery types (set via DIP switch)

DIP switch bank (5 switches) selects the house-battery chemistry / cell count. **Press the reset DIP to 0V before adjusting battery specs.** Toggle up = ON, down = OFF. Exact DIP positions are on p.17 of the paper manual — verify against the paper manual before changing anything; do not set from memory.

Supported types / voltages (from the manual's tables): 1S LA (14.5V), 2S LA (29V), 3S NCA/NCM (12.6V), 4S NCA/NCM (16.8V), 5S NCA/NCM (21V), 6S NCA/NCM (25.2V), 7S NCA/NCM (29.4V), 4S LFP (14.4V), 5S LFP (18V), 6S LFP (21.6V), 7S LFP (25.2V), 8S LFP (28.8V). Plus a 0V Reset position.
- **Damage from incorrect battery-type settings is not covered by warranty.** Check the battery manufacturer's specs before selecting.
- **Connection of 48V batteries is strictly prohibited** (manual troubleshooting). Battery voltage at the charger terminals must not exceed 33V.

## Wiring

- **DC Input (starter side) — 3 terminals:** BATT+ (starter battery positive, large cable), BATT− (ground), IGN (ignition signal — splice into the ignition circuit / D+; the manual shows a fuse-holder splice connector). Use ring terminals.
- **DC Output (house side):** house battery + and −.
- **Grounding:** common negative — connect the starter battery and house battery directly to the negative terminals of the charger. No need to ground both to the chassis separately.
- **Cable gauge:** ring terminals recommended; keep voltage drop ≤ 3%. Thicker wire + shorter distance = less drop. (Manual p.11 table gives min AWG per model and cable length — verify against the paper manual for the installed model.)
- **Solar input (MPPT models only):** XT60 solar input port on the DC input side. **C40A does NOT support solar charging.**
- **Mounting:** flat, sturdy surface, horizontal or vertical. **Minimum 5 cm clearance in all directions** for ventilation. Dry, splash-proof, ventilated, away from heat sources, dust, flammables. Install close to the battery being charged.
- **Fusing:** fuse the battery cables per the manual's guidance; overcurrent protection on the positive line is required.

## Operation

### Forward charging (alternator → house)
- When the engine runs, the charger charges the house battery from the starter battery / alternator. Constant-current (CC) phase first, then constant-voltage (CV) phase.
- **Lithium activation:** the charger automatically reactivates a "sleeping" lithium battery (BMS in protection / 0V) by applying a small charge current until the protection circuit wakes and normal charging starts. This is the safe way to revive a BMS-shut-down lithium pack — NOT jumper cables between packs.

### Reverse charging (house → starter)
- Flip the switch on the unit to the **Reverse Charging** position — **no wiring changes required**. The charger charges the starter battery from the house battery.
- Purpose: prevents starter-battery drain from on-board loads when parked (the "power cut-off upon engine shutdown" problem). When parked with the engine off, house loads can be supplied from the auxiliary battery via the reverse output.
- **C40A note:** during reverse charging, generator and solar inputs automatically disconnect and the unit enters a non-operational state (for the C40A only — it has no solar input).

### LED indicators (p.16)

| Light | Forward charging | Reverse charging |
|---|---|---|
| Green steady on | Fully charged / working normally | Fully charged / working normally |
| Green rapid flashing | MPPT charging | Is charging |
| Green slow flashing | Is charging | — |
| Green off | Power cut off (abnormality) | Power cut off (abnormality) |
| Red steady on | Fault — see troubleshooting | Fault — see troubleshooting |
| Red slow flashing | Incorrect battery type at output terminals | Reverse charging switch not required — turn off the switch |
| Red rapid flashing | — | Reverse charging switch activated — check |

## Troubleshooting highlights (p.19–20)

- **Input over-voltage:** 12V system > 16.5V, 24V system > 33V → disconnect loads, let voltage drop, check charging sources.
- **Input under-voltage:** 12V system < 10V, 24V system < 20V → charge the battery (for lead-acid below 8V, an external charger may be needed to boost the DC-DC charger).
- **Reverse polarity of output:** can cause **irreversible damage to lithium batteries** — verify +/− before connecting.
- **High temperature:** above 122 °F / 50 °C → protection trips; resumes automatically when cooled. Move to a shaded/ventilated location.
- **Short circuit:** disconnect input/output, check wiring, restart.
- **Incorrect battery type:** battery voltage must not exceed 33V; 48V connection strictly prohibited.
- **Circuit breakage:** check all wiring continuity with a multimeter (no beep = open circuit).
- **Maintenance:** inspect monthly — wiring, cable cracking/abrasion, terminal tightness, dust/liquid on the unit, ventilation.

## Open question — WHICH charger is actually in the van? — RESOLVED 2026-10-16: THE VEVOR IS GONE

Shawn confirmed he got rid of the VEVOR DC-DC charger. The van's DC-DC charger is the **Victron Orion-Tr Smart** (original assumption stands). The VEVOR manual is kept for reference only.

*Transcribed 2026-10-16 from Shawn's photos of the paper manual. DIP switch positions intentionally not transcribed from the photos — verify on p.17 of the paper manual.*
