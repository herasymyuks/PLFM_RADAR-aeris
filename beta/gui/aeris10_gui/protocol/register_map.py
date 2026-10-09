"""FPGA control/status register map -- transcribed from the RTL.

Source of truth: ``beta/fpga/rtl/radar_control_regs.v`` (address map comment
block and the two ``case`` statements).  Registers are **16 bits** wide,
4-bit word addresses.

DISCREPANCY (recorded 2026-10-09): ``engineering/DESIGN/HOST_LINK/
HOST_LINK_DESIGN.md`` section 7 describes 32-bit registers with a different
layout (0x0 "run/long_chirp/mixers", 0x2 "NCO tuning word", 0x4 packed
calibration control, 0x5/0x7/0x8..0xC status).  That table says "the RTL owner
keeps this table in sync" -- it is not in sync with the RTL.  This module
follows the RTL; the GUI labels say so.  Fields that only exist in the design
note (run, mixers enable, NCO word, "auto blind" calibration) are **not**
offered because no RTL implements them.

Bridge transport note: the SPI command set (section 7) carries 32-bit values;
the upper 16 bits are ignored by / read as zero from this register file.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

REG_WIDTH_BITS = 16
REG_MASK = 0xFFFF
ADDR_MASK = 0xF


@dataclass(frozen=True)
class Field:
    name: str
    lsb: int
    width: int
    desc: str
    kind: str = "level"          # level | toggle (write-1-to-toggle, reads 0) | ro

    @property
    def mask(self) -> int:
        return ((1 << self.width) - 1) << self.lsb

    def get(self, value: int) -> int:
        return (value & self.mask) >> self.lsb

    def put(self, value: int, field_value: int) -> int:
        if field_value < 0 or field_value >= (1 << self.width):
            raise ValueError(f"{self.name}={field_value} does not fit {self.width} bits")
        return (value & ~self.mask) | (field_value << self.lsb)


@dataclass(frozen=True)
class Register:
    addr: int
    name: str
    access: str                  # rw | ro
    reset: int
    desc: str
    fields: Tuple[Field, ...] = ()

    def decode(self, value: int) -> Dict[str, int]:
        return {f.name: f.get(value) for f in self.fields}

    def encode(self, **fields: int) -> int:
        v = 0
        for f in self.fields:
            if f.name in fields:
                v = f.put(v, fields.pop(f.name))
        if fields:
            raise ValueError(f"unknown fields for {self.name}: {sorted(fields)}")
        return v


# radar_control_regs.v -- address map
REGISTERS: Dict[int, Register] = {r.addr: r for r in (
    Register(0x0, "CONTROL", "rw", 0b101, "receiver control",
             (Field("use_long_chirp", 0, 1, "1 = long chirp reference (reset 1)"),
              Field("adc_pwdn", 1, 1, "AD9484 power-down (reset 0)"),
              Field("usb_enable", 2, 1, "enable usb_data_interface output (reset 1)"))),
    Register(0x1, "CFAR_THR", "rw", 10000, "|I|+|Q| detection threshold (16 bit; 10000 = original placeholder)",
             (Field("threshold", 0, 16, "|I|+|Q| threshold"),)),
    Register(0x2, "DECIM", "rw", 0b01, "range decimation mode", (Field("mode", 0, 2, "01 = peak"),)),
    Register(0x3, "START_BIN", "rw", 0, "first range bin passed to the decimator", (Field("start_bin", 0, 10, ""),)),
    Register(0x4, "CAL_CTRL", "rw", 0, "ADC capture calibration control (bits 0..2 write-1-to-toggle, read as 0)",
             (Field("auto_start", 0, 1, "write 1: start auto (pattern) calibration", "toggle"),
              Field("manual_load", 1, 1, "write 1: load CAL_TAP into lane CAL_LANE", "toggle"),
              Field("bitslip_load", 2, 1, "write 1: issue CAL_SLIP BITSLIP pulses to lane CAL_LANE", "toggle"),
              Field("check_en", 3, 1, "level: pattern-check error counting"))),
    Register(0x5, "CAL_LANE", "rw", 0, "lane for CAL_TAP/CAL_SLIP writes and CAL_LANE_INFO read", (Field("lane", 0, 3, "0..7"),)),
    Register(0x6, "CAL_TAP", "rw", 16, "manual IDELAY tap (reset 16)", (Field("tap", 0, 5, "0..31, 78 ps each"),)),
    Register(0x7, "CAL_SLIP", "rw", 0, "BITSLIP pulses for a manual bitslip load", (Field("bitslip", 0, 2, "0..3"),)),
    Register(0x8, "CAL_PATT", "rw", 0x55AA, "expected alternating ADC test codes {pattern_b, pattern_a}",
             (Field("pattern_a", 0, 8, ""), Field("pattern_b", 8, 8, ""))),
    Register(0x9, "CAL_STAT", "ro", 0, "{fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}",
             (Field("lock", 0, 8, "per-lane lock mask", "ro"), Field("done", 8, 1, "", "ro"),
              Field("busy", 9, 1, "", "ro"), Field("align_fail", 10, 1, "", "ro"),
              Field("fifo_ovf", 15, 1, "", "ro"))),
    Register(0xA, "CAL_LANE_INFO", "ro", 0, "{1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]} of lane CAL_LANE",
             (Field("tap", 0, 5, "chosen tap", "ro"), Field("win_lo", 5, 5, "", "ro"), Field("win_hi", 10, 5, "", "ro"))),
    Register(0xB, "CAL_ERR", "ro", 0, "pattern-check error counter (saturating)", (Field("errors", 0, 16, "", "ro"),)),
    Register(0xC, "CAL_UNDET", "ro", 0, "{8'b0, undetermined[7:0]}", (Field("undetermined", 0, 8, "lanes constant in pattern", "ro"),)),
    Register(0xF, "ID", "ro", 0xBE7A, "beta build identifier", (Field("id", 0, 16, "", "ro"),)),
)}

READ_ALL_ADDRESSES: List[int] = sorted(REGISTERS)
# addresses not in the map read as 0 and ignore writes (RTL default arms)
UNMAPPED_ADDRESSES = [a for a in range(16) if a not in REGISTERS]


def register(addr: int) -> Register:
    try:
        return REGISTERS[addr]
    except KeyError:
        raise KeyError(f"register {addr:#x} is not in radar_control_regs.v") from None


def decode(addr: int, value: int) -> Dict[str, int]:
    return register(addr).decode(value & REG_MASK)


def describe_cal_stat(value: int) -> str:
    f = decode(0x9, value)
    lanes = "".join("L" if f["lock"] >> i & 1 else "." for i in range(8))
    return (f"lock[7..0]={lanes[::-1]} ({f['lock']:#04x}) done={f['done']} busy={f['busy']} "
            f"align_fail={f['align_fail']} fifo_ovf={f['fifo_ovf']}")
