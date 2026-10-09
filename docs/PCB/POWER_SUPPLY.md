# Power Supply Board — Manufacturing Readiness Report

Board: `4_Schematics and Boards Layout/4_6_Schematics/PowerBoard/PowerBoard.sch` (EAGLE **9.6.2**) / `PowerBoard.brd` (EAGLE **7.4.0** — version mismatch). Status date 2026-10-08. Method: XML inspection only. **Readiness verdict: NOT FABRICATION-READY** — 309 airwires, 132 of 312 parts parked outside the outline, no production outputs.

> **Update 2026-10-09:** a generated manufacturing & drawing package (KiCad 10 conversion of the EAGLE board: Gerber, drill, PDF/SVG layer and assembly drawings, DXF, STEP, P&P, BOM, IPC-2581, IPC-D-356, DRC with DRU-derived rules, 3-D renders) is in `engineering/PCB/POWER_SUPPLY/` (see its `README.md`, `STACKUP.md`). Schematic PDF/SVG: `engineering/ELECTRICAL/schematics/POWER_SUPPLY/`. Netlist and connection reports: `engineering/ELECTRICAL/netlists/`. The package is SOURCE-DERIVED/PARTIAL, not designer-released; the EAGLE procedures below remain the path to the authoritative export.

## 1. Source-file inventory

| File | Size | Content (verified) |
|---|---|---|
| `PowerBoard.sch` | 828 274 B | 1 sheet; 562 `<part>`, 312 physical; 156 nets; 9 embedded libraries (Autodesk URN references present but content embedded) |
| `PowerBoard.brd` | 442 121 B | 312 elements (**132 outside the outline**, y down to −486 mm), 157 signals (`+3V3_LO` board-only), 879 wires (**309 airwires**), 346 vias (0.3 ×4, 0.35 ×42, 0.6 ×300), outline **280 × 300 mm**, 2 copper layers (`layerSetup=(1*16)`), DRU `PCBWay_2L_100um-Track`, core 1.5 mm (`mtIsolate[0]`) |
| `docs/BOM/BOM_POWER_SUPPLY.csv`, `docs/BOM/BOM_POWER_SUPPLY.md`, `REFS_POWER_SUPPLY.csv` | generated | 312 references, 28 line items, 0 MPN attributes, 80 references without value |
| `docs/MECHANICAL/drawings/POWER_SUPPLY_outline.svg` | generated | outline + 8 × Ø3.2 mm NPTH at (10,10) (270,10) (270,230) (10,230) (138.45,267.85) (140,10) (270,120) (10,120) |
| `3_Power Management/Power Management V6.xlsx` | 17 410 B | rail list, currents, enable, sequence (single sheet `Feuil1`, A1:M99) — design input, not an output |

Key ICs (deviceset names, UNVERIFIED as MPN): TPS562208DDCT ×21 (buck), ADM7151ACPZ-04-R7 ×6 (LDO), TPS7A8300RGRR ×2 (LDO), LM2662MX/NOPB ×5 (inverter), T521W476M020ATE045 ×10 (tantalum), 34 × Molex 22-23-2021, AK300/2 (X1, input terminal). Datasheet folder contains TPS562201 and LM2663 instead of the TPS562208/LM2662 actually used — datasheets to be added. MAX20029 (datasheet present) is not on the board.

Rails (silkscreen layer 51 labels): `Vin [12-17]V`, `+5V5_PA, -5V5_PA, +1V8_CLOCK, +3V3_CLOCK, +3V3_VDD_SW, +5V0_PA_1/2/3, -3V3_SW, +3V3_SW, +3V3_ADTR, -5V0_ADAR12, -5V0_ADAR34, +3V4, -3V4, +3V3_LO, +5V0_ADAR, +3V3_ADAR_12, +3V3_ADAR_34, +5V0_0, +1V8_FPGA, +1V0_FPGA, +3V3, +3V3_FPGA, +3V3_AN`, 12 × `EN`. The 16 `EN_*` nets match the STM32 enable GPIOs (PE7..PE15, PG0..PG5).

## 2. Layout state and defects

| Item | Finding |
|---|---|
| Routing | 309 airwires across 86 of 157 signals; 72 signals entirely unrouted (all 16 `EN_*`, several `+5V0_*`, `+3V3_XO`, `+3V3_LO_1/2`) |
| Placement | 132 of 312 elements outside the 280 × 300 mm outline; mounting holes lie within 10..270 × 10..230 (+ one at y = 267.85) → the intended final outline is **UNRESOLVED** |
| Version mismatch | sch 9.6.2 vs brd 7.4.0 — annotation link cannot be trusted; one board-only signal `+3V3_LO` |
| DRC | 0 approved errors (meaningless while unrouted) |
| ERC | 0 approved entries; 0 single-pin nets |
| Design-input discrepancies | xlsx budgets 16 × QPA2962 at +22 V (2 A each); the Power Board has no 22 V rail label (`Vin [12-17]V`) and the RF PA board holds one QPA2962 — PA supply architecture **UNRESOLVED** |

## 3. Missing manufacturing outputs

Gerber (2 Cu + mask + silk + paste + profile), drill, fab drawing, assembly drawings, BOM with MPN, pick-and-place, schematic PDF, netlist, DRC/ERC reports, stack-up confirmation: **all MISSING**.

## 4. Required software

EAGLE 9.6.2 (will upgrade the 7.4.0 board on save; keep original) / Fusion 360 Electronics / KiCad 8+. Gerber viewer.

## 5. CAD operations (exact)

P-EAGLE-01: on opening, expect the "severed annotation" dialog because of the version mismatch — do **not** accept automatic fixes; export both part lists and reconcile. Then P-EAGLE-02, P-EAGLE-03 (`RATSNEST` → expect 309 airwires until routed), complete placement and routing (designer), P-EAGLE-04 with template *2 Layer*, P-EAGLE-06/07/08.

## 6. Export settings and expected filenames

RS-274X mm 4.4; Excellon mm; files `PowerBoard/Gerber/copper_top.gbr, copper_bottom.gbr, soldermask_top/bottom.gbr, silkscreen_top/bottom.gbr, solderpaste_top/bottom.gbr, profile.gbr`; `Drill/drill_1_16.xln, drill_npth.xln`; `PowerBoard-smd.mnt`, `PowerBoard-tht.mnt`; `PowerBoard_BOM.csv`; `PowerBoard_fab.pdf`; `PowerBoard_assembly_top.pdf`; `PowerBoard_schematic.pdf`.

## 7. DRC/ERC validation requirements

- Consistency restored (same part and net sets in sch and brd; `+3V3_LO` resolved).
- `RATSNEST` nothing to do; 0 elements outside outline; outline decision documented.
- DRC 0 errors with `PCBWay_2L_100um-Track` (min track 0.1 mm, drill 0.3 mm as stored); thermal relief on the 300 × 0.6 mm vias checked.
- Current capacity: trace widths for the highest-current rails (xlsx: QPA2962 bias ≥ 1.68 A each; FPGA +1V0) verified against IPC-2221 — not checkable from XML, REQUIRES DESIGN REVIEW.

## 8. BOM validation requirements

`docs/BOM/BOM_POWER_SUPPLY.csv`: 28 lines; 0 MPN; 80 references without value (inductors/capacitors of the buck stages must carry values for the TPS562208 compensation to be reproducible). Confirm 21 × TPS562208 vs the xlsx rail count; confirm the input connector rating (AK300/2 at 12–17 V, total current from the xlsx sum — not computed here).

## 9. Manufacturing package structure

Per common document, `<Board>` = `Power_Board`.

## 10. Acceptance criteria

| Criterion | Measure |
|---|---|
| Consistency | ERC consistency check passes after re-linking sch/brd in one EAGLE version |
| Placement/routing | 0 airwires, 0 off-board parts, final outline recorded |
| DRC/ERC | 0 errors |
| Gerber/drill | 2 Cu layers + mask/silk/paste/profile; NPTH 8 × Ø3.2; viewer matches `POWER_SUPPLY_outline.svg` (280 × 300 mm, or the revised outline) |
| BOM | 100 % MPN; all passives valued; datasheets for TPS562208 and LM2662 added to `7_Components Datasheets` |
| Design closure | PA supply (22 V rail) architecture decided and consistent with `Power Management V6.xlsx` and `RF_PA.sch` |
