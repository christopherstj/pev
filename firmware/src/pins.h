#pragma once

// ESP32-S3 DevKitC pin assignments.
// UART1 talks to Bethel's display line THROUGH the level shifting:
//   - bike TX (5V) -> voltage divider (e.g. 2k2 over 3k3) -> BAFANG_RX
//   - BAFANG_TX (3.3V) -> straight to bike RX (controller input reads 3.3V fine;
//     if flaky on the bike, route through a spare 74AHCT125 channel)
// LED data goes THROUGH the 74AHCT125 (3.3V -> 5V) to the WS2812 strip.

constexpr int BAFANG_RX = 18;   // from bike TX, via divider
constexpr int BAFANG_TX = 17;   // to bike RX
constexpr int LED_DATA  = 4;    // to AHCT125 input; its output feeds the strip

constexpr int NUM_LEDS  = 30;

// Global brightness ceiling (0-255). Desk mode runs off USB power:
// 30 red LEDs at 96/255 is well inside a USB port's budget.
constexpr uint8_t MAX_BRIGHTNESS = 96;
