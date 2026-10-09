# Drawing validation record

Project AERIS-10 · VAL-DRW-01 · Rev A · 2026-10-09. What was actually checked, with the command and the result. "PASS" is used only for checks that were executed; a drawing that only exists is "GENERATED", not verified.

## 1. Automatic checks executed

| Check | Command | Result |
|---|---|---|
| EAGLE XML ↔ KiCad conversion counts (outline W×H, footprints, vias, tracks, copper layers, PTH/NPTH totals) for 4 boards | `python3 tools/gen_engineering_pcb_docs.py` → `PCB_CROSS_CHECK.md` | **PASS — 32/32 rows OK** (exit 0) |
| KiCad DRC with EAGLE-DRU-derived rules, zones refilled | `tools/kicad_pcb_pipeline.sh` step `drc` (log in `CAD_EXPORT_LOG.md`) | executed; violations RF PA 48, Synth 639, Main 912 (+15 unconnected), Power 160 (+308 unconnected) — see each `engineering/PCB/<BOARD>/README.md` §6. **Not a pass**: designer disposition required |
| Every kicad-cli export step exit code | `CAD_EXPORT_LOG.md` | 0 failed steps in the final run of all four boards (first run of 3 boards failed on EAGLE layer 47 → fixed by remap, logged) |
| Schematic connectivity: netlist, single-pin nets, unconnected pins, sch↔brd parity, missing symbols/footprints | `python3 tools/gen_schematic_reports.py` | exit 0: 0 missing symbols/footprints; sch↔brd part lists identical for all 4 boards; findings listed in `ELECTRICAL/netlists/<BOARD>_unresolved_connections.md` |
| Verilog hierarchy vs RTL | `python3 tools/gen_verilog_hierarchy.py` | exit 1 (expected): 5 instantiated modules have no definition; matches `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §2.2 |
| Python module graph | `python3 tools/gen_python_module_graph.py` | exit 1 (expected): `GUI_V1.py` syntax error shown as red node |
| Schematic SVG → PDF/PNG conversion | `python3 tools/svg_sheets_to_pdf.py` | 7 sheets, 4 PDFs with `%%EOF`, 7 PNGs — all written |
| SVG well-formedness of generated drawings | `python3 -c "import xml.etree.ElementTree as ET; ET.parse(f)"` over `engineering/**/*.svg` | see §3 |
| Registered files exist | `python3 tools/gen_drawing_register.py --check` | see §3 |

## 2. Visual checks performed by the author (rendered PNGs inspected)

| Drawing | What was looked at | Result |
|---|---|---|
| `ELECTRICAL/schematics/RF_PA/png/RF_PA_schematic_sheet1.png` | frame, symbols, pins + pad numbers, nets, junctions, labels, title block substitution | readable; literal text `>QPA2962` is in the source (not a renderer defect) |
| `ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet1.png` | 4-sheet file: frame title block (TITLE/Date/Sheet 1/4 substituted), decoupling networks | readable |
| `PCB/FREQUENCY_SYNTHESIZER/3d/FREQUENCY_SYNTHESIZER_render_top.png` | pours, SMA/header footprints, silkscreen refs | consistent with `.brd`; no component bodies (no 3-D models) |
| `MECHANICAL/CAD/pcb_set_plan_view.png` | 4 outlines at 1:1 with dimensions and holes | matches `dimensions/*.md` |
| `ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png` | balloons 1–6, labels, CONCEPTUAL marking | legible; marked CONCEPTUAL |

| `DESIGN/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png` | 16 rows × 8 patches, feeds, 16 connector footprints, 6 holes; KiCad loads the generated board (DRC ran: 49 violations, 0 unconnected) | consistent with the calc sheet |
| `DESIGN/MECHANICAL/drawings/png/DSN-MECH-01_head_plan_section.png` | tier order, fins, radome window, dimensions | consistent with `design_layout.py` |
| `DESIGN/MECHANICAL/CAD/aeris10_head_pedestal_iso.png`, `aeris10_head_xray_iso.png` | FreeCAD STL rendered: head on turntable/pedestal, internals visible in x-ray | model builds; painter-algorithm artefacts only |

Not visually checked: the remaining schematic sheets (Synth, Main 2–4, Power), the per-layer PDFs/SVGs, the DOT renders beyond existence/size — listed as GENERATED in the register, pending review.

## 3. Results of the file-level checks

`python3 tools/gen_drawing_register.py --check` (2026-10-09): 73 registered drawings, every registered native file and export present, non-empty and well-formed (SVG parsed, PDF has header and `%%EOF`, DOT has a graph) — **0 problems, exit 0**. Full list in `../DRAWING_REGISTER.md` footer.
