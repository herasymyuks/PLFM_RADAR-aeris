# Antenna design calculation sheet — DSN-ANT-01 (PROPOSED DESIGN)

Rev A · 2026-10-09 · generator `tools/design_antenna_array.py` · parameters `engineering/DESIGN/design_parameters.json` · decisions D-01…D-06.

**Status: PROPOSED DESIGN — first-order analytical dimensions. Not simulated, not built, not measured.** The openEMS model `openems_patch_row.py` must be run (openEMS is not installed on the authoring machine) and the patch length/inset and transformer tuned until |S11| < −10 dB over the operating band; then the full 16-row panel must be simulated for mutual coupling before any fabrication.

## 1. Inputs

| Parameter | Value | Basis |
|---|---|---|
| f₀ | 10.500 GHz, λ₀ = 28.552 mm | VERIFIED |
| Rows (elements) × patches per row | 16 × 8 | VERIFIED / D-03 |
| Row pitch (elevation) | 14.3 mm = 0.501 λ₀ | VERIFIED |
| Substrate | RO4350B εr = 3.66, tanδ = 0.0037, h = 0.508 mm, Cu 35 µm | D-04 |

## 2. Patch (transmission-line model, Balanis ch. 14)

| Quantity | Value |
|---|---|
| Width W = (λ₀/2)·√(2/(εr+1)) | **9.352 mm** |
| εeff (patch) | 3.3648 |
| ΔL (fringing) | 0.2400 mm |
| Length L = λ₀/(2√εeff) − 2ΔL | **7.303 mm** |
| Slot conductance G1 / mutual G12 | 1.1922 mS / 0.5701 mS |
| Edge resonant resistance R_edge = 1/(2(G1+G12)) | 283.7 Ω |
| Fractional bandwidth (VSWR 2, Balanis approx.) | ≈ 1.7 % (≈ 179 MHz) — chirp bandwidth B is TBD in the parameter table; verify B fits |

## 3. Feed network (per row)

| Element | Z | Width | Length | Note |
|---|---|---|---|---|
| Inter-patch link | 100 Ω | 0.278 mm | 8.841 mm (λg/2, εeff 2.608) | patches in phase (resonant series feed) |
| Centre-to-centre patch spacing along the row | — | — | 16.143 mm = 0.565 λ₀ | fixed azimuth beam (no scan along the row) |
| Row input resistance ≈ R_edge/M | 35.5 Ω | — | — | standing-wave array, in-phase patches |
| Quarter-wave transformer √(50·R_in) | 42.1 Ω | 1.451 mm | 4.182 mm | |
| 50 Ω lead to connector | 50 Ω | 1.112 mm | 10.0 mm (equal on all rows, D-06) | εeff 2.852, λg 16.91 mm |

## 4. Panel

| Item | Value |
|---|---|
| Board outline | **165 × 248 mm** (rows start x = 36.18 mm; row 1 centre y = 16.68 mm) |
| Row length (8 patches + 7 links) | 120.30 mm |
| Mounting | 6 × Ø3.2 mm (M3 inferred) at 5 mm from the edges |
| Connectors | 16 × end-launch 2.92 mm on the left edge at 14.3 mm pitch (body width must be ≤ 12 mm — e.g. Southwest 1092-series, Amphenol 901-10510; **verify footprint**) |
| Estimated HPBW azimuth (row, 8 × 16.1 mm) | ≈ 11.2° (uniform) |
| Estimated HPBW elevation (16 × 14.3 mm) | ≈ 6.3° (matches HW-ANT-10: 6.3°) |
| Estimated directivity (aperture 129 × 229 mm, η_ap 0.7 assumed) | ≈ 25.0 dBi (parameter table says ~20 dBi TBD) |
| Series-feed frequency squint | the row beam tilts with frequency; with B TBD this must be checked in simulation (corporate feed is the fallback, D-02) |

## 5. Files

- Native editable board: `kicad/aeris10_patch_array.kicad_pcb` (KiCad 8+/10; stackup with RO4350B entered)
- Drawing: `aeris10_patch_array_layout.svg` (+ PDF/PNG)
- KiCad exports: `kicad_exports/` (Gerber, drill, PDF, SVG, STEP, 3-D render) — generated with kicad-cli where available
- Simulation model: `openems_patch_row.py` (one row) — **executed with openEMS built from source**: see `simulation/TUNING_LOG.md` (S11 −18 dB at 10.5 GHz but only ≈ 128 MHz contiguous −10 dB band — narrow-band comb response; row directivity 11.5 dBi; feed topology to be revisited if B > ~100 MHz)

## 6. Slotted-waveguide variant (Extended) — sizing only, CONCEPTUAL

WR-90 (22.86 × 10.16 mm, 8.2–12.4 GHz): λg at 10.5 GHz = λ₀/√(1−(λ₀/2a)²) = 36.56 mm; resonant longitudinal shunt slots spaced λg/2 = 18.28 mm, 32 slots per stick → stick length ≈ 585 mm; 16 sticks stacked at 14.3 mm cannot fit (WR-90 broad wall 22.86 mm + wall) → the Extended variant needs reduced-height or ridged guide or a 2-row interleave. This is why D-01 selects the patch array for the proposal.

## 7. Verification plan before fabrication

1. Run `openems_patch_row.py` (openEMS ≥ 0.0.36 + python-openEMS): sweep 9.5–11.5 GHz; tune L (±0.3 mm) and `qw_len` until |S11| < −10 dB at 10.5 GHz ± B/2.
2. Simulate 3 adjacent rows for mutual coupling (S21 between row ports < −20 dB target) — affects the ADAR1000 calibration.
3. Fabricate one 3-row coupon; measure S11/S21 on a VNA; compare with simulation; update `design_parameters.json`.
4. Only then release the 16-row panel (`kicad_exports/` Gerbers) and record the result in `engineering/VALIDATION/DRAWING_CHECKS.md`.
