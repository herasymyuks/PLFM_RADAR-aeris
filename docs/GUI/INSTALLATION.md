# Python GUI — Installation and Validation

Applies to `9_Firmware/9_3_GUI/`. Generated files: `requirements.txt`, `pyproject.toml` (same directory). Tested environment: CPython 3.14.7 + Tk 9.0, macOS arm64, 2026-10-08. Steps marked *executed* were run during this reconstruction; the others are documented procedures.

### GUI-T01 — Create the virtual environment (executed)

- **Purpose:** isolated, reproducible interpreter.
- **Prerequisites:** Python ≥ 3.10 with Tk (`python3 -c "import tkinter; print(tkinter.TkVersion)"` must print a version). macOS: `brew install python@3.12` or python.org installer; Debian/Ubuntu: `apt install python3 python3-venv python3-tk libusb-1.0-0`; Windows: python.org installer (Tk included).
- **Procedure:**
  ```
  cd 9_Firmware/9_3_GUI
  python3 -m venv .venv
  source .venv/bin/activate          # Windows: .venv\Scripts\activate
  python -m pip install --upgrade pip
  ```
- **Verification:** `python -c "import sys; print(sys.prefix)"` points into `.venv`.

### GUI-T02 — Install dependencies (executed in a scratch venv)

- **Procedure:** `pip install -r requirements.txt` (pins are lower bounds; the versions listed as "tested" in the file are known-good).
- **System libraries:** `pyusb` needs libusb-1.0 (`brew install libusb` / `apt install libusb-1.0-0`). `pyftdi` needs the FTDI device to be free of the kernel driver (macOS: no action; Linux: udev rule; Windows: Zadig/WinUSB).
- **Expected output:** `pip check` prints "No broken requirements found".
- **Troubleshooting:** `filterpy` is unmaintained; if it fails on a future numpy, pin `numpy<3`. `tkinterweb` is only needed for `GUI_V5_Demo.py`, which is not runnable anyway — skip it with `pip install -r requirements.txt --no-deps` is **not** recommended; instead delete the line.

### GUI-T03 — Import checks (executed)

- **Procedure:** from the repository root: `python3 tools/check_python_imports.py --dir 9_Firmware/9_3_GUI --try-import` (inside the venv).
- **Expected output:** every third-party module `OK`; `GUI_V1.py` reported as `SYNTAX ERROR` (known fragment).
- **Completion criteria:** exit code 1 only because of `GUI_V1.py`; all imports OK. To get exit 0, pass `--dir` paths that exclude V1 or remove/relocate the fragment (repository decision).

### GUI-T04 — Offline / demo mode

- **Only runnable demo:** `GUI_V6_Demo.py` (self-contained `SimulatedRadarProcessor`, `GUI_V6_Demo.py:61-231`; needs numpy, matplotlib, tkinter).
- **Procedure:** `python GUI_V6_Demo.py` → window "Radar Demo"; press *Start*; targets drift in the PPI; *Record* writes `.npz`; *Save config* writes JSON.
- **CSV replay:** `python GUI_V4_2_CSV.py` → *Load CSV* → select `test_radar_data.csv`. Known defects: derived columns are computed before the file is read (`:354-368`, works on the second load) and the error-path lambda references an unbound variable (`:430`).
- **Not runnable:** `GUI_V5_Demo.py` (missing methods, `AttributeError` at `:955`), `GUI_V6.py` (stub classes), `GUI_V1.py`.
- **Status:** the window launch was **not executed** during this reconstruction (static + module-import verification only).

### GUI-T05 — GUI startup smoke test (procedure; not executed)

```
cd 9_Firmware/9_3_GUI && source .venv/bin/activate
python - <<'EOF'
import importlib, tkinter
for m in ("GUI_V6_Demo", "GUI_V4_2_CSV", "GUI_V5"):
    importlib.import_module(m); print("import OK", m)
root = tkinter.Tk(); root.after(1500, root.destroy); root.mainloop(); print("Tk OK")
EOF
```
Then launch `GUI_V6_Demo.py` and confirm the window appears within 5 s and closes cleanly (exit code 0). On a headless CI runner use `xvfb-run -a python GUI_V6_Demo.py` with a watchdog that sends `root.destroy()` after N seconds (requires a small wrapper; not provided).

### GUI-T06 — Hardware-dependent features (do not expect to work without the fixes in `docs/STM32` and `docs/FPGA`)

| Feature | File / lines | Hardware required | Known blocker |
|---|---|---|---|
| STM32 settings upload | `GUI_V5.py:403-469` | STM32 CDC on USB-FS | firmware RX path dead (STM32 C4); start-flag padding (C5) |
| GPS display | `GUI_V5.py:684-751` | STM32 | `GPS_Init` never called (C6); text format mismatch |
| Radar data stream | `GUI_V5.py:755-797` (FT2232H) / `GUI_V6.py:94-363` (FT601) | FTDI bridge | neither chip is wired on the Main Board; RTL packet format differs |
| Map | V4+ | Google Maps API key | placeholder key |

### GUI-T07 — Packaging for distribution (procedure; not executed)

- **Wheel:** `cd 9_Firmware/9_3_GUI && pip install build && python -m build` → `dist/aeris10_gui-0.6.0-py3-none-any.whl`; `pip install dist/*.whl` provides `aeris10-gui` (→ `GUI_V6:main`, non-functional until V6 is completed) and `aeris10-gui-demo` (→ `GUI_V6_Demo:main`).
- **Stand-alone binary:** `pip install pyinstaller && pyinstaller --onefile --windowed --name aeris10-demo GUI_V6_Demo.py` → `dist/aeris10-demo(.exe/.app)`. Add `--hidden-import matplotlib.backends.backend_tkagg` if the backend is missing at runtime. For the hardware GUIs add `--collect-all pyftdi --collect-all usb`.
- **Acceptance:** the packaged demo starts on a machine without Python installed and shows moving targets; size and start-up time recorded.

### GUI-T08 — Recommended clean-up (repository decisions, not performed)

1. Move `GUI_V1.py`, `GUI_V5_Demo.py`, `GUI_V6.py` to an `archive/` folder or complete them; the `pyproject.toml` `py-modules` list must then be updated.
2. Replace bare `except: pass` blocks (`.planning/codebase/CONCERNS.md`).
3. Decide the host interface (STM32 CDC-ACM via `pyserial` is the only path with hardware) and remove the FTDI code paths or wire an FTDI chip.
