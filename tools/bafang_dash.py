"""Live BBSHD telemetry dashboard + control panel.

Polls the controller over the display UART (like bafang_sniff) and serves
live gauges at http://localhost:8722 via Server-Sent Events. The laptop IS
the display, so it can also send display-side commands: assist level,
lights, mode, and the display speed limit.

    python tools/bafang_dash.py

Write formats decoded from bbs-fw extcom.c (what real displays send):
  assist:      16 0B <code> <ck>   ck = sum of first 3 bytes
  lights:      16 1A <F0|F1>       no checksum
  mode:        16 0C <02|04> <ck>  02=default 04=sport
  speed limit: 16 1F <hi> <lo> <ck>  value = wheel max speed in RPM
"""
import json
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import serial
from serial.tools import list_ports

from bafang_sniff import (NOMINAL_VOLTS, STATUS_NAMES, read_battery,
                          read_current, read_speed_rpm, read_status)

BAUD = 1200
WHEEL_CIRC = 2.24
HTTP_PORT = 8722

STATE = {"kph": 0.0, "mph": 0.0, "amps": 0.0, "watts": 0, "batt": None,
         "status": "?", "link": False, "ts": 0.0, "echo": ""}
LOCK = threading.Lock()
CMDS = queue.Queue()

ASSIST_CODES = {0: 0x00, 1: 0x01, 2: 0x0B, 3: 0x0C, 4: 0x0D,
                5: 0x02, 6: 0x15, 7: 0x16, 8: 0x17, 9: 0x03}


def send_cmd(ser, cmd):
    """Execute one queued command; returns human echo string."""
    kind = cmd.get("action")
    if kind == "assist":
        lvl = int(cmd["value"])
        if lvl not in ASSIST_CODES:
            return "bad assist level"
        msg = bytes([0x16, 0x0B, ASSIST_CODES[lvl]])
        ser.write(msg + bytes([sum(msg) & 0xFF]))
        return f"assist -> {lvl}"
    if kind == "lights":
        on = bool(cmd["value"])
        ser.write(bytes([0x16, 0x1A, 0xF1 if on else 0xF0]))
        return f"lights -> {'ON' if on else 'off'}"
    if kind == "mode":
        sport = cmd["value"] == "sport"
        msg = bytes([0x16, 0x0C, 0x04 if sport else 0x02])
        ser.write(msg + bytes([sum(msg) & 0xFF]))
        return f"mode -> {'SPORT' if sport else 'default'}"
    if kind == "speed_limit":
        kph = max(10, min(99, int(cmd["value"])))
        rpm = int(kph * 1000 / 60 / WHEEL_CIRC)
        msg = bytes([0x16, 0x1F, (rpm >> 8) & 0xFF, rpm & 0xFF])
        ser.write(msg + bytes([sum(msg) & 0xFF]))
        return f"speed limit -> {kph} kph ({rpm} rpm)"
    return "unknown command"


def open_serial():
    """Patient open — this CH340 clone needs ~15s cooldown after any attempt."""
    while True:
        cands = [p.device for p in list_ports.comports()
                 if "CH340" in (p.description or "").upper()]
        if not cands:
            time.sleep(3)
            continue
        try:
            return serial.Serial(cands[0], BAUD, timeout=0.3)
        except serial.SerialException:
            time.sleep(15)


def poll_loop():
    last_batt = 0.0
    while True:
        ser = open_serial()
        try:
            while True:
                # drain pending commands first — writes get priority
                while not CMDS.empty():
                    try:
                        echo = send_cmd(ser, CMDS.get_nowait())
                        time.sleep(0.08)  # let 1200 baud breathe
                        ser.reset_input_buffer()
                        with LOCK:
                            STATE["echo"] = f"{time.strftime('%H:%M:%S')}  {echo}"
                    except queue.Empty:
                        break

                rpm = read_speed_rpm(ser, False)
                amps = read_current(ser, False)
                status = read_status(ser, False)
                batt = None
                now = time.time()
                if now - last_batt > 5:
                    batt = read_battery(ser, False)
                    last_batt = now
                with LOCK:
                    if rpm is not None:
                        STATE["kph"] = round(rpm * WHEEL_CIRC * 60 / 1000, 1)
                        STATE["mph"] = round(STATE["kph"] * 0.621371, 1)
                    if amps is not None:
                        STATE["amps"] = amps
                        STATE["watts"] = round(amps * NOMINAL_VOLTS)
                    if status is not None:
                        STATE["status"] = STATUS_NAMES.get(status, f"0x{status:02X}")
                    if batt is not None:
                        STATE["batt"] = batt
                    STATE["link"] = any(v is not None for v in (rpm, amps, status))
                    STATE["ts"] = now
                time.sleep(0.12)
        except serial.SerialException:
            try:
                ser.close()
            except Exception:
                pass
            with LOCK:
                STATE["link"] = False
            time.sleep(15)


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bethel Command Deck</title>
<style>
  body { margin:0; background:#0b0e14; color:#e5e9f0; font-family:'Segoe UI',system-ui,sans-serif;
         display:flex; flex-direction:column; align-items:center; min-height:100vh; }
  body.brake { background:#1a0b0e; }
  .wrap { margin-top:3vh; text-align:center; }
  h1 { font-size:15px; letter-spacing:.35em; color:#6b7280; font-weight:600; margin:0 0 6px; }
  svg { display:block; margin:0 auto; }
  .track { stroke:#1f2733; }
  .val { stroke:#22d3ee; transition:stroke-dashoffset .15s linear; }
  body.brake .val { stroke:#ef4444; }
  .mph { font-size:64px; font-weight:700; line-height:1; margin-top:-88px; }
  .mph small { font-size:17px; color:#6b7280; font-weight:400; }
  .kph { color:#6b7280; font-size:14px; margin-top:2px; }
  .row { display:flex; gap:12px; justify-content:center; margin-top:26px; }
  .card { background:#131a24; border:1px solid #1f2733; border-radius:12px; padding:10px 18px; min-width:84px; }
  .card .v { font-size:24px; font-weight:600; }
  .card .l { font-size:10px; letter-spacing:.15em; color:#6b7280; margin-top:2px; }
  #battv.good { color:#22c55e; } #battv.mid { color:#f59e0b; } #battv.low { color:#ef4444; }
  .chip { display:inline-block; margin-top:18px; padding:5px 16px; border-radius:999px;
          background:#131a24; border:1px solid #1f2733; font-size:12px; letter-spacing:.2em;
          text-transform:uppercase; color:#9ca3af; }
  body.brake .chip { background:#7f1d1d; color:#fff; border-color:#ef4444; font-weight:700; }
  .deck { margin-top:26px; background:#0f141d; border:1px solid #1f2733; border-radius:16px;
          padding:18px 22px 22px; max-width:560px; }
  .deck h2 { font-size:11px; letter-spacing:.3em; color:#6b7280; margin:0 0 12px; font-weight:600; }
  .btns { display:flex; gap:8px; justify-content:center; flex-wrap:wrap; }
  button { background:#131a24; color:#e5e9f0; border:1px solid #253044; border-radius:10px;
           padding:10px 0; width:44px; font-size:16px; font-weight:600; cursor:pointer; }
  button:hover { border-color:#22d3ee; }
  button.on { background:#0e7490; border-color:#22d3ee; color:#fff; }
  button.wide { width:auto; padding:10px 18px; font-size:13px; letter-spacing:.1em; }
  button.danger.on { background:#b45309; border-color:#f59e0b; }
  .slider-row { display:flex; align-items:center; gap:12px; margin-top:14px; }
  input[type=range] { flex:1; accent-color:#22d3ee; }
  .echo { margin-top:14px; font-size:12px; color:#22d3ee; min-height:16px; font-family:Consolas,monospace; }
  #link { position:fixed; inset:0; background:#0b0e14ee; display:flex; align-items:center;
          justify-content:center; font-size:17px; letter-spacing:.2em; color:#f59e0b; }
  #link.hide { display:none; }
  footer { margin-top:auto; padding:12px; font-size:10px; color:#374151; letter-spacing:.1em; }
</style></head><body>
<div class="wrap">
  <h1>BETHEL COMMAND DECK</h1>
  <svg width="300" height="168" viewBox="0 0 320 180">
    <path class="track" d="M 40 165 A 120 120 0 0 1 280 165" fill="none" stroke-width="14" stroke-linecap="round"/>
    <path class="val" id="arc" d="M 40 165 A 120 120 0 0 1 280 165" fill="none" stroke-width="14"
          stroke-linecap="round" stroke-dasharray="377" stroke-dashoffset="377"/>
  </svg>
  <div class="mph"><span id="mph">0.0</span> <small>mph</small></div>
  <div class="kph"><span id="kph">0.0</span> kph</div>
  <div class="row">
    <div class="card"><div class="v" id="watts">0</div><div class="l">WATTS</div></div>
    <div class="card"><div class="v" id="amps">0.0</div><div class="l">AMPS</div></div>
    <div class="card"><div class="v" id="battv">--%</div><div class="l">BATTERY</div></div>
  </div>
  <div class="chip" id="status">WAITING</div>

  <div class="deck">
    <h2>ASSIST LEVEL</h2>
    <div class="btns" id="assist"></div>
    <div class="btns" style="margin-top:14px">
      <button class="wide" id="lights">&#128161; LIGHTS</button>
      <button class="wide" id="mode-d">MODE: DEFAULT</button>
      <button class="wide danger" id="mode-s">MODE: SPORT</button>
    </div>
    <div class="slider-row">
      <span style="font-size:11px;color:#6b7280;letter-spacing:.15em">SPEED&nbsp;LIMIT</span>
      <input type="range" id="sl" min="10" max="99" value="40">
      <span id="slv" style="min-width:56px;font-weight:600">40 kph</span>
      <button class="wide" id="slsend">SET</button>
      <button class="wide danger" id="slmax">MAX</button>
    </div>
    <div class="echo" id="echo"></div>
  </div>
</div>
<div id="link">CONNECTING TO CONTROLLER&hellip;</div>
<footer>BETHEL &middot; BBSHD REV 1.4 &middot; LAPTOP-AS-DISPLAY &middot; TEST COMMANDS PARKED, WHEEL FREE</footer>
<script>
  const MAX_KPH = 40, ARC = 377;
  let lightsOn = false, lastMsg = 0;

  function post(action, value) {
    fetch('/cmd', {method:'POST', headers:{'Content-Type':'application/json'},
                   body: JSON.stringify({action, value})});
  }

  const arow = document.getElementById('assist');
  for (let i = 0; i <= 9; i++) {
    const b = document.createElement('button');
    b.textContent = i;
    b.onclick = () => {
      post('assist', i);
      [...arow.children].forEach(x => x.classList.remove('on'));
      b.classList.add('on');
    };
    arow.appendChild(b);
  }
  const lights = document.getElementById('lights');
  lights.onclick = () => { lightsOn = !lightsOn; post('lights', lightsOn);
                           lights.classList.toggle('on', lightsOn); };
  const md = document.getElementById('mode-d'), ms = document.getElementById('mode-s');
  md.onclick = () => { post('mode','default'); md.classList.add('on'); ms.classList.remove('on'); };
  ms.onclick = () => { post('mode','sport');  ms.classList.add('on'); md.classList.remove('on'); };
  const sl = document.getElementById('sl'), slv = document.getElementById('slv');
  sl.oninput = () => slv.textContent = sl.value + ' kph';
  document.getElementById('slsend').onclick = () => post('speed_limit', +sl.value);
  document.getElementById('slmax').onclick  = () => { sl.value = 99; slv.textContent = '99 kph';
                                                      post('speed_limit', 99); };

  const es = new EventSource('/events');
  es.onmessage = (e) => {
    const d = JSON.parse(e.data);
    lastMsg = Date.now();
    document.getElementById('mph').textContent = d.mph.toFixed(1);
    document.getElementById('kph').textContent = d.kph.toFixed(1);
    document.getElementById('watts').textContent = d.watts;
    document.getElementById('amps').textContent = d.amps.toFixed(1);
    const b = document.getElementById('battv');
    b.textContent = (d.batt === null ? '--' : d.batt) + '%';
    b.className = d.batt === null ? '' : (d.batt > 50 ? 'good' : d.batt > 20 ? 'mid' : 'low');
    document.getElementById('arc').style.strokeDashoffset = ARC * (1 - Math.min(d.kph / MAX_KPH, 1));
    document.getElementById('status').textContent = d.status.toUpperCase();
    document.getElementById('echo').textContent = d.echo;
    document.body.className = d.status === 'brake' ? 'brake' : '';
    document.getElementById('link').className = d.link ? 'hide' : '';
  };
  setInterval(() => {
    if (Date.now() - lastMsg > 3000) document.getElementById('link').className = '';
  }, 1000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                while True:
                    with LOCK:
                        payload = json.dumps(STATE)
                    self.wfile.write(f"data: {payload}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(0.25)
            except (BrokenPipeError, ConnectionError, OSError):
                return
        else:
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def do_POST(self):
        if self.path != "/cmd":
            self.send_response(404)
            self.end_headers()
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            cmd = json.loads(self.rfile.read(n))
            assert cmd.get("action") in ("assist", "lights", "mode", "speed_limit")
            CMDS.put(cmd)
            body = b'{"ok": true}'
        except Exception:
            body = b'{"ok": false}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    threading.Thread(target=poll_loop, daemon=True).start()
    print(f"Bethel command deck: http://localhost:{HTTP_PORT}")
    ThreadingHTTPServer(("127.0.0.1", HTTP_PORT), Handler).serve_forever()
