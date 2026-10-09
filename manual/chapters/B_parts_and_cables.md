# B. Parts lists and cable schedule

**Appendix status summary:** PCB BOM summaries — PARTIAL (generated from the schematics, 0 MPN in the source; BETA MPN proposals with confidence classes); mechanical parts list — PROPOSED DESIGN (DSN-MECH-PL Rev A, masses are volume × density estimates); cable schedule — PROPOSED DESIGN (DSN-HAR-01 Rev A, lengths are Manhattan estimates to be cut after a first fit). No part in this appendix has been purchased, fitted or measured. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/BOM/README.md`, `docs/BOM/BOM_<BOARD>.csv`; `beta/pcb/README.md`, `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`; `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, `harness_schedule.csv`.

## B.1 PCB bills of materials

Generated 2026-10-08 by `python3 tools/gen_eagle_bom.py` directly from the EAGLE schematics (no EAGLE run); regenerate after any schematic change with the commands in `docs/BOM/README.md`. Columns of `BOM_<BOARD>.csv`: `item, qty, value, deviceset, device, package, library, mpn_attribute, manufacturer_attribute, mpn_candidate, mpn_status, references`; `REFS_<BOARD>.csv` has one row per reference designator (source: `docs/BOM/README.md` §What is in each file).

Summary copied from `docs/BOM/README.md` §Summary:

| Board | Physical references | Line items | Lines with MPN attribute | References without value | Status |
|---|---:|---:|---:|---:|---|
| Main Board | 776 | 98 | 0 | 244 | INCOMPLETE — no MPNs, FT601 (U6) unconnected but listed, 11 parts parked off-board |
| Power Supply | 312 | 28 | 0 | 80 | INCOMPLETE — no MPNs, 132 parts not placed on the board |
| RF PA | 25 | 11 | 0 | 6 | INCOMPLETE — no MPNs; `QPA2962_B` is a deviceset name |
| Frequency Synthesizer | 184 | 40 | 0 | 47 | INCOMPLETE — matches the existing `Clocks_Freq_Synth_board_BOM.xlsx` (40 lines) which also has empty MPN columns |

`mpn_status` meaning (same source): `VERIFIED (attribute)` — an explicit MPN attribute exists in the schematic (none today); `UNVERIFIED (deviceset name)` — the EAGLE deviceset name looks like a part number but has not been checked against a distributor; `GENERIC — value/package only` — passive to be sourced by value/package/tolerance (tolerance and voltage rating are not in the schematics).

BETA MPN proposals (`beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`, columns `manufacturer, mpn, mpn_confidence, dnp, note`; lines / quantity; source: `beta/pcb/README.md` §BOM confidence, line counts re-counted from the CSV files on 2026-10-09):

| Board | HIGH (deviceset = MPN) | MEDIUM (standard passive from value+package) | LOW (guess / non-standard value / conflict) | EMPTY (no value in the source) |
|---|---|---|---|---|
| Main Board | 23 / 204 | 41 / 461 | 30 / 93 | 4 / 18 |
| Power Supply | 7 / 79 | 18 / 225 | 3 / 8 | 0 / 0 |
| RF PA | 5 / 6 | 6 / 19 | 0 / 0 | 0 / 0 |
| Frequency Synthesizer | 10 / 37 | 22 / 110 | 6 / 29 | 2 / 8 |

The RF PA quantities are per board; the AERIS-10X variant uses 16 boards (source: `docs/PCB/RF_PA.md` §2). Chapters 4–7 §BOM summary list the conflicts flagged per board.

System-level items not on any PCB (source: `docs/BOM/README.md` §System-level items; quantities and part numbers UNKNOWN unless stated):

| Item | Evidence | Part number |
|---|---|---|
| GPS module (NMEA 9600 on UART5) | `main.cpp:2143-2170`; xlsx "NEO-6M" | NEO-6M (xlsx only) |
| IMU GY-85 (ADXL345/ITG3205/HMC5883L, I2C3) | `GY_85_HAL.c`; xlsx | GY-85 module |
| Barometer BMP180 (I2C3) | `BMP180.cpp`; xlsx | BMP180 |
| Temperature sensors TMP37 ×8 via ADS7830 | `main.cpp:1752-1775`; xlsx | TMP37 |
| Stepper motor 200 steps/rev + driver | `main.cpp:195`; xlsx "TBS6600 [9-42 V]" (TB6600-class) | motor UNKNOWN |
| Slip ring | `README.md:86`; `Project_Description.docx` | UNKNOWN |
| Cooling fans | `main.h:142` `EN_DIS_COOLING`; xlsx "COOLING SYSTEM" | UNKNOWN |
| Antenna array (8×16 patch or 32×16 slotted waveguide) | `README.md:82-83` | no CAD, no part |
| Enclosure | `README.md:143` (missing path) | none |
| Inter-board cables: SMA (37 + 11 + 2 ports), Molex 22-23-20xx (56 + 34 + 6 + 2 headers) | schematics | cable assemblies not defined |

The proposed designs of chapters 8–10 and the harness schedule below replace the last five rows with PROPOSED parts; the 22 V supply module BOM is `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/` (chapter 9).

## B.2 Mechanical parts list — DSN-MECH-PL Rev A (PROPOSED DESIGN)

Copied verbatim from `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (date 2026-10-09, from `CAD/detail/parts_list.json`, FreeCAD model `tools/design_enclosure_detail_freecad.py`; masses are volume × density estimates). Head ≈ 6.4 kg (structure only, PCBs/antenna not included except as noted), pedestal ≈ 12.4 kg (incl. stepper 1.1 kg, bearing/slip ring as modelled) (same source).

| # | Group | Part | Material | Mass (g) | Fasteners | Note |
|---|---|---|---|---|---|---|
| 1 | HEAD | Tray — base + sides + rear, 2.5 mm Al 5754, 3 bends R2.5, flanges 15 mm with M4 PEM nuts | Al | 1559 | PEM S-M4-1 ×18 | 8 lid holes M4, 10 front-plate holes M4, Ø70 cable entry, intake slots |
| 2 | HEAD | Front plate 2.5 mm Al with radome window opening and intake louvres | Al | 346 | M4×8 ×10 to tray front flanges | window 175×258, 16 M3 clamp holes |
| 3 | HEAD | Radome window PTFE 2 mm (outside the front plate) | PTFE | 246 |  | RF loss ≈ 0.1 dB at 10.5 GHz (PTFE εr 2.1, tanδ 0.0002 — to be confirmed) |
| 4 | HEAD | Window gasket EPDM 1.5 mm (ring 10 mm) | EPDM | 17 |  |  |
| 5 | HEAD | Window clamp frame 2 mm Al, 14 mm wide | Al | 69 | M3×10 ×16 + nyloc |  |
| 6 | HEAD | Lid 2.5 mm Al with exhaust slots | Al | 272 | M4×8 ×8 |  |
| 7 | HEAD | Lid gasket EPDM 3 mm self-adhesive, 15 mm wide on the flanges | EPDM | 44 |  | compressed to 2 mm → IP54 target |
| 8 | HEAD | PA heat spreader 300×300×10 Al 6061, machined fin fields, M3 tapped (16×7 PA + 6 antenna) | Al | 3400 | M3×6 ×118 (PA 112 + antenna 6) | thermal pads 5×5 under each QPA2962; antenna on 2.4 mm nylon spacers |
| 9 | HEAD | Plate bracket L 25×25×3 Al at x=5 z=20 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 10 | HEAD | Plate bracket L 25×25×3 Al at x=5 z=265.0 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 11 | HEAD | Plate bracket L 25×25×3 Al at x=280 z=20 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 12 | HEAD | Plate bracket L 25×25×3 Al at x=280 z=265.0 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 13 | HEAD | Main Board carrier rail bottom U15×12×1.5 Al, 280 mm | Al | 42 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 14 | HEAD | Main Board carrier rail top U15×12×1.5 Al, 280 mm | Al | 42 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 15 | HEAD | Main Board standoff M3×10 hex at (4,4) | steel | 2 | M3×6 ×1 |  |
| 16 | HEAD | Main Board standoff M3×10 hex at (256,4) | steel | 2 | M3×6 ×1 |  |
| 17 | HEAD | Main Board standoff M3×10 hex at (116,114) | steel | 2 | M3×6 ×1 |  |
| 18 | HEAD | Main Board standoff M3×10 hex at (256,114) | steel | 2 | M3×6 ×1 |  |
| 19 | HEAD | Main Board standoff M3×10 hex at (116,250) | steel | 2 | M3×6 ×1 |  |
| 20 | HEAD | Main Board standoff M3×10 hex at (256,250) | steel | 2 | M3×6 ×1 |  |
| 21 | HEAD | Main Board standoff M3×10 hex at (4,296) | steel | 2 | M3×6 ×1 |  |
| 22 | HEAD | Main Board standoff M3×10 hex at (256,296) | steel | 2 | M3×6 ×1 |  |
| 23 | HEAD | Synth carrier rail bottom U15×12×1.5 Al, 120 mm | Al | 18 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 24 | HEAD | Synth carrier rail top U15×12×1.5 Al, 120 mm | Al | 18 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 25 | HEAD | Synth standoff M3×10 hex at (5,5) | steel | 2 | M3×6 ×1 |  |
| 26 | HEAD | Synth standoff M3×10 hex at (95,5) | steel | 2 | M3×6 ×1 |  |
| 27 | HEAD | Synth standoff M3×10 hex at (5,95) | steel | 2 | M3×6 ×1 |  |
| 28 | HEAD | Synth standoff M3×10 hex at (95,95) | steel | 2 | M3×6 ×1 |  |
| 29 | HEAD | Power Board carrier rail bottom U15×12×1.5 Al, 300 mm | Al | 44 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 30 | HEAD | Power Board carrier rail top U15×12×1.5 Al, 300 mm | Al | 44 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 31 | HEAD | Power Board standoff M3×10 hex at (10,10) | steel | 2 | M3×6 ×1 |  |
| 32 | HEAD | Power Board standoff M3×10 hex at (140,10) | steel | 2 | M3×6 ×1 |  |
| 33 | HEAD | Power Board standoff M3×10 hex at (270,10) | steel | 2 | M3×6 ×1 |  |
| 34 | HEAD | Power Board standoff M3×10 hex at (10,120) | steel | 2 | M3×6 ×1 |  |
| 35 | HEAD | Power Board standoff M3×10 hex at (270,120) | steel | 2 | M3×6 ×1 |  |
| 36 | HEAD | Power Board standoff M3×10 hex at (10,230) | steel | 2 | M3×6 ×1 |  |
| 37 | HEAD | Power Board standoff M3×10 hex at (270,230) | steel | 2 | M3×6 ×1 |  |
| 38 | HEAD | Power Board standoff M3×10 hex at (138,268) | steel | 2 | M3×6 ×1 |  |
| 39 | HEAD | Cable-entry gland plate 100×100×2 Al under the base (M32 + M20 glands) | Al | 48 | M4×8 ×4; glands M32 + M20 IP68 | harness from the slip ring: VIN, 22 V, USB |
| 40 | PEDESTAL | Turntable plate Ø340×8 Al, 8×M6 to the head base, 12×M6 to the bearing outer ring | Al | 1864 | M6×16 ×8, M6×25 ×12 |  |
| 41 | PEDESTAL | Slewing bearing OD190/ID100×20 (4-point contact, e.g. igus PRT-04-100 class) | steel | 3218 |  | part number to be selected (axial ≥ 50 kg, moment ≥ 60 N·m) |
| 42 | PEDESTAL | Ring pulley GT3 180T Ø172 Al (machined/3D-printed), clamped under the turntable | Al | 0 | M4×10 ×6 |  |
| 43 | PEDESTAL | Pedestal top plate 360×360×5 Al, 12×M6 to the bearing inner ring, bore Ø90 | Al | 1658 | M6×20 ×12 |  |
| 44 | PEDESTAL | Pedestal housing 360×360×125 folded 2.5 mm Al (4 bends), open top, connector panel cut-out | Al | 1575 | M5×10 ×12 to the top plate | DC input (XT60/M12), USB-B bulkhead, vent |
| 45 | PEDESTAL | Stepper NEMA 23 76 mm | steel | 1898 | M5×12 ×4 |  |
| 46 | PEDESTAL | Motor bracket 80×80×3 Al with slotted belt-tension holes | Al | 41 | M5×10 ×4 to the top plate | slots ±5 mm for GT3 tension |
| 47 | PEDESTAL | Motor pulley GT3 60T Ø57, bore 6.35 | Al | 84 | grub M4 ×2 |  |
| 48 | PEDESTAL | Through-bore slip ring Ø99×60, bore 60, 12 circuits (4×10 A, 4×10 A, 4 signal) | plastic | 351 |  | e.g. Senring H3899 class — select |
| 49 | PEDESTAL | Slip-ring stator bracket 140×140×3 Al | Al | 95 | M4×8 ×4 | stator fixed to the pedestal, rotor flange to the turntable |
| 50 | PEDESTAL | Stepper driver TB6600 on DIN rail | plastic | 299 |  |  |
| 51 | PEDESTAL | Mast flange Ø150×10 steel, 4×M10 PCD 110 (ASSUMPTION — mast interface undefined) | steel | 1360 | M10×30 ×4 |  |

Fastener totals from the per-part lists (same source):

| Fastener | Qty |
|---|---|
| M10×30 | 4 |
| M3×10 | 16 |
| M3×6 | 138 |
| M4 | 2 |
| M4×10 | 6 |
| M4×8 | 38 |
| M5×10 | 16 |
| M5×12 | 12 |
| M5×16 | 4 |
| M6×16 | 8 |
| M6×20 | 12 |
| M6×25 | 12 |
| S-M4-1 | 18 |

Sealing and finish (same source): lid EPDM 15 × 3 mm self-adhesive gasket on the three top flanges, compressed to 2 mm by the M4 screws (pitch 60 mm); front plate 1.5 mm EPDM strip on the two front flanges; radome window PTFE 2 mm clamped by the 2 mm Al frame with EPDM 1.5 mm gasket, M3 × 18 (alternative 2 mm Rogers/ABS radome); cable entry 100 × 100 gland plate under the base with M32 (power) and M20 (USB) IP68 glands; finish chromate conversion (Alodine) + powder coat RAL 7035 outside, bare chromate inside for grounding at the flanges, PA plate bare 6061 with thermal pads. Open: bend reliefs and corner welds of the tray, stiffeners of the 315 mm lid, fan mounting brackets, antenna spacer material, earthing stud, lifting points, mast interface (row 51 is an ASSUMPTION).

## B.3 Cable schedule — DSN-HAR-01 Rev A (PROPOSED DESIGN)

Generated by `tools/design_mechanical_drawings.py` from the proposed layout (`tools/design_layout.py`) and the connector positions in the KiCad P&P files. Length = Manhattan distance between connector positions in the head + service allowance (40 mm coax / 60 mm wire), rounded up to 10 mm; lengths are PROPOSED, cut after a first fit (source: `HARNESS_SCHEDULE.md` header). Totals stated there: **144 cables; coax 55; wire 89; total proposed length ≈ 41.6 m**. Re-counted from `harness_schedule.csv` on 2026-10-09: 144 rows, 55 coax / 89 wire, sum of numeric lengths 41600 mm, 14 rows with length TBD (CBL-001, CBL-006, CBL-007, CBL-008, CBL-010, CBL-012, CBL-013, CBL-014, CBL-016, CBL-024, CBL-025, CBL-027, CBL-028, CBL-144).

Cable types (count from `harness_schedule.csv`, column `cable_type`):

| Count | Cable type |
|---|---|
| 32 | coax RG-405 SMA-SMA, EQUAL LENGTH set |
| 21 | 2-wire 20 AWG, Molex 22-01-2027 both ends |
| 16 | 2-wire 24 AWG shielded, Molex 22-01-2027 |
| 16 | 3-wire 24 AWG twisted, Molex 22-01-3037 |
| 16 | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set |
| 16 | 2-wire 18 AWG twisted, AK300/2 screw terminal |
| 13 | 2-wire 20 AWG |
| 7 | coax RG-405 (0.086") SMA-SMA, phase-stable |
| 2 | ribbon/discrete 26 AWG, 2.54 mm housings |
| 2 | 2 × 2-wire 16 AWG |
| 1 | 20-way 1.27 mm IDC ribbon |
| 1 | USB 2.0 shielded, mini-B |
| 1 | 3-wire 24 AWG shielded |

Signal groups: 16 × each of `VG_n` gate bias, drain-current sense, RF to PA RFIN, RF from PA RFOUT, RF to antenna row n, 22 V pulsed drain (CBL-045…CBL-140, six cables per PA); 34 Power Board rail cables (CBL-001…CBL-034, 13 of them TBD because no connector on the Main/Synth board carries the same net name — resolve with `engineering/SYSTEM/interfaces/interconnection_table.md`); the enable bus (CBL-035, 20-way IDC); 7 Synth → Main coax (CBL-036…CBL-042, RG-405 phase-stable); 2 control-header cables (CBL-043/044); slip-ring VIN, 22 V boost input and USB (CBL-141…CBL-143); stepper STEP/DIR/EN (CBL-144, DECISION NEEDED: driver on the fixed base needs 3 more slip-ring circuits, or move the driver into the head).

Caveats carried in the `note` column: PA instance ↔ `VG_n` assignment PROPOSED (n = n, not documented in CAD); Main sense connector ↔ PA n PROPOSED; which SMA of each Main Board pair is RFIN/RFOUT is UNVERIFIED (`interconnection_table.md` §7); antenna row n ↔ PA n PROPOSED, equal length mandatory for elevation phase. Note that the cable IDs of this schedule (CBL-001…CBL-144) are the DSN-HAR-01 numbering; the interconnection table of chapter 3 uses its own earlier CBL-xx numbering.

### B.3.1 Full schedule (copied verbatim from `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`)

| ID | From | To | Signal | Cable | Length (mm) | Note |
|---|---|---|---|---|---|---|
| CBL-001 | POWER_SUPPLY X2 | ? ? | +5V0_1 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-002 | POWER_SUPPLY X3 | MAIN_BOARD X55 | +5V5_PA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 780 | rail name matched in both netlists |
| CBL-003 | POWER_SUPPLY X4 | MAIN_BOARD X8 | +1V0_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 310 | rail name matched in both netlists |
| CBL-004 | POWER_SUPPLY X5 | MAIN_BOARD X10 | +1V8_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 340 | rail name matched in both netlists |
| CBL-005 | POWER_SUPPLY X6 | FREQUENCY_SYNTHESIZER X15 | +5V0_LO | 2-wire 20 AWG, Molex 22-01-2027 both ends | 960 | rail name matched in both netlists |
| CBL-006 | POWER_SUPPLY X7 | ? ? | +3V3_LO_2 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-007 | POWER_SUPPLY X8 | ? ? | +3V3_LO_1 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-008 | POWER_SUPPLY X9 | ? ? | +5V0_2 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-009 | POWER_SUPPLY X10 | MAIN_BOARD X17 | +1V8_CLOCK | 2-wire 20 AWG, Molex 22-01-2027 both ends | 840 | rail name matched in both netlists |
| CBL-010 | POWER_SUPPLY X11 | ? ? | +3V3_CLOCK | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-011 | POWER_SUPPLY X12 | MAIN_BOARD X56 | +3V3_AN | 2-wire 20 AWG, Molex 22-01-2027 both ends | 380 | rail name matched in both netlists |
| CBL-012 | POWER_SUPPLY X13 | ? ? | +5V0_ADAR | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-013 | POWER_SUPPLY X14 | ? ? | +3V3_ADAR_12 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-014 | POWER_SUPPLY X15 | ? ? | +3V3_ADAR_34 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-015 | POWER_SUPPLY X16 | MAIN_BOARD X24 | +3V3 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 200 | rail name matched in both netlists |
| CBL-016 | POWER_SUPPLY X17 | ? ? | +5V0_3 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-017 | POWER_SUPPLY X18 | MAIN_BOARD X6 | -3V3_SW | 2-wire 20 AWG, Molex 22-01-2027 both ends | 310 | rail name matched in both netlists |
| CBL-018 | POWER_SUPPLY X19 | MAIN_BOARD X19 | -5V5_PA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 380 | rail name matched in both netlists |
| CBL-019 | POWER_SUPPLY X20 | MAIN_BOARD X15 | -5V0_ADAR34 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 240 | rail name matched in both netlists |
| CBL-020 | POWER_SUPPLY X21 | MAIN_BOARD X13 | -5V0_ADAR12 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 360 | rail name matched in both netlists |
| CBL-021 | POWER_SUPPLY X22 | MAIN_BOARD X18 | +5V0_0 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 400 | rail name matched in both netlists |
| CBL-022 | POWER_SUPPLY X23 | MAIN_BOARD X1 | +3V4 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 360 | rail name matched in both netlists |
| CBL-023 | POWER_SUPPLY X24 | MAIN_BOARD X11 | -3V4 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 330 | rail name matched in both netlists |
| CBL-024 | POWER_SUPPLY X25 | ? ? | +5V0_4 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-025 | POWER_SUPPLY X26 | ? ? | +5V0_ADTR | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-026 | POWER_SUPPLY X27 | MAIN_BOARD X16 | +3V3_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 430 | rail name matched in both netlists |
| CBL-027 | POWER_SUPPLY X28 | ? ? | +5V0_5 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-028 | POWER_SUPPLY X29 | ? ? | +3V3_SW | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-029 | POWER_SUPPLY X30 | MAIN_BOARD X12 | +3V3_VDD_SW | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1090 | rail name matched in both netlists |
| CBL-030 | POWER_SUPPLY X31 | MAIN_BOARD X14 | +5V0_PA_1 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1180 | rail name matched in both netlists |
| CBL-031 | POWER_SUPPLY X32 | MAIN_BOARD X5 | +5V0_PA_2 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1310 | rail name matched in both netlists |
| CBL-032 | POWER_SUPPLY X33 | MAIN_BOARD X7 | +5V0_PA_3 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1020 | rail name matched in both netlists |
| CBL-033 | POWER_SUPPLY X34 | MAIN_BOARD X4 | +3V3_ADTR | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1120 | rail name matched in both netlists |
| CBL-034 | POWER_SUPPLY X35 | FREQUENCY_SYNTHESIZER X4 | +3V3_XO | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1030 | rail name matched in both netlists |
| CBL-035 | POWER_SUPPLY SV1 | MAIN_BOARD SV1 | enable bus (15 EN + GND) | 20-way 1.27 mm IDC ribbon | 320 |  |
| CBL-036 | FREQUENCY_SYNTHESIZER J7 | MAIN_BOARD J1 | 100 MHz FPGA sys clk | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-037 | FREQUENCY_SYNTHESIZER J5 | MAIN_BOARD J20 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 170 | mapping from interconnection_table.md §6 |
| CBL-038 | FREQUENCY_SYNTHESIZER J6 | MAIN_BOARD J18 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-039 | FREQUENCY_SYNTHESIZER J3 | MAIN_BOARD J21 | 400 MHz ADC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-040 | FREQUENCY_SYNTHESIZER J10 | MAIN_BOARD J23 | LO TX | coax RG-405 (0.086") SMA-SMA, phase-stable | 100 | mapping from interconnection_table.md §6 |
| CBL-041 | FREQUENCY_SYNTHESIZER J11 | MAIN_BOARD J22 | LO RX | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-042 | FREQUENCY_SYNTHESIZER J4 | MAIN_BOARD J19 | test | coax RG-405 (0.086") SMA-SMA, phase-stable | 100 | mapping from interconnection_table.md §6 |
| CBL-043 | FREQUENCY_SYNTHESIZER JP1 | MAIN_BOARD JP1 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 210 |  |
| CBL-044 | FREQUENCY_SYNTHESIZER JP2 | MAIN_BOARD JP13 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 240 |  |
| CBL-045 | MAIN_BOARD X_7 | RF_PA PA1 X2 | VG_1 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 150 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-046 | MAIN_BOARD X3 | RF_PA PA1 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 150 | Main sense connector ↔ PA n PROPOSED |
| CBL-047 | MAIN_BOARD J27 | RF_PA PA1 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 330 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-048 | MAIN_BOARD J26 | RF_PA PA1 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-049 | RF_PA PA1 J2 | ANTENNA ROW1 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 100 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-050 | DSN-PSU-01 OUT1 | RF_PA PA1 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 510 |  |
| CBL-051 | MAIN_BOARD X_16 | RF_PA PA2 X2 | VG_2 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 140 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-052 | MAIN_BOARD X38 | RF_PA PA2 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 110 | Main sense connector ↔ PA n PROPOSED |
| CBL-053 | MAIN_BOARD J29 | RF_PA PA2 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 310 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-054 | MAIN_BOARD J28 | RF_PA PA2 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-055 | RF_PA PA2 J2 | ANTENNA ROW2 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 150 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-056 | DSN-PSU-01 OUT2 | RF_PA PA2 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 470 |  |
| CBL-057 | MAIN_BOARD X_8 | RF_PA PA3 X2 | VG_3 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 210 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-058 | MAIN_BOARD X39 | RF_PA PA3 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 160 | Main sense connector ↔ PA n PROPOSED |
| CBL-059 | MAIN_BOARD J25 | RF_PA PA3 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 290 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-060 | MAIN_BOARD J24 | RF_PA PA3 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 300 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-061 | RF_PA PA3 J2 | ANTENNA ROW3 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 210 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-062 | DSN-PSU-01 OUT3 | RF_PA PA3 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 430 |  |
| CBL-063 | MAIN_BOARD X_15 | RF_PA PA4 X2 | VG_4 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 240 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-064 | MAIN_BOARD X40 | RF_PA PA4 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 210 | Main sense connector ↔ PA n PROPOSED |
| CBL-065 | MAIN_BOARD J31 | RF_PA PA4 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 290 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-066 | MAIN_BOARD J30 | RF_PA PA4 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 330 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-067 | RF_PA PA4 J2 | ANTENNA ROW4 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 260 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-068 | DSN-PSU-01 OUT4 | RF_PA PA4 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 390 |  |
| CBL-069 | MAIN_BOARD X_4 | RF_PA PA5 X2 | VG_5 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 190 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-070 | MAIN_BOARD X41 | RF_PA PA5 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 220 | Main sense connector ↔ PA n PROPOSED |
| CBL-071 | MAIN_BOARD J35 | RF_PA PA5 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 340 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-072 | MAIN_BOARD J34 | RF_PA PA5 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-073 | RF_PA PA5 J2 | ANTENNA ROW5 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 90 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-074 | DSN-PSU-01 OUT5 | RF_PA PA5 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 440 |  |
| CBL-075 | MAIN_BOARD X_11 | RF_PA PA6 X2 | VG_6 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 220 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-076 | MAIN_BOARD X42 | RF_PA PA6 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 220 | Main sense connector ↔ PA n PROPOSED |
| CBL-077 | MAIN_BOARD J37 | RF_PA PA6 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 310 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-078 | MAIN_BOARD J36 | RF_PA PA6 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-079 | RF_PA PA6 J2 | ANTENNA ROW6 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 140 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-080 | DSN-PSU-01 OUT6 | RF_PA PA6 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 400 |  |
| CBL-081 | MAIN_BOARD X_3 | RF_PA PA7 X2 | VG_7 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 290 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-082 | MAIN_BOARD X43 | RF_PA PA7 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 250 | Main sense connector ↔ PA n PROPOSED |
| CBL-083 | MAIN_BOARD J33 | RF_PA PA7 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 300 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-084 | MAIN_BOARD J32 | RF_PA PA7 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 250 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-085 | RF_PA PA7 J2 | ANTENNA ROW7 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 200 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-086 | DSN-PSU-01 OUT7 | RF_PA PA7 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 360 |  |
| CBL-087 | MAIN_BOARD X_12 | RF_PA PA8 X2 | VG_8 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 280 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-088 | MAIN_BOARD X44 | RF_PA PA8 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 280 | Main sense connector ↔ PA n PROPOSED |
| CBL-089 | MAIN_BOARD J39 | RF_PA PA8 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 270 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-090 | MAIN_BOARD J38 | RF_PA PA8 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-091 | RF_PA PA8 J2 | ANTENNA ROW8 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 250 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-092 | DSN-PSU-01 OUT8 | RF_PA PA8 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 320 |  |
| CBL-093 | MAIN_BOARD X_5 | RF_PA PA9 X2 | VG_9 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 290 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-094 | MAIN_BOARD X45 | RF_PA PA9 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 340 | Main sense connector ↔ PA n PROPOSED |
| CBL-095 | MAIN_BOARD J47 | RF_PA PA9 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-096 | MAIN_BOARD J46 | RF_PA PA9 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 270 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-097 | RF_PA PA9 J2 | ANTENNA ROW9 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 100 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-098 | DSN-PSU-01 OUT9 | RF_PA PA9 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 380 |  |
| CBL-099 | MAIN_BOARD X_14 | RF_PA PA10 X2 | VG_10 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 280 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-100 | MAIN_BOARD X46 | RF_PA PA10 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 290 | Main sense connector ↔ PA n PROPOSED |
| CBL-101 | MAIN_BOARD J41 | RF_PA PA10 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-102 | MAIN_BOARD J40 | RF_PA PA10 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 240 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-103 | RF_PA PA10 J2 | ANTENNA ROW10 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 130 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-104 | DSN-PSU-01 OUT10 | RF_PA PA10 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 340 |  |
| CBL-105 | MAIN_BOARD X_6 | RF_PA PA11 X2 | VG_11 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 350 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-106 | MAIN_BOARD X47 | RF_PA PA11 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 240 | Main sense connector ↔ PA n PROPOSED |
| CBL-107 | MAIN_BOARD J45 | RF_PA PA11 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 160 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-108 | MAIN_BOARD J44 | RF_PA PA11 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 140 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-109 | RF_PA PA11 J2 | ANTENNA ROW11 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 190 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-110 | DSN-PSU-01 OUT11 | RF_PA PA11 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 300 |  |
| CBL-111 | MAIN_BOARD X_13 | RF_PA PA12 X2 | VG_12 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 380 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-112 | MAIN_BOARD X48 | RF_PA PA12 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 290 | Main sense connector ↔ PA n PROPOSED |
| CBL-113 | MAIN_BOARD J43 | RF_PA PA12 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 160 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-114 | MAIN_BOARD J42 | RF_PA PA12 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 120 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-115 | RF_PA PA12 J2 | ANTENNA ROW12 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 240 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-116 | DSN-PSU-01 OUT12 | RF_PA PA12 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 260 |  |
| CBL-117 | MAIN_BOARD X_2 | RF_PA PA13 X2 | VG_13 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 360 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-118 | MAIN_BOARD X49 | RF_PA PA13 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 410 | Main sense connector ↔ PA n PROPOSED |
| CBL-119 | MAIN_BOARD J55 | RF_PA PA13 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 250 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-120 | MAIN_BOARD J54 | RF_PA PA13 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-121 | RF_PA PA13 J2 | ANTENNA ROW13 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 110 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-122 | DSN-PSU-01 OUT13 | RF_PA PA13 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 310 |  |
| CBL-123 | MAIN_BOARD X_9 | RF_PA PA14 X2 | VG_14 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 380 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-124 | MAIN_BOARD X50 | RF_PA PA14 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 380 | Main sense connector ↔ PA n PROPOSED |
| CBL-125 | MAIN_BOARD J49 | RF_PA PA14 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 250 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-126 | MAIN_BOARD J48 | RF_PA PA14 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 230 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-127 | RF_PA PA14 J2 | ANTENNA ROW14 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 130 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-128 | DSN-PSU-01 OUT14 | RF_PA PA14 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 270 |  |
| CBL-129 | MAIN_BOARD X_1 | RF_PA PA15 X2 | VG_15 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 450 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-130 | MAIN_BOARD X51 | RF_PA PA15 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 350 | Main sense connector ↔ PA n PROPOSED |
| CBL-131 | MAIN_BOARD J53 | RF_PA PA15 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 150 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-132 | MAIN_BOARD J52 | RF_PA PA15 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 190 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-133 | RF_PA PA15 J2 | ANTENNA ROW15 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 180 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-134 | DSN-PSU-01 OUT15 | RF_PA PA15 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 230 |  |
| CBL-135 | MAIN_BOARD X_10 | RF_PA PA16 X2 | VG_16 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 450 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-136 | MAIN_BOARD X52 | RF_PA PA16 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 370 | Main sense connector ↔ PA n PROPOSED |
| CBL-137 | MAIN_BOARD J51 | RF_PA PA16 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 170 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-138 | MAIN_BOARD J50 | RF_PA PA16 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 190 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-139 | RF_PA PA16 J2 | ANTENNA ROW16 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 230 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-140 | DSN-PSU-01 OUT16 | RF_PA PA16 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 190 |  |
| CBL-141 | SLIP RING VIN | POWER_SUPPLY X1 | VIN 12-17 V | 2 × 2-wire 16 AWG | 340 |  |
| CBL-142 | SLIP RING VIN | DSN-PSU-01 IN | VIN to 22 V boost | 2 × 2-wire 16 AWG | 470 |  |
| CBL-143 | SLIP RING USB | MAIN_BOARD X53 | USB 2.0 FS to host | USB 2.0 shielded, mini-B | 360 |  |
| CBL-144 | MAIN_BOARD stepper pins | PEDESTAL TB6600 (via slip ring) | STEP/DIR/EN | 3-wire 24 AWG shielded | TBD | the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head (then only motor phases cross: 4 circuits) — DECISION NEEDED |
