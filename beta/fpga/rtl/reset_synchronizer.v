`timescale 1ns / 1ps
// ============================================================================
// reset_synchronizer.v  -  asynchronous-assert / synchronous-release reset
// synchroniser (one per clock domain).  BETA - AERIS-10 beta FPGA project.
//
// The top level has a single active-low reset (reset_n, STM32 DIG_4). Every
// clock domain that is not clk_100m (adc_dco 400 MHz, clk_120m_dac) must
// release reset synchronously to its own clock, otherwise flip-flops come out
// of reset in different cycles (recovery/removal violations).
// ============================================================================
module reset_synchronizer #(
    parameter STAGES = 2
) (
    input  wire clk,
    input  wire async_reset_n,   // asynchronous active-low reset (asserted immediately)
    output wire sync_reset_n     // released STAGES clock edges after async_reset_n rises
);
    // The shift register is asynchronously cleared and synchronously shifted by design
    // (Verilator SYNCASYNCNET is the expected pattern for a reset synchroniser).
    /* verilator lint_off SYNCASYNCNET */
    (* ASYNC_REG = "TRUE" *) reg [STAGES-1:0] sync_ff;
    /* verilator lint_on SYNCASYNCNET */

    always @(posedge clk or negedge async_reset_n) begin
        if (!async_reset_n)
            sync_ff <= {STAGES{1'b0}};
        else
            sync_ff <= {sync_ff[STAGES-2:0], 1'b1};
    end

    assign sync_reset_n = sync_ff[STAGES-1];
endmodule
