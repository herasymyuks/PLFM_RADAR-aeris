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
├── rtl/                     synthesisable Verilog-2001 (28 files)
│   ├── sim/unisim_sim_models.v   BUFG/IBUFDS/IDDR stand-ins (simulation + lint only)
│   └── unused_orig/              5 untouched originals that are no longer compiled (+README)
├── mem/                     8 original .mem copies + generated long_chirp_seg3_{i,q}.mem
├── tb/                      4 self-checking testbenches, gen_vectors.py, vectors/, original TB (reference)
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

## What passed (last run 2026-10-09, logs in `logs/`)

| Step | Command (from `build.sh`) | Result | Log |
|---|---|---|---|
| 1 | `iverilog -g2005 -DSIM -s radar_system_top rtl/*.v rtl/sim/unisim_sim_models.v` | PASS | `logs/iverilog_top_sim.log` |
| 2 | `iverilog -g2005 -s radar_system_top ...` (synthesis view) | PASS | `logs/iverilog_top_synth.log` |
| 3a | `verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top ...` (synth view) | PASS, **0 %Error, 113 %Warning** | `logs/verilator_synth.log` |
| 3b | same with `-DSIM` | PASS, **0 %Error, 106 %Warning** | `logs/verilator_sim.log` |
| 4 | `python3 gen_chirp_mem.py` | PASS: seg0/1/2 reproduced within 1 LSB, seg3 written | `logs/gen_chirp_mem.log` |
| 5 | `python3 tb/gen_vectors.py` | PASS | `logs/gen_vectors.log` |
| 6a | `tb_fft_wrappers` - xfft_32 (4 frames incl. back-pressure) and FFT_enhanced (fwd + inv) vs numpy | PASS: 2176 samples within +/-2 LSB | `logs/tb_fft_wrappers.run.log` |
| 6b | `tb_matched_filter` - chain + memory, reference chirp delayed 300 samples | PASS: peak at bin 302 (300 +/-4), peak/sidelobe 4.76 | `logs/tb_matched_filter.run.log` |
| 6c | `tb_range_bin_decimator` - 2 x 1024 bins (one with input gaps) vs numpy, peak mode | PASS: 128/128 bins | `logs/tb_range_bin_decimator.run.log` |
| 6d | `tb_system_smoke` - full top, 10 chirps, synthetic IF echoes, 3.3 ms | PASS (65 s): see below | `logs/tb_system_smoke.run.log` |

`build.sh` summary line: `0 failure(s), 219 verilator warning line(s) (both views)`.

System smoke test evidence (`logs/tb_system_smoke.run.log`): DAC left mid-scale (57540 samples);
40 range profiles (4 segments x 10 chirps); for alternating echo delays of 100 and 420 baseband
samples the segment-0 peak sat at decimated bin 8 and 28 on every chirp - a shift of 20 bins for a
320-sample delay change (320/16 = 20), i.e. pulse compression works end to end through capture ->
DDC -> matched filter -> decimator; 2048 Doppler outputs (one 64 x 32 frame); 2688 USB packets with
0 header/footer/sequence errors; no X on outputs; the matched-filter FSM was idle at every toggle.

Verilator warning breakdown (synthesis view, 113): 34 UNUSEDSIGNAL (debug/diagnostic nets of the
original, unused IP tready/tlast nets in the wrappers), 34 PINCONNECTEMPTY (monitor outputs left
unconnected on purpose), 13 WIDTHEXPAND / 4 WIDTHTRUNC (original arithmetic widths, e.g.
`plfm_chirp_controller.v` 16-bit counter indexing a 3600-entry LUT), 12 UNUSEDPARAM (original
parameters such as `F_START`, `IF_FREQ`), 9 DECLFILENAME (original file names differ from module
names - kept so the docs stay valid), 4 PROCASSINIT (sim models), 3 GENUNNAMED (original `generate`
in `lfsr_dither_enhanced`). None was hidden with a global `-Wno-*`; the few local `lint_off` pragmas
are documented in the source next to the reason.

Additional checks: `tools/check_fpga_constraints.py --top beta/fpga/rtl/radar_system_top.v --xdc
beta/fpga/constraints/radar_system_top_beta.xdc` -> 0 placeholders, 0 invalid properties, 64/180
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
   now have one driver with documented reset defaults. Its write port is tied off because the board
   offers no host write path (see "Host path").

## Constraints (`constraints/radar_system_top_beta.xdc`)

* Pins: verbatim schematic-derived candidates for 64 ports / 64 bits (`PIN_MAP_FROM_SCHEMATIC.md`),
  every ball still to be cross-checked against the AMD FTG256 package file and the final layout.
* Clocks: `create_clock` for clk_100m (10 ns), clk_120m_dac (8.333 ns), adc_dco (2.5 ns),
  ft601_clk_in (10 ns, no pin); `set_clock_groups -asynchronous` for all four; false paths for the
  asynchronous STM32 lines and the SPI pass-through; `set_input_delay` for the ADC bus from the
  datasheet skew plus an **unverified** +/-0.25 ns board allowance (both edges, falling-edge capture).
* **Design conflict kept visible:** bank 14 is 3.3 V on the schematic; the LVDS_25 ADC inputs are
  therefore constrained with `DIFF_TERM FALSE` (external 100 Ohm termination required - option A,
  REQUIRES VERIFICATION) and the `DIFF_TERM TRUE` lines are left commented as option B (bank VCCO
  change). `CFGBVS VCCO` / `CONFIG_VOLTAGE 3.3` set from the bank-0 supply.
* UNRESOLVED (116 bits, listed at the end of the file, unconstrained): `dac_clk` (DAC is clocked by
  AD9523 OUT10, not by the FPGA), all `ft601_*` (FT601 U6 has 0/77 pins connected), `current_*`,
  `new_chirp_frame`, `dbg_*`, `system_status` (no board nets). `write_bitstream` will refuse the
  unconstrained I/O unless they are removed from the top or `UNCONSTRAINEDPINS ALLOW` is set for a
  resource/timing trial only.

## Host path (FT601 absent)

The RTL's host interface is an FT601 slave-FIFO packetiser. On the Main Board the FT601 is placed but
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
3. **400 MHz processing is not realistic in Artix-7 fabric.** NCO, 18x16 mixer, five 36-bit CIC
   integrators and the FIFO write side run at the DCO rate. The capture is correct in simulation,
   but timing closure at 2.5 ns is very unlikely; the production structure is ISERDESE2 (SDR, 2 bits)
   + BUFR/2 giving two samples per 200 MHz clock, with the DDC reworked for 2 samples/cycle, plus
   IDELAYE2/IDELAYCTRL for data centring. The beta keeps the original single-rate architecture so
   the documentation stays valid.
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
7. Register-map host interface; CFAR (the detector is still a fixed threshold); removal of the 116
   unconstrained debug/status bits from the top before a board build.

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
