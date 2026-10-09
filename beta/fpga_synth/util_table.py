#!/usr/bin/env python3
"""util_table.py - turn a Yosys `stat -tech xilinx` report into an XC7A50T utilisation table.

Usage: python3 util_table.py reports/yosys_stat.txt > reports/utilisation_xc7a50t.md
Exit: 0 ok, 1 parse error. Dependencies: Python 3 standard library only.
Budget (XC7A50T): AMD/Xilinx DS180 "7 Series FPGAs Data Sheet: Overview", Table 3 (Artix-7):
  Slices 8,150 (4 LUT6 + 8 FF each -> 32,600 LUTs, 65,200 FFs), distributed RAM 600 kb,
  DSP48E1 slices 120, block RAM 75 x 36 kb (= 150 x 18 kb, 2,700 kb), CMTs 5.
Open-source estimate only (Yosys synth_xilinx); not a Vivado utilisation report.
"""
import re, sys
from collections import OrderedDict

BUDGET = {"LUT": 32600, "FF": 65200, "DSP48E1": 120, "BRAM36": 75, "MMCM/PLL": 5,
          "BUFG": 32, "CARRY4": 8150}
def main(path):
    txt = open(path).read()
    # the flat top-level section is the last "=== radar_system_top ===" block
    blk = txt.split("=== radar_system_top ===")[-1]
    cells = OrderedDict()
    for m in re.finditer(r"^\s+(\d+)\s+(?:[\d.]+\s+)?([A-Za-z_$][\w$]*)\s*$", blk, re.M):
        cells[m.group(2)] = cells.get(m.group(2), 0) + int(m.group(1))
    if not cells:
        print("ERROR: no cells parsed", file=sys.stderr); return 1
    g = lambda *names: sum(cells.get(n, 0) for n in names)
    luts = g("LUT1","LUT2","LUT3","LUT4","LUT5","LUT6")
    # LUTs consumed by distributed RAM primitives (UG474: RAM32M/RAM64M = 4 LUTs, RAMxxX1D = 2 per 64 bits)
    lutram = 4*g("RAM32M","RAM64M") + 2*g("RAM32X1D","RAM64X1D") + 4*g("RAM128X1D") + g("RAM32X1S","RAM64X1S") + 2*g("RAM128X1S") + 4*g("RAM256X1S")
    srl = g("SRL16E","SRLC32E","SRLC16E")
    ffs = g("FDRE","FDSE","FDCE","FDPE","FDRE_1","FDCE_1","FDPE_1","FDSE_1")
    lat = g("LDCE","LDPE")
    dsp = g("DSP48E1")
    b36, b18 = g("RAMB36E1"), g("RAMB18E1")
    rows = [
        ("LUT total (logic + distributed RAM + SRL)", luts + lutram + srl, "LUT"),
        ("  of which logic LUT1..LUT6", luts, None),
        ("  of which distributed RAM (RAM64M/RAM32M x 4 LUTs)", lutram, None),
        ("  of which shift register (SRL16E/SRLC32E)", srl, None),
        ("INV cells (absorbed into LUTs by P&R, not counted)", g("INV"), None),
        ("Flip-flops (FDRE/FDSE/FDCE/FDPE, incl. _1 falling-edge)", ffs, "FF"),
        ("Latches (LDCE/LDPE)", lat, None),
        ("DSP48E1", dsp, "DSP48E1"),
        ("RAMB36E1", b36, None),
        ("RAMB18E1", b18, None),
        ("BRAM in 36 kb equivalents (RAMB36 + RAMB18/2)", b36 + b18/2, "BRAM36"),
        ("CARRY4", g("CARRY4"), "CARRY4"),
        ("MUXF7 / MUXF8", g("MUXF7")+g("MUXF8"), None),
        ("BUFG / BUFGCTRL", g("BUFG","BUFGCTRL"), "BUFG"),
        ("BUFIO / BUFR", g("BUFIO")+g("BUFR"), None),
        ("MMCME2_BASE/ADV, PLLE2", g("MMCME2_BASE","MMCME2_ADV","PLLE2_BASE","PLLE2_ADV"), "MMCM/PLL"),
        ("IBUF / IBUFG / IBUFDS", g("IBUF","IBUFG","IBUFDS"), None),
        ("OBUF / OBUFT / IOBUF", g("OBUF","OBUFT","IOBUF"), None),
        ("IDELAYE2 / IDELAYCTRL", g("IDELAYE2")+g("IDELAYCTRL"), None),
        ("ISERDESE2 / IDDR", g("ISERDESE2")+g("IDDR"), None),
        ("FFT IP black boxes (not counted above)", g("XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README","FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README"), None),
    ]
    print("| Resource | Yosys count | XC7A50T budget | Utilisation |")
    print("|---|---:|---:|---:|")
    for name, n, key in rows:
        if key:
            b = BUDGET[key]; print(f"| {name} | {n:g} | {b:,} | {100.0*n/b:.1f} % |")
        else:
            print(f"| {name} | {n:g} | - | - |")
    print()
    print("All cell types (flat netlist):")
    print()
    print("| Cell | Count |"); print("|---|---:|")
    for k, v in sorted(cells.items(), key=lambda kv: -kv[1]):
        print(f"| `{k}` | {v} |")
    return 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
