# Python GUI Modules - imports and definitions (auto-generated)

Generated 2026-10-09 by `tools/gen_python_module_graph.py` from `9_Firmware/9_3_GUI` (9 files). Python 3.14.7 `ast`; stdlib classification uses `sys.stdlib_module_names` of the running interpreter. Script exit code: 1.

Drawing SD-05, revision A, status SOURCE-DERIVED. Native file: `python_gui_modules.dot`.

| File | Lines | Parse | Classes (line) | Top-level functions (line) | stdlib imports | third-party imports (line; optional?) | local imports |
|---|---:|---|---|---|---|---|---|
| `GUI_V1.py` | 42 | **SYNTAX ERROR** - IndentationError: unexpected indent (line 2) | - | - | - | - | - |
| `GUI_V2.py` | 1060 | OK (has `__main__`) | `RadarTarget` (40), `RadarSettings` (51), `GPSData` (62), `STM32USBInterface` (68), `FTDIInterface` (238), `RadarProcessor` (310), `USBPacketParser` (431), `RadarPacketParser` (499), `RadarGUI` (613) | `main` (1048) | `tkinter` (1,2), `threading` (3), `queue` (4), `time` (5), `struct` (6), `logging` (11), `dataclasses` (12), `typing` (13), `math` (18) | `numpy` (7), `matplotlib` (8,9,10), `scipy` (14), `sklearn` (15), `filterpy` (16), `crcmod` (17), `usb` (21,22; optional), `pyftdi` (29,30; optional) | - |
| `GUI_V3.py` | 1147 | OK (has `__main__`) | `RadarTarget` (40), `RadarSettings` (51), `GPSData` (62), `STM32USBInterface` (69), `FTDIInterface` (239), `RadarProcessor` (311), `USBPacketParser` (432), `RadarPacketParser` (513), `RadarGUI` (627) | `main` (1135) | `tkinter` (1,2), `threading` (3), `queue` (4), `time` (5), `struct` (6), `logging` (11), `dataclasses` (12), `typing` (13), `math` (18) | `numpy` (7), `matplotlib` (8,9,10), `scipy` (14), `sklearn` (15), `filterpy` (16), `crcmod` (17), `usb` (21,22; optional), `pyftdi` (29,30; optional) | - |
| `GUI_V4.py` | 1428 | OK (has `__main__`) | `RadarTarget` (44), `RadarSettings` (57), `GPSData` (70), `MapGenerator` (77), `STM32USBInterface` (295), `FTDIInterface` (467), `RadarProcessor` (539), `USBPacketParser` (660), `RadarPacketParser` (741), `RadarGUI` (855) | `main` (1416) | `tkinter` (1,2), `threading` (3), `queue` (4), `time` (5), `struct` (6), `logging` (12), `dataclasses` (13), `typing` (14), `math` (19), `webbrowser` (20), `tempfile` (21), `os` (22) | `numpy` (7), `matplotlib` (8,9,10,11), `scipy` (15), `sklearn` (16), `filterpy` (17), `crcmod` (18), `usb` (25,26; optional), `pyftdi` (33,34; optional) | - |
| `GUI_V4_2_CSV.py` | 679 | OK (has `__main__`) | `RadarTarget` (23), `SignalProcessor` (32), `RadarGUI` (228) | `main` (667) | `tkinter` (1,2), `logging` (12), `dataclasses` (13), `typing` (14), `threading` (15), `queue` (16), `time` (17) | `pandas` (3), `numpy` (4), `matplotlib` (5,6,7,8), `scipy` (9,10,11) | - |
| `GUI_V5.py` | 1543 | OK (has `__main__`) | `RadarTarget` (56), `RadarSettings` (69), `GPSData` (82), `MapGenerator` (89), `STM32USBInterface` (307), `FTDIInterface` (479), `RadarProcessor` (551), `USBPacketParser` (672), `RadarPacketParser` (753), `RadarGUI` (867) | `main` (1531) | `tkinter` (1,2), `threading` (3), `queue` (4), `time` (5), `struct` (6), `logging` (12), `dataclasses` (13), `typing` (14), `math` (19), `webbrowser` (20), `tempfile` (21), `os` (22) | `numpy` (7), `matplotlib` (8,9,10,11), `scipy` (15), `sklearn` (16), `filterpy` (17), `crcmod` (18), `usb` (25,26; optional), `pyftdi` (33,34; optional) | - |
| `GUI_V5_Demo.py` | 1357 | OK (has `__main__`) | `RadarTarget` (67), `RadarSettings` (80), `GPSData` (93), `RadarProcessor` (100), `USBPacketParser` (221), `RadarPacketParser` (302), `MapGenerator` (416), `STM32USBInterface` (697), `FTDIInterface` (869), `RadarGUI` (941) | `main` (1344) | `tkinter` (1,2), `threading` (3), `queue` (4), `time` (5), `struct` (6), `logging` (12), `dataclasses` (13), `typing` (14), `math` (19), `webbrowser` (20), `tempfile` (21,1326), `os` (22), `random` (23), `json` (24) | `numpy` (7), `matplotlib` (8,9,10,11), `scipy` (15), `sklearn` (16), `filterpy` (17), `crcmod` (18), `tkinterweb` (28; optional), `usb` (36,37; optional), `pyftdi` (44,45; optional) | - |
| `GUI_V6.py` | 618 | OK (has `__main__`) | `RadarTarget` (57), `RadarSettings` (70), `GPSData` (83), `MapGenerator` (90), `FT601Interface` (94), `RadarProcessor` (365), `USBPacketParser` (369), `RadarPacketParser` (373), `RadarGUI` (377) | `main` (605) | `tkinter` (1,2), `threading` (3), `queue` (4), `time` (5), `struct` (6), `logging` (12), `dataclasses` (13), `typing` (14), `math` (19), `webbrowser` (20), `tempfile` (21), `os` (22) | `numpy` (7), `matplotlib` (8,9,10,11), `scipy` (15), `sklearn` (16), `filterpy` (17), `crcmod` (18), `usb` (25,26; optional), `pyftdi` (33,34,35; optional) | - |
| `GUI_V6_Demo.py` | 1222 | OK (has `__main__`) | `RadarTarget` (36), `RadarSettings` (45), `SimulatedRadarProcessor` (61), `RadarDemoGUI` (237) | `main` (1196) | `tkinter` (9,10,972,1007,1038), `threading` (11), `queue` (12), `time` (13), `logging` (18), `dataclasses` (19), `typing` (20), `random` (21), `json` (22), `os` (23), `datetime` (24), `platform` (1073) | `numpy` (14), `matplotlib` (15,16,17) | - |

## Third-party packages

| Import name | PyPI distribution | Used by |
|---|---|---|
| `numpy` | numpy | GUI_V2.py, GUI_V3.py, GUI_V4.py, GUI_V4_2_CSV.py, GUI_V5.py, GUI_V5_Demo.py, GUI_V6.py, GUI_V6_Demo.py |
| `matplotlib` | matplotlib | GUI_V2.py, GUI_V3.py, GUI_V4.py, GUI_V4_2_CSV.py, GUI_V5.py, GUI_V5_Demo.py, GUI_V6.py, GUI_V6_Demo.py |
| `scipy` | scipy | GUI_V2.py, GUI_V3.py, GUI_V4.py, GUI_V4_2_CSV.py, GUI_V5.py, GUI_V5_Demo.py, GUI_V6.py |
| `sklearn` | scikit-learn | GUI_V2.py, GUI_V3.py, GUI_V4.py, GUI_V5.py, GUI_V5_Demo.py, GUI_V6.py |
| `filterpy` | filterpy | GUI_V2.py, GUI_V3.py, GUI_V4.py, GUI_V5.py, GUI_V5_Demo.py, GUI_V6.py |
| `crcmod` | crcmod | GUI_V2.py, GUI_V3.py, GUI_V4.py, GUI_V5.py, GUI_V5_Demo.py, GUI_V6.py |
| `usb` | pyusb | GUI_V2.py (optional), GUI_V3.py (optional), GUI_V4.py (optional), GUI_V5.py (optional), GUI_V5_Demo.py (optional), GUI_V6.py (optional) |
| `pyftdi` | pyftdi | GUI_V2.py (optional), GUI_V3.py (optional), GUI_V4.py (optional), GUI_V5.py (optional), GUI_V5_Demo.py (optional), GUI_V6.py (optional) |
| `pandas` | pandas | GUI_V4_2_CSV.py |
| `tkinterweb` | tkinterweb | GUI_V5_Demo.py (optional) |

## Notes

- `optional` = every import of that package sits inside a `try:` block (the file degrades when the package is absent).
- `local` = import name equals another `.py` file stem in the scanned directory. None were found: the GUI versions are independent monolithic scripts.
- Classification is lexical; whether a third-party module is actually exercised at runtime is not determined here.
