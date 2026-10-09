`timescale 1ns / 1ps
// ============================================================================
// async_fifo.v  -  dual-clock FIFO with Gray-code pointers (Cummings style).
// BETA - AERIS-10 beta FPGA project.
//
// Replaces cdc_adc_to_processing (cdc_modules.v) on the CIC (clk_400m) ->
// FIR (clk_100m) data path. Gray-coding arbitrary data words, as the original
// module did, is not a valid clock-domain crossing; a FIFO with Gray-coded
// pointers is. Depth = 2**ADDR_BITS words. Both clocks are nominally
// phase-locked (AD9523 outputs) so the FIFO only absorbs phase, not rate.
//
// Write side : wr_en with wr_data when !full (writes while full are dropped
//              and counted in wr_overflow_count).
// Read side  : rd_en pops one word; rd_data/rd_valid are registered one cycle
//              later ("standard" FIFO, not first-word-fall-through).
// ============================================================================
module async_fifo #(
    parameter WIDTH     = 18,
    parameter ADDR_BITS = 4
) (
    // write domain
    input  wire                 wr_clk,
    input  wire                 wr_reset_n,
    input  wire                 wr_en,
    input  wire [WIDTH-1:0]     wr_data,
    output reg                  full,
    output reg  [15:0]          wr_overflow_count,
    // read domain
    input  wire                 rd_clk,
    input  wire                 rd_reset_n,
    input  wire                 rd_en,
    output reg  [WIDTH-1:0]     rd_data,
    output reg                  rd_valid,
    output reg                  empty
);
    localparam DEPTH = (1 << ADDR_BITS);

    reg [WIDTH-1:0] mem [0:DEPTH-1];

    // pointers (declared first: both sides refer to the other's gray pointer)
    reg  [ADDR_BITS:0] wr_bin;
    reg  [ADDR_BITS:0] wr_gray;
    reg  [ADDR_BITS:0] rd_bin;
    reg  [ADDR_BITS:0] rd_gray;

    // ---------------- write pointer (binary + gray) ----------------
    wire [ADDR_BITS:0] wr_bin_next  = wr_bin + {{ADDR_BITS{1'b0}}, (wr_en & ~full)};
    wire [ADDR_BITS:0] wr_gray_next = (wr_bin_next >> 1) ^ wr_bin_next;

    // read pointer synchronised into the write domain
    (* ASYNC_REG = "TRUE" *) reg [ADDR_BITS:0] rd_gray_wsync1, rd_gray_wsync2;

    wire full_next = (wr_gray_next == {~rd_gray_wsync2[ADDR_BITS:ADDR_BITS-1], rd_gray_wsync2[ADDR_BITS-2:0]});

    always @(posedge wr_clk or negedge wr_reset_n) begin
        if (!wr_reset_n) begin
            wr_bin            <= {(ADDR_BITS+1){1'b0}};
            wr_gray           <= {(ADDR_BITS+1){1'b0}};
            rd_gray_wsync1    <= {(ADDR_BITS+1){1'b0}};
            rd_gray_wsync2    <= {(ADDR_BITS+1){1'b0}};
            wr_overflow_count <= 16'd0;
            full              <= 1'b0;
        end else begin
            wr_bin         <= wr_bin_next;
            wr_gray        <= wr_gray_next;
            full           <= full_next;
            rd_gray_wsync1 <= rd_gray;
            rd_gray_wsync2 <= rd_gray_wsync1;
            if (wr_en && full && wr_overflow_count != 16'hFFFF)
                wr_overflow_count <= wr_overflow_count + 16'd1;
        end
    end

    always @(posedge wr_clk) begin
        if (wr_en && !full)
            mem[wr_bin[ADDR_BITS-1:0]] <= wr_data;
    end

    // ---------------- read pointer (binary + gray) ----------------
    wire               do_read      = rd_en & ~empty;
    wire [ADDR_BITS:0] rd_bin_next  = rd_bin + {{ADDR_BITS{1'b0}}, do_read};
    wire [ADDR_BITS:0] rd_gray_next = (rd_bin_next >> 1) ^ rd_bin_next;

    (* ASYNC_REG = "TRUE" *) reg [ADDR_BITS:0] wr_gray_rsync1, wr_gray_rsync2;

    wire empty_next = (rd_gray_next == wr_gray_rsync2);

    always @(posedge rd_clk or negedge rd_reset_n) begin
        if (!rd_reset_n) begin
            rd_bin         <= {(ADDR_BITS+1){1'b0}};
            rd_gray        <= {(ADDR_BITS+1){1'b0}};
            wr_gray_rsync1 <= {(ADDR_BITS+1){1'b0}};
            wr_gray_rsync2 <= {(ADDR_BITS+1){1'b0}};
            rd_valid       <= 1'b0;
            rd_data        <= {WIDTH{1'b0}};
            empty          <= 1'b1;
        end else begin
            rd_bin         <= rd_bin_next;
            rd_gray        <= rd_gray_next;
            empty          <= empty_next;
            wr_gray_rsync1 <= wr_gray;
            wr_gray_rsync2 <= wr_gray_rsync1;
            rd_valid       <= do_read;
            if (do_read)
                rd_data <= mem[rd_bin[ADDR_BITS-1:0]];
        end
    end
endmodule
