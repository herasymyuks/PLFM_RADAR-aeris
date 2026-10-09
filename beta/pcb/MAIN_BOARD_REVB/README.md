# Main Board rev. B (PROPOSAL) — FT601 USB 3.0 host interface wired

Project AERIS-10 · `beta/pcb/MAIN_BOARD_REVB/` · 2026-10-09 · **Status: BETA PROPOSAL — explicit netlist change (rev. B); partially routed; DRC-checked; not reviewed by the original designer; not fabricated.**

> **The EAGLE schematic `4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch` has NOT been changed and no longer matches this board.** This KiCad rev. B is the proposal; the designer must enter the same connections (table §3) and parts (§4) in the schematic, verify them against the FT601 datasheet (not in the repository) and re-annotate, before any rev. B layout is released.

Source: `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb` (rev. A BETA, unchanged). Design input: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §4, `ft601_pin_assignment.csv`, `ft601_added_parts_BOM.csv`, `ft601_bank35.xdc`. Reproducible with `beta/pcb/tools/beta_revb_ft601.py` (every pcbnew call is in that script).

## 1. Result

| Check | Rev. A BETA (`MAIN_BOARD/`) | Rev. B after netlist change, before routing | Rev. B after routing (exports) |
|---|---|---|---|
| unconnected_items | 0 | 129 | 59 |
| clearance | 72 | 76 | 72 |
| copper_edge_clearance | 0 | 0 | 1 |
| courtyards_overlap | 0 | 2 | 2 |
| hole_clearance | 87 | 87 | 87 |
| shorting_items | 125 | 125 | 125 |
| silk_edge_clearance | 3 | 3 | 3 |
| silk_over_copper | 199 | 199 | 199 |
| silk_overlap | 199 | 199 | 199 |
| solder_mask_bridge | 199 | 199 | 199 |
| track_dangling | 130 | 130 | 130 |
| track_width | 0 | 0 | 14 |
| via_dangling | 35 | 35 | 40 |
| **DRC total** | 1049 | 1055 | 1071 |

* **Unconnected 59** — every one of them is a new rev. B connection (by net: FT_VD10 5, +3V3_FT 5, FT_AVDD 1, FT_BE_0 1, FT_BE_1 1, FT_BE_2 1, FT_BE_3 1, FT_TXE_N 1, FT_RXF_N 1, FT_SIWU_N 1, FT_WR_N 1, FT_RD_N 1, FT_OE_N 1, FT_RESET_N 1, FT_WAKEUP_N 1, FT_GPIO0 1, FT_XO 1, USB_SSTX_P 1, FT_DATA_0 1, FT_DATA_1 1, FT_DATA_2 1, FT_DATA_3 1, FT_DATA_4 1, FT_DATA_5 1, FT_DATA_6 1, FT_DATA_7 1, FT_DATA_8 1, FT_DATA_9 1, FT_DATA_10 1, FT_DATA_11 1, FT_DATA_12 1, FT_DATA_13 1, FT_DATA_14 1, FT_DATA_15 1, FT_CLK 1, FT_DATA_16 1, FT_DATA_17 1, FT_DATA_18 1, FT_DATA_19 1, FT_DATA_20 1, FT_DATA_21 1, FT_DATA_22 1, FT_DATA_23 1, FT_DATA_24 1, FT_DATA_25 1, FT_DATA_26 1, FT_DATA_27 1, FT_DATA_28 1, FT_DATA_29 1, FT_DATA_30 1, FT_DATA_31 1). The rev. A board had 0. See `UNROUTED.md`.
* Routed and connected: 17 of the 64 new nets (USB D±, both SuperSpeed RX lines, SSTX_N and both SSTX_C lines, CC1/CC2, USB_VBUS, FT_VBUS_DET, FT_RREF, FT_XI, FT_GPIO1, partly +3V3_FT/FT_VD10/FT_AVDD/FT_XO).
* **The 32-bit FIFO bus and its control lines (46 of 47 FPGA-side signals) are NOT routed.** Root cause, measured: 36 of the 47 bank-35 balls of U42 (XC7A50T FTG256, 1.0 mm pitch) have **no free position for an escape via** — the four dog-bone positions around each ball are already occupied by the existing BGA fan-out vias/traces of neighbouring balls (`tools`-measured, list in `UNROUTED.md`). Freerouting (1 pass, 25 min, existing copper locked) fanned out the FT601 side but could not reach these balls; its partial copper on the 47 open bus nets (127 items) was removed again so the board is left clean (`removed_unfinished_routes.json`). Routing the bus requires re-doing the U42 bank-35 breakout (moving existing vias/traces) — a layout-owner decision outside this BETA's "existing tracks locked" rule.
* New DRC items caused by rev. B copper: 9 `track_width` (Freerouting neck-down 0.075 mm on +3V3_FT/CC1/CC2 at 0.4 mm-pitch pads; to be widened to 0.1 mm), 2 courtyard overlaps (Y_FT ↔ C_XI/C_XO — move the load caps 0.5 mm), 1 copper-edge (USB_CC2 inner track 0.2 mm from the J_USB3 NPTH peg), 5 dangling vias (+3V3_FT ×4, USB_SSTX_C_P). All other DRC items are the rev. A ones (see `../MAIN_BOARD/README.md`). Two further scripted clean-ups (second restricted Freerouting pass on the open power nets; widening the neck-downs) were prepared but **not executed — the tool-permission system blocked those board writes in this session**; they are listed in `UNROUTED.md` as next steps.

## 2. Routing geometry and lengths

| Group | Rule used | Achieved |
|---|---|---|
| FT_BUS (FT_DATA_0..31, FT_BE_0..3, FT_CLK, control, GPIO) | netclass `FT_BUS` 0.204 mm (50 Ω microstrip on the 0.102 mm RO4350B outer layer per `../MAIN_BOARD/FAB_NOTES.md`; on inner layers ≈ 42 Ω stripline estimate, FR-4, not field-solved), clearance 0.1 mm (DRU), length-match target ±25 mm | only `FT_GPIO1` routed: 37.57 mm, 3 vias, F.Cu/In2/In7 — **no skew figure exists for the bus because it is unrouted**; FT601→bank-35 Manhattan distance is 20–35 mm, so ±25 mm is achievable once the breakout exists |
| USB SuperSpeed + D± | netclass `USB_DIFF` width 0.204 mm, pair gap 0.18 mm (≈ 90 Ω edge-coupled microstrip on RO4350B h = 0.102 mm, closed-form estimate 91 Ω, fab to solve) | Freerouting routes pair members as single traces (coupling not enforced): SSRX_P/N 29.28 / 29.41 mm (skew 0.13 mm), D+/D− 23.72 / 27.12 mm (skew 3.4 mm), SSTX_C_P/N 9.08 / 8.72 mm, SSTX_N 16.08 mm (SSTX_P open); neck-down to 0.153 mm at pads. **Pairs must be re-routed coupled (KiCad diff-pair router, 0.204/0.18 mm) before release** |
| Power `FT_PWR` (FT_VD10, FT_AVDD, USB_VBUS) | 0.3 mm | USB_VBUS 34.5 mm, FT_AVDD 18.6 mm; FT_VD10 only partially connected |

Per-net lengths: run `beta/pcb/tools/beta_net_lengths.py MAIN_BOARD_REVB.kicad_pcb --prefix FT_,USB_,+3V3_FT`.

## 3. Netlist delta (every new connection; also `NETLIST_DELTA.csv`)

64 new nets, 123 pad connections on existing parts (U6, U42), 71 pad connections on 20 added parts. U6 pads 2, 14, 20, 24, 28, 37, 38, 49, 59, 68 were on single-pin nets named after the pin (`AVDD`, `VCCIO_2`, …) in rev. A — they were moved to the nets below.

| # | Change | Net | Ref | Pad | Previous net | Note |
|---|---|---|---|---|---|---|
| 1 | NEW NET | `FT_CLK` |  |  | — |  |
| 2 | CONNECT | `FT_CLK` | U6 | 58 | — | FT601 CLK |
| 3 | CONNECT | `FT_CLK` | U42 | C4 | — | IO_L12N_T1_MRCC_35 (LVCMOS33) out |
| 4 | NEW NET | `FT_DATA_0` |  |  | — |  |
| 5 | CONNECT | `FT_DATA_0` | U6 | 40 | — | FT601 DATA_0 |
| 6 | CONNECT | `FT_DATA_0` | U42 | A2 | — | IO_L8N_T1_AD14N_35 (LVCMOS33) bidir |
| 7 | NEW NET | `FT_DATA_1` |  |  | — |  |
| 8 | CONNECT | `FT_DATA_1` | U6 | 41 | — | FT601 DATA_1 |
| 9 | CONNECT | `FT_DATA_1` | U42 | A3 | — | IO_L4N_T0_35 (LVCMOS33) bidir |
| 10 | NEW NET | `FT_DATA_2` |  |  | — |  |
| 11 | CONNECT | `FT_DATA_2` | U6 | 42 | — | FT601 DATA_2 |
| 12 | CONNECT | `FT_DATA_2` | U42 | A4 | — | IO_L3N_T0_DQS_AD5N_35 (LVCMOS33) bidir |
| 13 | NEW NET | `FT_DATA_3` |  |  | — |  |
| 14 | CONNECT | `FT_DATA_3` | U6 | 43 | — | FT601 DATA_3 |
| 15 | CONNECT | `FT_DATA_3` | U42 | A5 | — | IO_L3P_T0_DQS_AD5P_35 (LVCMOS33) bidir |
| 16 | NEW NET | `FT_DATA_4` |  |  | — |  |
| 17 | CONNECT | `FT_DATA_4` | U6 | 44 | — | FT601 DATA_4 |
| 18 | CONNECT | `FT_DATA_4` | U42 | A7 | — | IO_L1N_T0_AD4N_35 (LVCMOS33) bidir |
| 19 | NEW NET | `FT_DATA_5` |  |  | — |  |
| 20 | CONNECT | `FT_DATA_5` | U6 | 45 | — | FT601 DATA_5 |
| 21 | CONNECT | `FT_DATA_5` | U42 | B1 | — | IO_L9N_T1_DQS_AD7N_35 (LVCMOS33) bidir |
| 22 | NEW NET | `FT_DATA_6` |  |  | — |  |
| 23 | CONNECT | `FT_DATA_6` | U6 | 46 | — | FT601 DATA_6 |
| 24 | CONNECT | `FT_DATA_6` | U42 | B2 | — | IO_L8P_T1_AD14P_35 (LVCMOS33) bidir |
| 25 | NEW NET | `FT_DATA_7` |  |  | — |  |
| 26 | CONNECT | `FT_DATA_7` | U6 | 47 | — | FT601 DATA_7 |
| 27 | CONNECT | `FT_DATA_7` | U42 | B4 | — | IO_L4P_T0_35 (LVCMOS33) bidir |
| 28 | NEW NET | `FT_DATA_8` |  |  | — |  |
| 29 | CONNECT | `FT_DATA_8` | U6 | 50 | — | FT601 DATA_8 |
| 30 | CONNECT | `FT_DATA_8` | U42 | B5 | — | IO_L2N_T0_AD12N_35 (LVCMOS33) bidir |
| 31 | NEW NET | `FT_DATA_9` |  |  | — |  |
| 32 | CONNECT | `FT_DATA_9` | U6 | 51 | — | FT601 DATA_9 |
| 33 | CONNECT | `FT_DATA_9` | U42 | B6 | — | IO_L2P_T0_AD12P_35 (LVCMOS33) bidir |
| 34 | NEW NET | `FT_DATA_10` |  |  | — |  |
| 35 | CONNECT | `FT_DATA_10` | U6 | 52 | — | FT601 DATA_10 |
| 36 | CONNECT | `FT_DATA_10` | U42 | B7 | — | IO_L1P_T0_AD4P_35 (LVCMOS33) bidir |
| 37 | NEW NET | `FT_DATA_11` |  |  | — |  |
| 38 | CONNECT | `FT_DATA_11` | U6 | 53 | — | FT601 DATA_11 |
| 39 | CONNECT | `FT_DATA_11` | U42 | C1 | — | IO_L9P_T1_DQS_AD7P_35 (LVCMOS33) bidir |
| 40 | NEW NET | `FT_DATA_12` |  |  | — |  |
| 41 | CONNECT | `FT_DATA_12` | U6 | 54 | — | FT601 DATA_12 |
| 42 | CONNECT | `FT_DATA_12` | U42 | C2 | — | IO_L7N_T1_AD6N_35 (LVCMOS33) bidir |
| 43 | NEW NET | `FT_DATA_13` |  |  | — |  |
| 44 | CONNECT | `FT_DATA_13` | U6 | 55 | — | FT601 DATA_13 |
| 45 | CONNECT | `FT_DATA_13` | U42 | C3 | — | IO_L7P_T1_AD6P_35 (LVCMOS33) bidir |
| 46 | NEW NET | `FT_DATA_14` |  |  | — |  |
| 47 | CONNECT | `FT_DATA_14` | U6 | 56 | — | FT601 DATA_14 |
| 48 | CONNECT | `FT_DATA_14` | U42 | C6 | — | IO_L5N_T0_AD13N_35 (LVCMOS33) bidir |
| 49 | NEW NET | `FT_DATA_15` |  |  | — |  |
| 50 | CONNECT | `FT_DATA_15` | U6 | 57 | — | FT601 DATA_15 |
| 51 | CONNECT | `FT_DATA_15` | U42 | C7 | — | IO_L5P_T0_AD13P_35 (LVCMOS33) bidir |
| 52 | NEW NET | `FT_DATA_16` |  |  | — |  |
| 53 | CONNECT | `FT_DATA_16` | U6 | 60 | — | FT601 DATA_16 |
| 54 | CONNECT | `FT_DATA_16` | U42 | D1 | — | IO_L10N_T1_AD15N_35 (LVCMOS33) bidir |
| 55 | NEW NET | `FT_DATA_17` |  |  | — |  |
| 56 | CONNECT | `FT_DATA_17` | U6 | 61 | — | FT601 DATA_17 |
| 57 | CONNECT | `FT_DATA_17` | U42 | D3 | — | IO_L11N_T1_SRCC_35 (LVCMOS33) bidir |
| 58 | NEW NET | `FT_DATA_18` |  |  | — |  |
| 59 | CONNECT | `FT_DATA_18` | U6 | 62 | — | FT601 DATA_18 |
| 60 | CONNECT | `FT_DATA_18` | U42 | D4 | — | IO_L12P_T1_MRCC_35 (LVCMOS33) bidir |
| 61 | NEW NET | `FT_DATA_19` |  |  | — |  |
| 62 | CONNECT | `FT_DATA_19` | U6 | 63 | — | FT601 DATA_19 |
| 63 | CONNECT | `FT_DATA_19` | U42 | D6 | — | IO_L6P_T0_35 (LVCMOS33) bidir |
| 64 | NEW NET | `FT_DATA_20` |  |  | — |  |
| 65 | CONNECT | `FT_DATA_20` | U6 | 64 | — | FT601 DATA_20 |
| 66 | CONNECT | `FT_DATA_20` | U42 | E1 | — | IO_L15N_T2_DQS_35 (LVCMOS33) bidir |
| 67 | NEW NET | `FT_DATA_21` |  |  | — |  |
| 68 | CONNECT | `FT_DATA_21` | U6 | 65 | — | FT601 DATA_21 |
| 69 | CONNECT | `FT_DATA_21` | U42 | E2 | — | IO_L10P_T1_AD15P_35 (LVCMOS33) bidir |
| 70 | NEW NET | `FT_DATA_22` |  |  | — |  |
| 71 | CONNECT | `FT_DATA_22` | U6 | 66 | — | FT601 DATA_22 |
| 72 | CONNECT | `FT_DATA_22` | U42 | E3 | — | IO_L11P_T1_SRCC_35 (LVCMOS33) bidir |
| 73 | NEW NET | `FT_DATA_23` |  |  | — |  |
| 74 | CONNECT | `FT_DATA_23` | U6 | 67 | — | FT601 DATA_23 |
| 75 | CONNECT | `FT_DATA_23` | U42 | E5 | — | IO_L13N_T2_MRCC_35 (LVCMOS33) bidir |
| 76 | NEW NET | `FT_DATA_24` |  |  | — |  |
| 77 | CONNECT | `FT_DATA_24` | U6 | 69 | — | FT601 DATA_24 |
| 78 | CONNECT | `FT_DATA_24` | U42 | E6 | — | IO_0_35 (LVCMOS33) bidir |
| 79 | NEW NET | `FT_DATA_25` |  |  | — |  |
| 80 | CONNECT | `FT_DATA_25` | U6 | 70 | — | FT601 DATA_25 |
| 81 | CONNECT | `FT_DATA_25` | U42 | F2 | — | IO_L15P_T2_DQS_35 (LVCMOS33) bidir |
| 82 | NEW NET | `FT_DATA_26` |  |  | — |  |
| 83 | CONNECT | `FT_DATA_26` | U6 | 71 | — | FT601 DATA_26 |
| 84 | CONNECT | `FT_DATA_26` | U42 | F3 | — | IO_L14N_T2_SRCC_35 (LVCMOS33) bidir |
| 85 | NEW NET | `FT_DATA_27` |  |  | — |  |
| 86 | CONNECT | `FT_DATA_27` | U6 | 72 | — | FT601 DATA_27 |
| 87 | CONNECT | `FT_DATA_27` | U42 | F4 | — | IO_L14P_T2_SRCC_35 (LVCMOS33) bidir |
| 88 | NEW NET | `FT_DATA_28` |  |  | — |  |
| 89 | CONNECT | `FT_DATA_28` | U6 | 73 | — | FT601 DATA_28 |
| 90 | CONNECT | `FT_DATA_28` | U42 | F5 | — | IO_L13P_T2_MRCC_35 (LVCMOS33) bidir |
| 91 | NEW NET | `FT_DATA_29` |  |  | — |  |
| 92 | CONNECT | `FT_DATA_29` | U6 | 74 | — | FT601 DATA_29 |
| 93 | CONNECT | `FT_DATA_29` | U42 | G1 | — | IO_L17N_T2_35 (LVCMOS33) bidir |
| 94 | NEW NET | `FT_DATA_30` |  |  | — |  |
| 95 | CONNECT | `FT_DATA_30` | U6 | 75 | — | FT601 DATA_30 |
| 96 | CONNECT | `FT_DATA_30` | U42 | G2 | — | IO_L17P_T2_35 (LVCMOS33) bidir |
| 97 | NEW NET | `FT_DATA_31` |  |  | — |  |
| 98 | CONNECT | `FT_DATA_31` | U6 | 76 | — | FT601 DATA_31 |
| 99 | CONNECT | `FT_DATA_31` | U42 | G4 | — | IO_L16N_T2_35 (LVCMOS33) bidir |
| 100 | NEW NET | `FT_BE_0` |  |  | — |  |
| 101 | CONNECT | `FT_BE_0` | U6 | 4 | — | FT601 BE_0 |
| 102 | CONNECT | `FT_BE_0` | U42 | G5 | — | IO_L16P_T2_35 (LVCMOS33) bidir |
| 103 | NEW NET | `FT_BE_1` |  |  | — |  |
| 104 | CONNECT | `FT_BE_1` | U6 | 5 | — | FT601 BE_1 |
| 105 | CONNECT | `FT_BE_1` | U42 | H1 | — | IO_L20N_T3_35 (LVCMOS33) bidir |
| 106 | NEW NET | `FT_BE_2` |  |  | — |  |
| 107 | CONNECT | `FT_BE_2` | U6 | 6 | — | FT601 BE_2 |
| 108 | CONNECT | `FT_BE_2` | U42 | H2 | — | IO_L20P_T3_35 (LVCMOS33) bidir |
| 109 | NEW NET | `FT_BE_3` |  |  | — |  |
| 110 | CONNECT | `FT_BE_3` | U6 | 7 | — | FT601 BE_3 |
| 111 | CONNECT | `FT_BE_3` | U42 | H3 | — | IO_L21N_T3_DQS_35 (LVCMOS33) bidir |
| 112 | NEW NET | `FT_TXE_N` |  |  | — |  |
| 113 | CONNECT | `FT_TXE_N` | U6 | 8 | — | FT601 TXE_N |
| 114 | CONNECT | `FT_TXE_N` | U42 | H4 | — | IO_L18N_T2_35 (LVCMOS33) out |
| 115 | NEW NET | `FT_RXF_N` |  |  | — |  |
| 116 | CONNECT | `FT_RXF_N` | U6 | 9 | — | FT601 RXF_N |
| 117 | CONNECT | `FT_RXF_N` | U42 | H5 | — | IO_L18P_T2_35 (LVCMOS33) out |
| 118 | NEW NET | `FT_WR_N` |  |  | — |  |
| 119 | CONNECT | `FT_WR_N` | U6 | 11 | — | FT601 WR_N |
| 120 | CONNECT | `FT_WR_N` | U42 | J1 | — | IO_L22N_T3_35 (LVCMOS33) in |
| 121 | NEW NET | `FT_RD_N` |  |  | — |  |
| 122 | CONNECT | `FT_RD_N` | U6 | 12 | — | FT601 RD_N |
| 123 | CONNECT | `FT_RD_N` | U42 | J3 | — | IO_L21P_T3_DQS_35 (LVCMOS33) in |
| 124 | NEW NET | `FT_OE_N` |  |  | — |  |
| 125 | CONNECT | `FT_OE_N` | U6 | 13 | — | FT601 OE_N |
| 126 | CONNECT | `FT_OE_N` | U42 | J5 | — | IO_L19P_T3_35 (LVCMOS33) in |
| 127 | NEW NET | `FT_SIWU_N` |  |  | — |  |
| 128 | CONNECT | `FT_SIWU_N` | U6 | 10 | — | FT601 SIWU_N |
| 129 | CONNECT | `FT_SIWU_N` | U42 | K1 | — | IO_L22P_T3_35 (LVCMOS33) in |
| 130 | NEW NET | `FT_RESET_N` |  |  | — |  |
| 131 | CONNECT | `FT_RESET_N` | U6 | 15 | — | FT601 RESET_N |
| 132 | CONNECT | `FT_RESET_N` | U42 | K2 | — | IO_L24N_T3_35 (LVCMOS33) in |
| 133 | NEW NET | `FT_WAKEUP_N` |  |  | — |  |
| 134 | CONNECT | `FT_WAKEUP_N` | U6 | 16 | — | FT601 WAKEUP_N |
| 135 | CONNECT | `FT_WAKEUP_N` | U42 | K3 | — | IO_L24P_T3_35 (LVCMOS33) in |
| 136 | NEW NET | `FT_GPIO0` |  |  | — |  |
| 137 | CONNECT | `FT_GPIO0` | U6 | 17 | — | FT601 GPIO0 |
| 138 | CONNECT | `FT_GPIO0` | U42 | K5 | — | IO_25_35 (LVCMOS33) out |
| 139 | NEW NET | `FT_GPIO1` |  |  | — |  |
| 140 | CONNECT | `FT_GPIO1` | U6 | 18 | — | FT601 GPIO1 |
| 141 | CONNECT | `FT_GPIO1` | U42 | L2 | — | IO_L23N_T3_35 (LVCMOS33) out |
| 142 | CONNECT | `+3V3_FT` | U6 | 20 | VCC33_2 | VCC33 |
| 143 | CONNECT | `+3V3_FT` | U6 | 24 | VCC33_3 | VCC33 |
| 144 | CONNECT | `+3V3_FT` | U6 | 38 | VCC33 | VCC33 |
| 145 | CONNECT | `+3V3_FT` | U6 | 14 | VCCIO_2 | VCCIO |
| 146 | CONNECT | `+3V3_FT` | U6 | 49 | VCCIO_3 | VCCIO |
| 147 | CONNECT | `+3V3_FT` | U6 | 59 | VCCIO_4 | VCCIO |
| 148 | CONNECT | `+3V3_FT` | U6 | 68 | VCCIO | VCCIO |
| 149 | CONNECT | `GND` | U6 | 77 | — | GND / exposed pad |
| 150 | CONNECT | `GND` | U6 | 1 | — | GND / exposed pad |
| 151 | CONNECT | `GND` | U6 | 26 | — | GND / exposed pad |
| 152 | CONNECT | `GND` | U6 | 29 | — | GND / exposed pad |
| 153 | CONNECT | `GND` | U6 | 36 | — | GND / exposed pad |
| 154 | NEW NET | `FT_AVDD` |  |  | — |  |
| 155 | CONNECT | `FT_AVDD` | U6 | 2 | AVDD | AVDD/VDDA via FB_A from +3V3_FT |
| 156 | CONNECT | `FT_AVDD` | U6 | 28 | VDDA | AVDD/VDDA via FB_A from +3V3_FT |
| 157 | NEW NET | `FT_VD10` |  |  | — |  |
| 158 | CONNECT | `FT_VD10` | U6 | 3 | — | VD10/DV10 1.0 V core — VERIFY datasheet (internal regulator output assumed) |
| 159 | CONNECT | `FT_VD10` | U6 | 30 | — | VD10/DV10 1.0 V core — VERIFY datasheet (internal regulator output assumed) |
| 160 | CONNECT | `FT_VD10` | U6 | 33 | — | VD10/DV10 1.0 V core — VERIFY datasheet (internal regulator output assumed) |
| 161 | CONNECT | `FT_VD10` | U6 | 48 | — | VD10/DV10 1.0 V core — VERIFY datasheet (internal regulator output assumed) |
| 162 | CONNECT | `FT_VD10` | U6 | 39 | — | VD10/DV10 1.0 V core — VERIFY datasheet (internal regulator output assumed) |
| 163 | NEW NET | `FT_XI` |  |  | — |  |
| 164 | CONNECT | `FT_XI` | U6 | 21 | — | XI |
| 165 | NEW NET | `FT_XO` |  |  | — |  |
| 166 | CONNECT | `FT_XO` | U6 | 22 | — | XO |
| 167 | NEW NET | `FT_RREF` |  |  | — |  |
| 168 | CONNECT | `FT_RREF` | U6 | 27 | — | RREF |
| 169 | NEW NET | `FT_VBUS_DET` |  |  | — |  |
| 170 | CONNECT | `FT_VBUS_DET` | U6 | 37 | VBUS | VBUS detect (divider) |
| 171 | NEW NET | `USB_DP` |  |  | — |  |
| 172 | CONNECT | `USB_DP` | U6 | 23 | — | DP |
| 173 | NEW NET | `USB_DM` |  |  | — |  |
| 174 | CONNECT | `USB_DM` | U6 | 25 | — | DM |
| 175 | NEW NET | `USB_SSTX_P` |  |  | — |  |
| 176 | CONNECT | `USB_SSTX_P` | U6 | 32 | — | TODP (to AC-coupling cap) |
| 177 | NEW NET | `USB_SSTX_N` |  |  | — |  |
| 178 | CONNECT | `USB_SSTX_N` | U6 | 31 | — | TODN (to AC-coupling cap) |
| 179 | NEW NET | `USB_SSRX_P` |  |  | — |  |
| 180 | CONNECT | `USB_SSRX_P` | U6 | 35 | — | RIDP |
| 181 | NEW NET | `USB_SSRX_N` |  |  | — |  |
| 182 | CONNECT | `USB_SSRX_N` | U6 | 34 | — | RIDN |
| 183 | CONNECT (new part) | `GND` | J_USB3 | A1 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 184 | CONNECT (new part) | `GND` | J_USB3 | A12 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 185 | CONNECT (new part) | `GND` | J_USB3 | B1 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 186 | CONNECT (new part) | `GND` | J_USB3 | B12 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 187 | CONNECT (new part) | `GND` | J_USB3 | SH | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 188 | NEW NET | `USB_VBUS` |  |  | — |  |
| 189 | CONNECT (new part) | `USB_VBUS` | J_USB3 | A4 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 190 | CONNECT (new part) | `USB_VBUS` | J_USB3 | A9 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 191 | CONNECT (new part) | `USB_VBUS` | J_USB3 | B4 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 192 | CONNECT (new part) | `USB_VBUS` | J_USB3 | B9 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 193 | NEW NET | `USB_CC1` |  |  | — |  |
| 194 | CONNECT (new part) | `USB_CC1` | J_USB3 | A5 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 195 | NEW NET | `USB_CC2` |  |  | — |  |
| 196 | CONNECT (new part) | `USB_CC2` | J_USB3 | B5 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 197 | CONNECT (new part) | `USB_DP` | J_USB3 | A6 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 198 | CONNECT (new part) | `USB_DP` | J_USB3 | B6 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 199 | CONNECT (new part) | `USB_DM` | J_USB3 | A7 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 200 | CONNECT (new part) | `USB_DM` | J_USB3 | B7 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 201 | NEW NET | `USB_SSTX_C_P` |  |  | — |  |
| 202 | CONNECT (new part) | `USB_SSTX_C_P` | J_USB3 | A2 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 203 | NEW NET | `USB_SSTX_C_N` |  |  | — |  |
| 204 | CONNECT (new part) | `USB_SSTX_C_N` | J_USB3 | A3 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 205 | CONNECT (new part) | `USB_SSRX_P` | J_USB3 | B11 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 206 | CONNECT (new part) | `USB_SSRX_N` | J_USB3 | B10 | — | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| 207 | CONNECT (new part) | `USB_SSTX_C_P` | D_ESD1 | 1 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 208 | CONNECT (new part) | `USB_SSTX_C_P` | D_ESD1 | 10 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 209 | CONNECT (new part) | `USB_SSTX_C_N` | D_ESD1 | 2 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 210 | CONNECT (new part) | `USB_SSTX_C_N` | D_ESD1 | 9 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 211 | CONNECT (new part) | `USB_SSRX_P` | D_ESD1 | 4 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 212 | CONNECT (new part) | `USB_SSRX_P` | D_ESD1 | 7 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 213 | CONNECT (new part) | `USB_SSRX_N` | D_ESD1 | 5 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 214 | CONNECT (new part) | `USB_SSRX_N` | D_ESD1 | 6 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 215 | CONNECT (new part) | `GND` | D_ESD1 | 3 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 216 | CONNECT (new part) | `GND` | D_ESD1 | 8 | — | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| 217 | CONNECT (new part) | `USB_DP` | D_ESD2 | 1 | — | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| 218 | CONNECT (new part) | `USB_DP` | D_ESD2 | 10 | — | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| 219 | CONNECT (new part) | `USB_DM` | D_ESD2 | 2 | — | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| 220 | CONNECT (new part) | `USB_DM` | D_ESD2 | 9 | — | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| 221 | CONNECT (new part) | `GND` | D_ESD2 | 3 | — | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| 222 | CONNECT (new part) | `GND` | D_ESD2 | 8 | — | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| 223 | CONNECT (new part) | `USB_SSTX_P` | C_SSTX_P | 1 | — | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| 224 | CONNECT (new part) | `USB_SSTX_C_P` | C_SSTX_P | 2 | — | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| 225 | CONNECT (new part) | `USB_SSTX_N` | C_SSTX_N | 1 | — | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| 226 | CONNECT (new part) | `USB_SSTX_C_N` | C_SSTX_N | 2 | — | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| 227 | CONNECT (new part) | `USB_CC1` | R_CC1 | 1 | — | Type-C Rd 5.1 kΩ (device) — added because a USB-C receptacle was chosen |
| 228 | CONNECT (new part) | `GND` | R_CC1 | 2 | — | Type-C Rd 5.1 kΩ (device) — added because a USB-C receptacle was chosen |
| 229 | CONNECT (new part) | `USB_CC2` | R_CC2 | 1 | — | Type-C Rd 5.1 kΩ (device) |
| 230 | CONNECT (new part) | `GND` | R_CC2 | 2 | — | Type-C Rd 5.1 kΩ (device) |
| 231 | CONNECT (new part) | `USB_VBUS` | R_VBUS_1 | 1 | — | VERIFY VBUS pin limit |
| 232 | CONNECT (new part) | `FT_VBUS_DET` | R_VBUS_1 | 2 | — | VERIFY VBUS pin limit |
| 233 | CONNECT (new part) | `FT_VBUS_DET` | R_VBUS_2 | 1 | — | VERIFY VBUS pin limit |
| 234 | CONNECT (new part) | `GND` | R_VBUS_2 | 2 | — | VERIFY VBUS pin limit |
| 235 | CONNECT (new part) | `FT_RREF` | R_RREF | 1 | — | value per FT60x datasheet — VERIFY |
| 236 | CONNECT (new part) | `GND` | R_RREF | 2 | — | value per FT60x datasheet — VERIFY |
| 237 | CONNECT (new part) | `FT_VD10` | C_VD10_1 | 1 | — | VD10/DV10 decoupling — VERIFY |
| 238 | CONNECT (new part) | `GND` | C_VD10_1 | 2 | — | VD10/DV10 decoupling — VERIFY |
| 239 | CONNECT (new part) | `FT_VD10` | C_VD10_2 | 1 | — | VD10/DV10 decoupling — VERIFY |
| 240 | CONNECT (new part) | `GND` | C_VD10_2 | 2 | — | VD10/DV10 decoupling — VERIFY |
| 241 | CONNECT (new part) | `FT_VD10` | C_VD10_3 | 1 | — | VD10/DV10 decoupling — VERIFY |
| 242 | CONNECT (new part) | `GND` | C_VD10_3 | 2 | — | VD10/DV10 decoupling — VERIFY |
| 243 | CONNECT (new part) | `FT_VD10` | C_VD10_4 | 1 | — | VD10/DV10 decoupling — VERIFY |
| 244 | CONNECT (new part) | `GND` | C_VD10_4 | 2 | — | VD10/DV10 decoupling — VERIFY |
| 245 | CONNECT (new part) | `+3V3_FT` | FB_A | 1 | — | +3V3_FT -> AVDD/VDDA |
| 246 | CONNECT (new part) | `FT_AVDD` | FB_A | 2 | — | +3V3_FT -> AVDD/VDDA |
| 247 | CONNECT (new part) | `FT_AVDD` | C_AVDD_1 | 1 | — |  |
| 248 | CONNECT (new part) | `GND` | C_AVDD_1 | 2 | — |  |
| 249 | CONNECT (new part) | `FT_AVDD` | C_AVDD_2 | 1 | — |  |
| 250 | CONNECT (new part) | `GND` | C_AVDD_2 | 2 | — |  |
| 251 | CONNECT (new part) | `FT_XI` | Y_FT | 1 | — | ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY |
| 252 | CONNECT (new part) | `FT_XO` | Y_FT | 3 | — | ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY |
| 253 | CONNECT (new part) | `GND` | Y_FT | 2 | — | ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY |
| 254 | CONNECT (new part) | `GND` | Y_FT | 4 | — | ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY |
| 255 | CONNECT (new part) | `FT_XI` | C_XI | 1 | — | load cap — VERIFY against crystal CL |
| 256 | CONNECT (new part) | `GND` | C_XI | 2 | — | load cap — VERIFY against crystal CL |
| 257 | CONNECT (new part) | `FT_XO` | C_XO | 1 | — | load cap — VERIFY against crystal CL |
| 258 | CONNECT (new part) | `GND` | C_XO | 2 | — | load cap — VERIFY against crystal CL |

## 4. Added parts (rev. B)

| Ref | Footprint (KiCad 10 library) | Value | MPN | Position (mm), rot | Note |
|---|---|---|---|---|---|
| J_USB3 | `Connector_USB:USB_C_Receptacle_Amphenol_12401610E4-2A` | USB-C 3.1 receptacle | Amphenol ICC 12401610E4#2A | (4.00, -208.00), 270° | only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable |
| D_ESD1 | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | TPD4E05U06 | Texas Instruments TPD4E05U06DQAR | (12.50, -210.00), 0° | pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY |
| D_ESD2 | `Package_SON:USON-10_2.5x1.0mm_P0.5mm` | TPD4E05U06 | Texas Instruments TPD4E05U06DQAR | (12.50, -206.00), 0° | second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused |
| C_SSTX_P | `Capacitor_SMD:C_0402_1005Metric` | 100nF | Murata GRM155R71C104KA88D | (16.50, -211.20), 0° | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| C_SSTX_N | `Capacitor_SMD:C_0402_1005Metric` | 100nF | Murata GRM155R71C104KA88D | (16.50, -210.00), 0° | USB 3 TX AC coupling — added (spec requirement), VERIFY |
| R_CC1 | `Resistor_SMD:R_0402_1005Metric` | 5.1k | Yageo RC0402FR-075K1L | (11.00, -214.00), 0° | Type-C Rd 5.1 kΩ (device) — added because a USB-C receptacle was chosen |
| R_CC2 | `Resistor_SMD:R_0402_1005Metric` | 5.1k | Yageo RC0402FR-075K1L | (11.00, -202.50), 0° | Type-C Rd 5.1 kΩ (device) |
| R_VBUS_1 | `Resistor_SMD:R_0402_1005Metric` | 10k | Yageo RC0402FR-0710KL | (32.50, -201.90), 90° | VERIFY VBUS pin limit |
| R_VBUS_2 | `Resistor_SMD:R_0402_1005Metric` | 3.3k | Yageo RC0402FR-073K3L | (33.70, -201.90), 90° | VERIFY VBUS pin limit |
| R_RREF | `Resistor_SMD:R_0402_1005Metric` | 3.24k 1% | Yageo RC0402FR-073K24L | (26.30, -201.90), 90° | value per FT60x datasheet — VERIFY |
| C_VD10_1 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (20.30, -210.40), 90° | VD10/DV10 decoupling — VERIFY |
| C_VD10_2 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (27.50, -201.90), 90° | VD10/DV10 decoupling — VERIFY |
| C_VD10_3 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (28.70, -201.90), 90° | VD10/DV10 decoupling — VERIFY |
| C_VD10_4 | `Capacitor_SMD:C_0402_1005Metric` | 4.7uF 6.3V | Murata GRM155R60J475ME47D | (29.90, -201.90), 90° | VD10/DV10 decoupling — VERIFY |
| FB_A | `Inductor_SMD:L_0603_1608Metric` | 600R@100MHz | Murata BLM18PG601SN1D | (18.00, -214.60), 0° | +3V3_FT -> AVDD/VDDA |
| C_AVDD_1 | `Capacitor_SMD:C_0402_1005Metric` | 100nF | Murata GRM155R71C104KA88D | (20.30, -212.60), 90° |  |
| C_AVDD_2 | `Capacitor_SMD:C_0402_1005Metric` | 1uF | Murata GRM155R61A105KE15D | (19.20, -212.60), 90° |  |
| Y_FT | `Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm` | 30MHz 18pF | Abracon ABM8-30.000MHZ-B2-T | (22.50, -199.60), 0° | ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY |
| C_XI | `Capacitor_SMD:C_0402_1005Metric` | 18pF C0G | Murata GRM1555C1H180JA01D | (19.60, -198.75), 0° | load cap — VERIFY against crystal CL |
| C_XO | `Capacitor_SMD:C_0402_1005Metric` | 18pF C0G | Murata GRM1555C1H180JA01D | (25.20, -199.20), 0° | load cap — VERIFY against crystal CL |

Deviations from `ft601_added_parts_BOM.csv` (all in the BOM `note`): USB-C **Amphenol 12401610E4#2A** (24-pin, has SS pins) instead of GCT USB4085 (the KiCad USB4085 footprint is USB 2.0-only); a **second** TPD4E05U06 for D± (one 4-channel array cannot cover 6 lines); **added** 2 × 100 nF SSTX AC-coupling capacitors (USB 3 requirement) and 2 × 5.1 kΩ CC pull-downs (required for a Type-C device receptacle); only the TX1/RX1 SuperSpeed lane is wired (no orientation mux → SS in one plug orientation only); C_VD10 as 4 × 4.7 µF (100 nF companions not placed). Crystal on the KiCad ABM8G land pattern (ABM8 3.2 × 2.5 mm).

## 5. FPGA pin list for the XDC (bank 35, LVCMOS33) — identical to `engineering/DESIGN/HOST_LINK/ft601_bank35.xdc`

| Net | FPGA ball | Bank-35 pin | XDC port |
|---|---|---|---|
| `FT_CLK` | C4 | IO_L12N_T1_MRCC_35 | `ft601_clk` |
| `FT_DATA_0` | A2 | IO_L8N_T1_AD14N_35 | `ft601_data[0]` |
| `FT_DATA_1` | A3 | IO_L4N_T0_35 | `ft601_data[1]` |
| `FT_DATA_2` | A4 | IO_L3N_T0_DQS_AD5N_35 | `ft601_data[2]` |
| `FT_DATA_3` | A5 | IO_L3P_T0_DQS_AD5P_35 | `ft601_data[3]` |
| `FT_DATA_4` | A7 | IO_L1N_T0_AD4N_35 | `ft601_data[4]` |
| `FT_DATA_5` | B1 | IO_L9N_T1_DQS_AD7N_35 | `ft601_data[5]` |
| `FT_DATA_6` | B2 | IO_L8P_T1_AD14P_35 | `ft601_data[6]` |
| `FT_DATA_7` | B4 | IO_L4P_T0_35 | `ft601_data[7]` |
| `FT_DATA_8` | B5 | IO_L2N_T0_AD12N_35 | `ft601_data[8]` |
| `FT_DATA_9` | B6 | IO_L2P_T0_AD12P_35 | `ft601_data[9]` |
| `FT_DATA_10` | B7 | IO_L1P_T0_AD4P_35 | `ft601_data[10]` |
| `FT_DATA_11` | C1 | IO_L9P_T1_DQS_AD7P_35 | `ft601_data[11]` |
| `FT_DATA_12` | C2 | IO_L7N_T1_AD6N_35 | `ft601_data[12]` |
| `FT_DATA_13` | C3 | IO_L7P_T1_AD6P_35 | `ft601_data[13]` |
| `FT_DATA_14` | C6 | IO_L5N_T0_AD13N_35 | `ft601_data[14]` |
| `FT_DATA_15` | C7 | IO_L5P_T0_AD13P_35 | `ft601_data[15]` |
| `FT_DATA_16` | D1 | IO_L10N_T1_AD15N_35 | `ft601_data[16]` |
| `FT_DATA_17` | D3 | IO_L11N_T1_SRCC_35 | `ft601_data[17]` |
| `FT_DATA_18` | D4 | IO_L12P_T1_MRCC_35 | `ft601_data[18]` |
| `FT_DATA_19` | D6 | IO_L6P_T0_35 | `ft601_data[19]` |
| `FT_DATA_20` | E1 | IO_L15N_T2_DQS_35 | `ft601_data[20]` |
| `FT_DATA_21` | E2 | IO_L10P_T1_AD15P_35 | `ft601_data[21]` |
| `FT_DATA_22` | E3 | IO_L11P_T1_SRCC_35 | `ft601_data[22]` |
| `FT_DATA_23` | E5 | IO_L13N_T2_MRCC_35 | `ft601_data[23]` |
| `FT_DATA_24` | E6 | IO_0_35 | `ft601_data[24]` |
| `FT_DATA_25` | F2 | IO_L15P_T2_DQS_35 | `ft601_data[25]` |
| `FT_DATA_26` | F3 | IO_L14N_T2_SRCC_35 | `ft601_data[26]` |
| `FT_DATA_27` | F4 | IO_L14P_T2_SRCC_35 | `ft601_data[27]` |
| `FT_DATA_28` | F5 | IO_L13P_T2_MRCC_35 | `ft601_data[28]` |
| `FT_DATA_29` | G1 | IO_L17N_T2_35 | `ft601_data[29]` |
| `FT_DATA_30` | G2 | IO_L17P_T2_35 | `ft601_data[30]` |
| `FT_DATA_31` | G4 | IO_L16N_T2_35 | `ft601_data[31]` |
| `FT_BE_0` | G5 | IO_L16P_T2_35 | `ft601_be[0]` |
| `FT_BE_1` | H1 | IO_L20N_T3_35 | `ft601_be[1]` |
| `FT_BE_2` | H2 | IO_L20P_T3_35 | `ft601_be[2]` |
| `FT_BE_3` | H3 | IO_L21N_T3_DQS_35 | `ft601_be[3]` |
| `FT_TXE_N` | H4 | IO_L18N_T2_35 | `ft601_txe_n` |
| `FT_RXF_N` | H5 | IO_L18P_T2_35 | `ft601_rxf_n` |
| `FT_WR_N` | J1 | IO_L22N_T3_35 | `ft601_wr_n` |
| `FT_RD_N` | J3 | IO_L21P_T3_DQS_35 | `ft601_rd_n` |
| `FT_OE_N` | J5 | IO_L19P_T3_35 | `ft601_oe_n` |
| `FT_SIWU_N` | K1 | IO_L22P_T3_35 | `ft601_siwu_n` |
| `FT_RESET_N` | K2 | IO_L24N_T3_35 | `ft601_reset_n` |
| `FT_WAKEUP_N` | K3 | IO_L24P_T3_35 | `ft601_wakeup_n` |
| `FT_GPIO0` | K5 | IO_25_35 | `ft601_gpio[0]` |
| `FT_GPIO1` | L2 | IO_L23N_T3_35 | `ft601_gpio[1]` |

## 6. Placement

J_USB3 on the left board edge (x = 0, nearest edge to U6, mating face outward, origin (4.0, −208.0), 270°); ESD arrays at x = 12.5; crystal, RREF, VBUS divider and VD10 capacitors in the free band below U6 (y ≈ −199…−202); AVDD filter left of U6. All parts on F.Cu. Placement is a proposal (thermal/EMC not assessed).

## 7. Files

`MAIN_BOARD_REVB.kicad_pcb/.kicad_pro` (netclasses FT_BUS / USB_DIFF / FT_PWR), `NETLIST_DELTA.csv`, `revb_parts.json`, `BOM_MAIN_BOARD_REVB_beta.csv` (rev. A BOM + 12 new lines, column `revision`), `UNROUTED.md`, `MAIN_BOARD_REVB_ft601.dsn/.ses`, `freerouting.log`, `ses_merge*.json`, `removed_unfinished_routes.json`, `reports_before_routing/`, `exports/` (full package, all 24 export steps exit 0, `exports/EXPORT_LOG.md`).
