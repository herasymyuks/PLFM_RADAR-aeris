# 05 — Traceability Matrix

Maps every requirement of the task specification (`claude.md`, sections 2–14) and every system claim of `README.md` to the repository evidence, the generated artefact that addresses it, and the verification status. Status: MET (artefact exists and its check was executed), PARTIAL (artefact exists, check not executable here), NOT MET (needs designer input or tools not available).

## A. Task specification (`claude.md`)

| Req. | Requirement | Evidence examined | Artefact | Verification | Status |
|---|---|---|---|---|---|
| §2 | Repository inventory with per-file status | all 467 original files + generated | `docs/01_REPOSITORY_INVENTORY.md`, `tools/repo_inventory.py`, `tools/gen_inventory_doc.py` | executed, 482 rows | MET |
| §2 | Dependency map | subsystem analyses | `docs/02_DEPENDENCY_MAP.md` | reviewed | MET |
| §3.1 | Enumerate unresolved XDC constraints | `cntrt.xdc` | `tools/check_fpga_constraints.py` (142 placeholders) | executed | MET |
| §3.2 | RTL top-level ports | `radar_system_top.v:18-115` | FPGA doc §3 (67 ports/180 bits) | executed | MET |
| §3.3 | Match ports to design documentation | `02_hardware/05_fpga_board.md`, schematic U42 | FPGA doc §3.1, `PIN_MAP_FROM_SCHEMATIC.md` | 64 ports mapped from schematic | PARTIAL (designer confirmation) |
| §3.4 | Which assignments can be verified | schematic pads vs AMD package file | FPGA doc §3.1 caveat | not verifiable without package file | PARTIAL |
| §3.5 | Missing I/O standards and timing | XDC lines 14-27, 85, 92, 160-167, 305-321 | FPGA doc §3.3 | executed (21 bits w/o IOSTANDARD) | MET |
| §3.6 | Vivado project creation procedure | — | FPGA-T02, `tools/vivado/create_project.tcl` | not executed (no Vivado) | PARTIAL |
| §3.7 | Elaboration and simulation procedures | iverilog/verilator runs | FPGA doc §4, FPGA-T05, `tools/fpga_lint.sh` | executed (FAIL recorded) | MET (procedure) |
| §3.8 | Report-inspection procedure | — | FPGA-T06 | not executed | PARTIAL |
| §3.9 | Bitstream prerequisites | — | FPGA-T07 (9 items) | — | MET (list) |
| §3 | No invented pins; UNRESOLVED marking | — | `reconstructed/*.xdc` comments, FPGA doc §3.2 | 25 ports marked UNRESOLVED | MET |
| §4.1 | MCU identification | schematic U2, README | STM32 doc §1 | executed (netlist) | MET |
| §4.2–4.4 | Cube package, HAL components, USB CDC deps | `hal_conf.h`, includes | STM32 doc §2, §3.4, §3.5; `tools/check_stm32_includes.py`, `tools/stm32_check_cube_package.sh` | includes check executed | MET |
| §4.5–4.6 | Clock and GPIO/peripheral configuration | `main.cpp:1803-1849`, MSP, `main.h` | STM32 doc §3.1–3.3 | cross-checked with schematic | MET (HSE conflict flagged) |
| §4.7–4.9 | Memory/linker, startup, compile prerequisites | absent files | STM32 doc §3.6, STM-T01..T05, `reconstructed/CMakeLists.txt` | not compiled | PARTIAL |
| §4.10 | Firmware verification steps | — | STM-T06 | not executed | PARTIAL |
| §4 | `.ioc` reconstruction of verified portions; confirmed vs assumed | — | STM32 doc §3 + §5 table | — | MET |
| §5 | Per-board readiness reports with 10 items | EAGLE XML | `docs/PCB/MAIN_BOARD.md`, `POWER_SUPPLY.md`, `RF_PA.md`, `FREQUENCY_SYNTHESIZER.md`, `00_COMMON_EAGLE_PROCEDURES.md` | XML checks executed; CAD runs not | MET (report) / NOT MET (outputs) |
| §5 | No fabrication-ready claim without evidence | — | each PCB doc verdict | — | MET |
| §6 | Python constraints, deps, assets, platform | 27 scripts | `docs/GUI/DEPENDENCIES.md`, `INSTALLATION.md`, `requirements.txt`, `pyproject.toml`, `tools/check_python_imports.py` | venv install + import executed | MET |
| §6 | Unverified ranges marked | — | `requirements.txt` comments | — | MET |
| §7 | Mechanical search, missing references, gap analysis, assembly requirements | `find`, README | `docs/MECHANICAL/MECHANICAL_GAP_ANALYSIS.md`, `ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md`, `drawings/*.svg` | drawings generated | MET (analysis) / NOT MET (CAD) |
| §8 | Test plan and acceptance criteria with executed status | — | `docs/TESTING/VALIDATION_PLAN.md`, `ACCEPTANCE_CRITERIA.md`, `tools/run_all_checks.sh` | executed | MET |
| §9 | Master manual Parts I–X | — | `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` | — | MET |
| §10 | Instruction format (Task ID … Completion criteria) | — | FPGA-T0x, STM-T0x, GUI-T0x, P-EAGLE-0x | — | MET |
| §11 | Evidence with path/line; missing-component register with ID/Evidence/Impact/Recovery/Verification/Priority | — | `docs/03_MISSING_COMPONENTS.md`, `04_RECOVERY_TASKS.md`, this file | — | MET |
| §12 | Automation scripts (inventory, missing files, deps, references, imports, placeholders, links, manufacturing, build checks), non-destructive, exit codes | — | `tools/` 11 scripts + Tcl | each executed; none modifies sources | MET |
| §13 | Documentation tree | — | all listed files present + extras (`docs/BOM`, `docs/SYSTEM`) | `tools/check_missing_files.py` DOC-* | MET |
| §14 | Perform all safe actions; preserve originals; no silent design changes | — | no original file modified (new files only); design changes only as documented tasks | `git status`-style check in manual Part X | MET |
| user add-on | BOM lists, schematic package, block diagram, approximate dimensional drawings | EAGLE files | `docs/BOM/*`, `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md` P-EAGLE-08 (schematic PDF procedure; PDFs not producible without EAGLE), `docs/SYSTEM/BLOCK_DIAGRAM.md`, `docs/MECHANICAL/drawings/*.svg` | generated | MET (BOM, diagram, PCB outlines) / PARTIAL (schematic PDFs) / NOT MET (enclosure/mass) |

## B. README claims vs evidence

| README line | Claim | Evidence | Status |
|---|---|---|---|
| 11, 23-24 | 10.5 GHz, two variants 3 km / 20 km | no measurement data in repo; `research/03_hw_improvements.md` assumptions | UNVERIFIED |
| 29 | "Complete schematics, PCB layouts, firmware, and software available" | schematics yes; two layouts unfinished; firmware/FPGA cannot build; GUI partially | NOT MET |
| 52 | XC7A100T | CAD XC7A50T-2FTG256I | CONTRADICTED |
| 63 | STM32F746xx | STM32F746ZGT7 (U2) | MET |
| 44-50 | AD9523-1 clock, ADF4382 ×2 | Synth board IC1, U1, U6 | MET (CAD) |
| 54-62 | FPGA processing chain incl. CFAR, MTI, Doppler, USB | RTL: CFAR is a threshold placeholder, matched filter chain missing, USB not wired | NOT MET |
| 80 | 16 × QPA2962 PA boards (Extended) | one RF PA board design; supply rail unresolved | PARTIAL |
| 82-83 | antenna arrays 8×16 / 32×16 | no CAD; contradictory simulations | NOT MET |
| 104-106 | GUI with map | V5 complete (map needs API key); V6 incomplete | PARTIAL |
| 139 | "All Gerber files are available" | none | CONTRADICTED |
| 140 | BOM in production files | Synth only, no MPN; generated BOMs now in `docs/BOM/` | PARTIAL |
| 141 | assembly guide `10_docs/assembly_guide.md` | missing | CONTRADICTED |
| 143 | enclosure files `10_docs/Hardware/Enclosure` | missing | CONTRADICTED |
| 3 | MIT licence badge | no LICENSE file | UNVERIFIED |

## C. Generated artefact → source evidence

| Artefact | Derived from | Tool |
|---|---|---|
| `docs/01_REPOSITORY_INVENTORY.md` | file tree | `tools/gen_inventory_doc.py` |
| `9_Firmware/9_2_FPGA/reconstructed/*.xdc`, `PIN_MAP_FROM_SCHEMATIC.md` | `RADAR_Main_Board.sch` U42, `main.cpp` | `tools/gen_xdc_from_schematic.py` |
| `docs/BOM/*` | four `.sch` | `tools/gen_eagle_bom.py` |
| `docs/MECHANICAL/drawings/*.svg` | four `.brd` layer 20 + holes | `tools/gen_board_outline_svg.py` |
| `docs/SYSTEM/BLOCK_DIAGRAM.md` §2 | connector nets of four `.sch` | `xml.etree` extraction (procedure in `tools/extract_eagle_netlist.py`) |
| `9_Firmware/9_3_GUI/requirements.txt`, `pyproject.toml` | imports of GUI files; venv install | `tools/check_python_imports.py` |
| `9_Firmware/9_1_Microcontroller/reconstructed/CMakeLists.txt` | include graph, `hal_conf.h` | `tools/check_stm32_includes.py` |
| `tools/vivado/create_project.tcl` | RTL file list | `tools/fpga_lint.sh` file selection |
