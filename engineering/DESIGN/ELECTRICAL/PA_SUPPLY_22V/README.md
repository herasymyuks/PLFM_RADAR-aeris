# DSN-PSU-01 — 22 V PA drain supply, enable switch and per-PA pulse gating (PROPOSED DESIGN)

Rev A · 2026-10-09 · closes conflict K4 (22 V PA supply not in CAD) per decision D-14. Block schematic `DSN-PSU-01_block_schematic.svg` (+ PDF/PNG), BOM `DSN-PSU-01_BOM.csv`, net summary `DSN-PSU-01_netlist.csv`.

| Requirement | Value | Source |
|---|---|---|
| Input | 12–17 V (system VIN via slip ring) | xlsx VIN |
| Output | 22 V ± 2 %, 8 A continuous, 46 A pulsed (11.5 % duty) | QPA2962 datasheet, timing |
| Bulk energy | ≥ 2734 µF total for ΔV ≤ 0.5 V per 30 µs chirp | `THERMAL_AND_PA_SUPPLY.md` §5 |
| Enable | `EN/DIS_RFPA_VDD` (existing STM32 pin) → hot-swap switch | `main.h` |
| Pulse gate | `TX_GATE` from the FPGA — **spare pin to allocate (UNRESOLVED)**; without it the system runs case A (591 W) | D-14 |
| Telemetry | PGOOD/FAULT to the MCU (pin to allocate); per-PA drain current already measured by INA241 on the Main Board | schematic |
| Mechanical | 120 × 80 × 25 mm on the head rear wall (DSN-MECH-01) | layout |

Next steps (MDR-12): KiCad component-level schematic → layout (4-layer, 2 oz) → bench test of one gate channel with a 30 µs / 45 A dummy load → EMC pre-check of the boost.
