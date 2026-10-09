# Frequency Synthesizer (Clocks_Freq_Synth_board) — Fabrication notes and stack-up proposal

Project AERIS-10 · BETA · `beta/pcb/FREQUENCY_SYNTHESIZER/FAB_NOTES.md` · 2026-10-09

> **Status: PROPOSED (BETA).** Every value below is a proposal derived from the EAGLE design rules (DRU) in the source `.brd`,
> the PCBWay impedance note shipped with the Frequency Synthesizer production files and measurements taken on the KiCad
> conversion with pcbnew. Nothing has been confirmed by the original designer or by PCBWay. The stack-up must be
> re-solved by the fabricator (field solver + coupons) before any order.

## 1. Board

| Item | Value | Source |
|---|---|---|
| Outline | 100 × 100 mm | `exports/mechanical/FREQUENCY_SYNTHESIZER_outline.dxf` (Edge.Cuts) |
| Copper layers | 6 | EAGLE layerSetup / KiCad stack |
| EAGLE design rules | `PCBWay_6L_100um-Track` | `<designrules>` in the source `.brd`, mapped in `engineering/PCB/FREQUENCY_SYNTHESIZER/reports/design_rules_mapping.md` |
| Fabricator template | PCBWay standard 6-layer (PROPOSED) | DRU name |

## 2. Stack-up (PROPOSED)

| # | KiCad layer | EAGLE | Copper | Dielectric below (DRU) | Proposed material |
|---|---|---|---|---|---|
| 1 | F.Cu | 1 | 35 µm base (~40–45 µm finished) | 0.11 mm (impedance note: 0.102 mm) | **Rogers RO4350B 4 mil** (RF/LVDS layer, maskless RF traces) |
| 2 | In1.Cu | 2 | 35 µm | 0.6 mm | FR-4 core (GND reference under layer 1) |
| 3 | In2.Cu | 3 | 35 µm | 0.11 mm | FR-4 prepreg |
| 4 | In3.Cu | 14 | 35 µm | 0.6 mm | FR-4 core |
| 5 | In4.Cu | 15 | 35 µm | 0.11 mm | FR-4 prepreg (or RO4350B — B.Cu carries the AD9523_OUT8/9 pairs at 0.204 mm, so a symmetric RO4350B bottom layer is PROPOSED) |
| 6 | B.Cu | 16 | 35 µm | — | — |

Dielectric sum 1.53 mm + 6 × 35 µm ≈ **1.74 mm**: PROPOSED finished thickness **1.6 mm ± 10 %** with the fabricator thinning the two 0.6 mm cores, or 2.0 mm if the cores are kept — to be decided with PCBWay. The DRU 0.11 mm vs the note's 0.102 mm outer dielectric must be reconciled (RO4350B 4 mil = 0.101 mm).

## 3. Materials and finish (PROPOSED)

| Parameter | Proposal | Rationale |
|---|---|---|
| Base material | see stack-up (FR-4 Tg ≥ 150 °C; RO4350B outer layer where RF is routed) | `Stack_Hybrid.png` in the source tree, DRU dielectric table, impedance note |
| Copper weight | 1 oz (35 µm) all layers, finished outer ~40–45 µm | DRU mtCopper 0.035 mm; impedance note |
| Surface finish | **ENIG** (2–5 µin Au over 120–240 µin Ni) | RF/LGA/BGA assembly (ADAR1000 LGA, XC7A50T BGA, 0201 passives); flat pads |
| Solder mask | green, LPI, both sides; **no mask over RF traces on the RF layer** (maskless microstrip per impedance note) — RF nets listed in §4 | impedance note |
| Silkscreen | white, top (and bottom where B.SilkS is non-empty); fab to clip silk from pads | export set |
| Min track / space | 0.10 mm / 0.10 mm | DRU |
| Min drill (finished hole) | 0.15 mm (0.35 mm via) | DRU / drill report |
| Copper-to-edge | 0.3 mm | DRU |
| Via treatment | tented (mask over vias) except RF-layer vias near maskless traces — fab to confirm; filled+capped only where noted | proposal |
| Impedance control | yes — see §4; coupons for every target | impedance note |
| Electrical test | 100 % flying probe / fixture, IPC-D-356 netlist supplied (`exports/ipc/FREQUENCY_SYNTHESIZER_netlist.d356`) | export set |
| Acceptance | IPC-A-600 Class 2 (PROPOSED) | — |
| Panelisation | none specified (single board); PCBWay may panelise with rails, no V-cut through the RF area | — |

## 4. Controlled impedance (PROPOSED targets, measured geometry)

| Net group | Target | Measured on the KiCad board (pcbnew) | Reference (PCBWay note) |
|---|---|---|---|
| LVDS/clock pairs `AD9523_OUT0..9_P/N`, `ADF4382_TX/RX_SYNC_P/N`, `TX/RX_RFOUT_1/2_P/N` | 100 Ω differential ± 8 % | w = **0.204 mm**, s = **0.26 mm** (OUT0/1/8 pairs, F.Cu and B.Cu); RX_SYNC s = 0.296 mm; RFOUT pairs run with s ≈ 0.8 mm (uncoupled) | w = 0.204 mm, s = 0.26 mm (process Dk 3.48) |
| Single-ended `100MHZ_OUT`, `10MHZ_OUT`, `VCXO_OUT`, `AD9523_OUT6/7/10/11+` | 50 Ω ± 10 % | w = 0.204 mm (0.22 mm on some OUT+ stubs) | w = 0.204 mm |
| SPI/control (`ADF4382_*`, `AD9523_SCLK`) | — | 0.10 / 0.15 / 0.22 mm | not controlled |

The impedance note (`4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf`) belongs to this board: continuous GND under the RF layer, no solder mask on RF traces, coupons for 50 Ω and 100 Ω, PCBWay may tune w by ±0.02–0.04 mm and s by ±0.03–0.05 mm.

## 5. Deliverables in `exports/`

Gerber RS-274X (X2 attributes, Protel extensions, `*-job.gbrjob`), Excellon drills PTH/NPTH with PDF maps and `drill_report.txt`, copper/assembly/outline PDFs, per-layer SVG, DXF outline + top fab, STEP (board body only), pick-and-place CSV, IPC-2581 and IPC-D-356, DRC report (text + JSON), board statistics, 3-D renders, BETA BOM with proposed MPNs.

## 6. Open items for the fabricator / designer

1. Confirm the stack-up materials and total thickness (the DRU gives dielectric thicknesses but no material or total).
2. Confirm the RF layer dielectric (0.102 vs 0.11 mm) and re-solve w/s with coupons.
3. Confirm surface finish and mask opening policy on RF traces.
4. Review the DRC disposition in `README.md` / `DRC_DISPOSITION.md` (where present) before CAM.
