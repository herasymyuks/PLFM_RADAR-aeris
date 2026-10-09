`timescale 1ns / 1ps
// ============================================================================
// ad9484_iserdes_capture.v  -  AD9484 LVDS capture without 400 MHz fabric logic.
// BETA (not synthesised, not on hardware).
//
// Datasheet facts (7_Components Datasheets and Application notes/AD9484/AD9484.pdf,
// Table 4 and "Output Data Rate", re-checked 2026-10-09): LVDS SDR, 8 data pairs,
// DCO at the sampling clock rate (400 MHz here, AD9523 OUT4), data valid on the
// rising DCO edge, data-to-DCO skew tSKEW = -0.07..+0.07 ns (tPD 0.85 ns, tCPD
// 0.6 ns typ), output latency 15 clocks, offset binary by default.
//
// Structure (all in bank 14, one clock region: DCO on N14/P14 = MRCC pair):
//   adc_dco_p/n -> IBUFDS -> BUFIO (clk_io, 400 MHz, I/O clock network only)
//                        \-> BUFR /4 (clk_div, 100 MHz regional clock)
//   adc_d_p/n[i] -> IBUFDS -> IDELAYE2 (VAR_LOAD, tap from adc_capture_calib)
//                -> ISERDESE2 (SDR 1:4, NETWORKING, CLK = clk_io, CLKDIV = clk_div)
//   IDELAYCTRL with clk_200m_ref (clk_gen.v) -> idelay_rdy
//   4 samples x 8 bit per clk_div cycle -> async_fifo (32 bit) -> clk_100m domain
//
// Word format: word[7:0] = oldest sample (s0), word[31:24] = newest (s3), with
// Q1_IS_OLDEST = 1 (ISERDESE2 Q1 = first bit received). The Q ordering is
// UNVERIFIED against UG471 Fig. 3-13; if hardware shows the reverse, set the
// parameter to 0 (a wrong setting reverses the sample order inside every word,
// which the PN9 test pattern on the ADC exposes - see README).
//
// Clock assumption: clk_div (DCO/4) and clk_100m (AD9523 OUT6) are both 100 MHz
// from the same AD9523, i.e. frequency-locked with unknown phase. The FIFO
// (depth 16) absorbs the phase and jitter; fifo_overflow is sticky and must stay
// 0 - if the two clocks were not frequency-locked it would set within ms.
// SDR 1:4 is used, not DDR 1:8 (datasheet: SDR only).
// ============================================================================
module ad9484_iserdes_capture #(
    parameter DIFF_TERM    = "FALSE",   // bank 14 VCCO = 3.3 V: external 100 Ohm termination required
    parameter Q1_IS_OLDEST = 1,
    parameter VALID_DELAY  = 16
) (
    // LVDS pins
    input  wire [7:0]  adc_d_p,
    input  wire [7:0]  adc_d_n,
    input  wire        adc_dco_p,
    input  wire        adc_dco_n,
    // resets / reference
    input  wire        reset_n,        // asynchronous active-low
    input  wire        clk_200m_ref,   // IDELAYCTRL reference (clk_gen.v)
    input  wire        ref_locked,     // MMCM locked
    output wire        idelay_rdy,
    // regional clock domain (clk_div = DCO/4) - calibration interface
    output wire        clk_div,
    output wire        rst_n_div,
    input  wire [7:0]  tap_ld,         // per lane: load tap_val[lane]
    input  wire [39:0] tap_val,        // 8 x 5-bit IDELAY tap values
    input  wire [7:0]  bitslip,        // per lane: one-cycle BITSLIP pulse
    output wire [39:0] tap_cur,        // 8 x 5-bit CNTVALUEOUT
    output wire [31:0] word_div,       // {s3,s2,s1,s0} in the clk_div domain (for calibration)
    output wire        word_div_valid,
    // system clock domain
    input  wire        clk_100m,
    input  wire        rst_n_100m,
    output wire [31:0] word,           // {s3,s2,s1,s0}
    output wire        word_valid,
    output wire        fifo_overflow   // sticky: a word was lost (clock assumption violated)
);
    // ---------------- DCO: IBUFDS -> BUFIO + BUFR/4 ----------------
    wire dco_se, clk_io;
    IBUFDS #(.DIFF_TERM(DIFF_TERM), .IOSTANDARD("LVDS_25")) u_ibufds_dco (
        .O(dco_se), .I(adc_dco_p), .IB(adc_dco_n));
    BUFIO u_bufio (.I(dco_se), .O(clk_io));
    BUFR #(.BUFR_DIVIDE("4"), .SIM_DEVICE("7SERIES")) u_bufr (
        .O(clk_div), .CE(1'b1), .CLR(~reset_n), .I(dco_se));

    // reset synchronised into the regional clock domain
    wire rst_n_div_i;
    reset_synchronizer #(.STAGES(2)) u_rst_div (
        .clk(clk_div), .async_reset_n(reset_n & ref_locked), .sync_reset_n(rst_n_div_i));
    assign rst_n_div = rst_n_div_i;
    wire rst_div = ~rst_n_div_i;

    // ---------------- IDELAYCTRL ----------------
    IDELAYCTRL u_idelayctrl (.RDY(idelay_rdy), .REFCLK(clk_200m_ref), .RST(~(reset_n & ref_locked)));

    // ---------------- 8 lanes: IBUFDS -> IDELAYE2 -> ISERDESE2 ----------------
    wire [7:0] data_se, data_dly;
    wire [7:0] q1, q2, q3, q4;
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : g_lane
            IBUFDS #(.DIFF_TERM(DIFF_TERM), .IOSTANDARD("LVDS_25")) u_ibufds (
                .O(data_se[i]), .I(adc_d_p[i]), .IB(adc_d_n[i]));

            IDELAYE2 #(
                .CINVCTRL_SEL("FALSE"), .DELAY_SRC("IDATAIN"), .HIGH_PERFORMANCE_MODE("TRUE"),
                .IDELAY_TYPE("VAR_LOAD"), .IDELAY_VALUE(16), .PIPE_SEL("FALSE"),
                .REFCLK_FREQUENCY(200.0), .SIGNAL_PATTERN("DATA")
            ) u_idelay (
                .CNTVALUEOUT(tap_cur[5*i +: 5]), .DATAOUT(data_dly[i]),
                .C(clk_div), .CE(1'b0), .CINVCTRL(1'b0), .CNTVALUEIN(tap_val[5*i +: 5]),
                .DATAIN(1'b0), .IDATAIN(data_se[i]), .INC(1'b0), .LD(tap_ld[i]),
                .LDPIPEEN(1'b0), .REGRST(1'b0));

            ISERDESE2 #(
                .DATA_RATE("SDR"), .DATA_WIDTH(4), .DYN_CLKDIV_INV_EN("FALSE"), .DYN_CLK_INV_EN("FALSE"),
                .INIT_Q1(1'b0), .INIT_Q2(1'b0), .INIT_Q3(1'b0), .INIT_Q4(1'b0),
                .INTERFACE_TYPE("NETWORKING"), .IOBDELAY("IFD"), .NUM_CE(1), .OFB_USED("FALSE"),
                .SERDES_MODE("MASTER"), .SRVAL_Q1(1'b0), .SRVAL_Q2(1'b0), .SRVAL_Q3(1'b0), .SRVAL_Q4(1'b0)
            ) u_iserdes (
                .O(), .Q1(q1[i]), .Q2(q2[i]), .Q3(q3[i]), .Q4(q4[i]), .Q5(), .Q6(), .Q7(), .Q8(),
                .SHIFTOUT1(), .SHIFTOUT2(),
                .BITSLIP(bitslip[i]), .CE1(1'b1), .CE2(1'b0),
                .CLK(clk_io), .CLKB(~clk_io), .CLKDIV(clk_div), .CLKDIVP(1'b0),
                .D(data_se[i]), .DDLY(data_dly[i]),
                .DYNCLKDIVSEL(1'b0), .DYNCLKSEL(1'b0), .OCLK(1'b0), .OCLKB(1'b0), .OFB(1'b0),
                .RST(rst_div), .SHIFTIN1(1'b0), .SHIFTIN2(1'b0));
        end
    endgenerate

    // ---------------- word assembly + valid (clk_div) ----------------
    wire [31:0] word_asm = (Q1_IS_OLDEST != 0) ? {q4, q3, q2, q1} : {q1, q2, q3, q4};
    reg  [31:0] word_r;
    reg  [4:0]  valid_cnt;
    reg         valid_r;
    always @(posedge clk_div or negedge rst_n_div_i) begin
        if (!rst_n_div_i) begin
            word_r <= 32'd0; valid_cnt <= 5'd0; valid_r <= 1'b0;
        end else begin
            word_r <= word_asm;
            if (idelay_rdy) begin
                if (valid_cnt == VALID_DELAY[4:0]) valid_r <= 1'b1;
                else valid_cnt <= valid_cnt + 5'd1;
            end
        end
    end
    assign word_div       = word_r;
    assign word_div_valid = valid_r;

    // ---------------- clk_div -> clk_100m ----------------
    wire        fifo_empty;
    wire [15:0] ovf_cnt;
    async_fifo #(.WIDTH(32), .ADDR_BITS(4)) u_fifo (
        .wr_clk(clk_div), .wr_reset_n(rst_n_div_i), .wr_en(valid_r), .wr_data(word_r),
        .full(), .wr_overflow_count(ovf_cnt),
        .rd_clk(clk_100m), .rd_reset_n(rst_n_100m), .rd_en(!fifo_empty),
        .rd_data(word), .rd_valid(word_valid), .empty(fifo_empty));
    assign fifo_overflow = (ovf_cnt != 16'd0);
endmodule
