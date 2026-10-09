# Host link (FPGA → host, options A/B) and 22 V PA supply module

**Author: Antidrone Ukraine · antidrone.cc**

**Status summary:** host data path DSN-LINK-01 PROPOSED DESIGN; option B (SPI bridge through the STM32 CDC) implemented as BETA in `beta/fpga`, `beta/stm32`, `beta/gui` (simulated and unit-tested, never run on hardware); option A (FT601 on Main Board rev. B) is a pin plan plus a partially routed KiCad proposal whose 32-bit bus is blocked by the existing bank-35 fan-out (layout-owner decision required); 22 V PA supply DSN-PSU-01 PROPOSED DESIGN (block schematic, BOM, requirement table; no component-level schematic, no bench test). Figure F9.1 PROPOSED DESIGN; figure F9.2 BETA. Decisions D-16…D-19 and D-14 are not approved by the owner (chapter 17 §2).

**Sources:** `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md`, `engineering/DESIGN/HOST_LINK/README.md`, `ft601_pin_assignment.csv`, `ft601_added_parts_BOM.csv`, `option_b_signal_map.csv`, `ft601_bank35.xdc`; `beta/fpga/README.md` (host path, results), `beta/fpga/CHANGELOG.md`; `beta/stm32/README.md`, `beta/stm32/CHANGELOG.md`, `beta/stm32/DECISIONS.md` D-17/D-18; `beta/gui/README.md`, `beta/gui/CHANGELOG.md`; `beta/pcb/MAIN_BOARD_REVB/README.md`, `UNROUTED.md`, `NETLIST_DELTA.csv`; `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/README.md`, `DSN-PSU-01_BOM.csv`; `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5.

**Planned figures:** F9.1 DSN-PSU-01 block schematic; F9.2 Main Board rev. B isometric render.

## 1. Problem (conflict K3)

The RTL streams radar data through an FT601 USB 3.0 FIFO (`usb_data_interface.v`), but on the Main Board **U6 (FT601Q) has 0 of 77 pins connected** — only the decoupling of its `+3V3_FT` rail exists (L19, C184–C186). The only wired host link is the STM32 USB-FS CDC (X53) (source: `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §1).

### 1.1 Data-rate budget (source: `HOST_LINK_DESIGN.md` §2, copied verbatim)

| Quantity | Value | Basis |
|---|---|---|
| Range-Doppler cells per beam position | 64 × 32 = 2048 | `doppler_processor.v` (RANGE_BINS 64, 32 chirps) |
| Beam-position frame time | 5647.4 µs | `main.cpp:180-186` |
| Raw RTL packet stream (44 B per cell) | **16.0 MB/s** | `usb_data_interface.v` (11 × 32-bit words) |
| Compact map frame (8-bit log-magnitude per cell + header + ≤ 32 detections + CRC) | 2164 B → **383 kB/s** | this design, §5 |
| STM32 USB-FS CDC practical limit | ≈ 0.8–1.1 MB/s | USB 2.0 FS bulk (19 × 64 B per 1 ms frame max) |
| SPI1 STM32 ↔ FPGA (existing lines) | 27 Mbit/s ≈ 3.3 MB/s (DMA) | APB2 108 MHz / 4 (beta clock tree) |
| FT601 245 sync FIFO, 32 bit @ 100 MHz | up to 400 MB/s | FT601 |

Conclusion of the source: the raw stream needs the FT601 (option A); the compact map fits the existing STM32 path with 3× margin (option B).

### 1.2 Options and decisions (source: `HOST_LINK_DESIGN.md` §3, copied verbatim)

| | A — FT601 on Main Board rev. B | B — SPI bridge via STM32 (no PCB change) | C — Ethernet mezzanine on bank 35 (future) |
|---|---|---|---|
| Hardware change | route U6 to bank 35 (46 I/Os), add USB 3 connector, crystal, RREF, ESD (`ft601_added_parts_BOM.csv`) | none: DIG_5/6/7 + SPI1 are already routed to the FPGA | new PCB with RGMII PHY on the 50 free bank-35 pins |
| Throughput | 400 MB/s | ≤ 1 MB/s (CDC-bound) | 100 MB/s |
| Firmware/RTL | RTL already written (fix 2-bit BE → 4-bit; honour TXE_N); host driver FTDI D3XX | new RTL `host_bridge_spi.v` + packer; STM32 `host_bridge.c`; GUI parser | new MAC/UDP stack |
| Risk | 10-layer board respin; USB 3 SI | protocol only; SPI1 shared with ADAR1000 (time-multiplexed) | highest |
| Decision | **D-16: target for rev. B** | **D-17: implement now (BETA)** | D-18: documented only |

Decision D-19 for the RTL: widen `ft601_be` to 4 bits, drive `BE = 4'b1111` for full words, respect `TXE_N` back-pressure, add `ft601_reset_n`/`wakeup_n`/`siwu_n` as outputs — recorded for `beta/fpga`, not yet applied there (source: `HOST_LINK_DESIGN.md` §4).

## 2. Option A — FT601 on Main Board rev. B (PROPOSED DESIGN)

### 2.1 Pin plan

`ft601_pin_assignment.csv` maps every FT601 signal to a free bank-35 pad, with CLK on the MRCC pin C4 = `IO_L12N_T1_MRCC_35`; `ft601_bank35.xdc` (60 lines) is the matching constraint fragment. The table has 47 signal rows: CLK, DATA_0..31, BE_0..3, TXE_N, RXF_N, WR_N, RD_N, OE_N, SIWU_N, RESET_N, WAKEUP_N, GPIO0, GPIO1 — all LVCMOS33, bank 35 VCCO = `+3V3_FPGA` on the schematic (source: `engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv`, 48 lines including header; `ft601_bank35.xdc` header). FT601 pad numbers come from the EAGLE library symbol used in the schematic (U6 `FT601Q-B-T`); the **FT601 datasheet is not in the repository** — AC timing, RREF value, VBUS limits and the 1.0 V core supply arrangement (VD10 pins) must be verified against it before the schematic is edited. Rev. B schematic work per the source: connect U6 VCC33 (pads 20/24/38) and VCCIO (14/49/59/68) to `+3V3_FT`, GND pads, the 46 signals per the CSV, XI/XO crystal, RREF, VBUS divider, D±/SS pairs to the new connector through the ESD array; route the 32-bit bus as a length-matched group (±25 mm, 100 MHz single-ended, 50 Ω) on the two bank-35 side layers (source: `HOST_LINK_DESIGN.md` §4). The full pin table is reproduced in section 9 of this chapter.

### 2.2 Parts to add for rev. B (source: `ft601_added_parts_BOM.csv`, copied verbatim)

| ref | qty | description | proposed_part | note |
|---|---|---|---|---|
| J_USB3 | 1 | USB 3.1 Gen1 receptacle (Type-C, USB 2.0 + one SuperSpeed pair used) or USB 3.0 micro-B | GCT USB4085-GF-A (Type-C) / Amphenol GSB4211111WEU (micro-B 3.0) | VERIFY pin-out; SS pairs TODP/TODN ↔ RIDP/RIDN per FT601 datasheet |
| Y_FT | 1 | Crystal 30 MHz ±30 ppm, 18 pF | Abracon ABM8-30.000MHZ-B2-T | FT601 XI/XO (pads 21/22) + 2 × 18 pF (VERIFY load per datasheet) |
| R_RREF | 1 | Resistor 3.24 kΩ 1 % 0402 | Yageo RC0402FR-073K24L | FT601 RREF (pad 27) — value per FT60x datasheet, VERIFY |
| C_VD10 | 4 | Capacitor 4.7 µF 6.3 V 0402 + 100 nF | Murata GRM155R60J475ME47D | 1.0 V core pins VD10/VD10_2..4/DV10 (pads 3,30,33,39,48): FT60x internal regulator output, decouple each — VERIFY |
| C_AVDD | 2 | Capacitor 100 nF / 1 µF 0402 | Murata GRM155R71C104KA88D | AVDD/VDDA (pads 2, 28) analogue 3.3 V via ferrite from +3V3_FT |
| FB_A | 1 | Ferrite bead 600 Ω@100 MHz 0603 | Murata BLM18PG601SN1D | +3V3_FT → AVDD |
| D_ESD | 1 | USB 3.0 ESD array (SS + HS) | TI TPD4E05U06 | on connector side of the SS and D± pairs |
| R_VBUS | 2 | Resistor divider 10 k / 3.3 k (VBUS detect, pad 37) | Yageo RC0402 | VERIFY VBUS pin voltage limit in datasheet |
| L19/C184-C186 | 0 | already in the schematic: +3V3_FT = +3V3_FPGA via L19; 10 µF + 100 nF + 1 nF | — | present (U6 pads 20, 24, 38 VCC33; 14, 49, 59, 68 VCCIO) — nets to be connected |

### 2.3 Rev. B layout outcome (BETA PROPOSAL, `beta/pcb/MAIN_BOARD_REVB/`)

Status of the directory: "BETA PROPOSAL — explicit netlist change (rev. B); partially routed; DRC-checked; not reviewed by the original designer; not fabricated." The EAGLE schematic has **not** been changed and no longer matches this board; the designer must enter the same connections and parts in the schematic, verify them against the FT601 datasheet and re-annotate before any rev. B layout is released. Source board: `beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb` (rev. A BETA, unchanged); reproducible with `beta/pcb/tools/beta_revb_ft601.py` (source: `beta/pcb/MAIN_BOARD_REVB/README.md`, header).

![F9.2 — Main Board rev. B isometric render with the FT601 cluster and USB-C receptacle placed at the left board edge; the 32-bit FIFO bus is unrouted — BETA (source: beta/pcb/MAIN_BOARD_REVB/MAIN_BOARD_REVB.kicad_pcb; produced by kicad-cli pcb render, exports/3d)](beta/pcb/MAIN_BOARD_REVB/exports/3d/MAIN_BOARD_REVB_render_isometric.png)

DRC result (source: `MAIN_BOARD_REVB/README.md` §1, copied verbatim):

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

Routing result (source: `MAIN_BOARD_REVB/README.md` §1 bullets; `UNROUTED.md` §1):

- Routed and connected: 17 of the 64 new nets (USB D±, both SuperSpeed RX lines, SSTX_N and both SSTX_C lines, CC1/CC2, USB_VBUS, FT_VBUS_DET, FT_RREF, FT_XI, FT_GPIO1, partly +3V3_FT/FT_VD10/FT_AVDD/FT_XO).
- **The 32-bit FIFO bus and its control lines (46 of 47 FPGA-side signals) are NOT routed.** Root cause, measured: 36 of the 47 bank-35 balls of U42 (XC7A50T FTG256, 1.0 mm pitch) have **no free position for an escape via** — the four dog-bone positions around each ball are already occupied by the existing BGA fan-out vias/traces of neighbouring balls. Balls with no free position: A2, A3, A7, B1, B2, B6, C1, C2, C3, C4, C6, D1, D3, D4, D6, E1, E2, E3, E5, E6, F2, F3, F4, F5, G4, G5, H4, H5, J1, J3, J5, K1, K2, K3, K5, L2; one free position for A4, A5, B4, B5, B7, C7, G1, H1, H3; two for G2, H2. Freerouting (1 pass, 25 min, existing copper locked) fanned out the FT601 side but could not reach these balls; its partial copper on the 47 open bus nets (127 items) was removed again so the board is left clean.
- What is needed (layout owner): re-do the bank-35 corner breakout of U42 (outer two rows on F.Cu, inner rows by dog-bone vias to In2/In3/In5/In7, which requires moving existing vias of adjacent nets), then route the 46 nets as one group at 0.204 mm, length-matched to ±25 mm; alternatively choose bank-35 balls on the two outer rows only, which would require revising `ft601_pin_assignment.csv` together with the XDC. This is "a layout-owner decision outside this BETA's 'existing tracks locked' rule"; no re-done fan-out exists in the repository at the time of writing.
- New DRC items caused by rev. B copper: 9 `track_width` (Freerouting neck-down 0.075 mm on +3V3_FT/CC1/CC2 at 0.4 mm-pitch pads; to be widened to 0.1 mm), 2 courtyard overlaps (Y_FT ↔ C_XI/C_XO — move the load caps 0.5 mm), 1 copper-edge (USB_CC2 inner track 0.2 mm from the J_USB3 NPTH peg), 5 dangling vias (+3V3_FT ×4, USB_SSTX_C_P). Two further scripted clean-ups (second restricted Freerouting pass on the open power nets; widening the neck-downs) were prepared but not executed in that session.

Routing geometry (source: `MAIN_BOARD_REVB/README.md` §2, copied verbatim):

| Group | Rule used | Achieved |
|---|---|---|
| FT_BUS (FT_DATA_0..31, FT_BE_0..3, FT_CLK, control, GPIO) | netclass `FT_BUS` 0.204 mm (50 Ω microstrip on the 0.102 mm RO4350B outer layer per `../MAIN_BOARD/FAB_NOTES.md`; on inner layers ≈ 42 Ω stripline estimate, FR-4, not field-solved), clearance 0.1 mm (DRU), length-match target ±25 mm | only `FT_GPIO1` routed: 37.57 mm, 3 vias, F.Cu/In2/In7 — **no skew figure exists for the bus because it is unrouted**; FT601→bank-35 Manhattan distance is 20–35 mm, so ±25 mm is achievable once the breakout exists |
| USB SuperSpeed + D± | netclass `USB_DIFF` width 0.204 mm, pair gap 0.18 mm (≈ 90 Ω edge-coupled microstrip on RO4350B h = 0.102 mm, closed-form estimate 91 Ω, fab to solve) | Freerouting routes pair members as single traces (coupling not enforced): SSRX_P/N 29.28 / 29.41 mm (skew 0.13 mm), D+/D− 23.72 / 27.12 mm (skew 3.4 mm), SSTX_C_P/N 9.08 / 8.72 mm, SSTX_N 16.08 mm (SSTX_P open); neck-down to 0.153 mm at pads. **Pairs must be re-routed coupled (KiCad diff-pair router, 0.204/0.18 mm) before release** |
| Power `FT_PWR` (FT_VD10, FT_AVDD, USB_VBUS) | 0.3 mm | USB_VBUS 34.5 mm, FT_AVDD 18.6 mm; FT_VD10 only partially connected |

Netlist delta: 64 new nets, 123 pad connections on existing parts (U6, U42), 71 pad connections on 20 added parts; U6 pads 2, 14, 20, 24, 28, 37, 38, 49, 59, 68 were on single-pin nets in rev. A and were moved to the new nets. Every connection is listed in `MAIN_BOARD_REVB/README.md` §3 and `NETLIST_DELTA.csv` (258 rows) (source: `MAIN_BOARD_REVB/README.md` §3, lead-in).

Added parts as placed in rev. B (source: `MAIN_BOARD_REVB/README.md` §4, copied verbatim):

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

Deviations from `ft601_added_parts_BOM.csv` (source: `MAIN_BOARD_REVB/README.md` §4, closing paragraph): USB-C Amphenol 12401610E4#2A (24-pin, has SS pins) instead of GCT USB4085 (the KiCad USB4085 footprint is USB 2.0-only); a second TPD4E05U06 for D± (one 4-channel array cannot cover 6 lines); added 2 × 100 nF SSTX AC-coupling capacitors (USB 3 requirement) and 2 × 5.1 kΩ CC pull-downs (required for a Type-C device receptacle); only the TX1/RX1 SuperSpeed lane is wired (no orientation mux → SS in one plug orientation only); C_VD10 as 4 × 4.7 µF (100 nF companions not placed). Placement: J_USB3 on the left board edge nearest U6, ESD arrays at x = 12.5, crystal/RREF/VBUS divider/VD10 capacitors in the free band below U6, all on F.Cu; placement is a proposal, thermal/EMC not assessed (source: same, §6).

Open items on the routed power/clock/USB nets (source: `MAIN_BOARD_REVB/UNROUTED.md` §2, copied verbatim):

| Net | Open connections | What is needed |
|---|---|---|
| FT_VD10 | 5 | connect U6 pads 3/30/33/39/48 together and to C_VD10_1..4 — the QFN pads face other-net pads on all sides; route on F.Cu around the exposed pad corners or via-in-pad to an inner pour |
| +3V3_FT | 5 | feed from the L19/C184-186 filter (y ≈ −232) to U6 VCC33/VCCIO pads; 4 autorouter vias are dangling (remove or connect) |
| FT_AVDD | 1 | U6 pad 2 to C_AVDD_1 (0.6 mm stub) |
| FT_XO | 1 | U6 pad 22 to Y_FT pad 3 |
| USB_SSTX_P | 1 | U6 pad 32 to C_SSTX_P — route coupled with USB_SSTX_N (0.204/0.18 mm) |

Prepared but not executed (source: `UNROUTED.md` §3): (1) second Freerouting pass restricted to FT_VD10, +3V3_FT, FT_AVDD, FT_XO, USB_SSTX_P; (2) widen the 14 Freerouting neck-downs below 0.1 mm to 0.1 mm; (3) move C_XI / C_XO 0.5 mm away from Y_FT. The export package of rev. B (all 24 export steps exit 0, `exports/EXPORT_LOG.md`) exists but describes an unfinished board (source: `MAIN_BOARD_REVB/README.md` §7).

## 3. Option B — SPI bridge through the STM32 (BETA)

### 3.1 Signals (source: `option_b_signal_map.csv`, copied verbatim)

| signal | schematic_net | stm32_pin | fpga_pin | direction | note |
|---|---|---|---|---|---|
| FPGA_CS_N (option B) | DIG_5 | STM32 PD13 (today configured INPUT in main.cpp:2313-2317 → becomes OUTPUT) | U42 H11 (IO_L19P_T3_A22_15) | STM32 → FPGA | active-low chip select for the bridge; ADAR1000 pass-through is gated off while low |
| DRDY (option B) | DIG_6 | STM32 PD14 (INPUT, EXTI14) | U42 G12 (IO_L19N_T3_A21_VREF_15) | FPGA → STM32 | a complete frame is in the FPGA TX FIFO |
| spare / ACK | DIG_7 | STM32 PD15 | U42 H12 (IO_L20P_T3_A20_15) | FPGA → STM32 | reserved (frame dropped / overflow flag) |
| SCLK | STM32_SCLK1 | STM32 PA5 (SPI1_SCK) | U42 J16 (IO_L23N_T3_FWE_B_15) | STM32 → FPGA | existing net, 3.3 V; ≤ 27 MHz (SPI1 on APB2 108 MHz, prescaler 4) |
| MOSI | STM32_MOSI1 | STM32 PA7 (SPI1_MOSI) | U42 H13 (IO_L20N_T3_A19_15) | STM32 → FPGA | existing; carries the bridge command byte |
| MISO | STM32_MISO1 | STM32 PA6 (SPI1_MISO) | U42 G14 (IO_L21P_T3_DQS_15) | FPGA → STM32 | existing; frame bytes, MSB first, mode 0 |
| ADAR_n_CS_3V3 | ADAR_1..4_CS_3V3 | STM32 GPIO | U42 bank 15 | STM32 → FPGA | unchanged; must all be HIGH during a bridge transfer (firmware guarantees; RTL also checks) |

Transfer (source: `HOST_LINK_DESIGN.md` §5): the STM32 waits for DRDY (EXTI on PD14), pulls `FPGA_CS_N` low, clocks one command byte (0x01 = read frame) and then reads the frame over MISO with DMA (SPI1 mode 0, MSB first, ≤ 27 MHz); the FPGA holds the ADAR1000 pass-through idle while `FPGA_CS_N` is low; the firmware never starts an ADAR1000 SPI transaction while a bridge read is in progress (both share SPI1). The STM32 forwards each frame unchanged over CDC (`AERIS_USB_SendBridgeFrame`), interleaved with the existing status strings; the GUI stream parser resyncs on the sync word (status strings never contain `0xA5 0x5A`).

### 3.2 Frame format (source: `HOST_LINK_DESIGN.md` §5, copied verbatim; little-endian; reference parser `engineering/DESIGN/HOST_LINK/gui/bridge_frame.py`)

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | sync `0xA5 0x5A` |
| 2 | 1 | version = 1 |
| 3 | 1 | flags (bit0 = long-chirp set, bit1 = overflow since last frame) |
| 4 | 2 | sequence number |
| 6 | 1 | azimuth index (1..50) |
| 7 | 1 | elevation index (1..31) |
| 8 | 2 | chirp count |
| 10 | 1 | n_range = 64 |
| 11 | 1 | n_doppler = 32 |
| 12 | 2 | n_det (≤ 32) |
| 14 | 2 | reserved |
| 16 | 2048 | magnitude map, uint8 = 8·log2(abs(I)+abs(Q)) saturated, range-major |
| 2064 | 3·n_det | detections: range u8, doppler u8, mag u8 |
| end | 2 | CRC-16/CCITT-FALSE over bytes 0..end-1 |

Files (source: `HOST_LINK_DESIGN.md` §5): `rtl/host_bridge_spi.v` (SPI slave + frame FIFO, 1 BRAM), `rtl/rd_map_packer.v` (cell → frame builder, CRC), `rtl/tb_host_bridge.v` (self-checking iverilog test), `stm32/host_bridge.c/.h` (SPI1 DMA + EXTI + CDC forward), `gui/bridge_frame.py` (+ tests); integration into `beta/fpga`, `beta/stm32`, `beta/gui` is recorded in their CHANGELOGs.

### 3.3 Bridge command set v2 — register access (source: `HOST_LINK_DESIGN.md` §7, copied verbatim; RTL implemented 2026-10-09)

All transfers: `FPGA_CS_N` low, SPI mode 0, MSB first; first byte = command. Bytes marked ← are driven by the FPGA on MISO (the master clocks dummy 0x00). Implemented in `beta/fpga/rtl/host_bridge_spi.v` (copy in `engineering/DESIGN/HOST_LINK/rtl/`), firmware counterpart `beta/stm32/Core/Src/host_bridge_proto.c`, verified by `beta/fpga/tb/tb_host_bridge_top.v` (through `radar_system_top`) and `rtl/tb_host_bridge.v` (unit).

| Cmd | Total bytes | Bytes after the command | Reply | Meaning |
|---|---|---|---|---|
| 0x01 | 1 + frame + 2 | — | frame + CRC (as §3.2); all zeros when no frame is pending (no sync word) | read the pending range-Doppler frame (unchanged) |
| 0x02 | 8 | a0 = addr[7:0], a1 = addr[15:8], d0..d3 = data[7:0]..[31:24], xx | ← byte 7 = 0xA2 (ack = command accepted; the write commits in the clk domain within ~5 clk cycles) | write register word `addr` |
| 0x03 | 7 | a0, a1, xx, xx, xx, xx | ← bytes 3..6 = d0 d1 d2 d3 (little-endian). No turnaround byte: the read is launched when a0 is complete; a1 is accepted but not decoded (the map has 5 address bits, so a1 must be 0) | read register word `addr` |
| 0x04 | 9 | xx × 8 | ← bytes 1..8 = four little-endian u16: status word, RTL version (0x0002), frames produced, 0x0000 | status without touching the frame |
| other (incl. 0x00) | any | — | ← 0xEE on every following byte | unknown command (ignored) |

Status word (assembled in `radar_system_top.v`): bit0 frame ready (= DRDY), bit1 ADAR CS conflict (sticky: an ADAR1000 CS was low while `FPGA_CS_N` was low), bit2 ADC capture FIFO overflow (sticky, `ADC_CAPTURE_MODE = 1`), bit3 calibration lock (all 8 lanes locked), bit4 packer overflow (a frame was dropped since reset), bits 5..15 = 0. The status is sampled when the command byte completes (quasi-static values; `frames produced` may be one behind).

Register map — word addresses, **16-bit registers** (data[31:16] are ignored on write and read as 0). Source of truth: `beta/fpga/rtl/radar_control_regs.v` (address-map comment and the two `case` statements); the table is kept identical to it. `toggle` = write 1 to the bit to pulse the action, reads as 0; `level` = stored bit.

| Addr | Name | Access | Reset | Bits |
|---|---|---|---|---|
| 0x00 | CONTROL | rw | 0x0005 | bit0 use_long_chirp, bit1 adc_pwdn, bit2 usb_enable |
| 0x01 | CFAR_THR | rw | 10000 | [15:0] abs(I)+abs(Q) detection threshold |
| 0x02 | DECIM | rw | 0x0001 | [1:0] range decimation mode (01 = peak) |
| 0x03 | START_BIN | rw | 0 | [9:0] first range bin passed to the decimator |
| 0x04 | CAL_CTRL | rw | 0 | bit0 start auto calibration (toggle), bit1 manual tap load (toggle), bit2 bitslip load (toggle), bit3 pattern-check enable (level), bit4 blind method (level: 0 = ADC test pattern, 1 = CW tone at the IF) |
| 0x05 | CAL_LANE | rw | 0 | [2:0] lane for CAL_TAP / CAL_SLIP writes and CAL_LANE_INFO / CAL_BLIND_MIN reads |
| 0x06 | CAL_TAP | rw | 16 | [4:0] manual IDELAY tap |
| 0x07 | CAL_SLIP | rw | 0 | [1:0] BITSLIP pulses for a manual bitslip load |
| 0x08 | CAL_PATT | rw | 0x55AA | {pattern_b[7:0], pattern_a[7:0]} expected alternating ADC test codes |
| 0x09 | CAL_STAT | ro | — | {fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]} |
| 0x0A | CAL_LANE_INFO | ro | — | {1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]} of CAL_LANE |
| 0x0B | CAL_ERR | ro | — | pattern-check error counter (saturating) |
| 0x0C | CAL_UNDET | ro | — | {8'b0, undetermined[7:0]} |
| 0x0D | CAL_BLIND_COEF | rw | 0xEC39 | signed Q1.14 cos(2π·f_IF/f_S) for the blind notch (0xEC39 = −5063 = 120 MHz at 400 MSPS) |
| 0x0E | CAL_BLIND_MARGIN | rw | 0x0040 | absolute part of the blind pass margin (a tap passes when metric ≤ min + margin + min/16) |
| 0x0F | ID | ro | 0xBE7A | beta build identifier |
| 0x10 | CAL_BLIND_MIN | ro | — | minimum blind metric (sum of abs(r) over the window, >> 4, saturated) of CAL_LANE |

Registers that earlier revisions of this section listed but that do **not** exist in the RTL (run bit, mixers enable, NCO tuning word) have been removed from the table; `use_long_chirp` is CONTROL bit0. STM32 API: `HostBridge_WriteReg(addr, value)`, `HostBridge_ReadReg(addr, &value)`, `HostBridge_Status(&st)`; exposed to the GUI through the existing settings path as a text command `REG W <addr> <value>` / `REG R <addr>` → reply `REG <addr> <value>` in the status stream (ASCII, so the bridge-frame parser passes it through) (source: `HOST_LINK_DESIGN.md` §7, closing paragraphs).

### 3.4 BETA implementation status per subsystem

**FPGA (`beta/fpga`, BETA).** `rd_map_packer` turns each 64 × 32 Doppler frame into a 2066..2162-byte frame and `host_bridge_spi` streams it to the STM32 as an SPI slave on the existing SCLK/MOSI/MISO nets with DIG_5 = `spi_bridge_cs_n` (H11), DIG_6 = `spi_bridge_drdy` (G12), DIG_7 = `spi_bridge_spare` (H12, packer overflow flag). While the bridge CS is low the ADAR1000 pass-through is gated (CS high, SCLK/MOSI idle on the 1.8 V side) and MISO is driven by the bridge; `system_status[1]` latches a conflict if any ADAR CS is low during a transfer. Beam indices come from the transmitter's STM32-toggle counters, the chirp count from the receiver's chirp pulses, `long_chirp` from the register map. The bridge drives the register map's write/read port (5-bit addresses, 16-bit data); register toggles cross SCLK → clk through 3-flop synchronisers; a read needs ≥ 8 SCLK periods between a0 and d0 (≥ 296 ns at 27 MHz, the fetch takes ≤ 5 clk cycles). Executed tests: `tb_host_bridge` — 3 detections, 32 detections (`det_wr` regression), command set v2 against a 4-word register model: PASS, 2075- and 2162-byte frames, CRC ok, v2 write/read-back/status/unknown ok; `tb_host_bridge_top` — v2 register commands (CFAR_THR 10000 → 150 written over SPI, 5 read-backs, 0x04 status before/with/after a frame, 0xEE), then one 64×32 frame after DRDY: PASS (~77 s), 2162-byte frame, 32 detections (only possible because the threshold write took effect), sync/dims/az-el/chirp-count/map/CRC ok, ADAR pass-through gated (source: `beta/fpga/README.md`, "What passed" rows 6e/6f and "Host path"). One defect was found and fixed in the copied packer: `det_wr` widened from 6 to 7 bits — with 6 bits the packer never left its header/detection state once `n_det ≥ 22`, so the frame never completed and DRDY never asserted (source: `beta/fpga/CHANGELOG.md`, "Host-link option B integration", row `rd_map_packer.v`). Unresolved for option B in the RTL: STM32 SPI1 timing versus the FPGA pins (XDC placeholders), BRAM inference of the SCLK-domain frame RAM read (asynchronous read registered on falling SCLK; Yosys maps it to 1,536 LUTs as RAM64M, chapter 11 §12), and the firmware rule that no ADAR1000 transaction overlaps a bridge read (source: `beta/fpga/README.md`, "Host path"; `beta/fpga_synth/README.md`, "Reading the numbers" item 2).

**STM32 (`beta/stm32`, BETA).** New `Core/Src/host_bridge.c` / `Core/Inc/host_bridge.h` (copies of `engineering/DESIGN/HOST_LINK/stm32/`): SPI1 bridge to the FPGA using the already-routed DIG_5 (PD13 → FPGA_CS_N, reconfigured as output), DIG_6 (PD14 → DRDY, EXTI14 rising), DIG_7 (PD15 spare); `Core/Src/host_bridge_proto.c` implements the HAL-free command set v2 (0x02 write/ack 0xA2, 0x03 read, 0x04 status) and the ASCII `REG W/R` parser/executor/reply formatter; `HostBridge_WriteReg/ReadReg/Status/ExecuteTextCommand` run over a transport that refuses while a frame read is active or any ADAR CS is low; the main loop executes a pending `REG` command after `HostBridge_Poll()` and replies with `CDC_Transmit_FS` (bounded 50 ms busy wait) (source: `beta/stm32/CHANGELOG.md`, "ADAR1000 vector-modulator tables + bridge command set v2"). Decision D-17: register access runs in the main loop, never in the USB ISR; one command slot; reply format `REG 0x%04X 0x%08X\r\n` (a write echoes the written value after the ack), `REG ERR\r\n` on syntax error, NACK, busy or SPI error. Decision D-18 records the framing assumptions (8-byte write with ack in byte 8, 7-byte read with data little-endian in bytes 3..6, 9-byte status with four u16) (source: `beta/stm32/DECISIONS.md` D-17, D-18). Build: FLASH 93 276 B, RAM 17 480 B, 0 errors; host tests 6/6 PASSED including `test_host_bridge_cmds.c` (bridge v2 byte sequences with a mock SPI: 0x02 + ack 0xA2 / no ack / 0xEE / transfer error, 0x03 LE decode, 0x04 status fields; ASCII `REG W/R` parser and reply formatting) (source: `beta/stm32/README.md` §3–4).

**GUI (`beta/gui`, BETA).** The default hardware path is the SPI bridge: the FPGA serves 64×32 log-magnitude frames over SPI, the STM32 forwards them unchanged over USB CDC, interleaved with status strings and `REG` replies; the raw 35-byte RTL packet path (option A, FT601) stays available with `--raw-ft601`. The "FPGA registers / ADC calibration" tab issues `REG W/R` over CDC with the same text protocol as the firmware (one command per USB transfer, timeout + retransmit, no request ID). In demo mode the simulator answers `REG` commands from an in-memory model of `radar_control_regs.v`. The GUI register map was brought to the final RTL map (RTL version 0x0002): `protocol/register_map.py` uses 5-bit addresses (`ADDR_MASK = 0x1F`, unmapped 0x11..0x1F), CAL_CTRL bit4 blind level, registers 0x0D `CAL_BLIND_COEF`, 0x0E `CAL_BLIND_MARGIN`, 0x10 `CAL_BLIND_MIN`; the register panel gained the blind-method controls and a per-lane `blind_min` read-out; `read_all` issues 3 commands per lane (client pacing test: 52 commands, 0 drops) (source: `beta/gui/CHANGELOG.md`, "2026-10-09 (final register map, RTL 0x0002)"; `beta/gui/aeris10_gui/protocol/register_map.py:18`; `beta/gui/README.md`, limitation 12). 72 tests pass; `--selftest` on the bridge link: 3 frames, 0 CRC errors, 31 REG replies, read-all OK; `--selftest --raw-ft601`: 6144 packets, 0 drops; PyInstaller bundle passes both self-tests (source: `beta/gui/README.md`, "BETA statement", "Run", "Test"; `beta/gui/CHANGELOG.md`, "Verification performed").

**Documentation state between the three BETA trees (observation MAN-04, chapter 17 §6).** The FPGA README and CHANGELOG state that command set v2 is implemented in the RTL, that the register write/read port is wired to `ctl_regs`, and that `HOST_LINK_DESIGN.md` §7 is kept identical to `radar_control_regs.v` (source: `beta/fpga/README.md`, "What was found and decided" item 5, "Host path"; `beta/fpga/CHANGELOG.md`, "Command set v2…"). The GUI tree has been brought to the same map and its earlier discrepancy items 1–3 are struck through as resolved (source: `beta/gui/CHANGELOG.md`, "Discrepancies / unresolved" and "2026-10-09 (final register map, RTL 0x0002)"). Two firmware documents still carry the earlier state: `beta/stm32/README.md` §6a ("The FPGA side of 0x02..0x04 is not implemented in `beta/fpga` yet", line 120) and `beta/stm32/DECISIONS.md` D-18 (same statement, "grep 2026-10-09"); the FPGA README's remaining-work item 8 still names the GUI `register_map.py` 4-bit mask as open although the file now has `ADDR_MASK = 0x1F` (source: `beta/fpga/README.md`, "Remaining work" item 8; `beta/gui/aeris10_gui/protocol/register_map.py:18`). These are stale statements, not functional gaps; the register path is consistent between the RTL, `HOST_LINK_DESIGN.md` §7, the firmware byte sequences and the GUI map, and it has not been exercised on hardware in any combination.

### 3.5 What remains for the host link (source: `HOST_LINK_DESIGN.md` §6; `engineering/DESIGN/HOST_LINK/README.md`, "Not done")

- Option A: Main Board rev. B schematic/layout (MDR-13) — the bank-35 breakout decision above; FT601 datasheet checks; FTDI D3XX host driver test; RTL changes of D-19.
- Option B: bench test of the SPI timing (level shifter path is 3.3 V, no translation needed), CDC throughput measurement, firmware arbitration of SPI1 with the ADAR1000 writes; end-to-end `REG` test on hardware.

## 4. 22 V PA drain supply module DSN-PSU-01 (PROPOSED DESIGN)

The RF PA boards need a 22 V drain supply (`VD`, xlsx row 59: 18–22 V, 2000 mA per board) that exists in no CAD file — conflict K4; the Power Board's input is 12–17 V and it has no 22 V rail (chapter 3 §4.1, rail `+22V0`/`VD`). DSN-PSU-01 closes K4 per decision D-14 with a block schematic, a BOM and a net summary; it has no component-level schematic, no layout and no bench test (source: `engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/README.md`, header; `engineering/DESIGN/00_DESIGN_BASIS.md` §2, D-14).

![F9.1 — DSN-PSU-01 block schematic: 2-phase synchronous boost 12–17 V → 22 V, LM5069 hot-swap enable from EN/DIS_RFPA_VDD, 16 high-side pulse gates from TX_GATE, bulk capacitance, 16 output terminals to the PA boards — PROPOSED DESIGN, no component-level schematic, not built (source: engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.svg; produced by tools/design_pa_supply_schematic.py)](engineering/DESIGN/ELECTRICAL/PA_SUPPLY_22V/DSN-PSU-01_block_schematic.png)

### 4.1 Requirements (source: `PA_SUPPLY_22V/README.md`, copied verbatim)

| Requirement | Value | Source |
|---|---|---|
| Input | 12–17 V (system VIN via slip ring) | xlsx VIN |
| Output | 22 V ± 2 %, 8 A continuous, 46 A pulsed (11.5 % duty) | QPA2962 datasheet, timing |
| Bulk energy | ≥ 2734 µF total for ΔV ≤ 0.5 V per 30 µs chirp | `THERMAL_AND_PA_SUPPLY.md` §5 |
| Enable | `EN/DIS_RFPA_VDD` (existing STM32 pin) → hot-swap switch | `main.h` |
| Pulse gate | `TX_GATE` from the FPGA — **spare pin to allocate (UNRESOLVED)**; without it the system runs case A (591 W) | D-14 |
| Telemetry | PGOOD/FAULT to the MCU (pin to allocate); per-PA drain current already measured by INA241 on the Main Board | schematic |
| Mechanical | 120 × 80 × 25 mm on the head rear wall (DSN-MECH-01) | layout |

### 4.2 Sizing (source: `engineering/DESIGN/THERMAL/THERMAL_AND_PA_SUPPLY.md` §5, copied verbatim)

| Quantity | Value |
|---|---|
| Peak drain current (all 16 PAs at ID_max 2.848 A) | **45.6 A** during each 30 µs chirp |
| Average current, case B (IDQ × gate duty + RF increment × RF duty) | **3.47 A** → 76 W |
| Average current, case A (continuous bias) | 27.3 A → 600 W (not supported by the proposal) |
| Bulk capacitance for ΔV ≤ 0.5 V over a chirp (total) | **2734 µF** → ≥ 220 µF low-ESR polymer per PA board (local, 171 µF each) + 2 × 1000 µF/35 V at the switch module |
| Input current at VIN_min 12 V, η 92% | 6.9 A average (case B) |
| Converter | synchronous boost 12–17 V → 22 V, 2-phase interleaved (LM5122 ×2 or equivalent), 150 W continuous rating, 300 kHz, 2 × 10 µH / 15 A inductors, output ripple < 100 mV |
| Protection / enable | LM5069 hot-swap controller + N-FET high-side switch on the 22 V bus, EN from `EN/DIS_RFPA_VDD` (STM32), current limit 12 A average, dv/dt-limited turn-on; status to the MCU |
| Per-PA pulse gating | 16 × high-side P-FET (−40 V, 30 A pulsed) with fast high-side driver (e.g. LTC7003, ≤ 100 ns), common `TX_GATE` TTL input from the FPGA (spare I/O to be allocated — UNRESOLVED), local 220 µF per channel |
| Sequencing | VG (−4 V via DAC5578) before VD (firmware already does this); gate switch only after `EN/DIS_RFPA_VDD`; power-down reverse |

The drain-gating requirement follows from the thermal analysis: with the drain continuously biased (case A) the 16 QPA2962 dissipate 591 W and the 2-D plate model gives ≈ 213 °C; with per-chirp gating at 11.5 % duty (case B) 68 W, plate 64 °C and PA base ≈ 73 °C at 45 °C ambient (source: `docs/AERIS10_BETA_ENGINEERING_REPORT.md` §9; `engineering/DESIGN/CALCS/DESIGN_CALCULATIONS.md` §1). The BOM's gate switch (N-MOSFET with LTC7003) and the thermal document's "high-side P-FET" describe the same function with different device polarity; the BOM is the later, part-level statement, and the component-level design (MDR-12) must settle it.

### 4.3 Bill of materials (source: `PA_SUPPLY_22V/DSN-PSU-01_BOM.csv`, copied verbatim)

| ref | qty | description | proposed_part | section |
|---|---|---|---|---|
| J1 | 1 | DC input terminal 2-pole 16 A | Phoenix 1792270 or AK300/2 | input |
| F1 | 1 | Fuse 20 A 32 V automotive | Littelfuse 0297020 | input |
| D1 | 1 | TVS 18 V SMB | SMBJ18A | input |
| FL1 | 1 | CM choke 10 µH 15 A + 4×4.7 µF/50 V X7R | Würth 744 823 110 / GRM32ER71H475K | filter |
| U1,U2 | 2 | Sync boost controller | TI LM5122MH | boost |
| Q1–Q4 | 4 | N-MOSFET 100 V 100 A | TI CSD19532Q5B | boost |
| L1,L2 | 2 | Inductor 10 µH 15 A | Coilcraft XAL1580-103 | boost |
| C_out | 4 | Polymer 100 µF/35 V | Panasonic 35SVPF100M | boost |
| C_bulk | 2 | Electrolytic 1000 µF/35 V low ESR | Nichicon UHE1V102MHD | boost/bulk |
| U3 | 1 | Hot-swap controller 9–80 V | TI LM5069MM-1 | switch |
| Q5 | 1 | N-MOSFET 100 V 200 A D2PAK | TI CSD19536KTT | switch |
| Rs | 1 | Sense 2 mΩ 3 W | Bourns CSS2H-2512R-L200F | switch |
| U4–U19 | 16 | High-side gate driver ≤ 100 ns | ADI LTC7003 | gate |
| Q6–Q21 | 16 | N-MOSFET 100 V | TI CSD19532Q5B | gate |
| C_loc | 16 | Polymer 220 µF/35 V | Panasonic 35SVPF220M (or on each PA board) | gate |
| OUT1–16 | 16 | Screw terminal 2-pole | AK300/2 (matches the PA board) | output |

### 4.4 Interfaces and next steps

Cabling: slip ring VIN → DSN-PSU-01 IN (CBL-142, 2 × 2-wire 16 AWG) and DSN-PSU-01 OUT1..16 → PA `22V` terminals (CBL-050, 056, …, 140; 2-wire 18 AWG twisted, AK300/2) in the proposed harness schedule (source: `engineering/DESIGN/HARNESS/HARNESS_SCHEDULE.md`, rows CBL-050…CBL-142; chapter 3 §5). The module occupies 120 × 80 × 25 mm on the head rear wall in the proposed mechanical layout (DSN-MECH-01). Next steps (MDR-12, source: `PA_SUPPLY_22V/README.md`): KiCad component-level schematic → layout (4-layer, 2 oz) → bench test of one gate channel with a 30 µs / 45 A dummy load → EMC pre-check of the boost. Decision needed from the owner: D-14, in particular the `TX_GATE` line (FPGA spare pin, UNRESOLVED — none of the 116 unconstrained RTL ports has a board net; chapter 11 §7) and the telemetry pin (chapter 17 §2).

## 5. Appendix — FT601 pin assignment, option A (source: `engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv`, copied verbatim; identical to `ft601_bank35.xdc` and `beta/pcb/MAIN_BOARD_REVB/README.md` §5)

| ft601_signal | ft601_pad (QFN76, from EAGLE lib) | proposed_net | fpga_pad | fpga_pin_name | direction (FT601 view) | iostandard |
|---|---|---|---|---|---|---|
| CLK | 58 | FT_CLK | C4 | IO_L12N_T1_MRCC_35 | out | LVCMOS33 |
| DATA_0 | 40 | FT_DATA_0 | A2 | IO_L8N_T1_AD14N_35 | bidir | LVCMOS33 |
| DATA_1 | 41 | FT_DATA_1 | A3 | IO_L4N_T0_35 | bidir | LVCMOS33 |
| DATA_2 | 42 | FT_DATA_2 | A4 | IO_L3N_T0_DQS_AD5N_35 | bidir | LVCMOS33 |
| DATA_3 | 43 | FT_DATA_3 | A5 | IO_L3P_T0_DQS_AD5P_35 | bidir | LVCMOS33 |
| DATA_4 | 44 | FT_DATA_4 | A7 | IO_L1N_T0_AD4N_35 | bidir | LVCMOS33 |
| DATA_5 | 45 | FT_DATA_5 | B1 | IO_L9N_T1_DQS_AD7N_35 | bidir | LVCMOS33 |
| DATA_6 | 46 | FT_DATA_6 | B2 | IO_L8P_T1_AD14P_35 | bidir | LVCMOS33 |
| DATA_7 | 47 | FT_DATA_7 | B4 | IO_L4P_T0_35 | bidir | LVCMOS33 |
| DATA_8 | 50 | FT_DATA_8 | B5 | IO_L2N_T0_AD12N_35 | bidir | LVCMOS33 |
| DATA_9 | 51 | FT_DATA_9 | B6 | IO_L2P_T0_AD12P_35 | bidir | LVCMOS33 |
| DATA_10 | 52 | FT_DATA_10 | B7 | IO_L1P_T0_AD4P_35 | bidir | LVCMOS33 |
| DATA_11 | 53 | FT_DATA_11 | C1 | IO_L9P_T1_DQS_AD7P_35 | bidir | LVCMOS33 |
| DATA_12 | 54 | FT_DATA_12 | C2 | IO_L7N_T1_AD6N_35 | bidir | LVCMOS33 |
| DATA_13 | 55 | FT_DATA_13 | C3 | IO_L7P_T1_AD6P_35 | bidir | LVCMOS33 |
| DATA_14 | 56 | FT_DATA_14 | C6 | IO_L5N_T0_AD13N_35 | bidir | LVCMOS33 |
| DATA_15 | 57 | FT_DATA_15 | C7 | IO_L5P_T0_AD13P_35 | bidir | LVCMOS33 |
| DATA_16 | 60 | FT_DATA_16 | D1 | IO_L10N_T1_AD15N_35 | bidir | LVCMOS33 |
| DATA_17 | 61 | FT_DATA_17 | D3 | IO_L11N_T1_SRCC_35 | bidir | LVCMOS33 |
| DATA_18 | 62 | FT_DATA_18 | D4 | IO_L12P_T1_MRCC_35 | bidir | LVCMOS33 |
| DATA_19 | 63 | FT_DATA_19 | D6 | IO_L6P_T0_35 | bidir | LVCMOS33 |
| DATA_20 | 64 | FT_DATA_20 | E1 | IO_L15N_T2_DQS_35 | bidir | LVCMOS33 |
| DATA_21 | 65 | FT_DATA_21 | E2 | IO_L10P_T1_AD15P_35 | bidir | LVCMOS33 |
| DATA_22 | 66 | FT_DATA_22 | E3 | IO_L11P_T1_SRCC_35 | bidir | LVCMOS33 |
| DATA_23 | 67 | FT_DATA_23 | E5 | IO_L13N_T2_MRCC_35 | bidir | LVCMOS33 |
| DATA_24 | 69 | FT_DATA_24 | E6 | IO_0_35 | bidir | LVCMOS33 |
| DATA_25 | 70 | FT_DATA_25 | F2 | IO_L15P_T2_DQS_35 | bidir | LVCMOS33 |
| DATA_26 | 71 | FT_DATA_26 | F3 | IO_L14N_T2_SRCC_35 | bidir | LVCMOS33 |
| DATA_27 | 72 | FT_DATA_27 | F4 | IO_L14P_T2_SRCC_35 | bidir | LVCMOS33 |
| DATA_28 | 73 | FT_DATA_28 | F5 | IO_L13P_T2_MRCC_35 | bidir | LVCMOS33 |
| DATA_29 | 74 | FT_DATA_29 | G1 | IO_L17N_T2_35 | bidir | LVCMOS33 |
| DATA_30 | 75 | FT_DATA_30 | G2 | IO_L17P_T2_35 | bidir | LVCMOS33 |
| DATA_31 | 76 | FT_DATA_31 | G4 | IO_L16N_T2_35 | bidir | LVCMOS33 |
| BE_0 | 4 | FT_BE_0 | G5 | IO_L16P_T2_35 | bidir | LVCMOS33 |
| BE_1 | 5 | FT_BE_1 | H1 | IO_L20N_T3_35 | bidir | LVCMOS33 |
| BE_2 | 6 | FT_BE_2 | H2 | IO_L20P_T3_35 | bidir | LVCMOS33 |
| BE_3 | 7 | FT_BE_3 | H3 | IO_L21N_T3_DQS_35 | bidir | LVCMOS33 |
| TXE_N | 8 | FT_TXE_N | H4 | IO_L18N_T2_35 | out | LVCMOS33 |
| RXF_N | 9 | FT_RXF_N | H5 | IO_L18P_T2_35 | out | LVCMOS33 |
| WR_N | 11 | FT_WR_N | J1 | IO_L22N_T3_35 | in | LVCMOS33 |
| RD_N | 12 | FT_RD_N | J3 | IO_L21P_T3_DQS_35 | in | LVCMOS33 |
| OE_N | 13 | FT_OE_N | J5 | IO_L19P_T3_35 | in | LVCMOS33 |
| SIWU_N | 10 | FT_SIWU_N | K1 | IO_L22P_T3_35 | in | LVCMOS33 |
| RESET_N | 15 | FT_RESET_N | K2 | IO_L24N_T3_35 | in | LVCMOS33 |
| WAKEUP_N | 16 | FT_WAKEUP_N | K3 | IO_L24P_T3_35 | in | LVCMOS33 |
| GPIO0 | 17 | FT_GPIO0 | K5 | IO_25_35 | out | LVCMOS33 |
| GPIO1 | 18 | FT_GPIO1 | L2 | IO_L23N_T3_35 | out | LVCMOS33 |

Of these 47 balls, 36 have no free escape-via position in the rev. A fan-out and 9 have one, 2 have two (section 2.3); the pin plan therefore cannot be routed on the rev. A breakout as it stands (source: `beta/pcb/MAIN_BOARD_REVB/UNROUTED.md` §1).
