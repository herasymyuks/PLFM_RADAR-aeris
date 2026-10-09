# Power Supply Board (POWER_SUPPLY) — mechanical dimensions

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Drawing ID | MECH-DIM-POWER_SUPPLY |
| Revision | A |
| Date | 2026-10-09 |
| Units | mm; origin = lower-left corner of the outline bounding box (EAGLE coordinates offset by (0.000, 0.000)) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd` (EAGLE 7.4.0, file date 2026-03-14), layer 20 Dimension + holes |
| Status | **SOURCE-DERIVED** for outline and holes; **BLOCKED — MISSING DATA** for thickness, component heights, mass |

## 1. Outline

Bounding box **280.00 × 300.00 mm** (4 outline segments on layer 20). Outline geometry: `../DXF/POWER_SUPPLY_outline_holes_eagle.dxf` (from EAGLE XML) and `../DXF/POWER_SUPPLY_outline_kicad.dxf` (KiCad Edge.Cuts export); 3-D body: `../STEP/POWER_SUPPLY_board_only.step` (KiCad, assumed 1.6 mm thick).

## 2. Holes and mounting pads

| # | X (mm) | Y (mm) | Ø (mm) | Type | Part |
|---|---|---|---|---|---|
| 1 | 10.000 | 10.000 | 3.20 | NPTH (free hole) | — |
| 2 | 140.000 | 10.000 | 3.20 | NPTH (free hole) | — |
| 3 | 270.000 | 10.000 | 3.20 | NPTH (free hole) | — |
| 4 | 10.000 | 120.000 | 3.20 | NPTH (free hole) | — |
| 5 | 270.000 | 120.000 | 3.20 | NPTH (free hole) | — |
| 6 | 10.000 | 230.000 | 3.20 | NPTH (free hole) | — |
| 7 | 270.000 | 230.000 | 3.20 | NPTH (free hole) | — |
| 8 | 138.450 | 267.850 | 3.20 | NPTH (free hole) | — |

Mounting-hole pattern (Ø ≥ 2 mm): X positions [10.0, 138.45, 140.0, 270.0]; Y positions [10.0, 120.0, 230.0, 267.85]; extreme pitch X = 260.00 mm, Y = 257.85 mm.

## 3. Thickness, heights, mass

| Quantity | Value | Basis |
|---|---|---|
| Board thickness | 1.6 mm | **ASSUMED** (not in source; KiCad default). Must be confirmed with the stack-up |
| Bare-board mass | ≈ 249 g | **ESTIMATE**: area 840.0 cm² × 1.6 mm × 1.85 g/cm³ (FR-4 + Cu). Assembled mass unknown |
| Max component height | UNKNOWN | no 3-D models in the CAD (Autodesk URNs only); tallest parts are the SMA/terminal connectors — measure on hardware or add models |
| Keep-out / clearance to enclosure | UNKNOWN | no enclosure design exists |

## 4. Files

- `engineering/MECHANICAL/STEP/POWER_SUPPLY_board_only.step`
- `engineering/MECHANICAL/DXF/POWER_SUPPLY_outline_kicad.dxf`
- `engineering/MECHANICAL/PDF/POWER_SUPPLY_outline.pdf`
