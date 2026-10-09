`timescale 1ns / 1ps
// ============================================================================
// ad9484_lvds_to_cmos_400m.v  -  AD9484 LVDS data capture.  BETA.
//
// This module was instantiated by radar_receiver_final.v:82 but never existed
// in the repository. It is written from the port list of that instantiation
// plus the AD9484 datasheet (7_Components Datasheets and Application notes/
// AD9484/AD9484.pdf, "Output Data Rate and Pinout Configuration" and the
// timing section):
//
//   * The AD9484 drives 8 LVDS data pairs (D0..D7) in SDR mode, one bit per
//     lane per sample, at the sample rate. The data clock output DCO toggles
//     at the sample rate (f_DCO = f_S = 400 MHz here, AD9523 OUT4 -> ADC CLK).
//   * Data edges are aligned to the DCO edges within tSKEW = +/-0.07 ns
//     (edge-aligned source-synchronous interface). The datasheet says data
//     "must be captured on the rising edge of the DCO", which for an
//     edge-aligned bus means the receiver has to phase-shift by ~90..180 deg.
//
// CLOCKING ASSUMPTION (documented, not verified on hardware):
//   The DCO is used directly as the 400 MHz capture and processing clock
//   (IBUFDS -> BUFG -> adc_dco_cmos). Data is captured with an IDDR in
//   SAME_EDGE_PIPELINED mode; with CAPTURE_FALLING = 1 (default) the
//   falling-edge sample (Q2) is used, i.e. the bit is sampled 1.25 ns after
//   its transition = centre of the 2.5 ns bit period; with CAPTURE_FALLING = 0
//   the rising-edge sample (Q1) is used (requires an external/IDELAY phase
//   shift). This is NOT a DDR interface; the IDDR is used only as a dual-edge
//   sampler. Internal clock-tree skew (BUFG insertion ~1-2 ns) is comparable
//   with the bit period, so the choice of edge MUST be confirmed by Vivado
//   timing analysis with the set_input_delay constraints in
//   constraints/radar_system_top_beta.xdc, and on hardware with a known test
//   pattern (AD9484 register 0x0D test modes). A production design should use
//   IDELAYE2 + IDELAYCTRL (200 MHz reference) or ISERDESE2 with a 200 MHz
//   divided clock (2 samples/cycle); see README "Remaining work".
//
// Bank/IO-standard: the schematic puts these pairs in bank 14 with
// VCCO = 3.3 V. LVDS_25 inputs are legal there only with DIFF_TERM = FALSE
// (external 100 Ohm termination, UG471) - hence the DIFF_TERM default below.
// This is a board-level open point (see PIN_MAP_FROM_SCHEMATIC.md).
//
// `ifdef SIM : purely behavioural model (no primitives) so Icarus/Verilator
//              run without UNISIM; p inputs are used, n inputs ignored.
// ============================================================================
module ad9484_lvds_to_cmos_400m #(
    parameter DIFF_TERM       = "FALSE",   // "TRUE" only if bank VCCO = 2.5 V (board change)
    parameter CAPTURE_FALLING = 1,         // 1: sample on DCO falling edge (mid-bit for edge-aligned SDR)
    parameter VALID_DELAY     = 16         // DCO cycles after reset release before adc_valid rises
) (
    input  wire [7:0] adc_d_p,       // AD9484 D0..D7 true
    input  wire [7:0] adc_d_n,       // AD9484 D0..D7 complement
    input  wire       adc_dco_p,     // AD9484 DCO true  (400 MHz SDR)
    input  wire       adc_dco_n,     // AD9484 DCO complement
    input  wire       reset_n,       // asynchronous active-low (any domain)
    input  wire       pwdn_req,      // 1 = power the ADC down (from register map)
    output wire [7:0] adc_data_cmos, // captured sample, synchronous to adc_dco_cmos rising edge
    output wire       adc_dco_cmos,  // 400 MHz capture clock (global buffer output)
    output wire       adc_valid,     // 1 once the capture path is out of reset
    output wire       adc_pwdn       // to AD9484 PDWN pin (active high)
);

    wire [7:0] data_se;   // single-ended data after the differential input buffers
    wire       dco_se;    // single-ended DCO
    wire [7:0] cap_rise;  // sample taken on the DCO rising edge
    wire [7:0] cap_fall;  // sample taken on the DCO falling edge

`ifdef SIM
    // ---------------- behavioural model (no primitives) ----------------
    /* verilator lint_off UNUSEDSIGNAL */
    wire [8:0] unused_n = {adc_d_n, adc_dco_n};
    /* verilator lint_on UNUSEDSIGNAL */
    assign data_se      = adc_d_p;
    assign dco_se       = adc_dco_p;
    assign adc_dco_cmos = dco_se;

    reg [7:0] q_rise, q_fall, q_rise_p, q_fall_p;
    initial begin q_rise = 8'd0; q_fall = 8'd0; q_rise_p = 8'd0; q_fall_p = 8'd0; end
    always @(posedge adc_dco_cmos) q_rise <= data_se;
    always @(negedge adc_dco_cmos) q_fall <= data_se;
    always @(posedge adc_dco_cmos) begin   // IDDR SAME_EDGE_PIPELINED equivalent
        q_rise_p <= q_rise;
        q_fall_p <= q_fall;
    end
    assign cap_rise = q_rise_p;
    assign cap_fall = q_fall_p;
`else
    // ---------------- synthesis view: IBUFDS + BUFG + IDDR ----------------
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : g_data_in
            IBUFDS #(
                .DIFF_TERM  (DIFF_TERM),
                .IOSTANDARD ("LVDS_25")
            ) u_ibufds_data (
                .O  (data_se[i]),
                .I  (adc_d_p[i]),
                .IB (adc_d_n[i])
            );
        end
    endgenerate

    IBUFDS #(
        .DIFF_TERM  (DIFF_TERM),
        .IOSTANDARD ("LVDS_25")
    ) u_ibufds_dco (
        .O  (dco_se),
        .I  (adc_dco_p),
        .IB (adc_dco_n)
    );

    // Clock forwarding to the global clock network. The DCO pins (N14/P14)
    // are an MRCC pair in bank 14, so BUFG routing is legal.
    BUFG u_bufg_dco (
        .I (dco_se),
        .O (adc_dco_cmos)
    );

    generate
        for (i = 0; i < 8; i = i + 1) begin : g_iddr
            IDDR #(
                .DDR_CLK_EDGE ("SAME_EDGE_PIPELINED"),
                .INIT_Q1      (1'b0),
                .INIT_Q2      (1'b0),
                .SRTYPE       ("SYNC")
            ) u_iddr (
                .Q1 (cap_rise[i]),   // rising-edge sample, pipelined
                .Q2 (cap_fall[i]),   // falling-edge sample
                .C  (adc_dco_cmos),
                .CE (1'b1),
                .D  (data_se[i]),
                .R  (1'b0),
                .S  (1'b0)
            );
        end
    endgenerate
`endif

    // ---------------- reset synchronised into the DCO domain ----------------
    wire rst_n_dco;
    reset_synchronizer #(.STAGES(2)) u_rst_sync (
        .clk           (adc_dco_cmos),
        .async_reset_n (reset_n),
        .sync_reset_n  (rst_n_dco)
    );

    // ---------------- output register + valid ----------------
    reg [7:0] data_r;
    reg [4:0] valid_cnt;
    reg       valid_r;

    always @(posedge adc_dco_cmos or negedge rst_n_dco) begin
        if (!rst_n_dco) begin
            data_r    <= 8'd0;
            valid_cnt <= 5'd0;
            valid_r   <= 1'b0;
        end else begin
            data_r <= (CAPTURE_FALLING != 0) ? cap_fall : cap_rise;
            if (valid_cnt == VALID_DELAY[4:0])
                valid_r <= 1'b1;
            else
                valid_cnt <= valid_cnt + 5'd1;
        end
    end

    assign adc_data_cmos = data_r;
    assign adc_valid     = valid_r;
    assign adc_pwdn      = pwdn_req;
endmodule
