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

## 7. Bridge command set v2 (register access) — added 2026-10-09, RTL implemented 2026-10-09

All transfers: `FPGA_CS_N` low, SPI mode 0, MSB first; first byte = command. Bytes marked ← are driven by the FPGA on MISO (the master clocks dummy 0x00). Implemented in `beta/fpga/rtl/host_bridge_spi.v` (copy in `rtl/`), firmware counterpart `beta/stm32/Core/Src/host_bridge_proto.c`, verified by `beta/fpga/tb/tb_host_bridge_top.v` (through `radar_system_top`) and `rtl/tb_host_bridge.v` (unit).

| Cmd | Total bytes | Bytes after the command | Reply | Meaning |
|---|---|---|---|---|
| 0x01 | 1 + frame + 2 | — | frame + CRC (as §5); all zeros when no frame is pending (no sync word) | read the pending range-Doppler frame (unchanged) |
| 0x02 | 8 | a0 = addr[7:0], a1 = addr[15:8], d0..d3 = data[7:0]..[31:24], xx | ← byte 7 = 0xA2 (ack = command accepted; the write commits in the clk domain within ~5 clk cycles) | write register word `addr` |
| 0x03 | 7 | a0, a1, xx, xx, xx, xx | ← bytes 3..6 = d0 d1 d2 d3 (little-endian). No turnaround byte: the read is launched when a0 is complete; a1 is accepted but not decoded (the map has 5 address bits, so a1 must be 0) | read register word `addr` |
| 0x04 | 9 | xx × 8 | ← bytes 1..8 = four little-endian u16: status word, RTL version (0x0002), frames produced, 0x0000 | status without touching the frame |
| other (incl. 0x00) | any | — | ← 0xEE on every following byte | unknown command (ignored) |

Status word (assembled in `radar_system_top.v`): bit0 frame ready (= DRDY), bit1 ADAR CS conflict (sticky: an ADAR1000 CS was low while `FPGA_CS_N` was low), bit2 ADC capture FIFO overflow (sticky, `ADC_CAPTURE_MODE = 1`), bit3 calibration lock (all 8 lanes locked), bit4 packer overflow (a frame was dropped since reset), bits 5..15 = 0. The status is sampled when the command byte completes (quasi-static values; `frames produced` may be one behind).

Register map — word addresses, **16-bit registers** (data[31:16] are ignored on write and read as 0). Source of truth: `beta/fpga/rtl/radar_control_regs.v` (address-map comment and the two `case` statements); this table is kept identical to it. `toggle` = write 1 to the bit to pulse the action, reads as 0; `level` = stored bit.

| Addr | Name | Access | Reset | Bits |
|---|---|---|---|---|
| 0x00 | CONTROL | rw | 0x0005 | bit0 use_long_chirp, bit1 adc_pwdn, bit2 usb_enable |
| 0x01 | CFAR_THR | rw | 10000 | [15:0] |I|+|Q| detection threshold |
| 0x02 | DECIM | rw | 0x0001 | [1:0] range decimation mode (01 = peak) |
| 0x03 | START_BIN | rw | 0 | [9:0] first range bin passed to the decimator |
| 0x04 | CAL_CTRL | rw | 0 | bit0 start auto calibration (toggle), bit1 manual tap load (toggle), bit2 bitslip load (toggle), bit3 pattern-check enable (level), bit4 blind method (level: 0 = ADC test pattern, 1 = CW tone at the IF) |
| 0x05 | CAL_LANE | rw | 0 | [2:0] lane for CAL_TAP / CAL_SLIP writes and CAL_LANE_INFO / CAL_BLIND_MIN reads |
| 0x06 | CAL_TAP | rw | 16 | [4:0] manual IDELAY tap |
| 0x07 | CAL_SLIP | rw | 0 | [1:0] BITSLIP pulses for a manual bitslip load |
| 0x08 | CAL_PATT | rw | 0x55AA | {pattern_b[7:0], pattern_a[7:0]} expected alternating ADC test codes |
| 0x09 | CAL_STAT | ro | — | {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]} |
| 0x0A | CAL_LANE_INFO | ro | — | {1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]} of CAL_LANE |
| 0x0B | CAL_ERR | ro | — | pattern-check error counter (saturating) |
| 0x0C | CAL_UNDET | ro | — | {8'b0, undetermined[7:0]} |
| 0x0D | CAL_BLIND_COEF | rw | 0xEC39 | signed Q1.14 cos(2π·f_IF/f_S) for the blind notch (0xEC39 = −5063 = 120 MHz at 400 MSPS) |
| 0x0E | CAL_BLIND_MARGIN | rw | 0x0040 | absolute part of the blind pass margin (a tap passes when metric ≤ min + margin + min/16) |
| 0x0F | ID | ro | 0xBE7A | beta build identifier |
| 0x10 | CAL_BLIND_MIN | ro | — | minimum blind metric (Σ|r| over the window, >> 4, saturated) of CAL_LANE |

Registers that earlier revisions of this section listed but that do **not** exist in the RTL (run bit, mixers enable, NCO tuning word) have been removed from the table; `use_long_chirp` is CONTROL bit0.

STM32 API: `HostBridge_WriteReg(addr, value)`, `HostBridge_ReadReg(addr, &value)`, `HostBridge_Status(&st)`; exposed to the GUI through the existing settings path as a text command `REG W <addr> <value>` / `REG R <addr>` → reply `REG <addr> <value>` in the status stream (ASCII, so the bridge-frame parser passes it through).
