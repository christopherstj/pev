"""Live Bafang BBSHD telemetry over the display UART.

The laptop impersonates the stock display: it polls the controller over the
green Higo connector via the USB programming cable and prints speed, current,
battery, and status in a live terminal line.

Usage:
    python bafang_sniff.py                  # auto-detect COM port
    python bafang_sniff.py --port COM5      # explicit port
    python bafang_sniff.py --raw            # hex-dump every exchange
    python bafang_sniff.py --wheel-circ 2.24   # meters (28x1.75 default)

Read-only: sends only 0x11 read requests, never 0x16 writes.
"""
import argparse
import sys
import time

import serial
from serial.tools import list_ports

BAUD = 1200
NOMINAL_VOLTS = 52.0  # Luna pack nominal, used for watts estimate only

STATUS_NAMES = {0x00: "ok", 0x01: "pedaling", 0x03: "brake"}


def find_port():
    ports = list(list_ports.comports())
    likely = [p for p in ports if any(
        tag in (p.description or "").upper() + (p.manufacturer or "").upper()
        for tag in ("CH340", "CH341", "CH910", "PL2303", "USB-SERIAL", "WCH", "PROLIFIC", "FTDI")
    )]
    if len(likely) == 1:
        return likely[0].device
    if not likely and len(ports) == 1:
        return ports[0].device
    print("Could not auto-pick a COM port. Available ports:")
    for p in ports:
        print(f"  {p.device}: {p.description}")
    print("Re-run with --port COMx")
    sys.exit(1)


def xact(ser, request, resp_len, raw=False):
    """Send a read request, return response bytes (or None on timeout)."""
    ser.reset_input_buffer()
    ser.write(request)
    resp = ser.read(resp_len)
    if raw:
        req_hex = " ".join(f"{b:02X}" for b in request)
        resp_hex = " ".join(f"{b:02X}" for b in resp) if resp else "(timeout)"
        print(f"  > {req_hex}   < {resp_hex}")
    return resp if len(resp) == resp_len else None


def read_status(ser, raw):
    r = xact(ser, b"\x11\x08", 1, raw)
    return r[0] if r else None


def read_current(ser, raw):
    r = xact(ser, b"\x11\x0A", 2, raw)
    if r and r[0] == r[1]:
        return r[0] / 2.0
    return None


def read_battery(ser, raw):
    r = xact(ser, b"\x11\x11", 2, raw)
    if r and r[0] == r[1]:
        return r[0]
    return None


def read_speed_rpm(ser, raw):
    r = xact(ser, b"\x11\x20", 3, raw)
    if r and ((r[0] + r[1] + 0x20) & 0xFF) == r[2]:
        return (r[0] << 8) | r[1]
    return None


def read_moving(ser, raw):
    r = xact(ser, b"\x11\x31", 2, raw)
    if r and r[0] == r[1]:
        return r[0] == 0x31
    return None


def main():
    ap = argparse.ArgumentParser(description="Live BBSHD telemetry via display UART")
    ap.add_argument("--port", help="COM port (default: auto-detect)")
    ap.add_argument("--wheel-circ", type=float, default=2.24,
                    help="wheel circumference in meters (default 2.24 = 28x1.75)")
    ap.add_argument("--raw", action="store_true", help="hex-dump every exchange")
    args = ap.parse_args()

    port = args.port or find_port()
    print(f"Opening {port} @ {BAUD} baud (8N1). Ctrl+C to stop.")
    print("Battery ON (XT90 in), charger UNPLUGGED. Controller answers only when awake.")

    # This CH340 clone needs a long cooldown after any open attempt (pass or
    # fail) before the next one can succeed. Never hammer; wait and retry.
    ser = None
    for attempt in range(1, 7):
        try:
            ser = serial.Serial(port, BAUD, timeout=0.3)
            break
        except serial.SerialException:
            print(f"port busy/wedged (attempt {attempt}); cooling down 15s...")
            time.sleep(15)
    if ser is None:
        print("Could not open the port. Unplug/replug the USB end, wait 15s, rerun.")
        sys.exit(1)

    with ser:
        misses = 0
        battery = None
        last_battery_poll = 0.0
        while True:
            rpm = read_speed_rpm(ser, args.raw)
            amps = read_current(ser, args.raw)
            status = read_status(ser, args.raw)

            now = time.monotonic()
            if now - last_battery_poll > 5.0:  # battery changes slowly
                b = read_battery(ser, args.raw)
                if b is not None:
                    battery = b
                last_battery_poll = now

            if rpm is None and amps is None and status is None:
                misses += 1
                if misses in (5, 50):
                    print("\nNo response — is the battery switch on and the cable "
                          "seated at the green Higo connector?")
                time.sleep(0.5)
                continue
            misses = 0

            kph = (rpm or 0) * args.wheel_circ * 60.0 / 1000.0
            mph = kph * 0.621371
            watts = (amps or 0.0) * NOMINAL_VOLTS
            stat = STATUS_NAMES.get(status, f"0x{status:02X}" if status is not None else "?")
            batt = f"{battery:3d}%" if battery is not None else "  ?%"

            line = (f"{kph:5.1f} kph ({mph:4.1f} mph) | {amps if amps is not None else 0:5.1f} A "
                    f"~{watts:6.0f} W | batt {batt} | {stat:<8}")
            if args.raw:
                print(line)
            else:
                print("\r" + line, end="", flush=True)
            time.sleep(0.15)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nbye")
