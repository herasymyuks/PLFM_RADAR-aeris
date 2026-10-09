# System overview — what AERIS-10 is

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** system description SOURCE-DERIVED (reconstructed from the four EAGLE schematics, the firmware and the RTL); variant table and performance targets ORIGINAL PROJECT FILE (README claims, not verified); calculated performance PROPOSED DESIGN / BETA (DSN-CALC-01, with stated assumptions); figures F1.1 SOURCE-DERIVED, F1.2 and F1.3 ORIGINAL PROJECT FILE. Eight configuration conflicts K1–K8 between the CAD and the documentation remain open.

**Sources:** `README.md`, `00_notation/parameter_table.md`, `docs/SYSTEM/BLOCK_DIAGRAM.md`, `docs/AERIS10_BETA_ENGINEERING_REPORT.md`, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, `engineering/SYSTEM/architecture/README.md`, `02_hardware/01_system_overview.md`.

**Planned figures:** F1.1 system block diagram (SYS-01), F1.2 original draw.io block diagram, F1.3 prototype photographs.

## 1. Purpose and principle

AERIS-10 is described by its upstream README as "an open-source, low-cost 10.5 GHz phased array radar system featuring Pulse Linear Frequency Modulated (LFM) modulation", available in two versions (3 km and 20 km range) for researchers, drone developers and SDR enthusiasts (source: `README.md`, introduction). The radar transmits linear-frequency-modulated pulses (chirps) at X-band, steers the beam electronically in elevation with four ADAR1000 beamformer ICs across a 16-element linear array, rotates the head mechanically in azimuth with a stepper motor, and processes the echoes in an FPGA (down-conversion, decimation, pulse compression, Doppler FFT, detection) before sending results to a host PC running a Python GUI (source: `README.md`, "Processing Pipeline"; `engineering/DESIGN/00_DESIGN_BASIS.md` §1, row "Array").

The carrier frequency f_c = 10.5 GHz and wavelength λ = 0.02857 m are the canonical values (source: `00_notation/parameter_table.md`, "Inconsistency Resolutions" §1; `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp:1133`). The pulse timing coded in the firmware is: long chirp 30 µs at PRI 167 µs, short chirp 0.5 µs at PRI 175 µs, guard 175.4 µs, 32 chirps per beam position, 31 elevation positions, 50 azimuth positions per revolution (source: `main.cpp:178-184`, `main.cpp:190`; `00_notation/parameter_table.md`, "Waveform and Timing"). The chirp bandwidth B is **TBD** in the parameter table ("Requires ADF4382 config"); every range-resolution and range-equation number in this manual that depends on B says so explicitly.

![F1.1 — System block diagram SYS-01, all subsystems with status legend — SOURCE-DERIVED; antenna, host PC, 22 V supply and off-board modules are CONCEPTUAL (source: engineering/SYSTEM/block_diagrams/system_block_diagram.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SYSTEM/block_diagrams/system_block_diagram.png)

Figure F1.1 shows what is wired in the CAD, not what the README describes; every box and edge is traceable to a repository file (source: `engineering/SYSTEM/architecture/README.md`, row SYS-01). The original designer's block diagram is reproduced as F1.2 for comparison; it labels the FPGA XC7A50T-2FTG256 and names the parts FPGA, AD9708, ADF4382 TX/RX, LTC5552 ×2, LPF/BPF, AD9484, EP4RKU+, ADAR1000 ×4, ADTR1107, M3SWA2-34DR+, FT601, STM32F746ZGT7, AD8352, OCXO ECOC-2522-10.000, AD9523, XO CCHD-957-100, VCXO CVHD-950-100.000, MTX2-143+, ATS1005-3DB and "QPA2862 ×4" (the CAD has QPA2962_B) (source: `engineering/SYSTEM/architecture/README.md`, row SYS-01, "RADAR_V6.drawio original block names").

![F1.2 — Original functional block diagram RADAR_V6, draw.io 29.6.1 export — ORIGINAL PROJECT FILE, upstream authorship, not dimensioned (source: 2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg; as found)](2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg)

## 2. Variants

The README specifies two variants (source: `README.md`, "Technical Specifications", copied verbatim):

| Parameter | AERIS-10N (Nexus) | AERIS-10X (Extended) |
|---|---|---|
| **Frequency** | 10.5 GHz | 10.5 GHz |
| **Max Range** | 3 km | 20 km |
| **Antenna** | 8x16 Patch Array | 32x16 Slotted Waveguide |
| **Beam Steering** | Electronic (±45°) | Electronic (±45°) |
| **Mechanical Scan** | 360° (stepper motor) | 360° (stepper motor) |
| **Output Power** | ~1Wx16 | 10Wx16 (GaN amplifier) |
| **Processing** | FPGA + STM32 | FPGA + STM32 |

The hardware notes add the following per-variant differences (source: `02_hardware/01_system_overview.md` §2.1, copied; gains are marked TBD in the source):

| | Nexus (AERIS-10N) | Extended (AERIS-10X) |
|---|---|---|
| Transmit power P_t per element | 1 W (ADTR1107) | 10 W (QPA2962 GaN) |
| Antenna type | 8x16 patch array | 32x16 slotted waveguide |
| Antenna gain G | ~20 dBi (patch, TBD) | ~30 dBi (waveguide, TBD) |
| Detection range R_max | 3 km | 20 km |

Three facts qualify this table. (1) The README names the PA-board variant "AERIS-10E" in one place and "AERIS-10X" elsewhere (source: `README.md:79` vs `README.md:24,83`); this manual uses AERIS-10X. (2) The "±45°" steering figure is a README statement; the firmware phase table spans −160° to +160° and the parameter table derives from it a steering range it states as "approximately ±33°" (source: `00_notation/parameter_table.md`, "Inconsistency Resolutions" §4) — the arithmetic disagreement between the project's own documents is recorded as observation MAN-01 in chapter 17. (3) No antenna CAD exists for either variant (conflict K8); the only antenna geometry in the repository is the PROPOSED 16-row × 8-patch panel of `engineering/DESIGN/ANTENNA/` (chapter 8).

![F1.3 — Prototype antenna array photograph — ORIGINAL PROJECT FILE, undimensioned, not used for any dimension in this manual (source: 8_Utils/Antenna_Array.jpg; as found)](8_Utils/Antenna_Array.jpg)

![F1.3b — Prototype electronics photograph — ORIGINAL PROJECT FILE, undimensioned, not used for any dimension in this manual (source: 8_Utils/0044.jpg; as found)](8_Utils/0044.jpg)

## 3. Subsystems as evidenced by the CAD

The system consists of four PCB types, an antenna, a pedestal and off-board modules. Board sizes and layer counts come from the EAGLE board files; part counts from the schematics (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §1, Mermaid diagram node labels; `engineering/DESIGN/00_DESIGN_BASIS.md` §1, rows "PA board", "Other boards"):

| Subsystem | Size / layers | Key parts (reference designators) | CAD status | Chapter |
|---|---|---|---|---|
| Power Supply Board | 280 × 300 mm, 2 layers, 8 holes | X1 AK300/2 VIN 12–17 V; 21 × TPS562208, 6 × ADM7151, 2 × TPS7A8300, 5 × LM2662; 34 rail outputs X2..X35; enable bus SV1 | layout unfinished in the source (308 unconnected before BETA, 89 after) | 5 |
| Frequency Synthesizer Board | 100 × 100 mm, 6 layers, 4 holes | X4 OCXO 100 MHz, X5/X6 VCXO 50 MHz (schematic values; K7); IC1 AD9523; U1 ADF4382 TX LO; U6 ADF4382 RX LO | complete; only board with a designer P&P/BOM export | 6 |
| Main Board | 260 × 300 mm, 10 layers, 10 holes | U2 STM32F746ZGT7; U42 XC7A50T-2FTG256I (K1); U1 AD9484 8-bit 400 MSPS; U3 AD9708 8-bit DAC; U5/U13 LTC5552 mixers; 4 × ADAR1000; 16 × ADTR1107; 17 × M3SWA2-34DR+; U6 FT601 (0 of 77 pins connected, K3); X53 mini-USB | layout unfinished in the source (15 unconnected before BETA, 0 after) | 4 |
| RF PA board (×16, AERIS-10X only) | 35 × 60 mm, 4 layers, 7 × Ø3.2 holes | U$1 QPA2962 GaN 10 W; J1 RFIN / J2 RFOUT; X2 VG; X3 VD/VIN_M sense; `22V` AK300/2 terminal | complete (1 clearance DRC item in the source) | 7 |
| Antenna array | — | 8×16 patch (Nexus) or 32×16 slotted waveguide (Extended) per README | NO CAD (K8); PROPOSED panel exists | 8 |
| Off-board modules | — | GPS (UART5), GY-85 IMU + BMP180 (I2C3), 8 × TMP37 via ADS7830, stepper driver (PD4/PD5), fan relay (PD7), PA drain switch (PD6) | named only; no part numbers, no module schematics | 3, 9 |
| Host PC | — | Python GUI; USB 2.0 full-speed CDC on X53 is the only host data link in the CAD | GUI_V5 (hardware) / GUI_V6_Demo (offline) in the source; `beta/gui` package | 13 |

The README's description of the processing pipeline (waveform generation in the DAC, up/down conversion in the LT5552 mixers, beam steering by the ADAR1000s, FPGA processing of ADC capture → I/Q down-conversion → CIC/FIR decimation → pulse compression → Doppler FFT → MTI/CFAR, STM32 system management, Python visualisation) is the design intent (source: `README.md`, "Processing Pipeline"). Chapter 2 states what the RTL as committed and the BETA RTL actually implement; the differences are material (no MTI, fixed-threshold "CFAR" placeholder, no wired FPGA→host path).

## 4. Documented versus verified: conflicts K1–K8

Independent cross-reading of the CAD, the firmware, the RTL, the GUI and the documentation produced eight configuration conflicts that only the hardware owner can close (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §4, copied verbatim):

| # | Topic | A | B | Owner |
|---|---|---|---|---|
| K1 | FPGA part | CAD/xlsx/drawio XC7A50T-2FTG256I | README/docs/XDC XC7A100T | hardware designer |
| K2 | STM32 HSE | schematic 8 MHz crystal | firmware 25 MHz | hardware designer |
| K3 | Host data path | CAD: STM32 USB-FS only | RTL/GUI V6: FT601 USB 3.0; GUI V2–V5: FT2232H | system architect |
| K4 | PA supply | xlsx 16 × 22 V / 2 A | Power Board `Vin [12-17] V`, no 22 V rail | power designer |
| K5 | FPGA packet format | RTL `0xAA … 0x55` | GUI `A5C3 … CRC16` | software |
| K6 | ADF4382 pins | `main.h` PG6..PG15 (= schematic) | `adf4382a_manager.h` PG0..PG9 | firmware |
| K7 | Synth oscillators | schematic OCXO 100 MHz + 2 × VCXO 50 MHz | xlsx VCXO 100 MHz; firmware `vcxo_freq = 100 MHz` | RF designer |
| K8 | Antenna | README patch 8×16 / slotted 32×16 | two different waveguide simulations, no CAD | antenna designer |

The BETA work adopted interim assumptions for several of them without closing them: the BETA FPGA project targets `xc7a50tftg256-2`, the schematic part (K1); the BETA firmware clock tree is written for the real 8 MHz crystal (K2); the host path is implemented as option B (SPI bridge through the STM32 CDC) with option A (FT601 on a Main Board rev. B) prepared as a pin plan (K3); a 22 V supply module DSN-PSU-01 is proposed (K4); the bridge frame replaces both packet formats (K5); the ADF4382 pin collision is fixed in the BETA firmware (K6); K7 and K8 remain open, the antenna being a PROPOSED patch panel per decision D-01 (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4, §7, §8, §12; `beta/fpga/README.md`, "Remaining work" item 2). The full register with these interim positions is in chapter 17.

## 5. Performance targets versus calculated performance

The README targets (3 km Nexus, 20 km Extended) are not accompanied by a link budget in the upstream repository; the parameter table lists antenna gain, LNA noise figure and chirp bandwidth as TBD (source: `00_notation/parameter_table.md`, "TBD Tracking"). The BETA phase produced a single-pulse coherent range-equation estimate for the long chirp, using the simulated gain of the proposed antenna panel and an **assumed** bandwidth (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, both tables copied verbatim):

| Parameter | Value | Basis |
|---|---|---|
| f₀ / λ | 10.5 GHz / 28.57 mm | verified |
| TX power | 16 × 10 W (PSAT) = 160 W peak, coherent | QPA2962 datasheet; array coherence assumed |
| Antenna gain (TX = RX) | 22.6 dBi | one simulated row 11.5 dBi + 10·log10(16) − 1 dB feed/scan loss (proposed panel, D-01) |
| Chirp | T_c = 30 µs, **B = 50 MHz ASSUMED** (TBD in `parameter_table.md`) → pulse-compression gain 31.8 dB, ΔR = 3 m | firmware timing |
| Coherent integration | 16 long chirps → +12.0 dB | main.cpp |
| Noise figure / system losses | 4.0 dB / 6 dB | ADTR1107 2.5 dB NF + chain; losses assumed |
| Required SNR | 13 dB (Pd ≈ 0.9, Pfa 1e-6, Swerling 1) | standard |
| Unambiguous range (PRI 167 µs) | 25.1 km | firmware |

| Target RCS (m²) | R_max (km) |
|---|---|
| 0.01 | 1.9 |
| 0.1 | 3.4 |
| 1.0 | 6.0 |
| 10.0 | 10.6 |

The source's verdict (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, "Verdict"): with the proposed antenna, 16 × 10 W and 16-chirp integration, R_max(1 m²) ≈ 6.0 km — the 20 km Extended-variant goal is **not** reached and needs ≈ 21 dB more (longer coherent integration across the 31 elevations/azimuth dwell, a narrower B with the same T_c, lower losses, or a higher-gain antenna). The 3 km Nexus goal is met for RCS ≥ 0.1 m² (R ≈ 3.4 km); a 0.01 m² drone-class target falls near 1.9 km. Dominant unknowns: B (assumed), real array gain (16-row coupling not yet simulated), RF chain losses.

Two caveats apply to reading this estimate. First, it combines the Extended variant's PA power (16 × 10 W) with the proposed patch panel's simulated gain, i.e. neither variant of the README exactly; the Nexus variant with ~1 W per element would be 10 dB lower in transmit power, which the source does not evaluate. Second, nothing in the estimate has been measured: the gain comes from an openEMS simulation of one row (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §8) and the noise figure and losses are assumptions stated in the table.

## 6. Reconstruction state at a glance

The project is being rebuilt in three layers that this manual keeps separate: the upstream originals (ORIGINAL PROJECT FILE), the SOURCE-DERIVED engineering package generated from them (`engineering/`, 89 registered drawings, file check 333 OK, 0 problems; source: `engineering/DRAWING_REGISTER.md`, "Summary" and "File check"), and the PROPOSED / BETA additions (`engineering/DESIGN/`, `beta/`). Recovery tasks are tracked in `docs/04_RECOVERY_TASKS.md` (status summary at its 2026-10-08 date: 7 DONE, 20 OPEN, 9 BLOCKED, plus the R-ENG, R-DSN and R-BETA groups added 2026-10-09; source: `docs/04_RECOVERY_TASKS.md`, "Status summary" and the three added sections). Acceptance criteria and their current MET / NOT MET / NOT RUN state are in `docs/TESTING/ACCEPTANCE_CRITERIA.md`; the physical criteria (AC-F9, AC-S6, AC-S7, AC-B7, AC-E7) are all NOT RUN (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`, sections A–G).
