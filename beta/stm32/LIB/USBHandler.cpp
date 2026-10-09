#include "USBHandler.h"
#include <cstring>

/*
 * BETA changes vs. 9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp
 * (CHANGELOG.md, defect fix C5 + robustness):
 *  - processStartFlag(): guard against length < 4 (unsigned underflow made the
 *    search loop read out of bounds for short packets).
 *  - processSettingsData(): the GUI zero-pads every USB packet to 64 bytes
 *    (GUI_V5.py:444-446). The padding that follows the 4-byte start flag used to
 *    be copied into usb_buffer, so "SET" was never at offset 0 and settings were
 *    never accepted. The receiver now synchronises on the "SET" marker: bytes
 *    before it are discarded (keeping up to 2 bytes that may be a partial marker
 *    straddling a packet boundary). Both padded and unpadded framing parse.
 *  - A packet that fails validation resets the buffer and re-synchronises
 *    instead of leaving stale bytes in front of the next attempt.
 */

USBHandler::USBHandler() {
    reset();
}

void USBHandler::reset() {
    current_state = USBState::WAITING_FOR_START;
    start_flag_received = false;
    buffer_index = 0;
    synced_on_set = false;
    current_settings.resetToDefaults();
}

void USBHandler::processUSBData(const uint8_t* data, uint32_t length) {
    if (data == nullptr || length == 0) {
        return;
    }

    switch (current_state) {
        case USBState::WAITING_FOR_START:
            processStartFlag(data, length);
            break;

        case USBState::RECEIVING_SETTINGS:
            processSettingsData(data, length);
            break;

        case USBState::READY_FOR_DATA:
            // Ready to receive radar data commands
            // Add additional command processing here if needed
            break;
    }
}

void USBHandler::processStartFlag(const uint8_t* data, uint32_t length) {
    // Start flag: bytes [23, 46, 158, 237]
    const uint8_t START_FLAG[] = {23, 46, 158, 237};

    if (length < 4) {
        return;  // cannot contain the flag; ignore (BETA guard)
    }

    // Check if start flag is in the received data
    for (uint32_t i = 0; i + 4 <= length; i++) {
        if (memcmp(data + i, START_FLAG, 4) == 0) {
            start_flag_received = true;
            current_state = USBState::RECEIVING_SETTINGS;
            buffer_index = 0;  // Reset buffer for settings data
            synced_on_set = false;

            // If there's more data after the start flag, process it (it is
            // normally the GUI's zero padding, which the sync logic discards).
            if (length > i + 4) {
                processSettingsData(data + i + 4, length - i - 4);
            }
            return;
        }
    }
}

void USBHandler::processSettingsData(const uint8_t* data, uint32_t length) {
    // Add data to buffer
    uint32_t bytes_to_copy = (length < (MAX_BUFFER_SIZE - buffer_index)) ?
                             length : (MAX_BUFFER_SIZE - buffer_index);

    memcpy(usb_buffer + buffer_index, data, bytes_to_copy);
    buffer_index += bytes_to_copy;

    // Synchronise on the "SET" marker: drop everything in front of it.
    if (!synced_on_set) {
        uint32_t k = 0;
        bool found = false;
        for (; buffer_index >= 3 && k + 3 <= buffer_index; k++) {
            if (memcmp(usb_buffer + k, "SET", 3) == 0) {
                found = true;
                break;
            }
        }
        if (found) {
            if (k > 0) {
                memmove(usb_buffer, usb_buffer + k, buffer_index - k);
                buffer_index -= k;
            }
            synced_on_set = true;
        } else {
            // Keep at most the last 2 bytes (possible partial "SE" marker).
            uint32_t keep = (buffer_index > 2) ? 2 : buffer_index;
            if (keep > 0 && buffer_index > keep) {
                memmove(usb_buffer, usb_buffer + buffer_index - keep, keep);
            }
            buffer_index = keep;
            return;
        }
    }

    // Check if we have a complete settings packet (contains "SET" and "END")
    if (buffer_index >= 74) {  // Minimum size for valid settings packet
        bool has_end = false;

        for (uint32_t i = 3; i + 3 <= buffer_index; i++) {
            if (memcmp(usb_buffer + i, "END", 3) == 0) {
                has_end = true;

                // Parse the complete packet up to "END"
                if (current_settings.parseFromUSB(usb_buffer, i + 3)) {
                    current_state = USBState::READY_FOR_DATA;
                } else {
                    // Invalid content: discard and wait for a fresh "SET" packet.
                    buffer_index = 0;
                    synced_on_set = false;
                }
                break;
            }
        }

        // If we didn't find a valid packet but buffer is full, reset
        if (buffer_index >= MAX_BUFFER_SIZE && !has_end) {
            buffer_index = 0;  // Reset buffer to avoid overflow
            synced_on_set = false;
        }
    }
}
