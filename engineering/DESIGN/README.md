# engineering/DESIGN — PROPOSED designs for the missing elements

Generated 2026-10-09. Everything here is new engineering content (status **PROPOSED DESIGN**), derived from the verified constraints in the repository plus the decisions logged in `00_DESIGN_BASIS.md` (D-01…D-15). Parameters: `design_parameters.json` (single source; every generator reads it). Nothing here has been simulated on hardware, built or measured.

| Item | Directory | Native / editable | Exports | Generator |
|---|---|---|---|---|
| Design basis + decision log | `00_DESIGN_BASIS.md`, `design_parameters.json` | Markdown/JSON | — | hand-written |
| Antenna: 16-row × 8-patch microstrip array, 10.5 GHz, RO4350B | `ANTENNA/` | `kicad/aeris10_patch_array.kicad_pcb` (KiCad 8+) | layout SVG/PDF/PNG, Gerber + drill + STEP + render in `kicad_exports/`, `ANTENNA_DESIGN_CALC.md`, `openems_patch_row.py` | `tools/design_antenna_array.py` |
| Thermal budget, 22 V supply sizing | `THERMAL/` | Markdown + JSON | — | `tools/design_thermal.py` |
| 22 V PA supply / enable switch / per-PA pulse gating | `ELECTRICAL/PA_SUPPLY_22V/` | block schematic SVG (editable), BOM CSV, net list | PDF/PNG | `tools/design_pa_supply_schematic.py` |
| Radar head + pedestal 3-D | `MECHANICAL/CAD/` | `aeris10_head_pedestal.FCStd` (FreeCAD 1.1) | STEP (assembly, head, pedestal), STL, TechDraw DXF page, mass table, isometric SVG/PDF/PNG (`tools/stl_to_svg_iso.py`) | `tools/design_mechanical_freecad.py` (run with `freecadcmd`) |
| Head/pedestal 2-D drawings DSN-MECH-01…05 | `MECHANICAL/drawings/` | SVG 1:1 | PDF (5 pages), PNG | `tools/design_mechanical_drawings.py` |
| Harness schedule (144 cables, computed lengths) | `HARNESS/` | CSV | Markdown | `tools/design_mechanical_drawings.py` |

Key proposed numbers: head 315 × 315 × 133 mm (W × H × D), all boards vertical; PA heat spreader 300 × 300 × 10 mm with two fin fields; antenna panel 165 × 248 mm; 16 PA boards 4 × 4; pedestal 360 × 360 × 130 mm with slewing bearing, 1:3 GT3 belt to a NEMA 23 (needs `Stepper_steps = 600` in firmware), 12-circuit slip ring; PA drain gating per chirp reduces the PA dissipation from 591 W (as coded) to 68 W.

Regenerate: `python3 tools/design_thermal.py && python3 tools/design_antenna_array.py && python3 tools/design_pa_supply_schematic.py && python3 tools/design_mechanical_drawings.py && freecadcmd -c "exec(open('tools/design_mechanical_freecad.py').read())"`.

What the owner must decide before any of this is built: D-01 (antenna variant), D-07 (measure component heights), D-12 (firmware constant / gear ratio), D-13 (host link through the slip ring), D-14 (where the `TX_GATE` signal comes from), plus conflicts K1–K8.
