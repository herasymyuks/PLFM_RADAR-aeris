# openEMS tuning of one antenna row (DSN-ANT-01)

Date 2026-10-09 · openEMS 0.0.36+ built from source (`~/opt/openEMS`, python-openEMS in a Python 3.12 venv) · model `../openems_patch_row.py` · runner `tools/design_antenna_tune.py` · 1.56 M cells, ~73 s per run, end criterion −40 dB.

| iter | L_SCALE | f_res (GHz) | S11 at f_res (dB) | S11 at 10.5 GHz (dB) | −10 dB band (MHz) | D_row (dBi) |
|---|---|---|---|---|---|---|
| 0 | 1.0000 | 11.092 | -37.6 | -18.0 | 2362 | 11.51 |
| 1 | 1.0564 | 10.830 | -30.6 | -10.8 | 1958 | 11.35 |
| 2 | 1.1274 | 10.560 | -27.6 | -6.3 | 1162 | 11.23 |

**Selected: L_SCALE = 1.0000** (the transmission-line patch length). It gives the best match at the carrier: S11 = -18.0 dB at 10.5 GHz, −10 dB band ≈ 2362 MHz (9.9–12.3 GHz), single-row directivity 11.51 dBi (16 rows → ≈ 23.5 dBi estimated). Lengthening the patches moves the deepest dip towards 10.5 GHz but narrows the band below the carrier (iteration 2: S11 −6.3 dB at f0), because the input match of this series-fed row is set by the transformer/feed rather than by a single patch resonance.

Model limits: PEC copper, lossy RO4350B, no connector, one row only (no mutual coupling between the 16 rows), MUR boundaries, lumped 50 Ω port. **Not yet evaluated:** beam squint vs. frequency (series feed), cross-row coupling, pattern at the band edges, and the ADAR1000 phase-calibration impact. Status: PROPOSED DESIGN — simulated (one row), not measured.
