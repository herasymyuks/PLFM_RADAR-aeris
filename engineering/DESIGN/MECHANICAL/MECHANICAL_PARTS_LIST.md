# AERIS-10 — Mechanical parts list (radar head + pedestal) — DSN-MECH-PL Rev A

Date 2026-10-09 · from `CAD/detail/parts_list.json` (FreeCAD model `tools/design_enclosure_detail_freecad.py`) · Status: PROPOSED DESIGN · masses are volume × density estimates.

Head ≈ 6.4 kg (structure only, PCBs/antenna not included except as noted), pedestal ≈ 12.4 kg (incl. stepper 1.1 kg, bearing/slip ring as modelled).

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

## Fastener totals (from the per-part lists)

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

## Sealing and finish

- Lid: EPDM 15 × 3 mm self-adhesive gasket on the three top flanges, compressed to 2 mm by the M4 screws (pitch 60 mm). Front plate: 1.5 mm EPDM strip on the two front flanges (same pattern).
- Radome window: PTFE 2 mm clamped by the 2 mm Al frame with EPDM 1.5 mm gasket, M3 × 18. Alternative: 2 mm Rogers/ABS radome if PTFE loss is acceptable but cost is not.
- Cable entry: 100 × 100 gland plate under the base with M32 (power) and M20 (USB) IP68 glands; the Ø70 base hole lets the harness reach the slip ring rotor.
- Finish: chromate conversion (Alodine) + powder coat RAL 7035 outside; bare chromate inside for grounding at the flanges; PA plate bare 6061 with thermal pads.
- Open: bend reliefs and corner welds of the tray, stiffeners of the 315 mm lid (2.5 mm may need a 20 mm hem), fan mounting brackets, antenna spacer material, earthing stud, lifting points, mast interface.
