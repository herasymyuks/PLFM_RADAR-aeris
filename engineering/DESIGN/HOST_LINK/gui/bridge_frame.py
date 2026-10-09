"""Parser for the AERIS-10 host-link option-B frame (DSN-LINK-01, HOST_LINK_DESIGN.md §5).

Frame = 16-byte header + N_RANGE*N_DOPPLER uint8 log-magnitudes (range-major) + 3*n_det detection
triples + CRC-16/CCITT-FALSE (big-endian) over everything before it.  The STM32 forwards frames over
USB CDC interleaved with ASCII status strings; `BridgeStreamParser` resynchronises on the sync word.
Reference vector: tests/vectors/bridge_frame_from_rtl_tb.hex (dumped by the Verilog testbench).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

SYNC = b"\xa5\x5a"
HEADER_LEN = 16
VERSION = 1
MAX_DET = 32


def crc16_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


@dataclass
class BridgeFrame:
    version: int
    flags: int
    seq: int
    azimuth: int
    elevation: int
    chirp_count: int
    n_range: int
    n_doppler: int
    magnitude: bytes                      # n_range*n_doppler uint8, range-major (8*log2(|I|+|Q|))
    detections: list = field(default_factory=list)   # (range_idx, doppler_idx, mag)

    @property
    def long_chirp(self) -> bool:
        return bool(self.flags & 1)

    @property
    def overflow(self) -> bool:
        return bool(self.flags & 2)

    def map2d(self):
        """Return the magnitude map as a list of rows (range) × columns (doppler)."""
        return [list(self.magnitude[r * self.n_doppler:(r + 1) * self.n_doppler]) for r in range(self.n_range)]


class FrameError(ValueError):
    pass


def frame_length(header: bytes) -> int:
    """Total frame length (incl. CRC) from a 16-byte header."""
    if len(header) < HEADER_LEN or header[:2] != SYNC:
        raise FrameError("bad sync")
    n_range, n_doppler = header[10], header[11]
    n_det = struct.unpack_from("<H", header, 12)[0]
    if n_det > MAX_DET:
        raise FrameError(f"n_det {n_det} > {MAX_DET}")
    return HEADER_LEN + n_range * n_doppler + 3 * n_det + 2


def parse_frame(buf: bytes) -> BridgeFrame:
    if len(buf) < HEADER_LEN:
        raise FrameError("truncated header")
    total = frame_length(buf[:HEADER_LEN])
    if len(buf) < total:
        raise FrameError(f"truncated: {len(buf)} < {total}")
    body = buf[:total - 2]
    crc_rx = (buf[total - 2] << 8) | buf[total - 1]
    if crc16_ccitt_false(body) != crc_rx:
        raise FrameError("crc mismatch")
    version, flags = buf[2], buf[3]
    if version != VERSION:
        raise FrameError(f"unsupported version {version}")
    seq, = struct.unpack_from("<H", buf, 4)
    az, el = buf[6], buf[7]
    chirps, = struct.unpack_from("<H", buf, 8)
    n_range, n_doppler = buf[10], buf[11]
    n_det, = struct.unpack_from("<H", buf, 12)
    off = HEADER_LEN
    mag = bytes(buf[off:off + n_range * n_doppler]); off += n_range * n_doppler
    dets = [(buf[off + 3 * i], buf[off + 3 * i + 1], buf[off + 3 * i + 2]) for i in range(n_det)]
    return BridgeFrame(version, flags, seq, az, el, chirps, n_range, n_doppler, mag, dets)


def build_frame(frame: BridgeFrame) -> bytes:
    """Serialise (used by tests and the simulator)."""
    hdr = SYNC + bytes([frame.version, frame.flags]) + struct.pack("<H", frame.seq) + bytes([frame.azimuth, frame.elevation]) \
        + struct.pack("<H", frame.chirp_count) + bytes([frame.n_range, frame.n_doppler]) + struct.pack("<H", len(frame.detections)) + b"\x00\x00"
    body = hdr + bytes(frame.magnitude) + b"".join(bytes(d) for d in frame.detections)
    crc = crc16_ccitt_false(body)
    return body + bytes([crc >> 8, crc & 0xFF])


class BridgeStreamParser:
    """Feed arbitrary CDC chunks; yields BridgeFrame objects and passes non-frame bytes (status text) to `text_sink`."""

    def __init__(self, text_sink=None):
        self.buf = bytearray()
        self.text_sink = text_sink
        self.frames = 0
        self.crc_errors = 0
        self.resyncs = 0

    def feed(self, chunk: bytes):
        self.buf.extend(chunk)
        out = []
        while True:
            i = self.buf.find(SYNC)
            if i < 0:
                self._emit_text(bytes(self.buf[:-1])) if len(self.buf) > 1 else None
                if len(self.buf) > 1:
                    del self.buf[:-1]
                break
            if i > 0:
                self._emit_text(bytes(self.buf[:i])); del self.buf[:i]
            if len(self.buf) < HEADER_LEN:
                break
            try:
                total = frame_length(bytes(self.buf[:HEADER_LEN]))
            except FrameError:
                self.resyncs += 1; del self.buf[:2]; continue
            if len(self.buf) < total:
                break
            try:
                out.append(parse_frame(bytes(self.buf[:total]))); self.frames += 1; del self.buf[:total]
            except FrameError:
                self.crc_errors += 1; self.resyncs += 1; del self.buf[:2]
        return out

    def _emit_text(self, data: bytes):
        if data and self.text_sink:
            self.text_sink(data)
