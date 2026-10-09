# AERIS-10 Radar Host GUI -- BETA (`beta/gui`)

**BETA statement.** This package has **never been run against hardware**.

* The FPGA -> host data path has **no hardware**: the Main Board's FT601 FIFO bus is
  not wired to the FPGA and there is no FT2232H (`docs/PCB/MAIN_BOARD.md`). The FPGA
  packet parser is verified only against vectors derived by hand from the RTL and
  against the built-in simulator.
* The STM32 USB CDC path (settings upload, status/GPS reception) is implemented from
  the firmware sources but is **unverified on a board**; the firmware RX path itself is
  reported dead in `docs/STM32/`.
* Range/velocity scaling of the display rests on assumptions listed below.

The original GUI versions in `9_Firmware/9_3_GUI/` are untouched; this is a separate
package. `CHANGELOG.md` records what was taken from which original file and every
behavioural change.

## Install

Tested with CPython 3.14.7 + Tk 9.0 on macOS arm64 (2026-10-09). Python >= 3.10 is
declared; older interpreters are unverified. A Tk-enabled Python is required
(`python3 -c "import tkinter"` must work).

```sh
cd beta/gui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt       # pinned to the tested versions
# or, for development:  .venv/bin/pip install -e .[dev,packaging]
```

`pyusb` (optional raw-USB fallback) needs the libusb-1.0 system library
(`brew install libusb` / `apt install libusb-1.0-0`). Nothing else needs system packages.

## Run

```sh
.venv/bin/python -m aeris10_gui --demo            # simulator, no hardware
.venv/bin/python -m aeris10_gui                   # hardware mode: pick the STM32 CDC port, press Start
.venv/bin/python -m aeris10_gui --selftest        # hidden window, 3 simulated frames, exit 0 on success
.venv/bin/python -m aeris10_gui --port /dev/cu.usbmodemXXXX
```

After `pip install -e .` the same is available as `aeris10-gui [--demo]`.

In demo mode the simulator emits, per frame, 2048 packets in the **RTL wire format**
plus a status string in the **firmware format**; the GUI consumes them through the same
parsers it would use for hardware. In hardware mode the FPGA link reports
"FT601 not wired" (see `aeris10_gui/io/ftdi_ft601.py`) and only the CDC link is used.

## Test

```sh
.venv/bin/python -m pytest -q
```

46 tests: settings packet (byte-exact firmware vector, round trip, a model of the
firmware receiver proving unpadded framing is accepted and GUI_V5's 64-byte zero
padding is rejected), FPGA packet (word-level and byte-level vectors from the Verilog,
corruption of footer/redundant copies/detection byte, truncation, stream
resynchronisation), status text / GPS text / GPSB binary, CA-CFAR on synthetic scenes,
DBSCAN clustering, Kalman tracker, simulator -> parser -> assembler exactness,
pipeline target recovery, testbench CSV loading, and a headless Tk smoke test (skipped
if no display).

## Package

```sh
.venv/bin/pip install pyinstaller      # already in requirements.txt
./build_app.sh                         # PyInstaller --onedir -> dist/aeris10-gui/, then runs --demo --selftest
```

Result on the test machine: PyInstaller 6.22.3 on Python 3.14.7 built a 134 MB `--onedir`
bundle and `dist/aeris10-gui/aeris10-gui --demo --selftest` exited 0. If PyInstaller
fails on your interpreter, the fallback is simply `python -m aeris10_gui --demo` inside
the venv. Note: `aeris10_gui/__main__.py` uses a relative import, so PyInstaller is
pointed at `pyinstaller_launcher.py` instead.

## Mapping: original file -> beta module

| Original (`9_Firmware/9_3_GUI/`) | Lines | Beta module | Notes |
|---|---|---|---|
| `GUI_V5.py` `RadarSettings`, `RadarTarget`, `GPSData` dataclasses | 56-88 | `aeris10_gui/model.py` | defaults = firmware defaults |
| `GUI_V5.py` `STM32USBInterface._create_settings_packet` | 454-467 | `protocol/settings_packet.py` | layout re-derived from `RadarSettings.cpp`; padding made a flag (default off) |
| `GUI_V5.py` `STM32USBInterface` (pyusb bulk) | 307-477 | `io/usb_cdc.py` | pyserial CDC-ACM port is primary; pyusb fallback picks the CDC *data* interface |
| `GUI_V5.py` `FTDIInterface` (pyftdi FT2232H) | 479-549 | `io/ftdi_ft601.py` | replaced by an explicit `NotImplementedError` (no hardware) |
| `GUI_V5.py` `RadarProcessor.clustering` | 587-605 | `dsp/clustering.py` | DBSCAN, now actually called |
| `GUI_V5.py` `RadarProcessor.association/tracking` | 607-670 | `dsp/tracking.py` | filterpy Kalman, time injected |
| `GUI_V5.py` `USBPacketParser` (GPS text / GPSB) | 672-751 | `protocol/status_text.py` | 3-field firmware GPS text accepted; status string parser added |
| `GUI_V5.py` `RadarPacketParser` (A5C3 + CRC16) | 753-865 | `protocol/fpga_packet.py` | **replaced**: decodes the RTL format (0xAA ... 0x55, no CRC) |
| `GUI_V5.py` `RadarGUI` (dark theme, control row, notebook, imshow, Treeview, settings tab) | 867-1300 | `ui/main_window.py`, `ui/theme.py` | Google Maps HTML export dropped; PPI polar plot added; no threads |
| `GUI_V6_Demo.py` `SimulatedRadarProcessor` | 61-231 | `sim/simulator.py` | emits I/Q 64x32 + RTL packets + firmware status string |
| `GUI_V6_Demo.py` `animate()` timer loop | 718-748 | `ui/main_window.py` `_tick/step` | |
| `GUI_V4_2_CSV.py` CSV reader | 354-372 | `sim/replay.py` | csv module instead of pandas |
| `test_radar_data.csv` | -- | used by `tests/test_sim_pipeline.py` | read only |
| -- (none existed) | -- | `dsp/cfar.py` | new CA-CFAR 1-D/2-D |
| -- | -- | `processing.py` | frame assembly + pipeline (new) |

## Protocol facts the beta relies on (with sources)

| Item | Source | Beta |
|---|---|---|
| Start flag `17 2E 9E ED` | `USBHandler.cpp:38` | `settings_packet.START_FLAG` |
| 82-byte `SET`+3x`>d`+`>I`+6x`>d`+`END`, big-endian | `RadarSettings.cpp:23-120` | `build_settings_packet`, frozen vector in tests |
| `SET` must be at buffer offset 0 after the flag | `USBHandler.cpp:70` | no zero padding by default (`pad_to_64=False`) |
| Firmware value limits | `RadarSettings.cpp:86-101` | `validate_settings` (UI refuses values the firmware would reject) |
| FPGA packet = 11 FT601 words, `0xAA`, 4 range words, 4 Doppler words, detection, `0x55` | `usb_data_interface.v:39-160` | `fpga_packet.encode_words/decode_packet` |
| `range_profile` = `{Q, I}` Doppler word; `doppler_real` = bits 15:0 | `radar_system_top.v:294-331`, `doppler_processor.v:244` | `encode_cell`, `check_top_level_consistency` |
| Emission order range-major, 64 x 32 cells | `doppler_processor.v:244-266`, `radar_receiver_final.v:291-293` | `processing.FrameAssembler` |
| Detection bit = `|I|+|Q| > 10000` | `radar_system_top.v:318` | simulator |
| Status string fields, `ChirpCount` last | `main.cpp:807-877` | `status_text.parse_status_line` |
| `GPS:%.8f,%.8f,%.2f\r\n` (UART3) and 30-byte `GPSB` (CDC) | `gps_handler.cpp:45-119` | `parse_gps_text`, `parse_gpsb` |

## Assumptions and known limitations

1. **A1 -- FT601 byte-lane order.** Bus words are mapped to the host byte stream
   little-endian (lane 0 = `DATA[7:0]` first); `be=01` -> 1 byte, `be=11` -> 4 bytes.
   The RTL declares a 2-bit `ft601_be` for a 32-bit bus (FT601 has 4 byte enables);
   this is an RTL defect to resolve at bring-up. Packet length 35 bytes follows from A1.
2. **No CRC in the RTL packet.** Integrity checking uses header, footer and the
   redundant shifted copies the RTL emits. The simulation-only `usb_packet_analyzer.v`
   expects a *different* layout from the writer; the beta follows the writer.
3. **No bin indices in the packet.** The host counts packets to place cells; any lost
   packet shifts the whole frame until the next resync. Needs a frame marker in the RTL.
4. **Range scaling UNVERIFIED**: cell `r` -> `r * max_distance / 64` m. The physical
   spacing of the 64 decimated range bins is not documented anywhere in the repository.
5. **Velocity scaling** uses the standard pulse-Doppler relation with `prf1` and
   `system_frequency`, natural FFT order (bins >= N/2 negative). Not confirmed against RTL.
6. **Azimuth angle** = `(Azimuth-1) * 360/50` degrees from `main.cpp:188-189`; the
   firmware has no angle table. `BeamPos` (elevation index) is shown as an index.
7. **Settings acknowledgement** does not exist in the protocol; the UI cannot confirm
   the firmware accepted the packet.
8. The status string from the firmware has no terminator; the parser uses the
   `ChirpCount:<n>|` field as end marker.
9. Google Maps export (placeholder API key in V4-V6) was dropped.
10. `filterpy` 1.4.5 (2018) runs on numpy 2.5.3 here; long-term maintenance risk.
11. Only CPython 3.14.7/Tk 9.0 on macOS was exercised; Windows/Linux and older Pythons
    are unverified.
