#ifndef USBHANDLER_H
#define USBHANDLER_H

#include "RadarSettings.h"
#include <cstdint>

class USBHandler {
public:
    enum class USBState {
        WAITING_FOR_START,
        RECEIVING_SETTINGS,
        READY_FOR_DATA
    };
    
    USBHandler();
    
    // Process incoming USB data
    void processUSBData(const uint8_t* data, uint32_t length);
    
    // Check if start flag was received
    bool isStartFlagReceived() const { return start_flag_received; }
    
    // Get current settings
    const RadarSettings& getSettings() const { return current_settings; }
    
    // Get current state
    USBState getState() const { return current_state; }
    
    // BETA (bridge v2): ASCII "REG ..." command captured from CDC (ISR context) and
    // executed later from the main loop (SPI1 must not be used from the USB ISR).
    bool hasPendingCommand() const { return cmd_pending; }
    // Copies the pending command (NUL-terminated) and clears it; false if none.
    bool takePendingCommand(char* out, uint32_t cap);
    static constexpr uint32_t MAX_CMD_LEN = 64;

    // Reset USB handler
    void reset();

private:
    RadarSettings current_settings;
    USBState current_state;
    bool start_flag_received;
    
    // Buffer for accumulating USB data
    static constexpr uint32_t MAX_BUFFER_SIZE = 256;
    uint8_t usb_buffer[MAX_BUFFER_SIZE];
    uint32_t buffer_index;
    bool synced_on_set;
    volatile bool cmd_pending;
    char cmd_buf[MAX_CMD_LEN + 1];
    bool captureTextCommand(const uint8_t* data, uint32_t length);        // BETA: true once "SET" is at usb_buffer[0]
    
    void processStartFlag(const uint8_t* data, uint32_t length);
    void processSettingsData(const uint8_t* data, uint32_t length);
};

#endif // USBHANDLER_H