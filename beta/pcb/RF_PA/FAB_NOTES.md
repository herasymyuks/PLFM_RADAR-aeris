# RF Power Amplifier (RF_PA) — Fabrication notes and stack-up proposal

Project AERIS-10 · BETA · `beta/pcb/RF_PA/FAB_NOTES.md` · 2026-10-09

> **Status: PROPOSED (BETA).** Every value below is a proposal derived from the EAGLE design rules (DRU) in the source `.brd`,
> the PCBWay impedance note shipped with the Frequency Synthesizer production files and measurements taken on the KiCad
> conversion with pcbnew. Nothing has been confirmed by the original designer or by PCBWay. The stack-up must be
> re-solved by the fabricator (field solver + coupons) before any order.

## 1. Board

| Item | Value | Source |
|---|---|---|
| Outline | 35 × 60 mm | `exports/mechanical/RF_PA_outline.dxf` (Edge.Cuts) |
| Copper layers | 4 | EAGLE layerSetup / KiCad stack |
| EAGLE design rules | `PCBWay_4L_100um-Track` | `<designrules>` in the source `.brd`, mapped in `engineering/PCB/RF_PA/reports/design_rules_mapping.md` |
| Fabricator template | PCBWay standard 4-layer (PROPOSED) | DRU name |

## 2. Stack-up (PROPOSED)

| # | KiCad layer | EAGLE | Copper | Dielectric below (DRU) | Proposed material |
|---|---|---|---|---|---|
| 1 | F.Cu | 1 | 35 µm base | 0.11 mm (impedance note: 0.102 mm) | **Rogers RO4350B 4 mil** (RF layer; QPA2962 PA) |
| 2 | In1.Cu | 2 | 35 µm | 1.2 mm | FR-4 core |
| 3 | In2.Cu | 15 | 35 µm | 0.11 mm | FR-4 prepreg (or RO4350B if bottom RF — none routed on B.Cu) |
| 4 | B.Cu | 16 | 35 µm | — | — |

Finished thickness **1.6 mm ± 10 %** (DRU sum 1.42 mm + copper ≈ 1.56 mm). Thermal: the QPA2962 ground paddle (U$1 polygon, now a GND copper polygon) carries 21 GND vias 0.35/0.15 mm — PROPOSED: fill these vias (via-in-pad, filled and capped) because the paddle is a solder surface; designer/fab to confirm.

## 3. Materials and finish (PROPOSED)

| Parameter | Proposal | Rationale |
|---|---|---|
| Base material | see stack-up (FR-4 Tg ≥ 150 °C; RO4350B outer layer where RF is routed) | `Stack_Hybrid.png` in the source tree, DRU dielectric table, impedance note |
| Copper weight | 1 oz (35 µm) all layers, finished outer ~40–45 µm | DRU mtCopper 0.035 mm; impedance note |
| Surface finish | **ENIG** (2–5 µin Au over 120–240 µin Ni) | RF/LGA/BGA assembly (ADAR1000 LGA, XC7A50T BGA, 0201 passives); flat pads |
| Solder mask | green, LPI, both sides; **no mask over RF traces on the RF layer** (maskless microstrip per impedance note) — RF nets listed in §4 | impedance note |
| Silkscreen | white, top (and bottom where B.SilkS is non-empty); fab to clip silk from pads | export set |
| Min track / space | 0.10 mm / 0.15 mm | DRU |
| Min drill (finished hole) | 0.15 mm (0.35 mm via) | DRU / drill report |
| Copper-to-edge | 0.3 mm | DRU |
| Via treatment | tented (mask over vias) except RF-layer vias near maskless traces — fab to confirm; filled+capped only where noted | proposal |
| Impedance control | yes — see §4; coupons for every target | impedance note |
| Electrical test | 100 % flying probe / fixture, IPC-D-356 netlist supplied (`exports/ipc/RF_PA_netlist.d356`) | export set |
| Acceptance | IPC-A-600 Class 2 (PROPOSED) | — |
| Panelisation | none specified (single board); PCBWay may panelise with rails, no V-cut through the RF area | — |

## 4. Controlled impedance (PROPOSED targets, measured geometry)

| Net | Target | Measured on the KiCad board | Note |
|---|---|---|---|
| `N$2`, `N$8` (SMA ↔ PA RF input/output, F.Cu) | 50 Ω single-ended ± 10 % | w = **0.204 mm**, F.Cu, 2 segments each | same geometry as the impedance note (RO4350B h = 0.102 mm, maskless) |
| `VIN_M`, `VD`, `VG` (bias) | — | 0.37 / 0.6 / 0.8 / 2.0 mm | DC |

Nets are unnamed in the source (`N$x`), identified by their connection to the 142-0731-211 SMA jacks. The RF tracks were NOT modified in BETA.

## 5. Deliverables in `exports/`

Gerber RS-274X (X2 attributes, Protel extensions, `*-job.gbrjob`), Excellon drills PTH/NPTH with PDF maps and `drill_report.txt`, copper/assembly/outline PDFs, per-layer SVG, DXF outline + top fab, STEP (board body only), pick-and-place CSV, IPC-2581 and IPC-D-356, DRC report (text + JSON), board statistics, 3-D renders, BETA BOM with proposed MPNs.

## 6. Open items for the fabricator / designer

1. Confirm the stack-up materials and total thickness (the DRU gives dielectric thicknesses but no material or total).
2. Confirm the RF layer dielectric (0.102 vs 0.11 mm) and re-solve w/s with coupons.
3. Confirm surface finish and mask opening policy on RF traces.
4. Review the DRC disposition in `README.md` / `DRC_DISPOSITION.md` (where present) before CAM.
