`timescale 1ns / 1ps
// ============================================================================
// unisim_sim_models.v  -  SIMULATION / LINT ONLY behavioural stand-ins for the
// Xilinx 7-series UNISIM primitives used by the AERIS-10 beta RTL.
//
// NOT FOR SYNTHESIS. Vivado provides the real primitives; this file is excluded
// from the synthesis file set by vivado/create_project.tcl. It exists so that
// Icarus Verilog / Verilator can elaborate the synthesis view of the design
// without $XILINX_VIVADO/data/verilog/src/unisims.
//
// Modelled subset (parameters accepted, behaviour simplified):
//   BUFG   : O = I
//   IBUFDS : O = I (IB is ignored; the TB drives IB = ~I)
//   IDDR   : OPPOSITE_EDGE / SAME_EDGE / SAME_EDGE_PIPELINED, CE, sync/async R
// Status: BETA. Not equivalent to the UNISIM timing models.
// ============================================================================

module BUFG (
    input  wire I,
    output wire O
);
    assign O = I;
endmodule

module IBUFDS #(
    parameter DIFF_TERM    = "FALSE",
    parameter IBUF_LOW_PWR = "TRUE",
    parameter IOSTANDARD   = "DEFAULT"
) (
    input  wire I,
    input  wire IB,
    output wire O
);
    /* verilator lint_off UNUSEDSIGNAL */
    wire unused_ib = IB;   // the complementary input carries no information in this model
    /* verilator lint_on UNUSEDSIGNAL */
    assign O = I;
endmodule

module IDDR #(
    parameter DDR_CLK_EDGE = "OPPOSITE_EDGE",
    parameter INIT_Q1      = 1'b0,
    parameter INIT_Q2      = 1'b0,
    parameter SRTYPE       = "SYNC"
) (
    output wire Q1,
    output wire Q2,
    input  wire C,
    input  wire CE,
    input  wire D,
    input  wire R,
    input  wire S
);
    reg q_rise = INIT_Q1;   // D sampled on the rising edge of C
    reg q_fall = INIT_Q2;   // D sampled on the falling edge of C
    reg q_rise_p = INIT_Q1; // q_rise re-registered on the rising edge (pipeline stage)
    reg q_fall_p = INIT_Q2; // q_fall re-registered on the rising edge

    always @(posedge C) begin
        if (R)       q_rise <= 1'b0;
        else if (S)  q_rise <= 1'b1;
        else if (CE) q_rise <= D;
    end
    always @(negedge C) begin
        if (R)       q_fall <= 1'b0;
        else if (S)  q_fall <= 1'b1;
        else if (CE) q_fall <= D;
    end
    always @(posedge C) begin
        if (R) begin
            q_rise_p <= 1'b0;
            q_fall_p <= 1'b0;
        end else begin
            q_rise_p <= q_rise;
            q_fall_p <= q_fall;
        end
    end

    // OPPOSITE_EDGE       : Q1 = rising sample (at the rising edge), Q2 = falling sample (at the falling edge)
    // SAME_EDGE           : Q1 = rising sample, Q2 = previous falling sample, both presented on the rising edge
    // SAME_EDGE_PIPELINED : as SAME_EDGE but Q1 delayed one more cycle so Q1/Q2 belong to the same bit period
    assign Q1 = (DDR_CLK_EDGE == "SAME_EDGE_PIPELINED") ? q_rise_p : q_rise;
    assign Q2 = (DDR_CLK_EDGE == "OPPOSITE_EDGE")       ? q_fall   : q_fall_p;
endmodule
