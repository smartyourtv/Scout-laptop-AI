# Offline First Aid Library — Laptop Scout

**Location on the laptop:** `~/scout/knowledge/first-aid-library.md` (plain text, no dependencies).
**Purpose:** Let Shawn show Scout a wound (photo) or describe an issue (voice) and get step-by-step first aid, fully offline.
**Source basis:** Standard Red Cross / St John Ambulance first aid guidance. This is general information, not medical advice.

---

## How Scout must use this library (behavior rules)

1. **Assess first, then act.** Ask: what happened, where on the body, how bad is the bleeding/pain, is the person conscious and breathing. One question at a time if the situation is urgent.
2. **Emergencies come before the library.** If any red-flag sign is present, say "Call 911 now" FIRST, then give steps while help is on the way. Never bury the 911 call at the end.
3. **Never diagnose from a photo.** Scout describes what it can see ("I see a cut on the forearm with steady bleeding") and matches it to the closest entry. It never says "that's infected" or "that's broken" as a fact — it says "this looks consistent with X, treat as X, and get checked if Y."
4. **Always state the red flags.** Every answer ends with the "Call 911 / get care if" lines for that entry.
5. **Never say "you're fine."** If the situation is outside the library or uncertain, say so and default to getting professional help.
6. **Spoken delivery:** short steps, one at a time, confirm each before moving on when the situation allows. In a true emergency, give the first 2–3 steps immediately.
7. **Disclaimer:** say once per session, not every answer: "I'm giving general first aid information, not medical advice. If you're unsure, call 911 or Poison Control."

## Global rules (apply to every entry)

- **ABCs first:** Airway, Breathing, Circulation. Unresponsive + not breathing normally → CPR.
- **Consent:** if helping someone else, ask permission if they're conscious. If they're unresponsive, consent is implied.
- **Protect yourself:** gloves if available; don't touch blood/bodily fluids with bare hands if avoidable; wash hands after.
- **Call 911 for:** unresponsiveness, trouble breathing, chest pain, signs of stroke, uncontrolled bleeding, severe burns, head injury with confusion/vomiting, anaphylaxis, seizure lasting over 5 minutes, suspected spinal injury, poisoning with symptoms.
- **Poison Control (US):** 1-800-222-1222 — save this number in Scout's memory.
- **Do not move** a person with suspected spinal injury unless they are in danger (fire, water, traffic).
- **Do not give food, drink, or medication** to someone who is unresponsive, vomiting, or having trouble swallowing/breathing — except the specific exceptions in this library (sugar for low blood sugar, aspirin for heart attack, epinephrine for anaphylaxis).

## Vision path (photo of a wound)

Scout's vision runs on the laptop: Qwen3-VL-8B-Instruct (GGUF + mmproj projector) under llama.cpp, wired in via `thinkpad/scout-vision.py` (swap with the main model — see the ThinkPad spec's Vision section). Photo arrives via the laptop camera or the phone app over van Wi-Fi / Tailscale.

When a photo is available, Scout looks for:
- **Bleeding:** none / oozing / steady flow / spurting or pooling (spurting or pooling = severe bleeding entry, call 911).
- **Depth:** surface scrape vs. gaping edges vs. visible fat/tissue/bone (gaping or deep = get care, may need stitches).
- **Foreign object:** embedded object, dirt, gravel (don't remove deeply embedded objects).
- **Surrounding skin:** redness spreading outward, swelling, warmth, streaking (possible infection — get care).
- **Location:** face, hands, joints, genitals, over a major joint = lower threshold for professional care.

Scout reports what it sees in plain words, then reads the matching entry's steps.

---

## 1. Cardiac arrest / CPR (adult)

**Keywords:** unresponsive, not breathing, no pulse, collapsed, CPR, chest compressions
**Signs:** person is unresponsive, not breathing or only gasping.
**Steps:**
1. Call 911 (or tell someone to). Get an AED if one is nearby.
2. Lay the person on their back on a firm surface.
3. Compressions: heel of hand on center of chest, other hand on top, arms straight. Push hard and fast — at least 2 inches deep, 100–120 per minute. Let the chest fully rise between pushes.
4. 30 compressions, then 2 rescue breaths (tilt head back, lift chin, pinch nose, breathe into mouth until chest rises). If untrained or unwilling to give breaths, do compressions only — that still helps.
5. If an AED arrives, turn it on and follow its voice prompts. Keep compressions going until it tells you to pause.
6. Don't stop until the person moves/breathes, an AED or responder takes over, or you're physically unable to continue.
**Don't:** Don't delay compressions to look for a pulse for more than 10 seconds. Don't stop to move the person unless they're in danger.
**Call 911 if:** always — cardiac arrest is always a 911 call.

## 2. Choking (adult, conscious)

**Keywords:** choking, can't breathe, can't talk, grabbing throat
**Signs:** can't cough, speak, or breathe; clutching throat; face turning blue.
**Steps:**
1. Ask "Are you choking?" If they nod and can't speak, act.
2. 5 back blows: stand behind and slightly to the side, support their chest, heel of hand firmly between the shoulder blades.
3. 5 abdominal thrusts (Heimlich): stand behind, fist just above the navel, other hand over it, quick inward-and-upward thrusts.
4. Alternate 5 and 5 until the object comes out or the person becomes unresponsive.
5. If they become unresponsive: call 911, start CPR (compressions may dislodge the object; check the mouth for the object before breaths).
**Don't:** Don't slap the back of someone who is coughing forcefully — let them cough. Don't do blind finger sweeps in the mouth.
**Call 911 if:** the person can't breathe, turns blue, or becomes unresponsive. Even if the object comes out, get checked if they had trouble breathing afterward.

## 3. Heart attack

**Keywords:** chest pain, heart attack, pressure in chest, arm pain, jaw pain
**Signs:** pressure, squeezing, or pain in the center of the chest lasting more than a few minutes or going away and coming back; pain spreading to arm, jaw, neck, back, or stomach; shortness of breath; cold sweat; nausea; lightheadedness.
**Steps:**
1. Call 911 immediately. Don't drive yourself to the hospital.
2. Have the person sit down and rest. Loosen tight clothing.
3. If they are conscious, not allergic to aspirin, and no one has told them not to take it: chew one 325 mg aspirin (or four 81 mg) — only if emergency dispatch or a doctor hasn't said otherwise.
4. If they become unresponsive and stop breathing normally, start CPR.
**Don't:** Don't delay calling 911 to see if it passes. Don't give food or drink.
**Call 911 if:** always — any suspected heart attack is a 911 call.

## 4. Stroke (FAST)

**Keywords:** stroke, face drooping, slurred speech, one side weak, FAST
**Signs — FAST:**
- **F**ace: one side droops or is numb. Ask them to smile.
- **A**rms: one arm drifts down when both are raised.
- **S**peech: slurred or hard to understand. Ask them to repeat a simple sentence.
- **T**ime: note the time symptoms started — tell responders.
**Steps:**
1. Call 911 immediately. Say "possible stroke" and the time symptoms started.
2. Keep the person still, lying with head and shoulders slightly raised.
3. Don't give food, drink, or medication.
4. If they vomit or are unresponsive but breathing, roll them onto their side (recovery position), keeping head/neck aligned.
5. If they stop breathing normally, start CPR.
**Don't:** Don't wait to see if symptoms go away. Don't give aspirin — it can make some strokes worse.
**Call 911 if:** always — every minute matters with stroke.

## 5. Severe bleeding

**Keywords:** heavy bleeding, spurting blood, arterial, won't stop bleeding, blood pooling
**Signs:** blood spurting or pooling, soaking through cloth quickly, pale/clammy skin, dizziness, confusion.
**Steps:**
1. Call 911.
2. Press hard directly on the wound with a clean cloth or gauze. Don't lift it to check — add more layers on top if it soaks through.
3. If the bleeding is on an arm or leg and direct pressure isn't stopping it, apply a tourniquet 2–3 inches above the wound (never over a joint), tighten until bleeding stops, and note the time. A belt, strap, or torn cloth works if no commercial tourniquet is available.
4. Keep the person still and lying down. Keep them warm.
5. If they become unresponsive and stop breathing normally, start CPR.
**Don't:** Don't remove an embedded object — press around it. Don't remove a soaked dressing; add on top. Don't take a tourniquet off once applied — leave that to responders.
**Call 911 if:** always — severe bleeding is a 911 call.

## 6. Shock

**Keywords:** shock, pale clammy skin, weak pulse, confused after injury
**Signs:** pale, cool, clammy skin; rapid weak pulse; rapid breathing; confusion; weakness; nausea. Often follows severe bleeding, burns, or major injury.
**Steps:**
1. Call 911.
2. Lay the person down. Elevate the legs about 12 inches — unless there's a head, neck, spinal, or leg injury, or it makes breathing harder.
3. Keep them warm with a blanket or coat. Loosen tight clothing.
4. Don't give food or drink.
5. Treat the cause if you can (stop bleeding, etc.).
**Don't:** Don't move someone with a suspected spinal injury to elevate legs.
**Call 911 if:** always — shock is life-threatening.

## 7. Spinal / back injury

**Keywords:** spinal injury, neck injury, fell on head, can't feel legs, back injury
**Signs:** neck or back pain after a fall/crash, numbness or weakness in limbs, loss of bladder/bowel control, deformed spine.
**Steps:**
1. Call 911.
2. Don't move the person unless they are in danger (fire, water, traffic).
3. Hold the head and neck still, in line with the body, until responders arrive. Tell the person not to move.
4. If they vomit, roll the whole body as one unit (log roll) keeping head/neck/back aligned.
**Don't:** Don't twist or bend the spine. Don't let them sit up or "walk it off."
**Call 911 if:** always.

---

## Wounds & bleeding

## 8. Minor cuts & scrapes

**Keywords:** cut, scrape, graze, small cut, skinned knee
**Signs:** shallow wound, edges together or slightly apart, bleeding stops with light pressure.
**Steps:**
1. Wash your hands. Put on gloves if available.
2. Stop the bleeding: press with clean gauze or cloth for a few minutes.
3. Clean: rinse under clean running water. Wash around the wound with soap; keep soap out of the wound. Remove visible dirt with clean tweezers if needed.
4. Apply a thin layer of petroleum jelly or antibiotic ointment (optional).
5. Cover with a bandage or sterile gauze. Change daily or when wet/dirty.
6. Watch for infection over the next few days (see "Call 911 / get care").
**Don't:** Don't use hydrogen peroxide or iodine in the wound — they damage healing tissue. Don't pick at scabs.
**Get care if:** wound is deep, gaping, or won't close; over a joint, on the face, or on the hand; bleeding won't stop after 10 minutes of pressure; redness spreads outward, red streaks appear, pus forms, fever develops; tetanus shot isn't up to date (more than 10 years, or 5 for a dirty wound).

## 9. Puncture wounds

**Keywords:** puncture, nail in foot, stepped on nail, stabbed by object
**Signs:** small entry wound, possibly deep, may bleed little.
**Steps:**
1. Stop bleeding with direct pressure.
2. Clean with running water. Don't probe the wound.
3. Cover with a clean bandage.
4. If it's from a rusty/dirty object and tetanus isn't current, get medical care the same day.
**Don't:** Don't remove a large or deeply embedded object (knife, large shard) — stabilize it and call 911. Don't squeeze the wound.
**Call 911 / get care if:** object is large or deeply embedded; bleeding won't stop; wound is on the face, chest, or abdomen; signs of infection; tetanus not up to date; the person has diabetes or poor circulation.

## 10. Nosebleed

**Keywords:** nosebleed, bloody nose
**Steps:**
1. Sit up and lean slightly forward (not back — swallowing blood causes vomiting).
2. Pinch the soft part of the nose below the bony bridge and hold for 10–15 minutes without checking. Breathe through the mouth.
3. Spit out any blood in the mouth.
4. After it stops, avoid blowing, picking, or bending down for several hours.
**Don't:** Don't tilt the head back. Don't pack the nose with tissue deep inside.
**Get care if:** bleeding lasts more than 20 minutes despite pressure; heavy bleeding; trouble breathing; after a head injury; nosebleeds keep happening; the person takes blood thinners or has a bleeding disorder.

## 11. Eye injury / object in eye

**Keywords:** eye injury, something in eye, chemical in eye, eye pain
**Steps — object (dust, eyelash):**
1. Don't rub the eye.
2. Rinse gently with clean water or saline, blinking while rinsing.
3. If it stays, look up and pull the upper lid over the lower lid — tears may flush it out.
**Steps — chemical splash:**
1. Flush immediately with clean water for at least 15–20 minutes, holding the eye open. Rinse from the inner corner outward so it doesn't wash into the other eye.
2. Call Poison Control (1-800-222-1222) or 911 if vision is affected.
**Steps — embedded object or blow to the eye:**
1. Don't touch or remove the object. Don't press on the eye.
2. Cover both eyes lightly with a shield (paper cup) without pressing, and get emergency care.
**Call 911 / get care if:** embedded object, chemical burn, vision changes, severe pain, cut on the eyeball, or anything that doesn't flush out.

## 12. Knocked-out tooth

**Keywords:** tooth knocked out, lost tooth, dental injury
**Steps:**
1. Pick the tooth up by the crown (the white part), not the root.
2. Rinse briefly with water if dirty — don't scrub, don't remove attached tissue.
3. If possible, place it back in the socket and hold it in place by biting on gauze.
4. If it won't go back, keep it in milk, or inside the cheek (only for an adult who won't swallow it), or in saline.
5. See a dentist within 30 minutes — speed is the difference between saving and losing the tooth.
**Don't:** Don't let the tooth dry out. Don't wrap it in a dry cloth.
**Get care if:** always — same-day emergency dental care.

## 13. Blisters

**Keywords:** blister, friction blister, popped blister
**Steps:**
1. Leave an intact blister alone — the skin roof is the best protection. Cover with a bandage or moleskin if it rubs.
2. If it pops on its own, wash with soap and water, apply petroleum jelly, cover with a bandage.
3. If it must be drained (large, painful, on a weight-bearing spot): wash hands, sterilize a needle with alcohol, prick the edge, press fluid out, keep the skin flap in place, cover with a bandage.
**Don't:** Don't tear off the skin flap. Don't drain a blister from a burn or from a person with diabetes/poor circulation.
**Get care if:** redness spreads, pus, increasing pain, fever, or the blister came from a burn.

## 14. Splinter

**Keywords:** splinter, thorn, wood splinter
**Steps:**
1. Wash hands and the area with soap and water.
2. Pull the splinter out at the same angle it went in, using clean tweezers. Grasp the end closest to the skin.
3. Wash again, apply a bandage.
**Don't:** Don't squeeze the area — it can break the splinter deeper.
**Get care if:** it's deep, under a nail, fully under the skin, the area gets red/swollen, or tetanus isn't current.

## 15. Animal bites

**Keywords:** dog bite, cat bite, animal bite, bitten
**Steps:**
1. Wash the wound thoroughly with soap and running water for several minutes.
2. Press to stop bleeding, then cover with a clean bandage.
3. Cat bites and bites to the hand/face need same-day medical care — cat bites infect easily.
4. If the animal may have rabies (wild animal, stray, unprovoked attack, animal acting strangely): call animal control and get medical care immediately — rabies is fatal once symptoms appear.
**Don't:** Don't close a deep bite wound tightly with tape — it needs to drain.
**Get care if:** bite is deep, on the face/hand, from a cat, from a wild or unknown animal, bleeding won't stop, signs of infection, or tetanus not current.

## 16. Insect stings & bites

**Keywords:** bee sting, wasp sting, mosquito bite, ant bite, spider bite, stung
**Steps — bee/wasp:**
1. Remove the stinger by scraping with a card edge (don't squeeze it).
2. Wash with soap and water.
3. Cold pack 10 minutes on, 10 off, to reduce swelling.
4. Oral antihistamine for itching; pain reliever if needed.
**Steps — spider bite (most are mild):**
1. Wash, cold pack, keep the area still and at heart level.
2. Watch for spreading redness or severe pain.
**Call 911 if:** any sign of anaphylaxis — trouble breathing, swelling of lips/tongue/throat, widespread hives, dizziness, collapse. See entry 25.
**Get care if:** bite is from a black widow or brown recluse (severe pain, muscle cramps, ulcer), or swelling/pain worsens over hours, or red streaks appear.

## 17. Tick bites

**Keywords:** tick, tick bite, tick on skin
**Steps:**
1. Grasp the tick with fine-tipped tweezers as close to the skin as possible.
2. Pull straight up with steady pressure. Don't twist or jerk.
3. Wash the area and your hands with soap and water.
4. Note the date — watch for a bullseye rash, fever, or joint pain over the next 30 days.
**Don't:** Don't burn the tick, don't smother it with petroleum jelly or nail polish.
**Get care if:** the head/mouthparts stay in the skin and can't be removed, a bullseye rash appears, fever/chills/joint pain develop, or the tick was engorged and you can't tell how long it was attached.

## 18. Snake bite

**Keywords:** snake bite, bitten by snake
**Steps:**
1. Call 911.
2. Keep the person still and calm. Keep the bitten limb still and at or slightly below heart level.
3. Remove rings, watches, and tight clothing near the bite before swelling starts.
4. Note the time of the bite and, if safe, what the snake looked like (photo from a distance). Don't try to catch or kill it.
5. Get to a hospital — antivenom is the treatment, and it must be given at a facility.
**Don't:** Don't cut the wound, don't suck out venom, don't apply a tourniquet, ice, or electric shock. Don't give alcohol or caffeine.
**Call 911 if:** always — every snake bite needs emergency evaluation.

---

## Burns & musculoskeletal

## 19. Burns (1st / 2nd / 3rd degree)

**Keywords:** burn, burned, scald, hot water burn, thermal burn, third degree burn
**Signs:** 1st degree — red, painful, no blisters (like a mild sunburn). 2nd degree — blisters, swelling, very painful, skin looks wet/red. 3rd degree — white, charred, or leathery skin; may be numb; can be deep.
**Steps:**
1. Stop the burning: move away from the heat source. Cool the burn with clean, cool (not cold) running water for 10–20 minutes. If running water isn't available, use a cool wet compress.
2. Remove jewelry and loose clothing near the burn before swelling starts — but don't pull off anything stuck to the burn.
3. Cover loosely with a clean, dry, non-stick dressing or cling film. Keep it loose — burns swell.
4. For pain: over-the-counter pain relief if the person can take it.
**Don't:** Don't use ice, butter, toothpaste, or adhesive dressings on a burn. Don't pop blisters — they protect the skin. Don't remove clothing stuck to a burn.
**Call 911 / get care if:** 3rd-degree burns (white/charred/leathery skin); burns on the face, hands, feet, joints, or genitals; burns covering a large area; burns from chemicals, electricity, or an explosion; signs of infection (increasing pain, pus, fever); the person is a child or elderly.

## 20. Sunburn

**Keywords:** sunburn, sun burn, burned by sun
**Signs:** red, painful, warm skin; swelling; blisters in severe cases; possible fever/chills.
**Steps:**
1. Get out of the sun and into shade or indoors.
2. Cool the skin with a cool damp cloth or a cool bath/shower.
3. Apply plain moisturizer or aloe vera gel. Petroleum jelly on blistered areas is fine; avoid heavily fragranced lotions.
4. Drink plenty of water.
5. Over-the-counter pain relief if needed.
**Don't:** Don't pop blisters. Don't apply butter, toothpaste, or ice directly to the skin.
**Get care if:** blistering over a large area, fever over 102°F (39°C), chills, confusion, signs of dehydration, or sunburn on a baby under 1 year.

## 21. Fractures

**Keywords:** broken bone, fracture, broken arm, broken leg, crack, compound fracture
**Signs:** pain, swelling, bruising, deformity or unnatural angle, can't move or bear weight, grinding feeling, bone visible through skin (open/compound fracture).
**Steps:**
1. Call 911 for an open fracture, a leg/pelvis/spine fracture, or if the person can't be moved safely.
2. Keep the injured part still. Immobilize it in the position found — don't try to straighten it.
3. Splint as found: support the joints above and below the injury with a rigid object (rolled magazine, stick, board) padded with cloth, and tie firmly but not so tight it cuts off circulation. Check that fingers/toes stay warm and pink.
4. Apply a cold pack (wrapped in cloth) to reduce swelling.
5. Treat for shock if needed (see entry 6).
**Don't:** Don't straighten a deformed limb. Don't move a person with a suspected spine or pelvis fracture unless they're in danger.
**Call 911 if:** open/compound fracture, leg, pelvis, or spine involved, heavy bleeding, signs of shock, or the person can't be transported safely.

## 22. Sprains & strains

**Keywords:** sprain, strain, twisted ankle, pulled muscle, rolled ankle
**Signs:** pain, swelling, bruising, limited movement after a twist, stretch, or overuse. A sprain is a ligament injury (joint); a strain is a muscle/tendon injury.
**Steps — RICE:**
1. **R**est: stop using the injured area.
2. **I**ce: cold pack wrapped in cloth, 15–20 minutes at a time, several times a day for the first 48 hours.
3. **C**ompression: elastic bandage, snug but not tight — loosen if fingers/toes go numb, blue, or cold.
4. **E**levation: raise the injured area above heart level when possible.
5. Over-the-counter pain relief if needed.
**Don't:** Don't apply heat in the first 48 hours. Don't push through the pain or "test" the joint.
**Get care if:** can't bear weight or move the joint, numbness, the joint looks deformed, swelling doesn't improve after 2 days, or pain worsens. (Deformity or inability to bear weight may mean a fracture — treat as entry 21.)

## 23. Dislocation

**Keywords:** dislocation, dislocated shoulder, joint popped out, out of socket
**Signs:** joint visibly out of place, intense pain, swelling, can't move the joint, limb may look deformed.
**Steps:**
1. Keep the joint still — immobilize it in the position found with a sling or padding.
2. Apply a cold pack wrapped in cloth.
3. Get medical care the same day — a dislocation needs to be put back by a professional, ideally within hours.
**Don't:** Don't try to pop the joint back in — you can damage nerves, blood vessels, and the joint itself. Don't let the person "shake it out."
**Call 911 / get care if:** always — same-day emergency care. Call 911 if the limb is blue, cold, or numb, or if the person can't be transported.

---

## Medical emergencies

## 24. Head injury / concussion

**Keywords:** head injury, concussion, hit head, knocked head, bump on head
**Signs:** headache, dizziness, confusion, nausea/vomiting, brief loss of consciousness, slurred speech, drowsiness, sensitivity to light/noise. Red flags: worsening headache, repeated vomiting, increasing confusion or agitation, unequal pupils, clear fluid or blood from the nose or ear, weakness, slurred speech, seizure, won't wake up.
**Steps:**
1. Check for red flags. If any are present, call 911.
2. Keep the person still and calm. If a neck/spine injury is possible (hard fall, crash), don't move them — see entry 7.
3. Apply a cold pack wrapped in cloth to the bump for swelling.
4. For a minor bump with no red flags: rest, avoid screens and strenuous activity for 24 hours, no alcohol, no driving. Have someone check on them every few hours for the first day — wake them once during the night to confirm they respond normally.
**Don't:** Don't give aspirin or NSAIDs (ibuprofen) in the first hours — they increase bleeding risk; acetaminophen is safer if needed. Don't let the person drive, drink alcohol, or play contact sports.
**Call 911 if:** any red flag listed above; loss of consciousness (even brief); the person is a young child, elderly, or on blood thinners; symptoms worsen over hours.

## 25. Anaphylaxis

**Keywords:** anaphylaxis, severe allergic reaction, epi pen, epinephrine, throat swelling, allergic shock
**Signs:** trouble breathing or wheezing, swelling of lips/tongue/throat, widespread hives, dizziness, collapse, rapid weak pulse — often within minutes of exposure (food, sting, medication).
**Steps:**
1. Call 911 immediately.
2. Use an epinephrine auto-injector right away — don't wait for symptoms to worsen. Inject into the outer thigh (through clothing is fine). Hold 10 seconds, then massage the site.
3. Lie the person down with legs raised — unless they're having trouble breathing, in which case let them sit up slightly.
4. If no improvement after 5–15 minutes, give a second dose in the other thigh if available.
5. If they vomit or become unresponsive but are breathing, roll them onto their side.
6. If they stop breathing normally, start CPR.
**Don't:** Don't give food or drink. Don't delay epinephrine to give antihistamines — antihistamines don't stop anaphylaxis.
**Call 911 if:** always — anaphylaxis is always a 911 call, even if epinephrine helps. A second reaction can occur hours later.

## 26. Mild allergic reaction

**Keywords:** allergic reaction, hives, itchy rash, mild allergy, sneezing after exposure
**Signs:** itchy skin, hives, sneezing, runny nose, mild swelling of lips or face — but breathing is normal and the person feels otherwise okay.
**Steps:**
1. Remove or move away from the trigger if possible.
2. Oral antihistamine (cetirizine, loratadine, or diphenhydramine) per package directions.
3. Cool compress on itchy skin.
4. Watch closely for the next hour — mild reactions can progress to anaphylaxis.
**Don't:** Don't ignore worsening symptoms. Don't give anything by mouth if breathing becomes difficult.
**Call 911 if:** any sign of anaphylaxis (see entry 25) — trouble breathing, swelling of lips/tongue/throat, dizziness, collapse. Use epinephrine if available.

## 27. Asthma attack

**Keywords:** asthma attack, can't breathe, wheezing, inhaler, asthma
**Signs:** wheezing, coughing, tight chest, shortness of breath, trouble speaking in full sentences.
**Steps:**
1. Sit the person upright — don't lay them down.
2. Help them use their rescue inhaler (e.g., albuterol): 2–4 puffs through a spacer if available, one puff at a time with slow breaths. Repeat per their asthma action plan (usually every 20 minutes up to 3 times).
3. Keep them calm. Loosen tight clothing.
4. If they have a peak flow meter and a written plan, follow it.
**Don't:** Don't lay them flat. Don't leave them alone.
**Call 911 if:** lips or face turning blue; can't speak full sentences; inhaler isn't helping after 2–3 rounds; breathing is getting worse; they become drowsy or unresponsive. If they stop breathing normally, start CPR.

## 28. Low blood sugar (diabetic emergency)

**Keywords:** low blood sugar, hypoglycemia, diabetic emergency, insulin shock, shaky sweating confused diabetic
**Signs:** shakiness, sweating, fast heartbeat, hunger, dizziness, confusion, irritability, slurred speech, pale skin. Severe: unresponsiveness, seizure.
**Steps — if conscious and able to swallow:**
1. Give 15 grams of fast-acting sugar: 4 oz (half a cup) of juice or regular (not diet) soda, 3–4 glucose tablets, or a tablespoon of sugar/honey.
2. Recheck in 15 minutes. If still low, give another 15 grams. Repeat — the "15-15 rule."
3. Once normal, give a small snack with protein (crackers and peanut butter) if the next meal is more than an hour away.
**Steps — if unconscious or can't swallow safely:**
1. Call 911.
2. Give NOTHING by mouth — no food, drink, or sugar. Choking risk.
3. If trained and glucagon is available, give glucagon per its instructions.
4. Roll the person onto their side (recovery position) to keep the airway clear.
5. If they stop breathing normally, start CPR.
**Don't:** Don't give insulin for low blood sugar. Don't give food or drink to someone who can't swallow.
**Call 911 if:** unconscious, seizing, can't swallow, doesn't improve after two rounds of sugar, or you're unsure whether it's low or high blood sugar (when in doubt, treat as low and get help).

---

## Environmental emergencies

## 29. Heat exhaustion

**Keywords:** heat exhaustion, overheated, heat cramps, too hot, heat sick
**Signs:** heavy sweating, cool pale clammy skin, fast weak pulse, nausea, headache, dizziness, muscle cramps, weakness.
**Steps:**
1. Move to a cool place (shade, air conditioning).
2. Lie down and elevate the legs slightly.
3. Loosen or remove excess clothing.
4. Sip cool water slowly. Cool the skin with wet cloths or a fan.
5. Rest — no activity until fully recovered.
**Don't:** Don't give alcohol or caffeine. Don't give large gulps of water to someone who is vomiting.
**Get care if:** vomiting, symptoms worsen or don't improve within an hour, confusion, fainting, or body temperature rising — it may be progressing to heatstroke (see entry 30).

## 30. Heatstroke

**Keywords:** heatstroke, heat stroke, overheating emergency, hot and confused
**Signs:** high body temperature (103°F / 39.4°C or higher), hot red dry or damp skin, rapid strong pulse, throbbing headache, dizziness, nausea, confusion, loss of consciousness. This is a medical emergency.
**Steps:**
1. Call 911 immediately.
2. Move the person to a cool place.
3. Cool rapidly by any means available: cold water on the skin, fan, ice packs or cold wet cloths on neck, armpits, and groin. If a tub is available, immerse in cool water.
4. If they are conscious and alert, small sips of water are okay. If confused or unconscious, give NOTHING by mouth.
5. Keep cooling until responders arrive or the person starts shivering.
**Don't:** Don't give fluids to someone who is confused or unconscious. Don't give alcohol or caffeine. Don't delay cooling to wait for help.
**Call 911 if:** always — heatstroke is life-threatening.

## 31. Hypothermia

**Keywords:** hypothermia, freezing cold, too cold, shivering stopped, cold exposure
**Signs:** shivering (early), then confusion, slurred speech, drowsiness, weak pulse, slow breathing, loss of coordination. Late stage: shivering stops — this is worse, not better.
**Steps:**
1. Call 911.
2. Move to a warm place. If moving isn't possible, shield from wind and insulate from the cold ground.
3. Remove wet clothing and replace with dry blankets or clothing.
4. Warm gradually: wrap in blankets, including the head (leave the face clear). Skin-to-skin contact under blankets helps.
5. If conscious and alert, give warm (not hot), non-alcoholic drinks and high-energy food.
6. Handle gently — rough handling can trigger a dangerous heart rhythm.
**Don't:** Don't use direct heat (hot water, heating pads, fire) on the skin — it can cause burns and shock. Don't give alcohol. Don't massage the limbs.
**Call 911 if:** always — hypothermia needs emergency care, especially with confusion, no shivering, or a weak pulse.

## 32. Frostbite

**Keywords:** frostbite, frozen fingers, frozen toes, white numb skin cold
**Signs:** skin that is white, waxy, or grayish-yellow; numbness; hard or waxy-feeling skin; blisters after rewarming.
**Steps:**
1. Get to a warm place.
2. Remove wet clothing and jewelry from the affected area.
3. Rewarm in warm water — 100–104°F (37–40°C), comfortably warm to the inside of the wrist, not hot — for 20–30 minutes. Keep the water temperature steady.
4. After rewarming, loosely bandage with sterile gauze, placing gauze between fingers/toes.
5. Get medical care — frostbite needs professional evaluation.
**Don't:** Don't rub the area. Don't use direct heat (fire, heating pad, hot water). Don't break blisters.
**Don't rewarm if:** refreezing is possible — frozen, thawed, and refrozen tissue is damaged far worse. If you can't keep it warm, leave it frozen and get to care.
**Get care if:** always — same-day medical care for any frostbite. Call 911 if hypothermia is also present.

---

## Poisoning & other

## 33. Poisoning (swallowed)

**Keywords:** poisoning, swallowed poison, ate poison, overdose, drank chemicals
**Signs:** depends on the substance — nausea, vomiting, burns around the mouth, confusion, drowsiness, trouble breathing, seizures. Some poisons show no immediate symptoms.
**Steps:**
1. Call Poison Control: 1-800-222-1222. Call 911 if the person is unresponsive, not breathing, having seizures, or in severe distress.
2. Identify the substance: bring the container or label. Note how much was taken and when.
3. Follow Poison Control's instructions exactly.
4. If the person vomits, keep them on their side to protect the airway.
**Don't:** Don't induce vomiting unless Poison Control or a doctor tells you to — for corrosive or petroleum products, vomiting causes more damage. Don't give food, drink, or home remedies unless told to.
**Call 911 if:** unresponsive, trouble breathing, seizures, or you can't reach Poison Control and symptoms are severe.

## 34. Fainting

**Keywords:** fainting, fainted, passed out, syncope, collapsed briefly
**Signs:** brief loss of consciousness, pale sweaty skin beforehand, lightheadedness, tunnel vision, nausea. Usually recovers quickly.
**Steps:**
1. Lay the person down and elevate their legs about 12 inches.
2. Loosen tight clothing. Get fresh air — open a window or move outdoors.
3. Once fully alert, have them sit up slowly, then stand slowly.
4. Don't give food or drink until fully alert and able to swallow safely.
5. Check for injury from the fall.
**Don't:** Don't slap or shake them awake. Don't give food or drink while they're still groggy.
**Get care if:** fainting happened during exercise or while lying down; chest pain or heart palpitations before/after; no quick recovery (more than a couple of minutes); repeated fainting; the person is pregnant, elderly, or has a heart condition; or they were injured in the fall.

## 35. Dehydration

**Keywords:** dehydration, dehydrated, dry mouth, no urine, dizzy thirsty
**Signs:** thirst, dry mouth, dark or no urine, dizziness, fatigue, headache. Severe: confusion, rapid heartbeat, rapid breathing, sunken eyes, no urination, loss of consciousness.
**Steps:**
1. Move to a cool place and rest.
2. Small, frequent sips of water or oral rehydration solution (ORS). For homemade ORS: 1 liter of clean water + 6 teaspoons of sugar + 1/2 teaspoon of salt, stirred until dissolved.
3. If the person can't keep fluids down, give small sips every few minutes rather than large amounts.
4. Replace electrolytes: sports drinks, broth, or ORS.
**Don't:** Don't give alcohol, caffeine, or large amounts of plain water very fast to someone severely dehydrated — small sips of ORS are safer.
**Get care if:** confusion, rapid heartbeat, no urination for 8+ hours, can't keep fluids down, bloody or black stool, or the person is an infant, young child, or elderly. Call 911 if unresponsive or seizing.

## 36. Food poisoning / vomiting & diarrhea

**Keywords:** food poisoning, vomiting, diarrhea, stomach bug, threw up, nausea
**Signs:** nausea, vomiting, stomach cramps, diarrhea, mild fever. Usually starts hours after eating contaminated food.
**Steps:**
1. Rest. Avoid solid food until vomiting stops.
2. Small, frequent sips of water, ORS, or clear fluids. Ice chips can help if sipping is hard.
3. Once vomiting stops, try bland foods: crackers, toast, rice, bananas.
4. Avoid dairy, fatty food, alcohol, and caffeine until recovered.
5. Wash hands often — this is contagious.
**Don't:** Don't take anti-diarrhea medicine if there's fever or bloody stool — it can trap the infection. Don't give aspirin to children.
**Get care if:** bloody stool or vomit; high fever (over 102°F / 39°C); signs of dehydration (see entry 35); symptoms lasting more than 3 days; the person is an infant, elderly, pregnant, or has a weakened immune system. Call 911 if unresponsive or unable to keep any fluids down for many hours.

---

End of library. Review annually against current Red Cross guidance. Last updated: 2026-10-16.
