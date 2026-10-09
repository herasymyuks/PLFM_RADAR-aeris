#!/usr/bin/env python3
"""gen_verilog_hierarchy.py - Verilog module hierarchy extractor (AERIS-10).

Parses every ``.v`` file under ``--rtl`` (recursively, nothing skipped), finds
``module <name>`` definitions and module instantiations
(``<module> [#(...)] <instance> (``), and writes:

  <out>/fpga_module_hierarchy.dot   Graphviz hierarchy (top = --top)
  <out>/fpga_module_hierarchy.md    evidence table (module, file:line, instantiated by, status)

Status values: DEFINED / MISSING / PRIMITIVE / UNUSED.

Non-destructive: only writes the two output files; never touches the RTL.
Dependencies: Python 3.8+ standard library only.
Exit codes: 0 = success and every instantiated module has a definition or is a
Xilinx primitive; 1 = at least one instantiated module has no definition in the
RTL tree (the outputs are still written); 2 = usage / I/O error.
"""
import argparse
import os
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import date

VERILOG_KEYWORDS = {
    "always", "and", "assign", "automatic", "begin", "bit", "buf", "bufif0", "bufif1",
    "byte", "case", "casex", "casez", "cell", "cmos", "config", "const", "deassign",
    "default", "defparam", "design", "disable", "do", "edge", "else", "end", "endcase",
    "endconfig", "endfunction", "endgenerate", "endmodule", "endprimitive",
    "endspecify", "endtable", "endtask", "enum", "event", "for", "force", "forever",
    "fork", "function", "generate", "genvar", "highz0", "highz1", "if", "ifnone",
    "incdir", "include", "initial", "inout", "input", "instance", "int", "integer",
    "join", "large", "liblist", "library", "localparam", "logic", "longint",
    "macromodule", "medium", "module", "nand", "negedge", "nmos", "nor",
    "noshowcancelled", "not", "notif0", "notif1", "or", "output", "package",
    "parameter", "pmos", "posedge", "primitive", "pull0", "pull1", "pulldown",
    "pullup", "pulsestyle_onevent", "pulsestyle_ondetect", "rcmos", "real",
    "realtime", "reg", "release", "repeat", "return", "rnmos", "rpmos", "rtran",
    "rtranif0", "rtranif1", "scalared", "shortint", "showcancelled", "signed",
    "small", "specify", "specparam", "static", "string", "strong0", "strong1",
    "struct", "supply0", "supply1", "table", "task", "time", "tran", "tranif0",
    "tranif1", "tri", "tri0", "tri1", "triand", "trior", "trireg", "typedef",
    "unique", "unsigned", "use", "uwire", "vectored", "void", "wait", "wand",
    "weak0", "weak1", "while", "wire", "wor", "xnor", "xor",
    # SystemVerilog words seen in the testbench
    "assert", "property", "assume", "cover", "sequence", "final",
}

# 7-series UNISIM primitives seen or plausible in this design.  Anything else
# instantiated without a definition is reported as MISSING.
XILINX_PRIMITIVES = {
    "BUFG", "BUFGCE", "BUFH", "BUFIO", "BUFR", "BUFMR", "IBUF", "IBUFG", "IBUFDS",
    "IBUFGDS", "OBUF", "OBUFDS", "OBUFT", "IOBUF", "IDDR", "ODDR", "IDELAYE2",
    "ODELAYE2", "IDELAYCTRL", "ISERDESE2", "OSERDESE2", "MMCME2_BASE", "MMCME2_ADV",
    "PLLE2_BASE", "PLLE2_ADV", "DSP48E1", "RAMB18E1", "RAMB36E1", "FDRE", "FDCE",
    "FDPE", "FDSE", "LUT1", "LUT2", "LUT3", "LUT4", "LUT5", "LUT6", "STARTUPE2",
    "BSCANE2", "ICAPE2", "XADC",
}

MODULE_RE = re.compile(r"(?<![\w$.])module\s+([A-Za-z_]\w*)")
# <type> [#( balanced-one-level )] <inst> (
# Either "<type> #( ... ) <inst> (" or "<type> <inst> (" - whitespace between the
# two identifiers is mandatory in the second form so that "for (" / "if (" or a
# function call "name(" can never be split into two identifiers.
INST_RE = re.compile(
    r"(?<![\w$.#])([A-Za-z_]\w*)"
    r"(?:\s*(#\s*\((?:[^()]|\([^()]*\))*\))\s*|\s+)"
    r"([A-Za-z_]\w*)\s*\("
)


def strip_comments_and_strings(text):
    """Replace comments and string literals with spaces, preserving newlines."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            seg = text[i:j]
            out.append("".join("\n" if ch == "\n" else " " for ch in seg))
            i = j
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(" " * (j - i))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def scan(rtl_dir):
    defs = OrderedDict()            # module -> (relpath, line)
    insts = []                      # (type, inst_name, parent_module, relpath, line)
    files = []
    for root, _dirs, names in os.walk(rtl_dir):
        for name in sorted(names):
            if name.lower().endswith(".v"):
                files.append(os.path.join(root, name))
    files.sort()
    for path in files:
        rel = os.path.relpath(path, rtl_dir)
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
        text = strip_comments_and_strings(raw)
        # module spans: (name, start, end)
        spans = []
        for m in MODULE_RE.finditer(text):
            name = m.group(1)
            end = text.find("endmodule", m.end())
            end = len(text) if end == -1 else end
            spans.append((name, m.start(), end))
            if name in defs:
                print(f"WARNING: module {name} redefined at {rel}:{line_of(text, m.start())} "
                      f"(first at {defs[name][0]}:{defs[name][1]})", file=sys.stderr)
            else:
                defs[name] = (rel, line_of(text, m.start()))
        for m in INST_RE.finditer(text):
            mtype, inst = m.group(1), m.group(3)
            if mtype in VERILOG_KEYWORDS or inst in VERILOG_KEYWORDS:
                continue
            if mtype == "module":
                continue
            parent = None
            for name, s, e in spans:
                if s <= m.start() < e:
                    parent = name
                    break
            if parent is None:
                continue  # text outside any module (e.g. chirp_lut_init.v include)
            insts.append((mtype, inst, parent, rel, line_of(text, m.start())))
    return defs, insts, [os.path.relpath(f, rtl_dir) for f in files]


def classify(name, defs):
    if name in defs:
        return "DEFINED"
    if name in XILINX_PRIMITIVES:
        return "PRIMITIVE"
    return "MISSING"


def dot_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_dot(path, defs, insts, top, rtl_label, files):
    by_type = defaultdict(list)
    for mtype, inst, parent, rel, line in insts:
        by_type[mtype].append((inst, parent, rel, line))
    all_types = set(defs) | set(by_type)
    instantiated = set(by_type)
    missing = sorted(t for t in by_type if classify(t, defs) == "MISSING")

    title = (
        "AERIS-10 - FPGA RTL module hierarchy (auto-generated)\\l"
        "Drawing ID: SD-01   Revision: A   Date: 2026-10-09   Status: SOURCE-DERIVED\\l"
        f"Source: {dot_escape(rtl_label)}/*.v ({len(files)} files) parsed by tools/gen_verilog_hierarchy.py\\l"
        f"Modules defined: {len(defs)}   instantiated types: {len(instantiated)}   "
        f"MISSING definitions: {len(missing)} ({', '.join(missing) if missing else 'none'})\\l"
        "Edge label = instance name @line-of-instantiation in the parent file. Solid = defined in repo; dashed red = no definition in repo; grey = Xilinx UNISIM primitive; "
        "dotted outline = defined but never instantiated.\\l"
    )
    lines = [
        "digraph fpga_module_hierarchy {",
        "  rankdir=TB; splines=true; nodesep=0.2; ranksep=0.9; concentrate=false;",
        f'  graph [label="{title}", labelloc=t, labeljust=l, fontname="Helvetica", fontsize=11];',
        '  node [fontname="Helvetica", fontsize=10, shape=box, style="filled", fillcolor="#f4f6f8", color="#2c3e50"];',
        '  edge [fontname="Helvetica", fontsize=8, color="#2c3e50"];',
        "",
    ]
    # nodes
    for t in sorted(all_types):
        st = classify(t, defs)
        if st == "DEFINED":
            rel, line = defs[t]
            label = f"{t}\\n{rel}:{line}"
            attrs = f'label="{dot_escape(label)}"'
            if t == top:
                attrs += ', fillcolor="#d6eaf8", penwidth=2'
            elif t not in instantiated:
                attrs += ', style="filled,dotted", fillcolor="#fdf2e9"'
                attrs = attrs.replace(f'label="{dot_escape(label)}"',
                                      f'label="{dot_escape(label)}\\n(UNUSED: not instantiated)"')
        elif st == "PRIMITIVE":
            attrs = f'label="{t}\\n(Xilinx UNISIM primitive)", fillcolor="#d5d8dc", color="#7f8c8d", fontcolor="#2c3e50"'
        else:
            attrs = (f'label="{t}\\nMISSING: no definition in repo", style="filled,dashed", '
                     f'fillcolor="#fdecea", color="#c0392b", fontcolor="#c0392b", penwidth=1.5')
        lines.append(f'  "{t}" [{attrs}];')
    lines.append("")
    if top in defs:
        lines.append(f'  {{ rank=source; "{top}"; }}')
    # edges: one per instantiation, grouped so repeated instances of the same type share an edge label
    grouped = defaultdict(list)
    for mtype, inst, parent, rel, line in insts:
        grouped[(parent, mtype)].append(f"{inst} @{line}")
    for (parent, mtype), labels in sorted(grouped.items()):
        st = classify(mtype, defs)
        lab = "\\n".join(labels)
        extra = ""
        if st == "MISSING":
            extra = ', color="#c0392b", style=dashed, fontcolor="#c0392b"'
        elif st == "PRIMITIVE":
            extra = ', color="#7f8c8d", fontcolor="#7f8c8d"'
        lines.append(f'  "{parent}" -> "{mtype}" [label="{dot_escape(lab)}"{extra}];')
    lines.append("}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_md(path, defs, insts, top, rtl_label, files, exit_code):
    by_type = defaultdict(list)
    for mtype, inst, parent, rel, line in insts:
        by_type[mtype].append((inst, parent, rel, line))
    all_types = sorted(set(defs) | set(by_type))
    rows = []
    for t in all_types:
        st = classify(t, defs)
        if st == "DEFINED" and t not in by_type:
            st = "UNUSED"
        where = f"`{defs[t][0]}:{defs[t][1]}`" if t in defs else "-"
        users = "; ".join(f"`{parent}` as `{inst}` (`{rel}:{line}`)" for inst, parent, rel, line in by_type.get(t, []))
        rows.append((t, where, users or "-", st))
    counts = defaultdict(int)
    for r in rows:
        counts[r[3]] += 1
    md = [
        "# FPGA RTL Module Hierarchy - AERIS-10 (auto-generated)",
        "",
        f"Generated {date.today().isoformat()} by `tools/gen_verilog_hierarchy.py` from `{rtl_label}` "
        f"({len(files)} Verilog files, all parsed). Top module requested: `{top}` "
        f"({'found' if top in defs else 'NOT FOUND'}). Script exit code: {exit_code}.",
        "",
        "Drawing SD-01, revision A, status SOURCE-DERIVED. Native file: `fpga_module_hierarchy.dot`.",
        "",
        "Parsing method: comments and string literals are blanked, then `module <name>` and "
        "`<type> [#(...)] <instance> (` patterns are matched; Verilog keywords are excluded; "
        "`BUFG/IBUFDS/IDDR/...` are classified as Xilinx UNISIM primitives. Line numbers refer to the "
        "original files. This is a lexical scan, not an elaboration: generate-loop replication counts "
        "(e.g. 8x IBUFDS/IDDR in `ad9484_interface_400m.v`) are shown once.",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for k in ("DEFINED", "MISSING", "PRIMITIVE", "UNUSED"):
        md.append(f"| {k} | {counts.get(k, 0)} |")
    md += [
        "",
        "| Module | Defined at (file:line) | Instantiated by (parent as instance, file:line) | Status |",
        "|---|---|---|---|",
    ]
    for t, where, users, st in rows:
        md.append(f"| `{t}` | {where} | {users} | **{st}** |")
    md += [
        "",
        "## Files scanned",
        "",
    ]
    for f in files:
        n_defs = sum(1 for v in defs.values() if v[0] == f)
        md.append(f"- `{f}` - {n_defs} module definition(s)")
    md += [
        "",
        "## Notes",
        "",
        "- MISSING = instantiated somewhere in the tree but no `module` of that name exists in the scanned files. "
        "Names with AXI4-Stream ports (`s_axis_config_*`, `m_axis_data_*`) indicate Xilinx IP cores whose `.xci` "
        "is not in the repository; the others are RTL modules that were never committed.",
        "- UNUSED = defined but never instantiated (orphans or the testbench root).",
        "- The script does not evaluate `` `ifdef `` blocks; all text is scanned.",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rtl", required=True, help="directory containing the .v files (scanned recursively)")
    ap.add_argument("--out", required=True, help="output directory for the .dot and .md files")
    ap.add_argument("--top", default="radar_system_top", help="top module name (default radar_system_top)")
    args = ap.parse_args()
    if not os.path.isdir(args.rtl):
        print(f"ERROR: --rtl {args.rtl} is not a directory", file=sys.stderr)
        return 2
    try:
        os.makedirs(args.out, exist_ok=True)
        defs, insts, files = scan(args.rtl)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not files:
        print("ERROR: no .v files found", file=sys.stderr)
        return 2
    missing = sorted({t for t, *_ in insts if classify(t, defs) == "MISSING"})
    exit_code = 1 if missing else 0
    rtl_label = args.rtl.rstrip("/")
    write_dot(os.path.join(args.out, "fpga_module_hierarchy.dot"), defs, insts, args.top, rtl_label, files)
    write_md(os.path.join(args.out, "fpga_module_hierarchy.md"), defs, insts, args.top, rtl_label, files, exit_code)
    print(f"files={len(files)} modules_defined={len(defs)} instantiations={len(insts)} missing={len(missing)}")
    for t in missing:
        users = [f"{p} ({r}:{l})" for mt, i, p, r, l in insts if mt == t]
        print(f"  MISSING {t}: instantiated by {', '.join(users)}")
    if args.top not in defs:
        print(f"WARNING: top module {args.top} not defined in the scanned files", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
