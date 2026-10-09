# RF Power Amplifier (RF_PA) — mechanical dimensions

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Drawing ID | MECH-DIM-RF_PA |
| Revision | A |
| Date | 2026-10-09 |
| Units | mm; origin = lower-left corner of the outline bounding box (EAGLE coordinates offset by (0.000, 0.000)) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd` (EAGLE 9.6.2, file date 2026-03-14), layer 20 Dimension + holes |
| Status | **SOURCE-DERIVED** for outline and holes; **BLOCKED — MISSING DATA** for thickness, component heights, mass |

## 1. Outline

Bounding box **35.00 × 60.00 mm** (4 outline segments on layer 20). Outline geometry: `../DXF/RF_PA_outline_holes_eagle.dxf` (from EAGLE XML) and `../DXF/RF_PA_outline_kicad.dxf` (KiCad Edge.Cuts export); 3-D body: `../STEP/RF_PA_board_only.step` (KiCad, assumed 1.6 mm thick).

## 2. Holes and mounting pads

| # | X (mm) | Y (mm) | Ø (mm) | Type | Part |
|---|---|---|---|---|---|
| 1 | 2.600 | 2.600 | 3.20 | NPTH (free hole) | — |
| 2 | 17.500 | 2.600 | 3.20 | NPTH (free hole) | — |
| 3 | 32.400 | 2.600 | 3.20 | NPTH (free hole) | — |
| 4 | 2.600 | 38.000 | 3.20 | NPTH (free hole) | — |
| 5 | 32.400 | 38.000 | 3.20 | NPTH (free hole) | — |
| 6 | 2.600 | 57.400 | 3.20 | NPTH (free hole) | — |
| 7 | 32.400 | 57.400 | 3.20 | NPTH (free hole) | — |

Mounting-hole pattern (Ø ≥ 2 mm): X positions [2.6, 17.5, 32.4]; Y positions [2.6, 38.0, 57.4]; extreme pitch X = 29.80 mm, Y = 54.80 mm.

## 3. Thickness, heights, mass

| Quantity | Value | Basis |
|---|---|---|
| Board thickness | 1.6 mm | **ASSUMED** (not in source; KiCad default). Must be confirmed with the stack-up |
| Bare-board mass | ≈ 6 g | **ESTIMATE**: area 21.0 cm² × 1.6 mm × 1.85 g/cm³ (FR-4 + Cu). Assembled mass unknown |
| Max component height | UNKNOWN | no 3-D models in the CAD (Autodesk URNs only); tallest parts are the SMA/terminal connectors — measure on hardware or add models |
| Keep-out / clearance to enclosure | UNKNOWN | no enclosure design exists |

## 4. Files

- `engineering/MECHANICAL/STEP/RF_PA_board_only.step`
- `engineering/MECHANICAL/DXF/RF_PA_outline_kicad.dxf`
- `engineering/MECHANICAL/PDF/RF_PA_outline.pdf`
