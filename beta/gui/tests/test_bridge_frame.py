"""Option-B bridge frame: RTL-testbench vector, round trip, corruption, stream resync."""
import pathlib
import pytest
from aeris10_gui.protocol.bridge_frame import (BridgeFrame, BridgeStreamParser, FrameError, build_frame, crc16_ccitt_false, parse_frame)

VEC = pathlib.Path(__file__).parent / "vectors" / "bridge_frame_from_rtl_tb.hex"


def rtl_frame() -> bytes:
    return bytes.fromhex(VEC.read_text().strip())


def test_crc_reference():
    assert crc16_ccitt_false(b"123456789") == 0x29B1


def test_rtl_vector_parses():
    f = parse_frame(rtl_frame())
    assert (f.version, f.azimuth, f.elevation, f.chirp_count, f.n_range, f.n_doppler) == (1, 7, 16, 1234, 64, 32)
    assert f.long_chirp and not f.overflow
    assert f.detections == [(100 // 32, 100 % 32, f.magnitude[100]), (777 // 32, 777 % 32, f.magnitude[777]), (2047 // 32, 2047 % 32, f.magnitude[2047])]
    # the testbench pattern: |I|+|Q| with I = (n*37)&0x7FFF, Q = (n*11)&0x3FFF → 8*log2 with 3 fractional bits
    for n in (0, 1, 2, 5, 100, 777, 2047):
        m = ((n * 37) & 0x7FFF) + ((n * 11) & 0x3FFF)
        if m == 0:
            exp = 0
        else:
            msb = m.bit_length() - 1
            frac = (m >> (msb - 3)) & 7 if msb >= 3 else (m << (3 - msb)) & 7
            exp = (msb << 3) | frac
        assert f.magnitude[n] == exp, n


def test_round_trip_and_map():
    f = parse_frame(rtl_frame())
    assert build_frame(f) == rtl_frame()
    assert len(f.map2d()) == 64 and len(f.map2d()[0]) == 32


@pytest.mark.parametrize("pos", [0, 3, 500, 2074])
def test_corruption_detected(pos):
    b = bytearray(rtl_frame()); b[pos] ^= 0x40
    with pytest.raises(FrameError):
        parse_frame(bytes(b))


def test_truncated():
    with pytest.raises(FrameError):
        parse_frame(rtl_frame()[:-10])


def test_stream_resync_with_status_text():
    texts = []
    p = BridgeStreamParser(text_sink=texts.append)
    fr = rtl_frame()
    stream = b"BeamPos:3|Azimuth:7|ChirpCount:1234|" + fr + b"\xa5\x5a\x01garbage" + fr[:1000] + b"GPS:1,2,3|" + fr
    out = []
    for i in range(0, len(stream), 61):
        out.extend(p.feed(stream[i:i + 61]))
    assert len(out) == 2 and all(o.seq == out[0].seq for o in out)
    assert p.resyncs >= 1
    assert b"BeamPos:3" in b"".join(texts)
