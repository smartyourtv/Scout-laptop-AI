# Van Field Repairs — MacGyver / Get-Home Fixes

**Vehicle:** 1992 GMC G2500 Vandura, 5.7L TBI, 700R4.
**Location on the laptop:** `~/scout/knowledge/van-field-repairs.md`
**Companion files:** `van-repair-guide.md` (proper repairs) · `van-troubleshooting-library.md` (diagnosis) · `van-knowledge-base.md` (specs + parts)

## The rule for this whole file

Every fix here is **temporary — get-home only**. Drive gently, check it every few miles, and do the proper repair as soon as you're somewhere safe. A field fix that holds for 50 miles is a win; a field fix you keep for a month is a breakdown waiting to happen.

**Three things this file will never tell you to do:**
- Patch a **fuel** leak with tape, glue, or anything else. Fuel + heat + spark = fire. A leaking fuel line means you don't drive. Period.
- Patch a **brake** line or hose. No clamps, no tape, no epoxy. Brakes either work properly or the van doesn't move.
- Drive on a **failed ball joint, broken steering part, or a wheel that's coming loose**. There is no field fix for those. Tow it.

**Before any field fix:** hazards on, off the road, flat ground, parking brake on, engine off unless the fix requires it running. If you're on a highway shoulder, stay on the far side of the van from traffic.

## The MacGyver kit — carry this in the van

These are the raw materials for nearly every fix below. Total cost is small; the payoff is getting home.

- Duct tape (a full roll, not a flat pack)
- Zip ties — assorted, including a few heavy 12" ones
- Hose clamps — assorted small/medium (2 each of the sizes on your hoses)
- Bailing wire / mechanic's wire (a coil) + pliers
- JB Weld (the slow-cure kind — stronger than the quick stuff)
- Electrical tape
- Spare fuses (assorted, matching your box)
- Jumper cables (heavy gauge — see the house-bank trick below)
- Tire plug kit + 12V tire inflator
- 1 quart engine oil, 1 quart ATF (Dexron), 1 gallon water (or premixed coolant)
- Small bottle of brake fluid (DOT 3)
- A cheap multimeter
- Work gloves, flashlight, rags, a hammer
- A spare belt (the one that drives your water pump + alternator)

## Your best field tool: the house bank

The van has a 500Ah LiFePO4 house bank and a 2000W inverter. That changes the math on several "stranded" scenarios:

- **Dead starter battery:** jumper cables from the house bank to the starter battery (positive to positive, negative to a good ground on the engine). The house bank has more than enough capacity to crank the 350. Start the engine, remove cables, drive — the alternator takes over.
  - **12V lead-acid starter battery ONLY.** Never jump a lithium pack (CMAX modules, etc.) directly from the LiFePO4 bank — different chemistry, different voltage, no current control, BMS bypassed. See "Jump-starting a lithium pack" below.
- **Dead alternator:** turn off everything non-essential (lights, stereo, fan, inverter loads) and drive on the starter battery to the nearest parts store. If you have to stop, recharge the starter battery from the house bank with jumper cables.
- **No 12V power for tools/lights:** the inverter runs 120V tools and chargers off the house bank.

---

## Engine + cooling

### Coolant hose burst or leaking

**Fix:** Let it cool. Wrap the split tightly with duct tape (stretch it as you wrap — 6–8 overlapping layers), then clamp a hose clamp over each end of the tape. If the split is at the very end of the hose, cut off the damaged inch with a knife and re-clamp the hose shorter.
**Get-home range:** 20–50 miles if the leak is small. Watch the temp gauge constantly. Carry water and stop to top up.
**Proper fix:** new hose (see repair guide).
**Never:** radiator stop-leak as a first resort on a big split — it won't hold, and it can clog the heater core.

### Radiator leak (small)

**Fix:** For a pinhole or hairline crack: a raw egg cracked into the radiator (engine running, cap off, then cap on) — the egg white cooks and plugs small holes. Black pepper (a tablespoon) does the same. This is an old trick that genuinely works on small leaks.
**Get-home range:** enough to reach a shop or home, if the leak is small.
**Proper fix:** radiator repair or replacement. Flush the system afterward — the egg/pepper has to come out.
**Never:** egg/pepper on a big leak or a cracked plastic tank — it won't hold. JB Weld on a cooled, cleaned, dry plastic tank crack can hold longer, but it's still temporary.

### Coolant low, no coolant available

**Fix:** plain clean water. Distilled is best, tap water works, creek water in a real emergency. Fill to the mark, drive gently, watch the gauge.
**Proper fix:** drain and refill with the correct coolant mix when home (straight water has no corrosion protection and a lower boiling point).
**Never:** nothing — water is the right emergency substitute for coolant.

### Belt snapped

**Fix:** pantyhose/stocking tied tight as a temporary belt is the classic — it works on a V-belt for a short distance. A length of rope can work too. Route it exactly as the old belt ran, tie it tight, and expect it to stretch — re-tighten after a few miles.
**Get-home range:** a few miles to maybe 20. Watch the temp gauge like a hawk — if this belt drives the water pump, you're on a clock.
**Proper fix:** new belt (carry a spare — see the kit list).
**Never:** drive far with a slipping substitute belt on a hot day. Overheating kills engines fast.

### Squealing belt

**Fix:** a bar of soap rubbed on the inside of the belt (engine off) quiets a glazed belt for a while. Belt dressing spray works too if you carry it.
**Proper fix:** new belt + check the tensioner.

### Jump-starting a lithium pack (CMAX etc.) — NO DIRECT CABLES

**Fix:** there is no safe jumper-cable version of this. A CMAX pack is not a 12V battery — it's a high-voltage building block (84 LMO cells in the full Energi pack, arranged in series groups), and its voltage depends entirely on how it's configured. A 12V LiFePO4 bank (12.8V nominal, 14.6V charging) connected directly across it means:
- **Voltage mismatch.** If the CMAX side is higher voltage, it dumps uncontrolled current into the LiFePO4 bank. If lower, the LiFePO4 bank overcharges it. Either way, nothing limits the current — hundreds of amps can flow.
- **BMS bypassed.** Jumper cables connect pack to pack, going around the battery management system. The BMS is the thing that stops overcharge, over-discharge, and cell imbalance. Bypassing it removes the only protection.
- **Cell damage → thermal runaway.** LMO cells max out at 4.2V per cell. Overcharge one cell and it heats, vents gas, and can catch fire. A lithium fire is self-sustaining and water makes it worse.
- **A flat (0V) lithium pack must never be jumped.** A deeply discharged cell can have an internal short; forcing current into it is how thermal runaway starts.

**Safe ways to charge a CMAX pack from another source:**
1. A **DC-DC charger** rated for the CMAX pack's actual voltage (confirm the pack's series count and voltage with a multimeter first).
2. A **proper lithium charger** set to the pack's chemistry and cell count.
3. If the goal is starting a vehicle, a **jump pack designed for that job** (built-in current limiting + protection), not raw cables between two lithium packs.

**Proper fix:** confirm the pack's configuration and voltage, then charge it with the right charger. If the pack is at 0V or has a swollen/vented cell, don't charge it at all — it's done.

**Fix:** tap the starter body firmly with a hammer while someone holds the key in START. This frees stuck brushes or a sticky solenoid. Often gets one or two more starts out of it.
**Proper fix:** new starter (see repair guide).
**Never:** keep hammering it for days — it's dying, replace it.

### Spark plug wire broken / arcing

**Fix:** wrap the break tightly with electrical tape, several layers, and reroute the wire away from metal and other wires. If the boot is torn, tape it too.
**Get-home range:** the rest of the trip if the tape holds and the wire isn't shorting.
**Proper fix:** new wire set.

### Distributor cap cracked / moisture inside

**Fix:** dry the inside with a rag, spray with WD-40 if you have it (displaces moisture), and seal a hairline crack with a thin layer of epoxy or super glue. Tape over the crack as backup.
**Proper fix:** new cap + rotor.

### Gas cap lost

**Fix:** plastic bag + rubber band over the filler neck. Keeps dirt and water out and stops the check engine light from a missing cap (eventually).
**Proper fix:** new gas cap.

---

## Fuel + oil + fluids

### Oil low, no oil available

**Fix:** any engine oil is better than none. A different viscosity (10W-40 instead of 5W-30) is fine for getting home. ATF in a dire emergency can top up a half-quart — it's oil, but thin, and it's not a substitute for a full fill.
**Proper fix:** find the leak or the burn, top up with the correct oil.
**Never:** cooking oil, gear oil, or brake fluid in the engine. Cooking oil breaks down under engine heat; gear oil is far too thick; brake fluid destroys seals.

### Power steering fluid low / leaking

**Fix:** top up. In a pinch, Dexron ATF is what GM specified for many power steering systems of this era — check the cap or manual first. Drive gently; a leaking PS hose will keep losing fluid.
**Proper fix:** replace the leaking hose (see repair guide).
**Never:** brake fluid in the power steering (destroys seals), or driving with a dry PS pump (it burns up fast).

### Brake fluid low

**Fix:** top up with DOT 3 only — there is no substitute. Then find why it's low (it's a sealed system; low means a leak or worn pads).
**Proper fix:** find and fix the leak.
**Never:** water, oil, ATF, or any other fluid in the brake system. Any contamination means a full flush, and driving with a compromised brake system is not an option.

### Fuel leak — NO FIELD FIX

**Fix:** none. Do not tape it, clamp it, or epoxy it. Do not start the engine. Do not flip any switches. Get away from the van and call for help. A fuel leak on a hot engine is a fire, not a repair job.
**Proper fix:** new fuel line/hose, done properly with the pressure relieved (see repair guide).

---

## Electrical

### Blown fuse, no spare

**Fix:** borrow a fuse of the SAME amperage from a non-critical circuit (horn, cigarette lighter, radio) and put it in the dead circuit. Write down which one you borrowed.
**Get-home range:** until you buy fuses. Replace the borrowed fuse first thing.
**Proper fix:** new fuses + find out why it blew if it happens again.
**Never:** foil, wire, a penny, or a bigger fuse in place of the blown one. The fuse is the cheapest part of the circuit — bypassing it turns a 50-cent problem into a wiring fire.

### Battery cable loose / corroded

**Fix:** twist the terminal tight by hand, then tighten with a wrench. If the terminal is cracked, a hose clamp around it can squeeze it tight enough to get home. Clean corrosion with water + baking soda if you have it, or just scrape it off with a knife and wipe it clean.
**Proper fix:** clean terminals + new cable end if cracked.

### Headlight out

**Fix:** none that restores the light — but check the obvious first: the connector may just be loose, or the ground may be corroded (clean it). If the bulb is truly dead, drive with hazards on low-traffic roads to the nearest parts store, or wait for daylight.
**Proper fix:** new bulb.

### Wiring short / melting smell

**Fix:** disconnect the negative battery cable immediately. Find the melted section, cut it out if you can, and tape/insulate the ends so they can't touch anything. If you can identify the circuit (from the fuse box diagram), pull its fuse so it can't re-energize.
**Proper fix:** trace and repair the short properly — find what rubbed through or melted.
**Never:** reconnect the battery with exposed melted wiring. That's how vans burn.

---

## Tires + wheels

### Flat tire, no spare (or spare is flat too)

**Fix:** tire plug kit — ream the hole, push in a plug, trim it, inflate with the 12V compressor. Works on nail/screw holes in the tread. Drive gently (under 50 mph) and get it patched properly or replaced.
**Get-home range:** the rest of the trip if the plug holds and the hole is in the tread.
**Proper fix:** professional patch (from the inside) or a new tire.
**Never:** plug a sidewall hole or a gash. Sidewall damage = the tire is done, no field fix. Tow it or put on the spare.

### Slow leak, no plug kit

**Fix:** inflate to full pressure and drive to the nearest air + repair. Check pressure every 10–15 miles. A can of tire sealant/inflator works on small tread punctures in a pinch.
**Proper fix:** plug/patch or new tire.

### Lug nut loose / missing

**Fix:** tighten the rest. If one lug is missing entirely, you can drive slowly and carefully on the remaining lugs to the nearest parts store — but no highway, and check the others every few miles.
**Proper fix:** replace the missing lug nut, re-torque all to 100 ft-lb.
**Never:** drive fast or far on missing lugs. A wheel coming off at speed is catastrophic.

---

## Body + misc

### Broken side window / rear window

**Fix:** clear plastic (a trash bag works) taped over the opening from the outside, edges sealed with duct tape. Keeps rain and wind out.
**Proper fix:** replacement glass.

### Door won't latch / latch broken

**Fix:** bungee cord or ratchet strap holding the door closed, or a zip tie through the latch loop. Make sure it can't pop open while driving.
**Proper fix:** new latch mechanism.

### Exhaust hanger broken / pipe dragging

**Fix:** bailing wire or a coat hanger looped around the pipe and the frame to hold it up. Keep the wire away from anything meltable.
**Get-home range:** the rest of the trip if it holds.
**Proper fix:** new hanger + check for exhaust leaks.

### Exhaust hole / leak (small)

**Fix:** a soda can cut open and wrapped around the hole, held with two hose clamps. Muffler tape (the heat-resistant kind) works too.
**Get-home range:** a few hundred miles at most — exhaust heat eats the patch.
**Proper fix:** new pipe/muffler section.
**Never:** drive with exhaust leaking into the cabin. Carbon monoxide is odorless — if you smell exhaust inside, windows down, get out, and don't drive it.

### Mirror broken / hanging

**Fix:** duct tape it back in position, or tape over the stub so it doesn't flap. If it's the driver's mirror, position it before taping — you need it.
**Proper fix:** replacement mirror.

### Wiper blade torn / wiper arm broken

**Fix:** if the blade is torn, remove it — a bare arm scratches the windshield. In rain, slow down, use Rain-X if you have it, and pull over if you can't see. A zip tie can sometimes hold a flapping blade to the arm.
**Proper fix:** new blade/arm.

### Throttle return spring broken

**Fix:** a small bungee cord or a hardware-store spring rigged to pull the throttle closed. TEST IT thoroughly before driving: engine off, open the throttle by hand, release — it must snap fully closed every time, with no sticking.
**Proper fix:** new return spring.
**Never:** drive with a throttle that doesn't snap closed on its own. A sticking throttle is an accident.

### TV cable broken (700R4)

**Fix:** none that lets you drive safely. A broken TV cable means the transmission runs with no line-pressure control — driving it burns up the clutches. Tow it.
**Proper fix:** new TV cable + adjustment (see repair guide).

---

## No safe field fix — tow it

These failures have no MacGyver answer. Diagnose, then call a tow:

- Brake line/hose burst, brake pedal to the floor, caliper falling off
- Ball joint failure, tie rod break, steering box failure, wheel wobbling
- Fuel leak of any size
- Transmission slipping badly, no forward gears, fluid pouring out
- Engine knocking hard, oil pressure at zero, coolant in the oil
- Tire sidewall blowout with no usable spare
- Frame / suspension mounting failure
- Fire, or a strong fuel smell with a hot engine

## After a field fix — the same day, when you're safe

1. **Do the proper repair** from the repair guide. Don't let a field fix become permanent.
2. **Re-check everything** the field fix touched: torque, fluid levels, leaks, tire pressure.
3. **Restock the kit.** Replace whatever you used (tape, plugs, fuses, zip ties).
4. **Log it:** what failed, what the field fix was, what the proper repair was. The log is how you learn what keeps breaking — and what to carry more of.

*End of guide. Last updated: 2026-10-16. Proper repairs: van-repair-guide.md. Diagnosis: van-troubleshooting-library.md.*
