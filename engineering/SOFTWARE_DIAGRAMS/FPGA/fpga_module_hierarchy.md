# FPGA RTL Module Hierarchy - AERIS-10 (auto-generated)

Generated 2026-10-09 by `tools/gen_verilog_hierarchy.py` from `9_Firmware/9_2_FPGA` (26 Verilog files, all parsed). Top module requested: `radar_system_top` (found). Script exit code: 1.

Drawing SD-01, revision A, status SOURCE-DERIVED. Native file: `fpga_module_hierarchy.dot`.

Parsing method: comments and string literals are blanked, then `module <name>` and `<type> [#(...)] <instance> (` patterns are matched; Verilog keywords are excluded; `BUFG/IBUFDS/IDDR/...` are classified as Xilinx UNISIM primitives. Line numbers refer to the original files. This is a lexical scan, not an elaboration: generate-loop replication counts (e.g. 8x IBUFDS/IDDR in `ad9484_interface_400m.v`) are shown once.

| Status | Count |
|---|---:|
| DEFINED | 19 |
| MISSING | 5 |
| PRIMITIVE | 3 |
| UNUSED | 9 |

| Module | Defined at (file:line) | Instantiated by (parent as instance, file:line) | Status |
|---|---|---|---|
| `BUFG` | - | `lvds_to_cmos_400m` as `bufg_dco` (`lvds_to_cmos_400m.v:28`); `radar_system_top` as `bufg_100m` (`radar_system_top.v:174`); `radar_system_top` as `bufg_120m` (`radar_system_top.v:179`); `radar_system_top` as `bufg_ft601` (`radar_system_top.v:184`) | **PRIMITIVE** |
| `FFT_enhanced` | - | `fft_1024_forward_enhanced` as `fft_forward_inst` (`fft_1024_forward.v:102`); `fft_1024_inverse_enhanced` as `ifft_inverse_inst` (`fft_1024_inverse.v:78`) | **MISSING** |
| `IBUFDS` | - | `ad9484_interface_400m` as `ibufds_data` (`ad9484_interface_400m.v:25`); `ad9484_interface_400m` as `ibufds_dco` (`ad9484_interface_400m.v:37`); `lvds_to_cmos_400m` as `ibufds_dco` (`lvds_to_cmos_400m.v:17`) | **PRIMITIVE** |
| `IDDR` | - | `ad9484_interface_400m` as `iddr_inst` (`ad9484_interface_400m.v:53`) | **PRIMITIVE** |
| `ad9484_interface_400m` | `ad9484_interface_400m.v:1` | - | **UNUSED** |
| `ad9484_lvds_to_cmos_400m` | - | `radar_receiver_final` as `adc` (`radar_receiver_final.v:82`) | **MISSING** |
| `cdc_adc_to_processing` | `cdc_modules.v:6` | `ddc_400m_enhanced` as `CDC_FIR_i` (`ddc_400m.v:243`); `ddc_400m_enhanced` as `CDC_FIR_q` (`ddc_400m.v:256`); `radar_receiver_final` as `cdc` (`radar_receiver_final.v:94`) | **DEFINED** |
| `cdc_handshake` | `cdc_modules.v:156` | - | **UNUSED** |
| `cdc_single_bit` | `cdc_modules.v:129` | - | **UNUSED** |
| `chirp_memory_loader_param` | `chirp_memory_loader_param.v:2` | `radar_receiver_final` as `chirp_mem` (`radar_receiver_final.v:144`) | **DEFINED** |
| `cic_decimator_4x_enhanced` | `cic_decimator_4x_enhanced.v:1` | `ddc_400m_enhanced` as `cic_i_inst` (`ddc_400m.v:223`); `ddc_400m_enhanced` as `cic_q_inst` (`ddc_400m.v:232`) | **DEFINED** |
| `dac_interface_enhanced` | `dac_interface_single.v:1` | `radar_transmitter` as `dac_interface_inst` (`radar_transmitter.v:148`) | **DEFINED** |
| `ddc_400m_enhanced` | `ddc_400m.v:3` | `radar_receiver_final` as `ddc` (`radar_receiver_final.v:114`) | **DEFINED** |
| `ddc_input_interface` | `ddc_input_interface.v:3` | `radar_receiver_final` as `ddc_if` (`radar_receiver_final.v:129`) | **DEFINED** |
| `doppler_processor_optimized` | `doppler_processor.v:3` | `radar_receiver_final` as `doppler_proc` (`radar_receiver_final.v:290`) | **DEFINED** |
| `edge_detector_enhanced` | `edge_detector.v:1` | `radar_transmitter` as `chirp_edge` (`radar_transmitter.v:93`); `radar_transmitter` as `elevation_edge` (`radar_transmitter.v:100`); `radar_transmitter` as `azimuth_edge` (`radar_transmitter.v:107`) | **DEFINED** |
| `fft_1024_forward_enhanced` | `fft_1024_forward.v:3` | - | **UNUSED** |
| `fft_1024_inverse_enhanced` | `fft_1024_inverse.v:3` | - | **UNUSED** |
| `fir_lowpass_parallel_enhanced` | `fir_lowpass.v:3` | `ddc_400m_enhanced` as `fir_i_inst` (`ddc_400m.v:278`); `ddc_400m_enhanced` as `fir_q_inst` (`ddc_400m.v:290`) | **DEFINED** |
| `frequency_matched_filter` | `frequency_matched_filter.v:4` | - | **UNUSED** |
| `latency_buffer_2159` | `latency_buffer_2159.v:4` | `radar_receiver_final` as `ref_latency_buffer` (`radar_receiver_final.v:173`) | **DEFINED** |
| `level_shifter_interface` | `level_shifter_interface.v:10` | - | **UNUSED** |
| `lfsr_dither_enhanced` | `ddc_400m.v:381` | `ddc_400m_enhanced` as `phase_dither_gen` (`ddc_400m.v:131`) | **DEFINED** |
| `lvds_to_cmos_400m` | `lvds_to_cmos_400m.v:2` | `radar_receiver_final` as `clk_400m_inst` (`radar_receiver_final.v:61`) | **DEFINED** |
| `matched_filter_multi_segment` | `matched_filter_multi_segment.v:3` | `radar_receiver_final` as `mf_dual` (`radar_receiver_final.v:198`) | **DEFINED** |
| `matched_filter_processing_chain` | - | `matched_filter_multi_segment` as `m_f_p_c` (`matched_filter_multi_segment.v:361`) | **MISSING** |
| `nco_400m_enhanced` | `nco_400m_enhanced.v:3` | `ddc_400m_enhanced` as `nco_core` (`ddc_400m.v:152`) | **DEFINED** |
| `plfm_chirp_controller_enhanced` | `plfm_chirp_controller.v:3` | `radar_transmitter` as `plfm_chirp_inst` (`radar_transmitter.v:115`) | **DEFINED** |
| `radar_receiver_final` | `radar_receiver_final.v:3` | `radar_system_top` as `rx_inst` (`radar_system_top.v:270`) | **DEFINED** |
| `radar_system_tb` | `radar_system_tb.v:14` | - | **UNUSED** |
| `radar_system_top` | `radar_system_top.v:18` | `radar_system_tb` as `dut` (`radar_system_tb.v:370`) | **DEFINED** |
| `radar_transmitter` | `radar_transmitter.v:21` | `radar_system_top` as `tx_inst` (`radar_system_top.v:204`) | **DEFINED** |
| `range_bin_decimator` | - | `radar_receiver_final` as `range_decim` (`radar_receiver_final.v:226`) | **MISSING** |
| `usb_data_interface` | `usb_data_interface.v:1` | `radar_system_top` as `usb_inst` (`radar_system_top.v:345`) | **DEFINED** |
| `usb_packet_analyzer` | `usb_packet_analyzer.v:10` | - | **UNUSED** |
| `xfft_32` | - | `doppler_processor_optimized` as `fft_inst` (`doppler_processor.v:283`) | **MISSING** |

## Files scanned

- `ad9484_interface_400m.v` - 1 module definition(s)
- `cdc_modules.v` - 3 module definition(s)
- `chirp_lut_init.v` - 0 module definition(s)
- `chirp_memory_loader_param.v` - 1 module definition(s)
- `cic_decimator_4x_enhanced.v` - 1 module definition(s)
- `dac_interface_single.v` - 1 module definition(s)
- `ddc_400m.v` - 2 module definition(s)
- `ddc_input_interface.v` - 1 module definition(s)
- `doppler_processor.v` - 1 module definition(s)
- `edge_detector.v` - 1 module definition(s)
- `fft_1024_forward.v` - 1 module definition(s)
- `fft_1024_inverse.v` - 1 module definition(s)
- `fir_lowpass.v` - 1 module definition(s)
- `frequency_matched_filter.v` - 1 module definition(s)
- `latency_buffer_2159.v` - 1 module definition(s)
- `level_shifter_interface.v` - 1 module definition(s)
- `lvds_to_cmos_400m.v` - 1 module definition(s)
- `matched_filter_multi_segment.v` - 1 module definition(s)
- `nco_400m_enhanced.v` - 1 module definition(s)
- `plfm_chirp_controller.v` - 1 module definition(s)
- `radar_receiver_final.v` - 1 module definition(s)
- `radar_system_tb.v` - 1 module definition(s)
- `radar_system_top.v` - 1 module definition(s)
- `radar_transmitter.v` - 1 module definition(s)
- `usb_data_interface.v` - 1 module definition(s)
- `usb_packet_analyzer.v` - 1 module definition(s)

## Notes

- MISSING = instantiated somewhere in the tree but no `module` of that name exists in the scanned files. Names with AXI4-Stream ports (`s_axis_config_*`, `m_axis_data_*`) indicate Xilinx IP cores whose `.xci` is not in the repository; the others are RTL modules that were never committed.
- UNUSED = defined but never instantiated (orphans or the testbench root).
- The script does not evaluate `` `ifdef `` blocks; all text is scanned.
