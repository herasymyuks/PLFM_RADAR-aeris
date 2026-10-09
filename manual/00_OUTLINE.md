# AERIS-10 manual — chapter outline and sources (binding)

| # | Chapter file | Title | Primary sources | Figures (from FIGURE_PLAN) |
|---|---|---|---|---|
| 0 | `chapters/00_front_matter.md` | Title, status statement, how to read, revision table | `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` header, `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §1–2 | — |
| 1 | `chapters/01_system_overview.md` | What AERIS-10 is: pulsed-LFM X-band phased array, variants Nexus/Extended, performance targets vs calculated | `README.md`, `00_notation/parameter_table.md`, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, `docs/SYSTEM/BLOCK_DIAGRAM.md` | F1.1 system block diagram (SYS-01), F1.2 original drawio diagram, F1.3 photos |
| 2 | `chapters/02_theory_of_operation.md` | Waveform/timing, beamforming, signal processing chain, data path | `01_physics/*`, `02_hardware/04_antenna_beamforming.md`, `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.*`, `DATA_FLOW/end_to_end_data_flow.*`, `engineering/SYSTEM/data_flow/*` | F2.1 signal/data flow (SYS-03), F2.2 FPGA pipeline (SD-02), F2.3 end-to-end flow (SD-07) |
| 3 | `chapters/03_architecture_and_interfaces.md` | Boards, modules, connectors, cables, power rails | `engineering/SYSTEM/interfaces/*`, `engineering/ELECTRICAL/power_distribution/*`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` | F3.1 interconnection diagram (SYS-02), F3.2 power distribution (ELEC-PWR-01), tables: interconnection, rails, harness |
| 4 | `chapters/04_main_board.md` | Main Board: schematic set, layout, BOM, DRC state, rev. B host interface | `engineering/ELECTRICAL/schematics/MAIN_BOARD/`, `engineering/PCB/MAIN_BOARD/README.md`, `beta/pcb/MAIN_BOARD*/README.md`, `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` | F4.1–4.4 schematic sheets, F4.5 top/bottom layer plots, F4.6 3-D render, F4.7 assembly drawing |
| 5 | `chapters/05_power_supply_board.md` | Power Board | same pattern, POWER_SUPPLY | F5.x |
| 6 | `chapters/06_frequency_synthesizer.md` | Synth board | same pattern, FREQUENCY_SYNTHESIZER | F6.x |
| 7 | `chapters/07_rf_pa_board.md` | RF PA board (×16) | same pattern, RF_PA; `engineering/DESIGN/THERMAL/*` | F7.x |
| 8 | `chapters/08_antenna.md` | Proposed 16×8 patch panel: design, simulation, fabrication data | `engineering/DESIGN/ANTENNA/*` | F8.1 layout drawing, F8.2 3-D render, F8.3 S11 plot, F8.4 coupling |
| 9 | `chapters/09_host_link_and_supply.md` | FPGA→host path (options A/B), 22 V PA supply module | `engineering/DESIGN/HOST_LINK/*`, `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/*` | F9.1 PSU block schematic, tables: FT601 pin plan, bridge frame |
| 10 | `chapters/10_mechanical_design.md` | Head and pedestal: layout, drawings, parts, flat patterns, thermal map, torque | `engineering/DESIGN/MECHANICAL/*`, `engineering/DESIGN/CALCS/*`, `engineering/MECHANICAL/*` | F10.1–10.5 DSN-MECH-01…05, F10.6 flat patterns, F10.7 section with fasteners, F10.8 isometrics, F10.9 thermal map, F10.10 PCB plan view |
| 11 | `chapters/11_fpga_firmware.md` | FPGA design: module hierarchy, build, constraints, tests, synthesis status | `beta/fpga/README.md`, `engineering/SOFTWARE_DIAGRAMS/FPGA/*`, `beta/fpga_synth/README.md` | F11.1 hierarchy (SD-01), F11.2 pipeline |
| 12 | `chapters/12_stm32_firmware.md` | Firmware: architecture, build, defects fixed, sequencing, USB protocol | `beta/stm32/README.md`, `DECISIONS.md`, `engineering/SOFTWARE_DIAGRAMS/STM32/*` | F12.1 architecture (SD-03), F12.2 USB CDC flow (SD-04) |
| 13 | `chapters/13_gui_software.md` | GUI: install, run, protocol, register panel, packaging | `beta/gui/README.md`, `engineering/SOFTWARE_DIAGRAMS/PYTHON/*` | F13.1 modules (SD-05), F13.2 runtime (SD-06), screenshots to render (`--demo`, headless Tk) |
| 14 | `chapters/14_manufacturing.md` | Manufacturing packages per board, stack-ups, BOMs with MPN confidence, fab checklist | `engineering/PCB/*/README.md`, `beta/pcb/*/FAB_NOTES.md`, `BOM_*_beta.csv` | tables |
| 15 | `chapters/15_assembly_procedure.md` | Step-by-step mechanical assembly, board installation, harness, integration order, inspection checkpoints | `manual/ASSEMBLY_STEPS_SOURCE.md` (+ its sources) | F15.x exploded view, DSN-MECH-04/06/07, harness, connector positions |
| 16 | `chapters/16_bring_up_and_test.md` | Power-up, firmware flashing, FPGA programming, calibration (ADC taps, beam), bench tests, acceptance criteria | `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §B/D, `docs/TESTING/*`, beta READMEs | tables |
| 17 | `chapters/17_open_issues_and_decisions.md` | K1–K8, D-01…D-19, G-01…G-12, MDR-*, register of unresolved items | `docs/03_MISSING_COMPONENTS.md`, `docs/04_RECOVERY_TASKS.md`, `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`, `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` | — |
| A | `chapters/A_drawing_register.md` | Drawing register (copy) | `engineering/DRAWING_REGISTER.md` | — |
| B | `chapters/B_parts_and_cables.md` | Parts lists (PCB BOM summaries, mechanical parts, fasteners), cable schedule | `docs/BOM/*.md`, `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` | — |
| C | `chapters/C_tooling.md` | Tools and scripts (what each generator does, how to regenerate) | `tools/*.py` docstrings, `engineering/README.md`, `beta/README.md` | — |
| D | `chapters/D_glossary.md` | Glossary, acronyms, status vocabulary | `00_notation/*` | — |

Order of concatenation = this table. Chapter files that do not exist yet are stubs (`manual/chapters/*.md` created with the source list only) — Claude Design writes them.
