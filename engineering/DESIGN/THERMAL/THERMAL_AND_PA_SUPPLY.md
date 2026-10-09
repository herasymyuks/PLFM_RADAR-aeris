# Thermal budget and 22 V PA supply sizing — DSN-THM-01 (PROPOSED DESIGN)

Rev A · 2026-10-09 · generator `tools/design_thermal.py` · inputs `engineering/DESIGN/design_parameters.json` · decisions D-10, D-11, D-14. First-order estimates; no measurement.

## 1. Duty cycle from the firmware timing (`main.cpp:180-186`)

| Quantity | Value |
|---|---|
| TX time per beam position | 16 × 30 µs + 16 × 0.5 µs = **488.0 µs** |
| Frame per beam position | 16 × 167 + 175.4 + 16 × 175 = **5647.4 µs** |
| RF duty | **8.64 %** |
| Drain-gate duty (switch on 5 µs around each chirp, assumption) | **11.47 %** |

## 2. Dissipation per QPA2962 (datasheet: VD 22 V, IDQ 1.68 A, PSAT 40 dBm, PAE 22 %)

| State | DC power | Dissipation |
|---|---|---|
| Quiescent, no RF | 37.0 W | **37.0 W** |
| At PSAT (PIN 27 dBm) | 43.2 W | 33.7 W |
| Design value per PA while the drain is on | — | **37.0 W** |

## 3. System cases (16 PAs)

| Case | Total PA dissipation | Verdict |
|---|---|---|
| A continuous drain bias (firmware as coded: VD left on) | **591 W** | INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ 142 CFM at ΔT_air 12 K) |
| B drain gated per chirp (D-14), duty 11.5 % | **68 W** | design case |
| C drain gated per CPI frame only (on during the 5.6 ms frame, off while the stepper moves) | **532 W** | INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ 142 CFM at ΔT_air 12 K) |

**Conclusion (D-10/D-14):** the firmware as coded (VD left on after bias-up, `main.cpp:1560-1601`) puts the head in case A. The proposal therefore requires per-chirp drain gating (D-14) — a hardware function (the 22 V switch module) driven by a timing line; after that the thermal design is case B: **68 W** average.

## 4. Heat path, case B

| Element | Value | Basis |
|---|---|---|
| Average dissipation per PA | 4.24 W | §1–2 |
| R(PA board thermal-via field) | 1.5 °C/W | ASSUMPTION — the RF_PA board stack-up and via field under U$1 must be checked (`engineering/PCB/RF_PA/`) |
| R(TIM) + local spreading | 0.3 + 0.2 °C/W | assumption (thermal pad 1–3 W/mK, 5 × 5 mm) |
| ΔT PA base → plate | 8.5 °C | |
| Plate temperature allowed (TBASE ≤ 85 °C) | ≤ 77 °C | datasheet |
| Required plate-to-air resistance at 45 °C ambient | ≤ **0.46 °C/W** | (T_plate,max − T_amb)/P |
| Heat spreader (D-11) | 300 × 300 × 10 mm Al; PAs 4 × 4 on the rear centre; antenna panel on the front centre | `MECHANICAL/` |
| Fin fields | 2 side strips 55 mm wide × 280 mm, 26 fins 25 × 2 mm at 4 mm pitch, area 0.39 m² | D-11 |
| R(lateral spreading, 10 mm Al, ~100 mm, both sides) | 0.09 °C/W | k = 200 W/mK |
| R(fins → air, forced, h = 25 W/m²K) | 0.10 °C/W | ASSUMPTION h |
| Resulting plate / PA base temperature | **58 °C / 66 °C** at 45 °C ambient | margin to 85 °C: 19 °C |
| Airflow for ΔT_air = 12 K with margin ×1.5 | **16 CFM** (7.7 L/s) → 2 × 60 mm fans (≥ 15 CFM each) in the side ducts, intake bottom, exhaust top, controlled by the existing fan relay (xlsx row 64) | |

Not included: Power Board regulator losses (currents UNKNOWN), Main Board (FPGA/ADC/clock ≈ 10–20 W estimate), solar load on the radome — add a 30 % margin when selecting the fans.

## 5. 22 V drain supply (D-14)

| Quantity | Value |
|---|---|
| Peak drain current (all 16 PAs at ID_max 2.848 A) | **45.6 A** during each 30 µs chirp |
| Average current, case B (IDQ × gate duty + RF increment × RF duty) | **3.47 A** → 76 W |
| Average current, case A (continuous bias) | 27.3 A → 600 W (not supported by the proposal) |
| Bulk capacitance for ΔV ≤ 0.5 V over a chirp (total) | **2734 µF** → ≥ 220 µF low-ESR polymer per PA board (local, 171 µF each) + 2 × 1000 µF/35 V at the switch module |
| Input current at VIN_min 12 V, η 92% | 6.9 A average (case B) |
| Converter | synchronous boost 12–17 V → 22 V, 2-phase interleaved (LM5122 ×2 or equivalent), 150 W continuous rating, 300 kHz, 2 × 10 µH / 15 A inductors, output ripple < 100 mV |
| Protection / enable | LM5069 hot-swap controller + N-FET high-side switch on the 22 V bus, EN from `EN/DIS_RFPA_VDD` (STM32), current limit 12 A average, dv/dt-limited turn-on; status to the MCU |
| Per-PA pulse gating | 16 × high-side P-FET (−40 V, 30 A pulsed) with fast high-side driver (e.g. LTC7003, ≤ 100 ns), common `TX_GATE` TTL input from the FPGA (spare I/O to be allocated — UNRESOLVED), local 220 µF per channel |
| Sequencing | VG (−4 V via DAC5578) before VD (firmware already does this); gate switch only after `EN/DIS_RFPA_VDD`; power-down reverse |

See `../ELECTRICAL/PA_SUPPLY_22V/` for the block schematic, netlist and BOM.
