# Power Supply Board (PowerBoard) — Fabrication notes and stack-up proposal

Project AERIS-10 · BETA · `beta/pcb/POWER_SUPPLY/FAB_NOTES.md` · 2026-10-09

> **Status: PROPOSED (BETA).** Every value below is a proposal derived from the EAGLE design rules (DRU) in the source `.brd`,
> the PCBWay impedance note shipped with the Frequency Synthesizer production files and measurements taken on the KiCad
> conversion with pcbnew. Nothing has been confirmed by the original designer or by PCBWay. The stack-up must be
> re-solved by the fabricator (field solver + coupons) before any order.

## 1. Board

| Item | Value | Source |
|---|---|---|
| Outline | 280 × 300 mm | `exports/mechanical/POWER_SUPPLY_outline.dxf` (Edge.Cuts) |
| Copper layers | 2 | EAGLE layerSetup / KiCad stack |
| EAGLE design rules | `PCBWay_2L_100um-Track` | `<designrules>` in the source `.brd`, mapped in `engineering/PCB/POWER_SUPPLY/reports/design_rules_mapping.md` |
| Fabricator template | PCBWay standard 2-layer (PROPOSED) | DRU name |

## 2. Stack-up (PROPOSED)

| # | KiCad layer | EAGLE | Copper | Dielectric below (DRU) | Proposed material |
|---|---|---|---|---|---|
| 1 | F.Cu | 1 | 35 µm (**PROPOSED 70 µm / 2 oz** — power distribution board, VIN rails are 2 mm polygons; designer to decide) | 1.5 mm | FR-4 Tg 150 °C core (standard PCBWay 2-layer) |
| 2 | B.Cu | 16 | 35 µm (same proposal) | — | — |

Finished thickness **1.6 mm ± 10 %** (DRU 1.5 mm core + copper). No controlled impedance.

## 3. Materials and finish (PROPOSED)

| Parameter | Proposal | Rationale |
|---|---|---|
| Base material | see stack-up (FR-4 Tg ≥ 150 °C; RO4350B outer layer where RF is routed) | `Stack_Hybrid.png` in the source tree, DRU dielectric table, impedance note |
| Copper weight | 1 oz (35 µm) all layers, finished outer ~40–45 µm | DRU mtCopper 0.035 mm; impedance note |
| Surface finish | **ENIG** (2–5 µin Au over 120–240 µin Ni) | RF/LGA/BGA assembly (ADAR1000 LGA, XC7A50T BGA, 0201 passives); flat pads |
| Solder mask | green, LPI, both sides; **no mask over RF traces on the RF layer** (maskless microstrip per impedance note) — RF nets listed in §4 | impedance note |
| Silkscreen | white, top (and bottom where B.SilkS is non-empty); fab to clip silk from pads | export set |
| Min track / space | 0.10 mm (BETA routing 0.25 mm) / 0.20 mm | DRU |
| Min drill (finished hole) | 0.30 mm (0.5 mm via) | DRU / drill report |
| Copper-to-edge | 0.3 mm | DRU |
| Via treatment | tented (mask over vias) except RF-layer vias near maskless traces — fab to confirm; filled+capped only where noted | proposal |
| Impedance control | yes — see §4; coupons for every target | impedance note |
| Electrical test | 100 % flying probe / fixture, IPC-D-356 netlist supplied (`exports/ipc/POWER_SUPPLY_netlist.d356`) | export set |
| Acceptance | IPC-A-600 Class 2 (PROPOSED) | — |
| Panelisation | none specified (single board); PCBWay may panelise with rails, no V-cut through the RF area | — |

## 4. Controlled impedance (PROPOSED targets, measured geometry)

No RF or LVDS nets on this board. Routing added in BETA uses 0.25 mm tracks / 0.2 mm clearance (netclass set in `POWER_SUPPLY.kicad_pro`); existing EAGLE routing uses 0.15–2.0 mm. Via 0.5/0.3 mm (DRU min drill 0.3 mm).

## 5. Deliverables in `exports/`

Gerber RS-274X (X2 attributes, Protel extensions, `*-job.gbrjob`), Excellon drills PTH/NPTH with PDF maps and `drill_report.txt`, copper/assembly/outline PDFs, per-layer SVG, DXF outline + top fab, STEP (board body only), pick-and-place CSV, IPC-2581 and IPC-D-356, DRC report (text + JSON), board statistics, 3-D renders, BETA BOM with proposed MPNs.

## 6. Open items for the fabricator / designer

1. Confirm the stack-up materials and total thickness (the DRU gives dielectric thicknesses but no material or total).
2. Confirm the RF layer dielectric (0.102 vs 0.11 mm) and re-solve w/s with coupons.
3. Confirm surface finish and mask opening policy on RF traces.
4. Review the DRC disposition in `README.md` / `DRC_DISPOSITION.md` (where present) before CAM.
