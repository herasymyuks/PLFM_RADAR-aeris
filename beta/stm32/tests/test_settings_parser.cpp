// Host-side unit test: USB start-flag / settings-packet parser (USBHandler + RadarSettings).
// Builds with the system C++ compiler, no HAL needed. Run via tests/run_tests.sh.
//
// Protocol under test (9_Firmware/9_3_GUI/GUI_V5.py:401-468, LIB/RadarSettings.cpp:23-78):
//   start flag  = [23, 46, 158, 237]
//   settings    = "SET" + 3 x double + uint32 + 6 x double + "END" = 82 bytes, big-endian
//   GUI framing = every chunk zero-padded to 64 bytes  (GUI_V5.py:444-446)
#include "../LIB/USBHandler.h"
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <vector>
#include <cmath>

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { std::printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

static void put_be_double(std::vector<uint8_t>& v, double d) {
    uint64_t bits; std::memcpy(&bits, &d, 8);
    for (int i = 7; i >= 0; i--) v.push_back((uint8_t)(bits >> (8 * i)));
}
static void put_be_u32(std::vector<uint8_t>& v, uint32_t u) {
    for (int i = 3; i >= 0; i--) v.push_back((uint8_t)(u >> (8 * i)));
}

struct Params { double f, t1, t2; uint32_t n; double fmin, fmax, prf1, prf2, dmax, map; };
static const Params kValid = { 10.5e9, 30e-6, 0.5e-6, 32, 10e6, 30e6, 6000.0, 5700.0, 50000.0, 50000.0 };

static std::vector<uint8_t> settings_packet(const Params& p) {
    std::vector<uint8_t> v = {'S', 'E', 'T'};
    put_be_double(v, p.f); put_be_double(v, p.t1); put_be_double(v, p.t2);
    put_be_u32(v, p.n);
    put_be_double(v, p.fmin); put_be_double(v, p.fmax); put_be_double(v, p.prf1);
    put_be_double(v, p.prf2); put_be_double(v, p.dmax); put_be_double(v, p.map);
    v.push_back('E'); v.push_back('N'); v.push_back('D');
    return v;
}

// Emulates GUI_V5.py _send_data(): split into 64-byte chunks, zero-pad the last one.
static void send_padded(USBHandler& h, const std::vector<uint8_t>& data) {
    for (size_t i = 0; i < data.size(); i += 64) {
        std::vector<uint8_t> chunk(data.begin() + i, data.begin() + std::min(data.size(), i + 64));
        chunk.resize(64, 0);
        h.processUSBData(chunk.data(), (uint32_t)chunk.size());
    }
}

static bool settings_match(const RadarSettings& s, const Params& p) {
    return s.getSystemFrequency() == p.f && s.getChirpDuration1() == p.t1 && s.getChirpDuration2() == p.t2 &&
           s.getChirpsPerPosition() == p.n && s.getFreqMin() == p.fmin && s.getFreqMax() == p.fmax &&
           s.getPRF1() == p.prf1 && s.getPRF2() == p.prf2 && s.getMaxDistance() == p.dmax && s.getMapSize() == p.map;
}

int main() {
    const uint8_t FLAG[4] = {23, 46, 158, 237};
    std::vector<uint8_t> pkt = settings_packet(kValid);
    CHECK(pkt.size() == 82);

    std::printf("T1 unpadded: flag (4 B) then settings (82 B) as two writes\n");
    { USBHandler h;
      h.processUSBData(FLAG, 4);
      CHECK(h.isStartFlagReceived());
      CHECK(h.getState() == USBHandler::USBState::RECEIVING_SETTINGS);
      h.processUSBData(pkt.data(), (uint32_t)pkt.size());
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA);
      CHECK(settings_match(h.getSettings(), kValid)); }

    std::printf("T2 GUI framing: 64-B zero-padded flag frame, then 64 + 64(padded) settings frames\n");
    { USBHandler h;
      send_padded(h, std::vector<uint8_t>(FLAG, FLAG + 4));
      CHECK(h.isStartFlagReceived());
      send_padded(h, pkt);
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA);
      CHECK(settings_match(h.getSettings(), kValid)); }

    std::printf("T3 flag and settings concatenated in one write\n");
    { USBHandler h;
      std::vector<uint8_t> all(FLAG, FLAG + 4); all.insert(all.end(), pkt.begin(), pkt.end());
      h.processUSBData(all.data(), (uint32_t)all.size());
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA);
      CHECK(settings_match(h.getSettings(), kValid)); }

    std::printf("T4 'SET' marker straddling a packet boundary ('S','E' | 'T',...)\n");
    { USBHandler h;
      h.processUSBData(FLAG, 4);
      std::vector<uint8_t> a = {0, 0, 0, 'S', 'E'};
      std::vector<uint8_t> b(pkt.begin() + 2, pkt.end());
      h.processUSBData(a.data(), (uint32_t)a.size());
      h.processUSBData(b.data(), (uint32_t)b.size());
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA);
      CHECK(settings_match(h.getSettings(), kValid)); }

    std::printf("T5 byte-at-a-time delivery\n");
    { USBHandler h;
      for (uint8_t c : FLAG) h.processUSBData(&c, 1);   // flag never arrives in a single packet ...
      CHECK(!h.isStartFlagReceived());                   // ... documented limitation: flag must be in one packet
      h.processUSBData(FLAG, 4);
      for (uint8_t c : pkt) h.processUSBData(&c, 1);
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA); }

    std::printf("T6 short packets (< 4 B) before the flag must not crash or trigger\n");
    { USBHandler h; uint8_t one = 23; uint8_t three[3] = {23, 46, 158};
      h.processUSBData(&one, 1); h.processUSBData(three, 3);
      CHECK(!h.isStartFlagReceived()); }

    std::printf("T7 invalid values are rejected and a later valid packet is accepted\n");
    { USBHandler h; Params bad = kValid; bad.prf1 = 50.0;   // below the 100 Hz validateSettings() limit
      send_padded(h, std::vector<uint8_t>(FLAG, FLAG + 4));
      send_padded(h, settings_packet(bad));
      CHECK(h.getState() == USBHandler::USBState::RECEIVING_SETTINGS);
      CHECK(!h.getSettings().isValid());
      send_padded(h, pkt);
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA);
      CHECK(settings_match(h.getSettings(), kValid)); }

    std::printf("T8 RadarSettings::parseFromUSB rejects wrong markers / short input\n");
    { RadarSettings s;
      CHECK(!s.parseFromUSB(pkt.data(), 73));
      std::vector<uint8_t> q = pkt; q[0] = 'X';
      CHECK(!s.parseFromUSB(q.data(), (uint32_t)q.size()));
      q = pkt; q[81] = 'X';
      CHECK(!s.parseFromUSB(q.data(), (uint32_t)q.size()));
      CHECK(s.parseFromUSB(pkt.data(), (uint32_t)pkt.size()));
      CHECK(settings_match(s, kValid)); }

    std::printf("T9 big-endian decode against a hand-encoded constant (1.0 = 0x3FF0000000000000)\n");
    { Params p = kValid; p.map = 1.0e3; // map_size lower limit is 1000 -> use 1000.0? keep 1.0 check separately
      std::vector<uint8_t> v = settings_packet(p);
      // the last double (map_size) sits at offset 71..78
      const uint8_t one_kib[8] = {0x40, 0x8F, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00}; // 1000.0
      CHECK(std::memcmp(v.data() + 71, one_kib, 8) == 0);
      RadarSettings s; CHECK(s.parseFromUSB(v.data(), (uint32_t)v.size())); CHECK(s.getMapSize() == 1000.0); }

    std::printf("T10 ASCII 'REG' command branch does not disturb the binary settings path\n");
    { USBHandler h; char buf[80];
      const char* c1 = "REG R 0x5\r\n";
      h.processUSBData((const uint8_t*)c1, (uint32_t)std::strlen(c1));          // before the start flag
      CHECK(h.hasPendingCommand()); CHECK(!h.isStartFlagReceived());
      CHECK(h.takePendingCommand(buf, sizeof buf)); CHECK(std::strcmp(buf, "REG R 0x5") == 0);
      CHECK(!h.hasPendingCommand());
      send_padded(h, std::vector<uint8_t>(FLAG, FLAG + 4));
      // a settings packet whose 2nd 64-byte chunk starts with "REG": must stay binary
      std::vector<uint8_t> p2 = pkt; p2[64] = 'R'; p2[65] = 'E'; p2[66] = 'G';
      send_padded(h, p2);
      CHECK(!h.hasPendingCommand());
      send_padded(h, pkt);
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA);
      const char* c2 = "REG W 0 7";
      h.processUSBData((const uint8_t*)c2, (uint32_t)std::strlen(c2));          // after settings
      CHECK(h.takePendingCommand(buf, sizeof buf)); CHECK(std::strcmp(buf, "REG W 0 7") == 0);
      CHECK(h.getState() == USBHandler::USBState::READY_FOR_DATA); }

    std::printf("%s (%d failure(s))\n", failures ? "TEST FAILED" : "TEST PASSED", failures);
    return failures ? 1 : 0;
}
