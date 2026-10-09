`timescale 1ns / 1ps
// ============================================================================
// nco_400m_enhanced.v  -  quarter-wave LUT NCO (sin/cos), 400 MHz domain.
// BETA rewrite of 9_Firmware/9_2_FPGA/nco_400m_enhanced.v.
//
// Why rewritten (see CHANGELOG.md): the original 64-entry "quarter-wave" table
// (:34-49) is not a sine quarter wave (it peaks at index 42 and falls to 0x3B71
// at index 63), the quadrant mirroring used quadrant[1] instead of quadrant[0]
// (:54), and cos was read as sin_lut[63-idx] which is one LUT step off
// (:58). Module name, ports and pipeline depth (2 cycles from phase to
// output) are unchanged.
//
// Phase: 32-bit accumulator; the top 8 bits address a 256-step circle
// (quadrant = [7:6], index = [5:0]); a 65-entry table holds sin(90deg*i/64),
// i = 0..64, so that cos(theta) = sin_lut[64 - idx] is exact at the table
// points. Phase truncation to 8 bits limits spurs to about -48 dBc, adequate
// for the beta; a finer table (or CORDIC) is a possible improvement.
// Output amplitude: 32767 full scale (sin_out/cos_out, 16-bit signed).
// ============================================================================
module nco_400m_enhanced (
    input  wire               clk_400m,
    input  wire               reset_n,
    input  wire [31:0]        frequency_tuning_word,
    input  wire               phase_valid,
    input  wire [15:0]        phase_offset,
    output reg  signed [15:0] sin_out,
    output reg  signed [15:0] cos_out,
    output reg                dds_ready
);
    reg [31:0] phase_accumulator;
    reg [31:0] phase_with_offset;
    reg        phase_valid_d1;

    // quarter-wave sine table, 65 entries (0 .. 90 degrees inclusive)
    reg [15:0] sin_lut [0:64];
    initial begin
    sin_lut[ 0] = 16'h0000; sin_lut[ 1] = 16'h0324; sin_lut[ 2] = 16'h0648; sin_lut[ 3] = 16'h096A;
    sin_lut[ 4] = 16'h0C8C; sin_lut[ 5] = 16'h0FAB; sin_lut[ 6] = 16'h12C8; sin_lut[ 7] = 16'h15E2;
    sin_lut[ 8] = 16'h18F9; sin_lut[ 9] = 16'h1C0B; sin_lut[10] = 16'h1F1A; sin_lut[11] = 16'h2223;
    sin_lut[12] = 16'h2528; sin_lut[13] = 16'h2826; sin_lut[14] = 16'h2B1F; sin_lut[15] = 16'h2E11;
    sin_lut[16] = 16'h30FB; sin_lut[17] = 16'h33DF; sin_lut[18] = 16'h36BA; sin_lut[19] = 16'h398C;
    sin_lut[20] = 16'h3C56; sin_lut[21] = 16'h3F17; sin_lut[22] = 16'h41CE; sin_lut[23] = 16'h447A;
    sin_lut[24] = 16'h471C; sin_lut[25] = 16'h49B4; sin_lut[26] = 16'h4C3F; sin_lut[27] = 16'h4EBF;
    sin_lut[28] = 16'h5133; sin_lut[29] = 16'h539B; sin_lut[30] = 16'h55F5; sin_lut[31] = 16'h5842;
    sin_lut[32] = 16'h5A82; sin_lut[33] = 16'h5CB3; sin_lut[34] = 16'h5ED7; sin_lut[35] = 16'h60EB;
    sin_lut[36] = 16'h62F1; sin_lut[37] = 16'h64E8; sin_lut[38] = 16'h66CF; sin_lut[39] = 16'h68A6;
    sin_lut[40] = 16'h6A6D; sin_lut[41] = 16'h6C23; sin_lut[42] = 16'h6DC9; sin_lut[43] = 16'h6F5E;
    sin_lut[44] = 16'h70E2; sin_lut[45] = 16'h7254; sin_lut[46] = 16'h73B5; sin_lut[47] = 16'h7504;
    sin_lut[48] = 16'h7641; sin_lut[49] = 16'h776B; sin_lut[50] = 16'h7884; sin_lut[51] = 16'h7989;
    sin_lut[52] = 16'h7A7C; sin_lut[53] = 16'h7B5C; sin_lut[54] = 16'h7C29; sin_lut[55] = 16'h7CE3;
    sin_lut[56] = 16'h7D89; sin_lut[57] = 16'h7E1D; sin_lut[58] = 16'h7E9C; sin_lut[59] = 16'h7F09;
    sin_lut[60] = 16'h7F61; sin_lut[61] = 16'h7FA6; sin_lut[62] = 16'h7FD8; sin_lut[63] = 16'h7FF5;
    sin_lut[64] = 16'h7FFF;
    end

    wire [7:0] lut_address = phase_with_offset[31:24];
    wire [1:0] quadrant    = lut_address[7:6];   // 00: 0-90, 01: 90-180, 10: 180-270, 11: 270-360
    wire [5:0] idx         = lut_address[5:0];
    wire [6:0] idx_mirror  = 7'd64 - {1'b0, idx};

    // table reads (asynchronous ROM read, registered one stage later)
    wire [15:0] lut_a = sin_lut[idx];          // sin for Q1/Q3, cos for Q2/Q4
    wire [15:0] lut_b = sin_lut[idx_mirror];   // cos for Q1/Q3, sin for Q2/Q4

    always @(posedge clk_400m or negedge reset_n) begin
        if (!reset_n) begin
            phase_accumulator <= 32'h0000_0000;
            phase_with_offset <= 32'h0000_0000;
            phase_valid_d1    <= 1'b0;
            dds_ready         <= 1'b0;
            sin_out           <= 16'sh0000;
            cos_out           <= 16'sh7FFF;
        end else begin
            phase_valid_d1 <= phase_valid;
            if (phase_valid) begin
                phase_accumulator <= phase_accumulator + frequency_tuning_word;
                phase_with_offset <= phase_accumulator + {phase_offset, 16'b0};
                dds_ready         <= 1'b1;
            end else begin
                dds_ready         <= 1'b0;
            end

            if (phase_valid_d1) begin
                case (quadrant)
                    2'b00: begin sin_out <=  $signed({1'b0, lut_a[14:0]}); cos_out <=  $signed({1'b0, lut_b[14:0]}); end
                    2'b01: begin sin_out <=  $signed({1'b0, lut_b[14:0]}); cos_out <= -$signed({1'b0, lut_a[14:0]}); end
                    2'b10: begin sin_out <= -$signed({1'b0, lut_a[14:0]}); cos_out <= -$signed({1'b0, lut_b[14:0]}); end
                    default: begin sin_out <= -$signed({1'b0, lut_b[14:0]}); cos_out <=  $signed({1'b0, lut_a[14:0]}); end
                endcase
            end
        end
    end
endmodule
