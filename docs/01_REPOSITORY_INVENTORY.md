# 01 — Repository Inventory (AERIS-10)

Generated 2026-10-08 by `tools/gen_inventory_doc.py` from the live file tree (524 files, `.git` excluded). Regenerate after any change: `python3 tools/gen_inventory_doc.py`.

Status legend: COMPLETE — usable as-is for its purpose; INCOMPLETE — exists but cannot fulfil its purpose (syntax error, fragment, contradictory); MISSING DEPENDENCY — needs files absent from the repository; PLACEHOLDER — template/stub content; REQUIRES VALIDATION — plausible but not verified by an executed check; UNKNOWN — no check applied.

## Status summary

| Status | Files |
|---|---:|
| COMPLETE | 220 |
| INCOMPLETE | 7 |
| MISSING DEPENDENCY | 37 |
| PLACEHOLDER | 3 |
| REQUIRES VALIDATION | 256 |
| UNKNOWN | 1 |

## Subsystem summary

| Subsystem | Files |
|---|---:|
| Automation | 16 |
| Datasheets | 48 |
| Docs: hardware | 9 |
| Docs: notation | 3 |
| Docs: physics | 12 |
| Docs: research | 9 |
| Docs: software | 4 |
| Engineering manual (generated) | 37 |
| FPGA | 37 |
| Media / utilities | 7 |
| PCB | 2 |
| PCB: Frequency Synthesizer | 2 |
| PCB: Main Board | 2 |
| PCB: Power Supply | 2 |
| PCB: Production files | 8 |
| PCB: RF PA | 2 |
| Planning (GSD) | 71 |
| Power management | 1 |
| Project description | 1 |
| Python GUI | 14 |
| Root | 2 |
| STM32 firmware | 138 |
| Simulation | 82 |
| System diagrams | 3 |
| Utility scripts | 12 |

## File table

| Path | File type | Subsystem | Purpose | Dependencies | Status |
|---|---|---|---|---|---|
| `README.md` | Markdown | Root | Project overview; claims Gerbers, assembly guide (10_docs/) and enclosure files that do not exist | — | INCOMPLETE |
| `claude.md` | Markdown | Root | Task specification for this engineering reconstruction | — | COMPLETE |
| `.planning/PROJECT.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/REQUIREMENTS.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/ROADMAP.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/STATE.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/config.json` | JSON | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/ARCHITECTURE.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/CONCERNS.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/CONVENTIONS.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/INTEGRATIONS.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/STACK.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/STRUCTURE.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/codebase/TESTING.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/01-notation-parameter-standardization/01-01-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/01-notation-parameter-standardization/01-01-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/01-notation-parameter-standardization/01-02-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/01-notation-parameter-standardization/01-02-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/01-notation-parameter-standardization/01-RESEARCH.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/01-notation-parameter-standardization/01-VERIFICATION.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-01-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-01-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-02-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-02-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-03-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-03-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-04-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-04-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-RESEARCH.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/02-physics-foundation/02-VERIFICATION.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-01-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-01-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-02-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-02-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-03-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-03-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-04-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-04-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-05-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-05-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-RESEARCH.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/03-hardware-documentation/03-VERIFICATION.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-01-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-01-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-02-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-02-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-03-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-03-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-RESEARCH.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/04-software-documentation/04-VERIFICATION.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-01-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-01-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-02-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-02-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-03-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-03-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-04-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-04-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-RESEARCH.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/05-software-improvement-research/05-VERIFICATION.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-01-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-01-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-02-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-02-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-03-PLAN.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-03-SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-RESEARCH.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/phases/06-hardware-improvement-research/06-VERIFICATION.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/research/ARCHITECTURE.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/research/FEATURES.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/research/PITFALLS.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/research/STACK.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `.planning/research/SUMMARY.md` | Markdown | Planning (GSD) | GSD planning / phase records (process artefacts) | — | COMPLETE |
| `00_notation/conventions.md` | Markdown | Docs: notation | Notation / parameter documentation | — | COMPLETE |
| `00_notation/parameter_table.md` | Markdown | Docs: notation | Notation / parameter documentation | — | COMPLETE |
| `00_notation/symbol_table.md` | Markdown | Docs: notation | Notation / parameter documentation | — | COMPLETE |
| `01_physics/01_fmcw_theory.md` | Markdown | Docs: physics | Physics derivation documentation | — | COMPLETE |
| `01_physics/02_lfm_waveform_model.md` | Markdown | Docs: physics | Physics derivation documentation | — | COMPLETE |
| `01_physics/03_beamforming_theory.md` | Markdown | Docs: physics | Physics derivation documentation | — | COMPLETE |
| `01_physics/04_detection_theory.md` | Markdown | Docs: physics | Physics derivation documentation | — | COMPLETE |
| `01_physics/05_noise_analysis.md` | Markdown | Docs: physics | Physics derivation documentation | — | COMPLETE |
| `01_physics/06_calibration_theory.md` | Markdown | Docs: physics | Physics derivation documentation | — | COMPLETE |
| `01_physics/figures/beam_pattern_N16_taylor.svg` | SVG figure | Docs: physics | Generated physics figure or generator script | numpy, matplotlib | COMPLETE |
| `01_physics/figures/beam_pattern_N16_uniform.svg` | SVG figure | Docs: physics | Generated physics figure or generator script | numpy, matplotlib | COMPLETE |
| `01_physics/figures/detection_curves_swerling0.svg` | SVG figure | Docs: physics | Generated physics figure or generator script | numpy, matplotlib | COMPLETE |
| `01_physics/figures/detection_curves_swerling1.svg` | SVG figure | Docs: physics | Generated physics figure or generator script | numpy, matplotlib | COMPLETE |
| `01_physics/figures/gen_detection_curves.py` | Python | Docs: physics | Generated physics figure or generator script | numpy, matplotlib | COMPLETE |
| `01_physics/figures/generate_beam_patterns.py` | Python | Docs: physics | Generated physics figure or generator script | numpy, matplotlib | COMPLETE |
| `02_hardware/01_system_overview.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/02_rf_frontend.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/03_frequency_synthesis.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/04_antenna_beamforming.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/05_fpga_board.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/06_power_management.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/07_timing_budget.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/08_power_budget.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `02_hardware/09_gps_imu_transforms.md` | Markdown | Docs: hardware | Hardware documentation (derived from RTL/firmware; partly contradicts schematic) | — | REQUIRES VALIDATION |
| `03_software/01_fpga_pipeline.md` | Markdown | Docs: software | Software documentation | — | REQUIRES VALIDATION |
| `03_software/02_stm32_firmware.md` | Markdown | Docs: software | Software documentation | — | REQUIRES VALIDATION |
| `03_software/03_python_gui.md` | Markdown | Docs: software | Software documentation | — | REQUIRES VALIDATION |
| `03_software/04_usb_protocol.md` | Markdown | Docs: software | Software documentation | — | REQUIRES VALIDATION |
| `04_research/01_cfar_variants.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/02_clutter_rejection.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/03_range_extension.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/04_fpga_optimization.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/05_ml_detection.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/06_pulse_compression.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/07_target_tracking.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `04_research/08_adaptive_beamforming.md` | Markdown | Docs: research | Improvement research survey | — | COMPLETE |
| `1_Project_Description/Project_Description.docx` | Word document | Project description | Project description (Word) | — | COMPLETE |
| `2_Functional Diagram & Interconnection Matrices/Functional_Diagram.dwg` | AutoCAD drawing | System diagrams | AutoCAD functional diagram (binary; not a mechanical drawing) | AutoCAD | REQUIRES VALIDATION |
| `2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio` | draw.io diagram | System diagrams | System block diagram (draw.io XML) | — | COMPLETE |
| `2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg` | Image | System diagrams | Rendered block diagram | — | COMPLETE |
| `3_Power Management/Power Management V6.xlsx` | Excel workbook | Power management | Rail list and sequencing table (source for STM32 EN_* GPIO sequencing) | — | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` | Image | PCB | Hybrid stack-up image (no numeric layer table in text form) | — | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/Stack_Hybrid.png` | Image | PCB | Duplicate of 4_4_Board Stack-up/Stack_Hybrid.png | — | COMPLETE |
| `4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd` | EAGLE board | PCB: Frequency Synthesizer | EAGLE board: frequency synthesizer | .sch | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch` | Schematic (EAGLE/Qucs) | PCB: Frequency Synthesizer | EAGLE schematic: AD9523-1 clock + 2x ADF4382 synthesizers | embedded libraries | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd` | EAGLE board | PCB: Main Board | EAGLE board layout for Main Board | .sch (forward/back annotation) | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` | Schematic (EAGLE/Qucs) | PCB: Main Board | EAGLE 7.4.0 schematic: XC7A50T-2FTG256I (U42), STM32F746ZGT7 (U2), AD9484, AD9708, 4x ADAR1000, 16x ADTR1107, 2x LTC5552, FT601Q (U6, UNCONNECTED) | embedded libraries | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd` | EAGLE board | PCB: RF PA | EAGLE board: RF PA | .sch | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch` | Schematic (EAGLE/Qucs) | PCB: RF PA | EAGLE schematic: QPA2962 GaN PA board (AERIS-10X) | embedded libraries | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd` | EAGLE board | PCB: Power Supply | EAGLE board: power supply board | .sch | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch` | Schematic (EAGLE/Qucs) | PCB: Power Supply | EAGLE schematic: power supply board | embedded libraries | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board-smd.mnt` | EAGLE mount/PnP | PCB: Production files | EAGLE SMD mount (pick-and-place) file | .brd | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board-tht.csv` | CSV data | PCB: Production files | THT placement CSV | .brd | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board-tht.mnt` | EAGLE mount/PnP | PCB: Production files | EAGLE THT mount file | .brd | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board_BOM.xlsx` | Excel workbook | PCB: Production files | BOM for frequency synthesizer board (only board with a BOM) | .sch | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` | PDF | PCB: Production files | Fab impedance note (RO4350B, 0.102 mm) — only stack-up evidence in text form | — | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/mnt.csv` | CSV data | PCB: Production files | Placement CSV | .brd | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/smd_.xlsx` | Excel workbook | PCB: Production files | SMD placement workbook | .brd | REQUIRES VALIDATION |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/th_.xlsx` | Excel workbook | PCB: Production files | THT placement workbook | .brd | REQUIRES VALIDATION |
| `5_Simulations/E_plane_Kaiser25dB_like.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/E_plane_cut.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/H_plane_Kaiser25dB_like.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/H_plane_cut.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Heatmap_Kaiser25dB_like.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/QPA2962.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/QPA2962.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/QPA2962.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Slotted_DielectricFilled_Waveguide.m` | MATLAB/Octave | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Stub_BPF_V5.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Stub_BPF_V5.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Stub_BPF_V5.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/array_pattern_Kaiser25dB_like.py` | Python | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/array_pattern_heatmap.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/slot_layout_taper32.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/wg_alumina_slotted_openems.m` | MATLAB/Octave | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Antenna/Quartz_Waveguide.py` | Python | Simulation | openEMS antenna simulation script | openEMS, CSXCAD python | REQUIRES VALIDATION |
| `5_Simulations/Antenna/openems_quartz_slotted_wg_10p5GHz.py` | Python | Simulation | openEMS antenna simulation script | openEMS, CSXCAD python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/DAC_RLPF.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/DAC_RLPF.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/DAC_RLPF.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/Generate_ChirpcsvFile.py` | Python | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/dac_output.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/multi_ramp_output.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/multi_ramp_stairs.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/DAC_ReconstructionFilter/ramp_output.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Fencing/Via_fencing.py` | Python | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Fencing/Via_fencing2.py` | Python | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Fencing/via_fence_setup_pitch.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Fencing/via_fence_setup_pitch_offset.png` | Image | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF/IF_BPF.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF/IF_BPF.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF/IF_BPF.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF_Balanced/IF_BPF_Balanced.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF_Balanced/IF_BPF_Balanced.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF_Balanced/IF_BPF_Balanced.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF_Balanced/multiband_signal.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/IF_BPF_Balanced/six_tone_signal.csv` | CSV data | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Impedance.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Impedance.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Impedance.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Sparameters/M3SWA2-34DR+_3.5V_RF1 ON_100MHz_Plus25DegC_UNIT1.s3p` | Touchstone 3-port | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Sparameters/M3SWA2-34DR+_3.5V_RF1 ON_40GHz_Plus25DegC_UNIT1.s3p` | Touchstone 3-port | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Sparameters/M3SWA2-34DR+_3.5V_RF2 ON_100MHz_Plus25DegC_UNIT1.s3p` | Touchstone 3-port | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/RF switch/Sparameters/M3SWA2-34DR+_3.5V_RF2 ON_40GHz_Plus25DegC_UNIT1.s3p` | Touchstone 3-port | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Drawing1.bak` | Backup | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Drawing1.dxf` | DXF drawing | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.dpl` | Qucs display | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.gds` | GDSII layout | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.ite` | Qucs/other | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.net` | Netlist | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.pcb` | PCB (legacy) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.pdf` | PDF | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Sim_BPF_Te_100um.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/gerber_file.gbr` | Gerber | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/qucs2grb_log.txt` | Text | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Gerber/Gerber.kicad_pcb` | KiCad PCB | Simulation | KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB) | KiCad | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Gerber/Gerber.kicad_prl` | KiCad local prefs | Simulation | KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB) | KiCad | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Gerber/Gerber.kicad_pro` | KiCad project | Simulation | KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB) | KiCad | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Gerber/Gerber.kicad_sch` | KiCad schematic | Simulation | KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB) | KiCad | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Gerber/fp-info-cache` | none | Simulation | KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB) | KiCad | REQUIRES VALIDATION |
| `5_Simulations/Sim_BPF_Te_100um/Gerber/Gerber-backups/Gerber-2025-09-21_024138.zip` | Archive | Simulation | KiCad project exporting the simulated BPF layout (simulation only, NOT a product PCB) | KiCad | REQUIRES VALIDATION |
| `5_Simulations/Stub_BPF/Stub_BPF.dat` | Simulation data (Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Stub_BPF/Stub_BPF.net` | Netlist | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/Stub_BPF/Stub_BPF.sch` | Schematic (EAGLE/Qucs) | Simulation | RF/analog simulation (Qucs .sch/.dat/.dpl, Touchstone, MATLAB/Octave, Python) | Qucs / Octave / Python | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/et` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/ht` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/port_it1A` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/port_it1B` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/port_ut1A` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/port_ut1B` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/port_ut1C` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_32/wg_alumina_32.xml` | XML | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/et` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/ht` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/port_it1A` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/port_it1B` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/port_ut1A` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/port_ut1B` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/port_ut1C` | none | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `5_Simulations/sim_wg_alumina_fast/wg_alumina.xml` | XML | Simulation | openEMS waveguide simulation output / model | openEMS | REQUIRES VALIDATION |
| `6_Application Notes/UG-290.pdf` | PDF | Datasheets | Application note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/60124102122403.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AD9708.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/ADAR1000.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/ADM7151.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AT93C46A.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/DS_FT2232H.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/DS_FT232RN.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/EP4RKU_2b-1858448.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/FR2-SMA-KFD0405A_2025-08-11.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/LTC5552f.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/LTC6419fa.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/M3SWA2-34DR+.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/MAX1449-3468915.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/MMIQA-0218HPSM-Integrated Drive GaAs MMIC IQ Mixer.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/MTX2-143+.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/PMA2-123LNW+.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/PMA5_123_3W_2b-3577903.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/QPA1013D Data Sheet.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/QPM1021 Data Sheet.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/RO4000 Laminates RO4003C and RO4350B - Data Sheet (1).pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/RO4000 Laminates RO4003C and RO4350B - Data Sheet.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/SMIQ-5143H+.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/STUW81300TR.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/TGA2623_Data_Sheet-1518452.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/ads7830.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/adtr1107.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/attenuator_n_catalog_partition37_en.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/dac7578.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/hr2220p601r-10-datasheet.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/ina241a.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/lm2663.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/max20029-max20029d.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/opa703.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/tmp35_36_37.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/tps562201.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/tps7a8300.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AD9484/AD9434_AD9484_Schematic.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AD9484/AD9484.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AD9484/RX_Chain_Gain_Noise_Summary_ABAC_Radar.docx` | Word document | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AD9484/UG-290.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/AD9484/ad8352.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/ADF4382A/ADF4382A.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/ADF4382A/eval_adf4382a_ug_2185-3392420.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/QPA2962/QPA2962 Data Sheet.pdf` | PDF | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/QPA2962/QPA2962_22V1680mA_s2p/QPA2962_SN63_22v1680ma_25C.s2p` | Touchstone 2-port | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/QPA2962/QPA2962_22V1680mA_s2p/QPA2962_SN63_22v1680ma_85C.s2p` | Touchstone 2-port | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `7_Components Datasheets and Application notes/QPA2962/QPA2962_22V1680mA_s2p/QPA2962_SN63_22v1680ma_n40C.s2p` | Touchstone 2-port | Datasheets | Component datasheet / app note (reference) | — | COMPLETE |
| `8_Utils/0044.jpg` | Image | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/3fb1dabf-2c6d-4b5d-b471-48bc461ce914.jpg` | Image | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/Antenna_Array.jpg` | Image | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/GUI.jpg` | Image | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/RADAR_V6.jpg` | Image | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/SplitRing_test.mp4` | Video | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/b79a6fe3-5abf-473d-b3e2-178e6a9cf4da - Copie.jpg` | Image | Media / utilities | Photo / media asset | — | COMPLETE |
| `8_Utils/Python/CSV_radar.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/CSV_radar_2.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/FFT_Ramp_Frequency.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/Gen_Triangular.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/Generic_Ramp_Frequency.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/Generic_Triangular_Frequency.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/LUT.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/RADAR_eq.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/Ramp_Frequency.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/patch_antenna.py` | Python | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/small_test_radar_data.csv` | CSV data | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `8_Utils/Python/test_radar_data.csv` | CSV data | Utility scripts | Utility / analysis script | numpy, matplotlib (see DEPENDENCIES.md) | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.cpp` | C++ source | STM32 firmware | C++ wrapper managing 4x ADAR1000 beamformers | adar1000.h, stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADAR1000_Manager.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADS7830.H` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ADS7830.c` | C source | STM32 firmware | ADS7830 8-ch ADC I2C driver (Idq / temperature) | ADS7830.H (case mismatch) | INCOMPLETE |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/BMP180.cpp` | C++ source | STM32 firmware | BMP180 barometer driver | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/BMP180.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/DA5578.c` | C source | STM32 firmware | DAC5578 (PA gate-voltage DAC) I2C driver; file name differs from header DAC5578.H | DAC5578.H (case mismatch) | INCOMPLETE |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/DAC5578.H` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/GY_85_HAL.c` | C source | STM32 firmware | GY-85 IMU (ADXL345/ITG3205/HMC5883L) I2C driver | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/GY_85_HAL.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/RadarSettings.cpp` | C++ source | STM32 firmware | Radar parameter container/parser | RadarSettings.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/RadarSettings.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/TinyGPS++.cpp` | C++ source | STM32 firmware | Arduino TinyGPS++ NMEA parser (third-party, Arduino API) | TinyGPS++.h; Arduino String/Stream in original | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/TinyGPS++.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/TinyGPSPlus.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.cpp` | C++ source | STM32 firmware | USB CDC command parser (SET/END framing, start flag 23,46,158,237) | usbd_cdc_if.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/USBHandler.h` | C/C++ header | STM32 firmware | USB handler interface | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ad9523.c` | C source | STM32 firmware | ADI no-OS AD9523 clock generator driver | no_os_spi.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/ad9523.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adar1000.c` | C source | STM32 firmware | ADAR1000 register driver (HAL SPI/GPIO) | stm32f7xx_hal_spi.h/gpio.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adar1000.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adf4382.c` | C source | STM32 firmware | ADI no-OS ADF4382 synthesizer driver | no_os_spi.h, no_os_util.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adf4382.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adf4382a_manager.c` | C source | STM32 firmware | Project wrapper for TX/RX ADF4382A | adf4382.h, platform_noos_stm32.H | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/adf4382a_manager.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/errno.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/gps_handler.cpp` | C++ source | STM32 firmware | GPS UART -> USB forwarding | usb_device.h, usbd_cdc_if.h (absent), TinyGPSPlus.h | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/gps_handler.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio.c` | C source | STM32 firmware | ADI no-OS IIO daemon (not used by main.cpp; pulls tcp_socket.h/lwip) | tcp_socket.h, lwip_socket.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio.h` | C/C++ header | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio_app.c` | C source | STM32 firmware | ADI no-OS IIO app (unused; references xilinx/maxim/aducm headers) | parameters.h, xilinx_uart.h ... (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio_app.h` | C/C++ header | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio_trigger.c` | C source | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio_trigger.h` | C/C++ header | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iio_types.h` | C/C++ header | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iiod.c` | C source | STM32 firmware | ADI no-OS IIOD protocol (unused) | iiod_private.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iiod.h` | C/C++ header | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/iiod_private.h` | C/C++ header | STM32 firmware | ADI no-OS IIO stack (unused by main.cpp) | no_os_* | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/jesd204.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_ain.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_alloc.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_alloc.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_aout.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_axi_io.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_circular_buffer.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_circular_buffer.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_clk.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_clk.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc16.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc16.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc24.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc24.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc8.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_crc8.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_delay.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_dma.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_dma.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_eeprom.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_eeprom.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_error.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_fifo.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_fifo.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_flash.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_font_8x8.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_gpio.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_gpio.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_i2c.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_i2c.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_i3c.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_i3c.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_init.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_irq.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_irq.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_lf256fifo.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_lf256fifo.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_list.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_list.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_mdio.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_mdio.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_mutex.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_mutex.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_pid.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_pid.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_print_log.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_pwm.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_pwm.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_rtc.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_semaphore.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_semaphore.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_sin_lut.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_spi.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_spi.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_tdm.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_tdm.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_timer.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_timer.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_trng.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_trng.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_uart.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_uart.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_units.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_util.c` | C source | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/no_os_util.h` | C/C++ header | STM32 firmware | ADI no-OS framework source (third-party, vendored) | no_os_*.h | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/platform_noos_stm32.H` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/platform_noos_stm32.c` | C source | STM32 firmware | Glue binding no-OS SPI/GPIO/delay to STM32 HAL | platform_noos_stm32.H (case mismatch), stm32_spi.h | INCOMPLETE |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_delay.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_delay.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_dma.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_dma.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_gpio.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_gpio.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_gpio_irq.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_gpio_irq.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_hal.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_i2c.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_i2c.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_irq.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_irq.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_pwm.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_pwm.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_spi.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_spi.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_timer.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_timer.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_uart.c` | C source | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_uart.h` | C/C++ header | STM32 firmware | ADI no-OS STM32 platform driver (third-party, vendored; needs HAL) | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32f7xx_hal_conf.h` | C/C++ header | STM32 firmware | CubeMX-style HAL module enable list and oscillator values | STM32CubeF7 HAL headers (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32f7xx_hal_msp.c` | C source | STM32 firmware | CubeMX-style MSP init: peripheral GPIO/AF/DMA/IRQ configuration (verified pin evidence) | stm32f7xx_hal.h (absent), main.h | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32f7xx_it.c` | C source | STM32 firmware | Interrupt handlers | stm32f7xx_hal.h (absent), main.h | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32f7xx_it.h` | C/C++ header | STM32 firmware | C/C++ header | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/syscalls.c` | C source | STM32 firmware | Newlib syscall stubs | libc | COMPLETE |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/sysmem.c` | C source | STM32 firmware | Newlib _sbrk heap | libc; linker symbols from missing .ld | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/system_stm32f7xx.c` | C source | STM32 firmware | CMSIS SystemInit / SystemCoreClock | stm32f7xx.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_2_C_Cpp_Algorithms/STM32_ALGO.docx` | Word document | STM32 firmware | Firmware algorithm description (Word) | — | REQUIRES VALIDATION |
| `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp` | C++ source | STM32 firmware | CubeMX-style main: power sequencing, AD9523/ADF4382/ADAR1000 setup, GPS/IMU, USB CDC, chirp scheduling (2411 lines) | main.h, usb_device.h, usbd_cdc_if.h (absent), HAL (absent), all drivers | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h` | C/C++ header | STM32 firmware | Pin macros and handle externs | stm32f7xx_hal.h (absent) | MISSING DEPENDENCY |
| `9_Firmware/9_1_Microcontroller/reconstructed/CMakeLists.txt` | Text | STM32 firmware | Text | — | UNKNOWN |
| `9_Firmware/9_2_FPGA/ad9484_interface_400m.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/cdc_modules.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/chirp_lut_init.v` | Verilog RTL | FPGA | Bare `initial` block (no module) initialising long_chirp_lut[]; include-fragment, not standalone | a module declaring long_chirp_lut | INCOMPLETE |
| `9_Firmware/9_2_FPGA/chirp_memory_loader_param.v` | Verilog RTL | FPGA | $readmemh loader for 4x1024 long-chirp segments + short chirp | long_chirp_seg0..3_{i,q}.mem (seg3 MISSING), short_chirp_{i,q}.mem | MISSING DEPENDENCY |
| `9_Firmware/9_2_FPGA/cic_decimator_4x_enhanced.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/cntrt.xdc` | Vivado constraints | FPGA | Vivado constraints: clocks + I/O standards; 142 [PIN_NUMBER] placeholders, invalid PACKAGE_PIN_BANK property | radar_system_top.v port names | PLACEHOLDER |
| `9_Firmware/9_2_FPGA/dac_interface_single.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/ddc_400m.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/ddc_input_interface.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/doppler_processor.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/edge_detector.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/fft_1024_forward.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/fft_1024_inverse.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/fir_lowpass.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/frequency_matched_filter.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/latency_buffer_2159.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/level_shifter_interface.v` | Verilog RTL | FPGA | Pass-through of STM32 SPI 3.3 V <-> ADAR1000 1.8 V through FPGA banks | — | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/long_chirp_seg0_i.mem` | Memory init (hex) | FPGA | Long chirp LUT segment, 1024 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/long_chirp_seg0_q.mem` | Memory init (hex) | FPGA | Long chirp LUT segment, 1024 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/long_chirp_seg1_i.mem` | Memory init (hex) | FPGA | Long chirp LUT segment, 1024 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/long_chirp_seg1_q.mem` | Memory init (hex) | FPGA | Long chirp LUT segment, 1024 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/long_chirp_seg2_i.mem` | Memory init (hex) | FPGA | Long chirp LUT segment, 1024 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/long_chirp_seg2_q.mem` | Memory init (hex) | FPGA | Long chirp LUT segment, 1024 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/lvds_to_cmos_400m.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/matched_filter_multi_segment.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/nco_400m_enhanced.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/plfm_chirp_controller.v` | Verilog RTL | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/radar_receiver_final.v` | Verilog RTL | FPGA | RX chain: ADC LVDS -> DDC -> CIC -> FIR -> matched filter -> Doppler | ad9484_interface_400m.v, ddc_400m.v, cic_decimator_4x_enhanced.v, fir_lowpass.v, matched_filter_multi_segment.v, doppler_processor.v | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/radar_system_tb.v` | Verilog RTL | FPGA | System testbench with SystemVerilog assertions (needs SV simulator: xsim/Questa; Icarus fails) | radar_system_top.v | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/radar_system_top.v` | Verilog RTL | FPGA | FPGA top level: 67 ports, instantiates transmitter, receiver, USB, level shifter, CDC | all other RTL; cntrt.xdc; .mem files | INCOMPLETE |
| `9_Firmware/9_2_FPGA/radar_transmitter.v` | Verilog RTL | FPGA | TX: chirp controller -> DAC interface, ADAR load/TR sequencing | plfm_chirp_controller.v, dac_interface_single.v | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/short_chirp_i.mem` | Memory init (hex) | FPGA | Short chirp I LUT, 50 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/short_chirp_q.mem` | Memory init (hex) | FPGA | Short chirp Q LUT, 50 lines hex | chirp_memory_loader_param.v | COMPLETE |
| `9_Firmware/9_2_FPGA/usb_data_interface.v` | Verilog RTL | FPGA | FT601 32-bit synchronous FIFO master interface | cdc_modules.v | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/usb_packet_analyzer.v` | Verilog RTL | FPGA | Packet framing for USB stream | usb_data_interface.v | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/reconstructed/PIN_MAP_FROM_SCHEMATIC.md` | Markdown | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_2_FPGA/reconstructed/radar_system_top_schematic_derived.xdc` | Vivado constraints | FPGA | Verilog RTL module | see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md hierarchy | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V1.py` | Python | Python GUI | 41-line method fragment (update_gps_display) with leading indent — not a program | — | PLACEHOLDER |
| `9_Firmware/9_3_GUI/GUI_V2.py` | Python | Python GUI | Tk GUI v2: STM32 USB CDC, DBSCAN, Kalman | numpy, scipy, matplotlib, sklearn, filterpy, crcmod, pyusb, pyftdi | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V3.py` | Python | Python GUI | Tk GUI v3: pitch correction, map, real-time plot | same as V2 | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V4.py` | Python | Python GUI | Tk GUI v4: pitch correction | same as V2 | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V4_2_CSV.py` | Python | Python GUI | Offline CSV replay GUI | numpy, scipy, matplotlib, pandas; test_radar_data.csv | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V5.py` | Python | Python GUI | Tk GUI v5 (last complete hardware GUI): Mercury colour map | same as V2 | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V5_Demo.py` | Python | Python GUI | v5 demo with synthetic data + tkinterweb map | same as V2 + tkinterweb | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_V6.gif` | Image | Python GUI | Animated screenshot used by README | — | COMPLETE |
| `9_Firmware/9_3_GUI/GUI_V6.py` | Python | Python GUI | v6 FT601 USB3 GUI — RadarProcessor/USBPacketParser/RadarPacketParser are `pass` stubs ('same as before'); get_packet_length() returns constant 64 | same as V2 | PLACEHOLDER |
| `9_Firmware/9_3_GUI/GUI_V6_Demo.py` | Python | Python GUI | v6 demo: synthetic targets, no hardware | numpy, matplotlib (tkinter) | REQUIRES VALIDATION |
| `9_Firmware/9_3_GUI/GUI_versions.txt` | Text | Python GUI | Change log of GUI versions | — | COMPLETE |
| `9_Firmware/9_3_GUI/pyproject.toml` | .toml | Python GUI | Generated: packaging metadata | setuptools | COMPLETE |
| `9_Firmware/9_3_GUI/requirements.txt` | Text | Python GUI | Generated: pinned/tested Python dependencies | pip | COMPLETE |
| `9_Firmware/9_3_GUI/test_radar_data.csv` | CSV data | Python GUI | Sample data for CSV replay | GUI_V4_2_CSV.py | REQUIRES VALIDATION |
| `docs/01_REPOSITORY_INVENTORY.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/02_DEPENDENCY_MAP.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/03_MISSING_COMPONENTS.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/04_RECOVERY_TASKS.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/05_TRACEABILITY_MATRIX.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_FREQUENCY_SYNTHESIZER.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_FREQUENCY_SYNTHESIZER.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_MAIN_BOARD.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_MAIN_BOARD.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_POWER_SUPPLY.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_POWER_SUPPLY.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_RF_PA.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/BOM_RF_PA.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/README.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/REFS_FREQUENCY_SYNTHESIZER.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/REFS_MAIN_BOARD.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/REFS_POWER_SUPPLY.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/BOM/REFS_RF_PA.csv` | CSV data | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/GUI/DEPENDENCIES.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/GUI/INSTALLATION.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/MECHANICAL/ASSEMBLY_DOCUMENTATION_REQUIREMENTS.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/MECHANICAL/MECHANICAL_GAP_ANALYSIS.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/MECHANICAL/drawings/FREQUENCY_SYNTHESIZER_outline.svg` | SVG figure | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/MECHANICAL/drawings/MAIN_BOARD_outline.svg` | SVG figure | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/MECHANICAL/drawings/POWER_SUPPLY_outline.svg` | SVG figure | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/MECHANICAL/drawings/RF_PA_outline.svg` | SVG figure | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/PCB/FREQUENCY_SYNTHESIZER.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/PCB/MAIN_BOARD.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/PCB/POWER_SUPPLY.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/PCB/RF_PA.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/SYSTEM/BLOCK_DIAGRAM.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/TESTING/ACCEPTANCE_CRITERIA.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `docs/TESTING/VALIDATION_PLAN.md` | Markdown | Engineering manual (generated) | Engineering reconstruction manual (generated by this project) | tools/ | COMPLETE |
| `research/03_hw_improvements.md` | Markdown | Docs: research | Improvement research survey (references missing sibling files) | — | INCOMPLETE |
| `tools/check_doc_links.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/check_fpga_constraints.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/check_manufacturing_files.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/check_missing_files.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/check_python_imports.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/check_stm32_includes.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/extract_eagle_netlist.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/fpga_lint.sh` | Shell script | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/gen_board_outline_svg.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/gen_eagle_bom.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/gen_inventory_doc.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/gen_xdc_from_schematic.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/repo_inventory.py` | Python | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/run_all_checks.sh` | Shell script | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/stm32_check_cube_package.sh` | Shell script | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
| `tools/vivado/create_project.tcl` | .tcl | Automation | Validation / generation script (this project) | Python 3.10+, bash | COMPLETE |
