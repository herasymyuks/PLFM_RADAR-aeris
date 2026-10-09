#!/usr/bin/env python3
"""PROPOSED DESIGN — detailed radar-head enclosure and pedestal (DSN-MECH-06…09), FreeCAD headless.

Builds every mechanical part as its own solid (sheet-metal tray with folded walls and top flanges,
front plate with radome window + louvres, lid, radome window + clamp frame, PA heat-spreader plate
with brackets, board carrier rails + standoffs, cable-entry gland plate, pedestal box with bearing
plate, motor bracket, slip-ring bracket, mast flange) and writes to engineering/DESIGN/MECHANICAL/CAD/detail/:
  aeris10_enclosure_detail.FCStd, aeris10_enclosure_detail.step (assembly), one STEP + STL per part,
  parts_list.json (part, material, thickness, mass estimate, fasteners).
Run:  ~/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tools/design_enclosure_detail_freecad.py').read())"
Status: PROPOSED DESIGN (sheet metal thickness/bend radius per D-08; fastener sizes inferred from the
PCB holes; gaskets/sealing to IP54 target; nothing fabricated).
"""
import json, os, sys, math
HERE = os.path.join(os.getcwd(), "tools")
sys.path.insert(0, HERE)
import design_layout as L
import FreeCAD as App, Part, Mesh, Import

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "engineering", "DESIGN", "MECHANICAL", "CAD", "detail")
os.makedirs(OUT, exist_ok=True)
doc = App.newDocument("AERIS10_enclosure_detail")
V = App.Vector
W, H, D, T = L.W_IN, L.H_IN, L.D_IN, L.WALL
FL = 15.0          # flange width (lid and front-plate flanges)
R_BEND = T         # inside bend radius = thickness (D-08)
DENS = {"Al": 2.70, "PTFE": 2.20, "steel": 7.85, "EPDM": 1.20, "PCB": 1.85, "plastic": 1.2}
parts = []

def box(x, y, z, dx, dy, dz): return Part.makeBox(dx, dy, dz, V(x, y, z))
def cyl(r, h, x, y, z, axis=V(0, 0, 1)): return Part.makeCylinder(r, h, V(x, y, z), axis)
def holes(shape, pts, d, axis=V(0, 0, 1), z0=-50, h=200):
    for (x, y) in pts:
        shape = shape.cut(Part.makeCylinder(d / 2, h, V(x, y, z0) if axis == V(0, 0, 1) else V(x, z0, y), axis))
    return shape
def add(group, label, shape, mat, note="", fasteners=""):
    parts.append((group, label, shape, mat, note, fasteners))

# ------------------------------------------------------------------ HEAD: tray (base + L/R sides + rear, folded) ---
base = box(-T, -T, -T, W + 2 * T, D + 2 * T, T)
base = base.cut(cyl(35, 3 * T, W / 2, L.Y_POWER - 20, -2 * T))                     # Ø70 cable entry
left = box(-T, -T, -T, T, D + 2 * T, H + T)
right = box(W, -T, -T, T, D + 2 * T, H + T)
rear = box(-T, D, -T, W + 2 * T, T, H + T)
# top flanges (inward, for the lid) on L/R/rear; front flanges (inward) on L/R for the front plate
fl_top_l = box(0, 0, H - T, FL, D, T); fl_top_r = box(W - FL, 0, H - T, FL, D, T); fl_top_rr = box(0, D - FL, H - T, W, FL, T)
fl_fr_l = box(0, 0, 0, FL, T, H); fl_fr_r = box(W - FL, 0, 0, FL, T, H)
tray = base.fuse(left).fuse(right).fuse(rear).fuse(fl_top_l).fuse(fl_top_r).fuse(fl_top_rr).fuse(fl_fr_l).fuse(fl_fr_r)
# duct intake slots in the base under the two fin fields
sw = L.FIN["strip_w"]
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    for k in range(6):
        tray = tray.cut(box(sx + 5 + k * 8, L.Y_PLATE_REAR, -2 * T, 4, L.FIN["h"] + 2, 3 * T))
# lid screw holes M4 on top flanges (pitch ~60 mm) and front-plate holes M4 on front flanges
lid_pts = [(FL / 2, y) for y in range(30, int(D) - 20, 60)] + [(W - FL / 2, y) for y in range(30, int(D) - 20, 60)] + [(x, D - FL / 2) for x in range(40, int(W) - 30, 60)]
for (x, y) in lid_pts: tray = tray.cut(cyl(2.2, 3 * T, x, y, H - 2 * T))
front_pts = [(FL / 2, z) for z in range(30, int(H) - 20, 60)] + [(W - FL / 2, z) for z in range(30, int(H) - 20, 60)]
for (x, z) in front_pts: tray = tray.cut(Part.makeCylinder(2.2, 3 * T, V(x, -T - 1, z), V(0, 1, 0)))
# side-wall cut-outs: exhaust louvres near the top of both side ducts (6 slots each)
for sx in (-T, W):
    for k in range(6):
        tray = tray.cut(box(sx - 1, L.Y_PLATE_REAR + 2, H - 60 + k * 8, T + 2, L.FIN["h"] - 4, 4))
add("HEAD", "Tray — base + sides + rear, 2.5 mm Al 5754, 3 bends R2.5, flanges 15 mm with M4 PEM nuts", tray, "Al",
    f"{len(lid_pts)} lid holes M4, {len(front_pts)} front-plate holes M4, Ø70 cable entry, intake slots", f"PEM S-M4-1 ×{len(lid_pts) + len(front_pts)}")
# ------------------------------------------------------------------ front plate with window + louvres ------------
front = box(-T, -T, -T, W + 2 * T, T, H + T)
aw, ah = L.ANT["w"] + 10, L.ANT["h"] + 10
ax, az = L.ANT_POS["x"] - 5, L.ANT_POS["z"] - 5
front = front.cut(box(ax, -T - 1, az, aw, T + 2, ah))
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    for k in range(5):
        front = front.cut(box(sx + 6, -T - 1, 12 + k * 8, sw - 12, T + 2, 4))        # intake louvres (fan side)
for (x, z) in front_pts: front = front.cut(Part.makeCylinder(2.2, 3 * T, V(x, -T - 1, z), V(0, 1, 0)))
# window clamp-frame holes M3 around the window (pitch ≈ 50 mm)
win_pts = [(ax - 6, z) for z in range(int(az) - 6, int(az + ah) + 7, 50)] + [(ax + aw + 6, z) for z in range(int(az) - 6, int(az + ah) + 7, 50)] + \
          [(x, az - 6) for x in range(int(ax) + 44, int(ax + aw) - 40, 50)] + [(x, az + ah + 6) for x in range(int(ax) + 44, int(ax + aw) - 40, 50)]
for (x, z) in win_pts: front = front.cut(Part.makeCylinder(1.7, 3 * T, V(x, -T - 1, z), V(0, 1, 0)))
add("HEAD", "Front plate 2.5 mm Al with radome window opening and intake louvres", front, "Al", f"window {aw:.0f}×{ah:.0f}, {len(win_pts)} M3 clamp holes", f"M4×8 ×{len(front_pts)} to tray front flanges")
# ------------------------------------------------------------------ radome window, gasket, clamp frame ----------
win = box(ax - 12, -T - 2.0, az - 12, aw + 24, 2.0, ah + 24)
for (x, z) in win_pts: win = win.cut(Part.makeCylinder(1.7, 10, V(x, -T - 5, z), V(0, 1, 0)))
add("HEAD", "Radome window PTFE 2 mm (outside the front plate)", win, "PTFE", "RF loss ≈ 0.1 dB at 10.5 GHz (PTFE εr 2.1, tanδ 0.0002 — to be confirmed)", "")
gasket = box(ax - 12, -T - 3.5, az - 12, aw + 24, 1.5, ah + 24).cut(box(ax - 2, -T - 4, az - 2, aw + 4, 3, ah + 4))
add("HEAD", "Window gasket EPDM 1.5 mm (ring 10 mm)", gasket, "EPDM", "", "")
frame = box(ax - 14, -T - 5.5, az - 14, aw + 28, 2.0, ah + 28).cut(box(ax, -T - 6, az, aw, 4, ah))
for (x, z) in win_pts: frame = frame.cut(Part.makeCylinder(1.7, 10, V(x, -T - 7, z), V(0, 1, 0)))
add("HEAD", "Window clamp frame 2 mm Al, 14 mm wide", frame, "Al", "", f"M3×10 ×{len(win_pts)} + nyloc")
# ------------------------------------------------------------------ lid + gasket ---------------------------------
lid = box(-T, -T, H, W + 2 * T, D + 2 * T, T)
for (x, y) in lid_pts: lid = lid.cut(cyl(2.2, 3 * T, x, y, H - T))
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    for k in range(6):
        lid = lid.cut(box(sx + 5 + k * 8, L.Y_PLATE_REAR, H - 1, 4, L.FIN["h"] + 2, T + 2))     # exhaust slots
add("HEAD", "Lid 2.5 mm Al with exhaust slots", lid, "Al", "", f"M4×8 ×{len(lid_pts)}")
lg = box(0, 0, H - T, W, D, 3.0).cut(box(FL, FL, H - T - 1, W - 2 * FL, D - 2 * FL, 5))
add("HEAD", "Lid gasket EPDM 3 mm self-adhesive, 15 mm wide on the flanges", lg, "EPDM", "compressed to 2 mm → IP54 target", "")
# ------------------------------------------------------------------ PA plate + brackets ---------------------------
plate = box(L.PLATE_POS["x"], L.Y_PLATE, L.PLATE_POS["z"], L.PLATE["w"], L.PLATE["t"], L.PLATE["h"])
nf = int(sw // L.FIN["pitch"]); z0 = L.PLATE_POS["z"] + (L.PLATE["h"] - L.FIN["len"]) / 2
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - sw):
    for i in range(nf):
        plate = plate.fuse(box(sx + i * L.FIN["pitch"] + (L.FIN["pitch"] - L.FIN["t"]) / 2, L.Y_PLATE_REAR, z0, L.FIN["t"], L.FIN["h"], L.FIN["len"]))
pa_h = []   # PA board holes (from RF_PA_dimensions: 7 per board, use the 4 corners + 3 mid approximated by the PCB file)
import csv
def board_holes(board):
    p = os.path.join(ROOT, "engineering", "MECHANICAL", "dimensions", f"{board}_dimensions.md"); out = []
    for line in open(p):
        if line.startswith("| ") and "mm" not in line:
            c = [x.strip() for x in line.strip("|\n").split("|")]
            try:
                if float(c[3]) >= 2.0: out.append((float(c[1]), float(c[2])))
            except (ValueError, IndexError): pass
    return out
pa_holes = board_holes("RF_PA")
for (px, pz) in L.pa_positions():
    for (hx, hy) in pa_holes:
        plate = plate.cut(Part.makeCylinder(1.25, 8, V(px + hx, L.Y_PLATE_REAR - 7.9, pz + hy), V(0, 1, 0)))   # M3 tapped, rear face
ant_holes = [(5, 5), (160, 5), (5, 243), (160, 243), (82.5, 5), (82.5, 243)]
for (hx, hy) in ant_holes:
    plate = plate.cut(Part.makeCylinder(1.25, 8, V(L.ANT_POS["x"] + hx, L.Y_PLATE - 0.1, L.ANT_POS["z"] + hy), V(0, 1, 0)))
add("HEAD", "PA heat spreader 300×300×10 Al 6061, machined fin fields, M3 tapped (16×7 PA + 6 antenna)", plate.removeSplitter(), "Al",
    "thermal pads 5×5 under each QPA2962; antenna on 2.4 mm nylon spacers", "M3×6 ×118 (PA 112 + antenna 6)")
for sx in (L.PLATE_POS["x"], L.PLATE_POS["x"] + L.PLATE["w"] - 25):
    for zz in (20, H - 45):
        br = box(sx, L.Y_PLATE - 25, zz, 25, 25 + L.PLATE["t"], 25).cut(box(sx + 3, L.Y_PLATE - 22, zz - 1, 25, 22, 27))
        add("HEAD", f"Plate bracket L 25×25×3 Al at x={sx:.0f} z={zz}", br, "Al", "bolts the plate to the side wall and to the front flange", "M5×12 ×2 + M5×16 ×1")
# ------------------------------------------------------------------ board carrier rails + standoffs --------------
sp = L.synth_pos()
tiers = [("Main Board", L.Y_MAIN, L.MAIN_POS, "MAIN_BOARD"), ("Synth", L.Y_SYNTH, sp, "FREQUENCY_SYNTHESIZER"), ("Power Board", L.Y_POWER, L.POWER_POS, "POWER_SUPPLY")]
for name, y, pos, bname in tiers:
    bw = L.B[bname]["w"]; bh = L.B[bname]["h"]
    hs = board_holes(bname)
    for zz, lab in ((pos["z"] - 10, "bottom"), (pos["z"] + bh - 5, "top")):
        rail = box(pos["x"] - 10, y - 12, zz, bw + 20, 12, 15).cut(box(pos["x"] - 9, y - 10.5, zz + 1.5, bw + 18, 12, 12))   # U 12×15×1.5
        add("HEAD", f"{name} carrier rail {lab} U15×12×1.5 Al, {bw + 20:.0f} mm", rail, "Al", "bolted to the side walls (M4) — spans the full width when the board is narrower", "M4×8 ×2")
    for (hx, hy) in hs:
        so = cyl(3.0, 10, pos["x"] + hx, y - 10, pos["z"] + hy, V(0, 1, 0))
        add("HEAD", f"{name} standoff M3×10 hex at ({hx:.0f},{hy:.0f})", so, "steel", "", "M3×6 ×1")
# ------------------------------------------------------------------ cable entry gland plate -----------------------
gp = box(W / 2 - 50, L.Y_POWER - 20 - 50, -T - 2, 100, 100, 2).cut(cyl(16, 10, W / 2 - 20, L.Y_POWER - 20, -T - 5)).cut(cyl(10, 10, W / 2 + 25, L.Y_POWER - 20, -T - 5))
add("HEAD", "Cable-entry gland plate 100×100×2 Al under the base (M32 + M20 glands)", gp, "Al", "harness from the slip ring: VIN, 22 V, USB", "M4×8 ×4; glands M32 + M20 IP68")
# ------------------------------------------------------------------ PEDESTAL -----------------------------------------
P = L.PEDESTAL
cx, cy = W / 2, L.Y_POWER - 20
zt = -T - P["turntable_t"]
tt = cyl(P["turntable_d"] / 2, P["turntable_t"], cx, cy, zt).cut(cyl(35, 20, cx, cy, zt - 5))
tt = holes(tt, [(cx + 150 * math.cos(math.radians(a)), cy + 150 * math.sin(math.radians(a))) for a in range(0, 360, 45)], 6.5, z0=zt - 5, h=20)
tt = holes(tt, [(cx + (P["bearing_od"] / 2 - 10) * math.cos(math.radians(a)), cy + (P["bearing_od"] / 2 - 10) * math.sin(math.radians(a))) for a in range(0, 360, 30)], 6.5, z0=zt - 5, h=20)
add("PEDESTAL", "Turntable plate Ø340×8 Al, 8×M6 to the head base, 12×M6 to the bearing outer ring", tt, "Al", "", "M6×16 ×8, M6×25 ×12")
zb = zt - P["bearing_t"]
add("PEDESTAL", "Slewing bearing OD190/ID100×20 (4-point contact, e.g. igus PRT-04-100 class)", cyl(P["bearing_od"] / 2, P["bearing_t"], cx, cy, zb).cut(cyl(P["bearing_id"] / 2, P["bearing_t"] + 2, cx, cy, zb - 1)), "steel", "part number to be selected (axial ≥ 50 kg, moment ≥ 60 N·m)", "")
rp = cyl(P["ring_pulley_d"] / 2, P["ring_pulley_t"], cx, cy, zb + 4).cut(cyl(P["bearing_od"] / 2 + 1, P["ring_pulley_t"] + 2, cx, cy, zb + 3))
add("PEDESTAL", f"Ring pulley GT3 {P['ring_teeth']}T Ø{P['ring_pulley_d']:.0f} Al (machined/3D-printed), clamped under the turntable", rp, "Al", "", "M4×10 ×6")
top = box(cx - P["base_w"] / 2, cy - P["base_d"] / 2, zb - 5, P["base_w"], P["base_d"], 5).cut(cyl(P["bearing_id"] / 2 - 5, 20, cx, cy, zb - 10))
top = holes(top, [(cx + (P["bearing_id"] / 2 + 8) * math.cos(math.radians(a)), cy + (P["bearing_id"] / 2 + 8) * math.sin(math.radians(a))) for a in range(15, 360, 30)], 6.5, z0=zb - 10, h=20)
add("PEDESTAL", "Pedestal top plate 360×360×5 Al, 12×M6 to the bearing inner ring, bore Ø90", top, "Al", "", "M6×20 ×12")
box_out = box(cx - P["base_w"] / 2, cy - P["base_d"] / 2, zb - 5 - P["base_h"], P["base_w"], P["base_d"], P["base_h"])
box_in = box(cx - P["base_w"] / 2 + T, cy - P["base_d"] / 2 + T, zb - 5 - P["base_h"] - 1, P["base_w"] - 2 * T, P["base_d"] - 2 * T, P["base_h"])
pbox = box_out.cut(box_in)
pbox = pbox.cut(box(cx + P["base_w"] / 2 - 60, cy - P["base_d"] / 2 - 1, zb - 5 - P["base_h"] + 30, 50, T + 2, 60))   # connector panel opening
add("PEDESTAL", "Pedestal housing 360×360×125 folded 2.5 mm Al (4 bends), open top, connector panel cut-out", pbox, "Al", "DC input (XT60/M12), USB-B bulkhead, vent", "M5×10 ×12 to the top plate")
mx = cx + P["ring_pulley_d"] / 2 + P["motor_pulley_d"] / 2 + 25
add("PEDESTAL", "Stepper NEMA 23 76 mm", box(mx - 28.2, cy - 28.2, zb - 5 - 20 - 76, 56.4, 56.4, 76), "steel", "", "M5×12 ×4")
mb = box(mx - 40, cy - 40, zb - 5 - 20 - 3, 80, 80, 3).cut(cyl(19.5, 10, mx, cy, zb - 30))
mb = holes(mb, [(mx + 23.6, cy + 23.6), (mx - 23.6, cy + 23.6), (mx + 23.6, cy - 23.6), (mx - 23.6, cy - 23.6)], 5.5, z0=zb - 30, h=10)
add("PEDESTAL", "Motor bracket 80×80×3 Al with slotted belt-tension holes", mb, "Al", "slots ±5 mm for GT3 tension", "M5×10 ×4 to the top plate")
add("PEDESTAL", f"Motor pulley GT3 {P['motor_teeth']}T Ø{P['motor_pulley_d']:.0f}, bore 6.35", cyl(P["motor_pulley_d"] / 2, P["ring_pulley_t"], mx, cy, zb + 4), "Al", "", "grub M4 ×2")
add("PEDESTAL", "Through-bore slip ring Ø99×60, bore 60, 12 circuits (4×10 A, 4×10 A, 4 signal)", cyl(P["slip_ring_od"] / 2, P["slip_ring_len"], cx, cy, zb - 35).cut(cyl(30, P["slip_ring_len"] + 2, cx, cy, zb - 36)), "plastic", "e.g. Senring H3899 class — select", "")
sb = box(cx - 70, cy - 70, zb - 5 - 45, 140, 140, 3).cut(cyl(50, 10, cx, cy, zb - 55))
add("PEDESTAL", "Slip-ring stator bracket 140×140×3 Al", sb, "Al", "stator fixed to the pedestal, rotor flange to the turntable", "M4×8 ×4")
add("PEDESTAL", "Stepper driver TB6600 on DIN rail", box(cx - 150, cy + 80, zb - 5 - P["base_h"] + T + 2, 96, 72, 36), "plastic", "", "")
mf = cyl(75, 10, cx, cy, zb - 5 - P["base_h"] - 10)
mf = holes(mf, [(cx + 55 * math.cos(math.radians(a)), cy + 55 * math.sin(math.radians(a))) for a in (45, 135, 225, 315)], 10.5, z0=zb - 5 - P["base_h"] - 15, h=20)
add("PEDESTAL", "Mast flange Ø150×10 steel, 4×M10 PCD 110 (ASSUMPTION — mast interface undefined)", mf, "steel", "", "M10×30 ×4")
# ------------------------------------------------------------------ document, exports, masses ---------------------
grp = {}; objs = {"HEAD": [], "PEDESTAL": []}; plist = []
for g, label, shape, mat, note, fast in parts:
    if g not in grp: grp[g] = doc.addObject("App::Part", g)
    o = doc.addObject("Part::Feature", label[:40].replace(" ", "_")); o.Label = label; o.Shape = shape; grp[g].addObject(o); objs[g].append(o)
    m = shape.Volume / 1000.0 * DENS[mat]
    plist.append({"group": g, "part": label, "material": mat, "mass_g_estimate": round(m, 1), "note": note, "fasteners": fast})
doc.recompute()
doc.saveAs(os.path.join(OUT, "aeris10_enclosure_detail.FCStd"))
allobjs = objs["HEAD"] + objs["PEDESTAL"]
Import.export(allobjs, os.path.join(OUT, "aeris10_enclosure_detail.step"))
Import.export(objs["HEAD"], os.path.join(OUT, "aeris10_head_detail.step"))
Import.export(objs["PEDESTAL"], os.path.join(OUT, "aeris10_pedestal_detail.step"))
Mesh.export(objs["HEAD"], os.path.join(OUT, "aeris10_head_detail.stl")); Mesh.export(objs["PEDESTAL"], os.path.join(OUT, "aeris10_pedestal_detail.stl"))
shell = [o for o in objs["HEAD"] if o.Label.startswith(("Tray", "Front plate", "Lid 2.5", "Radome", "Window"))]
Mesh.export(shell, os.path.join(OUT, "aeris10_head_shell_detail.stl")); Mesh.export([o for o in objs["HEAD"] if o not in shell], os.path.join(OUT, "aeris10_head_internals_detail.stl"))
os.makedirs(os.path.join(OUT, "parts"), exist_ok=True)
for o in allobjs:
    Import.export([o], os.path.join(OUT, "parts", o.Name + ".step"))
json.dump({"parts": plist, "mass_head_g": round(sum(p["mass_g_estimate"] for p in plist if p["group"] == "HEAD")), "mass_pedestal_g": round(sum(p["mass_g_estimate"] for p in plist if p["group"] == "PEDESTAL")),
           "note": "volume × density estimates; sheet parts modelled as solids without bend reliefs; stepper 1.1 kg included as steel box"}, open(os.path.join(OUT, "parts_list.json"), "w"), indent=2)
print("detail model:", len(parts), "parts; head", round(sum(p["mass_g_estimate"] for p in plist if p["group"] == "HEAD") / 1000, 1), "kg; pedestal", round(sum(p["mass_g_estimate"] for p in plist if p["group"] == "PEDESTAL") / 1000, 1), "kg")
