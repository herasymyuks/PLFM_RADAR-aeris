#!/usr/bin/env python3
"""PROPOSED DESIGN — parametric 3-D model of the AERIS-10 radar head and pedestal in FreeCAD.

Run with FreeCAD's Python (headless):
  ~/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tools/design_mechanical_freecad.py').read())"
or:  freecadcmd tools/design_mechanical_freecad.py   (Linux/Windows: FreeCADCmd)
Reads tools/design_layout.py (which reads engineering/DESIGN/design_parameters.json) and writes to
engineering/DESIGN/MECHANICAL/CAD/:
  aeris10_head_pedestal.FCStd      native editable FreeCAD document (one Part::Feature per part, grouped)
  aeris10_head_pedestal.step       STEP AP214 assembly (all parts)
  aeris10_head_only.step, aeris10_pedestal_only.step, STL per group
  aeris10_mass_table.json          volumes × assumed densities (ESTIMATE)
  aeris10_orthographic.dxf         TechDraw page (front/top/side/iso) if TechDraw works headless
Status: PROPOSED DESIGN — decisions D-07…D-13; antenna/PA geometry verified, everything else proposed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "tools")
if not os.path.isdir(HERE):
    HERE = os.path.join(os.getcwd(), "tools")
sys.path.insert(0, HERE)
import design_layout as L  # noqa: E402

import FreeCAD as App  # noqa: E402
import Part  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "engineering", "DESIGN", "MECHANICAL", "CAD")
os.makedirs(OUT, exist_ok=True)
doc = App.newDocument("AERIS10_head_pedestal")
V = App.Vector
parts = []   # (group, label, shape, material, density g/cm3)
DENS = {"Al": 2.70, "PCB": 1.85, "PTFE": 2.20, "steel": 7.85, "plastic": 1.20, "Cu": 8.9}


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))


def cyl(r, h, x, y, z, axis=V(0, 0, 1)):
    return Part.makeCylinder(r, h, V(x, y, z), axis)


def add(group, label, shape, material):
    parts.append((group, label, shape, material))


W, H, D, T = L.W_IN, L.H_IN, L.D_IN, L.WALL
# ---------------- HEAD: chassis (open top) + lid ----------------
outer = box(-T, -T, -T, W + 2 * T, D + 2 * T, H + T)       # no top (lid separate)
inner = box(0, 0, 0, W, D, H + 2)
chassis = outer.cut(inner)
# radome window in the front wall
aw, ah = L.ANT["w"] + 10, L.ANT["h"] + 10
ax, az = L.ANT_POS["x"] - 5, L.ANT_POS["z"] - 5
chassis = chassis.cut(box(ax, -T - 1, az, aw, T + 2, ah))
# duct intake (bottom wall) and exhaust (top is the lid) slots in the two side strips, between plate rear and PA tier end
sw = L.FIN["strip_w"]
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    chassis = chassis.cut(box(sx + 5, L.Y_PLATE_REAR, -T - 1, sw - 10, L.FIN["h"] + 2, T + 2))
# slip-ring / cable passage in the base plate (Ø 70) under the Power Board
chassis = chassis.cut(cyl(35, T + 2, W / 2, L.Y_POWER - 20, -T - 1))
add("HEAD", "Chassis (2.5 mm Al, folded)", chassis, "Al")
lid = box(-T, -T, H, W + 2 * T, D + 2 * T, T)
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    lid = lid.cut(box(sx + 5, L.Y_PLATE_REAR, H - 1, sw - 10, L.FIN["h"] + 2, T + 2))
add("HEAD", "Lid (2.5 mm Al)", lid, "Al")
add("HEAD", "Radome window (PTFE 2 mm)", box(ax, -T, az, aw, 2.0, ah), "PTFE")
# ---------------- antenna panel ----------------
add("HEAD", "Antenna panel PCB 16x8 patches (RO4350B 0.508 + Cu)", box(L.ANT_POS["x"], L.Y_ANT, L.ANT_POS["z"], L.ANT["w"], L.ANT["t"], L.ANT["h"]), "PCB")
# ---------------- heat spreader with fins ----------------
plate = box(L.PLATE_POS["x"], L.Y_PLATE, L.PLATE_POS["z"], L.PLATE["w"], L.PLATE["t"], L.PLATE["h"])
nf = int(sw // L.FIN["pitch"])
z0 = L.PLATE_POS["z"] + (L.PLATE["h"] - L.FIN["len"]) / 2
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    for i in range(nf):
        fx = sx + i * L.FIN["pitch"] + (L.FIN["pitch"] - L.FIN["t"]) / 2
        plate = plate.fuse(box(fx, L.Y_PLATE_REAR, z0, L.FIN["t"], L.FIN["h"], L.FIN["len"]))
add("HEAD", "PA heat spreader 300x300x10 Al with 2 fin fields", plate.removeSplitter(), "Al")
# ---------------- PA boards ----------------
pw, ph = L.B["RF_PA"]["w"], L.B["RF_PA"]["h"]
for i, (px, pz) in enumerate(L.pa_positions(), 1):
    add("HEAD", f"RF PA board PA{i} (35x60)", box(px, L.Y_PA, pz, pw, 1.6, ph), "PCB")
    add("HEAD", f"PA{i} component envelope", box(px + 3, L.Y_PA + 1.6, pz + 5, pw - 6, 10, ph - 10), "plastic")
# ---------------- Main / Synth / Power boards ----------------
mb = L.B["MAIN_BOARD"]
add("HEAD", "Main Board (260x300, vertical)", box(L.MAIN_POS["x"], L.Y_MAIN, L.MAIN_POS["z"], mb["w"], 1.6, mb["h"]), "PCB")
add("HEAD", "Main Board component envelope (15 mm, ASSUMED)", box(L.MAIN_POS["x"] + 5, L.Y_MAIN + 1.6, L.MAIN_POS["z"] + 5, mb["w"] - 10, L.B["component_height_top_mm"]["value"], mb["h"] - 10), "plastic")
sp = L.synth_pos()
sb = L.B["FREQUENCY_SYNTHESIZER"]
add("HEAD", "Frequency Synthesizer (100x100, vertical)", box(sp["x"], L.Y_SYNTH, sp["z"], sb["w"], 1.6, sb["h"]), "PCB")
add("HEAD", "Synth component envelope", box(sp["x"] + 3, L.Y_SYNTH + 1.6, sp["z"] + 3, sb["w"] - 6, 12, sb["h"] - 6), "plastic")
pb = L.B["POWER_SUPPLY"]
add("HEAD", "Power Board (280x300, vertical)", box(L.POWER_POS["x"], L.Y_POWER, L.POWER_POS["z"], pb["w"], 1.6, pb["h"]), "PCB")
add("HEAD", "Power Board component envelope (15 mm, ASSUMED)", box(L.POWER_POS["x"] + 5, L.Y_POWER + 1.6, L.POWER_POS["z"] + 5, pb["w"] - 10, L.B["component_height_top_mm"]["value"], pb["h"] - 10), "plastic")
# fans at the bottom of the two ducts
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    add("HEAD", "Fan 60x60x15 (duct intake)", box(sx - 2, L.Y_PLATE_REAR - 2, 0, 59, 29, 15), "plastic")
# 22 V PA supply/switch module (proposed, 120 x 80 x 25) on the rear wall beside the Power Board bottom
add("HEAD", "22 V PA supply + gate module (DSN-PSU-01, 120x80)", box(W - 130, L.Y_POWER + 1.6, 220, 120, 20, 80), "PCB")
# ---------------- PEDESTAL ----------------
P = L.PEDESTAL
cx, cy = W / 2, L.Y_POWER - 20          # rotation axis under the slip-ring passage
add("PEDESTAL", "Turntable plate Ø340x8 Al (bolted to the head base)", cyl(P["turntable_d"] / 2, P["turntable_t"], cx, cy, -T - P["turntable_t"]).cut(cyl(35, 20, cx, cy, -T - P["turntable_t"] - 5)), "Al")
zb = -T - P["turntable_t"] - P["bearing_t"]
add("PEDESTAL", "Slewing bearing OD190/ID100x20 (steel)", cyl(P["bearing_od"] / 2, P["bearing_t"], cx, cy, zb).cut(cyl(P["bearing_id"] / 2, P["bearing_t"] + 2, cx, cy, zb - 1)), "steel")
add("PEDESTAL", f"Ring pulley GT3 {P['ring_teeth']}T Ø{P['ring_pulley_d']} (Al, on the turntable)", cyl(P["ring_pulley_d"] / 2, P["ring_pulley_t"], cx, cy, zb + 4).cut(cyl(P["bearing_od"] / 2 + 1, P["ring_pulley_t"] + 2, cx, cy, zb + 3)), "Al")
add("PEDESTAL", "Through-bore slip ring Ø99x60, 12 circuits", cyl(P["slip_ring_od"] / 2, P["slip_ring_len"], cx, cy, zb - 30).cut(cyl(30, P["slip_ring_len"] + 2, cx, cy, zb - 31)), "plastic")
zbase_top = zb
zbase_bot = zb - P["base_h"]
base_out = box(cx - P["base_w"] / 2, cy - P["base_d"] / 2, zbase_bot, P["base_w"], P["base_d"], P["base_h"])
base_in = box(cx - P["base_w"] / 2 + T, cy - P["base_d"] / 2 + T, zbase_bot + T, P["base_w"] - 2 * T, P["base_d"] - 2 * T, P["base_h"] - 2 * T)
base = base_out.cut(base_in).cut(cyl(P["bearing_id"] / 2 - 5, T + 2, cx, cy, zbase_top - T - 1))
add("PEDESTAL", "Pedestal housing 360x360x130 (2.5 mm Al)", base, "Al")
# stepper + pulley + belt (belt as a thin ring approximation)
mx = cx + P["ring_pulley_d"] / 2 + P["motor_pulley_d"] / 2 + 25
add("PEDESTAL", "Stepper NEMA 23 (56.4x56.4x76)", box(mx - 28.2, cy - 28.2, zbase_top - 20 - 76, 56.4, 56.4, 76), "steel")
add("PEDESTAL", f"Motor pulley GT3 {P['motor_teeth']}T", cyl(P["motor_pulley_d"] / 2, P["ring_pulley_t"], mx, cy, zb + 4), "Al")
add("PEDESTAL", "Stepper driver TB6600 (96x72x36)", box(cx - 150, cy + 80, zbase_bot + T + 2, 96, 72, 36), "plastic")
add("PEDESTAL", "Mast flange Ø150x10, 4xM10 PCD110 (ASSUMPTION)", cyl(75, 10, cx, cy, zbase_bot - 10), "steel")
# ---------------- build document ----------------
groups = {}
mass = {}
objs_by_group = {"HEAD": [], "PEDESTAL": []}
for g, label, shape, mat in parts:
    if g not in groups:
        groups[g] = doc.addObject("App::Part", g)
    o = doc.addObject("Part::Feature", label.replace(" ", "_")[:60])
    o.Label = label
    o.Shape = shape
    groups[g].addObject(o)
    objs_by_group[g].append(o)
    m = shape.Volume / 1000.0 * DENS[mat]  # g
    mass.setdefault(g, 0.0)
    mass[g] += m
    mass[label] = round(m, 1)
doc.recompute()
fc = os.path.join(OUT, "aeris10_head_pedestal.FCStd")
doc.saveAs(fc)
import Import  # noqa: E402
allobjs = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
Import.export(allobjs, os.path.join(OUT, "aeris10_head_pedestal.step"))
Import.export(objs_by_group["HEAD"], os.path.join(OUT, "aeris10_head_only.step"))
Import.export(objs_by_group["PEDESTAL"], os.path.join(OUT, "aeris10_pedestal_only.step"))
import Mesh  # noqa: E402
for g in ("HEAD", "PEDESTAL"):
    Mesh.export(objs_by_group[g], os.path.join(OUT, f"aeris10_{g.lower()}.stl"))
shell = [o for o in objs_by_group["HEAD"] if o.Label.startswith(("Chassis", "Lid", "Radome"))]
Mesh.export(shell, os.path.join(OUT, "aeris10_head_shell.stl"))
Mesh.export([o for o in objs_by_group["HEAD"] if o not in shell], os.path.join(OUT, "aeris10_head_internals.stl"))
mass["_note"] = "grams; volume x assumed density (Al 2.70, PCB 1.85, PTFE 2.20, steel 7.85, plastic envelopes 1.20); component envelopes are NOT real masses — ESTIMATE only"
mass["_stepper_fixed_g"] = 1100
json.dump(mass, open(os.path.join(OUT, "aeris10_mass_table.json"), "w"), indent=2)
# ---------------- TechDraw page (DXF) ----------------
try:
    import TechDraw  # noqa: E402
    page = doc.addObject("TechDraw::DrawPage", "Page")
    tmpl = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
    tdir = os.path.join(App.getResourceDir(), "Mod", "TechDraw", "Templates")
    cand = []
    for sub in ("ISO", "ANSI", ""):
        d = os.path.join(tdir, sub)
        if os.path.isdir(d):
            cand += [os.path.join(d, f) for f in sorted(os.listdir(d)) if "A2" in f and "andscape" in f and f.endswith(".svg")]
    if not cand:
        for sub in ("ISO", ""):
            d = os.path.join(tdir, sub)
            if os.path.isdir(d):
                cand += [os.path.join(d, f) for f in sorted(os.listdir(d)) if "andscape" in f and f.endswith(".svg")]
    tmpl.Template = cand[0]
    page.Template = tmpl
    pg = doc.addObject("TechDraw::DrawProjGroup", "Views")
    page.addView(pg)
    pg.Source = allobjs
    pg.ScaleType = "Custom"
    pg.Scale = 0.2
    pg.addProjection("Front")
    pg.addProjection("Top")
    pg.addProjection("Right")
    pg.addProjection("FrontTopRight")
    pg.Anchor.Direction = V(0, -1, 0)   # look at the antenna
    doc.recompute()
    TechDraw.writeDXFPage(page, os.path.join(OUT, "aeris10_orthographic.dxf"))
    doc.save()
    print("TechDraw DXF page written")
except Exception as exc:  # noqa: BLE001
    print("TechDraw page skipped:", exc)
print("FreeCAD outputs written to", OUT, "| head mass est. g:", round(mass["HEAD"]), "pedestal g:", round(mass["PEDESTAL"]))
