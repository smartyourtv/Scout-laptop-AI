# MDVR Manual — Transcribed Summary (JOINLGO 4CH)

**Source:** Paper manual photographed by Shawn, 2026-10-16 (13 photos, pages 2–27). This file is a summary of that manual for the manuals library — not a copy of the manual itself.
**Applies to:** JOINLGO 4CH Mobile DVR (MDVR) — the van unit (J2-4GW-AF) and the G2-WS spare share this manual family. Both point at the CMSV7 server (see Network).
**Full manual status:** Paper copy is the source. No PDF located online yet.

## Identification

- **Brand:** JOINLGO (YouTube channel under the same name)
- **Type:** 4CH Mobile DVR (MDVR), 4-channel AHD
- **Chipset:** HiSilicon Hi3520DV300
- **Compression:** H.264
- **Video inputs:** 4CH AHD, supports 1080p / 720p / 960H / D1 / CIF
- **Audio:** 4CH audio input
- **Outputs:** 1CH VGA + 1CH HDMI
- **Connectivity (optional modules):** GPS/BD, 3G/4G, WiFi (802.11b/g/n, 2.4 GHz)
- **Storage:** 2× SD slots (up to 256 GB each) and/or HDD/SSD (up to 2 TB)
- **Sensors:** Built-in G-sensor
- **Dimensions:** 147 × 180 × 41 mm (SD-card version); 148 × 188 × 60 mm (hard-disk version)
- **Weight:** ~1.0–1.5 kg (net)
- **Operating temp:** −20 °C to +70 °C

## Power + wiring — the important part

| Wire / pin | Meaning |
|---|---|
| Red | +12V / +24V (battery positive) |
| Black | Ground |
| Yellow | ACC / ignition — **must get power or the MDVR will not start** (and will shut down) |

- **Input voltage:** DC 8–36V. Below 8V or above 36V → shutdown protection.
- **Consumption:** max 30W @ 12V; standby 3 mA.
- **Output:** 12V ± 0.2V, max 2A (for cameras).
- **4-pin aviation connector (per camera):** 1 = +12V, 2 = GND, 3 = AIN (audio), 4 = VIN (video).
- **I/O interface (8 pins):** Alarm 1–4 (inputs), Alarm Output, 485A, 485B, GND.
- **Alarm outputs** are voltage outputs, drive capability 200 mA. For larger loads, drive an external relay.
- **Remote controller:** not included — buy a CR2025 battery locally if you want one (manual p.26).
- **Remote controller battery:** CR2025 (not included).

### "MDVR won't power on" (FAQ #1)

Check in this order: (A) make sure the **YELLOW ACC wire** gets power; (B) make sure the **SD card door is locked**; (C) try another SD card to test.

## Storage + recording

- **Recording resolutions:** 1080p / 720p / 960H / D1 / CIF per channel (default password account: Admin).
- **Video bitrate:** up to 4096 kbps. **Audio bitrate:** 8 KB/s.
- **File length:** default 15 minutes per file.
- **Overwrite:** automatic — oldest files are overwritten when storage fills.
- **Format on first use:** a new SD card / hard disk MUST be formatted in the MDVR first (Main Menu → Basic → HD Management → Format). If the system shows "HDD ERR" after inserting a card, format it.
- **If the MDVR turns on and off repeatedly:** a bad SD card can cause this — remove/replace the card and test.
- **Playback:** by file (recorded files) or by time (timeline search).
- **Recording resolution** is set per channel: Main → Record → Resolution (CIF / HD1 / D1 / 960H / 720P).

## Menu map (for finding settings)

**Main Menu:** SEARCH · RECORD · BASIC · INFO · VEHICLE · DISPLAY · PASSWORD · EXIT

- **SEARCH:** playback by file or by time; backup to USB.
- **RECORD:** per-channel resolution, frame rate, quality, audio on/off, record mode.
- **BASIC →**
  - **Alarm:** 4 alarm inputs; set trigger type, alarm output, buzzer.
  - **PTZ:** PTZ camera control (if fitted).
  - **Date/Time:** date, time, time zone, format.
  - **HD Management:** format SD/HDD, check status.
  - **System Maintain:** restore defaults, upgrade firmware, reboot.
  - **Network:** server address, server port, network type.
  - **System Setup:** language, video standard, device ID, auto-record, etc.
- **INFO:** system info (serial number, software version, MAC address, SIM/GPS/WiFi/wireless module status) + network status.
- **VEHICLE →**
  - **Basic:** plate number, vehicle info.
  - **ACC:** ACC on/off behavior.
  - **ON/OFF:** scheduled power on/off.
  - **Wireless:** 4G module settings, APN (set per your SIM card — see FAQ).
  - **WiFi:** WiFi settings.
  - **GPS:** GPS settings (baud rate 9600, send interval), overspeed alarm, low-speed alarm, parking timeout alarm.
- **DISPLAY:** channel name, preview mode, image flip (horizontal/vertical), OSD, record-time overlay, GPS overlay.
- **PASSWORD:** device ID, use-password on/off, Admin password, User password. Only Admin can set passwords. (Factory default password is printed in the manual — change it before the unit is exposed to any network. Passwords are not recorded in this library.)
- **EXIT:** leave the menu.

## Network / CMSV7 (vendor cloud)

- **Server:** 47.88.8.31 (same for the van DVR and the G2-WS spare).
- **Server port:** 6608 (shown in manual as 06608).
- **CMSV7 web / download:** http://47.88.8.31:808/gps/login.html — Windows version, iOS version, Android version, and Playback client available there.
- **CMSV7 app:** search "CMSV7" in the app store.
- **Phone login** uses the same account as the PC client (account = the name on the device label).
- **Network status screen (INFO):** GPS: YES/NO (GPS module recognized), LAT/LNG (GPS fix), 4G: YES/NO (4G module recognized), SIM: YES/NO (SIM card recognized), 4G ONLINE: YES/NO (networked), CMS ONLINE: YES/NO (connected to the server).
- **4G setup:** Main → Vehicle → Wireless → User Setup APN — enter the APN for your SIM card's carrier.
- **Plate number change:** log into the CMSV6 client software or webpage → Operation → Vehicle → Edit → enter plate number → save. To change company name / server, contact the vendor (server is free to change per the manual).

## Alarms / I/O (manual §6)

- **4 alarm inputs.** Alarm input detection is by voltage — it can detect high or low voltage (e.g., brake pedal, steering, horn, door).
- **Brake test schematic** in the manual: brake plate → brake light → I/O cable; when the brake pedal is pressed, the MDVR detects it.
- **Alarm output:** voltage output, 200 mA drive capability. For large-power devices, use external relays (schematic in manual §6).
- **Overspeed / low-speed alarms:** set thresholds in Vehicle → GPS. The device alarms when speed is above the overspeed value or below the low-speed value.
- **Parking timeout:** alarm after the vehicle is parked longer than the set time.

## FAQ highlights (manual §9)

- **MDVR won't power on:** yellow ACC wire power → SD door locked → try another SD card.
- **"HDD ERR" after inserting an SD card:** format the card in the MDVR first; if it still shows, change to another SD card.
- **MDVR turns on and off automatically:** bad SD card is the usual cause — remove/replace it.
- **How to connect and use the I/O cable:** supports 4-channel alarm input (see §6).
- **Recording resolution:** Main → Record → Resolution (CIF / HD1 / D1 / 960H / 720P).
- **Rearview image mirrored:** OSD menu → Admin account → Operation → Display → check Horizontal Flip.
- **Download the APP / CMSV6 / PC playback software:** from the CMSV7 web address above.
- **Configure 4G:** input the APN for your 4G SIM card (Main → Vehicle → Wireless → User Setup APN).
- **Change plate number on CMSV6:** log in → Operation → Vehicle → Edit → save.

## Notes for the self-hosted backend work (Sat Oct 17)

- **Known-good vendor endpoints:** server 47.88.8.31, port 6608 (device → server), web 808. These are the values the cutover must replace — record them before changing anything on the live DVR.
- **The device talks JT808-style telemetry + video to the vendor server.** The self-hosted plan (Traccar GPS + Frigate video) must prove itself with a non-DVR GPS source and a test stream BEFORE touching the live DVR — the G2-WS spare cannot be re-pointed (its Admin password is lost).
- **Local recording is independent of the server.** Even if the vendor server disappeared, the DVR keeps recording to SD/HDD locally. Only remote viewing / GPS tracking depends on the server.
- **Do not factory-reset the live DVR** during testing — settings (server, plate, passwords) would be lost.

*Transcribed 2026-10-16 from Shawn's photos of the paper manual. Passwords and device credentials are intentionally not recorded in this library.*
