#!/usr/bin/env python3
"""
gen_board_outline_svg.py — Draw an outline/mounting-hole dimension drawing (SVG) from an EAGLE .brd.

Verified geometry only: board outline = wires on layer 20 (Dimension); mounting holes = <hole>
elements (NPTH) and package pads with drill >= 2.0 mm; selected component origins (by name
prefix) are marked as reference crosses.  Dimensions are printed in mm.  The drawing contains
NO enclosure, NO component outlines and NO thickness; those are not in the source files.

Usage:
    python3 tools/gen_board_outline_svg.py BOARD.brd --out drawing.svg [--title "Main Board"] [--mark U42,U2,U1,U3]
Exit codes: 0 ok, 1 no outline found, 2 parse error.
Dependencies: Python 3.8+ standard library.
"""
import argparse
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("board")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--mark", default="", help="comma-separated element names to mark")
    ap.add_argument("--scale", type=float, default=2.0, help="px per mm")
    args = ap.parse_args()
    try:
        root = ET.parse(args.board).getroot()
    except (ET.ParseError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr); return 2
    outline = [(float(w.get("x1")), float(w.get("y1")), float(w.get("x2")), float(w.get("y2")))
               for w in root.iter("wire") if w.get("layer") == "20"]
    if not outline:
        print("ERROR: no layer-20 outline wires", file=sys.stderr); return 1
    xs = [c for w in outline for c in (w[0], w[2])]; ys = [c for w in outline for c in (w[1], w[3])]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    W, H = maxx - minx, maxy - miny
    holes = [(float(h.get("x")), float(h.get("y")), float(h.get("drill"))) for h in root.iter("hole")]
    # large drills inside packages (e.g. mounting-hole packages)
    pkgs = {}
    for lib in root.iter("library"):
        for p in lib.iter("package"):
            pkgs[(lib.get("name"), p.get("name"))] = p
    marks = {m.strip() for m in args.mark.split(",") if m.strip()}
    mark_pts, pad_holes = [], []
    for el in root.iter("element"):
        ex, ey = float(el.get("x")), float(el.get("y"))
        if el.get("name") in marks:
            mark_pts.append((ex, ey, el.get("name"), el.get("value", "")))
        p = pkgs.get((el.get("library"), el.get("package")))
        if p is None:
            continue
        rot = el.get("rot", "R0"); ang = float(rot.lstrip("MR") or 0); mirror = rot.startswith("M")
        for pad in p.iter("pad"):
            d = float(pad.get("drill", 0))
            if d >= 2.0:
                px, py = float(pad.get("x")), float(pad.get("y"))
                if mirror: px = -px
                a = math.radians(ang); rx = px * math.cos(a) - py * math.sin(a); ry = px * math.sin(a) + py * math.cos(a)
                pad_holes.append((ex + rx, ey + ry, d))
    s = args.scale; margin = 40
    def X(x): return margin + (x - minx) * s
    def Y(y): return margin + (maxy - y) * s   # EAGLE y up -> SVG y down
    width, height = W * s + 2 * margin + 260, H * s + 2 * margin + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" font-family="monospace" font-size="11">',
           '<rect width="100%" height="100%" fill="white"/>',
           f'<text x="{margin}" y="18" font-size="14" font-weight="bold">{args.title or Path(args.board).name} — outline and mounting holes (from EAGLE layer 20 / NPTH holes). Scale {s} px/mm. NOT a mechanical design drawing.</text>']
    for x1, y1, x2, y2 in outline:
        out.append(f'<line x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}" stroke="black" stroke-width="1.5"/>')
    # dimension lines
    out.append(f'<line x1="{X(minx):.1f}" y1="{Y(miny)+18:.1f}" x2="{X(maxx):.1f}" y2="{Y(miny)+18:.1f}" stroke="blue"/>')
    out.append(f'<text x="{(X(minx)+X(maxx))/2-20:.1f}" y="{Y(miny)+32:.1f}" fill="blue">{W:.2f} mm</text>')
    out.append(f'<line x1="{X(maxx)+18:.1f}" y1="{Y(miny):.1f}" x2="{X(maxx)+18:.1f}" y2="{Y(maxy):.1f}" stroke="blue"/>')
    out.append(f'<text x="{X(maxx)+22:.1f}" y="{(Y(miny)+Y(maxy))/2:.1f}" fill="blue">{H:.2f} mm</text>')
    allh = holes + pad_holes
    for i, (hx, hy, d) in enumerate(allh, 1):
        out.append(f'<circle cx="{X(hx):.1f}" cy="{Y(hy):.1f}" r="{d/2*s:.1f}" fill="none" stroke="red" stroke-width="1.2"/>')
        out.append(f'<text x="{X(hx)+d/2*s+2:.1f}" y="{Y(hy)-2:.1f}" fill="red" font-size="9">H{i}</text>')
    for mx, my, name, val in mark_pts:
        out.append(f'<line x1="{X(mx)-6:.1f}" y1="{Y(my):.1f}" x2="{X(mx)+6:.1f}" y2="{Y(my):.1f}" stroke="green"/>')
        out.append(f'<line x1="{X(mx):.1f}" y1="{Y(my)-6:.1f}" x2="{X(mx):.1f}" y2="{Y(my)+6:.1f}" stroke="green"/>')
        out.append(f'<text x="{X(mx)+7:.1f}" y="{Y(my)+12:.1f}" fill="green" font-size="9">{name} {val}</text>')
    # table
    tx, ty = W * s + 2 * margin + 10, margin
    out.append(f'<text x="{tx}" y="{ty}" font-weight="bold">Hole table (mm, board origin = EAGLE origin)</text>')
    for i, (hx, hy, d) in enumerate(allh, 1):
        out.append(f'<text x="{tx}" y="{ty + 14*i}">H{i}: x={hx - minx:.2f} y={hy - miny:.2f} Ø{d:.2f}</text>')
    yy = ty + 14 * (len(allh) + 2)
    out.append(f'<text x="{tx}" y="{yy}">Outline bbox: {W:.2f} x {H:.2f} mm</text>')
    out.append(f'<text x="{tx}" y="{yy+14}">Origin offset: ({minx:.2f}, {miny:.2f})</text>')
    out.append(f'<text x="{tx}" y="{yy+28}">Thickness / mass: NOT IN SOURCE</text>')
    out.append("</svg>")
    Path(args.out).write_text("\n".join(out))
    print(f"{Path(args.board).name}: outline {W:.2f} x {H:.2f} mm, {len(holes)} NPTH holes, {len(pad_holes)} large pad drills, {len(mark_pts)} marks -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
