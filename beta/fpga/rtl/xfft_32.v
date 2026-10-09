`timescale 1ns / 1ps
// ============================================================================
// xfft_32.v  -  32-point AXI4-Stream FFT used by doppler_processor.v:283-296.
// BETA.  Port list and widths taken from that instantiation:
//   s_axis_config_tdata [7:0]  = {2'b00, SCALE_SCH[4:0], FWD_INV}
//   s_axis_data_tdata  [31:0]  = {Q[15:0], I[15:0]}
//   m_axis_data_tready present  (Non-Real-Time throttle scheme)
//
// SIMULATION: behavioural model (axis_fft_behav).
// SYNTHESIS : replace with Xilinx FFT IP (xfft v9.1) - create_ip -name xfft
//   -vendor xilinx.com -library ip -version 9.1 -module_name xfft_32 with the
//   settings listed in beta/fpga/ip/README.md (transform length 32, 1 channel,
//   Pipelined Streaming I/O, scaled fixed point, 16-bit data, 16-bit phase
//   factors, natural order output, Non Real Time throttle, aresetn, no cyclic
//   prefix). vivado/create_project.tcl uses ip/xfft_32/xfft_32.xci when it
//   exists and then keeps this file in the simulation set only. If the IP is
//   absent the synthesis branch below instantiates a deliberately missing
//   module so that elaboration fails loudly instead of silently producing an
//   empty core.
// ============================================================================
module xfft_32 (
    input  wire        aclk,
    input  wire        aresetn,
    input  wire [7:0]  s_axis_config_tdata,
    input  wire        s_axis_config_tvalid,
    output wire        s_axis_config_tready,
    input  wire [31:0] s_axis_data_tdata,
    input  wire        s_axis_data_tvalid,
    output wire        s_axis_data_tready,
    input  wire        s_axis_data_tlast,
    output wire [31:0] m_axis_data_tdata,
    output wire        m_axis_data_tvalid,
    output wire        m_axis_data_tlast,
    input  wire        m_axis_data_tready
);
`ifndef SYNTHESIS
    axis_fft_behav #(
        .N(32), .LOG2N(5), .DATA_W(16), .CFG_W(8), .LATENCY(72), .QUEUE(4)
    ) u_core (
        .aclk(aclk), .aresetn(aresetn),
        .s_axis_config_tdata(s_axis_config_tdata), .s_axis_config_tvalid(s_axis_config_tvalid),
        .s_axis_config_tready(s_axis_config_tready),
        .s_axis_data_tdata(s_axis_data_tdata), .s_axis_data_tvalid(s_axis_data_tvalid),
        .s_axis_data_tready(s_axis_data_tready), .s_axis_data_tlast(s_axis_data_tlast),
        .m_axis_data_tdata(m_axis_data_tdata), .m_axis_data_tvalid(m_axis_data_tvalid),
        .m_axis_data_tlast(m_axis_data_tlast), .m_axis_data_tready(m_axis_data_tready)
    );
`else
    // SYNTHESIS: replace with Xilinx FFT IP (xfft v9.1) - see beta/fpga/ip/README.md.
    XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README u_missing_ip (
        .aclk(aclk), .aresetn(aresetn),
        .s_axis_config_tdata(s_axis_config_tdata), .s_axis_config_tvalid(s_axis_config_tvalid),
        .s_axis_config_tready(s_axis_config_tready),
        .s_axis_data_tdata(s_axis_data_tdata), .s_axis_data_tvalid(s_axis_data_tvalid),
        .s_axis_data_tready(s_axis_data_tready), .s_axis_data_tlast(s_axis_data_tlast),
        .m_axis_data_tdata(m_axis_data_tdata), .m_axis_data_tvalid(m_axis_data_tvalid),
        .m_axis_data_tlast(m_axis_data_tlast), .m_axis_data_tready(m_axis_data_tready)
    );
`endif
endmodule
