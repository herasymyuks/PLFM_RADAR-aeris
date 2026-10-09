# beta/pcb/tools — BETA PCB tooling

All scripts are non-destructive unless an output path is given (most take `IN.kicad_pcb OUT.kicad_pcb`; pass the same
path to work in place). They never touch `4_Schematics and Boards Layout/` or `engineering/PCB/`.

| Script | Runtime | Purpose |
|---|---|---|
| `beta_pcb_analyze.py` | KiCad Python | read-only board census: outline, footprints outside the outline, unconnected count, net-less zones, track widths on RF/LVDS/CLK nets (`--json`) |
| `beta_place_outside.py` | KiCad Python | move footprints that lie outside the outline inside (net clusters, anchors, 1 mm grid, free-space search, connectors on edges); `--skip-nonet`, `--log` |
| `beta_fix_stubs.py` | KiCad Python | close arc/track ↔ pad gaps left by the EAGLE import (`--radius`, `--arc-tail`, explicit `--extra NET,LAYER,W,x1,y1,x2,y2`) |
| `beta_polygon_nets.py` | KiCad Python | disposition of net-less footprint copper polygons; unambiguous ones get their net (`--to-board` re-creates them as board-level copper so KiCad DRC honours the net); Markdown table |
| `beta_zone_priorities.py` | KiCad Python | distinct priorities for overlapping same-net zones (removes `zones_intersect` ambiguity) |
| `beta_add_plane.py` | KiCad Python | add a board-wide pour of one net on one layer (lowest priority) |
| `beta_specctra.py` | KiCad Python | `export`: lock all existing tracks in memory and write a Specctra DSN (`(type fix)` wires); `merge`: add only the new wires/vias of a Freerouting SES for selected nets (existing tracks never rebuilt, arcs preserved) |
| `beta_bridge_unconnected.py` | KiCad Python | straight same-net bridges / vias for gaps listed in a DRC JSON (zone↔zone, pad↔zone…); `--revert LOG --drc JSON` removes the ones that caused clearance/crossing violations |
| `beta_gnd_stitch.py` | KiCad Python | 2-layer GND stitching: vias where bottom-fill islands overlap top fills, via + stub for unconnected SMD pads of the net (hole-aware), revertable log |
| `beta_silk_nudge.py` | KiCad Python | move silkscreen reference/value texts off pads and other silk (spiral search); `--dry-run` counts conflicts (uncapped, unlike the KiCad report) |
| `beta_revb_ft601.py` | KiCad Python | Main Board rev. B: create nets, assign U6/U42 pads, add the FT601 support parts from the KiCad library, write netclasses, `NETLIST_DELTA.csv` (explicit netlist change) |
| `beta_dsn_restrict.py` | CPython 3 | restrict a DSN to selected nets (other nets keep their wires as obstacles but lose their pins) |
| `beta_net_lengths.py` | KiCad Python | routed length / vias / layers per net and group skew vs a ±tolerance |
| `beta_bom_mpn.py` | CPython 3 | BETA BOM with proposed MPNs and confidence levels from `docs/BOM/BOM_<BOARD>.csv` |
| `beta_drc.sh` | bash + kicad-cli | refill zones, save board, DRC text + JSON, one-line summary |
| `beta_export_package.sh` | bash + kicad-cli | full manufacturing/drawing package (same export set as `tools/kicad_pcb_pipeline.sh`) into `exports/` |
| `freerouting-2.5.0.jar` | OpenJDK 27 | autorouter (`java -jar freerouting-2.5.0.jar -de X.dsn -do X.ses -mp 20 -mt 8 -l en`); checksum file alongside (the jar itself is not listed in the upstream CLI checksum file; SHA-256 recorded in `../CHANGELOG.md`) |

KiCad Python: `~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`; kicad-cli: `~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (override with `KICAD_CLI`).

Typical BETA sequence for a board: analyze → place outside parts → fix stubs / polygon nets → `beta_specctra.py export` → Freerouting → `beta_specctra.py merge` → zone priorities → `beta_drc.sh` → `beta_bridge_unconnected.py` (+ DRC + `--revert`) → `beta_export_package.sh`.
