# Main Board (RADAR_Main_Board) — Fabrication notes and stack-up proposal

Project AERIS-10 · BETA · `beta/pcb/MAIN_BOARD/FAB_NOTES.md` · 2026-10-09

> **Status: PROPOSED (BETA).** Every value below is a proposal derived from the EAGLE design rules (DRU) in the source `.brd`,
> the PCBWay impedance note shipped with the Frequency Synthesizer production files and measurements taken on the KiCad
> conversion with pcbnew. Nothing has been confirmed by the original designer or by PCBWay. The stack-up must be
> re-solved by the fabricator (field solver + coupons) before any order.

## 1. Board

| Item | Value | Source |
|---|---|---|
| Outline | 260 × 300 mm rectangular (`exports/mechanical/MAIN_BOARD_outline.dxf`) | `exports/mechanical/MAIN_BOARD_outline.dxf` (Edge.Cuts) |
| Copper layers | 10 | EAGLE layerSetup / KiCad stack |
| EAGLE design rules | `PCBWay_8L_100um-Track (NOTE: the DRU is named for 8 layers but the board uses 10 copper layers — EAGLE layerSetup `(1*2+3*4+5*12+13*14+15*16)`; the fabricator template must be the 10-layer one)` | `<designrules>` in the source `.brd`, mapped in `engineering/PCB/MAIN_BOARD/reports/design_rules_mapping.md` |
| Fabricator template | PCBWay standard 10-layer (PROPOSED) | DRU name |

## 2. Stack-up (PROPOSED)

| # | KiCad layer | EAGLE | Copper | Dielectric below (DRU mtIsolate) | Proposed material |
|---|---|---|---|---|---|
| 1 | F.Cu | 1 | 35 µm base (~40–45 µm finished) | 0.102 mm | **Rogers RO4350B 4 mil** (impedance layer, maskless RF per note) |
| 2 | In1.Cu | 2 | 35 µm | 0.200 mm | FR-4 prepreg (Tg ≥ 170 °C) |
| 3 | In2.Cu | 3 | 35 µm | 0.200 mm | FR-4 core |
| 4 | In3.Cu | 4 | 35 µm | 0.200 mm | FR-4 prepreg |
| 5 | In4.Cu | 5 | 35 µm | 0.200 mm | FR-4 core |
| 6 | In5.Cu | 12 | 35 µm | 0.150 mm | FR-4 prepreg |
| 7 | In6.Cu | 13 | 35 µm | 0.200 mm | FR-4 core |
| 8 | In7.Cu | 14 | 35 µm | 0.200 mm | FR-4 prepreg |
| 9 | In8.Cu | 15 | 35 µm | 0.102 mm | **Rogers RO4350B 4 mil** (mirror of layer 1 — only if bottom RF routing exists; otherwise FR-4) |
| 10 | B.Cu | 16 | 35 µm | — | — |

Dielectric sum 1.554 mm + 10 × 35 µm copper ≈ **1.9 mm**. PROPOSED finished thickness **2.0 mm ± 10 %** (PCBWay standard 10-layer builds are 1.6 or 2.0 mm; the DRU sum does not fit 1.6 mm). The controlled impedance depends only on the outer 0.102 mm RO4350B layer, so the fabricator may re-balance the inner dielectrics freely.

## 3. Materials and finish (PROPOSED)

| Parameter | Proposal | Rationale |
|---|---|---|
| Base material | see stack-up (FR-4 Tg ≥ 150 °C; RO4350B outer layer where RF is routed) | `Stack_Hybrid.png` in the source tree, DRU dielectric table, impedance note |
| Copper weight | 1 oz (35 µm) all layers, finished outer ~40–45 µm | DRU mtCopper 0.035 mm; impedance note |
| Surface finish | **ENIG** (2–5 µin Au over 120–240 µin Ni) | RF/LGA/BGA assembly (ADAR1000 LGA, XC7A50T BGA, 0201 passives); flat pads |
| Solder mask | green, LPI, both sides; **no mask over RF traces on the RF layer** (maskless microstrip per impedance note) — RF nets listed in §4 | impedance note |
| Silkscreen | white, top (and bottom where B.SilkS is non-empty); fab to clip silk from pads | export set |
| Min track / space | 0.10 mm / 0.10 mm | DRU |
| Min drill (finished hole) | 0.15 mm (0.35 mm via, 0.15 mm drill — micro-size mechanical drill, PCBWay "advanced" class) | DRU / drill report |
| Copper-to-edge | 0.3 mm | DRU |
| Via treatment | tented (mask over vias) except RF-layer vias near maskless traces — fab to confirm; filled+capped only where noted | proposal |
| Impedance control | yes — see §4; coupons for every target | impedance note |
| Electrical test | 100 % flying probe / fixture, IPC-D-356 netlist supplied (`exports/ipc/MAIN_BOARD_netlist.d356`) | export set |
| Acceptance | IPC-A-600 Class 2 (PROPOSED) | — |
| Panelisation | none specified (single board); PCBWay may panelise with rails, no V-cut through the RF area | — |

## 4. Controlled impedance (PROPOSED targets, measured geometry)

| Net group (examples) | Target | Measured on the KiCad board (pcbnew) | Reference geometry (PCBWay note, RO4350B h = 0.102 mm, maskless) |
|---|---|---|---|
| RF lines on F.Cu: `RF_IO*`, `RF_TX*`, `RF_RX*`, `ANTx_y`, `TXx_y`, `RXx_y`, `DAC_CLOCK`, `FPGA_*_CLOCK*`, `STM32_OSC*` | 50 Ω single-ended ± 10 % | w = **0.204 mm**, F.Cu (10219-track census: 2729 segments at 0.204 mm) | w = 0.204 mm (process Dk 3.48) / 0.195 mm (design Dk 3.66) |
| Differential pairs: `ADC_CLK_IN_P/N`, `FPGA_ADC_CLOCK_P/N`, `MIX_RX_P/N`, `ADC_IF_IN_P/N`, `AMP_IF_IN_P/N` | 100 Ω differential ± 8 % | w = **0.204 mm**, s = **0.26 mm** edge-to-edge (FPGA_ADC_CLOCK, MIX_RX); ADC_CLK_IN s = 0.288 mm; AMP_IF_IN runs uncoupled (s = 1.58 mm) | w = 0.204 mm, s = 0.26 mm |
| `+1V8_CLOCK_F` etc. (0.25 mm) and signal 0.10/0.15 mm | not impedance controlled | — | — |

The impedance note is a Frequency Synthesizer document; the Main Board uses the same w/s geometry on the same outer dielectric (DRU mtIsolate 0.102 mm), so the same targets are proposed. The 0.102 mm-under-F.Cu assumption must be confirmed — if the Main Board is built on plain FR-4 the 0.204 mm lines are not 50 Ω.

## 5. Deliverables in `exports/`

Gerber RS-274X (X2 attributes, Protel extensions, `*-job.gbrjob`), Excellon drills PTH/NPTH with PDF maps and `drill_report.txt`, copper/assembly/outline PDFs, per-layer SVG, DXF outline + top fab, STEP (board body only), pick-and-place CSV, IPC-2581 and IPC-D-356, DRC report (text + JSON), board statistics, 3-D renders, BETA BOM with proposed MPNs.

## 6. Open items for the fabricator / designer

1. Confirm the stack-up materials and total thickness (the DRU gives dielectric thicknesses but no material or total).
2. Confirm the RF layer dielectric (0.102 vs 0.11 mm) and re-solve w/s with coupons.
3. Confirm surface finish and mask opening policy on RF traces.
4. Review the DRC disposition in `README.md` / `DRC_DISPOSITION.md` (where present) before CAM.
