`timescale 1ns / 1ps
// ============================================================================
// radar_control_regs.v  -  control / status register map.  BETA.
//
// Purpose: give every receiver control input that was left undriven in the
// original RTL (radar_receiver_final.v:21-22, :204-208; adc_pwdn; CFAR
// threshold) a single, documented driver with a reset default, instead of a
// floating wire. The write/read port is driven by the host-link option B SPI
// bridge (host_bridge_spi.v, command set v2: 0x02 write / 0x03 read, see
// engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md §7). The bridge carries
// 16-bit word addresses and 32-bit data; this map decodes addr[4:0] and
// data[15:0], reads return {16'h0000, value}.
//
// Address map (16-bit registers, word addresses; §7 of HOST_LINK_DESIGN.md mirrors this list):
//   0x00 CONTROL   bit0 use_long_chirp (1)  bit1 adc_pwdn (0)  bit2 usb_enable (1)
//   0x01 CFAR_THR  |I|+|Q| threshold, 16 bits (10000 = original placeholder)
//   0x02 DECIM     bits[1:0] range decimation mode (01 = peak)
//   0x03 START_BIN bits[9:0] first range bin passed to the decimator (0)
//   0x04 CAL_CTRL  write 1 to bit0: start auto calibration (toggle), bit1: manual tap load (toggle),
//                  bit2: bitslip load (toggle); bit3 (level) pattern-check enable;
//                  bit4 (level) blind calibration method (0 = ADC test pattern, 1 = CW tone at the IF)
//   0x05 CAL_LANE  bits[2:0] lane for CAL_TAP / CAL_BITSLIP writes and for the CAL_LANE_INFO /
//                  CAL_BLIND_MIN reads
//   0x06 CAL_TAP   bits[4:0] manual IDELAY tap (default 16)
//   0x07 CAL_SLIP  bits[1:0] number of BITSLIP pulses for a manual bitslip load
//   0x08 CAL_PATT  {pattern_b[7:0], pattern_a[7:0]} expected alternating ADC test codes (0x55AA)
//   0x09 CAL_STAT  read-only {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}
//   0x0A CAL_LANE_INFO read-only {1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]} of CAL_LANE
//   0x0B CAL_ERR   read-only pattern-check error counter
//   0x0C CAL_UNDET read-only {8'b0, undetermined[7:0]}
//   0x0D CAL_BLIND_COEF   signed Q1.14 cos(2*pi*f_IF/f_S) for the blind notch; default 0xEC39 =
//                         -5063 = round(16384*cos(2*pi*120/400))
//   0x0E CAL_BLIND_MARGIN absolute part of the pass margin: a tap passes when metric <= min +
//                         CAL_BLIND_MARGIN + min/16 (default 0x0040)
//   0x0F ID        read-only 0xBE7A (beta build identifier)
//   0x10 CAL_BLIND_MIN    read-only minimum blind metric of CAL_LANE (sum |r| over the window, >>4,
//                         saturated to 16 bits)
// (0x4..0xC added for the ISERDES capture path, ADC_CAPTURE_MODE = 1; 0xD/0xE/0x10 for the blind method)
// ============================================================================
module radar_control_regs #(
    parameter DEF_USE_LONG_CHIRP = 1'b1,
    parameter DEF_ADC_PWDN       = 1'b0,
    parameter DEF_USB_ENABLE     = 1'b1,
    parameter [15:0] DEF_CFAR_THRESHOLD = 16'd10000,
    parameter [1:0]  DEF_DECIM_MODE     = 2'b01,
    parameter [9:0]  DEF_START_BIN      = 10'd0,
    parameter [15:0] DEF_BLIND_COEF     = 16'hEC39,
    parameter [15:0] DEF_BLIND_MARGIN   = 16'h0040
) (
    input  wire        clk,
    input  wire        reset_n,
    // generic write/read port (host_bridge_spi, clk domain)
    input  wire        reg_we,
    input  wire [4:0]  reg_addr,
    input  wire [15:0] reg_wdata,
    output reg  [15:0] reg_rdata,
    // control outputs
    output wire        use_long_chirp,
    output wire        adc_pwdn,
    output wire        usb_enable,
    output wire [15:0] cfar_threshold,
    output wire [1:0]  decimation_mode,
    output wire [9:0]  start_bin,
    // ADC capture calibration (quasi-static toggles/levels to adc_capture_calib)
    output reg         cal_auto_start_t,
    output reg         cal_manual_load_t,
    output reg         cal_bitslip_load_t,
    output wire        cal_check_en,
    output wire        cal_blind,
    output wire [2:0]  cal_lane,
    output wire [4:0]  cal_tap,
    output wire [1:0]  cal_bitslip,
    output wire [7:0]  cal_pattern_a,
    output wire [7:0]  cal_pattern_b,
    output wire [15:0] cal_blind_coef,
    output wire [15:0] cal_blind_margin,
    input  wire [15:0] cal_status,        // {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}
    input  wire [15:0] cal_lane_info,     // {1'b0, win_hi, win_lo, tap}
    input  wire [15:0] cal_err_count,
    input  wire [7:0]  cal_undetermined,
    input  wire [15:0] cal_blind_min
);
    reg        r_check_en;
    reg        r_blind;
    reg [2:0]  r_lane;
    reg [4:0]  r_tap;
    reg [1:0]  r_slip;
    reg [15:0] r_patt;
    reg [15:0] r_coef;
    reg [15:0] r_margin;
    reg [2:0]  r_control;
    reg [15:0] r_cfar;
    reg [1:0]  r_decim;
    reg [9:0]  r_start;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            r_control <= {DEF_USB_ENABLE, DEF_ADC_PWDN, DEF_USE_LONG_CHIRP};
            r_cfar    <= DEF_CFAR_THRESHOLD;
            r_decim   <= DEF_DECIM_MODE;
            r_start   <= DEF_START_BIN;
            cal_auto_start_t <= 1'b0; cal_manual_load_t <= 1'b0; cal_bitslip_load_t <= 1'b0;
            r_check_en <= 1'b0; r_blind <= 1'b0; r_lane <= 3'd0; r_tap <= 5'd16; r_slip <= 2'd0; r_patt <= 16'h55AA;
            r_coef <= DEF_BLIND_COEF; r_margin <= DEF_BLIND_MARGIN;
        end else if (reg_we) begin
            case (reg_addr)
                5'h00: r_control <= reg_wdata[2:0];
                5'h01: r_cfar    <= reg_wdata;
                5'h02: r_decim   <= reg_wdata[1:0];
                5'h03: r_start   <= reg_wdata[9:0];
                5'h04: begin
                    if (reg_wdata[0]) cal_auto_start_t  <= ~cal_auto_start_t;
                    if (reg_wdata[1]) cal_manual_load_t <= ~cal_manual_load_t;
                    if (reg_wdata[2]) cal_bitslip_load_t <= ~cal_bitslip_load_t;
                    r_check_en <= reg_wdata[3];
                    r_blind    <= reg_wdata[4];
                end
                5'h05: r_lane   <= reg_wdata[2:0];
                5'h06: r_tap    <= reg_wdata[4:0];
                5'h07: r_slip   <= reg_wdata[1:0];
                5'h08: r_patt   <= reg_wdata;
                5'h0D: r_coef   <= reg_wdata;
                5'h0E: r_margin <= reg_wdata;
                default: ;
            endcase
        end
    end

    always @(*) begin
        case (reg_addr)
            5'h00:   reg_rdata = {13'd0, r_control};
            5'h01:   reg_rdata = r_cfar;
            5'h02:   reg_rdata = {14'd0, r_decim};
            5'h03:   reg_rdata = {6'd0, r_start};
            5'h04:   reg_rdata = {11'd0, r_blind, r_check_en, 3'b000};
            5'h05:   reg_rdata = {13'd0, r_lane};
            5'h06:   reg_rdata = {11'd0, r_tap};
            5'h07:   reg_rdata = {14'd0, r_slip};
            5'h08:   reg_rdata = r_patt;
            5'h09:   reg_rdata = cal_status;
            5'h0A:   reg_rdata = cal_lane_info;
            5'h0B:   reg_rdata = cal_err_count;
            5'h0C:   reg_rdata = {8'd0, cal_undetermined};
            5'h0D:   reg_rdata = r_coef;
            5'h0E:   reg_rdata = r_margin;
            5'h0F:   reg_rdata = 16'hBE7A;
            5'h10:   reg_rdata = cal_blind_min;
            default: reg_rdata = 16'h0000;
        endcase
    end

    assign use_long_chirp   = r_control[0];
    assign adc_pwdn         = r_control[1];
    assign usb_enable       = r_control[2];
    assign cfar_threshold   = r_cfar;
    assign decimation_mode  = r_decim;
    assign start_bin        = r_start;
    assign cal_check_en     = r_check_en;
    assign cal_blind        = r_blind;
    assign cal_lane         = r_lane;
    assign cal_tap          = r_tap;
    assign cal_bitslip      = r_slip;
    assign cal_pattern_a    = r_patt[7:0];
    assign cal_pattern_b    = r_patt[15:8];
    assign cal_blind_coef   = r_coef;
    assign cal_blind_margin = r_margin;
endmodule
