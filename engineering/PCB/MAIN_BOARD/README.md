# Main Board (RADAR_Main_Board) — Manufacturing & drawing package

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Package ID | PCB-PKG-MAIN_BOARD |
| Revision | A (first generated package) — **source board revision: none recorded in the EAGLE file** |
| Date | 2026-10-09 |
| Units | mm (Gerber X2 RS-274X, 6 decimals; Excellon mm) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd` — EAGLE 7.4.0 XML, file date 2026-03-14 |
| Generator | `tools/kicad_pcb_pipeline.sh` (kicad-cli 10.0.6) + `tools/gen_engineering_pcb_docs.py` |
| Status | **PARTIAL** — layout NOT finished in the source (2390 airwires in EAGLE; 15 unconnected items after KiCad zone fill). Exports document the current state and must not be sent to fabrication |
| Verification | DRC run (KiCad, EAGLE-DRU-derived rules): 912 violations, 15 unconnected — see §6. No fabricator review, no physical verification |

Preserve-original rule: the EAGLE files were only read. The KiCad copy under `kicad/` is an editable conversion (`kicad-cli pcb import --format eagle`), with EAGLE layer 47 *Measures* remapped to `Dwgs.User` and the EAGLE design rules transferred to the project file (`reports/design_rules_mapping.md`). The conversion is an approximation of EAGLE's polygon pours and thermals; the original EAGLE file remains the design master.

## 1. Deliverables (claude.md addendum §18)

| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/MAIN_BOARD_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/MAIN_BOARD_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/MAIN_BOARD_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/MAIN_BOARD_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/MAIN_BOARD_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/MAIN_BOARD-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/MAIN_BOARD_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/MAIN_BOARD_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/MAIN_BOARD_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/MAIN_BOARD_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/MAIN_BOARD_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/MAIN_BOARD_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/MAIN_BOARD_board_only.step`, `mechanical/MAIN_BOARD_top_fab.dxf`, `ipc/MAIN_BOARD.xml` (IPC-2581), `ipc/MAIN_BOARD_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/MAIN_BOARD.kicad_pcb` + `.kicad_pro`.

## 2. Board statistics (KiCad `pcb export stats` on the converted board)

| Item | Value |
|---|---|
| Outline (bounding box) | 260.0000 × 300.0000 mm |
| Copper layers | 10 (EAGLE layerSetup `(1*2+3*4+5*12+13*14+15*16)`) |
| Footprints (incl. free holes) | 784 |
| Pads THT / SMD / NPTH | 421 / 3225 / 10 |
| Vias | 2893 |
| Tracks / zones imported | 10219 / 26 |
| Min track width / clearance used | 0.1000 / 0.1000 mm |
| Min drill used | 0.1500 mm |
| Board thickness | 1.6000 mm — **KiCad default, NOT from the source (UNVERIFIED)** |

## 3. Cross-check EAGLE XML ↔ KiCad conversion

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 260.0 | 260.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 784 | 784 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 2893 | 2893 | OK |  |
| Tracks (signal wires excl. airwires) | 10219 | 10219 | OK |  |
| Copper layers | 10 | 10 | OK |  |
| NPTH holes (free holes + package holes) | 10 | 10 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 3314 | 3314 | OK |  |

EAGLE airwires (layer 19): 2390; signal polygons: 22; approved (waived) DRC/ERC entries in the source: 211.

## 4. Design rules

EAGLE DRU `PCBWay_8L_100um-Track *`: min width 0.1mm, min drill 0.15mm, wire-wire clearance 0.1mm. Mapping to KiCad: `reports/design_rules_mapping.md`.

## 5. Hole table (from `drill/drill_report.txt`)

| Type | Tool | Ø (mm) | Count |
|---|---|---|---|
| PTH | T1 | 0.150 | 1045 |
| PTH | T2 | 0.200 | 1367 |
| PTH | T3 | 0.254 | 18 |
| PTH | T4 | 0.300 | 332 |
| PTH | T5 | 0.350 | 113 |
| PTH | T6 | 0.500 | 21 |
| PTH | T7 | 0.600 | 7 |
| PTH | T8 | 0.640 | 4 |
| PTH | T9 | 0.840 | 8 |
| PTH | T10 | 1.000 | 4 |
| PTH | T11 | 1.000 | 128 |
| PTH | T12 | 1.016 | 115 |
| PTH | T13 | 1.194 | 148 |
| PTH | T14 | 1.200 | 4 |
| NPTH | T1 | 0.900 | 2 |
| NPTH | T2 | 3.200 | 8 |
| **Total** | | PTH 3314 / NPTH 10 | 3324 |

## 6. DRC result (KiCad, rules from the EAGLE DRU)

Report: `reports/DRC_report.txt` / `.json`. Total violations 912, unconnected items 15. KiCad stops reporting a rule after 199 hits, so counts of exactly 199 are lower bounds. Breakdown:

| Rule | Count | Interpretation |
|---|---|---|
| `solder_mask_bridge` | 199 | mask web between adjacent pads thinner than KiCad default (EAGLE has no such rule) — fabricator decision |
| `silk_overlap` | 199 | overlapping silkscreen texts/lines — cosmetic |
| `silk_over_copper` | 199 | silk over exposed copper — cosmetic/assembly |
| `track_dangling` | 136 | track end not connected — review (stubs or unfinished routing) |
| `shorting_items` | 93 | copper of different nets touching after conversion (typically EAGLE polygon vs unnamed copper) — REVIEW in EAGLE |
| `clearance` | 63 | copper clearance < DRU — review |
| `via_dangling` | 15 | via connected on one layer only — review |
| `hole_clearance` | 4 | hole to copper clearance (KiCad rule, no EAGLE equivalent) |
| `silk_edge_clearance` | 3 | silk too close to edge |
| `zones_intersect` | 1 | overlapping pours of different priority — conversion artefact or design issue |

## 7. Layer stack-up (STACKUP.md)

Layer order and copper thickness come from the EAGLE DRU; dielectric thicknesses in the DRU are EAGLE defaults and are **not** a vendor stack-up. See `STACKUP.md` for the table and the list of unknowns (material, prepreg/core, finish, impedance).

## 8. Manufacturing export checklist

- [x] Gerber set (all copper, mask, paste, silk, outline, fab) exported
- [x] Excellon drill files PTH/NPTH + drill map + report
- [x] Pick-and-place (both sides, mm, CSV)
- [x] BOM with reference designators
- [ ] BOM with manufacturer part numbers for 100 % of lines
- [ ] Fabrication drawing with vendor notes (material, thickness, finish, mask/silk colours, tolerances, impedance)
- [ ] Stack-up confirmed by the fabricator
- [ ] Layout routed to completion (0 airwires / 0 unconnected)
- [ ] DRC with 0 unapproved errors, waivers documented
- [ ] Designer review of the KiCad conversion against EAGLE (pours, thermals, text)
- [ ] Gerbers viewed in an independent viewer (gerbv/online) and compared with the outline drawing
- [ ] IPC-2581 / IPC-D-356 netlist test accepted by the fabricator

## 9. Known gaps for this board (BLOCKED — MISSING DATA)

- Board material, finished thickness, copper weight per layer, surface finish, solder-mask/silk colours, impedance targets: not recorded in the EAGLE file (only `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` and the PCBWay impedance note for RO4350B exist, unlabelled).
- Manufacturer part numbers: none in the schematic attributes.
- 3-D component models: not embedded (Autodesk online URNs) → STEP export is board-only.
- Routing incomplete: 2390 EAGLE airwires; 15 unconnected items after KiCad fill.
