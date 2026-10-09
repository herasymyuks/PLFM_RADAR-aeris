# AERIS-10 — Engineering Reconstruction, Build Preparation & Documentation Manual

Version 1.3 — 2026-10-09 (1.2: proposed designs; 1.1: drawings package; 1.0: 2026-10-08). Produced from the repository `PLFM_RADAR` as found (original content dated 2026-03-14), without modifying any original file. Every statement cites repository evidence or an executed command; items that could not be verified are marked UNRESOLVED / REQUIRES VERIFICATION. The authoring environment had Python 3.14.7, Icarus Verilog 13.0, Verilator 5.052, and — from version 1.1 — KiCad 10.0.6 (kicad-cli), Graphviz 16.1 and Google Chrome (headless, for SVG→PDF/PNG); no Vivado, ARM toolchain or EAGLE. Nothing was synthesised, compiled for the target or tested on hardware; CAD exports were produced through a KiCad conversion of the EAGLE files (Part XI), not by EAGLE itself.

**Readiness in one sentence:** the repository is a documented design study with schematics for four boards, partially routed layouts, non-building FPGA RTL, non-building STM32 firmware, one offline-runnable Python demo, and no mechanical design. No subsystem can be built reproducibly today; the blockers, their evidence and the recovery procedures are enumerated in this manual and its companion documents.

Companion documents (all under `docs/`):

| File | Content |
|---|---|
| `01_REPOSITORY_INVENTORY.md` | 482-row file inventory with status |
| `02_DEPENDENCY_MAP.md` | source → output graphs per subsystem |
| `03_MISSING_COMPONENTS.md` | register with ID / evidence / impact / recovery / priority |
| `04_RECOVERY_TASKS.md` | task tracker (7 done, 20 open, 9 blocked) |
| `05_TRACEABILITY_MATRIX.md` | requirement ↔ evidence ↔ artefact |
| `FPGA/FPGA_PROJECT_RECONSTRUCTION.md` | RTL/XDC analysis, pin map, Vivado procedures |
| `STM32/STM32_PROJECT_RECONSTRUCTION.md` | firmware analysis, `.ioc` reconstruction, build procedures |
| `PCB/00_COMMON_EAGLE_PROCEDURES.md`, `PCB/MAIN_BOARD.md`, `PCB/POWER_SUPPLY.md`, `PCB/RF_PA.md`, `PCB/FREQUENCY_SYNTHESIZER.md` | per-board manufacturing readiness |
| `BOM/README.md` + `BOM_*.csv/.md` | bills of materials extracted from the schematics |
| `SYSTEM/BLOCK_DIAGRAM.md` | verified block diagram and inter-board connector matrix |
| `GUI/INSTALLATION.md`, `GUI/DEPENDENCIES.md` | Python environment and dependency analysis |
| `MECHANICAL/MECHANICAL_GAP_ANALYSIS.md`, `MECHANICAL/ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md`, `MECHANICAL/drawings/*.svg` | mechanical evidence, gaps, PCB outline drawings |
| `TESTING/VALIDATION_PLAN.md`, `TESTING/ACCEPTANCE_CRITERIA.md` | tests with executed results; acceptance status |
| `../engineering/` (`DRAWING_REGISTER.md`, `MISSING_DRAWINGS_RECOVERY_PLAN.md`, `SYSTEM/`, `ELECTRICAL/`, `PCB/`, `MECHANICAL/`, `ASSEMBLY/`, `SOFTWARE_DIAGRAMS/`, `VALIDATION/`) | engineering drawings and CAD package (Part XI) |

---

# Part I — Project Overview

## I.1 Architecture (as evidenced)

AERIS-10 is a 10.5 GHz pulsed-LFM phased-array radar (README). The CAD shows four PCBs and off-board modules; the data flow is: AD9523 clock generator (Synth board) → ADF4382 LOs → LTC5552 mixers (Main) ← AD9708 DAC ← FPGA chirp LUT; receive ADTR1107 ×16 → ADAR1000 ×4 beamformers → mixer → AD8352 IF amps → AD9484 8-bit 400 MSPS ADC → FPGA (DDC, CIC, FIR, matched filter, Doppler) → host. The STM32F746ZGT7 sequences 16 power rails, programs AD9523/ADF4382/ADAR1000/DAC5578/ADS7830, reads GPS/IMU/barometer/temperatures, drives a stepper and talks to the host over USB-FS CDC. See `docs/SYSTEM/BLOCK_DIAGRAM.md` for the verified diagram and the connector matrix.

## I.2 Subsystems and their state

| Subsystem | Location | State (evidence) |
|---|---|---|
| FPGA RTL | `9_Firmware/9_2_FPGA/` (25 `.v`, 8 `.mem`, 1 `.xdc`) | does not parse (`radar_system_top.v:312`); 6 missing modules/IP; XDC 100 % placeholders; device contradiction (XC7A50T CAD vs XC7A100T docs) |
| STM32 firmware | `9_Firmware/9_1_Microcontroller/` (136 files) | application sources only; no `.ioc`, linker, startup, HAL, USB middleware, build system; 7 functional defects incl. HSE 8 vs 25 MHz |
| Python GUI | `9_Firmware/9_3_GUI/` (9 versions) | V5 complete for hardware; V6 (documented as current) is a stub; V6_Demo runs offline; no tests |
| Main Board | EAGLE 7.4.0, 260 × 300 mm, 10 Cu | 2 390 airwires, 11 parts off-board, 211 approved DRC; FT601 unconnected |
| Power Supply | sch 9.6.2 / brd 7.4.0, 280 × 300 mm, 2 Cu | 309 airwires, 132 parts off-board |
| RF PA | 9.6.2, 35 × 60 mm, 4 Cu | routed, no outputs |
| Frequency Synthesizer | 9.6.2, 100 × 100 mm, 6 Cu | routed; P&P + MPN-less BOM; no Gerbers |
| Mechanical | — | no CAD at all; README references to `10_docs/` are dead |
| Documentation | `00_notation … 04_research`, `.planning` | extensive, but derived from RTL/firmware and repeats the XC7A100T error |

## I.3 Repository map

See `docs/01_REPOSITORY_INVENTORY.md` (generated). Top level: `1_Project_Description` (docx), `2_Functional Diagram…` (drawio/dwg/jpg), `3_Power Management` (xlsx), `4_Schematics and Boards Layout` (EAGLE + partial production files), `5_Simulations` (Qucs, openEMS, KiCad filter export), `6_Application Notes`, `7_Components Datasheets…` (44 PDFs), `8_Utils` (photos, Python utilities), `9_Firmware` (STM32, FPGA, GUI), `00_notation`–`04_research` and `research/` (engineering docs), `.planning` (process records). Added by this reconstruction: `docs/`, `tools/`, `9_Firmware/9_2_FPGA/reconstructed/`, `9_Firmware/9_1_Microcontroller/reconstructed/`, `9_Firmware/9_3_GUI/requirements.txt`, `pyproject.toml`.

## I.4 Toolchains

| Subsystem | Required | Evidence of version used originally |
|---|---|---|
| FPGA | AMD Vivado (2020.2+; FFT IP v9.1) | none; `$readmemh` path names an ISE project (`chirp_memory_loader_param.v:3`) |
| STM32 | STM32CubeIDE/CubeMX + STM32CubeF7, GNU Arm Embedded | generated-file headers © 2025 (CubeMX ≥ 6.x), exact version unknown |
| GUI | CPython ≥ 3.10 with Tk; packages in `requirements.txt` | none; tested on 3.14.7 |
| PCB | EAGLE 9.6.2 (or Fusion 360 Electronics / KiCad import) | file headers 7.4.0 and 9.6.2 |
| Simulation | QucsStudio 5.8, openEMS, MATLAB/Octave | file headers |

---

# Part II — Environment Preparation

| Item | Procedure | Verification |
|---|---|---|
| OS | macOS 13+/Linux/Windows 10+ for Vivado (Linux/Windows only), CubeIDE, EAGLE, Python | — |
| Python | GUI-T01/T02 (`docs/GUI/INSTALLATION.md`) | `tools/check_python_imports.py --try-import` all OK (executed) |
| Open-source RTL tools | `brew install icarus-verilog verilator` (done on the authoring machine) | `tools/fpga_lint.sh` runs |
| Vivado | install ML Standard (Artix-7 in free list) | `vivado -version` |
| STM32 | STM-T01 | `tools/stm32_check_cube_package.sh <CubeF7>` exit 0 |
| EAGLE/KiCad | install; EAGLE 9.6.2 needed for the 9.6.2 files | opens `Clocks_Freq_Synth_board.sch` |
| Version compatibility | EAGLE 7.4 cannot open 9.6.2 files; KiCad importer approximates DRU; filterpy (2018) vs numpy 2 untested at runtime | documented in subsystem docs |
| External dependencies | STM32CubeF7, UNISIM, FFT IP, libusb, FTDI D3XX (only if FT601 is retained) | — |

---

# Part III — FPGA Project Preparation

Full detail: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md`.

**Missing configurations:** device/package/speed (CAD: `xc7a50tftg256-2`); every PACKAGE_PIN; three clock input constraints; FFT IP (`xfft_32`, `FFT_enhanced`); three RTL modules; `long_chirp_seg3_*.mem`; project file.

**Project reconstruction:** FPGA-T01 (part) → FPGA-T02 (`vivado -mode batch -source tools/vivado/create_project.tcl -tclargs xc7a50tftg256-2`) → FPGA-T03 (6 syntax/declaration edits) → FPGA-T04 (recover modules/IP, fix `.mem` paths) → FPGA-T05 (xsim) → FPGA-T06/T07 (synthesis, implementation, bitstream prerequisites).

**Source integration:** 23 synthesisable files (all `.v` except `radar_system_tb.v` and the module-less `chirp_lut_init.v`), `.mem` files as Memory Files, constraints = timing part of `cntrt.xdc` + `reconstructed/radar_system_top_schematic_derived.xdc` (64 ports mapped from the schematic with confidence levels; 25 ports UNRESOLVED because the FT601 is not wired and status/debug outputs have no nets).

**Static verification performed:** iverilog/verilator FAIL at `radar_system_top.v:312`; after scratch patches: 6 missing modules, 9 use-before-declare errors, 207 lint warnings (4 MULTIDRIVEN, 14 UNDRIVEN). `tools/check_fpga_constraints.py`: 142 placeholders, 180/180 bits unassigned. No test PASSED.

**Design-level findings that block function even after the build is repaired:** 400 MHz ADC capture not implemented (`lvds_to_cmos_400m.v:35-43`); level shifter never instantiated (ADAR1000 SPI dead); receiver controls undriven; fixed-threshold "CFAR"; bank-14 LVDS inputs on a 3.3 V bank with `DIFF_TERM`; LVCMOS33 assigned to 1.8 V bank-34 signals; no clock groups.

---

# Part IV — STM32 Firmware Preparation

Full detail: `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`.

**Project reconstruction:** STM-T01 (CubeIDE + CubeF7) → STM-T02 (regenerate `.ioc` from the verified peripheral/pin/clock tables: I2C1/2/3, SPI1/4, UART5, USART3, TIM1, OTG_FS CDC, 60 GPIO macros — all confirmed against schematic U2 nets) → STM-T03 (build-set cleanup: `.H` headers, excluded files, defines) → STM-T04 (7 defects) → STM-T05 (compile/link/size) → STM-T06 (hardware verification).

**Middleware integration:** USB Device Library Core + CDC from CubeF7; CubeMX-generated `usb_device.c`, `usbd_cdc_if.c` (must forward RX to `usbHandler.processUSBData()` in USER CODE — the repository's `main.cpp:328-339` callback is never bound), `usbd_conf.c`, `usbd_desc.c` (VID/PID unknown).

**Toolchain configuration:** `-DSTM32F746xx -DUSE_HAL_DRIVER`, Cortex-M7 FPv5-SP hard-float (ASSUMED CubeIDE defaults); `reconstructed/CMakeLists.txt` provided, UNVERIFIED.

**Build verification:** checklist in STM32 doc §6; current status: includes check FAIL (53 absent headers — expected until CubeF7 is added), no target build attempted.

**Unresolved:** HSE 8 MHz (board) vs 25 MHz (firmware) — PLL cannot lock as coded; ADF4382 pin macros collide with PA enables; ADF4382 SPI `platform_ops = NULL` → `Error_Handler`; USB RX dead; start-flag padding; `GPS_Init` never called; AD9523 CS never toggled; SPI at 36 MHz vs 10 MHz requested.

---

# Part V — Python Application

Full detail: `docs/GUI/INSTALLATION.md`, `docs/GUI/DEPENDENCIES.md`.

**Dependencies:** numpy, scipy, matplotlib (TkAgg), scikit-learn, filterpy, crcmod, pyusb (+libusb), pyftdi, pandas (CSV replay), tkinterweb (V5_Demo only). Generated `requirements.txt` (tested versions annotated; lower bounds UNVERIFIED) and `pyproject.toml` (entry points `aeris10-gui` → `GUI_V6:main`, `aeris10-gui-demo` → `GUI_V6_Demo:main`).

**Installation:** GUI-T01/T02 executed in a scratch venv: all packages installed and import-tested on Python 3.14.7.

**Configuration:** no config files; Google Maps API key placeholder in V4–V6; USB VID/PID for FTDI only (FT2232H 0403:6010 in V2–V5; FT601 0403:6030/6031 in V6, unsupported by pyftdi); STM32 CDC opened by raw bulk endpoints (platform-problematic).

**Offline validation:** `GUI_V6_Demo.py` is the only hardware-free runnable program (module import verified; window launch NOT executed). `GUI_V4_2_CSV.py` + `test_radar_data.csv` verified consistent (synthetic data). `GUI_V6.py` and `GUI_V5_Demo.py` cannot run (stubs / missing methods); `GUI_V1.py` is a fragment with a syntax error.

**Protocol:** GUI ↔ firmware settings packet consistent (82 B big-endian); start-flag padding breaks firmware parsing; FPGA packet format differs from every GUI parser; GPS text format mismatch. Documentation (`04_usb_protocol.md`) wrong on endianness and MCU family.

---

# Part VI — PCB Manufacturing Package Preparation

Full detail: `docs/PCB/*.md`, `docs/BOM/README.md`.

**CAD inspection (executed on XML):** formats/versions, sheet/part/net counts, routing completeness (airwires), approved DRC/ERC, layer setup, DRU parameters, outlines and holes, connector/net maps, sch/brd consistency — tabulated per board.

**Output generation:** executed on 2026-10-09 through KiCad 10 (`tools/kicad_pcb_pipeline.sh`): Gerber X2, Excellon PTH/NPTH + maps, layer/assembly/outline PDFs, per-layer SVG, DXF, STEP, P&P, IPC-2581, IPC-D-356, DRC (rules from the EAGLE DRU) and 3-D renders for all four boards → `engineering/PCB/<BOARD>/` (README with hole table, cross-check and checklist; `STACKUP.md`). The EAGLE-native path (P-EAGLE-01..09, P-KICAD-01 in `00_COMMON_EAGLE_PROCEDURES.md`) remains the authoritative export and is still not executed. Main/Power packages are PARTIAL (unfinished routing: 15 / 308 unconnected items after pour fill).

**BOM preparation (executed):** `tools/gen_eagle_bom.py` → 776 / 312 / 25 / 184 references in 98 / 28 / 11 / 40 lines; **0 MPN attributes on any board**; 244 / 80 / 6 / 47 references without value. Validation procedure in `docs/BOM/README.md`. System-level items (GPS, IMU, barometer, TMP37 ×8, stepper + TB6600-class driver, slip ring, fans, antenna, enclosure, cables) have no part numbers.

**Manufacturing checks:** `tools/check_manufacturing_files.py` FAIL for the designer-released folder (`4_Schematics and Boards Layout/4_7_Production Files/`: no Gerber/drill; Synth P&P + BOM only); with `--include-generated` (KiCad package) exit 0. `engineering/VALIDATION/PCB_CROSS_CHECK.md`: 32/32 EAGLE↔KiCad count checks OK. Stack-up unresolved for all boards (`Stack_Hybrid.png` 6-layer unlabeled vs DRU vs PCBWay note). README's "All Gerber files are available" is false.

---

# Part VII — Mechanical Documentation

Full detail: `docs/MECHANICAL/*.md`.

**Available design evidence:** PCB outlines and mounting holes from the `.brd` files (drawn in `docs/MECHANICAL/drawings/`; DXF/STEP/1:1 plan view/dimension sheets in `engineering/MECHANICAL/`): Main 260 × 300 mm / 8 × Ø3.2; Power 280 × 300 mm / 8 × Ø3.2 (hole pattern suggests a smaller final outline — UNRESOLVED); RF PA 35 × 60 mm / 7 × Ø3.2; Synth 100 × 100 mm / 4 × Ø3.2. Element spacing λ/2 ≈ 14.3 mm and 16-element aperture 214.3 mm (`02_hardware/04_antenna_beamforming.md:280,288`). Stepper 200 steps/rev, 50 azimuth positions (`main.cpp:189,195`).

**Missing models:** enclosure, antenna (two contradictory waveguide simulations, no patch CAD), pedestal/slip ring/stepper/fans, heatsinks, cables, 3-D PCB models, thickness and mass. `10_docs/assembly_guide.md` and `10_docs/Hardware/Enclosure` (README) do not exist.

**Required drawings:** A1–A11 list in `ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md`; delivered: outline/dimension drawings, block/interconnection diagrams, CONCEPTUAL exploded view, parts list, assembly sequence (`engineering/ASSEMBLY/`); BLOCKED: enclosure, antenna, pedestal, cooling (guides MDR-01…05).

**Documentation requirements:** minimum content of the assembly guide (§2 of that document), exploded-view procedure (§3).

---

# Part VIII — Integration Dependencies

**Subsystem interface inventory:** `docs/SYSTEM/BLOCK_DIAGRAM.md` §2–3 (Power→Main/Synth rail connectors; Main↔Synth JP1/JP13 control + SMA clocks; Main↔PA 16 × bias/sense + 17 SMA pairs; Main↔host mini-USB; peripheral headers).

**Documentation gaps:** anonymous nets on 34 Main-Board SMAs and 16 PA connectors (assignment table must be produced from the schematic); cable lengths/gauges; LO SMA mapping; antenna feed transition.

**Configuration consistency:** eight open conflicts K1–K8 (FPGA part; HSE; host data path; PA supply; packet format; ADF4382 pins; Synth oscillators; antenna variant).

**Unresolved integration assumptions:** `clk_100m` is free-running (AD9523 OUT6) while the RTL crosses 400 MHz/4 samples into it without a phase relationship — sample drops/duplicates are expected unless the design is changed; the 3.3 V bank-14 LVDS inputs; whether the SPI1 pass-through through the FPGA was ever functional (level shifter not instantiated).

---

# Part IX — Test and Acceptance Procedures

`docs/TESTING/VALIDATION_PLAN.md` lists 10 FPGA, 10 STM32, 9 Python, 9 PCB and 3 repository tests with type (design check vs physical), command, tool availability and executed result; `ACCEPTANCE_CRITERIA.md` gives 41 objective criteria.

**Executed and PASSED:** P-01 dependency install, P-03 import test, P-08 demo-data consistency, B-03 embedded libraries, B-07 outline extraction, F-05 pin-map generation (generation only), S-07 GPIO macro cross-check (with two conflicts found), R-01 inventory.

**Executed and FAILED (expected, documenting the state):** F-01..F-04 (RTL parse/elaborate/lint/constraints), S-01 (includes), P-02 (GUI_V1 syntax), B-04 (Main/Power consistency), B-05 (BOM MPN), B-06 (manufacturing files), R-02 (doc links), R-03 (manifest: 25 P0 items missing).

**Not run (tools/hardware unavailable):** Vivado synthesis/timing/bitstream, xsim, ARM build, EAGLE ERC/DRC/CAM, GUI window launch, all physical tests.

**Evidence collection:** logs under `build/` (lint logs produced), test IDs referenced in reports; physical tests require instrument records.

Run everything: `bash tools/run_all_checks.sh` → currently 7 of 8 checks FAIL, 1 PASS (inventory).

---

# Part X — Final Readiness Report

## X.1 Completed items (this reconstruction)

- Documentation tree per specification + `docs/BOM`, `docs/SYSTEM`, `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`.
- 11 validation/generation scripts in `tools/` + `tools/vivado/create_project.tcl` (non-destructive; exit codes; stdlib only).
- Schematic-derived FPGA pin map (64/67 ports) and candidate XDC.
- BOMs for four boards; PCB outline/hole drawings; connector matrix; block diagram.
- Python `requirements.txt` / `pyproject.toml`, verified by installation.
- STM32 `.ioc` content reconstruction tables; Cube package checker; CMake template (unverified).
- **Version 1.1:** engineering drawings package `engineering/` — 73 registered drawings (39 SOURCE-DERIVED, 28 PARTIAL, 1 CONCEPTUAL, 5 BLOCKED), 13 additional generator/validation scripts (29 in `tools/` total). See Part XI.

## X.2 Missing items (P0, from `03_MISSING_COMPONENTS.md`)

FPGA: parseable RTL, pin-complete XDC, project, 3 RTL modules, 2 FFT IP, seg3 `.mem`, portable paths, device decision, ADC capture structure, multi-driven registers, level shifter, host data path (12). STM32: `.ioc`, linker, startup, build system, 4 USB files, HAL, CMSIS, HSE conflict, ADF4382 pins, ADF4382 SPI ops, USB RX (14 entries). PCB: Gerber/drill/BOM for 4 boards, two unfinished layouts, stack-ups (11). Total P0: 37 register entries; manifest check reports 25 missing P0 file patterns.

## X.3 Blockers (cannot be resolved from repository content)

1. FPGA part number (XC7A50T-2FTG256I vs XC7A100T).
2. Original FPGA project (missing modules, FFT IP, `.mem` generator, seg3 files, authoritative TX LUT).
3. STM32 HSE crystal (8 vs 25 MHz) and board revision.
4. Host data path architecture (FT601 unwired).
5. Main and Power Board layout completion; stack-ups for all boards.
6. All mechanical design data (enclosure, antenna, pedestal, part numbers).
7. PA supply architecture (22 V rail) and Synth oscillator topology.

## X.4 Open technical questions

Listed per subsystem: FPGA doc §8 (6 items), STM32 doc §5 (10 items), PCB docs §"open items", Mechanical gap analysis §7 (5 items), Block diagram §4 (K1–K8).

## X.5 Recommended next engineering actions (ordered, with dependencies)

1. **R-SYS-01, R-FPGA-01, R-STM-05, R-PCB-06** — architecture/designer decisions (host link, FPGA part, HSE, stack-ups). Everything else depends on these.
2. **R-STM-01..03** — toolchain + CubeMX regeneration + build-set cleanup → first firmware build (independent of hardware).
3. **R-FPGA-03..06** — syntax fixes, Vivado project, module/IP recovery, `.mem` → first elaboration.
4. **R-PCB-03, R-PCB-04, R-PCB-05** — export RF PA and Synth production packages; complete BOMs with MPNs (can proceed in parallel with 2–3).
5. **R-STM-04, R-STM-06, R-STM-07** — firmware functional fixes → bench test with the GUI (needs 2).
6. **R-FPGA-07..10** — functional RTL redesign (ADC capture, CDC, single drivers, CFAR), constraints, testbench, synthesis → bitstream (needs 1, 3).
7. **R-PCB-01, R-PCB-02** — finish Main and Power layouts (needs 1), then export.
8. **R-GUI-01..03** — consolidate GUI, tests, packaging (needs 1 for protocol).
9. **R-MECH-01, R-MECH-02** — obtain CAD, write assembly guide, exploded view (needs 7 for board outlines).
10. **R-DOC-01..03** — README/LICENSE/.gitignore/links, datasheets, `STM32_ALGO.docx`.

## X.6 Completeness metric

Method: acceptance criteria MET ÷ total criteria (`docs/TESTING/ACCEPTANCE_CRITERIA.md`), and manifest items present ÷ manifest items (`tools/check_missing_files.py`).

| Metric | Value |
|---|---|
| Acceptance criteria MET | 5 / 41 = **12 %** (AC-P1, AC-P2, AC-M1, AC-D1, AC-D5) |
| Expected-artefact manifest present | 24 / 59 = **41 %** after v1.1 (documentation + GUI packaging + Synth P&P/BOM + 13 engineering-package entries); P0 present 1 / 26 — unchanged, because generated Gerbers are not the designer-released export |
| Documentation package of the specification | 20 / 20 files = 100 % (plus 8 extra) |
| Build-artefact completeness (bitstream, firmware image, GUI package, 4 manufacturing packages) | 0 / 7 = **0 %** designer-released; 2 / 4 manufacturing packages exist as generated KiCad conversions of routed boards (RF PA, Synth) and 2 as PARTIAL conversions of unfinished layouts |
| Engineering drawings (addendum §26) | 73 registered: 68 generated (39 SOURCE-DERIVED + 28 PARTIAL + 1 CONCEPTUAL), 5 BLOCKED; 0 VERIFIED |

These percentages measure verified reproducibility, not effort; the design-level defects found (Parts III–IV) mean that even with all missing files recovered, functional hardware is not established by any evidence in the repository.


---

# Part XI — Engineering Drawings & CAD Package (addendum §16–26, version 1.1)

Index: `engineering/README.md`. Register: `engineering/DRAWING_REGISTER.md` (73 drawings, statuses, missing data, file check 0 problems). Recovery guides: `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md` (MDR-01…MDR-11). Validation: `engineering/VALIDATION/{DRAWING_CHECKS,CAD_EXPORT_LOG,PCB_CROSS_CHECK,UNRESOLVED_GEOMETRY}.md`.

## XI.1 Electrical schematics (§16)

| Deliverable | Location | Status |
|---|---|---|
| Editable native schematics | the EAGLE `.sch` files (unchanged masters); KiCad twins not created (GUI-only import, MDR-10) | present |
| SVG sheets + multi-page PDF + PNG, 7 sheets, title block with project/ID/rev/date/sheet/units/source/status | `engineering/ELECTRICAL/schematics/<BOARD>/` (`tools/render_eagle_schematic.py`, `tools/svg_sheets_to_pdf.py`) | SOURCE-DERIVED |
| Netlist (by net, by part), IPC-D-356 | `engineering/ELECTRICAL/netlists/<BOARD>_netlist*.csv`, `engineering/PCB/<BOARD>/ipc/*.d356` | SOURCE-DERIVED |
| Component-to-net report with connector pin-outs | `engineering/ELECTRICAL/connection_diagrams/<BOARD>_connection_report.md` | SOURCE-DERIVED |
| Unresolved-connection report (single-pin nets, open pins, sch↔brd parity, airwires) | `engineering/ELECTRICAL/netlists/<BOARD>_unresolved_connections.md` — Synth 5 single-pin nets / 34 open pins; Main 3 / 280 / 2 390 airwires; Power 0 / 24 / 309; PA 0 / 0 | needs designer disposition |
| Missing-symbol / footprint report | `engineering/ELECTRICAL/netlists/<BOARD>_missing_symbols_footprints.md` — none missing on any board | MET |

## XI.2 System architecture diagrams (§17)

SYS-01 block diagram (DOT + Mermaid), SYS-02 interconnection diagram + table (every connector/cable, pins where the symbols carry them, CBL-IDs proposed), SYS-03 signal/data flow (frequencies = firmware intent), ELEC-PWR-01 power distribution + 36-rail register; SD-01…SD-07 software diagrams (auto-generated FPGA hierarchy and Python module graph; hand-authored pipeline, STM32, USB CDC, GUI runtime, end-to-end flow). All DOT files are editable; SVG/PDF/PNG rendered with Graphviz. New findings from this work: 15 (not 16) enable lines on SV1; firmware never asserts the ADTR/PA/5V5 enables; U30 ADM7151 input from VIN; `+1V8_CLOCK` needed by two boards from one output; J22/J23 are the LO inputs.

## XI.3 PCB fabrication and assembly drawings (§18)

Per board, the 15 items of §18 are tabulated in `engineering/PCB/<BOARD>/README.md` §1 with file names and status. Stack-up: layer order and copper from the DRU; materials/thickness/finish/impedance BLOCKED — MISSING DATA (`STACKUP.md`). Every file identifies its source board file and the absence of a source revision. DRC results (KiCad, DRU-derived rules): RF PA 48, Synth 639, Main 912 + 15 unconnected, Power 160 + 308 unconnected — dispositions pending.

## XI.4 Mechanical (§19) and exploded views (§20)

Generated from verified geometry: outline + hole DXF (two independent sources, EAGLE XML and KiCad), board-only STEP (thickness ASSUMED 1.6 mm), 1:1 plan view, dimension sheets with hole tables, pitch and mass ESTIMATES. CONCEPTUAL only: exploded view ASM-EXP-01 (balloons ↔ `PARTS_LIST.md`), assembly sequence (electrical order SOURCE-DERIVED, mechanical steps CONCEPTUAL). BLOCKED: enclosure, internal layout, antenna, cooling, pedestal — no geometry exists; guides MDR-01…MDR-06 state exactly what must be decided and how to produce the drawings in FreeCAD/KiCad.

## XI.5 Standards and status vocabulary (§22)

Title blocks carry project, drawing ID, revision, date, sheet, units, scale, source and status (ISO 7200 fields); no standards compliance is claimed. No drawing is VERIFIED: nothing was compared with an EAGLE/vendor output or with hardware (MDR-11).

## XI.6 Final drawings report (§26)

| Item | Value |
|---|---|
| Drawings identified as required | 73 registered (+ the 15-item §18 list per board inside each PCB README) |
| Existing drawings found | drawio/jpg/dwg block diagram, unlabelled stack-up PNG, Synth P&P + BOM, photos, first-pass outline SVGs — none dimensioned |
| Generated from verified evidence (SOURCE-DERIVED) | 39 |
| Partially reconstructed (PARTIAL / CONCEPTUAL) | 28 + 1 |
| Blocked by missing source information | 5 (enclosure, internal layout, antenna, cooling, pedestal) |
| Native editable files created | 11 DOT, 1 Mermaid, 4 `.kicad_pcb` + `.kicad_pro`, 16 DXF, 8 STEP, 78 SVG (schematics, layers, mechanical, exploded), 16 CSV, 4 Gerber job sets |
| PDF/SVG/PNG exports | 53 PDF, 78 SVG, 32 PNG |
| CAD validation | export log 0 failed steps (final run); EAGLE↔KiCad cross-check 32/32; register file check 73 drawings / 0 problems; DRC executed (not passed) |
| Remaining engineering decisions | K1–K8 (part, HSE, host link, PA supply, packet format, ADF4382 pins, oscillators, antenna) + G-01…G-12 geometry + MPNs + stack-ups |


---

# Part XII — Proposed Designs for the Missing Elements (version 1.2)

The BLOCKED drawings of Part XI (enclosure, internal layout, antenna, cooling, pedestal) and conflict K4 (22 V PA supply) now have **PROPOSED DESIGNS** under `engineering/DESIGN/` (index `engineering/DESIGN/README.md`, basis and decision log `00_DESIGN_BASIS.md`, parameters `design_parameters.json`). They are new engineering content derived from the verified constraints (board outlines/holes, connector positions from the P&P files, firmware timing and scan geometry, QPA2962/RO4350B datasheets) plus fifteen logged decisions D-01…D-15; nothing was simulated on hardware, built or measured. Register IDs DSN-* (11 entries, status PROPOSED DESIGN).

| Element | Proposal | Native file | Key result | Must be confirmed |
|---|---|---|---|---|
| Antenna (DSN-ANT-01) | 16 horizontal rows × 8 series-fed patches, 14.3 mm row pitch, RO4350B 0.508 mm, end-launch 2.92 mm per row, equal-length feeds | `engineering/DESIGN/ANTENNA/kicad/aeris10_patch_array.kicad_pcb` | patch 9.35 × 7.30 mm, panel 165 × 248 mm, est. ≈ 25 dBi, HPBW ≈ 6.3° (el) / 10° (az) | openEMS run (`openems_patch_row.py`), coupon measurement, B (bandwidth) |
| Thermal (DSN-THM-01) | per-chirp drain gating → 68 W average (vs 591 W as coded); 300 × 300 × 10 Al spreader with 2 fin fields, 2 × 60 mm fans, ≥ 16 CFM | `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` | PA base ≈ 66 °C at 45 °C ambient | PA-board via-field Rth, fan parts |
| 22 V PA supply (DSN-PSU-01) | 2-phase boost 12–17 → 22 V, LM5069 hot-swap enable from `EN/DIS_RFPA_VDD`, 16 × LTC7003/N-FET pulse gates from a `TX_GATE` line, ≥ 2.7 mF bulk | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.svg` | 45.6 A pulsed / 3.5 A average | FPGA spare pin for `TX_GATE`, KiCad capture (MDR-12) |
| Radar head (DSN-MECH-3D, -01…-04) | 315 × 315 × 133 mm folded-Al chassis; all boards vertical behind the antenna: antenna → PA plate → 16 PA (4 × 4) → Main → Synth → Power; radome window; side cooling ducts | `engineering/DESIGN/MECHANICAL/CAD/aeris10_head_pedestal.FCStd` (+ STEP/STL/DXF) | mass ESTIMATE ≈ 9.9 kg (envelopes as solids) | component heights (D-07), fasteners, sealing |
| Pedestal (DSN-MECH-05) | 360 × 360 × 130 mm base, slewing bearing OD190/ID100, 1:3 GT3 belt to a NEMA 23, 12-circuit through-bore slip ring | same FCStd | needs `Stepper_steps = 600` in `main.cpp:195` | part selection, mast interface, driver location |
| Harness (DSN-HAR-01) | 144 cables with proposed lengths (≈ 42 m) from connector positions | `engineering/DESIGN/HARNESS/harness_schedule.csv` | — | rail pairs not matched by net name; first fit |

Regeneration: see `engineering/DESIGN/README.md`. Tools added: `tools/design_antenna_array.py`, `design_thermal.py`, `design_pa_supply_schematic.py`, `design_layout.py`, `design_mechanical_freecad.py`, `design_mechanical_drawings.py`, `stl_to_svg_iso.py` (FreeCAD 1.1 installed in `~/Applications` for the 3-D model).


---

# Part XIII — BETA Completions (version 1.3)

Everything that was missing now exists at least in a BETA state under `beta/` (index `beta/README.md`; each sub-project has `README.md` + `CHANGELOG.md`; originals untouched). BETA = builds/simulates/routes/tests on this machine; **not** synthesised in Vivado, flashed, fabricated, measured, or reviewed by the original designer. Repository: `https://github.com/herasymyuks/PLFM_RADAR-aeris` (all work pushed).

| Sub-project | What exists now | Verified by (executed) | Still open |
|---|---|---|---|
| `beta/fpga` | RTL copies with syntax/driver fixes; 5 missing modules written (SDR-LVDS ADC capture with IDDR, FFT-domain matched-filter chain, range-bin decimator, FFT wrappers with behavioural core + IP settings); seg3 `.mem` generated (the `.mem` files proved to be conj-FFT references); timing + schematic-derived XDC; Vivado Tcl | `beta/fpga/build.sh`: iverilog elaboration (sim + synth views) PASS, verilator 0 errors, 5 self-checking testbenches PASS incl. end-to-end smoke test (pulse compression peaks at the expected bins, 2688 packets, 0 errors) | synthesis/timing (400 MHz single-rate DDC will not close → ISERDES redesign), matched filter not pipelined, FFT IP generation, 116 unconstrained port bits, host path (see DSN-LINK-01) |
| `beta/stm32` | CMake project with Arm GNU 14.2 + STM32CubeF7 (pinned sparse clone), hand-written CubeMX-equivalent USB CDC/startup/linker/HAL conf, 11 defect fixes (incl. 2 newly found AD9523 init bugs), hardware-truth decisions (8 MHz HSE clock tree, ADF4382 pins, power-enable sequencing), host-link bridge driver | `beta/stm32/build.sh` exit 0 (FLASH 92 KB, RAM 17 KB); host tests 4/4 (settings parser incl. padded frames, beam matrix, AD9523 register table, I2C timing) | CubeMX regeneration, flash + bring-up, ADAR1000 `VM_*` tables empty in the original, production VID/PID |
| `beta/gui` | `aeris10_gui` package: firmware-exact settings packet, RTL packet parser, bridge-frame parser, CDC I/O, CA-CFAR/DBSCAN/Kalman, simulator in RTL format, Tk UI, PyInstaller app | `pytest -q`: 55 passed; `--selftest` exit 0; PyInstaller `dist/aeris10-gui --demo --selftest` exit 0 | hardware CDC test, hardware source switch to bridge frames, Windows/Linux packaging |
| `beta/pcb` | KiCad completion of the four boards: Main 15 → 0 unconnected (arc stubs, +3V3_FT cluster placed/routed, polygon-net dispositions), RF PA 1 → 0, Power 308 → 89 (132 parts placed, Freerouting 2.5.0, GND plane), Synth DRC disposition; BOMs with proposed MPNs (HIGH/MEDIUM/LOW/EMPTY counts per board); `FAB_NOTES.md` with PCBWay stack-ups and measured impedance widths; full re-exported packages | DRC reports per board (`exports/reports/`), export logs exit 0 | Power Board 89 pour-to-pour connections (manual), Main U69/U7 paddle nets + BPF2 polygons (schematic fix), 0201 silkscreen density, stack-up/MPN sign-off |
| `engineering/DESIGN/HOST_LINK` (DSN-LINK-01) | FPGA→host path: option A FT601 pin plan on the 50 free bank-35 pins (+ XDC, parts to add for Main Board rev. B); option B SPI bridge over the already-routed DIG_5/6/7 + SPI1 lines: RTL packer + SPI slave, STM32 driver (integrated, builds), GUI parser (tested on the RTL vector) | iverilog `PASS tb_host_bridge`, verilator clean, firmware build exit 0, pytest 9 passed | bridge integration into the beta top (in progress), bench SPI/CDC test, Main Board rev. B |
| `engineering/DESIGN/ANTENNA` | openEMS built from source; one-row FDTD run and tuning loop | S11 −18 dB at 10.5 GHz, contiguous −10 dB band only ≈ 128 MHz (comb response), row directivity 11.5 dBi | feed topology if B > ~100 MHz; 16-row coupling; coupon measurement |
| `engineering/DESIGN/MECHANICAL` (detail) | 51-part FreeCAD model (tray with flanges, front plate, lid, window stack, PA plate with tapped holes and brackets, carrier rails, standoffs, gland plate; pedestal plates, bearing, pulleys, slip ring, motor bracket, mast flange); flat patterns with bend allowance; assembly section with fasteners; parts list with fastener totals | model builds; register file check 0 problems | bend reliefs/welds, lid stiffening, part numbers, sealing test |

Tooling installed on the authoring machine for this phase (all user-level): KiCad 10.0.6, FreeCAD 1.1.4, openEMS (source build, `~/opt/openEMS`), Arm GNU Toolchain 14.2 (tarball), OpenJDK 27 + Freerouting 2.5.0, Graphviz, poppler.
