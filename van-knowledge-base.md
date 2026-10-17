# Van Knowledge Base — 1992 GMC G2500 Vandura (Tiara Executive Edition)

Offline reference for van Scout. Sources: NHTSA VIN decode (2026-10-15) + sourced research (see Sources at end).
Caveat: values marked (forum-reported) come from forums/listings, NOT a factory manual. Do not treat them as factory specs.
Authoritative parts data lives in `parts-interchange-db.json` (697 entries: 541 VERIFIED, 156 CANDIDATE, as of 2026-10-15). Scout answers parts-compatibility questions from that file, not from the summary table below. Synced with the web knowledge-base page 2026-10-15.

## Vehicle identity

- VIN: 1GDEG25K9N7501549 (decoded clean, check digit correct)
- California plate: 3BAS765 — registration current through May 2027
- 1992 GMC, built in Lordstown, Ohio, USA
- Shipped by GM as an INCOMPLETE VEHICLE (conversion candidate — matches the TMC/Tiara conversion)
- NHTSA lists model as "Rally" (Vandura platform — same van, NHTSA naming)
- 3/4-ton (G2500), cargo-van body, 4x2, GVWR 6,600 lb (factory Document for Incomplete Vehicle). GAWR FRT 3,400 lb / RR 3,406 lb. Model G21305. Built 09/91. Tires P225/75R15, 35 PSI cold. Lug torque 100 ft-lb (Owner's Manual X-9205).
- Engine: 5.7L (350 cu in) V8, gasoline, Throttle Body Fuel Injection (TBI), 8 cylinders. Engine oil SAE 5W-30 preferred (API SG); change 7,500 mi / 12 mo (Light Duty Emissions), 3,000 mi / 3 mo severe service. Coolant 17 qt (no rear heater) / 20 qt (with rear heater) (Owner's Manual X-9205).
- Transmission: 700R4 (THM700-R4/4L60, non-electronic except TCC lockup) — CONFIRMED by Shawn 2026-10-15 (MD8). NOT the 4L80E (MT1). 4L60E NOT correct for 1992.
- Fuel tank: 22 gal (confirmed by Shawn 2026-10-15).
- Fuel economy: EPA Combined 14 (City 13 / Hwy 17), 7.1 gal/100 mi (FuelEconomy.gov). KBB's 15 is the simple average of rounded 13/17, not the EPA combined figure.
- A/C was originally R12 (1992).
- NO glove box on dash (Tiara plaque in its place, confirmed by Shawn 2026-10-15). SPID label location UNKNOWN — see Diagnostics playbook / Gaps. Do NOT tell Shawn to look in the glove box.
- No open recalls reported (Carfax, 2026-10-15) — but see Recalls below: 92V127000 may still apply depending on build window. Mileage 93,567 mi (Carfax 2026-10-15). Favorite shop: Linville Bros Tire & Alignment (Sacramento).

## Maintenance

- Engine oil: ~5 qt with filter (forum-reported, not factory-verified).
- TBI fuel pressure: 9–13 psi (forum quoting Chart A-5, not factory-verified).
- 700R4/4L60 TV cable controls line pressure. Misadjustment can destroy the transmission. Do NOT drive with it disconnected.
- ALDL (OBD1, 12-pin) port under the driver dash. Paperclip A-B to flash codes; Code 12 = normal. 8192-baud live data via TunerPro + cable + ECM service number. Live PIDs: RPM, coolant temp, MAP, TPS, O2 voltage, spark advance, IAC, battery voltage, speed, fuel trim.
- SBC head-bolt torque 22 → 40 → 65 ft-lb is FORUM consensus only, NOT factory-verified.
- WARNING: A widely quoted capacities block (coolant 20.1/17.4 qt, diff pints, etc.) is for a 1990 Suburban 1500, NOT the Vandura. Do NOT use it as Vandura spec. The correct Vandura coolant figures are 17 qt (no rear heater) / 20 qt (with rear heater) per Owner's Manual X-9205.
- Horsepower: conflicting figures found (150 hp vs 197 hp) — unresolved. Do not quote either as fact.
- Service history (owner-supplied records, not all in Carfax): Ricardo's Auto Repair, 5/24/2025, 88,894 mi — transmission would not downshift; pan had metal + clutch material; teardown found a BROKEN SPRAG (one-way clutch in the 700R4), replaced with parts + torque converter. Total $1,800 (parts $500, labor $1,191, tax ~$49), 12,000-mile warranty on the trans work. Jiffy Lube, last service 9/4/2026 — next oil change due at 100,572 mi (windshield sticker). Further 2026 transmission work at All Transmission (see web page).

## Towing (Owner's Manual X-9205, pp. 4-40/4-41 — from Shawn's photo)

- The manual does NOT give a max towing number. It says "How heavy can a trailer safely be? It depends..." and defers to the dealer for trailering information. Max towing stays UNVERIFIED from GM.
- CANDIDATE max trailer weight 7,500 lb (Tow Ratings per-engine table, 5.7L; manufacturer-origin claimed, no GM doc inspected, cannot tie to an axle ratio). Do NOT present 7,500 lb as "this van can tow 7,500" without an equipment/weighing caveat — the Tiara conversion adds weight. Conflicting figures recorded, not used: 9,600 / 6,600 / 6,500 / 10,000 / 8,000 / 7,000 lb. GCWR not found anywhere. Tongue weight not verified.
- Manual rules that ARE verified: sway control required if trailer weighs over 4,000 lb; no towing at all during first 500 miles; under 50 mph when towing in the first 500 miles of towing; trailer tongue weight counts toward gross vehicle weight.
- Turning diameter: NO verified GM figure. Do NOT fill with a single number. Conflicts: AutoDetective 41.3 ft at 110-in wheelbase, but at 125-in it lists both 48.5 ft (G3500 HD) and 46.0 ft (Chevy Sport Van G20); KBB lists 54.0 ft for BOTH wheelbases (self-contradictory). CHARM has no turning-diameter page. Wheelbase still unknown. Only remaining routes: a physical 1992 GMC Commercial Truck brochure, or measuring the van's wheelbase. No source states curb-to-curb vs wall-to-wall.

## Recalls (verified 2026-10-15, exhaustive search)

- **92V127000 VERIFIED:** brake pedal assembly, 246 units, G25 named. Build-window caveat: aggregators report a single-day 1992-02-01 — needs an NHTSA-record check against this van's build date (09/91) before claiming it applies.
- **06E043000 VERIFIED:** aftermarket Fram G3727 fuel filter ONLY (not a van defect).
- **07E088000 CANDIDATE:** aftermarket Fram Racing oil filter.
- EXCLUDED: 92V077000 (G30/G35 only), 94V125000 (>9,200 lb GVWR only), 94V087000/94V227000 (1994–1995 only), Tiara 93V170/94V207 (Sept 1992–Sept 1993 conversion window = 1993 production). Edmunds "5 recalls" unverified. AutoDetective "0 recalls" contradicted.

## Diagnostics playbook (how Scout diagnoses — database-only, or database + live ALDL)

Method, every time: (1) take Shawn's symptom + when it happens + sounds/smells; (2) match against this file, the service history above, and `parts-interchange-db.json`; (3) give RANKED likely causes with the basis for each (this van's history > KB rule > general pattern — never a bare guess); (4) give the confirming TEST for each cause, cheapest/easiest first; (5) Shawn runs the test and reports back; (6) narrow. Never guess a part number — if it is not a VERIFIED entry in the DB, say so. Never present a CANDIDATE figure as certain.

Database-only (no live data): symptom → ranked causes + tests, conversational back-and-forth. Scout guides Shawn through checks; Shawn is the eyes/hands. Slower, still real diagnosis.
Database + ALDL live data: same, plus live PIDs (RPM, coolant temp, MAP, TPS, O2, spark advance, IAC, battery voltage, speed, fuel trim) to confirm or rule out causes directly. Cameras (DVR RTSP if enabled) can add a visual check for leaks/smoke/belt condition.
Honest limits: Scout cannot physically inspect (no feeling for play in a joint, no smelling burnt fluid firsthand). Some diagnoses need a specific test before confidence — say so rather than guess.

- **Won't downshift (transmission):** Ranked: (1) Broken sprag (one-way clutch) — THIS van's own history: Ricardo's 5/24/2025 found a broken sprag for exactly this complaint. (2) TV cable misadjustment — KB rule, check before anything invasive. (3) Governor. Tests: road test — does it downshift manually? Check TV cable adjustment. ALDL: TPS, speed, RPM during the failure. Parts note: NO GM part number for the sprag in the DB (honest gap) — do not invent one.
- **Slipping / harsh shifts (transmission):** Check TV cable adjustment FIRST — misadjustment kills the trans; do not drive disconnected. Then fluid level/condition (owner check). ALDL: TPS, speed, RPM.
- **No-start / rough running:** Check TBI fuel pressure (9–13 psi), TBI injector spray pattern, ALDL codes (paperclip A-B; Code 12 = normal). ALDL live: MAP, TPS, O2 voltage, IAC, spark advance, fuel trim, coolant temp. Parts note: TBI injector assembly/pod 19110538 VERIFIED for 1992 G2500 (pod, not the complete unit); complete 1992 G-van TBI unit number NOT found; 17112563 is 1987–1991 only.
- **Overheating / coolant:** ALDL coolant temp first. Coolant capacity 17 qt (no rear heater) / 20 qt (with rear heater) per X-9205. Check level, then thermostat/fan (thermostat/fan-clutch part numbers NOT in the DB — do not guess).
- **Charging / battery:** ALDL battery voltage. Alternator reman 10463123 (CS130, 105A) VERIFIED. Check charger-to-battery terminals, fuse/breaker on that run and its holder, and whether the LiFePO4 bank's BMS tripped — a healthy-looking voltage reading alongside a battery fault points to a high-resistance connection, a latched fault, or a tripped BMS (lesson from the van solar-charger diagnosis).
- **Brakes:** SPID-dependent: JB5 vs JD5 changes calipers, rotors, bearings. Calipers 19140905 (LH) / 19140904 (RH) VERIFIED for 1992 G2500; pair 19140915/19140914 is 13-in brakes (G30/G3500). Which pair matches JB5 vs JD5 is inferred only — SPID sticker is the arbiter. Pads 19242608 (JB5 + JD5). Also check recall 92V127000 (brake pedal assembly) build-window applicability.
- **Steering:** Steering gear reman 26087019 VERIFIED (replaces 26052325); 26087018 for L05/C6Q. Ratio/spline unverified. Linkage: pitman kit 14067700, idler kit 26019775, center link 26020885. Do NOT assert the withdrawn "truck box turns backwards" claim.
- **Conversion electronics (rear stereo/TV, electric bed, mood lighting):** check conversion wiring grounds and fuses. Known-issue pattern: rear electronics often dead/untested, VCR removed, TV obsolete, electric-bed motor/switch failures. NO GM interchange for conversion-specific parts.
- **SPID inspection checklist (location unknown — no glove box):** inner hood panel → passenger door → driver door jamb / B-pillar (holds the Certification Label, NOT SPID) → dash / Tiara plaque area → Tiara pouch / Incomplete Vehicle Document envelope → under-hood → converter panels. The SPID sticker settles JB5/JD5 (brakes), MD8/MT1 (trans), axle/radiator/spring codes. Until it is found, brake/bearing/spring answers stay SPID-conditional.

## Tiara Executive Edition

- No factory spec sheet or brochure for "Executive Edition" was found. The name appears in seller listings. Do NOT assert it was a distinct factory trim.
- Composite from listings: hi-top, captain chairs, electric rear sofa/bed, rear stereo/TV/VCR, mood lighting, wood trim, blinds, running boards.
- Naming confusion: listings show "Diamond Executive / Regal Knight Elite" (1995), "Hampton Knight" (1993), "Diamond Edition" (2000). These may be different packages — do not conflate them.
- Best ID source for THIS van: the owner's Tiara pouch / build sheet / electric diagram (if present in the van).
- Conversion-specific parts (hi-top, electric bed, conversion wiring/stereo/TV, blinds, wood) have NO GM interchange. Base GMC parts (chassis/engine/trans/brakes/etc.) use the GM catalog.

## TMC — the conversion company

- Correct entity: **Tiara Motorcoach Corporation (TMC), Elkhart, Indiana.**
- Trademark address: 29618 County Road 12 West, Elkhart, IN 46514 (filed 1996-10-15, abandoned 1999-11-29).
- Endpoint: Chapter 11 bankruptcy — In re Tiara Motorcoach Corp., 212 B.R. 133 (Bankr. N.D. Ind. 1997), No. 97-32500/HCD, petition 1997-07-11, ~$15M assets / ~$22M liabilities, 109 employees at risk.
- A July 10, 1997 Mark III Industries letter of intent ($2.8M + assumed liabilities) was NON-BINDING. A sale closing was NOT verified — do NOT claim an acquisition happened.
- Treat TMC as DEFUNCT. No current OEM parts or support found.
- Only secondary-market items: a 1995 TMC 68-page manual and brochures, plus salvage / generic RV parts.
- Do NOT conflate TMC with: TMC Group (bus builder), Transportation Manufacturing Corp. (Roswell, NM), Tiara RV Sales (dealer), Tiara Yachts, or Thor Motor Coach. Different companies.

## Verified parts interchange (deep dive 2026-10-15 — data only, no links)

**Check the van's SPID sticker FIRST** (location UNKNOWN — there is no glove box; see SPID checklist in Diagnostics playbook) for JB5 vs JD5 (brake code), MD8 vs MT1 (transmission — MD8 confirmed by Shawn), and axle/radiator/spring codes. Many parts differ by these codes. Entries marked UNVERIFIED must NOT be answered with certainty — Scout says so. The full verified table is `parts-interchange-db.json`; the entries below are a summary.

### VERIFIED

- **Lower control arm, driver:** 15988031 (replaces 15633141, 12548329) — fits 1992–1995 GMC G1500/G2500 + 1994 Chevrolet G20. Source: GM catalog mirror.
- **Lower control arm, passenger JB5:** 15988032 (replaces 12548330).
- **Lower control arm, passenger JD5 assembly:** 15988034 (replaces 15594134, 12548332, 31.10 lb).
- **Lower control arm, driver JD5:** Does NOT exist — 15988033 is NOT a real GM number. The 1992 catalog page lists only passenger JD5 15988034, driver JB5 15988031, passenger JB5 15988032.
- **Lower control arm:** NO C/K pickup interchange verified.
- **Upper control arm kit, driver:** 12361258 (replaces 15637877). **Passenger:** 12361259 — VERIFIED via Mevotech/Moog/Dorman OE interchanges. 14067680 is a shaft only, not an arm.
- **Ball joint, lower:** 9766423 — VERIFIED for 1992 G2500.
- **Ball joint, upper:** 9769576 — VERIFIED for 1992 G2500.
- **Ball joint 9762020:** VERIFIED Front Upper, fitment incl. 1985–1992 GMC G2500.
- **Tie rod, outer kit:** 14069514 — VERIFIED. Inner tie-rod kit 14002550, adjuster 19433477.
- **Steering linkage VERIFIED:** pitman kit 14067700, idler kit 26019775, center link/relay rod 26020885.
- **Steering box:** GM assembly number UNVERIFIED. Steering gear reman 26087019 (replaces 26052325); fitment split — 26087019 for L05/JB5/NA1, 26087018 for L05/C6Q. Ratio/spline UNVERIFIED. The earlier claim that a truck steering box turns backwards (van-specific) is WITHDRAWN — unconfirmed at part-number level, do NOT assert it. Van-specific status unconfirmed.
- **Rear brakes VERIFIED:** shoe kit 19150002 (11.15x2.75), wheel cylinder 19175563 (replaced by 19537034, qty 2), spring kit 12375408, parking-brake strut 468677 (qty 2).
- **Front brakes:** Pad kit 19242608 (JB5 + JD5, same kit) VERIFIED. Front rotor JB5 GM 06274216 (rotor assy 15641586); JD5 GM 15667752 / 15641564 with exciter ring. Rear drum 15622360. Brake RPO: JB5 applies, JD5 if rear ABS. JB6/JB7/JB8 do NOT apply — they are C/K codes. Calipers VERIFIED: 19140905 (LH) / 19140904 (RH) for 1992 G2500. Pair 19140915/19140914 is 13-in brakes (G30/G3500). Which pair matches JB5 vs JD5 is inferred only — SPID sticker is the arbiter. 20999156/20999157 and Cardone candidates REJECTED (no G-van fitment).
- **Wheel bearings VERIFIED (JB5 vs JD5 split):** inner 457232 / 457052; outer 457049 (JB5) / 14054922 (JD5); caps 15070471 (JB5) / 15972552 (JD5); spindle hardware 378137/457707 (JB5) vs 3953436/3936464 (JD5/export). Serviceable tapered bearings, not sealed hub OE.
- **Shocks:** GM standard numbers UNVERIFIED; only 22003310 (rear leveling) found.
- **Coil springs:** 14054344 (5647 lb, LH6/JD5) and 328098 (5026 lb, JB5). Rear leaf assembly 15705505 (qty 02). Full L05 spring table NOT found.
- **Transmission:** 700R4 (THM700-R4/4L60, non-electronic except TCC lockup) — CONFIRMED by Shawn 2026-10-15 (MD8). NOT the 4L80E (MT1). 4L60E NOT correct for 1992. MD8 = 700R4/4L60 only. Assembly GM number + donor rules UNVERIFIED. GM service-reman 19329872 exists, fitment unverified.
- **Rear axle:** VERIFIED 8.5-in ring gear. GM catalog via OEMcats, 1992 G2500 rear axle assemblies 26017493–26017499, all 8.50 ring gear, 11.15x2.75 brake, JB5/JD5, ratios 3.08/3.42/3.73. Axle shaft 26013313, 30-spline. 9.5/10.5 are heavier truck axles / catalog errors. Gear set 26038848 = 8.50 ring gear, 3.08, GU4; seal 26047378 = 8.50 diameter, GU4; cover gasket 15807693 = 10 bolt holes; housing 12471203; rear drum 5-lug. RPO: GU4 3.08, GU5 3.23, GU6 3.42, GT4 3.73, GT5 4.10, GQ1 base, G80 Gov-Lock (decodes ratio/locking, NOT diameter).
- **Fuel pump VERIFIED:** 25168719 (gas incl. 5.7L). Sender 19179691 (replaces 25004112). Meter/pump sender 19111397. 25116503 diesel-only, NOT for 5.7L.
- **Distributor:** Assembly UNVERIFIED — components only (module 19179578, pickup 10495089, shaft 10495798, housing 10472052, cap 10477182, rotor 10497452). 1103952→19420927 is C/K/Suburban only. **TBI unit:** Van unit UNVERIFIED — 17091042 (earlier/truck) vs 17093035 (1993–95) remains hypothesis; 17112563 kit fits 1987–1991 G2500 only, NOT 1992. **19110538 injector assembly/pod VERIFIED** for 1992 G2500 (pod, not the complete unit).
- **A/C compressor 1136502 VERIFIED.** Condenser/evaporator assembly numbers unverified. Door hardware numbers VERIFIED (see DB). CHARM bulletin GMC 92-10-05 VERIFIED 1992 truck exterior paint table. Trim 19I = black; other trim codes inferred only. Window regulator 14040342 is 1985–1991 ONLY; 22049764/22049765 is a CANDIDATE power pair with a year-range conflict; 12497971 is the MOTOR, not the regulator.
- **Radiator VERIFIED:** 52489551 (replaces 11 numbers incl. 52463944, 52471638, 52471642), fits 1992–1995 G1500/G2500, 1992–1996 G3500. Core 30 7/16 x 21 3/16 x 7/8 in with trans cooler. Verify exact code by SPID/tag.
- **Alternator VERIFIED reman:** 10463123 CS130, fits 1985–1992 G1500/G2500/G3500 + 1988–1989 C/K 1500/2500/3500. Clock 3:00 for this van (CS130, 105A, 6-groove serpentine; ACDelco reman 3945-02403544; O'Reilly R111794). 11:00 = V-belt/1-groove/diesel variant. 7:00 = other applications. GM assembly number UNVERIFIED.
- **Starter VERIFIED:** 10455305 New, 5.7L-only (strongest match). 10496873 / 10465065 Reman (cover 5.7L). 10465054 diesel-only, NOT for 5.7L. 10465032 4.3/5.0-only, NOT for 5.7L.
- **Wheels:** 8x6.5" (8x165.1mm) GM/Ford/Dodge 8-lug — check bore, offset, stud, 16" vs 16.5".
- **6258493:** RESOLVED as Front Lower Pivot Shaft Kit, JD5 (not an upper arm). Companions: 14019921 (driver, JB1/JB3/JB5), 14019922 (passenger, JB1/JB3/JB5).

### Superseded (forum-level, do NOT use as verified)

The earlier cross-compat table (suspension arms "mostly yes" from G10/C10, brakes "mostly yes" from squarebody trucks, etc.) was forum-level and is superseded by the verified table above. Do not quote it as certainty.

## Gaps / to verify on the van itself

- Factory 1992 service schedule, remaining torque specs — NOT verified. Coolant, oil, lug torque, GVWR/GAWR, tire size/pressure now verified from Owner's Manual X-9205 + factory Incomplete Vehicle document (see above).
- Rear-axle variant, brake package (JB5 vs JD5), gear ratio — need the SPID sticker (location unknown, no glove box) or axle code.
- Tiara "Executive Edition" factory definition — NOT found publicly. Name is now multi-source (1993 "Executive Conversion Package" listing + two 1999 Standard-Examiner classified ads) but no equipment definition. Check the Tiara pouch/build sheet in the van, or a NADA RV Appraisal Guide library copy.
- TMC founding date, production totals, post-1997 disposition — NOT found. In operation by Feb. 1, 1984 (trademark first use) — do NOT use 1984 as the founding date. The July 25, 1997 court decision denied the sale motion ONLY as to the breakup fee, not the sale itself; sale hearing was Aug. 8, 1997; no later order found. Best remaining route: PACER docket pull for No. 97-32500/HCD.
- Recalls: 92V127000 build-window check against this van (built 09/91) — needs an NHTSA-record check.
- NICB (salvage/theft): free at nicb.org/vincheck, but requires a CAPTCHA — owner runs it.
- Full history (ownership, accidents, service): paid Carfax / AutoCheck report — owner buys if wanted. VIN is the key; the plate does not add history.
- Zero verifiable parts entries (omitted from the DB, not padded): Glass (entire system). Belts/Hoses (entire system — serpentine belt GM number unverified; vacuum hoses no verified numbers). Plus steering column/coupling/shaft, sway bar, rear leaf 15705505 (no fitment table), rear standard shock, P/S pump GM number, ignition switch/lock cylinder, horn, wiper arms/linkage, washer pump, most lamp assemblies, starter shims, ABS beyond dump valve, complete brake hard-line set, fuel pump relay, water pump, thermostat, fan clutch, exhaust manifolds/muffler/pipes, TV cable, TCC solenoid, trans pan + separate gasket, front pump/extension seals, cooler lines, dipstick+tube, valve body, servo, bands, sun shell, sprag (no GM number despite Ricardo's sprag failure), output shaft, driveshaft assembly, pinion yoke/seal, axle bearing, Gov-Lock carrier, rear axle housing, most rear axle assemblies, hood latch/hinges, bumpers, mirrors, fuel filler door, dashboard, carpet, base seat belts, condenser/evaporator assemblies, HVAC control panel, engine sensors, ignition coil, plug wires, intake manifold, most gaskets, engine mounts, valve train, oil pump, harmonic balancer, flexplate, EGR solenoid, charcoal canister, AIR pump, assorted unnamed bolts/washers/nuts.

## Sources

- NHTSA vPIC VIN decode (2026-10-15) — vehicle identity, engine, plant, incomplete-vehicle status.
- Owner's Manual X-9205 (Shawn's photo, transcribed in-chat) — towing section pp. 4-40/4-41, lug torque 100 ft-lb, coolant 17/20 qt, oil SAE 5W-30.
- Factory Document for Incomplete Vehicle — GVWR 6,600 lb, GAWR FRT 3,400 / RR 3,406, tires P225/75R15 35 PSI, model G21305, built 09/91, SEO YF7 Upfitters Package.
- FuelEconomy.gov / EPA — Combined 14 (City 13 / Hwy 17).
- Tow Ratings per-engine table — 7,500 lb towing CANDIDATE (no GM doc inspected).
- Exhaustive fill-the-blanks research (2026-10-15, 826-line report, no links) + parts-interchange deep dive (2026-10-15, `parts-interchange-db.json`, 480 entries) — calipers, steering gear, alternator, TBI pod, recalls, Tiara/TMC, SPID, turning-diameter conflicts, Hollander entries.
- Tiara Motorcoach Corp. bankruptcy: In re Tiara Motorcoach Corp., 212 B.R. 133 (Bankr. N.D. Ind. 1997) — via CaseMine.
- Fluid-capacity warning: TruckModCentral thread (1990 Suburban 1500 capacities, NOT Vandura).
- Remainder: sourced research report (forums, listings, trademark records) — forum values flagged as such above.
