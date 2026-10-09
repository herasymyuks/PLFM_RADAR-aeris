#!/usr/bin/env bash
# Build a stand-alone (--onedir) bundle of the AERIS-10 GUI beta with PyInstaller
# and verify that it starts with `--demo --selftest`.
# Usage: ./build_app.sh            (uses ./.venv created per README)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-.venv/bin/python}
if [ ! -x "$PY" ]; then
  echo "error: $PY not found. Create the venv first (see README.md)." >&2; exit 2
fi
"$PY" -c "import PyInstaller" 2>/dev/null || { echo "error: PyInstaller not installed in $PY" >&2; exit 2; }
rm -rf build dist
"$PY" -m PyInstaller --noconfirm --clean --onedir --name aeris10-gui \
  --hidden-import matplotlib.backends.backend_tkagg \
  --collect-submodules sklearn \
  --collect-data matplotlib \
  --exclude-module tkinterweb --exclude-module pandas --exclude-module pyftdi \
  --paths . pyinstaller_launcher.py
BIN=dist/aeris10-gui/aeris10-gui
[ -x "$BIN" ] || BIN=dist/aeris10-gui/aeris10-gui.exe
echo "--- verifying $BIN --demo --selftest"
"$BIN" --demo --selftest --frames 3
echo "--- build OK: $(du -sh dist/aeris10-gui | cut -f1) in dist/aeris10-gui"
