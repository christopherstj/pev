// Bethel body controller — stage 1: brake light.
// Real mode:  polls the bike over UART1 (through the level shifting).
// Desk mode:  automatic fallback — if the bike never answers, drive the
//             state from the USB serial console instead:
//               b = toggle brake     0-9 = speed (as tenths of max)
//               p = toggle pedaling  +/- = battery up/down
// Desk mode is how the brake light works on a desk with no bicycle involved.

#include <Arduino.h>
#include "pins.h"
#include "bafang.h"
#include "brake_light.h"
#include <string.h>   // strcmp (Arduino.h happens to pull it in; do not rely on that)

// Build identity. `bench build` generates out/bench/bench_version.h and passes
// -Iout/bench; a bare `pio run` has no such file and reports "unknown" on purpose.
#if __has_include("bench_version.h")
#  include "bench_version.h"
#endif
#ifndef BENCH_GIT_SHA
#  define BENCH_GIT_SHA "unknown"
#endif
#ifndef BENCH_DIRTY
#  define BENCH_DIRTY -1
#endif
#ifndef BENCH_BUILT_AT
#  define BENCH_BUILT_AT "unknown"
#endif
#ifndef BENCH_PROJECT
#  define BENCH_PROJECT "bethel-body"
#endif
#ifndef BENCH_ENV
#  define BENCH_ENV "esp32-s3-devkitc-1"
#endif
#define BENCH_STR_(x) #x
#define BENCH_STR(x) BENCH_STR_(x)
// One literal in flash, so the .bin itself carries the answer:
static const char BENCH_VER_LINE[] =
    "ver sha=" BENCH_GIT_SHA " dirty=" BENCH_STR(BENCH_DIRTY)
    " built=" BENCH_BUILT_AT " proj=" BENCH_PROJECT " env=" BENCH_ENV;

BafangClient bafang;
BrakeLight  light;
BikeState   state;

bool simMode = false;
uint32_t bootMs = 0;

static void handleSimKeys() {
    while (Serial.available()) {
        char c = Serial.read();
        if (!simMode && (c == 'b' || c == 'p' || (c >= '0' && c <= '9'))) {
            simMode = true;               // first sim key switches us over
            state.link = true;
            Serial.println("[sim] desk mode active — I believe in a bicycle I cannot see");
        }
        // Line reader for the host-side "?ver" query. It sits above the
        // `!simMode` bail-out so it answers in bike mode too. None of '?','v',
        // 'e','r' is a sim trigger, so asking the version can't flip desk mode
        // on; and a sim key typed with no newline just idles in this buffer.
        static char verBuf[16];
        static uint8_t verLen = 0;
        static bool verTooLong = false;      // line overran the buffer: ignore it
        if (c == '\r' || c == '\n') {
            if (!verTooLong) {
                verBuf[verLen] = '\0';
                if (strcmp(verBuf, "?ver") == 0) Serial.println(BENCH_VER_LINE);
            }
            verLen = 0;
            verTooLong = false;
        } else if (verLen < sizeof(verBuf) - 1) {
            verBuf[verLen++] = c;
        } else {
            verTooLong = true;               // too long to be "?ver"; drop to end of line
        }

        if (!simMode) continue;
        switch (c) {
            case 'b': state.brake = !state.brake;
                      Serial.printf("[sim] brake %s\n", state.brake ? "ON" : "off");
                      break;
            case 'p': state.pedaling = !state.pedaling;
                      Serial.printf("[sim] pedaling %s\n", state.pedaling ? "ON" : "off");
                      break;
            case '+': state.batteryPct = min(100, state.batteryPct + 10); break;
            case '-': state.batteryPct = (state.batteryPct >= 10) ? state.batteryPct - 10 : 0; break;
            default:
                if (c >= '0' && c <= '9') state.wheelRpm = (c - '0') * 40;
        }
    }
}

void setup() {
    Serial.begin(115200);
    bootMs = millis();
    light.begin();
    bafang.begin(Serial1, BAFANG_RX, BAFANG_TX);
    Serial.println("Bethel body controller up. Keys: b=brake p=pedal 0-9=speed +/-=battery");
    Serial.println(BENCH_VER_LINE);
}

void loop() {
    handleSimKeys();

    if (!simMode) {
        bafang.poll(state);
    }

    light.update(state);

    // once per second, say what we believe
    static uint32_t lastLog = 0;
    if (millis() - lastLog > 1000) {
        lastLog = millis();
        Serial.printf("[%s] link=%d brake=%d rpm=%u amps=%.1f batt=%u%%\n",
                      simMode ? "sim" : "bike", state.link, state.brake,
                      state.wheelRpm, state.amps, state.batteryPct);
    }
}
