`timescale 1ns / 1ps
// ============================================================================
// ddc_4x_100m.v  -  polyphase DDC: 4 ADC samples per 100 MHz clock.  BETA.
//
// Replaces the 400 MHz mixer + CIC of ddc_400m_enhanced (which cannot close
// timing in Artix-7 fabric). Numerically equivalent to the legacy path (same
// NCO tuning word, table, dither sequence, mixer slicing, CIC order/scaling and
// FIR), verified by tb_ddc_4x.v (outputs identical after alignment).
//
//   word {s3,s2,s1,s0} (offset binary) ──► 4-phase NCO + 4 complex mixers
//        ──► CIC ÷4 (5 stages, as a 16-tap FIR (1+z^-1+z^-2+z^-3)^5, >>10, saturate)
//        ──► fir_lowpass_parallel_enhanced x2 ──► registered output
//
// NCO: phase(k) = A(k-1), A(n) = sum_{j<n} (FTW + d(j)), d(0) = d(1) = 0xFF,
// d(j) = L_{j-1} (8-bit LFSR x^8+x^6+x^5+x^4+1 seeded 0xFF) - exactly the sequence
// of nco_400m_enhanced + lfsr_dither_enhanced when the NCO is enabled by the data
// valid (observed in simulation: legacy mixed = 0 (sample 0 is lost in the legacy
// pipeline), src[1]*cos(A(0)), src[2]*cos(A(1)), ...; here sample 0 gets phase 0 too).
// Four phases per clock: p0 = A(4m-1), p1 = A(4m), p2 = A(4m+1), p3 = A(4m+2);
// the LFSR is unrolled four steps per clock (lcur = L_{4m-2}).
// Mixer: legacy mixed[33:16] = ((2*adc-255)*c) >>> 8  (9x16 signed multiply,
// DSP48E1 friendly) - bit exact.
// CIC: h = (1+z^-1+z^-2+z^-3)^5 = [1,5,15,35,65,101,135,155,155,135,101,65,35,15,5,1]
// (sum 1024 = legacy gain), evaluated once per word: y[m] = sum_k h[k] x[4m + CIC_PHASE - k]
// over a 20-sample history, >>> 10, saturated to 18 bits like cic_decimator_4x_enhanced.
// Resources: 8 x (9x16) multipliers (4 I + 4 Q; DSP48E1), 2 x 32-tap FIR (64
// DSP48E1, unchanged), constant-coefficient adder trees for the CIC, 1 ROM.
// ============================================================================
module ddc_4x_100m #(
    parameter [31:0] FTW = 32'h4CCCCCCD,    // 120 MHz at 400 MSPS (ddc_400m.v:144)
    parameter CIC_PHASE = 0                 // which sample of a word ends a decimation group:
                                            // 0 = slot 4m (legacy cic_decimator_4x_enhanced: the comb
                                            // samples the integrator one clock after the decimation
                                            // tick), 3 = slot 4m+3. Verified bit-exact by tb_ddc_4x.
) (
    input  wire               clk,          // 100 MHz
    input  wire               reset_n,
    input  wire               mixers_enable,
    input  wire               bypass_mode,
    input  wire [31:0]        word,         // 4 ADC samples, s0 oldest
    input  wire               word_valid,
    output wire signed [17:0] baseband_i,
    output wire signed [17:0] baseband_q,
    output wire               baseband_valid_i,
    output wire               baseband_valid_q,
    // debug taps (CIC output, before the FIR)
    output wire signed [17:0] cic_i_dbg,
    output wire signed [17:0] cic_q_dbg,
    output wire               cic_valid_dbg
);
    // ---------------- sine table (identical to nco_400m_enhanced.v) ----------------
    reg [15:0] sin_lut [0:64];
    initial begin
    sin_lut[ 0] = 16'h0000; sin_lut[ 1] = 16'h0324; sin_lut[ 2] = 16'h0648; sin_lut[ 3] = 16'h096A;
    sin_lut[ 4] = 16'h0C8C; sin_lut[ 5] = 16'h0FAB; sin_lut[ 6] = 16'h12C8; sin_lut[ 7] = 16'h15E2;
    sin_lut[ 8] = 16'h18F9; sin_lut[ 9] = 16'h1C0B; sin_lut[10] = 16'h1F1A; sin_lut[11] = 16'h2223;
    sin_lut[12] = 16'h2528; sin_lut[13] = 16'h2826; sin_lut[14] = 16'h2B1F; sin_lut[15] = 16'h2E11;
    sin_lut[16] = 16'h30FB; sin_lut[17] = 16'h33DF; sin_lut[18] = 16'h36BA; sin_lut[19] = 16'h398C;
    sin_lut[20] = 16'h3C56; sin_lut[21] = 16'h3F17; sin_lut[22] = 16'h41CE; sin_lut[23] = 16'h447A;
    sin_lut[24] = 16'h471C; sin_lut[25] = 16'h49B4; sin_lut[26] = 16'h4C3F; sin_lut[27] = 16'h4EBF;
    sin_lut[28] = 16'h5133; sin_lut[29] = 16'h539B; sin_lut[30] = 16'h55F5; sin_lut[31] = 16'h5842;
    sin_lut[32] = 16'h5A82; sin_lut[33] = 16'h5CB3; sin_lut[34] = 16'h5ED7; sin_lut[35] = 16'h60EB;
    sin_lut[36] = 16'h62F1; sin_lut[37] = 16'h64E8; sin_lut[38] = 16'h66CF; sin_lut[39] = 16'h68A6;
    sin_lut[40] = 16'h6A6D; sin_lut[41] = 16'h6C23; sin_lut[42] = 16'h6DC9; sin_lut[43] = 16'h6F5E;
    sin_lut[44] = 16'h70E2; sin_lut[45] = 16'h7254; sin_lut[46] = 16'h73B5; sin_lut[47] = 16'h7504;
    sin_lut[48] = 16'h7641; sin_lut[49] = 16'h776B; sin_lut[50] = 16'h7884; sin_lut[51] = 16'h7989;
    sin_lut[52] = 16'h7A7C; sin_lut[53] = 16'h7B5C; sin_lut[54] = 16'h7C29; sin_lut[55] = 16'h7CE3;
    sin_lut[56] = 16'h7D89; sin_lut[57] = 16'h7E1D; sin_lut[58] = 16'h7E9C; sin_lut[59] = 16'h7F09;
    sin_lut[60] = 16'h7F61; sin_lut[61] = 16'h7FA6; sin_lut[62] = 16'h7FD8; sin_lut[63] = 16'h7FF5;
    sin_lut[64] = 16'h7FFF;
    end

    function [7:0] lfsr_step;   // lfsr_dither_enhanced, DITHER_WIDTH 8
        input [7:0] l;
        begin lfsr_step = {l[6:0], l[7] ^ l[5] ^ l[4] ^ l[3]}; end
    endfunction

    // ---------------- stage 0: phases ----------------
    reg  [31:0] acc;          // A(4m-1) entering clock m (m >= 1)
    reg  [7:0]  lcur;         // L_{4m-2} entering clock m
    reg         first;        // m == 0
    wire [7:0]  d0 = lcur, d1 = lfsr_step(d0), d2 = lfsr_step(d1), d3 = lfsr_step(d2);
    wire [31:0] i0 = FTW + {24'd0, d0}, i1 = FTW + {24'd0, d1}, i2 = FTW + {24'd0, d2}, i3 = FTW + {24'd0, d3};
    // m = 0 : p0 = A(-1) := 0, p1 = A(0) = 0, p2 = A(1) = FTW + 0xFF, p3 = A(2) = 2 FTW + 0x1FE,
    //         next acc = A(3) = A(2) + FTW + L_1,  next lcur = L_2
    wire [31:0] a1_first = FTW + 32'h0000_00FF;
    wire [31:0] a2_first = a1_first + FTW + 32'h0000_00FF;
    wire [7:0]  l1_first = lfsr_step(8'hFF);
    wire [31:0] p0 = first ? 32'd0    : acc;
    wire [31:0] p1 = first ? 32'd0    : acc + i0;
    wire [31:0] p2 = first ? a1_first : acc + i0 + i1;
    wire [31:0] p3 = first ? a2_first : acc + i0 + i1 + i2;
    wire [31:0] acc_next  = first ? (a2_first + FTW + {24'd0, l1_first}) : acc + i0 + i1 + i2 + i3;
    wire [7:0]  lcur_next = first ? lfsr_step(l1_first) : lfsr_step(d3);

    reg        en_sync0, en_sync1;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin en_sync0 <= 1'b0; en_sync1 <= 1'b0; end
        else begin en_sync0 <= mixers_enable; en_sync1 <= en_sync0; end
    end
    wire step = word_valid & en_sync1;

    // stage-1 registers: LUT addresses + samples
    reg [7:0] a0_r, a1_r, a2_r, a3_r;
    reg [7:0] s0_r, s1_r, s2_r, s3_r;
    reg       v1;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            acc <= 32'd0; lcur <= 8'hFF; first <= 1'b1;
            a0_r <= 8'd0; a1_r <= 8'd0; a2_r <= 8'd0; a3_r <= 8'd0;
            s0_r <= 8'd0; s1_r <= 8'd0; s2_r <= 8'd0; s3_r <= 8'd0; v1 <= 1'b0;
        end else begin
            v1 <= step;
            if (step) begin
                acc <= acc_next; lcur <= lcur_next; first <= 1'b0;
                a0_r <= p0[31:24]; a1_r <= p1[31:24]; a2_r <= p2[31:24]; a3_r <= p3[31:24];
                s0_r <= word[7:0]; s1_r <= word[15:8]; s2_r <= word[23:16]; s3_r <= word[31:24];
            end
        end
    end

    // ---------------- stage 1: table lookup (quadrant logic as nco_400m_enhanced) ----------------
    function signed [15:0] nco_sin;
        input [7:0] addr;
        reg [15:0] la, lb;
        begin
            la = sin_lut[addr[5:0]]; lb = sin_lut[7'd64 - {1'b0, addr[5:0]}];
            case (addr[7:6])
                2'b00: nco_sin =  $signed({1'b0, la[14:0]});
                2'b01: nco_sin =  $signed({1'b0, lb[14:0]});
                2'b10: nco_sin = -$signed({1'b0, la[14:0]});
                default: nco_sin = -$signed({1'b0, lb[14:0]});
            endcase
        end
    endfunction
    function signed [15:0] nco_cos;
        input [7:0] addr;
        reg [15:0] la, lb;
        begin
            la = sin_lut[addr[5:0]]; lb = sin_lut[7'd64 - {1'b0, addr[5:0]}];
            case (addr[7:6])
                2'b00: nco_cos =  $signed({1'b0, lb[14:0]});
                2'b01: nco_cos = -$signed({1'b0, la[14:0]});
                2'b10: nco_cos = -$signed({1'b0, lb[14:0]});
                default: nco_cos =  $signed({1'b0, la[14:0]});
            endcase
        end
    endfunction

    reg signed [15:0] c0, c1, c2, c3, n0, n1, n2, n3;   // cos / sin per phase
    reg signed [8:0]  x0, x1, x2, x3;                   // 2*adc - 255
    reg               v2;
    reg               byp_r;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            c0 <= 0; c1 <= 0; c2 <= 0; c3 <= 0; n0 <= 0; n1 <= 0; n2 <= 0; n3 <= 0;
            x0 <= 0; x1 <= 0; x2 <= 0; x3 <= 0; v2 <= 1'b0; byp_r <= 1'b0;
        end else begin
            v2 <= v1; byp_r <= bypass_mode;
            c0 <= nco_cos(a0_r); c1 <= nco_cos(a1_r); c2 <= nco_cos(a2_r); c3 <= nco_cos(a3_r);
            n0 <= nco_sin(a0_r); n1 <= nco_sin(a1_r); n2 <= nco_sin(a2_r); n3 <= nco_sin(a3_r);
            x0 <= $signed({1'b0, s0_r, 1'b0}) - 9'sd255;
            x1 <= $signed({1'b0, s1_r, 1'b0}) - 9'sd255;
            x2 <= $signed({1'b0, s2_r, 1'b0}) - 9'sd255;
            x3 <= $signed({1'b0, s3_r, 1'b0}) - 9'sd255;
        end
    end

    // ---------------- stage 2: mixers (9 x 16 -> 25 bits, >>> 8 -> 17 bits) ----------------
    wire signed [15:0] cc0 = byp_r ? 16'sh7FFF : c0, cc1 = byp_r ? 16'sh7FFF : c1,
                       cc2 = byp_r ? 16'sh7FFF : c2, cc3 = byp_r ? 16'sh7FFF : c3;
    wire signed [15:0] nn0 = byp_r ? 16'sh0000 : n0, nn1 = byp_r ? 16'sh0000 : n1,
                       nn2 = byp_r ? 16'sh0000 : n2, nn3 = byp_r ? 16'sh0000 : n3;
    wire signed [24:0] pi0 = x0 * cc0, pi1 = x1 * cc1, pi2 = x2 * cc2, pi3 = x3 * cc3;
    wire signed [24:0] pq0 = x0 * nn0, pq1 = x1 * nn1, pq2 = x2 * nn2, pq3 = x3 * nn3;
    reg  signed [17:0] mi [0:19];   // mixed I history, [19] newest (slot 4m+3)
    reg  signed [17:0] mq [0:19];
    reg                v3;
    integer k;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            for (k = 0; k < 20; k = k + 1) begin mi[k] <= 18'sd0; mq[k] <= 18'sd0; end
            v3 <= 1'b0;
        end else begin
            v3 <= v2;
            if (v2) begin
                for (k = 0; k < 16; k = k + 1) begin mi[k] <= mi[k+4]; mq[k] <= mq[k+4]; end
                mi[16] <= pi0 >>> 8; mi[17] <= pi1 >>> 8; mi[18] <= pi2 >>> 8; mi[19] <= pi3 >>> 8;
                mq[16] <= pq0 >>> 8; mq[17] <= pq1 >>> 8; mq[18] <= pq2 >>> 8; mq[19] <= pq3 >>> 8;
            end
        end
    end

    // ---------------- stage 3/4: CIC as 16-tap FIR, two pipeline stages ----------------
    // y = sum h[k] * x[N - k] with N = 16 + CIC_PHASE (index into the 20-sample history, 19 = newest)
    localparam NP = 16 + CIC_PHASE;
    function signed [35:0] cic_part;    // 8 taps
        input signed [17:0] a0, a1, a2, a3, a4, a5, a6, a7;   // a0 = newest of the group
        input integer which;             // 0: taps 0..7, 1: taps 8..15
        begin
            if (which == 0)
                cic_part = a0 * 36'sd1 + a1 * 36'sd5 + a2 * 36'sd15 + a3 * 36'sd35 + a4 * 36'sd65 + a5 * 36'sd101 + a6 * 36'sd135 + a7 * 36'sd155;
            else
                cic_part = a0 * 36'sd155 + a1 * 36'sd135 + a2 * 36'sd101 + a3 * 36'sd65 + a4 * 36'sd35 + a5 * 36'sd15 + a6 * 36'sd5 + a7 * 36'sd1;
        end
    endfunction
    reg signed [35:0] si_hi, si_lo, sq_hi, sq_lo;
    reg               v4;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin si_hi <= 0; si_lo <= 0; sq_hi <= 0; sq_lo <= 0; v4 <= 1'b0; end
        else begin
            v4 <= v3;
            si_hi <= cic_part(mi[NP], mi[NP-1], mi[NP-2], mi[NP-3], mi[NP-4], mi[NP-5], mi[NP-6], mi[NP-7], 0);
            si_lo <= cic_part(mi[NP-8], mi[NP-9], mi[NP-10], mi[NP-11], mi[NP-12], mi[NP-13], mi[NP-14], mi[NP-15], 1);
            sq_hi <= cic_part(mq[NP], mq[NP-1], mq[NP-2], mq[NP-3], mq[NP-4], mq[NP-5], mq[NP-6], mq[NP-7], 0);
            sq_lo <= cic_part(mq[NP-8], mq[NP-9], mq[NP-10], mq[NP-11], mq[NP-12], mq[NP-13], mq[NP-14], mq[NP-15], 1);
        end
    end
    wire signed [35:0] sum_i = si_hi + si_lo;
    wire signed [35:0] sum_q = sq_hi + sq_lo;
    wire signed [35:0] sc_i = sum_i >>> 10;
    wire signed [35:0] sc_q = sum_q >>> 10;
    function signed [17:0] sat18;
        input signed [35:0] v;
        begin
            if (v > 36'sd131071)       sat18 = 18'sd131071;
            else if (v < -36'sd131072) sat18 = -18'sd131072;
            else                       sat18 = v[17:0];
        end
    endfunction
    reg signed [17:0] cic_i, cic_q;
    reg               cic_v;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin cic_i <= 18'sd0; cic_q <= 18'sd0; cic_v <= 1'b0; end
        else begin cic_v <= v4; if (v4) begin cic_i <= sat18(sc_i); cic_q <= sat18(sc_q); end end
    end
    assign cic_i_dbg = cic_i;
    assign cic_q_dbg = cic_q;
    assign cic_valid_dbg = cic_v;

    // ---------------- FIR (unchanged modules) + output stage ----------------
    wire signed [17:0] fir_i_out, fir_q_out;
    wire fir_valid_i, fir_valid_q;
    fir_lowpass_parallel_enhanced fir_i_inst (
        .clk(clk), .reset_n(reset_n), .data_in(cic_i), .data_valid(cic_v),
        .data_out(fir_i_out), .data_out_valid(fir_valid_i), .fir_ready(), .filter_overflow());
    fir_lowpass_parallel_enhanced fir_q_inst (
        .clk(clk), .reset_n(reset_n), .data_in(cic_q), .data_valid(cic_v),
        .data_out(fir_q_out), .data_out_valid(fir_valid_q), .fir_ready(), .filter_overflow());

    reg signed [17:0] bb_i, bb_q;
    reg bb_v;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin bb_i <= 18'sd0; bb_q <= 18'sd0; bb_v <= 1'b0; end
        else if (fir_valid_i & fir_valid_q) begin bb_i <= fir_i_out; bb_q <= fir_q_out; bb_v <= 1'b1; end
        else bb_v <= 1'b0;
    end
    assign baseband_i = bb_i;
    assign baseband_q = bb_q;
    assign baseband_valid_i = bb_v;
    assign baseband_valid_q = bb_v;
endmodule
