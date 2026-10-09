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
//   * auto (ctrl_auto_start_t toggled while the ADC emits a known 2-sample pattern):
//     for tap = 0..31 all lanes are loaded, SETTLE cycles are skipped and MEAS words
//     are compared; lane l passes a tap when bit l of every word is {A,B,A,B} or
//     {B,A,B,A} (pattern_a/b = the two alternating 8-bit codes). The longest
//     circular pass run is found per lane, its centre is loaded, and lock[l] is set
//     when the run is >= MIN_WINDOW taps and < 32 (a 32-tap run means the lane bit
//     is constant in the pattern - undetermined - and DEFAULT_TAP is kept).
//     After the taps are applied the lanes are ALIGNED: a one-bit framing error on a
//     single lane cannot be seen by a 2-sample pattern per lane (it looks like the other
//     rotation), so the rotation ({A,B,A,B} vs {B,A,B,A}) of every lane is measured
//     over MEAS words, lanes in the minority get one BITSLIP, and the measurement is
//     repeated; align_fail is set if the lanes still disagree.
//   * ctrl_check_en: counts words that do not match the pattern as a WHOLE (all lanes
//     the same rotation, no bit errors) - err_count, saturating; usable while the ADC
//     is in test mode.
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
    parameter       MEAS        = 64,     // words compared per tap
    parameter       MIN_WINDOW  = 4       // taps (x 78 ps) for a lane to count as locked
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
    output reg  [15:0] err_count
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

    // ---------------- state ----------------
    localparam [3:0] S_WAIT_RDY = 0, S_LOAD_DEF = 1, S_IDLE = 2, S_SW_LOAD = 3, S_SW_SETTLE = 4,
                     S_SW_MEAS = 5, S_ANALYSE = 6, S_APPLY = 7, S_SLIP = 8,
                     S_AL_SETTLE = 9, S_AL_MEAS = 10, S_AL_FIX = 11, S_DONE = 12;
    reg [7:0]  rot_ba;             // lanes seen in the BA rotation during alignment
    reg [7:0]  rot_ab;
    reg        al_pass;            // 0: first measurement, 1: verification
    reg [3:0]  st;
    reg [4:0]  tap_i;              // sweep tap
    reg [7:0]  settle_cnt;
    reg [7:0]  meas_cnt;
    reg [7:0]  lane_fail;          // accumulated over MEAS words
    reg [31:0] pass_mask [0:7];    // per lane, bit = tap passes
    reg [4:0]  tap_sel  [0:7];
    reg [4:0]  win_lo   [0:7];
    reg [4:0]  win_hi   [0:7];
    // circular longest-run search (one lane at a time)
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

    integer k;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            align_fail <= 1'b0; rot_ab <= 8'd0; rot_ba <= 8'd0; al_pass <= 1'b0;
            st <= S_WAIT_RDY; tap_ld <= 8'd0; tap_val <= {8{DEFAULT_TAP}}; bitslip <= 8'd0;
            cal_busy <= 1'b0; cal_done <= 1'b0; lock <= 8'd0; undetermined <= 8'd0; err_count <= 16'd0;
            tap_i <= 5'd0; settle_cnt <= 8'd0; meas_cnt <= 8'd0; lane_fail <= 8'd0;
            an_lane <= 3'd0; an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0;
            slip_cnt <= 2'd0; slip_gap <= 1'b0;
            for (k = 0; k < 8; k = k + 1) begin pass_mask[k] <= 32'd0; tap_sel[k] <= DEFAULT_TAP; win_lo[k] <= 5'd0; win_hi[k] <= 5'd0; end
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
                        tap_i <= 5'd0; st <= S_SW_LOAD;
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
                S_SW_LOAD: begin
                    tap_val <= {8{tap_i}}; tap_ld <= 8'hFF; settle_cnt <= 8'd0; st <= S_SW_SETTLE;
                end
                S_SW_SETTLE: begin
                    if (settle_cnt == SETTLE[7:0]) begin meas_cnt <= 8'd0; lane_fail <= 8'd0; st <= S_SW_MEAS; end
                    else settle_cnt <= settle_cnt + 8'd1;
                end
                S_SW_MEAS: if (word_valid) begin
                    lane_fail <= lane_fail | ~lane_ok;
                    if (meas_cnt == MEAS[7:0] - 1) begin
                        for (k = 0; k < 8; k = k + 1) pass_mask[k][tap_i] <= ~(lane_fail[k] | ~lane_ok[k]);
                        if (tap_i == 5'd31) begin
                            an_lane <= 3'd0; an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0;
                            st <= S_ANALYSE;
                        end else begin
                            tap_i <= tap_i + 5'd1; st <= S_SW_LOAD;
                        end
                    end else meas_cnt <= meas_cnt + 8'd1;
                end
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
                        win_hi[an_lane] <= best_start + best_len[4:0] - 5'd1;
                        if (an_lane == 3'd7) st <= S_APPLY;
                        else begin an_lane <= an_lane + 3'd1; an_pos <= 7'd0; run_len <= 6'd0; best_len <= 6'd0; run_start <= 5'd0; best_start <= 5'd0; end
                    end
                end
                S_APPLY: begin
                    for (k = 0; k < 8; k = k + 1) tap_val[5*k +: 5] <= tap_sel[k];
                    tap_ld <= 8'hFF; settle_cnt <= 8'd0; al_pass <= 1'b0; st <= S_AL_SETTLE;
                end
                S_AL_SETTLE: begin
                    if (settle_cnt == SETTLE[7:0]) begin meas_cnt <= 8'd0; rot_ab <= 8'd0; rot_ba <= 8'd0; st <= S_AL_MEAS; end
                    else settle_cnt <= settle_cnt + 8'd1;
                end
                S_AL_MEAS: if (word_valid) begin
                    rot_ab <= rot_ab | (ok_ab & lane_var);
                    rot_ba <= rot_ba | (ok_ba & lane_var);
                    if (meas_cnt == MEAS[7:0] - 1) st <= S_AL_FIX;
                    else meas_cnt <= meas_cnt + 8'd1;
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
endmodule
