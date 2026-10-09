#!/usr/bin/env python3
"""Shared helpers for rendering Autodesk EAGLE XML (.sch/.brd) to SVG.

Stdlib only. Used by render_eagle_board.py and render_eagle_schematic.py.

EAGLE coordinates are millimetres with Y pointing up.  All drawing is emitted
inside an SVG group with ``transform="scale(1,-1)"`` so that EAGLE coordinates
can be used directly; text elements get an extra un-flip transform.

Nothing here computes copper pours (EAGLE polygon fill); signal polygons are
drawn as outlines only and the renderers say so in their title block.
"""
from __future__ import annotations

import html
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Iterable, Optional

ROT_RE = re.compile(r"^(S?)(M?)R(-?[0-9.]+)$")


def parse_rot(rot: Optional[str]) -> tuple[bool, float, bool]:
    """Return (mirror, angle_deg, spin) for an EAGLE rot attribute like 'MR90'."""
    if not rot:
        return False, 0.0, False
    m = ROT_RE.match(rot)
    if not m:
        return False, 0.0, False
    return bool(m.group(2)), float(m.group(3)), bool(m.group(1))


@dataclass
class Xform:
    """Local → global transform of an element/instance: mirror(x) → rotate → translate."""

    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    mirror: bool = False

    def apply(self, px: float, py: float) -> tuple[float, float]:
        if self.mirror:
            px = -px
        a = math.radians(self.angle)
        c, s = math.cos(a), math.sin(a)
        return (self.x + px * c - py * s, self.y + px * s + py * c)

    def angle_of(self, local_angle: float) -> float:
        """Global angle of a local rotation (mirroring flips the sense)."""
        if self.mirror:
            return (self.angle - local_angle) % 360
        return (self.angle + local_angle) % 360

    def curve(self, curve: float) -> float:
        return -curve if self.mirror else curve


IDENTITY = Xform()


def f(v: float) -> str:
    """Compact float formatting for SVG."""
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fl(el: ET.Element, name: str, default: float = 0.0) -> float:
    v = el.get(name)
    if v is None or v == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default


def unit_to_mm(v: str) -> float:
    """Parse a DRU value like '6mil', '0.5mm', '0.25' (plain → mm)."""
    v = v.strip()
    m = re.match(r"^(-?[0-9.]+)\s*([a-z]*)$", v)
    if not m:
        return 0.0
    num = float(m.group(1))
    unit = m.group(2)
    if unit == "mil":
        return num * 0.0254
    if unit == "inch":
        return num * 25.4
    if unit == "mic":
        return num / 1000.0
    return num


def arc_points(x1: float, y1: float, x2: float, y2: float, curve: float, n: int = 0) -> list[tuple[float, float]]:
    """Approximate an EAGLE arc (chord p1→p2, included angle 'curve' deg, CCW positive) by points."""
    if abs(curve) < 1e-6:
        return [(x1, y1), (x2, y2)]
    th = math.radians(curve)
    dx, dy = x2 - x1, y2 - y1
    chord = math.hypot(dx, dy)
    if chord < 1e-9:
        return [(x1, y1), (x2, y2)]
    r = chord / (2 * math.sin(abs(th) / 2))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    # distance from chord midpoint to centre
    h = math.sqrt(max(r * r - (chord / 2) ** 2, 0.0))
    # unit normal (left of p1→p2)
    nx, ny = -dy / chord, dx / chord
    if curve > 0:
        cx, cy = mx + nx * h, my + ny * h
    else:
        cx, cy = mx - nx * h, my - ny * h
    if abs(curve) > 180:
        cx, cy = 2 * mx - cx, 2 * my - cy
    a1 = math.atan2(y1 - cy, x1 - cx)
    if n <= 0:
        n = max(4, int(abs(curve) / 10) + 1)
    pts = []
    for i in range(n + 1):
        a = a1 + th * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts[0] = (x1, y1)
    pts[-1] = (x2, y2)
    return pts


class BBox:
    def __init__(self) -> None:
        self.minx = math.inf
        self.miny = math.inf
        self.maxx = -math.inf
        self.maxy = -math.inf

    def add(self, x: float, y: float, pad: float = 0.0) -> None:
        self.minx = min(self.minx, x - pad)
        self.miny = min(self.miny, y - pad)
        self.maxx = max(self.maxx, x + pad)
        self.maxy = max(self.maxy, y + pad)

    def valid(self) -> bool:
        return self.minx < self.maxx and self.miny < self.maxy

    def width(self) -> float:
        return self.maxx - self.minx

    def height(self) -> float:
        return self.maxy - self.miny


@dataclass
class Style:
    stroke: str = "#000"
    fill: str = "none"
    opacity: float = 1.0
    dash: str = ""
    extra: str = ""


class SvgCanvas:
    """Collects SVG fragments per named layer group and writes a complete file."""

    def __init__(self) -> None:
        self.groups: dict[str, list[str]] = {}
        self.order: list[str] = []
        self.bbox = BBox()

    def group(self, name: str) -> list[str]:
        if name not in self.groups:
            self.groups[name] = []
            self.order.append(name)
        return self.groups[name]

    # --- primitives (EAGLE coordinates, Y up) ---------------------------------
    def line(self, g: str, x1, y1, x2, y2, width, st: Style, curve: float = 0.0) -> None:
        w = max(width, 0.05)
        self.bbox.add(x1, y1, w)
        self.bbox.add(x2, y2, w)
        dash = f' stroke-dasharray="{st.dash}"' if st.dash else ""
        if abs(curve) > 1e-6:
            pts = arc_points(x1, y1, x2, y2, curve)
            d = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
            self.group(g).append(
                f'<path d="{d}" fill="none" stroke="{st.stroke}" stroke-width="{f(w)}" '
                f'stroke-linecap="round" stroke-linejoin="round" opacity="{f(st.opacity)}"{dash}{st.extra}/>'
            )
        else:
            self.group(g).append(
                f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{st.stroke}" '
                f'stroke-width="{f(w)}" stroke-linecap="round" opacity="{f(st.opacity)}"{dash}{st.extra}/>'
            )

    def circle(self, g: str, x, y, r, width, st: Style) -> None:
        self.bbox.add(x, y, r + width)
        fill = st.fill
        self.group(g).append(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}" stroke="{st.stroke}" '
            f'stroke-width="{f(width)}" opacity="{f(st.opacity)}"{st.extra}/>'
        )

    def polygon(self, g: str, pts: Iterable[tuple[float, float]], width, st: Style, close: bool = True) -> None:
        pts = list(pts)
        if len(pts) < 2:
            return
        for x, y in pts:
            self.bbox.add(x, y, width)
        d = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts) + (" Z" if close else "")
        dash = f' stroke-dasharray="{st.dash}"' if st.dash else ""
        self.group(g).append(
            f'<path d="{d}" fill="{st.fill}" stroke="{st.stroke}" stroke-width="{f(width)}" '
            f'stroke-linejoin="round" opacity="{f(st.opacity)}"{dash}{st.extra}/>'
        )

    def rect_rot(self, g: str, cx, cy, w, h, angle, st: Style, rx: float = 0.0, width: float = 0.0) -> None:
        """Rectangle centred at (cx,cy), size w×h, rotated by angle (deg, CCW)."""
        a = math.radians(angle)
        c, s = math.cos(a), math.sin(a)
        half = max(abs(w), abs(h)) / 2 * 1.42
        self.bbox.add(cx, cy, half)
        self.group(g).append(
            f'<rect x="{f(-w/2)}" y="{f(-h/2)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" '
            f'transform="matrix({f(c)} {f(s)} {f(-s)} {f(c)} {f(cx)} {f(cy)})" fill="{st.fill}" '
            f'stroke="{st.stroke}" stroke-width="{f(width)}" opacity="{f(st.opacity)}"{st.extra}/>'
        )

    def text(self, g: str, x, y, s: str, size, angle, align: str, color: str, mirror: bool = False,
             opacity: float = 1.0, mono: bool = True, weight: str = "normal") -> None:
        if not s:
            return
        angle = angle % 360
        h_al, v_al = split_align(align)
        # EAGLE keeps texts readable: 180/270 are drawn as 0/90 anchored from the other end
        if 90 < angle <= 270:
            angle = (angle - 180) % 360
            h_al = {"left": "right", "right": "left"}.get(h_al, h_al)
            v_al = {"bottom": "top", "top": "bottom"}.get(v_al, v_al)
        anchor = {"left": "start", "center": "middle", "right": "end"}[h_al]
        baseline = {"bottom": "alphabetic", "center": "central", "top": "hanging"}[v_al]
        fs = size * 1.25
        approx_w = len(s) * fs * 0.62
        # extent along the text direction depends on the anchor; keep it one-sided for start/end
        import math as _m
        ca, sa = _m.cos(_m.radians(angle)), _m.sin(_m.radians(angle))
        if anchor == "start":
            lo, hi = 0.0, approx_w
        elif anchor == "end":
            lo, hi = -approx_w, 0.0
        else:
            lo, hi = -approx_w / 2, approx_w / 2
        for d in (lo, hi):
            self.bbox.add(x + d * ca, y + d * sa, fs)
        fam = "'DejaVu Sans Mono','Menlo','Consolas',monospace" if mono else "'DejaVu Sans',Arial,sans-serif"
        tr = f"translate({f(x)} {f(y)}) rotate({f(angle)}) scale({'-1' if mirror else '1'} -1)"
        self.group(g).append(
            f'<text transform="{tr}" font-size="{f(fs)}" font-family="{fam}" font-weight="{weight}" '
            f'text-anchor="{anchor}" dominant-baseline="{baseline}" fill="{color}" opacity="{f(opacity)}">'
            f"{html.escape(s)}</text>"
        )

    # --- output ----------------------------------------------------------------
    def write(self, path: str, title: str, subtitle_lines: list[str], margin: float = 6.0,
              legend: Optional[list[tuple[str, str]]] = None, hidden: Iterable[str] = (),
              bbox: Optional[BBox] = None, extra_blocks: Optional[list[str]] = None) -> None:
        bb = bbox or self.bbox
        if not bb.valid():
            bb = BBox()
            bb.add(0, 0)
            bb.add(100, 100)
        title_h = 6.0 + 3.6 * (len(subtitle_lines) + 1)
        legend_h = 0.0
        if legend:
            legend_h = 4.0 * (len(legend) + 1)
        minx = bb.minx - margin
        miny = bb.miny - margin - legend_h
        w = bb.width() + 2 * margin
        h = bb.height() + 2 * margin + title_h + legend_h
        maxy = bb.maxy + margin + title_h
        hidden = set(hidden)
        out = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(w)}mm" height="{f(h)}mm" '
            f'viewBox="{f(minx)} {f(-maxy)} {f(w)} {f(h)}">',
            f"<title>{html.escape(title)}</title>",
            '<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="#ffffff"/>'.format(f(minx), f(-maxy), f(w), f(h)),
        ]
        # title block (in screen coordinates, no flip)
        ty = -maxy + 5.0
        out.append(
            f'<text x="{f(minx + 2)}" y="{f(ty)}" font-size="4" font-family="Arial,sans-serif" font-weight="bold" fill="#000">'
            f"{html.escape(title)}</text>"
        )
        for i, line in enumerate(subtitle_lines):
            out.append(
                f'<text x="{f(minx + 2)}" y="{f(ty + 3.6 * (i + 1))}" font-size="2.6" font-family="Arial,sans-serif" fill="#333">'
                f"{html.escape(line)}</text>"
            )
        out.append(f'<line x1="{f(minx)}" y1="{f(-maxy + title_h)}" x2="{f(minx + w)}" y2="{f(-maxy + title_h)}" stroke="#999" stroke-width="0.2"/>')
        if legend:
            ly = -(bb.miny - margin) + 4.0
            for i, (color, label) in enumerate(legend):
                yy = ly + 4.0 * i
                out.append(f'<rect x="{f(minx + 2)}" y="{f(yy - 2.2)}" width="6" height="2.6" fill="{color}" stroke="#555" stroke-width="0.15"/>')
                out.append(f'<text x="{f(minx + 10)}" y="{f(yy)}" font-size="2.6" font-family="Arial,sans-serif" fill="#222">{html.escape(label)}</text>')
        out.append('<g transform="scale(1,-1)">')
        for name in self.order:
            style = ' style="display:none"' if name in hidden else ""
            out.append(f'<g id="{html.escape(name)}"{style}>')
            out.extend(self.groups[name])
            out.append("</g>")
        out.append("</g>")
        if extra_blocks:
            out.extend(extra_blocks)
        out.append("</svg>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out))


def split_align(align: Optional[str]) -> tuple[str, str]:
    if not align:
        return "left", "bottom"
    if align == "center":
        return "center", "center"
    parts = align.split("-")
    if len(parts) == 2:
        v, h = parts
        return h, v
    if align in ("left", "right"):
        return align, "center"
    if align in ("top", "bottom"):
        return "center", align
    return "left", "bottom"


def load_eagle(path: str) -> ET.Element:
    """Parse an EAGLE XML file and return the <eagle> root."""
    return ET.parse(path).getroot()


def eagle_version(root: ET.Element) -> str:
    return root.get("version", "?")


def layer_names(root: ET.Element) -> dict[int, str]:
    return {int(l.get("number")): l.get("name", "") for l in root.iter("layer")}
