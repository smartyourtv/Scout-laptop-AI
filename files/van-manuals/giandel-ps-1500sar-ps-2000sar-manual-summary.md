# Giandel Inverter Manual — Summary (PS-1500SAR / PS-2000SAR)

**Source:** Giandel PS-1500SAR / PS-2000SAR shared user manual (manual version V0.21.03), fetched 2026-10-16. This file is a summary in my own words — not a copy of the manual. The full PDF lives in this folder as `giandel-ps-1500sar-ps-2000sar-manual.pdf`.
**Applies to:** the van's inverter — **Giandel PS-2000SAR** (2000W continuous). Where the manual covers both models, the PS-2000SAR figures are the ones that matter here.

## Identification

- **Models covered:** PS-1500SAR (1500W) and PS-2000SAR (2000W) — one shared manual, checkbox on the cover.
- **Type:** DC-to-AC pure sine wave inverter, 12V or 24V input versions.
- **Support (from manual):** support@giandel.com.au; giandel.com.au.
- **Warranty notes (from manual):** keep the receipt/invoice — it must go back with the unit for a repair/replacement claim. Warranty is voided by reversed DC polarity, unauthorized disassembly/repair, and damage from incorrect installation or operation.

## Specs — PS-2000SAR (12V version, the van's unit)

| Spec | Value |
|---|---|
| Continuous power | 2000W |
| Peak (surge) power | 4000W |
| Rated input voltage | 12V DC |
| Input voltage range | 9.5–16V DC |
| Over-voltage shutdown | 16V DC |
| Low-voltage shutdown | 9.5V DC |
| Low-voltage alarm | 9.8V DC |
| Output voltage | 110–120V AC ±10% (per label) |
| Frequency | 50 / 60 Hz ±1 Hz (per label) |
| Waveform | Pure sine wave |
| Efficiency | ~90% |
| Overload protection range | 2000–2400W |
| Short-circuit protection | Yes |
| Overheat protection | ~149 °F shutdown |
| Display | LCD (battery status, input voltage, output wattage) |
| USB | 5V DC, max 2.4A × 2 |
| No-load current | ~1.5A (12V version) |
| Cooling fan | Starts at ~104 °F case temp or above ~40% of rated load |
| Operating temperature | 32–104 °F |
| Storage temperature | 14–113 °F |
| Size (L×W×H) | 443 × 203 × 100 mm |
| Weight | ~4.98 kg |
| AC hard-wire terminals | PS-2000SAR 120V only (not on the 1500W model) |
| Single-socket max (110–120V) | 15A / 1500W per socket |

**Van note:** a single AC socket tops out at 1500W. Anything bigger must go through the hard-wire terminals (with the ground terminal tied to the appliance ground). The 500Ah bank at 12V can in theory feed the inverter at full load, but at 2000W the DC draw is roughly 185A after inverter losses — plan wiring and fusing for that, not for the average load.

## What is in the box (per manual)

Inverter, battery cables, remote controller box + wire, user manual, mounting hardware.

## Installation — key points

- **Location:** dry, cool (ideally 50–77 °F), ventilated, clean (no dust/wood chips that the fan can pull in). Keep clearance around the vents; do not put anything on top or cover the fans. Keep flammables away — the case gets hot in use, and battery connections can spark.
- **Mounting:** heavy unit — mount on a solid platform (floor, table, bracket) that can carry the weight, secured with four screws.
- **Grounding:** the rear-panel ground terminal must be connected — to the vehicle chassis in a vehicle, to the boat grounding system in a boat, to earth in a fixed install. Ground wire 14 AWG (2.08 mm²) or larger. Do not run the inverter ungrounded.
- **Battery cable sizing (manual's table, 12V):** for a 2000W load at up to 1 m: 3 AWG; 1–2 m: 0 AWG; longer runs: parallel runs of 3 AWG (total cross-section must meet the table). Thicker wire can substitute for two thinner parallel wires if the total cross-section matches.
- **Current estimate (manual's rule):** battery current ≈ load watts ÷ battery volts × 110%. Example from the manual's method: 1000W on 12V ≈ 92A. At 2000W on 12V, ≈ 183A.
- **Runtime estimate (manual's rule):** battery capacity (Ah) ÷ current. Example from the manual's method: 2000Ah at 1000W ≈ 21.8 h. The manual notes this assumes a 20-hour discharge rate — above ~100A discharge on a 2000Ah bank, real runtime drops, and the battery maker's own specs govern.
- **Connections:** negative (black) battery cable to the inverter's negative terminal first, then positive (red) to positive. Tight connections — loose DC connections cause voltage drop and overheating.
- **Remote box:** screw-mounts flat (two screws) or fits an 86×86 mm standard electrical box; connect with the supplied wire. The inverter also works without the remote, switched from its own power switch.
- **Battery separation:** batteries can give off a little flammable gas — keep them away from the inverter, ideally in a different space. Remove metal jewelry (rings, watches) before working around the battery. Eye protection + work clothes; keep soap and water handy for acid contact.

## Operation

- **Switching on:** long-press the inverter switch or the remote for over 0.5 s, then release. The indicator light confirms it is running. The long-press design prevents accidental switch-on.
- **Switching off:** switch off the inverter and remote — indicator lights go out, and the inverter draws no battery current when off.
- **Connecting loads:** with inverter and appliance switches off, plug the appliance into an AC outlet, then switch the appliance on.
- **USB:** 5V, up to 2.4A total per port — confirm the device can charge by USB and stays within 2.4A.
- **Soft start:** the inverter ramps AC voltage up gradually. For motor/inductive loads, switch the appliance on BEFORE switching on the inverter so the soft start does its job.
- **Fans:** do not run until the case hits ~104 °F or load passes ~40% of rating — silence at low load is normal.
- **Do not use for medical / life-support equipment** (manual's own restriction).
- **Negative-ground systems only** — do not use with positive-ground electrical systems.

## LCD fault indications

| Display | Meaning |
|---|---|
| Warning + IN: LOW | Input low-voltage protection |
| Warning + IN: HIGH | Input high-voltage protection |
| Warning + OVERLOAD | Overload or short-circuit protection |
| Warning + thermometer | Overheat protection |

## Protections

- **Under-voltage alarm:** below 9.8V (12V) — buzzer beeps intermittently.
- **Under-voltage shutdown:** below 9.5V (12V) — inverter shuts down, buzzer sounds continuously, green light off / red light on. Recharge the battery before restarting.
- **Over-voltage shutdown:** above 16V (12V) — same shutdown + buzzer + red light. Correct the input voltage first.
- **Overload:** above rated power — shuts down, buzzer continuous. Remove the excess load, then restart.
- **Short-circuit:** AC output shuts down automatically, resets once the fault is cleared.
- **Thermal:** above ~149 °F — shuts down, buzzer continuous, red light on. Let it cool naturally, fix the cause (ventilation, ambient temp, blocked vent, load), then restart.

## Troubleshooting (paraphrased)

- **No AC output:** power switch off (press 1–2 s — it is a long-press switch); poor battery contact (check cables tight); meter reading low — use a True RMS meter and a fresh meter battery, and keep input voltage in the rated range.
- **Cannot drive the load:** load too big or motor startup surge above rating (try appliance-on-first for soft start, or a bigger inverter); battery too small or not fully charged.
- **Buzzer sounds continuously, no output:** overload — reduce load.
- **Overheating:** cut the load, let it cool naturally 10–30 min, restart once normal; improve ventilation, unblock vents, reduce load.
- **Ground tester reads "open ground":** expected in a vehicle/boat — the inverter cannot create a true earth ground on its own; no tester needed.
- **Startup alarm:** inrush current can briefly trip low-voltage detection — restart several times if needed.
- **~40V measured between ground and neutral:** normal, no current, no leakage — neutral can be grounded.
- **Still not working after the above:** possible internal fault — contact the seller for warranty.

*Summary written 2026-10-16 from the Giandel manual. Specs are the manual's figures; procedures are paraphrased, not quoted.*
