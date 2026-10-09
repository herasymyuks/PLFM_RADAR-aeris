# AERIS-10 — Design basis for the missing elements (PROPOSED DESIGNS)

Document DSN-00 · Rev A · 2026-10-09 · Status: **PROPOSED DESIGN** (new engineering content; nothing here is a reconstruction of an existing design).

Everything under `engineering/DESIGN/` is *proposed*: it closes the BLOCKED items of `engineering/DRAWING_REGISTER.md` (enclosure, internal layout, antenna, cooling, pedestal, 22 V PA supply, harness) with designs derived from the **verified constraints** of the repository plus **explicit design decisions** logged below. Parameters live in `design_parameters.json`; every generator (`tools/design_*.py`) reads that file so a changed decision regenerates every drawing. Status vocabulary for these drawings: `PROPOSED DESIGN` (with the decisions it depends on) — never SOURCE-DERIVED or VERIFIED.

## 1. Verified inputs (from the repository)

| Input | Value | Evidence |
|---|---|---|
| Carrier | 10.5 GHz, λ = 28.57 mm | `main.cpp` wavelength constant; `00_notation/parameter_table.md` |
| Array | 16 elements, uniform linear, pitch λ/2 = 14.3 mm, electronically scanned in **elevation** (31 positions, Δφ ±160° ⇒ ≈ ±33°); azimuth by **mechanical rotation**, 50 positions/rev = 7.2°, 4 stepper steps per position (200 steps/rev) | `02_hardware/04_antenna_beamforming.md` §3–4; `main.cpp:187-195, 514-521` |
| Patch variant | "8×16 patch array", ~20 dBi TBD, 1 W/element (ADTR1107); Extended variant: slotted waveguide + QPA2962 10 W | `parameter_table.md` rows 77, 87 |
| Waveform timing | 16 long chirps (30 µs / PRI 167 µs) + guard 175.4 µs + 16 short chirps (0.5 µs / PRI 175 µs) per beam position | `main.cpp:180-186` |
| PA | QPA2962: PSAT 40 dBm, PAE 22 %, VD 22 V, IDQ 1.68 A, PDISS max 40 W @ TBASE 85 °C, 5×5 mm package | `7_Components Datasheets…/QPA2962/QPA2962 Data Sheet.pdf` p.1-2 |
| PA board | 35 × 60 mm, 7 × Ø3.2 holes, X2 VG (Molex 2-pin), X3 sense (3-pin), `22V` AK300/2 terminal, J1 RFIN / J2 RFOUT SMA | `engineering/PCB/RF_PA/`, `engineering/MECHANICAL/dimensions/RF_PA_dimensions.md` |
| Other boards | Main 260 × 300 (10 holes), Power 280 × 300 (8 holes), Synth 100 × 100 (4 holes) | `engineering/MECHANICAL/dimensions/` |
| System DC input | VIN 12–17 V (Power Board X1) | `Power Management V6.xlsx`; `power_rails.md` |
| Stepper driver | TB6600-class, 9–42 V, 4 A, 20 V selected | xlsx row 63 |
| Cooling | "apply when temperature reaches a threshold (relay)" — a fan relay exists in the plan | xlsx row 64 |
| Host link | USB 2.0 full-speed CDC via Main Board X53 | schematic |
| Yaw sensor | IMU in the head is used to point the array north at start-up | `main.cpp:1513-1519` |

## 2. Design decisions (log)

| ID | Decision | Rationale | Alternatives |
|---|---|---|---|
| D-01 | Design the **patch-array (Nexus) antenna** as the primary antenna; provide only a sizing sheet for the slotted-waveguide (Extended) variant | A patch array is manufacturable with the same PCB workflow and verifiable with the openEMS/Qucs tools already used in `5_Simulations`; slotted waveguides need machining and a full EM design | waveguide array (CONCEPTUAL sizing sheet in `ANTENNA/README.md`) |
| D-02 | The 16 radiating "elements" are **16 horizontal rows** stacked vertically at 14.3 mm; each row is a **series-fed resonant array of 8 patches** | Matches "8×16", the elevation-scanned ULA of the firmware and a fixed narrow azimuth beam rotated mechanically | corporate feed per row (lower squint, more layout area) |
| D-03 | 8 patches per row | parameter table row 77 | — |
| D-04 | Substrate RO4350B, h = 0.508 mm, 35 µm Cu, single dielectric layer, full back ground | datasheet in repo; PCBWay impedance note is for RO4350B; 20 mil gives good patch bandwidth (~2 %) with manageable surface waves | 0.762 mm (wider band, more surface wave) |
| D-05 | 50 Ω end-launch 2.92 mm connectors on the left edge, one per row, 14.3 mm pitch (body ≤ 12 mm wide) | simplest verifiable feed; keeps the ground plane continuous | probe feed from the back (allows SMA on rear) |
| D-06 | Row phase centre spacing is λ/2; each row's feed line length is **equal** so the ADAR1000 calibration tables remain valid | elevation scanning depends on equal electrical length to each row | — |
| D-07 | Board stack pitch 25 mm (component heights assumed 15 mm top / 4 mm bottom until measured) | no 3-D models; standard 25 mm M3 standoffs | measure, then shrink |
| D-08 | Enclosure: folded 2.5 mm aluminium chassis + lid, 10 mm board-to-wall clearance, IP54 target, antenna panel in the front face behind a PTFE/ABS radome window | aluminium gives the heat path for the PA spreader; sheet metal keeps cost low | machined frame |
| D-09 | Board arrangement: Power Board on the base, Main Board above it (25 mm), Synth on the Main-Board tier beside the SMA field; PA spreader vertical behind the antenna panel at the front; stepper/slip ring below the base | shortest coax from Synth J-ports to Main J1/J18–J23; rails cables short; RF to the front | side-by-side single tier (larger footprint) |
| D-10 | Thermal design case: ambient 45 °C, TBASE(PA) ≤ 85 °C, **drain gated with the pulse train** (duty computed from the timing); continuous-bias case reported as infeasible without liquid cooling | 16 × 37 W = 591 W quiescent is not coolable in a sealed rotating head; gating requires a hardware change (D-14) | — |
| D-11 | 10 mm aluminium heat spreader common to all 16 PA boards, fan-cooled fin stack at the rear, 1.5× airflow margin | conduction from 16 hot spots into one plate, then forced air | per-PA heatsinks |
| D-12 | Azimuth drive: NEMA 23 stepper → 1:1 GT2 belt → turntable, so the firmware's 4 steps per 7.2° stays valid | firmware is fixed; 1:1 keeps the step count; belt isolates the motor from the slewing ring | direct shaft coupling; geared with firmware change |
| D-13 | Slip ring 12 channels (VIN ×4 @10 A, 22 V ×4 @10 A, USB 2.0 ×4) through a 60 mm bore slewing bearing; everything else rotates with the head | only DC in and the host link cross the rotation | Ethernet/wireless host link (removes 4 channels) |
| D-14 | 22 V PA supply: synchronous boost 12–17 V → 22 V, 150 W average / bulk capacitance for 45 A pulse peaks, high-side eFuse/MOSFET switch from `EN/DIS_RFPA_VDD`, plus a per-pulse drain-gating FET per PA board (TTL from the FPGA/MCU `DIG` lines — pin to be allocated) | closes conflict K4; the firmware already sequences VG before VD | separate 22 V mains PSU on the pedestal (bigger slip ring) |
| D-15 | Harness: cable IDs from `interconnection_table.md`; coax RG-405 (0.086") hand-formable equal-length for Main↔PA and Synth↔Main; Molex 22-01-3027/3037 crimp housings for the 2-/3-pin headers; 20-way IDC ribbon for SV1 | standard parts matching the footprints in the schematics | — |

## 3. What the proposals do NOT settle (still owner decisions)

Conflicts K1–K8 (`docs/SYSTEM/BLOCK_DIAGRAM.md`), component heights (G-02), final Power Board outline (G-10), whether the host link stays USB (affects D-13), antenna variant (D-01), the PA pulse-gating implementation (D-14 needs a spare control line), and all RF performance targets (gain, bandwidth B is TBD in the parameter table).

## 4. Deliverables generated from this basis

| Item | Generator | Output |
|---|---|---|
| Antenna array PCB (native KiCad), drawings, calculation sheet, openEMS model | `tools/design_antenna_array.py` | `engineering/DESIGN/ANTENNA/` |
| Thermal and 22 V supply sizing | `tools/design_thermal.py` | `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` |
| Enclosure, internal layout, heat spreader, pedestal — 3-D (FreeCAD/STEP) and 2-D drawings | `tools/design_mechanical_freecad.py` (FreeCAD) and `tools/design_mechanical_drawings.py` (SVG/PDF, no CAD needed) | `engineering/DESIGN/MECHANICAL/` |
| Harness schedule with computed lengths | `tools/design_mechanical_drawings.py --harness` | `engineering/DESIGN/HARNESS/` |
| 22 V PA supply/switch module schematic + BOM | hand-authored | `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/` |
