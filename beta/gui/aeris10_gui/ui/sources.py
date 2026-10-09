"""Data sources feeding the main window.

Two host-link variants (``engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md``):

* ``bridge`` (default, option B): the STM32 forwards range-Doppler frames from
  the FPGA SPI bridge over USB CDC, interleaved with ASCII status strings and
  ``REG`` replies.  One byte stream: ``BridgeStreamParser`` extracts frames and
  hands the rest to ``StatusStreamParser``.
* ``raw-ft601`` (option A, ``--raw-ft601``): raw 35-byte RTL packets from
  ``usb_data_interface.v`` over an FT601; status text still comes over CDC.
  In hardware mode this path is unavailable (FT601 unwired).

Every source returns a :class:`PollResult`; the decoding is done here by
:class:`LinkDecoder`, so demo and hardware share exactly the same parsers.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from ..io.ftdi_ft601 import FT601Interface, FT601NotAvailable
from ..io.usb_cdc import CdcSerialPort
from ..model import RadarSettings
from ..processing import FrameAssembler
from ..protocol import fpga_packet as fp
from ..protocol.bridge_frame import BridgeFrame, BridgeStreamParser
from ..protocol.status_text import StatusStreamParser
from ..sim.simulator import RadarSimulator

log = logging.getLogger(__name__)

LINK_BRIDGE = "bridge"
LINK_RAW_FT601 = "raw-ft601"
LINKS = (LINK_BRIDGE, LINK_RAW_FT601)


@dataclass
class PollResult:
    bridge_frames: List[BridgeFrame] = field(default_factory=list)
    raw_frames: list = field(default_factory=list)      # (iq ndarray, detection ndarray)
    messages: list = field(default_factory=list)        # SystemStatus | GPSData | RegisterReply


class LinkDecoder:
    """Byte streams -> frames + messages for one link variant."""

    def __init__(self, link: str = LINK_BRIDGE):
        if link not in LINKS:
            raise ValueError(f"unknown link {link!r}; expected one of {LINKS}")
        self.link = link
        self.status_parser = StatusStreamParser()
        self._text: List[bytes] = []
        self.bridge_parser = BridgeStreamParser(text_sink=self._text.append)
        self.fpga_parser = fp.FpgaPacketParser()
        self.assembler = FrameAssembler()

    def decode(self, cdc_bytes: bytes = b"", fpga_bytes: bytes = b"", timestamp: Optional[float] = None) -> PollResult:
        res = PollResult()
        if self.link == LINK_BRIDGE:
            res.bridge_frames = self.bridge_parser.feed(cdc_bytes) if cdc_bytes else []
            text, self._text[:] = b"".join(self._text), []
        else:
            text = cdc_bytes
            if fpga_bytes:
                res.raw_frames = self.assembler.feed(self.fpga_parser.feed(fpga_bytes))
        if text:
            res.messages = self.status_parser.feed(text, timestamp)
        return res

    def stats(self) -> dict:
        s = {"status": dict(self.status_parser.stats)}
        if self.link == LINK_BRIDGE:
            s["bridge"] = {"frames": self.bridge_parser.frames, "crc_errors": self.bridge_parser.crc_errors,
                           "resyncs": self.bridge_parser.resyncs}
        else:
            s["fpga"] = dict(self.fpga_parser.stats)
        return s

    def error_count(self) -> int:
        if self.link == LINK_BRIDGE:
            n = self.bridge_parser.crc_errors
        else:
            n = sum(v for k, v in self.fpga_parser.stats.items() if k.startswith("bad_") or k == "inconsistent_range_word")
        return n + self.status_parser.stats["errors"]

    def frames(self) -> int:
        return self.bridge_parser.frames if self.link == LINK_BRIDGE else self.assembler.frames_completed


class DataSource:
    name = "none"
    link = LINK_BRIDGE

    def __init__(self, link: str = LINK_BRIDGE):
        self.link = link
        self.decoder = LinkDecoder(link)

    def start(self, settings: RadarSettings, *, pad_to_64: bool = False) -> None: ...
    def stop(self) -> None: ...

    def send_line(self, data: bytes) -> None:
        """Send an ASCII command line (REG ...) on the CDC connection."""
        raise IOError("source not started")

    def poll(self) -> PollResult:
        return PollResult()


class DemoSource(DataSource):
    """Simulator; in bridge mode the CDC stream = bridge frame + status string + REG replies."""

    def __init__(self, simulator: Optional[RadarSimulator] = None, link: str = LINK_BRIDGE):
        super().__init__(link)
        self.sim = simulator if simulator is not None else RadarSimulator()
        self.name = f"DEMO (simulator, {link})"
        self.running = False
        self.last_frame = None
        self._reg_out = bytearray()
        self._cmd_slot: Optional[bytes] = None      # firmware single command slot (USBHandler::cmd_pending)
        self.dropped_commands = 0

    def start(self, settings: RadarSettings, *, pad_to_64: bool = False) -> None:
        self.sim.settings = settings
        self.sim.max_range_m = settings.max_distance
        self.running = True

    def stop(self) -> None:
        self.running = False

    def send_line(self, data: bytes) -> None:
        """Emulates the firmware: one transfer = one command; dropped while the previous one is pending;
        executed (and answered) at the next poll, i.e. the next main-loop iteration."""
        if not self.running:
            raise IOError("demo source not started")
        if not data.startswith(b"REG"):
            return                                  # not a text command: the settings state machine would see it
        if self._cmd_slot is not None:
            self.dropped_commands += 1
            return
        self._cmd_slot = bytes(data)

    def _execute_slot(self) -> None:
        if self._cmd_slot is not None:
            self._reg_out += self.sim.regs.handle_transfer(self._cmd_slot)
            self._cmd_slot = None

    def raw_cdc_chunk(self) -> bytes:
        """One poll worth of simulated CDC bytes (exposed for tests)."""
        self._execute_slot()
        replies, self._reg_out = bytes(self._reg_out), bytearray()
        if self.link == LINK_BRIDGE:
            self.last_frame, bf = self.sim.next_bridge_frame(time.time())
            from ..protocol.bridge_frame import build_frame
            return replies + self.last_frame.status_bytes + build_frame(bf)
        return replies

    def poll(self) -> PollResult:
        if not self.running:
            return PollResult()
        if self.link == LINK_BRIDGE:
            return self.decoder.decode(self.raw_cdc_chunk(), timestamp=time.time())
        self._execute_slot()
        replies, self._reg_out = bytes(self._reg_out), bytearray()
        self.last_frame = self.sim.next_frame(time.time())
        self.sim.regs.on_frame()
        return self.decoder.decode(replies + self.last_frame.status_bytes, self.last_frame.fpga_bytes, time.time())


class HardwareSource(DataSource):
    """STM32 CDC serial port (+ FT601 in raw mode, unavailable).  UNVERIFIED with hardware.

    ``cdc`` may be injected (any object with open/close/write/read/is_open and
    ``send_start_and_settings``) -- used by the tests with a fake port.
    """

    def __init__(self, port: Optional[str] = None, link: str = LINK_BRIDGE, cdc=None):
        super().__init__(link)
        self.name = f"HARDWARE (STM32 CDC, {link})"
        self.port_name = port
        self.cdc = cdc
        self.fpga = FT601Interface()
        self.fpga_error: Optional[str] = None

    def start(self, settings: RadarSettings, *, pad_to_64: bool = False) -> None:
        if self.cdc is None:
            if not self.port_name:
                raise IOError("no CDC port selected")
            self.cdc = CdcSerialPort(self.port_name)
        if not self.cdc.is_open:
            self.cdc.open()
        n = self.cdc.send_start_and_settings(settings, pad_to_64=pad_to_64)
        log.info("sent start flag + settings (%d bytes, pad_to_64=%s)", n, pad_to_64)
        if self.link == LINK_RAW_FT601:
            try:
                self.fpga.open()
            except FT601NotAvailable as e:
                self.fpga_error = str(e)
                log.warning("%s", e)

    def stop(self) -> None:
        if self.cdc is not None:
            self.cdc.close()
        self.fpga.close()

    def send_line(self, data: bytes) -> None:
        if self.cdc is None or not self.cdc.is_open:
            raise IOError("CDC port not open")
        self.cdc.write(data)

    def poll(self) -> PollResult:
        cdc = self.cdc.read(8192) if self.cdc is not None and self.cdc.is_open else b""
        return self.decoder.decode(cdc, b"", time.time())
