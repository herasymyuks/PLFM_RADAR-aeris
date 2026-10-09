import math

import pytest

from aeris10_gui.model import GPSData, SystemStatus
from aeris10_gui.protocol import status_text as st

# Reproduction of main.cpp:807-877 output with PowerAmplifier == 0
FIRMWARE_STATUS = ("System Status: NORMAL|LastError:0|ErrorCount:0|IMU:1.5,-0.5,0.0|GPS:41.902800,12.496400|ALT:50.0|"
                   "LO_TX:LOCKED|LO_RX:UNLOCKED|T1:35.0|T2:36.0|T3:37.0|T4:38.0|T5:39.0|T6:40.0|T7:41.0|T8:42.0|"
                   "BeamPos:3|Azimuth:17|ChirpCount:96|")


def test_parse_status_fields():
    s = st.parse_status_line(FIRMWARE_STATUS)
    assert s.mode == "NORMAL"
    assert (s.last_error, s.error_count) == (0, 0)
    assert (s.imu_pitch, s.imu_roll, s.imu_yaw) == (1.5, -0.5, 0.0)
    assert (s.gps_latitude, s.gps_longitude, s.altitude) == (41.9028, 12.4964, 50.0)
    assert (s.lo_tx_locked, s.lo_rx_locked) == (True, False)
    assert s.temperatures == [35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0]
    assert (s.beam_pos, s.azimuth, s.chirp_count) == (3, 17, 96)
    assert s.pa_avg_current is None and s.unknown_fields == {}


def test_format_matches_firmware_snprintf():
    out = st.format_status_line(imu=(1.5, -0.5, 0.0), gps=(41.9028, 12.4964), altitude=50.0,
                                lo_rx_locked=False, temperatures=tuple(35.0 + i for i in range(8)),
                                beam_pos=3, azimuth=17, chirp_count=96)
    assert out == FIRMWARE_STATUS


def test_pa_block_and_emergency():
    line = st.format_status_line(mode="EMERGENCY_STOP", pa_avg_current=1.25, pa_enabled=1)
    s = st.parse_status_line(line)
    assert s.mode == "EMERGENCY_STOP" and s.pa_avg_current == 1.25 and s.pa_enabled == 1


def test_gps_text_three_fields_firmware_and_four_legacy():
    g = st.parse_gps_text("GPS:41.90280000,12.49640000,50.00\r\n", timestamp=1.0)
    assert (g.latitude, g.longitude, g.altitude, g.pitch) == (41.9028, 12.4964, 50.0, 0.0)
    g4 = st.parse_gps_text("GPS:1,2,3,4.5", timestamp=1.0)
    assert g4.pitch == 4.5
    with pytest.raises(ValueError):
        st.parse_gps_text("GPS:1,2")


def test_gpsb_round_trip_and_checksum():
    frame = st.encode_gpsb(41.9028, 12.4964, 50.0, -2.5)
    assert len(frame) == 30 and frame[:4] == b"GPSB"
    g = st.parse_gpsb(frame, timestamp=0.0)
    assert math.isclose(g.latitude, 41.9028) and math.isclose(g.longitude, 12.4964)
    assert math.isclose(g.altitude, 50.0, rel_tol=1e-6) and math.isclose(g.pitch, -2.5, rel_tol=1e-6)
    bad = bytearray(frame)
    bad[10] ^= 1
    with pytest.raises(ValueError, match="checksum"):
        st.parse_gpsb(bytes(bad))


def test_stream_parser_mixed_unterminated_status_and_binary():
    p = st.StatusStreamParser()
    data = FIRMWARE_STATUS.encode() + st.encode_gpsb(1.0, 2.0, 3.0, 4.0) + b"GPS:5,6,7\r\n" + b"System Status: NORMAL|LastError:1|"
    msgs = p.feed(data[:40])          # fragment
    assert msgs == []
    msgs += p.feed(data[40:])
    assert [type(m) for m in msgs] == [SystemStatus, GPSData, GPSData]
    assert msgs[0].azimuth == 17 and msgs[1].pitch == 4.0 and msgs[2].altitude == 7.0
    # the trailing partial status stays buffered until ChirpCount arrives
    assert p.feed(b"BeamPos:1|Azimuth:2|ChirpCount:3|") [0].chirp_count == 3


def test_azimuth_index_interpretation():
    assert st.azimuth_index_to_degrees(1) == 0.0
    assert st.azimuth_index_to_degrees(26) == 180.0
    assert st.azimuth_index_to_degrees(50) == pytest.approx(352.8)
