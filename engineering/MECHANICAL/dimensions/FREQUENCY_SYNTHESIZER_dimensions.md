# Frequency Synthesizer (FREQUENCY_SYNTHESIZER) — mechanical dimensions

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Drawing ID | MECH-DIM-FREQUENCY_SYNTHESIZER |
| Revision | A |
| Date | 2026-10-09 |
| Units | mm; origin = lower-left corner of the outline bounding box (EAGLE coordinates offset by (0.000, 0.000)) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd` (EAGLE 9.6.2, file date 2026-03-14), layer 20 Dimension + holes |
| Status | **SOURCE-DERIVED** for outline and holes; **BLOCKED — MISSING DATA** for thickness, component heights, mass |

## 1. Outline

Bounding box **100.00 × 100.00 mm** (4 outline segments on layer 20). Outline geometry: `../DXF/FREQUENCY_SYNTHESIZER_outline_holes_eagle.dxf` (from EAGLE XML) and `../DXF/FREQUENCY_SYNTHESIZER_outline_kicad.dxf` (KiCad Edge.Cuts export); 3-D body: `../STEP/FREQUENCY_SYNTHESIZER_board_only.step` (KiCad, assumed 1.6 mm thick).

## 2. Holes and mounting pads

| # | X (mm) | Y (mm) | Ø (mm) | Type | Part |
|---|---|---|---|---|---|
| 1 | 5.000 | 5.000 | 3.20 | NPTH (free hole) | — |
| 2 | 95.000 | 5.000 | 3.20 | NPTH (free hole) | — |
| 3 | 5.000 | 95.000 | 3.20 | NPTH (free hole) | — |
| 4 | 95.000 | 95.000 | 3.20 | NPTH (free hole) | — |

Mounting-hole pattern (Ø ≥ 2 mm): X positions [5.0, 95.0]; Y positions [5.0, 95.0]; extreme pitch X = 90.00 mm, Y = 90.00 mm.

## 3. Thickness, heights, mass

| Quantity | Value | Basis |
|---|---|---|
| Board thickness | 1.6 mm | **ASSUMED** (not in source; KiCad default). Must be confirmed with the stack-up |
| Bare-board mass | ≈ 30 g | **ESTIMATE**: area 100.0 cm² × 1.6 mm × 1.85 g/cm³ (FR-4 + Cu). Assembled mass unknown |
| Max component height | UNKNOWN | no 3-D models in the CAD (Autodesk URNs only); tallest parts are the SMA/terminal connectors — measure on hardware or add models |
| Keep-out / clearance to enclosure | UNKNOWN | no enclosure design exists |

## 4. Files

- `engineering/MECHANICAL/STEP/FREQUENCY_SYNTHESIZER_board_only.step`
- `engineering/MECHANICAL/DXF/FREQUENCY_SYNTHESIZER_outline_kicad.dxf`
- `engineering/MECHANICAL/PDF/FREQUENCY_SYNTHESIZER_outline.pdf`
