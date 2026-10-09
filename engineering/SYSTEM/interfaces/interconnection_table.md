# AERIS-10 — Inter-board interconnection table (SYS-02 companion)

Drawing ID SYS-02 · Revision A · Date 2026-10-09 · Status SOURCE-DERIVED. One row per wire/signal of every edge in `hardware_interconnection.dot`. Pins are the EAGLE pin names of the connector symbols (`tools/extract_eagle_netlist.py` logic applied to the four `.sch` files); Molex 22-23-20x1 symbols name **all** pads `S`, so their pin *order* cannot be read from the schematic and is written `S` (UNVERIFIED order). Cable IDs `CBL-xx` are a **proposal of this document**, not from the original project. "Power requirement" is copied from `3_Power Management/Power Management V6.xlsx` (column G, mA, per device) only where the rail maps to a single row; otherwise UNKNOWN. Status: CONFIRMED = both ends found in the schematics with the same net meaning; UNVERIFIED = one end or the pin order cannot be established; MISSING SPEC = no cable/part/number exists in the repository.

Evidence shorthand: `MB` = `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch`, `PB` = `.../PowerBoard/PowerBoard.sch`, `SY` = `.../FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch` (+ `.brd` silkscreen), `PA` = `.../PowerAmplifierBoard/RF_PA.sch`, `main.h` = `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h`, `xlsx` = `3_Power Management/Power Management V6.xlsx` (row numbers of sheet `Feuil1`).

## 1. DC input

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| External DC source (not specified) | — | — | VIN 12–17 V | Power Board | X1 AK300/2 | KL (1) | DC power | UNKNOWN (sum not computed in xlsx) | CBL-00 | PB X1 nets `VIN`,`GND`; brd silk `Vin [12-17]V` | MISSING SPEC (source) |
| External DC source | — | — | GND | Power Board | X1 AK300/2 | KL (2) | DC power | — | CBL-00 | PB X1 | MISSING SPEC |

## 2. Power Board → Main Board rails (Molex 22-23-2021 → 22-23-2021, 2 wires each)

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

## 3. Main Board → Power Board enable bus (SV1 MA10-2 ↔ SV1 MA10-2, 20-way)

Pin map is identical on both boards (nets per `PB SV1` and `MB SV1`); MCU pin per `main.h:94-123` and `MB U2` nets.

| Source device | Source connector | Pin | Signal (MCU pin) | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board | SV1 | 1 | `EN_+1V0_FPGA` (PE7) | Power Board | SV1 | 1 | 3.3 V CMOS → TPS562208 U1 EN | — | CBL-21 | MB SV1.1, U2.PE7; PB SV1.1, U1.EN | CONFIRMED |
| Main Board | SV1 | 2 | `EN_+5V0_PA2` (PG1) | Power Board | SV1 | 2 | 3.3 V CMOS → U15 EN | — | CBL-21 | MB/PB SV1.2 | CONFIRMED |
| Main Board | SV1 | 3 | `EN_+1V8_FPGA` (PE8) | Power Board | SV1 | 3 | → U2 EN | — | CBL-21 | SV1.3 | CONFIRMED |
| Main Board | SV1 | 4 | `EN_+5V0_PA3` (PG2) | Power Board | SV1 | 4 | → U16 EN | — | CBL-21 | SV1.4 | CONFIRMED |
| Main Board | SV1 | 5 | `EN_+3V3_FPGA` (PE9) | Power Board | SV1 | 5 | → U4 EN | — | CBL-21 | SV1.5 | CONFIRMED |
| Main Board | SV1 | 6 | `EN_+5V5_PA` (PG3) | Power Board | SV1 | 6 | → U17 EN | — | CBL-21 | SV1.6 | CONFIRMED |
| Main Board | SV1 | 7 | `EN_+5V0_ADAR` (PE10) | Power Board | SV1 | 7 | → U13 EN | — | CBL-21 | SV1.7 | CONFIRMED |
| Main Board | SV1 | 8 | `EN_+1V8_CLOCK` (PG4) | Power Board | SV1 | 8 | → ADM7151 U25 EN | — | CBL-21 | SV1.8 | CONFIRMED |
| Main Board | SV1 | 9 | `EN_+3V3_ADAR12` (PE11) | Power Board | SV1 | 9 | → U6 EN | — | CBL-21 | SV1.9 | CONFIRMED |
| Main Board | SV1 | 10 | `EN_+3V3_CLOCK` (PG5) | Power Board | SV1 | 10 | → ADM7151 U23 EN | — | CBL-21 | SV1.10 | CONFIRMED |
| Main Board | SV1 | 11 | `EN_+3V3_ADAR34` (PE12) | Power Board | SV1 | 11 | → U7 EN | — | CBL-21 | SV1.11 | CONFIRMED |
| Main Board | SV1 | 12,14,16,18,20 | GND | Power Board | SV1 | 12,14,16,18,20 | — | — | CBL-21 | SV1 | CONFIRMED |
| Main Board | SV1 | 13 | `EN_+3V3_ADTR` (PE13) | Power Board | SV1 | 13 | → TPS7A8300 U32 EN | — | CBL-21 | SV1.13 | CONFIRMED (firmware never sets it high — see power_rails.md) |
| Main Board | SV1 | 15 | `EN_+3V3_SW` (PE14) | Power Board | SV1 | 15 | → U10 EN | — | CBL-21 | SV1.15 | CONFIRMED |
| Main Board | SV1 | 17 | `EN_+3V3_VDD_SW` (PE15) | Power Board | SV1 | 17 | → U8 EN | — | CBL-21 | SV1.17 | CONFIRMED |
| Main Board | SV1 | 19 | `EN_+5V0_PA1` (PG0) | Power Board | SV1 | 19 | → U14 EN | — | CBL-21 | SV1.19 | CONFIRMED |

Note: `docs/SYSTEM/BLOCK_DIAGRAM.md` says "16 × EN"; the connector carries **15** enable nets (pins 1–11, 13, 15, 17, 19) and 5 grounds.

## 4. Power Board → Frequency Synthesizer Board rails (Molex 22-23-2021, 2 wires each)

Synth-side nets are anonymous (`N$69..N$77`) and reach the named rail through a series inductor (`SY L9..L13`), which is how the rail identity was established.

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement (xlsx) | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Power Board | X35 | S | `+3V3_XO` | Synth Board | X10 (`N$69` → L9 → `+3V3_XO`) | S | DC power 3.3 V | 1200+25+25 mA (rows 2,4,5) | CBL-22 | PB X35; SY X10, L9, X4/X5/X6 VDD | CONFIRMED |
| Power Board | X11 | S | `+3V3_CLOCK` | Synth Board | X11 (`N$71` → L10 → `+3V3_CLOCK`) | S | DC power 3.3 V | 250 mA (row 6) | CBL-23 | PB X11; SY X11, L10, IC1 VDD3_* | CONFIRMED |
| Power Board | X10 | S | `+1V8_CLOCK` | Synth Board | X12 (`N$73` → L11 → `+1V8_CLOCK`) | S | DC power 1.8 V | 250 mA (row 7) | CBL-24 | PB X10; SY X12, L11, IC1 VDD1.8_* | UNVERIFIED — same PB X10 also needed by Main X17 (CBL-06); a Y-cable or second output is not in CAD |
| Power Board | X8 | S | `+3V3_LO_1` | Synth Board | X13 (`N$75` → L12 → `+3V3_LO_1`) | S | DC power 3.3 V | 2×240 mA (row 11) | CBL-25 | PB X8; SY X13, L12, U1/U6 V3_LDO/LS/NDIV/PFD/REF/SYNC | CONFIRMED |
| Power Board | X7 | S | `+3V3_LO_2` | Synth Board | X14 (`N$77` → L13 → `+3V3_LO_2`) | S | DC power 3.3 V | 2×340 mA (row 12) | CBL-26 | PB X7; SY X14, L13, U1/U6 V3_OUTDIV/RFOUT/VCOB | CONFIRMED |
| Power Board | X6 | S | `+5V0_LO` | Synth Board | X15 (`+5V0_LO`) | S | DC power 5 V | 2×(200+0.3+70) mA (rows 8-10) | CBL-27 | PB X6; SY X15, FB1..FB4 | CONFIRMED |

## 5. Main Board ↔ Frequency Synthesizer Board control headers

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

## 6. Frequency Synthesizer Board → Main Board clocks and LO (coaxial)

Frequencies are the values programmed in `main.cpp:970-1028` (AD9523 channel dividers from a 3.6 GHz PLL2) and `adf4382a_manager.h:32-34`; they are firmware intent, not measurements.

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

## 7. Main Board ↔ RF PA boards (16 instances)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board RF_SW_n (n = 1..16) RFOUT1 / RFOUT2 via 1 pF | J27/J26 (n=1), J29/J28 (2), J25/J24 (3), J31/J30 (4), J35/J34 (5), J37/J36 (6), J33/J32 (7), J39/J38 (8), J47/J46 (9), J41/J40 (10), J45/J44 (11), J43/J42 (12), J55/J54 (13), J49/J48 (14), J53/J52 (15), J51/J50 (16) | 1 | element RF (TX to PA / RX return) | RF PA board n | J1 `RFIN` / J2 `RFOUT` | 1 | 50 Ω coax, 10.5 GHz | — | CBL-40..CBL-55 | MB RF_SW_n pins (traced through C126/C128-type 1 pF caps); PA J1 (`N$2`), J2 (`N$8`), brd silk | UNVERIFIED — which SMA of each pair is RFIN vs RFOUT and PA-instance mapping are not documented |
| Main Board (U7/U69 DAC5578 → OPA4703 → `VG_n`) | X_7=VG_1, X_16=VG_2, X_8=VG_3, X_15=VG_4, X_4=VG_5, X_11=VG_6, X_3=VG_7, X_12=VG_8, X_5=VG_9, X_14=VG_10, X_6=VG_11, X_13=VG_12, X_2=VG_13, X_9=VG_14, X_1=VG_15, X_10=VG_16 (Molex 22-23-2021) | S (VG), S (GND) | gate bias `VG_n` (xlsx: −4 … −1.2 V, 10 mA) | RF PA board | X2 Molex 22-23-2021 | 1 `VG`, 2 `GND` | analogue DC | 10 mA (row 60) | CBL-56..CBL-71 | MB X_n nets `VG_n`; PA X2 | CONFIRMED (VG_n → PA instance assignment UNVERIFIED) |
| RF PA board (R10 WSL2816 5 mΩ shunt: `VD` / `VIN_M`) | X3 Molex 22-23-2031 | 1 `VD`, 2 `VIN_M`, 3 `GND` | drain current sense pair | Main Board (INA241A3 U11 for X3, U73 for X38, …) | X3, X38..X52 Molex 22-23-2031 | S (`GND`), S (`N$207`=IN+), S (`N$209`=IN−) (X3 example) | analogue differential sense | — | CBL-72..CBL-87 | PA X3, R10; MB X3 → U11.IN+/IN−, X38 → U73 … | CONFIRMED topology; pin ORDER UNVERIFIED (pads named `S`), PA-instance → Main-connector map NOT DOCUMENTED |
| +22 V drain supply (NOT IN CAD) | — | — | `VD` 22 V (xlsx row 59: 18–22 V, 2000 mA, "Set VD +22 V") | RF PA board | `22V` AK300/2 terminal | KL1 `VD`, KL2 `GND` | DC power | 2 A per board (xlsx) | CBL-88 | PA part `22V`; xlsx row 59; Power Board has no 22 V rail (K4) | MISSING SPEC |
| Main Board (U2 PD6) | JP10 PINHD-1X3 | 1 `EN/DIS_RFPA_VDD`, 3 GND | PA drain enable (set in `main.cpp:1601`) | PA drain switch — device NOT IN CAD | — | — | 3.3 V CMOS | — | — | MB JP10; `main.h:140` | MISSING SPEC |

## 8. Main Board ↔ host and off-board modules

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

## 9. Antenna

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RF PA board n | J2 `RFOUT` | 1 | element n TX (AERIS-10X) | antenna array element | — | — | 50 Ω coax / waveguide transition | 10 W per element (README) | — | README.md; RADAR_V6.drawio | MISSING SPEC (no antenna CAD, K8) |
| Main Board | J24..J55 | 1 | element RF (AERIS-10N direct) | antenna array element | — | — | 50 Ω | ~1 W per element (README) | — | README.md | MISSING SPEC |
