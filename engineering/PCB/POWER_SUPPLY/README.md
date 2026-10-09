# Power Supply Board (PowerBoard) — Manufacturing & drawing package

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Package ID | PCB-PKG-POWER_SUPPLY |
| Revision | A (first generated package) — **source board revision: none recorded in the EAGLE file** |
| Date | 2026-10-09 |
| Units | mm (Gerber X2 RS-274X, 6 decimals; Excellon mm) |
| Source | `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd` — EAGLE 7.4.0 XML, file date 2026-03-14 |
| Generator | `tools/kicad_pcb_pipeline.sh` (kicad-cli 10.0.6) + `tools/gen_engineering_pcb_docs.py` |
| Status | **PARTIAL** — layout NOT finished in the source (309 airwires in EAGLE; 308 unconnected items after KiCad zone fill). Exports document the current state and must not be sent to fabrication |
| Verification | DRC run (KiCad, EAGLE-DRU-derived rules): 160 violations, 308 unconnected — see §6. No fabricator review, no physical verification |

Preserve-original rule: the EAGLE files were only read. The KiCad copy under `kicad/` is an editable conversion (`kicad-cli pcb import --format eagle`), with EAGLE layer 47 *Measures* remapped to `Dwgs.User` and the EAGLE design rules transferred to the project file (`reports/design_rules_mapping.md`). The conversion is an approximation of EAGLE's polygon pours and thermals; the original EAGLE file remains the design master.

## 1. Deliverables (claude.md addendum §18)

| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/POWER_SUPPLY_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/POWER_SUPPLY_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/POWER_SUPPLY_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/POWER_SUPPLY_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/POWER_SUPPLY_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/POWER_SUPPLY-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/POWER_SUPPLY_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/POWER_SUPPLY_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/POWER_SUPPLY_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/POWER_SUPPLY_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/POWER_SUPPLY_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/POWER_SUPPLY_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/POWER_SUPPLY_board_only.step`, `mechanical/POWER_SUPPLY_top_fab.dxf`, `ipc/POWER_SUPPLY.xml` (IPC-2581), `ipc/POWER_SUPPLY_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/POWER_SUPPLY.kicad_pcb` + `.kicad_pro`.

## 2. Board statistics (KiCad `pcb export stats` on the converted board)

| Item | Value |
|---|---|
| Outline (bounding box) | 280.0000 × 300.0000 mm |
| Copper layers | 2 (EAGLE layerSetup `(1*16)`) |
| Footprints (incl. free holes) | 320 |
| Pads THT / SMD / NPTH | 98 / 746 / 8 |
| Vias | 346 |
| Tracks / zones imported | 570 / 69 |
| Min track width / clearance used | 0.1000 / 0.3000 mm |
| Min drill used | 0.2540 mm |
| Board thickness | 1.6000 mm — **KiCad default, NOT from the source (UNVERIFIED)** |

## 3. Cross-check EAGLE XML ↔ KiCad conversion

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 280.0 | 280.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 320 | 320 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 346 | 346 | OK |  |
| Tracks (signal wires excl. airwires) | 570 | 570 | OK |  |
| Copper layers | 2 | 2 | OK |  |
| NPTH holes (free holes + package holes) | 8 | 8 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 444 | 444 | OK |  |

EAGLE airwires (layer 19): 309; signal polygons: 69; approved (waived) DRC/ERC entries in the source: 0.

## 4. Design rules

EAGLE DRU `PCBWay_2L_100um-Track *`: min width 0.1mm, min drill 0.3mm, wire-wire clearance 0.2mm. Mapping to KiCad: `reports/design_rules_mapping.md`.

## 5. Hole table (from `drill/drill_report.txt`)

| Type | Tool | Ø (mm) | Count |
|---|---|---|---|
| PTH | T1 | 0.254 | 8 |
| PTH | T2 | 0.300 | 4 |
| PTH | T3 | 0.350 | 42 |
| PTH | T4 | 0.600 | 300 |
| PTH | T5 | 1.000 | 68 |
| PTH | T6 | 1.016 | 20 |
| PTH | T7 | 1.321 | 2 |
| NPTH | T1 | 3.200 | 8 |
| **Total** | | PTH 444 / NPTH 8 | 452 |

## 6. DRC result (KiCad, rules from the EAGLE DRU)

Report: `reports/DRC_report.txt` / `.json`. Total violations 160, unconnected items 308. KiCad stops reporting a rule after 199 hits, so counts of exactly 199 are lower bounds. Breakdown:

| Rule | Count | Interpretation |
|---|---|---|
| `clearance` | 53 | copper clearance < DRU — review |
| `silk_over_copper` | 40 | silk over exposed copper — cosmetic/assembly |
| `silk_overlap` | 22 | overlapping silkscreen texts/lines — cosmetic |
| `zones_intersect` | 21 | overlapping pours of different priority — conversion artefact or design issue |
| `drill_out_of_range` | 8 | drill smaller than DRU msDrill |
| `solder_mask_bridge` | 8 | mask web between adjacent pads thinner than KiCad default (EAGLE has no such rule) — fabricator decision |
| `track_dangling` | 4 | track end not connected — review (stubs or unfinished routing) |
| `isolated_copper` | 4 | review |

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
- Routing incomplete: 309 EAGLE airwires; 308 unconnected items after KiCad fill.
