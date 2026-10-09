#!/usr/bin/env python3
"""Generate the per-board manufacturing-package README (engineering/PCB/<BOARD>/README.md),
copy the schematic-derived BOM next to the exports, and write the EAGLE↔KiCad cross-check
(engineering/VALIDATION/PCB_CROSS_CHECK.md).

Reads: the EAGLE .brd (XML), KiCad outputs produced by tools/kicad_pcb_pipeline.sh
(reports/kicad_import_report.txt, reports/board_statistics.md, reports/DRC_report.json,
drill/drill_report.txt) and docs/BOM/BOM_<BOARD>.csv.
Usage: python3 tools/gen_engineering_pcb_docs.py [--board NAME] [--date YYYY-MM-DD]
Exit codes: 0 all cross-checks consistent, 1 a cross-check mismatch or a missing export, 2 error.
Stdlib only, non-destructive (writes only README.md, STACKUP.md, assembly/<BOARD>_BOM.csv and the cross-check file).
"""
from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import math
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH_DIR = os.path.join(ROOT, "4_Schematics and Boards Layout", "4_6_Schematics")
BOARDS = {
    "MAIN_BOARD": ("MainBoard/RADAR_Main_Board.brd", "Main Board (RADAR_Main_Board)"),
    "POWER_SUPPLY": ("PowerBoard/PowerBoard.brd", "Power Supply Board (PowerBoard)"),
    "RF_PA": ("PowerAmplifierBoard/RF_PA.brd", "RF Power Amplifier (RF_PA)"),
    "FREQUENCY_SYNTHESIZER": ("FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd", "Frequency Synthesizer (Clocks_Freq_Synth_board)"),
}
ENG = os.path.join(ROOT, "engineering", "PCB")


def mm(v: str) -> float:
    m = re.match(r"^\s*(-?[0-9.]+)\s*([a-z]*)", v or "")
    if not m:
        return 0.0
    n, u = float(m.group(1)), m.group(2)
    return {"mil": n * 0.0254, "inch": n * 25.4, "mic": n / 1000.0}.get(u, n)


def eagle_facts(path: str) -> dict:
    root = ET.parse(path).getroot()
    brd = root.find(".//board")
    f = {"version": root.get("version"), "mtime": _dt.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")}
    pk = {}
    for lib in brd.find("libraries").findall("library"):
        for p in lib.iter("package"):
            pk[(lib.get("name"), p.get("name"))] = p
    elements = brd.find("elements").findall("element")
    f["elements"] = len(elements)
    tht_pads = pkg_holes = smd_pads = 0
    for el in elements:
        p = pk.get((el.get("library"), el.get("package")))
        if p is None:
            continue
        tht_pads += len(p.findall("pad"))
        smd_pads += len(p.findall("smd"))
        pkg_holes += len(p.findall("hole"))
    f["tht_pads"], f["smd_pads"], f["pkg_holes"] = tht_pads, smd_pads, pkg_holes
    plain = brd.find("plain")
    f["plain_holes"] = len(plain.findall("hole")) if plain is not None else 0
    xs, ys = [], []
    for w in (plain.findall("wire") if plain is not None else []):
        if w.get("layer") == "20":
            xs += [float(w.get("x1")), float(w.get("x2"))]
            ys += [float(w.get("y1")), float(w.get("y2"))]
    f["outline"] = (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)) if xs else (None, None)
    f["outline_origin"] = (round(min(xs), 3), round(min(ys), 3)) if xs else (None, None)
    sig = brd.find("signals").findall("signal")
    f["signals"] = len(sig)
    f["vias"] = sum(len(s.findall("via")) for s in sig)
    f["tracks"] = sum(len([w for w in s.findall("wire") if w.get("layer") != "19"]) for s in sig)
    f["airwires"] = sum(len([w for w in s.findall("wire") if w.get("layer") == "19"]) for s in sig)
    f["sig_polygons"] = sum(len(s.findall("polygon")) for s in sig)
    f["plain_polygons"] = len(plain.findall("polygon")) if plain is not None else 0
    dr = brd.find("designrules")
    f["dru"] = dr.get("name") if dr is not None else "?"
    p = {e.get("name"): e.get("value") for e in (dr.findall("param") if dr is not None else [])}
    f["layerSetup"] = p.get("layerSetup", "?")
    f["copper_layers"] = sorted({int(n) for n in re.findall(r"\d+", f["layerSetup"])})
    f["mtCopper"] = (p.get("mtCopper") or "").split()
    f["mtIsolate"] = (p.get("mtIsolate") or "").split()
    f["msDrill"], f["msWidth"], f["mdWireWire"] = p.get("msDrill"), p.get("msWidth"), p.get("mdWireWire")
    f["approved_drc"] = len(brd.findall("approved")) + len(root.findall(".//approved"))
    return f


def kicad_facts(d: str) -> dict:
    k = {"missing": []}
    rp = os.path.join(d, "reports", "kicad_import_report.txt")
    if os.path.isfile(rp):
        t = open(rp, encoding="utf-8").read()
        for key in ("Footprints", "Tracks", "Vias", "Zones"):
            m = re.search(key + r":\s*(\d+)", t)
            k["imp_" + key.lower()] = int(m.group(1)) if m else None
    else:
        k["missing"].append(rp)
    st = os.path.join(d, "reports", "board_statistics.md")
    if os.path.isfile(st):
        t = open(st, encoding="utf-8").read()
        g = lambda pat: (re.search(pat, t) or [None, None])[1]
        k["width"] = g(r"Width:\s*([0-9.]+)")
        k["height"] = g(r"Height:\s*([0-9.]+)")
        k["min_clearance"] = g(r"Min track clearance:\s*([0-9.]+)")
        k["min_track"] = g(r"Min track width:\s*([0-9.]+)")
        k["min_drill"] = g(r"Min drill diameter:\s*([0-9.]+)")
        k["thickness"] = g(r"stackup thickness:\s*([0-9.]+)")
        k["pads_th"] = g(r"Through hole:\s*(\d+)")
        k["pads_smd"] = g(r"SMD:\s*(\d+)")
        k["pads_npth"] = g(r"NPTH:\s*(\d+)")
        k["vias"] = g(r"Through vias:\s*(\d+)")
        k["stats_text"] = t
    else:
        k["missing"].append(st)
    dj = os.path.join(d, "reports", "DRC_report.json")
    if os.path.isfile(dj):
        j = json.load(open(dj, encoding="utf-8"))
        k["drc_types"] = collections.Counter(v["type"] for v in j.get("violations", []))
        k["drc_total"] = len(j.get("violations", []))
        k["unconnected"] = len(j.get("unconnected_items", []))
        k["kicad_version"] = j.get("kicad_version")
    else:
        k["missing"].append(dj)
    drp = os.path.join(d, "drill", "drill_report.txt")
    k["holes"] = []
    if os.path.isfile(drp):
        sec = None
        for line in open(drp, encoding="utf-8"):
            if "plated through holes" in line and "unplated" not in line:
                sec = "PTH"
            elif "unplated through holes" in line:
                sec = "NPTH"
            m = re.match(r"\s*T(\d+)\s+([0-9.]+)mm\s+[0-9.\"]+\s+\((\d+) holes?\)", line)
            if m and sec:
                k["holes"].append((sec, int(m.group(1)), float(m.group(2)), int(m.group(3))))
            m2 = re.search(r"Total (un)?plated holes count (\d+)", line)
            if m2:
                k["npth_total" if m2.group(1) else "pth_total"] = int(m2.group(2))
    else:
        k["missing"].append(drp)
    return k


DELIVERABLES = [  # (§18 item, title, relative path pattern, kind)
    (1, "PCB top-layer drawing", "drawings/{B}_top_layer.pdf", "pdf"),
    (2, "PCB bottom-layer drawing (mirrored)", "drawings/{B}_bottom_layer_mirrored.pdf", "pdf"),
    (3, "Copper-layer views (one page per copper layer)", "drawings/{B}_copper_layers.pdf", "pdf"),
    (4, "Board-outline drawing", "drawings/{B}_outline.pdf", "pdf"),
    (5, "Mechanical dimensions (outline + holes, DXF / STEP)", "mechanical/{B}_outline.dxf", "dxf"),
    (6, "Drill map", "drill/{B}-PTH-drl_map.pdf", "pdf"),
    (7, "Hole table", "README.md (§5) and drill/drill_report.txt", "txt"),
    (8, "Component placement drawing (fab layer with pad outlines)", "drawings/{B}_assembly_top.pdf", "pdf"),
    (9, "Top assembly drawing", "drawings/{B}_assembly_top.pdf", "pdf"),
    (10, "Bottom assembly drawing (mirrored)", "drawings/{B}_assembly_bottom_mirrored.pdf", "pdf"),
    (11, "Fabrication drawing", "drawings/{B}_outline.pdf + drill maps + STACKUP.md", "pdf"),
    (12, "Layer stack-up documentation", "STACKUP.md", "md"),
    (13, "BOM with reference designators", "assembly/{B}_BOM.csv", "csv"),
    (14, "Pick-and-place file", "assembly/{B}_pick_and_place.csv", "csv"),
    (15, "Manufacturing export checklist", "README.md (§8)", "md"),
]


def process(board: str, date: str) -> tuple[list[str], int]:
    rel, title = BOARDS[board]
    src = os.path.join(SCH_DIR, rel)
    d = os.path.join(ENG, board)
    e = eagle_facts(src)
    k = kicad_facts(d)
    rc = 0
    # BOM copy
    bom_src = os.path.join(ROOT, "docs", "BOM", f"BOM_{board}.csv")
    bom_dst = os.path.join(d, "assembly", f"{board}_BOM.csv")
    if os.path.isfile(bom_src):
        os.makedirs(os.path.dirname(bom_dst), exist_ok=True)
        shutil.copyfile(bom_src, bom_dst)
    # cross-check
    checks = []
    def chk(name, a, b, note=""):
        ok = (a == b)
        checks.append((name, a, b, "OK" if ok else "MISMATCH", note))
        return ok
    ncu = len(e["copper_layers"])
    chk("Width (mm)", e["outline"][0], float(k.get("width") or -1))
    chk("Height (mm)", e["outline"][1], float(k.get("height") or -1))
    chk("Footprints = EAGLE elements + free holes", e["elements"] + e["plain_holes"], k.get("imp_footprints"),
        "KiCad imports every free <hole> as a footprint")
    chk("Vias", e["vias"], int(k.get("vias") or -1))
    chk("Tracks (signal wires excl. airwires)", e["tracks"], k.get("imp_tracks"))
    chk("Copper layers", ncu, None if "stats_text" not in k else len(re.findall(r"^\s+L\d+\s*:", open(os.path.join(d, "drill", "drill_report.txt")).read(), re.M)) if os.path.isfile(os.path.join(d, "drill", "drill_report.txt")) else None)
    chk("NPTH holes (free holes + package holes)", e["plain_holes"] + e["pkg_holes"], k.get("npth_total"),
        "pads with drill but no copper are NPTH in KiCad too")
    chk("PTH holes (vias + THT pads)", e["vias"] + e["tht_pads"], k.get("pth_total"))
    chk("Min drill (mm)", mm(e["msDrill"]) if e["msDrill"] else None, float(k.get("min_drill") or -1), "DRU msDrill vs smallest drill actually used (KiCad stats)") if False else None
    mism = sum(1 for c in checks if c[3] != "OK")
    if mism or k["missing"]:
        rc = 1
    # hole table
    holes_md = ["| Type | Tool | Ø (mm) | Count |", "|---|---|---|---|"]
    for sec, t, dia, n in k["holes"]:
        holes_md.append(f"| {sec} | T{t} | {dia:.3f} | {n} |")
    holes_md.append(f"| **Total** | | PTH {k.get('pth_total', '?')} / NPTH {k.get('npth_total', '?')} | {int(k.get('pth_total', 0) or 0) + int(k.get('npth_total', 0) or 0)} |")
    # stackup
    cu = e["copper_layers"]
    stack = ["| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |", "|---|---|---|---|---|"]
    kic = ["F.Cu"] + [f"In{i}.Cu" for i in range(1, ncu - 1)] + ["B.Cu"]
    for i, ln in enumerate(cu):
        cop = e["mtCopper"][ln - 1] if ln - 1 < len(e["mtCopper"]) else "?"
        iso = e["mtIsolate"][ln - 1] if i < ncu - 1 and ln - 1 < len(e["mtIsolate"]) else "—"
        stack.append(f"| {i + 1} | {ln} | {kic[i] if i < len(kic) else '?'} | {cop} | {iso} |")
    routed = e["airwires"] == 0
    status = "SOURCE-DERIVED" if routed else "PARTIAL"
    unc = k.get("unconnected")
    lines = []
    L = lines.append
    L(f"# {title} — Manufacturing & drawing package\n")
    L(f"| Field | Value |\n|---|---|")
    L(f"| Project | AERIS-10 |")
    L(f"| Package ID | PCB-PKG-{board} |")
    L(f"| Revision | A (first generated package) — **source board revision: none recorded in the EAGLE file** |")
    L(f"| Date | {date} |")
    L(f"| Units | mm (Gerber X2 RS-274X, 6 decimals; Excellon mm) |")
    L(f"| Source | `{os.path.relpath(src, ROOT)}` — EAGLE {e['version']} XML, file date {e['mtime']} |")
    L(f"| Generator | `tools/kicad_pcb_pipeline.sh` (kicad-cli {k.get('kicad_version', '10.0.6')}) + `tools/gen_engineering_pcb_docs.py` |")
    L(f"| Status | **{status}** — {'layout fully routed in the source; exports are a faithful conversion but have not been reviewed by the board designer or a fabricator' if routed else f'layout NOT finished in the source ({e['airwires']} airwires in EAGLE; {unc} unconnected items after KiCad zone fill). Exports document the current state and must not be sent to fabrication'} |")
    L(f"| Verification | DRC run (KiCad, EAGLE-DRU-derived rules): {k.get('drc_total', '?')} violations, {unc} unconnected — see §6. No fabricator review, no physical verification |\n")
    L("Preserve-original rule: the EAGLE files were only read. The KiCad copy under `kicad/` is an editable conversion "
      "(`kicad-cli pcb import --format eagle`), with EAGLE layer 47 *Measures* remapped to `Dwgs.User` and the EAGLE design rules "
      "transferred to the project file (`reports/design_rules_mapping.md`). The conversion is an approximation of EAGLE's "
      "polygon pours and thermals; the original EAGLE file remains the design master.\n")
    L("## 1. Deliverables (claude.md addendum §18)\n")
    L("| # | Item | File | Status |\n|---|---|---|---|")
    for n, t, pat, kind in DELIVERABLES:
        path = pat.format(B=board)
        first = path.split(" ")[0]
        exists = os.path.exists(os.path.join(d, first)) if "/" in first else True
        st = ("GENERATED" if exists else "MISSING")
        if n == 12:
            st = "PARTIAL — layer order from DRU; materials/thickness UNVERIFIED"
        if n == 13:
            st = "GENERATED — 0 MPN attributes in the source (values only)" if exists else "MISSING"
        if n == 11:
            st = "PARTIAL — no vendor notes (material, finish, tolerances) in the source"
        if not exists and n not in (7, 15):
            rc = 1
        L(f"| {n} | {t} | `{path}` | {st} |")
    L("\nAdditional exports: `gerber/` (RS-274X X2, Protel extensions, `*-job.gbrjob`), `drill/*.drl` (Excellon, PTH/NPTH separate), "
      "`svg/` per-layer SVG, `mechanical/{B}_board_only.step`, `mechanical/{B}_top_fab.dxf`, `ipc/{B}.xml` (IPC-2581), "
      "`ipc/{B}_netlist.d356` (IPC-D-356), `3d/*.png` (KiCad 3-D renders, no component models), `kicad/{B}.kicad_pcb` + `.kicad_pro`.".replace("{B}", board))
    L("\n## 2. Board statistics (KiCad `pcb export stats` on the converted board)\n")
    L("| Item | Value |\n|---|---|")
    L(f"| Outline (bounding box) | {k.get('width')} × {k.get('height')} mm |")
    L(f"| Copper layers | {ncu} (EAGLE layerSetup `{e['layerSetup']}`) |")
    L(f"| Footprints (incl. free holes) | {k.get('imp_footprints')} |")
    L(f"| Pads THT / SMD / NPTH | {k.get('pads_th')} / {k.get('pads_smd')} / {k.get('pads_npth')} |")
    L(f"| Vias | {k.get('vias')} |")
    L(f"| Tracks / zones imported | {k.get('imp_tracks')} / {k.get('imp_zones')} |")
    L(f"| Min track width / clearance used | {k.get('min_track')} / {k.get('min_clearance')} mm |")
    L(f"| Min drill used | {k.get('min_drill')} mm |")
    L(f"| Board thickness | {k.get('thickness')} mm — **KiCad default, NOT from the source (UNVERIFIED)** |")
    L("\n## 3. Cross-check EAGLE XML ↔ KiCad conversion\n")
    L("| Check | EAGLE (XML) | KiCad | Result | Note |\n|---|---|---|---|---|")
    for c in checks:
        if c is None:
            continue
        L(f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} |")
    L(f"\nEAGLE airwires (layer 19): {e['airwires']}; signal polygons: {e['sig_polygons']}; approved (waived) DRC/ERC entries in the source: {e['approved_drc']}.")
    L("\n## 4. Design rules\n")
    L(f"EAGLE DRU `{e['dru']}`: min width {e['msWidth']}, min drill {e['msDrill']}, wire-wire clearance {e['mdWireWire']}. "
      f"Mapping to KiCad: `reports/design_rules_mapping.md`.")
    L("\n## 5. Hole table (from `drill/drill_report.txt`)\n")
    lines.extend(holes_md)
    L("\n## 6. DRC result (KiCad, rules from the EAGLE DRU)\n")
    L(f"Report: `reports/DRC_report.txt` / `.json`. Total violations {k.get('drc_total')}, unconnected items {unc}. "
      "KiCad stops reporting a rule after 199 hits, so counts of exactly 199 are lower bounds. Breakdown:\n")
    L("| Rule | Count | Interpretation |\n|---|---|---|")
    interp = {
        "unconnected_items": "unrouted connections (after zone fill)",
        "solder_mask_bridge": "mask web between adjacent pads thinner than KiCad default (EAGLE has no such rule) — fabricator decision",
        "silk_overlap": "overlapping silkscreen texts/lines — cosmetic", "silk_over_copper": "silk over exposed copper — cosmetic/assembly",
        "track_dangling": "track end not connected — review (stubs or unfinished routing)",
        "via_dangling": "via connected on one layer only — review",
        "shorting_items": "copper of different nets touching after conversion (typically EAGLE polygon vs unnamed copper) — REVIEW in EAGLE",
        "clearance": "copper clearance < DRU — review", "hole_clearance": "hole to copper clearance (KiCad rule, no EAGLE equivalent)",
        "zones_intersect": "overlapping pours of different priority — conversion artefact or design issue",
        "courtyards_overlap": "footprint courtyards overlap — imported courtyard approximation",
        "drill_out_of_range": "drill smaller than DRU msDrill", "silk_edge_clearance": "silk too close to edge",
    }
    for t, n in sorted((k.get("drc_types") or {}).items(), key=lambda kv: -kv[1]):
        L(f"| `{t}` | {n} | {interp.get(t, 'review')} |")
    L("\n## 7. Layer stack-up (STACKUP.md)\n")
    L("Layer order and copper thickness come from the EAGLE DRU; dielectric thicknesses in the DRU are EAGLE defaults and are "
      "**not** a vendor stack-up. See `STACKUP.md` for the table and the list of unknowns (material, prepreg/core, finish, impedance).")
    L("\n## 8. Manufacturing export checklist\n")
    for item, done in [
        ("Gerber set (all copper, mask, paste, silk, outline, fab) exported", True),
        ("Excellon drill files PTH/NPTH + drill map + report", True),
        ("Pick-and-place (both sides, mm, CSV)", True),
        ("BOM with reference designators", True),
        ("BOM with manufacturer part numbers for 100 % of lines", False),
        ("Fabrication drawing with vendor notes (material, thickness, finish, mask/silk colours, tolerances, impedance)", False),
        ("Stack-up confirmed by the fabricator", False),
        ("Layout routed to completion (0 airwires / 0 unconnected)", routed and (unc == 0)),
        ("DRC with 0 unapproved errors, waivers documented", False),
        ("Designer review of the KiCad conversion against EAGLE (pours, thermals, text)", False),
        ("Gerbers viewed in an independent viewer (gerbv/online) and compared with the outline drawing", False),
        ("IPC-2581 / IPC-D-356 netlist test accepted by the fabricator", False),
    ]:
        L(f"- [{'x' if done else ' '}] {item}")
    L("\n## 9. Known gaps for this board (BLOCKED — MISSING DATA)\n")
    L("- Board material, finished thickness, copper weight per layer, surface finish, solder-mask/silk colours, impedance targets: "
      "not recorded in the EAGLE file (only `4_Schematics and Boards Layout/4_4_Board Stack-up/Stack_Hybrid.png` and the PCBWay "
      "impedance note for RO4350B exist, unlabelled).")
    L("- Manufacturer part numbers: none in the schematic attributes.")
    L("- 3-D component models: not embedded (Autodesk online URNs) → STEP export is board-only.")
    if not routed:
        L(f"- Routing incomplete: {e['airwires']} EAGLE airwires; {unc} unconnected items after KiCad fill.")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    S = [f"# {title} — Layer stack-up\n",
         f"Project AERIS-10 · PCB-STK-{board} · Rev A · {date} · Status: **PARTIAL** (layer order SOURCE-DERIVED; thicknesses/materials UNVERIFIED)\n",
         f"Source: EAGLE DRU `{e['dru']}` in `{os.path.relpath(src, ROOT)}` (layerSetup `{e['layerSetup']}`).\n",
         "| # | EAGLE layer | KiCad layer | Copper (DRU mtCopper) | Dielectric below (DRU mtIsolate) |", "|---|---|---|---|---|"]
    S.extend(stack[2:])
    S.append("\n**Caveats**: `mtCopper` 0.035 mm = 1 oz copper; `mtIsolate` values are the EAGLE DRU table (the DRU names a PCBWay "
             "template, but the values were not confirmed by a vendor stack-up document). Total thickness is not defined in the source; "
             "KiCad assumed 1.6 mm. Material (FR-4 / RO4350B hybrid per `Stack_Hybrid.png`), prepreg/core assignment, finish and "
             "impedance targets must be supplied by the designer/fabricator → `engineering/MISSING_DRAWINGS_RECOVERY_PLAN.md`.")
    with open(os.path.join(d, "STACKUP.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(S) + "\n")
    summary = [f"### {board}\n", "| Check | EAGLE (XML) | KiCad | Result | Note |", "|---|---|---|---|---|"]
    summary += [f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} |" for c in checks if c]
    summary.append(f"\nMissing KiCad reports: {', '.join(k['missing']) if k['missing'] else 'none'}; EAGLE airwires {e['airwires']} → KiCad unconnected after fill {unc}.\n")
    print(f"{board}: checks={len([c for c in checks if c])} mismatches={mism} airwires={e['airwires']} unconnected={unc} drc={k.get('drc_total')}")
    return summary, rc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", choices=sorted(BOARDS))
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    rc = 0
    out = [f"# PCB cross-check: EAGLE XML vs KiCad conversion\n",
           f"Generated {a.date} by `tools/gen_engineering_pcb_docs.py`. Every row compares a quantity counted directly in the EAGLE "
           "`.brd` XML with the same quantity reported by KiCad after `kicad-cli pcb import`. A mismatch means the conversion must be "
           "reviewed before the KiCad outputs are used.\n"]
    for b in ([a.board] if a.board else ["RF_PA", "FREQUENCY_SYNTHESIZER", "MAIN_BOARD", "POWER_SUPPLY"]):
        try:
            s, r = process(b, a.date)
        except Exception as exc:  # noqa: BLE001
            print("ERROR", b, exc)
            return 2
        out += s
        rc |= r
    os.makedirs(os.path.join(ROOT, "engineering", "VALIDATION"), exist_ok=True)
    with open(os.path.join(ROOT, "engineering", "VALIDATION", "PCB_CROSS_CHECK.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
