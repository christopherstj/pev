#pragma once
#include <Arduino.h>

// Bafang BBSHD display-protocol client (the ESP32 plays the display).
// Same conversation bafang_sniff.py has been having, ported to C++.
// Protocol: 1200 baud 8N1; laptop-verified opcodes in reference/protocol-notes.md.

struct BikeState {
    bool     link      = false;  // controller answering?
    bool     brake     = false;  // status 0x03
    bool     pedaling  = false;  // status 0x01
    uint16_t wheelRpm  = 0;
    float    amps      = 0.0f;
    uint8_t  batteryPct = 0;
    uint32_t lastReplyMs = 0;
};

class BafangClient {
public:
    void begin(HardwareSerial &port, int rxPin, int txPin);

    // Call often; internally rate-limits to one request per interval.
    // Returns true when any field was refreshed.
    bool poll(BikeState &state);

private:
    HardwareSerial *ser = nullptr;
    uint32_t lastPollMs = 0;
    uint8_t  round = 0;       // rotates through status/current/speed/battery
    uint8_t  missCount = 0;

    int  request(const uint8_t *req, size_t reqLen, uint8_t *resp, size_t respLen);
    bool readStatus(BikeState &s);
    bool readCurrent(BikeState &s);
    bool readSpeed(BikeState &s);
    bool readBattery(BikeState &s);
};
