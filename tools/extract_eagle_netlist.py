#!/usr/bin/env python3
"""
extract_eagle_netlist.py — Extract per-part pin/net connectivity from an EAGLE 6/7 XML schematic.

Purpose: provide verifiable evidence (net name <-> device pin <-> package pad) for FPGA/MCU
pin-assignment reconstruction.  Read-only; writes only to the --out CSV you name.

Usage:
    python3 tools/extract_eagle_netlist.py SCHEMATIC.sch --part U42 [--out pins.csv]
    python3 tools/extract_eagle_netlist.py SCHEMATIC.sch --list-parts
Exit codes: 0 ok, 1 part not found, 2 file/parse error.
Dependencies: Python 3.8+ standard library (xml.etree).
Notes: EAGLE stores pinrefs as <pinref part gate pin/> inside <net><segment>.  Pad names are
resolved through library -> deviceset -> device -> connects (gate+pin -> pad).
"""
import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def load(path: Path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError) as e:
        print(f"ERROR: cannot parse {path}: {e}", file=sys.stderr)
        sys.exit(2)


def pad_map(root, part_el):
    """Return {(gate, pin): pad} for the part's device."""
    lib, ds, dev = part_el.get("library"), part_el.get("deviceset"), part_el.get("device", "")
    for library in root.iter("library"):
        if library.get("name") != lib:
            continue
        for deviceset in library.iter("deviceset"):
            if deviceset.get("name") != ds:
                continue
            for device in deviceset.iter("device"):
                if device.get("name", "") != dev:
                    continue
                return {(c.get("gate"), c.get("pin")): c.get("pad") for c in device.iter("connect")}
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("schematic")
    ap.add_argument("--part", help="part name, e.g. U42")
    ap.add_argument("--list-parts", action="store_true")
    ap.add_argument("--out", help="CSV output path (default: stdout)")
    args = ap.parse_args()
    root = load(Path(args.schematic))
    parts = {p.get("name"): p for p in root.iter("part")}
    if args.list_parts:
        for n, p in sorted(parts.items()):
            print(f"{n}\t{p.get('library')}\t{p.get('deviceset')}\t{p.get('device','')}\t{p.get('value','')}")
        return 0
    if not args.part or args.part not in parts:
        print(f"ERROR: part {args.part!r} not found (use --list-parts)", file=sys.stderr)
        return 1
    pads = pad_map(root, parts[args.part])
    rows = []
    for si, sheet in enumerate(root.iter("sheet"), 1):
        for net in sheet.iter("net"):
            for pr in net.iter("pinref"):
                if pr.get("part") == args.part:
                    g, pin = pr.get("gate"), pr.get("pin")
                    rows.append({"net": net.get("name"), "part": args.part, "gate": g, "pin": pin,
                                 "pad": pads.get((g, pin), ""), "sheet": si})
    rows.sort(key=lambda r: (r["gate"], r["pad"], r["pin"]))
    out = open(args.out, "w", newline="") if args.out else sys.stdout
    w = csv.DictWriter(out, fieldnames=["net", "part", "gate", "pin", "pad", "sheet"])
    w.writeheader(); w.writerows(rows)
    if args.out:
        out.close()
    print(f"{args.part}: {len(rows)} connected pins, {len(set(r['net'] for r in rows))} nets "
          f"({parts[args.part].get('deviceset')})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
