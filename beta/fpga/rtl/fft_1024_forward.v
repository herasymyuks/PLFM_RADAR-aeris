`timescale 1ns / 1ps

// BETA (beta/fpga/CHANGELOG.md): SCALE_SCH parameter added; the configuration word is
// {5'b0, SCALE_SCH, 1'b1}. The original fixed 16'h0001 (:28) selects NO scaling, which
// overflows a 16-bit 1024-point transform for any input above ~32 LSB.
module fft_1024_forward_enhanced #(
    parameter [9:0] SCALE_SCH = 10'h255   // 2^-6 total (1,1,1,1,2 bits per stage)
) (
    input wire clk,
    input wire reset_n,
    input wire [15:0] data_i,
    input wire [15:0] data_q,
    input wire data_valid,
    output wire [15:0] fft_i,
    output wire [15:0] fft_q,
    output wire fft_valid
);

// ========== MATCH YOUR FFT IP CONFIGURATION ==========
wire [15:0] s_axis_config_tdata;      // 16-bit for your IP
wire s_axis_config_tvalid;
wire s_axis_config_tready;
wire [31:0] s_axis_data_tdata;        // 32-bit for your IP  {Q[15:0],I[15:0]}
wire s_axis_data_tvalid;
wire s_axis_data_tready;              // not used: the block feeder never stalls (see README)
wire s_axis_data_tlast;
wire [31:0] m_axis_data_tdata;        // 32-bit for your IP
wire m_axis_data_tvalid;
wire m_axis_data_tready;
wire m_axis_data_tlast;

// Configuration: 16-bit, bit 0 = 1 for forward FFT, bits [10:1] = scaling schedule
assign s_axis_config_tdata = {5'b00000, SCALE_SCH, 1'b1};
assign s_axis_config_tvalid = 1'b1;  // Keep valid until accepted


assign s_axis_data_tdata = {data_q, data_i};  // {Q, I}
assign s_axis_data_tvalid = data_valid;

// Frame counter for tlast
reg [9:0] sample_count;
// BETA: the original counter (:36-58) did not count the first sample of a frame
// (frame_active was still 0), so tlast came one sample late and the next frame
// started with a stray tlast -> the FFT emitted an extra zero-filled frame per block.
always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        sample_count <= 0;
    end else if (data_valid) begin
        if (sample_count == 1023)
            sample_count <= 0;
        else
            sample_count <= sample_count + 1;
    end
end
assign s_axis_data_tlast = (sample_count == 1023) && data_valid;

// Output: Extract from 64-bit output
// Assuming output format is also {Q[31:0], I[31:0]}
assign fft_i = m_axis_data_tdata[15:0];   // Lower 16 bits = I
assign fft_q = m_axis_data_tdata[31:16];  // Upper 16 bits = Q
assign fft_valid = m_axis_data_tvalid;
assign m_axis_data_tready = 1'b1;   // Real-Time throttle: the IP has no m_axis tready port

// ========== DEBUG ==========
/*
reg [31:0] debug_counter = 0;
always @(posedge clk) begin
    debug_counter <= debug_counter + 1;
    
    // Monitor first 2000 cycles
    if (debug_counter < 2000) begin
        // Configuration
        if (s_axis_config_tvalid && s_axis_config_tready) begin
            $display("[FFT_CORRECTED @%d] CONFIG ACCEPTED! tdata=%h", 
                     debug_counter, s_axis_config_tdata);
        end
        
        // Data input
        if (s_axis_data_tvalid && s_axis_data_tready && debug_counter < 1050) begin
            $display("[FFT_CORRECTED @%d] Data in: I=%h Q=%h count=%d tlast=%b",
                     debug_counter, data_i, data_q, sample_count, s_axis_data_tlast);
        end
        
        // Data output
        if (m_axis_data_tvalid && debug_counter < 3000) begin
            $display("[FFT_CORRECTED @%d] FFT OUT: I=%h Q=%h",
                     debug_counter, fft_i, fft_q);
        end
        
        // Stuck detection
        if (debug_counter == 100 && !s_axis_config_tready) begin
            $display("[FFT_CORRECTED] WARNING: config_tready still 0 after 100 cycles");
        end
    end
end
*/
// ========== FFT IP INSTANCE ==========
// This must match the name in your project
FFT_enhanced fft_forward_inst (
    .aclk(clk),
    .aresetn(reset_n),  // Active-low reset
    
    // Configuration (16-bit)
    .s_axis_config_tdata(s_axis_config_tdata),
    .s_axis_config_tvalid(s_axis_config_tvalid),
    .s_axis_config_tready(s_axis_config_tready),
    
    // Data input (64-bit)
    .s_axis_data_tdata(s_axis_data_tdata),
    .s_axis_data_tvalid(s_axis_data_tvalid),
    .s_axis_data_tready(s_axis_data_tready),
    .s_axis_data_tlast(s_axis_data_tlast),
    
    // Data output (64-bit)
    .m_axis_data_tdata(m_axis_data_tdata),
    .m_axis_data_tvalid(m_axis_data_tvalid),
    .m_axis_data_tlast(m_axis_data_tlast)
    
);

endmodule
