# AERIS-10 beta FPGA - open-source synthesis / P&R estimate (`beta/fpga_synth/`)

**Status: OPEN-SOURCE ESTIMATE. Not a Vivado result.** Every number below comes from Yosys
(`synth_xilinx -family xc7`) and, where stated, nextpnr-xilinx. Vivado's synthesis, retiming,
DSP/BRAM inference and timing models differ; nothing here replaces `beta/fpga/vivado/build.tcl`.
This directory only *reads* `beta/fpga/` (RTL, mem, XDC); nothing under `beta/fpga/` was changed.

## What was synthesised

* Source: git snapshot **65cd160** of `beta/fpga` (`REV=HEAD ./run_synth.sh`; `beta/fpga` is
  unchanged up to e3b7930). The working tree had uncommitted edits by another session
  (`adc_capture_calib.v`, `host_bridge_spi.v`, top, register map - new ports not yet wired:
  Yosys reported undriven `host_bridge.reg_rdata`, `calib.blind_*`, `lane_metric` and two
  implicitly declared identifiers `inherit_tap`/`inherit_valid` in `adc_capture_calib.v`), so
  the committed snapshot was used. **Re-run `REV=HEAD ./run_synth.sh` after those edits are committed.**
* File list = `build.sh` step 2 (synthesis view: `rtl/*.v`, no `-DSIM`, Yosys defines
  `SYNTHESIS`) minus `rtl/axis_fft_behav.v` (simulation-only, real arithmetic) and
  `rtl/sim/unisim_sim_models.v` (replaced by Yosys' `+/xilinx/cells_sim.v`/`cells_xtra.v`).
* Top `radar_system_top`, default parameters (`ADC_CAPTURE_MODE = 1`: ISERDES capture +
  polyphase DDC at 100 MHz). Part xc7a50tftg256-2.
* The two Xilinx FFT IP cores are **not generated**; their synthesis-view placeholders
  (`XFFT_32_IP_NOT_GENERATED__...`, `FFT_ENHANCED_IP_NOT_GENERATED__...`) are declared
  `(* blackbox *)` in `bb/fft_ip_blackbox.v` - **3 instances** (1 x xfft_32 in
  `doppler_processor`, 2 x FFT_enhanced in `fft_1024_forward/inverse`) are excluded from the counts.

## Tool versions

| Tool | Version | Source |
|---|---|---|
| Yosys | 0.69+post (git 143eb14), Homebrew `yosys 0.69_1`, arm64 | `brew install yosys` |
| nextpnr-xilinx | bc9b234 (2026-09-25, openXC7/nextpnr-xilinx, archived - development moved to openXC7/nextpnr himbaechel) | built from source, `-DARCH=xilinx -DUSE_OPENMP=OFF -DBUILD_PYTHON=OFF` (Apple clang rejects `-fopenmp`) |
| prjxray-db | a90f27c (2026-09-19, submodule of nextpnr-xilinx) | artix7 / xc7a50tftg256-2 |
| chip database | `xc7a50t.bin` 93 MB | `python3 xilinx/python/bbaexport.py --device xc7a50tftg256-2 --bba xc7a50t.bba` + `bbasm --l` |
| prjxray tools | f4pga/prjxray c9f02d8 (2025-06-05): `xc7frames2bit` (C++), `utils/fasm2frames.py` (Python 3.14 venv with `fasm`, prjxray) | built from source |

Build tree of the external tools: `~/.cache/aeris10_work/{nextpnr-src,prjxray-src,xray-venv}` (not in the repo).

## Commands

```sh
cd beta/fpga_synth
REV=HEAD HIER=1 ./run_synth.sh   # Yosys, ~25 s, 1.5 GB; REV omitted = working tree; HIER=1 adds per-module run
./run_pnr.sh                     # nextpnr-xilinx P&R trial + prjxray bitstream (see "P&R trial")
```

| File | Purpose |
|---|---|
| `synth_yosys.ys` | utilisation run (flat, `synth_xilinx -family xc7 -flatten -abc9`, DSP/BRAM/LUTRAM inference on) |
| `synth_yosys_hier.ys` | same, hierarchy kept (per-module breakdown) |
| `synth_yosys_pnr.ys` | netlist for nextpnr (FFT stubs, unconstrained ports demoted, `$print` removed) |
| `run_synth.sh`, `util_table.py` | runner; Yosys `stat` -> utilisation table |
| `make_pnr_inputs.py`, `run_pnr.sh` | trimmed XDC + port demotion; P&R / bitstream runner |
| `bb/fft_ip_blackbox.v`, `bb/fft_ip_pnr_stub.v` | FFT IP black boxes (utilisation) / pass-through stubs (P&R only) |
| `reports/` | `yosys_stat.txt`, `utilisation_xc7a50t.md`, `yosys_stat_hier.txt`, `per_module.md`, `yosys_warnings_summary.txt`, `yosys_check_post.txt`, `yosys_latches.txt`, nextpnr report |
| `logs/` | full Yosys / nextpnr logs (gzipped for the commit; `run_synth.sh` rewrites `yosys_synth.log` uncompressed) |

## Utilisation (Yosys, flat netlist, FFT IP excluded)

Budget: XC7A50T, AMD DS180 *7 Series FPGAs Data Sheet: Overview*, Table 3 (Artix-7): 8,150 slices
(4 LUT6 + 8 FF each = 32,600 LUT / 65,200 FF), 600 kb distributed RAM, 120 DSP48E1,
75 x 36 kb block RAM (2,700 kb), 5 CMT. nextpnr's device database agrees (DSP48E1 120,
RAMB18E1 150, CARRY4 8,150, BUFGCTRL 32, MMCME2_ADV 5, IDELAYCTRL 5).

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

Per module (hierarchical run, local cells only, counts per module *definition*:
`fir_lowpass_parallel_enhanced` is instantiated twice - I and Q - so its 32 DSP count twice;
flat total 36 + 2 x 32 + 4 + 2 = 106 DSP):

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

### Reading the numbers

1. **DSP48E1 is the binding resource: 106 of 120 (88 %) without the FFT IP.** 64 are the two
   32-tap fully parallel FIRs (`fir_lowpass.v`), 36 the polyphase DDC (`ddc_4x_100m.v`: 8 mixers +
   the CIC-as-FIR), 4 the matched-filter complex multiply, 2 the Doppler window. Only **14 DSP48E1
   remain for three FFT cores** (2 x 1024-point + 1 x 32-point, Pipelined Streaming, 16-bit). The
   xfft v9.1 DSP count must be read from the Vivado IP GUI (Implementation Details tab) before
   anything else; if it exceeds 14 the design does not fit the XC7A50T as written (options: FIR
   symmetry folding / time-multiplexing at 100 MHz vs. 25 MSPS output, Radix-2 Lite / Burst I/O FFT
   architecture, or LUT multipliers via `use_dsp = "no"`). Not decided here.
2. **Block RAM is almost unused (2 x RAMB18) because the RTL memories cannot map to BRAM**, not
   because the design is small:
   * `chirp_memory_loader_param.v:32-35` (`ram_style = "block"`, 2 x 4096 x 16 + 2 x 1024 x 16):
     the read data goes through the long/short-chirp mux before the output register
     (lines 106-120) and the register has an asynchronous reset -> no synchronous read port.
     Yosys aborts on the forced block mapping ("no valid mapping found"); with the attribute
     removed the ROM becomes ~1,850 LUTs of logic.
   * `doppler_processor.v:74-75` (`ram_style = "block"`, 2 x 2048 x 16): read data feeds the
     multiplier combinationally (lines 236-238) -> asynchronous read -> 1,536 LUTs as RAM64M.
     **Yosys-specific trap:** the write sits inside an async-reset `always` block, so by default
     the Yosys frontend turns the memory into **65,611 flip-flops** (> the 65,200 FF of the whole
     device); `run_synth.sh` reads this file with `-nomem2reg` to avoid that artefact.
   * `host_bridge_spi` frame RAM: 1,536 LUTs as RAM64M (asynchronous read in the SCLK domain,
     already listed as unresolved in `beta/fpga/README.md`).
   * Only `matched_filter_multi_segment.v:83-84` input buffers map to RAMB18 (2).
   Recommended RTL change (designer decision, not made here): register each memory output in its
   own clocked block without reset (or with synchronous reset), mux afterwards; that moves ~4,900
   LUTs (1,847 + 1,536 + 1,536) into roughly 7-8 RAMB36 (long chirp 2 x 64 kb, short chirp 2 x 16 kb,
   Doppler 2 x 32 kb, bridge frame ~17 kb) and matches what the `ram_style` attributes ask for. Vivado must be checked
   for the same inference result in its synthesis log / `report_utilization -hierarchical`.
3. LUTs (39 %) and FFs (7 %) leave room; the FFT IP adds BRAM/LUT/DSP on top.
4. **I/O: 183 port bits need 192 package pins** (9 LVDS pairs) - more than the 170 user I/O of the
   FTG256 package (DS180 Table 3 / package table - verify against UG475), even before pin conflicts. The 116 UNRESOLVED
   debug/FT601/status bits (`beta/fpga/README.md`) must be removed from the top for any board build.

### Synthesis warnings that indicate real problems

From `reports/yosys_warnings_summary.txt` and `yosys_check_post.txt` (snapshot 65cd160):

* Latches: **none** (`reports/yosys_latches.txt` empty). Multi-driven nets: **none**. Post-synthesis
  `check`: 0 problems. No unresolved modules other than the 3 deliberate FFT black boxes.
* `chirp_memory_loader_param.v:112`: `$time` implicitly declared / undriven - inside a
  `DEBUG`-gated `$display` (`DEBUG = 0`); harmless for hardware but leaves a `$print` cell that
  nextpnr cannot place (removed in `synth_yosys_pnr.ys`). Wrap it in `// synthesis translate_off`.
* Forced `ram_style = "block"` impossible on 6 memories (above) - real inference problem.
* `rtl/usb_data_interface.v:84`, `rtl/host_bridge_spi.v:106`: tri-state logic (FT601 data bus,
  MISO) - mapped to IOBUF/OBUFT at the top; fine.
* "Replacing memory ... with list of registers" for small arrays (`fir_lowpass.v:82` delay line,
  `ddc_4x_100m.v:182`, `adc_capture_calib.v`, `rd_map_packer.v:94`) - intended (shift registers /
  per-lane registers), small.
* Floating-point UNISIM parameters (`MMCME2_BASE`, `IDELAYE2.REFCLK_FREQUENCY`) converted to
  strings - Yosys cosmetic.
* **Working tree (uncommitted, not the reported numbers):** undriven `host_bridge.reg_rdata[31:0]`,
  `status_in`, `frames_produced`, `calib.blind_coef/blind_thr/blind_max/ctrl_blind`,
  `lane_metric`; implicit identifiers `inherit_tap`, `inherit_valid`
  (`adc_capture_calib.v:291-295`, would be 1-bit implicit wires - a real bug if it stays).
* **Clocking:** Yosys inserted a 4th BUFG on `host_bridge.sclk` (= `stm32_sclk_3v3`, XDC pin
  **J16 = IO_L23N_T3_FWE_B_15, not a clock-capable MRCC/SRCC pin**). Vivado will refuse a non-CC
  pin driving a BUFG (placer clock-route DRC) unless the net gets
  `set_property CLOCK_DEDICATED_ROUTE FALSE`, which the XDC does not contain, or SCLK is
  oversampled in clk_100m instead.

## P&R trial (nextpnr-xilinx) and bitstream

**Status: NOT COMPLETED - no placed/routed design, no Fmax, no bitstream.** The toolchain was
built and the netlist was accepted by nextpnr-xilinx (packing succeeded); placement did not complete.

Inputs (generated by `make_pnr_inputs.py` / `synth_yosys_pnr.ys`):
* `pnr/radar_system_top_beta_pnr.xdc`: the 67 PACKAGE_PIN + IOSTANDARD assignments of the beta XDC
  and its `create_clock` lines (clk_100m 10 ns, clk_120m_dac 8.333 ns, adc_dco 2.5 ns, spi_sclk 37 ns).
* Netlist with the 116 unconstrained port bits demoted to internal nets (24 ports: `ft601_*`,
  `dac_clk`, `dbg_*`, `current_*`, `new_chirp_frame`, `system_status`), the FFT IP replaced by
  1-register pass-through stubs (`bb/fft_ip_pnr_stub.v`, NOT an FFT), `$print`/`$scopeinfo`
  removed. Resulting netlist: 12,747 LUT, 4,667 FF, 106 DSP48E1, 2 RAMB18E1 (`reports/yosys_stat_pnr_netlist.txt`).

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

Blocking items for the open-source P&R (tool side, not design errors):
1. DSP48E1 cascade chains at 88 % DSP utilisation: HeAP legaliser cannot place them; SA placer livelocks
   (unbounded retry loop). Next things to try (not done): the patched SA run to completion (~30-60 min
   estimate, unverified), or the maintained openXC7/nextpnr `himbaechel` xilinx flow, which the archived
   fork's README names as the successor.
2. Even with a routed result, the timing would be incomplete: `set_clock_groups`, `set_false_path`,
   `set_input_delay`, `IODELAY_GROUP`, `DIFF_TERM`, `CFGBVS`/`CONFIG_VOLTAGE` are not parsed, the
   ADC ISERDES/IDELAY input window is not analysed, and the FFT stubs remove the FFT critical paths.
   Any bitstream from this flow would contain the stubs (named `radar_system_top_beta_OPENSOURCE_STUBFFT.bit`
   by `run_pnr.sh`) and must never be loaded on the radar hardware.

`run_pnr.sh` reproduces the whole branch (`PLACER=sa` default, `NOBIT=1` skips the bitstream);
external tool paths are overridable by environment variables (header of the script).

## Primitive support in the open-source flow

| Primitive (used by beta) | Yosys (`synth_xilinx`) | nextpnr-xilinx bc9b234 (xc7) |
|---|---|---|
| IBUFDS (LVDS_25), IBUF, OBUF, IOBUF | yes (instantiated / auto `iopadmap`) | yes |
| BUFG | yes | yes (BUFGCTRL) |
| BUFIO, BUFR (`BUFR_DIVIDE 4`) | black-box cells from `cells_xtra.v` | yes (packer handles BUFIO/BUFR) |
| IDELAYE2 (VAR_LOAD), IDELAYCTRL | passed through | yes; `IODELAY_GROUP` not parsed (XDC subset) |
| ISERDESE2 (NETWORKING SDR 1:4) | passed through | yes |
| IDDR (legacy mode 0 only, not built) | passed through | yes |
| MMCME2_BASE | passed through | yes (mapped to MMCME2_ADV) |
| DSP48E1 incl. PCIN/PCOUT cascades | inferred (`-abc9`, cascades on FIR/DDC adder chains) | yes, but the default HeAP placer failed to legalise the cascades at 88 % DSP use; SA placer needed |
| RAMB18E1 / RAM64M | inferred | yes |
| Xilinx FFT IP (xfft v9.1) | **no** - encrypted IP, Vivado only | **no** |
| XDC: `set_clock_groups`, `set_false_path`, `set_input_delay`, `IODELAY_GROUP`, `DIFF_TERM`, `CFGBVS`/`CONFIG_VOLTAGE` | n/a | **not parsed** (nextpnr-xilinx `xdc.cc` only handles `set_property` PACKAGE_PIN/IOSTANDARD-type properties, `create_clock`, `set_multicycle_path`) - all CDC/IO timing exceptions are absent, so cross-clock paths are not analysed the way Vivado would |
| Timing models | approximate (prjxray-derived) | no IO timing (ISERDES/IDELAY capture window is NOT analysed) |

## What must be run in Vivado to confirm

```sh
# 1. generate the FFT IP (beta/fpga/ip/README.md), then
vivado -mode batch -source beta/fpga/vivado/create_project.tcl
vivado -mode batch -source beta/fpga/vivado/build.tcl -tclargs <path>/aeris10_beta.xpr 8
```
and inspect, against the numbers above:
* `report_utilization -hierarchical` (synth + impl): DSP48E1 total **with** the 3 FFT cores <= 120;
  BRAM use of `chirp_mem`, `doppler_proc`, `host_bridge` (expect LUTRAM/logic unless the RTL is
  changed); the synthesis log's RAM/ROM inference tables (look for the `ram_style` memories).
* `report_timing_summary` (WNS/WHS >= 0 for clk_100m, clk_120m_dac, adc_dco/BUFR, clk_200m, spi_sclk),
  `report_clock_interaction`, `report_cdc`, `report_methodology`.
* `report_io` / `report_drc` (non-CC pin J16 -> BUFG; bank-14 LVDS_25 at 3.3 V VCCO; IODELAY_GROUP
  and IDELAYCTRL placement; unconstrained ports - remove the 116 UNRESOLVED bits from the top first).
* `write_bitstream` only after all of the above; the open-source bitstream from this directory is
  never a substitute.
