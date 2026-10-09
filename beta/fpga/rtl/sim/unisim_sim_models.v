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

// ============================================================================
// Added for the ISERDES capture path (beta follow-up). Behavioural only.
//   BUFIO        : O = I
//   BUFR         : divide-by-N (BUFR_DIVIDE "1".."8" or "BYPASS"), CE, async CLR
//   IDELAYE2     : VAR_LOAD / FIXED / VARIABLE; tap x 1/(64*REFCLK) = 78.125 ps @ 200 MHz,
//                  modelled as a delayed assignment (inertial; data period must exceed the delay)
//   IDELAYCTRL   : RDY after 16 REFCLK cycles
//   ISERDESE2    : SDR, DATA_WIDTH 2..8, NETWORKING; Q1 = FIRST (oldest) bit received,
//                  BITSLIP rotates the word framing by one bit (UNVERIFIED against UG471 figures;
//                  the RTL has a parameter to reverse the order). A data transition within
//                  T_SU before or T_H after the sampling CLK edge gives a RANDOM bit (metastable
//                  window model, 0.20 ns each - representative, not a datasheet value), so that
//                  the IDELAY calibration sees a real fail region in simulation.
//   MMCME2_BASE  : CLKOUT0/CLKFBOUT/LOCKED only; CLKOUT0 period = CLKIN1_PERIOD * DIVCLK_DIVIDE /
//                  CLKFBOUT_MULT_F * CLKOUT0_DIVIDE_F
// Delays and real arithmetic are simulation constructs (Verilator STMTDLY/REALCVT disabled here).
// ============================================================================
/* verilator lint_off STMTDLY */
/* verilator lint_off REALCVT */
/* verilator lint_off WIDTHTRUNC */
/* verilator lint_off WIDTHEXPAND */
/* verilator lint_off UNUSEDSIGNAL */
/* verilator lint_off UNUSEDPARAM */

module BUFIO (
    input  wire I,
    output wire O
);
    assign O = I;
endmodule

module BUFR #(
    parameter BUFR_DIVIDE = "BYPASS",
    parameter SIM_DEVICE  = "7SERIES"
) (
    output wire O,
    input  wire CE,
    input  wire CLR,
    input  wire I
);
    localparam integer DIV = (BUFR_DIVIDE == "2") ? 2 : (BUFR_DIVIDE == "3") ? 3 : (BUFR_DIVIDE == "4") ? 4 :
                             (BUFR_DIVIDE == "5") ? 5 : (BUFR_DIVIDE == "6") ? 6 : (BUFR_DIVIDE == "7") ? 7 :
                             (BUFR_DIVIDE == "8") ? 8 : 1;
    reg [3:0] cnt = 0;
    reg       o_div = 0;
    always @(posedge I or posedge CLR) begin
        if (CLR) begin
            cnt <= 0; o_div <= 0;
        end else if (CE) begin
            if (cnt == DIV - 1) cnt <= 0; else cnt <= cnt + 1;
            o_div <= ((cnt == DIV - 1) ? 0 : cnt + 1) < (DIV / 2);   // high for the first DIV/2 input cycles
        end
    end
    assign O = (DIV == 1) ? I : o_div;
endmodule

module IDELAYE2 #(
    parameter CINVCTRL_SEL          = "FALSE",
    parameter DELAY_SRC             = "IDATAIN",
    parameter HIGH_PERFORMANCE_MODE = "FALSE",
    parameter IDELAY_TYPE           = "FIXED",
    parameter integer IDELAY_VALUE  = 0,
    parameter PIPE_SEL              = "FALSE",
    parameter real REFCLK_FREQUENCY = 200.0,
    parameter SIGNAL_PATTERN        = "DATA"
) (
    output wire [4:0] CNTVALUEOUT,
    output wire       DATAOUT,
    input  wire       C,
    input  wire       CE,
    input  wire       CINVCTRL,
    input  wire [4:0] CNTVALUEIN,
    input  wire       DATAIN,
    input  wire       IDATAIN,
    input  wire       INC,
    input  wire       LD,
    input  wire       LDPIPEEN,
    input  wire       REGRST
);
    reg [4:0] tap = IDELAY_VALUE[4:0];
    always @(posedge C) begin
        if (IDELAY_TYPE != "FIXED") begin
            if (LD)      tap <= CNTVALUEIN;
            else if (CE) tap <= INC ? tap + 5'd1 : tap - 5'd1;
        end
    end
    wire din = (DELAY_SRC == "DATAIN") ? DATAIN : IDATAIN;
    reg  dout = 0;
    real dly;
    always @(din) begin
        dly = tap * (1000.0 / (64.0 * REFCLK_FREQUENCY));   // ns per tap: 0.078125 at 200 MHz
        #(dly) dout = din;
    end
    assign DATAOUT     = dout;
    assign CNTVALUEOUT = tap;
endmodule

module IDELAYCTRL (
    output reg  RDY,
    input  wire REFCLK,
    input  wire RST
);
    reg [4:0] cnt;
    initial begin RDY = 0; cnt = 0; end
    always @(posedge REFCLK or posedge RST) begin
        if (RST) begin cnt <= 0; RDY <= 0; end
        else if (cnt == 5'd16) RDY <= 1'b1;
        else cnt <= cnt + 5'd1;
    end
endmodule

module ISERDESE2 #(
    parameter DATA_RATE         = "DDR",
    parameter integer DATA_WIDTH = 4,
    parameter DYN_CLKDIV_INV_EN = "FALSE",
    parameter DYN_CLK_INV_EN    = "FALSE",
    parameter INIT_Q1 = 1'b0, parameter INIT_Q2 = 1'b0, parameter INIT_Q3 = 1'b0, parameter INIT_Q4 = 1'b0,
    parameter INTERFACE_TYPE    = "MEMORY",
    parameter IOBDELAY          = "NONE",
    parameter integer NUM_CE    = 2,
    parameter OFB_USED          = "FALSE",
    parameter SERDES_MODE       = "MASTER",
    parameter SRVAL_Q1 = 1'b0, parameter SRVAL_Q2 = 1'b0, parameter SRVAL_Q3 = 1'b0, parameter SRVAL_Q4 = 1'b0
) (
    output wire O,
    output wire Q1, output wire Q2, output wire Q3, output wire Q4,
    output wire Q5, output wire Q6, output wire Q7, output wire Q8,
    output wire SHIFTOUT1, output wire SHIFTOUT2,
    input  wire BITSLIP,
    input  wire CE1, input wire CE2,
    input  wire CLK, input wire CLKB, input wire CLKDIV, input wire CLKDIVP,
    input  wire D, input wire DDLY,
    input  wire DYNCLKDIVSEL, input wire DYNCLKSEL,
    input  wire OCLK, input wire OCLKB, input wire OFB,
    input  wire RST,
    input  wire SHIFTIN1, input wire SHIFTIN2
);
    wire din = (IOBDELAY == "NONE") ? D : DDLY;
    localparam real T_SU = 0.20, T_H = 0.20;   // ns, metastability window around the CLK edge
    real t_change = -1000.0, t_sample = -1000.0;
    reg  meta_pending = 0;
    always @(din) begin
        t_change = $realtime;
        if (($realtime - t_sample) < T_H) meta_pending = 1'b1;   // hold violation on the last sample
    end
    reg [7:0] sr = 0;         // serial history, sr[0] = newest
    reg [7:0] word = 0;       // latched word, word[0] = oldest bit of the frame
    reg [7:0] q = 0;
    reg [2:0] cnt = 0;        // bit position within the frame
    reg [2:0] slip = 0;       // framing offset (BITSLIP)
    reg       frame_end = 0;
    initial if (DATA_RATE != "SDR") $display("WARNING: ISERDESE2 model implements SDR only (instance has DATA_RATE=%s)", DATA_RATE);
    always @(posedge CLK) begin
        if (RST) begin sr <= 0; cnt <= 0; word <= 0; frame_end <= 0; end
        else if (CE1) begin
            t_sample = $realtime;
            if (meta_pending) begin sr[0] <= $random; meta_pending = 1'b0; end   // corrupt previous bit (hold)
            if (($realtime - t_change) < T_SU) sr <= {sr[6:0], $random};          // setup violation
            else                                sr <= {sr[6:0], din};
            if (((cnt + slip) % DATA_WIDTH) == DATA_WIDTH - 1) begin
                frame_end <= 1'b1;
            end else frame_end <= 1'b0;
            cnt <= (cnt == DATA_WIDTH - 1) ? 3'd0 : cnt + 3'd1;
            if (frame_end) begin   // one CLK after the last bit: latch from sr (oldest bit first)
                case (DATA_WIDTH)
                    2: word <= {6'd0, sr[0], sr[1]};
                    3: word <= {5'd0, sr[0], sr[1], sr[2]};
                    4: word <= {4'd0, sr[0], sr[1], sr[2], sr[3]};
                    5: word <= {3'd0, sr[0], sr[1], sr[2], sr[3], sr[4]};
                    6: word <= {2'd0, sr[0], sr[1], sr[2], sr[3], sr[4], sr[5]};
                    7: word <= {1'd0, sr[0], sr[1], sr[2], sr[3], sr[4], sr[5], sr[6]};
                    default: word <= {sr[0], sr[1], sr[2], sr[3], sr[4], sr[5], sr[6], sr[7]};
                endcase
            end
        end
    end
    always @(posedge CLKDIV) begin
        if (RST) begin q <= 0; slip <= 0; end
        else begin
            q <= word;
            if (BITSLIP) slip <= (slip == DATA_WIDTH - 1) ? 3'd0 : slip + 3'd1;
        end
    end
    // Q1 = oldest bit of the frame ... Q(DATA_WIDTH) = newest  (UNVERIFIED ordering, see header)
    assign {Q8, Q7, Q6, Q5, Q4, Q3, Q2, Q1} = q;
    assign O = din;
    assign SHIFTOUT1 = 1'b0;
    assign SHIFTOUT2 = 1'b0;
endmodule

module MMCME2_BASE #(
    parameter BANDWIDTH            = "OPTIMIZED",
    parameter real CLKFBOUT_MULT_F = 5.0,
    parameter real CLKFBOUT_PHASE  = 0.0,
    parameter real CLKIN1_PERIOD   = 0.0,
    parameter real CLKOUT0_DIVIDE_F = 1.0,
    parameter integer CLKOUT1_DIVIDE = 1, parameter integer CLKOUT2_DIVIDE = 1, parameter integer CLKOUT3_DIVIDE = 1,
    parameter integer CLKOUT4_DIVIDE = 1, parameter integer CLKOUT5_DIVIDE = 1, parameter integer CLKOUT6_DIVIDE = 1,
    parameter real CLKOUT0_DUTY_CYCLE = 0.5, parameter real CLKOUT0_PHASE = 0.0,
    parameter CLKOUT4_CASCADE      = "FALSE",
    parameter integer DIVCLK_DIVIDE = 1,
    parameter real REF_JITTER1     = 0.0,
    parameter STARTUP_WAIT         = "FALSE"
) (
    output reg  CLKOUT0, output wire CLKOUT0B,
    output wire CLKOUT1, output wire CLKOUT1B, output wire CLKOUT2, output wire CLKOUT2B,
    output wire CLKOUT3, output wire CLKOUT3B, output wire CLKOUT4, output wire CLKOUT5, output wire CLKOUT6,
    output wire CLKFBOUT, output wire CLKFBOUTB,
    output reg  LOCKED,
    input  wire CLKIN1,
    input  wire PWRDWN,
    input  wire RST,
    input  wire CLKFBIN
);
    localparam real T0 = CLKIN1_PERIOD * DIVCLK_DIVIDE / CLKFBOUT_MULT_F * CLKOUT0_DIVIDE_F;
    integer lock_cnt;
    initial begin CLKOUT0 = 0; LOCKED = 0; lock_cnt = 0; end
    always begin
        #(T0 / 2.0) CLKOUT0 = ~CLKOUT0 & ~RST;
    end
    always @(posedge CLKIN1 or posedge RST) begin
        if (RST) begin lock_cnt <= 0; LOCKED <= 0; end
        else if (lock_cnt == 50) LOCKED <= 1'b1;
        else lock_cnt <= lock_cnt + 1;
    end
    assign CLKOUT0B  = ~CLKOUT0;
    assign CLKFBOUT  = CLKIN1;
    assign CLKFBOUTB = ~CLKIN1;
    assign CLKOUT1 = 1'b0; assign CLKOUT1B = 1'b1; assign CLKOUT2 = 1'b0; assign CLKOUT2B = 1'b1;
    assign CLKOUT3 = 1'b0; assign CLKOUT3B = 1'b1; assign CLKOUT4 = 1'b0; assign CLKOUT5 = 1'b0; assign CLKOUT6 = 1'b0;
endmodule
/* verilator lint_on UNUSEDPARAM */
/* verilator lint_on UNUSEDSIGNAL */
/* verilator lint_on WIDTHEXPAND */
/* verilator lint_on WIDTHTRUNC */
/* verilator lint_on REALCVT */
/* verilator lint_on STMTDLY */
