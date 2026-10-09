# AERIS-10 — BETA PCB packages

**Status of everything in this directory: BETA.** KiCad 10.0.6 copies of the EAGLE → KiCad conversion in `engineering/PCB/`, brought to a routed / DRC-checked state by scripts and Freerouting 2.5.0, with proposed BOM part numbers and fabrication notes. **Not reviewed by the original designer. Not fabricated. Not a release.** The EAGLE originals in `4_Schematics and Boards Layout/` and the reference conversion in `engineering/PCB/` are untouched; no circuit connectivity (netlist) was changed on any board.

| Board | Dir | Unconnected before → after | DRC before → after | Outside outline before → after | Routing work | Remaining blockers |
|---|---|---|---|---|---|---|
| Main Board (10 L, 260×300) | `MAIN_BOARD/` | 15 → **0** | 912 → 1049 (0 real new; +polygon/thermal-pad items now visible, see README) | 11 → 6 (6 net-less 0201 resistors left, DNP) | 7 arc tails, 5-part filter cluster placed + hand-routed, 14 copper polygons given their net | no-net thermal-via pads of U69/U7 and 4 ambiguous BPF2 polygons (schematic/footprint level); FT601 unwired in the schematic |
| Power Supply (2 L, 280×300) | `POWER_SUPPLY/` | 308 → **89** | 163 → 328 | 132 → **0** | 132 parts placed by script, Freerouting ×2 (+1372 tracks, +171 vias), 29 bridges, 22 stitching items, B.Cu GND plane | 89 open connections (`UNROUTED.md`: pour-to-pour VIN/GND distribution, fragmented bottom plane); placement needs designer review |
| RF PA (4 L, 35×60) | `RF_PA/` | 1 → **0** | 67 → 18 | 0 → 0 | 1 GND strap, paddle polygon → GND, zone priorities; RF tracks untouched | 1 clearance 0.123 mm in the source (VIN_M stub) |
| Frequency Synthesizer (6 L, 100×100) | `FREQUENCY_SYNTHESIZER/` | 0 → **0** | 639 → 639 (capped; silk conflicts 147 → 103 measured) | 0 → 0 | copper untouched; 43 silk texts nudged; `DRC_DISPOSITION.md` | 7 courtyard overlaps to review; 0201 silk density |

"DRC before" = `engineering/PCB/<BOARD>/reports/DRC_report.json`; "after" = `<BOARD>/exports/reports/DRC_report.json` (KiCad caps each violation type at 199 entries). Counts went *up* on the Main Board and Power Supply because the net-less copper polygons that previously hid behind one `shorting_items` entry each are now checked as real copper, and because newly placed/routed parts expose their footprint-level silk/pad issues — the per-board READMEs classify every type.

## Per-board contents

```
beta/pcb/<BOARD>/
├── <BOARD>.kicad_pcb, <BOARD>.kicad_pro   BETA board (open in KiCad 10)
├── README.md                              before/after table, change list, what remains, BETA statement
├── FAB_NOTES.md                           PCBWay stack-up / material / finish / impedance proposal (PROPOSED)
├── BOM_<BOARD>_beta.csv                   BOM with manufacturer, mpn, mpn_confidence, dnp, note
├── UNROUTED.md | DRC_DISPOSITION.md | POLYGON_NET_DISPOSITION.md   where applicable
├── *.json                                 logs of every scripted change (placement, routing merge, bridges, nudges)
├── *.dsn / *.ses / freerouting*.log       Freerouting input/output (Power Supply)
├── reports/                               working DRC reports
└── exports/                               Gerber, drill, PDF drawings, SVG, DXF, STEP, pick-and-place, IPC-2581,
                                           IPC-D-356, DRC, statistics, 3-D renders (tools/beta_export_package.sh)
```

## BOM confidence (lines / quantity)

| Board | HIGH (deviceset = MPN) | MEDIUM (standard passive from value+package) | LOW (guess / non-standard value / conflict) | EMPTY (no value in the source) |
|---|---|---|---|---|
| Main Board | 23 / 204 | 41 / 461 | 30 / 93 | 4 / 18 |
| Power Supply | 7 / 79 | 18 / 225 | 3 / 8 | 0 / 0 |
| RF PA | 5 / 6 | 6 / 19 | 0 / 0 | 0 / 0 |
| Frequency Synthesizer | 10 / 37 | 22 / 110 | 6 / 29 | 2 / 8 |

MPNs are proposals (`tools/beta_bom_mpn.py`): Murata GRM / Yageo RC / Murata LQP03 / TDK VLP families for passives, orderable IC codes for the device sets; voltage ratings, non-E-series values (e.g. 2.443 kΩ, 103 pF, 107.3 nH) and package/value conflicts (47 µF in 0201, NX3225 footprint with a 32.768 kHz value, 5 mΩ shunt with a 0.1 Ω part number) are flagged in the `note` column and must be resolved by the designer.

## Tooling and provenance

`tools/` — pcbnew/kicad-cli scripts (see `tools/README.md`), Freerouting 2.5.0 jar (OpenJDK 27). `CHANGELOG.md` — every change per board in order. All scripts are re-runnable; the sequence per board is documented in `tools/README.md`.
