# Main Board (RADAR_Main_Board) — BETA board

Project AERIS-10 · `beta/pcb/MAIN_BOARD/` · 2026-10-09 · **Status: BETA — KiCad-checked, 15 → 0 unconnected, not reviewed by the original designer, not fabricated.**

Source of this copy: `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` (kicad-cli EAGLE import of `RADAR_Main_Board.brd`; 10 layers, 260 × 300 mm, 784 footprints, 10219 tracks). All existing tracks were kept untouched (no autorouter output was merged into this board; the Freerouting run on the locked DSN was stopped during its fanout stage because the nine remaining connections were routed by hand instead).

## 1. Before / after

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 15 | 0 |
| clearance | 63 | 72 |
| hole_clearance | 4 | 87 |
| shorting_items | 93 | 125 |
| silk_edge_clearance | 3 | 3 |
| silk_over_copper | 199 | 199 |
| silk_overlap | 199 | 199 |
| solder_mask_bridge | 199 | 199 |
| track_dangling | 136 | 130 |
| via_dangling | 15 | 35 |
| zones_intersect | 1 | 0 |
| **DRC violations total** | 912 | 1049 |

Silk/mask counts are capped at 199 by the KiCad report (see the synthesizer `DRC_DISPOSITION.md` for the explanation). Reports: `exports/reports/DRC_report.txt|json`.

## 2. What was changed (all logged, nothing in the netlist)

| # | Change | Tool / log |
|---|---|---|
| 1 | 7 arc tails (same net/layer/width, inside the arc copper) where EAGLE arcs end exactly on a pad centre but KiCad reported arc ↔ pad unconnected: AMP_IN_P→L9.1, +3V3_AN→L18.1 and L16.1, RF_RX_FIL→U$3.P$2, VG_11→R121.1, DAC_2_VG_CLR→U69.12, N$49→R19.1 | `tools/beta_fix_stubs.py --arc-tail 0.3`, `fixes_stubs.json` |
| 2 | +3V3_FT input filter (L19 L5650M, C159 22 µF 1206, C184 10 µF 0805, C185 100 nF 0402, C186 1 nF 0402) moved from outside the outline (y ≈ +63…+75 mm) to the free area at (5…12, −232…−240) on F.Cu next to X16 (`+3V3_FPGA`/`GND` KK header) | `tools/beta_place_outside.py --skip-nonet`, `placement_moves.json` |
| 3 | Hand routing of that cluster: 4 GND vias 0.45/0.20 mm into the inner GND planes (In1/In4/In6/In8), +3V3_FT bus 0.3 mm F.Cu at y = −233.3, +3V3_FPGA feed 0.5 mm F.Cu C159.1 → (3.3, −235) → (3.3, −223.5) → X16.1; two straight bridges kept from the scripted attempt (L19.1↔C159.1, C184.1↔L19.2) | `manual_routing.json`, `bridges.json` |
| 4 | 30 net-less footprint copper polygons (BPF2 filters U$2/U$3, U13, U5): 14 unambiguous ones re-created as board-level copper polygons carrying the net they touch (GND ×8, RF_TX, RF_RX ×2, RF_TX_FIL ×2, RF_RX_FIL); 4 ambiguous (touch GND **and** an RF net) and 12 isolated left unchanged | `tools/beta_polygon_nets.py --to-board`, `POLYGON_NET_DISPOSITION.md` |
| 5 | Overlapping same-net zones re-prioritised | `zone_priorities.json` |
| 6 | Refill, DRC, package export | `exports/EXPORT_LOG.md` |

R60, R61, R83, R84, R145, R146 (33 Ω 0201, no net on either pin in the schematic) stay outside the outline and are marked `dnp = yes` in the BOM — placing unconnected parts would be a design decision.

## 3. What remains (1049 DRC items, 0 unconnected)

| Type | Count | Disposition |
|---|---|---|
| shorting_items | 125 | **REAL (schematic)**: GND tracks/arcs run through the thermal-via pads `V…V_8` of U69 (DAC5578) and U7 — those pads have **no net** because the schematic symbols have no paddle pin; EAGLE connected them with the GND polygon. Also the 4 ambiguous BPF2 polygons (GND + RF net) and KK headers JP7/JP8/JP10/JP17. Not changed in BETA (assigning a net to a pad changes the netlist) → designer must add the paddle pins to the symbols or confirm the intended net |
| hole_clearance / clearance | 87 / 72 | same U69/U7 no-net via pads and the 4 ambiguous BPF2 polygons (RF_TX/RF_RX/…_FIL ↔ GND): follow-on of the item above; plus 3 at ADAR1_0/ADAR3_0/J33 from the source |
| track_dangling | 130 | EAGLE stub ends inside pours/pads — cosmetic, copper not modified |
| via_dangling | 35 | 20 vias of RF_TX/RF_RX/RF_TX_FIL/RF_RX_FIL inside the BPF2 pads (connected on F.Cu to the pad polygon, nothing on B.Cu — footprint-level, designer to confirm the filter footprint) + 15 from the source (ADAR load/enable nets) |
| silk_overlap / silk_over_copper / solder_mask_bridge | 199+ each | cosmetic / fab CAM (0201 density), as on the synthesizer |
| silk_edge_clearance | 3 | X53 outline and JP3 reference at the board edge — cosmetic |
| zones_intersect | 0 | — |

Schematic-level open points that block fabrication regardless of layout: FT601 (U6) supply/control pins unconnected, 280 unconnected symbol pins, single-pin nets (`engineering/ELECTRICAL/netlists/MAIN_BOARD_unresolved_connections.md`).

## 4. Files

`MAIN_BOARD.kicad_pcb` / `.kicad_pro`, `BOM_MAIN_BOARD_beta.csv` (23 HIGH / 41 MEDIUM / 30 LOW / 4 EMPTY lines), `FAB_NOTES.md` (10-layer hybrid stack-up proposal; 50 Ω = 0.204 mm, 100 Ω diff = 0.204/0.26 mm measured), `POLYGON_NET_DISPOSITION.md`, logs, `exports/`.
