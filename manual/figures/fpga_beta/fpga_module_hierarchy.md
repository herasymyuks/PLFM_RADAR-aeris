# FPGA RTL Module Hierarchy - AERIS-10 (auto-generated)

Generated 2026-10-09 by `tools/gen_verilog_hierarchy.py` from `beta/fpga/rtl` (40 Verilog files, all parsed). Top module requested: `radar_system_top` (found). Script exit code: 1.

Drawing SD-01, revision A, status SOURCE-DERIVED. Native file: `fpga_module_hierarchy.dot`.

Parsing method: comments and string literals are blanked, then `module <name>` and `<type> [#(...)] <instance> (` patterns are matched; Verilog keywords are excluded; `BUFG/IBUFDS/IDDR/...` are classified as Xilinx UNISIM primitives. Line numbers refer to the original files. This is a lexical scan, not an elaboration: generate-loop replication counts (e.g. 8x IBUFDS/IDDR in `ad9484_interface_400m.v`) are shown once.

| Status | Count |
|---|---:|
| DEFINED | 43 |
| MISSING | 2 |
| PRIMITIVE | 0 |
| UNUSED | 8 |

| Module | Defined at (file:line) | Instantiated by (parent as instance, file:line) | Status |
|---|---|---|---|
| `BUFG` | `sim/unisim_sim_models.v:18` | `ad9484_lvds_to_cmos_400m` as `u_bufg_dco` (`ad9484_lvds_to_cmos_400m.v:111`); `clk_gen` as `u_bufg_200` (`clk_gen.v:59`); `radar_system_top` as `bufg_100m` (`radar_system_top.v:226`); `radar_system_top` as `bufg_120m` (`radar_system_top.v:231`); `lvds_to_cmos_400m` as `bufg_dco` (`unused_orig/lvds_to_cmos_400m.v:28`) | **DEFINED** |
| `BUFIO` | `sim/unisim_sim_models.v:116` | `ad9484_iserdes_capture` as `u_bufio` (`ad9484_iserdes_capture.v:70`) | **DEFINED** |
| `BUFR` | `sim/unisim_sim_models.v:123` | `ad9484_iserdes_capture` as `u_bufr` (`ad9484_iserdes_capture.v:71`) | **DEFINED** |
| `FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README` | - | `FFT_enhanced` as `u_missing_ip` (`FFT_enhanced.v:48`) | **MISSING** |
| `FFT_enhanced` | `FFT_enhanced.v:20` | `fft_1024_forward_enhanced` as `fft_forward_inst` (`fft_1024_forward.v:99`); `fft_1024_inverse_enhanced` as `ifft_inverse_inst` (`fft_1024_inverse.v:63`) | **DEFINED** |
| `IBUFDS` | `sim/unisim_sim_models.v:25` | `ad9484_iserdes_capture` as `u_ibufds_dco` (`ad9484_iserdes_capture.v:68`); `ad9484_iserdes_capture` as `u_ibufds` (`ad9484_iserdes_capture.v:90`); `ad9484_lvds_to_cmos_400m` as `u_ibufds_data` (`ad9484_lvds_to_cmos_400m.v:89`); `ad9484_lvds_to_cmos_400m` as `u_ibufds_dco` (`ad9484_lvds_to_cmos_400m.v:100`); `ad9484_interface_400m` as `ibufds_data` (`unused_orig/ad9484_interface_400m.v:25`); `ad9484_interface_400m` as `ibufds_dco` (`unused_orig/ad9484_interface_400m.v:37`); `lvds_to_cmos_400m` as `ibufds_dco` (`unused_orig/lvds_to_cmos_400m.v:17`) | **DEFINED** |
| `IDDR` | `sim/unisim_sim_models.v:40` | `ad9484_lvds_to_cmos_400m` as `u_iddr` (`ad9484_lvds_to_cmos_400m.v:118`); `ad9484_interface_400m` as `iddr_inst` (`unused_orig/ad9484_interface_400m.v:53`) | **DEFINED** |
| `IDELAYCTRL` | `sim/unisim_sim_models.v:189` | `ad9484_iserdes_capture` as `u_idelayctrl` (`ad9484_iserdes_capture.v:82`) | **DEFINED** |
| `IDELAYE2` | `sim/unisim_sim_models.v:148` | `ad9484_iserdes_capture` as `u_idelay` (`ad9484_iserdes_capture.v:93`) | **DEFINED** |
| `ISERDESE2` | `sim/unisim_sim_models.v:203` | `ad9484_iserdes_capture` as `u_iserdes` (`ad9484_iserdes_capture.v:103`) | **DEFINED** |
| `MMCME2_BASE` | `sim/unisim_sim_models.v:279` | `clk_gen` as `u_mmcm` (`clk_gen.v:37`) | **DEFINED** |
| `XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README` | - | `xfft_32` as `u_missing_ip` (`xfft_32.v:50`) | **MISSING** |
| `ad9484_interface_400m` | `unused_orig/ad9484_interface_400m.v:1` | - | **UNUSED** |
| `ad9484_iserdes_capture` | `ad9484_iserdes_capture.v:35` | `radar_receiver_final` as `adc` (`radar_receiver_final.v:172`) | **DEFINED** |
| `ad9484_lvds_to_cmos_400m` | `ad9484_lvds_to_cmos_400m.v:43` | `radar_receiver_final` as `adc` (`radar_receiver_final.v:100`) | **DEFINED** |
| `adc_capture_calib` | `adc_capture_calib.v:86` | `radar_receiver_final` as `calib` (`radar_receiver_final.v:183`) | **DEFINED** |
| `async_fifo` | `async_fifo.v:17` | `ad9484_iserdes_capture` as `u_fifo` (`ad9484_iserdes_capture.v:141`); `ddc_400m_enhanced` as `CDC_FIR_i` (`ddc_400m.v:283`); `ddc_400m_enhanced` as `CDC_FIR_q` (`ddc_400m.v:290`) | **DEFINED** |
| `axis_fft_behav` | `axis_fft_behav.v:29` | `FFT_enhanced` as `u_core` (`FFT_enhanced.v:35`); `xfft_32` as `u_core` (`xfft_32.v:37`) | **DEFINED** |
| `cdc_adc_to_processing` | `unused_orig/cdc_modules.v:6` | - | **UNUSED** |
| `cdc_handshake` | `unused_orig/cdc_modules.v:156` | - | **UNUSED** |
| `cdc_single_bit` | `unused_orig/cdc_modules.v:129` | - | **UNUSED** |
| `chirp_memory_loader_param` | `chirp_memory_loader_param.v:7` | `radar_receiver_final` as `chirp_mem` (`radar_receiver_final.v:270`) | **DEFINED** |
| `cic_decimator_4x_enhanced` | `cic_decimator_4x_enhanced.v:5` | `ddc_400m_enhanced` as `cic_i_inst` (`ddc_400m.v:250`); `ddc_400m_enhanced` as `cic_q_inst` (`ddc_400m.v:262`) | **DEFINED** |
| `clk_gen` | `clk_gen.v:13` | `radar_receiver_final` as `u_clk_gen` (`radar_receiver_final.v:165`) | **DEFINED** |
| `dac_interface_enhanced` | `dac_interface_single.v:1` | `radar_transmitter` as `dac_interface_inst` (`radar_transmitter.v:148`) | **DEFINED** |
| `ddc_400m_enhanced` | `ddc_400m.v:11` | `radar_receiver_final` as `ddc` (`radar_receiver_final.v:120`) | **DEFINED** |
| `ddc_4x_100m` | `ddc_4x_100m.v:29` | `radar_receiver_final` as `ddc` (`radar_receiver_final.v:203`) | **DEFINED** |
| `ddc_input_interface` | `ddc_input_interface.v:3` | `radar_receiver_final` as `ddc_if` (`radar_receiver_final.v:218`) | **DEFINED** |
| `doppler_processor_optimized` | `doppler_processor.v:12` | `radar_receiver_final` as `doppler_proc` (`radar_receiver_final.v:340`) | **DEFINED** |
| `edge_detector_enhanced` | `edge_detector.v:8` | `radar_receiver_final` as `rx_chirp_edge` (`radar_receiver_final.v:234`); `radar_receiver_final` as `rx_elevation_edge` (`radar_receiver_final.v:236`); `radar_receiver_final` as `rx_azimuth_edge` (`radar_receiver_final.v:238`); `radar_transmitter` as `chirp_edge` (`radar_transmitter.v:93`); `radar_transmitter` as `elevation_edge` (`radar_transmitter.v:100`); `radar_transmitter` as `azimuth_edge` (`radar_transmitter.v:107`) | **DEFINED** |
| `fft_1024_forward_enhanced` | `fft_1024_forward.v:6` | `matched_filter_processing_chain` as `u_fft_fwd` (`matched_filter_processing_chain.v:91`) | **DEFINED** |
| `fft_1024_inverse_enhanced` | `fft_1024_inverse.v:6` | `matched_filter_processing_chain` as `u_fft_inv` (`matched_filter_processing_chain.v:155`) | **DEFINED** |
| `fir_lowpass_parallel_enhanced` | `fir_lowpass.v:3` | `ddc_400m_enhanced` as `fir_i_inst` (`ddc_400m.v:305`); `ddc_400m_enhanced` as `fir_q_inst` (`ddc_400m.v:317`); `ddc_4x_100m` as `fir_i_inst` (`ddc_4x_100m.v:244`); `ddc_4x_100m` as `fir_q_inst` (`ddc_4x_100m.v:247`) | **DEFINED** |
| `frequency_matched_filter` | `frequency_matched_filter.v:8` | `matched_filter_processing_chain` as `u_fmf` (`matched_filter_processing_chain.v:140`) | **DEFINED** |
| `host_bridge_spi` | `host_bridge_spi.v:28` | `radar_system_top` as `host_bridge` (`radar_system_top.v:542`) | **DEFINED** |
| `latency_buffer_2159` | `unused_orig/latency_buffer_2159.v:4` | - | **UNUSED** |
| `level_shifter_interface` | `level_shifter_interface.v:10` | `radar_transmitter` as `ls_adar1` (`radar_transmitter.v:168`); `radar_transmitter` as `ls_adar2` (`radar_transmitter.v:175`); `radar_transmitter` as `ls_adar3` (`radar_transmitter.v:182`); `radar_transmitter` as `ls_adar4` (`radar_transmitter.v:189`) | **DEFINED** |
| `lfsr_dither_enhanced` | `ddc_400m.v:368` | `ddc_400m_enhanced` as `phase_dither_gen` (`ddc_400m.v:149`) | **DEFINED** |
| `lvds_to_cmos_400m` | `unused_orig/lvds_to_cmos_400m.v:2` | - | **UNUSED** |
| `matched_filter_multi_segment` | `matched_filter_multi_segment.v:31` | `radar_receiver_final` as `mf_dual` (`radar_receiver_final.v:286`) | **DEFINED** |
| `matched_filter_processing_chain` | `matched_filter_processing_chain.v:39` | `matched_filter_multi_segment` as `m_f_p_c` (`matched_filter_multi_segment.v:302`) | **DEFINED** |
| `nco_400m_enhanced` | `nco_400m_enhanced.v:20` | `ddc_400m_enhanced` as `nco_core` (`ddc_400m.v:170`) | **DEFINED** |
| `plfm_chirp_controller_enhanced` | `plfm_chirp_controller.v:5` | `radar_transmitter` as `plfm_chirp_inst` (`radar_transmitter.v:115`) | **DEFINED** |
| `radar_control_regs` | `radar_control_regs.v:40` | `radar_system_top` as `ctl_regs` (`radar_system_top.v:325`) | **DEFINED** |
| `radar_receiver_final` | `radar_receiver_final.v:29` | `radar_system_top` as `rx_inst` (`radar_system_top.v:354`) | **DEFINED** |
| `radar_system_top` | `radar_system_top.v:36` | - | **UNUSED** |
| `radar_transmitter` | `radar_transmitter.v:22` | `radar_system_top` as `tx_inst` (`radar_system_top.v:258`) | **DEFINED** |
| `range_bin_decimator` | `range_bin_decimator.v:20` | `radar_receiver_final` as `range_decim` (`radar_receiver_final.v:316`) | **DEFINED** |
| `rd_map_packer` | `rd_map_packer.v:8` | `radar_system_top` as `rd_packer` (`radar_system_top.v:511`) | **DEFINED** |
| `reset_synchronizer` | `reset_synchronizer.v:11` | `ad9484_iserdes_capture` as `u_rst_div` (`ad9484_iserdes_capture.v:76`); `ad9484_lvds_to_cmos_400m` as `u_rst_sync` (`ad9484_lvds_to_cmos_400m.v:138`); `radar_receiver_final` as `rst_sync_400m` (`radar_receiver_final.v:114`) | **DEFINED** |
| `usb_data_interface` | `usb_data_interface.v:36` | `radar_system_top` as `usb_inst` (`radar_system_top.v:566`) | **DEFINED** |
| `usb_packet_analyzer` | `unused_orig/usb_packet_analyzer.v:10` | - | **UNUSED** |
| `xfft_32` | `xfft_32.v:21` | `doppler_processor_optimized` as `fft_inst` (`doppler_processor.v:303`) | **DEFINED** |

## Files scanned

- `FFT_enhanced.v` - 1 module definition(s)
- `ad9484_iserdes_capture.v` - 1 module definition(s)
- `ad9484_lvds_to_cmos_400m.v` - 1 module definition(s)
- `adc_capture_calib.v` - 1 module definition(s)
- `async_fifo.v` - 1 module definition(s)
- `axis_fft_behav.v` - 1 module definition(s)
- `chirp_memory_loader_param.v` - 1 module definition(s)
- `cic_decimator_4x_enhanced.v` - 1 module definition(s)
- `clk_gen.v` - 1 module definition(s)
- `dac_interface_single.v` - 1 module definition(s)
- `ddc_400m.v` - 2 module definition(s)
- `ddc_4x_100m.v` - 1 module definition(s)
- `ddc_input_interface.v` - 1 module definition(s)
- `doppler_processor.v` - 1 module definition(s)
- `edge_detector.v` - 1 module definition(s)
- `fft_1024_forward.v` - 1 module definition(s)
- `fft_1024_inverse.v` - 1 module definition(s)
- `fir_lowpass.v` - 1 module definition(s)
- `frequency_matched_filter.v` - 1 module definition(s)
- `host_bridge_spi.v` - 1 module definition(s)
- `level_shifter_interface.v` - 1 module definition(s)
- `matched_filter_multi_segment.v` - 1 module definition(s)
- `matched_filter_processing_chain.v` - 1 module definition(s)
- `nco_400m_enhanced.v` - 1 module definition(s)
- `plfm_chirp_controller.v` - 1 module definition(s)
- `radar_control_regs.v` - 1 module definition(s)
- `radar_receiver_final.v` - 1 module definition(s)
- `radar_system_top.v` - 1 module definition(s)
- `radar_transmitter.v` - 1 module definition(s)
- `range_bin_decimator.v` - 1 module definition(s)
- `rd_map_packer.v` - 1 module definition(s)
- `reset_synchronizer.v` - 1 module definition(s)
- `sim/unisim_sim_models.v` - 9 module definition(s)
- `unused_orig/ad9484_interface_400m.v` - 1 module definition(s)
- `unused_orig/cdc_modules.v` - 3 module definition(s)
- `unused_orig/latency_buffer_2159.v` - 1 module definition(s)
- `unused_orig/lvds_to_cmos_400m.v` - 1 module definition(s)
- `unused_orig/usb_packet_analyzer.v` - 1 module definition(s)
- `usb_data_interface.v` - 1 module definition(s)
- `xfft_32.v` - 1 module definition(s)

## Notes

- MISSING = instantiated somewhere in the tree but no `module` of that name exists in the scanned files. Names with AXI4-Stream ports (`s_axis_config_*`, `m_axis_data_*`) indicate Xilinx IP cores whose `.xci` is not in the repository; the others are RTL modules that were never committed.
- UNUSED = defined but never instantiated (orphans or the testbench root).
- The script does not evaluate `` `ifdef `` blocks; all text is scanned.
