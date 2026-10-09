#!/usr/bin/env python3
"""gen_python_module_graph.py - Python GUI module/import graph (AERIS-10).

For every ``.py`` file under ``--src`` (non-recursive by default) the script
parses the file with ``ast`` and records:

  * imports, classified as stdlib / third-party / local (a local import is one
    whose top-level name equals the stem of another .py file in the same tree);
  * imports wrapped in ``try:`` (optional dependencies, drawn dashed);
  * classes and top-level functions defined.

Outputs (in ``--out``):
  python_gui_modules.dot   one cluster per file, edges to third-party packages
                           (grouped in a cluster), local imports as file->file edges
  python_gui_modules.md    evidence table

A file that fails to parse (SyntaxError) is reported, drawn as a red
"SYNTAX ERROR" node and never skipped silently.

Non-destructive; stdlib only; Python 3.10+ (uses sys.stdlib_module_names).
Exit codes: 0 = all files parsed; 1 = at least one file failed to parse
(outputs are still written); 2 = usage / I/O error.
"""
import argparse
import ast
import os
import sys
from collections import OrderedDict
from datetime import date

STDLIB = set(getattr(sys, "stdlib_module_names", ()))
# distribution names for the import names used in this repository (for the table)
DIST = {
    "numpy": "numpy", "scipy": "scipy", "matplotlib": "matplotlib", "sklearn": "scikit-learn",
    "filterpy": "filterpy", "crcmod": "crcmod", "usb": "pyusb", "pyftdi": "pyftdi",
    "pandas": "pandas", "tkinterweb": "tkinterweb", "serial": "pyserial", "ftd3xx": "ftd3xx",
}


def analyse(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as exc:
        return {"error": f"{type(exc).__name__}: {exc.msg} (line {exc.lineno})", "lines": src.count("\n") + 1}
    imports = OrderedDict()  # top-level name -> {"lines": [..], "optional": bool, "names": set()}
    # mark nodes that sit inside a try: body
    optional_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for sub in node.body:
                for n in ast.walk(sub):
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        optional_ids.add(id(n))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                ent = imports.setdefault(top, {"lines": [], "optional": True, "names": set()})
                ent["lines"].append(node.lineno)
                ent["optional"] = ent["optional"] and (id(node) in optional_ids)
                ent["names"].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and not node.module:
                top = "."
            else:
                top = (node.module or "").split(".")[0]
            ent = imports.setdefault(top, {"lines": [], "optional": True, "names": set()})
            ent["lines"].append(node.lineno)
            ent["optional"] = ent["optional"] and (id(node) in optional_ids)
            ent["names"].add(f"{node.module}:{','.join(a.name for a in node.names)}")
    classes = [(n.name, n.lineno) for n in tree.body if isinstance(n, ast.ClassDef)]
    funcs = [(n.name, n.lineno) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    has_main = any(
        isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
        and isinstance(n.test.left, ast.Name) and n.test.left.id == "__name__"
        for n in tree.body
    )
    return {"imports": imports, "classes": classes, "functions": funcs, "lines": src.count("\n") + 1,
            "has_main": has_main}


def classify(top, local_names):
    if top in local_names:
        return "local"
    if top in STDLIB or top == ".":
        return "stdlib"
    return "third-party"


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("<", "\\<").replace(">", "\\>").replace("{", "\\{").replace("}", "\\}").replace("|", "\\|")


def write_dot(path, results, src_label):
    local_names = {os.path.splitext(f)[0] for f in results}
    third = OrderedDict()
    for f, r in results.items():
        if "error" in r:
            continue
        for top, ent in r["imports"].items():
            if classify(top, local_names) == "third-party":
                third.setdefault(top, []).append(f)
    n_err = sum(1 for r in results.values() if "error" in r)
    title = (
        "AERIS-10 - Python GUI modules, imports and definitions (auto-generated)\\l"
        "Drawing ID: SD-05   Revision: A   Date: 2026-10-09   Status: SOURCE-DERIVED\\l"
        f"Source: {esc(src_label)}/*.py ({len(results)} files) parsed with ast by tools/gen_python_module_graph.py\\l"
        f"Files with syntax errors: {n_err}. Solid edge = unconditional import; dashed edge = import inside try/except (optional). "
        "stdlib imports are listed inside each file node, not drawn as edges. No file imports another GUI file (no local edges found).\\l"
    )
    out = [
        "digraph python_gui_modules {",
        "  rankdir=LR; nodesep=0.25; ranksep=1.2; splines=true;",
        f'  graph [label="{title}", labelloc=t, labeljust=l, fontname="Helvetica", fontsize=11];',
        '  node [fontname="Helvetica", fontsize=9, shape=record, style="filled", fillcolor="#f4f6f8", color="#2c3e50"];',
        '  edge [fontname="Helvetica", fontsize=8, color="#2c3e50"];',
        "",
    ]
    for i, (f, r) in enumerate(results.items()):
        node = "f_" + os.path.splitext(f)[0]
        out.append(f'  subgraph "cluster_{i}" {{ label="{esc(f)}"; style="rounded"; color="#95a5a6"; fontsize=9;')
        if "error" in r:
            out.append(f'    "{node}" [label="{{{esc(f)}|SYNTAX ERROR\\n{esc(r["error"])}|{r["lines"]} lines - NOT PARSED}}", '
                       f'fillcolor="#fdecea", color="#c0392b", fontcolor="#c0392b", penwidth=2];')
        else:
            cls = "\\n".join(f"class {n} (:{ln})" for n, ln in r["classes"]) or "(no classes)"
            fns = "\\n".join(f"def {n}() (:{ln})" for n, ln in r["functions"]) or "(no top-level functions)"
            std = ", ".join(sorted(t for t in r["imports"] if classify(t, local_names) == "stdlib")) or "-"
            entry = "has __main__ entry" if r["has_main"] else "no __main__ entry"
            out.append(f'    "{node}" [label="{{{esc(f)}\\n{r["lines"]} lines - {entry}|{esc(cls)}|{esc(fns)}|stdlib: {esc(std)}}}"];')
        out.append("  }")
    out.append('  subgraph "cluster_third" { label="third-party packages (PyPI distribution)"; style="rounded,filled"; fillcolor="#fbfbfb"; color="#95a5a6";')
    for top in third:
        dist = DIST.get(top, "?")
        out.append(f'    "pkg_{top}" [shape=box, fillcolor="#e8f6f3", color="#1e8449", label="{esc(top)}\\n({esc(dist)})"];')
    out.append("  }")
    for f, r in results.items():
        if "error" in r:
            continue
        node = "f_" + os.path.splitext(f)[0]
        for top, ent in r["imports"].items():
            kind = classify(top, local_names)
            if kind == "third-party":
                style = ', style=dashed, label="optional (try/except)"' if ent["optional"] else ""
                out.append(f'  "{node}" -> "pkg_{top}" [color="#1e8449"{style}];')
            elif kind == "local":
                out.append(f'  "{node}" -> "f_{top}" [color="#8e44ad", penwidth=2, label="local import"];')
    out.append("}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def write_md(path, results, src_label, exit_code):
    local_names = {os.path.splitext(f)[0] for f in results}
    md = [
        "# Python GUI Modules - imports and definitions (auto-generated)",
        "",
        f"Generated {date.today().isoformat()} by `tools/gen_python_module_graph.py` from `{src_label}` "
        f"({len(results)} files). Python {sys.version.split()[0]} `ast`; stdlib classification uses "
        f"`sys.stdlib_module_names` of the running interpreter. Script exit code: {exit_code}.",
        "",
        "Drawing SD-05, revision A, status SOURCE-DERIVED. Native file: `python_gui_modules.dot`.",
        "",
        "| File | Lines | Parse | Classes (line) | Top-level functions (line) | stdlib imports | third-party imports (line; optional?) | local imports |",
        "|---|---:|---|---|---|---|---|---|",
    ]
    for f, r in results.items():
        if "error" in r:
            md.append(f"| `{f}` | {r['lines']} | **SYNTAX ERROR** - {r['error']} | - | - | - | - | - |")
            continue
        cls = ", ".join(f"`{n}` ({ln})" for n, ln in r["classes"]) or "-"
        fns = ", ".join(f"`{n}` ({ln})" for n, ln in r["functions"]) or "-"
        std, third, local = [], [], []
        for top, ent in r["imports"].items():
            k = classify(top, local_names)
            lines = ",".join(str(x) for x in ent["lines"])
            tag = f"`{top}` ({lines}{'; optional' if ent['optional'] else ''})"
            {"stdlib": std, "third-party": third, "local": local}[k].append(tag)
        md.append(f"| `{f}` | {r['lines']} | OK{' (has `__main__`)' if r['has_main'] else ''} | {cls} | {fns} | "
                  f"{', '.join(std) or '-'} | {', '.join(third) or '-'} | {', '.join(local) or '-'} |")
    # package summary
    pk = OrderedDict()
    for f, r in results.items():
        if "error" in r:
            continue
        for top, ent in r["imports"].items():
            if classify(top, local_names) == "third-party":
                pk.setdefault(top, []).append(f + (" (optional)" if ent["optional"] else ""))
    md += ["", "## Third-party packages", "", "| Import name | PyPI distribution | Used by |", "|---|---|---|"]
    for top, users in pk.items():
        md.append(f"| `{top}` | {DIST.get(top, 'UNKNOWN - verify')} | {', '.join(users)} |")
    md += [
        "",
        "## Notes",
        "",
        "- `optional` = every import of that package sits inside a `try:` block (the file degrades when the package is absent).",
        "- `local` = import name equals another `.py` file stem in the scanned directory. None were found: the GUI versions are independent monolithic scripts.",
        "- Classification is lexical; whether a third-party module is actually exercised at runtime is not determined here.",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="directory with the .py files")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--recursive", action="store_true", help="also scan sub-directories")
    args = ap.parse_args()
    if not os.path.isdir(args.src):
        print(f"ERROR: --src {args.src} is not a directory", file=sys.stderr)
        return 2
    files = []
    if args.recursive:
        for root, _d, names in os.walk(args.src):
            files += [os.path.join(root, n) for n in names if n.endswith(".py")]
    else:
        files = [os.path.join(args.src, n) for n in os.listdir(args.src) if n.endswith(".py")]
    files.sort()
    if not files:
        print("ERROR: no .py files found", file=sys.stderr)
        return 2
    results = OrderedDict()
    for p in files:
        results[os.path.relpath(p, args.src)] = analyse(p)
    errors = [f for f, r in results.items() if "error" in r]
    exit_code = 1 if errors else 0
    try:
        os.makedirs(args.out, exist_ok=True)
        write_dot(os.path.join(args.out, "python_gui_modules.dot"), results, args.src.rstrip("/"))
        write_md(os.path.join(args.out, "python_gui_modules.md"), results, args.src.rstrip("/"), exit_code)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"files={len(files)} parsed={len(files) - len(errors)} syntax_errors={len(errors)}")
    for f in errors:
        print(f"  SYNTAX ERROR {f}: {results[f]['error']}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
