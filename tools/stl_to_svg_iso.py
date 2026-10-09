#!/usr/bin/env python3
"""Render binary/ASCII STL files to a flat-shaded isometric SVG (painter's algorithm). Stdlib only.
Usage: python3 tools/stl_to_svg_iso.py -o out.svg [--title T] [--scale 0.5] [--az 35 --el 30] file1.stl[:#color[:opacity]] [file2.stl ...]
Intended for quick visual checks of FreeCAD/KiCad STL exports; not a CAD drawing.
"""
import argparse
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_svg_common import SvgCanvas, Style  # noqa: E402


def read_stl(path):
    data = open(path, "rb").read()
    tris = []
    if data[:5] == b"solid" and b"facet" in data[:1000]:
        v = []
        for line in data.decode("latin1").splitlines():
            t = line.strip().split()
            if t[:1] == ["vertex"]:
                v.append(tuple(float(x) for x in t[1:4]))
                if len(v) == 3:
                    tris.append(tuple(v)); v = []
        return tris
    n = struct.unpack("<I", data[80:84])[0]
    off = 84
    for _ in range(n):
        vals = struct.unpack("<12fH", data[off:off + 50]); off += 50
        tris.append(((vals[3], vals[4], vals[5]), (vals[6], vals[7], vals[8]), (vals[9], vals[10], vals[11])))
    return tris


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+"); ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="STL isometric view"); ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--az", type=float, default=35.0); ap.add_argument("--el", type=float, default=30.0)
    ap.add_argument("--subtitle", default="")
    a = ap.parse_args()
    az, el = math.radians(a.az), math.radians(a.el)
    ca, sa, ce, se = math.cos(az), math.sin(az), math.cos(el), math.sin(el)
    def proj(p):
        x, y, z = p
        xr = x * ca - y * sa; yr = x * sa + y * ca
        X = xr; Y = z * ce - yr * se; depth = yr * ce + z * se
        return X * a.scale, Y * a.scale, depth
    light = (0.4, -0.6, 0.7)
    ln = math.sqrt(sum(c * c for c in light)); light = tuple(c / ln for c in light)
    faces = []
    for spec in a.files:
        parts_ = spec.split(":")
        path = parts_[0]
        col = parts_[1].lstrip("#") if len(parts_) > 1 and parts_[1] else ""
        opacity = float(parts_[2]) if len(parts_) > 2 else 1.0
        base = tuple(int(col[i:i + 2], 16) for i in (0, 2, 4)) if col else (154, 167, 181)
        for t in read_stl(path):
            (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
            ux, uy, uz = x2 - x1, y2 - y1, z2 - z1; vx, vy, vz = x3 - x1, y3 - y1, z3 - z1
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            nn = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            shade = 0.35 + 0.65 * max(0.0, (nx * light[0] + ny * light[1] + nz * light[2]) / nn)
            pts = [proj(p) for p in t]
            d = sum(p[2] for p in pts) / 3
            col_rgb = "#%02x%02x%02x" % tuple(min(255, int(c * shade)) for c in base)
            faces.append((d, [(p[0], p[1]) for p in pts], col_rgb, opacity))
    faces.sort(key=lambda f: f[0])
    cv = SvgCanvas(); g = "iso"; cv.group(g)
    for d, pts, col, op in faces:
        cv.polygon(g, pts, 0.05, Style(stroke=col, fill=col, opacity=op))
    cv.write(a.output, a.title, [a.subtitle, f"{len(faces)} triangles from {len(a.files)} STL file(s); azimuth {a.az}°, elevation {a.el}°, scale {a.scale}; rendered by tools/stl_to_svg_iso.py"], margin=8)
    print("wrote", a.output, len(faces), "faces")


if __name__ == "__main__":
    main()
