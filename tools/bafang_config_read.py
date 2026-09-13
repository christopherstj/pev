"""READ-ONLY dump of the BBSHD's persistent config (EEPROM) over the display line.

Speaks the Bafang config-tool protocol (opcodes 0x51-0x54, same green cable):
  connect: 11 51 04 B0 05   -> info (manufacturer, model, HW/FW, voltage class, max current)
  basic:   11 52            -> low-batt cutoff, current limit, 10x2 assist table, wheel, speedmeter
  pedal:   11 53            -> PAS behavior (start current, decay, stop timing, ...)
  throttle:11 54            -> throttle voltages, speed/current mode, designated assist

Sends ONLY 0x11 reads — never 0x16 writes. Saves a timestamped backup JSON
into reference/ before any future tuning is allowed to happen.

    python tools/bafang_config_read.py
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

# Bafang wheel enum: 0x1F=16", 0x20=16"+, ... 0x35=27", 0x36=27"+,
# 0x37=700C, 0x38=28", 0x39=28"+, 0x3A=29", 0x3B=29"+, 0x3C=30", 0x3D=30"+
WHEEL_ENUM = {}
for i, code in enumerate(range(0x1F, 0x37)):
    WHEEL_ENUM[code] = f'{16 + i // 2}"' + ("+" if i % 2 else "")
WHEEL_ENUM[0x37] = "700C"
for i, code in enumerate(range(0x38, 0x3E)):
    WHEEL_ENUM[code] = f'{28 + i // 2}"' + ("+" if i % 2 else "")

VOLTAGE_ENUM = {0: "24V", 1: "36V", 2: "48V", 3: "60V", 4: "24-48V", 5: "24-60V"}
PEDAL_TYPE = {0: "none", 1: "DH-sensor-12", 2: "BB-sensor-32", 3: "double-signal-24"}
THROTTLE_MODE = {0: "speed", 1: "current"}


def open_serial():
    """Patient open — the CH340 clone needs ~15s cooldown after any attempt."""
    while True:
        cands = [p.device for p in list_ports.comports()
                 if "CH340" in (p.description or "").upper()]
        if not cands:
            print("no CH340 cable found; waiting...", flush=True)
            time.sleep(3)
            continue
        try:
            s = serial.Serial(cands[0], BAUD, timeout=0.5)
            print(f"opened {cands[0]}", flush=True)
            return s
        except serial.SerialException:
            print("port wedged; cooling down 15s...", flush=True)
            time.sleep(15)


def xact(ser, cmd, tries=4):
    for i in range(tries):
        ser.reset_input_buffer()
        ser.write(cmd)
        ser.flush()
        time.sleep(1.0)
        resp = ser.read(100)
        # a dead/unpowered line reads as endless 0x00 (break condition) —
        # that's silence wearing a costume, not an answer
        if resp and any(resp):
            return bytes(resp)
        why = "line dead (all zeros)" if resp else "no answer"
        print(f"  {why} for {cmd.hex(' ')} (try {i+1}) — battery on? cable seated?", flush=True)
        time.sleep(0.5)
    return b""


def wait_for_controller(ser, window_s=180):
    """Poll the display status opcode until the controller answers with life."""
    print("waiting for controller to wake (plug the XT90 in now)...", flush=True)
    t0 = time.monotonic()
    while time.monotonic() - t0 < window_s:
        ser.reset_input_buffer()
        ser.write(b"\x11\x08")
        time.sleep(0.4)
        r = ser.read(8)
        if r and any(r):
            print(f"controller is AWAKE (status {r.hex(' ')})", flush=True)
            return True
        time.sleep(1.5)
    print("controller never woke up within the window.", flush=True)
    return False


def ck_ok(resp):
    """Response checksum = (sum of all bytes before the last) % 256."""
    if len(resp) < 3:
        return False
    return sum(resp[:-1]) % 256 == resp[-1]


def parse_info(r):
    if len(r) < 19 or r[0] != 0x51:
        return {"error": f"unexpected: {r.hex(' ')}"}
    return {
        "manufacturer": r[2:6].decode(errors="replace"),
        "model": r[6:10].decode(errors="replace"),
        "hw_version": r[10:12].decode(errors="replace"),
        "fw_version": r[12:16].decode(errors="replace"),
        "voltage_class": VOLTAGE_ENUM.get(r[16], f"0x{r[16]:02X}"),
        "max_current_A": r[17],
    }


def parse_basic(r):
    if len(r) < 27 or r[0] != 0x52:
        return {"error": f"unexpected: {r.hex(' ')}"}
    return {
        "low_battery_protect_V": r[2],
        "current_limit_A": r[3],
        "assist_current_pct": list(r[4:14]),
        "assist_speed_pct": list(r[14:24]),
        "wheel_diameter": WHEEL_ENUM.get(r[24], f"0x{r[24]:02X}"),
        "speedmeter_model": ["external", "internal", "motorphase"][r[25] >> 6]
                            if (r[25] >> 6) < 3 else f"0b{r[25] >> 6:02b}",
        "speedmeter_signals": r[25] & 0x3F,
        "checksum_ok": ck_ok(r[:27]),
    }


def parse_pedal(r):
    if len(r) < 14 or r[0] != 0x53:
        return {"error": f"unexpected: {r.hex(' ')}"}
    return {
        "pedal_type": PEDAL_TYPE.get(r[2], f"0x{r[2]:02X}"),
        "designated_assist": "display" if r[3] == 0xFF else r[3],
        "speed_limit": "display" if r[4] == 0xFF else f"{r[4]} km/h",
        "start_current_pct": r[5],
        "slow_start_mode": r[6],
        "startup_degree": r[7],
        "work_mode": r[8],
        "time_of_stop_x10ms": r[9],
        "current_decay": r[10],
        "stop_decay_x10ms": r[11],
        "keep_current_pct": r[12],
        "checksum_ok": ck_ok(r[:14]),
    }


def parse_throttle(r):
    if len(r) < 9 or r[0] != 0x54:
        return {"error": f"unexpected: {r.hex(' ')}"}
    return {
        "start_voltage_x100mV": r[2],
        "end_voltage_x100mV": r[3],
        "mode": THROTTLE_MODE.get(r[4], f"0x{r[4]:02X}"),
        "designated_assist": "display" if r[5] == 0xFF else r[5],
        "speed_limit": "display" if r[6] == 0xFF else f"{r[6]} km/h",
        "start_current_pct": r[7],
        "checksum_ok": ck_ok(r[:9]),
    }


def main():
    ser = open_serial()
    out = {"date": str(date.today()), "note": "Bethel BBSHD stock config backup (read-only dump)"}
    with ser:
        if not wait_for_controller(ser):
            sys.exit(1)

        print("\n[1/4] connect / controller info", flush=True)
        r = xact(ser, b"\x11\x51\x04\xb0\x05")
        out["info"] = {"raw": r.hex(" "), **parse_info(r)}
        print(json.dumps(out["info"], indent=2))

        print("\n[2/4] BASIC page", flush=True)
        r = xact(ser, b"\x11\x52")
        out["basic"] = {"raw": r.hex(" "), **parse_basic(r)}
        print(json.dumps(out["basic"], indent=2))

        print("\n[3/4] PEDAL page", flush=True)
        r = xact(ser, b"\x11\x53")
        out["pedal"] = {"raw": r.hex(" "), **parse_pedal(r)}
        print(json.dumps(out["pedal"], indent=2))

        print("\n[4/4] THROTTLE page", flush=True)
        r = xact(ser, b"\x11\x54")
        out["throttle"] = {"raw": r.hex(" "), **parse_throttle(r)}
        print(json.dumps(out["throttle"], indent=2))

    dest = Path(__file__).resolve().parent.parent / "reference" / \
        f"bethel-config-backup-{date.today().strftime('%Y%m%d')}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nBACKUP SAVED: {dest}", flush=True)


if __name__ == "__main__":
    main()
