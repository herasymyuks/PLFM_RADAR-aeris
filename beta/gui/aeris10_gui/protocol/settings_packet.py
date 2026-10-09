"""Host -> STM32 settings packet over USB CDC.

Byte-exact mirror of the firmware receiver:

* ``9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp``
  - ``START_FLAG = {23, 46, 158, 237}`` (line 38); any bytes after the flag in
    the same transfer are forwarded to the settings buffer (lines 51-52).
  - settings buffer is 256 bytes; parsing is attempted once >= 74 bytes have
    accumulated; ``"SET"`` must sit at **offset 0** of the buffer and ``"END"``
    is searched from offset 3 (lines 60-88).
* ``RadarSettings.cpp``
  - ``parseFromUSB``: length >= 74, ``SET`` at 0, ``END`` at ``length-3``,
    fields at fixed offsets, all **big-endian** (``extractDouble`` /
    ``extractUint32`` shift bytes in MSB-first, lines 104-120).
  - ``validateSettings`` ranges (lines 86-101) are reproduced in
    :func:`validate_settings`.

Packet layout (82 bytes)::

    offset  size  field                 format
    0       3     "SET"
    3       8     system_frequency      >d
    11      8     chirp_duration_1      >d
    19      8     chirp_duration_2      >d
    27      4     chirps_per_position   >I
    31      8     freq_min              >d
    39      8     freq_max              >d
    47      8     prf1                  >d
    55      8     prf2                  >d
    63      8     max_distance          >d
    71      8     map_size              >d
    79      3     "END"

The original host builder (``GUI_V5.py:454-467``) produces the same 82 bytes.
Its *transport* layer (``GUI_V5.py:434-452``) zero-padded every write to 64
bytes; the firmware forwards those zeros into the settings buffer, so ``"SET"``
is no longer at offset 0 and the settings are never accepted
(``docs/GUI/DEPENDENCIES.md`` section 6 item 2).  The beta therefore does not
pad by default; ``pad_to_64=True`` reproduces the legacy behaviour only.
"""
from __future__ import annotations

import struct
from typing import Iterable, List

from ..model import RadarSettings

START_FLAG = bytes([23, 46, 158, 237])
SET_MARKER = b"SET"
END_MARKER = b"END"
PACKET_LENGTH = 82
FIRMWARE_MIN_LENGTH = 74          # USBHandler.cpp:66, RadarSettings.cpp:25
CDC_CHUNK_SIZE = 64               # USB full-speed bulk max packet, GUI_V5.py:440

# (field name, struct format) in wire order -- RadarSettings.cpp:40-73
FIELDS = (
    ("system_frequency", ">d"),
    ("chirp_duration_1", ">d"),
    ("chirp_duration_2", ">d"),
    ("chirps_per_position", ">I"),
    ("freq_min", ">d"),
    ("freq_max", ">d"),
    ("prf1", ">d"),
    ("prf2", ">d"),
    ("max_distance", ">d"),
    ("map_size", ">d"),
)

# RadarSettings.cpp:86-101 -- (min, max, inclusive?) ; freq_max additionally > freq_min
FIRMWARE_LIMITS = {
    "system_frequency": (1e9, 100e9),
    "chirp_duration_1": (1e-6, 1000e-6),
    "chirp_duration_2": (0.1e-6, 10e-6),
    "chirps_per_position": (1, 256),
    "freq_min": (1e6, 100e6),
    "freq_max": (None, 100e6),
    "prf1": (100, 10000),
    "prf2": (100, 10000),
    "max_distance": (100, 100000),
    "map_size": (1000, 200000),
}


class SettingsPacketError(ValueError):
    """Raised when a packet does not satisfy the firmware acceptance rules."""


def build_settings_packet(settings: RadarSettings) -> bytes:
    """Serialise ``settings`` exactly as ``GUI_V5._create_settings_packet`` does."""
    out = bytearray(SET_MARKER)
    for name, fmt in FIELDS:
        value = getattr(settings, name)
        if fmt == ">I":
            value = int(value)
            if not 0 <= value <= 0xFFFFFFFF:
                raise SettingsPacketError(f"{name}={value} does not fit uint32")
        out += struct.pack(fmt, value)
    out += END_MARKER
    assert len(out) == PACKET_LENGTH
    return bytes(out)


def parse_settings_packet(data: bytes) -> RadarSettings:
    """Decode a packet with the firmware's acceptance rules (``parseFromUSB``).

    Mirrors the firmware exactly, including its laxness: the length may be
    anything >= 74 as long as ``END`` is the last three bytes and the fixed
    field offsets are present.  Values are **not** range-checked here; use
    :func:`validate_settings`.
    """
    if data is None or len(data) < FIRMWARE_MIN_LENGTH:
        raise SettingsPacketError(f"length {0 if data is None else len(data)} < {FIRMWARE_MIN_LENGTH}")
    if data[0:3] != SET_MARKER:
        raise SettingsPacketError("missing 'SET' at offset 0")
    if data[-3:] != END_MARKER:
        raise SettingsPacketError("missing 'END' at end of packet")
    if len(data) < PACKET_LENGTH:
        # firmware would read past END into whatever follows; we refuse instead
        raise SettingsPacketError(f"length {len(data)} < {PACKET_LENGTH}: fields would overrun 'END'")
    values = {}
    offset = 3
    for name, fmt in FIELDS:
        size = struct.calcsize(fmt)
        values[name] = struct.unpack(fmt, data[offset:offset + size])[0]
        offset += size
    return RadarSettings(**values)


def validate_settings(settings: RadarSettings) -> List[str]:
    """Return the list of firmware ``validateSettings`` rules that would fail (empty = accepted)."""
    problems = []
    for name, (lo, hi) in FIRMWARE_LIMITS.items():
        v = getattr(settings, name)
        if lo is not None and v < lo:
            problems.append(f"{name}={v} < {lo}")
        if hi is not None and v > hi:
            problems.append(f"{name}={v} > {hi}")
    if settings.freq_max <= settings.freq_min:
        problems.append(f"freq_max={settings.freq_max} <= freq_min={settings.freq_min}")
    return problems


def frame_for_transmission(payload: bytes, *, pad_to_64: bool = False,
                           chunk_size: int = CDC_CHUNK_SIZE) -> List[bytes]:
    """Split ``payload`` into CDC write chunks.

    ``pad_to_64=False`` (default): chunks are the payload bytes only.  This is
    what the firmware state machine expects.

    ``pad_to_64=True``: reproduces ``GUI_V5._send_data`` (lines 434-452), which
    zero-pads the final chunk.  With the current firmware this makes the
    settings packet un-parseable (zeros enter the settings buffer before
    ``SET``).  Only use it if a future firmware is changed to strip padding.
    """
    chunks = [payload[i:i + chunk_size] for i in range(0, len(payload), chunk_size)]
    if pad_to_64:
        chunks = [c + b"\x00" * (chunk_size - len(c)) if len(c) < chunk_size else c for c in chunks]
    return chunks


def build_start_sequence(settings: RadarSettings, *, pad_to_64: bool = False) -> List[bytes]:
    """Writes the host must perform to bring the firmware to READY_FOR_DATA.

    Order from ``GUI_V5.start_radar`` (lines 1234-1239) and the firmware state
    machine: start flag first, then the settings packet.
    """
    writes = frame_for_transmission(START_FLAG, pad_to_64=pad_to_64)
    writes += frame_for_transmission(build_settings_packet(settings), pad_to_64=pad_to_64)
    return writes


def simulate_firmware_receiver(writes: Iterable[bytes]):
    """Pure-Python model of ``USBHandler`` + ``RadarSettings::parseFromUSB``.

    Used by the tests to prove which transport framing the firmware accepts.
    Returns ``(state, settings_or_None)`` where state is one of
    ``WAITING_FOR_START``, ``RECEIVING_SETTINGS``, ``READY_FOR_DATA``.
    """
    state = "WAITING_FOR_START"
    buf = bytearray()
    settings = None
    max_buffer = 256

    def process_settings(data: bytes):
        nonlocal state, buf, settings
        room = max_buffer - len(buf)
        buf += data[:room]
        if len(buf) >= FIRMWARE_MIN_LENGTH:
            has_set = buf[0:3] == SET_MARKER
            has_end = False
            for i in range(3, len(buf) - 3 + 1):
                if buf[i:i + 3] == END_MARKER:
                    has_end = True
                    if has_set:
                        try:
                            cand = parse_settings_packet(bytes(buf[:i + 3]))
                            if not validate_settings(cand):
                                settings = cand
                                state = "READY_FOR_DATA"
                        except SettingsPacketError:
                            pass
                    break
            if len(buf) >= max_buffer and not has_end:
                buf.clear()

    for data in writes:
        if not data:
            continue
        if state == "WAITING_FOR_START":
            idx = data.find(START_FLAG)
            if idx != -1:
                state = "RECEIVING_SETTINGS"
                buf.clear()
                if len(data) > idx + 4:
                    process_settings(data[idx + 4:])
        elif state == "RECEIVING_SETTINGS":
            process_settings(data)
        # READY_FOR_DATA: firmware ignores further input (USBHandler.cpp:30-33)
    return state, settings
