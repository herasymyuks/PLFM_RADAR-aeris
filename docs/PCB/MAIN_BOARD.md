# Main Board — Manufacturing Readiness Report

Board: `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` / `.brd` (EAGLE **7.4.0**, both). Status date 2026-10-08. Method: XML inspection (`tools/extract_eagle_netlist.py`, `tools/gen_eagle_bom.py`, `tools/gen_board_outline_svg.py`, scratch analysers); no EAGLE run. **Readiness verdict: NOT FABRICATION-READY** — the layout is unfinished (stored airwires, parts outside the outline, 211 approved DRC errors), the USB 3.0 chip is unconnected, and no production outputs exist.

> **Update 2026-10-09:** a generated manufacturing & drawing package (KiCad 10 conversion of the EAGLE board: Gerber, drill, PDF/SVG layer and assembly drawings, DXF, STEP, P&P, BOM, IPC-2581, IPC-D-356, DRC with DRU-derived rules, 3-D renders) is in `engineering/PCB/MAIN_BOARD/` (see its `README.md`, `STACKUP.md`). Schematic PDF/SVG: `engineering/ELECTRICAL/schematics/MAIN_BOARD/`. Netlist and connection reports: `engineering/ELECTRICAL/netlists/`. The package is SOURCE-DERIVED/PARTIAL, not designer-released; the EAGLE procedures below remain the path to the authoritative export.

## 1. Source-file inventory

| File | Size | Content (verified) |
|---|---|---|
| `RADAR_Main_Board.sch` | 2 726 023 B | 4 sheets: *POWER SUPPLIES*, *Digital (FPGA+microcontroller)*, *RF*, *RF POWER AMPLIFIER BIAS*; 1 955 `<part>` of which 776 physical; 625 nets; 18 embedded libraries (`My_Library`, `My_Library_RADAR`, `My_Library_2`, `XC7A50T-2FTG256I`, `rcl`, `eagle-ltspice`, connectors…) |
| `RADAR_Main_Board.brd` | 2 426 122 B | 776 elements (all top side), 635 signals, 12 609 wires (2 390 are airwires), 2 893 vias, outline **260 × 300 mm**, 10 copper layers (`layerSetup=(1*2+3*4+5*12+13*14+15*16)`), DRU `PCBWay_8L_100um-Track` |
| `docs/BOM/BOM_MAIN_BOARD.csv`, `docs/BOM/BOM_MAIN_BOARD.md`, `REFS_MAIN_BOARD.csv` | generated | 776 references, 98 line items, 0 MPN attributes, 244 references without value |
| `docs/MECHANICAL/drawings/MAIN_BOARD_outline.svg` | generated | outline + 8 × Ø3.2 mm NPTH at (4,4) (256,4) (256,296) (4,296) (256,250) (256,114) (116,114) (116,250) + 2 × Ø0.9 |

Key ICs (deviceset names from the schematic; MPN status UNVERIFIED): XC7A50T-2FTG256I (U42), STM32F746ZGT7 (U2), AD9484BCPZ-500 (U1), AD9708AR (U3), ADAR1000ACCZN ×4, ADTR1107ACCZ ×16, LTC5552IUDBTRMPBF ×2 (U5, U13), AD8352ACPZ-R7 ×2, M3SWA2-34DR+ ×17, INA241A3IDGKR ×16, ADS7830IPWR ×3, DAC5578SRGET ×2, OPA4703EA/250 ×4, MT25QL01GBBB8E12 (U9, config flash), EP4RKU+ (U16), FT601Q-B-T (U6, **0 of 77 pins connected**), NX3225GD-8MHZ ×2 (XTAL1 STM32 HSE — see STM32 C1), 37 × SMA 142-0731-211, 56 × Molex 22-23-20xx, mini-USB X53.

Absent from the schematic although present in `7_Components Datasheets`: FT2232H, FT232RN, MAX20029, STUW81300, QPM1021, QPA1013, TGA2623.

## 2. Layout state and defects (evidence)

| Item | Finding |
|---|---|
| Airwires | 2 390 stored on layer 19: GND 2 354, +3V3_FPGA 33, +3V3_FT 3 (entirely unrouted). GND has polygons on layers 2, 5, 13, 15 — whether `RATSNEST` clears the GND airwires **REQUIRES VERIFICATION IN EAGLE** |
| Parts outside outline | 11: C159, C184, C185, C186, L19 (FT601 decoupling), R60, R61, R83, R84, R145, R146 (parked at x = 0.1 mm, y < 0) |
| DRC | 211 `<approved>` entries (hash types 19 ×172, 5 ×39; EAGLE stores no text) |
| ERC | 4 approved entries on net `STM32_MISO_1V8` |
| Board-only signals | 10 (`AVDD, VBUS, VCC33, VCC33_2, VCC33_3, VCCIO, VCCIO_2..4, VDDA`) — FT601 supply pin names with contact refs only, stale forward-annotation residue |
| Single-pin nets | `N$44` (AD9484 CML), `EN_OPAMP_IF_1`, `EN_OPAMP_IF_2` (AD8352 ENB floating) |
| Layer-count mismatch | DRU name says 8 layers; 10 copper layers are defined and all carry copper (L1 7 619 objects, L2 1, L3 18, L4 9, L5 1, L12 587, L13 1, L14 395, L15 5, L16 1 605) |
| Via drills | 0.15 mm ×1 045, 0.2 ×1 367, 0.3 ×332, 0.35 ×113, 0.5 ×21, 0.6 ×7, 1.0 ×4, 1.2 ×4 (all through 1-16; no blind/buried) |
| Min track | 0.1 mm (3 408 wires); 0.204 mm RF width ×2 729 (matches PCBWay 50 Ω note) |
| XADC wiring | VP/VN/VREFN tied to GND, VREFP to +1V0_FPGA — unusual, verify against AMD UG480 |
| USB 3.0 | FT601 unconnected; the only host link is STM32 USB-FS (PA11/PA12 → X53) |

## 3. Missing manufacturing outputs

| Output | Status |
|---|---|
| Gerber set (10 Cu + mask + silk + paste + profile) | MISSING |
| Excellon drill (PTH/NPTH) + drill map | MISSING |
| Fabrication drawing with stack-up & impedance | MISSING (only `Stack_Hybrid.png`, which shows 6 layers and cannot be this board) |
| Assembly drawings top/bottom | MISSING |
| BOM with MPNs | MISSING (generated BOM has no MPN attributes) |
| Pick-and-place | MISSING |
| Schematic PDF | MISSING |
| Netlist export | MISSING (regenerable with `tools/extract_eagle_netlist.py`) |
| DRC/ERC reports | MISSING |
| Vendor stack-up confirmation | MISSING |

## 4. Required software

EAGLE 9.6.2 (opens 7.4.0 and upgrades on save — keep the original), or Fusion 360 Electronics, or KiCad 8/9 (import). Gerber viewer: `gerbv` or KiCad GerbView. Python 3.10+ for the repository tools.

## 5. CAD operations (exact)

Follow `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`: P-EAGLE-01 (open; expect no severed-annotation dialog), P-EAGLE-02 (ERC — reopen the 4 approved items on `STM32_MISO_1V8`), P-EAGLE-03 (`RATSNEST` then DRC — record the airwire count), P-EAGLE-04 with a **10-layer** job (template *6 Layer* + inner layers 3, 4, 5, 12, 13, 14), P-EAGLE-06/07/08 for BOM, P&P, drawings and schematic PDF.

## 6. Export settings and expected filenames

RS-274X, mm, 4.4, zipped; Excellon mm, PTH and NPTH separate. Expected: `RADAR_Main_Board/Gerber/copper_top.gbr, copper_inner_2.gbr … copper_inner_9.gbr, copper_bottom.gbr, soldermask_top/bottom.gbr, silkscreen_top/bottom.gbr, solderpaste_top/bottom.gbr, profile.gbr, gerber_job.gbrjob`; `Drill/drill_1_16.xln, drill_npth.xln`; `RADAR_Main_Board-smd.mnt`; `RADAR_Main_Board_BOM.csv`; `RADAR_Main_Board_fab.pdf`; `RADAR_Main_Board_assembly_top.pdf`; `RADAR_Main_Board_schematic.pdf`.

## 7. DRC/ERC validation requirements

- `RATSNEST` → "Nothing to do" (all 2 390 airwires resolved, including +3V3_FT after the FT601 decision).
- DRC with the stored PCBWay DRU: 0 unapproved; the 211 approved errors re-examined and listed with justification.
- Layer count decision: either reduce to 8 (rename not enough — copper exists on all 10) or confirm a 10-layer stack with the fab and correct the DRU name/`mtIsolate` table.
- ERC 0 errors; floating `EN_OPAMP_IF_1/2` and `N$44` dispositioned.
- Bank-voltage check for the FPGA LVDS inputs (bank 14 at 3.3 V with LVDS_25/DIFF_TERM in the XDC — see `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §3.3).
- STM32 HSE crystal value (8 MHz on board vs 25 MHz in firmware — `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` C1).

## 8. BOM validation requirements

Generated `docs/BOM/BOM_MAIN_BOARD.csv`: 98 lines. Required before purchase: MPN + manufacturer for every line (0/98 today); values for the 244 value-less references (mostly `C`/`R` in library `eagle-ltspice`); confirm the 37 SMA and 56 Molex connectors are intended for production (many are test/interconnect points); FT601 and its 7 parked passives marked DNP or wired; INA241A3 ×16 and OPA4703 ×4 (PA bias sensing) confirmed as populated for the Nexus variant.

## 9. Manufacturing package structure

See common document, with `<Board>` = `Main_Board`.

## 10. Expected outputs and acceptance criteria

| Criterion | Measure |
|---|---|
| Layout complete | 0 airwires; 0 elements outside 0..260 × 0..300 mm |
| DRC | 0 unapproved errors with PCBWay 10-layer (or revised) rules |
| ERC | 0 errors |
| Gerber set | 10 copper + 2 mask + 2 silk + 2 paste + profile + job file; viewer check matches `MAIN_BOARD_outline.svg` (260 × 300 mm, 8 × Ø3.2 holes) |
| Drill | PTH count = 2 893 vias + plated pads; NPTH = 8 × 3.2 mm + 2 × 0.9 mm |
| Stack-up | vendor drawing for 10 layers, RO4350B 0.102 mm outer cores, 50 Ω at 0.204 mm, 100 Ω diff 0.204/0.26 mm confirmed |
| BOM | 100 % MPN coverage; DNP column; quantity sum = 776 (minus DNP) |
| Design decisions closed | FT601 wired or removed; FPGA part; HSE crystal; XADC reference wiring |

**Do not** declare this board fabrication-ready on the basis of the existing `.sch/.brd` files.
