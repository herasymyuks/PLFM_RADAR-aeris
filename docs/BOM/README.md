# Bill of Materials Package — AERIS-10

Generated 2026-10-08 by `python3 tools/gen_eagle_bom.py` directly from the EAGLE schematics (no EAGLE run). Regenerate after any schematic change:

```
S="4_Schematics and Boards Layout/4_6_Schematics"
python3 tools/gen_eagle_bom.py "$S/MainBoard/RADAR_Main_Board.sch"                        --out docs/BOM/BOM_MAIN_BOARD.csv            --refs docs/BOM/REFS_MAIN_BOARD.csv            --md docs/BOM/BOM_MAIN_BOARD.md
python3 tools/gen_eagle_bom.py "$S/PowerBoard/PowerBoard.sch"                              --out docs/BOM/BOM_POWER_SUPPLY.csv          --refs docs/BOM/REFS_POWER_SUPPLY.csv          --md docs/BOM/BOM_POWER_SUPPLY.md
python3 tools/gen_eagle_bom.py "$S/PowerAmplifierBoard/RF_PA.sch"                          --out docs/BOM/BOM_RF_PA.csv                 --refs docs/BOM/REFS_RF_PA.csv                 --md docs/BOM/BOM_RF_PA.md
python3 tools/gen_eagle_bom.py "$S/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch"  --out docs/BOM/BOM_FREQUENCY_SYNTHESIZER.csv --refs docs/BOM/REFS_FREQUENCY_SYNTHESIZER.csv --md docs/BOM/BOM_FREQUENCY_SYNTHESIZER.md
```

## What is in each file

| File | Content |
|---|---|
| `BOM_<BOARD>.csv` | grouped line items: `item, qty, value, deviceset, device, package, library, mpn_attribute, manufacturer_attribute, mpn_candidate, mpn_status, references` |
| `BOM_<BOARD>.md` | same, human-readable |
| `REFS_<BOARD>.csv` | one row per reference designator (for pick-and-place / assembly cross-check) |

## Summary

| Board | Physical references | Line items | Lines with MPN attribute | References without value | Status |
|---|---:|---:|---:|---:|---|
| Main Board | 776 | 98 | 0 | 244 | INCOMPLETE — no MPNs, FT601 (U6) unconnected but listed, 11 parts parked off-board |
| Power Supply | 312 | 28 | 0 | 80 | INCOMPLETE — no MPNs, 132 parts not placed on the board |
| RF PA | 25 | 11 | 0 | 6 | INCOMPLETE — no MPNs; `QPA2962_B` is a deviceset name |
| Frequency Synthesizer | 184 | 40 | 0 | 47 | INCOMPLETE — matches the existing `Clocks_Freq_Synth_board_BOM.xlsx` (40 lines) which also has empty MPN columns |

**`mpn_status` meaning:** `VERIFIED (attribute)` — an explicit MPN attribute exists in the schematic (none today); `UNVERIFIED (deviceset name)` — the EAGLE deviceset name looks like a part number (e.g. `ADAR1000ACCZN`, `TPS562208DDCT`) but has not been checked against a distributor; `GENERIC — value/package only` — passive to be sourced by value/package/tolerance (tolerance and voltage rating are **not** in the schematics).

## System-level items not on any PCB (from `README.md`, `Power Management V6.xlsx`, `main.cpp`) — quantities and part numbers UNKNOWN unless stated

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

## Validation procedure (BOM)

1. Regenerate with the command above; compare `qty` sum with the element count of the `.brd` (776 / 312 / 25 / 184).
2. For every `UNVERIFIED` line, look the deviceset up at a distributor and write the confirmed MPN into the schematic part attribute `MPN` (EAGLE: part → *Attributes*), then regenerate — the status becomes `VERIFIED (attribute)`.
3. Fill every empty `value` (244/80/6/47 today) in the schematic; passives also need tolerance/voltage attributes.
4. Add a `DNP` attribute for parts not populated in a given variant (FT601 and its decoupling; variant-specific PA parts).
5. Acceptance: 0 `UNVERIFIED`, 0 empty values, DNP column present, generated CSV identical in part count to the `.mnt` pick-and-place.
