# Missing drawings — recovery plan

Document ENG-MDR-01 · Rev A · 2026-10-09. One guide per drawing that could **not** be generated from repository evidence (status BLOCKED — MISSING DATA or PARTIAL in `DRAWING_REGISTER.md`), in the format of claude.md addendum §21. Guides for drawings that *were* generated are the generator scripts themselves (`tools/*.py`, `tools/kicad_pcb_pipeline.sh`) — their usage lines are the procedure, and `engineering/VALIDATION/CAD_EXPORT_LOG.md` is the execution record.

Common conventions for every guide below: units mm; title block per ISO 7200 fields (project AERIS-10, drawing number from the register, revision, date, sheet, scale, status); sheet sizes per ISO 5457 (A3 landscape unless stated); nothing may be dimensioned from the photographs in `8_Utils/`.

---

## MDR-01 — MECH-ENC-01 Main enclosure (overall geometry, mounting, PCB supports, connector openings)

- **Engineering purpose:** define the chassis that carries the four PCB types, provides RF connector access and heat paths; required for ASM-EXP-01 to become a real drawing and for assembly steps M1–M6.
- **Available source evidence:** PCB outlines and hole tables (`MECHANICAL/dimensions/*_dimensions.md`, `MECHANICAL/DXF/*`, `MECHANICAL/STEP/*`); connector positions can be read from `PCB/<BOARD>/assembly/<BOARD>_pick_and_place.csv` (X/Y of J*/X* references).
- **Missing source information:** envelope, material, wall thickness, board stacking order and spacing (G-04, G-05), component heights (G-02), thermal path (G-08), ingress/EMC requirements — all are design decisions, not recoverable.
- **Required software:** FreeCAD 1.0 (free; Part Design + TechDraw workbenches) or any MCAD. KiCad 10 for the board STEP bodies (already exported).
- **Input files:** `MECHANICAL/STEP/*_board_only.step`, `PCB/*/assembly/*_pick_and_place.csv`, decisions from the designer (written record).
- **Procedure:** (1) FreeCAD → File → Import each STEP; place them per the decided stacking (record the decision in `VALIDATION/UNRESOLVED_GEOMETRY.md` G-05 with author/date). (2) Part Design → new body "Chassis"; sketch the base plate from the Main/Power hole patterns (`*_dimensions.md` §2), extrude to the decided thickness. (3) Add stand-off bosses at every Ø3.2 hole (M3 inferred — confirm fastener spec G-11). (4) Cut connector openings where the P&P shows J*/X* parts on the board edge; verify with the board STEP overlaid. (5) TechDraw → new page A3 (ISO 5457), insert front/top/side views (ISO 128 third-angle), dimension per ISO 129-1 all mounting positions and openings, add title block ISO 7200. (6) Export: File → Export → STEP (`MECHANICAL/STEP/enclosure.step`), TechDraw → Export page as SVG and PDF (`MECHANICAL/PDF/MECH-ENC-01.pdf`). (7) Compare: re-import the enclosure STEP with the board STEPs and run FreeCAD Part → Check geometry → interference = 0.
- **Validation checklist:** every PCB hole has a boss; every edge connector has an opening ≥ connector body + cable; interference check 0; drawing has all ISO 7200 fields; status set to SOURCE-DERIVED only after the geometry decisions are written down.
- **Expected outputs:** `MECHANICAL/CAD/enclosure.FCStd`, `MECHANICAL/STEP/enclosure.step`, `MECHANICAL/DXF/enclosure_*.dxf`, `MECHANICAL/PDF/MECH-ENC-01.pdf`, register row MECH-ENC-01 updated.
- **Acceptance:** drawing reviewed by the hardware owner; fasteners and materials specified; mass computed from CAD replaces the ESTIMATE in `MECHANICAL/dimensions/README.md`.

## MDR-02 — MECH-INT-01 Internal component layout and cable routing

- **Purpose:** show board positions, harness paths, service access.
- **Evidence:** cable list with endpoints (`SYSTEM/interfaces/interconnection_table.md`, CBL-00…CBL-106 proposals); board outlines.
- **Missing:** enclosure (MDR-01), cable types/lengths/gauges (G-09), bend-radius rules for the 10.5 GHz coax.
- **Software/inputs:** FreeCAD (after MDR-01) or a 2-D drawing from `MECHANICAL/CAD/pcb_set_plan_view.svg` as a base; `interconnection_table.md`.
- **Procedure:** (1) start from `pcb_set_plan_view.svg` (editable; Inkscape or any SVG editor), move the four outlines into the decided arrangement at scale 1:1; (2) draw each cable as a polyline between the connector positions taken from the P&P files, label with CBL-ID; (3) add keep-outs around J24..J55 (SMA field) and the QPA2962 heatsink; (4) generate a cable schedule table (ID, from, to, type, length measured from the drawing, gauge) and append it to `interconnection_table.md`; (5) export SVG + PDF (`tools/svg_sheets_to_pdf.py`).
- **Validation:** every CBL-ID in the table appears once in the drawing; lengths ≥ straight-line distance; coax count = 34 (Main SMA J1..J55 used ports) — cross-check with `ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §2.
- **Outputs:** `MECHANICAL/CAD/internal_layout.svg/.pdf`, cable schedule. **Acceptance:** harness manufacturer can quote from the schedule.

## MDR-03 — MECH-ANT-01 Antenna assembly

- **Purpose:** element geometry, feed network, mounting and radome; needed for the RF path to exist at all (K8).
- **Evidence:** `02_hardware/04_antenna_beamforming.md` (16 elements, λ/2 = 14.3 mm, aperture 214.3 mm), `8_Utils/Antenna_Array.jpg` (photo, no scale), `5_Simulations/` (two contradictory waveguide simulations), Main Board SMA field (34 ports).
- **Missing:** everything dimensional (G-06); which simulation reflects the built prototype; feed/transition to the PA SMA ports.
- **Software:** openEMS/QucsStudio (already used in `5_Simulations`), FreeCAD; Altium/KiCad if the antenna is a PCB.
- **Procedure:** (1) designer decides the antenna type (record decision); (2) model it in CAD with the 14.3 mm pitch as the only inherited constraint; (3) produce TechDraw sheets (front, section through a feed, mounting interface to MDR-01), dimension per ISO 129-1; (4) export STEP/DXF/PDF; (5) validate against the simulation model used (same dimensions in the openEMS script and the CAD).
- **Outputs:** `MECHANICAL/CAD/antenna.FCStd`, `MECHANICAL/STEP/antenna.step`, `MECHANICAL/PDF/MECH-ANT-01.pdf`. **Acceptance:** simulated S11 and pattern files committed alongside; mounting interface matches MDR-01.

## MDR-04 — MECH-COOL-01 Cooling and power assembly

- **Purpose:** heatsink/fan placement for 16 × QPA2962 (xlsx: IDQ 1.68 A at 22 V each) and the Power Board regulators; maintenance access.
- **Evidence:** `Power Management V6.xlsx` rows 58-62; PA board outline and 7 holes; regulator positions in `PCB/POWER_SUPPLY/assembly/POWER_SUPPLY_pick_and_place.csv`.
- **Missing:** dissipation budget (no current budget per rail), ambient/enclosure conditions, heatsink part, fan part (G-08).
- **Procedure:** (1) compute dissipation per PA from the bias point (record assumptions); (2) select heatsink/fan (part numbers → `ASSEMBLY/PARTS_LIST.md`); (3) FreeCAD: heat-spreader plate with the 16 PA hole patterns (`RF_PA_dimensions.md` §2 repeated at the decided pitch), fan cut-outs; (4) TechDraw sheet with thermal-interface notes; (5) export STEP/PDF.
- **Validation:** hole pattern of each PA position matches `RF_PA_outline_holes_eagle.dxf` exactly (overlay in FreeCAD); thermal calculation attached. **Outputs:** `MECHANICAL/STEP/heat_spreader.step`, `MECHANICAL/PDF/MECH-COOL-01.pdf`.

## MDR-05 — MECH-PED-01 Pedestal / azimuth drive

- **Evidence:** `main.cpp:189,195` (200 steps/rev, 50 azimuth positions), stepper and slip-ring names in the xlsx. **Missing:** all mechanics (G-07). **Procedure:** as MDR-01 after motor/slip-ring selection; add the slip-ring channel count = number of conductors crossing the rotation (count from the cable schedule of MDR-02). **Outputs:** `MECHANICAL/PDF/MECH-PED-01.pdf`, STEP.

## MDR-06 — ASM-EXP-01 upgrade from CONCEPTUAL to SOURCE-DERIVED exploded view

- **Evidence:** board STEP bodies; CONCEPTUAL SVG `ASSEMBLY/EXPLODED_VIEWS/`. **Missing:** MDR-01..05 outputs, fastener spec.
- **Procedure:** FreeCAD Assembly workbench: insert chassis, boards, heat-spreader, antenna; create an exploded view (Assembly → Exploded view, one line per fastener group); TechDraw page with balloons mapped to `ASSEMBLY/PARTS_LIST.md` IDs (ISO 128 leader lines); export PDF/SVG; replace the CONCEPTUAL file and update the register status.
- **Acceptance:** every balloon ↔ parts-list row; fastener identification present; assembly sequence M1–M6 rewritten against the real geometry.

## MDR-07 — PCB fabrication drawings with vendor notes (PCB-*-09/11 to reach VERIFIED)

- **Evidence:** `PCB/<BOARD>/STACKUP.md` (layer order from DRU), `Stack_Hybrid.png`, `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf`. **Missing:** material, finished thickness, copper weights, finish, mask/silk colours, impedance table, tolerances.
- **Procedure (EAGLE path, preferred because EAGLE is the master):** open the `.brd` in EAGLE 9.6.2 → Layer settings show 20, 44, 45, 48 → `DIMENSION` tool on layer 48 for outline and hole datum → `TEXT` block with the vendor notes (values supplied by the designer/fabricator — never invented) → Print → PDF 1:1 → `engineering/PCB/<BOARD>/drawings/<BOARD>_fabrication.pdf`; CAM Processor → Gerber set (P-EAGLE-04 in `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`) and compare layer-by-layer with the KiCad Gerbers in `gerbv` (same outline, same drill count). **KiCad path:** Board Setup → Physical Stackup (enter vendor values) → File → Fabrication Outputs → Gerbers + Drill → add a Dwgs.User sheet with the notes → `kicad-cli pcb export pdf -l Edge.Cuts,Dwgs.User`.
- **Validation:** `tools/check_manufacturing_files.py` exit 0; fabricator DFM report attached; drill count = hole table. **Acceptance:** status VERIFIED only after the EAGLE-generated and KiCad-generated Gerbers agree and the fabricator confirms the stack-up.

## MDR-08 — Completion of the Main and Power Board layouts (prerequisite for PCB-MAIN_BOARD-*/PCB-POWER_SUPPLY-* to leave PARTIAL)

- **Evidence:** `ELECTRICAL/netlists/<BOARD>_unresolved_connections.md` §5 (airwire list), KiCad DRC `unconnected_items` (15 for Main after pour fill — mostly GND/+3V3_FPGA/+3V3_FT pads and arc stubs; 308 for Power), 132 Power elements outside the outline (`docs/PCB/POWER_SUPPLY.md`).
- **Procedure:** in EAGLE (master): `RATSNEST` → route the listed signals → `DRC` with the stored DRU → 0 unapproved errors → save; then re-run `bash tools/kicad_pcb_pipeline.sh MAIN_BOARD POWER_SUPPLY` and `python3 tools/gen_engineering_pcb_docs.py` to regenerate the package and the cross-check. For Power also decide the final outline (G-10).
- **Acceptance:** `unconnected_items` = 0 in `PCB/<BOARD>/reports/DRC_report.json`; airwires = 0 in the EAGLE file.

## MDR-09 — 3-D component models and assembled STEP

- **Evidence:** `package3d_urn` attributes in the EAGLE files (Autodesk cloud IDs, not embedded). **Missing:** model files. **Procedure:** in KiCad PCB Editor open `PCB/<BOARD>/kicad/<BOARD>.kicad_pcb` → Footprint properties → 3D models → assign models from the KiCad library (`PCM`/`packages3D`) or vendor STEP files for each distinct package (list: `docs/BOM/BOM_<BOARD>.csv` column `package`) → `kicad-cli pcb export step --subst-models -o <BOARD>_assembled.step`. **Validation:** `kicad-cli pcb render` shows bodies; max height recorded in `*_dimensions.md` §3. **Acceptance:** G-02 resolved.

## MDR-10 — Native KiCad schematics (editable twin of the EAGLE schematics)

- **Evidence:** EAGLE `.sch` files are the editable natives (already present). **Why still listed:** the addendum asks for an "updated electrical schematic package"; the SVG/PDF sets here are renderings, and KiCad's schematic importer is GUI-only. **Procedure:** KiCad → File → Import → Non-KiCad Project → EAGLE → select `.sch` (the `.brd` imports with it) → save as `engineering/ELECTRICAL/schematics/<BOARD>/kicad/<BOARD>.kicad_sch` → `kicad-cli sch export pdf` and `kicad-cli sch erc` → compare the ERC with `ELECTRICAL/netlists/<BOARD>_unresolved_connections.md` and the netlist with `kicad-cli sch export netlist` vs `<BOARD>_netlist.csv` (same net count and pin count). **Acceptance:** net and pin counts equal; ERC dispositioned.

## MDR-11 — Hardware-verified drawings (status VERIFIED)

Every SOURCE-DERIVED drawing becomes VERIFIED only by comparison with an EAGLE print/CAM output or with the physical board (outline and hole positions measured, connector positions checked). Record each comparison in `VALIDATION/DRAWING_CHECKS.md` §2 with date, method and result.

---

## Status update 2026-10-09 — proposals now exist

| Guide | Proposal delivered | Remaining to reach SOURCE-DERIVED / VERIFIED |
|---|---|---|
| MDR-01 enclosure | `engineering/DESIGN/MECHANICAL/` (FreeCAD model DSN-MECH-3D, drawings DSN-MECH-01…03) | owner approval of D-07…D-09; sheet-metal detailing (bends, fasteners, gaskets); component heights |
| MDR-02 internal layout + harness | DSN-MECH-04 (connector positions from P&P), DSN-HAR-01 (144 cables, lengths) | first-fit length check; unmatched rail pairs; stepper driver location |
| MDR-03 antenna | DSN-ANT-01 (native KiCad board, calc sheet, openEMS model) | run openEMS; coupon; connector footprint |
| MDR-04 cooling | DSN-THM-01 + fin fields in DSN-MECH-3D | PA-board via-field Rth; fan part selection; test |
| MDR-05 pedestal | DSN-MECH-05 + pedestal in DSN-MECH-3D | bearing/slip-ring/motor part selection; mast interface |
| MDR-06 exploded view | still CONCEPTUAL (ASM-EXP-01); the FreeCAD assembly can now be exploded in the GUI | FreeCAD Assembly exploded view + balloons |
| MDR-12 (new) 22 V PA supply | DSN-PSU-01 block schematic, BOM, nets | KiCad component-level schematic + layout; TX_GATE pin allocation; bench test of one gate channel |
