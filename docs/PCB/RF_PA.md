# RF Power Amplifier Board — Manufacturing Readiness Report

Board: `4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard/RF_PA.sch` / `RF_PA.brd` (EAGLE **9.6.2**, both). Status date 2026-10-08. Method: XML inspection only. **Readiness verdict: LAYOUT COMPLETE, NOT FABRICATION-READY** — fully routed and DRC-clean in the file, but no Gerber/drill/BOM/drawings exist and the stack-up is unconfirmed. RF performance is not assessed here.

> **Update 2026-10-09:** a generated manufacturing & drawing package (KiCad 10 conversion of the EAGLE board: Gerber, drill, PDF/SVG layer and assembly drawings, DXF, STEP, P&P, BOM, IPC-2581, IPC-D-356, DRC with DRU-derived rules, 3-D renders) is in `engineering/PCB/RF_PA/` (see its `README.md`, `STACKUP.md`). Schematic PDF/SVG: `engineering/ELECTRICAL/schematics/RF_PA/`. Netlist and connection reports: `engineering/ELECTRICAL/netlists/`. The package is SOURCE-DERIVED/PARTIAL, not designer-released; the EAGLE procedures below remain the path to the authoritative export.

## 1. Source-file inventory

| File | Size | Content (verified) |
|---|---|---|
| `RF_PA.sch` | 448 836 B | 1 sheet; 43 `<part>`, 25 physical; 15 nets; 7 embedded libraries; ERC approved 0; 0 single-pin nets |
| `RF_PA.brd` | 124 368 B | 25 elements (all top, all inside outline), 15 signals, 77 wires, **0 airwires**, 342 vias (0.15 ×103, 0.2 ×24, 0.35 ×215 — stitching/thermal), outline **35 × 60 mm**, 4 copper layers (`layerSetup=(1+2*15+16)`), DRU `PCBWay_4L_100um-Track`, 0 approved DRC |
| `docs/BOM/BOM_RF_PA.csv`, `docs/BOM/BOM_RF_PA.md`, `REFS_RF_PA.csv` | generated | 25 references, 11 line items, 0 MPN attributes, 6 references without value |
| `docs/MECHANICAL/drawings/RF_PA_outline.svg` | generated | outline + 7 × Ø3.2 mm NPTH at (2.6,2.6) (2.6,57.4) (32.4,57.4) (32.4,2.6) (17.5,2.6) (2.6,38) (32.4,38) |

Parts: `QPA2962_B` ×1 (U$1, Qorvo 10 W GaN PA — deviceset name is not the orderable MPN; datasheet `7_Components Datasheets.../QPA2962/QPA2962 Data Sheet.pdf` and S-parameters at 22 V / 1680 mA present), SMA 142-0731-211 ×2 (J1 RFIN, J2 RFOUT per silk), Molex 22-23-2021 (X2), 22-23-2031 (X3), terminal `con-ptr500`; silk labels `CURRENT SENSOR`, `VIN+`, `VIN-`, `VG`.

## 2. Layout state

| Item | Finding |
|---|---|
| Routing | complete (0 airwires) |
| DRC/ERC | 0 approved entries; sch/brd consistent |
| Min track | 0.204 mm (50 Ω microstrip width of the PCBWay note) |
| DRU | mdWireWire 0.15, mdCopperDimension 0.3, msDrill 0.15 mm; `mtCopper` third slot 0.07 mm (70 µm) although slot 3 is not an active layer — interpretation **UNRESOLVED**; `mtIsolate` 0.11 / 1.2 / 0.36 … mm |
| Stack-up | 4 layers; `Stack_Hybrid.png` (6 layers) does not describe this board; no vendor stack-up → **UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION** |
| Thermal | 215 × 0.35 mm vias under/around the PA: thermal path to the enclosure/heatsink is undocumented (no mechanical data) |
| System fit | README (`README.md:80`) says 16 PA boards for AERIS-10X at 10 W each; `Power Management V6.xlsx` budgets +22 V / 2 A × 16; the Power Board has no 22 V rail (`Vin [12-17]V`) — PA supply **UNRESOLVED** |

## 3. Missing manufacturing outputs

Gerber (4 Cu + mask + silk + paste + profile), drill, fab drawing (with the RF-critical notes: no mask over RF traces, impedance coupons), assembly drawing, BOM with MPN, pick-and-place, schematic PDF, netlist, DRC/ERC reports, stack-up confirmation: **all MISSING**.

## 4. Required software

EAGLE 9.6.2 / Fusion 360 Electronics / KiCad 8+; Gerber viewer.

## 5. CAD operations (exact)

P-EAGLE-01 (no mismatch expected), P-EAGLE-02, P-EAGLE-03 (`RATSNEST` → "Nothing to do" expected), P-EAGLE-04 with template *4 Layer* (inner layers 2 and 15), P-EAGLE-06/07/08. Add to the fab drawing (P-EAGLE-07) the text of `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` only after the designer confirms it applies to this 4-layer stack (the note's h = 0.102 mm does not match the DRU outer isolation 0.11 mm).

## 6. Export settings and expected filenames

RS-274X mm 4.4; Excellon mm; `RF_PA/Gerber/copper_top.gbr, copper_inner_2.gbr, copper_inner_3.gbr, copper_bottom.gbr, soldermask_top/bottom.gbr, silkscreen_top/bottom.gbr, solderpaste_top/bottom.gbr, profile.gbr`; `Drill/drill_1_16.xln, drill_npth.xln`; `RF_PA-smd.mnt`, `RF_PA-tht.mnt`; `RF_PA_BOM.csv`; `RF_PA_fab.pdf`; `RF_PA_assembly_top.pdf`; `RF_PA_schematic.pdf`.

## 7. DRC/ERC validation requirements

- DRC 0 errors with `PCBWay_4L_100um-Track`.
- ERC 0 errors.
- Stack-up: vendor confirms 4-layer construction, outer dielectric material/thickness, copper weight (the 70 µm DRU slot must be explained), and 50 Ω width 0.204 mm.
- Thermal/mechanical: PA mounting method (screws through the 7 NPTH holes, heatsink contact) defined — not derivable from the files.

## 8. BOM validation requirements

`docs/BOM/BOM_RF_PA.csv`: 11 lines, 0 MPN, 6 value-less references (bias/decoupling passives). The QPA2962 orderable part number (e.g. with package suffix) must be entered; gate-bias network values must be consistent with the DAC5578-driven `VG` range (−4 … −1.2 V per `Power Management V6.xlsx`).

## 9. Manufacturing package structure

Per common document, `<Board>` = `RF_PA`.

## 10. Acceptance criteria

| Criterion | Measure |
|---|---|
| DRC/ERC | 0 errors (already 0 approved in file; must be re-run) |
| Gerber/drill | 4 Cu + mask/silk/paste/profile; NPTH 7 × Ø3.2; PTH count = 342 vias + pads; viewer matches `RF_PA_outline.svg` (35 × 60 mm) |
| Stack-up | vendor drawing confirmed; RF layer mask-free as per impedance note |
| BOM | 100 % MPN; all 25 references valued/identified |
| System | PA supply voltage/current source decided; quantity per variant (16 for AERIS-10X) confirmed; RF performance (gain, P1dB at 10.5 GHz) remains **unverified** until measured |
