`timescale 1ns / 1ps
// ============================================================================
// FFT_enhanced.v  -  1024-point AXI4-Stream FFT used by fft_1024_forward.v:102
// and fft_1024_inverse.v:78 (same core, direction set at run time). BETA.
// Port list and widths taken from those instantiations:
//   s_axis_config_tdata [15:0] = {5'b0, SCALE_SCH[9:0], FWD_INV}
//   s_axis_data_tdata  [31:0]  = {Q[15:0], I[15:0]}
//   NO m_axis_data_tready       (Real-Time throttle scheme: the consumer must
//                                always accept; both wrappers tie tready high)
//
// SIMULATION: behavioural model (axis_fft_behav).
// SYNTHESIS : replace with Xilinx FFT IP (xfft v9.1) - create_ip -name xfft
//   -vendor xilinx.com -library ip -version 9.1 -module_name FFT_enhanced with
//   the settings in beta/fpga/ip/README.md (length 1024, 1 channel, Pipelined
//   Streaming I/O, run-time configurable transform direction, scaled fixed
//   point, 16-bit data, 16-bit phase factors, natural order output, Real Time
//   throttle, aresetn). See xfft_32.v for how create_project.tcl treats this
//   file when the .xci exists.
// ============================================================================
module FFT_enhanced (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire [15:0] s_axis_config_tdata,
    input  wire        s_axis_config_tvalid,
    output wire        s_axis_config_tready,
    input  wire [31:0] s_axis_data_tdata,
    input  wire        s_axis_data_tvalid,
    output wire        s_axis_data_tready,
    input  wire        s_axis_data_tlast,
    output wire [31:0] m_axis_data_tdata,
    output wire        m_axis_data_tvalid,
    output wire        m_axis_data_tlast
);
`ifndef SYNTHESIS
    axis_fft_behav #(
        .N(1024), .LOG2N(10), .DATA_W(16), .CFG_W(16), .LATENCY(160), .QUEUE(4)
    ) u_core (
        .aclk(aclk), .aresetn(aresetn),
        .s_axis_config_tdata(s_axis_config_tdata), .s_axis_config_tvalid(s_axis_config_tvalid),
        .s_axis_config_tready(s_axis_config_tready),
        .s_axis_data_tdata(s_axis_data_tdata), .s_axis_data_tvalid(s_axis_data_tvalid),
        .s_axis_data_tready(s_axis_data_tready), .s_axis_data_tlast(s_axis_data_tlast),
        .m_axis_data_tdata(m_axis_data_tdata), .m_axis_data_tvalid(m_axis_data_tvalid),
        .m_axis_data_tlast(m_axis_data_tlast), .m_axis_data_tready(1'b1)
    );
`else
    // SYNTHESIS: replace with Xilinx FFT IP (xfft v9.1) - see beta/fpga/ip/README.md.
    FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README u_missing_ip (
        .aclk(aclk), .aresetn(aresetn),
        .s_axis_config_tdata(s_axis_config_tdata), .s_axis_config_tvalid(s_axis_config_tvalid),
        .s_axis_config_tready(s_axis_config_tready),
        .s_axis_data_tdata(s_axis_data_tdata), .s_axis_data_tvalid(s_axis_data_tvalid),
        .s_axis_data_tready(s_axis_data_tready), .s_axis_data_tlast(s_axis_data_tlast),
        .m_axis_data_tdata(m_axis_data_tdata), .m_axis_data_tvalid(m_axis_data_tvalid),
        .m_axis_data_tlast(m_axis_data_tlast)
    );
`endif
endmodule
