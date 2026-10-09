# Assembly Documentation Requirements — AERIS-10

Purpose: define the assembly documentation package that `README.md:141-143` promises (`10_docs/assembly_guide.md`, `10_docs/Hardware/Enclosure`) but that does not exist, and state what can be written today versus what needs designer input. Status date 2026-10-08.

> **Update 2026-10-09:** mechanical artefacts generated from the PCB geometry (DXF, STEP bodies, 1:1 plan view, dimension sheets with hole tables and mass ESTIMATES), the CONCEPTUAL exploded view, parts list and assembly sequence are in `engineering/MECHANICAL/` and `engineering/ASSEMBLY/`; the unresolved geometry register is `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`; reconstruction guides for enclosure/antenna/pedestal/cooling drawings are MDR-01…MDR-05 in `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`.

## 1. Required assembly views and documents

| # | Document | Content | Can be produced now? | Source |
|---|---|---|---|---|
| A1 | Board outline & hole drawings (4 boards) | outline, NPTH positions, connector positions | **YES — produced** (`docs/MECHANICAL/drawings/*_outline.svg`) | EAGLE `.brd` |
| A2 | PCB assembly drawings top/bottom (component outlines + reference designators) | per board | NO (needs EAGLE/KiCad run; P-EAGLE-07) | `.brd` |
| A3 | Inter-board interconnection table (cable list) | from/to connector, signal, cable type, length | PARTIAL — signal map possible from schematic net names on the Molex/SMA connectors; lengths unknown | `.sch` files |
| A4 | System block diagram with physical interfaces | boards, antenna, pedestal, host | YES for electrical blocks (`docs/SYSTEM/BLOCK_DIAGRAM.md`); NO for mechanical envelope | `RADAR_V6.drawio`, schematics, firmware |
| A5 | Enclosure drawing (overall dimensions, mounting, openings for 37+11+2 SMA, mini-USB, power terminal) | — | NO — no enclosure CAD | designer |
| A6 | Exploded view (enclosure, Main Board, Power Board, Synth board, PA boards ×16, antenna, pedestal) | — | NO — no 3-D models | designer |
| A7 | Antenna array drawing (element positions, feed interface) | — | NO — two contradictory simulation geometries, no CAD | antenna designer |
| A8 | Pedestal / azimuth drive (stepper, slip ring, bearing) | — | NO | designer |
| A9 | Thermal/airflow layout (fans, PA heatsinks) | — | NO | designer |
| A10 | Assembly sequence and torque/ESD notes | step list | PARTIAL — electrical bring-up order is known (power sequencing from firmware); mechanical order unknown | `main.cpp:1240-1275,1485-1489`, `Power Management V6.xlsx` |
| A11 | Mass and centre-of-gravity table | per assembly | NO (no thickness, no enclosure) | — |

## 2. Minimum content of `10_docs/assembly_guide.md` (to be written once A5–A9 exist)

1. Safety: PA drain voltage (+22 V per `Power Management V6.xlsx`; actual rail UNRESOLVED), RF exposure at 10.5 GHz with up to 16 × 10 W (Extended variant), ESD for GaN/GaAs MMICs.
2. Kitting: BOMs from `docs/BOM/` (after MPN completion), cables (A3), hardware (M3 screws for the Ø3.2 holes — standoff heights unknown).
3. PCB inspection: visual, continuity on power rails per the Power Board silkscreen rail list, no shorts between `+1V0_FPGA/+1V8_FPGA/+3V3_FPGA` and GND.
4. Board mounting order and standoffs (A5/A6).
5. Cabling: SMA map (A3) — the Frequency Synthesizer silkscreen names its SMAs (`LO TX, LO RX, AUX. LO TX, AUX. LO RX, ADC, FPGA=ADC, FPGA=DAC, DAC, FPGA SYS. CLOCK, TEST, AD9523 PLL_OUT, TX_LO MUXOUT, RX_LO MUXOUT`); Main Board receives `FPGA_SYS_CLOCK` on J1, `FPGA_DAC_CLOCK` on J18, DAC clock on J20, ADC clock on J19 (`docs/PCB/MAIN_BOARD.md`); the remaining 33 Main-Board SMAs (J22–J55) carry RF/antenna/test signals whose assignment must be tabulated from the schematic before cabling.
6. First power-up: STM32 sequencing (`docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` STM-T06 step 4), expected LED behaviour (`LED_1..4` on PF12–PF15: LO lock indication `main.cpp:1453-1474`).
7. Antenna attachment and boresight alignment; stepper homing to North (`main.cpp:1513-1519`).
8. Host connection: mini-USB X53 (STM32 CDC) — the only host link on the current hardware.

## 3. Exploded-view documentation package — procedure (once CAD exists)

- **Software:** Fusion 360 / FreeCAD / SolidWorks.
- **Procedure:** import PCB STEP models (EAGLE 9 → Fusion "Push to 3D" or KiCad → File → Export → STEP after assigning component models), the enclosure STEP, antenna STEP; create an assembly with mates on the Ø3.2 hole patterns; generate an exploded view with a parts list balloon table; export `ASSEMBLY_EXPLODED.pdf` (A3), `ASSEMBLY_ISO.png`, `ASSEMBLY.step`.
- **Verification:** every BOM line item (docs/BOM + system-level items) has a balloon; hole patterns mate without interference; SMA connector positions match the enclosure openings.
- **Acceptance:** the exploded view, the assembly guide and the BOMs agree on part count and reference numbering.

## 4. What this reconstruction delivered

- `docs/MECHANICAL/drawings/MAIN_BOARD_outline.svg`, `POWER_SUPPLY_outline.svg`, `RF_PA_outline.svg`, `FREQUENCY_SYNTHESIZER_outline.svg` (A1).
- `docs/SYSTEM/BLOCK_DIAGRAM.md` (A4, electrical).
- `docs/BOM/` (kitting input).
- This requirements list and `MECHANICAL_GAP_ANALYSIS.md`.

No enclosure, antenna, pedestal, exploded view or mass data was created, because no verified geometry exists in the repository.
