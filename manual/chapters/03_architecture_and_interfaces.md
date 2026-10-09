# Architecture and interfaces — boards, connectors, cables, power rails

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** interconnection diagram and tables SOURCE-DERIVED (connector nets of the four EAGLE schematics, board silkscreen, `main.h`), with every row carrying CONFIRMED / UNVERIFIED / MISSING SPEC; power-rail register SOURCE-DERIVED (voltages from net names, currents UNKNOWN, firmware sequence as coded, not executed); harness schedule PROPOSED DESIGN (DSN-HAR-01, lengths computed from the proposed layout); cable IDs are proposals, not upstream data; figures F3.1 and F3.2 SOURCE-DERIVED.

**Sources:** `engineering/SYSTEM/interfaces/interconnection_table.md`, `engineering/SYSTEM/architecture/README.md`, `engineering/ELECTRICAL/power_distribution/power_rails.md`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, `docs/SYSTEM/BLOCK_DIAGRAM.md` §2–3.

**Planned figures:** F3.1 hardware interconnection diagram (SYS-02), F3.2 power distribution diagram (ELEC-PWR-01 / SYS-04).

## 1. Physical architecture

The radar electronics consist of a Power Supply Board (280 × 300 mm, 2 layers), a Frequency Synthesizer Board (100 × 100 mm, 6 layers), a Main Board (260 × 300 mm, 10 layers) and, for the Extended variant, sixteen RF PA boards (35 × 60 mm, 4 layers), interconnected by 2-pin and 3-pin Molex 22-23-20x1 power cables, one 20-way enable ribbon (SV1), two control ribbons (JP1↔JP1 2×6, JP13↔JP2 2×7), coaxial clock/LO links and 34 SMA RF ports (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §1; `engineering/SYSTEM/interfaces/interconnection_table.md`, lead-in). The antenna, the host PC, the 22 V PA drain supply and the off-board modules (GPS, IMU, barometer, temperature sensors, stepper driver, fan relay, drain switch) have no CAD in the repository and appear as CONCEPTUAL nodes (source: `engineering/SYSTEM/architecture/README.md`, row SYS-01).

![F3.1 — Hardware interconnection diagram SYS-02: one node per board/module, one edge per connector/cable with connector IDs, pin numbers where the symbol has them, signal names and interface standard — SOURCE-DERIVED; cable types, lengths, Molex pin order, SMA RFIN/RFOUT side and PA-instance mapping are UNVERIFIED (source: engineering/SYSTEM/interfaces/hardware_interconnection.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SYSTEM/interfaces/hardware_interconnection.png)

How the diagram was obtained (source: `engineering/SYSTEM/architecture/README.md`, "What was verified against the schematics"): the four `.sch` files were parsed read-only with Python `xml.etree`; parts and `<pinref>` nets were tabulated; anonymous nets (`N$…`) were followed through two-pin passives until a named net or an IC pin was reached; the Synth and PA `.brd` files were parsed for silkscreen text nearest each connector (the Main Board `.brd` contains no free silkscreen text); MCU pins were read from `main.h`, the enable order and clock settings from `main.cpp`, `ADAR1000_Manager.cpp` and `adf4382a_manager.{h,c}`; `Power Management V6.xlsx` was unzipped and its sheet XML parsed.

Corrections to `docs/SYSTEM/BLOCK_DIAGRAM.md` established by SYS-02 (source: `engineering/SYSTEM/architecture/README.md`, same section, copied): (1) SV1 has 15 enable lines; (2) Synth power connectors X10..X15 = `+3V3_XO`, `+3V3_CLOCK`, `+1V8_CLOCK`, `+3V3_LO_1`, `+3V3_LO_2`, `+5V0_LO`; (3) the "17th SMA pair" J22/J23 are the RX-LO and TX-LO inputs of U13/U5 (18 pF coupled); (4) Synth LO SMAs: J10 = `LO TX` (U1 RFOUT1 path), J11 = `LO RX` (U6 RFOUT1 path), J1 = `AUX. LO TX`, J12 = second RX path; (5) `+5V0_ADAR`, `+5V0_ADTR`, `+3V3_SW` outputs (X13, X26, X29) and `+5V0_1..5` (X2, X9, X17, X25, X28) are intermediate rails with no off-board consumer; (6) the PA gate-bias cables are X_1..X_16 (VG_n), the 3-pin X3/X38..X52 carry the INA241 shunt-sense pair.

## 2. Inter-board interconnection tables

Conventions of the copied tables (source: `engineering/SYSTEM/interfaces/interconnection_table.md`, lead-in): pins are EAGLE pin names of the connector symbols; Molex 22-23-20x1 symbols name **all** pads `S`, so their pin order cannot be read from the schematic and is written `S` (UNVERIFIED order). Cable IDs `CBL-xx` are a proposal of that document, not from the original project. "Power requirement" is copied from `3_Power Management/Power Management V6.xlsx` (column G, mA, per device) only where the rail maps to a single row. Status: CONFIRMED = both ends found in the schematics with the same net meaning; UNVERIFIED = one end or the pin order cannot be established; MISSING SPEC = no cable/part/number exists in the repository. Evidence shorthand: `MB` = `RADAR_Main_Board.sch`, `PB` = `PowerBoard.sch`, `SY` = `Clocks_Freq_Synth_board.sch` (+ `.brd` silkscreen), `PA` = `RF_PA.sch`, `main.h` = `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h`, `xlsx` = `Power Management V6.xlsx` sheet `Feuil1`.

### 2.1 DC input (source: `interconnection_table.md` §1)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| External DC source (not specified) | — | — | VIN 12–17 V | Power Board | X1 AK300/2 | KL (1) | DC power | UNKNOWN (sum not computed in xlsx) | CBL-00 | PB X1 nets `VIN`,`GND`; brd silk `Vin [12-17]V` | MISSING SPEC (source) |
| External DC source | — | — | GND | Power Board | X1 AK300/2 | KL (2) | DC power | — | CBL-00 | PB X1 | MISSING SPEC |

### 2.2 Power Board → Main Board rails, Molex 22-23-2021 → 22-23-2021, 2 wires each (source: `interconnection_table.md` §2)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement (xlsx) | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Power Board | X4 | S | `+1V0_FPGA` | Main Board | X8 | S | DC power 1.0 V | 30 mA (row 17, VCCINT/VCCBRAM) | CBL-01 | PB X4; MB X8 | CONFIRMED (pin order UNVERIFIED) |
| Power Board | X5 | S | `+1V8_FPGA` | Main Board | X10 | S | DC power 1.8 V | 50+22+100 mA (rows 14,16,26) | CBL-02 | PB X5; MB X10 | CONFIRMED |
| Power Board | X27 | S | `+3V3_FPGA` | Main Board | X16 | S | DC power 3.3 V | 20+200+20+230 mA (rows 15,18,20,27) | CBL-03 | PB X27; MB X16 | CONFIRMED |
| Power Board | X16 | S | `+3V3` | Main Board | X24 | S | DC power 3.3 V | 130+10+1+50+1 mA (rows 13,47-49,55) | CBL-04 | PB X16; MB X24 | CONFIRMED |
| Power Board | X12 | S | `+3V3_AN` | Main Board | X9 (X56 is on the same net) | S | DC power 3.3 V | 30+2×150+1+2+6+16×6 mA (rows 19,21,50,51,54,56) | CBL-05 | PB X12; MB X9, X56 | CONFIRMED (which of X9/X56 is used: UNVERIFIED) |
| Power Board | X10 | S | `+1V8_CLOCK` | Main Board | X17 | S | DC power 1.8 V | 300 mA (row 25, AD9484 AVDD) | CBL-06 | PB X10; MB X17 → L1 → `+1V8_CLOCK_F` | UNVERIFIED — PB X10 is the only `+1V8_CLOCK` output and is also required by Synth X12 (CBL-24) |
| Power Board | X14 | S | `+3V3_ADAR_12` | Main Board | X20 (`+3V3_ADAR12`) | S | DC power 3.3 V | 2×700 mA (row 30) | CBL-07 | PB X14; MB X20 | CONFIRMED (net names differ by one underscore) |
| Power Board | X15 | S | `+3V3_ADAR_34` | Main Board | X21 (`+3V3_ADAR34`) | S | DC power 3.3 V | 2×700 mA (row 30) | CBL-08 | PB X15; MB X21 | CONFIRMED (name differs) |
| Power Board | X21 | S | `-5V0_ADAR12` | Main Board | X13 | S | DC power −5 V | 2×60 mA (row 29) | CBL-09 | PB X21; MB X13 | CONFIRMED |
| Power Board | X20 | S | `-5V0_ADAR34` | Main Board | X15 | S | DC power −5 V | 2×60 mA (row 29) | CBL-10 | PB X20; MB X15 | CONFIRMED |
| Power Board | X34 | S | `+3V3_ADTR` | Main Board | X4 | S | DC power 3.3 V | 16×80 mA (row 35) | CBL-11 | PB X34; MB X4 | CONFIRMED |
| Power Board | X18 | S | `-3V3_SW` | Main Board | X6 | S | DC power −3.3 V | 16×0.12 mA (row 37) | CBL-12 | PB X18; MB X6 | CONFIRMED |
| Power Board | X30 | S | `+3V3_VDD_SW` | Main Board | X12 | S | DC power 3.3 V | 16×0.014 mA (row 38) | CBL-13 | PB X30; MB X12 | CONFIRMED |
| Power Board | X23 | S | `+3V4` | Main Board | X1 (X54 same net) | S | DC power 3.4 V | 17×2.9 mA (row 22) | CBL-14 | PB X23; MB X1, X54 | CONFIRMED (X1/X54 choice UNVERIFIED) |
| Power Board | X24 | S | `-3V4` | Main Board | X11 (X22 same net) | S | DC power −3.4 V | 17×1.8 mA (row 23) | CBL-15 | PB X24; MB X11, X22 | CONFIRMED (X11/X22 choice UNVERIFIED) |
| Power Board | X3 | S | `+5V5_PA` | Main Board | X55 | S | DC power 5.5 V | 2×50 mA (row 52) | CBL-16 | PB X3; MB X55 | CONFIRMED |
| Power Board | X19 | S | `-5V5_PA` | Main Board | X19 | S | DC power −5.5 V | 2×50 mA (row 53) | CBL-17 | PB X19; MB X19 | CONFIRMED |
| Power Board | X31 | S | `+5V0_PA_1` | Main Board | X14 | S | DC power 5 V | 5×250 mA (row 40; ADTR1107_1,2,3,4,7) | CBL-18 | PB X31; MB X14 | CONFIRMED |
| Power Board | X32 | S | `+5V0_PA_2` | Main Board | X5 | S | DC power 5 V | 5×250 mA (ADTR1107_5,6,8,10,12) | CBL-19 | PB X32; MB X5 | CONFIRMED |
| Power Board | X33 | S | `+5V0_PA_3` | Main Board | X7 | S | DC power 5 V | 6×250 mA (ADTR1107_9,11,13,14,15,16) | CBL-20 | PB X33; MB X7 | CONFIRMED |
| Power Board | X22 | S | `+5V0_0` | Main Board | X18 | S | DC power 5 V | 2×200 mA (row 24, AD8352) — also feeds PB U5 (+3V3_AN) on the Power Board | CBL-20a | PB X22; MB X18 | CONFIRMED |
| Power Board | X2, X9, X17, X25, X28 | S | `+5V0_1..+5V0_5` | — (no counterpart on Main or Synth) | — | — | DC power 5 V | — | — | PB X2,X9,X17,X25,X28; MB/SY: net absent | UNVERIFIED (spare or test outputs; rails are consumed on-board by U23/U25/U27/U29/U34) |
| Power Board | X13 | S | `+5V0_ADAR` | — (no counterpart) | — | — | DC power 5 V | — | — | PB X13; MB: net absent (ADAR AVDD is −5 V from X13/X15) | UNVERIFIED (consumed on-board by U20/U21) |
| Power Board | X26 | S | `+5V0_ADTR` | — (no counterpart) | — | — | DC power 5 V | — | — | PB X26; MB: net absent | UNVERIFIED (consumed on-board by U32) |
| Power Board | X29 | S | `+3V3_SW` | — (no counterpart) | — | — | DC power 3.3 V | — | — | PB X29; MB: net absent | UNVERIFIED (consumed on-board by U18) |

### 2.3 Main Board → Power Board enable bus, SV1 MA10-2 ↔ SV1 MA10-2, 20-way, cable CBL-21 (source: `power_rails.md` §2, identical pin map on both boards; all rows CONFIRMED in `interconnection_table.md` §3)

| SV1 pin | Net | STM32 pin (`main.h`) | Power Board EN input |
|---|---|---|---|
| 1 | `EN_+1V0_FPGA` | PE7 | U1 |
| 2 | `EN_+5V0_PA2` | PG1 | U15 |
| 3 | `EN_+1V8_FPGA` | PE8 | U2 |
| 4 | `EN_+5V0_PA3` | PG2 | U16 |
| 5 | `EN_+3V3_FPGA` | PE9 | U4 |
| 6 | `EN_+5V5_PA` | PG3 | U17 |
| 7 | `EN_+5V0_ADAR` | PE10 | U13 |
| 8 | `EN_+1V8_CLOCK` | PG4 | U25 |
| 9 | `EN_+3V3_ADAR12` | PE11 | U6 |
| 10 | `EN_+3V3_CLOCK` | PG5 | U23 |
| 11 | `EN_+3V3_ADAR34` | PE12 | U7 |
| 13 | `EN_+3V3_ADTR` | PE13 | U32 |
| 15 | `EN_+3V3_SW` | PE14 | U10 |
| 17 | `EN_+3V3_VDD_SW` | PE15 | U8 |
| 19 | `EN_+5V0_PA1` | PG0 | U14 |
| 12, 14, 16, 18, 20 | GND | — | — |

15 enable lines (not 16 as stated in `docs/SYSTEM/BLOCK_DIAGRAM.md`). All enables are driven as push-pull outputs initialised LOW in `MX_GPIO_Init` (`main.cpp:2239-2247`); the Power Board has no pull-downs/pull-ups on the EN nets visible in the netlist (not checked exhaustively — REQUIRES VERIFICATION) (source: `power_rails.md` §2).

### 2.4 Power Board → Frequency Synthesizer Board rails, Molex 22-23-2021, 2 wires each (source: `interconnection_table.md` §4; Synth-side nets are anonymous `N$69..N$77` and reach the named rail through a series inductor `SY L9..L13`)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement (xlsx) | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Power Board | X35 | S | `+3V3_XO` | Synth Board | X10 (`N$69` → L9 → `+3V3_XO`) | S | DC power 3.3 V | 1200+25+25 mA (rows 2,4,5) | CBL-22 | PB X35; SY X10, L9, X4/X5/X6 VDD | CONFIRMED |
| Power Board | X11 | S | `+3V3_CLOCK` | Synth Board | X11 (`N$71` → L10 → `+3V3_CLOCK`) | S | DC power 3.3 V | 250 mA (row 6) | CBL-23 | PB X11; SY X11, L10, IC1 VDD3_* | CONFIRMED |
| Power Board | X10 | S | `+1V8_CLOCK` | Synth Board | X12 (`N$73` → L11 → `+1V8_CLOCK`) | S | DC power 1.8 V | 250 mA (row 7) | CBL-24 | PB X10; SY X12, L11, IC1 VDD1.8_* | UNVERIFIED — same PB X10 also needed by Main X17 (CBL-06); a Y-cable or second output is not in CAD |
| Power Board | X8 | S | `+3V3_LO_1` | Synth Board | X13 (`N$75` → L12 → `+3V3_LO_1`) | S | DC power 3.3 V | 2×240 mA (row 11) | CBL-25 | PB X8; SY X13, L12, U1/U6 V3_LDO/LS/NDIV/PFD/REF/SYNC | CONFIRMED |
| Power Board | X7 | S | `+3V3_LO_2` | Synth Board | X14 (`N$77` → L13 → `+3V3_LO_2`) | S | DC power 3.3 V | 2×340 mA (row 12) | CBL-26 | PB X7; SY X14, L13, U1/U6 V3_OUTDIV/RFOUT/VCOB | CONFIRMED |
| Power Board | X6 | S | `+5V0_LO` | Synth Board | X15 (`+5V0_LO`) | S | DC power 5 V | 2×(200+0.3+70) mA (rows 8-10) | CBL-27 | PB X6; SY X15, FB1..FB4 | CONFIRMED |

### 2.5 Main Board ↔ Frequency Synthesizer Board control headers (source: `interconnection_table.md` §5)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board (U2 PF3) | JP1 PINHD-2X6 | 1 | `AD9523_PD` | Synth Board | JP1 PINHD-2X6 | 1 | 3.3 V CMOS GPIO | — | CBL-28 | MB JP1.1, U2.PF3 (`main.h:62`); SY JP1.1 → IC1 | CONFIRMED |
| Main Board (PF4) | JP1 | 2 | `AD9523_REF_SEL` | Synth Board | JP1 | 2 | 3.3 V CMOS | — | CBL-28 | `main.h:64`; SY IC1.REF_SEL | CONFIRMED |
| Main Board (PF5) | JP1 | 3 | `AD9523_SYNC` | Synth Board | JP1 | 3 | 3.3 V CMOS | — | CBL-28 | `main.h:66` | CONFIRMED |
| Main Board (PF6) | JP1 | 4 | `AD9523_RESET` | Synth Board | JP1 | 4 | 3.3 V CMOS | — | CBL-28 | `main.h:68` | CONFIRMED |
| Main Board (PF7) | JP1 | 5 | `AD9523_CS` | Synth Board | JP1 | 5 | SPI CS (3.3 V) | — | CBL-28 | `main.h:70`; firmware never toggles it (docs C7) | CONFIRMED (hardware) |
| Main Board (PE2 SPI4_SCK) | JP1 | 6 | `STM32_SCLK4` → `AD9523_SCLK` | Synth Board | JP1 | 6 | SPI 3.3 V (R6 0.65 k series) | — | CBL-28 | MB U2.PE2; SY JP1.6, R6, IC1.SCLK | CONFIRMED |
| Main Board (PE6 SPI4_MOSI) | JP1 | 7 | `STM32_MOSI4` → `AD9523_SDIO` | Synth Board | JP1 | 7 | SPI 3.3 V (R8 0.65 k) | — | CBL-28 | MB U2.PE6; SY R8, IC1.SDIO | CONFIRMED |
| Synth Board (IC1 SDO) | JP1 | 8 | `AD9523_SDO` → `STM32_MISO4` | Main Board (PE5) | JP1 | 8 | SPI 3.3 V | — | CBL-28 | SY IC1.SDO; MB U2.PE5 | CONFIRMED |
| Synth Board | JP1 | 9 / 10 | `AD9523_STATUS0` / `STATUS1` | Main Board (PF8 / PF9) | JP1 | 9 / 10 | 3.3 V CMOS | — | CBL-28 | `main.h:72-75` | CONFIRMED |
| Main Board (PF10) | JP1 | 11 | `AD9523_EEPROM_SEL` | Synth Board | JP1 | 11 | 3.3 V CMOS | — | CBL-28 | `main.h:76` | CONFIRMED |
| — | JP1 | 12 | GND | — | JP1 | 12 | — | — | CBL-28 | both | CONFIRMED |
| Synth Board (U1/U6 SDO) | JP2 PINHD-2X7 | 1 | `ADF4382_SDO` → `STM32_MISO4` | Main Board (PE5) | JP13 PINHD-2X7 | 1 | SPI 3.3 V (shared SPI4 bus with AD9523) | — | CBL-29 | SY JP2.1; MB JP13.1 | CONFIRMED |
| Main Board (PE2) | JP13 | 2 | `STM32_SCLK4` → `ADF4382_SCLK` | Synth Board | JP2 | 2 | SPI 3.3 V | — | CBL-29 | MB JP13.2; SY JP2.2, U1/U6.SCLK | CONFIRMED |
| Main Board (PE6) | JP13 | 3 | `STM32_MOSI4` → `ADF4382_SDIO` | Synth Board | JP2 | 3 | SPI 3.3 V | — | CBL-29 | MB JP13.3; SY JP2.3 | CONFIRMED |
| Main Board (PG14) | JP13 | 4 | `ADF4382_TX_CS` | Synth Board (U1 CSB, 200 k pull-up R24) | JP2 | 4 | SPI CS 3.3 V | — | CBL-29 | `main.h:154`; SY R24 | CONFIRMED (K6: `adf4382a_manager.h` expects other pins) |
| Main Board (PG15) | JP13 | 5 | `ADF4382_TX_CE` | Synth Board (U1 CE, R25) | JP2 | 5 | 3.3 V CMOS | — | CBL-29 | `main.h:156` | CONFIRMED |
| Main Board (PG12) | JP13 | 6 | `ADF4382_TX_DELSTR` | Synth Board (U1) | JP2 | 6 | 3.3 V CMOS | — | CBL-29 | `main.h:150` | CONFIRMED |
| Main Board (PG13) | JP13 | 7 | `ADF4382_TX_DELADJ` | Synth Board (U1) | JP2 | 7 | 3.3 V CMOS | — | CBL-29 | `main.h:152` | CONFIRMED |
| Synth Board (U1 LKDET) | JP2 | 8 | `ADF4382_TX_LKDET` | Main Board (PG11) | JP13 | 8 | 3.3 V CMOS | — | CBL-29 | `main.h:148` | CONFIRMED |
| Main Board (PG10) | JP13 | 9 | `ADF4382_RX_CS` | Synth Board (U6 CSB, R37) | JP2 | 9 | SPI CS | — | CBL-29 | `main.h:146` | CONFIRMED |
| Main Board (PG9) | JP13 | 10 | `ADF4382_RX_CE` | Synth Board (U6 CE, R38) | JP2 | 10 | 3.3 V CMOS | — | CBL-29 | `main.h:144` | CONFIRMED |
| Main Board (PG8) | JP13 | 11 | `ADF4382_RX_DELSTR` | Synth Board (U6) | JP2 | 11 | 3.3 V CMOS | — | CBL-29 | `main.h:128` | CONFIRMED |
| Main Board (PG7) | JP13 | 12 | `ADF4382_RX_DELADJ` | Synth Board (U6) | JP2 | 12 | 3.3 V CMOS | — | CBL-29 | `main.h:126` | CONFIRMED |
| Synth Board (U6 LKDET) | JP2 | 13 | `ADF4382_RX_LKDET` | Main Board (PG6) | JP13 | 13 | 3.3 V CMOS | — | CBL-29 | `main.h:124` | CONFIRMED |
| — | JP13 | 14 | GND | — | JP2 | 14 | — | — | CBL-29 | both | CONFIRMED |

### 2.6 Frequency Synthesizer Board → Main Board clocks and LO, coaxial (source: `interconnection_table.md` §6; frequencies are the values programmed in `main.cpp:970-1028` and `adf4382a_manager.h:32-34`, firmware intent, not measurements)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Synth (IC1 OUT6 → R39 22 R → C15 10 nF) | J7 SMA 142-0731-211, silk `FPGA SYS. CLOCK` | 1 | `AD9523_OUT6+` 100 MHz LVCMOS → `FPGA_SYS_CLOCK` | Main Board (U42 `IO_L13P_T2_MRCC_15`) | J1 SMA | 1 | 50 Ω coax, single-ended clock | — | CBL-30 | SY J7, R39, C15; MB J1, U42; `main.cpp:1004` | CONFIRMED |
| Synth (OUT10 → R40 → C17) | J5 SMA, silk `DAC` | 1 | 120 MHz LVCMOS → `DAC_CLOCK` | Main Board (U3 AD9708 CLOCK via R31) | J20 SMA | 1 | 50 Ω coax | — | CBL-31 | SY J5; MB J20, R31, U3 | CONFIRMED |
| Synth (OUT11 → R41 → C19) | J6 SMA, silk `FPGA=DAC` | 1 | 120 MHz LVCMOS → `FPGA_DAC_CLOCK` | Main Board (U42 `IO_L12N_T1_MRCC_15`) | J18 SMA | 1 | 50 Ω coax | — | CBL-32 | SY J6; MB J18, U42 | CONFIRMED |
| Synth (OUT7) | J8 SMA, silk `TEST` | 1 | 20 MHz LVCMOS → `FPGA_CLOCK_TEST` | Main Board (U42 `IO_L24P_T3_RS1_15`) | JP20 PINHD-1X2 | 1 (2 = GND) | SMA → 0.1" header (adapter not specified) | — | CBL-33 | SY J8; MB JP20 | UNVERIFIED (adapter) |
| Synth (OUT4) | J3 CJT-T-P-HH-ST-TH1, silk `ADC` | 1 P, 2 N | `AD9523_OUT4_P/N` 400 MHz LVDS → `N$2_P/N` → C1/C2 → `ADC_CLK_IN_P/N` | Main Board (U1 AD9484 CLK+/CLK−, R173 100 Ω) | J21 CJT | 1 P, 2 N | twinax differential | — | CBL-34 | SY J3; MB J21, C1, C2, R173, U1 | CONFIRMED |
| Synth (OUT5) | J4 CJT, silk `FPGA=ADC` | 1 P, 2 N | 400 MHz LVDS → `FPGA_ADC_CLOCK_P/N` | Main Board (U42 `IO_L13P/N_T2_MRCC_14`, R4) | J19 CJT | 1 P, 2 N | twinax differential | — | CBL-35 | SY J4; MB J19, U42 | CONFIRMED (not used by RTL) |
| Synth (U1 ADF4382 TX RFOUT1 → C64/C65 → U2 MTX2-143+ → U4 ATS1005 −3 dB) | J10 SMA, silk `LO TX` | 1 | TX LO 10.5 GHz (`TX_FREQ_HZ`) | Main Board (U5 LTC5552 LO via C272 18 pF) | J23 SMA (`N$23`) | 1 | 50 Ω coax, X-band | — | CBL-36 | SY U1, U2, U4, J10 (`N$30`), brd silk; MB J23, C272, U5.LO | CONFIRMED (silk-to-net association from brd text proximity) |
| Synth (U6 ADF4382 RX RFOUT1 → U7 → U8) | J11 SMA, silk `LO RX` | 1 | RX LO 10.38 GHz (`RX_FREQ_HZ`) | Main Board (U13 LTC5552 LO via C274 18 pF) | J22 SMA (`N$24`) | 1 | 50 Ω coax, X-band | — | CBL-37 | SY U6, U7, U8, J11 (`N$55`); MB J22, C274, U13.LO | CONFIRMED |
| Synth (U1 RFOUT2 → U3 → U5) | J1 SMA, silk `AUX. LO TX` | 1 | auxiliary TX LO | — | — | — | — | — | — | SY J1 (`N$35`) | UNVERIFIED (no destination) |
| Synth (U6 RFOUT2 → U9 → U10) | J12 SMA (silk by elimination `AUX. LO RX`) | 1 | auxiliary RX LO | — | — | — | — | — | — | SY J12 (`N$59`) | UNVERIFIED (no destination, silk not adjacent) |
| Synth (U1 MUXOUT / U6 MUXOUT / IC1 PLL_OUT) | J9 / J2 / J13 SMA | 1 | test outputs | — | — | — | — | — | — | SY J9 (`N$37`), J2 (`N$51`), J13 (`N$61`) | test points, no counterpart |

### 2.7 Main Board ↔ RF PA boards, 16 instances (source: `interconnection_table.md` §7)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board RF_SW_n (n = 1..16) RFOUT1 / RFOUT2 via 1 pF | J27/J26 (n=1), J29/J28 (2), J25/J24 (3), J31/J30 (4), J35/J34 (5), J37/J36 (6), J33/J32 (7), J39/J38 (8), J47/J46 (9), J41/J40 (10), J45/J44 (11), J43/J42 (12), J55/J54 (13), J49/J48 (14), J53/J52 (15), J51/J50 (16) | 1 | element RF (TX to PA / RX return) | RF PA board n | J1 `RFIN` / J2 `RFOUT` | 1 | 50 Ω coax, 10.5 GHz | — | CBL-40..CBL-55 | MB RF_SW_n pins (traced through C126/C128-type 1 pF caps); PA J1 (`N$2`), J2 (`N$8`), brd silk | UNVERIFIED — which SMA of each pair is RFIN vs RFOUT and PA-instance mapping are not documented |
| Main Board (U7/U69 DAC5578 → OPA4703 → `VG_n`) | X_7=VG_1, X_16=VG_2, X_8=VG_3, X_15=VG_4, X_4=VG_5, X_11=VG_6, X_3=VG_7, X_12=VG_8, X_5=VG_9, X_14=VG_10, X_6=VG_11, X_13=VG_12, X_2=VG_13, X_9=VG_14, X_1=VG_15, X_10=VG_16 (Molex 22-23-2021) | S (VG), S (GND) | gate bias `VG_n` (xlsx: −4 … −1.2 V, 10 mA) | RF PA board | X2 Molex 22-23-2021 | 1 `VG`, 2 `GND` | analogue DC | 10 mA (row 60) | CBL-56..CBL-71 | MB X_n nets `VG_n`; PA X2 | CONFIRMED (VG_n → PA instance assignment UNVERIFIED) |
| RF PA board (R10 WSL2816 5 mΩ shunt: `VD` / `VIN_M`) | X3 Molex 22-23-2031 | 1 `VD`, 2 `VIN_M`, 3 `GND` | drain current sense pair | Main Board (INA241A3 U11 for X3, U73 for X38, …) | X3, X38..X52 Molex 22-23-2031 | S (`GND`), S (`N$207`=IN+), S (`N$209`=IN−) (X3 example) | analogue differential sense | — | CBL-72..CBL-87 | PA X3, R10; MB X3 → U11.IN+/IN−, X38 → U73 … | CONFIRMED topology; pin ORDER UNVERIFIED (pads named `S`), PA-instance → Main-connector map NOT DOCUMENTED |
| +22 V drain supply (NOT IN CAD) | — | — | `VD` 22 V (xlsx row 59: 18–22 V, 2000 mA, "Set VD +22 V") | RF PA board | `22V` AK300/2 terminal | KL1 `VD`, KL2 `GND` | DC power | 2 A per board (xlsx) | CBL-88 | PA part `22V`; xlsx row 59; Power Board has no 22 V rail (K4) | MISSING SPEC |
| Main Board (U2 PD6) | JP10 PINHD-1X3 | 1 `EN/DIS_RFPA_VDD`, 3 GND | PA drain enable (set in `main.cpp:1601`) | PA drain switch — device NOT IN CAD | — | — | 3.3 V CMOS | — | — | MB JP10; `main.h:140` | MISSING SPEC |

### 2.8 Main Board ↔ host and off-board modules (source: `interconnection_table.md` §8)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board (U2 PA11 / PA12 / PA10) | X53 MINI-USB | 2 `STM32_USB_FS_D_N`, 3 `D_P`, 4 `ID`, 5 GND (1 VBUS not connected in sch) | USB 2.0 full-speed, CDC class (firmware `usbd_cdc_if` references) | Host PC | USB-A/host port | — | USB 2.0 FS | bus-powered: NO (VBUS pin unconnected; VDDUSB = +3V3) | CBL-90 | MB X53, U2.PA10-PA12, VDDUSB | CONFIRMED (host side MISSING SPEC) |
| Main Board (U6 FT601) | — | — | USB 3.0 (RTL `radar_system_top.v:79-97`, GUI_V6.py FT601 class) | Host PC | — | — | USB 3.0 | — | — | MB U6: 0 nets | MISSING SPEC — no hardware path (K3) |
| Main Board | JP2 PINHD-1X6 | 1 `+3V3`, 2 `STM32_SWCLK`, 3 GND, 4 `STM32_SWDIO`, 5 `STM32_NRST`, 6 `STM32_SWO` | SWD | debug probe (not specified) | — | — | ARM SWD 3.3 V | — | CBL-91 | MB JP2 | CONFIRMED (probe MISSING SPEC) |
| Main Board (U2 PC12 / PD2) | JP8 PINHD-1X4 | 1 `+3V3`, 2 `STM32_TX5`, 3 `STM32_RX5`, 4 GND | UART5 (9600 Bd per firmware GPS driver) | GPS module NEO-6M (xlsx row 49) | module header | — | UART 3.3 V | 50 mA (row 49) | CBL-92 | MB JP8, U2.PC12/PD2 | UNVERIFIED (module pinout) |
| Main Board (U2 PA8 / PC9 / PC6 / PC7 / PC8) | JP7 PINHD-1X8 | 2 `+3V3`, 3 GND, 4 `STM32_SCL3`, 5 `STM32_SDA3`, 6 `MAG_DRDY`, 7 `ACC_INT`, 8 `GYR_INT` (pin 1 unconnected) | I2C3 + interrupts | GY-85 IMU (xlsx row 47) | module header | — | I2C 3.3 V | 10 mA | CBL-93 | MB JP7; `main.h:130-135` | UNVERIFIED (module pinout) |
| Main Board | JP18 PINHD-1X4 | 1 `STM32_SDA3`, 2 `STM32_SCL3`, 3 GND, 4 `+3V3` | I2C3 | BMP180 barometer (xlsx row 48) | module header | — | I2C 3.3 V | 1 mA | CBL-94 | MB JP18 | UNVERIFIED (module pinout; JP7/JP18 assignment to IMU vs BMP180 is an assumption) |
| Main Board | JP5, JP6, JP11, JP12, JP14, JP15, JP16, JP19 PINHD-1X3 | 1 `+3V3_AN4_F`, 2 analogue (`N$295, N$296, N$306, N$298, N$299, N$307, N$301, N$297`), 3 GND | TMP37 output → ADS7830 channel | 8 × TMP37 (xlsx row 50) | sensor leads | — | analogue 3.3 V | 1 mA each | CBL-95..CBL-102 | MB JP5..JP19 nets | CONFIRMED (header) / channel order UNVERIFIED |
| Main Board (U2 PD4 / PD5) | JP9 PINHD-1X4 | 1 GND, 2 `STEPPER_CW+`, 3 GND, 4 `STEPPER_CLK+` | direction / step | stepper driver "TBS6600" (xlsx row 63; TB6600-class) | driver inputs | — | 3.3 V logic | driver 4000 mA @ 20 V from its own supply (row 63) | CBL-103 | MB JP9; `main.h:136-139` | UNVERIFIED (driver pinout, supply not in CAD) |
| Main Board (U2 PD7) | JP4 PINHD-1X3 | 1 `EN/DIS_COOLING`, 3 GND | fan relay control (`main.cpp:1767-1770`) | cooling relay / fans (xlsx row 64) | — | — | 3.3 V logic | UNKNOWN | CBL-104 | MB JP4; `main.h:142` | MISSING SPEC (relay/fan parts) |
| Main Board (U2 PB10 / PB11) | JP17 PINHD-1X3 | 1 `STM32_TX3`, 2 `STM32_RX3`, 3 GND | USART3 debug console (`huart3` in `main.cpp`) | serial adapter (not specified) | — | — | UART 3.3 V | — | CBL-105 | MB JP17 | CONFIRMED (header) |
| Main Board | JP3 PINHD-2X4 | 1 `N$32`, 2 `+3V3_FPGA`, 3 `N$33`, 5 `N$34`, 7 `N$36`, 8 GND | FPGA JTAG header (nets reach U42 TCK/TMS/TDI/TDO through R62/R49/R64/R63 — see `docs/FPGA/`) | JTAG programmer | — | — | JTAG 3.3 V | — | CBL-106 | MB JP3 | UNVERIFIED (pin-to-TAP assignment not traced here) |

### 2.9 Antenna (source: `interconnection_table.md` §9)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RF PA board n | J2 `RFOUT` | 1 | element n TX (AERIS-10X) | antenna array element | — | — | 50 Ω coax / waveguide transition | 10 W per element (README) | — | README.md; RADAR_V6.drawio | MISSING SPEC (no antenna CAD, K8) |
| Main Board | J24..J55 | 1 | element RF (AERIS-10N direct) | antenna array element | — | — | 50 Ω | ~1 W per element (README) | — | README.md | MISSING SPEC |

### 2.10 Items left UNVERIFIED by SYS-02 and why (source: `engineering/SYSTEM/architecture/README.md`, "Items left UNVERIFIED", copied)

| Item | Reason |
|---|---|
| Pin order of all Molex 22-23-2021/2031 connections | EAGLE symbol names every pad `S`; order not recoverable from the schematic |
| Which SMA of each element pair (e.g. J27/J26) goes to PA `RFIN` vs returns from `RFOUT`, and PA-board-instance → Main-connector assignment | no silkscreen text on the Main Board `.brd`, no cabling document |
| Synth J12 function (`AUX. LO RX`) | silkscreen text not adjacent; assigned by elimination |
| Oscillator identities (X4 100 MHz OCXO vs net `10MHZ_OUT`; X5/X6 50 MHz VCXO vs nets `100MHZ_OUT`/`VCXO_OUT` and firmware 100 MHz) | contradictory sources (K7) |
| `+1V8_CLOCK` distribution to both Main X17 and Synth X12 from the single Power output X10 | no cable/Y-splice in CAD |
| 22 V PA drain source and the switch driven by `EN/DIS_RFPA_VDD` | absent from all CAD (K4) |
| GPS / IMU / BMP180 / stepper-driver / relay module pinouts and supplies | modules named only in the xlsx; no module schematics |
| JP3 pin → FPGA TAP signal assignment | nets `N$32..N$36` not traced here (see `docs/FPGA/`) |
| Host-link packet format, USB 3.0 path | no FT601 nets (K3); RTL/GUI packet formats differ (K5) |
| DIG_0..7 bit meaning | inferred from firmware/RTL names only (`docs/SYSTEM/BLOCK_DIAGRAM.md` §3) |
| Output voltages, regulator current capability, VIN total current | dividers listed, no datasheet for TPS562208 in repo; no budget sum in xlsx |
| Cable types, lengths, coax grade, wire gauge | not in any repository file |
| Antenna feed network, element-to-port mapping, waveguide transition | no antenna CAD (K8) |

## 3. Interface implementation status

The electrical existence of an interface says nothing about whether the firmware or the RTL drives it. The cross-check per interface (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §3, copied verbatim; the RTL column describes the original `9_Firmware/9_2_FPGA`, the BETA state is in chapters 2 and 11):

| Interface | CAD | Firmware | RTL | Status |
|---|---|---|---|---|
| STM32 → FPGA handshake (`DIG_0..4`) | yes | `main.cpp:448,484,514,1483,1660` | `stm32_new_*`, `stm32_mixers_enable`, `reset_n` | bit mapping inferred (MEDIUM) |
| STM32 SPI1 → FPGA → ADAR1000 (1.8 V) | yes | `ADAR1000_Manager.cpp` on `hspi1` | level shifter **not instantiated** (`radar_transmitter.v:59-71` undriven) | **BROKEN in RTL** |
| FPGA → host (FT601) | **not wired** | — | `usb_data_interface.v` | **NO HARDWARE** |
| STM32 ↔ host (USB CDC) | yes | RX callback never bound (C4); start-flag padding (C5) | — | **BROKEN in firmware** |
| STM32 → AD9523 (SPI4) | yes | CS never toggled, 36 MHz (C7) | — | questionable |
| STM32 → ADF4382 (SPI4) | yes | pin macros collide with PA enables (C2); `platform_ops=NULL` (C3) | — | **BROKEN** |
| AD9523 → FPGA clocks | yes (J1, J18, J19) | OUT6/OUT11/OUT5 programmed | `clk_100m`, `clk_120m_dac`; 400 MHz path uses ADC DCO only | partially consistent |
| ADC → FPGA LVDS | yes (bank 14 at 3.3 V) | — | capture not implemented; XDC wants LVDS_25 + DIFF_TERM | **BROKEN / bank-voltage conflict** |
| GPS → host | UART5 + USB | `GPS_Init` never called (C6) | — | **BROKEN** |

The firmware defects C2–C7 are fixed in `beta/stm32` (ADF4382 pin collision, `platform_ops = NULL`, unbound CDC RX, padded settings frames, GPS_Init, AD9523 CS/SPI speed) and the RTL defects in `beta/fpga` (level-shifter pass-through instantiated, ISERDES capture, SPI bridge); none of these fixes has been exercised on hardware (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §3–4).

## 4. Power distribution

![F3.2 — Power distribution diagram ELEC-PWR-01 / SYS-04: every Power Board rail with regulator, feedback divider, source rail, enable net and MCU pin, firmware sequence step, output connector → destination connector → consumer — SOURCE-DERIVED; output voltages from net names, currents UNKNOWN (source: engineering/ELECTRICAL/power_distribution/power_distribution.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/ELECTRICAL/power_distribution/power_distribution.png)

Conventions of the rail register (source: `engineering/ELECTRICAL/power_distribution/power_rails.md`, lead-in): **Nominal V** is the value encoded in the net name and the xlsx column H "SELECTED VOLTAGE"; feedback resistor values are listed as evidence but output voltages were **not recomputed** (the TPS562208 datasheet is not in the repository — only `tps562201.pdf`). **Current ratings are UNKNOWN** unless the xlsx gives a per-device budget; regulator capability is not asserted. **Enable** = net on the Power Board EN pin (`VIN` or own input = always on). Sequence step: `xlsx` = text of column L/K, `FW` = firmware order F1..F10 of section 4.2. Status: CONFIRMED = regulator, nets and consumer connector all found; PARTIAL = found but something inconsistent; UNVERIFIED = consumer or cable cannot be established; CONFLICT = contradicts another source.

### 4.1 Rail register (source: `power_rails.md` §1, copied verbatim)

| Rail | Nominal V (source) | Regulator (ref, part) | Source rail | Consumers (board: connector → loads) | Enable signal (MCU pin) | Sequence step | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| `VIN` | 12–17 V (brd silk `Vin [12-17]V`) | — (input) | external DC source (not specified) | all 21 bucks; U30 ADM7151 directly | — | — | PB X1 `AK300/2` (KL: VIN, GND) | UNVERIFIED (source, total current) |
| `+1V0_FPGA` | 1.0 V (net; xlsx row 17 "1") | U1 TPS562208DDCT, FB R1 3.09 k / R2 10 k | VIN | Main: X4→X8 → U42 VCCINT, VCCBRAM | `EN_+1V0_FPGA` PE7 (`main.h:98`) | xlsx: FPGA rows order +1V0 → +1V8 → +3V3 (L15-L17), K=YES; FW: F3 (`main.cpp:1271`, +100 ms) | PB U1 pins; MB X8, U42 | CONFIRMED |
| `+1V8_FPGA` | 1.8 V (xlsx rows 14,16,26) | U2 TPS562208, R3 13.7 k / R4 10 k | VIN | Main: X5→X10 → U42 VCCAUX, VCCADC, VCCBATT, VCCO_34; U1 AD9484 DRVDD; R154–R157 pull-ups (ADAR CS 1.8 V) | `EN_+1V8_FPGA` PE8 | K=YES; FW: F4 (`main.cpp:1273`, +100 ms) | PB U2; MB X10 | CONFIRMED |
| `+3V3_FPGA` | 3.3 V (rows 15,18,20,27) | U4 TPS562208, R7 32.2 k / R8 10 k | VIN | Main: X27→X16 → U42 VCCO banks 14/15 + config pull-ups, U3 AD9708 DVDD, U9 flash; L19 → `+3V3_FT` (FT601, unrouted) | `EN_+3V3_FPGA` PE9 | K=YES; FW: F5 (`main.cpp:1275`, +100 ms) | PB U4; MB X16 | CONFIRMED |
| `+3V3` | 3.3 V (rows 13,47-49,55) | U3 TPS562208, R5 32.2 k / R6 10 k | VIN | Main: X16→X24 → U2 STM32 VDD/VDDUSB, headers JP2/JP7/JP8/JP18 (+3V3 pin for modules), ADS7830 VREF (xlsx row 55) | always on (EN = VIN) | xlsx K=NO | PB U3; MB X24, U2.VDDUSB | CONFIRMED |
| `+3V3_AN` | 3.3 V (rows 19,21,50,51,54,56) | U5 ADM7151ACPZ-04, EN tied to its input | `+5V0_0` (U12) | Main: X12→X9 (and X56 same net) → L15 `+3V3_AN1_F` U5 mixer VCC; L16 `+3V3_AN2_F` U13 mixer; L17 `+3V3_AN3_F` U7/U69 DAC5578; L18 `+3V3_AN4_F` TMP37 headers + ADS7830; L21/L23 `+3V3_AN5_F`/`_6_F` 16 × INA241; L6 BLM15H `DAC_AVDD` U3 | none (follows `+5V0_0`) | K=NO | PB U5; MB X9, X56, L6/L15–L18/L21/L23 | CONFIRMED (X9 vs X56 use UNVERIFIED) |
| `+1V8_CLOCK` | 1.8 V (rows 7, 25) | U25 ADM7151, EN = `EN_+1V8_CLOCK` | `+5V0_2` (U24) | Synth: X10→X12 → L11 → IC1 AD9523 VDD1.8_OUT*, VDD1.8_PLL2. Main: X10→X17 → L1 → `+1V8_CLOCK_F` → U1 AD9484 AVDD ×11, CSB | `EN_+1V8_CLOCK` PG4 (`main.h:120`) | xlsx L6: "bring the 1.8 V supplies high ... prior to or simultaneously with the 3.3 V"; FW: **F1** (`main.cpp:1241`, +100 ms) | PB U25, X10; SY X12, L11; MB X17, L1 | **PARTIAL** — one Power-Board output (X10) for two destination connectors; splitting not in CAD |
| `+3V3_CLOCK` | 3.3 V (row 6) | U23 ADM7151, EN = `EN_+3V3_CLOCK` | `+5V0_1` (U9) | Synth: X11→X11 → L10 → IC1 VDD3_OUT*, VDD3_PLL1/2, VDD3_REF | `EN_+3V3_CLOCK` PG5 (`main.h:122`) | xlsx L6 (after 1.8 V), K=YES; FW: F2 (`main.cpp:1243`, +100 ms, then AD9523 RESET released) | PB U23, X11; SY X11, L10 | CONFIRMED |
| `+3V3_XO` | 3.3 V (rows 2-5) | U34 TPS7A8300RGRR, EN = its input | `+5V0_5` (U33) | Synth: X35→X10 → L9 → X4 OCXO SUPPLY_VOLTAGE (+R2/R3 VC divider), X5/X6 VCXO VDD | none (always on when VIN present) | K=NO | PB U34, X35; SY X10, L9 | CONFIRMED |
| `+5V0_LO` | 5.0 V (rows 8-10) | U30 ADM7151, EN = VIN | **VIN directly (12–17 V)** | Synth: X6→X15 → FB1..FB4 ferrites → ADF4382 U1/U6 5 V domains | none | K=NO | PB U30 (VIN = `VIN`), X6; SY X15 | **CONFLICT / REQUIRES DESIGN REVIEW** — ADM7151 input fed from the 12–17 V bus; check against `7_Components Datasheets and Application notes/ADM7151.pdf` input-voltage rating |
| `+3V3_LO_1` | 3.3 V (row 11) | U27 ADM7151, EN = its input | `+5V0_3` (U26) | Synth: X8→X13 → L12 → U1/U6 V3_LDO, V3_LS, V3_NDIV, V3_PFD, V3_REF, V3_SYNC; 200 k pull-ups R24/R25/R37/R38 | none | K=NO | PB U27, X8; SY X13, L12 | CONFIRMED |
| `+3V3_LO_2` | 3.3 V (row 12) | U29 ADM7151, EN = its input | `+5V0_4` (U28) | Synth: X7→X14 → L13 → U1/U6 V3_OUTDIV, V3_RFOUT1/2, V3_VCOB; RFOUT bias chokes L1..L8 | none | K=NO | PB U29, X7; SY X14, L13 | CONFIRMED (brd has a board-only `+3V3_LO` signal — annotation residue, `docs/PCB/POWER_SUPPLY.md`) |
| `+5V0_ADAR` | 5.0 V | U13 TPS562208, R25 56.2 k / R26 10 k | VIN | Power Board only: U20, U21 LM2662 inputs; X13 output has **no consumer** on Main | `EN_+5V0_ADAR` PE10 (`main.h:104`) | FW: F7 (`main.cpp:1488`, +500 ms) — enables the −5 V ADAR rails indirectly | PB U13, U20, U21, X13; MB: no `+5V0_ADAR` net | CONFIRMED (X13 spare) |
| `-5V0_ADAR12` | −5 V (row 29) | U20 LM2662MX/NOPB (charge-pump inverter) | `+5V0_ADAR` | Main: X21→X13 → ADAR1_, ADAR2_ AVDD | via `EN_+5V0_ADAR` | xlsx L30: AVDD3 (3.3 V) before or with AVDD1 (−5 V); FW: F7 after F6 (+500 ms) — consistent | PB U20, X21; MB X13 | CONFIRMED |
| `-5V0_ADAR34` | −5 V | U21 LM2662 | `+5V0_ADAR` | Main: X20→X15 → ADAR3_, ADAR4_ AVDD | via `EN_+5V0_ADAR` | as above | PB U21, X20; MB X15 | CONFIRMED |
| `+3V3_ADAR_12` (Main: `+3V3_ADAR12`) | 3.3 V (row 30) | U6 TPS562208, R11 32.2 k / R12 10 k | VIN | Main: X14→X20 → L11 `+3V3_ADAR1_F` ADAR1_ AVDD3 ×3; L12 `+3V3_ADAR2_F` ADAR2_ | `EN_+3V3_ADAR12` PE11 (`main.h:106`) | K=YES; FW: F6 (`main.cpp:1485`, +500 ms with ADAR34) | PB U6, X14; MB X20, L11, L12 | CONFIRMED (net name differs by underscore) |
| `+3V3_ADAR_34` (Main: `+3V3_ADAR34`) | 3.3 V | U7 TPS562208, R13 32.2 k / R14 10 k | VIN | Main: X15→X21 → ADAR3_, ADAR4_ AVDD3 (filters analogous) | `EN_+3V3_ADAR34` PE12 (`main.h:108`) | FW: F6 (`main.cpp:1486`) | PB U7, X15; MB X21 | CONFIRMED |
| `+5V0_ADTR` | 5.0 V | U31 TPS562208, R51 56.2 k / R52 10 k | VIN | Power Board only: U32 TPS7A8300 input; X26 output has no consumer | always on (EN = VIN) | — | PB U31, U32, X26 | CONFIRMED (X26 spare) |
| `+3V3_ADTR` | 3.3 V (row 35, VDD_LNA 16 × 80 mA) | U32 TPS7A8300RGRR, EN = `EN_+3V3_ADTR` | `+5V0_ADTR` | Main: X34→X4 → 16 × ADTR1107 VDD_LNA | `EN_+3V3_ADTR` PE13 (`main.h:110`) | xlsx RX power-up step 8 "Set VDD_LNA to 3.3 V" (M38), TX step 6 VDD_LNA = 0 V; FW: **never set HIGH** — only reset at init (`main.cpp:2245-2247`) and power-down (`main.cpp:394`) | PB U32, X34; MB X4; grep of `9_Firmware/9_1_Microcontroller` for `EN_P_3V3_ADTR_Pin` + `GPIO_PIN_SET` = 0 hits | **CONFLICT (firmware never enables the LNA supply)** |
| `+3V3_VDD_SW` | 3.3 V (row 38) | U8 TPS562208, R15 32.2 k / R16 10 k | VIN | Main: X30→X12 → 16 × ADTR1107 VDD_SW | `EN_+3V3_VDD_SW` PE15 (`main.h:114`) | xlsx TX/RX step 2 "Set VDD_SW to 3.3 V" (first ADTR rail); FW: F8 (`ADAR1000_Manager.cpp:51`, +2 ms) | PB U8, X30; MB X12 | CONFIRMED |
| `+3V3_SW` | 3.3 V | U10 TPS562208, R19 32.2 k / R20 10 k | VIN | Power Board only: U18 LM2662 input; X29 output has no consumer | `EN_+3V3_SW` PE14 (`main.h:112`) | FW: F9 (`ADAR1000_Manager.cpp:54`, +2 ms) — enables `-3V3_SW` | PB U10, U18, X29 | CONFIRMED (X29 spare) |
| `-3V3_SW` | −3.3 V (row 37) | U18 LM2662 | `+3V3_SW` | Main: X18→X6 → 16 × ADTR1107 VSS_SW | via `EN_+3V3_SW` | xlsx step 3 "Set VSS_SW to −3.3 V" after VDD_SW; FW F9 after F8 — consistent | PB U18, X18; MB X6 | CONFIRMED |
| `+5V0_PA_1` | 5.0 V (row 40, VDD_PA 250 mA each) | U14 TPS562208, R27 56.2 k / R28 10 k | VIN | Main: X31→X14 → ADTR1107_1, _2, _3, _4, _7 VDD_PA | `EN_+5V0_PA1` PG0 (`main.h:94`) | xlsx TX step 8 "Set VDD_PA to 5 V"; FW: **never set HIGH** (reset at `main.cpp:2239-2241`, power-down `:381`) | PB U14, X31; MB X14, ADTR VDD_PA nets | **CONFLICT (firmware)** |
| `+5V0_PA_2` | 5.0 V | U15 TPS562208, R29 56.2 k / R30 10 k | VIN | Main: X32→X5 → ADTR1107_5, _6, _8, _10, _12 | `EN_+5V0_PA2` PG1 | as above | PB U15, X32; MB X5 | **CONFLICT (firmware)** |
| `+5V0_PA_3` | 5.0 V | U16 TPS562208, R31 56.2 k / R32 10 k | VIN | Main: X33→X7 → ADTR1107_9, _11, _13, _14, _15, _16 | `EN_+5V0_PA3` PG2 | as above | PB U16, X33; MB X7 | **CONFLICT (firmware)** |
| `+5V5_PA` | 5.5 V (row 52) | U17 TPS562208, R33 61.9 k / R34 10 k | VIN | Main: X3→X55 → 4 × OPA4703 V+ (VG drivers); Power Board: U22 input | `EN_+5V5_PA` PG3 (`main.h:118`) | xlsx K=YES; FW: **never set HIGH** (reset at `main.cpp:2239`) | PB U17, X3; MB X55 | **CONFLICT (firmware)** — VG drivers unpowered although `main.cpp:1583-1601` programs them |
| `-5V5_PA` | −5.5 V (row 53) | U22 LM2662 | `+5V5_PA` | Main: X19→X19 → 4 × OPA4703 V− | via `EN_+5V5_PA` | as above | PB U22, X19; MB X19 | **CONFLICT (firmware)** |
| `+3V4` | 3.4 V (row 22) | U11 TPS562208, R21 34.8 k / R22 10 k | VIN | Main: X23→X1 (X54 same net) → 17 × M3SWA2-34DR+ VDD; Power Board: U19 input | always on | K=NO | PB U11, X23; MB X1, X54 | CONFIRMED |
| `-3V4` | −3.4 V (row 23) | U19 LM2662 | `+3V4` | Main: X24→X11 (X22 same net) → 17 × M3SWA2 VEE | always on | K=NO | PB U19, X24; MB X11, X22 | CONFIRMED |
| `+5V0_0` | 5.0 V (row 24) | U12 TPS562208, R23 56.2 k / R24 10 k | VIN | Main: X22→X18 → U4, U8 AD8352 VCC; Power Board: U5 ADM7151 input | always on | K=NO | PB U12, X22; MB X18 | CONFIRMED |
| `+5V0_1` | 5.0 V | U9 TPS562208, R17 56.2 k / R18 10 k | VIN | Power Board: U23 input; X2 spare | always on | — | PB U9, X2 | CONFIRMED (X2 spare) |
| `+5V0_2` | 5.0 V | U24 TPS562208, R37 56.2 k / R38 10 k | VIN | Power Board: U25 input; X9 spare | always on | — | PB U24, X9 | CONFIRMED (X9 spare) |
| `+5V0_3` | 5.0 V | U26 TPS562208, R41 56.2 k / R42 10 k | VIN | Power Board: U27 input; X17 spare | always on | — | PB U26, X17 | CONFIRMED (X17 spare) |
| `+5V0_4` | 5.0 V | U28 TPS562208, R45 56.2 k / R46 10 k | VIN | Power Board: U29 input; X25 spare | always on | — | PB U28, X25 | CONFIRMED (X25 spare) |
| `+5V0_5` | 5.0 V | U33 TPS562208, R55 56.2 k / R56 10 k | VIN | Power Board: U34 input; X28 spare | always on | — | PB U33, X28 | CONFIRMED (X28 spare) |
| `+22V0` / `VD` (PA drain) | 22 V (xlsx row 59: 18–22 V, 2000 mA × 16) | **none in CAD** | external | RF PA board: `22V` AK300/2 → VD → R10 5 mΩ → VIN_M → QPA2962 VD1/VD2 | `EN/DIS_RFPA_VDD` PD6 → JP10 (`main.h:140`; set at `main.cpp:1601`) — switch device NOT IN CAD | xlsx L58-L62 bias-up: ID limit 2840 mA, VG −4 V, then VD +22 V, raise VG until IDQ 1680 mA, then RF; K=YES | PA sch `22V`, R10, X3; xlsx; `docs/PCB/POWER_SUPPLY.md` | **CONFLICT K4 — no 22 V source on the Power Board** |
| `VG_1..16` (PA gate) | −4 … −1.2 V (xlsx row 60; `main.cpp:1583` sets −3.98 V = code 126) | Main Board OPA4703 (OPA_1..4) driven by U7/U69 DAC5578 | `+5V5_PA` / `-5V5_PA` | Main X_1..X_16 → PA X2 → QPA2962 VG via R1..R3 | DAC codes over I2C1; LDAC/CLR PB4/PB5/PB8/PB9 | xlsx: VG before VD | MB VG_n nets, OPA_2.OUTD; PA X2, R1-R3 | PARTIAL (depends on `+5V5_PA`, never enabled) |
| Stepper driver supply | 20 V (xlsx row 63, 4000 mA) | none in CAD | external | "TBS6600" driver | — | — | xlsx row 63 only | MISSING SPEC |
| Cooling | — (xlsx row 64, relay) | none in CAD | external | fans via relay, `EN/DIS_COOLING` PD7 (JP4) | PD7 (`main.cpp:1767-1770`) | "Apply when temperature reaches a threshold (Relay)" | xlsx row 64; MB JP4 | MISSING SPEC |

Rails on the Main Board that have no Power-Board source: none (every Main Board rail connector maps to a Power Board output). Main Board rail names that differ from the Power Board: `+3V3_ADAR12/34` vs `+3V3_ADAR_12/34` (naming only; electrical identity assumed, to be confirmed by the designer) (source: `power_rails.md` §1, closing paragraph).

### 4.2 Firmware enable sequence as coded, not executed on hardware (source: `power_rails.md` §3, copied verbatim)

| Step | Action | Delay after | Source |
|---|---|---|---|
| F0 | `HAL_Delay(180000)` (3 min) then AD9523 RESET low | — | `main.cpp:1237-1238` |
| F1 | `EN_+1V8_CLOCK` high | 100 ms | `main.cpp:1241-1242` |
| F2 | `EN_+3V3_CLOCK` high; AD9523 RESET high; `configure_ad9523()` | 100 ms + 100 ms | `main.cpp:1243-1267` |
| F3 | `EN_+1V0_FPGA` high | 100 ms | `main.cpp:1271-1272` |
| F4 | `EN_+1V8_FPGA` high | 100 ms | `main.cpp:1273-1274` |
| F5 | `EN_+3V3_FPGA` high | 100 ms | `main.cpp:1275-1276` |
| F6 | DIG_3 (PD11) low "mixers off"; `EN_+3V3_ADAR12` + `EN_+3V3_ADAR34` high | 500 ms | `main.cpp:1483-1487` |
| F7 | `EN_+5V0_ADAR` high (→ −5 V ADAR rails) | 500 ms | `main.cpp:1488-1489` |
| F8 | `EN_+3V3_VDD_SW` high | 2 ms | `ADAR1000_Manager.cpp:51-52` (`powerUpSystem()`; whether `systemPowerUpSequence()` reaches it via `initializeADTR1107Sequence()` is UNVERIFIED) |
| F9 | `EN_+3V3_SW` high (→ −3V3_SW) | 2 ms | `ADAR1000_Manager.cpp:54-55` |
| F10 | DAC5578 VG codes written, LDAC pulsed, then `EN/DIS_RFPA_VDD` high (22 V drain) | — | `main.cpp:1560-1601` |
| never | `EN_+3V3_ADTR`, `EN_+5V0_PA1/2/3`, `EN_+5V5_PA` | — | no `GPIO_PIN_SET` write anywhere under `9_Firmware/9_1_Microcontroller/` |
| power-down | ADAR RX mode → `EN_+5V0_PA1..3` low → PA bias safe → `EN_+3V3_ADTR` low → LNA bias 0 → `EN_+3V3_VDD_SW`, `EN_+3V3_SW` low (10 ms steps) | 10 ms | `main.cpp:372-409` |

Comparison with the xlsx (source: `power_rails.md` §3): the 1.8 V-before-3.3 V rule for the AD9523 (L6) and the AVDD3-before-AVDD1 rule for the ADAR1000 (L30) are respected by F1→F2 and F6→F7. The ADTR1107 TX/RX procedures (L31-L46) require VDD_SW, VSS_SW, then VDD_LNA / VDD_PA — the firmware performs F8/F9 but never asserts the LNA (`+3V3_ADTR`) or PA (`+5V0_PA_x`) enables, so the ADTR1107 bias procedure cannot complete as coded. The QPA2962 bias-up (L58-L62: VG −4 V → VD 22 V → raise VG to IDQ 1680 mA) is partially mirrored by F10 (VG −3.98 V then drain enable), but the VG driver supply (`+5V5_PA`) is never enabled. The BETA report lists the firmware defects fixed in `beta/stm32` (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4); whether the five missing enables are among them is documented in chapter 12, not asserted here.

### 4.3 Open items for the power designer (source: `power_rails.md` §4, copied)

1. 22 V PA drain supply: no source, no switch, no cabling in CAD (K4).
2. `+5V0_LO` LDO U30 input tied to the 12–17 V bus — confirm against the ADM7151 rating or add a pre-regulator.
3. `+1V8_CLOCK` output X10 must feed both the Main Board (ADC AVDD) and the Synth Board (AD9523) — add a second output or document a Y-cable.
4. Five `+5V0_n` outputs (X2, X9, X17, X25, X28), X13, X26 and X29 have no destination — mark as spare or remove.
5. Rail current capability per regulator and the VIN total are not documented anywhere; the xlsx gives device budgets only.
6. Firmware: enables for `+3V3_ADTR`, `+5V0_PA_1..3`, `+5V5_PA` are missing (CONFLICT rows above).

## 5. Harness schedule (PROPOSED DESIGN)

The harness schedule DSN-HAR-01 is generated by `tools/design_mechanical_drawings.py` from the proposed internal layout (`tools/design_layout.py`) and the connector positions in the KiCad pick-and-place files. Length = Manhattan distance between connector positions in the head + service allowance (40 mm coax / 60 mm wire), rounded up to 10 mm; lengths are PROPOSED and are to be cut after a first fit. Totals: 144 cables; coax 55; wire 89; total proposed length ≈ 41.6 m (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, header). Cable types follow decision D-15: coax RG-405 (0.086") hand-formable equal-length for Main↔PA and Synth↔Main, Molex 22-01-3027/3037 crimp housings for the 2-/3-pin headers, 20-way IDC ribbon for SV1 (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2, D-15).

Grouping of the 144 rows (source: `HARNESS_SCHEDULE.md`, rows CBL-001…CBL-144; this grouping is a reading aid of the manual, the row content is the source's):

| ID range | Count | From → to | Cable | Notes in the source |
|---|---|---|---|---|
| CBL-001 … CBL-034 | 34 | Power Supply X2..X35 → Main Board / Synth rail connectors | 2-wire 20 AWG, Molex 22-01-2027 both ends | 12 rows have destination "? ?" and length TBD: `+5V0_1..5`, `+3V3_LO_1/2`, `+3V3_CLOCK`, `+5V0_ADAR`, `+3V3_ADAR_12/34`, `+5V0_ADTR`, `+3V3_SW` — "no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md" |
| CBL-035 | 1 | Power Supply SV1 → Main Board SV1 | enable bus (15 EN + GND), 320 mm | — |
| CBL-036 … CBL-042 | 7 | Synth J7/J5/J6/J3/J10/J11/J4 → Main J1/J20/J18/J21/J23/J22/J19 | coax: 100 MHz sys clk, 120 MHz DAC ×2, 400 MHz ADC, LO TX, LO RX, test | 100–170 mm |
| CBL-043 … CBL-044 | 2 | Synth JP1/JP2 → Main JP1/JP13 | control headers | 210 / 240 mm |
| CBL-045 … CBL-140 | 96 | per PA board n = 1..16, six cables each: Main X_n → PA X2 (VG_n, 2-wire 24 AWG shielded), Main X3/X38..X52 → PA X3 (drain current sense, 3-wire 24 AWG twisted), Main J-pair → PA J1 RFIN and PA J2 → Main J-pair (RG-405 SMA-SMA, EQUAL LENGTH set), PA J2 → antenna row n (RG-405 SMA-2.92 mm, EQUAL LENGTH set), DSN-PSU-01 OUTn → PA `22V` (2-wire 18 AWG twisted, AK300/2) | "PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD"; "which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7)"; "antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase" |
| CBL-141 … CBL-142 | 2 | slip ring VIN → Power Supply X1; slip ring VIN → DSN-PSU-01 IN | 2 × 2-wire 16 AWG | 340 / 470 mm |
| CBL-143 | 1 | slip ring USB → Main Board X53 | USB 2.0 shielded, mini-B | 360 mm |
| CBL-144 | 1 | Main Board stepper pins → pedestal TB6600 (via slip ring) | 3-wire 24 AWG shielded, TBD | "the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head (then only motor phases cross: 4 circuits) — DECISION NEEDED" |

The full 144-row schedule is in [engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md](engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md) and, machine-readable, in `engineering/DESIGN/HARNESS/harness_schedule.csv`; Appendix B reproduces it.

Two cable-ID schemes coexist in the repository and must not be confused: the interconnection table uses two-digit IDs `CBL-00…CBL-106` assigned per signal group (e.g. CBL-01 = `+1V0_FPGA` X4→X8, CBL-21 = the whole SV1 ribbon, CBL-40..55 = the RF pairs), whereas the harness schedule uses three-digit IDs `CBL-001…CBL-144` assigned per physical cable in connector order (e.g. CBL-003 = `+1V0_FPGA` X4→X8, CBL-035 = the SV1 ribbon, CBL-047/048 = PA1 RF pair) (source: `engineering/SYSTEM/interfaces/interconnection_table.md` §2–3, §7; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` rows CBL-003, CBL-035, CBL-047). The manual keeps each ID in the form of its source and records the duplication as observation MAN-03 in chapter 17. The twelve "? ?" rows of the harness schedule correspond to the rails that the interconnection table resolves either to Synth connectors through series inductors (`+3V3_LO_1/2`, `+3V3_CLOCK` → SY X13/X14/X11 via L12/L13/L10; CBL-23, CBL-25, CBL-26) or to spare outputs with no consumer (`+5V0_1..5`, `+5V0_ADAR`, `+5V0_ADTR`, `+3V3_SW`), and `+3V3_ADAR_12/34`, which the interconnection table matches to Main X20/X21 despite the one-underscore name difference (CBL-07, CBL-08) (source: `interconnection_table.md` §2, §4).
