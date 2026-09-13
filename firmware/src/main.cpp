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
