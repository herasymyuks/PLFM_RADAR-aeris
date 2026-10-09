# AERIS-10 — Complete Engineering & Assembly Manual

**Author: Antidrone Ukraine · antidrone.cc**

Built 2026-10-09 by tools/build_manual.py from manual/chapters (order: manual/00_OUTLINE.md). Status: BETA documentation — no item is hardware-verified; see the status label on every figure and procedure.

<!-- chapter 0: Title, status statement, how to read, revision table -->
# AERIS-10 — Complete Engineering & Assembly Manual

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** this chapter is editorial (BETA documentation edition). It introduces a manual in which no item is VERIFIED on hardware; every figure and procedure carries one of the labels defined in section 4 below.

**Sources:** `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` (header, v1.3), `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §1–2, `MANUAL_BUILD_SPEC.md`, `manual/STYLE_GUIDE.md`, `manual/00_OUTLINE.md`, `README.md`.

**Planned figures:** none.

## 1. Title and authorship

| Field | Value |
|---|---|
| Title | AERIS-10 — Pulsed-LFM X-band phased-array radar — Complete Engineering & Assembly Manual |
| Author (compilation, generated drawings, reconstruction, proposed designs) | Antidrone Ukraine · antidrone.cc |
| Edition | 2026-10-09 — BETA |
| Compiled from | repository `PLFM_RADAR` (branch `main`), reconstruction documents `docs/`, engineering package `engineering/`, BETA implementations `beta/` |
| Upstream project files | NawfalMotii79/PLFM_RADAR, labelled ORIGINAL PROJECT FILE wherever they appear (source: `README.md` badges; `MANUAL_BUILD_SPEC.md` §AUTHORSHIP) |
| Build | `python3 tools/build_manual.py` concatenates `manual/chapters/*.md` in the order of `manual/00_OUTLINE.md` and writes `manual/AERIS10_MANUAL.md`, `manual/build/AERIS10_MANUAL.html` and `manual/build/AERIS10_MANUAL.pdf` |

The manual's authorship covers the compilation, the generated drawings (title blocks carry the `ATTRIBUTION` line of `tools/eagle_svg_common.py`), the reconstruction work and the proposed designs. Original upstream files (EAGLE schematics and boards, firmware sources, GUI scripts, photographs, the draw.io block diagram) keep their own authorship and are labelled ORIGINAL PROJECT FILE in captions and tables (source: `manual/STYLE_GUIDE.md`, rule "Authorship").

## 2. Revision table

| Edition | Date | Author | Scope | Status |
|---|---|---|---|---|
| 2026-10-09 | 2026-10-09 | Antidrone Ukraine · antidrone.cc | First complete edition: system description, theory of operation, architecture and interfaces, four PCBs, antenna, host link and 22 V supply, mechanical design, FPGA/STM32/GUI, manufacturing, assembly and bring-up procedures, open-issue registers, appendices | BETA — not hardware-verified |

Lineage of the source documents this edition compiles (each is cited where used):

| Source document | Version / date | Content |
|---|---|---|
| `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` | v1.3, 2026-10-09 (v1.0 2026-10-08; v1.1 drawings package; v1.2 proposed designs; v1.3 BETA) | reconstruction, build preparation and documentation manual, Parts I–XIII |
| `docs/AERIS10_BETA_ENGINEERING_REPORT.md` | v0.9 draft, 2026-10-09 | consolidated report of everything built, simulated and calculated in the BETA phase, with executed evidence |
| `engineering/DRAWING_REGISTER.md` | 2026-10-09 | 89 registered drawings (39 SOURCE-DERIVED, 28 PARTIAL, 16 PROPOSED, 1 CONCEPTUAL, 5 BLOCKED); file check 333 OK, 0 problems |
| `engineering/DESIGN/00_DESIGN_BASIS.md` | DSN-00 Rev A, 2026-10-09 | design basis and decision log D-01…D-15 for the proposed designs |
| `beta/fpga`, `beta/stm32`, `beta/gui`, `beta/pcb` READMEs and CHANGELOGs | 2026-10-09 | BETA implementations (build/simulate/test on a workstation only) |
| Upstream repository content | dated 2026-03-14 (source: `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md` header) | schematics, layouts, firmware, GUI, physics notes, photographs |

## 3. Status statement

The reconstruction manual summarises the repository state in one sentence: "the repository is a documented design study with schematics for four boards, partially routed layouts, non-building FPGA RTL, non-building STM32 firmware, one offline-runnable Python demo, and no mechanical design. No subsystem can be built reproducibly today" (source: `docs/AERIS10_ENGINEERING_BUILD_MANUAL.md`, header, "Readiness in one sentence"). The BETA phase changed the software state on the authoring workstation but not the hardware state; the executed evidence per area is (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §1, copied):

| Area | State before | State now | Executed evidence |
|---|---|---|---|
| FPGA RTL | did not parse; 5 modules/IP missing; 400 MHz fabric; no host path | parses/lints; all modules present; ISERDES 1:4 capture + 100 MHz polyphase DDC (bit-exact vs legacy); SPI host bridge; register map | `beta/fpga/build.sh`: 0 failures, 9 testbench runs PASS |
| STM32 firmware | no build system/HAL; 7+ defects; empty ADAR1000 phase tables | builds and links (93 KB flash); 12 defects fixed; ADAR1000 tables from the datasheet; bridge + REG commands | `beta/stm32/build.sh` exit 0; host tests 6/6 |
| Python GUI | V6 stub; no tests; wrong packet format | package with firmware-exact protocol, bridge-frame path, register panel, simulator; PyInstaller app | pytest 72 passed; selftests exit 0 |
| PCBs | no Gerbers; Main 15 / Power 308 unconnected; 0 MPN | Main/RF PA 0 unconnected; Power 89 (listed); BOM MPNs; fab notes; full packages; Main rev. B with FT601 | KiCad DRC reports, export logs |
| Host data path | FT601 unwired | option A pin plan (bank 35) + option B SPI bridge implemented end-to-end | tb PASS, firmware build, GUI tests on the RTL vector |
| Antenna | none | 16×8 patch panel, KiCad board, openEMS simulated | S11 −18 dB at f0, 128 MHz band, coupling −20.7 dB |
| Thermal / power | none | drain-gating requirement, 22 V module design, 2-D plate map | 64 °C plate / ≈ 73 °C PA base in case B |
| Mechanics | none | head + pedestal, 51-part detail model, flat patterns, parts list; torque check | FreeCAD model builds; register file check 0 problems |
| Radar performance | TBD everywhere | range equation with simulated gain | R(1 m²) ≈ 6 km at B = 50 MHz |

What remains impossible on the authoring machine, and therefore is not claimed anywhere in this manual: Vivado synthesis, timing and bitstream generation; flashing and bench tests; PCB fabrication; measurement of component heights; antenna coupon on a VNA; PA thermal test; the 89 Power Board pour connections (manual CAD); EAGLE schematic updates for rev. B; the owner decisions K1–K8 and D-01…D-19 (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §2).

## 4. How to read the status labels

Every figure caption and every procedure title carries exactly one of the following labels (source: `manual/STYLE_GUIDE.md`, "Status vocabulary"; `MANUAL_BUILD_SPEC.md`, "HARD RULES"). Nothing in this manual is promoted above the status recorded in its source register.

| Label | Meaning | Typical content |
|---|---|---|
| ORIGINAL PROJECT FILE | as found in the upstream repository; authorship stays with the upstream project; photographs carry no dimensions | `8_Utils/*.jpg`, `2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg`, EAGLE `.sch`/`.brd`, `9_Firmware/` |
| SOURCE-DERIVED | generated from the native design files by a repository tool; some elements may be unverifiable and are listed | schematic renders, KiCad-converted board plots, system diagrams SYS-01…04, netlists |
| PARTIAL | significant parts missing from the sources | FPGA pipeline SD-02, STM32 diagrams SD-03/04, end-to-end flow SD-07 |
| CONCEPTUAL | documented intent only, no geometry or wiring behind it | exploded view ASM-EXP-01, antenna and host blocks in SYS-01 |
| PROPOSED DESIGN | new engineering content that depends on logged decisions D-xx | antenna panel, head and pedestal, 22 V supply, harness schedule, host link |
| BETA | builds, simulates or tests on a workstation; not synthesised for the target, not flashed, not on hardware | `beta/fpga`, `beta/stm32`, `beta/gui`, `beta/pcb` |
| BLOCKED — MISSING DATA | cannot be produced from the repository | enclosure dimensions, component heights, cable lengths (G-01…G-12) |
| VERIFIED | reserved for hardware- or vendor-confirmed items; **currently unused in the whole project** | — |

Supplementary vocabularies used inside copied tables keep the meaning of their source: CONFIRMED / UNVERIFIED / MISSING SPEC (interconnection and power-rail registers, source: `engineering/SYSTEM/interfaces/interconnection_table.md`), DONE / OPEN / BLOCKED (task tracker, source: `docs/04_RECOVERY_TASKS.md`), MET / NOT MET / NOT RUN / PARTIALLY MET (acceptance criteria, source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`), ASSUMED / ESTIMATE (numbers, source: `manual/STYLE_GUIDE.md`). Citations are inline, in the form `(source: path:line)` or `(source: path §section)`; a table copied from a source states the source once in its caption or lead-in. Where a value is not available in any repository file the text says "UNKNOWN" and names the register item that tracks it.

Identifier families used for cross-references (defined in Appendix D): K1–K8 configuration conflicts, D-01…D-19 design decisions, G-01…G-12 geometry gaps, MDR-01…13 missing-drawing recovery guides, DSN-* proposed-design drawings, SYS-/SD-/ELEC-/MECH-/ASM-/PCB-* registered drawings, CBL-* cables, AC-* acceptance criteria, R-* recovery tasks, C1–C7 firmware conflicts, MAN-* observations raised by this manual.

## 5. Safety

Three hazards are present in the design as documented and are repeated before the first procedure step that needs them (source: `manual/STYLE_GUIDE.md`, rule "Procedures"): the 22 V PA drain supply (QPA2962 bias-up sequence VG −4 V → VD +22 V, 2 A per board, 16 boards; source: `engineering/ELECTRICAL/power_distribution/power_rails.md` §1 row `+22V0`/`VD`), RF radiation from the array (up to 16 × 10 W peak for the Extended variant; source: `README.md`, Technical Specifications), and the rotating pedestal (head mass estimate 10.4 kg, 50 azimuth positions per revolution; source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §2).

## 6. Upstream acknowledgement

The AERIS-10 project was published by NawfalMotii79 as `PLFM_RADAR` under an MIT licence badge (source: `README.md`, lines 3–6). The upstream repository supplies the four EAGLE schematic/board sets, the FPGA RTL, the STM32 sources, the Python GUI versions, the physics and hardware notes under `00_notation/`, `01_physics/`, `02_hardware/`, the power-management spreadsheet, the draw.io block diagram and the photographs. These files are reproduced or rendered in this manual as ORIGINAL PROJECT FILE and were not modified (source: `MANUAL_BUILD_SPEC.md`, "Preserve originals"). No `LICENSE` file exists in the repository root; acceptance criterion AC-D4 records that the licence file consistent with the badge is NOT MET (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`, row AC-D4).

## 7. Document map

Chapter order equals the concatenation order of `manual/00_OUTLINE.md` (copied):

| # | Chapter | Content | Status of content |
|---|---|---|---|
| 0 | Front matter | title, revision table, status statement, labels, acknowledgement, map | editorial |
| 1 | System overview | pulsed-LFM X-band phased array, variants Nexus/Extended, documented vs calculated performance, conflicts K1–K8 | SOURCE-DERIVED + PROPOSED (calculations) |
| 2 | Theory of operation | waveform and timing, pulse compression, Doppler, beamforming, FPGA chain, data path | ORIGINAL PROJECT FILE (physics notes) + PARTIAL (RTL diagrams) + BETA |
| 3 | Architecture and interfaces | boards, connectors, cables, power rails, enable sequence, harness | SOURCE-DERIVED + PROPOSED (harness) |
| 4 | Main Board | schematic set, layout, BOM, DRC state, rev. B host interface | SOURCE-DERIVED + BETA |
| 5 | Power Supply Board | same pattern | SOURCE-DERIVED + BETA |
| 6 | Frequency Synthesizer | same pattern | SOURCE-DERIVED + BETA |
| 7 | RF PA board (×16) | same pattern + thermal | SOURCE-DERIVED + BETA + PROPOSED |
| 8 | Antenna | proposed 16×8 patch panel, simulation, fabrication data | PROPOSED DESIGN |
| 9 | Host link and 22 V supply | FPGA→host options A/B, 22 V PA supply module | PROPOSED DESIGN + BETA |
| 10 | Mechanical design | head and pedestal, drawings, parts, flat patterns, thermal map, torque | PROPOSED DESIGN |
| 11 | FPGA firmware | hierarchy, build, constraints, tests, synthesis status | BETA |
| 12 | STM32 firmware | architecture, build, defects fixed, sequencing, USB protocol | BETA |
| 13 | GUI software | install, run, protocol, register panel, packaging | BETA |
| 14 | Manufacturing | packages per board, stack-ups, BOMs, fab checklist | SOURCE-DERIVED + BETA |
| 15 | Assembly procedure | numbered steps with checks | PROPOSED DESIGN (geometry) |
| 16 | Bring-up and test | power-up, flashing, calibration, bench tests, acceptance | procedures OPEN, not executed |
| 17 | Open issues and decisions | K, D, G, MDR, R registers | registers |
| A | Drawing register | copy of `engineering/DRAWING_REGISTER.md` | register |
| B | Parts and cables | BOM summaries, mechanical parts, cable schedule | SOURCE-DERIVED + PROPOSED |
| C | Tooling | generators and checkers under `tools/` | documentation |
| D | Glossary | acronyms, symbols, status vocabulary, ID families | documentation |


---

<!-- chapter 1: What AERIS-10 is: pulsed-LFM X-band phased array, variants Nexus/Extended, performance targets vs calculated -->
# System overview — what AERIS-10 is

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** system description SOURCE-DERIVED (reconstructed from the four EAGLE schematics, the firmware and the RTL); variant table and performance targets ORIGINAL PROJECT FILE (README claims, not verified); calculated performance PROPOSED DESIGN / BETA (DSN-CALC-01, with stated assumptions); figures F1.1 SOURCE-DERIVED, F1.2 and F1.3 ORIGINAL PROJECT FILE. Eight configuration conflicts K1–K8 between the CAD and the documentation remain open.

**Sources:** `README.md`, `00_notation/parameter_table.md`, `docs/SYSTEM/BLOCK_DIAGRAM.md`, `docs/AERIS10_BETA_ENGINEERING_REPORT.md`, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, `engineering/SYSTEM/architecture/README.md`, `02_hardware/01_system_overview.md`.

**Planned figures:** F1.1 system block diagram (SYS-01), F1.2 original draw.io block diagram, F1.3 prototype photographs.

## 1. Purpose and principle

AERIS-10 is described by its upstream README as "an open-source, low-cost 10.5 GHz phased array radar system featuring Pulse Linear Frequency Modulated (LFM) modulation", available in two versions (3 km and 20 km range) for researchers, drone developers and SDR enthusiasts (source: `README.md`, introduction). The radar transmits linear-frequency-modulated pulses (chirps) at X-band, steers the beam electronically in elevation with four ADAR1000 beamformer ICs across a 16-element linear array, rotates the head mechanically in azimuth with a stepper motor, and processes the echoes in an FPGA (down-conversion, decimation, pulse compression, Doppler FFT, detection) before sending results to a host PC running a Python GUI (source: `README.md`, "Processing Pipeline"; `engineering/DESIGN/00_DESIGN_BASIS.md` §1, row "Array").

The carrier frequency f_c = 10.5 GHz and wavelength λ = 0.02857 m are the canonical values (source: `00_notation/parameter_table.md`, "Inconsistency Resolutions" §1; `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp:1133`). The pulse timing coded in the firmware is: long chirp 30 µs at PRI 167 µs, short chirp 0.5 µs at PRI 175 µs, guard 175.4 µs, 32 chirps per beam position, 31 elevation positions, 50 azimuth positions per revolution (source: `main.cpp:178-184`, `main.cpp:190`; `00_notation/parameter_table.md`, "Waveform and Timing"). The chirp bandwidth B is **TBD** in the parameter table ("Requires ADF4382 config"); every range-resolution and range-equation number in this manual that depends on B says so explicitly.

![Figure 1 — F1.1 — System block diagram SYS-01, all subsystems with status legend — SOURCE-DERIVED; antenna, host PC, 22 V supply and off-board modules are CONCEPTUAL (source: engineering/SYSTEM/block_diagrams/system_block_diagram.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SYSTEM/block_diagrams/system_block_diagram.png)

Figure F1.1 shows what is wired in the CAD, not what the README describes; every box and edge is traceable to a repository file (source: `engineering/SYSTEM/architecture/README.md`, row SYS-01). The original designer's block diagram is reproduced as F1.2 for comparison; it labels the FPGA XC7A50T-2FTG256 and names the parts FPGA, AD9708, ADF4382 TX/RX, LTC5552 ×2, LPF/BPF, AD9484, EP4RKU+, ADAR1000 ×4, ADTR1107, M3SWA2-34DR+, FT601, STM32F746ZGT7, AD8352, OCXO ECOC-2522-10.000, AD9523, XO CCHD-957-100, VCXO CVHD-950-100.000, MTX2-143+, ATS1005-3DB and "QPA2862 ×4" (the CAD has QPA2962_B) (source: `engineering/SYSTEM/architecture/README.md`, row SYS-01, "RADAR_V6.drawio original block names").

![Figure 2 — F1.2 — Original functional block diagram RADAR_V6, draw.io 29.6.1 export — ORIGINAL PROJECT FILE, upstream authorship, not dimensioned (source: 2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg; as found)](2_Functional Diagram & Interconnection Matrices/RADAR_V6.jpg)

## 2. Variants

The README specifies two variants (source: `README.md`, "Technical Specifications", copied verbatim):

| Parameter | AERIS-10N (Nexus) | AERIS-10X (Extended) |
|---|---|---|
| **Frequency** | 10.5 GHz | 10.5 GHz |
| **Max Range** | 3 km | 20 km |
| **Antenna** | 8x16 Patch Array | 32x16 Slotted Waveguide |
| **Beam Steering** | Electronic (±45°) | Electronic (±45°) |
| **Mechanical Scan** | 360° (stepper motor) | 360° (stepper motor) |
| **Output Power** | ~1Wx16 | 10Wx16 (GaN amplifier) |
| **Processing** | FPGA + STM32 | FPGA + STM32 |

The hardware notes add the following per-variant differences (source: `02_hardware/01_system_overview.md` §2.1, copied; gains are marked TBD in the source):

| | Nexus (AERIS-10N) | Extended (AERIS-10X) |
|---|---|---|
| Transmit power P_t per element | 1 W (ADTR1107) | 10 W (QPA2962 GaN) |
| Antenna type | 8x16 patch array | 32x16 slotted waveguide |
| Antenna gain G | ~20 dBi (patch, TBD) | ~30 dBi (waveguide, TBD) |
| Detection range R_max | 3 km | 20 km |

Three facts qualify this table. (1) The README names the PA-board variant "AERIS-10E" in one place and "AERIS-10X" elsewhere (source: `README.md:79` vs `README.md:24,83`); this manual uses AERIS-10X. (2) The "±45°" steering figure is a README statement; the firmware phase table spans −160° to +160° and the parameter table derives from it a steering range it states as "approximately ±33°" (source: `00_notation/parameter_table.md`, "Inconsistency Resolutions" §4) — the arithmetic disagreement between the project's own documents is recorded as observation MAN-01 in chapter 17. (3) No antenna CAD exists for either variant (conflict K8); the only antenna geometry in the repository is the PROPOSED 16-row × 8-patch panel of `engineering/DESIGN/ANTENNA/` (chapter 8).

![Figure 3 — F1.3 — Prototype antenna array photograph — ORIGINAL PROJECT FILE, undimensioned, not used for any dimension in this manual (source: 8_Utils/Antenna_Array.jpg; as found)](8_Utils/Antenna_Array.jpg)

![Figure 4 — F1.3b — Prototype electronics photograph — ORIGINAL PROJECT FILE, undimensioned, not used for any dimension in this manual (source: 8_Utils/0044.jpg; as found)](8_Utils/0044.jpg)

## 3. Subsystems as evidenced by the CAD

The system consists of four PCB types, an antenna, a pedestal and off-board modules. Board sizes and layer counts come from the EAGLE board files; part counts from the schematics (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §1, Mermaid diagram node labels; `engineering/DESIGN/00_DESIGN_BASIS.md` §1, rows "PA board", "Other boards"):

| Subsystem | Size / layers | Key parts (reference designators) | CAD status | Chapter |
|---|---|---|---|---|
| Power Supply Board | 280 × 300 mm, 2 layers, 8 holes | X1 AK300/2 VIN 12–17 V; 21 × TPS562208, 6 × ADM7151, 2 × TPS7A8300, 5 × LM2662; 34 rail outputs X2..X35; enable bus SV1 | layout unfinished in the source (308 unconnected before BETA, 89 after) | 5 |
| Frequency Synthesizer Board | 100 × 100 mm, 6 layers, 4 holes | X4 OCXO 100 MHz, X5/X6 VCXO 50 MHz (schematic values; K7); IC1 AD9523; U1 ADF4382 TX LO; U6 ADF4382 RX LO | complete; only board with a designer P&P/BOM export | 6 |
| Main Board | 260 × 300 mm, 10 layers, 10 holes | U2 STM32F746ZGT7; U42 XC7A50T-2FTG256I (K1); U1 AD9484 8-bit 400 MSPS; U3 AD9708 8-bit DAC; U5/U13 LTC5552 mixers; 4 × ADAR1000; 16 × ADTR1107; 17 × M3SWA2-34DR+; U6 FT601 (0 of 77 pins connected, K3); X53 mini-USB | layout unfinished in the source (15 unconnected before BETA, 0 after) | 4 |
| RF PA board (×16, AERIS-10X only) | 35 × 60 mm, 4 layers, 7 × Ø3.2 holes | U$1 QPA2962 GaN 10 W; J1 RFIN / J2 RFOUT; X2 VG; X3 VD/VIN_M sense; `22V` AK300/2 terminal | complete (1 clearance DRC item in the source) | 7 |
| Antenna array | — | 8×16 patch (Nexus) or 32×16 slotted waveguide (Extended) per README | NO CAD (K8); PROPOSED panel exists | 8 |
| Off-board modules | — | GPS (UART5), GY-85 IMU + BMP180 (I2C3), 8 × TMP37 via ADS7830, stepper driver (PD4/PD5), fan relay (PD7), PA drain switch (PD6) | named only; no part numbers, no module schematics | 3, 9 |
| Host PC | — | Python GUI; USB 2.0 full-speed CDC on X53 is the only host data link in the CAD | GUI_V5 (hardware) / GUI_V6_Demo (offline) in the source; `beta/gui` package | 13 |

The README's description of the processing pipeline (waveform generation in the DAC, up/down conversion in the LT5552 mixers, beam steering by the ADAR1000s, FPGA processing of ADC capture → I/Q down-conversion → CIC/FIR decimation → pulse compression → Doppler FFT → MTI/CFAR, STM32 system management, Python visualisation) is the design intent (source: `README.md`, "Processing Pipeline"). Chapter 2 states what the RTL as committed and the BETA RTL actually implement; the differences are material (no MTI, fixed-threshold "CFAR" placeholder, no wired FPGA→host path).

## 4. Documented versus verified: conflicts K1–K8

Independent cross-reading of the CAD, the firmware, the RTL, the GUI and the documentation produced eight configuration conflicts that only the hardware owner can close (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §4, copied verbatim):

| # | Topic | A | B | Owner |
|---|---|---|---|---|
| K1 | FPGA part | CAD/xlsx/drawio XC7A50T-2FTG256I | README/docs/XDC XC7A100T | hardware designer |
| K2 | STM32 HSE | schematic 8 MHz crystal | firmware 25 MHz | hardware designer |
| K3 | Host data path | CAD: STM32 USB-FS only | RTL/GUI V6: FT601 USB 3.0; GUI V2–V5: FT2232H | system architect |
| K4 | PA supply | xlsx 16 × 22 V / 2 A | Power Board `Vin [12-17] V`, no 22 V rail | power designer |
| K5 | FPGA packet format | RTL `0xAA … 0x55` | GUI `A5C3 … CRC16` | software |
| K6 | ADF4382 pins | `main.h` PG6..PG15 (= schematic) | `adf4382a_manager.h` PG0..PG9 | firmware |
| K7 | Synth oscillators | schematic OCXO 100 MHz + 2 × VCXO 50 MHz | xlsx VCXO 100 MHz; firmware `vcxo_freq = 100 MHz` | RF designer |
| K8 | Antenna | README patch 8×16 / slotted 32×16 | two different waveguide simulations, no CAD | antenna designer |

The BETA work adopted interim assumptions for several of them without closing them: the BETA FPGA project targets `xc7a50tftg256-2`, the schematic part (K1); the BETA firmware clock tree is written for the real 8 MHz crystal (K2); the host path is implemented as option B (SPI bridge through the STM32 CDC) with option A (FT601 on a Main Board rev. B) prepared as a pin plan (K3); a 22 V supply module DSN-PSU-01 is proposed (K4); the bridge frame replaces both packet formats (K5); the ADF4382 pin collision is fixed in the BETA firmware (K6); K7 and K8 remain open, the antenna being a PROPOSED patch panel per decision D-01 (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4, §7, §8, §12; `beta/fpga/README.md`, "Remaining work" item 2). The full register with these interim positions is in chapter 17.

## 5. Performance targets versus calculated performance

The README targets (3 km Nexus, 20 km Extended) are not accompanied by a link budget in the upstream repository; the parameter table lists antenna gain, LNA noise figure and chirp bandwidth as TBD (source: `00_notation/parameter_table.md`, "TBD Tracking"). The BETA phase produced a single-pulse coherent range-equation estimate for the long chirp, using the simulated gain of the proposed antenna panel and an **assumed** bandwidth (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, both tables copied verbatim):

| Parameter | Value | Basis |
|---|---|---|
| f₀ / λ | 10.5 GHz / 28.57 mm | verified |
| TX power | 16 × 10 W (PSAT) = 160 W peak, coherent | QPA2962 datasheet; array coherence assumed |
| Antenna gain (TX = RX) | 22.6 dBi | one simulated row 11.5 dBi + 10·log10(16) − 1 dB feed/scan loss (proposed panel, D-01) |
| Chirp | T_c = 30 µs, **B = 50 MHz ASSUMED** (TBD in `parameter_table.md`) → pulse-compression gain 31.8 dB, ΔR = 3 m | firmware timing |
| Coherent integration | 16 long chirps → +12.0 dB | main.cpp |
| Noise figure / system losses | 4.0 dB / 6 dB | ADTR1107 2.5 dB NF + chain; losses assumed |
| Required SNR | 13 dB (Pd ≈ 0.9, Pfa 1e-6, Swerling 1) | standard |
| Unambiguous range (PRI 167 µs) | 25.1 km | firmware |

| Target RCS (m²) | R_max (km) |
|---|---|
| 0.01 | 1.9 |
| 0.1 | 3.4 |
| 1.0 | 6.0 |
| 10.0 | 10.6 |

The source's verdict (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, "Verdict"): with the proposed antenna, 16 × 10 W and 16-chirp integration, R_max(1 m²) ≈ 6.0 km — the 20 km Extended-variant goal is **not** reached and needs ≈ 21 dB more (longer coherent integration across the 31 elevations/azimuth dwell, a narrower B with the same T_c, lower losses, or a higher-gain antenna). The 3 km Nexus goal is met for RCS ≥ 0.1 m² (R ≈ 3.4 km); a 0.01 m² drone-class target falls near 1.9 km. Dominant unknowns: B (assumed), real array gain (16-row coupling not yet simulated), RF chain losses.

Two caveats apply to reading this estimate. First, it combines the Extended variant's PA power (16 × 10 W) with the proposed patch panel's simulated gain, i.e. neither variant of the README exactly; the Nexus variant with ~1 W per element would be 10 dB lower in transmit power, which the source does not evaluate. Second, nothing in the estimate has been measured: the gain comes from an openEMS simulation of one row (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §8) and the noise figure and losses are assumptions stated in the table.

## 6. Reconstruction state at a glance

The project is being rebuilt in three layers that this manual keeps separate: the upstream originals (ORIGINAL PROJECT FILE), the SOURCE-DERIVED engineering package generated from them (`engineering/`, 89 registered drawings, file check 333 OK, 0 problems; source: `engineering/DRAWING_REGISTER.md`, "Summary" and "File check"), and the PROPOSED / BETA additions (`engineering/DESIGN/`, `beta/`). Recovery tasks are tracked in `docs/04_RECOVERY_TASKS.md` (status summary at its 2026-10-08 date: 7 DONE, 20 OPEN, 9 BLOCKED, plus the R-ENG, R-DSN and R-BETA groups added 2026-10-09; source: `docs/04_RECOVERY_TASKS.md`, "Status summary" and the three added sections). Acceptance criteria and their current MET / NOT MET / NOT RUN state are in `docs/TESTING/ACCEPTANCE_CRITERIA.md`; the physical criteria (AC-F9, AC-S6, AC-S7, AC-B7, AC-E7) are all NOT RUN (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`, sections A–G).


---

<!-- chapter 2: Waveform/timing, beamforming, signal processing chain, data path -->
# Theory of operation — waveform, pulse compression, Doppler, beamforming, processing chain

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** equations ORIGINAL PROJECT FILE (the upstream physics notes `01_physics/*.md`, transcribed to plain text; equation tags kept); firmware timing constants SOURCE-DERIVED (`main.cpp`); frequency plan SOURCE-DERIVED (firmware-programmed values, not measurements); FPGA processing chain as committed PARTIAL (SD-02: missing modules, placeholders) and as implemented in `beta/fpga` BETA (simulated, not synthesised); figures F2.1 SOURCE-DERIVED, F2.2 and F2.3 PARTIAL. The chirp bandwidth B is TBD in the parameter table; the matched-filter reference memories encode a 10→30 MHz baseband sweep whose relation to B is not established.

**Sources:** `01_physics/01_fmcw_theory.md`, `01_physics/02_lfm_waveform_model.md`, `01_physics/03_beamforming_theory.md`, `01_physics/04_detection_theory.md`, `01_physics/05_noise_analysis.md`, `01_physics/06_calibration_theory.md`, `02_hardware/04_antenna_beamforming.md`, `00_notation/parameter_table.md`, `engineering/SYSTEM/data_flow/signal_and_data_flow.dot`, `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot`, `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot`, `engineering/SYSTEM/interfaces/interconnection_table.md` §6, `beta/fpga/README.md`, `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §2.

**Planned figures:** F2.1 signal and data flow (SYS-03), F2.2 FPGA pipeline as written in the original RTL (SD-02), F2.3 end-to-end data flow (SD-07).

Notation: equations are written in plain text because the manual build has no LaTeX renderer; symbols follow `00_notation/symbol_table.md` (Appendix D), equation tags follow `00_notation/conventions.md` §1 and refer to the display equation of that tag in the cited file. `x^2` is a power, `sqrt()` a square root, `*` complex conjugation when written as `s*(t)`, `·` multiplication.

## 1. Waveform model

### 1.1 LFM chirp

The transmitted pulse is a linear-frequency-modulated chirp of duration T_c and bandwidth B. In complex baseband (source: `01_physics/02_lfm_waveform_model.md` §1, Eq. LFM-1, LFM-3, LFM-4):

- `s(t) = rect(t / T_c) · exp( j·2π·( f_c·t + (μ/2)·t^2 ) )` (LFM-1)
- chirp rate `μ = B / T_c` (LFM-3)
- instantaneous frequency `f_i(t) = f_c + μ·t` (LFM-4)

The time-bandwidth product `TBP = B · T_c` (LFM-5) equals the pulse-compression gain (section 2) and the ratio of the two chirp modes' TBPs is `T_c,1 / T_c,2` (LFM-7) (source: `01_physics/02_lfm_waveform_model.md` §2).

### 1.2 Timing coded in the firmware

The firmware defines the following constants (source: `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp:178-184,190,195`; symbols per `00_notation/parameter_table.md`, "Waveform and Timing", copied):

| Parameter | Symbol | Value | Firmware variable | Source line |
|---|---|---|---|---|
| Chirps per beam position | M | 32 | `m_max` | `main.cpp:178` |
| Elevation positions | N_el | 31 | `n_max` | `main.cpp:179` |
| Long chirp duration | T_c,1 | 30 µs | `T1` | `main.cpp:180` |
| Long chirp PRI | T_r,1 | 167 µs | `PRI1` | `main.cpp:181` |
| Short chirp duration | T_c,2 | 0.5 µs | `T2` | `main.cpp:182` |
| Short chirp PRI | T_r,2 | 175 µs | `PRI2` | `main.cpp:183` |
| Guard time | T_guard | 175.4 µs | `Guard` | `main.cpp:184` |
| Azimuth positions per revolution | N_az | 50 | `y_max` | `main.cpp:189` |
| IF frequency | f_IF | 120 MHz | `IF_freq` | `main.cpp:190` |
| Stepper steps per revolution | — | 200 | `Stepper_steps` | `main.cpp:195` |
| Centre frequency / wavelength | f_c / λ | 10.5 GHz / 0.02857 m | `wavelength` | `main.cpp:1133` |
| Chirp bandwidth | B | **TBD** | — | `00_notation/parameter_table.md`, "TBD Tracking" |

The firmware comment at `main.cpp:186` states the per-position sequence: "m = N° of chirp/position = 16 (made of T1 and PRF1) + Guard = 175µs + 16 (made of T2 and PRF2)", i.e. 16 long chirps, a guard interval, then 16 short chirps per beam position. The resulting beam-position frame time is 5647.4 µs (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §2, row "Beam-position frame time", basis `main.cpp:180-186`). The parameter table resolves the apparent PRF discrepancy between firmware and GUI: `PRI1 = 167 µs` is the chirp-level PRI (f_r,1 ≈ 5988 Hz), whereas the GUI variables `prf1 = 1000 Hz` / `prf2 = 2000 Hz` are display rates, not chirp PRFs (source: `00_notation/parameter_table.md`, "Inconsistency Resolutions" §2).

### 1.3 Range, resolution and unambiguous range

With round-trip delay `τ = 2R / c` (FMCW-2) the dechirped beat frequency of a stationary target is `f_b = 2·μ·R / c` (FMCW-17), giving `R = c · f_b / (2μ)` (FMCW-18). Two targets are resolvable when their beat frequencies differ by at least 1/T_c, which yields the range resolution (source: `01_physics/01_fmcw_theory.md` §5–6, Eq. FMCW-19):

- `ΔR = c / (2B)` (FMCW-19) — depends only on B; numerical value not computable while B is TBD (the source says so explicitly).

The maximum unambiguous range follows from the PRI (source: `01_physics/01_fmcw_theory.md` §8, Eq. FMCW-22):

- `R_max = c · T_r / 2 = c / (2 f_r)` (FMCW-22) → 25.1 km for T_r,1 = 167 µs (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, row "Unambiguous range").

The radar range equation used for the performance estimate of chapter 1 §5 is (source: `01_physics/01_fmcw_theory.md` §2, Eq. FMCW-11):

- `SNR = P_t · G^2 · λ^2 · σ / ( (4π)^3 · R^4 · k_B · T_0 · B_n · F · L )` (FMCW-11)

### 1.4 Doppler

For a radial velocity v (approaching positive) the Doppler shift is `f_d = 2v / λ = 2 v f_c / c` (FMCW-4); the full beat frequency with Doppler coupling is `f_b = 2μR_0/c ± f_d` (FMCW-16). Velocity and velocity resolution over M pulses are `v = λ f_d / 2` (FMCW-20) and `Δv = λ / (2 M T_r)` (FMCW-21); the unambiguous velocity is `v_max = λ f_r / 4` (FMCW-23) and the range–velocity trade-off `R_max · v_max = c λ / 8` (FMCW-24) (source: `01_physics/01_fmcw_theory.md` §1, §4, §7, §8).

Range–Doppler coupling of an LFM pulse displaces the apparent range by `ΔR_Doppler = c f_d / (2μ) = v c T_c / (λ B)` (FMCW-27); the coupling ratio of the long to the short chirp equals `T_c,1 / T_c,2` (FMCW-28), i.e. 60 for the firmware values, and range migration across a CPI is `ΔR_migration = v · M · T_r` (FMCW-30) (source: `01_physics/01_fmcw_theory.md` §9). This is the stated reason for the two chirp modes: the long chirp gives processing gain and finer Doppler resolution, the short chirp smaller coupling and wider unambiguous range (source: `01_physics/02_lfm_waveform_model.md` §7, "Design Tradeoffs").

## 2. Pulse compression

### 2.1 Matched filter

The matched filter for s(t) is `h(t) = s*(−t)` (LFM-8), or in the frequency domain `H(f) = S*(f)` (LFM-9). It maximises the output SNR to `2E / N_0` (LFM-10) and provides the processing gain `G_p = B · T_c` (LFM-14); the matched-filter output SNR is the range-equation SNR multiplied by B·T_c (LFM-15). The compressed pulse width is `τ_c = 1 / B` (LFM-16), so the compression ratio is `T_c / τ_c = B T_c` (LFM-17) and the range resolution is again `ΔR = c τ_c / 2 = c / (2B)` (LFM-18). The compressed envelope is approximately `|y(τ)| ≈ T_c · |sinc(B τ)|` (LFM-20) with a first sidelobe of −13.3 dB for rectangular weighting (LFM-21); windowing trades mainlobe width for sidelobe level (source: `01_physics/02_lfm_waveform_model.md` §3–5).

The LFM ambiguity function `|χ(τ, ν)| = (1 − |τ|/T_c) · |sinc( (ν + μτ)(T_c − |τ|) )|` for |τ| ≤ T_c (LFM-23) has its ridge on `ν = −μτ` (LFM-24); the zero-delay Doppler cut gives the single-pulse Doppler resolution `Δf_d,pulse = 1 / T_c` (LFM-27) and `Δv_pulse = λ / (2 T_c)` (LFM-28) (source: `01_physics/02_lfm_waveform_model.md` §6). With B = 50 MHz **ASSUMED** and T_c = 30 µs the pulse-compression gain is 31.8 dB and ΔR = 3 m (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3, row "Chirp"); these two numbers are estimates until B is known.

### 2.2 What the repository data encodes — the `.mem` finding

The RTL loads its matched-filter reference from memory files `long_chirp_seg{0,1,2}_{i,q}.mem` and `short_chirp_{i,q}.mem`. The BETA analysis established that the long-chirp files are **conjugate FFT-domain** coefficients, not time-domain samples: `long_chirp_seg{0,1,2}_{i,q}.mem = conj(FFT_1024(u_s)) · 31128 / max|.|`, where u is a unit-amplitude 10 → 30 MHz linear up-chirp of 3000 samples at 100 MSPS, split into 1024-sample segments (phase-fit residual 0.0018 rad; regenerated to within 1 LSB by `beta/fpga/gen_chirp_mem.py`). Segment 3 lies beyond the chirp and is all zeros — that is the file that was missing from the upstream repository and was generated (source: `beta/fpga/README.md`, "What was found and decided", item 1; `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §3.2).

Consequences recorded in the same source:

- the matched filter is a frequency-domain chain (FFT → multiply by the stored reference → IFFT), as the orphan wrappers `fft_1024_forward/inverse_enhanced` and `frequency_matched_filter` of the original RTL imply; a time-domain FIR would not have used the repository data;
- the stored reference is already conjugated, so the chain must **not** conjugate again (`CONJUGATE_REF = 0` in the BETA RTL); with the extra conjugation neither the numpy model nor the RTL produces a compression peak;
- the same data equals the plain FFT of a 30 → 10 MHz down-chirp, so the actual baseband chirp direction after the RF/IF chain decides whether `CONJUGATE_REF` must be 0 or 1 — an open point for the designer (UNRESOLVED, hardware bring-up item);
- `short_chirp_{i,q}.mem` (50 words) matches neither a time- nor a frequency-domain chirp and cannot be used; the short-chirp processing path is UNRESOLVED.

The 10 → 30 MHz sweep of the reference data is a 20 MHz span at baseband. No repository file states whether this equals the RF chirp bandwidth B (TBD in `00_notation/parameter_table.md`; 50 MHz ASSUMED in `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3); the discrepancy is logged as observation MAN-02 in chapter 17.

### 2.3 Detection

The detection notes derive the cell-averaging CFAR threshold multiplier `α = N_ref · ( P_fa^(−1/N_ref) − 1 )` (DET-20) with `P_fa = (1 + α/N_ref)^(−N_ref)` (DET-19), the Swerling I detection probability `P_d = P_fa^(1/(1 + SNR_mean))` (DET-22) and the CFAR loss `L_CFAR ≈ (1/N_ref) · P_d / ((1 − P_d)·ln P_fa)` (DET-24) (source: `01_physics/04_detection_theory.md` §6–8). The RTL as committed does not implement this: the "CFAR" stage is a fixed threshold `|I| + |Q| > 10000` on the Doppler output, marked PLACEHOLDER by the original source comment at `radar_system_top.v:298-299` (source: `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot`, node "CFAR"; `beta/fpga/README.md`, "Remaining work" item 7: the detector is still a fixed threshold, default 10000 via `CFAR_THRESHOLD_DEFAULT`, writable over the bridge as `CFAR_THR` in the BETA).

### 2.4 Noise

The receive-chain noise figure follows Friis' formula `F_sys = F_LNA + (F_mix − 1)/G_LNA + (F_IF − 1)/(G_LNA G_mix) + (F_ADC − 1)/(G_LNA G_mix G_IF)` (NF-8); ADC quantisation adds `SQNR = 6.02 b + 1.76 dB` (NF-11) for b = 8 bits; the CIC decimator has DC gain `G_CIC = D_CIC^N_CIC` (NF-14) and bit growth `b_out = b_in + N_CIC · ceil(log2 D_CIC)` (NF-15) (source: `01_physics/05_noise_analysis.md` §3–6). The numerical budget is "pending parameter resolution" in the source (§7.3): LNA noise figures and the Extended-variant chain are TBD (source: `00_notation/parameter_table.md`, "TBD Tracking").

## 3. Beamforming

### 3.1 Array factor and steering

For a uniform linear array of N elements at spacing d, the inter-element propagation phase is `Δφ_prop = k d sinθ` with `k = 2π/λ` (BF-1); the electrical angle is `ψ = k d sinθ + Δφ` (BF-2) and the array factor `AF(θ) = Σ_{n=0}^{N−1} w_n · exp(j n ψ)` (BF-3). Steering to θ_0 requires `Δφ = −k d sinθ_0` (BF-4). With uniform weights `|AF(θ)| = |sin(Nψ/2) / sin(ψ/2)|` (BF-8), the half-power beamwidth is `θ_3dB ≈ 0.886 λ / (N d)` (BF-10), broadening by `1/cosθ_0` when scanned (BF-11). Grating lobes appear at `sinθ_GL = sinθ_0 + m λ / d` (BF-14); with d = λ/2 they never enter visible space for any scan angle, and for a limited scan |θ_0| ≤ θ_max the spacing may be relaxed to `d/λ < 1 / (1 + sinθ_max)` (BF-16) (source: `01_physics/03_beamforming_theory.md` §1–6). The 2-D extension factorises into the product of two 1-D array factors (BF-19) (source: same, §9).

AERIS-10 values: N = 16, d = λ/2 ≈ 14.3 mm (`element_spacing = wavelength / 2.0f`, `main.cpp:1134`), four ADAR1000 beamformers of four channels each, 31 elevation positions, azimuth by mechanical rotation (source: `00_notation/parameter_table.md`, "Antenna and Beamforming"; `02_hardware/04_antenna_beamforming.md` §1). The 8×16 patch description of the README is interpreted in the proposed antenna as 16 rows of 8 series-fed patches, each row being one "element" of the elevation-scanned array (decision D-02, source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2); that interpretation is a PROPOSED DESIGN choice, not a verified fact about the prototype.

### 3.2 Phase table and steering angles

The firmware holds 31 inter-element phase differences Δφ_n (`phase_differences[31]` in `main.cpp`) (source: `02_hardware/04_antenna_beamforming.md` §3.1, copied verbatim):

| Index | Δφ_n (deg) | Index | Δφ_n (deg) | Index | Δφ_n (deg) |
|---|---|---|---|---|---|
| 0 | +160.000 | 11 | +13.333 | 22 | -17.778 |
| 1 | +80.000 | 12 | +12.308 | 23 | -20.000 |
| 2 | +53.333 | 13 | +11.429 | 24 | -22.857 |
| 3 | +40.000 | 14 | +10.667 | 25 | -26.667 |
| 4 | +32.000 | 15 | 0.000 | 26 | -32.000 |
| 5 | +26.667 | 16 | -10.667 | 27 | -40.000 |
| 6 | +22.857 | 17 | -11.429 | 28 | -53.333 |
| 7 | +20.000 | 18 | -12.308 | 29 | -80.000 |
| 8 | +17.778 | 19 | -13.333 | 30 | -160.000 |
| 9 | +16.000 | 20 | -14.545 | | |
| 10 | +14.545 | 21 | -16.000 | | |

Position 15 is broadside; the table is symmetric. The per-element phase is `φ_n = n · Δφ_pos` (HW-ANT-4), quantised to the 7-bit ADAR1000 register `reg_n = floor( (φ_n mod 360°)/360° · 128 ) mod 128` (HW-ANT-5) with a phase step of `360°/128 = 2.8125°` (HW-ANT-1, CAL-6) and a maximum quantisation error of 1.40625° (CAL-7) (source: `02_hardware/04_antenna_beamforming.md` §2.4, §3.3–3.4; `01_physics/06_calibration_theory.md` §4). The steering angle for d = λ/2 is `θ_0 = arcsin( Δφ_n / 180° )` (HW-ANT-3) (source: `02_hardware/04_antenna_beamforming.md` §3.2).

The project's documents disagree on the resulting scan range: `02_hardware/04_antenna_beamforming.md` §3.2 evaluates HW-ANT-3 at |Δφ_n| = 160° to |θ_0| ≈ ±62.7° and then calls ≈ ±33° the "safe scan range" before grating lobes, while `01_physics/03_beamforming_theory.md` §6 shows that d = λ/2 is grating-lobe-free at every scan angle, and `00_notation/parameter_table.md` ("Inconsistency Resolutions" §4) states ≈ ±33° at Δφ = ±160° from the same formula. The README states ±45°. This manual does not resolve the disagreement; it is recorded as MAN-01 in chapter 17 for the antenna designer. The BETA firmware filled the ADAR1000 vector-modulator tables from datasheet Tables 10–13 (128 rows, ≤ 3.1° encoding error) and fixed a channel-index defect that "rotated the beam by one element" (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4).

### 3.3 Calibration and errors

Per-element amplitude and phase errors `h_n = (a_n + δa_n) · exp(j δφ_n)` (CAL-1) raise the RMS sidelobe level to `σ_a^2 + σ_φ^2` (CAL-5); mutual coupling is modelled as `v_actual = C · w` (CAL-11) and pre-compensated by `w_applied = C^(−1) · w_desired` (CAL-12). The calibration procedure (measure each element against a reference, compute `c_n = a_n / (h_n,meas / S_ref)` (CAL-14), apply, verify) leaves a residual phase error bounded by half a quantisation step (CAL-15) (source: `01_physics/06_calibration_theory.md` §1–8). No calibration has been performed; per-board phase calibration is listed as open in the BETA report (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4, "Open").

### 3.4 Beam sequence

During each azimuth position the firmware loads the 15 positive-steering patterns (`matrix1`), broadside (`vector_0`) and the 15 negative patterns (`matrix2`) into all four ADAR1000s (TX and RX) and, for each, executes M/2 long chirps at T_r,1, the guard time, then M/2 short chirps at T_r,2 (source: `02_hardware/04_antenna_beamforming.md` §3.5–3.6). The STM32 signals each new chirp, elevation and azimuth to the FPGA by toggling `DIG_0..2` (PD8..PD10) and enables the mixers with `DIG_3` (PD11); the bit-to-port mapping is inferred from source comments and rated MEDIUM confidence (source: `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot`, edge "handshake DIG_0..4"; `docs/SYSTEM/BLOCK_DIAGRAM.md` §3).

## 4. Frequency plan and signal flow

![Figure 5 — F2.1 — Signal and data flow SYS-03: reference and clock tree, TX chain, RX chain, control paths; solid = confirmed, dashed = unverified, dotted red = missing specification — SOURCE-DERIVED; frequencies are firmware-programmed values, not measurements (source: engineering/SYSTEM/data_flow/signal_and_data_flow.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SYSTEM/data_flow/signal_and_data_flow.png)

The frequencies below are the values programmed by the firmware, traced through the schematics; none has been measured (source: `engineering/SYSTEM/data_flow/signal_and_data_flow.dot`, node labels; `engineering/SYSTEM/interfaces/interconnection_table.md` §6):

| Signal | Value (firmware intent) | Path | Evidence |
|---|---|---|---|
| Reference | REFB 100 MHz selected (X5 net `100MHZ_OUT`); VCXO X6 on `OSC_IN`, `vcxo_freq = 100 MHz` | Synth IC1 AD9523: PLL1 (REFB, R = 1) → VCXO; PLL2 PFD 100 MHz, N = 36 → VCO 3.6 GHz | `main.cpp:933-946, 1070`; K7: schematic part values are 50 MHz VCXO / 100 MHz OCXO |
| ADF4382 reference | 300 MHz LVDS (OUT0/OUT1) | IC1 → C11/C12, C68/C69, R1/R12 → U1/U6 REFP/N | synth schematic; `adf4382a_manager.h:32-34` |
| TX LO | 10.5 GHz (`TX_FREQ_HZ`) | U1 ADF4382 RFOUT1 → MTX2-143+ → ATS1005 −3 dB → J10 "LO TX" → coax → Main J23 → C272 → U5 LTC5552 LO | `adf4382a_manager.h:32-34`; interconnection §6, CBL-36 |
| RX LO | 10.38 GHz (`RX_FREQ_HZ`) = 10.5 GHz − 120 MHz | U6 ADF4382 RFOUT1 → U7 → U8 → J11 "LO RX" → Main J22 → C274 → U13 LTC5552 LO | same; CBL-37 |
| ADC sample clock | 400 MHz LVDS (OUT4) | J3 → J21 twinax → U1 AD9484 CLK± | `main.cpp:983-984`; CBL-34 |
| FPGA ADC clock | 400 MHz LVDS (OUT5) | J4 → J19 → U42 bank 14 MRCC | not used by the RTL; CBL-35 |
| FPGA system clock | 100 MHz LVCMOS (OUT6) | J7 → J1 → U42 `IO_L13P_T2_MRCC_15` = `clk_100m` | `main.cpp:1004`; CBL-30 |
| DAC clock | 120 MHz LVCMOS (OUT10) | J5 → J20 → U3 AD9708 CLOCK | `main.cpp:1025-1026`; CBL-31 |
| FPGA DAC clock | 120 MHz LVCMOS (OUT11) | J6 → J18 → U42 = `clk_120m_dac` | CBL-32 |
| Test clock | 20 MHz (OUT7) | J8 → JP20 `FPGA_CLOCK_TEST` | CBL-33 (adapter UNVERIFIED) |
| IF | 120 MHz | TX: DAC → LC network → U5 IF±; RX: U13 IF± → LC → 2 × AD8352 → AD9484 | `main.cpp:190`; `ddc_400m.v:48` |

TX chain (source: SYS-03 node labels): the FPGA chirp controller (`plfm_chirp_controller`, LUT-based) drives the 8-bit AD9708 DAC at 120 MHz; the differential LC network (C127 32.8 pF, L22/L25 107.3 nH, C141, L26/L27 107.3 nH, C59 32.8 pF) feeds the IF port of the LTC5552 up-converter U5; the RF output passes band-pass filter U$2 "BPF2" (part number NOT IDENTIFIED; sideband selection UNVERIFIED), the SPDT switch U$1 M3SWA2-34DR+, the 4-way combiner/divider U16 EP4RKU+, the four ADAR1000s (TX1..TX4 → ADTR TX_IN), the sixteen ADTR1107 T/R front ends and sixteen M3SWA2-34DR+ element switches to SMA pairs J24..J55, from which the Extended variant goes through one QPA2962 PA board per element to the antenna, and the Nexus variant goes directly to the antenna. RX chain: the echo returns through the same element switch and ADTR1107 LNA path (RX_OUT → ADAR RXn), the combiner, U$1 to the LTC5552 down-converter U13 (LO 10.38 GHz → IF 120 MHz, "consistent with IF_freq"), the IF LC network, two cascaded AD8352 amplifiers U8/U4 (enable pins `EN_OPAMP_IF_1/2` floating) and the AD9484 ADC (VIN± via R13/R1 24 Ω, C3 2.7 pF), whose LVDS D0..7 + DCO go to FPGA bank 14 (source: `engineering/SYSTEM/data_flow/signal_and_data_flow.dot`, nodes of the "transmit chain", "common port", "receive chain" clusters).

## 5. FPGA processing chain

### 5.1 As written in the original RTL (PARTIAL)

![Figure 6 — F2.2 — FPGA signal-processing pipeline as written in the original RTL (SD-02): blue = defined and instantiated, orange = documented defect or placeholder, red dashed = instantiated but missing from the repository, grey dotted = orphan — PARTIAL (source: engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.png)

The original receiver chain (`radar_receiver_final.v`, instantiation order at lines 61, 82, 94, 114, 129, 144, 173, 198, 226, 290) is, per stage (source: `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot`, node labels):

| Stage | Module (file:line) | Function and parameters | State in the original RTL |
|---|---|---|---|
| LVDS capture | `lvds_to_cmos_400m` (rrf:61), `ad9484_lvds_to_cmos_400m` (rrf:82) | IBUFDS → BUFG; 8-bit ADC bus + DCO at 400 MSPS | clock defect (`lvds_to_cmos_400m.v:35-43`: a flop re-sampling its own clock); capture module MISSING |
| CDC | `cdc_adc_to_processing #(8,3)` (rrf:94) | ADC DCO → clk_400m | present |
| DDC | `ddc_400m_enhanced` (rrf:114) with `nco_400m_enhanced` + `lfsr_dither_enhanced` (`ddc_400m.v:131-160`) | NCO IF 120 MHz at 400 MSPS, `PHASE_INC 32'h4CCCCCCD`; complex mixer; `cic_decimator_4x_enhanced` ×2 (decimate by 4, 5 stages); CDC to clk_100m; `fir_lowpass_parallel_enhanced` ×2; `baseband_i/q[17:0]` | connected with `mixers_enable = 1'b1`, `bypass_mode = 1'b1` (`:125-126`); 400 MHz fabric logic |
| Scaling | `ddc_input_interface` (rrf:129) | 18-bit → 16-bit `adc_i/q_scaled` | present |
| Reference | `chirp_memory_loader_param` (rrf:144) + `latency_buffer_2159 #(32, 3187)` (rrf:173) | `$readmemh` ×10 from absolute Windows paths; `long_chirp_seg3_i/q.mem` MISSING | path defect; one file missing |
| Matched filter | `matched_filter_multi_segment` (rrf:198) → `matched_filter_processing_chain` (`matched_filter_multi_segment.v:361`) | overlap-save 1024-point, 4 segments | control inputs `use_long_chirp`, `chirp_counter`, `mc_new_*` UNDRIVEN (rrf:21-25, 204-208) → filter never starts; processing chain MISSING; FFT wrappers orphaned, IP missing |
| Range decimation | `range_bin_decimator #(1024, 64, 16)` (rrf:226) | 1024 → 64 bins, peak mode | MISSING |
| Doppler | `doppler_processor_optimized #(32, 64, 32)` (rrf:290) → `xfft_32` (`doppler_processor.v:283`) | 64 range bins × 32 chirps frame → 32-point FFT | `xfft_32` MISSING (Xilinx IP, no `.xci`); frame-sync pulse never fires (chirp_counter undriven) |
| Detection | glue in `radar_system_top.v:298-323` | fixed threshold `abs(I) + abs(Q) > 10000` | PLACEHOLDER per source comment |
| Host | `usb_data_interface` (`radar_system_top.v:345-373`) | FT601 slave FIFO, packet `0xAA` header … `0x55` footer, FSM on `ft601_clk_in` | NO HARDWARE (FT601 U6 0 of 77 pins connected); inputs sampled across clock domains without synchroniser; `ft601_clk_out` two drivers |
| Transmitter | `radar_transmitter` (`radar_system_top.v:204-264`) | edge detectors on STM32 toggles; `plfm_chirp_controller_enhanced` (LUT chirp, beam/elevation/azimuth/chirp counters, RF switch, mixer enables, ADAR load/TR); `dac_interface_enhanced` at 120 MHz | `level_shifter_interface` not instantiated → STM32→ADAR1000 SPI pass-through outputs never driven |

The register `docs/SYSTEM/BLOCK_DIAGRAM.md` §3 summarises the same findings per interface (STM32→FPGA handshake inferred, SPI pass-through BROKEN in RTL, FPGA→host NO HARDWARE, ADC→FPGA capture not implemented and bank-voltage conflict).

### 5.2 As implemented in `beta/fpga` (BETA)

The BETA RTL keeps the architecture and repairs it so that it parses, lints and simulates with Icarus Verilog 13.0 and Verilator 5.052; it is **not synthesised**, has **no timing closure** and has **not been loaded on hardware**; the two Xilinx FFT IP cores are not generated (source: `beta/fpga/README.md`, "Status"). The functional changes relevant to the theory of operation (source: `beta/fpga/README.md`, "What was found and decided", "ADC capture and DDC front end", "Remaining work"; `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §3.2):

- **ADC capture** (`ADC_CAPTURE_MODE = 1`, default): the AD9484 output is SDR LVDS at the sample rate (datasheet facts: DCO at 400 MHz, data valid on the rising DCO edge, tSKEW ±0.07 ns). Capture uses IBUFDS(DCO) → BUFIO + BUFR/4, IDELAYE2 per lane with calibration (`adc_capture_calib`: default tap 16, manual tap/bitslip, automatic IDELAY sweep with the ADC test pattern, per-lane lock status, pattern error counter), ISERDESE2 SDR 1:4, and a 32-bit asynchronous FIFO into `clk_100m`. Mode 0 keeps the legacy 400 MHz fabric path for comparison.
- **DDC at 100 MHz** (`ddc_4x_100m`): 4-phase NCO, 8 mixers, CIC as a 16-tap FIR and the unchanged FIRs, all at 100 MHz; bit-exact with the legacy 400 MHz chain (`tb_ddc_4x`: 1855 outputs, max diff 0 LSB).
- **Matched filter**: frequency-domain chain with `CONJUGATE_REF = 0` (section 2.2); reference alignment by address instead of the fixed 3187-cycle latency buffer; `tb_matched_filter` peak at bin 302 for a 300-sample delay (±4), peak/sidelobe 4.76.
- **Clock-domain crossings**: Gray-pointer FIFOs, reset synchroniser per domain, STM32 toggles synchronised in the consuming domain.
- **Register map** (`radar_control_regs`): the previously floating control inputs have one driver with reset defaults; its write/read port is driven by the SPI bridge (command set v2, 5-bit word addresses 0x00..0x10, 16-bit registers; table in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §7).
- **Host path option B**: `rd_map_packer` turns each 64 × 32 Doppler frame into a 2066..2162-byte frame (header, 2048 × uint8 log-magnitude, up to 32 detections, CRC-16/CCITT-FALSE) and `host_bridge_spi` streams it to the STM32 as an SPI slave on the existing SPI1 nets with `DIG_5..7` as CS/DRDY/spare; the ADAR1000 pass-through is gated during transfers (section 6).

System-level evidence from `tb_system_smoke` (source: `beta/fpga/README.md`, "System smoke test evidence"): for alternating echo delays of 100 and 420 baseband samples the segment-0 peak sat at decimated bins 8 and 28 on every chirp — a 20-bin shift for a 320-sample delay change (320/16 = 20) — i.e. pulse compression works end to end through capture → DDC → matched filter → decimator in simulation; 2048 Doppler outputs (one 64 × 32 frame); 2688 USB packets with 0 header/footer/sequence errors.

Two architectural limitations remain and matter for interpreting the processing chain (source: `beta/fpga/README.md`, "Remaining work" items 4–5): (a) **throughput** — the matched-filter FSM is not pipelined against the sample collector; one long chirp (4 segments) occupies it for ~92 µs with the behavioural FFT latency and ~270 µs with a realistic IP latency, whereas the transmitter repeats long chirps every 167 µs, so samples arriving outside `ST_COLLECT_DATA` are dropped (original behaviour; the smoke test uses a 300 µs period for this reason); (b) **segment semantics** — each 1024-sample segment is compressed against its own reference segment and yields its own 64-bin profile; the four profiles per chirp are not summed, and the Doppler processor counts each profile as a "chirp", so a 32-"chirp" frame covers 8 real chirps. Whether to sum the partial correlations (true partitioned matched filter) or use a 4096-point transform is a design decision not yet taken.

## 6. Data path to the host

![Figure 7 — F2.3 — End-to-end signal and control data flow SD-07: antenna → RF → ADC → FPGA → host and host → STM32 → clock/LO/beamformer → FPGA; solid = confirmed by schematic net and firmware/RTL, dashed = unverified, dotted red = missing specification — PARTIAL; the FPGA→host path has no hardware (source: engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.png)

Key finding of SD-07 (source: `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot`, legend): the only wired host link is the STM32 USB-FS CDC on X53 (control, GPS and status); the FPGA radar-data output targets an FT601 that has no nets; no GUI version in the upstream repository can decode the RTL packet format (K5). Therefore no end-to-end radar data path exists in the repository as committed.

The data-rate budget that frames the BETA solution (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §2, copied verbatim):

| Quantity | Value | Basis |
|---|---|---|
| Range-Doppler cells per beam position | 64 × 32 = 2048 | `doppler_processor.v` (RANGE_BINS 64, 32 chirps) |
| Beam-position frame time | 5647.4 µs | `main.cpp:180-186` |
| Raw RTL packet stream (44 B per cell) | **16.0 MB/s** | `usb_data_interface.v` (11 × 32-bit words) |
| Compact map frame (8-bit log-magnitude per cell + header + ≤ 32 detections + CRC) | 2164 B → **383 kB/s** | this design, §5 |
| STM32 USB-FS CDC practical limit | ≈ 0.8–1.1 MB/s | USB 2.0 FS bulk (19 × 64 B per 1 ms frame max) |
| SPI1 STM32 ↔ FPGA (existing lines) | 27 Mbit/s ≈ 3.3 MB/s (DMA) | APB2 108 MHz / 4 (beta clock tree) |
| FT601 245 sync FIFO, 32 bit @ 100 MHz | up to 400 MB/s | FT601 |

The source concludes that the raw stream needs the FT601 (option A, Main Board rev. B, decision D-16) while the compact map fits the existing STM32 path with 3× margin (option B, implemented as BETA, decision D-17). The STM32 forwards each bridge frame unchanged over CDC, interleaved with its status strings, and the GUI stream parser resynchronises on the `0xA5 0x5A` sync word (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §5). Chapter 9 gives the frame layout and the command set; chapter 17 lists the decisions D-16…D-19.


---

<!-- chapter 3: Boards, modules, connectors, cables, power rails -->
# Architecture and interfaces — boards, connectors, cables, power rails

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** interconnection diagram and tables SOURCE-DERIVED (connector nets of the four EAGLE schematics, board silkscreen, `main.h`), with every row carrying CONFIRMED / UNVERIFIED / MISSING SPEC; power-rail register SOURCE-DERIVED (voltages from net names, currents UNKNOWN, firmware sequence as coded, not executed); harness schedule PROPOSED DESIGN (DSN-HAR-01, lengths computed from the proposed layout); cable IDs are proposals, not upstream data; figures F3.1 and F3.2 SOURCE-DERIVED.

**Sources:** `engineering/SYSTEM/interfaces/interconnection_table.md`, `engineering/SYSTEM/architecture/README.md`, `engineering/ELECTRICAL/power_distribution/power_rails.md`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, `docs/SYSTEM/BLOCK_DIAGRAM.md` §2–3.

**Planned figures:** F3.1 hardware interconnection diagram (SYS-02), F3.2 power distribution diagram (ELEC-PWR-01 / SYS-04).

## 1. Physical architecture

The radar electronics consist of a Power Supply Board (280 × 300 mm, 2 layers), a Frequency Synthesizer Board (100 × 100 mm, 6 layers), a Main Board (260 × 300 mm, 10 layers) and, for the Extended variant, sixteen RF PA boards (35 × 60 mm, 4 layers), interconnected by 2-pin and 3-pin Molex 22-23-20x1 power cables, one 20-way enable ribbon (SV1), two control ribbons (JP1↔JP1 2×6, JP13↔JP2 2×7), coaxial clock/LO links and 34 SMA RF ports (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §1; `engineering/SYSTEM/interfaces/interconnection_table.md`, lead-in). The antenna, the host PC, the 22 V PA drain supply and the off-board modules (GPS, IMU, barometer, temperature sensors, stepper driver, fan relay, drain switch) have no CAD in the repository and appear as CONCEPTUAL nodes (source: `engineering/SYSTEM/architecture/README.md`, row SYS-01).

![Figure 8 — F3.1 — Hardware interconnection diagram SYS-02: one node per board/module, one edge per connector/cable with connector IDs, pin numbers where the symbol has them, signal names and interface standard — SOURCE-DERIVED; cable types, lengths, Molex pin order, SMA RFIN/RFOUT side and PA-instance mapping are UNVERIFIED (source: engineering/SYSTEM/interfaces/hardware_interconnection.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SYSTEM/interfaces/hardware_interconnection.png)

How the diagram was obtained (source: `engineering/SYSTEM/architecture/README.md`, "What was verified against the schematics"): the four `.sch` files were parsed read-only with Python `xml.etree`; parts and `<pinref>` nets were tabulated; anonymous nets (`N$…`) were followed through two-pin passives until a named net or an IC pin was reached; the Synth and PA `.brd` files were parsed for silkscreen text nearest each connector (the Main Board `.brd` contains no free silkscreen text); MCU pins were read from `main.h`, the enable order and clock settings from `main.cpp`, `ADAR1000_Manager.cpp` and `adf4382a_manager.{h,c}`; `Power Management V6.xlsx` was unzipped and its sheet XML parsed.

Corrections to `docs/SYSTEM/BLOCK_DIAGRAM.md` established by SYS-02 (source: `engineering/SYSTEM/architecture/README.md`, same section, copied): (1) SV1 has 15 enable lines; (2) Synth power connectors X10..X15 = `+3V3_XO`, `+3V3_CLOCK`, `+1V8_CLOCK`, `+3V3_LO_1`, `+3V3_LO_2`, `+5V0_LO`; (3) the "17th SMA pair" J22/J23 are the RX-LO and TX-LO inputs of U13/U5 (18 pF coupled); (4) Synth LO SMAs: J10 = `LO TX` (U1 RFOUT1 path), J11 = `LO RX` (U6 RFOUT1 path), J1 = `AUX. LO TX`, J12 = second RX path; (5) `+5V0_ADAR`, `+5V0_ADTR`, `+3V3_SW` outputs (X13, X26, X29) and `+5V0_1..5` (X2, X9, X17, X25, X28) are intermediate rails with no off-board consumer; (6) the PA gate-bias cables are X_1..X_16 (VG_n), the 3-pin X3/X38..X52 carry the INA241 shunt-sense pair.

## 2. Inter-board interconnection tables

Conventions of the copied tables (source: `engineering/SYSTEM/interfaces/interconnection_table.md`, lead-in): pins are EAGLE pin names of the connector symbols; Molex 22-23-20x1 symbols name **all** pads `S`, so their pin order cannot be read from the schematic and is written `S` (UNVERIFIED order). Cable IDs `CBL-xx` are a proposal of that document, not from the original project. "Power requirement" is copied from `3_Power Management/Power Management V6.xlsx` (column G, mA, per device) only where the rail maps to a single row. Status: CONFIRMED = both ends found in the schematics with the same net meaning; UNVERIFIED = one end or the pin order cannot be established; MISSING SPEC = no cable/part/number exists in the repository. Evidence shorthand: `MB` = `RADAR_Main_Board.sch`, `PB` = `PowerBoard.sch`, `SY` = `Clocks_Freq_Synth_board.sch` (+ `.brd` silkscreen), `PA` = `RF_PA.sch`, `main.h` = `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.h`, `xlsx` = `Power Management V6.xlsx` sheet `Feuil1`.

### 2.1 DC input (source: `interconnection_table.md` §1)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| External DC source (not specified) | — | — | VIN 12–17 V | Power Board | X1 AK300/2 | KL (1) | DC power | UNKNOWN (sum not computed in xlsx) | CBL-00 | PB X1 nets `VIN`,`GND`; brd silk `Vin [12-17]V` | MISSING SPEC (source) |
| External DC source | — | — | GND | Power Board | X1 AK300/2 | KL (2) | DC power | — | CBL-00 | PB X1 | MISSING SPEC |

### 2.2 Power Board → Main Board rails, Molex 22-23-2021 → 22-23-2021, 2 wires each (source: `interconnection_table.md` §2)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement (xlsx) | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Power Board | X4 | S | `+1V0_FPGA` | Main Board | X8 | S | DC power 1.0 V | 30 mA (row 17, VCCINT/VCCBRAM) | CBL-01 | PB X4; MB X8 | CONFIRMED (pin order UNVERIFIED) |
| Power Board | X5 | S | `+1V8_FPGA` | Main Board | X10 | S | DC power 1.8 V | 50+22+100 mA (rows 14,16,26) | CBL-02 | PB X5; MB X10 | CONFIRMED |
| Power Board | X27 | S | `+3V3_FPGA` | Main Board | X16 | S | DC power 3.3 V | 20+200+20+230 mA (rows 15,18,20,27) | CBL-03 | PB X27; MB X16 | CONFIRMED |
| Power Board | X16 | S | `+3V3` | Main Board | X24 | S | DC power 3.3 V | 130+10+1+50+1 mA (rows 13,47-49,55) | CBL-04 | PB X16; MB X24 | CONFIRMED |
| Power Board | X12 | S | `+3V3_AN` | Main Board | X9 (X56 is on the same net) | S | DC power 3.3 V | 30+2×150+1+2+6+16×6 mA (rows 19,21,50,51,54,56) | CBL-05 | PB X12; MB X9, X56 | CONFIRMED (which of X9/X56 is used: UNVERIFIED) |
| Power Board | X10 | S | `+1V8_CLOCK` | Main Board | X17 | S | DC power 1.8 V | 300 mA (row 25, AD9484 AVDD) | CBL-06 | PB X10; MB X17 → L1 → `+1V8_CLOCK_F` | UNVERIFIED — PB X10 is the only `+1V8_CLOCK` output and is also required by Synth X12 (CBL-24) |
| Power Board | X14 | S | `+3V3_ADAR_12` | Main Board | X20 (`+3V3_ADAR12`) | S | DC power 3.3 V | 2×700 mA (row 30) | CBL-07 | PB X14; MB X20 | CONFIRMED (net names differ by one underscore) |
| Power Board | X15 | S | `+3V3_ADAR_34` | Main Board | X21 (`+3V3_ADAR34`) | S | DC power 3.3 V | 2×700 mA (row 30) | CBL-08 | PB X15; MB X21 | CONFIRMED (name differs) |
| Power Board | X21 | S | `-5V0_ADAR12` | Main Board | X13 | S | DC power −5 V | 2×60 mA (row 29) | CBL-09 | PB X21; MB X13 | CONFIRMED |
| Power Board | X20 | S | `-5V0_ADAR34` | Main Board | X15 | S | DC power −5 V | 2×60 mA (row 29) | CBL-10 | PB X20; MB X15 | CONFIRMED |
| Power Board | X34 | S | `+3V3_ADTR` | Main Board | X4 | S | DC power 3.3 V | 16×80 mA (row 35) | CBL-11 | PB X34; MB X4 | CONFIRMED |
| Power Board | X18 | S | `-3V3_SW` | Main Board | X6 | S | DC power −3.3 V | 16×0.12 mA (row 37) | CBL-12 | PB X18; MB X6 | CONFIRMED |
| Power Board | X30 | S | `+3V3_VDD_SW` | Main Board | X12 | S | DC power 3.3 V | 16×0.014 mA (row 38) | CBL-13 | PB X30; MB X12 | CONFIRMED |
| Power Board | X23 | S | `+3V4` | Main Board | X1 (X54 same net) | S | DC power 3.4 V | 17×2.9 mA (row 22) | CBL-14 | PB X23; MB X1, X54 | CONFIRMED (X1/X54 choice UNVERIFIED) |
| Power Board | X24 | S | `-3V4` | Main Board | X11 (X22 same net) | S | DC power −3.4 V | 17×1.8 mA (row 23) | CBL-15 | PB X24; MB X11, X22 | CONFIRMED (X11/X22 choice UNVERIFIED) |
| Power Board | X3 | S | `+5V5_PA` | Main Board | X55 | S | DC power 5.5 V | 2×50 mA (row 52) | CBL-16 | PB X3; MB X55 | CONFIRMED |
| Power Board | X19 | S | `-5V5_PA` | Main Board | X19 | S | DC power −5.5 V | 2×50 mA (row 53) | CBL-17 | PB X19; MB X19 | CONFIRMED |
| Power Board | X31 | S | `+5V0_PA_1` | Main Board | X14 | S | DC power 5 V | 5×250 mA (row 40; ADTR1107_1,2,3,4,7) | CBL-18 | PB X31; MB X14 | CONFIRMED |
| Power Board | X32 | S | `+5V0_PA_2` | Main Board | X5 | S | DC power 5 V | 5×250 mA (ADTR1107_5,6,8,10,12) | CBL-19 | PB X32; MB X5 | CONFIRMED |
| Power Board | X33 | S | `+5V0_PA_3` | Main Board | X7 | S | DC power 5 V | 6×250 mA (ADTR1107_9,11,13,14,15,16) | CBL-20 | PB X33; MB X7 | CONFIRMED |
| Power Board | X22 | S | `+5V0_0` | Main Board | X18 | S | DC power 5 V | 2×200 mA (row 24, AD8352) — also feeds PB U5 (+3V3_AN) on the Power Board | CBL-20a | PB X22; MB X18 | CONFIRMED |
| Power Board | X2, X9, X17, X25, X28 | S | `+5V0_1..+5V0_5` | — (no counterpart on Main or Synth) | — | — | DC power 5 V | — | — | PB X2,X9,X17,X25,X28; MB/SY: net absent | UNVERIFIED (spare or test outputs; rails are consumed on-board by U23/U25/U27/U29/U34) |
| Power Board | X13 | S | `+5V0_ADAR` | — (no counterpart) | — | — | DC power 5 V | — | — | PB X13; MB: net absent (ADAR AVDD is −5 V from X13/X15) | UNVERIFIED (consumed on-board by U20/U21) |
| Power Board | X26 | S | `+5V0_ADTR` | — (no counterpart) | — | — | DC power 5 V | — | — | PB X26; MB: net absent | UNVERIFIED (consumed on-board by U32) |
| Power Board | X29 | S | `+3V3_SW` | — (no counterpart) | — | — | DC power 3.3 V | — | — | PB X29; MB: net absent | UNVERIFIED (consumed on-board by U18) |

### 2.3 Main Board → Power Board enable bus, SV1 MA10-2 ↔ SV1 MA10-2, 20-way, cable CBL-21 (source: `power_rails.md` §2, identical pin map on both boards; all rows CONFIRMED in `interconnection_table.md` §3)

| SV1 pin | Net | STM32 pin (`main.h`) | Power Board EN input |
|---|---|---|---|
| 1 | `EN_+1V0_FPGA` | PE7 | U1 |
| 2 | `EN_+5V0_PA2` | PG1 | U15 |
| 3 | `EN_+1V8_FPGA` | PE8 | U2 |
| 4 | `EN_+5V0_PA3` | PG2 | U16 |
| 5 | `EN_+3V3_FPGA` | PE9 | U4 |
| 6 | `EN_+5V5_PA` | PG3 | U17 |
| 7 | `EN_+5V0_ADAR` | PE10 | U13 |
| 8 | `EN_+1V8_CLOCK` | PG4 | U25 |
| 9 | `EN_+3V3_ADAR12` | PE11 | U6 |
| 10 | `EN_+3V3_CLOCK` | PG5 | U23 |
| 11 | `EN_+3V3_ADAR34` | PE12 | U7 |
| 13 | `EN_+3V3_ADTR` | PE13 | U32 |
| 15 | `EN_+3V3_SW` | PE14 | U10 |
| 17 | `EN_+3V3_VDD_SW` | PE15 | U8 |
| 19 | `EN_+5V0_PA1` | PG0 | U14 |
| 12, 14, 16, 18, 20 | GND | — | — |

15 enable lines (not 16 as stated in `docs/SYSTEM/BLOCK_DIAGRAM.md`). All enables are driven as push-pull outputs initialised LOW in `MX_GPIO_Init` (`main.cpp:2239-2247`); the Power Board has no pull-downs/pull-ups on the EN nets visible in the netlist (not checked exhaustively — REQUIRES VERIFICATION) (source: `power_rails.md` §2).

### 2.4 Power Board → Frequency Synthesizer Board rails, Molex 22-23-2021, 2 wires each (source: `interconnection_table.md` §4; Synth-side nets are anonymous `N$69..N$77` and reach the named rail through a series inductor `SY L9..L13`)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement (xlsx) | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Power Board | X35 | S | `+3V3_XO` | Synth Board | X10 (`N$69` → L9 → `+3V3_XO`) | S | DC power 3.3 V | 1200+25+25 mA (rows 2,4,5) | CBL-22 | PB X35; SY X10, L9, X4/X5/X6 VDD | CONFIRMED |
| Power Board | X11 | S | `+3V3_CLOCK` | Synth Board | X11 (`N$71` → L10 → `+3V3_CLOCK`) | S | DC power 3.3 V | 250 mA (row 6) | CBL-23 | PB X11; SY X11, L10, IC1 VDD3_* | CONFIRMED |
| Power Board | X10 | S | `+1V8_CLOCK` | Synth Board | X12 (`N$73` → L11 → `+1V8_CLOCK`) | S | DC power 1.8 V | 250 mA (row 7) | CBL-24 | PB X10; SY X12, L11, IC1 VDD1.8_* | UNVERIFIED — same PB X10 also needed by Main X17 (CBL-06); a Y-cable or second output is not in CAD |
| Power Board | X8 | S | `+3V3_LO_1` | Synth Board | X13 (`N$75` → L12 → `+3V3_LO_1`) | S | DC power 3.3 V | 2×240 mA (row 11) | CBL-25 | PB X8; SY X13, L12, U1/U6 V3_LDO/LS/NDIV/PFD/REF/SYNC | CONFIRMED |
| Power Board | X7 | S | `+3V3_LO_2` | Synth Board | X14 (`N$77` → L13 → `+3V3_LO_2`) | S | DC power 3.3 V | 2×340 mA (row 12) | CBL-26 | PB X7; SY X14, L13, U1/U6 V3_OUTDIV/RFOUT/VCOB | CONFIRMED |
| Power Board | X6 | S | `+5V0_LO` | Synth Board | X15 (`+5V0_LO`) | S | DC power 5 V | 2×(200+0.3+70) mA (rows 8-10) | CBL-27 | PB X6; SY X15, FB1..FB4 | CONFIRMED |

### 2.5 Main Board ↔ Frequency Synthesizer Board control headers (source: `interconnection_table.md` §5)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board (U2 PF3) | JP1 PINHD-2X6 | 1 | `AD9523_PD` | Synth Board | JP1 PINHD-2X6 | 1 | 3.3 V CMOS GPIO | — | CBL-28 | MB JP1.1, U2.PF3 (`main.h:62`); SY JP1.1 → IC1 | CONFIRMED |
| Main Board (PF4) | JP1 | 2 | `AD9523_REF_SEL` | Synth Board | JP1 | 2 | 3.3 V CMOS | — | CBL-28 | `main.h:64`; SY IC1.REF_SEL | CONFIRMED |
| Main Board (PF5) | JP1 | 3 | `AD9523_SYNC` | Synth Board | JP1 | 3 | 3.3 V CMOS | — | CBL-28 | `main.h:66` | CONFIRMED |
| Main Board (PF6) | JP1 | 4 | `AD9523_RESET` | Synth Board | JP1 | 4 | 3.3 V CMOS | — | CBL-28 | `main.h:68` | CONFIRMED |
| Main Board (PF7) | JP1 | 5 | `AD9523_CS` | Synth Board | JP1 | 5 | SPI CS (3.3 V) | — | CBL-28 | `main.h:70`; firmware never toggles it (docs C7) | CONFIRMED (hardware) |
| Main Board (PE2 SPI4_SCK) | JP1 | 6 | `STM32_SCLK4` → `AD9523_SCLK` | Synth Board | JP1 | 6 | SPI 3.3 V (R6 0.65 k series) | — | CBL-28 | MB U2.PE2; SY JP1.6, R6, IC1.SCLK | CONFIRMED |
| Main Board (PE6 SPI4_MOSI) | JP1 | 7 | `STM32_MOSI4` → `AD9523_SDIO` | Synth Board | JP1 | 7 | SPI 3.3 V (R8 0.65 k) | — | CBL-28 | MB U2.PE6; SY R8, IC1.SDIO | CONFIRMED |
| Synth Board (IC1 SDO) | JP1 | 8 | `AD9523_SDO` → `STM32_MISO4` | Main Board (PE5) | JP1 | 8 | SPI 3.3 V | — | CBL-28 | SY IC1.SDO; MB U2.PE5 | CONFIRMED |
| Synth Board | JP1 | 9 / 10 | `AD9523_STATUS0` / `STATUS1` | Main Board (PF8 / PF9) | JP1 | 9 / 10 | 3.3 V CMOS | — | CBL-28 | `main.h:72-75` | CONFIRMED |
| Main Board (PF10) | JP1 | 11 | `AD9523_EEPROM_SEL` | Synth Board | JP1 | 11 | 3.3 V CMOS | — | CBL-28 | `main.h:76` | CONFIRMED |
| — | JP1 | 12 | GND | — | JP1 | 12 | — | — | CBL-28 | both | CONFIRMED |
| Synth Board (U1/U6 SDO) | JP2 PINHD-2X7 | 1 | `ADF4382_SDO` → `STM32_MISO4` | Main Board (PE5) | JP13 PINHD-2X7 | 1 | SPI 3.3 V (shared SPI4 bus with AD9523) | — | CBL-29 | SY JP2.1; MB JP13.1 | CONFIRMED |
| Main Board (PE2) | JP13 | 2 | `STM32_SCLK4` → `ADF4382_SCLK` | Synth Board | JP2 | 2 | SPI 3.3 V | — | CBL-29 | MB JP13.2; SY JP2.2, U1/U6.SCLK | CONFIRMED |
| Main Board (PE6) | JP13 | 3 | `STM32_MOSI4` → `ADF4382_SDIO` | Synth Board | JP2 | 3 | SPI 3.3 V | — | CBL-29 | MB JP13.3; SY JP2.3 | CONFIRMED |
| Main Board (PG14) | JP13 | 4 | `ADF4382_TX_CS` | Synth Board (U1 CSB, 200 k pull-up R24) | JP2 | 4 | SPI CS 3.3 V | — | CBL-29 | `main.h:154`; SY R24 | CONFIRMED (K6: `adf4382a_manager.h` expects other pins) |
| Main Board (PG15) | JP13 | 5 | `ADF4382_TX_CE` | Synth Board (U1 CE, R25) | JP2 | 5 | 3.3 V CMOS | — | CBL-29 | `main.h:156` | CONFIRMED |
| Main Board (PG12) | JP13 | 6 | `ADF4382_TX_DELSTR` | Synth Board (U1) | JP2 | 6 | 3.3 V CMOS | — | CBL-29 | `main.h:150` | CONFIRMED |
| Main Board (PG13) | JP13 | 7 | `ADF4382_TX_DELADJ` | Synth Board (U1) | JP2 | 7 | 3.3 V CMOS | — | CBL-29 | `main.h:152` | CONFIRMED |
| Synth Board (U1 LKDET) | JP2 | 8 | `ADF4382_TX_LKDET` | Main Board (PG11) | JP13 | 8 | 3.3 V CMOS | — | CBL-29 | `main.h:148` | CONFIRMED |
| Main Board (PG10) | JP13 | 9 | `ADF4382_RX_CS` | Synth Board (U6 CSB, R37) | JP2 | 9 | SPI CS | — | CBL-29 | `main.h:146` | CONFIRMED |
| Main Board (PG9) | JP13 | 10 | `ADF4382_RX_CE` | Synth Board (U6 CE, R38) | JP2 | 10 | 3.3 V CMOS | — | CBL-29 | `main.h:144` | CONFIRMED |
| Main Board (PG8) | JP13 | 11 | `ADF4382_RX_DELSTR` | Synth Board (U6) | JP2 | 11 | 3.3 V CMOS | — | CBL-29 | `main.h:128` | CONFIRMED |
| Main Board (PG7) | JP13 | 12 | `ADF4382_RX_DELADJ` | Synth Board (U6) | JP2 | 12 | 3.3 V CMOS | — | CBL-29 | `main.h:126` | CONFIRMED |
| Synth Board (U6 LKDET) | JP2 | 13 | `ADF4382_RX_LKDET` | Main Board (PG6) | JP13 | 13 | 3.3 V CMOS | — | CBL-29 | `main.h:124` | CONFIRMED |
| — | JP13 | 14 | GND | — | JP2 | 14 | — | — | CBL-29 | both | CONFIRMED |

### 2.6 Frequency Synthesizer Board → Main Board clocks and LO, coaxial (source: `interconnection_table.md` §6; frequencies are the values programmed in `main.cpp:970-1028` and `adf4382a_manager.h:32-34`, firmware intent, not measurements)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Synth (IC1 OUT6 → R39 22 R → C15 10 nF) | J7 SMA 142-0731-211, silk `FPGA SYS. CLOCK` | 1 | `AD9523_OUT6+` 100 MHz LVCMOS → `FPGA_SYS_CLOCK` | Main Board (U42 `IO_L13P_T2_MRCC_15`) | J1 SMA | 1 | 50 Ω coax, single-ended clock | — | CBL-30 | SY J7, R39, C15; MB J1, U42; `main.cpp:1004` | CONFIRMED |
| Synth (OUT10 → R40 → C17) | J5 SMA, silk `DAC` | 1 | 120 MHz LVCMOS → `DAC_CLOCK` | Main Board (U3 AD9708 CLOCK via R31) | J20 SMA | 1 | 50 Ω coax | — | CBL-31 | SY J5; MB J20, R31, U3 | CONFIRMED |
| Synth (OUT11 → R41 → C19) | J6 SMA, silk `FPGA=DAC` | 1 | 120 MHz LVCMOS → `FPGA_DAC_CLOCK` | Main Board (U42 `IO_L12N_T1_MRCC_15`) | J18 SMA | 1 | 50 Ω coax | — | CBL-32 | SY J6; MB J18, U42 | CONFIRMED |
| Synth (OUT7) | J8 SMA, silk `TEST` | 1 | 20 MHz LVCMOS → `FPGA_CLOCK_TEST` | Main Board (U42 `IO_L24P_T3_RS1_15`) | JP20 PINHD-1X2 | 1 (2 = GND) | SMA → 0.1" header (adapter not specified) | — | CBL-33 | SY J8; MB JP20 | UNVERIFIED (adapter) |
| Synth (OUT4) | J3 CJT-T-P-HH-ST-TH1, silk `ADC` | 1 P, 2 N | `AD9523_OUT4_P/N` 400 MHz LVDS → `N$2_P/N` → C1/C2 → `ADC_CLK_IN_P/N` | Main Board (U1 AD9484 CLK+/CLK−, R173 100 Ω) | J21 CJT | 1 P, 2 N | twinax differential | — | CBL-34 | SY J3; MB J21, C1, C2, R173, U1 | CONFIRMED |
| Synth (OUT5) | J4 CJT, silk `FPGA=ADC` | 1 P, 2 N | 400 MHz LVDS → `FPGA_ADC_CLOCK_P/N` | Main Board (U42 `IO_L13P/N_T2_MRCC_14`, R4) | J19 CJT | 1 P, 2 N | twinax differential | — | CBL-35 | SY J4; MB J19, U42 | CONFIRMED (not used by RTL) |
| Synth (U1 ADF4382 TX RFOUT1 → C64/C65 → U2 MTX2-143+ → U4 ATS1005 −3 dB) | J10 SMA, silk `LO TX` | 1 | TX LO 10.5 GHz (`TX_FREQ_HZ`) | Main Board (U5 LTC5552 LO via C272 18 pF) | J23 SMA (`N$23`) | 1 | 50 Ω coax, X-band | — | CBL-36 | SY U1, U2, U4, J10 (`N$30`), brd silk; MB J23, C272, U5.LO | CONFIRMED (silk-to-net association from brd text proximity) |
| Synth (U6 ADF4382 RX RFOUT1 → U7 → U8) | J11 SMA, silk `LO RX` | 1 | RX LO 10.38 GHz (`RX_FREQ_HZ`) | Main Board (U13 LTC5552 LO via C274 18 pF) | J22 SMA (`N$24`) | 1 | 50 Ω coax, X-band | — | CBL-37 | SY U6, U7, U8, J11 (`N$55`); MB J22, C274, U13.LO | CONFIRMED |
| Synth (U1 RFOUT2 → U3 → U5) | J1 SMA, silk `AUX. LO TX` | 1 | auxiliary TX LO | — | — | — | — | — | — | SY J1 (`N$35`) | UNVERIFIED (no destination) |
| Synth (U6 RFOUT2 → U9 → U10) | J12 SMA (silk by elimination `AUX. LO RX`) | 1 | auxiliary RX LO | — | — | — | — | — | — | SY J12 (`N$59`) | UNVERIFIED (no destination, silk not adjacent) |
| Synth (U1 MUXOUT / U6 MUXOUT / IC1 PLL_OUT) | J9 / J2 / J13 SMA | 1 | test outputs | — | — | — | — | — | — | SY J9 (`N$37`), J2 (`N$51`), J13 (`N$61`) | test points, no counterpart |

### 2.7 Main Board ↔ RF PA boards, 16 instances (source: `interconnection_table.md` §7)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board RF_SW_n (n = 1..16) RFOUT1 / RFOUT2 via 1 pF | J27/J26 (n=1), J29/J28 (2), J25/J24 (3), J31/J30 (4), J35/J34 (5), J37/J36 (6), J33/J32 (7), J39/J38 (8), J47/J46 (9), J41/J40 (10), J45/J44 (11), J43/J42 (12), J55/J54 (13), J49/J48 (14), J53/J52 (15), J51/J50 (16) | 1 | element RF (TX to PA / RX return) | RF PA board n | J1 `RFIN` / J2 `RFOUT` | 1 | 50 Ω coax, 10.5 GHz | — | CBL-40..CBL-55 | MB RF_SW_n pins (traced through C126/C128-type 1 pF caps); PA J1 (`N$2`), J2 (`N$8`), brd silk | UNVERIFIED — which SMA of each pair is RFIN vs RFOUT and PA-instance mapping are not documented |
| Main Board (U7/U69 DAC5578 → OPA4703 → `VG_n`) | X_7=VG_1, X_16=VG_2, X_8=VG_3, X_15=VG_4, X_4=VG_5, X_11=VG_6, X_3=VG_7, X_12=VG_8, X_5=VG_9, X_14=VG_10, X_6=VG_11, X_13=VG_12, X_2=VG_13, X_9=VG_14, X_1=VG_15, X_10=VG_16 (Molex 22-23-2021) | S (VG), S (GND) | gate bias `VG_n` (xlsx: −4 … −1.2 V, 10 mA) | RF PA board | X2 Molex 22-23-2021 | 1 `VG`, 2 `GND` | analogue DC | 10 mA (row 60) | CBL-56..CBL-71 | MB X_n nets `VG_n`; PA X2 | CONFIRMED (VG_n → PA instance assignment UNVERIFIED) |
| RF PA board (R10 WSL2816 5 mΩ shunt: `VD` / `VIN_M`) | X3 Molex 22-23-2031 | 1 `VD`, 2 `VIN_M`, 3 `GND` | drain current sense pair | Main Board (INA241A3 U11 for X3, U73 for X38, …) | X3, X38..X52 Molex 22-23-2031 | S (`GND`), S (`N$207`=IN+), S (`N$209`=IN−) (X3 example) | analogue differential sense | — | CBL-72..CBL-87 | PA X3, R10; MB X3 → U11.IN+/IN−, X38 → U73 … | CONFIRMED topology; pin ORDER UNVERIFIED (pads named `S`), PA-instance → Main-connector map NOT DOCUMENTED |
| +22 V drain supply (NOT IN CAD) | — | — | `VD` 22 V (xlsx row 59: 18–22 V, 2000 mA, "Set VD +22 V") | RF PA board | `22V` AK300/2 terminal | KL1 `VD`, KL2 `GND` | DC power | 2 A per board (xlsx) | CBL-88 | PA part `22V`; xlsx row 59; Power Board has no 22 V rail (K4) | MISSING SPEC |
| Main Board (U2 PD6) | JP10 PINHD-1X3 | 1 `EN/DIS_RFPA_VDD`, 3 GND | PA drain enable (set in `main.cpp:1601`) | PA drain switch — device NOT IN CAD | — | — | 3.3 V CMOS | — | — | MB JP10; `main.h:140` | MISSING SPEC |

### 2.8 Main Board ↔ host and off-board modules (source: `interconnection_table.md` §8)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Main Board (U2 PA11 / PA12 / PA10) | X53 MINI-USB | 2 `STM32_USB_FS_D_N`, 3 `D_P`, 4 `ID`, 5 GND (1 VBUS not connected in sch) | USB 2.0 full-speed, CDC class (firmware `usbd_cdc_if` references) | Host PC | USB-A/host port | — | USB 2.0 FS | bus-powered: NO (VBUS pin unconnected; VDDUSB = +3V3) | CBL-90 | MB X53, U2.PA10-PA12, VDDUSB | CONFIRMED (host side MISSING SPEC) |
| Main Board (U6 FT601) | — | — | USB 3.0 (RTL `radar_system_top.v:79-97`, GUI_V6.py FT601 class) | Host PC | — | — | USB 3.0 | — | — | MB U6: 0 nets | MISSING SPEC — no hardware path (K3) |
| Main Board | JP2 PINHD-1X6 | 1 `+3V3`, 2 `STM32_SWCLK`, 3 GND, 4 `STM32_SWDIO`, 5 `STM32_NRST`, 6 `STM32_SWO` | SWD | debug probe (not specified) | — | — | ARM SWD 3.3 V | — | CBL-91 | MB JP2 | CONFIRMED (probe MISSING SPEC) |
| Main Board (U2 PC12 / PD2) | JP8 PINHD-1X4 | 1 `+3V3`, 2 `STM32_TX5`, 3 `STM32_RX5`, 4 GND | UART5 (9600 Bd per firmware GPS driver) | GPS module NEO-6M (xlsx row 49) | module header | — | UART 3.3 V | 50 mA (row 49) | CBL-92 | MB JP8, U2.PC12/PD2 | UNVERIFIED (module pinout) |
| Main Board (U2 PA8 / PC9 / PC6 / PC7 / PC8) | JP7 PINHD-1X8 | 2 `+3V3`, 3 GND, 4 `STM32_SCL3`, 5 `STM32_SDA3`, 6 `MAG_DRDY`, 7 `ACC_INT`, 8 `GYR_INT` (pin 1 unconnected) | I2C3 + interrupts | GY-85 IMU (xlsx row 47) | module header | — | I2C 3.3 V | 10 mA | CBL-93 | MB JP7; `main.h:130-135` | UNVERIFIED (module pinout) |
| Main Board | JP18 PINHD-1X4 | 1 `STM32_SDA3`, 2 `STM32_SCL3`, 3 GND, 4 `+3V3` | I2C3 | BMP180 barometer (xlsx row 48) | module header | — | I2C 3.3 V | 1 mA | CBL-94 | MB JP18 | UNVERIFIED (module pinout; JP7/JP18 assignment to IMU vs BMP180 is an assumption) |
| Main Board | JP5, JP6, JP11, JP12, JP14, JP15, JP16, JP19 PINHD-1X3 | 1 `+3V3_AN4_F`, 2 analogue (`N$295, N$296, N$306, N$298, N$299, N$307, N$301, N$297`), 3 GND | TMP37 output → ADS7830 channel | 8 × TMP37 (xlsx row 50) | sensor leads | — | analogue 3.3 V | 1 mA each | CBL-95..CBL-102 | MB JP5..JP19 nets | CONFIRMED (header) / channel order UNVERIFIED |
| Main Board (U2 PD4 / PD5) | JP9 PINHD-1X4 | 1 GND, 2 `STEPPER_CW+`, 3 GND, 4 `STEPPER_CLK+` | direction / step | stepper driver "TBS6600" (xlsx row 63; TB6600-class) | driver inputs | — | 3.3 V logic | driver 4000 mA @ 20 V from its own supply (row 63) | CBL-103 | MB JP9; `main.h:136-139` | UNVERIFIED (driver pinout, supply not in CAD) |
| Main Board (U2 PD7) | JP4 PINHD-1X3 | 1 `EN/DIS_COOLING`, 3 GND | fan relay control (`main.cpp:1767-1770`) | cooling relay / fans (xlsx row 64) | — | — | 3.3 V logic | UNKNOWN | CBL-104 | MB JP4; `main.h:142` | MISSING SPEC (relay/fan parts) |
| Main Board (U2 PB10 / PB11) | JP17 PINHD-1X3 | 1 `STM32_TX3`, 2 `STM32_RX3`, 3 GND | USART3 debug console (`huart3` in `main.cpp`) | serial adapter (not specified) | — | — | UART 3.3 V | — | CBL-105 | MB JP17 | CONFIRMED (header) |
| Main Board | JP3 PINHD-2X4 | 1 `N$32`, 2 `+3V3_FPGA`, 3 `N$33`, 5 `N$34`, 7 `N$36`, 8 GND | FPGA JTAG header (nets reach U42 TCK/TMS/TDI/TDO through R62/R49/R64/R63 — see `docs/FPGA/`) | JTAG programmer | — | — | JTAG 3.3 V | — | CBL-106 | MB JP3 | UNVERIFIED (pin-to-TAP assignment not traced here) |

### 2.9 Antenna (source: `interconnection_table.md` §9)

| Source device | Source connector | Pin | Signal | Destination device | Destination connector | Pin | Interface standard | Power requirement | Cable ID | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RF PA board n | J2 `RFOUT` | 1 | element n TX (AERIS-10X) | antenna array element | — | — | 50 Ω coax / waveguide transition | 10 W per element (README) | — | README.md; RADAR_V6.drawio | MISSING SPEC (no antenna CAD, K8) |
| Main Board | J24..J55 | 1 | element RF (AERIS-10N direct) | antenna array element | — | — | 50 Ω | ~1 W per element (README) | — | README.md | MISSING SPEC |

### 2.10 Items left UNVERIFIED by SYS-02 and why (source: `engineering/SYSTEM/architecture/README.md`, "Items left UNVERIFIED", copied)

| Item | Reason |
|---|---|
| Pin order of all Molex 22-23-2021/2031 connections | EAGLE symbol names every pad `S`; order not recoverable from the schematic |
| Which SMA of each element pair (e.g. J27/J26) goes to PA `RFIN` vs returns from `RFOUT`, and PA-board-instance → Main-connector assignment | no silkscreen text on the Main Board `.brd`, no cabling document |
| Synth J12 function (`AUX. LO RX`) | silkscreen text not adjacent; assigned by elimination |
| Oscillator identities (X4 100 MHz OCXO vs net `10MHZ_OUT`; X5/X6 50 MHz VCXO vs nets `100MHZ_OUT`/`VCXO_OUT` and firmware 100 MHz) | contradictory sources (K7) |
| `+1V8_CLOCK` distribution to both Main X17 and Synth X12 from the single Power output X10 | no cable/Y-splice in CAD |
| 22 V PA drain source and the switch driven by `EN/DIS_RFPA_VDD` | absent from all CAD (K4) |
| GPS / IMU / BMP180 / stepper-driver / relay module pinouts and supplies | modules named only in the xlsx; no module schematics |
| JP3 pin → FPGA TAP signal assignment | nets `N$32..N$36` not traced here (see `docs/FPGA/`) |
| Host-link packet format, USB 3.0 path | no FT601 nets (K3); RTL/GUI packet formats differ (K5) |
| DIG_0..7 bit meaning | inferred from firmware/RTL names only (`docs/SYSTEM/BLOCK_DIAGRAM.md` §3) |
| Output voltages, regulator current capability, VIN total current | dividers listed, no datasheet for TPS562208 in repo; no budget sum in xlsx |
| Cable types, lengths, coax grade, wire gauge | not in any repository file |
| Antenna feed network, element-to-port mapping, waveguide transition | no antenna CAD (K8) |

## 3. Interface implementation status

The electrical existence of an interface says nothing about whether the firmware or the RTL drives it. The cross-check per interface (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §3, copied verbatim; the RTL column describes the original `9_Firmware/9_2_FPGA`, the BETA state is in chapters 2 and 11):

| Interface | CAD | Firmware | RTL | Status |
|---|---|---|---|---|
| STM32 → FPGA handshake (`DIG_0..4`) | yes | `main.cpp:448,484,514,1483,1660` | `stm32_new_*`, `stm32_mixers_enable`, `reset_n` | bit mapping inferred (MEDIUM) |
| STM32 SPI1 → FPGA → ADAR1000 (1.8 V) | yes | `ADAR1000_Manager.cpp` on `hspi1` | level shifter **not instantiated** (`radar_transmitter.v:59-71` undriven) | **BROKEN in RTL** |
| FPGA → host (FT601) | **not wired** | — | `usb_data_interface.v` | **NO HARDWARE** |
| STM32 ↔ host (USB CDC) | yes | RX callback never bound (C4); start-flag padding (C5) | — | **BROKEN in firmware** |
| STM32 → AD9523 (SPI4) | yes | CS never toggled, 36 MHz (C7) | — | questionable |
| STM32 → ADF4382 (SPI4) | yes | pin macros collide with PA enables (C2); `platform_ops=NULL` (C3) | — | **BROKEN** |
| AD9523 → FPGA clocks | yes (J1, J18, J19) | OUT6/OUT11/OUT5 programmed | `clk_100m`, `clk_120m_dac`; 400 MHz path uses ADC DCO only | partially consistent |
| ADC → FPGA LVDS | yes (bank 14 at 3.3 V) | — | capture not implemented; XDC wants LVDS_25 + DIFF_TERM | **BROKEN / bank-voltage conflict** |
| GPS → host | UART5 + USB | `GPS_Init` never called (C6) | — | **BROKEN** |

The firmware defects C2–C7 are fixed in `beta/stm32` (ADF4382 pin collision, `platform_ops = NULL`, unbound CDC RX, padded settings frames, GPS_Init, AD9523 CS/SPI speed) and the RTL defects in `beta/fpga` (level-shifter pass-through instantiated, ISERDES capture, SPI bridge); none of these fixes has been exercised on hardware (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §3–4).

## 4. Power distribution

![Figure 9 — F3.2 — Power distribution diagram ELEC-PWR-01 / SYS-04: every Power Board rail with regulator, feedback divider, source rail, enable net and MCU pin, firmware sequence step, output connector → destination connector → consumer — SOURCE-DERIVED; output voltages from net names, currents UNKNOWN (source: engineering/ELECTRICAL/power_distribution/power_distribution.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/ELECTRICAL/power_distribution/power_distribution.png)

Conventions of the rail register (source: `engineering/ELECTRICAL/power_distribution/power_rails.md`, lead-in): **Nominal V** is the value encoded in the net name and the xlsx column H "SELECTED VOLTAGE"; feedback resistor values are listed as evidence but output voltages were **not recomputed** (the TPS562208 datasheet is not in the repository — only `tps562201.pdf`). **Current ratings are UNKNOWN** unless the xlsx gives a per-device budget; regulator capability is not asserted. **Enable** = net on the Power Board EN pin (`VIN` or own input = always on). Sequence step: `xlsx` = text of column L/K, `FW` = firmware order F1..F10 of section 4.2. Status: CONFIRMED = regulator, nets and consumer connector all found; PARTIAL = found but something inconsistent; UNVERIFIED = consumer or cable cannot be established; CONFLICT = contradicts another source.

### 4.1 Rail register (source: `power_rails.md` §1, copied verbatim)

| Rail | Nominal V (source) | Regulator (ref, part) | Source rail | Consumers (board: connector → loads) | Enable signal (MCU pin) | Sequence step | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| `VIN` | 12–17 V (brd silk `Vin [12-17]V`) | — (input) | external DC source (not specified) | all 21 bucks; U30 ADM7151 directly | — | — | PB X1 `AK300/2` (KL: VIN, GND) | UNVERIFIED (source, total current) |
| `+1V0_FPGA` | 1.0 V (net; xlsx row 17 "1") | U1 TPS562208DDCT, FB R1 3.09 k / R2 10 k | VIN | Main: X4→X8 → U42 VCCINT, VCCBRAM | `EN_+1V0_FPGA` PE7 (`main.h:98`) | xlsx: FPGA rows order +1V0 → +1V8 → +3V3 (L15-L17), K=YES; FW: F3 (`main.cpp:1271`, +100 ms) | PB U1 pins; MB X8, U42 | CONFIRMED |
| `+1V8_FPGA` | 1.8 V (xlsx rows 14,16,26) | U2 TPS562208, R3 13.7 k / R4 10 k | VIN | Main: X5→X10 → U42 VCCAUX, VCCADC, VCCBATT, VCCO_34; U1 AD9484 DRVDD; R154–R157 pull-ups (ADAR CS 1.8 V) | `EN_+1V8_FPGA` PE8 | K=YES; FW: F4 (`main.cpp:1273`, +100 ms) | PB U2; MB X10 | CONFIRMED |
| `+3V3_FPGA` | 3.3 V (rows 15,18,20,27) | U4 TPS562208, R7 32.2 k / R8 10 k | VIN | Main: X27→X16 → U42 VCCO banks 14/15 + config pull-ups, U3 AD9708 DVDD, U9 flash; L19 → `+3V3_FT` (FT601, unrouted) | `EN_+3V3_FPGA` PE9 | K=YES; FW: F5 (`main.cpp:1275`, +100 ms) | PB U4; MB X16 | CONFIRMED |
| `+3V3` | 3.3 V (rows 13,47-49,55) | U3 TPS562208, R5 32.2 k / R6 10 k | VIN | Main: X16→X24 → U2 STM32 VDD/VDDUSB, headers JP2/JP7/JP8/JP18 (+3V3 pin for modules), ADS7830 VREF (xlsx row 55) | always on (EN = VIN) | xlsx K=NO | PB U3; MB X24, U2.VDDUSB | CONFIRMED |
| `+3V3_AN` | 3.3 V (rows 19,21,50,51,54,56) | U5 ADM7151ACPZ-04, EN tied to its input | `+5V0_0` (U12) | Main: X12→X9 (and X56 same net) → L15 `+3V3_AN1_F` U5 mixer VCC; L16 `+3V3_AN2_F` U13 mixer; L17 `+3V3_AN3_F` U7/U69 DAC5578; L18 `+3V3_AN4_F` TMP37 headers + ADS7830; L21/L23 `+3V3_AN5_F`/`_6_F` 16 × INA241; L6 BLM15H `DAC_AVDD` U3 | none (follows `+5V0_0`) | K=NO | PB U5; MB X9, X56, L6/L15–L18/L21/L23 | CONFIRMED (X9 vs X56 use UNVERIFIED) |
| `+1V8_CLOCK` | 1.8 V (rows 7, 25) | U25 ADM7151, EN = `EN_+1V8_CLOCK` | `+5V0_2` (U24) | Synth: X10→X12 → L11 → IC1 AD9523 VDD1.8_OUT*, VDD1.8_PLL2. Main: X10→X17 → L1 → `+1V8_CLOCK_F` → U1 AD9484 AVDD ×11, CSB | `EN_+1V8_CLOCK` PG4 (`main.h:120`) | xlsx L6: "bring the 1.8 V supplies high ... prior to or simultaneously with the 3.3 V"; FW: **F1** (`main.cpp:1241`, +100 ms) | PB U25, X10; SY X12, L11; MB X17, L1 | **PARTIAL** — one Power-Board output (X10) for two destination connectors; splitting not in CAD |
| `+3V3_CLOCK` | 3.3 V (row 6) | U23 ADM7151, EN = `EN_+3V3_CLOCK` | `+5V0_1` (U9) | Synth: X11→X11 → L10 → IC1 VDD3_OUT*, VDD3_PLL1/2, VDD3_REF | `EN_+3V3_CLOCK` PG5 (`main.h:122`) | xlsx L6 (after 1.8 V), K=YES; FW: F2 (`main.cpp:1243`, +100 ms, then AD9523 RESET released) | PB U23, X11; SY X11, L10 | CONFIRMED |
| `+3V3_XO` | 3.3 V (rows 2-5) | U34 TPS7A8300RGRR, EN = its input | `+5V0_5` (U33) | Synth: X35→X10 → L9 → X4 OCXO SUPPLY_VOLTAGE (+R2/R3 VC divider), X5/X6 VCXO VDD | none (always on when VIN present) | K=NO | PB U34, X35; SY X10, L9 | CONFIRMED |
| `+5V0_LO` | 5.0 V (rows 8-10) | U30 ADM7151, EN = VIN | **VIN directly (12–17 V)** | Synth: X6→X15 → FB1..FB4 ferrites → ADF4382 U1/U6 5 V domains | none | K=NO | PB U30 (VIN = `VIN`), X6; SY X15 | **CONFLICT / REQUIRES DESIGN REVIEW** — ADM7151 input fed from the 12–17 V bus; check against `7_Components Datasheets and Application notes/ADM7151.pdf` input-voltage rating |
| `+3V3_LO_1` | 3.3 V (row 11) | U27 ADM7151, EN = its input | `+5V0_3` (U26) | Synth: X8→X13 → L12 → U1/U6 V3_LDO, V3_LS, V3_NDIV, V3_PFD, V3_REF, V3_SYNC; 200 k pull-ups R24/R25/R37/R38 | none | K=NO | PB U27, X8; SY X13, L12 | CONFIRMED |
| `+3V3_LO_2` | 3.3 V (row 12) | U29 ADM7151, EN = its input | `+5V0_4` (U28) | Synth: X7→X14 → L13 → U1/U6 V3_OUTDIV, V3_RFOUT1/2, V3_VCOB; RFOUT bias chokes L1..L8 | none | K=NO | PB U29, X7; SY X14, L13 | CONFIRMED (brd has a board-only `+3V3_LO` signal — annotation residue, `docs/PCB/POWER_SUPPLY.md`) |
| `+5V0_ADAR` | 5.0 V | U13 TPS562208, R25 56.2 k / R26 10 k | VIN | Power Board only: U20, U21 LM2662 inputs; X13 output has **no consumer** on Main | `EN_+5V0_ADAR` PE10 (`main.h:104`) | FW: F7 (`main.cpp:1488`, +500 ms) — enables the −5 V ADAR rails indirectly | PB U13, U20, U21, X13; MB: no `+5V0_ADAR` net | CONFIRMED (X13 spare) |
| `-5V0_ADAR12` | −5 V (row 29) | U20 LM2662MX/NOPB (charge-pump inverter) | `+5V0_ADAR` | Main: X21→X13 → ADAR1_, ADAR2_ AVDD | via `EN_+5V0_ADAR` | xlsx L30: AVDD3 (3.3 V) before or with AVDD1 (−5 V); FW: F7 after F6 (+500 ms) — consistent | PB U20, X21; MB X13 | CONFIRMED |
| `-5V0_ADAR34` | −5 V | U21 LM2662 | `+5V0_ADAR` | Main: X20→X15 → ADAR3_, ADAR4_ AVDD | via `EN_+5V0_ADAR` | as above | PB U21, X20; MB X15 | CONFIRMED |
| `+3V3_ADAR_12` (Main: `+3V3_ADAR12`) | 3.3 V (row 30) | U6 TPS562208, R11 32.2 k / R12 10 k | VIN | Main: X14→X20 → L11 `+3V3_ADAR1_F` ADAR1_ AVDD3 ×3; L12 `+3V3_ADAR2_F` ADAR2_ | `EN_+3V3_ADAR12` PE11 (`main.h:106`) | K=YES; FW: F6 (`main.cpp:1485`, +500 ms with ADAR34) | PB U6, X14; MB X20, L11, L12 | CONFIRMED (net name differs by underscore) |
| `+3V3_ADAR_34` (Main: `+3V3_ADAR34`) | 3.3 V | U7 TPS562208, R13 32.2 k / R14 10 k | VIN | Main: X15→X21 → ADAR3_, ADAR4_ AVDD3 (filters analogous) | `EN_+3V3_ADAR34` PE12 (`main.h:108`) | FW: F6 (`main.cpp:1486`) | PB U7, X15; MB X21 | CONFIRMED |
| `+5V0_ADTR` | 5.0 V | U31 TPS562208, R51 56.2 k / R52 10 k | VIN | Power Board only: U32 TPS7A8300 input; X26 output has no consumer | always on (EN = VIN) | — | PB U31, U32, X26 | CONFIRMED (X26 spare) |
| `+3V3_ADTR` | 3.3 V (row 35, VDD_LNA 16 × 80 mA) | U32 TPS7A8300RGRR, EN = `EN_+3V3_ADTR` | `+5V0_ADTR` | Main: X34→X4 → 16 × ADTR1107 VDD_LNA | `EN_+3V3_ADTR` PE13 (`main.h:110`) | xlsx RX power-up step 8 "Set VDD_LNA to 3.3 V" (M38), TX step 6 VDD_LNA = 0 V; FW: **never set HIGH** — only reset at init (`main.cpp:2245-2247`) and power-down (`main.cpp:394`) | PB U32, X34; MB X4; grep of `9_Firmware/9_1_Microcontroller` for `EN_P_3V3_ADTR_Pin` + `GPIO_PIN_SET` = 0 hits | **CONFLICT (firmware never enables the LNA supply)** |
| `+3V3_VDD_SW` | 3.3 V (row 38) | U8 TPS562208, R15 32.2 k / R16 10 k | VIN | Main: X30→X12 → 16 × ADTR1107 VDD_SW | `EN_+3V3_VDD_SW` PE15 (`main.h:114`) | xlsx TX/RX step 2 "Set VDD_SW to 3.3 V" (first ADTR rail); FW: F8 (`ADAR1000_Manager.cpp:51`, +2 ms) | PB U8, X30; MB X12 | CONFIRMED |
| `+3V3_SW` | 3.3 V | U10 TPS562208, R19 32.2 k / R20 10 k | VIN | Power Board only: U18 LM2662 input; X29 output has no consumer | `EN_+3V3_SW` PE14 (`main.h:112`) | FW: F9 (`ADAR1000_Manager.cpp:54`, +2 ms) — enables `-3V3_SW` | PB U10, U18, X29 | CONFIRMED (X29 spare) |
| `-3V3_SW` | −3.3 V (row 37) | U18 LM2662 | `+3V3_SW` | Main: X18→X6 → 16 × ADTR1107 VSS_SW | via `EN_+3V3_SW` | xlsx step 3 "Set VSS_SW to −3.3 V" after VDD_SW; FW F9 after F8 — consistent | PB U18, X18; MB X6 | CONFIRMED |
| `+5V0_PA_1` | 5.0 V (row 40, VDD_PA 250 mA each) | U14 TPS562208, R27 56.2 k / R28 10 k | VIN | Main: X31→X14 → ADTR1107_1, _2, _3, _4, _7 VDD_PA | `EN_+5V0_PA1` PG0 (`main.h:94`) | xlsx TX step 8 "Set VDD_PA to 5 V"; FW: **never set HIGH** (reset at `main.cpp:2239-2241`, power-down `:381`) | PB U14, X31; MB X14, ADTR VDD_PA nets | **CONFLICT (firmware)** |
| `+5V0_PA_2` | 5.0 V | U15 TPS562208, R29 56.2 k / R30 10 k | VIN | Main: X32→X5 → ADTR1107_5, _6, _8, _10, _12 | `EN_+5V0_PA2` PG1 | as above | PB U15, X32; MB X5 | **CONFLICT (firmware)** |
| `+5V0_PA_3` | 5.0 V | U16 TPS562208, R31 56.2 k / R32 10 k | VIN | Main: X33→X7 → ADTR1107_9, _11, _13, _14, _15, _16 | `EN_+5V0_PA3` PG2 | as above | PB U16, X33; MB X7 | **CONFLICT (firmware)** |
| `+5V5_PA` | 5.5 V (row 52) | U17 TPS562208, R33 61.9 k / R34 10 k | VIN | Main: X3→X55 → 4 × OPA4703 V+ (VG drivers); Power Board: U22 input | `EN_+5V5_PA` PG3 (`main.h:118`) | xlsx K=YES; FW: **never set HIGH** (reset at `main.cpp:2239`) | PB U17, X3; MB X55 | **CONFLICT (firmware)** — VG drivers unpowered although `main.cpp:1583-1601` programs them |
| `-5V5_PA` | −5.5 V (row 53) | U22 LM2662 | `+5V5_PA` | Main: X19→X19 → 4 × OPA4703 V− | via `EN_+5V5_PA` | as above | PB U22, X19; MB X19 | **CONFLICT (firmware)** |
| `+3V4` | 3.4 V (row 22) | U11 TPS562208, R21 34.8 k / R22 10 k | VIN | Main: X23→X1 (X54 same net) → 17 × M3SWA2-34DR+ VDD; Power Board: U19 input | always on | K=NO | PB U11, X23; MB X1, X54 | CONFIRMED |
| `-3V4` | −3.4 V (row 23) | U19 LM2662 | `+3V4` | Main: X24→X11 (X22 same net) → 17 × M3SWA2 VEE | always on | K=NO | PB U19, X24; MB X11, X22 | CONFIRMED |
| `+5V0_0` | 5.0 V (row 24) | U12 TPS562208, R23 56.2 k / R24 10 k | VIN | Main: X22→X18 → U4, U8 AD8352 VCC; Power Board: U5 ADM7151 input | always on | K=NO | PB U12, X22; MB X18 | CONFIRMED |
| `+5V0_1` | 5.0 V | U9 TPS562208, R17 56.2 k / R18 10 k | VIN | Power Board: U23 input; X2 spare | always on | — | PB U9, X2 | CONFIRMED (X2 spare) |
| `+5V0_2` | 5.0 V | U24 TPS562208, R37 56.2 k / R38 10 k | VIN | Power Board: U25 input; X9 spare | always on | — | PB U24, X9 | CONFIRMED (X9 spare) |
| `+5V0_3` | 5.0 V | U26 TPS562208, R41 56.2 k / R42 10 k | VIN | Power Board: U27 input; X17 spare | always on | — | PB U26, X17 | CONFIRMED (X17 spare) |
| `+5V0_4` | 5.0 V | U28 TPS562208, R45 56.2 k / R46 10 k | VIN | Power Board: U29 input; X25 spare | always on | — | PB U28, X25 | CONFIRMED (X25 spare) |
| `+5V0_5` | 5.0 V | U33 TPS562208, R55 56.2 k / R56 10 k | VIN | Power Board: U34 input; X28 spare | always on | — | PB U33, X28 | CONFIRMED (X28 spare) |
| `+22V0` / `VD` (PA drain) | 22 V (xlsx row 59: 18–22 V, 2000 mA × 16) | **none in CAD** | external | RF PA board: `22V` AK300/2 → VD → R10 5 mΩ → VIN_M → QPA2962 VD1/VD2 | `EN/DIS_RFPA_VDD` PD6 → JP10 (`main.h:140`; set at `main.cpp:1601`) — switch device NOT IN CAD | xlsx L58-L62 bias-up: ID limit 2840 mA, VG −4 V, then VD +22 V, raise VG until IDQ 1680 mA, then RF; K=YES | PA sch `22V`, R10, X3; xlsx; `docs/PCB/POWER_SUPPLY.md` | **CONFLICT K4 — no 22 V source on the Power Board** |
| `VG_1..16` (PA gate) | −4 … −1.2 V (xlsx row 60; `main.cpp:1583` sets −3.98 V = code 126) | Main Board OPA4703 (OPA_1..4) driven by U7/U69 DAC5578 | `+5V5_PA` / `-5V5_PA` | Main X_1..X_16 → PA X2 → QPA2962 VG via R1..R3 | DAC codes over I2C1; LDAC/CLR PB4/PB5/PB8/PB9 | xlsx: VG before VD | MB VG_n nets, OPA_2.OUTD; PA X2, R1-R3 | PARTIAL (depends on `+5V5_PA`, never enabled) |
| Stepper driver supply | 20 V (xlsx row 63, 4000 mA) | none in CAD | external | "TBS6600" driver | — | — | xlsx row 63 only | MISSING SPEC |
| Cooling | — (xlsx row 64, relay) | none in CAD | external | fans via relay, `EN/DIS_COOLING` PD7 (JP4) | PD7 (`main.cpp:1767-1770`) | "Apply when temperature reaches a threshold (Relay)" | xlsx row 64; MB JP4 | MISSING SPEC |

Rails on the Main Board that have no Power-Board source: none (every Main Board rail connector maps to a Power Board output). Main Board rail names that differ from the Power Board: `+3V3_ADAR12/34` vs `+3V3_ADAR_12/34` (naming only; electrical identity assumed, to be confirmed by the designer) (source: `power_rails.md` §1, closing paragraph).

### 4.2 Firmware enable sequence as coded, not executed on hardware (source: `power_rails.md` §3, copied verbatim)

| Step | Action | Delay after | Source |
|---|---|---|---|
| F0 | `HAL_Delay(180000)` (3 min) then AD9523 RESET low | — | `main.cpp:1237-1238` |
| F1 | `EN_+1V8_CLOCK` high | 100 ms | `main.cpp:1241-1242` |
| F2 | `EN_+3V3_CLOCK` high; AD9523 RESET high; `configure_ad9523()` | 100 ms + 100 ms | `main.cpp:1243-1267` |
| F3 | `EN_+1V0_FPGA` high | 100 ms | `main.cpp:1271-1272` |
| F4 | `EN_+1V8_FPGA` high | 100 ms | `main.cpp:1273-1274` |
| F5 | `EN_+3V3_FPGA` high | 100 ms | `main.cpp:1275-1276` |
| F6 | DIG_3 (PD11) low "mixers off"; `EN_+3V3_ADAR12` + `EN_+3V3_ADAR34` high | 500 ms | `main.cpp:1483-1487` |
| F7 | `EN_+5V0_ADAR` high (→ −5 V ADAR rails) | 500 ms | `main.cpp:1488-1489` |
| F8 | `EN_+3V3_VDD_SW` high | 2 ms | `ADAR1000_Manager.cpp:51-52` (`powerUpSystem()`; whether `systemPowerUpSequence()` reaches it via `initializeADTR1107Sequence()` is UNVERIFIED) |
| F9 | `EN_+3V3_SW` high (→ −3V3_SW) | 2 ms | `ADAR1000_Manager.cpp:54-55` |
| F10 | DAC5578 VG codes written, LDAC pulsed, then `EN/DIS_RFPA_VDD` high (22 V drain) | — | `main.cpp:1560-1601` |
| never | `EN_+3V3_ADTR`, `EN_+5V0_PA1/2/3`, `EN_+5V5_PA` | — | no `GPIO_PIN_SET` write anywhere under `9_Firmware/9_1_Microcontroller/` |
| power-down | ADAR RX mode → `EN_+5V0_PA1..3` low → PA bias safe → `EN_+3V3_ADTR` low → LNA bias 0 → `EN_+3V3_VDD_SW`, `EN_+3V3_SW` low (10 ms steps) | 10 ms | `main.cpp:372-409` |

Comparison with the xlsx (source: `power_rails.md` §3): the 1.8 V-before-3.3 V rule for the AD9523 (L6) and the AVDD3-before-AVDD1 rule for the ADAR1000 (L30) are respected by F1→F2 and F6→F7. The ADTR1107 TX/RX procedures (L31-L46) require VDD_SW, VSS_SW, then VDD_LNA / VDD_PA — the firmware performs F8/F9 but never asserts the LNA (`+3V3_ADTR`) or PA (`+5V0_PA_x`) enables, so the ADTR1107 bias procedure cannot complete as coded. The QPA2962 bias-up (L58-L62: VG −4 V → VD 22 V → raise VG to IDQ 1680 mA) is partially mirrored by F10 (VG −3.98 V then drain enable), but the VG driver supply (`+5V5_PA`) is never enabled. The BETA report lists the firmware defects fixed in `beta/stm32` (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4); whether the five missing enables are among them is documented in chapter 12, not asserted here.

### 4.3 Open items for the power designer (source: `power_rails.md` §4, copied)

1. 22 V PA drain supply: no source, no switch, no cabling in CAD (K4).
2. `+5V0_LO` LDO U30 input tied to the 12–17 V bus — confirm against the ADM7151 rating or add a pre-regulator.
3. `+1V8_CLOCK` output X10 must feed both the Main Board (ADC AVDD) and the Synth Board (AD9523) — add a second output or document a Y-cable.
4. Five `+5V0_n` outputs (X2, X9, X17, X25, X28), X13, X26 and X29 have no destination — mark as spare or remove.
5. Rail current capability per regulator and the VIN total are not documented anywhere; the xlsx gives device budgets only.
6. Firmware: enables for `+3V3_ADTR`, `+5V0_PA_1..3`, `+5V5_PA` are missing (CONFLICT rows above).

## 5. Harness schedule (PROPOSED DESIGN)

The harness schedule DSN-HAR-01 is generated by `tools/design_mechanical_drawings.py` from the proposed internal layout (`tools/design_layout.py`) and the connector positions in the KiCad pick-and-place files. Length = Manhattan distance between connector positions in the head + service allowance (40 mm coax / 60 mm wire), rounded up to 10 mm; lengths are PROPOSED and are to be cut after a first fit. Totals: 144 cables; coax 55; wire 89; total proposed length ≈ 41.6 m (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, header). Cable types follow decision D-15: coax RG-405 (0.086") hand-formable equal-length for Main↔PA and Synth↔Main, Molex 22-01-3027/3037 crimp housings for the 2-/3-pin headers, 20-way IDC ribbon for SV1 (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2, D-15).

Grouping of the 144 rows (source: `HARNESS_SCHEDULE.md`, rows CBL-001…CBL-144; this grouping is a reading aid of the manual, the row content is the source's):

| ID range | Count | From → to | Cable | Notes in the source |
|---|---|---|---|---|
| CBL-001 … CBL-034 | 34 | Power Supply X2..X35 → Main Board / Synth rail connectors | 2-wire 20 AWG, Molex 22-01-2027 both ends | 12 rows have destination "? ?" and length TBD: `+5V0_1..5`, `+3V3_LO_1/2`, `+3V3_CLOCK`, `+5V0_ADAR`, `+3V3_ADAR_12/34`, `+5V0_ADTR`, `+3V3_SW` — "no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md" |
| CBL-035 | 1 | Power Supply SV1 → Main Board SV1 | enable bus (15 EN + GND), 320 mm | — |
| CBL-036 … CBL-042 | 7 | Synth J7/J5/J6/J3/J10/J11/J4 → Main J1/J20/J18/J21/J23/J22/J19 | coax: 100 MHz sys clk, 120 MHz DAC ×2, 400 MHz ADC, LO TX, LO RX, test | 100–170 mm |
| CBL-043 … CBL-044 | 2 | Synth JP1/JP2 → Main JP1/JP13 | control headers | 210 / 240 mm |
| CBL-045 … CBL-140 | 96 | per PA board n = 1..16, six cables each: Main X_n → PA X2 (VG_n, 2-wire 24 AWG shielded), Main X3/X38..X52 → PA X3 (drain current sense, 3-wire 24 AWG twisted), Main J-pair → PA J1 RFIN and PA J2 → Main J-pair (RG-405 SMA-SMA, EQUAL LENGTH set), PA J2 → antenna row n (RG-405 SMA-2.92 mm, EQUAL LENGTH set), DSN-PSU-01 OUTn → PA `22V` (2-wire 18 AWG twisted, AK300/2) | "PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD"; "which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7)"; "antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase" |
| CBL-141 … CBL-142 | 2 | slip ring VIN → Power Supply X1; slip ring VIN → DSN-PSU-01 IN | 2 × 2-wire 16 AWG | 340 / 470 mm |
| CBL-143 | 1 | slip ring USB → Main Board X53 | USB 2.0 shielded, mini-B | 360 mm |
| CBL-144 | 1 | Main Board stepper pins → pedestal TB6600 (via slip ring) | 3-wire 24 AWG shielded, TBD | "the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head (then only motor phases cross: 4 circuits) — DECISION NEEDED" |

The full 144-row schedule is in [engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md](engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md) and, machine-readable, in `engineering/DESIGN/HARNESS/harness_schedule.csv`; Appendix B reproduces it.

Two cable-ID schemes coexist in the repository and must not be confused: the interconnection table uses two-digit IDs `CBL-00…CBL-106` assigned per signal group (e.g. CBL-01 = `+1V0_FPGA` X4→X8, CBL-21 = the whole SV1 ribbon, CBL-40..55 = the RF pairs), whereas the harness schedule uses three-digit IDs `CBL-001…CBL-144` assigned per physical cable in connector order (e.g. CBL-003 = `+1V0_FPGA` X4→X8, CBL-035 = the SV1 ribbon, CBL-047/048 = PA1 RF pair) (source: `engineering/SYSTEM/interfaces/interconnection_table.md` §2–3, §7; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` rows CBL-003, CBL-035, CBL-047). The manual keeps each ID in the form of its source and records the duplication as observation MAN-03 in chapter 17. The twelve "? ?" rows of the harness schedule correspond to the rails that the interconnection table resolves either to Synth connectors through series inductors (`+3V3_LO_1/2`, `+3V3_CLOCK` → SY X13/X14/X11 via L12/L13/L10; CBL-23, CBL-25, CBL-26) or to spare outputs with no consumer (`+5V0_1..5`, `+5V0_ADAR`, `+5V0_ADTR`, `+3V3_SW`), and `+3V3_ADAR_12/34`, which the interconnection table matches to Main X20/X21 despite the one-underscore name difference (CBL-07, CBL-08) (source: `interconnection_table.md` §2, §4).


---

<!-- chapter 4: Main Board: schematic set, layout, BOM, DRC state, rev. B host interface -->
# 4. Main Board (RADAR_Main_Board)

**Chapter status summary:** schematic set — SOURCE-DERIVED (rendered from the EAGLE 7.4.0 file); connector and part inventory — SOURCE-DERIVED; layout — PARTIAL in the source (2 390 airwires), BETA in `beta/pcb/MAIN_BOARD/` (0 unconnected, 1 049 DRC items dispositioned); layer plots and 3-D renders — SOURCE-DERIVED / BETA (KiCad conversion, no component models); stack-up — PARTIAL (layer order from the DRU) with a PROPOSED fabrication proposal; BOM — PARTIAL (0 MPN in the source; BETA proposals with confidence classes); rev. B host interface — PROPOSED DESIGN (chapter 9). Nothing in this chapter is hardware-verified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/MAIN_BOARD.md`; `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §1–2; `engineering/ELECTRICAL/schematics/MAIN_BOARD/` (renders + `sheets.json`); `engineering/PCB/MAIN_BOARD/README.md`, `STACKUP.md`; `beta/pcb/MAIN_BOARD/README.md`, `FAB_NOTES.md`, `BOM_MAIN_BOARD_beta.csv`; `engineering/SYSTEM/interfaces/interconnection_table.md`; `docs/SYSTEM/BLOCK_DIAGRAM.md` (K1–K8).

## 4.1 Role and key parts

The Main Board carries the complete digital and RF core of the radar head: the Artix-7 FPGA, the STM32F7 controller, the 500 MSPS ADC and the DAC, the four ADAR1000 beamformer ICs with sixteen ADTR1107 front-end modules, the two LTC5552 mixers, the PA bias/sense circuitry for sixteen external PA boards, and all power-entry connectors from the Power Board. It is the largest board of the set: **260 × 300 mm, 10 copper layers**, EAGLE 7.4.0 schematic and board, 776 physical parts, 625 nets, 2 893 vias (source: `docs/PCB/MAIN_BOARD.md` §1).

Key ICs — deviceset names from the schematic; the MPN status of every line is UNVERIFIED (source: `docs/PCB/MAIN_BOARD.md` §1):

| Function | Part (refdes) | Qty | Note |
|---|---|---|---|
| FPGA | XC7A50T-2FTG256I (U42) | 1 | conflict K1: README/XDC name an XC7A100T (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` K1) |
| MCU | STM32F746ZGT7 (U2) | 1 | HSE crystal NX3225GD-8MHZ on board vs. 25 MHz in firmware — K2 |
| ADC | AD9484BCPZ-500 (U1) | 1 | |
| DAC | AD9708AR (U3) | 1 | |
| Beamformer | ADAR1000ACCZN | 4 | |
| T/R front end | ADTR1107ACCZ | 16 | |
| Mixers | LTC5552IUDBTRMPBF (U5, U13) | 2 | |
| IF amplifiers | AD8352ACPZ-R7 | 2 | `EN_OPAMP_IF_1/2` are single-pin nets (ENB floating) |
| RF switches | M3SWA2-34DR+ | 17 | |
| PA current sense | INA241A3IDGKR | 16 | |
| Temperature ADC | ADS7830IPWR | 3 | |
| PA gate-bias DACs | DAC5578SRGET (U7, U69) | 2 | thermal-pad pins missing from the symbol — see §4.4 |
| Bias op-amps | OPA4703EA/250 | 4 | |
| Config flash | MT25QL01GBBB8E12 (U9) | 1 | |
| Power module | EP4RKU+ (U16) | 1 | |
| USB 3.0 FIFO | FT601Q-B-T (U6) | 1 | **0 of 77 pins connected** in the schematic — K3, see §4.8 |
| Connectors | SMA 142-0731-211 ×37, Molex 22-23-20xx ×56, mini-USB X53 | — | |

Parts whose datasheets are in `7_Components Datasheets` but which are *not* on this schematic: FT2232H, FT232RN, MAX20029, STUW81300, QPM1021, QPA1013, TGA2623 (source: `docs/PCB/MAIN_BOARD.md` §1).

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §1):

| Item | Count |
|---|---|
| Sheets | 4 |
| Parts (all) / physical | 1955 / 776 |
| Nets | 625 |
| Pin connections | 4456 |
| Single-pin nets | 3 |
| Unconnected pins on placed gates | 280 |
| Physical parts without value | 244 |
| Board airwires (unrouted connections, layer 19) | 2390 |
| Missing symbol/footprint records | 0 |

## 4.2 Connectors

The connection report lists 117 connector parts (source: `engineering/ELECTRICAL/connection_diagrams/MAIN_BOARD_connection_report.md` §2; the table below groups them by function, nets as in the report; pin order of the Molex symbols is UNVERIFIED because all pads are named `S` — source: `engineering/SYSTEM/interfaces/interconnection_table.md` header).

| Group | Refdes | Package | Nets (signal pins; GND omitted) | Sheet |
|---|---|---|---|---|
| Clock inputs (SMA) | J1 | 142-0731-211 | `FPGA_SYS_CLOCK` | 2 |
| | J18 | 142-0731-211 | `FPGA_DAC_CLOCK` | 2 |
| | J20 | 142-0731-211 | `DAC_CLOCK` | 3 |
| Differential clock inputs | J19 | CJT-T-P-HH-ST-TH1 | `FPGA_ADC_CLOCK_P/N` | 2 |
| | J21 | CJT-T-P-HH-ST-TH1 | `N$2_P/N` (ADC clock) | 3 |
| LO inputs (SMA) | J22, J23 | 142-0731-211 | `N$24` (LO RX), `N$23` (LO TX) — assignment per `interconnection_table.md` §6 | 3 |
| Element RF ports (SMA, 16 pairs) | J24–J55 | 142-0731-211 | unnamed nets `N$128…N$204`, one pair per RF switch; pairing J27/J26 = PA1 … J51/J50 = PA16 (source: `interconnection_table.md` §7); which SMA of a pair is TX-out vs RX-return is UNVERIFIED | 3 |
| Synth control | JP1 | PINHD-2X6 | `AD9523_PD, _REF_SEL, _SYNC, _RESET, _CS, STM32_SCLK4/MOSI4/MISO4, AD9523_STATUS0/1, _EEPROM_SEL` | 2 |
| | JP13 | PINHD-2X7 | `STM32_MISO4/SCLK4/MOSI4`, `ADF4382_TX_*`, `ADF4382_RX_*` (CS, CE, DELSTR, DELADJ, LKDET) | 2 |
| SWD debug | JP2 | PINHD-1X6 | `+3V3, STM32_SWCLK, STM32_SWDIO, STM32_NRST, STM32_SWO` | 2 |
| FPGA JTAG | JP3 | PINHD-2X4 | `N$32, +3V3_FPGA, N$33, N$34, N$36` | 2 |
| Cooling / PA enable | JP4, JP10 | PINHD-1X3 | `EN/DIS_COOLING`, `EN/DIS_RFPA_VDD` | 2 |
| Temperature sensors | JP5, JP6, JP11, JP12, JP14, JP15, JP16, JP19 | PINHD-1X3 | `+3V3_AN4_F` + one analogue net each (`N$295…N$307`) | 4 |
| I2C3 modules | JP7 (1×8), JP18 (1×4) | PINHD | `+3V3, STM32_SCL3, STM32_SDA3, MAG_DRDY, ACC_INT, GYR_INT` / `STM32_SDA3, STM32_SCL3, +3V3` | 2 |
| UART5 (GPS) | JP8 | PINHD-1X4 | `+3V3, STM32_TX5, STM32_RX5` | 2 |
| Stepper | JP9 | PINHD-1X4 | `STEPPER_CW+, STEPPER_CLK+` | 2 |
| USART3 console | JP17 | PINHD-1X3 | `STM32_TX3, STM32_RX3` | 2 |
| Clock test | JP20 | PINHD-1X2 | `FPGA_CLOCK_TEST` | 2 |
| Enable bus to Power Board | SV1 | MA10-2 (20-way) | 15 × `EN_+…` rails (`EN_+1V0_FPGA … EN_+5V0_PA1`) | 2 |
| Power inputs (2-pin Molex) | X1, X4–X22, X24, X54–X56 | 22-23-2021 | one rail each: `+3V4, +3V3_ADTR, +5V0_PA_2, -3V3_SW, +5V0_PA_3, +1V0_FPGA, +3V3_AN, +1V8_FPGA, -3V4, +3V3_VDD_SW, -5V0_ADAR12, +5V0_PA_1, -5V0_ADAR34, +3V3_FPGA, +1V8_CLOCK, +5V0_0, -5V5_PA, +3V3_ADAR12, +3V3_ADAR34, +3V3, +5V5_PA` | 1 |
| PA gate bias outputs | X_1 … X_16 | 22-23-2021 | `VG_15, VG_13, VG_7, VG_5, VG_9, VG_11, VG_1, VG_3, VG_14, VG_16, VG_6, VG_8, VG_12, VG_10, VG_4, VG_2` (in refdes order X_1…X_16) | 4 |
| PA drain-current sense inputs | X3, X38–X52 | 22-23-2031 | one differential pair each (`N$207/N$209` … `N$286/N$287`) | 4 |
| Host USB | X53 | MINI-USB 32005-201 | `STM32_USB_FS_D_N, _D_P, _ID` (VBUS not connected) | 2 |

The cable-level use of these connectors (which Power Board output feeds which input, which Synth SMA drives J1/J18/J19/J20/J22/J23) is in chapter 3 and in `engineering/SYSTEM/interfaces/interconnection_table.md` §2–§8.

## 4.3 Schematic sheets

The four sheets were rendered from `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` with `tools/render_eagle_schematic.py` + `tools/svg_sheets_to_pdf.py` (PDF: `engineering/ELECTRICAL/schematics/MAIN_BOARD/MAIN_BOARD_schematic.pdf`; sheet sizes and part/net counts per sheet in `engineering/ELECTRICAL/schematics/MAIN_BOARD/sheets.json`). Sheet names are those stored in the EAGLE file (source: `docs/PCB/MAIN_BOARD.md` §1). Sheet 3 is 1 904 × 1 652 mm at 1:1 and must be read from the SVG/PDF for pin-level detail.

![Figure 10 — F4.1 — Main Board schematic sheet 1 "POWER SUPPLIES": 189 parts, 33 nets (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet1.png)

![Figure 11 — F4.2 — Main Board schematic sheet 2 "Digital (FPGA+microcontroller)": 196 parts, 181 nets (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet2.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet2.png)

![Figure 12 — F4.3 — Main Board schematic sheet 3 "RF": 1 304 parts, 356 nets — ADAR1000 ×4, ADTR1107 ×16, mixers, switches, 32 element SMAs (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet3.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet3.png)

![Figure 13 — F4.4 — Main Board schematic sheet 4 "RF POWER AMPLIFIER BIAS": DAC5578 ×2, OPA4703 ×4, INA241A3 ×16, VG outputs X_1…X_16, sense inputs X3/X38…X52 (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet4.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/MAIN_BOARD/png/MAIN_BOARD_schematic_sheet4.png)

Schematic-level findings that no layout work can close (source: `docs/PCB/MAIN_BOARD.md` §2; `beta/pcb/MAIN_BOARD/README.md` §3): FT601 U6 supply/control pins unconnected (board-only signals `AVDD, VBUS, VCC33…, VCCIO…, VDDA` are forward-annotation residue); 280 unconnected symbol pins; single-pin nets `N$44` (AD9484 CML), `EN_OPAMP_IF_1`, `EN_OPAMP_IF_2`; XADC wiring VP/VN/VREFN to GND and VREFP to `+1V0_FPGA` (to be checked against AMD UG480); 4 approved ERC entries on `STM32_MISO_1V8`. The full list is in `engineering/ELECTRICAL/netlists/MAIN_BOARD_unresolved_connections.md`.

## 4.4 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 7.4.0)

| Item | Finding (source: `docs/PCB/MAIN_BOARD.md` §2) |
|---|---|
| Airwires | 2 390 stored on layer 19: GND 2 354, `+3V3_FPGA` 33, `+3V3_FT` 3 (entirely unrouted). GND has polygons on layers 2, 5, 13, 15 — whether `RATSNEST` clears the GND airwires REQUIRES VERIFICATION IN EAGLE |
| Parts outside outline | 11: C159, C184, C185, C186, L19 (FT601 decoupling), R60, R61, R83, R84, R145, R146 (parked at x = 0.1 mm, y < 0) |
| DRC | 211 `<approved>` entries (EAGLE stores no text) |
| ERC | 4 approved entries on net `STM32_MISO_1V8` |
| Layer-count mismatch | DRU name says 8 layers; 10 copper layers are defined and all carry copper (L1 7 619 objects, L2 1, L3 18, L4 9, L5 1, L12 587, L13 1, L14 395, L15 5, L16 1 605) |
| Via drills | 0.15 mm ×1 045, 0.2 ×1 367, 0.3 ×332, 0.35 ×113, 0.5 ×21, 0.6 ×7, 1.0 ×4, 1.2 ×4 (all through 1-16; no blind/buried) |
| Min track | 0.1 mm (3 408 wires); 0.204 mm RF width ×2 729 (matches the PCBWay 50 Ω note) |
| USB 3.0 | FT601 unconnected; the only host link is STM32 USB-FS (PA11/PA12 → X53) |

### Engineering conversion (`engineering/PCB/MAIN_BOARD/`, KiCad 10.0.6 import)

Cross-check of the EAGLE XML against the KiCad conversion (source: `engineering/PCB/MAIN_BOARD/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 260.0 | 260.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 784 | 784 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 2893 | 2893 | OK |  |
| Tracks (signal wires excl. airwires) | 10219 | 10219 | OK |  |
| Copper layers | 10 | 10 | OK |  |
| NPTH holes (free holes + package holes) | 10 | 10 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 3314 | 3314 | OK |  |

DRC on the conversion with EAGLE-DRU-derived rules: 912 violations, 15 unconnected (source: `engineering/PCB/MAIN_BOARD/README.md` §6):

| Rule | Count | Interpretation |
|---|---|---|
| `solder_mask_bridge` | 199 | mask web between adjacent pads thinner than KiCad default (EAGLE has no such rule) — fabricator decision |
| `silk_overlap` | 199 | overlapping silkscreen texts/lines — cosmetic |
| `silk_over_copper` | 199 | silk over exposed copper — cosmetic/assembly |
| `track_dangling` | 136 | track end not connected — review (stubs or unfinished routing) |
| `shorting_items` | 93 | copper of different nets touching after conversion (typically EAGLE polygon vs unnamed copper) — REVIEW in EAGLE |
| `clearance` | 63 | copper clearance < DRU — review |
| `via_dangling` | 15 | via connected on one layer only — review |
| `hole_clearance` | 4 | hole to copper clearance (KiCad rule, no EAGLE equivalent) |
| `silk_edge_clearance` | 3 | silk too close to edge |
| `zones_intersect` | 1 | overlapping pours of different priority — conversion artefact or design issue |

Counts of exactly 199 are lower bounds (KiCad report cap).

### BETA board (`beta/pcb/MAIN_BOARD/`)

Before/after table (source: `beta/pcb/MAIN_BOARD/README.md` §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 15 | 0 |
| clearance | 63 | 72 |
| hole_clearance | 4 | 87 |
| shorting_items | 93 | 125 |
| silk_edge_clearance | 3 | 3 |
| silk_over_copper | 199 | 199 |
| silk_overlap | 199 | 199 |
| solder_mask_bridge | 199 | 199 |
| track_dangling | 136 | 130 |
| via_dangling | 15 | 35 |
| zones_intersect | 1 | 0 |
| **DRC violations total** | 912 | 1049 |

What was changed in BETA — nothing in the netlist, every step logged (source: `beta/pcb/MAIN_BOARD/README.md` §2): 7 arc tails where EAGLE arcs end on a pad centre (`fixes_stubs.json`); the `+3V3_FT` input filter L19/C159/C184/C185/C186 moved from outside the outline to (5…12, −232…−240) mm next to X16 (`placement_moves.json`); hand routing of that cluster with 4 GND vias 0.45/0.20 mm, a 0.3 mm `+3V3_FT` bus and a 0.5 mm `+3V3_FPGA` feed to X16.1 (`manual_routing.json`, `bridges.json`); 14 of 30 net-less footprint copper polygons (BPF2 filters, U13, U5) re-created as board-level polygons with the net they touch (`POLYGON_NET_DISPOSITION.md`); same-net zone priorities. R60, R61, R83, R84, R145, R146 (33 Ω 0201, no net on either pin) stay outside the outline and are `dnp = yes` in the BETA BOM.

Why the total went *up* although 15 → 0 unconnected: the remaining 1 049 items are dominated by copper that the schematic cannot describe (source: `beta/pcb/MAIN_BOARD/README.md` §3):

| Type | Count | Disposition |
|---|---|---|
| shorting_items | 125 | REAL (schematic): GND tracks/arcs run through the thermal-via pads `V…V_8` of U69 (DAC5578) and U7 — those pads have no net because the symbols have no paddle pin; EAGLE connected them with the GND polygon. Also the 4 ambiguous BPF2 polygons (GND + RF net) and KK headers JP7/JP8/JP10/JP17. Not changed in BETA → designer must add the paddle pins to the symbols or confirm the intended net |
| hole_clearance / clearance | 87 / 72 | same U69/U7 no-net via pads and the 4 ambiguous BPF2 polygons; plus 3 at ADAR1_0/ADAR3_0/J33 from the source |
| track_dangling | 130 | EAGLE stub ends inside pours/pads — cosmetic, copper not modified |
| via_dangling | 35 | 20 vias of RF_TX/RF_RX/RF_TX_FIL/RF_RX_FIL inside the BPF2 pads + 15 from the source (ADAR load/enable nets) |
| silk_overlap / silk_over_copper / solder_mask_bridge | 199+ each | cosmetic / fab CAM (0201 density) |
| silk_edge_clearance | 3 | X53 outline and JP3 reference at the board edge — cosmetic |

## 4.5 Layer plots and 3-D renders

Composite top and bottom views (copper + silkscreen + outline) of the engineering conversion. Per-layer plots (F.Cu, In1…In8, B.Cu) are listed as files in chapter 14, not reproduced here.

![Figure 14 — F4.5a — Main Board top composite (F.Cu + F.SilkS + Edge.Cuts) of the KiCad conversion of RADAR_Main_Board.brd, 260 × 300 mm (status: SOURCE-DERIVED; source: engineering/PCB/MAIN_BOARD/svg/MAIN_BOARD_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/MAIN_BOARD_top_composite.png)

![Figure 15 — F4.5b — Main Board bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts) (status: SOURCE-DERIVED; source: engineering/PCB/MAIN_BOARD/svg/MAIN_BOARD_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/MAIN_BOARD_bottom_composite_mirrored.png)

![Figure 16 — F4.6a — Main Board 3-D render, top, KiCad conversion; no component models (STEP is board-only) (status: SOURCE-DERIVED; source: engineering/PCB/MAIN_BOARD/3d/MAIN_BOARD_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/MAIN_BOARD/3d/MAIN_BOARD_render_top.png)

![Figure 17 — F4.6b — Main Board BETA board, isometric render after the +3V3_FT cluster placement and routing (status: BETA; source: beta/pcb/MAIN_BOARD/exports/3d/MAIN_BOARD_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/MAIN_BOARD/exports/3d/MAIN_BOARD_render_isometric.png)

Assembly drawings: the generated `engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf` and `beta/pcb/MAIN_BOARD/exports/drawings/MAIN_BOARD_assembly_top.pdf` exist (F.Fab + F.SilkS + Edge.Cuts, black and white), but when rendered with `pdftoppm -png -r 110` the A4 page frame plotted by `kicad-cli pcb export pdf --sp` contains only the parts parked outside the outline; the board body itself (at negative y in the KiCad coordinate frame) lies outside the page. The same applies to the Power Supply, Frequency Synthesizer and RF PA assembly PDFs. These PDFs are therefore not used as figures in this manual; the planned figure F4.7 is replaced by the top composite F4.5a (which carries F.SilkS and F.Fab reference designators) until the pipeline plots the drawing without the page frame (open item in chapter 17).

## 4.6 Stack-up

Layer order and copper thickness come from the EAGLE DRU `PCBWay_8L_100um-Track` (the name says 8 layers; the board uses 10). Dielectric thicknesses are the EAGLE DRU table, not a vendor stack-up; total thickness is not defined in the source (KiCad assumed 1.6 mm) (source: `engineering/PCB/MAIN_BOARD/STACKUP.md`, status PARTIAL):

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 0.102mm |
| 2 | 2 | In1.Cu | 0.035mm | 0.2mm |
| 3 | 3 | In2.Cu | 0.035mm | 0.2mm |
| 4 | 4 | In3.Cu | 0.035mm | 0.2mm |
| 5 | 5 | In4.Cu | 0.035mm | 0.2mm |
| 6 | 12 | In5.Cu | 0.035mm | 0.15mm |
| 7 | 13 | In6.Cu | 0.035mm | 0.2mm |
| 8 | 14 | In7.Cu | 0.035mm | 0.2mm |
| 9 | 15 | In8.Cu | 0.035mm | 0.102mm |
| 10 | 16 | B.Cu | 0.035mm | — |

PROPOSED fabrication stack-up (BETA, nothing confirmed by the designer or PCBWay; source: `beta/pcb/MAIN_BOARD/FAB_NOTES.md` §2): outer layers 1 and 9 on **Rogers RO4350B 4 mil (0.102 mm)** as the impedance layers, FR-4 cores/prepregs inside; dielectric sum 1.554 mm + 10 × 35 µm copper ≈ 1.9 mm → PROPOSED finished thickness **2.0 mm ± 10 %** (the DRU sum does not fit 1.6 mm). Materials/finish proposal (`FAB_NOTES.md` §3): 1 oz copper all layers, ENIG, green LPI mask with **no mask over RF traces** on the RF layer, white silk, min track/space 0.10/0.10 mm, min drill 0.15 mm, copper-to-edge 0.3 mm, IPC-A-600 Class 2, 100 % electrical test with the supplied IPC-D-356 netlist. Controlled impedance targets with the geometry measured on the KiCad board (`FAB_NOTES.md` §4): 50 Ω single-ended at w = 0.204 mm (2 729 segments); 100 Ω differential at w = 0.204 mm / s = 0.26 mm (`FPGA_ADC_CLOCK`, `MIX_RX`), `ADC_CLK_IN` s = 0.288 mm, `AMP_IF_IN` uncoupled (s = 1.58 mm). The impedance note itself (`4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf`) is a Frequency Synthesizer document; its applicability to this board is an assumption of the proposal — if the Main Board is built on plain FR-4 the 0.204 mm lines are not 50 Ω.

## 4.7 BOM summary

Source BOM (`docs/BOM/BOM_MAIN_BOARD.csv`, generated from the schematic): 776 references, 98 line items, **0 MPN attributes**, 244 references without value (source: `docs/BOM/README.md` §Summary). The BETA BOM `beta/pcb/MAIN_BOARD/BOM_MAIN_BOARD_beta.csv` adds `manufacturer, mpn, mpn_confidence, dnp, note` columns with proposed part numbers (`beta/pcb/tools/beta_bom_mpn.py`). Confidence count obtained with

`python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/MAIN_BOARD/BOM_MAIN_BOARD_beta.csv'))))"`

| mpn_confidence | Lines | Meaning (source: `beta/pcb/README.md` §BOM confidence) |
|---|---|---|
| HIGH | 23 | deviceset name is an orderable MPN |
| MEDIUM | 41 | standard passive proposed from value + package |
| LOW | 30 | guess / non-standard value / package-value conflict |
| EMPTY | 4 | no value in the source |
| **Total** | **98** | quantities 204 / 461 / 93 / 18 (same source) |

Flagged conflicts that the designer must resolve before purchase (source: `beta/pcb/README.md`): non-E-series values (2.443 kΩ, 103 pF, 107.3 nH), 47 µF in 0201, NX3225 footprint with a 32.768 kHz value, 5 mΩ shunt with a 0.1 Ω part number; the 37 SMA and 56 Molex connectors to be confirmed as production parts (many are test/interconnect points); FT601 and its 7 parked passives marked DNP or wired; INA241A3 ×16 and OPA4703 ×4 confirmed for the Nexus variant (source: `docs/PCB/MAIN_BOARD.md` §8).

## 4.8 Rev. B host interface (FT601)

The source Main Board has no usable high-speed host path: U6 (FT601Q-B-T) is placed but none of its 77 pins is connected, and the only host link is the STM32 USB full-speed port on X53 (source: `docs/PCB/MAIN_BOARD.md` §1–2; conflict K3 in `docs/SYSTEM/BLOCK_DIAGRAM.md`). Chapter 9 documents the two proposed options: option A — wire the FT601 to free FPGA bank-35 pins (47 signals, pin plan `engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv`, XDC fragment `ft601_bank35.xdc`, added parts `ft601_added_parts_BOM.csv`) in a **Main Board rev. B**; option B — the SPI bridge frame through the STM32 CDC link, implemented end-to-end in simulation (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §7).

The rev. B board package is `beta/pcb/MAIN_BOARD_REVB/` (status **BETA PROPOSAL — explicit netlist change, partially routed, DRC-checked, not reviewed by the original designer, not fabricated**; source: `beta/pcb/MAIN_BOARD_REVB/README.md`). It was derived from the rev. A BETA board with `beta/pcb/tools/beta_revb_ft601.py` and the design input of `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §4. **The EAGLE schematic has not been changed and no longer matches this board**: the designer must enter the connections of `NETLIST_DELTA.csv` (README §3) and the added parts (README §4) in the schematic, verify them against the FT601 datasheet (not in the repository) and re-annotate before any rev. B layout is released (same source, header note).

State of the rev. B board (source: `beta/pcb/MAIN_BOARD_REVB/README.md` §1):

| Check | Rev. A BETA (`MAIN_BOARD/`) | Rev. B after netlist change, before routing | Rev. B after routing (exports) |
|---|---|---|---|
| unconnected_items | 0 | 129 | 59 |
| **DRC total** | 1049 | 1055 | 1071 |

Of the 64 new nets, 17 are routed and connected (USB D±, both SuperSpeed RX lines, SSTX_N and both SSTX_C lines, CC1/CC2, USB_VBUS, FT_VBUS_DET, FT_RREF, FT_XI, FT_GPIO1, partly `+3V3_FT`/`FT_VD10`/`FT_AVDD`/`FT_XO`). **The 32-bit FIFO bus and its control lines (46 of 47 FPGA-side signals) are not routed**: 36 of the 47 bank-35 balls of U42 (XC7A50T FTG256, 1.0 mm pitch) have no free position for an escape via because the dog-bone positions are occupied by the existing BGA fan-out; routing the bus requires re-doing the U42 bank-35 breakout (same source; list in `beta/pcb/MAIN_BOARD_REVB/UNROUTED.md`, 59 open items all on rev. B nets). New DRC items from rev. B copper: 9 `track_width` neck-downs (0.075 mm, to be widened to 0.1 mm), 2 courtyard overlaps (Y_FT ↔ C_XI/C_XO), 1 copper-edge clearance at the J_USB3 NPTH peg, 5 dangling vias; the USB differential pairs were routed as single traces by Freerouting and must be re-routed coupled (0.204/0.18 mm) before release (README §1–§2). Added parts (README §4): USB-C receptacle J_USB3 Amphenol 12401610E4#2A (SS lane wired in one orientation only — VERIFY), 2 × TPD4E05U06 ESD arrays, 2 × 100 nF SSTX coupling capacitors, 2 × 5.1 kΩ CC resistors, VBUS divider 10 k/3.3 k, RREF 3.24 kΩ, 4 × 4.7 µF VD10 decoupling, AVDD ferrite + 100 nF + 1 µF, 30 MHz crystal ABM8 with 2 × 18 pF — every value carries a VERIFY note against the FT60x datasheet. `BOM_MAIN_BOARD_REVB_beta.csv` has 110 lines (97 rev. A, 12 new rev. B, 1 rev. A part now wired; counted from the CSV `revision` column). Full export package in `beta/pcb/MAIN_BOARD_REVB/exports/` (all 24 export steps exit 0 per `exports/EXPORT_LOG.md`). Procedures, pin plan and the bridge-frame alternative: chapter 9.

![Figure 18 — F4.7 — Main Board rev. B proposal, isometric render: USB-C receptacle J_USB3 on the left edge next to U6 (FT601), ESD arrays, crystal and decoupling in the band below U6; FIFO bus to bank 35 unrouted (status: BETA; source: beta/pcb/MAIN_BOARD_REVB/exports/3d/MAIN_BOARD_REVB_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/MAIN_BOARD_REVB/exports/3d/MAIN_BOARD_REVB_render_isometric.png)

The rev. B netlist delta is the only schematic-level change proposed for this board; it is a PROPOSED DESIGN / BETA and not part of the ORIGINAL PROJECT FILE set.

## 4.9 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K1 | FPGA part: XC7A50T-2FTG256I in CAD vs XC7A100T in README/XDC | OPEN — hardware designer | `docs/SYSTEM/BLOCK_DIAGRAM.md` |
| K2 | STM32 HSE: 8 MHz crystal on board vs 25 MHz in firmware (beta firmware assumes 8 MHz) | OPEN | same; `docs/AERIS10_BETA_ENGINEERING_REPORT.md` |
| K3 | Host data path: FT601 unwired (option A rev. B / option B bridge) | OPEN — system architect | chapter 9 |
| — | Rev. B: FIFO bus (46 of 47 FPGA-side signals) unrouted — U42 bank-35 breakout must be redone; USB pairs to be re-routed coupled; EAGLE schematic not updated | OPEN — designer | `beta/pcb/MAIN_BOARD_REVB/README.md` §1, `UNROUTED.md` |
| — | 2 390 EAGLE airwires; `RATSNEST` behaviour on the GND polygons REQUIRES VERIFICATION IN EAGLE | OPEN | `docs/PCB/MAIN_BOARD.md` §2 |
| — | 125 shorting items from net-less thermal-via pads of U7/U69 and 4 ambiguous BPF2 polygons — symbol/footprint fix needed | OPEN — designer | `beta/pcb/MAIN_BOARD/README.md` §3 |
| — | 10-layer stack-up: DRU named for 8 layers; material, thickness, finish, impedance UNVERIFIED (G-01) | BLOCKED — MISSING DATA | `engineering/PCB/MAIN_BOARD/STACKUP.md`; MDR-07 |
| — | BOM: 0/98 lines with a verified MPN; 244 value-less references | OPEN | `docs/BOM/README.md` |
| — | XADC reference wiring; single-pin nets `N$44`, `EN_OPAMP_IF_1/2`; 280 unconnected symbol pins | OPEN | `engineering/ELECTRICAL/netlists/MAIN_BOARD_unresolved_connections.md` |
| — | Generated assembly-drawing PDFs clipped by the A4 page frame (§4.5) | OPEN — tooling | this chapter |
| — | 211 approved DRC entries in the source without justification text | OPEN | `docs/PCB/MAIN_BOARD.md` §2 |

Acceptance criteria for calling this board layout-complete are copied in chapter 14 (`docs/PCB/MAIN_BOARD.md` §10). Do not declare this board fabrication-ready on the basis of the existing `.sch/.brd` files or of the BETA package.


---

<!-- chapter 5: Power Board -->
# 5. Power Supply Board (PowerBoard)

**Chapter status summary:** schematic — SOURCE-DERIVED (EAGLE 9.6.2 schematic rendered); connector inventory — SOURCE-DERIVED; layout — PARTIAL in the source (309 airwires, 132 of 312 parts parked outside the outline, sch/brd version mismatch) and BETA in `beta/pcb/POWER_SUPPLY/` (308 → 89 unconnected, placement by script not reviewed); layer plots and renders — SOURCE-DERIVED / BETA; stack-up — PARTIAL (2-layer, 1.5 mm core from the DRU) with a PROPOSED fabrication note; BOM — PARTIAL (0 MPN in the source). The 22 V PA drain supply does not exist on this board (K4) — see chapter 9. Nothing is hardware-verified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/POWER_SUPPLY.md`; `engineering/ELECTRICAL/connection_diagrams/POWER_SUPPLY_connection_report.md` §1–2; `engineering/ELECTRICAL/schematics/POWER_SUPPLY/`; `engineering/PCB/POWER_SUPPLY/README.md`, `STACKUP.md`; `beta/pcb/POWER_SUPPLY/README.md`, `UNROUTED.md`, `FAB_NOTES.md`, `BOM_POWER_SUPPLY_beta.csv`; `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` (G-10).

## 5.1 Role and key parts

The Power Board converts the single DC input `Vin [12-17] V` (silkscreen label; source: `docs/PCB/POWER_SUPPLY.md` §1) into the 24 rails consumed by the Main Board and the Frequency Synthesizer, each rail leaving the board on its own 2-pin Molex KK connector, and receives the 15-line enable bus from the STM32 on the 20-way header SV1. Board: **280 × 300 mm, 2 copper layers**, EAGLE schematic 9.6.2 / board 7.4.0 (version mismatch), 312 physical parts, 156 nets, 346 vias, DRU `PCBWay_2L_100um-Track` with a 1.5 mm core (source: `docs/PCB/POWER_SUPPLY.md` §1).

Key ICs (deviceset names, MPN UNVERIFIED; source: `docs/PCB/POWER_SUPPLY.md` §1):

| Function | Part | Qty | Note |
|---|---|---|---|
| Buck regulators | TPS562208DDCT | 21 | datasheet folder contains TPS562201 instead — datasheet to be added |
| LDO | ADM7151ACPZ-04-R7 | 6 | |
| LDO | TPS7A8300RGRR | 2 | feedback-select pins without net (24 unconnected pins, see §5.3) |
| Inverters | LM2662MX/NOPB | 5 | datasheet folder has LM2663 |
| Tantalum capacitors | T521W476M020ATE045 | 10 | |
| Rail outputs | Molex 22-23-2021 | 34 | |
| DC input | AK300/2 (X1) | 1 | `VIN`, `GND` |
| Not on the board | MAX20029 | — | datasheet present, part absent |

Rails present as silkscreen labels (layer 51; source: `docs/PCB/POWER_SUPPLY.md` §1): `+5V5_PA, -5V5_PA, +1V8_CLOCK, +3V3_CLOCK, +3V3_VDD_SW, +5V0_PA_1/2/3, -3V3_SW, +3V3_SW, +3V3_ADTR, -5V0_ADAR12, -5V0_ADAR34, +3V4, -3V4, +3V3_LO, +5V0_ADAR, +3V3_ADAR_12, +3V3_ADAR_34, +5V0_0, +1V8_FPGA, +1V0_FPGA, +3V3, +3V3_FPGA, +3V3_AN`, 12 × `EN`. The 16 `EN_*` nets match the STM32 enable GPIOs PE7…PE15, PG0…PG5 (same source). The design input for rail currents is `3_Power Management/Power Management V6.xlsx` (sheet `Feuil1`); it budgets 16 × QPA2962 at +22 V / 2 A, a rail this board does not have — K4 (source: `docs/PCB/POWER_SUPPLY.md` §2; `docs/SYSTEM/BLOCK_DIAGRAM.md`).

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/POWER_SUPPLY_connection_report.md` §1):

| Item | Count |
|---|---|
| Sheets | 1 |
| Parts (all) / physical | 562 / 312 |
| Nets | 156 |
| Pin connections | 1061 |
| Single-pin nets | 0 |
| Unconnected pins on placed gates | 24 |
| Physical parts without value | 80 |
| Board airwires (unrouted connections, layer 19) | 309 |
| Missing symbol/footprint records | 0 |

## 5.2 Connectors

36 connector parts (source: `engineering/ELECTRICAL/connection_diagrams/POWER_SUPPLY_connection_report.md` §2; every Molex output carries the named rail on one pad and `GND` on the other, pad order UNVERIFIED):

| Refdes | Package | Rail / signal |
|---|---|---|
| X1 | AK300/2 | `VIN` (12–17 V input) |
| SV1 | MA10-2 (20-way) | `EN_+1V0_FPGA, EN_+5V0_PA2, EN_+1V8_FPGA, EN_+5V0_PA3, EN_+3V3_FPGA, EN_+5V5_PA, EN_+5V0_ADAR, EN_+1V8_CLOCK, EN_+3V3_ADAR12, EN_+3V3_CLOCK, EN_+3V3_ADAR34, EN_+3V3_ADTR, EN_+3V3_SW, EN_+3V3_VDD_SW, EN_+5V0_PA1` (15 enables + GND) |
| X2 | 22-23-2021 | `+5V0_1` |
| X3 | 22-23-2021 | `+5V5_PA` |
| X4 | 22-23-2021 | `+1V0_FPGA` |
| X5 | 22-23-2021 | `+1V8_FPGA` |
| X6 | 22-23-2021 | `+5V0_LO` |
| X7 | 22-23-2021 | `+3V3_LO_2` |
| X8 | 22-23-2021 | `+3V3_LO_1` |
| X9 | 22-23-2021 | `+5V0_2` |
| X10 | 22-23-2021 | `+1V8_CLOCK` |
| X11 | 22-23-2021 | `+3V3_CLOCK` |
| X12 | 22-23-2021 | `+3V3_AN` |
| X13 | 22-23-2021 | `+5V0_ADAR` |
| X14 | 22-23-2021 | `+3V3_ADAR_12` |
| X15 | 22-23-2021 | `+3V3_ADAR_34` |
| X16 | 22-23-2021 | `+3V3` |
| X17 | 22-23-2021 | `+5V0_3` |
| X18 | 22-23-2021 | `-3V3_SW` |
| X19 | 22-23-2021 | `-5V5_PA` |
| X20 | 22-23-2021 | `-5V0_ADAR34` |
| X21 | 22-23-2021 | `-5V0_ADAR12` |
| X22 | 22-23-2021 | `+5V0_0` |
| X23 | 22-23-2021 | `+3V4` |
| X24 | 22-23-2021 | `-3V4` |
| X25 | 22-23-2021 | `+5V0_4` |
| X26 | 22-23-2021 | `+5V0_ADTR` |
| X27 | 22-23-2021 | `+3V3_FPGA` |
| X28 | 22-23-2021 | `+5V0_5` |
| X29 | 22-23-2021 | `+3V3_SW` |
| X30 | 22-23-2021 | `+3V3_VDD_SW` |
| X31 | 22-23-2021 | `+5V0_PA_1` |
| X32 | 22-23-2021 | `+5V0_PA_2` |
| X33 | 22-23-2021 | `+5V0_PA_3` |
| X34 | 22-23-2021 | `+3V3_ADTR` |
| X35 | 22-23-2021 | `+3V3_XO` |

Which output feeds which Main Board / Synthesizer input is the subject of `engineering/SYSTEM/interfaces/interconnection_table.md` §2–§4 (chapter 3). Thirteen outputs (`+5V0_1…+5V0_5`, `+3V3_LO_1/2`, `+3V3_CLOCK`, `+5V0_ADAR`, `+3V3_ADAR_12/34`, `+5V0_ADTR`, `+3V3_SW`) have no connector with the same net name on the Main or Synth board and are marked TBD in the harness schedule (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, CBL-001…CBL-028 rows with "no connector with this net name"); some are matched by meaning in the interconnection table (e.g. `+3V3_ADAR_12` → Main `+3V3_ADAR12`, CBL-07 there).

## 5.3 Schematic sheet

![Figure 19 — F5.1 — Power Board schematic, single sheet: 21 × TPS562208 buck stages, 6 × ADM7151 and 2 × TPS7A8300 LDOs, 5 × LM2662 inverters, 34 rail outputs, enable header SV1 (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/POWER_SUPPLY/png/POWER_SUPPLY_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/POWER_SUPPLY/png/POWER_SUPPLY_schematic_sheet1.png)

Schematic-level items that no layout work closes: 24 pins without net (TPS7A8300 feedback-select pins, LM2662 FC/OSC — source: `beta/pcb/POWER_SUPPLY/README.md` §3, detail in `engineering/ELECTRICAL/netlists/POWER_SUPPLY_unresolved_connections.md`); 80 references without value — the buck-stage inductors and capacitors must carry values for the TPS562208 compensation to be reproducible (source: `docs/PCB/POWER_SUPPLY.md` §8); one board-only signal `+3V3_LO` (sch/brd mismatch, source: `docs/PCB/POWER_SUPPLY.md` §2).

## 5.4 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 7.4.0 board, 9.6.2 schematic)

| Item | Finding (source: `docs/PCB/POWER_SUPPLY.md` §2) |
|---|---|
| Routing | 309 airwires across 86 of 157 signals; 72 signals entirely unrouted (all 16 `EN_*`, several `+5V0_*`, `+3V3_XO`, `+3V3_LO_1/2`) |
| Placement | 132 of 312 elements outside the 280 × 300 mm outline; mounting holes lie within 10..270 × 10..230 (+ one at y = 267.85) → the intended final outline is UNRESOLVED (G-10) |
| Version mismatch | sch 9.6.2 vs brd 7.4.0 — annotation link cannot be trusted; one board-only signal `+3V3_LO` |
| DRC | 0 approved errors (meaningless while unrouted) |
| ERC | 0 approved entries; 0 single-pin nets |
| Design-input discrepancies | xlsx budgets 16 × QPA2962 at +22 V (2 A each); the Power Board has no 22 V rail label (`Vin [12-17]V`) and the RF PA board holds one QPA2962 — PA supply architecture UNRESOLVED |

### Engineering conversion (`engineering/PCB/POWER_SUPPLY/`)

Cross-check (source: `engineering/PCB/POWER_SUPPLY/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 280.0 | 280.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 320 | 320 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 346 | 346 | OK |  |
| Tracks (signal wires excl. airwires) | 570 | 570 | OK |  |
| Copper layers | 2 | 2 | OK |  |
| NPTH holes (free holes + package holes) | 8 | 8 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 444 | 444 | OK |  |

DRC on the conversion: 160 violations, 308 unconnected (source: `engineering/PCB/POWER_SUPPLY/README.md` §6):

| Rule | Count | Interpretation |
|---|---|---|
| `clearance` | 53 | copper clearance < DRU — review |
| `silk_over_copper` | 40 | silk over exposed copper — cosmetic/assembly |
| `silk_overlap` | 22 | overlapping silkscreen texts/lines — cosmetic |
| `zones_intersect` | 21 | overlapping pours of different priority — conversion artefact or design issue |
| `drill_out_of_range` | 8 | drill smaller than DRU msDrill |
| `solder_mask_bridge` | 8 | mask web between adjacent pads thinner than KiCad default (EAGLE has no such rule) — fabricator decision |
| `track_dangling` | 4 | track end not connected — review (stubs or unfinished routing) |
| `isolated_copper` | 4 | review |

### BETA board (`beta/pcb/POWER_SUPPLY/`)

Before/after (source: `beta/pcb/POWER_SUPPLY/README.md` §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 308 | 89 |
| clearance | 53 | 56 |
| drill_out_of_range | 8 | 8 |
| isolated_copper | 4 | 0 |
| silk_over_copper | 40 | 168 |
| silk_overlap | 22 | 65 |
| solder_mask_bridge | 8 | 8 |
| track_dangling | 4 | 2 |
| via_dangling | 0 | 20 |
| zones_intersect | 21 | 1 |
| **DRC violations total** | 160 | 328 |

Unconnected items 308 → 89 (−71 %); footprints outside the outline 132 → 0. What was done, in order (source: `beta/pcb/POWER_SUPPLY/README.md` §2): netclass `Default` set to track 0.25 mm / clearance 0.2 mm / via 0.5/0.3 mm for new copper only; 110 parts placed inside the outline in 29 net clusters and 22 KK connectors placed on the nearest board edge (`beta/pcb/tools/beta_place_outside.py`, `placement_moves*.json`); Freerouting 2.5.0 pass 1 with the existing 916 tracks/vias fixed (+1 336 tracks, +168 vias; 308 → 102); 45 same-net zones re-prioritised and a board-wide B.Cu GND zone added (zones_intersect 21 → 1); 29 straight same-net bridges kept out of 102 tried (102 → 96); Freerouting pass 2 (+36 tracks, +3 vias; 96 → 96); GND stitching, 22 of 50 vias kept (96 → 89); refill, DRC, export.

**The placement by script is topological, not thermal/EMC** — regulator clusters sit where free space was nearest to their connectors; a designer must review inductor orientation, input/output capacitor proximity and heat spreading before any routing clean-up (source: `beta/pcb/POWER_SUPPLY/README.md` §3).

### The 89 open connections (`beta/pcb/POWER_SUPPLY/UNROUTED.md`)

None of the 89 could be completed without a routing decision that a script should not take (crossing other copper, moving existing tracks, re-shaping the EAGLE pours); the netlist was never changed (source: `UNROUTED.md` header). By net: **GND 49, VIN 10**, `+5V0_ADAR` 4, `+3V3_ADAR_12` 3, `+3V3_FPGA` 2, `+5V0_PA_3` 2, `+5V5_PA` 2, `+1V0_FPGA` 2, `+3V3_SW` 2, `+3V3_VDD_SW` 2, `+3V3_ADAR_34` 2, `+5V0_0` 2, `+5V0_PA_1` 2, `+3V4` 1, `+1V8_FPGA` 1, `+3V3` 1, `+3V3_AN` 1, `+5V0_PA_2` 1. Freerouting's own verdict was 45 unrouted / 23 violations after pass 1; KiCad counts more because each isolated pour island counts separately (same source).

The reasons fall into three classes (wording of the `UNROUTED.md` table):

| Class | Typical entry | What is needed |
|---|---|---|
| GND pad ↔ GND pad | e.g. U34 pads 8/18/21 at (121.0, −90…−94) | the B.Cu GND plane is fragmented by the autorouted bottom tracks; the stitching via next to the pad was reverted by DRC → manual via placement or move the bottom tracks |
| zone island ↔ zone island (same net) | e.g. `VIN` zones priority 22 ↔ 28 at (71.2, −175.9) ↔ (215.6, −208.3) | the EAGLE polygons are separate local pours joined only by airwires; Freerouting routes pins, not pours → a manual 2 mm VIN / GND bus or a redesign of the pour layout |
| pin ↔ pin unroutable | e.g. `+1V8_FPGA` tracks at (129.6, −52.7) ↔ (152.5, −49.2) | Freerouting reported the connection unroutable in both passes (2-layer, local congestion) → manual routing |
| pad/track ↔ pour | e.g. U27 pad 4 ↔ GND zone priority 23 | no DRC-clean straight path and the autorouter escape failed |

Manual closing procedure (source: `UNROUTED.md` §How to close them): open `POWER_SUPPLY.kicad_pcb`, Inspect → Design Rules Checker → *Run DRC*, use the *Unconnected Items* tab; route 2.0 mm (VIN) / 1.0 mm (other rails) tracks between pours or extend a pour outline, then *Refill zones*; add 0.6/0.3 mm GND vias into the B.Cu plane where clearance allows, else move the autorouted 0.25 mm B.Cu track that cuts the island (all autorouted tracks are listed in `ses_merge.json` / `ses_merge_pass2.json`); re-run DRC until *Unconnected items* = 0, then `bash beta/pcb/tools/beta_export_package.sh POWER_SUPPLY`.

Remaining DRC after BETA (source: `beta/pcb/POWER_SUPPLY/README.md` §3): clearance 56 (0.15 mm pad-to-pad inside the ADM7151/TPS7A83 footprints and 3 `N$` tracks of the source — footprint level), drill_out_of_range 8 (0.254 mm via-pads in the TPS7A8300 footprint vs DRU 0.3 mm min drill — fab to confirm), silk 168/65 (reference texts of script-placed parts on their own pads — cosmetic), via_dangling 20 (autorouter vias whose second-side wire was dropped — remove with *Cleanup tracks & vias* once routing is final), solder_mask_bridge 8, track_dangling 2, zones_intersect 1.

## 5.5 Layer plots and 3-D renders

![Figure 20 — F5.2a — Power Board top composite (F.Cu + F.SilkS + Edge.Cuts) of the KiCad conversion of PowerBoard.brd, 280 × 300 mm; 132 parts parked outside the outline are not visible in this crop (status: SOURCE-DERIVED; source: engineering/PCB/POWER_SUPPLY/svg/POWER_SUPPLY_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/POWER_SUPPLY_top_composite.png)

![Figure 21 — F5.2b — Power Board bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts) (status: SOURCE-DERIVED; source: engineering/PCB/POWER_SUPPLY/svg/POWER_SUPPLY_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/POWER_SUPPLY_bottom_composite_mirrored.png)

![Figure 22 — F5.3a — Power Board 3-D render, top, KiCad conversion of the source layout (unplaced parts outside the outline) (status: SOURCE-DERIVED; source: engineering/PCB/POWER_SUPPLY/3d/POWER_SUPPLY_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/POWER_SUPPLY/3d/POWER_SUPPLY_render_top.png)

![Figure 23 — F5.3b — Power Board BETA board after scripted placement, two Freerouting passes, bridges and GND stitching; 89 connections still open (status: BETA; source: beta/pcb/POWER_SUPPLY/exports/3d/POWER_SUPPLY_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/POWER_SUPPLY/exports/3d/POWER_SUPPLY_render_isometric.png)

The generated assembly-drawing PDFs of this board are clipped by the A4 page frame in the same way as described for the Main Board (chapter 4 §4.5) and are not used as figures.

## 5.6 Stack-up

Source DRU `PCBWay_2L_100um-Track` (source: `engineering/PCB/POWER_SUPPLY/STACKUP.md`, status PARTIAL):

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 1.5mm |
| 2 | 16 | B.Cu | 0.035mm | — |

PROPOSED fabrication note (source: `beta/pcb/POWER_SUPPLY/FAB_NOTES.md` §2–§4): FR-4 Tg 150 °C core 1.5 mm, finished **1.6 mm ± 10 %**, no controlled impedance; copper **35 µm, PROPOSED 70 µm / 2 oz** because the VIN rails are 2 mm polygons on a power-distribution board (designer to decide); ENIG; min track/space 0.10 (BETA routing 0.25) / 0.20 mm; min drill 0.30 mm (0.5 mm via); copper-to-edge 0.3 mm; IPC-A-600 Class 2; 100 % e-test with `exports/ipc/POWER_SUPPLY_netlist.d356`. Note that §3 of that FAB_NOTES file repeats the RF-board template text (RO4350B, maskless RF traces) — it does not apply to this board, which has no RF or LVDS nets (`FAB_NOTES.md` §4). Current capacity of the highest-current traces (QPA2962 bias ≥ 1.68 A each per the xlsx; FPGA +1V0) is not checkable from XML and REQUIRES DESIGN REVIEW against IPC-2221 (source: `docs/PCB/POWER_SUPPLY.md` §7).

## 5.7 BOM summary

Source BOM `docs/BOM/BOM_POWER_SUPPLY.csv`: 312 references, 28 line items, 0 MPN attributes, 80 references without value (source: `docs/BOM/README.md`). BETA BOM confidence, counted with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/POWER_SUPPLY/BOM_POWER_SUPPLY_beta.csv'))))"`:

| mpn_confidence | Lines | Quantity (source: `beta/pcb/README.md`) |
|---|---|---|
| HIGH | 7 | 79 |
| MEDIUM | 18 | 225 |
| LOW | 3 | 8 |
| EMPTY | 0 | 0 |
| **Total** | **28** | 312 |

Before purchase (source: `docs/PCB/POWER_SUPPLY.md` §8): confirm 21 × TPS562208 against the xlsx rail count; confirm the AK300/2 input connector rating for the total current (sum not computed in the xlsx); add the TPS562208 and LM2662 datasheets to `7_Components Datasheets`.

## 5.8 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K4 | PA supply: xlsx needs 16 × 22 V / 2 A; this board has `Vin [12-17] V` only → DSN-PSU-01 proposal (chapter 9, D-14) | OPEN — power designer | `docs/SYSTEM/BLOCK_DIAGRAM.md`; `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5 |
| G-10 | Final outline: hole pattern (10..270 × 10..230, one at y = 267.85) suggests a smaller board than 280 × 300 | UNRESOLVED | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` |
| — | sch 9.6.2 / brd 7.4.0 mismatch; consistency check (P-EAGLE-01) not yet run in EAGLE | OPEN | `docs/PCB/POWER_SUPPLY.md` §5 |
| — | 89 open connections in BETA; placement review by a designer | OPEN | `beta/pcb/POWER_SUPPLY/UNROUTED.md` |
| — | 24 pins without net (TPS7A8300 feedback select, LM2662 FC/OSC) | OPEN | `engineering/ELECTRICAL/netlists/POWER_SUPPLY_unresolved_connections.md` |
| — | 80 value-less references (buck compensation parts) | OPEN | `docs/BOM/README.md` |
| — | 13 rail outputs without a same-name destination connector | OPEN | `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` |
| — | Copper weight 1 oz vs 2 oz; trace current capacity review | OPEN — designer | `beta/pcb/POWER_SUPPLY/FAB_NOTES.md` §2 |
| — | Datasheets of the parts actually used (TPS562208, LM2662) missing | OPEN | `docs/PCB/POWER_SUPPLY.md` §1 |

Acceptance criteria for this board (0 airwires, 0 off-board parts, outline recorded, DRC/ERC 0, Gerber/drill matching `POWER_SUPPLY_outline.svg`, 100 % MPN, PA-supply architecture decided) are copied from `docs/PCB/POWER_SUPPLY.md` §10 in chapter 14.


---

<!-- chapter 6: Synth board -->
# 6. Frequency Synthesizer Board (Clocks_Freq_Synth_board)

**Chapter status summary:** schematic — SOURCE-DERIVED (EAGLE 9.6.2 rendered); connector inventory — SOURCE-DERIVED; layout — complete in the source (0 airwires, 0 approved DRC) and SOURCE-DERIVED in the KiCad conversion; BETA copy with silkscreen clean-up only (copper untouched); layer plots and renders — SOURCE-DERIVED / BETA; stack-up — PARTIAL with three contradictory sources (DRU, `Stack_Hybrid.png`, PCBWay impedance note) and a PROPOSED fabrication note; pick-and-place — ORIGINAL PROJECT FILE (the only production artefact the upstream project delivered); BOM — PARTIAL (0 MPN; oscillator part-number conflict K7). Nothing is hardware-verified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/FREQUENCY_SYNTHESIZER.md`; `engineering/ELECTRICAL/connection_diagrams/FREQUENCY_SYNTHESIZER_connection_report.md` §1–2; `engineering/ELECTRICAL/schematics/FREQUENCY_SYNTHESIZER/`; `engineering/PCB/FREQUENCY_SYNTHESIZER/README.md`, `STACKUP.md`; `beta/pcb/FREQUENCY_SYNTHESIZER/README.md`, `DRC_DISPOSITION.md`, `FAB_NOTES.md`, `BOM_FREQUENCY_SYNTHESIZER_beta.csv`; `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/` (ORIGINAL PROJECT FILE).

## 6.1 Role and key parts

The synthesizer board generates every clock and local oscillator of the radar: the AD9523 clock generator distributes 100 MHz (FPGA system clock), 400 MHz (ADC and FPGA ADC-side clock), 120 MHz (DAC and FPGA DAC-side clock), 300 MHz references to the two ADF4382 PLLs and a 20 MHz test output; the two ADF4382 synthesizers produce the TX and RX local oscillators. Board: **100 × 100 mm, 6 copper layers**, EAGLE 9.6.2, 184 physical parts, 139 nets, 769 vias, DRU `PCBWay_6L_100um-Track` (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §1).

Key parts (deviceset names, MPN UNVERIFIED; source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §1):

| Function | Part (refdes) | Qty | Note |
|---|---|---|---|
| Clock generator | AD9523BCPZ (IC1) | 1 | channel programming in firmware `main.cpp:965-1030` |
| TX / RX LO synthesizers | ADF4382ABCCZ (U1 TX, U6 RX) | 2 | |
| Baluns / transformers | MTX2-143+ | 4 | |
| 3 dB attenuators | ATS1005-3DB-FD-T05 | 4 | |
| OCXO 100 MHz | ECOC-2522-100.000-3HC (X4) | 1 | xlsx lists `-3FC` suffix — CONFLICT |
| VCXO 50 MHz | CVHD-950-50.000 (X5, X6) | 2 | xlsx lists CVHD-950-100.000; firmware `vcxo_freq = 100 MHz` — K7 |
| Ferrites | FBMH1608HL601-T | 4 | |
| SMA jacks | 142-0731-211 | 11 | silk names: `LO TX`, `LO RX`, `AUX. LO TX`, `AUX. LO RX`, `ADC`, `FPGA=ADC`, `FPGA=DAC`, `DAC`, `FPGA SYS. CLOCK`, `TEST`, `AD9523 PLL_OUT`, `TX_LO MUXOUT`, `RX_LO MUXOUT` |
| Differential outputs | CJT-T-P-HH-ST-TH1 (J3, J4) | 2 | |
| Power inputs | Molex 22-23-2021 (X10–X15) | 6 | |
| Control headers | JP1 (2×6), JP2 (2×7) | 2 | mate with Main Board JP1 / JP13 |

Firmware cross-reference of the AD9523 outputs (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §1, `main.cpp:965-1030`): OUT0/1 300 MHz → ADF4382 TX/RX reference; OUT4 400 MHz → ADC; OUT5 400 MHz → FPGA (`FPGA=ADC`); OUT6 100 MHz → `FPGA SYS. CLOCK`; OUT7 20 MHz → `TEST`; OUT8/9 60 MHz SYNC; OUT10 120 MHz → `DAC`; OUT11 120 MHz → `FPGA=DAC`. Which oscillator (OCXO X4 or VCXO X5/X6) drives which AD9523 input REQUIRES VERIFICATION against the schematic nets (same source; K7).

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/FREQUENCY_SYNTHESIZER_connection_report.md` §1):

| Item | Count |
|---|---|
| Sheets | 1 |
| Parts (all) / physical | 318 / 184 |
| Nets | 139 |
| Pin connections | 752 |
| Single-pin nets | 5 |
| Unconnected pins on placed gates | 34 |
| Physical parts without value | 47 |
| Board airwires (unrouted connections, layer 19) | 0 |
| Missing symbol/footprint records | 0 |

The 5 single-pin nets are `N$29`, `AD9523_OUT2±`, `AD9523_OUT3±` — unused clock outputs (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §1); they may stay unterminated only if the AD9523 datasheet permits, and `main.cpp:961-968` (unused channel divider = 0) must be checked for `output_dis` (same source §7).

## 6.2 Connectors

24 connector parts (source: `engineering/ELECTRICAL/connection_diagrams/FREQUENCY_SYNTHESIZER_connection_report.md` §2; SMA signal nets are mostly unnamed `N$xx` — the silkscreen name and the interconnection table §6 give their function):

| Refdes | Package | Signal nets (GND omitted) | Function (silk / interconnection table §6) |
|---|---|---|---|
| J1 | 142-0731-211 | `N$35` | SMA — see silk label on the board |
| J2 | 142-0731-211 | `N$51` | SMA |
| J3 | CJT-T-P-HH-ST-TH1 | `AD9523_OUT4_P/N` | 400 MHz ADC clock → Main J21 (CBL-039 in DSN-HAR-01) |
| J4 | CJT-T-P-HH-ST-TH1 | `AD9523_OUT5_P/N` | OUT5 = 400 MHz FPGA=ADC per the firmware cross-reference → Main J19 (`FPGA_ADC_CLOCK_P/N`); the harness row CBL-042 labels this cable "test" — discrepancy to resolve |
| J5 | 142-0731-211 | `N$64` | 120 MHz DAC → Main J20 |
| J6 | 142-0731-211 | `N$67` | 120 MHz FPGA=DAC → Main J18 |
| J7 | 142-0731-211 | `AD9523_OUT6+` | 100 MHz FPGA SYS. CLOCK → Main J1 |
| J8 | 142-0731-211 | `AD9523_OUT7+` | 20 MHz TEST |
| J9 | 142-0731-211 | `N$37` | SMA |
| J10 | 142-0731-211 | `N$30` | LO TX → Main J23 |
| J11 | 142-0731-211 | `N$55` | LO RX → Main J22 |
| J12 | 142-0731-211 | `N$59` | SMA |
| J13 | 142-0731-211 | `N$61` | SMA |
| JP1 | PINHD-2X6 | `AD9523_PD, _REF_SEL, _SYNC, _RESET, _CS, _SCLK, _SDIO, _SDO, _STATUS0, _STATUS1, _EEPROM_SEL` | AD9523 control ↔ Main JP1 |
| JP2 | PINHD-2X7 | `ADF4382_SDO, _SCLK, _SDIO, ADF4382_TX_CS/CE/DELSTR/DELADJ/LKDET, ADF4382_RX_CS/CE/DELSTR/DELADJ/LKDET` | ADF4382 control ↔ Main JP13 |
| X4 | ECOC-2522 (OCXO) | `N$1, +3V3_XO, 10MHZ_OUT` | 100 MHz OCXO |
| X5 | CVHD-950 (VCXO) | `100MHZ_OUT, +3V3_XO` | VCXO |
| X6 | CVHD-950 (VCXO) | `N$2, VCXO_OUT, +3V3_XO` | VCXO |
| X10–X14 | 22-23-2021 | `N$69, N$71, N$73, N$75, N$77` | power inputs (rail names on the Power Board side — interconnection table §4) |
| X15 | 22-23-2021 | `+5V0_LO` | power input ← Power Board X6 (CBL-005) |

The SMA ↔ silk-name assignment for J1, J2, J9, J12, J13 (`AUX. LO TX`, `AUX. LO RX`, `AD9523 PLL_OUT`, `TX_LO MUXOUT`, `RX_LO MUXOUT`) is in `engineering/SYSTEM/interfaces/interconnection_table.md` §6; it is not repeated here because the report lists only the net names.

## 6.3 Schematic sheet

![Figure 24 — F6.1 — Frequency Synthesizer schematic, single sheet: AD9523 clock generator, 2 × ADF4382 LO synthesizers, OCXO/VCXO, 11 SMA outputs, control headers JP1/JP2 (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/FREQUENCY_SYNTHESIZER/png/FREQUENCY_SYNTHESIZER_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/FREQUENCY_SYNTHESIZER/png/FREQUENCY_SYNTHESIZER_schematic_sheet1.png)

## 6.4 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 9.6.2)

| Item | Finding (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §2) |
|---|---|
| Routing / DRC / ERC | complete; 0 airwires; 0 approved DRC; 0 approved ERC; sch/brd part and net sets identical |
| Min track | 0.1 mm; RF widths 0.204 mm (×329) and 0.22 mm (×414) |
| DRU | mdWireWire 0.1, mdCopperDimension 0.3, msDrill 0.15, rvViaOuter 0.25, `mtIsolate = 0.11, 0.6, 0.11, 0.36, 0.2 …, 0.6, 0.11 mm`, thermals for vias off |
| Stack-up | EAGLE: 6 Cu, prepreg-outer/foil construction. `Stack_Hybrid.png`: 6 Cu with RO4350B 0.102 mm outer cores, FR-4 0.100 centre, prepregs 0.100. PCBWay note: h = 0.102 mm. Three sources disagree on construction and thickness → UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION |
| 2.0 mm via | one 2.0 mm drill via — check purpose (mounting/thermal) |

Production files delivered by the upstream project (ORIGINAL PROJECT FILE; source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §1): `Clocks_Freq_Synth_board_BOM.xlsx` (41 rows, EAGLE `bom.ulp` CSV pasted into one column, empty MPN columns, mojibake `0.1ÂµF`); `-smd.mnt` (173 rows, all TOP) and `-tht.mnt` (10 rows: JP1, JP2, X10–X15, J3, J4) with duplicates `mnt.csv`, `-tht.csv`, `smd_.xlsx`, `th_.xlsx`; `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` (RO4350B, h = 0.102 mm, Dk 3.48/3.66, 35 µm Cu, no mask on RF, 50 Ω w = 0.204 mm, 100 Ω diff w = 0.204 / s = 0.26 mm, via fence ≤ 1 mm pitch, coupons requested). No Gerber, drill, fab or assembly drawing was delivered.

### Engineering conversion (`engineering/PCB/FREQUENCY_SYNTHESIZER/`)

Cross-check (source: `engineering/PCB/FREQUENCY_SYNTHESIZER/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 100.0 | 100.0 | OK |  |
| Height (mm) | 100.0 | 100.0 | OK |  |
| Footprints = EAGLE elements + free holes | 188 | 188 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 769 | 769 | OK |  |
| Tracks (signal wires excl. airwires) | 1374 | 1374 | OK |  |
| Copper layers | 6 | 6 | OK |  |
| NPTH holes (free holes + package holes) | 4 | 4 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 863 | 863 | OK |  |

DRC on the conversion: 639 violations, 0 unconnected (source: `engineering/PCB/FREQUENCY_SYNTHESIZER/README.md` §6):

| Rule | Count | Interpretation |
|---|---|---|
| `solder_mask_bridge` | 199 | mask web between adjacent pads thinner than KiCad default (EAGLE has no such rule) — fabricator decision |
| `silk_overlap` | 199 | overlapping silkscreen texts/lines — cosmetic |
| `silk_over_copper` | 199 | silk over exposed copper — cosmetic/assembly |
| `track_dangling` | 35 | track end not connected — review (stubs or unfinished routing) |
| `courtyards_overlap` | 7 | footprint courtyards overlap — imported courtyard approximation |

### BETA board (`beta/pcb/FREQUENCY_SYNTHESIZER/`)

Copper was **not modified** (source: `beta/pcb/FREQUENCY_SYNTHESIZER/README.md`). Before/after (same source §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 0 | 0 |
| courtyards_overlap | 7 | 7 |
| silk_over_copper | 199 | 199 |
| silk_overlap | 199 | 199 |
| solder_mask_bridge | 199 | 199 |
| track_dangling | 35 | 35 |
| **DRC violations total** | 639 | 639 |

Change: 43 silkscreen reference texts moved to the nearest free position (≤ 3 mm, 0.05 mm step; `beta/pcb/tools/beta_silk_nudge.py`, `silk_nudges.json`); 103 texts remain in conflict because the 0201-dense board has no free spot within 3 mm (`silk_conflicts_remaining.json`). Disposition of all 639 items (source: `beta/pcb/FREQUENCY_SYNTHESIZER/DRC_DISPOSITION.md` §1): 7 courtyard overlaps REAL (review) — pairs C25↔L10, L12↔C45, L12↔C33, C27↔L10, L11↔C29, L11↔C31, L9↔C21; the pads do not touch, designer to confirm that the L5650M inductor body does not collide with the adjacent capacitors at assembly; 35 dangling GND arc stubs 0.002–0.212 mm inside the GND pour — COSMETIC; silkscreen 147 → 103 texts in conflict (measured uncapped) — COSMETIC, fab clips silk on pads; solder-mask bridges — FAB REVIEW (PCBWay minimum mask dam 0.1 mm, CAM merges apertures). Recommendation for the production revision: hide 0201/0402 reference designators on silk.

## 6.5 Layer plots and 3-D renders

![Figure 25 — F6.2a — Frequency Synthesizer top composite (F.Cu + F.SilkS + Edge.Cuts), 100 × 100 mm (status: SOURCE-DERIVED; source: engineering/PCB/FREQUENCY_SYNTHESIZER/svg/FREQUENCY_SYNTHESIZER_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/FREQUENCY_SYNTHESIZER_top_composite.png)

![Figure 26 — F6.2b — Frequency Synthesizer bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts); the AD9523_OUT8/9 pairs run on B.Cu (status: SOURCE-DERIVED; source: engineering/PCB/FREQUENCY_SYNTHESIZER/svg/FREQUENCY_SYNTHESIZER_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/FREQUENCY_SYNTHESIZER_bottom_composite_mirrored.png)

![Figure 27 — F6.3a — Frequency Synthesizer 3-D render, top, KiCad conversion; no component models (status: SOURCE-DERIVED; source: engineering/PCB/FREQUENCY_SYNTHESIZER/3d/FREQUENCY_SYNTHESIZER_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/FREQUENCY_SYNTHESIZER/3d/FREQUENCY_SYNTHESIZER_render_top.png)

![Figure 28 — F6.3b — Frequency Synthesizer BETA board, isometric render (silkscreen nudged, copper identical to the source) (status: BETA; source: beta/pcb/FREQUENCY_SYNTHESIZER/exports/3d/FREQUENCY_SYNTHESIZER_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/FREQUENCY_SYNTHESIZER/exports/3d/FREQUENCY_SYNTHESIZER_render_isometric.png)

The generated assembly-drawing PDFs are clipped by the A4 page frame (chapter 4 §4.5) and are not used as figures; the original `-smd.mnt`/`-tht.mnt` pick-and-place files remain the upstream placement reference.

## 6.6 Stack-up

Source DRU `PCBWay_6L_100um-Track`, layerSetup `(1+2*3+14*15+16)` (source: `engineering/PCB/FREQUENCY_SYNTHESIZER/STACKUP.md`, status PARTIAL):

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 0.11mm |
| 2 | 2 | In1.Cu | 0.035mm | 0.6mm |
| 3 | 3 | In2.Cu | 0.035mm | 0.11mm |
| 4 | 14 | In3.Cu | 0.035mm | 0.6mm |
| 5 | 15 | In4.Cu | 0.035mm | 0.11mm |
| 6 | 16 | B.Cu | 0.035mm | — |

PROPOSED fabrication stack-up (source: `beta/pcb/FREQUENCY_SYNTHESIZER/FAB_NOTES.md` §2): layer 1 on **RO4350B 4 mil** (DRU 0.11 mm vs. note 0.102 mm — to be reconciled; RO4350B 4 mil = 0.101 mm), FR-4 cores 0.6 mm and prepregs 0.11 mm inside, layer 5/6 dielectric PROPOSED as RO4350B as well because B.Cu carries the `AD9523_OUT8/9` pairs at 0.204 mm; dielectric sum 1.53 mm + 6 × 35 µm ≈ 1.74 mm → finished **1.6 mm ± 10 %** with thinned cores, or 2.0 mm — to be decided with PCBWay. Controlled impedance (same source §4): 100 Ω differential at w = 0.204 / s = 0.26 mm for `AD9523_OUT0..9_P/N`, `ADF4382_TX/RX_SYNC_P/N` (RX_SYNC s = 0.296 mm), `TX/RX_RFOUT_1/2_P/N` run uncoupled (s ≈ 0.8 mm); 50 Ω at w = 0.204 mm (0.22 mm on some OUT+ stubs) for `100MHZ_OUT`, `10MHZ_OUT`, `VCXO_OUT`, `AD9523_OUT6/7/10/11+`; SPI/control not controlled. The PCBWay impedance note belongs to this board: continuous GND under the RF layer, no solder mask on RF traces, coupons for 50 Ω and 100 Ω, PCBWay may tune w by ±0.02–0.04 mm and s by ±0.03–0.05 mm.

## 6.7 BOM summary

Source BOM `docs/BOM/BOM_FREQUENCY_SYNTHESIZER.csv`: 184 references, 40 line items, 0 MPN attributes, 47 references without value — consistent with the upstream 40-line xlsx (source: `docs/BOM/README.md`). BETA confidence, counted with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/FREQUENCY_SYNTHESIZER/BOM_FREQUENCY_SYNTHESIZER_beta.csv'))))"`:

| mpn_confidence | Lines | Quantity (source: `beta/pcb/README.md`) |
|---|---|---|
| HIGH | 10 | 37 |
| MEDIUM | 22 | 110 |
| LOW | 6 | 29 |
| EMPTY | 2 | 8 |
| **Total** | **40** | 184 |

BOM validation before purchase (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §8): add MPN and manufacturer to all 40 lines; fill the 47 missing values; fix the encoding (UTF-8 `µ`); mark the 11 SMA connectors populated/DNP per variant; resolve the oscillator conflict (ECOC-2522-100.000-3FC vs -3HC suffix; CVHD-950-100.000 in the xlsx vs CVHD-950-50.000 in the schematic — K7).

## 6.8 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K7 | Oscillator topology and part numbers (OCXO 100 MHz + 2 × VCXO 50 MHz in CAD vs VCXO 100 MHz in xlsx/firmware); which oscillator feeds AD9523 REF/OSC_IN | OPEN — RF designer | `docs/SYSTEM/BLOCK_DIAGRAM.md`; `docs/PCB/FREQUENCY_SYNTHESIZER.md` §1 |
| — | Stack-up: DRU / `Stack_Hybrid.png` / PCBWay note disagree; one construction to be chosen and the DRU `mtIsolate` updated (G-01, MDR-07) | BLOCKED — MISSING DATA | `docs/PCB/FREQUENCY_SYNTHESIZER.md` §2 |
| — | 5 single-pin nets (unused AD9523 outputs) — datasheet/firmware `output_dis` check | OPEN | same §7 |
| — | 7 courtyard overlaps (L10/L11/L12/L9 vs 0201 capacitors) — body-height check | OPEN — designer | `beta/pcb/FREQUENCY_SYNTHESIZER/DRC_DISPOSITION.md` §2 |
| — | 2.0 mm via — purpose unknown | OPEN | `docs/PCB/FREQUENCY_SYNTHESIZER.md` §2 |
| — | Duplicate P&P files (`mnt.csv`, `-tht.csv`, `smd_.xlsx`, `th_.xlsx`) to be superseded by one regenerated pair | OPEN | same §3 |
| — | BOM: 0/40 MPN verified, 47 value-less references, encoding | OPEN | `docs/BOM/README.md` |
| — | 103 silkscreen conflicts on 0201 parts; hide small refdes for production | OPEN | `beta/pcb/FREQUENCY_SYNTHESIZER/README.md` §3 |

Post-fabrication functional acceptance (hardware test, not a file check; source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §10): AD9523 lock (STATUS0/1 high), OUT6 = 100 MHz, OUT4/5 = 400 MHz, OUT10/11 = 120 MHz measured — see chapter 16.


---

<!-- chapter 7: RF PA board (×16) -->
# 7. RF Power Amplifier Board (RF_PA, ×16)

**Chapter status summary:** schematic — SOURCE-DERIVED (EAGLE 9.6.2 rendered); layout — complete in the source (0 airwires, 0 approved DRC), SOURCE-DERIVED in the KiCad conversion, BETA copy with one GND strap and the paddle polygon given its net (RF tracks untouched); layer plots and renders — SOURCE-DERIVED / BETA; stack-up — PARTIAL (4-layer DRU, 70 µm copper slot unexplained) with a PROPOSED fabrication note; BOM — PARTIAL (0 MPN; `QPA2962_B` is a deviceset name); thermal budget and drain gating — PROPOSED DESIGN (DSN-THM-01, D-10/D-11/D-14, first-order estimates). The 22 V drain supply, the drain-gating switch and the heat path do not exist in the original CAD. RF performance (gain, P1dB at 10.5 GHz) is unverified. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/PCB/RF_PA.md`; `engineering/ELECTRICAL/connection_diagrams/RF_PA_connection_report.md`; `engineering/ELECTRICAL/schematics/RF_PA/`; `engineering/PCB/RF_PA/README.md`, `STACKUP.md`; `beta/pcb/RF_PA/README.md`, `FAB_NOTES.md`, `BOM_RF_PA_beta.csv`; `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md`; `engineering/SYSTEM/interfaces/interconnection_table.md` §7.

## 7.1 Role and key parts

One RF_PA board amplifies the transmit signal of one antenna row; the AERIS-10X variant uses sixteen boards, 10 W each (source: `docs/PCB/RF_PA.md` §2, citing `README.md:80`). Each board holds a single Qorvo QPA2962 GaN PA with its gate-bias input (`VG`, from the Main Board DAC5578/OPA4703 chain), a drain input (`VD`) through a 5 mΩ shunt whose two ends (`VD`, `VIN_M`) are returned to the Main Board INA241A3 current-sense amplifier, and two SMA jacks. Board: **35 × 60 mm, 4 copper layers**, EAGLE 9.6.2, 25 physical parts, 15 nets, 77 wires, 342 vias (of which 215 × 0.35 mm stitching/thermal), DRU `PCBWay_4L_100um-Track` (source: `docs/PCB/RF_PA.md` §1).

Parts (source: `docs/PCB/RF_PA.md` §1; `engineering/ELECTRICAL/connection_diagrams/RF_PA_connection_report.md` §4):

| Refdes | Value / device | Connections (pad:net) | Note |
|---|---|---|---|
| U$1 | QPA2962_B (Qorvo 10 W GaN PA) | GND, RFIN:`N$2`, RFOUT:`N$8`, VD1/VD2:`VIN_M`, VG:`VG` | deviceset name is not the orderable MPN; datasheet and S-parameters at 22 V / 1 680 mA in `7_Components Datasheets` |
| J1, J2 | SMA 142-0731-211 | J1 pin 1 `N$2` (RFIN per silk), J2 pin 1 `N$8` (RFOUT per silk) | |
| X2 | Molex 22-23-2021 | 1 `VG`, 2 `GND` | gate bias from Main X_n |
| X3 | Molex 22-23-2031 | 1 `VD`, 2 `VIN_M`, 3 `GND` | drain-current sense pair to Main X3/X38…X52 |
| 22V | AK300/2 screw terminal | 1 `VD`, 2 `GND` | drain supply input — no source in CAD (K4) |
| R10 | 5 mΩ WSL2816 | 1 `VIN_M`, 2 `VD` | shunt; BETA BOM flags a 0.1 Ω part number for a 5 mΩ value |
| R1, R4 | 10R 0402 | VG / VIN_M decoupling | |
| R2, R3, R5–R9 | 0R 0402/0603 | VG / VIN_M decoupling links | |
| C1, C4, C5 | 10 µF 1206 | decoupling | |
| C2, C3, C6–C9 | 0.1 µF 0402 | decoupling | |

Schematic summary (source: `engineering/ELECTRICAL/connection_diagrams/RF_PA_connection_report.md` §1): 1 sheet; 43 parts / 25 physical; 15 nets; 78 pin connections; 0 single-pin nets; 0 unconnected pins; 6 physical parts without value; 0 airwires; 0 missing symbol/footprint records. Net fan-out: `GND` 38 connections, `VIN_M` 10 (same source §3). Silk labels on the board: `CURRENT SENSOR`, `VIN+`, `VIN-`, `VG` (source: `docs/PCB/RF_PA.md` §1).

System connections of one PA instance n (source: `engineering/SYSTEM/interfaces/interconnection_table.md` §7): element RF from Main Board SMA pair (J27/J26 for n = 1 … J51/J50 for n = 16) to J1/J2 — which SMA of the Main pair is TX-to-PA and which is RX-return is UNVERIFIED; gate bias `VG_n` from Main X_7 = VG_1, X_16 = VG_2, X_8 = VG_3, X_15 = VG_4, X_4 = VG_5, X_11 = VG_6, X_3 = VG_7, X_12 = VG_8, X_5 = VG_9, X_14 = VG_10, X_6 = VG_11, X_13 = VG_12, X_2 = VG_13, X_9 = VG_14, X_1 = VG_15, X_10 = VG_16 (xlsx: −4 … −1.2 V, 10 mA); sense pair to Main X3, X38…X52 (INA241A3); drain `VD` 22 V from a supply that is NOT IN CAD (xlsx row 59: 18–22 V, 2 000 mA, "Set VD +22 V"); drain enable `EN/DIS_RFPA_VDD` on Main JP10 (STM32 PD6, `main.cpp:1601`) to a switch that is NOT IN CAD.

## 7.2 Schematic sheet

![Figure 29 — F7.1 — RF PA schematic, single sheet: QPA2962, SMA in/out, VG and VD/VIN_M decoupling, 5 mΩ sense shunt, 22 V terminal (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/RF_PA/png/RF_PA_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/RF_PA/png/RF_PA_schematic_sheet1.png)

## 7.3 Layout state: source vs. engineering conversion vs. BETA

### Source (EAGLE 9.6.2)

| Item | Finding (source: `docs/PCB/RF_PA.md` §2) |
|---|---|
| Routing | complete (0 airwires) |
| DRC/ERC | 0 approved entries; sch/brd consistent |
| Min track | 0.204 mm (50 Ω microstrip width of the PCBWay note) |
| DRU | mdWireWire 0.15, mdCopperDimension 0.3, msDrill 0.15 mm; `mtCopper` third slot 0.07 mm (70 µm) although slot 3 is not an active layer — interpretation UNRESOLVED; `mtIsolate` 0.11 / 1.2 / 0.36 … mm |
| Stack-up | 4 layers; `Stack_Hybrid.png` (6 layers) does not describe this board; no vendor stack-up → UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION |
| Thermal | 215 × 0.35 mm vias under/around the PA: thermal path to the enclosure/heatsink is undocumented (no mechanical data) |
| System fit | 16 PA boards at 10 W each; xlsx budgets +22 V / 2 A × 16; the Power Board has no 22 V rail — PA supply UNRESOLVED |

### Engineering conversion (`engineering/PCB/RF_PA/`)

Cross-check (source: `engineering/PCB/RF_PA/README.md` §3):

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 35.0 | 35.0 | OK |  |
| Height (mm) | 60.0 | 60.0 | OK |  |
| Footprints = EAGLE elements + free holes | 32 | 32 | OK | KiCad imports every free `<hole>` as a footprint |
| Vias | 342 | 342 | OK |  |
| Tracks (signal wires excl. airwires) | 77 | 77 | OK |  |
| Copper layers | 4 | 4 | OK |  |
| NPTH holes (free holes + package holes) | 7 | 7 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 357 | 357 | OK |  |

DRC on the conversion: 48 violations, 1 unconnected (source: `engineering/PCB/RF_PA/README.md` §6):

| Rule | Count | Interpretation |
|---|---|---|
| `clearance` | 16 | copper clearance < DRU — review |
| `zones_intersect` | 8 | overlapping pours of different priority — conversion artefact or design issue |
| `silk_overlap` | 8 | overlapping silkscreen texts/lines — cosmetic |
| `silk_over_copper` | 8 | silk over exposed copper — cosmetic/assembly |
| `shorting_items` | 7 | copper of different nets touching after conversion (typically EAGLE polygon vs unnamed copper) — REVIEW in EAGLE |
| `silk_edge_clearance` | 1 | silk too close to edge |

### BETA board (`beta/pcb/RF_PA/`)

Before/after (source: `beta/pcb/RF_PA/README.md` §1):

| Check | Before (engineering/PCB conversion) | After (BETA) |
|---|---|---|
| unconnected_items | 1 | 0 |
| clearance | 16 | 1 |
| shorting_items | 7 | 0 |
| silk_edge_clearance | 1 | 1 |
| silk_over_copper | 8 | 8 |
| silk_overlap | 8 | 8 |
| zones_intersect | 8 | 0 |
| **DRC violations total** | 48 | 18 |

Changes, nothing in the netlist (source: `beta/pcb/RF_PA/README.md` §2): (1) GND strap F.Cu 0.5 mm from the via at (16.20, −11.20) to the QPA2962 ground-paddle centre (16.20, −13.40) — the only unconnected item: the paddle was connected to the GND via field only through a net-less footprint polygon, which KiCad does not count as copper of the net; (2) the U$1 paddle polygon re-created as a board-level copper polygon with net GND, identical geometry (it touched 21 GND items and nothing else; as a net-less graphic it produced 7 shorting + 19 hole-clearance + 15 clearance false errors); (3) 6 overlapping same-net GND zones given distinct priorities; (4) refill, DRC, export. RF tracks (`N$2`, `N$8` at 0.204 mm) and bias lines were **not** touched.

Remaining 18 items (same source §3): 1 clearance — GND paddle polygon ↔ `VIN_M` track stub at (17.46, −15.63): 0.123 mm < 0.15 mm DRU, exists in the source → designer to confirm or nudge the VIN_M stub; 8 silk_overlap (`VIN+`/`VIN−` texts over the X3 outline, UNK22V0 texts) and 8 silk_over_copper (X2/X3 outlines over THT pads, J1/J2/U$1 silk on mask-defined areas) — cosmetic; 1 silk_edge_clearance (UNK22V0 reference 0.1 mm from the edge) — cosmetic.

## 7.4 Layer plots and 3-D renders

![Figure 30 — F7.2a — RF PA top composite (F.Cu + F.SilkS + Edge.Cuts), 35 × 60 mm: 0.204 mm RF microstrips J1 → U$1 → J2 and the thermal-via field under the PA (status: SOURCE-DERIVED; source: engineering/PCB/RF_PA/svg/RF_PA_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/RF_PA_top_composite.png)

![Figure 31 — F7.2b — RF PA bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts) (status: SOURCE-DERIVED; source: engineering/PCB/RF_PA/svg/RF_PA_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/RF_PA_bottom_composite_mirrored.png)

![Figure 32 — F7.3a — RF PA 3-D render, top, KiCad conversion; no component models (status: SOURCE-DERIVED; source: engineering/PCB/RF_PA/3d/RF_PA_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/RF_PA/3d/RF_PA_render_top.png)

![Figure 33 — F7.3b — RF PA BETA board, isometric render (GND strap and paddle polygon net added, RF copper unchanged) (status: BETA; source: beta/pcb/RF_PA/exports/3d/RF_PA_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/RF_PA/exports/3d/RF_PA_render_isometric.png)

The generated assembly-drawing PDFs are clipped by the A4 page frame (chapter 4 §4.5) and are not used as figures.

## 7.5 Stack-up

Source DRU `PCBWay_4L_100um-Track`, layerSetup `(1+2*15+16)` (source: `engineering/PCB/RF_PA/STACKUP.md`, status PARTIAL):

| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |
|---|---|---|---|---|
| 1 | 1 | F.Cu | 0.035mm | 0.11mm |
| 2 | 2 | In1.Cu | 0.035mm | 1.2mm |
| 3 | 15 | In2.Cu | 0.035mm | 0.11mm |
| 4 | 16 | B.Cu | 0.035mm | — |

PROPOSED fabrication note (source: `beta/pcb/RF_PA/FAB_NOTES.md` §2–§4): F.Cu on **RO4350B 4 mil** (DRU 0.11 mm vs. note 0.102 mm), FR-4 core 1.2 mm, prepreg 0.11 mm (RO4350B only if bottom RF existed — none routed on B.Cu); finished **1.6 mm ± 10 %** (DRU sum 1.42 mm + copper ≈ 1.56 mm); the QPA2962 ground paddle carries 21 GND vias 0.35/0.15 mm — PROPOSED via-in-pad, filled and capped, because the paddle is a solder surface (designer/fab to confirm); 50 Ω ± 10 % on `N$2`/`N$8` at w = 0.204 mm (2 segments each, same geometry as the impedance note); bias nets `VIN_M`, `VD`, `VG` 0.37 / 0.6 / 0.8 / 2.0 mm DC. ENIG, maskless RF traces, min track/space 0.10/0.15 mm, min drill 0.15 mm, IPC-A-600 Class 2 — all PROPOSED. The fab drawing may carry the text of the PCBWay impedance note only after the designer confirms it applies to this 4-layer stack (source: `docs/PCB/RF_PA.md` §5).

## 7.6 Thermal budget and drain gating (DSN-THM-01, PROPOSED DESIGN)

First-order estimates from `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` (generator `tools/design_thermal.py`, inputs `engineering/DESIGN/design_parameters.json`, decisions D-10, D-11, D-14; no measurement).

Duty cycle from the firmware timing (`main.cpp:180-186`; source: §1 of the thermal note):

| Quantity | Value |
|---|---|
| TX time per beam position | 16 × 30 µs + 16 × 0.5 µs = **488.0 µs** |
| Frame per beam position | 16 × 167 + 175.4 + 16 × 175 = **5647.4 µs** |
| RF duty | **8.64 %** |
| Drain-gate duty (switch on 5 µs around each chirp, assumption) | **11.47 %** |

Dissipation per QPA2962 (datasheet: VD 22 V, IDQ 1.68 A, PSAT 40 dBm, PAE 22 %; source: §2): quiescent, no RF — 37.0 W DC / **37.0 W** dissipated; at PSAT (PIN 27 dBm) — 43.2 W / 33.7 W; design value while the drain is on — **37.0 W**.

System cases, 16 PAs (source: §3):

| Case | Total PA dissipation | Verdict |
|---|---|---|
| A continuous drain bias (firmware as coded: VD left on) | **591 W** | INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ 142 CFM at ΔT_air 12 K) |
| B drain gated per chirp (D-14), duty 11.5 % | **68 W** | design case |
| C drain gated per CPI frame only (on during the 5.6 ms frame, off while the stepper moves) | **532 W** | INFEASIBLE in a sealed rotating head without liquid cooling (needs ≈ 142 CFM at ΔT_air 12 K) |

Conclusion (D-10/D-14, source: §3): the firmware as coded (VD left on after bias-up, `main.cpp:1560-1601`) puts the head in case A; the proposal therefore requires per-chirp drain gating — a hardware function of the 22 V switch module driven by a timing line — after which the thermal design is case B at **68 W** average.

Heat path, case B (source: §4): 4.24 W average per PA; R(PA board thermal-via field) 1.5 °C/W — **ASSUMPTION, the RF_PA stack-up and via field under U$1 must be checked**; R(TIM) + spreading 0.3 + 0.2 °C/W (assumption, thermal pad 1–3 W/mK, 5 × 5 mm); ΔT PA base → plate 8.5 °C; plate ≤ 77 °C for TBASE ≤ 85 °C; required plate-to-air resistance ≤ **0.46 °C/W** at 45 °C ambient; heat spreader (D-11) 300 × 300 × 10 mm Al with PAs 4 × 4 on the rear centre; two fin fields 55 × 280 mm, 26 fins 25 × 2 mm at 4 mm pitch, 0.39 m²; R(lateral spreading) 0.09 °C/W, R(fins → air, h = 25 W/m²K ASSUMPTION) 0.10 °C/W; resulting plate / PA base **58 °C / 66 °C** at 45 °C ambient (margin 19 °C); airflow **16 CFM** (7.7 L/s) → 2 × 60 mm fans (≥ 15 CFM each) controlled by the existing fan relay. Not included: Power Board regulator losses (currents UNKNOWN), Main Board (≈ 10–20 W estimate), solar load — add 30 % margin when selecting the fans.

22 V drain supply sizing (D-14, source: §5; the block schematic, netlist and BOM are DSN-PSU-01 in chapter 9): peak drain current all 16 PAs at ID_max 2.848 A = **45.6 A** during each 30 µs chirp; average case B **3.47 A** → 76 W (case A 27.3 A → 600 W, not supported); bulk capacitance **2734 µF** total for ΔV ≤ 0.5 V over a chirp → ≥ 220 µF low-ESR polymer per PA board (171 µF each) + 2 × 1000 µF/35 V at the switch module; input 6.9 A average at 12 V, η 92 %; per-PA pulse gating 16 × high-side P-FET (−40 V, 30 A pulsed) with fast driver (e.g. LTC7003), common `TX_GATE` TTL input from the FPGA — **spare I/O to be allocated, UNRESOLVED**; sequencing VG (−4 V via DAC5578) before VD (firmware already does this), gate switch only after `EN/DIS_RFPA_VDD`, power-down in reverse.

Consequence for this board: the "≥ 220 µF low-ESR polymer per PA board" of the proposal is not on the RF_PA schematic (which has 3 × 10 µF + 6 × 0.1 µF); whether it is added on a rev. B of this board or at the switch module is an open decision under D-14.

## 7.7 BOM summary

Source BOM `docs/BOM/BOM_RF_PA.csv`: 25 references, 11 line items, 0 MPN attributes, 6 references without value (source: `docs/BOM/README.md`). BETA confidence, counted with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/RF_PA/BOM_RF_PA_beta.csv'))))"`:

| mpn_confidence | Lines | Quantity (source: `beta/pcb/README.md`) |
|---|---|---|
| HIGH | 5 | 6 |
| MEDIUM | 6 | 19 |
| LOW | 0 | 0 |
| EMPTY | 0 | 0 |
| **Total** | **11** | 25 |

Before purchase (source: `docs/PCB/RF_PA.md` §8): enter the QPA2962 orderable part number (package suffix); gate-bias network values consistent with the DAC5578-driven `VG` range (−4 … −1.2 V per `Power Management V6.xlsx`); the 5 mΩ shunt vs 0.1 Ω MPN conflict flagged in the BETA `note` column (source: `beta/pcb/README.md`). Multiply all quantities by 16 for the AERIS-10X variant.

## 7.8 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K4 | 22 V drain supply and drain switch not in CAD; DSN-PSU-01 proposal (chapter 9) | OPEN — power designer | `docs/SYSTEM/BLOCK_DIAGRAM.md` |
| D-14 | `TX_GATE` timing line — spare FPGA I/O not allocated | UNRESOLVED | `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5 |
| G-12 | Keep-out zones around the RF connectors and the QPA2962 | BLOCKED | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` |
| — | Stack-up 4-layer construction, outer dielectric, 70 µm DRU slot, 50 Ω width confirmation | BLOCKED — MISSING DATA | `docs/PCB/RF_PA.md` §7; MDR-07 |
| — | PA mounting (7 × Ø3.2 mm NPTH), heatsink contact, via-field thermal resistance (1.5 °C/W ASSUMPTION) | OPEN — mechanical/thermal | `docs/PCB/RF_PA.md` §7; thermal note §4 |
| — | Which SMA of each Main Board pair is RFIN/RFOUT; PA n ↔ antenna row n assignment | UNVERIFIED / PROPOSED | `interconnection_table.md` §7; `HARNESS_SCHEDULE.md` |
| — | 1 clearance 0.123 mm (`VIN_M` stub) in the source | OPEN — designer | `beta/pcb/RF_PA/README.md` §3 |
| — | Local 220 µF bulk capacitance per PA board (D-14) not on the schematic | OPEN | this chapter §7.6 |
| — | BOM: QPA2962 MPN, 6 value-less references, shunt MPN conflict | OPEN | `docs/PCB/RF_PA.md` §8 |
| — | RF performance (gain, P1dB at 10.5 GHz) | unverified until measured | `docs/PCB/RF_PA.md` §10 |


---

<!-- chapter 8: Proposed 16×8 patch panel: design, simulation, fabrication data -->
# 8. Antenna — proposed 16 × 8 microstrip patch panel (DSN-ANT-01)

**Chapter status summary:** everything in this chapter is **PROPOSED DESIGN** (decisions D-01…D-06): first-order analytical dimensions, a native KiCad board with a fabrication export set, and openEMS simulations of one row and of three adjacent rows. Nothing has been built or measured; the original project contains no antenna CAD (K8, G-06, MECH-ANT-01 BLOCKED — MISSING DATA). The chirp bandwidth B, which decides whether the series-fed row is adequate, is TBD in the parameter table. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `engineering/DESIGN/ANTENNA/ANTENNA_DESIGN_CALC.md`; `engineering/DESIGN/ANTENNA/simulation/TUNING_LOG.md`, `tuning_result.json`, `s11.csv`, `coupling_3rows.csv`; `engineering/DESIGN/ANTENNA/kicad_exports/board_statistics.md`, `DRC_report.txt`, `EXPORT_LOG.md`; `engineering/DESIGN/00_DESIGN_BASIS.md` (D-01…D-06); `engineering/DRAWING_REGISTER.md` (DSN-ANT-01, DSN-ANT-01-SIM).

## 8.1 Why a patch array

The upstream README names two antenna variants — an 8 × 16 patch array ("Nexus") and a 32 × 16 slotted-waveguide array ("Extended") — without CAD for either (K8; source: `docs/SYSTEM/BLOCK_DIAGRAM.md`). Decision D-01 designs the patch array as the primary antenna because it is manufacturable with the same PCB workflow and verifiable with the openEMS tools already used in `5_Simulations`, and gives only a sizing sheet for the waveguide variant; D-02 makes the 16 radiating "elements" of the firmware's elevation-scanned ULA sixteen horizontal rows at 14.3 mm pitch, each a series-fed resonant array of 8 patches (D-03); D-04 fixes the substrate (RO4350B, h = 0.508 mm, 35 µm Cu, full back ground); D-05 the feed (50 Ω end-launch 2.92 mm connectors on the left edge, one per row); D-06 equal feed-line length on every row so that the ADAR1000 calibration tables stay valid (source: `engineering/DESIGN/00_DESIGN_BASIS.md` D-01…D-06).

The waveguide sizing (CONCEPTUAL, source: `ANTENNA_DESIGN_CALC.md` §6): WR-90 λg at 10.5 GHz = 36.56 mm, resonant shunt slots at λg/2 = 18.28 mm, 32 slots → stick ≈ 585 mm; 16 sticks at 14.3 mm cannot be stacked (WR-90 broad wall 22.86 mm + wall), so the Extended variant would need reduced-height or ridged guide or a 2-row interleave — one reason D-01 selects the patch array.

## 8.2 Design calculation (transmission-line model)

Inputs (source: `ANTENNA_DESIGN_CALC.md` §1):

| Parameter | Value | Basis |
|---|---|---|
| f₀ | 10.500 GHz, λ₀ = 28.552 mm | VERIFIED (parameter table) |
| Rows (elements) × patches per row | 16 × 8 | VERIFIED / D-03 |
| Row pitch (elevation) | 14.3 mm = 0.501 λ₀ | VERIFIED |
| Substrate | RO4350B εr = 3.66, tanδ = 0.0037, h = 0.508 mm, Cu 35 µm | D-04 |

Patch (Balanis ch. 14; source: §2):

| Quantity | Value |
|---|---|
| Width W = (λ₀/2)·√(2/(εr+1)) | **9.352 mm** |
| εeff (patch) | 3.3648 |
| ΔL (fringing) | 0.2400 mm |
| Length L = λ₀/(2√εeff) − 2ΔL | **7.303 mm** |
| Slot conductance G1 / mutual G12 | 1.1922 mS / 0.5701 mS |
| Edge resonant resistance R_edge = 1/(2(G1+G12)) | 283.7 Ω |
| Fractional bandwidth (VSWR 2, Balanis approx.) | ≈ 1.7 % (≈ 179 MHz) — chirp bandwidth B is TBD in the parameter table; verify B fits |

Feed network per row (source: §3):

| Element | Z | Width | Length | Note |
|---|---|---|---|---|
| Inter-patch link | 100 Ω | 0.278 mm | 8.841 mm (λg/2, εeff 2.608) | patches in phase (resonant series feed) |
| Centre-to-centre patch spacing along the row | — | — | 16.143 mm = 0.565 λ₀ | fixed azimuth beam (no scan along the row) |
| Row input resistance ≈ R_edge/M | 35.5 Ω | — | — | standing-wave array, in-phase patches |
| Quarter-wave transformer √(50·R_in) | 42.1 Ω | 1.451 mm | 4.182 mm | |
| 50 Ω lead to connector | 50 Ω | 1.112 mm | 10.0 mm (equal on all rows, D-06) | εeff 2.852, λg 16.91 mm |

Panel (source: §4):

| Item | Value |
|---|---|
| Board outline | **165 × 248 mm** (rows start x = 36.18 mm; row 1 centre y = 16.68 mm) |
| Row length (8 patches + 7 links) | 120.30 mm |
| Mounting | 6 × Ø3.2 mm (M3 inferred) at 5 mm from the edges |
| Connectors | 16 × end-launch 2.92 mm on the left edge at 14.3 mm pitch (body width ≤ 12 mm — e.g. Southwest 1092-series, Amphenol 901-10510; **verify footprint**) |
| Estimated HPBW azimuth (row, 8 × 16.1 mm) | ≈ 11.2° (uniform) |
| Estimated HPBW elevation (16 × 14.3 mm) | ≈ 6.3° (matches HW-ANT-10: 6.3°) |
| Estimated directivity (aperture 129 × 229 mm, η_ap 0.7 assumed) | ≈ 25.0 dBi (parameter table says ~20 dBi TBD) |
| Series-feed frequency squint | the row beam tilts with frequency; with B TBD this must be checked in simulation (corporate feed is the fallback, D-02) |

## 8.3 Board and fabrication data

Native editable board `engineering/DESIGN/ANTENNA/kicad/aeris10_patch_array.kicad_pcb` (KiCad 8+/10, RO4350B stack-up entered); exports in `kicad_exports/` generated with kicad-cli (all steps exit 0 on 2026-10-09: drc, gerbers, drill, pdf, svg, step, stats, render — source: `kicad_exports/EXPORT_LOG.md`). Gerber set: `aeris10_patch_array-F_Cu.gtl`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Silkscreen.gto`, `-Edge_Cuts.gm1`, `-job.gbrjob`; drill files in `kicad_exports/drill/`; `aeris10_patch_array.step`; `aeris10_patch_array_top.pdf`; `aeris10_patch_array_F_Cu.svg`.

Board statistics (source: `kicad_exports/board_statistics.md`, KiCad report of 2026-10-09):

| Item | Value |
|---|---|
| Width × height | 165.0000 × 248.0000 mm, area 40920.00 mm² |
| Front / back copper area | 9867.896 mm² / 40475.063 mm² |
| Board stackup thickness | 0.5980 mm |
| Min drill diameter | 0.3000 mm |
| Pads: through hole / SMD / NPTH | 32 / 48 / 6 |
| Vias | 0 (no through, blind, buried or micro vias) |
| Components | 22 (16 SMD, 6 "unspecified" — the count matches the 6 NPTH mounting holes), all front side |
| Drill holes | 32 × Ø0.3 mm PTH (connector pads), 6 × Ø3.2 mm NPTH |

The statistics report also prints "Min track clearance / width 2147.4836 mm"; this equals 2 147 483 647 nm (INT32_MAX) and is read here as KiCad's placeholder for a board whose copper is made of polygons, not tracks — an interpretation of this manual, not a statement of the source file. DRC on the board (source: `kicad_exports/DRC_report.txt`): 46 items — 22 `lib_footprint_issues`, 17 `silk_over_copper`, 7 `silk_edge_clearance` (connector reference fields clipped by the board edge); none is a copper violation.

![Figure 34 — F8.1 — DSN-ANT-01 panel layout drawing: 16 rows × 8 patches, feed network, 2.92 mm connector positions, 165 × 248 mm outline with title block (status: PROPOSED DESIGN; source: engineering/DESIGN/ANTENNA/aeris10_patch_array_layout.png; produced by tools/design_antenna_array.py)](engineering/DESIGN/ANTENNA/aeris10_patch_array_layout.png)

![Figure 35 — F8.2 — DSN-ANT-01 KiCad 3-D render of the patch panel, top side (status: PROPOSED DESIGN; source: engineering/DESIGN/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png; produced by kicad-cli pcb render)](engineering/DESIGN/ANTENNA/kicad_exports/aeris10_patch_array_render_top.png)

## 8.4 Simulation of one row (DSN-ANT-01-SIM)

openEMS 0.0.36+ built from source (python-openEMS in a Python 3.12 venv), model `openems_patch_row.py`, runner `tools/design_antenna_tune.py`, 1.56 M cells, ~73 s per run, end criterion −40 dB (source: `simulation/TUNING_LOG.md`). Tuning iterations:

| iter | L_SCALE | f_res (GHz) | S11 at f_res (dB) | S11 at 10.5 GHz (dB) | −10 dB band (MHz) | D_row (dBi) |
|---|---|---|---|---|---|---|
| 0 | 1.0000 | 11.092 | -37.6 | -18.0 | 2362 | 11.51 |
| 1 | 1.0564 | 10.830 | -30.6 | -10.8 | 1958 | 11.35 |
| 2 | 1.1274 | 10.560 | -27.6 | -6.3 | 1162 | 11.23 |

Selected: **L_SCALE = 1.0000** (the transmission-line patch length): S11 = −18.0 dB at 10.5 GHz, but the **contiguous −10 dB band around f₀ is only ≈ 128 MHz** — the 2362 MHz span in the table is the non-contiguous extent of all dips and must not be read as bandwidth; between the dips the match is −6…−8 dB, worst −6.2 dB within 10.3–10.7 GHz (source: `TUNING_LOG.md`; `tuning_result.json`: `BW_10dB_MHz_contiguous = 128`, `worst_S11_10.3_10.7_GHz_dB = -6.2`). Single-row directivity 11.51 dBi (16 rows → ≈ 23.5 dBi estimated). Lengthening the patches moves the deepest dip towards 10.5 GHz but narrows the band below the carrier, because the input match of this series-fed row is set by the transformer/feed rather than by a single patch resonance.

Model limits: PEC copper, lossy RO4350B, no connector, one row only, MUR boundaries, lumped 50 Ω port. **Design consequence:** the series-fed resonant row is inherently narrow-band; if the chirp bandwidth B (TBD) exceeds ≈ 100 MHz the row needs a travelling-wave (matched-load) or corporate feed, or a thicker substrate — open item for DSN-ANT-01 rev B. Not evaluated: beam squint vs. frequency, pattern at the band edges, ADAR1000 phase-calibration impact (source: `TUNING_LOG.md`).

![Figure 36 — F8.3 — One-row |S11| vs frequency from openEMS (L_SCALE 1.0): comb of narrow resonances, −18.0 dB at 10.5 GHz, ≈ 128 MHz contiguous −10 dB band (status: PROPOSED DESIGN (simulated); source: engineering/DESIGN/ANTENNA/simulation/s11_row.png; produced by tools/design_antenna_tune.py)](engineering/DESIGN/ANTENNA/simulation/s11_row.png)

## 8.5 Three-row mutual coupling

Model `openems_three_rows.py` (2026-10-09): centre row driven, neighbours at ±14.3 mm terminated in 50 Ω. At 10.5 GHz: S22 (centre row) −16.3 dB, S12 = S32 ≈ **−20.7 dB**; worst coupling over 9–12 GHz ≈ −18.8 dB (source: `TUNING_LOG.md` §Three-row mutual coupling; data `coupling_3rows.csv`, 401 samples 9–12 GHz — the figure below reads −16.3 / −20.7 / −20.7 dB at the sample nearest 10.5 GHz and the worst S12/S32 of −18.8 dB at 11.3475 GHz, both taken from the CSV by `manual/figures/plot_coupling.py`). Verdict (same source): coupling is at the −20 dB target of `ANTENNA_DESIGN_CALC.md` §7 at the carrier and slightly above it at the band edges — acceptable for a first panel, but the ADAR1000 phase calibration must be done with all rows terminated (array calibration), and the 16-row full-panel simulation remains open.

![Figure 37 — F8.4 — Three-row mutual coupling S12/S32 and centre-row S22 vs frequency, 9–12 GHz, from openEMS (status: PROPOSED DESIGN (simulated); source: engineering/DESIGN/ANTENNA/simulation/coupling_3rows.csv; produced by beta/gui/.venv/bin/python manual/figures/plot_coupling.py, matplotlib Agg)](manual/figures/antenna_coupling_3rows.png)

## 8.6 Verification plan before fabrication

Copied from `ANTENNA_DESIGN_CALC.md` §7 with the current state:

1. Run `openems_patch_row.py` (openEMS ≥ 0.0.36 + python-openEMS): sweep 9.5–11.5 GHz; tune L (±0.3 mm) and `qw_len` until |S11| < −10 dB at 10.5 GHz ± B/2 — **done for L (three iterations, §8.4); the ±B/2 criterion cannot be applied while B is TBD; the ≈ 128 MHz contiguous band is the result to compare against B.**
2. Simulate 3 adjacent rows for mutual coupling (S21 between row ports < −20 dB target) — **done (§8.5): −20.7 dB at f₀, −18.8 dB worst in 9–12 GHz.**
3. Fabricate one 3-row coupon; measure S11/S21 on a VNA; compare with simulation; update `design_parameters.json` — **not done.**
4. Only then release the 16-row panel (`kicad_exports/` Gerbers) and record the result in `engineering/VALIDATION/DRAWING_CHECKS.md` — **not done; the Gerbers exist but are not released.**

## 8.7 Open items

| ID | Item | Status | Source |
|---|---|---|---|
| K8 | Antenna variant (patch vs slotted waveguide) — proposal selects patch (D-01); owner decision pending | OPEN | `docs/SYSTEM/BLOCK_DIAGRAM.md`; D-01 |
| G-06 | Element geometry, substrate, feed, radome of the *original* design — no source data; the proposal replaces, not recovers, it | BLOCKED — MISSING DATA | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` |
| — | Chirp bandwidth B TBD → feed topology decision (series resonant vs travelling-wave/corporate, D-02 fallback) | OPEN | `TUNING_LOG.md`; `ANTENNA_DESIGN_CALC.md` §2 |
| — | 2.92 mm end-launch connector footprint (body ≤ 12 mm) to verify | OPEN | `ANTENNA_DESIGN_CALC.md` §4 |
| — | Beam squint vs frequency, band-edge pattern, 16-row full-panel simulation | OPEN | `TUNING_LOG.md` |
| — | 3-row coupon fabrication and VNA measurement; array calibration procedure with all rows terminated | OPEN | §8.6 |
| — | Mounting of the panel on the heat spreader (6 × M3, 2.4 mm nylon spacers) and radome window — chapter 10 | PROPOSED DESIGN | `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` rows 3, 8 |
| — | PA n ↔ antenna row n cable assignment and equal-length coax set (CBL-049…CBL-139) | PROPOSED | `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` |


---

<!-- chapter 9: FPGA→host path (options A/B), 22 V PA supply module -->
# Host link (FPGA → host, options A/B) and 22 V PA supply module

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** host data path DSN-LINK-01 PROPOSED DESIGN; option B (SPI bridge through the STM32 CDC) implemented as BETA in `beta/fpga`, `beta/stm32`, `beta/gui` (simulated and unit-tested, never run on hardware); option A (FT601 on Main Board rev. B) is a pin plan plus a partially routed KiCad proposal whose 32-bit bus is blocked by the existing bank-35 fan-out (layout-owner decision required); 22 V PA supply DSN-PSU-01 PROPOSED DESIGN (block schematic, BOM, requirement table; no component-level schematic, no bench test). Figure F9.1 PROPOSED DESIGN; figure F9.2 BETA. Decisions D-16…D-19 and D-14 are not approved by the owner (chapter 17 §2).

**Sources:** `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md`, `engineering/DESIGN/HOST_LINK/README.md`, `ft601_pin_assignment.csv`, `ft601_added_parts_BOM.csv`, `option_b_signal_map.csv`, `ft601_bank35.xdc`; `beta/fpga/README.md` (host path, results), `beta/fpga/CHANGELOG.md`; `beta/stm32/README.md`, `beta/stm32/CHANGELOG.md`, `beta/stm32/DECISIONS.md` D-17/D-18; `beta/gui/README.md`, `beta/gui/CHANGELOG.md`; `beta/pcb/MAIN_BOARD_REVB/README.md`, `UNROUTED.md`, `NETLIST_DELTA.csv`; `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/README.md`, `DSN-PSU-01_BOM.csv`; `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5.

**Planned figures:** F9.1 DSN-PSU-01 block schematic; F9.2 Main Board rev. B isometric render.

## 1. Problem (conflict K3)

The RTL streams radar data through an FT601 USB 3.0 FIFO (`usb_data_interface.v`), but on the Main Board **U6 (FT601Q) has 0 of 77 pins connected** — only the decoupling of its `+3V3_FT` rail exists (L19, C184–C186). The only wired host link is the STM32 USB-FS CDC (X53) (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §1).

### 1.1 Data-rate budget (source: `HOST_LINK_DESIGN.md` §2, copied verbatim)

| Quantity | Value | Basis |
|---|---|---|
| Range-Doppler cells per beam position | 64 × 32 = 2048 | `doppler_processor.v` (RANGE_BINS 64, 32 chirps) |
| Beam-position frame time | 5647.4 µs | `main.cpp:180-186` |
| Raw RTL packet stream (44 B per cell) | **16.0 MB/s** | `usb_data_interface.v` (11 × 32-bit words) |
| Compact map frame (8-bit log-magnitude per cell + header + ≤ 32 detections + CRC) | 2164 B → **383 kB/s** | this design, §5 |
| STM32 USB-FS CDC practical limit | ≈ 0.8–1.1 MB/s | USB 2.0 FS bulk (19 × 64 B per 1 ms frame max) |
| SPI1 STM32 ↔ FPGA (existing lines) | 27 Mbit/s ≈ 3.3 MB/s (DMA) | APB2 108 MHz / 4 (beta clock tree) |
| FT601 245 sync FIFO, 32 bit @ 100 MHz | up to 400 MB/s | FT601 |

Conclusion of the source: the raw stream needs the FT601 (option A); the compact map fits the existing STM32 path with 3× margin (option B).

### 1.2 Options and decisions (source: `HOST_LINK_DESIGN.md` §3, copied verbatim)

| | A — FT601 on Main Board rev. B | B — SPI bridge via STM32 (no PCB change) | C — Ethernet mezzanine on bank 35 (future) |
|---|---|---|---|
| Hardware change | route U6 to bank 35 (46 I/Os), add USB 3 connector, crystal, RREF, ESD (`ft601_added_parts_BOM.csv`) | none: DIG_5/6/7 + SPI1 are already routed to the FPGA | new PCB with RGMII PHY on the 50 free bank-35 pins |
| Throughput | 400 MB/s | ≤ 1 MB/s (CDC-bound) | 100 MB/s |
| Firmware/RTL | RTL already written (fix 2-bit BE → 4-bit; honour TXE_N); host driver FTDI D3XX | new RTL `host_bridge_spi.v` + packer; STM32 `host_bridge.c`; GUI parser | new MAC/UDP stack |
| Risk | 10-layer board respin; USB 3 SI | protocol only; SPI1 shared with ADAR1000 (time-multiplexed) | highest |
| Decision | **D-16: target for rev. B** | **D-17: implement now (BETA)** | D-18: documented only |

Decision D-19 for the RTL: widen `ft601_be` to 4 bits, drive `BE = 4'b1111` for full words, respect `TXE_N` back-pressure, add `ft601_reset_n`/`wakeup_n`/`siwu_n` as outputs — recorded for `beta/fpga`, not yet applied there (source: `HOST_LINK_DESIGN.md` §4).

## 2. Option A — FT601 on Main Board rev. B (PROPOSED DESIGN)

### 2.1 Pin plan

`ft601_pin_assignment.csv` maps every FT601 signal to a free bank-35 pad, with CLK on the MRCC pin C4 = `IO_L12N_T1_MRCC_35`; `ft601_bank35.xdc` (60 lines) is the matching constraint fragment. The table has 47 signal rows: CLK, DATA_0..31, BE_0..3, TXE_N, RXF_N, WR_N, RD_N, OE_N, SIWU_N, RESET_N, WAKEUP_N, GPIO0, GPIO1 — all LVCMOS33, bank 35 VCCO = `+3V3_FPGA` on the schematic (source: `engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv`, 48 lines including header; `ft601_bank35.xdc` header). FT601 pad numbers come from the EAGLE library symbol used in the schematic (U6 `FT601Q-B-T`); the **FT601 datasheet is not in the repository** — AC timing, RREF value, VBUS limits and the 1.0 V core supply arrangement (VD10 pins) must be verified against it before the schematic is edited. Rev. B schematic work per the source: connect U6 VCC33 (pads 20/24/38) and VCCIO (14/49/59/68) to `+3V3_FT`, GND pads, the 46 signals per the CSV, XI/XO crystal, RREF, VBUS divider, D±/SS pairs to the new connector through the ESD array; route the 32-bit bus as a length-matched group (±25 mm, 100 MHz single-ended, 50 Ω) on the two bank-35 side layers (source: `HOST_LINK_DESIGN.md` §4). The full pin table is reproduced in section 9 of this chapter.

### 2.2 Parts to add for rev. B (source: `ft601_added_parts_BOM.csv`, copied verbatim)

| ref | qty | description | proposed_part | note |
|---|---|---|---|---|
| J_USB3 | 1 | USB 3.1 Gen1 receptacle (Type-C, USB 2.0 + one SuperSpeed pair used) or USB 3.0 micro-B | GCT USB4085-GF-A (Type-C) / Amphenol GSB4211111WEU (micro-B 3.0) | VERIFY pin-out; SS pairs TODP/TODN ↔ RIDP/RIDN per FT601 datasheet |
| Y_FT | 1 | Crystal 30 MHz ±30 ppm, 18 pF | Abracon ABM8-30.000MHZ-B2-T | FT601 XI/XO (pads 21/22) + 2 × 18 pF (VERIFY load per datasheet) |
| R_RREF | 1 | Resistor 3.24 kΩ 1 % 0402 | Yageo RC0402FR-073K24L | FT601 RREF (pad 27) — value per FT60x datasheet, VERIFY |
| C_VD10 | 4 | Capacitor 4.7 µF 6.3 V 0402 + 100 nF | Murata GRM155R60J475ME47D | 1.0 V core pins VD10/VD10_2..4/DV10 (pads 3,30,33,39,48): FT60x internal regulator output, decouple each — VERIFY |
| C_AVDD | 2 | Capacitor 100 nF / 1 µF 0402 | Murata GRM155R71C104KA88D | AVDD/VDDA (pads 2, 28) analogue 3.3 V via ferrite from +3V3_FT |
| FB_A | 1 | Ferrite bead 600 Ω@100 MHz 0603 | Murata BLM18PG601SN1D | +3V3_FT → AVDD |
| D_ESD | 1 | USB 3.0 ESD array (SS + HS) | TI TPD4E05U06 | on connector side of the SS and D± pairs |
| R_VBUS | 2 | Resistor divider 10 k / 3.3 k (VBUS detect, pad 37) | Yageo RC0402 | VERIFY VBUS pin voltage limit in datasheet |
| L19/C184-C186 | 0 | already in the schematic: +3V3_FT = +3V3_FPGA via L19; 10 µF + 100 nF + 1 nF | — | present (U6 pads 20, 24, 38 VCC33; 14, 49, 59, 68 VCCIO) — nets to be connected |

### 2.3 Rev. B layout outcome (BETA PROPOSAL, `beta/pcb/MAIN_BOARD_REVB/`)

Status of the directory: "BETA PROPOSAL — explicit netlist change (rev. B); partially routed; DRC-checked; not reviewed by the original designer; not fabricated." The EAGLE schematic has **not** been changed and no longer matches this board; the designer must enter the same connections and parts in the schematic, verify them against the FT601 datasheet and re-annotate before any rev. B layout is released. Source board: `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb` (rev. A BETA, unchanged); reproducible with `beta/pcb/tools/beta_revb_ft601.py` (source: `beta/pcb/MAIN_BOARD_REVB/README.md`, header).

![Figure 38 — F9.2 — Main Board rev. B isometric render with the FT601 cluster and USB-C receptacle placed at the left board edge; the 32-bit FIFO bus is unrouted — BETA (source: beta/pcb/MAIN_BOARD_REVB/MAIN_BOARD_REVB.kicad_pcb; produced by kicad-cli pcb render, exports/3d)](beta/pcb/MAIN_BOARD_REVB/exports/3d/MAIN_BOARD_REVB_render_isometric.png)

DRC result (source: `MAIN_BOARD_REVB/README.md` §1, copied verbatim):

| Check | Rev. A BETA (`MAIN_BOARD/`) | Rev. B after netlist change, before routing | Rev. B after routing (exports) |
|---|---|---|---|
| unconnected_items | 0 | 129 | 59 |
| clearance | 72 | 76 | 72 |
| copper_edge_clearance | 0 | 0 | 1 |
| courtyards_overlap | 0 | 2 | 2 |
| hole_clearance | 87 | 87 | 87 |
| shorting_items | 125 | 125 | 125 |
| silk_edge_clearance | 3 | 3 | 3 |
| silk_over_copper | 199 | 199 | 199 |
| silk_overlap | 199 | 199 | 199 |
| solder_mask_bridge | 199 | 199 | 199 |
| track_dangling | 130 | 130 | 130 |
| track_width | 0 | 0 | 14 |
| via_dangling | 35 | 35 | 40 |
| **DRC total** | 1049 | 1055 | 1071 |

Routing result (source: `MAIN_BOARD_REVB/README.md` §1 bullets; `UNROUTED.md` §1):

- Routed and connected: 17 of the 64 new nets (USB D±, both SuperSpeed RX lines, SSTX_N and both SSTX_C lines, CC1/CC2, USB_VBUS, FT_VBUS_DET, FT_RREF, FT_XI, FT_GPIO1, partly +3V3_FT/FT_VD10/FT_AVDD/FT_XO).
- **The 32-bit FIFO bus and its control lines (46 of 47 FPGA-side signals) are NOT routed.** Root cause, measured: 36 of the 47 bank-35 balls of U42 (XC7A50T FTG256, 1.0 mm pitch) have **no free position for an escape via** — the four dog-bone positions around each ball are already occupied by the existing BGA fan-out vias/traces of neighbouring balls. Balls with no free position: A2, A3, A7, B1, B2, B6, C1, C2, C3, C4, C6, D1, D3, D4, D6, E1, E2, E3, E5, E6, F2, F3, F4, F5, G4, G5, H4, H5, J1, J3, J5, K1, K2, K3, K5, L2; one free position for A4, A5, B4, B5, B7, C7, G1, H1, H3; two for G2, H2. Freerouting (1 pass, 25 min, existing copper locked) fanned out the FT601 side but could not reach these balls; its partial copper on the 47 open bus nets (127 items) was removed again so the board is left clean.
- What is needed (layout owner): re-do the bank-35 corner breakout of U42 (outer two rows on F.Cu, inner rows by dog-bone vias to In2/In3/In5/In7, which requires moving existing vias of adjacent nets), then route the 46 nets as one group at 0.204 mm, length-matched to ±25 mm; alternatively choose bank-35 balls on the two outer rows only, which would require revising `ft601_pin_assignment.csv` together with the XDC. This is "a layout-owner decision outside this BETA's 'existing tracks locked' rule"; no re-done fan-out exists in the repository at the time of writing.
- New DRC items caused by rev. B copper: 9 `track_width` (Freerouting neck-down 0.075 mm on +3V3_FT/CC1/CC2 at 0.4 mm-pitch pads; to be widened to 0.1 mm), 2 courtyard overlaps (Y_FT ↔ C_XI/C_XO — move the load caps 0.5 mm), 1 copper-edge (USB_CC2 inner track 0.2 mm from the J_USB3 NPTH peg), 5 dangling vias (+3V3_FT ×4, USB_SSTX_C_P). Two further scripted clean-ups (second restricted Freerouting pass on the open power nets; widening the neck-downs) were prepared but not executed in that session.

Routing geometry (source: `MAIN_BOARD_REVB/README.md` §2, copied verbatim):

| Group | Rule used | Achieved |
|---|---|---|
| FT_BUS (FT_DATA_0..31, FT_BE_0..3, FT_CLK, control, GPIO) | netclass `FT_BUS` 0.204 mm (50 Ω microstrip on the 0.102 mm RO4350B outer layer per `../MAIN_BOARD/FAB_NOTES.md`; on inner layers ≈ 42 Ω stripline estimate, FR-4, not field-solved), clearance 0.1 mm (DRU), length-match target ±25 mm | only `FT_GPIO1` routed: 37.57 mm, 3 vias, F.Cu/In2/In7 — **no skew figure exists for the bus because it is unrouted**; FT601→bank-35 Manhattan distance is 20–35 mm, so ±25 mm is achievable once the breakout exists |
| USB SuperSpeed + D± | netclass `USB_DIFF` width 0.204 mm, pair gap 0.18 mm (≈ 90 Ω edge-coupled microstrip on RO4350B h = 0.102 mm, closed-form estimate 91 Ω, fab to solve) | Freerouting routes pair members as single traces (coupling not enforced): SSRX_P/N 29.28 / 29.41 mm (skew 0.13 mm), D+/D− 23.72 / 27.12 mm (skew 3.4 mm), SSTX_C_P/N 9.08 / 8.72 mm, SSTX_N 16.08 mm (SSTX_P open); neck-down to 0.153 mm at pads. **Pairs must be re-routed coupled (KiCad diff-pair router, 0.204/0.18 mm) before release** |
| Power `FT_PWR` (FT_VD10, FT_AVDD, USB_VBUS) | 0.3 mm | USB_VBUS 34.5 mm, FT_AVDD 18.6 mm; FT_VD10 only partially connected |

Netlist delta: 64 new nets, 123 pad connections on existing parts (U6, U42), 71 pad connections on 20 added parts; U6 pads 2, 14, 20, 24, 28, 37, 38, 49, 59, 68 were on single-pin nets in rev. A and were moved to the new nets. Every connection is listed in `MAIN_BOARD_REVB/README.md` §3 and `NETLIST_DELTA.csv` (258 rows) (source: `MAIN_BOARD_REVB/README.md` §3, lead-in).

Added parts as placed in rev. B (source: `MAIN_BOARD_REVB/README.md` §4, copied verbatim):

| Ref | Footprint (KiCad 10 library) | Value | MPN | Position (mm), rot | Note |
|---|---|---|---|---|---|
| J_USB3 | `Connector_USB:USB_C_Receptacle_Amphenol_12401610E4-2A` | USB-C 3.1 receptacle | Amphenol ICC 12401610E4#2A | (4.00, -208.00), 270° | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| D_ESD1 | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | TPD4E05U06 | Texas Instruments TPD4E05U06DQAR | (12.50, -210.00), 0° | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| D_ESD2 | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | TPD4E05U06 | Texas Instruments TPD4E05U06DQAR | (12.50, -206.00), 0° | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| C_SSTX_P | `Capacitor_SMD:C_0402_1005Metric` | 100nF | Murata GRM155R71C104KA88D | (16.50, -211.20), 0° | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| C_SSTX_N | `Capacitor_SMD:C_0402_1005Metric` | 100nF | Murata GRM155R71C104KA88D | (16.50, -210.00), 0° | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| R_CC1 | `Resistor_SMD:R_0402_1005Metric` | 5.1k | Yageo RC0402FR-075K1L | (11.00, -214.00), 0° | Type-C Rd 5.1 kΩ (device) — added because a USB-C receptacle was chosen |
| R_CC2 | `Resistor_SMD:R_0402_1005Metric` | 5.1k | Yageo RC0402FR-075K1L | (11.00, -202.50), 0° | Type-C Rd 5.1 kΩ (device) |
| R_VBUS_1 | `Resistor_SMD:R_0402_1005Metric` | 10k | Yageo RC0402FR-0710KL | (32.50, -201.90), 90° | VERIFY VBUS pin limit |
| R_VBUS_2 | `Resistor_SMD:R_0402_1005Metric` | 3.3k | Yageo RC0402FR-073K3L | (33.70, -201.90), 90° | VERIFY VBUS pin limit |
| R_RREF | `Resistor_SMD:R_0402_1005Metric` | 3.24k 1% | Yageo RC0402FR-073K24L | (26.30, -201.90), 90° | value per FT60x datasheet — VERIFY |
| C_VD10_1 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (20.30, -210.40), 90° | VD10/DV10 decoupling — VERIFY |
| C_VD10_2 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (27.50, -201.90), 90° | VD10/DV10 decoupling — VERIFY |
| C_VD10_3 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (28.70, -201.90), 90° | VD10/DV10 decoupling — VERIFY |
| C_VD10_4 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (29.90, -201.90), 90° | VD10/DV10 decoupling — VERIFY |
| FB_A | `Inductor_SMD:L_0603_1608Metric` | 600R@100MHz | Murata BLM18PG601SN1D | (18.00, -214.60), 0° | +3V3_FT -> AVDD/VDDA |
| C_AVDD_1 | `Capacitor_SMD:C_0402_1005Metric` | 100nF | Murata GRM155R71C104KA88D | (20.30, -212.60), 90° |  |
| C_AVDD_2 | `Capacitor_SMD:C_0402_1005Metric` | 1uF | Murata GRM155R61A105KE15D | (19.20, -212.60), 90° |  |
| Y_FT | `Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm` | 30MHz 18pF | Abracon ABM8-30.000MHZ-B2-T | (22.50, -199.60), 0° | ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY |
| C_XI | `Capacitor_SMD:C_0402_1005Metric` | 18pF C0G | Murata GRM1555C1H180JA01D | (19.60, -198.75), 0° | load cap — VERIFY against crystal CL |
| C_XO | `Capacitor_SMD:C_0402_1005Metric` | 18pF C0G | Murata GRM1555C1H180JA01D | (25.20, -199.20), 0° | load cap — VERIFY against crystal CL |

Deviations from `ft601_added_parts_BOM.csv` (source: `MAIN_BOARD_REVB/README.md` §4, closing paragraph): USB-C Amphenol 12401610E4#2A (24-pin, has SS pins) instead of GCT USB4085 (the KiCad USB4085 footprint is USB 2.0-only); a second TPD4E05U06 for D± (one 4-channel array cannot cover 6 lines); added 2 × 100 nF SSTX AC-coupling capacitors (USB 3 requirement) and 2 × 5.1 kΩ CC pull-downs (required for a Type-C device receptacle); only the TX1/RX1 SuperSpeed lane is wired (no orientation mux → SS in one plug orientation only); C_VD10 as 4 × 4.7 µF (100 nF companions not placed). Placement: J_USB3 on the left board edge nearest U6, ESD arrays at x = 12.5, crystal/RREF/VBUS divider/VD10 capacitors in the free band below U6, all on F.Cu; placement is a proposal, thermal/EMC not assessed (source: same, §6).

Open items on the routed power/clock/USB nets (source: `MAIN_BOARD_REVB/UNROUTED.md` §2, copied verbatim):

| Net | Open connections | What is needed |
|---|---|---|
| FT_VD10 | 5 | connect U6 pads 3/30/33/39/48 together and to C_VD10_1..4 — the QFN pads face other-net pads on all sides; route on F.Cu around the exposed pad corners or via-in-pad to an inner pour |
| +3V3_FT | 5 | feed from the L19/C184-186 filter (y ≈ −232) to U6 VCC33/VCCIO pads; 4 autorouter vias are dangling (remove or connect) |
| FT_AVDD | 1 | U6 pad 2 to C_AVDD_1 (0.6 mm stub) |
| FT_XO | 1 | U6 pad 22 to Y_FT pad 3 |
| USB_SSTX_P | 1 | U6 pad 32 to C_SSTX_P — route coupled with USB_SSTX_N (0.204/0.18 mm) |

Prepared but not executed (source: `UNROUTED.md` §3): (1) second Freerouting pass restricted to FT_VD10, +3V3_FT, FT_AVDD, FT_XO, USB_SSTX_P; (2) widen the 14 Freerouting neck-downs below 0.1 mm to 0.1 mm; (3) move C_XI / C_XO 0.5 mm away from Y_FT. The export package of rev. B (all 24 export steps exit 0, `exports/EXPORT_LOG.md`) exists but describes an unfinished board (source: `MAIN_BOARD_REVB/README.md` §7).

## 3. Option B — SPI bridge through the STM32 (BETA)

### 3.1 Signals (source: `option_b_signal_map.csv`, copied verbatim)

| signal | schematic_net | stm32_pin | fpga_pin | direction | note |
|---|---|---|---|---|---|
| FPGA_CS_N (option B) | DIG_5 | STM32 PD13 (today configured INPUT in main.cpp:2313-2317 → becomes OUTPUT) | U42 H11 (IO_L19P_T3_A22_15) | STM32 → FPGA | active-low chip select for the bridge; ADAR1000 pass-through is gated off while low |
| DRDY (option B) | DIG_6 | STM32 PD14 (INPUT, EXTI14) | U42 G12 (IO_L19N_T3_A21_VREF_15) | FPGA → STM32 | a complete frame is in the FPGA TX FIFO |
| spare / ACK | DIG_7 | STM32 PD15 | U42 H12 (IO_L20P_T3_A20_15) | FPGA → STM32 | reserved (frame dropped / overflow flag) |
| SCLK | STM32_SCLK1 | STM32 PA5 (SPI1_SCK) | U42 J16 (IO_L23N_T3_FWE_B_15) | STM32 → FPGA | existing net, 3.3 V; ≤ 27 MHz (SPI1 on APB2 108 MHz, prescaler 4) |
| MOSI | STM32_MOSI1 | STM32 PA7 (SPI1_MOSI) | U42 H13 (IO_L20N_T3_A19_15) | STM32 → FPGA | existing; carries the bridge command byte |
| MISO | STM32_MISO1 | STM32 PA6 (SPI1_MISO) | U42 G14 (IO_L21P_T3_DQS_15) | FPGA → STM32 | existing; frame bytes, MSB first, mode 0 |
| ADAR_n_CS_3V3 | ADAR_1..4_CS_3V3 | STM32 GPIO | U42 bank 15 | STM32 → FPGA | unchanged; must all be HIGH during a bridge transfer (firmware guarantees; RTL also checks) |

Transfer (source: `HOST_LINK_DESIGN.md` §5): the STM32 waits for DRDY (EXTI on PD14), pulls `FPGA_CS_N` low, clocks one command byte (0x01 = read frame) and then reads the frame over MISO with DMA (SPI1 mode 0, MSB first, ≤ 27 MHz); the FPGA holds the ADAR1000 pass-through idle while `FPGA_CS_N` is low; the firmware never starts an ADAR1000 SPI transaction while a bridge read is in progress (both share SPI1). The STM32 forwards each frame unchanged over CDC (`AERIS_USB_SendBridgeFrame`), interleaved with the existing status strings; the GUI stream parser resyncs on the sync word (status strings never contain `0xA5 0x5A`).

### 3.2 Frame format (source: `HOST_LINK_DESIGN.md` §5, copied verbatim; little-endian; reference parser `engineering/DESIGN/HOST_LINK/gui/bridge_frame.py`)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | sync `0xA5 0x5A` |
| 2 | 1 | version = 1 |
| 3 | 1 | flags (bit0 = long-chirp set, bit1 = overflow since last frame) |
| 4 | 2 | sequence number |
| 6 | 1 | azimuth index (1..50) |
| 7 | 1 | elevation index (1..31) |
| 8 | 2 | chirp count |
| 10 | 1 | n_range = 64 |
| 11 | 1 | n_doppler = 32 |
| 12 | 2 | n_det (≤ 32) |
| 14 | 2 | reserved |
| 16 | 2048 | magnitude map, uint8 = 8·log2(abs(I)+abs(Q)) saturated, range-major |
| 2064 | 3·n_det | detections: range u8, doppler u8, mag u8 |
| end | 2 | CRC-16/CCITT-FALSE over bytes 0..end-1 |

Files (source: `HOST_LINK_DESIGN.md` §5): `rtl/host_bridge_spi.v` (SPI slave + frame FIFO, 1 BRAM), `rtl/rd_map_packer.v` (cell → frame builder, CRC), `rtl/tb_host_bridge.v` (self-checking iverilog test), `stm32/host_bridge.c/.h` (SPI1 DMA + EXTI + CDC forward), `gui/bridge_frame.py` (+ tests); integration into `beta/fpga`, `beta/stm32`, `beta/gui` is recorded in their CHANGELOGs.

### 3.3 Bridge command set v2 — register access (source: `HOST_LINK_DESIGN.md` §7, copied verbatim; RTL implemented 2026-10-09)

All transfers: `FPGA_CS_N` low, SPI mode 0, MSB first; first byte = command. Bytes marked ← are driven by the FPGA on MISO (the master clocks dummy 0x00). Implemented in `beta/fpga/rtl/host_bridge_spi.v` (copy in `engineering/DESIGN/HOST_LINK/rtl/`), firmware counterpart `beta/stm32/Core/Src/host_bridge_proto.c`, verified by `beta/fpga/tb/tb_host_bridge_top.v` (through `radar_system_top`) and `rtl/tb_host_bridge.v` (unit).

| Cmd | Total bytes | Bytes after the command | Reply | Meaning |
|---|---|---|---|---|
| 0x01 | 1 + frame + 2 | — | frame + CRC (as §3.2); all zeros when no frame is pending (no sync word) | read the pending range-Doppler frame (unchanged) |
| 0x02 | 8 | a0 = addr[7:0], a1 = addr[15:8], d0..d3 = data[7:0]..[31:24], xx | ← byte 7 = 0xA2 (ack = command accepted; the write commits in the clk domain within ~5 clk cycles) | write register word `addr` |
| 0x03 | 7 | a0, a1, xx, xx, xx, xx | ← bytes 3..6 = d0 d1 d2 d3 (little-endian). No turnaround byte: the read is launched when a0 is complete; a1 is accepted but not decoded (the map has 5 address bits, so a1 must be 0) | read register word `addr` |
| 0x04 | 9 | xx × 8 | ← bytes 1..8 = four little-endian u16: status word, RTL version (0x0002), frames produced, 0x0000 | status without touching the frame |
| other (incl. 0x00) | any | — | ← 0xEE on every following byte | unknown command (ignored) |

Status word (assembled in `radar_system_top.v`): bit0 frame ready (= DRDY), bit1 ADAR CS conflict (sticky: an ADAR1000 CS was low while `FPGA_CS_N` was low), bit2 ADC capture FIFO overflow (sticky, `ADC_CAPTURE_MODE = 1`), bit3 calibration lock (all 8 lanes locked), bit4 packer overflow (a frame was dropped since reset), bits 5..15 = 0. The status is sampled when the command byte completes (quasi-static values; `frames produced` may be one behind).

Register map — word addresses, **16-bit registers** (data[31:16] are ignored on write and read as 0). Source of truth: `beta/fpga/rtl/radar_control_regs.v` (address-map comment and the two `case` statements); the table is kept identical to it. `toggle` = write 1 to the bit to pulse the action, reads as 0; `level` = stored bit.

| Addr | Name | Access | Reset | Bits |
|---|---|---|---|---|
| 0x00 | CONTROL | rw | 0x0005 | bit0 use_long_chirp, bit1 adc_pwdn, bit2 usb_enable |
| 0x01 | CFAR_THR | rw | 10000 | [15:0] abs(I)+abs(Q) detection threshold |
| 0x02 | DECIM | rw | 0x0001 | [1:0] range decimation mode (01 = peak) |
| 0x03 | START_BIN | rw | 0 | [9:0] first range bin passed to the decimator |
| 0x04 | CAL_CTRL | rw | 0 | bit0 start auto calibration (toggle), bit1 manual tap load (toggle), bit2 bitslip load (toggle), bit3 pattern-check enable (level), bit4 blind method (level: 0 = ADC test pattern, 1 = CW tone at the IF) |
| 0x05 | CAL_LANE | rw | 0 | [2:0] lane for CAL_TAP / CAL_SLIP writes and CAL_LANE_INFO / CAL_BLIND_MIN reads |
| 0x06 | CAL_TAP | rw | 16 | [4:0] manual IDELAY tap |
| 0x07 | CAL_SLIP | rw | 0 | [1:0] BITSLIP pulses for a manual bitslip load |
| 0x08 | CAL_PATT | rw | 0x55AA | {pattern_b[7:0], pattern_a[7:0]} expected alternating ADC test codes |
| 0x09 | CAL_STAT | ro | — | {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]} |
| 0x0A | CAL_LANE_INFO | ro | — | {1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]} of CAL_LANE |
| 0x0B | CAL_ERR | ro | — | pattern-check error counter (saturating) |
| 0x0C | CAL_UNDET | ro | — | {8'b0, undetermined[7:0]} |
| 0x0D | CAL_BLIND_COEF | rw | 0xEC39 | signed Q1.14 cos(2π·f_IF/f_S) for the blind notch (0xEC39 = −5063 = 120 MHz at 400 MSPS) |
| 0x0E | CAL_BLIND_MARGIN | rw | 0x0040 | absolute part of the blind pass margin (a tap passes when metric ≤ min + margin + min/16) |
| 0x0F | ID | ro | 0xBE7A | beta build identifier |
| 0x10 | CAL_BLIND_MIN | ro | — | minimum blind metric (sum of abs(r) over the window, >> 4, saturated) of CAL_LANE |

Registers that earlier revisions of this section listed but that do **not** exist in the RTL (run bit, mixers enable, NCO tuning word) have been removed from the table; `use_long_chirp` is CONTROL bit0. STM32 API: `HostBridge_WriteReg(addr, value)`, `HostBridge_ReadReg(addr, &value)`, `HostBridge_Status(&st)`; exposed to the GUI through the existing settings path as a text command `REG W <addr> <value>` / `REG R <addr>` → reply `REG <addr> <value>` in the status stream (ASCII, so the bridge-frame parser passes it through) (source: `HOST_LINK_DESIGN.md` §7, closing paragraphs).

### 3.4 BETA implementation status per subsystem

**FPGA (`beta/fpga`, BETA).** `rd_map_packer` turns each 64 × 32 Doppler frame into a 2066..2162-byte frame and `host_bridge_spi` streams it to the STM32 as an SPI slave on the existing SCLK/MOSI/MISO nets with DIG_5 = `spi_bridge_cs_n` (H11), DIG_6 = `spi_bridge_drdy` (G12), DIG_7 = `spi_bridge_spare` (H12, packer overflow flag). While the bridge CS is low the ADAR1000 pass-through is gated (CS high, SCLK/MOSI idle on the 1.8 V side) and MISO is driven by the bridge; `system_status[1]` latches a conflict if any ADAR CS is low during a transfer. Beam indices come from the transmitter's STM32-toggle counters, the chirp count from the receiver's chirp pulses, `long_chirp` from the register map. The bridge drives the register map's write/read port (5-bit addresses, 16-bit data); register toggles cross SCLK → clk through 3-flop synchronisers; a read needs ≥ 8 SCLK periods between a0 and d0 (≥ 296 ns at 27 MHz, the fetch takes ≤ 5 clk cycles). Executed tests: `tb_host_bridge` — 3 detections, 32 detections (`det_wr` regression), command set v2 against a 4-word register model: PASS, 2075- and 2162-byte frames, CRC ok, v2 write/read-back/status/unknown ok; `tb_host_bridge_top` — v2 register commands (CFAR_THR 10000 → 150 written over SPI, 5 read-backs, 0x04 status before/with/after a frame, 0xEE), then one 64×32 frame after DRDY: PASS (~77 s), 2162-byte frame, 32 detections (only possible because the threshold write took effect), sync/dims/az-el/chirp-count/map/CRC ok, ADAR pass-through gated (source: `beta/fpga/README.md`, "What passed" rows 6e/6f and "Host path"). One defect was found and fixed in the copied packer: `det_wr` widened from 6 to 7 bits — with 6 bits the packer never left its header/detection state once `n_det ≥ 22`, so the frame never completed and DRDY never asserted (source: `beta/fpga/CHANGELOG.md`, "Host-link option B integration", row `rd_map_packer.v`). Unresolved for option B in the RTL: STM32 SPI1 timing versus the FPGA pins (XDC placeholders), BRAM inference of the SCLK-domain frame RAM read (asynchronous read registered on falling SCLK; Yosys maps it to 1,536 LUTs as RAM64M, chapter 11 §12), and the firmware rule that no ADAR1000 transaction overlaps a bridge read (source: `beta/fpga/README.md`, "Host path"; `beta/fpga_synth/README.md`, "Reading the numbers" item 2).

**STM32 (`beta/stm32`, BETA).** New `Core/Src/host_bridge.c` / `Core/Inc/host_bridge.h` (copies of `engineering/DESIGN/HOST_LINK/stm32/`): SPI1 bridge to the FPGA using the already-routed DIG_5 (PD13 → FPGA_CS_N, reconfigured as output), DIG_6 (PD14 → DRDY, EXTI14 rising), DIG_7 (PD15 spare); `Core/Src/host_bridge_proto.c` implements the HAL-free command set v2 (0x02 write/ack 0xA2, 0x03 read, 0x04 status) and the ASCII `REG W/R` parser/executor/reply formatter; `HostBridge_WriteReg/ReadReg/Status/ExecuteTextCommand` run over a transport that refuses while a frame read is active or any ADAR CS is low; the main loop executes a pending `REG` command after `HostBridge_Poll()` and replies with `CDC_Transmit_FS` (bounded 50 ms busy wait) (source: `beta/stm32/CHANGELOG.md`, "ADAR1000 vector-modulator tables + bridge command set v2"). Decision D-17: register access runs in the main loop, never in the USB ISR; one command slot; reply format `REG 0x%04X 0x%08X\r\n` (a write echoes the written value after the ack), `REG ERR\r\n` on syntax error, NACK, busy or SPI error. Decision D-18 records the framing assumptions (8-byte write with ack in byte 8, 7-byte read with data little-endian in bytes 3..6, 9-byte status with four u16) (source: `beta/stm32/DECISIONS.md` D-17, D-18). Build: FLASH 93 276 B, RAM 17 480 B, 0 errors; host tests 6/6 PASSED including `test_host_bridge_cmds.c` (bridge v2 byte sequences with a mock SPI: 0x02 + ack 0xA2 / no ack / 0xEE / transfer error, 0x03 LE decode, 0x04 status fields; ASCII `REG W/R` parser and reply formatting) (source: `beta/stm32/README.md` §3–4).

**GUI (`beta/gui`, BETA).** The default hardware path is the SPI bridge: the FPGA serves 64×32 log-magnitude frames over SPI, the STM32 forwards them unchanged over USB CDC, interleaved with status strings and `REG` replies; the raw 35-byte RTL packet path (option A, FT601) stays available with `--raw-ft601`. The "FPGA registers / ADC calibration" tab issues `REG W/R` over CDC with the same text protocol as the firmware (one command per USB transfer, timeout + retransmit, no request ID). In demo mode the simulator answers `REG` commands from an in-memory model of `radar_control_regs.v`. The GUI register map was brought to the final RTL map (RTL version 0x0002): `protocol/register_map.py` uses 5-bit addresses (`ADDR_MASK = 0x1F`, unmapped 0x11..0x1F), CAL_CTRL bit4 blind level, registers 0x0D `CAL_BLIND_COEF`, 0x0E `CAL_BLIND_MARGIN`, 0x10 `CAL_BLIND_MIN`; the register panel gained the blind-method controls and a per-lane `blind_min` read-out; `read_all` issues 3 commands per lane (client pacing test: 52 commands, 0 drops) (source: `beta/gui/CHANGELOG.md`, "2026-10-09 (final register map, RTL 0x0002)"; `beta/gui/aeris10_gui/protocol/register_map.py:18`; `beta/gui/README.md`, limitation 12). 72 tests pass; `--selftest` on the bridge link: 3 frames, 0 CRC errors, 31 REG replies, read-all OK; `--selftest --raw-ft601`: 6144 packets, 0 drops; PyInstaller bundle passes both self-tests (source: `beta/gui/README.md`, "BETA statement", "Run", "Test"; `beta/gui/CHANGELOG.md`, "Verification performed").

**Documentation state between the three BETA trees (observation MAN-04, chapter 17 §6).** The FPGA README and CHANGELOG state that command set v2 is implemented in the RTL, that the register write/read port is wired to `ctl_regs`, and that `HOST_LINK_DESIGN.md` §7 is kept identical to `radar_control_regs.v` (source: `beta/fpga/README.md`, "What was found and decided" item 5, "Host path"; `beta/fpga/CHANGELOG.md`, "Command set v2…"). The GUI tree has been brought to the same map and its earlier discrepancy items 1–3 are struck through as resolved (source: `beta/gui/CHANGELOG.md`, "Discrepancies / unresolved" and "2026-10-09 (final register map, RTL 0x0002)"). Two firmware documents still carry the earlier state: `beta/stm32/README.md` §6a ("The FPGA side of 0x02..0x04 is not implemented in `beta/fpga` yet", line 120) and `beta/stm32/DECISIONS.md` D-18 (same statement, "grep 2026-10-09"); the FPGA README's remaining-work item 8 still names the GUI `register_map.py` 4-bit mask as open although the file now has `ADDR_MASK = 0x1F` (source: `beta/fpga/README.md`, "Remaining work" item 8; `beta/gui/aeris10_gui/protocol/register_map.py:18`). These are stale statements, not functional gaps; the register path is consistent between the RTL, `HOST_LINK_DESIGN.md` §7, the firmware byte sequences and the GUI map, and it has not been exercised on hardware in any combination.

### 3.5 What remains for the host link (source: `HOST_LINK_DESIGN.md` §6; `engineering/DESIGN/HOST_LINK/README.md`, "Not done")

- Option A: Main Board rev. B schematic/layout (MDR-13) — the bank-35 breakout decision above; FT601 datasheet checks; FTDI D3XX host driver test; RTL changes of D-19.
- Option B: bench test of the SPI timing (level shifter path is 3.3 V, no translation needed), CDC throughput measurement, firmware arbitration of SPI1 with the ADAR1000 writes; end-to-end `REG` test on hardware.

## 4. 22 V PA drain supply module DSN-PSU-01 (PROPOSED DESIGN)

The RF PA boards need a 22 V drain supply (`VD`, xlsx row 59: 18–22 V, 2000 mA per board) that exists in no CAD file — conflict K4; the Power Board's input is 12–17 V and it has no 22 V rail (chapter 3 §4.1, rail `+22V0`/`VD`). DSN-PSU-01 closes K4 per decision D-14 with a block schematic, a BOM and a net summary; it has no component-level schematic, no layout and no bench test (source: `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/README.md`, header; `engineering/DESIGN/00_DESIGN_BASIS.md` §2, D-14).

![Figure 39 — F9.1 — DSN-PSU-01 block schematic: 2-phase synchronous boost 12–17 V → 22 V, LM5069 hot-swap enable from EN/DIS_RFPA_VDD, 16 high-side pulse gates from TX_GATE, bulk capacitance, 16 output terminals to the PA boards — PROPOSED DESIGN, no component-level schematic, not built (source: engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.svg; produced by tools/design_pa_supply_schematic.py)](engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.png)

### 4.1 Requirements (source: `PA_SUPPLY_22V/README.md`, copied verbatim)

| Requirement | Value | Source |
|---|---|---|
| Input | 12–17 V (system VIN via slip ring) | xlsx VIN |
| Output | 22 V ± 2 %, 8 A continuous, 46 A pulsed (11.5 % duty) | QPA2962 datasheet, timing |
| Bulk energy | ≥ 2734 µF total for ΔV ≤ 0.5 V per 30 µs chirp | `THERMAL_AND_PA_SUPPLY.md` §5 |
| Enable | `EN/DIS_RFPA_VDD` (existing STM32 pin) → hot-swap switch | `main.h` |
| Pulse gate | `TX_GATE` from the FPGA — **spare pin to allocate (UNRESOLVED)**; without it the system runs case A (591 W) | D-14 |
| Telemetry | PGOOD/FAULT to the MCU (pin to allocate); per-PA drain current already measured by INA241 on the Main Board | schematic |
| Mechanical | 120 × 80 × 25 mm on the head rear wall (DSN-MECH-01) | layout |

### 4.2 Sizing (source: `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5, copied verbatim)

| Quantity | Value |
|---|---|
| Peak drain current (all 16 PAs at ID_max 2.848 A) | **45.6 A** during each 30 µs chirp |
| Average current, case B (IDQ × gate duty + RF increment × RF duty) | **3.47 A** → 76 W |
| Average current, case A (continuous bias) | 27.3 A → 600 W (not supported by the proposal) |
| Bulk capacitance for ΔV ≤ 0.5 V over a chirp (total) | **2734 µF** → ≥ 220 µF low-ESR polymer per PA board (local, 171 µF each) + 2 × 1000 µF/35 V at the switch module |
| Input current at VIN_min 12 V, η 92% | 6.9 A average (case B) |
| Converter | synchronous boost 12–17 V → 22 V, 2-phase interleaved (LM5122 ×2 or equivalent), 150 W continuous rating, 300 kHz, 2 × 10 µH / 15 A inductors, output ripple < 100 mV |
| Protection / enable | LM5069 hot-swap controller + N-FET high-side switch on the 22 V bus, EN from `EN/DIS_RFPA_VDD` (STM32), current limit 12 A average, dv/dt-limited turn-on; status to the MCU |
| Per-PA pulse gating | 16 × high-side P-FET (−40 V, 30 A pulsed) with fast high-side driver (e.g. LTC7003, ≤ 100 ns), common `TX_GATE` TTL input from the FPGA (spare I/O to be allocated — UNRESOLVED), local 220 µF per channel |
| Sequencing | VG (−4 V via DAC5578) before VD (firmware already does this); gate switch only after `EN/DIS_RFPA_VDD`; power-down reverse |

The drain-gating requirement follows from the thermal analysis: with the drain continuously biased (case A) the 16 QPA2962 dissipate 591 W and the 2-D plate model gives ≈ 213 °C; with per-chirp gating at 11.5 % duty (case B) 68 W, plate 64 °C and PA base ≈ 73 °C at 45 °C ambient (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §9; `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §1). The BOM's gate switch (N-MOSFET with LTC7003) and the thermal document's "high-side P-FET" describe the same function with different device polarity; the BOM is the later, part-level statement, and the component-level design (MDR-12) must settle it.

### 4.3 Bill of materials (source: `PA_SUPPLY_22V/DSN-PSU-01_BOM.csv`, copied verbatim)

| ref | qty | description | proposed_part | section |
|---|---|---|---|---|
| J1 | 1 | DC input terminal 2-pole 16 A | Phoenix 1792270 or AK300/2 | input |
| F1 | 1 | Fuse 20 A 32 V automotive | Littelfuse 0297020 | input |
| D1 | 1 | TVS 18 V SMB | SMBJ18A | input |
| FL1 | 1 | CM choke 10 µH 15 A + 4×4.7 µF/50 V X7R | Würth 744 823 110 / GRM32ER71H475K | filter |
| U1,U2 | 2 | Sync boost controller | TI LM5122MH | boost |
| Q1–Q4 | 4 | N-MOSFET 100 V 100 A | TI CSD19532Q5B | boost |
| L1,L2 | 2 | Inductor 10 µH 15 A | Coilcraft XAL1580-103 | boost |
| C_out | 4 | Polymer 100 µF/35 V | Panasonic 35SVPF100M | boost |
| C_bulk | 2 | Electrolytic 1000 µF/35 V low ESR | Nichicon UHE1V102MHD | boost/bulk |
| U3 | 1 | Hot-swap controller 9–80 V | TI LM5069MM-1 | switch |
| Q5 | 1 | N-MOSFET 100 V 200 A D2PAK | TI CSD19536KTT | switch |
| Rs | 1 | Sense 2 mΩ 3 W | Bourns CSS2H-2512R-L200F | switch |
| U4–U19 | 16 | High-side gate driver ≤ 100 ns | ADI LTC7003 | gate |
| Q6–Q21 | 16 | N-MOSFET 100 V | TI CSD19532Q5B | gate |
| C_loc | 16 | Polymer 220 µF/35 V | Panasonic 35SVPF220M (or on each PA board) | gate |
| OUT1–16 | 16 | Screw terminal 2-pole | AK300/2 (matches the PA board) | output |

### 4.4 Interfaces and next steps

Cabling: slip ring VIN → DSN-PSU-01 IN (CBL-142, 2 × 2-wire 16 AWG) and DSN-PSU-01 OUT1..16 → PA `22V` terminals (CBL-050, 056, …, 140; 2-wire 18 AWG twisted, AK300/2) in the proposed harness schedule (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, rows CBL-050…CBL-142; chapter 3 §5). The module occupies 120 × 80 × 25 mm on the head rear wall in the proposed mechanical layout (DSN-MECH-01). Next steps (MDR-12, source: `PA_SUPPLY_22V/README.md`): KiCad component-level schematic → layout (4-layer, 2 oz) → bench test of one gate channel with a 30 µs / 45 A dummy load → EMC pre-check of the boost. Decision needed from the owner: D-14, in particular the `TX_GATE` line (FPGA spare pin, UNRESOLVED — none of the 116 unconstrained RTL ports has a board net; chapter 11 §7) and the telemetry pin (chapter 17 §2).

## 5. Appendix — FT601 pin assignment, option A (source: `engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv`, copied verbatim; identical to `ft601_bank35.xdc` and `beta/pcb/MAIN_BOARD_REVB/README.md` §5)

| ft601_signal | ft601_pad (QFN76, from EAGLE lib) | proposed_net | fpga_pad | fpga_pin_name | direction (FT601 view) | iostandard |
|---|---|---|---|---|---|---|
| CLK | 58 | FT_CLK | C4 | IO_L12N_T1_MRCC_35 | out | LVCMOS33 |
| DATA_0 | 40 | FT_DATA_0 | A2 | IO_L8N_T1_AD14N_35 | bidir | LVCMOS33 |
| DATA_1 | 41 | FT_DATA_1 | A3 | IO_L4N_T0_35 | bidir | LVCMOS33 |
| DATA_2 | 42 | FT_DATA_2 | A4 | IO_L3N_T0_DQS_AD5N_35 | bidir | LVCMOS33 |
| DATA_3 | 43 | FT_DATA_3 | A5 | IO_L3P_T0_DQS_AD5P_35 | bidir | LVCMOS33 |
| DATA_4 | 44 | FT_DATA_4 | A7 | IO_L1N_T0_AD4N_35 | bidir | LVCMOS33 |
| DATA_5 | 45 | FT_DATA_5 | B1 | IO_L9N_T1_DQS_AD7N_35 | bidir | LVCMOS33 |
| DATA_6 | 46 | FT_DATA_6 | B2 | IO_L8P_T1_AD14P_35 | bidir | LVCMOS33 |
| DATA_7 | 47 | FT_DATA_7 | B4 | IO_L4P_T0_35 | bidir | LVCMOS33 |
| DATA_8 | 50 | FT_DATA_8 | B5 | IO_L2N_T0_AD12N_35 | bidir | LVCMOS33 |
| DATA_9 | 51 | FT_DATA_9 | B6 | IO_L2P_T0_AD12P_35 | bidir | LVCMOS33 |
| DATA_10 | 52 | FT_DATA_10 | B7 | IO_L1P_T0_AD4P_35 | bidir | LVCMOS33 |
| DATA_11 | 53 | FT_DATA_11 | C1 | IO_L9P_T1_DQS_AD7P_35 | bidir | LVCMOS33 |
| DATA_12 | 54 | FT_DATA_12 | C2 | IO_L7N_T1_AD6N_35 | bidir | LVCMOS33 |
| DATA_13 | 55 | FT_DATA_13 | C3 | IO_L7P_T1_AD6P_35 | bidir | LVCMOS33 |
| DATA_14 | 56 | FT_DATA_14 | C6 | IO_L5N_T0_AD13N_35 | bidir | LVCMOS33 |
| DATA_15 | 57 | FT_DATA_15 | C7 | IO_L5P_T0_AD13P_35 | bidir | LVCMOS33 |
| DATA_16 | 60 | FT_DATA_16 | D1 | IO_L10N_T1_AD15N_35 | bidir | LVCMOS33 |
| DATA_17 | 61 | FT_DATA_17 | D3 | IO_L11N_T1_SRCC_35 | bidir | LVCMOS33 |
| DATA_18 | 62 | FT_DATA_18 | D4 | IO_L12P_T1_MRCC_35 | bidir | LVCMOS33 |
| DATA_19 | 63 | FT_DATA_19 | D6 | IO_L6P_T0_35 | bidir | LVCMOS33 |
| DATA_20 | 64 | FT_DATA_20 | E1 | IO_L15N_T2_DQS_35 | bidir | LVCMOS33 |
| DATA_21 | 65 | FT_DATA_21 | E2 | IO_L10P_T1_AD15P_35 | bidir | LVCMOS33 |
| DATA_22 | 66 | FT_DATA_22 | E3 | IO_L11P_T1_SRCC_35 | bidir | LVCMOS33 |
| DATA_23 | 67 | FT_DATA_23 | E5 | IO_L13N_T2_MRCC_35 | bidir | LVCMOS33 |
| DATA_24 | 69 | FT_DATA_24 | E6 | IO_0_35 | bidir | LVCMOS33 |
| DATA_25 | 70 | FT_DATA_25 | F2 | IO_L15P_T2_DQS_35 | bidir | LVCMOS33 |
| DATA_26 | 71 | FT_DATA_26 | F3 | IO_L14N_T2_SRCC_35 | bidir | LVCMOS33 |
| DATA_27 | 72 | FT_DATA_27 | F4 | IO_L14P_T2_SRCC_35 | bidir | LVCMOS33 |
| DATA_28 | 73 | FT_DATA_28 | F5 | IO_L13P_T2_MRCC_35 | bidir | LVCMOS33 |
| DATA_29 | 74 | FT_DATA_29 | G1 | IO_L17N_T2_35 | bidir | LVCMOS33 |
| DATA_30 | 75 | FT_DATA_30 | G2 | IO_L17P_T2_35 | bidir | LVCMOS33 |
| DATA_31 | 76 | FT_DATA_31 | G4 | IO_L16N_T2_35 | bidir | LVCMOS33 |
| BE_0 | 4 | FT_BE_0 | G5 | IO_L16P_T2_35 | bidir | LVCMOS33 |
| BE_1 | 5 | FT_BE_1 | H1 | IO_L20N_T3_35 | bidir | LVCMOS33 |
| BE_2 | 6 | FT_BE_2 | H2 | IO_L20P_T3_35 | bidir | LVCMOS33 |
| BE_3 | 7 | FT_BE_3 | H3 | IO_L21N_T3_DQS_35 | bidir | LVCMOS33 |
| TXE_N | 8 | FT_TXE_N | H4 | IO_L18N_T2_35 | out | LVCMOS33 |
| RXF_N | 9 | FT_RXF_N | H5 | IO_L18P_T2_35 | out | LVCMOS33 |
| WR_N | 11 | FT_WR_N | J1 | IO_L22N_T3_35 | in | LVCMOS33 |
| RD_N | 12 | FT_RD_N | J3 | IO_L21P_T3_DQS_35 | in | LVCMOS33 |
| OE_N | 13 | FT_OE_N | J5 | IO_L19P_T3_35 | in | LVCMOS33 |
| SIWU_N | 10 | FT_SIWU_N | K1 | IO_L22P_T3_35 | in | LVCMOS33 |
| RESET_N | 15 | FT_RESET_N | K2 | IO_L24N_T3_35 | in | LVCMOS33 |
| WAKEUP_N | 16 | FT_WAKEUP_N | K3 | IO_L24P_T3_35 | in | LVCMOS33 |
| GPIO0 | 17 | FT_GPIO0 | K5 | IO_25_35 | out | LVCMOS33 |
| GPIO1 | 18 | FT_GPIO1 | L2 | IO_L23N_T3_35 | out | LVCMOS33 |

Of these 47 balls, 36 have no free escape-via position in the rev. A fan-out and 9 have one, 2 have two (section 2.3); the pin plan therefore cannot be routed on the rev. A breakout as it stands (source: `beta/pcb/MAIN_BOARD_REVB/UNROUTED.md` §1).


---

<!-- chapter 10: Head and pedestal: layout, drawings, parts, flat patterns, thermal map, torque -->
# Mechanical design — radar head and pedestal

**Author of this chapter:** Antidrone Ukraine · antidrone.cc (compilation of the PROPOSED mechanical design; the PCB geometry it is built on is SOURCE-DERIVED from the upstream EAGLE files).

**Status summary:** every enclosure, layout, pedestal, sheet-metal, fastener, thermal and torque item in this chapter is **PROPOSED DESIGN** (decisions D-07…D-13 of `engineering/DESIGN/00_DESIGN_BASIS.md`, D-12 as revised by DSN-CALC-01 §2). Only the four PCB outlines and hole patterns are **SOURCE-DERIVED** (from the `.brd` files). PCB thickness, component heights, board masses and the mast interface are **BLOCKED — MISSING DATA / ASSUMED** (G-01, G-02, G-03, G-11). Nothing has been built, measured or hardware-verified. The thermal map and the drive-torque check are calculations (BETA, no measurement).

**Sources:** `engineering/DESIGN/00_DESIGN_BASIS.md` (DSN-00 Rev A), `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (DSN-MECH-PL Rev A), `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` (DSN-CALC-01), `engineering/MECHANICAL/dimensions/*.md` (MECH-DIM-*), `tools/design_layout.py` (station table, printed by `python3 tools/design_layout.py`), `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` (VAL-GEO-01), `engineering/DESIGN/README.md`, `engineering/DRAWING_REGISTER.md` (DSN-MECH-01…07, DSN-MECH-3D, DSN-MECH-3D-DETAIL, MECH-PLAN-01, ASM-EXP-01).

**Figures in this chapter:** F10.1–F10.5 (DSN-MECH-01…05), F10.6 (DSN-MECH-06 flat patterns), F10.7 (DSN-MECH-07 assembly section), F10.8 (isometrics of the FreeCAD models), F10.9 (thermal map, two cases), F10.10 (PCB plan view and conceptual exploded view).

## 10.1 Scope and what is verified

The upstream repository contains no enclosure, antenna, pedestal, cooling or harness design: the drawing register lists MECH-ENC-01, MECH-INT-01, MECH-ANT-01, MECH-COOL-01 and MECH-PED-01 as BLOCKED — MISSING DATA (source: `engineering/DRAWING_REGISTER.md`, rows MECH-ENC-01…MECH-PED-01; `README.md` references to `10_docs/Hardware/Enclosure` resolve to nothing). The content of this chapter therefore closes those gaps with **proposed** geometry derived from (a) the verified PCB outlines and hole tables and (b) the explicit design decisions logged in DSN-00. The repository states the rule that applies to all of it: "Everything under `engineering/DESIGN/` is *proposed* … Status vocabulary for these drawings: `PROPOSED DESIGN` (with the decisions it depends on) — never SOURCE-DERIVED or VERIFIED" (source: `engineering/DESIGN/00_DESIGN_BASIS.md`, preamble).

Verified mechanical inputs (source: `engineering/MECHANICAL/dimensions/README.md`, copied; generated by `tools/gen_mechanical_package.py` from layer 20 of each `.brd`):

| Board | Outline W × H (mm) | Holes/mounting pads | Bare-board mass ESTIMATE (g, 1.6 mm assumed) | Document |
|---|---|---|---|---|
| Main Board | 260.00 × 300.00 | 10 | ≈ 231 | `MAIN_BOARD_dimensions.md` |
| Power Supply Board | 280.00 × 300.00 | 8 | ≈ 249 | `POWER_SUPPLY_dimensions.md` |
| Frequency Synthesizer | 100.00 × 100.00 | 4 | ≈ 30 | `FREQUENCY_SYNTHESIZER_dimensions.md` |
| RF Power Amplifier | 35.00 × 60.00 | 7 | ≈ 6 | `RF_PA_dimensions.md` |

Mounting-hole coordinates (mm, origin = lower-left corner of the outline bounding box, all Ø3.20 NPTH) (source: the four `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md` §2):

| Board | Hole positions (X, Y) | Extreme pitch |
|---|---|---|
| Main Board (EAGLE 7.4.0 file, `RADAR_Main_Board.brd`) | (4, 4), (256, 4), (116, 114), (256, 114), (116, 250), (256, 250), (4, 296), (256, 296); plus two Ø0.90 package holes of X53 at (5.33, 105.36) and (5.33, 109.76) | X 252.00, Y 292.00 |
| Power Supply (EAGLE 7.4.0, `PowerBoard.brd`) | (10, 10), (140, 10), (270, 10), (10, 120), (270, 120), (10, 230), (270, 230), (138.45, 267.85) | X 260.00, Y 257.85 |
| Frequency Synthesizer (EAGLE 9.6.2, `Clocks_Freq_Synth_board.brd`) | (5, 5), (95, 5), (5, 95), (95, 95) | X 90.00, Y 90.00 |
| RF PA (EAGLE 9.6.2, `RF_PA.brd`) | (2.6, 2.6), (17.5, 2.6), (32.4, 2.6), (2.6, 38), (32.4, 38), (2.6, 57.4), (32.4, 57.4) | X 29.80, Y 54.80 |

Board thickness is **ASSUMED 1.6 mm** ("not in source; KiCad default. Must be confirmed with the stack-up"), maximum component height is **UNKNOWN** ("no 3-D models in the CAD (Autodesk URNs only)") and the Power Board hole pattern "suggests a smaller board than 280 × 300" (G-10) (source: `engineering/MECHANICAL/dimensions/*_dimensions.md` §3; `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` rows G-01, G-02, G-10).

![Figure 40 — F10.10a — Plan view of the four PCB outlines with holes, scale 1:1 on the native SVG, placement for comparison only (MECH-PLAN-01) — SOURCE-DERIVED (source: engineering/MECHANICAL/CAD/pcb_set_plan_view.png; produced by tools/gen_mechanical_package.py from the four .brd files)](engineering/MECHANICAL/CAD/pcb_set_plan_view.png)

![Figure 41 — F10.10b — Conceptual exploded view of the electronics set; board outlines are verified, the vertical arrangement, spacing, antenna panel and host are conceptual (ASM-EXP-01) — CONCEPTUAL (source: engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png; produced by tools/gen_assembly_exploded_view.py)](engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png)

## 10.2 Design decisions that define the mechanics

Copied from the decision log (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2, rows D-07…D-13; D-14/D-15 are listed because the harness and the 22 V module occupy space in the head):

| ID | Decision | Rationale | Alternatives |
|---|---|---|---|
| D-07 | Board stack pitch 25 mm (component heights assumed 15 mm top / 4 mm bottom until measured) | no 3-D models; standard 25 mm M3 standoffs | measure, then shrink |
| D-08 | Enclosure: folded 2.5 mm aluminium chassis + lid, 10 mm board-to-wall clearance, IP54 target, antenna panel in the front face behind a PTFE/ABS radome window | aluminium gives the heat path for the PA spreader; sheet metal keeps cost low | machined frame |
| D-09 | Board arrangement: Power Board on the base, Main Board above it (25 mm), Synth on the Main-Board tier beside the SMA field; PA spreader vertical behind the antenna panel at the front; stepper/slip ring below the base | shortest coax from Synth J-ports to Main J1/J18–J23; rails cables short; RF to the front | side-by-side single tier (larger footprint) |
| D-10 | Thermal design case: ambient 45 °C, TBASE(PA) ≤ 85 °C, **drain gated with the pulse train** (duty computed from the timing); continuous-bias case reported as infeasible without liquid cooling | 16 × 37 W = 591 W quiescent is not coolable in a sealed rotating head; gating requires a hardware change (D-14) | — |
| D-11 | 10 mm aluminium heat spreader common to all 16 PA boards, fan-cooled fin stack at the rear, 1.5× airflow margin | conduction from 16 hot spots into one plate, then forced air | per-PA heatsinks |
| D-12 | Azimuth drive: stepper → GT3 belt 1:3 → turntable; **revised by DSN-CALC-01 §2**: with a ≈ 10 kg head a NEMA 23 needs ≥ 200 ms per 7.2° step (revolution ≈ 19 s); a NEMA 34 (3 N·m class) allows ≈ 100 ms; firmware `Stepper_steps = 600` for 1:3 | torque calculation from the detailed mass table; belt isolates the motor from the slewing ring | ratio 1:6 (`Stepper_steps = 1200`), lighter head |
| D-13 | Slip ring 12 channels (VIN ×4 @10 A, 22 V ×4 @10 A, USB 2.0 ×4) through a 60 mm bore slewing bearing; everything else rotates with the head | only DC in and the host link cross the rotation | Ethernet/wireless host link (removes 4 channels) |
| D-14 | 22 V PA supply: synchronous boost 12–17 V → 22 V, 150 W average / bulk capacitance for 45 A pulse peaks, high-side eFuse/MOSFET switch from `EN/DIS_RFPA_VDD`, plus a per-pulse drain-gating FET per PA board (TTL from the FPGA/MCU `DIG` lines — pin to be allocated) | closes conflict K4; the firmware already sequences VG before VD | separate 22 V mains PSU on the pedestal (bigger slip ring) |
| D-15 | Harness: cable IDs from `interconnection_table.md`; coax RG-405 (0.086") hand-formable equal-length for Main↔PA and Synth↔Main; Molex 22-01-3027/3037 crimp housings for the 2-/3-pin headers; 20-way IDC ribbon for SV1 | standard parts matching the footprints in the schematics | — |

The D-09 wording ("Main Board above it (25 mm)") describes the first layout; the generators now place **all boards vertical, parallel to the antenna, in depth order** radome gap → antenna panel → PA heat-spreader plate → 16 PA boards → Main Board → Synth → Power Board → rear wall (source: `tools/design_layout.py` module docstring). The 25 mm pitch of D-07 is kept between tiers (§10.3).

Decisions still open for the owner (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §3; `engineering/DESIGN/README.md`, last paragraph): D-01 antenna variant, D-07 component heights to be measured, D-12 firmware constant / gear ratio, D-13 whether the host link stays USB, D-14 where `TX_GATE` comes from, G-10 Power Board outline, and conflicts K1–K8.

## 10.3 Radar head — layout and stations

All dimensions below are the values printed by `python3 tools/design_layout.py` (executed 2026-10-09, exit 0; the script reads `engineering/DESIGN/design_parameters.json`). Coordinate system of the head: X = width (0 at the inner left wall, looking at the antenna), Y = depth (0 = inner face of the front wall, antenna side), Z = height (0 = top of the base plate) (source: `tools/design_layout.py` docstring).

| Item | Value (mm) | Source key |
|---|---|---|
| Outer envelope W × H × D | 315.0 × 315.0 × 132.6 | `outer_mm` |
| Inner envelope W × H × D | 310.0 × 310.0 × 127.6 | `inner_mm` |
| Station Y: antenna panel | 8.0 | `stations_y.antenna` |
| Station Y: PA plate front face | 11.0 | `stations_y.plate_front` |
| Station Y: PA plate rear face | 21.0 | `stations_y.plate_rear` |
| Station Y: Main Board tier | 56.0 | `stations_y.main` |
| Station Y: Synth tier | 81.0 | `stations_y.synth` |
| Station Y: Power Board tier | 106.0 | `stations_y.power` |
| Station Y: rear inner wall | 127.6 | `stations_y.rear_inner` |
| PA heat-spreader plate W × H × t | 300.0 × 300.0 × 10 | `plate` |
| Fin fields: n / height / thickness / pitch / length / strip width | 26 / 25.0 / 2.0 / 4.0 / 280.0 / 55.0 | `fins` |
| Antenna panel W × H × t, gap to plate, radome gap, position (x, z) | 165.0 × 248.0 × 0.6, 2.4, 8.0, (72.5, 31.0) | `antenna` |
| PA field (x, z, w, h) | (77.5, 23.0, 155.0, 264.0) | `pa_field` |
| PA grid cols × rows, pitch x / z | 4 × 4, 40.0 / 68.0 | `pa_grid` |
| Main Board position (x, z) | (25.0, 5.0) | `main_pos` |
| Synth position (x, z) | (46.36, 141.60) — basis: "centred on Main Board J1,J18,J20,J21,J22,J23 (P&P)" | `synth_pos` |
| Power Board position (x, z) | (15.0, 5.0) | `power_pos` |

The tier pitch Main → Synth → Power is 25 mm (56 → 81 → 106), i.e. decision D-07; the antenna sits 2.4 mm in front of the plate on nylon spacers and 8 mm behind the radome window (source: same table). The envelope 315 × 315 × 133 mm is also the headline number of `engineering/DESIGN/README.md` ("head 315 × 315 × 133 mm (W × H × D), all boards vertical").

![Figure 42 — F10.1 — Head plan section at mid height (X–Y), DSN-MECH-01 Rev A, scale 1:1 on the native SVG — PROPOSED DESIGN, D-07…D-13 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-01_head_plan_section.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-01_head_plan_section.png)

![Figure 43 — F10.2 — Head front elevation (X–Z) with radome window and intake ducts, DSN-MECH-02 Rev A — PROPOSED DESIGN, D-07…D-13 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-02_head_front_elevation.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-02_head_front_elevation.png)

![Figure 44 — F10.3 — Head side section including the pedestal, DSN-MECH-03 Rev A — PROPOSED DESIGN, D-07…D-13 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-03_head_side_section.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-03_head_side_section.png)

![Figure 45 — F10.4 — Internal layout, each tier seen from the rear, with connector positions: tier 1 PA heat spreader with PA1…PA16 and fin fields, tier 2 Main Board (rear = component side, J1…J55, X_n, JP, SV1), Synth and Power tiers; board outlines and connector positions are from the EAGLE .brd / KiCad P&P files, enclosure, spacing and fasteners are proposed, component heights ASSUMED 15 mm — DSN-MECH-04 Rev A — PROPOSED DESIGN, D-07…D-13 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-04_internal_layout_rear.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-04_internal_layout_rear.png)

The drawing's own title block states the mixed status: "Board outlines and connector positions are VERIFIED (EAGLE .brd / KiCad P&P); enclosure, spacing, pedestal and fasteners are PROPOSED; component heights ASSUMED 15 mm" (source: `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-04_internal_layout_rear.svg`, header text). In the vocabulary of this manual the word "VERIFIED" in that title block means SOURCE-DERIVED from the native CAD files, not hardware-verified (`manual/STYLE_GUIDE.md`).

## 10.4 Pedestal and azimuth drive

Parameters printed by `python3 tools/design_layout.py`, key `pedestal` (copied):

| Item | Value |
|---|---|
| Turntable | Ø340.0 × 8.0 mm Al |
| Slewing bearing | OD 190.0 / ID 100.0 × 20.0 mm |
| Ring pulley | Ø172.0 × 12.0 mm, 180 teeth GT3 |
| Motor | "NEMA 23 (56.4 mm square, 76 mm long, 6.35 mm shaft), 200 steps/rev, ≥ 1.9 N·m" |
| Motor pulley | Ø57.3 mm, 60 teeth; belt GT3 9 mm; ratio 3 |
| Firmware change | "Stepper_steps = 600 (main.cpp:195) so that 4×3 = 12 pulses give 7.2° at the table; TB6600 at full step" |
| Slip ring | "through-bore slip ring, bore ≥ 60 mm, 12 circuits (4 × 10 A VIN, 4 × 10 A 22 V, 4 × signal USB 2.0)", OD 99.0, length 60.0 mm |
| Pedestal base W × D × H | 360.0 × 360.0 × 130.0 mm |
| Mast flange | "Ø 150 mm, 4 × M10 on PCD 110 mm (ASSUMPTION — mast interface not defined)" |

![Figure 46 — F10.5 — Pedestal plan: turntable, slewing bearing, ring pulley, NEMA 23 with motor bracket, slip ring, DSN-MECH-05 Rev A — PROPOSED DESIGN, D-12 (as revised), D-13 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-05_pedestal_plan.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-05_pedestal_plan.png)

### Drive-torque check (revises D-12)

Copied from DSN-CALC-01 §2 (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §2; inputs `MECHANICAL/CAD/detail/parts_list.json`; no measurement):

| Quantity | Value | Basis |
|---|---|---|
| Rotating mass | 10.4 kg | detailed head structure 6.4 kg + 4 kg PCBs/antenna/cables (estimate) |
| Moment of inertia (head as a box 315 × 133 mm about its centre + turntable) | 0.128 kg·m² | solid-box formula; head centred on the axis |
| Move: 7.2° in 50 ms, triangular profile | α = 201 rad/s², peak ω = 5.03 rad/s | per azimuth step (50 positions/rev; 5.65 ms dwell per elevation, 31 elevations ≈ 175 ms per azimuth, so a 50 ms move costs 22 % of the scan time) |
| Table torque | 25.69 N·m | J·α |
| Motor torque with 1:3 belt, 80 % efficiency | **10.70 N·m** at ≈ 144 rpm peak | |
| NEMA 23 (1.9 N·m holding, ≈ 60 % at that speed) | 1.14 N·m available → margin ×0.1 | assumption on the torque curve — check the chosen motor's curve at 24 V with the TB6600 |

Move time versus motor torque (same mass, triangular profile, 1:3 belt) (source: same section):

| Move time per 7.2° step | Motor torque needed | NEMA 23 (≈ 1.14 N·m) | NEMA 34 (≈ 3.0 N·m at speed) | Revolution time (50 × (175 ms dwell + move)) |
|---|---|---|---|---|
| 50 ms | 10.70 N·m | NO | NO | 11.2 s |
| 100 ms | 2.68 N·m | NO | NO | 13.8 s |
| 150 ms | 1.19 N·m | NO | OK | 16.2 s |
| 200 ms | 0.67 N·m | OK | OK | 18.8 s |
| 300 ms | 0.30 N·m | OK | OK | 23.8 s |

Verdict as recorded: "the earlier assumption 'NEMA 23, 1:3, fast steps' does not hold for a 10 kg head: NEMA 23 needs ≥ 200 ms per step (revolution ≈ 19 s), NEMA 34 (3 N·m class, 86 mm frame) allows ≈ 100 ms (revolution ≈ 14 s). Alternatives: ratio 1:6 with `Stepper_steps = 1200`, or a lighter head (lid/tray in 2 mm, no PA plate side strips). Bearing moment load from wind is not included (no enclosure wind spec)" (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §2, "Verdict"). The parts list still models a NEMA 23 (part #45) and the layout file still names a NEMA 23: the motor class is an **open owner decision (D-12)** and the assembly procedure (chapter 15, Step 15.21) carries the ⚠ marker for it.

## 10.5 Enclosure detail: sheet metal, fasteners, sealing

The detailed model (`tools/design_enclosure_detail_freecad.py`, FreeCAD 1.1) builds 51 parts; the flat patterns and the fastener section are drawn from its `parts_list.json` by `tools/design_enclosure_drawings.py` with bend allowance "90°, inside radius R = t, K = 0.4 → BA = π/2·(R + K·t)" (source: `tools/design_enclosure_drawings.py` docstring; `engineering/DRAWING_REGISTER.md` rows DSN-MECH-3D-DETAIL, DSN-MECH-06, DSN-MECH-07).

![Figure 47 — F10.6 — Sheet-metal flat patterns with bend lines for the tray, front plate and lid (2.5 mm Al 5754), DSN-MECH-06 Rev A; bend allowance per the K-factor formula stated in the generator, CAM check of bend reliefs still open — PROPOSED DESIGN, D-08 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png; produced by tools/design_enclosure_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png)

![Figure 48 — F10.7 — Assembly section with fastener balloons (balloon numbers = part # of the mechanical parts list), DSN-MECH-07 Rev A — PROPOSED DESIGN, D-07…D-13 (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png; produced by tools/design_enclosure_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png)

### Mechanical parts list (DSN-MECH-PL Rev A)

Copied verbatim (source: `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`; "from `CAD/detail/parts_list.json` … Status: PROPOSED DESIGN · masses are volume × density estimates"). Head ≈ 6.4 kg (structure only, PCBs/antenna not included except as noted), pedestal ≈ 12.4 kg (incl. stepper 1.1 kg, bearing/slip ring as modelled).

| # | Group | Part | Material | Mass (g) | Fasteners | Note |
|---|---|---|---|---|---|---|
| 1 | HEAD | Tray — base + sides + rear, 2.5 mm Al 5754, 3 bends R2.5, flanges 15 mm with M4 PEM nuts | Al | 1559 | PEM S-M4-1 ×18 | 8 lid holes M4, 10 front-plate holes M4, Ø70 cable entry, intake slots |
| 2 | HEAD | Front plate 2.5 mm Al with radome window opening and intake louvres | Al | 346 | M4×8 ×10 to tray front flanges | window 175×258, 16 M3 clamp holes |
| 3 | HEAD | Radome window PTFE 2 mm (outside the front plate) | PTFE | 246 |  | RF loss ≈ 0.1 dB at 10.5 GHz (PTFE εr 2.1, tanδ 0.0002 — to be confirmed) |
| 4 | HEAD | Window gasket EPDM 1.5 mm (ring 10 mm) | EPDM | 17 |  |  |
| 5 | HEAD | Window clamp frame 2 mm Al, 14 mm wide | Al | 69 | M3×10 ×16 + nyloc |  |
| 6 | HEAD | Lid 2.5 mm Al with exhaust slots | Al | 272 | M4×8 ×8 |  |
| 7 | HEAD | Lid gasket EPDM 3 mm self-adhesive, 15 mm wide on the flanges | EPDM | 44 |  | compressed to 2 mm → IP54 target |
| 8 | HEAD | PA heat spreader 300×300×10 Al 6061, machined fin fields, M3 tapped (16×7 PA + 6 antenna) | Al | 3400 | M3×6 ×118 (PA 112 + antenna 6) | thermal pads 5×5 under each QPA2962; antenna on 2.4 mm nylon spacers |
| 9 | HEAD | Plate bracket L 25×25×3 Al at x=5 z=20 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 10 | HEAD | Plate bracket L 25×25×3 Al at x=5 z=265.0 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 11 | HEAD | Plate bracket L 25×25×3 Al at x=280 z=20 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 12 | HEAD | Plate bracket L 25×25×3 Al at x=280 z=265.0 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 13 | HEAD | Main Board carrier rail bottom U15×12×1.5 Al, 280 mm | Al | 42 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 14 | HEAD | Main Board carrier rail top U15×12×1.5 Al, 280 mm | Al | 42 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 15 | HEAD | Main Board standoff M3×10 hex at (4,4) | steel | 2 | M3×6 ×1 |  |
| 16 | HEAD | Main Board standoff M3×10 hex at (256,4) | steel | 2 | M3×6 ×1 |  |
| 17 | HEAD | Main Board standoff M3×10 hex at (116,114) | steel | 2 | M3×6 ×1 |  |
| 18 | HEAD | Main Board standoff M3×10 hex at (256,114) | steel | 2 | M3×6 ×1 |  |
| 19 | HEAD | Main Board standoff M3×10 hex at (116,250) | steel | 2 | M3×6 ×1 |  |
| 20 | HEAD | Main Board standoff M3×10 hex at (256,250) | steel | 2 | M3×6 ×1 |  |
| 21 | HEAD | Main Board standoff M3×10 hex at (4,296) | steel | 2 | M3×6 ×1 |  |
| 22 | HEAD | Main Board standoff M3×10 hex at (256,296) | steel | 2 | M3×6 ×1 |  |
| 23 | HEAD | Synth carrier rail bottom U15×12×1.5 Al, 120 mm | Al | 18 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 24 | HEAD | Synth carrier rail top U15×12×1.5 Al, 120 mm | Al | 18 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 25 | HEAD | Synth standoff M3×10 hex at (5,5) | steel | 2 | M3×6 ×1 |  |
| 26 | HEAD | Synth standoff M3×10 hex at (95,5) | steel | 2 | M3×6 ×1 |  |
| 27 | HEAD | Synth standoff M3×10 hex at (5,95) | steel | 2 | M3×6 ×1 |  |
| 28 | HEAD | Synth standoff M3×10 hex at (95,95) | steel | 2 | M3×6 ×1 |  |
| 29 | HEAD | Power Board carrier rail bottom U15×12×1.5 Al, 300 mm | Al | 44 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 30 | HEAD | Power Board carrier rail top U15×12×1.5 Al, 300 mm | Al | 44 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 31 | HEAD | Power Board standoff M3×10 hex at (10,10) | steel | 2 | M3×6 ×1 |  |
| 32 | HEAD | Power Board standoff M3×10 hex at (140,10) | steel | 2 | M3×6 ×1 |  |
| 33 | HEAD | Power Board standoff M3×10 hex at (270,10) | steel | 2 | M3×6 ×1 |  |
| 34 | HEAD | Power Board standoff M3×10 hex at (10,120) | steel | 2 | M3×6 ×1 |  |
| 35 | HEAD | Power Board standoff M3×10 hex at (270,120) | steel | 2 | M3×6 ×1 |  |
| 36 | HEAD | Power Board standoff M3×10 hex at (10,230) | steel | 2 | M3×6 ×1 |  |
| 37 | HEAD | Power Board standoff M3×10 hex at (270,230) | steel | 2 | M3×6 ×1 |  |
| 38 | HEAD | Power Board standoff M3×10 hex at (138,268) | steel | 2 | M3×6 ×1 |  |
| 39 | HEAD | Cable-entry gland plate 100×100×2 Al under the base (M32 + M20 glands) | Al | 48 | M4×8 ×4; glands M32 + M20 IP68 | harness from the slip ring: VIN, 22 V, USB |
| 40 | PEDESTAL | Turntable plate Ø340×8 Al, 8×M6 to the head base, 12×M6 to the bearing outer ring | Al | 1864 | M6×16 ×8, M6×25 ×12 |  |
| 41 | PEDESTAL | Slewing bearing OD190/ID100×20 (4-point contact, e.g. igus PRT-04-100 class) | steel | 3218 |  | part number to be selected (axial ≥ 50 kg, moment ≥ 60 N·m) |
| 42 | PEDESTAL | Ring pulley GT3 180T Ø172 Al (machined/3D-printed), clamped under the turntable | Al | 0 | M4×10 ×6 |  |
| 43 | PEDESTAL | Pedestal top plate 360×360×5 Al, 12×M6 to the bearing inner ring, bore Ø90 | Al | 1658 | M6×20 ×12 |  |
| 44 | PEDESTAL | Pedestal housing 360×360×125 folded 2.5 mm Al (4 bends), open top, connector panel cut-out | Al | 1575 | M5×10 ×12 to the top plate | DC input (XT60/M12), USB-B bulkhead, vent |
| 45 | PEDESTAL | Stepper NEMA 23 76 mm | steel | 1898 | M5×12 ×4 |  |
| 46 | PEDESTAL | Motor bracket 80×80×3 Al with slotted belt-tension holes | Al | 41 | M5×10 ×4 to the top plate | slots ±5 mm for GT3 tension |
| 47 | PEDESTAL | Motor pulley GT3 60T Ø57, bore 6.35 | Al | 84 | grub M4 ×2 |  |
| 48 | PEDESTAL | Through-bore slip ring Ø99×60, bore 60, 12 circuits (4×10 A, 4×10 A, 4 signal) | plastic | 351 |  | e.g. Senring H3899 class — select |
| 49 | PEDESTAL | Slip-ring stator bracket 140×140×3 Al | Al | 95 | M4×8 ×4 | stator fixed to the pedestal, rotor flange to the turntable |
| 50 | PEDESTAL | Stepper driver TB6600 on DIN rail | plastic | 299 |  |  |
| 51 | PEDESTAL | Mast flange Ø150×10 steel, 4×M10 PCD 110 (ASSUMPTION — mast interface undefined) | steel | 1360 | M10×30 ×4 |  |

Fastener totals (source: same file, "Fastener totals (from the per-part lists)"):

| Fastener | Qty |
|---|---|
| M10×30 | 4 |
| M3×10 | 16 |
| M3×6 | 138 |
| M4 | 2 |
| M4×10 | 6 |
| M4×8 | 38 |
| M5×10 | 16 |
| M5×12 | 12 |
| M5×16 | 4 |
| M6×16 | 8 |
| M6×20 | 12 |
| M6×25 | 12 |
| S-M4-1 | 18 |

Note on fastener torque: the repository gives no torque table for the fasteners above; the assembly-step source quotes 0.5 N·m for the M3 PA-board screws and 0.9 N·m for the SMA couplings as check values (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, rows B3 and C3) — these values have no deeper source in the repository and are marked ASSUMED in chapter 15.

### Sealing and finish

Copied (source: `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`, "Sealing and finish"):

- Lid: EPDM 15 × 3 mm self-adhesive gasket on the three top flanges, compressed to 2 mm by the M4 screws (pitch 60 mm). Front plate: 1.5 mm EPDM strip on the two front flanges (same pattern).
- Radome window: PTFE 2 mm clamped by the 2 mm Al frame with EPDM 1.5 mm gasket, M3 × 18. Alternative: 2 mm Rogers/ABS radome if PTFE loss is acceptable but cost is not.
- Cable entry: 100 × 100 gland plate under the base with M32 (power) and M20 (USB) IP68 glands; the Ø70 base hole lets the harness reach the slip ring rotor.
- Finish: chromate conversion (Alodine) + powder coat RAL 7035 outside; bare chromate inside for grounding at the flanges; PA plate bare 6061 with thermal pads.
- Open: bend reliefs and corner welds of the tray, stiffeners of the 315 mm lid (2.5 mm may need a 20 mm hem), fan mounting brackets, antenna spacer material, earthing stud, lifting points, mast interface.

Observation MAN-10-1: the window clamp is listed as "M3×10 ×16" in part #5 and in the fastener totals, but as "M3 × 18" in the sealing text of the same document; the per-part list (16) is taken as the count for chapter 15 until the owner reconciles the text.

## 10.6 Three-dimensional models

Two FreeCAD models exist: the parametric head + pedestal (`aeris10_head_pedestal.FCStd`, DSN-MECH-3D, STEP/STL/DXF exports and a mass table) and the 51-part detail model (`aeris10_enclosure_detail.FCStd`, DSN-MECH-3D-DETAIL) (source: `engineering/DRAWING_REGISTER.md`, rows DSN-MECH-3D and DSN-MECH-3D-DETAIL). The isometric renders below are flat-shaded projections of the STL exports (`tools/stl_to_svg_iso.py`: "Intended for quick visual checks … not a CAD drawing").

![Figure 49 — F10.8a — Detail model, X-ray front isometric: tray, front plate with window, PA plate, carrier rails, boards — PROPOSED DESIGN, DSN-MECH-3D-DETAIL (source: engineering/DESIGN/MECHANICAL/CAD/detail/aeris10_detail_xray_front_iso.png; produced by tools/design_enclosure_detail_freecad.py (FreeCAD 1.1) + tools/stl_to_svg_iso.py)](engineering/DESIGN/MECHANICAL/CAD/detail/aeris10_detail_xray_front_iso.png)

![Figure 50 — F10.8b — Detail model, rear isometric: lid, rear wall, pedestal housing, motor bracket — PROPOSED DESIGN, DSN-MECH-3D-DETAIL (source: engineering/DESIGN/MECHANICAL/CAD/detail/aeris10_detail_iso_rear.png; produced by tools/design_enclosure_detail_freecad.py + tools/stl_to_svg_iso.py)](engineering/DESIGN/MECHANICAL/CAD/detail/aeris10_detail_iso_rear.png)

![Figure 51 — F10.8c — Parametric head model, X-ray isometric with board envelopes (component heights ASSUMED 15 mm top / 4 mm bottom, D-07) — PROPOSED DESIGN, DSN-MECH-3D (source: engineering/DESIGN/MECHANICAL/CAD/aeris10_head_xray_iso.png; produced by tools/design_mechanical_freecad.py (freecadcmd) + tools/stl_to_svg_iso.py)](engineering/DESIGN/MECHANICAL/CAD/aeris10_head_xray_iso.png)

Mass figures from the two models disagree by construction and both are estimates: the detail parts list gives head structure ≈ 6.4 kg and pedestal ≈ 12.4 kg; the parametric model's volume-based table gives "head ≈ 9.9 kg (includes component envelopes as solid plastic — overestimate), pedestal ≈ 12 kg + 1.1 kg stepper" (source: `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` header; `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`, "Update 2026-10-09", G-03). The torque check of §10.4 uses 10.4 kg.

## 10.7 PA heat-spreader thermal map

Model statement copied (source: `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §1): "300 × 300 × 10 mm aluminium plate (k = 200 W/mK), 60 × 60 cells, steady state, 16 heat sources 5 × 5 mm at the PA-board centres (QPA2962 position on the PA board is assumed at the board centre — verify in `engineering/PCB/RF_PA`), two fin strips as an effective convective sink (h_eff ≈ 288 W/m²K over the strip footprint = 25 W/m²K × fin area ratio × 0.9 efficiency), 5 W/m²K elsewhere; ambient 45 °C. Conduction through the PA PCB via field and the thermal pad (≈ 2 °C/W → +8 °C in case B) is added analytically."

| Case | Per PA | Plate max / min (°C) | PA base estimate (°C) | Verdict |
|---|---|---|---|---|
| A continuous drain bias | 37.0 W | 213 / — | > 287 | far beyond TBASE 85 °C — confirms case A is infeasible |
| B drain gated per chirp | 4.24 W | 64.3 / 55.3 | ≈ 73 | below 85 °C with margin 12 °C |

Limits stated by the source: "2-D (through-thickness gradient of a 10 mm plate at these fluxes < 1 °C), uniform h on the strips, no radiation, no PCB/antenna heat"; both maps "converged in 3999/3999 iterations" (source: same section). Case B is the design case of D-10 and requires the per-pulse drain gating of D-14, which is not in any CAD file today (K4).

![Figure 52 — F10.9a — PA heat-spreader temperature map, case B (drain gated per chirp, 4.24 W per PA): T min 55.3 °C … max 64.3 °C at 45 °C ambient; white rectangles = PA board outlines in the 4 × 4 field; conduction through PA board and TIM (+8 °C) not included in the map — DSN-CALC-01 — PROPOSED DESIGN (calculated), BETA (source: engineering/DESIGN/CALCS/thermal_map_B-gated-drain.svg; produced by tools/design_calcs.py, rendered to PNG by `python3 tools/svg_sheets_to_pdf.py -o manual/figures/thermal_map.pdf --png-dir manual/figures …`)](manual/figures/thermal_map_B-gated-drain.png)

![Figure 53 — F10.9b — PA heat-spreader temperature map, case A (continuous drain bias, 37.0 W per PA): plate max 213 °C, PA base > 287 °C — shown only to document why continuous bias is infeasible in the sealed head — DSN-CALC-01 — PROPOSED DESIGN (calculated), BETA (source: engineering/DESIGN/CALCS/thermal_map_A-continuous-bias.svg; produced by tools/design_calcs.py, rendered by tools/svg_sheets_to_pdf.py)](manual/figures/thermal_map_A-continuous-bias.png)

## 10.8 Unresolved geometry register (VAL-GEO-01)

Copied (source: `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`): "Every mechanical quantity that the drawings need but no repository file provides. Nothing below was estimated into a drawing; where a planning estimate exists it is labelled ESTIMATE in the source document."

| ID | Quantity | Needed by | Available evidence | Missing | Status |
|---|---|---|---|---|---|
| G-01 | PCB thickness (all 4 boards) | STEP bodies, stack-up, stand-offs | none (KiCad assumed 1.6 mm) | vendor stack-up / designer decision | BLOCKED — MISSING DATA |
| G-02 | Component heights (both sides) | enclosure clearances, stand-off heights, exploded view | packages only; 3-D URNs not embedded | 3-D models or measurement of assembled boards | BLOCKED |
| G-03 | Board masses (bare and assembled) | pedestal/motor sizing, mass table | area × assumed thickness (ESTIMATE in `MECHANICAL/dimensions/`) | weighing or CAD with densities | BLOCKED (estimate only) |
| G-04 | Enclosure: envelope, wall thickness, mounting bosses, connector cut-outs | ASM-EXP-01, M1–M6 | README text references only (`10_docs/Hardware/Enclosure` absent) | enclosure CAD | BLOCKED |
| G-05 | Relative board placement and stacking height | internal layout drawing | none | layout decision | BLOCKED (CONCEPTUAL drawing only) |
| G-06 | Antenna element geometry, substrate, feed network, radome | antenna assembly drawing | `02_hardware/04_antenna_beamforming.md` (λ/2 = 14.3 mm, aperture 214.3 mm), `8_Utils/Antenna_Array.jpg` (undimensioned photo), two contradictory waveguide simulations | antenna CAD and measurements | BLOCKED |
| G-07 | Pedestal, stepper, slip ring, bearing envelope | pedestal drawing | firmware constants only (200 steps/rev, 50 positions) | mechanical design | BLOCKED |
| G-08 | Heatsink / fan geometry and airflow | cooling drawing | PA dissipation implied by xlsx IDQ | thermal design | BLOCKED |
| G-09 | Cable lengths, routing, bend radii (SMA coax ×34, Molex ×~50) | harness drawing | connector list only | harness design | BLOCKED |
| G-10 | Power Board final outline (hole pattern suggests a smaller board than 280 × 300) | fab drawing | `POWER_SUPPLY_dimensions.md` (holes at inner positions) | designer confirmation | UNRESOLVED |
| G-11 | Fastener sizes (Ø3.2 holes → M3 inferred) | parts list | hole diameters | specification | UNRESOLVED (inferred) |
| G-12 | Keep-out zones around RF connectors and the QPA2962 | layout/enclosure | none | designer input | BLOCKED |

Update recorded in the same register: "G-04, G-05, G-07, G-08, G-09, G-12 now have PROPOSED values in `engineering/DESIGN/` (D-07…D-15); they stay open until the owner accepts the decisions and the assumed inputs (G-01 thickness, G-02 component heights, G-11 fasteners) are measured/specified. … G-06 antenna: PROPOSED patch panel 165 × 248 mm; G-10 Power Board outline unchanged" (source: `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`, "Update 2026-10-09 — proposals"). Photographs in `8_Utils/` "show a prototype but carry no scale reference … they were **not** used to derive dimensions" (same file).

## 10.9 Regenerating this chapter's artefacts

All drawings read one parameter file, so a changed decision regenerates every drawing (source: `engineering/DESIGN/00_DESIGN_BASIS.md`, preamble; `engineering/DESIGN/README.md`, "Regenerate"):

```sh
python3 tools/design_layout.py                                   # prints the station table of §10.3
python3 tools/design_mechanical_drawings.py                      # DSN-MECH-01…05 SVG/PDF/PNG + harness schedule
python3 tools/design_calcs.py                                    # DSN-CALC-01 (+ thermal_map_*.svg)
python3 tools/design_enclosure_drawings.py                       # DSN-MECH-06/07 + MECHANICAL_PARTS_LIST.md
~/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tools/design_mechanical_freecad.py').read())"
~/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tools/design_enclosure_detail_freecad.py').read())"
python3 tools/svg_sheets_to_pdf.py -o manual/figures/thermal_map.pdf --png-dir manual/figures \
    engineering/DESIGN/CALCS/thermal_map_B-gated-drain.svg engineering/DESIGN/CALCS/thermal_map_A-continuous-bias.svg
python3 tools/gen_drawing_register.py --check                    # 89 drawings, file check 0 problems (run 2026-10-09)
```

Executed for this edition: `python3 tools/design_layout.py` (exit 0, values quoted in §10.3), the `svg_sheets_to_pdf.py` render of the two thermal maps (2 pages, PNGs written to `manual/figures/`), and `python3 tools/gen_drawing_register.py --check` ("register: 89 drawings … file check: 0 problems"). The FreeCAD generators were not re-run for this edition; their existing exports were used as found.


---

<!-- chapter 11: FPGA design: module hierarchy, build, constraints, tests, synthesis status -->
# FPGA design — module hierarchy, build, constraints, tests, synthesis status

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** the original RTL (`9_Firmware/9_2_FPGA/`, ORIGINAL PROJECT FILE) does not elaborate; the BETA project `beta/fpga/` parses, lints and simulates with open-source tools (BETA: 0 build failures, 9 testbench runs PASS), is **not synthesised with Vivado**, has no timing closure, has not been loaded on hardware, and its two Xilinx FFT IP cores are not generated. An open-source Yosys/nextpnr estimate exists (`beta/fpga_synth/`, OPEN-SOURCE ESTIMATE, not a Vivado result; placement did not complete). Figures: F11.1 original hierarchy SOURCE-DERIVED; F11.1b BETA hierarchy SOURCE-DERIVED / BETA (regenerated for this manual); F11.2 original pipeline PARTIAL.

**Sources:** `beta/fpga/README.md`, `beta/fpga/CHANGELOG.md`, `beta/fpga/ip/README.md`, `beta/fpga/constraints/radar_system_top_beta.xdc`, `beta/fpga_synth/README.md`, `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md`, `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.md`, `manual/figures/fpga_beta/fpga_module_hierarchy.md` (generated), `tools/check_fpga_constraints.py` (executed).

**Planned figures:** F11.1 module hierarchy (SD-01, original), F11.1b module hierarchy of `beta/fpga/rtl`, F11.2 signal-processing pipeline (SD-02).

## 1. Starting point — the original RTL as committed

Bottom line of the reconstruction (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md`, header): "the FPGA sources cannot be elaborated by any tool today. Before a Vivado project can even reach synthesis, four user modules and two Xilinx FFT IP configurations must be recovered, three syntax/declaration defects must be fixed, and the device part number must be confirmed (schematic says XC7A50T-2FTG256I; README/XDC say XC7A100T). Pin assignment can be reconstructed for 64 of 67 top-level ports from the Main Board schematic, but 25 ports (FT601 USB 3.0, status and debug outputs) have no board counterpart because the FT601 was never wired."

Device identification (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §1, copied verbatim):

| Source | Device statement | Evidence |
|---|---|---|
| Main Board schematic | **XC7A50T-2FTG256I**, package `BGA256C100P16X16_1700X1700X155` | `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` part `U42`, library/deviceset `XC7A50T-2FTG256I` |
| Power budget workbook | `XC7A50T-2FTG256` | `3_Power Management/Power Management V6.xlsx` (sharedStrings entry 25) |
| Block diagram | `XC7A50T-2FTG256` | `2_Functional Diagram & Interconnection Matrices/RADAR_V6.drawio` |
| Constraint file | `# Device: [XC7A100T]` (placeholder brackets, no package, no speed grade) | `cntrt.xdc:4` |
| README / hardware docs | "XC7A100T FPGA" | `README.md:52`; `02_hardware/05_fpga_board.md:1,15,30,34,262` |

The source concludes that the only CAD evidence is XC7A50T-2FTG256I (Vivado part string `xc7a50tftg256-2`); whether the design fits a 50T (52 160 logic cells, 120 DSP48E1, 2 700 Kbit BRAM per AMD DS180) is UNRESOLVED until a real synthesis run (conflict K1).

![Figure 54 — F11.1 — FPGA RTL module hierarchy of the original 9_Firmware/9_2_FPGA (SD-01): 19 defined, 5 missing, 3 primitives, 9 unused — SOURCE-DERIVED, lexical scan not elaboration (source: engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.dot; produced by tools/gen_verilog_hierarchy.py and Graphviz dot)](engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.png)

Hierarchy counts of the original (source: `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.md`): 26 Verilog files parsed; DEFINED 19, MISSING 5 (`FFT_enhanced`, `xfft_32` — Xilinx IP without `.xci`; `ad9484_lvds_to_cmos_400m`, `matched_filter_processing_chain`, `range_bin_decimator` — RTL never committed), PRIMITIVE 3 (BUFG, IBUFDS, IDDR), UNUSED 9 (`ad9484_interface_400m`, `cdc_handshake`, `cdc_single_bit`, `fft_1024_forward_enhanced`, `fft_1024_inverse_enhanced`, `frequency_matched_filter`, `level_shifter_interface`, `usb_packet_analyzer`, the testbench root).

Static verification actually performed on the original (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §4, copied verbatim; tools Icarus Verilog 13.0, Verilator 5.052):

| Run | Command (abridged) | Exit | Result |
|---|---|---|---|
| A | `iverilog -g2012 -s radar_system_top` on all `.v` except testbench, including `chirp_lut_init.v` | 2 | `chirp_lut_init.v:6: syntax error` (`initial` outside a module) |
| B | same without `chirp_lut_init.v` | 2 | `radar_system_top.v:312: syntax error / Syntax in assignment statement l-value` |
| C | run B + `-I 9_Firmware/9_2_FPGA` | 2 | identical (never reaches `$readmemh`) |
| D | `iverilog -g2012 -s radar_system_tb` | 20 | 18 SVA syntax errors `radar_system_tb.v:528-543` + error B |
| lint | `verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top` | 1 | `radar_system_top.v:312:13: syntax error, unexpected wire`; 23 EOFNEWLINE |
| E–J (scratch copy only, repo untouched) | after hoisting the `wire` at :312, `wire`→`reg` at :155-156, removing `.ref_i/.ref_q`, and stubbing the missing modules | 10/11 | iverilog: "modules were missing: BUFG, IBUFDS, ad9484_lvds_to_cmos_400m, matched_filter_processing_chain, range_bin_decimator, xfft_32"; then use-before-declare errors `ddc_400m.v:252-266`, `radar_receiver_final.v:150`, `radar_system_tb.v:329`. Verilator with stubs: 0 errors, 207 warnings |
| sim | `vvp` | not run | no executable could be produced |

"No simulation or synthesis test PASSED. All results above are FAIL or informational." (source: same). Top-level ports with no board counterpart (source: `docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md` §3.2, copied verbatim):

| Ports | Bits | Reason |
|---|---|---|
| `dac_clk` | 1 | RTL forwards `clk_120m` to a pin (`dac_interface_single.v:23`); the board clocks the AD9708 from AD9523 OUT10 via SMA J20 (`main.cpp:1019-1020`); no FPGA net |
| `ft601_clk_in`, `ft601_data[31:0]`, `ft601_be[1:0]`, `ft601_txe_n`, `ft601_rxf_n`, `ft601_txe`, `ft601_rxf`, `ft601_wr_n`, `ft601_rd_n`, `ft601_oe_n`, `ft601_siwu_n`, `ft601_srb[1:0]`, `ft601_swb[1:0]`, `ft601_clk_out` | 49 | FT601Q-B-T (U6) is placed on the schematic with 0 of 77 pins connected; decoupling parts parked outside the outline; no FPGA pin carries a USB net. The RTL's USB 3.0 path has no hardware |
| `current_elevation[5:0]`, `current_azimuth[5:0]`, `current_chirp[5:0]`, `new_chirp_frame` | 19 | no status nets on the schematic |
| `dbg_doppler_data[31:0]`, `dbg_doppler_valid`, `dbg_doppler_bin[4:0]`, `dbg_range_bin[5:0]`, `system_status[3:0]` | 48 | debug outputs; no nets |

Schematic FPGA nets with no RTL port: `ADC_OR_P/N` (M6/N6, over-range), `FPGA_ADC_CLOCK_P/N` (N11/N12, 400 MHz LVDS from AD9523 OUT5 — the RTL uses the ADC DCO instead), `FPGA_CLOCK_TEST` (H14, 20 MHz test clock), `DIG_5..7` (H11/G12/H12, STM32 PD13..PD15 configured as inputs), QSPI flash `FPGA_FLASH_*` (bank 14, MT25QL01G), JTAG (source: same §3.2). The original `cntrt.xdc` has 140 `PACKAGE_PIN [PIN_NUMBER*]` placeholders, LVCMOS33 on 1.8 V bank-34 signals, LVDS_25 + DIFF_TERM on a 3.3 V bank, no `set_clock_groups`, and no `CONFIG_VOLTAGE`/`CFGBVS` (source: same §3.3). The pipeline as written is drawn in F11.2 (chapter 2 §5.1 lists the stage-by-stage findings).

![Figure 55 — F11.2 — FPGA signal-processing pipeline as written in the original RTL (SD-02) — PARTIAL; 5 instantiated-but-missing modules, placeholders and undriven controls marked (source: engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot; produced by Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.png)

## 2. The BETA project `beta/fpga/`

Status (source: `beta/fpga/README.md`, header): everything in the directory parses, elaborates, lints and simulates with open-source tools (Icarus Verilog 13.0, Verilator 5.052, Python 3 / numpy); it has **not been synthesised** (no Vivado on the authoring machine), has **no timing closure**, has **not been loaded on hardware**, and the two Xilinx FFT IP cores it needs have **not been generated**. Nothing under `9_Firmware/9_2_FPGA/` was modified; every difference is listed in `CHANGELOG.md` with original file:line references.

Directory (source: `beta/fpga/README.md`, "Directory"):

| Path | Content |
|---|---|
| `build.sh` | open-source flow (exit code = number of failures) |
| `gen_chirp_mem.py` | verifies the `.mem` formula, writes the missing seg3 files |
| `CHANGELOG.md` | every change vs. `9_Firmware/9_2_FPGA`, file:line + reason |
| `rtl/` | synthesisable Verilog-2001 (34 files; incl. host-link option B and the ISERDES capture path); `rtl/sim/unisim_sim_models.v` BUFG/IBUFDS/IDDR stand-ins (simulation + lint only); `rtl/unused_orig/` 5 untouched originals no longer compiled (+README) |
| `mem/` | 8 original `.mem` copies + generated `long_chirp_seg3_{i,q}.mem` |
| `tb/` | 8 self-checking testbenches (9 runs), `gen_vectors.py`, `vectors/`, original TB (reference) |
| `constraints/radar_system_top_beta.xdc` | constraints (section 7) |
| `vivado/create_project.tcl`, `vivado/build.tcl` | Vivado scripts — NOT executed |
| `ip/README.md` | exact FFT IP settings (xfft v9.1) derived from the port usage (section 9) |
| `logs/` | output of the last `build.sh` run (iverilog, verilator, vvp logs) |

How to run (source: `beta/fpga/README.md`, "How to run"): `cd beta/fpga && ./build.sh` (~2 min; `SKIP_SYSTEM=1` skips the long system test; `VERBOSE=1` prints sim output). `build.sh` runs, in order: iverilog elaboration (simulation view `-DSIM` and synthesis view), `verilator --lint-only -Wall` on both views, `gen_chirp_mem.py`, `tb/gen_vectors.py`, and every `tb/tb_*.v` with `vvp`. A testbench passes only if it exits 0 and prints `PASS` and never `FAIL`. The RTL's `$readmemh` paths are `mem/...` relative to `beta/fpga`.

### 2.1 Module hierarchy of the BETA RTL

![Figure 56 — F11.1b — FPGA RTL module hierarchy of beta/fpga/rtl: 43 defined, 2 missing (the deliberate FFT IP placeholders), 0 primitives (UNISIM stand-ins are defined in rtl/sim), 8 unused — SOURCE-DERIVED from the BETA sources, lexical scan not elaboration (source: beta/fpga/rtl via tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl --out manual/figures/fpga_beta; produced by dot -Tpng -Gdpi=110)](manual/figures/fpga_beta/fpga_module_hierarchy.png)

Regenerated for this manual with `python3 tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl --out manual/figures/fpga_beta` (40 Verilog files, all parsed; script exit code 1 because the two IP placeholders `FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README` and `XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README` are instantiated but undefined — the intended fail-loud behaviour) and `dot -Tpng -Gdpi=110 -o manual/figures/fpga_beta/fpga_module_hierarchy.png manual/figures/fpga_beta/fpga_module_hierarchy.dot` (source: `manual/figures/fpga_beta/fpga_module_hierarchy.md`, generated 2026-10-09: DEFINED 43, MISSING 2, PRIMITIVE 0, UNUSED 8).

## 3. Executed build and test results

Last run 2026-10-09, after command set v2 + blind calibration; logs in `beta/fpga/logs/` (source: `beta/fpga/README.md`, "What passed", copied verbatim):

| Step | Command (from `build.sh`) | Result | Log |
|---|---|---|---|
| 1 | `iverilog -g2005 -DSIM -s radar_system_top rtl/*.v rtl/sim/unisim_sim_models.v` | PASS | `logs/iverilog_top_sim.log` |
| 2 | `iverilog -g2005 -s radar_system_top ...` (synthesis view) | PASS | `logs/iverilog_top_synth.log` |
| 3a | `verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top ...` (synth view) | PASS, **0 %Error, 165 %Warning** (unchanged) | `logs/verilator_synth.log` |
| 3b | same with `-DSIM` | PASS, **0 %Error, 159 %Warning** | `logs/verilator_sim.log` |
| 4 | `python3 gen_chirp_mem.py` | PASS: seg0/1/2 reproduced within 1 LSB, seg3 written | `logs/gen_chirp_mem.log` |
| 5 | `python3 tb/gen_vectors.py` | PASS | `logs/gen_vectors.log` |
| 6a | `tb_fft_wrappers` - xfft_32 (4 frames incl. back-pressure) and FFT_enhanced (fwd + inv) vs numpy | PASS: 2176 samples within +/-2 LSB | `logs/tb_fft_wrappers.run.log` |
| 6b | `tb_matched_filter` - chain + memory, reference chirp delayed 300 samples | PASS: peak at bin 302 (300 +/-4), peak/sidelobe 4.76 | `logs/tb_matched_filter.run.log` |
| 6c | `tb_range_bin_decimator` - 2 x 1024 bins (one with input gaps) vs numpy, peak mode | PASS: 128/128 bins | `logs/tb_range_bin_decimator.run.log` |
| 6d | `tb_system_smoke` - full top, 10 chirps, synthetic IF echoes, 3.3 ms (see 6i for the two capture modes) | PASS (~65 s each): see below | `logs/tb_system_smoke_mode1.run.log` |
| 6e | `tb_host_bridge` - HOST_LINK unit test (packer + SPI slave): 3 detections, 32 detections (det_wr regression), command set v2 against a 4-word register model | PASS: 2075- and 2162-byte frames, CRC ok; v2 write/read-back/status/unknown ok | `logs/tb_host_bridge.run.log` |
| 6f | `tb_host_bridge_top` - option B bridge through the top: v2 register commands (CFAR_THR 10000 -> 150 written over SPI, 5 read-backs, 0x04 status before/with/after a frame, 0xEE), then the SPI master reads one 64x32 frame after DRDY | PASS (~77 s): 2162-byte frame, 32 detections (only possible because the threshold write took effect), sync/dims/az-el/chirp-count/map/CRC ok, ADAR pass-through gated | `logs/tb_host_bridge_top.run.log` |
| 6g | `tb_adc_iserdes_capture` - ISERDES capture + IDELAY calibration (pattern and blind) + FIFO | PASS (~30 s): pattern method 8/8 lanes locked, centre tap 13, skewed lane 5 -> 5 (8 taps = 0.6 ns compensated), bitslip detected/realigned, 4000 samples exact; blind method on a 120 MHz tone + 0.7 LSB rms noise with lane 2 parked on a metastable tap and lane 0 mis-framed: 8/8 lanes locked, every lane within **+/-0 taps** of the pattern centre, framing restored, 4000 tone samples exact | `logs/tb_adc_iserdes_capture.run.log` |
| 6h | `tb_ddc_4x` - legacy 400 MHz DDC vs polyphase DDC, same input | PASS: 1855 outputs, max diff 0 LSB | `logs/tb_ddc_4x.run.log` |
| 6i | `tb_system_smoke` runs twice: `ADC_CAPTURE_MODE=1` (default) and `=0` | both PASS | `logs/tb_system_smoke_mode1.run.log`, `_mode0` |

`build.sh` summary line: `0 failure(s), 324 verilator warning line(s) (both views)` — 165 synth view + 159 sim view; 219 for the first beta, 241 after the host link, 324 after the ISERDES capture path, unchanged 324 after command set v2 + blind calibration (the only new lint findings were two BLKSEQ on block-local temporaries in the sim-only ISERDESE2 model, marked as intended) (source: `beta/fpga/README.md`).

System smoke test evidence (source: `beta/fpga/README.md`, `logs/tb_system_smoke.run.log`): DAC left mid-scale (57540 samples); 40 range profiles (4 segments × 10 chirps); for alternating echo delays of 100 and 420 baseband samples the segment-0 peak sat at decimated bin 8 and 28 on every chirp — a shift of 20 bins for a 320-sample delay change (320/16 = 20), i.e. pulse compression works end to end through capture → DDC → matched filter → decimator; 2048 Doppler outputs (one 64 × 32 frame); 2688 USB packets with 0 header/footer/sequence errors; no X on outputs; the matched-filter FSM was idle at every toggle.

Verilator warning breakdown (synthesis view, 165; source: `beta/fpga/README.md`): 59 PINCONNECTEMPTY (monitor/unused IP outputs left unconnected on purpose), 32 UNUSEDSIGNAL (diagnostic nets of the original, unused IP tready/tlast), 22 WIDTHTRUNC / 16 WIDTHEXPAND (original arithmetic widths, the copied host-link modules, the UNISIM models), 13 PROCASSINIT + 2 BLKSEQ + 1 ZERODLY (simulation-only UNISIM models in `rtl/sim/`), 9 DECLFILENAME (original file names differ from module names — kept so the docs stay valid), 7 UNUSEDPARAM, 3 GENUNNAMED (original `generate`), 1 CMPCONST (`host_bridge_spi`). None was hidden with a global `-Wno-*`.

Additional checks (source: `beta/fpga/README.md`; `tools/check_fpga_constraints.py` re-executed for this manual on 2026-10-09 with identical output): `tools/check_fpga_constraints.py --top beta/fpga/rtl/radar_system_top.v --xdc beta/fpga/constraints/radar_system_top_beta.xdc` → 0 placeholders, 0 invalid properties, 0 unknown port refs, 67/183 port bits constrained (the 116 unconstrained bits are exactly the UNRESOLVED ports of section 7); `tools/gen_verilog_hierarchy.py --rtl beta/fpga/rtl` → 0 missing RTL modules, the only "missing" names are the two deliberate IP placeholders.

## 4. Engineering findings recorded in the BETA (source: `beta/fpga/README.md`, "What was found and decided")

1. **The reference memories are frequency-domain matched-filter coefficients.** `long_chirp_seg{0,1,2}_{i,q}.mem` = `conj(FFT_1024(u_s)) · 31128/max`, where u is a unit-amplitude 10 → 30 MHz linear up-chirp, 3000 samples at 100 MSPS (phase fit residual 0.0018 rad; regenerated to within 1 LSB by `gen_chirp_mem.py`); segment 3 lies beyond the chirp and is all zeros — the missing file. Consequence: `matched_filter_processing_chain` is the frequency-domain chain the original architecture implies, and the reference is multiplied **without** the extra conjugation (`CONJUGATE_REF = 0`) — with the original conjugating form neither the numpy model nor the RTL produces a compression peak. Open point for the designer: the same data equals the FFT of a 30 → 10 MHz down-chirp, so the actual baseband chirp direction decides whether `CONJUGATE_REF` must be 0 or 1. `short_chirp_{i,q}.mem` (50 words) matches neither a time- nor a frequency-domain chirp and cannot be used — the short-chirp path is UNRESOLVED (see also chapter 2 §2.2 and observation MAN-02).
2. **AD9484 output is SDR LVDS at the sample rate** (datasheet: "LVDS SDR output", data captured on the rising edge of the DCO, tSKEW ±0.07 ns). The legacy capture module (mode 0) uses the DCO as a 400 MHz clock (IBUFDS → BUFG) and an IDDR as a dual-edge sampler taking the falling-edge sample by default (`CAPTURE_FALLING`); this assumption must be confirmed by Vivado timing analysis and an ADC test pattern on hardware.
3. **Reference alignment by address, not by delay line.** The chain requests reference bin k when FFT output bin k appears, so the fixed 3187-cycle `latency_buffer_2159` is not needed; works with the behavioural model (latency 160) and with any IP latency.
4. **Clock-domain crossings**: `cdc_adc_to_processing` (Gray-coded data words) replaced by Gray-pointer FIFOs; a reset synchroniser per non-100 MHz domain; STM32 toggles synchronised in the clock domain that consumes them (TX: 120 MHz FSM, RX: 100 MHz).
5. **Register map** (`radar_control_regs`): the receiver's control inputs that were floating wires now have one driver with documented reset defaults; its write/read port is driven by the SPI bridge (command set v2); 5-bit word addresses 0x00..0x10, 16-bit registers; table in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §7 (kept identical to the RTL; reproduced in chapter 9 §3.3).

## 5. ADC capture and DDC front end (`ADC_CAPTURE_MODE`, default 1)

Source: `beta/fpga/README.md`, "ADC capture and DDC front end", table copied verbatim:

| | mode 0 (legacy) | mode 1 (default) |
|---|---|---|
| Capture | `ad9484_lvds_to_cmos_400m`: IBUFDS -> BUFG (400 MHz global clock) -> IDDR as dual-edge sampler | `ad9484_iserdes_capture`: IBUFDS(DCO) -> BUFIO + BUFR/4; IDELAYE2 (VAR_LOAD) -> ISERDESE2 SDR 1:4 per lane; IDELAYCTRL on 200 MHz from `clk_gen` (MMCM); 32-bit `async_fifo` into clk_100m |
| DDC | `ddc_400m_enhanced`: NCO, mixer, 5-stage CIC at 400 MHz in fabric (timing closure unrealistic), FIFO, FIR | `ddc_4x_100m`: 4-phase NCO + 8 mixers + CIC as 16-tap FIR + the same FIRs, all at 100 MHz; **bit-exact** with the legacy path (`tb_ddc_4x`: max diff 0 LSB) |
| Calibration | none (`CAPTURE_FALLING` edge choice) | `adc_capture_calib`: default tap 16; manual tap/bitslip per lane; **pattern method** (CAL_CTRL bit4 = 0): auto IDELAY sweep with the ADC in a 2-code test pattern (register 0x0D = 0x48, P1/P2 = 0x19..0x1C = pattern A/B; or 0x04 checkerboard / 0x07 toggle), centre tap per lane, lane rotation alignment, lock/undetermined/align_fail status, pattern error counter; **blind method** (CAL_CTRL bit4 = 1, no ADC SPI needed): a CW tone at the IF on the live input, notch residual r[n] = x[n] - 2cos(w)x[n-1] + x[n-2] (CAL_BLIND_COEF = Q1.14 cos(w)), metric = sum of abs(r) over 512 words per tap, one lane swept at a time MSB first, pass = metric <= min + CAL_BLIND_MARGIN + min/16, longest linear run (1-tap holes closed), eye truncated at tap 0 extrapolated with the 32-taps-per-bit period, blind framing alignment (best of 4 framings per lane) before and after each of 2 passes; CAL_BLIND_MIN read-back (register map 0x4..0x10) |

Datasheet facts used (AD9484.pdf, re-checked): LVDS SDR, DCO at the sample rate (400 MHz), data valid on the rising DCO edge, tSKEW −0.07..+0.07 ns (tPD 0.85 / tCPD 0.6 ns typ), offset binary. Resource estimate for mode 1 (XC7A50T): 8 ISERDESE2 + 8 IDELAYE2 + 1 IDELAYCTRL (bank 14), 1 BUFIO + 1 BUFR, 1 MMCME2 (of 5) + 1 BUFG, 8 DSP48E1 for the mixers (9×16) + 64 DSP48E1 for the two unchanged 32-tap FIRs (of 120), CIC adder trees in LUTs (~16 constant multiplies per I/Q), 1 BRAM18 for the 32-bit FIFO (or distributed RAM), small ROM for the 65-entry sine table. The 400 MHz fabric path (mode 0) is kept only for comparison (source: same section).

Remaining risks / what to check in Vivado for mode 1 (source: same section):

- BUFR (DCO/4) versus clk_100m (AD9523 OUT6): same nominal frequency, unknown phase; the FIFO absorbs phase/jitter, `cal_status[15]` (FIFO overflow) must stay 0 on hardware. If the two clocks are not frequency-locked the design needs a re-sampler (not present).
- IDELAYCTRL placement: all IDELAYE2 and the IDELAYCTRL must be in bank 14 (`IODELAY_GROUP` set in the XDC); the 200 MHz reference comes from the MMCM through a BUFG.
- Bank 14 is 3.3 V: LVDS_25 inputs only with `DIFF_TERM FALSE` and external 100 Ω termination (design conflict kept visible in the XDC; section 6 item 3).
- ISERDESE2 Q1..Q4 bit order: resolved from UG471 (section 6) — `Q1_IS_OLDEST = 0` in RTL, receiver and TB, and the simulation model was corrected to the same order; still confirm on hardware with the ADC PN9 pattern (0x0D = 0x06) against a PN9 generator. BUFR framing is irrelevant for the data path and absorbed by the per-lane alignment.
- Blind calibration limits (`adc_capture_calib.v` header): single CW tone at the programmed frequency with every bit toggling (≥ ~64 LSB peak for bit 7); the LSB lanes need ≤ ~1 LSB rms input noise at the default 512-word window (0.7 LSB rms in the TB; AD9484 ~47 dB SNR = ~0.5 LSB rms) — at 1.4 LSB rms lane 0 reports `undetermined` and keeps its tap; the eye-centre extrapolation for runs cut at tap 0 assumes exactly 32 taps per bit (400 MSPS, 78.125 ps/tap) and a 5-tap metastable region (`FAIL_HALF = 2`, the simulation model's 0.4 ns; the hardware value is unknown, an error of e taps moves the centre by e); the blind framing alignment takes the minimum of four metrics without a significance test (`align_fail` stays 0). Run time ~3.3 ms (2 passes × 8 lanes × 32 taps × 528 clk_div cycles + 3 alignments).
- Checks after implementation: `report_clock_interaction` (clk_div ↔ clk_100m only through the FIFO, adc_dco/clk_div/clk_200m as derived clocks), `report_timing_summary` for the clk_div and clk_200m paths, `report_cdc`, `report_io`; on hardware: run the auto calibration with the ADC test pattern, read `CAL_STAT`/`CAL_LANE_INFO` per lane (windows should be ~27 of 32 taps wide at 400 MSPS), then switch to normal data and check `CAL_ERR` stays 0 while the pattern check is off.

## 6. UG471 documentary checks

UG471 v1.10 (`build/docs_ext/ug471.txt` = pdftotext of the web-archive copy, 2026-10-09) was used to settle two open points; the simulation model and the RTL default were changed where they disagreed (CHANGELOG "Command set v2, blind calibration, UG471") (source: `beta/fpga/README.md`, "UG471 checks", quotes copied verbatim):

1. ISERDESE2 output order, section "ISERDESE2 Ports - Registered Outputs - Q1 to Q8" (p. 146): *"The first data bit received appears on the highest order Q output. The bit ordering at the input of an OSERDESE2 is the opposite of the bit ordering at the output of an ISERDESE2 block, as shown in Figure 3-3. For example, the least significant bit A of the word FEDCBA is placed at the D1 input of an OSERDESE2, but the same bit A emerges from the ISERDESE2 block at the Q8 output. In other words, D1 is the least significant input to the OSERDESE2, while Q8 is the least significant output of the ISERDESE2 block."* (OSERDESE2 section, p. 161: *"data on the D1 input pin is the first bit transmitted"*). For the 1:4 SDR configuration the first (oldest) bit is therefore on **Q4**, the newest on **Q1** → `Q1_IS_OLDEST = 0`, `word[7:0] = Q4` (s0 = oldest). The sim model had Q1 = oldest and was corrected.
2. BITSLIP in SDR mode, section "BITSLIP Submodule - Bitslip Operation" (p. 158): *"By asserting the Bitslip pin of the ISERDESE2 block, the incoming serial data stream is reordered at the parallel side. ... (Bit 8 of an input ISERDESE2 is the first bit received.) ... The Bitslip operation is synchronous to CLKDIV. In SDR mode, every Bitslip operation causes the output pattern to shift left by one. In DDR mode, every Bitslip operation causes the output pattern to alternate between a shift right by one and shift left by three."* and *"Although the repeating pattern seems to show that bitslip is a barrel shifting operation, this is not the case. A bitslip operation adds one bit to the input data stream and loses the nth bit in the input data stream."* Figure 3-11 (SDR): initial 10010011 → after one Bitslip 00100111 (Q8..Q1 notation), i.e. the word boundary moves one bit later in the serial stream. "Guidelines for Using the Bitslip Submodule" (p. 159): *"In NETWORKING mode the Bitslip submodule is available. ... the BITSLIP port must be asserted High for one CLKDIV cycle. Bitslip cannot be asserted for two consecutive CLKDIV cycles; ... the total latency ... is two CLKDIV cycles. ... The user logic should wait for at least two CLKDIV cycles in SDR mode ... before analyzing the received data pattern"* — `adc_capture_calib` pulses BITSLIP for one cycle with ≥ 1 idle cycle between pulses and waits SETTLE = 16 cycles; the sim model's slip direction was corrected to Fig. 3-11.
3. LVDS_25 inputs in a 3.3 V HR bank, section "LVDS and LVDS_25 (Low Voltage Differential Signaling)" (p. 92): *"It is acceptable to have differential inputs such as LVDS and LVDS_25 in I/O banks that are powered at voltage levels other than the nominal voltages required for the outputs of those standards (1.8V for LVDS outputs, and 2.5V for LVDS_25 outputs). However, these criteria must be met: - The optional internal differential termination is not used (DIFF_TERM = FALSE, which is the default value). - The differential signals at the input pins meet the VIN requirements in the Recommended Operating Conditions table of the specific device family data sheet. - The differential signals at the input pins meet the VIDIFF (min) requirements in the corresponding LVDS or LVDS_25 DC specifications tables of the specific device family data sheet. - For HR I/O banks in bidirectional configuration, internal differential termination is always used."*; Figure 1-72 text: *"RDIFF provides the 100 Ohm differential receiver termination because the internal DIFF_TERM is set to FALSE."*; Table 1-55 note 1a: *"The optional internal differential termination is not used (DIFF_TERM = FALSE, which is the default value) unless the VCCO voltage is at the level required for outputs."*; "Differential Termination Attribute" (p. 49): *"The VCCO of the I/O bank must be connected to 1.8V for LVDS, and 2.5V for the other differential I/O standards to provide 100 Ohm of effective differential termination. DIFF_TERM is only available for inputs and can only be used the appropriate VCCO voltage."* → the XDC keeps `LVDS_25` + `DIFF_TERM FALSE` on the nine bank-14 pairs and states that an external 100 Ω termination at the FPGA (absent on the schematic) and a VIN/VIDIFF/VICM check of the AD9484 output against DS181 are REQUIRED (board change / verification).

## 7. Constraints (`beta/fpga/constraints/radar_system_top_beta.xdc`, 348 lines)

Clocks as read by `tools/check_fpga_constraints.py` (executed 2026-10-09; source: tool output and the XDC lines quoted):

| XDC line | Clock | Period | Port | Comment in the XDC |
|---|---|---|---|---|
| 18 | `clk_100m` | 10.000 ns | `clk_100m` | AD9523 OUT6 "FPGA_SYSTEM_CLOCK" |
| 19 | `clk_120m_dac` | 8.333 ns | `clk_120m_dac` | AD9523 OUT11 "FPGA_DAC" |
| 20 | `adc_dco` | 2.500 ns | `adc_dco_p` | AD9484 DCO, 400 MHz SDR |
| 23 | `ft601_clk_in` | 10.000 ns | `ft601_clk_in` | no pin (FT601 unwired) |
| 28 | `spi_sclk` | 37.000 ns | `stm32_sclk_3v3` | 27 MHz max (STM32 SPI1, APB2 108 MHz / 4) |

Content of the file (source: `beta/fpga/README.md`, "Constraints"; XDC lines 36, 60–61, 70–71, 83, 96–98, 140–146):

- Pins: verbatim schematic-derived candidates for 64 ports / 64 bits (`PIN_MAP_FROM_SCHEMATIC.md`), every ball still to be cross-checked against the AMD FTG256 package file and the final layout.
- `set_clock_groups -asynchronous` for all clock groups (line 36); false paths for the asynchronous STM32 lines and the SPI pass-through; `set_input_delay` for the ADC bus from the datasheet skew plus an **unverified** ±0.25 ns board allowance.
- `IODELAY_GROUP adc_idelay_grp` on the IDELAYCTRL and the per-lane IDELAYE2 cells (lines 60–61).
- DAC output delays: UNRESOLVED placeholder — `dac_clk` has no FPGA pin, the AD9708 is clocked by AD9523 OUT10 (lines 70–71); STM32F7 SPI1 master timing versus SCLK at the FPGA pins UNRESOLVED (line 83).
- `CFGBVS VCCO` / `CONFIG_VOLTAGE 3.3` from the bank-0 supply (lines 96–98; CFGBVS pull direction via R to be verified).
- **Design conflict kept visible:** bank 14 is 3.3 V on the schematic; the LVDS_25 ADC inputs (9 pairs: `adc_dco_p/n`, `adc_d_p/n[7:0]`) are constrained `IOSTANDARD LVDS_25` + `DIFF_TERM FALSE` (option A — external 100 Ω termination REQUIRED, REQUIRES VERIFICATION; the UG471 criteria are quoted in the XDC header) and the `DIFF_TERM TRUE` lines are left commented as option B (bank VCCO change to 2.5 V, a board change) (lines 140–146 and following).
- Host-link option B pins H11/G12/H12 (DIG_5..7, bank 15, LVCMOS33, `PULLUP` on CS) added; `spi_sclk` is a fifth asynchronous clock group.
- UNRESOLVED (116 bits, listed at the end of the file, unconstrained): `dac_clk`, all `ft601_*` (FT601 U6 has 0/77 pins connected), `current_*`, `new_chirp_frame`, `dbg_*`, `system_status` (no board nets). `write_bitstream` will refuse the unconstrained I/O unless they are removed from the top or `UNCONSTRAINEDPINS ALLOW` is set for a resource/timing trial only.

## 8. Host path

Option B (SPI bridge on the STM32 SPI1 bus, command set v2, register map) is implemented in the BETA RTL and verified by `tb_host_bridge` and `tb_host_bridge_top`; option A (FT601) is kept unchanged as the original `usb_data_interface` packetiser running on clk_100m so the data path can be simulated — a real FT601 needs the FSM re-timed to `ft601_clk` through `async_fifo` and the D-19 changes (source: `beta/fpga/README.md`, "Host path"). Signals, frame format, command set and register map are in chapter 9 §3; the unresolved RTL items are: STM32 SPI1 timing versus the FPGA pins (XDC placeholders), BRAM inference of the SCLK-domain frame RAM read (`host_bridge_spi.v`, asynchronous read registered on falling SCLK), and the firmware rule that no ADAR1000 transaction overlaps a bridge read.

## 9. Xilinx FFT IP settings (not generated)

Status (source: `beta/fpga/ip/README.md`): IP **not generated** (no Vivado on the authoring machine). `rtl/xfft_32.v` and `rtl/FFT_enhanced.v` contain simulation-only behavioural models (`axis_fft_behav.v`) and, under `SYNTHESIS`, an instantiation of a deliberately missing module so that synthesis fails loudly until the IP exists; `vivado/create_project.tcl` imports `ip/<name>/<name>.xci` when present. Settings are derived from how the RTL drives the ports; rounding mode, latency and output order are recorded choices so that model and IP agree.

Common settings (source: `beta/fpga/ip/README.md`, copied verbatim):

| Setting (Vivado FFT v9.1 GUI) | Value | Evidence |
|---|---|---|
| Vendor / library / version | `xilinx.com:ip:xfft:9.1` | docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md FPGA-T04 |
| Number of channels | 1 | one `s_axis_data` stream |
| Architecture | Pipelined Streaming I/O | back-to-back frames assumed by `matched_filter_processing_chain.v` (queue) and continuous output in the model |
| Data format | Fixed point, **Scaled** | config word carries a scaling schedule (see below); block floating point would need `m_axis_data_tuser` BLK_EXP handling that the RTL does not have |
| Input data width | 16 | `s_axis_data_tdata[31:0] = {Q[15:0], I[15:0]}` (`fft_1024_forward.v:18`, `doppler_processor.v:289`) |
| Phase factor width | 16 | choice (model uses double precision; 16 keeps the +/-2 LSB tolerance of `tb_fft_wrappers.v` realistic - to be confirmed by running the TB against the IP's simulation model) |
| Rounding | Convergent rounding | choice; the model uses round-half-up (not bit exact, +/-1 LSB) |
| Output ordering | **Natural order** | `matched_filter_processing_chain.v` addresses the reference memory with a sequential bin counter |
| Cyclic prefix | none | not used |
| ACLKEN / ARESETn | ARESETn enabled (active low, >= 2 cycles) | `.aresetn(reset_n)` |
| XK_INDEX / OVFLO in tuser | optional (not connected) | not used by the RTL |

`xfft_32` (Doppler, `doppler_processor.v:283-296`; source: same, copied verbatim):

| Setting | Value | Evidence |
|---|---|---|
| Module name | `xfft_32` | instance name in the RTL |
| Transform length | 32 | `DOPPLER_FFT_SIZE = 32`, `fft_input_last` after 32 samples |
| Throttle scheme | **Non Real Time** (has `m_axis_data_tready`) | `.m_axis_data_tready(1'b1)` is connected |
| Config word | 8 bits: bit0 FWD_INV, bits[5:1] SCALE_SCH (2+2+1 bits for radix-4, radix-4, radix-2 stages) | `s_axis_config_tdata(8'h..)`; RTL default `FFT_CONFIG_WORD = 8'h35` = forward, shift 2+2+1 = 2^-5 |
| Transform direction | run-time configurable (forward used) | config bit0 = 1 |
| Model latency (`axis_fft_behav` LATENCY) | 72 clocks from the last input | placeholder; the real IP latency is reported by the GUI and must be below `FFT_WAIT_TIMEOUT` (1000) in `doppler_processor.v` |

`FFT_enhanced` (pulse compression, `fft_1024_forward.v:102`, `fft_1024_inverse.v:78`; source: same, copied verbatim):

| Setting | Value | Evidence |
|---|---|---|
| Module name | `FFT_enhanced` | "This must match the name in your project" (`fft_1024_forward.v:101`) |
| Transform length | 1024 | `tlast` after 1024 samples (`fft_1024_forward.v:58`), reference memory 1024 bins per segment |
| Throttle scheme | **Real Time** (no `m_axis_data_tready`) | the instantiations do not connect `m_axis_data_tready`; the wrappers tie their internal tready to 1 |
| Config word | 16 bits: bit0 FWD_INV, bits[10:1] SCALE_SCH (2 bits x 5 radix-4 stages), upper bits padding | `s_axis_config_tdata[15:0]`; forward default `SCALE_SCH = 10'h255` (shifts 1,1,1,1,2 = 2^-6), inverse `10'h155` (2^-5) |
| Transform direction | **run-time configurable** | same core used forward (`16'h...1`) and inverse (`16'h...0`) |
| Model latency | 160 clocks (beta model value, the IP is ~2-3k clocks for 1024 points) | the chain tolerates any latency (reference fetched by address, frames queued) |

The `create_ip` / `set_property -dict` Tcl for both cores is given in `beta/fpga/ip/README.md` (property names follow the xfft v9.1 `CONFIG.*` set; to be verified with `report_property`, not executed). Scaling-schedule rationale (source: same, "Scaling-schedule arithmetic"): a 1024-sample segment of the 10–30 MHz chirp occupies ~68 bins; with 2^-6 a full-scale input gives ~15.5k without saturation; the inverse transform's 2^-5 puts the compressed peak at ~32k, i.e. the full 16-bit range; the Doppler FFT uses 2^-5 (= 1/N) so that any 16-bit input cannot overflow. Verification of a generated IP against the model: run `tb_fft_wrappers` with the IP simulation model (`SYNTHESIS` not defined), expect PASS at ±2 LSB (raise `TOL` and record the measured difference if the IP rounds differently), record the IP latency and check `FFT_WAIT_TIMEOUT`.

## 10. Change classes versus the original (`beta/fpga/CHANGELOG.md`)

Legend of the changelog: **SYN** syntax/elaboration fix, **BUG** functional defect fix, **ARCH** architecture/interface change (documented in the README), **NEW** file written for the beta, **CLEAN** lint/readability only. Counting the typed rows of its tables gives 28 ARCH, 28 BUG, 12 CLEAN, 11 NEW, 9 SYN (count made for this manual with `grep` over `beta/fpga/CHANGELOG.md`; the file has 242 lines). Files copied unchanged except line endings: `dac_interface_single.v`, `fir_lowpass.v`, `level_shifter_interface.v`, `ddc_input_interface.v`; `plfm_chirp_controller.v` LUT contents unchanged. Files moved to `rtl/unused_orig/` (not compiled): `ad9484_interface_400m.v`, `lvds_to_cmos_400m.v`, `cdc_modules.v`, `latency_buffer_2159.v`, `usb_packet_analyzer.v`; `chirp_lut_init.v` and `radar_system_tb.v` were not copied into `rtl/` (the original testbench is kept as `tb/radar_system_tb_original.v`, not run). Per-file sections exist for `radar_system_top.v`, `radar_receiver_final.v` (rewritten; instance names and chain order kept), `radar_transmitter.v`, `plfm_chirp_controller.v`, `edge_detector.v`, `ddc_400m.v`, `cic_decimator_4x_enhanced.v`, `nco_400m_enhanced.v`, `chirp_memory_loader_param.v`, `matched_filter_multi_segment.v`, `frequency_matched_filter.v`, `fft_1024_forward/inverse.v`, `doppler_processor.v`, `usb_data_interface.v`, plus three follow-up sections (host-link option B integration; ISERDES capture + polyphase DDC; command set v2, blind calibration, UG471 checks) (source: `beta/fpga/CHANGELOG.md`, section headings).

New files (source: `beta/fpga/CHANGELOG.md`, "New files", copied verbatim):

| File | Content |
|---|---|
| `rtl/ad9484_lvds_to_cmos_400m.v` | AD9484 SDR LVDS capture (IBUFDS + BUFG + IDDR as dual-edge sampler, `CAPTURE_FALLING`), `ifdef SIM` behavioural model, reset synchroniser, `adc_valid`, `adc_pwdn` from `pwdn_req` |
| `rtl/matched_filter_processing_chain.v` | FFT1024 -> x conj(ref) -> IFFT1024 with address-driven reference fetch and segment queue |
| `rtl/range_bin_decimator.v` | 1024 -> 64 bins, modes first/peak/mean/sum, `start_bin` |
| `rtl/xfft_32.v`, `rtl/FFT_enhanced.v` | IP-named AXI4-Stream wrappers: behavioural model under `ifndef SYNTHESIS`, fail-loud placeholder under `SYNTHESIS` (see `ip/README.md`) |
| `rtl/axis_fft_behav.v` | behavioural AXI4-Stream FFT (simulation only) |
| `rtl/async_fifo.v`, `rtl/reset_synchronizer.v`, `rtl/radar_control_regs.v` | CDC FIFO, reset synchroniser, register map |
| `rtl/sim/unisim_sim_models.v` | BUFG / IBUFDS / IDDR models for simulation and lint (excluded from Vivado) |
| `mem/long_chirp_seg3_{i,q}.mem` | generated (all zero - segment beyond the 3000-sample chirp), `gen_chirp_mem.py` |
| `tb/tb_*.v`, `tb/gen_vectors.py`, `tb/vectors/` | self-checking testbenches and numpy references |
| `constraints/radar_system_top_beta.xdc`, `vivado/*.tcl`, `ip/README.md`, `build.sh` | constraints, Vivado scripts (not executed), IP settings, open-source flow |

The follow-ups added `rtl/host_bridge_spi.v`, `rtl/rd_map_packer.v` (with the `det_wr` width fix), `tb/tb_host_bridge.v`, `tb/tb_host_bridge_top.v`, `rtl/ad9484_iserdes_capture.v`, `rtl/adc_capture_calib.v`, `rtl/ddc_4x_100m.v`, `rtl/clk_gen.v`, `tb/tb_adc_iserdes_capture.v`, `tb/tb_ddc_4x.v`, extended `rtl/sim/unisim_sim_models.v` (BUFIO, BUFR, IDELAYE2, IDELAYCTRL, ISERDESE2, MMCME2_BASE), and one legacy bug fix in `ddc_400m.v` (NCO `phase_valid` gated by `adc_data_valid`) (source: `beta/fpga/CHANGELOG.md`, the three follow-up sections).

## 11. Synthesis without Vivado — open-source estimate (`beta/fpga_synth/`)

**Status: OPEN-SOURCE ESTIMATE. Not a Vivado result.** Every number comes from Yosys (`synth_xilinx -family xc7`) and, where stated, nextpnr-xilinx; Vivado's synthesis, retiming, DSP/BRAM inference and timing models differ; nothing here replaces `beta/fpga/vivado/build.tcl` (source: `beta/fpga_synth/README.md`, header).

What was synthesised (source: same, "What was synthesised"): git snapshot **65cd160** of `beta/fpga` (the working tree had uncommitted edits by another session — undriven `host_bridge.reg_rdata`, `calib.blind_*`, `lane_metric`, implicit `inherit_tap`/`inherit_valid` — so the committed snapshot was used; **re-run `REV=HEAD ./run_synth.sh` after those edits are committed**, which the command-set-v2 follow-up has since done in `beta/fpga` but the synthesis directory has not been re-run at the time of writing); file list = `build.sh` step 2 minus `rtl/axis_fft_behav.v` and `rtl/sim/unisim_sim_models.v`; top `radar_system_top`, default parameters (`ADC_CAPTURE_MODE = 1`); part xc7a50tftg256-2; the two FFT IP cores declared `(* blackbox *)` — 3 instances excluded from the counts. Tools: Yosys 0.69+post (Homebrew), nextpnr-xilinx bc9b234 (openXC7, archived fork), prjxray-db a90f27c, chip database `xc7a50t.bin` 93 MB, prjxray tools c9f02d8.

Utilisation (source: `beta/fpga_synth/README.md`, copied verbatim; budget XC7A50T per AMD DS180 Table 3: 8,150 slices = 32,600 LUT / 65,200 FF, 120 DSP48E1, 75 × 36 kb BRAM, 5 CMT):

| Resource | Yosys count | XC7A50T budget | Utilisation |
|---|---:|---:|---:|
| LUT total (logic + distributed RAM + SRL) | 12793 | 32,600 | 39.2 % |
|   of which logic LUT1..LUT6 | 9693 | - | - |
|   of which distributed RAM (RAM64M/RAM32M x 4 LUTs) | 3100 | - | - |
|   of which shift register (SRL16E/SRLC32E) | 0 | - | - |
| INV cells (absorbed into LUTs by P&R, not counted) | 246 | - | - |
| Flip-flops (FDRE/FDSE/FDCE/FDPE, incl. _1 falling-edge) | 4726 | 65,200 | 7.2 % |
| Latches (LDCE/LDPE) | 0 | - | - |
| DSP48E1 | 106 | 120 | 88.3 % |
| RAMB36E1 | 0 | - | - |
| RAMB18E1 | 2 | - | - |
| BRAM in 36 kb equivalents (RAMB36 + RAMB18/2) | 1 | 75 | 1.3 % |
| CARRY4 | 333 | 8,150 | 4.1 % |
| MUXF7 / MUXF8 | 0 | - | - |
| BUFG / BUFGCTRL | 4 | 32 | 12.5 % |
| BUFIO / BUFR | 2 | - | - |
| MMCME2_BASE/ADV, PLLE2 | 1 | 5 | 20.0 % |
| IBUF / IBUFG / IBUFDS | 31 | - | - |
| OBUF / OBUFT / IOBUF | 143 | - | - |
| IDELAYE2 / IDELAYCTRL | 9 | - | - |
| ISERDESE2 / IDDR | 8 | - | - |
| FFT IP black boxes (not counted above) | 3 | - | - |

Per module (source: same, hierarchical run, local cells only; `fir_lowpass_parallel_enhanced` is instantiated twice so its 32 DSP count twice; flat total 36 + 2 × 32 + 4 + 2 = 106 DSP):

| Module (hierarchical run, -noflatten) | LUT logic | LUT as RAM | FF | DSP48E1 | RAMB18E1 |
|---|---:|---:|---:|---:|---:|
| `host_bridge_spi` | 809 | 1536 | 85 | 0 | 0 |
| `plfm_chirp_controller_enhanced` | 2287 | 0 | 52 | 0 | 0 |
| `doppler_processor_optimized` | 630 | 1536 | 128 | 2 | 0 |
| `chirp_memory_loader_param` | 1847 | 0 | 33 | 0 | 0 |
| `adc_capture_calib` | 961 | 0 | 572 | 0 | 0 |
| `ddc_4x_100m` | 889 | 0 | 1118 | 36 | 0 |
| `rd_map_packer` | 610 | 0 | 726 | 0 | 0 |
| `range_bin_decimator` | 318 | 0 | 180 | 0 | 0 |
| `matched_filter_multi_segment` | 177 | 0 | 76 | 0 | 2 |
| `fir_lowpass_parallel_enhanced` | 129 | 0 | 614 | 32 | 0 |
| `frequency_matched_filter` | 126 | 0 | 292 | 4 | 0 |
| `radar_control_regs` | 84 | 0 | 61 | 0 | 0 |
| `radar_system_top` | 63 | 0 | 98 | 0 | 0 |
| `usb_data_interface` | 61 | 0 | 118 | 0 | 0 |
| `async_fifo` | 22 | 24 | 89 | 0 | 0 |
| `matched_filter_processing_chain` | 41 | 4 | 57 | 0 | 0 |
| `ad9484_iserdes_capture` | 7 | 0 | 38 | 0 | 0 |
| `ddc_input_interface` | 4 | 0 | 36 | 0 | 0 |

The four design consequences (source: `beta/fpga_synth/README.md`, "Reading the numbers"):

1. **DSP48E1 is the binding resource: 106 of 120 (88 %) without the FFT IP.** 64 are the two 32-tap fully parallel FIRs (`fir_lowpass.v`), 36 the polyphase DDC (`ddc_4x_100m.v`: 8 mixers + the CIC-as-FIR), 4 the matched-filter complex multiply, 2 the Doppler window. Only **14 DSP48E1 remain for three FFT cores** (2 × 1024-point + 1 × 32-point, Pipelined Streaming, 16-bit). The xfft v9.1 DSP count must be read from the Vivado IP GUI before anything else; if it exceeds 14 the design does not fit the XC7A50T as written (options: FIR symmetry folding / time-multiplexing at 100 MHz vs. 25 MSPS output, Radix-2 Lite / Burst I/O FFT architecture, or LUT multipliers via `use_dsp = "no"`). Not decided.
2. **Block RAM is almost unused (2 × RAMB18) because the RTL memories cannot map to BRAM**, not because the design is small: `chirp_memory_loader_param.v:32-35` (`ram_style = "block"`) muxes the read data before the output register, which has an asynchronous reset → no synchronous read port → ~1,850 LUTs of logic; `doppler_processor.v:74-75` feeds the multiplier combinationally → 1,536 LUTs as RAM64M (Yosys-specific trap: by default the frontend turned the memory into 65,611 flip-flops, more than the whole device; `run_synth.sh` reads this file with `-nomem2reg`); the `host_bridge_spi` frame RAM has an asynchronous read in the SCLK domain → 1,536 LUTs as RAM64M; only the `matched_filter_multi_segment.v:83-84` input buffers map to RAMB18 (2). Recommended RTL change (designer decision, not made): register each memory output in its own clocked block without reset, mux afterwards — moves ~4,900 LUTs into roughly 7–8 RAMB36.
3. LUTs (39 %) and FFs (7 %) leave room; the FFT IP adds BRAM/LUT/DSP on top.
4. **I/O: 183 port bits need 192 package pins** (9 LVDS pairs) — more than the 170 user I/O of the FTG256 package (DS180 Table 3 / package table — verify against UG475), even before pin conflicts. The 116 UNRESOLVED debug/FT601/status bits must be removed from the top for any board build.

Synthesis warnings that indicate real problems (source: same section): latches none, multi-driven nets none, post-synthesis `check` 0 problems; `chirp_memory_loader_param.v:112` `$time` inside a `DEBUG`-gated `$display` leaves a `$print` cell that nextpnr cannot place (wrap in `translate_off`); forced `ram_style = "block"` impossible on 6 memories (above); tri-state logic on the FT601 bus and MISO mapped to IOBUF/OBUFT (fine); **clocking: Yosys inserted a 4th BUFG on `host_bridge.sclk` = `stm32_sclk_3v3`, XDC pin J16 = `IO_L23N_T3_FWE_B_15`, not a clock-capable MRCC/SRCC pin** — Vivado will refuse a non-CC pin driving a BUFG unless the net gets `set_property CLOCK_DEDICATED_ROUTE FALSE` (not in the XDC) or SCLK is oversampled in clk_100m instead.

P&R trial, nextpnr-xilinx (source: `beta/fpga_synth/README.md`, "P&R trial", copied verbatim): **NOT COMPLETED — no placed/routed design, no Fmax, no bitstream.** Inputs: the 67 PACKAGE_PIN + IOSTANDARD assignments and `create_clock` lines of the beta XDC; netlist with the 116 unconstrained port bits demoted to internal nets, the FFT IP replaced by 1-register pass-through stubs (NOT an FFT), `$print` removed — 12,747 LUT, 4,667 FF, 106 DSP48E1, 2 RAMB18E1.

| Step | Result | Log |
|---|---|---|
| nextpnr-xilinx build (openXC7 bc9b234) | PASS after `-DUSE_OPENMP=OFF` (Apple clang: `unsupported option '-fopenmp'`) | `~/.cache/aeris10_work/nextpnr_make.log` |
| Chip database xc7a50tftg256-2 (`bbaexport.py` + `bbasm`) | PASS, 93 MB `xc7a50t.bin` | `~/.cache/aeris10_work/nextpnr-src/chipdb/*.log` |
| prjxray `xc7frames2bit` + `fasm2frames.py` (venv) | PASS (built/installed, never reached) | `~/.cache/aeris10_work/prjxray_make.log` |
| nextpnr, first try | FAIL at placement: `Unable to place cell ... $display ...: no Bels remaining of type '$print'` (DEBUG `$display` in `chirp_memory_loader_param.v:113`) -> fixed in `synth_yosys_pnr.ys` | (overwritten; reproducible) |
| Packing (all primitives) | **PASS**: IBUFDS/IBUF/OBUF, BUFGCTRL 4/32, BUFIO 1/20, BUFR 1/20, IDELAYE2 8, ISERDESE2 8, IDELAYCTRL 1/5, MMCME2_ADV 1/5 (from MMCME2_BASE), DSP48E1 106/120, RAMB18E1 2/150, CARRY4 344/8150, SLICE_LUTX 15,182/65,200 (LUT sites incl. LUTRAM), SLICE_FFX 4,667 | `logs/nextpnr_heap_seed*.log.gz` (utilisation block) |
| Placement, HeAP (default) placer, seeds 2-6 | **FAIL** (deterministic, < 5 s): `Unable to find legal placement for cell '...ddc_4x_100m.v:175$12861'` - a standalone DSP48E1 (DDC mixer) that cannot be legalised after the 10 cascade chains (8 x 8 DSP FIR adder chains `fir_lowpass.v:53`, 2 x 7 DDC chains `ddc_4x_100m.v:204`; 78 of the 106 DSPs) are fixed in the two 60-site DSP columns (x = 28, 86 in prjxray tilegrid) | `logs/nextpnr_heap_seed{2..6}.log.gz` |
| Placement, SA placer, seed 1 (unpatched) | **HUNG**: annealing converged to iteration 255 (wirelen 743,990) after ~16 min, then 20+ min at 100 % CPU without output; `sample` shows `SAPlacer::random_bel_for_cell` spinning in its unbounded `while (true)` retry loop (`common/placer1.cc:876-895`) when moving a DSP chain base with `force_z`. Killed. | `logs/nextpnr_sa_livelock.log.gz` |
| Placement, SA placer, seed 1, locally patched retry bound (`pnr/nextpnr_placer1_retry_bound.patch`) | **ABORTED by time-box** at iteration ~170 (10.5 min, still placing, same trajectory); routing never started | `logs/nextpnr_sa_patched_seed1.log.gz` |
| Routing, timing (Fmax), FASM, `fasm2frames`, `xc7frames2bit` | **NOT REACHED** - no Fmax figure exists from any run; no `.fasm`, no `.bit` | - |

Blocking items for the open-source P&R (tool side, not design errors; source: same): (1) DSP48E1 cascade chains at 88 % DSP utilisation — HeAP cannot legalise them, SA livelocks; next things to try (not done): the patched SA run to completion (~30–60 min estimate, unverified) or the maintained openXC7/nextpnr `himbaechel` xilinx flow; (2) even with a routed result the timing would be incomplete: `set_clock_groups`, `set_false_path`, `set_input_delay`, `IODELAY_GROUP`, `DIFF_TERM`, `CFGBVS`/`CONFIG_VOLTAGE` are not parsed by nextpnr-xilinx, the ADC ISERDES/IDELAY input window is not analysed, and the FFT stubs remove the FFT critical paths. Any bitstream from this flow would contain the stubs (named `..._OPENSOURCE_STUBFFT.bit` by `run_pnr.sh`) and **must never be loaded on the radar hardware**.

What must be run in Vivado to confirm (source: same, "What must be run in Vivado"): generate the FFT IP per section 9; `vivado -mode batch -source beta/fpga/vivado/create_project.tcl`; `vivado -mode batch -source beta/fpga/vivado/build.tcl -tclargs <path>/aeris10_beta.xpr 8`; inspect `report_utilization -hierarchical` (DSP48E1 total **with** the 3 FFT cores ≤ 120; BRAM use of `chirp_mem`, `doppler_proc`, `host_bridge`; RAM/ROM inference tables), `report_timing_summary` (WNS/WHS ≥ 0 for clk_100m, clk_120m_dac, adc_dco/BUFR, clk_200m, spi_sclk), `report_clock_interaction`, `report_cdc`, `report_methodology`, `report_io` / `report_drc` (non-CC pin J16 → BUFG; bank-14 LVDS_25 at 3.3 V VCCO; IODELAY_GROUP and IDELAYCTRL placement; unconstrained ports — remove the 116 UNRESOLVED bits from the top first); `write_bitstream` only after all of the above (acceptance criteria AC-F5…AC-F8, all NOT MET; source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`).

## 12. Remaining work (ordered) and known limitations

Remaining work (source: `beta/fpga/README.md`, "Remaining work (ordered)"):

1. **Generate the two FFT IP cores** per `ip/README.md`, run `tb_fft_wrappers` against the IP simulation models (adjust `TOL` if the IP's per-stage rounding differs), record the IP latency and check `FFT_WAIT_TIMEOUT` in `doppler_processor.v`.
2. **Synthesis / implementation** with `vivado/create_project.tcl` + `vivado/build.tcl` (default part `xc7a50tftg256-2` = schematic U42; README/XDC claim XC7A100T — resolve first, K1). Expect resource pressure: two 1024-point FFT IPs, 2 × 32 parallel 18×18 multipliers in the FIR (64 DSP48E1 of the 50T's 120); the open-source estimate of section 11 puts the non-FFT design at 106 of 120 DSP48E1.
3. **400 MHz fabric path replaced** (`ADC_CAPTURE_MODE = 1`): remaining are Vivado timing on the clk_div/clk_200m paths, IDELAYCTRL/IODELAY_GROUP placement, hardware calibration with the ADC test pattern, Q1..Q4 order on hardware.
4. **Matched-filter throughput.** The chain is not pipelined against the collector: one long chirp (4 segments) occupies the FSM for ~92 µs with the behavioural FFT latency (160 clocks) and ~270 µs with a realistic IP latency (~2.3k clocks per transform), while the TX repeats long chirps every 167 µs (`plfm_chirp_controller.v`: 30 µs chirp + 137 µs listen). Samples arriving while the FSM is not in `ST_COLLECT_DATA` are dropped (original behaviour). Needs ping-pong buffering or overlapping collect/process; the smoke test uses a 300 µs period for this reason.
5. **Segment semantics.** Each 1024-sample segment is compressed against its own reference segment and produces its own 64-bin profile; the four profiles per chirp are not summed, and the Doppler processor counts each profile as a "chirp" (a 32-"chirp" frame = 8 real chirps). Decide whether to sum the partial correlations (true partitioned matched filter) or to use a 4096-point transform.
6. **Hardware bring-up items** (all UNRESOLVED): confirm the chirp direction / `CONJUGATE_REF`; AD9484 capture edge and trace skew; bank-14 LVDS termination; ADC test pattern check; DAC data timing versus the externally clocked AD9708 (`dac_clk` has no pin); STM32 SPI1 clock rate versus the 1-cycle SPI pass-through re-timing; the short-chirp reference; the FT601/host decision.
7. CFAR (the detector is still a fixed threshold, default 10000 via `CFAR_THRESHOLD_DEFAULT`, now writable over the bridge as CFAR_THR); removal of the 116 unconstrained debug/status bits from the top before a board build. Register-map host interface: done (command set v2); `det_wr` back-port to `engineering/DESIGN/HOST_LINK/rtl/`: done.
8. GUI `beta/gui/aeris10_gui/protocol/register_map.py` follow-up (5-bit address mask, 0x04 bit4, 0x0D, 0x0E, 0x10) — recorded in the FPGA README; the GUI changelog's "final register map, RTL 0x0002" entry records the alignment (`ADDR_MASK = 0x1F`, registers 0x0D/0x0E/0x10) (source: `beta/gui/CHANGELOG.md`, "2026-10-09 (final register map, RTL 0x0002)"; `beta/gui/aeris10_gui/protocol/register_map.py:18`).

Known limitations of the beta (source: `beta/fpga/README.md`, "Known limitations"): not synthesised, no timing, no hardware test; FFT IP not generated (fail-loud placeholders); behavioural FFT models are not bit-exact with the Xilinx IP (total-shift scaling, round-half-up; TB tolerance ±2 LSB) and their latencies (72 / 160 clocks) are placeholders; `rtl/sim/unisim_sim_models.v` models only the behaviour the design uses (no timing, IB ignored); the USB packetiser runs on clk_100m and drops records that arrive while a packet is in flight (counted internally); the 11-word packet format is a beta definition; the level-shifter pass-through adds one clk_100m cycle to SCLK/MOSI/CS and two to MISO; `use_long_chirp` is a register bit (default 1) and the TX sequence's long/short alternation is not mirrored automatically in the receiver.

Acceptance state for the FPGA (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md` §A and §H): AC-F1…AC-F8 NOT MET on the original tree, AC-F9 (physical ADC capture with a CW tone) NOT RUN; AC-X1 (beta RTL parses/elaborates/lints with 0 errors and all testbenches pass) MET (BETA).


---

<!-- chapter 12: Firmware: architecture, build, defects fixed, sequencing, USB protocol -->
# STM32 firmware — architecture, build, defects fixed, power sequencing, USB protocol

**Author of this chapter:** Antidrone Ukraine · antidrone.cc (compilation of the BETA firmware tree and its decision records; the upstream sources under `9_Firmware/9_1_Microcontroller/` are ORIGINAL PROJECT FILE and untouched).

**Status summary:** **BETA** — "compiles and links with the ST HAL/USB stack. Not flashed. Not run on hardware. No peripheral, RF or power-sequence behaviour has been observed" (source: `beta/stm32/README.md`, header). Architecture diagrams SD-03/SD-04 are **PARTIAL** (drawn from the original sources, in which the HAL, CubeMX files and USB middleware were absent). Clock tree, I2C timing, SPI prescalers, USB descriptors and the power-sequencing delays are **engineering decisions** (D-01…D-19 of `beta/stm32/DECISIONS.md`), not measurements.

**Sources:** `beta/stm32/README.md`, `beta/stm32/DECISIONS.md`, `beta/stm32/CHANGELOG.md`, `beta/stm32/CUBEMX_SETTINGS.md`, `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`, `engineering/ELECTRICAL/power_distribution/power_rails.md` §2–§3, `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_architecture.md`, `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §5, §7, `beta/gui/aeris10_gui/protocol/settings_packet.py` and `status_text.py` (docstrings that quote the firmware line numbers).

**Figures in this chapter:** F12.1 firmware architecture (SD-03), F12.2 USB CDC flow (SD-04).

## 12.1 Target and what the firmware does

MCU: **STM32F746ZGTx (LQFP-144), part U2 on `RADAR_Main_Board.sch`** (source: `beta/stm32/CUBEMX_SETTINGS.md` §1). The application is a CubeMX-style `main.c` renamed to C++ (`main.cpp`, 2411 lines in the original) that owns every peripheral handle, all `MX_*_Init` functions, the clock tree and the whole application sequence; drivers live in `LIB/` as three families (source: `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_architecture.md` §1, copied):

| Family | Files | Transport | Evidence |
|---|---|---|---|
| C++ board classes | `ADAR1000_Manager.cpp/.h`, `USBHandler.cpp/.h`, `RadarSettings.cpp/.h`, `BMP180.cpp/.h`, `gps_handler.cpp/.h`, `TinyGPS++.cpp` | HAL directly (`hspi1`, `huart3`, `hi2c3`), CDC | `ADAR1000_Manager.cpp:8-9,619-621`; `BMP180.cpp:405-409`; `gps_handler.cpp:60,118` |
| ADI no-OS drivers + core | `ad9523.c/.h`, `adf4382.c/.h`, `adf4382a_manager.c/.h`, `adar1000.c/.h`, `no_os_*.c/.h` (60 files), `iio*.c/.h` | `no_os_spi` -> `platform_ops` -> `stm32_spi.c` -> `hspi4` | `CODE/main.cpp:1039-1040`; `adf4382a_manager.c:42-43,51-52` |
| C HAL sensor drivers | `DA5578.c`/`DAC5578.H`, `ADS7830.c/.H`, `GY_85_HAL.c/.h` | HAL I2C (`hi2c1`, `hi2c2`, `hi2c3`) | `DA5578.c:69`; `ADS7830.c:111-121`; `GY_85_HAL.c:35-116`; handles passed at `CODE/main.cpp:1563,1570,1605,1611,1670` |

Peripheral-to-device map (source: same note §1): I2C1 PB6/PB7 → 2 × DAC5578 (PA gate bias); I2C2 PF0/PF1 → 3 × ADS7830 (IDQ sense, temperatures); I2C3 PA8/PC9 → GY-85 + BMP180; SPI1 PA5/PA6/PA7 + CS PA0..PA3 → ADAR1000 ×4 through the FPGA level shift; SPI4 PE2/PE5/PE6 → AD9523 (CS PF7) and ADF4382 TX/RX (CS PG14/PG10); UART5 PC12/PD2 → GPS NMEA; USART3 PB10/PB11 → debug text; TIM1 → `delay_us()`; GPIO PD8..PD12 → FPGA handshake; USB OTG_FS → host CDC.

![Figure 57 — F12.1 — STM32 firmware architecture: main.cpp application sequence, driver families, peripheral handles; dashed red = HAL/CMSIS/startup/linker/USB middleware absent from the upstream repository (SD-03) — PARTIAL (source: engineering/SOFTWARE_DIAGRAMS/STM32/stm32_firmware_architecture.png; produced by hand-authored DOT + Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/STM32/stm32_firmware_architecture.png)

![Figure 58 — F12.2 — USB CDC flow host ↔ STM32 as found in the original sources: start flag, zero-padding defect C5, settings packet, unbound receive callback C4, status/GPS transmit (SD-04); the beta tree fixes C4/C5 (§12.4) — PARTIAL (source: engineering/SOFTWARE_DIAGRAMS/STM32/stm32_usb_cdc_flow.png; produced by hand-authored DOT + Graphviz)](engineering/SOFTWARE_DIAGRAMS/STM32/stm32_usb_cdc_flow.png)

## 12.2 BETA tree layout

(source: `beta/stm32/README.md`, "Layout", copied)

```
beta/stm32/
├── Core/Inc, Core/Src, Core/Startup   main.cpp/main.h + CubeMX glue (copied), startup_stm32f746xx.s (ST CMSIS template)
├── LIB/                               copy of 9_1_1_C_Cpp_Libraries (+ aeris_beam.*, _excluded/)
├── USB_DEVICE/App, USB_DEVICE/Target  hand-written CubeMX-equivalent USB CDC files
├── STM32F746ZGTx_FLASH.ld             ST Nucleo-F746ZG template (AXIM flash 1 MB @0x08000000, RAM 320 KB @0x20000000)
├── CMakeLists.txt, cmake/arm-none-eabi.cmake, build.sh, setup_cube.sh
├── cube/                              STM32CubeF7 sparse checkout (git-ignored; pinned commits in DECISIONS.md D-15)
├── tests/                             host-side unit tests (run_tests.sh)
├── build/ (ignored), build_out/       artefacts: aeris10_fw.elf/.hex/.bin/.map
├── logs/                              build, size, warning, include-check and test logs
└── CHANGELOG.md, DECISIONS.md, CUBEMX_SETTINGS.md, README.md
```

What was missing upstream and how the beta fills it (source: `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_architecture.md` §2; `beta/stm32/CHANGELOG.md` §3): no `stm32f7xx_hal.h`/HAL driver, no CMSIS device header, no `startup_stm32f746xx.s`, no linker script, no `.ioc`, no `usb_device.c/.h`, `usbd_cdc_if.c/.h`, `usbd_desc.c/.h`, `usbd_conf.c/.h`, no USB Device Library. The beta adds the HAL/CMSIS/USB library as a pinned sparse checkout (`cube/`), the ST startup and linker templates verbatim, and hand-written CubeMX-equivalent USB files built from the ST templates (D-07…D-10). The `.ioc` itself cannot be generated without CubeMX; `CUBEMX_SETTINGS.md` lists every setting "so an engineer can rebuild it in ~20 minutes and then diff the generated code against the hand-written files".

## 12.3 Build procedure

### Step 12.1 — Toolchain [BETA, executed on the authoring machine]

- **Purpose:** provide the cross-compiler and build tools.
- **Parts & tools:** Arm GNU Toolchain 14.2.Rel1 (`arm-none-eabi-gcc 14.2.1 20241119`); CMake ≥ 3.20 (4.4.3 used); Ninja optional; Python 3; a host C/C++ compiler for the tests (source: `beta/stm32/README.md` §1).
- **Action:** install the Arm tarball (on the authoring machine extracted to `~/opt/arm-gnu-toolchain` and symlinked into `/opt/homebrew/bin/arm-none-eabi-*`; the Homebrew cask `gcc-arm-embedded` failed because its installer needs sudo). The CMake toolchain file searches `/opt/homebrew/bin`, `~/opt/arm-gnu-toolchain/bin` and `/Applications/ArmGNUToolchain/*/arm-none-eabi/bin`, or pass `-DTOOLCHAIN_PREFIX=/path/arm-none-eabi-`.
- **Check:** `arm-none-eabi-gcc --version` prints 14.2.1 (verified on 2026-10-09 on the authoring machine: "Arm GNU Toolchain 14.2.Rel1 (Build arm-14.52) 14.2.1 20241119"). "Any 12.x–14.x arm-none-eabi GCC should work" (README §1 — unverified claim of the source).
- **Figure:** —
- **⚠ Decision:** D-13 — compiler/linker flags are **ASSUMED** CubeIDE defaults (`-mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=hard`, `-Og -g3` Debug, `-ffunction-sections -fdata-sections`, C++ `-fno-exceptions -fno-rtti -fno-use-cxa-atexit -fno-threadsafe-statics`, link `--specs=nano.specs -u _printf_float --gc-sections`, libs `c m stdc++ nosys`).

### Step 12.2 — STM32CubeF7 package [BETA]

- **Purpose:** obtain the HAL, CMSIS and USB Device Library at the pinned commits.
- **Parts & tools:** `bash beta/stm32/setup_cube.sh` (sparse clone + check with `tools/stm32_check_cube_package.sh`).
- **Action:** run the script; it clones `STMicroelectronics/STM32CubeF7` @ `79165e26…` (sparse: `Drivers/CMSIS`, `Drivers/STM32F7xx_HAL_Driver`, `Middlewares/ST/STM32_USB_Device_Library`, Nucleo-F746ZG templates and USB_Device applications) with submodules `stm32f7xx_hal_driver` @ `e860c4ff…` (HAL 1.3.3), `cmsis_device_f7` @ `2352e888…` (v1.2.10), `stm32-mw-usb-device` @ `2a0a3521…` (source: `beta/stm32/DECISIONS.md` D-15).
- **Check:** "`Package: beta/stm32/cube — missing 0 of 34 required files` (exit 0)" (source: `beta/stm32/README.md` §2).
- **Figure:** —
- **⚠ Decision:** D-15 (pinned commits).

### Step 12.3 — Compile and link [BETA, result recorded]

- **Purpose:** produce `aeris10_fw.elf/.hex/.bin/.map`.
- **Parts & tools:** `bash beta/stm32/build.sh` (Debug, `-Og -g3`) or `bash beta/stm32/build.sh Release`.
- **Action:** run the script; it configures CMake, builds, prints `arm-none-eabi-size`, writes `logs/build_full.log`, `logs/build_warnings.log`, `logs/build_errors.log`, `logs/size.log` and copies the artefacts to `build_out/`. "Exit code 0 only on a clean link."
- **Check:** result recorded on 2026-10-09 (source: `beta/stm32/README.md` §3, copied):

```
Memory region         Used Size  Region Size  %age Used
             RAM:       17480 B       320 KB      5.33%
           FLASH:       93276 B         1 MB      8.90%
   text    data     bss     dec     hex filename
  92480     788   16704  109972   1ad94 aeris10_fw.elf
```

  0 errors; 5 unique warnings, all pre-existing code (`main.cpp` unused `settings` reference, `BMP180.cpp` misleading indentation ×3, `TinyGPS++.cpp` implicit fall-through); third-party HAL/USB sources compiled with `-w`. Include audit `python3 tools/check_stm32_includes.py`: 0 case mismatches (was 6); the 11 remaining UNKNOWN headers are all in `iio*.c`/`iiod.c`, which are not built.
- **Figure:** —
- **⚠ Decision:** D-14 — sources excluded from the build: `platform_noos_stm32.c`, `adar1000.c`, `iio.c`, `iio_app.c`, `iiod.c`, `iio_trigger.c`, and every `no_os_*.c` not required by `ad9523.c`/`adf4382.c`/`no_os_spi.c`.

### Step 12.4 — Host unit tests [BETA, 6/6 PASSED on 2026-10-09]

- **Purpose:** test the protocol and driver logic on the host without hardware.
- **Parts & tools:** `bash beta/stm32/tests/run_tests.sh` (needs cc/c++ + python3 only).
- **Check:** (source: `beta/stm32/README.md` §4, copied)

| Test | What it checks |
|---|---|
| `test_settings_parser.cpp` | real `USBHandler.cpp` + `RadarSettings.cpp`: start flag `[23,46,158,237]`, 82-byte big-endian `SET…END` packet, unpadded and GUI-style 64-byte zero-padded framing, flag+settings in one packet, `SET` straddling a packet boundary, byte-at-a-time, short packets, invalid-value rejection and recovery, big-endian decode against a hand-encoded constant, `REG` text commands coexisting with the binary path (10 cases) |
| `test_beam_matrix.c` | `aeris_beam.c` (verbatim arithmetic of `initializeBeamMatrices`/`degreesTo7BitPhase`): 7-bit phase conversion, reference element, range, hand-computed samples, mirror symmetry, linearity |
| `test_ad9523_regs.c` | real `ad9523.c` + `no_os_spi.c` against a mock SPI register file: full `ad9523_setup()` path, channel distribution registers for OUT0/1/4/5/6/7/8/9/10/11 (dividers 12/9/36/180/60/30, LVDS/CMOS modes), unused outputs powered down, IO_UPDATE/SYNC/status. **This test found defect C8** |
| `test_adar_vm_tables.c` | ADAR1000 VM tables vs data sheet Tables 10-13: 128 entries, bits 7:6 clear, quadrant signs, spot rows 0/45/90/180/230.625/270/312.1875/357.1875°, strictly monotonic decoded phase (max error 3.12°), `degreesTo7BitPhase` → table round trip |
| `test_host_bridge_cmds.c` | bridge v2 byte sequences with a mock SPI (0x02 + ack 0xA2 / no ack / 0xEE / transfer error, 0x03 LE decode, 0x04 status fields), ASCII `REG W/R` parser (hex/decimal, errors) and reply formatting |
| `check_i2c_timing.py` | decodes TIMINGR: original `0x00808CD2`@36 MHz ≈ 100 kHz; beta `0x10916EA0`@54 MHz ≈ 97.6 kHz, I2C Standard-mode minima met |

  Not host-testable as-is (need HAL types): `stm32_spi_prescaler_for()`, the USB glue, power sequencing.

## 12.4 Defects fixed in the BETA tree

Defect C1 is the HSE conflict (firmware 25 MHz vs the 8 MHz crystal XTAL1 NX3225GD-8MHZ on PH0/PH1 of the schematic; "with 8 MHz HSE the PLL input would be 0.32 MHz (below the 0.95 MHz minimum of RM0385)") and is closed by decision D-01 (source: `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` §5 row C1; `beta/stm32/DECISIONS.md` D-01). C2…C10 and the further defects (source: `beta/stm32/README.md` §5, copied; file:line details in `CHANGELOG.md`):

| ID | Defect in the original | Fix |
|---|---|---|
| C1 | HSE 25 MHz (firmware) vs 8 MHz crystal (schematic) — `hal_conf.h:97`, `main.cpp:1823` | `HSE_VALUE = 8000000`; PLL M8/N432/P2/Q9 → 216 MHz (D-01, hardware-truth decision) |
| C2 | `adf4382a_manager.h` drove PG0..PG9 (PA/clock power enables) as ADF4382 CE/CS/lock-detect | macros alias `main.h` PG6..PG15; CE parameter widened to 16 bit |
| C3 | ADF4382 `platform_ops = NULL` → `no_os_spi_init` returns `-EINVAL` → `Error_Handler()` | `&stm32_spi_ops` |
| C4 | USB RX callback never bound; start-flag wait loop could never exit | `usbd_cdc_if.c:CDC_Receive_FS` → `AERIS_USB_OnReceive()` → `USBHandler` |
| C5 | GUI zero-padding after the start flag landed in the settings buffer; `"SET"` never at offset 0 | parser synchronises on `SET`, handles padded/unpadded/split frames (tested) |
| C6 | `GPS_Init()` never called → `GPS_SendBinaryToGUI()` returned early | `GPS_Init(&huart3)` |
| C7 | SPI chip selects driven low permanently and never toggled; SPI clock PCLK/2 regardless of the 10 MHz request | CS index table + toggling in `stm32_spi.c`, CS parked high, prescaler from `max_speed_hz` |
| C8 | `ad9523_init()` called after `pdata` was configured → whole AD9523 channel/PLL configuration reset to defaults | call removed |
| C9 | `ad9523_setup()` executed twice (first device leaked) | single call after reset release |
| C10 | ADAR1000 phase/gain setters used `(channel & 3)` with 1-based channels → element pattern rotated by one channel per device | `((channel - 1) & 3)` |
| — | `VM_I/VM_Q/VM_GAIN` empty → every phase write was I = Q = 0 | tables from the data sheet (D-19) |
| U10 | IDQ servo for DAC2 read ADC2 into `adc1_readings` and computed from stale data | `adc2_readings` |
| — | `printf()` → weak `__io_putchar` undefined → call to address 0 | retargeted to USART3 |
| — | `USBHandler::processStartFlag` unsigned underflow on packets < 4 bytes | guarded |
| — | `stm32_spi_write_and_read` prototype mismatch (`uint32_t` vs `uint16_t`), hard error on GCC 14 | fixed |
| — | `LIB/errno.h` `#include_next` self-inclusion → `EINVAL` undefined | shim excluded |
| — | `.H` include-case mismatches | files renamed `.h` |

The C2 defect is safety-relevant: with the original macros `ADF4382A_Manager_Init()` "would have driven the PA 5 V enables as chip-enables … and read 'lock detect' from the clock-enable outputs" (source: `beta/stm32/DECISIONS.md` D-04).

## 12.5 Hardware-truth decisions (D-01…D-19)

One-line index (source: `beta/stm32/README.md` §6, copied; full text in `beta/stm32/DECISIONS.md`): D-01 8 MHz HSE → PLL M8/N432/P2/Q9, 216 MHz, over-drive, 7 WS · D-02 APB1 54 / APB2 108 MHz, TIM1 PSC 215 · D-03 I2C TIMINGR 0x10916EA0 (computed, not CubeMX) · D-04 ADF4382 pins per schematic · D-05 CS index/idle-high · D-06 SPI 6.75 MHz (≤10 MHz) · D-07 OTG_FS device-only PA11/PA12, no VBUS sensing · D-08 USB IRQ priority 0 · D-09 VID/PID 0x0483:0x5740 PLACEHOLDER · D-10 CDC RX hook · D-11 PA sequencing: `+5V5_PA` before VG DAC programming, VG before VD, VD removed first on power-down (delays are estimates) · D-12 AD9523 single setup · D-13 compiler flags = CubeIDE defaults (assumed) · D-14 excluded sources · D-15 pinned Cube commits · D-16 `GPS_Init` · D-17 REG commands executed from the main loop · D-18 bridge v2 framing assumptions · D-19 VM tables / VM_GAIN = 0.

Clock tree as decided (source: `beta/stm32/CUBEMX_SETTINGS.md` §2, copied):

| Item | Value |
|---|---|
| HSE | Crystal/Ceramic resonator, **8 MHz** (XTAL1 NX3225GD-8MHZ on PH0/PH1) |
| LSE | crystal 32.768 kHz present on PC14/PC15 (XTAL3) — **not used** (leave disabled) |
| PLL source | HSE; **M = 8, N = 432, P = 2, Q = 9** → VCO 432 MHz |
| SYSCLK / HCLK | PLLCLK, **216 MHz**; AHB /1 |
| APB1 / APB2 | /4 → 54 MHz; /2 → 108 MHz (timer clocks: TIMPRE **activated** → TIM1CLK = 216 MHz) |
| USB (CLK48) | PLLQ = 48 MHz |
| Power | Voltage scale 1, **Over-Drive enabled**; Flash latency 7 WS |
| Original (for reference) | 25 MHz HSE, M25 N144 P2 Q3, 72 MHz, APB1 /2, APB2 /1, scale 3, 2 WS — invalid with the 8 MHz crystal |

Unverified items named by the decisions: crystal load capacitors / drive level at 8 MHz (D-01); the I2C TIMINGR is "not a CubeMX output — regenerate with CubeMX … and compare before trusting it on hardware" (D-03); ADAR1000 SCLK maximum and FPGA level-shifter bandwidth at 6.75 MHz (D-06); whether VBUS is wired to PA9 (D-07); a product VID/PID (D-09); the sequencing delays "are conservative estimates, not measured" (D-11); ADAR1000 phase accuracy (data-sheet tables realise the nominal phase within ≈ 3°, per-board calibration is a hardware task — D-19).

## 12.6 Power-enable sequencing

Enable-bus pin map (SV1 MA10-2, identical on both boards; 15 enable lines, "not 16 as stated in `docs/SYSTEM/BLOCK_DIAGRAM.md`") (source: `engineering/ELECTRICAL/power_distribution/power_rails.md` §2, copied):

| SV1 pin | Net | STM32 pin (`main.h`) | Power Board EN input |
|---|---|---|---|
| 1 | `EN_+1V0_FPGA` | PE7 | U1 |
| 2 | `EN_+5V0_PA2` | PG1 | U15 |
| 3 | `EN_+1V8_FPGA` | PE8 | U2 |
| 4 | `EN_+5V0_PA3` | PG2 | U16 |
| 5 | `EN_+3V3_FPGA` | PE9 | U4 |
| 6 | `EN_+5V5_PA` | PG3 | U17 |
| 7 | `EN_+5V0_ADAR` | PE10 | U13 |
| 8 | `EN_+1V8_CLOCK` | PG4 | U25 |
| 9 | `EN_+3V3_ADAR12` | PE11 | U6 |
| 10 | `EN_+3V3_CLOCK` | PG5 | U23 |
| 11 | `EN_+3V3_ADAR34` | PE12 | U7 |
| 13 | `EN_+3V3_ADTR` | PE13 | U32 |
| 15 | `EN_+3V3_SW` | PE14 | U10 |
| 17 | `EN_+3V3_VDD_SW` | PE15 | U8 |
| 19 | `EN_+5V0_PA1` | PG0 | U14 |
| 12, 14, 16, 18, 20 | GND | — | — |

Firmware enable sequence **as coded in the original** ("not executed on hardware") (source: `power_rails.md` §3, copied):

| Step | Action | Delay after | Source |
|---|---|---|---|
| F0 | `HAL_Delay(180000)` (3 min) then AD9523 RESET low | — | `main.cpp:1237-1238` |
| F1 | `EN_+1V8_CLOCK` high | 100 ms | `main.cpp:1241-1242` |
| F2 | `EN_+3V3_CLOCK` high; AD9523 RESET high; `configure_ad9523()` | 100 ms + 100 ms | `main.cpp:1243-1267` |
| F3 | `EN_+1V0_FPGA` high | 100 ms | `main.cpp:1271-1272` |
| F4 | `EN_+1V8_FPGA` high | 100 ms | `main.cpp:1273-1274` |
| F5 | `EN_+3V3_FPGA` high | 100 ms | `main.cpp:1275-1276` |
| F6 | DIG_3 (PD11) low "mixers off"; `EN_+3V3_ADAR12` + `EN_+3V3_ADAR34` high | 500 ms | `main.cpp:1483-1487` |
| F7 | `EN_+5V0_ADAR` high (→ −5 V ADAR rails) | 500 ms | `main.cpp:1488-1489` |
| F8 | `EN_+3V3_VDD_SW` high | 2 ms | `ADAR1000_Manager.cpp:51-52` (`powerUpSystem()`; whether `systemPowerUpSequence()` reaches it via `initializeADTR1107Sequence()` is UNVERIFIED) |
| F9 | `EN_+3V3_SW` high (→ −3V3_SW) | 2 ms | `ADAR1000_Manager.cpp:54-55` |
| F10 | DAC5578 VG codes written, LDAC pulsed, then `EN/DIS_RFPA_VDD` high (22 V drain) | — | `main.cpp:1560-1601` |
| never | `EN_+3V3_ADTR`, `EN_+5V0_PA1/2/3`, `EN_+5V5_PA` | — | no `GPIO_PIN_SET` write anywhere under `9_Firmware/9_1_Microcontroller/` |
| power-down | ADAR RX mode → `EN_+5V0_PA1..3` low → PA bias safe → `EN_+3V3_ADTR` low → LNA bias 0 → `EN_+3V3_VDD_SW`, `EN_+3V3_SW` low (10 ms steps) | 10 ms | `main.cpp:372-409` |

What the BETA changes in this sequence (D-11; source: `beta/stm32/DECISIONS.md` D-11 and `CHANGELOG.md` §2 `main.cpp` rows 380-382, 403-406, 1560-1562, 1600-1601): (a) finding — `EN_+5V5_PA` (PG3) "was **never** driven high — the OPA4703 VG buffers were unpowered while `main.cpp:1583-1601` 'programmed' VG and then enabled the 22 V drain"; (b) `EN_+3V3_ADTR` and `EN_+5V0_PA1/2/3` **are** asserted, but through raw pin numbers in `ADAR1000_Manager.cpp` (`initializeADTR1107Sequence()`, `setADTR1107Mode()`, `enable/disablePASupplies()`, `enable/disableLNASupplies()`), in the xlsx order VDD_SW → VSS_SW → CTRL → VGG → VDD_PA/VDD_LNA — kept, re-expressed with `main.h` macros; (c) power-down never removed the 22 V drain. Decisions: enable `+5V5_PA` 100 ms before the first DAC write; 20 ms VG settle before `EN/DIS_RFPA_VDD`; on power-down drop VD first (`EN_DIS_RFPA_VDD` LOW + 10 ms), then PA 5 V, LNA, switch rails, and `+5V5_PA` last. "Delays are conservative estimates, **not measured**. The IDQ servo loop (`main.cpp:1628-1656`) and the 1.68 A target were not touched. The external 22 V source and its switch are not in CAD (K4)."

The "never" row of the original therefore reads, in the beta: `+5V5_PA` is now enabled before VG programming (D-11), while `+3V3_ADTR`/`+5V0_PA_x` were already enabled by `ADAR1000_Manager` (finding b). Observation MAN-12-1: the CONFLICT rows of `power_rails.md` §1 (`+3V3_ADTR`, `+5V0_PA_1..3`, `+5V5_PA`) were written before finding (b); the register has not been updated and still states "firmware never enables the LNA supply". The bench verification in chapter 16 (Step 16.2) is the only way to settle the actual order.

## 12.7 USB protocol

### Settings packet (host → firmware)

Start flag `17 2E 9E ED` = `[23, 46, 158, 237]` (source: `USBHandler.cpp:38`, quoted in `beta/gui/README.md` "Protocol facts"), followed by the 82-byte packet `SET` + 3 × `>d` + `>I` + 6 × `>d` + `END`, all big-endian (source: `RadarSettings.cpp:23-120`; `beta/gui/aeris10_gui/protocol/settings_packet.py` lines 18-32, `PACKET_LENGTH = 82`). Field order (source: `settings_packet.py` `FIELDS`, lines 56-66; defaults from `beta/gui/aeris10_gui/model.py` `RadarSettings`):

| Offset | Size | Field | Format | Firmware limit (`RadarSettings.cpp:80-95` `validateSettings`) | Default (`model.py`) |
|---|---|---|---|---|---|
| 0 | 3 | marker | `SET` | must be at buffer offset 0 after the flag (`USBHandler.cpp:70`) | — |
| 3 | 8 | `system_frequency` | `>d` | 1e9 … 100e9 Hz | 10.0e9 |
| 11 | 8 | `chirp_duration_1` | `>d` | 1e-6 … 1000e-6 s | 30.0e-6 |
| 19 | 8 | `chirp_duration_2` | `>d` | 0.1e-6 … 10e-6 s | 0.5e-6 |
| 27 | 4 | `chirps_per_position` | `>I` | 1 … 256 | 32 |
| 31 | 8 | `freq_min` | `>d` | 1e6 … 100e6 Hz | 10.0e6 |
| 39 | 8 | `freq_max` | `>d` | > freq_min, ≤ 100e6 Hz | 30.0e6 |
| 47 | 8 | `prf1` | `>d` | 100 … 10000 Hz | 1000.0 |
| 55 | 8 | `prf2` | `>d` | 100 … 10000 Hz | 2000.0 |
| 63 | 8 | `max_distance` | `>d` | 100 … 100000 m | 50000.0 |
| 71 | 8 | `map_size` | `>d` | 1000 … 200000 m | 50000.0 |
| 79 | 3 | marker | `END` | — | — |

Framing rule (C5): the original GUI zero-padded every write to 64 bytes and the firmware copied the zeros into the settings buffer, so `SET` was never at offset 0; the beta parser "synchronises on `SET`, handles padded/unpadded/split frames" (source: `beta/stm32/README.md` §5 row C5; `CHANGELOG.md` `USBHandler.cpp` rows 59-93). There is no acknowledgement for a settings packet (source: `beta/gui/README.md`, assumption 7).

### Status and GPS (firmware → host)

Status string built by `getSystemStatusForGUI` (`main.cpp:807-877`), sent once with `CDC_Transmit_FS` at `main.cpp:1692`, no terminator (source: `beta/gui/aeris10_gui/protocol/status_text.py` docstring, copied):

```
System Status: NORMAL|LastError:%d|ErrorCount:%lu|
IMU:%.1f,%.1f,%.1f|GPS:%.6f,%.6f|ALT:%.1f|LO_TX:LOCKED|LO_RX:UNLOCKED|
T1:%.1f|...|T8:%.1f|[PA_AvgCurrent:%.2f|PA_Enabled:%d|]
BeamPos:%d|Azimuth:%d|ChirpCount:%d|
```

(`EMERGENCY_STOP` replaces `NORMAL`; the PA block appears only when `PowerAmplifier` is non-zero; `ChirpCount:%d|` is always the last field.) GPS: text `GPS:%.8f,%.8f,%.2f\r\n` on **UART3** (`gps_handler.cpp:45-62`) and the 30-byte binary `GPSB` frame over CDC — `'GPSB'` + lat (>d) + lon (>d) + alt (>f) + pitch (>f) + 16-bit sum of the first 28 bytes, big-endian (`gps_handler.cpp:65-119`). Known limitation carried into the status fields: `getSystemStatusForGUI()` "reports raw ADC codes as temperatures (no 0.64705 scale)" (source: `beta/stm32/README.md` §7 item 6).

### REG register commands (host → firmware → FPGA)

Text commands over the same CDC stream (source: `beta/stm32/DECISIONS.md` D-17, copied): `REG W <addr> <value>` / `REG R <addr>` → reply `REG 0x%04X 0x%08X\r\n` (a write echoes the written value after the ack) or `REG ERR\r\n` on syntax error, NACK, busy or SPI error. Numbers `0x` hex or decimal; keyword `REG` upper-case at byte 0 of the transfer, `W/R` either case; **one command per USB transfer**; the firmware holds **one command slot** — a second `REG` before execution is dropped, so the host waits for the reply. The line is captured in the OTG_FS ISR (`CDC_Receive_FS` → `USBHandler::captureTextCommand`) and executed from the main loop right after `HostBridge_Poll()` (`main.cpp:1713-1726` in the beta) because SPI1 is shared with the ADAR1000 path; the transport refuses (`REG ERR`) while a frame read is active or any ADAR1000 CS is low. Text detection is suppressed while a synchronised binary settings packet is being assembled (test T10).

SPI side towards the FPGA, bridge command set v2 (source: `beta/stm32/DECISIONS.md` D-18): write = 8 clocked bytes `02 a0 a1 d0 d1 d2 d3 00`, ack `0xA2` expected on MISO during the 8th byte; read = 7 bytes `03 a0 a1 00 00 00 00`, data little-endian in bytes 3..6; status = 9 bytes `04` + 8 reply bytes (status u16, version u16, frames u16, reserved u16, LE; u16 widths **assumed**); `0xEE` in the ack position = unknown command → NACK. "**The beta FPGA RTL (`beta/fpga/rtl/host_bridge_spi.v`) does not implement 0x02..0x04 yet** … STM32 side is ready, end-to-end untested."

### Bridge-frame forwarding (FPGA → firmware → host, option B)

The firmware waits for DRDY (EXTI on PD14 = DIG_6), pulls `FPGA_CS_N` (PD13 = DIG_5, reconfigured as output) low, clocks command byte `0x01` and reads one frame over SPI1 (mode 0, MSB first; the beta keeps the ADAR1000 setting of 6.75 MHz → ≈ 2.5 ms per frame), CRC-checks it and forwards it **unchanged** over CDC with `CDC_Transmit_FS`, interleaved with the status strings (source: `beta/stm32/CHANGELOG.md`, "host-link option B (DSN-LINK-01)"; `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §5). Frame layout (little-endian) (source: `HOST_LINK_DESIGN.md` §5, copied):

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | sync `0xA5 0x5A` |
| 2 | 1 | version = 1 |
| 3 | 1 | flags (bit0 = long-chirp set, bit1 = overflow since last frame) |
| 4 | 2 | sequence number |
| 6 | 1 | azimuth index (1..50) |
| 7 | 1 | elevation index (1..31) |
| 8 | 2 | chirp count |
| 10 | 1 | n_range = 64 |
| 11 | 1 | n_doppler = 32 |
| 12 | 2 | n_det (≤ 32) |
| 14 | 2 | reserved |
| 16 | 2048 | magnitude map, uint8 = 8·log2(|I|+|Q|) saturated, range-major |
| 2064 | 3·n_det | detections: range u8, doppler u8, mag u8 |
| end | 2 | CRC-16/CCITT-FALSE over bytes 0..end-1 |

Firmware rule: "the firmware must not start an ADAR1000 transaction while `HostBridge_Busy()`" (source: `beta/stm32/CHANGELOG.md`, option B entry). Build after this change: 0 errors, RAM 17 480 B (5.33 %), FLASH 93 276 B (8.90 %).

## 12.8 USB descriptors and CDC configuration

(source: `beta/stm32/CUBEMX_SETTINGS.md` §4–§5): USB_OTG_FS **Device_Only**, PA11 DM / PA12 DP (AF10, very high speed), VBUS sensing off, SOF off, low-power off, LPM off, PA10 (ID) unassigned (D-07); CDC (VCP) with `USBD_MAX_NUM_INTERFACES 1`, `USBD_SELF_POWERED 1`; descriptors VID 0x0483, PID 0x5740, LANGID 0x409 — **PLACEHOLDER (D-09)**, chosen "only because `GUI_V5.py:323-330` enumerates on that list"; serial number = STM32 96-bit UID; FIFO Rx 0x80 / Tx EP0 0x40 / Tx EP1 0x80 words; `APP_RX_DATA_SIZE 2048`, `APP_TX_DATA_SIZE 2048`; OTG_FS interrupt priority 0/0 (D-08); user code to re-insert after a CubeMX regeneration: `AERIS_USB_OnReceive(Buf, *Len);` in `usbd_cdc_if.c` `CDC_Receive_FS()` USER CODE 6 (D-10).

## 12.9 Flashing and what remains

Flash command recorded for the bring-up (source: `beta/stm32/README.md` §7 item 2): `STM32_Programmer_CLI -c port=SWD -w beta/stm32/build_out/aeris10_fw.elf -v -rst` (SWD on PA13/PA14; SWO PB3 on the schematic — `CUBEMX_SETTINGS.md` §3). The bring-up checks themselves are Steps 16.1–16.2 and 16.8.

Unresolved / remaining work (source: `beta/stm32/README.md` §7, condensed, numbering kept): (1) regenerate the CubeMX project from `CUBEMX_SETTINGS.md` and diff the generated `usbd_conf.c`, `usbd_desc.c`, `usbd_cdc_if.c`, `usb_device.c`, startup and linker script against the hand-written files; let CubeMX recompute the I2C TIMINGR (D-03) and confirm the clock tree (D-01/D-02); (2) hardware bring-up per chapter 16; (3) ADAR1000 phase accuracy on hardware; FPGA implementation of bridge commands 0x02..0x04 and an end-to-end `REG` test; (4) ADAR1000 SCLK limit and FPGA level-shifter bandwidth; AD9523/ADF4382 register-level correctness; ADF4382 `DELADJ` "PWM" is a stub (`adf4382a_manager.c:433-460`); (5) VBUS wiring to PA9 (D-07); production VID/PID (D-09); USB interrupt priority policy (D-08); (6) `main.cpp` logic not touched: 180 s OCXO wait at boot; `last_check` reused for the temperature timer (`main.cpp:1774`); raw ADC codes reported as temperatures; health-check thresholds; IDQ servo exit conditions; (7) I/D cache stays disabled, MPU background region as generated; (8) PA drain 22 V source/switch and stepper supply are not in CAD (K4); (9) static analysis (cppcheck) and `-fstack-usage` review not yet done.

Acceptance criteria touched by this chapter (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`): AC-S1…AC-S5 are recorded NOT MET against the **original** tree; AC-X2 ("beta firmware compiles and links; host tests pass") is **MET (BETA)**; AC-S6/AC-S7 (physical) are NOT RUN.


---

<!-- chapter 13: GUI: install, run, protocol, register panel, packaging -->
# Host GUI software — install, run, protocol, register panel, packaging

**Author of this chapter:** Antidrone Ukraine · antidrone.cc (compilation of the BETA package `beta/gui`; the upstream scripts `9_Firmware/9_3_GUI/GUI_V1…V6*.py` are ORIGINAL PROJECT FILE and untouched).

**Status summary:** **BETA** — "This package has **never been run against hardware**" (source: `beta/gui/README.md`, "BETA statement"). Module and runtime diagrams SD-05/SD-06 are SOURCE-DERIVED from the original scripts. The test suite, the headless self-test and the PyInstaller bundle were executed on the authoring workstation (CPython 3.14, Tk 9.x, macOS arm64); Windows/Linux and older interpreters are unverified. The demo figure F13.3 is a render of the plot canvas only (see its caption).

**Sources:** `beta/gui/README.md`, `beta/gui/CHANGELOG.md`, `docs/GUI/INSTALLATION.md`, `docs/GUI/DEPENDENCIES.md`, `engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.md`, `beta/gui/aeris10_gui/protocol/register_map.py`, `beta/fpga/rtl/radar_control_regs.v`, `beta/gui/pyproject.toml`.

**Figures in this chapter:** F13.1 module graph (SD-05), F13.2 runtime architecture (SD-06), F13.3 demo-mode plot render.

## 13.1 Which program is the application

The upstream directory holds nine GUI versions; only one is runnable offline and only one is hardware-capable (source: `docs/GUI/DEPENDENCIES.md` §1, copied):

| File | Lines | State | Runnable? |
|---|---:|---|---|
| `GUI_V1.py` | 41 | fragment of one method with a leading indent — `IndentationError` line 2 | no |
| `GUI_V2.py` | 1 059 | complete (STM32 CDC, FTDI, DBSCAN, Kalman, matplotlib) | parses, imports OK; hardware needed |
| `GUI_V3.py` | 1 146 | complete; pitch in GPS packet | parses; hardware |
| `GUI_V4.py` | 1 427 | complete; Google Maps HTML with placeholder API key (`:229`) | parses; hardware; network |
| `GUI_V4_2_CSV.py` | 678 | offline CSV replay; two defects (`:354-368` derives columns before `read_csv`; `:430` lambda captures unbound `e`) | parses; offline |
| `GUI_V5.py` | 1 542 | **last complete hardware GUI**; V5 buffer-advance bug `:1313` vs `:809-816` (packet length always 6) | parses; hardware |
| `GUI_V5_Demo.py` | 1 356 | truncated (`:696`, `:1339` "Rest of the methods remain the same"); `RadarGUI` calls 9 undefined methods → `AttributeError` at `:955` | **no** |
| `GUI_V6.py` | 617 | partial rewrite for FT601: `RadarProcessor`, `USBPacketParser`, `RadarPacketParser`, `MapGenerator` are `pass` stubs (`:90-92`, `:365-375`); `create_gui`/`configure_dark_theme` `pass` (`:419-425`); `STM32USBInterface` undefined (`:392`); `get_packet_length` returns constant 64 (`:597-600`) | **no** |
| `GUI_V6_Demo.py` | 1 221 | self-contained simulator (`SimulatedRadarProcessor` `:61-231`), only numpy + matplotlib + tkinter | **yes (offline)** — module import verified; window not launched |

No GUI version could decode the RTL's actual packet (`A5C3`+CRC16 expected vs the RTL's `0xAA … 0x55` without CRC — `docs/GUI/DEPENDENCIES.md` §6 row 5), and both FTDI paths (FT2232H in V2–V5, FT601 in V6) have no hardware on the Main Board (same §4). The BETA package `beta/gui/aeris10_gui` therefore re-implements the host from the firmware and RTL sources; the provenance of every beta module is tabulated in `beta/gui/README.md` ("Mapping: original file -> beta module") and `CHANGELOG.md` ("Provenance").

![Figure 59 — F13.1 — Python GUI modules: imports and definitions of the nine upstream scripts, classified stdlib / third-party / local (SD-05; auto-generated) — SOURCE-DERIVED (source: engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.png; produced by tools/gen_python_module_graph.py + Graphviz dot)](engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.png)

![Figure 60 — F13.2 — Python GUI runtime architecture as found in GUI_V5.py / GUI_V6_Demo.py: threads, queues, parsers, processor, Tk timer; clustering/tracking defined but never called in V5 (SD-06) — SOURCE-DERIVED (source: engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_architecture.png; produced by hand-authored DOT + Graphviz)](engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_architecture.png)

## 13.2 BETA package: what it implements

(source: `beta/gui/README.md`, "BETA statement", condensed)

- **FPGA → host data:** default path is the **SPI bridge (option B, DSN-LINK-01)**: the FPGA serves 64 × 32 log-magnitude frames over SPI, the STM32 forwards them unchanged over USB CDC interleaved with status strings and `REG` replies (frame layout in chapter 12 §12.7). Simulated and unit-tested only. The raw 35-byte RTL packet path (option A, FT601) remains behind `--raw-ft601`; "on the board the FT601 is not wired".
- **FPGA register access:** `REG W/R` over CDC and the "FPGA registers / ADC calibration" tab follow `beta/fpga/rtl/radar_control_regs.v`; the text protocol "is **the same as the firmware's**" (`beta/stm32/Core/Src/host_bridge_proto.c`): one command per USB transfer, replies `REG 0x%04X 0x%08X\r\n` / `REG ERR\r\n`, a write echoes the written value, single firmware command slot → the GUI sends one command at a time and waits (timeout + retransmit). "Not bench-tested; the top-level RTL still ties the register write port off."
- **STM32 CDC path** (settings upload, status/GPS reception): implemented from the firmware sources, "unverified on a board".
- **Range/velocity scaling** of the display rests on assumptions (§13.7).

Protocol facts the beta relies on (source: `beta/gui/README.md`, "Protocol facts", copied):

| Item | Source | Beta |
|---|---|---|
| Start flag `17 2E 9E ED` | `USBHandler.cpp:38` | `settings_packet.START_FLAG` |
| 82-byte `SET`+3x`>d`+`>I`+6x`>d`+`END`, big-endian | `RadarSettings.cpp:23-120` | `build_settings_packet`, frozen vector in tests |
| `SET` must be at buffer offset 0 after the flag | `USBHandler.cpp:70` | no zero padding by default (`pad_to_64=False`) |
| Firmware value limits | `RadarSettings.cpp:86-101` | `validate_settings` (UI refuses values the firmware would reject) |
| FPGA packet = 11 FT601 words, `0xAA`, 4 range words, 4 Doppler words, detection, `0x55` | `usb_data_interface.v:39-160` | `fpga_packet.encode_words/decode_packet` |
| `range_profile` = `{Q, I}` Doppler word; `doppler_real` = bits 15:0 | `radar_system_top.v:294-331`, `doppler_processor.v:244` | `encode_cell`, `check_top_level_consistency` |
| Emission order range-major, 64 x 32 cells | `doppler_processor.v:244-266`, `radar_receiver_final.v:291-293` | `processing.FrameAssembler` |
| Detection bit = `|I|+|Q| > 10000` | `radar_system_top.v:318` | simulator |
| Status string fields, `ChirpCount` last | `main.cpp:807-877` | `status_text.parse_status_line` |
| `GPS:%.8f,%.8f,%.2f\r\n` (UART3) and 30-byte `GPSB` (CDC) | `gps_handler.cpp:45-119` | `parse_gps_text`, `parse_gpsb` |

Package modules (source: `beta/gui/README.md` mapping table; `CHANGELOG.md` "Added"): `model.py` (dataclasses, firmware defaults), `protocol/settings_packet.py`, `protocol/status_text.py`, `protocol/fpga_packet.py`, `protocol/bridge_frame.py`, `protocol/register_cmd.py`, `protocol/register_map.py`, `io/usb_cdc.py` (pyserial CDC-ACM primary, pyusb fallback on the CDC *data* interface), `io/ftdi_ft601.py` (stub raising `NotImplementedError`), `dsp/cfar.py` (new CA-CFAR), `dsp/clustering.py` (DBSCAN, now actually called), `dsp/tracking.py` (filterpy Kalman), `sim/simulator.py`, `sim/replay.py`, `sim/register_file.py` (in-memory model of `radar_control_regs.v`), `processing.py`, `ui/main_window.py`, `ui/theme.py`, `ui/sources.py` (`LinkDecoder`, default link `bridge`), `ui/register_panel.py`, `app.py`/`__main__.py`.

## 13.3 Installation

### Step 13.1 — Create the environment and install [BETA, executed]

- **Purpose:** reproducible interpreter with the pinned dependencies.
- **Parts & tools:** Python ≥ 3.10 with Tk (`python3 -c "import tkinter"` must work); tested with CPython 3.14.7 + Tk 9.0 on macOS arm64 (source: `beta/gui/README.md`, "Install"); `beta/gui/requirements.txt` ("pinned to the tested versions"), `pyproject.toml` (extras `dev` = pytest ≥ 7, `packaging` = pyinstaller ≥ 6.0).
- **Action:**

```sh
cd beta/gui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt       # pinned to the tested versions
# or, for development:  .venv/bin/pip install -e .[dev,packaging]
```

  `pyusb` (optional raw-USB fallback) needs the libusb-1.0 system library (`brew install libusb` / `apt install libusb-1.0-0`); nothing else needs system packages.
- **Check:** `.venv/bin/python -m aeris10_gui --version` prints `aeris10-gui 0.7.0b1` (version string from `app.py` `--version`; package version in `CHANGELOG.md` "0.7.0b1").
- **Figure:** —
- **⚠ Decision:** Tk 9.1 upgrade note — "Homebrew had upgraded `tcl-tk` to 9.1, which broke `_tkinter` … Fixed with `brew reinstall python-tk@3.14`" (source: `beta/gui/CHANGELOG.md`, "Environment note").

Dependency ranges (source: `docs/GUI/DEPENDENCIES.md` §2, for the upstream scripts; the beta pins the tested versions in `requirements.txt`): numpy 2.5.3 (`>=1.24,<3`, UNVERIFIED below 2.5.3), scipy 1.18.1, matplotlib 3.11.2 (TkAgg), scikit-learn 1.9.1, filterpy 1.4.5 ("last release 2018 … runs on numpy 2.5.3 here; long-term maintenance risk" — `beta/gui/README.md` assumption 10), crcmod 1.7, pyusb 1.3.1, pyserial (added by the beta as the primary CDC transport), pyinstaller 6.22.3. `pyftdi` "does not support FT601" (`docs/GUI/DEPENDENCIES.md` §2) and is not used by the beta.

## 13.4 Running

### Step 13.2 — Run in demo, self-test or hardware mode [BETA]

- **Purpose:** start the application against the simulator (no hardware) or against the STM32 CDC port.
- **Parts & tools:** the venv of Step 13.1; for hardware mode the STM32 CDC port (after chapter 16 Step 16.1).
- **Action:** (source: `beta/gui/README.md`, "Run", copied)

```sh
.venv/bin/python -m aeris10_gui --demo            # simulator, no hardware
.venv/bin/python -m aeris10_gui                   # hardware mode: pick the STM32 CDC port, press Start
.venv/bin/python -m aeris10_gui --selftest        # hidden window, 3 simulated frames, exit 0 on success
.venv/bin/python -m aeris10_gui --port /dev/cu.usbmodemXXXX
.venv/bin/python -m aeris10_gui --demo --raw-ft601   # option A: raw RTL packets instead of bridge frames
```

  Other options (source: `beta/gui/aeris10_gui/app.py` argparse): `--frames N` (frames for `--selftest`, default 3), `--update-ms` (UI poll interval, default 100), `--log-level`. After `pip install -e .` the same is available as `aeris10-gui [--demo]`. In demo mode the simulator emits per frame one **bridge frame** (`build_frame`, packed exactly like `rd_map_packer.v`) plus a status string in the firmware format, in one CDC byte stream, and "also answers `REG` commands from an in-memory model of `radar_control_regs.v`, so the register panel works without hardware".
- **Check:** `--selftest` exit 0. Executed for this edition on 2026-10-09 (`cd beta/gui && .venv/bin/python -m aeris10_gui --selftest`), output: `selftest: link=bridge frames=31 link_stats={'status': {'status': 31, 'gps_text': 0, 'gpsb': 0, 'reg': 31, 'errors': 0, 'dropped_bytes': 0}, 'bridge': {'frames': 31, 'crc_errors': 0, 'resyncs': 0}} reg_read_all=OK (sent=31, dropped_by_slot=0) -> OK` (the self-test keeps stepping until the register read-all of 31 single-slot commands is answered, hence 31 frames).
- **Figure:** F13.3.
- **⚠ Decision:** hardware mode depends on the firmware CDC path (chapter 12, C4/C5 fixed in the beta, never enumerated on a board) and on the placeholder VID/PID 0x0483:0x5740 (D-09).

![Figure 61 — F13.3 — Demo-mode plot area of the beta GUI after 5 simulated bridge frames: left range-Doppler map (dB) with CFAR detections (red circles), right PPI with Kalman tracks (cyan); range/velocity scaling UNVERIFIED (assumptions 4–6 of beta/gui/README.md). Rendered off-screen on 2026-10-09 by driving MainWindow.step() with the Tk root withdrawn and saving the matplotlib Figure (`fig.savefig`, 110 dpi) — only the plot canvas is captured; the Tk control row, notebook tabs and register panel are not in this image because no screen grab was taken — BETA (source: beta/gui/aeris10_gui/ui/main_window.py, sim/simulator.py; produced by a 20-line driver script equivalent to app.py --selftest plus fig.savefig into manual/figures/gui_demo_plots.png)](manual/figures/gui_demo_plots.png)

## 13.5 Tests

### Step 13.3 — Run the test suite [BETA, 76 passed on 2026-10-09]

- **Purpose:** verify parsers, DSP, simulator, register client and UI construction without hardware.
- **Parts & tools:** `.venv/bin/python -m pytest -q` in `beta/gui` (pytest configured with `testpaths = ["tests"]`, `addopts = "-q"` in `pyproject.toml`).
- **Action:** run the command.
- **Check:** executed for this edition: **`76 passed in 3.62s`** (the README text still says 72 and `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-X3 says 55 — both older counts; the suite grew with the register-command rewrite, `CHANGELOG.md` "Tests"). Coverage as described (source: `beta/gui/README.md`, "Test"): bridge frames (RTL testbench vector `tests/vectors/bridge_frame_from_rtl_tb.hex`, a hardware source fed a synthetic CDC stream interleaving frames, status strings, GPS and REG replies), register commands (codec, RTL register semantics, client ↔ demo register file round trip, firmware single-slot model), settings packet (byte-exact firmware vector, round trip, a model of the firmware receiver proving unpadded framing is accepted and GUI_V5's 64-byte zero padding is rejected), FPGA packet (word- and byte-level vectors from the Verilog, corruption, truncation, resynchronisation), status/GPS/GPSB parsers, CA-CFAR, DBSCAN, Kalman tracker, simulator → parser → assembler exactness, pipeline target recovery, CSV loading, headless Tk smoke tests (skipped if no display).
- **Figure:** —
- **⚠ Decision:** none.

## 13.6 FPGA register panel and ADC calibration

The panel "FPGA registers / ADC calibration" (`ui/register_panel.py`) exposes (source: `beta/gui/CHANGELOG.md`, "Added"): CONTROL bits, CFAR threshold, decimation, start bin; auto (pattern) calibration, pattern-check enable, manual tap + lane load, bitslip + lane, pattern A/B; decoded CAL_STAT lock mask / done / busy / align_fail / fifo_ovf, chosen tap + pass window for all 8 lanes, CAL_ERR, CAL_UNDET, ID; "Read all / refresh". Inputs are range-checked against the RTL field widths. Register map transcribed from the RTL (source: `beta/gui/aeris10_gui/protocol/register_map.py` `REGISTERS`, which cites `beta/fpga/rtl/radar_control_regs.v`; registers are 16 bits wide, 4-bit word addresses as seen by the GUI):

| Addr | Name | Access | Reset | Fields |
|---|---|---|---|---|
| 0x0 | CONTROL | rw | 0b101 | bit0 `use_long_chirp` (1), bit1 `adc_pwdn` (0), bit2 `usb_enable` (1) |
| 0x1 | CFAR_THR | rw | 10000 | `|I|+|Q|` threshold, 16 bit (10000 = original placeholder) |
| 0x2 | DECIM | rw | 0b01 | bits[1:0] range decimation mode (01 = peak) |
| 0x3 | START_BIN | rw | 0 | bits[9:0] first range bin passed to the decimator |
| 0x4 | CAL_CTRL | rw | 0 | bit0 `auto_start` (write 1: start auto calibration, toggle), bit1 `manual_load` (toggle), bit2 `bitslip_load` (toggle), bit3 `check_en` (level: pattern-check error counting) |
| 0x5 | CAL_LANE | rw | 0 | bits[2:0] lane 0..7 for CAL_TAP/CAL_SLIP writes and CAL_LANE_INFO read |
| 0x6 | CAL_TAP | rw | 16 | bits[4:0] manual IDELAY tap 0..31 (78 ps each) |
| 0x7 | CAL_SLIP | rw | 0 | bits[1:0] BITSLIP pulses for a manual bitslip load |
| 0x8 | CAL_PATT | rw | 0x55AA | `{pattern_b[7:0], pattern_a[7:0]}` expected alternating ADC test codes |
| 0x9 | CAL_STAT | ro | 0 | `{fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}` |
| 0xA | CAL_LANE_INFO | ro | 0 | `{1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]}` of lane CAL_LANE |
| 0xB | CAL_ERR | ro | 0 | pattern-check error counter (saturating) |
| 0xC | CAL_UNDET | ro | 0 | `{8'b0, undetermined[7:0]}` lanes constant in pattern |
| 0xF | ID | ro | 0xBE7A | beta build identifier |

The RTL additionally defines 0x0D CAL_BLIND_COEF, 0x0E CAL_BLIND_MARGIN and 0x10 CAL_BLIND_MIN for the blind method (source: `beta/fpga/rtl/radar_control_regs.v` address-map comment, lines 31-37); the GUI's 4-bit address map does not include them and the panel "shows it [blind calibration] as unavailable" (source: `beta/gui/CHANGELOG.md`, "Discrepancies" item 2). The calibration procedure using these registers is Step 16.5.

Recorded discrepancies (source: `beta/gui/CHANGELOG.md`, "Discrepancies / unresolved", condensed): (1) `HOST_LINK_DESIGN.md` §7 describes 32-bit registers with a different layout; the beta follows the RTL — run, mixers enable and the NCO word "are not offered because no RTL implements them"; (2) blind calibration not driven by any register in `radar_control_regs.v` (see above); (3) `radar_system_top.v:321-323` ties `reg_we`/`reg_addr`/`reg_wdata` of `ctl_regs` to constants, so "register writes do not reach the register file on the current RTL"; (4) the firmware `REG` implementation exists (chapter 12 §12.7) and the GUI was re-aligned to it line for line; (5) no request ID — the single in-flight command relies on timeout/retransmit.

## 13.7 Assumptions and known limitations

(source: `beta/gui/README.md`, "Assumptions and known limitations", copied in condensed form, numbering kept)

1. **A1 — FT601 byte-lane order** little-endian; the RTL declares a 2-bit `ft601_be` for a 32-bit bus — an RTL defect to resolve at bring-up. Packet length 35 bytes follows from A1.
2. **No CRC in the RTL packet**; integrity uses header, footer and the redundant shifted copies.
3. **No bin indices in the packet**; any lost packet shifts the whole frame until the next resync (option A only).
4. **Range scaling UNVERIFIED**: cell `r` → `r * max_distance / 64` m; the physical spacing of the 64 decimated range bins is not documented anywhere in the repository.
5. **Velocity scaling** uses the standard pulse-Doppler relation with `prf1` and `system_frequency`; not confirmed against the RTL.
6. **Azimuth angle** = `(Azimuth-1) * 360/50` degrees from `main.cpp:188-189`; `BeamPos` is shown as an index.
7. **Settings acknowledgement** does not exist in the protocol.
8. The status string has no terminator; the parser uses `ChirpCount:<n>|` as end marker.
9. Google Maps export dropped.
10. `filterpy` 1.4.5 (2018) on numpy 2.5.3: maintenance risk.
11. Only CPython 3.14.7 (Tk 9.0, then 9.1) on macOS was exercised.
12. **Register map mismatch** between `HOST_LINK_DESIGN.md` §7 and the RTL; the GUI follows the RTL.
13. **REG text protocol** matches the firmware line for line, but neither side has been exercised on hardware.

Behavioural changes versus the originals that matter on the bench (source: `beta/gui/CHANGELOG.md`, "Behavioural changes", condensed): CDC writes are **not** zero-padded by default (checkbox "Zero-pad CDC writes" reproduces the legacy behaviour that the firmware rejects); firmware value limits are enforced in the UI before sending; the STM32 CDC port is opened with pyserial as an OS serial port (no mock devices on enumeration failure); the RTL's real packet format is decoded; GPS text with 3 fields (firmware) or 4 (legacy) is accepted; no background threads — a single Tk timer polls the source (`--selftest` is deterministic).

## 13.8 Packaging

### Step 13.4 — Build the stand-alone bundle [BETA, executed by the beta author]

- **Purpose:** run the host application on a machine without Python.
- **Parts & tools:** `.venv/bin/pip install pyinstaller` (already in `requirements.txt`); `beta/gui/build_app.sh`; `pyinstaller_launcher.py` (because `aeris10_gui/__main__.py` uses a relative import).
- **Action:** `./build_app.sh` — PyInstaller `--onedir` → `dist/aeris10-gui/`, then runs `--demo --selftest`.
- **Check:** result recorded in the source: "PyInstaller 6.22.3 on Python 3.14.7 built a 134 MB `--onedir` bundle and `dist/aeris10-gui/aeris10-gui --demo --selftest` exited 0" (README "Package"); after the register work "135 MB … passes `--demo --selftest` (bridge) and `--demo --selftest --raw-ft601`, both exit 0" (CHANGELOG). Not re-run for this edition.
- **Figure:** —
- **⚠ Decision:** AC-P7 ("Packaged demo runs on a machine without Python") remains NOT RUN — the bundle was only executed on the build machine.

Acceptance criteria touched by this chapter (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`): AC-P1, AC-P2 MET (upstream dependency install/import); AC-P3 NOT MET (`GUI_V1.py` syntax); AC-P4, AC-P7 NOT RUN; AC-P5 "A unit-test suite exists and passes" is recorded NOT MET against the upstream tree and **MET (BETA)** as AC-X3 for `beta/gui` (count now 76); AC-P6 (hardware end-to-end) NOT RUN.


---

<!-- chapter 14: Manufacturing packages per board, stack-ups, BOMs with MPN confidence, fab checklist -->
# 14. Manufacturing packages

**Chapter status summary:** generated manufacturing packages per board — SOURCE-DERIVED (Frequency Synthesizer, RF PA) / PARTIAL (Main Board, Power Supply) in `engineering/PCB/<BOARD>/`, BETA in `beta/pcb/<BOARD>/exports/`; stack-ups — PARTIAL with PROPOSED fabrication notes; BOMs — PARTIAL (0 MPN in the source, BETA proposals with confidence classes); EAGLE-native export procedures — documented, not executed (EAGLE is not installed on the authoring machine). **The KiCad conversion is not the designer-released package**: the EAGLE files in `4_Schematics and Boards Layout/` remain the design master, and no package in this chapter may be sent to a fabricator without the checklist in §14.6 being closed. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `engineering/PCB/<BOARD>/README.md` (§1, §5, §8, §9) and `STACKUP.md` for the four boards; `beta/pcb/README.md`, `CHANGELOG.md`, `beta/pcb/<BOARD>/FAB_NOTES.md`, `BOM_<BOARD>_beta.csv`, `exports/EXPORT_LOG.md`; `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`; `docs/PCB/<BOARD>.md` §10; `docs/BOM/README.md`.

## 14.1 What exists, and where

Two generated package trees exist per board. Both were produced with kicad-cli 10.0.6 from a KiCad import of the EAGLE board (`kicad-cli pcb import --format eagle`, EAGLE layer 47 *Measures* remapped to `Dwgs.User`, EAGLE design rules transferred to the project file — source: `engineering/PCB/<BOARD>/README.md` preserve-original paragraph). The conversion approximates EAGLE's polygon pours and thermals.

| Board | Layers | Outline (mm) | Reference conversion (unmodified import) | BETA package (routed/cleaned copy) | Status of the reference package | BETA result (source: `beta/pcb/README.md`) |
|---|---|---|---|---|---|---|
| Main Board (RADAR_Main_Board) | 10 | 260 × 300 | `engineering/PCB/MAIN_BOARD/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/MAIN_BOARD/exports/` (same sub-directories) + `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb`, `FAB_NOTES.md`, `BOM_MAIN_BOARD_beta.csv` | PARTIAL | unconnected 15 → 0; DRC 912 → 1049 (no real new item; polygon/thermal-pad items now visible); outside outline 11 → 6 (DNP) |
| Power Supply Board (PowerBoard) | 2 | 280 × 300 | `engineering/PCB/POWER_SUPPLY/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/POWER_SUPPLY/exports/` (same sub-directories) + `beta/pcb/POWER_SUPPLY/POWER_SUPPLY.kicad_pcb`, `FAB_NOTES.md`, `BOM_POWER_SUPPLY_beta.csv` | PARTIAL | unconnected 308 → 89; DRC 163 → 328; outside outline 132 → 0; placement needs designer review |
| Frequency Synthesizer (Clocks_Freq_Synth_board) | 6 | 100 × 100 | `engineering/PCB/FREQUENCY_SYNTHESIZER/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/FREQUENCY_SYNTHESIZER/exports/` (same sub-directories) + `beta/pcb/FREQUENCY_SYNTHESIZER/FREQUENCY_SYNTHESIZER.kicad_pcb`, `FAB_NOTES.md`, `BOM_FREQUENCY_SYNTHESIZER_beta.csv` | SOURCE-DERIVED | unconnected 0 → 0; DRC 639 → 639 (capped; silk conflicts 147 → 103); copper untouched |
| RF Power Amplifier (RF_PA) | 4 | 35 × 60 | `engineering/PCB/RF_PA/` (gerber/, drill/, drawings/, svg/, assembly/, mechanical/, ipc/, 3d/, reports/, kicad/) | `beta/pcb/RF_PA/exports/` (same sub-directories) + `beta/pcb/RF_PA/RF_PA.kicad_pcb`, `FAB_NOTES.md`, `BOM_RF_PA_beta.csv` | SOURCE-DERIVED | unconnected 1 → 0; DRC 67 → 18; RF tracks untouched |

The "DRC before" figures are `engineering/PCB/<BOARD>/reports/DRC_report.json`, "after" `beta/pcb/<BOARD>/exports/reports/DRC_report.json`; KiCad caps each violation type at 199 entries (source: `beta/pcb/README.md`). The BETA export set is the same as that of `tools/kicad_pcb_pipeline.sh`, produced by `beta/pcb/tools/beta_export_package.sh` with the commands logged in `beta/pcb/<BOARD>/exports/EXPORT_LOG.md` (source: `beta/pcb/CHANGELOG.md` §All boards).

Files per package directory (file names for the Main Board; the other boards follow the same pattern with their own prefix and layer count — listing of `engineering/PCB/MAIN_BOARD/`):

| Sub-directory | Files | Format / note |
|---|---|---|
| `gerber/` | `MAIN_BOARD-F_Cu.gtl`, `-In1_Cu.g1 … -In8_Cu.g8`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Paste.gtp`, `-B_Paste.gbp`, `-F_Silkscreen.gto`, `-B_Silkscreen.gbo`, `-F_Fab.gbr`, `-B_Fab.gbr`, `-Edge_Cuts.gm1`, `-job.gbrjob` | RS-274X X2, Protel extensions, 6 decimals, mm |
| `drill/` | `MAIN_BOARD-PTH.drl`, `-NPTH.drl`, `-PTH-drl_map.pdf`, `-NPTH-drl_map.pdf`, `drill_report.txt` | Excellon mm, PTH/NPTH separate |
| `drawings/` | `MAIN_BOARD_top_layer.pdf`, `_bottom_layer_mirrored.pdf`, `_copper_layers.pdf` (one page per copper layer), `_outline.pdf`, `_assembly_top.pdf`, `_assembly_bottom_mirrored.pdf` | PDF; the two assembly PDFs are clipped by the A4 page frame (chapter 4 §4.5) |
| `svg/` | `MAIN_BOARD-F_Cu.svg … -B_Cu.svg`, `-F_Mask/-B_Mask`, `-F_Silkscreen/-B_Silkscreen`, `-F_Fab/-B_Fab`, `-Edge_Cuts.svg`, `MAIN_BOARD_top_composite.svg`, `MAIN_BOARD_bottom_composite_mirrored.svg` | per-layer plots (the layer-plot figures of chapters 4–7 are rendered from the two composites) |
| `assembly/` | `MAIN_BOARD_BOM.csv`, `MAIN_BOARD_pick_and_place.csv` | BOM from the schematic (values only); P&P both sides, mm |
| `mechanical/` | `MAIN_BOARD_outline.dxf`, `MAIN_BOARD_top_fab.dxf`, `MAIN_BOARD_board_only.step` | STEP is board body only (no component models) |
| `ipc/` | `MAIN_BOARD.xml.gz` (IPC-2581), `MAIN_BOARD_netlist.d356` (IPC-D-356) | for fabricator netlist test |
| `3d/` | `MAIN_BOARD_render_top.png`, `_bottom.png`, `_isometric.png` | KiCad renders, no component models |
| `reports/` | `DRC_report.txt`, `DRC_report.json`, `board_statistics.md`, `design_rules_mapping.md`, `kicad_import_report.txt` | reference package only has the import report and the DRU mapping |
| `kicad/` | `MAIN_BOARD.kicad_pcb`, `.kicad_pro`, `.kicad_prl` | editable conversion (reference package); the BETA board is at `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb` |

## 14.2 Deliverable tables (claude.md addendum §18), copied from the package READMEs

### Main Board (RADAR_Main_Board) — `engineering/PCB/MAIN_BOARD/README.md` §1 [PARTIAL]


| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/MAIN_BOARD_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/MAIN_BOARD_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/MAIN_BOARD_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/MAIN_BOARD_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/MAIN_BOARD_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/MAIN_BOARD-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/MAIN_BOARD_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/MAIN_BOARD_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/MAIN_BOARD_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/MAIN_BOARD_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/MAIN_BOARD_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/MAIN_BOARD_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/MAIN_BOARD_board_only.step`, `mechanical/MAIN_BOARD_top_fab.dxf`, `ipc/MAIN_BOARD.xml` (IPC-2581), `ipc/MAIN_BOARD_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/MAIN_BOARD.kicad_pcb` + `.kicad_pro`.

### Power Supply Board (PowerBoard) — `engineering/PCB/POWER_SUPPLY/README.md` §1 [PARTIAL]


| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/POWER_SUPPLY_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/POWER_SUPPLY_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/POWER_SUPPLY_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/POWER_SUPPLY_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/POWER_SUPPLY_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/POWER_SUPPLY-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/POWER_SUPPLY_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/POWER_SUPPLY_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/POWER_SUPPLY_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/POWER_SUPPLY_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/POWER_SUPPLY_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/POWER_SUPPLY_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/POWER_SUPPLY_board_only.step`, `mechanical/POWER_SUPPLY_top_fab.dxf`, `ipc/POWER_SUPPLY.xml` (IPC-2581), `ipc/POWER_SUPPLY_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/POWER_SUPPLY.kicad_pcb` + `.kicad_pro`.

### Frequency Synthesizer (Clocks_Freq_Synth_board) — `engineering/PCB/FREQUENCY_SYNTHESIZER/README.md` §1 [SOURCE-DERIVED]


| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/FREQUENCY_SYNTHESIZER_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/FREQUENCY_SYNTHESIZER_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/FREQUENCY_SYNTHESIZER_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/FREQUENCY_SYNTHESIZER_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/FREQUENCY_SYNTHESIZER_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/FREQUENCY_SYNTHESIZER-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/FREQUENCY_SYNTHESIZER_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/FREQUENCY_SYNTHESIZER_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/FREQUENCY_SYNTHESIZER_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/FREQUENCY_SYNTHESIZER_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/FREQUENCY_SYNTHESIZER_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/FREQUENCY_SYNTHESIZER_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/FREQUENCY_SYNTHESIZER_board_only.step`, `mechanical/FREQUENCY_SYNTHESIZER_top_fab.dxf`, `ipc/FREQUENCY_SYNTHESIZER.xml` (IPC-2581), `ipc/FREQUENCY_SYNTHESIZER_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` + `.kicad_pro`.

### RF Power Amplifier (RF_PA) — `engineering/PCB/RF_PA/README.md` §1 [SOURCE-DERIVED]


| # | Item | File | Status |
|---|---|---|---|
| 1 | PCB top-layer drawing | `drawings/RF_PA_top_layer.pdf` | GENERATED |
| 2 | PCB bottom-layer drawing (mirrored) | `drawings/RF_PA_bottom_layer_mirrored.pdf` | GENERATED |
| 3 | Copper-layer views (one page per copper layer) | `drawings/RF_PA_copper_layers.pdf` | GENERATED |
| 4 | Board-outline drawing | `drawings/RF_PA_outline.pdf` | GENERATED |
| 5 | Mechanical dimensions (outline + holes, DXF / STEP) | `mechanical/RF_PA_outline.dxf` | GENERATED |
| 6 | Drill map | `drill/RF_PA-PTH-drl_map.pdf` | GENERATED |
| 7 | Hole table | `README.md (§5) and drill/drill_report.txt` | GENERATED |
| 8 | Component placement drawing (fab layer with pad outlines) | `drawings/RF_PA_assembly_top.pdf` | GENERATED |
| 9 | Top assembly drawing | `drawings/RF_PA_assembly_top.pdf` | GENERATED |
| 10 | Bottom assembly drawing (mirrored) | `drawings/RF_PA_assembly_bottom_mirrored.pdf` | GENERATED |
| 11 | Fabrication drawing | `drawings/RF_PA_outline.pdf + drill maps + STACKUP.md` | PARTIAL — no vendor notes (material, finish, tolerances) in the source |
| 12 | Layer stack-up documentation | `STACKUP.md` | PARTIAL — layer order from DRU; materials/thickness UNVERIFIED |
| 13 | BOM with reference designators | `assembly/RF_PA_BOM.csv` | GENERATED — 0 MPN attributes in the source (values only) |
| 14 | Pick-and-place file | `assembly/RF_PA_pick_and_place.csv` | GENERATED |
| 15 | Manufacturing export checklist | `README.md (§8)` | GENERATED |

Additional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), `svg/` per-layer SVG, `mechanical/RF_PA_board_only.step`, `mechanical/RF_PA_top_fab.dxf`, `ipc/RF_PA.xml` (IPC-2581), `ipc/RF_PA_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/RF_PA.kicad_pcb` + `.kicad_pro`.


## 14.3 Stack-ups

Layer order and copper thickness in every `STACKUP.md` come from the EAGLE DRU; dielectric thicknesses are the EAGLE DRU table and **not** a vendor stack-up; total thickness is not defined in any source (KiCad assumed 1.6 mm); material, prepreg/core assignment, finish and impedance targets must be supplied by the designer/fabricator (source: `engineering/PCB/<BOARD>/STACKUP.md` caveats; `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md` MDR-07). The only material evidence in the upstream project is `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` (a 6-layer picture, unlabelled, matching no board exactly) and the PCBWay impedance note delivered with the Frequency Synthesizer production files (RO4350B h = 0.102 mm, 50 Ω w = 0.204 mm, 100 Ω w/s = 0.204/0.26 mm, maskless RF, coupons).

| Board | DRU | Layer setup (EAGLE) | DRU dielectrics (mm, top → bottom) | PROPOSED fabrication stack (BETA `FAB_NOTES.md` §2) | PROPOSED finished thickness |
|---|---|---|---|---|---|
| Main Board | `PCBWay_8L_100um-Track` (name says 8, board has 10 layers) | `(1*2+3*4+5*12+13*14+15*16)` | 0.102, 0.2, 0.2, 0.2, 0.2, 0.15, 0.2, 0.2, 0.102 | L1 and L9 on RO4350B 4 mil, FR-4 inside; ENIG; maskless RF; 1 oz all layers | 2.0 mm ± 10 % (DRU sum 1.554 + copper ≈ 1.9 mm) |
| Power Supply | `PCBWay_2L_100um-Track` | `(1*16)` | 1.5 | FR-4 Tg 150 °C core; 35 µm, PROPOSED 70 µm / 2 oz; no impedance control | 1.6 mm ± 10 % |
| Frequency Synthesizer | `PCBWay_6L_100um-Track` | `(1+2*3+14*15+16)` | 0.11, 0.6, 0.11, 0.6, 0.11 | L1 on RO4350B 4 mil (DRU 0.11 vs note 0.102 — reconcile), FR-4 cores 0.6, L5/6 RO4350B PROPOSED (B.Cu LVDS pairs); ENIG; maskless RF | 1.6 mm ± 10 % with thinned cores, or 2.0 mm |
| RF PA | `PCBWay_4L_100um-Track` (unexplained 70 µm third copper slot) | `(1+2*15+16)` | 0.11, 1.2, 0.11 | F.Cu on RO4350B 4 mil, FR-4 core 1.2; paddle vias filled and capped PROPOSED; ENIG; maskless RF | 1.6 mm ± 10 % (DRU sum 1.42 + copper ≈ 1.56 mm) |

Full per-layer tables are in chapters 4–7 §Stack-up. Common proposal items for all boards (source: `beta/pcb/<BOARD>/FAB_NOTES.md` §3): ENIG 2–5 µin Au over 120–240 µin Ni; green LPI mask both sides, white silk; vias tented except RF-layer vias near maskless traces (fab to confirm); 100 % electrical test against the supplied IPC-D-356 netlist; IPC-A-600 Class 2; single boards, fab may panelise with rails, no V-cut through RF areas. Open items for every board (same source §6): confirm stack-up materials and total thickness; confirm the RF-layer dielectric (0.102 vs 0.11 mm) and re-solve w/s with coupons; confirm finish and mask-opening policy on RF traces; review the DRC disposition before CAM.

## 14.4 BOMs with MPN confidence

The source schematics carry **no MPN attribute on any part** (0/98, 0/28, 0/40, 0/11 lines; source: `docs/BOM/README.md`). `docs/BOM/BOM_<BOARD>.csv` is generated by `tools/gen_eagle_bom.py` directly from the `.sch` files; `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv` adds `manufacturer, mpn, mpn_confidence, dnp, note` with proposals from `beta/pcb/tools/beta_bom_mpn.py` (Murata GRM / Yageo RC / Murata LQP03 / TDK VLP families for passives, orderable IC codes for the device sets — source: `beta/pcb/README.md`).

| Board | Physical references | Line items | References without value | HIGH (deviceset = MPN) | MEDIUM (standard passive from value+package) | LOW (guess / non-standard value / conflict) | EMPTY (no value) |
|---|---|---|---|---|---|---|---|
| Main Board | 776 | 98 | 244 | 23 lines / 204 pcs | 41 / 461 | 30 / 93 | 4 / 18 |
| Power Supply Board | 312 | 28 | 80 | 7 lines / 79 pcs | 18 / 225 | 3 / 8 | 0 / 0 |
| Frequency Synthesizer | 184 | 40 | 47 | 10 lines / 37 pcs | 22 / 110 | 6 / 29 | 2 / 8 |
| RF Power Amplifier | 25 | 11 | 6 | 5 lines / 6 pcs | 6 / 19 | 0 / 0 | 0 / 0 |

Line counts obtained with `python3 -c "import csv,collections;print(collections.Counter(r['mpn_confidence'] for r in csv.DictReader(open('beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv'))))"` on 2026-10-09; quantities from `beta/pcb/README.md` §BOM confidence; reference/line/value counts from `docs/BOM/README.md`. Conflicts flagged in the BETA `note` column that only the designer can resolve (source: `beta/pcb/README.md`): voltage ratings absent; non-E-series values (2.443 kΩ, 103 pF, 107.3 nH); 47 µF in 0201; NX3225 footprint with a 32.768 kHz value; 5 mΩ shunt with a 0.1 Ω part number; Main Board R60/R61/R83/R84/R145/R146 marked `dnp = yes` (no net). BOM validation procedure (source: `docs/BOM/README.md` §Validation): regenerate; compare `qty` sum with the element counts 776 / 312 / 25 / 184; look every `UNVERIFIED` line up at a distributor and write the MPN into the schematic part attribute `MPN`, then regenerate; fill every empty value (244/80/6/47); add a `DNP` attribute per variant; acceptance = 0 `UNVERIFIED`, 0 empty values, DNP column present, part count identical to the `.mnt` pick-and-place.

## 14.5 EAGLE-native export procedures (summary of `docs/PCB/00_COMMON_EAGLE_PROCEDURES.md`)

All four boards are EAGLE XML files: Main Board 7.4.0 (sch + brd), Frequency Synthesizer 9.6.2, RF PA 9.6.2, Power Board sch 9.6.2 / brd 7.4.0 (mismatch); libraries are embedded. EAGLE 9.6.2 opens all of them (and upgrades 7.4.0 files on save — keep the originals), as does Fusion 360 Electronics; KiCad 7/8/9 imports EAGLE 6+ XML. Output file names below are the tools' defaults and are **expected, not observed** — the upstream project never produced them (source: `00_COMMON_EAGLE_PROCEDURES.md` preamble). EAGLE is not installed on the authoring machine; none of these procedures has been executed here.

| ID | Procedure | Tool / menu | Expected output | Acceptance |
|---|---|---|---|---|
| P-EAGLE-01 | Open and consistency-check a board pair | EAGLE 9.6.2 File → Open → Schematic; board opens with it; ERC → *Consistency check*. Power Board: expect the "severed annotation" dialog, do **not** accept automatic fixes; export both part lists and reconcile | both windows open | "Board and schematic are consistent" |
| P-EAGLE-02 | ERC | schematic → Tools → ERC; reopen every `<approved>` entry (Main Board: 4 on `STM32_MISO_1V8`) | screenshot/transcript into `docs/PCB/reports/<board>_ERC_<date>.txt` (directory to create) | 0 errors; every warning dispositioned |
| P-EAGLE-03 | DRC with the stored rules | board → type `RATSNEST` (expect "Nothing to do" on Synth/PA; 2 390 airwires Main, 309 Power) → Tools → DRC → *Check* with the stored DRU | DRC error list, exported | 0 unapproved errors; each approved error justified |
| P-EAGLE-04 | Gerber + drill (EAGLE 9.6.2 CAM) | File → CAM Processor → Templates `2 Layer` / `4 Layer` / `6 Layer` (Main Board: start from `6 Layer`, add layers 3, 4, 5, 12, 13, 14 as inner copper); RS-274X, mm, 4.4, ZIP; Excellon mm, PTH/NPTH separate | `CAMOutputs/GerberFiles/copper_top.gbr, copper_inner_<n>.gbr, copper_bottom.gbr, soldermask_*, silkscreen_*, solderpaste_*, profile.gbr, gerber_job.gbrjob`; `DrillFiles/drill_1_16.xln`, `drill_npth.xln` | viewer check: layer count and outline match `docs/MECHANICAL/drawings/<BOARD>_outline.svg`; drill counts match `docs/PCB/<BOARD>.md` |
| P-EAGLE-05 | Gerber + drill (EAGLE 7.4 CAM, for the 7.4.0 files) | `gerb274x.cam` / `excellon.cam` jobs | `<board>.cmp, .sol, .ly2…, .plc/.pls, .stc/.sts, .crc/.crs, .drd + .dri` | prefer 9.6.2 unless the designer requires 7.4 |
| P-KICAD-01 | Alternative open-source export | KiCad File → Import → Non-KiCad Project → EAGLE; re-enter the 10-layer stack for the Main Board in Board Setup; `kicad-cli pcb export gerbers` / `export drill` | `board-F_Cu.gbr … board-PTH.drl, board-NPTH.drl, board-job.gbrjob` | re-DRC and compare with the EAGLE output before use (importer approximates polygons/thermals) |
| P-EAGLE-06 | BOM export | schematic → File → Run ULP → `bom.ulp` → Parts/Values, CSV, all attributes; compare with `docs/BOM/BOM_<BOARD>.csv` | `<Board>_BOM.csv` | every line has MPN + package; passives valued (244/80/6/47 missing today); DNP column |
| P-EAGLE-07 | Pick-and-place and drawings | board → Run ULP → `mountsmd.ulp` (+ `mount.ulp` for THT); assembly drawing = layers 20, 21, 25, 51 (+ bottom) → Print → PDF 1:1; fab drawing = layers 20 + 44 + 45 + dimensions on 48 + text block (layer count, material, thickness, copper, finish, colours, impedance table from the PCBWay note, min track 0.1 mm, min drill 0.15 mm Main/Synth/PA, 0.3 mm Power) | `<board>-smd.mnt`, `-tht.mnt` (`RefDes,Value,Package,X,Y,Rot,Side`), `<board>_assembly_top/bottom.pdf`, `<board>_fab.pdf` | Synth: regenerate the `.mnt` pair to supersede the four duplicate files |
| P-EAGLE-08 | Schematic PDF | schematic → File → Print → PDF, all sheets, fit to page, black, caption | `<board>_schematic.pdf` under `docs/PCB/schematics/` (directory to be created) | — (SOURCE-DERIVED renders exist in `engineering/ELECTRICAL/schematics/` meanwhile) |
| P-EAGLE-09 | Netlist export without EAGLE | `python3 tools/extract_eagle_netlist.py <sch> --part <REF> --out <csv>` / `--list-parts`; EAGLE alternative File → Export → Netlist | CSV net ↔ pin ↔ pad | used for the connection reports of chapters 4–7 |

Expected manufacturing package structure per board (source: `00_COMMON_EAGLE_PROCEDURES.md` §Manufacturing package structure):

```
4_7_Production Files/<Board>/
├── Gerber/        copper_*.gbr, soldermask_*.gbr, silkscreen_*.gbr, solderpaste_*.gbr, profile.gbr, *.gbrjob
├── Drill/         drill_*_pth.xln, drill_npth.xln, drill map pdf
├── <Board>_fab.pdf
├── <Board>_assembly_top.pdf, <Board>_assembly_bottom.pdf
├── <Board>_BOM.csv            (with MPN, manufacturer, DNP)
├── <Board>-smd.mnt, <Board>-tht.mnt
├── <Board>_schematic.pdf
├── <Board>_netlist.ipc (IPC-D-356, optional)
└── reports/ ERC, DRC, impedance/stack-up confirmation from the fab
```

Board-specific notes for the EAGLE path: Main Board — P-EAGLE-04 with a **10-layer** job; reopen the 211 approved DRC entries; decide 8 vs 10 layers (copper exists on all 10) (source: `docs/PCB/MAIN_BOARD.md` §5, §7). Power Board — complete placement and routing first (designer); `RATSNEST` expects 309 airwires until then (source: `docs/PCB/POWER_SUPPLY.md` §5). Frequency Synthesizer — template *6 Layer* with inner layers 2, 3, 14, 15; keep `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` under `reports/` (source: `docs/PCB/FREQUENCY_SYNTHESIZER.md` §5, §9). RF PA — template *4 Layer* with inner layers 2 and 15; add the impedance-note text to the fab drawing only after the designer confirms it applies to this stack (source: `docs/PCB/RF_PA.md` §5).

## 14.6 Fabrication checklist (README §8 of every package)

The checklist is identical for the four boards except for the routing line; state on 2026-10-09 (source: `engineering/PCB/<BOARD>/README.md` §8):

| Item | Main Board | Power Supply | Frequency Synthesizer | RF PA |
|---|---|---|---|---|
| Gerber set (all copper, mask, paste, silk, outline, fab) exported | done | done | done | done |
| Excellon drill files PTH/NPTH + drill map + report | done | done | done | done |
| Pick-and-place (both sides, mm, CSV) | done | done | done | done |
| BOM with reference designators | done | done | done | done |
| BOM with manufacturer part numbers for 100 % of lines | open | open | open | open |
| Fabrication drawing with vendor notes (material, thickness, finish, mask/silk colours, tolerances, impedance) | open | open | open | open |
| Stack-up confirmed by the fabricator | open | open | open | open |
| Layout routed to completion (0 airwires / 0 unconnected) | open in the source (BETA: 0 unconnected, netlist issues remain) | open (BETA: 89 open) | done | open in the source (1 unconnected after import; BETA 0) |
| DRC with 0 unapproved errors, waivers documented | open | open | open | open |
| Designer review of the KiCad conversion against EAGLE (pours, thermals, text) | open | open | open | open |
| Gerbers viewed in an independent viewer and compared with the outline drawing | open | open | open | open |
| IPC-2581 / IPC-D-356 netlist test accepted by the fabricator | open | open | open | open |

Known gaps common to all boards (source: `engineering/PCB/<BOARD>/README.md` §9, BLOCKED — MISSING DATA): board material, finished thickness, copper weight per layer, surface finish, mask/silk colours and impedance targets are not recorded in the EAGLE files; no MPN attributes; 3-D component models not embedded (Autodesk online URNs) so every STEP is board-only.

## 14.7 Acceptance criteria per board (copied from `docs/PCB/<BOARD>.md` §10)

### Main Board (RADAR_Main_Board) — `docs/PCB/MAIN_BOARD.md` §10

| Criterion | Measure |
|---|---|
| Layout complete | 0 airwires; 0 elements outside 0..260 × 0..300 mm |
| DRC | 0 unapproved errors with PCBWay 10-layer (or revised) rules |
| ERC | 0 errors |
| Gerber set | 10 copper + 2 mask + 2 silk + 2 paste + profile + job file; viewer check matches `MAIN_BOARD_outline.svg` (260 × 300 mm, 8 × Ø3.2 holes) |
| Drill | PTH count = 2 893 vias + plated pads; NPTH = 8 × 3.2 mm + 2 × 0.9 mm |
| Stack-up | vendor drawing for 10 layers, RO4350B 0.102 mm outer cores, 50 Ω at 0.204 mm, 100 Ω diff 0.204/0.26 mm confirmed |
| BOM | 100 % MPN coverage; DNP column; quantity sum = 776 (minus DNP) |
| Design decisions closed | FT601 wired or removed; FPGA part; HSE crystal; XADC reference wiring |

### Power Supply Board (PowerBoard) — `docs/PCB/POWER_SUPPLY.md` §10

| Criterion | Measure |
|---|---|
| Consistency | ERC consistency check passes after re-linking sch/brd in one EAGLE version |
| Placement/routing | 0 airwires, 0 off-board parts, final outline recorded |
| DRC/ERC | 0 errors |
| Gerber/drill | 2 Cu layers + mask/silk/paste/profile; NPTH 8 × Ø3.2; viewer matches `POWER_SUPPLY_outline.svg` (280 × 300 mm, or the revised outline) |
| BOM | 100 % MPN; all passives valued; datasheets for TPS562208 and LM2662 added to `7_Components Datasheets` |
| Design closure | PA supply (22 V rail) architecture decided and consistent with `Power Management V6.xlsx` and `RF_PA.sch` |

### Frequency Synthesizer (Clocks_Freq_Synth_board) — `docs/PCB/FREQUENCY_SYNTHESIZER.md` §10

| Criterion | Measure |
|---|---|
| DRC/ERC | 0 errors, reports archived |
| Gerber/drill | 6 Cu + mask/silk/paste/profile; NPTH 4 × Ø3.2; PTH = 769 vias + pads; viewer matches `FREQUENCY_SYNTHESIZER_outline.svg` (100 × 100 mm) |
| Stack-up | one vendor-confirmed 6-layer stack consistent with the impedance note |
| BOM | 100 % MPN, 0 value-less references, oscillator conflict resolved |
| P&P | single regenerated pair of `.mnt` files, duplicates removed |
| Function (post-fab) | AD9523 lock (STATUS0/1 high), OUT6 = 100 MHz, OUT4/5 = 400 MHz, OUT10/11 = 120 MHz measured — hardware test, not a file check |

### RF Power Amplifier (RF_PA) — `docs/PCB/RF_PA.md` §10

| Criterion | Measure |
|---|---|
| DRC/ERC | 0 errors (already 0 approved in file; must be re-run) |
| Gerber/drill | 4 Cu + mask/silk/paste/profile; NPTH 7 × Ø3.2; PTH count = 342 vias + pads; viewer matches `RF_PA_outline.svg` (35 × 60 mm) |
| Stack-up | vendor drawing confirmed; RF layer mask-free as per impedance note |
| BOM | 100 % MPN; all 25 references valued/identified |
| System | PA supply voltage/current source decided; quantity per variant (16 for AERIS-10X) confirmed; RF performance (gain, P1dB at 10.5 GHz) remains **unverified** until measured |


Do not declare any board fabrication-ready on the basis of the existing `.sch/.brd` files, of the KiCad conversion or of the BETA packages (source: `docs/PCB/MAIN_BOARD.md` §10; `beta/pcb/README.md`).

## 14.8 Antenna panel package (PROPOSED DESIGN)

The proposed patch panel has its own KiCad-native package in `engineering/DESIGN/ANTENNA/kicad_exports/` (Gerber `F_Cu/B_Cu/F_Mask/B_Mask/F_Silkscreen/Edge_Cuts` + job file, drill, PDF, SVG, STEP, 3-D render, statistics, DRC — all steps exit 0, source: `kicad_exports/EXPORT_LOG.md`). It is a design proposal awaiting simulation closure and a coupon measurement (chapter 8 §8.6) and is **not released** for fabrication.


---

<!-- chapter 15: Step-by-step mechanical assembly, board installation, harness, integration order, inspection checkpoints -->
# Assembly procedure — PCB assemblies, head, harness, pedestal

**Author of this chapter:** Antidrone Ukraine · antidrone.cc.

**Status summary:** the whole procedure is **PROPOSED / BETA — never executed** (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, header). Mechanical steps rest on the PROPOSED DESIGN of chapter 10 (D-07…D-13); electrical integration order is SOURCE-DERIVED from the connector matrix and the firmware power sequence (`engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md`, status PARTIAL); cable lengths are PROPOSED (`engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`); Molex pin order, the RFIN/RFOUT side of the Main Board SMA pairs and the PA-instance assignment are UNVERIFIED (`engineering/SYSTEM/interfaces/interconnection_table.md` §2, §7). Steps that depend on an open decision carry ⚠ and name it. Torque values quoted from the step source have no deeper repository source and are marked ASSUMED.

**Sources:** `manual/ASSEMBLY_STEPS_SOURCE.md` (phases A–D), `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` (ASM-SEQ-01), `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (part # and fasteners), `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-04…07`, `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` (CBL-001…144), `engineering/SYSTEM/interfaces/interconnection_table.md`, `engineering/ELECTRICAL/power_distribution/power_rails.md`, `engineering/MECHANICAL/dimensions/*.md`, `tools/design_layout.py` (stations), `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`.

**Figures in this chapter:** F15.1 exploded view, F15.2–F15.5 per-board assembly drawings, F15.6 DSN-MECH-07, F15.7 DSN-MECH-06, F15.8 DSN-MECH-04, harness schedule excerpt (table).

## 15.0 Safety preamble — read before any step

Copied from the step source (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, "Safety preamble"), with the evidence behind each hazard:

- **S1 — 22 V PA drain supply (up to 45 A pulsed):** never connect PA boards with VG at 0 V; VG −4 V first (firmware sequence). Evidence: QPA2962 bias-up "VG −4 V → VD +22 V → raise VG until IDQ 1680 mA" (source: `engineering/ELECTRICAL/power_distribution/power_rails.md` §1 row `+22V0`/`VD`, xlsx L58-L62); 45 A pulse peak from D-14 (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2). The 22 V source itself is **not in any CAD file** (conflict K4).
- **S2 — RF radiation:** no transmission without a terminated or connected antenna/PA path; 16 × 10 W peak (source: QPA2962 PSAT 40 dBm, `engineering/DESIGN/00_DESIGN_BASIS.md` §1).
- **S3 — Rotating pedestal:** keep hands clear; set the stepper-driver current limit before first motion (TB6600-class, 9–42 V, 4 A, 20 V selected — source: `engineering/DESIGN/00_DESIGN_BASIS.md` §1, xlsx row 63).
- **S4 — ESD:** all boards are ESD-sensitive (GaN PA, ADC, FPGA).

Also applicable throughout: ⚠ **K2** — the beta firmware assumes the 8 MHz HSE crystal found on the schematic (`beta/stm32/DECISIONS.md` D-01); ⚠ **K4** — 22 V PA supply not in CAD; ⚠ **D-14** — per-pulse drain gating required by the thermal design (chapter 10 §10.7) has no hardware yet.

## 15.1 Pre-assembly inspection checkpoints

Copied (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §A):

| CP | Check | Acceptance | Evidence/tool |
|---|---|---|---|
| CP-1 | Bare board matches outline and hole table | dimensions per `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md`, ±0.2 mm (vendor tolerance UNSPECIFIED) | caliper; fab CoC |
| CP-2 | Assembled board matches BOM + pick-and-place | every reference populated with the BOM value; polarity per `drawings/<BOARD>_assembly_top.pdf` | AOI / visual |
| CP-3 | No shorts between rails | > 1 kΩ between every rail and GND before power-up (rail list `engineering/ELECTRICAL/power_distribution/power_rails.md`) | DMM |
| CP-4 | Power Board rails at nominal with no load | each X2..X35 output within the net-name voltage (currents UNKNOWN) | bench PSU + DMM |

![Figure 62 — F15.1 — Conceptual exploded view of the electronics set used as the orientation reference for phases A–C; board outlines verified from the .brd files, arrangement conceptual (ASM-EXP-01) — CONCEPTUAL (source: engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png; produced by tools/gen_assembly_exploded_view.py)](engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.png)

## 15.2 Phase A — PCB assemblies (repeat per board: Main, Power, Synth, 16 × RF PA)

### Step 15.1 — Inspect the bare boards [PROPOSED / SOURCE-DERIVED acceptance values]

- **Purpose:** confirm the fabricated board matches the verified outline and hole table before anything is mounted (CP-1).
- **Parts & tools:** bare PCBs; caliper; `engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md`; fab certificate of conformance.
- **Action:** measure the outline bounding box and every mounting hole; compare with chapter 10 §10.1 (Main 260.00 × 300.00, 10 holes; Power 280.00 × 300.00, 8 holes; Synth 100.00 × 100.00, 4 holes; RF PA 35.00 × 60.00, 7 holes — all Ø3.20 NPTH).
- **Check:** dimensions within ±0.2 mm (vendor tolerance UNSPECIFIED); hole count exact; board thickness recorded (it is ASSUMED 1.6 mm everywhere in the design — G-01).
- **Figure:** F10.10a (plan view of the four outlines).
- **⚠ Decision:** G-10 — the Power Board's inner hole pattern "suggests a smaller board than 280 × 300"; if the delivered outline differs, the carrier rails #29/#30 (300 mm) and standoffs #31–#38 must be re-checked.

### Step 15.2 — Populate per BOM and pick-and-place [BETA BOM, SOURCE-DERIVED drawings]

- **Purpose:** assembled board matches the BOM and the placement data (CP-2).
- **Parts & tools:** `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv` (with MPN confidence column) and `beta/pcb/<BOARD>/exports/pos` placement files; reflow/hand assembly equipment; AOI or magnifier.
- **Action:** place every reference listed in the BOM at the position and rotation of the P&P file; orient polarised parts per the assembly drawing (F15.2–F15.5).
- **Check:** every reference populated; no reference left with an empty value (the original EAGLE BOMs have 0 MPN attributes — AC-B5 NOT MET, so the beta MPN proposals must be reviewed by the owner before purchase); polarity per the assembly drawing.
- **Figure:** F15.2–F15.5.
- **⚠ Decision:** K1 (FPGA part XC7A50T on the schematic vs XC7A100T in the FPGA README) — the Main Board U42 placement follows the schematic part; the Main Board rev. B (FT601 wired) is a separate BETA layout (`beta/pcb/MAIN_BOARD_REVB/`), not the baseline of this step.

![Figure 63 — F15.2 — Main Board, top assembly drawing (component placement, references), page 1 of engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf; layout state PARTIAL (2 390 airwires in the EAGLE source) — SOURCE-DERIVED / PARTIAL (source: engineering/PCB/MAIN_BOARD/drawings/MAIN_BOARD_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh (kicad-cli 10.0.6), rendered to PNG by `pdftoppm -png -r 110 -f 1 -l 1`)](manual/figures/MAIN_BOARD_assembly_top-1.png)

![Figure 64 — F15.3 — Power Supply Board, top assembly drawing, page 1; layout state PARTIAL (309 airwires in the EAGLE source) — SOURCE-DERIVED / PARTIAL (source: engineering/PCB/POWER_SUPPLY/drawings/POWER_SUPPLY_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh, rendered by pdftoppm)](manual/figures/POWER_SUPPLY_assembly_top-1.png)

![Figure 65 — F15.4 — Frequency Synthesizer Board, top assembly drawing, page 1 — SOURCE-DERIVED (source: engineering/PCB/FREQUENCY_SYNTHESIZER/drawings/FREQUENCY_SYNTHESIZER_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh, rendered by pdftoppm)](manual/figures/FREQUENCY_SYNTHESIZER_assembly_top-1.png)

![Figure 66 — F15.5 — RF PA board, top assembly drawing, page 1 (one of 16 identical boards) — SOURCE-DERIVED (source: engineering/PCB/RF_PA/drawings/RF_PA_assembly_top.pdf; produced by tools/kicad_pcb_pipeline.sh, rendered by pdftoppm)](manual/figures/RF_PA_assembly_top-1.png)

### Step 15.3 — Rail-to-ground resistance before power [SOURCE-DERIVED rail list]

- **Purpose:** detect solder shorts before any rail is energised (CP-3).
- **Parts & tools:** DMM; rail register `engineering/ELECTRICAL/power_distribution/power_rails.md` §1 (36 rows).
- **Action:** on every assembled board measure resistance between each rail net and GND at its connector (Power Board outputs X2…X35; Main Board inputs X1, X4…X24, X55, X56; Synth inputs X10…X15; PA `22V`, X2 `VG`).
- **Check:** > 1 kΩ on every rail (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` CP-3). Record the values.
- **Figure:** F3.2 (power distribution, chapter 3).
- **⚠ Decision:** none.

### Step 15.4 — Power Board alone on the bench supply [SOURCE-DERIVED, ⚠ design review item]

- **Purpose:** verify every regulator output with no load (CP-4) before the enable bus is ever driven.
- **Parts & tools:** bench PSU 12–17 V (VIN range from the board silkscreen `Vin [12-17]V`, source: `power_rails.md` §1 row `VIN`), DMM.
- **Action:** connect VIN/GND to X1 (AK300/2, KL1 VIN, KL2 GND — source: `interconnection_table.md` §1). Measure each output X2…X35 against its net-name nominal: always-on rails (+3V3 X16, +3V3_AN X12, +3V3_XO X35, +5V0_LO X6, +3V3_LO_1 X8, +3V3_LO_2 X7, +3V4 X23, −3V4 X24, +5V0_0 X22, +5V0_1…5 X2/X9/X17/X25/X28, +5V0_ADTR X26) are present with no enable; enabled rails stay at 0 V until the SV1 enable lines are driven (all EN nets are MCU outputs initialised LOW).
- **Check:** each present output within the net-name voltage (currents UNKNOWN — not documented anywhere, `power_rails.md` §4 item 5); the enabled rails read 0 V with SV1 open.
- **Figure:** F3.2.
- **⚠ Decision:** `+5V0_LO` LDO U30 (ADM7151) is fed directly from the 12–17 V bus — "CONFLICT / REQUIRES DESIGN REVIEW … check against the ADM7151 input-voltage rating" (source: `power_rails.md` §1 row `+5V0_LO`, §4 item 2). Do not exceed the LDO's rating until the owner resolves it.

## 15.3 Phase B — Mechanical assembly of the radar head

Part numbers (#) are those of `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (copied in chapter 10 §10.5). Station coordinates (Y, mm from the inner face of the front wall) are the values printed by `python3 tools/design_layout.py` (chapter 10 §10.3). The step source (`manual/ASSEMBLY_STEPS_SOURCE.md`, phase B) uses an older part numbering in some rows; the numbers below follow the parts list, and each divergence is noted.

![Figure 67 — F15.6 — Assembly section with fastener balloons: balloon number = part # of the mechanical parts list; defines which fastener goes where in Steps 15.5–15.13, DSN-MECH-07 Rev A — PROPOSED DESIGN (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png; produced by tools/design_enclosure_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-07_assembly_section_fasteners.png)

![Figure 68 — F15.7 — Sheet-metal flat patterns (tray, front plate, lid) that the fabricator folds before Step 15.5; bend lines and allowance per the generator formula, DSN-MECH-06 Rev A — PROPOSED DESIGN (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png; produced by tools/design_enclosure_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-06_sheet_metal_flat_patterns.png)

### Step 15.5 — Fit PEM nuts, lid gasket and front gasket to the tray [PROPOSED DESIGN]

- **Purpose:** prepare the folded tray so that every later fastener has a nut and the IP54 sealing surfaces exist before parts block access.
- **Parts & tools:** tray #1 (2.5 mm Al 5754, 3 bends R2.5, 15 mm flanges); PEM nuts S-M4-1 ×18 (parts list #1 and fastener totals); lid gasket #7 (EPDM 3 mm self-adhesive, 15 mm wide, on the three top flanges); front-flange gasket: 1.5 mm EPDM strip on the two front flanges (parts list "Sealing and finish", no part number); PEM press tool.
- **Action:** press the 18 PEM nuts into the lid and front-plate flange holes (8 lid holes M4 + 10 front-plate holes M4, parts list #1 note); lay the lid gasket on the three top flanges and the front strip on the two front flanges, continuous around the corners.
- **Check:** gasket continuous, no gaps at corners; every flange hole has a nut; the Ø70 cable-entry hole and intake slots are free.
- **Figure:** F15.6, F15.7.
- **⚠ Decision:** the step source quotes "PEM S-M4 ×38" (source: `manual/ASSEMBLY_STEPS_SOURCE.md` B1) whereas the parts list and its fastener totals give S-M4-1 ×18; the parts list count is used here (observation MAN-15-1). Bend reliefs and corner welds of the tray are listed as open in the parts list.

### Step 15.6 — Mount the PA heat-spreader brackets and the plate [PROPOSED DESIGN]

- **Purpose:** fix the 300 × 300 × 10 mm plate (#8) vertically at the front of the tray so that its front face is at station Y = 11.0 mm (plate front) and its rear face at Y = 21.0 mm.
- **Parts & tools:** plate #8 (Al 6061, fin fields machined, M3 tapped 16×7 + 6); brackets #9, #10, #11, #12 (L 25×25×3 Al at x = 5/280, z = 20/265); per bracket M5×12 ×2 + M5×16 ×1 (totals M5×12 ×12 incl. the stepper, M5×16 ×4); square, 5 mm hex key.
- **Action:** bolt each bracket to the side wall and to the front flange (parts list note), then bolt the plate to the four brackets; set the plate front face at Y = 11.0 mm from the inner face of the front wall (source: `tools/design_layout.py`, `stations_y.plate_front`).
- **Check:** plate square to the base ±0.5 mm (source: step source B2); front face flush for the antenna spacers; the fin fields face the rear (towards the Main Board tier).
- **Figure:** F15.6, F10.1, F10.3.
- **⚠ Decision:** D-08/D-11 (chassis material and spreader concept); step source names "brackets #10" — the parts list has four brackets #9–#12.

### Step 15.7 — Mount the 16 PA boards on the rear of the plate [PROPOSED DESIGN]

- **Purpose:** put every QPA2962 on the plate through a thermal pad so that the conduction path of the thermal design (chapter 10 §10.7) exists.
- **Parts & tools:** 16 assembled RF PA boards (Step 15.2); thermal pads 5 × 5 mm, one under each QPA2962 (parts list #8 note); M3×6 ×112 (parts list #8: "PA 112"); torque screwdriver.
- **Action:** place the boards on the tapped field in the 4 × 4 grid of the layout (pitch x 40.0 mm, z 68.0 mm; field origin x 77.5, z 23.0; source: `tools/design_layout.py` `pa_grid`, `pa_field`) with the pad centred on the QPA2962; fasten with 7 × M3×6 per board through the Ø3.20 holes at (2.6, 2.6), (17.5, 2.6), (32.4, 2.6), (2.6, 38), (32.4, 38), (2.6, 57.4), (32.4, 57.4) (source: `engineering/MECHANICAL/dimensions/RF_PA_dimensions.md` §2); number the boards PA1…PA16 as drawn on DSN-MECH-04 tier 1.
- **Check:** torque 0.5 N·m (step source B3 — ASSUMED, no repository torque specification); pads centred; numbering PA1…PA16 matches F15.8 tier 1.
- **Figure:** F15.8 (tier 1), F15.5.
- **⚠ Decision:** the QPA2962 is assumed at the board centre in the thermal model ("verify in `engineering/PCB/RF_PA`", `DESIGN_CALCULATIONS.md` §1) — confirm the pad position on the real board before fastening.

### Step 15.8 — Mount the antenna panel on the plate front [PROPOSED DESIGN, D-01…D-06]

- **Purpose:** fix the proposed 16-row patch panel at station Y = 8.0 mm, 2.4 mm in front of the plate, with its row-1 connector at the bottom.
- **Parts & tools:** antenna PCB DSN-ANT-01 (165.0 × 248.0 × 0.6 mm, position x 72.5, z 31.0; source: `tools/design_layout.py` `antenna`); 6 × 2.4 mm nylon spacers (parts list #8 note; spacer material listed as open); M3×6 ×6 (parts list #8: "antenna 6").
- **Action:** stand the panel on the six spacers over the plate's six antenna tap holes; fasten; keep the 16 end-launch 2.92 mm connectors on the left edge accessible (D-05).
- **Check:** row 1 at the bottom; connectors accessible; gap to plate 2.4 mm; radome gap 8.0 mm remains in front (layout `antenna.radome_gap`).
- **Figure:** F10.2 (front elevation), F8.1 (chapter 8).
- **⚠ Decision:** D-01 (patch array vs slotted waveguide) is an owner decision; the panel is PROPOSED and only simulated (AC-E7 NOT RUN).

### Step 15.9 — Fit the Main Board tier (Y = 56.0 mm) [PROPOSED DESIGN, D-07, D-09]

- **Purpose:** carry the Main Board vertically, components to the rear, with its SMA field reachable for the Synth coax (D-09).
- **Parts & tools:** carrier rails #13 (bottom) and #14 (top), U15×12×1.5 Al, 280 mm, M4×8 ×2 each to the side walls; standoffs #15–#22 (M3×10 hex) at the eight Ø3.20 holes (4, 4), (256, 4), (116, 114), (256, 114), (116, 250), (256, 250), (4, 296), (256, 296) (source: `MAIN_BOARD_dimensions.md` §2) with M3×6 ×1 each; assembled Main Board (Step 15.2).
- **Action:** bolt the rails to the side walls at station Y = 56.0 mm (`stations_y.main`); screw the eight standoffs into the rails; mount the board at (x 25.0, z 5.0) (`main_pos`) component side to the rear.
- **Check:** connector field positions match DSN-MECH-04 tier 2 (J1, J18…J55 on the rear face; X_n Molex, JP and SV1 reachable); board does not touch the PA boards (component heights ASSUMED 15 mm top / 4 mm bottom — G-02).
- **Figure:** F15.8 (tier 2), F15.2.
- **⚠ Decision:** D-07 — the 25 mm tier pitch is an assumption until component heights are measured (G-02).

### Step 15.10 — Fit the Synth tier (Y = 81.0 mm) and the Power tier (Y = 106.0 mm) [PROPOSED DESIGN]

- **Purpose:** complete the board stack behind the Main Board.
- **Parts & tools:** Synth rails #23/#24 (120 mm, M4×8 ×2 each), standoffs #25–#28 at (5, 5), (95, 5), (5, 95), (95, 95) (source: `FREQUENCY_SYNTHESIZER_dimensions.md` §2), M3×6 ×4; Power rails #29/#30 (300 mm, M4×8 ×2 each), standoffs #31–#38 at (10, 10), (140, 10), (270, 10), (10, 120), (270, 120), (10, 230), (270, 230), (138, 268) (source: `POWER_SUPPLY_dimensions.md` §2, rounded as in the parts list), M3×6 ×8; assembled boards.
- **Action:** mount as in Step 15.9: Synth at station Y = 81.0 (`stations_y.synth`), position (x 46.36, z 141.60) — "centred on Main Board J1,J18,J20,J21,J22,J23 (P&P)" (`synth_pos.basis`); Power Board at Y = 106.0 (`stations_y.power`), position (x 15.0, z 5.0).
- **Check:** Synth J-ports face the Main Board SMA field (shortest coax, D-09); Power Board X1 input and X2…X35 outputs reachable from the rear; rear inner wall at Y = 127.6 leaves clearance for the Power Board components (ASSUMED heights).
- **Figure:** F15.8 (tiers 3–4), F15.3, F15.4.
- **⚠ Decision:** G-10 (Power Board outline), G-02 (heights).

### Step 15.11 — Mount the 22 V PA supply / gate module on the rear wall [PROPOSED DESIGN — module not built]

- **Purpose:** provide the 22 V drain source, the high-side switch driven by `EN/DIS_RFPA_VDD` and the per-PA pulse-gating FETs (D-14).
- **Parts & tools:** DSN-PSU-01 module (block schematic, BOM and netlist only: `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/`; component-level capture is recovery item MDR-12); fasteners not defined.
- **Action:** fix the module to the rear wall between the Power Board tier and the rear inner wall (DSN-MECH-01 shows the location); route its 16 outputs OUT1…OUT16 towards the PA field (cables CBL-050, -056, -062, -068, -074, -080, -086, -092, -098, -104, -110, -116, -122, -128, -134, -140 in Step 15.17).
- **Check:** none possible — the module does not exist.
- **Figure:** F10.1, F9.1 (chapter 9).
- **⚠ Decision:** ⚠ D-14 — module not built; the `TX_GATE` FPGA/MCU pin is undecided; ⚠ K4 — no 22 V rail in any CAD file.

### Step 15.12 — Fit the fans and the gland plate [PROPOSED DESIGN — fans not in the parts list]

- **Purpose:** establish the bottom-to-top forced airflow of the cooling concept (D-11) and seal the cable entry.
- **Parts & tools:** 2 × 60 mm fans (step source B8; **no fan part, bracket or airflow figure exists in the parts list** — "fan mounting brackets" is an open item there); gland plate #39 (100 × 100 × 2 Al) with M4×8 ×4 and IP68 glands M32 (power) + M20 (USB).
- **Action:** fit the fans at the duct intakes shown on DSN-MECH-01/03; bolt the gland plate under the base over the Ø70 entry hole.
- **Check:** airflow direction bottom → top (intake louvres in the front plate, exhaust slots in the lid — parts list #2, #6); glands tightened on the harness only after Step 15.18.
- **Figure:** F10.1, F10.3.
- **⚠ Decision:** G-08 — fan selection and airflow are not designed; the thermal map assumes an effective h over the fin strips (chapter 10 §10.7).

### Step 15.13 — Fit the front plate, PTFE window, gasket and clamp frame [PROPOSED DESIGN]

- **Purpose:** close the front with the radome window in front of the antenna (radome gap 8.0 mm).
- **Parts & tools:** front plate #2 (window opening 175 × 258, intake louvres, 16 M3 clamp holes) with M4×8 ×10 to the tray front flanges (into the PEM nuts of Step 15.5); window #3 (PTFE 2 mm, outside the front plate); window gasket #4 (EPDM 1.5 mm, 10 mm ring); clamp frame #5 (2 mm Al, 14 mm wide) with M3×10 ×16 + nyloc.
- **Action:** bolt the front plate; lay the gasket, the window and the frame outside the plate; fasten the 16 M3×10 with nyloc nuts evenly in a cross pattern.
- **Check:** window flat; gasket compressed evenly; louvres unobstructed.
- **Figure:** F15.6, F10.2.
- **⚠ Decision:** observation MAN-10-1 (16 vs 18 clamp screws in the parts-list text); step source B9 numbers the parts "#2, #5, #6, #7" (older numbering) — the parts-list numbers #2, #3, #4, #5 apply. PTFE loss "≈ 0.1 dB at 10.5 GHz … to be confirmed" (parts list #3).

The lid (#6, M4×8 ×8, gasket #7) stays off until the bring-up of chapter 16 is complete (Step 16.10 closes it).

## 15.4 Phase C — Harness

Lengths are PROPOSED: "Manhattan distance between connector positions in the head + service allowance (40 mm coax / 60 mm wire), rounded up to 10 mm … cut after a first fit" (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, header). Totals: 144 cables; coax 55; wire 89; ≈ 41.6 m. ⚠ The pin order of every Molex 22-23-20x1 connector is UNVERIFIED because the EAGLE symbols name all pads `S` (source: `interconnection_table.md`, header) — buzz out before mating.

![Figure 69 — F15.8 — Internal layout per tier, rear view, with every connector reference (J, X, JP, SV) at its P&P position — the routing reference for Steps 15.14–15.18, DSN-MECH-04 Rev A — PROPOSED DESIGN; connector positions SOURCE-DERIVED (source: engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-04_internal_layout_rear.png; produced by tools/design_mechanical_drawings.py)](engineering/DESIGN/MECHANICAL/drawings/png/DSN-MECH-04_internal_layout_rear.png)

Harness schedule excerpt — the cables named in this phase (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, rows copied; the full 144-row table is reproduced in Appendix B):

| ID | From | To | Signal | Cable | Length (mm) | Note |
|---|---|---|---|---|---|---|
| CBL-035 | POWER_SUPPLY SV1 | MAIN_BOARD SV1 | enable bus (15 EN + GND) | 20-way 1.27 mm IDC ribbon | 320 |  |
| CBL-002 | POWER_SUPPLY X3 | MAIN_BOARD X55 | +5V5_PA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 780 | rail name matched in both netlists |
| CBL-003 | POWER_SUPPLY X4 | MAIN_BOARD X8 | +1V0_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 310 | rail name matched in both netlists |
| CBL-009 | POWER_SUPPLY X10 | MAIN_BOARD X17 | +1V8_CLOCK | 2-wire 20 AWG, Molex 22-01-2027 both ends | 840 | rail name matched in both netlists |
| CBL-001 | POWER_SUPPLY X2 | ? ? | +5V0_1 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-036 | FREQUENCY_SYNTHESIZER J7 | MAIN_BOARD J1 | 100 MHz FPGA sys clk | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-037 | FREQUENCY_SYNTHESIZER J5 | MAIN_BOARD J20 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 170 | mapping from interconnection_table.md §6 |
| CBL-038 | FREQUENCY_SYNTHESIZER J6 | MAIN_BOARD J18 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-039 | FREQUENCY_SYNTHESIZER J3 | MAIN_BOARD J21 | 400 MHz ADC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-040 | FREQUENCY_SYNTHESIZER J10 | MAIN_BOARD J23 | LO TX | coax RG-405 (0.086") SMA-SMA, phase-stable | 100 | mapping from interconnection_table.md §6 |
| CBL-041 | FREQUENCY_SYNTHESIZER J11 | MAIN_BOARD J22 | LO RX | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-043 | FREQUENCY_SYNTHESIZER JP1 | MAIN_BOARD JP1 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 210 |  |
| CBL-044 | FREQUENCY_SYNTHESIZER JP2 | MAIN_BOARD JP13 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 240 |  |
| CBL-045 | MAIN_BOARD X_7 | RF_PA PA1 X2 | VG_1 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 150 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-046 | MAIN_BOARD X3 | RF_PA PA1 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 150 | Main sense connector ↔ PA n PROPOSED |
| CBL-047 | MAIN_BOARD J27 | RF_PA PA1 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 330 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-048 | MAIN_BOARD J26 | RF_PA PA1 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-049 | RF_PA PA1 J2 | ANTENNA ROW1 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 100 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-050 | DSN-PSU-01 OUT1 | RF_PA PA1 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 510 |  |
| CBL-141 | SLIP RING VIN | POWER_SUPPLY X1 | VIN 12-17 V | 2 × 2-wire 16 AWG | 340 |  |
| CBL-142 | SLIP RING VIN | DSN-PSU-01 IN | VIN to 22 V boost | 2 × 2-wire 16 AWG | 470 |  |
| CBL-143 | SLIP RING USB | MAIN_BOARD X53 | USB 2.0 FS to host | USB 2.0 shielded, mini-B | 360 |  |
| CBL-144 | MAIN_BOARD stepper pins | PEDESTAL TB6600 (via slip ring) | STEP/DIR/EN | 3-wire 24 AWG shielded | TBD | the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head (then only motor phases cross: 4 circuits) — DECISION NEEDED |

### Step 15.14 — Enable bus SV1 ↔ SV1 [SOURCE-DERIVED pinout, PROPOSED cable]

- **Purpose:** connect the 15 enable lines from the STM32 to the Power Board regulators.
- **Parts & tools:** CBL-035, 20-way 1.27 mm IDC ribbon, 320 mm; two MA10-2 IDC connectors.
- **Action:** mate Main SV1 to Power SV1 pin-for-pin (pin map: 1 `EN_+1V0_FPGA` PE7 → U1, 2 `EN_+5V0_PA2` PG1 → U15, 3 `EN_+1V8_FPGA` PE8 → U2, 4 `EN_+5V0_PA3` PG2 → U16, 5 `EN_+3V3_FPGA` PE9 → U4, 6 `EN_+5V5_PA` PG3 → U17, 7 `EN_+5V0_ADAR` PE10 → U13, 8 `EN_+1V8_CLOCK` PG4 → U25, 9 `EN_+3V3_ADAR12` PE11 → U6, 10 `EN_+3V3_CLOCK` PG5 → U23, 11 `EN_+3V3_ADAR34` PE12 → U7, 13 `EN_+3V3_ADTR` PE13 → U32, 15 `EN_+3V3_SW` PE14 → U10, 17 `EN_+3V3_VDD_SW` PE15 → U8, 19 `EN_+5V0_PA1` PG0 → U14; 12/14/16/18/20 GND — source: `power_rails.md` §2).
- **Check:** pin-1 orientation identical at both ends; continuity on all 20 positions.
- **Figure:** F15.8 (SV1 positions on tiers 2 and 4).
- **⚠ Decision:** none (the Power Board has no visible pull-downs on the EN nets — "REQUIRES VERIFICATION", `power_rails.md` §2).

### Step 15.15 — Rail cables Power → Main / Synth [SOURCE-DERIVED mapping, ⚠ pin order UNVERIFIED]

- **Purpose:** bring every supply rail to its consumer board.
- **Parts & tools:** the 2-wire 20 AWG Molex 22-01-2027 cables CBL-002…034 whose rail name "matched in both netlists" (X3→X55, X4→X8, X5→X10, X6→Synth X15, X10→X17, X12→X56, X16→X24, X18→X6, X19→X19, X20→X15, X21→X13, X22→X18, X23→X1, X24→X11, X27→X16, X30→X12, X31→X14, X32→X5, X33→X7, X34→X4, X35→Synth X4 — source: `HARNESS_SCHEDULE.md` rows CBL-002…034), crimp tool, DMM.
- **Action:** buzz out the polarity of each Molex pad pair on both boards against the netlist before crimping (pads are named `S`); crimp and mate.
- **Check:** continuity and polarity per `power_rails.md` §1 (consumer connector column).
- **Figure:** F3.2, F15.8.
- **⚠ Decision:** (a) rails whose destination connector could not be matched by net name — CBL-001, -006, -007, -008, -010, -012, -013, -014, -016, -024, -025, -027, -028 (TBD rows of the harness schedule; interconnection table §2/§4 resolves most of them: e.g. +3V3_ADAR_12 X14 → Main X20 `+3V3_ADAR12`, +3V3_ADAR_34 X15 → Main X21, +3V3_CLOCK X11 → Synth X11, +3V3_LO_1 X8 → Synth X13, +3V3_LO_2 X7 → Synth X14; `+5V0_1…5`, `+5V0_ADAR` X13, `+5V0_ADTR` X26, `+3V3_SW` X29 have **no consumer** and stay unconnected — `power_rails.md` §4 item 4); (b) `+1V8_CLOCK` X10 must feed both Main X17 and Synth X12 — "add a second output or document a Y-cable" (`power_rails.md` §4 item 3).

### Step 15.16 — Synth ↔ Main control headers and coax clocks/LO [SOURCE-DERIVED mapping]

- **Purpose:** deliver the 100 / 120 / 400 MHz clocks and the TX/RX LO to the Main Board and connect the SPI4/control lines.
- **Parts & tools:** CBL-043 (JP1 ↔ JP1, 210 mm), CBL-044 (JP2 ↔ JP13, 240 mm); coax set CBL-036…041 (J7→J1 100 MHz FPGA, J5→J20 and J6→J18 120 MHz DAC, J3→J21 400 MHz ADC, J10→J23 LO TX, J11→J22 LO RX; RG-405 phase-stable, 100–170 mm) and CBL-042 (J4→J19 test, 100 mm); SMA torque wrench.
- **Action:** connect the headers; form and connect the coax; label each cable with its CBL-ID.
- **Check:** SMA torque 0.9 N·m (step source C3 — ASSUMED, no repository torque specification); labels present; no coax below its minimum bend radius.
- **Figure:** F15.8 (tiers 2–3).
- **⚠ Decision:** none beyond the clock-frequency intent being firmware-derived (`main.cpp:933-1072`), to be verified in Step 16.4.

### Step 15.17 — PA harness: VG, sense, RF pairs, antenna coax, 22 V leads [PROPOSED mapping, ⚠ several UNVERIFIED]

- **Purpose:** connect all 16 PA boards to the Main Board, the antenna rows and the 22 V module.
- **Parts & tools:** per PA n: VG cable (Main X_k → PA n X2, 24 AWG shielded, Molex 22-01-2027), sense cable (Main X3/X38…X52 → PA X3, 3-wire 24 AWG twisted, Molex 22-01-3037), RF pair (Main J-pair → PA J1/J2, RG-405 EQUAL LENGTH set), antenna coax (PA J2 → antenna row n, RG-405 SMA–2.92 mm, EQUAL LENGTH set), 22 V lead (DSN-PSU-01 OUTn → PA `22V` AK300/2, 2-wire 18 AWG twisted) — rows CBL-045…140 of the harness schedule. VG_n ↔ Main connector map from the schematic: X_7=VG_1, X_16=VG_2, X_8=VG_3, X_15=VG_4, X_4=VG_5, X_11=VG_6, X_3=VG_7, X_12=VG_8, X_5=VG_9, X_14=VG_10, X_6=VG_11, X_13=VG_12, X_2=VG_13, X_9=VG_14, X_1=VG_15, X_10=VG_16 (source: `interconnection_table.md` §7). RF pairs per n: J27/J26 (1), J29/J28 (2), J25/J24 (3), J31/J30 (4), J35/J34 (5), J37/J36 (6), J33/J32 (7), J39/J38 (8), J47/J46 (9), J41/J40 (10), J45/J44 (11), J43/J42 (12), J55/J54 (13), J49/J48 (14), J53/J52 (15), J51/J50 (16) (same source).
- **Action:** cable PA n to VG_n, sense connector n, RF pair n and antenna row n exactly as labelled; cut the 16 antenna coax and the 16 RF pairs as equal-length sets; connect the 22 V leads **last** and only with VG wiring complete (S1).
- **Check:** equal length within ±2 mm on the 16 antenna coax (step source C4 — ASSUMED tolerance; the harness schedule only states "equal length mandatory for elevation phase"); labels PA1…PA16; 22 V polarity (KL1 `VD`, KL2 `GND`, `interconnection_table.md` §7); screw-terminal torque of the AK300/2 per its datasheet (not in the repository).
- **Figure:** F15.8 (tier 1 PA numbering, tier 2 SMA field), F15.5.
- **⚠ Decision:** which SMA of each Main Board pair is RFIN vs RFOUT is UNVERIFIED — "determine from the Main Board switch RF_SW_n routing before cabling" (`ASSEMBLY_SEQUENCE.md` §B.7); PA-instance ↔ VG_n / sense-connector mapping is PROPOSED (n = n), not documented in CAD; ⚠ K4 / D-14 for the 22 V leads.

### Step 15.18 — Slip-ring harness through the base gland [PROPOSED DESIGN, D-13]

- **Purpose:** bring VIN, 22 V-boost input and USB from the pedestal into the rotating head.
- **Parts & tools:** CBL-141 (slip ring VIN → Power X1, 2 × 2-wire 16 AWG, 340 mm), CBL-142 (slip ring VIN → DSN-PSU-01 IN, 470 mm), CBL-143 (slip ring USB → Main X53 mini-B, 360 mm); gland plate #39 glands M32 (power) and M20 (USB).
- **Action:** route the three cables through the Ø70 base hole and the glands; tighten the glands.
- **Check:** continuity after a full 360° rotation of the turntable (Step 15.22); no cable strain.
- **Figure:** F10.3, F10.5.
- **⚠ Decision:** CBL-144 (STEP/DIR/EN to the TB6600) — "the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head … DECISION NEEDED" (harness schedule); D-13 channel count (12) assumes USB stays the host link.

## 15.5 Phase D — Pedestal

### Step 15.19 — Slewing bearing, turntable and ring pulley [PROPOSED DESIGN]

- **Purpose:** build the rotating joint.
- **Parts & tools:** pedestal top plate #43 (360 × 360 × 5 Al, bore Ø90) with M6×20 ×12 to the bearing inner ring; slewing bearing #41 (OD 190 / ID 100 × 20, "part number to be selected (axial ≥ 50 kg, moment ≥ 60 N·m)"); turntable #40 (Ø340 × 8 Al) with M6×25 ×12 to the bearing outer ring; ring pulley #42 (GT3 180 T Ø172) with M4×10 ×6 clamped under the turntable; pedestal housing #44 with M5×10 ×12 to the top plate.
- **Action:** bolt the bearing inner ring to the top plate (12 × M6×20), the turntable to the outer ring (12 × M6×25), the ring pulley under the turntable (6 × M4×10); fit the top plate on the housing (12 × M5×10).
- **Check:** turntable runs freely; axial play < 0.1 mm (step source D1 — ASSUMED acceptance value).
- **Figure:** F10.5, F10.3.
- **⚠ Decision:** bearing part number not selected (parts list #41 note).

### Step 15.20 — Stepper, bracket, pulley, belt and driver [PROPOSED DESIGN, ⚠ D-12 revised]

- **Purpose:** install the azimuth drive.
- **Parts & tools:** stepper #45 (NEMA 23, 76 mm, M5×12 ×4); motor bracket #46 (80 × 80 × 3 Al, slots ±5 mm, M5×10 ×4 to the top plate); motor pulley #47 (GT3 60 T Ø57, bore 6.35, grub M4 ×2); belt GT3 9 mm (ratio 3, `design_layout.py` `pedestal`); driver #50 (TB6600 on DIN rail).
- **Action:** bolt the bracket, mount the motor and pulley, fit the belt and tension it with the bracket slots; mount the driver; set the driver current limit before any motion (S3).
- **Check:** belt deflection within the belt maker's figure (not in the repository); driver current limit set and recorded.
- **Figure:** F10.5.
- **⚠ Decision:** ⚠ D-12 — DSN-CALC-01 §2 shows a NEMA 23 needs ≥ 200 ms per 7.2° step (≈ 19 s per revolution) for the ≈ 10 kg head; a NEMA 34 (3 N·m class) allows ≈ 100 ms; alternatives 1:6 ratio (`Stepper_steps = 1200`) or a lighter head. The firmware constant must match the ratio (`Stepper_steps = 600` for 1:3, `main.cpp:195`). Choose motor class and ratio **before** this step.

### Step 15.21 — Slip ring, stator bracket, mast flange [PROPOSED DESIGN, ⚠ mast interface undefined]

- **Purpose:** fix the slip-ring stator to the pedestal with its rotor turning with the turntable; prepare the mast interface.
- **Parts & tools:** slip ring #48 (through-bore Ø99 × 60, bore 60, 12 circuits, "e.g. Senring H3899 class — select"); stator bracket #49 (140 × 140 × 3 Al, M4×8 ×4); mast flange #51 (Ø150 × 10 steel, 4 × M10 PCD 110, M10×30 ×4 — "ASSUMPTION — mast interface undefined").
- **Action:** mount the stator bracket under the top plate, the slip ring in the bore, the rotor flange to the turntable; route the harness of Step 15.18 through the bore; bolt the mast flange under the housing.
- **Check:** rotor turns with the turntable without cable strain over 360°.
- **Figure:** F10.5, F10.3.
- **⚠ Decision:** slip-ring part not selected; mast flange is an ASSUMPTION (parts list #51; `design_layout.py` `mast_flange`); D-13 channel count.

### Step 15.22 — Bolt the head to the turntable [PROPOSED DESIGN]

- **Purpose:** join the head and the pedestal with the cable passage aligned.
- **Parts & tools:** M6×16 ×8 (parts list #40: "8×M6 to the head base"); head assembly of phase B; harness of Step 15.18 already through the Ø70 base hole.
- **Action:** align the Ø70 base passage with the slip-ring bore and bolt the tray base to the turntable with the 8 × M6×16.
- **Check:** head square to the turntable (no tolerance in the source); harness continuity after a 360° rotation (Step 15.18 check); lid still open for chapter 16.
- **Figure:** F10.3, F10.8a.
- **⚠ Decision:** lifting points and earthing stud are open items (parts list "Open").

## 15.6 Hand-over to bring-up

Phases A–D leave the head open (lid #6 off), the pedestal stationary, the 22 V leads connected only if the DSN-PSU-01 module exists, and every cable labelled with its CBL-ID. Chapter 16 continues with Step 16.1 (firmware flash). Evidence to collect during the first build (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §D): rail voltages (CP-4), photos of the first harness with cable labels, the measured component heights (closes G-02), the measured board thickness (G-01) and the real cut lengths of all 144 cables (replaces the PROPOSED lengths) — store under `engineering/VALIDATION/`.


---

<!-- chapter 16: Power-up, firmware flashing, FPGA programming, calibration (ADC taps, beam), bench tests, acceptance criteria -->
# Bring-up and test — power-up, flashing, FPGA programming, calibration, bench tests, acceptance

**Author of this chapter:** Antidrone Ukraine · antidrone.cc.

**Status summary:** every procedure in this chapter is **PROPOSED / BETA — never executed on hardware** (source: `manual/ASSEMBLY_STEPS_SOURCE.md`, header; `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md`, "Nothing in this sequence has been executed on hardware"). The test plan and acceptance tables are copied from `docs/TESTING/`; a test is reported PASSED only where the source records an executed run, and physical tests are NOT RUN everywhere. The FPGA bitstream does not exist (no Vivado on the authoring machine), so Steps 16.3 and 16.5–16.9 cannot be started today.

**Sources:** `manual/ASSEMBLY_STEPS_SOURCE.md` (phase E), `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §B/§D, `docs/TESTING/VALIDATION_PLAN.md`, `docs/TESTING/ACCEPTANCE_CRITERIA.md` (sections A–H), `beta/fpga/README.md` (calibration registers, Vivado scripts), `beta/gui/README.md` and `beta/gui/aeris10_gui/protocol/register_map.py` (register panel), `beta/stm32/README.md` §7, `engineering/ELECTRICAL/power_distribution/power_rails.md` §3, `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §1–§2.

**Figures in this chapter:** none mandatory (tables); the register map is in chapter 13 §13.6, the enable sequence in chapter 12 §12.6.

## 16.0 Safety and preconditions

The safety preamble of chapter 15 §15.0 applies (S1 22 V drain, S2 RF, S3 pedestal, S4 ESD). Preconditions: phases A–D of chapter 15 complete with the lid off and the pedestal stationary; bench PSU 12–17 V with current limit; the 22 V leads disconnected until Step 16.6; a 50 Ω dummy load or anechoic setup for Step 16.9; instruments listed per step. Three decisions gate the chapter: ⚠ **K1** (FPGA part XC7A50T on the schematic vs XC7A100T in the FPGA README — `tools/vivado/create_project.tcl` header), ⚠ **K2** (HSE 8 MHz assumed by the beta firmware, D-01), ⚠ **K4** (22 V PA supply not in CAD).

## 16.1 Phase E — bench bring-up steps

### Step 16.1 — Flash the STM32 beta image via SWD [BETA image, ⚠ K2]

- **Purpose:** load `aeris10_fw.elf` and prove the clock tree and CDC enumeration.
- **Parts & tools:** ST-LINK on SWD (PA13 SWDIO / PA14 SWCLK; SWO PB3 — `beta/stm32/CUBEMX_SETTINGS.md` §3); `beta/stm32/build_out/aeris10_fw.elf` (build of Step 12.3); USART3 terminal 115200 8N1 (PB10/PB11); host PC.
- **Action:** `STM32_Programmer_CLI -c port=SWD -w beta/stm32/build_out/aeris10_fw.elf -v -rst` (source: `beta/stm32/README.md` §7 item 2).
- **Check:** USART3 banner appears (SWO/USART3 output at 115200 "proves the clock" — same source); the host enumerates a CDC ACM device with the placeholder VID/PID 0x0483:0x5740 (D-09). Note the 180 s OCXO wait at boot (`HAL_Delay(180000)`, F0 in `power_rails.md` §3) before any rail is enabled.
- **Figure:** F12.2.
- **⚠ Decision:** K2 — if the board's crystal is not 8 MHz the PLL constants of D-01 are wrong and `HAL_RCC_OscConfig` fails into `Error_Handler()`; verify XTAL1 on the assembled board first.

### Step 16.2 — Observe the power-enable sequence F0–F10 on a scope [SOURCE-DERIVED order, BETA delays]

- **Purpose:** confirm that the rails appear in the coded order with the coded delays (chapter 12 §12.6) and that the D-11 additions (`+5V5_PA` before VG, VD last off) are present.
- **Parts & tools:** oscilloscope ≥ 4 channels; probe points at the Power Board outputs X2…X35 and at SV1 pins 1…19.
- **Action:** capture from reset: F1 `EN_+1V8_CLOCK` (SV1-8) → F2 `EN_+3V3_CLOCK` (SV1-10) → F3/F4/F5 FPGA rails (SV1-1/3/5) → F6 ADAR 3.3 V (SV1-9/11) → F7 `EN_+5V0_ADAR` (SV1-7) → F8 `EN_+3V3_VDD_SW` (SV1-17) → F9 `EN_+3V3_SW` (SV1-15) → `EN_+5V5_PA` (SV1-6, D-11 addition) → F10 VG DAC update then `EN/DIS_RFPA_VDD` (PD6 → JP10).
- **Check:** order matches `power_rails.md` §3; delays 100 ms (F1–F5), 500 ms (F6, F7), 2 ms (F8, F9), 100 ms `+5V5_PA` → DAC, 20 ms VG → VD (D-11); the xlsx rules "1.8 V before 3.3 V for the AD9523" and "AVDD3 before AVDD1 for the ADAR1000" are respected (F1→F2, F6→F7). Record the captures (AC-S7).
- **Figure:** F3.2, chapter 12 §12.6 tables.
- **⚠ Decision:** whether `systemPowerUpSequence()` reaches F8/F9 via `initializeADTR1107Sequence()` is UNVERIFIED (`power_rails.md` §3 row F8); the actual assertion of `EN_+3V3_ADTR` / `EN_+5V0_PA1..3` settles observation MAN-12-1.

### Step 16.3 — Program the FPGA via JP3 JTAG [BLOCKED — no bitstream; ⚠ K1]

- **Purpose:** load the radar RTL and prove the STM32 ↔ FPGA handshake.
- **Parts & tools:** Xilinx platform cable on Main Board JP3 (JTAG); Vivado with `beta/fpga/vivado/create_project.tcl` + `vivado/build.tcl` (NOT executed — `beta/fpga/README.md`); the two FFT IP cores per `beta/fpga/ip/README.md` (not generated).
- **Action:** when a bitstream exists: `vivado -mode batch -source tools/vivado/create_project.tcl -tclargs xc7a50tftg256-2` (part must be passed explicitly — `tools/vivado/create_project.tcl` header), then `build.tcl`, then program via Hardware Manager.
- **Check:** DONE pin high; STM32 ↔ FPGA handshake DIG_0..4 (PD8..PD12: new chirp, new elevation, new azimuth, mixers enable, FPGA reset — `CUBEMX_SETTINGS.md` §6) toggles.
- **Figure:** F11.1 (chapter 11).
- **⚠ Decision:** ⚠ K1 part number; the beta constraints leave 116 port bits unconstrained ("`write_bitstream` will refuse the unconstrained I/O unless they are removed from the top or `UNCONSTRAINEDPINS ALLOW` is set" — `beta/fpga/README.md`, "Constraints"); bank-14 LVDS termination (DIFF_TERM FALSE, external 100 Ω — option A, REQUIRES VERIFICATION).

### Step 16.4 — AD9523 lock and output frequencies [SOURCE-DERIVED intent]

- **Purpose:** verify the clock distribution before any sampling or DAC test.
- **Parts & tools:** frequency counter (± 1 ppm or better); coax set CBL-036…041 in place (Step 15.16).
- **Action:** read the AD9523 status pins (PF8/PF9 `AD9523_STATUS0/1`) and measure Synth J7 (100 MHz FPGA), J5/J6 (120 MHz DAC), J3 (400 MHz ADC) at the Main Board ends.
- **Check:** 100 / 120 / 400 MHz ± 1 ppm (acceptance from `ASSEMBLY_SEQUENCE.md` §B.4; "firmware intent `main.cpp:933-1072`"; register table verified on the host against the driver's encoding, "**not on silicon**" — `beta/stm32/DECISIONS.md` D-12).
- **Figure:** F2.1 (chapter 2).
- **⚠ Decision:** the beta ADC capture (mode 1) requires BUFR (DCO/4) and `clk_100m` (AD9523 OUT6) to be frequency-locked — "if the two clocks are not frequency-locked the design needs a re-sampler (not present)" (`beta/fpga/README.md`, "Remaining risks").

### Step 16.5 — ADC capture calibration (IDELAY taps) [BETA register procedure; ⚠ ADC SPI unwired]

- **Purpose:** centre each of the 8 LVDS lanes of the AD9484 in its valid window and align the lane rotation (the `adc_capture_calib` module of the beta RTL, `ADC_CAPTURE_MODE = 1`).
- **Parts & tools:** GUI register panel (chapter 13 §13.6) over CDC `REG` commands (firmware D-17) **or** any host that can issue the SPI bridge commands 0x02/0x03; the AD9484 test-pattern registers (datasheet: register 0x0D = 0x48 user pattern, P1/P2 = 0x19..0x1C = pattern A/B; or 0x04 checkerboard / 0x07 toggle — `beta/fpga/README.md`, "ADC capture and DDC front end"); logic analyser optional.
- **Action — auto (pattern) method:** (1) put the ADC in the 2-code test pattern matching `CAL_PATT` (reset 0x55AA: pattern_a 0xAA, pattern_b 0x55); (2) `REG W 0x4 0x1` (CAL_CTRL `auto_start`, write-1-to-toggle); (3) poll `REG R 0x9` (CAL_STAT) until `busy` = 0 and `done` = 1; (4) for lane = 0…7: `REG W 0x5 <lane>`, `REG R 0xA` (CAL_LANE_INFO: chosen `tap`, `win_lo`, `win_hi`) — the panel's "Read all / refresh" does this loop and restores CAL_LANE; (5) `REG R 0xC` (CAL_UNDET); (6) with the pattern still applied set `check_en` (`REG W 0x4 0x8`) and read `REG R 0xB` (CAL_ERR) after a few seconds; (7) switch the ADC to normal data, clear `check_en`.
- **Action — manual method (fallback):** `REG W 0x5 <lane>`, `REG W 0x6 <tap>` (CAL_TAP 0..31, 78 ps each, reset 16), `REG W 0x4 0x2` (`manual_load`); for a lane rotation `REG W 0x7 <n>` (CAL_SLIP 0..3) then `REG W 0x4 0x4` (`bitslip_load`).
- **Check:** CAL_STAT `lock[7:0]` = 0xFF, `align_fail` = 0, `fifo_ovf` (bit 15) = 0; per-lane pass windows "should be ~27 of 32 taps wide at 400 MSPS"; CAL_ERR stays 0 with the pattern applied and `check_en` set; `CAL_ERR` stays 0 in normal data with the pattern check off (source: `beta/fpga/README.md`, "Remaining risks / what to check in Vivado (mode 1)"). Simulation reference: testbench `tb_adc_iserdes_capture` — "8/8 lanes locked, centre tap 12 (skewed lane 5 … compensated), bitslip detected/realigned, 4000 samples exact" (same README, table row 6g).
- **Figure:** chapter 13 §13.6 register table; F2.2.
- **⚠ Decision:** (a) the ADC test pattern needs the AD9484 SPI, which the step source marks "⚠ SPI unwired" (`manual/ASSEMBLY_STEPS_SOURCE.md` E5) — if no SPI path to the ADC exists only the manual method and the blind method remain; (b) the **blind method** (`adc_capture_calib.v` `ctrl_blind`, registers 0x0D/0x0E/0x10 CAL_BLIND_*) is in the RTL but "no register in `radar_control_regs.v` drives it" from the GUI's 4-bit map — the panel shows it as unavailable (`beta/gui/CHANGELOG.md` "Discrepancies" 2); (c) on the current top level `reg_we/reg_addr/reg_wdata` of `ctl_regs` are tied to constants (`radar_system_top.v:321-323`) and the bridge RTL does not implement 0x02..0x04 — **register writes cannot reach the FPGA until that RTL work is done**; (d) ISERDES Q1..Q4 bit order "UNVERIFIED against UG471 … run the ADC PN9 pattern (0x0D = 0x06) and compare against a PN9 generator before trusting the data" (`beta/fpga/README.md`).

### Step 16.6 — PA bias-up, one board at a time [SOURCE-DERIVED sequence, PROPOSED thermal limit; ⚠ K4, D-14]

- **Purpose:** bring each QPA2962 to its quiescent point safely and confirm the thermal design case.
- **Parts & tools:** 22 V source with current limit (xlsx: ID limit 2840 mA — `power_rails.md` §1 row `+22V0`/`VD`); GUI status tab (INA241 `PA_AvgCurrent` field of the status string); thermocouple on the heat-spreader plate; the DSN-PSU-01 module if built.
- **Action:** per board n: VG −4 V (firmware sets −3.98 V = DAC code 126, `main.cpp:1583`) → VD 22 V (`EN/DIS_RFPA_VDD`) → raise VG until IDQ 1.68 A (IDQ servo `main.cpp:1628-1656`) → only then RF (xlsx L58-L62 as quoted in `power_rails.md`).
- **Check:** IDQ within ±10 % of 1.68 A (step source E6 — ASSUMED tolerance); plate temperature < 70 °C after 10 min **with drain gating** (design case B: plate max 64.3 °C, PA base ≈ 73 °C at 45 °C ambient — `DESIGN_CALCULATIONS.md` §1); never run continuous bias on all 16 boards (case A: plate > 213 °C).
- **Figure:** F10.9a/b.
- **⚠ Decision:** ⚠ K4 (no 22 V source in CAD), ⚠ D-14 (drain gating not implemented — without it only short single-board tests are thermally admissible), ADAR1000/ADTR1107 LNA/PA rails per MAN-12-1.

### Step 16.7 — Host link [BETA]

- **Purpose:** prove the GUI ↔ firmware ↔ FPGA stream.
- **Parts & tools:** host PC with the `beta/gui` venv (chapter 13); USB cable to X53 (through the slip ring once Step 15.18 is done).
- **Action:** first `python -m aeris10_gui --selftest` on the host (no hardware); then `python -m aeris10_gui --port <CDC port>` and press Start: the GUI sends the start flag and the 82-byte settings packet, then expects status strings and, with the FPGA bridge running, bridge frames.
- **Check:** `--selftest` exit 0 (executed 2026-10-09, chapter 13 Step 13.2); with hardware: status strings parsed, bridge frames arrive with `seq` incrementing and `crc_errors` 0 in the GUI status bar; `REG R 0xF` returns 0xBE7A.
- **Figure:** F13.3.
- **⚠ Decision:** AC-S6 (CDC enumerates; start flag + settings accepted; status received) NOT RUN; the settings packet has no acknowledgement (`beta/gui/README.md` assumption 7) — confirmation is only indirect via the status string.

### Step 16.8 — Beam steering [BETA tables, ⚠ no hardware verification]

- **Purpose:** verify that the firmware writes the ADAR1000 phase tables for the 31 elevation positions.
- **Parts & tools:** logic analyser on the 1.8 V side of the FPGA level shifters (ADAR1000 SPI1: SCLK/MOSI/MISO + CS PA0..PA3 → FPGA pass-through); optionally a VNA/phase measurement on one row.
- **Action:** step the beam position (firmware sequence); capture the SPI traffic.
- **Check:** CS toggles per device (D-05); SCLK 6.75 MHz (D-06); phase words follow `degreesTo7BitPhase` → data-sheet Tables 10-13 → CHx_RX/TX_PHASE_I/Q with register offset `((channel - 1) & 3)` (C10 fix); "data-sheet tables realise the nominal phase within ~3°; array calibration needed" (`beta/stm32/README.md` §7 item 3).
- **Figure:** —
- **⚠ Decision:** ADAR1000 SCLK maximum and level-shifter bandwidth at 6.75 MHz "REQUIRES DATASHEET / BOARD VERIFICATION" (D-06); the SPI pass-through adds one `clk_100m` cycle to SCLK/MOSI/CS and two to MISO (`beta/fpga/README.md`, "Known limitations").

### Step 16.9 — First RF test into a dummy load, then antenna [PROPOSED]

- **Purpose:** confirm the transmit waveform at 10.5 GHz before radiating.
- **Parts & tools:** 50 Ω high-power load or anechoic setup (S2); spectrum analyser / fast power detector; the PA chain of Step 16.6.
- **Action:** transmit the long-chirp set into the load; observe the spectrum around 10.5 GHz and the pulse envelope.
- **Check:** carrier at 10.5 GHz; pulse envelope 30 µs (long chirp, PRI 167 µs; `main.cpp:180-186` as quoted in `engineering/DESIGN/00_DESIGN_BASIS.md` §1); chirp bandwidth B is **TBD** in the parameter table (`DESIGN_CALCULATIONS.md` §3 assumes 50 MHz) — record what is measured.
- **Figure:** —
- **⚠ Decision:** D-01 antenna variant; the chirp direction at baseband decides `CONJUGATE_REF` in the FPGA matched filter (`beta/fpga/README.md`, note 1).

### Step 16.10 — Close the lid; pedestal rotation test [PROPOSED, ⚠ D-12]

- **Purpose:** complete the head and verify the azimuth scan timing.
- **Parts & tools:** lid #6 with gasket #7 and M4×8 ×8 (parts list); stopwatch / log of the firmware azimuth counter.
- **Action:** fit the lid (pitch 60 mm, gasket compressed to 2 mm — parts list "Sealing"); run 50 azimuth positions; log the scan time.
- **Check:** ≈ 19 s per revolution with the NEMA 23 at 200 ms per step (DSN-CALC-01 §2: 18.8 s for 50 × (175 ms dwell + 200 ms move)); harness continuity through the slip ring maintained over 360°.
- **Figure:** F10.5.
- **⚠ Decision:** D-12 motor class / ratio and the matching `Stepper_steps` constant (600 for 1:3, 1200 for 1:6); CBL-144 driver location.

## 16.2 Validation plan (software-based design checks and physical tests)

Copied from `docs/TESTING/VALIDATION_PLAN.md` (status date 2026-10-08 unless a later executed result is noted; the authoring machine had iverilog 13.0 and Verilator 5.052 but **no Vivado, no EAGLE**; the Arm GCC and KiCad used later by the beta trees are recorded in `beta/*/README.md`). "A test is reported PASSED only if it was executed and succeeded. 'Software-based design check' means a file/tool check; 'physical verification' needs hardware and is never claimed here." Run everything runnable with `bash tools/run_all_checks.sh` (exit code = number of failed checks).

### FPGA (section 1)

| ID | Test | Type | Command | Result on the original tree (2026-10-08) | BETA tree result (`beta/fpga/README.md`, 2026-10-09) |
|---|---|---|---|---|---|
| F-01 | Syntax / parse of all RTL | design check | `tools/fpga_lint.sh` (iverilog -g2012) | **FAIL** — `radar_system_top.v:312` syntax error | PASS (iverilog, both views) |
| F-02 | Elaboration of `radar_system_top` | design check | same | **FAIL** — 6 missing modules on a patched copy | PASS |
| F-03 | Lint | design check | `verilator --lint-only -Wall` | **FAIL** — 207 warnings incl. MULTIDRIVEN ×4, UNDRIVEN ×14 (with stubs) | PASS, 0 %Error, 165/159 %Warning (synth/sim view) |
| F-04 | Constraint completeness | design check | `python3 tools/check_fpga_constraints.py` | **FAIL** (exit 1) — 142 placeholder lines, 180/180 bits without PACKAGE_PIN | beta XDC: 0 placeholders, 67/183 port bits constrained (116 UNRESOLVED) |
| F-05 | Schematic-derived pin map generation | design check | `python3 tools/gen_xdc_from_schematic.py` | PASSED (exit 0) — 64 ports mapped, 25 unresolved (generation step, not a correctness proof) | used verbatim in the beta XDC |
| F-06 | Simulation `radar_system_tb` | design check | Vivado xsim (SVA needed) | NOT RUN | 9 open-source testbench runs PASS (`build.sh`: 0 failures) |
| F-07 | Synthesis utilisation on `xc7a50tftg256-2` | design check | `tools/vivado/create_project.tcl` + `launch_runs synth_1` | NOT RUN | NOT RUN |
| F-08 | Timing summary / clock interaction / CDC report | design check | `report_timing_summary`, `report_cdc` | NOT RUN | NOT RUN |
| F-09 | Bitstream generation | design check | `write_bitstream` | NOT RUN | NOT RUN |
| F-10 | ADC LVDS capture on hardware (eye/valid data) | physical | ILA + known tone into AD9484 | NOT RUN | NOT RUN |

### STM32 (section 2)

| ID | Test | Type | Command | Result on the original tree | BETA tree result (`beta/stm32/README.md`) |
|---|---|---|---|---|---|
| S-01 | Dependency / include check | design check | `python3 tools/check_stm32_includes.py` | **FAIL** (exit 1) — 53 absent HAL/CMSIS/USB headers, 6 case mismatches | 0 case mismatches; 11 UNKNOWN headers only in unbuilt `iio*.c` |
| S-02 | Cube package completeness | design check | `tools/stm32_check_cube_package.sh <CubeF7>` | NOT RUN (no package) | "missing 0 of 34", exit 0 |
| S-03 | Host syntax probe (non-target) | design check | `clang -fsyntax-only …` | 29/60 TUs fail on missing `stm32f7xx_hal.h` (informational) | superseded by S-04 |
| S-04 | Cross-compile | design check | `arm-none-eabi-g++` | NOT RUN | `build.sh` exit 0, 0 errors, 5 pre-existing warnings |
| S-05 | Link + size | design check | `arm-none-eabi-size` | NOT RUN | RAM 17 480 B (5.33 %), FLASH 93 276 B (8.90 %) |
| S-06 | Static analysis | design check | `cppcheck --enable=warning,style` | NOT RUN (not installed) | NOT RUN |
| S-07 | Pin-map cross-check firmware ↔ schematic | design check | `tools/extract_eagle_netlist.py --part U2` vs `main.h` | PASSED for the 60 named GPIO macros; **conflict found** for HSE (8 vs 25 MHz) and ADF4382 pins | conflicts closed by D-01, D-04 |
| S-08 | Flash + CDC enumeration | physical | ST-LINK, `lsusb`/Device Manager | NOT RUN | NOT RUN (Step 16.1) |
| S-09 | Settings packet accepted (state READY_FOR_DATA) | physical | send flag + 82-byte packet | NOT RUN (static analysis predicted failure: C4, C5) | NOT RUN; C4/C5 fixed and host-tested |
| S-10 | Power-sequence timing on `EN_*` rails | physical | oscilloscope | NOT RUN | NOT RUN (Step 16.2) |

### Python (section 3)

| ID | Test | Type | Command | Result on the original scripts | BETA package result |
|---|---|---|---|---|---|
| P-01 | Dependency resolution | design check | `pip install -r requirements.txt` in a venv | PASSED (10 packages) | pinned `beta/gui/requirements.txt` installed |
| P-02 | Syntax (ast) of 27 scripts | design check | `python3 tools/check_python_imports.py` | **FAIL** (exit 1) — `GUI_V1.py` IndentationError; 26/27 OK | n/a |
| P-03 | Import test of third-party modules | design check | `… --try-import` (venv) | PASSED for GUI modules; FAIL for `openEMS`/`CSXCAD` (not on PyPI) | n/a |
| P-04 | Module import of each GUI file | design check | `python -c "import GUI_V6_Demo"` etc. | PASSED V2…V6_Demo (import only); V1 FAIL | n/a |
| P-05 | pyflakes | design check | `pyflakes 9_Firmware/9_3_GUI/*.py` | undefined names in `GUI_V6.py:392`, `GUI_V4_2_CSV.py:430` (informational) | n/a |
| P-06 | Unit tests | design check | `pytest` | NOT RUN — no tests exist upstream | **76 passed in 3.62s** (executed 2026-10-09 for this edition) |
| P-07 | GUI startup smoke | design check | procedure GUI-T05 | NOT RUN | `--selftest` exit 0 (executed 2026-10-09); headless Tk smoke tests in the suite |
| P-08 | Demo-data verification (`test_radar_data.csv`) | design check | column/row check | PASSED (16 384 rows = 32 chirps × 512) | used by `tests/test_sim_pipeline.py` |
| P-09 | Hardware link (CDC / FTDI) | physical | — | NOT RUN | NOT RUN (Step 16.7) |

### PCB documentation (section 4)

| ID | Test | Type | Command | Result |
|---|---|---|---|---|
| B-01 | ERC (fresh run) | design check | EAGLE `ERC` | NOT RUN — stored approved ERC items: Main 4, others 0 |
| B-02 | DRC (fresh run) | design check | EAGLE `RATSNEST; DRC` | NOT RUN — stored: Main 211 approved + 2 390 airwires; Power 309 airwires; Synth 0; PA 0 (KiCad DRC of the beta boards: Main/RF PA 0 unconnected, Power 89 — `beta/pcb/README.md`) |
| B-03 | Missing-library detection | design check | XML: all `<library>` embedded | PASSED — no external library references for any board |
| B-04 | sch/brd consistency | design check | part/net set comparison (XML) | PASSED Synth, PA; **FAIL** Main (10 board-only signals, 210 value mismatches) and Power (version mismatch 9.6.2/7.4.0, 1 board-only signal) |
| B-05 | BOM completeness | design check | `python3 tools/gen_eagle_bom.py …` → `docs/BOM/` | **FAIL** — 0 MPN attributes on all boards; value-less references 244/80/6/47 |
| B-06 | Manufacturing-export completeness | design check | `python3 tools/check_manufacturing_files.py` | **FAIL** (exit 1) for the designer-released export; `--include-generated` exit 0 for the generated `engineering/PCB/` packages (AC-B4) |
| B-07 | Outline/hole extraction | design check | `python3 tools/gen_board_outline_svg.py …` | PASSED for 4 boards |
| B-08 | Stack-up confirmation | physical/vendor | fab quote with stack-up drawing | NOT RUN |
| B-09 | Impedance coupon measurement | physical | TDR at fab | NOT RUN |

### Repository / documentation (section 5)

| ID | Test | Command | Result |
|---|---|---|---|
| R-01 | Inventory generation | `python3 tools/gen_inventory_doc.py` | PASSED (482 rows) |
| R-02 | Documentation link validation | `python3 tools/check_doc_links.py` | **FAIL** — 34 broken references before the reconstruction (README `10_docs/*` etc.); re-run for the residual list |
| R-03 | Expected-artifact manifest | `python3 tools/check_missing_files.py` | **FAIL** — 26 P0 items missing (see `docs/03_MISSING_COMPONENTS.md`) |

## 16.3 Acceptance criteria (sections A–H)

Copied from `docs/TESTING/ACCEPTANCE_CRITERIA.md` ("Each criterion is objective, references the test ID … Current status is given honestly: nothing hardware-related is accepted"). Status column as recorded in the source on 2026-10-08/09; the BETA tree (section H) is evaluated on `beta/`, not on the originals.

| ID | Criterion | Evidence required | Status |
|---|---|---|---|
| AC-F1 | RTL parses and elaborates with iverilog and verilator with zero errors (F-01..F-03) | `build/lint/iverilog_top.log` empty of errors; verilator 0 `%Error` | NOT MET (original); see AC-X1 |
| AC-F2 | No module instantiated without definition; all Xilinx IP as committed `.xci` | Vivado elaboration log; `ls 9_Firmware/9_2_FPGA/ip/*.xci` | NOT MET (6 missing) |
| AC-F3 | `cntrt.xdc` (or successor) has zero placeholders and every top-level port bit constrained or removed; F-04 exit 0 | tool output | NOT MET |
| AC-F4 | Pin map confirmed by the designer against the AMD FTG256 package file and the routed board | signed-off `PIN_MAP_FROM_SCHEMATIC.md` with "VERIFIED" column | NOT MET |
| AC-F5 | Synthesis on the confirmed part with ≤ 90 % of LUT/FF/DSP/BRAM and zero unresolved CRITICAL WARNINGs | `build/vivado/util.rpt` | NOT MET |
| AC-F6 | Timing closure WNS ≥ 0, WHS ≥ 0 on all constrained clocks; `report_cdc` no critical | `timing.rpt`, `cdc.rpt` | NOT MET |
| AC-F7 | Testbench runs on xsim with pass/fail gating and passes | sim log with 0 assertion failures | NOT MET |
| AC-F8 | Bitstream generated and archived with its build log | `build/vivado/*.bit` + log | NOT MET |
| AC-F9 | (Physical) ADC capture validated with a CW tone | ILA capture / host data | NOT RUN |
| AC-S1 | Cube package check exit 0 (S-02) | script output | NOT MET (no package; beta: exit 0) |
| AC-S2 | `.ioc` regenerated; generated MSP equals repository MSP | diff | NOT MET |
| AC-S3 | `tools/check_stm32_includes.py` exit 0 with Cube sources on the include path and zero case mismatches | tool output | NOT MET |
| AC-S4 | Firmware compiles and links with `arm-none-eabi-g++`, zero errors; size < 1 MB flash / 320 KB RAM | map, `size` output | NOT MET (original); see AC-X2 |
| AC-S5 | Conflicts C1–C7 closed with documented decisions | `docs/04_RECOVERY_TASKS.md` R-STM-xx DONE | NOT MET |
| AC-S6 | (Physical) CDC enumerates; start flag + settings accepted; status string received | host log | NOT RUN |
| AC-S7 | (Physical) rail sequencing order and delays match `Power Management V6.xlsx` | scope captures | NOT RUN |
| AC-P1 | `pip install -r requirements.txt` succeeds on a clean venv | pip log | **MET** (2026-10-08, Python 3.14.7) |
| AC-P2 | All third-party imports succeed | tool output | **MET** for GUI modules |
| AC-P3 | Every file in `9_Firmware/9_3_GUI` parses | tool exit 0 | NOT MET (`GUI_V1.py`) |
| AC-P4 | `GUI_V6_Demo.py` starts, shows moving targets, closes with exit 0 | screenshot + exit code | NOT RUN |
| AC-P5 | A unit-test suite exists and passes | pytest log | NOT MET (upstream); see AC-X3 |
| AC-P6 | One hardware GUI decodes the real firmware/FPGA packet format end-to-end | capture + decoded targets | NOT RUN |
| AC-P7 | Packaged demo runs on a machine without Python | installer test log | NOT RUN |
| AC-B1 | Fresh ERC and DRC reports with 0 unapproved errors for each board | reports under `docs/PCB/reports/` (directory to be created) | NOT MET |
| AC-B2 | `RATSNEST` "Nothing to do" and 0 elements outside the outline for Main and Power | EAGLE status line | NOT MET |
| AC-B3 | sch/brd consistent, single EAGLE version per board | consistency check pass | NOT MET (Main, Power) |
| AC-B4 | Gerber + drill + fab + assembly + P&P + BOM(MPN) + schematic PDF for all four boards | `tools/check_manufacturing_files.py` exit 0 | **PARTIALLY MET** (generated packages exist for all four boards; designer-released EAGLE export, MPNs, vendor fab notes NOT MET) |
| AC-B5 | BOMs 100 % MPN, 0 empty values, DNP column | `docs/BOM/*` with `mpn_status` all VERIFIED | NOT MET |
| AC-B6 | Vendor stack-up drawing per board consistent with DRU and impedance note | fab documents | NOT MET |
| AC-B7 | (Physical) impedance coupons 50 Ω ± 10 %, 100 Ω ± 8 % | TDR report | NOT RUN |
| AC-B8 | Design conflicts K1, K2, K3, K4, K7 closed | decision records | NOT MET |
| AC-M1 | Outline/hole drawings for all PCBs | `engineering/MECHANICAL/` DXF, STEP, plan view, dimension sheets | **MET** (thickness ASSUMED) |
| AC-M2 | Enclosure, antenna and pedestal CAD committed with drawings | STEP + PDF under `10_docs/Hardware/` (missing in the repository) | NOT MET (PROPOSED designs exist under `engineering/DESIGN/`, chapter 10) |
| AC-M3 | Assembly guide `10_docs/assembly_guide.md` (missing in the repository) | file exists, link check passes | NOT MET (this manual's chapter 15 is the proposed content) |
| AC-M4 | Exploded view with balloons matching BOM | PDF | PARTIAL (CONCEPTUAL view with balloons; real geometry BLOCKED, MDR-06) |
| AC-M5 | Mass table per assembly | measured or CAD-derived values | NOT MET (estimates only) |
| AC-D1 | Documentation tree of `claude.md` §13 present | `tools/check_missing_files.py` DOC-* all present | **MET** |
| AC-D2 | `tools/check_doc_links.py` exit 0 | tool output | NOT MET |
| AC-D3 | README corrected (Gerber claim, FPGA part, `10_docs` references) | diff | NOT MET (needs the owner's decision) |
| AC-D4 | LICENSE file consistent with the MIT badge; `.gitignore` | files | NOT MET |
| AC-D5 | Every P0 item in `docs/03_MISSING_COMPONENTS.md` has an owner and a recovery task | `docs/04_RECOVERY_TASKS.md` | **MET** (tasks defined; none closed) |
| AC-E1 | Every registered drawing has native file and exports present and well-formed | `python3 tools/gen_drawing_register.py --check` exit 0 | **MET** (re-run 2026-10-09: 89 drawings, 333 files, 0 problems) |
| AC-E2 | EAGLE XML ↔ KiCad conversion counts agree for all boards | `engineering/VALIDATION/PCB_CROSS_CHECK.md` | **MET** (32/32 rows OK) |
| AC-E3 | No missing symbols/footprints; schematic ↔ board part lists identical | `tools/gen_schematic_reports.py` exit 0 | **MET** |
| AC-E4 | Any drawing VERIFIED against EAGLE output or hardware | `VALIDATION/DRAWING_CHECKS.md` §2 | NOT MET (0 VERIFIED) |
| AC-E5 | Enclosure/antenna/pedestal/cooling drawings exist | register MECH-ENC/ANT/PED/COOL | NOT MET (BLOCKED; DSN-* proposals exist) |
| AC-E6 | Proposed designs (DSN-*) registered with native editable files and exports present | `tools/gen_drawing_register.py --check` | **MET** (16 PROPOSED entries after regeneration, 0 file problems) |
| AC-E7 | Antenna proposal simulated (S11 < −10 dB at f0 ± B/2) and coupon measured | openEMS log + VNA data | simulation MET per AC-X6; coupon NOT RUN |
| AC-E8 | Owner approval of decisions D-01…D-15 recorded | signed decision log | NOT MET |
| AC-X1 | beta RTL parses/elaborates/lints with 0 errors and all testbenches pass | `beta/fpga/logs/` | **MET** (BETA) |
| AC-X2 | beta firmware compiles and links; host tests pass | `beta/stm32/build_out/`, `logs/` | **MET** (BETA) |
| AC-X3 | beta GUI test suite passes; packaged app starts | `beta/gui` pytest (source says 55 passed; 76 passed on 2026-10-09) | **MET** (BETA) |
| AC-X4 | beta boards: 0 unconnected on Main/RF PA/Synth; Power ≤ 100 open with documented reasons | `beta/pcb/*/exports/reports/DRC_report.json` | **MET** (BETA; Power 89 listed) |
| AC-X5 | host-link bridge testbench, firmware build and GUI parser agree on one frame vector | `tb_frame.hex` shared | **MET** (BETA) |
| AC-X6 | antenna row S11 < −10 dB at f0 in simulation | `TUNING_LOG.md` | **MET** (−18 dB; band 128 MHz) |

Observation MAN-16-1: `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-E1/AC-E6 still quote "73 drawings" and "11 PROPOSED entries"; the register regenerated for this edition has 89 drawings and 16 PROPOSED entries (Appendix A). The acceptance file was not modified (it is outside `manual/`).

## 16.4 Evidence collection

Rules (source: `docs/TESTING/VALIDATION_PLAN.md` §6, copied): every executed command's output is saved under `build/` (lint logs in `build/lint/`, Vivado in `build/vivado/`, STM32 in `build/stm32/`) and referenced by test ID in `docs/TESTING/ACCEPTANCE_CRITERIA.md` when reporting; physical tests record instrument, serial number, date and raw capture file; a test result changes from NOT RUN to PASSED/FAILED only with an attached log. BETA logs already exist under `beta/fpga/logs/`, `beta/stm32/logs/` and are referenced by the tables above.

Evidence to collect during the first integration (source: `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §D, extended by the steps above), to be stored under `engineering/VALIDATION/` with the acceptance ID it closes:

| Item | Step | Closes |
|---|---|---|
| Rail voltages, no load, per X2…X35 (CP-4) | 15.4 | AC-S7 input |
| Scope captures of the enable sequence F1–F10 with delays | 16.2 | AC-S7 |
| USART3 banner and host CDC enumeration log (VID/PID, serial = UID) | 16.1 | AC-S6 |
| Settings packet accepted → status string received | 16.7 | AC-S6, AC-P6 |
| AD9523 lock status and counter readings 100 / 120 / 400 MHz | 16.4 | Step 16.4 acceptance |
| CAL_STAT / CAL_LANE_INFO / CAL_ERR / CAL_UNDET per lane, ADC pattern used | 16.5 | AC-F9 |
| FPGA DONE, DIG_0..4 handshake capture; Vivado utilisation/timing/CDC reports and bitstream log | 16.3 | AC-F5…AC-F8 |
| PA IDQ per board and plate temperature vs time (drain gating on/off noted) | 16.6 | thermal design case B |
| ADAR1000 SPI capture (CS, SCLK, phase words) | 16.8 | D-06, D-19 |
| Spectrum and envelope at 10.5 GHz into the load; measured chirp bandwidth B | 16.9 | parameter-table TBD |
| Scan time per revolution, motor class and `Stepper_steps` used | 16.10 | D-12 |
| Photos of the first harness with cable labels; real cut lengths of the 144 cables | 15.14–15.18 | DSN-HAR-01 |
| Measured board thickness and component heights | 15.1, 15.9 | G-01, G-02 |


---

<!-- chapter 17: K1–K8, D-01…D-19, G-01…G-12, MDR-*, register of unresolved items -->
# Open issues and decisions — consolidated registers

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** this chapter is a register compilation. Conflicts K1–K8 are copied from `docs/SYSTEM/BLOCK_DIAGRAM.md` §4 (SOURCE-DERIVED findings, all OPEN); decisions D-01…D-15 from `engineering/DESIGN/00_DESIGN_BASIS.md` §2 and D-16…D-19 from `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §3–4 (PROPOSED DESIGN, none approved by the owner); geometry gaps G-01…G-12 from `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md` (BLOCKED / UNRESOLVED, with PROPOSED values where noted); recovery guides MDR-01…13 from `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`; task states from `docs/04_RECOVERY_TASKS.md`. Four observations raised while compiling this manual are added as MAN-01…MAN-04. Nothing here is closed.

**Sources:** `docs/SYSTEM/BLOCK_DIAGRAM.md` §4, `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §12, `engineering/DESIGN/00_DESIGN_BASIS.md` §2–3, `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §3–4, §6, `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`, `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`, `docs/04_RECOVERY_TASKS.md`, `docs/03_MISSING_COMPONENTS.md`, `docs/TESTING/ACCEPTANCE_CRITERIA.md`.

**Planned figures:** none.

## 1. Configuration conflicts K1–K8

Eight conflicts between the CAD, the firmware, the RTL, the GUI and the documentation; each has an owner and none is closed (source: `docs/SYSTEM/BLOCK_DIAGRAM.md` §4, copied verbatim):

| # | Topic | A | B | Owner |
|---|---|---|---|---|
| K1 | FPGA part | CAD/xlsx/drawio XC7A50T-2FTG256I | README/docs/XDC XC7A100T | hardware designer |
| K2 | STM32 HSE | schematic 8 MHz crystal | firmware 25 MHz | hardware designer |
| K3 | Host data path | CAD: STM32 USB-FS only | RTL/GUI V6: FT601 USB 3.0; GUI V2–V5: FT2232H | system architect |
| K4 | PA supply | xlsx 16 × 22 V / 2 A | Power Board `Vin [12-17] V`, no 22 V rail | power designer |
| K5 | FPGA packet format | RTL `0xAA … 0x55` | GUI `A5C3 … CRC16` | software |
| K6 | ADF4382 pins | `main.h` PG6..PG15 (= schematic) | `adf4382a_manager.h` PG0..PG9 | firmware |
| K7 | Synth oscillators | schematic OCXO 100 MHz + 2 × VCXO 50 MHz | xlsx VCXO 100 MHz; firmware `vcxo_freq = 100 MHz` | RF designer |
| K8 | Antenna | README patch 8×16 / slotted 32×16 | two different waveguide simulations, no CAD | antenna designer |

Interim positions taken by the BETA work, which the owner must confirm or overturn (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4, §7, §8, §12; `beta/fpga/README.md` "Remaining work" item 2; `engineering/DESIGN/00_DESIGN_BASIS.md` §2):

| # | BETA / PROPOSED interim position | Decision needed from | Blocking for |
|---|---|---|---|
| K1 | `beta/fpga/vivado/create_project.tcl` default part `xc7a50tftg256-2` = schematic U42 | hardware designer: confirm the mounted part | R-FPGA-01, AC-F5 (resource fit of two 1024-point FFT IPs and 64 DSP48E1 FIRs on the 50T) |
| K2 | `beta/stm32` clock tree written for the real 8 MHz crystal | hardware designer: board revision check of XTAL1 | R-STM-05, AC-S7 |
| K3 | option B (SPI bridge through the STM32 CDC) implemented as BETA; option A (FT601 on Main Board rev. B, bank 35) prepared as pin plan and `beta/pcb/MAIN_BOARD_REVB` | system architect: D-16 / D-17 / D-18 | R-SYS-01, AC-P6, slip-ring channel count D-13 |
| K4 | DSN-PSU-01 22 V module proposed; needs a `TX_GATE` line (FPGA spare pin UNRESOLVED) | power designer: D-14 | MDR-12, thermal case B (drain gating) |
| K5 | bridge frame (`0xA5 0x5A` sync, CRC-16/CCITT-FALSE) implemented in RTL, firmware and GUI | software: adopt the frame as the one format | R-SYS-01, AC-P6 |
| K6 | ADF4382 pin collision fixed in `beta/stm32` to the `main.h` / schematic assignment | firmware: confirm | R-STM-06 |
| K7 | none — the BETA firmware keeps `vcxo_freq = 100 MHz`; schematic part values are 50 MHz VCXO / 100 MHz OCXO | RF designer: identify the mounted oscillators | clock tree of the AD9523, all programmed frequencies in chapter 2 §4 |
| K8 | PROPOSED 16-row × 8-patch panel per D-01; waveguide variant only as a sizing sheet | antenna designer: D-01 and the variant | R-MECH-01, MDR-03, AC-E7, range performance (chapter 1 §5) |

## 2. Design decisions D-01…D-19

All decisions are PROPOSED DESIGN content; none has been approved by the owner (AC-E8 "Owner approval of decisions D-01…D-15 recorded" is NOT MET; source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`, row AC-E8). D-01…D-15 (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §2, columns Decision / Rationale / Alternatives copied verbatim; the "Owner approval" column is compiled from `00_DESIGN_BASIS.md` §3, `docs/04_RECOVERY_TASKS.md` R-DSN-06 and `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §12):

| ID | Decision | Rationale | Alternatives | Owner approval |
|---|---|---|---|---|
| D-01 | Design the **patch-array (Nexus) antenna** as the primary antenna; provide only a sizing sheet for the slotted-waveguide (Extended) variant | A patch array is manufacturable with the same PCB workflow and verifiable with the openEMS/Qucs tools already used in `5_Simulations`; slotted waveguides need machining and a full EM design | waveguide array (CONCEPTUAL sizing sheet in `ANTENNA/README.md`) | REQUIRED — antenna designer (R-DSN-06 BLOCKED); rev. B of D-01 pending: if B exceeds ≈ 100 MHz the series row feed must change (report §8) |
| D-02 | The 16 radiating "elements" are **16 horizontal rows** stacked vertically at 14.3 mm; each row is a **series-fed resonant array of 8 patches** | Matches "8×16", the elevation-scanned ULA of the firmware and a fixed narrow azimuth beam rotated mechanically | corporate feed per row (lower squint, more layout area) | REQUIRED (AC-E8) |
| D-03 | 8 patches per row | parameter table row 77 | — | REQUIRED (AC-E8) |
| D-04 | Substrate RO4350B, h = 0.508 mm, 35 µm Cu, single dielectric layer, full back ground | datasheet in repo; PCBWay impedance note is for RO4350B; 20 mil gives good patch bandwidth (~2 %) with manageable surface waves | 0.762 mm (wider band, more surface wave) | REQUIRED (AC-E8) |
| D-05 | 50 Ω end-launch 2.92 mm connectors on the left edge, one per row, 14.3 mm pitch (body ≤ 12 mm wide) | simplest verifiable feed; keeps the ground plane continuous | probe feed from the back (allows SMA on rear) | REQUIRED (AC-E8) |
| D-06 | Row phase centre spacing is λ/2; each row's feed line length is **equal** so the ADAR1000 calibration tables remain valid | elevation scanning depends on equal electrical length to each row | — | REQUIRED (AC-E8) |
| D-07 | Board stack pitch 25 mm (component heights assumed 15 mm top / 4 mm bottom until measured) | no 3-D models; standard 25 mm M3 standoffs | measure, then shrink | REQUIRED — mechanical owner; depends on G-02 measurement (R-DSN-06, R-DSN-07) |
| D-08 | Enclosure: folded 2.5 mm aluminium chassis + lid, 10 mm board-to-wall clearance, IP54 target, antenna panel in the front face behind a PTFE/ABS radome window | aluminium gives the heat path for the PA spreader; sheet metal keeps cost low | machined frame | REQUIRED (AC-E8; MDR-01 "owner approval of D-07…D-09") |
| D-09 | Board arrangement: Power Board on the base, Main Board above it (25 mm), Synth on the Main-Board tier beside the SMA field; PA spreader vertical behind the antenna panel at the front; stepper/slip ring below the base | shortest coax from Synth J-ports to Main J1/J18–J23; rails cables short; RF to the front | side-by-side single tier (larger footprint) | REQUIRED (AC-E8; MDR-01) |
| D-10 | Thermal design case: ambient 45 °C, TBASE(PA) ≤ 85 °C, **drain gated with the pulse train** (duty computed from the timing); continuous-bias case reported as infeasible without liquid cooling | 16 × 37 W = 591 W quiescent is not coolable in a sealed rotating head; gating requires a hardware change (D-14) | — | REQUIRED (AC-E8); consequence of K4 |
| D-11 | 10 mm aluminium heat spreader common to all 16 PA boards, fan-cooled fin stack at the rear, 1.5× airflow margin | conduction from 16 hot spots into one plate, then forced air | per-PA heatsinks | REQUIRED (AC-E8) |
| D-12 | Azimuth drive: stepper → GT3 belt 1:3 → turntable; **revised by DSN-CALC-01 §2**: with a ≈ 10 kg head a NEMA 23 needs ≥ 200 ms per 7.2° step (revolution ≈ 19 s); a NEMA 34 (3 N·m class) allows ≈ 100 ms; firmware `Stepper_steps = 600` for 1:3 | torque calculation from the detailed mass table; belt isolates the motor from the slewing ring | ratio 1:6 (`Stepper_steps = 1200`), lighter head | REQUIRED — motor class / ratio (R-DSN-06 BLOCKED; report §12) |
| D-13 | Slip ring 12 channels (VIN ×4 @10 A, 22 V ×4 @10 A, USB 2.0 ×4) through a 60 mm bore slewing bearing; everything else rotates with the head | only DC in and the host link cross the rotation | Ethernet/wireless host link (removes 4 channels) | REQUIRED — channel count depends on K3 and on CBL-144 (stepper driver location, "DECISION NEEDED") (R-DSN-06) |
| D-14 | 22 V PA supply: synchronous boost 12–17 V → 22 V, 150 W average / bulk capacitance for 45 A pulse peaks, high-side eFuse/MOSFET switch from `EN/DIS_RFPA_VDD`, plus a per-pulse drain-gating FET per PA board (TTL from the FPGA/MCU `DIG` lines — pin to be allocated) | closes conflict K4; the firmware already sequences VG before VD | separate 22 V mains PSU on the pedestal (bigger slip ring) | REQUIRED — gating line allocation (R-DSN-06; MDR-12) |
| D-15 | Harness: cable IDs from `interconnection_table.md`; coax RG-405 (0.086") hand-formable equal-length for Main↔PA and Synth↔Main; Molex 22-01-3027/3037 crimp housings for the 2-/3-pin headers; 20-way IDC ribbon for SV1 | standard parts matching the footprints in the schematics | — | REQUIRED (AC-E8); see MAN-03 on cable-ID schemes |

Host-link decisions D-16…D-19 (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §3 option table and §4; owner per `docs/SYSTEM/BLOCK_DIAGRAM.md` §4 row K3 and `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §12):

| ID | Decision | Content | Status | Owner approval |
|---|---|---|---|---|
| D-16 | Option A — FT601 on Main Board rev. B is the **target for rev. B** | route U6 to bank 35 (46 I/Os), add USB 3 connector, crystal, RREF, ESD (`ft601_added_parts_BOM.csv`); throughput 400 MB/s; RTL already written (fix 2-bit BE → 4-bit; honour TXE_N); host driver FTDI D3XX; risk: 10-layer board respin, USB 3 SI | pin plan `ft601_pin_assignment.csv` + `ft601_bank35.xdc`; `beta/pcb/MAIN_BOARD_REVB` layout; FT601 datasheet not in the repository — AC timing, RREF, VBUS, 1.0 V core supply to be verified before the schematic is edited | REQUIRED — system architect (K3) |
| D-17 | Option B — SPI bridge via the STM32, **implement now (BETA)** | no PCB change: DIG_5/6/7 + SPI1 already routed to the FPGA; throughput ≤ 1 MB/s (CDC-bound); new RTL `host_bridge_spi.v` + packer, STM32 `host_bridge.c`, GUI parser; risk: protocol only, SPI1 shared with the ADAR1000 (time-multiplexed) | implemented in `beta/fpga`, `beta/stm32`, `beta/gui`; `tb_host_bridge_top` PASS; bench test open (§6) | REQUIRED — system architect (K3); firmware rule "no ADAR1000 transaction overlaps a bridge read" to be enforced |
| D-18 | Option C — Ethernet mezzanine on bank 35, **documented only** | new PCB with RGMII PHY on the 50 free bank-35 pins; 100 MB/s; new MAC/UDP stack; highest risk | not pursued | — |
| D-19 | RTL changes for a real FT601 | widen `ft601_be` to 4 bits, drive `BE = 4'b1111` for full words, respect `TXE_N` back-pressure, add `ft601_reset_n`/`wakeup_n`/`siwu_n` as outputs | recorded for `beta/fpga`, **not yet applied there** | follows D-16 |

What the proposals do **not** settle (source: `engineering/DESIGN/00_DESIGN_BASIS.md` §3, copied): conflicts K1–K8, component heights (G-02), final Power Board outline (G-10), whether the host link stays USB (affects D-13), antenna variant (D-01), the PA pulse-gating implementation (D-14 needs a spare control line), and all RF performance targets (gain, bandwidth B is TBD in the parameter table).

## 3. Unresolved geometry G-01…G-12

Every mechanical quantity that the drawings need but no repository file provides; nothing below was estimated into a drawing (source: `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`, VAL-GEO-01 Rev A, copied verbatim):

| ID | Quantity | Needed by | Available evidence | Missing | Status |
|---|---|---|---|---|---|
| G-01 | PCB thickness (all 4 boards) | STEP bodies, stack-up, stand-offs | none (KiCad assumed 1.6 mm) | vendor stack-up / designer decision | BLOCKED — MISSING DATA |
| G-02 | Component heights (both sides) | enclosure clearances, stand-off heights, exploded view | packages only; 3-D URNs not embedded | 3-D models or measurement of assembled boards | BLOCKED |
| G-03 | Board masses (bare and assembled) | pedestal/motor sizing, mass table | area × assumed thickness (ESTIMATE in `MECHANICAL/dimensions/`) | weighing or CAD with densities | BLOCKED (estimate only) |
| G-04 | Enclosure: envelope, wall thickness, mounting bosses, connector cut-outs | ASM-EXP-01, M1–M6 | README text references only (`10_docs/Hardware/Enclosure` absent) | enclosure CAD | BLOCKED |
| G-05 | Relative board placement and stacking height | internal layout drawing | none | layout decision | BLOCKED (CONCEPTUAL drawing only) |
| G-06 | Antenna element geometry, substrate, feed network, radome | antenna assembly drawing | `02_hardware/04_antenna_beamforming.md` (λ/2 = 14.3 mm, aperture 214.3 mm), `8_Utils/Antenna_Array.jpg` (undimensioned photo), two contradictory waveguide simulations | antenna CAD and measurements | BLOCKED |
| G-07 | Pedestal, stepper, slip ring, bearing envelope | pedestal drawing | firmware constants only (200 steps/rev, 50 positions) | mechanical design | BLOCKED |
| G-08 | Heatsink / fan geometry and airflow | cooling drawing | PA dissipation implied by xlsx IDQ | thermal design | BLOCKED |
| G-09 | Cable lengths, routing, bend radii (SMA coax ×34, Molex ×~50) | harness drawing | connector list only | harness design | BLOCKED |
| G-10 | Power Board final outline (hole pattern suggests a smaller board than 280 × 300) | fab drawing | `POWER_SUPPLY_dimensions.md` (holes at inner positions) | designer confirmation | UNRESOLVED |
| G-11 | Fastener sizes (Ø3.2 holes → M3 inferred) | parts list | hole diameters | specification | UNRESOLVED (inferred) |
| G-12 | Keep-out zones around RF connectors and the QPA2962 | layout/enclosure | none | designer input | BLOCKED |

Update 2026-10-09 (source: same file, "Update 2026-10-09 — proposals", copied): G-04, G-05, G-07, G-08, G-09, G-12 now have PROPOSED values in `engineering/DESIGN/` (D-07…D-15); they stay open until the owner accepts the decisions and the assumed inputs (G-01 thickness, G-02 component heights, G-11 fasteners) are measured/specified. G-03 mass: FreeCAD volume-based estimate head ≈ 9.9 kg (includes component envelopes as solid plastic — overestimate), pedestal ≈ 12 kg + 1.1 kg stepper (`MECHANICAL/CAD/aeris10_mass_table.json`). G-06 antenna: PROPOSED patch panel 165 × 248 mm; G-10 Power Board outline unchanged. Photographs in `8_Utils/` show a prototype but carry no scale reference and were not used to derive dimensions.

| ID | Owner / decision needed |
|---|---|
| G-01 | PCB fabricator stack-up or designer decision per board (MDR-07) |
| G-02 | measurement of assembled boards or 3-D models assigned in KiCad (MDR-09); gates D-07 |
| G-03 | weighing of assembled boards; replaces the ESTIMATE and the FreeCAD overestimate; feeds D-12 |
| G-04, G-05, G-08, G-09, G-12 | owner acceptance of D-07…D-11, D-15 (PROPOSED values exist) |
| G-06 | antenna designer: D-01 and K8 |
| G-07 | owner acceptance of D-12, D-13 and part selection (bearing, slip ring, motor; MDR-05) |
| G-10 | Power Board designer confirmation of the outline (also MDR-08) |
| G-11 | fastener specification (M3 inferred from Ø3.2) |

## 4. Missing-drawing recovery guides MDR-01…MDR-13

One guide exists for each drawing that could not be generated from repository evidence; the generator scripts themselves are the procedure for the drawings that were generated (source: `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`, ENG-MDR-01 Rev A, headings, "Missing" fields and the status table "Status update 2026-10-09 — proposals now exist"; MDR-13 is referenced only in `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §6):

| ID | Drawing / purpose | Missing source information (not recoverable from the repository) | Proposal delivered 2026-10-09 | Remaining to reach SOURCE-DERIVED / VERIFIED | Owner |
|---|---|---|---|---|---|
| MDR-01 | MECH-ENC-01 Main enclosure (overall geometry, mounting, PCB supports, connector openings) | envelope, material, wall thickness, board stacking order and spacing (G-04, G-05), component heights (G-02), thermal path (G-08), ingress/EMC requirements | `engineering/DESIGN/MECHANICAL/` (FreeCAD model DSN-MECH-3D, drawings DSN-MECH-01…03) | owner approval of D-07…D-09; sheet-metal detailing (bends, fasteners, gaskets); component heights | mechanical owner |
| MDR-02 | MECH-INT-01 Internal component layout and cable routing | enclosure (MDR-01), cable types/lengths/gauges (G-09), bend-radius rules for the 10.5 GHz coax | DSN-MECH-04 (connector positions from P&P), DSN-HAR-01 (144 cables, lengths) | first-fit length check; unmatched rail pairs; stepper driver location | mechanical owner + harness |
| MDR-03 | MECH-ANT-01 Antenna assembly | everything dimensional (G-06); which simulation reflects the built prototype; feed/transition to the PA SMA ports | DSN-ANT-01 (native KiCad board, calc sheet, openEMS model) | run openEMS (one row done, report §8); coupon; connector footprint | antenna designer (K8, D-01) |
| MDR-04 | MECH-COOL-01 Cooling and power assembly | dissipation budget (no current budget per rail), ambient/enclosure conditions, heatsink part, fan part (G-08) | DSN-THM-01 + fin fields in DSN-MECH-3D | PA-board via-field Rth; fan part selection; test | thermal / power designer |
| MDR-05 | MECH-PED-01 Pedestal / azimuth drive | all mechanics (G-07) | DSN-MECH-05 + pedestal in DSN-MECH-3D | bearing/slip-ring/motor part selection; mast interface | mechanical owner (D-12, D-13) |
| MDR-06 | ASM-EXP-01 upgrade from CONCEPTUAL to SOURCE-DERIVED exploded view | MDR-01..05 outputs, fastener spec | still CONCEPTUAL (ASM-EXP-01); the FreeCAD assembly can now be exploded in the GUI | FreeCAD Assembly exploded view + balloons | documentation / mechanical |
| MDR-07 | PCB fabrication drawings with vendor notes (PCB-*-09/11 to reach VERIFIED) | material, finished thickness, copper weights, finish, mask/silk colours, impedance table, tolerances | — | EAGLE-native Gerbers compared with the KiCad set; fabricator DFM report; status VERIFIED only after both agree and the fabricator confirms the stack-up | PCB designer + fabricator |
| MDR-08 | Completion of the Main and Power Board layouts | routing of the listed airwires in EAGLE (master); Power Board final outline (G-10) | BETA: Main 15 → 0 unconnected, Power 308 → 89 (listed in `beta/pcb/POWER_SUPPLY/UNROUTED.md`) | `unconnected_items` = 0 in the DRC report; airwires = 0 in the EAGLE file; regenerate packages | PCB designer |
| MDR-09 | 3-D component models and assembled STEP | model files (EAGLE `package3d_urn` are Autodesk cloud IDs, not embedded) | — | assign 3-D models per package in KiCad, `kicad-cli pcb export step --subst-models`; record max height → resolves G-02 | PCB designer |
| MDR-10 | Native KiCad schematics (editable twin of the EAGLE schematics) | KiCad's schematic importer is GUI-only | — | import each `.sch` via KiCad GUI, ERC, netlist comparison (same net and pin counts) | PCB designer |
| MDR-11 | Hardware-verified drawings (status VERIFIED) | comparison with an EAGLE print/CAM output or with the physical board | — | record each comparison in `VALIDATION/DRAWING_CHECKS.md` §2 with date, method and result | hardware owner |
| MDR-12 | 22 V PA supply (new) | component-level schematic and layout; `TX_GATE` pin | DSN-PSU-01 block schematic, BOM, nets | KiCad component-level schematic + layout; TX_GATE pin allocation; bench test of one gate channel | power designer (D-14, K4) |
| MDR-13 | Main Board rev. B schematic/layout for option A (FT601) | EAGLE schematic update for U6 (46 signals, VCC33/VCCIO, crystal, RREF, VBUS divider, ESD, USB 3 connector); FT601 datasheet checks | `beta/pcb/MAIN_BOARD_REVB/` KiCad project with `NETLIST_DELTA.csv` (new FT_* nets U6 ↔ U42 bank 35, e.g. FT_CLK U6.58 ↔ U42.C4) and `BOM_MAIN_BOARD_REVB_beta.csv` (BETA; no README in the directory at the time of writing) | EAGLE-native schematic update; FT601 datasheet checks; FTDI D3XX host driver test | hardware designer (D-16, K3) |

## 5. Open tasks

### 5.1 Reconstruction tasks (source: `docs/04_RECOVERY_TASKS.md`, section headings; status date 2026-10-08: DONE 7, OPEN 20, BLOCKED 9)

| ID | Task | Status |
|---|---|---|
| R-SYS-01 | Decide the host data path and packet format (K3/K5) | BLOCKED |
| R-FPGA-01 | Confirm FPGA part | BLOCKED |
| R-FPGA-02 | Verify the schematic-derived pin map | BLOCKED |
| R-FPGA-03 | Fix syntax and declaration-order defects | OPEN (done in `beta/fpga`, not in the originals) |
| R-FPGA-04 | Create the Vivado project | OPEN |
| R-FPGA-05 | Recover or re-implement missing modules and FFT IP | BLOCKED → OPEN if originals unavailable |
| R-FPGA-06 | Memory files and LUT authority | BLOCKED |
| R-FPGA-07 | Functional redesign items | OPEN, design work |
| R-FPGA-08 | Constraints: clock groups, CDC, I/O delays | OPEN |
| R-FPGA-09 | Testbench with pass/fail | OPEN |
| R-FPGA-10 | Synthesis, implementation, bitstream | OPEN |
| R-STM-01 | Install toolchain and STM32CubeF7 | OPEN |
| R-STM-02 | Regenerate CubeMX project and USB CDC files | OPEN |
| R-STM-03 | Build-set cleanup | OPEN |
| R-STM-04 | Fix USB RX binding and start-flag padding | OPEN |
| R-STM-05 | Resolve HSE 8 MHz vs 25 MHz | BLOCKED |
| R-STM-06 | Fix ADF4382 driver (pins + platform ops + CS) | OPEN |
| R-STM-07 | GPS path | OPEN |
| R-STM-08 | Compile, link, size, static analysis | OPEN |
| R-GUI-01 | Consolidate GUI versions | OPEN |
| R-GUI-02 | Unit tests | OPEN |
| R-GUI-03 | Packaging and smoke test | OPEN |
| R-PCB-01 | Complete Main Board layout | BLOCKED |
| R-PCB-02 | Complete Power Board layout and fix version mismatch | BLOCKED |
| R-PCB-03 | RF PA production export | PARTIALLY DONE 2026-10-09 (KiCad-converted package; EAGLE-native export and fabricator review OPEN) |
| R-PCB-04 | Frequency Synthesizer production export | PARTIALLY DONE 2026-10-09 (same) |
| R-PCB-05 | BOM completion with MPNs | OPEN |
| R-PCB-06 | Stack-up confirmation | BLOCKED |
| R-MECH-01 | Obtain enclosure, antenna, pedestal CAD and part numbers | BLOCKED |
| R-MECH-02 | Write `10_docs/assembly_guide.md` (missing in the repository) and exploded view | PARTIALLY DONE 2026-10-09 (ASSEMBLY_SEQUENCE.md, PARTS_LIST.md, CONCEPTUAL exploded view; real geometry needs R-MECH-01) |
| R-DOC-01 | Repository hygiene | OPEN, owner decisions |
| R-DOC-02 | Datasheet collection | OPEN |
| R-DOC-03 | Recover `STM32_ALGO.docx` | BLOCKED |

The statuses of the R-FPGA, R-STM and R-GUI tasks refer to the original trees; the corresponding BETA work is tracked separately as R-BETA-01…09 (section 5.4). The missing-component register `docs/03_MISSING_COMPONENTS.md` (IDs FPGA-00…15, STM-01…19, GUI-01…08, MECH-01…06, REPO-01…05, with P0/P1/P2 priorities) maps every item to one of these tasks (source: `docs/03_MISSING_COMPONENTS.md`, lead-in and tables).

### 5.2 Engineering drawings package R-ENG (source: `docs/04_RECOVERY_TASKS.md`, "Engineering drawings package", copied verbatim)

| Task | Status | Evidence |
|---|---|---|
| R-ENG-01 — Render all schematics to SVG/PDF/PNG with title blocks | DONE | `engineering/ELECTRICAL/schematics/*/` (7 sheets); `tools/render_eagle_schematic.py`, `tools/svg_sheets_to_pdf.py` |
| R-ENG-02 — Netlists, component-to-net, unresolved-connection and missing-symbol/footprint reports | DONE | `engineering/ELECTRICAL/netlists/`, `connection_diagrams/`; `tools/gen_schematic_reports.py` exit 0 |
| R-ENG-03 — Convert the four EAGLE boards to KiCad and export Gerber/drill/PDF/SVG/DXF/STEP/P&P/IPC-2581/IPC-D-356/DRC/3-D | DONE (generated; not designer-released) | `engineering/PCB/<BOARD>/`, `engineering/VALIDATION/CAD_EXPORT_LOG.md` (0 failed steps), `PCB_CROSS_CHECK.md` 32/32 OK |
| R-ENG-04 — System block / interconnection / data-flow / power-distribution diagrams (editable DOT + Mermaid) | DONE | `engineering/SYSTEM/`, `engineering/ELECTRICAL/power_distribution/` |
| R-ENG-05 — Software architecture diagrams (FPGA hierarchy, pipeline, STM32, USB CDC, Python, end-to-end) | DONE | `engineering/SOFTWARE_DIAGRAMS/` (SD-01…SD-07) |
| R-ENG-06 — Mechanical package from PCB geometry (DXF ×2 sources, STEP, 1:1 plan view, dimension sheets, hole tables) | DONE | `engineering/MECHANICAL/`; `tools/gen_mechanical_package.py` |
| R-ENG-07 — Drawing register + file check, recovery plan, validation records | DONE | `engineering/DRAWING_REGISTER.md` (73 drawings, 0 file problems), `MISSING_DRAWINGS_RECOVERY_PLAN.md` (MDR-01…11), `VALIDATION/*` |
| R-ENG-08 — Enclosure, internal layout, antenna, cooling, pedestal drawings | BLOCKED (MDR-01…05) | no source geometry; `VALIDATION/UNRESOLVED_GEOMETRY.md` G-01…G-12 |
| R-ENG-09 — Upgrade exploded view from CONCEPTUAL to SOURCE-DERIVED | BLOCKED (needs R-ENG-08) | MDR-06 |
| R-ENG-10 — Vendor fabrication notes + stack-up → fabrication drawings; EAGLE-native Gerbers compared with the KiCad set | OPEN | MDR-07 |
| R-ENG-11 — Finish Main/Power routing, regenerate packages | OPEN (designer) | MDR-08; KiCad `unconnected_items` 15 / 308 |
| R-ENG-12 — 3-D component models → assembled STEP, component heights | OPEN | MDR-09 |
| R-ENG-13 — Native KiCad schematic twins + ERC (GUI import) | OPEN | MDR-10 |

### 5.3 Proposed designs R-DSN (source: `docs/04_RECOVERY_TASKS.md`, "Proposed designs", copied verbatim)

| Task | Status | Evidence |
|---|---|---|
| R-DSN-01 — Antenna panel proposal (KiCad, calc, openEMS model) | DONE (PROPOSED; not simulated) | `engineering/DESIGN/ANTENNA/` |
| R-DSN-02 — Thermal budget + drain-gating requirement | DONE (PROPOSED) | `engineering/DESIGN/THERMAL/` |
| R-DSN-03 — 22 V PA supply/gate module block design | DONE (PROPOSED) → KiCad capture OPEN (MDR-12) | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/` |
| R-DSN-04 — Head + pedestal 3-D model and 2-D drawings | DONE (PROPOSED) | `engineering/DESIGN/MECHANICAL/` |
| R-DSN-05 — Harness schedule | DONE (PROPOSED) | `engineering/DESIGN/HARNESS/` |
| R-DSN-06 — Owner decisions D-01, D-07, D-12, D-13, D-14 | BLOCKED (owner) | `engineering/DESIGN/00_DESIGN_BASIS.md` §2–3 |
| R-DSN-07 — Simulate/measure the antenna, test one gate channel, measure component heights | OPEN | `ANTENNA_DESIGN_CALC.md` §7; `PA_SUPPLY_22V/README.md` |

The R-DSN-01 status "not simulated" predates the one-row openEMS simulation recorded as R-BETA-06 below and in `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §8; the 16-row coupled simulation and the coupon measurement remain open.

### 5.4 BETA completions R-BETA (source: `docs/04_RECOVERY_TASKS.md`, "BETA completions", copied verbatim)

| Task | Status | Evidence |
|---|---|---|
| R-BETA-01 FPGA RTL builds + missing modules + testbenches | DONE (BETA) | `beta/fpga/build.sh` 0 failures |
| R-BETA-02 STM32 firmware builds + defect fixes + host tests | DONE (BETA) | `beta/stm32/build.sh` exit 0, tests 4/4 |
| R-BETA-03 GUI package + tests + packaging | DONE (BETA) | `beta/gui` pytest 55 passed |
| R-BETA-04 PCB routing completion + BOM MPN + fab notes | DONE (BETA; Power 89 open) | `beta/pcb/*/README.md` |
| R-BETA-05 FPGA→host path (DSN-LINK-01) | DONE (option B code), OPEN (bench, rev. B) | `engineering/DESIGN/HOST_LINK/` |
| R-BETA-06 Antenna simulation | DONE (one row) | `engineering/DESIGN/ANTENNA/simulation/` |
| R-BETA-07 Enclosure detail (flat patterns, fasteners, parts list) | DONE (PROPOSED) | `engineering/DESIGN/MECHANICAL/` |
| R-BETA-09 ISERDES ADC capture + polyphase DDC at 100 MHz | DONE (BETA, bit-exact vs legacy in simulation) | `beta/fpga/rtl/ad9484_iserdes_capture.v`, `adc_capture_calib.v`, `ddc_4x_100m.v`; tb_adc_iserdes_capture, tb_ddc_4x |
| R-BETA-08 Vivado synthesis, flashing, fabrication, bench tests | BLOCKED (tools/hardware not on this machine) | — |

The test counts in this table are those recorded at the tracker's date; the later BETA report states host tests 6/6 and pytest 72 passed (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §4–5).

### 5.5 Items impossible on the authoring machine (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §2, copied)

Vivado synthesis/timing/bitstream (open-source flow attempted — report §3.4), flashing and bench tests, fabrication, measurement of component heights, antenna coupon on a VNA, PA thermal test, 89 Power Board pour connections (manual CAD), EAGLE schematic updates for rev. B, owner decisions K1–K8 and D-01…D-19.

## 6. Observations raised by this manual (MAN-01…MAN-04)

These are inconsistencies found while compiling the chapters; they are recorded for the owners, not resolved here.

| ID | Observation | Evidence | Owner / decision needed |
|---|---|---|---|
| MAN-01 | The electronic scan range is stated four different ways: README "±45°"; `00_notation/parameter_table.md` "approximately ±33° at Δφ = ±160°" from θ = arcsin(Δφ/π); `02_hardware/04_antenna_beamforming.md` §3.2 evaluates the same relation (HW-ANT-3, θ_0 = arcsin(Δφ_n/180°)) to ≈ ±62.7° and then calls ±33° a grating-lobe limit; `01_physics/03_beamforming_theory.md` §6 shows d = λ/2 is grating-lobe-free at all scan angles. arcsin(160/180) is not ≈ 33°. | `README.md` "Technical Specifications"; `00_notation/parameter_table.md` "Inconsistency Resolutions" §4; `02_hardware/04_antenna_beamforming.md` §3.2; `01_physics/03_beamforming_theory.md` §6 | antenna / systems designer: state the intended maximum elevation scan angle and correct the documents; affects the antenna row pattern requirement (D-02) and the range estimate at scan |
| MAN-02 | The matched-filter reference memories encode a 10 → 30 MHz baseband up-chirp (20 MHz span, 3000 samples at 100 MSPS), while the chirp bandwidth B is TBD in the parameter table and 50 MHz is ASSUMED in the range calculation. No file states whether the 20 MHz span is the RF chirp bandwidth. | `beta/fpga/README.md` "What was found and decided" item 1; `00_notation/parameter_table.md` "TBD Tracking"; `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §3 | RF / FPGA designer: define B (ADF4382 sweep or DAC LUT), then redo ΔR, G_p, R_max and the antenna bandwidth requirement (D-01 rev. B) |
| MAN-03 | Two cable-ID schemes coexist: `interconnection_table.md` uses CBL-00…CBL-106 per signal group; `HARNESS_SCHEDULE.md` uses CBL-001…CBL-144 per physical cable with different assignments (e.g. CBL-02 = `+1V8_FPGA` vs CBL-002 = `+5V5_PA`; CBL-21 = SV1 ribbon vs CBL-035). | `engineering/SYSTEM/interfaces/interconnection_table.md` §2–3; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` rows CBL-002, CBL-003, CBL-035 | harness / documentation owner: adopt one scheme (D-15 says "cable IDs from `interconnection_table.md`", the generated schedule does not follow it) before cable labels are printed |
| MAN-04 | Stale cross-tree statements about bridge command set v2: `beta/stm32/README.md` §6a (line 120) and `beta/stm32/DECISIONS.md` D-18 say "The FPGA side of 0x02..0x04 is not implemented in `beta/fpga` yet", whereas `beta/fpga/README.md` and `CHANGELOG.md` record the implementation, `tb_host_bridge_top` PASS with a register write taking effect, and `HOST_LINK_DESIGN.md` §7 synced to the RTL; conversely `beta/fpga/README.md` remaining-work item 8 still lists the GUI `register_map.py` 4-bit mask as open while the file has `ADDR_MASK = 0x1F` and the GUI changelog records the final map. | `beta/stm32/README.md:120`; `beta/stm32/DECISIONS.md` D-18; `beta/fpga/README.md` "Host path", "Remaining work" item 8; `beta/fpga/CHANGELOG.md` "Command set v2…"; `beta/gui/CHANGELOG.md` "final register map"; `beta/gui/aeris10_gui/protocol/register_map.py:18` | firmware and FPGA documentation owners: refresh the two firmware statements and FPGA item 8; then run the end-to-end `REG` test on hardware (open in all three trees) |


---

<!-- chapter A: Drawing register (copy) -->
# Appendix A — Drawing register (copy of `engineering/DRAWING_REGISTER.md`)

**Author of this appendix:** Antidrone Ukraine · antidrone.cc (compilation); the register itself is generated by `tools/gen_drawing_register.py`.

**Status summary:** the register lists 89 drawings — 39 SOURCE-DERIVED, 28 PARTIAL, 16 PROPOSED DESIGN, 1 CONCEPTUAL, 5 BLOCKED — MISSING DATA, 0 VERIFIED (source: `engineering/DRAWING_REGISTER.md`, "Summary"). It was regenerated for this edition with `python3 tools/gen_drawing_register.py --check` on 2026-10-09; the tool reported "register: 89 drawings; statuses {'SOURCE-DERIVED': 39, 'PARTIAL': 28, 'BLOCKED': 5, 'CONCEPTUAL': 1, 'PROPOSED': 16}; file check: 0 problems" (333 registered files checked for existence, non-emptiness and SVG/PDF/DOT well-formedness).

**Sources:** `engineering/DRAWING_REGISTER.md` (ENG-REG-01 Rev A), `tools/gen_drawing_register.py`.

This appendix reproduces the register verbatim so that every figure of this manual can be traced to its drawing ID, native file, exports and missing-data note. Paths in the "Native format" and "exports" columns are relative to the repository root or to the drawing's own directory as the register prints them; the figures used in chapters 1–16 reference the same files. The text below this paragraph is the generated register, unchanged.

## AERIS-10 — Drawing register (generated)

Document ENG-REG-01 · Rev A · 2026-10-09 · generated by `tools/gen_drawing_register.py` (run with `--check` to validate files). Status vocabulary: VERIFIED (checked against hardware/EAGLE output), SOURCE-DERIVED (generated from the native design files, not reviewed), PARTIAL, CONCEPTUAL, BLOCKED — MISSING DATA. No drawing is VERIFIED: nothing was compared with an EAGLE/vendor output or with hardware.

| ID | Drawing | Source | Native format | PDF/SVG/other exports | Status | Missing data |
|---|---|---|---|---|---|---|
| ELEC-SCH-MAIN_BOARD | Schematic set, MAIN_BOARD (4 sheets) | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch (native EAGLE, editable) | `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` | `MAIN_BOARD_schematic.pdf`, `MAIN_BOARD_schematic_sheet1.svg`, `MAIN_BOARD_schematic_sheet2.svg`, `MAIN_BOARD_schematic_sheet3.svg`, `MAIN_BOARD_schematic_sheet4.svg`, `MAIN_BOARD_schematic_sheet1.png`, `MAIN_BOARD_schematic_sheet2.png`, `MAIN_BOARD_schematic_sheet3.png`, `MAIN_BOARD_schematic_sheet4.png` | SOURCE-DERIVED | no revision in source; fonts differ from EAGLE; not reviewed against an EAGLE print |
| ELEC-NET-MAIN_BOARD | Netlist + component-to-net report, MAIN_BOARD | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch | `engineering/ELECTRICAL/netlists/MAIN_BOARD_netlist.csv` | `MAIN_BOARD_netlist_by_part.csv`, `MAIN_BOARD_connection_report.md`, `MAIN_BOARD_unresolved_connections.md`, `MAIN_BOARD_missing_symbols_footprints.md`, `MAIN_BOARD_netlist.d356` | SOURCE-DERIVED | designer disposition of single-pin nets / unconnected pins |
| ELEC-SCH-POWER_SUPPLY | Schematic set, POWER_SUPPLY (1 sheet) | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch (native EAGLE, editable) | `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch` | `POWER_SUPPLY_schematic.pdf`, `POWER_SUPPLY_schematic_sheet1.svg`, `POWER_SUPPLY_schematic_sheet1.png` | SOURCE-DERIVED | no revision in source; fonts differ from EAGLE; not reviewed against an EAGLE print |
| ELEC-NET-POWER_SUPPLY | Netlist + component-to-net report, POWER_SUPPLY | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch | `engineering/ELECTRICAL/netlists/POWER_SUPPLY_netlist.csv` | `POWER_SUPPLY_netlist_by_part.csv`, `POWER_SUPPLY_connection_report.md`, `POWER_SUPPLY_unresolved_connections.md`, `POWER_SUPPLY_missing_symbols_footprints.md`, `POWER_SUPPLY_netlist.d356` | SOURCE-DERIVED | designer disposition of single-pin nets / unconnected pins |
| ELEC-SCH-RF_PA | Schematic set, RF_PA (1 sheet) | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch (native EAGLE, editable) | `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch` | `RF_PA_schematic.pdf`, `RF_PA_schematic_sheet1.svg`, `RF_PA_schematic_sheet1.png` | SOURCE-DERIVED | no revision in source; fonts differ from EAGLE; not reviewed against an EAGLE print |
| ELEC-NET-RF_PA | Netlist + component-to-net report, RF_PA | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch | `engineering/ELECTRICAL/netlists/RF_PA_netlist.csv` | `RF_PA_netlist_by_part.csv`, `RF_PA_connection_report.md`, `RF_PA_unresolved_connections.md`, `RF_PA_missing_symbols_footprints.md`, `RF_PA_netlist.d356` | SOURCE-DERIVED | designer disposition of single-pin nets / unconnected pins |
| ELEC-SCH-FREQUENCY_SYNTHESIZER | Schematic set, FREQUENCY_SYNTHESIZER (1 sheet) | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch (native EAGLE, editable) | `4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch` | `FREQUENCY_SYNTHESIZER_schematic.pdf`, `FREQUENCY_SYNTHESIZER_schematic_sheet1.svg`, `FREQUENCY_SYNTHESIZER_schematic_sheet1.png` | SOURCE-DERIVED | no revision in source; fonts differ from EAGLE; not reviewed against an EAGLE print |
| ELEC-NET-FREQUENCY_SYNTHESIZER | Netlist + component-to-net report, FREQUENCY_SYNTHESIZER | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch | `engineering/ELECTRICAL/netlists/FREQUENCY_SYNTHESIZER_netlist.csv` | `FREQUENCY_SYNTHESIZER_netlist_by_part.csv`, `FREQUENCY_SYNTHESIZER_connection_report.md`, `FREQUENCY_SYNTHESIZER_unresolved_connections.md`, `FREQUENCY_SYNTHESIZER_missing_symbols_footprints.md`, `FREQUENCY_SYNTHESIZER_netlist.d356` | SOURCE-DERIVED | designer disposition of single-pin nets / unconnected pins |
| ELEC-PWR-01 | Power distribution diagram + rail register | PowerBoard.sch, Main/Synth/PA schematics, main.h/main.cpp, Power Management V6.xlsx | `engineering/ELECTRICAL/power_distribution/power_distribution.dot` | `power_distribution.svg`, `power_distribution.pdf`, `power_distribution.png`, `power_rails.md` | SOURCE-DERIVED | rail currents, VIN budget, 22 V PA supply (K4) |
| SYS-01 | System block diagram | 4 schematics, firmware, RADAR_V6.drawio, docs/SYSTEM/BLOCK_DIAGRAM.md | `engineering/SYSTEM/block_diagrams/system_block_diagram.dot` | `system_block_diagram.svg`, `system_block_diagram.pdf`, `system_block_diagram.png`, `system_block_diagram.mmd` | SOURCE-DERIVED | antenna, host, 22 V supply CONCEPTUAL; conflicts K1–K8 open |
| SYS-02 | Hardware interconnection diagram + table | connector nets of 4 schematics, .brd silkscreen, main.h | `engineering/SYSTEM/interfaces/hardware_interconnection.dot` | `hardware_interconnection.svg`, `hardware_interconnection.pdf`, `hardware_interconnection.png`, `interconnection_table.md` | SOURCE-DERIVED | cable types/lengths, Molex pin order, SMA RFIN/RFOUT side, PA instance mapping |
| SYS-03 | Signal and data flow diagram | schematics traced through passives; main.cpp:933-1072; adf4382a_manager.h; radar_system_top.v | `engineering/SYSTEM/data_flow/signal_and_data_flow.dot` | `signal_and_data_flow.svg`, `signal_and_data_flow.pdf`, `signal_and_data_flow.png` | SOURCE-DERIVED | frequencies are firmware intent; BPF parts, antenna path, host data path (K3/K5) |
| SD-01 | FPGA module hierarchy (auto) | 9_Firmware/9_2_FPGA/*.v via tools/gen_verilog_hierarchy.py | `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_module_hierarchy.dot` | `fpga_module_hierarchy.svg`, `fpga_module_hierarchy.pdf`, `fpga_module_hierarchy.png` | SOURCE-DERIVED | 5 modules/IP missing from repo |
| SD-02 | FPGA signal-processing pipeline | radar_system_top.v and submodules | `engineering/SOFTWARE_DIAGRAMS/FPGA/fpga_data_pipeline.dot` | `fpga_data_pipeline.svg`, `fpga_data_pipeline.pdf`, `fpga_data_pipeline.png` | PARTIAL | 400 MHz capture, CFAR, host path not implemented |
| SD-03 | STM32 firmware architecture | main.cpp, main.h, LIB/* | `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_firmware_architecture.dot` | `stm32_firmware_architecture.svg`, `stm32_firmware_architecture.pdf`, `stm32_firmware_architecture.png` | PARTIAL | HAL/CMSIS/startup/linker/USB middleware absent |
| SD-04 | STM32 USB CDC flow | main.cpp, USBHandler.cpp, GUI_V5.py | `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_usb_cdc_flow.dot` | `stm32_usb_cdc_flow.svg`, `stm32_usb_cdc_flow.pdf`, `stm32_usb_cdc_flow.png` | PARTIAL | usbd_cdc_if.c missing; RX callback unbound |
| SD-05 | Python GUI modules (auto) | 9_Firmware/9_3_GUI/*.py via tools/gen_python_module_graph.py | `engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.dot` | `python_gui_modules.svg`, `python_gui_modules.pdf`, `python_gui_modules.png` | SOURCE-DERIVED | GUI_V1.py syntax error |
| SD-06 | Python GUI runtime architecture | GUI_V5.py, GUI_V6_Demo.py | `engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_architecture.dot` | `python_gui_architecture.svg`, `python_gui_architecture.pdf`, `python_gui_architecture.png` | SOURCE-DERIVED | not executed |
| SD-07 | End-to-end data flow | docs/SYSTEM, docs/FPGA, docs/STM32, PIN_MAP_FROM_SCHEMATIC.md | `engineering/SOFTWARE_DIAGRAMS/DATA_FLOW/end_to_end_data_flow.dot` | `end_to_end_data_flow.svg`, `end_to_end_data_flow.pdf`, `end_to_end_data_flow.png` | PARTIAL | FPGA→host path BLOCKED (FT601 unwired) |
| PCB-MAIN_BOARD-01 | Top-layer drawing | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD_top_layer.pdf`, `MAIN_BOARD_top_composite.svg` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-MAIN_BOARD-02 | Bottom-layer drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD_bottom_layer_mirrored.pdf`, `MAIN_BOARD_bottom_composite_mirrored.svg` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-MAIN_BOARD-03 | Copper-layer views (one page per layer) | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD_copper_layers.pdf` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-MAIN_BOARD-04 | Board-outline drawing | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD_outline.pdf`, `MAIN_BOARD-Edge_Cuts.svg` | SOURCE-DERIVED | thickness, tolerances |
| PCB-MAIN_BOARD-05 | Mechanical dimensions (DXF/STEP, hole table) | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/MECHANICAL/DXF/MAIN_BOARD_outline_holes_eagle.dxf` | `MAIN_BOARD_outline.dxf`, `MAIN_BOARD_board_only.step`, `MAIN_BOARD_dimensions.md` | SOURCE-DERIVED | thickness ASSUMED 1.6 mm; heights, mass |
| PCB-MAIN_BOARD-06 | Drill map + hole table + Excellon | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD-PTH-drl_map.pdf`, `MAIN_BOARD-NPTH-drl_map.pdf`, `MAIN_BOARD-PTH.drl`, `MAIN_BOARD-NPTH.drl`, `drill_report.txt` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-MAIN_BOARD-07 | Component placement / top assembly drawing | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD_assembly_top.pdf`, `MAIN_BOARD-F_Fab.svg` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-MAIN_BOARD-08 | Bottom assembly drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD_assembly_bottom_mirrored.pdf` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-MAIN_BOARD-09 | Fabrication package: Gerber set + stack-up document | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `MAIN_BOARD-job.gbrjob`, `MAIN_BOARD-F_Cu.gtl`, `MAIN_BOARD-B_Cu.gbl`, `MAIN_BOARD-Edge_Cuts.gm1`, `STACKUP.md` | PARTIAL | vendor notes: material, finish, thickness, impedance, tolerances |
| PCB-MAIN_BOARD-10 | BOM with references + pick-and-place | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch / .brd | `docs/BOM/BOM_MAIN_BOARD.csv` | `MAIN_BOARD_BOM.csv`, `MAIN_BOARD_pick_and_place.csv` | PARTIAL | 0 manufacturer part numbers in source |
| PCB-MAIN_BOARD-11 | DRC / IPC-2581 / 3-D renders / package README | 4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.brd (native EAGLE, editable) | `engineering/PCB/MAIN_BOARD/kicad/MAIN_BOARD.kicad_pcb` | `DRC_report.txt`, `README.md`, `MAIN_BOARD_render_top.png`, `MAIN_BOARD_render_isometric.png` | PARTIAL | layout unfinished (2 390 airwires; 15 unconnected after fill); stack-up, thickness, finish, MPNs |
| PCB-POWER_SUPPLY-01 | Top-layer drawing | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY_top_layer.pdf`, `POWER_SUPPLY_top_composite.svg` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-POWER_SUPPLY-02 | Bottom-layer drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY_bottom_layer_mirrored.pdf`, `POWER_SUPPLY_bottom_composite_mirrored.svg` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-POWER_SUPPLY-03 | Copper-layer views (one page per layer) | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY_copper_layers.pdf` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-POWER_SUPPLY-04 | Board-outline drawing | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY_outline.pdf`, `POWER_SUPPLY-Edge_Cuts.svg` | SOURCE-DERIVED | thickness, tolerances |
| PCB-POWER_SUPPLY-05 | Mechanical dimensions (DXF/STEP, hole table) | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/MECHANICAL/DXF/POWER_SUPPLY_outline_holes_eagle.dxf` | `POWER_SUPPLY_outline.dxf`, `POWER_SUPPLY_board_only.step`, `POWER_SUPPLY_dimensions.md` | SOURCE-DERIVED | thickness ASSUMED 1.6 mm; heights, mass |
| PCB-POWER_SUPPLY-06 | Drill map + hole table + Excellon | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY-PTH-drl_map.pdf`, `POWER_SUPPLY-NPTH-drl_map.pdf`, `POWER_SUPPLY-PTH.drl`, `POWER_SUPPLY-NPTH.drl`, `drill_report.txt` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-POWER_SUPPLY-07 | Component placement / top assembly drawing | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY_assembly_top.pdf`, `POWER_SUPPLY-F_Fab.svg` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-POWER_SUPPLY-08 | Bottom assembly drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY_assembly_bottom_mirrored.pdf` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-POWER_SUPPLY-09 | Fabrication package: Gerber set + stack-up document | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `POWER_SUPPLY-job.gbrjob`, `POWER_SUPPLY-F_Cu.gtl`, `POWER_SUPPLY-B_Cu.gbl`, `POWER_SUPPLY-Edge_Cuts.gm1`, `STACKUP.md` | PARTIAL | vendor notes: material, finish, thickness, impedance, tolerances |
| PCB-POWER_SUPPLY-10 | BOM with references + pick-and-place | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch / .brd | `docs/BOM/BOM_POWER_SUPPLY.csv` | `POWER_SUPPLY_BOM.csv`, `POWER_SUPPLY_pick_and_place.csv` | PARTIAL | 0 manufacturer part numbers in source |
| PCB-POWER_SUPPLY-11 | DRC / IPC-2581 / 3-D renders / package README | 4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.brd (native EAGLE, editable) | `engineering/PCB/POWER_SUPPLY/kicad/POWER_SUPPLY.kicad_pcb` | `DRC_report.txt`, `README.md`, `POWER_SUPPLY_render_top.png`, `POWER_SUPPLY_render_isometric.png` | PARTIAL | layout unfinished (309 airwires / 308 unconnected); final outline (G-10); stack-up; MPNs |
| PCB-RF_PA-01 | Top-layer drawing | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA_top_layer.pdf`, `RF_PA_top_composite.svg` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-RF_PA-02 | Bottom-layer drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA_bottom_layer_mirrored.pdf`, `RF_PA_bottom_composite_mirrored.svg` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-RF_PA-03 | Copper-layer views (one page per layer) | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA_copper_layers.pdf` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-RF_PA-04 | Board-outline drawing | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA_outline.pdf`, `RF_PA-Edge_Cuts.svg` | SOURCE-DERIVED | thickness, tolerances |
| PCB-RF_PA-05 | Mechanical dimensions (DXF/STEP, hole table) | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/MECHANICAL/DXF/RF_PA_outline_holes_eagle.dxf` | `RF_PA_outline.dxf`, `RF_PA_board_only.step`, `RF_PA_dimensions.md` | SOURCE-DERIVED | thickness ASSUMED 1.6 mm; heights, mass |
| PCB-RF_PA-06 | Drill map + hole table + Excellon | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA-PTH-drl_map.pdf`, `RF_PA-NPTH-drl_map.pdf`, `RF_PA-PTH.drl`, `RF_PA-NPTH.drl`, `drill_report.txt` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-RF_PA-07 | Component placement / top assembly drawing | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA_assembly_top.pdf`, `RF_PA-F_Fab.svg` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-RF_PA-08 | Bottom assembly drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA_assembly_bottom_mirrored.pdf` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-RF_PA-09 | Fabrication package: Gerber set + stack-up document | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `RF_PA-job.gbrjob`, `RF_PA-F_Cu.gtl`, `RF_PA-B_Cu.gbl`, `RF_PA-Edge_Cuts.gm1`, `STACKUP.md` | PARTIAL | vendor notes: material, finish, thickness, impedance, tolerances |
| PCB-RF_PA-10 | BOM with references + pick-and-place | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch / .brd | `docs/BOM/BOM_RF_PA.csv` | `RF_PA_BOM.csv`, `RF_PA_pick_and_place.csv` | PARTIAL | 0 manufacturer part numbers in source |
| PCB-RF_PA-11 | DRC / IPC-2581 / 3-D renders / package README | 4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.brd (native EAGLE, editable) | `engineering/PCB/RF_PA/kicad/RF_PA.kicad_pcb` | `DRC_report.txt`, `README.md`, `RF_PA_render_top.png`, `RF_PA_render_isometric.png` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (48) |
| PCB-FREQUENCY_SYNTHESIZER-01 | Top-layer drawing | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER_top_layer.pdf`, `FREQUENCY_SYNTHESIZER_top_composite.svg` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| PCB-FREQUENCY_SYNTHESIZER-02 | Bottom-layer drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER_bottom_layer_mirrored.pdf`, `FREQUENCY_SYNTHESIZER_bottom_composite_mirrored.svg` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| PCB-FREQUENCY_SYNTHESIZER-03 | Copper-layer views (one page per layer) | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER_copper_layers.pdf` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| PCB-FREQUENCY_SYNTHESIZER-04 | Board-outline drawing | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER_outline.pdf`, `FREQUENCY_SYNTHESIZER-Edge_Cuts.svg` | SOURCE-DERIVED | thickness, tolerances |
| PCB-FREQUENCY_SYNTHESIZER-05 | Mechanical dimensions (DXF/STEP, hole table) | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/MECHANICAL/DXF/FREQUENCY_SYNTHESIZER_outline_holes_eagle.dxf` | `FREQUENCY_SYNTHESIZER_outline.dxf`, `FREQUENCY_SYNTHESIZER_board_only.step`, `FREQUENCY_SYNTHESIZER_dimensions.md` | SOURCE-DERIVED | thickness ASSUMED 1.6 mm; heights, mass |
| PCB-FREQUENCY_SYNTHESIZER-06 | Drill map + hole table + Excellon | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER-PTH-drl_map.pdf`, `FREQUENCY_SYNTHESIZER-NPTH-drl_map.pdf`, `FREQUENCY_SYNTHESIZER-PTH.drl`, `FREQUENCY_SYNTHESIZER-NPTH.drl`, `drill_report.txt` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| PCB-FREQUENCY_SYNTHESIZER-07 | Component placement / top assembly drawing | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER_assembly_top.pdf`, `FREQUENCY_SYNTHESIZER-F_Fab.svg` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| PCB-FREQUENCY_SYNTHESIZER-08 | Bottom assembly drawing (mirrored) | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER_assembly_bottom_mirrored.pdf` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| PCB-FREQUENCY_SYNTHESIZER-09 | Fabrication package: Gerber set + stack-up document | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `FREQUENCY_SYNTHESIZER-job.gbrjob`, `FREQUENCY_SYNTHESIZER-F_Cu.gtl`, `FREQUENCY_SYNTHESIZER-B_Cu.gbl`, `FREQUENCY_SYNTHESIZER-Edge_Cuts.gm1`, `STACKUP.md` | PARTIAL | vendor notes: material, finish, thickness, impedance, tolerances |
| PCB-FREQUENCY_SYNTHESIZER-10 | BOM with references + pick-and-place | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch / .brd | `docs/BOM/BOM_FREQUENCY_SYNTHESIZER.csv` | `FREQUENCY_SYNTHESIZER_BOM.csv`, `FREQUENCY_SYNTHESIZER_pick_and_place.csv` | PARTIAL | 0 manufacturer part numbers in source |
| PCB-FREQUENCY_SYNTHESIZER-11 | DRC / IPC-2581 / 3-D renders / package README | 4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd (native EAGLE, editable) | `engineering/PCB/FREQUENCY_SYNTHESIZER/kicad/FREQUENCY_SYNTHESIZER.kicad_pcb` | `DRC_report.txt`, `README.md`, `FREQUENCY_SYNTHESIZER_render_top.png`, `FREQUENCY_SYNTHESIZER_render_isometric.png` | SOURCE-DERIVED | stack-up/material, finish, tolerances, MPNs; designer review of DRC (639) |
| MECH-PLAN-01 | PCB set plan view 1:1 | 4 × .brd layer 20 + holes | `engineering/MECHANICAL/CAD/pcb_set_plan_view.svg` | `pcb_set_plan_view.pdf`, `pcb_set_plan_view.png` | SOURCE-DERIVED | placement is for comparison only |
| MECH-ENC-01 | Main enclosure drawings | none (README references a non-existent 10_docs/Hardware/Enclosure) | — (none) | — | BLOCKED — MISSING DATA | all enclosure geometry (G-04) |
| MECH-INT-01 | Internal component layout / cable routing | none | — (none) | — | BLOCKED — MISSING DATA | board placement, stacking, harness (G-05, G-09) |
| MECH-ANT-01 | Antenna assembly drawing | 02_hardware/04_antenna_beamforming.md (spacing only), photo | — (none) | — | BLOCKED — MISSING DATA | element geometry, feed, mounting (G-06) |
| MECH-COOL-01 | Cooling and power assembly drawing | none (PA dissipation implied by xlsx) | — (none) | — | BLOCKED — MISSING DATA | heatsink/fan geometry (G-08) |
| MECH-PED-01 | Pedestal / azimuth drive drawing | firmware constants only | — (none) | — | BLOCKED — MISSING DATA | G-07 |
| ASM-EXP-01 | Exploded assembly view (electronics set) | 4 × .brd outlines; interconnection table; antenna spacing doc | `engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.svg` | `aeris10_exploded_conceptual.pdf`, `aeris10_exploded_conceptual.png` | CONCEPTUAL | stacking, spacing, fasteners, enclosure, antenna, host |
| ASM-PL-01 | Parts list | BOMs + connector matrix + firmware | `engineering/ASSEMBLY/PARTS_LIST.md` | — | PARTIAL | all off-board part numbers |
| ASM-SEQ-01 | Assembly / integration sequence | connector matrix, power sequence (power_rails.md) | `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` | — | PARTIAL | mechanical steps CONCEPTUAL; conflicts K1–K8 |
| DSN-00 | Design basis, decisions D-01…D-15, parameter file | verified repo constraints + decisions | `engineering/DESIGN/00_DESIGN_BASIS.md` | `design_parameters.json` | PROPOSED DESIGN | owner approval of D-01…D-15 |
| DSN-ANT-01 | 16×8 microstrip patch array panel (native KiCad PCB, calc sheet, openEMS model) | f0, pitch, 8×16 from docs; RO4350B datasheet; decisions D-01…D-06 | `engineering/DESIGN/ANTENNA/kicad/aeris10_patch_array.kicad_pcb` | `aeris10_patch_array_layout.svg`, `aeris10_patch_array_layout.pdf`, `ANTENNA_DESIGN_CALC.md`, `openems_patch_row.py`, `aeris10_patch_array_top.pdf`, `aeris10_patch_array.step`, `aeris10_patch_array_render_top.png`, `aeris10_patch_array-job.gbrjob` | PROPOSED DESIGN | EM simulation + coupon measurement (not run: openEMS absent); chirp bandwidth B TBD; connector footprint |
| DSN-THM-01 | Thermal budget + 22 V supply sizing | firmware timing, QPA2962 datasheet, D-10/D-11/D-14 | `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` | `thermal_summary.json` | PROPOSED DESIGN | PA-board via-field Rth, fan selection, per-rail currents |
| DSN-PSU-01 | 22 V PA drain supply, enable switch, per-PA pulse gating (block schematic, BOM, nets) | D-14; xlsx VIN; main.h EN pin | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.svg` | `DSN-PSU-01_block_schematic.pdf`, `DSN-PSU-01_BOM.csv`, `DSN-PSU-01_netlist.csv`, `README.md` | PROPOSED DESIGN | TX_GATE FPGA pin, PGOOD MCU pin, component-level capture (MDR-12) |
| DSN-MECH-3D | Radar head + pedestal parametric 3-D model (FreeCAD native, STEP, STL, DXF page, mass table) | board outlines/holes (verified), D-07…D-13 | `engineering/DESIGN/MECHANICAL/CAD/aeris10_head_pedestal.FCStd` | `aeris10_head_pedestal.step`, `aeris10_head_only.step`, `aeris10_pedestal_only.step`, `aeris10_head.stl`, `aeris10_pedestal.stl`, `aeris10_orthographic.dxf`, `aeris10_mass_table.json`, `aeris10_head_pedestal_iso.svg`, `aeris10_head_xray_iso.svg`, `aeris10_head_xray_iso.png` | PROPOSED DESIGN | component heights (G-02), fasteners, sheet-metal detailing, sealing, mast interface |
| DSN-MECH-01 | Head plan section | tools/design_layout.py (D-07…D-13) + KiCad P&P | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-01_head_plan_section.svg` | `DSN-MECH-01_head_plan_section.png`, `DSN-MECH-01-05_head_pedestal_drawings.pdf` | PROPOSED DESIGN | as DSN-MECH-3D |
| DSN-MECH-02 | Head front elevation | tools/design_layout.py (D-07…D-13) + KiCad P&P | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-02_head_front_elevation.svg` | `DSN-MECH-02_head_front_elevation.png`, `DSN-MECH-01-05_head_pedestal_drawings.pdf` | PROPOSED DESIGN | as DSN-MECH-3D |
| DSN-MECH-03 | Head side section incl. pedestal | tools/design_layout.py (D-07…D-13) + KiCad P&P | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-03_head_side_section.svg` | `DSN-MECH-03_head_side_section.png`, `DSN-MECH-01-05_head_pedestal_drawings.pdf` | PROPOSED DESIGN | as DSN-MECH-3D |
| DSN-MECH-04 | Internal layout per tier with connector positions | tools/design_layout.py (D-07…D-13) + KiCad P&P | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-04_internal_layout_rear.svg` | `DSN-MECH-04_internal_layout_rear.png`, `DSN-MECH-01-05_head_pedestal_drawings.pdf` | PROPOSED DESIGN | as DSN-MECH-3D |
| DSN-MECH-05 | Pedestal plan | tools/design_layout.py (D-07…D-13) + KiCad P&P | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-05_pedestal_plan.svg` | `DSN-MECH-05_pedestal_plan.png`, `DSN-MECH-01-05_head_pedestal_drawings.pdf` | PROPOSED DESIGN | as DSN-MECH-3D |
| DSN-LINK-01 | FPGA → host data path: option A FT601 pin plan (bank 35) + option B SPI bridge (RTL, STM32 driver, GUI parser) | Main Board netlist (free bank-35 pins, DIG_5..7, SPI1), RTL geometry, firmware timing | `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` | `ft601_pin_assignment.csv`, `ft601_bank35.xdc`, `ft601_added_parts_BOM.csv`, `option_b_signal_map.csv`, `rd_map_packer.v`, `host_bridge_spi.v`, `tb_host_bridge.v`, `host_bridge.c`, `bridge_frame.py`, `README.md` | PROPOSED DESIGN | option A needs Main Board rev. B + FT601 datasheet checks; option B bench test; packer integration into beta/fpga |
| DSN-ANT-01-SIM | openEMS simulation of one antenna row (S11, directivity, tuning log) | openems_patch_row.py run with openEMS built from source | `engineering/DESIGN/ANTENNA/simulation/TUNING_LOG.md` | `s11.csv`, `s11_row.png`, `tuning_result.json` | PROPOSED DESIGN | 16-row coupling, squint vs. frequency, measurement |
| DSN-MECH-3D-DETAIL | Detailed enclosure + pedestal model: 51 parts (tray, front plate, lid, window + gasket + frame, PA plate with brackets, carrier rails, standoffs, gland plate, bearing, pulleys, slip ring, motor bracket, mast flange) | tools/design_layout.py + PCB hole tables + D-07…D-13 | `engineering/DESIGN/MECHANICAL/CAD/detail/aeris10_enclosure_detail.FCStd` | `aeris10_enclosure_detail.step`, `aeris10_head_detail.step`, `aeris10_pedestal_detail.step`, `parts_list.json`, `aeris10_detail_xray_front_iso.png`, `aeris10_detail_iso_rear.png`, `aeris10_detail_isometrics.pdf` | PROPOSED DESIGN | bend reliefs, welds, lid stiffening, fan brackets, earthing, mast interface; part numbers for bearing/slip ring/glands |
| DSN-MECH-06 | Sheet-metal flat patterns with bend lines (tray, front plate, lid) | detail model, BA = π/2·(R + K·t) | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-06_sheet_metal_flat_patterns.svg` | `DSN-MECH-06_sheet_metal_flat_patterns.png`, `DSN-MECH-06-07_enclosure_detail.pdf` | PROPOSED DESIGN | CAM check of bend allowance/reliefs |
| DSN-MECH-07 | Assembly section with fastener balloons | detail model | `engineering/DESIGN/MECHANICAL/drawings/DSN-MECH-07_assembly_section_fasteners.svg` | `DSN-MECH-07_assembly_section_fasteners.png`, `MECHANICAL_PARTS_LIST.md` | PROPOSED DESIGN | as DSN-MECH-3D-DETAIL |
| DSN-HAR-01 | Harness schedule with computed lengths (144 cables) | interconnection_table.md + P&P + proposed layout | `engineering/DESIGN/HARNESS/harness_schedule.csv` | `HARNESS_SCHEDULE.md` | PROPOSED DESIGN | Power-rail pairs not matched by net name; stepper driver location; PA-instance mapping |
| ASM-DRW-01 | Assembly drawings (per board) | KiCad fab/silk plots | `engineering/ASSEMBLY/ASSEMBLY_DRAWINGS/README.md` | — | SOURCE-DERIVED | component heights; bottom views mirrored only |

### Summary

| Status | Drawings |
|---|---|
| BLOCKED | 5 |
| CONCEPTUAL | 1 |
| PARTIAL | 28 |
| PROPOSED | 16 |
| SOURCE-DERIVED | 39 |
| **Total registered** | 89 |

Existing drawings found in the repository before this work: `2_Functional Diagram…/RADAR_V6.drawio` (+ .jpg, .dwg) system block diagram; `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` (unlabelled stack-up); `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/` (P&P + BOM xlsx); `8_Utils/*.jpg` photographs; `docs/MECHANICAL/drawings/*_outline.svg` (first reconstruction). None of them is a dimensioned engineering drawing.

### File check (2026-10-09)

Checked 333 registered files (existence, non-empty, SVG/PDF/DOT well-formed): **333 OK, 0 problems**.


---

<!-- chapter B: Parts lists (PCB BOM summaries, mechanical parts, fasteners), cable schedule -->
# B. Parts lists and cable schedule

**Appendix status summary:** PCB BOM summaries — PARTIAL (generated from the schematics, 0 MPN in the source; BETA MPN proposals with confidence classes); mechanical parts list — PROPOSED DESIGN (DSN-MECH-PL Rev A, masses are volume × density estimates); cable schedule — PROPOSED DESIGN (DSN-HAR-01 Rev A, lengths are Manhattan estimates to be cut after a first fit). No part in this appendix has been purchased, fitted or measured. Compiled by Antidrone Ukraine · antidrone.cc.

**Sources:** `docs/BOM/README.md`, `docs/BOM/BOM_<BOARD>.csv`; `beta/pcb/README.md`, `beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`; `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md`; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, `harness_schedule.csv`.

## B.1 PCB bills of materials

Generated 2026-10-08 by `python3 tools/gen_eagle_bom.py` directly from the EAGLE schematics (no EAGLE run); regenerate after any schematic change with the commands in `docs/BOM/README.md`. Columns of `BOM_<BOARD>.csv`: `item, qty, value, deviceset, device, package, library, mpn_attribute, manufacturer_attribute, mpn_candidate, mpn_status, references`; `REFS_<BOARD>.csv` has one row per reference designator (source: `docs/BOM/README.md` §What is in each file).

Summary copied from `docs/BOM/README.md` §Summary:

| Board | Physical references | Line items | Lines with MPN attribute | References without value | Status |
|---|---:|---:|---:|---:|---|
| Main Board | 776 | 98 | 0 | 244 | INCOMPLETE — no MPNs, FT601 (U6) unconnected but listed, 11 parts parked off-board |
| Power Supply | 312 | 28 | 0 | 80 | INCOMPLETE — no MPNs, 132 parts not placed on the board |
| RF PA | 25 | 11 | 0 | 6 | INCOMPLETE — no MPNs; `QPA2962_B` is a deviceset name |
| Frequency Synthesizer | 184 | 40 | 0 | 47 | INCOMPLETE — matches the existing `Clocks_Freq_Synth_board_BOM.xlsx` (40 lines) which also has empty MPN columns |

`mpn_status` meaning (same source): `VERIFIED (attribute)` — an explicit MPN attribute exists in the schematic (none today); `UNVERIFIED (deviceset name)` — the EAGLE deviceset name looks like a part number but has not been checked against a distributor; `GENERIC — value/package only` — passive to be sourced by value/package/tolerance (tolerance and voltage rating are not in the schematics).

BETA MPN proposals (`beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv`, columns `manufacturer, mpn, mpn_confidence, dnp, note`; lines / quantity; source: `beta/pcb/README.md` §BOM confidence, line counts re-counted from the CSV files on 2026-10-09):

| Board | HIGH (deviceset = MPN) | MEDIUM (standard passive from value+package) | LOW (guess / non-standard value / conflict) | EMPTY (no value in the source) |
|---|---|---|---|---|
| Main Board | 23 / 204 | 41 / 461 | 30 / 93 | 4 / 18 |
| Power Supply | 7 / 79 | 18 / 225 | 3 / 8 | 0 / 0 |
| RF PA | 5 / 6 | 6 / 19 | 0 / 0 | 0 / 0 |
| Frequency Synthesizer | 10 / 37 | 22 / 110 | 6 / 29 | 2 / 8 |

The RF PA quantities are per board; the AERIS-10X variant uses 16 boards (source: `docs/PCB/RF_PA.md` §2). Chapters 4–7 §BOM summary list the conflicts flagged per board.

System-level items not on any PCB (source: `docs/BOM/README.md` §System-level items; quantities and part numbers UNKNOWN unless stated):

| Item | Evidence | Part number |
|---|---|---|
| GPS module (NMEA 9600 on UART5) | `main.cpp:2143-2170`; xlsx "NEO-6M" | NEO-6M (xlsx only) |
| IMU GY-85 (ADXL345/ITG3205/HMC5883L, I2C3) | `GY_85_HAL.c`; xlsx | GY-85 module |
| Barometer BMP180 (I2C3) | `BMP180.cpp`; xlsx | BMP180 |
| Temperature sensors TMP37 ×8 via ADS7830 | `main.cpp:1752-1775`; xlsx | TMP37 |
| Stepper motor 200 steps/rev + driver | `main.cpp:195`; xlsx "TBS6600 [9-42 V]" (TB6600-class) | motor UNKNOWN |
| Slip ring | `README.md:86`; `Project_Description.docx` | UNKNOWN |
| Cooling fans | `main.h:142` `EN_DIS_COOLING`; xlsx "COOLING SYSTEM" | UNKNOWN |
| Antenna array (8×16 patch or 32×16 slotted waveguide) | `README.md:82-83` | no CAD, no part |
| Enclosure | `README.md:143` (missing path) | none |
| Inter-board cables: SMA (37 + 11 + 2 ports), Molex 22-23-20xx (56 + 34 + 6 + 2 headers) | schematics | cable assemblies not defined |

The proposed designs of chapters 8–10 and the harness schedule below replace the last five rows with PROPOSED parts; the 22 V supply module BOM is `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/` (chapter 9).

## B.2 Mechanical parts list — DSN-MECH-PL Rev A (PROPOSED DESIGN)

Copied verbatim from `engineering/DESIGN/MECHANICAL/MECHANICAL_PARTS_LIST.md` (date 2026-10-09, from `CAD/detail/parts_list.json`, FreeCAD model `tools/design_enclosure_detail_freecad.py`; masses are volume × density estimates). Head ≈ 6.4 kg (structure only, PCBs/antenna not included except as noted), pedestal ≈ 12.4 kg (incl. stepper 1.1 kg, bearing/slip ring as modelled) (same source).

| # | Group | Part | Material | Mass (g) | Fasteners | Note |
|---|---|---|---|---|---|---|
| 1 | HEAD | Tray — base + sides + rear, 2.5 mm Al 5754, 3 bends R2.5, flanges 15 mm with M4 PEM nuts | Al | 1559 | PEM S-M4-1 ×18 | 8 lid holes M4, 10 front-plate holes M4, Ø70 cable entry, intake slots |
| 2 | HEAD | Front plate 2.5 mm Al with radome window opening and intake louvres | Al | 346 | M4×8 ×10 to tray front flanges | window 175×258, 16 M3 clamp holes |
| 3 | HEAD | Radome window PTFE 2 mm (outside the front plate) | PTFE | 246 |  | RF loss ≈ 0.1 dB at 10.5 GHz (PTFE εr 2.1, tanδ 0.0002 — to be confirmed) |
| 4 | HEAD | Window gasket EPDM 1.5 mm (ring 10 mm) | EPDM | 17 |  |  |
| 5 | HEAD | Window clamp frame 2 mm Al, 14 mm wide | Al | 69 | M3×10 ×16 + nyloc |  |
| 6 | HEAD | Lid 2.5 mm Al with exhaust slots | Al | 272 | M4×8 ×8 |  |
| 7 | HEAD | Lid gasket EPDM 3 mm self-adhesive, 15 mm wide on the flanges | EPDM | 44 |  | compressed to 2 mm → IP54 target |
| 8 | HEAD | PA heat spreader 300×300×10 Al 6061, machined fin fields, M3 tapped (16×7 PA + 6 antenna) | Al | 3400 | M3×6 ×118 (PA 112 + antenna 6) | thermal pads 5×5 under each QPA2962; antenna on 2.4 mm nylon spacers |
| 9 | HEAD | Plate bracket L 25×25×3 Al at x=5 z=20 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 10 | HEAD | Plate bracket L 25×25×3 Al at x=5 z=265.0 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 11 | HEAD | Plate bracket L 25×25×3 Al at x=280 z=20 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 12 | HEAD | Plate bracket L 25×25×3 Al at x=280 z=265.0 | Al | 26 | M5×12 ×2 + M5×16 ×1 | bolts the plate to the side wall and to the front flange |
| 13 | HEAD | Main Board carrier rail bottom U15×12×1.5 Al, 280 mm | Al | 42 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 14 | HEAD | Main Board carrier rail top U15×12×1.5 Al, 280 mm | Al | 42 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 15 | HEAD | Main Board standoff M3×10 hex at (4,4) | steel | 2 | M3×6 ×1 |  |
| 16 | HEAD | Main Board standoff M3×10 hex at (256,4) | steel | 2 | M3×6 ×1 |  |
| 17 | HEAD | Main Board standoff M3×10 hex at (116,114) | steel | 2 | M3×6 ×1 |  |
| 18 | HEAD | Main Board standoff M3×10 hex at (256,114) | steel | 2 | M3×6 ×1 |  |
| 19 | HEAD | Main Board standoff M3×10 hex at (116,250) | steel | 2 | M3×6 ×1 |  |
| 20 | HEAD | Main Board standoff M3×10 hex at (256,250) | steel | 2 | M3×6 ×1 |  |
| 21 | HEAD | Main Board standoff M3×10 hex at (4,296) | steel | 2 | M3×6 ×1 |  |
| 22 | HEAD | Main Board standoff M3×10 hex at (256,296) | steel | 2 | M3×6 ×1 |  |
| 23 | HEAD | Synth carrier rail bottom U15×12×1.5 Al, 120 mm | Al | 18 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 24 | HEAD | Synth carrier rail top U15×12×1.5 Al, 120 mm | Al | 18 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 25 | HEAD | Synth standoff M3×10 hex at (5,5) | steel | 2 | M3×6 ×1 |  |
| 26 | HEAD | Synth standoff M3×10 hex at (95,5) | steel | 2 | M3×6 ×1 |  |
| 27 | HEAD | Synth standoff M3×10 hex at (5,95) | steel | 2 | M3×6 ×1 |  |
| 28 | HEAD | Synth standoff M3×10 hex at (95,95) | steel | 2 | M3×6 ×1 |  |
| 29 | HEAD | Power Board carrier rail bottom U15×12×1.5 Al, 300 mm | Al | 44 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 30 | HEAD | Power Board carrier rail top U15×12×1.5 Al, 300 mm | Al | 44 | M4×8 ×2 | bolted to the side walls (M4) — spans the full width when the board is narrower |
| 31 | HEAD | Power Board standoff M3×10 hex at (10,10) | steel | 2 | M3×6 ×1 |  |
| 32 | HEAD | Power Board standoff M3×10 hex at (140,10) | steel | 2 | M3×6 ×1 |  |
| 33 | HEAD | Power Board standoff M3×10 hex at (270,10) | steel | 2 | M3×6 ×1 |  |
| 34 | HEAD | Power Board standoff M3×10 hex at (10,120) | steel | 2 | M3×6 ×1 |  |
| 35 | HEAD | Power Board standoff M3×10 hex at (270,120) | steel | 2 | M3×6 ×1 |  |
| 36 | HEAD | Power Board standoff M3×10 hex at (10,230) | steel | 2 | M3×6 ×1 |  |
| 37 | HEAD | Power Board standoff M3×10 hex at (270,230) | steel | 2 | M3×6 ×1 |  |
| 38 | HEAD | Power Board standoff M3×10 hex at (138,268) | steel | 2 | M3×6 ×1 |  |
| 39 | HEAD | Cable-entry gland plate 100×100×2 Al under the base (M32 + M20 glands) | Al | 48 | M4×8 ×4; glands M32 + M20 IP68 | harness from the slip ring: VIN, 22 V, USB |
| 40 | PEDESTAL | Turntable plate Ø340×8 Al, 8×M6 to the head base, 12×M6 to the bearing outer ring | Al | 1864 | M6×16 ×8, M6×25 ×12 |  |
| 41 | PEDESTAL | Slewing bearing OD190/ID100×20 (4-point contact, e.g. igus PRT-04-100 class) | steel | 3218 |  | part number to be selected (axial ≥ 50 kg, moment ≥ 60 N·m) |
| 42 | PEDESTAL | Ring pulley GT3 180T Ø172 Al (machined/3D-printed), clamped under the turntable | Al | 0 | M4×10 ×6 |  |
| 43 | PEDESTAL | Pedestal top plate 360×360×5 Al, 12×M6 to the bearing inner ring, bore Ø90 | Al | 1658 | M6×20 ×12 |  |
| 44 | PEDESTAL | Pedestal housing 360×360×125 folded 2.5 mm Al (4 bends), open top, connector panel cut-out | Al | 1575 | M5×10 ×12 to the top plate | DC input (XT60/M12), USB-B bulkhead, vent |
| 45 | PEDESTAL | Stepper NEMA 23 76 mm | steel | 1898 | M5×12 ×4 |  |
| 46 | PEDESTAL | Motor bracket 80×80×3 Al with slotted belt-tension holes | Al | 41 | M5×10 ×4 to the top plate | slots ±5 mm for GT3 tension |
| 47 | PEDESTAL | Motor pulley GT3 60T Ø57, bore 6.35 | Al | 84 | grub M4 ×2 |  |
| 48 | PEDESTAL | Through-bore slip ring Ø99×60, bore 60, 12 circuits (4×10 A, 4×10 A, 4 signal) | plastic | 351 |  | e.g. Senring H3899 class — select |
| 49 | PEDESTAL | Slip-ring stator bracket 140×140×3 Al | Al | 95 | M4×8 ×4 | stator fixed to the pedestal, rotor flange to the turntable |
| 50 | PEDESTAL | Stepper driver TB6600 on DIN rail | plastic | 299 |  |  |
| 51 | PEDESTAL | Mast flange Ø150×10 steel, 4×M10 PCD 110 (ASSUMPTION — mast interface undefined) | steel | 1360 | M10×30 ×4 |  |

Fastener totals from the per-part lists (same source):

| Fastener | Qty |
|---|---|
| M10×30 | 4 |
| M3×10 | 16 |
| M3×6 | 138 |
| M4 | 2 |
| M4×10 | 6 |
| M4×8 | 38 |
| M5×10 | 16 |
| M5×12 | 12 |
| M5×16 | 4 |
| M6×16 | 8 |
| M6×20 | 12 |
| M6×25 | 12 |
| S-M4-1 | 18 |

Sealing and finish (same source): lid EPDM 15 × 3 mm self-adhesive gasket on the three top flanges, compressed to 2 mm by the M4 screws (pitch 60 mm); front plate 1.5 mm EPDM strip on the two front flanges; radome window PTFE 2 mm clamped by the 2 mm Al frame with EPDM 1.5 mm gasket, M3 × 18 (alternative 2 mm Rogers/ABS radome); cable entry 100 × 100 gland plate under the base with M32 (power) and M20 (USB) IP68 glands; finish chromate conversion (Alodine) + powder coat RAL 7035 outside, bare chromate inside for grounding at the flanges, PA plate bare 6061 with thermal pads. Open: bend reliefs and corner welds of the tray, stiffeners of the 315 mm lid, fan mounting brackets, antenna spacer material, earthing stud, lifting points, mast interface (row 51 is an ASSUMPTION).

## B.3 Cable schedule — DSN-HAR-01 Rev A (PROPOSED DESIGN)

Generated by `tools/design_mechanical_drawings.py` from the proposed layout (`tools/design_layout.py`) and the connector positions in the KiCad P&P files. Length = Manhattan distance between connector positions in the head + service allowance (40 mm coax / 60 mm wire), rounded up to 10 mm; lengths are PROPOSED, cut after a first fit (source: `HARNESS_SCHEDULE.md` header). Totals stated there: **144 cables; coax 55; wire 89; total proposed length ≈ 41.6 m**. Re-counted from `harness_schedule.csv` on 2026-10-09: 144 rows, 55 coax / 89 wire, sum of numeric lengths 41600 mm, 14 rows with length TBD (CBL-001, CBL-006, CBL-007, CBL-008, CBL-010, CBL-012, CBL-013, CBL-014, CBL-016, CBL-024, CBL-025, CBL-027, CBL-028, CBL-144).

Cable types (count from `harness_schedule.csv`, column `cable_type`):

| Count | Cable type |
|---|---|
| 32 | coax RG-405 SMA-SMA, EQUAL LENGTH set |
| 21 | 2-wire 20 AWG, Molex 22-01-2027 both ends |
| 16 | 2-wire 24 AWG shielded, Molex 22-01-2027 |
| 16 | 3-wire 24 AWG twisted, Molex 22-01-3037 |
| 16 | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set |
| 16 | 2-wire 18 AWG twisted, AK300/2 screw terminal |
| 13 | 2-wire 20 AWG |
| 7 | coax RG-405 (0.086") SMA-SMA, phase-stable |
| 2 | ribbon/discrete 26 AWG, 2.54 mm housings |
| 2 | 2 × 2-wire 16 AWG |
| 1 | 20-way 1.27 mm IDC ribbon |
| 1 | USB 2.0 shielded, mini-B |
| 1 | 3-wire 24 AWG shielded |

Signal groups: 16 × each of `VG_n` gate bias, drain-current sense, RF to PA RFIN, RF from PA RFOUT, RF to antenna row n, 22 V pulsed drain (CBL-045…CBL-140, six cables per PA); 34 Power Board rail cables (CBL-001…CBL-034, 13 of them TBD because no connector on the Main/Synth board carries the same net name — resolve with `engineering/SYSTEM/interfaces/interconnection_table.md`); the enable bus (CBL-035, 20-way IDC); 7 Synth → Main coax (CBL-036…CBL-042, RG-405 phase-stable); 2 control-header cables (CBL-043/044); slip-ring VIN, 22 V boost input and USB (CBL-141…CBL-143); stepper STEP/DIR/EN (CBL-144, DECISION NEEDED: driver on the fixed base needs 3 more slip-ring circuits, or move the driver into the head).

Caveats carried in the `note` column: PA instance ↔ `VG_n` assignment PROPOSED (n = n, not documented in CAD); Main sense connector ↔ PA n PROPOSED; which SMA of each Main Board pair is RFIN/RFOUT is UNVERIFIED (`interconnection_table.md` §7); antenna row n ↔ PA n PROPOSED, equal length mandatory for elevation phase. Note that the cable IDs of this schedule (CBL-001…CBL-144) are the DSN-HAR-01 numbering; the interconnection table of chapter 3 uses its own earlier CBL-xx numbering.

### B.3.1 Full schedule (copied verbatim from `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`)

| ID | From | To | Signal | Cable | Length (mm) | Note |
|---|---|---|---|---|---|---|
| CBL-001 | POWER_SUPPLY X2 | ? ? | +5V0_1 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-002 | POWER_SUPPLY X3 | MAIN_BOARD X55 | +5V5_PA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 780 | rail name matched in both netlists |
| CBL-003 | POWER_SUPPLY X4 | MAIN_BOARD X8 | +1V0_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 310 | rail name matched in both netlists |
| CBL-004 | POWER_SUPPLY X5 | MAIN_BOARD X10 | +1V8_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 340 | rail name matched in both netlists |
| CBL-005 | POWER_SUPPLY X6 | FREQUENCY_SYNTHESIZER X15 | +5V0_LO | 2-wire 20 AWG, Molex 22-01-2027 both ends | 960 | rail name matched in both netlists |
| CBL-006 | POWER_SUPPLY X7 | ? ? | +3V3_LO_2 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-007 | POWER_SUPPLY X8 | ? ? | +3V3_LO_1 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-008 | POWER_SUPPLY X9 | ? ? | +5V0_2 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-009 | POWER_SUPPLY X10 | MAIN_BOARD X17 | +1V8_CLOCK | 2-wire 20 AWG, Molex 22-01-2027 both ends | 840 | rail name matched in both netlists |
| CBL-010 | POWER_SUPPLY X11 | ? ? | +3V3_CLOCK | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-011 | POWER_SUPPLY X12 | MAIN_BOARD X56 | +3V3_AN | 2-wire 20 AWG, Molex 22-01-2027 both ends | 380 | rail name matched in both netlists |
| CBL-012 | POWER_SUPPLY X13 | ? ? | +5V0_ADAR | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-013 | POWER_SUPPLY X14 | ? ? | +3V3_ADAR_12 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-014 | POWER_SUPPLY X15 | ? ? | +3V3_ADAR_34 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-015 | POWER_SUPPLY X16 | MAIN_BOARD X24 | +3V3 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 200 | rail name matched in both netlists |
| CBL-016 | POWER_SUPPLY X17 | ? ? | +5V0_3 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-017 | POWER_SUPPLY X18 | MAIN_BOARD X6 | -3V3_SW | 2-wire 20 AWG, Molex 22-01-2027 both ends | 310 | rail name matched in both netlists |
| CBL-018 | POWER_SUPPLY X19 | MAIN_BOARD X19 | -5V5_PA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 380 | rail name matched in both netlists |
| CBL-019 | POWER_SUPPLY X20 | MAIN_BOARD X15 | -5V0_ADAR34 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 240 | rail name matched in both netlists |
| CBL-020 | POWER_SUPPLY X21 | MAIN_BOARD X13 | -5V0_ADAR12 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 360 | rail name matched in both netlists |
| CBL-021 | POWER_SUPPLY X22 | MAIN_BOARD X18 | +5V0_0 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 400 | rail name matched in both netlists |
| CBL-022 | POWER_SUPPLY X23 | MAIN_BOARD X1 | +3V4 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 360 | rail name matched in both netlists |
| CBL-023 | POWER_SUPPLY X24 | MAIN_BOARD X11 | -3V4 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 330 | rail name matched in both netlists |
| CBL-024 | POWER_SUPPLY X25 | ? ? | +5V0_4 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-025 | POWER_SUPPLY X26 | ? ? | +5V0_ADTR | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-026 | POWER_SUPPLY X27 | MAIN_BOARD X16 | +3V3_FPGA | 2-wire 20 AWG, Molex 22-01-2027 both ends | 430 | rail name matched in both netlists |
| CBL-027 | POWER_SUPPLY X28 | ? ? | +5V0_5 | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-028 | POWER_SUPPLY X29 | ? ? | +3V3_SW | 2-wire 20 AWG | TBD | no connector with this net name on Main/Synth (rail renamed through a filter/inductor or spare output) — resolve with interconnection_table.md |
| CBL-029 | POWER_SUPPLY X30 | MAIN_BOARD X12 | +3V3_VDD_SW | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1090 | rail name matched in both netlists |
| CBL-030 | POWER_SUPPLY X31 | MAIN_BOARD X14 | +5V0_PA_1 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1180 | rail name matched in both netlists |
| CBL-031 | POWER_SUPPLY X32 | MAIN_BOARD X5 | +5V0_PA_2 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1310 | rail name matched in both netlists |
| CBL-032 | POWER_SUPPLY X33 | MAIN_BOARD X7 | +5V0_PA_3 | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1020 | rail name matched in both netlists |
| CBL-033 | POWER_SUPPLY X34 | MAIN_BOARD X4 | +3V3_ADTR | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1120 | rail name matched in both netlists |
| CBL-034 | POWER_SUPPLY X35 | FREQUENCY_SYNTHESIZER X4 | +3V3_XO | 2-wire 20 AWG, Molex 22-01-2027 both ends | 1030 | rail name matched in both netlists |
| CBL-035 | POWER_SUPPLY SV1 | MAIN_BOARD SV1 | enable bus (15 EN + GND) | 20-way 1.27 mm IDC ribbon | 320 |  |
| CBL-036 | FREQUENCY_SYNTHESIZER J7 | MAIN_BOARD J1 | 100 MHz FPGA sys clk | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-037 | FREQUENCY_SYNTHESIZER J5 | MAIN_BOARD J20 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 170 | mapping from interconnection_table.md §6 |
| CBL-038 | FREQUENCY_SYNTHESIZER J6 | MAIN_BOARD J18 | 120 MHz DAC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-039 | FREQUENCY_SYNTHESIZER J3 | MAIN_BOARD J21 | 400 MHz ADC | coax RG-405 (0.086") SMA-SMA, phase-stable | 120 | mapping from interconnection_table.md §6 |
| CBL-040 | FREQUENCY_SYNTHESIZER J10 | MAIN_BOARD J23 | LO TX | coax RG-405 (0.086") SMA-SMA, phase-stable | 100 | mapping from interconnection_table.md §6 |
| CBL-041 | FREQUENCY_SYNTHESIZER J11 | MAIN_BOARD J22 | LO RX | coax RG-405 (0.086") SMA-SMA, phase-stable | 140 | mapping from interconnection_table.md §6 |
| CBL-042 | FREQUENCY_SYNTHESIZER J4 | MAIN_BOARD J19 | test | coax RG-405 (0.086") SMA-SMA, phase-stable | 100 | mapping from interconnection_table.md §6 |
| CBL-043 | FREQUENCY_SYNTHESIZER JP1 | MAIN_BOARD JP1 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 210 |  |
| CBL-044 | FREQUENCY_SYNTHESIZER JP2 | MAIN_BOARD JP13 | control header | ribbon/discrete 26 AWG, 2.54 mm housings | 240 |  |
| CBL-045 | MAIN_BOARD X_7 | RF_PA PA1 X2 | VG_1 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 150 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-046 | MAIN_BOARD X3 | RF_PA PA1 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 150 | Main sense connector ↔ PA n PROPOSED |
| CBL-047 | MAIN_BOARD J27 | RF_PA PA1 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 330 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-048 | MAIN_BOARD J26 | RF_PA PA1 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-049 | RF_PA PA1 J2 | ANTENNA ROW1 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 100 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-050 | DSN-PSU-01 OUT1 | RF_PA PA1 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 510 |  |
| CBL-051 | MAIN_BOARD X_16 | RF_PA PA2 X2 | VG_2 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 140 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-052 | MAIN_BOARD X38 | RF_PA PA2 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 110 | Main sense connector ↔ PA n PROPOSED |
| CBL-053 | MAIN_BOARD J29 | RF_PA PA2 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 310 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-054 | MAIN_BOARD J28 | RF_PA PA2 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-055 | RF_PA PA2 J2 | ANTENNA ROW2 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 150 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-056 | DSN-PSU-01 OUT2 | RF_PA PA2 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 470 |  |
| CBL-057 | MAIN_BOARD X_8 | RF_PA PA3 X2 | VG_3 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 210 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-058 | MAIN_BOARD X39 | RF_PA PA3 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 160 | Main sense connector ↔ PA n PROPOSED |
| CBL-059 | MAIN_BOARD J25 | RF_PA PA3 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 290 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-060 | MAIN_BOARD J24 | RF_PA PA3 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 300 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-061 | RF_PA PA3 J2 | ANTENNA ROW3 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 210 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-062 | DSN-PSU-01 OUT3 | RF_PA PA3 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 430 |  |
| CBL-063 | MAIN_BOARD X_15 | RF_PA PA4 X2 | VG_4 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 240 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-064 | MAIN_BOARD X40 | RF_PA PA4 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 210 | Main sense connector ↔ PA n PROPOSED |
| CBL-065 | MAIN_BOARD J31 | RF_PA PA4 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 290 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-066 | MAIN_BOARD J30 | RF_PA PA4 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 330 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-067 | RF_PA PA4 J2 | ANTENNA ROW4 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 260 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-068 | DSN-PSU-01 OUT4 | RF_PA PA4 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 390 |  |
| CBL-069 | MAIN_BOARD X_4 | RF_PA PA5 X2 | VG_5 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 190 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-070 | MAIN_BOARD X41 | RF_PA PA5 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 220 | Main sense connector ↔ PA n PROPOSED |
| CBL-071 | MAIN_BOARD J35 | RF_PA PA5 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 340 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-072 | MAIN_BOARD J34 | RF_PA PA5 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-073 | RF_PA PA5 J2 | ANTENNA ROW5 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 90 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-074 | DSN-PSU-01 OUT5 | RF_PA PA5 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 440 |  |
| CBL-075 | MAIN_BOARD X_11 | RF_PA PA6 X2 | VG_6 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 220 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-076 | MAIN_BOARD X42 | RF_PA PA6 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 220 | Main sense connector ↔ PA n PROPOSED |
| CBL-077 | MAIN_BOARD J37 | RF_PA PA6 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 310 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-078 | MAIN_BOARD J36 | RF_PA PA6 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 320 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-079 | RF_PA PA6 J2 | ANTENNA ROW6 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 140 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-080 | DSN-PSU-01 OUT6 | RF_PA PA6 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 400 |  |
| CBL-081 | MAIN_BOARD X_3 | RF_PA PA7 X2 | VG_7 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 290 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-082 | MAIN_BOARD X43 | RF_PA PA7 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 250 | Main sense connector ↔ PA n PROPOSED |
| CBL-083 | MAIN_BOARD J33 | RF_PA PA7 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 300 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-084 | MAIN_BOARD J32 | RF_PA PA7 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 250 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-085 | RF_PA PA7 J2 | ANTENNA ROW7 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 200 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-086 | DSN-PSU-01 OUT7 | RF_PA PA7 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 360 |  |
| CBL-087 | MAIN_BOARD X_12 | RF_PA PA8 X2 | VG_8 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 280 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-088 | MAIN_BOARD X44 | RF_PA PA8 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 280 | Main sense connector ↔ PA n PROPOSED |
| CBL-089 | MAIN_BOARD J39 | RF_PA PA8 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 270 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-090 | MAIN_BOARD J38 | RF_PA PA8 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-091 | RF_PA PA8 J2 | ANTENNA ROW8 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 250 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-092 | DSN-PSU-01 OUT8 | RF_PA PA8 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 320 |  |
| CBL-093 | MAIN_BOARD X_5 | RF_PA PA9 X2 | VG_9 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 290 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-094 | MAIN_BOARD X45 | RF_PA PA9 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 340 | Main sense connector ↔ PA n PROPOSED |
| CBL-095 | MAIN_BOARD J47 | RF_PA PA9 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-096 | MAIN_BOARD J46 | RF_PA PA9 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 270 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-097 | RF_PA PA9 J2 | ANTENNA ROW9 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 100 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-098 | DSN-PSU-01 OUT9 | RF_PA PA9 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 380 |  |
| CBL-099 | MAIN_BOARD X_14 | RF_PA PA10 X2 | VG_10 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 280 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-100 | MAIN_BOARD X46 | RF_PA PA10 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 290 | Main sense connector ↔ PA n PROPOSED |
| CBL-101 | MAIN_BOARD J41 | RF_PA PA10 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-102 | MAIN_BOARD J40 | RF_PA PA10 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 240 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-103 | RF_PA PA10 J2 | ANTENNA ROW10 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 130 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-104 | DSN-PSU-01 OUT10 | RF_PA PA10 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 340 |  |
| CBL-105 | MAIN_BOARD X_6 | RF_PA PA11 X2 | VG_11 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 350 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-106 | MAIN_BOARD X47 | RF_PA PA11 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 240 | Main sense connector ↔ PA n PROPOSED |
| CBL-107 | MAIN_BOARD J45 | RF_PA PA11 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 160 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-108 | MAIN_BOARD J44 | RF_PA PA11 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 140 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-109 | RF_PA PA11 J2 | ANTENNA ROW11 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 190 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-110 | DSN-PSU-01 OUT11 | RF_PA PA11 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 300 |  |
| CBL-111 | MAIN_BOARD X_13 | RF_PA PA12 X2 | VG_12 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 380 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-112 | MAIN_BOARD X48 | RF_PA PA12 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 290 | Main sense connector ↔ PA n PROPOSED |
| CBL-113 | MAIN_BOARD J43 | RF_PA PA12 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 160 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-114 | MAIN_BOARD J42 | RF_PA PA12 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 120 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-115 | RF_PA PA12 J2 | ANTENNA ROW12 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 240 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-116 | DSN-PSU-01 OUT12 | RF_PA PA12 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 260 |  |
| CBL-117 | MAIN_BOARD X_2 | RF_PA PA13 X2 | VG_13 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 360 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-118 | MAIN_BOARD X49 | RF_PA PA13 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 410 | Main sense connector ↔ PA n PROPOSED |
| CBL-119 | MAIN_BOARD J55 | RF_PA PA13 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 250 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-120 | MAIN_BOARD J54 | RF_PA PA13 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 260 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-121 | RF_PA PA13 J2 | ANTENNA ROW13 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 110 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-122 | DSN-PSU-01 OUT13 | RF_PA PA13 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 310 |  |
| CBL-123 | MAIN_BOARD X_9 | RF_PA PA14 X2 | VG_14 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 380 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-124 | MAIN_BOARD X50 | RF_PA PA14 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 380 | Main sense connector ↔ PA n PROPOSED |
| CBL-125 | MAIN_BOARD J49 | RF_PA PA14 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 250 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-126 | MAIN_BOARD J48 | RF_PA PA14 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 230 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-127 | RF_PA PA14 J2 | ANTENNA ROW14 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 130 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-128 | DSN-PSU-01 OUT14 | RF_PA PA14 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 270 |  |
| CBL-129 | MAIN_BOARD X_1 | RF_PA PA15 X2 | VG_15 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 450 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-130 | MAIN_BOARD X51 | RF_PA PA15 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 350 | Main sense connector ↔ PA n PROPOSED |
| CBL-131 | MAIN_BOARD J53 | RF_PA PA15 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 150 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-132 | MAIN_BOARD J52 | RF_PA PA15 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 190 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-133 | RF_PA PA15 J2 | ANTENNA ROW15 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 180 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-134 | DSN-PSU-01 OUT15 | RF_PA PA15 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 230 |  |
| CBL-135 | MAIN_BOARD X_10 | RF_PA PA16 X2 | VG_16 | 2-wire 24 AWG shielded, Molex 22-01-2027 | 450 | PA instance ↔ VG_n assignment PROPOSED (n = n); not documented in CAD |
| CBL-136 | MAIN_BOARD X52 | RF_PA PA16 X3 | drain current sense | 3-wire 24 AWG twisted, Molex 22-01-3037 | 370 | Main sense connector ↔ PA n PROPOSED |
| CBL-137 | MAIN_BOARD J51 | RF_PA PA16 J1 | RF 10.5 GHz (to PA RFIN) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 170 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-138 | MAIN_BOARD J50 | RF_PA PA16 J2 | RF 10.5 GHz (from PA RFOUT) | coax RG-405 SMA-SMA, EQUAL LENGTH set | 190 | which SMA of the pair is RFIN/RFOUT is UNVERIFIED (interconnection_table §7) |
| CBL-139 | RF_PA PA16 J2 | ANTENNA ROW16 | RF to antenna row n | coax RG-405 SMA-2.92 mm, EQUAL LENGTH set | 230 | antenna row n ↔ PA n PROPOSED; equal length mandatory for elevation phase |
| CBL-140 | DSN-PSU-01 OUT16 | RF_PA PA16 22V | 22 V drain, pulsed | 2-wire 18 AWG twisted, AK300/2 screw terminal | 190 |  |
| CBL-141 | SLIP RING VIN | POWER_SUPPLY X1 | VIN 12-17 V | 2 × 2-wire 16 AWG | 340 |  |
| CBL-142 | SLIP RING VIN | DSN-PSU-01 IN | VIN to 22 V boost | 2 × 2-wire 16 AWG | 470 |  |
| CBL-143 | SLIP RING USB | MAIN_BOARD X53 | USB 2.0 FS to host | USB 2.0 shielded, mini-B | 360 |  |
| CBL-144 | MAIN_BOARD stepper pins | PEDESTAL TB6600 (via slip ring) | STEP/DIR/EN | 3-wire 24 AWG shielded | TBD | the driver sits on the fixed base; needs 3 more slip-ring circuits OR move the driver into the head (then only motor phases cross: 4 circuits) — DECISION NEEDED |


---

<!-- chapter C: Tools and scripts (what each generator does, how to regenerate) -->
# Appendix C — Tools and scripts: what each generator does and how to regenerate

**Author of this appendix:** Antidrone Ukraine · antidrone.cc.

**Status summary:** documentation of the repository's own automation (`tools/`) and of the external tools installed on the authoring workstation. Every purpose statement is taken from the script's module docstring or header comment (read on 2026-10-09 with a shell loop over `tools/*`); every external version is the output of the tool's own `--version` call on the same date. No script modifies the upstream design files; outputs go to `engineering/`, `docs/`, `beta/`, `manual/` or `build/`.

**Sources:** `tools/*.py`, `tools/*.sh`, `tools/vivado/create_project.tcl` (docstrings/headers), `engineering/README.md` ("Regenerate everything"), `engineering/DESIGN/README.md` ("Regenerate"), `beta/README.md`, `beta/stm32/README.md` §1–§3, `beta/pcb/README.md`, `beta/fpga/README.md`, `docs/TESTING/VALIDATION_PLAN.md`.

## C.1 Repository scripts (`tools/`)

| Script | Purpose (from its docstring) | Inputs | Outputs | Regenerate / run |
|---|---|---|---|---|
| `build_manual.py` | "Build the AERIS-10 manual: concatenate manual/chapters/*.md in the order of manual/00_OUTLINE.md, number figures, resolve relative image links, write manual/AERIS10_MANUAL.md, manual/build/AERIS10_MANUAL.html (images embedded as data URIs; SVG inline) and manual/build/AERIS10_MANUAL.pdf (headless Chrome). `--check` only validates … Stdlib only (+ Google Chrome for the PDF). Exit 0 ok, 1 validation problems, 2 error." | `manual/00_OUTLINE.md`, `manual/chapters/*.md`, figure files | `manual/AERIS10_MANUAL.md`, `manual/build/*.html`, `*.pdf` | `python3 tools/build_manual.py [--check] [--no-pdf]` |
| `check_doc_links.py` | "Markdown link and path-reference validator … Scans every *.md file for Markdown links and backticked repository paths and verifies that each target exists relative to the referencing file's directory" | all `*.md` | report, exit code | `python3 tools/check_doc_links.py` (R-02) |
| `check_fpga_constraints.py` | "FPGA constraint completeness checker … reports unresolved placeholders, top-level ports with no PACKAGE_PIN constraint, ports with no IOSTANDARD" | top-level `.v`, `.xdc` | report, exit code | `python3 tools/check_fpga_constraints.py [--top … --xdc …]` (F-04) |
| `check_manufacturing_files.py` | "PCB manufacturing-package inventory … checks presence of schematic, board, Gerber set, NC drill, pick-and-place, BOM, assembly drawing, fabrication drawing, netlist, DRC/ERC reports. Reports a readiness table. Never creates files." | repository tree | readiness table, exit code | `python3 tools/check_manufacturing_files.py [--include-generated]` (B-06) |
| `check_missing_files.py` | "Expected-artifact manifest checker … Each entry has an ID that matches docs/03_MISSING_COMPONENTS.md. Never creates files." | manifest in the script | report, exit code | `python3 tools/check_missing_files.py` (R-03) |
| `check_python_imports.py` | "Python dependency extractor and import checker … Parses every *.py file with `ast` (no execution), lists imported top-level modules, classifies them as stdlib / third-party / local, maps third-party modules to PyPI distribution names, and (optionally, --try-import) tries importing each" | `*.py` under `--dir` | report, exit code | `python3 tools/check_python_imports.py [--dir …] [--try-import]` (P-02/P-03) |
| `check_stm32_includes.py` | "STM32 firmware include-graph and missing-header analyser … classifies each header as LOCAL / HAL / …" | C/C++ sources under `9_Firmware/9_1_Microcontroller` (or `--root`) | report, exit code | `python3 tools/check_stm32_includes.py [--root …]` (S-01) |
| `design_antenna_array.py` | "PROPOSED DESIGN — 16-row × 8-patch series-fed microstrip array for AERIS-10 (10.5 GHz). Reads engineering/DESIGN/design_parameters.json, computes first-order patch and microstrip dimensions … and writes engineering/DESIGN/ANTENNA/kicad/aeris10_patch_array.kicad_pcb" | `design_parameters.json` | `engineering/DESIGN/ANTENNA/` (KiCad board, drawings, calc sheet, openEMS model) | `python3 tools/design_antenna_array.py` |
| `design_antenna_tune.py` | "Tune the patch length of the openEMS row model until the resonance sits at f0 (secant on L_SCALE). Runs … openems_patch_row.py with the openEMS Python venv; writes … TUNING_LOG.md and the final s11.csv / s11 plot / pattern." | openEMS model | `engineering/DESIGN/ANTENNA/simulation/` | `python3 tools/design_antenna_tune.py [--iters 3] [--python PATH]` |
| `design_calcs.py` | "PROPOSED DESIGN calculations (BETA, no measurement): 2-D thermal map of the PA heat-spreader plate, pedestal drive torque, and the radar range equation. Stdlib only." | `design_parameters.json`, `THERMAL/thermal_summary.json`, `CAD/detail/parts_list.json`, `ANTENNA/simulation/tuning_result.json` | `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md`, `thermal_map_*.svg` | `python3 tools/design_calcs.py` |
| `design_enclosure_detail_freecad.py` | "PROPOSED DESIGN — detailed radar-head enclosure and pedestal (DSN-MECH-06…09), FreeCAD headless. Builds every mechanical part as its own solid … writes to engineering/DESIGN/MECHANICAL/CAD/detail/" | `tools/design_layout.py`, PCB hole tables | `aeris10_enclosure_detail.FCStd`, STEP, `parts_list.json`, isometric PNG/PDF | `freecadcmd -c "exec(open('tools/design_enclosure_detail_freecad.py').read())"` |
| `design_enclosure_drawings.py` | "PROPOSED DESIGN — enclosure detail drawings (no CAD needed): sheet-metal flat patterns with bend lines (DSN-MECH-06), assembly section with fastener balloons (DSN-MECH-07) and the mechanical parts list … Bend allowance: 90°, inside radius R = t, K = 0.4 → BA = π/2·(R + K·t)." | `CAD/detail/parts_list.json` | DSN-MECH-06/07 SVG/PDF/PNG, `MECHANICAL_PARTS_LIST.md` | `python3 tools/design_enclosure_drawings.py` |
| `design_host_link.py` | "PROPOSED DESIGN — FPGA → host data path (DSN-LINK-01). Option A 'FT601 on Main Board rev. B' … Option B 'SPI bridge, no PCB change'" | Main Board netlist, RTL geometry | `engineering/DESIGN/HOST_LINK/` (design note, pin plan, signal map) | `python3 tools/design_host_link.py` |
| `design_layout.py` | "Shared PROPOSED head/pedestal layout for the AERIS-10 design generators (D-08, D-09, D-11, D-12, D-13). Coordinate system of the HEAD … Boards are VERTICAL, parallel to the antenna, in depth order" | `design_parameters.json` | prints the station table (JSON) when run directly; imported by the other generators | `python3 tools/design_layout.py` |
| `design_mechanical_drawings.py` | "PROPOSED DESIGN — 2-D engineering drawings (SVG, scale 1:1) of the AERIS-10 head and pedestal plus the harness schedule, from tools/design_layout.py (no CAD application needed). Outputs … DSN-MECH-01 … DSN-MECH-05" | `design_layout.py`, KiCad P&P files | `engineering/DESIGN/MECHANICAL/drawings/`, `engineering/DESIGN/HARNESS/` | `python3 tools/design_mechanical_drawings.py [--harness]` |
| `design_mechanical_freecad.py` | "PROPOSED DESIGN — parametric 3-D model of the AERIS-10 radar head and pedestal in FreeCAD. Run with FreeCAD's Python (headless) … Reads tools/design_layout.py" | `design_layout.py` | `engineering/DESIGN/MECHANICAL/CAD/` (FCStd, STEP, STL, DXF page, mass table, isometrics) | `~/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tools/design_mechanical_freecad.py').read())"` |
| `design_pa_supply_schematic.py` | "PROPOSED DESIGN — block-level schematic, netlist and BOM of the 22 V PA drain supply / switch module (DSN-PSU-01, decision D-14). Draws an editable SVG … Component-level capture in KiCad is the next step (MDR-12); values come from tools/design_thermal.py." | `THERMAL/thermal_summary.json` | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/` | `python3 tools/design_pa_supply_schematic.py` |
| `design_thermal.py` | "PROPOSED DESIGN — thermal budget of the 16 × QPA2962 PA set and sizing of the 22 V drain supply. Reads … design_parameters.json and writes … THERMAL_AND_PA_SUPPLY.md (+ thermal_summary.json). All formulas are first-order engineering estimates" | `design_parameters.json` | `engineering/DESIGN/THERMAL/` | `python3 tools/design_thermal.py` |
| `eagle_svg_common.py` | "Shared helpers for rendering Autodesk EAGLE XML (.sch/.brd) to SVG. Stdlib only. Used by render_eagle_board.py and render_eagle_schematic.py." Holds the `ATTRIBUTION` title-block line (Antidrone Ukraine · antidrone.cc) applied when figures are regenerated. | — | library | imported |
| `extract_eagle_netlist.py` | "Extract per-part pin/net connectivity from an EAGLE 6/7 XML schematic … provide verifiable evidence (net name <-> device pin <-> package pad) for FPGA/MCU pin-assignment reconstruction. Read-only" | `.sch` | CSV named by `--out` | `python3 tools/extract_eagle_netlist.py <sch> --part U42 --out …` (S-07) |
| `fpga_lint.sh` | "syntax/elaboration check of the AERIS-10 FPGA RTL with open-source tools. Runs iverilog -g2012 elaboration of radar_system_top, verilator --lint-only, iverilog elaboration of the testbench (expected to fail: SystemVerilog assertions) … Never modifies RTL. Exit code: 0 if step 1 AND step 2 succeed, 1 otherwise, 3 if no tool found. Dependencies: bash 3.2+, iverilog >= 11 (tested 13.0), verilator >= 5 (tested 5.052)" | `9_Firmware/9_2_FPGA/*.v` | logs in `build/lint/` | `bash tools/fpga_lint.sh` (F-01…F-03) |
| `gen_assembly_exploded_view.py` | "CONCEPTUAL exploded assembly view of the AERIS-10 electronics set (SVG). Board outlines and hole positions are taken from the EAGLE .brd files (verified geometry …). The vertical ARRANGEMENT, the spacing, the antenna panel and the host computer are CONCEPTUAL" | `.brd` files | `engineering/ASSEMBLY/EXPLODED_VIEWS/` | `python3 tools/gen_assembly_exploded_view.py` |
| `gen_board_outline_svg.py` | "Draw an outline/mounting-hole dimension drawing (SVG) from an EAGLE .brd. Verified geometry only … The drawing contains NO enclosure, NO component outlines and NO thickness" | `.brd` | SVG | `python3 tools/gen_board_outline_svg.py …` (B-07) |
| `gen_drawing_register.py` | "Drawing register for engineering/ — definition table + existence/validity check. Writes engineering/DRAWING_REGISTER.md from the REGISTER table below and, with --check, verifies that every native file and export exists, is non-empty and (for SVG/DOT/PDF) is well-formed" | register table in the script, files | `engineering/DRAWING_REGISTER.md` | `python3 tools/gen_drawing_register.py --check` (AC-E1; run 2026-10-09: 89 drawings, 0 problems) |
| `gen_eagle_bom.py` | "Extract a bill of materials from an EAGLE 6+/7/9 XML schematic … Output: CSV (grouped), optional per-reference CSV" | `.sch` | `docs/BOM/*.csv` | `python3 tools/gen_eagle_bom.py …` (B-05) |
| `gen_engineering_pcb_docs.py` | "Generate the per-board manufacturing-package README (engineering/PCB/<BOARD>/README.md), copy the schematic-derived BOM next to the exports, and write the EAGLE↔KiCad cross-check (engineering/VALIDATION/PCB_CROSS_CHECK.md)" | `.brd`, KiCad pipeline outputs | README/STACKUP per board, cross-check | `python3 tools/gen_engineering_pcb_docs.py` |
| `gen_inventory_doc.py` | "Generate docs/01_REPOSITORY_INVENTORY.md (Path / File type / Subsystem / Purpose / Dependencies / Status) from the live file tree plus a curated purpose/dependency map … Writes ONLY the --out file." | file tree | `docs/01_REPOSITORY_INVENTORY.md` | `python3 tools/gen_inventory_doc.py` (R-01) |
| `gen_manual_asset_index.py` | "Scan the repository for figures usable in the manual (PNG/SVG/PDF/JPG/DOT/MMD renders) and write manual/ASSET_INDEX.md: one row per asset with path, type, size, origin, proposed caption and status" | repository tree, drawing register | `manual/ASSET_INDEX.md` | `python3 tools/gen_manual_asset_index.py` |
| `gen_mechanical_package.py` | "Build engineering/MECHANICAL/ from verified PCB geometry. For every board it extracts from the EAGLE .brd XML: the board outline (layer 20 Dimension), all non-plated holes and mounting pads … and writes … <BOARD>_dimensions.md" | `.brd` | `engineering/MECHANICAL/` (DXF, STEP, PDF, dimension sheets, plan view) | `python3 tools/gen_mechanical_package.py` |
| `gen_python_module_graph.py` | "Python GUI module/import graph. For every .py file under --src … parses the file with ast and records imports, classified as stdlib / third-party / local" | `9_Firmware/9_3_GUI/*.py` | `engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.dot/.md` | `python3 tools/gen_python_module_graph.py` (SD-05) |
| `gen_schematic_reports.py` | "Schematic connectivity reports from the EAGLE XML files (no EAGLE needed). For every board … writes netlist CSV (by net, by part), connection report …" | `.sch` | `engineering/ELECTRICAL/netlists/`, `connection_diagrams/` | `python3 tools/gen_schematic_reports.py` (AC-E3) |
| `gen_verilog_hierarchy.py` | "Verilog module hierarchy extractor. Parses every .v file under --rtl (recursively, nothing skipped), finds module definitions and module instantiations and writes" the DOT/Markdown hierarchy | RTL directory | `fpga_module_hierarchy.dot/.md` | `python3 tools/gen_verilog_hierarchy.py --rtl <dir> --out <dir>` (SD-01) |
| `gen_xdc_from_schematic.py` | "Build a candidate pin-constraint file for radar_system_top from the Main Board EAGLE schematic (RADAR_Main_Board.sch, FPGA part U42). Every PACKAGE_PIN written by this tool is taken verbatim from the schematic pad of the FPGA symbol; the mapping 'schematic net -> RTL port' is a documented, reviewable table with a confidence level." | `RADAR_Main_Board.sch` | candidate XDC + `PIN_MAP_FROM_SCHEMATIC.md` | `python3 tools/gen_xdc_from_schematic.py` (F-05) |
| `kicad_pcb_pipeline.sh` | "import the EAGLE .brd files into KiCad and export the complete manufacturing / drawing package with kicad-cli (KiCad >= 10.0). Non-destructive: original EAGLE files are only read. Outputs go to engineering/PCB/<BOARD>/ and every command + exit code is appended to engineering/VALIDATION/CAD_EXPORT_LOG.md." | `.brd` files | `engineering/PCB/<BOARD>/` (Gerber, drill, PDF drawings, SVG layers, DXF/STEP, P&P, IPC-2581, IPC-D-356, DRC, 3-D renders) | `bash tools/kicad_pcb_pipeline.sh [--kicad-cli PATH] [--out DIR] [BOARD …]` |
| `kicad_project_from_dru.py` | "Create a KiCad project file (.kicad_pro) whose design rules come from the EAGLE design rules (<designrules> block) stored in an EAGLE .brd file" — otherwise DRC runs with KiCad defaults | `.brd` | `.kicad_pro` | called by the pipeline |
| `render_eagle_schematic.py` | "Render an Autodesk EAGLE schematic (.sch, XML) to one SVG per sheet. Stdlib only; no EAGLE needed … a documentation rendering (SOURCE-DERIVED), not a CAD export: EAGLE's vector font is replaced by a monospace system font" | `.sch` | `engineering/ELECTRICAL/schematics/<BOARD>/svg/` | `python3 tools/render_eagle_schematic.py <sch> --out … --board … --root .` |
| `repo_inventory.py` | "AERIS-10 repository inventory generator. Walks the repository, classifies every file by type and subsystem, and prints a Markdown or CSV table. Non-destructive" | file tree | table on stdout or `--out` | `python3 tools/repo_inventory.py` |
| `run_all_checks.sh` | "runs every AERIS-10 static check and summarises PASS/FAIL. Non-destructive. Exit code = number of failed checks (capped at 125). Dependencies: bash, python3 (>=3.10). Optional: iverilog, verilator" | — | summary | `bash tools/run_all_checks.sh` |
| `stl_to_svg_iso.py` | "Render binary/ASCII STL files to a flat-shaded isometric SVG (painter's algorithm). Stdlib only … Intended for quick visual checks of FreeCAD/KiCad STL exports; not a CAD drawing." | STL | SVG | `python3 tools/stl_to_svg_iso.py -o out.svg [--title T] [--scale 0.5] [--az 35 --el 30] file.stl[:#color[:opacity]] …` |
| `stm32_check_cube_package.sh` | "verify that a STM32CubeF7 package tree contains every file the AERIS-10 firmware needs (HAL modules enabled in stm32f7xx_hal_conf.h, CMSIS device files, startup/linker templates, USB Device Library Core + CDC class). Read-only … Exit: 0 all found, 1 some missing, 2 bad argument." | Cube tree path | report | `tools/stm32_check_cube_package.sh beta/stm32/cube` (S-02) |
| `svg_sheets_to_pdf.py` | "Combine one or more SVG drawings into a multi-page PDF using headless Chrome/Chromium. Each SVG becomes one page whose size equals the SVG's width/height (mm), so the drawing prints at scale 1:1. No Python packages needed" (`--png-dir` also writes a PNG per sheet) | SVG files | PDF (+ PNG) | `python3 tools/svg_sheets_to_pdf.py -o out.pdf [--png-dir DIR] a.svg b.svg …` |
| `vivado/create_project.tcl` | "create a Vivado project from the repository RTL. This script DOES NOT choose the FPGA part for you … You must pass the verified part explicitly … It never edits RTL. Output: build/vivado/aeris10/aeris10.xpr. Tested: NOT executed in this repository (Vivado is not installed on the authoring machine)." | RTL, XDC | Vivado project | `vivado -mode batch -source tools/vivado/create_project.tcl -tclargs xc7a50tftg256-2` (F-07) |

Scripts living next to their sub-projects, documented in their own READMEs: `beta/fpga/build.sh`, `beta/fpga/gen_chirp_mem.py`, `beta/fpga/tb/gen_vectors.py`, `beta/fpga/vivado/*.tcl` (`beta/fpga/README.md`); `beta/stm32/build.sh`, `setup_cube.sh`, `tests/run_tests.sh` (`beta/stm32/README.md`); `beta/gui/build_app.sh` (`beta/gui/README.md`); `beta/pcb/tools/*.py` pcbnew/kicad-cli scripts (`beta/pcb/tools/README.md`).

## C.2 External tools installed on the authoring workstation (macOS arm64)

Versions as printed on 2026-10-09 by the commands in the last column; where a version was only recorded in a README it is marked so.

| Tool | Version found | Used for | Command / evidence |
|---|---|---|---|
| Python (system) | 3.14.8 | all `tools/*.py`, `build_manual.py` | `python3 --version` |
| Python venv `beta/gui/.venv` | CPython 3.14.7 + Tk 9.x | GUI, pytest, matplotlib (coupling plot F8.4) | `beta/gui/README.md`, `CHANGELOG.md` |
| KiCad / kicad-cli | 10.0.6 | EAGLE import, Gerber/drill/PDF/STEP exports, DRC (`kicad_pcb_pipeline.sh`, `beta/pcb`) | `~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli version` |
| FreeCAD | 1.1.4 (Revision 20260928) | `design_mechanical_freecad.py`, `design_enclosure_detail_freecad.py` | `~/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd --version` |
| openEMS (+ CSXCAD) | built from source, installed under `~/opt/openEMS` with its own Python venv | antenna row simulation (`design_antenna_tune.py`, `openems_patch_row.py`) | `beta/README.md` ("built from source on this machine"); `pip install openEMS` fails (not on PyPI — `docs/GUI/DEPENDENCIES.md` §7) |
| Arm GNU Toolchain | 14.2.Rel1 (`arm-none-eabi-gcc 14.2.1 20241119`) | `beta/stm32/build.sh` | `arm-none-eabi-gcc --version` |
| CMake | 4.4.3 | STM32 build | `cmake --version` |
| OpenJDK | 27 (Homebrew `openjdk 27`) — **not on the shell PATH**: `java -version` printed "Unable to locate a Java Runtime" during the check; `beta/pcb/README.md` records "Freerouting 2.5.0 jar (OpenJDK 27)" | Freerouting | `brew list --versions openjdk` |
| Freerouting | 2.5.0 (jar; log in `~/Library/Logs/freerouting/`) | Power Supply board routing (`beta/pcb`) | `beta/pcb/README.md` |
| Yosys | 0.69+post (git 143eb14f) | open-source synthesis trial (`beta/fpga_synth/`) | `yosys -V` |
| Icarus Verilog | 13.0 (stable) | `fpga_lint.sh`, `beta/fpga/build.sh` | `iverilog -V` |
| Verilator | 5.052 (2026-09-05) | lint, `beta/fpga/build.sh` | `verilator --version` |
| Graphviz | 16.1.0 (dot) | SYS-/SD-/ELEC- diagrams from `.dot` | `dot -V` |
| poppler | pdftoppm 26.10.0 | PDF → PNG renders for the manual (assembly drawings F15.2–F15.5) | `pdftoppm -v` |
| Google Chrome | present at `/Applications/Google Chrome.app` | `svg_sheets_to_pdf.py`, `build_manual.py` PDF | path check |
| Vivado | **not installed** | synthesis, timing, bitstream (F-07…F-09) | `docs/TESTING/VALIDATION_PLAN.md`; `beta/fpga/README.md` |
| STM32CubeMX / CubeIDE | **not installed** | `.ioc` regeneration (AC-S2) | `beta/stm32/CUBEMX_SETTINGS.md` |
| EAGLE | **not installed** | fresh ERC/DRC on the originals (B-01/B-02) | `docs/TESTING/VALIDATION_PLAN.md` |

## C.3 Regeneration order

Full engineering package (source: `engineering/README.md`, "Regenerate everything (≈ 10 min, needs KiCad 10 and Google Chrome on the machine; Graphviz for the DOT renders)", copied):

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

Proposed designs (source: `engineering/DESIGN/README.md`, "Regenerate", copied; every generator reads `engineering/DESIGN/design_parameters.json`):

```bash
python3 tools/design_thermal.py && python3 tools/design_antenna_array.py && python3 tools/design_pa_supply_schematic.py && python3 tools/design_mechanical_drawings.py && freecadcmd -c "exec(open('tools/design_mechanical_freecad.py').read())"
```

followed by `python3 tools/design_enclosure_drawings.py` and `python3 tools/design_calcs.py` (they consume `CAD/detail/parts_list.json` and `THERMAL/thermal_summary.json`, so they run after the FreeCAD detail model and the thermal sheet — chapter 10 §10.9), and `python3 tools/design_antenna_tune.py` for the openEMS run.

BETA trees (source: `beta/README.md`, table "Build/verify"): `bash beta/fpga/build.sh` (iverilog + verilator + 9 testbench runs); `bash beta/stm32/setup_cube.sh` then `bash beta/stm32/build.sh` and `bash beta/stm32/tests/run_tests.sh`; `cd beta/gui && .venv/bin/python -m pytest -q` and `.venv/bin/python -m aeris10_gui --selftest`; `beta/pcb` scripts per board as documented in `beta/pcb/tools/README.md`.

Manual (this document): render the figures listed in `manual/FIGURE_PLAN.md` ("to render") into `manual/figures/`, then `python3 tools/build_manual.py --check` (0 problems required), then `python3 tools/build_manual.py` (HTML + PDF). Figures rendered for the chapters of this edition and their exact commands are recorded in `manual/FIGURE_LOG.md`.

Static checks in one go: `bash tools/run_all_checks.sh` (exit code = number of failed checks; optional FPGA checks are skipped if iverilog/verilator are absent).


---

<!-- chapter D: Glossary, acronyms, status vocabulary -->
# Appendix D — Glossary, acronyms, symbols, status vocabulary and identifier families

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** reference appendix. Symbols are transcribed to plain text from `00_notation/symbol_table.md` (ORIGINAL PROJECT FILE); acronym expansions are standard engineering usage with the repository location where each term is used; the status vocabulary and identifier families are those of `manual/STYLE_GUIDE.md` and the registers cited in chapter 17.

**Sources:** `00_notation/symbol_table.md`, `00_notation/parameter_table.md`, `00_notation/conventions.md`, `manual/STYLE_GUIDE.md`, `engineering/SYSTEM/architecture/README.md`, `engineering/SYSTEM/interfaces/interconnection_table.md`, `docs/04_RECOVERY_TASKS.md`, `docs/TESTING/ACCEPTANCE_CRITERIA.md`, `docs/TESTING/VALIDATION_PLAN.md`, `docs/03_MISSING_COMPONENTS.md`, `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`.

**Planned figures:** none.

## 1. Acronyms and terms

| Term | Meaning in this manual | Where used (example) |
|---|---|---|
| ADC | analogue-to-digital converter; here the AD9484, 8-bit, 500 MSPS rated, operated at 400 MSPS | `00_notation/parameter_table.md` "RF Front-End"; chapter 2 §4 |
| ADAR1000 | four-channel X/Ku-band beamformer IC with 7-bit phase and gain control; four devices give 16 channels | `02_hardware/04_antenna_beamforming.md` §2 |
| ADF4382 | wideband PLL/VCO synthesizer used as TX LO (U1, 10.5 GHz) and RX LO (U6, 10.38 GHz) | chapter 3 §2.6 |
| AD9523 | low-jitter clock generator (IC1 on the Synth Board) producing the 400/120/100/20 MHz clocks and the 300 MHz ADF4382 reference | chapter 2 §4 |
| AD9708 | 8-bit DAC (U3) generating the chirp at 120 MHz | chapter 2 §4 |
| ADTR1107 | integrated X-band T/R front end (PA + LNA + switch), 16 devices, Nexus variant output stage | `README.md` "Main Board" |
| AF | array factor, AF(θ) | `01_physics/03_beamforming_theory.md` Eq. BF-3 |
| AGC | automatic gain control | `README.md` "FPGA" list (design intent only) |
| BETA | status label: builds/simulates/tests on a workstation, not on hardware | `manual/STYLE_GUIDE.md` |
| BOM | bill of materials | `docs/BOM/`, `beta/pcb/*/BOM_*_beta.csv` |
| BPF | band-pass filter; U$2/U$3 "BPF2" on the Main Board, part number NOT IDENTIFIED | chapter 2 §4 |
| BRAM | FPGA block RAM | `beta/fpga/README.md` resource estimate |
| BUFG / BUFIO / BUFR | Xilinx global / I/O / regional clock buffers | `beta/fpga/README.md` "ADC capture" |
| CA-CFAR | cell-averaging constant false alarm rate detector | `01_physics/04_detection_theory.md` §6 |
| CDC (1) | USB Communications Device Class (virtual serial port) — the STM32 host link on X53 | chapter 3 §2.8 |
| CDC (2) | clock-domain crossing (FPGA) | `beta/fpga/README.md` item 4 |
| CFAR | constant false alarm rate detection; a fixed-threshold PLACEHOLDER in the RTL | chapter 2 §2.3 |
| CIC | cascaded integrator–comb decimation filter (5 stages, decimate by 4) | `00_notation/parameter_table.md` "Signal Processing" |
| CPI | coherent processing interval (M chirps per beam position) | `00_notation/symbol_table.md` §1 |
| DAC | digital-to-analogue converter | chapter 2 §4 |
| DAC5578 | 8-channel I2C DAC driving the PA gate voltages VG_1..16 | chapter 3 §4.1 row `VG_1..16` |
| DDC | digital down-converter (NCO + mixer + CIC + FIR) | chapter 2 §5 |
| DIG_0..7 | STM32 PD8..PD15 handshake lines to the FPGA (new chirp/elevation/azimuth, mixers enable, reset; DIG_5..7 used by the option B bridge) | `docs/SYSTEM/BLOCK_DIAGRAM.md` §3 |
| DRC / ERC | design-rule check (PCB) / electrical-rule check (schematic) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-B1 |
| DRU | EAGLE design-rules file | `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md` MDR-07 |
| DSP48E1 | Xilinx 7-series DSP slice | `beta/fpga/README.md` resource estimate |
| DXF / STEP / STL | 2-D drawing exchange / 3-D CAD exchange / mesh formats | `engineering/MECHANICAL/` |
| EAGLE | Autodesk EAGLE, the native schematic/board CAD of the upstream project (`.sch`, `.brd`) | `4_Schematics and Boards Layout/` |
| eFuse | electronic fuse / hot-swap controller (LM5069 in DSN-PSU-01) | `engineering/DESIGN/00_DESIGN_BASIS.md` D-14 |
| ENOB / SQNR / SINAD | effective number of bits / signal-to-quantisation-noise ratio / signal-to-noise-and-distortion | `01_physics/05_noise_analysis.md` §5 |
| FFT / IFFT | fast Fourier transform / inverse; 1024-point range, 32-point Doppler | `00_notation/parameter_table.md` "Signal Processing" |
| FIR | finite impulse response filter | chapter 2 §5 |
| FMCW | frequency-modulated continuous wave; the physics notes use the FMCW formulation for the dechirp relations | `01_physics/01_fmcw_theory.md` |
| FPGA | field-programmable gate array; U42, Xilinx Artix-7 (XC7A50T per CAD, XC7A100T per README — K1) | chapter 1 §4 |
| FreeCAD | open-source MCAD used for the proposed head/pedestal model | `engineering/DESIGN/MECHANICAL/` |
| FT601 | FTDI USB 3.0 FIFO bridge (U6), placed but unwired on the Main Board | chapter 2 §6 |
| GaN | gallium nitride (QPA2962 PA technology) | `README.md` |
| Gerber | PCB photoplot data format | `engineering/PCB/<BOARD>/` |
| GT3 | 3 mm pitch timing belt profile (pedestal drive proposal) | `engineering/DESIGN/00_DESIGN_BASIS.md` D-12 |
| GUI | graphical user interface (Python, Tk) | `beta/gui/` |
| HAL | STM32Cube hardware abstraction layer | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` |
| HSE | STM32 high-speed external oscillator (8 MHz crystal vs 25 MHz firmware — K2) | chapter 17 §1 |
| I/Q | in-phase / quadrature components of a complex baseband signal | chapter 2 §5 |
| I2C / SPI / UART / USART | serial buses used by the STM32 to peripherals | chapter 3 §2.5, §2.8 |
| IDELAYE2 / ISERDESE2 / IDELAYCTRL | Xilinx input delay element / input serialiser-deserialiser / delay-control block used in the BETA ADC capture | `beta/fpga/README.md` "ADC capture" |
| IF | intermediate frequency, 120 MHz | `main.cpp:190` |
| IMU | inertial measurement unit (GY-85 module on I2C3) | chapter 3 §2.8 |
| INA241A3 | current-sense amplifier, 16 devices reading the PA drain shunts | chapter 3 §2.7 |
| IP core | vendor-supplied FPGA block (Xilinx xfft FFT cores, not generated) | `beta/fpga/ip/README.md` |
| IP54 | ingress-protection target of the proposed enclosure | `engineering/DESIGN/00_DESIGN_BASIS.md` D-08 |
| JTAG / SWD | FPGA test-access port (JP3) / ARM serial-wire debug (JP2) | chapter 3 §2.8 |
| KiCad | open-source PCB CAD used for the converted manufacturing packages and the proposed antenna | `engineering/PCB/`, `beta/pcb/` |
| LFM / PLFM | linear frequency modulation / pulsed LFM | `01_physics/02_lfm_waveform_model.md` |
| LNA | low-noise amplifier | `00_notation/parameter_table.md` "RF Front-End" |
| LO | local oscillator (TX LO 10.5 GHz, RX LO 10.38 GHz) | chapter 2 §4 |
| LTC5552 / LT5552 | wideband mixer (U5 up-converter, U13 down-converter); the README writes LT5552, the schematic LTC5552 | chapter 2 §4 |
| LUT | look-up table (chirp LUT in the FPGA; also FPGA logic resource) | `beta/fpga/README.md` |
| LVDS / LVDS_25 | low-voltage differential signalling; the ADC data standard and the FPGA I/O standard | chapter 3 §3 |
| M3SWA2-34DR+ | Mini-Circuits SPDT RF switch (17 devices) | chapter 2 §4 |
| MCU | microcontroller unit (STM32F746ZGT7, U2) | chapter 1 §3 |
| MMCM | Xilinx mixed-mode clock manager | `beta/fpga/README.md` |
| MPN | manufacturer part number | `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-B5 |
| MTI | moving-target indication (README intent; not implemented) | `README.md` |
| NCO | numerically controlled oscillator | chapter 2 §5 |
| NEMA 23 / NEMA 34 | stepper motor frame sizes (57 mm / 86 mm class) | `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §2 |
| NF | noise figure (dB) | `00_notation/symbol_table.md` §4 |
| OCXO / VCXO | oven-controlled / voltage-controlled crystal oscillator (X4; X5, X6 on the Synth Board — K7) | chapter 3 §4.1 row `+3V3_XO` |
| openEMS | open-source FDTD electromagnetic solver used for the antenna simulation | `engineering/DESIGN/ANTENNA/simulation/` |
| P&P | pick-and-place (component placement) file | `engineering/PCB/<BOARD>/assembly/` |
| PA | power amplifier (QPA2962 GaN 10 W on the RF PA board) | chapter 1 §3 |
| PAE / PSAT / IDQ | power-added efficiency / saturated output power / quiescent drain current of the PA | `engineering/DESIGN/00_DESIGN_BASIS.md` §1 row "PA" |
| PLL | phase-locked loop | chapter 2 §4 |
| PRF / PRI | pulse repetition frequency / interval | `00_notation/symbol_table.md` §1 |
| PSL | peak sidelobe level | `01_physics/02_lfm_waveform_model.md` Eq. LFM-21 |
| QPA2962 | Qorvo GaN power amplifier, 10 W class, 22 V drain | `engineering/DESIGN/00_DESIGN_BASIS.md` §1 |
| RCS | radar cross section σ | `00_notation/symbol_table.md` §4 |
| RF | radio frequency | — |
| RTL | register-transfer level (Verilog) description of the FPGA design | `beta/fpga/rtl/` |
| SDR (1) | single data rate (AD9484 LVDS output timing) | `beta/fpga/README.md` item 2 |
| SDR (2) | software-defined radio (README audience) | `README.md` |
| SMA / 2.92 mm | coaxial connector types (Main Board RF ports; proposed antenna connectors) | chapter 3 §2.7; D-05 |
| SNR | signal-to-noise ratio | `00_notation/symbol_table.md` §4 |
| STM32CubeMX / `.ioc` | ST configuration tool and its project file (absent from the repository) | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` |
| T/R | transmit/receive | `02_hardware/01_system_overview.md` §1.1 |
| TBP | time-bandwidth product B·T_c | `01_physics/02_lfm_waveform_model.md` Eq. LFM-5 |
| TBD | to be determined (value absent from every repository file) | `00_notation/parameter_table.md` "TBD Tracking" |
| TMP37 | analogue temperature sensor (8 devices via ADS7830) | chapter 3 §2.8 |
| TPS562208 / ADM7151 / TPS7A8300 / LM2662 | buck regulator / LDO / LDO / charge-pump inverter families on the Power Board | chapter 3 §4.1 |
| ULA | uniform linear array | `01_physics/03_beamforming_theory.md` §1 |
| VD / VG / VIN_M | PA drain voltage / gate voltage / drain-current sense return | chapter 3 §2.7 |
| Vivado | AMD/Xilinx FPGA toolchain (not available on the authoring machine) | `beta/fpga/README.md` |
| VNA | vector network analyser (antenna coupon measurement, NOT RUN) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-E7 |
| XDC | Xilinx design constraints file | `beta/fpga/constraints/` |

## 2. Mathematical symbols

Transcribed to plain text from `00_notation/symbol_table.md` (notation authority IEEE 686-2024 per that file); subscripts are written after an underscore, e.g. `T_c,1` for the long chirp duration.

| Symbol | Definition | Units |
|---|---|---|
| f_c | centre (carrier) frequency | Hz |
| B | chirp bandwidth (sweep range) | Hz |
| T_c | chirp duration (pulse width); T_c,1 long, T_c,2 short | s |
| μ | chirp rate, μ = B / T_c | Hz/s |
| f_b | beat frequency (IF after dechirp) | Hz |
| f_r | pulse repetition frequency; f_r,1 long mode, f_r,2 short mode | Hz |
| T_r | pulse repetition interval, T_r = 1/f_r; T_r,1, T_r,2 | s |
| τ | round-trip delay, τ = 2R/c | s |
| T_guard | guard time between chirp sequences | s |
| M | number of chirps per CPI (per beam position) | — |
| R, R_max, ΔR | range, maximum unambiguous range, range resolution | m |
| v, Δv | target radial velocity, velocity resolution | m/s |
| f_d | Doppler frequency shift | Hz |
| c | speed of light, ≈ 2.998 × 10^8 | m/s |
| λ | wavelength, λ = c / f_c | m |
| N | number of array elements | — |
| N_el, N_az | beam elevation positions; azimuth positions per revolution | — |
| d | inter-element spacing | m |
| θ, θ_0 | beam angle from broadside; desired steering angle | rad or deg |
| Δφ, Δφ_n | phase shift per element; phase difference for elevation position n | rad or deg |
| G, G_t, G_r | antenna gain (combined; transmit; receive) | dBi |
| k | wavenumber, k = 2π/λ | rad/m |
| ψ | electrical angle, ψ = k d sinθ + Δφ | rad |
| θ_3dB | half-power beamwidth | rad or deg |
| w_n, a_n | amplitude weight / nominal amplitude weight of element n | — |
| δφ_n, δa_n | phase / amplitude error of element n | rad / — |
| AF(θ) | array factor | — |
| P_t, P_r | transmit power (per element), received power | W |
| σ | radar cross section | m² |
| L | total system losses (linear ratio) | — |
| F, NF | noise figure (linear; dB) | — / dB |
| T_0 | reference noise temperature, 290 K | K |
| k_B | Boltzmann constant, 1.381 × 10^−23 | J/K |
| P_fa, P_d | probability of false alarm, probability of detection | — |
| SNR, SNR_min | signal-to-noise ratio, minimum detectable SNR | dB |
| α | CFAR threshold multiplier | — |
| N_ref, N_guard | CFAR reference cells, guard cells (total) | — |
| T_e, B_n | equivalent noise temperature, noise bandwidth | K, Hz |
| f_s | ADC sampling frequency | Hz |
| f_IF | intermediate frequency | Hz |
| N_FFT, N_Doppler, N_R | FFT size (range), Doppler FFT size, number of range bins | — |
| N_CIC, D_CIC | CIC filter stages, CIC decimation factor | — |
| w[n] | window function (discrete) | — |
| χ(τ, ν) | ambiguity function | — |
| Δφ_NCO | NCO phase accumulator increment per clock cycle | — |
| G_CIC | CIC filter DC gain, G_CIC = D_CIC^N_CIC | — |
| N_seg, L_adv, L_overlap | overlap-save segments, segment advance, overlap length (matched filter) | — / samples |
| N_rb, D_rb | output range bins after decimation, range-bin decimation factor | — |
| V_rail, I_rail | voltage rail value, current draw per rail | V, A |
| P_diss, T_junction, θ_JA | power dissipation, junction temperature, thermal resistance junction-to-ambient | W, °C, °C/W |
| t_lock | PLL lock time | s |
| L(f_m) | phase noise at offset f_m from carrier | dBc/Hz |
| t_pipeline | end-to-end pipeline latency | s |
| N_LUT, N_FF, N_BRAM, N_DSP | FPGA look-up tables, flip-flops, block RAMs, DSP48E1 slices | — |

Equation tags (FMCW-n, LFM-n, BF-n, DET-n, NF-n, CAL-n, HW-ANT-n) refer to the display equations of the upstream physics and hardware notes under the document-prefix scheme of `00_notation/conventions.md` §1.

## 3. Status vocabulary

Labels on figures and procedures (source: `manual/STYLE_GUIDE.md`): ORIGINAL PROJECT FILE · SOURCE-DERIVED · PARTIAL · CONCEPTUAL · PROPOSED DESIGN · BETA · BLOCKED — MISSING DATA · VERIFIED (reserved; unused). Qualifiers on numbers: ASSUMED, ESTIMATE, TBD, UNKNOWN, UNRESOLVED, REQUIRES VERIFICATION.

Register-specific vocabularies kept as in their sources:

| Register | Values | Source |
|---|---|---|
| Interconnection table, power-rail register | CONFIRMED / UNVERIFIED / MISSING SPEC; PARTIAL; CONFLICT | `engineering/SYSTEM/interfaces/interconnection_table.md`; `engineering/ELECTRICAL/power_distribution/power_rails.md` |
| Drawing register | SOURCE-DERIVED / PARTIAL / CONCEPTUAL / PROPOSED / BLOCKED | `engineering/DRAWING_REGISTER.md` |
| Recovery tasks | DONE / OPEN / BLOCKED (designer input) / PARTIALLY DONE | `docs/04_RECOVERY_TASKS.md` |
| Acceptance criteria | MET / NOT MET / PARTIALLY MET / NOT RUN (physical tests) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` |
| Missing components | priorities P0 (blocks a reproducible build or required artefact) / P1 (blocks a complete release or reliable validation) / P2 (documentation, maintainability) | `docs/03_MISSING_COMPONENTS.md` |
| Firmware defects | C1–C7 conflict rows of STM-T04 | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` |
| Interface confidence | MEDIUM (bit mapping inferred from source comments) | `docs/SYSTEM/BLOCK_DIAGRAM.md` §3 |

## 4. Identifier families

| Family | Range | Meaning | Register |
|---|---|---|---|
| K | K1–K8 | configuration conflicts between CAD, firmware, RTL, GUI and documentation | `docs/SYSTEM/BLOCK_DIAGRAM.md` §4; chapter 17 §1 |
| D | D-01…D-15; D-16…D-19 | proposed-design decisions (mechanical/antenna/thermal/harness; host link) | `engineering/DESIGN/00_DESIGN_BASIS.md` §2; `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §3–4; chapter 17 §2 |
| G | G-01…G-12 | unresolved mechanical geometry | `engineering/VALIDATION/UNRESOLVED_GEOMETRY.md`; chapter 17 §3 |
| MDR | MDR-01…MDR-13 | missing-drawing recovery guides | `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`; chapter 17 §4 |
| DSN | DSN-00, DSN-ANT-01, DSN-THM-01, DSN-PSU-01, DSN-MECH-01…07, DSN-MECH-3D, DSN-HAR-01, DSN-LINK-01, DSN-CALC-01 | proposed-design documents and drawings | `engineering/DRAWING_REGISTER.md` |
| SYS / SD / ELEC-PWR | SYS-01…04; SD-01…07; ELEC-PWR-01 | system-level and software diagrams (SOURCE-DERIVED / PARTIAL) | `engineering/SYSTEM/architecture/README.md`; `engineering/DRAWING_REGISTER.md` |
| PCB-*, MECH-*, ASM-EXP-01, VAL-GEO-01, ENG-MDR-01 | per board / per drawing | registered PCB drawings, mechanical drawings, exploded view, validation and recovery documents | `engineering/DRAWING_REGISTER.md` |
| CBL | CBL-00…CBL-106 (two-digit, per signal group) and CBL-001…CBL-144 (three-digit, per physical cable) | cable identifiers — two schemes, see MAN-03 | `engineering/SYSTEM/interfaces/interconnection_table.md`; `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md` |
| AC | AC-F1…F9, AC-S1…S7, AC-P1…P7, AC-B1…B8, AC-M1…M5, AC-D1…D5, AC-E1…E8, AC-X1… | acceptance criteria per area (FPGA, STM32, Python, PCB, mechanical, documentation, engineering package, BETA tree) | `docs/TESTING/ACCEPTANCE_CRITERIA.md` |
| F / S / P / B / R | F-01…F-10, S-01…S-10, P-01…P-09, B-01…B-09, R-01…R-03 | validation-plan checks (FPGA, STM32, Python, PCB, repository) referenced by the acceptance criteria | `docs/TESTING/VALIDATION_PLAN.md` |
| R | R-SYS-01, R-FPGA-01…10, R-STM-01…08, R-GUI-01…03, R-PCB-01…06, R-MECH-01…02, R-DOC-01…03, R-ENG-01…13, R-DSN-01…07, R-BETA-01…09 | recovery tasks | `docs/04_RECOVERY_TASKS.md`; chapter 17 §5 |
| FPGA- / STM- / GUI- / PCB- / MECH- / REPO- | FPGA-00…15, STM-01…19, GUI-01…08, MECH-01…06, REPO-01…05 | missing-component manifest IDs checked by `tools/check_missing_files.py` | `docs/03_MISSING_COMPONENTS.md` |
| C | C1–C7 | STM32 firmware conflicts/defects (HSE, ADF4382 pins, platform ops, USB RX, start-flag padding, GPS_Init, AD9523 CS/SPI speed) | `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` STM-T04 |
| F0–F10 | — | firmware power-enable sequence steps as coded | `engineering/ELECTRICAL/power_distribution/power_rails.md` §3; chapter 3 §4.2 |
| MAN | MAN-01…04 | observations raised by this manual while compiling the sources | chapter 17 §6 |
| Figure numbers | F<chapter>.<n> | figure slots of `manual/FIGURE_PLAN.md`; the build tool prefixes a running "Figure n —" | `manual/FIGURE_PLAN.md` |
