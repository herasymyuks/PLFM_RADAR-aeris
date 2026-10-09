#!/usr/bin/env python3
"""
check_python_imports.py — Python dependency extractor and import checker for AERIS-10.

Parses every *.py file with `ast` (no execution), lists imported top-level modules,
classifies them as stdlib / third-party / local, maps third-party modules to PyPI
distribution names, and (optionally, --try-import) tries importing each third-party
module in the *current* interpreter to report what is missing.

Non-destructive, read-only.
Usage:
    python3 tools/check_python_imports.py [--root PATH] [--dir 9_Firmware/9_3_GUI] [--try-import] [--json]
Exit codes:
    0  all files parse, and (with --try-import) all third-party modules import
    1  syntax error in a file, or (with --try-import) a module failed to import
    2  directory not found
Dependencies: Python 3.10+ standard library only (uses sys.stdlib_module_names).
"""
import argparse
import ast
import importlib
import json
import sys
from pathlib import Path

PYPI_NAME = {
    "serial": "pyserial", "PyQt5": "PyQt5", "PyQt6": "PyQt6", "PySide6": "PySide6", "pyqtgraph": "pyqtgraph",
    "numpy": "numpy", "scipy": "scipy", "matplotlib": "matplotlib", "pandas": "pandas", "folium": "folium",
    "cv2": "opencv-python", "PIL": "Pillow", "sklearn": "scikit-learn", "usb": "pyusb", "ftd3xx": "ftd3xx",
    "pyftdi": "pyftdi", "tkintermapview": "tkintermapview", "customtkinter": "customtkinter",
    "geopy": "geopy", "requests": "requests", "pyproj": "pyproj", "filterpy": "filterpy", "yaml": "PyYAML",
    "skimage": "scikit-image", "plotly": "plotly", "dash": "dash", "CSXCAD": "openEMS (CSXCAD python)",
    "openEMS": "openEMS", "h5py": "h5py", "pyvista": "pyvista", "vtk": "vtk", "shapely": "shapely",
    "simplekml": "simplekml", "pygame": "pygame", "ttkbootstrap": "ttkbootstrap", "utm": "utm",
    "psutil": "psutil", "pykalman": "pykalman",
}


def top_modules(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name.split(".")[0], node.lineno
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.module.split(".")[0], node.lineno


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--dir", action="append", help="sub-directory to scan (repeatable); default: GUI + 8_Utils/Python + 01_physics/figures + 5_Simulations")
    ap.add_argument("--try-import", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    dirs = args.dir or ["9_Firmware/9_3_GUI", "8_Utils/Python", "01_physics/figures", "5_Simulations"]
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    files, result, rc = [], {}, 0
    for d in dirs:
        p = root / d
        if not p.exists():
            print(f"ERROR: directory not found: {p}", file=sys.stderr)
            return 2
        files += sorted(p.rglob("*.py"))
    local_names = {f.stem for f in files}
    third_party = {}
    for f in files:
        rel = f.relative_to(root).as_posix()
        try:
            tree = ast.parse(f.read_text(errors="ignore"), filename=rel)
        except SyntaxError as e:
            result[rel] = {"syntax_error": f"{e.msg} (line {e.lineno})"}
            rc = 1
            continue
        mods = {}
        for m, ln in top_modules(tree):
            cls = "stdlib" if m in stdlib else "local" if m in local_names else "third-party"
            mods[m] = {"class": cls, "line": ln, "pypi": PYPI_NAME.get(m, m) if cls == "third-party" else ""}
            if cls == "third-party":
                third_party.setdefault(m, set()).add(rel)
        has_main = any(isinstance(n, ast.If) and getattr(getattr(n.test, "left", None), "id", "") == "__name__" for n in tree.body)
        result[rel] = {"imports": mods, "has_main_guard": has_main}
    import_status = {}
    if args.try_import:
        for m in sorted(third_party):
            try:
                importlib.import_module(m)
                import_status[m] = "OK"
            except Exception as e:  # noqa: BLE001
                import_status[m] = f"FAIL: {type(e).__name__}: {e}"
                rc = 1
    if args.json:
        print(json.dumps({"files": result, "third_party": {k: sorted(v) for k, v in third_party.items()},
                          "import_status": import_status, "python": sys.version}, indent=2))
    else:
        print(f"python {sys.version.split()[0]}; scanned {len(files)} files")
        for rel, info in result.items():
            if "syntax_error" in info:
                print(f"SYNTAX ERROR {rel}: {info['syntax_error']}")
        print("\nThird-party modules (module -> PyPI distribution) and users:")
        for m in sorted(third_party):
            print(f"  {m:18s} -> {PYPI_NAME.get(m, m + ' (UNVERIFIED mapping)'):28s} used by {len(third_party[m])} file(s)")
        if args.try_import:
            print("\nImport test in current interpreter:")
            for m, st in import_status.items():
                print(f"  {m:18s} {st}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
