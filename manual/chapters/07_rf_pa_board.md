# 7. RF Power Amplifier Board (RF_PA, ×16)

**Chapter status summary:** schematic — SOURCE-DERIVED (EAGLE 9.6.2 rendered); layout — complete in the source (0 airwires, 0 approved DRC), SOURCE-DERIVED in the KiCad conversion, BETA copy with one GND strap and the paddle polygon given its net (RF tracks untouched); layer plots and renders — SOURCE-DERIVED / BETA; stack-up — PARTIAL (4-layer DRU, 70 µm copper slot unexplained) with a PROPOSED fabrication note; BOM — PARTIAL (0 MPN; `QPA2962_B` is a deviceset name); thermal budget and drain gating — PROPOSED DESIGN (DSN-THM-01, D-10/D-11/D-14, first-order estimates). The 22 V drain supply, the drain-gating switch and the heat path do not exist in the original CAD. RF performance (gain, P1dB at 10.5 GHz) is unverified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/RF_PA.md`; `engineering/ELECTRICAL/connection_diagrams/RF_PA_connection_report.md`; `engineering/ELECTRICAL/schematics/RF_PA/`; `engineering/PCB/RF_PA/README.md`, `STACKUP.md`; `beta/pcb/RF_PA/README.md`, `FAB_NOTES.md`, `BOM_RF_PA_beta.csv`; `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md`; `engineering/SYSTEM/interfaces/interconnection_table.md` §7.

## 7.1 Role and key parts

One RF_PA board amplifies the transmit signal of one antenna row; the AERIS-10X variant uses sixteen boards, 10 W each (source: `docs/PCB/RF_PA.md` §2, citing `README.md:80`). Each board holds a single Qorvo QPA2962 GaN PA with its gate-bias input (`VG`, from the Main Board DAC5578/OPA4703 chain), a drain input (`VD`) through a 5 mΩ shunt whose two ends (`VD`, `VIN_M`) are returned to the Main Board INA241A3 current-sense amplifier, and two SMA jacks. Board: **35 × 60 mm, 4 copper layers**, EAGLE 9.6.2, 25 physical parts, 15 nets, 77 wires, 342 vias (of which 215 × 0.35 mm stitching/thermal), DRU `PCBWay_4L_100um-Track` (source: `docs/PCB/RF_PA.md` §1).

Parts (source: `docs/PCB/RF_PA.md` §1; `engineering/ELECTRICAL/connection_diagrams/RF_PA_connection_report.md` §4):

| Refdes | Value / device | Connections (pad:net) | Note |
|---|---|---|---|
| U$1 | QPA2962_B (Qorvo 10 W GaN PA) | GND, RFIN:`N$2`, RFOUT:`N$8`, VD1/VD2:`VIN_M`, VG:`VG` | deviceset name is not the orderable MPN; datasheet and S-parameters at 22 V / 1 680 mA in `7_Components Datasheets` |
| J1, J2 | SMA 142-0731-211 | J1 pin 1 `N$2` (RFIN per silk), J2 pin 1 `N$8` (RFOUT per silk) | |
| X2 | Molex 22-23-2021 | 1 `VG`, 2 `GND` | gate bias from Main X_n |
| X3 | Molex 22-23-2031 | 1 `VD`, 2 `VIN_M`, 3 `GND` | drain-current sense pair to Main X3/X38…X52 |
| 22V | AK300/2 screw terminal | 1 `VD`, 2 `GND` | drain supply input — no source in CAD (K4) |
| R10 | 5 mΩ WSL2816 | 1 `VIN_M`, 2 `VD` | shunt; BETA BOM flags a 0.1 Ω part number for a 5 mΩ value |
| R1, R4 | 10R 0402 | VG / VIN_M decoupling | |
| R2, R3, R5–R9 | 0R 0402/0603 | VG / VIN_M decoupling links | |
| C1, C4, C5 | 10 µF 1206 | decoupling | |
| C2, C3, C6–C9 | 0.1 µF 0402 | decoupling | |

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/RF_PA_connection_report.md` §1): 1 sheet; 43 parts / 25 physical; 15 nets; 78 pin connections; 0 single-pin nets; 0 unconnected pins; 6 physical parts without value; 0 airwires; 0 missing symbol/footprint records. Net fan-out: `GND` 38 connections, `VIN_M` 10 (same source §3). Silk labels on the board: `CURRENT SENSOR`, `VIN+`, `VIN-`, `VG` (source: `docs/PCB/RF_PA.md` §1).

System connections of one PA instance n (source: `engineering/SYSTEM/interfaces/interconnection_table.md` §7): element RF from Main Board SMA pair (J27/J26 for n = 1 … J51/J50 for n = 16) to J1/J2 — which SMA of the Main pair is TX-to-PA and which is RX-return is UNVERIFIED; gate bias `VG_n` from Main X_7 = VG_1, X_16 = VG_2, X_8 = VG_3, X_15 = VG_4, X_4 = VG_5, X_11 = VG_6, X_3 = VG_7, X_12 = VG_8, X_5 = VG_9, X_14 = VG_10, X_6 = VG_11, X_13 = VG_12, X_2 = VG_13, X_9 = VG_14, X_1 = VG_15, X_10 = VG_16 (xlsx: −4 … −1.2 V, 10 mA); sense pair to Main X3, X38…X52 (INA241A3); drain `VD` 22 V from a supply that is NOT IN CAD (xlsx row 59: 18–22 V, 2 000 mA, "Set VD +22 V"); drain enable `EN/DIS_RFPA_VDD` on Main JP10 (STM32 PD6, `main.cpp:1601`) to a switch that is NOT IN CAD.

## 7.2 Schematic sheet

![F7.1 — RF PA schematic, single sheet: QPA2962, SMA in/out, VG and VD/VIN_M decoupling, 5 mΩ sense shunt, 22 V terminal (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/RF_PA/png/RF_PA_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/RF_PA/png/RF_PA_schematic_sheet1.png)

## 7.3 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 9.6.2)

| Item | Finding (source: `docs/PCB/RF_PA.md` §2) |
|---|---|
| Routing | complete (0 airwires) |
| DRC/ERC | 0 approved entries; sch/brd consistent |
| Min track | 0.204 mm (50 Ω microstrip width of the PCBWay note) |
| DRU | mdWireWire 0.15, mdCopperDimension 0.3, msDrill 0.15 mm; `mtCopper` third slot 0.07 mm (70 µm) although slot 3 is not an active layer — interpretation UNRESOLVED; `mtIsolate` 0.11 / 1.2 / 0.36 … mm |
| Stack-up | 4 layers; `Stack_Hybrid.png` (6 layers) does not describe this board; no vendor stack-up → UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION |
| Thermal | 215 × 0.35 mm vias under/around the PA: thermal path to the enclosure/heatsink is undocumented (no mechanical data) |
| System fit | 16 PA boards at 10 W each; xlsx budgets +22 V / 2 A × 16; the Power Board has no 22 V rail — PA supply UNRESOLVED |

### Engineering conversion (`engineering/PCB/RF_PA/`)

Cross-check (source: `engineering/PCB/RF_PA/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 35.0 | 35.0 | OK |  |
| Height (mm) | 60.0 | 60.0 | OK |  |
| Footprints = EAGLE elements + free holes | 32 | 32 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 342 | 342 | OK |  |
| Tracks (signal wires excl. airwires) | 77 | 77 | OK |  |
| Copper layers | 4 | 4 | OK |  |
| NPTH holes (free holes + package holes) | 7 | 7 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 357 | 357 | OK |  |

DRC on the conversion: 48 violations, 1 unconnected (source: `engineering/PCB/RF_PA/README.md` §6):

| Rule | Count | Interpretation |
|---|---|---|
| `clearance` | 16 | copper clearance < DRU — review |
| `zones_intersect` | 8 | overlapping pours of different priority — conversion artefact or design issue |
| `silk_overlap` | 8 | overlapping silkscreen texts/lines — cosmetic |
| `silk_over_copper` | 8 | silk over exposed copper — cosmetic/assembly |
| `shorting_items` | 7 | copper of different nets touching after conversion (typically EAGLE polygon vs unnamed copper) — REVIEW in EAGLE |
| `silk_edge_clearance` | 1 | silk too close to edge |

### BETA board (`beta/pcb/RF_PA/`)

Before/after (source: `beta/pcb/RF_PA/README.md` §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 1 | 0 |
| clearance | 16 | 1 |
| shorting_items | 7 | 0 |
| silk_edge_clearance | 1 | 1 |
| silk_over_copper | 8 | 8 |
| silk_overlap | 8 | 8 |
| zones_intersect | 8 | 0 |
| **DRC violations total** | 48 | 18 |

Changes, nothing in the netlist (source: `beta/pcb/RF_PA/README.md` §2): (1) GND strap F.Cu 0.5 mm from the via at (16.20, −11.20) to the QPA2962 ground-paddle centre (16.20, −13.40) — the only unconnected item: the paddle was connected to the GND via field only through a net-less footprint polygon, which KiCad does not count as copper of the net; (2) the U$1 paddle polygon re-created as a board-level copper polygon with net GND, identical geometry (it touched 21 GND items and nothing else; as a net-less graphic it produced 7 shorting + 19 hole-clearance + 15 clearance false errors); (3) 6 overlapping same-net GND zones given distinct priorities; (4) refill, DRC, export. RF tracks (`N$2`, `N$8` at 0.204 mm) and bias lines were **not** touched.

Remaining 18 items (same source §3): 1 clearance — GND paddle polygon ↔ `VIN_M` track stub at (17.46, −15.63): 0.123 mm < 0.15 mm DRU, exists in the source → designer to confirm or nudge the VIN_M stub; 8 silk_overlap (`VIN+`/`VIN−` texts over the X3 outline, UNK22V0 texts) and 8 silk_over_copper (X2/X3 outlines over THT pads, J1/J2/U$1 silk on mask-defined areas) — cosmetic; 1 silk_edge_clearance (UNK22V0 reference 0.1 mm from the edge) — cosmetic.

## 7.4 Layer plots and 3-D renders

![F7.2a — RF PA top composite (F.Cu + F.SilkS + Edge.Cuts), 35 × 60 mm: 0.204 mm RF microstrips J1 → U$1 → J2 and the thermal-via field under the PA (status: SOURCE-DERIVED; source: engineering/PCB/RF_PA/svg/RF_PA_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/RF_PA_top_composite.png)

![F7.2b — RF PA bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts) (status: SOURCE-DERIVED; source: engineering/PCB/RF_PA/svg/RF_PA_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/RF_PA_bottom_composite_mirrored.png)

![F7.3a — RF PA 3-D render, top, KiCad conversion; no component models (status: SOURCE-DERIVED; source: engineering/PCB/RF_PA/3d/RF_PA_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/RF_PA/3d/RF_PA_render_top.png)

![F7.3b — RF PA BETA board, isometric render (GND strap and paddle polygon net added, RF copper unchanged) (status: BETA; source: beta/pcb/RF_PA/exports/3d/RF_PA_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/RF_PA/exports/3d/RF_PA_render_isometric.png)

The generated assembly-drawing PDFs are clipped by the A4 page frame (chapter 4 §4.5) and are not used as figures.

## 7.5 Stack-up

Source DRU `PCBWay_4L_100um-Track`, layerSetup `(1+2*15+16)` (source: `engineering/PCB/RF_PA/STACKUP.md`, status PARTIAL):

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 0.11mm |
| 2 | 2 | In1.Cu | 0.035mm | 1.2mm |
| 3 | 15 | In2.Cu | 0.035mm | 0.11mm |
| 4 | 16 | B.Cu | 0.035mm | — |

PROPOSED fabrication note (source: `beta/pcb/RF_PA/FAB_NOTES.md` §2–§4): F.Cu on **RO4350B 4 mil** (DRU 0.11 mm vs. note 0.102 mm), FR-4 core 1.2 mm, prepreg 0.11 mm (RO4350B only if bottom RF existed — none routed on B.Cu); finished **1.6 mm ± 10 %** (DRU sum 1.42 mm + copper ≈ 1.56 mm); the QPA2962 ground paddle carries 21 GND vias 0.35/0.15 mm — PROPOSED via-in-pad, filled and capped, because the paddle is a solder surface (designer/fab to confirm); 50 Ω ± 10 % on `N$2`/`N$8` at w = 0.204 mm (2 segments each, same geometry as the impedance note); bias nets `VIN_M`, `VD`, `VG` 0.37 / 0.6 / 0.8 / 2.0 mm DC. ENIG, maskless RF traces, min track/space 0.10/0.15 mm, min drill 0.15 mm, IPC-A-600 Class 2 — all PROPOSED. The fab drawing may carry the text of the PCBWay impedance note only after the designer confirms it applies to this 4-layer stack (source: `docs/PCB/RF_PA.md` §5).

## 7.6 Thermal budget and drain gating (DSN-THM-01, PROPOSED DESIGN)

First-order estimates from `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` (generator `tools/design_thermal.py`, inputs `engineering/DESIGN/design_parameters.json`, decisions D-10, D-11, D-14; no measurement).

Duty cycle from the firmware timing (`main.cpp:180-186`; source: §1 of the thermal note):

| Quantity | Value |
|---|---|
| TX time per beam position | 16 × 30 µs + 16 × 0.5 µs = **488.0 µs** |
| Frame per beam position | 16 × 167 + 175.4 + 16 × 175 = **5647.4 µs** |
| RF duty | **8.64 %** |
| Drain-gate duty (switch on 5 µs around each chirp, assumption) | **11.47 %** |

Dissipation per QPA2962 (datasheet: VD 22 V, IDQ 1.68 A, PSAT 40 dBm, PAE 22 %; source: §2): quiescent, no RF — 37.0 W DC / **37.0 W** dissipated; at PSAT (PIN 27 dBm) — 43.2 W / 33.7 W; design value while the drain is on — **37.0 W**.

System cases, 16 PAs (source: §3):

| Case | Total PA dissipation | Verdict |
|---|---|---|
| A continuous drain bias (firmware as coded: VD left on) | **591 W** | INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ 142 CFM at ΔT_air 12 K) |
| B drain gated per chirp (D-14), duty 11.5 % | **68 W** | design case |
| C drain gated per CPI frame only (on during the 5.6 ms frame, off while the stepper moves) | **532 W** | INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ 142 CFM at ΔT_air 12 K) |

Conclusion (D-10/D-14, source: §3): the firmware as coded (VD left on after bias-up, `main.cpp:1560-1601`) puts the head in case A; the proposal therefore requires per-chirp drain gating — a hardware function of the 22 V switch module driven by a timing line — after which the thermal design is case B at **68 W** average.

Heat path, case B (source: §4): 4.24 W average per PA; R(PA board thermal-via field) 1.5 °C/W — **ASSUMPTION, the RF_PA stack-up and via field under U$1 must be checked**; R(TIM) + spreading 0.3 + 0.2 °C/W (assumption, thermal pad 1–3 W/mK, 5 × 5 mm); ΔT PA base → plate 8.5 °C; plate ≤ 77 °C for TBASE ≤ 85 °C; required plate-to-air resistance ≤ **0.46 °C/W** at 45 °C ambient; heat spreader (D-11) 300 × 300 × 10 mm Al with PAs 4 × 4 on the rear centre; two fin fields 55 × 280 mm, 26 fins 25 × 2 mm at 4 mm pitch, 0.39 m²; R(lateral spreading) 0.09 °C/W, R(fins → air, h = 25 W/m²K ASSUMPTION) 0.10 °C/W; resulting plate / PA base **58 °C / 66 °C** at 45 °C ambient (margin 19 °C); airflow **16 CFM** (7.7 L/s) → 2 × 60 mm fans (≥ 15 CFM each) controlled by the existing fan relay. Not included: Power Board regulator losses (currents UNKNOWN), Main Board (≈ 10–20 W estimate), solar load — add 30 % margin when selecting the fans.

22 V drain supply sizing (D-14, source: §5; the block schematic, netlist and BOM are DSN-PSU-01 in chapter 9): peak drain current all 16 PAs at ID_max 2.848 A = **45.6 A** during each 30 µs chirp; average case B **3.47 A** → 76 W (case A 27.3 A → 600 W, not supported); bulk capacitance **2734 µF** total for ΔV ≤ 0.5 V over a chirp → ≥ 220 µF low-ESR polymer per PA board (171 µF each) + 2 × 1000 µF/35 V at the switch module; input 6.9 A average at 12 V, η 92 %; per-PA pulse gating 16 × high-side P-FET (−40 V, 30 A pulsed) with fast driver (e.g. LTC7003), common `TX_GATE` TTL input from the FPGA — **spare I/O to be allocated, UNRESOLVED**; sequencing VG (−4 V via DAC5578) before VD (firmware already does this), gate switch only after `EN/DIS_RFPA_VDD`, power-down in reverse.

Consequence for this board: the "≥ 220 µF low-ESR polymer per PA board" of the proposal is not on the RF_PA schematic (which has 3 × 10 µF + 6 × 0.1 µF); whether it is added on a rev. B of this board or at the switch module is an open decision under D-14.

## 7.7 BOM summary

Source BOM `docs/BOM/BOM_RF_PA.csv`: 25 references, 11 line items, 0 MPN attributes, 6 references without value (source: `docs/BOM/README.md`). BETA confidence, counted with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/RF_PA/BOM_RF_PA_beta.csv'))))"`:

| mpn_confidence | Lines | Quantity (source: `beta/pcb/README.md`) |
|---|---|---|
| HIGH | 5 | 6 |
| MEDIUM | 6 | 19 |
| LOW | 0 | 0 |
| EMPTY | 0 | 0 |
| **Total** | **11** | 25 |

Before purchase (source: `docs/PCB/RF_PA.md` §8): enter the QPA2962 orderable part number (package suffix); gate-bias network values consistent with the DAC5578-driven `VG` range (−4 … −1.2 V per `Power Management V6.xlsx`); the 5 mΩ shunt vs 0.1 Ω MPN conflict flagged in the BETA `note` column (source: `beta/pcb/README.md`). Multiply all quantities by 16 for the AERIS-10X variant.

## 7.8 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K4 | 22 V drain supply and drain switch not in CAD; DSN-PSU-01 proposal (chapter 9) | OPEN — power designer | `docs/SYSTEM/BLOCK_DIAGRAM.md` |
| D-14 | `TX_GATE` timing line — spare FPGA I/O not allocated | UNRESOLVED | `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5 |
| G-12 | Keep-out zones around the RF connectors and the QPA2962 | BLOCKED | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` |
| — | Stack-up 4-layer construction, outer dielectric, 70 µm DRU slot, 50 Ω width confirmation | BLOCKED — MISSING DATA | `docs/PCB/RF_PA.md` §7; MDR-07 |
| — | PA mounting (7 × Ø3.2 mm NPTH), heatsink contact, via-field thermal resistance (1.5 °C/W ASSUMPTION) | OPEN — mechanical/thermal | `docs/PCB/RF_PA.md` §7; thermal note §4 |
| — | Which SMA of each Main Board pair is RFIN/RFOUT; PA n ↔ antenna row n assignment | UNVERIFIED / PROPOSED | `interconnection_table.md` §7; `HARNESS_SCHEDULE.md` |
| — | 1 clearance 0.123 mm (`VIN_M` stub) in the source | OPEN — designer | `beta/pcb/RF_PA/README.md` §3 |
| — | Local 220 µF bulk capacitance per PA board (D-14) not on the schematic | OPEN | this chapter §7.6 |
| — | BOM: QPA2962 MPN, 6 value-less references, shunt MPN conflict | OPEN | `docs/PCB/RF_PA.md` §8 |
| — | RF performance (gain, P1dB at 10.5 GHz) | unverified until measured | `docs/PCB/RF_PA.md` §10 |
