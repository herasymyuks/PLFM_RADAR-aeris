# beta/fpga CHANGELOG - every difference versus `9_Firmware/9_2_FPGA/`

Status of everything in `beta/fpga`: **BETA** - parses, elaborates, lints and simulates with
Icarus Verilog 13.0 / Verilator 5.052; **not synthesised** (no Vivado available) and **not tested on
hardware**. Line numbers "orig :N" refer to the unmodified files in `9_Firmware/9_2_FPGA/`
(CRLF->LF normalisation did not change line numbers); "beta :N" refers to `beta/fpga/rtl/`.
Nothing under `9_Firmware/9_2_FPGA/` was modified.

Legend: **SYN** syntax/elaboration fix, **BUG** functional defect fix, **ARCH** architecture/interface
change (documented in README), **NEW** file written for the beta, **CLEAN** lint/readability only.

## Files copied unchanged except line endings

`dac_interface_single.v`, `fir_lowpass.v`, `level_shifter_interface.v`, `ddc_input_interface.v`
(a trailing newline was added where missing). `plfm_chirp_controller.v` LUT contents unchanged.

## Files moved to `rtl/unused_orig/` (not compiled)

`ad9484_interface_400m.v`, `lvds_to_cmos_400m.v`, `cdc_modules.v`, `latency_buffer_2159.v`,
`usb_packet_analyzer.v` - see `rtl/unused_orig/README.md` for the reason per file.
`chirp_lut_init.v` (module-less `initial` fragment, orig :6) and `radar_system_tb.v`
(SystemVerilog assertions, orig :528-543) were not copied into `rtl/`; the original testbench is kept
as `tb/radar_system_tb_original.v` for reference only (not run).

## `radar_system_top.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| SYN | :312-313 | `wire [16:0] mag` moved to module scope (beta :355-357) | wire declaration inside `always` is a syntax error (iverilog/Verilator stop here) |
| SYN | :155-156 | `rx_cfar_detection`, `rx_cfar_valid` `wire` -> `reg` | assigned procedurally at :304-318 |
| ARCH | :184-187 | `BUFG bufg_ft601` removed; `ft601_clk_in` kept as an (unused) port | FT601 not wired on the board; USB FSM runs on clk_100m |
| ARCH | new | `radar_control_regs ctl_regs` instance (write port tied to 0) | single driver for use_long_chirp / adc_pwdn / CFAR threshold / decimation controls |
| ARCH | :270-286 | `rx_inst` gets the new receiver ports (STM32 toggles, register controls, range profile out, status) | receiver controls were undriven |
| BUG | :298-323 | CFAR placeholder: `rx_cfar_valid` pulses on every `rx_doppler_valid`, detection = `mag > ctl_cfar_threshold`; `rx_cfar_detection` was set and never cleared | threshold from register map; valid/detection semantics |
| BUG | :329-332 | `usb_range_profile` = real decimated range profile (`rx_range_profile_w`), `usb_*_valid` gated by `ctl_usb_enable` | original sent Doppler data "as a placeholder" |
| CLEAN | :398 | `status_reg[1]` also ORs the CDC-FIFO overflow flag | observability of lost samples |

## `radar_receiver_final.v` (rewritten; instance names and chain order kept)

| Type | orig | Change | Reason |
|---|---|---|---|
| SYN | :150 vs :192 | `sample_addr_from_chain` declared before use | use-before-declare |
| SYN | :216-217 | `.ref_i(16'd0)`, `.ref_q(16'd0)` removed | ports do not exist in `matched_filter_multi_segment` |
| SYN | :14-17 | outputs `reg` -> `wire` | driven by instance output ports |
| SYN/BUG | :21-25, :204-208 | `use_long_chirp`, `chirp_counter`, `mc_new_*` are now driven: `use_long_chirp` is an input (register map); `mc_new_*` come from three `edge_detector_enhanced` instances on the STM32 toggle inputs (new ports); `chirp_counter` is a local 0..CHIRPS_PER_FRAME-1 counter | undriven wires -> matched filter never started |
| ARCH | :59-69, :94-105 | `lvds_to_cmos_400m` instance and the first `cdc_adc_to_processing` removed; `clk_400m` = `adc_dco_cmos` from `ad9484_lvds_to_cmos_400m` | two IBUFDS on the same pins are illegal; flop-derived clock (orig lvds_to_cmos_400m.v:35-43) is not a clock |
| ARCH | new | `reset_synchronizer rst_sync_400m` -> `ddc.reset_n_400m` | synchronous reset release in the 400 MHz domain |
| ARCH | :168-189 | `latency_buffer_2159` removed; `long/short_chirp_*` fed directly from the memory outputs | reference now fetched by address at FFT-output time (see processing chain) |
| BUG | :125-126 | `ddc.mixers_enable` stays 1'b1; `bypass_mode` now from port `ddc_bypass` (top ties 0) | original tied `bypass_mode = 1'b1` to an unimplemented test input |
| BUG | :201-202 | `ddc_i = {adc_i_scaled, 2'b00}` instead of sign extension | the multi-segment filter stores `ddc_i[17:2]`; sign extension lost 2 LSB (/4) |
| BUG | :244-283 | frame-sync: pulse on the first chirp of every CHIRPS_PER_FRAME (32) chirps | original compared an undriven counter against 0/32 |
| ARCH | new | outputs `range_profile_out/valid/bin`, `rx_chirp_counter`, `new_chirp_frame`, `cdc_overflow` | host path and observability |
| CLEAN | :320-349 | debug `$display` block removed | uninitialised counters, noise |

## `radar_transmitter.v` (rewritten; ports unchanged)

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :93-112 | edge detectors clocked by `clk_120m_dac` | their pulses are consumed by the clk_120m FSM; a 10 ns pulse sampled at 120 MHz is unsafe |
| BUG | :59-71 | four `level_shifter_interface` instances drive `stm32_*_1v8` / `stm32_miso_3v3` | outputs were undriven (module was an orphan) |

## `plfm_chirp_controller.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :563-576 | clk_100m `chirp_counter` block deleted (beta :566-569) | second driver of `chirp_counter` (also written at :683-784 on clk_120m) |
| BUG | :580, :597 | elevation/azimuth counters clocked by `clk_120m` | single clock domain for the TX controller |
| CLEAN | :5 | `clk_100m` port kept, marked unused | interface compatibility |

## `edge_detector.v` (rewritten; ports unchanged)

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :16-23 | two ASYNC_REG synchroniser flops + history flop; edge from stage 2 | edge was taken from the first synchroniser stage |

## `ddc_400m.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| SYN | :252-266 vs :272-275 | `fir_*` wires declared before the CDC instances | use-before-declare |
| ARCH | new port | `reset_n_400m` for NCO/mixer/CIC/dither; control inputs double-synchronised | async reset release in the 400 MHz domain |
| ARCH | :243-267 | `cdc_adc_to_processing` x2 -> `async_fifo` x2 (Gray pointers, depth 16) + `cdc_overflow` output | Gray-coding data words is not a CDC |
| BUG | :117-125 | `reset_monitors` removed from the async reset condition (synchronous now); `saturation_count` written only in the mixer block | data-dependent async reset; multi-driven register |
| BUG | :156 | NCO `phase_valid` from `mixers_enable_sync` | raw asynchronous input used as an enable |
| BUG | :306 | output stage on `posedge clk_100m` | negedge register halves the timing budget |
| BUG | :21 | `bypass_mode` implemented (mixer bypass, I = adc, Q = 0) | input existed but did nothing |
| BUG | :19 | `filter_overflow` driven from the two FIR overflow flags | undriven output |
| CLEAN | :223-240 | CIC monitor pins connected explicitly | PINMISSING |
| CLEAN | :332-371 | debug `$display` blocks removed | uninitialised counters |

## `cic_decimator_4x_enhanced.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :71, :181, :291 | `saturation_detected` = `int_saturation` (integrator block) OR `comb_saturation` (comb block); `overflow_latched`/`saturation_event_count` split likewise; `always @(posedge reset_monitors)` block deleted; `data_valid_comb` written only in its pipeline block (:77 removed) | three/two drivers per register, control input used as a clock |
| ARCH | :9 | `saturation_detected` `output reg` -> `output wire` | OR of two flags |

## `nco_400m_enhanced.v` (rewritten; ports and 2-cycle latency unchanged)

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :34-49 | 65-entry table `sin(90deg*i/64)` (generated, monotonic, ends at 0x7FFF) | original table peaks at index 42 and ends at 0x3B71 (not a sine) |
| BUG | :54, :58 | mirroring on `quadrant[0]`; `cos = lut[64-idx]` | mirrored on `quadrant[1]`; `lut[63-idx]` is one step off |
| CLEAN | :111-115 | `initial $display` removed | |

## `chirp_memory_loader_param.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| SYN | :3-12 | absolute Windows paths -> `mem/<file>.mem` | files did not exist; `long_chirp_seg3_*.mem` generated (`gen_chirp_mem.py`) |
| CLEAN | :104 | `long_addr` is a wire | blocking assignment in a clocked block |
| CLEAN | :13, :64-65 | `DEBUG` default 0; explicit `$readmemh` range 0..49 for the short chirp | noise / warning |

## `matched_filter_multi_segment.v` (rewritten; ports, states, parameters kept)

| Type | orig | Change | Reason |
|---|---|---|---|
| ARCH | :60-61, :329-332 | circular 1024-entry RAM, overlap = pointer move (`blk_start += 896`) | per-cycle copy of 128 entries forced 2x1024x16 flip-flops |
| ARCH | :199 | first block waits for 1024 samples (not 896 + unwritten tail) | undefined data in the block |
| ARCH | :27-29, :265 | `mem_request`/`segment_request`/`sample_addr_out` multiplexed between the FSM priming request and the processing chain's `ref_addr` requests; no per-sample request while feeding | reference fetched at FFT-output time |
| ARCH | :361-386 | chain instance gets `segment_in`, `use_long_chirp`, `ref_addr`, `ref_req` | new chain interface |
| CLEAN | :47 | `DEBUG` default 0; every `$display` gated | simulation noise |
| CLEAN | :165 | `LONG_SEGMENTS[2:0]` part-select -> sized localparams | part-select of an unsized parameter |

## `frequency_matched_filter.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :26-27, :85-86 | `CONJUGATE_REF` parameter (default 1 = original); the chain uses 0 | the memories already hold `conj(FFT(chirp))`; a second conjugation turns the correlation into a convolution (verified: no compression peak with the original form, peak at the injected delay with `CONJUGATE_REF = 0`) |

## `fft_1024_forward.v`, `fft_1024_inverse.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :38-58 | `tlast` counter counts every valid sample (first sample was not counted) | tlast one sample late -> stray tlast -> an extra zero-filled FFT frame per block (observed in simulation: 8192 outputs for 4096 inputs) |
| BUG | :28 | `SCALE_SCH` parameter; config = `{5'b0, SCALE_SCH, FWD_INV}` (fwd default 2^-6, inv 2^-5) | fixed `16'h0001`/`16'h0000` = no scaling -> 16-bit overflow |
| CLEAN | inverse :66-75 | uninitialised debug counter removed | |

## `doppler_processor.v`

| Type | orig | Change | Reason |
|---|---|---|---|
| BUG | :217-229 | `fft_input_valid/last` delayed one cycle (`load_valid_p/load_last_p`) | valid asserted before the registered product was ready: first word stale, tlast early |
| BUG | :238 | `processing_timeout <= FFT_WAIT_TIMEOUT` (1000) | 100 cycles < FFT latency + 32 outputs |
| BUG | :286 | `FFT_CONFIG_WORD` parameter, default `8'h35` (forward, 2^-5) | `8'h01` = no scaling |
| CLEAN | :159, :245, :283 | `default` case; `doppler_bin <= fft_sample_counter[4:0]`; `.s_axis_data_tready()` | CASEINCOMPLETE, width, PINMISSING |

## `usb_data_interface.v` (rewritten; ports unchanged)

| Type | orig | Change | Reason |
|---|---|---|---|
| SYN | :46-56 | `typedef enum` -> localparams | SystemVerilog in a `.v` file |
| BUG | :65-79 vs :176-182 | `ft601_clk_out` single driver | two always blocks on different clocks |
| ARCH | :65 | FSM on `clk` (100 MHz); payload latched at packet start; fixed 11-word packet | inputs were sampled across clock domains without synchronisation and the FSM waited for one-cycle valids on every word; FT601 has no hardware (see README "Host path") |
| BUG | :20-21 | `ft601_txe_n/rxf_n` driven inactive | they are FT601 outputs per the datasheet |

## New files (`NEW`)

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

## Host-link option B integration (follow-up, 2026-10-09)

Source: `engineering/DESIGN/HOST_LINK/` (HOST_LINK_DESIGN.md section 5, `option_b_signal_map.csv`,
`rtl/rd_map_packer.v`, `rtl/host_bridge_spi.v`, `rtl/tb_host_bridge.v`). Originals untouched.

| Type | File | Change | Reason |
|---|---|---|---|
| NEW | `rtl/host_bridge_spi.v` | byte-identical copy of `engineering/DESIGN/HOST_LINK/rtl/host_bridge_spi.v` | SPI slave + 2-bank frame RAM |
| NEW/BUG | `rtl/rd_map_packer.v` | copy with one fix: `det_wr` widened `[5:0]` -> `[6:0]` (beta :44) | the detection-list write counter must reach `3*MAX_DET = 96`; with 6 bits the packer never left its header/detection state once `n_det >= 22` (frame never completed, DRDY never asserted). Found by `tb_host_bridge_top` (91 detections); the source unit test uses 3 detections. **To be back-ported to `engineering/DESIGN/HOST_LINK/rtl/rd_map_packer.v`.** |
| NEW | `tb/tb_host_bridge.v` | copy of the source unit test; only the dump path changed to `logs/tb_frame.hex` | runs inside `build.sh` from `beta/fpga` |
| NEW | `tb/tb_host_bridge_top.v` | top-level test: behavioural SPI master (mode 0, 25 MHz) reads one frame after DRDY in the smoke scenario; checks sync/version/flags/az-el/chirp-count/dims/n_det/2048 map bytes/detection entries/CRC/DRDY-clear/consumed/overflow, pass-through gating during the transfer and pass-through operation after it | requested by the coordinator |
| ARCH | `rtl/radar_system_top.v` | new ports `spi_bridge_cs_n` (in), `spi_bridge_drdy` (out), `spi_bridge_spare` (out); instances `rd_packer` (`rd_map_packer`) and `host_bridge` (`host_bridge_spi`) on the shared SPI1 lines; `stm32_miso_3v3 = bridge_active ? bridge_miso : passthrough_miso_3v3`; `spi_bridge_spare = packer overflow`; sticky `bridge_cs_conflict` (any ADAR CS low while the bridge CS is low) ORed into `system_status[1]`; new parameter `CFAR_THRESHOLD_DEFAULT` (default 10000, passed to the register map) | option B bridge; RTL check demanded by `option_b_signal_map.csv`; the TB lowers the threshold to exercise detections |
| ARCH | `rtl/radar_system_top.v` | cell stream to the packer: Doppler I/Q delayed one clock so that they line up with `rx_cfar_valid/detection` (which lag `rx_doppler_valid` by one clock); `cell_valid = rx_cfar_valid`, `cell_det = rx_cfar_detection`; `frame_start` = undelayed first cell (`range_bin == 0 && doppler_bin == 0`), one clock before the delayed first cell as the packer requires | the Doppler stream is range-major (64 x 32) exactly as the packer expects |
| ARCH | `rtl/radar_system_top.v` | `az_idx/el_idx` = transmitter counters `current_azimuth/elevation` (clk_120m domain) through a 2-flop synchroniser + "two equal samples" filter; `chirp_count` = 16-bit count of receiver chirp-counter changes (clk_100m); `long_chirp` = register-map `use_long_chirp` | the TX STM32-toggle counters are the only beam-position source in the design (the register map has no az/el field); they change milliseconds apart so the stability filter is sufficient |
| ARCH | `rtl/radar_transmitter.v` | new input `spi_passthrough_gate`; while high the level-shifter inputs are forced idle (`cs_3v3 | gate`, `sclk/mosi & ~gate`) so the ADAR1000 CS stay high and SCLK/MOSI are quiet on the 1.8 V side; `stm32_miso_3v3` output now carries only the pass-through MISO (muxed at the top) | bridge transfers on the shared bus must not reach the beamformers |
| — | `rtl/usb_data_interface.v` | unchanged | option A path kept for Main Board rev. B |
| XDC | `constraints/radar_system_top_beta.xdc` | `PACKAGE_PIN H11/G12/H12` + `LVCMOS33` (+ `PULLUP` on CS) for the three bridge ports (bank 15, nets DIG_5/6/7 exist on the board); `create_clock spi_sclk` 37 ns on `stm32_sclk_3v3` added to the asynchronous clock groups; the pass-through false paths narrowed to the `ls_adar*` cells; bridge input/output delays left as commented placeholders (STM32 SPI1 timing + trace delays UNRESOLVED); DIG_5..7 removed from the "no RTL port" list | option B pins |
| — | `build.sh` | no logic change (picks up `tb/tb_*.v`); header lists the two new testbenches | |

## ISERDES capture + polyphase DDC (follow-up, 2026-10-09) - `ADC_CAPTURE_MODE`

Datasheet re-check (`AD9484.pdf`, Table 4 / "Output Data Rate" / register map): LVDS **SDR**, DCO at
the sample clock rate, data valid on the rising DCO edge, tSKEW -0.07..+0.07 ns, tPD 0.85 ns,
tCPD 0.6 ns, latency 15 clocks; test modes in register 0x0D[3:0] (0100 checkerboard, 0101 PN23,
0110 PN9, 0111 one/zero toggle, 1000 user defined with 0x0D[7:6] = 01 "toggle P1/P2", P1 =
0x19/0x1A, P2 = 0x1B/0x1C); output format offset binary by default (0x14).

| Type | File | Change | Reason |
|---|---|---|---|
| NEW | `rtl/ad9484_iserdes_capture.v` | IBUFDS(DCO) -> BUFIO + BUFR/4; 8 x IBUFDS -> IDELAYE2 (VAR_LOAD, tap from `adc_capture_calib`) -> ISERDESE2 (SDR 1:4, NETWORKING, IOBDELAY IFD); IDELAYCTRL on `clk_200m_ref`; 4 x 8-bit word per clk_div cycle + valid; `async_fifo` (32-bit) into clk_100m; `fifo_overflow` sticky; `Q1_IS_OLDEST` parameter | no fabric logic at 400 MHz; SDR per datasheet (DDR 1:8 not needed) |
| NEW | `rtl/adc_capture_calib.v` | calibration FSM in the clk_div domain: default taps (16) after reset; manual tap / bitslip per lane; auto sweep taps 0..31 (SETTLE 16, MEAS 64 words, per-lane pass mask, longest circular run, centre tap, lock if run >= MIN_WINDOW 4 and < 32, undetermined for constant pattern bits); lane alignment pass (rotation majority, BITSLIP for minority lanes, `align_fail`); word-level pattern error counter | per-lane eye centring and framing consistency; see header for the AD9484 SPI writes the host must do (SPI path UNRESOLVED on the schematic) |
| NEW | `rtl/ddc_4x_100m.v` | 4-phase NCO (same FTW, table, quadrant logic and dither sequence as the legacy path, LFSR unrolled 4 steps/clock), 8 x (9x16) mixers bit-exact to `mixed[33:16]`, CIC/4 as the 16-tap FIR (1+z^-1+z^-2+z^-3)^5 >> 10 saturated (`CIC_PHASE` 0 = legacy decimation phase), the two unchanged `fir_lowpass_parallel_enhanced`, registered output with the legacy valid semantics | 100 MHz implementation of the 400 MHz mixer + CIC; `tb_ddc_4x`: max diff **0 LSB** vs the legacy over 1855 outputs |
| NEW | `rtl/clk_gen.v` | MMCME2_BASE clk_100m x8/4 -> 200 MHz BUFG (`clk_200m_ref`, `locked`); `ifdef SIM` behavioural | IDELAYCTRL reference; the design had no MMCM |
| NEW | `rtl/sim/unisim_sim_models.v` (+) | BUFIO, BUFR (/N), IDELAYE2 (78.125 ps/tap transport delay, VAR_LOAD/CE), IDELAYCTRL (RDY after 16 REFCLK), ISERDESE2 (SDR 1:N networking, BITSLIP, Q1 = oldest, 0.2 ns setup/hold metastability window -> random bit), MMCME2_BASE (CLKOUT0/CLKFBOUT/LOCKED) | iverilog/Verilator stand-ins; the metastability window is what makes the IDELAY sweep find a fail region in simulation |
| ARCH | `rtl/radar_receiver_final.v` | `ADC_CAPTURE_MODE` parameter (default 1) with a `generate`: 0 = `ad9484_lvds_to_cmos_400m` + `ddc_400m_enhanced` (unchanged legacy), 1 = `clk_gen` + `ad9484_iserdes_capture` + `adc_capture_calib` + `ddc_4x_100m`; calibration control/status ports added; `cdc_overflow` = capture FIFO overflow in mode 1 | selectable implementation, identical baseband format into `ddc_input_interface` |
| ARCH | `rtl/radar_system_top.v` | `ADC_CAPTURE_MODE` parameter passed to the receiver; register-map calibration signals wired | |
| ARCH | `rtl/radar_control_regs.v` | registers 0x4..0xC (CAL_CTRL toggles/check-enable, CAL_LANE, CAL_TAP, CAL_SLIP, CAL_PATT = 0x55AA, read-only CAL_STAT/CAL_LANE_INFO/CAL_ERR/CAL_UNDET) | host control of the calibration (write port still tied off at the top) |
| BUG | `rtl/ddc_400m.v` | legacy NCO `phase_valid` = `mixers_enable_sync & adc_data_valid` (was `mixers_enable_sync`) | phase becomes a function of the sample index; required for the bit-exact comparison; identical behaviour for a continuous stream |
| NEW | `tb/tb_adc_iserdes_capture.v` | 400 MHz source, 8 lanes at +0.25 ns (tPD-tCPD), lane 5 +0.85 ns; auto cal locks 8/8 (taps 12, lane 5 -> 4, 8 taps less = 0.6 ns), error counter 0 at the centres, 1 bitslip on lane 0 -> errors, 4 -> none, manual tap visible on CNTVALUEOUT, 4000 sine samples reproduced exactly through the FIFO with clk_100m offset 1.3 ns vs DCO/4 | |
| NEW | `tb/tb_ddc_4x.v` | same 8000-sample sequence (two IF tones + chirp burst + noise) through `ddc_400m_enhanced` and `ddc_4x_100m`; baseband outputs compared after lag search (first 64 skipped); `CIC_PHASE_TB` parameter | PASS: max diff 0 LSB |
| — | `tb/tb_system_smoke.v`, `build.sh` | `ADC_MODE` parameter; `build.sh` runs the smoke test twice (`_mode1`, `_mode0`) via `-P` | both capture paths exercised end to end |
| XDC | `constraints/radar_system_top_beta.xdc` | ADC `set_input_delay` = datasheet tSKEW +/-0.070 ns (board trace skew to be added), legacy falling-edge lines commented, `IODELAY_GROUP adc_idelay_grp` for IDELAYCTRL + IDELAYE2, notes on BUFIO/BUFR/MMCM auto-derived clocks and the Vivado checks | |

## Command set v2, blind calibration, UG471 checks (follow-up, 2026-10-09)

Sources: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` section 7 (byte sequences fixed by the
firmware `beta/stm32/Core/Src/host_bridge_proto.c`), UG471 v1.10 (`build/docs_ext/ug471.txt`, quotes
in README "UG471 checks"). Originals untouched. The previous, uncommitted attempt at these changes
(did not compile: `rd_data_tog` used before declaration, top/module port mismatch, undeclared
`inherit_tap`, undriven `lane_metric`) was replaced.

| Type | File | Change | Reason |
|---|---|---|---|
| ARCH | `rtl/host_bridge_spi.v` | command set v2: `cmd`/`bytec` decode after the command byte; 0x02 write (addr bytes 0-1, data bytes 2-5 little-endian, `wr_req_t` toggle at d3, ack 0xA2 loaded for byte 7), 0x03 read (`rd_req_t` toggle when a0 is complete, `reg_addr = {8'h00, a0}`, data captured one clk after the address through `rd_fetch`, d0..d3 in bytes 3..6), 0x04 status (`status_snap` = {0, frames_produced, RTL_VERSION, status_in} sampled at the command byte, bytes 1..8), unknown/0x00 -> 0xEE; new parameter `RTL_VERSION` (0x0002), new ports `reg_we/reg_addr[15:0]/reg_wdata[31:0]/reg_rdata[31:0]/status_in[15:0]/frames_produced[15:0]`; 3-flop toggle synchronisers for the register requests; 0x01 path unchanged | register access over the existing bridge; byte positions match `hb_proto_write_reg/read_reg/status` exactly (rx[7] ack, rx[3..6] value, rx[1..8] status) |
| ARCH | `rtl/radar_control_regs.v` | `reg_addr` 4 -> 5 bits (existing addresses unchanged); CAL_CTRL bit4 `cal_blind` (level); new 0x0D `CAL_BLIND_COEF` (Q1.14 cos, default 0xEC39 = -5063 = cos(2*pi*120/400)*16384), 0x0E `CAL_BLIND_MARGIN` (default 0x0040), 0x10 `CAL_BLIND_MIN` (ro); header comment = section 7 table | blind calibration controls; address space for the read-back |
| ARCH | `rtl/radar_system_top.v` | bridge register port wired to `ctl_regs` (`reg_addr[4:0]`, `reg_wdata[15:0]`, `reg_rdata = {16'h0, rdata}`); `frames_produced` counter of `pk_frame_done`; `bridge_status = {11'b0, pk_overflow, cal_status[7:0] == 8'hFF, rx_cdc_overflow, bridge_cs_conflict, spi_bridge_drdy}`; blind calibration signals routed register map <-> receiver | the register write port was tied off (`1'b0`) since the first beta |
| ARCH | `rtl/radar_receiver_final.v` | ports `cal_blind`, `cal_blind_coef`, `cal_blind_margin`, `cal_blind_min`; mode 0 ties `cal_blind_min = 0`; `Q1_IS_OLDEST(0)` on the capture instance | |
| ARCH | `rtl/adc_capture_calib.v` | blind method (`ctrl_blind`): notch residual r[n] = x[n] - (coef*x[n-1])/8192 + x[n-2] on the 4 samples of each word (x = sample - 128, x[-1]/x[-2] from the previous word), metric = sum of abs(r) over `MEAS_BLIND = 512` words, 24-bit saturating, per-tap store `met[0:31]` + running minimum; lanes swept one at a time MSB first with the result applied before the next lane; pass mask = metric <= min + margin + min/16, 1-tap holes closed, linear longest run; centre = (lo+hi)/2, or hi+1-16+FAIL_HALF when the run touches tap 0, lo-1+16-FAIL_HALF when it touches tap 31 (32 taps = 1 bit at 400 MSPS), truncated runs accepted from 2 taps, untruncated need MIN_WINDOW, 32/32 -> undetermined (tap kept); `BLIND_PASSES = 2`; blind framing alignment (metric for the 4 framings of every lane via BITSLIP, minimum kept) before the first pass and after every pass; `lane_metric_min` output; `meas_cnt` 8 -> 10 bits; states 5 bits (S_BL_*). Pattern method, manual mode, check counter unchanged | calibration without the ADC test pattern (AD9484 SPI not wired); the originally suggested abs(x[n]-x[n-1]) does not discriminate for a 120 MHz tone at 400 MSPS (adjacent samples legitimately differ by up to 1.6 A) |
| BUG | `rtl/sim/unisim_sim_models.v` (ISERDESE2) | Q order: `word <= sr & WMASK` so that Q1 = newest, Q(N) = oldest = first received (was Q1 = oldest); BITSLIP moves the frame boundary one bit later (`cnt + N - slip`, was earlier); hold-window corruption fixed: the old code did `sr[0] <= $random` and then `sr <= {sr[6:0], din}` in the same block, so the second assignment overrode the first and the declared 0.2 ns hold window never acted - now `nxt[1] = rnd[1]` before `sr <= nxt` (the two block-local temporaries carry a local `lint_off BLKSEQ`). Fail region per lane is now 5 taps (27..31) instead of 2 (27..28) | UG471 p. 146 / Fig. 3-3 / p. 158 Fig. 3-11 (quotes in README); model fidelity |
| ARCH | `rtl/ad9484_iserdes_capture.v` | `Q1_IS_OLDEST` default 1 -> 0, header cites UG471 | first bit received on the highest-order Q |
| TB | `tb/tb_host_bridge_top.v` | DUT at the default `CFAR_THRESHOLD_DEFAULT` (10000); v2 register commands before the chirps (ID, CFAR_THR default, writes of CFAR_THR = 150 / CAL_CTRL = 0x18 / CAL_LANE = 3 / CAL_BLIND_COEF = 0xDEAD1234, read-backs incl. upper-16-bit masking, DUT control outputs checked, 0x04 status, 0x7F -> 0xEE, 0x01 without a frame -> zeros, DRDY still 0, pass-through gated); 0x04 with a frame pending (bit0 = 1, frames = 1) and after the read (bit0 = 0); detections must be present (threshold reached the detector only through the bridge write) | PASS: 2162-byte frame, 32 detections |
| TB | `tb/tb_host_bridge.v` (= `engineering/DESIGN/HOST_LINK/rtl/tb_host_bridge.v`) | now the engineering version (scenario 2: 32-detection regression) plus scenario 3: v2 write/read against a 4-word register model, 0x04 (status = DRDY, version 2, frames 2), 0xEE; the frame dump falls back to `tb_frame.hex` when `logs/` does not exist, so both copies are byte-identical | PASS |
| TB | `tb/tb_adc_iserdes_capture.v` | step 5 (blind): 120 MHz tone (100 LSB peak) + -1/0/+1 LSB noise, `tone_n` phase index (the `src` store stops at 65536 samples - the previous attempt froze the source mid-run), lane 2 parked on tap 27 (metastable), lane 0 bitslipped once, blind run with coef 0xEC39 / margin 64; checks: 8/8 lock, no undetermined, every lane within +/-2 taps of its pattern centre (result: +/-0), tone sequence reproduced exactly (framing restored); `check_sequence` task; `Q1_IS_OLDEST(0)`; timeout 12 ms. Pattern-method expectations unchanged (centre is now 13 / lane 5 -> 5 because of the model's wider fail region) | PASS |
| DOC | `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` section 7 | byte counts, no-turnaround read, status-word bits, full register table 0x00..0x10 identical to the RTL (run / mixers / NCO entries that never existed removed) | the shared source for firmware and GUI |
| DOC | `engineering/DESIGN/HOST_LINK/rtl/host_bridge_spi.v`, `.../tb_host_bridge.v` | byte-identical copies of the beta files; `run_tb.sh` PASS | back-port |
| XDC | `constraints/radar_system_top_beta.xdc` | header quotes the UG471 LVDS criteria verbatim; per-pin comments on the 18 bank-14 LVDS lines cite them; external 100 Ohm RDIFF + DS181 VIN/VIDIFF/VICM check marked REQUIRED / REQUIRES VERIFICATION | |
| DOC | `README.md` | results table, register-map paragraph, blind method + limits, "UG471 checks" section with the quotes, remaining-work list (items 7/8 closed, GUI register_map follow-up added) | |
| — | `build.sh` | unchanged; full run after these changes: 0 failures, 324 verilator warning lines (165 synth + 159 sim, identical to the previous state) | |

Not changed: `beta/gui/aeris10_gui/protocol/register_map.py` (GUI, out of scope here) - it masks
addresses with 0xF and documents a section-7 discrepancy that no longer exists; see README item 8.
