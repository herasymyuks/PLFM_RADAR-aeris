`timescale 1ns / 1ps
// BETA (beta/fpga/CHANGELOG.md) changes vs 9_Firmware/9_2_FPGA/ddc_400m.v:
//  * reset_n_400m port added: reset released synchronously to clk_400m for the NCO/mixer/CIC
//  * CIC -> FIR clock crossing uses async_fifo (Gray pointers) instead of cdc_adc_to_processing
//  * declaration-before-use fixed (fir_* wires), output stage on posedge, reset_monitors made
//    synchronous, saturation_count single-driven, NCO phase_valid from the synchronised enable,
//    bypass_mode implemented (mixer bypass for tests), uninitialised $display debug removed.

module ddc_400m_enhanced (
    input wire clk_400m,           // 400MHz clock from ADC DCO
    input wire clk_100m,           // 100MHz system clock
    input wire reset_n,            // reset for the clk_100m side
    input wire reset_n_400m,       // reset synchronised to clk_400m (reset_synchronizer in the receiver)
    input wire mixers_enable,
    input wire [7:0] adc_data,     // ADC data at 400MHz
    input wire adc_data_valid_i,     // Valid at 400MHz
	 input wire adc_data_valid_q,
    output wire signed [17:0] baseband_i,
    output wire signed [17:0] baseband_q,  
    output wire baseband_valid_i,
	 output wire baseband_valid_q,

    output wire [1:0] ddc_status,
    // Enhanced interfaces
    output wire [7:0] ddc_diagnostics,
    output wire mixer_saturation,
    output wire filter_overflow,
    input wire bypass_mode,        // Test mode
	 
    /* verilator lint_off UNUSEDSIGNAL */
	 input wire [1:0] test_mode,          // reserved (not implemented in the original either)
    input wire [15:0] test_phase_inc,
    /* verilator lint_on UNUSEDSIGNAL */
    input wire force_saturation,
    input wire reset_monitors,
    output wire [31:0] debug_sample_count,
    output wire [17:0] debug_internal_i,
    output wire [17:0] debug_internal_q,
    output wire cdc_overflow            // BETA: sticky FIFO overflow flag (any lost CIC sample)
);

// Parameters for numerical precision
parameter ADC_WIDTH = 8;
parameter NCO_WIDTH = 16;
parameter MIXER_WIDTH = 18;
parameter OUTPUT_WIDTH = 18;

// IF frequency parameters
parameter IF_FREQ = 120000000;
parameter FS = 400000000;
parameter PHASE_WIDTH = 32;

// Internal signals
wire signed [15:0] sin_out, cos_out;
wire nco_ready;
wire cic_valid;
wire fir_valid;
wire [17:0] cic_i_out, cic_q_out;
wire signed [17:0] fir_i_out, fir_q_out;


// Diagnostic registers
reg [2:0] saturation_count;
reg overflow_detected;
reg [7:0] error_counter;

// CDC synchronization for control signals
reg mixers_enable_sync;
reg bypass_mode_sync;

// Debug monitoring signals
reg [31:0] sample_counter;
wire signed [17:0] debug_mixed_i_trunc;
wire signed [17:0] debug_mixed_q_trunc;

// Real-time status monitoring
reg [7:0] signal_power_i, signal_power_q;

// Enhanced saturation injection for testing
reg force_saturation_sync;

// Internal mixing signals
reg signed [MIXER_WIDTH-1:0] adc_signed;
reg signed [MIXER_WIDTH + NCO_WIDTH -1:0] mixed_i, mixed_q;
reg mixed_valid;
reg mixer_overflow_i, mixer_overflow_q;

// Output stage registers
reg signed [17:0] baseband_i_reg, baseband_q_reg;
reg baseband_valid_reg;

// ============================================================================
// Phase Dithering Signals
// ============================================================================
wire [7:0] phase_dither_bits;
wire [31:0] phase_inc_dithered;



// ============================================================================
// Debug Signal Assignments
// ============================================================================
assign debug_internal_i = mixed_i[25:8];
assign debug_internal_q = mixed_q[25:8];
assign debug_sample_count = sample_counter;
assign debug_mixed_i_trunc = mixed_i[25:8];
assign debug_mixed_q_trunc = mixed_q[25:8];

// ============================================================================
// Clock Domain Crossing for Control Signals
// ============================================================================
(* ASYNC_REG = "TRUE" *) reg mixers_enable_meta, bypass_mode_meta, force_saturation_meta, reset_monitors_meta;
reg reset_monitors_sync;
always @(posedge clk_400m or negedge reset_n_400m) begin
    if (!reset_n_400m) begin
        mixers_enable_meta <= 1'b0;    mixers_enable_sync <= 1'b0;
        bypass_mode_meta <= 1'b0;      bypass_mode_sync <= 1'b0;
        force_saturation_meta <= 1'b0; force_saturation_sync <= 1'b0;
        reset_monitors_meta <= 1'b0;   reset_monitors_sync <= 1'b0;
    end else begin
        mixers_enable_meta <= mixers_enable;       mixers_enable_sync <= mixers_enable_meta;
        bypass_mode_meta <= bypass_mode;           bypass_mode_sync <= bypass_mode_meta;
        force_saturation_meta <= force_saturation; force_saturation_sync <= force_saturation_meta;
        reset_monitors_meta <= reset_monitors;     reset_monitors_sync <= reset_monitors_meta;
    end
end

// ============================================================================
// Sample Counter and Debug Monitoring
// ============================================================================
always @(posedge clk_400m or negedge reset_n_400m) begin
    if (!reset_n_400m) begin
        sample_counter <= 0;
        error_counter <= 0;
    end else if (reset_monitors_sync) begin
        sample_counter <= 0;
        error_counter <= 0;
    end else if (adc_data_valid_i && adc_data_valid_q ) begin
        sample_counter <= sample_counter + 1;
    end
end


// ============================================================================
// Enhanced Phase Dithering Instance
// ============================================================================
lfsr_dither_enhanced #(
    .DITHER_WIDTH(8)
) phase_dither_gen (
    .clk(clk_400m),
    .reset_n(reset_n_400m),
    .enable(nco_ready),
    .dither_out(phase_dither_bits)
);

// ============================================================================
// Phase Increment Calculation with Dithering
// ============================================================================
// Calculate phase increment for 120MHz IF at 400MHz sampling
localparam PHASE_INC_120MHZ = 32'h4CCCCCCD;

// Apply dithering to reduce spurious tones
assign phase_inc_dithered = PHASE_INC_120MHZ + {24'b0, phase_dither_bits};

// ============================================================================
// Enhanced NCO with Diagnostics
// ============================================================================
nco_400m_enhanced nco_core (
    .clk_400m(clk_400m),
    .reset_n(reset_n_400m),
    .frequency_tuning_word(phase_inc_dithered),
    .phase_valid(mixers_enable_sync),
    .phase_offset(16'h0000),
    .sin_out(sin_out),
    .cos_out(cos_out),
    .dds_ready(nco_ready)
);

// ============================================================================
// Enhanced Mixing Stage with AGC
// ============================================================================
always @(posedge clk_400m or negedge reset_n_400m) begin
    if (!reset_n_400m) begin
        adc_signed <= 0;
        mixed_i <= 0;
        mixed_q <= 0;
        mixed_valid <= 0;
        mixer_overflow_i <= 0;
        mixer_overflow_q <= 0;
        saturation_count <= 0;
        overflow_detected <= 0;
    end else if (nco_ready && adc_data_valid_i && adc_data_valid_q) begin
        // Convert ADC data to signed with extended precision
        adc_signed <= {1'b0, adc_data, {(MIXER_WIDTH-ADC_WIDTH-1){1'b0}}} - 
                     {1'b0, {ADC_WIDTH{1'b1}}, {(MIXER_WIDTH-ADC_WIDTH-1){1'b0}}} / 2;
        
        // Force saturation for testing
        if (force_saturation_sync) begin
            mixed_i <= 34'h1FFFFFFFF;  // Force positive saturation
            mixed_q <= 34'h200000000;  // Force negative saturation
            mixer_overflow_i <= 1'b1;
            mixer_overflow_q <= 1'b1;
        end else if (bypass_mode_sync) begin
            // test mode: pass the ADC sample straight through as I (scaled like cos = +32767), Q = 0
            mixed_i <= $signed(adc_signed) * $signed(16'sh7FFF);
            mixed_q <= 34'sd0;
            mixer_overflow_i <= 1'b0;
            mixer_overflow_q <= 1'b0;
        end else begin

                // Normal mixing
                mixed_i <= $signed(adc_signed) * $signed(cos_out);
                mixed_q <= $signed(adc_signed) * $signed(sin_out);
            
            
            // Enhanced overflow detection with counting
            mixer_overflow_i <= (mixed_i > (2**(MIXER_WIDTH+NCO_WIDTH-2)-1)) || 
                               (mixed_i < -(2**(MIXER_WIDTH+NCO_WIDTH-2)));
            mixer_overflow_q <= (mixed_q > (2**(MIXER_WIDTH+NCO_WIDTH-2)-1)) || 
                               (mixed_q < -(2**(MIXER_WIDTH+NCO_WIDTH-2)));
        end
        
        mixed_valid <= 1;
        
        if (reset_monitors_sync) begin
            saturation_count <= 0;
            overflow_detected <= 1'b0;
        end else if (mixer_overflow_i || mixer_overflow_q) begin
            saturation_count <= saturation_count + 1;
            overflow_detected <= 1'b1;
        end else begin
            overflow_detected <= 1'b0;
        end
        
    end else begin
        mixed_valid <= 0;
        mixer_overflow_i <= 0;
        mixer_overflow_q <= 0;
        overflow_detected <= 1'b0;
    end
end

// ============================================================================
// Enhanced CIC Decimators
// ============================================================================
wire cic_valid_i, cic_valid_q;

cic_decimator_4x_enhanced cic_i_inst (
    .clk(clk_400m),
    .reset_n(reset_n_400m),
    .data_in(mixed_i[33:16]),
    .data_valid(mixed_valid),
    .data_out(cic_i_out),
    .data_out_valid(cic_valid_i),
    .saturation_detected(),
    .max_value_monitor(),
    .reset_monitors(reset_monitors_sync)
);

cic_decimator_4x_enhanced cic_q_inst (
    .clk(clk_400m),
    .reset_n(reset_n_400m),
    .data_in(mixed_q[33:16]),
    .data_valid(mixed_valid),
    .data_out(cic_q_out),
    .data_out_valid(cic_valid_q),
    .saturation_detected(),
    .max_value_monitor(),
    .reset_monitors(reset_monitors_sync)
);

assign cic_valid = cic_valid_i & cic_valid_q;

// ---- clk_400m -> clk_100m crossing: dual-clock FIFOs (BETA, replaces cdc_adc_to_processing) ----
wire fir_in_valid_i, fir_in_valid_q;
wire fir_valid_i, fir_valid_q;
wire [17:0] fir_d_in_i, fir_d_in_q;
wire fifo_i_empty, fifo_q_empty;
wire [15:0] fifo_i_ovf, fifo_q_ovf;

async_fifo #(.WIDTH(18), .ADDR_BITS(4)) CDC_FIR_i (
    .wr_clk(clk_400m), .wr_reset_n(reset_n_400m), .wr_en(cic_valid_i), .wr_data(cic_i_out),
    .full(), .wr_overflow_count(fifo_i_ovf),
    .rd_clk(clk_100m), .rd_reset_n(reset_n), .rd_en(!fifo_i_empty),
    .rd_data(fir_d_in_i), .rd_valid(fir_in_valid_i), .empty(fifo_i_empty)
);

async_fifo #(.WIDTH(18), .ADDR_BITS(4)) CDC_FIR_q (
    .wr_clk(clk_400m), .wr_reset_n(reset_n_400m), .wr_en(cic_valid_q), .wr_data(cic_q_out),
    .full(), .wr_overflow_count(fifo_q_ovf),
    .rd_clk(clk_100m), .rd_reset_n(reset_n), .rd_en(!fifo_q_empty),
    .rd_data(fir_d_in_q), .rd_valid(fir_in_valid_q), .empty(fifo_q_empty)
);

assign cdc_overflow = (fifo_i_ovf != 16'd0) || (fifo_q_ovf != 16'd0);
wire fir_i_overflow, fir_q_overflow;
assign filter_overflow = fir_i_overflow | fir_q_overflow;   // BETA: was undriven

// ============================================================================
// Enhanced FIR Filters with FIXED valid signal handling
// ============================================================================
// FIR I channel
fir_lowpass_parallel_enhanced fir_i_inst (
    .clk(clk_100m),
    .reset_n(reset_n),
    .data_in(fir_d_in_i),  // Use synchronized data
    .data_valid(fir_in_valid_i),  // Use synchronized valid
    .data_out(fir_i_out),
    .data_out_valid(fir_valid_i),
    .fir_ready(),
    .filter_overflow(fir_i_overflow)
);

// FIR Q channel  
fir_lowpass_parallel_enhanced fir_q_inst (
    .clk(clk_100m),
    .reset_n(reset_n),
    .data_in(fir_d_in_q),  // Use synchronized data
    .data_valid(fir_in_valid_q),  // Use synchronized valid
    .data_out(fir_q_out),
    .data_out_valid(fir_valid_q),
    .fir_ready(),
    .filter_overflow(fir_q_overflow)
);

assign fir_valid = fir_valid_i & fir_valid_q;

// ============================================================================
// Enhanced Output Stage
// ============================================================================
always @(posedge clk_100m or negedge reset_n) begin   // BETA: was negedge
    if (!reset_n) begin
        baseband_i_reg <= 0;
        baseband_q_reg <= 0;
        baseband_valid_reg <= 0;
    end else if (fir_valid) begin
        baseband_i_reg <= fir_i_out;
        baseband_q_reg <= fir_q_out;
        baseband_valid_reg <= 1;
    end else begin
        baseband_valid_reg <= 0;
    end
end


// ============================================================================
// Output Assignments
// ============================================================================
assign baseband_i = baseband_i_reg;
assign baseband_q = baseband_q_reg;
assign baseband_valid_i = baseband_valid_reg;
assign baseband_valid_q = baseband_valid_reg;
assign ddc_status = {mixer_overflow_i | mixer_overflow_q, nco_ready};
assign mixer_saturation = overflow_detected;
assign ddc_diagnostics = {saturation_count, error_counter[4:0]};

// (BETA: uninitialised $display debug blocks removed - see CHANGELOG)

endmodule

// ============================================================================
// Enhanced Phase Dithering Module
// ============================================================================
`timescale 1ns / 1ps

module lfsr_dither_enhanced #(
    parameter DITHER_WIDTH = 8  // Increased for better dithering
)(
    input wire clk,
    input wire reset_n,
    input wire enable,
    output wire [DITHER_WIDTH-1:0] dither_out
);

reg [DITHER_WIDTH-1:0] lfsr_reg;
reg [15:0] cycle_counter;
reg lock_detected;

// Polynomial for better randomness: x^8 + x^6 + x^5 + x^4 + 1
wire feedback;

generate
    if (DITHER_WIDTH == 4) begin
        assign feedback = lfsr_reg[3] ^ lfsr_reg[2];
    end else if (DITHER_WIDTH == 8) begin
        assign feedback = lfsr_reg[7] ^ lfsr_reg[5] ^ lfsr_reg[4] ^ lfsr_reg[3];
    end else begin
        assign feedback = lfsr_reg[DITHER_WIDTH-1] ^ lfsr_reg[DITHER_WIDTH-2];
    end
endgenerate

always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        lfsr_reg <= {DITHER_WIDTH{1'b1}};  // Non-zero initial state
        cycle_counter <= 0;
        lock_detected <= 0;
    end else if (enable) begin
        lfsr_reg <= {lfsr_reg[DITHER_WIDTH-2:0], feedback};
        cycle_counter <= cycle_counter + 1;
        
        // Detect LFSR lock after sufficient cycles
        if (cycle_counter > (2**DITHER_WIDTH * 8)) begin
            lock_detected <= 1'b1;
        end
    end
end

assign dither_out = lfsr_reg;

endmodule
