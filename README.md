# Scout Laptop AI

Van Scout — the big brain that runs on the ThinkPad in the van (Qwen3.6-35B-A3B).
The phone app (Scout Android) is the face; this repo is the laptop side.

## Files

- `start-usb-prep.bat` — Double-click on the Windows home PC to launch the USB prep tool.
- `usb-prep.py` — Prepares the 512GB flash drive: Ubuntu installer + ~300GB of models/maps/data + the installer below.
- `scout-installer.py` — Runs on the ThinkPad from the prepared USB; sets up Ubuntu + Scout + all models.
- `scout-persona.txt` — Scout's system prompt / personality for the van.
- `outpost_client.py` — Python client for Outpost (Shield/TV-box control) from the ThinkPad.
- `scout-thinkpad-home-spec.md` — The living spec: architecture, network, multi-instance, wake words, queue, and the app-parity checklist.
- `name_sync.py` — ThinkPad-side name sync: canonical name store + HTTP sync API (port 8091). Change the name on either body, both share one name. Run `python3 name_sync.py --self-test` to verify.
- `NAME-SYNC-PROTOCOL.md` — The name-sync wire protocol: message format, endpoints, conflict rule, offline/queue behavior, wake-word rule.

## Status

Install chain is UI shells with TODO stubs — real logic lands at "pull it together."
See `scout-thinkpad-home-spec.md` for the full plan.
