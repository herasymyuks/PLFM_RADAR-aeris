#!/usr/bin/env python3
"""PROPOSED DESIGN — 16-row × 8-patch series-fed microstrip array for AERIS-10 (10.5 GHz).

Reads engineering/DESIGN/design_parameters.json, computes first-order patch and
microstrip dimensions (transmission-line model, Hammerstad/Jensen microstrip
formulas), and writes:
  engineering/DESIGN/ANTENNA/kicad/aeris10_patch_array.kicad_pcb   native editable KiCad board
  engineering/DESIGN/ANTENNA/aeris10_patch_array_layout.svg         1:1 drawing with dimensions
  engineering/DESIGN/ANTENNA/ANTENNA_DESIGN_CALC.md                 calculation sheet + status
  engineering/DESIGN/ANTENNA/openems_patch_row.py                   openEMS model of one row (NOT executed here)
Then (if kicad-cli is available) exports Gerber, drill, PDF, SVG, STEP and a 3-D render
into engineering/DESIGN/ANTENNA/kicad_exports/.

First-order formulas only: the design MUST be simulated (openEMS script provided) and
tuned before fabrication.  Status: PROPOSED DESIGN.
Usage: python3 tools/design_antenna_array.py [--no-kicad]
Exit 0 ok, 1 kicad export failed (files still written), 2 error.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_svg_common import SvgCanvas, Style  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSN = os.path.join(ROOT, "engineering", "DESIGN")
OUT = os.path.join(DSN, "ANTENNA")
C0 = 299_792_458.0


def ms_width(z0: float, er: float, h: float) -> float:
    """Microstrip width (mm) for Z0 (Hammerstad)."""
    A = z0 / 60 * math.sqrt((er + 1) / 2) + (er - 1) / (er + 1) * (0.23 + 0.11 / er)
    B = 377 * math.pi / (2 * z0 * math.sqrt(er))
    wh = 8 * math.exp(A) / (math.exp(2 * A) - 2)
    if wh > 2:
        wh = 2 / math.pi * (B - 1 - math.log(2 * B - 1) + (er - 1) / (2 * er) * (math.log(B - 1) + 0.39 - 0.61 / er))
    return wh * h


def ms_eeff(w: float, er: float, h: float) -> float:
    return (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / w)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-kicad", action="store_true")
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    P = json.load(open(os.path.join(DSN, "design_parameters.json")))
    rf = P["rf"]
    f = rf["f_c_hz"]["value"]
    er, h, t_cu = rf["substrate"]["er"], rf["substrate"]["h_mm"], rf["substrate"]["cu_um"] / 1000
    N = rf["n_elements"]["value"]
    pitch = rf["element_pitch_mm"]["value"]
    M = rf["patches_per_row"]["value"]
    lam0 = C0 / f * 1000  # mm
    # --- patch (transmission-line model) ---
    W = lam0 / 2 * math.sqrt(2 / (er + 1))
    eeff_p = ms_eeff(W, er, h)
    dL = 0.412 * h * (eeff_p + 0.3) * (W / h + 0.264) / ((eeff_p - 0.258) * (W / h + 0.8))
    L = lam0 / (2 * math.sqrt(eeff_p)) - 2 * dL
    # edge resistance (Balanis approximation via slot conductance)
    k0 = 2 * math.pi / lam0
    G1 = (W / lam0) ** 2 / 90 if W < 0.35 * lam0 else W / (120 * lam0) - 1 / (60 * math.pi ** 2)
    # mutual conductance (numeric integral)
    import math as m
    def g12():
        s = 0.0
        n = 400
        for i in range(1, n):
            th = m.pi * i / n
            x = k0 * W / 2 * m.cos(th)
            term = (m.sin(x) / x) ** 2 if abs(x) > 1e-9 else 1.0
            # J0 via series
            z = k0 * L * m.sin(th)
            j0 = sum(((-1) ** k) * (z / 2) ** (2 * k) / (m.factorial(k) ** 2) for k in range(0, 25))
            s += term * j0 * m.sin(th) ** 3 * (m.pi / n)
        return s / (120 * m.pi ** 2)
    G12 = g12()
    R_edge = 1 / (2 * (G1 + G12))
    # --- lines ---
    z0 = rf["feed_z0_ohm"]["value"]
    w50 = ms_width(z0, er, h)
    e50 = ms_eeff(w50, er, h)
    lg50 = lam0 / math.sqrt(e50)
    z_link = 100.0
    w_link = ms_width(z_link, er, h)
    e_link = ms_eeff(w_link, er, h)
    lg_link = lam0 / math.sqrt(e_link)
    link_len = lg_link / 2          # 180° between patch edges → patches in phase (patch itself ≈ 180°)
    cc = L + link_len               # centre-to-centre along the row
    # input impedance of M in-phase patches seen through half-wave links ≈ R_edge/M (standing-wave array)
    R_in = R_edge / M
    z_qw = math.sqrt(z0 * R_in)
    w_qw = ms_width(z_qw, er, h)
    e_qw = ms_eeff(w_qw, er, h)
    qw_len = lam0 / math.sqrt(e_qw) / 4
    row_len = M * L + (M - 1) * link_len
    # --- panel geometry ---
    margin_x_left = 22.0   # connector + 50 Ω lead + transformer
    margin_x_right = 8.0
    margin_y = 12.0
    feed50_len = 10.0
    board_w = margin_x_left + feed50_len + qw_len + row_len + margin_x_right
    board_h = (N - 1) * pitch + W + 2 * margin_y
    board_w = math.ceil(board_w)
    board_h = math.ceil(board_h)
    y0 = margin_y + W / 2   # centre of row 1
    x_conn = 0.0
    x_feed_start = margin_x_left
    x_qw_start = x_feed_start + feed50_len
    x_row_start = x_qw_start + qw_len
    hole_d = 3.2
    holes = [(5, 5), (board_w - 5, 5), (5, board_h - 5), (board_w - 5, board_h - 5), (board_w / 2, 5), (board_w / 2, board_h - 5)]
    bw_pct = 3.77 * (er - 1) / er ** 2 * (W / L) * (h / lam0) * 100  # Balanis approx. fractional BW
    # ---------------- KiCad board ----------------
    os.makedirs(os.path.join(OUT, "kicad"), exist_ok=True)
    nets = ['(net 0 "")', '(net 1 "GND")'] + [f'(net {i+2} "ROW{i+1}")' for i in range(N)]
    def poly(layer, pts, net=None):
        p = " ".join(f"(xy {x:.4f} {-y:.4f})" for x, y in pts)   # KiCad Y down
        out = f'(gr_poly (pts {p}) (stroke (width 0) (type solid)) (fill solid) (layer "{layer}") (uuid "{uuid.uuid4()}"))'
        if layer == "F.Cu":   # solder-mask opening over all radiating/feeding copper (bare ENIG, no mask on the patches)
            out += f'\n  (gr_poly (pts {p}) (stroke (width 0) (type solid)) (fill solid) (layer "F.Mask") (uuid "{uuid.uuid4()}"))'
        return out
    def rect(layer, x1, y1, x2, y2, fill=True, width=0.1):
        return (f'(gr_rect (start {x1:.4f} {-y1:.4f}) (end {x2:.4f} {-y2:.4f}) (stroke (width {width}) (type solid)) '
                f'(fill {"solid" if fill else "none"}) (layer "{layer}") (uuid "{uuid.uuid4()}"))')
    def text(layer, x, y, s, size=1.5):
        return (f'(gr_text "{s}" (at {x:.3f} {-y:.3f} 0) (layer "{layer}") (uuid "{uuid.uuid4()}") '
                f'(effects (font (size {size} {size}) (thickness 0.2))))')
    items = []
    # outline
    items.append(rect("Edge.Cuts", 0, 0, board_w, board_h, fill=False, width=0.1))
    # back ground plane (B.Cu) as filled zone
    items.append(f'''(zone (net 1) (net_name "GND") (layer "B.Cu") (uuid "{uuid.uuid4()}") (hatch edge 0.5)
  (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no)
  (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts (xy 0 0) (xy {board_w} 0) (xy {board_w} {-board_h}) (xy 0 {-board_h}))))''')
    for i in range(N):
        yc = y0 + i * pitch
        # 50 Ω feed from connector pad to transformer
        items.append(poly("F.Cu", [(x_conn + 2.0, yc - w50 / 2), (x_qw_start, yc - w50 / 2), (x_qw_start, yc + w50 / 2), (x_conn + 2.0, yc + w50 / 2)]))
        # quarter-wave transformer
        items.append(poly("F.Cu", [(x_qw_start, yc - w_qw / 2), (x_row_start, yc - w_qw / 2), (x_row_start, yc + w_qw / 2), (x_qw_start, yc + w_qw / 2)]))
        # patches + links
        x = x_row_start
        for k in range(M):
            items.append(poly("F.Cu", [(x, yc - W / 2), (x + L, yc - W / 2), (x + L, yc + W / 2), (x, yc + W / 2)]))
            x += L
            if k < M - 1:
                items.append(poly("F.Cu", [(x, yc - w_link / 2), (x + link_len, yc - w_link / 2), (x + link_len, yc + w_link / 2), (x, yc + w_link / 2)]))
                x += link_len
        items.append(text("F.SilkS", x_conn + 6, yc + 3.2, f"ROW{i+1}", 1.2))
        # connector footprint: end-launch 2.92 mm, signal pad + 2 ground pads (generic; verify against the chosen connector)
        fp_uuid = uuid.uuid4()
        items.append(f'''(footprint "AERIS10:EndLaunch_2.92mm_generic" (layer "F.Cu") (uuid "{fp_uuid}") (at 1.0 {-yc:.4f})
  (property "Reference" "J{i+1}" (at 0 -4 0) (layer "F.SilkS") (uuid "{uuid.uuid4()}") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "END-LAUNCH 2.92mm (e.g. Southwest 1092-xx / Amphenol 901-10510) VERIFY" (at 0 4 0) (layer "F.Fab") (uuid "{uuid.uuid4()}") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (attr smd)
  (pad "1" smd rect (at 1.0 0) (size 2.0 {w50:.3f}) (layers "F.Cu" "F.Mask") (net {i+2} "ROW{i+1}") (uuid "{uuid.uuid4()}"))
  (pad "2" smd rect (at 1.0 -3.0) (size 2.0 2.0) (layers "F.Cu" "F.Mask") (net 1 "GND") (uuid "{uuid.uuid4()}"))
  (pad "2" smd rect (at 1.0 3.0) (size 2.0 2.0) (layers "F.Cu" "F.Mask") (net 1 "GND") (uuid "{uuid.uuid4()}"))
  (pad "3" thru_hole circle (at 1.0 -3.0) (size 0.6 0.6) (drill 0.3) (layers "*.Cu" "*.Mask") (net 1 "GND") (uuid "{uuid.uuid4()}"))
  (pad "3" thru_hole circle (at 1.0 3.0) (size 0.6 0.6) (drill 0.3) (layers "*.Cu" "*.Mask") (net 1 "GND") (uuid "{uuid.uuid4()}"))
)''')
    for (hx, hy) in holes:
        items.append(f'''(footprint "MountingHole:MountingHole_3.2mm" (layer "F.Cu") (uuid "{uuid.uuid4()}") (at {hx:.3f} {-hy:.3f})
  (property "Reference" "H" (at 0 -3 0) (layer "F.SilkS") (hide yes) (uuid "{uuid.uuid4()}") (effects (font (size 1 1) (thickness 0.15))))
  (property "Value" "M3" (at 0 3 0) (layer "F.Fab") (hide yes) (uuid "{uuid.uuid4()}") (effects (font (size 1 1) (thickness 0.15))))
  (attr exclude_from_pos_files exclude_from_bom)
  (pad "" np_thru_hole circle (at 0 0) (size {hole_d} {hole_d}) (drill {hole_d}) (layers "*.Cu" "*.Mask") (uuid "{uuid.uuid4()}"))
)''')
    items.append(text("F.SilkS", board_w / 2, board_h - 4, f"AERIS-10 PATCH ARRAY 16x8 10.5GHz DSN-ANT-01 RevA PROPOSED - SIMULATE BEFORE FAB", 1.5))
    items.append(text("Cmts.User", board_w / 2, 4, f"Board {board_w} x {board_h} mm; rows at {pitch} mm pitch; patch {W:.2f} x {L:.2f} mm; link {w_link:.2f} mm wide x {link_len:.2f} mm; QW transformer {w_qw:.2f} x {qw_len:.2f} mm", 1.2))
    pcb = f'''(kicad_pcb (version 20240108) (generator "aeris10_design_antenna_array") (generator_version "1.0")
  (general (thickness {h + 2*t_cu:.3f}) (legacy_teardrops no))
  (paper "A3")
  (title_block (title "AERIS-10 patch array 16x8 — PROPOSED DESIGN") (date "{a.date}") (rev "A") (company "AERIS-10 reconstruction")
    (comment 1 "DSN-ANT-01 generated by tools/design_antenna_array.py from engineering/DESIGN/design_parameters.json")
    (comment 2 "First-order transmission-line design: SIMULATE AND TUNE before fabrication"))
  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments")
    (44 "Edge.Cuts" user) (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard") (48 "B.Fab" user) (49 "F.Fab" user))
  (setup (pad_to_mask_clearance 0.05)
    (stackup (layer "F.SilkS" (type "Top Silk Screen")) (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness {t_cu:.3f})) (layer "dielectric 1" (type "core") (thickness {h}) (material "RO4350B") (epsilon_r {er}) (loss_tangent {rf["substrate"]["tan_d"]}))
      (layer "B.Cu" (type "copper") (thickness {t_cu:.3f})) (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01)) (layer "B.SilkS" (type "Bottom Silk Screen"))
      (copper_finish "ENIG") (dielectric_constraints no))
    (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000) (disableapertmacros no) (usegerberextensions no)
      (usegerberattributes yes) (usegerberadvancedattributes yes) (creategerberjobfile yes) (dashed_line_dash_ratio 12) (dashed_line_gap_ratio 3)
      (svgprecision 4) (plotframeref no) (mode 1) (useauxorigin no) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15) (pdf_front_fp_property_popups yes)
      (pdf_back_fp_property_popups yes) (dxfpolygonmode yes) (dxfimperialunits no) (dxfusepcbnewfont yes) (psnegative no) (psa4output no) (plotreference yes)
      (plotvalue yes) (plotfptext yes) (plotinvisibletext no) (sketchpadsonfab no) (subtractmaskfromsilk no) (outputformat 1) (mirror no) (drillshape 1) (scaleselection 1) (outputdirectory "")))
  {chr(10).join("  " + n for n in nets)}
  {chr(10).join("  " + it for it in items)}
)
'''
    pcb_path = os.path.join(OUT, "kicad", "aeris10_patch_array.kicad_pcb")
    open(pcb_path, "w", encoding="utf-8").write(pcb)
    # ---------------- SVG drawing ----------------
    cv = SvgCanvas()
    g = "antenna"
    cv.group(g)
    cv.polygon(g, [(0, 0), (board_w, 0), (board_w, board_h), (0, board_h)], 0.3, Style(stroke="#000"))
    for (hx, hy) in holes:
        cv.circle(g, hx, hy, hole_d / 2, 0.2, Style(stroke="#b00000"))
    cu = Style(stroke="none", fill="#c8781e", opacity=0.9)
    for i in range(N):
        yc = y0 + i * pitch
        cv.polygon(g, [(2, yc - w50 / 2), (x_qw_start, yc - w50 / 2), (x_qw_start, yc + w50 / 2), (2, yc + w50 / 2)], 0, cu)
        cv.polygon(g, [(x_qw_start, yc - w_qw / 2), (x_row_start, yc - w_qw / 2), (x_row_start, yc + w_qw / 2), (x_qw_start, yc + w_qw / 2)], 0, cu)
        x = x_row_start
        for k in range(M):
            cv.polygon(g, [(x, yc - W / 2), (x + L, yc - W / 2), (x + L, yc + W / 2), (x, yc + W / 2)], 0, cu)
            x += L
            if k < M - 1:
                cv.polygon(g, [(x, yc - w_link / 2), (x + link_len, yc - w_link / 2), (x + link_len, yc + w_link / 2), (x, yc + w_link / 2)], 0, cu)
                x += link_len
        cv.polygon(g, [(0, yc - 4.5), (6, yc - 4.5), (6, yc + 4.5), (0, yc + 4.5)], 0.2, Style(stroke="#1f5f8b", fill="none", dash="1,0.7"))
        cv.text(g, -1.5, yc, f"J{i+1}", 2.0, 0, "center-right", "#1f5f8b", mono=False)
    dim = Style(stroke="#000")
    cv.line(g, 0, board_h + 8, board_w, board_h + 8, 0.2, dim)
    cv.text(g, board_w / 2, board_h + 9.5, f"{board_w:.0f}", 3, 0, "bottom-center", "#000", mono=False)
    cv.line(g, board_w + 8, 0, board_w + 8, board_h, 0.2, dim)
    cv.text(g, board_w + 9.5, board_h / 2, f"{board_h:.0f}", 3, 90, "bottom-center", "#000", mono=False)
    cv.line(g, board_w + 3, y0, board_w + 3, y0 + pitch, 0.2, dim)
    cv.text(g, board_w + 4.5, y0 + pitch / 2, f"{pitch} pitch ×{N-1}", 2.2, 90, "bottom-center", "#000", mono=False)
    cv.line(g, x_row_start, -4, x_row_start + L, -4, 0.2, dim)
    cv.text(g, x_row_start + L / 2, -7.5, f"L={L:.2f}", 2.2, 0, "bottom-center", "#000", mono=False)
    cv.line(g, x_row_start - 3, y0 - W / 2, x_row_start - 3, y0 + W / 2, 0.2, dim)
    cv.text(g, x_row_start - 4.5, y0, f"W={W:.2f}", 2.0, 90, "bottom-center", "#000", mono=False)
    cv.line(g, x_row_start + L, -4, x_row_start + L + link_len, -4, 0.2, dim)
    cv.text(g, x_row_start + L + link_len / 2, -1.5, f"{link_len:.2f}", 2.0, 0, "bottom-center", "#000", mono=False)
    svg_path = os.path.join(OUT, "aeris10_patch_array_layout.svg")
    cv.write(svg_path, "AERIS-10 — 16×8 microstrip patch array, top copper, scale 1:1 — DSN-ANT-01 Rev A — STATUS: PROPOSED DESIGN",
             [f"Date {a.date} · Units mm · f = {f/1e9:.2f} GHz · RO4350B εr {er}, h {h} mm, Cu {rf['substrate']['cu_um']} µm · generated by tools/design_antenna_array.py from design_parameters.json",
              "First-order transmission-line design (Balanis/Hammerstad). Not simulated, not measured. Requires openEMS tuning (openems_patch_row.py) before fabrication. Decisions D-01…D-06 in 00_DESIGN_BASIS.md."],
             margin=12.0)
    # ---------------- calculation sheet ----------------
    hpbw_az = math.degrees(0.886 * lam0 / (M * cc))
    hpbw_el = math.degrees(0.886 * lam0 / (N * pitch))
    D_est = 10 * math.log10(4 * math.pi * (M * cc) * (N * pitch) / lam0 ** 2 * 0.7)  # aperture efficiency 0.7 assumed
    md = f"""# Antenna design calculation sheet — DSN-ANT-01 (PROPOSED DESIGN)

Rev A · {a.date} · generator `tools/design_antenna_array.py` · parameters `engineering/DESIGN/design_parameters.json` · decisions D-01…D-06.

**Status: PROPOSED DESIGN — first-order analytical dimensions. Not simulated, not built, not measured.** The openEMS model `openems_patch_row.py` must be run (openEMS is not installed on the authoring machine) and the patch length/inset and transformer tuned until |S11| < −10 dB over the operating band; then the full 16-row panel must be simulated for mutual coupling before any fabrication.

## 1. Inputs

| Parameter | Value | Basis |
|---|---|---|
| f₀ | {f/1e9:.3f} GHz, λ₀ = {lam0:.3f} mm | VERIFIED |
| Rows (elements) × patches per row | {N} × {M} | VERIFIED / D-03 |
| Row pitch (elevation) | {pitch} mm = {pitch/lam0:.3f} λ₀ | VERIFIED |
| Substrate | RO4350B εr = {er}, tanδ = {rf['substrate']['tan_d']}, h = {h} mm, Cu {rf['substrate']['cu_um']} µm | D-04 |

## 2. Patch (transmission-line model, Balanis ch. 14)

| Quantity | Value |
|---|---|
| Width W = (λ₀/2)·√(2/(εr+1)) | **{W:.3f} mm** |
| εeff (patch) | {eeff_p:.4f} |
| ΔL (fringing) | {dL:.4f} mm |
| Length L = λ₀/(2√εeff) − 2ΔL | **{L:.3f} mm** |
| Slot conductance G1 / mutual G12 | {G1*1e3:.4f} mS / {G12*1e3:.4f} mS |
| Edge resonant resistance R_edge = 1/(2(G1+G12)) | {R_edge:.1f} Ω |
| Fractional bandwidth (VSWR 2, Balanis approx.) | ≈ {bw_pct:.1f} % (≈ {bw_pct/100*f/1e6:.0f} MHz) — chirp bandwidth B is TBD in the parameter table; verify B fits |

## 3. Feed network (per row)

| Element | Z | Width | Length | Note |
|---|---|---|---|---|
| Inter-patch link | {z_link:.0f} Ω | {w_link:.3f} mm | {link_len:.3f} mm (λg/2, εeff {e_link:.3f}) | patches in phase (resonant series feed) |
| Centre-to-centre patch spacing along the row | — | — | {cc:.3f} mm = {cc/lam0:.3f} λ₀ | fixed azimuth beam (no scan along the row) |
| Row input resistance ≈ R_edge/M | {R_in:.1f} Ω | — | — | standing-wave array, in-phase patches |
| Quarter-wave transformer √(50·R_in) | {z_qw:.1f} Ω | {w_qw:.3f} mm | {qw_len:.3f} mm | |
| 50 Ω lead to connector | 50 Ω | {w50:.3f} mm | {feed50_len:.1f} mm (equal on all rows, D-06) | εeff {e50:.3f}, λg {lg50:.2f} mm |

## 4. Panel

| Item | Value |
|---|---|
| Board outline | **{board_w:.0f} × {board_h:.0f} mm** (rows start x = {x_row_start:.2f} mm; row 1 centre y = {y0:.2f} mm) |
| Row length (8 patches + 7 links) | {row_len:.2f} mm |
| Mounting | 6 × Ø{hole_d} mm (M3 inferred) at 5 mm from the edges |
| Connectors | 16 × end-launch 2.92 mm on the left edge at {pitch} mm pitch (body width must be ≤ 12 mm — e.g. Southwest 1092-series, Amphenol 901-10510; **verify footprint**) |
| Estimated HPBW azimuth (row, {M} × {cc:.1f} mm) | ≈ {hpbw_az:.1f}° (uniform) |
| Estimated HPBW elevation ({N} × {pitch} mm) | ≈ {hpbw_el:.1f}° (matches HW-ANT-10: 6.3°) |
| Estimated directivity (aperture {M*cc:.0f} × {N*pitch:.0f} mm, η_ap 0.7 assumed) | ≈ {D_est:.1f} dBi (parameter table says ~20 dBi TBD) |
| Series-feed frequency squint | the row beam tilts with frequency; with B TBD this must be checked in simulation (corporate feed is the fallback, D-02) |

## 5. Files

- Native editable board: `kicad/aeris10_patch_array.kicad_pcb` (KiCad 8+/10; stackup with RO4350B entered)
- Drawing: `aeris10_patch_array_layout.svg` (+ PDF/PNG)
- KiCad exports: `kicad_exports/` (Gerber, drill, PDF, SVG, STEP, 3-D render) — generated with kicad-cli where available
- Simulation model: `openems_patch_row.py` (one row, PEC patches on RO4350B, lumped port at the 50 Ω lead) — NOT executed here

## 6. Slotted-waveguide variant (Extended) — sizing only, CONCEPTUAL

WR-90 (22.86 × 10.16 mm, 8.2–12.4 GHz): λg at 10.5 GHz = λ₀/√(1−(λ₀/2a)²) = {lam0/math.sqrt(1-(lam0/(2*22.86))**2):.2f} mm; resonant longitudinal shunt slots spaced λg/2 = {lam0/math.sqrt(1-(lam0/(2*22.86))**2)/2:.2f} mm, 32 slots per stick → stick length ≈ {32*lam0/math.sqrt(1-(lam0/(2*22.86))**2)/2:.0f} mm; 16 sticks stacked at 14.3 mm cannot fit (WR-90 broad wall 22.86 mm + wall) → the Extended variant needs reduced-height or ridged guide or a 2-row interleave. This is why D-01 selects the patch array for the proposal.

## 7. Verification plan before fabrication

1. Run `openems_patch_row.py` (openEMS ≥ 0.0.36 + python-openEMS): sweep 9.5–11.5 GHz; tune L (±0.3 mm) and `qw_len` until |S11| < −10 dB at 10.5 GHz ± B/2.
2. Simulate 3 adjacent rows for mutual coupling (S21 between row ports < −20 dB target) — affects the ADAR1000 calibration.
3. Fabricate one 3-row coupon; measure S11/S21 on a VNA; compare with simulation; update `design_parameters.json`.
4. Only then release the 16-row panel (`kicad_exports/` Gerbers) and record the result in `engineering/VALIDATION/DRAWING_CHECKS.md`.
"""
    open(os.path.join(OUT, "ANTENNA_DESIGN_CALC.md"), "w", encoding="utf-8").write(md)
    # ---------------- openEMS script (not executed) ----------------
    oe = f'''#!/usr/bin/env python3
"""openEMS model of ONE series-fed row of the AERIS-10 patch array (DSN-ANT-01).
NOT EXECUTED by the generator (openEMS not installed). Requires openEMS + python-openEMS (CSXCAD).
Geometry values come from tools/design_antenna_array.py; edit L_PATCH / QW_LEN to tune.
Usage: python3 openems_patch_row.py  -> writes S11 plot and NF2FF gain to ./openems_out/
"""
import os, numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0

F0 = {f:.0f}; FC = 1.5e9            # centre and half-bandwidth of the Gaussian excitation
ER = {er}; H = {h}e-3; TAND = {rf['substrate']['tan_d']}
W_PATCH = {W:.4f}e-3; L_PATCH = {L:.4f}e-3; N_PATCH = {M}
W_LINK = {w_link:.4f}e-3; L_LINK = {link_len:.4f}e-3
W_QW = {w_qw:.4f}e-3; QW_LEN = {qw_len:.4f}e-3; W50 = {w50:.4f}e-3; L50 = {feed50_len:.1f}e-3
ROW_LEN = N_PATCH*L_PATCH + (N_PATCH-1)*L_LINK
SUB_X = L50 + QW_LEN + ROW_LEN + 20e-3; SUB_Y = 40e-3
unit = 1
FDTD = openEMS(NrTS=300000, EndCriteria=1e-4)
FDTD.SetGaussExcite(F0, FC)
FDTD.SetBoundaryCond(['MUR']*4 + ['PEC', 'MUR'])   # ground plane side PEC
CSX = ContinuousStructure(); FDTD.SetCSX(CSX)
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(unit)
sub = CSX.AddMaterial('RO4350B', epsilon=ER, kappa=2*np.pi*F0*8.854e-12*ER*TAND)
sub.AddBox([0, -SUB_Y/2, -H], [SUB_X, SUB_Y, 0])
cu = CSX.AddMetal('copper')
x = 0.0; yc = 0.0
cu.AddBox([x, yc-W50/2, 0], [x+L50, yc+W50/2, 0]); x += L50
cu.AddBox([x, yc-W_QW/2, 0], [x+QW_LEN, yc+W_QW/2, 0]); x += QW_LEN
for k in range(N_PATCH):
    cu.AddBox([x, yc-W_PATCH/2, 0], [x+L_PATCH, yc+W_PATCH/2, 0]); x += L_PATCH
    if k < N_PATCH-1:
        cu.AddBox([x, yc-W_LINK/2, 0], [x+L_LINK, yc+W_LINK/2, 0]); x += L_LINK
port = FDTD.AddLumpedPort(1, 50, [1e-3, yc-W50/2, -H], [1e-3, yc+W50/2, 0], 'z', 1.0, priority=5, edges2grid='xy')
res = C0/(F0+FC)/np.sqrt(ER)/25
mesh.AddLine('x', np.arange(-15e-3, SUB_X+15e-3, res)); mesh.AddLine('y', np.arange(-SUB_Y/2-15e-3, SUB_Y/2+15e-3, res))
mesh.AddLine('z', np.concatenate((np.linspace(-H, 0, 5), np.arange(0, 20e-3, res))))
mesh.SmoothMeshLines('all', res, 1.4)
nf2ff = FDTD.CreateNF2FFBox()
out = os.path.join(os.getcwd(), 'openems_out'); os.makedirs(out, exist_ok=True)
FDTD.Run(out, cleanup=True)
f = np.linspace(F0-FC, F0+FC, 401); port.CalcPort(out, f)
s11 = port.uf_ref/port.uf_inc
import matplotlib.pyplot as plt
plt.plot(f/1e9, 20*np.log10(np.abs(s11))); plt.grid(); plt.xlabel('GHz'); plt.ylabel('|S11| dB'); plt.savefig(os.path.join(out, 's11_row.png'))
idx = np.argmin(np.abs(s11)); print('best match', f[idx]/1e9, 'GHz', 20*np.log10(abs(s11[idx])), 'dB')
ff = nf2ff.CalcNF2FF(out, f[idx], np.arange(-180, 180, 1), [0, 90]); print('Dmax', 10*np.log10(ff.Dmax[0]), 'dBi')
'''
    open(os.path.join(OUT, "openems_patch_row.py"), "w", encoding="utf-8").write(oe)
    print(f"patch W={W:.3f} L={L:.3f} mm; R_edge={R_edge:.0f} Ω; link {w_link:.3f}x{link_len:.3f}; QW {w_qw:.3f}x{qw_len:.3f}; board {board_w}x{board_h} mm; D≈{D_est:.1f} dBi")
    rc = 0
    if not a.no_kicad:
        kc = None
        for c in [os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"), "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli", shutil.which("kicad-cli")]:
            if c and os.path.exists(c):
                kc = c
                break
        if kc:
            ex = os.path.join(OUT, "kicad_exports")
            os.makedirs(ex, exist_ok=True)
            cmds = [
                [kc, "pcb", "drc", "--format", "report", "--severity-all", "--refill-zones", "--save-board", "-o", f"{ex}/DRC_report.txt", pcb_path],
                [kc, "pcb", "export", "gerbers", "--check-zones", "-l", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,Edge.Cuts", "-o", f"{ex}/gerber/", pcb_path],
                [kc, "pcb", "export", "drill", "--excellon-separate-th", "--generate-map", "-o", f"{ex}/drill/", pcb_path],
                [kc, "pcb", "export", "pdf", "--check-zones", "--mode-single", "-l", "F.Cu,F.SilkS,Edge.Cuts", "--ibt", "-o", f"{ex}/aeris10_patch_array_top.pdf", pcb_path],
                [kc, "pcb", "export", "svg", "--check-zones", "--mode-single", "--page-size-mode", "2", "-l", "F.Cu,Edge.Cuts", "-o", f"{ex}/aeris10_patch_array_F_Cu.svg", pcb_path],
                [kc, "pcb", "export", "step", "--force", "--include-pads", "--include-tracks", "--include-zones", "-o", f"{ex}/aeris10_patch_array.step", pcb_path],
                [kc, "pcb", "export", "stats", "-o", f"{ex}/board_statistics.md", pcb_path],
                [kc, "pcb", "render", "--side", "top", "--background", "opaque", "--quality", "high", "-w", "2400", "-h", "1800", "-o", f"{ex}/aeris10_patch_array_render_top.png", pcb_path],
            ]
            log = []
            for cmd in cmds:
                r = subprocess.run(cmd, capture_output=True, text=True)
                log.append(f"| {a.date} | {' '.join(cmd[1:4])} | {r.returncode} |")
                if r.returncode != 0:
                    rc = 1
                    print("kicad step failed:", " ".join(cmd[1:5]), r.stderr[-300:])
            open(os.path.join(ex, "EXPORT_LOG.md"), "w").write("| date | step | exit |\n|---|---|---|\n" + "\n".join(log) + "\n")
            print("kicad exports:", "ok" if rc == 0 else "with failures")
        else:
            print("kicad-cli not found: exports skipped")
    return rc


if __name__ == "__main__":
    sys.exit(main())
