"""Settings packet: byte-exact vector, round trip, firmware receiver model, padding issue."""
import struct

import pytest

from aeris10_gui.model import RadarSettings
from aeris10_gui.protocol import settings_packet as sp

# Firmware defaults (RadarSettings.cpp:8-20) serialised with the fixed layout of
# RadarSettings.cpp:40-73 -- computed independently with struct, hex frozen here.
FIRMWARE_DEFAULT_VECTOR = bytes.fromhex(
    "534554"                      # "SET"
    "4202a05f20000000"            # system_frequency 10e9      >d
    "3eff75104d551d69"            # chirp_duration_1 30e-6     >d
    "3ea0c6f7a0b5ed8d"            # chirp_duration_2 0.5e-6    >d
    "00000020"                    # chirps_per_position 32     >I
    "416312d000000000"            # freq_min 10e6              >d
    "417c9c3800000000"            # freq_max 30e6              >d
    "408f400000000000"            # prf1 1000                  >d
    "409f400000000000"            # prf2 2000                  >d
    "40e86a0000000000"            # max_distance 50000         >d
    "40e86a0000000000"            # map_size 50000             >d
    "454e44"                      # "END"
)


def test_vector_length_and_markers():
    assert len(FIRMWARE_DEFAULT_VECTOR) == sp.PACKET_LENGTH == 82
    assert FIRMWARE_DEFAULT_VECTOR[:3] == b"SET" and FIRMWARE_DEFAULT_VECTOR[-3:] == b"END"


def test_build_matches_firmware_vector():
    assert sp.build_settings_packet(RadarSettings()) == FIRMWARE_DEFAULT_VECTOR


def test_field_offsets_match_firmware():
    # RadarSettings.cpp offsets: 3, 11, 19, 27(uint32), 31, 39, 47, 55, 63, 71
    pkt = FIRMWARE_DEFAULT_VECTOR
    assert struct.unpack(">d", pkt[3:11])[0] == 10e9
    assert struct.unpack(">d", pkt[11:19])[0] == 30e-6
    assert struct.unpack(">d", pkt[19:27])[0] == 0.5e-6
    assert struct.unpack(">I", pkt[27:31])[0] == 32
    assert struct.unpack(">d", pkt[31:39])[0] == 10e6
    assert struct.unpack(">d", pkt[39:47])[0] == 30e6
    assert struct.unpack(">d", pkt[47:55])[0] == 1000.0
    assert struct.unpack(">d", pkt[55:63])[0] == 2000.0
    assert struct.unpack(">d", pkt[63:71])[0] == 50000.0
    assert struct.unpack(">d", pkt[71:79])[0] == 50000.0


def test_round_trip_non_default():
    s = RadarSettings(system_frequency=9.5e9, chirp_duration_1=40e-6, chirp_duration_2=1e-6,
                      chirps_per_position=64, freq_min=12e6, freq_max=28e6, prf1=1500, prf2=2500,
                      max_distance=20000, map_size=30000)
    assert sp.parse_settings_packet(sp.build_settings_packet(s)) == s
    assert sp.validate_settings(s) == []


def test_parse_rejects_bad_markers_and_short():
    with pytest.raises(sp.SettingsPacketError):
        sp.parse_settings_packet(b"XET" + FIRMWARE_DEFAULT_VECTOR[3:])
    with pytest.raises(sp.SettingsPacketError):
        sp.parse_settings_packet(FIRMWARE_DEFAULT_VECTOR[:-3] + b"XXX")
    with pytest.raises(sp.SettingsPacketError):
        sp.parse_settings_packet(FIRMWARE_DEFAULT_VECTOR[:70])


def test_validate_mirrors_firmware_ranges():
    bad = RadarSettings(prf1=50, freq_max=5e6)
    problems = sp.validate_settings(bad)
    assert any("prf1" in p for p in problems)
    assert any("freq_max" in p for p in problems)
    assert sp.validate_settings(RadarSettings()) == []


def test_firmware_model_accepts_unpadded_sequence():
    writes = sp.build_start_sequence(RadarSettings(), pad_to_64=False)
    assert writes[0] == sp.START_FLAG
    assert b"".join(writes[1:]) == FIRMWARE_DEFAULT_VECTOR
    state, settings = sp.simulate_firmware_receiver(writes)
    assert state == "READY_FOR_DATA"
    assert settings == RadarSettings()


def test_firmware_model_accepts_flag_and_packet_in_one_transfer():
    state, settings = sp.simulate_firmware_receiver([sp.START_FLAG + FIRMWARE_DEFAULT_VECTOR])
    assert state == "READY_FOR_DATA" and settings == RadarSettings()


def test_firmware_model_accepts_usb_fs_fragmentation():
    """82 bytes arrive as a 64-byte and an 18-byte CDC transfer."""
    writes = [sp.START_FLAG, FIRMWARE_DEFAULT_VECTOR[:64], FIRMWARE_DEFAULT_VECTOR[64:]]
    state, settings = sp.simulate_firmware_receiver(writes)
    assert state == "READY_FOR_DATA" and settings == RadarSettings()


def test_firmware_model_rejects_v5_zero_padding():
    """Reproduces docs/GUI/DEPENDENCIES.md section 6 item 2: V5 padding breaks the firmware."""
    writes = sp.build_start_sequence(RadarSettings(), pad_to_64=True)
    assert all(len(w) == 64 for w in writes)
    state, settings = sp.simulate_firmware_receiver(writes)
    assert state == "RECEIVING_SETTINGS"
    assert settings is None


def test_frame_for_transmission_default_unpadded():
    chunks = sp.frame_for_transmission(FIRMWARE_DEFAULT_VECTOR)
    assert [len(c) for c in chunks] == [64, 18]
    assert b"".join(chunks) == FIRMWARE_DEFAULT_VECTOR
