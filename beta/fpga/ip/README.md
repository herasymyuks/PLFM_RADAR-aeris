# Xilinx FFT IP settings for the beta project

Status: **IP not generated** (no Vivado on the authoring machine). The two files `rtl/xfft_32.v`
and `rtl/FFT_enhanced.v` contain simulation-only behavioural models (`axis_fft_behav.v`) and, under
`SYNTHESIS`, an instantiation of a deliberately missing module so that synthesis fails loudly until
the IP exists. `vivado/create_project.tcl` imports `ip/<name>/<name>.xci` when present and then moves
the wrapper file to the simulation set.

Settings are derived from how the RTL drives the ports (widths, config words, throttle) - they are
the minimum needed for the ports to match; everything else (rounding mode, latency, output order)
is a choice recorded here so that the model and the IP agree.

## Common

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

## `xfft_32` (Doppler, `doppler_processor.v:283-296`)

| Setting | Value | Evidence |
|---|---|---|
| Module name | `xfft_32` | instance name in the RTL |
| Transform length | 32 | `DOPPLER_FFT_SIZE = 32`, `fft_input_last` after 32 samples |
| Throttle scheme | **Non Real Time** (has `m_axis_data_tready`) | `.m_axis_data_tready(1'b1)` is connected |
| Config word | 8 bits: bit0 FWD_INV, bits[5:1] SCALE_SCH (2+2+1 bits for radix-4, radix-4, radix-2 stages) | `s_axis_config_tdata(8'h..)`; RTL default `FFT_CONFIG_WORD = 8'h35` = forward, shift 2+2+1 = 2^-5 |
| Transform direction | run-time configurable (forward used) | config bit0 = 1 |
| Model latency (`axis_fft_behav` LATENCY) | 72 clocks from the last input | placeholder; the real IP latency is reported by the GUI and must be below `FFT_WAIT_TIMEOUT` (1000) in `doppler_processor.v` |

Create with:
```
create_ip -name xfft -vendor xilinx.com -library ip -version 9.1 -module_name xfft_32 -dir beta/fpga/ip
set_property -dict [list CONFIG.transform_length {32} CONFIG.implementation_options {pipelined_streaming_io} \
  CONFIG.data_format {fixed_point} CONFIG.scaling_options {scaled} CONFIG.input_width {16} CONFIG.phase_factor_width {16} \
  CONFIG.rounding_modes {convergent_rounding} CONFIG.output_ordering {natural_order} CONFIG.throttle_scheme {nonrealtime} \
  CONFIG.aresetn {true} CONFIG.run_time_configurable_transform_length {false}] [get_ips xfft_32]
generate_target all [get_ips xfft_32]
```
(Property names follow the xfft v9.1 `CONFIG.*` set; verify in `report_property [get_ips xfft_32]` - not executed here.)

## `FFT_enhanced` (pulse compression, `fft_1024_forward.v:102`, `fft_1024_inverse.v:78`)

| Setting | Value | Evidence |
|---|---|---|
| Module name | `FFT_enhanced` | "This must match the name in your project" (`fft_1024_forward.v:101`) |
| Transform length | 1024 | `tlast` after 1024 samples (`fft_1024_forward.v:58`), reference memory 1024 bins per segment |
| Throttle scheme | **Real Time** (no `m_axis_data_tready`) | the instantiations do not connect `m_axis_data_tready`; the wrappers tie their internal tready to 1 |
| Config word | 16 bits: bit0 FWD_INV, bits[10:1] SCALE_SCH (2 bits x 5 radix-4 stages), upper bits padding | `s_axis_config_tdata[15:0]`; forward default `SCALE_SCH = 10'h255` (shifts 1,1,1,1,2 = 2^-6), inverse `10'h155` (2^-5) |
| Transform direction | **run-time configurable** | same core used forward (`16'h...1`) and inverse (`16'h...0`) |
| Model latency | 160 clocks (beta model value, the IP is ~2-3k clocks for 1024 points) | the chain tolerates any latency (reference fetched by address, frames queued) |

Create with:
```
create_ip -name xfft -vendor xilinx.com -library ip -version 9.1 -module_name FFT_enhanced -dir beta/fpga/ip
set_property -dict [list CONFIG.transform_length {1024} CONFIG.implementation_options {pipelined_streaming_io} \
  CONFIG.data_format {fixed_point} CONFIG.scaling_options {scaled} CONFIG.input_width {16} CONFIG.phase_factor_width {16} \
  CONFIG.rounding_modes {convergent_rounding} CONFIG.output_ordering {natural_order} CONFIG.throttle_scheme {realtime} \
  CONFIG.aresetn {true}] [get_ips FFT_enhanced]
generate_target all [get_ips FFT_enhanced]
```

## Scaling-schedule arithmetic (why these defaults)

A 1024-sample segment of the 10-30 MHz chirp occupies ~68 bins; an input of amplitude A gives
|X(k)| ~ 124*A unscaled. With 2^-6: ~1.9*A (A = 8000 -> 15.5k, no saturation). The Q15 product with
the stored reference (|M| <= 31128) is ~0.95*|X|; the inverse transform sums ~68 bins coherently at
the peak: ~68 * 15k = 1.0M unscaled -> 2^-5 gives ~32k, i.e. the compressed peak uses the full 16-bit
range for a full-scale input. Smaller inputs scale linearly. The Doppler FFT uses the conservative
2^-5 (= 1/N) so that any 16-bit input cannot overflow. The numpy model in `tb/gen_vectors.py` applies
the same total shifts; `tb_matched_filter.v` checks the resulting peak amplitude against it.

## Verification of a generated IP against the model

1. Generate the IP, open the project, set `sim_1` top to `tb_fft_wrappers`, run behavioural
   simulation with the IP's simulation model (`verilog_define` must NOT define `SYNTHESIS`).
2. Expected: `PASS tb_fft_wrappers` with the +/-2 LSB tolerance. If the IP rounds differently, raise
   `TOL` in the testbench and record the measured maximum difference here.
3. Record the IP latency (GUI "Latency" field) and check `FFT_WAIT_TIMEOUT` in `doppler_processor.v`.
