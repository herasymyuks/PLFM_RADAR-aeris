# Appendix D — Glossary, acronyms, symbols, status vocabulary and identifier families

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** reference appendix. Symbols are transcribed to plain text from `00_notation/symbol_table.md` (ORIGINAL PROJECT FILE); acronym expansions are standard engineering usage with the repository location where each term is used; the status vocabulary and identifier families are those of `manual/STYLE_GUIDE.md` and the registers cited in chapter 17.

**Sources:** `00_notation/symbol_table.md`, `00_notation/parameter_table.md`, `00_notation/conventions.md`, `manual/STYLE_GUIDE.md`, `engineering/SYSTEM/architecture/README.md`, `engineering/SYSTEM/interfaces/interconnection_table.md`, `docs/04_RECOVERY_TASKS.md`, `docs/TESTING/ACCEPTANCE_CRITERIA.md`, `docs/TESTING/VALIDATION_PLAN.md`, `docs/03_MISSING_COMPONENTS.md`, `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`.

**Planned figures:** none.

## 1. Acronyms and terms

| Term | Meaning in this manual | Where used (example) |
|---|---|---|
| ADC | analogue-to-digital converter; here the AD9484, 8-bit, 500 MSPS rated, operated at 400 MSPS | `00_notation/parameter_table.md` "RF Front-End"; chapter 2 §4 |
| ADAR1000 | four-channel X/Ku-band beamformer IC with 7-bit phase and gain control; four devices give 16 channels | `02_hardware/04_antenna_beamforming.md` §2 |
| ADF4382 | wideband PLL/VCO synthesizer used as TX LO (U1, 10.5 GHz) and RX LO (U6, 10.38 GHz) | chapter 3 §2.6 |
| AD9523 | low-jitter clock generator (IC1 on the Synth Board) producing the 400/120/100/20 MHz clocks and the 300 MHz ADF4382 reference | chapter 2 §4 |
| AD9708 | 8-bit DAC (U3) generating the chirp at 120 MHz | chapter 2 §4 |
| ADTR1107 | integrated X-band T/R front end (PA + LNA + switch), 16 devices, Nexus variant output stage | `README.md` "Main Board" |
| AF | array factor, AF(θ) | `01_physics/03_beamforming_theory.md` Eq. BF-3 |
| AGC | automatic gain control | `README.md` "FPGA" list (design intent only) |
| BETA | status label: builds/simulates/tests on a workstation, not on hardware | `manual/STYLE_GUIDE.md` |
| BOM | bill of materials | `docs/BOM/`, `beta/pcb/*/BOM_*_beta.csv` |
| BPF | band-pass filter; U$2/U$3 "BPF2" on the Main Board, part number NOT IDENTIFIED | chapter 2 §4 |
| BRAM | FPGA block RAM | `beta/fpga/README.md` resource estimate |
| BUFG / BUFIO / BUFR | Xilinx global / I/O / regional clock buffers | `beta/fpga/README.md` "ADC capture" |
| CA-CFAR | cell-averaging constant false alarm rate detector | `01_physics/04_detection_theory.md` §6 |
| CDC (1) | USB Communications Device Class (virtual serial port) — the STM32 host link on X53 | chapter 3 §2.8 |
| CDC (2) | clock-domain crossing (FPGA) | `beta/fpga/README.md` item 4 |
| CFAR | constant false alarm rate detection; a fixed-threshold PLACEHOLDER in the RTL | chapter 2 §2.3 |
| CIC | cascaded integrator–comb decimation filter (5 stages, decimate by 4) | `00_notation/parameter_table.md` "Signal Processing" |
| CPI | coherent processing interval (M chirps per beam position) | `00_notation/symbol_table.md` §1 |
| DAC | digital-to-analogue converter | chapter 2 §4 |
| DAC5578 | 8-channel I2C DAC driving the PA gate voltages VG_1..16 | chapter 3 §4.1 row `VG_1..16` |
| DDC | digital down-converter (NCO + mixer + CIC + FIR) | chapter 2 §5 |
| DIG_0..7 | STM32 PD8..PD15 handshake lines to the FPGA (new chirp/elevation/azimuth, mixers enable, reset; DIG_5..7 used by the option B bridge) | `docs/SYSTEM/BLOCK_DIAGRAM.md` §3 |
| DRC / ERC | design-rule check (PCB) / electrical-rule check (schematic) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-B1 |
| DRU | EAGLE design-rules file | `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md` MDR-07 |
| DSP48E1 | Xilinx 7-series DSP slice | `beta/fpga/README.md` resource estimate |
| DXF / STEP / STL | 2-D drawing exchange / 3-D CAD exchange / mesh formats | `engineering/MECHANICAL/` |
| EAGLE | Autodesk EAGLE, the native schematic/board CAD of the upstream project (`.sch`, `.brd`) | `4_Schematics and Boards Layout/` |
| eFuse | electronic fuse / hot-swap controller (LM5069 in DSN-PSU-01) | `engineering/DESIGN/00_DESIGN_BASIS.md` D-14 |
| ENOB / SQNR / SINAD | effective number of bits / signal-to-quantisation-noise ratio / signal-to-noise-and-distortion | `01_physics/05_noise_analysis.md` §5 |
| FFT / IFFT | fast Fourier transform / inverse; 1024-point range, 32-point Doppler | `00_notation/parameter_table.md` "Signal Processing" |
| FIR | finite impulse response filter | chapter 2 §5 |
| FMCW | frequency-modulated continuous wave; the physics notes use the FMCW formulation for the dechirp relations | `01_physics/01_fmcw_theory.md` |
| FPGA | field-programmable gate array; U42, Xilinx Artix-7 (XC7A50T per CAD, XC7A100T per README — K1) | chapter 1 §4 |
| FreeCAD | open-source MCAD used for the proposed head/pedestal model | `engineering/DESIGN/MECHANICAL/` |
| FT601 | FTDI USB 3.0 FIFO bridge (U6), placed but unwired on the Main Board | chapter 2 §6 |
| GaN | gallium nitride (QPA2962 PA technology) | `README.md` |
| Gerber | PCB photoplot data format | `engineering/PCB/<BOARD>/` |
| GT3 | 3 mm pitch timing belt profile (pedestal drive proposal) | `engineering/DESIGN/00_DESIGN_BASIS.md` D-12 |
| GUI | graphical user interface (Python, Tk) | `beta/gui/` |
| HAL | STM32Cube hardware abstraction layer | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` |
| HSE | STM32 high-speed external oscillator (8 MHz crystal vs 25 MHz firmware — K2) | chapter 17 §1 |
| I/Q | in-phase / quadrature components of a complex baseband signal | chapter 2 §5 |
| I2C / SPI / UART / USART | serial buses used by the STM32 to peripherals | chapter 3 §2.5, §2.8 |
| IDELAYE2 / ISERDESE2 / IDELAYCTRL | Xilinx input delay element / input serialiser-deserialiser / delay-control block used in the BETA ADC capture | `beta/fpga/README.md` "ADC capture" |
| IF | intermediate frequency, 120 MHz | `main.cpp:190` |
| IMU | inertial measurement unit (GY-85 module on I2C3) | chapter 3 §2.8 |
| INA241A3 | current-sense amplifier, 16 devices reading the PA drain shunts | chapter 3 §2.7 |
| IP core | vendor-supplied FPGA block (Xilinx xfft FFT cores, not generated) | `beta/fpga/ip/README.md` |
| IP54 | ingress-protection target of the proposed enclosure | `engineering/DESIGN/00_DESIGN_BASIS.md` D-08 |
| JTAG / SWD | FPGA test-access port (JP3) / ARM serial-wire debug (JP2) | chapter 3 §2.8 |
| KiCad | open-source PCB CAD used for the converted manufacturing packages and the proposed antenna | `engineering/PCB/`, `beta/pcb/` |
| LFM / PLFM | linear frequency modulation / pulsed LFM | `01_physics/02_lfm_waveform_model.md` |
| LNA | low-noise amplifier | `00_notation/parameter_table.md` "RF Front-End" |
| LO | local oscillator (TX LO 10.5 GHz, RX LO 10.38 GHz) | chapter 2 §4 |
| LTC5552 / LT5552 | wideband mixer (U5 up-converter, U13 down-converter); the README writes LT5552, the schematic LTC5552 | chapter 2 §4 |
| LUT | look-up table (chirp LUT in the FPGA; also FPGA logic resource) | `beta/fpga/README.md` |
| LVDS / LVDS_25 | low-voltage differential signalling; the ADC data standard and the FPGA I/O standard | chapter 3 §3 |
| M3SWA2-34DR+ | Mini-Circuits SPDT RF switch (17 devices) | chapter 2 §4 |
| MCU | microcontroller unit (STM32F746ZGT7, U2) | chapter 1 §3 |
| MMCM | Xilinx mixed-mode clock manager | `beta/fpga/README.md` |
| MPN | manufacturer part number | `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-B5 |
| MTI | moving-target indication (README intent; not implemented) | `README.md` |
| NCO | numerically controlled oscillator | chapter 2 §5 |
| NEMA 23 / NEMA 34 | stepper motor frame sizes (57 mm / 86 mm class) | `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §2 |
| NF | noise figure (dB) | `00_notation/symbol_table.md` §4 |
| OCXO / VCXO | oven-controlled / voltage-controlled crystal oscillator (X4; X5, X6 on the Synth Board — K7) | chapter 3 §4.1 row `+3V3_XO` |
| openEMS | open-source FDTD electromagnetic solver used for the antenna simulation | `engineering/DESIGN/ANTENNA/simulation/` |
| P&P | pick-and-place (component placement) file | `engineering/PCB/<BOARD>/assembly/` |
| PA | power amplifier (QPA2962 GaN 10 W on the RF PA board) | chapter 1 §3 |
| PAE / PSAT / IDQ | power-added efficiency / saturated output power / quiescent drain current of the PA | `engineering/DESIGN/00_DESIGN_BASIS.md` §1 row "PA" |
| PLL | phase-locked loop | chapter 2 §4 |
| PRF / PRI | pulse repetition frequency / interval | `00_notation/symbol_table.md` §1 |
| PSL | peak sidelobe level | `01_physics/02_lfm_waveform_model.md` Eq. LFM-21 |
| QPA2962 | Qorvo GaN power amplifier, 10 W class, 22 V drain | `engineering/DESIGN/00_DESIGN_BASIS.md` §1 |
| RCS | radar cross section σ | `00_notation/symbol_table.md` §4 |
| RF | radio frequency | — |
| RTL | register-transfer level (Verilog) description of the FPGA design | `beta/fpga/rtl/` |
| SDR (1) | single data rate (AD9484 LVDS output timing) | `beta/fpga/README.md` item 2 |
| SDR (2) | software-defined radio (README audience) | `README.md` |
| SMA / 2.92 mm | coaxial connector types (Main Board RF ports; proposed antenna connectors) | chapter 3 §2.7; D-05 |
| SNR | signal-to-noise ratio | `00_notation/symbol_table.md` §4 |
| STM32CubeMX / `.ioc` | ST configuration tool and its project file (absent from the repository) | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` |
| T/R | transmit/receive | `02_hardware/01_system_overview.md` §1.1 |
| TBP | time-bandwidth product B·T_c | `01_physics/02_lfm_waveform_model.md` Eq. LFM-5 |
| TBD | to be determined (value absent from every repository file) | `00_notation/parameter_table.md` "TBD Tracking" |
| TMP37 | analogue temperature sensor (8 devices via ADS7830) | chapter 3 §2.8 |
| TPS562208 / ADM7151 / TPS7A8300 / LM2662 | buck regulator / LDO / LDO / charge-pump inverter families on the Power Board | chapter 3 §4.1 |
| ULA | uniform linear array | `01_physics/03_beamforming_theory.md` §1 |
| VD / VG / VIN_M | PA drain voltage / gate voltage / drain-current sense return | chapter 3 §2.7 |
| Vivado | AMD/Xilinx FPGA toolchain (not available on the authoring machine) | `beta/fpga/README.md` |
| VNA | vector network analyser (antenna coupon measurement, NOT RUN) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-E7 |
| XDC | Xilinx design constraints file | `beta/fpga/constraints/` |

## 2. Mathematical symbols

Transcribed to plain text from `00_notation/symbol_table.md` (notation authority IEEE 686-2024 per that file); subscripts are written after an underscore, e.g. `T_c,1` for the long chirp duration.

| Symbol | Definition | Units |
|---|---|---|
| f_c | centre (carrier) frequency | Hz |
| B | chirp bandwidth (sweep range) | Hz |
| T_c | chirp duration (pulse width); T_c,1 long, T_c,2 short | s |
| μ | chirp rate, μ = B / T_c | Hz/s |
| f_b | beat frequency (IF after dechirp) | Hz |
| f_r | pulse repetition frequency; f_r,1 long mode, f_r,2 short mode | Hz |
| T_r | pulse repetition interval, T_r = 1/f_r; T_r,1, T_r,2 | s |
| τ | round-trip delay, τ = 2R/c | s |
| T_guard | guard time between chirp sequences | s |
| M | number of chirps per CPI (per beam position) | — |
| R, R_max, ΔR | range, maximum unambiguous range, range resolution | m |
| v, Δv | target radial velocity, velocity resolution | m/s |
| f_d | Doppler frequency shift | Hz |
| c | speed of light, ≈ 2.998 × 10^8 | m/s |
| λ | wavelength, λ = c / f_c | m |
| N | number of array elements | — |
| N_el, N_az | beam elevation positions; azimuth positions per revolution | — |
| d | inter-element spacing | m |
| θ, θ_0 | beam angle from broadside; desired steering angle | rad or deg |
| Δφ, Δφ_n | phase shift per element; phase difference for elevation position n | rad or deg |
| G, G_t, G_r | antenna gain (combined; transmit; receive) | dBi |
| k | wavenumber, k = 2π/λ | rad/m |
| ψ | electrical angle, ψ = k d sinθ + Δφ | rad |
| θ_3dB | half-power beamwidth | rad or deg |
| w_n, a_n | amplitude weight / nominal amplitude weight of element n | — |
| δφ_n, δa_n | phase / amplitude error of element n | rad / — |
| AF(θ) | array factor | — |
| P_t, P_r | transmit power (per element), received power | W |
| σ | radar cross section | m² |
| L | total system losses (linear ratio) | — |
| F, NF | noise figure (linear; dB) | — / dB |
| T_0 | reference noise temperature, 290 K | K |
| k_B | Boltzmann constant, 1.381 × 10^−23 | J/K |
| P_fa, P_d | probability of false alarm, probability of detection | — |
| SNR, SNR_min | signal-to-noise ratio, minimum detectable SNR | dB |
| α | CFAR threshold multiplier | — |
| N_ref, N_guard | CFAR reference cells, guard cells (total) | — |
| T_e, B_n | equivalent noise temperature, noise bandwidth | K, Hz |
| f_s | ADC sampling frequency | Hz |
| f_IF | intermediate frequency | Hz |
| N_FFT, N_Doppler, N_R | FFT size (range), Doppler FFT size, number of range bins | — |
| N_CIC, D_CIC | CIC filter stages, CIC decimation factor | — |
| w[n] | window function (discrete) | — |
| χ(τ, ν) | ambiguity function | — |
| Δφ_NCO | NCO phase accumulator increment per clock cycle | — |
| G_CIC | CIC filter DC gain, G_CIC = D_CIC^N_CIC | — |
| N_seg, L_adv, L_overlap | overlap-save segments, segment advance, overlap length (matched filter) | — / samples |
| N_rb, D_rb | output range bins after decimation, range-bin decimation factor | — |
| V_rail, I_rail | voltage rail value, current draw per rail | V, A |
| P_diss, T_junction, θ_JA | power dissipation, junction temperature, thermal resistance junction-to-ambient | W, °C, °C/W |
| t_lock | PLL lock time | s |
| L(f_m) | phase noise at offset f_m from carrier | dBc/Hz |
| t_pipeline | end-to-end pipeline latency | s |
| N_LUT, N_FF, N_BRAM, N_DSP | FPGA look-up tables, flip-flops, block RAMs, DSP48E1 slices | — |

Equation tags (FMCW-n, LFM-n, BF-n, DET-n, NF-n, CAL-n, HW-ANT-n) refer to the display equations of the upstream physics and hardware notes under the document-prefix scheme of `00_notation/conventions.md` §1.

## 3. Status vocabulary

Labels on figures and procedures (source: `manual/STYLE_GUIDE.md`): ORIGINAL PROJECT FILE · SOURCE-DERIVED · PARTIAL · CONCEPTUAL · PROPOSED DESIGN · BETA · BLOCKED — MISSING DATA · VERIFIED (reserved; unused). Qualifiers on numbers: ASSUMED, ESTIMATE, TBD, UNKNOWN, UNRESOLVED, REQUIRES VERIFICATION.

Register-specific vocabularies kept as in their sources:

| Register | Values | Source |
|---|---|---|
| Interconnection table, power-rail register | CONFIRMED / UNVERIFIED / MISSING SPEC; PARTIAL; CONFLICT | `engineering/SYSTEM/interfaces/interconnection_table.md`; `engineering/ELECTRICAL/power_distribution/power_rails.md` |
| Drawing register | SOURCE-DERIVED / PARTIAL / CONCEPTUAL / PROPOSED / BLOCKED | `engineering/DRAWING_REGISTER.md` |
| Recovery tasks | DONE / OPEN / BLOCKED (designer input) / PARTIALLY DONE | `docs/04_RECOVERY_TASKS.md` |
| Acceptance criteria | MET / NOT MET / PARTIALLY MET / NOT RUN (physical tests) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` |
| Missing components | priorities P0 (blocks a reproducible build or required artefact) / P1 (blocks a complete release or reliable validation) / P2 (documentation, maintainability) | `docs/03_MISSING_COMPONENTS.md` |
| Firmware defects | C1–C7 conflict rows of STM-T04 | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` |
| Interface confidence | MEDIUM (bit mapping inferred from source comments) | `docs/SYSTEM/BLOCK_DIAGRAM.md` §3 |

## 4. Identifier families

| Family | Range | Meaning | Register |
|---|---|---|---|
| K | K1–K8 | configuration conflicts between CAD, firmware, RTL, GUI and documentation | `docs/SYSTEM/BLOCK_DIAGRAM.md` §4; chapter 17 §1 |
| D | D-01…D-15; D-16…D-19 | proposed-design decisions (mechanical/antenna/thermal/harness; host link) | `engineering/DESIGN/00_DESIGN_BASIS.md` §2; `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §3–4; chapter 17 §2 |
| G | G-01…G-12 | unresolved mechanical geometry | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`; chapter 17 §3 |
| MDR | MDR-01…MDR-13 | missing-drawing recovery guides | `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`; chapter 17 §4 |
| DSN | DSN-00, DSN-ANT-01, DSN-THM-01, DSN-PSU-01, DSN-MECH-01…07, DSN-MECH-3D, DSN-HAR-01, DSN-LINK-01, DSN-CALC-01 | proposed-design documents and drawings | `engineering/DRAWING_REGISTER.md` |
| SYS / SD / ELEC-PWR | SYS-01…04; SD-01…07; ELEC-PWR-01 | system-level and software diagrams (SOURCE-DERIVED / PARTIAL) | `engineering/SYSTEM/architecture/README.md`; `engineering/DRAWING_REGISTER.md` |
| PCB-*, MECH-*, ASM-EXP-01, VAL-GEO-01, ENG-MDR-01 | per board / per drawing | registered PCB drawings, mechanical drawings, exploded view, validation and recovery documents | `engineering/DRAWING_REGISTER.md` |
| CBL | CBL-00…CBL-106 (two-digit, per signal group) and CBL-001…CBL-144 (three-digit, per physical cable) | cable identifiers — two schemes, see MAN-03 | `engineering/SYSTEM/interfaces/interconnection_table.md`; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` |
| AC | AC-F1…F9, AC-S1…S7, AC-P1…P7, AC-B1…B8, AC-M1…M5, AC-D1…D5, AC-E1…E8, AC-X1… | acceptance criteria per area (FPGA, STM32, Python, PCB, mechanical, documentation, engineering package, BETA tree) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` |
| F / S / P / B / R | F-01…F-10, S-01…S-10, P-01…P-09, B-01…B-09, R-01…R-03 | validation-plan checks (FPGA, STM32, Python, PCB, repository) referenced by the acceptance criteria | `docs/TESTING/VALIDATION_PLAN.md` |
| R | R-SYS-01, R-FPGA-01…10, R-STM-01…08, R-GUI-01…03, R-PCB-01…06, R-MECH-01…02, R-DOC-01…03, R-ENG-01…13, R-DSN-01…07, R-BETA-01…09 | recovery tasks | `docs/04_RECOVERY_TASKS.md`; chapter 17 §5 |
| FPGA- / STM- / GUI- / PCB- / MECH- / REPO- | FPGA-00…15, STM-01…19, GUI-01…08, MECH-01…06, REPO-01…05 | missing-component manifest IDs checked by `tools/check_missing_files.py` | `docs/03_MISSING_COMPONENTS.md` |
| C | C1–C7 | STM32 firmware conflicts/defects (HSE, ADF4382 pins, platform ops, USB RX, start-flag padding, GPS_Init, AD9523 CS/SPI speed) | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` STM-T04 |
| F0–F10 | — | firmware power-enable sequence steps as coded | `engineering/ELECTRICAL/power_distribution/power_rails.md` §3; chapter 3 §4.2 |
| MAN | MAN-01…03 | observations raised by this manual while compiling the sources | chapter 17 §6 |
| Figure numbers | F<chapter>.<n> | figure slots of `manual/FIGURE_PLAN.md`; the build tool prefixes a running "Figure n —" | `manual/FIGURE_PLAN.md` |
