# Main Board (MAIN_BOARD) — mechanical dimensions

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Drawing ID | MECH-DIM-MAIN_BOARD |
| Revision | A |
| Date | 2026-10-09 |
| Units | mm; origin = lower-left corner of the outline bounding box (EAGLE coordinates offset by (0.000, 0.000)) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd` (EAGLE 7.4.0, file date 2026-03-14), layer 20 Dimension + holes |
| Status | **SOURCE-DERIVED** for outline and holes; **BLOCKED — MISSING DATA** for thickness, component heights, mass |

## 1. Outline

Bounding box **260.00 × 300.00 mm** (4 outline segments on layer 20). Outline geometry: `../DXF/MAIN_BOARD_outline_holes_eagle.dxf` (from EAGLE XML) and `../DXF/MAIN_BOARD_outline_kicad.dxf` (KiCad Edge.Cuts export); 3-D body: `../STEP/MAIN_BOARD_board_only.step` (KiCad, assumed 1.6 mm thick).

## 2. Holes and mounting pads

| # | X (mm) | Y (mm) | Ø (mm) | Type | Part |
|---|---|---|---|---|---|
| 1 | 4.000 | 4.000 | 3.20 | NPTH (free hole) | — |
| 2 | 256.000 | 4.000 | 3.20 | NPTH (free hole) | — |
| 3 | 116.000 | 114.000 | 3.20 | NPTH (free hole) | — |
| 4 | 256.000 | 114.000 | 3.20 | NPTH (free hole) | — |
| 5 | 116.000 | 250.000 | 3.20 | NPTH (free hole) | — |
| 6 | 256.000 | 250.000 | 3.20 | NPTH (free hole) | — |
| 7 | 4.000 | 296.000 | 3.20 | NPTH (free hole) | — |
| 8 | 256.000 | 296.000 | 3.20 | NPTH (free hole) | — |
| 9 | 5.330 | 105.360 | 0.90 | NPTH (package hole) | X53 |
| 10 | 5.330 | 109.760 | 0.90 | NPTH (package hole) | X53 |

Mounting-hole pattern (Ø ≥ 2 mm): X positions [4.0, 116.0, 256.0]; Y positions [4.0, 114.0, 250.0, 296.0]; extreme pitch X = 252.00 mm, Y = 292.00 mm.

## 3. Thickness, heights, mass

| Quantity | Value | Basis |
|---|---|---|
| Board thickness | 1.6 mm | **ASSUMED** (not in source; KiCad default). Must be confirmed with the stack-up |
| Bare-board mass | ≈ 231 g | **ESTIMATE**: area 780.0 cm² × 1.6 mm × 1.85 g/cm³ (FR-4 + Cu). Assembled mass unknown |
| Max component height | UNKNOWN | no 3-D models in the CAD (Autodesk URNs only); tallest parts are the SMA/terminal connectors — measure on hardware or add models |
| Keep-out / clearance to enclosure | UNKNOWN | no enclosure design exists |

## 4. Files

- `engineering/MECHANICAL/STEP/MAIN_BOARD_board_only.step`
- `engineering/MECHANICAL/DXF/MAIN_BOARD_outline_kicad.dxf`
- `engineering/MECHANICAL/PDF/MAIN_BOARD_outline.pdf`
