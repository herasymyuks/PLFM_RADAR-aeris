`timescale 1ns / 1ps
// ============================================================================
// radar_receiver_final.v  -  receive chain: ADC capture -> DDC -> pulse
// compression -> range decimation -> Doppler FFT.
// BETA rewrite of 9_Firmware/9_2_FPGA/radar_receiver_final.v. Instance names
// and the chain order are those of the original (see
// engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot); every
// difference is listed in CHANGELOG.md. Summary of changes:
//   * control inputs that were undriven wires (use_long_chirp, chirp_counter,
//     mc_new_*; original :21-22, :204-208) are now ports driven by the top
//     level (register map + STM32 toggle lines); the receiver detects the
//     STM32 edges itself and keeps its own chirp counter (rx_chirp_counter).
//   * lvds_to_cmos_400m instance and the first cdc_adc_to_processing removed:
//     ad9484_lvds_to_cmos_400m provides the buffered DCO clock and the data
//     already synchronous to it (a second IBUFDS on the same pins is illegal).
//   * reset for the 400 MHz domain is synchronised (reset_synchronizer).
//   * latency_buffer_2159 removed (reference fetched by address in the chain).
//   * phantom ports .ref_i/.ref_q on mf_dual (:216-217) removed; declaration
//     order fixed (:150 vs :192); outputs changed from reg to wire (they are
//     driven by instance outputs).
//   * range profile exported (range_profile_out/valid/bin) for the host path.
//   * adc_pwdn driven from the register map; bypass/decimation controls added.
//   * debug $display blocks (:321-349) removed.
// ============================================================================
module radar_receiver_final #(
    parameter CHIRPS_PER_FRAME = 32
) (
    input  wire        clk,           // 100MHz
    input  wire        reset_n,

    // ADC Physical Interface (LVDS Inputs)
    input  wire [7:0]  adc_d_p,
    input  wire [7:0]  adc_d_n,
    input  wire        adc_dco_p,
    input  wire        adc_dco_n,
    output wire        adc_pwdn,

    // Control (BETA: were undriven internal wires)
    input  wire        stm32_new_chirp,       // raw STM32 toggle lines (asynchronous)
    input  wire        stm32_new_elevation,
    input  wire        stm32_new_azimuth,
    input  wire        use_long_chirp,        // register map
    input  wire        adc_pwdn_req,          // register map
    input  wire        ddc_bypass,            // register map (test)
    input  wire [1:0]  decimation_mode,       // register map
    input  wire [9:0]  start_bin,             // register map

    // Range profile (decimated, {Q,I}) - BETA export for the host path
    output wire [31:0] range_profile_out,
    output wire        range_profile_valid,
    output wire [5:0]  range_profile_bin,

    // Doppler outputs
    output wire [31:0] doppler_output,
    output wire        doppler_valid,
    output wire [4:0]  doppler_bin,
    output wire [5:0]  range_bin,

    // Status
    output wire [5:0]  rx_chirp_counter,
    output wire        new_chirp_frame,
    output wire        cdc_overflow
);

// ========== 1. ADC capture (400 MHz DCO domain) ==========
wire [7:0] adc_data_cmos;
wire       clk_400m;        // buffered ADC DCO
wire       adc_valid;

ad9484_lvds_to_cmos_400m adc (
    .adc_d_p       (adc_d_p),
    .adc_d_n       (adc_d_n),
    .adc_dco_p     (adc_dco_p),
    .adc_dco_n     (adc_dco_n),
    .reset_n       (reset_n),
    .pwdn_req      (adc_pwdn_req),
    .adc_data_cmos (adc_data_cmos),
    .adc_dco_cmos  (clk_400m),
    .adc_valid     (adc_valid),
    .adc_pwdn      (adc_pwdn)
);

wire reset_n_400m;
reset_synchronizer #(.STAGES(2)) rst_sync_400m (
    .clk           (clk_400m),
    .async_reset_n (reset_n),
    .sync_reset_n  (reset_n_400m)
);

// ========== 2. DDC ==========
wire signed [17:0] ddc_out_i, ddc_out_q;
wire ddc_valid_i, ddc_valid_q;

ddc_400m_enhanced ddc (
    .clk_400m          (clk_400m),
    .clk_100m          (clk),
    .reset_n           (reset_n),
    .reset_n_400m      (reset_n_400m),
    .mixers_enable     (1'b1),            // NCO always running (original)
    .adc_data          (adc_data_cmos),
    .adc_data_valid_i  (adc_valid),
    .adc_data_valid_q  (adc_valid),
    .baseband_i        (ddc_out_i),
    .baseband_q        (ddc_out_q),
    .baseband_valid_i  (ddc_valid_i),
    .baseband_valid_q  (ddc_valid_q),
    .ddc_status        (),
    .ddc_diagnostics   (),
    .mixer_saturation  (),
    .filter_overflow   (),
    .bypass_mode       (ddc_bypass),      // original tied 1'b1 (:126) to an unimplemented input
    .test_mode         (2'b00),
    .test_phase_inc    (16'h0000),
    .force_saturation  (1'b0),
    .reset_monitors    (1'b0),
    .debug_sample_count(),
    .debug_internal_i  (),
    .debug_internal_q  (),
    .cdc_overflow      (cdc_overflow)
);

wire signed [15:0] adc_i_scaled, adc_q_scaled;
wire adc_valid_sync;

ddc_input_interface ddc_if (
    .clk            (clk),
    .reset_n        (reset_n),
    .ddc_i          (ddc_out_i),
    .ddc_q          (ddc_out_q),
    .valid_i        (ddc_valid_i),
    .valid_q        (ddc_valid_q),
    .adc_i          (adc_i_scaled),
    .adc_q          (adc_q_scaled),
    .adc_valid      (adc_valid_sync),
    .data_sync_error()
);

// ========== 3. Chirp sequence tracking (BETA) ==========
wire new_chirp_pulse, new_elevation_pulse, new_azimuth_pulse;

edge_detector_enhanced rx_chirp_edge (
    .clk(clk), .reset_n(reset_n), .signal_in(stm32_new_chirp), .rising_falling_edge(new_chirp_pulse));
edge_detector_enhanced rx_elevation_edge (
    .clk(clk), .reset_n(reset_n), .signal_in(stm32_new_elevation), .rising_falling_edge(new_elevation_pulse));
edge_detector_enhanced rx_azimuth_edge (
    .clk(clk), .reset_n(reset_n), .signal_in(stm32_new_azimuth), .rising_falling_edge(new_azimuth_pulse));

reg [5:0] chirp_counter;
reg       new_frame_pulse;
always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        chirp_counter   <= 6'd0;
        new_frame_pulse <= 1'b0;
    end else begin
        new_frame_pulse <= 1'b0;
        if (new_chirp_pulse) begin
            // frame = CHIRPS_PER_FRAME chirps; pulse at the first chirp of each frame
            if (chirp_counter == 6'd0)
                new_frame_pulse <= 1'b1;
            if (chirp_counter == CHIRPS_PER_FRAME - 1)
                chirp_counter <= 6'd0;
            else
                chirp_counter <= chirp_counter + 6'd1;
        end
    end
end
assign rx_chirp_counter = chirp_counter;
assign new_chirp_frame  = new_frame_pulse;

// ========== 4. Chirp reference memory ==========
wire [1:0]  segment_request;
wire        mem_request;
wire [9:0]  sample_addr_from_chain;
wire [15:0] ref_i, ref_q;
wire        mem_ready;

chirp_memory_loader_param chirp_mem (
    .clk            (clk),
    .reset_n        (reset_n),
    .segment_select (segment_request),
    .mem_request    (mem_request),
    .use_long_chirp (use_long_chirp),
    .sample_addr    (sample_addr_from_chain),
    .ref_i          (ref_i),
    .ref_q          (ref_q),
    .mem_ready      (mem_ready)
);

// ========== 5. Pulse compression ==========
wire signed [15:0] range_profile_i, range_profile_q;
wire               range_valid;

matched_filter_multi_segment mf_dual (
    .clk              (clk),
    .reset_n          (reset_n),
    .ddc_i            ({adc_i_scaled, 2'b00}),   // x4 so that the [17:2] slice inside keeps all 16 bits
    .ddc_q            ({adc_q_scaled, 2'b00}),
    .ddc_valid        (adc_valid_sync),
    .use_long_chirp   (use_long_chirp),
    .chirp_counter    (chirp_counter),
    .mc_new_chirp     (new_chirp_pulse),
    .mc_new_elevation (new_elevation_pulse),
    .mc_new_azimuth   (new_azimuth_pulse),
    .long_chirp_real  (ref_i),      // the loader selects long/short internally
    .long_chirp_imag  (ref_q),
    .short_chirp_real (ref_i),
    .short_chirp_imag (ref_q),
    .segment_request  (segment_request),
    .sample_addr_out  (sample_addr_from_chain),
    .mem_request      (mem_request),
    .mem_ready        (mem_ready),
    .pc_i_w           (range_profile_i),
    .pc_q_w           (range_profile_q),
    .pc_valid_w       (range_valid),
    .status           ()
);

// ========== 6. Range bin decimation 1024 -> 64 ==========
wire signed [15:0] decimated_range_i, decimated_range_q;
wire               decimated_range_valid;
wire [5:0]         decimated_range_bin;

range_bin_decimator #(
    .INPUT_BINS        (1024),
    .OUTPUT_BINS       (64),
    .DECIMATION_FACTOR (16)
) range_decim (
    .clk             (clk),
    .reset_n         (reset_n),
    .range_i_in      (range_profile_i),
    .range_q_in      (range_profile_q),
    .range_valid_in  (range_valid),
    .range_i_out     (decimated_range_i),
    .range_q_out     (decimated_range_q),
    .range_valid_out (decimated_range_valid),
    .range_bin_index (decimated_range_bin),
    .decimation_mode (decimation_mode),
    .start_bin       (start_bin)
);

wire [31:0] range_data_32bit = {decimated_range_q, decimated_range_i};
assign range_profile_out   = range_data_32bit;
assign range_profile_valid = decimated_range_valid;
assign range_profile_bin   = decimated_range_bin;

// ========== 7. Doppler processing ==========
doppler_processor_optimized #(
    .DOPPLER_FFT_SIZE (32),
    .RANGE_BINS       (64),
    .CHIRPS_PER_FRAME (32)
) doppler_proc (
    .clk               (clk),
    .reset_n           (reset_n),
    .range_data        (range_data_32bit),
    .data_valid        (decimated_range_valid),
    .new_chirp_frame   (new_frame_pulse),
    .doppler_output    (doppler_output),
    .doppler_valid     (doppler_valid),
    .doppler_bin       (doppler_bin),
    .range_bin         (range_bin),
    .processing_active (),
    .frame_complete    (),
    .status            ()
);

endmodule
