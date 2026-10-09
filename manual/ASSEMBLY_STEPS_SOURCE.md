# Assembly and integration steps — consolidated source for chapter 15/16

Sources: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` (electrical order, checkpoints), `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (parts #, fasteners), `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-04…07`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` (CBL-IDs, lengths), `engineering/SYSTEM/interfaces/interconnection_table.md` (pins), `engineering/ELECTRICAL/power_distribution/power_rails.md` §3 (power sequence), `beta/stm32/README.md` (flash/bring-up), `beta/fpga/README.md` (programming, calibration registers), `beta/gui/README.md`. Status of the whole procedure: **PROPOSED / BETA — never executed**. ⚠ marks steps that depend on an open decision.

## Safety preamble
S1 22 V PA drain supply (up to 45 A pulsed): never connect PA boards with VG at 0 V; VG −4 V first (firmware sequence). S2 RF: no transmission without a terminated or connected antenna/PA path; 16 × 10 W peak. S3 Rotating pedestal: keep hands clear; stepper driver current limit set before first motion. S4 ESD: all boards are ESD-sensitive (GaN, ADC, FPGA).

## Phase A — PCB assemblies (per board)
| Step | Action | Parts / tools | Check | Figure |
|---|---|---|---|---|
| A1 | Inspect bare boards against outline and hole tables | `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md` | dimensions ±0.2 mm; hole count | DSN-MECH plan view |
| A2 | Populate per BOM and pick-and-place (beta BOM with MPN confidence) | `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`, `exports/pos` | every reference populated; polarity per assembly drawing | `<BOARD>_assembly_top.pdf` |
| A3 | Rail-to-GND resistance before power | DMM | > 1 kΩ on every rail (list in `power_rails.md`) | — |
| A4 | Power Board alone on bench PSU 12–17 V | PSU, DMM | each X2..X35 output at nominal with no load; ⚠ U30 ADM7151 input from VIN (review) | F3.2 |

## Phase B — Mechanical assembly of the head (parts # from MECHANICAL_PARTS_LIST)
| Step | Action | Parts / fasteners | Check | Figure |
|---|---|---|---|---|
| B1 | Fit PEM nuts in the tray flanges; fit lid gasket and front gasket | tray #1, PEM S-M4 ×38, EPDM | gasket continuous, no gaps at corners | DSN-MECH-06 |
| B2 | Mount PA heat-spreader brackets to the tray sides; set the plate at y = 11 mm from the front flange plane | brackets #10, M5 | plate square to the base ±0.5 mm; front face flush for the antenna | DSN-MECH-07 |
| B3 | Mount 16 PA boards on the plate rear with thermal pads 5×5 under each QPA2962 | PA boards, pads, M3×6 ×112 | torque 0.5 N·m; pads centred; board numbering PA1…PA16 per DSN-MECH-04 | DSN-MECH-04 tier 1 |
| B4 | Mount the antenna panel on the plate front on 2.4 mm spacers | antenna PCB, M3×6 ×6, spacers | row 1 at the bottom; connectors on the left edge accessible | DSN-MECH-02 |
| B5 | Fit carrier rails for the Main tier (y = 56) with standoffs; mount Main Board vertically, components to the rear | rails #12, standoffs M3×10, M4×8 | connector field positions match DSN-MECH-04 tier 2 | DSN-MECH-04 |
| B6 | Fit Synth tier (y = 81) and Power tier (y = 106) the same way | rails, standoffs | — | DSN-MECH-04 |
| B7 | Mount the 22 V PA supply/gate module on the rear wall (⚠ D-14: module not built; `TX_GATE` pin undecided) | DSN-PSU-01 | — | DSN-MECH-01 |
| B8 | Fit 2 × 60 mm fans at the duct intakes; gland plate with M32/M20 glands under the base | fans, gland plate #15, M4 | airflow direction bottom → top | DSN-MECH-01/03 |
| B9 | Fit the front plate with PTFE window, gasket and clamp frame | front plate #2, window #5, gasket #6, frame #7, M3×10 ×18 | window flat; gasket compressed evenly | DSN-MECH-07 |

## Phase C — Harness (lengths from HARNESS_SCHEDULE, pin order ⚠ UNVERIFIED for Molex `S` pads)
| Step | Action | Cables | Check |
|---|---|---|---|
| C1 | Enable bus SV1↔SV1 ribbon (20-way) | CBL enable bus | pin 1 orientation both ends |
| C2 | Rail cables Power → Main / Synth (2-pin Molex) — buzz out polarity before mating | CBL-001…(rail list) | continuity + polarity per `power_rails.md` |
| C3 | Synth ↔ Main control headers JP1↔JP1, JP2↔JP13 and coax clocks/LO (J7→J1, J5→J20, J6→J18, J3→J21, J10→J23, J11→J22) | CBL coax set 1 | SMA torque 0.9 N·m; labels |
| C4 | PA harness: VG (Main X_k → PA n X2), sense (Main X3/X38.. → PA X3), RF pairs (Main J-pairs → PA J1/J2 ⚠ RFIN/RFOUT side UNVERIFIED), PA RFOUT → antenna row n (equal-length set) | CBL-0xx per table | equal length within ±2 mm on the 16 antenna coax; labels PA1…16 |
| C5 | 22 V drain leads to each PA `22V` terminal (⚠ K4) | 18 AWG twisted | polarity; torque of AK300/2 |
| C6 | Slip-ring harness: VIN, 22 V, USB through the base gland to the pedestal | 16 AWG, USB | continuity after rotation of the turntable 360° |

## Phase D — Pedestal
| Step | Action | Parts | Check |
|---|---|---|---|
| D1 | Bolt the slewing bearing to the pedestal top plate (12 × M6) and the turntable to the bearing outer ring (12 × M6); fit the ring pulley | #16–#18 | turntable runs freely, axial play < 0.1 mm |
| D2 | Mount stepper + bracket, motor pulley, GT3 belt; tension; TB6600 on DIN rail; ⚠ D-12: NEMA 23 needs ≥ 200 ms per step — set motor class/ratio first | #motor, bracket | belt deflection; driver current limit set |
| D3 | Fit slip ring stator bracket; route harness; mast flange ⚠ (interface undefined) | #20–#22 | rotor turns with the turntable without cable strain |
| D4 | Bolt the head base to the turntable (8 × M6) with the Ø70 passage aligned | — | head square to the turntable |

## Phase E — Bring-up (bench, head open, pedestal stationary)
| Step | Action | Check |
|---|---|---|
| E1 | Flash the STM32 beta image via SWD (`beta/stm32/build_out/aeris10_fw.elf`) ⚠ K2 (8 MHz HSE assumed in beta) | USART3 banner; CDC enumerates (VID/PID placeholder) |
| E2 | Observe the power-enable sequence F0–F10 on a scope (rails appear in order; delays) | matches `power_rails.md` §3 |
| E3 | Program the FPGA via JP3 JTAG with the Vivado-built bitstream ⚠ (not available: beta is simulation-only; open-source flow see `beta/fpga_synth`) ⚠ K1 part | DONE pin; STM32↔FPGA handshake DIG_0..4 toggles |
| E4 | AD9523 lock and output frequencies (100 / 120 / 400 MHz) on a counter | ± 1 ppm |
| E5 | ADC capture calibration: GUI register panel → auto (pattern, needs ADC test pattern ⚠ SPI unwired) or blind method; check lock mask 0xFF and error counter 0 | `CAL_STAT` registers |
| E6 | PA bias-up one board at a time: VG −4 V → VD 22 V → VG to IDQ 1.68 A; read INA241 current in the GUI status | IDQ within ±10 %; plate temperature < 70 °C after 10 min with drain gating |
| E7 | Host link: `--demo` self-test passes; with hardware, bridge frames arrive (seq increments, CRC errors 0) | GUI status bar |
| E8 | Beam steering: write phase tables (firmware), verify ADAR1000 SPI traffic on the 1.8 V side | logic analyser |
| E9 | First RF test into a dummy load / anechoic setup; then antenna | spectrum at 10.5 GHz, pulse envelope 30 µs |
| E10 | Close the lid; pedestal rotation test 50 positions; log scan time | ≈ 19 s per revolution (NEMA 23, 200 ms steps) |

Acceptance criteria: `docs/TESTING/ACCEPTANCE_CRITERIA.md` (AC-F*, AC-S*, AC-P*, AC-B*, AC-M*, AC-E*, AC-X*).
