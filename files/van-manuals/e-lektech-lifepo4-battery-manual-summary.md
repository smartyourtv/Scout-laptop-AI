# E-LekTech LiFePO4 Battery — Family User Manual Summary

**Status: FOUND — family manual on file.** This summary replaces the earlier placeholder (`e-lektech-12v-500ah-battery-manual-placeholder.md`, removed 2026-10-16).
**Source:** Shawn photographed all 11 pages of the printed E-LekTech "Lithium LiFePO4 Battery — User Manual" on 2026-10-16 and confirmed it is the manual for the van's bank. Photos are in `~/workspace/user/files/` (uploads 16403–16418, Oct 16). No PDF was downloaded. Per library rule, this file is a **paraphrased summary + spec tables (numbers/facts)**, not a reprint of the manual text.
**Applies to:** the van's battery bank — **E-LekTech 12V 500Ah LiFePO4** (bank identified from Shawn's Amazon order history; see the honest gap in §2 before quoting model-specific figures).

**Manufacturer support (from the manual, pp. 1 & 11):** email **e-lektech_service@outlook.com**, website **www.e-lektech.com**. For support, they ask for: order number, order quantity, recipient's name, battery model, and photos/video of the problem. Sold mainly via Amazon and the brand's website; they state a reply within 24 hours.

## 1. What the manual covers

One family manual for the whole E-LekTech LiFePO4 range (12V / 24V / 36V / 48V): brand profile (p. 1), battery features & safety (p. 2), model specification table (p. 3), series/parallel connection rules (pp. 4–5), charging/discharging precautions (p. 6), charger/controller parameter table (p. 7), BMS protection tables (pp. 8–9), troubleshooting (p. 10), after-sale service (p. 11).

Family-level points (paraphrased):

- LiFePO4 chemistry; the manual markets long cycle life vs lead-acid, roughly 40% of lead-acid weight, an operating range of −30 °C to 60 °C, and a built-in BMS that watches for over-voltage, over-current, over-shoot, over-discharge and short circuit and disconnects the battery automatically.
- **The battery must NOT be used as a starting (cranking) battery** (p. 2).
- Charge with a charger made for LiFePO4; if charging from solar or a generator, set the controller to the p. 7 parameters — wrong charge parameters can damage the battery.
- Connection rules: never mix chemistries, brands, models, capacities or nominal voltages in series or parallel; fully charge every battery and match voltages before connecting; small voltage differences between units after use are normal (manual says they will not exceed 3V). Tighten terminal lugs properly — over-tightening can break a terminal, loose connections can melt a terminal or start a fire. Install clean, cool, dry, ventilated, away from water/oil/dust.
- Safety basics: keep away from water, heat, sparks and hazardous chemicals; don't puncture, drop, crush, burn, open or modify; don't touch exposed electrolyte/powder from a damaged case — rinse skin/eyes with plenty of water and seek medical attention for eye contact; disconnect charger/controller before working on the battery; disconnect the load before connecting/disconnecting terminals.

## 2. ⚠️ Honest gap — no 12-500 row in this manual

**Model status (Shawn, 2026-10-16): the 12V 500Ah model is DISCONTINUED, per the E-LekTech seller — and the seller confirmed this family manual still applies to it.** The missing 12-500 row is most likely explained by that (the printed table covers the current/live lineup) — *(inferred)*.

The specification table (p. 3) lists these 12V models: **12-100, 12-120, 12-200, 12-300, 12-300Blu, 12-330Blu, 12-600Blu, 12-660Blu**. There is **no explicit 12-500 (500Ah) row**, and the BMS table (p. 8) likewise has no 500Ah column. So:

- **Model-specific figures for the 500Ah unit are NOT stated in this manual** — most importantly its **max continuous discharge current** (the listed 12V models are 100A / 150A / 200A / 250A depending on model) and its max charge current (listed models: 25A / 30A / 50A / 75A). Do not quote any of those numbers as the 500Ah's rating.
- What **does** apply to the 500Ah: everything the manual states **family-wide for the 12V line** — the p. 7 charging parameters (§3), the shared BMS protection values (§4, "shared" rows), the connection rules, and the troubleshooting procedures (§5). The 500Ah's nominal energy (~6,400Wh, from its 12.8V nominal rating) is a listing-level figure, not from this manual.
- The 500Ah-specific ratings can be confirmed by emailing **e-lektech_service@outlook.com** (include order number + model, per p. 11) or via the Amazon seller (SHANKE STORE).

## 3. Charging parameters — 12V column (p. 7, shared across the 12V family)

Settings the manual gives for a charger/controller used with a 12V battery:

| Parameter | 12V value |
|---|---|
| High Volt Disconnect | 14.8V |
| Charge Voltage | 14.6V |
| Equalize Charge Volt | 14V |
| Boost Charge Volt | 14.4V |
| Float Charge Volt | 13.8V |
| Boost Charge Return Volt | 13.2V |
| Over-Discharge Return Volt | 14.2V |
| Low Voltage Alarm | 12V |
| Over Discharge Volt | 10V |
| Discharge Limit Volt | 10V |

Cross-check for this van: the 14.6V charge voltage matches the 12V Lithium profile already planned for the Victron SmartSolar (14.6V boost, no float) and the SUNER interim controller's Lithium mode.

Also shared on p. 3 for all listed 12V models: voltage range 11–13.6V, charge voltage 14.6V, **series connection supported (total voltage not to exceed 80V)**, **parallel connection supported**.

## 4. BMS protection values — 12V models (p. 8)

The p. 8 columns are headed 12-100, 12-300, 12-600, 12-300Blu, 12-330Blu, 12-600Blu, 12-660Blu (note: p. 3 calls the 600Ah model "12-600Blu" — the plain "12-600" header on p. 8 appears to be the same model group).

### Shared across ALL 12V columns

| Item | Value |
|---|---|
| Max discharge instantaneous current | 300A |
| Over-voltage protection — trip | 15V |
| Over-voltage release condition | Voltage self-recovery, or recovery by discharging |
| Low-voltage protection — trip | 8.8V |
| Low-voltage release condition | Voltage self-recovery, or recovery by discharging |
| Over-current (discharge) protection — trip | 300A |

### Subgroup-dependent — depends on exact variant (the 500Ah's subgroup is not identified in this manual)

| Item | Non-Blu (12-100 / 12-300 / 12-600) | Blu (12-300Blu / 12-330Blu / 12-600Blu / 12-660Blu) |
|---|---|---|
| Max discharge continuous current | 100A (12-100) · 200A (12-300) · 250A (12-600) | 200A (300Blu/330Blu) · 250A (600Blu/660Blu) |
| Over-voltage release value | 14.2V | 14.4V |
| Low-voltage release value | 10.8V | 10.4V (300Blu/330Blu) · 11.2V (600Blu/660Blu) |
| Over-current release | Disconnect load, or release by charging | Auto-recovery after a 32 s delay |
| Short-circuit recovery | Disconnect load, or release by charging | Recovers ~5 s after the load is released |
| Balance (equalization) turn-on voltage | 14V | 13.2V |
| Balance (equalization) current | 200mA (12-100) · 140mA (12-300) · none stated (12-600) | 200mA (300Blu/330Blu) · 80mA (600Blu/660Blu) |
| Over-temperature charge protection / release | 127.4°F / 120.2°F (12-100) · 194°F / 149°F (12-300) · 149°F / 140°F (12-600) | 149°F / 131°F (all Blu) |
| Low-temperature charge protection / release | 5°F / 17.6°F (12-100) · none stated (12-300) · 28.4°F / 37.4°F (12-600) | 14°F / 23°F (all Blu) |
| Over-temperature discharge protection / release | 167°F / 136.4°F (12-100) · 194°F / 149°F (12-300) · 185°F / 140°F (12-600) | 167°F / 149°F (all Blu) |
| Low-temperature discharge protection / release | None stated | −4°F / 14°F |

Practical read for the van: the low-temperature **charge** cutoff exists on most variants but trips anywhere from 5°F to 28.4°F depending on subgroup (inferred range) — treat "don't charge below freezing" as the safe rule regardless of variant.

## 5. Troubleshooting that matters for this van (pp. 6 & 10, paraphrased)

- **Battery output reads 0–5V during discharge:** the BMS has cut discharge off (protection trip). The battery is **not damaged**. Reactivate by charging it for **1–3 minutes** with a LiFePO4-specific charger (or a charger with an activation function).
- **Display voltage looks normal but terminal (+/−) voltage is under 8.8V:** BMS protection tripped by excessive current. Charging with a proper charger for **3 minutes** reactivates the battery.
- **Fully charged voltage:** expect it to settle at about **13.5V after a full charge and 1 hour of rest**; anywhere in **13.3–14.4V** is normal.
- **Battery won't charge / won't fully charge:** use a proper LiFePO4 charger; for controller charging, set the controller to the p. 7 parameters (§3).
- **Built-in display reads inaccurately:** the display infers charge level from voltage, so it's a rough reference only and doesn't affect operation; the manual suggests a professional coulomb meter for accurate capacity/state-of-charge.
- **Display dead but battery works:** display fault only — contact support with a photo/video for a replacement display. Display dead **and** battery dead: contact support for repair/replacement.

## 6. What the placeholder got right / wrong

The superseded placeholder (written before this manual was photographed) listed Bluetooth app monitoring and 8,000+ cycle / 10-year life claims for the 500Ah from E-LekTech family listings. Those remain **listing-level claims, not confirmed by this manual** — this printed manual doesn't mention an app, and its cycle-life language is comparative marketing (up to 20× lead-acid), not a cycle count. The generic 14.6V bulk figure in the placeholder turned out to match the manual's actual 12V charge voltage.

*Summary written 2026-10-16 from Shawn's photos of the printed manual. Family manual for the E-LekTech LiFePO4 range; no PDF obtained and no official PDF URL is given in the manual (website root only).*
