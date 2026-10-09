`timescale 1ns / 1ps

/**
 * level_shifter_interface.v
 * 
 * Simple level shifter interface for STM32 to ADAR1000 communication
 * Converts 3.3V SPI signals to 1.8V for ADAR1000 beamformer chips
 */

module level_shifter_interface (
    input wire clk,
    input wire reset_n,
    
    // 3.3V side (from STM32)
    input wire sclk_3v3,
    input wire mosi_3v3,
    output wire miso_3v3,
    input wire cs_3v3,
    
    // 1.8V side (to ADAR1000)
    output wire sclk_1v8,
    output wire mosi_1v8,
    input wire miso_1v8,
    output wire cs_1v8
);

// Simple level shifting through synchronization
reg sclk_sync, mosi_sync, cs_sync;
reg miso_sync;

always @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
        sclk_sync <= 1'b0;
        mosi_sync <= 1'b0;
        cs_sync <= 1'b1;
        miso_sync <= 1'b0;
    end else begin
        sclk_sync <= sclk_3v3;
        mosi_sync <= mosi_3v3;
        cs_sync <= cs_3v3;
        miso_sync <= miso_1v8;
    end
end

// Output assignments (direct connection with synchronization)
assign sclk_1v8 = sclk_sync;
assign mosi_1v8 = mosi_sync;
assign cs_1v8 = cs_sync;
assign miso_3v3 = miso_sync;

endmodule
