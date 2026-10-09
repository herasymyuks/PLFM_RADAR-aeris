# Assembly procedure — PCB assemblies, head, harness, pedestal

**Author of this chapter:** Antidrone Ukraine · antidrone.cc.

**Status summary:** the whole procedure is **PROPOSED / BETA — never executed** (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, header). Mechanical steps rest on the PROPOSED DESIGN of chapter 10 (D-07…D-13); electrical integration order is SOURCE-DERIVED from the connector matrix and the firmware power sequence (`engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md`, status PARTIAL); cable lengths are PROPOSED (`engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`); Molex pin order, the RFIN/RFOUT side of the Main Board SMA pairs and the PA-instance assignment are UNVERIFIED (`engineering/SYSTEM/interfaces/interconnection_table.md` §2, §7). Steps that depend on an open decision carry ⚠ and name it. Torque values quoted from the step source have no deeper repository source and are marked ASSUMED.

**Sources:** `manual/ASSEMBLY_STEPS_SOURCE.md` (phases A–D), `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` (ASM-SEQ-01), `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (part # and fasteners), `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-04…07`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` (CBL-001…144), `engineering/SYSTEM/interfaces/interconnection_table.md`, `engineering/ELECTRICAL/power_distribution/power_rails.md`, `engineering/MECHANICAL/dimensions/*.md`, `tools/design_layout.py` (stations), `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`.

**Figures in this chapter:** F15.1 exploded view, F15.2–F15.5 per-board assembly drawings, F15.6 DSN-MECH-07, F15.7 DSN-MECH-06, F15.8 DSN-MECH-04, harness schedule excerpt (table).

## 15.0 Safety preamble — read before any step

Copied from the step source (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, "Safety preamble"), with the evidence behind each hazard:

- **S1 — 22 V PA drain supply (up to 45 A pulsed):** never connect PA boards with VG at 0 V; VG −4 V first (firmware sequence). Evidence: QPA2962 bias-up "VG −4 V → VD +22 V → raise VG until IDQ 1680 mA" (source: `engineering/ELECTRICAL/power_distribution/power_rails.md` §1 row `+22V0`/`VD`, xlsx L58-L62); 45 A pulse peak from D-14 (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2). The 22 V source itself is **not in any CAD file** (conflict K4).
- **S2 — RF radiation:** no transmission without a terminated or connected antenna/PA path; 16 × 10 W peak (source: QPA2962 PSAT 40 dBm, `engineering/DESIGN/00_DESIGN_BASIS.md` §1).
- **S3 — Rotating pedestal:** keep hands clear; set the stepper-driver current limit before first motion (TB6600-class, 9–42 V, 4 A, 20 V selected — source: `engineering/DESIGN/00_DESIGN_BASIS.md` §1, xlsx row 63).
- **S4 — ESD:** all boards are ESD-sensitive (GaN PA, ADC, FPGA).

Also applicable throughout: ⚠ **K2** — the beta firmware assumes the 8 MHz HSE crystal found on the schematic (`beta/stm32/DECISIONS.md` D-01); ⚠ **K4** — 22 V PA supply not in CAD; ⚠ **D-14** — per-pulse drain gating required by the thermal design (chapter 10 §10.7) has no hardware yet.

## 15.1 Pre-assembly inspection checkpoints

Copied (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §A):

| CP | Check | Acceptance | Evidence/tool |
|---|---|---|---|
| CP-1 | Bare board matches outline and hole table | dimensions per `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md`, ±0.2 mm (vendor tolerance UNSPECIFIED) | caliper; fab CoC |
| CP-2 | Assembled board matches BOM + pick-and-place | every reference populated with the BOM value; polarity per `drawings/<BOARD>_assembly_top.pdf` | AOI / visual |
| CP-3 | No shorts between rails | > 1 kΩ between every rail and GND before power-up (rail list `engineering/ELECTRICAL/power_distribution/power_rails.md`) | DMM |
| CP-4 | Power Board rails at nominal with no load | each X2..X35 output within the net-name voltage (currents UNKNOWN) | bench PSU + DMM |

![F15.1 — Conceptual exploded view of the electronics set used as the orientation reference for phases A–C; board outlines verified from the .brd files, arrangement conceptual (ASM-EXP-01) — CONCEPTUAL (source: engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png; produced by tools/gen_assembly_exploded_view.py)](engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png)

## 15.2 Phase A — PCB assemblies (repeat per board: Main, Power, Synth, 16 × RF PA)

### Step 15.1 — Inspect the bare boards [PROPOSED / SOURCE-DERIVED acceptance values]

- **Purpose:** confirm the fabricated board matches the verified outline and hole table before anything is mounted (CP-1).
- **Parts & tools:** bare PCBs; caliper; `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md`; fab certificate of conformance.
- **Action:** measure the outline bounding box and every mounting hole; compare with chapter 10 §10.1 (Main 260.00 × 300.00, 10 holes; Power 280.00 × 300.00, 8 holes; Synth 100.00 × 100.00, 4 holes; RF PA 35.00 × 60.00, 7 holes — all Ø3.20 NPTH).
- **Check:** dimensions within ±0.2 mm (vendor tolerance UNSPECIFIED); hole count exact; board thickness recorded (it is ASSUMED 1.6 mm everywhere in the design — G-01).
- **Figure:** F10.10a (plan view of the four outlines).
- **⚠ Decision:** G-10 — the Power Board's inner hole pattern "suggests a smaller board than 280 × 300"; if the delivered outline differs, the carrier rails #29/#30 (300 mm) and standoffs #31–#38 must be re-checked.

### Step 15.2 — Populate per BOM and pick-and-place [BETA BOM, SOURCE-DERIVED drawings]

- **Purpose:** assembled board matches the BOM and the placement data (CP-2).
- **Parts & tools:** `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv` (with MPN confidence column) and `beta/pcb/<BOARD>/exports/pos` placement files; reflow/hand assembly equipment; AOI or magnifier.
- **Action:** place every reference listed in the BOM at the position and rotation of the P&P file; orient polarised parts per the assembly drawing (F15.2–F15.5).
- **Check:** every reference populated; no reference left with an empty value (the original EAGLE BOMs have 0 MPN attributes — AC-B5 NOT MET, so the beta MPN proposals must be reviewed by the owner before purchase); polarity per the assembly drawing.
- **Figure:** F15.2–F15.5.
- **⚠ Decision:** K1 (FPGA part XC7A50T on the schematic vs XC7A100T in the FPGA README) — the Main Board U42 placement follows the schematic part; the Main Board rev. B (FT601 wired) is a separate BETA layout (`beta/pcb/MAIN_BOARD_REVB/`), not the baseline of this step.

![F15.2 — Main Board, top assembly drawing (component placement, references), page 1 of engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf; layout state PARTIAL (2 390 airwires in the EAGLE source) — SOURCE-DERIVED / PARTIAL (source: engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh (kicad-cli 10.0.6), rendered to PNG by `pdftoppm -png -r 110 -f 1 -l 1`)](manual/figures/MAIN_BOARD_assembly_top-1.png)

![F15.3 — Power Supply Board, top assembly drawing, page 1; layout state PARTIAL (309 airwires in the EAGLE source) — SOURCE-DERIVED / PARTIAL (source: engineering/PCB/POWER_SUPPLY/drawings/POWER_SUPPLY_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh, rendered by pdftoppm)](manual/figures/POWER_SUPPLY_assembly_top-1.png)

![F15.4 — Frequency Synthesizer Board, top assembly drawing, page 1 — SOURCE-DERIVED (source: engineering/PCB/FREQUENCY_SYNTHESIZER/drawings/FREQUENCY_SYNTHESIZER_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh, rendered by pdftoppm)](manual/figures/FREQUENCY_SYNTHESIZER_assembly_top-1.png)

![F15.5 — RF PA board, top assembly drawing, page 1 (one of 16 identical boards) — SOURCE-DERIVED (source: engineering/PCB/RF_PA/drawings/RF_PA_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh, rendered by pdftoppm)](manual/figures/RF_PA_assembly_top-1.png)

### Step 15.3 — Rail-to-ground resistance before power [SOURCE-DERIVED rail list]

- **Purpose:** detect solder shorts before any rail is energised (CP-3).
- **Parts & tools:** DMM; rail register `engineering/ELECTRICAL/power_distribution/power_rails.md` §1 (36 rows).
- **Action:** on every assembled board measure resistance between each rail net and GND at its connector (Power Board outputs X2…X35; Main Board inputs X1, X4…X24, X55, X56; Synth inputs X10…X15; PA `22V`, X2 `VG`).
- **Check:** > 1 kΩ on every rail (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` CP-3). Record the values.
- **Figure:** F3.2 (power distribution, chapter 3).
- **⚠ Decision:** none.

### Step 15.4 — Power Board alone on the bench supply [SOURCE-DERIVED, ⚠ design review item]

- **Purpose:** verify every regulator output with no load (CP-4) before the enable bus is ever driven.
- **Parts & tools:** bench PSU 12–17 V (VIN range from the board silkscreen `Vin [12-17]V`, source: `power_rails.md` §1 row `VIN`), DMM.
- **Action:** connect VIN/GND to X1 (AK300/2, KL1 VIN, KL2 GND — source: `interconnection_table.md` §1). Measure each output X2…X35 against its net-name nominal: always-on rails (+3V3 X16, +3V3_AN X12, +3V3_XO X35, +5V0_LO X6, +3V3_LO_1 X8, +3V3_LO_2 X7, +3V4 X23, −3V4 X24, +5V0_0 X22, +5V0_1…5 X2/X9/X17/X25/X28, +5V0_ADTR X26) are present with no enable; enabled rails stay at 0 V until the SV1 enable lines are driven (all EN nets are MCU outputs initialised LOW).
- **Check:** each present output within the net-name voltage (currents UNKNOWN — not documented anywhere, `power_rails.md` §4 item 5); the enabled rails read 0 V with SV1 open.
- **Figure:** F3.2.
- **⚠ Decision:** `+5V0_LO` LDO U30 (ADM7151) is fed directly from the 12–17 V bus — "CONFLICT / REQUIRES DESIGN REVIEW … check against the ADM7151 input-voltage rating" (source: `power_rails.md` §1 row `+5V0_LO`, §4 item 2). Do not exceed the LDO's rating until the owner resolves it.

## 15.3 Phase B — Mechanical assembly of the radar head

Part numbers (#) are those of `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (copied in chapter 10 §10.5). Station coordinates (Y, mm from the inner face of the front wall) are the values printed by `python3 tools/design_layout.py` (chapter 10 §10.3). The step source (`manual/ASSEMBLY_STEPS_SOURCE.md`, phase B) uses an older part numbering in some rows; the numbers below follow the parts list, and each divergence is noted.

![F15.6 — Assembly section with fastener balloons: balloon number = part # of the mechanical parts list; defines which fastener goes where in Steps 15.5–15.13, DSN-MECH-07 Rev A — PROPOSED DESIGN (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png; produced by tools/design_enclosure_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png)

![F15.7 — Sheet-metal flat patterns (tray, front plate, lid) that the fabricator folds before Step 15.5; bend lines and allowance per the generator formula, DSN-MECH-06 Rev A — PROPOSED DESIGN (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png; produced by tools/design_enclosure_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png)

### Step 15.5 — Fit PEM nuts, lid gasket and front gasket to the tray [PROPOSED DESIGN]

- **Purpose:** prepare the folded tray so that every later fastener has a nut and the IP54 sealing surfaces exist before parts block access.
- **Parts & tools:** tray #1 (2.5 mm Al 5754, 3 bends R2.5, 15 mm flanges); PEM nuts S-M4-1 ×18 (parts list #1 and fastener totals); lid gasket #7 (EPDM 3 mm self-adhesive, 15 mm wide, on the three top flanges); front-flange gasket: 1.5 mm EPDM strip on the two front flanges (parts list "Sealing and finish", no part number); PEM press tool.
- **Action:** press the 18 PEM nuts into the lid and front-plate flange holes (8 lid holes M4 + 10 front-plate holes M4, parts list #1 note); lay the lid gasket on the three top flanges and the front strip on the two front flanges, continuous around the corners.
- **Check:** gasket continuous, no gaps at corners; every flange hole has a nut; the Ø70 cable-entry hole and intake slots are free.
- **Figure:** F15.6, F15.7.
- **⚠ Decision:** the step source quotes "PEM S-M4 ×38" (source: `manual/ASSEMBLY_STEPS_SOURCE.md` B1) whereas the parts list and its fastener totals give S-M4-1 ×18; the parts list count is used here (observation MAN-15-1). Bend reliefs and corner welds of the tray are listed as open in the parts list.

### Step 15.6 — Mount the PA heat-spreader brackets and the plate [PROPOSED DESIGN]

- **Purpose:** fix the 300 × 300 × 10 mm plate (#8) vertically at the front of the tray so that its front face is at station Y = 11.0 mm (plate front) and its rear face at Y = 21.0 mm.
- **Parts & tools:** plate #8 (Al 6061, fin fields machined, M3 tapped 16×7 + 6); brackets #9, #10, #11, #12 (L 25×25×3 Al at x = 5/280, z = 20/265); per bracket M5×12 ×2 + M5×16 ×1 (totals M5×12 ×12 incl. the stepper, M5×16 ×4); square, 5 mm hex key.
- **Action:** bolt each bracket to the side wall and to the front flange (parts list note), then bolt the plate to the four brackets; set the plate front face at Y = 11.0 mm from the inner face of the front wall (source: `tools/design_layout.py`, `stations_y.plate_front`).
- **Check:** plate square to the base ±0.5 mm (source: step source B2); front face flush for the antenna spacers; the fin fields face the rear (towards the Main Board tier).
- **Figure:** F15.6, F10.1, F10.3.
- **⚠ Decision:** D-08/D-11 (chassis material and spreader concept); step source names "brackets #10" — the parts list has four brackets #9–#12.

### Step 15.7 — Mount the 16 PA boards on the rear of the plate [PROPOSED DESIGN]

- **Purpose:** put every QPA2962 on the plate through a thermal pad so that the conduction path of the thermal design (chapter 10 §10.7) exists.
- **Parts & tools:** 16 assembled RF PA boards (Step 15.2); thermal pads 5 × 5 mm, one under each QPA2962 (parts list #8 note); M3×6 ×112 (parts list #8: "PA 112"); torque screwdriver.
- **Action:** place the boards on the tapped field in the 4 × 4 grid of the layout (pitch x 40.0 mm, z 68.0 mm; field origin x 77.5, z 23.0; source: `tools/design_layout.py` `pa_grid`, `pa_field`) with the pad centred on the QPA2962; fasten with 7 × M3×6 per board through the Ø3.20 holes at (2.6, 2.6), (17.5, 2.6), (32.4, 2.6), (2.6, 38), (32.4, 38), (2.6, 57.4), (32.4, 57.4) (source: `engineering/MECHANICAL/dimensions/RF_PA_dimensions.md` §2); number the boards PA1…PA16 as drawn on DSN-MECH-04 tier 1.
- **Check:** torque 0.5 N·m (step source B3 — ASSUMED, no repository torque specification); pads centred; numbering PA1…PA16 matches F15.8 tier 1.
- **Figure:** F15.8 (tier 1), F15.5.
- **⚠ Decision:** the QPA2962 is assumed at the board centre in the thermal model ("verify in `engineering/PCB/RF_PA`", `DESIGN_CALCULATIONS.md` §1) — confirm the pad position on the real board before fastening.

### Step 15.8 — Mount the antenna panel on the plate front [PROPOSED DESIGN, D-01…D-06]

- **Purpose:** fix the proposed 16-row patch panel at station Y = 8.0 mm, 2.4 mm in front of the plate, with its row-1 connector at the bottom.
- **Parts & tools:** antenna PCB DSN-ANT-01 (165.0 × 248.0 × 0.6 mm, position x 72.5, z 31.0; source: `tools/design_layout.py` `antenna`); 6 × 2.4 mm nylon spacers (parts list #8 note; spacer material listed as open); M3×6 ×6 (parts list #8: "antenna 6").
- **Action:** stand the panel on the six spacers over the plate's six antenna tap holes; fasten; keep the 16 end-launch 2.92 mm connectors on the left edge accessible (D-05).
- **Check:** row 1 at the bottom; connectors accessible; gap to plate 2.4 mm; radome gap 8.0 mm remains in front (layout `antenna.radome_gap`).
- **Figure:** F10.2 (front elevation), F8.1 (chapter 8).
- **⚠ Decision:** D-01 (patch array vs slotted waveguide) is an owner decision; the panel is PROPOSED and only simulated (AC-E7 NOT RUN).

### Step 15.9 — Fit the Main Board tier (Y = 56.0 mm) [PROPOSED DESIGN, D-07, D-09]

- **Purpose:** carry the Main Board vertically, components to the rear, with its SMA field reachable for the Synth coax (D-09).
- **Parts & tools:** carrier rails #13 (bottom) and #14 (top), U15×12×1.5 Al, 280 mm, M4×8 ×2 each to the side walls; standoffs #15–#22 (M3×10 hex) at the eight Ø3.20 holes (4, 4), (256, 4), (116, 114), (256, 114), (116, 250), (256, 250), (4, 296), (256, 296) (source: `MAIN_BOARD_dimensions.md` §2) with M3×6 ×1 each; assembled Main Board (Step 15.2).
- **Action:** bolt the rails to the side walls at station Y = 56.0 mm (`stations_y.main`); screw the eight standoffs into the rails; mount the board at (x 25.0, z 5.0) (`main_pos`) component side to the rear.
- **Check:** connector field positions match DSN-MECH-04 tier 2 (J1, J18…J55 on the rear face; X_n Molex, JP and SV1 reachable); board does not touch the PA boards (component heights ASSUMED 15 mm top / 4 mm bottom — G-02).
- **Figure:** F15.8 (tier 2), F15.2.
- **⚠ Decision:** D-07 — the 25 mm tier pitch is an assumption until component heights are measured (G-02).

### Step 15.10 — Fit the Synth tier (Y = 81.0 mm) and the Power tier (Y = 106.0 mm) [PROPOSED DESIGN]

- **Purpose:** complete the board stack behind the Main Board.
- **Parts & tools:** Synth rails #23/#24 (120 mm, M4×8 ×2 each), standoffs #25–#28 at (5, 5), (95, 5), (5, 95), (95, 95) (source: `FREQUENCY_SYNTHESIZER_dimensions.md` §2), M3×6 ×4; Power rails #29/#30 (300 mm, M4×8 ×2 each), standoffs #31–#38 at (10, 10), (140, 10), (270, 10), (10, 120), (270, 120), (10, 230), (270, 230), (138, 268) (source: `POWER_SUPPLY_dimensions.md` §2, rounded as in the parts list), M3×6 ×8; assembled boards.
- **Action:** mount as in Step 15.9: Synth at station Y = 81.0 (`stations_y.synth`), position (x 46.36, z 141.60) — "centred on Main Board J1,J18,J20,J21,J22,J23 (P&P)" (`synth_pos.basis`); Power Board at Y = 106.0 (`stations_y.power`), position (x 15.0, z 5.0).
- **Check:** Synth J-ports face the Main Board SMA field (shortest coax, D-09); Power Board X1 input and X2…X35 outputs reachable from the rear; rear inner wall at Y = 127.6 leaves clearance for the Power Board components (ASSUMED heights).
- **Figure:** F15.8 (tiers 3–4), F15.3, F15.4.
- **⚠ Decision:** G-10 (Power Board outline), G-02 (heights).

### Step 15.11 — Mount the 22 V PA supply / gate module on the rear wall [PROPOSED DESIGN — module not built]

- **Purpose:** provide the 22 V drain source, the high-side switch driven by `EN/DIS_RFPA_VDD` and the per-PA pulse-gating FETs (D-14).
- **Parts & tools:** DSN-PSU-01 module (block schematic, BOM and netlist only: `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/`; component-level capture is recovery item MDR-12); fasteners not defined.
- **Action:** fix the module to the rear wall between the Power Board tier and the rear inner wall (DSN-MECH-01 shows the location); route its 16 outputs OUT1…OUT16 towards the PA field (cables CBL-050, -056, -062, -068, -074, -080, -086, -092, -098, -104, -110, -116, -122, -128, -134, -140 in Step 15.17).
- **Check:** none possible — the module does not exist.
- **Figure:** F10.1, F9.1 (chapter 9).
- **⚠ Decision:** ⚠ D-14 — module not built; the `TX_GATE` FPGA/MCU pin is undecided; ⚠ K4 — no 22 V rail in any CAD file.

### Step 15.12 — Fit the fans and the gland plate [PROPOSED DESIGN — fans not in the parts list]

- **Purpose:** establish the bottom-to-top forced airflow of the cooling concept (D-11) and seal the cable entry.
- **Parts & tools:** 2 × 60 mm fans (step source B8; **no fan part, bracket or airflow figure exists in the parts list** — "fan mounting brackets" is an open item there); gland plate #39 (100 × 100 × 2 Al) with M4×8 ×4 and IP68 glands M32 (power) + M20 (USB).
- **Action:** fit the fans at the duct intakes shown on DSN-MECH-01/03; bolt the gland plate under the base over the Ø70 entry hole.
- **Check:** airflow direction bottom → top (intake louvres in the front plate, exhaust slots in the lid — parts list #2, #6); glands tightened on the harness only after Step 15.18.
- **Figure:** F10.1, F10.3.
- **⚠ Decision:** G-08 — fan selection and airflow are not designed; the thermal map assumes an effective h over the fin strips (chapter 10 §10.7).

### Step 15.13 — Fit the front plate, PTFE window, gasket and clamp frame [PROPOSED DESIGN]

- **Purpose:** close the front with the radome window in front of the antenna (radome gap 8.0 mm).
- **Parts & tools:** front plate #2 (window opening 175 × 258, intake louvres, 16 M3 clamp holes) with M4×8 ×10 to the tray front flanges (into the PEM nuts of Step 15.5); window #3 (PTFE 2 mm, outside the front plate); window gasket #4 (EPDM 1.5 mm, 10 mm ring); clamp frame #5 (2 mm Al, 14 mm wide) with M3×10 ×16 + nyloc.
- **Action:** bolt the front plate; lay the gasket, the window and the frame outside the plate; fasten the 16 M3×10 with nyloc nuts evenly in a cross pattern.
- **Check:** window flat; gasket compressed evenly; louvres unobstructed.
- **Figure:** F15.6, F10.2.
- **⚠ Decision:** observation MAN-10-1 (16 vs 18 clamp screws in the parts-list text); step source B9 numbers the parts "#2, #5, #6, #7" (older numbering) — the parts-list numbers #2, #3, #4, #5 apply. PTFE loss "≈ 0.1 dB at 10.5 GHz … to be confirmed" (parts list #3).

The lid (#6, M4×8 ×8, gasket #7) stays off until the bring-up of chapter 16 is complete (Step 16.10 closes it).

## 15.4 Phase C — Harness

Lengths are PROPOSED: "Manhattan distance between connector positions in the head + service allowance (40 mm coax / 60 mm wire), rounded up to 10 mm … cut after a first fit" (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, header). Totals: 144 cables; coax 55; wire 89; ≈ 41.6 m. ⚠ The pin order of every Molex 22-23-20x1 connector is UNVERIFIED because the EAGLE symbols name all pads `S` (source: `interconnection_table.md`, header) — buzz out before mating.

![F15.8 — Internal layout per tier, rear view, with every connector reference (J, X, JP, SV) at its P&P position — the routing reference for Steps 15.14–15.18, DSN-MECH-04 Rev A — PROPOSED DESIGN; connector positions SOURCE-DERIVED (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-04_internal_layout_rear.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-04_internal_layout_rear.png)

Harness schedule excerpt — the cables named in this phase (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, rows copied; the full 144-row table is reproduced in Appendix B):

| ID | From | To | Signal | Cable | Length (mm) | Note |
|---|---|---|---|---|---|---|
| CBL-035 | POWER_SUPPLY SV1 | MAIN_BOARD SV1 | enable bus (15 EN + GND) | 20-way 1.27 mm IDC ribbon | 320 |  |
| CBL-002 | POWER_SUPPLY X3 | MAIN_BOARD X55 | +5V5_PA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 780 | rail name matched in both netlists |
| CBL-003 | POWER_SUPPLY X4 | MAIN_BOARD X8 | +1V0_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 310 | rail name matched in both netlists |
| CBL-009 | POWER_SUPPLY X10 | MAIN_BOARD X17 | +1V8_CLOCK | 2-wire 20 AWG, Molex 22-01-2027 both ends | 840 | rail name matched in both netlists |
| CBL-001 | POWER_SUPPLY X2 | ? ? | +5V0_1 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-036 | FREQUENCY_SYNTHESIZER J7 | MAIN_BOARD J1 | 100 MHz FPGA sys clk | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-037 | FREQUENCY_SYNTHESIZER J5 | MAIN_BOARD J20 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 170 | mapping from interconnection_table.md §6 |
| CBL-038 | FREQUENCY_SYNTHESIZER J6 | MAIN_BOARD J18 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-039 | FREQUENCY_SYNTHESIZER J3 | MAIN_BOARD J21 | 400 MHz ADC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-040 | FREQUENCY_SYNTHESIZER J10 | MAIN_BOARD J23 | LO TX | coax RG-405 (0.086") SMA-SMA, phase-stable | 100 | mapping from interconnection_table.md §6 |
| CBL-041 | FREQUENCY_SYNTHESIZER J11 | MAIN_BOARD J22 | LO RX | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-043 | FREQUENCY_SYNTHESIZER JP1 | MAIN_BOARD JP1 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 210 |  |
| CBL-044 | FREQUENCY_SYNTHESIZER JP2 | MAIN_BOARD JP13 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 240 |  |
| CBL-045 | MAIN_BOARD X_7 | RF_PA PA1 X2 | VG_1 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 150 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-046 | MAIN_BOARD X3 | RF_PA PA1 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 150 | Main sense connector ↔ PA n PROPOSED |
| CBL-047 | MAIN_BOARD J27 | RF_PA PA1 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 330 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-048 | MAIN_BOARD J26 | RF_PA PA1 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-049 | RF_PA PA1 J2 | ANTENNA ROW1 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 100 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-050 | DSN-PSU-01 OUT1 | RF_PA PA1 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 510 |  |
| CBL-141 | SLIP RING VIN | POWER_SUPPLY X1 | VIN 12-17 V | 2 × 2-wire 16 AWG | 340 |  |
| CBL-142 | SLIP RING VIN | DSN-PSU-01 IN | VIN to 22 V boost | 2 × 2-wire 16 AWG | 470 |  |
| CBL-143 | SLIP RING USB | MAIN_BOARD X53 | USB 2.0 FS to host | USB 2.0 shielded, mini-B | 360 |  |
| CBL-144 | MAIN_BOARD stepper pins | PEDESTAL TB6600 (via slip ring) | STEP/DIR/EN | 3-wire 24 AWG shielded | TBD | the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head (then only motor phases cross: 4 circuits) — DECISION NEEDED |

### Step 15.14 — Enable bus SV1 ↔ SV1 [SOURCE-DERIVED pinout, PROPOSED cable]

- **Purpose:** connect the 15 enable lines from the STM32 to the Power Board regulators.
- **Parts & tools:** CBL-035, 20-way 1.27 mm IDC ribbon, 320 mm; two MA10-2 IDC connectors.
- **Action:** mate Main SV1 to Power SV1 pin-for-pin (pin map: 1 `EN_+1V0_FPGA` PE7 → U1, 2 `EN_+5V0_PA2` PG1 → U15, 3 `EN_+1V8_FPGA` PE8 → U2, 4 `EN_+5V0_PA3` PG2 → U16, 5 `EN_+3V3_FPGA` PE9 → U4, 6 `EN_+5V5_PA` PG3 → U17, 7 `EN_+5V0_ADAR` PE10 → U13, 8 `EN_+1V8_CLOCK` PG4 → U25, 9 `EN_+3V3_ADAR12` PE11 → U6, 10 `EN_+3V3_CLOCK` PG5 → U23, 11 `EN_+3V3_ADAR34` PE12 → U7, 13 `EN_+3V3_ADTR` PE13 → U32, 15 `EN_+3V3_SW` PE14 → U10, 17 `EN_+3V3_VDD_SW` PE15 → U8, 19 `EN_+5V0_PA1` PG0 → U14; 12/14/16/18/20 GND — source: `power_rails.md` §2).
- **Check:** pin-1 orientation identical at both ends; continuity on all 20 positions.
- **Figure:** F15.8 (SV1 positions on tiers 2 and 4).
- **⚠ Decision:** none (the Power Board has no visible pull-downs on the EN nets — "REQUIRES VERIFICATION", `power_rails.md` §2).

### Step 15.15 — Rail cables Power → Main / Synth [SOURCE-DERIVED mapping, ⚠ pin order UNVERIFIED]

- **Purpose:** bring every supply rail to its consumer board.
- **Parts & tools:** the 2-wire 20 AWG Molex 22-01-2027 cables CBL-002…034 whose rail name "matched in both netlists" (X3→X55, X4→X8, X5→X10, X6→Synth X15, X10→X17, X12→X56, X16→X24, X18→X6, X19→X19, X20→X15, X21→X13, X22→X18, X23→X1, X24→X11, X27→X16, X30→X12, X31→X14, X32→X5, X33→X7, X34→X4, X35→Synth X4 — source: `HARNESS_SCHEDULE.md` rows CBL-002…034), crimp tool, DMM.
- **Action:** buzz out the polarity of each Molex pad pair on both boards against the netlist before crimping (pads are named `S`); crimp and mate.
- **Check:** continuity and polarity per `power_rails.md` §1 (consumer connector column).
- **Figure:** F3.2, F15.8.
- **⚠ Decision:** (a) rails whose destination connector could not be matched by net name — CBL-001, -006, -007, -008, -010, -012, -013, -014, -016, -024, -025, -027, -028 (TBD rows of the harness schedule; interconnection table §2/§4 resolves most of them: e.g. +3V3_ADAR_12 X14 → Main X20 `+3V3_ADAR12`, +3V3_ADAR_34 X15 → Main X21, +3V3_CLOCK X11 → Synth X11, +3V3_LO_1 X8 → Synth X13, +3V3_LO_2 X7 → Synth X14; `+5V0_1…5`, `+5V0_ADAR` X13, `+5V0_ADTR` X26, `+3V3_SW` X29 have **no consumer** and stay unconnected — `power_rails.md` §4 item 4); (b) `+1V8_CLOCK` X10 must feed both Main X17 and Synth X12 — "add a second output or document a Y-cable" (`power_rails.md` §4 item 3).

### Step 15.16 — Synth ↔ Main control headers and coax clocks/LO [SOURCE-DERIVED mapping]

- **Purpose:** deliver the 100 / 120 / 400 MHz clocks and the TX/RX LO to the Main Board and connect the SPI4/control lines.
- **Parts & tools:** CBL-043 (JP1 ↔ JP1, 210 mm), CBL-044 (JP2 ↔ JP13, 240 mm); coax set CBL-036…041 (J7→J1 100 MHz FPGA, J5→J20 and J6→J18 120 MHz DAC, J3→J21 400 MHz ADC, J10→J23 LO TX, J11→J22 LO RX; RG-405 phase-stable, 100–170 mm) and CBL-042 (J4→J19 test, 100 mm); SMA torque wrench.
- **Action:** connect the headers; form and connect the coax; label each cable with its CBL-ID.
- **Check:** SMA torque 0.9 N·m (step source C3 — ASSUMED, no repository torque specification); labels present; no coax below its minimum bend radius.
- **Figure:** F15.8 (tiers 2–3).
- **⚠ Decision:** none beyond the clock-frequency intent being firmware-derived (`main.cpp:933-1072`), to be verified in Step 16.4.

### Step 15.17 — PA harness: VG, sense, RF pairs, antenna coax, 22 V leads [PROPOSED mapping, ⚠ several UNVERIFIED]

- **Purpose:** connect all 16 PA boards to the Main Board, the antenna rows and the 22 V module.
- **Parts & tools:** per PA n: VG cable (Main X_k → PA n X2, 24 AWG shielded, Molex 22-01-2027), sense cable (Main X3/X38…X52 → PA X3, 3-wire 24 AWG twisted, Molex 22-01-3037), RF pair (Main J-pair → PA J1/J2, RG-405 EQUAL LENGTH set), antenna coax (PA J2 → antenna row n, RG-405 SMA–2.92 mm, EQUAL LENGTH set), 22 V lead (DSN-PSU-01 OUTn → PA `22V` AK300/2, 2-wire 18 AWG twisted) — rows CBL-045…140 of the harness schedule. VG_n ↔ Main connector map from the schematic: X_7=VG_1, X_16=VG_2, X_8=VG_3, X_15=VG_4, X_4=VG_5, X_11=VG_6, X_3=VG_7, X_12=VG_8, X_5=VG_9, X_14=VG_10, X_6=VG_11, X_13=VG_12, X_2=VG_13, X_9=VG_14, X_1=VG_15, X_10=VG_16 (source: `interconnection_table.md` §7). RF pairs per n: J27/J26 (1), J29/J28 (2), J25/J24 (3), J31/J30 (4), J35/J34 (5), J37/J36 (6), J33/J32 (7), J39/J38 (8), J47/J46 (9), J41/J40 (10), J45/J44 (11), J43/J42 (12), J55/J54 (13), J49/J48 (14), J53/J52 (15), J51/J50 (16) (same source).
- **Action:** cable PA n to VG_n, sense connector n, RF pair n and antenna row n exactly as labelled; cut the 16 antenna coax and the 16 RF pairs as equal-length sets; connect the 22 V leads **last** and only with VG wiring complete (S1).
- **Check:** equal length within ±2 mm on the 16 antenna coax (step source C4 — ASSUMED tolerance; the harness schedule only states "equal length mandatory for elevation phase"); labels PA1…PA16; 22 V polarity (KL1 `VD`, KL2 `GND`, `interconnection_table.md` §7); screw-terminal torque of the AK300/2 per its datasheet (not in the repository).
- **Figure:** F15.8 (tier 1 PA numbering, tier 2 SMA field), F15.5.
- **⚠ Decision:** which SMA of each Main Board pair is RFIN vs RFOUT is UNVERIFIED — "determine from the Main Board switch RF_SW_n routing before cabling" (`ASSEMBLY_SEQUENCE.md` §B.7); PA-instance ↔ VG_n / sense-connector mapping is PROPOSED (n = n), not documented in CAD; ⚠ K4 / D-14 for the 22 V leads.

### Step 15.18 — Slip-ring harness through the base gland [PROPOSED DESIGN, D-13]

- **Purpose:** bring VIN, 22 V-boost input and USB from the pedestal into the rotating head.
- **Parts & tools:** CBL-141 (slip ring VIN → Power X1, 2 × 2-wire 16 AWG, 340 mm), CBL-142 (slip ring VIN → DSN-PSU-01 IN, 470 mm), CBL-143 (slip ring USB → Main X53 mini-B, 360 mm); gland plate #39 glands M32 (power) and M20 (USB).
- **Action:** route the three cables through the Ø70 base hole and the glands; tighten the glands.
- **Check:** continuity after a full 360° rotation of the turntable (Step 15.22); no cable strain.
- **Figure:** F10.3, F10.5.
- **⚠ Decision:** CBL-144 (STEP/DIR/EN to the TB6600) — "the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head … DECISION NEEDED" (harness schedule); D-13 channel count (12) assumes USB stays the host link.

## 15.5 Phase D — Pedestal

### Step 15.19 — Slewing bearing, turntable and ring pulley [PROPOSED DESIGN]

- **Purpose:** build the rotating joint.
- **Parts & tools:** pedestal top plate #43 (360 × 360 × 5 Al, bore Ø90) with M6×20 ×12 to the bearing inner ring; slewing bearing #41 (OD 190 / ID 100 × 20, "part number to be selected (axial ≥ 50 kg, moment ≥ 60 N·m)"); turntable #40 (Ø340 × 8 Al) with M6×25 ×12 to the bearing outer ring; ring pulley #42 (GT3 180 T Ø172) with M4×10 ×6 clamped under the turntable; pedestal housing #44 with M5×10 ×12 to the top plate.
- **Action:** bolt the bearing inner ring to the top plate (12 × M6×20), the turntable to the outer ring (12 × M6×25), the ring pulley under the turntable (6 × M4×10); fit the top plate on the housing (12 × M5×10).
- **Check:** turntable runs freely; axial play < 0.1 mm (step source D1 — ASSUMED acceptance value).
- **Figure:** F10.5, F10.3.
- **⚠ Decision:** bearing part number not selected (parts list #41 note).

### Step 15.20 — Stepper, bracket, pulley, belt and driver [PROPOSED DESIGN, ⚠ D-12 revised]

- **Purpose:** install the azimuth drive.
- **Parts & tools:** stepper #45 (NEMA 23, 76 mm, M5×12 ×4); motor bracket #46 (80 × 80 × 3 Al, slots ±5 mm, M5×10 ×4 to the top plate); motor pulley #47 (GT3 60 T Ø57, bore 6.35, grub M4 ×2); belt GT3 9 mm (ratio 3, `design_layout.py` `pedestal`); driver #50 (TB6600 on DIN rail).
- **Action:** bolt the bracket, mount the motor and pulley, fit the belt and tension it with the bracket slots; mount the driver; set the driver current limit before any motion (S3).
- **Check:** belt deflection within the belt maker's figure (not in the repository); driver current limit set and recorded.
- **Figure:** F10.5.
- **⚠ Decision:** ⚠ D-12 — DSN-CALC-01 §2 shows a NEMA 23 needs ≥ 200 ms per 7.2° step (≈ 19 s per revolution) for the ≈ 10 kg head; a NEMA 34 (3 N·m class) allows ≈ 100 ms; alternatives 1:6 ratio (`Stepper_steps = 1200`) or a lighter head. The firmware constant must match the ratio (`Stepper_steps = 600` for 1:3, `main.cpp:195`). Choose motor class and ratio **before** this step.

### Step 15.21 — Slip ring, stator bracket, mast flange [PROPOSED DESIGN, ⚠ mast interface undefined]

- **Purpose:** fix the slip-ring stator to the pedestal with its rotor turning with the turntable; prepare the mast interface.
- **Parts & tools:** slip ring #48 (through-bore Ø99 × 60, bore 60, 12 circuits, "e.g. Senring H3899 class — select"); stator bracket #49 (140 × 140 × 3 Al, M4×8 ×4); mast flange #51 (Ø150 × 10 steel, 4 × M10 PCD 110, M10×30 ×4 — "ASSUMPTION — mast interface undefined").
- **Action:** mount the stator bracket under the top plate, the slip ring in the bore, the rotor flange to the turntable; route the harness of Step 15.18 through the bore; bolt the mast flange under the housing.
- **Check:** rotor turns with the turntable without cable strain over 360°.
- **Figure:** F10.5, F10.3.
- **⚠ Decision:** slip-ring part not selected; mast flange is an ASSUMPTION (parts list #51; `design_layout.py` `mast_flange`); D-13 channel count.

### Step 15.22 — Bolt the head to the turntable [PROPOSED DESIGN]

- **Purpose:** join the head and the pedestal with the cable passage aligned.
- **Parts & tools:** M6×16 ×8 (parts list #40: "8×M6 to the head base"); head assembly of phase B; harness of Step 15.18 already through the Ø70 base hole.
- **Action:** align the Ø70 base passage with the slip-ring bore and bolt the tray base to the turntable with the 8 × M6×16.
- **Check:** head square to the turntable (no tolerance in the source); harness continuity after a 360° rotation (Step 15.18 check); lid still open for chapter 16.
- **Figure:** F10.3, F10.8a.
- **⚠ Decision:** lifting points and earthing stud are open items (parts list "Open").

## 15.6 Hand-over to bring-up

Phases A–D leave the head open (lid #6 off), the pedestal stationary, the 22 V leads connected only if the DSN-PSU-01 module exists, and every cable labelled with its CBL-ID. Chapter 16 continues with Step 16.1 (firmware flash). Evidence to collect during the first build (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §D): rail voltages (CP-4), photos of the first harness with cable labels, the measured component heights (closes G-02), the measured board thickness (G-01) and the real cut lengths of all 144 cables (replaces the PROPOSED lengths) — store under `engineering/VALIDATION/`.
