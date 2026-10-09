"""FPGA -> host radar data packet, as emitted by the RTL.

Source of truth: ``9_Firmware/9_2_FPGA/usb_data_interface.v`` (state machine,
lines 39-40 and 93-160).  The module drives an FT601 32-bit synchronous FIFO
bus and writes **eleven bus words** per packet.  There is **no CRC and no
length field** in the RTL; integrity can only be checked through the header,
the footer, and the redundant shifted copies the RTL happens to emit.

Word sequence (``ft601_data_out``, ``ft601_be``)::

    #   state                value                                             be
    0   SEND_HEADER          {24'b0, 8'hAA}                                    01
    1   SEND_RANGE_DATA[0]   range_profile[31:0]                               11
    2   SEND_RANGE_DATA[1]   {range_profile[23:0], 8'h00}                      11
    3   SEND_RANGE_DATA[2]   {range_profile[15:0], 16'h0000}                   11
    4   SEND_RANGE_DATA[3]   {range_profile[7:0],  24'h000000}                 11
    5   SEND_DOPPLER_DATA[0] {doppler_real, doppler_imag}                      11
    6   SEND_DOPPLER_DATA[1] {doppler_imag, doppler_real[15:8], 8'h00}         11
    7   SEND_DOPPLER_DATA[2] {doppler_real[7:0], doppler_imag[15:8], 16'h0000} 11
    8   SEND_DOPPLER_DATA[3] {doppler_imag[7:0], 24'h000000}                   11
    9   SEND_DETECTION_DATA  {31'b0, cfar_detection}                           01
    10  SEND_FOOTER          {24'b0, 8'h55}                                    01

Byte-stream mapping (ASSUMPTION A1, documented in README): the FT601 in 245
synchronous FIFO mode presents byte lane 0 (``DATA[7:0]``) first in the host
byte stream, lanes in little-endian order.  ``be = 2'b01`` ("only lower byte
valid", RTL comment) contributes 1 byte; ``be = 2'b11`` ("all bytes valid")
contributes 4 bytes.  Note the RTL declares ``ft601_be`` as 2 bits while the
FT601 has four byte-enable lines in 32-bit mode -- this is a defect of the RTL
that board bring-up must resolve; the parser works on the RTL's stated intent.

Resulting packet: **35 bytes**, ``0xAA`` + 16 range bytes + 16 Doppler bytes +
detection byte + ``0x55``.

Field semantics (``radar_system_top.v``): ``range_profile`` is wired to the
32-bit Doppler FFT output word ``{fft_q[15:0], fft_i[15:0]}``
(``radar_system_top.v:331``, ``doppler_processor.v:244``) -- the RTL comment
calls it a placeholder for a matched-filter range profile.  ``doppler_real`` =
``word[15:0]`` and ``doppler_imag`` = ``word[31:16]`` (``radar_system_top.v:
294-295``).  So in the current top level the range word and the Doppler pair
carry the same 32 bits; :func:`decode_packet` can optionally enforce that.

The packet carries **no range-bin or Doppler-bin index**.  The Doppler
processor emits cells range-major (outer loop ``read_range_bin`` 0..63, inner
``fft_sample_counter`` 0..31, ``doppler_processor.v:244-266``); a host must
count packets to place them in a map (see ``processing.FrameAssembler``).

The companion ``usb_packet_analyzer.v`` (simulation only) expects a different
layout (header in bits [31:24], range as four low bytes) and therefore does not
match the writer.  This parser follows the writer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

HEADER = 0xAA
FOOTER = 0x55
BE_LOW_BYTE = 0b01
BE_ALL = 0b11
WORDS_PER_PACKET = 11
PACKET_LENGTH = 35
# Default FPGA frame geometry: doppler_processor_optimized parameters in
# radar_receiver_final.v:291-293 (RANGE_BINS=64, DOPPLER_FFT_SIZE=32).
N_RANGE_BINS = 64
N_DOPPLER_BINS = 32


class PacketError(ValueError):
    def __init__(self, reason: str, message: str = ""):
        super().__init__(message or reason)
        self.reason = reason


@dataclass(frozen=True)
class FT601Word:
    value: int
    byte_enable: int

    def to_bytes(self) -> bytes:
        if self.byte_enable == BE_LOW_BYTE:
            return bytes([self.value & 0xFF])
        if self.byte_enable == BE_ALL:
            return (self.value & 0xFFFFFFFF).to_bytes(4, "little")
        raise PacketError("bad_byte_enable", f"unsupported byte enable {self.byte_enable:#04b}")


@dataclass
class FpgaPacket:
    range_word: int          # unsigned 32-bit as transmitted
    doppler_real: int        # signed 16-bit
    doppler_imag: int        # signed 16-bit
    detection: bool
    raw: bytes = b""

    @property
    def range_i(self) -> int:
        """range_word[15:0] as signed -- the FFT I sample in the current top level."""
        return _s16(self.range_word & 0xFFFF)

    @property
    def range_q(self) -> int:
        """range_word[31:16] as signed -- the FFT Q sample in the current top level."""
        return _s16((self.range_word >> 16) & 0xFFFF)


def _s16(u: int) -> int:
    return u - 0x10000 if u & 0x8000 else u


def _u16(s: int) -> int:
    if not -0x8000 <= s <= 0xFFFF:
        raise PacketError("range", f"{s} does not fit 16 bits")
    return s & 0xFFFF


def range_words(range_word: int) -> List[int]:
    r = range_word & 0xFFFFFFFF
    return [r, (r & 0xFFFFFF) << 8, (r & 0xFFFF) << 16, (r & 0xFF) << 24]


def doppler_words(real: int, imag: int) -> List[int]:
    re, im = _u16(real), _u16(imag)
    return [
        (re << 16) | im,
        (im << 16) | (((re >> 8) & 0xFF) << 8),
        ((re & 0xFF) << 24) | (((im >> 8) & 0xFF) << 16),
        (im & 0xFF) << 24,
    ]


def encode_words(range_word: int, doppler_real: int, doppler_imag: int,
                 detection: bool) -> List[FT601Word]:
    """Exact bus-word sequence the RTL writes for one packet."""
    words = [FT601Word(HEADER, BE_LOW_BYTE)]
    words += [FT601Word(w, BE_ALL) for w in range_words(range_word)]
    words += [FT601Word(w, BE_ALL) for w in doppler_words(doppler_real, doppler_imag)]
    words.append(FT601Word(1 if detection else 0, BE_LOW_BYTE))
    words.append(FT601Word(FOOTER, BE_LOW_BYTE))
    return words


def words_to_bytes(words: Sequence[FT601Word]) -> bytes:
    return b"".join(w.to_bytes() for w in words)


def encode_packet(range_word: int, doppler_real: int, doppler_imag: int,
                  detection: bool) -> bytes:
    """35-byte host-side image of one RTL packet (assumption A1)."""
    data = words_to_bytes(encode_words(range_word, doppler_real, doppler_imag, detection))
    assert len(data) == PACKET_LENGTH
    return data


def encode_cell(i: int, q: int, detection: bool) -> bytes:
    """Encode one Doppler cell the way the current top level wires it:
    range_word = {Q, I}, doppler_real = I, doppler_imag = Q."""
    return encode_packet((_u16(q) << 16) | _u16(i), i, q, detection)


def decode_packet(buf: bytes, *, check_top_level_consistency: bool = False) -> FpgaPacket:
    """Decode exactly one packet at ``buf[0:35]``.

    Raises :class:`PacketError` with ``reason`` in
    ``truncated | bad_header | bad_footer | bad_range_redundancy |
    bad_doppler_redundancy | bad_detection_byte | inconsistent_range_word``.
    """
    if len(buf) < PACKET_LENGTH:
        raise PacketError("truncated", f"{len(buf)} < {PACKET_LENGTH} bytes")
    if buf[0] != HEADER:
        raise PacketError("bad_header", f"header {buf[0]:#04x} != {HEADER:#04x}")
    if buf[34] != FOOTER:
        raise PacketError("bad_footer", f"footer {buf[34]:#04x} != {FOOTER:#04x}")
    w = [int.from_bytes(buf[1 + 4 * k:5 + 4 * k], "little") for k in range(8)]
    range_word = w[0]
    if w[1:4] != range_words(range_word)[1:]:
        raise PacketError("bad_range_redundancy", "shifted range copies do not match word 0")
    real_u = (w[4] >> 16) & 0xFFFF
    imag_u = w[4] & 0xFFFF
    if w[5:8] != doppler_words(real_u, imag_u)[1:]:
        raise PacketError("bad_doppler_redundancy", "shifted Doppler copies do not match word 0")
    det = buf[33]
    if det not in (0, 1):
        raise PacketError("bad_detection_byte", f"detection byte {det:#04x} not in {{0,1}}")
    if check_top_level_consistency and range_word != ((imag_u << 16) | real_u):
        raise PacketError("inconsistent_range_word",
                          "range_word != {doppler_imag, doppler_real} (radar_system_top.v:294-331)")
    return FpgaPacket(range_word, _s16(real_u), _s16(imag_u), bool(det), bytes(buf[:PACKET_LENGTH]))


def decode_words(words: Sequence[FT601Word], **kw) -> FpgaPacket:
    """Decode from captured bus words (e.g. a simulation dump) instead of a byte stream."""
    if len(words) != WORDS_PER_PACKET:
        raise PacketError("truncated", f"{len(words)} words != {WORDS_PER_PACKET}")
    return decode_packet(words_to_bytes(words), **kw)


class FpgaPacketParser:
    """Streaming parser with resynchronisation.

    ``feed(bytes)`` returns the packets completed so far.  Invalid candidates
    are skipped one byte at a time (the header value 0xAA is not escaped in the
    payload, so a false header is possible; the footer and the redundancy
    checks reject it).  ``stats`` counts every outcome.
    """

    def __init__(self, *, check_top_level_consistency: bool = False, max_buffer: int = 1 << 20):
        self._buf = bytearray()
        self.check_top_level_consistency = check_top_level_consistency
        self.max_buffer = max_buffer
        self.stats = {"packets": 0, "bytes": 0, "resync_bytes_dropped": 0,
                      "bad_footer": 0, "bad_range_redundancy": 0,
                      "bad_doppler_redundancy": 0, "bad_detection_byte": 0,
                      "inconsistent_range_word": 0}

    @property
    def pending(self) -> int:
        return len(self._buf)

    def reset(self) -> None:
        self._buf.clear()

    def feed(self, data: bytes) -> List[FpgaPacket]:
        self.stats["bytes"] += len(data)
        self._buf += data
        out: List[FpgaPacket] = []
        while True:
            idx = self._buf.find(bytes([HEADER]))
            if idx == -1:
                self.stats["resync_bytes_dropped"] += len(self._buf)
                self._buf.clear()
                break
            if idx:
                self.stats["resync_bytes_dropped"] += idx
                del self._buf[:idx]
            if len(self._buf) < PACKET_LENGTH:
                break                                   # truncated: wait for more bytes
            try:
                pkt = decode_packet(self._buf, check_top_level_consistency=self.check_top_level_consistency)
            except PacketError as e:
                self.stats[e.reason] = self.stats.get(e.reason, 0) + 1
                self.stats["resync_bytes_dropped"] += 1
                del self._buf[:1]
                continue
            out.append(pkt)
            self.stats["packets"] += 1
            del self._buf[:PACKET_LENGTH]
        if len(self._buf) > self.max_buffer:
            self.stats["resync_bytes_dropped"] += len(self._buf) - PACKET_LENGTH
            del self._buf[:-PACKET_LENGTH]
        return out
