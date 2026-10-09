`timescale 1ns / 1ps
// ============================================================================
// matched_filter_multi_segment.v  -  block collector / segment sequencer for the
// pulse-compression chain.  BETA rewrite of
// 9_Firmware/9_2_FPGA/matched_filter_multi_segment.v (module name, state names,
// parameters and port list kept; see CHANGELOG.md for every difference).
//
// Behaviour (as in the original): after a chirp-start pulse (mc_new_chirp) the
// DDC samples are collected into a 1024-sample block; when the block is full
// the reference segment is requested from the chirp memory and the block is
// streamed into matched_filter_processing_chain; for the long chirp the next
// block starts SEGMENT_ADVANCE (896) samples after the previous one (128
// samples overlap), up to LONG_SEGMENTS blocks or until LONG_CHIRP_SAMPLES
// have been collected; the short chirp is one block zero-padded after 50
// samples. Samples that arrive while the FSM is not in ST_COLLECT_DATA are
// NOT stored (original behaviour; see README "Known limitations").
//
// Differences from the original:
//   * input buffer is a circular RAM (one write port, one read port, BRAM
//     inferable) and the 128-sample overlap is a pointer move; the original
//     copied 128 entries per cycle with a for-loop (:329-332), which forces
//     2 x 1024 x 16 flip-flops.
//   * the first block waits for a full 1024 samples (the original processed
//     after 896 with an unwritten tail, :199).
//   * the reference is fetched by the processing chain at FFT-output time
//     (ref_addr = {segment, bin}); mem_request is asserted for the priming
//     handshake (ST_WAIT_REF) and for every chain request. The chain's
//     segment_in and use_long_chirp ports are driven from here.
//   * all $display messages are gated by the DEBUG parameter (default 0).
// ============================================================================
module matched_filter_multi_segment (
    input wire clk,           // 100MHz
    input wire reset_n,

    // Input from DDC (100 MSPS)
    input wire signed [17:0] ddc_i,
    input wire signed [17:0] ddc_q,
    input wire ddc_valid,

    // Chirp control (from sequence controller)
    input wire use_long_chirp,
    input wire [5:0] chirp_counter,

    // Microcontroller sync signals (level or pulse; rising edge starts a chirp)
    input wire mc_new_chirp,
    input wire mc_new_elevation,
    input wire mc_new_azimuth,

    input wire [15:0] long_chirp_real,
    input wire [15:0] long_chirp_imag,
    input wire [15:0] short_chirp_real,
    input wire [15:0] short_chirp_imag,

    // Memory system interface
    output wire [1:0] segment_request,
    output wire [9:0] sample_addr_out,  // Tell memory which sample we need
    output wire mem_request,
    input wire mem_ready,

    // Output: Pulse compressed
    output wire signed [15:0] pc_i_w,
    output wire signed [15:0] pc_q_w,
    output wire pc_valid_w,

    // Status
    output reg [3:0] status
);

// ========== PARAMETERS ==========
parameter BUFFER_SIZE = 1024;
parameter LONG_CHIRP_SAMPLES = 3000;  // 30 us at 100 MSPS
parameter SHORT_CHIRP_SAMPLES = 50;   // 0.5 us at 100 MSPS
parameter OVERLAP_SAMPLES = 128;
parameter SEGMENT_ADVANCE = BUFFER_SIZE - OVERLAP_SAMPLES;  // 896 samples
parameter DEBUG = 0;
parameter LONG_SEGMENTS = 4;          // chirp_memory_loader_param holds 4 segments (seg3 = zeros)
parameter SHORT_SEGMENTS = 1;

localparam [2:0] LONG_SEG_W  = LONG_SEGMENTS;
localparam [2:0] SHORT_SEG_W = SHORT_SEGMENTS;

// ========== INPUT BUFFER (circular, BRAM) ==========
(* ram_style = "block" *) reg signed [15:0] input_buffer_i [0:BUFFER_SIZE-1];
(* ram_style = "block" *) reg signed [15:0] input_buffer_q [0:BUFFER_SIZE-1];
reg  [9:0]  wr_ptr;          // next write position (mod 1024)
reg  [9:0]  blk_start;       // first sample of the block being collected / processed
reg  [10:0] new_cnt;         // samples written since blk_start (0..1024)
reg  [10:0] rd_cnt;          // samples streamed to the chain (0..1024)
wire [9:0]  rd_addr = blk_start + rd_cnt[9:0];
reg  [15:0] chirp_samples_collected;

// State machine
reg [3:0] state;
localparam ST_IDLE = 0;
localparam ST_COLLECT_DATA = 1;
localparam ST_ZERO_PAD = 2;
localparam ST_WAIT_REF = 3;
localparam ST_PROCESSING = 4;
localparam ST_WAIT_FFT = 5;
localparam ST_OUTPUT = 6;
localparam ST_NEXT_SEGMENT = 7;

// Segment tracking
reg [2:0] current_segment;
reg [2:0] total_segments;
reg chirp_complete;

// Microcontroller sync detection
reg mc_new_chirp_prev, mc_new_elevation_prev, mc_new_azimuth_prev;
wire chirp_start_pulse = mc_new_chirp && !mc_new_chirp_prev;
/* verilator lint_off UNUSEDSIGNAL */
wire elevation_change_pulse = mc_new_elevation && !mc_new_elevation_prev;  // not used by the FSM (original)
wire azimuth_change_pulse   = mc_new_azimuth && !mc_new_azimuth_prev;
wire unused_sig = elevation_change_pulse | azimuth_change_pulse;
/* verilator lint_on UNUSEDSIGNAL */

// Processing chain signals
wire [15:0] fft_pc_i, fft_pc_q;
wire fft_pc_valid;
wire [3:0] fft_chain_state;
wire [11:0] chain_ref_addr;
wire chain_ref_req;

reg [15:0] fft_input_i, fft_input_q;
reg fft_input_valid;
reg fsm_mem_request;

// ========== MEMORY INTERFACE MUX ==========
assign mem_request     = fsm_mem_request | chain_ref_req;
assign segment_request = chain_ref_req ? chain_ref_addr[11:10] : current_segment[1:0];
assign sample_addr_out = chain_ref_req ? chain_ref_addr[9:0]   : 10'd0;

// ========== MICROCONTROLLER SYNC ==========
always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        mc_new_chirp_prev <= 1'b0;
        mc_new_elevation_prev <= 1'b0;
        mc_new_azimuth_prev <= 1'b0;
    end else begin
        mc_new_chirp_prev <= mc_new_chirp;
        mc_new_elevation_prev <= mc_new_elevation;
        mc_new_azimuth_prev <= mc_new_azimuth;
    end
end

// ========== BUFFER INITIALIZATION (simulation; BRAM powers up zero) ==========
integer buf_init;
initial begin
    for (buf_init = 0; buf_init < BUFFER_SIZE; buf_init = buf_init + 1) begin
        input_buffer_i[buf_init] = 16'd0;
        input_buffer_q[buf_init] = 16'd0;
    end
end

// ========== BUFFER WRITE PORT ==========
wire        buf_we   = (state == ST_COLLECT_DATA && ddc_valid) || (state == ST_ZERO_PAD);
wire [15:0] buf_wi   = (state == ST_ZERO_PAD) ? 16'd0 : (ddc_i[17:2] + {15'd0, ddc_i[1]});
wire [15:0] buf_wq   = (state == ST_ZERO_PAD) ? 16'd0 : (ddc_q[17:2] + {15'd0, ddc_q[1]});
always @(posedge clk) begin
    if (buf_we) begin
        input_buffer_i[wr_ptr] <= buf_wi;
        input_buffer_q[wr_ptr] <= buf_wq;
    end
end

// ========== STATE MACHINE ==========
always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        state <= ST_IDLE;
        wr_ptr <= 10'd0;
        blk_start <= 10'd0;
        new_cnt <= 11'd0;
        rd_cnt <= 11'd0;
        current_segment <= 3'd0;
        total_segments <= 3'd1;
        fsm_mem_request <= 1'b0;
        status <= 4'd0;
        chirp_samples_collected <= 16'd0;
        chirp_complete <= 1'b0;
        fft_input_valid <= 1'b0;
        fft_input_i <= 16'd0;
        fft_input_q <= 16'd0;
    end else begin
        fsm_mem_request <= 1'b0;
        fft_input_valid <= 1'b0;

        case (state)
            ST_IDLE: begin
                new_cnt <= 11'd0;
                rd_cnt <= 11'd0;
                current_segment <= 3'd0;
                chirp_samples_collected <= 16'd0;
                chirp_complete <= 1'b0;
                blk_start <= wr_ptr;
                if (chirp_start_pulse) begin
                    state <= ST_COLLECT_DATA;
                    total_segments <= use_long_chirp ? LONG_SEG_W : SHORT_SEG_W;
                    if (DEBUG) $display("[MULTI_SEG] Starting %s chirp, segments: %0d",
                                        use_long_chirp ? "LONG" : "SHORT",
                                        use_long_chirp ? LONG_SEGMENTS : SHORT_SEGMENTS);
                end
            end

            ST_COLLECT_DATA: begin
                if (ddc_valid) begin
                    wr_ptr <= wr_ptr + 10'd1;
                    new_cnt <= new_cnt + 11'd1;
                    chirp_samples_collected <= chirp_samples_collected + 16'd1;

                    if (use_long_chirp) begin
                        if (new_cnt == BUFFER_SIZE - 1) begin
                            state <= ST_WAIT_REF;
                            fsm_mem_request <= 1'b1;
                            if (DEBUG) $display("[MULTI_SEG] Segment %0d ready: %0d samples collected",
                                                current_segment, chirp_samples_collected + 1);
                        end
                        if (chirp_samples_collected >= LONG_CHIRP_SAMPLES - 1) begin
                            chirp_complete <= 1'b1;
                        end
                    end else begin
                        if (chirp_samples_collected >= SHORT_CHIRP_SAMPLES - 1) begin
                            state <= ST_ZERO_PAD;
                            chirp_complete <= 1'b1;
                        end
                    end
                end
            end

            ST_ZERO_PAD: begin
                wr_ptr <= wr_ptr + 10'd1;
                new_cnt <= new_cnt + 11'd1;
                if (new_cnt == BUFFER_SIZE - 1) begin
                    state <= ST_WAIT_REF;
                    fsm_mem_request <= 1'b1;
                    if (DEBUG) $display("[MULTI_SEG] Zero-pad complete, buffer full");
                end
            end

            ST_WAIT_REF: begin
                if (mem_ready) begin
                    rd_cnt <= 11'd0;
                    state <= ST_PROCESSING;
                    if (DEBUG) $display("[MULTI_SEG] Reference ready, processing segment %0d", current_segment);
                end
            end

            ST_PROCESSING: begin
                if (rd_cnt < BUFFER_SIZE) begin
                    fft_input_i <= input_buffer_i[rd_addr];
                    fft_input_q <= input_buffer_q[rd_addr];
                    fft_input_valid <= 1'b1;
                    rd_cnt <= rd_cnt + 11'd1;
                end else begin
                    state <= ST_WAIT_FFT;
                    if (DEBUG) $display("[MULTI_SEG] Finished feeding %0d samples to FFT, waiting...", BUFFER_SIZE);
                end
            end

            ST_WAIT_FFT: begin
                if (fft_pc_valid) begin
                    state <= ST_OUTPUT;
                    if (DEBUG) $display("[MULTI_SEG] FFT processing complete for segment %0d", current_segment);
                end
            end

            ST_OUTPUT: begin
                if (current_segment < total_segments - 1 || !chirp_complete) begin
                    state <= ST_NEXT_SEGMENT;
                end else begin
                    state <= ST_IDLE;
                    if (DEBUG) $display("[MULTI_SEG] All %0d segments complete", total_segments);
                end
            end

            ST_NEXT_SEGMENT: begin
                current_segment <= current_segment + 3'd1;
                if (use_long_chirp) begin
                    // overlap-save: keep the last OVERLAP_SAMPLES, i.e. the next block starts
                    // SEGMENT_ADVANCE after the previous one
                    blk_start <= blk_start + SEGMENT_ADVANCE[9:0];
                    new_cnt <= OVERLAP_SAMPLES[10:0];
                end else begin
                    blk_start <= wr_ptr;
                    new_cnt <= 11'd0;
                end
                if (!chirp_complete) begin
                    state <= ST_COLLECT_DATA;
                    if (DEBUG) $display("[MULTI_SEG] Starting segment %0d/%0d", current_segment + 1, total_segments);
                end else begin
                    state <= ST_IDLE;
                end
            end

            default: state <= ST_IDLE;
        endcase

        status <= {state[2:0], use_long_chirp};
    end
end

// ========== PROCESSING CHAIN INSTANTIATION ==========
matched_filter_processing_chain m_f_p_c (
    .clk(clk),
    .reset_n(reset_n),
    .adc_data_i(fft_input_i),
    .adc_data_q(fft_input_q),
    .adc_valid(fft_input_valid),
    .segment_in(current_segment[1:0]),
    .chirp_counter(chirp_counter),
    .use_long_chirp(use_long_chirp),
    .ref_addr(chain_ref_addr),
    .ref_req(chain_ref_req),
    .long_chirp_real(long_chirp_real),
    .long_chirp_imag(long_chirp_imag),
    .short_chirp_real(short_chirp_real),
    .short_chirp_imag(short_chirp_imag),
    .range_profile_i(fft_pc_i),
    .range_profile_q(fft_pc_q),
    .range_profile_valid(fft_pc_valid),
    .chain_state(fft_chain_state)
);

/* verilator lint_off UNUSEDSIGNAL */
wire [3:0] unused_chain_state = fft_chain_state;
/* verilator lint_on UNUSEDSIGNAL */

// ========== OUTPUT CONNECTIONS ==========
assign pc_i_w = fft_pc_i;
assign pc_q_w = fft_pc_q;
assign pc_valid_w = fft_pc_valid;

endmodule
