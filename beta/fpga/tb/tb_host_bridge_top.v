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

    // CFAR threshold lowered so that the detection list is exercised (default 10000 gives none)
    radar_system_top #(.CFAR_THRESHOLD_DEFAULT(16'd150)) dut (
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
    initial begin
        #200; reset_n = 1; #500; stm32_mixers_enable = 1; #2000;
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

        if (errors == 0) begin
            $display("PASS tb_host_bridge_top: frame %0d bytes read over SPI1 (%0d detections), sync/dims/az-el/chirp-count/map/CRC ok, ADAR pass-through gated during the transfer",
                     flen + 2, n_det);
            $finish;
        end else begin
            $display("FAIL tb_host_bridge_top: %0d check(s) failed", errors);
            $fatal(1);
        end
    end
endmodule
