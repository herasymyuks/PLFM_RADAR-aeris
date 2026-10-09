# Bring-up and test — power-up, flashing, FPGA programming, calibration, bench tests, acceptance

**Author of this chapter:** Antidrone Ukraine · antidrone.cc.

**Status summary:** every procedure in this chapter is **PROPOSED / BETA — never executed on hardware** (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, header; `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md`, "Nothing in this sequence has been executed on hardware"). The test plan and acceptance tables are copied from `docs/TESTING/`; a test is reported PASSED only where the source records an executed run, and physical tests are NOT RUN everywhere. The FPGA bitstream does not exist (no Vivado on the authoring machine), so Steps 16.3 and 16.5–16.9 cannot be started today.

**Sources:** `manual/ASSEMBLY_STEPS_SOURCE.md` (phase E), `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §B/§D, `docs/TESTING/VALIDATION_PLAN.md`, `docs/TESTING/ACCEPTANCE_CRITERIA.md` (sections A–H), `beta/fpga/README.md` (calibration registers, Vivado scripts), `beta/gui/README.md` and `beta/gui/aeris10_gui/protocol/register_map.py` (register panel), `beta/stm32/README.md` §7, `engineering/ELECTRICAL/power_distribution/power_rails.md` §3, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §1–§2.

**Figures in this chapter:** none mandatory (tables); the register map is in chapter 13 §13.6, the enable sequence in chapter 12 §12.6.

## 16.0 Safety and preconditions

The safety preamble of chapter 15 §15.0 applies (S1 22 V drain, S2 RF, S3 pedestal, S4 ESD). Preconditions: phases A–D of chapter 15 complete with the lid off and the pedestal stationary; bench PSU 12–17 V with current limit; the 22 V leads disconnected until Step 16.6; a 50 Ω dummy load or anechoic setup for Step 16.9; instruments listed per step. Three decisions gate the chapter: ⚠ **K1** (FPGA part XC7A50T on the schematic vs XC7A100T in the FPGA README — `tools/vivado/create_project.tcl` header), ⚠ **K2** (HSE 8 MHz assumed by the beta firmware, D-01), ⚠ **K4** (22 V PA supply not in CAD).

## 16.1 Phase E — bench bring-up steps

### Step 16.1 — Flash the STM32 beta image via SWD [BETA image, ⚠ K2]

- **Purpose:** load `aeris10_fw.elf` and prove the clock tree and CDC enumeration.
- **Parts & tools:** ST-LINK on SWD (PA13 SWDIO / PA14 SWCLK; SWO PB3 — `beta/stm32/CUBEMX_SETTINGS.md` §3); `beta/stm32/build_out/aeris10_fw.elf` (build of Step 12.3); USART3 terminal 115200 8N1 (PB10/PB11); host PC.
- **Action:** `STM32_Programmer_CLI -c port=SWD -w beta/stm32/build_out/aeris10_fw.elf -v -rst` (source: `beta/stm32/README.md` §7 item 2).
- **Check:** USART3 banner appears (SWO/USART3 output at 115200 "proves the clock" — same source); the host enumerates a CDC ACM device with the placeholder VID/PID 0x0483:0x5740 (D-09). Note the 180 s OCXO wait at boot (`HAL_Delay(180000)`, F0 in `power_rails.md` §3) before any rail is enabled.
- **Figure:** F12.2.
- **⚠ Decision:** K2 — if the board's crystal is not 8 MHz the PLL constants of D-01 are wrong and `HAL_RCC_OscConfig` fails into `Error_Handler()`; verify XTAL1 on the assembled board first.

### Step 16.2 — Observe the power-enable sequence F0–F10 on a scope [SOURCE-DERIVED order, BETA delays]

- **Purpose:** confirm that the rails appear in the coded order with the coded delays (chapter 12 §12.6) and that the D-11 additions (`+5V5_PA` before VG, VD last off) are present.
- **Parts & tools:** oscilloscope ≥ 4 channels; probe points at the Power Board outputs X2…X35 and at SV1 pins 1…19.
- **Action:** capture from reset: F1 `EN_+1V8_CLOCK` (SV1-8) → F2 `EN_+3V3_CLOCK` (SV1-10) → F3/F4/F5 FPGA rails (SV1-1/3/5) → F6 ADAR 3.3 V (SV1-9/11) → F7 `EN_+5V0_ADAR` (SV1-7) → F8 `EN_+3V3_VDD_SW` (SV1-17) → F9 `EN_+3V3_SW` (SV1-15) → `EN_+5V5_PA` (SV1-6, D-11 addition) → F10 VG DAC update then `EN/DIS_RFPA_VDD` (PD6 → JP10).
- **Check:** order matches `power_rails.md` §3; delays 100 ms (F1–F5), 500 ms (F6, F7), 2 ms (F8, F9), 100 ms `+5V5_PA` → DAC, 20 ms VG → VD (D-11); the xlsx rules "1.8 V before 3.3 V for the AD9523" and "AVDD3 before AVDD1 for the ADAR1000" are respected (F1→F2, F6→F7). Record the captures (AC-S7).
- **Figure:** F3.2, chapter 12 §12.6 tables.
- **⚠ Decision:** whether `systemPowerUpSequence()` reaches F8/F9 via `initializeADTR1107Sequence()` is UNVERIFIED (`power_rails.md` §3 row F8); the actual assertion of `EN_+3V3_ADTR` / `EN_+5V0_PA1..3` settles observation MAN-12-1.

### Step 16.3 — Program the FPGA via JP3 JTAG [BLOCKED — no bitstream; ⚠ K1]

- **Purpose:** load the radar RTL and prove the STM32 ↔ FPGA handshake.
- **Parts & tools:** Xilinx platform cable on Main Board JP3 (JTAG); Vivado with `beta/fpga/vivado/create_project.tcl` + `vivado/build.tcl` (NOT executed — `beta/fpga/README.md`); the two FFT IP cores per `beta/fpga/ip/README.md` (not generated).
- **Action:** when a bitstream exists: `vivado -mode batch -source tools/vivado/create_project.tcl -tclargs xc7a50tftg256-2` (part must be passed explicitly — `tools/vivado/create_project.tcl` header), then `build.tcl`, then program via Hardware Manager.
- **Check:** DONE pin high; STM32 ↔ FPGA handshake DIG_0..4 (PD8..PD12: new chirp, new elevation, new azimuth, mixers enable, FPGA reset — `CUBEMX_SETTINGS.md` §6) toggles.
- **Figure:** F11.1 (chapter 11).
- **⚠ Decision:** ⚠ K1 part number; the beta constraints leave 116 port bits unconstrained ("`write_bitstream` will refuse the unconstrained I/O unless they are removed from the top or `UNCONSTRAINEDPINS ALLOW` is set" — `beta/fpga/README.md`, "Constraints"); bank-14 LVDS termination (DIFF_TERM FALSE, external 100 Ω — option A, REQUIRES VERIFICATION).

### Step 16.4 — AD9523 lock and output frequencies [SOURCE-DERIVED intent]

- **Purpose:** verify the clock distribution before any sampling or DAC test.
- **Parts & tools:** frequency counter (± 1 ppm or better); coax set CBL-036…041 in place (Step 15.16).
- **Action:** read the AD9523 status pins (PF8/PF9 `AD9523_STATUS0/1`) and measure Synth J7 (100 MHz FPGA), J5/J6 (120 MHz DAC), J3 (400 MHz ADC) at the Main Board ends.
- **Check:** 100 / 120 / 400 MHz ± 1 ppm (acceptance from `ASSEMBLY_SEQUENCE.md` §B.4; "firmware intent `main.cpp:933-1072`"; register table verified on the host against the driver's encoding, "**not on silicon**" — `beta/stm32/DECISIONS.md` D-12).
- **Figure:** F2.1 (chapter 2).
- **⚠ Decision:** the beta ADC capture (mode 1) requires BUFR (DCO/4) and `clk_100m` (AD9523 OUT6) to be frequency-locked — "if the two clocks are not frequency-locked the design needs a re-sampler (not present)" (`beta/fpga/README.md`, "Remaining risks").

### Step 16.5 — ADC capture calibration (IDELAY taps) [BETA register procedure; ⚠ ADC SPI unwired]

- **Purpose:** centre each of the 8 LVDS lanes of the AD9484 in its valid window and align the lane rotation (the `adc_capture_calib` module of the beta RTL, `ADC_CAPTURE_MODE = 1`).
- **Parts & tools:** GUI register panel (chapter 13 §13.6) over CDC `REG` commands (firmware D-17) **or** any host that can issue the SPI bridge commands 0x02/0x03; the AD9484 test-pattern registers (datasheet: register 0x0D = 0x48 user pattern, P1/P2 = 0x19..0x1C = pattern A/B; or 0x04 checkerboard / 0x07 toggle — `beta/fpga/README.md`, "ADC capture and DDC front end"); logic analyser optional.
- **Action — auto (pattern) method:** (1) put the ADC in the 2-code test pattern matching `CAL_PATT` (reset 0x55AA: pattern_a 0xAA, pattern_b 0x55); (2) `REG W 0x4 0x1` (CAL_CTRL `auto_start`, write-1-to-toggle); (3) poll `REG R 0x9` (CAL_STAT) until `busy` = 0 and `done` = 1; (4) for lane = 0…7: `REG W 0x5 <lane>`, `REG R 0xA` (CAL_LANE_INFO: chosen `tap`, `win_lo`, `win_hi`) — the panel's "Read all / refresh" does this loop and restores CAL_LANE; (5) `REG R 0xC` (CAL_UNDET); (6) with the pattern still applied set `check_en` (`REG W 0x4 0x8`) and read `REG R 0xB` (CAL_ERR) after a few seconds; (7) switch the ADC to normal data, clear `check_en`.
- **Action — manual method (fallback):** `REG W 0x5 <lane>`, `REG W 0x6 <tap>` (CAL_TAP 0..31, 78 ps each, reset 16), `REG W 0x4 0x2` (`manual_load`); for a lane rotation `REG W 0x7 <n>` (CAL_SLIP 0..3) then `REG W 0x4 0x4` (`bitslip_load`).
- **Check:** CAL_STAT `lock[7:0]` = 0xFF, `align_fail` = 0, `fifo_ovf` (bit 15) = 0; per-lane pass windows "should be ~27 of 32 taps wide at 400 MSPS"; CAL_ERR stays 0 with the pattern applied and `check_en` set; `CAL_ERR` stays 0 in normal data with the pattern check off (source: `beta/fpga/README.md`, "Remaining risks / what to check in Vivado (mode 1)"). Simulation reference: testbench `tb_adc_iserdes_capture` — "8/8 lanes locked, centre tap 12 (skewed lane 5 … compensated), bitslip detected/realigned, 4000 samples exact" (same README, table row 6g).
- **Figure:** chapter 13 §13.6 register table; F2.2.
- **⚠ Decision:** (a) the ADC test pattern needs the AD9484 SPI, which the step source marks "⚠ SPI unwired" (`manual/ASSEMBLY_STEPS_SOURCE.md` E5) — if no SPI path to the ADC exists only the manual method and the blind method remain; (b) the **blind method** (`adc_capture_calib.v` `ctrl_blind`, registers 0x0D/0x0E/0x10 CAL_BLIND_*) is in the RTL but "no register in `radar_control_regs.v` drives it" from the GUI's 4-bit map — the panel shows it as unavailable (`beta/gui/CHANGELOG.md` "Discrepancies" 2); (c) on the current top level `reg_we/reg_addr/reg_wdata` of `ctl_regs` are tied to constants (`radar_system_top.v:321-323`) and the bridge RTL does not implement 0x02..0x04 — **register writes cannot reach the FPGA until that RTL work is done**; (d) ISERDES Q1..Q4 bit order "UNVERIFIED against UG471 … run the ADC PN9 pattern (0x0D = 0x06) and compare against a PN9 generator before trusting the data" (`beta/fpga/README.md`).

### Step 16.6 — PA bias-up, one board at a time [SOURCE-DERIVED sequence, PROPOSED thermal limit; ⚠ K4, D-14]

- **Purpose:** bring each QPA2962 to its quiescent point safely and confirm the thermal design case.
- **Parts & tools:** 22 V source with current limit (xlsx: ID limit 2840 mA — `power_rails.md` §1 row `+22V0`/`VD`); GUI status tab (INA241 `PA_AvgCurrent` field of the status string); thermocouple on the heat-spreader plate; the DSN-PSU-01 module if built.
- **Action:** per board n: VG −4 V (firmware sets −3.98 V = DAC code 126, `main.cpp:1583`) → VD 22 V (`EN/DIS_RFPA_VDD`) → raise VG until IDQ 1.68 A (IDQ servo `main.cpp:1628-1656`) → only then RF (xlsx L58-L62 as quoted in `power_rails.md`).
- **Check:** IDQ within ±10 % of 1.68 A (step source E6 — ASSUMED tolerance); plate temperature < 70 °C after 10 min **with drain gating** (design case B: plate max 64.3 °C, PA base ≈ 73 °C at 45 °C ambient — `DESIGN_CALCULATIONS.md` §1); never run continuous bias on all 16 boards (case A: plate > 213 °C).
- **Figure:** F10.9a/b.
- **⚠ Decision:** ⚠ K4 (no 22 V source in CAD), ⚠ D-14 (drain gating not implemented — without it only short single-board tests are thermally admissible), ADAR1000/ADTR1107 LNA/PA rails per MAN-12-1.

### Step 16.7 — Host link [BETA]

- **Purpose:** prove the GUI ↔ firmware ↔ FPGA stream.
- **Parts & tools:** host PC with the `beta/gui` venv (chapter 13); USB cable to X53 (through the slip ring once Step 15.18 is done).
- **Action:** first `python -m aeris10_gui --selftest` on the host (no hardware); then `python -m aeris10_gui --port <CDC port>` and press Start: the GUI sends the start flag and the 82-byte settings packet, then expects status strings and, with the FPGA bridge running, bridge frames.
- **Check:** `--selftest` exit 0 (executed 2026-10-09, chapter 13 Step 13.2); with hardware: status strings parsed, bridge frames arrive with `seq` incrementing and `crc_errors` 0 in the GUI status bar; `REG R 0xF` returns 0xBE7A.
- **Figure:** F13.3.
- **⚠ Decision:** AC-S6 (CDC enumerates; start flag + settings accepted; status received) NOT RUN; the settings packet has no acknowledgement (`beta/gui/README.md` assumption 7) — confirmation is only indirect via the status string.

### Step 16.8 — Beam steering [BETA tables, ⚠ no hardware verification]

- **Purpose:** verify that the firmware writes the ADAR1000 phase tables for the 31 elevation positions.
- **Parts & tools:** logic analyser on the 1.8 V side of the FPGA level shifters (ADAR1000 SPI1: SCLK/MOSI/MISO + CS PA0..PA3 → FPGA pass-through); optionally a VNA/phase measurement on one row.
- **Action:** step the beam position (firmware sequence); capture the SPI traffic.
- **Check:** CS toggles per device (D-05); SCLK 6.75 MHz (D-06); phase words follow `degreesTo7BitPhase` → data-sheet Tables 10-13 → CHx_RX/TX_PHASE_I/Q with register offset `((channel - 1) & 3)` (C10 fix); "data-sheet tables realise the nominal phase within ~3°; array calibration needed" (`beta/stm32/README.md` §7 item 3).
- **Figure:** —
- **⚠ Decision:** ADAR1000 SCLK maximum and level-shifter bandwidth at 6.75 MHz "REQUIRES DATASHEET / BOARD VERIFICATION" (D-06); the SPI pass-through adds one `clk_100m` cycle to SCLK/MOSI/CS and two to MISO (`beta/fpga/README.md`, "Known limitations").

### Step 16.9 — First RF test into a dummy load, then antenna [PROPOSED]

- **Purpose:** confirm the transmit waveform at 10.5 GHz before radiating.
- **Parts & tools:** 50 Ω high-power load or anechoic setup (S2); spectrum analyser / fast power detector; the PA chain of Step 16.6.
- **Action:** transmit the long-chirp set into the load; observe the spectrum around 10.5 GHz and the pulse envelope.
- **Check:** carrier at 10.5 GHz; pulse envelope 30 µs (long chirp, PRI 167 µs; `main.cpp:180-186` as quoted in `engineering/DESIGN/00_DESIGN_BASIS.md` §1); chirp bandwidth B is **TBD** in the parameter table (`DESIGN_CALCULATIONS.md` §3 assumes 50 MHz) — record what is measured.
- **Figure:** —
- **⚠ Decision:** D-01 antenna variant; the chirp direction at baseband decides `CONJUGATE_REF` in the FPGA matched filter (`beta/fpga/README.md`, note 1).

### Step 16.10 — Close the lid; pedestal rotation test [PROPOSED, ⚠ D-12]

- **Purpose:** complete the head and verify the azimuth scan timing.
- **Parts & tools:** lid #6 with gasket #7 and M4×8 ×8 (parts list); stopwatch / log of the firmware azimuth counter.
- **Action:** fit the lid (pitch 60 mm, gasket compressed to 2 mm — parts list "Sealing"); run 50 azimuth positions; log the scan time.
- **Check:** ≈ 19 s per revolution with the NEMA 23 at 200 ms per step (DSN-CALC-01 §2: 18.8 s for 50 × (175 ms dwell + 200 ms move)); harness continuity through the slip ring maintained over 360°.
- **Figure:** F10.5.
- **⚠ Decision:** D-12 motor class / ratio and the matching `Stepper_steps` constant (600 for 1:3, 1200 for 1:6); CBL-144 driver location.

## 16.2 Validation plan (software-based design checks and physical tests)

Copied from `docs/TESTING/VALIDATION_PLAN.md` (status date 2026-10-08 unless a later executed result is noted; the authoring machine had iverilog 13.0 and Verilator 5.052 but **no Vivado, no EAGLE**; the Arm GCC and KiCad used later by the beta trees are recorded in `beta/*/README.md`). "A test is reported PASSED only if it was executed and succeeded. 'Software-based design check' means a file/tool check; 'physical verification' needs hardware and is never claimed here." Run everything runnable with `bash tools/run_all_checks.sh` (exit code = number of failed checks).

### FPGA (section 1)

| ID | Test | Type | Command | Result on the original tree (2026-10-08) | BETA tree result (`beta/fpga/README.md`, 2026-10-09) |
|---|---|---|---|---|---|
| F-01 | Syntax / parse of all RTL | design check | `tools/fpga_lint.sh` (iverilog -g2012) | **FAIL** — `radar_system_top.v:312` syntax error | PASS (iverilog, both views) |
| F-02 | Elaboration of `radar_system_top` | design check | same | **FAIL** — 6 missing modules on a patched copy | PASS |
| F-03 | Lint | design check | `verilator --lint-only -Wall` | **FAIL** — 207 warnings incl. MULTIDRIVEN ×4, UNDRIVEN ×14 (with stubs) | PASS, 0 %Error, 165/159 %Warning (synth/sim view) |
| F-04 | Constraint completeness | design check | `python3 tools/check_fpga_constraints.py` | **FAIL** (exit 1) — 142 placeholder lines, 180/180 bits without PACKAGE_PIN | beta XDC: 0 placeholders, 67/183 port bits constrained (116 UNRESOLVED) |
| F-05 | Schematic-derived pin map generation | design check | `python3 tools/gen_xdc_from_schematic.py` | PASSED (exit 0) — 64 ports mapped, 25 unresolved (generation step, not a correctness proof) | used verbatim in the beta XDC |
| F-06 | Simulation `radar_system_tb` | design check | Vivado xsim (SVA needed) | NOT RUN | 9 open-source testbench runs PASS (`build.sh`: 0 failures) |
| F-07 | Synthesis utilisation on `xc7a50tftg256-2` | design check | `tools/vivado/create_project.tcl` + `launch_runs synth_1` | NOT RUN | NOT RUN |
| F-08 | Timing summary / clock interaction / CDC report | design check | `report_timing_summary`, `report_cdc` | NOT RUN | NOT RUN |
| F-09 | Bitstream generation | design check | `write_bitstream` | NOT RUN | NOT RUN |
| F-10 | ADC LVDS capture on hardware (eye/valid data) | physical | ILA + known tone into AD9484 | NOT RUN | NOT RUN |

### STM32 (section 2)

| ID | Test | Type | Command | Result on the original tree | BETA tree result (`beta/stm32/README.md`) |
|---|---|---|---|---|---|
| S-01 | Dependency / include check | design check | `python3 tools/check_stm32_includes.py` | **FAIL** (exit 1) — 53 absent HAL/CMSIS/USB headers, 6 case mismatches | 0 case mismatches; 11 UNKNOWN headers only in unbuilt `iio*.c` |
| S-02 | Cube package completeness | design check | `tools/stm32_check_cube_package.sh <CubeF7>` | NOT RUN (no package) | "missing 0 of 34", exit 0 |
| S-03 | Host syntax probe (non-target) | design check | `clang -fsyntax-only …` | 29/60 TUs fail on missing `stm32f7xx_hal.h` (informational) | superseded by S-04 |
| S-04 | Cross-compile | design check | `arm-none-eabi-g++` | NOT RUN | `build.sh` exit 0, 0 errors, 5 pre-existing warnings |
| S-05 | Link + size | design check | `arm-none-eabi-size` | NOT RUN | RAM 17 480 B (5.33 %), FLASH 93 276 B (8.90 %) |
| S-06 | Static analysis | design check | `cppcheck --enable=warning,style` | NOT RUN (not installed) | NOT RUN |
| S-07 | Pin-map cross-check firmware ↔ schematic | design check | `tools/extract_eagle_netlist.py --part U2` vs `main.h` | PASSED for the 60 named GPIO macros; **conflict found** for HSE (8 vs 25 MHz) and ADF4382 pins | conflicts closed by D-01, D-04 |
| S-08 | Flash + CDC enumeration | physical | ST-LINK, `lsusb`/Device Manager | NOT RUN | NOT RUN (Step 16.1) |
| S-09 | Settings packet accepted (state READY_FOR_DATA) | physical | send flag + 82-byte packet | NOT RUN (static analysis predicted failure: C4, C5) | NOT RUN; C4/C5 fixed and host-tested |
| S-10 | Power-sequence timing on `EN_*` rails | physical | oscilloscope | NOT RUN | NOT RUN (Step 16.2) |

### Python (section 3)

| ID | Test | Type | Command | Result on the original scripts | BETA package result |
|---|---|---|---|---|---|
| P-01 | Dependency resolution | design check | `pip install -r requirements.txt` in a venv | PASSED (10 packages) | pinned `beta/gui/requirements.txt` installed |
| P-02 | Syntax (ast) of 27 scripts | design check | `python3 tools/check_python_imports.py` | **FAIL** (exit 1) — `GUI_V1.py` IndentationError; 26/27 OK | n/a |
| P-03 | Import test of third-party modules | design check | `… --try-import` (venv) | PASSED for GUI modules; FAIL for `openEMS`/`CSXCAD` (not on PyPI) | n/a |
| P-04 | Module import of each GUI file | design check | `python -c "import GUI_V6_Demo"` etc. | PASSED V2…V6_Demo (import only); V1 FAIL | n/a |
| P-05 | pyflakes | design check | `pyflakes 9_Firmware/9_3_GUI/*.py` | undefined names in `GUI_V6.py:392`, `GUI_V4_2_CSV.py:430` (informational) | n/a |
| P-06 | Unit tests | design check | `pytest` | NOT RUN — no tests exist upstream | **76 passed in 3.62s** (executed 2026-10-09 for this edition) |
| P-07 | GUI startup smoke | design check | procedure GUI-T05 | NOT RUN | `--selftest` exit 0 (executed 2026-10-09); headless Tk smoke tests in the suite |
| P-08 | Demo-data verification (`test_radar_data.csv`) | design check | column/row check | PASSED (16 384 rows = 32 chirps × 512) | used by `tests/test_sim_pipeline.py` |
| P-09 | Hardware link (CDC / FTDI) | physical | — | NOT RUN | NOT RUN (Step 16.7) |

### PCB documentation (section 4)

| ID | Test | Type | Command | Result |
|---|---|---|---|---|
| B-01 | ERC (fresh run) | design check | EAGLE `ERC` | NOT RUN — stored approved ERC items: Main 4, others 0 |
| B-02 | DRC (fresh run) | design check | EAGLE `RATSNEST; DRC` | NOT RUN — stored: Main 211 approved + 2 390 airwires; Power 309 airwires; Synth 0; PA 0 (KiCad DRC of the beta boards: Main/RF PA 0 unconnected, Power 89 — `beta/pcb/README.md`) |
| B-03 | Missing-library detection | design check | XML: all `<library>` embedded | PASSED — no external library references for any board |
| B-04 | sch/brd consistency | design check | part/net set comparison (XML) | PASSED Synth, PA; **FAIL** Main (10 board-only signals, 210 value mismatches) and Power (version mismatch 9.6.2/7.4.0, 1 board-only signal) |
| B-05 | BOM completeness | design check | `python3 tools/gen_eagle_bom.py …` → `docs/BOM/` | **FAIL** — 0 MPN attributes on all boards; value-less references 244/80/6/47 |
| B-06 | Manufacturing-export completeness | design check | `python3 tools/check_manufacturing_files.py` | **FAIL** (exit 1) for the designer-released export; `--include-generated` exit 0 for the generated `engineering/PCB/` packages (AC-B4) |
| B-07 | Outline/hole extraction | design check | `python3 tools/gen_board_outline_svg.py …` | PASSED for 4 boards |
| B-08 | Stack-up confirmation | physical/vendor | fab quote with stack-up drawing | NOT RUN |
| B-09 | Impedance coupon measurement | physical | TDR at fab | NOT RUN |

### Repository / documentation (section 5)

| ID | Test | Command | Result |
|---|---|---|---|
| R-01 | Inventory generation | `python3 tools/gen_inventory_doc.py` | PASSED (482 rows) |
| R-02 | Documentation link validation | `python3 tools/check_doc_links.py` | **FAIL** — 34 broken references before the reconstruction (README `10_docs/*` etc.); re-run for the residual list |
| R-03 | Expected-artifact manifest | `python3 tools/check_missing_files.py` | **FAIL** — 26 P0 items missing (see `docs/03_MISSING_COMPONENTS.md`) |

## 16.3 Acceptance criteria (sections A–H)

Copied from `docs/TESTING/ACCEPTANCE_CRITERIA.md` ("Each criterion is objective, references the test ID … Current status is given honestly: nothing hardware-related is accepted"). Status column as recorded in the source on 2026-10-08/09; the BETA tree (section H) is evaluated on `beta/`, not on the originals.

| ID | Criterion | Evidence required | Status |
|---|---|---|---|
| AC-F1 | RTL parses and elaborates with iverilog and verilator with zero errors (F-01..F-03) | `build/lint/iverilog_top.log` empty of errors; verilator 0 `%Error` | NOT MET (original); see AC-X1 |
| AC-F2 | No module instantiated without definition; all Xilinx IP as committed `.xci` | Vivado elaboration log; `ls 9_Firmware/9_2_FPGA/ip/*.xci` | NOT MET (6 missing) |
| AC-F3 | `cntrt.xdc` (or successor) has zero placeholders and every top-level port bit constrained or removed; F-04 exit 0 | tool output | NOT MET |
| AC-F4 | Pin map confirmed by the designer against the AMD FTG256 package file and the routed board | signed-off `PIN_MAP_FROM_SCHEMATIC.md` with "VERIFIED" column | NOT MET |
| AC-F5 | Synthesis on the confirmed part with ≤ 90 % of LUT/FF/DSP/BRAM and zero unresolved CRITICAL WARNINGs | `build/vivado/util.rpt` | NOT MET |
| AC-F6 | Timing closure WNS ≥ 0, WHS ≥ 0 on all constrained clocks; `report_cdc` no critical | `timing.rpt`, `cdc.rpt` | NOT MET |
| AC-F7 | Testbench runs on xsim with pass/fail gating and passes | sim log with 0 assertion failures | NOT MET |
| AC-F8 | Bitstream generated and archived with its build log | `build/vivado/*.bit` + log | NOT MET |
| AC-F9 | (Physical) ADC capture validated with a CW tone | ILA capture / host data | NOT RUN |
| AC-S1 | Cube package check exit 0 (S-02) | script output | NOT MET (no package; beta: exit 0) |
| AC-S2 | `.ioc` regenerated; generated MSP equals repository MSP | diff | NOT MET |
| AC-S3 | `tools/check_stm32_includes.py` exit 0 with Cube sources on the include path and zero case mismatches | tool output | NOT MET |
| AC-S4 | Firmware compiles and links with `arm-none-eabi-g++`, zero errors; size < 1 MB flash / 320 KB RAM | map, `size` output | NOT MET (original); see AC-X2 |
| AC-S5 | Conflicts C1–C7 closed with documented decisions | `docs/04_RECOVERY_TASKS.md` R-STM-xx DONE | NOT MET |
| AC-S6 | (Physical) CDC enumerates; start flag + settings accepted; status string received | host log | NOT RUN |
| AC-S7 | (Physical) rail sequencing order and delays match `Power Management V6.xlsx` | scope captures | NOT RUN |
| AC-P1 | `pip install -r requirements.txt` succeeds on a clean venv | pip log | **MET** (2026-10-08, Python 3.14.7) |
| AC-P2 | All third-party imports succeed | tool output | **MET** for GUI modules |
| AC-P3 | Every file in `9_Firmware/9_3_GUI` parses | tool exit 0 | NOT MET (`GUI_V1.py`) |
| AC-P4 | `GUI_V6_Demo.py` starts, shows moving targets, closes with exit 0 | screenshot + exit code | NOT RUN |
| AC-P5 | A unit-test suite exists and passes | pytest log | NOT MET (upstream); see AC-X3 |
| AC-P6 | One hardware GUI decodes the real firmware/FPGA packet format end-to-end | capture + decoded targets | NOT RUN |
| AC-P7 | Packaged demo runs on a machine without Python | installer test log | NOT RUN |
| AC-B1 | Fresh ERC and DRC reports with 0 unapproved errors for each board | reports under `docs/PCB/reports/` (directory to be created) | NOT MET |
| AC-B2 | `RATSNEST` "Nothing to do" and 0 elements outside the outline for Main and Power | EAGLE status line | NOT MET |
| AC-B3 | sch/brd consistent, single EAGLE version per board | consistency check pass | NOT MET (Main, Power) |
| AC-B4 | Gerber + drill + fab + assembly + P&P + BOM(MPN) + schematic PDF for all four boards | `tools/check_manufacturing_files.py` exit 0 | **PARTIALLY MET** (generated packages exist for all four boards; designer-released EAGLE export, MPNs, vendor fab notes NOT MET) |
| AC-B5 | BOMs 100 % MPN, 0 empty values, DNP column | `docs/BOM/*` with `mpn_status` all VERIFIED | NOT MET |
| AC-B6 | Vendor stack-up drawing per board consistent with DRU and impedance note | fab documents | NOT MET |
| AC-B7 | (Physical) impedance coupons 50 Ω ± 10 %, 100 Ω ± 8 % | TDR report | NOT RUN |
| AC-B8 | Design conflicts K1, K2, K3, K4, K7 closed | decision records | NOT MET |
| AC-M1 | Outline/hole drawings for all PCBs | `engineering/MECHANICAL/` DXF, STEP, plan view, dimension sheets | **MET** (thickness ASSUMED) |
| AC-M2 | Enclosure, antenna and pedestal CAD committed with drawings | STEP + PDF under `10_docs/Hardware/` (missing in the repository) | NOT MET (PROPOSED designs exist under `engineering/DESIGN/`, chapter 10) |
| AC-M3 | Assembly guide `10_docs/assembly_guide.md` (missing in the repository) | file exists, link check passes | NOT MET (this manual's chapter 15 is the proposed content) |
| AC-M4 | Exploded view with balloons matching BOM | PDF | PARTIAL (CONCEPTUAL view with balloons; real geometry BLOCKED, MDR-06) |
| AC-M5 | Mass table per assembly | measured or CAD-derived values | NOT MET (estimates only) |
| AC-D1 | Documentation tree of `claude.md` §13 present | `tools/check_missing_files.py` DOC-* all present | **MET** |
| AC-D2 | `tools/check_doc_links.py` exit 0 | tool output | NOT MET |
| AC-D3 | README corrected (Gerber claim, FPGA part, `10_docs` references) | diff | NOT MET (needs the owner's decision) |
| AC-D4 | LICENSE file consistent with the MIT badge; `.gitignore` | files | NOT MET |
| AC-D5 | Every P0 item in `docs/03_MISSING_COMPONENTS.md` has an owner and a recovery task | `docs/04_RECOVERY_TASKS.md` | **MET** (tasks defined; none closed) |
| AC-E1 | Every registered drawing has native file and exports present and well-formed | `python3 tools/gen_drawing_register.py --check` exit 0 | **MET** (re-run 2026-10-09: 89 drawings, 333 files, 0 problems) |
| AC-E2 | EAGLE XML ↔ KiCad conversion counts agree for all boards | `engineering/VALIDATION/PCB_CROSS_CHECK.md` | **MET** (32/32 rows OK) |
| AC-E3 | No missing symbols/footprints; schematic ↔ board part lists identical | `tools/gen_schematic_reports.py` exit 0 | **MET** |
| AC-E4 | Any drawing VERIFIED against EAGLE output or hardware | `VALIDATION/DRAWING_CHECKS.md` §2 | NOT MET (0 VERIFIED) |
| AC-E5 | Enclosure/antenna/pedestal/cooling drawings exist | register MECH-ENC/ANT/PED/COOL | NOT MET (BLOCKED; DSN-* proposals exist) |
| AC-E6 | Proposed designs (DSN-*) registered with native editable files and exports present | `tools/gen_drawing_register.py --check` | **MET** (16 PROPOSED entries after regeneration, 0 file problems) |
| AC-E7 | Antenna proposal simulated (S11 < −10 dB at f0 ± B/2) and coupon measured | openEMS log + VNA data | simulation MET per AC-X6; coupon NOT RUN |
| AC-E8 | Owner approval of decisions D-01…D-15 recorded | signed decision log | NOT MET |
| AC-X1 | beta RTL parses/elaborates/lints with 0 errors and all testbenches pass | `beta/fpga/logs/` | **MET** (BETA) |
| AC-X2 | beta firmware compiles and links; host tests pass | `beta/stm32/build_out/`, `logs/` | **MET** (BETA) |
| AC-X3 | beta GUI test suite passes; packaged app starts | `beta/gui` pytest (source says 55 passed; 76 passed on 2026-10-09) | **MET** (BETA) |
| AC-X4 | beta boards: 0 unconnected on Main/RF PA/Synth; Power ≤ 100 open with documented reasons | `beta/pcb/*/exports/reports/DRC_report.json` | **MET** (BETA; Power 89 listed) |
| AC-X5 | host-link bridge testbench, firmware build and GUI parser agree on one frame vector | `tb_frame.hex` shared | **MET** (BETA) |
| AC-X6 | antenna row S11 < −10 dB at f0 in simulation | `TUNING_LOG.md` | **MET** (−18 dB; band 128 MHz) |

Observation MAN-16-1: `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-E1/AC-E6 still quote "73 drawings" and "11 PROPOSED entries"; the register regenerated for this edition has 89 drawings and 16 PROPOSED entries (Appendix A). The acceptance file was not modified (it is outside `manual/`).

## 16.4 Evidence collection

Rules (source: `docs/TESTING/VALIDATION_PLAN.md` §6, copied): every executed command's output is saved under `build/` (lint logs in `build/lint/`, Vivado in `build/vivado/`, STM32 in `build/stm32/`) and referenced by test ID in `docs/TESTING/ACCEPTANCE_CRITERIA.md` when reporting; physical tests record instrument, serial number, date and raw capture file; a test result changes from NOT RUN to PASSED/FAILED only with an attached log. BETA logs already exist under `beta/fpga/logs/`, `beta/stm32/logs/` and are referenced by the tables above.

Evidence to collect during the first integration (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §D, extended by the steps above), to be stored under `engineering/VALIDATION/` with the acceptance ID it closes:

| Item | Step | Closes |
|---|---|---|
| Rail voltages, no load, per X2…X35 (CP-4) | 15.4 | AC-S7 input |
| Scope captures of the enable sequence F1–F10 with delays | 16.2 | AC-S7 |
| USART3 banner and host CDC enumeration log (VID/PID, serial = UID) | 16.1 | AC-S6 |
| Settings packet accepted → status string received | 16.7 | AC-S6, AC-P6 |
| AD9523 lock status and counter readings 100 / 120 / 400 MHz | 16.4 | Step 16.4 acceptance |
| CAL_STAT / CAL_LANE_INFO / CAL_ERR / CAL_UNDET per lane, ADC pattern used | 16.5 | AC-F9 |
| FPGA DONE, DIG_0..4 handshake capture; Vivado utilisation/timing/CDC reports and bitstream log | 16.3 | AC-F5…AC-F8 |
| PA IDQ per board and plate temperature vs time (drain gating on/off noted) | 16.6 | thermal design case B |
| ADAR1000 SPI capture (CS, SCLK, phase words) | 16.8 | D-06, D-19 |
| Spectrum and envelope at 10.5 GHz into the load; measured chirp bandwidth B | 16.9 | parameter-table TBD |
| Scan time per revolution, motor class and `Stepper_steps` used | 16.10 | D-12 |
| Photos of the first harness with cable labels; real cut lengths of the 144 cables | 15.14–15.18 | DSN-HAR-01 |
| Measured board thickness and component heights | 15.1, 15.9 | G-01, G-02 |
