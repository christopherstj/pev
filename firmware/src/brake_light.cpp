#include "brake_light.h"
#include "pins.h"
#include <FastLED.h>

namespace {
CRGB leds[NUM_LEDS];
constexpr uint8_t TAIL_BRIGHTNESS = 40;    // dim red cruise
constexpr uint32_t FLASH_PERIOD_MS = 80;   // attention-grabbing onset flashes
constexpr uint32_t FLASH_COUNT = 3;
}

void BrakeLight::begin() {
    FastLED.addLeds<WS2812B, LED_DATA, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.clear(true);
}

void BrakeLight::update(const BikeState &s) {
    uint32_t now = millis();

    if (!s.link) {
        // heartbeat: one amber pixel breathing so you know the brain is alive
        FastLED.clear();
        uint8_t pulse = beatsin8(30, 10, 120);
        leds[0] = CRGB(pulse, pulse / 3, 0);
        FastLED.show();
        return;
    }

    if (s.brake && !wasBraking) brakeStartMs = now;   // rising edge
    wasBraking = s.brake;

    if (s.brake) {
        uint32_t elapsed = now - brakeStartMs;
        bool inFlashWindow = elapsed < FLASH_COUNT * 2 * FLASH_PERIOD_MS;
        bool flashOff = inFlashWindow && ((elapsed / FLASH_PERIOD_MS) & 1);
        CRGB color = flashOff ? CRGB::Black : CRGB::Red;
        fill_solid(leds, NUM_LEDS, color);
    } else {
        fill_solid(leds, NUM_LEDS, CRGB(TAIL_BRIGHTNESS, 0, 0));
    }
    FastLED.show();
}
