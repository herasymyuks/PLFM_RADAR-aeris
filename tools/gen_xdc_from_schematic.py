#!/usr/bin/env python3
"""
gen_xdc_from_schematic.py — Build a candidate pin-constraint file for radar_system_top from
the Main Board EAGLE schematic (RADAR_Main_Board.sch, FPGA part U42).

Every PACKAGE_PIN written by this tool is taken verbatim from the schematic pad of the FPGA
symbol; the mapping "schematic net -> RTL port" is a documented, reviewable table (MAPPING
below) with a confidence level.  Ports that have no unambiguous net in the schematic are
emitted as commented-out lines marked UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION.
No pin number is ever invented.

The output is a NEW file; the original cntrt.xdc is never modified.

Usage:
    python3 tools/gen_xdc_from_schematic.py [--sch PATH] [--part U42] [--out FILE] [--table FILE.md]
Exit codes: 0 ok, 1 mapping problem (duplicate pad / missing net), 2 parse error.
Dependencies: Python 3.8+ standard library; tools/extract_eagle_netlist.py (same directory).
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_eagle_netlist import load, pad_map  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCH = ROOT / "4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch"

# (schematic net, RTL port, confidence, note)
# confidence: HIGH = same function & name; MEDIUM = name differs but function unambiguous;
#             LOW  = plausible only, designer must confirm.
MAPPING = [
    ("FPGA_SYS_CLOCK", "clk_100m", "MEDIUM", "MRCC clock-capable pin; 100 MHz supported by firmware AD9523 OUT6 'FPGA_SYSTEM_CLOCK' /36 (main.cpp:995-996), not by schematic alone"),
    ("FPGA_DAC_CLOCK", "clk_120m_dac", "MEDIUM", "MRCC clock-input pin; 120 MHz supported by firmware AD9523 OUT11 'FPGA_DAC' /30 (main.cpp:1025-1026). RTL output dac_clk has NO board pin (DAC clocked by AD9523 OUT10) — designer to confirm"),
    ("ADC_DCO_P", "adc_dco_p", "HIGH", ""), ("ADC_DCO_N", "adc_dco_n", "HIGH", ""),
    ("ADC_PWRD", "adc_pwdn", "HIGH", ""),
    ("DAC_SLEEP", "dac_sleep", "HIGH", ""),
    ("MIX_TX_EN", "tx_mixer_en", "HIGH", ""), ("MIX_RX_EN", "rx_mixer_en", "HIGH", ""),
    ("M3S_VCTRL", "fpga_rf_switch", "MEDIUM", "M3SWA2-34DR+ RF switch control net"),
    ("DIG_0", "stm32_new_chirp", "MEDIUM", "STM32 PD8 toggled as 'New chirp signal to FPGA' (main.cpp:448,459); schematic net DIG_0 = U2.PD8"),
    ("DIG_1", "stm32_new_elevation", "MEDIUM", "STM32 PD9 toggled 'Notify FPGA of elevation change' (main.cpp:484); DIG_1 = U2.PD9"),
    ("DIG_2", "stm32_new_azimuth", "MEDIUM", "STM32 PD10 toggled 'new azimuth' (main.cpp:514); DIG_2 = U2.PD10"),
    ("DIG_3", "stm32_mixers_enable", "MEDIUM", "STM32 PD11 'enable Mixers' (main.cpp:1483,1667,1714); DIG_3 = U2.PD11"),
    ("DIG_4", "reset_n", "MEDIUM", "STM32 PD12 pulsed low 10 ms as 'RESET FPGA' (main.cpp:1659-1662), active-low matches RTL reset_n; DIG_4 = U2.PD12"),
    ("STM32_SCLK1", "stm32_sclk_3v3", "HIGH", "shared with STM32 PA5 (SPI1_SCK)"),
    ("STM32_MOSI1", "stm32_mosi_3v3", "HIGH", "shared with STM32 PA7 (SPI1_MOSI)"),
    ("STM32_MISO1", "stm32_miso_3v3", "HIGH", "shared with STM32 PA6 (SPI1_MISO)"),
    ("STM32_SCLK_1V8", "stm32_sclk_1v8", "HIGH", ""), ("STM32_MOSI_1V8", "stm32_mosi_1v8", "HIGH", ""),
    ("STM32_MISO_1V8", "stm32_miso_1v8", "HIGH", ""),
] + [(f"ADC_D{i}_P", f"adc_d_p[{i}]", "HIGH", "") for i in range(8)] \
  + [(f"ADC_D{i}_N", f"adc_d_n[{i}]", "HIGH", "") for i in range(8)] \
  + [(f"DAC_{i}", f"dac_data[{i}]", "HIGH", "") for i in range(8)] \
  + [(f"ADAR_{i}_CS_3V3", f"stm32_cs_adar{i}_3v3", "HIGH", f"shared with STM32 PA{i-1}") for i in range(1, 5)] \
  + [(f"ADAR_{i}_CS_1V8", f"stm32_cs_adar{i}_1v8", "HIGH", "") for i in range(1, 5)] \
  + [(f"ADAR_TX_LOAD_{i}", f"adar_tx_load_{i}", "HIGH", "") for i in range(1, 5)] \
  + [(f"ADAR_RX_LOAD_{i}", f"adar_rx_load_{i}", "HIGH", "") for i in range(1, 5)] \
  + [(f"ADAR_TR_{i}", f"adar_tr_{i}", "HIGH", "") for i in range(1, 5)]

# RTL ports with no schematic counterpart (emitted commented-out)
UNRESOLVED = {
    "dac_clk": "RTL drives a DAC clock output, but the board clocks the AD9708 from AD9523 OUT10 (main.cpp:1019-1020); no FPGA net",
    "ft601_clk_in": "FT601Q-B-T (U6) is placed in the schematic but has 0 of 77 pins connected; its decoupling parts are parked outside the board outline",
    "ft601_data[*], ft601_be[*], ft601_txe_n, ft601_rxf_n, ft601_txe, ft601_rxf, ft601_wr_n, ft601_rd_n, ft601_oe_n, ft601_siwu_n, ft601_srb[*], ft601_swb[*], ft601_clk_out": "FT601 not wired on Main Board",
    "(DIG_5..DIG_7)": "schematic nets DIG_5/6/7 (STM32 PD13/14/15 configured as INPUTS in main.cpp:2313-2317) reach FPGA H11/G12/H12 but no RTL port uses them",
    "current_elevation[*], current_azimuth[*], current_chirp[*], new_chirp_frame": "no status outputs on the schematic",
    "dbg_doppler_data[*], dbg_doppler_valid, dbg_doppler_bin[*], dbg_range_bin[*], system_status[*]": "debug outputs; no schematic nets (internal-only in a real build; remove from top or leave unconstrained with -quiet)",
}

# I/O standard derived from the VCCO rail of the bank (from schematic power nets) — see table in output.
BANK_VCCO = {"14": "+3V3_FPGA", "15": "+3V3_FPGA", "34": "+1V8_FPGA", "35": "+3V3_FPGA"}


def bank_of(pin_name: str) -> str:
    return pin_name.rsplit("_", 1)[-1] if pin_name.startswith("IO_") else "0"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sch", default=DEFAULT_SCH)
    ap.add_argument("--part", default="U42")
    ap.add_argument("--out", default=ROOT / "9_Firmware/9_2_FPGA/reconstructed/radar_system_top_schematic_derived.xdc")
    ap.add_argument("--table", default=ROOT / "9_Firmware/9_2_FPGA/reconstructed/PIN_MAP_FROM_SCHEMATIC.md")
    args = ap.parse_args()
    root = load(Path(args.sch))
    parts = {p.get("name"): p for p in root.iter("part")}
    if args.part not in parts:
        print(f"ERROR: part {args.part} not in schematic", file=sys.stderr)
        return 2
    device = parts[args.part].get("deviceset")
    pads = pad_map(root, parts[args.part])
    net_of = {}
    for sheet in root.iter("sheet"):
        for net in sheet.iter("net"):
            for pr in net.iter("pinref"):
                if pr.get("part") == args.part:
                    key = (pr.get("gate"), pr.get("pin"))
                    net_of.setdefault(net.get("name"), []).append((pr.get("pin"), pads.get(key, "")))
    rc = 0
    lines, table = [], []
    lines += [
        "# ============================================================================",
        "# radar_system_top — CANDIDATE pin constraints DERIVED FROM SCHEMATIC",
        f"# Source   : {Path(args.sch).relative_to(ROOT)}  (part {args.part} = {device})",
        f"# Generated: {dt.date.today().isoformat()} by tools/gen_xdc_from_schematic.py",
        "# STATUS   : NOT VERIFIED ON HARDWARE. Each line cites the schematic net and FPGA pad.",
        "#            Review PIN_MAP_FROM_SCHEMATIC.md before use. Timing constraints are NOT",
        "#            included here — keep them in a separate file (see cntrt.xdc lines 14-27).",
        "# NOTE     : schematic device is XC7A50T-2FTG256I; RTL/README state XC7A100T.",
        "#            FTG256 ball names are shared across XC7A50T/XC7A100T but the part number",
        "#            used in Vivado MUST match the board (UNRESOLVED — designer to confirm).",
        "# ============================================================================", "",
    ]
    used_pads = {}
    for net, port, conf, note in MAPPING:
        hits = net_of.get(net)
        if not hits:
            lines.append(f"# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: net {net} not found for port {port}")
            table.append((port, net, "—", "—", "NOT FOUND", note)); rc = 1
            continue
        pin, pad = hits[0]
        if pad in used_pads:
            lines.append(f"# ERROR duplicate pad {pad} ({net} vs {used_pads[pad]})"); rc = 1
        used_pads[pad] = net
        bank = bank_of(pin)
        vcco = BANK_VCCO.get(bank, "?")
        if port.startswith("adc_d") or port.startswith("adc_dco"):
            iostd = "LVDS_25"
            iostd_note = f"bank {bank} VCCO={vcco}: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION"
        else:
            iostd = "LVCMOS18" if vcco == "+1V8_FPGA" else "LVCMOS33"
            iostd_note = f"bank {bank} VCCO={vcco}"
        lines.append(f"set_property PACKAGE_PIN {pad} [get_ports {{{port}}}]   ;# net {net}, pin {pin} [{conf}]")
        lines.append(f"set_property IOSTANDARD {iostd} [get_ports {{{port}}}]   ;# {iostd_note}")
        table.append((port, net, pad, pin, conf, (note + "; " if note else "") + iostd_note))
    lines += ["", "# ---------------- UNRESOLVED RTL PORTS (no schematic evidence) ----------------"]
    for ports, why in UNRESOLVED.items():
        lines.append(f"# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: {ports}")
        lines.append(f"#     reason: {why}")
    lines += ["", "# ---------------- schematic FPGA nets with NO RTL port ----------------"]
    mapped = {m[0] for m in MAPPING}
    for net, hits in sorted(net_of.items()):
        if net in mapped or net.startswith("+") or net == "GND" or net.startswith("N$"):
            continue
        for pin, pad in hits:
            lines.append(f"# {net:22s} pad {pad:4s} pin {pin}")
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    tbl = Path(args.table)
    with tbl.open("w") as f:
        f.write(f"# FPGA pin map derived from schematic ({device}, part {args.part})\n\n")
        f.write(f"Source: `{Path(args.sch).relative_to(ROOT)}`. Generated by `tools/gen_xdc_from_schematic.py`. ")
        f.write("Confidence refers to the net-name-to-RTL-port interpretation only; the pad is exact.\n\n")
        f.write("| RTL port | Schematic net | Pad | FPGA pin name | Confidence | Notes |\n|---|---|---|---|---|---|\n")
        for r in table:
            f.write("| " + " | ".join(f"`{x}`" if i in (0, 1, 2, 3) and x not in ("—",) else x for i, x in enumerate(r)) + " |\n")
        f.write("\n## Unresolved RTL ports\n\n| Ports | Reason |\n|---|---|\n")
        for ports, why in UNRESOLVED.items():
            f.write(f"| `{ports}` | {why} — **UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION** |\n")
    print(f"wrote {out.relative_to(ROOT)} ({len(table)} mapped ports) and {tbl.relative_to(ROOT)}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
