# Unmodified originals not compiled in the beta build

| File | Original defect / reason it is not used |
|---|---|
| `ad9484_interface_400m.v` | orphan in the original; superseded by `../ad9484_lvds_to_cmos_400m.v` (IBUFDS + IDDR capture written to the receiver's port list) |
| `lvds_to_cmos_400m.v` | IBUFDS -> BUFG -> flop re-sampling its own clock (`:35-43`); the DCO BUFG now lives in `ad9484_lvds_to_cmos_400m.v` |
| `cdc_modules.v` | `cdc_adc_to_processing` Gray-codes arbitrary data (`:74`), not a valid CDC; replaced by `../async_fifo.v`. `cdc_single_bit` / `cdc_handshake` were orphans |
| `latency_buffer_2159.v` | fixed-delay reference alignment (LATENCY 3187) replaced by address-driven reference fetch in `../matched_filter_processing_chain.v`; asynchronous read (`:102`) blocks BRAM inference |
| `usb_packet_analyzer.v` | verification helper using SystemVerilog `typedef enum` in a `.v` file (`:27`); the beta testbenches contain their own packet checker |

These copies are byte-identical to `9_Firmware/9_2_FPGA/` (line endings normalised) and are kept for traceability only.
