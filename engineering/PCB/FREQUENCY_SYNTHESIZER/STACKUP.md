# Frequency Synthesizer (Clocks_Freq_Synth_board) — Layer stack-up

Project AERIS-10 · PCB-STK-FREQUENCY_SYNTHESIZER · Rev A · 2026-10-09 · Status: **PARTIAL** (layer order SOURCE-DERIVED; thicknesses/materials UNVERIFIED)

Source: EAGLE DRU `PCBWay_6L_100um-Track *` in `4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd` (layerSetup `(1+2*3+14*15+16)`).

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 0.11mm |
| 2 | 2 | In1.Cu | 0.035mm | 0.6mm |
| 3 | 3 | In2.Cu | 0.035mm | 0.11mm |
| 4 | 14 | In3.Cu | 0.035mm | 0.6mm |
| 5 | 15 | In4.Cu | 0.035mm | 0.11mm |
| 6 | 16 | B.Cu | 0.035mm | — |

**Caveats**: `mtCopper` 0.035 mm = 1 oz copper; `mtIsolate` values are the EAGLE DRU table (the DRU names a PCBWay template, but the values were not confirmed by a vendor stack-up document). Total thickness is not defined in the source; KiCad assumed 1.6 mm. Material (FR-4 / RO4350B hybrid per `Stack_Hybrid.png`), prepreg/core assignment, finish and impedance targets must be supplied by the designer/fabricator → `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`.
