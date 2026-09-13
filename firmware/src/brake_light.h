#pragma once
#include "bafang.h"

// Rear strip behavior:
//   no link/sim yet -> single dim amber "heartbeat" pixel (alive, no data)
//   riding          -> dim red tail light
//   brake ON        -> 3 fast full-red flashes, then solid full red
//   brake released  -> back to tail
class BrakeLight {
public:
    void begin();
    void update(const BikeState &state);

private:
    bool     wasBraking = false;
    uint32_t brakeStartMs = 0;
};
