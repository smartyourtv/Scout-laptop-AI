#!/bin/bash
# download-manuals.sh — fetch the van manuals library (run with internet).
# Downloads go into this same folder. Re-run anytime; existing files are skipped.
# Manuals are copyrighted by their manufacturers — this script fetches them from
# the publishers'/retailers' servers for personal offline use. It copies no text.
set -u
cd "$(dirname "$0")"

get() { # get <filename> <url>
  if [ -f "$1" ]; then echo "SKIP (exists): $1"; return; fi
  echo "GET: $1"
  curl -sL --max-time 120 -A "Mozilla/5.0" -o "$1.tmp" "$2" \
    && file "$1.tmp" | grep -qi "PDF" \
    && mv "$1.tmp" "$1" && echo "OK: $1" \
    || { echo "FAILED: $1 — fetch it by browser from the URL in the notes below"; rm -f "$1.tmp"; }
}

# --- Verified direct downloads (HTTP 200 + PDF, checked 2026-10-16) ---
get "orion-tr-smart-dc-dc-charger-isolated-manual.pdf" \
  "https://cdn.customfields.bonify.io/intellitec.myshopify.com/fields/products/manual/4466861703266/Manual-Orion-Tr-Smart-Charger-Isolated-EN-NL-FR-DE-SE-PL.pdf"
get "thinkpad-p1-gen5-x1-extreme-setup-guide.pdf" \
  "https://download.lenovo.com/pccbbs/mobiles_pdf/tp_p1_x1extreme_sg_en.pdf"
get "blu-view-speed-ultra-5g-b1660v-user-guide.pdf" \
  "https://fccpdf.com/YHL/YHLBLUB1660V/8064259.pdf"
# ThinkPad P1 Gen 5 FULL User Guide (72 pp, ~17 MB, verified 2026-10-17).
get "thinkpad-p1-gen5-user-guide.pdf" \
  "https://download.lenovo.com/pccbbs/pubs/x1e_p1_gen5/html/html_en/book.pdf"
# Victron MPPT solar charger manual, Rev 13 (68 pp, verified 2026-10-17).
# NOTE: this is Victron's unified 75/10–100/20 manual (doc 29694). The PDF
# link on Victron's SmartSolar index page points to the same file under a
# Manual_SmartSolar_ folder and returns 404 (Victron's broken link); the
# working official copy sits under the Manual_BlueSolar_ folder — same
# document, covers the SmartSolar 100/20 (specs + dimension drawings).
get "victron-smartsolar-mppt-100-20-manual.pdf" \
  "https://www.victronenergy.com/upload/documents/Manual_BlueSolar_MPPT_75-10_up_to_100-20/29694-MPPT_solar_charger_manual-pdf-en.pdf"

# --- Fetch by browser (no working direct link found) ---
# 0. Giandel PS-1500SAR/PS-2000SAR inverter manual:
#    VERIFIED direct download via the Wayback Machine (manuals.plus blocks
#    automated download with a bot challenge page):
#    https://web.archive.org/web/20220528194728/https://manuals.plus/m/46ed5d76e44e88e985dfed479780517c9359c723a85051e73527d0c23f6ddc7b_optim.pdf
#    Save as: giandel-ps-1500sar-ps-2000sar-manual.pdf
#    Summary: giandel-ps-1500sar-ps-2000sar-manual-summary.md
#
# 1. Boss BCPA9 user manual:
#    VERIFIED URL (manual text indexed in full; checked again 2026-10-17):
#    https://manuals.plus/asin/B08TQMPH84.pdf
#    Still NOT fetchable by script — manuals.plus returns 403 (bot
#    challenge) to automated download, and no Wayback Machine snapshot
#    of the PDF exists (checked 2026-10-17). No manual PDF found on
#    bossaudio.com. Fetch it BY BROWSER from the URL above.
#    Save as: boss-bcpa9-user-manual.pdf
#    Summary (from the indexed manual text): boss-bcpa9-manual-summary.md
#
# 2. Victron SmartSolar MPPT 100/20 manual: DONE — moved to the verified
#    direct downloads above 2026-10-17 (see the NOTE there about Victron's
#    broken SmartSolar-folder PDF link). Summary:
#    victron-smartsolar-mppt-100-20-manual-summary.md
#
# 3. Victron Orion-Tr Smart — confirm exact variant first (see inventory gaps).
#    The family manual above covers the Isolated range; the non-isolated range
#    has a separate manual on victronenergy.com if yours is non-isolated.
#
# 4. Lenovo ThinkPad P1 Gen 5 full User Guide: DONE — moved to the verified
#    direct downloads above 2026-10-17 (download.lenovo.com book.pdf,
#    72 pp). Summary: thinkpad-p1-gen5-user-guide-summary.md
#
# 5. SUNER SP-30A-MPPT: no manual found online. Use the paper manual from the box;
#    scan/photo it, or photograph the label and send it to Scout to search again.
#
# 6. Inverter, battery bank, solar panels, JOINGLO DVR, van phone:
#    manuals pending — need brand/model first (see van-manuals-inventory.md gaps).
#
# 7. Frigidaire EFR182 mini fridge — PDF NOT downloadable (manuals.plus
#    bot-challenge; no Wayback snapshot, incl. _optim variant). Library entry is
#    the summary: frigidaire-efr182-mini-fridge-manual-summary.md.
#
# 8. Mainstays MS8436127995 microwave — PDF NOT downloadable (same block).
#    Library entry is the summary from Shawn's paper-manual photos + indexed
#    manual text: mainstays-ms8436127995-microwave-manual-summary.md.
#
# 9. E-LekTech LiFePO4 battery (van bank: 12V 500Ah, model discontinued) —
#    manual obtained as photos from Shawn (all 11 pages, 2026-10-16); the
#    manual gives no PDF URL (website root www.e-lektech.com only), so there
#    is nothing to fetch here. Library entry: e-lektech-lifepo4-battery-manual-summary.md.

echo "Done. Check the folder for any FAILED lines and fetch those by browser."
