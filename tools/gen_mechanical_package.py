#!/usr/bin/env python3
"""Build engineering/MECHANICAL/ from verified PCB geometry.

For every board it extracts from the EAGLE .brd XML: the board outline (layer 20
Dimension), all non-plated holes (<hole> in the drawing and in packages) and
mounting pads (plated pads with drill >= 2.0 mm) with their positions, and writes
  engineering/MECHANICAL/dimensions/<BOARD>_dimensions.md   (outline, hole table, pitch, mass ESTIMATE)
  engineering/MECHANICAL/DXF/<BOARD>_outline_holes_eagle.dxf (DXF R12, stdlib writer, mm)
  engineering/MECHANICAL/CAD/pcb_set_plan_view.svg           (all boards at scale 1:1, plan view)
  engineering/MECHANICAL/dimensions/README.md
and copies the KiCad-generated STEP / DXF / outline PDF from engineering/PCB/<BOARD>/ into
engineering/MECHANICAL/{STEP,DXF,PDF}/.

Nothing is invented: no enclosure, antenna or pedestal geometry exists in the repository;
those are reported as BLOCKED — MISSING DATA in engineering/VALIDATION/UNRESOLVED_GEOMETRY.md
(written by hand, not by this script).
Usage: python3 tools/gen_mechanical_package.py [--date YYYY-MM-DD]
Exit: 0 ok, 1 a KiCad source file to copy is missing (the rest is still generated), 2 error.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import math
import os
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_svg_common import Xform, parse_rot, fl, arc_points, SvgCanvas, Style  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH_DIR = os.path.join(ROOT, "4_Schematics and Boards Layout", "4_6_Schematics")
BOARDS = [
    ("MAIN_BOARD", "MainBoard/RADAR_Main_Board.brd", "Main Board"),
    ("POWER_SUPPLY", "PowerBoard/PowerBoard.brd", "Power Supply Board"),
    ("FREQUENCY_SYNTHESIZER", "FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd", "Frequency Synthesizer"),
    ("RF_PA", "PowerAmplifierBoard/RF_PA.brd", "RF Power Amplifier"),
]
MECH = os.path.join(ROOT, "engineering", "MECHANICAL")
ASSUMED_THICKNESS_MM = 1.6     # NOT in the source; KiCad default — stated in every output
FR4_DENSITY_G_CM3 = 1.85        # typical FR-4 with copper; ESTIMATE only


def extract(path: str) -> dict:
    root = ET.parse(path).getroot()
    brd = root.find(".//board")
    pk = {}
    for lib in brd.find("libraries").findall("library"):
        for p in lib.iter("package"):
            pk[(lib.get("name"), p.get("name"))] = p
    plain = brd.find("plain")
    outline = []   # list of polylines [(x,y),...]
    for w in plain.findall("wire"):
        if w.get("layer") == "20":
            pts = arc_points(fl(w, "x1"), fl(w, "y1"), fl(w, "x2"), fl(w, "y2"), fl(w, "curve"))
            outline.append(pts)
    for c in plain.findall("circle"):
        if c.get("layer") == "20":
            cx, cy, r = fl(c, "x"), fl(c, "y"), fl(c, "radius")
            outline.append([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [i * math.pi / 36 for i in range(73)]])
    holes = []  # (x, y, drill, kind, ref)
    for h in plain.findall("hole"):
        holes.append((fl(h, "x"), fl(h, "y"), fl(h, "drill"), "NPTH (free hole)", "—"))
    for el in brd.find("elements").findall("element"):
        p = pk.get((el.get("library"), el.get("package")))
        if p is None:
            continue
        m, a, _ = parse_rot(el.get("rot"))
        xf = Xform(fl(el, "x"), fl(el, "y"), a, m)
        for h in p.findall("hole"):
            x, y = xf.apply(fl(h, "x"), fl(h, "y"))
            holes.append((x, y, fl(h, "drill"), "NPTH (package hole)", el.get("name")))
        for pad in p.findall("pad"):
            d = fl(pad, "drill")
            if d >= 2.0:
                x, y = xf.apply(fl(pad, "x"), fl(pad, "y"))
                holes.append((x, y, d, "PTH mounting pad", el.get("name")))
    xs = [x for pl in outline for x, _ in pl]
    ys = [y for pl in outline for _, y in pl]
    bb = (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)
    return {"version": root.get("version"), "outline": outline, "holes": holes, "bbox": bb,
            "mtime": _dt.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")}


def write_dxf(path: str, outline, holes, bbox):
    """Minimal DXF R12 (ASCII) with layers OUTLINE and HOLES; coordinates relative to the outline's min corner."""
    ox, oy = bbox[0], bbox[1]
    L = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "9", "$EXTMIN", "10", "0", "20", "0",
         "9", "$EXTMAX", "10", f"{bbox[2]-ox:.4f}", "20", f"{bbox[3]-oy:.4f}", "0", "ENDSEC",
         "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "2",
         "0", "LAYER", "2", "OUTLINE", "70", "0", "62", "7", "6", "CONTINUOUS",
         "0", "LAYER", "2", "HOLES", "70", "0", "62", "1", "6", "CONTINUOUS",
         "0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for pl in outline:
        for (x1, y1), (x2, y2) in zip(pl, pl[1:]):
            L += ["0", "LINE", "8", "OUTLINE", "10", f"{x1-ox:.4f}", "20", f"{y1-oy:.4f}", "30", "0",
                  "11", f"{x2-ox:.4f}", "21", f"{y2-oy:.4f}", "31", "0"]
    for x, y, d, kind, ref in holes:
        L += ["0", "CIRCLE", "8", "HOLES", "10", f"{x-ox:.4f}", "20", f"{y-oy:.4f}", "30", "0", "40", f"{d/2:.4f}"]
    L += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", encoding="ascii") as fh:
        fh.write("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    for sub in ("CAD", "STEP", "DXF", "PDF", "dimensions"):
        os.makedirs(os.path.join(MECH, sub), exist_ok=True)
    rc = 0
    plan = SvgCanvas()
    cursor_x = 0.0
    summary = []
    for board, rel, title in BOARDS:
        src = os.path.join(SCH_DIR, rel)
        g = extract(src)
        ox, oy, mx, my = g["bbox"]
        W, H = mx - ox, my - oy
        area_cm2 = W * H / 100.0
        mass_est = area_cm2 * ASSUMED_THICKNESS_MM / 10.0 * FR4_DENSITY_G_CM3
        holes = sorted(g["holes"], key=lambda h: (h[3], h[1], h[0]))
        # DXF (own writer) + copies of KiCad exports
        write_dxf(os.path.join(MECH, "DXF", f"{board}_outline_holes_eagle.dxf"), g["outline"], holes, g["bbox"])
        copies = []
        for srcp, dst in [
            (os.path.join(ROOT, "engineering", "PCB", board, "mechanical", f"{board}_board_only.step"), os.path.join(MECH, "STEP", f"{board}_board_only.step")),
            (os.path.join(ROOT, "engineering", "PCB", board, "mechanical", f"{board}_outline.dxf"), os.path.join(MECH, "DXF", f"{board}_outline_kicad.dxf")),
            (os.path.join(ROOT, "engineering", "PCB", board, "drawings", f"{board}_outline.pdf"), os.path.join(MECH, "PDF", f"{board}_outline.pdf")),
        ]:
            if os.path.isfile(srcp):
                shutil.copyfile(srcp, dst)
                copies.append(os.path.relpath(dst, ROOT))
            else:
                rc = 1
                copies.append(f"MISSING: {os.path.relpath(srcp, ROOT)}")
        # dimensions document
        D = [f"# {title} ({board}) — mechanical dimensions\n",
             f"| Field | Value |\n|---|---|",
             f"| Project | AERIS-10 |", f"| Drawing ID | MECH-DIM-{board} |", f"| Revision | A |", f"| Date | {a.date} |",
             f"| Units | mm; origin = lower-left corner of the outline bounding box (EAGLE coordinates offset by ({ox:.3f}, {oy:.3f})) |",
             f"| Source | `{os.path.relpath(src, ROOT)}` (EAGLE {g['version']}, file date {g['mtime']}), layer 20 Dimension + holes |",
             f"| Status | **SOURCE-DERIVED** for outline and holes; **BLOCKED — MISSING DATA** for thickness, component heights, mass |\n",
             "## 1. Outline\n",
             f"Bounding box **{W:.2f} × {H:.2f} mm** ({len(g['outline'])} outline segments on layer 20). "
             "Outline geometry: `../DXF/" + board + "_outline_holes_eagle.dxf` (from EAGLE XML) and `../DXF/" + board + "_outline_kicad.dxf` (KiCad Edge.Cuts export); 3-D body: `../STEP/" + board + "_board_only.step` (KiCad, assumed 1.6 mm thick).\n",
             "## 2. Holes and mounting pads\n",
             "| # | X (mm) | Y (mm) | Ø (mm) | Type | Part |", "|---|---|---|---|---|---|"]
        for i, (x, y, d, kind, ref) in enumerate(holes, 1):
            D.append(f"| {i} | {x-ox:.3f} | {y-oy:.3f} | {d:.2f} | {kind} | {ref} |")
        mh = [(x - ox, y - oy) for x, y, d, kind, ref in holes if d >= 2.0]
        if len(mh) >= 2:
            xs = sorted({round(x, 2) for x, _ in mh})
            ys = sorted({round(y, 2) for _, y in mh})
            D.append(f"\nMounting-hole pattern (Ø ≥ 2 mm): X positions {xs}; Y positions {ys}; "
                     f"extreme pitch X = {max(xs)-min(xs):.2f} mm, Y = {max(ys)-min(ys):.2f} mm.")
        D += ["\n## 3. Thickness, heights, mass\n",
              "| Quantity | Value | Basis |", "|---|---|---|",
              f"| Board thickness | {ASSUMED_THICKNESS_MM} mm | **ASSUMED** (not in source; KiCad default). Must be confirmed with the stack-up |",
              f"| Bare-board mass | ≈ {mass_est:.0f} g | **ESTIMATE**: area {area_cm2:.1f} cm² × {ASSUMED_THICKNESS_MM} mm × {FR4_DENSITY_G_CM3} g/cm³ (FR-4 + Cu). Assembled mass unknown |",
              "| Max component height | UNKNOWN | no 3-D models in the CAD (Autodesk URNs only); tallest parts are the SMA/terminal connectors — measure on hardware or add models |",
              "| Keep-out / clearance to enclosure | UNKNOWN | no enclosure design exists |",
              "\n## 4. Files\n"] + [f"- `{c}`" for c in copies]
        with open(os.path.join(MECH, "dimensions", f"{board}_dimensions.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(D) + "\n")
        # plan view
        gname = f"board-{board}"
        dx = cursor_x - ox
        st = Style(stroke="#000")
        for pl in g["outline"]:
            plan.polygon(gname, [(x + dx, y - oy) for x, y in pl], 0.4, st, close=False)
        for x, y, d, kind, ref in holes:
            plan.circle(gname, x + dx, y - oy, d / 2, 0.25, Style(stroke="#c00000", fill="none"))
        plan.text(gname, cursor_x, -6, f"{title} — {W:.1f} × {H:.1f} mm, {len(holes)} holes/mounting pads", 3.2, 0, None, "#000", mono=False, weight="bold")
        plan.text(gname, cursor_x, -11, f"source {os.path.basename(src)} (EAGLE {g['version']})", 2.6, 0, None, "#444", mono=False)
        # dimension lines
        plan.line(gname, cursor_x, H + 6, cursor_x + W, H + 6, 0.2, st)
        plan.text(gname, cursor_x + W / 2, H + 7.5, f"{W:.2f}", 3.0, 0, "bottom-center", "#000", mono=False)
        plan.line(gname, cursor_x + W + 6, 0, cursor_x + W + 6, H, 0.2, st)
        plan.text(gname, cursor_x + W + 7.5, H / 2, f"{H:.2f}", 3.0, 90, "bottom-center", "#000", mono=False)
        cursor_x += W + 40
        summary.append((board, title, W, H, len(holes), mass_est))
    plan.write(os.path.join(MECH, "CAD", "pcb_set_plan_view.svg"),
               "AERIS-10 — PCB set, plan view, scale 1:1 — MECH-PLAN-01 Rev A",
               [f"Date {a.date} · Units mm · Status: SOURCE-DERIVED (outlines and holes from the EAGLE .brd files; side-by-side placement is for comparison only, NOT a layout of the enclosure)",
                "Red circles = NPTH holes and plated mounting pads (Ø ≥ 2 mm). Generated by tools/gen_mechanical_package.py."], margin=8.0)
    with open(os.path.join(MECH, "dimensions", "README.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# PCB dimensions summary (generated {a.date})\n\n| Board | Outline W × H (mm) | Holes/mounting pads | Bare-board mass ESTIMATE (g, 1.6 mm assumed) | Document |\n|---|---|---|---|---|\n")
        for board, title, W, H, nh, m in summary:
            fh.write(f"| {title} | {W:.2f} × {H:.2f} | {nh} | ≈ {m:.0f} | `{board}_dimensions.md` |\n")
        fh.write("\nThickness is not recorded in any source file; masses are estimates for planning only (see each document §3). "
                 "Component heights, enclosure, antenna and pedestal geometry: BLOCKED — MISSING DATA (`../../VALIDATION/UNRESOLVED_GEOMETRY.md`).\n")
    print("\n".join(f"{b}: {W:.1f}x{H:.1f} mm, {nh} holes, ~{m:.0f} g" for b, t, W, H, nh, m in summary))
    return rc


if __name__ == "__main__":
    sys.exit(main())
