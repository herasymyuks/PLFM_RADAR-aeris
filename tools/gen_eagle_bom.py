#!/usr/bin/env python3
"""
gen_eagle_bom.py — Extract a bill of materials from an EAGLE 6+/7/9 XML schematic.

For every <part> that maps to a physical package (supply symbols and frames are dropped),
collect: reference, value, library, deviceset, device, package, and any part-level
attributes (MPN, MANUFACTURER_PART_NUMBER, MANUFACTURER, etc.).  Lines are grouped by
(value, deviceset, device, package).  Output: CSV (grouped), optional per-reference CSV, and
a Markdown summary.  Read-only on the schematic.

Usage:
    python3 tools/gen_eagle_bom.py SCHEMATIC.sch --out BOM.csv [--refs REFS.csv] [--md BOM.md]
Exit codes: 0 ok, 2 parse error.
Dependencies: Python 3.8+ standard library.
Caveat: the deviceset name is often, but not always, a manufacturer part number. Treat the
"mpn_candidate" column as UNVERIFIED unless an explicit MPN attribute is present.
"""
import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path

NON_PHYSICAL_LIBS = {"supply1", "supply2", "frames"}
MPN_ATTRS = ("MPN", "MANUFACTURER_PART_NUMBER", "MFR_PART_NUMBER", "PARTNO", "PART_NUMBER")
MFR_ATTRS = ("MANUFACTURER", "MANUFACTURER_NAME", "MFR_NAME", "MF")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("schematic")
    ap.add_argument("--out", required=True)
    ap.add_argument("--refs")
    ap.add_argument("--md")
    args = ap.parse_args()
    try:
        root = ET.parse(args.schematic).getroot()
    except (ET.ParseError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr); return 2
    # library -> deviceset -> device -> package
    pkg = {}
    for lib in root.iter("library"):
        for ds in lib.iter("deviceset"):
            for dev in ds.iter("device"):
                pkg[(lib.get("name"), ds.get("name"), dev.get("name", ""))] = dev.get("package", "")
    refs = []
    for p in root.iter("part"):
        lib, ds, dev = p.get("library"), p.get("deviceset"), p.get("device", "")
        package = pkg.get((lib, ds, dev), "")
        if lib in NON_PHYSICAL_LIBS or not package:
            continue
        attrs = {a.get("name"): a.get("value", "") for a in p.iter("attribute")}
        mpn = next((attrs[k] for k in MPN_ATTRS if attrs.get(k)), "")
        mfr = next((attrs[k] for k in MFR_ATTRS if attrs.get(k)), "")
        refs.append({"ref": p.get("name"), "value": p.get("value", ""), "library": lib, "deviceset": ds,
                     "device": dev, "package": package, "mpn": mpn, "manufacturer": mfr})
    refs.sort(key=lambda r: (r["deviceset"], r["value"], r["ref"]))
    grouped = OrderedDict()
    for r in refs:
        k = (r["value"], r["deviceset"], r["device"], r["package"])
        g = grouped.setdefault(k, {"qty": 0, "refs": [], "mpn": r["mpn"], "manufacturer": r["manufacturer"], "library": r["library"]})
        g["qty"] += 1; g["refs"].append(r["ref"])
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "qty", "value", "deviceset", "device", "package", "library", "mpn_attribute", "manufacturer_attribute", "mpn_candidate", "mpn_status", "references"])
        for i, ((value, ds, dev, package), g) in enumerate(grouped.items(), 1):
            cand = g["mpn"] or ds
            status = "VERIFIED (attribute)" if g["mpn"] else ("UNVERIFIED (deviceset name)" if ds not in ("C", "R", "L", "C-EU", "R-EU_", "L-EU", "GND", "LED-BLUE") else "GENERIC — value/package only")
            w.writerow([i, g["qty"], value, ds, dev, package, g["library"], g["mpn"], g["manufacturer"], cand, status, " ".join(g["refs"])])
    if args.refs:
        with open(args.refs, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(refs[0].keys()) if refs else ["ref"])
            w.writeheader(); w.writerows(refs)
    if args.md:
        with open(args.md, "w") as f:
            n_mpn = sum(1 for g in grouped.values() if g["mpn"])
            f.write(f"# BOM extracted from `{Path(args.schematic).name}`\n\n")
            f.write(f"Physical parts: **{len(refs)}** references in **{len(grouped)}** line items. Lines with an explicit MPN attribute: **{n_mpn}**. ")
            f.write("Every other `mpn_candidate` is the EAGLE deviceset name and is **UNVERIFIED**. Values missing in the schematic appear empty.\n\n")
            f.write("| # | Qty | Value | Deviceset | Package | MPN candidate | Status | References |\n|---|---:|---|---|---|---|---|---|\n")
            for i, ((value, ds, dev, package), g) in enumerate(grouped.items(), 1):
                cand = g["mpn"] or ds
                status = "attr" if g["mpn"] else ("generic" if ds in ("C", "R", "L", "C-EU", "R-EU_", "L-EU", "LED-BLUE") else "UNVERIFIED")
                rr = " ".join(g["refs"]); rr = rr if len(rr) < 90 else rr[:87] + "..."
                f.write(f"| {i} | {g['qty']} | {value} | {ds} | {package} | {cand} | {status} | {rr} |\n")
    print(f"{Path(args.schematic).name}: {len(refs)} physical parts, {len(grouped)} line items, {sum(1 for g in grouped.values() if g['mpn'])} with MPN attribute", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
