# beta/ — BETA completions of the missing AERIS-10 elements

Created 2026-10-09. Everything here is **BETA**: it builds/parses/simulates/routes with the tools on the authoring machine but has **not** been synthesised in Vivado, flashed, run on hardware, reviewed by the original designer or fabricated. Originals under `9_Firmware/` and `4_Schematics and Boards Layout/` are untouched; each sub-project starts from a copy and keeps a `CHANGELOG.md` of every change.

| Sub-project | Content | Build/verify | Status |
|---|---|---|---|
| `fpga/` | RTL copies with syntax/driver fixes, the 5 missing modules (ADC capture, matched-filter chain, range-bin decimator, FFT wrappers), seg3 `.mem`, self-checking testbenches, timing + schematic-derived XDC, Vivado Tcl | `bash beta/fpga/build.sh` (iverilog + verilator) | see `fpga/README.md` |
| `stm32/` | Firmware copies with the 7 defect fixes and hardware-truth decisions (8 MHz HSE), hand-written CubeMX-equivalent files (USB CDC, startup, linker, HAL conf), CMake build with the ARM GNU toolchain, host unit tests | `bash beta/stm32/build.sh` | see `stm32/README.md` |
| `gui/` | `aeris10_gui` package: firmware-exact settings packet, FPGA packet parser, CDC I/O, CFAR/clustering/tracking, simulator, Tk UI, pytest suite, PyInstaller | `pytest -q` in `beta/gui` | see `gui/README.md` |
| `pcb/` | KiCad routing completion (Freerouting), placement of off-board parts, DRC dispositions, BOMs with proposed MPNs, fabrication notes/stack-up proposals, re-exported packages | DRC reports in each board folder | see `pcb/README.md` |

Simulation of the proposed antenna (openEMS, built from source on this machine) is reported in `engineering/DESIGN/ANTENNA/` once run.
