# Van Troubleshooting Library — Offline

**Vehicle:** 1992 GMC G2500 Vandura (Tiara Executive Edition), 5.7L (350) TBI V8, 700R4 automatic, OBD1/ALDL 12-pin.
**Location on the laptop:** `~/scout/knowledge/van-troubleshooting.md`.
**Purpose:** Shawn describes a symptom ("it cranks but won't start", "solar isn't charging") and Scout walks the checks in order — cheapest and easiest first — until the cause is found or it's time to call a mechanic/tow.
**Companion files:** `van-knowledge-base.md` (specs, capacities, parts interchange), `van-manuals/` (component manuals), `first-aid-library.md` (if anyone is hurt).

## How Scout must use this library

1. **Safety first.** If anyone is hurt → first aid library. Fuel smell + spark risk → no cranking, no switches, get out, call for help. Never work under a vehicle supported only by a jack — jack stands only. Hot coolant burns — never open a hot radiator cap.
2. **One symptom at a time.** Ask: when did it start, what changed just before, any warning lights, any new sounds/smells. Then walk the checks in the order listed — do not skip to the "likely" cause.
3. **Confirm each check.** "Is the battery light on?" → wait for answer → next check. Don't rattle off the whole tree at once.
4. **Know when to stop.** Every entry ends with "Stop and get a mechanic/tow if…". When that's reached, say so plainly — don't keep guessing.
5. **Use live data when available.** If TunerPro/ALDL is streaming, Scout reads RPM, coolant temp, MAP, TPS, O2, spark advance, IAC, battery voltage, speed, fuel trim and uses them in the checks (see the KB's diagnostics playbook).
6. **Specs come from the KB, procedures from the manuals.** This file is the decision tree. Torque specs, fluid capacities, and part numbers live in `van-knowledge-base.md`; component procedures live in `van-manuals/`. Never guess a spec.

## Stop rules (apply to every entry)

- **Don't drive if:** no oil pressure, overheating into the red, brake pedal goes to the floor, steering feels loose/disconnected, a wheel is wobbling, heavy fuel leak, transmission fluid pouring out.
- **Call a tow if:** the engine won't start after the basic checks, the vehicle stalls and won't restart, any stop-rule item above, or you're on the side of a highway and it's not safe to work.
- **Call 911 if:** anyone is injured, there's a fire, or you're in an unsafe location.

---

## Engine — starting & running

### Cranks but won't start

**Ask first:** Did it run fine yesterday? Any recent work? Fuel gauge reading? Any smell of fuel?
**Checks in order:**
1. Fuel — gauge above empty? Listen for the fuel pump prime (2-second hum) when the key turns to ON. No hum → check fuel pump fuse/relay, then pump.
2. Spark — pull one plug wire, check for spark while cranking (insulated pliers, don't hold the wire). No spark → ignition module, coil, distributor pickup.
3. Fuel delivery — TBI injectors: look down the throttle body while cranking; fuel should spray in a cone. No spray → fuel pressure, filter, pump, injector fuse.
4. Battery voltage while cranking — below ~9.6V under load means the battery can't drive the system even if it cranks.
5. Flooded — if it smells strongly of fuel, hold the pedal to the floor while cranking (clear-flood mode on TBI) for 10 seconds.
**Likely causes:** fuel pump (common on this age), ignition module, clogged fuel filter.
**Stop and get a mechanic/tow if:** no spark AND no fuel after fuse checks, or you can't confirm fuel pressure.

### Starts, then dies

**Ask first:** Dies immediately or after a few seconds? Will it stay running with a little throttle?
**Checks in order:**
1. Idle air control (IAC) — if it stays running with throttle but dies at idle, IAC valve or passages.
2. Vacuum leaks — listen for hissing; check vacuum hoses for cracks/disconnects (very common at this age).
3. Fuel pressure — weak pump or clogged filter shows up as dying under load.
4. ALDL data: IAC counts, TPS reading at closed throttle, MAP reading, coolant temp sensor (a failed coolant temp sensor can flood or starve the engine).
**Likely causes:** vacuum leak, IAC valve, coolant temp sensor.
**Stop and get a mechanic/tow if:** it dies in traffic repeatedly and won't restart reliably.

### Rough idle / misfire

**Ask first:** Check engine light on? Worse when cold or hot? Any recent tune-up?
**Checks in order:**
1. Plug wires — look for cracked insulation, arcing at night, loose connections. Pull one wire at a time (insulated pliers) — the cylinder that doesn't change the idle is the dead one.
2. Spark plugs — pull the plug on the dead cylinder: fouled (black/oily) vs. clean.
3. Distributor cap and rotor — carbon tracks, corrosion, cracks.
4. Vacuum leaks (see above).
5. ALDL data: O2 sensor switching (should swing rich/lean), fuel trim, misfire pattern.
**Likely causes:** plug wire, plug, cap/rotor, vacuum leak, injector.
**Stop and get a mechanic/tow if:** heavy knocking, blue/white smoke with misfire, or coolant loss with misfire (possible head gasket).

### Stalling while driving

**Ask first:** At idle, at speed, or when slowing down? Restarts right away?
**Checks in order:**
1. Fuel filter / pump — stalls under load, restarts after sitting = often fuel starvation.
2. Ignition module — heat-soak failure: runs until hot, dies, restarts after cooling. Classic TBI-era failure.
3. Torque converter clutch (TCC) solenoid — stalls when coming to a stop, restarts fine, feels like a manual stalled in gear.
4. ALDL data at the time of stall if possible: fuel trim, O2, spark advance.
**Likely causes:** ignition module, TCC solenoid, fuel delivery.
**Stop and get a mechanic/tow if:** stalls in traffic and won't restart, or stalls at highway speed repeatedly.

### No crank (turn key, nothing or just a click)

**Ask first:** Do the dash lights come on? One click or rapid clicking?
**Checks in order:**
1. Battery terminals — clean and tight? Corrosion = no crank with good battery.
2. Battery voltage — 12.4–12.7V resting. Below 12V, charge or jump.
3. Rapid clicking = weak battery. Single loud click = starter solenoid or starter.
4. Shift lever — try starting in Neutral as well as Park (neutral safety switch).
5. Starter connections — tap the starter body lightly while someone cranks (stuck starter brushes sometimes free up).
**Likely causes:** corroded terminals, dead battery, starter, neutral safety switch.
**Stop and get a mechanic/tow if:** battery is good and it still won't crank after the Neutral test.

### Overheating

**Ask first:** How hot on the gauge? Coolant level? Any steam, leaks, or smell?
**Checks in order:**
1. STOP if the gauge is in the red or there's steam — shut it off, let it cool at least 30 minutes. Never open a hot radiator cap.
2. Coolant level in the overflow tank (when cool). Low → look for leaks: hoses, water pump weep hole, radiator, heater core (wet carpet / sweet smell inside).
3. Fan — mechanical fan: does it spin freely when cold (fan clutch failed)? Electric fan if fitted: does it kick on when hot?
4. Thermostat — stuck closed: heats up fast, upper hose hot, lower hose cool.
5. Radiator — external blockage (bugs, debris), internal clog (coolant looks rusty).
6. ALDL data: coolant temp sensor reading vs. gauge (a bad sensor can lie).
**Likely causes:** low coolant from a leak, thermostat, fan clutch, radiator.
**Stop and get a mechanic/tow if:** gauge in the red, steam, coolant mixing with oil (milky oil cap), or white smoke from the exhaust.

### Oil pressure light / gauge at zero

**Ask first:** Any knocking? Oil level on the dipstick?
**Checks in order:**
1. Shut it off immediately if there's knocking or the light is on with a hot engine.
2. Oil level — add if low, then restart and watch.
3. Oil pressure sending unit — a failed sender reads zero with a healthy engine; if the engine sounds normal and oil is full, the sender is suspect (verify with a mechanical gauge if possible).
**Likely causes:** low oil, failed sending unit, oil pump (rare, serious).
**Stop and get a mechanic/tow if:** knocking, or pressure doesn't return after topping up oil. Do not drive it.

### Check engine light

**Ask first:** Solid or flashing? Any drivability symptom?
**Checks in order:**
1. Flashing = active misfire, potential catalyst damage — reduce load, get it checked promptly.
2. ALDL: pull the code (paperclip method or TunerPro). Code narrows it to a circuit/system.
3. Gas cap — loose/missing cap can set an evaporative code.
4. Note the code + symptoms and match to the relevant entry in this file.
**Likely causes:** depends on code — O2 sensor, MAP, TPS, coolant temp sensor, EGR are the usual TBI-era suspects.
**Stop and get a mechanic/tow if:** flashing + rough running, or any stop-rule symptom with it.

### Exhaust smoke colors

- **Black smoke** = too much fuel (rich). Check: coolant temp sensor (lying "cold" = over-fueling), MAP sensor, leaking injector, clogged air filter.
- **Blue smoke** = burning oil. Check: oil level (overfilled?), valve seals (smoke on startup), rings (smoke under load).
- **White smoke** = coolant burning (sweet smell) or just condensation (thin, disappears when warm = normal). Persistent thick white + coolant loss = head gasket territory.
**Stop and get a mechanic/tow if:** thick white smoke with coolant loss, or heavy blue smoke with oil loss.

### Fuel smell

**Ask first:** Inside the cab, outside, or near the engine? Strong or faint?
**Checks in order:**
1. Look for visible leaks at fuel lines, filter, TBI unit, tank. Wet spots, drips.
2. Charcoal canister / vapor lines — cracked hoses leak fumes.
3. If the smell is strong or there's a visible leak: do NOT crank, do NOT flip switches, do NOT use a phone near the leak. Get away from the van and call for help.
**Stop and get a mechanic/tow if:** any visible fuel leak or strong smell. This is a fire risk, not a drive-it-home problem.

---

## Transmission (700R4)

### Won't downshift

**Ask first:** Won't downshift at all, or only at certain speeds? Any slipping?
**Checks in order:**
1. TV (throttle valve) cable — the 700R4's life depends on it. Check adjustment and that it's connected at the throttle body. A misadjusted TV cable causes late/harsh/no downshifts AND burns up the transmission.
2. Fluid level and condition — check with engine running, warm, in Park, on level ground. Low = top up with Dexron, then find the leak. Burnt smell / black = internal wear.
3. Detent / downshift linkage.
**Known history:** the 5/24/2025 Ricardo's job found a broken sprag (one-way clutch) causing a won't-downshift complaint — that part was replaced. If the symptom is back, treat it as a new cause (TV cable, fluid, governor) rather than assuming the same part.
**Stop and get a mechanic/tow if:** fluid is black/burnt, there's slipping with the downshift problem, or the transmission overheats. Driving with a misadjusted TV cable destroys the 700R4 — fix the cable before driving.

### Slipping (revs rise, speed doesn't follow)

**Ask first:** In all gears or one gear? Worse when hot?
**Checks in order:**
1. Fluid level (see above). Low fluid = slipping.
2. Fluid condition — burnt/black = internal clutch wear.
3. TV cable adjustment.
**Stop and get a mechanic/tow if:** slipping in all gears, burnt fluid, or it won't move. This needs a transmission shop.

### Won't shift / stuck in one gear

**Ask first:** Which gear? Any recent work on the TV cable or governor?
**Checks in order:**
1. TV cable — connected and adjusted?
2. Fluid level and condition.
3. Governor — sticking governor causes late/no upshifts; it's accessible without pulling the transmission.
**Stop and get a mechanic/tow if:** it won't move, or fluid is burnt.

### Harsh / late shifts

**Checks in order:**
1. TV cable adjustment (too tight = harsh/late).
2. Fluid level — overfilled can cause harsh shifts too.
3. Vacuum modulator (if fitted) — check the vacuum line for fluid (a failed modulator sucks ATF into the engine).
**Stop and get a mechanic/tow if:** accompanied by slipping or burnt fluid.

---

## Brakes, steering, suspension

### Brake pedal goes to the floor / spongy

**Ask first:** Gradual or sudden? Any puddle under the van?
**Checks in order:**
1. Brake fluid level in the master cylinder reservoir. Low = leak somewhere.
2. Look for leaks: lines, calipers, wheel cylinders, master cylinder (wet firewall inside).
3. If the pedal slowly sinks while holding pressure with no visible leak → master cylinder internal failure.
**Stop and get a mechanic/tow if:** always — do not drive with a sinking or floor-level pedal. Tow it.

### Brakes pulling to one side

**Checks in order:**
1. Tire pressures — a low tire pulls.
2. Caliper sticking (front) — one wheel much hotter after driving, or the van pulls after braking.
3. Brake hose collapse — internal failure blocks return flow, locks one caliper.
**Stop and get a mechanic/tow if:** severe pull, grinding, or a wheel locking up.

### Grinding when braking

**Checks in order:**
1. Pads/shoes worn to metal — inspect. Metal-on-metal destroys rotors/drums fast.
2. Debris (small stone) caught between pad and rotor — sometimes clears with a few gentle stops in reverse.
**Stop and get a mechanic/tow if:** grinding is loud/constant. Get pads replaced before driving far.

### Steering wander / loose feel

**Checks in order:**
1. Tire pressures and condition.
2. Front-end play — steering box adjustment, tie rod ends, ball joints, idler arm (all wear items at this age/mileage).
3. Alignment — after any front-end work.
**Stop and get a mechanic/tow if:** clunking over bumps, visible play in a ball joint, or the steering feels disconnected. A failed ball joint drops the wheel.

### Vibration at speed

**Ask first:** At what speed? Steering wheel, seat, or whole van?
**Checks in order:**
1. Tires — balance, worn spots, a separated belt (bulge in the tread).
2. U-joints — clunk on takeoff, vibration under load.
3. Wheel bearings — noise changes when swerving left/right.
**Stop and get a mechanic/tow if:** a tire has a visible bulge, or the vibration is violent/sudden.

---

## Electrical — chassis

### Battery dies overnight / parasitic drain

**Ask first:** Any new accessories? Dome light staying on? How old is the battery?
**Checks in order:**
1. Dome/courtesy lights — a stuck door switch drains overnight.
2. Battery age and condition — load-test. A 5+ year battery that won't hold a charge is the battery, not a drain.
3. Parasitic draw test: multimeter in series on the negative cable, key off, doors closed, wait 20 minutes for modules to sleep. Over ~50mA = something is awake. Pull fuses one at a time until the draw drops — that circuit is the culprit.
**Likely causes:** stuck light, aftermarket accessory, failing battery.
**Stop and get a mechanic/tow if:** the battery is swollen, hot, or smells of sulfur (internal short — don't jump it).

### Alternator not charging

**Ask first:** Battery light on? Voltage reading?
**Checks in order:**
1. Belt — present, tight, not cracked/glazed.
2. Battery terminals — clean and tight.
3. Voltage with engine running: 13.5–14.5V = charging. 12.6V or less = not charging.
4. Alternator connections — main output wire, ground.
**Likely causes:** belt, alternator, corroded connections.
**Stop and get a mechanic/tow if:** voltage above 15V (overcharging — cooks the battery) or the belt is gone (also stops the water pump on most setups — overheating follows).

### No 12V power / lights dead

**Checks in order:**
1. House battery disconnect switch (if fitted) — on?
2. Main fuse / breaker on the house battery positive lead.
3. Battery voltage at the bank.
4. Ground connections — loose ground kills everything at once.
**Likely causes:** disconnect off, blown main fuse, dead bank, bad ground.

---

## Van systems — solar, inverter, charging

### Solar not charging

**Ask first:** Which controller — SmartSolar (roof panel) or SUNER (portable)? Any error lights? What does the app say?
**Checks in order:**
1. Panel in sun? Shading kills output — even partial shade on one cell drops the whole panel.
2. Connections — MC4 plugs seated, no corrosion, no rodent-chewed wires.
3. Controller LEDs / VictronConnect app — read the status and error. SmartSolar: battery voltage, PV voltage, charge state.
4. Fuse on the controller's battery lead (SmartSolar: 25A fuse near battery positive; portable: 10A fuse).
5. Battery first rule — if the controller was disconnected, reconnect battery BEFORE panels (check the manual).
6. PV voltage at the controller terminals (multimeter) — should exceed battery voltage + 5V for the SmartSolar to start.
**Likely causes:** shading, blown fuse, loose/corroded connection, controller in wrong battery mode (must be 12V Lithium / 14.6V boost for LiFePO4).
**Stop and get a mechanic/tow if:** burnt smell, melted wires, or a swollen battery. Disconnect solar + loads and let it cool.

### Inverter fault / shuts down

**Ask first:** What load was running? Any error code/beep pattern? Battery voltage?
**Checks in order:**
1. Battery voltage — low-voltage cutoff is the #1 cause. If the bank is low, charge before retrying.
2. Overload — add up the watts on the inverter. Over 2000W = shutdown. Unplug loads, reset, add back one at a time.
3. Overheat — ventilation blocked? Fan running? Let it cool.
4. Error code — look it up in the inverter's manual (van-manuals/).
5. Loose battery cables — a loose connection drops voltage under load and trips the inverter.
**Likely causes:** low bank voltage, overload, loose cable, overheating.
**Stop and get a mechanic/tow if:** burnt smell, melted cable, or the inverter is hot to the touch with no load.

### Battery bank low / won't hold charge

**Ask first:** What does the SmartSolar/VictronConnect show? Any single battery in the bank reading differently?
**Checks in order:**
1. Charge sources — is solar actually delivering? Is the Orion charging while driving?
2. Loads — what's drawing? Inverter left on with a load? Fridge/fan running all night?
3. Voltage at rest (no charge, no load for 30 min): ~13.2–13.4V = full for LiFePO4; ~12.8V = roughly half; below 12.0V = nearly empty / possible cell issue.
4. Cell balance — if one battery in the bank reads far lower than the others, it's the weak link.
**Likely causes:** not enough charge input, a load left on, one weak battery dragging the bank.
**Stop and get a mechanic/tow if:** a battery is swollen, hot, or smells. Isolate it (disconnect) and don't charge it.

### Orion DC-DC charger not charging while driving

**Ask first:** Engine running? What does VictronConnect show for the Orion?
**Checks in order:**
1. Input voltage — alternator/starter battery healthy?
2. Orion LEDs — green status LED meanings are in the Orion manual (van-manuals/).
3. Fuses on input and output leads.
4. Engine-running detection — the Orion's charger mode needs to see the engine running; if it thinks the engine is off, it won't charge (protects the starter battery).
5. Output wiring to the house bank — connections, fuse.
**Likely causes:** blown fuse, engine detection setting, loose connection.
**Stop and get a mechanic/tow if:** burnt smell or melted wiring at the charger.

---

## BCPA9 stereo

### No sound

**Checks in order:**
1. Volume / mute — the knob press toggles mute.
2. Source — correct input selected (CarPlay / Android Auto / Bluetooth / Tuner)?
3. Bluetooth routing — is audio going to the phone instead of the van speakers? (Known BCPA9 routing split — see the BCPA9 fix notes.)
4. Speaker wiring — if one speaker works and others don't, it's wiring, not the head unit.
5. Reset — the reset button (pinhole) restarts the unit without losing settings.
**Stop and get a mechanic/tow if:** n/a — stereo issue, not a safety issue. But no sound + no display = check the fuse and power wiring.

### Won't power on

**Checks in order:**
1. Ignition/accessory power — does it have power with the key on?
2. Fuse — head unit fuse and the vehicle's radio fuse.
3. Wiring harness — seated, ground connected.
4. Reset button.
**Stop and get a mechanic/tow if:** burning smell from the dash — pull the fuse and stop.

### CarPlay / Android Auto won't connect

**Checks in order:**
1. Cable (wired) — try a different known-good cable. Most wired CarPlay failures are the cable.
2. Phone Bluetooth + Wi-Fi on (wireless CarPlay/AA needs both).
3. Forget-and-repair the phone in the BCPA9's Bluetooth settings and on the phone.
4. Restart the phone and the head unit.
**Stop and get a mechanic/tow if:** n/a.

---

## DVR / cameras

### Cameras offline / DVR not recording

**Checks in order:**
1. DVR powered? Status lights?
2. Wi-Fi/4G on the DVR — can the app see it?
3. SD card — full, corrupted, or unseated. (A full card stops recording on many DVRs.)
4. Camera connections — a single camera out = its cable/connector; all out = DVR power or main harness.
5. App — BabelStar CMSV7: log out/in, check the device is still on the account.
**Stop and get a mechanic/tow if:** n/a — security issue, not a drivability issue.

---

*End of library. Last updated: 2026-10-16. Specs: van-knowledge-base.md. Procedures: van-manuals/.*
