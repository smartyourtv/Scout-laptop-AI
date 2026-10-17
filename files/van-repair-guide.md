# Van Repair Guide — 1992 GMC G2500 Vandura (Tiara Executive Edition)

**Engine:** 5.7L (350) TBI V8 · **Transmission:** 700R4 automatic · **Drive:** 4x2, 3/4-ton
**Location on the laptop:** `~/scout/knowledge/van-repair-guide.md`
**Companion files:** `van-troubleshooting-library.md` (diagnosis) · `van-knowledge-base.md` (specs, capacities, parts interchange) · `van-manuals/` (component manuals) · `van-field-repairs.md` (MacGyver / get-home fixes) · `first-aid-library.md` (if anyone is hurt)

## The workflow — every repair follows these three steps

1. **Diagnose** — use the troubleshooting library. Don't buy parts until the checks point at a cause. A symptom can have several causes; the library orders the checks cheapest-first so you replace the right thing.
2. **Parts** — use the parts section below + the verified interchange table in the knowledge base. Confirm the exact part before buying (see "Getting the right part").
3. **Repair** — follow the procedure in this guide. Every job lists difficulty, time, tools, parts, steps, and a test-after check.

**Torque rule:** torque values in this guide are standard for this engine/chassis. Where the service manual differs, the manual wins. The only torque confirmed from your own documents is lug nuts: **100 ft-lb**.

## Before every job — safety

- **Jack stands, always.** Never work under a vehicle supported only by a jack. Chock the wheels that stay on the ground. Park on level ground, transmission in Park, parking brake on.
- **Disconnect the negative battery cable** before any electrical work, fuel work, or anything near the starter/alternator.
- **Fuel = fire.** No sparks, no open flame, no power tools near an open fuel line. Keep a fire extinguisher within reach. Catch fuel in a container, never let it run onto the ground or a hot engine.
- **Hot coolant burns.** Never open a radiator cap on a hot engine. Wait at least 30 minutes after shutdown.
- **Sharp + heavy.** Fan blades, sheet metal edges, exhaust parts. Gloves for sharp work; a transmission jack or a second person for anything over ~50 lb.
- **First aid kit** within reach. If anyone is hurt, the first aid library comes before the repair.
- **Know your stop point.** Every job lists "stop and get a shop if…". Hitting it isn't failure — it's the guide doing its job.

## Difficulty scale

- **★ Easy** — basic hand tools, no special equipment. First-timer friendly.
- **★★ Moderate** — more steps, some care with adjustment (TV cable, bleeding). Read the whole procedure before starting.
- **★★★ Advanced** — heavy parts, precise setup, or safety-critical adjustment. Do it only with the right tools and a full afternoon. Several jobs at this level are marked "shop recommended" — the guide still tells you how to diagnose and what parts to expect, so you walk into the shop informed.

## Getting the right part

1. **Identify it precisely.** Year (1992), make (GMC), model (G2500 Vandura / Rally platform), engine (5.7L V8 TBI), transmission (700R4). For chassis parts, 2WD vs 4WD matters — yours is 4x2.
2. **Check the verified interchange table** in the knowledge base first. It lists GM part numbers + compatible make/model/years + source. A part is "verified" only if it's in that table or confirmed by a live search with a cited source — never a guess.
3. **Match the old part.** Bring the old part to the store when you can. Compare bolt patterns, connectors, hose sizes, and length. For electrical parts, compare the connector plug, not just the shape.
4. **Check the details that change the part:** engine size (5.0 vs 5.7), 2WD vs 4WD, with/without AC, gross vehicle weight (6,600 lb GVWR), and build date (09/91) for early-vs-late production changes.
5. **Consumables to keep on hand:** oil filter, air filter, fuel filter, PCV valve, spark plugs, a spare belt, fuses, hose clamps, brake fluid, coolant, penetrating oil, threadlocker (blue), anti-seize, dielectric grease.
6. **Core charges:** starters, alternators, calipers, and power steering pumps usually carry a core charge — bring the old part back for the refund.

---

## Engine tune-up

### Spark plugs + plug wires — ★ Easy, 1–2 hrs

**Fixes:** rough idle, misfire, hard starting, poor fuel economy.
**Parts:** 8 spark plugs (ACDelco R45TS or equivalent — verify in the interchange table), plug wire set, dielectric grease, anti-seize.
**Tools:** spark plug socket (5/8"), ratchet + extensions, gap gauge, wire puller or careful hands.
**Steps:**
1. Engine cool. Work one wire at a time — never pull all wires off at once, or you'll mix up the firing order.
2. Pull the wire off the plug by the boot, not the cable. Remove the old plug.
3. Gap the new plug to spec (0.035" for TBI 350 — verify in the service manual). A little anti-seize on the threads.
4. Install by hand first to avoid cross-threading, then tighten to **15 ft-lb**. Snug is enough — over-tightening cracks the plug or strips the head.
5. Push the new wire on until it clicks at both ends (plug + distributor). A dab of dielectric grease inside the boots keeps moisture out.
6. Repeat for all 8. Double-check routing: wires shouldn't touch the exhaust manifolds or each other tightly (crossfire).
**Test after:** start, idle smooth, no misfire. Check engine light should stay off.
**Stop and get a shop if:** a plug won't come out (seized — forcing it can break it off in the head), or a plug comes out wet with coolant (head gasket territory).

### Distributor cap + rotor — ★ Easy, 30–60 min

**Fixes:** misfire, hard starting, stalling in damp weather.
**Parts:** cap + rotor set, dielectric grease.
**Tools:** screwdriver / small socket set, marker.
**Steps:**
1. Mark the position of the cap and the #1 wire before removing anything (photo helps).
2. Remove wires from the cap one at a time, or transfer them one by one to the new cap in the same positions.
3. Remove the cap, note the rotor's position, pull the rotor straight up, push the new one on (it only fits one way).
4. Install the new cap, reconnect wires in the same positions, grease the boots lightly.
**Test after:** start, idle smooth.
**Stop and get a shop if:** the distributor shaft wobbles side to side (worn bushings — distributor replacement).

### Air filter — ★ Easy, 10 min

**Fixes:** sluggish, rich running, poor economy.
**Parts:** air filter element.
**Steps:** Unclip the air cleaner housing, lift out the old filter, wipe out the housing, drop in the new one, re-clip. Check the intake hose for cracks while you're there.
**Test after:** none needed.

### Fuel filter — ★ Easy, 30–45 min

**Fixes:** stalling under load, hesitation, hard starting, fuel starvation.
**Parts:** fuel filter, new O-rings/clamps if included, container for fuel.
**Tools:** line wrenches (flare-nut wrenches — open-end wrenches round off fuel fittings), rags, safety glasses.
**Steps:**
1. **Relieve fuel pressure first.** Pull the fuel pump fuse, start the engine, let it die. Crank once more for 3 seconds. (TBI runs ~9–13 psi — low pressure, but it still sprays.)
2. Disconnect the negative battery cable.
3. The filter is inline on the frame rail. Put a container under it. Loosen fittings with line wrenches, note the flow direction arrow on the filter.
4. Install the new filter with the arrow pointing toward the engine. Tighten fittings, reconnect the battery and the pump fuse.
5. Turn the key to ON (don't crank) for 2 seconds, off, on again — this primes the system. Check for leaks at both fittings. No leaks → start it.
**Test after:** idle smooth, no fuel smell, no leaks after 5 minutes of running.
**Stop and get a shop if:** fittings are rusted solid (forcing them twists the fuel line), or a leak persists after re-tightening.

### PCV valve — ★ Easy, 10 min

**Fixes:** rough idle, oil in the air cleaner, sludge buildup.
**Parts:** PCV valve, grommet if cracked.
**Steps:** Pull the valve out of the valve cover, pull off the hose. Shake it — it should rattle. No rattle = replace. Push the new one in, reconnect the hose.
**Test after:** idle steadies.

### Serpentine / V-belts — ★ Easy, 30–60 min

**Fixes:** squealing, alternator not charging, overheating (if the belt drives the water pump), power steering loss.
**Parts:** belt(s) — match by routing diagram (usually on the fan shroud or radiator support; photo it before removing).
**Tools:** ratchet + breaker bar for the tensioner, or wrenches for manual-adjust accessories.
**Steps:**
1. Photo the belt routing. Draw it if the sticker is gone.
2. Release the tensioner (or loosen the accessory pivot bolt for manual adjust), slip the belt off.
3. Route the new belt exactly as the photo shows. Release the tensioner slowly.
4. Check tension: about 1/2" deflection mid-span with firm thumb pressure on the longest run (manual-adjust setups).
5. Start and listen — no squeal, no chirp.
**Test after:** all accessories turn, no squeal, charging voltage 13.5–14.5V.
**Stop and get a shop if:** a tensioner pulley wobbles or grinds (bearing shot), or an accessory pulley is seized.

---

## Cooling system

### Thermostat — ★★ Moderate, 1–2 hrs

**Fixes:** overheating (stuck closed), slow warm-up / cold running (stuck open), no cabin heat.
**Parts:** thermostat (195°F for the 350 TBI — verify in the interchange table), housing gasket, coolant.
**Tools:** socket set, gasket scraper, drain pan, funnel.
**Steps:**
1. Engine cold. Drain coolant into a pan (radiator petcock or lower hose). Coolant is toxic — keep pets away, don't dump it.
2. Follow the upper radiator hose to the thermostat housing on the intake. Remove the housing bolts, lift the housing, note the thermostat's orientation (spring toward the engine).
3. Clean both mating surfaces completely. Old gasket material left behind = leak.
4. Install the new thermostat in the same orientation, new gasket (a thin smear of RTV only if the manual calls for it), torque housing bolts to **~20 ft-lb** — evenly, in a crisscross pattern. Over-tightening cracks the housing.
5. Refill coolant, leave the cap off, start the engine, let it warm up. Air bubbles will burp out — top up as the level drops. When the thermostat opens (upper hose gets hot), cap it and check for leaks.
**Test after:** gauge reads normal, upper hose hot, no leaks after a full warm-up + cool-down cycle.
**Stop and get a shop if:** housing bolts snap (corroded — extraction job), or the housing surface is pitted/corroded through.

### Radiator hoses — ★ Easy, 45–60 min

**Fixes:** coolant leaks, swelling/cracked hoses, overheating from collapse.
**Parts:** upper + lower hoses (replace both if one failed), new clamps, coolant.
**Steps:** Drain coolant, loosen clamps, twist hoses off (cut stubborn ones lengthwise with a utility knife — don't pry against the radiator neck, it bends). Clean the necks, install new hoses fully seated, tighten clamps. Refill, burp air, check for leaks.
**Test after:** no leaks at full operating temperature.
**Stop and get a shop if:** a radiator neck is corroded or cracked.

### Coolant flush + refill — ★ Easy, 1 hr

**Fixes:** rusty coolant, overheating from clogged passages, maintenance.
**Parts:** coolant (green conventional for this era — verify spec), distilled water.
**Steps:** Drain old coolant, close the drain, fill with clean water, run 10 minutes with the heater on full hot, drain again. Repeat until the water runs clear. Drain fully, then refill with the correct coolant/water mix (50/50). Burp air with the cap off as above.
**Test after:** gauge normal, heat works, no leaks.
**Stop and get a shop if:** the drained coolant has oil in it (milky) or the flush brings out chunks of rust — get a diagnosis before driving far.

---

## Charging + starting

### Battery replacement — ★ Easy, 20 min

**Fixes:** no crank, slow crank, swollen/dead battery.
**Parts:** battery (group size + CCA for the 350 — verify in the interchange table), battery terminal cleaner, anti-corrosion washers or spray.
**Steps:**
1. Negative cable off FIRST, then positive. Remove the hold-down.
2. Lift the battery out (it's heavy — bend with your legs). Clean the tray and terminals.
3. Set the new battery in, secure the hold-down, positive cable on FIRST, then negative. Tighten snug — don't crush the terminals.
4. Start, check charging voltage (13.5–14.5V running).
**Test after:** cranks strong, voltage correct, no warning lights.
**Stop and get a shop if:** cables are corroded through, or the tray is rusted out.

### Alternator — ★★ Moderate, 1–2 hrs

**Fixes:** battery light on, voltage below 13.5V running, dead battery that keeps recurring.
**Parts:** alternator (remanufactured is fine — bring the core), belt if worn.
**Tools:** socket set, breaker bar for the tensioner.
**Steps:**
1. Disconnect the negative battery cable. Photo the wiring connections on the back of the alternator.
2. Release belt tension, slip the belt off the alternator pulley.
3. Unplug the wiring, unbolt the alternator (usually 2–3 bolts), lift it out.
4. Compare the new alternator to the old: mounting ears, pulley, connector. Swap the pulley if needed.
5. Bolt it in, reconnect wiring exactly as the photo shows, reinstall the belt, reconnect the battery.
6. Start, check voltage: 13.5–14.5V at idle. No squeal.
**Test after:** voltage correct, battery light off, belt quiet.
**Stop and get a shop if:** the mounting bracket is cracked, or voltage reads over 15V with the new alternator (wiring/regulator issue).

### Starter — ★★ Moderate, 1–2 hrs

**Fixes:** single click / no crank with a good battery, grinding on start, intermittent no-start.
**Parts:** starter (remanufactured — bring the core).
**Tools:** socket set, extensions, jack + jack stands (starter is underneath).
**Steps:**
1. Disconnect the negative battery cable. Van on jack stands, chocked.
2. From underneath, photo the wiring on the starter solenoid. Disconnect the wires.
3. Unbolt the starter (usually 2 bolts — support it, it's heavy for its size).
4. Compare new vs old: mounting pattern, nose cone, solenoid position.
5. Bolt in, reconnect wiring as the photo shows, reconnect the battery.
6. Crank — should spin fast with no grinding.
**Test after:** starts cleanly 3 times in a row, no grinding, no click.
**Stop and get a shop if:** the flywheel teeth are chewed (grinding with a new starter = flywheel job, transmission has to come out — shop).

---

## Sensors + ignition (TBI system)

**General rule:** TBI sensors are cheap and easy to replace, but a bad sensor and a bad wire look identical to the computer. Check the connector and wiring first — corroded pins and cracked insulation cause most "sensor failures" at this age. Disconnect the battery before unplugging sensors. Clear codes after replacement by disconnecting the battery for 30 seconds, or with TunerPro.

### Coolant temperature sensor — ★ Easy, 30 min

**Fixes:** hard starting, black smoke (running rich), poor economy, stalling when cold.
**Parts:** coolant temp sensor (the one for the computer — NOT the gauge sender; there are two. The computer sensor is usually near the thermostat housing with a 2-wire connector).
**Steps:** Engine cool. Disconnect the connector, unscrew the sensor (a little coolant will spill — catch it), thread the new one in with sealant if the threads call for it, reconnect. Top up coolant. Clear codes.
**Test after:** starts clean, no black smoke, ALDL shows coolant temp matching the gauge.

### Oxygen (O2) sensor — ★ Easy, 30–45 min

**Fixes:** poor economy, rough idle, check engine light, failed emissions.
**Parts:** O2 sensor (single-wire on this year — verify), anti-seize (usually pre-applied on the new sensor — don't add more if it's already there).
**Tools:** O2 sensor socket (slotted) or a 7/8" open-end wrench.
**Steps:** Engine cool. Unplug the connector, unscrew the old sensor from the exhaust manifold / downpipe. Thread the new one in by hand, tighten snug (don't over-torque — it strips). Reconnect. Clear codes.
**Test after:** ALDL shows the O2 signal swinging rich/lean. Economy improves over a tank or two.
**Stop and get a shop if:** the sensor is seized and the threads come out with it (exhaust manifold repair).

### IAC valve (idle air control) — ★ Easy, 30–45 min

**Fixes:** dies at idle, stays running only with throttle, surging idle.
**Parts:** IAC valve, new gasket/O-ring.
**Steps:** Disconnect the connector, unbolt the IAC from the throttle body, clean the passages with throttle body cleaner + a soft brush (don't push dirt into the intake). Install the new IAC with a new gasket, reconnect. Clear codes. The computer re-learns idle over a few drive cycles — expect a slightly high idle at first.
**Test after:** idles steady, doesn't die at stops.

### MAP sensor — ★ Easy, 20 min

**Fixes:** black smoke, hesitation, stalling, poor economy.
**Parts:** MAP sensor, vacuum hose if cracked.
**Steps:** Check the vacuum hose to the sensor first — a cracked hose mimics a dead MAP sensor. If the hose is good, unplug the connector + hose, unbolt the sensor, bolt the new one on, reconnect. Clear codes.
**Test after:** ALDL shows MAP responding to throttle (high vacuum = low kPa at idle, rises with throttle).

### Ignition module — ★ Easy, 30 min

**Fixes:** stalls when hot, restarts after cooling, no spark.
**Parts:** ignition module, heat-sink grease (critical — the module dies without it).
**Steps:** The module is inside the distributor. Disconnect the battery, remove the cap, unplug the module, unbolt it. Apply a thin, even layer of heat-sink grease to the back of the new module (this is what keeps it alive), bolt it in, reconnect. Clear codes.
**Test after:** runs until fully hot without stalling.
**Stop and get a shop if:** the distributor pickup coil is also failing (erratic spark with a new module — distributor work).


---

## Transmission (700R4)

### Fluid + filter change — ★★ Moderate, 1.5–2 hrs

**Fixes:** maintenance, dirty fluid, minor shift sluggishness. Does NOT fix slipping or burnt fluid — that's internal wear.
**Parts:** transmission filter kit (filter + pan gasket), Dexron fluid (check capacity in the knowledge base), drain pan (a big one — the pan holds several quarts).
**Tools:** socket set, torque wrench, gasket scraper.
**Steps:**
1. Warm the transmission with a short drive, then park level. This drains more fluid.
2. Unbolt the pan slowly, loosening the rear bolts last — let it tip and drain from one corner. Fluid will spill; have a wide pan ready.
3. Remove the pan, pour out the rest. Pull the old filter straight down. Check the pan for metal: a fine gray film is normal; chunks or a pile of clutch material is not.
4. Clean the pan and the magnet. Install the new filter (push firmly until seated), new gasket, bolt the pan up evenly in a crisscross pattern to spec (snug — over-tightening crushes the gasket and causes leaks).
5. Refill through the dipstick tube: start with 4 quarts, start the engine, run through the gears with the brake on, check the dipstick, add until the level reads correctly with the engine running, warm, in Park.
**Test after:** no leaks after a drive, shifts normal, fluid pink/red on the dipstick.
**Stop and get a shop if:** the pan has metal chunks, clutch material, or the fluid is black and burnt — that's a rebuild conversation, not a fluid change.

### TV cable adjustment — ★★ Moderate, 30 min (read this twice first)

**Why it matters:** the 700R4's TV (throttle valve) cable controls line pressure. Misadjusted = wrong shifts AND the transmission burns itself up. This is the single most important adjustment on this transmission.
**Parts:** none (unless the cable is frayed — then replace it first).
**Steps:**
1. Engine off. Find the TV cable where it connects to the throttle body.
2. Press the cable's adjustment button/tab (the D-shaped button on the cable housing) and push the cable slider all the way back toward the firewall.
3. Release the button. Open the throttle to wide-open (full pedal or by hand at the throttle body) — the cable will ratchet out to the correct position with an audible click.
4. Verify: with the throttle closed, the cable should be taut with no slack. With the throttle wide open, the cable is fully extended.
5. Drive gently: shifts should be firm and at reasonable RPM. Late/harsh shifts = too tight; soft/early shifts + slipping = too loose. Re-adjust if needed — do NOT drive far with it wrong.
**Test after:** normal shift points, firm shifts, no slipping.
**Stop and get a shop if:** the cable is frayed, sticking, or the adjustment won't hold — replace the cable before driving.

### Transmission mount — ★★ Moderate, 1–1.5 hrs

**Fixes:** clunk on takeoff, vibration, shifter movement under load.
**Parts:** transmission mount.
**Tools:** jack + jack stands, a second jack or wood block to support the transmission.
**Steps:** Support the transmission with a jack + wood block (don't lift by the pan — it dents). Unbolt the crossmember/mount, lower slightly, swap the mount, bolt up. Torque to spec.
**Test after:** no clunk on takeoff, no vibration at idle in gear.
**Stop and get a shop if:** the crossmember is rusted through.

---

## Brakes

### Front pads + rotors — ★★ Moderate, 1.5–2 hrs per axle

**Fixes:** grinding, squealing, pulsation when braking, thin pads.
**Parts:** pads + rotors (replace rotors if scored, warped, or below minimum thickness — stamped on the rotor), brake cleaner, brake grease.
**Tools:** socket set, C-clamp or caliper piston tool, jack + jack stands, torque wrench.
**Steps:**
1. Van on jack stands, wheels chocked. Remove the wheel.
2. Unbolt the caliper, hang it from a wire — never let it dangle by the brake hose.
3. Slide out the old pads. Unbolt the rotor (may need a tap with a mallet — rust holds it).
4. Compare new rotor to old (diameter, thickness, bolt pattern). Clean the new rotor with brake cleaner (it ships with an anti-rust coating).
5. Compress the caliper piston slowly with a C-clamp — watch the master cylinder reservoir; fluid may rise. Remove excess fluid if it nears the top.
6. Install new pads (grease the slide pins and pad contact points lightly with brake grease — never on the friction surface), reinstall the caliper, torque the caliper bolts.
7. Repeat the other side. Pump the brake pedal several times before driving (the pedal will go to the floor on the first pump — that's normal until the pistons seat).
8. Bed the pads: several moderate stops from 30 mph, letting the brakes cool between stops. Avoid hard stops for the first 200 miles.
**Test after:** firm pedal, no pulling, no grinding, no pulsation.
**Stop and get a shop if:** a caliper piston won't compress (seized caliper — replace it), a brake line is rusted, or the master cylinder reservoir is empty (leak somewhere — find it first).

### Rear shoes — ★★ Moderate, 2 hrs

**Fixes:** grinding from the rear, weak parking brake, squealing.
**Parts:** shoe set, hardware kit (springs + clips), brake cleaner.
**Tools:** socket set, drum brake spring tool (worth buying), jack + jack stands.
**Steps:**
1. Van on jack stands, wheels chocked, parking brake OFF. Remove the drum (tap with a mallet if rusted on).
2. **Photo the assembly before touching anything.** Drum brakes have many springs — the photo is your reassembly map. Do one side at a time so the other side stays as a reference.
3. Replace shoes + hardware one piece at a time, matching the photo. Grease the backing plate contact points lightly.
4. Reinstall the drum, adjust the star wheel until the drum drags slightly, then back off a few clicks.
5. Pump the brakes, test the parking brake.
**Test after:** firm pedal, parking brake holds on a hill, no dragging (drum should spin with slight resistance, not lock up).
**Stop and get a shop if:** a wheel cylinder leaks (wet inside the drum — replace it), or the drum is cracked/scored beyond spec.

### Brake bleeding — ★ Easy, 45 min (two people) or solo with a vacuum bleeder

**Fixes:** spongy pedal after brake work, air in the lines.
**Parts:** brake fluid (DOT 3 for this van — verify), clear tubing, jar.
**Steps:**
1. Fill the master cylinder reservoir. Keep it full through the whole job — letting it run dry puts air back in.
2. Bleed in order: right rear, left rear, right front, left front (furthest from the master cylinder first).
3. Helper pumps the pedal 3–4 times and holds it down. Open the bleeder screw, let fluid + air flow into the jar, close the screw, then helper releases the pedal. Repeat until no bubbles.
4. Check the reservoir level after every wheel. Top up.
**Test after:** firm pedal, no sponginess, no leaks at any bleeder.
**Stop and get a shop if:** the pedal still sinks slowly while holding pressure (master cylinder internal leak — replace it), or a bleeder screw snaps off (shop extraction).

### Caliper replacement — ★★ Moderate, 1 hr per side

**Fixes:** sticking caliper (van pulls, one wheel hot), seized piston, leaking caliper.
**Parts:** caliper (remanufactured — bring the core + old one for matching), brake fluid.
**Steps:** Remove the wheel, unbolt the caliper, cap the brake hose (or clamp it gently), bolt the new caliper on, reconnect the hose with a new copper washer, bleed that wheel. Bed as above.
**Test after:** no pulling, both front wheels similar temperature after a drive, firm pedal.
**Stop and get a shop if:** the brake hose is cracked or swollen — replace the hose too.

---

## Steering + suspension

### Tie rod ends — ★★★ Advanced, 2 hrs + alignment

**Fixes:** loose steering, wandering, uneven tire wear, clunking.
**Parts:** tie rod end(s), cotter pins.
**Tools:** socket set, tie rod separator (pickle fork or puller), jack + jack stands.
**Steps:**
1. Measure the exposed thread / count the turns when removing the old tie rod end — the new one must go on the same number of turns to keep the alignment close.
2. Remove the cotter pin + nut, pop the joint with the separator (don't hammer the stud directly).
3. Thread the new end on the same number of turns. Install, torque the nut, new cotter pin.
4. **Get an alignment.** The turn-count trick gets you close enough to drive to the shop, not close enough to skip it. Driving long without an alignment eats tires.
**Test after:** steering tighter, no clunk, alignment done.
**Stop and get a shop if:** the adjuster sleeve is rusted solid (heat + penetrating oil, or shop), or the steering box itself has play (adjustment is shop work).

### Ball joints — ★★★ Advanced / shop recommended

**Fixes:** clunking over bumps, loose steering, tire wear.
**Why shop:** pressing ball joints in/out needs a ball joint press and the lower joint carries the spring load — dangerous without the right tools. Diagnose it yourself (jack the wheel off the ground, pry under the tire — play at the joint = worn), then decide: press + tools + a full afternoon, or a shop.
**Stop and get a shop if:** there's visible play in a ball joint. A failed ball joint drops the wheel — this is not a "drive it a while" problem.

### Shocks — ★★ Moderate, 1–2 hrs

**Fixes:** bouncing after bumps, wallowing, nose-diving when braking.
**Parts:** shocks (front + rear sets).
**Steps:** One corner at a time, van on jack stands. Unbolt top and bottom, compare new vs old (length, mounting), bolt in. Torque to spec. Rear shocks are usually easy; front may need the wheel off.
**Test after:** one bounce and settle over a bump, no wallowing.
**Stop and get a shop if:** mounting bolts are rusted through the frame (frame repair — shop).

---

## Electrical — chassis

### Fuses + relays — ★ Easy, 10–20 min

**Fixes:** dead circuit (lights, horn, wipers, blower), intermittent accessory.
**Parts:** fuses (match amperage exactly — never a bigger fuse), relay if testing points at one.
**Steps:** Find the fuse box (driver's side dash / underhood — check the owner's manual diagram). Pull the suspect fuse, hold it to the light — broken filament = blown. Replace with the same amperage. If it blows again immediately, there's a short — stop and trace it (or get a shop). For relays: swap with an identical relay from a non-critical circuit (horn) and see if the problem moves.
**Test after:** circuit works, fuse holds.
**Stop and get a shop if:** a fuse blows repeatedly, or you smell burning from the wiring (short — disconnect the battery).

### Ground straps + connections — ★ Easy, 30–60 min

**Fixes:** dim lights, slow crank, weird electrical gremlins, gauges acting up.
**Parts:** wire brush, dielectric grease, replacement ground straps if corroded.
**Steps:** Check the main grounds: battery-to-engine, battery-to-body, engine-to-firewall strap. Unbolt each, wire-brush both surfaces until shiny, grease lightly, bolt back tight. Also clean the battery terminals.
**Test after:** lights brighten, crank speeds up, gremlins gone.
**Stop and get a shop if:** a ground cable is corroded through inside the insulation (replace the cable).

### Alternator / starter wiring — see Charging + starting above

### Headlight / taillight bulbs — ★ Easy, 15 min

**Fixes:** light out.
**Parts:** bulb (match the number — 9004/9006 etc. — printed on the old bulb or in the owner's manual).
**Steps:** Access from behind the housing (or remove the grille/housing per the manual). Don't touch the glass of a halogen bulb — skin oil kills it. Seat it fully, test before reassembling.
**Test after:** light works, aimed correctly.

---

## Van systems — solar, inverter, charging

### Replacing a fuse (solar / house system) — ★ Easy, 10 min

**Fixes:** solar controller dead, inverter dead, no 12V power to a circuit.
**Parts:** fuse (match amperage + type exactly — the SmartSolar battery lead is 25A, the portable panel lead is 10A).
**Steps:** Disconnect the load if possible. Pull the fuse, check it, replace with the same rating. If it blows again, there's a short or overload — don't keep replacing fuses, trace the fault (see troubleshooting library).
**Test after:** system powers up, fuse holds.
**Stop and get a shop if:** a fuse blows repeatedly or wiring is melted/burnt.

### Swapping the solar controller (SUNER ↔ SmartSolar) — ★★ Moderate, 45 min

**Fixes:** dead controller, upgrading to the SmartSolar.
**Parts:** controller, ring terminals if needed, fuses (correct rating for the new controller).
**Steps:**
1. **Battery FIRST rule:** disconnect the solar panels BEFORE the battery (disconnect order: panels → battery). Reconnect in reverse: battery → panels. Connecting panels to a controller with no battery can damage it.
2. Photo the wiring. Label each wire: panel +, panel −, battery +, battery −, load.
3. Unbolt, swap in the new controller, reconnect exactly as the photo shows.
4. Set the battery mode: **12V Lithium, 14.6V boost, no float** for the LiFePO4 bank (SmartSolar: VictronConnect app; SUNER: check its manual).
5. Reconnect: battery first, then panels. Verify charging in the app / LEDs.
**Test after:** controller shows charging, battery voltage rising in sun, correct battery mode confirmed.
**Stop and get a shop if:** wiring is burnt or the battery is swollen/hot.

### Inverter cable replacement — ★★ Moderate, 45 min

**Fixes:** inverter shutting down under load, hot cables, voltage drop.
**Parts:** cables (correct gauge for 2000W at 12V — thick: 2/0 AWG is typical for this power — verify against the inverter manual), lugs, heat shrink.
**Steps:** Disconnect the battery first. Photo the routing. Replace one cable at a time (don't mix up +/−). Crimp lugs properly (a hammer crimper or proper crimper — loose crimps heat up). Heat-shrink the lugs. Reconnect battery, test under load — cables should stay cool.
**Test after:** inverter runs a full load without shutdown, cables cool to the touch, no voltage sag.
**Stop and get a shop if:** the inverter itself smells burnt or the terminals are melted.

---

## Jobs that need a shop (diagnose yourself, repair there)

Use this guide + the troubleshooting library to diagnose, then walk in knowing what's wrong and what parts are involved:

- **Transmission rebuild / overhaul** — internal clutches, bands, sprag, pump. (Fluid + filter, TV cable, and mounts are DIY — see above.)
- **Head gasket / engine internal work** — coolant in oil, white smoke with coolant loss, low compression. Engine-out or head-off work.
- **AC refrigerant work** — legally requires recovery equipment. Diagnose (compressor clutch, fuses, pressure), but the refrigerant side is shop-only.
- **Ball joints** — unless you own a ball joint press and have done it before (see above).
- **Flywheel / flexplate** — transmission has to come out.
- **Frame rust repair / welding** — structural safety.
- **Fuel tank removal** — heavy, awkward, fire risk without a lift.
- **Steering box rebuild / replacement** — adjustment is precise; a mistake is a safety failure.
- **Anything with the airbag system** — not fitted on a 1992 van, but noted for completeness if a later vehicle ever enters this guide.

## After every repair — close the loop

1. **Test drive:** gentle at first. Listen, feel, watch the gauges. Check for leaks after parking.
2. **Re-torque:** lug nuts after any wheel work (100 ft-lb), and re-check after 50 miles.
3. **Log it:** date, mileage, what was done, parts used (with part numbers), cost. The log is how you (and Scout) know what's been done, what's due, and what keeps failing.
4. **Clear codes** if any were set, then confirm they don't come back.
5. **Update the knowledge base** if you learned something new about the van (a part number, a spec, a quirk).

*End of guide. Last updated: 2026-10-16. Diagnosis: van-troubleshooting-library.md. Specs + parts: van-knowledge-base.md. Procedures for components: van-manuals/.*
