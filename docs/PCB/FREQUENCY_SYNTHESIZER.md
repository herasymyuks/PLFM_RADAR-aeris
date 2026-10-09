# Frequency Synthesizer Board — Manufacturing Readiness Report

Board: `4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch` / `.brd` (EAGLE **9.6.2**, both). Production folder: `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/`. Status date 2026-10-08. Method: XML inspection; `unzip -p` on the xlsx; PDF stream decoded. **Readiness verdict: LAYOUT COMPLETE, PARTIAL PRODUCTION DATA, NOT FABRICATION-READY** — routed and DRC-clean in the file, pick-and-place exists, but no Gerber/drill, the BOM has no manufacturer part numbers, and the stack-up evidence is contradictory.

> **Update 2026-10-09:** a generated manufacturing & drawing package (KiCad 10 conversion of the EAGLE board: Gerber, drill, PDF/SVG layer and assembly drawings, DXF, STEP, P&P, BOM, IPC-2581, IPC-D-356, DRC with DRU-derived rules, 3-D renders) is in `engineering/PCB/FREQUENCY_SYNTHESIZER/` (see its `README.md`, `STACKUP.md`). Schematic PDF/SVG: `engineering/ELECTRICAL/schematics/FREQUENCY_SYNTHESIZER/`. Netlist and connection reports: `engineering/ELECTRICAL/netlists/`. The package is SOURCE-DERIVED/PARTIAL, not designer-released; the EAGLE procedures below remain the path to the authoritative export.

## 1. Source-file inventory

| File | Size | Content (verified) |
|---|---|---|
| `Clocks_Freq_Synth_board.sch` | 1 825 451 B | 1 sheet; 318 `<part>`, 184 physical; 139 nets; 11 embedded libraries; ERC approved 0; single-pin nets 5 (`N$29`, `AD9523_OUT2±`, `AD9523_OUT3±` — unused clock outputs) |
| `Clocks_Freq_Synth_board.brd` | 469 841 B | 184 elements (top, all inside outline), 139 signals, 1 374 wires, **0 airwires**, 769 vias (0.15 ×212, 0.2 ×101, 0.3 ×391, 0.5 ×32, 1.0 ×32, 2.0 ×1), outline **100 × 100 mm**, 6 copper layers (`layerSetup=(1+2*3+14*15+16)`), DRU `PCBWay_6L_100um-Track`, 0 approved DRC |
| `4_Schematics and Boards Layout/4_7_Production Files/Frequency_Synthesizer/Clocks_Freq_Synth_board_BOM.xlsx` | 11 696 B | EAGLE `bom.ulp` CSV pasted into one column (41 rows); MPN/manufacturer columns empty; mojibake (`0.1ÂµF`) |
| `...-smd.mnt` (173 rows) / `mnt.csv` (identical) | 7 317 B | `RefDes,Value,Package,X,Y,Rot,Side`, all TOP |
| `...-tht.mnt` (10 rows) / `...-tht.csv` (identical) | 513 B | JP1, JP2, X10–X15, J3, J4 |
| `smd_.xlsx`, `th_.xlsx` | 15 927 / 10 052 B | the same P&P data retyped into columns |
| `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` | 3 757 B | RO4350B, h = 0.102 mm, Dk 3.48/3.66, 35 µm Cu, no mask on RF, 50 Ω w = 0.204 mm, 100 Ω diff w = 0.204 / s = 0.26 mm, via fence ≤ 1 mm pitch, coupons requested |
| `docs/BOM/BOM_FREQUENCY_SYNTHESIZER.csv`, `docs/BOM/BOM_FREQUENCY_SYNTHESIZER.md` | generated | 184 references, 40 line items, 0 MPN attributes, 47 references without value — consistent with the 40-line xlsx |
| `docs/MECHANICAL/drawings/FREQUENCY_SYNTHESIZER_outline.svg` | generated | outline + 4 × Ø3.2 mm NPTH at (5,5) (95,5) (95,95) (5,95) |

Key parts (deviceset names, MPN UNVERIFIED): AD9523BCPZ (IC1, clock generator), ADF4382ABCCZ ×2 (U1 TX LO, U6 RX LO), MTX2-143+ ×4 (baluns/transformers), ATS1005-3DB-FD-T05 ×4 (3 dB attenuators), OCXO ECOC-2522-100.000-3HC (X4), VCXO CVHD-950-50.000 ×2 (X5, X6), ferrite FBMH1608HL601-T ×4, 11 × SMA 142-0731-211, 2 × CJT-T-P-HH-ST-TH1 (J3, J4), 6 × Molex 22-23-2021, headers JP1 (2×6), JP2 (2×7). Silkscreen names the SMAs: `LO TX`, `LO RX`, `AUX. LO TX`, `AUX. LO RX`, `ADC`, `FPGA=ADC`, `FPGA=DAC`, `DAC`, `FPGA SYS. CLOCK`, `TEST`, `AD9523 PLL_OUT`, `TX_LO MUXOUT`, `RX_LO MUXOUT`.

Firmware cross-reference (AD9523 channel programming, `9_Firmware/.../main.cpp:965-1030`): OUT0/1 300 MHz → ADF4382 TX/RX reference; OUT4 400 MHz → ADC; OUT5 400 MHz → FPGA (`FPGA=ADC` SMA); OUT6 100 MHz → `FPGA SYS. CLOCK`; OUT7 20 MHz → `TEST`; OUT8/9 60 MHz SYNC; OUT10 120 MHz → `DAC`; OUT11 120 MHz → `FPGA=DAC`. VCXO 100 MHz on OSC_IN (`main.cpp:933`) — but the board carries a 100 MHz OCXO (X4) and two 50 MHz VCXOs (X5/X6): which oscillator drives which AD9523 input is **REQUIRES VERIFICATION** against the schematic nets (not resolved here).

## 2. Layout state

| Item | Finding |
|---|---|
| Routing / DRC / ERC | complete; 0 airwires; 0 approved DRC; 0 approved ERC; sch/brd part and net sets identical |
| Min track | 0.1 mm; RF widths 0.204 mm (×329) and 0.22 mm (×414) |
| DRU | mdWireWire 0.1, mdCopperDimension 0.3, msDrill 0.15, rvViaOuter 0.25, `mtIsolate = 0.11, 0.6, 0.11, 0.36, 0.2 …, 0.6, 0.11 mm`, thermals for vias off |
| Stack-up | EAGLE: 6 Cu, prepreg-outer/foil construction. `Stack_Hybrid.png`: 6 Cu with RO4350B 0.102 mm **outer cores**, FR-4 0.100 centre, prepregs 0.100. PCBWay note: h = 0.102 mm. Three sources disagree on construction and thickness → **UNRESOLVED — REQUIRES BOARD DESIGN VERIFICATION** |
| 2.0 mm via | one 2.0 mm drill via — check purpose (mounting/thermal) |

## 3. Missing manufacturing outputs

| Output | Status |
|---|---|
| Gerber (6 Cu + mask + silk + paste + profile) | MISSING |
| Excellon drill PTH/NPTH + map | MISSING |
| CAM job file | MISSING |
| Fab drawing with stack-up/impedance callouts | MISSING (impedance note exists, unlinked to a drawing) |
| Assembly drawing | MISSING |
| BOM with MPN | INCOMPLETE (xlsx and generated CSV both without MPN; 47 value-less references) |
| Pick-and-place | PRESENT (`-smd.mnt`, `-tht.mnt`); duplicates (`mnt.csv`, `-tht.csv`, `smd_.xlsx`, `th_.xlsx`) should be removed or regenerated from one source |
| Schematic PDF | MISSING |
| Netlist (IPC-D-356) | MISSING |
| DRC/ERC reports | MISSING (0 stored errors, but no report) |
| Vendor stack-up confirmation | MISSING |

## 4. Required software

EAGLE 9.6.2 / Fusion 360 Electronics / KiCad 8+; Gerber viewer; spreadsheet tool for BOM completion.

## 5. CAD operations (exact)

P-EAGLE-01, P-EAGLE-02, P-EAGLE-03 (`RATSNEST` → "Nothing to do" expected), P-EAGLE-04 with template *6 Layer* (inner layers 2, 3, 14, 15), P-EAGLE-06 (then fill MPN/manufacturer columns), P-EAGLE-07 (regenerate `-smd.mnt`/`-tht.mnt` from the current board to supersede the four duplicates; assembly and fab drawings), P-EAGLE-08.

## 6. Export settings and expected filenames

RS-274X mm 4.4; Excellon mm; `Frequency_Synthesizer/Gerber/copper_top.gbr, copper_inner_2.gbr … copper_inner_5.gbr, copper_bottom.gbr, soldermask_top/bottom.gbr, silkscreen_top/bottom.gbr, solderpaste_top/bottom.gbr, profile.gbr, gerber_job.gbrjob`; `Drill/drill_1_16.xln, drill_npth.xln`; `Clocks_Freq_Synth_board-smd.mnt`, `-tht.mnt` (regenerated); `Clocks_Freq_Synth_board_BOM.csv` (with MPN); `Clocks_Freq_Synth_board_fab.pdf`; `..._assembly_top.pdf`; `..._schematic.pdf`.

## 7. DRC/ERC validation requirements

- DRC 0 errors with `PCBWay_6L_100um-Track`; ERC 0 errors; the 5 single-pin nets (unused AD9523 outputs) dispositioned (leave unterminated only if the AD9523 datasheet permits — unused LVDS/CMOS outputs should be powered down in firmware; `main.cpp:961-968` sets unused channels' divider to 0 — verify `channels[i].output_dis`).
- Stack-up reconciled: one construction chosen; EAGLE `mtIsolate` updated to match; impedance note re-issued for that stack.
- Oscillator topology (OCXO vs VCXO into AD9523 REF/OSC_IN) verified against schematic nets and `main.cpp:933-935`.

## 8. BOM validation requirements

40 lines → add MPN and manufacturer to all; fill the 47 missing values; fix encoding (UTF-8 `µ`); mark the 11 SMA connectors as populated/DNP per variant; confirm OCXO/VCXO part numbers against `Power Management V6.xlsx` (ECOC-2522-100.000-3FC vs schematic ECOC-2522-100.000-3HC suffix difference; CVHD-950-100.000 in xlsx vs CVHD-950-50.000 in schematic — **CONFLICT, REQUIRES VERIFICATION**).

## 9. Manufacturing package structure

Per common document, `<Board>` = `Frequency_Synthesizer`; keep the existing `PCBWay_Impedance_Note_RO4350B_h0p102mm.pdf` under `reports/`.

## 10. Acceptance criteria

| Criterion | Measure |
|---|---|
| DRC/ERC | 0 errors, reports archived |
| Gerber/drill | 6 Cu + mask/silk/paste/profile; NPTH 4 × Ø3.2; PTH = 769 vias + pads; viewer matches `FREQUENCY_SYNTHESIZER_outline.svg` (100 × 100 mm) |
| Stack-up | one vendor-confirmed 6-layer stack consistent with the impedance note |
| BOM | 100 % MPN, 0 value-less references, oscillator conflict resolved |
| P&P | single regenerated pair of `.mnt` files, duplicates removed |
| Function (post-fab) | AD9523 lock (STATUS0/1 high), OUT6 = 100 MHz, OUT4/5 = 400 MHz, OUT10/11 = 120 MHz measured — hardware test, not a file check |
