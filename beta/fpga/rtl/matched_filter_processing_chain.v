`timescale 1ns / 1ps
// ============================================================================
// matched_filter_processing_chain.v  -  frequency-domain pulse compression of
// one 1024-sample block.  BETA.
//
// Instantiated by matched_filter_multi_segment.v:361-386 but missing from the
// repository. The repository evidence fixes the architecture:
//   * the reference memories long_chirp_seg*_{i,q}.mem are FREQUENCY-domain
//     (conj(FFT) of 1024-sample chirp segments, see gen_chirp_mem.py),
//   * frequency_matched_filter.v multiplies an FFT output by the conjugate of
//     a reference "assumed to be FFT of transmitted chirp" (:13),
//   * fft_1024_forward.v / fft_1024_inverse.v were orphans wrapping the same
//     1024-point FFT IP (FFT_enhanced) with run-time direction.
// This module therefore composes those three blocks:
//
//   adc_data_i/q ──► FFT_1024 (forward) ──► × conj(REF[k]) ──► FFT_1024 (inverse) ──► range_profile_i/q
//                                            ▲
//                       chirp memory ◄── ref_addr = {segment, k} (this module drives the address)
//
// Reference addressing: instead of streaming the reference during the input
// phase and re-aligning it with a fixed 3187-cycle delay line
// (latency_buffer_2159.v, which would have to match the exact IP latency), the
// chain requests bin k of the frame's segment when FFT output bin k appears
// and compensates the memory's one-cycle read latency with a one-stage
// pipeline on the FFT output. This works for any FFT latency (behavioural
// model or Xilinx IP) and for frames back to back; the segment index of each
// frame is queued (depth 4) at frame start.
//
// Fixed-point: forward FFT scaled by 2^-FWD_SHIFT (parameter of the wrapper),
// complex multiply Q15xQ15 -> Q15 with saturation (frequency_matched_filter),
// inverse FFT scaled by 2^-INV_SHIFT. Defaults (6 and 5) keep a full-scale
// 16-bit chirp input below saturation; see ip/README.md for the IP scaling
// schedule that realises the same shifts.
//
// Interface note (vs. the inferred port list): segment_in, use_long_chirp,
// ref_addr and ref_req were added; chirp_counter is kept for compatibility and
// only exported in chain_state[3].
// ============================================================================
module matched_filter_processing_chain #(
    parameter [9:0] FWD_SCALE_SCH = 10'h255,   // 1,1,1,1,2 bits per stage (LSB first) = 2^-6
    parameter [9:0] INV_SCALE_SCH = 10'h155    // 1,1,1,1,1 bits per stage            = 2^-5
) (
    input  wire        clk,
    input  wire        reset_n,
    // input block (1024 samples, adc_valid for each)
    input  wire [15:0] adc_data_i,
    input  wire [15:0] adc_data_q,
    input  wire        adc_valid,
    input  wire [1:0]  segment_in,        // reference segment for the block being fed
    // chirp selection
    input  wire [5:0]  chirp_counter,     // informational only (exported in chain_state)
    input  wire        use_long_chirp,    // 1: long-chirp memory, 0: short-chirp memory
    // reference memory interface (registered read, data valid 1 clk after ref_req)
    output wire [11:0] ref_addr,          // {segment[1:0], bin[9:0]}
    output wire        ref_req,
    input  wire [15:0] long_chirp_real,
    input  wire [15:0] long_chirp_imag,
    input  wire [15:0] short_chirp_real,
    input  wire [15:0] short_chirp_imag,
    // output: pulse-compressed block (1024 samples)
    output wire [15:0] range_profile_i,
    output wire [15:0] range_profile_q,
    output wire        range_profile_valid,
    // status
    output wire [3:0]  chain_state
);
    // ---------------- segment queue (one entry per frame in flight) ----------------
    reg [9:0] in_count;
    reg [1:0] seg_q [0:3];
    reg [1:0] seg_wr, seg_rd;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            in_count <= 10'd0;
            seg_wr   <= 2'd0;
        end else if (adc_valid) begin
            if (in_count == 10'd0)
                seg_wr <= seg_wr + 2'd1;
            in_count <= in_count + 10'd1;   // wraps at 1024 = frame length
        end
    end
    always @(posedge clk) begin
        if (adc_valid && in_count == 10'd0)
            seg_q[seg_wr] <= segment_in;
    end

    // ---------------- forward FFT ----------------
    wire [15:0] fft_i, fft_q;
    wire        fft_valid;

    fft_1024_forward_enhanced #(.SCALE_SCH(FWD_SCALE_SCH)) u_fft_fwd (
        .clk        (clk),
        .reset_n    (reset_n),
        .data_i     (adc_data_i),
        .data_q     (adc_data_q),
        .data_valid (adc_valid),
        .fft_i      (fft_i),
        .fft_q      (fft_q),
        .fft_valid  (fft_valid)
    );

    // ---------------- reference addressing ----------------
    reg [9:0] out_count;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            out_count <= 10'd0;
            seg_rd    <= 2'd0;
        end else if (fft_valid) begin
            out_count <= out_count + 10'd1;
            if (out_count == 10'd1023)
                seg_rd <= seg_rd + 2'd1;
        end
    end

    assign ref_addr = {seg_q[seg_rd], out_count};
    assign ref_req  = fft_valid;

    // one-cycle delay of the FFT output to meet the memory read latency
    reg [15:0] fft_i_d, fft_q_d;
    reg        fft_valid_d;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            fft_i_d     <= 16'd0;
            fft_q_d     <= 16'd0;
            fft_valid_d <= 1'b0;
        end else begin
            fft_i_d     <= fft_i;
            fft_q_d     <= fft_q;
            fft_valid_d <= fft_valid;
        end
    end

    wire [15:0] ref_re = use_long_chirp ? long_chirp_real : short_chirp_real;
    wire [15:0] ref_im = use_long_chirp ? long_chirp_imag : short_chirp_imag;

    // ---------------- X(k) * conj(REF(k)) ----------------
    wire [15:0] fmf_re, fmf_im;
    wire        fmf_valid;

    frequency_matched_filter #(.CONJUGATE_REF(0)) u_fmf (   // memory already holds conj(FFT(ref))
        .clk            (clk),
        .reset_n        (reset_n),
        .fft_real_in    (fft_i_d),
        .fft_imag_in    (fft_q_d),
        .fft_valid_in   (fft_valid_d),
        .ref_chirp_real (ref_re),
        .ref_chirp_imag (ref_im),
        .filtered_real  (fmf_re),
        .filtered_imag  (fmf_im),
        .filtered_valid (fmf_valid),
        .state          ()
    );

    // ---------------- inverse FFT ----------------
    fft_1024_inverse_enhanced #(.SCALE_SCH(INV_SCALE_SCH)) u_fft_inv (
        .clk        (clk),
        .reset_n    (reset_n),
        .data_i     (fmf_re),
        .data_q     (fmf_im),
        .data_valid (fmf_valid),
        .ifft_i     (range_profile_i),
        .ifft_q     (range_profile_q),
        .ifft_valid (range_profile_valid)
    );

    assign chain_state = {chirp_counter[0], range_profile_valid, fft_valid, adc_valid};
endmodule
