#!/usr/bin/env python3
"""CONCEPTUAL exploded assembly view of the AERIS-10 electronics set (SVG).

Board outlines and hole positions are taken from the EAGLE .brd files (verified
geometry, drawn in oblique projection at a uniform scale).  The vertical
ARRANGEMENT, the spacing, the antenna panel and the host computer are CONCEPTUAL:
no enclosure, antenna or pedestal CAD exists in the repository.  The drawing is
labelled accordingly and must not be used as a production drawing.

Balloon numbers refer to engineering/ASSEMBLY/PARTS_LIST.md.
Usage: python3 tools/gen_assembly_exploded_view.py [--out engineering/ASSEMBLY/EXPLODED_VIEWS/aeris10_exploded_conceptual.svg]
Exit 0 ok, 2 error.  Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import math
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_svg_common import SvgCanvas, Style, Xform, parse_rot, fl, arc_points  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH_DIR = os.path.join(ROOT, "4_Schematics and Boards Layout", "4_6_Schematics")
SCALE = 0.35          # drawing mm per board mm (uniform)
OBL = (0.5, 0.35)     # oblique projection: x' = x + d*0.5, y' = y + d*0.35 (d = depth axis)


def geometry(rel: str):
    root = ET.parse(os.path.join(SCH_DIR, rel)).getroot()
    brd = root.find(".//board")
    plain = brd.find("plain")
    xs, ys, holes = [], [], []
    for w in plain.findall("wire"):
        if w.get("layer") == "20":
            xs += [fl(w, "x1"), fl(w, "x2")]
            ys += [fl(w, "y1"), fl(w, "y2")]
    pk = {}
    for lib in brd.find("libraries").findall("library"):
        for p in lib.iter("package"):
            pk[(lib.get("name"), p.get("name"))] = p
    for h in plain.findall("hole"):
        holes.append((fl(h, "x"), fl(h, "y"), fl(h, "drill")))
    for el in brd.find("elements").findall("element"):
        p = pk.get((el.get("library"), el.get("package")))
        if p is None:
            continue
        m, a, _ = parse_rot(el.get("rot"))
        xf = Xform(fl(el, "x"), fl(el, "y"), a, m)
        for h in p.findall("hole"):
            x, y = xf.apply(fl(h, "x"), fl(h, "y"))
            holes.append((x, y, fl(h, "drill")))
        for pad in p.findall("pad"):
            if fl(pad, "drill") >= 2.0:
                x, y = xf.apply(fl(pad, "x"), fl(pad, "y"))
                holes.append((x, y, fl(pad, "drill")))
    ox, oy = min(xs), min(ys)
    return (max(xs) - ox, max(ys) - oy, [(x - ox, y - oy, d) for x, y, d in holes if d >= 2.0])


def proj(x, depth, z):
    """Oblique projection of a point on a horizontal board plane at height z."""
    return (x + depth * OBL[0], z + depth * OBL[1])


def draw_board(cv, g, x0, z, W, D, holes, label, color, dashed=False, scale=SCALE):
    W, D = W * scale, D * scale
    pts = [proj(x0, 0, z), proj(x0 + W, 0, z), proj(x0 + W, D, z), proj(x0, D, z)]
    cv.polygon(g, pts, 0.5, Style(stroke="#000", fill=color, opacity=0.9, dash="2,1.5" if dashed else ""))
    for hx, hy, d in holes:
        px, py = proj(x0 + hx * scale, hy * scale, z)
        cv.circle(g, px, py, max(d * scale / 2, 0.6), 0.25, Style(stroke="#b00000", fill="#fff"))
    cx, cy = proj(x0 + W / 2, D / 2, z)
    return pts, (cx, cy)


def balloon(cv, g, x, y, n, tx, ty):
    cv.line(g, x, y, tx, ty, 0.3, Style(stroke="#000"))
    cv.circle(g, tx, ty, 4.2, 0.35, Style(stroke="#000", fill="#fff"))
    cv.text(g, tx, ty, str(n), 3.4, 0, "center", "#000", mono=False, weight="bold")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "engineering", "ASSEMBLY", "EXPLODED_VIEWS", "aeris10_exploded_conceptual.svg"))
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    main_b = geometry("MainBoard/RADAR_Main_Board.brd")
    pwr = geometry("PowerBoard/PowerBoard.brd")
    syn = geometry("FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd")
    pa = geometry("PowerAmplifierBoard/RF_PA.brd")
    cv = SvgCanvas()
    g = "exploded"
    cv.group(g)
    x0 = 20.0
    # level 0: Power Board (bottom)
    _, c_pwr = draw_board(cv, g, x0, 0, pwr[0], pwr[1], pwr[2], "Power", "#d9ead3")
    # level 1: Main Board
    z_main = 70
    _, c_main = draw_board(cv, g, x0 + 5, z_main, main_b[0], main_b[1], main_b[2], "Main", "#cfe2f3")
    # Synth beside the main board, same level
    _, c_syn = draw_board(cv, g, x0 + 5 + main_b[0] * SCALE + 25, z_main, syn[0], syn[1], syn[2], "Synth", "#fff2cc")
    # level 2: 16 RF PA boards in a row (CONCEPTUAL arrangement)
    z_pa = 150
    pa_centres = []
    for i in range(16):
        px = x0 + 5 + i * (pa[0] * SCALE + 2.5)
        _, c = draw_board(cv, g, px, z_pa, pa[0], pa[1], pa[2], f"PA{i+1}", "#f4cccc")
        pa_centres.append(c)
    # level 3: antenna panel (CONCEPTUAL: 16 elements at λ/2 = 14.3 mm per 02_hardware/04_antenna_beamforming.md; no CAD)
    z_ant = 215
    ant_w, ant_d = 214.3, 60.0
    pts, c_ant = draw_board(cv, g, x0 + 5, z_ant, ant_w, ant_d, [], "Antenna", "#eeeeee", dashed=True)
    for i in range(16):
        ex = x0 + 5 + (7.15 + i * 14.3) * SCALE
        ex_, ey_ = proj(ex, ant_d * SCALE / 2, z_ant)
        cv.circle(g, ex_, ey_, 1.6, 0.25, Style(stroke="#666", fill="none", dash="1,0.8"))
    # host computer (CONCEPTUAL box)
    hx = x0 + 5 + 16 * (pa[0] * SCALE + 2.5) + 20
    draw_board(cv, g, hx, z_pa, 120, 80, [], "Host", "#ffffff", dashed=True)
    # explode axes
    for (cx, cy) in [c_pwr, c_main]:
        pass
    axis_x = x0 + 5 + main_b[0] * SCALE / 2
    cv.line(g, axis_x, -5, axis_x, z_ant + 40, 0.25, Style(stroke="#888", dash="4,2"))
    # labels
    T = lambda x, y, s, size=3.0, w="normal": cv.text(g, x, y, s, size, 0, None, "#000", mono=False, weight=w)
    T(x0 + 5, -9, f"(1) Power Supply Board {pwr[0]:.0f} × {pwr[1]:.0f} mm (PowerBoard.brd)", 3.2, "bold")
    T(x0 + 5, z_main - 9, f"(2) Main Board {main_b[0]:.0f} × {main_b[1]:.0f} mm (RADAR_Main_Board.brd)", 3.2, "bold")
    T(x0 + 5 + main_b[0] * SCALE + 25, z_main - 9, f"(3) Frequency Synthesizer {syn[0]:.0f} × {syn[1]:.0f} mm", 3.2, "bold")
    T(x0 + 5, z_pa - 9, f"(4) 16 × RF PA board {pa[0]:.0f} × {pa[1]:.0f} mm (RF_PA.brd) — count from Main Board connectors X_1..X_16 / X3,X38..X52 / J24..J55", 3.2, "bold")
    T(hx, z_pa + 80 * SCALE * OBL[1] + 8, "(6) Host computer + Python GUI (CONCEPTUAL; USB CDC via Main Board mini-USB X53)", 3.0)
    T(x0 + 5, z_ant - 9, "(5) Antenna array — CONCEPTUAL: 16 elements, λ/2 = 14.3 mm, aperture 214.3 mm per 02_hardware/04_antenna_beamforming.md; NO CAD in repository", 3.2, "bold")
    # balloons
    balloon(cv, g, c_pwr[0], c_pwr[1], 1, c_pwr[0] - 60, c_pwr[1] + 20)
    balloon(cv, g, c_main[0], c_main[1], 2, c_main[0] - 70, c_main[1] + 25)
    balloon(cv, g, c_syn[0], c_syn[1], 3, c_syn[0] + 40, c_syn[1] + 20)
    balloon(cv, g, pa_centres[0][0], pa_centres[0][1], 4, pa_centres[0][0] - 20, pa_centres[0][1] + 22)
    balloon(cv, g, c_ant[0], c_ant[1], 5, c_ant[0] - 60, c_ant[1] + 25)
    hc = proj(hx + 60 * SCALE * 0.5 + 20, 40 * SCALE, z_pa)
    balloon(cv, g, hc[0], hc[1], 6, hc[0] + 40, hc[1] + 18)
    # cable references (from engineering/SYSTEM/interfaces/interconnection_table.md)
    cab = [("CBL-01..CBL-15 rails Power→Main (Molex 22-23-2021)", c_pwr, c_main),
           ("CBL-20 enable bus SV1↔SV1 (20-way)", c_pwr, c_main),
           ("CBL-30.. clocks/LO Synth→Main (SMA coax)", c_syn, c_main),
           ("CBL-40..55 RF, CBL-56..71 VG, CBL-72..87 sense: Main↔PA", c_main, pa_centres[7])]
    yy = z_ant + 60
    for i, (lbl, p1, p2) in enumerate(cab):
        cv.line(g, p1[0], p1[1], p2[0], p2[1], 0.3, Style(stroke="#1f5f8b", dash="3,2", opacity=0.6))
        T(x0 + 5, yy + i * 5, "— " + lbl + " (cable IDs are proposals; types/lengths UNVERIFIED)", 2.8)
    # legend
    T(x0 + 5, yy + 24, "Legend: solid outline = board geometry VERIFIED from EAGLE .brd (scale 0.35); dashed = CONCEPTUAL item without CAD; red circles = NPTH/mounting holes ≥ 2 mm; balloons → PARTS_LIST.md; vertical spacing is arbitrary.", 2.8)
    cv.write(a.out, "AERIS-10 — Exploded assembly view, electronics set — ASM-EXP-01 Rev A — STATUS: CONCEPTUAL",
             [f"Date {a.date} · Units: drawing scale 0.35 (board sizes true to source) · Source: 4 × EAGLE .brd, 02_hardware/04_antenna_beamforming.md, engineering/SYSTEM/interfaces/interconnection_table.md",
              "CONCEPTUAL ILLUSTRATION — the stacking order, spacing, antenna panel, host and fasteners are NOT from any design file. Not a production drawing. Generated by tools/gen_assembly_exploded_view.py"],
             margin=8.0)
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
