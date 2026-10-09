# RF Power Amplifier (RF_PA) — Manufacturing & drawing package

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Package ID | PCB-PKG-RF_PA |
| Revision | A (first generated package) — **source board revision: none recorded in the EAGLE file** |
| Date | 2026-10-09 |
| Units | mm (Gerber X2 RS-274X, 6 decimals; Excellon mm) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd` — EAGLE 9.6.2 XML, file date 2026-03-14 |
| Generator | `tools/kicad_pcb_pipeline.sh` (kicad-cli 10.0.6) + `tools/gen_engineering_pcb_docs.py` |
| Status | **SOURCE-DERIVED** — layout fully routed in the source; exports are a faithful conversion but have not been reviewed by the board designer or a fabricator |
| Verification | DRC run (KiCad, EAGLE-DRU-derived rules): 48 violations, 1 unconnected — see §6. No fabricator review, no physical verification |

Preserve-original rule: the EAGLE files were only read. The KiCad copy under `kicad/` is an editable conversion (`kicad-cli pcb import --format eagle`), with EAGLE layer 47 *Measures* remapped to `Dwgs.User` and the EAGLE design rules transferred to the project file (`reports/design_rules_mapping.md`). The conversion is an approximation of EAGLE's polygon pours and thermals; the original EAGLE file remains the design master.

## 1. Deliverables (claude.md addendum §18)

| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/RF_PA_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/RF_PA_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/RF_PA_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/RF_PA_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/RF_PA_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/RF_PA-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/RF_PA_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/RF_PA_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/RF_PA_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/RF_PA_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/RF_PA_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/RF_PA_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/RF_PA_board_only.step`, `mechanical/RF_PA_top_fab.dxf`, `ipc/RF_PA.xml` (IPC-2581), `ipc/RF_PA_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/RF_PA.kicad_pcb` + `.kicad_pro`.

## 2. Board statistics (KiCad `pcb export stats` on the converted board)

| Item | Value |
|---|---|
| Outline (bounding box) | 35.0000 × 60.0000 mm |
| Copper layers | 4 (EAGLE layerSetup `(1+2*15+16)`) |
| Footprints (incl. free holes) | 32 |
| Pads THT / SMD / NPTH | 15 / 46 / 7 |
| Vias | 342 |
| Tracks / zones imported | 77 / 14 |
| Min track width / clearance used | 0.2040 / 0.1850 mm |
| Min drill used | 0.1500 mm |
| Board thickness | 1.6000 mm — **KiCad default, NOT from the source (UNVERIFIED)** |

## 3. Cross-check EAGLE XML ↔ KiCad conversion

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 35.0 | 35.0 | OK |  |
| Height (mm) | 60.0 | 60.0 | OK |  |
| Footprints = EAGLE elements + free holes | 32 | 32 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 342 | 342 | OK |  |
| Tracks (signal wires excl. airwires) | 77 | 77 | OK |  |
| Copper layers | 4 | 4 | OK |  |
| NPTH holes (free holes + package holes) | 7 | 7 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 357 | 357 | OK |  |

EAGLE airwires (layer 19): 0; signal polygons: 10; approved (waived) DRC/ERC entries in the source: 0.

## 4. Design rules

EAGLE DRU `PCBWay_4L_100um-Track *`: min width 0.1mm, min drill 0.15mm, wire-wire clearance 0.15mm. Mapping to KiCad: `reports/design_rules_mapping.md`.

## 5. Hole table (from `drill/drill_report.txt`)

| Type | Tool | Ø (mm) | Count |
|---|---|---|---|
| PTH | T1 | 0.150 | 103 |
| PTH | T2 | 0.200 | 24 |
| PTH | T3 | 0.350 | 215 |
| PTH | T4 | 1.000 | 5 |
| PTH | T5 | 1.194 | 8 |
| PTH | T6 | 1.321 | 2 |
| NPTH | T1 | 3.200 | 7 |
| **Total** | | PTH 357 / NPTH 7 | 364 |

## 6. DRC result (KiCad, rules from the EAGLE DRU)

Report: `reports/DRC_report.txt` / `.json`. Total violations 48, unconnected items 1. KiCad stops reporting a rule after 199 hits, so counts of exactly 199 are lower bounds. Breakdown:

| Rule | Count | Interpretation |
|---|---|---|
| `clearance` | 16 | copper clearance < DRU — review |
| `zones_intersect` | 8 | overlapping pours of different priority — conversion artefact or design issue |
| `silk_overlap` | 8 | overlapping silkscreen texts/lines — cosmetic |
| `silk_over_copper` | 8 | silk over exposed copper — cosmetic/assembly |
| `shorting_items` | 7 | copper of different nets touching after conversion (typically EAGLE polygon vs unnamed copper) — REVIEW in EAGLE |
| `silk_edge_clearance` | 1 | silk too close to edge |

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
