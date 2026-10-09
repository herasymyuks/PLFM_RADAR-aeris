# Host GUI software — install, run, protocol, register panel, packaging

**Author of this chapter:** Antidrone Ukraine · antidrone.cc (compilation of the BETA package `beta/gui`; the upstream scripts `9_Firmware/9_3_GUI/GUI_V1…V6*.py` are ORIGINAL PROJECT FILE and untouched).

**Status summary:** **BETA** — "This package has **never been run against hardware**" (source: `beta/gui/README.md`, "BETA statement"). Module and runtime diagrams SD-05/SD-06 are SOURCE-DERIVED from the original scripts. The test suite, the headless self-test and the PyInstaller bundle were executed on the authoring workstation (CPython 3.14, Tk 9.x, macOS arm64); Windows/Linux and older interpreters are unverified. The demo figure F13.3 is a render of the plot canvas only (see its caption).

**Sources:** `beta/gui/README.md`, `beta/gui/CHANGELOG.md`, `docs/GUI/INSTALLATION.md`, `docs/GUI/DEPENDENCIES.md`, `engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.md`, `beta/gui/aeris10_gui/protocol/register_map.py`, `beta/fpga/rtl/radar_control_regs.v`, `beta/gui/pyproject.toml`.

**Figures in this chapter:** F13.1 module graph (SD-05), F13.2 runtime architecture (SD-06), F13.3 demo-mode plot render.

## 13.1 Which program is the application

The upstream directory holds nine GUI versions; only one is runnable offline and only one is hardware-capable (source: `docs/GUI/DEPENDENCIES.md` §1, copied):

| File | Lines | State | Runnable? |
|---|---:|---|---|
| `GUI_V1.py` | 41 | fragment of one method with a leading indent — `IndentationError` line 2 | no |
| `GUI_V2.py` | 1 059 | complete (STM32 CDC, FTDI, DBSCAN, Kalman, matplotlib) | parses, imports OK; hardware needed |
| `GUI_V3.py` | 1 146 | complete; pitch in GPS packet | parses; hardware |
| `GUI_V4.py` | 1 427 | complete; Google Maps HTML with placeholder API key (`:229`) | parses; hardware; network |
| `GUI_V4_2_CSV.py` | 678 | offline CSV replay; two defects (`:354-368` derives columns before `read_csv`; `:430` lambda captures unbound `e`) | parses; offline |
| `GUI_V5.py` | 1 542 | **last complete hardware GUI**; V5 buffer-advance bug `:1313` vs `:809-816` (packet length always 6) | parses; hardware |
| `GUI_V5_Demo.py` | 1 356 | truncated (`:696`, `:1339` "Rest of the methods remain the same"); `RadarGUI` calls 9 undefined methods → `AttributeError` at `:955` | **no** |
| `GUI_V6.py` | 617 | partial rewrite for FT601: `RadarProcessor`, `USBPacketParser`, `RadarPacketParser`, `MapGenerator` are `pass` stubs (`:90-92`, `:365-375`); `create_gui`/`configure_dark_theme` `pass` (`:419-425`); `STM32USBInterface` undefined (`:392`); `get_packet_length` returns constant 64 (`:597-600`) | **no** |
| `GUI_V6_Demo.py` | 1 221 | self-contained simulator (`SimulatedRadarProcessor` `:61-231`), only numpy + matplotlib + tkinter | **yes (offline)** — module import verified; window not launched |

No GUI version could decode the RTL's actual packet (`A5C3`+CRC16 expected vs the RTL's `0xAA … 0x55` without CRC — `docs/GUI/DEPENDENCIES.md` §6 row 5), and both FTDI paths (FT2232H in V2–V5, FT601 in V6) have no hardware on the Main Board (same §4). The BETA package `beta/gui/aeris10_gui` therefore re-implements the host from the firmware and RTL sources; the provenance of every beta module is tabulated in `beta/gui/README.md` ("Mapping: original file -> beta module") and `CHANGELOG.md` ("Provenance").

![F13.1 — Python GUI modules: imports and definitions of the nine upstream scripts, classified stdlib / third-party / local (SD-05; auto-generated) — SOURCE-DERIVED (source: engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.png; produced by tools/gen_python_module_graph.py + Graphviz dot)](engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_modules.png)

![F13.2 — Python GUI runtime architecture as found in GUI_V5.py / GUI_V6_Demo.py: threads, queues, parsers, processor, Tk timer; clustering/tracking defined but never called in V5 (SD-06) — SOURCE-DERIVED (source: engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_architecture.png; produced by hand-authored DOT + Graphviz)](engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_architecture.png)

## 13.2 BETA package: what it implements

(source: `beta/gui/README.md`, "BETA statement", condensed)

- **FPGA → host data:** default path is the **SPI bridge (option B, DSN-LINK-01)**: the FPGA serves 64 × 32 log-magnitude frames over SPI, the STM32 forwards them unchanged over USB CDC interleaved with status strings and `REG` replies (frame layout in chapter 12 §12.7). Simulated and unit-tested only. The raw 35-byte RTL packet path (option A, FT601) remains behind `--raw-ft601`; "on the board the FT601 is not wired".
- **FPGA register access:** `REG W/R` over CDC and the "FPGA registers / ADC calibration" tab follow `beta/fpga/rtl/radar_control_regs.v`; the text protocol "is **the same as the firmware's**" (`beta/stm32/Core/Src/host_bridge_proto.c`): one command per USB transfer, replies `REG 0x%04X 0x%08X\r\n` / `REG ERR\r\n`, a write echoes the written value, single firmware command slot → the GUI sends one command at a time and waits (timeout + retransmit). "Not bench-tested; the top-level RTL still ties the register write port off."
- **STM32 CDC path** (settings upload, status/GPS reception): implemented from the firmware sources, "unverified on a board".
- **Range/velocity scaling** of the display rests on assumptions (§13.7).

Protocol facts the beta relies on (source: `beta/gui/README.md`, "Protocol facts", copied):

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

Package modules (source: `beta/gui/README.md` mapping table; `CHANGELOG.md` "Added"): `model.py` (dataclasses, firmware defaults), `protocol/settings_packet.py`, `protocol/status_text.py`, `protocol/fpga_packet.py`, `protocol/bridge_frame.py`, `protocol/register_cmd.py`, `protocol/register_map.py`, `io/usb_cdc.py` (pyserial CDC-ACM primary, pyusb fallback on the CDC *data* interface), `io/ftdi_ft601.py` (stub raising `NotImplementedError`), `dsp/cfar.py` (new CA-CFAR), `dsp/clustering.py` (DBSCAN, now actually called), `dsp/tracking.py` (filterpy Kalman), `sim/simulator.py`, `sim/replay.py`, `sim/register_file.py` (in-memory model of `radar_control_regs.v`), `processing.py`, `ui/main_window.py`, `ui/theme.py`, `ui/sources.py` (`LinkDecoder`, default link `bridge`), `ui/register_panel.py`, `app.py`/`__main__.py`.

## 13.3 Installation

### Step 13.1 — Create the environment and install [BETA, executed]

- **Purpose:** reproducible interpreter with the pinned dependencies.
- **Parts & tools:** Python ≥ 3.10 with Tk (`python3 -c "import tkinter"` must work); tested with CPython 3.14.7 + Tk 9.0 on macOS arm64 (source: `beta/gui/README.md`, "Install"); `beta/gui/requirements.txt` ("pinned to the tested versions"), `pyproject.toml` (extras `dev` = pytest ≥ 7, `packaging` = pyinstaller ≥ 6.0).
- **Action:**

```sh
cd beta/gui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt       # pinned to the tested versions
# or, for development:  .venv/bin/pip install -e .[dev,packaging]
```

  `pyusb` (optional raw-USB fallback) needs the libusb-1.0 system library (`brew install libusb` / `apt install libusb-1.0-0`); nothing else needs system packages.
- **Check:** `.venv/bin/python -m aeris10_gui --version` prints `aeris10-gui 0.7.0b1` (version string from `app.py` `--version`; package version in `CHANGELOG.md` "0.7.0b1").
- **Figure:** —
- **⚠ Decision:** Tk 9.1 upgrade note — "Homebrew had upgraded `tcl-tk` to 9.1, which broke `_tkinter` … Fixed with `brew reinstall python-tk@3.14`" (source: `beta/gui/CHANGELOG.md`, "Environment note").

Dependency ranges (source: `docs/GUI/DEPENDENCIES.md` §2, for the upstream scripts; the beta pins the tested versions in `requirements.txt`): numpy 2.5.3 (`>=1.24,<3`, UNVERIFIED below 2.5.3), scipy 1.18.1, matplotlib 3.11.2 (TkAgg), scikit-learn 1.9.1, filterpy 1.4.5 ("last release 2018 … runs on numpy 2.5.3 here; long-term maintenance risk" — `beta/gui/README.md` assumption 10), crcmod 1.7, pyusb 1.3.1, pyserial (added by the beta as the primary CDC transport), pyinstaller 6.22.3. `pyftdi` "does not support FT601" (`docs/GUI/DEPENDENCIES.md` §2) and is not used by the beta.

## 13.4 Running

### Step 13.2 — Run in demo, self-test or hardware mode [BETA]

- **Purpose:** start the application against the simulator (no hardware) or against the STM32 CDC port.
- **Parts & tools:** the venv of Step 13.1; for hardware mode the STM32 CDC port (after chapter 16 Step 16.1).
- **Action:** (source: `beta/gui/README.md`, "Run", copied)

```sh
.venv/bin/python -m aeris10_gui --demo            # simulator, no hardware
.venv/bin/python -m aeris10_gui                   # hardware mode: pick the STM32 CDC port, press Start
.venv/bin/python -m aeris10_gui --selftest        # hidden window, 3 simulated frames, exit 0 on success
.venv/bin/python -m aeris10_gui --port /dev/cu.usbmodemXXXX
.venv/bin/python -m aeris10_gui --demo --raw-ft601   # option A: raw RTL packets instead of bridge frames
```

  Other options (source: `beta/gui/aeris10_gui/app.py` argparse): `--frames N` (frames for `--selftest`, default 3), `--update-ms` (UI poll interval, default 100), `--log-level`. After `pip install -e .` the same is available as `aeris10-gui [--demo]`. In demo mode the simulator emits per frame one **bridge frame** (`build_frame`, packed exactly like `rd_map_packer.v`) plus a status string in the firmware format, in one CDC byte stream, and "also answers `REG` commands from an in-memory model of `radar_control_regs.v`, so the register panel works without hardware".
- **Check:** `--selftest` exit 0. Executed for this edition on 2026-10-09 (`cd beta/gui && .venv/bin/python -m aeris10_gui --selftest`), output: `selftest: link=bridge frames=31 link_stats={'status': {'status': 31, 'gps_text': 0, 'gpsb': 0, 'reg': 31, 'errors': 0, 'dropped_bytes': 0}, 'bridge': {'frames': 31, 'crc_errors': 0, 'resyncs': 0}} reg_read_all=OK (sent=31, dropped_by_slot=0) -> OK` (the self-test keeps stepping until the register read-all of 31 single-slot commands is answered, hence 31 frames).
- **Figure:** F13.3.
- **⚠ Decision:** hardware mode depends on the firmware CDC path (chapter 12, C4/C5 fixed in the beta, never enumerated on a board) and on the placeholder VID/PID 0x0483:0x5740 (D-09).

![F13.3 — Demo-mode plot area of the beta GUI after 5 simulated bridge frames: left range-Doppler map (dB) with CFAR detections (red circles), right PPI with Kalman tracks (cyan); range/velocity scaling UNVERIFIED (assumptions 4–6 of beta/gui/README.md). Rendered off-screen on 2026-10-09 by driving MainWindow.step() with the Tk root withdrawn and saving the matplotlib Figure (`fig.savefig`, 110 dpi) — only the plot canvas is captured; the Tk control row, notebook tabs and register panel are not in this image because no screen grab was taken — BETA (source: beta/gui/aeris10_gui/ui/main_window.py, sim/simulator.py; produced by a 20-line driver script equivalent to app.py --selftest plus fig.savefig into manual/figures/gui_demo_plots.png)](manual/figures/gui_demo_plots.png)

## 13.5 Tests

### Step 13.3 — Run the test suite [BETA, 76 passed on 2026-10-09]

- **Purpose:** verify parsers, DSP, simulator, register client and UI construction without hardware.
- **Parts & tools:** `.venv/bin/python -m pytest -q` in `beta/gui` (pytest configured with `testpaths = ["tests"]`, `addopts = "-q"` in `pyproject.toml`).
- **Action:** run the command.
- **Check:** executed for this edition: **`76 passed in 3.62s`** (the README text still says 72 and `docs/TESTING/ACCEPTANCE_CRITERIA.md` AC-X3 says 55 — both older counts; the suite grew with the register-command rewrite, `CHANGELOG.md` "Tests"). Coverage as described (source: `beta/gui/README.md`, "Test"): bridge frames (RTL testbench vector `tests/vectors/bridge_frame_from_rtl_tb.hex`, a hardware source fed a synthetic CDC stream interleaving frames, status strings, GPS and REG replies), register commands (codec, RTL register semantics, client ↔ demo register file round trip, firmware single-slot model), settings packet (byte-exact firmware vector, round trip, a model of the firmware receiver proving unpadded framing is accepted and GUI_V5's 64-byte zero padding is rejected), FPGA packet (word- and byte-level vectors from the Verilog, corruption, truncation, resynchronisation), status/GPS/GPSB parsers, CA-CFAR, DBSCAN, Kalman tracker, simulator → parser → assembler exactness, pipeline target recovery, CSV loading, headless Tk smoke tests (skipped if no display).
- **Figure:** —
- **⚠ Decision:** none.

## 13.6 FPGA register panel and ADC calibration

The panel "FPGA registers / ADC calibration" (`ui/register_panel.py`) exposes (source: `beta/gui/CHANGELOG.md`, "Added"): CONTROL bits, CFAR threshold, decimation, start bin; auto (pattern) calibration, pattern-check enable, manual tap + lane load, bitslip + lane, pattern A/B; decoded CAL_STAT lock mask / done / busy / align_fail / fifo_ovf, chosen tap + pass window for all 8 lanes, CAL_ERR, CAL_UNDET, ID; "Read all / refresh". Inputs are range-checked against the RTL field widths. Register map transcribed from the RTL (source: `beta/gui/aeris10_gui/protocol/register_map.py` `REGISTERS`, which cites `beta/fpga/rtl/radar_control_regs.v`; registers are 16 bits wide, 4-bit word addresses as seen by the GUI):

| Addr | Name | Access | Reset | Fields |
|---|---|---|---|---|
| 0x0 | CONTROL | rw | 0b101 | bit0 `use_long_chirp` (1), bit1 `adc_pwdn` (0), bit2 `usb_enable` (1) |
| 0x1 | CFAR_THR | rw | 10000 | `|I|+|Q|` threshold, 16 bit (10000 = original placeholder) |
| 0x2 | DECIM | rw | 0b01 | bits[1:0] range decimation mode (01 = peak) |
| 0x3 | START_BIN | rw | 0 | bits[9:0] first range bin passed to the decimator |
| 0x4 | CAL_CTRL | rw | 0 | bit0 `auto_start` (write 1: start auto calibration, toggle), bit1 `manual_load` (toggle), bit2 `bitslip_load` (toggle), bit3 `check_en` (level: pattern-check error counting) |
| 0x5 | CAL_LANE | rw | 0 | bits[2:0] lane 0..7 for CAL_TAP/CAL_SLIP writes and CAL_LANE_INFO read |
| 0x6 | CAL_TAP | rw | 16 | bits[4:0] manual IDELAY tap 0..31 (78 ps each) |
| 0x7 | CAL_SLIP | rw | 0 | bits[1:0] BITSLIP pulses for a manual bitslip load |
| 0x8 | CAL_PATT | rw | 0x55AA | `{pattern_b[7:0], pattern_a[7:0]}` expected alternating ADC test codes |
| 0x9 | CAL_STAT | ro | 0 | `{fifo_ovf, 4'b0, align_fail, busy, done, lock[7:0]}` |
| 0xA | CAL_LANE_INFO | ro | 0 | `{1'b0, win_hi[4:0], win_lo[4:0], tap[4:0]}` of lane CAL_LANE |
| 0xB | CAL_ERR | ro | 0 | pattern-check error counter (saturating) |
| 0xC | CAL_UNDET | ro | 0 | `{8'b0, undetermined[7:0]}` lanes constant in pattern |
| 0xF | ID | ro | 0xBE7A | beta build identifier |

The RTL additionally defines 0x0D CAL_BLIND_COEF, 0x0E CAL_BLIND_MARGIN and 0x10 CAL_BLIND_MIN for the blind method (source: `beta/fpga/rtl/radar_control_regs.v` address-map comment, lines 31-37); the GUI's 4-bit address map does not include them and the panel "shows it [blind calibration] as unavailable" (source: `beta/gui/CHANGELOG.md`, "Discrepancies" item 2). The calibration procedure using these registers is Step 16.5.

Recorded discrepancies (source: `beta/gui/CHANGELOG.md`, "Discrepancies / unresolved", condensed): (1) `HOST_LINK_DESIGN.md` §7 describes 32-bit registers with a different layout; the beta follows the RTL — run, mixers enable and the NCO word "are not offered because no RTL implements them"; (2) blind calibration not driven by any register in `radar_control_regs.v` (see above); (3) `radar_system_top.v:321-323` ties `reg_we`/`reg_addr`/`reg_wdata` of `ctl_regs` to constants, so "register writes do not reach the register file on the current RTL"; (4) the firmware `REG` implementation exists (chapter 12 §12.7) and the GUI was re-aligned to it line for line; (5) no request ID — the single in-flight command relies on timeout/retransmit.

## 13.7 Assumptions and known limitations

(source: `beta/gui/README.md`, "Assumptions and known limitations", copied in condensed form, numbering kept)

1. **A1 — FT601 byte-lane order** little-endian; the RTL declares a 2-bit `ft601_be` for a 32-bit bus — an RTL defect to resolve at bring-up. Packet length 35 bytes follows from A1.
2. **No CRC in the RTL packet**; integrity uses header, footer and the redundant shifted copies.
3. **No bin indices in the packet**; any lost packet shifts the whole frame until the next resync (option A only).
4. **Range scaling UNVERIFIED**: cell `r` → `r * max_distance / 64` m; the physical spacing of the 64 decimated range bins is not documented anywhere in the repository.
5. **Velocity scaling** uses the standard pulse-Doppler relation with `prf1` and `system_frequency`; not confirmed against the RTL.
6. **Azimuth angle** = `(Azimuth-1) * 360/50` degrees from `main.cpp:188-189`; `BeamPos` is shown as an index.
7. **Settings acknowledgement** does not exist in the protocol.
8. The status string has no terminator; the parser uses `ChirpCount:<n>|` as end marker.
9. Google Maps export dropped.
10. `filterpy` 1.4.5 (2018) on numpy 2.5.3: maintenance risk.
11. Only CPython 3.14.7 (Tk 9.0, then 9.1) on macOS was exercised.
12. **Register map mismatch** between `HOST_LINK_DESIGN.md` §7 and the RTL; the GUI follows the RTL.
13. **REG text protocol** matches the firmware line for line, but neither side has been exercised on hardware.

Behavioural changes versus the originals that matter on the bench (source: `beta/gui/CHANGELOG.md`, "Behavioural changes", condensed): CDC writes are **not** zero-padded by default (checkbox "Zero-pad CDC writes" reproduces the legacy behaviour that the firmware rejects); firmware value limits are enforced in the UI before sending; the STM32 CDC port is opened with pyserial as an OS serial port (no mock devices on enumeration failure); the RTL's real packet format is decoded; GPS text with 3 fields (firmware) or 4 (legacy) is accepted; no background threads — a single Tk timer polls the source (`--selftest` is deterministic).

## 13.8 Packaging

### Step 13.4 — Build the stand-alone bundle [BETA, executed by the beta author]

- **Purpose:** run the host application on a machine without Python.
- **Parts & tools:** `.venv/bin/pip install pyinstaller` (already in `requirements.txt`); `beta/gui/build_app.sh`; `pyinstaller_launcher.py` (because `aeris10_gui/__main__.py` uses a relative import).
- **Action:** `./build_app.sh` — PyInstaller `--onedir` → `dist/aeris10-gui/`, then runs `--demo --selftest`.
- **Check:** result recorded in the source: "PyInstaller 6.22.3 on Python 3.14.7 built a 134 MB `--onedir` bundle and `dist/aeris10-gui/aeris10-gui --demo --selftest` exited 0" (README "Package"); after the register work "135 MB … passes `--demo --selftest` (bridge) and `--demo --selftest --raw-ft601`, both exit 0" (CHANGELOG). Not re-run for this edition.
- **Figure:** —
- **⚠ Decision:** AC-P7 ("Packaged demo runs on a machine without Python") remains NOT RUN — the bundle was only executed on the build machine.

Acceptance criteria touched by this chapter (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`): AC-P1, AC-P2 MET (upstream dependency install/import); AC-P3 NOT MET (`GUI_V1.py` syntax); AC-P4, AC-P7 NOT RUN; AC-P5 "A unit-test suite exists and passes" is recorded NOT MET against the upstream tree and **MET (BETA)** as AC-X3 for `beta/gui` (count now 76); AC-P6 (hardware end-to-end) NOT RUN.
