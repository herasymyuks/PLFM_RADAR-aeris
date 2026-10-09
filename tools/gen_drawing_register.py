#!/usr/bin/env python3
"""Drawing register for engineering/ — definition table + existence/validity check.

Writes engineering/DRAWING_REGISTER.md from the REGISTER table below and, with
--check, verifies that every native file and export exists, is non-empty and (for
SVG/DOT/PDF) is well-formed, appending the result to the register footer.
Usage: python3 tools/gen_drawing_register.py [--check] [--date YYYY-MM-DD]
Exit: 0 all registered files present and valid; 1 at least one missing/invalid; 2 error.
Stdlib only; non-destructive.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = "engineering"
BOARDS = ["MAIN_BOARD", "POWER_SUPPLY", "RF_PA", "FREQUENCY_SYNTHESIZER"]
BSRC = {"MAIN_BOARD": "MainBoard/RADAR_Main_Board", "POWER_SUPPLY": "PowerBoard/PowerBoard",
        "RF_PA": "PowerAmplifierBoard/RF_PA", "FREQUENCY_SYNTHESIZER": "FrequencySynthesizerBoard/Clocks_Freq_Synth_board"}
SCH = "4_Schematics and Boards Layout/4_6_Schematics/"
PCB_STATUS = {"MAIN_BOARD": ("PARTIAL", "layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs"),
              "POWER_SUPPLY": ("PARTIAL", "layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs"),
              "RF_PA": ("SOURCE-DERIVED", "stack-up/material, finish, tolerances, MPNs; designer review of DRC (48)"),
              "FREQUENCY_SYNTHESIZER": ("SOURCE-DERIVED", "stack-up/material, finish, tolerances, MPNs; designer review of DRC (639)")}

REGISTER: list[tuple] = []  # (ID, title, source, native, [exports], status, missing)


def add(i, t, s, n, x, st, m):
    REGISTER.append((i, t, s, n, x, st, m))


# --- electrical schematics
SHEETS = {"MAIN_BOARD": 4, "POWER_SUPPLY": 1, "RF_PA": 1, "FREQUENCY_SYNTHESIZER": 1}
for b in BOARDS:
    n = SHEETS[b]
    add(f"ELEC-SCH-{b}", f"Schematic set, {b} ({n} sheet{'s' if n > 1 else ''})", f"{SCH}{BSRC[b]}.sch (native EAGLE, editable)",
        f"{SCH}{BSRC[b]}.sch", [f"{E}/ELECTRICAL/schematics/{b}/{b}_schematic.pdf"] +
        [f"{E}/ELECTRICAL/schematics/{b}/svg/{b}_schematic_sheet{i}.svg" for i in range(1, n + 1)] +
        [f"{E}/ELECTRICAL/schematics/{b}/png/{b}_schematic_sheet{i}.png" for i in range(1, n + 1)],
        "SOURCE-DERIVED", "no revision in source; fonts differ from EAGLE; not reviewed against an EAGLE print")
    add(f"ELEC-NET-{b}", f"Netlist + component-to-net report, {b}", f"{SCH}{BSRC[b]}.sch",
        f"{E}/ELECTRICAL/netlists/{b}_netlist.csv",
        [f"{E}/ELECTRICAL/netlists/{b}_netlist_by_part.csv", f"{E}/ELECTRICAL/connection_diagrams/{b}_connection_report.md",
         f"{E}/ELECTRICAL/netlists/{b}_unresolved_connections.md", f"{E}/ELECTRICAL/netlists/{b}_missing_symbols_footprints.md",
         f"{E}/PCB/{b}/ipc/{b}_netlist.d356"],
        "SOURCE-DERIVED", "designer disposition of single-pin nets / unconnected pins")
add("ELEC-PWR-01", "Power distribution diagram + rail register", "PowerBoard.sch, Main/Synth/PA schematics, main.h/main.cpp, Power Management V6.xlsx",
    f"{E}/ELECTRICAL/power_distribution/power_distribution.dot",
    [f"{E}/ELECTRICAL/power_distribution/power_distribution.{x}" for x in ("svg", "pdf", "png")] + [f"{E}/ELECTRICAL/power_distribution/power_rails.md"],
    "SOURCE-DERIVED", "rail currents, VIN budget, 22 V PA supply (K4)")
# --- system
add("SYS-01", "System block diagram", "4 schematics, firmware, RADAR_V6.drawio, docs/SYSTEM/BLOCK_DIAGRAM.md",
    f"{E}/SYSTEM/block_diagrams/system_block_diagram.dot",
    [f"{E}/SYSTEM/block_diagrams/system_block_diagram.{x}" for x in ("svg", "pdf", "png", "mmd")], "SOURCE-DERIVED",
    "antenna, host, 22 V supply CONCEPTUAL; conflicts K1–K8 open")
add("SYS-02", "Hardware interconnection diagram + table", "connector nets of 4 schematics, .brd silkscreen, main.h",
    f"{E}/SYSTEM/interfaces/hardware_interconnection.dot",
    [f"{E}/SYSTEM/interfaces/hardware_interconnection.{x}" for x in ("svg", "pdf", "png")] + [f"{E}/SYSTEM/interfaces/interconnection_table.md"],
    "SOURCE-DERIVED", "cable types/lengths, Molex pin order, SMA RFIN/RFOUT side, PA instance mapping")
add("SYS-03", "Signal and data flow diagram", "schematics traced through passives; main.cpp:933-1072; adf4382a_manager.h; radar_system_top.v",
    f"{E}/SYSTEM/data_flow/signal_and_data_flow.dot", [f"{E}/SYSTEM/data_flow/signal_and_data_flow.{x}" for x in ("svg", "pdf", "png")],
    "SOURCE-DERIVED", "frequencies are firmware intent; BPF parts, antenna path, host data path (K3/K5)")
# --- software
SD = [("SD-01", "FPGA module hierarchy (auto)", "9_Firmware/9_2_FPGA/*.v via tools/gen_verilog_hierarchy.py", "FPGA/fpga_module_hierarchy", "SOURCE-DERIVED", "5 modules/IP missing from repo"),
      ("SD-02", "FPGA signal-processing pipeline", "radar_system_top.v and submodules", "FPGA/fpga_data_pipeline", "PARTIAL", "400 MHz capture, CFAR, host path not implemented"),
      ("SD-03", "STM32 firmware architecture", "main.cpp, main.h, LIB/*", "STM32/stm32_firmware_architecture", "PARTIAL", "HAL/CMSIS/startup/linker/USB middleware absent"),
      ("SD-04", "STM32 USB CDC flow", "main.cpp, USBHandler.cpp, GUI_V5.py", "STM32/stm32_usb_cdc_flow", "PARTIAL", "usbd_cdc_if.c missing; RX callback unbound"),
      ("SD-05", "Python GUI modules (auto)", "9_Firmware/9_3_GUI/*.py via tools/gen_python_module_graph.py", "PYTHON/python_gui_modules", "SOURCE-DERIVED", "GUI_V1.py syntax error"),
      ("SD-06", "Python GUI runtime architecture", "GUI_V5.py, GUI_V6_Demo.py", "PYTHON/python_gui_architecture", "SOURCE-DERIVED", "not executed"),
      ("SD-07", "End-to-end data flow", "docs/SYSTEM, docs/FPGA, docs/STM32, PIN_MAP_FROM_SCHEMATIC.md", "DATA_FLOW/end_to_end_data_flow", "PARTIAL", "FPGA→host path BLOCKED (FT601 unwired)")]
for i, t, s, base, st, m in SD:
    add(i, t, s, f"{E}/SOFTWARE_DIAGRAMS/{base}.dot", [f"{E}/SOFTWARE_DIAGRAMS/{base}.{x}" for x in ("svg", "pdf", "png")], st, m)
# --- PCB packages
for b in BOARDS:
    st, miss = PCB_STATUS[b]
    base = f"{E}/PCB/{b}"
    src = f"{SCH}{BSRC[b]}.brd (native EAGLE, editable)"
    kic = f"{base}/kicad/{b}.kicad_pcb"
    add(f"PCB-{b}-01", "Top-layer drawing", src, kic, [f"{base}/drawings/{b}_top_layer.pdf", f"{base}/svg/{b}_top_composite.svg"], st, miss)
    add(f"PCB-{b}-02", "Bottom-layer drawing (mirrored)", src, kic, [f"{base}/drawings/{b}_bottom_layer_mirrored.pdf", f"{base}/svg/{b}_bottom_composite_mirrored.svg"], st, miss)
    add(f"PCB-{b}-03", "Copper-layer views (one page per layer)", src, kic, [f"{base}/drawings/{b}_copper_layers.pdf"], st, miss)
    add(f"PCB-{b}-04", "Board-outline drawing", src, kic, [f"{base}/drawings/{b}_outline.pdf", f"{base}/svg/{b}-Edge_Cuts.svg"], "SOURCE-DERIVED", "thickness, tolerances")
    add(f"PCB-{b}-05", "Mechanical dimensions (DXF/STEP, hole table)", src, f"{E}/MECHANICAL/DXF/{b}_outline_holes_eagle.dxf",
        [f"{base}/mechanical/{b}_outline.dxf", f"{base}/mechanical/{b}_board_only.step", f"{E}/MECHANICAL/dimensions/{b}_dimensions.md"], "SOURCE-DERIVED", "thickness ASSUMED 1.6 mm; heights, mass")
    add(f"PCB-{b}-06", "Drill map + hole table + Excellon", src, kic, [f"{base}/drill/{b}-PTH-drl_map.pdf", f"{base}/drill/{b}-NPTH-drl_map.pdf", f"{base}/drill/{b}-PTH.drl", f"{base}/drill/{b}-NPTH.drl", f"{base}/drill/drill_report.txt"], st, miss)
    add(f"PCB-{b}-07", "Component placement / top assembly drawing", src, kic, [f"{base}/drawings/{b}_assembly_top.pdf", f"{base}/svg/{b}-F_Fab.svg"], st, miss)
    add(f"PCB-{b}-08", "Bottom assembly drawing (mirrored)", src, kic, [f"{base}/drawings/{b}_assembly_bottom_mirrored.pdf"], st, miss)
    add(f"PCB-{b}-09", "Fabrication package: Gerber set + stack-up document", src, kic, [f"{base}/gerber/{b}-job.gbrjob", f"{base}/gerber/{b}-F_Cu.gtl", f"{base}/gerber/{b}-B_Cu.gbl", f"{base}/gerber/{b}-Edge_Cuts.gm1", f"{base}/STACKUP.md"], "PARTIAL", "vendor notes: material, finish, thickness, impedance, tolerances")
    add(f"PCB-{b}-10", "BOM with references + pick-and-place", f"{SCH}{BSRC[b]}.sch / .brd", f"docs/BOM/BOM_{b}.csv", [f"{base}/assembly/{b}_BOM.csv", f"{base}/assembly/{b}_pick_and_place.csv"], "PARTIAL", "0 manufacturer part numbers in source")
    add(f"PCB-{b}-11", "DRC / IPC-2581 / 3-D renders / package README", src, kic, [f"{base}/reports/DRC_report.txt", f"{base}/README.md", f"{base}/3d/{b}_render_top.png", f"{base}/3d/{b}_render_isometric.png"], st, miss)
# --- mechanical & assembly
add("MECH-PLAN-01", "PCB set plan view 1:1", "4 × .brd layer 20 + holes", f"{E}/MECHANICAL/CAD/pcb_set_plan_view.svg",
    [f"{E}/MECHANICAL/PDF/pcb_set_plan_view.pdf", f"{E}/MECHANICAL/CAD/pcb_set_plan_view.png"], "SOURCE-DERIVED", "placement is for comparison only")
add("MECH-ENC-01", "Main enclosure drawings", "none (README references a non-existent 10_docs/Hardware/Enclosure)", "—", [], "BLOCKED — MISSING DATA", "all enclosure geometry (G-04)")
add("MECH-INT-01", "Internal component layout / cable routing", "none", "—", [], "BLOCKED — MISSING DATA", "board placement, stacking, harness (G-05, G-09)")
add("MECH-ANT-01", "Antenna assembly drawing", "02_hardware/04_antenna_beamforming.md (spacing only), photo", "—", [], "BLOCKED — MISSING DATA", "element geometry, feed, mounting (G-06)")
add("MECH-COOL-01", "Cooling and power assembly drawing", "none (PA dissipation implied by xlsx)", "—", [], "BLOCKED — MISSING DATA", "heatsink/fan geometry (G-08)")
add("MECH-PED-01", "Pedestal / azimuth drive drawing", "firmware constants only", "—", [], "BLOCKED — MISSING DATA", "G-07")
add("ASM-EXP-01", "Exploded assembly view (electronics set)", "4 × .brd outlines; interconnection table; antenna spacing doc", f"{E}/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.svg",
    [f"{E}/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.pdf", f"{E}/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png"], "CONCEPTUAL", "stacking, spacing, fasteners, enclosure, antenna, host")
add("ASM-PL-01", "Parts list", "BOMs + connector matrix + firmware", f"{E}/ASSEMBLY/PARTS_LIST.md", [], "PARTIAL", "all off-board part numbers")
add("ASM-SEQ-01", "Assembly / integration sequence", "connector matrix, power sequence (power_rails.md)", f"{E}/ASSEMBLY/ASSEMBLY_SEQUENCE.md", [], "PARTIAL", "mechanical steps CONCEPTUAL; conflicts K1–K8")
# --- PROPOSED DESIGNS (engineering/DESIGN, 2026-10-09) ---
DZ = f"{E}/DESIGN"
add("DSN-00", "Design basis, decisions D-01…D-15, parameter file", "verified repo constraints + decisions", f"{DZ}/00_DESIGN_BASIS.md", [f"{DZ}/design_parameters.json"], "PROPOSED DESIGN", "owner approval of D-01…D-15")
add("DSN-ANT-01", "16×8 microstrip patch array panel (native KiCad PCB, calc sheet, openEMS model)", "f0, pitch, 8×16 from docs; RO4350B datasheet; decisions D-01…D-06", f"{DZ}/ANTENNA/kicad/aeris10_patch_array.kicad_pcb",
    [f"{DZ}/ANTENNA/aeris10_patch_array_layout.svg", f"{DZ}/ANTENNA/aeris10_patch_array_layout.pdf", f"{DZ}/ANTENNA/ANTENNA_DESIGN_CALC.md", f"{DZ}/ANTENNA/openems_patch_row.py",
     f"{DZ}/ANTENNA/kicad_exports/aeris10_patch_array_top.pdf", f"{DZ}/ANTENNA/kicad_exports/aeris10_patch_array.step", f"{DZ}/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png", f"{DZ}/ANTENNA/kicad_exports/gerber/aeris10_patch_array-job.gbrjob"],
    "PROPOSED DESIGN", "EM simulation + coupon measurement (not run: openEMS absent); chirp bandwidth B TBD; connector footprint")
add("DSN-THM-01", "Thermal budget + 22 V supply sizing", "firmware timing, QPA2962 datasheet, D-10/D-11/D-14", f"{DZ}/THERMAL/THERMAL_AND_PA_SUPPLY.md", [f"{DZ}/THERMAL/thermal_summary.json"], "PROPOSED DESIGN", "PA-board via-field Rth, fan selection, per-rail currents")
add("DSN-PSU-01", "22 V PA drain supply, enable switch, per-PA pulse gating (block schematic, BOM, nets)", "D-14; xlsx VIN; main.h EN pin", f"{DZ}/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.svg",
    [f"{DZ}/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.pdf", f"{DZ}/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_BOM.csv", f"{DZ}/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_netlist.csv", f"{DZ}/ELECTRICAL/PA_SUPPLY_22V/README.md"],
    "PROPOSED DESIGN", "TX_GATE FPGA pin, PGOOD MCU pin, component-level capture (MDR-12)")
add("DSN-MECH-3D", "Radar head + pedestal parametric 3-D model (FreeCAD native, STEP, STL, DXF page, mass table)", "board outlines/holes (verified), D-07…D-13", f"{DZ}/MECHANICAL/CAD/aeris10_head_pedestal.FCStd",
    [f"{DZ}/MECHANICAL/CAD/aeris10_head_pedestal.step", f"{DZ}/MECHANICAL/CAD/aeris10_head_only.step", f"{DZ}/MECHANICAL/CAD/aeris10_pedestal_only.step", f"{DZ}/MECHANICAL/CAD/aeris10_head.stl", f"{DZ}/MECHANICAL/CAD/aeris10_pedestal.stl",
     f"{DZ}/MECHANICAL/CAD/aeris10_orthographic.dxf", f"{DZ}/MECHANICAL/CAD/aeris10_mass_table.json", f"{DZ}/MECHANICAL/CAD/aeris10_head_pedestal_iso.svg", f"{DZ}/MECHANICAL/CAD/aeris10_head_xray_iso.svg", f"{DZ}/MECHANICAL/CAD/aeris10_head_xray_iso.png"],
    "PROPOSED DESIGN", "component heights (G-02), fasteners, sheet-metal detailing, sealing, mast interface")
for n, t in [("01", "Head plan section"), ("02", "Head front elevation"), ("03", "Head side section incl. pedestal"), ("04", "Internal layout per tier with connector positions"), ("05", "Pedestal plan")]:
    base = {"01": "head_plan_section", "02": "head_front_elevation", "03": "head_side_section", "04": "internal_layout_rear", "05": "pedestal_plan"}[n]
    add(f"DSN-MECH-{n}", t, "tools/design_layout.py (D-07…D-13) + KiCad P&P", f"{DZ}/MECHANICAL/drawings/DSN-MECH-{n}_{base}.svg", [f"{DZ}/MECHANICAL/drawings/png/DSN-MECH-{n}_{base}.png", f"{DZ}/MECHANICAL/drawings/DSN-MECH-01-05_head_pedestal_drawings.pdf"], "PROPOSED DESIGN", "as DSN-MECH-3D")
add("DSN-LINK-01", "FPGA → host data path: option A FT601 pin plan (bank 35) + option B SPI bridge (RTL, STM32 driver, GUI parser)", "Main Board netlist (free bank-35 pins, DIG_5..7, SPI1), RTL geometry, firmware timing", f"{DZ}/HOST_LINK/HOST_LINK_DESIGN.md",
    [f"{DZ}/HOST_LINK/ft601_pin_assignment.csv", f"{DZ}/HOST_LINK/ft601_bank35.xdc", f"{DZ}/HOST_LINK/ft601_added_parts_BOM.csv", f"{DZ}/HOST_LINK/option_b_signal_map.csv",
     f"{DZ}/HOST_LINK/rtl/rd_map_packer.v", f"{DZ}/HOST_LINK/rtl/host_bridge_spi.v", f"{DZ}/HOST_LINK/rtl/tb_host_bridge.v", f"{DZ}/HOST_LINK/stm32/host_bridge.c", f"{DZ}/HOST_LINK/gui/bridge_frame.py", f"{DZ}/HOST_LINK/README.md"],
    "PROPOSED DESIGN", "option A needs Main Board rev. B + FT601 datasheet checks; option B bench test; packer integration into beta/fpga")
add("DSN-ANT-01-SIM", "openEMS simulation of one antenna row (S11, directivity, tuning log)", "openems_patch_row.py run with openEMS built from source", f"{DZ}/ANTENNA/simulation/TUNING_LOG.md",
    [f"{DZ}/ANTENNA/simulation/s11.csv", f"{DZ}/ANTENNA/simulation/s11_row.png", f"{DZ}/ANTENNA/simulation/tuning_result.json"], "PROPOSED DESIGN", "16-row coupling, squint vs. frequency, measurement")
add("DSN-MECH-3D-DETAIL", "Detailed enclosure + pedestal model: 51 parts (tray, front plate, lid, window + gasket + frame, PA plate with brackets, carrier rails, standoffs, gland plate, bearing, pulleys, slip ring, motor bracket, mast flange)", "tools/design_layout.py + PCB hole tables + D-07…D-13", f"{DZ}/MECHANICAL/CAD/detail/aeris10_enclosure_detail.FCStd",
    [f"{DZ}/MECHANICAL/CAD/detail/aeris10_enclosure_detail.step", f"{DZ}/MECHANICAL/CAD/detail/aeris10_head_detail.step", f"{DZ}/MECHANICAL/CAD/detail/aeris10_pedestal_detail.step", f"{DZ}/MECHANICAL/CAD/detail/parts_list.json",
     f"{DZ}/MECHANICAL/CAD/detail/aeris10_detail_xray_front_iso.png", f"{DZ}/MECHANICAL/CAD/detail/aeris10_detail_iso_rear.png", f"{DZ}/MECHANICAL/CAD/detail/aeris10_detail_isometrics.pdf"], "PROPOSED DESIGN", "bend reliefs, welds, lid stiffening, fan brackets, earthing, mast interface; part numbers for bearing/slip ring/glands")
add("DSN-MECH-06", "Sheet-metal flat patterns with bend lines (tray, front plate, lid)", "detail model, BA = π/2·(R + K·t)", f"{DZ}/MECHANICAL/drawings/DSN-MECH-06_sheet_metal_flat_patterns.svg", [f"{DZ}/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png", f"{DZ}/MECHANICAL/drawings/DSN-MECH-06-07_enclosure_detail.pdf"], "PROPOSED DESIGN", "CAM check of bend allowance/reliefs")
add("DSN-MECH-07", "Assembly section with fastener balloons", "detail model", f"{DZ}/MECHANICAL/drawings/DSN-MECH-07_assembly_section_fasteners.svg", [f"{DZ}/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png", f"{DZ}/MECHANICAL/MECHANICAL_PARTS_LIST.md"], "PROPOSED DESIGN", "as DSN-MECH-3D-DETAIL")
add("DSN-HAR-01", "Harness schedule with computed lengths (144 cables)", "interconnection_table.md + P&P + proposed layout", f"{DZ}/HARNESS/harness_schedule.csv", [f"{DZ}/HARNESS/HARNESS_SCHEDULE.md"], "PROPOSED DESIGN", "Power-rail pairs not matched by net name; stepper driver location; PA-instance mapping")
add("ASM-DRW-01", "Assembly drawings (per board)", "KiCad fab/silk plots", f"{E}/ASSEMBLY/ASSEMBLY_DRAWINGS/README.md", [], "SOURCE-DERIVED", "component heights; bottom views mirrored only")


def check_file(path: str) -> str:
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        return "MISSING"
    if os.path.getsize(p) == 0:
        return "EMPTY"
    if path.endswith(".svg"):
        try:
            ET.parse(p)
        except ET.ParseError as exc:
            return f"INVALID SVG ({exc})"
    if path.endswith(".pdf"):
        with open(p, "rb") as fh:
            head = fh.read(5)
            fh.seek(-64, os.SEEK_END)
            tail = fh.read()
        if head != b"%PDF-" or b"%%EOF" not in tail:
            return "INVALID PDF"
    if path.endswith(".dot") and b"digraph" not in open(p, "rb").read(2000) and b"graph" not in open(p, "rb").read(2000):
        return "INVALID DOT"
    return "OK"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    counts = {}
    L = ["# AERIS-10 — Drawing register\n",
         f"Document ENG-REG-01 · Rev A · {a.date} · generated by `tools/gen_drawing_register.py` (run with `--check` to validate files). "
         "Status vocabulary: VERIFIED (checked against hardware/EAGLE output), SOURCE-DERIVED (generated from the native design files, not reviewed), PARTIAL, CONCEPTUAL, BLOCKED — MISSING DATA. "
         "No drawing is VERIFIED: nothing was compared with an EAGLE/vendor output or with hardware.\n",
         "| ID | Drawing | Source | Native format | PDF/SVG/other exports | Status | Missing data |", "|---|---|---|---|---|---|---|"]
    problems = []
    for i, t, s, n, x, st, m in REGISTER:
        counts[st.split(" ")[0]] = counts.get(st.split(" ")[0], 0) + 1
        nat = f"`{n}`" if n != "—" else "— (none)"
        exp = ", ".join(f"`{os.path.basename(e)}`" for e in x) if x else "—"
        if a.check:
            for f in ([n] if n != "—" and not n.startswith("4_") else []) + x:
                r = check_file(f)
                if r != "OK":
                    problems.append((i, f, r))
        L.append(f"| {i} | {t} | {s} | {nat} | {exp} | {st} | {m} |")
    L.append("\n## Summary\n")
    L.append("| Status | Drawings |\n|---|---|")
    for k, v in sorted(counts.items()):
        L.append(f"| {k} | {v} |")
    L.append(f"| **Total registered** | {len(REGISTER)} |")
    L.append("\nExisting drawings found in the repository before this work: `2_Functional Diagram…/RADAR_V6.drawio` (+ .jpg, .dwg) system block diagram; "
             "`4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` (unlabelled stack-up); `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/` (P&P + BOM xlsx); "
             "`8_Utils/*.jpg` photographs; `docs/MECHANICAL/drawings/*_outline.svg` (first reconstruction). None of them is a dimensioned engineering drawing.")
    if a.check:
        nfiles = sum(len(x) + (1 if n != "—" and not n.startswith("4_") else 0) for _, _, _, n, x, _, _ in REGISTER)
        L.append(f"\n## File check ({a.date})\n")
        L.append(f"Checked {nfiles} registered files (existence, non-empty, SVG/PDF/DOT well-formed): **{nfiles - len(problems)} OK, {len(problems)} problems**.")
        for i, f, r in problems:
            L.append(f"- {i}: `{f}` — {r}")
    with open(os.path.join(ROOT, E, "DRAWING_REGISTER.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"register: {len(REGISTER)} drawings; statuses {counts}")
    if a.check:
        print(f"file check: {len(problems)} problems")
        for p in problems:
            print("  ", p)
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
