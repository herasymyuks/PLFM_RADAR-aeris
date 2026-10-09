// host_bridge_spi.v — AERIS-10 host-link option B (DSN-LINK-01): SPI slave (mode 0, MSB first)
// on the existing STM32_SCLK1/MOSI1/MISO1 lines with DIG_5 as FPGA_CS_N and DIG_6 as DRDY.
// Streams the frame built by rd_map_packer from a 2-bank dual-port RAM and appends CRC-16/CCITT-FALSE.
// The SPI side runs in the SCLK domain (SCLK ≤ 27 MHz); the packer side in clk.  BETA — iverilog only.
//
// Command set v2 (HOST_LINK_DESIGN.md §7; firmware counterpart beta/stm32/Core/Src/host_bridge_proto.c).
// First byte after CS_N falls = command; bytes marked <- are driven on MISO, the master clocks 0x00:
//   0x01                          : frame + CRC-16 (unchanged, zeros when no frame is ready)
//   0x02 a0 a1 d0 d1 d2 d3 xx     : write register word {a1,a0} = {d3,d2,d1,d0}; <- byte 7 = 0xA2 (ack).
//                                   The write is handed to the clk domain when d3 is complete and
//                                   commits within ~5 clk cycles; the ack means "accepted".
//   0x03 a0 a1 xx xx xx xx        : <- bytes 3..6 = d0 d1 d2 d3 (little-endian) of register {a1,a0}.
//                                   No turnaround byte: the read is launched in the clk domain as soon
//                                   as a0 is complete (reg_addr = {8'h00, a0}); a1 is accepted but NOT
//                                   decoded (the register map has 5 address bits). d0 is loaded on the
//                                   falling SCLK edge after a1, i.e. ≥ 8 SCLK periods (≥ 296 ns at
//                                   27 MHz ≥ 29 clk cycles at 100 MHz) after the request; the fetch takes
//                                   ≤ 5 clk cycles (3-flop synchroniser + address + data register).
//   0x04 xx*8                     : <- 8 bytes = four little-endian u16: status_in[15:0] (bit0 frame
//                                   ready, bit1 ADAR CS conflict, bit2 FIFO overflow, bit3 calibration
//                                   lock; bits 4..15 as assembled by the top), RTL_VERSION,
//                                   frames_produced, 0x0000. Sampled in the SCLK domain when the command
//                                   byte completes (quasi-static values; frames_produced may be one old).
//   other (incl. 0x00)            : <- 0xEE on every following byte.
// Register port (clk domain): reg_we one-clock pulse with reg_addr/reg_wdata; reg_rdata must be
// combinational from reg_addr (it is sampled one clk after reg_addr is driven).
`timescale 1ns/1ps
module host_bridge_spi #(
    parameter [15:0] RTL_VERSION = 16'h0002
) (
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
    // register access (clk domain) - command set v2
    output reg         reg_we,          // one-clock pulse
    output reg  [15:0] reg_addr,        // valid with reg_we and during a read fetch
    output reg  [31:0] reg_wdata,
    input  wire [31:0] reg_rdata,       // combinational read data for reg_addr
    input  wire [15:0] status_in,       // status word for command 0x04 (bit assignment by the top)
    input  wire [15:0] frames_produced,
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

    // SPI-domain state (declared early: used by the clk-domain synchronisers)
    reg [2:0]  bitc;
    reg [7:0]  shin;
    reg [7:0]  shout;
    reg [7:0]  cmd;               // command byte (0x00 while receiving it; 0x00 itself is stored as 0xFF)
    reg [3:0]  bytec;             // number of complete parameter bytes after the command (saturating)
    reg        streaming;
    reg [12:0] raddr;
    reg [12:0] end_addr;
    reg [15:0] crc;
    reg [1:0]  crc_phase;         // 0 data, 1 crc hi, 2 crc lo, 3 done
    reg        xfer_done_t;       // toggles when a frame has been fully read
    reg [15:0] cmd_addr;          // register address (parameter bytes 0, 1)
    reg [31:0] cmd_data;          // register write data (parameter bytes 2..5)
    reg        rd_req_t;          // toggles when a0 of a 0x03 read is complete
    reg        wr_req_t;          // toggles when d3 of a 0x02 write is complete
    reg [63:0] status_snap;       // 0x04 reply, sampled when the command byte completes

    // frame bookkeeping (clk domain)
    reg        rd_bank_pending;   // bank of the frame to be read next
    reg [11:0] len_pending;
    reg        ready;             // frame available
    reg        done_ack_s1, done_ack_s2, done_ack_s3;
    // register access (clk domain)
    (* ASYNC_REG = "TRUE" *) reg rd_s1, rd_s2, wr_s1, wr_s2;
    reg        rd_s3, wr_s3;
    reg        rd_fetch;          // reg_addr was driven last clock: capture reg_rdata now
    reg [31:0] rd_data_hold;      // read data held for the SPI domain (stable until the next read)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin ready <= 0; rd_bank_pending <= 0; len_pending <= 0; consumed <= 0;
                          done_ack_s1 <= 0; done_ack_s2 <= 0; done_ack_s3 <= 0;
                          rd_s1 <= 0; rd_s2 <= 0; rd_s3 <= 0; wr_s1 <= 0; wr_s2 <= 0; wr_s3 <= 0;
                          reg_we <= 0; reg_addr <= 0; reg_wdata <= 0; rd_fetch <= 0; rd_data_hold <= 0; end
        else begin
            consumed <= 0;
            reg_we   <= 0;
            rd_fetch <= 0;
            {done_ack_s3, done_ack_s2, done_ack_s1} <= {done_ack_s2, done_ack_s1, xfer_done_t};
            {rd_s3, rd_s2, rd_s1} <= {rd_s2, rd_s1, rd_req_t};
            {wr_s3, wr_s2, wr_s1} <= {wr_s2, wr_s1, wr_req_t};
            if (frame_done) begin ready <= 1; rd_bank_pending <= frame_bank; len_pending <= frame_len; end
            if (done_ack_s2 != done_ack_s3) begin ready <= 0; consumed <= 1; end   // toggle from SPI domain
            // register read: drive the address, capture the combinational read data one clock later
            if (rd_s2 != rd_s3) begin reg_addr <= cmd_addr; rd_fetch <= 1; end
            if (rd_fetch) rd_data_hold <= reg_rdata;
            // register write: address + data were complete ≥ 2 clk before the toggle is seen here
            if (wr_s2 != wr_s3) begin reg_addr <= cmd_addr; reg_wdata <= cmd_data; reg_we <= 1; end
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

    // sample MOSI on rising SCLK (this block owns bitc, shin, cmd, bytec, streaming, cmd_addr,
    // cmd_data, rd_req_t, wr_req_t, status_snap)
    wire [7:0] rx_byte = {shin[6:0], mosi};   // the complete byte at its 8th rising edge
    always @(posedge sclk or posedge cs_n) begin
        if (cs_n) begin bitc <= 0; shin <= 0; cmd <= 8'h00; bytec <= 0; streaming <= 0; end
        else begin
            shin <= {shin[6:0], mosi};
            bitc <= bitc + 1;
            if (bitc == 3'd7) begin
                if (cmd == 8'h00) begin                             // command byte complete
                    cmd <= (rx_byte == 8'h00) ? 8'hFF : rx_byte;    // 0x00 is an unknown command too
                    if (rx_byte == 8'h01 && ready) streaming <= 1;
                    if (rx_byte == 8'h04) status_snap <= {16'h0000, frames_produced, RTL_VERSION, status_in};
                end else begin                                      // parameter byte number bytec complete
                    if (bytec != 4'd15) bytec <= bytec + 1;
                    case (cmd)
                        8'h02: case (bytec)
                                   4'd0: cmd_addr[7:0]   <= rx_byte;
                                   4'd1: cmd_addr[15:8]  <= rx_byte;
                                   4'd2: cmd_data[7:0]   <= rx_byte;
                                   4'd3: cmd_data[15:8]  <= rx_byte;
                                   4'd4: cmd_data[23:16] <= rx_byte;
                                   4'd5: begin cmd_data[31:24] <= rx_byte; wr_req_t <= ~wr_req_t; end
                                   default: ;
                               endcase
                        8'h03: case (bytec)
                                   4'd0: begin cmd_addr <= {8'h00, rx_byte}; rd_req_t <= ~rd_req_t; end  // launch now
                                   4'd1: cmd_addr[15:8] <= rx_byte;    // accepted, not decoded (see header)
                                   default: ;
                               endcase
                        default: ;
                    endcase
                end
            end
        end
    end
    initial begin rd_req_t = 0; wr_req_t = 0; cmd_addr = 0; cmd_data = 0; status_snap = 0; end

    // byte fetch + MISO shift on falling SCLK (this block owns shout, raddr, end_addr, crc, crc_phase,
    // stream_init, xfer_done_t). At the falling edge after byte i completes, bytec == i-1 for i ≥ 1
    // (0 after the command byte) and the byte sent at index i+1 is loaded.
    reg        stream_init;
    wire [12:0] first_addr = {rd_bank_pending, 12'd0};
    wire [7:0]  ram_byte   = ram[raddr];
    wire [7:0]  first_byte = ram[first_addr];
    always @(negedge sclk or posedge cs_n) begin
        if (cs_n) begin shout <= 8'h00; stream_init <= 0; crc_phase <= 0; raddr <= 0; end_addr <= 0; crc <= 16'hFFFF; end
        else if (bitc == 3'd0) begin              // start of a new byte: load it
            case (cmd)
                8'h00: shout <= 8'h00;            // still receiving the command byte
                8'h01: begin
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
                    end else shout <= 8'h00;      // 0x01 with no frame ready: zeros (no sync word)
                end
                8'h02: shout <= (bytec == 4'd6) ? 8'hA2 : 8'h00;     // ack in byte 7 (after d3)
                8'h03: case (bytec)                                   // d0..d3 in bytes 3..6
                           4'd2: shout <= rd_data_hold[7:0];
                           4'd3: shout <= rd_data_hold[15:8];
                           4'd4: shout <= rd_data_hold[23:16];
                           4'd5: shout <= rd_data_hold[31:24];
                           default: shout <= 8'h00;
                       endcase
                8'h04: shout <= (bytec < 4'd8) ? status_snap[8*bytec +: 8] : 8'h00;   // bytes 1..8
                default: shout <= 8'hEE;                              // unknown command
            endcase
        end else shout <= {shout[6:0], 1'b0};
    end
    assign miso = cs_n ? 1'bz : shout[7];
    initial xfer_done_t = 0;
endmodule
