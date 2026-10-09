`timescale 1ns / 1ps
// ============================================================================
// usb_data_interface.v  -  radar data packetiser for an FT601 slave-FIFO bus.
// BETA rewrite of 9_Firmware/9_2_FPGA/usb_data_interface.v (ports unchanged).
//
// HARDWARE STATUS: the FT601 (U6) has 0 of 77 pins connected on the Main Board
// schematic (reconstructed/PIN_MAP_FROM_SCHEMATIC.md). This module therefore
// has no physical counterpart; it is kept so that the host data path can be
// simulated and so that the packet format is defined. See README "Host path".
//
// Changes vs the original (CHANGELOG.md):
//   * the FSM runs on `clk` (100 MHz system clock) instead of ft601_clk_in: the
//     data inputs come from the clk domain and the original sampled them
//     without synchronisation (:84-150). A real FT601 synchronous FIFO bus
//     must be driven from ft601_clk; when the hardware exists, an asynchronous
//     FIFO (rtl/async_fifo.v) has to be inserted between this FSM and the bus.
//     ft601_clk_in is unused here (ft601_clk_out = clk/2 keeps its single driver).
//   * SystemVerilog `typedef enum` (:46-56) replaced by localparams (Verilog-2001).
//   * ft601_clk_out had two drivers (:78 and :176-182); now one.
//   * the payload is latched in a snapshot when a packet starts; the original
//     waited for doppler_valid / cfar_valid again on every word (:124, :147),
//     which can never happen with single-cycle valid pulses.
//   * ft601_txe_n / ft601_rxf_n (which are FT601 OUTPUTS in the datasheet, i.e.
//     wrongly declared as FPGA outputs) are driven inactive high.
//
// Packet (11 x 32-bit words, ft601_be = 2'b11, one word per clk while
// ft601_txe == 0 = "FT601 can accept data"):
//   W0  {8'hAA, 8'h01, 5'b0, cfar_valid, doppler_valid, range_valid, seq[7:0]}
//   W1  range_profile[31:0]           W2..W4  32'h0 (reserved)
//   W5  {doppler_imag, doppler_real}  W6..W8  32'h0 (reserved)
//   W9  {31'b0, cfar_detection}
//   W10 {24'h0, 8'h55}
// Records arriving while a packet is in flight are dropped and counted
// (dropped_count, internal, visible in simulation).
// ============================================================================
module usb_data_interface (
    input wire clk,              // Main clock (100MHz)
    input wire reset_n,

    // Radar data inputs
    input wire [31:0] range_profile,
    input wire range_valid,
    input wire [15:0] doppler_real,
    input wire [15:0] doppler_imag,
    input wire doppler_valid,
    input wire cfar_detection,
    input wire cfar_valid,

    // FT601 Interface (Slave FIFO mode)
    inout wire [31:0] ft601_data,    // 32-bit bidirectional data bus
    output reg [1:0] ft601_be,       // Byte enable
    output wire ft601_txe_n,         // (FT601 output in reality) driven inactive
    output wire ft601_rxf_n,         // (FT601 output in reality) driven inactive
    input wire ft601_txe,            // 0 = FT601 can accept data (original polarity kept)
    input wire ft601_rxf,            // unused (no read path)
    output reg ft601_wr_n,           // Write strobe (active low)
    output wire ft601_rd_n,          // Read strobe (active low) - never asserted
    output wire ft601_oe_n,          // Output enable (active low) - never asserted
    output wire ft601_siwu_n,        // Send immediate / Wakeup - inactive
    input wire [1:0] ft601_srb,      // unused
    input wire [1:0] ft601_swb,      // unused
    output reg ft601_clk_out,        // clk / 2 (optional)
    input wire ft601_clk_in          // NOT USED in the beta (see header)
);

localparam HEADER = 8'hAA;
localparam FOOTER = 8'h55;
localparam VERSION = 8'h01;
localparam PACKET_WORDS = 11;

localparam [1:0] S_IDLE = 2'd0, S_SEND = 2'd1, S_GAP = 2'd2;

reg [1:0]  state;
reg [3:0]  word_idx;
reg [31:0] snap_range;
reg [15:0] snap_dre, snap_dim;
reg        snap_det;
reg [2:0]  snap_flags;
reg [7:0]  seq;
reg [15:0] dropped_count;
reg [31:0] ft601_data_out;
reg        ft601_data_oe;

assign ft601_data   = ft601_data_oe ? ft601_data_out : 32'hzzzz_zzzz;
assign ft601_txe_n  = 1'b1;
assign ft601_rxf_n  = 1'b1;
assign ft601_rd_n   = 1'b1;
assign ft601_oe_n   = 1'b1;
assign ft601_siwu_n = 1'b1;

/* verilator lint_off UNUSEDSIGNAL */
wire unused_inputs = ft601_rxf | ft601_clk_in | (|ft601_srb) | (|ft601_swb);
/* verilator lint_on UNUSEDSIGNAL */

wire trigger = range_valid | doppler_valid | cfar_valid;

function [31:0] packet_word;
    input [3:0] idx;
    begin
        case (idx)
            4'd0:    packet_word = {HEADER, VERSION, 5'b0, snap_flags, seq};
            4'd1:    packet_word = snap_range;
            4'd5:    packet_word = {snap_dim, snap_dre};
            4'd9:    packet_word = {31'b0, snap_det};
            4'd10:   packet_word = {24'h0, FOOTER};
            default: packet_word = 32'h0000_0000;
        endcase
    end
endfunction

always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        state <= S_IDLE;
        word_idx <= 4'd0;
        snap_range <= 32'd0;
        snap_dre <= 16'd0;
        snap_dim <= 16'd0;
        snap_det <= 1'b0;
        snap_flags <= 3'b000;
        seq <= 8'd0;
        dropped_count <= 16'd0;
        ft601_data_out <= 32'd0;
        ft601_data_oe <= 1'b0;
        ft601_be <= 2'b11;
        ft601_wr_n <= 1'b1;
    end else begin
        case (state)
            S_IDLE: begin
                ft601_wr_n <= 1'b1;
                ft601_data_oe <= 1'b0;
                if (trigger) begin
                    snap_range <= range_profile;
                    snap_dre <= doppler_real;
                    snap_dim <= doppler_imag;
                    snap_det <= cfar_detection;
                    snap_flags <= {cfar_valid, doppler_valid, range_valid};
                    word_idx <= 4'd0;
                    state <= S_SEND;
                end
            end

            S_SEND: begin
                if (trigger && dropped_count != 16'hFFFF)
                    dropped_count <= dropped_count + 16'd1;
                if (!ft601_txe) begin
                    ft601_data_oe <= 1'b1;
                    ft601_be <= 2'b11;
                    ft601_data_out <= packet_word(word_idx);
                    ft601_wr_n <= 1'b0;
                    if (word_idx == PACKET_WORDS - 1) begin
                        state <= S_GAP;
                    end else begin
                        word_idx <= word_idx + 4'd1;
                    end
                end else begin
                    ft601_wr_n <= 1'b1;   // hold while the FT601 cannot accept
                end
            end

            S_GAP: begin
                if (trigger && dropped_count != 16'hFFFF)
                    dropped_count <= dropped_count + 16'd1;
                ft601_wr_n <= 1'b1;
                ft601_data_oe <= 1'b0;
                seq <= seq + 8'd1;
                state <= S_IDLE;
            end

            default: state <= S_IDLE;
        endcase
    end
end

// Optional clock for the FT601 (clk / 2) - single driver
always @(posedge clk or negedge reset_n) begin
    if (!reset_n)
        ft601_clk_out <= 1'b0;
    else
        ft601_clk_out <= ~ft601_clk_out;
end

endmodule
