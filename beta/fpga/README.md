# AERIS-10 FPGA design - BETA project (`beta/fpga/`)

**Status: BETA.** Everything in this directory parses, elaborates, lints and simulates with
open-source tools (Icarus Verilog 13.0, Verilator 5.052, Python 3 / numpy). It has **not been
synthesised** (no Vivado on the authoring machine), has **no timing closure**, has **not been
loaded on hardware**, and the two Xilinx FFT IP cores it needs have **not been generated**.
Nothing under `9_Firmware/9_2_FPGA/` was modified; every difference is listed in
[`CHANGELOG.md`](CHANGELOG.md) with original file:line references.

Starting point: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` (the original RTL did not elaborate:
3 syntax defects, 5 missing modules, multi-driven registers, undriven control inputs, no 400 MHz
capture, placeholder constraints).

## Directory

```
beta/fpga/
├── build.sh                 open-source flow (exit code = number of failures)      <- RUN THIS
├── gen_chirp_mem.py         verifies the .mem formula, writes the missing seg3 files
├── CHANGELOG.md             every change vs. 9_Firmware/9_2_FPGA, file:line + reason
├── rtl/                     synthesisable Verilog-2001 (34 files; incl. host-link option B and the ISERDES capture path)
│   ├── sim/unisim_sim_models.v   BUFG/IBUFDS/IDDR stand-ins (simulation + lint only)
│   └── unused_orig/              5 untouched originals that are no longer compiled (+README)
├── mem/                     8 original .mem copies + generated long_chirp_seg3_{i,q}.mem
├── tb/                      8 self-checking testbenches (9 runs), gen_vectors.py, vectors/, original TB (reference)
├── constraints/radar_system_top_beta.xdc
├── vivado/create_project.tcl, vivado/build.tcl     (NOT executed)
├── ip/README.md             exact FFT IP settings (xfft v9.1) derived from the port usage
└── logs/                    output of the last build.sh run (iverilog, verilator, vvp logs)
```

## How to run

```sh
cd beta/fpga
./build.sh                 # ~2 min; SKIP_SYSTEM=1 ./build.sh skips the long system test; VERBOSE=1 prints sim output
```
`build.sh` runs, in order: iverilog elaboration (simulation view `-DSIM` and synthesis view),
`verilator --lint-only -Wall` on both views, `gen_chirp_mem.py`, `tb/gen_vectors.py`, and every
`tb/tb_*.v` with `vvp`. A testbench passes only if it exits 0 and prints `PASS` and never `FAIL`.
The RTL's `$readmemh` paths are `mem/...` relative to `beta/fpga` (the script `cd`s there; Vivado
resolves Memory Files by name).

## What passed (last run 2026-10-09, after command set v2 + blind calibration; logs in `logs/`)

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

`build.sh` summary line: `0 failure(s), 324 verilator warning line(s) (both views)` (165 synth view + 159 sim view; 219 for the first beta, 241 after the host link, 324 after the ISERDES capture path, unchanged 324 after command set v2 + blind calibration: the only new lint findings were two BLKSEQ on block-local temporaries in the sim-only ISERDESE2 model, marked as intended).

System smoke test evidence (`logs/tb_system_smoke.run.log`): DAC left mid-scale (57540 samples);
40 range profiles (4 segments x 10 chirps); for alternating echo delays of 100 and 420 baseband
samples the segment-0 peak sat at decimated bin 8 and 28 on every chirp - a shift of 20 bins for a
320-sample delay change (320/16 = 20), i.e. pulse compression works end to end through capture ->
DDC -> matched filter -> decimator; 2048 Doppler outputs (one 64 x 32 frame); 2688 USB packets with
0 header/footer/sequence errors; no X on outputs; the matched-filter FSM was idle at every toggle.

Verilator warning breakdown (synthesis view, 165): 59 PINCONNECTEMPTY (monitor/unused IP outputs left
unconnected on purpose), 32 UNUSEDSIGNAL (diagnostic nets of the original, unused IP tready/tlast),
22 WIDTHTRUNC / 16 WIDTHEXPAND (original arithmetic widths, the copied host-link modules, the UNISIM
models), 13 PROCASSINIT + 2 BLKSEQ + 1 ZERODLY (simulation-only UNISIM models in `rtl/sim/`), 9
DECLFILENAME (original file names differ from module names - kept so the docs stay valid), 7
UNUSEDPARAM, 3 GENUNNAMED (original `generate`), 1 CMPCONST (`host_bridge_spi`). None was hidden
with a global `-Wno-*`; the few local `lint_off` pragmas are documented in the source next to the
reason.

Additional checks: `tools/check_fpga_constraints.py --top beta/fpga/rtl/radar_system_top.v --xdc
beta/fpga/constraints/radar_system_top_beta.xdc` -> 0 placeholders, 0 invalid properties, 67/183
port bits constrained (the 116 unconstrained bits are exactly the UNRESOLVED ports below).
`tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl` -> 0 missing RTL modules; the only "missing"
names are the two deliberate IP placeholders (`logs/hier/`).

## What was found and decided (engineering notes)

1. **The reference memories are frequency-domain matched-filter coefficients.**
   `long_chirp_seg{0,1,2}_{i,q}.mem` = `conj(FFT_1024(u_s)) * 31128/max|.|`, where `u` is a
   unit-amplitude 10 -> 30 MHz linear up-chirp, 3000 samples at 100 MSPS (phase fit residual
   0.0018 rad; regenerated to within 1 LSB by `gen_chirp_mem.py`). Segment 3 lies beyond the
   chirp and is therefore all zeros - that is the file that was missing.
   Consequence: the brief's suggestion of a time-domain FIR matched filter would not have used
   the repository data. `matched_filter_processing_chain` is therefore the frequency-domain chain
   the original architecture implies (orphan wrappers `fft_1024_forward/inverse_enhanced` +
   `frequency_matched_filter`), and the reference is multiplied **without** the extra conjugation
   (`CONJUGATE_REF = 0`): with the original conjugating form the numpy model and the RTL produce no
   compression peak (convolution instead of correlation).
   **Open point for the designer:** the same data equals `FFT` of a 30 -> 10 MHz down-chirp, so the
   actual baseband chirp direction after the RF/IF chain decides whether `CONJUGATE_REF` must be
   0 (up-chirp at baseband, as the beta assumes) or 1. `short_chirp_{i,q}.mem` (50 words) matches
   neither a time- nor a frequency-domain chirp and cannot be used - the short-chirp path is
   UNRESOLVED.
2. **AD9484 output is SDR LVDS at the sample rate** (datasheet: "LVDS SDR output", "data clock
   output ... must be captured on the rising edge of the DCO", tSKEW +/-0.07 ns). The capture module
   uses the DCO as the 400 MHz clock (IBUFDS -> BUFG) and an IDDR as a dual-edge sampler, taking
   the falling-edge sample (mid-bit for an edge-aligned bus) by default (`CAPTURE_FALLING`). This
   assumption is documented in `rtl/ad9484_lvds_to_cmos_400m.v` and constrained in the XDC; it must
   be confirmed by Vivado timing analysis and an ADC test pattern on hardware.
3. **Reference alignment by address, not by delay line.** The chain requests reference bin k when
   FFT output bin k appears (1-cycle memory latency compensated), so the fixed 3187-cycle
   `latency_buffer_2159` (tied to an unknown IP latency) is not needed. Works with the behavioural
   model (latency 160) and with any IP latency.
4. **Clock-domain crossings**: `cdc_adc_to_processing` (Gray-coded data words) replaced by Gray-pointer
   FIFOs; a reset synchroniser per non-100 MHz domain; STM32 toggles synchronised in the clock
   domain that consumes them (TX: 120 MHz FSM, RX: 100 MHz).
5. **Register map** (`radar_control_regs`): the receiver's control inputs that were floating wires
   now have one driver with documented reset defaults. Its write/read port is driven by the SPI
   bridge (command set v2, see "Host path"); 5-bit word addresses 0x00..0x10, 16-bit registers,
   table in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` section 7 (kept identical to the RTL).

## ADC capture and DDC front end (`ADC_CAPTURE_MODE`, default 1)

| | mode 0 (legacy) | mode 1 (default) |
|---|---|---|
| Capture | `ad9484_lvds_to_cmos_400m`: IBUFDS -> BUFG (400 MHz global clock) -> IDDR as dual-edge sampler | `ad9484_iserdes_capture`: IBUFDS(DCO) -> BUFIO + BUFR/4; IDELAYE2 (VAR_LOAD) -> ISERDESE2 SDR 1:4 per lane; IDELAYCTRL on 200 MHz from `clk_gen` (MMCM); 32-bit `async_fifo` into clk_100m |
| DDC | `ddc_400m_enhanced`: NCO, mixer, 5-stage CIC at 400 MHz in fabric (timing closure unrealistic), FIFO, FIR | `ddc_4x_100m`: 4-phase NCO + 8 mixers + CIC as 16-tap FIR + the same FIRs, all at 100 MHz; **bit-exact** with the legacy path (`tb_ddc_4x`: max diff 0 LSB) |
| Calibration | none (`CAPTURE_FALLING` edge choice) | `adc_capture_calib`: default tap 16; manual tap/bitslip per lane; **pattern method** (CAL_CTRL bit4 = 0): auto IDELAY sweep with the ADC in a 2-code test pattern (register 0x0D = 0x48, P1/P2 = 0x19..0x1C = pattern A/B; or 0x04 checkerboard / 0x07 toggle), centre tap per lane, lane rotation alignment, lock/undetermined/align_fail status, pattern error counter; **blind method** (CAL_CTRL bit4 = 1, no ADC SPI needed): a CW tone at the IF on the live input, notch residual r[n] = x[n] - 2cos(w)x[n-1] + x[n-2] (CAL_BLIND_COEF = Q1.14 cos(w)), metric = sum of abs(r) over 512 words per tap, one lane swept at a time MSB first, pass = metric <= min + CAL_BLIND_MARGIN + min/16, longest linear run (1-tap holes closed), eye truncated at tap 0 extrapolated with the 32-taps-per-bit period, blind framing alignment (best of 4 framings per lane) before and after each of 2 passes; CAL_BLIND_MIN read-back (register map 0x4..0x10) |

Datasheet facts used (AD9484.pdf, re-checked): LVDS SDR, DCO at the sample rate (400 MHz), data valid
on the rising DCO edge, tSKEW -0.07..+0.07 ns (tPD 0.85 / tCPD 0.6 ns typ), offset binary.

Resource estimate for mode 1 (XC7A50T): 8 ISERDESE2 + 8 IDELAYE2 + 1 IDELAYCTRL (bank 14), 1 BUFIO +
1 BUFR, 1 MMCME2 (of 5) + 1 BUFG, 8 DSP48E1 for the mixers (9x16) + 64 DSP48E1 for the two
unchanged 32-tap FIRs (of 120), CIC adder trees in LUTs (~16 constant multiplies per I/Q), 1 BRAM18
for the 32-bit FIFO (or distributed RAM), small ROM for the 65-entry sine table. The 400 MHz
fabric path (mode 0) is kept only for comparison.

Remaining risks / what to check in Vivado (mode 1):
* BUFR (DCO/4) versus clk_100m (AD9523 OUT6): same nominal frequency, unknown phase; the FIFO
  absorbs phase/jitter, `cal_status[15]` (FIFO overflow) must stay 0 on hardware. If the two clocks
  are not frequency-locked the design needs a re-sampler (not present).
* IDELAYCTRL placement: all IDELAYE2 and the IDELAYCTRL must be in bank 14 (`IODELAY_GROUP` set in
  the XDC); the 200 MHz reference comes from the MMCM through a BUFG.
* Bank 14 is 3.3 V: LVDS_25 inputs only with `DIFF_TERM FALSE` and external 100 Ohm termination
  (design conflict kept visible in the XDC).
* ISERDESE2 Q1..Q4 bit order: resolved from UG471 (see "UG471 checks" below) - `Q1_IS_OLDEST = 0`
  (first bit received on Q4, newest on Q1) in RTL, receiver and TB, and the simulation model was
  corrected to the same order; still confirm on hardware with the ADC PN9 pattern (0x0D = 0x06)
  against a PN9 generator. BUFR framing (which DCO edge starts a 4-sample word) is irrelevant for
  the data path (common rotation of all lanes) and is absorbed by the per-lane alignment.
* Blind calibration limits (`adc_capture_calib.v` header): single CW tone at the programmed
  frequency with every bit toggling (>= ~64 LSB peak for bit 7); the LSB lanes need <= ~1 LSB rms
  input noise at the default 512-word window (0.7 LSB rms in the TB; AD9484 ~47 dB SNR = ~0.5 LSB
  rms) - at 1.4 LSB rms lane 0 reports `undetermined` and keeps its tap; the eye-centre
  extrapolation for runs cut at tap 0 assumes exactly 32 taps per bit (400 MSPS, 78.125 ps/tap)
  and a 5-tap metastable region (`FAIL_HALF = 2`, the simulation model's 0.4 ns; the hardware
  value is unknown, an error of e taps moves the centre by e); the blind framing alignment takes
  the minimum of four metrics without a significance test (`align_fail` stays 0). Run time
  ~3.3 ms (2 passes x 8 lanes x 32 taps x 528 clk_div cycles + 3 alignments).
* Checks after implementation: `report_clock_interaction` (clk_div <-> clk_100m only through the
  FIFO, adc_dco/clk_div/clk_200m as derived clocks), `report_timing_summary` for the clk_div and
  clk_200m paths, `report_cdc`, `report_io`; on hardware: run the auto calibration with the ADC test
  pattern, read `CAL_STAT`/`CAL_LANE_INFO` per lane (windows should be ~27 of 32 taps wide at
  400 MSPS), then switch to normal data and check `CAL_ERR` stays 0 while the pattern check is off.

## UG471 checks (v1.10, `build/docs_ext/ug471.txt` = pdftotext of the web-archive copy, 2026-10-09)

Verbatim quotes used to settle two open points; the simulation model and the RTL default were
changed where they disagreed (CHANGELOG "Command set v2, blind calibration, UG471").

1. ISERDESE2 output order, section "ISERDESE2 Ports - Registered Outputs - Q1 to Q8" (p. 146):
   *"The first data bit received appears on the highest order Q output. The bit ordering at the
   input of an OSERDESE2 is the opposite of the bit ordering at the output of an ISERDESE2 block,
   as shown in Figure 3-3. For example, the least significant bit A of the word FEDCBA is placed at
   the D1 input of an OSERDESE2, but the same bit A emerges from the ISERDESE2 block at the Q8
   output. In other words, D1 is the least significant input to the OSERDESE2, while Q8 is the
   least significant output of the ISERDESE2 block."* (OSERDESE2 section, p. 161: *"data on the D1
   input pin is the first bit transmitted"*). For the 1:4 SDR configuration the first (oldest) bit
   is therefore on **Q4**, the newest on **Q1** -> `Q1_IS_OLDEST = 0`, `word[7:0] = Q4` (s0 = oldest).
   The sim model had Q1 = oldest and was corrected.
2. BITSLIP in SDR mode, section "BITSLIP Submodule - Bitslip Operation" (p. 158): *"By asserting
   the Bitslip pin of the ISERDESE2 block, the incoming serial data stream is reordered at the
   parallel side. ... (Bit 8 of an input ISERDESE2 is the first bit received.) ... The Bitslip
   operation is synchronous to CLKDIV. In SDR mode, every Bitslip operation causes the output
   pattern to shift left by one. In DDR mode, every Bitslip operation causes the output pattern to
   alternate between a shift right by one and shift left by three."* and *"Although the repeating
   pattern seems to show that bitslip is a barrel shifting operation, this is not the case. A
   bitslip operation adds one bit to the input data stream and loses the nth bit in the input data
   stream."* Figure 3-11 (SDR): initial 10010011 -> after one Bitslip 00100111 (Q8..Q1 notation),
   i.e. the word boundary moves one bit later in the serial stream. "Guidelines for Using the
   Bitslip Submodule" (p. 159): *"In NETWORKING mode the Bitslip submodule is available. ... the
   BITSLIP port must be asserted High for one CLKDIV cycle. Bitslip cannot be asserted for two
   consecutive CLKDIV cycles; ... the total latency ... is two CLKDIV cycles. ... The user logic
   should wait for at least two CLKDIV cycles in SDR mode ... before analyzing the received data
   pattern"* - `adc_capture_calib` pulses BITSLIP for one cycle with >= 1 idle cycle between
   pulses and waits SETTLE = 16 cycles; the sim model's slip direction was corrected to Fig. 3-11.
3. LVDS_25 inputs in a 3.3 V HR bank, section "LVDS and LVDS_25 (Low Voltage Differential
   Signaling)" (p. 92): *"It is acceptable to have differential inputs such as LVDS and LVDS_25 in
   I/O banks that are powered at voltage levels other than the nominal voltages required for the
   outputs of those standards (1.8V for LVDS outputs, and 2.5V for LVDS_25 outputs). However,
   these criteria must be met: - The optional internal differential termination is not used
   (DIFF_TERM = FALSE, which is the default value). - The differential signals at the input pins
   meet the VIN requirements in the Recommended Operating Conditions table of the specific device
   family data sheet. - The differential signals at the input pins meet the VIDIFF (min)
   requirements in the corresponding LVDS or LVDS_25 DC specifications tables of the specific
   device family data sheet. - For HR I/O banks in bidirectional configuration, internal
   differential termination is always used."*; Figure 1-72 text: *"RDIFF provides the 100 Ohm
   differential receiver termination because the internal DIFF_TERM is set to FALSE."*; Table 1-55
   note 1a: *"The optional internal differential termination is not used (DIFF_TERM = FALSE, which
   is the default value) unless the VCCO voltage is at the level required for outputs."*;
   "Differential Termination Attribute" (p. 49): *"The VCCO of the I/O bank must be connected to
   1.8V for LVDS, and 2.5V for the other differential I/O standards to provide 100 Ohm of effective
   differential termination. DIFF_TERM is only available for inputs and can only be used the
   appropriate VCCO voltage."* -> the XDC keeps `LVDS_25` + `DIFF_TERM FALSE` on the nine bank-14
   pairs and states that an external 100 Ohm termination at the FPGA (absent on the schematic) and a
   VIN/VIDIFF/VICM check of the AD9484 output against DS181 are REQUIRED (board change / verification).

## Constraints (`constraints/radar_system_top_beta.xdc`)

* Pins: verbatim schematic-derived candidates for 64 ports / 64 bits (`PIN_MAP_FROM_SCHEMATIC.md`),
  every ball still to be cross-checked against the AMD FTG256 package file and the final layout.
* Clocks: `create_clock` for clk_100m (10 ns), clk_120m_dac (8.333 ns), adc_dco (2.5 ns),
  ft601_clk_in (10 ns, no pin); `set_clock_groups -asynchronous` for all four; false paths for the
  asynchronous STM32 lines and the SPI pass-through; `set_input_delay` for the ADC bus from the
  datasheet skew plus an **unverified** +/-0.25 ns board allowance (both edges, falling-edge capture).
* **Design conflict kept visible:** bank 14 is 3.3 V on the schematic; the LVDS_25 ADC inputs are
  therefore constrained with `DIFF_TERM FALSE` (external 100 Ohm termination required - option A,
  REQUIRES VERIFICATION; the UG471 criteria are quoted verbatim in the XDC header) and the
  `DIFF_TERM TRUE` lines are left commented as option B (bank VCCO change). `CFGBVS VCCO` / `CONFIG_VOLTAGE 3.3` set from the bank-0 supply.
* Host-link option B pins H11/G12/H12 (DIG_5..7, bank 15, LVCMOS33) added; `spi_sclk` (37 ns)
  is a fifth asynchronous clock group.
* UNRESOLVED (116 bits, listed at the end of the file, unconstrained): `dac_clk` (DAC is clocked by
  AD9523 OUT10, not by the FPGA), all `ft601_*` (FT601 U6 has 0/77 pins connected), `current_*`,
  `new_chirp_frame`, `dbg_*`, `system_status` (no board nets). `write_bitstream` will refuse the
  unconstrained I/O unless they are removed from the top or `UNCONSTRAINEDPINS ALLOW` is set for a
  resource/timing trial only.

## Host path

**Option B (implemented, BETA): SPI bridge on the STM32 SPI1 bus.** `rd_map_packer` turns each
64 x 32 Doppler frame into a 2066..2162-byte frame (header, 2048 x uint8 log-magnitude, up to 32
detections, CRC-16/CCITT-FALSE; layout in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` section
5) and `host_bridge_spi` streams it to the STM32 as an SPI slave (mode 0, MSB first, <= 27 MHz) on
the existing SCLK/MOSI/MISO nets with DIG_5 = `spi_bridge_cs_n` (H11), DIG_6 = `spi_bridge_drdy`
(G12), DIG_7 = `spi_bridge_spare` (H12, packer overflow flag). While the bridge CS is low the
ADAR1000 pass-through is gated (CS high, SCLK/MOSI idle on the 1.8 V side) and MISO is driven by
the bridge; `system_status[1]` latches a conflict if any ADAR CS is low during a transfer. Beam
indices come from the transmitter's STM32-toggle counters (synchronised), the chirp count from the
receiver's chirp pulses, `long_chirp` from the register map. Verified by `tb_host_bridge_top`
(frame read end to end through the top, see table). Firmware side: STM32 PD13 must become an
output (`main.cpp:2313-2317` configures PD13..15 as inputs), see `engineering/DESIGN/HOST_LINK/stm32`.
**Command set v2** (`host_bridge_spi.v`, `HOST_LINK_DESIGN.md` section 7, firmware
`beta/stm32/Core/Src/host_bridge_proto.c`): 0x01 frame read (unchanged), 0x02 register write
(`02 a0 a1 d0 d1 d2 d3 00`, ack 0xA2 in byte 7), 0x03 register read (`03 a0 a1 00 00 00 00`, value
little-endian in bytes 3..6, no turnaround byte: the read is launched when a0 is complete), 0x04
status (8 reply bytes: status word / RTL version 0x0002 / frames produced / 0), unknown command ->
0xEE. The bridge drives the register map's write/read port (5-bit addresses, 16-bit data); the
status word is assembled in the top (bit0 DRDY, bit1 ADAR CS conflict, bit2 capture FIFO overflow,
bit3 all-lanes calibration lock, bit4 packer overflow). Register toggles cross SCLK -> clk through
3-flop synchronisers; a read needs the >= 8 SCLK periods between a0 and d0 (>= 296 ns at 27 MHz,
the fetch takes <= 5 clk cycles); the 0x04 values are sampled in the SCLK domain (quasi-static).
Unresolved for option B: STM32 SPI1 timing versus the FPGA pins (XDC placeholders), BRAM inference
of the SCLK-domain frame RAM read (`host_bridge_spi.v`, asynchronous read registered on falling
SCLK), and the firmware rule that no ADAR1000 transaction overlaps a bridge read.

**Option A (kept unchanged, Main Board rev. B): FT601.** The RTL's original host interface is an FT601 slave-FIFO packetiser. On the Main Board the FT601 is placed but
not wired, and the STM32 reaches the FPGA only via `DIG_0..7` and the SPI1 pass-through (no chip
select for the FPGA). The beta keeps `usb_data_interface` (packet format defined in its header,
checked by `tb_system_smoke`) running on clk_100m so the data path can be simulated; a real FT601
needs the FSM re-timed to `ft601_clk` through `async_fifo`. Any other host path (SPI slave on
`DIG_5..7`, STM32 USB-FS forwarding, a wired FT601) is a board + firmware decision; the register
map's write port is the hook for it.

## Remaining work (ordered)

1. **Generate the two FFT IP cores** per `ip/README.md`, run `tb_fft_wrappers` against the IP
   simulation models (adjust `TOL` if the IP's per-stage rounding differs), record the IP latency
   and check `FFT_WAIT_TIMEOUT` in `doppler_processor.v`.
2. **Synthesis / implementation** with `vivado/create_project.tcl` + `vivado/build.tcl`
   (default part `xc7a50tftg256-2` = schematic U42; README/XDC claim XC7A100T - resolve first).
   Expect resource pressure: two 1024-point FFT IPs, 2 x 32 parallel 18x18 multipliers in the FIR
   (`fir_lowpass.v`, 64 DSP48E1 of the 50T's 120), 400 MHz fabric logic (next item).
3. **400 MHz fabric path replaced** (`ADC_CAPTURE_MODE = 1`, see "ADC capture and DDC front
   end"): ISERDESE2 SDR 1:4 + BUFR/4 + IDELAY calibration and a polyphase DDC at 100 MHz, bit-exact
   with the legacy path in simulation. Remaining: Vivado timing on the clk_div/clk_200m paths,
   IDELAYCTRL/IODELAY_GROUP placement, hardware calibration with the ADC test pattern, Q1..Q4 order.
4. **Matched-filter throughput.** The chain is not pipelined against the collector: one long chirp
   (4 segments) occupies the FSM for ~92 us with the behavioural FFT latency (160 clocks) and
   ~270 us with a realistic IP latency (~2.3k clocks per transform), while the TX repeats long chirps
   every 167 us (`plfm_chirp_controller.v`: 30 us chirp + 137 us listen). Samples arriving while the
   FSM is not in `ST_COLLECT_DATA` are dropped (original behaviour). Needs ping-pong buffering or
   overlapping collect/process; the smoke test uses a 300 us period for this reason.
5. **Segment semantics.** Each 1024-sample segment is compressed against its own reference segment
   and produces its own 64-bin profile; the four profiles per chirp are not summed, and the Doppler
   processor counts each profile as a "chirp" (a 32-"chirp" frame = 8 real chirps). Decide whether to
   sum the partial correlations (true partitioned matched filter) or to use a 4096-point transform.
6. **Hardware bring-up items** (all UNRESOLVED): confirm the chirp direction / `CONJUGATE_REF`;
   AD9484 capture edge and trace skew; bank-14 LVDS termination; ADC test pattern check; DAC data
   timing versus the externally clocked AD9708 (`dac_clk` has no pin); STM32 SPI1 clock rate versus
   the 1-cycle SPI pass-through re-timing; the short-chirp reference; the FT601/host decision.
7. CFAR (the detector is still a fixed threshold, default 10000 via `CFAR_THRESHOLD_DEFAULT`, now
   writable over the bridge as CFAR_THR); removal of the 116 unconstrained debug/status bits from
   the top before a board build. (Register-map host interface: done, command set v2; `det_wr`
   back-port: done - `engineering/DESIGN/HOST_LINK/rtl/` carries the v2 bridge and the extended unit TB.)
8. GUI `beta/gui/aeris10_gui/protocol/register_map.py` still assumes 4-bit addresses (`ADDR_MASK = 0xF`)
   and carries a "DISCREPANCY" note about section 7 that is now resolved; it needs 0x04 bit4,
   0x0D, 0x0E, 0x10 and a 5-bit address mask.

## Known limitations of the beta (summary)

* Not synthesised, no timing, no hardware test; FFT IP not generated (fail-loud placeholders).
* Behavioural FFT models are not bit-exact with the Xilinx IP (total-shift scaling, round-half-up;
  TB tolerance +/-2 LSB) and their latencies (72 / 160 clocks) are placeholders.
* `rtl/sim/unisim_sim_models.v` models only the behaviour the design uses (no timing, IB ignored).
* USB packetiser runs on clk_100m and drops records that arrive while a packet is in flight
  (counted internally); 11-word packet format is a beta definition.
* The level-shifter pass-through adds one clk_100m cycle to SCLK/MOSI/CS and two to MISO.
* `use_long_chirp` is a register bit (default 1); the TX sequence's long/short alternation is not
  mirrored automatically in the receiver.
