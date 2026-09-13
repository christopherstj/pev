"""One-shot Bethel contact test + config dump. Run once, right after a fresh USB replug.

Sequence for the human (do in THIS order):
  1. Unplug the green cable's USB end from the laptop.
  2. Unplug the XT90 (battery off).
  3. Replug the USB end (this resets the CH340 chip).
  4. Start this script. It opens the port, then waits, printing what it hears.
  5. When it says LISTENING, plug the XT90 in firmly (cable already bridges the
     latch, so she wakes talking).

Phase A: prove basic display-protocol contact (status/speed/battery) — the same
         reads that worked before. Verbose: shows real bytes / zeros / silence.
Phase B: only if she's talking, dump the 4 config pages and save a backup.
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

import serial
from serial.tools import list_ports

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BAUD = 1200


def find():
    return [p.device for p in list_ports.comports()
            if "CH340" in (p.description or "").upper()]


def quick_open():
    """Fresh replug should open fast; a few short tries, not the long cooldown."""
    for a in range(15):
        c = find()
        if c:
            try:
                return serial.Serial(c[0], BAUD, timeout=0.3)
            except serial.SerialException:
                pass
        print(f"  waiting for port ({a+1})...", flush=True)
        time.sleep(2)
    return None


def classify(r):
    if not r:
        return "nothing", "(silence)"
    if not any(r):
        return "zeros", "ALL ZEROS " + r.hex(" ")
    return "real", "REAL " + r.hex(" ")


def main():
    ser = quick_open()
    if not ser:
        print("OPEN FAILED — unplug/replug the USB end and rerun.", flush=True)
        sys.exit(1)
    print(f"opened {ser.port}. LISTENING — plug the XT90 in now (firm push).", flush=True)

    # Phase A: up to 90s hunting for the first real display-protocol response.
    polls = [("status", b"\x11\x08"), ("speed", b"\x11\x20"), ("battery", b"\x11\x11")]
    awake = False
    t0 = time.monotonic()
    while time.monotonic() - t0 < 90 and not awake:
        for name, cmd in polls:
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(0.3)
            kind, shown = classify(ser.read(32))
            if kind == "real":
                print(f"  {name}: {shown}", flush=True)
                awake = True
                break
        time.sleep(0.4)

    if not awake:
        print("\nVERDICT: no display-protocol response in 90s.", flush=True)
        print("She's electrically reachable but not answering — check XT90 seated,", flush=True)
        print("Higo arrows aligned & fully home, and that battery actually has charge.", flush=True)
        ser.close()
        sys.exit(2)

    print("\n*** BETHEL IS TALKING *** — proceeding to config dump.\n", flush=True)
    time.sleep(0.5)

    def xact(cmd, tries=4):
        for _ in range(tries):
            ser.reset_input_buffer()
            ser.write(cmd)
            ser.flush()
            time.sleep(1.0)
            r = ser.read(100)
            if r and any(r):
                return bytes(r)
            time.sleep(0.4)
        return b""

    out = {"date": str(date.today()), "note": "Bethel BBSHD stock config backup"}
    for tag, cmd in [("info", b"\x11\x51\x04\xb0\x05"), ("basic", b"\x11\x52"),
                     ("pedal", b"\x11\x53"), ("throttle", b"\x11\x54")]:
        r = xact(cmd)
        out[tag] = {"raw": r.hex(" ")}
        print(f"{tag:9}: {r.hex(' ') if r else '(no answer)'}", flush=True)

    ser.close()
    dest = Path(__file__).resolve().parent.parent / "reference" / \
        f"bethel-config-raw-{date.today().strftime('%Y%m%d')}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nRAW BACKUP SAVED: {dest}", flush=True)


if __name__ == "__main__":
    main()
