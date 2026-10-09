// rd_map_packer.v — AERIS-10 host-link option B (DSN-LINK-01): builds a compact range-Doppler
// frame (header + 2048 × uint8 log-magnitude + detection list) in a dual-port RAM that the SPI
// bridge streams to the STM32.  BETA — simulated with iverilog, not synthesised.
// Frame layout: see engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md §5.
// beta/fpga copy: det_wr widened to 7 bits (see beta/fpga/CHANGELOG.md); otherwise identical to
// engineering/DESIGN/HOST_LINK/rtl/rd_map_packer.v.
`timescale 1ns/1ps
module rd_map_packer #(
    parameter N_RANGE   = 64,
    parameter N_DOPPLER = 32,
    parameter MAX_DET   = 32
)(
    input  wire        clk,
    input  wire        rst_n,
    // cell stream (range-major, N_RANGE*N_DOPPLER cells per beam position)
    input  wire        frame_start,      // pulse: first cell of a new beam position follows
    input  wire        cell_valid,
    input  wire [15:0] cell_i,
    input  wire [15:0] cell_q,
    input  wire        cell_det,         // CFAR detection flag for this cell
    input  wire [7:0]  az_idx,
    input  wire [7:0]  el_idx,
    input  wire [15:0] chirp_count,
    input  wire        long_chirp,
    // frame RAM write port (to host_bridge_spi)
    output reg         wr_en,
    output reg  [11:0] wr_addr,          // 0..4095 (2 banks × 2048+… see bridge)
    output reg  [7:0]  wr_data,
    output reg         bank,             // bank being written
    output reg         frame_done,       // pulse: frame in 'frame_bank' complete, length = frame_len
    output reg         frame_bank,       // bank that holds the completed frame (valid with frame_done)
    output reg  [11:0] frame_len,        // bytes excluding CRC
    output reg         overflow          // sticky until next frame_start: previous frame not consumed
    , input wire       consumed          // bridge finished reading the other bank
);
    localparam HDR = 16;
    localparam MAP = N_RANGE * N_DOPPLER;
    reg [11:0] cell_cnt;
    reg [5:0]  n_det;
    reg [1:0]  st;               // 0 idle, 1 cells, 2 header/dets
    reg [7:0]  det_r [0:MAX_DET-1];
    reg [7:0]  det_d [0:MAX_DET-1];
    reg [7:0]  det_m [0:MAX_DET-1];
    reg [6:0]  det_wr;           // BETA fix: counts to 3*MAX_DET = 96 (was [5:0] -> hang when n_det >= 22)
    reg [4:0]  hdr_i;
    reg [15:0] seq;
    reg        busy_other;       // other bank not yet consumed
    reg [15:0] cc_lat;
    reg [7:0]  az_lat, el_lat;
    reg        long_lat;

    // |I| + |Q| → 8*log2 with 3 fractional bits (uint8, saturating)
    function [7:0] logmag;
        input [16:0] m;
        integer k; reg [4:0] msb; reg [2:0] frac; reg found;
        begin
            msb = 0; found = 0;
            for (k = 16; k >= 0; k = k - 1)
                if (!found && m[k]) begin msb = k[4:0]; found = 1; end
            if (!found) logmag = 8'd0;
            else begin
                frac = (msb >= 3) ? m[msb-1 -: 3] : {m[2:0]} ;
                if (msb >= 3) frac = (m >> (msb-3));   // next 3 bits below the MSB
                else frac = m[2:0] << (3 - msb);
                logmag = ({msb, 3'b000} | frac);
                if (msb > 5'd31) logmag = 8'hFF;
            end
        end
    endfunction

    wire [16:0] mag = {1'b0, (cell_i[15] ? -cell_i : cell_i)} + {1'b0, (cell_q[15] ? -cell_q : cell_q)};
    wire [7:0]  lm  = logmag(mag);
    wire [5:0]  r_idx = cell_cnt / N_DOPPLER;
    wire [4:0]  d_idx = cell_cnt % N_DOPPLER;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            st <= 0; cell_cnt <= 0; n_det <= 0; wr_en <= 0; wr_addr <= 0; wr_data <= 0; bank <= 0;
            frame_done <= 0; frame_bank <= 0; frame_len <= 0; overflow <= 0; det_wr <= 0; hdr_i <= 0; seq <= 0; busy_other <= 0;
            cc_lat <= 0; az_lat <= 0; el_lat <= 0; long_lat <= 0;
        end else begin
            wr_en <= 0; frame_done <= 0;
            if (consumed) busy_other <= 0;
            case (st)
            2'd0: if (frame_start) begin
                      st <= 1; cell_cnt <= 0; n_det <= 0; det_wr <= 0;
                      az_lat <= az_idx; el_lat <= el_idx; cc_lat <= chirp_count; long_lat <= long_chirp;
                      overflow <= busy_other;
                  end
            2'd1: if (cell_valid) begin
                      wr_en <= 1; wr_addr <= HDR + cell_cnt; wr_data <= lm;
                      if (cell_det && n_det < MAX_DET) begin
                          det_r[n_det] <= {2'b00, r_idx}; det_d[n_det] <= {3'b000, d_idx}; det_m[n_det] <= lm; n_det <= n_det + 1;
                      end
                      if (cell_cnt == MAP - 1) begin st <= 2; hdr_i <= 0; det_wr <= 0; end
                      cell_cnt <= cell_cnt + 1;
                  end
            2'd2: begin
                      wr_en <= 1;
                      if (hdr_i < HDR) begin
                          wr_addr <= hdr_i;
                          case (hdr_i)
                              0: wr_data <= 8'hA5;  1: wr_data <= 8'h5A;  2: wr_data <= 8'd1;
                              3: wr_data <= {6'b0, overflow, long_lat};
                              4: wr_data <= seq[7:0];  5: wr_data <= seq[15:8];
                              6: wr_data <= az_lat;    7: wr_data <= el_lat;
                              8: wr_data <= cc_lat[7:0]; 9: wr_data <= cc_lat[15:8];
                              10: wr_data <= N_RANGE[7:0]; 11: wr_data <= N_DOPPLER[7:0];
                              12: wr_data <= {2'b00, n_det}; 13: wr_data <= 8'd0;
                              default: wr_data <= 8'd0;
                          endcase
                          hdr_i <= hdr_i + 1;
                      end else if (det_wr < n_det * 3) begin
                          wr_addr <= HDR + MAP + det_wr;
                          case (det_wr % 3)
                              0: wr_data <= det_r[det_wr / 3];
                              1: wr_data <= det_d[det_wr / 3];
                              default: wr_data <= det_m[det_wr / 3];
                          endcase
                          det_wr <= det_wr + 1;
                      end else begin
                          wr_en <= 0;
                          frame_len <= HDR + MAP + n_det * 3;
                          frame_done <= 1; frame_bank <= bank; busy_other <= 1; bank <= ~bank; seq <= seq + 1; st <= 0;
                      end
                  end
            default: st <= 0;
            endcase
        end
    end
endmodule
