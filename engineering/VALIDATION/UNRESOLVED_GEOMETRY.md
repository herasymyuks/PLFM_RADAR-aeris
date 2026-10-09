# Unresolved geometry register

Project AERIS-10 · VAL-GEO-01 · Rev A · 2026-10-09. Every mechanical quantity that the drawings need but no repository file provides. Nothing below was estimated into a drawing; where a planning estimate exists it is labelled ESTIMATE in the source document.

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

Photographs in `8_Utils/` (0044.jpg, Antenna_Array.jpg, two unnamed) show a prototype but carry no scale reference; per the addendum they were **not** used to derive dimensions.

## Update 2026-10-09 — proposals

G-04, G-05, G-07, G-08, G-09, G-12 now have PROPOSED values in `engineering/DESIGN/` (D-07…D-15); they stay open until the owner accepts the decisions and the assumed inputs (G-01 thickness, G-02 component heights, G-11 fasteners) are measured/specified. G-03 mass: FreeCAD volume-based estimate head ≈ 9.9 kg (includes component envelopes as solid plastic — overestimate), pedestal ≈ 12 kg + 1.1 kg stepper (`MECHANICAL/CAD/aeris10_mass_table.json`). G-06 antenna: PROPOSED patch panel 165 × 248 mm; G-10 Power Board outline unchanged.
