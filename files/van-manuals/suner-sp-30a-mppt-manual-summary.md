# SUNER SP-30A-MPPT Manual — Transcribed Summary

**Source:** Paper manual photographed by Shawn, 2026-10-16 (6 photos). Summary for the manuals library — not a copy of the manual.
**Applies to:** SUNER POWER SP-30A-MPPT, the interim solar controller in the van.
**Key confirmation:** The spec table lists this unit as **AS-MPPT-30A** — confirming the white-label identity (SUNER SP-30A-MPPT = AS-MPPT-30A).

## Identification

- **Brand:** SUNER POWER (www.sunerpower.com)
- **Model:** SP-30A-MPPT (spec table: AS-MPPT-30A)
- **Type:** 30A MPPT solar charge controller, 12V/24V auto-detect
- **Warranty:** 12 months. Support: support@sunerpower.com · Technical: technical@sunerpower.com
- **Package:** 1× controller, 4× mounting screws, 1× 3 m temperature sensor cable, 1× user manual

## Electrical specs (30A model)

| Spec | Value |
|---|---|
| Rated battery current | 30A |
| Battery system | 12V / 24V (auto-detected at first power-up) |
| Max PV open-circuit voltage | 100V — never exceed |
| Min PV voltage to start charging | PV voltage at least 5V above battery voltage |
| Min PV open-circuit voltage to light up controller alone | 15V |
| Min battery voltage to light up controller | 3V |
| Max PV input power | 12V system: ~400W · 24V system: ~800W |
| Self-consumption | ≤ 40–60 mA |
| USB port | 5V / 2A |
| Temp compensation | −3 mV/°C/2V |
| Max terminal size | 10 mm² / 8 AWG |
| Operating temp | −40 °C to +80 °C |
| Humidity | ≤ 95% (non-condensing) |
| Protection rating | IP64 |
| Dimensions / weight | 172 × 136 × 46.7 mm · 0.58 kg |
| Protections | Reversed battery polarity, reverse PV polarity, PV over-current, PV over-voltage, battery over-voltage, over-temp |
| Ports | RS232, CAN, USB, temp sensor |

## Battery modes — 6 modes, set with the MODE button

| Mode | Boost | Float | Boost recovery | Float duration |
|---|---|---|---|---|
| 12V Wet / Gel / Flooded | 14.4V | 13.8V | 12.8V | 2 h |
| 12V AGM | 14.6V | 13.8V | 12.8V | 2 h |
| **12V Lithium** | **14.6V** | **none (—)** | 12.8V | 2 h |
| 24V Wet / Gel / Flooded | 28.8V | 27.6V | 25.6V | 2 h |
| 24V AGM | 29.2V | 27.6V | 25.6V | 2 h |
| 24V Lithium | 29.2V | none (—) | 25.6V | 2 h |

- **Lithium mode has NO float stage** — correct for LiFePO4 (matches the van's existing setup: 14.6V boost, no float).
- **Cautions from the manual:** use Lithium mode only for 12V/24V lithium batteries with a built-in BMS. **Never use 24V mode to charge a 12V battery** — irreparable damage. Check with the battery manufacturer to confirm the right mode.

## Installation rules

- **Connect battery FIRST, then panels.** The controller detects 12V vs 24V at first power-up from the battery. If the solar charger is powered by PV alone it cannot measure battery voltage and defaults to 12V — set the system voltage manually if needed. After auto-detection, it will not auto-change type.
- **Fuse the battery supply** with an external fuse (per the manual's fuse table — size per wire gauge).
- **Wire gauge:** at least #12 AWG for both input and output; #10 AWG for longer runs. Keep the battery-side cable under 5 ft if possible, or use #10/#8.
- **Panel wiring:** panels in series, parallel, or series/parallel are all supported. Nominal PV voltage must be at least 5V above battery voltage. Max open-circuit PV voltage must not exceed 100V.
- **Two charge controllers CAN charge the same battery** (manual FAQ #8) — supports the van's split-controller plan.
- **Mounting:** vertical surface, protected from direct sunlight, high temps, and water. Good ventilation.
- **Remote temperature sensor** (included): tape to the side of the battery (3 m cable). Used for temperature-compensated charging.
- **Remote LCD display:** optional, NOT included.

## Charging stages (3-stage)

1. **Bulk** — full available solar power, constant current, until ~80–90% charge.
2. **Absorption** — constant voltage, current tapers. Ends when the battery reaches ~98% or the absorption time expires.
3. **Float** — reduced voltage, trickle/maintenance. Lithium mode skips this stage.
- LED indicators show Bulk / Absorption / Float; a red error LED + buzzer indicates faults (battery over-voltage, reversed polarity, over-temp, PV over-voltage, etc.).

## FAQ highlights (manual §9)

- **Min voltage to light up:** 15V PV open-circuit (panels alone) or 3V battery.
- **Temperature compensation:** charge voltage adjusts with battery temperature — important for lead-acid in heat/cold.
- **Under-producing panel:** sun intensity, panel angle, clouds, temperature, dirt on the panel surface.
- **Panel temperature:** heat drops MPPT voltage and charge current — gains return in cooler off-hours.
- **Wire length:** long wires lose power, especially at higher currents. #12 minimum, #10 for long runs.
- **Display vs multimeter voltage difference:** V = I×R — cable resistance between controller and battery causes a drop. Keep battery cables short.
- **Two controllers, one battery:** yes.
- **Panel orientation:** face south (SE to SW range) for max energy.
- **Maintenance:** clean panels with non-abrasive cleaner; keep fuse holders and connections dry and clean.

*Transcribed 2026-10-16 from Shawn's photos of the paper manual.*
