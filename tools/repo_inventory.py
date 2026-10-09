#!/usr/bin/env python3
"""
repo_inventory.py — AERIS-10 repository inventory generator.

Walks the repository, classifies every file by type and subsystem, and prints
a Markdown or CSV table.  Non-destructive: never writes inside the repository
unless --out is given explicitly.

Usage:
    python3 tools/repo_inventory.py [--root PATH] [--format md|csv] [--out FILE]

Exit codes:
    0  success
    2  root directory not found
Dependencies: Python 3.8+ standard library only.
"""
import argparse
import csv
import os
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}

TYPE_MAP = {
    ".v": "Verilog RTL", ".sv": "SystemVerilog", ".xdc": "Vivado constraints",
    ".mem": "Memory init (hex)", ".c": "C source", ".h": "C/C++ header",
    ".cpp": "C++ source", ".hpp": "C++ header", ".py": "Python",
    ".sch": "Schematic (EAGLE/Qucs)", ".brd": "EAGLE board", ".kicad_pcb": "KiCad PCB",
    ".kicad_sch": "KiCad schematic", ".kicad_pro": "KiCad project", ".kicad_prl": "KiCad local prefs",
    ".dat": "Simulation data (Qucs)", ".dpl": "Qucs display", ".net": "Netlist",
    ".s2p": "Touchstone 2-port", ".s3p": "Touchstone 3-port", ".m": "MATLAB/Octave",
    ".xml": "XML", ".csv": "CSV data", ".mnt": "EAGLE mount/PnP", ".xlsx": "Excel workbook",
    ".docx": "Word document", ".pdf": "PDF", ".md": "Markdown", ".txt": "Text",
    ".jpg": "Image", ".jpeg": "Image", ".png": "Image", ".gif": "Image", ".svg": "SVG figure",
    ".mp4": "Video", ".dwg": "AutoCAD drawing", ".dxf": "DXF drawing", ".drawio": "draw.io diagram",
    ".gds": "GDSII layout", ".gbr": "Gerber", ".ite": "Qucs/other", ".pcb": "PCB (legacy)",
    ".bak": "Backup", ".zip": "Archive", ".json": "JSON", ".sh": "Shell script", ".ioc": "STM32CubeMX project",
}

SUBSYSTEM_RULES = [
    ("9_Firmware/9_2_FPGA", "FPGA"),
    ("9_Firmware/9_1_Microcontroller", "STM32 firmware"),
    ("9_Firmware/9_3_GUI", "Python GUI"),
    ("4_Schematics and Boards Layout/4_6_Schematics/MainBoard", "PCB: Main Board"),
    ("4_Schematics and Boards Layout/4_6_Schematics/PowerBoard", "PCB: Power Supply"),
    ("4_Schematics and Boards Layout/4_6_Schematics/PowerAmplifierBoard", "PCB: RF PA"),
    ("4_Schematics and Boards Layout/4_6_Schematics/FrequencySynthesizerBoard", "PCB: Frequency Synthesizer"),
    ("4_Schematics and Boards Layout/4_7_Production Files", "PCB: Production files"),
    ("4_Schematics and Boards Layout", "PCB"),
    ("5_Simulations", "Simulation"),
    ("7_Components Datasheets", "Datasheets"),
    ("6_Application Notes", "Datasheets"),
    ("8_Utils/Python", "Utility scripts"),
    ("8_Utils", "Media / utilities"),
    ("3_Power Management", "Power management"),
    ("2_Functional Diagram", "System diagrams"),
    ("1_Project_Description", "Project description"),
    ("00_notation", "Docs: notation"),
    ("01_physics", "Docs: physics"),
    ("02_hardware", "Docs: hardware"),
    ("03_software", "Docs: software"),
    ("04_research", "Docs: research"),
    ("research", "Docs: research"),
    (".planning", "Planning (GSD)"),
    ("docs", "Engineering manual (generated)"),
    ("tools", "Automation"),
]


def classify_subsystem(rel: str) -> str:
    for prefix, name in SUBSYSTEM_RULES:
        if rel.startswith(prefix):
            return name
    return "Root"


def status_for(path: Path, rel: str) -> str:
    """Heuristic status. Only cheap, verifiable checks are performed here."""
    ext = path.suffix.lower()
    size = path.stat().st_size
    if size == 0:
        return "PLACEHOLDER"
    if ext == ".xdc":
        try:
            txt = path.read_text(errors="ignore")
            if "[PIN_NUMBER" in txt or "[BANK_NUMBER]" in txt:
                return "INCOMPLETE"
        except OSError:
            pass
    if ext in (".v", ".sv", ".c", ".cpp", ".h", ".py", ".sch", ".brd"):
        return "REQUIRES VALIDATION"
    if ext in (".md", ".pdf", ".docx", ".xlsx", ".jpg", ".png", ".gif", ".svg", ".mp4"):
        return "COMPLETE"
    return "UNKNOWN"


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            yield p, rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--format", choices=["md", "csv"], default="md")
    ap.add_argument("--out", help="write to file instead of stdout")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2
    rows = []
    for p, rel in walk(root):
        ext = p.suffix.lower()
        rows.append({
            "Path": rel,
            "File type": TYPE_MAP.get(ext, ext or "no extension"),
            "Subsystem": classify_subsystem(rel),
            "Size (bytes)": p.stat().st_size,
            "Status": status_for(p, rel),
        })
    out = open(args.out, "w", newline="") if args.out else sys.stdout
    try:
        if args.format == "csv":
            w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        else:
            out.write(f"| Path | File type | Subsystem | Size (bytes) | Status |\n|---|---|---|---:|---|\n")
            for r in rows:
                out.write(f"| `{r['Path']}` | {r['File type']} | {r['Subsystem']} | {r['Size (bytes)']} | {r['Status']} |\n")
            out.write(f"\nTotal files: {len(rows)}\n")
    finally:
        if args.out:
            out.close()
    print(f"inventory: {len(rows)} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
