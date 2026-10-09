# Theory of operation — waveform, pulse compression, Doppler, beamforming, processing chain

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** equations ORIGINAL PROJECT FILE (the upstream physics notes `01_physics/*.md`, transcribed to plain text; equation tags kept); firmware timing constants SOURCE-DERIVED (`main.cpp`); frequency plan SOURCE-DERIVED (firmware-programmed values, not measurements); FPGA processing chain as committed PARTIAL (SD-02: missing modules, placeholders) and as implemented in `beta/fpga` BETA (simulated, not synthesised); figures F2.1 SOURCE-DERIVED, F2.2 and F2.3 PARTIAL. The chirp bandwidth B is TBD in the parameter table; the matched-filter reference memories encode a 10→30 MHz baseband sweep whose relation to B is not established.

**Sources:** `01_physics/01_fmcw_theory.md`, `01_physics/02_lfm_waveform_model.md`, `01_physics/03_beamforming_theory.md`, `01_physics/04_detection_theory.md`, `01_physics/05_noise_analysis.md`, `01_physics/06_calibration_theory.md`, `02_hardware/04_antenna_beamforming.md`, `00_notation/parameter_table.md`, `engineering/SYSTEM/data_flow/signal_and_data_flow.dot`, `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot`, `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot`, `engineering/SYSTEM/interfaces/interconnection_table.md` §6, `beta/fpga/README.md`, `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §2.

**Planned figures:** F2.1 signal and data flow (SYS-03), F2.2 FPGA pipeline as written in the original RTL (SD-02), F2.3 end-to-end data flow (SD-07).

Notation: equations are written in plain text because the manual build has no LaTeX renderer; symbols follow `00_notation/symbol_table.md` (Appendix D), equation tags follow `00_notation/conventions.md` §1 and refer to the display equation of that tag in the cited file. `x^2` is a power, `sqrt()` a square root, `*` complex conjugation when written as `s*(t)`, `·` multiplication.

## 1. Waveform model

### 1.1 LFM chirp

The transmitted pulse is a linear-frequency-modulated chirp of duration T_c and bandwidth B. In complex baseband (source: `01_physics/02_lfm_waveform_model.md` §1, Eq. LFM-1, LFM-3, LFM-4):

- `s(t) = rect(t / T_c) · exp( j·2π·( f_c·t + (μ/2)·t^2 ) )` (LFM-1)
- chirp rate `μ = B / T_c` (LFM-3)
- instantaneous frequency `f_i(t) = f_c + μ·t` (LFM-4)

The time-bandwidth product `TBP = B · T_c` (LFM-5) equals the pulse-compression gain (section 2) and the ratio of the two chirp modes' TBPs is `T_c,1 / T_c,2` (LFM-7) (source: `01_physics/02_lfm_waveform_model.md` §2).

### 1.2 Timing coded in the firmware

The firmware defines the following constants (source: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp:178-184,190,195`; symbols per `00_notation/parameter_table.md`, "Waveform and Timing", copied):

| Parameter | Symbol | Value | Firmware variable | Source line |
|---|---|---|---|---|
| Chirps per beam position | M | 32 | `m_max` | `main.cpp:178` |
| Elevation positions | N_el | 31 | `n_max` | `main.cpp:179` |
| Long chirp duration | T_c,1 | 30 µs | `T1` | `main.cpp:180` |
| Long chirp PRI | T_r,1 | 167 µs | `PRI1` | `main.cpp:181` |
| Short chirp duration | T_c,2 | 0.5 µs | `T2` | `main.cpp:182` |
| Short chirp PRI | T_r,2 | 175 µs | `PRI2` | `main.cpp:183` |
| Guard time | T_guard | 175.4 µs | `Guard` | `main.cpp:184` |
| Azimuth positions per revolution | N_az | 50 | `y_max` | `main.cpp:189` |
| IF frequency | f_IF | 120 MHz | `IF_freq` | `main.cpp:190` |
| Stepper steps per revolution | — | 200 | `Stepper_steps` | `main.cpp:195` |
| Centre frequency / wavelength | f_c / λ | 10.5 GHz / 0.02857 m | `wavelength` | `main.cpp:1133` |
| Chirp bandwidth | B | **TBD** | — | `00_notation/parameter_table.md`, "TBD Tracking" |

The firmware comment at `main.cpp:186` states the per-position sequence: "m = N° of chirp/position = 16 (made of T1 and PRF1) + Guard = 175µs + 16 (made of T2 and PRF2)", i.e. 16 long chirps, a guard interval, then 16 short chirps per beam position. The resulting beam-position frame time is 5647.4 µs (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §2, row "Beam-position frame time", basis `main.cpp:180-186`). The parameter table resolves the apparent PRF discrepancy between firmware and GUI: `PRI1 = 167 µs` is the chirp-level PRI (f_r,1 ≈ 5988 Hz), whereas the GUI variables `prf1 = 1000 Hz` / `prf2 = 2000 Hz` are display rates, not chirp PRFs (source: `00_notation/parameter_table.md`, "Inconsistency Resolutions" §2).

### 1.3 Range, resolution and unambiguous range

With round-trip delay `τ = 2R / c` (FMCW-2) the dechirped beat frequency of a stationary target is `f_b = 2·μ·R / c` (FMCW-17), giving `R = c · f_b / (2μ)` (FMCW-18). Two targets are resolvable when their beat frequencies differ by at least 1/T_c, which yields the range resolution (source: `01_physics/01_fmcw_theory.md` §5–6, Eq. FMCW-19):

- `ΔR = c / (2B)` (FMCW-19) — depends only on B; numerical value not computable while B is TBD (the source says so explicitly).

The maximum unambiguous range follows from the PRI (source: `01_physics/01_fmcw_theory.md` §8, Eq. FMCW-22):

- `R_max = c · T_r / 2 = c / (2 f_r)` (FMCW-22) → 25.1 km for T_r,1 = 167 µs (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, row "Unambiguous range").

The radar range equation used for the performance estimate of chapter 1 §5 is (source: `01_physics/01_fmcw_theory.md` §2, Eq. FMCW-11):

- `SNR = P_t · G^2 · λ^2 · σ / ( (4π)^3 · R^4 · k_B · T_0 · B_n · F · L )` (FMCW-11)

### 1.4 Doppler

For a radial velocity v (approaching positive) the Doppler shift is `f_d = 2v / λ = 2 v f_c / c` (FMCW-4); the full beat frequency with Doppler coupling is `f_b = 2μR_0/c ± f_d` (FMCW-16). Velocity and velocity resolution over M pulses are `v = λ f_d / 2` (FMCW-20) and `Δv = λ / (2 M T_r)` (FMCW-21); the unambiguous velocity is `v_max = λ f_r / 4` (FMCW-23) and the range–velocity trade-off `R_max · v_max = c λ / 8` (FMCW-24) (source: `01_physics/01_fmcw_theory.md` §1, §4, §7, §8).

Range–Doppler coupling of an LFM pulse displaces the apparent range by `ΔR_Doppler = c f_d / (2μ) = v c T_c / (λ B)` (FMCW-27); the coupling ratio of the long to the short chirp equals `T_c,1 / T_c,2` (FMCW-28), i.e. 60 for the firmware values, and range migration across a CPI is `ΔR_migration = v · M · T_r` (FMCW-30) (source: `01_physics/01_fmcw_theory.md` §9). This is the stated reason for the two chirp modes: the long chirp gives processing gain and finer Doppler resolution, the short chirp smaller coupling and wider unambiguous range (source: `01_physics/02_lfm_waveform_model.md` §7, "Design Tradeoffs").

## 2. Pulse compression

### 2.1 Matched filter

The matched filter for s(t) is `h(t) = s*(−t)` (LFM-8), or in the frequency domain `H(f) = S*(f)` (LFM-9). It maximises the output SNR to `2E / N_0` (LFM-10) and provides the processing gain `G_p = B · T_c` (LFM-14); the matched-filter output SNR is the range-equation SNR multiplied by B·T_c (LFM-15). The compressed pulse width is `τ_c = 1 / B` (LFM-16), so the compression ratio is `T_c / τ_c = B T_c` (LFM-17) and the range resolution is again `ΔR = c τ_c / 2 = c / (2B)` (LFM-18). The compressed envelope is approximately `|y(τ)| ≈ T_c · |sinc(B τ)|` (LFM-20) with a first sidelobe of −13.3 dB for rectangular weighting (LFM-21); windowing trades mainlobe width for sidelobe level (source: `01_physics/02_lfm_waveform_model.md` §3–5).

The LFM ambiguity function `|χ(τ, ν)| = (1 − |τ|/T_c) · |sinc( (ν + μτ)(T_c − |τ|) )|` for |τ| ≤ T_c (LFM-23) has its ridge on `ν = −μτ` (LFM-24); the zero-delay Doppler cut gives the single-pulse Doppler resolution `Δf_d,pulse = 1 / T_c` (LFM-27) and `Δv_pulse = λ / (2 T_c)` (LFM-28) (source: `01_physics/02_lfm_waveform_model.md` §6). With B = 50 MHz **ASSUMED** and T_c = 30 µs the pulse-compression gain is 31.8 dB and ΔR = 3 m (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, row "Chirp"); these two numbers are estimates until B is known.

### 2.2 What the repository data encodes — the `.mem` finding

The RTL loads its matched-filter reference from memory files `long_chirp_seg{0,1,2}_{i,q}.mem` and `short_chirp_{i,q}.mem`. The BETA analysis established that the long-chirp files are **conjugate FFT-domain** coefficients, not time-domain samples: `long_chirp_seg{0,1,2}_{i,q}.mem = conj(FFT_1024(u_s)) · 31128 / max|.|`, where u is a unit-amplitude 10 → 30 MHz linear up-chirp of 3000 samples at 100 MSPS, split into 1024-sample segments (phase-fit residual 0.0018 rad; regenerated to within 1 LSB by `beta/fpga/gen_chirp_mem.py`). Segment 3 lies beyond the chirp and is all zeros — that is the file that was missing from the upstream repository and was generated (source: `beta/fpga/README.md`, "What was found and decided", item 1; `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §3.2).

Consequences recorded in the same source:

- the matched filter is a frequency-domain chain (FFT → multiply by the stored reference → IFFT), as the orphan wrappers `fft_1024_forward/inverse_enhanced` and `frequency_matched_filter` of the original RTL imply; a time-domain FIR would not have used the repository data;
- the stored reference is already conjugated, so the chain must **not** conjugate again (`CONJUGATE_REF = 0` in the BETA RTL); with the extra conjugation neither the numpy model nor the RTL produces a compression peak;
- the same data equals the plain FFT of a 30 → 10 MHz down-chirp, so the actual baseband chirp direction after the RF/IF chain decides whether `CONJUGATE_REF` must be 0 or 1 — an open point for the designer (UNRESOLVED, hardware bring-up item);
- `short_chirp_{i,q}.mem` (50 words) matches neither a time- nor a frequency-domain chirp and cannot be used; the short-chirp processing path is UNRESOLVED.

The 10 → 30 MHz sweep of the reference data is a 20 MHz span at baseband. No repository file states whether this equals the RF chirp bandwidth B (TBD in `00_notation/parameter_table.md`; 50 MHz ASSUMED in `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3); the discrepancy is logged as observation MAN-02 in chapter 17.

### 2.3 Detection

The detection notes derive the cell-averaging CFAR threshold multiplier `α = N_ref · ( P_fa^(−1/N_ref) − 1 )` (DET-20) with `P_fa = (1 + α/N_ref)^(−N_ref)` (DET-19), the Swerling I detection probability `P_d = P_fa^(1/(1 + SNR_mean))` (DET-22) and the CFAR loss `L_CFAR ≈ (1/N_ref) · P_d / ((1 − P_d)·ln P_fa)` (DET-24) (source: `01_physics/04_detection_theory.md` §6–8). The RTL as committed does not implement this: the "CFAR" stage is a fixed threshold `|I| + |Q| > 10000` on the Doppler output, marked PLACEHOLDER by the original source comment at `radar_system_top.v:298-299` (source: `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot`, node "CFAR"; `beta/fpga/README.md`, "Remaining work" item 7: the detector is still a fixed threshold, default 10000 via `CFAR_THRESHOLD_DEFAULT`, writable over the bridge as `CFAR_THR` in the BETA).

### 2.4 Noise

The receive-chain noise figure follows Friis' formula `F_sys = F_LNA + (F_mix − 1)/G_LNA + (F_IF − 1)/(G_LNA G_mix) + (F_ADC − 1)/(G_LNA G_mix G_IF)` (NF-8); ADC quantisation adds `SQNR = 6.02 b + 1.76 dB` (NF-11) for b = 8 bits; the CIC decimator has DC gain `G_CIC = D_CIC^N_CIC` (NF-14) and bit growth `b_out = b_in + N_CIC · ceil(log2 D_CIC)` (NF-15) (source: `01_physics/05_noise_analysis.md` §3–6). The numerical budget is "pending parameter resolution" in the source (§7.3): LNA noise figures and the Extended-variant chain are TBD (source: `00_notation/parameter_table.md`, "TBD Tracking").

## 3. Beamforming

### 3.1 Array factor and steering

For a uniform linear array of N elements at spacing d, the inter-element propagation phase is `Δφ_prop = k d sinθ` with `k = 2π/λ` (BF-1); the electrical angle is `ψ = k d sinθ + Δφ` (BF-2) and the array factor `AF(θ) = Σ_{n=0}^{N−1} w_n · exp(j n ψ)` (BF-3). Steering to θ_0 requires `Δφ = −k d sinθ_0` (BF-4). With uniform weights `|AF(θ)| = |sin(Nψ/2) / sin(ψ/2)|` (BF-8), the half-power beamwidth is `θ_3dB ≈ 0.886 λ / (N d)` (BF-10), broadening by `1/cosθ_0` when scanned (BF-11). Grating lobes appear at `sinθ_GL = sinθ_0 + m λ / d` (BF-14); with d = λ/2 they never enter visible space for any scan angle, and for a limited scan |θ_0| ≤ θ_max the spacing may be relaxed to `d/λ < 1 / (1 + sinθ_max)` (BF-16) (source: `01_physics/03_beamforming_theory.md` §1–6). The 2-D extension factorises into the product of two 1-D array factors (BF-19) (source: same, §9).

AERIS-10 values: N = 16, d = λ/2 ≈ 14.3 mm (`element_spacing = wavelength / 2.0f`, `main.cpp:1134`), four ADAR1000 beamformers of four channels each, 31 elevation positions, azimuth by mechanical rotation (source: `00_notation/parameter_table.md`, "Antenna and Beamforming"; `02_hardware/04_antenna_beamforming.md` §1). The 8×16 patch description of the README is interpreted in the proposed antenna as 16 rows of 8 series-fed patches, each row being one "element" of the elevation-scanned array (decision D-02, source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2); that interpretation is a PROPOSED DESIGN choice, not a verified fact about the prototype.

### 3.2 Phase table and steering angles

The firmware holds 31 inter-element phase differences Δφ_n (`phase_differences[31]` in `main.cpp`) (source: `02_hardware/04_antenna_beamforming.md` §3.1, copied verbatim):

| Index | Δφ_n (deg) | Index | Δφ_n (deg) | Index | Δφ_n (deg) |
|---|---|---|---|---|---|
| 0 | +160.000 | 11 | +13.333 | 22 | -17.778 |
| 1 | +80.000 | 12 | +12.308 | 23 | -20.000 |
| 2 | +53.333 | 13 | +11.429 | 24 | -22.857 |
| 3 | +40.000 | 14 | +10.667 | 25 | -26.667 |
| 4 | +32.000 | 15 | 0.000 | 26 | -32.000 |
| 5 | +26.667 | 16 | -10.667 | 27 | -40.000 |
| 6 | +22.857 | 17 | -11.429 | 28 | -53.333 |
| 7 | +20.000 | 18 | -12.308 | 29 | -80.000 |
| 8 | +17.778 | 19 | -13.333 | 30 | -160.000 |
| 9 | +16.000 | 20 | -14.545 | | |
| 10 | +14.545 | 21 | -16.000 | | |

Position 15 is broadside; the table is symmetric. The per-element phase is `φ_n = n · Δφ_pos` (HW-ANT-4), quantised to the 7-bit ADAR1000 register `reg_n = floor( (φ_n mod 360°)/360° · 128 ) mod 128` (HW-ANT-5) with a phase step of `360°/128 = 2.8125°` (HW-ANT-1, CAL-6) and a maximum quantisation error of 1.40625° (CAL-7) (source: `02_hardware/04_antenna_beamforming.md` §2.4, §3.3–3.4; `01_physics/06_calibration_theory.md` §4). The steering angle for d = λ/2 is `θ_0 = arcsin( Δφ_n / 180° )` (HW-ANT-3) (source: `02_hardware/04_antenna_beamforming.md` §3.2).

The project's documents disagree on the resulting scan range: `02_hardware/04_antenna_beamforming.md` §3.2 evaluates HW-ANT-3 at |Δφ_n| = 160° to |θ_0| ≈ ±62.7° and then calls ≈ ±33° the "safe scan range" before grating lobes, while `01_physics/03_beamforming_theory.md` §6 shows that d = λ/2 is grating-lobe-free at every scan angle, and `00_notation/parameter_table.md` ("Inconsistency Resolutions" §4) states ≈ ±33° at Δφ = ±160° from the same formula. The README states ±45°. This manual does not resolve the disagreement; it is recorded as MAN-01 in chapter 17 for the antenna designer. The BETA firmware filled the ADAR1000 vector-modulator tables from datasheet Tables 10–13 (128 rows, ≤ 3.1° encoding error) and fixed a channel-index defect that "rotated the beam by one element" (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4).

### 3.3 Calibration and errors

Per-element amplitude and phase errors `h_n = (a_n + δa_n) · exp(j δφ_n)` (CAL-1) raise the RMS sidelobe level to `σ_a^2 + σ_φ^2` (CAL-5); mutual coupling is modelled as `v_actual = C · w` (CAL-11) and pre-compensated by `w_applied = C^(−1) · w_desired` (CAL-12). The calibration procedure (measure each element against a reference, compute `c_n = a_n / (h_n,meas / S_ref)` (CAL-14), apply, verify) leaves a residual phase error bounded by half a quantisation step (CAL-15) (source: `01_physics/06_calibration_theory.md` §1–8). No calibration has been performed; per-board phase calibration is listed as open in the BETA report (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4, "Open").

### 3.4 Beam sequence

During each azimuth position the firmware loads the 15 positive-steering patterns (`matrix1`), broadside (`vector_0`) and the 15 negative patterns (`matrix2`) into all four ADAR1000s (TX and RX) and, for each, executes M/2 long chirps at T_r,1, the guard time, then M/2 short chirps at T_r,2 (source: `02_hardware/04_antenna_beamforming.md` §3.5–3.6). The STM32 signals each new chirp, elevation and azimuth to the FPGA by toggling `DIG_0..2` (PD8..PD10) and enables the mixers with `DIG_3` (PD11); the bit-to-port mapping is inferred from source comments and rated MEDIUM confidence (source: `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot`, edge "handshake DIG_0..4"; `docs/SYSTEM/BLOCK_DIAGRAM.md` §3).

## 4. Frequency plan and signal flow

![F2.1 — Signal and data flow SYS-03: reference and clock tree, TX chain, RX chain, control paths; solid = confirmed, dashed = unverified, dotted red = missing specification — SOURCE-DERIVED; frequencies are firmware-programmed values, not measurements (source: engineering/SYSTEM/data_flow/signal_and_data_flow.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SYSTEM/data_flow/signal_and_data_flow.png)

The frequencies below are the values programmed by the firmware, traced through the schematics; none has been measured (source: `engineering/SYSTEM/data_flow/signal_and_data_flow.dot`, node labels; `engineering/SYSTEM/interfaces/interconnection_table.md` §6):

| Signal | Value (firmware intent) | Path | Evidence |
|---|---|---|---|
| Reference | REFB 100 MHz selected (X5 net `100MHZ_OUT`); VCXO X6 on `OSC_IN`, `vcxo_freq = 100 MHz` | Synth IC1 AD9523: PLL1 (REFB, R = 1) → VCXO; PLL2 PFD 100 MHz, N = 36 → VCO 3.6 GHz | `main.cpp:933-946, 1070`; K7: schematic part values are 50 MHz VCXO / 100 MHz OCXO |
| ADF4382 reference | 300 MHz LVDS (OUT0/OUT1) | IC1 → C11/C12, C68/C69, R1/R12 → U1/U6 REFP/N | synth schematic; `adf4382a_manager.h:32-34` |
| TX LO | 10.5 GHz (`TX_FREQ_HZ`) | U1 ADF4382 RFOUT1 → MTX2-143+ → ATS1005 −3 dB → J10 "LO TX" → coax → Main J23 → C272 → U5 LTC5552 LO | `adf4382a_manager.h:32-34`; interconnection §6, CBL-36 |
| RX LO | 10.38 GHz (`RX_FREQ_HZ`) = 10.5 GHz − 120 MHz | U6 ADF4382 RFOUT1 → U7 → U8 → J11 "LO RX" → Main J22 → C274 → U13 LTC5552 LO | same; CBL-37 |
| ADC sample clock | 400 MHz LVDS (OUT4) | J3 → J21 twinax → U1 AD9484 CLK± | `main.cpp:983-984`; CBL-34 |
| FPGA ADC clock | 400 MHz LVDS (OUT5) | J4 → J19 → U42 bank 14 MRCC | not used by the RTL; CBL-35 |
| FPGA system clock | 100 MHz LVCMOS (OUT6) | J7 → J1 → U42 `IO_L13P_T2_MRCC_15` = `clk_100m` | `main.cpp:1004`; CBL-30 |
| DAC clock | 120 MHz LVCMOS (OUT10) | J5 → J20 → U3 AD9708 CLOCK | `main.cpp:1025-1026`; CBL-31 |
| FPGA DAC clock | 120 MHz LVCMOS (OUT11) | J6 → J18 → U42 = `clk_120m_dac` | CBL-32 |
| Test clock | 20 MHz (OUT7) | J8 → JP20 `FPGA_CLOCK_TEST` | CBL-33 (adapter UNVERIFIED) |
| IF | 120 MHz | TX: DAC → LC network → U5 IF±; RX: U13 IF± → LC → 2 × AD8352 → AD9484 | `main.cpp:190`; `ddc_400m.v:48` |

TX chain (source: SYS-03 node labels): the FPGA chirp controller (`plfm_chirp_controller`, LUT-based) drives the 8-bit AD9708 DAC at 120 MHz; the differential LC network (C127 32.8 pF, L22/L25 107.3 nH, C141, L26/L27 107.3 nH, C59 32.8 pF) feeds the IF port of the LTC5552 up-converter U5; the RF output passes band-pass filter U$2 "BPF2" (part number NOT IDENTIFIED; sideband selection UNVERIFIED), the SPDT switch U$1 M3SWA2-34DR+, the 4-way combiner/divider U16 EP4RKU+, the four ADAR1000s (TX1..TX4 → ADTR TX_IN), the sixteen ADTR1107 T/R front ends and sixteen M3SWA2-34DR+ element switches to SMA pairs J24..J55, from which the Extended variant goes through one QPA2962 PA board per element to the antenna, and the Nexus variant goes directly to the antenna. RX chain: the echo returns through the same element switch and ADTR1107 LNA path (RX_OUT → ADAR RXn), the combiner, U$1 to the LTC5552 down-converter U13 (LO 10.38 GHz → IF 120 MHz, "consistent with IF_freq"), the IF LC network, two cascaded AD8352 amplifiers U8/U4 (enable pins `EN_OPAMP_IF_1/2` floating) and the AD9484 ADC (VIN± via R13/R1 24 Ω, C3 2.7 pF), whose LVDS D0..7 + DCO go to FPGA bank 14 (source: `engineering/SYSTEM/data_flow/signal_and_data_flow.dot`, nodes of the "transmit chain", "common port", "receive chain" clusters).

## 5. FPGA processing chain

### 5.1 As written in the original RTL (PARTIAL)

![F2.2 — FPGA signal-processing pipeline as written in the original RTL (SD-02): blue = defined and instantiated, orange = documented defect or placeholder, red dashed = instantiated but missing from the repository, grey dotted = orphan — PARTIAL (source: engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.png)

The original receiver chain (`radar_receiver_final.v`, instantiation order at lines 61, 82, 94, 114, 129, 144, 173, 198, 226, 290) is, per stage (source: `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot`, node labels):

| Stage | Module (file:line) | Function and parameters | State in the original RTL |
|---|---|---|---|
| LVDS capture | `lvds_to_cmos_400m` (rrf:61), `ad9484_lvds_to_cmos_400m` (rrf:82) | IBUFDS → BUFG; 8-bit ADC bus + DCO at 400 MSPS | clock defect (`lvds_to_cmos_400m.v:35-43`: a flop re-sampling its own clock); capture module MISSING |
| CDC | `cdc_adc_to_processing #(8,3)` (rrf:94) | ADC DCO → clk_400m | present |
| DDC | `ddc_400m_enhanced` (rrf:114) with `nco_400m_enhanced` + `lfsr_dither_enhanced` (`ddc_400m.v:131-160`) | NCO IF 120 MHz at 400 MSPS, `PHASE_INC 32'h4CCCCCCD`; complex mixer; `cic_decimator_4x_enhanced` ×2 (decimate by 4, 5 stages); CDC to clk_100m; `fir_lowpass_parallel_enhanced` ×2; `baseband_i/q[17:0]` | connected with `mixers_enable = 1'b1`, `bypass_mode = 1'b1` (`:125-126`); 400 MHz fabric logic |
| Scaling | `ddc_input_interface` (rrf:129) | 18-bit → 16-bit `adc_i/q_scaled` | present |
| Reference | `chirp_memory_loader_param` (rrf:144) + `latency_buffer_2159 #(32, 3187)` (rrf:173) | `$readmemh` ×10 from absolute Windows paths; `long_chirp_seg3_i/q.mem` MISSING | path defect; one file missing |
| Matched filter | `matched_filter_multi_segment` (rrf:198) → `matched_filter_processing_chain` (`matched_filter_multi_segment.v:361`) | overlap-save 1024-point, 4 segments | control inputs `use_long_chirp`, `chirp_counter`, `mc_new_*` UNDRIVEN (rrf:21-25, 204-208) → filter never starts; processing chain MISSING; FFT wrappers orphaned, IP missing |
| Range decimation | `range_bin_decimator #(1024, 64, 16)` (rrf:226) | 1024 → 64 bins, peak mode | MISSING |
| Doppler | `doppler_processor_optimized #(32, 64, 32)` (rrf:290) → `xfft_32` (`doppler_processor.v:283`) | 64 range bins × 32 chirps frame → 32-point FFT | `xfft_32` MISSING (Xilinx IP, no `.xci`); frame-sync pulse never fires (chirp_counter undriven) |
| Detection | glue in `radar_system_top.v:298-323` | fixed threshold `abs(I) + abs(Q) > 10000` | PLACEHOLDER per source comment |
| Host | `usb_data_interface` (`radar_system_top.v:345-373`) | FT601 slave FIFO, packet `0xAA` header … `0x55` footer, FSM on `ft601_clk_in` | NO HARDWARE (FT601 U6 0 of 77 pins connected); inputs sampled across clock domains without synchroniser; `ft601_clk_out` two drivers |
| Transmitter | `radar_transmitter` (`radar_system_top.v:204-264`) | edge detectors on STM32 toggles; `plfm_chirp_controller_enhanced` (LUT chirp, beam/elevation/azimuth/chirp counters, RF switch, mixer enables, ADAR load/TR); `dac_interface_enhanced` at 120 MHz | `level_shifter_interface` not instantiated → STM32→ADAR1000 SPI pass-through outputs never driven |

The register `docs/SYSTEM/BLOCK_DIAGRAM.md` §3 summarises the same findings per interface (STM32→FPGA handshake inferred, SPI pass-through BROKEN in RTL, FPGA→host NO HARDWARE, ADC→FPGA capture not implemented and bank-voltage conflict).

### 5.2 As implemented in `beta/fpga` (BETA)

The BETA RTL keeps the architecture and repairs it so that it parses, lints and simulates with Icarus Verilog 13.0 and Verilator 5.052; it is **not synthesised**, has **no timing closure** and has **not been loaded on hardware**; the two Xilinx FFT IP cores are not generated (source: `beta/fpga/README.md`, "Status"). The functional changes relevant to the theory of operation (source: `beta/fpga/README.md`, "What was found and decided", "ADC capture and DDC front end", "Remaining work"; `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §3.2):

- **ADC capture** (`ADC_CAPTURE_MODE = 1`, default): the AD9484 output is SDR LVDS at the sample rate (datasheet facts: DCO at 400 MHz, data valid on the rising DCO edge, tSKEW ±0.07 ns). Capture uses IBUFDS(DCO) → BUFIO + BUFR/4, IDELAYE2 per lane with calibration (`adc_capture_calib`: default tap 16, manual tap/bitslip, automatic IDELAY sweep with the ADC test pattern, per-lane lock status, pattern error counter), ISERDESE2 SDR 1:4, and a 32-bit asynchronous FIFO into `clk_100m`. Mode 0 keeps the legacy 400 MHz fabric path for comparison.
- **DDC at 100 MHz** (`ddc_4x_100m`): 4-phase NCO, 8 mixers, CIC as a 16-tap FIR and the unchanged FIRs, all at 100 MHz; bit-exact with the legacy 400 MHz chain (`tb_ddc_4x`: 1855 outputs, max diff 0 LSB).
- **Matched filter**: frequency-domain chain with `CONJUGATE_REF = 0` (section 2.2); reference alignment by address instead of the fixed 3187-cycle latency buffer; `tb_matched_filter` peak at bin 302 for a 300-sample delay (±4), peak/sidelobe 4.76.
- **Clock-domain crossings**: Gray-pointer FIFOs, reset synchroniser per domain, STM32 toggles synchronised in the consuming domain.
- **Register map** (`radar_control_regs`): the previously floating control inputs have one driver with reset defaults; its write/read port is driven by the SPI bridge (command set v2, 5-bit word addresses 0x00..0x10, 16-bit registers; table in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §7).
- **Host path option B**: `rd_map_packer` turns each 64 × 32 Doppler frame into a 2066..2162-byte frame (header, 2048 × uint8 log-magnitude, up to 32 detections, CRC-16/CCITT-FALSE) and `host_bridge_spi` streams it to the STM32 as an SPI slave on the existing SPI1 nets with `DIG_5..7` as CS/DRDY/spare; the ADAR1000 pass-through is gated during transfers (section 6).

System-level evidence from `tb_system_smoke` (source: `beta/fpga/README.md`, "System smoke test evidence"): for alternating echo delays of 100 and 420 baseband samples the segment-0 peak sat at decimated bins 8 and 28 on every chirp — a 20-bin shift for a 320-sample delay change (320/16 = 20) — i.e. pulse compression works end to end through capture → DDC → matched filter → decimator in simulation; 2048 Doppler outputs (one 64 × 32 frame); 2688 USB packets with 0 header/footer/sequence errors.

Two architectural limitations remain and matter for interpreting the processing chain (source: `beta/fpga/README.md`, "Remaining work" items 4–5): (a) **throughput** — the matched-filter FSM is not pipelined against the sample collector; one long chirp (4 segments) occupies it for ~92 µs with the behavioural FFT latency and ~270 µs with a realistic IP latency, whereas the transmitter repeats long chirps every 167 µs, so samples arriving outside `ST_COLLECT_DATA` are dropped (original behaviour; the smoke test uses a 300 µs period for this reason); (b) **segment semantics** — each 1024-sample segment is compressed against its own reference segment and yields its own 64-bin profile; the four profiles per chirp are not summed, and the Doppler processor counts each profile as a "chirp", so a 32-"chirp" frame covers 8 real chirps. Whether to sum the partial correlations (true partitioned matched filter) or use a 4096-point transform is a design decision not yet taken.

## 6. Data path to the host

![F2.3 — End-to-end signal and control data flow SD-07: antenna → RF → ADC → FPGA → host and host → STM32 → clock/LO/beamformer → FPGA; solid = confirmed by schematic net and firmware/RTL, dashed = unverified, dotted red = missing specification — PARTIAL; the FPGA→host path has no hardware (source: engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.png)

Key finding of SD-07 (source: `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot`, legend): the only wired host link is the STM32 USB-FS CDC on X53 (control, GPS and status); the FPGA radar-data output targets an FT601 that has no nets; no GUI version in the upstream repository can decode the RTL packet format (K5). Therefore no end-to-end radar data path exists in the repository as committed.

The data-rate budget that frames the BETA solution (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §2, copied verbatim):

| Quantity | Value | Basis |
|---|---|---|
| Range-Doppler cells per beam position | 64 × 32 = 2048 | `doppler_processor.v` (RANGE_BINS 64, 32 chirps) |
| Beam-position frame time | 5647.4 µs | `main.cpp:180-186` |
| Raw RTL packet stream (44 B per cell) | **16.0 MB/s** | `usb_data_interface.v` (11 × 32-bit words) |
| Compact map frame (8-bit log-magnitude per cell + header + ≤ 32 detections + CRC) | 2164 B → **383 kB/s** | this design, §5 |
| STM32 USB-FS CDC practical limit | ≈ 0.8–1.1 MB/s | USB 2.0 FS bulk (19 × 64 B per 1 ms frame max) |
| SPI1 STM32 ↔ FPGA (existing lines) | 27 Mbit/s ≈ 3.3 MB/s (DMA) | APB2 108 MHz / 4 (beta clock tree) |
| FT601 245 sync FIFO, 32 bit @ 100 MHz | up to 400 MB/s | FT601 |

The source concludes that the raw stream needs the FT601 (option A, Main Board rev. B, decision D-16) while the compact map fits the existing STM32 path with 3× margin (option B, implemented as BETA, decision D-17). The STM32 forwards each bridge frame unchanged over CDC, interleaved with its status strings, and the GUI stream parser resynchronises on the `0xA5 0x5A` sync word (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §5). Chapter 9 gives the frame layout and the command set; chapter 17 lists the decisions D-16…D-19.
