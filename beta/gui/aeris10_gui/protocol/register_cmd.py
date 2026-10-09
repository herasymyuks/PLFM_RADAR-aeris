"""ASCII register access commands over the STM32 CDC link -- same rules as the firmware.

Firmware reference (BETA, 2026-10-09):
``beta/stm32/Core/Src/host_bridge_proto.c`` (``hb_cmd_parse``, ``parse_u32``,
``hb_cmd_execute``), ``beta/stm32/LIB/USBHandler.cpp`` (``captureTextCommand``,
``takePendingCommand``) and ``beta/stm32/Core/Src/main.cpp`` (main-loop reply).

Rules the GUI mirrors exactly:

* A command is recognised only when a USB transfer **starts** with ``REG``
  (upper case, bytes 0..2).  Keyword ``W``/``R`` is case-insensitive.  Numbers
  are ``0x``/``0X``-prefixed hexadecimal (at most 8 digits) or decimal;
  address <= 0xFFFF; anything after the arguments other than whitespace,
  ``\\r`` or ``\\n`` is an error.  The firmware cuts the line at the first
  ``\\0``, ``\\r`` or ``\\n``: **one command per transfer**, later lines in
  the same transfer are discarded.
* **Single slot**: while a captured command has not yet been executed by the
  main loop, further ``REG`` transfers are dropped silently.  The host must
  therefore send one command and wait for its reply before sending the next
  (:class:`RegisterClient` enforces this and retries on timeout).
* Replies: ``REG 0x%04X 0x%08X\\r\\n`` (a write echoes the *written* value;
  read-back needs an explicit read) or ``REG ERR\\r\\n`` on a parse error,
  SPI transfer error or missing 0xA2 write-ack.
* SPI status command 0x04 (``hb_proto_status``) returns four little-endian
  u16 fields: status (bit0 frame ready, bit1 ADAR CS conflict, bit2 FIFO
  overflow, bit3 calibration lock), version, frames, reserved.  It has no
  text form yet; :func:`parse_bridge_status` decodes the raw bytes.
"""
from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Optional, Tuple

REPLY_PREFIX = "REG"
MAX_HEX_DIGITS = 8          # parse_u32: n++ >= 8 -> NULL
_NUMBER_RE = re.compile(r"^(?:0[xX][0-9a-fA-F]{1,8}|[0-9]+)$")
_TOKEN_RE = re.compile(r"[ \t]+")
REPLY_RE = re.compile(r"^REG[ \t]+(0[xX][0-9a-fA-F]{1,8}|[0-9]+)[ \t]+(0[xX][0-9a-fA-F]{1,8}|[0-9]+)[ \t]*$")


class RegisterCommandError(ValueError):
    pass


def parse_int(token: str) -> int:
    """``parse_u32``: 0x-hex (<= 8 digits) or decimal, 32-bit."""
    if not _NUMBER_RE.match(token):
        raise RegisterCommandError(f"not a number (0x-hex <= 8 digits or decimal): {token!r}")
    v = int(token, 0)
    if v > 0xFFFFFFFF:
        raise RegisterCommandError(f"value {token!r} exceeds 32 bits")
    return v


def _cut_line(line: str) -> str:
    """captureTextCommand: the firmware keeps bytes up to the first \\0, \\r or \\n."""
    for sep in ("\x00", "\r", "\n"):
        i = line.find(sep)
        if i != -1:
            line = line[:i]
    return line


def format_write(addr: int, value: int) -> bytes:
    if not 0 <= addr <= 0xFFFF or not 0 <= value <= 0xFFFFFFFF:
        raise RegisterCommandError("address must fit 16 bits and value 32 bits")
    return f"REG W 0x{addr:X} 0x{value:X}\n".encode("ascii")


def format_read(addr: int) -> bytes:
    if not 0 <= addr <= 0xFFFF:
        raise RegisterCommandError("address must fit 16 bits")
    return f"REG R 0x{addr:X}\n".encode("ascii")


def format_reply(addr: int, value: int) -> bytes:
    """Firmware ``snprintf(reply, cap, "REG 0x%04X 0x%08lX\\r\\n", addr, v)``."""
    return f"REG 0x{addr & 0xFFFF:04X} 0x{value & 0xFFFFFFFF:08X}\r\n".encode("ascii")


def format_error() -> bytes:
    return b"REG ERR\r\n"


def is_text_command(data: bytes) -> bool:
    """``hb_cmd_is_text_command`` / ``captureTextCommand``: transfer starts with 'REG'."""
    return len(data) >= 3 and data[:3] == b"REG"


def parse_command(line: str) -> Tuple[str, int, Optional[int]]:
    """Device-side parse (``hb_cmd_parse``).  Returns ``("W", addr, value)`` or ``("R", addr, None)``."""
    line = _cut_line(line)
    p = line.lstrip(" \t")
    if not p.startswith("REG"):
        raise RegisterCommandError(f"not a REG command: {line!r}")
    toks = [t for t in _TOKEN_RE.split(p[3:].strip(" \t")) if t]
    if not toks or toks[0].upper() not in ("W", "R") or len(toks[0]) != 1:
        raise RegisterCommandError(f"malformed REG command: {line!r}")
    op = toks[0].upper()
    if op == "W" and len(toks) == 3:
        addr, value = parse_int(toks[1]), parse_int(toks[2])
    elif op == "R" and len(toks) == 2:
        addr, value = parse_int(toks[1]), None
    else:
        raise RegisterCommandError(f"malformed REG command (argument count / trailing junk): {line!r}")
    if addr > 0xFFFF:
        raise RegisterCommandError(f"address {addr:#x} > 0xFFFF")
    return op, addr, value


@dataclass
class RegisterReply:
    addr: Optional[int]
    value: Optional[int]
    error: bool = False
    raw: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and self.addr is not None


def is_reply_line(line: str) -> bool:
    s = _cut_line(line).strip(" \t")
    return s == "REG ERR" or bool(REPLY_RE.match(s))


def parse_reply(line: str) -> RegisterReply:
    s = _cut_line(line).strip(" \t")
    if s == "REG ERR":
        return RegisterReply(None, None, True, s)
    m = REPLY_RE.match(s)
    if not m:
        raise RegisterCommandError(f"not a REG reply: {line!r}")
    return RegisterReply(parse_int(m.group(1)), parse_int(m.group(2)), False, s)


@dataclass
class BridgeStatus:
    """SPI command 0x04 payload (``hb_proto_status``): four little-endian u16 after the command byte."""
    status: int
    version: int
    frames: int
    reserved: int

    frame_ready = property(lambda s: bool(s.status & 1))
    adar_cs_conflict = property(lambda s: bool(s.status & 2))
    fifo_overflow = property(lambda s: bool(s.status & 4))
    calibration_lock = property(lambda s: bool(s.status & 8))


def parse_bridge_status(rx: bytes) -> BridgeStatus:
    """``rx`` = the 9 bytes clocked for command 0x04 (rx[0] is the dummy byte under the command)."""
    if len(rx) < 9:
        raise RegisterCommandError(f"status transfer needs 9 bytes, got {len(rx)}")
    f = [rx[i] | (rx[i + 1] << 8) for i in (1, 3, 5, 7)]
    return BridgeStatus(*f)


@dataclass
class _Request:
    op: str
    addr: int
    value: Optional[int]
    tag: object
    sent_at: Optional[float] = None
    attempts: int = 0

    def as_tuple(self):
        return (self.op, self.addr, self.value, self.tag)

    def data(self) -> bytes:
        return format_write(self.addr, self.value) if self.op == "W" else format_read(self.addr)


class RegisterClient:
    """Host-side pacing and bookkeeping for the single-slot firmware.

    Exactly **one** command is in flight at a time: the next queued command
    is written only after the reply to the previous one was consumed by
    :meth:`on_reply`, or after ``timeout`` seconds (:meth:`poll`), in which
    case the in-flight command is re-sent up to ``retries`` times and then
    recorded in ``errors`` with tag ``"timeout"``.
    """

    LANE_INFO_ADDR = 0xA
    LANE_SELECT_ADDR = 0x5

    def __init__(self, write_fn: Callable[[bytes], object], *, max_pending: int = 256,
                 timeout: float = 1.0, retries: int = 2, clock: Callable[[], float] = time.monotonic):
        self.write_fn = write_fn
        self.max_pending = max_pending
        self.timeout = timeout
        self.retries = retries
        self.clock = clock
        self._queue: Deque[_Request] = deque()
        self.in_flight: Optional[_Request] = None
        self.values: dict = {}            # addr -> last value reported by the device
        self.lane_info: dict = {}         # lane -> raw CAL_LANE_INFO
        self.errors = []                  # (op, addr, value, tag) answered with REG ERR / timed out
        self.unexpected = 0               # replies with no in-flight request, or address mismatch
        self.retransmits = 0
        self.sent = 0

    # --- queueing --------------------------------------------------------------------------
    @property
    def pending(self):
        """All requests not yet answered (in-flight first)."""
        out = [self.in_flight.as_tuple()] if self.in_flight else []
        return out + [r.as_tuple() for r in self._queue]

    def _enqueue(self, req: _Request) -> None:
        if len(self._queue) + (1 if self.in_flight else 0) >= self.max_pending:
            raise RegisterCommandError("too many outstanding REG requests (device not answering?)")
        self._queue.append(req)
        self._pump()

    def _pump(self) -> None:
        if self.in_flight is None and self._queue:
            self.in_flight = self._queue.popleft()
            self._transmit(self.in_flight)

    def _transmit(self, req: _Request) -> None:
        req.sent_at = self.clock()
        req.attempts += 1
        self.sent += 1
        self.write_fn(req.data())

    def write(self, addr: int, value: int, tag=None) -> None:
        format_write(addr, value)                      # validate early
        self._enqueue(_Request("W", addr, value, tag))

    def read(self, addr: int, tag=None) -> None:
        format_read(addr)
        self._enqueue(_Request("R", addr, None, tag))

    def read_all(self, addresses, *, lanes: int = 8) -> None:
        """Read every address, then CAL_LANE_INFO of every lane (restoring CAL_LANE afterwards)."""
        for a in addresses:
            self.read(a)
        if lanes:
            restore = self.values.get(self.LANE_SELECT_ADDR, 0) & 0x7
            for lane in range(lanes):
                self.write(self.LANE_SELECT_ADDR, lane, tag=("lane_select", lane))
                self.read(self.LANE_INFO_ADDR, tag=("lane", lane))
            self.write(self.LANE_SELECT_ADDR, restore, tag=("lane_select", restore))

    # --- progress --------------------------------------------------------------------------
    def poll(self, now: Optional[float] = None) -> None:
        """Call periodically: handles the reply timeout of the in-flight command."""
        req = self.in_flight
        if req is None or req.sent_at is None:
            return
        now = self.clock() if now is None else now
        if now - req.sent_at < self.timeout:
            return
        if req.attempts <= self.retries:
            self.retransmits += 1
            self._transmit(req)
        else:
            self.errors.append((req.op, req.addr, req.value, "timeout"))
            self.in_flight = None
            self._pump()

    def on_reply(self, reply: RegisterReply):
        """Consume one reply; returns the matched request tuple (or None)."""
        req = self.in_flight
        if req is None:
            self.unexpected += 1
            if reply.ok:
                self.values[reply.addr] = reply.value
            return None
        self.in_flight = None
        if reply.error:
            self.errors.append(req.as_tuple())
        else:
            if reply.addr != req.addr:
                self.unexpected += 1
            self.values[reply.addr] = reply.value
            if isinstance(req.tag, tuple) and req.tag[0] == "lane" and reply.addr == self.LANE_INFO_ADDR:
                self.lane_info[req.tag[1]] = reply.value
        self._pump()
        return req.as_tuple()
