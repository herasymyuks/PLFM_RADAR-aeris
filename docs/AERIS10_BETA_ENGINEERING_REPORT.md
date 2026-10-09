# AERIS-10 — BETA Engineering Report (consolidated)

Version 0.9 (draft, 2026-10-09) · companion to `AERIS10_ENGINEERING_BUILD_MANUAL.md` (v1.3 Part XIII) · repository `https://github.com/herasymyuks/PLFM_RADAR-aeris` (branch `main`).

This report consolidates everything that was built, simulated and calculated for the missing elements of AERIS-10 during the reconstruction and BETA phases, with the verification actually executed for each item and the decisions still owned by the hardware owner. Status words: **BETA** = builds/simulates/tests on the authoring machine, not on hardware; **PROPOSED** = new design content; **BLOCKED** = cannot be done without hardware, Vivado or an owner decision.

## 1. Executive summary

| Area | State before | State now | Executed evidence |
|---|---|---|---|
| FPGA RTL | did not parse; 5 modules/IP missing; 400 MHz fabric; no host path | parses/lints; all modules present; ISERDES 1:4 capture + 100 MHz polyphase DDC (bit-exact vs legacy); SPI host bridge; register map | `beta/fpga/build.sh`: 0 failures, 9 testbench runs PASS (§3) |
| STM32 firmware | no build system/HAL; 7+ defects; empty ADAR1000 phase tables | builds and links (93 KB flash); 12 defects fixed; ADAR1000 tables from the datasheet; bridge + REG commands | `beta/stm32/build.sh` exit 0; host tests 6/6 (§4) |
| Python GUI | V6 stub; no tests; wrong packet format | package with firmware-exact protocol, bridge-frame path, register panel, simulator; PyInstaller app | pytest 72 passed; selftests exit 0 (§5) |
| PCBs | no Gerbers; Main 15 / Power 308 unconnected; 0 MPN | Main/RF PA 0 unconnected; Power 89 (listed); BOM MPNs; fab notes; full packages; Main rev. B with FT601 (§6) | KiCad DRC reports, export logs |
| Host data path | FT601 unwired | option A pin plan (bank 35) + option B SPI bridge implemented end-to-end | tb PASS, firmware build, GUI tests on the RTL vector (§7) |
| Antenna | none | 16×8 patch panel, KiCad board, openEMS simulated | S11 −18 dB at f0, 128 MHz band, coupling −20.7 dB (§8) |
| Thermal / power | none | drain-gating requirement, 22 V module design, 2-D plate map | 64 °C plate / ≈ 73 °C PA base in case B (§9) |
| Mechanics | none | head + pedestal, 51-part detail model, flat patterns, parts list; torque check | FreeCAD model builds; register file check 0 problems (§10) |
| Radar performance | TBD everywhere | range equation with simulated gain | R(1 m²) ≈ 6 km at B = 50 MHz (§11) |

## 2. What is still impossible here

Vivado synthesis/timing/bitstream (open-source flow attempted — §3.4), flashing and bench tests, fabrication, measurement of component heights, antenna coupon on a VNA, PA thermal test, 89 Power Board pour connections (manual CAD), EAGLE schematic updates for rev. B, owner decisions K1–K8 and D-01…D-19.

## 3. FPGA (beta/fpga)

### 3.1 What exists
28 RTL files (15 modified copies of the originals, 9 new, 4 identical), `mem/` incl. generated `long_chirp_seg3`, 7 testbenches, XDC with datasheet input delays and schematic-derived pins (67/183 bits constrained; 116 UNRESOLVED ports are FT601/status/debug), Vivado Tcl, open-source synthesis scripts (§3.4).

### 3.2 Key technical findings
- The `.mem` references are **conjugate FFT-domain** chirp spectra (1024-point); the matched filter is therefore frequency-domain (FFT → × ref → IFFT) and must not conjugate again; `short_chirp_*.mem` matches neither domain → short-chirp path UNRESOLVED.
- AD9484 is SDR LVDS at the sample rate (datasheet); capture redesigned with ISERDESE2 1:4 (BUFIO/BUFR), IDELAYE2 calibration (pattern-based and blind), MMCM 200 MHz reference, async FIFO into `clk_100m`; the 4-phase DDC/CIC at 100 MHz is bit-exact against the legacy 400 MHz chain (8000 samples, max diff 0 LSB).
- Original bugs fixed beyond the inventory: FFT wrapper `tlast` off-by-one, Doppler FFT valid timing, NCO LUT not a sine, FIR/CIC multi-driven monitors, 2-bit FT601 byte-enable, USB packetizer/analyzer inconsistency.
- SPI host bridge (option B) integrated: packer → 2-bank frame RAM → SPI slave on the STM32 SPI1 lines; ADAR1000 pass-through gated during transfers; command set v2 (frame / write / read / status) — see §7.

### 3.3 Executed tests (build.sh)
| Test | Result |
|---|---|
| iverilog elaboration, sim and synth views | PASS |
| verilator --lint-only -Wall | 0 errors (warnings listed in logs) |
| tb_fft_wrappers (vs numpy, ±2 LSB) | PASS |
| tb_matched_filter (peak at expected bin) | PASS |
| tb_range_bin_decimator (128/128) | PASS |
| tb_adc_iserdes_capture (8/8 lanes lock, skewed lane compensated) | PASS |
| tb_ddc_4x (bit-exact vs legacy) | PASS |
| tb_host_bridge / tb_host_bridge_top (frame + register commands) | PASS |
| tb_system_smoke, ADC_CAPTURE_MODE 1 and 0 (pulse compression end-to-end, 2688 packets) | PASS |

### 3.4 Synthesis without Vivado
Open-source flow (`beta/fpga_synth/`, Yosys 0.69 `synth_xilinx -family xc7 -flatten -abc9`, snapshot 65cd160, FFT IP as 3 black boxes): **12 793 LUT (39 %, incl. 3 100 LUTRAM), 4 726 FF (7 %), 106/120 DSP48E1 (88 %), 2 RAMB18, 0 latches, 0 multi-driven**. nextpnr-xilinx (openXC7, chipdb xc7a50t generated from prjxray) packed every primitive (IBUFDS, BUFG, BUFIO, BUFR, IDELAYE2, IDELAYCTRL, ISERDESE2, MMCME2, DSP48E1, RAMB18E1) but placement did not complete (DSP cascade legalisation; SA placer unbounded retry) — **no open-source Fmax, no bitstream**.

Design consequences found by synthesis: (1) only 14 DSPs remain for the three FFT cores (2 × 1024-point + 1 × 32-point) — the design may not fit the XC7A50T as written (K1 decision: XC7A100T would); (2) six `ram_style=block` memories (chirp ROM, Doppler buffer, bridge frame RAM) have asynchronous reads and become ≈ 4 900 LUTs instead of ≈ 8 RAMB36 — needs registered reads; (3) `stm32_sclk_3v3` on J16 is not clock-capable but drives a BUFG — needs `CLOCK_DEDICATED_ROUTE FALSE` or an oversampled SPI slave in `clk_100m`; (4) the full top needs 192 package pins vs 170 user I/O on FTG256 — the 116 unconstrained debug/FT601 bits must leave the top for a board build.

### 3.5 Open
Vivado run (timing on BUFR/MMCM paths, IDELAYCTRL placement), ISERDES bit order on hardware (PN9 check), matched filter not pipelined (~270 µs/chirp with real IP latency vs 167 µs PRI), FFT IP generation, bank-14 LVDS inputs on a 3.3 V bank (UG471 check in §3.6).

### 3.6 UG471 documentary checks
UG471 v1.10 (fetched from the web archive, `build/docs_ext/ug471.txt`): ISERDESE2 "the first data bit received appears on the highest order Q output" → for SDR 1:4 the oldest bit is on Q4 (the beta model had Q1; fixed, `Q1_IS_OLDEST=0`); BITSLIP in SDR mode shifts the output pattern left by one per pulse, one CLKDIV pulse with a gap, latency two CLKDIV cycles (model corrected); LVDS_25 inputs are acceptable in banks powered at other voltages "provided DIFF_TERM = FALSE, VIN/VIDIFF requirements met" → bank 14 at 3.3 V is allowed for inputs with **external 100 Ω termination, which the schematic does not have** (board change, REQUIRES VERIFICATION). Quotes recorded in `beta/fpga/README.md` and the XDC header.

## 4. STM32 firmware (beta/stm32)
Build: CMake + Arm GNU 14.2.Rel1 + STM32CubeF7 (pinned); FLASH 93 276 B, RAM 17 480 B. Hand-written CubeMX-equivalent USB CDC/startup/linker; clock tree for the real 8 MHz crystal. Defects fixed: ADF4382 pin collision, `platform_ops = NULL`, unbound CDC RX, padded settings frames, GPS_Init, AD9523 CS/SPI speed, AD9523 double init (new), IDQ reading bug, printf to UART, ADAR1000 channel index (new, rotated the beam by one element). ADAR1000 vector-modulator tables filled from datasheet Tables 10–13 (128 rows, ≤ 3.1° encoding error). Bridge: frame forwarding + REG W/R text commands. Host tests 6/6 (settings parser incl. padding, beam matrix, AD9523 registers, I2C timing, ADAR tables, bridge commands). Open: CubeMX regeneration, hardware bring-up, per-board phase calibration.

## 5. Python GUI (beta/gui)
Package `aeris10_gui`; default hardware path = bridge frames over CDC (raw FT601 behind `--raw-ft601`); register map transcribed from the RTL; demo register file; PyInstaller bundle. 72 tests; selftests pass in both modes. Open: hardware CDC test, request IDs for REG replies (ordered matching today).

## 6. PCBs (beta/pcb)
| Board | Unconnected before → after | DRC after | Notes |
|---|---|---|---|
| Main | 15 → 0 | 1049 (U69/U7 paddle pads without net, dangling stubs, silk) | +3V3_FT cluster placed/routed; polygon nets dispositioned |
| Power | 308 → 89 | 328 | 132 parts placed by script; Freerouting 2.5.0; 89 pour-to-pour joins listed in `UNROUTED.md` |
| RF PA | 1 → 0 | 18 | 1 clearance in the source |
| Synth | 0 → 0 | 639 (capped; dispositioned) | silk nudged |
BOM MPN confidence per board in `BOM_<BOARD>_beta.csv`; stack-ups/impedance widths in `FAB_NOTES.md` (PROPOSED).
**Main Board rev. B (`beta/pcb/MAIN_BOARD_REVB/`, FT601 host interface):** FT601 fully wired in the KiCad netlist (64 new nets, 194 pad connections, USB-C receptacle, 30 MHz crystal, RREF, VBUS divider, ESD arrays, SuperSpeed coupling caps); first routing attempt with existing copper locked left 59 open connections because 36 of the 47 bank-35 balls have no escape under the existing fan-out; owner decision (2026-10-09): redo the bank-35 fan-out in rev. B — in progress (result in the rev. B README when finished). The EAGLE schematic must be updated by the designer to match; FT601 datasheet checks (RREF, VBUS, VD10, crystal load) are open.

## 7. Host data path (DSN-LINK-01)
Budget: raw RTL stream 16 MB/s needs the FT601 (option A, rev. B); compact map frame 383 kB/s fits the STM32 CDC (option B). Option A: 47 FT601 signals mapped to free bank-35 pins (CLK on MRCC), XDC fragment, added parts BOM. Option B: implemented and tested end-to-end in simulation; firmware and GUI implement the same frame and the same command set (write 0x02 with ack 0xA2, read 0x03, status 0x04). Bench test on hardware is open.

## 8. Antenna (DSN-ANT-01)
16 rows × 8 series-fed patches on RO4350B 0.508 mm (KiCad native board, Gerbers, STEP). openEMS (built from source): one row S11 = −18 dB at 10.5 GHz but only ≈ 128 MHz contiguous −10 dB band (comb of narrow resonances; −6…−8 dB between dips); row directivity 11.5 dBi; three-row coupling S12 ≈ −20.7 dB at f0 (−18.8 dB worst in band). Consequence: if the chirp bandwidth B exceeds ≈ 100 MHz, the row feed must change (travelling-wave or corporate) — decision D-01 rev. B.

## 9. Thermal and 22 V supply (DSN-THM-01, DSN-PSU-01)
QPA2962 dissipates 37 W per device when the drain is on. Firmware as coded (VD left on) → 591 W (case A, plate ≈ 213 °C in the 2-D model — infeasible). With per-chirp drain gating (11.5 % duty) → 68 W; 2-D finite-difference map of the 300×300×10 plate with two fin fields gives plate max 64 °C, PA base ≈ 73 °C at 45 °C ambient. 22 V module: 2-phase boost, LM5069 enable, 16 pulse gates, ≥ 2.7 mF bulk; requires a `TX_GATE` line (FPGA spare pin — UNRESOLVED).

## 10. Mechanics (DSN-MECH-*)
Head 315 × 315 × 133 mm with vertical boards; 51-part FreeCAD detail model (tray 7 bends, front plate, lid, PTFE window stack, PA plate with tapped holes and brackets, carrier rails, standoffs, gland plate; pedestal plates, bearing, GT3 pulleys, slip ring, motor bracket, mast flange), flat patterns with bend allowance, assembly section, parts list (286 fasteners). Mass estimates: head structure 6.4 kg (+ ≈ 4 kg boards/antenna/cables), pedestal 12.4 kg. **Torque check revises D-12:** a NEMA 23 with 1:3 needs ≥ 200 ms per 7.2° step (revolution ≈ 19 s); NEMA 34 allows ≈ 100 ms.

## 11. Radar performance (DSN-CALC-01 §3)
With 16 × 10 W, the simulated panel gain (≈ 22.5 dBi), T_c = 30 µs, 16-chirp integration, NF 4 dB, 6 dB losses and **B = 50 MHz assumed**: R_max ≈ 6 km (1 m²), 3.4 km (0.1 m²), 1.9 km (0.01 m²). The 3 km Nexus goal is met for RCS ≥ 0.1 m²; the 20 km Extended goal needs ≈ +21 dB (longer integration, narrower B, lower losses, higher gain).

## 12. Decisions required from the owner
K1 FPGA part, K2 HSE crystal (beta assumes 8 MHz), K3 host path (option A rev. B vs option B), K4 22 V supply/`TX_GATE` pin, K5 packet format (bridge frame proposed), K6 ADF4382 pins, K7 synth oscillators, K8 antenna variant; D-01 feed topology vs B, D-07 component heights, D-12 motor class/ratio, D-13 slip-ring channels, D-14 gating line, D-16…D-19 host link.

## 13. File index
`beta/README.md`, `engineering/README.md`, `engineering/DRAWING_REGISTER.md`, `engineering/DESIGN/README.md`, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md`, `engineering/DESIGN/ANTENNA/simulation/TUNING_LOG.md`, `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md`, `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`, `docs/04_RECOVERY_TASKS.md`, `docs/TESTING/ACCEPTANCE_CRITERIA.md`.
