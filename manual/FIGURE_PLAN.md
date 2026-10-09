# Figure plan per chapter

Existing assets are referenced by path (see `ASSET_INDEX.md` for status). "To render" figures must be produced with the stated command into `manual/figures/` before the build. PNG at ≤ 2400 px for the PDF; keep SVG next to it.

| Fig | Chapter | Asset / command | Status label |
|---|---|---|---|
| F1.1 | 1 | `engineering/SYSTEM/block_diagrams/system_block_diagram.png` | SOURCE-DERIVED |
| F1.2 | 1 | `2_Functional Diagram, Block Diagram & Schematic/*.jpg` (original block diagram) | ORIGINAL PROJECT FILE |
| F1.3 | 1 | `8_Utils/Antenna_Array.jpg`, `8_Utils/0044.jpg` (prototype photos, undimensioned) | ORIGINAL PROJECT FILE |
| F2.1 | 2 | `engineering/SYSTEM/data_flow/signal_and_data_flow.png` | SOURCE-DERIVED |
| F2.2 | 2 | `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.png` | PARTIAL |
| F2.3 | 2 | `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.png` | PARTIAL |
| F3.1 | 3 | `engineering/SYSTEM/interfaces/hardware_interconnection.png` | SOURCE-DERIVED |
| F3.2 | 3 | `engineering/ELECTRICAL/power_distribution/power_distribution.png` | SOURCE-DERIVED |
| F4.1–4.4 | 4 | `engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet{1..4}.png` | SOURCE-DERIVED |
| F4.5 | 4 | `engineering/PCB/MAIN_BOARD/svg/MAIN_BOARD_top_composite.svg` + bottom (to render PNG: `python3 tools/svg_sheets_to_pdf.py -o manual/figures/tmp.pdf --png-dir manual/figures <svg>`) | SOURCE-DERIVED |
| F4.6 | 4 | `engineering/PCB/MAIN_BOARD/3d/MAIN_BOARD_render_top.png`, `beta/pcb/MAIN_BOARD/exports/3d/*` | SOURCE-DERIVED / BETA |
| F4.7 | 4 | `engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf` (to render PNG: `pdftoppm -png -r 110 -f 1 -l 1`) | SOURCE-DERIVED |
| F5.x, F6.x, F7.x | 5–7 | same pattern for POWER_SUPPLY, FREQUENCY_SYNTHESIZER, RF_PA | |
| F8.1 | 8 | `engineering/DESIGN/ANTENNA/aeris10_patch_array_layout.png` | PROPOSED DESIGN |
| F8.2 | 8 | `engineering/DESIGN/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png` | PROPOSED DESIGN |
| F8.3 | 8 | `engineering/DESIGN/ANTENNA/simulation/s11_row.png` | PROPOSED DESIGN (simulated) |
| F8.4 | 8 | to render from `simulation/coupling_3rows.csv` (matplotlib in `beta/gui/.venv`; script `manual/figures/plot_coupling.py` to write) | PROPOSED DESIGN (simulated) |
| F9.1 | 9 | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.png` | PROPOSED DESIGN |
| F10.1–10.5 | 10 | `engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-0{1..5}_*.png` | PROPOSED DESIGN |
| F10.6 | 10 | `engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png` | PROPOSED DESIGN |
| F10.7 | 10 | `engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png` | PROPOSED DESIGN |
| F10.8 | 10 | `engineering/DESIGN/MECHANICAL/CAD/detail/aeris10_detail_xray_front_iso.png`, `aeris10_detail_iso_rear.png`, `engineering/DESIGN/MECHANICAL/CAD/aeris10_head_xray_iso.png` | PROPOSED DESIGN |
| F10.9 | 10 | to render: `engineering/DESIGN/CALCS/thermal_map_B-gated-drain.svg` → PNG (svg_sheets_to_pdf.py) | PROPOSED DESIGN (calculated) |
| F10.10 | 10 | `engineering/MECHANICAL/CAD/pcb_set_plan_view.png`, `engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png` | SOURCE-DERIVED / CONCEPTUAL |
| F11.1 | 11 | `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.png` (regenerate from `beta/fpga/rtl` with `tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl --out manual/figures/fpga_beta` + `dot -Tpng`) | SOURCE-DERIVED / BETA |
| F12.1–12.2 | 12 | `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_firmware_architecture.png`, `stm32_usb_cdc_flow.png` | PARTIAL |
| F13.1–13.2 | 13 | `engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.png`, `python_gui_architecture.png` | SOURCE-DERIVED |
| F13.3 | 13 | to render: GUI screenshot in demo mode — `cd beta/gui && .venv/bin/python -m aeris10_gui --demo --screenshot manual/figures/gui_demo.png` (add a `--screenshot` option if absent: run 3 frames, `root.update()`, `canvas.postscript` or `ImageGrab` via Pillow; document) | BETA |
| F15.x | 15 | exploded view, DSN-MECH-04 (connector positions), DSN-MECH-06/07, harness table excerpt, `engineering/PCB/<BOARD>/drawings/<BOARD>_assembly_top.pdf` pages | mixed, label each |
| F16.x | 16 | none mandatory; tables | — |

Rules: no figure without a caption with status; drawings keep their title block; per-layer PCB plots go only into chapter 14 as a table of file links, not as figures.
