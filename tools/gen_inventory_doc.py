#!/usr/bin/env python3
"""
gen_inventory_doc.py — Generate docs/01_REPOSITORY_INVENTORY.md (Path | File type | Subsystem |
Purpose | Dependencies | Status) from the live file tree plus a curated purpose/dependency map.

The curated map (PURPOSE below) is keyed by exact relative path or by directory prefix; files
without a curated entry get a type-based generic purpose and status UNKNOWN unless a cheap
verifiable check applies (see repo_inventory.status_for).  Writes ONLY the --out file.

Usage:
    python3 tools/gen_inventory_doc.py [--root PATH] [--out docs/01_REPOSITORY_INVENTORY.md]
Exit codes: 0 ok, 2 root missing.
Dependencies: Python 3.8+ stdlib; tools/repo_inventory.py.
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo_inventory import TYPE_MAP, classify_subsystem, status_for, walk  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CAD = "4_Schematics and Boards Layout"
FW = "9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries"
FPGA = "9_Firmware/9_2_FPGA"
GUI = "9_Firmware/9_3_GUI"

# exact path -> (purpose, dependencies, status override or None)
PURPOSE = {
    "README.md": ("Project overview; claims Gerbers, assembly guide (10_docs/) and enclosure files that do not exist", "—", "INCOMPLETE"),
    "claude.md": ("Task specification for this engineering reconstruction", "—", "COMPLETE"),
    f"{FPGA}/radar_system_top.v": ("FPGA top level: 67 ports, instantiates transmitter, receiver, USB, level shifter, CDC", "all other RTL; cntrt.xdc; .mem files", "INCOMPLETE"),
    f"{FPGA}/cntrt.xdc": ("Vivado constraints: clocks + I/O standards; 142 [PIN_NUMBER] placeholders, invalid PACKAGE_PIN_BANK property", "radar_system_top.v port names", "PLACEHOLDER"),
    f"{FPGA}/radar_system_tb.v": ("System testbench with SystemVerilog assertions (needs SV simulator: xsim/Questa; Icarus fails)", "radar_system_top.v", "REQUIRES VALIDATION"),
    f"{FPGA}/chirp_lut_init.v": ("Bare `initial` block (no module) initialising long_chirp_lut[]; include-fragment, not standalone", "a module declaring long_chirp_lut", "INCOMPLETE"),
    f"{FPGA}/chirp_memory_loader_param.v": ("$readmemh loader for 4x1024 long-chirp segments + short chirp", "long_chirp_seg0..3_{i,q}.mem (seg3 MISSING), short_chirp_{i,q}.mem", "MISSING DEPENDENCY"),
    f"{FPGA}/radar_transmitter.v": ("TX: chirp controller -> DAC interface, ADAR load/TR sequencing", "plfm_chirp_controller.v, dac_interface_single.v", "REQUIRES VALIDATION"),
    f"{FPGA}/radar_receiver_final.v": ("RX chain: ADC LVDS -> DDC -> CIC -> FIR -> matched filter -> Doppler", "ad9484_interface_400m.v, ddc_400m.v, cic_decimator_4x_enhanced.v, fir_lowpass.v, matched_filter_multi_segment.v, doppler_processor.v", "REQUIRES VALIDATION"),
    f"{FPGA}/usb_data_interface.v": ("FT601 32-bit synchronous FIFO master interface", "cdc_modules.v", "REQUIRES VALIDATION"),
    f"{FPGA}/usb_packet_analyzer.v": ("Packet framing for USB stream", "usb_data_interface.v", "REQUIRES VALIDATION"),
    f"{FPGA}/level_shifter_interface.v": ("Pass-through of STM32 SPI 3.3 V <-> ADAR1000 1.8 V through FPGA banks", "—", "REQUIRES VALIDATION"),
    f"{FPGA}/short_chirp_i.mem": ("Short chirp I LUT, 50 lines hex", "chirp_memory_loader_param.v", "COMPLETE"),
    f"{FPGA}/short_chirp_q.mem": ("Short chirp Q LUT, 50 lines hex", "chirp_memory_loader_param.v", "COMPLETE"),
    f"{FW}/stm32f7xx_hal_conf.h": ("CubeMX-style HAL module enable list and oscillator values", "STM32CubeF7 HAL headers (absent)", "MISSING DEPENDENCY"),
    f"{FW}/stm32f7xx_hal_msp.c": ("CubeMX-style MSP init: peripheral GPIO/AF/DMA/IRQ configuration (verified pin evidence)", "stm32f7xx_hal.h (absent), main.h", "MISSING DEPENDENCY"),
    f"{FW}/stm32f7xx_it.c": ("Interrupt handlers", "stm32f7xx_hal.h (absent), main.h", "MISSING DEPENDENCY"),
    f"{FW}/system_stm32f7xx.c": ("CMSIS SystemInit / SystemCoreClock", "stm32f7xx.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/syscalls.c": ("Newlib syscall stubs", "libc", "COMPLETE"),
    f"{FW}/sysmem.c": ("Newlib _sbrk heap", "libc; linker symbols from missing .ld", "MISSING DEPENDENCY"),
    f"{FW}/USBHandler.cpp": ("USB CDC command parser (SET/END framing, start flag 23,46,158,237)", "usbd_cdc_if.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/USBHandler.h": ("USB handler interface", "—", "REQUIRES VALIDATION"),
    f"{FW}/RadarSettings.cpp": ("Radar parameter container/parser", "RadarSettings.h", "REQUIRES VALIDATION"),
    f"{FW}/ADAR1000_Manager.cpp": ("C++ wrapper managing 4x ADAR1000 beamformers", "adar1000.h, stm32f7xx_hal.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/adar1000.c": ("ADAR1000 register driver (HAL SPI/GPIO)", "stm32f7xx_hal_spi.h/gpio.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/adf4382.c": ("ADI no-OS ADF4382 synthesizer driver", "no_os_spi.h, no_os_util.h", "REQUIRES VALIDATION"),
    f"{FW}/adf4382a_manager.c": ("Project wrapper for TX/RX ADF4382A", "adf4382.h, platform_noos_stm32.H", "REQUIRES VALIDATION"),
    f"{FW}/ad9523.c": ("ADI no-OS AD9523 clock generator driver", "no_os_spi.h", "REQUIRES VALIDATION"),
    f"{FW}/platform_noos_stm32.c": ("Glue binding no-OS SPI/GPIO/delay to STM32 HAL", "platform_noos_stm32.H (case mismatch), stm32_spi.h", "INCOMPLETE"),
    f"{FW}/DA5578.c": ("DAC5578 (PA gate-voltage DAC) I2C driver; file name differs from header DAC5578.H", "DAC5578.H (case mismatch)", "INCOMPLETE"),
    f"{FW}/ADS7830.c": ("ADS7830 8-ch ADC I2C driver (Idq / temperature)", "ADS7830.H (case mismatch)", "INCOMPLETE"),
    f"{FW}/TinyGPS++.cpp": ("Arduino TinyGPS++ NMEA parser (third-party, Arduino API)", "TinyGPS++.h; Arduino String/Stream in original", "REQUIRES VALIDATION"),
    f"{FW}/gps_handler.cpp": ("GPS UART -> USB forwarding", "usb_device.h, usbd_cdc_if.h (absent), TinyGPSPlus.h", "MISSING DEPENDENCY"),
    f"{FW}/GY_85_HAL.c": ("GY-85 IMU (ADXL345/ITG3205/HMC5883L) I2C driver", "stm32f7xx_hal.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/BMP180.cpp": ("BMP180 barometer driver", "stm32f7xx_hal.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/iio.c": ("ADI no-OS IIO daemon (not used by main.cpp; pulls tcp_socket.h/lwip)", "tcp_socket.h, lwip_socket.h (absent)", "MISSING DEPENDENCY"),
    f"{FW}/iiod.c": ("ADI no-OS IIOD protocol (unused)", "iiod_private.h", "REQUIRES VALIDATION"),
    f"{FW}/iio_app.c": ("ADI no-OS IIO app (unused; references xilinx/maxim/aducm headers)", "parameters.h, xilinx_uart.h ... (absent)", "MISSING DEPENDENCY"),
    "9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp": ("CubeMX-style main: power sequencing, AD9523/ADF4382/ADAR1000 setup, GPS/IMU, USB CDC, chirp scheduling (2411 lines)", "main.h, usb_device.h, usbd_cdc_if.h (absent), HAL (absent), all drivers", "MISSING DEPENDENCY"),
    "9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h": ("Pin macros and handle externs", "stm32f7xx_hal.h (absent)", "MISSING DEPENDENCY"),
    "9_Firmware/9_1_Microcontroller/9_1_2_C_Cpp_Algorithms/STM32_ALGO.docx": ("Firmware algorithm description (Word)", "—", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V1.py": ("41-line method fragment (update_gps_display) with leading indent — not a program", "—", "PLACEHOLDER"),
    f"{GUI}/GUI_V2.py": ("Tk GUI v2: STM32 USB CDC, DBSCAN, Kalman", "numpy, scipy, matplotlib, sklearn, filterpy, crcmod, pyusb, pyftdi", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V3.py": ("Tk GUI v3: pitch correction, map, real-time plot", "same as V2", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V4.py": ("Tk GUI v4: pitch correction", "same as V2", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V4_2_CSV.py": ("Offline CSV replay GUI", "numpy, scipy, matplotlib, pandas; test_radar_data.csv", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V5.py": ("Tk GUI v5 (last complete hardware GUI): Mercury colour map", "same as V2", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V5_Demo.py": ("v5 demo with synthetic data + tkinterweb map", "same as V2 + tkinterweb", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V6.py": ("v6 FT601 USB3 GUI — RadarProcessor/USBPacketParser/RadarPacketParser are `pass` stubs ('same as before'); get_packet_length() returns constant 64", "same as V2", "PLACEHOLDER"),
    f"{GUI}/GUI_V6_Demo.py": ("v6 demo: synthetic targets, no hardware", "numpy, matplotlib (tkinter)", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_versions.txt": ("Change log of GUI versions", "—", "COMPLETE"),
    f"{GUI}/test_radar_data.csv": ("Sample data for CSV replay", "GUI_V4_2_CSV.py", "REQUIRES VALIDATION"),
    f"{GUI}/GUI_V6.gif": ("Animated screenshot used by README", "—", "COMPLETE"),
    f"{GUI}/requirements.txt": ("Generated: pinned/tested Python dependencies", "pip", "COMPLETE"),
    f"{GUI}/pyproject.toml": ("Generated: packaging metadata", "setuptools", "COMPLETE"),
    f"{CAD}/4_6_Schematics/MainBoard/RADAR_Main_Board.sch": ("EAGLE 7.4.0 schematic: XC7A50T-2FTG256I (U42), STM32F746ZGT7 (U2), AD9484, AD9708, 4x ADAR1000, 16x ADTR1107, 2x LTC5552, FT601Q (U6, UNCONNECTED)", "embedded libraries", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/MainBoard/RADAR_Main_Board.brd": ("EAGLE board layout for Main Board", ".sch (forward/back annotation)", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/PowerBoard/PowerBoard.sch": ("EAGLE schematic: power supply board", "embedded libraries", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/PowerBoard/PowerBoard.brd": ("EAGLE board: power supply board", ".sch", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch": ("EAGLE schematic: QPA2962 GaN PA board (AERIS-10X)", "embedded libraries", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd": ("EAGLE board: RF PA", ".sch", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch": ("EAGLE schematic: AD9523-1 clock + 2x ADF4382 synthesizers", "embedded libraries", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd": ("EAGLE board: frequency synthesizer", ".sch", "REQUIRES VALIDATION"),
    f"{CAD}/4_4_Board Stack-up/Stack_Hybrid.png": ("Hybrid stack-up image (no numeric layer table in text form)", "—", "REQUIRES VALIDATION"),
    f"{CAD}/4_6_Schematics/Stack_Hybrid.png": ("Duplicate of 4_4_Board Stack-up/Stack_Hybrid.png", "—", "COMPLETE"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board_BOM.xlsx": ("BOM for frequency synthesizer board (only board with a BOM)", ".sch", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board-smd.mnt": ("EAGLE SMD mount (pick-and-place) file", ".brd", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board-tht.mnt": ("EAGLE THT mount file", ".brd", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board-tht.csv": ("THT placement CSV", ".brd", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/mnt.csv": ("Placement CSV", ".brd", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/smd_.xlsx": ("SMD placement workbook", ".brd", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/th_.xlsx": ("THT placement workbook", ".brd", "REQUIRES VALIDATION"),
    f"{CAD}/4_7_Production Files/Frequency_Synthesizer/PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf": ("Fab impedance note (RO4350B, 0.102 mm) — only stack-up evidence in text form", "—", "REQUIRES VALIDATION"),
    "3_Power Management/Power Management V6.xlsx": ("Rail list and sequencing table (source for STM32 EN_* GPIO sequencing)", "—", "REQUIRES VALIDATION"),
    "2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio": ("System block diagram (draw.io XML)", "—", "COMPLETE"),
    "2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg": ("Rendered block diagram", "—", "COMPLETE"),
    "2_Functional Diagram & Interconnection Matrices/Functional_Diagram.dwg": ("AutoCAD functional diagram (binary; not a mechanical drawing)", "AutoCAD", "REQUIRES VALIDATION"),
    "1_Project_Description/Project_Description.docx": ("Project description (Word)", "—", "COMPLETE"),
}

PREFIX_PURPOSE = [
    (f"{FW}/no_os_", "ADI no-OS framework source (third-party, vendored)", "no_os_*.h", "REQUIRES VALIDATION"),
    (f"{FW}/stm32_", "ADI no-OS STM32 platform driver (third-party, vendored; needs HAL)", "stm32f7xx_hal.h (absent)", "MISSING DEPENDENCY"),
    (f"{FW}/iio", "ADI no-OS IIO stack (unused by main.cpp)", "no_os_*", "REQUIRES VALIDATION"),
    (f"{FPGA}/long_chirp_seg", "Long chirp LUT segment, 1024 lines hex", "chirp_memory_loader_param.v", "COMPLETE"),
    (f"{FPGA}/", "Verilog RTL module", "see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy", "REQUIRES VALIDATION"),
    ("7_Components Datasheets", "Component datasheet / app note (reference)", "—", "COMPLETE"),
    ("6_Application Notes", "Application note (reference)", "—", "COMPLETE"),
    ("5_Simulations/Antenna", "openEMS antenna simulation script", "openEMS, CSXCAD python", "REQUIRES VALIDATION"),
    ("5_Simulations/sim_wg_alumina", "openEMS waveguide simulation output / model", "openEMS", "REQUIRES VALIDATION"),
    ("5_Simulations/Sim_BPF_Te_100um/Gerber", "KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB)", "KiCad", "REQUIRES VALIDATION"),
    ("5_Simulations", "RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python)", "Qucs / Octave / Python", "REQUIRES VALIDATION"),
    ("8_Utils/Python", "Utility / analysis script", "numpy, matplotlib (see DEPENDENCIES.md)", "REQUIRES VALIDATION"),
    ("8_Utils", "Photo / media asset", "—", "COMPLETE"),
    ("01_physics/figures", "Generated physics figure or generator script", "numpy, matplotlib", "COMPLETE"),
    ("00_notation", "Notation / parameter documentation", "—", "COMPLETE"),
    ("01_physics", "Physics derivation documentation", "—", "COMPLETE"),
    ("02_hardware", "Hardware documentation (derived from RTL/firmware; partly contradicts schematic)", "—", "REQUIRES VALIDATION"),
    ("03_software", "Software documentation", "—", "REQUIRES VALIDATION"),
    ("04_research", "Improvement research survey", "—", "COMPLETE"),
    ("research/", "Improvement research survey (references missing sibling files)", "—", "INCOMPLETE"),
    (".planning", "GSD planning / phase records (process artefacts)", "—", "COMPLETE"),
    ("docs/", "Engineering reconstruction manual (generated by this project)", "tools/", "COMPLETE"),
    ("tools/", "Validation / generation script (this project)", "Python 3.10+, bash", "COMPLETE"),
    ("9_Firmware/9_2_FPGA/reconstructed", "Schematic-derived constraint candidate (NOT hardware-verified)", "tools/gen_xdc_from_schematic.py", "REQUIRES VALIDATION"),
]


def describe(rel: str, p: Path):
    if rel in PURPOSE:
        return PURPOSE[rel]
    for prefix, purpose, deps, st in PREFIX_PURPOSE:
        if rel.startswith(prefix):
            return purpose, deps, st
    return TYPE_MAP.get(p.suffix.lower(), "file"), "—", None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--out", default=ROOT / "docs/01_REPOSITORY_INVENTORY.md")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print("ERROR: root missing", file=sys.stderr); return 2
    rows, counts = [], {}
    for p, rel in walk(root):
        if rel.startswith("build/"):
            continue
        purpose, deps, st = describe(rel, p)
        status = st or status_for(p, rel)
        counts[status] = counts.get(status, 0) + 1
        rows.append((rel, TYPE_MAP.get(p.suffix.lower(), p.suffix or "none"), classify_subsystem(rel), purpose, deps, status))
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("# 01 — Repository Inventory (AERIS-10)\n\n")
        f.write(f"Generated {dt.date.today().isoformat()} by `tools/gen_inventory_doc.py` from the live file tree "
                f"({len(rows)} files, `.git` excluded). Regenerate after any change: "
                "`python3 tools/gen_inventory_doc.py`.\n\n")
        f.write("Status legend: COMPLETE — usable as-is for its purpose; INCOMPLETE — exists but cannot fulfil its purpose "
                "(syntax error, fragment, contradictory); MISSING DEPENDENCY — needs files absent from the repository; "
                "PLACEHOLDER — template/stub content; REQUIRES VALIDATION — plausible but not verified by an executed check; "
                "UNKNOWN — no check applied.\n\n")
        f.write("## Status summary\n\n| Status | Files |\n|---|---:|\n")
        for k in sorted(counts):
            f.write(f"| {k} | {counts[k]} |\n")
        f.write("\n## Subsystem summary\n\n| Subsystem | Files |\n|---|---:|\n")
        sub = {}
        for r in rows:
            sub[r[2]] = sub.get(r[2], 0) + 1
        for k in sorted(sub):
            f.write(f"| {k} | {sub[k]} |\n")
        f.write("\n## File table\n\n| Path | File type | Subsystem | Purpose | Dependencies | Status |\n|---|---|---|---|---|---|\n")
        for rel, t, s, purpose, deps, status in rows:
            esc = lambda x: x.replace("|", "\\|")  # noqa: E731
            f.write(f"| `{rel}` | {t} | {s} | {esc(purpose)} | {esc(deps)} | {status} |\n")
    print(f"wrote {out} ({len(rows)} rows); status counts: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
