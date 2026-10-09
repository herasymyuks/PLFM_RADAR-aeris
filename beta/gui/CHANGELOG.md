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
