"""FT601 (USB 3.0 FIFO bridge) transport -- intentionally not implemented.

Hardware evidence (``docs/PCB/MAIN_BOARD.md``, ``docs/GUI/DEPENDENCIES.md``
section 4): the Main Board schematic contains an FT601 whose FIFO bus is
**not connected** to the FPGA, and no FT2232H at all.  The RTL packetizer
(``usb_data_interface.v``) therefore has no physical path to the host today.
Additionally ``pyftdi`` (used by GUI_V2..V5) does not support the FT60x family;
FT60x devices need FTDI's proprietary D3XX driver and its Python binding.

This module exists so the application has a single, explicit place that
explains why FPGA data cannot be received, instead of silently returning mock
devices as ``GUI_V5.FTDIInterface.list_devices`` did (``GUI_V5.py:502``).
"""
from __future__ import annotations

from typing import List

FT601_VID = 0x0403
FT601_PIDS = (0x6030, 0x6031)      # GUI_V6.py:119-122

NOT_WIRED_MESSAGE = (
    "FT601 data path is not available: on the AERIS-10 Main Board the FT601 "
    "FIFO bus is not wired to the FPGA (docs/PCB/MAIN_BOARD.md), and pyftdi "
    "cannot drive FT60x parts (FTDI D3XX driver required). Use --demo for the "
    "simulated FPGA stream, or capture a byte stream from an RTL simulation "
    "and replay it with sim.replay."
)


class FT601NotAvailable(NotImplementedError):
    pass


class FT601Interface:
    """Placeholder implementing the ``PacketSource`` shape used by the UI."""

    def __init__(self, *args, **kwargs):
        self.is_open = False

    @staticmethod
    def list_devices() -> List[dict]:
        return []           # never mock devices

    def open(self) -> None:
        raise FT601NotAvailable(NOT_WIRED_MESSAGE)

    def read(self, size: int = 4096) -> bytes:
        raise FT601NotAvailable(NOT_WIRED_MESSAGE)

    def close(self) -> None:
        self.is_open = False
