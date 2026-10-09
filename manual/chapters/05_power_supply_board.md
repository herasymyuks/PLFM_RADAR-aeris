# 5. Power Supply Board (PowerBoard)

**Chapter status summary:** schematic — SOURCE-DERIVED (EAGLE 9.6.2 schematic rendered); connector inventory — SOURCE-DERIVED; layout — PARTIAL in the source (309 airwires, 132 of 312 parts parked outside the outline, sch/brd version mismatch) and BETA in `beta/pcb/POWER_SUPPLY/` (308 → 89 unconnected, placement by script not reviewed); layer plots and renders — SOURCE-DERIVED / BETA; stack-up — PARTIAL (2-layer, 1.5 mm core from the DRU) with a PROPOSED fabrication note; BOM — PARTIAL (0 MPN in the source). The 22 V PA drain supply does not exist on this board (K4) — see chapter 9. Nothing is hardware-verified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/POWER_SUPPLY.md`; `engineering/ELECTRICAL/connection_diagrams/POWER_SUPPLY_connection_report.md` §1–2; `engineering/ELECTRICAL/schematics/POWER_SUPPLY/`; `engineering/PCB/POWER_SUPPLY/README.md`, `STACKUP.md`; `beta/pcb/POWER_SUPPLY/README.md`, `UNROUTED.md`, `FAB_NOTES.md`, `BOM_POWER_SUPPLY_beta.csv`; `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` (G-10).

## 5.1 Role and key parts

The Power Board converts the single DC input `Vin [12-17] V` (silkscreen label; source: `docs/PCB/POWER_SUPPLY.md` §1) into the 24 rails consumed by the Main Board and the Frequency Synthesizer, each rail leaving the board on its own 2-pin Molex KK connector, and receives the 15-line enable bus from the STM32 on the 20-way header SV1. Board: **280 × 300 mm, 2 copper layers**, EAGLE schematic 9.6.2 / board 7.4.0 (version mismatch), 312 physical parts, 156 nets, 346 vias, DRU `PCBWay_2L_100um-Track` with a 1.5 mm core (source: `docs/PCB/POWER_SUPPLY.md` §1).

Key ICs (deviceset names, MPN UNVERIFIED; source: `docs/PCB/POWER_SUPPLY.md` §1):

| Function | Part | Qty | Note |
|---|---|---|---|
| Buck regulators | TPS562208DDCT | 21 | datasheet folder contains TPS562201 instead — datasheet to be added |
| LDO | ADM7151ACPZ-04-R7 | 6 | |
| LDO | TPS7A8300RGRR | 2 | feedback-select pins without net (24 unconnected pins, see §5.3) |
| Inverters | LM2662MX/NOPB | 5 | datasheet folder has LM2663 |
| Tantalum capacitors | T521W476M020ATE045 | 10 | |
| Rail outputs | Molex 22-23-2021 | 34 | |
| DC input | AK300/2 (X1) | 1 | `VIN`, `GND` |
| Not on the board | MAX20029 | — | datasheet present, part absent |

Rails present as silkscreen labels (layer 51; source: `docs/PCB/POWER_SUPPLY.md` §1): `+5V5_PA, -5V5_PA, +1V8_CLOCK, +3V3_CLOCK, +3V3_VDD_SW, +5V0_PA_1/2/3, -3V3_SW, +3V3_SW, +3V3_ADTR, -5V0_ADAR12, -5V0_ADAR34, +3V4, -3V4, +3V3_LO, +5V0_ADAR, +3V3_ADAR_12, +3V3_ADAR_34, +5V0_0, +1V8_FPGA, +1V0_FPGA, +3V3, +3V3_FPGA, +3V3_AN`, 12 × `EN`. The 16 `EN_*` nets match the STM32 enable GPIOs PE7…PE15, PG0…PG5 (same source). The design input for rail currents is `3_Power Management/Power Management V6.xlsx` (sheet `Feuil1`); it budgets 16 × QPA2962 at +22 V / 2 A, a rail this board does not have — K4 (source: `docs/PCB/POWER_SUPPLY.md` §2; `docs/SYSTEM/BLOCK_DIAGRAM.md`).

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/POWER_SUPPLY_connection_report.md` §1):

| Item | Count |
|---|---|
| Sheets | 1 |
| Parts (all) / physical | 562 / 312 |
| Nets | 156 |
| Pin connections | 1061 |
| Single-pin nets | 0 |
| Unconnected pins on placed gates | 24 |
| Physical parts without value | 80 |
| Board airwires (unrouted connections, layer 19) | 309 |
| Missing symbol/footprint records | 0 |

## 5.2 Connectors

36 connector parts (source: `engineering/ELECTRICAL/connection_diagrams/POWER_SUPPLY_connection_report.md` §2; every Molex output carries the named rail on one pad and `GND` on the other, pad order UNVERIFIED):

| Refdes | Package | Rail / signal |
|---|---|---|
| X1 | AK300/2 | `VIN` (12–17 V input) |
| SV1 | MA10-2 (20-way) | `EN_+1V0_FPGA, EN_+5V0_PA2, EN_+1V8_FPGA, EN_+5V0_PA3, EN_+3V3_FPGA, EN_+5V5_PA, EN_+5V0_ADAR, EN_+1V8_CLOCK, EN_+3V3_ADAR12, EN_+3V3_CLOCK, EN_+3V3_ADAR34, EN_+3V3_ADTR, EN_+3V3_SW, EN_+3V3_VDD_SW, EN_+5V0_PA1` (15 enables + GND) |
| X2 | 22-23-2021 | `+5V0_1` |
| X3 | 22-23-2021 | `+5V5_PA` |
| X4 | 22-23-2021 | `+1V0_FPGA` |
| X5 | 22-23-2021 | `+1V8_FPGA` |
| X6 | 22-23-2021 | `+5V0_LO` |
| X7 | 22-23-2021 | `+3V3_LO_2` |
| X8 | 22-23-2021 | `+3V3_LO_1` |
| X9 | 22-23-2021 | `+5V0_2` |
| X10 | 22-23-2021 | `+1V8_CLOCK` |
| X11 | 22-23-2021 | `+3V3_CLOCK` |
| X12 | 22-23-2021 | `+3V3_AN` |
| X13 | 22-23-2021 | `+5V0_ADAR` |
| X14 | 22-23-2021 | `+3V3_ADAR_12` |
| X15 | 22-23-2021 | `+3V3_ADAR_34` |
| X16 | 22-23-2021 | `+3V3` |
| X17 | 22-23-2021 | `+5V0_3` |
| X18 | 22-23-2021 | `-3V3_SW` |
| X19 | 22-23-2021 | `-5V5_PA` |
| X20 | 22-23-2021 | `-5V0_ADAR34` |
| X21 | 22-23-2021 | `-5V0_ADAR12` |
| X22 | 22-23-2021 | `+5V0_0` |
| X23 | 22-23-2021 | `+3V4` |
| X24 | 22-23-2021 | `-3V4` |
| X25 | 22-23-2021 | `+5V0_4` |
| X26 | 22-23-2021 | `+5V0_ADTR` |
| X27 | 22-23-2021 | `+3V3_FPGA` |
| X28 | 22-23-2021 | `+5V0_5` |
| X29 | 22-23-2021 | `+3V3_SW` |
| X30 | 22-23-2021 | `+3V3_VDD_SW` |
| X31 | 22-23-2021 | `+5V0_PA_1` |
| X32 | 22-23-2021 | `+5V0_PA_2` |
| X33 | 22-23-2021 | `+5V0_PA_3` |
| X34 | 22-23-2021 | `+3V3_ADTR` |
| X35 | 22-23-2021 | `+3V3_XO` |

Which output feeds which Main Board / Synthesizer input is the subject of `engineering/SYSTEM/interfaces/interconnection_table.md` §2–§4 (chapter 3). Thirteen outputs (`+5V0_1…+5V0_5`, `+3V3_LO_1/2`, `+3V3_CLOCK`, `+5V0_ADAR`, `+3V3_ADAR_12/34`, `+5V0_ADTR`, `+3V3_SW`) have no connector with the same net name on the Main or Synth board and are marked TBD in the harness schedule (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, CBL-001…CBL-028 rows with "no connector with this net name"); some are matched by meaning in the interconnection table (e.g. `+3V3_ADAR_12` → Main `+3V3_ADAR12`, CBL-07 there).

## 5.3 Schematic sheet

![F5.1 — Power Board schematic, single sheet: 21 × TPS562208 buck stages, 6 × ADM7151 and 2 × TPS7A8300 LDOs, 5 × LM2662 inverters, 34 rail outputs, enable header SV1 (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/POWER_SUPPLY/png/POWER_SUPPLY_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/POWER_SUPPLY/png/POWER_SUPPLY_schematic_sheet1.png)

Schematic-level items that no layout work closes: 24 pins without net (TPS7A8300 feedback-select pins, LM2662 FC/OSC — source: `beta/pcb/POWER_SUPPLY/README.md` §3, detail in `engineering/ELECTRICAL/netlists/POWER_SUPPLY_unresolved_connections.md`); 80 references without value — the buck-stage inductors and capacitors must carry values for the TPS562208 compensation to be reproducible (source: `docs/PCB/POWER_SUPPLY.md` §8); one board-only signal `+3V3_LO` (sch/brd mismatch, source: `docs/PCB/POWER_SUPPLY.md` §2).

## 5.4 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 7.4.0 board, 9.6.2 schematic)

| Item | Finding (source: `docs/PCB/POWER_SUPPLY.md` §2) |
|---|---|
| Routing | 309 airwires across 86 of 157 signals; 72 signals entirely unrouted (all 16 `EN_*`, several `+5V0_*`, `+3V3_XO`, `+3V3_LO_1/2`) |
| Placement | 132 of 312 elements outside the 280 × 300 mm outline; mounting holes lie within 10..270 × 10..230 (+ one at y = 267.85) → the intended final outline is UNRESOLVED (G-10) |
| Version mismatch | sch 9.6.2 vs brd 7.4.0 — annotation link cannot be trusted; one board-only signal `+3V3_LO` |
| DRC | 0 approved errors (meaningless while unrouted) |
| ERC | 0 approved entries; 0 single-pin nets |
| Design-input discrepancies | xlsx budgets 16 × QPA2962 at +22 V (2 A each); the Power Board has no 22 V rail label (`Vin [12-17]V`) and the RF PA board holds one QPA2962 — PA supply architecture UNRESOLVED |

### Engineering conversion (`engineering/PCB/POWER_SUPPLY/`)

Cross-check (source: `engineering/PCB/POWER_SUPPLY/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 280.0 | 280.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 320 | 320 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 346 | 346 | OK |  |
| Tracks (signal wires excl. airwires) | 570 | 570 | OK |  |
| Copper layers | 2 | 2 | OK |  |
| NPTH holes (free holes + package holes) | 8 | 8 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 444 | 444 | OK |  |

DRC on the conversion: 160 violations, 308 unconnected (source: `engineering/PCB/POWER_SUPPLY/README.md` §6):

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

### BETA board (`beta/pcb/POWER_SUPPLY/`)

Before/after (source: `beta/pcb/POWER_SUPPLY/README.md` §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 308 | 89 |
| clearance | 53 | 56 |
| drill_out_of_range | 8 | 8 |
| isolated_copper | 4 | 0 |
| silk_over_copper | 40 | 168 |
| silk_overlap | 22 | 65 |
| solder_mask_bridge | 8 | 8 |
| track_dangling | 4 | 2 |
| via_dangling | 0 | 20 |
| zones_intersect | 21 | 1 |
| **DRC violations total** | 160 | 328 |

Unconnected items 308 → 89 (−71 %); footprints outside the outline 132 → 0. What was done, in order (source: `beta/pcb/POWER_SUPPLY/README.md` §2): netclass `Default` set to track 0.25 mm / clearance 0.2 mm / via 0.5/0.3 mm for new copper only; 110 parts placed inside the outline in 29 net clusters and 22 KK connectors placed on the nearest board edge (`tools/beta_place_outside.py`, `placement_moves*.json`); Freerouting 2.5.0 pass 1 with the existing 916 tracks/vias fixed (+1 336 tracks, +168 vias; 308 → 102); 45 same-net zones re-prioritised and a board-wide B.Cu GND zone added (zones_intersect 21 → 1); 29 straight same-net bridges kept out of 102 tried (102 → 96); Freerouting pass 2 (+36 tracks, +3 vias; 96 → 96); GND stitching, 22 of 50 vias kept (96 → 89); refill, DRC, export.

**The placement by script is topological, not thermal/EMC** — regulator clusters sit where free space was nearest to their connectors; a designer must review inductor orientation, input/output capacitor proximity and heat spreading before any routing clean-up (source: `beta/pcb/POWER_SUPPLY/README.md` §3).

### The 89 open connections (`beta/pcb/POWER_SUPPLY/UNROUTED.md`)

None of the 89 could be completed without a routing decision that a script should not take (crossing other copper, moving existing tracks, re-shaping the EAGLE pours); the netlist was never changed (source: `UNROUTED.md` header). By net: **GND 49, VIN 10**, `+5V0_ADAR` 4, `+3V3_ADAR_12` 3, `+3V3_FPGA` 2, `+5V0_PA_3` 2, `+5V5_PA` 2, `+1V0_FPGA` 2, `+3V3_SW` 2, `+3V3_VDD_SW` 2, `+3V3_ADAR_34` 2, `+5V0_0` 2, `+5V0_PA_1` 2, `+3V4` 1, `+1V8_FPGA` 1, `+3V3` 1, `+3V3_AN` 1, `+5V0_PA_2` 1. Freerouting's own verdict was 45 unrouted / 23 violations after pass 1; KiCad counts more because each isolated pour island counts separately (same source).

The reasons fall into three classes (wording of the `UNROUTED.md` table):

| Class | Typical entry | What is needed |
|---|---|---|
| GND pad ↔ GND pad | e.g. U34 pads 8/18/21 at (121.0, −90…−94) | the B.Cu GND plane is fragmented by the autorouted bottom tracks; the stitching via next to the pad was reverted by DRC → manual via placement or move the bottom tracks |
| zone island ↔ zone island (same net) | e.g. `VIN` zones priority 22 ↔ 28 at (71.2, −175.9) ↔ (215.6, −208.3) | the EAGLE polygons are separate local pours joined only by airwires; Freerouting routes pins, not pours → a manual 2 mm VIN / GND bus or a redesign of the pour layout |
| pin ↔ pin unroutable | e.g. `+1V8_FPGA` tracks at (129.6, −52.7) ↔ (152.5, −49.2) | Freerouting reported the connection unroutable in both passes (2-layer, local congestion) → manual routing |
| pad/track ↔ pour | e.g. U27 pad 4 ↔ GND zone priority 23 | no DRC-clean straight path and the autorouter escape failed |

Manual closing procedure (source: `UNROUTED.md` §How to close them): open `POWER_SUPPLY.kicad_pcb`, Inspect → Design Rules Checker → *Run DRC*, use the *Unconnected Items* tab; route 2.0 mm (VIN) / 1.0 mm (other rails) tracks between pours or extend a pour outline, then *Refill zones*; add 0.6/0.3 mm GND vias into the B.Cu plane where clearance allows, else move the autorouted 0.25 mm B.Cu track that cuts the island (all autorouted tracks are listed in `ses_merge.json` / `ses_merge_pass2.json`); re-run DRC until *Unconnected items* = 0, then `bash beta/pcb/tools/beta_export_package.sh POWER_SUPPLY`.

Remaining DRC after BETA (source: `beta/pcb/POWER_SUPPLY/README.md` §3): clearance 56 (0.15 mm pad-to-pad inside the ADM7151/TPS7A83 footprints and 3 `N$` tracks of the source — footprint level), drill_out_of_range 8 (0.254 mm via-pads in the TPS7A8300 footprint vs DRU 0.3 mm min drill — fab to confirm), silk 168/65 (reference texts of script-placed parts on their own pads — cosmetic), via_dangling 20 (autorouter vias whose second-side wire was dropped — remove with *Cleanup tracks & vias* once routing is final), solder_mask_bridge 8, track_dangling 2, zones_intersect 1.

## 5.5 Layer plots and 3-D renders

![F5.2a — Power Board top composite (F.Cu + F.SilkS + Edge.Cuts) of the KiCad conversion of PowerBoard.brd, 280 × 300 mm; 132 parts parked outside the outline are not visible in this crop (status: SOURCE-DERIVED; source: engineering/PCB/POWER_SUPPLY/svg/POWER_SUPPLY_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/POWER_SUPPLY_top_composite.png)

![F5.2b — Power Board bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts) (status: SOURCE-DERIVED; source: engineering/PCB/POWER_SUPPLY/svg/POWER_SUPPLY_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/POWER_SUPPLY_bottom_composite_mirrored.png)

![F5.3a — Power Board 3-D render, top, KiCad conversion of the source layout (unplaced parts outside the outline) (status: SOURCE-DERIVED; source: engineering/PCB/POWER_SUPPLY/3d/POWER_SUPPLY_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/POWER_SUPPLY/3d/POWER_SUPPLY_render_top.png)

![F5.3b — Power Board BETA board after scripted placement, two Freerouting passes, bridges and GND stitching; 89 connections still open (status: BETA; source: beta/pcb/POWER_SUPPLY/exports/3d/POWER_SUPPLY_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/POWER_SUPPLY/exports/3d/POWER_SUPPLY_render_isometric.png)

The generated assembly-drawing PDFs of this board are clipped by the A4 page frame in the same way as described for the Main Board (chapter 4 §4.5) and are not used as figures.

## 5.6 Stack-up

Source DRU `PCBWay_2L_100um-Track` (source: `engineering/PCB/POWER_SUPPLY/STACKUP.md`, status PARTIAL):

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 1.5mm |
| 2 | 16 | B.Cu | 0.035mm | — |

PROPOSED fabrication note (source: `beta/pcb/POWER_SUPPLY/FAB_NOTES.md` §2–§4): FR-4 Tg 150 °C core 1.5 mm, finished **1.6 mm ± 10 %**, no controlled impedance; copper **35 µm, PROPOSED 70 µm / 2 oz** because the VIN rails are 2 mm polygons on a power-distribution board (designer to decide); ENIG; min track/space 0.10 (BETA routing 0.25) / 0.20 mm; min drill 0.30 mm (0.5 mm via); copper-to-edge 0.3 mm; IPC-A-600 Class 2; 100 % e-test with `exports/ipc/POWER_SUPPLY_netlist.d356`. Note that §3 of that FAB_NOTES file repeats the RF-board template text (RO4350B, maskless RF traces) — it does not apply to this board, which has no RF or LVDS nets (`FAB_NOTES.md` §4). Current capacity of the highest-current traces (QPA2962 bias ≥ 1.68 A each per the xlsx; FPGA +1V0) is not checkable from XML and REQUIRES DESIGN REVIEW against IPC-2221 (source: `docs/PCB/POWER_SUPPLY.md` §7).

## 5.7 BOM summary

Source BOM `docs/BOM/BOM_POWER_SUPPLY.csv`: 312 references, 28 line items, 0 MPN attributes, 80 references without value (source: `docs/BOM/README.md`). BETA BOM confidence, counted with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/POWER_SUPPLY/BOM_POWER_SUPPLY_beta.csv'))))"`:

| mpn_confidence | Lines | Quantity (source: `beta/pcb/README.md`) |
|---|---|---|
| HIGH | 7 | 79 |
| MEDIUM | 18 | 225 |
| LOW | 3 | 8 |
| EMPTY | 0 | 0 |
| **Total** | **28** | 312 |

Before purchase (source: `docs/PCB/POWER_SUPPLY.md` §8): confirm 21 × TPS562208 against the xlsx rail count; confirm the AK300/2 input connector rating for the total current (sum not computed in the xlsx); add the TPS562208 and LM2662 datasheets to `7_Components Datasheets`.

## 5.8 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K4 | PA supply: xlsx needs 16 × 22 V / 2 A; this board has `Vin [12-17] V` only → DSN-PSU-01 proposal (chapter 9, D-14) | OPEN — power designer | `docs/SYSTEM/BLOCK_DIAGRAM.md`; `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5 |
| G-10 | Final outline: hole pattern (10..270 × 10..230, one at y = 267.85) suggests a smaller board than 280 × 300 | UNRESOLVED | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` |
| — | sch 9.6.2 / brd 7.4.0 mismatch; consistency check (P-EAGLE-01) not yet run in EAGLE | OPEN | `docs/PCB/POWER_SUPPLY.md` §5 |
| — | 89 open connections in BETA; placement review by a designer | OPEN | `beta/pcb/POWER_SUPPLY/UNROUTED.md` |
| — | 24 pins without net (TPS7A8300 feedback select, LM2662 FC/OSC) | OPEN | `engineering/ELECTRICAL/netlists/POWER_SUPPLY_unresolved_connections.md` |
| — | 80 value-less references (buck compensation parts) | OPEN | `docs/BOM/README.md` |
| — | 13 rail outputs without a same-name destination connector | OPEN | `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` |
| — | Copper weight 1 oz vs 2 oz; trace current capacity review | OPEN — designer | `beta/pcb/POWER_SUPPLY/FAB_NOTES.md` §2 |
| — | Datasheets of the parts actually used (TPS562208, LM2662) missing | OPEN | `docs/PCB/POWER_SUPPLY.md` §1 |

Acceptance criteria for this board (0 airwires, 0 off-board parts, outline recorded, DRC/ERC 0, Gerber/drill matching `POWER_SUPPLY_outline.svg`, 100 % MPN, PA-supply architecture decided) are copied from `docs/PCB/POWER_SUPPLY.md` §10 in chapter 14.
