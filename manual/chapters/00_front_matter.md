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
