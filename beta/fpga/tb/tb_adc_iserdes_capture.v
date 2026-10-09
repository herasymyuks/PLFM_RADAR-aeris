`timescale 1ns / 1ps
// tb_adc_iserdes_capture.v - ad9484_iserdes_capture + adc_capture_calib + clk_gen (SIM model).
// A 400 MHz source drives the 8 LVDS pairs edge-aligned with the DCO (+0.25 ns = tPD - tCPD
// typ.); lane 5 has an extra +0.6 ns skew. Sequence:
//   1. ADC in "user pattern toggle" mode (0xAA / 0x55): auto calibration must lock all 8 lanes,
//      lanes 0-4,6,7 get equal centre taps (+/-1), lane 5 about 8 taps less (0.6 ns / 78 ps);
//      the pattern-check error counter stays 0 at the calibrated taps.
//   2. One BITSLIP on lane 0 breaks the pattern (error counter counts), three more restore it.
//   3. Manual tap load is reflected in CNTVALUEOUT; auto calibration restores the centres.
//   4. Normal data (sine + ramp): the 32-bit words read from the clk_100m FIFO reproduce the
//      source sample sequence exactly for 4000 samples (s0 oldest), with clk_100m deliberately
//      phase-shifted against DCO/4.
module tb_adc_iserdes_capture;
    localparam real PI = 3.14159265358979323846;
    reg clk_100m = 0, reset_n = 0, adc_dco_p = 0;
    always #1.25 adc_dco_p = ~adc_dco_p;
    initial begin #1.3 forever #5.0 clk_100m = ~clk_100m; end     // 100 MHz, 1.3 ns offset vs DCO/4
    wire adc_dco_n = ~adc_dco_p;

    // ---------------- source ----------------
    reg       pattern_mode = 1;
    reg [7:0] sample = 8'hAA, bus = 8'h00;
    reg [7:0] src [0:65535];
    integer   src_n = 0;
    integer   v;
    always @(posedge adc_dco_p) begin
        if (pattern_mode) sample = (sample == 8'hAA) ? 8'h55 : 8'hAA;
        else begin
            v = 128 + $rtoi(90.0 * $sin(2.0 * PI * 0.0731 * src_n)) + (src_n % 7);
            if (v < 0) v = 0; if (v > 255) v = 255;
            sample = v[7:0];
        end
        if (!pattern_mode && src_n < 65536) begin src[src_n] = sample; src_n = src_n + 1; end
        bus = sample;
    end
    // lane delays: tPD - tCPD = 0.25 ns typical, lane 5 skewed by +0.6 ns
    wire [7:0] adc_d_p;
    assign #0.25 adc_d_p[0] = bus[0]; assign #0.25 adc_d_p[1] = bus[1]; assign #0.25 adc_d_p[2] = bus[2];
    assign #0.25 adc_d_p[3] = bus[3]; assign #0.25 adc_d_p[4] = bus[4]; assign #0.85 adc_d_p[5] = bus[5];
    assign #0.25 adc_d_p[6] = bus[6]; assign #0.25 adc_d_p[7] = bus[7];
    wire [7:0] adc_d_n = ~adc_d_p;

    // ---------------- DUT ----------------
    wire clk_200m_ref, ref_locked, idelay_rdy, clk_div, rst_n_div;
    wire [7:0]  tap_ld, bitslip;
    wire [39:0] tap_val, tap_cur;
    wire [31:0] word_div, word;
    wire        word_div_valid, word_valid, fifo_ovf;
    reg  auto_t = 0, man_t = 0, slip_t = 0, check_en = 0;
    reg  [2:0] lane = 0; reg [4:0] mtap = 0; reg [1:0] nslip = 0;
    wire cal_busy, cal_done, align_fail; wire [7:0] lock, undet; wire [4:0] lane_tap, win_lo, win_hi; wire [15:0] err;

    clk_gen u_clk (.clk_100m(clk_100m), .reset_n(reset_n), .clk_200m_ref(clk_200m_ref), .locked(ref_locked));
    ad9484_iserdes_capture #(.DIFF_TERM("FALSE"), .Q1_IS_OLDEST(1)) cap (
        .adc_d_p(adc_d_p), .adc_d_n(adc_d_n), .adc_dco_p(adc_dco_p), .adc_dco_n(adc_dco_n),
        .reset_n(reset_n), .clk_200m_ref(clk_200m_ref), .ref_locked(ref_locked), .idelay_rdy(idelay_rdy),
        .clk_div(clk_div), .rst_n_div(rst_n_div), .tap_ld(tap_ld), .tap_val(tap_val), .bitslip(bitslip), .tap_cur(tap_cur),
        .word_div(word_div), .word_div_valid(word_div_valid),
        .clk_100m(clk_100m), .rst_n_100m(reset_n), .word(word), .word_valid(word_valid), .fifo_overflow(fifo_ovf));
    adc_capture_calib #(.DEFAULT_TAP(5'd16), .SETTLE(16), .MEAS(64), .MIN_WINDOW(4)) cal (
        .clk(clk_div), .rst_n(rst_n_div), .idelay_rdy(idelay_rdy), .word(word_div), .word_valid(word_div_valid),
        .ctrl_auto_start_t(auto_t), .ctrl_manual_load_t(man_t), .ctrl_bitslip_load_t(slip_t), .ctrl_check_en(check_en),
        .ctrl_lane(lane), .ctrl_tap(mtap), .ctrl_bitslip(nslip), .pattern_a(8'hAA), .pattern_b(8'h55),
        .tap_ld(tap_ld), .tap_val(tap_val), .bitslip(bitslip),
        .cal_busy(cal_busy), .cal_done(cal_done), .lock(lock), .undetermined(undet), .align_fail(align_fail),
        .lane_tap(lane_tap), .lane_win_lo(win_lo), .lane_win_hi(win_hi), .err_count(err));

    // ---------------- word capture (clk_100m) ----------------
    reg [31:0] got [0:16383];
    integer ng = 0;
    always @(posedge clk_100m) if (word_valid && ng < 16384) begin got[ng] = word; ng = ng + 1; end

    task wait_cal;
        begin @(posedge cal_busy); @(negedge cal_busy); #200; end
    endtask

    integer taps [0:7];
    integer l, errors = 0, i, k, lag, found, mism, e0, e1, e2, dtap, ref_tap;
    initial begin
        #200 reset_n = 1;
        wait (idelay_rdy); #2000;
        // ---- 1. auto calibration on the toggle pattern ----
        check_en = 1; #200;
        auto_t = ~auto_t; wait_cal;
        for (l = 0; l < 8; l = l + 1) begin lane = l; #50; taps[l] = lane_tap;
            $display("lane %0d: lock=%b undetermined=%b tap=%0d window %0d..%0d", l, lock[l], undet[l], lane_tap, win_lo, win_hi); end
        if (lock !== 8'hFF) begin errors = errors + 1; $display("FAIL: lock = %b", lock); end
        if (undet !== 8'h00) begin errors = errors + 1; $display("FAIL: undetermined = %b", undet); end
        if (align_fail) begin errors = errors + 1; $display("FAIL: lane alignment failed"); end
        ref_tap = taps[0];
        for (l = 1; l < 8; l = l + 1) if (l != 5) begin
            dtap = taps[l] - ref_tap; if (dtap > 16) dtap = dtap - 32; if (dtap < -16) dtap = dtap + 32;
            if (dtap > 1 || dtap < -1) begin errors = errors + 1; $display("FAIL: lane %0d tap %0d differs from lane 0 (%0d)", l, taps[l], ref_tap); end
        end
        dtap = ref_tap - taps[5]; if (dtap > 16) dtap = dtap - 32; if (dtap < -16) dtap = dtap + 32;
        if (dtap < 6 || dtap > 10) begin errors = errors + 1; $display("FAIL: skewed lane 5 tap %0d vs %0d (expected ~8 taps less)", taps[5], ref_tap); end
        // error counter at the calibrated taps
        check_en = 0; #100; check_en = 1; #20000; e0 = err;
        if (e0 != 0) begin errors = errors + 1; $display("FAIL: %0d pattern errors at the calibrated taps", e0); end
        // ---- 2. bitslip: 1 slip on lane 0 breaks the pattern, 3 more restore it ----
        lane = 0; nslip = 1; #50; slip_t = ~slip_t; #5000; check_en = 0; #100; check_en = 1; #20000; e1 = err;
        if (e1 == 0) begin errors = errors + 1; $display("FAIL: one bitslip on lane 0 did not break the pattern"); end
        nslip = 3; #50; slip_t = ~slip_t; #5000; check_en = 0; #100; check_en = 1; #20000; e2 = err;
        if (e2 != 0) begin errors = errors + 1; $display("FAIL: %0d errors after 4 bitslips (should realign)", e2); end
        $display("bitslip test: errors %0d (cal) / %0d (1 slip) / %0d (4 slips)", e0, e1, e2);
        // ---- 3. manual tap load + re-calibration ----
        lane = 2; mtap = 5'd3; #50; man_t = ~man_t; #500;
        if (tap_cur[5*2 +: 5] !== 5'd3) begin errors = errors + 1; $display("FAIL: manual tap not applied (CNTVALUEOUT = %0d)", tap_cur[5*2 +: 5]); end
        auto_t = ~auto_t; wait_cal;
        lane = 2; #50;
        if (lane_tap != taps[2]) begin errors = errors + 1; $display("FAIL: re-calibration gave tap %0d (was %0d)", lane_tap, taps[2]); end
        check_en = 0;
        // ---- 4. normal data through the FIFO ----
        #1000; src_n = 0; pattern_mode = 0;
        #2000; ng = 0;                      // let the pattern words drain from the pipeline/FIFO first
        #(4100 * 2.5 + 2000);
        $display("normal data: %0d source samples, %0d words captured, fifo_overflow=%b", src_n, ng, fifo_ovf);
        // find the source index of the first captured word
        found = -1;
        for (lag = 0; lag < 3000 && found < 0; lag = lag + 1)
            if (got[0][7:0] == src[lag] && got[0][15:8] == src[lag+1] && got[0][23:16] == src[lag+2] && got[0][31:24] == src[lag+3] &&
                got[1][7:0] == src[lag+4] && got[1][15:8] == src[lag+5]) found = lag;
        if (found < 0) begin errors = errors + 1; $display("FAIL: captured words do not match the source sequence (got[0]=%h)", got[0]); end
        else begin
            mism = 0;
            for (i = 0; i < 1000; i = i + 1) for (k = 0; k < 4; k = k + 1)
                if (got[i][8*k +: 8] !== src[found + 4*i + k]) mism = mism + 1;
            $display("sequence check: first word = source sample %0d, %0d mismatching samples of 4000", found, mism);
            if (mism != 0) errors = errors + 1;
        end
        if (fifo_ovf) begin errors = errors + 1; $display("FAIL: FIFO overflow"); end
        if (errors == 0) begin $display("PASS tb_adc_iserdes_capture: 8 lanes locked (lane 5 skew compensated, %0d taps), bitslip/manual/auto ok, 4000 samples reproduced exactly", dtap); $finish; end
        else begin $display("FAIL tb_adc_iserdes_capture: %0d errors", errors); $fatal(1); end
    end
    initial begin #4_000_000; $display("FAIL tb_adc_iserdes_capture: timeout (cal_busy=%b done=%b)", cal_busy, cal_done); $fatal(1); end
endmodule
