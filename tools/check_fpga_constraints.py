#!/usr/bin/env python3
"""
check_fpga_constraints.py — FPGA constraint completeness checker for AERIS-10.

Parses the Verilog top-level module port list and the XDC constraint file and reports:
  * unresolved placeholders ([PIN_NUMBER], [PIN_NUMBER_P], [BANK_NUMBER], [DATE], ...)
  * top-level ports with no PACKAGE_PIN constraint
  * top-level ports with no IOSTANDARD constraint (pattern-aware for simple globs)
  * constraints that reference ports absent from the RTL
  * invalid property names (e.g. PACKAGE_PIN_BANK is not a Vivado property)
  * clocks defined vs. clock input ports

Non-destructive, read-only.
Usage:
    python3 tools/check_fpga_constraints.py [--top 9_Firmware/9_2_FPGA/radar_system_top.v]
                                           [--xdc 9_Firmware/9_2_FPGA/cntrt.xdc] [--json]
Exit codes:
    0  no placeholders and all ports constrained
    1  placeholders or unconstrained ports found
    2  input file missing / parse error
Dependencies: Python 3.8+ standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_RE = re.compile(r"\[(PIN_NUMBER(?:_[PN])?|BANK_NUMBER|DATE|XC7A100T)\]")
VALID_PROPS = {"PACKAGE_PIN", "IOSTANDARD", "PULLUP", "PULLDOWN", "SLEW", "DRIVE", "DIFF_TERM",
               "IOB", "CLOCK_DEDICATED_ROUTE", "BITSTREAM.CONFIG.UNUSEDPIN", "CFGBVS", "CONFIG_VOLTAGE",
               "BITSTREAM.GENERAL.COMPRESS", "IN_TERM", "KEEPER"}


def parse_top_ports(top: Path, module: str):
    """Return list of (name, direction, width) for module's ANSI port list."""
    text = top.read_text(errors="ignore")
    m = re.search(rf"module\s+{re.escape(module)}\s*(?:#\s*\(.*?\)\s*)?\((.*?)\);", text, re.S)
    if not m:
        raise ValueError(f"module {module} not found in {top}")
    body = m.group(1)
    ports = []
    cur_dir, cur_w = None, 1
    for raw in body.splitlines():
        line = raw.split("//")[0].strip()
        if not line:
            continue
        dm = re.match(r"^(input|output|inout)\s+(?:wire|reg)?\s*(?:\[(\d+)\s*:\s*(\d+)\])?\s*(.*)$", line)
        if dm:
            cur_dir = dm.group(1)
            cur_w = abs(int(dm.group(2)) - int(dm.group(3))) + 1 if dm.group(2) else 1
            rest = dm.group(4)
        else:
            rest = line
        for name in [n.strip() for n in rest.rstrip(",").split(",") if n.strip()]:
            name = name.strip().rstrip(")").strip()
            if re.match(r"^[A-Za-z_]\w*$", name) and cur_dir:
                ports.append((name, cur_dir, cur_w))
    return ports


def expand_bits(ports):
    out = []
    for name, d, w in ports:
        if w == 1:
            out.append(name)
        else:
            out.extend(f"{name}[{i}]" for i in range(w))
    return out


def parse_xdc(xdc: Path):
    lines = xdc.read_text(errors="ignore").splitlines()
    placeholders, props, clocks, bad_props = [], [], [], []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("#"):
            # placeholders inside comments are informational only
            if PLACEHOLDER_RE.search(s):
                placeholders.append((i, s, "comment"))
            continue
        for ph in PLACEHOLDER_RE.findall(s):
            placeholders.append((i, s, ph))
        pm = re.match(r"set_property\s+(\S+)\s+(\S+)\s+\[get_ports\s+(?:\{([^}]+)\}|([^\]\s]+))\]", s)
        if pm:
            prop, val, p_brace, p_bare = pm.groups()
            ports = p_brace if p_brace is not None else p_bare
            props.append((i, prop, val, ports.strip()))
            if prop not in VALID_PROPS:
                bad_props.append((i, prop, s))
        cm = re.match(r"create_clock\s+-name\s+(\S+)\s+-period\s+(\S+)\s+\[get_ports\s+(?:\{([^}]+)\}|([^\]\s]+))\]", s)
        if cm:
            name, period, c_brace, c_bare = cm.groups()
            clocks.append((i, name, period, (c_brace if c_brace is not None else c_bare).strip()))
    return placeholders, props, clocks, bad_props


def glob_match(pattern: str, candidates):
    """Vivado-style glob where only '*' and '?' are wildcards; '[' and ']' are literal."""
    rx = "".join(".*" if ch == "*" else "." if ch == "?" else re.escape(ch) for ch in pattern)
    rx = re.compile("^" + rx + "$")
    return [c for c in candidates if rx.match(c)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", default=ROOT / "9_Firmware/9_2_FPGA/radar_system_top.v")
    ap.add_argument("--module", default="radar_system_top")
    ap.add_argument("--xdc", default=ROOT / "9_Firmware/9_2_FPGA/cntrt.xdc")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    top, xdc = Path(args.top), Path(args.xdc)
    if not top.exists() or not xdc.exists():
        print(f"ERROR: missing input: {top if not top.exists() else xdc}", file=sys.stderr)
        return 2
    try:
        ports = parse_top_ports(top, args.module)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    bits = expand_bits(ports)
    placeholders, props, clocks, bad_props = parse_xdc(xdc)

    pin_assigned, io_assigned, unknown_refs = set(), set(), []
    for ln, prop, val, pat in props:
        matched = glob_match(pat, bits)
        if not matched:
            unknown_refs.append((ln, prop, pat))
        if prop == "PACKAGE_PIN" and not PLACEHOLDER_RE.fullmatch(val):
            pin_assigned.update(matched)
        if prop == "IOSTANDARD":
            io_assigned.update(matched)

    no_pin = [b for b in bits if b not in pin_assigned]
    no_io = [b for b in bits if b not in io_assigned]
    real_placeholders = [p for p in placeholders if p[2] != "comment"]

    report = {
        "top_module": args.module,
        "port_count": len(ports),
        "port_bit_count": len(bits),
        "placeholder_lines": len(real_placeholders),
        "placeholder_comment_lines": len(placeholders) - len(real_placeholders),
        "ports_bits_without_PACKAGE_PIN": len(no_pin),
        "ports_bits_without_IOSTANDARD": no_io,
        "constraints_referencing_unknown_ports": unknown_refs,
        "invalid_properties": bad_props,
        "clocks": clocks,
        "clock_input_ports": [p[0] for p in ports if p[1] == "input" and ("clk" in p[0] or p[0].endswith("dco_p"))],
    }
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"Top module      : {args.module} ({len(ports)} ports, {len(bits)} bits)")
        print(f"XDC             : {xdc.relative_to(ROOT) if xdc.is_relative_to(ROOT) else xdc}")
        print(f"Placeholders    : {len(real_placeholders)} active lines (+{len(placeholders)-len(real_placeholders)} in comments)")
        print(f"No PACKAGE_PIN  : {len(no_pin)} / {len(bits)} port bits")
        print(f"No IOSTANDARD   : {len(no_io)} port bits -> {no_io}")
        print(f"Unknown port refs: {len(unknown_refs)}")
        for ln, prop, pat in unknown_refs:
            print(f"   line {ln}: {prop} on '{pat}' (no such RTL port)")
        print(f"Invalid props   : {len(bad_props)}")
        for ln, prop, s in bad_props:
            print(f"   line {ln}: {prop} -> {s}")
        print("Clocks          :")
        for ln, name, period, port in clocks:
            print(f"   line {ln}: {name} period {period} ns on {port}")
    ok = not real_placeholders and not no_pin and not bad_props
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
