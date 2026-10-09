// fft_ip_pnr_stub.v - P&R-trial stand-ins for the two missing Xilinx FFT IP cores.
// nextpnr-xilinx cannot place a black box, and simply deleting the cores would let Yosys
// remove all logic downstream of them (matched-filter multiply, IFFT, decimator, Doppler,
// packer). These stubs are a ONE-REGISTER AXI-Stream pass-through (data/valid/last registered,
// tready = 1): they keep the surrounding design alive for placement/routing/timing, but they
// contain NO FFT, do not compute anything meaningful, and their own resources/timing are NOT
// representative of xfft v9.1. Open-source P&R trial only - never use for a real build.
module XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README (
    input  wire        aclk, input wire aresetn,
    input  wire [7:0]  s_axis_config_tdata, input wire s_axis_config_tvalid, output wire s_axis_config_tready,
    input  wire [31:0] s_axis_data_tdata, input wire s_axis_data_tvalid, output wire s_axis_data_tready,
    input  wire        s_axis_data_tlast,
    output reg  [31:0] m_axis_data_tdata, output reg m_axis_data_tvalid, output reg m_axis_data_tlast,
    input  wire        m_axis_data_tready
);
    reg [7:0] cfg;
    assign s_axis_config_tready = 1'b1;
    assign s_axis_data_tready   = m_axis_data_tready;
    always @(posedge aclk) begin
        if (s_axis_config_tvalid) cfg <= s_axis_config_tdata;
        if (!aresetn) begin m_axis_data_tvalid <= 1'b0; m_axis_data_tlast <= 1'b0; end
        else if (m_axis_data_tready) begin
            m_axis_data_tdata  <= s_axis_data_tdata ^ {24'd0, cfg};
            m_axis_data_tvalid <= s_axis_data_tvalid;
            m_axis_data_tlast  <= s_axis_data_tlast;
        end
    end
endmodule

module FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README (
    input  wire        aclk, input wire aresetn,
    input  wire [15:0] s_axis_config_tdata, input wire s_axis_config_tvalid, output wire s_axis_config_tready,
    input  wire [31:0] s_axis_data_tdata, input wire s_axis_data_tvalid, output wire s_axis_data_tready,
    input  wire        s_axis_data_tlast,
    output reg  [31:0] m_axis_data_tdata, output reg m_axis_data_tvalid, output reg m_axis_data_tlast
);
    reg [15:0] cfg;
    assign s_axis_config_tready = 1'b1;
    assign s_axis_data_tready   = 1'b1;
    always @(posedge aclk) begin
        if (s_axis_config_tvalid) cfg <= s_axis_config_tdata;
        if (!aresetn) begin m_axis_data_tvalid <= 1'b0; m_axis_data_tlast <= 1'b0; end
        else begin
            m_axis_data_tdata  <= s_axis_data_tdata ^ {16'd0, cfg};
            m_axis_data_tvalid <= s_axis_data_tvalid;
            m_axis_data_tlast  <= s_axis_data_tlast;
        end
    end
endmodule
