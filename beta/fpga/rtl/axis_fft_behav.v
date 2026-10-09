`timescale 1ns / 1ps
// ============================================================================
// axis_fft_behav.v  -  behavioural AXI4-Stream FFT, simulation-correct model
// of the Xilinx FFT IP (xfft v9.1) as used by xfft_32.v and FFT_enhanced.v.
// BETA - SIMULATION ONLY (uses real arithmetic; not synthesisable).
//
// Modelled behaviour
//   * Frame of N complex samples on s_axis_data ({Q[DATA_W-1:0], I[DATA_W-1:0]},
//     two's complement); tlast on the last sample (an early tlast zero-fills
//     the rest of the frame, a missing tlast is ignored - the IP would flag
//     event_tlast_* errors).
//   * s_axis_config_tdata, latched when accepted (tready = 1 always) and
//     applied to the NEXT frame that starts, Xilinx style:
//        bit 0            FWD_INV   1 = forward (exp(-j...)), 0 = inverse (exp(+j...), NO 1/N)
//        bits [1 +: SCHW] SCALE_SCH scaling schedule, 2 bits per radix-4 stage
//                         (first stage in the LSBs) and 1 bit for a final
//                         radix-2 stage when log2(N) is odd. The model applies
//                         the TOTAL shift (sum of all fields) once at the end
//                         with round-half-up and saturation; the IP scales and
//                         rounds per stage, so results are not bit-exact (+/- a
//                         few LSB) - the testbench compares with a tolerance.
//   * Output: N samples, natural order, back-to-back, m_axis_data_tvalid with
//     tlast on the last, LATENCY clocks after the last input sample was
//     accepted. m_axis_data_tready is honoured (output stalls). Up to QUEUE
//     frames may be in flight (s_axis_data_tready drops when the queue is
//     full).
//   * tuser (XK_INDEX, BLK_EXP, OVFLO) is not modelled.
// ============================================================================
module axis_fft_behav #(
    parameter N       = 32,
    parameter LOG2N   = 5,
    parameter DATA_W  = 16,
    parameter CFG_W   = 8,
    parameter LATENCY = 64,
    parameter QUEUE   = 4
) (
    input  wire                 aclk,
    input  wire                 aresetn,
    input  wire [CFG_W-1:0]     s_axis_config_tdata,
    input  wire                 s_axis_config_tvalid,
    output wire                 s_axis_config_tready,
    input  wire [2*DATA_W-1:0]  s_axis_data_tdata,
    input  wire                 s_axis_data_tvalid,
    output wire                 s_axis_data_tready,
    input  wire                 s_axis_data_tlast,
    output reg  [2*DATA_W-1:0]  m_axis_data_tdata,
    output reg                  m_axis_data_tvalid,
    output reg                  m_axis_data_tlast,
    input  wire                 m_axis_data_tready
);
    /* verilator lint_off BLKSEQ */
    /* verilator lint_off REALCVT */
    /* verilator lint_off WIDTHEXPAND */
    /* verilator lint_off WIDTHTRUNC */
    localparam R4_STAGES = LOG2N / 2;
    localparam HAS_R2    = LOG2N % 2;
    localparam SCHW      = 2 * R4_STAGES + HAS_R2;

    // frame storage (time domain in, frequency domain out, in place)
    real  fr_re [0:QUEUE*N-1];
    real  fr_im [0:QUEUE*N-1];
    reg  [CFG_W-1:0] fr_cfg   [0:QUEUE-1];
    reg              fr_ready [0:QUEUE-1];   // computed, waiting for output
    integer          fr_time  [0:QUEUE-1];   // cycle at which output may start

    integer wr_frame, rd_frame, wr_idx, out_idx, n_frames, cycle;
    reg [CFG_W-1:0] cfg_pending;

    assign s_axis_config_tready = 1'b1;
    assign s_axis_data_tready   = (n_frames < QUEUE);

    // ---------------- helpers ----------------
    function real to_real;      // two's complement -> real
        input [DATA_W-1:0] v;
        begin
            if (v[DATA_W-1]) to_real = -$itor({1'b0, (~v) + 1'b1} & ((1 << DATA_W) - 1));
            else             to_real =  $itor(v);
        end
    endfunction

    function [DATA_W-1:0] to_fixed;  // real -> round-half-up, saturate
        input real x;
        real r;
        integer iv;
        begin
            r = $floor(x + 0.5);
            if (r >  (2.0 ** (DATA_W-1)) - 1.0) r =  (2.0 ** (DATA_W-1)) - 1.0;
            if (r < -(2.0 ** (DATA_W-1)))       r = -(2.0 ** (DATA_W-1));
            iv = $rtoi(r);
            to_fixed = iv[DATA_W-1:0];
        end
    endfunction

    function integer total_shift;    // decode the scaling schedule
        input [CFG_W-1:0] cfg;
        integer k, s;
        begin
            s = 0;
            for (k = 0; k < R4_STAGES; k = k + 1)
                s = s + cfg[1 + 2*k +: 2];
            if (HAS_R2 != 0)
                s = s + cfg[1 + 2*R4_STAGES];
            total_shift = s;
        end
    endfunction

    // in-place iterative radix-2 FFT of frame f (bit-reversal + butterflies)
    task compute_frame;
        input integer f;
        integer base, i, j, bitmask, len, half, k, p, q, sh;
        real tr, ti, wr, wi, ur, ui, ang, sgn, scale;
        reg [CFG_W-1:0] cfg;
        begin
            base = f * N;
            cfg  = fr_cfg[f];
            sgn  = cfg[0] ? -1.0 : 1.0;       // forward: exp(-j), inverse: exp(+j)
            // bit reversal permutation
            j = 0;
            for (i = 0; i < N - 1; i = i + 1) begin
                if (i < j) begin
                    tr = fr_re[base+i]; fr_re[base+i] = fr_re[base+j]; fr_re[base+j] = tr;
                    ti = fr_im[base+i]; fr_im[base+i] = fr_im[base+j]; fr_im[base+j] = ti;
                end
                bitmask = N >> 1;
                while (bitmask > 0 && (j & bitmask) != 0) begin
                    j = j ^ bitmask;
                    bitmask = bitmask >> 1;
                end
                j = j | bitmask;
            end
            // butterflies
            len = 2;
            while (len <= N) begin
                half = len / 2;
                for (i = 0; i < N; i = i + len) begin
                    for (k = 0; k < half; k = k + 1) begin
                        ang = sgn * 2.0 * 3.14159265358979323846 * k / len;
                        wr = $cos(ang); wi = $sin(ang);
                        p = base + i + k; q = p + half;
                        ur = fr_re[q] * wr - fr_im[q] * wi;
                        ui = fr_re[q] * wi + fr_im[q] * wr;
                        fr_re[q] = fr_re[p] - ur; fr_im[q] = fr_im[p] - ui;
                        fr_re[p] = fr_re[p] + ur; fr_im[p] = fr_im[p] + ui;
                    end
                end
                len = len * 2;
            end
            // scaling schedule (total shift) + rounding happens at output time via to_fixed
            sh = total_shift(cfg);
            scale = 1.0 / (2.0 ** sh);
            for (i = 0; i < N; i = i + 1) begin
                fr_re[base+i] = fr_re[base+i] * scale;
                fr_im[base+i] = fr_im[base+i] * scale;
            end
        end
    endtask

    integer ii;
    initial begin
        wr_frame = 0; rd_frame = 0; wr_idx = 0; out_idx = 0; n_frames = 0; cycle = 0;
        cfg_pending = {CFG_W{1'b0}};
        for (ii = 0; ii < QUEUE; ii = ii + 1) begin fr_ready[ii] = 1'b0; fr_time[ii] = 0; fr_cfg[ii] = 0; end
        for (ii = 0; ii < QUEUE*N; ii = ii + 1) begin fr_re[ii] = 0.0; fr_im[ii] = 0.0; end
    end

    // ---------------- input side ----------------
    always @(posedge aclk) begin
        cycle = cycle + 1;
        if (!aresetn) begin
            wr_frame = 0; rd_frame = 0; wr_idx = 0; out_idx = 0; n_frames = 0;
            cfg_pending = {CFG_W{1'b0}};
            for (ii = 0; ii < QUEUE; ii = ii + 1) fr_ready[ii] = 1'b0;
            m_axis_data_tvalid <= 1'b0;
            m_axis_data_tlast  <= 1'b0;
            m_axis_data_tdata  <= {(2*DATA_W){1'b0}};
        end else begin
            if (s_axis_config_tvalid && s_axis_config_tready)
                cfg_pending = s_axis_config_tdata;

            if (s_axis_data_tvalid && s_axis_data_tready) begin
                if (wr_idx == 0) fr_cfg[wr_frame] = cfg_pending;
                fr_re[wr_frame*N + wr_idx] = to_real(s_axis_data_tdata[DATA_W-1:0]);
                fr_im[wr_frame*N + wr_idx] = to_real(s_axis_data_tdata[2*DATA_W-1:DATA_W]);
                if (wr_idx == N - 1 || s_axis_data_tlast) begin
                    for (ii = wr_idx + 1; ii < N; ii = ii + 1) begin   // early tlast: zero fill
                        fr_re[wr_frame*N + ii] = 0.0;
                        fr_im[wr_frame*N + ii] = 0.0;
                    end
                    compute_frame(wr_frame);
                    fr_time[wr_frame]  = cycle + LATENCY;
                    fr_ready[wr_frame] = 1'b1;
                    n_frames = n_frames + 1;
                    wr_frame = (wr_frame + 1) % QUEUE;
                    wr_idx = 0;
                end else begin
                    wr_idx = wr_idx + 1;
                end
            end

            // ---------------- output side ----------------
            if (!m_axis_data_tvalid || m_axis_data_tready) begin
                if (fr_ready[rd_frame] && cycle >= fr_time[rd_frame]) begin
                    m_axis_data_tdata  <= {to_fixed(fr_im[rd_frame*N + out_idx]), to_fixed(fr_re[rd_frame*N + out_idx])};
                    m_axis_data_tvalid <= 1'b1;
                    m_axis_data_tlast  <= (out_idx == N - 1);
                    if (out_idx == N - 1) begin
                        out_idx = 0;
                        fr_ready[rd_frame] = 1'b0;
                        rd_frame = (rd_frame + 1) % QUEUE;
                        n_frames = n_frames - 1;
                    end else begin
                        out_idx = out_idx + 1;
                    end
                end else begin
                    m_axis_data_tvalid <= 1'b0;
                    m_axis_data_tlast  <= 1'b0;
                end
            end
        end
    end
    /* verilator lint_on WIDTHTRUNC */
    /* verilator lint_on WIDTHEXPAND */
    /* verilator lint_on REALCVT */
    /* verilator lint_on BLKSEQ */
endmodule
