// tb_host_bridge.v — self-checking test of rd_map_packer + host_bridge_spi (iverilog).
// Identical copy in beta/fpga/tb/ (the frame dump goes to logs/tb_frame.hex when that directory exists).
// Scenario 1: 3 detections, frame 2075 bytes; scenario 2: 40 flagged cells -> n_det saturates at 32
// (regression for the det_wr width bug); scenario 3: command set v2 (HOST_LINK_DESIGN.md §7) against a
// 4-word register model: 0x02 write (ack 0xA2 in byte 7), 0x03 read-back (little-endian in bytes 3..6),
// 0x04 status (status word, RTL version, frames produced), unknown command -> 0xEE.
`timescale 1ns/1ps
module tb_host_bridge;
    reg clk = 0; always #5 clk = ~clk;            // 100 MHz
    reg rst_n = 0;
    reg frame_start = 0, cell_valid = 0, cell_det = 0, long_chirp = 1;
    reg [15:0] cell_i = 0, cell_q = 0, chirp_count = 16'd1234;
    reg [7:0] az = 8'd7, el = 8'd16;
    wire wr_en; wire [11:0] wr_addr; wire [7:0] wr_data; wire bank, frame_bank, frame_done; wire [11:0] frame_len; wire overflow;
    wire consumed;
    reg sclk = 0, mosi = 0, cs_n = 1; wire miso, drdy, active;
    // register model (command set v2): 4 x 32-bit words, combinational read as host_bridge_spi requires
    wire        reg_we; wire [15:0] reg_addr; wire [31:0] reg_wdata;
    reg  [31:0] regs [0:3];
    wire [31:0] reg_rdata = regs[reg_addr[1:0]];
    reg  [15:0] status_in = 16'h0000, frames_produced = 16'd0;
    integer wr_count = 0;
    always @(posedge clk) begin
        if (reg_we) begin regs[reg_addr[1:0]] <= reg_wdata; wr_count = wr_count + 1; end
        if (frame_done) frames_produced <= frames_produced + 16'd1;
    end
    always @(*) status_in = {15'd0, drdy};
    initial begin regs[0] = 32'h00000000; regs[1] = 32'h11111111; regs[2] = 32'h22222222; regs[3] = 32'h33333333; end

    rd_map_packer P (.clk(clk), .rst_n(rst_n), .frame_start(frame_start), .cell_valid(cell_valid), .cell_i(cell_i), .cell_q(cell_q),
        .cell_det(cell_det), .az_idx(az), .el_idx(el), .chirp_count(chirp_count), .long_chirp(long_chirp),
        .wr_en(wr_en), .wr_addr(wr_addr), .wr_data(wr_data), .bank(bank), .frame_bank(frame_bank), .frame_done(frame_done), .frame_len(frame_len), .overflow(overflow), .consumed(consumed));
    host_bridge_spi #(.RTL_VERSION(16'h0002)) B (.clk(clk), .rst_n(rst_n), .wr_en(wr_en), .wr_addr(wr_addr), .wr_data(wr_data), .wr_bank(bank), .frame_bank(frame_bank), .frame_done(frame_done), .frame_len(frame_len),
        .consumed(consumed),
        .reg_we(reg_we), .reg_addr(reg_addr), .reg_wdata(reg_wdata), .reg_rdata(reg_rdata), .status_in(status_in), .frames_produced(frames_produced),
        .sclk(sclk), .mosi(mosi), .miso(miso), .cs_n(cs_n), .drdy(drdy), .bridge_active(active));
    // behavioural SPI master, mode 0, 25 MHz
    task spi_byte(input [7:0] tx, output [7:0] rx); integer k; begin
        for (k = 7; k >= 0; k = k - 1) begin mosi = tx[k]; #20 sclk = 1; rx[k] = miso; #20 sclk = 0; end
    end endtask
    reg consumed_seen = 0; always @(posedge clk) if (consumed) consumed_seen <= 1;
    reg [7:0] rx; reg [7:0] frame [0:2400]; integer n, k, errors = 0; reg [15:0] crc; reg [7:0] expect_lm [0:2047];
    reg [7:0] rb [0:8]; reg [31:0] rv;
    function [7:0] ref_logmag(input [16:0] m); integer msb, j; reg [2:0] fr; begin
        msb = -1; for (j = 16; j >= 0; j = j - 1) if (msb < 0 && m[j]) msb = j;
        if (msb < 0) ref_logmag = 0; else begin
            if (msb >= 3) fr = (m >> (msb - 3)); else fr = m[2:0] << (3 - msb);
            ref_logmag = (msb << 3) | fr; end end endfunction
    function [15:0] crc_step(input [15:0] c, input [7:0] d); integer q; reg [15:0] x; begin
        x = c ^ {d, 8'h00}; for (q = 0; q < 8; q = q + 1) x = x[15] ? ((x << 1) ^ 16'h1021) : (x << 1); crc_step = x; end endfunction
    // command set v2 helpers (byte sequences as in beta/stm32/Core/Src/host_bridge_proto.c)
    task reg_write(input [15:0] addr, input [31:0] value); begin
        cs_n = 0; #40; spi_byte(8'h02, rb[0]); spi_byte(addr[7:0], rb[1]); spi_byte(addr[15:8], rb[2]);
        spi_byte(value[7:0], rb[3]); spi_byte(value[15:8], rb[4]); spi_byte(value[23:16], rb[5]); spi_byte(value[31:24], rb[6]); spi_byte(8'h00, rb[7]);
        #40 cs_n = 1; #200;
        if (rb[7] !== 8'hA2) begin $display("FAIL write 0x%04x: ack %h != A2", addr, rb[7]); errors = errors + 1; end
    end endtask
    task reg_read(input [15:0] addr, output [31:0] value); begin
        cs_n = 0; #40; spi_byte(8'h03, rb[0]); spi_byte(addr[7:0], rb[1]); spi_byte(addr[15:8], rb[2]);
        spi_byte(8'h00, rb[3]); spi_byte(8'h00, rb[4]); spi_byte(8'h00, rb[5]); spi_byte(8'h00, rb[6]);
        #40 cs_n = 1; #200; value = {rb[6], rb[5], rb[4], rb[3]};
    end endtask
    initial begin #6000000 $display("FAIL timeout: drdy=%b st=%0d cnt=%0d", drdy, P.st, P.cell_cnt); $finish; end
    initial begin
        #50 rst_n = 1; #50;
        // feed one beam position: 2048 cells with a deterministic pattern, detections at cells 100, 777, 2047
        @(posedge clk); frame_start <= 1; @(posedge clk); frame_start <= 0;
        for (n = 0; n < 2048; n = n + 1) begin
            @(posedge clk); cell_valid <= 1; cell_i <= (n * 37) & 16'h7FFF; cell_q <= -((n * 11) & 16'h3FFF);
            cell_det <= (n == 100 || n == 777 || n == 2047);   // scenario 1: 3 detections
            expect_lm[n] = ref_logmag(((n * 37) & 16'h7FFF) + ((n * 11) & 16'h3FFF));
        end
        @(posedge clk); cell_valid <= 0; cell_det <= 0;
        wait (drdy); #100;
        if (!drdy) begin $display("FAIL: drdy not set"); errors = errors + 1; end
        cs_n = 0; #40;
        spi_byte(8'h01, rx);
        for (n = 0; n < 16 + 2048 + 9 + 2; n = n + 1) begin spi_byte(8'h00, rx); frame[n] = rx; end
        #40 cs_n = 1; #200;
        if (0) $display("DBG frame[0..3]=%h %h %h %h  frame[16]=%h  B.ready=%b streaming=%b raddr=%0d bank=%b len=%0d", frame[0], frame[1], frame[2], frame[3], frame[16], B.ready, B.streaming, B.raddr, B.rd_bank_pending, B.len_pending);
        // checks
        if (frame[0] !== 8'hA5 || frame[1] !== 8'h5A) begin $display("FAIL sync %h %h", frame[0], frame[1]); errors = errors + 1; end
        if (frame[2] !== 1) begin $display("FAIL version"); errors = errors + 1; end
        if (frame[3] !== 8'h01) begin $display("FAIL flags %h", frame[3]); errors = errors + 1; end
        if (frame[6] !== 7 || frame[7] !== 16) begin $display("FAIL az/el"); errors = errors + 1; end
        if ({frame[9], frame[8]} !== 16'd1234) begin $display("FAIL chirp count"); errors = errors + 1; end
        if (frame[10] !== 64 || frame[11] !== 32) begin $display("FAIL dims"); errors = errors + 1; end
        if (frame[12] !== 3) begin $display("FAIL n_det %d", frame[12]); errors = errors + 1; end
        for (n = 0; n < 2048; n = n + 1) if (frame[16 + n] !== expect_lm[n]) begin if (errors < 5) $display("FAIL map[%0d] %h != %h", n, frame[16+n], expect_lm[n]); errors = errors + 1; end
        if (frame[2064] !== 100/32 || frame[2065] !== 100%32) begin $display("FAIL det0 index"); errors = errors + 1; end
        if (frame[2067] !== 777/32 || frame[2068] !== 777%32) begin $display("FAIL det1 index"); errors = errors + 1; end
        if (frame[2070] !== 2047/32 || frame[2071] !== 2047%32) begin $display("FAIL det2 index"); errors = errors + 1; end
        crc = 16'hFFFF; for (n = 0; n < 16 + 2048 + 9; n = n + 1) crc = crc_step(crc, frame[n]);
        if ({frame[2073], frame[2074]} !== crc) begin $display("FAIL crc %h != %h", {frame[2073], frame[2074]}, crc); errors = errors + 1; end
        #500; if (drdy) begin $display("FAIL drdy not cleared after read"); errors = errors + 1; end
        if (!consumed_seen) begin $display("FAIL consumed pulse missing"); errors = errors + 1; end
        // scenario 2: 40 flagged cells → n_det saturates at MAX_DET = 32, frame length 16+2048+96+2; regression for the det_wr width bug
        @(posedge clk); frame_start <= 1; @(posedge clk); frame_start <= 0;
        for (n = 0; n < 2048; n = n + 1) begin @(posedge clk); cell_valid <= 1; cell_i <= 16'd1000; cell_q <= 16'd0; cell_det <= (n % 50 == 0); end
        @(posedge clk); cell_valid <= 0; cell_det <= 0;
        begin : wait2 integer t; t = 0; while (!drdy && t < 20000) begin @(posedge clk); t = t + 1; end
            if (!drdy) begin $display("FAIL scenario 2: drdy never asserted (packer hang)"); errors = errors + 1; end end
        if (drdy) begin
            cs_n = 0; #40; spi_byte(8'h01, rx);
            for (n = 0; n < 16 + 2048 + 96 + 2; n = n + 1) begin spi_byte(8'h00, rx); frame[n] = rx; end
            #40 cs_n = 1; #200;
            if (frame[12] !== 32) begin $display("FAIL scenario 2: n_det %0d != 32", frame[12]); errors = errors + 1; end
            crc = 16'hFFFF; for (n = 0; n < 16 + 2048 + 96; n = n + 1) crc = crc_step(crc, frame[n]);
            if ({frame[2160], frame[2161]} !== crc) begin $display("FAIL scenario 2: crc"); errors = errors + 1; end
            if (frame[3] !== 8'h01) begin $display("FAIL scenario 2: overflow flag set unexpectedly %h", frame[3]); errors = errors + 1; end
        end
        // scenario 3: command set v2 register access + status + unknown command (no frame pending)
        #500;
        reg_read(16'h0002, rv); if (rv !== 32'h22222222) begin $display("FAIL v2 read reg2 %08x", rv); errors = errors + 1; end
        reg_write(16'h0001, 32'hCAFE0150);
        reg_write(16'h0003, 32'h00000007);
        reg_read(16'h0001, rv); if (rv !== 32'hCAFE0150) begin $display("FAIL v2 read-back reg1 %08x", rv); errors = errors + 1; end
        reg_read(16'h0003, rv); if (rv !== 32'h00000007) begin $display("FAIL v2 read-back reg3 %08x", rv); errors = errors + 1; end
        if (wr_count != 2) begin $display("FAIL v2 write count %0d != 2", wr_count); errors = errors + 1; end
        cs_n = 0; #40; spi_byte(8'h04, rb[0]); for (n = 1; n <= 8; n = n + 1) spi_byte(8'h00, rb[n]); #40 cs_n = 1; #200;
        if ({rb[2], rb[1]} !== 16'h0000 || {rb[4], rb[3]} !== 16'h0002 || {rb[6], rb[5]} !== 16'd2 || {rb[8], rb[7]} !== 16'h0000) begin
            $display("FAIL v2 status: word %02x%02x version %02x%02x frames %02x%02x resv %02x%02x", rb[2], rb[1], rb[4], rb[3], rb[6], rb[5], rb[8], rb[7]); errors = errors + 1; end
        cs_n = 0; #40; spi_byte(8'h7F, rb[0]); spi_byte(8'h00, rb[1]); spi_byte(8'h00, rb[2]); #40 cs_n = 1; #200;
        if (rb[1] !== 8'hEE || rb[2] !== 8'hEE) begin $display("FAIL v2 unknown command reply %h %h", rb[1], rb[2]); errors = errors + 1; end
        if (drdy) begin $display("FAIL v2: drdy set by register commands"); errors = errors + 1; end
        begin : dump integer fh; fh = $fopen("logs/tb_frame.hex", "w"); if (fh == 0) fh = $fopen("tb_frame.hex", "w");
            for (n = 0; n < 16 + 2048 + 9 + 2; n = n + 1) $fwrite(fh, "%02x", frame[n]); $fclose(fh); end
        if (errors == 0) $display("PASS tb_host_bridge: frame %0d bytes (3 det) and 2162 bytes (32 det), CRC ok; v2 write/read/status/unknown ok", 16 + 2048 + 9 + 2);
        else $display("FAIL tb_host_bridge: %0d errors", errors);
        $finish;
    end
endmodule
