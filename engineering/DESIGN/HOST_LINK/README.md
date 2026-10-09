# DSN-LINK-01 — FPGA → host data path (PROPOSED DESIGN; option B implemented as BETA)

| File | Content | Verified by |
|---|---|---|
| `HOST_LINK_DESIGN.md` | problem, data-rate budget, options A/B/C, decisions D-16…D-19, pin plans, frame format | — |
| `ft601_pin_assignment.csv`, `ft601_bank35.xdc`, `ft601_added_parts_BOM.csv` | option A: FT601 on the 50 free bank-35 pins (CLK on MRCC C4), constraint fragment, parts to add for Main Board rev. B | pins cross-checked against the EAGLE netlist (no nets on those pads) |
| `option_b_signal_map.csv` | option B: existing nets DIG_5/6/7 + SPI1 ↔ FPGA pads | schematic netlist |
| `rtl/rd_map_packer.v`, `rtl/host_bridge_spi.v` | FPGA frame builder + SPI slave bridge (Verilog-2001) | `rtl/run_tb.sh` → `PASS tb_host_bridge` (iverilog); verilator `-Wall` clean except width warnings |
| `rtl/tb_host_bridge.v` | self-checking testbench; dumps `tb_frame.hex` used by the GUI tests | — |
| `stm32/host_bridge.c/.h` | STM32 driver (EXTI + SPI1 + CDC forward); integrated into `beta/stm32` | `beta/stm32/build.sh` exit 0 |
| `gui/bridge_frame.py` | reference parser; integrated into `beta/gui/aeris10_gui/protocol/` | `pytest tests/test_bridge_frame.py` 9 passed, on the RTL vector |

Not done: integration of the packer into `beta/fpga` (the FPGA beta agent was still working; hook it between `doppler_processor` and the existing `usb_data_interface`, and gate the ADAR1000 SPI pass-through with `bridge_active`), `ui/sources.py` hardware source switch to the bridge frames, bench test of SPI timing and CDC throughput, Main Board rev. B for option A.
