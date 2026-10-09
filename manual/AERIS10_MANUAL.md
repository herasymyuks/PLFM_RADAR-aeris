# AERIS-10 — Complete Engineering & Assembly Manual

**Author: Antidrone Ukraine · antidrone.cc**

Built 2026-10-09 by tools/build_manual.py from manual/chapters (order: manual/00_OUTLINE.md). Status: BETA documentation — no item is hardware-verified; see the status label on every figure and procedure.

<!-- chapter 0: Title, status statement, how to read, revision table -->
# Title, status statement, how to read, revision table

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` header, `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §1–2

**Planned figures:** —

## Content

(to write) — must include: author line **Antidrone Ukraine · antidrone.cc**, revision table (edition, date, author, scope), status statement, how to read the status labels, acknowledgement of the upstream project files (ORIGINAL PROJECT FILE).


---

<!-- chapter 1: What AERIS-10 is: pulsed-LFM X-band phased array, variants Nexus/Extended, performance targets vs calculated -->
# What AERIS-10 is: pulsed-LFM X-band phased array, variants Nexus/Extended, performance targets vs calculated

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `README.md`, `00_notation/parameter_table.md`, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, `docs/SYSTEM/BLOCK_DIAGRAM.md`

**Planned figures:** F1.1 system block diagram (SYS-01), F1.2 original drawio diagram, F1.3 photos

## Content

(to write)


---

<!-- chapter 2: Waveform/timing, beamforming, signal processing chain, data path -->
# Waveform/timing, beamforming, signal processing chain, data path

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `01_physics/*`, `02_hardware/04_antenna_beamforming.md`, `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.*`, `DATA_FLOW/end_to_end_data_flow.*`, `engineering/SYSTEM/data_flow/*`

**Planned figures:** F2.1 signal/data flow (SYS-03), F2.2 FPGA pipeline (SD-02), F2.3 end-to-end flow (SD-07)

## Content

(to write)


---

<!-- chapter 3: Boards, modules, connectors, cables, power rails -->
# Boards, modules, connectors, cables, power rails

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/SYSTEM/interfaces/*`, `engineering/ELECTRICAL/power_distribution/*`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`

**Planned figures:** F3.1 interconnection diagram (SYS-02), F3.2 power distribution (ELEC-PWR-01), tables: interconnection, rails, harness

## Content

(to write)


---

<!-- chapter 4: Main Board: schematic set, layout, BOM, DRC state, rev. B host interface -->
# Main Board: schematic set, layout, BOM, DRC state, rev. B host interface

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/ELECTRICAL/schematics/MAIN_BOARD/`, `engineering/PCB/MAIN_BOARD/README.md`, `beta/pcb/MAIN_BOARD*/README.md`, `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md`

**Planned figures:** F4.1–4.4 schematic sheets, F4.5 top/bottom layer plots, F4.6 3-D render, F4.7 assembly drawing

## Content

(to write)


---

<!-- chapter 5: Power Board -->
# Power Board

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** same pattern, POWER_SUPPLY

**Planned figures:** F5.x

## Content

(to write)


---

<!-- chapter 6: Synth board -->
# Synth board

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** same pattern, FREQUENCY_SYNTHESIZER

**Planned figures:** F6.x

## Content

(to write)


---

<!-- chapter 7: RF PA board (×16) -->
# RF PA board (×16)

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** same pattern, RF_PA; `engineering/DESIGN/THERMAL/*`

**Planned figures:** F7.x

## Content

(to write)


---

<!-- chapter 8: Proposed 16×8 patch panel: design, simulation, fabrication data -->
# Proposed 16×8 patch panel: design, simulation, fabrication data

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/DESIGN/ANTENNA/*`

**Planned figures:** F8.1 layout drawing, F8.2 3-D render, F8.3 S11 plot, F8.4 coupling

## Content

(to write)


---

<!-- chapter 9: FPGA→host path (options A/B), 22 V PA supply module -->
# FPGA→host path (options A/B), 22 V PA supply module

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/DESIGN/HOST_LINK/*`, `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/*`

**Planned figures:** F9.1 PSU block schematic, tables: FT601 pin plan, bridge frame

## Content

(to write)


---

<!-- chapter 10: Head and pedestal: layout, drawings, parts, flat patterns, thermal map, torque -->
# Head and pedestal: layout, drawings, parts, flat patterns, thermal map, torque

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/DESIGN/MECHANICAL/*`, `engineering/DESIGN/CALCS/*`, `engineering/MECHANICAL/*`

**Planned figures:** F10.1–10.5 DSN-MECH-01…05, F10.6 flat patterns, F10.7 section with fasteners, F10.8 isometrics, F10.9 thermal map, F10.10 PCB plan view

## Content

(to write)


---

<!-- chapter 11: FPGA design: module hierarchy, build, constraints, tests, synthesis status -->
# FPGA design: module hierarchy, build, constraints, tests, synthesis status

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `beta/fpga/README.md`, `engineering/SOFTWARE_DIAGRAMS/FPGA/*`, `beta/fpga_synth/README.md`

**Planned figures:** F11.1 hierarchy (SD-01), F11.2 pipeline

## Content

(to write)


---

<!-- chapter 12: Firmware: architecture, build, defects fixed, sequencing, USB protocol -->
# Firmware: architecture, build, defects fixed, sequencing, USB protocol

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `beta/stm32/README.md`, `DECISIONS.md`, `engineering/SOFTWARE_DIAGRAMS/STM32/*`

**Planned figures:** F12.1 architecture (SD-03), F12.2 USB CDC flow (SD-04)

## Content

(to write)


---

<!-- chapter 13: GUI: install, run, protocol, register panel, packaging -->
# GUI: install, run, protocol, register panel, packaging

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `beta/gui/README.md`, `engineering/SOFTWARE_DIAGRAMS/PYTHON/*`

**Planned figures:** F13.1 modules (SD-05), F13.2 runtime (SD-06), screenshots to render (`--demo`, headless Tk)

## Content

(to write)


---

<!-- chapter 14: Manufacturing packages per board, stack-ups, BOMs with MPN confidence, fab checklist -->
# Manufacturing packages per board, stack-ups, BOMs with MPN confidence, fab checklist

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/PCB/*/README.md`, `beta/pcb/*/FAB_NOTES.md`, `BOM_*_beta.csv`

**Planned figures:** tables

## Content

(to write)


---

<!-- chapter 15: Step-by-step mechanical assembly, board installation, harness, integration order, inspection checkpoints -->
# Step-by-step mechanical assembly, board installation, harness, integration order, inspection checkpoints

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `manual/ASSEMBLY_STEPS_SOURCE.md` (+ its sources)

**Planned figures:** F15.x exploded view, DSN-MECH-04/06/07, harness, connector positions

## Content

(to write)


---

<!-- chapter 16: Power-up, firmware flashing, FPGA programming, calibration (ADC taps, beam), bench tests, acceptance criteria -->
# Power-up, firmware flashing, FPGA programming, calibration (ADC taps, beam), bench tests, acceptance criteria

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §B/D, `docs/TESTING/*`, beta READMEs

**Planned figures:** tables

## Content

(to write)


---

<!-- chapter 17: K1–K8, D-01…D-19, G-01…G-12, MDR-*, register of unresolved items -->
# K1–K8, D-01…D-19, G-01…G-12, MDR-*, register of unresolved items

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `docs/03_MISSING_COMPONENTS.md`, `docs/04_RECOVERY_TASKS.md`, `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`, `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`

**Planned figures:** —

## Content

(to write)


---

<!-- chapter A: Drawing register (copy) -->
# Drawing register (copy)

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `engineering/DRAWING_REGISTER.md`

**Planned figures:** —

## Content

(to write)


---

<!-- chapter B: Parts lists (PCB BOM summaries, mechanical parts, fasteners), cable schedule -->
# Parts lists (PCB BOM summaries, mechanical parts, fasteners), cable schedule

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `docs/BOM/*.md`, `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`

**Planned figures:** —

## Content

(to write)


---

<!-- chapter C: Tools and scripts (what each generator does, how to regenerate) -->
# Tools and scripts (what each generator does, how to regenerate)

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `tools/*.py` docstrings, `engineering/README.md`, `beta/README.md`

**Planned figures:** —

## Content

(to write)


---

<!-- chapter D: Glossary, acronyms, status vocabulary -->
# Glossary, acronyms, status vocabulary

<!-- STUB: to be written by Claude Design per MANUAL_BUILD_SPEC.md -->

**Status summary:** (to fill — list the status label of every item in this chapter)

**Sources:** `00_notation/*`

**Planned figures:** —

## Content

(to write)
