# beta/gui CHANGELOG

## 0.7.0b1 -- 2026-10-09 -- initial BETA reconstruction

Environment: CPython 3.14.7, Tk 9.0, macOS arm64; venv `beta/gui/.venv` (not committed).
Originals in `9_Firmware/9_3_GUI/` were read only; nothing there was modified.

### Provenance -- what was taken from which original

| Beta file | Taken from | What |
|---|---|---|
| `aeris10_gui/model.py` | `GUI_V5.py:56-88` | `RadarTarget`, `RadarSettings`, `GPSData` dataclasses (field names kept; `range`->`range_m`, `velocity`->`velocity_mps`, etc. to carry units) |
| `aeris10_gui/protocol/settings_packet.py` | `GUI_V5.py:454-467` (`_create_settings_packet`), `GUI_V5.py:401-405` (start flag), firmware `RadarSettings.cpp`, `USBHandler.cpp` | packet builder; parser and validation written from the firmware |
| `aeris10_gui/protocol/status_text.py` | `GUI_V5.py:676-751` (`parse_gps_data`, `_parse_binary_gps_with_pitch`), firmware `main.cpp:807-877`, `gps_handler.cpp:45-119` | GPS text/GPSB parsers; status-string parser/formatter written from the firmware |
| `aeris10_gui/protocol/fpga_packet.py` | `9_Firmware/9_2_FPGA/usb_data_interface.v`, `radar_system_top.v`, `doppler_processor.v` | written from the RTL; nothing from `GUI_V5.RadarPacketParser` (wrong format) was reused |
| `aeris10_gui/io/usb_cdc.py` | `GUI_V5.py:307-477` (`STM32USBInterface`: VID/PID list :323-330, open/read/write shape) | re-implemented on pyserial; pyusb fallback kept |
| `aeris10_gui/io/ftdi_ft601.py` | `GUI_V5.py:479-549` (`FTDIInterface` shape), `GUI_V6.py:119-122` (FT601 PIDs) | stub raising `NotImplementedError` |
| `aeris10_gui/dsp/clustering.py` | `GUI_V5.py:587-605` (`RadarProcessor.clustering`) | DBSCAN eps/min_samples defaults kept |
| `aeris10_gui/dsp/tracking.py` | `GUI_V5.py:607-670` (`association`, `tracking`) | Kalman matrices, gate 500, 5 s stale timeout kept |
| `aeris10_gui/dsp/cfar.py` | -- | new (no original contained CFAR) |
| `aeris10_gui/sim/simulator.py` | `GUI_V6_Demo.py:61-231` (`SimulatedRadarProcessor`: target list :71-129, drift/bounds :131-169, noise/clutter/blob/gain :171-214) | refactored to I/Q + RTL packets |
| `aeris10_gui/sim/replay.py` | `GUI_V4_2_CSV.py:354-372` (CSV columns) | csv module instead of pandas |
| `aeris10_gui/ui/theme.py` | `GUI_V5.py:44-55`, `:911-990` | colours and ttk style |
| `aeris10_gui/ui/main_window.py` | `GUI_V5.py:993-1157` (control row, notebook, imshow range-Doppler, targets Treeview, settings tab fields :1128-1157), `GUI_V6_Demo.py:718-748` (timer loop) | |
| `aeris10_gui/ui/sources.py` | `GUI_V5.py:1201-1263` (`start_radar`/`stop_radar` sequence: open, start flag, settings) | |
| `aeris10_gui/processing.py` | -- | new |
| `aeris10_gui/app.py`, `__main__.py` | `GUI_V5.py:1531-1539`, `GUI_V6_Demo.py:1196-1219` (`main()`) | argparse added |

### Behavioural changes versus the originals

1. **CDC write framing**: `GUI_V5._send_data` zero-padded every write to 64 bytes
   (`GUI_V5.py:444-446`). The firmware copies those zeros into its settings buffer so
   `SET` is not at offset 0 and the settings are never accepted (`USBHandler.cpp:51-52,70`).
   Beta default: **no padding**. `pad_to_64=True` (UI checkbox "Zero-pad CDC writes")
   reproduces the legacy behaviour. `tests/test_settings_packet.py` models the firmware
   receiver and shows both outcomes.
2. **Firmware value limits enforced in the UI** before sending (`RadarSettings.cpp:86-101`);
   V5 sent anything parseable as float.
3. **Transport**: STM32 CDC opened as an OS serial port (pyserial) instead of pyusb bulk
   endpoints on interface (0,0); pyusb fallback now selects the CDC *data* interface.
   `pyserial` added to requirements. No mock devices are returned on enumeration failure
   (V5 returned fake devices, `GUI_V5.py:355,502`).
4. **FPGA packet format**: V2-V5 expected `A5 C3` + type + length + payload + CRC16; V6 a
   constant 64-byte packet. Beta decodes the RTL's actual 35-byte `0xAA ... 0x55`
   format, with footer + redundant-copy integrity checks (the RTL has no CRC) and
   stream resynchronisation. The V5 buffer-advance bug (`GUI_V5.py:1313`, packet length
   always 6) is moot.
5. **GPS text**: V3-V5 required 4 fields (`GUI_V5.py:686`); firmware sends 3
   (`gps_handler.cpp:53`). Beta accepts 3 (firmware) or 4 (legacy).
6. **Status string**: new parser for `getSystemStatusForGUI` output (no GUI version
   parsed it); BeamPos/Azimuth drive the PPI azimuth.
7. **CFAR**: implemented on the host (CA-CFAR). V5 only logged the FPGA detection flag;
   V6_Demo drew "detections" from the truth list with `random() < snr/35`.
8. **Clustering/tracking** are now in the processing path; in V5 they were defined but
   never called (`engineering/SOFTWARE_DIAGRAMS/PYTHON/python_gui_architecture.dot`).
9. **Threads removed**: V5 used two daemon threads + a Tk timer; beta polls the source
   from a single Tk timer (`GUI_V6_Demo` style), making `--selftest` deterministic.
10. **Simulator geometry**: 64 x 32 complex I/Q cells (RTL parameters) instead of V6's
    1024 x 32 power map; velocities scaled x0.75 and demo `prf1` = 10 kHz so the V6
    scene fits the unambiguous Doppler span; detection bit per cell = `|I|+|Q| > 10000`
    (`radar_system_top.v:318`).
11. **Dropped**: Google Maps HTML export (placeholder API key), FT2232H/pyftdi path,
    Mercury-colour A-scope/spectrum tabs of V6_Demo (not reconstructed in this beta).
12. **Added**: PPI polar plot, STM32 status tab, `--demo`, `--selftest`, `--port`,
    pytest suite, PyInstaller build script.

### Verification performed

* `pytest -q`: 46 passed (see README "Test").
* `python -m aeris10_gui --selftest --frames 3`: OK (3 frames, 6144 packets, 0 resync drops, 3 status strings).
* `./build_app.sh`: PyInstaller 6.22.3 `--onedir` bundle built; `dist/aeris10-gui/aeris10-gui --demo --selftest` exit 0.
* Not performed: any hardware test; Windows/Linux; Python < 3.14.

## 2026-10-09 — host-link option B (DSN-LINK-01)
- Added `aeris10_gui/protocol/bridge_frame.py`: parser/serialiser for the FPGA→STM32→CDC range-Doppler frame (sync A5 5A, 16-byte header, 2048 × uint8 log-magnitude, detection list, CRC-16/CCITT-FALSE) and `BridgeStreamParser` (resync, status-text pass-through). Reference vector `tests/vectors/bridge_frame_from_rtl_tb.hex` is dumped by the Verilog testbench `engineering/DESIGN/HOST_LINK/rtl/tb_host_bridge.v`. Tests: `tests/test_bridge_frame.py` (9). Not yet wired into `ui/sources.py` (the hardware source still expects the raw RTL packet stream).

## 2026-10-09 — bridge link as default hardware path, register access (DSN-LINK-01 §5, §7)

### Added
- `ui/sources.py` rewritten around `LinkDecoder`: **default link = `bridge`** (option B). The CDC byte stream goes through `BridgeStreamParser`; frames → `RadarPipeline.process_bridge_frame`, non-frame bytes → `StatusStreamParser` (status strings, GPS text/GPSB, REG replies). The raw-RTL-packet path (option A) is kept behind `--raw-ft601` (`LINK_RAW_FT601`). Sources return a `PollResult`; `HardwareSource` accepts an injected CDC object (used by tests).
- `processing.py`: `process_bridge_frame`, `process_power`, `bridge_frame_to_power` (uint8 `8·log2(|I|+|Q|)` → power proxy `2**(u8/4)`, detection list → map). Azimuth/elevation come from the frame header in bridge mode.
- `sim/simulator.py`: `logmag()` (bit-exact copy of `rd_map_packer.v` `logmag`, checked against the testbench formula), `bridge_frame_from_iq()`, `RadarSimulator.next_bridge_frame()` and the `bridge_frames(count)` generator (serialised with `build_frame`). Detection list = first 32 cells with `|I|+|Q| > CFAR_THR`, range-major, as the packer does.
- `sim/register_file.py`: `DemoRegisterFile`, in-memory model of `radar_control_regs.v` (write/read arms, toggle bits, RO registers, reset values) with a simulated calibration result (auto start → lock 0xFF, window [10, 22], tap 16). Answers `REG` lines in demo mode; CFAR_THR and CONTROL.use_long_chirp feed back into the simulated frames.
- `protocol/register_map.py`: register map transcribed from `beta/fpga/rtl/radar_control_regs.v` (field encode/decode, `describe_cal_stat`).
- `protocol/register_cmd.py`: `REG W <addr> <value>` / `REG R <addr>` formatter and device-side parser; reply parser for `REG <addr> <value>` / `REG ERR`; `RegisterClient` (FIFO of outstanding requests, per-lane CAL_LANE_INFO read-all that restores CAL_LANE).
- `protocol/status_text.py`: `StatusStreamParser` now recognises `REG` lines at a line start and yields `RegisterReply`.
- `io/usb_cdc.py`: `send_register_write` / `send_register_read` on `CdcSerialPort` and `PyUsbCdc` (same connection as the settings packet).
- `ui/register_panel.py`: notebook tab "FPGA registers / ADC calibration": CONTROL bits, CFAR threshold, decimation, start bin; auto (pattern) calibration, pattern-check enable, manual tap + lane load, bitslip + lane, pattern A/B; decoded CAL_STAT lock mask/done/busy/align_fail/fifo_ovf, chosen tap + pass window for all 8 lanes, CAL_ERR, CAL_UNDET, ID; "Read all / refresh". Inputs are range-checked against the RTL field widths.
- `app.py`: `--raw-ft601`; `--selftest` now also performs a register read-all against the demo register file and fails if any reply is missing, any `REG ERR` occurs, or any parser error is counted.
- Tests: `tests/test_register_cmd.py` (7), `tests/test_bridge_source.py` (7), 2 new UI smoke tests (raw-FT601 demo, register panel), 1 new bridge-parser regression test. Total 72.

### Changed
- `protocol/bridge_frame.py` `BridgeStreamParser.feed`: when no sync word is buffered it used to hold back the last byte unconditionally. That delayed a text line's closing `\n` (e.g. a trailing `REG` reply) until the next CDC chunk arrived. It now holds the byte back only when it is `0xA5`, i.e. a possible first sync byte. Regression test added.
- Demo detection threshold: taken from the simulated CFAR_THR register (reset 10000, same as before) instead of a constant.

### Discrepancies / unresolved (recorded, not papered over)
1. ~~HOST_LINK_DESIGN.md §7 register table ≠ RTL.~~ **Resolved**: §7 was rewritten to mirror `radar_control_regs.v` (run / mixers / NCO removed). The GUI follows the RTL (see the final-map entry below).
2. ~~Blind calibration not reachable through registers.~~ **Resolved**: CAL_CTRL bit4 + 0x0D/0x0E/0x10 (see below).
3. ~~`radar_system_top.v` ties the register write port off.~~ The register port is now driven by `host_bridge_spi` (RTL header of `radar_control_regs.v`); see the final-map entry for the GUI-side check.
4. ~~No firmware implements the REG text commands.~~ **Resolved the same day**: `beta/stm32/Core/Src/host_bridge_proto.c` (`hb_cmd_parse`/`hb_cmd_execute`), `LIB/USBHandler.cpp` (`captureTextCommand` single slot) and `main.cpp` (main-loop reply) now implement them. `protocol/register_cmd.py` was re-aligned to the firmware (see the entry below); the GUI's line rules are now "same as firmware", not a proposal.
5. There is no request ID in the protocol; replies are matched to the single in-flight command. A lost reply is handled by the client's timeout/retransmit, not by sequence numbers.

### Verification performed
- `pytest -q`: **72 passed**, 0 skipped.
- `python -m aeris10_gui --selftest`: bridge link: 3 frames, 0 CRC errors, 31 REG replies, read-all OK. `--selftest --raw-ft601`: 6144 packets, 0 drops, read-all OK.
- `./build_app.sh`: PyInstaller 6.22.3 rebuild OK (135 MB `--onedir`). The bundle passes `--demo --selftest` (bridge) and `--demo --selftest --raw-ft601`, both exit 0.
- Environment note: Homebrew had upgraded `tcl-tk` to 9.1, which broke `_tkinter` (`libtcl9.0.dylib` not found) and silently skipped the UI tests. Fixed with `brew reinstall python-tk@3.14` (Tk 9.1 now loads).

## 2026-10-09 (later) — REG commands aligned with the firmware implementation

Firmware read: `beta/stm32/Core/Src/host_bridge_proto.c`, `beta/stm32/Core/Src/host_bridge.c`
(`HostBridge_ExecuteTextCommand`), `beta/stm32/LIB/USBHandler.cpp` (`captureTextCommand`,
`takePendingCommand`), `beta/stm32/Core/Src/main.cpp:1713-1726`.

### Changed (`protocol/register_cmd.py`)
- Replies parsed/formatted exactly as the firmware prints them: `REG 0x%04X 0x%08X\r\n`
  and `REG ERR\r\n`. A **write reply echoes the written value** (`hb_cmd_execute` echoes
  `c.value`); the earlier GUI proposal (read-back) is gone. `DemoRegisterFile` does the same.
- Device-side parser (`parse_command`, used by the demo register file) mirrors `hb_cmd_parse`
  / `parse_u32`: `REG` upper case at byte 0 of the transfer, `W`/`R` either case, `0x`/`0X`
  hex with at most 8 digits or decimal, address <= 0xFFFF, trailing junk is an error, the line
  is cut at the first `\0`/`\r`/`\n` (**one command per USB transfer**; later lines are
  discarded). New `is_text_command()` = `hb_cmd_is_text_command`.
- `RegisterClient` now enforces the **firmware single slot**: exactly one command in flight;
  the next queued command is written only after the reply (or after `timeout` s, with
  `retries` retransmits, then recorded as `("…", "timeout")` in `errors`). `pending` still
  lists everything unanswered; new `in_flight`, `sent`, `retransmits`, `poll(now)`.
- New `parse_bridge_status()` / `BridgeStatus` for the SPI command 0x04 payload (four
  little-endian u16: status bits frame-ready / ADAR CS conflict / FIFO overflow /
  calibration lock, version, frames, reserved). No text form exists in the firmware yet.
- `ui/sources.py` `DemoSource` emulates the firmware slot: a `REG` transfer is captured,
  executed at the next poll (main loop), and a second transfer before that is dropped
  (`dropped_commands` counter). `--selftest` now steps until the read-all is fully answered
  and prints `sent` / `dropped_by_slot`.
- `ui/main_window.py` calls `reg_client.poll()` every tick (timeouts); panel shows sent /
  retransmits / timeouts.

### Tests
- `tests/test_register_cmd.py` rewritten (11): firmware-literal reply strings incl. `\r\n`
  and upper-case zero-padded hex, device-parser rules (`REG R 0x1\nREG R 0x2\n` executes only
  the first), a `FakeFirmware` with the single slot proving the client never triggers a drop
  (one command per main-loop iteration, 44 commands for write + read + read-all), the
  counter-example (unpaced sender loses the second command), timeout → 2 retransmits →
  error → next command, status bytes.
- `tests/test_bridge_source.py`: demo source slot semantics (second transfer dropped, replies
  arrive one per poll, write echoes the value). `tests/test_ui_smoke.py`: register panel
  loops `step()` until the read-all is answered; asserts 0 drops, `sent == polls`.

## 2026-10-09 (final register map, RTL 0x0002)

`beta/fpga/rtl/radar_control_regs.v` and HOST_LINK_DESIGN.md §7 are now identical; the GUI was
updated to that map.

### Changed
- `protocol/register_map.py`: 5-bit addresses (`ADDR_MASK = 0x1F`, unmapped 0x11..0x1F); CAL_CTRL
  bit4 `blind` (level: 0 = ADC test pattern, 1 = CW tone at the IF); new registers 0x0D
  `CAL_BLIND_COEF` (rw, signed Q1.14, reset 0xEC39), 0x0E `CAL_BLIND_MARGIN` (rw, reset 0x0040),
  0x10 `CAL_BLIND_MIN` (ro, per CAL_LANE); `RTL_VERSION = 0x0002`; helpers `blind_coef_to_cos`,
  `blind_coef_from_if` (120 MHz @ 400 MSPS -> 0xEC39, matches the RTL default). The discrepancy
  docstring is gone.
- `protocol/register_cmd.py`: `BridgeStatus.packer_overflow` (status word bit4); `RegisterClient.
  read_all` also reads CAL_BLIND_MIN for every lane (`lane_blind_min`), 3 commands per lane.
- `sim/register_file.py`: 5-bit decode, bit4 blind level, 0x0D/0x0E rw, 0x10 ro; blind auto
  calibration yields a per-lane minimum metric (0x0120 at the default coefficient) and a window
  that narrows as the coefficient is detuned from the default IF.
- `ui/register_panel.py`: the "unavailable" note is replaced by a plain map note; new blind-method
  checkbox (bit4), blind coef / margin fields with Write buttons, "IF -> coef" helper, per-lane
  `blind_min` readout and a method/coef/margin summary line. `auto_pattern`/`write_check` renamed
  `auto_start`/`write_cal_ctrl` (old names kept as aliases).
- Tests updated: map resets/fields/unmapped range, status bit4, register-file blind behaviour,
  read-all now 3 commands per lane (client pacing test: 52 commands, 0 drops), UI panel exercises
  compute-coef -> write -> blind auto calibration -> read-all.
