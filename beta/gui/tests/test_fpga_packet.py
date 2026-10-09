"""FPGA packet: vectors derived by hand from usb_data_interface.v, parser robustness."""
import pytest

from aeris10_gui.protocol import fpga_packet as fp


def test_word_sequence_matches_rtl_case_statements():
    # range_profile = 0x11223344, doppler_real = 0x0A0B, doppler_imag = 0x0C0D, detection = 1
    words = fp.encode_words(0x11223344, 0x0A0B, 0x0C0D, True)
    assert len(words) == fp.WORDS_PER_PACKET == 11
    assert (words[0].value, words[0].byte_enable) == (0xAA, 0b01)                 # SEND_HEADER
    assert [w.value for w in words[1:5]] == [0x11223344, 0x22334400, 0x33440000, 0x44000000]  # SEND_RANGE_DATA 0..3
    assert all(w.byte_enable == 0b11 for w in words[1:9])
    # SEND_DOPPLER_DATA: {re,im}, {im, re[15:8], 0}, {re[7:0], im[15:8], 0}, {im[7:0], 0}
    assert [w.value for w in words[5:9]] == [0x0A0B0C0D, 0x0C0D0A00, 0x0B0C0000, 0x0D000000]
    assert (words[9].value, words[9].byte_enable) == (1, 0b01)                    # SEND_DETECTION_DATA
    assert (words[10].value, words[10].byte_enable) == (0x55, 0b01)               # SEND_FOOTER


def test_byte_stream_vector():
    pkt = fp.encode_packet(0x11223344, 0x0A0B, 0x0C0D, True)
    assert len(pkt) == fp.PACKET_LENGTH == 35
    expected = bytes.fromhex(
        "aa"
        "44332211" "00443322" "00004433" "00000044"     # range words, little-endian lanes
        "0d0c0b0a" "000a0d0c" "00000c0b" "0000000d"     # doppler words
        "01" "55")
    assert pkt == expected


def test_decode_round_trip_signed_values():
    for re, im, det in [(-1, 1, False), (-32768, 32767, True), (12345, -12345, False), (0, 0, False)]:
        p = fp.decode_packet(fp.encode_packet(0xDEADBEEF, re, im, det))
        assert (p.doppler_real, p.doppler_imag, p.detection, p.range_word) == (re, im, det, 0xDEADBEEF)


def test_encode_cell_top_level_wiring():
    """radar_system_top.v:294-331 -- range word is {Q, I}, real = I, imag = Q."""
    p = fp.decode_packet(fp.encode_cell(-5, 7, False), check_top_level_consistency=True)
    assert (p.range_i, p.range_q) == (-5, 7)
    assert (p.doppler_real, p.doppler_imag) == (-5, 7)
    with pytest.raises(fp.PacketError) as ei:
        fp.decode_packet(fp.encode_packet(0x12345678, 1, 2, False), check_top_level_consistency=True)
    assert ei.value.reason == "inconsistent_range_word"


def test_decode_words_from_bus_capture():
    words = fp.encode_words(0x01020304, 100, -100, True)
    p = fp.decode_words(words)
    assert (p.range_word, p.doppler_real, p.doppler_imag, p.detection) == (0x01020304, 100, -100, True)


@pytest.mark.parametrize("corrupt_index,reason", [
    (34, "bad_footer"),
    (6, "bad_range_redundancy"),      # second range copy
    (22, "bad_doppler_redundancy"),   # second doppler copy
    (33, "bad_detection_byte"),
])
def test_corruption_detected(corrupt_index, reason):
    pkt = bytearray(fp.encode_packet(0x11223344, 0x0A0B, 0x0C0D, True))
    pkt[corrupt_index] ^= 0x5A
    with pytest.raises(fp.PacketError) as ei:
        fp.decode_packet(bytes(pkt))
    assert ei.value.reason == reason


def test_truncated():
    pkt = fp.encode_packet(1, 2, 3, False)
    with pytest.raises(fp.PacketError) as ei:
        fp.decode_packet(pkt[:20])
    assert ei.value.reason == "truncated"


def test_stream_parser_resync_and_fragmentation():
    good = [fp.encode_packet(i, i, -i, bool(i % 2)) for i in range(1, 6)]
    stream = b"\x00\x13\xaa\x01" + good[0] + good[1][:17]          # garbage + false header + split packet
    parser = fp.FpgaPacketParser()
    out = parser.feed(stream)
    assert [p.range_word for p in out] == [1]
    out = parser.feed(good[1][17:] + good[2] + b"\xaa\x55\x55" + good[3] + good[4])
    assert [p.range_word for p in out] == [2, 3, 4, 5]
    assert parser.stats["packets"] == 5
    assert parser.stats["resync_bytes_dropped"] > 0
    assert parser.pending == 0


def test_stream_parser_corrupt_packet_skipped_then_recovers():
    a = fp.encode_packet(7, 7, 7, False)
    bad = bytearray(a)
    bad[34] = 0x00                                                # footer destroyed
    parser = fp.FpgaPacketParser()
    out = parser.feed(bytes(bad) + a)
    assert len(out) == 1 and out[0].range_word == 7
    assert parser.stats["bad_footer"] >= 1
