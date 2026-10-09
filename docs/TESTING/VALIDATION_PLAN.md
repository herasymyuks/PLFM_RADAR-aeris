# Validation Plan — AERIS-10

Status date 2026-10-08. Each test has an ID, a command or procedure, the tool that was available on the authoring machine (macOS arm64, Python 3.14.7, iverilog 13.0, verilator 5.052; **no** Vivado, ARM GCC, EAGLE, KiCad), and the result actually obtained. A test is reported PASSED only if it was executed and succeeded. "Software-based design check" means a file/tool check; "physical verification" needs hardware and is never claimed here.

Run everything that is runnable with `bash tools/run_all_checks.sh` (exit code = number of failed checks).

## 1. FPGA

| ID | Test | Type | Command | Tool available | Executed result |
|---|---|---|---|---|---|
| F-01 | Syntax / parse of all RTL | design check | `tools/fpga_lint.sh` (iverilog -g2012) | yes | **FAIL** — `radar_system_top.v:312` syntax error |
| F-02 | Elaboration of `radar_system_top` | design check | same | yes | **FAIL** — not reached (F-01); on a patched scratch copy: 6 missing modules |
| F-03 | Lint | design check | `verilator --lint-only -Wall` (in `tools/fpga_lint.sh`) | yes | **FAIL** — same syntax error; with stubs: 207 warnings incl. MULTIDRIVEN ×4, UNDRIVEN ×14 |
| F-04 | Constraint completeness | design check | `python3 tools/check_fpga_constraints.py` | yes | **FAIL** (exit 1) — 142 placeholder lines, 180/180 bits without PACKAGE_PIN, 21 without IOSTANDARD, 2 invalid properties |
| F-05 | Schematic-derived pin map generation | design check | `python3 tools/gen_xdc_from_schematic.py` | yes | PASSED (exit 0) — 64 ports mapped, 25 ports unresolved (this is a generation step, not a correctness proof) |
| F-06 | Simulation `radar_system_tb` | design check | Vivado xsim (SVA needed) | no | NOT RUN |
| F-07 | Synthesis utilisation on `xc7a50tftg256-2` | design check | `tools/vivado/create_project.tcl` + `launch_runs synth_1` | no | NOT RUN |
| F-08 | Timing summary / clock interaction / CDC report | design check | `report_timing_summary`, `report_cdc` | no | NOT RUN |
| F-09 | Bitstream generation | design check | `write_bitstream` | no | NOT RUN |
| F-10 | ADC LVDS capture on hardware (eye/valid data) | physical | ILA + known tone into AD9484 | no | NOT RUN |

## 2. STM32

| ID | Test | Type | Command | Tool | Result |
|---|---|---|---|---|---|
| S-01 | Dependency / include check | design check | `python3 tools/check_stm32_includes.py` | yes | **FAIL** (exit 1) — 53 absent HAL/CMSIS/USB headers, 6 case mismatches |
| S-02 | Cube package completeness | design check | `tools/stm32_check_cube_package.sh <CubeF7>` | script yes, package no | NOT RUN (self-test with invalid path → exit 2 as designed) |
| S-03 | Host syntax probe (non-target) | design check | `clang -fsyntax-only -DSTM32F746xx -DUSE_HAL_DRIVER …` | yes | 29/60 TUs fail on missing `stm32f7xx_hal.h`; pure no-OS/C++ units pass (informational, **not a build**) |
| S-04 | Cross-compile | design check | `arm-none-eabi-g++` via CubeIDE or `reconstructed/CMakeLists.txt` | no | NOT RUN |
| S-05 | Link + size | design check | `arm-none-eabi-size` | no | NOT RUN |
| S-06 | Static analysis | design check | `cppcheck --enable=warning,style` | no (not installed) | NOT RUN |
| S-07 | Pin-map cross-check firmware ↔ schematic | design check | `tools/extract_eagle_netlist.py --part U2` vs `main.h` | yes | PASSED for the 60 named GPIO macros (all nets found on U2); **conflict found** for HSE (8 vs 25 MHz) and ADF4382 pins in `adf4382a_manager.h` |
| S-08 | Flash + CDC enumeration | physical | ST-LINK, `lsusb`/Device Manager | no | NOT RUN |
| S-09 | Settings packet accepted (state READY_FOR_DATA) | physical | send flag + 82-byte packet | no | NOT RUN (static analysis predicts failure: C4, C5) |
| S-10 | Power-sequence timing on `EN_*` rails | physical | oscilloscope | no | NOT RUN |

## 3. Python

| ID | Test | Type | Command | Tool | Result |
|---|---|---|---|---|---|
| P-01 | Dependency resolution | design check | `pip install -r 9_Firmware/9_3_GUI/requirements.txt` in a venv | yes | PASSED (all 10 packages installed; versions in `docs/GUI/DEPENDENCIES.md`) |
| P-02 | Syntax (ast) of 27 scripts | design check | `python3 tools/check_python_imports.py` | yes | **FAIL** (exit 1) — `GUI_V1.py` IndentationError; 26/27 OK |
| P-03 | Import test of third-party modules | design check | `… --try-import` (venv) | yes | PASSED for all GUI modules; FAIL for `openEMS`/`CSXCAD` (not on PyPI; simulation scripts only) |
| P-04 | Module import of each GUI file | design check | `python -c "import GUI_V6_Demo"` etc. | yes | PASSED for V2, V3, V4, V4_2_CSV, V5, V5_Demo, V6, V6_Demo (import only); V1 FAIL |
| P-05 | pyflakes | design check | `pyflakes 9_Firmware/9_3_GUI/*.py` | yes | undefined names: `GUI_V6.py:392` `STM32USBInterface`; `GUI_V4_2_CSV.py:430` `e`; V5_Demo missing methods (informational) |
| P-06 | Unit tests | design check | `pytest` | yes | NOT RUN — **no tests exist in the repository** |
| P-07 | GUI startup smoke (`GUI_V6_Demo.py` window) | design check | procedure GUI-T05 | yes (Tk 9.0) | NOT RUN (window not launched) |
| P-08 | Demo-data verification (`test_radar_data.csv` vs `GUI_V4_2_CSV.py` reader) | design check | column/row check | yes | PASSED (header matches reader; 16 384 rows = 32 chirps × 512; identical to generator output) |
| P-09 | Hardware link (CDC / FTDI) | physical | — | no | NOT RUN |

## 4. PCB documentation

| ID | Test | Type | Command | Tool | Result |
|---|---|---|---|---|---|
| B-01 | ERC (fresh run) | design check | EAGLE `ERC` | no | NOT RUN — stored approved ERC items: Main 4, others 0 |
| B-02 | DRC (fresh run) | design check | EAGLE `RATSNEST; DRC` | no | NOT RUN — stored: Main 211 approved + 2 390 airwires; Power 309 airwires; Synth 0; PA 0 |
| B-03 | Missing-library detection | design check | XML: all `<library>` embedded | yes | PASSED — no external library references for any board |
| B-04 | sch/brd consistency | design check | part/net set comparison (XML) | yes | PASSED Synth, PA; Main: 10 board-only signals, 210 value mismatches; Power: version mismatch 9.6.2/7.4.0, 1 board-only signal → **FAIL** for Main and Power |
| B-05 | BOM completeness | design check | `python3 tools/gen_eagle_bom.py …` → `docs/BOM/` | yes | **FAIL** — 0 MPN attributes on all boards; value-less references 244/80/6/47 |
| B-06 | Manufacturing-export completeness | design check | `python3 tools/check_manufacturing_files.py` | yes | **FAIL** (exit 1) — no Gerber/drill for any board; P&P + BOM only for Synth |
| B-07 | Outline/hole extraction | design check | `python3 tools/gen_board_outline_svg.py …` | yes | PASSED for 4 boards (drawings generated) |
| B-08 | Stack-up confirmation | physical/vendor | fab quote with stack-up drawing | no | NOT RUN |
| B-09 | Impedance coupon measurement | physical | TDR at fab | no | NOT RUN |

## 5. Repository / documentation

| ID | Test | Command | Result |
|---|---|---|---|
| R-01 | Inventory generation | `python3 tools/gen_inventory_doc.py` | PASSED (482 rows) |
| R-02 | Documentation link validation | `python3 tools/check_doc_links.py` | **FAIL** — 34 broken references before this reconstruction (README `10_docs/*`, `03_software/01_fpga_pipeline.md` → `02_lfm_waveform.md`, `00_notation/conventions.md:69`, `research/03_hw_improvements.md` siblings, plus the `claude.md` task paths that this work creates) — re-run after completion for the residual list |
| R-03 | Expected-artifact manifest | `python3 tools/check_missing_files.py` | **FAIL** — 26 P0 items missing (see `docs/03_MISSING_COMPONENTS.md`) |

## 6. Evidence collection rules

- Every executed command's output is saved under `build/` (lint logs in `build/lint/`, Vivado in `build/vivado/`, STM32 in `build/stm32/`) and referenced by test ID in `docs/TESTING/ACCEPTANCE_CRITERIA.md` when reporting.
- Physical tests record instrument, serial number, date and raw capture file.
- A test result changes from NOT RUN to PASSED/FAILED only with an attached log.
