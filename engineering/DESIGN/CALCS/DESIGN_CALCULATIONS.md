# Design calculations — DSN-CALC-01 (PROPOSED DESIGN, BETA)

Date 2026-10-09 · `tools/design_calcs.py` · inputs: `design_parameters.json`, `THERMAL/thermal_summary.json`, `MECHANICAL/CAD/detail/parts_list.json`, `ANTENNA/simulation/tuning_result.json`. No measurement; every assumption is stated inline.

## 1. PA heat-spreader temperature map (2-D finite differences)

Model: 300 × 300 × 10 mm aluminium plate (k = 200 W/mK), 60 × 60 cells, steady state, 16 heat sources 5 × 5 mm at the PA-board centres (QPA2962 position on the PA board is assumed at the board centre — verify in `engineering/PCB/RF_PA`), two fin strips as an effective convective sink (h_eff ≈ 288 W/m²K over the strip footprint = 25 W/m²K × fin area ratio × 0.9 efficiency), 5 W/m²K elsewhere; ambient 45 °C. Conduction through the PA PCB via field and the thermal pad (≈ 2 °C/W → +8 °C in case B) is added analytically.

| Case | Per PA | Plate max / min (°C) | PA base estimate (°C) | Verdict |
|---|---|---|---|---|
| A continuous drain bias | 37.0 W | 213 / — | > 287 | far beyond TBASE 85 °C — confirms case A is infeasible |
| B drain gated per chirp | 4.24 W | 64.3 / 55.3 | ≈ 73 | below 85 °C with margin 12 °C |

Maps: `thermal_map_A-continuous-bias.svg`, `thermal_map_B-gated-drain.svg` (converged in 3999/3999 iterations). Limits: 2-D (through-thickness gradient of a 10 mm plate at these fluxes < 1 °C), uniform h on the strips, no radiation, no PCB/antenna heat.

## 2. Pedestal drive torque

| Quantity | Value | Basis |
|---|---|---|
| Rotating mass | 10.4 kg | detailed head structure 6.4 kg + 4 kg PCBs/antenna/cables (estimate) |
| Moment of inertia (head as a box 315 × 133 mm about its centre + turntable) | 0.128 kg·m² | solid-box formula; head centred on the axis |
| Move: 7.2° in 50 ms, triangular profile | α = 201 rad/s², peak ω = 5.03 rad/s | per azimuth step (50 positions/rev; 5.65 ms dwell per elevation, 31 elevations ≈ 175 ms per azimuth, so a 50 ms move costs 22 % of the scan time) |
| Table torque | 25.69 N·m | J·α |
| Motor torque with 1:3 belt, 80 % efficiency | **10.70 N·m** at ≈ 144 rpm peak | |
| NEMA 23 (1.9 N·m holding, ≈ 60 % at that speed) | 1.14 N·m available → margin ×0.1 | assumption on the torque curve — check the chosen motor's curve at 24 V with the TB6600 |

Move time vs. motor torque (same mass, triangular profile, 1:3 belt):

| Move time per 7.2° step | Motor torque needed | NEMA 23 (≈ 1.14 N·m) | NEMA 34 (≈ 3.0 N·m at speed) | Revolution time (50 × (175 ms dwell + move)) |
|---|---|---|---|---|
| 50 ms | 10.70 N·m | NO | NO | 11.2 s |
| 100 ms | 2.68 N·m | NO | NO | 13.8 s |
| 150 ms | 1.19 N·m | NO | OK | 16.2 s |
| 200 ms | 0.67 N·m | OK | OK | 18.8 s |
| 300 ms | 0.30 N·m | OK | OK | 23.8 s |

**Verdict (revises D-12):** the earlier assumption "NEMA 23, 1:3, fast steps" does not hold for a 10 kg head: NEMA 23 needs ≥ 200 ms per step (revolution ≈ 19 s), NEMA 34 (3 N·m class, 86 mm frame) allows ≈ 100 ms (revolution ≈ 14 s). Alternatives: ratio 1:6 with `Stepper_steps = 1200`, or a lighter head (lid/tray in 2 mm, no PA plate side strips). Bearing moment load from wind is not included (no enclosure wind spec).

## 3. Radar range equation (single-pulse coherent, long chirp)

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

Verdict: with the proposed antenna, 16 × 10 W and 16-chirp integration, R_max(1 m²) ≈ 6.0 km — the 20 km Extended-variant goal (`parameter_table.md`) is **not** reached: it needs ≈ 21 dB more (longer coherent integration across the 31 elevations/azimuth dwell, a narrower B with the same T_c, lower losses, or a higher-gain antenna). The 3 km Nexus goal is met for RCS ≥ 0.1 m² (R ≈ 3.4 km). A 0.01 m² drone-class target falls near 1.9 km. Dominant unknowns: B (assumed), real array gain (16-row coupling not yet simulated), RF chain losses.
