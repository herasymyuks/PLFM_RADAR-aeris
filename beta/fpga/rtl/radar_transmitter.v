`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// radar_transmitter  -  chirp controller + DAC interface + ADAR1000 control.
// BETA rewrite of 9_Firmware/9_2_FPGA/radar_transmitter.v (ports unchanged).
// Changes (beta/fpga/CHANGELOG.md):
//   * the three edge detectors are clocked by clk_120m_dac instead of clk_100m
//     (original :93-112) so that their single-cycle pulses are consumed in the
//     same domain as the chirp FSM (plfm_chirp_controller_enhanced runs on
//     clk_120m); previously a 10 ns pulse was sampled by a 120 MHz FSM.
//   * level_shifter_interface (an orphan in the original) is instantiated four
//     times so that the STM32 SPI pass-through outputs (original :59-71,
//     undriven) are driven. Instance 1 carries SCLK/MOSI/MISO + CS1, instances
//     2..4 carry CS2..CS4 only. The pass-through re-times every SPI line by one
//     clk_100m cycle (10 ns, +1 cycle MISO return) - acceptable for SCLK up to a
//     few MHz; the STM32 SPI1 clock must be checked against this (README).
//   * spi_passthrough_gate input (host-link option B): while high (bridge chip
//     select active) the ADAR1000 CS lines are held high and SCLK/MOSI idle on
//     the 1.8 V side, so a bridge transfer on the shared SPI1 bus never reaches
//     the beamformers. passthrough_miso carries the ADAR1000 MISO; the top level
//     multiplexes it with the bridge MISO onto stm32_miso_3v3.
//////////////////////////////////////////////////////////////////////////////////
module radar_transmitter(
    // System Clocks
    input wire clk_100m,           // System clock (SPI pass-through re-timing)
    input wire clk_120m_dac,       // 120MHz DAC clock (chirp FSM domain)
    input wire reset_n,

    // DAC Interface
    output wire [7:0] dac_data,
    output wire dac_clk,
    output wire dac_sleep,
    output wire rx_mixer_en,
    output wire tx_mixer_en,

    // STM32 Control Interface
    input wire stm32_new_chirp,
    input wire stm32_new_elevation,
    input wire stm32_new_azimuth,
    input wire stm32_mixers_enable,

    output wire fpga_rf_switch,

    // ADAR1000 Control Interface
    output wire adar_tx_load_1,
    output wire adar_rx_load_1,
    output wire adar_tx_load_2,
    output wire adar_rx_load_2,
    output wire adar_tx_load_3,
    output wire adar_rx_load_3,
    output wire adar_tx_load_4,
    output wire adar_rx_load_4,
    output wire adar_tr_1,
    output wire adar_tr_2,
    output wire adar_tr_3,
    output wire adar_tr_4,

    // Level Shifter SPI Interface (STM32F7 to ADAR1000)
    input wire spi_passthrough_gate,   // BETA host-link: 1 = hold the ADAR1000 SPI idle
    input wire stm32_sclk_3v3,
    input wire stm32_mosi_3v3,
    output wire stm32_miso_3v3,        // ADAR1000 MISO after the level shifter (pass-through only)
    input wire stm32_cs_adar1_3v3,
    input wire stm32_cs_adar2_3v3,
    input wire stm32_cs_adar3_3v3,
    input wire stm32_cs_adar4_3v3,

    output wire stm32_sclk_1v8,
    output wire stm32_mosi_1v8,
    input wire stm32_miso_1v8,
    output wire stm32_cs_adar1_1v8,
    output wire stm32_cs_adar2_1v8,
    output wire stm32_cs_adar3_1v8,
    output wire stm32_cs_adar4_1v8,

    // Beam Position Tracking
    output wire [5:0] current_elevation,
    output wire [5:0] current_azimuth,
    output wire [5:0] current_chirp,
    output wire new_chirp_frame
    );

// Edge Detection Signals
wire new_chirp_pulse;
wire new_elevation_pulse;
wire new_azimuth_pulse;

// Chirp Control Signals
wire [7:0] chirp_data;
wire chirp_valid;
wire chirp_sequence_done;

// STM32 toggle lines -> single-cycle pulses in the chirp FSM clock domain
edge_detector_enhanced chirp_edge (
    .clk(clk_120m_dac),
    .reset_n(reset_n),
    .signal_in(stm32_new_chirp),
    .rising_falling_edge(new_chirp_pulse)
);

edge_detector_enhanced elevation_edge (
    .clk(clk_120m_dac),
    .reset_n(reset_n),
    .signal_in(stm32_new_elevation),
    .rising_falling_edge(new_elevation_pulse)
);

edge_detector_enhanced azimuth_edge (
    .clk(clk_120m_dac),
    .reset_n(reset_n),
    .signal_in(stm32_new_azimuth),
    .rising_falling_edge(new_azimuth_pulse)
);

// Enhanced PLFM Chirp Generation
plfm_chirp_controller_enhanced plfm_chirp_inst (
    .clk_120m(clk_120m_dac),
    .clk_100m(clk_100m),
    .reset_n(reset_n),
    .new_chirp(new_chirp_pulse),
    .new_elevation(new_elevation_pulse),
    .new_azimuth(new_azimuth_pulse),
    .new_chirp_frame(new_chirp_frame),
    .mixers_enable(stm32_mixers_enable),
    .chirp_data(chirp_data),
    .chirp_valid(chirp_valid),
    .chirp_done(chirp_sequence_done),
    .rf_switch_ctrl(fpga_rf_switch),
    .rx_mixer_en(rx_mixer_en),
    .tx_mixer_en(tx_mixer_en),
    .adar_tx_load_1(adar_tx_load_1),
    .adar_rx_load_1(adar_rx_load_1),
    .adar_tx_load_2(adar_tx_load_2),
    .adar_rx_load_2(adar_rx_load_2),
    .adar_tx_load_3(adar_tx_load_3),
    .adar_rx_load_3(adar_rx_load_3),
    .adar_tx_load_4(adar_tx_load_4),
    .adar_rx_load_4(adar_rx_load_4),
    .adar_tr_1(adar_tr_1),
    .adar_tr_2(adar_tr_2),
    .adar_tr_3(adar_tr_3),
    .adar_tr_4(adar_tr_4),
    .elevation_counter(current_elevation),
    .azimuth_counter(current_azimuth),
    .chirp_counter(current_chirp)
);

// Enhanced DAC Interface
dac_interface_enhanced dac_interface_inst (
    .clk_120m(clk_120m_dac),
    .reset_n(reset_n),
    .chirp_data(chirp_data),
    .chirp_valid(chirp_valid),
    .dac_data(dac_data),
    .dac_clk(dac_clk),
    .dac_sleep(dac_sleep)
);

// STM32 (3.3 V bank 15) -> ADAR1000 (1.8 V bank 34) SPI pass-through.
// Gate (host-link option B): the 3.3 V inputs are forced idle (CS high, SCLK/MOSI low)
// before the level shifters while spi_passthrough_gate is high.
wire ls_sclk_in = stm32_sclk_3v3 & ~spi_passthrough_gate;
wire ls_mosi_in = stm32_mosi_3v3 & ~spi_passthrough_gate;
wire ls_cs1_in  = stm32_cs_adar1_3v3 | spi_passthrough_gate;
wire ls_cs2_in  = stm32_cs_adar2_3v3 | spi_passthrough_gate;
wire ls_cs3_in  = stm32_cs_adar3_3v3 | spi_passthrough_gate;
wire ls_cs4_in  = stm32_cs_adar4_3v3 | spi_passthrough_gate;

level_shifter_interface ls_adar1 (
    .clk(clk_100m), .reset_n(reset_n),
    .sclk_3v3(ls_sclk_in), .mosi_3v3(ls_mosi_in), .miso_3v3(stm32_miso_3v3),
    .cs_3v3(ls_cs1_in),
    .sclk_1v8(stm32_sclk_1v8), .mosi_1v8(stm32_mosi_1v8), .miso_1v8(stm32_miso_1v8),
    .cs_1v8(stm32_cs_adar1_1v8)
);
level_shifter_interface ls_adar2 (
    .clk(clk_100m), .reset_n(reset_n),
    .sclk_3v3(ls_sclk_in), .mosi_3v3(ls_mosi_in), .miso_3v3(),
    .cs_3v3(ls_cs2_in),
    .sclk_1v8(), .mosi_1v8(), .miso_1v8(1'b0),
    .cs_1v8(stm32_cs_adar2_1v8)
);
level_shifter_interface ls_adar3 (
    .clk(clk_100m), .reset_n(reset_n),
    .sclk_3v3(ls_sclk_in), .mosi_3v3(ls_mosi_in), .miso_3v3(),
    .cs_3v3(ls_cs3_in),
    .sclk_1v8(), .mosi_1v8(), .miso_1v8(1'b0),
    .cs_1v8(stm32_cs_adar3_1v8)
);
level_shifter_interface ls_adar4 (
    .clk(clk_100m), .reset_n(reset_n),
    .sclk_3v3(ls_sclk_in), .mosi_3v3(ls_mosi_in), .miso_3v3(),
    .cs_3v3(ls_cs4_in),
    .sclk_1v8(), .mosi_1v8(), .miso_1v8(1'b0),
    .cs_1v8(stm32_cs_adar4_1v8)
);

/* verilator lint_off UNUSEDSIGNAL */
wire unused_done = chirp_sequence_done;   // chirp_done is not consumed at the top level (original behaviour)
/* verilator lint_on UNUSEDSIGNAL */

endmodule
