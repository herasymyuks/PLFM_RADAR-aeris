// fft_ip_blackbox.v - black-box stand-ins for the two Xilinx FFT IP cores (xfft v9.1)
// that beta/fpga has NOT generated. In the synthesis view (`SYNTHESIS` defined, which
// Yosys does by default) beta/fpga/rtl/xfft_32.v:50 and FFT_enhanced.v:49 instantiate
// these deliberately missing module names so that elaboration fails loudly. For the
// open-source resource estimate we declare them as (* blackbox *) so the rest of the
// design can be synthesised; their cost is NOT included in the Yosys numbers and is
// quoted separately (see README.md, "FFT IP budget"). Port lists copied verbatim from
// the instantiations. Open-source estimate only - not a Vivado result.
(* blackbox *)
module XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README (
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
endmodule

(* blackbox *)
module FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README (
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
endmodule
