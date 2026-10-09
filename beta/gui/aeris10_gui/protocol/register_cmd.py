"""ASCII register access commands over the STM32 CDC link.

HOST_LINK_DESIGN.md section 7 specifies only the shape:
``REG W <addr> <value>`` / ``REG R <addr>`` from the host, reply
``REG <addr> <value>`` in the status stream (ASCII, so the bridge-frame parser
passes it through), and the coordinator added ``REG ERR`` for failures.  No
firmware implements this yet (``beta/stm32/LIB/USBHandler.cpp`` ignores all
input once in READY_FOR_DATA), so the lexical details below are **PROPOSED by
the GUI side** and must be mirrored by the firmware owner:

* one command per line, terminated by ``\\n`` (``\\r\\n`` accepted);
* tokens separated by one or more spaces; keywords case-insensitive;
* numbers: ``0x``-prefixed hexadecimal or plain decimal (Python ``int(x, 0)``
  rules; the host always *emits* hexadecimal);
* reply ``REG 0x<addr> 0x<value>`` for both reads and successful writes
  (the write reply echoes the value the device now holds, so the host can see
  read-only/toggle bits), ``REG ERR`` on an unknown address, malformed line or
  SPI failure (bridge reply 0xEE / missing 0xA2 ack);
* the device never emits ``\\xA5\\x5A`` inside a text line (frame sync).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

REPLY_PREFIX = "REG"
_TOKEN_RE = re.compile(r"\s+")


class RegisterCommandError(ValueError):
    pass


def parse_int(token: str) -> int:
    try:
        v = int(token, 0)
    except ValueError:
        raise RegisterCommandError(f"not a number: {token!r}") from None
    if v < 0:
        raise RegisterCommandError(f"negative value: {token!r}")
    return v


def format_write(addr: int, value: int) -> bytes:
    if not 0 <= addr <= 0xFFFF or not 0 <= value <= 0xFFFFFFFF:
        raise RegisterCommandError("address must fit 16 bits and value 32 bits")
    return f"REG W 0x{addr:X} 0x{value:X}\n".encode("ascii")


def format_read(addr: int) -> bytes:
    if not 0 <= addr <= 0xFFFF:
        raise RegisterCommandError("address must fit 16 bits")
    return f"REG R 0x{addr:X}\n".encode("ascii")


def format_reply(addr: int, value: int) -> bytes:
    return f"REG 0x{addr:X} 0x{value:X}\n".encode("ascii")


def format_error() -> bytes:
    return b"REG ERR\n"


def parse_command(line: str) -> Tuple[str, int, Optional[int]]:
    """Device-side parse of a host command.  Returns ``("W", addr, value)`` or ``("R", addr, None)``."""
    toks = _TOKEN_RE.split(line.strip())
    if len(toks) < 3 or toks[0].upper() != REPLY_PREFIX:
        raise RegisterCommandError(f"not a REG command: {line!r}")
    op = toks[1].upper()
    if op == "W" and len(toks) == 4:
        return "W", parse_int(toks[2]), parse_int(toks[3])
    if op == "R" and len(toks) == 3:
        return "R", parse_int(toks[2]), None
    raise RegisterCommandError(f"malformed REG command: {line!r}")


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
    toks = _TOKEN_RE.split(line.strip())
    return bool(toks) and toks[0].upper() == REPLY_PREFIX and (len(toks) == 2 and toks[1].upper() == "ERR" or len(toks) == 3)


def parse_reply(line: str) -> RegisterReply:
    toks = _TOKEN_RE.split(line.strip())
    if not toks or toks[0].upper() != REPLY_PREFIX:
        raise RegisterCommandError(f"not a REG reply: {line!r}")
    if len(toks) == 2 and toks[1].upper() == "ERR":
        return RegisterReply(None, None, True, line.strip())
    if len(toks) == 3:
        return RegisterReply(parse_int(toks[1]), parse_int(toks[2]), False, line.strip())
    raise RegisterCommandError(f"malformed REG reply: {line!r}")


class RegisterClient:
    """Host-side bookkeeping for asynchronous REG commands.

    Commands are written with ``write_fn(bytes)``; replies arrive later in the
    status stream and are passed to :meth:`on_reply`.  The firmware is assumed
    to answer in command order (single CDC connection, sequential SPI), so a
    FIFO of outstanding requests attributes ``REG ERR`` replies and the
    per-lane CAL_LANE_INFO reads.
    """

    LANE_INFO_ADDR = 0xA
    LANE_SELECT_ADDR = 0x5

    def __init__(self, write_fn, *, max_pending: int = 256):
        self.write_fn = write_fn
        self.pending = []                 # (op, addr, value, tag)
        self.values: dict = {}            # addr -> last value reported by the device
        self.lane_info: dict = {}         # lane -> raw CAL_LANE_INFO
        self.errors = []                  # (op, addr, value, tag) of requests answered with REG ERR
        self.unexpected = 0               # replies with no outstanding request / address mismatch
        self.max_pending = max_pending

    def _send(self, op, addr, value, tag, data):
        if len(self.pending) >= self.max_pending:
            raise RegisterCommandError("too many outstanding REG requests (device not answering?)")
        self.pending.append((op, addr, value, tag))
        self.write_fn(data)

    def write(self, addr: int, value: int, tag=None) -> None:
        self._send("W", addr, value, tag, format_write(addr, value))

    def read(self, addr: int, tag=None) -> None:
        self._send("R", addr, None, tag, format_read(addr))

    def read_all(self, addresses, *, lanes: int = 8) -> None:
        """Read every address, then CAL_LANE_INFO of every lane (restoring CAL_LANE afterwards)."""
        for a in addresses:
            self.read(a)
        if lanes:
            restore = self.values.get(self.LANE_SELECT_ADDR, 0)
            for lane in range(lanes):
                self.write(self.LANE_SELECT_ADDR, lane, tag=("lane_select", lane))
                self.read(self.LANE_INFO_ADDR, tag=("lane", lane))
            self.write(self.LANE_SELECT_ADDR, restore & 0x7, tag=("lane_select", restore & 0x7))

    def on_reply(self, reply: RegisterReply):
        """Consume one reply; returns the matched request tuple (or None)."""
        req = self.pending.pop(0) if self.pending else None
        if req is None:
            self.unexpected += 1
            if reply.ok:
                self.values[reply.addr] = reply.value
            return None
        if reply.error:
            self.errors.append(req)
            return req
        op, addr, value, tag = req
        if reply.addr != addr:
            self.unexpected += 1
        self.values[reply.addr] = reply.value
        if isinstance(tag, tuple) and tag[0] == "lane" and reply.addr == self.LANE_INFO_ADDR:
            self.lane_info[tag[1]] = reply.value
        return req
