`timescale 1ns / 1ps
// ============================================================================
// adc_capture_calib.v  -  IDELAY tap calibration for ad9484_iserdes_capture. BETA.
//
// Runs in the capture's regional clock domain (clk_div = DCO/4, 100 MHz). The
// control inputs come from the register map in clk_100m and are quasi-static
// (written rarely, 2-flop synchronised here; "start" controls are toggles).
// Status outputs are quasi-static too: the host reads them twice.
//
// Modes
//   * after reset (idelay_rdy): every lane is loaded with DEFAULT_TAP (16 = 1.25 ns,
//     the nominal mid-bit point for an edge-aligned 400 MHz SDR bus).
//   * manual: toggling ctrl_manual_load_t loads ctrl_tap into lane ctrl_lane;
//     toggling ctrl_bitslip_load_t issues ctrl_bitslip BITSLIP pulses to that lane.
//   * auto, PATTERN method (ctrl_blind = 0, ctrl_auto_start_t toggled while the ADC
//     emits a known 2-sample pattern): for tap = 0..31 all lanes are loaded, SETTLE
//     cycles are skipped and MEAS words are compared; lane l passes a tap when bit l of
//     every word is {A,B,A,B} or {B,A,B,A} (pattern_a/b = the two alternating 8-bit
//     codes). The longest circular pass run is found per lane, its centre is loaded,
//     and lock[l] is set when the run is >= MIN_WINDOW taps and < 32 (a 32-tap run means
//     the lane bit is constant in the pattern - undetermined - and DEFAULT_TAP is kept).
//     After the taps are applied the lanes are ALIGNED: a one-bit framing error on a
//     single lane cannot be seen by a 2-sample pattern per lane (it looks like the other
//     rotation), so the rotation ({A,B,A,B} vs {B,A,B,A}) of every lane is measured
//     over MEAS words, lanes in the minority get one BITSLIP, and the measurement is
//     repeated; align_fail is set if the lanes still disagree.
//   * auto, BLIND method (ctrl_blind = 1; no ADC test pattern - the AD9484 SPI is not
//     wired on the schematic): the live input must be a single CW tone at the IF
//     (120 MHz at 400 MSPS by default). For a sampled sinusoid
//         x[n] = 2cos(w) x[n-1] - x[n-2]        exactly, w = 2*pi*f_IF/f_S,
//     so the notch residual r[n] = x[n] - 2cos(w) x[n-1] + x[n-2] (x = offset binary -
//     128, 2cos(w) = blind_coef/8192 with blind_coef = signed Q1.14 cos(w)) is
//     quantisation-sized when all lanes deliver the right bits and grows by ~2.6 * 2^l
//     per corrupted sample of lane l (edge sampling or wrong framing). Metric per tap =
//     sum |r[n]| over MEAS_BLIND words (x4 samples). Because the residual mixes all
//     bits, lanes are swept ONE AT A TIME (the others keep their taps), MSB first, and
//     each lane's result is applied before the next lane is swept; BLIND_PASSES passes
//     are run so that a badly skewed high lane does not spoil the first pass of the low
//     lanes. A tap passes when metric <= min(metric) + blind_margin + min(metric)/16 (the
//     relative part tracks the floor noise, which grows with the floor); the longest
//     LINEAR pass run gives the eye. Taps that sample the neighbouring bit fail (wrong
//     framing), so unlike the pattern method the run cannot wrap around tap 31 -> 0;
//     at 400 MSPS one bit period is exactly 32 taps (2.5 ns / 78.125 ps), so an eye
//     truncated at tap 0 (run 0..hi) is centred at hi + 1 - 16 + FAIL_HALF (mod 32) and
//     one truncated at tap 31 (run lo..31) at lo - 1 + 16 - FAIL_HALF, FAIL_HALF = 2 taps
//     (half the 5-tap metastable region of the simulation model; hardware value unknown,
//     an error of e taps in FAIL_HALF moves the centre by e). Single failing taps inside
//     the pass run are noise and are filled in before the run search (a real fail region
//     is >= 2 adjacent taps: metastable window plus the neighbouring bit). Sensitivity: an
//     error on lane l adds ~2.6 * 2^l to sum |r| when 2^l >> the noise, but only
//     ~0.7 for l = 0 at 0.8 LSB rms input noise (the error hides under the noise), so the
//     LSB lanes need a quiet input: with MEAS_BLIND = 512 (2048 samples) the LSB eye edge
//     is resolved for <= ~1 LSB rms noise (AD9484: ~47 dB SNR = ~0.5 LSB rms); at 1.4 LSB
//     rms lane 0 is reported undetermined (every tap passes) and keeps its tap. Results that wrap
//     below 0 select the previous bit. A blind ALIGNMENT pass measures the metric for the
//     4 framings of every lane (BITSLIP between them, MSB first) and keeps the best; it
//     runs BEFORE the tap passes (a mis-framed lane raises the floor for every lane and
//     cannot be tap-calibrated: all its taps are equally bad) and again AFTER every pass
//     (a tap result that wrapped below 0 or above 31 moved that lane by one bit; a lane
//     parked at a metastable tap is equidistant between two framings, so its first
//     alignment is a coin toss that the pass corrects). A run truncated at a sweep
//     boundary is accepted from 2 taps (the eye continues beyond the boundary); an
//     untruncated run needs MIN_WINDOW. lock[l] = run accepted and < 32;
//     undetermined[l] = every tap passes (the lane bit never toggles, e.g. a small tone),
//     the lane then keeps its current tap. Limits: single tone at the programmed
//     frequency with enough amplitude for every bit to toggle (>= ~64 LSB peak for bit 7
//     of a centred tone); DC, saturation, a chirp (~30 % residual for a 20 MHz sweep),
//     a second tone or a wrong blind_coef raise the floor for ALL taps and lanes equally
//     (min + margin still works until the floor noise exceeds the margin); the noise
//     floor is sum |r| ~ 1.8 * sigma_x * 4 * MEAS_BLIND. The blind alignment picks the
//     minimum of four without a significance test (align_fail stays 0 in blind mode).
//   * ctrl_check_en: counts words that do not match the pattern as a WHOLE (all lanes
//     the same rotation, no bit errors) - err_count, saturating; usable while the ADC
//     is in test mode (pattern method only).
//
// ADC test pattern (AD9484 register map, SPI - the ADC SPI path is UNRESOLVED on
// the schematic, so the STM32/host must perform these writes once it exists):
//   recommended: register 0x0D = 0x48 (bits[7:6] = 01 "toggle P1/P2", bits[3:0] =
//   1000 "user defined"), USER_PATT1 (0x19/0x1A) = pattern_a, USER_PATT2
//   (0x1B/0x1C) = pattern_b, register 0xFF = 0x01 (transfer); alternative 0x0D =
//   0x04 (checkerboard) or 0x07 (one/zero word toggle) with pattern_a/b set to the
//   codes the device produces in that mode (not stated numerically in the
//   datasheet - verify on hardware). Return to normal data with 0x0D = 0x00.
//   The register defaults here (0xAA / 0x55) correspond to the user-defined mode.
// ============================================================================
module adc_capture_calib #(
    parameter [4:0] DEFAULT_TAP = 5'd16,
    parameter       SETTLE      = 16,     // clk_div cycles after a tap load before measuring
    parameter       MEAS        = 64,     // words compared per tap (pattern method)
    parameter       MIN_WINDOW  = 4,      // taps (x 78 ps) for a lane to count as locked
    parameter       MEAS_BLIND  = 512,    // words (x4 samples) per tap / per framing (blind method)
    parameter       BLIND_PASSES = 2,     // lane sweeps per blind run
    parameter [4:0] TAPS_PER_BIT = 5'd0,  // 32 taps = one bit period at 400 MSPS (5-bit wrap)
    parameter [4:0] FAIL_HALF    = 5'd2   // half the metastable region, taps (sim model: 0.4 ns = 5 taps)
) (
    input  wire        clk,               // clk_div
    input  wire        rst_n,             // rst_n_div
    input  wire        idelay_rdy,
    input  wire [31:0] word,              // {s3,s2,s1,s0}
    input  wire        word_valid,
    // quasi-static controls (from the register map, clk_100m domain)
    input  wire        ctrl_auto_start_t,
    input  wire        ctrl_manual_load_t,
    input  wire        ctrl_bitslip_load_t,
    input  wire        ctrl_check_en,
    input  wire [2:0]  ctrl_lane,
    input  wire [4:0]  ctrl_tap,
    input  wire [1:0]  ctrl_bitslip,
    input  wire [7:0]  pattern_a,
    input  wire [7:0]  pattern_b,
    input  wire        ctrl_blind,        // 1: blind method (CW tone), 0: pattern method
    input  wire [15:0] blind_coef,        // signed Q1.14 cos(w), default 0xEC39 = -5063 (120 MHz @ 400 MSPS)
    input  wire [15:0] blind_margin,      // metric margin above the per-lane minimum (default 64)
    // to the capture module
    output reg  [7:0]  tap_ld,
    output reg  [39:0] tap_val,
    output reg  [7:0]  bitslip,
    // status (quasi-static)
    output reg         cal_busy,
    output reg         cal_done,
    output reg  [7:0]  lock,
    output reg  [7:0]  undetermined,
    output reg         align_fail,
    output wire [4:0]  lane_tap,          // for ctrl_lane
    output wire [4:0]  lane_win_lo,
    output wire [4:0]  lane_win_hi,
    output reg  [15:0] err_count,
    output wire [15:0] lane_metric_min    // blind: min metric of ctrl_lane >> 4, saturated
);
    // ---------------- control synchronisation ----------------
    (* ASYNC_REG = "TRUE" *) reg [2:0] auto_s, man_s, slip_s;
    reg [1:0] chk_s;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin auto_s <= 3'b000; man_s <= 3'b000; slip_s <= 3'b000; chk_s <= 2'b00; end
        else begin
            auto_s <= {auto_s[1:0], ctrl_auto_start_t};
            man_s  <= {man_s[1:0],  ctrl_manual_load_t};
            slip_s <= {slip_s[1:0], ctrl_bitslip_load_t};
            chk_s  <= {chk_s[0], ctrl_check_en};
        end
    end
    wire auto_req = auto_s[2] ^ auto_s[1];
    wire man_req  = man_s[2]  ^ man_s[1];
    wire slip_req = slip_s[2] ^ slip_s[1];
    wire check_en = chk_s[1];

    // ---------------- pattern comparison ----------------
    wire [7:0] s0 = word[7:0], s1 = word[15:8], s2 = word[23:16], s3 = word[31:24];
    wire [7:0] ok_ab = ~(s0 ^ pattern_a) & ~(s1 ^ pattern_b) & ~(s2 ^ pattern_a) & ~(s3 ^ pattern_b);
    wire [7:0] ok_ba = ~(s0 ^ pattern_b) & ~(s1 ^ pattern_a) & ~(s2 ^ pattern_b) & ~(s3 ^ pattern_a);
    wire [7:0] lane_ok = ok_ab | ok_ba;              // per lane: this word matches the pattern
    wire [7:0] lane_const = ~(pattern_a ^ pattern_b); // lane bit identical in A and B -> undetermined
    wire [7:0] lane_var  = ~lane_const;
    // word-level check: every varying lane shows the SAME rotation
    wire word_ok = ((ok_ab & lane_var) == lane_var) || ((ok_ba & lane_var) == lane_var);

    // ---------------- blind metric: notch residual at the IF ----------------
    // r[n] = x[n] - (coef * x[n-1]) / 8192 + x[n-2], x = sample - 128 (9-bit signed)
    wire signed [8:0] xs0 = $signed({1'b0, s0}) - 9'sd128, xs1 = $signed({1'b0, s1}) - 9'sd128,
                      xs2 = $signed({1'b0, s2}) - 9'sd128, xs3 = $signed({1'b0, s3}) - 9'sd128;
    reg  signed [8:0] xp1, xp2;                       // x[-1], x[-2] of the current word = s3, s2 of the previous
    wire signed [15:0] coef_s = $signed(blind_coef);
    /* verilator lint_off UNUSEDSIGNAL */
    function [11:0] resid;                            // 12-bit two's complement, |r| <= 512
        input signed [8:0] x0; input signed [8:0] xm1; input signed [8:0] xm2; input signed [15:0] c;
        reg signed [24:0] p; reg signed [24:0] q;      // q[24:12] are sign copies (|q| <= 256)
        begin
            p = xm1 * c;                               // 2cos(w) * x[n-1] in Q13 (coef is Q14 of cos)
            q = (p + 25'sd4096) >>> 13;                // rounded to integer
            resid = {{3{x0[8]}}, x0} - q[11:0] + {{3{xm2[8]}}, xm2};
        end
    endfunction
    /* verilator lint_on UNUSEDSIGNAL */
    function [11:0] absr; input [11:0] r; begin absr = r[11] ? (~r + 12'd1) : r; end endfunction
    wire [11:0] r0 = resid(xs0, xp1, xp2, coef_s);
    wire [11:0] r1 = resid(xs1, xs0, xp1, coef_s);
    wire [11:0] r2 = resid(xs2, xs1, xs0, coef_s);
    wire [11:0] r3 = resid(xs3, xs2, xs1, coef_s);
    wire [12:0] abs_sum = {1'b0, absr(r0)} + {1'b0, absr(r1)} + {1'b0, absr(r2)} + {1'b0, absr(r3)};   // <= 2048
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin xp1 <= 9'sd0; xp2 <= 9'sd0; end
        else if (word_valid) begin xp1 <= xs3; xp2 <= xs2; end
    end
    reg  [23:0] metric;                 // sum |r| in the current measurement (saturating)
    reg  [23:0] met_min;                // minimum over the taps of the current lane sweep
    reg  [23:0] met [0:31];             // metric per tap of the current lane sweep
    reg  [23:0] metric_min [0:7];       // per lane: minimum metric of its last sweep
    reg  [2:0]  bl_lane;                // lane being swept / aligned (blind)
    reg         blind_run;              // 1 while an auto run uses the blind method
    reg  [3:0]  bl_pass;
    reg  [1:0]  al_fr;                  // framing under test (BITSLIP pulses issued so far, mod 4)
    reg  [1:0]  al_best;                // best framing so far
    reg  [23:0] al_best_met;
    reg  [1:0]  al_todo;                // remaining BITSLIP pulses to reach al_best
    reg         al_final;               // 0: initial alignment (then sweep), 1: final alignment (then done)
    localparam integer MEAS_M1_I       = MEAS - 1;
    localparam integer MEAS_BLIND_M1_I = MEAS_BLIND - 1;
    localparam [9:0] MEAS_M1       = MEAS_M1_I[9:0];
    localparam [9:0] MEAS_BLIND_M1 = MEAS_BLIND_M1_I[9:0];     // 512 words -> 511
    localparam [4:0] HALF_BIT      = 5'd16;        // TAPS_PER_BIT / 2 (32 taps = one bit period)
    /* verilator lint_off UNUSEDPARAM */
    localparam [4:0] UNUSED_TPB = TAPS_PER_BIT;    // documented as 32 (= 0 mod 32); kept for the record
    /* verilator lint_on UNUSEDPARAM */

    // ---------------- state ----------------
    localparam [4:0] S_WAIT_RDY = 0, S_LOAD_DEF = 1, S_IDLE = 2, S_SW_LOAD = 3, S_SW_SETTLE = 4,
                     S_SW_MEAS = 5, S_ANALYSE = 6, S_APPLY = 7, S_SLIP = 8,
                     S_AL_SETTLE = 9, S_AL_MEAS = 10, S_AL_FIX = 11, S_DONE = 12,
                     S_BL_SCAN = 13, S_BL_RUN = 14, S_BL_DECIDE = 15, S_BL_NEXT = 16,
                     S_BL_AL_SETTLE = 17, S_BL_AL_MEAS = 18, S_BL_AL_STEP = 19, S_BL_AL_GAP = 20,
                     S_BL_AL_FIX = 21;
    reg [7:0]  rot_ba;             // lanes seen in the BA rotation during alignment
    reg [7:0]  rot_ab;
    reg        al_pass;            // 0: first measurement, 1: verification
    reg [4:0]  st;
    reg [4:0]  tap_i;              // sweep tap
    reg [7:0]  settle_cnt;
    reg [9:0]  meas_cnt;
    reg [7:0]  lane_fail;          // accumulated over MEAS words
    reg [31:0] pass_mask [0:7];    // per lane, bit = tap passes
    reg [4:0]  tap_sel  [0:7];
    reg [4:0]  win_lo   [0:7];
    reg [4:0]  win_hi   [0:7];
    // circular / linear longest-run search (one lane at a time)
    reg [2:0]  an_lane;
    reg [6:0]  an_pos;             // 0..63
    reg [5:0]  run_len, best_len;
    reg [4:0]  run_start, best_start;
    reg [1:0]  slip_cnt;
    reg        slip_gap;

    function [3:0] popcount;
        input [7:0] v;
        integer j;
        begin popcount = 0; for (j = 0; j < 8; j = j + 1) popcount = popcount + {3'd0, v[j]}; end
    endfunction

    wire [23:0] metric_now = (metric > 24'hFFF000) ? 24'hFFFFFF : metric + {11'd0, abs_sum};
    wire [23:0] pass_thr   = (met_min > 24'hE00000) ? 24'hFFFFFF : met_min + {8'd0, blind_margin} + (met_min >> 4);
    wire [4:0]  best_hi    = best_start + best_len[4:0] - 5'd1;
    wire [31:0] bl_mask_raw = pass_mask[bl_lane];
    wire [31:0] bl_mask    = bl_mask_raw | ((bl_mask_raw << 1) & (bl_mask_raw >> 1));   // fill single-tap holes
    wire        trunc_lo   = (best_start == 5'd0) && (best_hi != 5'd31);     // eye cut at tap 0
    wire        trunc_hi   = (best_hi == 5'd31) && (best_start != 5'd0);     // eye cut at tap 31

    integer k;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            align_fail <= 1'b0; rot_ab <= 8'd0; rot_ba <= 8'd0; al_pass <= 1'b0;
            st <= S_WAIT_RDY; tap_ld <= 8'd0; tap_val <= {8{DEFAULT_TAP}}; bitslip <= 8'd0;
            cal_busy <= 1'b0; cal_done <= 1'b0; lock <= 8'd0; undetermined <= 8'd0; err_count <= 16'd0;
            tap_i <= 5'd0; settle_cnt <= 8'd0; meas_cnt <= 10'd0; lane_fail <= 8'd0;
            an_lane <= 3'd0; an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0;
            slip_cnt <= 2'd0; slip_gap <= 1'b0;
            metric <= 24'd0; met_min <= 24'hFFFFFF; bl_lane <= 3'd7; blind_run <= 1'b0; bl_pass <= 4'd0;
            al_fr <= 2'd0; al_best <= 2'd0; al_best_met <= 24'hFFFFFF; al_todo <= 2'd0; al_final <= 1'b0;
            for (k = 0; k < 8; k = k + 1) begin pass_mask[k] <= 32'd0; tap_sel[k] <= DEFAULT_TAP; win_lo[k] <= 5'd0; win_hi[k] <= 5'd0; metric_min[k] <= 24'd0; end
            for (k = 0; k < 32; k = k + 1) met[k] <= 24'd0;
        end else begin
            tap_ld  <= 8'd0;
            bitslip <= 8'd0;

            // running pattern check (any mode): word must match as a whole
            if (check_en && word_valid && !word_ok && err_count != 16'hFFFF)
                err_count <= err_count + 16'd1;
            if (chk_s == 2'b01) err_count <= 16'd0;        // rising edge of check_en clears

            case (st)
                S_WAIT_RDY: if (idelay_rdy) st <= S_LOAD_DEF;
                S_LOAD_DEF: begin
                    tap_val <= {8{DEFAULT_TAP}}; tap_ld <= 8'hFF;
                    for (k = 0; k < 8; k = k + 1) tap_sel[k] <= DEFAULT_TAP;
                    st <= S_IDLE;
                end
                S_IDLE: begin
                    cal_busy <= 1'b0;
                    if (auto_req) begin
                        cal_busy <= 1'b1; cal_done <= 1'b0; lock <= 8'd0; undetermined <= 8'd0; err_count <= 16'd0; align_fail <= 1'b0;
                        tap_i <= 5'd0; blind_run <= ctrl_blind; bl_lane <= 3'd7; bl_pass <= 4'd0; met_min <= 24'hFFFFFF;
                        if (ctrl_blind) begin                   // blind: align the framing first
                            al_fr <= 2'd0; al_best <= 2'd0; al_best_met <= 24'hFFFFFF; al_final <= 1'b0;
                            settle_cnt <= 8'd0; st <= S_BL_AL_SETTLE;
                        end else st <= S_SW_LOAD;
                        for (k = 0; k < 8; k = k + 1) pass_mask[k] <= 32'd0;
                    end else if (man_req) begin
                        tap_val[5*ctrl_lane +: 5] <= ctrl_tap; tap_ld[ctrl_lane] <= 1'b1;
                        tap_sel[ctrl_lane] <= ctrl_tap;
                    end else if (slip_req && ctrl_bitslip != 2'd0) begin
                        slip_cnt <= ctrl_bitslip; slip_gap <= 1'b0; st <= S_SLIP;
                    end
                end
                S_SLIP: begin                                   // one BITSLIP pulse, one gap cycle, repeat
                    if (slip_gap) begin
                        slip_gap <= 1'b0;
                        if (slip_cnt == 2'd0) st <= S_IDLE;
                    end else begin
                        bitslip[ctrl_lane] <= 1'b1; slip_cnt <= slip_cnt - 2'd1; slip_gap <= 1'b1;
                    end
                end
                // ---------- tap sweep (both methods) ----------
                S_SW_LOAD: begin
                    if (blind_run) begin                        // one lane at a time, the others keep their taps
                        tap_val[5*bl_lane +: 5] <= tap_i; tap_ld[bl_lane] <= 1'b1;
                    end else begin
                        tap_val <= {8{tap_i}}; tap_ld <= 8'hFF;
                    end
                    settle_cnt <= 8'd0; st <= S_SW_SETTLE;
                end
                S_SW_SETTLE: begin
                    if (settle_cnt == SETTLE[7:0]) begin meas_cnt <= 10'd0; lane_fail <= 8'd0; metric <= 24'd0; st <= S_SW_MEAS; end
                    else settle_cnt <= settle_cnt + 8'd1;
                end
                S_SW_MEAS: if (word_valid) begin
                    lane_fail <= lane_fail | ~lane_ok;
                    metric    <= metric_now;
                    if (meas_cnt == (blind_run ? MEAS_BLIND_M1 : MEAS_M1)) begin
                        if (blind_run) begin
                            met[tap_i] <= metric_now;
                            if (metric_now < met_min) met_min <= metric_now;
                        end else
                            for (k = 0; k < 8; k = k + 1) pass_mask[k][tap_i] <= ~(lane_fail[k] | ~lane_ok[k]);
                        if (tap_i == 5'd31) begin
                            an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0;
                            if (blind_run) st <= S_BL_SCAN;
                            else begin an_lane <= 3'd0; st <= S_ANALYSE; end
                        end else begin
                            tap_i <= tap_i + 5'd1; st <= S_SW_LOAD;
                        end
                    end else meas_cnt <= meas_cnt + 10'd1;
                end
                // ---------- pattern method: circular longest run, all lanes ----------
                S_ANALYSE: begin
                    // walk 64 positions (two turns) to find the longest circular run of passing taps
                    if (an_pos < 7'd64) begin
                        if (pass_mask[an_lane][an_pos[4:0]]) begin
                            if (run_len == 6'd0) run_start <= an_pos[4:0];
                            if (run_len < 6'd32) begin
                                run_len <= run_len + 6'd1;
                                if (run_len + 6'd1 > best_len) begin
                                    best_len <= run_len + 6'd1;
                                    best_start <= (run_len == 6'd0) ? an_pos[4:0] : run_start;
                                end
                            end
                        end else run_len <= 6'd0;
                        an_pos <= an_pos + 7'd1;
                    end else begin
                        if (lane_const[an_lane] || best_len >= 6'd32 || best_len < MIN_WINDOW[5:0]) begin
                            tap_sel[an_lane] <= DEFAULT_TAP;
                            undetermined[an_lane] <= lane_const[an_lane] | (best_len >= 6'd32);
                            lock[an_lane] <= 1'b0;
                        end else begin
                            tap_sel[an_lane] <= best_start + best_len[5:1];     // centre (mod 32 by width)
                            lock[an_lane] <= 1'b1;
                        end
                        win_lo[an_lane] <= best_start;
                        win_hi[an_lane] <= best_hi;
                        if (an_lane == 3'd7) st <= S_APPLY;
                        else begin an_lane <= an_lane + 3'd1; an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0; end
                    end
                end
                S_APPLY: begin
                    for (k = 0; k < 8; k = k + 1) tap_val[5*k +: 5] <= tap_sel[k];
                    tap_ld <= 8'hFF; settle_cnt <= 8'd0; al_pass <= 1'b0; st <= S_AL_SETTLE;
                end
                S_AL_SETTLE: begin
                    if (settle_cnt == SETTLE[7:0]) begin meas_cnt <= 10'd0; rot_ab <= 8'd0; rot_ba <= 8'd0; st <= S_AL_MEAS; end
                    else settle_cnt <= settle_cnt + 8'd1;
                end
                S_AL_MEAS: if (word_valid) begin
                    rot_ab <= rot_ab | (ok_ab & lane_var);
                    rot_ba <= rot_ba | (ok_ba & lane_var);
                    if (meas_cnt == MEAS_M1) st <= S_AL_FIX;
                    else meas_cnt <= meas_cnt + 10'd1;
                end
                S_AL_FIX: begin
                    // majority rotation = the one seen on more lanes; minority lanes get one BITSLIP
                    if (rot_ab == (rot_ab | rot_ba) || rot_ba == (rot_ab | rot_ba) ||
                        (rot_ab & rot_ba) != 8'd0 && al_pass) begin
                        // consistent (all varying lanes agree) -> done; a lane that showed BOTH
                        // rotations is a bit-error lane, flagged through align_fail on the 2nd pass
                        align_fail <= ((rot_ab & rot_ba) != 8'd0);
                        st <= S_DONE;
                    end else if (!al_pass) begin
                        bitslip <= (popcount(rot_ab) >= popcount(rot_ba)) ? (rot_ba & ~rot_ab) : (rot_ab & ~rot_ba);
                        al_pass <= 1'b1; settle_cnt <= 8'd0; st <= S_AL_SETTLE;
                    end else begin
                        align_fail <= 1'b1; st <= S_DONE;
                    end
                end
                // ---------- blind method: per-lane pass mask, linear longest run, apply ----------
                S_BL_SCAN: begin                               // pass_mask[bl_lane][tap] = met[tap] <= min + margin
                    if (an_pos < 7'd32) begin
                        pass_mask[bl_lane] <= (pass_mask[bl_lane] & ~(32'd1 << an_pos[4:0])) |
                                              ({31'd0, (met[an_pos[4:0]] <= pass_thr)} << an_pos[4:0]);
                        an_pos <= an_pos + 7'd1;
                    end else begin
                        an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0;
                        st <= S_BL_RUN;
                    end
                end
                S_BL_RUN: begin                                // linear (non-circular) longest run, 1-tap holes closed
                    if (an_pos < 7'd32) begin
                        if (bl_mask[an_pos[4:0]]) begin
                            if (run_len == 6'd0) run_start <= an_pos[4:0];
                            run_len <= run_len + 6'd1;
                            if (run_len + 6'd1 > best_len) begin
                                best_len <= run_len + 6'd1;
                                best_start <= (run_len == 6'd0) ? an_pos[4:0] : run_start;
                            end
                        end else run_len <= 6'd0;
                        an_pos <= an_pos + 7'd1;
                    end else st <= S_BL_DECIDE;
                end
                S_BL_DECIDE: begin
                    metric_min[bl_lane] <= met_min;
                    win_lo[bl_lane] <= best_start;
                    win_hi[bl_lane] <= best_hi;
                    if (best_len >= 6'd32) begin                                 // never spikes: bit does not toggle
                        undetermined[bl_lane] <= 1'b1; lock[bl_lane] <= 1'b0;
                    end else if (best_len < ((trunc_lo || trunc_hi) ? 6'd2 : MIN_WINDOW[5:0])) begin
                        undetermined[bl_lane] <= 1'b0; lock[bl_lane] <= 1'b0;
                    end else begin
                        undetermined[bl_lane] <= 1'b0; lock[bl_lane] <= 1'b1;
                        if (trunc_lo)
                            tap_sel[bl_lane] <= best_hi + 5'd1 - HALF_BIT + FAIL_HALF;     // eye truncated at tap 0
                        else if (trunc_hi)
                            tap_sel[bl_lane] <= best_start - 5'd1 + HALF_BIT - FAIL_HALF;  // eye truncated at tap 31 (-> other framing)
                        else
                            tap_sel[bl_lane] <= best_start + best_len[5:1];                 // centre
                    end
                    st <= S_BL_NEXT;
                end
                S_BL_NEXT: begin                               // apply this lane's tap (restores it after the sweep)
                    tap_val[5*bl_lane +: 5] <= tap_sel[bl_lane]; tap_ld[bl_lane] <= 1'b1;
                    tap_i <= 5'd0; met_min <= 24'hFFFFFF;
                    if (bl_lane != 3'd0) begin bl_lane <= bl_lane - 3'd1; st <= S_SW_LOAD; end
                    else begin                                                   // pass complete: re-align, MSB first
                        bl_pass <= bl_pass + 4'd1; al_final <= (bl_pass + 4'd1 >= BLIND_PASSES[3:0]);
                        bl_lane <= 3'd7; al_fr <= 2'd0; al_best <= 2'd0; al_best_met <= 24'hFFFFFF;
                        settle_cnt <= 8'd0; st <= S_BL_AL_SETTLE;
                    end
                end
                // ---------- blind alignment: metric for the 4 framings of each lane ----------
                S_BL_AL_SETTLE: begin
                    if (settle_cnt == SETTLE[7:0]) begin meas_cnt <= 10'd0; metric <= 24'd0; st <= S_BL_AL_MEAS; end
                    else settle_cnt <= settle_cnt + 8'd1;
                end
                S_BL_AL_MEAS: if (word_valid) begin
                    metric <= metric_now;
                    if (meas_cnt == MEAS_BLIND_M1) st <= S_BL_AL_STEP;
                    else meas_cnt <= meas_cnt + 10'd1;
                end
                S_BL_AL_STEP: begin
                    if (metric < al_best_met) begin al_best_met <= metric; al_best <= al_fr; end
                    if (al_fr != 2'd3) begin                                     // next framing
                        bitslip[bl_lane] <= 1'b1; al_fr <= al_fr + 2'd1; st <= S_BL_AL_GAP;
                    end else begin                                               // at framing 3: go to the best one
                        al_todo <= ((metric < al_best_met) ? 2'd3 : al_best) + 2'd1;   // (best - 3) mod 4
                        st <= S_BL_AL_FIX;
                    end
                end
                S_BL_AL_GAP: begin settle_cnt <= 8'd0; st <= S_BL_AL_SETTLE; end   // >= 1 idle CLKDIV between pulses
                S_BL_AL_FIX: begin
                    if (slip_gap) slip_gap <= 1'b0;
                    else if (al_todo != 2'd0) begin bitslip[bl_lane] <= 1'b1; al_todo <= al_todo - 2'd1; slip_gap <= 1'b1; end
                    else if (bl_lane != 3'd0) begin
                        bl_lane <= bl_lane - 3'd1; al_fr <= 2'd0; al_best <= 2'd0; al_best_met <= 24'hFFFFFF;
                        settle_cnt <= 8'd0; st <= S_BL_AL_SETTLE;
                    end else if (!al_final) begin                                // framing consistent: (next) tap pass
                        bl_lane <= 3'd7; tap_i <= 5'd0; met_min <= 24'hFFFFFF; st <= S_SW_LOAD;
                    end else st <= S_DONE;
                end
                S_DONE: begin
                    cal_done <= 1'b1; cal_busy <= 1'b0; st <= S_IDLE;
                end
                default: st <= S_IDLE;
            endcase
        end
    end

    assign lane_tap    = tap_sel[ctrl_lane];
    assign lane_win_lo = win_lo[ctrl_lane];
    assign lane_win_hi = win_hi[ctrl_lane];
    wire [19:0] mm_sel = metric_min[ctrl_lane][23:4];
    assign lane_metric_min = (|mm_sel[19:16]) ? 16'hFFFF : mm_sel[15:0];
endmodule
