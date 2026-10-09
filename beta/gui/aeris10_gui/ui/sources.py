"""Data sources feeding the main window: simulator (demo) or hardware."""
from __future__ import annotations

import logging
import time
from typing import Optional, Tuple

from ..io.ftdi_ft601 import FT601Interface, FT601NotAvailable
from ..io.usb_cdc import CdcSerialPort
from ..model import RadarSettings
from ..sim.simulator import RadarSimulator

log = logging.getLogger(__name__)


class DataSource:
    """``poll()`` returns ``(fpga_bytes, cdc_bytes)`` available since the last call."""
    name = "none"

    def start(self, settings: RadarSettings, *, pad_to_64: bool = False) -> None: ...
    def stop(self) -> None: ...
    def poll(self) -> Tuple[bytes, bytes]:
        return b"", b""


class DemoSource(DataSource):
    name = "DEMO (simulator)"

    def __init__(self, simulator: Optional[RadarSimulator] = None):
        self.sim = simulator if simulator is not None else RadarSimulator()
        self.running = False
        self.last_frame = None

    def start(self, settings: RadarSettings, *, pad_to_64: bool = False) -> None:
        self.sim.settings = settings
        self.sim.max_range_m = settings.max_distance
        self.running = True

    def stop(self) -> None:
        self.running = False

    def poll(self) -> Tuple[bytes, bytes]:
        if not self.running:
            return b"", b""
        self.last_frame = self.sim.next_frame(time.time())
        return self.last_frame.fpga_bytes, self.last_frame.status_bytes


class HardwareSource(DataSource):
    """STM32 CDC serial port + (unavailable) FT601.  UNVERIFIED with hardware."""
    name = "HARDWARE (STM32 CDC)"

    def __init__(self, port: str):
        self.port_name = port
        self.cdc: Optional[CdcSerialPort] = None
        self.fpga = FT601Interface()
        self.fpga_error: Optional[str] = None

    def start(self, settings: RadarSettings, *, pad_to_64: bool = False) -> None:
        self.cdc = CdcSerialPort(self.port_name)
        self.cdc.open()
        n = self.cdc.send_start_and_settings(settings, pad_to_64=pad_to_64)
        log.info("sent start flag + settings (%d bytes, pad_to_64=%s)", n, pad_to_64)
        try:
            self.fpga.open()
        except FT601NotAvailable as e:
            self.fpga_error = str(e)
            log.warning("%s", e)

    def stop(self) -> None:
        if self.cdc is not None:
            self.cdc.close()
            self.cdc = None
        self.fpga.close()

    def poll(self) -> Tuple[bytes, bytes]:
        cdc = self.cdc.read(4096) if self.cdc is not None and self.cdc.is_open else b""
        return b"", cdc
