# ============================================================================
# radar_system_top — CANDIDATE pin constraints DERIVED FROM SCHEMATIC
# Source   : 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch  (part U42 = XC7A50T-2FTG256I)
# Generated: 2026-10-08 by tools/gen_xdc_from_schematic.py
# STATUS   : NOT VERIFIED ON HARDWARE. Each line cites the schematic net and FPGA pad.
#            Review PIN_MAP_FROM_SCHEMATIC.md before use. Timing constraints are NOT
#            included here — keep them in a separate file (see cntrt.xdc lines 14-27).
# NOTE     : schematic device is XC7A50T-2FTG256I; RTL/README state XC7A100T.
#            FTG256 ball names are shared across XC7A50T/XC7A100T but the part number
#            used in Vivado MUST match the board (UNRESOLVED — designer to confirm).
# ============================================================================

set_property PACKAGE_PIN E12 [get_ports {clk_100m}]   ;# net FPGA_SYS_CLOCK, pin IO_L13P_T2_MRCC_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {clk_100m}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN C13 [get_ports {clk_120m_dac}]   ;# net FPGA_DAC_CLOCK, pin IO_L12N_T1_MRCC_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {clk_120m_dac}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN N14 [get_ports {adc_dco_p}]   ;# net ADC_DCO_P, pin IO_L12P_T1_MRCC_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_dco_p}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN P14 [get_ports {adc_dco_n}]   ;# net ADC_DCO_N, pin IO_L12N_T1_MRCC_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_dco_n}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T5 [get_ports {adc_pwdn}]   ;# net ADC_PWRD, pin IO_L23N_T3_A02_D18_14 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {adc_pwdn}]   ;# bank 14 VCCO=+3V3_FPGA
set_property PACKAGE_PIN A15 [get_ports {dac_sleep}]   ;# net DAC_SLEEP, pin IO_L9N_T1_DQS_AD3N_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_sleep}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN C11 [get_ports {tx_mixer_en}]   ;# net MIX_TX_EN, pin IO_L11P_T1_SRCC_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {tx_mixer_en}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN D11 [get_ports {rx_mixer_en}]   ;# net MIX_RX_EN, pin IO_L14N_T2_SRCC_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {rx_mixer_en}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN G15 [get_ports {fpga_rf_switch}]   ;# net M3S_VCTRL, pin IO_L24N_T3_RS0_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {fpga_rf_switch}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN F13 [get_ports {stm32_new_chirp}]   ;# net DIG_0, pin IO_L16N_T2_A27_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_new_chirp}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN E16 [get_ports {stm32_new_elevation}]   ;# net DIG_1, pin IO_L17P_T2_A26_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_new_elevation}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN D16 [get_ports {stm32_new_azimuth}]   ;# net DIG_2, pin IO_L17N_T2_A25_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_new_azimuth}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN F15 [get_ports {stm32_mixers_enable}]   ;# net DIG_3, pin IO_L18P_T2_A24_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_mixers_enable}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN E15 [get_ports {reset_n}]   ;# net DIG_4, pin IO_L18N_T2_A23_15 [MEDIUM]
set_property IOSTANDARD LVCMOS33 [get_ports {reset_n}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN J16 [get_ports {stm32_sclk_3v3}]   ;# net STM32_SCLK1, pin IO_L23N_T3_FWE_B_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_sclk_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN H13 [get_ports {stm32_mosi_3v3}]   ;# net STM32_MOSI1, pin IO_L20N_T3_A19_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_mosi_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN G14 [get_ports {stm32_miso_3v3}]   ;# net STM32_MISO1, pin IO_L21P_T3_DQS_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_miso_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN P5 [get_ports {stm32_sclk_1v8}]   ;# net STM32_SCLK_1V8, pin IO_L10P_T1_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_sclk_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN M1 [get_ports {stm32_mosi_1v8}]   ;# net STM32_MOSI_1V8, pin IO_L2N_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_mosi_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN N3 [get_ports {stm32_miso_1v8}]   ;# net STM32_MISO_1V8, pin IO_L3P_T0_DQS_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_miso_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN P15 [get_ports {adc_d_p[0]}]   ;# net ADC_D0_P, pin IO_L8P_T1_D11_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[0]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R15 [get_ports {adc_d_p[1]}]   ;# net ADC_D1_P, pin IO_L9P_T1_DQS_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[1]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T14 [get_ports {adc_d_p[2]}]   ;# net ADC_D2_P, pin IO_L10P_T1_D14_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[2]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R13 [get_ports {adc_d_p[3]}]   ;# net ADC_D3_P, pin IO_L16P_T2_CSI_B_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[3]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R10 [get_ports {adc_d_p[4]}]   ;# net ADC_D4_P, pin IO_L17P_T2_A14_D30_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[4]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T9 [get_ports {adc_d_p[5]}]   ;# net ADC_D5_P, pin IO_L22P_T3_A05_D21_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[5]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T7 [get_ports {adc_d_p[6]}]   ;# net ADC_D6_P, pin IO_L21P_T3_DQS_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[6]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R6 [get_ports {adc_d_p[7]}]   ;# net ADC_D7_P, pin IO_L24P_T3_A01_D17_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_p[7]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN P16 [get_ports {adc_d_n[0]}]   ;# net ADC_D0_N, pin IO_L8N_T1_D12_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[0]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R16 [get_ports {adc_d_n[1]}]   ;# net ADC_D1_N, pin IO_L9N_T1_DQS_D13_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[1]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T15 [get_ports {adc_d_n[2]}]   ;# net ADC_D2_N, pin IO_L10N_T1_D15_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[2]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T13 [get_ports {adc_d_n[3]}]   ;# net ADC_D3_N, pin IO_L16N_T2_A15_D31_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[3]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R11 [get_ports {adc_d_n[4]}]   ;# net ADC_D4_N, pin IO_L17N_T2_A13_D29_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[4]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T10 [get_ports {adc_d_n[5]}]   ;# net ADC_D5_N, pin IO_L22N_T3_A04_D20_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[5]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN T8 [get_ports {adc_d_n[6]}]   ;# net ADC_D6_N, pin IO_L21N_T3_DQS_A06_D22_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[6]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN R7 [get_ports {adc_d_n[7]}]   ;# net ADC_D7_N, pin IO_L24N_T3_A00_D16_14 [HIGH]
set_property IOSTANDARD LVDS_25 [get_ports {adc_d_n[7]}]   ;# bank 14 VCCO=+3V3_FPGA: LVDS_25 input with DIFF_TERM requires 2.5 V VCCO (UG471) — REQUIRES VERIFICATION
set_property PACKAGE_PIN A14 [get_ports {dac_data[0]}]   ;# net DAC_0, pin IO_L7N_T1_AD2N_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[0]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN A13 [get_ports {dac_data[1]}]   ;# net DAC_1, pin IO_L7P_T1_AD2P_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[1]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN A12 [get_ports {dac_data[2]}]   ;# net DAC_2, pin IO_L5N_T0_AD9N_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[2]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN B11 [get_ports {dac_data[3]}]   ;# net DAC_3, pin IO_L4N_T0_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[3]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN B10 [get_ports {dac_data[4]}]   ;# net DAC_4, pin IO_L4P_T0_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[4]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN A10 [get_ports {dac_data[5]}]   ;# net DAC_5, pin IO_L3N_T0_DQS_AD1N_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[5]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN A9 [get_ports {dac_data[6]}]   ;# net DAC_6, pin IO_L2N_T0_AD8N_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[6]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN A8 [get_ports {dac_data[7]}]   ;# net DAC_7, pin IO_L2P_T0_AD8P_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {dac_data[7]}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN F14 [get_ports {stm32_cs_adar1_3v3}]   ;# net ADAR_1_CS_3V3, pin IO_L21N_T3_DQS_A18_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_cs_adar1_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN H16 [get_ports {stm32_cs_adar2_3v3}]   ;# net ADAR_2_CS_3V3, pin IO_L22P_T3_A17_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_cs_adar2_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN G16 [get_ports {stm32_cs_adar3_3v3}]   ;# net ADAR_3_CS_3V3, pin IO_L22N_T3_A16_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_cs_adar3_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN J15 [get_ports {stm32_cs_adar4_3v3}]   ;# net ADAR_4_CS_3V3, pin IO_L23P_T3_FOE_B_15 [HIGH]
set_property IOSTANDARD LVCMOS33 [get_ports {stm32_cs_adar4_3v3}]   ;# bank 15 VCCO=+3V3_FPGA
set_property PACKAGE_PIN L5 [get_ports {stm32_cs_adar1_1v8}]   ;# net ADAR_1_CS_1V8, pin IO_0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_cs_adar1_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN L4 [get_ports {stm32_cs_adar2_1v8}]   ;# net ADAR_2_CS_1V8, pin IO_L1P_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_cs_adar2_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN M4 [get_ports {stm32_cs_adar3_1v8}]   ;# net ADAR_3_CS_1V8, pin IO_L1N_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_cs_adar3_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN M2 [get_ports {stm32_cs_adar4_1v8}]   ;# net ADAR_4_CS_1V8, pin IO_L2P_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {stm32_cs_adar4_1v8}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN P3 [get_ports {adar_tx_load_1}]   ;# net ADAR_TX_LOAD_1, pin IO_L5N_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tx_load_1}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN T4 [get_ports {adar_tx_load_2}]   ;# net ADAR_TX_LOAD_2, pin IO_L9P_T1_DQS_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tx_load_2}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN R3 [get_ports {adar_tx_load_3}]   ;# net ADAR_TX_LOAD_3, pin IO_L8P_T1_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tx_load_3}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN R2 [get_ports {adar_tx_load_4}]   ;# net ADAR_TX_LOAD_4, pin IO_L7P_T1_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tx_load_4}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN M5 [get_ports {adar_rx_load_1}]   ;# net ADAR_RX_LOAD_1, pin IO_L6P_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_rx_load_1}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN T2 [get_ports {adar_rx_load_2}]   ;# net ADAR_RX_LOAD_2, pin IO_L8N_T1_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_rx_load_2}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN R1 [get_ports {adar_rx_load_3}]   ;# net ADAR_RX_LOAD_3, pin IO_L7N_T1_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_rx_load_3}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN N4 [get_ports {adar_rx_load_4}]   ;# net ADAR_RX_LOAD_4, pin IO_L6N_T0_VREF_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_rx_load_4}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN N2 [get_ports {adar_tr_1}]   ;# net ADAR_TR_1, pin IO_L3N_T0_DQS_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tr_1}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN N1 [get_ports {adar_tr_2}]   ;# net ADAR_TR_2, pin IO_L4P_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tr_2}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN P1 [get_ports {adar_tr_3}]   ;# net ADAR_TR_3, pin IO_L4N_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tr_3}]   ;# bank 34 VCCO=+1V8_FPGA
set_property PACKAGE_PIN P4 [get_ports {adar_tr_4}]   ;# net ADAR_TR_4, pin IO_L5P_T0_34 [HIGH]
set_property IOSTANDARD LVCMOS18 [get_ports {adar_tr_4}]   ;# bank 34 VCCO=+1V8_FPGA

# ---------------- UNRESOLVED RTL PORTS (no schematic evidence) ----------------
# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: dac_clk
#     reason: RTL drives a DAC clock output, but the board clocks the AD9708 from AD9523 OUT10 (main.cpp:1019-1020); no FPGA net
# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: ft601_clk_in
#     reason: FT601Q-B-T (U6) is placed in the schematic but has 0 of 77 pins connected; its decoupling parts are parked outside the board outline
# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: ft601_data[*], ft601_be[*], ft601_txe_n, ft601_rxf_n, ft601_txe, ft601_rxf, ft601_wr_n, ft601_rd_n, ft601_oe_n, ft601_siwu_n, ft601_srb[*], ft601_swb[*], ft601_clk_out
#     reason: FT601 not wired on Main Board
# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: (DIG_5..DIG_7)
#     reason: schematic nets DIG_5/6/7 (STM32 PD13/14/15 configured as INPUTS in main.cpp:2313-2317) reach FPGA H11/G12/H12 but no RTL port uses them
# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: current_elevation[*], current_azimuth[*], current_chirp[*], new_chirp_frame
#     reason: no status outputs on the schematic
# UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION: dbg_doppler_data[*], dbg_doppler_valid, dbg_doppler_bin[*], dbg_range_bin[*], system_status[*]
#     reason: debug outputs; no schematic nets (internal-only in a real build; remove from top or leave unconstrained with -quiet)

# ---------------- schematic FPGA nets with NO RTL port ----------------
# ADC_OR_N               pad N6   pin IO_L19N_T3_A09_D25_VREF_14
# ADC_OR_P               pad M6   pin IO_L19P_T3_A10_D26_14
# DIG_5                  pad H11  pin IO_L19P_T3_A22_15
# DIG_6                  pad G12  pin IO_L19N_T3_A21_VREF_15
# DIG_7                  pad H12  pin IO_L20P_T3_A20_15
# FPGA_ADC_CLOCK_N       pad N12  pin IO_L13N_T2_MRCC_14
# FPGA_ADC_CLOCK_P       pad N11  pin IO_L13P_T2_MRCC_14
# FPGA_CLOCK_TEST        pad H14  pin IO_L24P_T3_RS1_15
# FPGA_FLASH_CLK         pad E8   pin CCLK_0
# FPGA_FLASH_DQ0         pad J13  pin IO_L1P_T0_D00_MOSI_14
# FPGA_FLASH_DQ1         pad J14  pin IO_L1N_T0_D01_DIN_14
# FPGA_FLASH_DQ2         pad K15  pin IO_L2P_T0_D02_14
# FPGA_FLASH_DQ3         pad K16  pin IO_L2N_T0_D03_14
# FPGA_FLASH_NCS         pad L12  pin IO_L6P_T0_FCS_B_14
# FPGA_FLASH_NRST        pad L13  pin IO_L5N_T0_D07_14
# FPGA_PUDC_B            pad L15  pin IO_L3P_T0_DQS_PUDC_B_14
# FPGA_TCK               pad L7   pin TCK_0
# FPGA_TDI               pad N7   pin TDI_0
# FPGA_TDO               pad N8   pin TDO_0
# FPGA_TMS               pad M7   pin TMS_0
