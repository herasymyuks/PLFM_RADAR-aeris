`timescale 1ns / 1ps
// ============================================================================
// tb_system_smoke.v - full-system smoke test of radar_system_top (beta).
//
// Clocks: clk_100m 100 MHz, clk_120m_dac 120 MHz, ADC DCO 400 MHz (behavioural
// capture, `define SIM). ft601_clk_in is driven but unused by the DUT.
//
// Stimulus
//   * reset, mixers_enable = 1, NUM_CHIRPS STM32 "new chirp" toggles every
//     CHIRP_PERIOD_NS; elevation/azimuth toggles every 4/8 chirps.
//   * Synthetic ADC data (offset binary, 8 bit): noise floor plus, for each
//     chirp, an IF echo  s[n] = A cos(2*pi*0.30*n - phi_u(n/4))  starting
//     ECHO_DELAY(k) baseband samples after the toggle, where phi_u is the
//     phase of the 10->30 MHz reference up-chirp (gen_chirp_mem.py). Mixing
//     with the 120 MHz NCO (0.30 cycles/sample at 400 MSPS) yields the
//     baseband up-chirp u[n] that the stored reference matches.
//
// Checks (all must hold -> "PASS", otherwise "FAIL" + $fatal)
//   1. DAC produces non-mid-scale samples after the first chirp toggle.
//   2. The receiver emits decimated range profiles (64 bins) for every segment.
//   3. For chirps 1 and 2 the peak of segment-0's range profile moves by
//      (ECHO_DELAY(2) - ECHO_DELAY(1)) / 16 bins (+/-1 decimated bin) - end-to-end pulse
//      compression through capture -> DDC -> matched filter -> decimator.
//   4. The Doppler processor produces 64 x 32 = 2048 valid outputs per frame.
//   5. USB packets: 11 words, W0[31:24] = 0xAA, W10[7:0] = 0x55, sequence
//      numbers consecutive, at least MIN_PACKETS packets.
//   6. No X/Z on the DUT outputs after reset.
//   7. The matched-filter FSM is idle at every chirp toggle (otherwise the chirp is
//      missed - the chain is not pipelined; see README "Known limitations").
// Runtime: ~3.3 ms simulated (about 2 minutes with Icarus).
// ============================================================================
module tb_system_smoke #(
    parameter ADC_MODE = 1          // radar_system_top ADC_CAPTURE_MODE (build.sh runs 1 and 0)
);
    localparam NUM_CHIRPS      = 10;
    localparam CHIRP_PERIOD_NS = 300_000;   // > matched-filter processing time per chirp (see README: not real-time)
    localparam MIN_PACKETS     = 100;
    localparam real PI = 3.14159265358979323846;

    // ---------------- clocks / reset ----------------
    reg clk_100m = 0, clk_120m = 0, ft601_clk = 0, adc_dco_p = 0;
    wire adc_dco_n = ~adc_dco_p;
    always #5.0     clk_100m  = ~clk_100m;
    always #4.1667  clk_120m  = ~clk_120m;
    always #5.0     ft601_clk = ~ft601_clk;
    always #1.25    adc_dco_p = ~adc_dco_p;
    reg reset_n = 0;

    // ---------------- DUT I/O ----------------
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

    radar_system_top #(.ADC_CAPTURE_MODE(ADC_MODE)) dut (
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
        .ft601_data(ft601_data), .ft601_be(ft601_be), .ft601_txe_n(ft601_txe_n), .ft601_rxf_n(ft601_rxf_n),
        .ft601_txe(ft601_txe), .ft601_rxf(ft601_rxf), .ft601_wr_n(ft601_wr_n), .ft601_rd_n(ft601_rd_n),
        .ft601_oe_n(ft601_oe_n), .ft601_siwu_n(ft601_siwu_n), .ft601_srb(ft601_srb), .ft601_swb(ft601_swb),
        .ft601_clk_out(ft601_clk_out),
        .current_elevation(current_elevation), .current_azimuth(current_azimuth), .current_chirp(current_chirp),
        .new_chirp_frame(new_chirp_frame), .dbg_doppler_data(dbg_doppler_data), .dbg_doppler_valid(dbg_doppler_valid),
        .dbg_doppler_bin(dbg_doppler_bin), .dbg_range_bin(dbg_range_bin), .system_status(system_status)
    );

    // ---------------- synthetic ADC echo ----------------
    // echo_active / echo_n: baseband sample index (at 100 MSPS) of the current echo
    integer echo_delay [0:NUM_CHIRPS-1];
    integer chirp_idx = -1;
    integer adc_n = 0;          // ADC samples since the current toggle
    integer echo_start = 0;     // ADC sample index at which the echo begins
    real    tau, phi, s;
    integer v;
    always @(posedge adc_dco_p) begin
        adc_n = adc_n + 1;
        v = 128 + ($random % 5);                       // noise floor
        if (chirp_idx >= 0 && adc_n >= echo_start && adc_n < echo_start + 12000) begin
            tau = (adc_n - echo_start) / 4.0;          // baseband sample index
            phi = 2.0 * PI * (0.10 * tau + 0.5 * tau * tau / 15000.0);
            s   = 90.0 * $cos(2.0 * PI * 0.30 * (adc_n - echo_start) - phi);
            v   = v + $rtoi(s);
        end
        if (v < 0) v = 0; if (v > 255) v = 255;
        adc_d_p <= v[7:0];
    end

    // ---------------- monitors ----------------
    integer dac_active = 0;
    always @(posedge dac_clk) if (dac_data != 8'h80) dac_active = dac_active + 1;

    integer rp_count = 0, rp_seg0_count = 0;
    integer seg0_peak_bin [0:NUM_CHIRPS-1];
    integer seg0_peak_mag, seg0_bins;
    integer rp_chirp = -1;
    function integer absval; input [15:0] x; begin absval = x[15] ? {16'd0, (~x) + 16'd1} : {16'd0, x}; end endfunction
    integer m;
    always @(posedge clk_100m) begin
        if (dut.rx_inst.range_profile_valid) begin
            rp_count = rp_count + 1;
            // segment 0 of each chirp = the first 64 profile bins after the toggle
            if (rp_chirp == chirp_idx && seg0_bins < 64) begin
                m = absval(dut.rx_inst.range_profile_out[15:0]) + absval(dut.rx_inst.range_profile_out[31:16]);
                if (m > seg0_peak_mag) begin seg0_peak_mag = m; seg0_peak_bin[chirp_idx] = dut.rx_inst.range_profile_bin; end
                seg0_bins = seg0_bins + 1;
                if (seg0_bins == 64) rp_seg0_count = rp_seg0_count + 1;
            end
        end
    end

    integer dop_count = 0, frames = 0;
    always @(posedge clk_100m) begin
        if (dbg_doppler_valid) dop_count = dop_count + 1;
        if (dut.rx_inst.doppler_proc.frame_buffer_full && dut.rx_inst.doppler_proc.state == 3'b010 && dut.rx_inst.doppler_proc.read_range_bin == 0 && dut.rx_inst.doppler_proc.fft_sample_counter == 0) frames = frames + 1;
    end

    // USB packet checker (clk domain, strobe = ft601_wr_n low)
    integer pkt_words = 0, packets = 0, pkt_errors = 0, last_seq = -1;
    reg [31:0] w0;
    always @(posedge clk_100m) begin
        if (!ft601_wr_n) begin
            if (pkt_words == 0) begin
                w0 = ft601_data;
                if (w0[31:24] !== 8'hAA) begin pkt_errors = pkt_errors + 1; if (pkt_errors < 5) $display("FAIL packet header %h", w0); end
                if (last_seq >= 0 && w0[7:0] !== ((last_seq + 1) & 8'hFF)) begin pkt_errors = pkt_errors + 1; if (pkt_errors < 5) $display("FAIL sequence %0d after %0d", w0[7:0], last_seq); end
                last_seq = w0[7:0];
            end
            if (pkt_words == 10) begin
                if (ft601_data[7:0] !== 8'h55) begin pkt_errors = pkt_errors + 1; if (pkt_errors < 5) $display("FAIL packet footer %h", ft601_data); end
                packets = packets + 1;
            end
            pkt_words = (pkt_words == 10) ? 0 : pkt_words + 1;
        end
    end

    integer x_errors = 0;
    always @(posedge clk_100m) begin
        if (reset_n && $time > 2000) begin
            if (^{dac_data, fpga_rf_switch, rx_mixer_en, tx_mixer_en, adc_pwdn, system_status, dbg_doppler_valid,
                  current_chirp, stm32_sclk_1v8, stm32_cs_adar1_1v8, ft601_wr_n} === 1'bx) x_errors = x_errors + 1;
        end
    end

    // ---------------- stimulus ----------------
    integer k, errors = 0, expected_diff, got_diff, missed = 0;
    initial begin
        for (k = 0; k < NUM_CHIRPS; k = k + 1) echo_delay[k] = 100 + 320 * (k % 2);   // 100 / 420 baseband samples
        #200; reset_n = 1;
        #500; stm32_mixers_enable = 1;
        #2000;
        for (k = 0; k < NUM_CHIRPS; k = k + 1) begin
            @(posedge clk_100m);
            if (dut.rx_inst.mf_dual.state != 0) begin
                missed = missed + 1;
                $display("matched filter busy (state %0d) at chirp %0d toggle - chirp will be missed", dut.rx_inst.mf_dual.state, k);
            end
            chirp_idx = k; adc_n = 0; echo_start = echo_delay[k] * 4;
            rp_chirp = k; seg0_bins = 0; seg0_peak_mag = 0; seg0_peak_bin[k] = -1;
            stm32_new_chirp = ~stm32_new_chirp;
            if (k % 4 == 0) stm32_new_elevation = ~stm32_new_elevation;
            if (k % 8 == 0) stm32_new_azimuth = ~stm32_new_azimuth;
            #CHIRP_PERIOD_NS;
        end
        #300_000;

        $display("DAC active samples      : %0d", dac_active);
        $display("range-profile bins      : %0d (segment-0 profiles: %0d)", rp_count, rp_seg0_count);
        for (k = 0; k < NUM_CHIRPS; k = k + 1) $display("  chirp %0d: echo delay %0d samples -> seg0 peak bin %0d", k, echo_delay[k], seg0_peak_bin[k]);
        $display("Doppler valid outputs   : %0d (frames started: %0d)", dop_count, frames);
        $display("USB packets             : %0d (%0d header/footer/sequence errors)", packets, pkt_errors);
        $display("X on outputs            : %0d", x_errors);
        $display("chirps missed (MF busy) : %0d", missed);

        if (dac_active == 0) begin errors = errors + 1; $display("FAIL: DAC never left mid-scale"); end
        if (rp_seg0_count < NUM_CHIRPS) begin errors = errors + 1; $display("FAIL: only %0d segment-0 profiles", rp_seg0_count); end
        expected_diff = (echo_delay[1] - echo_delay[0]) / 16;
        got_diff = seg0_peak_bin[1] - seg0_peak_bin[0];
        if (got_diff < expected_diff - 1 || got_diff > expected_diff + 1) begin
            errors = errors + 1; $display("FAIL: peak bin shift %0d, expected %0d", got_diff, expected_diff);
        end
        if (seg0_peak_bin[2] != seg0_peak_bin[0] || seg0_peak_bin[3] != seg0_peak_bin[1]) begin
            errors = errors + 1; $display("FAIL: peak bins not repeatable between chirps with equal delay");
        end
        if (dop_count < 2048) begin errors = errors + 1; $display("FAIL: %0d Doppler outputs (< 2048)", dop_count); end
        if (packets < MIN_PACKETS || pkt_errors != 0) begin errors = errors + 1; $display("FAIL: USB packets"); end
        if (x_errors != 0) begin errors = errors + 1; $display("FAIL: X on outputs"); end
        if (missed != 0) begin errors = errors + 1; $display("FAIL: %0d chirp toggles arrived while the matched filter was busy", missed); end

        if (errors == 0) begin
            $display("PASS tb_system_smoke (ADC_CAPTURE_MODE=%0d): %0d chirps, %0d range profiles, peak shift %0d bins for a 320-sample delay change, %0d Doppler outputs, %0d USB packets",
                     ADC_MODE, NUM_CHIRPS, rp_count / 64, got_diff, dop_count, packets);
            $finish;
        end else begin
            $display("FAIL tb_system_smoke: %0d check(s) failed", errors);
            $fatal(1);
        end
    end
endmodule
