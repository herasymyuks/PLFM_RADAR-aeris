# AERIS-10 — Assembly and integration sequence

| Field | Value |
|---|---|
| Project | AERIS-10 |
| Document | ASM-SEQ-01 |
| Revision | A |
| Date | 2026-10-09 |
| Status | **PARTIAL** — electrical integration order is SOURCE-DERIVED (connector matrix + firmware power sequence); mechanical steps are CONCEPTUAL because no enclosure/antenna/pedestal design exists |

Nothing in this sequence has been executed on hardware. Steps marked ⚠ depend on a design decision that is still open (conflicts K1–K8 in `docs/SYSTEM/BLOCK_DIAGRAM.md`).

## A. Pre-assembly inspection checkpoints (per PCB assembly)

| CP | Check | Acceptance | Evidence/tool |
|---|---|---|---|
| CP-1 | Bare board matches outline and hole table | dimensions per `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md`, ±0.2 mm (vendor tolerance UNSPECIFIED) | caliper; fab CoC |
| CP-2 | Assembled board matches BOM + pick-and-place | every reference populated with the BOM value; polarity per `drawings/<BOARD>_assembly_top.pdf` | AOI / visual |
| CP-3 | No shorts between rails | > 1 kΩ between every rail and GND before power-up (rail list `engineering/ELECTRICAL/power_distribution/power_rails.md`) | DMM |
| CP-4 | Power Board rails at nominal with no load | each X2..X35 output within the net-name voltage (currents UNKNOWN) | bench PSU + DMM |

## B. Electrical integration order (bench, no enclosure)

1. **Power Board alone** — apply VIN (12–17 V per xlsx) through X1; verify CP-4. ⚠ U30 ADM7151 input from VIN needs design review (`power_rails.md` §4).
2. **Main Board ↔ Power Board** — connect the 20-way enable bus SV1↔SV1 (CBL-20) and the rail cables CBL-01..CBL-15 (Molex 22-23-2021, 2-pin, pin order of the `S` pads UNVERIFIED — buzz out before connecting). All rails are enabled only by the STM32, so nothing but the always-on rails should be present until firmware runs.
3. **Program the STM32** (SWD; firmware image MISSING today) and observe the enable sequence F0–F10 (`power_rails.md` §3): +1V8_CLOCK → +3V3_CLOCK → +1V0/+1V8/+3V3 FPGA → ADAR rails → switch rails. ⚠ HSE 8 MHz (board) vs 25 MHz (firmware) must be resolved first or the PLL will not lock.
4. **Frequency Synthesizer** — connect power X10..X15 (rails +3V3_XO, +3V3_CLOCK, +1V8_CLOCK, +3V3_LO_1, +3V3_LO_2, +5V0_LO) and control headers JP1↔Main JP1, JP2↔Main JP13 (CBL-30..); then SMA clocks Synth J7→Main J1 (FPGA 100 MHz), J5/J6→J20/J18 (DAC 120 MHz), J3→J21 (ADC 400 MHz), LO J10→Main J23 (TX), J11→J22 (RX) — table `interconnection_table.md` §5–6. Verify AD9523 lock and output frequencies with a counter (acceptance: 100 / 120 / 400 MHz ± 1 ppm, firmware intent `main.cpp:933-1072`).
5. **Program the FPGA** (bitstream MISSING; ⚠ part number XC7A50T vs XC7A100T) via JP3 JTAG; check the STM32↔FPGA handshake DIG_0..4 (PD8..PD12).
6. **RF PA boards (16)** — for each PA n: VG cable CBL-56+n from Main X_k (mapping X_7=VG_1 … X_10=VG_16 per `interconnection_table.md` §7 — PA-instance assignment UNDOCUMENTED, label cables on first build), sense cable to X3/X38..X52, 22 V drain from the external PA supply (⚠ K4). Bias-up per xlsx L58-L62: VG −4 V → VD 22 V → raise VG to IDQ 1.68 A. ⚠ Firmware never enables +5V5_PA / +5V0_PA_x / +3V3_ADTR as coded (`power_rails.md` §3) — fix before this step.
7. **RF interconnect** — Main J24..J55 ↔ PA J1/J2 (which SMA of each pair is RFIN vs RFOUT is UNVERIFIED — determine from the Main Board switch RF_SW_n routing before cabling). Terminate unused ports with 50 Ω.
8. **Host link** — mini-USB X53 → PC; GUI_V5 enumerates CDC; send settings packet (⚠ firmware RX callback never bound, defect C4). Radar data path FPGA→host does not exist (FT601 unwired, K3).
9. **Antenna** — ⚠ no design; connect only after an antenna/feed design exists.

## C. Mechanical assembly (CONCEPTUAL — to be rewritten once enclosure CAD exists)

| Step | Action | Fasteners | Inspection |
|---|---|---|---|
| M1 | Mount Power Board on chassis base using the 8 × Ø3.2 holes (`POWER_SUPPLY_dimensions.md` §2) | M3 (inferred from hole size) | stand-off height ≥ tallest bottom-side part (UNKNOWN) |
| M2 | Mount Main Board above/next to it using 10 × Ø3.2 holes; keep SMA field (J1..J55) accessible | M3 (inferred) | RF connector clearance UNKNOWN |
| M3 | Mount Synth board (4 × Ø3.2) close to Main J1/J18/J20/J21/J22/J23 to keep coax short | M3 (inferred) | — |
| M4 | Mount 16 PA boards (7 × Ø3.2 each) on a heat-spreader; thermal interface under QPA2962 | M3 (inferred) | thermal design MISSING |
| M5 | Route harness per cable IDs; strain-relieve coax | — | continuity per `interconnection_table.md` |
| M6 | Install antenna panel and pedestal | — | BLOCKED — no CAD |

## D. Evidence to collect during first integration

Rail voltages (CP-4), AD9523 lock + frequencies (B.4), STM32 CDC enumeration log (B.8), PA IDQ per board (B.6), photos of the first harness with cable labels → store under `engineering/VALIDATION/` and update `docs/TESTING/ACCEPTANCE_CRITERIA.md` (AC-S6, AC-S7, AC-F9).
