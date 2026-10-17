# Rooftop A/C Manual — Transcribed Summary (Leibing TR-L02 — LOOKALIKE UNIT)

**Source:** Paper manual photographed by Shawn, 2026-10-16 (12 photos). Summary for the manuals library — not a copy of the manual.
**Applies to:** the van's rooftop air conditioner — a later addition (the van left the factory with no rooftop A/C).
**⚠️ CORRECTION (Shawn, 2026-10-16): this manual is NOT from the exact manufacturer of the van's unit — the unit only looks identical.** The actual unit is an **ApexscnView, model PLTRC** (12V, 8530 BTU cooling, 3400 BTU heating, 800W power consumption, R134a, 43 lbs — Amazon listing, currently unavailable). **No unit-specific ApexscnView manual found online** (searched 2026-10-16: manuals.plus has no PLTRC/ApexscnView entry; PLTRC001 / Wlinflatable searches return unrelated manuals; Amazon listing has no documents section). Treat every TR-L02 spec below (current draw, fault codes, wire size) as provisional reference only — the ApexscnView specs govern. **Fuse call corrected 2026-10-16: 80A ANL** (was 70A — the 70A call assumed the TR-L02 manual's 50A figure; the ApexscnView's 800W spec implies ~67A at 12V, up to ~76A at low voltage, so 70A is too tight).

## Identification

- **Product name:** Leibing No. 2 overhead integrated air conditioner
- **Model:** TR-L02, top-mounted (roof) unit
- **Manual date:** 2022.2.1
- **Dimensions:** 680 × 200 × 621 mm (external machine 680 × 220 × 621; interior panel 480 × 320 × 160)
- **Body colors:** white / red / blue
- **Voltage:** 12–72V (12–24V for the single-cooling type — the van's unit runs on 12V)
- **Refrigerant:** R134a, 600 g charge (manual: injected amount should not exceed 500–600 g)
- **Safety / protection:** IP54, overvoltage / undervoltage / overcurrent / short-circuit protection. Compressor standard JB/T12845-2016.
- **Packing list:** 1 external machine, 2 fixed stretch bars, sponge strips, interior panels (optional control panel / manual knob), remote control, universal screw pack, water pipe (optional), installation drawings, instruction manual.

## Performance specs

| Spec | Value (from manual) |
|---|---|
| Current draw | 30–50A |
| Rated power | 300 / 1200W |
| Cooling capacity | 800–2200W |
| Coefficient of performance | ≥ 2.5 |
| Compressor speed range | 1600–3800 r/min |
| Air volume | 250–450 m³/h |
| Fan motor rated voltage | 12V / 24V |
| Compressor motor voltage | 12V–72V (optional / customizable) |
| Power cord | 16 mm² (2–5 m run) |
| Operating ambient | −15 °C to +48 °C (tested −28 °C to +50 °C with PTC/heat-pump heating) |

**Power-planning note:** at 30–50A on 12V, this is the van's biggest single electrical load. On the 500Ah house bank, sustained full-tilt A/C is roughly a 10–16 hour proposition before the bank is flat (inferred from 500Ah ÷ 30–50A — actual runtime depends on duty cycle, compressor speed, and other loads). Size expectations accordingly; the manual itself recommends a ≥200Ah battery bank and a ≥70A generator/alternator for sustained use.

## How it works

Standard vapor-compression refrigeration: compressor → condenser → receiver → expansion valve → evaporator → back to compressor, with fans and pipelines. Heating is via PTC / heat pump (on heating-capable variants). The unit mounts through the roof (sunroof opening or a cut hole) with an interior panel inside.

## Controls

- **Power:** press and hold the power button 3 seconds to turn on; press and hold 3 seconds to shut down.
- **Fan speed:** +/− keys, 5 gears (1–5).
- **Mode key:** cycles AC → heating → air supply (fan only).
- **Temperature:** +/− keys, 1° per press.
- **Modes:** Strong, ECO (energy saving), Sleep, plus High / Medium / Low battery indicators.
- **Display icons:** wind speed, fault, temperature, voltage, decimal point.
- **Remote control:** power (short press), mode cycle, fan speed, temp +/−, Strong key, Energy-saving key, lighting/auxiliary keys.
- **Heating note (manual):** with the AC light on, adjust temperature below 20 °C for cooling; adjust above 30 °C for heating.
- **Start/stop temperature difference:** at least 3 °C between start and stop setpoints, or the compressor will cycle frequently.
- **After shutdown:** turn off power and wait 5 minutes before restarting. After releasing refrigerant, wait 5 minutes.

## Fault codes — control panel

| Code | Meaning (manual) |
|---|---|
| EC | Temperature sensor faulty — check the sensor / panel temperature probe connector |
| EF | Indoor fan short circuit, carbon-brush or overcurrent problem — check the fan |
| E1 | Undervoltage / overvoltage — check power supply wiring and voltage |
| E2 | Controller overcurrent — check heat dissipation of the external machine, refrigerant overcharge, installation location |
| E3 | Controller stall protection — compressor stuck in cylinder |
| E4 | Controller under-voltage protection — check power supply |
| E5 | Short-circuit protection — check controller-to-compressor wiring for wear/short |
| E6 | Controller overvoltage protection — system voltage over 30V |
| E7 | 3 consecutive startup failures (usually caused by E3 or E12) |
| E8 | Outdoor fan failure — check fan connection cable |
| E9 | Temperature switch / pressure switch — system pressure or temperature switch |
| H2 (36–72V type) | Controller phase-loss protection — check compressor connection |
| H3 (36–72V type) | Controller power-device over-temperature protection |
| H4 (36–72V type) | Controller failure |

## Fault codes — Black Shell Controller (flash patterns)

| Flashes (then 1 s pause) | Meaning |
|---|---|
| Slow even flash | Normal standby |
| Light off | Compressor running normally |
| 2 flashes | Running current too large — current exceeds 50A |
| 3 flashes | Locked-rotor protection |
| 4 flashes | Under-voltage protection |
| 6 flashes | Electronic fan faulty |
| 7 flashes | Motor out of phase |
| 8 flashes | Compressor temperature protection |
| 9 flashes | System pressure switch protected |
| 12 flashes | Phase-loss protection |
| 13 flashes | Power-board over-temperature |

## Installation notes (from the manual)

- **Roof opening:** TR-L02 needs a sunroof/opening greater than 225 × 299 mm and less than 440 × 580 mm. Without a sunroof, cut the opening to suit.
- **Mounting:** tension bar + nuts (Nut 1, Nut 2, main screw), interior panel, decorative rubber plug. 4× M8 screw holes.
- **Interior panel install (12 steps):** clean the opening → stick cotton strips → set the unit → adjust brace → fix brace → connect harness → connect power → tie/fix → paste sponge strips → secure interior panel → install trim.
- **Wiring gauge (manual):** 16 mm² lines for compressor runs of 2–5 m; 10 mm² for battery runs under 2 m; 25 mm² for multiple-battery setups. Keep runs as short as possible; voltage drop causes low-voltage faults.
- **Vacuum before charging:** pump to −0.098 MPa, hold 10 minutes, pump for more than 20 minutes total. System must be moisture-free (moisture ≤ 75 PPM).
- **Refrigerant:** genuine R134a only. Charge 500–600 g. Pressures (manual, kg/cm² gauge): low side ~2.5, high side ~13; at 35 °C ambient, high pressure ~14.
- **Controller protections:** air-pressure protection 21.5V ± 1V; after under-voltage, restart at 25.5V ± 0.5V.
- **Condenser:** clean at least once a week — a dirty condenser seriously hurts cooling.
- **Pipeline:** keep the evaporator-to-compressor line as short as possible, with thermal insulation.
- **Compressor:** mount within 5° of level; close the system within 5 minutes of opening to keep moisture out; compressor bolt torque 11 ± 1 N·m.
- **Generator use:** battery must be fully charged first; generator should be ≥ 75A. If the generator is under 55A, the A/C will not run properly. Positive to battery positive, negative to negative — never reversed.

## Troubleshooting highlights (§11–12)

- **Low-voltage display:** check electrode contact, wiring, harness thickness/length, generator size/age, battery short, whether the generator is too small.
- **Battery won't charge / can't hold:** check generator output, battery condition, wiring.
- **Poor cooling:** refrigerant charge (too much/little), dirty condenser, blocked expansion valve, compressor issues, voltage drop from thin/long wiring, ambient temperature, sun load.
- **Compressor won't start:** voltage below threshold, pressure-switch protection, controller fault codes above.

*Transcribed 2026-10-16 from Shawn's photos of the paper manual. Pressure values are the manual's own kg/cm² gauge figures.*
