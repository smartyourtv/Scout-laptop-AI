# Van Manuals Library — Offline

**Location on the laptop:** `~/scout/knowledge/manuals/` (one PDF per component, plus this index).
**Purpose:** Every electronic component in the van has its complete manual available offline, so Scout can answer "what does the manual say about…" from the real document, not from memory.
**Rule for Scout:** When answering a question covered by a manual, cite the manual (name + section). If the manual isn't in the library, say so — never guess specs or procedures.

## How manuals get here

Manufacturers' manuals are copyrighted, so this library stores **download links + a fetch script**, not copied text. Run `download-manuals.sh` on a machine with internet; it pulls the PDFs from the publishers' / retailers' servers into this folder. The folder then rides the USB to the ThinkPad with everything else.

## Installed now

| Component | Model | Manual status |
|---|---|---|
| Dash stereo | Boss BCPA9 | **FOUND — PDF in library 2026-10-17** (`boss-bcpa9-user-manual.pdf`, 818,929 B, 8 pp, fetched via live browser from manuals.plus after automated download was 403-blocked; rendered title verified: "BOSS Audio Systems BCPA9 Car Stereo Receiver User Manual"). Summary also in library (`boss-bcpa9-manual-summary.md`). |
| Solar controller (main) | Victron SmartSolar MPPT 100/20 | **Manual PDF in library 2026-10-17** (`victron-smartsolar-mppt-100-20-manual.pdf`, Rev 13 – 10/2026, 68 pp, ~12 MB) + summary (`victron-smartsolar-mppt-100-20-manual-summary.md` — specs, LiFePO4 defaults 14.2 V absorb / 2 h / float, VE.Direct + Bluetooth, error codes, battery-first wiring order). Victron's unified 75/10–100/20 manual (doc 29694); their SmartSolar-folder PDF link is 404, working official copy is under the BlueSolar folder — see script notes. |
| Solar controller (interim) | SUNER SP-30A-MPPT (= AS-MPPT-30A) | **Paper manual transcribed 2026-10-16** — see `suner-sp-30a-mppt-manual-summary.md` (30A, 12/24V, 100V max PV, 6 battery modes, Lithium = 14.6V boost / no float, battery-first install, 2 controllers can share one battery). |
| DC-DC charger | **Victron Orion-Tr Smart 12/12-30 Isolated** — 30A / 360W, Bluetooth, Input 8–17V, Output 10–15V, IP43 | Purchased on Amazon Aug 4, 2026 (Shawn's order history). Isolated family manual verified — see script. **Bluetooth advertisement key OBTAINED 2026-10-16 via VictronConnect (Product Info → Instant readout → SHOW). Value NOT stored in files — see main-chat screenshot 2026-10-16. Do NOT change/reset the Bluetooth PIN (key changes on PIN change/reset).** |
| Rooftop A/C | **ApexscnView, model PLTRC** — 12V, 8530 BTU cooling, 3400 BTU heating, 800W power consumption, R134a, 43 lbs (Amazon listing, currently unavailable). **No unit-specific manual found online** (searched 2026-10-16). The TR-L02 manual is a lookalike reference only. **In this van: wired directly to the LiFePO4 bank** (DC, not through the inverter). Fuse: **100A ANL inline currently — believed to be the original factory fuse** (Shawn's recollection, 2026-10-16). **80A ANL recommended** (corrected from 70A — the 70A call assumed the TR-L02 manual's 50A figure; the ApexscnView's 800W spec implies ~67A at 12V, up to ~76A at low voltage, so 70A is too tight). Original factory wire (16mm² per the lookalike manual). **Wire route: bank → fuse (~2 ft from battery, in the electronics box near the bank) → up the wall → across the roof → A/C. The run IS protected — fuse placement is fine.** Disconnect switch: TBD. | **TR-L02 manual transcribed 2026-10-16** — see `rooftop-ac-tr-l02-manual-summary.md`. **TR-L02 specs are reference only; ApexscnView specs govern.** |
| Fridge | **Frigidaire EFR182** — 1.6 cu ft (1.8 in some specs), stainless, internal freezer, R600a, 120V. Purchased Mar 3, 2025 (Amazon). Model identified from listing + manual match (manual's own spec table reproduces the listing's 1.6/1.8 ambiguity). | Manual summary in library (`frigidaire-efr182-mini-fridge-manual-summary.md`). PDF itself not downloadable (manuals.plus bot-block; no Wayback snapshot) |
| Microwave | **Mainstays MS8436127995-01/-02/-03** — 0.7 cu ft, 700W output / 1100W input, 120V. Manual cover photographed by Shawn. | Manual summary in library (`mainstays-ms8436127995-microwave-manual-summary.md`) from paper-manual photos + indexed manual text. PDF itself not downloadable (manuals.plus bot-block; no Wayback snapshot) |
| Inverter | **Giandel PS-2000SAR** — 2000W continuous pure sine wave, 12V DC → 110–120V AC / 60Hz, USB 5V/2.4A ×2, wired remote Model R3, hard-wire terminal block | Purchased on Amazon Apr 28, 2023 (Shawn's order history). Manual PDF in library + summary file. |
| Battery bank | **E-LekTech 12V 500Ah LiFePO4** — identified from Shawn's Amazon order history (listing no longer available). **Model DISCONTINUED per the E-LekTech seller (Oct 2026); seller confirmed this family manual still applies to it** (Shawn, 2026-10-16) | **Family manual FOUND 2026-10-16** — Shawn photographed all 11 pages of the printed E-LekTech LiFePO4 family user manual; paraphrased summary + spec tables in `e-lektech-lifepo4-battery-manual-summary.md` (placeholder replaced). 12V-family charging parameters + shared BMS values apply. **Gap kept visible in the summary: the manual's spec table has NO 12-500 row, so the 500Ah's model-specific figures (esp. max continuous discharge) are not stated — confirm via e-lektech_service@outlook.com.** No PDF obtained (manual gives website root only). |
| Roof solar panel | **Newpowa 240W Monocrystalline, 15V off-grid** — purchased Aug 7, 2022 (Amazon; currently unavailable) | Family manual summary in library (`newpowa-240w-solar-panel-manual-summary.md`). Family manual (NP Monocrystalline v1.4), not 240W-specific; ratings are listing figures. |
| Portable solar panel | **GRECELL 100W Portable Foldable, 20V (SP-100)** — purchased Dec 1, 2022 (Amazon) | **Exact-model manual** summary in library (`grecell-sp-100-portable-solar-panel-manual-summary.md`). 100W, Voc 23.85V, 20V / 5A max load, MC4. |
| DVR / cameras | JOINLGO 4-camera — van unit J2-4GW-AF (12V/24V, CMSV7 server 47.88.8.31); spares: G2-WS + 1080P-SD+670x2+735x2 | **Paper manual transcribed 2026-10-16** — see `dvr-mdvr-manual-summary.md` (specs, wiring, menus, CMSV7, FAQ). No PDF located online yet. |
| Van phone | Dedicated van phone — **BLU View Speed Ultra 5G (B1660V)**, Android 15 | **Manual PDF in library** (`blu-view-speed-ultra-5g-b1660v-user-guide.pdf`, FCC-filed User Guide, 20 pp, ~1.1 MB) + summary (`blu-view-speed-ultra-5g-b1660v-manual-summary.md`). Link in `download-manuals.sh`. Phone number, IMEI, IP from screenshot NOT stored. |

## Installing soon / planned

| Component | Model | Manual status |
|---|---|---|
| Van laptop | Lenovo ThinkPad P1 Gen 5 (21DC002YUS) | Setup Guide verified — see script. **Full User Guide PDF in library 2026-10-17** (`thinkpad-p1-gen5-user-guide.pdf`, Fourth Edition Apr 2024, combined P1 Gen 5 / X1 Extreme Gen 5 guide, 72 pp, ~17 MB) + summary (`thinkpad-p1-gen5-user-guide-summary.md`). Direct download in script. |
| Deterrence speakers | TWS Bluetooth pair — model TBD | Add when purchased |

## Standing rule (future installs)

Every electronic component installed in the van in the future gets its manual added to this library. Process: photo the nameplate/label + the manual cover (or the box) → manual goes in the folder → this index gets a new row. No component goes in without its manual.

## Gaps — need from Shawn

1. ~~Inverter brand + model~~ — RESOLVED 2026-10-16: **Giandel PS-2000SAR** (Amazon order history, purchased Apr 28, 2023).
2. ~~Battery bank brand + model~~ — RESOLVED 2026-10-16: **E-LekTech 12V 500Ah LiFePO4**. ~~Exact manual outstanding~~ — RESOLVED 2026-10-16: family manual photographed by Shawn (all 11 pages) and summarized; see `e-lektech-lifepo4-battery-manual-summary.md`. Remaining sub-gap: no 12-500 row in the manual's tables (500Ah-specific ratings unconfirmed — see summary §2). The model is discontinued per the seller (Oct 2026), which likely explains the missing row (inferred); the seller confirmed the family manual applies to it.
3. ~~Roof panel brand + model~~ — RESOLVED 2026-10-16: **Newpowa 240W Monocrystalline, 15V**. Family manual summary filed.
4. ~~Portable panel brand + model~~ — RESOLVED 2026-10-16: **GRECELL 100W Portable (SP-100)**. Exact-model manual summary filed.
5. ~~JOINGLO DVR exact model~~ — RESOLVED 2026-10-16: van DVR is J2-4GW-AF; spares G2-WS + 1080P-SD+670x2+735x2. ~~DVR manual~~ — RESOLVED 2026-10-16: paper manual photographed, key contents transcribed to `dvr-mdvr-manual-summary.md`.
6. ~~Van phone make + model~~ — RESOLVED 2026-10-16: **BLU View Speed Ultra 5G (B1660V)**, Android 15. Manual PDF fetched + summary filed.
7. ~~Orion-Tr Smart exact variant~~ — RESOLVED 2026-10-16: **Orion-Tr Smart 12/12-30 Isolated** (30A/360W, Amazon order history, purchased Aug 4, 2026). The isolated family manual in the download script is the right one.
8. Any other electronics in the van not listed above (fridge? vent fan? lights? water pump? USB chargers? switches?)
9. ~~Orion-Tr Smart Bluetooth advertisement key~~ — RESOLVED 2026-10-16: obtained via VictronConnect (Product Info → Instant readout → SHOW). Value NOT stored in files — see main-chat screenshot 2026-10-16. Do NOT change/reset PIN.
