# FPGA → host data path — DSN-LINK-01 (PROPOSED DESIGN)

Rev A · 2026-10-09 · generator `tools/design_host_link.py` · status **PROPOSED DESIGN** (option B implemented as BETA code, not run on hardware; option A needs a Main Board revision).

## 1. Problem

The RTL streams radar data through an FT601 USB 3.0 FIFO (`usb_data_interface.v`), but on the Main Board **U6 (FT601Q) has 0 of 77 pins connected** — only the decoupling of its `+3V3_FT` rail exists (L19, C184–C186). The only wired host link is the STM32 USB-FS CDC (X53). Conflict K3.

## 2. Data-rate budget (from the RTL geometry and firmware timing)

| Quantity | Value | Basis |
|---|---|---|
| Range-Doppler cells per beam position | 64 × 32 = 2048 | `doppler_processor.v` (RANGE_BINS 64, 32 chirps) |
| Beam-position frame time | 5647.4 µs | `main.cpp:180-186` |
| Raw RTL packet stream (44 B per cell) | **16.0 MB/s** | `usb_data_interface.v` (11 × 32-bit words) |
| Compact map frame (8-bit log-magnitude per cell + header + ≤ 32 detections + CRC) | 2164 B → **383 kB/s** | this design, §5 |
| STM32 USB-FS CDC practical limit | ≈ 0.8–1.1 MB/s | USB 2.0 FS bulk (19 × 64 B per 1 ms frame max) |
| SPI1 STM32 ↔ FPGA (existing lines) | 27 Mbit/s ≈ 3.3 MB/s (DMA) | APB2 108 MHz / 4 (beta clock tree) |
| FT601 245 sync FIFO, 32 bit @ 100 MHz | up to 400 MB/s | FT601 |

Conclusion: the raw stream needs the FT601 (option A); the compact map fits the existing STM32 path with 3× margin (option B).

## 3. Options

| | A — FT601 on Main Board rev. B | B — SPI bridge via STM32 (no PCB change) | C — Ethernet mezzanine on bank 35 (future) |
|---|---|---|---|
| Hardware change | route U6 to bank 35 (46 I/Os), add USB 3 connector, crystal, RREF, ESD (`ft601_added_parts_BOM.csv`) | none: DIG_5/6/7 + SPI1 are already routed to the FPGA | new PCB with RGMII PHY on the 50 free bank-35 pins |
| Throughput | 400 MB/s | ≤ 1 MB/s (CDC-bound) | 100 MB/s |
| Firmware/RTL | RTL already written (fix 2-bit BE → 4-bit; honour TXE_N); host driver FTDI D3XX | new RTL `host_bridge_spi.v` + packer; STM32 `host_bridge.c`; GUI parser | new MAC/UDP stack |
| Risk | 10-layer board respin; USB 3 SI | protocol only; SPI1 shared with ADAR1000 (time-multiplexed) | highest |
| Decision | **D-16: target for rev. B** | **D-17: implement now (BETA)** | D-18: documented only |

## 4. Option A — pin plan (bank 35, all pins currently without nets)

`ft601_pin_assignment.csv` maps every FT601 signal to a free bank-35 pad (CLK on the MRCC pin C4 = `IO_L12N_T1_MRCC_35`); `ft601_bank35.xdc` is the matching constraint fragment. FT601 pad numbers come from the EAGLE library symbol used in the schematic (U6 `FT601Q-B-T`); the **FT601 datasheet is not in the repository** — AC timing, RREF value, VBUS limits and the 1.0 V core supply arrangement (VD10 pins) must be verified against it before the schematic is edited. Rev. B schematic work: connect U6 VCC33 (pads 20/24/38) and VCCIO (14/49/59/68) to `+3V3_FT`, GND pads, the 46 signals per the CSV, XI/XO crystal, RREF, VBUS divider, D±/SS pairs to the new connector through the ESD array; route the 32-bit bus as a length-matched group (±25 mm, 100 MHz single-ended, 50 Ω) on the two bank-35 side layers.

Decision D-19 for the RTL: widen `ft601_be` to 4 bits, drive `BE = 4'b1111` for full words, respect `TXE_N` back-pressure, add `ft601_reset_n`/`wakeup_n`/`siwu_n` as outputs — recorded for `beta/fpga` (not yet applied there).

## 5. Option B — SPI bridge (implemented, BETA)

Signals: `option_b_signal_map.csv`. Transfer: STM32 waits for DRDY (EXTI on PD14), pulls `FPGA_CS_N` low, clocks one command byte (0x01 = read frame) and then reads the frame over MISO with DMA (SPI1 mode 0, MSB first, ≤ 27 MHz); the FPGA holds the ADAR1000 pass-through idle while `FPGA_CS_N` is low; the firmware never starts an ADAR1000 SPI transaction while a bridge read is in progress (both share SPI1).

Frame (little-endian, `engineering/DESIGN/HOST_LINK/gui/bridge_frame.py` is the reference parser):

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | sync `0xA5 0x5A` |
| 2 | 1 | version = 1 |
| 3 | 1 | flags (bit0 = long-chirp set, bit1 = overflow since last frame) |
| 4 | 2 | sequence number |
| 6 | 1 | azimuth index (1..50) |
| 7 | 1 | elevation index (1..31) |
| 8 | 2 | chirp count |
| 10 | 1 | n_range = 64 |
| 11 | 1 | n_doppler = 32 |
| 12 | 2 | n_det (≤ 32) |
| 14 | 2 | reserved |
| 16 | 2048 | magnitude map, uint8 = 8·log2(|I|+|Q|) saturated, range-major |
| 2064 | 3·n_det | detections: range u8, doppler u8, mag u8 |
| end | 2 | CRC-16/CCITT-FALSE over bytes 0..end-1 |

The STM32 forwards each frame unchanged over CDC (`AERIS_USB_SendBridgeFrame`), interleaved with the existing status strings (the GUI stream parser resyncs on the sync word; status strings never contain `0xA5 0x5A`).

Files: `rtl/host_bridge_spi.v` (SPI slave + frame FIFO, 1 BRAM), `rtl/rd_map_packer.v` (cell → frame builder, CRC), `rtl/tb_host_bridge.v` (self-checking iverilog test: a behavioural SPI master reads a frame and checks sync/CRC/payload), `stm32/host_bridge.c/.h` (SPI1 DMA + EXTI + CDC forward), `gui/bridge_frame.py` (+ tests). Integration into `beta/fpga`, `beta/stm32`, `beta/gui` is recorded in their CHANGELOGs.

## 6. What remains

- Option A: Main Board rev. B schematic/layout (MDR-13), FT601 datasheet checks, FTDI D3XX host driver test; option B: bench test of the SPI timing (level shifter path is 3.3 V, no translation needed), CDC throughput measurement, firmware arbitration of SPI1 with the ADAR1000 writes.
