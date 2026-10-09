`timescale 1ns / 1ps

/**
 * radar_system_top.v
 * 
 * Complete Radar System Top Module
 * Integrates:
 * - Radar Transmitter (PLFM chirp generation)
 * - Radar Receiver (ADC interface, DDC, matched filtering, Doppler processing)
 * - USB Data Interface (FT601 for high-speed data transfer)
 * 
 * Clock domains:
 * - clk_100m: System clock (100MHz)
 * - clk_120m_dac: DAC clock (120MHz)
 * - adc_dco: 400 MHz ADC data clock (inside the receiver)
 * - ft601_clk_in: FT601 clock - NOT USED (FT601 not wired on the board; port kept)
 *
 * BETA (beta/fpga/CHANGELOG.md): see the list of changes vs 9_Firmware/9_2_FPGA/radar_system_top.v:
 *  - syntax: wire inside always (:312) hoisted; rx_cfar_* wire -> reg (:155-156)
 *  - register map (radar_control_regs) drives use_long_chirp / adc_pwdn / CFAR threshold /
 *    decimation controls; write port tied off (no host path on the board)
 *  - receiver gets the STM32 toggle lines and register controls (new ports)
 *  - USB packetiser receives the real decimated range profile instead of the Doppler data
 *  - BUFG on ft601_clk_in removed (clock unused)
 *  - host-link option B (engineering/DESIGN/HOST_LINK): rd_map_packer + host_bridge_spi on the
 *    shared STM32 SPI1 lines with three new ports (spi_bridge_cs_n = DIG_5, spi_bridge_drdy =
 *    DIG_6, spi_bridge_spare = DIG_7); the ADAR1000 pass-through is gated while the bridge CS is
 *    low. The FT601 path (usb_data_interface, option A) is unchanged.
 */

module radar_system_top (
    // System Clocks
    input wire clk_100m,                // 100MHz system clock
    input wire clk_120m_dac,             // 120MHz DAC clock
    input wire ft601_clk_in,             // FT601 clock (100MHz)
    input wire reset_n,                   // Active-low reset
    
    // ========== TRANSMITTER INTERFACES ==========
    
    // DAC Interface
    output wire [7:0] dac_data,
    output wire dac_clk,
    output wire dac_sleep,
    
    // RF Switch Control
    output wire fpga_rf_switch,
    
    // Mixer Enables
    output wire rx_mixer_en,
    output wire tx_mixer_en,
    
    // ADAR1000 Beamformer Control (via level shifters)
    output wire adar_tx_load_1, adar_rx_load_1,
    output wire adar_tx_load_2, adar_rx_load_2,
    output wire adar_tx_load_3, adar_rx_load_3,
    output wire adar_tx_load_4, adar_rx_load_4,
    output wire adar_tr_1, adar_tr_2, adar_tr_3, adar_tr_4,
    
    // Level Shifter SPI Interface (STM32F7 to ADAR1000)
    input wire stm32_sclk_3v3,
    input wire stm32_mosi_3v3,
    output wire stm32_miso_3v3,
    input wire stm32_cs_adar1_3v3, stm32_cs_adar2_3v3, 
    input wire stm32_cs_adar3_3v3, stm32_cs_adar4_3v3,
    
    output wire stm32_sclk_1v8,
    output wire stm32_mosi_1v8,
    input wire stm32_miso_1v8,
    output wire stm32_cs_adar1_1v8, stm32_cs_adar2_1v8,
    output wire stm32_cs_adar3_1v8, stm32_cs_adar4_1v8,
    
    // ========== RECEIVER INTERFACES ==========
    
    // ADC Physical Interface (LVDS)
    input wire [7:0] adc_d_p,            // ADC Data P (LVDS)
    input wire [7:0] adc_d_n,            // ADC Data N (LVDS)
    input wire adc_dco_p,                 // Data Clock Output P (400MHz LVDS)
    input wire adc_dco_n,                 // Data Clock Output N (400MHz LVDS)
    output wire adc_pwdn,                  // ADC Power Down
    
    // ========== STM32 CONTROL INTERFACES ==========
    
    // Chirp/Beam Control (toggle signals from STM32)
    input wire stm32_new_chirp,
    input wire stm32_new_elevation,
    input wire stm32_new_azimuth,
    input wire stm32_mixers_enable,

    // ========== HOST-LINK OPTION B (SPI bridge on SPI1, BETA) ==========
    input wire spi_bridge_cs_n,          // DIG_5 (H11): FPGA chip select, active low
    output wire spi_bridge_drdy,         // DIG_6 (G12): a complete frame is ready to be read
    output wire spi_bridge_spare,        // DIG_7 (H12): packer overflow flag (frame dropped)
    
    // ========== FT601 USB 3.0 INTERFACE ==========
    
    // Data bus
    inout wire [31:0] ft601_data,         // 32-bit bidirectional data bus
    output wire [1:0] ft601_be,            // Byte enable
    
    // Control signals
    output wire ft601_txe_n,                // Transmit enable (active low)
    output wire ft601_rxf_n,                // Receive enable (active low)
    input wire ft601_txe,                    // Transmit FIFO empty
    input wire ft601_rxf,                    // Receive FIFO full
    output wire ft601_wr_n,                  // Write strobe (active low)
    output wire ft601_rd_n,                  // Read strobe (active low)
    output wire ft601_oe_n,                  // Output enable (active low)
    output wire ft601_siwu_n,                 // Send immediate / Wakeup
    
    // FIFO flags
    input wire [1:0] ft601_srb,              // Selected read buffer
    input wire [1:0] ft601_swb,               // Selected write buffer
    
    // Clock output (optional)
    output wire ft601_clk_out,
    
    // ========== STATUS OUTPUTS ==========
    
    // Beam position tracking
    output wire [5:0] current_elevation,
    output wire [5:0] current_azimuth,
    output wire [5:0] current_chirp,
    output wire new_chirp_frame,
    
    // Doppler processing outputs (for debugging)
    output wire [31:0] dbg_doppler_data,
    output wire dbg_doppler_valid,
    output wire [4:0] dbg_doppler_bin,
    output wire [5:0] dbg_range_bin,
    
    // System status
    output wire [3:0] system_status
);

// ============================================================================
// PARAMETERS
// ============================================================================

// System configuration
parameter USE_LONG_CHIRP = 1'b1;          // Default to long chirp
parameter DOPPLER_ENABLE = 1'b1;           // Enable Doppler processing (not used - kept for compatibility)
parameter USB_ENABLE = 1'b1;               // Enable USB data transfer
parameter [15:0] CFAR_THRESHOLD_DEFAULT = 16'd10000;   // BETA: reset value of the register-map threshold (|I|+|Q|)
parameter ADC_CAPTURE_MODE = 1;            // BETA: 1 = ISERDES/polyphase DDC (default), 0 = legacy IDDR + 400 MHz fabric

// ============================================================================
// INTERNAL SIGNALS
// ============================================================================

// Clock and reset
wire clk_100m_buf;
wire clk_120m_dac_buf;
wire sys_reset_n;

// Transmitter internal signals
wire [7:0] tx_chirp_data;
wire tx_chirp_valid;
wire tx_chirp_done;
wire tx_new_chirp_frame;
wire [5:0] tx_current_elevation;
wire [5:0] tx_current_azimuth;
wire [5:0] tx_current_chirp;

// Receiver internal signals
wire [31:0] rx_doppler_output;
wire rx_doppler_valid;
wire [4:0] rx_doppler_bin;
wire [5:0] rx_range_bin;
wire [15:0] rx_doppler_real;
wire [15:0] rx_doppler_imag;
wire rx_doppler_data_valid;
reg  rx_cfar_detection;     // BETA: were wires assigned in an always block
reg  rx_cfar_valid;
wire [31:0] rx_range_profile_w;
wire        rx_range_profile_valid;
wire [5:0]  rx_range_profile_bin;
wire        rx_cdc_overflow;

// Host-link option B (BETA)
wire        bridge_active;
wire        bridge_miso;
wire        passthrough_miso_3v3;
wire [5:0]  rx_chirp_counter;

// Register map (BETA)
wire        ctl_use_long_chirp;
wire        ctl_adc_pwdn;
wire        ctl_usb_enable;
wire [15:0] ctl_cfar_threshold;
wire [1:0]  ctl_decimation_mode;
wire [9:0]  ctl_start_bin;
wire        cal_auto_start_t, cal_manual_load_t, cal_bitslip_load_t, cal_check_en;
wire [2:0]  cal_lane;
wire [4:0]  cal_tap;
wire [1:0]  cal_bitslip;
wire [7:0]  cal_pattern_a, cal_pattern_b, cal_undetermined;
wire [15:0] cal_status, cal_lane_info, cal_err_count;

// Data packing for USB
wire [31:0] usb_range_profile;
wire usb_range_valid;
wire [15:0] usb_doppler_real;
wire [15:0] usb_doppler_imag;
wire usb_doppler_valid;
wire usb_cfar_detection;
wire usb_cfar_valid;

// System status
reg [3:0] status_reg;

// ============================================================================
// CLOCK BUFFERING
// ============================================================================

BUFG bufg_100m (
    .I(clk_100m),
    .O(clk_100m_buf)
);

BUFG bufg_120m (
    .I(clk_120m_dac),
    .O(clk_120m_dac_buf)
);

// BETA: no BUFG on ft601_clk_in - the FT601 is not wired and the USB FSM runs on clk_100m.
/* verilator lint_off UNUSEDSIGNAL */
wire unused_sigs = (|rx_range_profile_bin) | ft601_clk_in | DOPPLER_ENABLE;
/* verilator lint_on UNUSEDSIGNAL */

// Reset synchronization (async assert / sync release; Verilator SYNCASYNCNET expected)
/* verilator lint_off SYNCASYNCNET */
reg [1:0] reset_sync;
/* verilator lint_on SYNCASYNCNET */
always @(posedge clk_100m_buf or negedge reset_n) begin
    if (!reset_n) begin
        reset_sync <= 2'b00;
    end else begin
        reset_sync <= {reset_sync[0], 1'b1};
    end
end
assign sys_reset_n = reset_sync[1];

// ============================================================================
// RADAR TRANSMITTER INSTANTIATION
// ============================================================================

radar_transmitter tx_inst (
    // System Clocks
    .clk_100m(clk_100m_buf),
    .clk_120m_dac(clk_120m_dac_buf),
    .reset_n(sys_reset_n),
    
    // DAC Interface
    .dac_data(dac_data),
    .dac_clk(dac_clk),
    .dac_sleep(dac_sleep),
    
    // Mixer Enables
    .rx_mixer_en(rx_mixer_en),
    .tx_mixer_en(tx_mixer_en),
    
    // STM32 Control Interface
    .stm32_new_chirp(stm32_new_chirp),
    .stm32_new_elevation(stm32_new_elevation),
    .stm32_new_azimuth(stm32_new_azimuth),
    .stm32_mixers_enable(stm32_mixers_enable),
    
    // RF Switch Control
    .fpga_rf_switch(fpga_rf_switch),
    
    // ADAR1000 Control Interface
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
    
    // Level Shifter SPI Interface
    .spi_passthrough_gate(bridge_active),
    .stm32_sclk_3v3(stm32_sclk_3v3),
    .stm32_mosi_3v3(stm32_mosi_3v3),
    .stm32_miso_3v3(passthrough_miso_3v3),
    .stm32_cs_adar1_3v3(stm32_cs_adar1_3v3),
    .stm32_cs_adar2_3v3(stm32_cs_adar2_3v3),
    .stm32_cs_adar3_3v3(stm32_cs_adar3_3v3),
    .stm32_cs_adar4_3v3(stm32_cs_adar4_3v3),
    
    .stm32_sclk_1v8(stm32_sclk_1v8),
    .stm32_mosi_1v8(stm32_mosi_1v8),
    .stm32_miso_1v8(stm32_miso_1v8),
    .stm32_cs_adar1_1v8(stm32_cs_adar1_1v8),
    .stm32_cs_adar2_1v8(stm32_cs_adar2_1v8),
    .stm32_cs_adar3_1v8(stm32_cs_adar3_1v8),
    .stm32_cs_adar4_1v8(stm32_cs_adar4_1v8),
    
    // Beam Position Tracking
    .current_elevation(tx_current_elevation),
    .current_azimuth(tx_current_azimuth),
    .current_chirp(tx_current_chirp),
    .new_chirp_frame(tx_new_chirp_frame)
);

// ============================================================================
// RADAR RECEIVER INSTANTIATION
// ============================================================================

radar_control_regs #(
    .DEF_USE_LONG_CHIRP (USE_LONG_CHIRP),
    .DEF_USB_ENABLE     (USB_ENABLE),
    .DEF_CFAR_THRESHOLD (CFAR_THRESHOLD_DEFAULT)
) ctl_regs (
    .clk             (clk_100m_buf),
    .reset_n         (sys_reset_n),
    .reg_we          (1'b0),            // no host write path on the board (README "Host path")
    .reg_addr        (4'h0),
    .reg_wdata       (16'h0000),
    .reg_rdata       (),
    .use_long_chirp  (ctl_use_long_chirp),
    .adc_pwdn        (ctl_adc_pwdn),
    .usb_enable      (ctl_usb_enable),
    .cfar_threshold  (ctl_cfar_threshold),
    .decimation_mode (ctl_decimation_mode),
    .start_bin       (ctl_start_bin),
    .cal_auto_start_t(cal_auto_start_t), .cal_manual_load_t(cal_manual_load_t),
    .cal_bitslip_load_t(cal_bitslip_load_t), .cal_check_en(cal_check_en),
    .cal_lane(cal_lane), .cal_tap(cal_tap), .cal_bitslip(cal_bitslip),
    .cal_pattern_a(cal_pattern_a), .cal_pattern_b(cal_pattern_b),
    .cal_status(cal_status), .cal_lane_info(cal_lane_info),
    .cal_err_count(cal_err_count), .cal_undetermined(cal_undetermined)
);

radar_receiver_final #(
    .CHIRPS_PER_FRAME(32),
    .ADC_CAPTURE_MODE(ADC_CAPTURE_MODE)
) rx_inst (
    .clk(clk_100m_buf),
    .reset_n(sys_reset_n),

    // ADC Physical Interface
    .adc_d_p(adc_d_p),
    .adc_d_n(adc_d_n),
    .adc_dco_p(adc_dco_p),
    .adc_dco_n(adc_dco_n),
    .adc_pwdn(adc_pwdn),

    // Control
    .stm32_new_chirp(stm32_new_chirp),
    .stm32_new_elevation(stm32_new_elevation),
    .stm32_new_azimuth(stm32_new_azimuth),
    .use_long_chirp(ctl_use_long_chirp),
    .adc_pwdn_req(ctl_adc_pwdn),
    .ddc_bypass(1'b0),
    .decimation_mode(ctl_decimation_mode),
    .start_bin(ctl_start_bin),

    // Range profile
    .range_profile_out(rx_range_profile_w),
    .range_profile_valid(rx_range_profile_valid),
    .range_profile_bin(rx_range_profile_bin),

    // Doppler Outputs
    .doppler_output(rx_doppler_output),
    .doppler_valid(rx_doppler_valid),
    .doppler_bin(rx_doppler_bin),
    .range_bin(rx_range_bin),

    // ADC capture calibration (register map)
    .cal_auto_start_t(cal_auto_start_t), .cal_manual_load_t(cal_manual_load_t),
    .cal_bitslip_load_t(cal_bitslip_load_t), .cal_check_en(cal_check_en),
    .cal_lane(cal_lane), .cal_tap(cal_tap), .cal_bitslip(cal_bitslip),
    .cal_pattern_a(cal_pattern_a), .cal_pattern_b(cal_pattern_b),
    .cal_status(cal_status), .cal_lane_info(cal_lane_info),
    .cal_err_count(cal_err_count), .cal_undetermined(cal_undetermined),

    // Status
    .rx_chirp_counter(rx_chirp_counter),
    .new_chirp_frame(),
    .cdc_overflow(rx_cdc_overflow)
);

// ============================================================================
// DOPPLER DATA DECODING
// ============================================================================

// Decode 32-bit doppler output into real and imaginary parts
// Format: {doppler_q[15:0], doppler_i[15:0]}
assign rx_doppler_real = rx_doppler_output[15:0];
assign rx_doppler_imag = rx_doppler_output[31:16];
assign rx_doppler_data_valid = rx_doppler_valid;

// Simple threshold detector on the Doppler magnitude (|I| + |Q| > threshold). This is a
// PLACEHOLDER for a CFAR detector (original comment :298-299); the threshold now comes from
// the register map instead of a literal. BETA: `mag` is a module-level wire (the original
// declared it inside the always block, :312, which is a syntax error).
reg [7:0] cfar_counter;
wire [16:0] mag = {1'b0, (rx_doppler_real[15] ? -rx_doppler_real : rx_doppler_real)} +
                  {1'b0, (rx_doppler_imag[15] ? -rx_doppler_imag : rx_doppler_imag)};
always @(posedge clk_100m_buf or negedge sys_reset_n) begin
    if (!sys_reset_n) begin
        cfar_counter <= 8'd0;
        rx_cfar_detection <= 1'b0;
        rx_cfar_valid <= 1'b0;
    end else begin
        rx_cfar_valid <= 1'b0;
        if (rx_doppler_valid) begin
            rx_cfar_valid <= 1'b1;
            rx_cfar_detection <= (mag > {1'b0, ctl_cfar_threshold});
            if (mag > {1'b0, ctl_cfar_threshold})
                cfar_counter <= cfar_counter + 8'd1;
        end
    end
end
/* verilator lint_off UNUSEDSIGNAL */
wire unused_cfar_counter = |cfar_counter;   // detection counter kept for debug visibility
/* verilator lint_on UNUSEDSIGNAL */

// ============================================================================
// DATA PACKING FOR USB
// ============================================================================

// BETA: the real decimated range profile ({Q,I} of one of 64 range bins) is sent; the
// original used the Doppler data as a placeholder (:329-332). All valids are gated by the
// register-map usb_enable bit.
assign usb_range_profile = rx_range_profile_w;
assign usb_range_valid = rx_range_profile_valid & ctl_usb_enable;

assign usb_doppler_real = rx_doppler_real;
assign usb_doppler_imag = rx_doppler_imag;
assign usb_doppler_valid = rx_doppler_valid & ctl_usb_enable;

assign usb_cfar_detection = rx_cfar_detection;
assign usb_cfar_valid = rx_cfar_valid & ctl_usb_enable;

// ============================================================================
// HOST-LINK OPTION B: range-Doppler frame packer + SPI bridge (BETA)
// Source: engineering/DESIGN/HOST_LINK (HOST_LINK_DESIGN.md section 5, option_b_signal_map.csv)
// ============================================================================
// Cell stream: the Doppler processor emits, for each range bin 0..63, the 32 Doppler bins in
// order (range-major, 2048 cells per frame). The detector output rx_cfar_valid/detection is one
// clock behind rx_doppler_valid, so the Doppler data are delayed by one register to line up with
// the detection flag; frame_start is derived from the undelayed first cell (range_bin == 0 and
// doppler_bin == 0) and therefore precedes the delayed first cell by one clock, as the packer
// requires.
// Beam indices: az/el come from the transmitter's STM32-toggle counters (the only source of the
// beam position in the design; the register map has no such field). They live in the clk_120m
// domain and change only on STM32 toggles (milliseconds apart), so they are taken through a
// 2-stage synchroniser and accepted only when two consecutive samples agree. chirp_count is a
// free-running 16-bit count of receiver chirp pulses (clk_100m). long_chirp = register map.
reg  [15:0] cell_i_d, cell_q_d;
reg  [4:0]  dop_bin_d;
reg  [5:0]  rng_bin_d;
reg         frame_first_d;
always @(posedge clk_100m_buf or negedge sys_reset_n) begin
    if (!sys_reset_n) begin
        cell_i_d <= 16'd0; cell_q_d <= 16'd0; dop_bin_d <= 5'd0; rng_bin_d <= 6'd0; frame_first_d <= 1'b0;
    end else begin
        cell_i_d <= rx_doppler_real;
        cell_q_d <= rx_doppler_imag;
        dop_bin_d <= rx_doppler_bin;
        rng_bin_d <= rx_range_bin;
        frame_first_d <= rx_doppler_valid && (rx_doppler_bin == 5'd0) && (rx_range_bin == 6'd0);
    end
end
wire packer_frame_start = rx_doppler_valid && (rx_doppler_bin == 5'd0) && (rx_range_bin == 6'd0);

(* ASYNC_REG = "TRUE" *) reg [5:0] az_s1, az_s2, el_s1, el_s2;
reg [5:0] az_stable, el_stable;
reg [15:0] chirp_count;
reg [5:0]  rx_chirp_counter_d;
always @(posedge clk_100m_buf or negedge sys_reset_n) begin
    if (!sys_reset_n) begin
        az_s1 <= 6'd0; az_s2 <= 6'd0; el_s1 <= 6'd0; el_s2 <= 6'd0;
        az_stable <= 6'd0; el_stable <= 6'd0; chirp_count <= 16'd0; rx_chirp_counter_d <= 6'd0;
    end else begin
        az_s1 <= tx_current_azimuth;   az_s2 <= az_s1;
        el_s1 <= tx_current_elevation; el_s2 <= el_s1;
        if (az_s1 == az_s2) az_stable <= az_s2;
        if (el_s1 == el_s2) el_stable <= el_s2;
        rx_chirp_counter_d <= rx_chirp_counter;
        if (rx_chirp_counter != rx_chirp_counter_d) chirp_count <= chirp_count + 16'd1;
    end
end

wire        pk_wr_en, pk_bank, pk_frame_done, pk_frame_bank, pk_overflow, pk_consumed;
wire [11:0] pk_wr_addr, pk_frame_len;
wire [7:0]  pk_wr_data;

rd_map_packer #(.N_RANGE(64), .N_DOPPLER(32), .MAX_DET(32)) rd_packer (
    .clk(clk_100m_buf), .rst_n(sys_reset_n),
    .frame_start(packer_frame_start),
    .cell_valid(rx_cfar_valid),
    .cell_i(cell_i_d), .cell_q(cell_q_d),
    .cell_det(rx_cfar_detection),
    .az_idx({2'b00, az_stable}), .el_idx({2'b00, el_stable}),
    .chirp_count(chirp_count), .long_chirp(ctl_use_long_chirp),
    .wr_en(pk_wr_en), .wr_addr(pk_wr_addr), .wr_data(pk_wr_data), .bank(pk_bank),
    .frame_done(pk_frame_done), .frame_bank(pk_frame_bank), .frame_len(pk_frame_len),
    .overflow(pk_overflow), .consumed(pk_consumed)
);

host_bridge_spi host_bridge (
    .clk(clk_100m_buf), .rst_n(sys_reset_n),
    .wr_en(pk_wr_en), .wr_addr(pk_wr_addr), .wr_data(pk_wr_data), .wr_bank(pk_bank),
    .frame_bank(pk_frame_bank), .frame_done(pk_frame_done), .frame_len(pk_frame_len),
    .consumed(pk_consumed),
    .sclk(stm32_sclk_3v3), .mosi(stm32_mosi_3v3), .miso(bridge_miso), .cs_n(spi_bridge_cs_n),
    .drdy(spi_bridge_drdy), .bridge_active(bridge_active)
);

// Shared SPI1 MISO: bridge while its chip select is low, ADAR1000 pass-through otherwise.
assign stm32_miso_3v3  = bridge_active ? bridge_miso : passthrough_miso_3v3;
assign spi_bridge_spare = pk_overflow;

// RTL check required by option_b_signal_map.csv: all ADAR1000 chip selects must be high
// during a bridge transfer (sticky flag, exported in system_status[1]).
reg bridge_cs_conflict;
always @(posedge clk_100m_buf or negedge sys_reset_n) begin
    if (!sys_reset_n) bridge_cs_conflict <= 1'b0;
    else if (bridge_active && !(stm32_cs_adar1_3v3 & stm32_cs_adar2_3v3 & stm32_cs_adar3_3v3 & stm32_cs_adar4_3v3))
        bridge_cs_conflict <= 1'b1;
end

/* verilator lint_off UNUSEDSIGNAL */
wire unused_packer = (|dop_bin_d) | (|rng_bin_d) | frame_first_d;   // kept for waveform debugging
/* verilator lint_on UNUSEDSIGNAL */

// ============================================================================
// USB DATA INTERFACE INSTANTIATION (host-link option A, unchanged)
// ============================================================================

usb_data_interface usb_inst (
    .clk(clk_100m_buf),
    .reset_n(sys_reset_n),
    
    // Radar data inputs
    .range_profile(usb_range_profile),
    .range_valid(usb_range_valid),
    .doppler_real(usb_doppler_real),
    .doppler_imag(usb_doppler_imag),
    .doppler_valid(usb_doppler_valid),
    .cfar_detection(usb_cfar_detection),
    .cfar_valid(usb_cfar_valid),
    
    // FT601 Interface
    .ft601_data(ft601_data),
    .ft601_be(ft601_be),
    .ft601_txe_n(ft601_txe_n),
    .ft601_rxf_n(ft601_rxf_n),
    .ft601_txe(ft601_txe),
    .ft601_rxf(ft601_rxf),
    .ft601_wr_n(ft601_wr_n),
    .ft601_rd_n(ft601_rd_n),
    .ft601_oe_n(ft601_oe_n),
    .ft601_siwu_n(ft601_siwu_n),
    .ft601_srb(ft601_srb),
    .ft601_swb(ft601_swb),
    .ft601_clk_out(ft601_clk_out),
    .ft601_clk_in(ft601_clk_in)
);

// ============================================================================
// OUTPUT ASSIGNMENTS
// ============================================================================

assign current_elevation = tx_current_elevation;
assign current_azimuth = tx_current_azimuth;
assign current_chirp = tx_current_chirp;
assign new_chirp_frame = tx_new_chirp_frame;

assign dbg_doppler_data = rx_doppler_output;
assign dbg_doppler_valid = rx_doppler_valid;
assign dbg_doppler_bin = rx_doppler_bin;
assign dbg_range_bin = rx_range_bin;

// ============================================================================
// SYSTEM STATUS MONITORING
// ============================================================================

always @(posedge clk_100m_buf or negedge sys_reset_n) begin
    if (!sys_reset_n) begin
        status_reg <= 4'b0000;
    end else begin
        status_reg[0] <= stm32_mixers_enable;      // Mixers enabled
        status_reg[1] <= ft601_txe | rx_cdc_overflow | bridge_cs_conflict; // USB TX ready / BETA: or CDC FIFO overflow / ADAR CS low during a bridge transfer
        status_reg[2] <= rx_doppler_valid;          // Data valid
        status_reg[3] <= tx_new_chirp_frame;        // New chirp frame
    end
end

assign system_status = status_reg;

// ============================================================================
// DEBUG AND VERIFICATION
// ============================================================================

`ifdef SIMULATION
// Simulation-only debug monitoring
reg [31:0] debug_cycle_counter;
reg [31:0] data_packet_counter;

always @(posedge clk_100m_buf) begin
    debug_cycle_counter <= debug_cycle_counter + 1;
    
    if (tx_new_chirp_frame) begin
        $display("[TOP] New chirp frame started at cycle %0d", debug_cycle_counter);
    end
    
    if (rx_doppler_valid) begin
        data_packet_counter <= data_packet_counter + 1;
        if (data_packet_counter < 10) begin
            $display("[TOP] Doppler data[%0d]: bin=%0d, range=%0d, I=%0d, Q=%0d",
                     data_packet_counter, rx_doppler_bin, rx_range_bin,
                     rx_doppler_real, rx_doppler_imag);
        end
    end
    
    if (data_packet_counter == 100) begin
        $display("[TOP] First 100 doppler packets processed");
    end
end
`endif

endmodule
