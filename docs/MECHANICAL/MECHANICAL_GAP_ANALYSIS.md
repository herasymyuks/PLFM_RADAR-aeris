# Mechanical Gap Analysis — AERIS-10

Status date 2026-10-08. Evidence: repository-wide file search (`find` by extension), EAGLE `.brd` parsing (`tools/gen_board_outline_svg.py`), documentation grep, Word/draw.io text extraction. No dimension in this document was invented; every number has a file source.

> **Update 2026-10-09:** mechanical artefacts generated from the PCB geometry (DXF, STEP bodies, 1:1 plan view, dimension sheets with hole tables and mass ESTIMATES), the CONCEPTUAL exploded view, parts list and assembly sequence are in `engineering/MECHANICAL/` and `engineering/ASSEMBLY/`; the unresolved geometry register is `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`; reconstruction guides for enclosure/antenna/pedestal/cooling drawings are MDR-01…MDR-05 in `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`.

## 1. Mechanical source files found

| Path | Type | What it is | Mechanical value |
|---|---|---|---|
| `2_Functional Diagram & Interconnection Matrices/Functional_Diagram.dwg` | AutoCAD DWG (header `AC1027`, AutoCAD 2013–2017) | functional block diagram | none (not a drawing of a part) |
| `5_Simulations/Sim_BPF_Te_100um/Drawing1.dxf` (+ `.bak`) | DXF (`AC1032`) | 2-D layout of the simulated microstrip band-pass filter (7 MLIN + 2 MTEE from the Qucs netlist); units unverified | filter geometry only |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.gds` | GDSII | same filter | same |
| `4_Schematics and Boards Layout/4_6_Schematics/*/*.brd` | EAGLE board | PCB outlines, mounting holes | **the only verified mechanical data** (section 3) |
| `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` (and identical copy under `4_Schematics and Boards Layout/4_6_Schematics/Stack_Hybrid.png`) | 252 × 298 px raster | 6-layer stack table: Cu 0.035 / RO4350B 0.102 / Cu / prepreg 0.100 / Cu / FR-4 0.100 / Cu / prepreg 0.100 / Cu / RO4350B 0.102 / Cu (read from the image) | board thickness ≈ 0.714 mm **derived**, board unidentified |

**Not found anywhere** (searched `STEP/STP/STL/IGES/IGS/F3D/SLDPRT/SLDASM/OBJ/3MF/SCAD/FCStd`, case-insensitive): enclosure model, antenna array model (patch or slotted waveguide), pedestal/azimuth drive, slip-ring mount, fan ducting, cable routing, exploded views, assembly photos with dimensions.

## 2. Referenced-but-missing paths

| Reference | Location | Status |
|---|---|---|
| `/10_docs/assembly_guide.md` ("Follow the assembly guide") | `README.md:141` | **directory `10_docs/` does not exist** |
| `/10_docs/Hardware/Enclosure` ("3D printable files") | `README.md:143` | **does not exist** |
| "All Gerber files are available in `/4_Schematics and Boards Layout`" | `README.md:139` | false — no Gerbers (`docs/PCB/*.md`) |
| "Bill of materials (BOM) in `/4_7_Production Files`" | `README.md:140` | true only for the Frequency Synthesizer, without MPNs |

## 3. Dimensions that CAN be established (from EAGLE layer 20 outline and NPTH holes; drawings in `docs/MECHANICAL/drawings/`)

| Board | Outline (mm) | Mounting holes (NPTH, Ø mm) and positions (mm, from board origin) | Copper layers | Drawing |
|---|---|---|---|---|
| Main Board | **260.00 × 300.00** | 8 × Ø3.2 at (4,4) (256,4) (256,296) (4,296) (256,250) (256,114) (116,114) (116,250); 2 × Ø0.9 at (0,±2.2) (inside packages) | 10 (EAGLE) | `MAIN_BOARD_outline.svg` |
| Power Supply | **280.00 × 300.00** (outline); holes within 10..270 × 10..230 (+1 at y 267.85) → final outline **UNRESOLVED** | 8 × Ø3.2 at (10,10) (270,10) (270,230) (10,230) (138.45,267.85) (140,10) (270,120) (10,120) | 2 | `POWER_SUPPLY_outline.svg` |
| RF PA | **35.00 × 60.00** | 7 × Ø3.2 at (2.6,2.6) (2.6,57.4) (32.4,57.4) (32.4,2.6) (17.5,2.6) (2.6,38) (32.4,38) | 4 | `RF_PA_outline.svg` |
| Frequency Synthesizer | **100.00 × 100.00** | 4 × Ø3.2 at (5,5) (95,5) (95,95) (5,95) | 6 | `FREQUENCY_SYNTHESIZER_outline.svg` |

Also verifiable from the boards: connector positions (SMA edge-launch 142-0731-211: 37 on Main, 11 on Synth, 2 on PA; Molex 22-23-20xx headers) — extractable with `tools/extract_eagle_netlist.py --list-parts` plus the `.brd` element coordinates (not tabulated here). Component heights are **not** in the files (no `HEIGHT` attributes populated).

## 4. Dimensions that are NOT available (and where the gap is stated)

| Item | Status | Evidence of absence |
|---|---|---|
| PCB thickness per board | UNRESOLVED | EAGLE `mtIsolate` tables disagree with `Stack_Hybrid.png` and the PCBWay note (`docs/PCB/*.md` §2) |
| Enclosure: dimensions, material, wall thickness, IP rating, mounting, weight | MISSING | word "enclosure" appears only at `README.md:89,143` and `research/03_hw_improvements.md:997` (hypothetical 443 mm aperture) |
| Antenna array geometry | PARTIAL, CONTRADICTORY | element spacing d = λ/2 ≈ 14.3 mm, 16-element aperture 214.3 mm (`02_hardware/04_antenna_beamforming.md:280,288`); array-factor script uses dy = 14.2758 mm, dz = 16.915 mm (`5_Simulations/array_pattern_Kaiser25dB_like.py:10-13`); two incompatible slotted-waveguide designs — alumina a 8.5 × b 3.5 mm, 32 slots (`Slotted_DielectricFilled_Waveguide.m:4-33`) vs quartz 13.28 × 6.5 mm, L 281 mm (`Antenna/Quartz_Waveguide.py:31-47`, `slot_layout_taper32.csv` ±262.18 mm). No patch-array CAD or EM model. Neither design is identified as built |
| Antenna feed transition (ADTR1107 → antenna element) | UNRESOLVED | nets `ANT1_1…ANT4_4` go ADTR1107 pin 17 → 0201 capacitor → M3SWA2 switches; no SMA/MMCX/U.FL footprint found by name |
| Stepper motor model, torque, mounting | MISSING | only 200 steps/rev and 50 azimuth positions (`main.cpp:189,195`), driver "TBS6600" (`Power Management V6.xlsx`) |
| Slip ring (channels, rating, mount) | MISSING | `README.md:86`, `Project_Description.docx` mention only |
| Fans (model, size, airflow, count) | MISSING | `EN_DIS_COOLING` GPIO (`main.h:142`), 25 °C threshold (`main.cpp:1752-1775`) only; thermal load ≈ 29 W Nexus (`02_hardware/08_power_budget.md:185`) |
| Heatsinking of the PA boards (16 × up to 10 W GaN) | MISSING | no thermal analysis; `08_power_budget.md:167` "active cooling mandatory for Extended during TX" |
| Weight / centre of gravity | MISSING | no statement anywhere |
| Cable harness lengths (SMA, Molex) | MISSING | — |
| Board-to-board stacking / standoff heights | MISSING | hole patterns do not share a common pitch between boards (section 3) |

## 5. Required CAD sources to close the gaps

| Deliverable | Source needed | Owner |
|---|---|---|
| Enclosure STEP + drawings | mechanical designer (original files were never committed; README promised 3-D printable files) | hardware designer |
| Antenna array STEP + fabrication drawing (patch PCB or machined waveguide) | antenna designer; decide alumina vs quartz vs patch variant | RF/antenna designer |
| Pedestal/azimuth drive assembly (motor, bearing, slip ring) STEP | mechanical designer | — |
| PCB 3-D models (EAGLE 9: *Fusion 360 → Push to 3D*; KiCad: File → Export → STEP after import; needs component 3-D models) | regenerable from `.brd` once component models are assigned | reconstruction team |
| Thermal design (fan/heatsink selection) | needs PA dissipation and enclosure geometry | — |

## 6. How to produce drawings from verified dimensions (performed for the PCB outlines)

1. `python3 tools/gen_board_outline_svg.py <board.brd> --out docs/MECHANICAL/drawings/<BOARD>_outline.svg --title "<name>" --mark <refs>` draws the layer-20 outline, every NPTH hole (and any pad drill ≥ 2 mm), reference crosses for named components, overall dimensions and a hole table. Executed for all four boards (section 3).
2. For a full PCB outline drawing with component outlines, use EAGLE: board → Layer settings (20, 21, 25, 39/40 tKeepout, 51) → File → Print → PDF 1:1 (P-EAGLE-07), or KiCad after import: File → Fabrication Outputs → Component Placement + Plot Edge.Cuts/F.Fab.
3. Approximate mass of a bare board (**estimate only, no source value**): m ≈ A × t × ρ with ρ(FR-4/RO4350B composite with copper) ≈ 1.9–2.1 g/cm³; the thickness t is unknown (section 4), so no number is given here. The method is recorded so the designer can fill it once the stack-up is confirmed.

## 7. Open questions for the hardware designer

1. Which antenna variant exists physically (patch 8×16 or one of the two slotted-waveguide designs)? Provide its CAD and the feed interface.
2. Enclosure: does any CAD exist outside this repository? Provide STEP/STL and the mounting interface to the Main Board (8 × Ø3.2 pattern) and Power Board.
3. Power Board final outline (280 × 300 mm outline vs 260 × 220 mm hole pattern).
4. Stack-up per board (thickness needed for mass and standoff selection).
5. Stepper, slip ring, fan part numbers.
