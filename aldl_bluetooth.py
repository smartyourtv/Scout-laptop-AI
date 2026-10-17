#!/usr/bin/env python3
"""
aldl_bluetooth.py — ALDL over Bluetooth SPP client skeleton (laptop Scout).

Phase C (2026-10-16). The van is OBD1: 1992 GMC G2500 Vandura, 5.7L TBI V8,
12-pin ALDL at 8192 baud (RPM, coolant temp, MAP, TPS, O2, spark advance,
IAC, battery voltage, speed, fuel trim). The adapter must be ALDL-specific
with a Bluetooth SPP bridge — OBD2/ELM327 adapters do NOT work here.

What this module is (off-device buildable):
  * Transport layer with graceful degradation:
      1. pybluez RFCOMM socket (if installed)
      2. pyserial on /dev/rfcommN (if pyserial installed + bound)
      3. neither → honest diagnostics ("no Bluetooth serial available"),
         never a fake connection.
  * Laptop-priority arbitration: a single-owner lock file. The ThinkPad
    holds the connection; the phone (ALDLdroid) may connect only when
    the laptop releases it. If both want it, the laptop wins and the
    phone reads engine data via Scout instead (spec, Shawn 2026-10-16).
  * Frame reader interface + ADX hook: ALDL frames carry a mode/header
    and a checksum; FIELD DECODING needs the ECM's ADX definition file,
    which is NOT yet obtained (blocker). The parser interface is here;
    decode() raises NotImplementedError with that stated plainly rather
    than guessing at byte meanings — Scout never guesses (standing rule).

Blockers (unchanged by this module): a purchasable ALDL Bluetooth adapter
source, and the ECM's ADX file. Both are listed in PHASE-C-STATUS.md.
"""

import json
import os
import sys
import time

DEFAULT_LOCK_PATH = os.path.expanduser("~/.scout/aldl-owner.lock")
DEFAULT_RFCOMM_DEV = "/dev/rfcomm0"
ALDL_BAUD = 8192

# Fields the ADX will define offsets/scales for. Interface only — no
# offsets are asserted here because the ADX is not yet obtained.
ALDL_FIELDS = ("rpm", "coolant_temp_f", "speed_mph", "map_kpa",
               "tps_pct", "o2_volts", "spark_advance_deg", "iac_steps",
               "battery_volts", "fuel_trim")


# ── arbitration (laptop priority, single owner) ─────────────────────

class AldlOwnershipError(Exception):
    pass


class OwnerLock:
    """Single-owner lock file with owner tag + timestamp. The laptop
    acquires as owner='laptop'; a phone-side helper would use
    owner='phone' and must fail while the laptop holds it."""

    def __init__(self, path=None, owner="laptop"):
        self.path = path or DEFAULT_LOCK_PATH
        self.owner = owner

    def current_owner(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def acquire(self, stale_after_s=300):
        held = self.current_owner()
        if held and held.get("owner") != self.owner:
            age = time.time() - float(held.get("ts", 0))
            if age < stale_after_s:
                raise AldlOwnershipError(
                    f"ALDL link owned by {held.get('owner')} "
                    f"({int(age)}s ago). Laptop has priority; the other "
                    "side reads engine data via Scout.")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"owner": self.owner, "ts": time.time(),
                       "pid": os.getpid()}, f)
        os.replace(tmp, self.path)
        return True

    def release(self):
        held = self.current_owner()
        if held and held.get("owner") == self.owner:
            try:
                os.remove(self.path)
            except OSError:
                pass


# ── transport (degrades honestly) ───────────────────────────────────

def available_transports():
    """Probe what's importable/present. Returns ordered [(name, ok, why)]."""
    out = []
    try:
        import bluetooth  # pybluez  # noqa: F401
        out.append(("pybluez-rfcomm", True, "pybluez importable"))
    except Exception as e:
        out.append(("pybluez-rfcomm", False, f"pybluez not installed ({e})"))
    try:
        import serial  # pyserial  # noqa: F401
        dev_ok = os.path.exists(DEFAULT_RFCOMM_DEV)
        out.append(("pyserial-rfcomm", dev_ok,
                    f"pyserial present; {DEFAULT_RFCOMM_DEV} "
                    + ("exists" if dev_ok else "not bound (rfcomm bind needed)")))
    except Exception as e:
        out.append(("pyserial-rfcomm", False, f"pyserial not installed ({e})"))
    out.append(("bluetooth-adapter-hardware", os.path.isdir("/sys/class/bluetooth"),
                "/sys/class/bluetooth "
                + ("present" if os.path.isdir("/sys/class/bluetooth")
                   else "absent on this machine")))
    return out


class AldlTransport:
    """One SPP connection. connect() raises AldlOwnershipError /
    RuntimeError with a plain-language reason when it can't — it never
    pretends to be connected."""

    def __init__(self, address=None, rfcomm_dev=DEFAULT_RFCOMM_DEV,
                 channel=1, lock=None):
        self.address = address          # adapter Bluetooth MAC (setting)
        self.rfcomm_dev = rfcomm_dev
        self.channel = channel
        self.lock = lock or OwnerLock()
        self._sock = None
        self._serial = None
        self.mode = None                # "pybluez" | "pyserial"

    def connect(self):
        self.lock.acquire()
        transports = dict((n, ok) for n, ok, _ in available_transports())
        # 1) pybluez RFCOMM
        if transports.get("pybluez-rfcomm") and self.address:
            import bluetooth
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((self.address, self.channel))
            self._sock, self.mode = sock, "pybluez"
            return self.mode
        # 2) pyserial on a bound rfcomm device
        if transports.get("pyserial-rfcomm"):
            import serial
            self._serial = serial.Serial(self.rfcomm_dev, ALDL_BAUD,
                                         timeout=2)
            self.mode = "pyserial"
            return self.mode
        self.lock.release()
        raise RuntimeError(
            "No usable ALDL Bluetooth transport: pybluez not installed "
            "and no bound /dev/rfcomm device with pyserial. On the "
            "ThinkPad: pair the ALDL adapter, `rfcomm bind`, and/or "
            "`pip install pyserial` (see diagnostics()).")

    def read(self, n):
        if self._sock is not None:
            return self._sock.recv(n)
        if self._serial is not None:
            return self._serial.read(n)
        raise RuntimeError("ALDL transport is not connected.")

    def write(self, data):
        if self._sock is not None:
            return self._sock.send(data)
        if self._serial is not None:
            return self._serial.write(data)
        raise RuntimeError("ALDL transport is not connected.")

    def close(self):
        for obj, meth in ((self._sock, "close"), (self._serial, "close")):
            if obj is not None:
                try:
                    getattr(obj, meth)()
                except Exception:
                    pass
        self._sock = self._serial = None
        self.mode = None
        self.lock.release()


# ── frames + ADX hook ───────────────────────────────────────────────

def aldl_checksum(data):
    """ALDL checksum: two's complement of the byte sum (mod 256)."""
    return (-sum(data)) & 0xFF


class Frame:
    def __init__(self, raw):
        self.raw = bytes(raw)

    @property
    def checksum_ok(self):
        return len(self.raw) >= 2 and aldl_checksum(self.raw[:-1]) == self.raw[-1]


class AdxDefinition:
    """ADX definition-file hook. The ADX for this van's ECM is NOT yet
    obtained — load() accepts a parsed field map when it exists; until
    then decode() refuses rather than guessing byte meanings."""

    def __init__(self, field_map=None, source=None):
        self.field_map = field_map      # {field: (offset, scale, bias)}
        self.source = source

    @classmethod
    def load(cls, path):
        """TODO(ADX): parse the ECM's .adx (XML) once obtained. The file
        format hook lives here; field extraction lands with the file."""
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"ADX file not found: {path}. Obtain the ADX for this "
                "ECM (same file TunerPro RT + ALDLdroid need) and keep "
                "it with the install files.")
        raise NotImplementedError(
            "ADX parsing is a stub until the ECM's ADX file is obtained "
            "(blocker — see PHASE-C-STATUS.md). No field decoding is "
            "guessed at in the meantime.")

    def decode(self, frame):
        if not self.field_map:
            raise NotImplementedError(
                "No ADX field map loaded — ALDL fields cannot be decoded "
                "yet (ADX blocker). Raw frames still read + checksum.")
        values = {}
        for field, (offset, scale, bias) in self.field_map.items():
            if offset < len(frame.raw):
                values[field] = frame.raw[offset] * scale + bias
        return values


class FrameReader:
    """Reads length-framed ALDL messages from a transport. ALDL data
    mode streams frames continuously once the mode request is sent;
    exact framing (header byte + length) is confirmed against the ADX
    when it arrives — the reader is deliberately conservative."""

    def __init__(self, transport, adx=None):
        self.transport = transport
        self.adx = adx or AdxDefinition()

    def read_frame(self, max_bytes=128):
        chunk = self.transport.read(max_bytes)
        if not chunk:
            raise RuntimeError("ALDL link returned no data (adapter "
                               "asleep, out of range, or not in data mode).")
        return Frame(chunk)

    def read_values(self):
        frame = self.read_frame()
        if not frame.checksum_ok:
            raise RuntimeError("ALDL frame checksum failed — discarding "
                               "(noise or wrong baud/mode).")
        return self.adx.decode(frame)


# ── diagnostics + self-test ─────────────────────────────────────────

def diagnostics():
    lines = ["ALDL Bluetooth — diagnostics"]
    for name, ok, why in available_transports():
        lines.append(f"- {name}: {'available' if ok else 'unavailable'} ({why})")
    held = OwnerLock().current_owner()
    lines.append(f"- Link owner: {held.get('owner') if held else 'nobody'} "
                 "(laptop has priority when it holds the link)")
    lines.append("- Adapter: ALDL-specific Bluetooth SPP (NOT OBD2/ELM327) "
                 "— purchasable source still open (blocker).")
    lines.append("- ADX definition file for this ECM: NOT obtained "
                 "(blocker) — frames can be read/checksummed, fields "
                 "cannot be decoded until it arrives.")
    return "\n".join(lines)


def self_test():
    ok_all = True

    def check(label, cond, detail=""):
        nonlocal ok_all
        print(("PASS  " if cond else "FAIL  ") + label +
              (f"  {detail}" if detail and not cond else ""))
        ok_all = ok_all and bool(cond)

    import tempfile
    with tempfile.TemporaryDirectory(prefix="aldl_test_") as tmp:
        lock_path = os.path.join(tmp, "owner.lock")
        laptop = OwnerLock(lock_path, owner="laptop")
        phone = OwnerLock(lock_path, owner="phone")
        laptop.acquire()
        check("laptop acquires ownership", laptop.current_owner()["owner"] == "laptop")
        try:
            phone.acquire()
            check("phone blocked while laptop holds link (priority)", False)
        except AldlOwnershipError:
            check("phone blocked while laptop holds link (priority)", True)
        laptop.release()
        phone.acquire()
        check("phone may acquire after laptop releases", True)
        phone.release()
        frame = Frame(bytes([0xF4, 0x57, 0x01, 0x00]))
        frame = Frame(frame.raw[:-1] + bytes([aldl_checksum(frame.raw[:-1])]))
        check("frame checksum round-trip", frame.checksum_ok)
        bad = Frame(bytes([0xF4, 0x57, 0x01, 0x00, 0x00]))
        check("bad checksum detected", not bad.checksum_ok)
        try:
            AdxDefinition().decode(frame)
            check("decode refuses without ADX (no guessing)", False)
        except NotImplementedError:
            check("decode refuses without ADX (no guessing)", True)
        transports = available_transports()
        check("transport probe honest (list returned)",
              len(transports) == 3 and all(len(t) == 3 for t in transports),
              str(transports))
        t = AldlTransport(lock=OwnerLock(os.path.join(tmp, "o2.lock")))
        try:
            t.connect()
            check("connect without adapter reports honestly", False,
              "unexpectedly connected on build VM")
            t.close()
        except (RuntimeError, AldlOwnershipError) as e:
            check("connect without adapter reports honestly", True, str(e)[:80])
    print("aldl_bluetooth self_test:",
          "ALL PASS" if ok_all else "FAILURES PRESENT")
    return ok_all


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    if "--diagnostics" in sys.argv:
        print(diagnostics())
        sys.exit(0)
    print(__doc__)
