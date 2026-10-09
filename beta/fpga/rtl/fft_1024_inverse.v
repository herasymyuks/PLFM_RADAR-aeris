`timescale 1ns / 1ps

// BETA (beta/fpga/CHANGELOG.md): SCALE_SCH parameter added; configuration word is
// {5'b0, SCALE_SCH, 1'b0} (bit 0 = 0 selects the inverse transform). The original
// 16'h0000 (:28) selected no scaling. The uninitialised debug counter (:66-75) was removed.
module fft_1024_inverse_enhanced #(
    parameter [9:0] SCALE_SCH = 10'h155   // 2^-5 total (1 bit per stage)
) (
    input wire clk,
    input wire reset_n,
    input wire [15:0] data_i,
    input wire [15:0] data_q,
    input wire data_valid,
    output wire [15:0] ifft_i,
    output wire [15:0] ifft_q,
    output wire ifft_valid
);

// ========== MATCH YOUR FFT IP CONFIGURATION ==========
wire [15:0] s_axis_config_tdata;      // 16-bit
wire s_axis_config_tvalid;
wire s_axis_config_tready;
wire [31:0] s_axis_data_tdata;        // 32-bit for your IP  {Q[15:0],I[15:0]}
wire s_axis_data_tvalid;
wire s_axis_data_tready;              // not used: the block feeder never stalls (see README)
wire s_axis_data_tlast;
wire [31:0] m_axis_data_tdata;        // 32-bit
wire m_axis_data_tvalid;
wire m_axis_data_tready;
wire m_axis_data_tlast;

// Configuration: bit 0 = 0 for inverse FFT, bits [10:1] = scaling schedule
assign s_axis_config_tdata = {5'b00000, SCALE_SCH, 1'b0};
assign s_axis_config_tvalid = 1'b1;


assign s_axis_data_tdata = {data_q, data_i};
assign s_axis_data_tvalid = data_valid;

// Frame counter
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
// Output
assign ifft_i = m_axis_data_tdata[15:0];   // I = lower 16 bits
assign ifft_q = m_axis_data_tdata[31:16];  // Q = upper 16 bits
assign ifft_valid = m_axis_data_tvalid;
assign m_axis_data_tready = 1'b1;   // Real-Time throttle: the IP has no m_axis tready port

// IFFT IP instance
FFT_enhanced ifft_inverse_inst (  // Same IP core, different configuration
    .aclk(clk),
    .aresetn(reset_n),
    
    .s_axis_config_tdata(s_axis_config_tdata),
    .s_axis_config_tvalid(s_axis_config_tvalid),
    .s_axis_config_tready(s_axis_config_tready),
    
    .s_axis_data_tdata(s_axis_data_tdata),
    .s_axis_data_tvalid(s_axis_data_tvalid),
    .s_axis_data_tready(s_axis_data_tready),
    .s_axis_data_tlast(s_axis_data_tlast),
    
    .m_axis_data_tdata(m_axis_data_tdata),
    .m_axis_data_tvalid(m_axis_data_tvalid),
    .m_axis_data_tlast(m_axis_data_tlast)
    
);

endmodule
