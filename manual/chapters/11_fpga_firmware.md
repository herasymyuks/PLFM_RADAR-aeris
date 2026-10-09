# FPGA design — module hierarchy, build, constraints, tests, synthesis status

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** the original RTL (`9_Firmware/9_2_FPGA/`, ORIGINAL PROJECT FILE) does not elaborate; the BETA project `beta/fpga/` parses, lints and simulates with open-source tools (BETA: 0 build failures, 9 testbench runs PASS), is **not synthesised with Vivado**, has no timing closure, has not been loaded on hardware, and its two Xilinx FFT IP cores are not generated. An open-source Yosys/nextpnr estimate exists (`beta/fpga_synth/`, OPEN-SOURCE ESTIMATE, not a Vivado result; placement did not complete). Figures: F11.1 original hierarchy SOURCE-DERIVED; F11.1b BETA hierarchy SOURCE-DERIVED / BETA (regenerated for this manual); F11.2 original pipeline PARTIAL.

**Sources:** `beta/fpga/README.md`, `beta/fpga/CHANGELOG.md`, `beta/fpga/ip/README.md`, `beta/fpga/constraints/radar_system_top_beta.xdc`, `beta/fpga_synth/README.md`, `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md`, `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.md`, `manual/figures/fpga_beta/fpga_module_hierarchy.md` (generated), `tools/check_fpga_constraints.py` (executed).

**Planned figures:** F11.1 module hierarchy (SD-01, original), F11.1b module hierarchy of `beta/fpga/rtl`, F11.2 signal-processing pipeline (SD-02).

## 1. Starting point — the original RTL as committed

Bottom line of the reconstruction (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md`, header): "the FPGA sources cannot be elaborated by any tool today. Before a Vivado project can even reach synthesis, four user modules and two Xilinx FFT IP configurations must be recovered, three syntax/declaration defects must be fixed, and the device part number must be confirmed (schematic says XC7A50T-2FTG256I; README/XDC say XC7A100T). Pin assignment can be reconstructed for 64 of 67 top-level ports from the Main Board schematic, but 25 ports (FT601 USB 3.0, status and debug outputs) have no board counterpart because the FT601 was never wired."

Device identification (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §1, copied verbatim):

| Source | Device statement | Evidence |
|---|---|---|
| Main Board schematic | **XC7A50T-2FTG256I**, package `BGA256C100P16X16_1700X1700X155` | `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` part `U42`, library/deviceset `XC7A50T-2FTG256I` |
| Power budget workbook | `XC7A50T-2FTG256` | `3_Power Management/Power Management V6.xlsx` (sharedStrings entry 25) |
| Block diagram | `XC7A50T-2FTG256` | `2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio` |
| Constraint file | `# Device: [XC7A100T]` (placeholder brackets, no package, no speed grade) | `cntrt.xdc:4` |
| README / hardware docs | "XC7A100T FPGA" | `README.md:52`; `02_hardware/05_fpga_board.md:1,15,30,34,262` |

The source concludes that the only CAD evidence is XC7A50T-2FTG256I (Vivado part string `xc7a50tftg256-2`); whether the design fits a 50T (52 160 logic cells, 120 DSP48E1, 2 700 Kbit BRAM per AMD DS180) is UNRESOLVED until a real synthesis run (conflict K1).

![F11.1 — FPGA RTL module hierarchy of the original 9_Firmware/9_2_FPGA (SD-01): 19 defined, 5 missing, 3 primitives, 9 unused — SOURCE-DERIVED, lexical scan not elaboration (source: engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.dot; produced by tools/gen_verilog_hierarchy.py and Graphviz dot)](engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.png)

Hierarchy counts of the original (source: `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.md`): 26 Verilog files parsed; DEFINED 19, MISSING 5 (`FFT_enhanced`, `xfft_32` — Xilinx IP without `.xci`; `ad9484_lvds_to_cmos_400m`, `matched_filter_processing_chain`, `range_bin_decimator` — RTL never committed), PRIMITIVE 3 (BUFG, IBUFDS, IDDR), UNUSED 9 (`ad9484_interface_400m`, `cdc_handshake`, `cdc_single_bit`, `fft_1024_forward_enhanced`, `fft_1024_inverse_enhanced`, `frequency_matched_filter`, `level_shifter_interface`, `usb_packet_analyzer`, the testbench root).

Static verification actually performed on the original (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §4, copied verbatim; tools Icarus Verilog 13.0, Verilator 5.052):

| Run | Command (abridged) | Exit | Result |
|---|---|---|---|
| A | `iverilog -g2012 -s radar_system_top` on all `.v` except testbench, including `chirp_lut_init.v` | 2 | `chirp_lut_init.v:6: syntax error` (`initial` outside a module) |
| B | same without `chirp_lut_init.v` | 2 | `radar_system_top.v:312: syntax error / Syntax in assignment statement l-value` |
| C | run B + `-I 9_Firmware/9_2_FPGA` | 2 | identical (never reaches `$readmemh`) |
| D | `iverilog -g2012 -s radar_system_tb` | 20 | 18 SVA syntax errors `radar_system_tb.v:528-543` + error B |
| lint | `verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top` | 1 | `radar_system_top.v:312:13: syntax error, unexpected wire`; 23 EOFNEWLINE |
| E–J (scratch copy only, repo untouched) | after hoisting the `wire` at :312, `wire`→`reg` at :155-156, removing `.ref_i/.ref_q`, and stubbing the missing modules | 10/11 | iverilog: "modules were missing: BUFG, IBUFDS, ad9484_lvds_to_cmos_400m, matched_filter_processing_chain, range_bin_decimator, xfft_32"; then use-before-declare errors `ddc_400m.v:252-266`, `radar_receiver_final.v:150`, `radar_system_tb.v:329`. Verilator with stubs: 0 errors, 207 warnings |
| sim | `vvp` | not run | no executable could be produced |

"No simulation or synthesis test PASSED. All results above are FAIL or informational." (source: same). Top-level ports with no board counterpart (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §3.2, copied verbatim):

| Ports | Bits | Reason |
|---|---|---|
| `dac_clk` | 1 | RTL forwards `clk_120m` to a pin (`dac_interface_single.v:23`); the board clocks the AD9708 from AD9523 OUT10 via SMA J20 (`main.cpp:1019-1020`); no FPGA net |
| `ft601_clk_in`, `ft601_data[31:0]`, `ft601_be[1:0]`, `ft601_txe_n`, `ft601_rxf_n`, `ft601_txe`, `ft601_rxf`, `ft601_wr_n`, `ft601_rd_n`, `ft601_oe_n`, `ft601_siwu_n`, `ft601_srb[1:0]`, `ft601_swb[1:0]`, `ft601_clk_out` | 49 | FT601Q-B-T (U6) is placed on the schematic with 0 of 77 pins connected; decoupling parts parked outside the outline; no FPGA pin carries a USB net. The RTL's USB 3.0 path has no hardware |
| `current_elevation[5:0]`, `current_azimuth[5:0]`, `current_chirp[5:0]`, `new_chirp_frame` | 19 | no status nets on the schematic |
| `dbg_doppler_data[31:0]`, `dbg_doppler_valid`, `dbg_doppler_bin[4:0]`, `dbg_range_bin[5:0]`, `system_status[3:0]` | 48 | debug outputs; no nets |

Schematic FPGA nets with no RTL port: `ADC_OR_P/N` (M6/N6, over-range), `FPGA_ADC_CLOCK_P/N` (N11/N12, 400 MHz LVDS from AD9523 OUT5 — the RTL uses the ADC DCO instead), `FPGA_CLOCK_TEST` (H14, 20 MHz test clock), `DIG_5..7` (H11/G12/H12, STM32 PD13..PD15 configured as inputs), QSPI flash `FPGA_FLASH_*` (bank 14, MT25QL01G), JTAG (source: same §3.2). The original `cntrt.xdc` has 140 `PACKAGE_PIN [PIN_NUMBER*]` placeholders, LVCMOS33 on 1.8 V bank-34 signals, LVDS_25 + DIFF_TERM on a 3.3 V bank, no `set_clock_groups`, and no `CONFIG_VOLTAGE`/`CFGBVS` (source: same §3.3). The pipeline as written is drawn in F11.2 (chapter 2 §5.1 lists the stage-by-stage findings).

![F11.2 — FPGA signal-processing pipeline as written in the original RTL (SD-02) — PARTIAL; 5 instantiated-but-missing modules, placeholders and undriven controls marked (source: engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.png)

## 2. The BETA project `beta/fpga/`

Status (source: `beta/fpga/README.md`, header): everything in the directory parses, elaborates, lints and simulates with open-source tools (Icarus Verilog 13.0, Verilator 5.052, Python 3 / numpy); it has **not been synthesised** (no Vivado on the authoring machine), has **no timing closure**, has **not been loaded on hardware**, and the two Xilinx FFT IP cores it needs have **not been generated**. Nothing under `9_Firmware/9_2_FPGA/` was modified; every difference is listed in `CHANGELOG.md` with original file:line references.

Directory (source: `beta/fpga/README.md`, "Directory"):

| Path | Content |
|---|---|
| `build.sh` | open-source flow (exit code = number of failures) |
| `gen_chirp_mem.py` | verifies the `.mem` formula, writes the missing seg3 files |
| `CHANGELOG.md` | every change vs. `9_Firmware/9_2_FPGA`, file:line + reason |
| `rtl/` | synthesisable Verilog-2001 (34 files; incl. host-link option B and the ISERDES capture path); `rtl/sim/unisim_sim_models.v` BUFG/IBUFDS/IDDR stand-ins (simulation + lint only); `rtl/unused_orig/` 5 untouched originals no longer compiled (+README) |
| `mem/` | 8 original `.mem` copies + generated `long_chirp_seg3_{i,q}.mem` |
| `tb/` | 8 self-checking testbenches (9 runs), `gen_vectors.py`, `vectors/`, original TB (reference) |
| `constraints/radar_system_top_beta.xdc` | constraints (section 7) |
| `vivado/create_project.tcl`, `vivado/build.tcl` | Vivado scripts — NOT executed |
| `ip/README.md` | exact FFT IP settings (xfft v9.1) derived from the port usage (section 9) |
| `logs/` | output of the last `build.sh` run (iverilog, verilator, vvp logs) |

How to run (source: `beta/fpga/README.md`, "How to run"): `cd beta/fpga && ./build.sh` (~2 min; `SKIP_SYSTEM=1` skips the long system test; `VERBOSE=1` prints sim output). `build.sh` runs, in order: iverilog elaboration (simulation view `-DSIM` and synthesis view), `verilator --lint-only -Wall` on both views, `gen_chirp_mem.py`, `tb/gen_vectors.py`, and every `tb/tb_*.v` with `vvp`. A testbench passes only if it exits 0 and prints `PASS` and never `FAIL`. The RTL's `$readmemh` paths are `mem/...` relative to `beta/fpga`.

### 2.1 Module hierarchy of the BETA RTL

![F11.1b — FPGA RTL module hierarchy of beta/fpga/rtl: 43 defined, 2 missing (the deliberate FFT IP placeholders), 0 primitives (UNISIM stand-ins are defined in rtl/sim), 8 unused — SOURCE-DERIVED from the BETA sources, lexical scan not elaboration (source: beta/fpga/rtl via tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl --out manual/figures/fpga_beta; produced by dot -Tpng -Gdpi=110)](manual/figures/fpga_beta/fpga_module_hierarchy.png)

Regenerated for this manual with `python3 tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl --out manual/figures/fpga_beta` (40 Verilog files, all parsed; script exit code 1 because the two IP placeholders `FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README` and `XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README` are instantiated but undefined — the intended fail-loud behaviour) and `dot -Tpng -Gdpi=110 -o manual/figures/fpga_beta/fpga_module_hierarchy.png manual/figures/fpga_beta/fpga_module_hierarchy.dot` (source: `manual/figures/fpga_beta/fpga_module_hierarchy.md`, generated 2026-10-09: DEFINED 43, MISSING 2, PRIMITIVE 0, UNUSED 8).

## 3. Executed build and test results

Last run 2026-10-09, after command set v2 + blind calibration; logs in `beta/fpga/logs/` (source: `beta/fpga/README.md`, "What passed", copied verbatim):

| Step | Command (from `build.sh`) | Result | Log |
|---|---|---|---|
| 1 | `iverilog -g2005 -DSIM -s radar_system_top rtl/*.v rtl/sim/unisim_sim_models.v` | PASS | `logs/iverilog_top_sim.log` |
| 2 | `iverilog -g2005 -s radar_system_top ...` (synthesis view) | PASS | `logs/iverilog_top_synth.log` |
| 3a | `verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top ...` (synth view) | PASS, **0 %Error, 165 %Warning** (unchanged) | `logs/verilator_synth.log` |
| 3b | same with `-DSIM` | PASS, **0 %Error, 159 %Warning** | `logs/verilator_sim.log` |
| 4 | `python3 gen_chirp_mem.py` | PASS: seg0/1/2 reproduced within 1 LSB, seg3 written | `logs/gen_chirp_mem.log` |
| 5 | `python3 tb/gen_vectors.py` | PASS | `logs/gen_vectors.log` |
| 6a | `tb_fft_wrappers` - xfft_32 (4 frames incl. back-pressure) and FFT_enhanced (fwd + inv) vs numpy | PASS: 2176 samples within +/-2 LSB | `logs/tb_fft_wrappers.run.log` |
| 6b | `tb_matched_filter` - chain + memory, reference chirp delayed 300 samples | PASS: peak at bin 302 (300 +/-4), peak/sidelobe 4.76 | `logs/tb_matched_filter.run.log` |
| 6c | `tb_range_bin_decimator` - 2 x 1024 bins (one with input gaps) vs numpy, peak mode | PASS: 128/128 bins | `logs/tb_range_bin_decimator.run.log` |
| 6d | `tb_system_smoke` - full top, 10 chirps, synthetic IF echoes, 3.3 ms (see 6i for the two capture modes) | PASS (~65 s each): see below | `logs/tb_system_smoke_mode1.run.log` |
| 6e | `tb_host_bridge` - HOST_LINK unit test (packer + SPI slave): 3 detections, 32 detections (det_wr regression), command set v2 against a 4-word register model | PASS: 2075- and 2162-byte frames, CRC ok; v2 write/read-back/status/unknown ok | `logs/tb_host_bridge.run.log` |
| 6f | `tb_host_bridge_top` - option B bridge through the top: v2 register commands (CFAR_THR 10000 -> 150 written over SPI, 5 read-backs, 0x04 status before/with/after a frame, 0xEE), then the SPI master reads one 64x32 frame after DRDY | PASS (~77 s): 2162-byte frame, 32 detections (only possible because the threshold write took effect), sync/dims/az-el/chirp-count/map/CRC ok, ADAR pass-through gated | `logs/tb_host_bridge_top.run.log` |
| 6g | `tb_adc_iserdes_capture` - ISERDES capture + IDELAY calibration (pattern and blind) + FIFO | PASS (~30 s): pattern method 8/8 lanes locked, centre tap 13, skewed lane 5 -> 5 (8 taps = 0.6 ns compensated), bitslip detected/realigned, 4000 samples exact; blind method on a 120 MHz tone + 0.7 LSB rms noise with lane 2 parked on a metastable tap and lane 0 mis-framed: 8/8 lanes locked, every lane within **+/-0 taps** of the pattern centre, framing restored, 4000 tone samples exact | `logs/tb_adc_iserdes_capture.run.log` |
| 6h | `tb_ddc_4x` - legacy 400 MHz DDC vs polyphase DDC, same input | PASS: 1855 outputs, max diff 0 LSB | `logs/tb_ddc_4x.run.log` |
| 6i | `tb_system_smoke` runs twice: `ADC_CAPTURE_MODE=1` (default) and `=0` | both PASS | `logs/tb_system_smoke_mode1.run.log`, `_mode0` |

`build.sh` summary line: `0 failure(s), 324 verilator warning line(s) (both views)` — 165 synth view + 159 sim view; 219 for the first beta, 241 after the host link, 324 after the ISERDES capture path, unchanged 324 after command set v2 + blind calibration (the only new lint findings were two BLKSEQ on block-local temporaries in the sim-only ISERDESE2 model, marked as intended) (source: `beta/fpga/README.md`).

System smoke test evidence (source: `beta/fpga/README.md`, `logs/tb_system_smoke.run.log`): DAC left mid-scale (57540 samples); 40 range profiles (4 segments × 10 chirps); for alternating echo delays of 100 and 420 baseband samples the segment-0 peak sat at decimated bin 8 and 28 on every chirp — a shift of 20 bins for a 320-sample delay change (320/16 = 20), i.e. pulse compression works end to end through capture → DDC → matched filter → decimator; 2048 Doppler outputs (one 64 × 32 frame); 2688 USB packets with 0 header/footer/sequence errors; no X on outputs; the matched-filter FSM was idle at every toggle.

Verilator warning breakdown (synthesis view, 165; source: `beta/fpga/README.md`): 59 PINCONNECTEMPTY (monitor/unused IP outputs left unconnected on purpose), 32 UNUSEDSIGNAL (diagnostic nets of the original, unused IP tready/tlast), 22 WIDTHTRUNC / 16 WIDTHEXPAND (original arithmetic widths, the copied host-link modules, the UNISIM models), 13 PROCASSINIT + 2 BLKSEQ + 1 ZERODLY (simulation-only UNISIM models in `rtl/sim/`), 9 DECLFILENAME (original file names differ from module names — kept so the docs stay valid), 7 UNUSEDPARAM, 3 GENUNNAMED (original `generate`), 1 CMPCONST (`host_bridge_spi`). None was hidden with a global `-Wno-*`.

Additional checks (source: `beta/fpga/README.md`; `tools/check_fpga_constraints.py` re-executed for this manual on 2026-10-09 with identical output): `tools/check_fpga_constraints.py --top beta/fpga/rtl/radar_system_top.v --xdc beta/fpga/constraints/radar_system_top_beta.xdc` → 0 placeholders, 0 invalid properties, 0 unknown port refs, 67/183 port bits constrained (the 116 unconstrained bits are exactly the UNRESOLVED ports of section 7); `tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl` → 0 missing RTL modules, the only "missing" names are the two deliberate IP placeholders.

## 4. Engineering findings recorded in the BETA (source: `beta/fpga/README.md`, "What was found and decided")

1. **The reference memories are frequency-domain matched-filter coefficients.** `long_chirp_seg{0,1,2}_{i,q}.mem` = `conj(FFT_1024(u_s)) · 31128/max`, where u is a unit-amplitude 10 → 30 MHz linear up-chirp, 3000 samples at 100 MSPS (phase fit residual 0.0018 rad; regenerated to within 1 LSB by `gen_chirp_mem.py`); segment 3 lies beyond the chirp and is all zeros — the missing file. Consequence: `matched_filter_processing_chain` is the frequency-domain chain the original architecture implies, and the reference is multiplied **without** the extra conjugation (`CONJUGATE_REF = 0`) — with the original conjugating form neither the numpy model nor the RTL produces a compression peak. Open point for the designer: the same data equals the FFT of a 30 → 10 MHz down-chirp, so the actual baseband chirp direction decides whether `CONJUGATE_REF` must be 0 or 1. `short_chirp_{i,q}.mem` (50 words) matches neither a time- nor a frequency-domain chirp and cannot be used — the short-chirp path is UNRESOLVED (see also chapter 2 §2.2 and observation MAN-02).
2. **AD9484 output is SDR LVDS at the sample rate** (datasheet: "LVDS SDR output", data captured on the rising edge of the DCO, tSKEW ±0.07 ns). The legacy capture module (mode 0) uses the DCO as a 400 MHz clock (IBUFDS → BUFG) and an IDDR as a dual-edge sampler taking the falling-edge sample by default (`CAPTURE_FALLING`); this assumption must be confirmed by Vivado timing analysis and an ADC test pattern on hardware.
3. **Reference alignment by address, not by delay line.** The chain requests reference bin k when FFT output bin k appears, so the fixed 3187-cycle `latency_buffer_2159` is not needed; works with the behavioural model (latency 160) and with any IP latency.
4. **Clock-domain crossings**: `cdc_adc_to_processing` (Gray-coded data words) replaced by Gray-pointer FIFOs; a reset synchroniser per non-100 MHz domain; STM32 toggles synchronised in the clock domain that consumes them (TX: 120 MHz FSM, RX: 100 MHz).
5. **Register map** (`radar_control_regs`): the receiver's control inputs that were floating wires now have one driver with documented reset defaults; its write/read port is driven by the SPI bridge (command set v2); 5-bit word addresses 0x00..0x10, 16-bit registers; table in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §7 (kept identical to the RTL; reproduced in chapter 9 §3.3).

## 5. ADC capture and DDC front end (`ADC_CAPTURE_MODE`, default 1)

Source: `beta/fpga/README.md`, "ADC capture and DDC front end", table copied verbatim:

| | mode 0 (legacy) | mode 1 (default) |
|---|---|---|
| Capture | `ad9484_lvds_to_cmos_400m`: IBUFDS -> BUFG (400 MHz global clock) -> IDDR as dual-edge sampler | `ad9484_iserdes_capture`: IBUFDS(DCO) -> BUFIO + BUFR/4; IDELAYE2 (VAR_LOAD) -> ISERDESE2 SDR 1:4 per lane; IDELAYCTRL on 200 MHz from `clk_gen` (MMCM); 32-bit `async_fifo` into clk_100m |
| DDC | `ddc_400m_enhanced`: NCO, mixer, 5-stage CIC at 400 MHz in fabric (timing closure unrealistic), FIFO, FIR | `ddc_4x_100m`: 4-phase NCO + 8 mixers + CIC as 16-tap FIR + the same FIRs, all at 100 MHz; **bit-exact** with the legacy path (`tb_ddc_4x`: max diff 0 LSB) |
| Calibration | none (`CAPTURE_FALLING` edge choice) | `adc_capture_calib`: default tap 16; manual tap/bitslip per lane; **pattern method** (CAL_CTRL bit4 = 0): auto IDELAY sweep with the ADC in a 2-code test pattern (register 0x0D = 0x48, P1/P2 = 0x19..0x1C = pattern A/B; or 0x04 checkerboard / 0x07 toggle), centre tap per lane, lane rotation alignment, lock/undetermined/align_fail status, pattern error counter; **blind method** (CAL_CTRL bit4 = 1, no ADC SPI needed): a CW tone at the IF on the live input, notch residual r[n] = x[n] - 2cos(w)x[n-1] + x[n-2] (CAL_BLIND_COEF = Q1.14 cos(w)), metric = sum of abs(r) over 512 words per tap, one lane swept at a time MSB first, pass = metric <= min + CAL_BLIND_MARGIN + min/16, longest linear run (1-tap holes closed), eye truncated at tap 0 extrapolated with the 32-taps-per-bit period, blind framing alignment (best of 4 framings per lane) before and after each of 2 passes; CAL_BLIND_MIN read-back (register map 0x4..0x10) |

Datasheet facts used (AD9484.pdf, re-checked): LVDS SDR, DCO at the sample rate (400 MHz), data valid on the rising DCO edge, tSKEW −0.07..+0.07 ns (tPD 0.85 / tCPD 0.6 ns typ), offset binary. Resource estimate for mode 1 (XC7A50T): 8 ISERDESE2 + 8 IDELAYE2 + 1 IDELAYCTRL (bank 14), 1 BUFIO + 1 BUFR, 1 MMCME2 (of 5) + 1 BUFG, 8 DSP48E1 for the mixers (9×16) + 64 DSP48E1 for the two unchanged 32-tap FIRs (of 120), CIC adder trees in LUTs (~16 constant multiplies per I/Q), 1 BRAM18 for the 32-bit FIFO (or distributed RAM), small ROM for the 65-entry sine table. The 400 MHz fabric path (mode 0) is kept only for comparison (source: same section).

Remaining risks / what to check in Vivado for mode 1 (source: same section):

- BUFR (DCO/4) versus clk_100m (AD9523 OUT6): same nominal frequency, unknown phase; the FIFO absorbs phase/jitter, `cal_status[15]` (FIFO overflow) must stay 0 on hardware. If the two clocks are not frequency-locked the design needs a re-sampler (not present).
- IDELAYCTRL placement: all IDELAYE2 and the IDELAYCTRL must be in bank 14 (`IODELAY_GROUP` set in the XDC); the 200 MHz reference comes from the MMCM through a BUFG.
- Bank 14 is 3.3 V: LVDS_25 inputs only with `DIFF_TERM FALSE` and external 100 Ω termination (design conflict kept visible in the XDC; section 6 item 3).
- ISERDESE2 Q1..Q4 bit order: resolved from UG471 (section 6) — `Q1_IS_OLDEST = 0` in RTL, receiver and TB, and the simulation model was corrected to the same order; still confirm on hardware with the ADC PN9 pattern (0x0D = 0x06) against a PN9 generator. BUFR framing is irrelevant for the data path and absorbed by the per-lane alignment.
- Blind calibration limits (`adc_capture_calib.v` header): single CW tone at the programmed frequency with every bit toggling (≥ ~64 LSB peak for bit 7); the LSB lanes need ≤ ~1 LSB rms input noise at the default 512-word window (0.7 LSB rms in the TB; AD9484 ~47 dB SNR = ~0.5 LSB rms) — at 1.4 LSB rms lane 0 reports `undetermined` and keeps its tap; the eye-centre extrapolation for runs cut at tap 0 assumes exactly 32 taps per bit (400 MSPS, 78.125 ps/tap) and a 5-tap metastable region (`FAIL_HALF = 2`, the simulation model's 0.4 ns; the hardware value is unknown, an error of e taps moves the centre by e); the blind framing alignment takes the minimum of four metrics without a significance test (`align_fail` stays 0). Run time ~3.3 ms (2 passes × 8 lanes × 32 taps × 528 clk_div cycles + 3 alignments).
- Checks after implementation: `report_clock_interaction` (clk_div ↔ clk_100m only through the FIFO, adc_dco/clk_div/clk_200m as derived clocks), `report_timing_summary` for the clk_div and clk_200m paths, `report_cdc`, `report_io`; on hardware: run the auto calibration with the ADC test pattern, read `CAL_STAT`/`CAL_LANE_INFO` per lane (windows should be ~27 of 32 taps wide at 400 MSPS), then switch to normal data and check `CAL_ERR` stays 0 while the pattern check is off.

## 6. UG471 documentary checks

UG471 v1.10 (`build/docs_ext/ug471.txt` = pdftotext of the web-archive copy, 2026-10-09) was used to settle two open points; the simulation model and the RTL default were changed where they disagreed (CHANGELOG "Command set v2, blind calibration, UG471") (source: `beta/fpga/README.md`, "UG471 checks", quotes copied verbatim):

1. ISERDESE2 output order, section "ISERDESE2 Ports - Registered Outputs - Q1 to Q8" (p. 146): *"The first data bit received appears on the highest order Q output. The bit ordering at the input of an OSERDESE2 is the opposite of the bit ordering at the output of an ISERDESE2 block, as shown in Figure 3-3. For example, the least significant bit A of the word FEDCBA is placed at the D1 input of an OSERDESE2, but the same bit A emerges from the ISERDESE2 block at the Q8 output. In other words, D1 is the least significant input to the OSERDESE2, while Q8 is the least significant output of the ISERDESE2 block."* (OSERDESE2 section, p. 161: *"data on the D1 input pin is the first bit transmitted"*). For the 1:4 SDR configuration the first (oldest) bit is therefore on **Q4**, the newest on **Q1** → `Q1_IS_OLDEST = 0`, `word[7:0] = Q4` (s0 = oldest). The sim model had Q1 = oldest and was corrected.
2. BITSLIP in SDR mode, section "BITSLIP Submodule - Bitslip Operation" (p. 158): *"By asserting the Bitslip pin of the ISERDESE2 block, the incoming serial data stream is reordered at the parallel side. ... (Bit 8 of an input ISERDESE2 is the first bit received.) ... The Bitslip operation is synchronous to CLKDIV. In SDR mode, every Bitslip operation causes the output pattern to shift left by one. In DDR mode, every Bitslip operation causes the output pattern to alternate between a shift right by one and shift left by three."* and *"Although the repeating pattern seems to show that bitslip is a barrel shifting operation, this is not the case. A bitslip operation adds one bit to the input data stream and loses the nth bit in the input data stream."* Figure 3-11 (SDR): initial 10010011 → after one Bitslip 00100111 (Q8..Q1 notation), i.e. the word boundary moves one bit later in the serial stream. "Guidelines for Using the Bitslip Submodule" (p. 159): *"In NETWORKING mode the Bitslip submodule is available. ... the BITSLIP port must be asserted High for one CLKDIV cycle. Bitslip cannot be asserted for two consecutive CLKDIV cycles; ... the total latency ... is two CLKDIV cycles. ... The user logic should wait for at least two CLKDIV cycles in SDR mode ... before analyzing the received data pattern"* — `adc_capture_calib` pulses BITSLIP for one cycle with ≥ 1 idle cycle between pulses and waits SETTLE = 16 cycles; the sim model's slip direction was corrected to Fig. 3-11.
3. LVDS_25 inputs in a 3.3 V HR bank, section "LVDS and LVDS_25 (Low Voltage Differential Signaling)" (p. 92): *"It is acceptable to have differential inputs such as LVDS and LVDS_25 in I/O banks that are powered at voltage levels other than the nominal voltages required for the outputs of those standards (1.8V for LVDS outputs, and 2.5V for LVDS_25 outputs). However, these criteria must be met: - The optional internal differential termination is not used (DIFF_TERM = FALSE, which is the default value). - The differential signals at the input pins meet the VIN requirements in the Recommended Operating Conditions table of the specific device family data sheet. - The differential signals at the input pins meet the VIDIFF (min) requirements in the corresponding LVDS or LVDS_25 DC specifications tables of the specific device family data sheet. - For HR I/O banks in bidirectional configuration, internal differential termination is always used."*; Figure 1-72 text: *"RDIFF provides the 100 Ohm differential receiver termination because the internal DIFF_TERM is set to FALSE."*; Table 1-55 note 1a: *"The optional internal differential termination is not used (DIFF_TERM = FALSE, which is the default value) unless the VCCO voltage is at the level required for outputs."*; "Differential Termination Attribute" (p. 49): *"The VCCO of the I/O bank must be connected to 1.8V for LVDS, and 2.5V for the other differential I/O standards to provide 100 Ohm of effective differential termination. DIFF_TERM is only available for inputs and can only be used the appropriate VCCO voltage."* → the XDC keeps `LVDS_25` + `DIFF_TERM FALSE` on the nine bank-14 pairs and states that an external 100 Ω termination at the FPGA (absent on the schematic) and a VIN/VIDIFF/VICM check of the AD9484 output against DS181 are REQUIRED (board change / verification).

## 7. Constraints (`beta/fpga/constraints/radar_system_top_beta.xdc`, 348 lines)

Clocks as read by `tools/check_fpga_constraints.py` (executed 2026-10-09; source: tool output and the XDC lines quoted):

| XDC line | Clock | Period | Port | Comment in the XDC |
|---|---|---|---|---|
| 18 | `clk_100m` | 10.000 ns | `clk_100m` | AD9523 OUT6 "FPGA_SYSTEM_CLOCK" |
| 19 | `clk_120m_dac` | 8.333 ns | `clk_120m_dac` | AD9523 OUT11 "FPGA_DAC" |
| 20 | `adc_dco` | 2.500 ns | `adc_dco_p` | AD9484 DCO, 400 MHz SDR |
| 23 | `ft601_clk_in` | 10.000 ns | `ft601_clk_in` | no pin (FT601 unwired) |
| 28 | `spi_sclk` | 37.000 ns | `stm32_sclk_3v3` | 27 MHz max (STM32 SPI1, APB2 108 MHz / 4) |

Content of the file (source: `beta/fpga/README.md`, "Constraints"; XDC lines 36, 60–61, 70–71, 83, 96–98, 140–146):

- Pins: verbatim schematic-derived candidates for 64 ports / 64 bits (`PIN_MAP_FROM_SCHEMATIC.md`), every ball still to be cross-checked against the AMD FTG256 package file and the final layout.
- `set_clock_groups -asynchronous` for all clock groups (line 36); false paths for the asynchronous STM32 lines and the SPI pass-through; `set_input_delay` for the ADC bus from the datasheet skew plus an **unverified** ±0.25 ns board allowance.
- `IODELAY_GROUP adc_idelay_grp` on the IDELAYCTRL and the per-lane IDELAYE2 cells (lines 60–61).
- DAC output delays: UNRESOLVED placeholder — `dac_clk` has no FPGA pin, the AD9708 is clocked by AD9523 OUT10 (lines 70–71); STM32F7 SPI1 master timing versus SCLK at the FPGA pins UNRESOLVED (line 83).
- `CFGBVS VCCO` / `CONFIG_VOLTAGE 3.3` from the bank-0 supply (lines 96–98; CFGBVS pull direction via R to be verified).
- **Design conflict kept visible:** bank 14 is 3.3 V on the schematic; the LVDS_25 ADC inputs (9 pairs: `adc_dco_p/n`, `adc_d_p/n[7:0]`) are constrained `IOSTANDARD LVDS_25` + `DIFF_TERM FALSE` (option A — external 100 Ω termination REQUIRED, REQUIRES VERIFICATION; the UG471 criteria are quoted in the XDC header) and the `DIFF_TERM TRUE` lines are left commented as option B (bank VCCO change to 2.5 V, a board change) (lines 140–146 and following).
- Host-link option B pins H11/G12/H12 (DIG_5..7, bank 15, LVCMOS33, `PULLUP` on CS) added; `spi_sclk` is a fifth asynchronous clock group.
- UNRESOLVED (116 bits, listed at the end of the file, unconstrained): `dac_clk`, all `ft601_*` (FT601 U6 has 0/77 pins connected), `current_*`, `new_chirp_frame`, `dbg_*`, `system_status` (no board nets). `write_bitstream` will refuse the unconstrained I/O unless they are removed from the top or `UNCONSTRAINEDPINS ALLOW` is set for a resource/timing trial only.

## 8. Host path

Option B (SPI bridge on the STM32 SPI1 bus, command set v2, register map) is implemented in the BETA RTL and verified by `tb_host_bridge` and `tb_host_bridge_top`; option A (FT601) is kept unchanged as the original `usb_data_interface` packetiser running on clk_100m so the data path can be simulated — a real FT601 needs the FSM re-timed to `ft601_clk` through `async_fifo` and the D-19 changes (source: `beta/fpga/README.md`, "Host path"). Signals, frame format, command set and register map are in chapter 9 §3; the unresolved RTL items are: STM32 SPI1 timing versus the FPGA pins (XDC placeholders), BRAM inference of the SCLK-domain frame RAM read (`host_bridge_spi.v`, asynchronous read registered on falling SCLK), and the firmware rule that no ADAR1000 transaction overlaps a bridge read.

## 9. Xilinx FFT IP settings (not generated)

Status (source: `beta/fpga/ip/README.md`): IP **not generated** (no Vivado on the authoring machine). `rtl/xfft_32.v` and `rtl/FFT_enhanced.v` contain simulation-only behavioural models (`axis_fft_behav.v`) and, under `SYNTHESIS`, an instantiation of a deliberately missing module so that synthesis fails loudly until the IP exists; `vivado/create_project.tcl` imports `ip/<name>/<name>.xci` when present. Settings are derived from how the RTL drives the ports; rounding mode, latency and output order are recorded choices so that model and IP agree.

Common settings (source: `beta/fpga/ip/README.md`, copied verbatim):

| Setting (Vivado FFT v9.1 GUI) | Value | Evidence |
|---|---|---|
| Vendor / library / version | `xilinx.com:ip:xfft:9.1` | docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md FPGA-T04 |
| Number of channels | 1 | one `s_axis_data` stream |
| Architecture | Pipelined Streaming I/O | back-to-back frames assumed by `matched_filter_processing_chain.v` (queue) and continuous output in the model |
| Data format | Fixed point, **Scaled** | config word carries a scaling schedule (see below); block floating point would need `m_axis_data_tuser` BLK_EXP handling that the RTL does not have |
| Input data width | 16 | `s_axis_data_tdata[31:0] = {Q[15:0], I[15:0]}` (`fft_1024_forward.v:18`, `doppler_processor.v:289`) |
| Phase factor width | 16 | choice (model uses double precision; 16 keeps the +/-2 LSB tolerance of `tb_fft_wrappers.v` realistic - to be confirmed by running the TB against the IP's simulation model) |
| Rounding | Convergent rounding | choice; the model uses round-half-up (not bit exact, +/-1 LSB) |
| Output ordering | **Natural order** | `matched_filter_processing_chain.v` addresses the reference memory with a sequential bin counter |
| Cyclic prefix | none | not used |
| ACLKEN / ARESETn | ARESETn enabled (active low, >= 2 cycles) | `.aresetn(reset_n)` |
| XK_INDEX / OVFLO in tuser | optional (not connected) | not used by the RTL |

`xfft_32` (Doppler, `doppler_processor.v:283-296`; source: same, copied verbatim):

| Setting | Value | Evidence |
|---|---|---|
| Module name | `xfft_32` | instance name in the RTL |
| Transform length | 32 | `DOPPLER_FFT_SIZE = 32`, `fft_input_last` after 32 samples |
| Throttle scheme | **Non Real Time** (has `m_axis_data_tready`) | `.m_axis_data_tready(1'b1)` is connected |
| Config word | 8 bits: bit0 FWD_INV, bits[5:1] SCALE_SCH (2+2+1 bits for radix-4, radix-4, radix-2 stages) | `s_axis_config_tdata(8'h..)`; RTL default `FFT_CONFIG_WORD = 8'h35` = forward, shift 2+2+1 = 2^-5 |
| Transform direction | run-time configurable (forward used) | config bit0 = 1 |
| Model latency (`axis_fft_behav` LATENCY) | 72 clocks from the last input | placeholder; the real IP latency is reported by the GUI and must be below `FFT_WAIT_TIMEOUT` (1000) in `doppler_processor.v` |

`FFT_enhanced` (pulse compression, `fft_1024_forward.v:102`, `fft_1024_inverse.v:78`; source: same, copied verbatim):

| Setting | Value | Evidence |
|---|---|---|
| Module name | `FFT_enhanced` | "This must match the name in your project" (`fft_1024_forward.v:101`) |
| Transform length | 1024 | `tlast` after 1024 samples (`fft_1024_forward.v:58`), reference memory 1024 bins per segment |
| Throttle scheme | **Real Time** (no `m_axis_data_tready`) | the instantiations do not connect `m_axis_data_tready`; the wrappers tie their internal tready to 1 |
| Config word | 16 bits: bit0 FWD_INV, bits[10:1] SCALE_SCH (2 bits x 5 radix-4 stages), upper bits padding | `s_axis_config_tdata[15:0]`; forward default `SCALE_SCH = 10'h255` (shifts 1,1,1,1,2 = 2^-6), inverse `10'h155` (2^-5) |
| Transform direction | **run-time configurable** | same core used forward (`16'h...1`) and inverse (`16'h...0`) |
| Model latency | 160 clocks (beta model value, the IP is ~2-3k clocks for 1024 points) | the chain tolerates any latency (reference fetched by address, frames queued) |

The `create_ip` / `set_property -dict` Tcl for both cores is given in `beta/fpga/ip/README.md` (property names follow the xfft v9.1 `CONFIG.*` set; to be verified with `report_property`, not executed). Scaling-schedule rationale (source: same, "Scaling-schedule arithmetic"): a 1024-sample segment of the 10–30 MHz chirp occupies ~68 bins; with 2^-6 a full-scale input gives ~15.5k without saturation; the inverse transform's 2^-5 puts the compressed peak at ~32k, i.e. the full 16-bit range; the Doppler FFT uses 2^-5 (= 1/N) so that any 16-bit input cannot overflow. Verification of a generated IP against the model: run `tb_fft_wrappers` with the IP simulation model (`SYNTHESIS` not defined), expect PASS at ±2 LSB (raise `TOL` and record the measured difference if the IP rounds differently), record the IP latency and check `FFT_WAIT_TIMEOUT`.

## 10. Change classes versus the original (`beta/fpga/CHANGELOG.md`)

Legend of the changelog: **SYN** syntax/elaboration fix, **BUG** functional defect fix, **ARCH** architecture/interface change (documented in the README), **NEW** file written for the beta, **CLEAN** lint/readability only. Counting the typed rows of its tables gives 28 ARCH, 28 BUG, 12 CLEAN, 11 NEW, 9 SYN (count made for this manual with `grep` over `beta/fpga/CHANGELOG.md`; the file has 242 lines). Files copied unchanged except line endings: `dac_interface_single.v`, `fir_lowpass.v`, `level_shifter_interface.v`, `ddc_input_interface.v`; `plfm_chirp_controller.v` LUT contents unchanged. Files moved to `rtl/unused_orig/` (not compiled): `ad9484_interface_400m.v`, `lvds_to_cmos_400m.v`, `cdc_modules.v`, `latency_buffer_2159.v`, `usb_packet_analyzer.v`; `chirp_lut_init.v` and `radar_system_tb.v` were not copied into `rtl/` (the original testbench is kept as `tb/radar_system_tb_original.v`, not run). Per-file sections exist for `radar_system_top.v`, `radar_receiver_final.v` (rewritten; instance names and chain order kept), `radar_transmitter.v`, `plfm_chirp_controller.v`, `edge_detector.v`, `ddc_400m.v`, `cic_decimator_4x_enhanced.v`, `nco_400m_enhanced.v`, `chirp_memory_loader_param.v`, `matched_filter_multi_segment.v`, `frequency_matched_filter.v`, `fft_1024_forward/inverse.v`, `doppler_processor.v`, `usb_data_interface.v`, plus three follow-up sections (host-link option B integration; ISERDES capture + polyphase DDC; command set v2, blind calibration, UG471 checks) (source: `beta/fpga/CHANGELOG.md`, section headings).

New files (source: `beta/fpga/CHANGELOG.md`, "New files", copied verbatim):

| File | Content |
|---|---|
| `rtl/ad9484_lvds_to_cmos_400m.v` | AD9484 SDR LVDS capture (IBUFDS + BUFG + IDDR as dual-edge sampler, `CAPTURE_FALLING`), `ifdef SIM` behavioural model, reset synchroniser, `adc_valid`, `adc_pwdn` from `pwdn_req` |
| `rtl/matched_filter_processing_chain.v` | FFT1024 -> x conj(ref) -> IFFT1024 with address-driven reference fetch and segment queue |
| `rtl/range_bin_decimator.v` | 1024 -> 64 bins, modes first/peak/mean/sum, `start_bin` |
| `rtl/xfft_32.v`, `rtl/FFT_enhanced.v` | IP-named AXI4-Stream wrappers: behavioural model under `ifndef SYNTHESIS`, fail-loud placeholder under `SYNTHESIS` (see `ip/README.md`) |
| `rtl/axis_fft_behav.v` | behavioural AXI4-Stream FFT (simulation only) |
| `rtl/async_fifo.v`, `rtl/reset_synchronizer.v`, `rtl/radar_control_regs.v` | CDC FIFO, reset synchroniser, register map |
| `rtl/sim/unisim_sim_models.v` | BUFG / IBUFDS / IDDR models for simulation and lint (excluded from Vivado) |
| `mem/long_chirp_seg3_{i,q}.mem` | generated (all zero - segment beyond the 3000-sample chirp), `gen_chirp_mem.py` |
| `tb/tb_*.v`, `tb/gen_vectors.py`, `tb/vectors/` | self-checking testbenches and numpy references |
| `constraints/radar_system_top_beta.xdc`, `vivado/*.tcl`, `ip/README.md`, `build.sh` | constraints, Vivado scripts (not executed), IP settings, open-source flow |

The follow-ups added `rtl/host_bridge_spi.v`, `rtl/rd_map_packer.v` (with the `det_wr` width fix), `tb/tb_host_bridge.v`, `tb/tb_host_bridge_top.v`, `rtl/ad9484_iserdes_capture.v`, `rtl/adc_capture_calib.v`, `rtl/ddc_4x_100m.v`, `rtl/clk_gen.v`, `tb/tb_adc_iserdes_capture.v`, `tb/tb_ddc_4x.v`, extended `rtl/sim/unisim_sim_models.v` (BUFIO, BUFR, IDELAYE2, IDELAYCTRL, ISERDESE2, MMCME2_BASE), and one legacy bug fix in `ddc_400m.v` (NCO `phase_valid` gated by `adc_data_valid`) (source: `beta/fpga/CHANGELOG.md`, the three follow-up sections).

## 11. Synthesis without Vivado — open-source estimate (`beta/fpga_synth/`)

**Status: OPEN-SOURCE ESTIMATE. Not a Vivado result.** Every number comes from Yosys (`synth_xilinx -family xc7`) and, where stated, nextpnr-xilinx; Vivado's synthesis, retiming, DSP/BRAM inference and timing models differ; nothing here replaces `beta/fpga/vivado/build.tcl` (source: `beta/fpga_synth/README.md`, header).

What was synthesised (source: same, "What was synthesised"): git snapshot **65cd160** of `beta/fpga` (the working tree had uncommitted edits by another session — undriven `host_bridge.reg_rdata`, `calib.blind_*`, `lane_metric`, implicit `inherit_tap`/`inherit_valid` — so the committed snapshot was used; **re-run `REV=HEAD ./run_synth.sh` after those edits are committed**, which the command-set-v2 follow-up has since done in `beta/fpga` but the synthesis directory has not been re-run at the time of writing); file list = `build.sh` step 2 minus `rtl/axis_fft_behav.v` and `rtl/sim/unisim_sim_models.v`; top `radar_system_top`, default parameters (`ADC_CAPTURE_MODE = 1`); part xc7a50tftg256-2; the two FFT IP cores declared `(* blackbox *)` — 3 instances excluded from the counts. Tools: Yosys 0.69+post (Homebrew), nextpnr-xilinx bc9b234 (openXC7, archived fork), prjxray-db a90f27c, chip database `xc7a50t.bin` 93 MB, prjxray tools c9f02d8.

Utilisation (source: `beta/fpga_synth/README.md`, copied verbatim; budget XC7A50T per AMD DS180 Table 3: 8,150 slices = 32,600 LUT / 65,200 FF, 120 DSP48E1, 75 × 36 kb BRAM, 5 CMT):

| Resource | Yosys count | XC7A50T budget | Utilisation |
|---|---:|---:|---:|
| LUT total (logic + distributed RAM + SRL) | 12793 | 32,600 | 39.2 % |
|   of which logic LUT1..LUT6 | 9693 | - | - |
|   of which distributed RAM (RAM64M/RAM32M x 4 LUTs) | 3100 | - | - |
|   of which shift register (SRL16E/SRLC32E) | 0 | - | - |
| INV cells (absorbed into LUTs by P&R, not counted) | 246 | - | - |
| Flip-flops (FDRE/FDSE/FDCE/FDPE, incl. _1 falling-edge) | 4726 | 65,200 | 7.2 % |
| Latches (LDCE/LDPE) | 0 | - | - |
| DSP48E1 | 106 | 120 | 88.3 % |
| RAMB36E1 | 0 | - | - |
| RAMB18E1 | 2 | - | - |
| BRAM in 36 kb equivalents (RAMB36 + RAMB18/2) | 1 | 75 | 1.3 % |
| CARRY4 | 333 | 8,150 | 4.1 % |
| MUXF7 / MUXF8 | 0 | - | - |
| BUFG / BUFGCTRL | 4 | 32 | 12.5 % |
| BUFIO / BUFR | 2 | - | - |
| MMCME2_BASE/ADV, PLLE2 | 1 | 5 | 20.0 % |
| IBUF / IBUFG / IBUFDS | 31 | - | - |
| OBUF / OBUFT / IOBUF | 143 | - | - |
| IDELAYE2 / IDELAYCTRL | 9 | - | - |
| ISERDESE2 / IDDR | 8 | - | - |
| FFT IP black boxes (not counted above) | 3 | - | - |

Per module (source: same, hierarchical run, local cells only; `fir_lowpass_parallel_enhanced` is instantiated twice so its 32 DSP count twice; flat total 36 + 2 × 32 + 4 + 2 = 106 DSP):

| Module (hierarchical run, -noflatten) | LUT logic | LUT as RAM | FF | DSP48E1 | RAMB18E1 |
|---|---:|---:|---:|---:|---:|
| `host_bridge_spi` | 809 | 1536 | 85 | 0 | 0 |
| `plfm_chirp_controller_enhanced` | 2287 | 0 | 52 | 0 | 0 |
| `doppler_processor_optimized` | 630 | 1536 | 128 | 2 | 0 |
| `chirp_memory_loader_param` | 1847 | 0 | 33 | 0 | 0 |
| `adc_capture_calib` | 961 | 0 | 572 | 0 | 0 |
| `ddc_4x_100m` | 889 | 0 | 1118 | 36 | 0 |
| `rd_map_packer` | 610 | 0 | 726 | 0 | 0 |
| `range_bin_decimator` | 318 | 0 | 180 | 0 | 0 |
| `matched_filter_multi_segment` | 177 | 0 | 76 | 0 | 2 |
| `fir_lowpass_parallel_enhanced` | 129 | 0 | 614 | 32 | 0 |
| `frequency_matched_filter` | 126 | 0 | 292 | 4 | 0 |
| `radar_control_regs` | 84 | 0 | 61 | 0 | 0 |
| `radar_system_top` | 63 | 0 | 98 | 0 | 0 |
| `usb_data_interface` | 61 | 0 | 118 | 0 | 0 |
| `async_fifo` | 22 | 24 | 89 | 0 | 0 |
| `matched_filter_processing_chain` | 41 | 4 | 57 | 0 | 0 |
| `ad9484_iserdes_capture` | 7 | 0 | 38 | 0 | 0 |
| `ddc_input_interface` | 4 | 0 | 36 | 0 | 0 |

The four design consequences (source: `beta/fpga_synth/README.md`, "Reading the numbers"):

1. **DSP48E1 is the binding resource: 106 of 120 (88 %) without the FFT IP.** 64 are the two 32-tap fully parallel FIRs (`fir_lowpass.v`), 36 the polyphase DDC (`ddc_4x_100m.v`: 8 mixers + the CIC-as-FIR), 4 the matched-filter complex multiply, 2 the Doppler window. Only **14 DSP48E1 remain for three FFT cores** (2 × 1024-point + 1 × 32-point, Pipelined Streaming, 16-bit). The xfft v9.1 DSP count must be read from the Vivado IP GUI before anything else; if it exceeds 14 the design does not fit the XC7A50T as written (options: FIR symmetry folding / time-multiplexing at 100 MHz vs. 25 MSPS output, Radix-2 Lite / Burst I/O FFT architecture, or LUT multipliers via `use_dsp = "no"`). Not decided.
2. **Block RAM is almost unused (2 × RAMB18) because the RTL memories cannot map to BRAM**, not because the design is small: `chirp_memory_loader_param.v:32-35` (`ram_style = "block"`) muxes the read data before the output register, which has an asynchronous reset → no synchronous read port → ~1,850 LUTs of logic; `doppler_processor.v:74-75` feeds the multiplier combinationally → 1,536 LUTs as RAM64M (Yosys-specific trap: by default the frontend turned the memory into 65,611 flip-flops, more than the whole device; `run_synth.sh` reads this file with `-nomem2reg`); the `host_bridge_spi` frame RAM has an asynchronous read in the SCLK domain → 1,536 LUTs as RAM64M; only the `matched_filter_multi_segment.v:83-84` input buffers map to RAMB18 (2). Recommended RTL change (designer decision, not made): register each memory output in its own clocked block without reset, mux afterwards — moves ~4,900 LUTs into roughly 7–8 RAMB36.
3. LUTs (39 %) and FFs (7 %) leave room; the FFT IP adds BRAM/LUT/DSP on top.
4. **I/O: 183 port bits need 192 package pins** (9 LVDS pairs) — more than the 170 user I/O of the FTG256 package (DS180 Table 3 / package table — verify against UG475), even before pin conflicts. The 116 UNRESOLVED debug/FT601/status bits must be removed from the top for any board build.

Synthesis warnings that indicate real problems (source: same section): latches none, multi-driven nets none, post-synthesis `check` 0 problems; `chirp_memory_loader_param.v:112` `$time` inside a `DEBUG`-gated `$display` leaves a `$print` cell that nextpnr cannot place (wrap in `translate_off`); forced `ram_style = "block"` impossible on 6 memories (above); tri-state logic on the FT601 bus and MISO mapped to IOBUF/OBUFT (fine); **clocking: Yosys inserted a 4th BUFG on `host_bridge.sclk` = `stm32_sclk_3v3`, XDC pin J16 = `IO_L23N_T3_FWE_B_15`, not a clock-capable MRCC/SRCC pin** — Vivado will refuse a non-CC pin driving a BUFG unless the net gets `set_property CLOCK_DEDICATED_ROUTE FALSE` (not in the XDC) or SCLK is oversampled in clk_100m instead.

P&R trial, nextpnr-xilinx (source: `beta/fpga_synth/README.md`, "P&R trial", copied verbatim): **NOT COMPLETED — no placed/routed design, no Fmax, no bitstream.** Inputs: the 67 PACKAGE_PIN + IOSTANDARD assignments and `create_clock` lines of the beta XDC; netlist with the 116 unconstrained port bits demoted to internal nets, the FFT IP replaced by 1-register pass-through stubs (NOT an FFT), `$print` removed — 12,747 LUT, 4,667 FF, 106 DSP48E1, 2 RAMB18E1.

| Step | Result | Log |
|---|---|---|
| nextpnr-xilinx build (openXC7 bc9b234) | PASS after `-DUSE_OPENMP=OFF` (Apple clang: `unsupported option '-fopenmp'`) | `~/.cache/aeris10_work/nextpnr_make.log` |
| Chip database xc7a50tftg256-2 (`bbaexport.py` + `bbasm`) | PASS, 93 MB `xc7a50t.bin` | `~/.cache/aeris10_work/nextpnr-src/chipdb/*.log` |
| prjxray `xc7frames2bit` + `fasm2frames.py` (venv) | PASS (built/installed, never reached) | `~/.cache/aeris10_work/prjxray_make.log` |
| nextpnr, first try | FAIL at placement: `Unable to place cell ... $display ...: no Bels remaining of type '$print'` (DEBUG `$display` in `chirp_memory_loader_param.v:113`) -> fixed in `synth_yosys_pnr.ys` | (overwritten; reproducible) |
| Packing (all primitives) | **PASS**: IBUFDS/IBUF/OBUF, BUFGCTRL 4/32, BUFIO 1/20, BUFR 1/20, IDELAYE2 8, ISERDESE2 8, IDELAYCTRL 1/5, MMCME2_ADV 1/5 (from MMCME2_BASE), DSP48E1 106/120, RAMB18E1 2/150, CARRY4 344/8150, SLICE_LUTX 15,182/65,200 (LUT sites incl. LUTRAM), SLICE_FFX 4,667 | `logs/nextpnr_heap_seed*.log.gz` (utilisation block) |
| Placement, HeAP (default) placer, seeds 2-6 | **FAIL** (deterministic, < 5 s): `Unable to find legal placement for cell '...ddc_4x_100m.v:175$12861'` - a standalone DSP48E1 (DDC mixer) that cannot be legalised after the 10 cascade chains (8 x 8 DSP FIR adder chains `fir_lowpass.v:53`, 2 x 7 DDC chains `ddc_4x_100m.v:204`; 78 of the 106 DSPs) are fixed in the two 60-site DSP columns (x = 28, 86 in prjxray tilegrid) | `logs/nextpnr_heap_seed{2..6}.log.gz` |
| Placement, SA placer, seed 1 (unpatched) | **HUNG**: annealing converged to iteration 255 (wirelen 743,990) after ~16 min, then 20+ min at 100 % CPU without output; `sample` shows `SAPlacer::random_bel_for_cell` spinning in its unbounded `while (true)` retry loop (`common/placer1.cc:876-895`) when moving a DSP chain base with `force_z`. Killed. | `logs/nextpnr_sa_livelock.log.gz` |
| Placement, SA placer, seed 1, locally patched retry bound (`pnr/nextpnr_placer1_retry_bound.patch`) | **ABORTED by time-box** at iteration ~170 (10.5 min, still placing, same trajectory); routing never started | `logs/nextpnr_sa_patched_seed1.log.gz` |
| Routing, timing (Fmax), FASM, `fasm2frames`, `xc7frames2bit` | **NOT REACHED** - no Fmax figure exists from any run; no `.fasm`, no `.bit` | - |

Blocking items for the open-source P&R (tool side, not design errors; source: same): (1) DSP48E1 cascade chains at 88 % DSP utilisation — HeAP cannot legalise them, SA livelocks; next things to try (not done): the patched SA run to completion (~30–60 min estimate, unverified) or the maintained openXC7/nextpnr `himbaechel` xilinx flow; (2) even with a routed result the timing would be incomplete: `set_clock_groups`, `set_false_path`, `set_input_delay`, `IODELAY_GROUP`, `DIFF_TERM`, `CFGBVS`/`CONFIG_VOLTAGE` are not parsed by nextpnr-xilinx, the ADC ISERDES/IDELAY input window is not analysed, and the FFT stubs remove the FFT critical paths. Any bitstream from this flow would contain the stubs (named `..._OPENSOURCE_STUBFFT.bit` by `run_pnr.sh`) and **must never be loaded on the radar hardware**.

What must be run in Vivado to confirm (source: same, "What must be run in Vivado"): generate the FFT IP per section 9; `vivado -mode batch -source beta/fpga/vivado/create_project.tcl`; `vivado -mode batch -source beta/fpga/vivado/build.tcl -tclargs <path>/aeris10_beta.xpr 8`; inspect `report_utilization -hierarchical` (DSP48E1 total **with** the 3 FFT cores ≤ 120; BRAM use of `chirp_mem`, `doppler_proc`, `host_bridge`; RAM/ROM inference tables), `report_timing_summary` (WNS/WHS ≥ 0 for clk_100m, clk_120m_dac, adc_dco/BUFR, clk_200m, spi_sclk), `report_clock_interaction`, `report_cdc`, `report_methodology`, `report_io` / `report_drc` (non-CC pin J16 → BUFG; bank-14 LVDS_25 at 3.3 V VCCO; IODELAY_GROUP and IDELAYCTRL placement; unconstrained ports — remove the 116 UNRESOLVED bits from the top first); `write_bitstream` only after all of the above (acceptance criteria AC-F5…AC-F8, all NOT MET; source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`).

## 12. Remaining work (ordered) and known limitations

Remaining work (source: `beta/fpga/README.md`, "Remaining work (ordered)"):

1. **Generate the two FFT IP cores** per `ip/README.md`, run `tb_fft_wrappers` against the IP simulation models (adjust `TOL` if the IP's per-stage rounding differs), record the IP latency and check `FFT_WAIT_TIMEOUT` in `doppler_processor.v`.
2. **Synthesis / implementation** with `vivado/create_project.tcl` + `vivado/build.tcl` (default part `xc7a50tftg256-2` = schematic U42; README/XDC claim XC7A100T — resolve first, K1). Expect resource pressure: two 1024-point FFT IPs, 2 × 32 parallel 18×18 multipliers in the FIR (64 DSP48E1 of the 50T's 120); the open-source estimate of section 11 puts the non-FFT design at 106 of 120 DSP48E1.
3. **400 MHz fabric path replaced** (`ADC_CAPTURE_MODE = 1`): remaining are Vivado timing on the clk_div/clk_200m paths, IDELAYCTRL/IODELAY_GROUP placement, hardware calibration with the ADC test pattern, Q1..Q4 order on hardware.
4. **Matched-filter throughput.** The chain is not pipelined against the collector: one long chirp (4 segments) occupies the FSM for ~92 µs with the behavioural FFT latency (160 clocks) and ~270 µs with a realistic IP latency (~2.3k clocks per transform), while the TX repeats long chirps every 167 µs (`plfm_chirp_controller.v`: 30 µs chirp + 137 µs listen). Samples arriving while the FSM is not in `ST_COLLECT_DATA` are dropped (original behaviour). Needs ping-pong buffering or overlapping collect/process; the smoke test uses a 300 µs period for this reason.
5. **Segment semantics.** Each 1024-sample segment is compressed against its own reference segment and produces its own 64-bin profile; the four profiles per chirp are not summed, and the Doppler processor counts each profile as a "chirp" (a 32-"chirp" frame = 8 real chirps). Decide whether to sum the partial correlations (true partitioned matched filter) or to use a 4096-point transform.
6. **Hardware bring-up items** (all UNRESOLVED): confirm the chirp direction / `CONJUGATE_REF`; AD9484 capture edge and trace skew; bank-14 LVDS termination; ADC test pattern check; DAC data timing versus the externally clocked AD9708 (`dac_clk` has no pin); STM32 SPI1 clock rate versus the 1-cycle SPI pass-through re-timing; the short-chirp reference; the FT601/host decision.
7. CFAR (the detector is still a fixed threshold, default 10000 via `CFAR_THRESHOLD_DEFAULT`, now writable over the bridge as CFAR_THR); removal of the 116 unconstrained debug/status bits from the top before a board build. Register-map host interface: done (command set v2); `det_wr` back-port to `engineering/DESIGN/HOST_LINK/rtl/`: done.
8. GUI `beta/gui/aeris10_gui/protocol/register_map.py` follow-up (5-bit address mask, 0x04 bit4, 0x0D, 0x0E, 0x10) — recorded in the FPGA README; the GUI changelog's "final register map, RTL 0x0002" entry records the alignment (`ADDR_MASK = 0x1F`, registers 0x0D/0x0E/0x10) (source: `beta/gui/CHANGELOG.md`, "2026-10-09 (final register map, RTL 0x0002)"; `beta/gui/aeris10_gui/protocol/register_map.py:18`).

Known limitations of the beta (source: `beta/fpga/README.md`, "Known limitations"): not synthesised, no timing, no hardware test; FFT IP not generated (fail-loud placeholders); behavioural FFT models are not bit-exact with the Xilinx IP (total-shift scaling, round-half-up; TB tolerance ±2 LSB) and their latencies (72 / 160 clocks) are placeholders; `rtl/sim/unisim_sim_models.v` models only the behaviour the design uses (no timing, IB ignored); the USB packetiser runs on clk_100m and drops records that arrive while a packet is in flight (counted internally); the 11-word packet format is a beta definition; the level-shifter pass-through adds one clk_100m cycle to SCLK/MOSI/CS and two to MISO; `use_long_chirp` is a register bit (default 1) and the TX sequence's long/short alternation is not mirrored automatically in the receiver.

Acceptance state for the FPGA (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md` §A and §H): AC-F1…AC-F8 NOT MET on the original tree, AC-F9 (physical ADC capture with a CW tone) NOT RUN; AC-X1 (beta RTL parses/elaborates/lints with 0 errors and all testbenches pass) MET (BETA).
