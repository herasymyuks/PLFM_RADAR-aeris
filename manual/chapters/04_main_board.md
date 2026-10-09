# 4. Main Board (RADAR_Main_Board)

**Chapter status summary:** schematic set — SOURCE-DERIVED (rendered from the EAGLE 7.4.0 file); connector and part inventory — SOURCE-DERIVED; layout — PARTIAL in the source (2 390 airwires), BETA in `beta/pcb/MAIN_BOARD/` (0 unconnected, 1 049 DRC items dispositioned); layer plots and 3-D renders — SOURCE-DERIVED / BETA (KiCad conversion, no component models); stack-up — PARTIAL (layer order from the DRU) with a PROPOSED fabrication proposal; BOM — PARTIAL (0 MPN in the source; BETA proposals with confidence classes); rev. B host interface — PROPOSED DESIGN (chapter 9). Nothing in this chapter is hardware-verified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/MAIN_BOARD.md`; `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §1–2; `engineering/ELECTRICAL/schematics/MAIN_BOARD/` (renders + `sheets.json`); `engineering/PCB/MAIN_BOARD/README.md`, `STACKUP.md`; `beta/pcb/MAIN_BOARD/README.md`, `FAB_NOTES.md`, `BOM_MAIN_BOARD_beta.csv`; `engineering/SYSTEM/interfaces/interconnection_table.md`; `docs/SYSTEM/BLOCK_DIAGRAM.md` (K1–K8).

## 4.1 Role and key parts

The Main Board carries the complete digital and RF core of the radar head: the Artix-7 FPGA, the STM32F7 controller, the 500 MSPS ADC and the DAC, the four ADAR1000 beamformer ICs with sixteen ADTR1107 front-end modules, the two LTC5552 mixers, the PA bias/sense circuitry for sixteen external PA boards, and all power-entry connectors from the Power Board. It is the largest board of the set: **260 × 300 mm, 10 copper layers**, EAGLE 7.4.0 schematic and board, 776 physical parts, 625 nets, 2 893 vias (source: `docs/PCB/MAIN_BOARD.md` §1).

Key ICs — deviceset names from the schematic; the MPN status of every line is UNVERIFIED (source: `docs/PCB/MAIN_BOARD.md` §1):

| Function | Part (refdes) | Qty | Note |
|---|---|---|---|
| FPGA | XC7A50T-2FTG256I (U42) | 1 | conflict K1: README/XDC name an XC7A100T (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` K1) |
| MCU | STM32F746ZGT7 (U2) | 1 | HSE crystal NX3225GD-8MHZ on board vs. 25 MHz in firmware — K2 |
| ADC | AD9484BCPZ-500 (U1) | 1 | |
| DAC | AD9708AR (U3) | 1 | |
| Beamformer | ADAR1000ACCZN | 4 | |
| T/R front end | ADTR1107ACCZ | 16 | |
| Mixers | LTC5552IUDBTRMPBF (U5, U13) | 2 | |
| IF amplifiers | AD8352ACPZ-R7 | 2 | `EN_OPAMP_IF_1/2` are single-pin nets (ENB floating) |
| RF switches | M3SWA2-34DR+ | 17 | |
| PA current sense | INA241A3IDGKR | 16 | |
| Temperature ADC | ADS7830IPWR | 3 | |
| PA gate-bias DACs | DAC5578SRGET (U7, U69) | 2 | thermal-pad pins missing from the symbol — see §4.4 |
| Bias op-amps | OPA4703EA/250 | 4 | |
| Config flash | MT25QL01GBBB8E12 (U9) | 1 | |
| Power module | EP4RKU+ (U16) | 1 | |
| USB 3.0 FIFO | FT601Q-B-T (U6) | 1 | **0 of 77 pins connected** in the schematic — K3, see §4.8 |
| Connectors | SMA 142-0731-211 ×37, Molex 22-23-20xx ×56, mini-USB X53 | — | |

Parts whose datasheets are in `7_Components Datasheets` but which are *not* on this schematic: FT2232H, FT232RN, MAX20029, STUW81300, QPM1021, QPA1013, TGA2623 (source: `docs/PCB/MAIN_BOARD.md` §1).

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §1):

| Item | Count |
|---|---|
| Sheets | 4 |
| Parts (all) / physical | 1955 / 776 |
| Nets | 625 |
| Pin connections | 4456 |
| Single-pin nets | 3 |
| Unconnected pins on placed gates | 280 |
| Physical parts without value | 244 |
| Board airwires (unrouted connections, layer 19) | 2390 |
| Missing symbol/footprint records | 0 |

## 4.2 Connectors

The connection report lists 117 connector parts (source: `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §2; the table below groups them by function, nets as in the report; pin order of the Molex symbols is UNVERIFIED because all pads are named `S` — source: `engineering/SYSTEM/interfaces/interconnection_table.md` header).

| Group | Refdes | Package | Nets (signal pins; GND omitted) | Sheet |
|---|---|---|---|---|
| Clock inputs (SMA) | J1 | 142-0731-211 | `FPGA_SYS_CLOCK` | 2 |
| | J18 | 142-0731-211 | `FPGA_DAC_CLOCK` | 2 |
| | J20 | 142-0731-211 | `DAC_CLOCK` | 3 |
| Differential clock inputs | J19 | CJT-T-P-HH-ST-TH1 | `FPGA_ADC_CLOCK_P/N` | 2 |
| | J21 | CJT-T-P-HH-ST-TH1 | `N$2_P/N` (ADC clock) | 3 |
| LO inputs (SMA) | J22, J23 | 142-0731-211 | `N$24` (LO RX), `N$23` (LO TX) — assignment per `interconnection_table.md` §6 | 3 |
| Element RF ports (SMA, 16 pairs) | J24–J55 | 142-0731-211 | unnamed nets `N$128…N$204`, one pair per RF switch; pairing J27/J26 = PA1 … J51/J50 = PA16 (source: `interconnection_table.md` §7); which SMA of a pair is TX-out vs RX-return is UNVERIFIED | 3 |
| Synth control | JP1 | PINHD-2X6 | `AD9523_PD, _REF_SEL, _SYNC, _RESET, _CS, STM32_SCLK4/MOSI4/MISO4, AD9523_STATUS0/1, _EEPROM_SEL` | 2 |
| | JP13 | PINHD-2X7 | `STM32_MISO4/SCLK4/MOSI4`, `ADF4382_TX_*`, `ADF4382_RX_*` (CS, CE, DELSTR, DELADJ, LKDET) | 2 |
| SWD debug | JP2 | PINHD-1X6 | `+3V3, STM32_SWCLK, STM32_SWDIO, STM32_NRST, STM32_SWO` | 2 |
| FPGA JTAG | JP3 | PINHD-2X4 | `N$32, +3V3_FPGA, N$33, N$34, N$36` | 2 |
| Cooling / PA enable | JP4, JP10 | PINHD-1X3 | `EN/DIS_COOLING`, `EN/DIS_RFPA_VDD` | 2 |
| Temperature sensors | JP5, JP6, JP11, JP12, JP14, JP15, JP16, JP19 | PINHD-1X3 | `+3V3_AN4_F` + one analogue net each (`N$295…N$307`) | 4 |
| I2C3 modules | JP7 (1×8), JP18 (1×4) | PINHD | `+3V3, STM32_SCL3, STM32_SDA3, MAG_DRDY, ACC_INT, GYR_INT` / `STM32_SDA3, STM32_SCL3, +3V3` | 2 |
| UART5 (GPS) | JP8 | PINHD-1X4 | `+3V3, STM32_TX5, STM32_RX5` | 2 |
| Stepper | JP9 | PINHD-1X4 | `STEPPER_CW+, STEPPER_CLK+` | 2 |
| USART3 console | JP17 | PINHD-1X3 | `STM32_TX3, STM32_RX3` | 2 |
| Clock test | JP20 | PINHD-1X2 | `FPGA_CLOCK_TEST` | 2 |
| Enable bus to Power Board | SV1 | MA10-2 (20-way) | 15 × `EN_+…` rails (`EN_+1V0_FPGA … EN_+5V0_PA1`) | 2 |
| Power inputs (2-pin Molex) | X1, X4–X22, X24, X54–X56 | 22-23-2021 | one rail each: `+3V4, +3V3_ADTR, +5V0_PA_2, -3V3_SW, +5V0_PA_3, +1V0_FPGA, +3V3_AN, +1V8_FPGA, -3V4, +3V3_VDD_SW, -5V0_ADAR12, +5V0_PA_1, -5V0_ADAR34, +3V3_FPGA, +1V8_CLOCK, +5V0_0, -5V5_PA, +3V3_ADAR12, +3V3_ADAR34, +3V3, +5V5_PA` | 1 |
| PA gate bias outputs | X_1 … X_16 | 22-23-2021 | `VG_15, VG_13, VG_7, VG_5, VG_9, VG_11, VG_1, VG_3, VG_14, VG_16, VG_6, VG_8, VG_12, VG_10, VG_4, VG_2` (in refdes order X_1…X_16) | 4 |
| PA drain-current sense inputs | X3, X38–X52 | 22-23-2031 | one differential pair each (`N$207/N$209` … `N$286/N$287`) | 4 |
| Host USB | X53 | MINI-USB 32005-201 | `STM32_USB_FS_D_N, _D_P, _ID` (VBUS not connected) | 2 |

The cable-level use of these connectors (which Power Board output feeds which input, which Synth SMA drives J1/J18/J19/J20/J22/J23) is in chapter 3 and in `engineering/SYSTEM/interfaces/interconnection_table.md` §2–§8.

## 4.3 Schematic sheets

The four sheets were rendered from `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` with `tools/render_eagle_schematic.py` + `tools/svg_sheets_to_pdf.py` (PDF: `engineering/ELECTRICAL/schematics/MAIN_BOARD/MAIN_BOARD_schematic.pdf`; sheet sizes and part/net counts per sheet in `engineering/ELECTRICAL/schematics/MAIN_BOARD/sheets.json`). Sheet names are those stored in the EAGLE file (source: `docs/PCB/MAIN_BOARD.md` §1). Sheet 3 is 1 904 × 1 652 mm at 1:1 and must be read from the SVG/PDF for pin-level detail.

![F4.1 — Main Board schematic sheet 1 "POWER SUPPLIES": 189 parts, 33 nets (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet1.png)

![F4.2 — Main Board schematic sheet 2 "Digital (FPGA+microcontroller)": 196 parts, 181 nets (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet2.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet2.png)

![F4.3 — Main Board schematic sheet 3 "RF": 1 304 parts, 356 nets — ADAR1000 ×4, ADTR1107 ×16, mixers, switches, 32 element SMAs (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet3.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet3.png)

![F4.4 — Main Board schematic sheet 4 "RF POWER AMPLIFIER BIAS": DAC5578 ×2, OPA4703 ×4, INA241A3 ×16, VG outputs X_1…X_16, sense inputs X3/X38…X52 (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet4.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet4.png)

Schematic-level findings that no layout work can close (source: `docs/PCB/MAIN_BOARD.md` §2; `beta/pcb/MAIN_BOARD/README.md` §3): FT601 U6 supply/control pins unconnected (board-only signals `AVDD, VBUS, VCC33…, VCCIO…, VDDA` are forward-annotation residue); 280 unconnected symbol pins; single-pin nets `N$44` (AD9484 CML), `EN_OPAMP_IF_1`, `EN_OPAMP_IF_2`; XADC wiring VP/VN/VREFN to GND and VREFP to `+1V0_FPGA` (to be checked against AMD UG480); 4 approved ERC entries on `STM32_MISO_1V8`. The full list is in `engineering/ELECTRICAL/netlists/MAIN_BOARD_unresolved_connections.md`.

## 4.4 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 7.4.0)

| Item | Finding (source: `docs/PCB/MAIN_BOARD.md` §2) |
|---|---|
| Airwires | 2 390 stored on layer 19: GND 2 354, `+3V3_FPGA` 33, `+3V3_FT` 3 (entirely unrouted). GND has polygons on layers 2, 5, 13, 15 — whether `RATSNEST` clears the GND airwires REQUIRES VERIFICATION IN EAGLE |
| Parts outside outline | 11: C159, C184, C185, C186, L19 (FT601 decoupling), R60, R61, R83, R84, R145, R146 (parked at x = 0.1 mm, y < 0) |
| DRC | 211 `<approved>` entries (EAGLE stores no text) |
| ERC | 4 approved entries on net `STM32_MISO_1V8` |
| Layer-count mismatch | DRU name says 8 layers; 10 copper layers are defined and all carry copper (L1 7 619 objects, L2 1, L3 18, L4 9, L5 1, L12 587, L13 1, L14 395, L15 5, L16 1 605) |
| Via drills | 0.15 mm ×1 045, 0.2 ×1 367, 0.3 ×332, 0.35 ×113, 0.5 ×21, 0.6 ×7, 1.0 ×4, 1.2 ×4 (all through 1-16; no blind/buried) |
| Min track | 0.1 mm (3 408 wires); 0.204 mm RF width ×2 729 (matches the PCBWay 50 Ω note) |
| USB 3.0 | FT601 unconnected; the only host link is STM32 USB-FS (PA11/PA12 → X53) |

### Engineering conversion (`engineering/PCB/MAIN_BOARD/`, KiCad 10.0.6 import)

Cross-check of the EAGLE XML against the KiCad conversion (source: `engineering/PCB/MAIN_BOARD/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 260.0 | 260.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 784 | 784 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 2893 | 2893 | OK |  |
| Tracks (signal wires excl. airwires) | 10219 | 10219 | OK |  |
| Copper layers | 10 | 10 | OK |  |
| NPTH holes (free holes + package holes) | 10 | 10 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 3314 | 3314 | OK |  |

DRC on the conversion with EAGLE-DRU-derived rules: 912 violations, 15 unconnected (source: `engineering/PCB/MAIN_BOARD/README.md` §6):

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

Counts of exactly 199 are lower bounds (KiCad report cap).

### BETA board (`beta/pcb/MAIN_BOARD/`)

Before/after table (source: `beta/pcb/MAIN_BOARD/README.md` §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 15 | 0 |
| clearance | 63 | 72 |
| hole_clearance | 4 | 87 |
| shorting_items | 93 | 125 |
| silk_edge_clearance | 3 | 3 |
| silk_over_copper | 199 | 199 |
| silk_overlap | 199 | 199 |
| solder_mask_bridge | 199 | 199 |
| track_dangling | 136 | 130 |
| via_dangling | 15 | 35 |
| zones_intersect | 1 | 0 |
| **DRC violations total** | 912 | 1049 |

What was changed in BETA — nothing in the netlist, every step logged (source: `beta/pcb/MAIN_BOARD/README.md` §2): 7 arc tails where EAGLE arcs end on a pad centre (`fixes_stubs.json`); the `+3V3_FT` input filter L19/C159/C184/C185/C186 moved from outside the outline to (5…12, −232…−240) mm next to X16 (`placement_moves.json`); hand routing of that cluster with 4 GND vias 0.45/0.20 mm, a 0.3 mm `+3V3_FT` bus and a 0.5 mm `+3V3_FPGA` feed to X16.1 (`manual_routing.json`, `bridges.json`); 14 of 30 net-less footprint copper polygons (BPF2 filters, U13, U5) re-created as board-level polygons with the net they touch (`POLYGON_NET_DISPOSITION.md`); same-net zone priorities. R60, R61, R83, R84, R145, R146 (33 Ω 0201, no net on either pin) stay outside the outline and are `dnp = yes` in the BETA BOM.

Why the total went *up* although 15 → 0 unconnected: the remaining 1 049 items are dominated by copper that the schematic cannot describe (source: `beta/pcb/MAIN_BOARD/README.md` §3):

| Type | Count | Disposition |
|---|---|---|
| shorting_items | 125 | REAL (schematic): GND tracks/arcs run through the thermal-via pads `V…V_8` of U69 (DAC5578) and U7 — those pads have no net because the symbols have no paddle pin; EAGLE connected them with the GND polygon. Also the 4 ambiguous BPF2 polygons (GND + RF net) and KK headers JP7/JP8/JP10/JP17. Not changed in BETA → designer must add the paddle pins to the symbols or confirm the intended net |
| hole_clearance / clearance | 87 / 72 | same U69/U7 no-net via pads and the 4 ambiguous BPF2 polygons; plus 3 at ADAR1_0/ADAR3_0/J33 from the source |
| track_dangling | 130 | EAGLE stub ends inside pours/pads — cosmetic, copper not modified |
| via_dangling | 35 | 20 vias of RF_TX/RF_RX/RF_TX_FIL/RF_RX_FIL inside the BPF2 pads + 15 from the source (ADAR load/enable nets) |
| silk_overlap / silk_over_copper / solder_mask_bridge | 199+ each | cosmetic / fab CAM (0201 density) |
| silk_edge_clearance | 3 | X53 outline and JP3 reference at the board edge — cosmetic |

## 4.5 Layer plots and 3-D renders

Composite top and bottom views (copper + silkscreen + outline) of the engineering conversion. Per-layer plots (F.Cu, In1…In8, B.Cu) are listed as files in chapter 14, not reproduced here.

![F4.5a — Main Board top composite (F.Cu + F.SilkS + Edge.Cuts) of the KiCad conversion of RADAR_Main_Board.brd, 260 × 300 mm (status: SOURCE-DERIVED; source: engineering/PCB/MAIN_BOARD/svg/MAIN_BOARD_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/MAIN_BOARD_top_composite.png)

![F4.5b — Main Board bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts) (status: SOURCE-DERIVED; source: engineering/PCB/MAIN_BOARD/svg/MAIN_BOARD_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/MAIN_BOARD_bottom_composite_mirrored.png)

![F4.6a — Main Board 3-D render, top, KiCad conversion; no component models (STEP is board-only) (status: SOURCE-DERIVED; source: engineering/PCB/MAIN_BOARD/3d/MAIN_BOARD_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/MAIN_BOARD/3d/MAIN_BOARD_render_top.png)

![F4.6b — Main Board BETA board, isometric render after the +3V3_FT cluster placement and routing (status: BETA; source: beta/pcb/MAIN_BOARD/exports/3d/MAIN_BOARD_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/MAIN_BOARD/exports/3d/MAIN_BOARD_render_isometric.png)

Assembly drawings: the generated `engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf` and `beta/pcb/MAIN_BOARD/exports/drawings/MAIN_BOARD_assembly_top.pdf` exist (F.Fab + F.SilkS + Edge.Cuts, black and white), but when rendered with `pdftoppm -png -r 110` the A4 page frame plotted by `kicad-cli pcb export pdf --sp` contains only the parts parked outside the outline; the board body itself (at negative y in the KiCad coordinate frame) lies outside the page. The same applies to the Power Supply, Frequency Synthesizer and RF PA assembly PDFs. These PDFs are therefore not used as figures in this manual; the planned figure F4.7 is replaced by the top composite F4.5a (which carries F.SilkS and F.Fab reference designators) until the pipeline plots the drawing without the page frame (open item in chapter 17).

## 4.6 Stack-up

Layer order and copper thickness come from the EAGLE DRU `PCBWay_8L_100um-Track` (the name says 8 layers; the board uses 10). Dielectric thicknesses are the EAGLE DRU table, not a vendor stack-up; total thickness is not defined in the source (KiCad assumed 1.6 mm) (source: `engineering/PCB/MAIN_BOARD/STACKUP.md`, status PARTIAL):

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

PROPOSED fabrication stack-up (BETA, nothing confirmed by the designer or PCBWay; source: `beta/pcb/MAIN_BOARD/FAB_NOTES.md` §2): outer layers 1 and 9 on **Rogers RO4350B 4 mil (0.102 mm)** as the impedance layers, FR-4 cores/prepregs inside; dielectric sum 1.554 mm + 10 × 35 µm copper ≈ 1.9 mm → PROPOSED finished thickness **2.0 mm ± 10 %** (the DRU sum does not fit 1.6 mm). Materials/finish proposal (`FAB_NOTES.md` §3): 1 oz copper all layers, ENIG, green LPI mask with **no mask over RF traces** on the RF layer, white silk, min track/space 0.10/0.10 mm, min drill 0.15 mm, copper-to-edge 0.3 mm, IPC-A-600 Class 2, 100 % electrical test with the supplied IPC-D-356 netlist. Controlled impedance targets with the geometry measured on the KiCad board (`FAB_NOTES.md` §4): 50 Ω single-ended at w = 0.204 mm (2 729 segments); 100 Ω differential at w = 0.204 mm / s = 0.26 mm (`FPGA_ADC_CLOCK`, `MIX_RX`), `ADC_CLK_IN` s = 0.288 mm, `AMP_IF_IN` uncoupled (s = 1.58 mm). The impedance note itself (`4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf`) is a Frequency Synthesizer document; its applicability to this board is an assumption of the proposal — if the Main Board is built on plain FR-4 the 0.204 mm lines are not 50 Ω.

## 4.7 BOM summary

Source BOM (`docs/BOM/BOM_MAIN_BOARD.csv`, generated from the schematic): 776 references, 98 line items, **0 MPN attributes**, 244 references without value (source: `docs/BOM/README.md` §Summary). The BETA BOM `beta/pcb/MAIN_BOARD/BOM_MAIN_BOARD_beta.csv` adds `manufacturer, mpn, mpn_confidence, dnp, note` columns with proposed part numbers (`beta/pcb/tools/beta_bom_mpn.py`). Confidence count obtained with

`python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/MAIN_BOARD/BOM_MAIN_BOARD_beta.csv'))))"`

| mpn_confidence | Lines | Meaning (source: `beta/pcb/README.md` §BOM confidence) |
|---|---|---|
| HIGH | 23 | deviceset name is an orderable MPN |
| MEDIUM | 41 | standard passive proposed from value + package |
| LOW | 30 | guess / non-standard value / package-value conflict |
| EMPTY | 4 | no value in the source |
| **Total** | **98** | quantities 204 / 461 / 93 / 18 (same source) |

Flagged conflicts that the designer must resolve before purchase (source: `beta/pcb/README.md`): non-E-series values (2.443 kΩ, 103 pF, 107.3 nH), 47 µF in 0201, NX3225 footprint with a 32.768 kHz value, 5 mΩ shunt with a 0.1 Ω part number; the 37 SMA and 56 Molex connectors to be confirmed as production parts (many are test/interconnect points); FT601 and its 7 parked passives marked DNP or wired; INA241A3 ×16 and OPA4703 ×4 confirmed for the Nexus variant (source: `docs/PCB/MAIN_BOARD.md` §8).

## 4.8 Rev. B host interface (FT601)

The source Main Board has no usable high-speed host path: U6 (FT601Q-B-T) is placed but none of its 77 pins is connected, and the only host link is the STM32 USB full-speed port on X53 (source: `docs/PCB/MAIN_BOARD.md` §1–2; conflict K3 in `docs/SYSTEM/BLOCK_DIAGRAM.md`). Chapter 9 documents the two proposed options: option A — wire the FT601 to free FPGA bank-35 pins (47 signals, pin plan `engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv`, XDC fragment `ft601_bank35.xdc`, added parts `ft601_added_parts_BOM.csv`) in a **Main Board rev. B**; option B — the SPI bridge frame through the STM32 CDC link, implemented end-to-end in simulation (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §7).

The rev. B board package is `beta/pcb/MAIN_BOARD_REVB/` (status **BETA PROPOSAL — explicit netlist change, partially routed, DRC-checked, not reviewed by the original designer, not fabricated**; source: `beta/pcb/MAIN_BOARD_REVB/README.md`). It was derived from the rev. A BETA board with `beta/pcb/tools/beta_revb_ft601.py` and the design input of `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §4. **The EAGLE schematic has not been changed and no longer matches this board**: the designer must enter the connections of `NETLIST_DELTA.csv` (README §3) and the added parts (README §4) in the schematic, verify them against the FT601 datasheet (not in the repository) and re-annotate before any rev. B layout is released (same source, header note).

State of the rev. B board (source: `beta/pcb/MAIN_BOARD_REVB/README.md` §1):

| Check | Rev. A BETA (`MAIN_BOARD/`) | Rev. B after netlist change, before routing | Rev. B after routing (exports) |
|---|---|---|---|
| unconnected_items | 0 | 129 | 59 |
| **DRC total** | 1049 | 1055 | 1071 |

Of the 64 new nets, 17 are routed and connected (USB D±, both SuperSpeed RX lines, SSTX_N and both SSTX_C lines, CC1/CC2, USB_VBUS, FT_VBUS_DET, FT_RREF, FT_XI, FT_GPIO1, partly `+3V3_FT`/`FT_VD10`/`FT_AVDD`/`FT_XO`). **The 32-bit FIFO bus and its control lines (46 of 47 FPGA-side signals) are not routed**: 36 of the 47 bank-35 balls of U42 (XC7A50T FTG256, 1.0 mm pitch) have no free position for an escape via because the dog-bone positions are occupied by the existing BGA fan-out; routing the bus requires re-doing the U42 bank-35 breakout (same source; list in `beta/pcb/MAIN_BOARD_REVB/UNROUTED.md`, 59 open items all on rev. B nets). New DRC items from rev. B copper: 9 `track_width` neck-downs (0.075 mm, to be widened to 0.1 mm), 2 courtyard overlaps (Y_FT ↔ C_XI/C_XO), 1 copper-edge clearance at the J_USB3 NPTH peg, 5 dangling vias; the USB differential pairs were routed as single traces by Freerouting and must be re-routed coupled (0.204/0.18 mm) before release (README §1–§2). Added parts (README §4): USB-C receptacle J_USB3 Amphenol 12401610E4#2A (SS lane wired in one orientation only — VERIFY), 2 × TPD4E05U06 ESD arrays, 2 × 100 nF SSTX coupling capacitors, 2 × 5.1 kΩ CC resistors, VBUS divider 10 k/3.3 k, RREF 3.24 kΩ, 4 × 4.7 µF VD10 decoupling, AVDD ferrite + 100 nF + 1 µF, 30 MHz crystal ABM8 with 2 × 18 pF — every value carries a VERIFY note against the FT60x datasheet. `BOM_MAIN_BOARD_REVB_beta.csv` has 110 lines (97 rev. A, 12 new rev. B, 1 rev. A part now wired; counted from the CSV `revision` column). Full export package in `beta/pcb/MAIN_BOARD_REVB/exports/` (all 24 export steps exit 0 per `exports/EXPORT_LOG.md`). Procedures, pin plan and the bridge-frame alternative: chapter 9.

![F4.7 — Main Board rev. B proposal, isometric render: USB-C receptacle J_USB3 on the left edge next to U6 (FT601), ESD arrays, crystal and decoupling in the band below U6; FIFO bus to bank 35 unrouted (status: BETA; source: beta/pcb/MAIN_BOARD_REVB/exports/3d/MAIN_BOARD_REVB_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/MAIN_BOARD_REVB/exports/3d/MAIN_BOARD_REVB_render_isometric.png)

The rev. B netlist delta is the only schematic-level change proposed for this board; it is a PROPOSED DESIGN / BETA and not part of the ORIGINAL PROJECT FILE set.

## 4.9 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K1 | FPGA part: XC7A50T-2FTG256I in CAD vs XC7A100T in README/XDC | OPEN — hardware designer | `docs/SYSTEM/BLOCK_DIAGRAM.md` |
| K2 | STM32 HSE: 8 MHz crystal on board vs 25 MHz in firmware (beta firmware assumes 8 MHz) | OPEN | same; `docs/AERIS10_BETA_ENGINEERING_REPORT.md` |
| K3 | Host data path: FT601 unwired (option A rev. B / option B bridge) | OPEN — system architect | chapter 9 |
| — | Rev. B: FIFO bus (46 of 47 FPGA-side signals) unrouted — U42 bank-35 breakout must be redone; USB pairs to be re-routed coupled; EAGLE schematic not updated | OPEN — designer | `beta/pcb/MAIN_BOARD_REVB/README.md` §1, `UNROUTED.md` |
| — | 2 390 EAGLE airwires; `RATSNEST` behaviour on the GND polygons REQUIRES VERIFICATION IN EAGLE | OPEN | `docs/PCB/MAIN_BOARD.md` §2 |
| — | 125 shorting items from net-less thermal-via pads of U7/U69 and 4 ambiguous BPF2 polygons — symbol/footprint fix needed | OPEN — designer | `beta/pcb/MAIN_BOARD/README.md` §3 |
| — | 10-layer stack-up: DRU named for 8 layers; material, thickness, finish, impedance UNVERIFIED (G-01) | BLOCKED — MISSING DATA | `engineering/PCB/MAIN_BOARD/STACKUP.md`; MDR-07 |
| — | BOM: 0/98 lines with a verified MPN; 244 value-less references | OPEN | `docs/BOM/README.md` |
| — | XADC reference wiring; single-pin nets `N$44`, `EN_OPAMP_IF_1/2`; 280 unconnected symbol pins | OPEN | `engineering/ELECTRICAL/netlists/MAIN_BOARD_unresolved_connections.md` |
| — | Generated assembly-drawing PDFs clipped by the A4 page frame (§4.5) | OPEN — tooling | this chapter |
| — | 211 approved DRC entries in the source without justification text | OPEN | `docs/PCB/MAIN_BOARD.md` §2 |

Acceptance criteria for calling this board layout-complete are copied in chapter 14 (`docs/PCB/MAIN_BOARD.md` §10). Do not declare this board fabrication-ready on the basis of the existing `.sch/.brd` files or of the BETA package.
