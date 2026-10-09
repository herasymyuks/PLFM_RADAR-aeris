`timescale 1ns / 1ps
// ============================================================================
// range_bin_decimator.v  -  reduce a 1024-bin range profile to 64 bins. BETA.
//
// Instantiated by radar_receiver_final.v:226-242 but missing from the
// repository; written from that instantiation's port list and parameters.
//
// For every DECIMATION_FACTOR consecutive input bins one output bin is
// produced (OUTPUT_BINS = INPUT_BINS / DECIMATION_FACTOR). Input bins below
// start_bin are skipped (near-range blanking). decimation_mode:
//   2'b00 : keep the first bin of each group        (sub-sampling)
//   2'b01 : keep the bin with the largest |I|+|Q|   (peak hold, default in RTL)
//   2'b10 : arithmetic mean of the group            (sum >> log2(DECIMATION_FACTOR))
//   2'b11 : saturating sum of the group
// Input bins are counted modulo INPUT_BINS; a profile may arrive with gaps in
// range_valid_in. After INPUT_BINS inputs the counters restart.
// Throughput: one input per clock, output latency 1 clock after the last bin
// of a group. Resource: 2 x (DATA_WIDTH+log2(D)) accumulators, no multipliers.
// ============================================================================
module range_bin_decimator #(
    parameter INPUT_BINS        = 1024,
    parameter OUTPUT_BINS       = 64,
    parameter DECIMATION_FACTOR = 16,
    parameter DATA_WIDTH        = 16
) (
    input  wire                          clk,
    input  wire                          reset_n,
    input  wire signed [DATA_WIDTH-1:0]  range_i_in,
    input  wire signed [DATA_WIDTH-1:0]  range_q_in,
    input  wire                          range_valid_in,
    input  wire [1:0]                    decimation_mode,
    input  wire [9:0]                    start_bin,
    output reg  signed [DATA_WIDTH-1:0]  range_i_out,
    output reg  signed [DATA_WIDTH-1:0]  range_q_out,
    output reg                           range_valid_out,
    output reg  [5:0]                    range_bin_index
);
    localparam IN_W   = 10;                        // log2(INPUT_BINS)
    localparam GRP_W  = 4;                         // log2(DECIMATION_FACTOR)
    localparam ACC_W  = DATA_WIDTH + GRP_W;        // sum of 16 values
    localparam MAG_W  = DATA_WIDTH + 1;

    reg [IN_W-1:0]  in_idx;     // position inside the 1024-bin profile
    reg [GRP_W-1:0] grp_cnt;    // position inside the current group
    reg [5:0]       out_idx;

    reg signed [ACC_W-1:0] acc_i, acc_q;
    reg signed [DATA_WIDTH-1:0] peak_i, peak_q;
    reg [MAG_W-1:0] peak_mag;
    reg signed [DATA_WIDTH-1:0] first_i, first_q;   // first sample of the current group (mode 00)

    wire [MAG_W-1:0] mag_in = (range_i_in[DATA_WIDTH-1] ? -range_i_in : range_i_in)
                            + (range_q_in[DATA_WIDTH-1] ? -range_q_in : range_q_in);

    wire accept  = range_valid_in && (in_idx >= start_bin);
    wire grp_end = accept && (grp_cnt == DECIMATION_FACTOR - 1);

    wire signed [ACC_W-1:0] sum_i = acc_i + {{GRP_W{range_i_in[DATA_WIDTH-1]}}, range_i_in};
    wire signed [ACC_W-1:0] sum_q = acc_q + {{GRP_W{range_q_in[DATA_WIDTH-1]}}, range_q_in};

    function signed [DATA_WIDTH-1:0] sat;
        input signed [ACC_W-1:0] v;
        begin
            if (v > $signed({{(ACC_W-DATA_WIDTH+1){1'b0}}, {(DATA_WIDTH-1){1'b1}}}))
                sat = {1'b0, {(DATA_WIDTH-1){1'b1}}};
            else if (v < $signed({{(ACC_W-DATA_WIDTH+1){1'b1}}, {(DATA_WIDTH-1){1'b0}}}))
                sat = {1'b1, {(DATA_WIDTH-1){1'b0}}};
            else
                sat = v[DATA_WIDTH-1:0];
        end
    endfunction

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            in_idx          <= {IN_W{1'b0}};
            grp_cnt         <= {GRP_W{1'b0}};
            out_idx         <= 6'd0;
            acc_i           <= {ACC_W{1'b0}};
            acc_q           <= {ACC_W{1'b0}};
            peak_i          <= {DATA_WIDTH{1'b0}};
            peak_q          <= {DATA_WIDTH{1'b0}};
            peak_mag        <= {MAG_W{1'b0}};
            range_i_out     <= {DATA_WIDTH{1'b0}};
            range_q_out     <= {DATA_WIDTH{1'b0}};
            range_valid_out <= 1'b0;
            range_bin_index <= 6'd0;
        end else begin
            range_valid_out <= 1'b0;

            if (range_valid_in) begin
                // profile position counter (modulo INPUT_BINS)
                if (in_idx == INPUT_BINS - 1) begin
                    in_idx  <= {IN_W{1'b0}};
                    out_idx <= 6'd0;
                    grp_cnt <= {GRP_W{1'b0}};
                end else begin
                    in_idx <= in_idx + 1'b1;
                end
            end

            if (accept) begin
                // ---- accumulate / track ----
                if (grp_cnt == 0) begin
                    acc_i    <= {{GRP_W{range_i_in[DATA_WIDTH-1]}}, range_i_in};
                    acc_q    <= {{GRP_W{range_q_in[DATA_WIDTH-1]}}, range_q_in};
                    peak_i   <= range_i_in;
                    peak_q   <= range_q_in;
                    peak_mag <= mag_in;
                end else begin
                    acc_i <= sum_i;
                    acc_q <= sum_q;
                    if (mag_in > peak_mag) begin
                        peak_i   <= range_i_in;
                        peak_q   <= range_q_in;
                        peak_mag <= mag_in;
                    end
                end

                if (grp_end) begin
                    grp_cnt <= {GRP_W{1'b0}};
                    range_valid_out <= (out_idx < OUTPUT_BINS);
                    range_bin_index <= out_idx;
                    if (out_idx != 6'd63 && in_idx != INPUT_BINS - 1)
                        out_idx <= out_idx + 6'd1;
                    case (decimation_mode)
                        2'b00: begin   // first bin of the group
                            range_i_out <= (grp_cnt == 0) ? range_i_in : first_i;
                            range_q_out <= (grp_cnt == 0) ? range_q_in : first_q;
                        end
                        2'b01: begin   // peak |I|+|Q| (compare the last bin too)
                            if (mag_in > peak_mag) begin
                                range_i_out <= range_i_in;
                                range_q_out <= range_q_in;
                            end else begin
                                range_i_out <= peak_i;
                                range_q_out <= peak_q;
                            end
                        end
                        2'b10: begin   // mean
                            range_i_out <= sum_i[ACC_W-1:GRP_W];
                            range_q_out <= sum_q[ACC_W-1:GRP_W];
                        end
                        default: begin // saturating sum
                            range_i_out <= sat(sum_i);
                            range_q_out <= sat(sum_q);
                        end
                    endcase
                end else begin
                    grp_cnt <= grp_cnt + 1'b1;
                end
            end
        end
    end

    // first sample of the current group (for mode 00)
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            first_i <= {DATA_WIDTH{1'b0}};
            first_q <= {DATA_WIDTH{1'b0}};
        end else if (accept && grp_cnt == 0) begin
            first_i <= range_i_in;
            first_q <= range_q_in;
        end
    end
endmodule
