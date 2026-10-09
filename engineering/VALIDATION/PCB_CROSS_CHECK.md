# PCB cross-check: EAGLE XML vs KiCad conversion

Generated 2026-10-09 by `tools/gen_engineering_pcb_docs.py`. Every row compares a quantity counted directly in the EAGLE `.brd` XML with the same quantity reported by KiCad after `kicad-cli pcb import`. A mismatch means the conversion must be reviewed before the KiCad outputs are used.

### RF_PA

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 35.0 | 35.0 | OK |  |
| Height (mm) | 60.0 | 60.0 | OK |  |
| Footprints = EAGLE elements + free holes | 32 | 32 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 342 | 342 | OK |  |
| Tracks (signal wires excl. airwires) | 77 | 77 | OK |  |
| Copper layers | 4 | 4 | OK |  |
| NPTH holes (free holes + package holes) | 7 | 7 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 357 | 357 | OK |  |

Missing KiCad reports: none; EAGLE airwires 0 → KiCad unconnected after fill 1.

### FREQUENCY_SYNTHESIZER

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 100.0 | 100.0 | OK |  |
| Height (mm) | 100.0 | 100.0 | OK |  |
| Footprints = EAGLE elements + free holes | 188 | 188 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 769 | 769 | OK |  |
| Tracks (signal wires excl. airwires) | 1374 | 1374 | OK |  |
| Copper layers | 6 | 6 | OK |  |
| NPTH holes (free holes + package holes) | 4 | 4 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 863 | 863 | OK |  |

Missing KiCad reports: none; EAGLE airwires 0 → KiCad unconnected after fill 0.

### MAIN_BOARD

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 260.0 | 260.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 784 | 784 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 2893 | 2893 | OK |  |
| Tracks (signal wires excl. airwires) | 10219 | 10219 | OK |  |
| Copper layers | 10 | 10 | OK |  |
| NPTH holes (free holes + package holes) | 10 | 10 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 3314 | 3314 | OK |  |

Missing KiCad reports: none; EAGLE airwires 2390 → KiCad unconnected after fill 15.

### POWER_SUPPLY

| Check | EAGLE (XML) | KiCad | Result | Note |
|---|---|---|---|---|
| Width (mm) | 280.0 | 280.0 | OK |  |
| Height (mm) | 300.0 | 300.0 | OK |  |
| Footprints = EAGLE elements + free holes | 320 | 320 | OK | KiCad imports every free <hole> as a footprint |
| Vias | 346 | 346 | OK |  |
| Tracks (signal wires excl. airwires) | 570 | 570 | OK |  |
| Copper layers | 2 | 2 | OK |  |
| NPTH holes (free holes + package holes) | 8 | 8 | OK | pads with drill but no copper are NPTH in KiCad too |
| PTH holes (vias + THT pads) | 444 | 444 | OK |  |

Missing KiCad reports: none; EAGLE airwires 309 → KiCad unconnected after fill 308.

