"""Notebook tab "FPGA registers / ADC calibration".

Register map = ``beta/fpga/rtl/radar_control_regs.v`` (see
``protocol.register_map``).  Fields requested from the design note but absent
from the RTL (run, mixers enable, NCO tuning word, blind calibration) are
listed as unavailable instead of being invented.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ..protocol import register_map as rm
from ..protocol.register_cmd import RegisterClient, RegisterCommandError
from .theme import DARK_FG, PLOT_BG

UNAVAILABLE_NOTE = (
    "Register map from beta/fpga/rtl/radar_control_regs.v (16-bit). HOST_LINK_DESIGN.md section 7 "
    "lists run / mixers enable / NCO tuning word / 32-bit packed CAL control -- NOT in the RTL, not offered. "
    "Blind calibration exists in adc_capture_calib.v (ctrl_blind) but no register drives it. "
    "radar_system_top.v ties reg_we/reg_addr/reg_wdata to 0: on the current RTL writes have no effect."
)


class RegisterPanel:
    def __init__(self, notebook: ttk.Notebook, get_client: Callable[[], Optional[RegisterClient]]):
        self.get_client = get_client
        tab = ttk.Frame(notebook, padding=8)
        notebook.add(tab, text="FPGA registers / ADC calibration")
        self.tab = tab
        ttk.Label(tab, text=UNAVAILABLE_NOTE, wraplength=1100, foreground="#f0a050").grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        ctl = ttk.LabelFrame(tab, text="Control (0x0 CONTROL, 0x1 CFAR_THR, 0x2 DECIM, 0x3 START_BIN)", padding=6)
        ctl.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.v_long = tk.BooleanVar(value=True)
        self.v_pwdn = tk.BooleanVar(value=False)
        self.v_usb = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctl, text="use_long_chirp (bit0)", variable=self.v_long).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(ctl, text="adc_pwdn (bit1)", variable=self.v_pwdn).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(ctl, text="usb_enable (bit2)", variable=self.v_usb).grid(row=2, column=0, sticky="w")
        ttk.Button(ctl, text="Write CONTROL", command=self.write_control).grid(row=0, column=1, padx=6)
        self.v_cfar = tk.StringVar(value="10000")
        self.v_decim = tk.StringVar(value="1")
        self.v_start = tk.StringVar(value="0")
        for r, (lbl, var, cmd) in enumerate([("CFAR threshold |I|+|Q|", self.v_cfar, lambda: self._write_entry(0x1, self.v_cfar)),
                                             ("Decimation mode (0..3)", self.v_decim, lambda: self._write_entry(0x2, self.v_decim)),
                                             ("Start bin (0..1023)", self.v_start, lambda: self._write_entry(0x3, self.v_start))], start=3):
            ttk.Label(ctl, text=lbl).grid(row=r, column=0, sticky="w", pady=2)
            ttk.Entry(ctl, textvariable=var, width=10).grid(row=r, column=1, padx=6)
            ttk.Button(ctl, text="Write", command=cmd).grid(row=r, column=2)

        cal = ttk.LabelFrame(tab, text="ADC calibration (0x4..0x8)", padding=6)
        cal.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        self.v_check = tk.BooleanVar(value=False)
        ttk.Button(cal, text="Auto calibration (pattern)", command=self.auto_pattern).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(cal, text="pattern check / error count (bit3)", variable=self.v_check,
                        command=self.write_check).grid(row=0, column=1, columnspan=2, sticky="w")
        ttk.Label(cal, text="Auto calibration (blind): not exposed by the register map").grid(row=1, column=0, columnspan=3, sticky="w")
        self.v_lane = tk.StringVar(value="0")
        self.v_tap = tk.StringVar(value="16")
        self.v_slip = tk.StringVar(value="0")
        self.v_patt = tk.StringVar(value="0x55AA")
        for r, (lbl, var, lo_hi) in enumerate([("Lane (0..7)", self.v_lane, "0..7"), ("Manual tap (0..31)", self.v_tap, "0..31"),
                                               ("Bitslip pulses (0..3)", self.v_slip, "0..3"),
                                               ("Pattern {B,A}", self.v_patt, "16 bit")], start=2):
            ttk.Label(cal, text=lbl).grid(row=r, column=0, sticky="w", pady=2)
            ttk.Entry(cal, textvariable=var, width=10).grid(row=r, column=1, padx=6)
        ttk.Button(cal, text="Load tap into lane", command=self.manual_tap).grid(row=2, column=2, rowspan=2, padx=4)
        ttk.Button(cal, text="Apply bitslip to lane", command=self.manual_bitslip).grid(row=4, column=2, padx=4)
        ttk.Button(cal, text="Write pattern", command=lambda: self._write_entry(0x8, self.v_patt)).grid(row=5, column=2, padx=4)

        st = ttk.LabelFrame(tab, text="Status (0x9 CAL_STAT, 0xA CAL_LANE_INFO per lane, 0xB CAL_ERR, 0xC CAL_UNDET, 0xF ID)", padding=6)
        st.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=4, pady=4)
        ttk.Button(st, text="Read all / refresh", command=self.read_all).pack(anchor="w")
        self.text = tk.Text(st, height=18, width=120, bg=PLOT_BG, fg=DARK_FG)
        self.text.pack(fill="both", expand=True)
        self.msg = ttk.Label(tab, text="")
        self.msg.grid(row=3, column=0, columnspan=2, sticky="w")
        self.render()

    # ---------------------------------------------------------------- commands
    def _client(self) -> Optional[RegisterClient]:
        c = self.get_client()
        if c is None:
            self.msg.config(text="Not connected: press Start first (REG commands share the CDC link).")
        return c

    def _int(self, var: tk.StringVar, lo: int, hi: int, name: str) -> Optional[int]:
        try:
            v = int(var.get(), 0)
        except ValueError:
            self.msg.config(text=f"{name}: not a number")
            return None
        if not lo <= v <= hi:
            self.msg.config(text=f"{name}: {v} outside {lo}..{hi}")
            return None
        return v

    def _do(self, fn) -> bool:
        c = self._client()
        if c is None:
            return False
        try:
            fn(c)
        except (RegisterCommandError, IOError) as e:
            self.msg.config(text=f"REG command failed: {e}")
            return False
        self.msg.config(text=f"sent; {len(c.pending)} reply(ies) outstanding")
        return True

    def _write_entry(self, addr: int, var: tk.StringVar) -> None:
        reg = rm.register(addr)
        width = sum(f.width for f in reg.fields)
        v = self._int(var, 0, (1 << max(width, 1)) - 1, reg.name)
        if v is not None:
            self._do(lambda c: (c.write(addr, v), c.read(addr)))

    def write_control(self) -> None:
        v = rm.register(0x0).encode(use_long_chirp=int(self.v_long.get()), adc_pwdn=int(self.v_pwdn.get()),
                                     usb_enable=int(self.v_usb.get()))
        self._do(lambda c: c.write(0x0, v))

    def _cal_ctrl(self, **toggles) -> int:
        return rm.register(0x4).encode(check_en=int(self.v_check.get()), **toggles)

    def write_check(self) -> None:
        self._do(lambda c: c.write(0x4, self._cal_ctrl()))

    def auto_pattern(self) -> None:
        self._do(lambda c: (c.write(0x4, self._cal_ctrl(auto_start=1)), c.read(0x9)))

    def manual_tap(self) -> None:
        lane, tap = self._int(self.v_lane, 0, 7, "lane"), self._int(self.v_tap, 0, 31, "tap")
        if lane is None or tap is None:
            return
        self._do(lambda c: (c.write(0x5, lane), c.write(0x6, tap), c.write(0x4, self._cal_ctrl(manual_load=1)),
                            c.read(0xA, tag=("lane", lane))))

    def manual_bitslip(self) -> None:
        lane, slip = self._int(self.v_lane, 0, 7, "lane"), self._int(self.v_slip, 0, 3, "bitslip")
        if lane is None or slip is None:
            return
        self._do(lambda c: (c.write(0x5, lane), c.write(0x7, slip), c.write(0x4, self._cal_ctrl(bitslip_load=1))))

    def read_all(self) -> None:
        self._do(lambda c: c.read_all(rm.READ_ALL_ADDRESSES))

    # ---------------------------------------------------------------- view
    def render(self) -> None:
        c = self.get_client()
        lines = []
        if c is None:
            lines.append("not connected")
        else:
            vals = c.values
            for addr in rm.READ_ALL_ADDRESSES:
                reg = rm.REGISTERS[addr]
                if addr in vals:
                    dec = ", ".join(f"{k}={v}" for k, v in reg.decode(vals[addr]).items())
                    lines.append(f"0x{addr:X} {reg.name:<13} {reg.access}  0x{vals[addr]:04X}  {dec}")
                else:
                    lines.append(f"0x{addr:X} {reg.name:<13} {reg.access}  ----")
            if 0x9 in vals:
                lines += ["", "CAL_STAT: " + rm.describe_cal_stat(vals[0x9])]
            if c.lane_info:
                lines.append("chosen taps / pass windows per lane:")
                for lane in sorted(c.lane_info):
                    f = rm.decode(0xA, c.lane_info[lane])
                    lines.append(f"  lane {lane}: tap={f['tap']:2d}  window=[{f['win_lo']:2d}, {f['win_hi']:2d}]")
            if 0xB in vals:
                lines.append(f"pattern-check errors (CAL_ERR): {vals[0xB]}")
            lines.append(f"outstanding requests: {len(c.pending)}   REG ERR replies: {len(c.errors)}   unmatched: {c.unexpected}")
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", "\n".join(lines) + "\n")
        self.text.configure(state="disabled")
