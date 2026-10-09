`timescale 1ns / 1ps
// tb_matched_filter.v - unit test of matched_filter_processing_chain + chirp_memory_loader_param.
// Stimulus: the time-domain chirp of reference segment 1 (ifft of the .mem data, amplitude
// 6000) circularly delayed by MF_DELAY = 300 samples (tb/vectors/mf_input.hex, {Q,I} words).
// Expectation (tb/vectors/mf_expected.hex from numpy with the same fixed-point model): the
// pulse-compressed block has its |I|+|Q| peak at bin 300 (+/-4: the mainlobe of a 6.67 MHz
// segment is ~15 bins wide and flat-topped, so the argmax wobbles with rounding) and is at least
// 3x larger than every bin outside the +/-16-bin mainlobe. Self-checking.
module tb_matched_filter;
    reg clk = 0, reset_n = 0;
    always #5 clk = ~clk;

    reg [31:0] din [0:1023];
    reg [31:0] dexp [0:1];

    // chain <-> memory
    wire [11:0] ref_addr;
    wire        ref_req;
    wire [15:0] ref_i, ref_q;
    wire        mem_ready;

    reg  [15:0] in_i = 0, in_q = 0;
    reg         in_valid = 0;
    wire [15:0] out_i, out_q;
    wire        out_valid;
    wire [3:0]  chain_state;

    chirp_memory_loader_param mem (
        .clk(clk), .reset_n(reset_n),
        .segment_select(ref_addr[11:10]), .mem_request(ref_req), .use_long_chirp(1'b1),
        .sample_addr(ref_addr[9:0]), .ref_i(ref_i), .ref_q(ref_q), .mem_ready(mem_ready)
    );

    matched_filter_processing_chain dut (
        .clk(clk), .reset_n(reset_n),
        .adc_data_i(in_i), .adc_data_q(in_q), .adc_valid(in_valid),
        .segment_in(2'd1), .chirp_counter(6'd0), .use_long_chirp(1'b1),
        .ref_addr(ref_addr), .ref_req(ref_req),
        .long_chirp_real(ref_i), .long_chirp_imag(ref_q),
        .short_chirp_real(ref_i), .short_chirp_imag(ref_q),
        .range_profile_i(out_i), .range_profile_q(out_q), .range_profile_valid(out_valid),
        .chain_state(chain_state)
    );

    function integer absval; input [15:0] v; begin absval = v[15] ? {16'd0, (~v) + 16'd1} : {16'd0, v}; end endfunction

    integer mag [0:1023];
    integer n_out = 0, i, peak_bin, peak_mag, side_max, d, errors = 0;
    always @(posedge clk) begin
        if (out_valid) begin
            if (n_out < 1024) mag[n_out] = absval(out_i) + absval(out_q);
            n_out = n_out + 1;
        end
    end

    initial begin
        $readmemh("tb/vectors/mf_input.hex", din);
        $readmemh("tb/vectors/mf_expected.hex", dexp);
        repeat (4) @(posedge clk);
        reset_n = 1;
        repeat (4) @(posedge clk);
        for (i = 0; i < 1024; i = i + 1) begin
            @(posedge clk);
            in_i <= din[i][15:0]; in_q <= din[i][31:16]; in_valid <= 1;
        end
        @(posedge clk); in_valid <= 0;
        // forward FFT + multiply + inverse FFT (+ model latencies) then 1024 outputs
        repeat (4000) @(posedge clk);
        if (n_out != 1024) begin
            $display("FAIL tb_matched_filter: %0d outputs, expected 1024", n_out); $fatal(1);
        end
        peak_bin = 0; peak_mag = 0;
        for (i = 0; i < 1024; i = i + 1) if (mag[i] > peak_mag) begin peak_mag = mag[i]; peak_bin = i; end
        side_max = 0;
        for (i = 0; i < 1024; i = i + 1) begin
            d = (i > peak_bin) ? (i - peak_bin) : (peak_bin - i);
            if (d > 512) d = 1024 - d;
            if (d > 16 && mag[i] > side_max) side_max = mag[i];
        end
        $display("peak bin %0d (expected %0d), |peak| %0d (model %0d), max outside mainlobe %0d, ratio %0d.%02d",
                 peak_bin, dexp[0], peak_mag, dexp[1], side_max, peak_mag / side_max, (100 * peak_mag / side_max) % 100);
        d = (peak_bin > dexp[0]) ? (peak_bin - dexp[0]) : (dexp[0] - peak_bin);
        if (d > 4) begin errors = errors + 1; $display("FAIL peak bin %0d not within 4 of %0d", peak_bin, dexp[0]); end
        if (peak_mag < 3 * side_max) begin errors = errors + 1; $display("FAIL compression ratio too low"); end
        if (peak_mag < dexp[1] / 2 || peak_mag > 2 * dexp[1]) begin errors = errors + 1; $display("FAIL peak amplitude far from model"); end
        if (errors == 0) begin $display("PASS tb_matched_filter: compression peak at bin %0d (delay 300), peak/sidelobe %0d", peak_bin, peak_mag / side_max); $finish; end
        else begin $display("FAIL tb_matched_filter: %0d errors", errors); $fatal(1); end
    end
endmodule
