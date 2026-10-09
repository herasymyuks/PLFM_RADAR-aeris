# Power Supply Board (PowerBoard) — BETA board

Project AERIS-10 · `beta/pcb/POWER_SUPPLY/` · 2026-10-09 · **Status: BETA — KiCad/Freerouting-routed, DRC-checked, NOT complete (89 connections still open, see `UNROUTED.md`), not reviewed by the original designer, not fabricated.**

Source of this copy: `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` (kicad-cli EAGLE import of `PowerBoard.brd`; 2 layers, 280 × 300 mm). The source layout was unfinished: 309 airwires and 132 of 320 footprints parked outside the outline (y = +77 … +701 mm).

## 1. Before / after

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 308 | 89 |
| clearance | 53 | 56 |
| drill_out_of_range | 8 | 8 |
| isolated_copper | 4 | 0 |
| silk_over_copper | 40 | 168 |
| silk_overlap | 22 | 65 |
| solder_mask_bridge | 8 | 8 |
| track_dangling | 4 | 2 |
| via_dangling | 0 | 20 |
| zones_intersect | 21 | 1 |
| **DRC violations total** | 160 | 328 |

Unconnected items 308 → **89** (−71 %). Footprints outside the outline 132 → **0**. Reports: `exports/reports/DRC_report.txt|json`.

## 2. What was changed (chronological, all logged)

| # | Change | Result | Tool / log |
|---|---|---|---|
| 1 | Netclass `Default`: track 0.25 mm, clearance 0.2 mm, via 0.5/0.3 mm (routing rule for new copper only) | — | `POWER_SUPPLY.kicad_pro` |
| 2 | 110 parts placed inside the outline in 29 net clusters next to the inside parts they connect to (1 mm grid, 3 mm edge margin, no overlap with existing parts/tracks/pours); 22 KK-254 connectors (`22-23-2021`) placed on the nearest board edge | 132 → 0 outside | `tools/beta_place_outside.py`, `placement_moves.json`, `placement_moves_connectors.json` |
| 3 | Freerouting 2.5.0 pass 1 (20 passes, existing 916 tracks/vias exported `(type fix)`), SES merged additively | +1336 tracks, +168 vias; unconnected 308 → 102 | `POWER_SUPPLY.dsn/.ses`, `freerouting.log`, `ses_merge.json` |
| 4 | 45 overlapping same-net zones re-prioritised; board-wide B.Cu GND zone `BETA_GND_plane_B.Cu` added (priority 0 — the EAGLE B.Cu GND polygon already covers the board, so it only fills remaining gaps) | zones_intersect 21 → 1 | `tools/beta_zone_priorities.py`, `tools/beta_add_plane.py` |
| 5 | Straight same-net bridges for the gaps in the DRC list, DRC, revert of every bridge that caused a clearance/crossing violation | 102 tried, 29 kept; 102 → 96 | `tools/beta_bridge_unconnected.py`, `bridges_pass1.json` |
| 6 | Freerouting pass 2 on the bridged board (12 passes) | +36 tracks, +3 vias; 96 → 96 | `POWER_SUPPLY_pass2.ses`, `freerouting_pass2.log`, `ses_merge_pass2.json` |
| 7 | GND stitching: vias where B.Cu GND islands overlap F.Cu GND fills, via next to unconnected GND pads; DRC-violating ones reverted | 50 tried, 22 kept; 96 → 89 | `tools/beta_gnd_stitch.py`, `stitch_gnd.json` |
| 8 | Refill, DRC, package export | | `tools/beta_drc.sh`, `tools/beta_export_package.sh`, `exports/EXPORT_LOG.md` |

## 3. What remains

* **89 unconnected items** — listed with reasons and a manual procedure in `UNROUTED.md` (49 GND, 10 VIN, rest on regulator outputs). Root causes: the EAGLE design distributes VIN/GND through separate local pours joined only by airwires (an autorouter does not connect pour to pour), and the autorouted bottom tracks fragment the B.Cu GND plane.
* DRC (`exports/reports/DRC_report.txt`): clearance 56 (0.15 mm pad-to-pad inside the ADM7151/TPS7A83 footprints and 3 N$ tracks of the source — footprint/library level, EAGLE DRU allowed 0.15 mm there), drill_out_of_range 8 (0.254 mm via-pads in the TPS7A8300 footprint vs DRU 0.3 mm min drill — footprint level, fab to confirm), silk_over_copper 168 / silk_overlap 65 (reference texts of the parts placed by script sit on their own pads — cosmetic, to be tidied with `tools/beta_silk_nudge.py` once routing is final), via_dangling 20 (autorouter vias whose second-side wire was dropped — remove with *Cleanup tracks & vias* once routing is final), solder_mask_bridge 8, track_dangling 2, zones_intersect 1.
* Placement by script is topological, not thermal/EMC: the regulator clusters sit where free space was nearest to their connectors. **A designer must review the placement** (inductor orientation, input/output capacitor proximity, heat spreading) before any routing clean-up.
* 24 pins without net in the schematic (`engineering/ELECTRICAL/netlists/POWER_SUPPLY_unresolved_connections.md`: TPS7A8300 feedback-select pins, LM2662 FC/OSC) are not a layout issue but must be dispositioned before fabrication.

## 4. Files

`POWER_SUPPLY.kicad_pcb` / `.kicad_pro` (BETA board), `BOM_POWER_SUPPLY_beta.csv` (7 HIGH / 18 MEDIUM / 3 LOW / 0 EMPTY lines), `FAB_NOTES.md`, `UNROUTED.md`, logs listed above, `exports/`.
