#include "bafang.h"

namespace {
constexpr uint32_t POLL_INTERVAL_MS = 120;   // 1200 baud needs breathing room
constexpr uint32_t RESP_TIMEOUT_MS  = 200;
constexpr uint8_t  OFFLINE_AFTER_MISSES = 12;
}

void BafangClient::begin(HardwareSerial &port, int rxPin, int txPin) {
    ser = &port;
    ser->begin(1200, SERIAL_8N1, rxPin, txPin);
}

// Send a read request, collect exactly respLen bytes (or time out).
// Returns bytes received.
int BafangClient::request(const uint8_t *req, size_t reqLen, uint8_t *resp, size_t respLen) {
    while (ser->available()) ser->read();   // drain stale bytes
    ser->write(req, reqLen);
    ser->flush();

    size_t got = 0;
    uint32_t start = millis();
    while (got < respLen && millis() - start < RESP_TIMEOUT_MS) {
        if (ser->available()) {
            resp[got++] = ser->read();
        }
    }
    return got;
}

bool BafangClient::readStatus(BikeState &s) {
    const uint8_t req[] = {0x11, 0x08};
    uint8_t r[1];
    if (request(req, sizeof(req), r, 1) != 1) return false;
    s.brake    = (r[0] == 0x03);
    s.pedaling = (r[0] == 0x01);
    return true;
}

bool BafangClient::readCurrent(BikeState &s) {
    const uint8_t req[] = {0x11, 0x0A};
    uint8_t r[2];
    if (request(req, sizeof(req), r, 2) != 2) return false;
    if (r[0] != r[1]) return false;         // checksum: value doubled
    s.amps = r[0] / 2.0f;
    return true;
}

bool BafangClient::readSpeed(BikeState &s) {
    const uint8_t req[] = {0x11, 0x20};
    uint8_t r[3];
    if (request(req, sizeof(req), r, 3) != 3) return false;
    if (((r[0] + r[1] + 0x20) & 0xFF) != r[2]) return false;  // the "weird checksum"
    s.wheelRpm = (uint16_t(r[0]) << 8) | r[1];
    return true;
}

bool BafangClient::readBattery(BikeState &s) {
    const uint8_t req[] = {0x11, 0x11};
    uint8_t r[2];
    if (request(req, sizeof(req), r, 2) != 2) return false;
    if (r[0] != r[1]) return false;
    s.batteryPct = r[0];
    return true;
}

bool BafangClient::poll(BikeState &state) {
    if (!ser) return false;
    uint32_t now = millis();
    if (now - lastPollMs < POLL_INTERVAL_MS) return false;
    lastPollMs = now;

    bool ok = false;
    switch (round++ & 0x03) {
        case 0: ok = readStatus(state);  break;   // brake is the money read —
        case 1: ok = readStatus(state);  break;   // poll it twice as often
        case 2: ok = readSpeed(state);   break;
        case 3: ok = (round & 0x08) ? readBattery(state) : readCurrent(state); break;
    }

    if (ok) {
        state.lastReplyMs = now;
        state.link = true;
        missCount = 0;
    } else if (++missCount >= OFFLINE_AFTER_MISSES) {
        state.link = false;
    }
    return ok;
}
