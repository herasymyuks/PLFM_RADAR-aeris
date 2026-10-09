# Acceptance Criteria — AERIS-10 Reconstruction

Each criterion is objective, references the test ID in `VALIDATION_PLAN.md`, and states the evidence that must exist. Current status (2026-10-08) is given honestly: nothing hardware-related is accepted.

## A. FPGA

| ID | Criterion | Evidence required | Status |
|---|---|---|---|
| AC-F1 | RTL parses and elaborates with iverilog and verilator with zero errors (F-01..F-03) | `build/lint/iverilog_top.log` empty of errors; verilator 0 `%Error` | **NOT MET** |
| AC-F2 | No module instantiated without definition; all Xilinx IP as committed `.xci` | Vivado elaboration log; `ls 9_Firmware/9_2_FPGA/ip/*.xci` | **NOT MET** (6 missing) |
| AC-F3 | `cntrt.xdc` (or successor) has zero placeholders and every top-level port bit constrained or removed; F-04 exit 0 | tool output | **NOT MET** |
| AC-F4 | Pin map confirmed by the designer against the AMD FTG256 package file and the routed board | signed-off `PIN_MAP_FROM_SCHEMATIC.md` with "VERIFIED" column | **NOT MET** |
| AC-F5 | Synthesis on the confirmed part with ≤ 90 % of LUT/FF/DSP/BRAM and zero unresolved CRITICAL WARNINGs | `build/vivado/util.rpt` | **NOT MET** |
| AC-F6 | Timing closure WNS ≥ 0, WHS ≥ 0 on all constrained clocks; `report_cdc` no critical | `timing.rpt`, `cdc.rpt` | **NOT MET** |
| AC-F7 | Testbench runs on xsim with pass/fail gating and passes | sim log with 0 assertion failures | **NOT MET** |
| AC-F8 | Bitstream generated and archived with its build log | `build/vivado/*.bit` + log | **NOT MET** |
| AC-F9 | (Physical) ADC capture validated with a CW tone: correct frequency bin, no bit errors over 10 s | ILA capture / host data | NOT RUN |

## B. STM32

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-S1 | Cube package check exit 0 (S-02) | script output | NOT MET (no package) |
| AC-S2 | `.ioc` regenerated; generated MSP equals repository MSP in peripheral content | diff | NOT MET |
| AC-S3 | `tools/check_stm32_includes.py` exit 0 after adding Cube sources to the include path (run with `--root` of the full project) and zero case mismatches | tool output | NOT MET |
| AC-S4 | Firmware compiles and links with `arm-none-eabi-g++`, zero errors; size < 1 MB flash / 320 KB RAM | `build/stm32/*.map`, `size` output | NOT MET |
| AC-S5 | Conflicts C1–C7 closed with documented decisions | `docs/04_RECOVERY_TASKS.md` entries R-STM-xx marked DONE | NOT MET |
| AC-S6 | (Physical) CDC enumerates; start flag + settings accepted; status string received | host log | NOT RUN |
| AC-S7 | (Physical) rail sequencing order and delays match `Power Management V6.xlsx` | scope captures | NOT RUN |

## C. Python GUI

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-P1 | `pip install -r requirements.txt` succeeds on a clean venv (P-01) | pip log | **MET** (2026-10-08, Python 3.14.7) |
| AC-P2 | All third-party imports succeed (P-03) | tool output | **MET** for GUI modules |
| AC-P3 | Every file in `9_Firmware/9_3_GUI` parses (P-02) | tool exit 0 | NOT MET (`GUI_V1.py`) |
| AC-P4 | `GUI_V6_Demo.py` starts, shows moving targets, closes with exit 0 (P-07) | screenshot + exit code | NOT RUN |
| AC-P5 | A unit-test suite exists and passes (parsers, CFAR, packet decode) (P-06) | pytest log | NOT MET (no tests) |
| AC-P6 | One hardware GUI decodes the real firmware/FPGA packet format end-to-end (P-09) | capture + decoded targets | NOT RUN (formats inconsistent today) |
| AC-P7 | Packaged demo runs on a machine without Python | installer test log | NOT RUN |

## D. PCB

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-B1 | Fresh ERC and DRC reports with 0 unapproved errors for each board (B-01, B-02); every approved error justified | reports under `docs/PCB/reports/` (to be created) | NOT MET |
| AC-B2 | `RATSNEST` "Nothing to do" and 0 elements outside the outline for Main and Power | EAGLE status line screenshot | NOT MET |
| AC-B3 | sch/brd consistent, single EAGLE version per board (B-04) | consistency check pass | NOT MET (Main, Power) |
| AC-B4 | Gerber + drill + fab + assembly + P&P + BOM(MPN) + schematic PDF for all four boards (B-06 exit 0) | `tools/check_manufacturing_files.py` exit 0 | **PARTIALLY MET** (2026-10-09): a complete *generated* package exists for all four boards (`engineering/PCB/<BOARD>/`, KiCad conversion; `--include-generated` exit 0) and schematic PDFs (`engineering/ELECTRICAL/schematics/`); NOT MET for the designer-released EAGLE export (`4_Schematics and Boards Layout/4_7_Production Files/`), MPNs and vendor fab notes |
| AC-B5 | BOMs 100 % MPN, 0 empty values, DNP column (B-05) | `docs/BOM/*` regenerated with `mpn_status` all VERIFIED | NOT MET |
| AC-B6 | Vendor stack-up drawing per board consistent with DRU and impedance note | fab documents | NOT MET |
| AC-B7 | (Physical) impedance coupons 50 Ω ± 10 %, 100 Ω ± 8 % | TDR report | NOT RUN |
| AC-B8 | Design conflicts K1 (FPGA part), K2 (HSE), K3 (host link), K4 (PA supply), K7 (oscillators) closed | decision records | NOT MET |

## E. Mechanical

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-M1 | Outline/hole drawings for all PCBs | `docs/MECHANICAL/drawings/*.svg`; `engineering/MECHANICAL/` (DXF, STEP, 1:1 plan view, dimension sheets) | **MET** (generated from `.brd`; thickness ASSUMED) |
| AC-M2 | Enclosure, antenna and pedestal CAD committed with drawings | STEP + PDF under `10_docs/Hardware/` (missing today) | NOT MET |
| AC-M3 | Assembly guide `10_docs/assembly_guide.md` (missing today) with the content of `ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md` §2 | file exists, link check passes | NOT MET |
| AC-M4 | Exploded view with balloons matching BOM | PDF | PARTIAL (2026-10-09): CONCEPTUAL view `engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.pdf` with balloons ↔ `PARTS_LIST.md`; real geometry BLOCKED (MDR-06) |
| AC-M5 | Mass table per assembly | measured or CAD-derived values | NOT MET |

## F. Documentation / repository

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-D1 | Documentation tree of `claude.md` §13 present | `tools/check_missing_files.py` DOC-* all present | **MET** after this reconstruction |
| AC-D2 | `tools/check_doc_links.py` exit 0 | tool output | NOT MET (pre-existing broken links listed in VALIDATION_PLAN R-02) |
| AC-D3 | README corrected: Gerber claim, FPGA part, `10_docs` references | diff | NOT MET (README not modified — content change needs the owner's decision) |
| AC-D4 | LICENSE file consistent with the MIT badge; `.gitignore` | files | NOT MET |
| AC-D5 | Every P0 item in `docs/03_MISSING_COMPONENTS.md` has an owner and a recovery task | `docs/04_RECOVERY_TASKS.md` | **MET** (tasks defined; none closed) |

## G. Engineering drawings package (added 2026-10-09)

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-E1 | Every drawing in `engineering/DRAWING_REGISTER.md` has its native file and exports present and well-formed | `python3 tools/gen_drawing_register.py --check` exit 0 | **MET** (73 drawings, 0 problems) |
| AC-E2 | EAGLE XML ↔ KiCad conversion counts agree for all boards | `engineering/VALIDATION/PCB_CROSS_CHECK.md` | **MET** (32/32 rows OK) |
| AC-E3 | No missing symbols/footprints; schematic ↔ board part lists identical | `tools/gen_schematic_reports.py` exit 0 | **MET** |
| AC-E4 | Any drawing VERIFIED against EAGLE output or hardware | `VALIDATION/DRAWING_CHECKS.md` §2 | NOT MET (0 VERIFIED) |
| AC-E5 | Enclosure/antenna/pedestal/cooling drawings exist | register MECH-ENC/ANT/PED/COOL | NOT MET (BLOCKED — MISSING DATA) |
| AC-E6 | Proposed designs (DSN-*) registered with native editable files and exports present | `tools/gen_drawing_register.py --check` | **MET** (11 PROPOSED entries, 0 file problems) |
| AC-E7 | Antenna proposal simulated (|S11| < −10 dB at f0 ± B/2) and coupon measured | openEMS log + VNA data | NOT RUN |
| AC-E8 | Owner approval of decisions D-01…D-15 recorded | signed decision log | NOT MET |

## H. BETA tree (added 2026-10-09) — criteria evaluated on `beta/`, not on the originals

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AC-X1 | beta RTL parses/elaborates/lints with 0 errors and all testbenches pass | `beta/fpga/logs/` | **MET** (BETA) |
| AC-X2 | beta firmware compiles and links; host tests pass | `beta/stm32/build_out/`, `logs/` | **MET** (BETA) |
| AC-X3 | beta GUI test suite passes; packaged app starts | `beta/gui` pytest 55 passed | **MET** (BETA) |
| AC-X4 | beta boards: 0 unconnected on Main/RF PA/Synth; Power ≤ 100 open with documented reasons | `beta/pcb/*/exports/reports/DRC_report.json` | **MET** (BETA; Power 89 listed) |
| AC-X5 | host-link bridge testbench, firmware build and GUI parser agree on one frame vector | `tb_frame.hex` shared | **MET** (BETA) |
| AC-X6 | antenna row S11 < −10 dB at f0 in simulation | `TUNING_LOG.md` | **MET** (−18 dB; band 128 MHz) |
