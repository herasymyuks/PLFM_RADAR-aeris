# 14. Manufacturing packages

**Chapter status summary:** generated manufacturing packages per board — SOURCE-DERIVED (Frequency Synthesizer, RF PA) / PARTIAL (Main Board, Power Supply) in `engineering/PCB/<BOARD>/`, BETA in `beta/pcb/<BOARD>/exports/`; stack-ups — PARTIAL with PROPOSED fabrication notes; BOMs — PARTIAL (0 MPN in the source, BETA proposals with confidence classes); EAGLE-native export procedures — documented, not executed (EAGLE is not installed on the authoring machine). **The KiCad conversion is not the designer-released package**: the EAGLE files in `4_Schematics and Boards Layout/` remain the design master, and no package in this chapter may be sent to a fabricator without the checklist in §14.6 being closed. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `engineering/PCB/<BOARD>/README.md` (§1, §5, §8, §9) and `STACKUP.md` for the four boards; `beta/pcb/README.md`, `CHANGELOG.md`, `beta/pcb/<BOARD>/FAB_NOTES.md`, `BOM_<BOARD>_beta.csv`, `exports/EXPORT_LOG.md`; `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`; `docs/PCB/<BOARD>.md` §10; `docs/BOM/README.md`.

## 14.1 What exists, and where

Two generated package trees exist per board. Both were produced with kicad-cli 10.0.6 from a KiCad import of the EAGLE board (`kicad-cli pcb import --format eagle`, EAGLE layer 47 *Measures* remapped to `Dwgs.User`, EAGLE design rules transferred to the project file — source: `engineering/PCB/<BOARD>/README.md` preserve-original paragraph). The conversion approximates EAGLE's polygon pours and thermals.

| Board | Layers | Outline (mm) | Reference conversion (unmodified import) | BETA package (routed/cleaned copy) | Status of the reference package | BETA result (source: `beta/pcb/README.md`) |
|---|---|---|---|---|---|---|
| Main Board (RADAR_Main_Board) | 10 | 260 × 300 | `engineering/PCB/MAIN_BOARD/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/MAIN_BOARD/exports/` (same sub-directories) + `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb`, `FAB_NOTES.md`, `BOM_MAIN_BOARD_beta.csv` | PARTIAL | unconnected 15 → 0; DRC 912 → 1049 (no real new item; polygon/thermal-pad items now visible); outside outline 11 → 6 (DNP) |
| Power Supply Board (PowerBoard) | 2 | 280 × 300 | `engineering/PCB/POWER_SUPPLY/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/POWER_SUPPLY/exports/` (same sub-directories) + `beta/pcb/POWER_SUPPLY/POWER_SUPPLY.kicad_pcb`, `FAB_NOTES.md`, `BOM_POWER_SUPPLY_beta.csv` | PARTIAL | unconnected 308 → 89; DRC 163 → 328; outside outline 132 → 0; placement needs designer review |
| Frequency Synthesizer (Clocks_Freq_Synth_board) | 6 | 100 × 100 | `engineering/PCB/FREQUENCY_SYNTHESIZER/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/FREQUENCY_SYNTHESIZER/exports/` (same sub-directories) + `beta/pcb/FREQUENCY_SYNTHESIZER/FREQUENCY_SYNTHESIZER.kicad_pcb`, `FAB_NOTES.md`, `BOM_FREQUENCY_SYNTHESIZER_beta.csv` | SOURCE-DERIVED | unconnected 0 → 0; DRC 639 → 639 (capped; silk conflicts 147 → 103); copper untouched |
| RF Power Amplifier (RF_PA) | 4 | 35 × 60 | `engineering/PCB/RF_PA/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/RF_PA/exports/` (same sub-directories) + `beta/pcb/RF_PA/RF_PA.kicad_pcb`, `FAB_NOTES.md`, `BOM_RF_PA_beta.csv` | SOURCE-DERIVED | unconnected 1 → 0; DRC 67 → 18; RF tracks untouched |

The "DRC before" figures are `engineering/PCB/<BOARD>/reports/DRC_report.json`, "after" `beta/pcb/<BOARD>/exports/reports/DRC_report.json`; KiCad caps each violation type at 199 entries (source: `beta/pcb/README.md`). The BETA export set is the same as that of `tools/kicad_pcb_pipeline.sh`, produced by `beta/pcb/tools/beta_export_package.sh` with the commands logged in `beta/pcb/<BOARD>/exports/EXPORT_LOG.md` (source: `beta/pcb/CHANGELOG.md` §All boards).

Files per package directory (file names for the Main Board; the other boards follow the same pattern with their own prefix and layer count — listing of `engineering/PCB/MAIN_BOARD/`):

| Sub-directory | Files | Format / note |
|---|---|---|
| `gerber/` | `MAIN_BOARD-F_Cu.gtl`, `-In1_Cu.g1 … -In8_Cu.g8`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Paste.gtp`, `-B_Paste.gbp`, `-F_Silkscreen.gto`, `-B_Silkscreen.gbo`, `-F_Fab.gbr`, `-B_Fab.gbr`, `-Edge_Cuts.gm1`, `-job.gbrjob` | RS-274X X2, Protel extensions, 6 decimals, mm |
| `drill/` | `MAIN_BOARD-PTH.drl`, `-NPTH.drl`, `-PTH-drl_map.pdf`, `-NPTH-drl_map.pdf`, `drill_report.txt` | Excellon mm, PTH/NPTH separate |
| `drawings/` | `MAIN_BOARD_top_layer.pdf`, `_bottom_layer_mirrored.pdf`, `_copper_layers.pdf` (one page per copper layer), `_outline.pdf`, `_assembly_top.pdf`, `_assembly_bottom_mirrored.pdf` | PDF; the two assembly PDFs are clipped by the A4 page frame (chapter 4 §4.5) |
| `svg/` | `MAIN_BOARD-F_Cu.svg … -B_Cu.svg`, `-F_Mask/-B_Mask`, `-F_Silkscreen/-B_Silkscreen`, `-F_Fab/-B_Fab`, `-Edge_Cuts.svg`, `MAIN_BOARD_top_composite.svg`, `MAIN_BOARD_bottom_composite_mirrored.svg` | per-layer plots (the layer-plot figures of chapters 4–7 are rendered from the two composites) |
| `assembly/` | `MAIN_BOARD_BOM.csv`, `MAIN_BOARD_pick_and_place.csv` | BOM from the schematic (values only); P&P both sides, mm |
| `mechanical/` | `MAIN_BOARD_outline.dxf`, `MAIN_BOARD_top_fab.dxf`, `MAIN_BOARD_board_only.step` | STEP is board body only (no component models) |
| `ipc/` | `MAIN_BOARD.xml.gz` (IPC-2581), `MAIN_BOARD_netlist.d356` (IPC-D-356) | for fabricator netlist test |
| `3d/` | `MAIN_BOARD_render_top.png`, `_bottom.png`, `_isometric.png` | KiCad renders, no component models |
| `reports/` | `DRC_report.txt`, `DRC_report.json`, `board_statistics.md`, `design_rules_mapping.md`, `kicad_import_report.txt` | reference package only has the import report and the DRU mapping |
| `kicad/` | `MAIN_BOARD.kicad_pcb`, `.kicad_pro`, `.kicad_prl` | editable conversion (reference package); the BETA board is at `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb` |

## 14.2 Deliverable tables (claude.md addendum §18), copied from the package READMEs

### Main Board (RADAR_Main_Board) — `engineering/PCB/MAIN_BOARD/README.md` §1 [PARTIAL]


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

### Power Supply Board (PowerBoard) — `engineering/PCB/POWER_SUPPLY/README.md` §1 [PARTIAL]


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

### Frequency Synthesizer (Clocks_Freq_Synth_board) — `engineering/PCB/FREQUENCY_SYNTHESIZER/README.md` §1 [SOURCE-DERIVED]


| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/FREQUENCY_SYNTHESIZER_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/FREQUENCY_SYNTHESIZER_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/FREQUENCY_SYNTHESIZER_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/FREQUENCY_SYNTHESIZER_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/FREQUENCY_SYNTHESIZER_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/FREQUENCY_SYNTHESIZER-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/FREQUENCY_SYNTHESIZER_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/FREQUENCY_SYNTHESIZER_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/FREQUENCY_SYNTHESIZER_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/FREQUENCY_SYNTHESIZER_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/FREQUENCY_SYNTHESIZER_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/FREQUENCY_SYNTHESIZER_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/FREQUENCY_SYNTHESIZER_board_only.step`, `mechanical/FREQUENCY_SYNTHESIZER_top_fab.dxf`, `ipc/FREQUENCY_SYNTHESIZER.xml` (IPC-2581), `ipc/FREQUENCY_SYNTHESIZER_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` + `.kicad_pro`.

### RF Power Amplifier (RF_PA) — `engineering/PCB/RF_PA/README.md` §1 [SOURCE-DERIVED]


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


## 14.3 Stack-ups

Layer order and copper thickness in every `STACKUP.md` come from the EAGLE DRU; dielectric thicknesses are the EAGLE DRU table and **not** a vendor stack-up; total thickness is not defined in any source (KiCad assumed 1.6 mm); material, prepreg/core assignment, finish and impedance targets must be supplied by the designer/fabricator (source: `engineering/PCB/<BOARD>/STACKUP.md` caveats; `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md` MDR-07). The only material evidence in the upstream project is `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` (a 6-layer picture, unlabelled, matching no board exactly) and the PCBWay impedance note delivered with the Frequency Synthesizer production files (RO4350B h = 0.102 mm, 50 Ω w = 0.204 mm, 100 Ω w/s = 0.204/0.26 mm, maskless RF, coupons).

| Board | DRU | Layer setup (EAGLE) | DRU dielectrics (mm, top → bottom) | PROPOSED fabrication stack (BETA `FAB_NOTES.md` §2) | PROPOSED finished thickness |
|---|---|---|---|---|---|
| Main Board | `PCBWay_8L_100um-Track` (name says 8, board has 10 layers) | `(1*2+3*4+5*12+13*14+15*16)` | 0.102, 0.2, 0.2, 0.2, 0.2, 0.15, 0.2, 0.2, 0.102 | L1 and L9 on RO4350B 4 mil, FR-4 inside; ENIG; maskless RF; 1 oz all layers | 2.0 mm ± 10 % (DRU sum 1.554 + copper ≈ 1.9 mm) |
| Power Supply | `PCBWay_2L_100um-Track` | `(1*16)` | 1.5 | FR-4 Tg 150 °C core; 35 µm, PROPOSED 70 µm / 2 oz; no impedance control | 1.6 mm ± 10 % |
| Frequency Synthesizer | `PCBWay_6L_100um-Track` | `(1+2*3+14*15+16)` | 0.11, 0.6, 0.11, 0.6, 0.11 | L1 on RO4350B 4 mil (DRU 0.11 vs note 0.102 — reconcile), FR-4 cores 0.6, L5/6 RO4350B PROPOSED (B.Cu LVDS pairs); ENIG; maskless RF | 1.6 mm ± 10 % with thinned cores, or 2.0 mm |
| RF PA | `PCBWay_4L_100um-Track` (unexplained 70 µm third copper slot) | `(1+2*15+16)` | 0.11, 1.2, 0.11 | F.Cu on RO4350B 4 mil, FR-4 core 1.2; paddle vias filled and capped PROPOSED; ENIG; maskless RF | 1.6 mm ± 10 % (DRU sum 1.42 + copper ≈ 1.56 mm) |

Full per-layer tables are in chapters 4–7 §Stack-up. Common proposal items for all boards (source: `beta/pcb/<BOARD>/FAB_NOTES.md` §3): ENIG 2–5 µin Au over 120–240 µin Ni; green LPI mask both sides, white silk; vias tented except RF-layer vias near maskless traces (fab to confirm); 100 % electrical test against the supplied IPC-D-356 netlist; IPC-A-600 Class 2; single boards, fab may panelise with rails, no V-cut through RF areas. Open items for every board (same source §6): confirm stack-up materials and total thickness; confirm the RF-layer dielectric (0.102 vs 0.11 mm) and re-solve w/s with coupons; confirm finish and mask-opening policy on RF traces; review the DRC disposition before CAM.

## 14.4 BOMs with MPN confidence

The source schematics carry **no MPN attribute on any part** (0/98, 0/28, 0/40, 0/11 lines; source: `docs/BOM/README.md`). `docs/BOM/BOM_<BOARD>.csv` is generated by `tools/gen_eagle_bom.py` directly from the `.sch` files; `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv` adds `manufacturer, mpn, mpn_confidence, dnp, note` with proposals from `beta/pcb/tools/beta_bom_mpn.py` (Murata GRM / Yageo RC / Murata LQP03 / TDK VLP families for passives, orderable IC codes for the device sets — source: `beta/pcb/README.md`).

| Board | Physical references | Line items | References without value | HIGH (deviceset = MPN) | MEDIUM (standard passive from value+package) | LOW (guess / non-standard value / conflict) | EMPTY (no value) |
|---|---|---|---|---|---|---|---|
| Main Board | 776 | 98 | 244 | 23 lines / 204 pcs | 41 / 461 | 30 / 93 | 4 / 18 |
| Power Supply Board | 312 | 28 | 80 | 7 lines / 79 pcs | 18 / 225 | 3 / 8 | 0 / 0 |
| Frequency Synthesizer | 184 | 40 | 47 | 10 lines / 37 pcs | 22 / 110 | 6 / 29 | 2 / 8 |
| RF Power Amplifier | 25 | 11 | 6 | 5 lines / 6 pcs | 6 / 19 | 0 / 0 | 0 / 0 |

Line counts obtained with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv'))))"` on 2026-10-09; quantities from `beta/pcb/README.md` §BOM confidence; reference/line/value counts from `docs/BOM/README.md`. Conflicts flagged in the BETA `note` column that only the designer can resolve (source: `beta/pcb/README.md`): voltage ratings absent; non-E-series values (2.443 kΩ, 103 pF, 107.3 nH); 47 µF in 0201; NX3225 footprint with a 32.768 kHz value; 5 mΩ shunt with a 0.1 Ω part number; Main Board R60/R61/R83/R84/R145/R146 marked `dnp = yes` (no net). BOM validation procedure (source: `docs/BOM/README.md` §Validation): regenerate; compare `qty` sum with the element counts 776 / 312 / 25 / 184; look every `UNVERIFIED` line up at a distributor and write the MPN into the schematic part attribute `MPN`, then regenerate; fill every empty value (244/80/6/47); add a `DNP` attribute per variant; acceptance = 0 `UNVERIFIED`, 0 empty values, DNP column present, part count identical to the `.mnt` pick-and-place.

## 14.5 EAGLE-native export procedures (summary of `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`)

All four boards are EAGLE XML files: Main Board 7.4.0 (sch + brd), Frequency Synthesizer 9.6.2, RF PA 9.6.2, Power Board sch 9.6.2 / brd 7.4.0 (mismatch); libraries are embedded. EAGLE 9.6.2 opens all of them (and upgrades 7.4.0 files on save — keep the originals), as does Fusion 360 Electronics; KiCad 7/8/9 imports EAGLE 6+ XML. Output file names below are the tools' defaults and are **expected, not observed** — the upstream project never produced them (source: `00_COMMON_EAGLE_PROCEDURES.md` preamble). EAGLE is not installed on the authoring machine; none of these procedures has been executed here.

| ID | Procedure | Tool / menu | Expected output | Acceptance |
|---|---|---|---|---|
| P-EAGLE-01 | Open and consistency-check a board pair | EAGLE 9.6.2 File → Open → Schematic; board opens with it; ERC → *Consistency check*. Power Board: expect the "severed annotation" dialog, do **not** accept automatic fixes; export both part lists and reconcile | both windows open | "Board and schematic are consistent" |
| P-EAGLE-02 | ERC | schematic → Tools → ERC; reopen every `<approved>` entry (Main Board: 4 on `STM32_MISO_1V8`) | screenshot/transcript into `docs/PCB/reports/<board>_ERC_<date>.txt` (directory to create) | 0 errors; every warning dispositioned |
| P-EAGLE-03 | DRC with the stored rules | board → type `RATSNEST` (expect "Nothing to do" on Synth/PA; 2 390 airwires Main, 309 Power) → Tools → DRC → *Check* with the stored DRU | DRC error list, exported | 0 unapproved errors; each approved error justified |
| P-EAGLE-04 | Gerber + drill (EAGLE 9.6.2 CAM) | File → CAM Processor → Templates `2 Layer` / `4 Layer` / `6 Layer` (Main Board: start from `6 Layer`, add layers 3, 4, 5, 12, 13, 14 as inner copper); RS-274X, mm, 4.4, ZIP; Excellon mm, PTH/NPTH separate | `CAMOutputs/GerberFiles/copper_top.gbr, copper_inner_<n>.gbr, copper_bottom.gbr, soldermask_*, silkscreen_*, solderpaste_*, profile.gbr, gerber_job.gbrjob`; `DrillFiles/drill_1_16.xln`, `drill_npth.xln` | viewer check: layer count and outline match `docs/MECHANICAL/drawings/<BOARD>_outline.svg`; drill counts match `docs/PCB/<BOARD>.md` |
| P-EAGLE-05 | Gerber + drill (EAGLE 7.4 CAM, for the 7.4.0 files) | `gerb274x.cam` / `excellon.cam` jobs | `<board>.cmp, .sol, .ly2…, .plc/.pls, .stc/.sts, .crc/.crs, .drd + .dri` | prefer 9.6.2 unless the designer requires 7.4 |
| P-KICAD-01 | Alternative open-source export | KiCad File → Import → Non-KiCad Project → EAGLE; re-enter the 10-layer stack for the Main Board in Board Setup; `kicad-cli pcb export gerbers` / `export drill` | `board-F_Cu.gbr … board-PTH.drl, board-NPTH.drl, board-job.gbrjob` | re-DRC and compare with the EAGLE output before use (importer approximates polygons/thermals) |
| P-EAGLE-06 | BOM export | schematic → File → Run ULP → `bom.ulp` → Parts/Values, CSV, all attributes; compare with `docs/BOM/BOM_<BOARD>.csv` | `<Board>_BOM.csv` | every line has MPN + package; passives valued (244/80/6/47 missing today); DNP column |
| P-EAGLE-07 | Pick-and-place and drawings | board → Run ULP → `mountsmd.ulp` (+ `mount.ulp` for THT); assembly drawing = layers 20, 21, 25, 51 (+ bottom) → Print → PDF 1:1; fab drawing = layers 20 + 44 + 45 + dimensions on 48 + text block (layer count, material, thickness, copper, finish, colours, impedance table from the PCBWay note, min track 0.1 mm, min drill 0.15 mm Main/Synth/PA, 0.3 mm Power) | `<board>-smd.mnt`, `-tht.mnt` (`RefDes,Value,Package,X,Y,Rot,Side`), `<board>_assembly_top/bottom.pdf`, `<board>_fab.pdf` | Synth: regenerate the `.mnt` pair to supersede the four duplicate files |
| P-EAGLE-08 | Schematic PDF | schematic → File → Print → PDF, all sheets, fit to page, black, caption | `<board>_schematic.pdf` under `docs/PCB/schematics/` (directory to be created) | — (SOURCE-DERIVED renders exist in `engineering/ELECTRICAL/schematics/` meanwhile) |
| P-EAGLE-09 | Netlist export without EAGLE | `python3 tools/extract_eagle_netlist.py <sch> --part <REF> --out <csv>` / `--list-parts`; EAGLE alternative File → Export → Netlist | CSV net ↔ pin ↔ pad | used for the connection reports of chapters 4–7 |

Expected manufacturing package structure per board (source: `00_COMMON_EAGLE_PROCEDURES.md` §Manufacturing package structure):

```
4_7_Production Files/<Board>/
├── Gerber/        copper_*.gbr, soldermask_*.gbr, silkscreen_*.gbr, solderpaste_*.gbr, profile.gbr, *.gbrjob
├── Drill/         drill_*_pth.xln, drill_npth.xln, drill map pdf
├── <Board>_fab.pdf
├── <Board>_assembly_top.pdf, <Board>_assembly_bottom.pdf
├── <Board>_BOM.csv            (with MPN, manufacturer, DNP)
├── <Board>-smd.mnt, <Board>-tht.mnt
├── <Board>_schematic.pdf
├── <Board>_netlist.ipc (IPC-D-356, optional)
└── reports/ ERC, DRC, impedance/stack-up confirmation from the fab
```

Board-specific notes for the EAGLE path: Main Board — P-EAGLE-04 with a **10-layer** job; reopen the 211 approved DRC entries; decide 8 vs 10 layers (copper exists on all 10) (source: `docs/PCB/MAIN_BOARD.md` §5, §7). Power Board — complete placement and routing first (designer); `RATSNEST` expects 309 airwires until then (source: `docs/PCB/POWER_SUPPLY.md` §5). Frequency Synthesizer — template *6 Layer* with inner layers 2, 3, 14, 15; keep `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` under `reports/` (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §5, §9). RF PA — template *4 Layer* with inner layers 2 and 15; add the impedance-note text to the fab drawing only after the designer confirms it applies to this stack (source: `docs/PCB/RF_PA.md` §5).

## 14.6 Fabrication checklist (README §8 of every package)

The checklist is identical for the four boards except for the routing line; state on 2026-10-09 (source: `engineering/PCB/<BOARD>/README.md` §8):

| Item | Main Board | Power Supply | Frequency Synthesizer | RF PA |
|---|---|---|---|---|
| Gerber set (all copper, mask, paste, silk, outline, fab) exported | done | done | done | done |
| Excellon drill files PTH/NPTH + drill map + report | done | done | done | done |
| Pick-and-place (both sides, mm, CSV) | done | done | done | done |
| BOM with reference designators | done | done | done | done |
| BOM with manufacturer part numbers for 100 % of lines | open | open | open | open |
| Fabrication drawing with vendor notes (material, thickness, finish, mask/silk colours, tolerances, impedance) | open | open | open | open |
| Stack-up confirmed by the fabricator | open | open | open | open |
| Layout routed to completion (0 airwires / 0 unconnected) | open in the source (BETA: 0 unconnected, netlist issues remain) | open (BETA: 89 open) | done | open in the source (1 unconnected after import; BETA 0) |
| DRC with 0 unapproved errors, waivers documented | open | open | open | open |
| Designer review of the KiCad conversion against EAGLE (pours, thermals, text) | open | open | open | open |
| Gerbers viewed in an independent viewer and compared with the outline drawing | open | open | open | open |
| IPC-2581 / IPC-D-356 netlist test accepted by the fabricator | open | open | open | open |

Known gaps common to all boards (source: `engineering/PCB/<BOARD>/README.md` §9, BLOCKED — MISSING DATA): board material, finished thickness, copper weight per layer, surface finish, mask/silk colours and impedance targets are not recorded in the EAGLE files; no MPN attributes; 3-D component models not embedded (Autodesk online URNs) so every STEP is board-only.

## 14.7 Acceptance criteria per board (copied from `docs/PCB/<BOARD>.md` §10)

### Main Board (RADAR_Main_Board) — `docs/PCB/MAIN_BOARD.md` §10

| Criterion | Measure |
|---|---|
| Layout complete | 0 airwires; 0 elements outside 0..260 × 0..300 mm |
| DRC | 0 unapproved errors with PCBWay 10-layer (or revised) rules |
| ERC | 0 errors |
| Gerber set | 10 copper + 2 mask + 2 silk + 2 paste + profile + job file; viewer check matches `MAIN_BOARD_outline.svg` (260 × 300 mm, 8 × Ø3.2 holes) |
| Drill | PTH count = 2 893 vias + plated pads; NPTH = 8 × 3.2 mm + 2 × 0.9 mm |
| Stack-up | vendor drawing for 10 layers, RO4350B 0.102 mm outer cores, 50 Ω at 0.204 mm, 100 Ω diff 0.204/0.26 mm confirmed |
| BOM | 100 % MPN coverage; DNP column; quantity sum = 776 (minus DNP) |
| Design decisions closed | FT601 wired or removed; FPGA part; HSE crystal; XADC reference wiring |

### Power Supply Board (PowerBoard) — `docs/PCB/POWER_SUPPLY.md` §10

| Criterion | Measure |
|---|---|
| Consistency | ERC consistency check passes after re-linking sch/brd in one EAGLE version |
| Placement/routing | 0 airwires, 0 off-board parts, final outline recorded |
| DRC/ERC | 0 errors |
| Gerber/drill | 2 Cu layers + mask/silk/paste/profile; NPTH 8 × Ø3.2; viewer matches `POWER_SUPPLY_outline.svg` (280 × 300 mm, or the revised outline) |
| BOM | 100 % MPN; all passives valued; datasheets for TPS562208 and LM2662 added to `7_Components Datasheets` |
| Design closure | PA supply (22 V rail) architecture decided and consistent with `Power Management V6.xlsx` and `RF_PA.sch` |

### Frequency Synthesizer (Clocks_Freq_Synth_board) — `docs/PCB/FREQUENCY_SYNTHESIZER.md` §10

| Criterion | Measure |
|---|---|
| DRC/ERC | 0 errors, reports archived |
| Gerber/drill | 6 Cu + mask/silk/paste/profile; NPTH 4 × Ø3.2; PTH = 769 vias + pads; viewer matches `FREQUENCY_SYNTHESIZER_outline.svg` (100 × 100 mm) |
| Stack-up | one vendor-confirmed 6-layer stack consistent with the impedance note |
| BOM | 100 % MPN, 0 value-less references, oscillator conflict resolved |
| P&P | single regenerated pair of `.mnt` files, duplicates removed |
| Function (post-fab) | AD9523 lock (STATUS0/1 high), OUT6 = 100 MHz, OUT4/5 = 400 MHz, OUT10/11 = 120 MHz measured — hardware test, not a file check |

### RF Power Amplifier (RF_PA) — `docs/PCB/RF_PA.md` §10

| Criterion | Measure |
|---|---|
| DRC/ERC | 0 errors (already 0 approved in file; must be re-run) |
| Gerber/drill | 4 Cu + mask/silk/paste/profile; NPTH 7 × Ø3.2; PTH count = 342 vias + pads; viewer matches `RF_PA_outline.svg` (35 × 60 mm) |
| Stack-up | vendor drawing confirmed; RF layer mask-free as per impedance note |
| BOM | 100 % MPN; all 25 references valued/identified |
| System | PA supply voltage/current source decided; quantity per variant (16 for AERIS-10X) confirmed; RF performance (gain, P1dB at 10.5 GHz) remains **unverified** until measured |


Do not declare any board fabrication-ready on the basis of the existing `.sch/.brd` files, of the KiCad conversion or of the BETA packages (source: `docs/PCB/MAIN_BOARD.md` §10; `beta/pcb/README.md`).

## 14.8 Antenna panel package (PROPOSED DESIGN)

The proposed patch panel has its own KiCad-native package in `engineering/DESIGN/ANTENNA/kicad_exports/` (Gerber `F_Cu/B_Cu/F_Mask/B_Mask/F_Silkscreen/Edge_Cuts` + job file, drill, PDF, SVG, STEP, 3-D render, statistics, DRC — all steps exit 0, source: `kicad_exports/EXPORT_LOG.md`). It is a design proposal awaiting simulation closure and a coupon measurement (chapter 8 §8.6) and is **not released** for fabrication.
