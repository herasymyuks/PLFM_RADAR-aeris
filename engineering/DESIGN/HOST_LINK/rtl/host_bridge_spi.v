// host_bridge_spi.v — AERIS-10 host-link option B (DSN-LINK-01): SPI slave (mode 0, MSB first)
// on the existing STM32_SCLK1/MOSI1/MISO1 lines with DIG_5 as FPGA_CS_N and DIG_6 as DRDY.
// Streams the frame built by rd_map_packer from a 2-bank dual-port RAM and appends CRC-16/CCITT-FALSE.
// The SPI side runs in the SCLK domain (SCLK ≤ 27 MHz); the packer side in clk.  BETA — iverilog only.
`timescale 1ns/1ps
module host_bridge_spi (
    input  wire        clk,
    input  wire        rst_n,
    // packer side
    input  wire        wr_en,
    input  wire [11:0] wr_addr,
    input  wire [7:0]  wr_data,
    input  wire        wr_bank,
    input  wire        frame_bank,      // bank of the completed frame (from the packer)
    input  wire        frame_done,
    input  wire [11:0] frame_len,
    output reg         consumed,        // pulse in clk domain: a frame was fully read
    // SPI (STM32 master)
    input  wire        sclk,
    input  wire        mosi,
    output wire        miso,
    input  wire        cs_n,
    output wire        drdy,
    output wire        bridge_active    // high while cs_n low: gate the ADAR1000 pass-through
);
    // ---------------- frame RAM: 2 banks × 2304 bytes (bank = addr[12]) ----------------
    reg [7:0] ram [0:8191];
    wire [12:0] wa = {wr_bank, wr_addr};
    always @(posedge clk) if (wr_en) ram[wa] <= wr_data;

    // SPI-domain state (declared early: used by the clk-domain synchroniser)
    reg [2:0]  bitc;
    reg [7:0]  shin;
    reg [7:0]  shout;
    reg        cmd_phase;         // first byte = command
    reg        streaming;
    reg [12:0] raddr;
    reg [12:0] end_addr;
    reg [15:0] crc;
    reg [1:0]  crc_phase;         // 0 data, 1 crc hi, 2 crc lo, 3 done
    reg        xfer_done_t;       // toggles when a frame has been fully read

    // frame bookkeeping (clk domain)
    reg        rd_bank_pending;   // bank of the frame to be read next
    reg [11:0] len_pending;
    reg        ready;             // frame available
    reg        done_ack_s1, done_ack_s2, done_ack_s3;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin ready <= 0; rd_bank_pending <= 0; len_pending <= 0; consumed <= 0;
                          done_ack_s1 <= 0; done_ack_s2 <= 0; done_ack_s3 <= 0; end
        else begin
            consumed <= 0;
            {done_ack_s3, done_ack_s2, done_ack_s1} <= {done_ack_s2, done_ack_s1, xfer_done_t};
            if (frame_done) begin ready <= 1; rd_bank_pending <= frame_bank; len_pending <= frame_len; end
            if (done_ack_s2 != done_ack_s3) begin ready <= 0; consumed <= 1; end   // toggle from SPI domain
        end
    end
    assign drdy = ready;
    assign bridge_active = ~cs_n;

    // ---------------- SPI slave, SCLK domain ----------------

    function [15:0] crc16_byte;   // CRC-16/CCITT-FALSE, poly 0x1021, init 0xFFFF
        input [15:0] c; input [7:0] d; integer k; reg [15:0] x;
        begin x = c ^ {d, 8'h00};
              for (k = 0; k < 8; k = k + 1) x = x[15] ? ((x << 1) ^ 16'h1021) : (x << 1);
              crc16_byte = x; end
    endfunction

    // sample MOSI on rising SCLK (this block owns bitc, shin, cmd_phase, streaming only)
    always @(posedge sclk or posedge cs_n) begin
        if (cs_n) begin bitc <= 0; shin <= 0; cmd_phase <= 1; streaming <= 0; end
        else begin
            shin <= {shin[6:0], mosi};
            bitc <= bitc + 1;
            if (bitc == 3'd7 && cmd_phase) begin
                cmd_phase <= 0;
                if ({shin[6:0], mosi} == 8'h01 && ready) streaming <= 1;
            end
        end
    end
    // byte fetch + MISO shift on falling SCLK (this block owns shout, raddr, end_addr, crc, crc_phase, stream_init)
    reg        stream_init;
    wire [12:0] first_addr = {rd_bank_pending, 12'd0};
    wire [7:0]  ram_byte   = ram[raddr];
    wire [7:0]  first_byte = ram[first_addr];
    always @(negedge sclk or posedge cs_n) begin
        if (cs_n) begin shout <= 8'h00; stream_init <= 0; crc_phase <= 0; raddr <= 0; end_addr <= 0; crc <= 16'hFFFF; end
        else if (bitc == 3'd0) begin              // start of a new byte: load it
            if (streaming && !stream_init) begin  // first data byte right after the command byte
                stream_init <= 1;
                shout <= first_byte; crc <= crc16_byte(16'hFFFF, first_byte);
                raddr <= first_addr + 1; end_addr <= {rd_bank_pending, len_pending}; crc_phase <= 0;
            end else if (streaming) begin
                case (crc_phase)
                    2'd0: begin shout <= ram_byte; crc <= crc16_byte(crc, ram_byte);
                                if (raddr + 1 == end_addr) crc_phase <= 1;
                                raddr <= raddr + 1; end
                    2'd1: begin shout <= crc[15:8]; crc_phase <= 2; end
                    2'd2: begin shout <= crc[7:0];  crc_phase <= 3; xfer_done_t <= ~xfer_done_t; end
                    default: shout <= 8'h00;
                endcase
            end else shout <= 8'h00;
        end else shout <= {shout[6:0], 1'b0};
    end
    assign miso = cs_n ? 1'bz : shout[7];
    initial xfer_done_t = 0;
endmodule
