# Main Board (RADAR_Main_Board) — Layer stack-up

Project AERIS-10 · PCB-STK-MAIN_BOARD · Rev A · 2026-10-09 · Status: **PARTIAL** (layer order SOURCE-DERIVED; thicknesses/materials UNVERIFIED)

Source: EAGLE DRU `PCBWay_8L_100um-Track *` in `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd` (layerSetup `(1*2+3*4+5*12+13*14+15*16)`).

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 0.102mm |
| 2 | 2 | In1.Cu | 0.035mm | 0.2mm |
| 3 | 3 | In2.Cu | 0.035mm | 0.2mm |
| 4 | 4 | In3.Cu | 0.035mm | 0.2mm |
| 5 | 5 | In4.Cu | 0.035mm | 0.2mm |
| 6 | 12 | In5.Cu | 0.035mm | 0.15mm |
| 7 | 13 | In6.Cu | 0.035mm | 0.2mm |
| 8 | 14 | In7.Cu | 0.035mm | 0.2mm |
| 9 | 15 | In8.Cu | 0.035mm | 0.102mm |
| 10 | 16 | B.Cu | 0.035mm | — |

**Caveats**: `mtCopper` 0.035 mm = 1 oz copper; `mtIsolate` values are the EAGLE DRU table (the DRU names a PCBWay template, but the values were not confirmed by a vendor stack-up document). Total thickness is not defined in the source; KiCad assumed 1.6 mm. Material (FR-4 / RO4350B hybrid per `Stack_Hybrid.png`), prepreg/core assignment, finish and impedance targets must be supplied by the designer/fabricator → `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`.
