`timescale 1ns / 1ps
// tb_ddc_4x.v - the legacy 400 MHz DDC (ddc_400m_enhanced) and the polyphase DDC
// (ddc_4x_100m) receive the same offset-binary ADC sequence (two tones in the IF band
// plus noise plus a short chirp burst); the baseband outputs must agree within +/-1 LSB
// after alignment (the designs have different pipeline latencies). The first 64 outputs
// are excluded (the legacy mixer drops sample 0 - documented start-up difference).
module tb_ddc_4x #(
    parameter CIC_PHASE_TB = 0      // passed to ddc_4x_100m (0 = legacy decimation phase; sweep with -P to re-derive)
);
    localparam N = 8000;            // ADC samples
    localparam real PI = 3.14159265358979323846;
    reg clk_400m = 0, clk_100m = 0, reset_n = 0;
    always #1.25 clk_400m = ~clk_400m;
    always #5.0  clk_100m = ~clk_100m;

    // ---------------- source sequence ----------------
    reg [7:0] src [0:N-1];
    integer n, v;
    real s;
    initial begin
        for (n = 0; n < N; n = n + 1) begin
            s = 60.0 * $cos(2.0 * PI * 0.3375 * n) + 40.0 * $sin(2.0 * PI * 0.2375 * n + 0.7);   // 135 MHz and 95 MHz -> +15 / -25 MHz baseband
            if (n > 3000 && n < 5000) s = s + 20.0 * $cos(2.0 * PI * (0.30 * n + 0.5 * (n - 3000.0) * (n - 3000.0) / 40000.0));
            v = 128 + $rtoi(s) + ($random % 3);
            if (v < 0) v = 0; if (v > 255) v = 255;
            src[n] = v[7:0];
        end
    end

    // ---------------- legacy DUT (400 MHz sample stream) ----------------
    reg  [7:0] adc_data = 8'd128;
    reg        adc_valid = 0;
    wire signed [17:0] l_i, l_q;
    wire l_vi, l_vq;
    ddc_400m_enhanced legacy (
        .clk_400m(clk_400m), .clk_100m(clk_100m), .reset_n(reset_n), .reset_n_400m(reset_n),
        .mixers_enable(1'b1), .adc_data(adc_data), .adc_data_valid_i(adc_valid), .adc_data_valid_q(adc_valid),
        .baseband_i(l_i), .baseband_q(l_q), .baseband_valid_i(l_vi), .baseband_valid_q(l_vq),
        .ddc_status(), .ddc_diagnostics(), .mixer_saturation(), .filter_overflow(),
        .bypass_mode(1'b0), .test_mode(2'b00), .test_phase_inc(16'h0000), .force_saturation(1'b0),
        .reset_monitors(1'b0), .debug_sample_count(), .debug_internal_i(), .debug_internal_q(), .cdc_overflow()
    );

    // ---------------- polyphase DUT (4 samples per 100 MHz clock) ----------------
    reg  [31:0] word = 32'h80808080;
    reg         word_valid = 0;
    wire signed [17:0] p_i, p_q;
    wire p_vi, p_vq;
    ddc_4x_100m #(.CIC_PHASE(CIC_PHASE_TB)) poly (
        .clk(clk_100m), .reset_n(reset_n), .mixers_enable(1'b1), .bypass_mode(1'b0),
        .word(word), .word_valid(word_valid),
        .baseband_i(p_i), .baseband_q(p_q), .baseband_valid_i(p_vi), .baseband_valid_q(p_vq),
        .cic_i_dbg(), .cic_q_dbg(), .cic_valid_dbg()
    );

    // ---------------- stimulus ----------------
    integer si = 0, wi = 0;
    reg go = 0;                      // both streams start 100 ns after reset (enable synchronisers settled)
    initial begin wait (reset_n); #100 go = 1; end
    always @(posedge clk_400m) begin
        if (go && si < N) begin adc_data <= src[si]; adc_valid <= 1'b1; si = si + 1; end
        else adc_valid <= 1'b0;
    end
    always @(posedge clk_100m) begin
        if (go && wi < N) begin
            word <= {src[wi+3], src[wi+2], src[wi+1], src[wi]}; word_valid <= 1'b1; wi = wi + 4;
        end else word_valid <= 1'b0;
    end

    // ---------------- capture outputs ----------------
    integer L_i [0:N/4+100]; integer L_q [0:N/4+100]; integer nl = 0;
    integer P_i [0:N/4+100]; integer P_q [0:N/4+100]; integer np = 0;
    always @(posedge clk_100m) begin
        if (l_vi && l_vq && nl < N/4+100) begin L_i[nl] = l_i; L_q[nl] = l_q; nl = nl + 1; end
        if (p_vi && p_vq && np < N/4+100) begin P_i[np] = p_i; P_q[np] = p_q; np = np + 1; end
    end

    integer lag, best_lag, best_err, err, i, d, maxdiff, cmp, errors = 0, peak;
    initial begin
        #100 reset_n = 1;
        #(N * 2.5 + 3000);
        $display("outputs: legacy %0d, polyphase %0d", nl, np);
        if (nl < N/4 - 50 || np < N/4 - 50) begin $display("FAIL: too few outputs"); $fatal(1); end
        // alignment: lag minimising the mismatch count over the overlap (skip the first 64)
        best_lag = 0; best_err = 1 << 30;
        for (lag = -64; lag <= 64; lag = lag + 1) begin
            err = 0;
            for (i = 64; i < nl - 80; i = i + 1) begin
                if (i + lag >= 0 && i + lag < np) begin
                    d = L_i[i] - P_i[i + lag]; if (d < 0) d = -d; if (d > 1) err = err + 1;
                    d = L_q[i] - P_q[i + lag]; if (d < 0) d = -d; if (d > 1) err = err + 1;
                end else err = err + 1;
            end
            if (err < best_err) begin best_err = err; best_lag = lag; end
        end
        maxdiff = 0; cmp = 0; peak = 0;
        for (i = 64; i < nl - 80; i = i + 1) begin
            if (i + best_lag >= 0 && i + best_lag < np) begin
                d = L_i[i] - P_i[i + best_lag]; if (d < 0) d = -d; if (d > maxdiff) maxdiff = d;
                d = L_q[i] - P_q[i + best_lag]; if (d < 0) d = -d; if (d > maxdiff) maxdiff = d;
                if (L_i[i] > peak) peak = L_i[i]; if (-L_i[i] > peak) peak = -L_i[i];
                cmp = cmp + 1;
            end
        end
        $display("alignment lag %0d output samples, %0d samples compared, max |diff| = %0d LSB, |legacy| peak %0d", best_lag, cmp, maxdiff, peak);
        if (maxdiff > 1) begin errors = errors + 1; $display("FAIL: outputs differ by more than 1 LSB"); end
        if (cmp < 1500) begin errors = errors + 1; $display("FAIL: too few compared samples"); end
        if (peak < 1000) begin errors = errors + 1; $display("FAIL: signal level too low for a meaningful comparison"); end
        if (errors == 0) begin $display("PASS tb_ddc_4x: legacy 400 MHz DDC and polyphase DDC agree (%0d samples, max diff %0d LSB, lag %0d)", cmp, maxdiff, best_lag); $finish; end
        else begin $display("FAIL tb_ddc_4x: %0d errors", errors); $fatal(1); end
    end
endmodule
