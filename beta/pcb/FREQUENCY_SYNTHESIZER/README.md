# Frequency Synthesizer (Clocks_Freq_Synth_board) — BETA board

Project AERIS-10 · `beta/pcb/FREQUENCY_SYNTHESIZER/` · 2026-10-09 · **Status: BETA — KiCad-checked, silkscreen-cleaned, not reviewed by the original designer, not fabricated.**

Source of this copy: `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` (kicad-cli EAGLE import of `Clocks_Freq_Synth_board.brd`). Copper was **not modified** (fully routed in the source, 0 unconnected).

## 1. Before / after

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 0 | 0 |
| courtyards_overlap | 7 | 7 |
| silk_over_copper | 199 | 199 |
| silk_overlap | 199 | 199 |
| solder_mask_bridge | 199 | 199 |
| track_dangling | 35 | 35 |
| **DRC violations total** | 639 | 639 |

The silkscreen and mask counts are capped at 199 by KiCad; uncapped measurements and the classification of every type are in `DRC_DISPOSITION.md` (cosmetic silk/mask vs. real). Real items for review: 7 courtyard overlaps.

## 2. What was changed

| # | Change | Tool / log |
|---|---|---|
| 1 | 43 silkscreen reference texts moved to the nearest free position (≤ 3 mm, 0.05 mm step; copper untouched) | `tools/beta_silk_nudge.py`, `silk_nudges.json`; 103 texts still in conflict → `silk_conflicts_remaining.json` |
| 2 | Zones refilled, DRC re-run, package exported | `tools/beta_drc.sh`, `tools/beta_export_package.sh`, `exports/EXPORT_LOG.md` |

## 3. What remains

See `DRC_DISPOSITION.md`: 7 courtyard overlaps (review), 35 GND arc stubs (cosmetic), silk/mask items (cosmetic / fab CAM). Recommendation for the production revision: hide 0201 reference designators on silk.

## 4. Files

`FREQUENCY_SYNTHESIZER.kicad_pcb` / `.kicad_pro` / `_from_eagle.kicad_dru`, `BOM_FREQUENCY_SYNTHESIZER_beta.csv` (10 HIGH / 22 MEDIUM / 6 LOW / 2 EMPTY lines), `FAB_NOTES.md` (6-layer RO4350B/FR-4 stack-up proposal, 50 Ω / 100 Ω geometry measured w = 0.204 mm, s = 0.26 mm), `DRC_DISPOSITION.md`, `exports/`.
