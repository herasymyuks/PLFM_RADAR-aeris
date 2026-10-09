# AERIS-10 — Power rail register (SYS-04 / ELEC-PWR-01 companion)

Revision A · Date 2026-10-09 · Status SOURCE-DERIVED. Every rail is taken from `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch` (regulator pin nets and feedback-divider resistors, extracted from the EAGLE XML with the same method as `tools/extract_eagle_netlist.py`), cross-checked against `3_Power Management/Power Management V6.xlsx` (sheet `Feuil1`; row numbers quoted), the STM32 enable macros in `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h:94-123`, the enable order in `main.cpp` / `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.cpp`, and the consumer connectors on the Main Board (`RADAR_Main_Board.sch`) and Synth Board (`Clocks_Freq_Synth_board.sch`).

Conventions. **Nominal V** is the value encoded in the net name (e.g. `+1V8_FPGA` → 1.8 V) and the xlsx column H "SELECTED VOLTAGE"; feedback resistor values are listed as evidence but output voltages were **not recomputed** (the TPS562208 datasheet is not in the repository — only `tps562201.pdf`). **Current ratings are UNKNOWN** unless the xlsx gives a per-device budget (column G, mA); regulator capability is not asserted. **Enable** = net on the Power Board EN pin (`VIN` or own input = always on). **Sequence step** columns: `xlsx` = text of column L/K, `FW` = firmware order F1..F9 defined in section 3. Status: CONFIRMED = regulator, nets and consumer connector all found; PARTIAL = found but something inconsistent; UNVERIFIED = consumer or cable cannot be established; CONFLICT = contradicts another source.

## 1. Rail register

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

Rails on the Main Board that have **no Power-Board source**: none (every Main Board rail connector maps to a Power Board output, section 1). Main Board rail names that differ from the Power Board: `+3V3_ADAR12/34` vs `+3V3_ADAR_12/34` (naming only; electrical identity assumed, to be confirmed by the designer).

## 2. Enable-bus pin map (SV1 MA10-2, identical on both boards)

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

15 enable lines (not 16 as stated in `docs/SYSTEM/BLOCK_DIAGRAM.md`). All enables are driven as push-pull outputs initialised LOW in `MX_GPIO_Init` (`main.cpp:2239-2247`); the Power Board has no pull-downs/pull-ups on the EN nets visible in the netlist (not checked exhaustively — REQUIRES VERIFICATION).

## 3. Firmware enable sequence (as coded; not executed on hardware)

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

Comparison with the xlsx: the 1.8 V-before-3.3 V rule for the AD9523 (L6) and the AVDD3-before-AVDD1 rule for the ADAR1000 (L30) are respected by F1→F2 and F6→F7. The ADTR1107 TX/RX procedures (L31-L46) require VDD_SW, VSS_SW, then VDD_LNA / VDD_PA — the firmware performs F8/F9 but never asserts the LNA (+3V3_ADTR) or PA (+5V0_PA_x) enables, so the ADTR1107 bias procedure cannot complete as coded. The QPA2962 bias-up (L58-L62: VG −4 V → VD 22 V → raise VG to IDQ 1680 mA) is partially mirrored by F10 (VG −3.98 V then drain enable), but the VG driver supply (`+5V5_PA`) is never enabled.

## 4. Open items for the power designer

1. 22 V PA drain supply: no source, no switch, no cabling in CAD (K4).
2. `+5V0_LO` LDO U30 input tied to the 12–17 V bus — confirm against the ADM7151 rating or add a pre-regulator.
3. `+1V8_CLOCK` output X10 must feed both the Main Board (ADC AVDD) and the Synth Board (AD9523) — add a second output or document a Y-cable.
4. Five `+5V0_n` outputs (X2, X9, X17, X25, X28), X13, X26 and X29 have no destination — mark as spare or remove.
5. Rail current capability per regulator and the VIN total are not documented anywhere; the xlsx gives device budgets only.
6. Firmware: enables for `+3V3_ADTR`, `+5V0_PA_1..3`, `+5V5_PA` are missing (CONFLICT rows above).
