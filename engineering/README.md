# engineering/ — AERIS-10 engineering drawings and CAD package

Generated 2026-10-09 (claude.md addendum §16–26). Everything here is derived from the repository's native design files; the EAGLE `.sch/.brd` files remain the design masters and were not modified. Start with:

- `DRAWING_REGISTER.md` — all 73 registered drawings with status (39 SOURCE-DERIVED, 28 PARTIAL, 1 CONCEPTUAL, 5 BLOCKED — MISSING DATA; 0 VERIFIED).
- `MISSING_DRAWINGS_RECOVERY_PLAN.md` — step-by-step guides MDR-01…MDR-11 for what could not be generated.
- `VALIDATION/` — `DRAWING_CHECKS.md` (what was checked and how), `CAD_EXPORT_LOG.md` (every kicad-cli command + exit code), `PCB_CROSS_CHECK.md` (EAGLE XML ↔ KiCad counts), `UNRESOLVED_GEOMETRY.md` (G-01…G-12).

| Directory | Content | Generator |
|---|---|---|
| `SYSTEM/block_diagrams`, `interfaces`, `data_flow`, `architecture/README.md` | SYS-01…SYS-03 DOT + SVG/PDF/PNG, Mermaid twin, interconnection table | hand-authored DOT from schematic nets (Graphviz) |
| `ELECTRICAL/schematics/<BOARD>/` | SVG per sheet, multi-page PDF, PNG, `sheets.json` | `tools/render_eagle_schematic.py`, `tools/svg_sheets_to_pdf.py` |
| `ELECTRICAL/netlists`, `connection_diagrams` | netlist CSV (by net, by part), connection reports, unresolved-connection and missing-symbol/footprint reports | `tools/gen_schematic_reports.py` |
| `ELECTRICAL/power_distribution` | ELEC-PWR-01 diagram + 36-row rail register | hand-authored DOT |
| `PCB/<BOARD>/` | KiCad conversion (`kicad/`), Gerber, drill, PDF drawings, SVG layers, DXF/STEP, P&P, BOM, IPC-2581, IPC-D-356, DRC, 3-D renders, `README.md`, `STACKUP.md` | `tools/kicad_pcb_pipeline.sh`, `tools/kicad_project_from_dru.py`, `tools/gen_engineering_pcb_docs.py` |
| `MECHANICAL/CAD`, `STEP`, `DXF`, `PDF`, `dimensions` | board bodies, outlines + holes (two independent DXF sources), 1:1 plan view, dimension sheets with hole tables | `tools/gen_mechanical_package.py` |
| `ASSEMBLY/` | parts list, assembly sequence, CONCEPTUAL exploded view, per-board assembly drawing index | `tools/gen_assembly_exploded_view.py` + hand-written MD |
| `SOFTWARE_DIAGRAMS/FPGA`, `STM32`, `PYTHON`, `DATA_FLOW` | SD-01…SD-07 DOT + renders, hierarchy/module tables | `tools/gen_verilog_hierarchy.py`, `tools/gen_python_module_graph.py`, hand-authored DOT |

Regenerate everything (≈ 10 min, needs KiCad 10 and Google Chrome on the machine; Graphviz for the DOT renders):

```bash
bash tools/kicad_pcb_pipeline.sh                      # 4 boards → engineering/PCB/*
python3 tools/gen_engineering_pcb_docs.py             # README/STACKUP per board + PCB_CROSS_CHECK.md
python3 tools/gen_schematic_reports.py                # netlists + connection reports
for b in RF_PA FREQUENCY_SYNTHESIZER MAIN_BOARD POWER_SUPPLY; do
  python3 tools/render_eagle_schematic.py "<path to .sch>" --out engineering/ELECTRICAL/schematics/$b/svg --board $b --root .
  python3 tools/svg_sheets_to_pdf.py -o engineering/ELECTRICAL/schematics/$b/${b}_schematic.pdf --png-dir engineering/ELECTRICAL/schematics/$b/png engineering/ELECTRICAL/schematics/$b/svg/*.svg
done
python3 tools/gen_mechanical_package.py && python3 tools/gen_assembly_exploded_view.py
python3 tools/gen_verilog_hierarchy.py --rtl 9_Firmware/9_2_FPGA --out engineering/SOFTWARE_DIAGRAMS/FPGA
python3 tools/gen_python_module_graph.py
for d in $(find engineering -name "*.dot"); do dot -Tsvg -o ${d%.dot}.svg $d; dot -Tpdf -o ${d%.dot}.pdf $d; dot -Tpng -Gdpi=150 -o ${d%.dot}.png $d; done
python3 tools/gen_drawing_register.py --check
```

Size note: `PCB/MAIN_BOARD/ipc/MAIN_BOARD.xml.gz` and the other large IPC-2581 files are gzip-compressed; `gunzip -k` before use.
