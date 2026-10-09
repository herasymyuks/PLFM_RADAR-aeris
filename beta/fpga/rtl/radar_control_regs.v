`timescale 1ns / 1ps
// ============================================================================
// radar_control_regs.v  -  control / status register map.  BETA.
//
// Purpose: give every receiver control input that was left undriven in the
// original RTL (radar_receiver_final.v:21-22, :204-208; adc_pwdn; CFAR
// threshold) a single, documented driver with a reset default, instead of a
// floating wire. The write port is generic (we/addr/data) and is TIED OFF at
// the top level in this beta because no host write path exists on the board:
// the STM32 SPI1 passes through the FPGA to the ADAR1000s with no chip select
// for the FPGA, and the FT601 is not wired. Connecting a host interface (e.g.
// an SPI slave on DIG_5..DIG_7, or an FT601 register channel) is listed in
// README "Remaining work".
//
// Address map (16-bit registers):
//   0x0  CONTROL   bit0 use_long_chirp (1)  bit1 adc_pwdn (0)  bit2 usb_enable (1)
//   0x1  CFAR_THR  |I|+|Q| threshold, 16 bits (10000 = original placeholder)
//   0x2  DECIM     bits[1:0] range decimation mode (01 = peak)
//   0x3  START_BIN bits[9:0] first range bin passed to the decimator (0)
//   0x4  CAL_CTRL  write 1 to bit0: start auto calibration (toggle), bit1: manual tap load (toggle),
//                  bit2: bitslip load (toggle); bit3 (level) pattern-check enable
//   0x5  CAL_LANE  bits[2:0] lane for CAL_TAP / CAL_BITSLIP writes and for the CAL_LANE_INFO read
//   0x6  CAL_TAP   bits[4:0] manual IDELAY tap (default 16)
//   0x7  CAL_SLIP  bits[1:0] number of BITSLIP pulses for a manual bitslip load
//   0x8  CAL_PATT  {pattern_b[7:0], pattern_a[7:0]} expected alternating ADC test codes (0x55AA)
//   0x9  CAL_STAT  read-only {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}
//   0xA  CAL_LANE_INFO read-only {1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]} of CAL_LANE
//   0xB  CAL_ERR   read-only pattern-check error counter
//   0xC  CAL_UNDET read-only {8'b0, undetermined[7:0]}
//   0xF  ID        read-only 0xBE7A (beta build identifier)
// (0x4..0xC added for the ISERDES capture path, ADC_CAPTURE_MODE = 1)
// ============================================================================
module radar_control_regs #(
    parameter DEF_USE_LONG_CHIRP = 1'b1,
    parameter DEF_ADC_PWDN       = 1'b0,
    parameter DEF_USB_ENABLE     = 1'b1,
    parameter [15:0] DEF_CFAR_THRESHOLD = 16'd10000,
    parameter [1:0]  DEF_DECIM_MODE     = 2'b01,
    parameter [9:0]  DEF_START_BIN      = 10'd0
) (
    input  wire        clk,
    input  wire        reset_n,
    // generic write/read port (tied off at the top level in the beta build)
    input  wire        reg_we,
    input  wire [3:0]  reg_addr,
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
    output wire [2:0]  cal_lane,
    output wire [4:0]  cal_tap,
    output wire [1:0]  cal_bitslip,
    output wire [7:0]  cal_pattern_a,
    output wire [7:0]  cal_pattern_b,
    input  wire [15:0] cal_status,        // {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}
    input  wire [15:0] cal_lane_info,     // {1'b0, win_hi, win_lo, tap}
    input  wire [15:0] cal_err_count,
    input  wire [7:0]  cal_undetermined
);
    reg        r_check_en;
    reg [2:0]  r_lane;
    reg [4:0]  r_tap;
    reg [1:0]  r_slip;
    reg [15:0] r_patt;
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
            r_check_en <= 1'b0; r_lane <= 3'd0; r_tap <= 5'd16; r_slip <= 2'd0; r_patt <= 16'h55AA;
        end else if (reg_we) begin
            case (reg_addr)
                4'h0: r_control <= reg_wdata[2:0];
                4'h1: r_cfar    <= reg_wdata;
                4'h2: r_decim   <= reg_wdata[1:0];
                4'h3: r_start   <= reg_wdata[9:0];
                4'h4: begin
                    if (reg_wdata[0]) cal_auto_start_t  <= ~cal_auto_start_t;
                    if (reg_wdata[1]) cal_manual_load_t <= ~cal_manual_load_t;
                    if (reg_wdata[2]) cal_bitslip_load_t <= ~cal_bitslip_load_t;
                    r_check_en <= reg_wdata[3];
                end
                4'h5: r_lane <= reg_wdata[2:0];
                4'h6: r_tap  <= reg_wdata[4:0];
                4'h7: r_slip <= reg_wdata[1:0];
                4'h8: r_patt <= reg_wdata;
                default: ;
            endcase
        end
    end

    always @(*) begin
        case (reg_addr)
            4'h0:    reg_rdata = {13'd0, r_control};
            4'h1:    reg_rdata = r_cfar;
            4'h2:    reg_rdata = {14'd0, r_decim};
            4'h3:    reg_rdata = {6'd0, r_start};
            4'h4:    reg_rdata = {12'd0, r_check_en, 3'b000};
            4'h5:    reg_rdata = {13'd0, r_lane};
            4'h6:    reg_rdata = {11'd0, r_tap};
            4'h7:    reg_rdata = {14'd0, r_slip};
            4'h8:    reg_rdata = r_patt;
            4'h9:    reg_rdata = cal_status;
            4'hA:    reg_rdata = cal_lane_info;
            4'hB:    reg_rdata = cal_err_count;
            4'hC:    reg_rdata = {8'd0, cal_undetermined};
            4'hF:    reg_rdata = 16'hBE7A;
            default: reg_rdata = 16'h0000;
        endcase
    end

    assign use_long_chirp  = r_control[0];
    assign adc_pwdn        = r_control[1];
    assign usb_enable      = r_control[2];
    assign cfar_threshold  = r_cfar;
    assign decimation_mode = r_decim;
    assign start_bin       = r_start;
    assign cal_check_en    = r_check_en;
    assign cal_lane        = r_lane;
    assign cal_tap         = r_tap;
    assign cal_bitslip     = r_slip;
    assign cal_pattern_a   = r_patt[7:0];
    assign cal_pattern_b   = r_patt[15:8];
endmodule
