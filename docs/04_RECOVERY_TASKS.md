# 04 — Recovery Tasks (tracker)

Status date 2026-10-08. Each task follows the required format (purpose, prerequisites, inputs, software, procedure, expected output, verification, troubleshooting, completion criteria); detailed step lists live in the subsystem documents referenced. Status values: DONE (executed in this reconstruction, with evidence), OPEN (procedure written, not executed), BLOCKED (needs information only the designer has).

## Status summary

| Status | Count |
|---|---:|
| DONE | 7 |
| OPEN | 20 |
| BLOCKED (designer input) | 9 |

---

## R-SYS-01 — Decide the host data path and packet format (BLOCKED)
- **Purpose:** resolve K3/K5 (`docs/SYSTEM/BLOCK_DIAGRAM.md` §4): CAD has only STM32 USB-FS; RTL assumes FT601; GUI V2–V5 assume FT2232H; packet formats differ.
- **Prerequisites:** system architect decision.
- **Inputs:** `RADAR_Main_Board.sch` (U6 unconnected), `usb_data_interface.v:39-160`, `GUI_V5.py:755-797`, `GUI_V6.py:94-363`.
- **Procedure:** (1) choose: (a) wire FT601 (PCB change: 32 data + control lines to FPGA bank 35, which has no I/O used today) or (b) route radar data through the STM32 (needs a high-speed FPGA↔STM32 link; only `DIG_0..7` + SPI1 exist) or (c) another bridge; (2) define one packet format; (3) update RTL, GUI and `03_software/04_usb_protocol.md`.
- **Expected output:** decision record; interface control document.
- **Verification:** AC-P6.
- **Completion criteria:** one format implemented on both ends and tested with loopback.

## R-FPGA-01 — Confirm FPGA part (BLOCKED)
See `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` FPGA-T01. Evidence conflict: XC7A50T-2FTG256I (CAD) vs XC7A100T (docs). Completion: part string recorded; README/XDC comment corrected.

## R-FPGA-02 — Verify the schematic-derived pin map (BLOCKED)
- **Inputs:** `9_Firmware/9_2_FPGA/reconstructed/PIN_MAP_FROM_SCHEMATIC.md` (64 ports), AMD package file `xc7a50tftg256pkg.txt` (UG475), final routed `.brd`.
- **Procedure:** for each row confirm pad against the package file and the board; decide the bank-14 LVDS VCCO issue; decide the 25 ports with no board counterpart (remove from top or add hardware).
- **Verification:** `tools/check_fpga_constraints.py --xdc <final.xdc>` exit 0.
- **Completion criteria:** XDC with zero placeholders signed off.

## R-FPGA-03 — Fix syntax and declaration-order defects (OPEN)
FPGA-T03; 6 edits listed. Verification: `tools/fpga_lint.sh` stops only on missing modules.

## R-FPGA-04 — Create the Vivado project (OPEN)
FPGA-T02 with `tools/vivado/create_project.tcl -tclargs <part>`. Not executed (no Vivado on authoring machine). Completion: `.xpr` + elaboration log archived under `build/vivado/`.

## R-FPGA-05 — Recover or re-implement missing modules and FFT IP (BLOCKED → OPEN if originals unavailable)
FPGA-T04. Needs: original ISE/Vivado project (`PLFM_RADAR_Xilinx_ISE_V2`) or re-implementation of `ad9484_lvds_to_cmos_400m`, `range_bin_decimator`, `matched_filter_processing_chain`, and regeneration of `xfft_32`/`FFT_enhanced`. Completion: iverilog elaboration with UNISIM succeeds; `.xci` committed.

## R-FPGA-06 — Memory files and LUT authority (BLOCKED)
Needs `long_chirp_seg3_{i,q}.mem` and the `.mem`/LUT generator; decide authoritative TX LUT (`plfm_chirp_controller.v` vs `chirp_lut_init.v`); replace Windows paths (`chirp_memory_loader_param.v:3-12`) with relative names via parameter override at `radar_receiver_final.v:144`. Completion: `$readmemh` clean on a fresh checkout; one LUT source.

## R-FPGA-07 — Functional redesign items (OPEN, design work)
ADC capture structure (IDDR/ISERDES + BUFIO/BUFR), single-driver refactor of `chirp_counter`, `ft601_clk_out`, CIC monitors; instantiate the level shifter; drive receiver controls; replace fixed-threshold "CFAR" (`radar_system_top.v:298-331`). Verification: verilator MULTIDRIVEN/UNDRIVEN = 0; AC-F6.

## R-FPGA-08 — Constraints: clock groups, CDC, I/O delays (OPEN)
Add `set_clock_groups -asynchronous` for the four external clocks; remove the multicycle at `cntrt.xdc:309-310`; add I/O delays for DAC data, SPI, FT601 control (if kept); set `CFGBVS`/`CONFIG_VOLTAGE`. Verification: `report_clock_interaction` no "unsafe"; `report_cdc` no critical.

## R-FPGA-09 — Testbench with pass/fail (OPEN)
FPGA-T05; add `$fatal` on assertion failure and a scoreboard; fix stimulus spacing (3 µs vs 167 µs chirp period). Completion: xsim log PASS.

## R-FPGA-10 — Synthesis, implementation, bitstream (OPEN)
FPGA-T06/T07. Completion: `.bit` + `util.rpt`, `timing.rpt`, `cdc.rpt` archived; AC-F5/F6/F8.

## R-STM-01 — Install toolchain and STM32CubeF7 (OPEN)
STM-T01. Verification: `tools/stm32_check_cube_package.sh <path>` exit 0.

## R-STM-02 — Regenerate CubeMX project and USB CDC files (OPEN)
STM-T02 with the verified tables of `docs/STM32` §3. Completion: generated MSP content equals `LIB/stm32f7xx_hal_msp.c`; VID/PID recorded.

## R-STM-03 — Build-set cleanup (OPEN)
STM-T03: rename `.H` headers, exclude `platform_noos_stm32.c`, `iio*.c`, `iiod.c`, decide `adar1000.c`, handle `LIB/errno.h`, set defines/flags. Verification: `tools/check_stm32_includes.py` 0 case mismatches; build 0 errors.

## R-STM-04 — Fix USB RX binding and start-flag padding (OPEN)
C4/C5. Verification: AC-S6 (READY_FOR_DATA reached).

## R-STM-05 — Resolve HSE 8 MHz vs 25 MHz (BLOCKED)
C1; needs board revision confirmation. Verification: measured SYSCLK.

## R-STM-06 — Fix ADF4382 driver (pins + platform ops + CS) (OPEN)
C2/C3/C7. Verification: `ADF4382A_Manager_Init` returns 0; LKDET high on LEDs; spectrum analyser on LO outputs (physical).

## R-STM-07 — GPS path (OPEN)
C6: call `GPS_Init`; align text format (3 vs 4 fields) with GUI. Verification: GPSB packets received.

## R-STM-08 — Compile, link, size, static analysis (OPEN)
STM-T05. Completion: AC-S4.

## R-GUI-01 — Consolidate GUI versions (OPEN)
Archive V1/V5_Demo/V6 or complete V6; keep V5 as hardware GUI and V6_Demo as offline demo; update `pyproject.toml` module list. Verification: `tools/check_python_imports.py --dir 9_Firmware/9_3_GUI` exit 0.

## R-GUI-02 — Unit tests (OPEN)
pytest suite for `RadarSettings` packet pack/unpack (82 B), GPSB parse, CFAR on `test_radar_data.csv`, V5 packet-length bug. Completion: AC-P5.

## R-GUI-03 — Packaging and smoke test (OPEN)
GUI-T05/T07. Completion: AC-P4, AC-P7.

## R-PCB-01 — Complete Main Board layout (BLOCKED)
Designer: route 2 390 airwires (after FT601 decision), place 11 parked parts, clear/justify 211 approved DRC errors, resolve 10-vs-8 layer DRU inconsistency and XADC reference wiring. Verification: AC-B1/B2.

## R-PCB-02 — Complete Power Board layout and fix version mismatch (BLOCKED)
Designer: re-link sch/brd in EAGLE 9.6.2, place 132 parts, route 309 airwires, decide outline (280 × 300 vs hole pattern), 22 V PA rail. Verification: AC-B1/B2/B8.

## R-PCB-03 — RF PA production export (PARTIALLY DONE 2026-10-09 — KiCad-converted package generated in `engineering/PCB/RF_PA/`; EAGLE-native export and fabricator review still OPEN)
P-EAGLE-01..08 on `RF_PA`; 4-layer stack confirmation. Completion: `check_manufacturing_files.py` RF PA row all YES.

## R-PCB-04 — Frequency Synthesizer production export (PARTIALLY DONE 2026-10-09 — KiCad-converted package in `engineering/PCB/FREQUENCY_SYNTHESIZER/`; EAGLE-native export and fabricator review still OPEN)
P-EAGLE-04/07/08; remove duplicate P&P files; resolve oscillator conflict (K7). Completion: Synth row all YES.

## R-PCB-05 — BOM completion with MPNs (OPEN)
`docs/BOM/README.md` validation procedure: add `MPN`/`MANUFACTURER`/`DNP` attributes in the schematics, fill 244/80/6/47 missing values, regenerate. Completion: `mpn_status` all VERIFIED.

## R-PCB-06 — Stack-up confirmation (BLOCKED)
Obtain vendor stack-up per board; reconcile EAGLE `mtIsolate`, `Stack_Hybrid.png`, PCBWay note; issue fab drawings. Completion: AC-B6.

## R-MECH-01 — Obtain enclosure, antenna, pedestal CAD and part numbers (BLOCKED)
Inputs from designer per `docs/MECHANICAL/MECHANICAL_GAP_ANALYSIS.md` §7. Completion: AC-M2.

## R-MECH-02 — Write `10_docs/assembly_guide.md` and exploded view (PARTIALLY DONE 2026-10-09 — `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md`, `PARTS_LIST.md` and a CONCEPTUAL exploded view exist; real geometry needs R-MECH-01)
Per `ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md`. Completion: AC-M3/M4.

## R-DOC-01 — Repository hygiene (OPEN, owner decisions)
LICENSE, `.gitignore`, own `.git`, README corrections (Gerber claim, FPGA part, `10_docs` links), fix 34 broken links. Completion: AC-D2/D3/D4.

## R-DOC-02 — Datasheet collection (OPEN)
Add datasheets for parts actually used (`docs/03_MISSING_COMPONENTS.md` PCB-ALL-03); remove duplicates (UG-290 ×2, RO4000 ×2).

## R-DOC-03 — Recover `STM32_ALGO.docx` (BLOCKED)
0-byte file; obtain from author.

---

## DONE in this reconstruction (evidence)

| Task | Output | Verification |
|---|---|---|
| D-01 Repository inventory | `docs/01_REPOSITORY_INVENTORY.md` (482 rows) | `tools/gen_inventory_doc.py` exit 0 |
| D-02 Validation tooling | `tools/*.py`, `tools/*.sh` (11 scripts), `tools/vivado/create_project.tcl` | each executed; see `docs/TESTING/VALIDATION_PLAN.md` |
| D-03 FPGA pin-map candidate | `9_Firmware/9_2_FPGA/reconstructed/*.xdc`, `PIN_MAP_FROM_SCHEMATIC.md` | `gen_xdc_from_schematic.py` exit 0; **unverified on hardware** |
| D-04 GUI packaging files | `9_Firmware/9_3_GUI/requirements.txt`, `pyproject.toml` | venv install + import PASSED |
| D-05 BOM package | `docs/BOM/*` for 4 boards | counts match `.brd` elements |
| D-06 Outline drawings | `docs/MECHANICAL/drawings/*.svg` | generated from `.brd` layer 20 |
| D-07 Documentation package | `docs/**` per `claude.md` §13 + `docs/SYSTEM/BLOCK_DIAGRAM.md`, `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md` | `tools/check_missing_files.py` DOC-* present |


---

## Engineering drawings package (added 2026-10-09, claude.md addendum §16–26)

| Task | Status | Evidence |
|---|---|---|
| R-ENG-01 — Render all schematics to SVG/PDF/PNG with title blocks | DONE | `engineering/ELECTRICAL/schematics/*/` (7 sheets); `tools/render_eagle_schematic.py`, `tools/svg_sheets_to_pdf.py` |
| R-ENG-02 — Netlists, component-to-net, unresolved-connection and missing-symbol/footprint reports | DONE | `engineering/ELECTRICAL/netlists/`, `connection_diagrams/`; `tools/gen_schematic_reports.py` exit 0 |
| R-ENG-03 — Convert the four EAGLE boards to KiCad and export Gerber/drill/PDF/SVG/DXF/STEP/P&P/IPC-2581/IPC-D-356/DRC/3-D | DONE (generated; not designer-released) | `engineering/PCB/<BOARD>/`, `engineering/VALIDATION/CAD_EXPORT_LOG.md` (0 failed steps), `PCB_CROSS_CHECK.md` 32/32 OK |
| R-ENG-04 — System block / interconnection / data-flow / power-distribution diagrams (editable DOT + Mermaid) | DONE | `engineering/SYSTEM/`, `engineering/ELECTRICAL/power_distribution/` |
| R-ENG-05 — Software architecture diagrams (FPGA hierarchy, pipeline, STM32, USB CDC, Python, end-to-end) | DONE | `engineering/SOFTWARE_DIAGRAMS/` (SD-01…SD-07) |
| R-ENG-06 — Mechanical package from PCB geometry (DXF ×2 sources, STEP, 1:1 plan view, dimension sheets, hole tables) | DONE | `engineering/MECHANICAL/`; `tools/gen_mechanical_package.py` |
| R-ENG-07 — Drawing register + file check, recovery plan, validation records | DONE | `engineering/DRAWING_REGISTER.md` (73 drawings, 0 file problems), `MISSING_DRAWINGS_RECOVERY_PLAN.md` (MDR-01…11), `VALIDATION/*` |
| R-ENG-08 — Enclosure, internal layout, antenna, cooling, pedestal drawings | BLOCKED (MDR-01…05) | no source geometry; `VALIDATION/UNRESOLVED_GEOMETRY.md` G-01…G-12 |
| R-ENG-09 — Upgrade exploded view from CONCEPTUAL to SOURCE-DERIVED | BLOCKED (needs R-ENG-08) | MDR-06 |
| R-ENG-10 — Vendor fabrication notes + stack-up → fabrication drawings; EAGLE-native Gerbers compared with the KiCad set | OPEN | MDR-07 |
| R-ENG-11 — Finish Main/Power routing, regenerate packages | OPEN (designer) | MDR-08; KiCad `unconnected_items` 15 / 308 |
| R-ENG-12 — 3-D component models → assembled STEP, component heights | OPEN | MDR-09 |
| R-ENG-13 — Native KiCad schematic twins + ERC (GUI import) | OPEN | MDR-10 |

## Proposed designs (added 2026-10-09, version 1.2)

| Task | Status | Evidence |
|---|---|---|
| R-DSN-01 — Antenna panel proposal (KiCad, calc, openEMS model) | DONE (PROPOSED; not simulated) | `engineering/DESIGN/ANTENNA/` |
| R-DSN-02 — Thermal budget + drain-gating requirement | DONE (PROPOSED) | `engineering/DESIGN/THERMAL/` |
| R-DSN-03 — 22 V PA supply/gate module block design | DONE (PROPOSED) → KiCad capture OPEN (MDR-12) | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/` |
| R-DSN-04 — Head + pedestal 3-D model and 2-D drawings | DONE (PROPOSED) | `engineering/DESIGN/MECHANICAL/` |
| R-DSN-05 — Harness schedule | DONE (PROPOSED) | `engineering/DESIGN/HARNESS/` |
| R-DSN-06 — Owner decisions D-01, D-07, D-12, D-13, D-14 | BLOCKED (owner) | `engineering/DESIGN/00_DESIGN_BASIS.md` §2–3 |
| R-DSN-07 — Simulate/measure the antenna, test one gate channel, measure component heights | OPEN | `ANTENNA_DESIGN_CALC.md` §7; `PA_SUPPLY_22V/README.md` |

## BETA completions (added 2026-10-09, version 1.3)

| Task | Status | Evidence |
|---|---|---|
| R-BETA-01 FPGA RTL builds + missing modules + testbenches | DONE (BETA) | `beta/fpga/build.sh` 0 failures |
| R-BETA-02 STM32 firmware builds + defect fixes + host tests | DONE (BETA) | `beta/stm32/build.sh` exit 0, tests 4/4 |
| R-BETA-03 GUI package + tests + packaging | DONE (BETA) | `beta/gui` pytest 55 passed |
| R-BETA-04 PCB routing completion + BOM MPN + fab notes | DONE (BETA; Power 89 open) | `beta/pcb/*/README.md` |
| R-BETA-05 FPGA→host path (DSN-LINK-01) | DONE (option B code), OPEN (bench, rev. B) | `engineering/DESIGN/HOST_LINK/` |
| R-BETA-06 Antenna simulation | DONE (one row) | `engineering/DESIGN/ANTENNA/simulation/` |
| R-BETA-07 Enclosure detail (flat patterns, fasteners, parts list) | DONE (PROPOSED) | `engineering/DESIGN/MECHANICAL/` |
| R-BETA-08 Vivado synthesis, flashing, fabrication, bench tests | BLOCKED (tools/hardware not on this machine) | — |
