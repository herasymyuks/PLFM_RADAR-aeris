"""In-memory model of ``radar_control_regs.v`` for demo mode.

Semantics copied from the RTL: 16-bit registers, reset values, write arms
(``case (reg_addr)`` in the write block: only the listed bit ranges are
stored), read arms (unmapped addresses read 0), CAL_CTRL bits 0..2 are
write-1-to-toggle and read back as 0, bit 3 is a level.  The calibration
*behaviour* (what ``adc_capture_calib.v`` would report) is a plain simulation:
an auto-start marks all lanes locked with a 12-tap window centred on tap 16,
pattern-check errors accumulate only when ``check_en`` is set and the
pattern register differs from the simulated ADC pattern 0x55AA.  Blind method
(CAL_CTRL bit4): the simulated minimum blind metric per lane is 0x0120 with
the default coefficient and grows with the coefficient's distance from the
default (a mistuned IF gives a worse notch).
"""
from __future__ import annotations

from typing import Dict, Optional

from ..protocol import register_cmd as rc
from ..protocol.register_map import REGISTERS, REG_MASK, ADDR_MASK

SIM_ADC_PATTERN = 0x55AA
SIM_WINDOW = (10, 22)             # (win_lo, win_hi) taps for every lane after auto calibration


class DemoRegisterFile:
    def __init__(self):
        self.regs: Dict[int, int] = {a: r.reset for a, r in REGISTERS.items() if r.access == "rw"}
        self.regs[0x4] = 0                       # toggles read as 0; check_en level kept separately
        self.check_en = 0
        self.blind = 0
        self.blind_min = [0] * 8
        self.toggles = {"auto_start": 0, "manual_load": 0, "bitslip_load": 0}
        self.lane_tap = [16] * 8                 # DEFAULT_TAP
        self.lane_window = [(0, 0)] * 8
        self.lock = 0
        self.done = 0
        self.busy = 0
        self.align_fail = 0
        self.fifo_ovf = 0
        self.undetermined = 0
        self.err_count = 0
        self.writes = 0
        self.reads = 0

    # --- RTL-equivalent access ------------------------------------------------------------
    def write(self, addr: int, value: int) -> None:
        addr &= ADDR_MASK
        value &= REG_MASK
        self.writes += 1
        if addr == 0x0:
            self.regs[0x0] = value & 0x7
        elif addr == 0x1:
            self.regs[0x1] = value
        elif addr == 0x2:
            self.regs[0x2] = value & 0x3
        elif addr == 0x3:
            self.regs[0x3] = value & 0x3FF
        elif addr == 0x4:
            if value & 1:
                self.toggles["auto_start"] ^= 1
                self._auto_calibrate()
            if value & 2:
                self.toggles["manual_load"] ^= 1
                self.lane_tap[self.regs[0x5]] = self.regs[0x6]
            if value & 4:
                self.toggles["bitslip_load"] ^= 1
            self.check_en = (value >> 3) & 1
            self.blind = (value >> 4) & 1
        elif addr == 0x5:
            self.regs[0x5] = value & 0x7
        elif addr == 0x6:
            self.regs[0x6] = value & 0x1F
        elif addr == 0x7:
            self.regs[0x7] = value & 0x3
        elif addr == 0x8:
            self.regs[0x8] = value
        elif addr == 0xD:
            self.regs[0xD] = value
        elif addr == 0xE:
            self.regs[0xE] = value
        # 0x9..0xC, 0xF, 0x10 and unmapped: ignored (RTL default arm)

    def read(self, addr: int) -> int:
        addr &= ADDR_MASK
        self.reads += 1
        if addr == 0x4:
            return (self.blind << 4) | (self.check_en << 3)
        if addr == 0x9:
            return (self.fifo_ovf << 15) | (self.align_fail << 10) | (self.busy << 9) | (self.done << 8) | (self.lock & 0xFF)
        if addr == 0xA:
            lane = self.regs[0x5]
            lo, hi = self.lane_window[lane]
            return (hi << 10) | (lo << 5) | (self.lane_tap[lane] & 0x1F)
        if addr == 0xB:
            return min(self.err_count, 0xFFFF)
        if addr == 0xC:
            return self.undetermined & 0xFF
        if addr == 0xF:
            return 0xBE7A
        if addr == 0x10:
            return self.blind_min[self.regs[0x5]]
        return self.regs.get(addr, 0)

    # --- simulated calibration behaviour -----------------------------------------------------
    def _auto_calibrate(self) -> None:
        lo, hi = SIM_WINDOW
        if self.blind:
            # blind method: window narrows as the notch coefficient departs from the default IF
            detune = abs(((self.regs[0xD] ^ 0x8000) - (0xEC39 ^ 0x8000))) >> 9      # 0 at default
            lo, hi = min(lo + detune, 15), max(hi - detune, 17)
            self.blind_min = [0x0120 + 0x40 * detune] * 8
        self.lane_window = [(lo, hi)] * 8
        self.lane_tap = [(lo + hi) // 2] * 8
        self.lock, self.done, self.busy, self.align_fail, self.undetermined = 0xFF, 1, 0, 0, 0

    def on_frame(self) -> None:
        """Called once per simulated frame: pattern-check errors when enabled and pattern mismatches."""
        if self.check_en and self.regs[0x8] != SIM_ADC_PATTERN:
            self.err_count = min(self.err_count + 1, 0xFFFF)

    # --- convenience views used by the simulator -----------------------------------------------
    @property
    def use_long_chirp(self) -> bool:
        return bool(self.regs[0x0] & 1)

    @property
    def cfar_threshold(self) -> int:
        return self.regs[0x1]

    # --- ASCII command handling (device side, mirrors hb_cmd_execute) -------------------------
    def handle_line(self, line: str) -> bytes:
        """One firmware-style execution: parse, SPI access, reply.

        A write replies with the *written* value (``hb_cmd_execute`` echoes
        ``c.value``); the FPGA bridge would NACK nothing for an unmapped
        address, but the demo returns ``REG ERR`` for addresses outside the
        register file so the GUI can see the difference.
        """
        try:
            op, addr, value = rc.parse_command(line)
        except rc.RegisterCommandError:
            return rc.format_error()
        if addr > ADDR_MASK or (addr not in REGISTERS):
            return rc.format_error()
        if op == "W":
            self.write(addr, value)
            return rc.format_reply(addr, value)
        return rc.format_reply(addr, self.read(addr))

    def handle_transfer(self, data: bytes) -> bytes:
        """``captureTextCommand`` + ``hb_cmd_execute`` for ONE USB transfer: only the first line counts."""
        if not rc.is_text_command(data):
            return b""
        return self.handle_line(data.decode("latin-1"))

    def handle_stream(self, data: bytes) -> bytes:
        """Convenience for tests: execute every line as if each arrived in its own transfer."""
        out = bytearray()
        for line in data.decode("latin-1").splitlines():
            if line.strip():
                out += self.handle_line(line)
        return bytes(out)
