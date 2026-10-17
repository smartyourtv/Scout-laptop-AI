# Victron SmartSolar MPPT 100/20 — Manual summary

**Source:** Victron Energy "MPPT solar charger manual" — SmartSolar MPPT 75/10 up to 100/20, Rev 13 – 10/2026 (document 29694), fetched 2026-10-17 from Victron's official site (victronenergy.com). PDF in library: `victron-smartsolar-mppt-100-20-manual.pdf` (68 pages, ~12 MB, SHA-256 `04acab8ebface0f740b6244e5be571e99640e670162ee50ee97618e2f128ba67`).
**Fetch note (honest):** Victron's SmartSolar HTML index page (victronenergy.com/media/pg/Manual_SmartSolar_MPPT_75-10_up_to_100-20/en/index-en.html) links its PDF under the `Manual_SmartSolar_MPPT_…` folder, but that URL returns 404 (verified 2026-10-17 — Victron's own broken link). The identical document (same doc number 29694, same revision) is served from Victron's official `upload/documents/Manual_BlueSolar_MPPT_75-10_up_to_100-20/` folder; its title page says "BlueSolar" but the body covers both variants — the specifications table and the dimension drawings list the SmartSolar MPPT 100/20 explicitly. That official PDF is what is filed here.
**Note:** Paraphrased summary, not copied manual text.

## Identification
- **Applies to:** the van's main solar controller — **Victron SmartSolar MPPT 100/20** (the up-to-48 V version, part SCC110020160R family). One shared manual covers MPPT 75/10, 75/15, 100/15 and 100/20; the 100/20 figures below are the ones that matter here.
- SmartSolar = built-in Bluetooth. BlueSolar = same charger without built-in Bluetooth (needs a VE.Direct Bluetooth dongle).

## Specs — MPPT 100/20
| Spec | Value |
|---|---|
| Battery voltage | 12 / 24 / 48 V auto-select (36 V selectable in settings; 48 V only on the 100/20) |
| Rated charge current | 20 A |
| Max PV open-circuit voltage | 100 V (never exceed; cold weather raises Voc) |
| Max PV short-circuit current | 20 A |
| Nominal PV power | 290 W (12 V) / 580 W (24 V) / 1160 W (48 V) — controller limits input if more is connected |
| Start condition | PV voltage must exceed Vbat + 5 V to start; thereafter Vbat + 1 V minimum |
| Peak efficiency | 98 % |
| Self-consumption | 12 V: 25 mA / 24 V: 15 mA / 48 V: 10 mA (approx., per spec table) |
| Default absorption (lead-acid) | 14.4 V / 28.8 V / 57.6 V (adjustable) |
| Default float (lead-acid) | 13.8 V / 27.6 V / 55.2 V (adjustable) |
| Equalization default | 16.2 V / 32.4 V / 64.8 V — disabled by default |
| Charge algorithm | Multi-stage adaptive, or user-defined |
| Temperature compensation | −16 mV/°C (12 V) / −32 mV/°C (24 V) / −64 mV/°C (48 V) — lead-acid only; disable for lithium |
| Load output | Continuous 20 A at 12/24 V; only 1 A at 48 V (36/48 V systems) |
| Low-voltage load disconnect | 11.1 V / 22.2 V / 44.4 V or 11.8 V / 23.6 V / 47.2 V, or BatteryLife algorithm |
| Low-voltage load reconnect | 13.1 V / 26.2 V / 52.4 V or 14 V / 28 V / 56 V, or BatteryLife |
| Protection | PV reverse polarity, output short circuit, over-temperature |
| Operating temperature | −30 to +60 °C (full rated output up to 40 °C) |
| Power terminals | 6 mm² / AWG 10 |
| Enclosure | IP43 (electronics) / IP22 (connection area), blue RAL 5012 |
| Weight / size | 0.65 kg; 100 × 131 × 60 mm |
| Data port | VE.Direct |
| Battery fuse (manual's troubleshooting) | 25 A fuse on the 100/20 battery lead (20 A on the smaller models) |

**Van note:** the van plan already matches the manual — 240 W roof panel alone on this controller sits under the 290 W / 20 A nominal at 12 V, with a 25 A fuse on the battery lead near the battery positive.

## Charge settings Scout needs
- **LiFePO4 defaults (manual §6.4 / battery-settings section):** absorption **14.2 V** (12 V system), fixed absorption time **2 h**, float **13.5 V** per the preset description (§6.4's table lists 13.2 V float as the recommended value — the manual states both; VictronConnect's lithium preset is the authority on the device), equalization **disabled**, tail current 0 A (full absorption time available for cell balancing), temperature compensation **disabled**, low-temperature cut-off **5 °C**.
- **Do NOT equalize** lithium (or Gel/AGM/VRLA) batteries — the manual is explicit.
- **Restart of charge cycle:** Vbat < (Vfloat − 0.4 V) for lead-acid, Vbat < (Vfloat − 0.1 V) for LiFePO4, sustained 1 minute (12 V values; ×2 for 24 V, ×4 for 48 V).
- **Van note:** the van's bank manual (E-LekTech) calls for 14.6 V boost / no float — that differs from Victron's LiFePO4 preset above. The battery maker's figures govern the bank; if the preset is changed, it is a user-defined profile in VictronConnect, not the stock lithium preset.

## Wiring order (manual §4.6 — order matters)
1. Connect the **battery** first (needed for automatic system-voltage detection).
2. Verify the detected system voltage in VictronConnect / on a display.
3. Connect the **DC loads**.
4. Connect the **PV** array.
5. Connect VE.Direct if used.
- PV-first is only allowed if the system voltage was set manually before connecting the battery. Wrong order can disable or damage the charger/installation.
- Teardown is the reverse logic: disconnect PV before the battery.
- The 100/20 is the only model in this manual where a separate chassis-ground path is permitted (chassis is isolated).

## Bluetooth / VE.Direct / monitoring
- **Bluetooth (SmartSolar):** built in — setup, monitoring and firmware updates via the VictronConnect app (iOS/Android/PC). No dongle needed. (BlueSolar models need the optional VE.Direct Bluetooth Smart dongle.)
- **VE.Direct port:** wired data to a GX device, MPPT Control display, or PC. VE.Direct cable max length 10 m, cannot be extended. The port also hosts the jumper link used to select the load-output algorithm.
- **VE.Smart Networking:** multiple SmartSolar chargers can synchronize charging and share battery voltage/temperature sense data (e.g. from a Smart Battery Sense or BMV-712) over Bluetooth.
- **Monitoring:** LED indications (meanings also in the Victron Toolkit app), VictronConnect status + 30-day history screens, error reporting in-app, and via a GX device to the VRM portal.
- **Settings routes:** VictronConnect changes everything + updates firmware; the MPPT Control display changes most settings; the VE.Direct jumper only selects the load algorithm. Manual's warning: don't change settings you don't understand — wrong charge settings damage batteries.

## Error codes (manual §8.12 — the ones Scout is most likely to be asked about)
| Code | Meaning (paraphrased) |
|---|---|
| Err 1 | Battery temperature too high — charging stops; auto-resets when temperature drops |
| Err 2 | Battery voltage too high — check other chargers on the battery, or system-voltage set lower than the actual battery |
| Err 17 | Charger overheated despite reduced output — auto-resets when cool; check ambient temp / heatsink airflow |
| Err 18 | Charger over-current — auto-resets; if not, disconnect all power 3 min and reconnect |
| Err 20 / 21 | Legacy bulk-time / current-sensor issues — update firmware; if persistent, factory reset + reconfigure (21 does not auto-reset; contact dealer if it stays) |
| Err 26 | Power terminal overheated — check wiring/strands, tighten bolts; auto-resets |
| Err 28 | Power stage issue — does not auto-reset; disconnect/reconnect all wires; if it persists the unit is faulty (replace) |
| Err 33 | PV over-voltage — auto-resets when PV voltage falls; check array Voc configuration |
| Err 38 / 39 | PV input shut down (internally shorted) to protect the battery from overcharge — update firmware; check the battery-voltage setting and other chargers' voltages. Recovery for 38: disconnect PV, then battery, wait 3 min, reconnect battery first, then PV |
| Err 40 | PV input failed to shut down — charger stops and is faulty |
| Err 80–88 | Same family as 38/39 (PV input shutdown) — firmware first, then the disconnect/wait/reconnect-battery-first procedure |
| Err 116 | Calibration data lost — unit faulty, contact dealer (can appear in history only from first factory power-up, where it can be ignored; also appears if SmartSolar firmware is downgraded from v1.4x — reinstall v1.4x) |
| Err 117 | Incompatible firmware — an update didn't complete; retry the update |
| Err 119 | Settings data lost — charger stopped; factory-default it, disconnect all power 3 min, power up, reconfigure, and report it to the dealer |

Full, most-current list: victronenergy.com/live/mppt-error-codes (manual's own pointer).

## Other sections covered
Safety precautions + wiring safety; features (auto voltage detection, MPPT algorithm, protections, load output + BatteryLife, adaptive 3-stage charging, temperature/voltage sensing, remote on/off, WireBox); installation (mounting, battery, PV array, grounding, connection overview); full settings reference (battery, load output, streetlight, TX/RX port); firmware updating; operation (start-up, charging, equalization, lithium, shutdown/restart, maintenance); troubleshooting (§8 — unresponsive/off charger, batteries not charged / undercharged / overcharged, low yield, communication and load-output issues); technical specifications + dimension drawings (§9).

*Summary written 2026-10-17 from Victron manual Rev 13 – 10/2026. Specs are the manual's figures; procedures are paraphrased, not quoted.*
