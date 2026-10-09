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
//   0xF  ID        read-only 0xBE7A (beta build identifier)
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
    output wire [9:0]  start_bin
);
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
        end else if (reg_we) begin
            case (reg_addr)
                4'h0: r_control <= reg_wdata[2:0];
                4'h1: r_cfar    <= reg_wdata;
                4'h2: r_decim   <= reg_wdata[1:0];
                4'h3: r_start   <= reg_wdata[9:0];
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
endmodule
