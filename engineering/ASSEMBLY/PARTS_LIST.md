# AERIS-10 — Assembly parts list (system level)

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Document | ASM-PL-01 |
| Revision | A |
| Date | 2026-10-09 |
| Status | **PARTIAL** — PCB assemblies are SOURCE-DERIVED (EAGLE schematics); every mechanical/off-board item is BLOCKED — MISSING DATA (no part numbers or CAD in the repository) |
| Balloons | numbers match `EXPLODED_VIEWS/aeris10_exploded_conceptual.svg` |

Per-board bills of materials (reference designators, values, quantities; 0 manufacturer part numbers in the source) are in `docs/BOM/` and copied as `engineering/PCB/<BOARD>/assembly/<BOARD>_BOM.csv`.

## 1. Printed-circuit assemblies

| Balloon | Item | Qty per system | Qty basis (evidence) | BOM lines / references | Drawing package | Status |
|---|---|---|---|---|---|---|
| 1 | Power Supply Board, 280 × 300 mm, 2 Cu | 1 | one `PowerBoard.sch`; its SV1/X2..X35 feed one Main + one Synth board (`engineering/SYSTEM/interfaces/interconnection_table.md` §2–4) | 28 / 312 | `engineering/PCB/POWER_SUPPLY/` | PARTIAL — layout unfinished (309 airwires, 308 unconnected after fill) |
| 2 | Main Board, 260 × 300 mm, 10 Cu | 1 | one `RADAR_Main_Board.sch` (U42 FPGA, U2 STM32) | 98 / 776 | `engineering/PCB/MAIN_BOARD/` | PARTIAL — 2 390 EAGLE airwires (15 unconnected after KiCad pour fill); FT601 U6 unconnected |
| 3 | Frequency Synthesizer Board, 100 × 100 mm, 6 Cu | 1 | one `Clocks_Freq_Synth_board.sch`; JP1/JP2 ↔ Main JP1/JP13 | 40 / 184 | `engineering/PCB/FREQUENCY_SYNTHESIZER/` | SOURCE-DERIVED — routed; existing P&P + BOM xlsx in `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/` |
| 4 | RF PA board (QPA2962), 35 × 60 mm, 4 Cu | 16 | Main Board provides 16 VG outputs X_1..X_16, 16 current-sense inputs X3/X38..X52 and 16 SMA pairs J24..J55 (`interconnection_table.md` §7) | 11 / 25 (each) | `engineering/PCB/RF_PA/` | SOURCE-DERIVED — routed; PA-instance ↔ Main-connector mapping UNDOCUMENTED |

## 2. Off-board electrical items (named in the sources, no part numbers)

| Balloon | Item | Qty | Evidence | Status |
|---|---|---|---|---|
| 5 | Antenna array, 16 elements, λ/2 = 14.3 mm, aperture 214.3 mm | 1 | `02_hardware/04_antenna_beamforming.md:280,288`; `8_Utils/Antenna_Array.jpg` (photo, undimensioned); two contradictory waveguide simulations in `5_Simulations` | BLOCKED — no CAD, no feed-network design |
| 6 | Host computer with Python GUI (USB CDC) | 1 | `GUI_V5.py`, Main Board X53 mini-USB (STM32 OTG-FS) | CONCEPTUAL (any PC; no spec) |
| — | 22 V PA drain supply + `EN/DIS_RFPA_VDD` switch | 1 | `RF_PA.sch` `22V` terminal AK300/2; `main.cpp:1560-1601`; not on any schematic (conflict K4) | BLOCKED — MISSING DATA |
| — | DC input source 12–17 V (VIN) | 1 | `PowerBoard.sch` X1, `Power Management V6.xlsx` | BLOCKED — current budget unknown |
| — | GPS module (UART5), IMU GY-85 (I2C3), barometer BMP180 (I2C3) | 1 each | `main.cpp` (`gps_handler.cpp`, GY-85/BMP180 drivers); `Power Management V6.xlsx` names | PARTIAL — module type from firmware only, no P/N, no mounting |
| — | Temperature sensors TMP37 ×8 | 8 | `main.cpp` ADS7830 channels / `docs/BOM/README.md` | PARTIAL |
| — | Stepper motor (200 steps/rev) + driver (TB6600-class), slip ring | 1 + 1 + 1 | `main.cpp:189,195` + pin macros; xlsx names | BLOCKED — no P/N, no mechanics |
| — | Fans, heatsinks (QPA2962 dissipation ≈ 22 V × 1.68 A per PA) | ? | xlsx L58-L62 (IDQ 1 680 mA) | BLOCKED — thermal design absent |
| — | Cable set CBL-01…CBL-106 (power, enable bus, SMA coax, PA harness, USB) | ~106 | `interconnection_table.md` (IDs are proposals) | BLOCKED — types, lengths, gauges unspecified |

## 3. Mechanical items

| Item | Qty | Evidence | Status |
|---|---|---|---|
| Enclosure / chassis | 1 | README references `10_docs/Hardware/Enclosure` (does not exist) | BLOCKED — MISSING DATA |
| Pedestal / azimuth drive (stepper, slip ring) | 1 | firmware only | BLOCKED |
| PCB fasteners | Main 10 holes, Power 8, Synth 4, PA 7 × 16 (Ø 3.2 mm holes → M3 hardware **inferred**, not specified) | `engineering/MECHANICAL/dimensions/*_dimensions.md` | PARTIAL — hole pattern verified, hardware unspecified |
| Stand-offs, thermal interface, RF absorber, antenna radome | ? | none | BLOCKED |

## 4. Software/firmware items delivered with the assembly

| Item | Evidence | Status |
|---|---|---|
| FPGA bitstream (XC7A50T-2FTG256I per CAD) | `9_Firmware/9_2_FPGA/` — RTL does not build | MISSING |
| STM32F746 firmware image | `9_Firmware/9_1_Microcontroller/` — no build system/HAL | MISSING |
| Python GUI package | `9_Firmware/9_3_GUI/` + `requirements.txt` | PARTIAL (V6 stub; V5 complete; demo runs) |
