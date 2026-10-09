# 8. Antenna — proposed 16 × 8 microstrip patch panel (DSN-ANT-01)

**Chapter status summary:** everything in this chapter is **PROPOSED DESIGN** (decisions D-01…D-06): first-order analytical dimensions, a native KiCad board with a fabrication export set, and openEMS simulations of one row and of three adjacent rows. Nothing has been built or measured; the original project contains no antenna CAD (K8, G-06, MECH-ANT-01 BLOCKED — MISSING DATA). The chirp bandwidth B, which decides whether the series-fed row is adequate, is TBD in the parameter table. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `engineering/DESIGN/ANTENNA/ANTENNA_DESIGN_CALC.md`; `engineering/DESIGN/ANTENNA/simulation/TUNING_LOG.md`, `tuning_result.json`, `s11.csv`, `coupling_3rows.csv`; `engineering/DESIGN/ANTENNA/kicad_exports/board_statistics.md`, `DRC_report.txt`, `EXPORT_LOG.md`; `engineering/DESIGN/00_DESIGN_BASIS.md` (D-01…D-06); `engineering/DRAWING_REGISTER.md` (DSN-ANT-01, DSN-ANT-01-SIM).

## 8.1 Why a patch array

The upstream README names two antenna variants — an 8 × 16 patch array ("Nexus") and a 32 × 16 slotted-waveguide array ("Extended") — without CAD for either (K8; source: `docs/SYSTEM/BLOCK_DIAGRAM.md`). Decision D-01 designs the patch array as the primary antenna because it is manufacturable with the same PCB workflow and verifiable with the openEMS tools already used in `5_Simulations`, and gives only a sizing sheet for the waveguide variant; D-02 makes the 16 radiating "elements" of the firmware's elevation-scanned ULA sixteen horizontal rows at 14.3 mm pitch, each a series-fed resonant array of 8 patches (D-03); D-04 fixes the substrate (RO4350B, h = 0.508 mm, 35 µm Cu, full back ground); D-05 the feed (50 Ω end-launch 2.92 mm connectors on the left edge, one per row); D-06 equal feed-line length on every row so that the ADAR1000 calibration tables stay valid (source: `engineering/DESIGN/00_DESIGN_BASIS.md` D-01…D-06).

The waveguide sizing (CONCEPTUAL, source: `ANTENNA_DESIGN_CALC.md` §6): WR-90 λg at 10.5 GHz = 36.56 mm, resonant shunt slots at λg/2 = 18.28 mm, 32 slots → stick ≈ 585 mm; 16 sticks at 14.3 mm cannot be stacked (WR-90 broad wall 22.86 mm + wall), so the Extended variant would need reduced-height or ridged guide or a 2-row interleave — one reason D-01 selects the patch array.

## 8.2 Design calculation (transmission-line model)

Inputs (source: `ANTENNA_DESIGN_CALC.md` §1):

| Parameter | Value | Basis |
|---|---|---|
| f₀ | 10.500 GHz, λ₀ = 28.552 mm | VERIFIED (parameter table) |
| Rows (elements) × patches per row | 16 × 8 | VERIFIED / D-03 |
| Row pitch (elevation) | 14.3 mm = 0.501 λ₀ | VERIFIED |
| Substrate | RO4350B εr = 3.66, tanδ = 0.0037, h = 0.508 mm, Cu 35 µm | D-04 |

Patch (Balanis ch. 14; source: §2):

| Quantity | Value |
|---|---|
| Width W = (λ₀/2)·√(2/(εr+1)) | **9.352 mm** |
| εeff (patch) | 3.3648 |
| ΔL (fringing) | 0.2400 mm |
| Length L = λ₀/(2√εeff) − 2ΔL | **7.303 mm** |
| Slot conductance G1 / mutual G12 | 1.1922 mS / 0.5701 mS |
| Edge resonant resistance R_edge = 1/(2(G1+G12)) | 283.7 Ω |
| Fractional bandwidth (VSWR 2, Balanis approx.) | ≈ 1.7 % (≈ 179 MHz) — chirp bandwidth B is TBD in the parameter table; verify B fits |

Feed network per row (source: §3):

| Element | Z | Width | Length | Note |
|---|---|---|---|---|
| Inter-patch link | 100 Ω | 0.278 mm | 8.841 mm (λg/2, εeff 2.608) | patches in phase (resonant series feed) |
| Centre-to-centre patch spacing along the row | — | — | 16.143 mm = 0.565 λ₀ | fixed azimuth beam (no scan along the row) |
| Row input resistance ≈ R_edge/M | 35.5 Ω | — | — | standing-wave array, in-phase patches |
| Quarter-wave transformer √(50·R_in) | 42.1 Ω | 1.451 mm | 4.182 mm | |
| 50 Ω lead to connector | 50 Ω | 1.112 mm | 10.0 mm (equal on all rows, D-06) | εeff 2.852, λg 16.91 mm |

Panel (source: §4):

| Item | Value |
|---|---|
| Board outline | **165 × 248 mm** (rows start x = 36.18 mm; row 1 centre y = 16.68 mm) |
| Row length (8 patches + 7 links) | 120.30 mm |
| Mounting | 6 × Ø3.2 mm (M3 inferred) at 5 mm from the edges |
| Connectors | 16 × end-launch 2.92 mm on the left edge at 14.3 mm pitch (body width ≤ 12 mm — e.g. Southwest 1092-series, Amphenol 901-10510; **verify footprint**) |
| Estimated HPBW azimuth (row, 8 × 16.1 mm) | ≈ 11.2° (uniform) |
| Estimated HPBW elevation (16 × 14.3 mm) | ≈ 6.3° (matches HW-ANT-10: 6.3°) |
| Estimated directivity (aperture 129 × 229 mm, η_ap 0.7 assumed) | ≈ 25.0 dBi (parameter table says ~20 dBi TBD) |
| Series-feed frequency squint | the row beam tilts with frequency; with B TBD this must be checked in simulation (corporate feed is the fallback, D-02) |

## 8.3 Board and fabrication data

Native editable board `engineering/DESIGN/ANTENNA/kicad/aeris10_patch_array.kicad_pcb` (KiCad 8+/10, RO4350B stack-up entered); exports in `kicad_exports/` generated with kicad-cli (all steps exit 0 on 2026-10-09: drc, gerbers, drill, pdf, svg, step, stats, render — source: `kicad_exports/EXPORT_LOG.md`). Gerber set: `aeris10_patch_array-F_Cu.gtl`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Silkscreen.gto`, `-Edge_Cuts.gm1`, `-job.gbrjob`; drill files in `kicad_exports/drill/`; `aeris10_patch_array.step`; `aeris10_patch_array_top.pdf`; `aeris10_patch_array_F_Cu.svg`.

Board statistics (source: `kicad_exports/board_statistics.md`, KiCad report of 2026-10-09):

| Item | Value |
|---|---|
| Width × height | 165.0000 × 248.0000 mm, area 40920.00 mm² |
| Front / back copper area | 9867.896 mm² / 40475.063 mm² |
| Board stackup thickness | 0.5980 mm |
| Min drill diameter | 0.3000 mm |
| Pads: through hole / SMD / NPTH | 32 / 48 / 6 |
| Vias | 0 (no through, blind, buried or micro vias) |
| Components | 22 (16 SMD, 6 "unspecified" — the count matches the 6 NPTH mounting holes), all front side |
| Drill holes | 32 × Ø0.3 mm PTH (connector pads), 6 × Ø3.2 mm NPTH |

The statistics report also prints "Min track clearance / width 2147.4836 mm"; this equals 2 147 483 647 nm (INT32_MAX) and is read here as KiCad's placeholder for a board whose copper is made of polygons, not tracks — an interpretation of this manual, not a statement of the source file. DRC on the board (source: `kicad_exports/DRC_report.txt`): 46 items — 22 `lib_footprint_issues`, 17 `silk_over_copper`, 7 `silk_edge_clearance` (connector reference fields clipped by the board edge); none is a copper violation.

![F8.1 — DSN-ANT-01 panel layout drawing: 16 rows × 8 patches, feed network, 2.92 mm connector positions, 165 × 248 mm outline with title block (status: PROPOSED DESIGN; source: engineering/DESIGN/ANTENNA/aeris10_patch_array_layout.png; produced by tools/design_antenna_array.py)](engineering/DESIGN/ANTENNA/aeris10_patch_array_layout.png)

![F8.2 — DSN-ANT-01 KiCad 3-D render of the patch panel, top side (status: PROPOSED DESIGN; source: engineering/DESIGN/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png; produced by kicad-cli pcb render)](engineering/DESIGN/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png)

## 8.4 Simulation of one row (DSN-ANT-01-SIM)

openEMS 0.0.36+ built from source (python-openEMS in a Python 3.12 venv), model `openems_patch_row.py`, runner `tools/design_antenna_tune.py`, 1.56 M cells, ~73 s per run, end criterion −40 dB (source: `simulation/TUNING_LOG.md`). Tuning iterations:

| iter | L_SCALE | f_res (GHz) | S11 at f_res (dB) | S11 at 10.5 GHz (dB) | −10 dB band (MHz) | D_row (dBi) |
|---|---|---|---|---|---|---|
| 0 | 1.0000 | 11.092 | -37.6 | -18.0 | 2362 | 11.51 |
| 1 | 1.0564 | 10.830 | -30.6 | -10.8 | 1958 | 11.35 |
| 2 | 1.1274 | 10.560 | -27.6 | -6.3 | 1162 | 11.23 |

Selected: **L_SCALE = 1.0000** (the transmission-line patch length): S11 = −18.0 dB at 10.5 GHz, but the **contiguous −10 dB band around f₀ is only ≈ 128 MHz** — the 2362 MHz span in the table is the non-contiguous extent of all dips and must not be read as bandwidth; between the dips the match is −6…−8 dB, worst −6.2 dB within 10.3–10.7 GHz (source: `TUNING_LOG.md`; `tuning_result.json`: `BW_10dB_MHz_contiguous = 128`, `worst_S11_10.3_10.7_GHz_dB = -6.2`). Single-row directivity 11.51 dBi (16 rows → ≈ 23.5 dBi estimated). Lengthening the patches moves the deepest dip towards 10.5 GHz but narrows the band below the carrier, because the input match of this series-fed row is set by the transformer/feed rather than by a single patch resonance.

Model limits: PEC copper, lossy RO4350B, no connector, one row only, MUR boundaries, lumped 50 Ω port. **Design consequence:** the series-fed resonant row is inherently narrow-band; if the chirp bandwidth B (TBD) exceeds ≈ 100 MHz the row needs a travelling-wave (matched-load) or corporate feed, or a thicker substrate — open item for DSN-ANT-01 rev B. Not evaluated: beam squint vs. frequency, pattern at the band edges, ADAR1000 phase-calibration impact (source: `TUNING_LOG.md`).

![F8.3 — One-row |S11| vs frequency from openEMS (L_SCALE 1.0): comb of narrow resonances, −18.0 dB at 10.5 GHz, ≈ 128 MHz contiguous −10 dB band (status: PROPOSED DESIGN (simulated); source: engineering/DESIGN/ANTENNA/simulation/s11_row.png; produced by tools/design_antenna_tune.py)](engineering/DESIGN/ANTENNA/simulation/s11_row.png)

## 8.5 Three-row mutual coupling

Model `openems_three_rows.py` (2026-10-09): centre row driven, neighbours at ±14.3 mm terminated in 50 Ω. At 10.5 GHz: S22 (centre row) −16.3 dB, S12 = S32 ≈ **−20.7 dB**; worst coupling over 9–12 GHz ≈ −18.8 dB (source: `TUNING_LOG.md` §Three-row mutual coupling; data `coupling_3rows.csv`, 401 samples 9–12 GHz — the figure below reads −16.3 / −20.7 / −20.7 dB at the sample nearest 10.5 GHz and the worst S12/S32 of −18.8 dB at 11.3475 GHz, both taken from the CSV by `manual/figures/plot_coupling.py`). Verdict (same source): coupling is at the −20 dB target of `ANTENNA_DESIGN_CALC.md` §7 at the carrier and slightly above it at the band edges — acceptable for a first panel, but the ADAR1000 phase calibration must be done with all rows terminated (array calibration), and the 16-row full-panel simulation remains open.

![F8.4 — Three-row mutual coupling S12/S32 and centre-row S22 vs frequency, 9–12 GHz, from openEMS (status: PROPOSED DESIGN (simulated); source: engineering/DESIGN/ANTENNA/simulation/coupling_3rows.csv; produced by beta/gui/.venv/bin/python manual/figures/plot_coupling.py, matplotlib Agg)](manual/figures/antenna_coupling_3rows.png)

## 8.6 Verification plan before fabrication

Copied from `ANTENNA_DESIGN_CALC.md` §7 with the current state:

1. Run `openems_patch_row.py` (openEMS ≥ 0.0.36 + python-openEMS): sweep 9.5–11.5 GHz; tune L (±0.3 mm) and `qw_len` until |S11| < −10 dB at 10.5 GHz ± B/2 — **done for L (three iterations, §8.4); the ±B/2 criterion cannot be applied while B is TBD; the ≈ 128 MHz contiguous band is the result to compare against B.**
2. Simulate 3 adjacent rows for mutual coupling (S21 between row ports < −20 dB target) — **done (§8.5): −20.7 dB at f₀, −18.8 dB worst in 9–12 GHz.**
3. Fabricate one 3-row coupon; measure S11/S21 on a VNA; compare with simulation; update `design_parameters.json` — **not done.**
4. Only then release the 16-row panel (`kicad_exports/` Gerbers) and record the result in `engineering/VALIDATION/DRAWING_CHECKS.md` — **not done; the Gerbers exist but are not released.**

## 8.7 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K8 | Antenna variant (patch vs slotted waveguide) — proposal selects patch (D-01); owner decision pending | OPEN | `docs/SYSTEM/BLOCK_DIAGRAM.md`; D-01 |
| G-06 | Element geometry, substrate, feed, radome of the *original* design — no source data; the proposal replaces, not recovers, it | BLOCKED — MISSING DATA | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` |
| — | Chirp bandwidth B TBD → feed topology decision (series resonant vs travelling-wave/corporate, D-02 fallback) | OPEN | `TUNING_LOG.md`; `ANTENNA_DESIGN_CALC.md` §2 |
| — | 2.92 mm end-launch connector footprint (body ≤ 12 mm) to verify | OPEN | `ANTENNA_DESIGN_CALC.md` §4 |
| — | Beam squint vs frequency, band-edge pattern, 16-row full-panel simulation | OPEN | `TUNING_LOG.md` |
| — | 3-row coupon fabrication and VNA measurement; array calibration procedure with all rows terminated | OPEN | §8.6 |
| — | Mounting of the panel on the heat spreader (6 × M3, 2.4 mm nylon spacers) and radome window — chapter 10 | PROPOSED DESIGN | `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` rows 3, 8 |
| — | PA n ↔ antenna row n cable assignment and equal-length coax set (CBL-049…CBL-139) | PROPOSED | `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` |
