# Bethel body controller — firmware

Stage 1: brake light. The ESP32-S3 plays the Bafang display, polls brake
status over the display UART, and drives a WS2812 strip.

## Build & flash (once the board arrives)

Install [PlatformIO](https://platformio.org/) (VS Code extension, or `pip install platformio`), then from this folder:

```
pio run -t upload
pio device monitor
```

Plug the USB-C cable into the port labeled **COM/UART** if the board has two.

## Desk mode (no bike, no strip wiring beyond the breadboard)

Flash it, open the monitor, press keys:

- `b` — toggle brake (strip does 3 fast flashes then solid red)
- `0-9` — fake speed
- `p` — toggle pedaling, `+`/`-` — battery

The firmware auto-detects: silence on the bike UART + a sim key = desk mode.
On the bike it ignores the keyboard and believes the bicycle.

## Breadboard wiring (stage 1, USB powered)

```
ESP32-S3 5V pin ──────────────┬── AHCT125 VCC (pin 14)
                              └── strip 5V   (plus 1000uF cap across strip 5V/GND)
ESP32-S3 GND ─────────────────┴── AHCT125 GND (pin 7) ── strip GND
GPIO4 ── AHCT125 1A (pin 2)   AHCT125 1Y (pin 3) ── 470R ── strip DIN
AHCT125 1OE (pin 1) ── GND    (enable is active-low: ground it)
```

## Stage 2 additions (bike)

- DROK buck: bike 52V (Higo power pin, fused) -> 5V feed replaces USB
- Bike TX (5V) -> divider (2k2/3k3) -> GPIO18; GPIO17 -> bike RX
- Measure the Higo power pin with the multimeter BEFORE connecting anything.

Protocol reference: `../reference/protocol-notes.md`. Pin map: `src/pins.h`.
