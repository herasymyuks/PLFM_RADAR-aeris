#!/usr/bin/env python3
"""Schematic connectivity reports from the EAGLE XML files (no EAGLE needed).

For every board (or the one given with --board) it writes:
  engineering/ELECTRICAL/netlists/<BOARD>_netlist.csv            net,part,gate,pin,pad,sheet,class
  engineering/ELECTRICAL/netlists/<BOARD>_netlist_by_part.csv    part,value,deviceset,device,package,gate,pin,pad,net
  engineering/ELECTRICAL/connection_diagrams/<BOARD>_connection_report.md
        component-to-net table, connector pin-outs, net fan-out summary
  engineering/ELECTRICAL/netlists/<BOARD>_unresolved_connections.md
        single-pin nets, unconnected pins of placed gates, parts without value,
        schematic↔board inconsistencies, board airwires (layer 19)
  engineering/ELECTRICAL/netlists/<BOARD>_missing_symbols_footprints.md
        parts whose deviceset/gate/symbol/device/package cannot be resolved

Usage: python3 tools/gen_schematic_reports.py [--board NAME] [--out engineering/ELECTRICAL]
Exit codes: 0 = all reports written and no missing symbol/footprint, 1 = reports written but
unresolved items exist (see the reports), 2 = parse error.  Stdlib only; non-destructive.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as _dt
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH_DIR = os.path.join(ROOT, "4_Schematics and Boards Layout", "4_6_Schematics")
BOARDS = {
    "MAIN_BOARD": ("MainBoard/RADAR_Main_Board.sch", "MainBoard/RADAR_Main_Board.brd"),
    "POWER_SUPPLY": ("PowerBoard/PowerBoard.sch", "PowerBoard/PowerBoard.brd"),
    "RF_PA": ("PowerAmplifierBoard/RF_PA.sch", "PowerAmplifierBoard/RF_PA.brd"),
    "FREQUENCY_SYNTHESIZER": ("FrequencySynthesizerBoard/Clocks_Freq_Synth_board.sch",
                              "FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd"),
}
NON_PHYSICAL_LIBS = {"supply1", "supply2", "frames", "supply"}
CONNECTOR_PREFIXES = ("J", "X", "JP", "SV", "CON", "P", "U$")  # U$ excluded below unless package looks like a connector


class Sch:
    def __init__(self, path: str):
        self.path = path
        self.root = ET.parse(path).getroot()
        self.sch = self.root.find(".//schematic")
        self.symbols, self.devicesets, self.packages = {}, {}, {}
        for lib in self.sch.find("libraries").findall("library"):
            ln = lib.get("name", "")
            for s in lib.iter("symbol"):
                self.symbols[(ln, s.get("name"))] = s
            for d in lib.iter("deviceset"):
                self.devicesets[(ln, d.get("name"))] = d
            for p in lib.iter("package"):
                self.packages[(ln, p.get("name"))] = p
        self.parts = {p.get("name"): p for p in self.sch.find("parts").findall("part")}
        self.sheets = self.sch.find("sheets").findall("sheet")

    def device(self, part):
        ds = self.devicesets.get((part.get("library", ""), part.get("deviceset", "")))
        if ds is None:
            return None, None
        for d in ds.find("devices").findall("device"):
            if d.get("name", "") == part.get("device", ""):
                return ds, d
        return ds, None

    def pad_map(self, part):
        ds, dev = self.device(part)
        m = {}
        if dev is not None and dev.find("connects") is not None:
            for c in dev.find("connects").findall("connect"):
                m[(c.get("gate"), c.get("pin"))] = c.get("pad")
        return m


def load_brd(path: str):
    root = ET.parse(path).getroot()
    elements = {e.get("name"): e for e in root.iter("element")}
    signals = {s.get("name"): s for s in root.iter("signal")}
    airwires = collections.Counter()
    for s in signals.values():
        for w in s.findall("wire"):
            if w.get("layer") == "19":
                airwires[s.get("name")] += 1
    return elements, signals, airwires


def is_physical(part, sch=None) -> bool:
    """Physical = not a supply/frame symbol.  A part is a supply symbol when its library is a
    supply library or when its device has no package and every symbol pin is of direction 'sup'."""
    if part.get("library", "") in NON_PHYSICAL_LIBS:
        return False
    if sch is not None:
        ds, dev = sch.device(part)
        if ds is not None and (dev is None or not dev.get("package")):
            dirs = set()
            for g in ds.find("gates").findall("gate"):
                sym = sch.symbols.get((part.get("library", ""), g.get("symbol")))
                if sym is not None:
                    dirs.update(p.get("direction", "io") for p in sym.findall("pin"))
            if dirs and dirs <= {"sup", "pwr"}:
                return False
    return True


def process(board: str, out_root: str, today: str) -> int:
    sch_rel, brd_rel = BOARDS[board]
    sch_path, brd_path = os.path.join(SCH_DIR, sch_rel), os.path.join(SCH_DIR, brd_rel)
    sch = Sch(sch_path)
    elements, signals, airwires = load_brd(brd_path)
    net_dir = os.path.join(out_root, "netlists")
    con_dir = os.path.join(out_root, "connection_diagrams")
    os.makedirs(net_dir, exist_ok=True)
    os.makedirs(con_dir, exist_ok=True)

    # ---- connectivity -------------------------------------------------------
    rows = []                       # net rows
    part_pins = collections.defaultdict(list)   # part -> [(gate,pin,pad,net)]
    placed_gates = collections.defaultdict(set)  # part -> gates placed on sheets
    net_class = {}
    for si, sheet in enumerate(sch.sheets, 1):
        inst = sheet.find("instances")
        for i in (inst.findall("instance") if inst is not None else []):
            placed_gates[i.get("part")].add(i.get("gate"))
        nets = sheet.find("nets")
        for net in (nets.findall("net") if nets is not None else []):
            nn = net.get("name", "")
            net_class[nn] = net.get("class", "0")
            for seg in net.findall("segment"):
                for pr in seg.findall("pinref"):
                    part = sch.parts.get(pr.get("part"))
                    if part is None:
                        continue
                    pad = sch.pad_map(part).get((pr.get("gate"), pr.get("pin")), "")
                    rows.append((nn, pr.get("part"), pr.get("gate"), pr.get("pin"), pad, si, net_class[nn]))
                    part_pins[pr.get("part")].append((pr.get("gate"), pr.get("pin"), pad, nn, si))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    with open(os.path.join(net_dir, f"{board}_netlist.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["net", "part", "gate", "pin", "pad", "sheet", "net_class"])
        w.writerows(rows)
    with open(os.path.join(net_dir, f"{board}_netlist_by_part.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["part", "value", "deviceset", "device", "package", "gate", "pin", "pad", "net", "sheet"])
        for pn in sorted(sch.parts, key=natural_key):
            p = sch.parts[pn]
            _, dev = sch.device(p)
            pkg = dev.get("package", "") if dev is not None else ""
            for g, pin, pad, nn, si in sorted(part_pins.get(pn, [])):
                w.writerow([pn, p.get("value", ""), p.get("deviceset", ""), p.get("device", ""), pkg, g, pin, pad, nn, si])

    # ---- missing symbols / footprints ---------------------------------------
    missing = []
    for pn, p in sch.parts.items():
        lib, dsn = p.get("library", ""), p.get("deviceset", "")
        ds, dev = sch.device(p)
        if ds is None:
            missing.append((pn, "deviceset not found in embedded libraries", f"{lib}:{dsn}"))
            continue
        for g in ds.find("gates").findall("gate"):
            if (lib, g.get("symbol")) not in sch.symbols:
                missing.append((pn, "symbol missing", f"{lib}:{g.get('symbol')}"))
        if dev is None:
            missing.append((pn, "device variant not found", f"{dsn}{p.get('device', '')}"))
        else:
            pkg = dev.get("package")
            if is_physical(p, sch):
                if not pkg:
                    missing.append((pn, "device has no package (no footprint)", f"{dsn}{p.get('device', '')}"))
                elif (lib, pkg) not in sch.packages:
                    missing.append((pn, "package not found in embedded libraries", f"{lib}:{pkg}"))
    # ---- unresolved connections ---------------------------------------------
    fan = collections.Counter(r[0] for r in rows)
    single = sorted(n for n, c in fan.items() if c == 1)
    unconnected = []   # (part, gate, pin, direction)
    for pn, gates in placed_gates.items():
        p = sch.parts.get(pn)
        if p is None or not is_physical(p, sch):
            continue
        ds, _ = sch.device(p)
        if ds is None:
            continue
        connected = {(g, pin) for g, pin, _, _, _ in part_pins.get(pn, [])}
        for g in ds.find("gates").findall("gate"):
            if g.get("name") not in gates:
                continue
            sym = sch.symbols.get((p.get("library", ""), g.get("symbol")))
            if sym is None:
                continue
            for pin in sym.findall("pin"):
                if (g.get("name"), pin.get("name")) not in connected:
                    unconnected.append((pn, g.get("name"), pin.get("name"), pin.get("direction", "io")))
    no_value = sorted(pn for pn, p in sch.parts.items() if is_physical(p, sch) and not p.get("value"))
    sch_phys = {pn for pn, p in sch.parts.items() if is_physical(p, sch)}
    only_sch = sorted(sch_phys - set(elements), key=natural_key)
    only_brd = sorted(set(elements) - sch_phys, key=natural_key)
    pkg_mismatch = []
    for pn in sorted(sch_phys & set(elements), key=natural_key):
        _, dev = sch.device(sch.parts[pn])
        spk = dev.get("package", "") if dev is not None else ""
        bpk = elements[pn].get("package", "")
        if spk and bpk and spk != bpk:
            pkg_mismatch.append((pn, spk, bpk))
    sch_nets = set(fan)
    brd_sig = set(signals)
    nets_only_sch = sorted(sch_nets - brd_sig)
    nets_only_brd = sorted(brd_sig - sch_nets)

    # ---- connection report ----------------------------------------------------
    rel_sch, rel_brd = os.path.relpath(sch_path, ROOT), os.path.relpath(brd_path, ROOT)
    L = []
    L.append(f"# {board} — Component-to-net connection report\n")
    L.append(f"Project AERIS-10 · Drawing ID ELEC-CON-{board} · Rev A · {today} · Status: SOURCE-DERIVED  ")
    L.append(f"Source: `{rel_sch}` (EAGLE {sch.root.get('version')}), `{rel_brd}`; generated by `tools/gen_schematic_reports.py`.\n")
    L.append("## 1. Summary\n")
    L.append("| Item | Count |\n|---|---|")
    L.append(f"| Sheets | {len(sch.sheets)} |")
    L.append(f"| Parts (all) / physical | {len(sch.parts)} / {len(sch_phys)} |")
    L.append(f"| Nets | {len(fan)} |")
    L.append(f"| Pin connections | {len(rows)} |")
    L.append(f"| Single-pin nets | {len(single)} |")
    L.append(f"| Unconnected pins on placed gates | {len(unconnected)} |")
    L.append(f"| Physical parts without value | {len(no_value)} |")
    L.append(f"| Board airwires (unrouted connections, layer 19) | {sum(airwires.values())} |")
    L.append(f"| Missing symbol/footprint records | {len(missing)} |\n")
    # connectors
    L.append("## 2. Connector pin-outs\n")
    L.append("Parts whose package name or prefix identifies a connector (header, SMA, terminal block, USB).\n")
    conns = []
    for pn in sorted(sch_phys, key=natural_key):
        p = sch.parts[pn]
        _, dev = sch.device(p)
        pkg = (dev.get("package", "") if dev is not None else "") or ""
        up = pkg.upper()
        if pn.rstrip("0123456789") in ("J", "X", "JP", "SV", "CON", "SMA", "USB", "K") or any(
                k in up for k in ("SMA", "PINHD", "HEADER", "USB", "TERMINAL", "22-23", "53047", "MOLEX", "SOCKET", "MINIUSB", "MICROUSB", "JST")):
            conns.append(pn)
    for pn in conns:
        p = sch.parts[pn]
        _, dev = sch.device(p)
        pkg = dev.get("package", "") if dev is not None else ""
        L.append(f"### {pn} — {p.get('value') or p.get('deviceset')} ({pkg})\n")
        L.append("| Pad | Pin name | Net | Sheet |\n|---|---|---|---|")
        for g, pin, pad, nn, si in sorted(part_pins.get(pn, []), key=lambda t: natural_key(t[2] or t[1])):
            L.append(f"| {pad} | {pin} | `{nn}` | {si} |")
        L.append("")
    L.append("## 3. Net fan-out (nets with ≥ 8 connections)\n")
    L.append("| Net | Connections | Class |\n|---|---|---|")
    for nn, c in sorted(fan.items(), key=lambda kv: -kv[1]):
        if c >= 8:
            L.append(f"| `{nn}` | {c} | {net_class.get(nn, '0')} |")
    L.append("\n## 4. Component-to-net table\n")
    L.append("Full machine-readable form: `netlists/" + board + "_netlist_by_part.csv`. Physical parts only; pads shown when the device defines a package connection.\n")
    L.append("| Part | Value | Device / package | Connections (pad:net) |\n|---|---|---|---|")
    for pn in sorted(sch_phys, key=natural_key):
        p = sch.parts[pn]
        _, dev = sch.device(p)
        pkg = dev.get("package", "") if dev is not None else ""
        pins = sorted(part_pins.get(pn, []), key=lambda t: natural_key(t[2] or t[1]))
        conn = ", ".join(f"{(pad or pin)}:`{nn}`" for g, pin, pad, nn, si in pins)
        if len(conn) > 600:
            conn = conn[:600] + f" … ({len(pins)} pins, see CSV)"
        L.append(f"| {pn} | {p.get('value', '')} | {p.get('deviceset', '')}{p.get('device', '')} / {pkg} | {conn} |")
    with open(os.path.join(con_dir, f"{board}_connection_report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")

    # ---- unresolved report ----------------------------------------------------
    U = [f"# {board} — Unresolved / suspicious connections\n",
         f"Project AERIS-10 · ELEC-UNR-{board} · Rev A · {today} · Status: SOURCE-DERIVED (automatic checks; each item needs the designer's disposition)  ",
         f"Source: `{rel_sch}`, `{rel_brd}`; generated by `tools/gen_schematic_reports.py`. Nothing here was changed in the design.\n"]
    U.append(f"## 1. Single-pin nets ({len(single)})\n")
    U.append("A named net connected to exactly one pin: either an intentional test point / unused output, or a missing wire. Each needs a disposition.\n")
    if single:
        U.append("| Net | Part | Pin | Sheet |\n|---|---|---|---|")
        for nn in single:
            r = next(r for r in rows if r[0] == nn)
            U.append(f"| `{nn}` | {r[1]} | {r[3]} (pad {r[4]}) | {r[5]} |")
    U.append(f"\n## 2. Unconnected pins on placed gates ({len(unconnected)})\n")
    U.append("Symbol pins with no net. Pins of direction `in`, `pwr` or `sup` are listed first because an open input/supply is usually a defect; `nc`, `pas`, `io`, `out` are frequently intentional.\n")
    if unconnected:
        order = {"in": 0, "pwr": 0, "sup": 0, "io": 1, "out": 2, "pas": 3, "oc": 3, "hiz": 3, "nc": 4}
        unconnected.sort(key=lambda t: (order.get(t[3], 2), natural_key(t[0]), t[1], natural_key(t[2])))
        U.append("| Part | Gate | Pin | Direction |\n|---|---|---|---|")
        for pn, g, pin, d in unconnected:
            U.append(f"| {pn} | {g} | {pin} | {d} |")
    U.append(f"\n## 3. Physical parts without a value ({len(no_value)})\n")
    U.append(", ".join(no_value) if no_value else "none")
    U.append(f"\n\n## 4. Schematic ↔ board consistency\n")
    U.append(f"- Parts only in schematic (not placed on the board): {len(only_sch)} — {', '.join(only_sch) if only_sch else 'none'}")
    U.append(f"- Elements only on the board (not in schematic): {len(only_brd)} — {', '.join(only_brd) if only_brd else 'none'}")
    U.append(f"- Package mismatches: {len(pkg_mismatch)}" + ("".join(f"\n  - {pn}: sch `{a}` vs brd `{b}`" for pn, a, b in pkg_mismatch) if pkg_mismatch else ""))
    U.append(f"- Nets only in schematic: {len(nets_only_sch)} — {', '.join('`'+n+'`' for n in nets_only_sch[:60])}{' …' if len(nets_only_sch) > 60 else ''}")
    U.append(f"- Signals only on the board: {len(nets_only_brd)} — {', '.join('`'+n+'`' for n in nets_only_brd[:60])}{' …' if len(nets_only_brd) > 60 else ''}")
    U.append(f"\n## 5. Unrouted connections on the board (airwires, EAGLE layer 19): {sum(airwires.values())}\n")
    if airwires:
        U.append("| Signal | Airwires |\n|---|---|")
        for nn, c in airwires.most_common(40):
            U.append(f"| `{nn}` | {c} |")
        if len(airwires) > 40:
            U.append(f"| … {len(airwires) - 40} more signals | |")
    with open(os.path.join(net_dir, f"{board}_unresolved_connections.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(U) + "\n")
    M = [f"# {board} — Missing symbol / footprint report\n",
         f"Project AERIS-10 · ELEC-LIB-{board} · Rev A · {today} · Source: `{rel_sch}` (libraries are embedded in the file).\n",
         f"Checked {len(sch.parts)} parts: deviceset present, every gate's symbol present, device variant present, package present for physical parts.\n"]
    if missing:
        M.append("| Part | Problem | Reference |\n|---|---|---|")
        for pn, prob, ref in missing:
            M.append(f"| {pn} | {prob} | `{ref}` |")
    else:
        M.append("**Result: no missing symbols or footprints** — every part resolves to an embedded symbol and package.")
    M.append("\nNote: 3-D models (`package3d_urn`) reference Autodesk's online library and are not embedded; "
             "they are not required for fabrication but are absent for STEP assembly export.")
    with open(os.path.join(net_dir, f"{board}_missing_symbols_footprints.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(M) + "\n")
    print(f"{board}: nets={len(fan)} pins={len(rows)} single={len(single)} unconnected={len(unconnected)} "
          f"no_value={len(no_value)} only_sch={len(only_sch)} only_brd={len(only_brd)} pkg_mismatch={len(pkg_mismatch)} "
          f"airwires={sum(airwires.values())} missing_lib={len(missing)}")
    return 1 if missing else 0


def natural_key(s: str):
    import re
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s or "")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", choices=sorted(BOARDS), default=None)
    ap.add_argument("--out", default=os.path.join(ROOT, "engineering", "ELECTRICAL"))
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    rc = 0
    for b in ([a.board] if a.board else sorted(BOARDS)):
        try:
            rc |= process(b, a.out, a.date)
        except ET.ParseError as exc:
            print("ERROR parsing", b, exc)
            return 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
