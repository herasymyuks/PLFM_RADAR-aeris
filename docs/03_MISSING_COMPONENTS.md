# 03 — Missing Components Register

Status date 2026-10-08. Priorities: **P0** blocks a reproducible build or a required artefact; **P1** blocks a complete release or reliable validation; **P2** documentation/maintainability. "Impact" names the build output that cannot be produced. Recovery procedures are detailed in `docs/04_RECOVERY_TASKS.md` (task IDs in the last column). Automated presence check: `python3 tools/check_missing_files.py` (IDs starting with FPGA-/STM-/GUI-/PCB-/MECH-/REPO- are the manifest IDs of that script).

## FPGA

| ID | Component | Evidence | Impact | Recovery procedure | Verification | Priority | Task |
|---|---|---|---|---|---|---|---|
| FPGA-00 | Parseable RTL | `radar_system_top.v:312` `wire` inside `always`; `:155-156` procedural assignment to `wire`; `ddc_400m.v:252-266` use-before-declare; `radar_receiver_final.v:150/192`, `:216-217` phantom ports (iverilog/verilator logs `build/lint/`) | no elaboration, no synthesis | edit the six locations (FPGA-T03) | `tools/fpga_lint.sh` no "syntax error" | P0 | R-FPGA-03 |
| FPGA-01 | Pin-complete XDC | `cntrt.xdc`: 142 placeholder lines, 180/180 bits unassigned, `PACKAGE_PIN_BANK` invalid (:320-321), LVCMOS33 on 1.8 V bank signals (:85,:92) | no implementation/bitstream | use `reconstructed/radar_system_top_schematic_derived.xdc` after designer verification; resolve 25 ports with no board counterpart | `tools/check_fpga_constraints.py` exit 0 | P0 | R-FPGA-02 |
| FPGA-02 | Vivado project / build script | no `.xpr`, `.tcl` existed | no reproducible build | `tools/vivado/create_project.tcl` (generated; part must be passed) | `.xpr` created, elaboration log archived | P0 | R-FPGA-04 |
| FPGA-03 | RTL modules `ad9484_lvds_to_cmos_400m`, `range_bin_decimator`, `matched_filter_processing_chain` | instantiated at `radar_receiver_final.v:82,226`, `matched_filter_multi_segment.v:361`; no definition repo-wide | elaboration fails | obtain original ISE project or re-implement to the inferred interfaces (FPGA-T04) | iverilog "missing modules" list empty | P0 | R-FPGA-05 |
| FPGA-04 | Xilinx FFT IP `xfft_32`, `FFT_enhanced` (.xci) | `doppler_processor.v:283`, `fft_1024_forward.v:102`, `fft_1024_inverse.v:78` | elaboration fails | regenerate in Vivado IP catalog to the port widths used | `.xci` committed; elaboration OK | P0 | R-FPGA-05 |
| FPGA-05 | `long_chirp_seg3_i/q.mem` | `chirp_memory_loader_param.v:58-59`; files absent; other 8 present | ROM segment 3 uninitialised | obtain from generator or set `LONG_SEGMENTS=3` (designer) | `$readmemh` without warnings | P0 | R-FPGA-06 |
| FPGA-06 | Portable `$readmemh` paths | `chirp_memory_loader_param.v:3-12` absolute `C:/Users/dell/...` | sim/synth cannot find files on any other machine | override parameters at `radar_receiver_final.v:144` with relative names | Vivado log no "cannot open" | P0 | R-FPGA-06 |
| FPGA-07 | Device decision XC7A50T vs XC7A100T | schematic/xlsx/drawio 50T vs README/XDC/docs 100T | wrong part → wrong resources, wrong constraints | designer decision (FPGA-T01) | recorded decision | P0 | R-FPGA-01 |
| FPGA-08 | 400 MHz LVDS capture structure | `lvds_to_cmos_400m.v:35-43` flop-derived clock; no ISERDES/IDDR in active path | design non-functional | redesign ADC front-end with IDDR/ISERDES + BUFIO/BUFR or MMCM | timing report; hardware capture test | P0 (functional) | R-FPGA-07 |
| FPGA-09 | Multi-driven registers | `plfm_chirp_controller.v:564-576/683-784`; `usb_data_interface.v:65-79/176-182`; `cic_decimator_4x_enhanced.v:71/181/291` | synthesis error | single-driver refactor | verilator MULTIDRIVEN = 0 | P0 | R-FPGA-07 |
| FPGA-10 | Level-shifter instantiation (STM32 SPI → ADAR1000) | `radar_transmitter.v:59-71` undriven; `level_shifter_interface.v` orphan | ADAR1000 unreachable | instantiate or route SPI differently | verilator UNDRIVEN = 0 for those nets | P0 (functional) | R-FPGA-07 |
| FPGA-11 | Host data path | FT601 unconnected on Main Board; RTL assumes it | no radar data to host | architecture decision (K3) | decision record | P0 | R-SYS-01 |
| FPGA-12 | Clock-group constraints, CDC fixes | no `set_clock_groups`; `cdc_adc_to_processing` Gray-codes data | timing/CDC unsafe | add constraints; use `cdc_handshake` | `report_cdc` clean | P1 | R-FPGA-08 |
| FPGA-13 | Runnable testbench with pass/fail | SVA only, no gating (`radar_system_tb.v:528-543`) | no regression | add `$fatal`, scoreboard; run xsim | sim log PASS | P1 | R-FPGA-09 |
| FPGA-14 | Authoritative TX LUT | `plfm_chirp_controller.v:99-560` vs `chirp_lut_init.v` differ; no generator script | waveform ambiguity | obtain generator; delete dead copy | one LUT source, generator committed | P1 | R-FPGA-06 |
| FPGA-15 | Bitstream | none | — | after all above | `.bit` + reports | P1 | R-FPGA-10 |

## STM32

| ID | Component | Evidence | Impact | Recovery procedure | Verification | Priority | Task |
|---|---|---|---|---|---|---|---|
| STM-01 | `.ioc` | absent repo-wide | no regeneration of USB/startup/linker | regenerate from `docs/STM32` §3 (STM-T02) | generated MSP = repo MSP | P0 | R-STM-02 |
| STM-02 | Linker script | absent | no link | CubeMX output | link OK | P0 | R-STM-02 |
| STM-03 | Startup `.s` | absent (`system_stm32f7xx.c:124` references it) | no boot | CubeF7 template | link OK | P0 | R-STM-02 |
| STM-04 | Build system | absent | no reproducible build | CubeIDE project or `reconstructed/CMakeLists.txt` (UNVERIFIED) | `.elf` built | P0 | R-STM-03 |
| STM-05..08 | USB Device app files | `main.cpp:21,23`; `gps_handler.h:6-7` include them; absent | no USB, no `MX_USB_DEVICE_Init` | CubeMX USB_DEVICE CDC generation + USER CODE RX forwarding (C4) | enumeration test | P0 | R-STM-02, R-STM-04 |
| STM-09 | HAL driver sources | 50 headers absent (`tools/check_stm32_includes.py`) | no compile | STM32CubeF7 | S-02 exit 0 | P0 | R-STM-01 |
| STM-10 | CMSIS device header | `system_stm32f7xx.c:47` | no compile | STM32CubeF7 | S-02 | P0 | R-STM-01 |
| STM-11 | HSE crystal consistency | 8 MHz (sch XTAL1) vs 25 MHz (`hal_conf.h:97`, `main.cpp:1823`) | PLL out of range → no clock/USB | designer decision (C1) | measured SYSCLK 72 MHz, USB 48 MHz | P0 | R-STM-05 |
| STM-12 | ADF4382 pin macros | `adf4382a_manager.h:9-28` collide with PA enables | PA rails toggled, LO never configured | use `main.h` macros (C2) | code review; LO lock LEDs | P0 | R-STM-06 |
| STM-13 | ADF4382 SPI platform ops | `adf4382a_manager.c:42,51` NULL → `Error_Handler` | firmware halts at init | set `stm32_spi_ops` + CS (C3, C7) | init returns 0 | P0 | R-STM-06 |
| STM-14 | USB RX forwarding | `main.cpp:328-339` never bound (C4); padding (C5) | GUI cannot start radar | USER CODE in `usbd_cdc_if.c`; fix padding | READY_FOR_DATA reached | P0 | R-STM-04 |
| STM-15 | Case-mismatched headers | `ADS7830.H`, `DAC5578.H`, `platform_noos_stm32.H` | build fails on Linux/CI | rename | includes check 0 mismatches | P1 | R-STM-03 |
| STM-16 | `hal_set_gpio_by_index` | `platform_noos_stm32.c:50-58` undefined | link error if compiled | exclude file | link OK | P1 | R-STM-03 |
| STM-17 | `GPS_Init` call | never called (`gps_handler.cpp:6,67`) | no GPS to GUI | add call (C6) | GPSB packets observed | P1 | R-STM-07 |
| STM-18 | USB VID/PID | unknown | GUI device filter | choose/record in `usbd_desc.c` | enumeration | P1 | R-STM-02 |
| STM-19 | `STM32_ALGO.docx` content | 0-byte file | algorithm documentation lost | obtain from author | file > 0 bytes | P2 | R-DOC-03 |

## Python GUI

| ID | Component | Evidence | Impact | Recovery | Verification | Priority | Task |
|---|---|---|---|---|---|---|---|
| GUI-01 | `requirements.txt` | absent → **generated** | env not reproducible | done (`9_Firmware/9_3_GUI/requirements.txt`) | P-01 PASSED | P1 | done |
| GUI-02 | `pyproject.toml` | absent → **generated** | no packaging | done | `python -m build` (NOT RUN) | P2 | R-GUI-03 |
| GUI-03 | Complete `GUI_V6.py` | stub classes `:90-92,365-375,419-425`; undefined `STM32USBInterface` `:392` | documented "current" GUI unusable | complete or demote to V5 | module runs | P1 | R-GUI-01 |
| GUI-04 | Protocol alignment with firmware/RTL | `docs/GUI/DEPENDENCIES.md` §6 | no end-to-end data | architecture decision K3/K5 | AC-P6 | P1 | R-SYS-01 |
| GUI-05 | Unit tests | none | no regression | write tests for parsers/CFAR | pytest | P1 | R-GUI-02 |
| GUI-06 | FT601 host library | pyftdi lacks FT601 support | V6 cannot open device | FTDI D3XX binding or drop FT601 | import + open | P1 | R-SYS-01 |
| GUI-07 | `GUI_V1.py` fragment, `GUI_V5_Demo.py` truncated | syntax error; `AttributeError` at `:955` | confusion, failed syntax check | archive | P-02 exit 0 | P2 | R-GUI-01 |
| GUI-08 | Google Maps API key | placeholder in V4–V6 | map blank | user key via config | map renders | P2 | R-GUI-03 |

## PCB

| ID | Component | Evidence | Impact | Recovery | Verification | Priority | Task |
|---|---|---|---|---|---|---|---|
| PCB-MB-01..04 | Main Board Gerber, drill, BOM(MPN), P&P | none exist | cannot fabricate | P-EAGLE-04/06/07 after layout completion | `check_manufacturing_files.py` | P0 | R-PCB-01, R-PCB-05 |
| PCB-MB-05 | Main Board layout completion | 2 390 airwires, 11 off-board parts, 211 approved DRC, `+3V3_FT` unrouted | fabrication would be wrong | designer completes routing; FT601 decision | RATSNEST nothing to do; DRC 0 | P0 | R-PCB-01 |
| PCB-PS-01..03 | Power Board Gerber, drill, BOM | none | cannot fabricate | as above | tool | P0 | R-PCB-02, R-PCB-05 |
| PCB-PS-04 | Power Board layout completion + sch/brd version mismatch | 309 airwires, 132 off-board, brd 7.4.0 vs sch 9.6.2 | — | re-link in 9.6.2, place, route | consistency + RATSNEST | P0 | R-PCB-02 |
| PCB-PA-01..03 | RF PA Gerber, drill, BOM | none (layout complete) | cannot fabricate | P-EAGLE-04/06 | tool | P0 | R-PCB-03, R-PCB-05 |
| PCB-FS-01..02 | Synth Gerber, drill | none (P&P + BOM exist) | cannot fabricate | P-EAGLE-04 | tool | P0 | R-PCB-04 |
| PCB-FS-03 | Synth BOM MPNs | xlsx MPN columns empty | cannot purchase | fill attributes | `mpn_status` VERIFIED | P0 | R-PCB-05 |
| PCB-ALL-01 | Stack-up per board | PNG (6L, unlabeled) ≠ DRU ≠ impedance note | impedance/thickness unknown | vendor stack-up | fab drawing | P0 | R-PCB-06 |
| PCB-ALL-02 | Fab + assembly drawings, schematic PDFs, ERC/DRC reports | none | incomplete package | P-EAGLE-02/03/07/08 | files present | P1 | R-PCB-05 |
| PCB-ALL-03 | Datasheets for parts actually used (TPS562208, LM2662, AD9523-1, FT601, STM32F746, XC7A50T, oscillators, GY-85, BMP180, NEO-6M, TB6600) | absent; unrelated ones present (TPS562201, LM2663, MAX20029, STUW81300, QPM1021, QPA1013, TGA2623) | review impossible | collect | files present | P2 | R-DOC-02 |

## Mechanical

| ID | Component | Evidence | Impact | Recovery | Verification | Priority | Task |
|---|---|---|---|---|---|---|---|
| MECH-01 | `10_docs/assembly_guide.md` | `README.md:141`; absent | no assembly instructions | write per `ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md` §2 after CAD exists | link check | P1 | R-MECH-02 |
| MECH-02 | `10_docs/Hardware/Enclosure` | `README.md:143`; absent | no enclosure | obtain CAD from designer | STEP/STL present | P1 | R-MECH-01 |
| MECH-03 | Antenna array CAD/drawing | two contradictory simulations, no CAD | cannot build antenna | designer decision + CAD | drawing present | P1 | R-MECH-01 |
| MECH-04 | Pedestal, slip ring, stepper, fans part numbers | none | cannot source | designer | BOM lines | P1 | R-MECH-01 |
| MECH-05 | PCB thickness / mass | stack-up unresolved | no mass budget | after PCB-ALL-01 | table | P2 | R-PCB-06 |
| MECH-06 | Outline/hole drawings | absent → **generated** (`docs/MECHANICAL/drawings/`) | — | done | AC-M1 MET | — | done |

## Repository / documentation

| ID | Component | Evidence | Impact | Recovery | Verification | Priority | Task |
|---|---|---|---|---|---|---|---|
| REPO-01 | `LICENSE` | README MIT badge, no file | licensing unclear | add MIT LICENSE (owner decision) | file | P2 | R-DOC-01 |
| REPO-02 | `.gitignore` | none; 16 `.pyc`, `.bak`, zip committed | noise | add | file | P2 | R-DOC-01 |
| REPO-03 | Git repository scope | project folder has no own `.git`; `git rev-parse --show-toplevel` = `/Users/void` | history/attribution unreliable | `git init` in `PLFM_RADAR` (owner decision) | `.git` present | P2 | R-DOC-01 |
| REPO-04 | README accuracy | Gerber claim, XC7A100T, `10_docs` links | misleads users | correct (owner) | link check | P2 | R-DOC-01 |
| REPO-05 | Broken doc links | 34 (`tools/check_doc_links.py`) | navigation | fix targets | tool exit 0 | P2 | R-DOC-01 |
| DOC-01..06 | Documentation tree of `claude.md` §13 | absent → **generated** | — | done | manifest DOC-* present | P2 | done |


---

## Update 2026-10-09 — engineering drawings package

The PCB production entries above (Gerber/drill/BOM/P&P for the four boards) now have a **generated** counterpart under `engineering/PCB/<BOARD>/` (KiCad 10 conversion of the EAGLE boards, DRC with EAGLE-DRU-derived rules, cross-checked against the EAGLE XML). They remain listed as missing because the designer-released EAGLE export does not exist, manufacturer part numbers are absent and the Main/Power layouts are unfinished. New missing items identified by the drawing work are registered in `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` (G-01…G-12) and `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md` (MDR-01…MDR-11). New design findings (firmware never asserts `EN_+3V3_ADTR`, `EN_+5V0_PA1/2/3`, `EN_+5V5_PA`; Power Board U30 input from VIN; `+1V8_CLOCK` single output needed twice; SV1 carries 15 enables) are in `engineering/ELECTRICAL/power_distribution/power_rails.md` §4.
