#!/usr/bin/env python3
"""Create a KiCad project file (.kicad_pro) whose design rules come from the EAGLE
design rules (<designrules> block) stored in an EAGLE .brd file.

kicad-cli's EAGLE importer writes only the .kicad_pcb; without a project file the
DRC runs with KiCad defaults (0.2 mm clearance, 0.4 mm vias), which do not
describe these boards.  This script transfers the DRU values that have a direct
KiCad equivalent and documents every mapping in a sidecar Markdown file.

Usage: python3 tools/kicad_project_from_dru.py <board.brd> <board.kicad_pcb> [--md report.md]
Exit codes: 0 ok, 1 missing designrules, 2 bad arguments. Stdlib only. Non-destructive
(only writes <board>.kicad_pro next to the .kicad_pcb and the optional report).
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET


def mm(v: str) -> float:
    m = re.match(r"^\s*(-?[0-9.]+)\s*([a-z]*)\s*$", v or "")
    if not m:
        return 0.0
    n, u = float(m.group(1)), m.group(2)
    return {"mil": n * 0.0254, "inch": n * 25.4, "mic": n / 1000.0}.get(u, n)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    md_path = None
    if "--md" in sys.argv:
        md_path = sys.argv[sys.argv.index("--md") + 1]
        args = [a for a in args if a != md_path]
    if len(args) != 2:
        print(__doc__)
        return 2
    brd, pcb = args
    root = ET.parse(brd).getroot()
    dr = root.find(".//designrules")
    if dr is None:
        print("ERROR: no <designrules> in", brd)
        return 1
    p = {e.get("name"): e.get("value") for e in dr.findall("param")}
    g = lambda k: mm(p.get(k, "0"))
    md_wire = g("mdWireWire")
    ms_width = g("msWidth")
    ms_drill = g("msDrill")
    rl_min_via = g("rlMinViaOuter")
    rv_via = float(p.get("rvViaOuter", "0.25"))
    rl_max_via = g("rlMaxViaOuter")
    ms_micro = g("msMicroVia")
    md_edge = g("mdCopperDimension")
    md_drill = g("mdDrill")
    # EAGLE annular ring = clamp(drill * rvViaOuter, rlMinViaOuter, rlMaxViaOuter)
    ann_min = max(min(ms_drill * rv_via, rl_max_via), rl_min_via)
    min_via_dia = round(ms_drill + 2 * ann_min, 4)
    rules = {
        "min_clearance": md_wire,
        "min_connection": 0.0,
        "min_copper_edge_clearance": md_edge,
        "min_hole_clearance": 0.0,
        "min_hole_to_hole": md_drill,
        "min_microvia_diameter": round(ms_micro + 2 * ann_min, 4),
        "min_microvia_drill": ms_micro,
        "min_resolved_spokes": 1,
        "min_silk_clearance": 0.0,
        "min_text_height": 0.0,
        "min_text_thickness": 0.0,
        "min_through_hole_diameter": ms_drill,
        "min_track_width": ms_width,
        "min_via_annular_width": ann_min,
        "min_via_diameter": min_via_dia,
        "solder_mask_to_copper_clearance": 0.0,
        "use_height_for_length_calcs": True,
    }
    name = os.path.splitext(os.path.basename(pcb))[0]
    pro = {
        "board": {
            "design_settings": {
                "defaults": {},
                "rule_severities": {"text_height": "ignore", "text_thickness": "ignore",
                                     "silk_overlap": "warning", "silk_over_copper": "warning",
                                     "lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore",
                                     "footprint_type_mismatch": "ignore", "footprint_filters_mismatch": "ignore"},
                "rules": rules,
            },
            "layer_presets": [],
            "viewports": [],
        },
        "meta": {"filename": name + ".kicad_pro", "version": 3},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12, "clearance": md_wire, "diff_pair_gap": md_wire,
                    "diff_pair_via_gap": md_wire, "diff_pair_width": ms_width, "line_style": 0,
                    "microvia_diameter": round(ms_micro + 2 * ann_min, 4), "microvia_drill": ms_micro,
                    "name": "Default", "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": ms_width,
                    "via_diameter": min_via_dia, "via_drill": ms_drill, "wire_width": 6,
                }
            ],
            "meta": {"version": 4}, "net_colors": None, "netclass_assignments": None, "netclass_patterns": [],
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {},
        "sheets": [],
        "text_variables": {},
    }
    out = os.path.join(os.path.dirname(pcb), name + ".kicad_pro")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(pro, fh, indent=2)
    print("wrote", out)
    if md_path:
        rows = [
            ("min_clearance", "mdWireWire", p.get("mdWireWire"), rules["min_clearance"]),
            ("min_track_width", "msWidth", p.get("msWidth"), rules["min_track_width"]),
            ("min_through_hole_diameter", "msDrill", p.get("msDrill"), rules["min_through_hole_diameter"]),
            ("min_via_annular_width", "clamp(msDrill·rvViaOuter, rlMinViaOuter, rlMaxViaOuter)",
             f"{p.get('rvViaOuter')} / {p.get('rlMinViaOuter')} / {p.get('rlMaxViaOuter')}", rules["min_via_annular_width"]),
            ("min_via_diameter", "msDrill + 2·annular", "", rules["min_via_diameter"]),
            ("min_microvia_drill", "msMicroVia", p.get("msMicroVia"), rules["min_microvia_drill"]),
            ("min_copper_edge_clearance", "mdCopperDimension", p.get("mdCopperDimension"), rules["min_copper_edge_clearance"]),
            ("min_hole_to_hole", "mdDrill", p.get("mdDrill"), rules["min_hole_to_hole"]),
            ("min_hole_clearance", "— (no EAGLE equivalent)", "", 0.0),
            ("min_silk_clearance / text rules", "— (no EAGLE equivalent, disabled)", "", 0.0),
        ]
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(f"# KiCad design rules derived from EAGLE DRU `{dr.get('name')}`\n\n")
            fh.write(f"Source: `{os.path.basename(brd)}` → `{os.path.basename(out)}` (generated by `tools/kicad_project_from_dru.py`).\n\n")
            fh.write("| KiCad rule | EAGLE DRU parameter | EAGLE value | KiCad value (mm) |\n|---|---|---|---|\n")
            for r in rows:
                fh.write(f"| `{r[0]}` | `{r[1]}` | {r[2] or '—'} | {r[3]} |\n")
            fh.write("\nEAGLE DRU parameters without a KiCad global-rule equivalent (per-pair clearances `mdWirePad`, "
                     "`mdWireVia`, `mdPadPad`, `mdPadVia`, `mdViaVia`, `mdSmdPad`, `mdSmdVia`, `mdSmdSmd`, stop-mask "
                     "frame `mvStopFrame`, thermal/isolate settings, layer setup `layerSetup`, copper/dielectric "
                     "thickness `mtCopper`/`mtIsolate`) are NOT transferred; the stack-up must be re-entered in "
                     "KiCad Board Setup if the KiCad copy is to be used for fabrication.\n\n")
            fh.write(f"Layer setup string: `{p.get('layerSetup')}`; mtCopper: `{p.get('mtCopper')}`; mtIsolate: `{p.get('mtIsolate')}`.\n")
        print("wrote", md_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
