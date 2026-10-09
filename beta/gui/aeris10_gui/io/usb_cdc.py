"""STM32 USB CDC-ACM transport.

Behavioural change versus ``GUI_V5.STM32USBInterface`` (``GUI_V5.py:307-477``):
V5 claimed USB interface (0,0) with pyusb and used its bulk endpoints.  On a
CDC-ACM device interface 0 is the *communications* (control) interface; the
bulk data endpoints live on the *data* interface, and on Windows/macOS/Linux
the kernel class driver already exposes the device as a serial port.  The beta
therefore opens the OS serial port with **pyserial** (``CdcSerialPort``).  A
pyusb fallback (``PyUsbCdc``) is kept for systems without a CDC driver; it
selects the CDC *data* interface (bInterfaceClass 0x0A) rather than (0,0).

Neither path has been verified against the AERIS-10 board (the firmware RX
path itself is reported dead in ``docs/STM32``).  Default write framing does
not zero-pad (see ``protocol.settings_packet``).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from ..model import RadarSettings
from ..protocol.settings_packet import build_start_sequence
from ..protocol import register_cmd as rc

log = logging.getLogger(__name__)

STM32_VID = 0x0483
# GUI_V5.py:323-330 -- PIDs the original GUI searched for
STM32_PIDS = (0x5740, 0x3748, 0x374B, 0x374D, 0x374E, 0x3752)

try:
    import serial                       # pyserial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:                      # pragma: no cover
    serial = None
    SERIAL_AVAILABLE = False

try:
    import usb.core                     # pyusb
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:                      # pragma: no cover
    PYUSB_AVAILABLE = False


@dataclass
class PortInfo:
    device: str
    description: str
    vid: Optional[int] = None
    pid: Optional[int] = None

    @property
    def is_stm32(self) -> bool:
        return self.vid == STM32_VID


def list_ports(stm32_only: bool = False) -> List[PortInfo]:
    """Enumerate serial ports.  Never returns mock devices (V5 did, masking failures)."""
    if not SERIAL_AVAILABLE:
        raise ImportError("pyserial is not installed: pip install pyserial")
    ports = [PortInfo(p.device, p.description or "", p.vid, p.pid)
             for p in serial.tools.list_ports.comports()]
    if stm32_only:
        ports = [p for p in ports if p.is_stm32]
    return ports


class _RegisterCommandsMixin:
    """REG W / REG R text commands (HOST_LINK_DESIGN.md section 7), same connection as the settings packet.

    Replies (``REG <addr> <value>`` / ``REG ERR``) arrive asynchronously in the
    status stream; decode them with ``protocol.status_text.StatusStreamParser``.
    """

    def send_register_write(self, addr: int, value: int) -> int:
        return self.write(rc.format_write(addr, value))

    def send_register_read(self, addr: int) -> int:
        return self.write(rc.format_read(addr))


class CdcSerialPort(_RegisterCommandsMixin):
    """Serial-port view of the STM32 CDC link.

    Baud rate is irrelevant for a CDC-ACM virtual port but must be given to
    pyserial; 115200 is a placeholder.
    """

    def __init__(self, port: str, *, timeout: float = 0.1, baudrate: int = 115200):
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial is not installed: pip install pyserial")
        self.port_name = port
        self.timeout = timeout
        self.baudrate = baudrate
        self._ser: Optional["serial.Serial"] = None

    @property
    def is_open(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def open(self) -> None:
        self._ser = serial.Serial(self.port_name, baudrate=self.baudrate, timeout=self.timeout,
                                  write_timeout=1.0)
        log.info("opened CDC port %s", self.port_name)

    def close(self) -> None:
        if self._ser is not None:
            try:
                self._ser.close()
            finally:
                self._ser = None

    def write(self, data: bytes) -> int:
        if not self.is_open:
            raise IOError("port not open")
        return self._ser.write(data)

    def read(self, size: int = 512) -> bytes:
        if not self.is_open:
            raise IOError("port not open")
        waiting = self._ser.in_waiting
        return self._ser.read(max(1, min(size, waiting)) if waiting else size) if waiting else b""

    def send_start_and_settings(self, settings: RadarSettings, *, pad_to_64: bool = False) -> int:
        """Start flag then 82-byte settings packet (firmware order).  Returns bytes written."""
        n = 0
        for chunk in build_start_sequence(settings, pad_to_64=pad_to_64):
            n += self.write(chunk)
        self._ser.flush()
        return n


class PyUsbCdc(_RegisterCommandsMixin):
    """Raw-bulk fallback (pyusb/libusb).  UNVERIFIED.  Prefer :class:`CdcSerialPort`."""

    CDC_DATA_CLASS = 0x0A

    def __init__(self, vid: int = STM32_VID, pid: Optional[int] = None):
        if not PYUSB_AVAILABLE:
            raise ImportError("pyusb is not installed: pip install pyusb (needs libusb-1.0)")
        self.vid, self.pid = vid, pid
        self.dev = None
        self.ep_in = self.ep_out = None
        self._intf = None

    @property
    def is_open(self) -> bool:
        return self.dev is not None

    def open(self) -> None:
        kwargs = {"idVendor": self.vid}
        if self.pid is not None:
            kwargs["idProduct"] = self.pid
        dev = usb.core.find(**kwargs)
        if dev is None:
            raise IOError("no STM32 USB device found")
        cfg = dev.get_active_configuration()
        data_intf = next((i for i in cfg if i.bInterfaceClass == self.CDC_DATA_CLASS), None)
        if data_intf is None:
            raise IOError("device has no CDC data interface (class 0x0A)")
        try:
            if dev.is_kernel_driver_active(data_intf.bInterfaceNumber):
                dev.detach_kernel_driver(data_intf.bInterfaceNumber)
        except (NotImplementedError, usb.core.USBError):
            pass
        usb.util.claim_interface(dev, data_intf.bInterfaceNumber)
        self.ep_out = usb.util.find_descriptor(
            data_intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.ep_in = usb.util.find_descriptor(
            data_intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        if self.ep_out is None or self.ep_in is None:
            raise IOError("CDC data interface has no bulk IN/OUT pair")
        self.dev, self._intf = dev, data_intf

    def close(self) -> None:
        if self.dev is not None:
            try:
                usb.util.release_interface(self.dev, self._intf.bInterfaceNumber)
                usb.util.dispose_resources(self.dev)
            finally:
                self.dev = None

    def write(self, data: bytes) -> int:
        return self.ep_out.write(data)

    def read(self, size: int = 512, timeout_ms: int = 100) -> bytes:
        try:
            return bytes(self.ep_in.read(size, timeout=timeout_ms))
        except usb.core.USBTimeoutError:
            return b""

    def send_start_and_settings(self, settings: RadarSettings, *, pad_to_64: bool = False) -> int:
        return sum(self.write(c) for c in build_start_sequence(settings, pad_to_64=pad_to_64))
