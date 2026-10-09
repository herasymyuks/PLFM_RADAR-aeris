#!/usr/bin/env python3
"""Scan the repository for figures usable in the manual (PNG/SVG/PDF/JPG/DOT/MMD renders) and write
manual/ASSET_INDEX.md: one row per asset with path, type, size, origin (generator/agent), proposed caption
and status (from the drawing register when registered). Usage: python3 tools/gen_manual_asset_index.py
"""
import os, re, datetime as _dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = ["engineering", "docs/MECHANICAL/drawings", "8_Utils", "2_Functional Diagram, Block Diagram & Schematic", "4_Schematics and Boards Layout/4_4_Board Stack-up", "beta/pcb", "5_Simulations"]
EXT = {".png", ".svg", ".pdf", ".jpg", ".jpeg", ".mmd", ".dot"}
SKIP = re.compile(r"/(gerber|drill|kicad|parts|logs|vectors|__pycache__|\.venv|dist|build)/|_segment_|-In\d+_Cu|B_Mask|F_Mask|B_Fab|F_Fab|B_Silkscreen|F_Silkscreen|Edge_Cuts\.svg|drl_map|thermal_map|_F_Cu\.svg|copper_layers")
reg = {}
rp = os.path.join(ROOT, "engineering", "DRAWING_REGISTER.md")
if os.path.isfile(rp):
    for line in open(rp, encoding="utf-8"):
        m = re.match(r"\| ([A-Z0-9\-]+) \| (.+?) \| .+? \| (.+?) \| (.+?) \| (.+?) \|", line)
        if m:
            for f in re.findall(r"`([^`]+)`", m.group(3) + " " + m.group(4)):
                reg[os.path.basename(f)] = (m.group(1), m.group(5).strip())
rows = []
for base in SCAN:
    d = os.path.join(ROOT, base)
    if not os.path.isdir(d):
        continue
    for dp, dn, fn in os.walk(d):
        for f in fn:
            p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
            if os.path.splitext(f)[1].lower() not in EXT or SKIP.search("/" + rel):
                continue
            size = os.path.getsize(p)
            rid, st = reg.get(f, ("—", "source file" if not rel.startswith(("engineering", "docs", "beta")) else "GENERATED (unregistered)"))
            cap = re.sub(r"[_\-]+", " ", os.path.splitext(f)[0])
            rows.append((rel, os.path.splitext(f)[1].lower()[1:], size, rid, st, cap))
rows.sort()
with open(os.path.join(ROOT, "manual", "ASSET_INDEX.md"), "w", encoding="utf-8") as fh:
    fh.write(f"# Manual asset index\n\nGenerated {_dt.date.today().isoformat()} by `tools/gen_manual_asset_index.py` — {len(rows)} candidate figures. Use the register ID/status to caption each figure honestly (SOURCE-DERIVED / PARTIAL / CONCEPTUAL / PROPOSED DESIGN / BETA / original project file). Per-layer PCB plots, drill maps and thermal maps are omitted here but exist under `engineering/PCB/<BOARD>/svg|drawings|drill` and `engineering/DESIGN/CALCS`.\n\n| Path | Type | kB | Register ID | Status | Proposed caption |\n|---|---|---|---|---|---|\n")
    for rel, ext, size, rid, st, cap in rows:
        fh.write(f"| `{rel}` | {ext} | {size//1024} | {rid} | {st} | {cap} |\n")
print(len(rows), "assets indexed")
