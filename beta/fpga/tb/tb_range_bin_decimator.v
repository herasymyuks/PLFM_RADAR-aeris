`timescale 1ns / 1ps
// tb_range_bin_decimator.v - 1024 random bins with two strong targets, peak mode (2'b01),
// against the numpy expectation (tb/vectors/decim_*.hex); also checks bin indices and that
// gaps in range_valid_in do not break the grouping. Self-checking.
module tb_range_bin_decimator;
    reg clk = 0, reset_n = 0;
    always #5 clk = ~clk;

    reg [31:0] din  [0:1023];
    reg [31:0] dexp [0:63];

    reg  signed [15:0] i_in = 0, q_in = 0;
    reg  valid_in = 0;
    wire signed [15:0] i_out, q_out;
    wire valid_out;
    wire [5:0] bin_idx;

    range_bin_decimator #(.INPUT_BINS(1024), .OUTPUT_BINS(64), .DECIMATION_FACTOR(16)) dut (
        .clk(clk), .reset_n(reset_n),
        .range_i_in(i_in), .range_q_in(q_in), .range_valid_in(valid_in),
        .decimation_mode(2'b01), .start_bin(10'd0),
        .range_i_out(i_out), .range_q_out(q_out), .range_valid_out(valid_out), .range_bin_index(bin_idx)
    );

    integer errors = 0, got = 0, i, pass_no;
    always @(posedge clk) begin
        if (valid_out) begin
            if (bin_idx !== got[5:0]) begin errors = errors + 1; $display("FAIL bin index %0d expected %0d", bin_idx, got[5:0]); end
            if ({q_out, i_out} !== dexp[got[5:0]]) begin
                errors = errors + 1;
                if (errors < 10) $display("FAIL bin %0d: got %h expected %h", got, {q_out, i_out}, dexp[got[5:0]]);
            end
            got = got + 1;
        end
    end

    initial begin
        $readmemh("tb/vectors/decim_in.hex", din);
        $readmemh("tb/vectors/decim_exp.hex", dexp);
        repeat (3) @(posedge clk);
        reset_n = 1;
        // two profiles: the first contiguous, the second with random gaps
        for (pass_no = 0; pass_no < 2; pass_no = pass_no + 1) begin
            for (i = 0; i < 1024; i = i + 1) begin
                @(posedge clk);
                if (pass_no == 1) while (($random % 3) == 0) begin valid_in <= 0; @(posedge clk); end
                i_in <= din[i][15:0]; q_in <= din[i][31:16]; valid_in <= 1;
            end
            @(posedge clk); valid_in <= 0;
            repeat (10) @(posedge clk);
        end
        if (got != 128) begin errors = errors + 1; $display("FAIL: %0d outputs, expected 128", got); end
        if (errors == 0) begin $display("PASS tb_range_bin_decimator: 2 x 64 bins, peak mode, with and without input gaps"); $finish; end
        else begin $display("FAIL tb_range_bin_decimator: %0d errors", errors); $fatal(1); end
    end
endmodule
