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

![F6.1 — Frequency Synthesizer schematic, single sheet: AD9523 clock generator, 2 × ADF4382 LO synthesizers, OCXO/VCXO, 11 SMA outputs, control headers JP1/JP2 (status: SOURCE-DERIVED; source: engineering/ELECTRICAL/schematics/FREQUENCY_SYNTHESIZER/png/FREQUENCY_SYNTHESIZER_schematic_sheet1.png; produced by tools/render_eagle_schematic.py)](engineering/ELECTRICAL/schematics/FREQUENCY_SYNTHESIZER/png/FREQUENCY_SYNTHESIZER_schematic_sheet1.png)

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

Change: 43 silkscreen reference texts moved to the nearest free position (≤ 3 mm, 0.05 mm step; `tools/beta_silk_nudge.py`, `silk_nudges.json`); 103 texts remain in conflict because the 0201-dense board has no free spot within 3 mm (`silk_conflicts_remaining.json`). Disposition of all 639 items (source: `beta/pcb/FREQUENCY_SYNTHESIZER/DRC_DISPOSITION.md` §1): 7 courtyard overlaps REAL (review) — pairs C25↔L10, L12↔C45, L12↔C33, C27↔L10, L11↔C29, L11↔C31, L9↔C21; the pads do not touch, designer to confirm that the L5650M inductor body does not collide with the adjacent capacitors at assembly; 35 dangling GND arc stubs 0.002–0.212 mm inside the GND pour — COSMETIC; silkscreen 147 → 103 texts in conflict (measured uncapped) — COSMETIC, fab clips silk on pads; solder-mask bridges — FAB REVIEW (PCBWay minimum mask dam 0.1 mm, CAM merges apertures). Recommendation for the production revision: hide 0201/0402 reference designators on silk.

## 6.5 Layer plots and 3-D renders

![F6.2a — Frequency Synthesizer top composite (F.Cu + F.SilkS + Edge.Cuts), 100 × 100 mm (status: SOURCE-DERIVED; source: engineering/PCB/FREQUENCY_SYNTHESIZER/svg/FREQUENCY_SYNTHESIZER_top_composite.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/FREQUENCY_SYNTHESIZER_top_composite.png)

![F6.2b — Frequency Synthesizer bottom composite, mirrored (B.Cu + B.SilkS + Edge.Cuts); the AD9523_OUT8/9 pairs run on B.Cu (status: SOURCE-DERIVED; source: engineering/PCB/FREQUENCY_SYNTHESIZER/svg/FREQUENCY_SYNTHESIZER_bottom_composite_mirrored.svg; produced by tools/svg_sheets_to_pdf.py --png-dir manual/figures)](manual/figures/FREQUENCY_SYNTHESIZER_bottom_composite_mirrored.png)

![F6.3a — Frequency Synthesizer 3-D render, top, KiCad conversion; no component models (status: SOURCE-DERIVED; source: engineering/PCB/FREQUENCY_SYNTHESIZER/3d/FREQUENCY_SYNTHESIZER_render_top.png; produced by kicad-cli pcb render, tools/kicad_pcb_pipeline.sh)](engineering/PCB/FREQUENCY_SYNTHESIZER/3d/FREQUENCY_SYNTHESIZER_render_top.png)

![F6.3b — Frequency Synthesizer BETA board, isometric render (silkscreen nudged, copper identical to the source) (status: BETA; source: beta/pcb/FREQUENCY_SYNTHESIZER/exports/3d/FREQUENCY_SYNTHESIZER_render_isometric.png; produced by beta/pcb/tools/beta_export_package.sh)](beta/pcb/FREQUENCY_SYNTHESIZER/exports/3d/FREQUENCY_SYNTHESIZER_render_isometric.png)

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
