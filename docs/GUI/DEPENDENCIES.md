# Python GUI — Dependency Analysis

Status date 2026-10-08. Evidence: `ast`-based import extraction (`tools/check_python_imports.py`), a clean virtual environment on CPython 3.14.7 (macOS arm64, Tk 9.0) in which all packages were installed and import-tested, pyflakes, per-file static reading. The GUIs were **not** launched; no hardware was connected.

## 1. Which file is the application?

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

Conclusion: the only hardware-capable complete GUI is `GUI_V5.py` (FT2232H + STM32 CDC); the only offline-runnable program is `GUI_V6_Demo.py`. `03_software/03_python_gui.md:73` ("RadarGUI Complete") describes `GUI_V6.py` incorrectly.

## 2. Third-party imports → PyPI distributions (all GUI files)

| Import | Distribution | Used by | Tested version (installed, import OK) | Proposed range | Range status |
|---|---|---|---|---|---|
| `numpy` | numpy | all | 2.5.3 | `>=1.24,<3` | UNVERIFIED below 2.5.3 |
| `scipy` | scipy | V2–V5, V4_2_CSV | 1.18.1 | `>=1.10` | UNVERIFIED below |
| `matplotlib` (TkAgg backend) | matplotlib | all | 3.11.2 | `>=3.7` | UNVERIFIED below |
| `sklearn` (DBSCAN) | scikit-learn | V2–V6 | 1.9.1 | `>=1.3` | UNVERIFIED below |
| `filterpy` (KalmanFilter) | filterpy | V2–V6 | 1.4.5 (last release 2018) | `>=1.4.5` | import OK on numpy 2; runtime with numpy 2 UNVERIFIED |
| `crcmod` | crcmod | V2–V6 | 1.7 | `>=1.7` | OK (pure Python fallback) |
| `usb` | pyusb | V2–V6 | 1.3.1 | `>=1.2` | needs `libusb-1.0` system library (`brew install libusb`) |
| `pyftdi` | pyftdi | V2–V6 | 0.57.2 | `>=0.55` | **does not support FT601** (runtime PID table: 6001/6010/6011/6014/6015/6043/6048); V6's FT601 path (`GUI_V6.py:119-122`, PIDs 0x6030/0x6031) cannot work with pyftdi; FT60x needs FTDI D3XX (`ftd3xx` Python binding + vendor driver) |
| `pandas` | pandas | V4_2_CSV, `8_Utils/Python/CSV_radar*.py` | 3.0.6 | `>=2.0` | UNVERIFIED below |
| `tkinterweb` | tkinterweb | V5_Demo only | 4.25.4 | `>=4.0` | V5_Demo is not runnable anyway |
| `tkinter` | stdlib, needs a Tk-enabled Python | all | Tk 9.0 | — | Homebrew Python includes it; python.org installers include it; Debian needs `python3-tk` |
| `pyserial` | — | **not imported by any GUI** (USB CDC is accessed via raw pyusb bulk endpoints, `GUI_V5.py:358-399`) | — | — | listed in `requirements.txt` only as a hint for a CDC-ACM rework |

Utility/simulation scripts additionally need `openEMS`/`CSXCAD` (`5_Simulations/Antenna/*.py`) which are **not on PyPI** (`pip install openEMS` exit 1); they ship with the openEMS binary distribution. `5_Simulations/Fencing/Via_fencing.py` writes to `/mnt/data` (non-existent absolute path). `openems_quartz_slotted_wg_10p5GHz.py:218-227` uses undefined names (`theta`, `phi`, `ports`, `freq`) and cannot complete.

## 3. Python version

No walrus, `match`, or PEP 604 unions; `dataclasses` used (V2+) → language floor 3.7. Tested only on 3.14.7. `pyproject.toml` declares `>=3.10` (oldest CPython still receiving security fixes in 2026); 3.7–3.9 compatibility is UNVERIFIED.

## 4. Hardware / platform dependencies

| Aspect | Finding |
|---|---|
| USB VID/PID | V2–V5: FTDI FT2232H `0x0403:0x6010` (`GUI_V5.py:493`); V6: FT601 `0x0403:0x6030/0x6031`. STM32 CDC: no VID/PID filter — opens bulk endpoints on interface (0,0) (`GUI_V5.py:358-399`), which on Windows (usbser) and macOS (kernel CDC driver) is normally claimed by the OS and is the control, not the data, interface of a CDC-ACM device → **platform-problematic; REQUIRES BENCH VERIFICATION** |
| Schematic reality | the Main Board has no FT2232H and an unconnected FT601; the only USB link is STM32 OTG-FS (`docs/PCB/MAIN_BOARD.md`) — neither FTDI path in any GUI version has hardware |
| Serial ports | no COM/tty names, no baud rates in GUI code |
| Threads | V2–V5: two daemon threads (USB read, processing); V6_Demo: `root.after` only |
| OS-specific code | none besides `platform.platform()` (informational) |
| Network | Google Maps JS API with placeholder key (`GUI_V4.py:229`, `GUI_V5.py:241`, `GUI_V6.py:414`); V5_Demo: unpkg Leaflet + OSM tiles |
| Mock fallback | `list_devices()` returns mock devices on error in every version — a hardware failure is silently masked |

## 5. External data files, configuration, assets

| Reference | Exists | Note |
|---|---|---|
| `test_radar_data.csv` (file-dialog input for V4_2_CSV) | yes (`9_Firmware/9_3_GUI/`, byte-identical copy in `8_Utils/Python/`) | synthetic, generated by `8_Utils/Python/CSV_radar.py`: 16 LONG + 16 SHORT chirps × 512 samples; columns `timestamp_ns,chirp_number,chirp_type,sample_index,I_value,Q_value,magnitude_squared` match the reader |
| icons / images / config JSON | none referenced | V6_Demo writes `.npz`/JSON on user action only |
| `GUI_V6.gif` | yes | README illustration, unreferenced by code |

## 6. Protocol consistency (GUI ↔ firmware ↔ FPGA ↔ `03_software/04_usb_protocol.md`)

| # | Item | Finding |
|---|---|---|
| 1 | Host→STM32 start flag `[23,46,158,237]` | consistent GUI (`GUI_V5.py:403`) ↔ firmware (`USBHandler.cpp:38`); doc omits the bytes |
| 2 | Start-flag padding to 64 bytes (`GUI_V5.py:444-446`) | firmware forwards the 60 zero bytes into the settings buffer (`USBHandler.cpp:51-52`) → `"SET"` check at offset 0 (`:70`) fails → settings never accepted (**static finding, bench-confirm**) |
| 3 | Settings packet `SET` + 3×`>d` + `>I` + 6×`>d` + `END` = 82 B big-endian | consistent GUI ↔ `RadarSettings.cpp:23-113`; doc `04_usb_protocol.md:350` wrongly says little-endian uint32 and omits framing; firmware min-length 74 (`USBHandler.cpp:25`) is lax |
| 4 | STM32→host GPS text `GPS:lat,lon,alt` (3 fields, UART3) | GUI V3+ requires 4 fields on USB (`GUI_V5.py:686`) → never parses; binary `GPSB` 30-byte packet consistent (`gps_handler.cpp:65-119` ↔ `GUI_V5.py:702-751`) but never sent (`GPS_Init` never called) |
| 5 | FPGA→host radar packet | RTL `usb_data_interface.v:39-40,93-160`: `0xAA` + 4×32-bit range + 4×32-bit Doppler + detection byte + `0x55` (no CRC); GUI V2–V5 expect `A5C3` sync + type + len + payload + CRC16-CCITT (`GUI_V5.py:755-797`); V6 parser is a stub with constant 64-byte length. **No GUI version can decode the RTL output** (and the RTL output has no hardware path) |
| 6 | MCU family | doc says STM32F4 (`04_usb_protocol.md:20-21,171`); hardware/firmware are STM32F7 |

## 7. Executed checks

| Check | Command | Result |
|---|---|---|
| Interpreter | `python3 --version` | 3.14.7 |
| venv + install | `python3 -m venv venv && pip install numpy scipy matplotlib pandas scikit-learn filterpy crcmod pyusb pyftdi tkinterweb` | installed (versions in table 2) |
| openEMS | `pip install openEMS` | **FAIL** (not on PyPI) |
| Syntax | `tools/check_python_imports.py` (ast) over 27 files | 26 pass; `GUI_V1.py` SyntaxError |
| Imports | `tools/check_python_imports.py --try-import` in the venv | all 10 GUI modules OK; `CSXCAD`, `openEMS` FAIL |
| Module import of GUI files | `python -c "import GUI_V6_Demo"` etc. | V2, V3, V4, V4_2_CSV, V5, V5_Demo, V6, V6_Demo import; V1 fails (import ≠ run: V5_Demo/V6 fail at construction) |
| GUI launch | not executed | — |
