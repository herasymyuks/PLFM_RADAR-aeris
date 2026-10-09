`timescale 1ns / 1ps
// edge_detector_enhanced  -  STM32 toggle-line edge detector.
// BETA (beta/fpga/CHANGELOG.md): the original (:16-23) took the edge from the FIRST
// synchroniser stage, so a metastable sample could propagate. Now: two synchroniser
// flops (ASYNC_REG) followed by one history flop; the edge is taken between the second
// synchroniser stage and the history flop. Module name and ports unchanged; latency
// increases by one clock.
module edge_detector_enhanced (
    input  wire clk,
    input  wire reset_n,
    input  wire signal_in,
    output wire rising_falling_edge
);
    (* ASYNC_REG = "TRUE" *) reg signal_sync0;
    (* ASYNC_REG = "TRUE" *) reg signal_sync1;
    reg signal_prev;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            signal_sync0 <= 1'b0;
            signal_sync1 <= 1'b0;
            signal_prev  <= 1'b0;
        end else begin
            signal_sync0 <= signal_in;
            signal_sync1 <= signal_sync0;
            signal_prev  <= signal_sync1;
        end
    end

    // one-clock pulse on either edge of the (synchronised) toggle line
    assign rising_falling_edge = signal_sync1 ^ signal_prev;
endmodule
