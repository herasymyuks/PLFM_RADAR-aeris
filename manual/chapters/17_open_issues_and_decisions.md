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
