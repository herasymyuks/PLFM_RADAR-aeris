"""STM32 -> host text/binary status messages.

Sources:

* ``9_1_3_C_Cpp_Code/main.cpp:807-877`` ``getSystemStatusForGUI`` builds the
  ``"System Status: "`` string (sent once over USB CDC with ``CDC_Transmit_FS``
  at line 1692, no terminator)::

      System Status: NORMAL|LastError:%d|ErrorCount:%lu|
      IMU:%.1f,%.1f,%.1f|GPS:%.6f,%.6f|ALT:%.1f|LO_TX:LOCKED|LO_RX:UNLOCKED|
      T1:%.1f|...|T8:%.1f|[PA_AvgCurrent:%.2f|PA_Enabled:%d|]
      BeamPos:%d|Azimuth:%d|ChirpCount:%d|

  (``EMERGENCY_STOP`` replaces ``NORMAL``; the PA block is present only when
  ``PowerAmplifier`` is non-zero.)  ``ChirpCount:%d|`` is always the last
  field, which this module uses as the end-of-message marker.
* ``9_1_1_C_Cpp_Libraries/gps_handler.cpp:45-62`` ``GPS:%.8f,%.8f,%.2f\\r\\n``
  (three fields; **UART3**, not USB).  A fourth ``pitch`` field is accepted
  for compatibility with ``GUI_V5.py:686`` but is not produced by the firmware.
* ``gps_handler.cpp:65-119`` 30-byte binary ``GPSB`` frame over CDC:
  ``'GPSB'`` + lat (>d) + lon (>d) + alt (>f) + pitch (>f) + 16-bit sum of the
  first 28 bytes (big-endian).  Mirrors ``GUI_V5.py:702-751``.

Azimuth/elevation indices: ``main.cpp:187-189`` declares ``n`` in [1..31]
(elevations per azimuth) and ``y`` in [1..y_max], ``y_max = 50`` azimuths per
revolution.  :func:`azimuth_index_to_degrees` converts with 360/y_max; this is
an interpretation (no angle table exists in the firmware) and is flagged as
such in the README.
"""
from __future__ import annotations

import re
import struct
import time
from typing import List, Optional, Union

from ..model import GPSData, SystemStatus

STATUS_PREFIX = "System Status: "
GPS_TEXT_PREFIX = "GPS:"
GPSB_MAGIC = b"GPSB"
GPSB_LENGTH = 30
FIRMWARE_Y_MAX = 50       # main.cpp:189
FIRMWARE_N_MAX = 31       # main.cpp:187

_END_FIELD_RE = re.compile(r"ChirpCount:-?\d+\|")


def _f(s: str) -> float:
    return float(s)


def parse_status_line(text: str) -> SystemStatus:
    text = text.strip("\r\n")
    if not text.startswith(STATUS_PREFIX):
        raise ValueError("not a 'System Status:' message")
    body = text[len(STATUS_PREFIX):]
    fields = [f for f in body.split("|") if f != ""]
    if not fields:
        raise ValueError("empty status body")
    st = SystemStatus(mode=fields[0], raw=text)
    for item in fields[1:]:
        if ":" not in item:
            st.unknown_fields[item] = None
            continue
        key, _, val = item.partition(":")
        try:
            if key == "LastError":
                st.last_error = int(val)
            elif key == "ErrorCount":
                st.error_count = int(val)
            elif key == "IMU":
                p, r, y = (_f(x) for x in val.split(","))
                st.imu_pitch, st.imu_roll, st.imu_yaw = p, r, y
            elif key == "GPS":
                la, lo = (_f(x) for x in val.split(","))
                st.gps_latitude, st.gps_longitude = la, lo
            elif key == "ALT":
                st.altitude = _f(val)
            elif key == "LO_TX":
                st.lo_tx_locked = (val == "LOCKED")
            elif key == "LO_RX":
                st.lo_rx_locked = (val == "LOCKED")
            elif re.fullmatch(r"T[1-8]", key):
                idx = int(key[1:]) - 1
                while len(st.temperatures) <= idx:
                    st.temperatures.append(None)
                st.temperatures[idx] = _f(val)
            elif key == "PA_AvgCurrent":
                st.pa_avg_current = _f(val)
            elif key == "PA_Enabled":
                st.pa_enabled = int(val)
            elif key == "BeamPos":
                st.beam_pos = int(val)
            elif key == "Azimuth":
                st.azimuth = int(val)
            elif key == "ChirpCount":
                st.chirp_count = int(val)
            else:
                st.unknown_fields[key] = val
        except ValueError:
            st.unknown_fields[key] = val
    return st


def format_status_line(*, mode="NORMAL", last_error=0, error_count=0,
                       imu=(0.0, 0.0, 0.0), gps=(0.0, 0.0), altitude=0.0,
                       lo_tx_locked=True, lo_rx_locked=True,
                       temperatures=(0.0,) * 8, pa_avg_current=None, pa_enabled=0,
                       beam_pos=1, azimuth=1, chirp_count=0) -> str:
    """Produce the firmware string byte-for-byte (used by the simulator and tests).

    Reproduces the ``snprintf`` formats of ``main.cpp:819-872``.
    """
    s = STATUS_PREFIX + f"{mode}|"
    s += f"LastError:{last_error}|ErrorCount:{error_count}|"
    s += "IMU:%.1f,%.1f,%.1f|GPS:%.6f,%.6f|ALT:%.1f|" % (*imu, *gps, altitude)
    s += "LO_TX:%s|LO_RX:%s|" % ("LOCKED" if lo_tx_locked else "UNLOCKED",
                                 "LOCKED" if lo_rx_locked else "UNLOCKED")
    s += "".join("T%d:%.1f|" % (i + 1, t) for i, t in enumerate(temperatures[:8]))
    if pa_enabled:
        s += "PA_AvgCurrent:%.2f|PA_Enabled:%d|" % (pa_avg_current or 0.0, pa_enabled)
    s += "BeamPos:%d|Azimuth:%d|ChirpCount:%d|" % (beam_pos, azimuth, chirp_count)
    return s


def parse_gps_text(text: str, timestamp: Optional[float] = None) -> GPSData:
    text = text.strip()
    if not text.startswith(GPS_TEXT_PREFIX):
        raise ValueError("not a 'GPS:' message")
    parts = text[len(GPS_TEXT_PREFIX):].split(",")
    if len(parts) not in (3, 4):
        raise ValueError(f"GPS text has {len(parts)} fields, expected 3 (firmware) or 4 (GUI_V5 legacy)")
    lat, lon, alt = (float(p) for p in parts[:3])
    pitch = float(parts[3]) if len(parts) == 4 else 0.0
    return GPSData(lat, lon, alt, pitch, timestamp if timestamp is not None else time.time())


def gpsb_checksum(data: bytes) -> int:
    return sum(data[:28]) & 0xFFFF


def parse_gpsb(data: bytes, timestamp: Optional[float] = None) -> GPSData:
    if len(data) < GPSB_LENGTH:
        raise ValueError(f"GPSB frame needs {GPSB_LENGTH} bytes, got {len(data)}")
    if data[:4] != GPSB_MAGIC:
        raise ValueError("missing GPSB magic")
    expected = (data[28] << 8) | data[29]
    if gpsb_checksum(data) != expected:
        raise ValueError(f"GPSB checksum mismatch: {gpsb_checksum(data):#06x} != {expected:#06x}")
    lat, lon, alt, pitch = struct.unpack(">ddff", data[4:28])
    return GPSData(lat, lon, alt, pitch, timestamp if timestamp is not None else time.time())


def encode_gpsb(lat: float, lon: float, alt: float, pitch: float) -> bytes:
    body = GPSB_MAGIC + struct.pack(">ddff", lat, lon, alt, pitch)
    crc = gpsb_checksum(body)
    return body + bytes([(crc >> 8) & 0xFF, crc & 0xFF])


def azimuth_index_to_degrees(y: int, y_max: int = FIRMWARE_Y_MAX) -> float:
    """Interpretation: azimuth index y in [1..y_max] -> (y-1) * 360 / y_max degrees."""
    return ((y - 1) % y_max) * 360.0 / y_max


Message = Union[SystemStatus, GPSData]


class StatusStreamParser:
    """Splits a CDC byte stream into status strings, GPS text lines and GPSB frames.

    The status string has no terminator in the firmware, so the parser relies
    on ``ChirpCount:<n>|`` being its last field.  Text is decoded as latin-1
    (the firmware only emits ASCII).
    """

    def __init__(self, max_buffer: int = 8192):
        self._buf = bytearray()
        self.max_buffer = max_buffer
        self.stats = {"status": 0, "gps_text": 0, "gpsb": 0, "errors": 0, "dropped_bytes": 0}

    def feed(self, data: bytes, timestamp: Optional[float] = None) -> List[Message]:
        self._buf += data
        out: List[Message] = []
        while self._buf:
            # binary frame first
            if self._buf.startswith(GPSB_MAGIC):
                if len(self._buf) < GPSB_LENGTH:
                    break
                try:
                    out.append(parse_gpsb(bytes(self._buf[:GPSB_LENGTH]), timestamp))
                    self.stats["gpsb"] += 1
                    del self._buf[:GPSB_LENGTH]
                except ValueError:
                    self.stats["errors"] += 1
                    del self._buf[:1]
                continue
            text = self._buf.decode("latin-1")
            # earliest recognisable start
            starts = [i for i in (text.find(STATUS_PREFIX), text.find(GPS_TEXT_PREFIX), text.find("GPSB")) if i >= 0]
            if not starts:
                # keep a tail in case a prefix is split across reads
                keep = max(len(STATUS_PREFIX), 4) - 1
                if len(self._buf) > keep:
                    self.stats["dropped_bytes"] += len(self._buf) - keep
                    del self._buf[:-keep]
                break
            start = min(starts)
            if start:
                self.stats["dropped_bytes"] += start
                del self._buf[:start]
                continue
            if text.startswith(STATUS_PREFIX):
                m = _END_FIELD_RE.search(text)
                if not m:
                    break                       # incomplete
                chunk = text[:m.end()]
                try:
                    out.append(parse_status_line(chunk))
                    self.stats["status"] += 1
                except ValueError:
                    self.stats["errors"] += 1
                del self._buf[:len(chunk.encode("latin-1"))]
                # swallow an optional CRLF
                if self._buf[:2] == b"\r\n":
                    del self._buf[:2]
                continue
            if text.startswith(GPS_TEXT_PREFIX):
                nl = text.find("\n")
                if nl == -1:
                    break
                line = text[:nl + 1]
                try:
                    out.append(parse_gps_text(line, timestamp))
                    self.stats["gps_text"] += 1
                except ValueError:
                    self.stats["errors"] += 1
                del self._buf[:len(line.encode("latin-1"))]
                continue
            break
        if len(self._buf) > self.max_buffer:
            self.stats["dropped_bytes"] += len(self._buf) - 64
            del self._buf[:-64]
        return out
