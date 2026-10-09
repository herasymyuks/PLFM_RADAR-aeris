# Main Board rev. B — unrouted connections

`beta/pcb/MAIN_BOARD_REVB/UNROUTED.md` · 2026-10-09 · source: `exports/reports/DRC_report.json` (59 unconnected items, all on rev. B nets).

## 1. FT601 FIFO bus + control (46 nets) — blocked by the U42 bank-35 breakout

Nets: FT_DATA_0..31, FT_BE_0..3, FT_CLK, FT_TXE_N, FT_RXF_N, FT_WR_N, FT_RD_N, FT_OE_N, FT_SIWU_N, FT_RESET_N, FT_WAKEUP_N, FT_GPIO0 (FT_GPIO1 is routed).

Measured escape availability (via 0.45 mm + 0.1 mm clearance at the four dog-bone positions ±0.5/±0.5 mm of each ball, all copper layers): **no free position** for A2, A3, A7, B1, B2, B6, C1, C2, C3, C4, C6, D1, D3, D4, D6, E1, E2, E3, E5, E6, F2, F3, F4, F5, G4, G5, H4, H5, J1, J3, J5, K1, K2, K3, K5, L2 (36 balls); one free position for A4, A5, B4, B5, B7, C7, G1, H1, H3; two for G2, H2. The occupying copper is the existing rev. A fan-out of neighbouring balls (locked in this BETA).

What is needed (layout owner): re-do the bank-35 corner breakout of U42 (outer two rows on F.Cu, inner rows by dog-bone vias to In2/In3/In5/In7, which requires moving existing vias of adjacent nets), then route the 46 nets as one group at 0.204 mm, length-matched to ±25 mm (KiCad *Tune length* on the group, 100 MHz single-ended); alternatively choose bank-35 balls on the two outer rows only (the pin plan in `ft601_pin_assignment.csv` would have to be revised together with the XDC).

## 2. FT601 power / clock / USB (open items)

| Net | Open connections | What is needed |
|---|---|---|
| FT_VD10 | 5 | connect U6 pads 3/30/33/39/48 together and to C_VD10_1..4 — the QFN pads face other-net pads on all sides; route on F.Cu around the exposed pad corners or via-in-pad to an inner pour |
| +3V3_FT | 5 | feed from the L19/C184-186 filter (y ≈ −232) to U6 VCC33/VCCIO pads; 4 autorouter vias are dangling (remove or connect) |
| FT_AVDD | 1 | U6 pad 2 to C_AVDD_1 (0.6 mm stub) |
| FT_XO | 1 | U6 pad 22 to Y_FT pad 3 |
| USB_SSTX_P | 1 | U6 pad 32 to C_SSTX_P — route coupled with USB_SSTX_N (0.204/0.18 mm) |

## 3. Prepared but not executed in this session (tool permission denied)

1. Second Freerouting pass restricted to FT_VD10, +3V3_FT, FT_AVDD, FT_XO, USB_SSTX_P (`beta_specctra.py export` → `beta_dsn_restrict.py --keep …` → Freerouting → `beta_specctra.py merge --nets …`).
2. Widen the 14 Freerouting neck-downs below 0.1 mm (DRC `track_width`) to 0.1 mm.
3. Move C_XI / C_XO 0.5 mm away from Y_FT (2 courtyard overlaps).
