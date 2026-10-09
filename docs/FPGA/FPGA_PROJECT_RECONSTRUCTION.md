# FPGA Project Reconstruction — AERIS-10 (`9_Firmware/9_2_FPGA/`)

Status date: 2026-10-08. Evidence: static inspection of all 25 `.v`, 1 `.xdc`, 8 `.mem` files; Icarus Verilog 13.0 and Verilator 5.052 runs (section 4); EAGLE schematic netlist extraction (`tools/extract_eagle_netlist.py`). Line references are relative to `9_Firmware/9_2_FPGA/` unless a full path is given. Nothing in this document was verified on hardware. No repository RTL file was modified; all generated artefacts are new files.

**Bottom line:** the FPGA sources cannot be elaborated by any tool today. Before a Vivado project can even reach synthesis, four user modules and two Xilinx FFT IP configurations must be recovered, three syntax/declaration defects must be fixed, and the device part number must be confirmed (schematic says XC7A50T-2FTG256I; README/XDC say XC7A100T). Pin assignment can be reconstructed for 64 of 67 top-level ports from the Main Board schematic, but 25 ports (FT601 USB 3.0, status and debug outputs) have no board counterpart because the FT601 was never wired.

---

## 1. Device identification

| Source | Device statement | Evidence |
|---|---|---|
| Main Board schematic | **XC7A50T-2FTG256I**, package `BGA256C100P16X16_1700X1700X155` | `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` part `U42`, library/deviceset `XC7A50T-2FTG256I` |
| Power budget workbook | `XC7A50T-2FTG256` | `3_Power Management/Power Management V6.xlsx` (sharedStrings entry 25) |
| Block diagram | `XC7A50T-2FTG256` | `2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio` |
| Constraint file | `# Device: [XC7A100T]` (placeholder brackets, no package, no speed grade) | `cntrt.xdc:4` |
| README / hardware docs | "XC7A100T FPGA" | `README.md:52`; `02_hardware/05_fpga_board.md:1,15,30,34,262` |

**Conclusion:** the only CAD evidence is XC7A50T-2FTG256I (speed grade −2, industrial). The XC7A100T claim appears only in prose and in a placeholder comment. Resource estimates in `02_hardware/05_fpga_board.md:44` (300 I/O etc.) therefore describe the wrong device. Vivado part string for the CAD device: `xc7a50tftg256-2`. Whether the design (two 1024-point FFT IPs, 64 parallel DSP multipliers in the FIR, ~32k flip-flops of matched-filter buffers — section 7) fits a 50T (52 160 logic cells, 120 DSP48E1, 2 700 Kbit BRAM per AMD DS180) is **UNRESOLVED** and must be answered by a real synthesis run. Any part substitution must be checked against AMD DS180 Table "Artix-7 Device-Package Combinations" and the board must be re-verified: `UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION`.

---

## 2. Source inventory and module hierarchy

### 2.1 Files

| File | Module(s) defined | Role | Status |
|---|---|---|---|
| `radar_system_top.v` | `radar_system_top` (line 18) | top level, 67 ports / 180 bits | INCOMPLETE — syntax error at :312 (`wire` declared inside `always`), `wire` assigned procedurally at :155-156/:304-318 |
| `radar_transmitter.v` | `radar_transmitter` (:21) | chirp controller + DAC interface + ADAR load/TR | REQUIRES VALIDATION — SPI level-shifter outputs undriven (:59-71) |
| `plfm_chirp_controller.v` | `plfm_chirp_controller_enhanced` (:3) | TX FSM, inline chirp LUTs (3600 + 60 entries, :99-560) | REQUIRES VALIDATION — `chirp_counter` multi-driven from `clk_100m` (:564-576) and `clk_120m` (:683-784) |
| `dac_interface_single.v` | `dac_interface_enhanced` | 8-bit DAC register; forwards `clk_120m` directly to `dac_clk` (:23) | REQUIRES VALIDATION |
| `edge_detector.v` | `edge_detector_enhanced` | STM32 toggle detection | REQUIRES VALIDATION — edge uses first synchroniser stage (:16-23) |
| `radar_receiver_final.v` | `radar_receiver_final` (:3) | RX chain wrapper | INCOMPLETE — instantiates 2 missing modules (:82, :226), phantom ports `.ref_i/.ref_q` (:216-217), use-before-declare (:150 vs :192), undriven controls (:21-22, :206-208) |
| `lvds_to_cmos_400m.v` | `lvds_to_cmos_400m` | IBUFDS+BUFG on DCO, then a flop re-sampling its own clock (:35-43) | INCOMPLETE — not a clock capture structure |
| `ad9484_interface_400m.v` | `ad9484_interface_400m` | IBUFDS x9 + IDDR x8 capture | ORPHAN (never instantiated; different port list from the missing `ad9484_lvds_to_cmos_400m`) |
| `ddc_input_interface.v` | `ddc_input_interface` | input formatting | REQUIRES VALIDATION |
| `ddc_400m.v` | `ddc_400m_enhanced`, `lfsr_dither_enhanced` | NCO mixer, CIC, FIR | INCOMPLETE — use-before-declare :252-266 vs :272-275; `reset_monitors` in async reset condition :118 |
| `nco_400m_enhanced.v` | `nco_400m_enhanced` | 64-entry quarter-wave LUT NCO | REQUIRES VALIDATION — LUT monotonicity questionable (:34-49) |
| `cic_decimator_4x_enhanced.v` | `cic_decimator_4x_enhanced` | CIC /4 | INCOMPLETE — three always blocks drive the same regs (:71, :181, :291); `posedge reset_monitors` used as a clock |
| `fir_lowpass.v` | `fir_lowpass_parallel_enhanced` | 32-tap parallel FIR | REQUIRES VALIDATION — 32 multipliers + combinational adder tree (:50-73) |
| `cdc_modules.v` | `cdc_adc_to_processing`, `cdc_single_bit`, `cdc_handshake` | clock crossing | REQUIRES VALIDATION — Gray-coding arbitrary data (:74) is not a valid CDC; the two safe modules are orphans |
| `chirp_memory_loader_param.v` | `chirp_memory_loader_param` | `$readmemh` ROM loader | MISSING DEPENDENCY — absolute Windows paths (:3-12); `long_chirp_seg3_{i,q}.mem` do not exist |
| `latency_buffer_2159.v` | `latency_buffer_2159` | delay line | REQUIRES VALIDATION — asynchronous read (:102) blocks BRAM inference; LATENCY 3187 vs name 2159 |
| `matched_filter_multi_segment.v` | `matched_filter_multi_segment` | segment FSM | MISSING DEPENDENCY — instantiates `matched_filter_processing_chain` (:361) which does not exist |
| `frequency_matched_filter.v` | `frequency_matched_filter` | frequency-domain multiply | ORPHAN |
| `fft_1024_forward.v`, `fft_1024_inverse.v` | `fft_1024_forward_enhanced`, `fft_1024_inverse_enhanced` | wrappers around Xilinx FFT IP `FFT_enhanced` (:102 / :78) | ORPHAN + MISSING IP |
| `doppler_processor.v` | `doppler_processor_optimized` | 32-point Doppler FFT via Xilinx IP `xfft_32` (:283) | MISSING IP; incomplete case :159; paste artefact :210-211 |
| `usb_data_interface.v` | `usb_data_interface` | FT601 32-bit FIFO master | REQUIRES VALIDATION — `ft601_clk_out` driven from two clocks (:65-79, :176-182); SV `typedef enum` in a `.v` file (:46) |
| `usb_packet_analyzer.v` | `usb_packet_analyzer` | verification helper | ORPHAN |
| `level_shifter_interface.v` | `level_shifter_interface` | 3.3 V <-> 1.8 V SPI pass-through | ORPHAN (never instantiated, hence the undriven top-level SPI outputs) |
| `chirp_lut_init.v` | none (bare `initial` at :6) | alternative TX LUT values, differ from inline copy | PLACEHOLDER / dead code |
| `radar_system_tb.v` | `radar_system_tb` | system testbench with SystemVerilog assertions (:528-543) | REQUIRES VALIDATION — needs an SVA-capable simulator |
| `cntrt.xdc` | — | constraints | PLACEHOLDER — 142 placeholder lines (section 5) |
| `long_chirp_seg{0,1,2}_{i,q}.mem` | — | 1024 lines each, 4 hex digits (16-bit) | COMPLETE (format verified) |
| `short_chirp_{i,q}.mem` | — | 50 lines each | COMPLETE |

### 2.2 Instantiation tree (as written)

```
radar_system_top                                   radar_system_top.v:18
├── BUFG x3 (clk_100m / clk_120m_dac / ft601_clk)   :174 :179 :184     (UNISIM)
├── radar_transmitter tx_inst                       :204
│   ├── edge_detector_enhanced x3                    radar_transmitter.v:93,100,107
│   ├── plfm_chirp_controller_enhanced               :115
│   └── dac_interface_enhanced                       :148
├── radar_receiver_final rx_inst                    :270
│   ├── lvds_to_cmos_400m (IBUFDS, BUFG)             radar_receiver_final.v:61
│   ├── ad9484_lvds_to_cmos_400m                     :82     *** MISSING ***
│   ├── cdc_adc_to_processing #(8,3)                 :94
│   ├── ddc_400m_enhanced                            :114
│   │   ├── lfsr_dither_enhanced                     ddc_400m.v:131
│   │   ├── nco_400m_enhanced                        :152
│   │   ├── cic_decimator_4x_enhanced x2             :223 :232
│   │   ├── cdc_adc_to_processing #(18,3) x2         :243 :256
│   │   └── fir_lowpass_parallel_enhanced x2         :278 :290
│   ├── ddc_input_interface                          :129
│   ├── chirp_memory_loader_param                    :144   ($readmemh x10, 2 files missing)
│   ├── latency_buffer_2159 #(32,3187)               :173
│   ├── matched_filter_multi_segment                 :198
│   │   └── matched_filter_processing_chain          matched_filter_multi_segment.v:361  *** MISSING ***
│   ├── range_bin_decimator #(1024,64,16)            :226   *** MISSING ***
│   └── doppler_processor_optimized #(32,64,32)      :290
│       └── xfft_32                                  doppler_processor.v:283   *** MISSING Xilinx FFT IP ***
└── usb_data_interface usb_inst                     :345
Orphans: ad9484_interface_400m, fft_1024_forward_enhanced -> FFT_enhanced (*** MISSING IP ***),
         fft_1024_inverse_enhanced -> FFT_enhanced, frequency_matched_filter, level_shifter_interface,
         cdc_single_bit, cdc_handshake, usb_packet_analyzer
```

### 2.3 Missing modules — inferred interfaces (from the instantiations only; INFERENCE, not design data)

| Missing module | Instantiated at | Inferred ports / parameters | Probable origin |
|---|---|---|---|
| `ad9484_lvds_to_cmos_400m` | `radar_receiver_final.v:82-92` | in `adc_d_p[7:0]`, `adc_d_n[7:0]`, `adc_dco_p`, `adc_dco_n`, `reset_n`; out `adc_data_cmos[7:0]`, `adc_dco_cmos`, `adc_valid`, `adc_pwdn` | a renamed rewrite of `ad9484_interface_400m.v` (which lacks `adc_pwdn`, `adc_dco_cmos`, `adc_valid`) |
| `range_bin_decimator` | `radar_receiver_final.v:226-242` | params `INPUT_BINS=1024, OUTPUT_BINS=64, DECIMATION_FACTOR=16`; in `clk, reset_n, range_i_in[15:0], range_q_in[15:0], range_valid_in, decimation_mode[1:0], start_bin[9:0]`; out `range_i_out, range_q_out, range_valid_out, range_bin_index[5:0]` | not present in any form |
| `matched_filter_processing_chain` | `matched_filter_multi_segment.v:361-386` | in `clk, reset_n, adc_data_i/q[15:0], adc_valid, chirp_counter[5:0], long_chirp_real/imag[15:0], short_chirp_real/imag[15:0]`; out `range_profile_i/q[15:0], range_profile_valid, chain_state[3:0]` | likely composed of the orphans `fft_1024_forward_enhanced` -> `frequency_matched_filter` -> `fft_1024_inverse_enhanced` |
| `xfft_32` | `doppler_processor.v:283-296` | AXI4-Stream FFT, 32-point, `s_axis_config_tdata[7:0]`, 32-bit `{Q,I}` data | Xilinx FFT IP (`.xci` absent) |
| `FFT_enhanced` | `fft_1024_forward.v:102`, `fft_1024_inverse.v:78` | AXI4-Stream FFT, 1024-point, runtime-configurable direction (config bit 0), `s_axis_config_tdata[15:0]` | Xilinx FFT IP (`.xci` absent); `fft_1024_forward.v:101` "This must match the name in your project" |
| `BUFG`, `IBUFDS`, `IDDR` | various | 7-series primitives | UNISIM (Vivado provides; for iverilog/verilator use `$XILINX_VIVADO/data/verilog/src/unisims`) |

No `.xpr`, `.xise`, `.xci`, `.coe`, `.ucf`, `.dcp` or `.bit` file exists anywhere in the repository (`find` executed 2026-10-08). The `$readmemh` path `C:/Users/dell/Desktop/ASUS/RADAR_V5/Firmware/FPGA/PLFM_RADAR_Xilinx_ISE_V2/...` (`chirp_memory_loader_param.v:3-12`) shows the original project was a Xilinx ISE project; nothing of it survives.

---

## 3. Top-level ports and physical assignment status

Automated check (`python3 tools/check_fpga_constraints.py`, executed 2026-10-08, exit 1):

```
Top module      : radar_system_top (67 ports, 180 bits)
Placeholders    : 142 active lines (+2 in comments)
No PACKAGE_PIN  : 180 / 180 port bits
No IOSTANDARD   : 21 port bits -> clk_100m, clk_120m_dac, ft601_clk_in, current_elevation[5:0], current_azimuth[5:0], current_chirp[5:0]
Invalid props   : 2  (line 320-321: PACKAGE_PIN_BANK is not a Vivado property)
Clocks          : clk_100m 10.0 ns (:14), clk_120m_dac 8.333 ns (:18), ft601_clk_in 10.0 ns (:22), adc_dco_p 2.5 ns (:26)
```

### 3.1 Ports with a schematic-derived candidate pin (64 ports, 100 bits)

Generated by `python3 tools/gen_xdc_from_schematic.py` into `9_Firmware/9_2_FPGA/reconstructed/radar_system_top_schematic_derived.xdc` and `.../PIN_MAP_FROM_SCHEMATIC.md`. The pad (ball) comes verbatim from the schematic library connect table of part U42; the net-name-to-port interpretation carries the stated confidence. **Caveat:** the library `XC7A50T-2FTG256I` is project-authored (not an AMD file); every ball must be cross-checked against the AMD FTG256 package file (`xc7a50tftg256pkg.txt`, UG475) before use, and the Main Board layout is not finished (see `docs/PCB/MAIN_BOARD.md`), so the pin set may still change.

| RTL port group | Schematic nets | Balls | Bank / VCCO (schematic) | Confidence | Note |
|---|---|---|---|---|---|
| `adc_d_p[7:0]` / `adc_d_n[7:0]` | `ADC_D0..7_P/N` | P15/P16, R15/R16, T14/T15, R13/T13, R10/R11, T9/T10, T7/T8, R6/R7 | 14 / +3V3_FPGA | HIGH | **LVDS_25 with `DIFF_TERM TRUE` (cntrt.xdc:160-167) requires VCCO = 2.5 V in HR banks (AMD UG471); bank 14 is 3.3 V on the schematic → constraint/board conflict, REQUIRES VERIFICATION** |
| `adc_dco_p/n` | `ADC_DCO_P/N` | N14 / P14 (MRCC pair) | 14 / +3V3_FPGA | HIGH | same LVDS/VCCO issue |
| `adc_pwdn` | `ADC_PWRD` | T5 | 14 | HIGH | |
| `dac_data[7:0]` | `DAC_0..7` | A14, A13, A12, B11, B10, A10, A9, A8 | 15 / +3V3_FPGA | HIGH | 22 Ω series resistors to AD9708 |
| `dac_sleep` | `DAC_SLEEP` | A15 | 15 | HIGH | |
| `clk_100m` | `FPGA_SYS_CLOCK` | E12 (MRCC) | 15 | MEDIUM | from SMA J1; 100 MHz supported only by firmware AD9523 OUT6 programming (`main.cpp:995-996`) |
| `clk_120m_dac` | `FPGA_DAC_CLOCK` | C13 (MRCC) | 15 | MEDIUM | 120 MHz per firmware AD9523 OUT11 (`main.cpp:1025-1026`); routed to SMA J18 |
| `tx_mixer_en`, `rx_mixer_en` | `MIX_TX_EN`, `MIX_RX_EN` | C11, D11 | 15 | HIGH | LTC5552 EN pins |
| `fpga_rf_switch` | `M3S_VCTRL` | G15 | 15 | MEDIUM | drives VCTRL of all 17 M3SWA2-34DR+ switches |
| `stm32_new_chirp`, `stm32_new_elevation`, `stm32_new_azimuth`, `stm32_mixers_enable`, `reset_n` | `DIG_0..DIG_4` | F13, E16, D16, F15, E15 | 15 | MEDIUM | STM32 PD8..PD12; mapping from `main.cpp:448,484,514,1483,1660` ("New chirp signal to FPGA", elevation, azimuth, mixers, "RESET FPGA") |
| `stm32_sclk_3v3`, `stm32_mosi_3v3`, `stm32_miso_3v3` | `STM32_SCLK1/MOSI1/MISO1` | J16, H13, G14 | 15 | HIGH | shared with STM32 PA5/PA7/PA6 (SPI1) |
| `stm32_cs_adar1..4_3v3` | `ADAR_1..4_CS_3V3` | F14, H16, G16, J15 | 15 | HIGH | shared with STM32 PA0..PA3 |
| `stm32_sclk_1v8`, `stm32_mosi_1v8`, `stm32_miso_1v8` | `STM32_SCLK_1V8/MOSI_1V8/MISO_1V8` | P5, M1, N3 | 34 / +1V8_FPGA | HIGH | **cntrt.xdc:116 says LVCMOS18 — consistent** |
| `stm32_cs_adar1..4_1v8` | `ADAR_1..4_CS_1V8` | L5, L4, M4, M2 | 34 / +1V8_FPGA | HIGH | |
| `adar_tx_load_1..4` | `ADAR_TX_LOAD_1..4` | P3, T4, R3, R2 | 34 / +1V8_FPGA | HIGH | **cntrt.xdc:85 assigns LVCMOS33 to `adar_*_load_*` — contradicts the 1.8 V bank; must be LVCMOS18** |
| `adar_rx_load_1..4` | `ADAR_RX_LOAD_1..4` | M5, T2, R1, N4 | 34 / +1V8_FPGA | HIGH | same LVCMOS33 error at `cntrt.xdc:85` |
| `adar_tr_1..4` | `ADAR_TR_1..4` | N2, N1, P1, P4 | 34 / +1V8_FPGA | HIGH | same error at `cntrt.xdc:92` |

### 3.2 Ports with no board counterpart (UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION)

| Ports | Bits | Reason |
|---|---|---|
| `dac_clk` | 1 | RTL forwards `clk_120m` to a pin (`dac_interface_single.v:23`); the board clocks the AD9708 from AD9523 OUT10 via SMA J20 (`main.cpp:1019-1020`); no FPGA net |
| `ft601_clk_in`, `ft601_data[31:0]`, `ft601_be[1:0]`, `ft601_txe_n`, `ft601_rxf_n`, `ft601_txe`, `ft601_rxf`, `ft601_wr_n`, `ft601_rd_n`, `ft601_oe_n`, `ft601_siwu_n`, `ft601_srb[1:0]`, `ft601_swb[1:0]`, `ft601_clk_out` | 49 | FT601Q-B-T (U6) is placed on the schematic with 0 of 77 pins connected; decoupling parts parked outside the outline; no FPGA pin carries a USB net. The RTL's USB 3.0 path has no hardware |
| `current_elevation[5:0]`, `current_azimuth[5:0]`, `current_chirp[5:0]`, `new_chirp_frame` | 19 | no status nets on the schematic |
| `dbg_doppler_data[31:0]`, `dbg_doppler_valid`, `dbg_doppler_bin[4:0]`, `dbg_range_bin[5:0]`, `system_status[3:0]` | 48 | debug outputs; no nets |

Schematic FPGA nets with no RTL port: `ADC_OR_P/N` (M6/N6, over-range), `FPGA_ADC_CLOCK_P/N` (N11/N12, 400 MHz LVDS from AD9523 OUT5 — the RTL uses the ADC DCO instead), `FPGA_CLOCK_TEST` (H14, 20 MHz test clock), `DIG_5..7` (H11/G12/H12, STM32 PD13..PD15 configured as inputs), QSPI flash `FPGA_FLASH_*` (bank 14, MT25QL01G), JTAG.

### 3.3 Other constraint defects in `cntrt.xdc`

| Line(s) | Defect | Fix |
|---|---|---|
| 4-5 | `[XC7A100T]`, `[DATE]` placeholders | set real part in the Vivado project (not in XDC) |
| 33-295 | 140 `PACKAGE_PIN [PIN_NUMBER*]` | replace with the schematic-derived file after designer verification |
| 283, 287, 290 | `# ... (continue for all N bits)` — 37 debug bits never listed | remove debug ports from the top or leave unconstrained (`-quiet`) |
| 85, 92 | LVCMOS33 on bank-34 (1.8 V) signals | LVCMOS18 |
| 160-167 | LVDS_25 + DIFF_TERM on a 3.3 V bank | designer decision: change bank VCCO to 2.5 V, or use external 100 Ω termination with `DIFF_TERM FALSE` (per UG471), or move pins |
| 14-27 | four unrelated clocks, no `set_clock_groups -asynchronous` | add clock groups; without it Vivado times every cross-domain path |
| 309-310 | multicycle path between asynchronous clocks `clk_100m` -> `ft601_clk_in` | remove (meaningless once clock groups are asynchronous) |
| — | no constraint for the flop-derived internal 400 MHz clock (section 7) | design change required, not a constraint |
| 320-321 | `PACKAGE_PIN_BANK` is not a Vivado property | delete |
| — | no `CONFIG_VOLTAGE` / `CFGBVS` | add `set_property CFGBVS VCCO` / `CONFIG_VOLTAGE 3.3` (bank 0 VCCO is +3V3_FPGA on the schematic; CFGBVS pulled via 4.7 kΩ to N$114 — verify the pull direction before setting) |

---

## 4. Static verification actually performed (results, not claims)

Tools: Icarus Verilog 13.0, Verilator 5.052 (`/opt/homebrew/bin`), installed 2026-10-08. Vivado, yosys, xvlog: not installed. Script: `tools/fpga_lint.sh` (logs under `build/lint/` or `$LOG_DIR`).

| Run | Command (abridged) | Exit | Result |
|---|---|---|---|
| A | `iverilog -g2012 -s radar_system_top` on all `.v` except testbench, including `chirp_lut_init.v` | 2 | `chirp_lut_init.v:6: syntax error` (`initial` outside a module) |
| B | same without `chirp_lut_init.v` | 2 | `radar_system_top.v:312: syntax error / Syntax in assignment statement l-value` |
| C | run B + `-I 9_Firmware/9_2_FPGA` | 2 | identical (never reaches `$readmemh`) |
| D | `iverilog -g2012 -s radar_system_tb` | 20 | 18 SVA syntax errors `radar_system_tb.v:528-543` + error B |
| lint | `verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top` | 1 | `radar_system_top.v:312:13: syntax error, unexpected wire`; 23 EOFNEWLINE |
| E–J (scratch copy only, repo untouched) | after hoisting the `wire` at :312, `wire`→`reg` at :155-156, removing `.ref_i/.ref_q`, and stubbing the missing modules | 10/11 | iverilog: "modules were missing: BUFG, IBUFDS, ad9484_lvds_to_cmos_400m, matched_filter_processing_chain, range_bin_decimator, xfft_32"; then use-before-declare errors `ddc_400m.v:252-266`, `radar_receiver_final.v:150`, `radar_system_tb.v:329`. Verilator with stubs: 0 errors, 207 warnings (14 UNDRIVEN, 4 MULTIDRIVEN, 5 MULTIDRIVENPROC, 18 PINMISSING, 17 WIDTHTRUNC, 1 CASEINCOMPLETE, ...) |
| sim | `vvp` | not run | no executable could be produced |

**No simulation or synthesis test PASSED.** All results above are FAIL or informational.

---

## 5. Procedures

### FPGA-T01 — Resolve the device part

- **Purpose:** choose the Vivado part string from verified evidence.
- **Prerequisites:** access to the hardware designer or to a physical Main Board.
- **Required input files:** `RADAR_Main_Board.sch` (U42), `cntrt.xdc:4`, `README.md:52`.
- **Software:** none (or Vivado for `get_parts`).
- **Procedure:** (1) read the marking on the physical FPGA if a board exists; (2) otherwise take the CAD part XC7A50T-2FTG256I; (3) record the decision with its evidence in `docs/04_RECOVERY_TASKS.md` (R-FPGA-01); (4) if XC7A100T is intended, confirm in AMD DS180 Table 2 that the chosen package exists for it and raise a PCB change request. Parameters known: package FTG256, speed −2, temperature I (from CAD). Parameters requiring verification: actual mounted device.
- **Expected output:** one line in `tools/vivado/create_project.tcl` invocation, e.g. `-tclargs xc7a50tftg256-2`.
- **Verification:** `vivado -mode tcl` → `get_parts xc7a50tftg256-2` returns the part.
- **Troubleshooting:** if the resource report later shows > 100 % utilisation, the 50T is too small; that is a design, not a constraint, problem.
- **Completion criteria:** part string recorded with evidence; README/docs/XDC comment corrected in a reviewed change.

### FPGA-T02 — Create the Vivado project

- **Purpose:** obtain Vivado elaboration messages on the real tool.
- **Prerequisites:** FPGA-T01; Vivado 2020.2 or newer (version not evidenced in repo; the IP names `xfft_32`/`FFT_enhanced` are user instance names, so any Vivado with FFT IP v9.1 should regenerate them).
- **Required input files:** all `9_Firmware/9_2_FPGA/*.v` except `radar_system_tb.v` (simulation set) and `chirp_lut_init.v` (not a module); `*.mem`; `cntrt.xdc` (timing section only) and `reconstructed/radar_system_top_schematic_derived.xdc`.
- **Software and version:** AMD Vivado (any 2020.2+ ML Standard edition; Artix-7 is in the free device list).
- **Procedure:**
  1. Open a shell at the repository root.
  2. Run `vivado -mode batch -source tools/vivado/create_project.tcl -tclargs xc7a50tftg256-2` (part from FPGA-T01). The script adds the source set, the `.mem` files as Memory Files, the two XDC files, and the testbench to `sim_1`; it writes `build/vivado/aeris10/aeris10.xpr`.
  3. Open the project in the GUI: `vivado build/vivado/aeris10/aeris10.xpr`.
  4. Flow Navigator → *RTL Analysis → Open Elaborated Design*. Collect the Messages window content (File → Export → Export Messages) into `build/vivado/elab_messages.txt`.
- **Parameters known:** source list (verified by `tools/fpga_lint.sh`), top `radar_system_top`. **Parameters requiring verification:** part; every PACKAGE_PIN (section 3.1 caveat).
- **Expected output:** `.xpr` and an elaboration log that reproduces section 4 errors (`[Synth 8-xxxx]` on `radar_system_top.v:312`, missing modules).
- **Verification:** the log lists exactly the six missing modules of section 2.3 and no others.
- **Troubleshooting:** "file not found" for `.mem` → Vivado resolves `$readmemh` relative to the project; override the ten file-name parameters of `chirp_memory_loader_param` at `radar_receiver_final.v:144` with repository-relative names (a source edit that must be reviewed, see FPGA-T04).
- **Completion criteria:** `.xpr` exists and elaboration messages are archived.

### FPGA-T03 — Fix the syntax and declaration-order defects (reviewed RTL edits)

- **Purpose:** make the RTL parse.
- **Prerequisites:** FPGA-T02 or `tools/fpga_lint.sh`.
- **Required input files:** `radar_system_top.v`, `radar_receiver_final.v`, `ddc_400m.v`, `radar_system_tb.v`.
- **Procedure (each edit is a design change; commit separately with review):**
  1. `radar_system_top.v:312-313`: move `wire [16:0] mag = ...` to module scope as `wire [16:0] mag = (...)`, or compute inside the block into a `reg`.
  2. `radar_system_top.v:155-156`: `wire rx_cfar_detection, rx_cfar_valid` → `reg` (they are assigned at :304-318).
  3. `radar_receiver_final.v:216-217`: delete `.ref_i(16'd0)`, `.ref_q(16'd0)` (ports do not exist in `matched_filter_multi_segment.v:3-39`) **or** add the intended ports to the module — designer decision.
  4. `ddc_400m.v`: move declarations at :272-275 above first use at :252.
  5. `radar_receiver_final.v`: move declaration at :192 above :150.
  6. `radar_system_tb.v`: move `sin_lut` declaration (:343) above :329.
- **Expected output:** `tools/fpga_lint.sh` iverilog run stops only on missing modules.
- **Verification:** `LOG_DIR=build/lint tools/fpga_lint.sh`; `grep -c "missing" build/lint/iverilog_top.log` ≥ 1 and no "syntax error".
- **Troubleshooting:** verilator `MULTIDRIVEN` warnings remain — those are section 7 design defects, out of scope for this task.
- **Completion criteria:** no syntax errors from either tool.

### FPGA-T04 — Recover or re-implement the missing modules and IP

- **Purpose:** complete the hierarchy.
- **Prerequisites:** FPGA-T03.
- **Required inputs from the designer:** the original ISE/Vivado project (`PLFM_RADAR_Xilinx_ISE_V2`), or the RTL of `ad9484_lvds_to_cmos_400m`, `range_bin_decimator`, `matched_filter_processing_chain`; FFT IP settings.
- **Procedure if the originals are unavailable:**
  1. FFT IP: Vivado IP Catalog → *Fast Fourier Transform* (v9.1). Create instance `FFT_enhanced`: 1 channel, transform length 1024, architecture Pipelined Streaming I/O, data width 16, phase factor width 16, scaled fixed-point (config word width must come out as 16 bits to match `fft_1024_forward.v:102-122`; adjust scaling-schedule options until `s_axis_config_tdata` is `[15:0]`), runtime-configurable transform direction. Create instance `xfft_32`: length 32, data width 16, config word `[7:0]` (`doppler_processor.v:283-296`). Record the resulting `.xci` files under `9_Firmware/9_2_FPGA/ip/` (directory to be created; does not exist yet). **All IP parameters beyond the port widths are UNVERIFIED assumptions.**
  2. `ad9484_lvds_to_cmos_400m`: wrap `ad9484_interface_400m.v` (IBUFDS/IDDR) behind the inferred port list, after resolving whether the AD9484 LVDS output is DDR at 200 MHz bit clock (AD9484 datasheet `7_Components Datasheets and Application notes/AD9484/AD9484.pdf`, "LVDS DDR output" — REQUIRES VERIFICATION) and replacing the flop-derived clock of `lvds_to_cmos_400m.v:35-43` with a proper BUFIO/BUFR or MMCM structure.
  3. `matched_filter_processing_chain`: compose the orphans `fft_1024_forward_enhanced` → `frequency_matched_filter` → `fft_1024_inverse_enhanced`; the reference-memory semantics (time vs frequency domain, `frequency_matched_filter.v:13`) must be confirmed with the `.mem` generator (missing).
  4. `range_bin_decimator`: new module per the inferred interface (peak-detect mode `decimation_mode=2'b01`).
  5. Add `long_chirp_seg3_{i,q}.mem` (or set `LONG_SEGMENTS=3` in `matched_filter_multi_segment.v:52` if 3072 samples cover the 3000-sample chirp — designer decision) and replace the Windows paths at `chirp_memory_loader_param.v:3-12` with project-relative names.
- **Expected output:** iverilog elaboration (with UNISIM models) succeeds; Vivado elaborated design opens.
- **Verification:** `tools/fpga_lint.sh` exit 0 when run with `-y $XILINX_VIVADO/data/verilog/src/unisims` added (edit the script's iverilog line or set `IVERILOG_EXTRA`).
- **Completion criteria:** zero missing modules; every `.xci` committed.

### FPGA-T05 — Simulation

- **Purpose:** run `radar_system_tb`.
- **Prerequisites:** FPGA-T04.
- **Software:** Vivado xsim (supports the SVA properties at `radar_system_tb.v:528-543`; Icarus does not).
- **Procedure:** in the project, Flow → *Run Simulation → Run Behavioral Simulation*; set simulation run time ≥ 500 µs (`radar_system_tb.v:149-162`); the TB generates 64 chirp toggles at 3 µs spacing (:230-254) which is shorter than the 167 µs chirp-plus-listen period of `plfm_chirp_controller.v:41-42` — adjust the stimulus or expect overlapping chirps. Disable `$dumpvars(0, ...)` (:549-557) or restrict depth; a full dump at 400 MHz for 500 µs is multi-GB.
- **Expected output:** console counts summary (:495-521).
- **Verification:** the TB has no pass/fail gating; a PASS can only be declared after adding `$fatal` on assertion failure and a scoreboard — this is new verification work.
- **Completion criteria:** assertions execute without error and the Doppler output monitor (:481-489) reports non-zero valid samples.

### FPGA-T06 — Synthesis and implementation report inspection

- **Purpose:** quantify resources and timing on the real part.
- **Prerequisites:** FPGA-T04, verified XDC.
- **Procedure:** `launch_runs synth_1 -jobs 4; wait_on_run synth_1; open_run synth_1; report_utilization -file build/vivado/util.rpt; report_timing_summary -file build/vivado/timing.rpt; report_clock_interaction -file build/vivado/clkint.rpt; report_cdc -file build/vivado/cdc.rpt`. Then `launch_runs impl_1 -to_step write_bitstream`.
- **What to look for:** utilisation > 100 % on DSP (FIR = 64 DSP48E1 for two instances, `fir_lowpass.v:50-73`; 50T has 120) or on slice registers (matched-filter arrays ≈ 32 768 FFs, `matched_filter_multi_segment.v:60-61,329-332`); WNS < 0 on any 400 MHz path (CIC integrators `cic_decimator_4x_enhanced.v:94-137`); `report_cdc` critical entries on `cdc_adc_to_processing`; `report_clock_interaction` showing "unsafe" between the four external clocks.
- **Completion criteria:** `write_bitstream` completes; reports archived; all CRITICAL WARNINGs dispositioned in writing.

### FPGA-T07 — Prerequisites for bitstream generation (checklist)

1. Part confirmed (FPGA-T01).
2. All 180 port bits either constrained to designer-verified balls or removed from the top (section 3.2 ports).
3. Bank voltage legality: bank 14 LVDS inputs vs 3.3 V VCCO resolved; bank 34 LVCMOS18.
4. Missing modules/IP recovered (FPGA-T04).
5. Clock architecture decided: is `clk_100m` phase-locked to ADC DCO/4? (`cdc_adc_to_processing` drops/duplicates samples otherwise; `ddc_400m.v:243-267`).
6. Multi-driven registers removed (`plfm_chirp_controller.v` `chirp_counter`; `usb_data_interface.v` `ft601_clk_out`; CIC monitors).
7. USB path decided: the FT601 does not exist on the board; either wire it (PCB change) or remove `usb_data_interface` and route data through the STM32 (which has no high-speed path to the FPGA — only `DIG_0..7` GPIO and SPI1).
8. `CFGBVS`/`CONFIG_VOLTAGE` set; configuration mode (M0..M2 pull resistors R138-R140 on the schematic — values define master SPI from MT25QL01G; verify).
9. Timing closure (FPGA-T06).

---

## 6. Clock architecture (RTL evidence vs board evidence)

| Clock | RTL (XDC) | Board / firmware |
|---|---|---|
| `clk_100m` 100 MHz | external pin, BUFG `radar_system_top.v:174` | AD9523 OUT6 "FPGA_SYSTEM_CLOCK" /36 = 100 MHz LVCMOS (`main.cpp:995-996`) → SMA J1 → FPGA E12 |
| `clk_120m_dac` 120 MHz | external pin, BUFG :179; also forwarded to `dac_clk` pin | AD9523 OUT11 "FPGA_DAC" /30 = 120 MHz (`main.cpp:1025-1026`) → FPGA C13; the DAC itself gets OUT10 via SMA J20 |
| `ft601_clk_in` 100 MHz | external pin from FT601 | FT601 unconnected — clock does not exist |
| `adc_dco_p/n` 400 MHz | IBUFDS → BUFG → flop (`lvds_to_cmos_400m.v:17-43`) | AD9484 DCO → N14/P14; AD9523 OUT4 clocks the ADC at 400 MHz (`main.cpp:983-984`); OUT5 "FPGA_ADC" 400 MHz LVDS → N11/N12 (unused by RTL) |
| internal `clk_400m` | flop output used as a clock for NCO/mixer/CIC | not a real clock; design defect |

Absent in RTL: any MMCM/PLL (`grep MMCME2|PLLE2|clk_wiz` → none). Absent in XDC: `set_clock_groups`.

---

## 7. Design defects that block synthesis or function (evidence)

| # | Defect | Evidence |
|---|---|---|
| 1 | 400 MHz capture not implemented; internal clock is a flop re-sampling its own clock | `lvds_to_cmos_400m.v:35-43`; consumers `radar_receiver_final.v:99,115` |
| 2 | `chirp_counter` written from two clock domains | `plfm_chirp_controller.v:564-576` (clk_100m) and `:683-784` (clk_120m) |
| 3 | `ft601_clk_out` written from two always blocks on different clocks | `usb_data_interface.v:65-79`, `:176-182` |
| 4 | CIC monitor registers written from three always blocks, one clocked by the floating input `reset_monitors` | `cic_decimator_4x_enhanced.v:71,181,291`; left unconnected at `ddc_400m.v:223-240` |
| 5 | Async-reset block with data-dependent reset condition | `ddc_400m.v:117-125` |
| 6 | Receiver control inputs undriven → matched filter never starts; `range_bin` never assigned | `radar_receiver_final.v:17,21-22,206-208` |
| 7 | STM32 SPI pass-through outputs undriven (level shifter never instantiated) → ADAR1000 SPI cannot work through the FPGA | `radar_transmitter.v:59-71`; `level_shifter_interface.v:10` orphan |
| 8 | Unsynchronised cross-domain sampling of `range_profile`, `doppler_*`, `cfar_*` in the FT601 domain | `usb_data_interface.v:84,106-109,124-132,147-150` |
| 9 | CFAR is a fixed threshold `mag > 17'd10000`; range profile output is the Doppler data "as a placeholder" | `radar_system_top.v:298-331` |
| 10 | Two conflicting TX LUT value sets | `plfm_chirp_controller.v:99-560` vs `chirp_lut_init.v:7` (e.g. index 1: 237 vs 128) |
| 11 | Asynchronous BRAM read prevents block-RAM inference of the 4096x32 latency buffer | `latency_buffer_2159.v:102` |
| 12 | FT601 interface definition inconsistent with the FT601 datasheet (TXE_N/RXF_N are device outputs; BE is 4 bits in 32-bit mode) | `radar_system_top.v:79-94`, `usb_data_interface.v:16-35` — REQUIRES VERIFICATION against `7_Components Datasheets` (no FT601 datasheet present) |

---

## 8. Information required from the hardware designer

1. Confirmed FPGA part (CAD: XC7A50T-2FTG256I).
2. Confirmation of every ball in `reconstructed/PIN_MAP_FROM_SCHEMATIC.md` against the AMD package file and the final routed board.
3. Bank 14 VCCO decision for the LVDS inputs (2.5 V or external termination).
4. The original ISE/Vivado project, the four missing RTL modules, the two FFT IP configurations, `long_chirp_seg3_*.mem`, and the `.mem`/LUT generator script (which TX LUT set is authoritative).
5. Clocking intent: is `clk_100m` phase-locked to DCO/4; AD9484 output mode (DDR/SDR) and bit-clock rate.
6. The intended host data path (FT601 is not wired; STM32 has only USB FS).

---

## 9. Generated artefacts (this reconstruction)

| Path | Content | Status |
|---|---|---|
| `9_Firmware/9_2_FPGA/reconstructed/radar_system_top_schematic_derived.xdc` | 64 ports / 100 bits with PACKAGE_PIN + IOSTANDARD from schematic banks; unresolved ports listed as comments | REQUIRES VALIDATION (not hardware-verified) |
| `9_Firmware/9_2_FPGA/reconstructed/PIN_MAP_FROM_SCHEMATIC.md` | mapping table with confidence and notes | REQUIRES VALIDATION |
| `tools/check_fpga_constraints.py` | placeholder / coverage checker | executed, exit 1 (expected) |
| `tools/extract_eagle_netlist.py`, `tools/gen_xdc_from_schematic.py` | netlist extraction and XDC generation | executed |
| `tools/fpga_lint.sh` | iverilog/verilator wrapper | executed, FAIL (expected) |
| `tools/vivado/create_project.tcl` | project creation (part mandatory) | NOT executed (no Vivado on this machine) |
