#!/usr/bin/env python3
"""PROPOSED DESIGN — FPGA → host data path for AERIS-10 (DSN-LINK-01).

Option A  "FT601 on Main Board rev. B": wire the unconnected U6 (FT601Q) to the 50 free
          I/Os of FPGA bank 35 (VCCO = +3V3_FPGA); 32-bit FT245 synchronous FIFO at 100 MHz.
Option B  "SPI bridge, no PCB change": FPGA = SPI slave on the existing STM32 SPI1 lines
          (STM32_SCLK1/MOSI1/MISO1 → FPGA J16/H13/G14) with the unused DIG_5/DIG_6 lines as
          CS / DRDY, compact range-Doppler frames forwarded by the STM32 over USB CDC.
Reads the Main Board schematic (EAGLE XML) for U6 / U42 pins and writes
engineering/DESIGN/HOST_LINK/{HOST_LINK_DESIGN.md, ft601_pin_assignment.csv, ft601_bank35.xdc,
ft601_added_parts_BOM.csv, option_b_signal_map.csv}.  Usage: python3 tools/design_host_link.py
"""
import csv, datetime as _dt, os, re, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = os.path.join(ROOT, "4_Schematics and Boards Layout/4_6_Schematics/MainBoard/RADAR_Main_Board.sch")
OUT = os.path.join(ROOT, "engineering/DESIGN/HOST_LINK")
os.makedirs(OUT, exist_ok=True)
DATE = _dt.date.today().isoformat()
root = ET.parse(SCH).getroot()


def part_pins(ref):
    part = [p for p in root.iter("part") if p.get("name") == ref][0]
    L = [l for l in root.iter("library") if l.get("name") == part.get("library")][0]
    DS = [d for d in L.iter("deviceset") if d.get("name") == part.get("deviceset")][0]
    dev = [d for d in DS.find("devices").findall("device") if d.get("name", "") == part.get("device", "")][0]
    pad = {(c.get("gate"), c.get("pin")): c.get("pad") for c in dev.find("connects").findall("connect")}
    out = []
    for g in DS.find("gates").findall("gate"):
        sym = [s for s in L.iter("symbol") if s.get("name") == g.get("symbol")][0]
        for p in sym.findall("pin"):
            out.append((g.get("name"), p.get("name"), pad.get((g.get("name"), p.get("name")))))
    return out


netrows = list(csv.DictReader(open(os.path.join(ROOT, "engineering/ELECTRICAL/netlists/MAIN_BOARD_netlist_by_part.csv"))))
u42_conn = {(r["gate"], r["pin"]): r["net"] for r in netrows if r["part"] == "U42"}
u42 = part_pins("U42")
free35 = sorted([(pad, name) for g, name, pad in u42 if name.endswith("_35") and (g, name) not in u42_conn], key=lambda t: (t[0][0], int(t[0][1:])))
u6 = part_pins("U6")
# --- Option A assignment -------------------------------------------------------
cc = [p for p in free35 if "MRCC" in p[1] or "SRCC" in p[1]]
clk_pin = [p for p in cc if "MRCC" in p[1]][0]
pool = [p for p in free35 if p != clk_pin and "VREF" not in p[1]]
signals = [f"DATA_{i}" for i in range(32)] + [f"BE_{i}" for i in range(4)] + ["TXE_N", "RXF_N", "WR_N", "RD_N", "OE_N", "SIWU_N", "RESET_N", "WAKEUP_N", "GPIO0", "GPIO1"]
assign = [("CLK", clk_pin)]
for s, p in zip(signals, pool):
    assign.append((s, p))
ft_pad = {name: pad for g, name, pad in u6}
with open(os.path.join(OUT, "ft601_pin_assignment.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["ft601_signal", "ft601_pad(QFN76, from EAGLE lib)", "proposed_net", "fpga_pad", "fpga_pin_name", "direction(FT601 view)", "iostandard"])
    for s, (pad, name) in assign:
        d = "out" if s in ("CLK", "TXE_N", "RXF_N", "GPIO0", "GPIO1") else ("in" if s in ("WR_N", "RD_N", "OE_N", "SIWU_N", "RESET_N", "WAKEUP_N") else "bidir")
        w.writerow([s, ft_pad.get(s, "?"), f"FT_{s}", pad, name, d, "LVCMOS33"])
xdc = [f"## FT601 32-bit FT245 synchronous FIFO on FPGA bank 35 — PROPOSED (DSN-LINK-01 option A, {DATE})",
       "## Bank 35 VCCO = +3V3_FPGA (schematic); FT601 VCCIO = 3.3 V. Pins chosen from the 50 I/Os of bank 35 that have NO net",
       "## in RADAR_Main_Board.sch; they become real only after the Main Board rev. B routes them (see HOST_LINK_DESIGN.md).",
       "## RTL port names follow 9_Firmware/9_2_FPGA/usb_data_interface.v (ft601_*); BE must be widened to 4 bits (RTL defect).", ""]
rtl_name = {"CLK": "ft601_clk", "TXE_N": "ft601_txe_n", "RXF_N": "ft601_rxf_n", "WR_N": "ft601_wr_n", "RD_N": "ft601_rd_n", "OE_N": "ft601_oe_n",
            "SIWU_N": "ft601_siwu_n", "RESET_N": "ft601_reset_n", "WAKEUP_N": "ft601_wakeup_n", "GPIO0": "ft601_gpio[0]", "GPIO1": "ft601_gpio[1]"}
for s, (pad, name) in assign:
    port = rtl_name.get(s) or (f"ft601_data[{s[5:]}]" if s.startswith("DATA_") else f"ft601_be[{s[3:]}]")
    xdc.append(f"set_property -dict {{PACKAGE_PIN {pad} IOSTANDARD LVCMOS33}} [get_ports {{{port}}}]   ;# {name}")
xdc += ["", "## FT601 drives CLK (100 MHz in 245 synchronous mode, 66 MHz option); data is launched/captured on that clock",
        "create_clock -period 10.000 -name ft601_clk [get_ports ft601_clk]",
        "set_clock_groups -asynchronous -group [get_clocks ft601_clk] -group [get_clocks -include_generated_clocks clk_100m]",
        "## FT601 datasheet AC timing (tsetup/thold vs CLK) MUST be entered here once the datasheet values are confirmed:",
        "# set_input_delay  -clock ft601_clk -max <t_co_max> [get_ports {ft601_data[*] ft601_be[*] ft601_txe_n ft601_rxf_n}]",
        "# set_output_delay -clock ft601_clk -max <t_su>     [get_ports {ft601_data[*] ft601_be[*] ft601_wr_n ft601_rd_n ft601_oe_n}]",
        "set_property SLEW FAST [get_ports {ft601_data[*] ft601_be[*] ft601_wr_n ft601_rd_n ft601_oe_n}]"]
open(os.path.join(OUT, "ft601_bank35.xdc"), "w").write("\n".join(xdc) + "\n")
bom = [("J_USB3", 1, "USB 3.1 Gen1 receptacle (Type-C, USB 2.0 + one SuperSpeed pair used) or USB 3.0 micro-B", "GCT USB4085-GF-A (Type-C) / Amphenol GSB4211111WEU (micro-B 3.0)", "VERIFY pin-out; SS pairs TODP/TODN ↔ RIDP/RIDN per FT601 datasheet"),
       ("Y_FT", 1, "Crystal 30 MHz ±30 ppm, 18 pF", "Abracon ABM8-30.000MHZ-B2-T", "FT601 XI/XO (pads 21/22) + 2 × 18 pF (VERIFY load per datasheet)"),
       ("R_RREF", 1, "Resistor 3.24 kΩ 1 % 0402", "Yageo RC0402FR-073K24L", "FT601 RREF (pad 27) — value per FT60x datasheet, VERIFY"),
       ("C_VD10", 4, "Capacitor 4.7 µF 6.3 V 0402 + 100 nF", "Murata GRM155R60J475ME47D", "1.0 V core pins VD10/VD10_2..4/DV10 (pads 3,30,33,39,48): FT60x internal regulator output, decouple each — VERIFY"),
       ("C_AVDD", 2, "Capacitor 100 nF / 1 µF 0402", "Murata GRM155R71C104KA88D", "AVDD/VDDA (pads 2, 28) analogue 3.3 V via ferrite from +3V3_FT"),
       ("FB_A", 1, "Ferrite bead 600 Ω@100 MHz 0603", "Murata BLM18PG601SN1D", "+3V3_FT → AVDD"),
       ("D_ESD", 1, "USB 3.0 ESD array (SS + HS)", "TI TPD4E05U06", "on connector side of the SS and D± pairs"),
       ("R_VBUS", 2, "Resistor divider 10 k / 3.3 k (VBUS detect, pad 37)", "Yageo RC0402", "VERIFY VBUS pin voltage limit in datasheet"),
       ("L19/C184-C186", 0, "already in the schematic: +3V3_FT = +3V3_FPGA via L19; 10 µF + 100 nF + 1 nF", "—", "present (U6 pads 20, 24, 38 VCC33; 14, 49, 59, 68 VCCIO) — nets to be connected")]
with open(os.path.join(OUT, "ft601_added_parts_BOM.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["ref", "qty", "description", "proposed_part", "note"]); w.writerows(bom)
# --- Option B map ----------------------------------------------------------------
optb = [("FPGA_CS_N (option B)", "DIG_5", "STM32 PD13 (today configured INPUT in main.cpp:2313-2317 → becomes OUTPUT)", "U42 H11 (IO_L19P_T3_A22_15)", "STM32 → FPGA", "active-low chip select for the bridge; ADAR1000 pass-through is gated off while low"),
        ("DRDY (option B)", "DIG_6", "STM32 PD14 (INPUT, EXTI14)", "U42 G12 (IO_L19N_T3_A21_VREF_15)", "FPGA → STM32", "a complete frame is in the FPGA TX FIFO"),
        ("spare / ACK", "DIG_7", "STM32 PD15", "U42 H12 (IO_L20P_T3_A20_15)", "FPGA → STM32", "reserved (frame dropped / overflow flag)"),
        ("SCLK", "STM32_SCLK1", "STM32 PA5 (SPI1_SCK)", "U42 J16 (IO_L23N_T3_FWE_B_15)", "STM32 → FPGA", "existing net, 3.3 V; ≤ 27 MHz (SPI1 on APB2 108 MHz, prescaler 4)"),
        ("MOSI", "STM32_MOSI1", "STM32 PA7 (SPI1_MOSI)", "U42 H13 (IO_L20N_T3_A19_15)", "STM32 → FPGA", "existing; carries the bridge command byte"),
        ("MISO", "STM32_MISO1", "STM32 PA6 (SPI1_MISO)", "U42 G14 (IO_L21P_T3_DQS_15)", "FPGA → STM32", "existing; frame bytes, MSB first, mode 0"),
        ("ADAR_n_CS_3V3", "ADAR_1..4_CS_3V3", "STM32 GPIO", "U42 bank 15", "STM32 → FPGA", "unchanged; must all be HIGH during a bridge transfer (firmware guarantees; RTL also checks)")]
with open(os.path.join(OUT, "option_b_signal_map.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["signal", "schematic_net", "stm32_pin", "fpga_pin", "direction", "note"]); w.writerows(optb)
# --- budget --------------------------------------------------------------------
cells = 64 * 32
frame_us = 16 * 167 + 175.4 + 16 * 175
raw_bps = cells * 44 / (frame_us * 1e-6)
map_bytes = 16 + cells + 2 + 3 * 32 + 2
map_bps = map_bytes / (frame_us * 1e-6)
md = f"""# FPGA → host data path — DSN-LINK-01 (PROPOSED DESIGN)

Rev A · {DATE} · generator `tools/design_host_link.py` · status **PROPOSED DESIGN** (option B implemented as BETA code, not run on hardware; option A needs a Main Board revision).

## 1. Problem

The RTL streams radar data through an FT601 USB 3.0 FIFO (`usb_data_interface.v`), but on the Main Board **U6 (FT601Q) has 0 of 77 pins connected** — only the decoupling of its `+3V3_FT` rail exists (L19, C184–C186). The only wired host link is the STM32 USB-FS CDC (X53). Conflict K3.

## 2. Data-rate budget (from the RTL geometry and firmware timing)

| Quantity | Value | Basis |
|---|---|---|
| Range-Doppler cells per beam position | 64 × 32 = {cells} | `doppler_processor.v` (RANGE_BINS 64, 32 chirps) |
| Beam-position frame time | {frame_us:.1f} µs | `main.cpp:180-186` |
| Raw RTL packet stream (44 B per cell) | **{raw_bps/1e6:.1f} MB/s** | `usb_data_interface.v` (11 × 32-bit words) |
| Compact map frame (8-bit log-magnitude per cell + header + ≤ 32 detections + CRC) | {map_bytes} B → **{map_bps/1e3:.0f} kB/s** | this design, §5 |
| STM32 USB-FS CDC practical limit | ≈ 0.8–1.1 MB/s | USB 2.0 FS bulk (19 × 64 B per 1 ms frame max) |
| SPI1 STM32 ↔ FPGA (existing lines) | 27 Mbit/s ≈ 3.3 MB/s (DMA) | APB2 108 MHz / 4 (beta clock tree) |
| FT601 245 sync FIFO, 32 bit @ 100 MHz | up to 400 MB/s | FT601 |

Conclusion: the raw stream needs the FT601 (option A); the compact map fits the existing STM32 path with 3× margin (option B).

## 3. Options

| | A — FT601 on Main Board rev. B | B — SPI bridge via STM32 (no PCB change) | C — Ethernet mezzanine on bank 35 (future) |
|---|---|---|---|
| Hardware change | route U6 to bank 35 (46 I/Os), add USB 3 connector, crystal, RREF, ESD (`ft601_added_parts_BOM.csv`) | none: DIG_5/6/7 + SPI1 are already routed to the FPGA | new PCB with RGMII PHY on the 50 free bank-35 pins |
| Throughput | 400 MB/s | ≤ 1 MB/s (CDC-bound) | 100 MB/s |
| Firmware/RTL | RTL already written (fix 2-bit BE → 4-bit; honour TXE_N); host driver FTDI D3XX | new RTL `host_bridge_spi.v` + packer; STM32 `host_bridge.c`; GUI parser | new MAC/UDP stack |
| Risk | 10-layer board respin; USB 3 SI | protocol only; SPI1 shared with ADAR1000 (time-multiplexed) | highest |
| Decision | **D-16: target for rev. B** | **D-17: implement now (BETA)** | D-18: documented only |

## 4. Option A — pin plan (bank 35, all pins currently without nets)

`ft601_pin_assignment.csv` maps every FT601 signal to a free bank-35 pad (CLK on the MRCC pin {clk_pin[0]} = `{clk_pin[1]}`); `ft601_bank35.xdc` is the matching constraint fragment. FT601 pad numbers come from the EAGLE library symbol used in the schematic (U6 `FT601Q-B-T`); the **FT601 datasheet is not in the repository** — AC timing, RREF value, VBUS limits and the 1.0 V core supply arrangement (VD10 pins) must be verified against it before the schematic is edited. Rev. B schematic work: connect U6 VCC33 (pads 20/24/38) and VCCIO (14/49/59/68) to `+3V3_FT`, GND pads, the 46 signals per the CSV, XI/XO crystal, RREF, VBUS divider, D±/SS pairs to the new connector through the ESD array; route the 32-bit bus as a length-matched group (±25 mm, 100 MHz single-ended, 50 Ω) on the two bank-35 side layers.

Decision D-19 for the RTL: widen `ft601_be` to 4 bits, drive `BE = 4'b1111` for full words, respect `TXE_N` back-pressure, add `ft601_reset_n`/`wakeup_n`/`siwu_n` as outputs — recorded for `beta/fpga` (not yet applied there).

## 5. Option B — SPI bridge (implemented, BETA)

Signals: `option_b_signal_map.csv`. Transfer: STM32 waits for DRDY (EXTI on PD14), pulls `FPGA_CS_N` low, clocks one command byte (0x01 = read frame) and then reads the frame over MISO with DMA (SPI1 mode 0, MSB first, ≤ 27 MHz); the FPGA holds the ADAR1000 pass-through idle while `FPGA_CS_N` is low; the firmware never starts an ADAR1000 SPI transaction while a bridge read is in progress (both share SPI1).

Frame (little-endian, `engineering/DESIGN/HOST_LINK/gui/bridge_frame.py` is the reference parser):

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
| 16 | 2048 | magnitude map, uint8 = 8·log2(|I|+|Q|) saturated, range-major |
| 2064 | 3·n_det | detections: range u8, doppler u8, mag u8 |
| end | 2 | CRC-16/CCITT-FALSE over bytes 0..end-1 |

The STM32 forwards each frame unchanged over CDC (`AERIS_USB_SendBridgeFrame`), interleaved with the existing status strings (the GUI stream parser resyncs on the sync word; status strings never contain `0xA5 0x5A`).

Files: `rtl/host_bridge_spi.v` (SPI slave + frame FIFO, 1 BRAM), `rtl/rd_map_packer.v` (cell → frame builder, CRC), `rtl/tb_host_bridge.v` (self-checking iverilog test: a behavioural SPI master reads a frame and checks sync/CRC/payload), `stm32/host_bridge.c/.h` (SPI1 DMA + EXTI + CDC forward), `gui/bridge_frame.py` (+ tests). Integration into `beta/fpga`, `beta/stm32`, `beta/gui` is recorded in their CHANGELOGs.

## 6. What remains

- Option A: Main Board rev. B schematic/layout (MDR-13), FT601 datasheet checks, FTDI D3XX host driver test; option B: bench test of the SPI timing (level shifter path is 3.3 V, no translation needed), CDC throughput measurement, firmware arbitration of SPI1 with the ADAR1000 writes.
"""
open(os.path.join(OUT, "HOST_LINK_DESIGN.md"), "w").write(md)
print("free bank-35 pins:", len(free35), "assigned:", len(assign), "clk:", clk_pin, "| raw", round(raw_bps/1e6, 1), "MB/s; map", round(map_bps/1e3), "kB/s")
