#!/usr/bin/env python3
"""Render an Autodesk EAGLE schematic (.sch, XML) to one SVG per sheet.

Stdlib only; no EAGLE needed.  Symbols, pins, nets, busses, junctions, labels,
texts, frames and part attributes are drawn from the XML.  The output is a
documentation rendering (SOURCE-DERIVED), not a CAD export: EAGLE's vector font
is replaced by a monospace system font, so text extents differ slightly.

Usage:
  python3 tools/render_eagle_schematic.py <file.sch> --out DIR --board NAME \
        [--drawing-id ID] [--rev A] [--date YYYY-MM-DD] [--index sheets.json]
Exit codes: 0 ok, 1 parse/IO error, 2 bad arguments.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_svg_common import (BBox, Style, SvgCanvas, Xform, fl, parse_rot, eagle_version)  # noqa: E402

COL = {
    91: "#007a3d",   # Nets
    92: "#7a007a",   # Busses
    93: "#2e8b57",   # Pins
    94: "#8b0000",   # Symbols
    95: "#333333",   # Names
    96: "#333333",   # Values
    97: "#8b6508",   # Info
    98: "#9a9a9a",   # Guide
}
PIN_LEN = {"point": 0.0, "short": 2.54, "middle": 5.08, "long": 7.62}


def color(layer: int) -> str:
    return COL.get(layer, "#555555")


class Schematic:
    def __init__(self, path: str) -> None:
        self.path = path
        self.root = ET.parse(path).getroot()
        self.sch = self.root.find(".//schematic")
        if self.sch is None:
            raise ValueError("not an EAGLE schematic: " + path)
        self.symbols: dict[tuple[str, str], ET.Element] = {}
        self.devicesets: dict[tuple[str, str], ET.Element] = {}
        libs = self.sch.find("libraries")
        if libs is not None:
            for lib in libs.findall("library"):
                ln = lib.get("name", "")
                for s in lib.iter("symbol"):
                    self.symbols[(ln, s.get("name"))] = s
                for d in lib.iter("deviceset"):
                    self.devicesets[(ln, d.get("name"))] = d
        self.parts: dict[str, ET.Element] = {}
        parts = self.sch.find("parts")
        if parts is not None:
            for p in parts.findall("part"):
                self.parts[p.get("name")] = p
        self.sheets = list(self.sch.find("sheets").findall("sheet")) if self.sch.find("sheets") is not None else []

    # ---- lookups ----------------------------------------------------------
    def gate_info(self, part: ET.Element, gate_name: str):
        """Return (symbol element, pad map {pin: pad}, n_gates) for a part's gate."""
        key = (part.get("library", ""), part.get("deviceset", ""))
        ds = self.devicesets.get(key)
        if ds is None:
            return None, {}, 1
        gates = ds.find("gates")
        gate = None
        n_gates = 0
        if gates is not None:
            glist = gates.findall("gate")
            n_gates = len(glist)
            for g in glist:
                if g.get("name") == gate_name:
                    gate = g
        if gate is None:
            return None, {}, n_gates
        sym = self.symbols.get((part.get("library", ""), gate.get("symbol", "")))
        pads: dict[str, str] = {}
        devs = ds.find("devices")
        if devs is not None:
            for d in devs.findall("device"):
                if d.get("name", "") == part.get("device", ""):
                    conns = d.find("connects")
                    if conns is not None:
                        for c in conns.findall("connect"):
                            if c.get("gate") == gate_name:
                                pads[c.get("pin")] = c.get("pad")
        return sym, pads, n_gates

    def display_name(self, part: ET.Element, gate_name: str, n_gates: int) -> str:
        name = part.get("name", "")
        if n_gates > 1 and not gate_name.startswith("G$"):
            return name + gate_name
        return name

    def display_value(self, part: ET.Element) -> str:
        v = part.get("value")
        if v:
            return v
        return part.get("deviceset", "") + part.get("device", "")


def draw_primitives(cv: SvgCanvas, el: ET.Element, xf: Xform, subst: dict[str, str], smashed: bool,
                    group_of=lambda layer: f"layer-{layer}") -> None:
    """Draw wires/circles/rectangles/polygons/texts of a symbol or plain section."""
    for e in el:
        tag = e.tag
        layer = int(e.get("layer", "94"))
        g = group_of(layer)
        if tag == "wire":
            x1, y1 = xf.apply(fl(e, "x1"), fl(e, "y1"))
            x2, y2 = xf.apply(fl(e, "x2"), fl(e, "y2"))
            w = fl(e, "width", 0.15)
            if layer == 91 and w < 0.2:
                w = 0.2
            cv.line(g, x1, y1, x2, y2, w, Style(stroke=color(layer)), curve=xf.curve(fl(e, "curve")))
        elif tag == "circle":
            cx, cy = xf.apply(fl(e, "x"), fl(e, "y"))
            w = fl(e, "width", 0.15)
            st = Style(stroke=color(layer), fill=color(layer) if w == 0 else "none")
            cv.circle(g, cx, cy, fl(e, "radius"), max(w, 0.15), st)
        elif tag == "rectangle":
            pts = [xf.apply(fl(e, "x1"), fl(e, "y1")), xf.apply(fl(e, "x2"), fl(e, "y1")),
                   xf.apply(fl(e, "x2"), fl(e, "y2")), xf.apply(fl(e, "x1"), fl(e, "y2"))]
            cv.polygon(g, pts, 0.0, Style(stroke="none", fill=color(layer)))
        elif tag == "polygon":
            pts = [xf.apply(fl(v, "x"), fl(v, "y")) for v in e.findall("vertex")]
            cv.polygon(g, pts, fl(e, "width", 0.15), Style(stroke=color(layer), fill=color(layer), opacity=0.9))
        elif tag == "text":
            raw = (e.text or "").strip()
            if raw.startswith(">"):
                key = raw[1:].upper()
                if smashed and key in ("NAME", "VALUE", "PART", "GATE"):
                    continue  # drawn from the instance attributes instead
                raw = subst.get(key, raw)
            tx, ty = xf.apply(fl(e, "x"), fl(e, "y"))
            _, a, _ = parse_rot(e.get("rot"))
            cv.text(g, tx, ty, raw, fl(e, "size", 1.778), xf.angle_of(a), e.get("align"), color(layer),
                    mirror=xf.mirror)
        elif tag == "frame":
            draw_frame(cv, e, xf)
        elif tag == "dimension":
            x1, y1 = xf.apply(fl(e, "x1"), fl(e, "y1"))
            x2, y2 = xf.apply(fl(e, "x2"), fl(e, "y2"))
            cv.line(g, x1, y1, x2, y2, 0.15, Style(stroke=color(layer)))


def draw_frame(cv: SvgCanvas, e: ET.Element, xf: Xform) -> None:
    x1, y1, x2, y2 = fl(e, "x1"), fl(e, "y1"), fl(e, "x2"), fl(e, "y2")
    cols, rows = int(e.get("columns", "8")), int(e.get("rows", "5"))
    layer = int(e.get("layer", "94"))
    g = f"layer-{layer}"
    st = Style(stroke=color(layer))
    ax1, ay1 = xf.apply(x1, y1)
    ax2, ay2 = xf.apply(x2, y2)
    xa, xb = sorted((ax1, ax2))
    ya, yb = sorted((ay1, ay2))
    cv.polygon(g, [(xa, ya), (xb, ya), (xb, yb), (xa, yb)], 0.3, st)
    inset = 4.0
    cv.polygon(g, [(xa + inset, ya + inset), (xb - inset, ya + inset), (xb - inset, yb - inset), (xa + inset, yb - inset)], 0.2, st)
    w, h = xb - xa, yb - ya
    for i in range(1, cols):
        xx = xa + w * i / cols
        cv.line(g, xx, ya, xx, ya + inset, 0.2, st)
        cv.line(g, xx, yb - inset, xx, yb, 0.2, st)
    for i in range(cols):
        xx = xa + w * (i + 0.5) / cols
        cv.text(g, xx, ya + 1.2, chr(65 + i), 1.8, 0, "center", color(layer))
        cv.text(g, xx, yb - 2.8, chr(65 + i), 1.8, 0, "center", color(layer))
    for i in range(1, rows):
        yy = ya + h * i / rows
        cv.line(g, xa, yy, xa + inset, yy, 0.2, st)
        cv.line(g, xb - inset, yy, xb, yy, 0.2, st)
    for i in range(rows):
        yy = yb - h * (i + 0.5) / rows
        cv.text(g, xa + 2.0, yy, str(i + 1), 1.8, 0, "center", color(layer))
        cv.text(g, xb - 2.0, yy, str(i + 1), 1.8, 0, "center", color(layer))


def draw_pin(cv: SvgCanvas, pin: ET.Element, xf: Xform, pads: dict[str, str]) -> None:
    px, py = fl(pin, "x"), fl(pin, "y")
    length = PIN_LEN.get(pin.get("length", "long"), 7.62)
    _, a, _ = parse_rot(pin.get("rot"))
    import math
    dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
    gx1, gy1 = xf.apply(px, py)
    gx2, gy2 = xf.apply(px + dx * length, py + dy * length)
    g = "layer-93"
    if length > 0:
        cv.line(g, gx1, gy1, gx2, gy2, 0.1524, Style(stroke=color(93)))
    func = pin.get("function", "none")
    if func in ("dot", "clkdot"):
        cx, cy = xf.apply(px + dx * (length + 0.8), py + dy * (length + 0.8))
        cv.circle(g, cx, cy, 0.8, 0.15, Style(stroke=color(93)))
    if func in ("clk", "clkdot"):
        bx, by = px + dx * length, py + dy * length
        nx, ny = -dy, dx
        p1 = xf.apply(bx + nx * 0.8, by + ny * 0.8)
        p2 = xf.apply(bx + dx * 1.2, by + dy * 1.2)
        p3 = xf.apply(bx - nx * 0.8, by - ny * 0.8)
        cv.polygon(g, [p1, p2, p3], 0.15, Style(stroke=color(93)), close=False)
    vis = pin.get("visible", "both")
    ga = xf.angle_of(a)  # global pin direction
    name = pin.get("name", "")
    if vis in ("pin", "both") and name:
        tx, ty = xf.apply(px + dx * (length + 0.8), py + dy * (length + 0.8))
        # text runs along the pin direction, anchored at the pin end
        if abs(ga - 0) < 1 or abs(ga - 360) < 1:
            cv.text("layer-95", tx, ty, name, 1.5, 0, "center-left", color(95))
        elif abs(ga - 180) < 1:
            cv.text("layer-95", tx, ty, name, 1.5, 0, "center-right", color(95))
        elif abs(ga - 90) < 1:
            cv.text("layer-95", tx, ty, name, 1.5, 90, "center-left", color(95))
        else:
            cv.text("layer-95", tx, ty, name, 1.5, 90, "center-right", color(95))
    pad = pads.get(name)
    if vis in ("pad", "both") and pad and length > 0:
        mx, my = px + dx * length * 0.5, py + dy * length * 0.5
        nx, ny = -dy, dx
        tx, ty = xf.apply(mx + nx * 0.6, my + ny * 0.6)
        ang = 0 if abs(ga) < 1 or abs(ga - 180) < 1 or abs(ga - 360) < 1 else 90
        cv.text("layer-95", tx, ty, pad, 1.1, ang, "bottom-center", "#1f5f8b")


def render_sheet(sch: Schematic, sheet: ET.Element, index: int, total: int, args) -> dict:
    cv = SvgCanvas()
    for l in (98, 97, 94, 93, 91, 92, 95, 96):
        cv.group(f"layer-{l}")
    mtime = _dt.datetime.fromtimestamp(os.path.getmtime(sch.path)).strftime("%Y-%m-%d %H:%M")
    frame_subst = {"DRAWING_NAME": os.path.basename(sch.path), "LAST_DATE_TIME": mtime,
                   "SHEET": f"{index}/{total}", "SHEETS": str(total), "SHEETNR": str(index)}
    plain = sheet.find("plain")
    if plain is not None:
        draw_primitives(cv, plain, Xform(), frame_subst, False)
    parts_on_sheet = []
    # instances
    inst_root = sheet.find("instances")
    for inst in (inst_root.findall("instance") if inst_root is not None else []):
        part = sch.parts.get(inst.get("part", ""))
        if part is None:
            continue
        gate = inst.get("gate", "")
        sym, pads, n_gates = sch.gate_info(part, gate)
        mirror, angle, _ = parse_rot(inst.get("rot"))
        xf = Xform(fl(inst, "x"), fl(inst, "y"), angle, mirror)
        name = sch.display_name(part, gate, n_gates)
        value = sch.display_value(part)
        parts_on_sheet.append(name)
        smashed = inst.get("smashed") == "yes"
        subst = dict(frame_subst)
        subst.update({"NAME": name, "VALUE": value, "PART": part.get("name", ""), "GATE": gate})
        if sym is not None:
            draw_primitives(cv, sym, xf, subst, smashed)
            for pin in sym.findall("pin"):
                draw_pin(cv, pin, xf, pads)
        else:
            cv.text("layer-97", xf.x, xf.y, f"{name}: SYMBOL MISSING", 1.8, 0, None, "#c00000")
        if smashed:
            for at in inst.findall("attribute"):
                key = at.get("name", "").upper()
                if at.get("display") == "off":
                    continue
                txt = subst.get(key, at.get("value", ""))
                if not txt:
                    continue
                _, a, _ = parse_rot(at.get("rot"))
                layer = int(at.get("layer", "95"))
                cv.text(f"layer-{layer}", fl(at, "x"), fl(at, "y"), txt, fl(at, "size", 1.778), a,
                        at.get("align"), color(layer))
    # busses
    busses = sheet.find("busses")
    for bus in (busses.findall("bus") if busses is not None else []):
        for seg in bus.findall("segment"):
            for w in seg.findall("wire"):
                cv.line("layer-92", fl(w, "x1"), fl(w, "y1"), fl(w, "x2"), fl(w, "y2"), max(fl(w, "width", 0.762), 0.6),
                        Style(stroke=color(92)), curve=fl(w, "curve"))
            for lab in seg.findall("label"):
                _, a, _ = parse_rot(lab.get("rot"))
                cv.text("layer-95", fl(lab, "x"), fl(lab, "y"), bus.get("name", ""), fl(lab, "size", 1.778), a, None, color(92))
    # nets
    nets = sheet.find("nets")
    net_names = []
    for net in (nets.findall("net") if nets is not None else []):
        net_names.append(net.get("name", ""))
        for seg in net.findall("segment"):
            for w in seg.findall("wire"):
                cv.line("layer-91", fl(w, "x1"), fl(w, "y1"), fl(w, "x2"), fl(w, "y2"), max(fl(w, "width", 0.1524), 0.2),
                        Style(stroke=color(91)), curve=fl(w, "curve"))
            for j in seg.findall("junction"):
                cv.circle("layer-91", fl(j, "x"), fl(j, "y"), 0.55, 0, Style(stroke="none", fill=color(91)))
            for lab in seg.findall("label"):
                _, a, _ = parse_rot(lab.get("rot"))
                size = fl(lab, "size", 1.778)
                x, y = fl(lab, "x"), fl(lab, "y")
                name = net.get("name", "")
                if lab.get("xref") == "yes":
                    # cross-reference flag: box around the name
                    wbox = len(name) * size * 0.8 + 2
                    import math
                    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                    pts = [(x, y - size * 0.3), (x + wbox, y - size * 0.3), (x + wbox + 1.5, y + size * 0.5),
                           (x + wbox, y + size * 1.3), (x, y + size * 1.3)]
                    pts = [(x + (px - x) * ca - (py - y) * sa, y + (px - x) * sa + (py - y) * ca) for px, py in pts]
                    cv.polygon("layer-95", pts, 0.15, Style(stroke=color(91)))
                    cv.text("layer-95", x + 0.5 * ca, y + 0.5 * sa, name, size, a, None, color(95))
                else:
                    cv.text("layer-95", x, y, name, size, a, None, color(95))
    # title block info
    src_rel = os.path.relpath(sch.path, args.root) if args.root else sch.path
    title = f"{args.project} — {args.board} — Schematic sheet {index}/{total}"
    sub = [
        f"Drawing ID: {args.drawing_id}-S{index}   Revision: {args.rev}   Date: {args.date}   Units: mm   Scale: 1:1 at the stated page size",
        f"Source: {src_rel} (EAGLE {eagle_version(sch.root)} XML; file revision: none recorded in the source)   Status: SOURCE-DERIVED",
        "Generated by tools/render_eagle_schematic.py — documentation rendering of the native EAGLE file; fonts differ from EAGLE vector font.",
    ]
    out = os.path.join(args.out, f"{args.board}_schematic_sheet{index}.svg")
    cv.write(out, title, sub, margin=5.0)
    return {"sheet": index, "file": os.path.basename(out), "parts": len(parts_on_sheet), "nets": len(net_names),
            "width_mm": round(cv.bbox.width() + 10, 1), "height_mm": round(cv.bbox.height() + 10 + 6 + 3.6 * 4, 1)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sch")
    ap.add_argument("--out", required=True)
    ap.add_argument("--board", required=True, help="board name used in file names and title block")
    ap.add_argument("--drawing-id", default="ELEC-SCH")
    ap.add_argument("--rev", default="A")
    ap.add_argument("--project", default="AERIS-10")
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--root", default="", help="repository root for relative source paths")
    ap.add_argument("--index", default="", help="write a JSON index of the sheets")
    args = ap.parse_args()
    try:
        sch = Schematic(args.sch)
    except Exception as exc:  # noqa: BLE001
        print("ERROR:", exc)
        return 1
    os.makedirs(args.out, exist_ok=True)
    total = len(sch.sheets)
    results = []
    for i, sheet in enumerate(sch.sheets, 1):
        r = render_sheet(sch, sheet, i, total, args)
        results.append(r)
        print(f"sheet {i}/{total}: {r['file']}  parts={r['parts']} nets={r['nets']} size={r['width_mm']}x{r['height_mm']} mm")
    if args.index:
        with open(args.index, "w", encoding="utf-8") as fh:
            json.dump({"board": args.board, "source": args.sch, "sheets": results}, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
