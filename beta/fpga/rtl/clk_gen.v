`timescale 1ns / 1ps
// ============================================================================
// clk_gen.v  -  200 MHz IDELAYCTRL reference clock from clk_100m.  BETA.
//
// The design had no MMCM/PLL (docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md section 6).
// The ISERDES capture path needs a 200 MHz REFCLK for IDELAYCTRL (tap = 78.125 ps),
// so one MMCME2_BASE is added: CLKIN1 = clk_100m (10 ns), VCO = 100 * 8 / 1 = 800 MHz
// (Artix-7 -2 range 600..1440 MHz), CLKOUT0 = 800 / 4 = 200 MHz, internal feedback.
// Resource: 1 of the 5 MMCME2 on an XC7A50T + 1 BUFG. The MMCM must be placed in the
// clock region of the IDELAYCTRL it feeds (Vivado handles this through the BUFG).
// `ifdef SIM: behavioural 200 MHz derived from clk_100m edges (no primitive).
// ============================================================================
module clk_gen (
    input  wire clk_100m,        // BUFG output of the 100 MHz system clock
    input  wire reset_n,
    output wire clk_200m_ref,    // 200 MHz, BUFG-driven
    output wire locked
);
`ifdef SIM
    /* verilator lint_off STMTDLY */
    reg clk200 = 1'b0;
    always @(posedge clk_100m) begin
        clk200 = 1'b1; #2.5 clk200 = 1'b0; #2.5 clk200 = 1'b1; #2.5 clk200 = 1'b0;
    end
    /* verilator lint_on STMTDLY */
    reg [5:0] lock_cnt;
    reg       locked_r;
    always @(posedge clk_100m or negedge reset_n) begin
        if (!reset_n) begin lock_cnt <= 6'd0; locked_r <= 1'b0; end
        else if (lock_cnt == 6'd40) locked_r <= 1'b1;
        else lock_cnt <= lock_cnt + 6'd1;
    end
    assign clk_200m_ref = clk200;
    assign locked       = locked_r;
`else
    wire clkfb, clk200_unbuf;
    MMCME2_BASE #(
        .BANDWIDTH          ("OPTIMIZED"),
        .CLKFBOUT_MULT_F    (8.0),
        .CLKFBOUT_PHASE     (0.0),
        .CLKIN1_PERIOD      (10.0),
        .CLKOUT0_DIVIDE_F   (4.0),
        .CLKOUT0_DUTY_CYCLE (0.5),
        .CLKOUT0_PHASE      (0.0),
        .DIVCLK_DIVIDE      (1),
        .REF_JITTER1        (0.010),
        .STARTUP_WAIT       ("FALSE")
    ) u_mmcm (
        .CLKOUT0  (clk200_unbuf), .CLKOUT0B (),
        .CLKOUT1  (), .CLKOUT1B (), .CLKOUT2 (), .CLKOUT2B (), .CLKOUT3 (), .CLKOUT3B (),
        .CLKOUT4  (), .CLKOUT5 (), .CLKOUT6 (),
        .CLKFBOUT (clkfb), .CLKFBOUTB (),
        .LOCKED   (locked),
        .CLKIN1   (clk_100m),
        .PWRDWN   (1'b0),
        .RST      (~reset_n),
        .CLKFBIN  (clkfb)
    );
    BUFG u_bufg_200 (.I(clk200_unbuf), .O(clk_200m_ref));
`endif
endmodule
