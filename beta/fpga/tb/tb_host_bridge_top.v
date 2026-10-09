`timescale 1ns / 1ps
// ============================================================================
// tb_host_bridge_top.v - host-link option B through radar_system_top (BETA).
//
// Same clocks/stimulus as tb_system_smoke (synthetic IF echoes, 9 chirps so that one
// 64 x 32 Doppler frame completes). A behavioural SPI master (mode 0, MSB first,
// 25 MHz <= 27 MHz) on the shared SPI1 lines waits for spi_bridge_drdy, pulls
// spi_bridge_cs_n low, sends command 0x01 and reads one frame.
// Checks (reused from engineering/DESIGN/HOST_LINK/rtl/tb_host_bridge.v):
//   sync A5 5A, version 1, flags bit0 = long chirp, az/el = transmitter counters,
//   dims 64/32, n_det <= 32 and equal to the detections counted on the DUT outputs,
//   2048 map bytes = 8*log2(|I|+|Q|) of the Doppler cells captured from
//   dbg_doppler_data (range-major), detection entries (range, doppler, mag) match,
//   CRC-16/CCITT-FALSE over the frame, DRDY cleared after the read, consumed pulse.
//   Pass-through gating: during the read all four ADAR CS (1.8 V) stay high, SCLK/MOSI
//   1.8 V stay idle and stm32_miso_3v3 equals the bridge MISO; after the read a CS1
//   pass-through toggle reaches stm32_cs_adar1_1v8 and MISO follows stm32_miso_1v8.
// Command set v2 (HOST_LINK_DESIGN.md §7, byte sequences as in beta/stm32 host_bridge_proto.c):
//   before the chirps: 0x03 read of ID (0xF) = 0xBE7A and CFAR_THR (0x1) = 10000 (the DUT keeps
//   the default CFAR_THRESHOLD_DEFAULT); 0x02 write CFAR_THR = 150 (ack 0xA2 in byte 7), write
//   CAL_CTRL (0x4) = 0x18 (check enable + blind, levels), CAL_LANE (0x5) = 3, CAL_BLIND_COEF (0xD)
//   = 0x1234; 0x03 read-back of all four (upper 16 bits = 0); 0x04 status = {0x0000, version 2,
//   frames 0, 0}; unknown 0x7F -> 0xEE on every following byte; then the 9 chirps, 0x04 status
//   again (bit0 frame ready, frames 1), and the 0x01 frame read as before; because the threshold
//   now comes only from the register write, the frame must contain detections (n_det > 0).
// ============================================================================
module tb_host_bridge_top;
    localparam NUM_CHIRPS      = 9;
    localparam CHIRP_PERIOD_NS = 300_000;
    localparam real PI = 3.14159265358979323846;
    localparam N_CELLS = 2048;

    reg clk_100m = 0, clk_120m = 0, ft601_clk = 0, adc_dco_p = 0;
    wire adc_dco_n = ~adc_dco_p;
    always #5.0    clk_100m  = ~clk_100m;
    always #4.1667 clk_120m  = ~clk_120m;
    always #5.0    ft601_clk = ~ft601_clk;
    always #1.25   adc_dco_p = ~adc_dco_p;
    reg reset_n = 0;

    reg  [7:0] adc_d_p = 8'h80;
    wire [7:0] adc_d_n = ~adc_d_p;
    wire       adc_pwdn;
    wire [7:0] dac_data; wire dac_clk, dac_sleep, fpga_rf_switch, rx_mixer_en, tx_mixer_en;
    wire adar_tx_load_1, adar_rx_load_1, adar_tx_load_2, adar_rx_load_2;
    wire adar_tx_load_3, adar_rx_load_3, adar_tx_load_4, adar_rx_load_4;
    wire adar_tr_1, adar_tr_2, adar_tr_3, adar_tr_4;
    reg  stm32_sclk_3v3 = 0, stm32_mosi_3v3 = 0;
    reg  stm32_cs_adar1_3v3 = 1, stm32_cs_adar2_3v3 = 1, stm32_cs_adar3_3v3 = 1, stm32_cs_adar4_3v3 = 1;
    wire stm32_miso_3v3, stm32_sclk_1v8, stm32_mosi_1v8;
    reg  stm32_miso_1v8 = 0;
    wire stm32_cs_adar1_1v8, stm32_cs_adar2_1v8, stm32_cs_adar3_1v8, stm32_cs_adar4_1v8;
    reg  stm32_new_chirp = 0, stm32_new_elevation = 0, stm32_new_azimuth = 0, stm32_mixers_enable = 0;
    wire [31:0] ft601_data; wire [1:0] ft601_be;
    wire ft601_txe_n, ft601_rxf_n, ft601_wr_n, ft601_rd_n, ft601_oe_n, ft601_siwu_n, ft601_clk_out;
    reg  ft601_txe = 0, ft601_rxf = 1; reg [1:0] ft601_srb = 0, ft601_swb = 0;
    wire [5:0] current_elevation, current_azimuth, current_chirp; wire new_chirp_frame;
    wire [31:0] dbg_doppler_data; wire dbg_doppler_valid; wire [4:0] dbg_doppler_bin; wire [5:0] dbg_range_bin;
    wire [3:0] system_status;
    reg  spi_bridge_cs_n = 1; wire spi_bridge_drdy, spi_bridge_spare;

    // CFAR threshold left at its reset default (10000 = no detections); the test lowers it to 150
    // through the bridge write command so that the detection list is exercised
    radar_system_top dut (
        .clk_100m(clk_100m), .clk_120m_dac(clk_120m), .ft601_clk_in(ft601_clk), .reset_n(reset_n),
        .dac_data(dac_data), .dac_clk(dac_clk), .dac_sleep(dac_sleep), .fpga_rf_switch(fpga_rf_switch),
        .rx_mixer_en(rx_mixer_en), .tx_mixer_en(tx_mixer_en),
        .adar_tx_load_1(adar_tx_load_1), .adar_rx_load_1(adar_rx_load_1), .adar_tx_load_2(adar_tx_load_2), .adar_rx_load_2(adar_rx_load_2),
        .adar_tx_load_3(adar_tx_load_3), .adar_rx_load_3(adar_rx_load_3), .adar_tx_load_4(adar_tx_load_4), .adar_rx_load_4(adar_rx_load_4),
        .adar_tr_1(adar_tr_1), .adar_tr_2(adar_tr_2), .adar_tr_3(adar_tr_3), .adar_tr_4(adar_tr_4),
        .stm32_sclk_3v3(stm32_sclk_3v3), .stm32_mosi_3v3(stm32_mosi_3v3), .stm32_miso_3v3(stm32_miso_3v3),
        .stm32_cs_adar1_3v3(stm32_cs_adar1_3v3), .stm32_cs_adar2_3v3(stm32_cs_adar2_3v3),
        .stm32_cs_adar3_3v3(stm32_cs_adar3_3v3), .stm32_cs_adar4_3v3(stm32_cs_adar4_3v3),
        .stm32_sclk_1v8(stm32_sclk_1v8), .stm32_mosi_1v8(stm32_mosi_1v8), .stm32_miso_1v8(stm32_miso_1v8),
        .stm32_cs_adar1_1v8(stm32_cs_adar1_1v8), .stm32_cs_adar2_1v8(stm32_cs_adar2_1v8),
        .stm32_cs_adar3_1v8(stm32_cs_adar3_1v8), .stm32_cs_adar4_1v8(stm32_cs_adar4_1v8),
        .adc_d_p(adc_d_p), .adc_d_n(adc_d_n), .adc_dco_p(adc_dco_p), .adc_dco_n(adc_dco_n), .adc_pwdn(adc_pwdn),
        .stm32_new_chirp(stm32_new_chirp), .stm32_new_elevation(stm32_new_elevation),
        .stm32_new_azimuth(stm32_new_azimuth), .stm32_mixers_enable(stm32_mixers_enable),
        .spi_bridge_cs_n(spi_bridge_cs_n), .spi_bridge_drdy(spi_bridge_drdy), .spi_bridge_spare(spi_bridge_spare),
        .ft601_data(ft601_data), .ft601_be(ft601_be), .ft601_txe_n(ft601_txe_n), .ft601_rxf_n(ft601_rxf_n),
        .ft601_txe(ft601_txe), .ft601_rxf(ft601_rxf), .ft601_wr_n(ft601_wr_n), .ft601_rd_n(ft601_rd_n),
        .ft601_oe_n(ft601_oe_n), .ft601_siwu_n(ft601_siwu_n), .ft601_srb(ft601_srb), .ft601_swb(ft601_swb),
        .ft601_clk_out(ft601_clk_out),
        .current_elevation(current_elevation), .current_azimuth(current_azimuth), .current_chirp(current_chirp),
        .new_chirp_frame(new_chirp_frame), .dbg_doppler_data(dbg_doppler_data), .dbg_doppler_valid(dbg_doppler_valid),
        .dbg_doppler_bin(dbg_doppler_bin), .dbg_range_bin(dbg_range_bin), .system_status(system_status)
    );

    // ---------------- synthetic ADC echo (as in tb_system_smoke) ----------------
    integer chirp_idx = -1, adc_n = 0, echo_start = 0, v;
    real tau, phi, s;
    always @(posedge adc_dco_p) begin
        adc_n = adc_n + 1;
        v = 128 + ($random % 5);
        if (chirp_idx >= 0 && adc_n >= echo_start && adc_n < echo_start + 12000) begin
            tau = (adc_n - echo_start) / 4.0;
            phi = 2.0 * PI * (0.10 * tau + 0.5 * tau * tau / 15000.0);
            s   = 90.0 * $cos(2.0 * PI * 0.30 * (adc_n - echo_start) - phi);
            v   = v + $rtoi(s);
        end
        if (v < 0) v = 0; if (v > 255) v = 255;
        adc_d_p <= v[7:0];
    end

    // ---------------- capture the first Doppler frame from the DUT outputs ----------------
    reg [15:0] cap_i [0:N_CELLS-1];
    reg [15:0] cap_q [0:N_CELLS-1];
    reg        cap_det [0:N_CELLS-1];
    integer cap_n = 0, cap_det_n = 0, det_idx = 0, ii;
    initial for (ii = 0; ii < N_CELLS; ii = ii + 1) cap_det[ii] = 1'b0;
    always @(posedge clk_100m) begin
        if (dbg_doppler_valid && cap_n < N_CELLS) begin
            cap_i[cap_n] = dbg_doppler_data[15:0];
            cap_q[cap_n] = dbg_doppler_data[31:16];
            if (dbg_range_bin !== cap_n / 32 || dbg_doppler_bin !== cap_n % 32)
                $display("NOTE cell %0d arrives as range %0d doppler %0d", cap_n, dbg_range_bin, dbg_doppler_bin);
            cap_n = cap_n + 1;
        end
        // detection flag stream (one clock behind the data, same cell order): own index
        if (dut.rx_cfar_valid && det_idx < N_CELLS) begin
            cap_det[det_idx] = dut.rx_cfar_detection;
            if (dut.rx_cfar_detection) cap_det_n = cap_det_n + 1;
            det_idx = det_idx + 1;
        end
    end

    // ---------------- pass-through gating monitors ----------------
    integer gate_errors = 0, miso_mux_errors = 0;
    always @(posedge clk_100m) begin
        if (!spi_bridge_cs_n) begin
            if (!(stm32_cs_adar1_1v8 & stm32_cs_adar2_1v8 & stm32_cs_adar3_1v8 & stm32_cs_adar4_1v8) || stm32_sclk_1v8 || stm32_mosi_1v8)
                gate_errors = gate_errors + 1;
            if (stm32_miso_3v3 !== dut.bridge_miso) miso_mux_errors = miso_mux_errors + 1;
        end
    end

    // ---------------- behavioural SPI master, mode 0, 25 MHz ----------------
    task spi_byte(input [7:0] tx, output [7:0] rx);
        integer k;
        begin
            for (k = 7; k >= 0; k = k - 1) begin
                stm32_mosi_3v3 = tx[k]; #20 stm32_sclk_3v3 = 1; rx[k] = stm32_miso_3v3; #20 stm32_sclk_3v3 = 0;
            end
        end
    endtask

    function [7:0] ref_logmag(input [16:0] m);
        integer msb, j; reg [2:0] fr;
        begin
            msb = -1; for (j = 16; j >= 0; j = j - 1) if (msb < 0 && m[j]) msb = j;
            if (msb < 0) ref_logmag = 0;
            else begin
                if (msb >= 3) fr = (m >> (msb - 3)); else fr = m[2:0] << (3 - msb);
                ref_logmag = (msb << 3) | fr;
            end
        end
    endfunction
    function [15:0] crc_step(input [15:0] c, input [7:0] d);
        integer q; reg [15:0] x;
        begin x = c ^ {d, 8'h00}; for (q = 0; q < 8; q = q + 1) x = x[15] ? ((x << 1) ^ 16'h1021) : (x << 1); crc_step = x; end
    endfunction
    function [16:0] absmag(input [15:0] a, input [15:0] b);
        begin absmag = {1'b0, (a[15] ? -a : a)} + {1'b0, (b[15] ? -b : b)}; end
    endfunction

    reg consumed_seen = 0; always @(posedge clk_100m) if (dut.pk_consumed) consumed_seen <= 1;

    reg [7:0] rx; reg [7:0] frame [0:2400];
    integer n, k, errors = 0, n_det, flen, det_i, cidx;
    reg [15:0] crc; reg [7:0] lm;

    // ---------------- command set v2 helpers (byte layout = host_bridge_proto.c) ----------------
    reg [7:0] rb [0:8];
    task reg_write(input [15:0] addr, input [31:0] value);            // 02 a0 a1 d0 d1 d2 d3 00 -> rb[7] = 0xA2
        begin
            spi_bridge_cs_n = 0; #40;
            spi_byte(8'h02, rb[0]); spi_byte(addr[7:0], rb[1]); spi_byte(addr[15:8], rb[2]);
            spi_byte(value[7:0], rb[3]); spi_byte(value[15:8], rb[4]); spi_byte(value[23:16], rb[5]); spi_byte(value[31:24], rb[6]);
            spi_byte(8'h00, rb[7]);
            #40 spi_bridge_cs_n = 1; #200;
            if (rb[7] !== 8'hA2) begin $display("FAIL write 0x%04x: ack %h != A2", addr, rb[7]); errors = errors + 1; end
        end
    endtask
    task reg_read(input [15:0] addr, output [31:0] value);            // 03 a0 a1 xx xx xx xx -> rb[3..6]
        begin
            spi_bridge_cs_n = 0; #40;
            spi_byte(8'h03, rb[0]); spi_byte(addr[7:0], rb[1]); spi_byte(addr[15:8], rb[2]);
            spi_byte(8'h00, rb[3]); spi_byte(8'h00, rb[4]); spi_byte(8'h00, rb[5]); spi_byte(8'h00, rb[6]);
            #40 spi_bridge_cs_n = 1; #200;
            value = {rb[6], rb[5], rb[4], rb[3]};
        end
    endtask
    task reg_status(output [15:0] st, output [15:0] ver, output [15:0] frames, output [15:0] resv);   // 04 + 8 x 00
        begin
            spi_bridge_cs_n = 0; #40;
            spi_byte(8'h04, rb[0]); for (n = 1; n <= 8; n = n + 1) spi_byte(8'h00, rb[n]);
            #40 spi_bridge_cs_n = 1; #200;
            st = {rb[2], rb[1]}; ver = {rb[4], rb[3]}; frames = {rb[6], rb[5]}; resv = {rb[8], rb[7]};
        end
    endtask
    task expect_read(input [15:0] addr, input [31:0] exp, input [255:0] label);
        reg [31:0] v;
        begin
            reg_read(addr, v);
            if (v !== exp) begin $display("FAIL read 0x%04x (%0s): %08x != %08x", addr, label, v, exp); errors = errors + 1; end
            else $display("  read 0x%04x (%0s) = 0x%08x ok", addr, label, v);
        end
    endtask

    reg [31:0] rv; reg [15:0] st_w, st_ver, st_frames, st_resv;
    initial begin
        #200; reset_n = 1; #500; stm32_mixers_enable = 1; #2000;
        // ---- command set v2: register access before any frame exists ----
        expect_read(16'h000F, 32'h0000BE7A, "ID");
        expect_read(16'h0001, 32'd10000,    "CFAR_THR default");
        reg_write(16'h0001, 32'd150);                         // CFAR threshold -> detections appear in the frame
        reg_write(16'h0004, 32'h00000018);                    // CAL_CTRL: check enable + blind method (levels)
        reg_write(16'h0005, 32'h00000003);                    // CAL_LANE = 3
        reg_write(16'h000D, 32'hDEAD1234);                    // CAL_BLIND_COEF (upper 16 bits must be dropped)
        expect_read(16'h0001, 32'd150,        "CFAR_THR");
        expect_read(16'h0004, 32'h00000018,   "CAL_CTRL");
        expect_read(16'h0005, 32'h00000003,   "CAL_LANE");
        expect_read(16'h000D, 32'h00001234,   "CAL_BLIND_COEF");
        expect_read(16'h000E, 32'h00000040,   "MARGIN default");
        if (dut.ctl_cfar_threshold !== 16'd150 || dut.cal_blind !== 1'b1 || dut.cal_check_en !== 1'b1 || dut.cal_lane !== 3'd3) begin
            $display("FAIL register outputs: thr=%0d blind=%b chk=%b lane=%0d", dut.ctl_cfar_threshold, dut.cal_blind, dut.cal_check_en, dut.cal_lane); errors = errors + 1; end
        reg_write(16'h000D, 32'h0000EC39);                    // restore the default coefficient
        reg_write(16'h0004, 32'h00000000);                    // levels back to 0 (no toggles written)
        reg_status(st_w, st_ver, st_frames, st_resv);
        $display("  status before frames: word %04x version %04x frames %0d reserved %04x", st_w, st_ver, st_frames, st_resv);
        if (st_w !== 16'h0000 || st_ver !== 16'h0002 || st_frames !== 16'd0 || st_resv !== 16'h0000) begin
            $display("FAIL status before frames"); errors = errors + 1; end
        // unknown command: 0xEE on every following byte, frame RAM untouched, DRDY unaffected
        spi_bridge_cs_n = 0; #40; spi_byte(8'h7F, rb[0]); spi_byte(8'h00, rb[1]); spi_byte(8'h00, rb[2]); spi_byte(8'h00, rb[3]); #40 spi_bridge_cs_n = 1; #200;
        if (rb[1] !== 8'hEE || rb[2] !== 8'hEE || rb[3] !== 8'hEE) begin $display("FAIL unknown command reply %h %h %h", rb[1], rb[2], rb[3]); errors = errors + 1; end
        // 0x01 without a frame: zeros, no sync word
        spi_bridge_cs_n = 0; #40; spi_byte(8'h01, rb[0]); spi_byte(8'h00, rb[1]); spi_byte(8'h00, rb[2]); #40 spi_bridge_cs_n = 1; #200;
        if (rb[1] !== 8'h00 || rb[2] !== 8'h00) begin $display("FAIL 0x01 without frame returned %h %h", rb[1], rb[2]); errors = errors + 1; end
        if (spi_bridge_drdy) begin $display("FAIL DRDY set before any frame"); errors = errors + 1; end
        if (gate_errors != 0) begin $display("FAIL ADAR pass-through not gated during register commands (%0d samples)", gate_errors); errors = errors + 1; end
        $display("register commands done: %0d error(s)", errors);
        #2000;
        for (k = 0; k < NUM_CHIRPS; k = k + 1) begin
            @(posedge clk_100m);
            chirp_idx = k; adc_n = 0; echo_start = 100 * 4;
            stm32_new_chirp = ~stm32_new_chirp;
            if (k % 4 == 0) stm32_new_elevation = ~stm32_new_elevation;
            if (k % 8 == 0) stm32_new_azimuth = ~stm32_new_azimuth;
            #CHIRP_PERIOD_NS;
        end
        begin : stats
            integer mx, c1, c2, c3;
            mx = 0; c1 = 0; c2 = 0; c3 = 0;
            for (n = 0; n < N_CELLS; n = n + 1) begin
                if (absmag(cap_i[n], cap_q[n]) > mx) mx = absmag(cap_i[n], cap_q[n]);
                if (absmag(cap_i[n], cap_q[n]) > 50) c1 = c1 + 1;
                if (absmag(cap_i[n], cap_q[n]) > 150) c2 = c2 + 1;
                if (absmag(cap_i[n], cap_q[n]) > 500) c3 = c3 + 1;
            end
            $display("Doppler cell |I|+|Q|: max %0d, >50: %0d, >150: %0d, >500: %0d", mx, c1, c2, c3);
        end
        if (!spi_bridge_drdy) begin
            $display("FAIL: DRDY not asserted after %0d chirps (Doppler cells captured: %0d)", NUM_CHIRPS, cap_n); $fatal(1);
        end
        $display("DRDY high; %0d Doppler cells captured, %0d detections; az=%0d el=%0d", cap_n, cap_det_n, current_azimuth, current_elevation);
        #1000;
        // ---- status with a frame pending ----
        reg_status(st_w, st_ver, st_frames, st_resv);
        $display("  status with frame pending: word %04x version %04x frames %0d reserved %04x", st_w, st_ver, st_frames, st_resv);
        if (st_w !== 16'h0001 || st_ver !== 16'h0002 || st_frames !== 16'd1 || st_resv !== 16'h0000) begin
            $display("FAIL status with frame pending (expected word 0001 = frame ready, frames 1)"); errors = errors + 1; end
        if (spi_bridge_drdy !== 1'b1) begin $display("FAIL status command cleared DRDY"); errors = errors + 1; end
        if (cap_det_n == 0) begin $display("FAIL no detections although CFAR_THR was written to 150"); errors = errors + 1; end
        // ---- read one frame ----
        spi_bridge_cs_n = 0; #40;
        spi_byte(8'h01, rx);
        for (n = 0; n < 16; n = n + 1) begin spi_byte(8'h00, rx); frame[n] = rx; end
        n_det = frame[12];
        flen = 16 + N_CELLS + 3 * n_det;
        for (n = 16; n < flen + 2; n = n + 1) begin spi_byte(8'h00, rx); frame[n] = rx; end
        #40 spi_bridge_cs_n = 1; #500;

        // ---- checks ----
        if (frame[0] !== 8'hA5 || frame[1] !== 8'h5A) begin $display("FAIL sync %h %h", frame[0], frame[1]); errors = errors + 1; end
        if (frame[2] !== 8'd1) begin $display("FAIL version %0d", frame[2]); errors = errors + 1; end
        if (frame[3] !== 8'h01) begin $display("FAIL flags %h (expected long_chirp=1, overflow=0)", frame[3]); errors = errors + 1; end
        if (frame[6] !== {2'b00, current_azimuth} || frame[7] !== {2'b00, current_elevation}) begin
            $display("FAIL az/el %0d/%0d != %0d/%0d", frame[6], frame[7], current_azimuth, current_elevation); errors = errors + 1; end
        if ({frame[9], frame[8]} !== dut.chirp_count) begin $display("FAIL chirp count %0d != %0d", {frame[9], frame[8]}, dut.chirp_count); errors = errors + 1; end
        if (frame[10] !== 8'd64 || frame[11] !== 8'd32) begin $display("FAIL dims %0d x %0d", frame[10], frame[11]); errors = errors + 1; end
        if (n_det > 32 || frame[13] !== 8'd0) begin $display("FAIL n_det field %0d/%0d", frame[12], frame[13]); errors = errors + 1; end
        if (n_det !== ((cap_det_n > 32) ? 32 : cap_det_n)) begin $display("FAIL n_det %0d != %0d detections seen", n_det, cap_det_n); errors = errors + 1; end
        for (n = 0; n < N_CELLS; n = n + 1) begin
            lm = ref_logmag(absmag(cap_i[n], cap_q[n]));
            if (frame[16 + n] !== lm) begin if (errors < 8) $display("FAIL map[%0d] %h != %h", n, frame[16 + n], lm); errors = errors + 1; end
        end
        det_i = 0;
        for (cidx = 0; cidx < N_CELLS && det_i < n_det; cidx = cidx + 1) begin
            if (cap_det[cidx]) begin
                if (frame[16 + N_CELLS + 3*det_i] !== cidx / 32 || frame[16 + N_CELLS + 3*det_i + 1] !== cidx % 32 ||
                    frame[16 + N_CELLS + 3*det_i + 2] !== ref_logmag(absmag(cap_i[cidx], cap_q[cidx]))) begin
                    if (errors < 12) $display("FAIL det[%0d] = (%0d,%0d,%h) expected cell %0d", det_i,
                        frame[16 + N_CELLS + 3*det_i], frame[16 + N_CELLS + 3*det_i + 1], frame[16 + N_CELLS + 3*det_i + 2], cidx);
                    errors = errors + 1;
                end
                det_i = det_i + 1;
            end
        end
        crc = 16'hFFFF; for (n = 0; n < flen; n = n + 1) crc = crc_step(crc, frame[n]);
        if ({frame[flen], frame[flen + 1]} !== crc) begin $display("FAIL crc %h != %h", {frame[flen], frame[flen + 1]}, crc); errors = errors + 1; end
        if (spi_bridge_drdy) begin $display("FAIL drdy not cleared after read"); errors = errors + 1; end
        if (!consumed_seen) begin $display("FAIL consumed pulse missing"); errors = errors + 1; end
        if (spi_bridge_spare) begin $display("FAIL overflow/spare flag set"); errors = errors + 1; end
        if (gate_errors != 0) begin $display("FAIL ADAR pass-through not gated during the bridge transfer (%0d samples)", gate_errors); errors = errors + 1; end
        if (miso_mux_errors != 0) begin $display("FAIL MISO mux (%0d samples)", miso_mux_errors); errors = errors + 1; end

        // ---- pass-through still works after the transfer ----
        stm32_cs_adar1_3v3 = 0; stm32_miso_1v8 = 1; #60;
        if (stm32_cs_adar1_1v8 !== 1'b0) begin $display("FAIL CS1 pass-through after bridge transfer"); errors = errors + 1; end
        if (stm32_miso_3v3 !== 1'b1) begin $display("FAIL MISO pass-through after bridge transfer"); errors = errors + 1; end
        stm32_cs_adar1_3v3 = 1; stm32_miso_1v8 = 0; #60;

        // ---- status after the read: frame consumed, counter unchanged ----
        reg_status(st_w, st_ver, st_frames, st_resv);
        if (st_w !== 16'h0000 || st_frames !== 16'd1) begin $display("FAIL status after read: word %04x frames %0d", st_w, st_frames); errors = errors + 1; end
        expect_read(16'h0001, 32'd150, "CFAR_THR after frame");

        if (errors == 0) begin
            $display("PASS tb_host_bridge_top: v2 register write/read/status/unknown ok (CFAR_THR 10000->150 via 0x02, 5 read-backs, status 0000/0001, 0xEE), frame %0d bytes read over SPI1 (%0d detections), sync/dims/az-el/chirp-count/map/CRC ok, ADAR pass-through gated during the transfer",
                     flen + 2, n_det);
            $finish;
        end else begin
            $display("FAIL tb_host_bridge_top: %0d check(s) failed", errors);
            $fatal(1);
        end
    end
endmodule
