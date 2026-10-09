# RF Power Amplifier (RF_PA) — BETA board

Project AERIS-10 · `beta/pcb/RF_PA/` · 2026-10-09 · **Status: BETA — KiCad-routed, DRC-checked, not reviewed by the original designer, not fabricated.**

Source of this copy: `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` (kicad-cli EAGLE import of `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd`). The EAGLE originals and the engineering conversion were not modified.

## 1. Before / after

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 1 | 0 |
| clearance | 16 | 1 |
| shorting_items | 7 | 0 |
| silk_edge_clearance | 1 | 1 |
| silk_over_copper | 8 | 8 |
| silk_overlap | 8 | 8 |
| zones_intersect | 8 | 0 |
| **DRC violations total** | 48 | 18 |

Reports: `exports/reports/DRC_report.txt|json` (after), `engineering/PCB/RF_PA/reports/DRC_report.txt` (before).

## 2. What was changed (all logged, nothing in the netlist)

| # | Change | Tool / log | Why |
|---|---|---|---|
| 1 | GND strap F.Cu 0.5 mm from via (16.20, −11.20) to the QPA2962 ground paddle centre (16.20, −13.40) | `tools/beta_fix_stubs.py --extra`, `fixes.json` | the only unconnected item: the paddle was connected to the GND via field only through a net-less footprint polygon, which KiCad does not count as copper of the net |
| 2 | QPA2962 (U$1) footprint copper polygon (paddle, F.Cu) re-created as a board-level copper polygon with net **GND** and removed from the footprint — identical geometry | `tools/beta_polygon_nets.py --to-board`, `POLYGON_NET_DISPOSITION.md` | it touched 21 GND items and nothing else (unambiguous); as a net-less footprint graphic it produced 7 shorting + 19 hole-clearance + 15 clearance false errors |
| 3 | 6 overlapping GND zones on F.Cu given distinct priorities (same net, same outlines) | `tools/beta_zone_priorities.py`, `zone_priorities.json` | `zones_intersect` ×8 — equal-priority same-net overlap is only a KiCad ambiguity |
| 4 | Zones refilled, DRC re-run, package exported | `tools/beta_drc.sh`, `tools/beta_export_package.sh`, `exports/EXPORT_LOG.md` | |

RF tracks (`N$2`, `N$8` at 0.204 mm, bias lines) were **not** touched.

## 3. What remains (18 DRC items)

| Type | Count | Disposition |
|---|---|---|
| clearance | 1 | GND paddle polygon ↔ `VIN_M` track stub at (17.46, −15.63): 0.123 mm < 0.15 mm DRU. Exists in the source; RF/bias copper not modified in BETA → **designer to confirm or nudge the VIN_M stub** |
| silk_overlap | 8 | board texts `VIN+`/`VIN−` over the X3 connector outline; UNK22V0 footprint texts over its own outline — cosmetic |
| silk_over_copper | 8 | X2/X3 KK-connector outlines over their THT pads, J1/J2/U$1 silk over a mask-defined area — cosmetic, fab clips silk on pads |
| silk_edge_clearance | 1 | UNK22V0 reference field 0.1 mm from the board edge — cosmetic |

Unconnected: **0**. Unrouted list: none (`UNROUTED.md` not needed).

## 4. Files

`RF_PA.kicad_pcb` / `.kicad_pro` (BETA board), `BOM_RF_PA_beta.csv` (MPN proposals: 5 lines HIGH / 6 MEDIUM / 0 LOW / 0 EMPTY), `FAB_NOTES.md` (stack-up and impedance proposal), `POLYGON_NET_DISPOSITION.md`, `fixes.json`, `zone_priorities.json`, `exports/` (full package, see `FAB_NOTES.md` §5).
