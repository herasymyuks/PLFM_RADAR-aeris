#!/usr/bin/env python3
"""
check_doc_links.py — Markdown link and path-reference validator for AERIS-10.

Scans every *.md file (and README.md) for:
  * Markdown links  [text](relative/path)  (http(s) links are skipped)
  * Backticked repository paths such as `10_docs/assembly_guide.md`
and verifies that each target exists relative to the referencing file's directory
or relative to the repository root.

Non-destructive, read-only.
Usage:
    python3 tools/check_doc_links.py [--root PATH] [--include-planning]
Exit codes:
    0  all references resolve
    1  one or more broken references
    2  root not found
Dependencies: Python 3.8+ standard library only.
"""
import argparse
import re
import sys
from urllib.parse import unquote
from pathlib import Path

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
TICK_RE = re.compile(r"`([^`\n]+)`")
PATH_HINT = re.compile(r"^/?(?:[0-9]+_[\w &\-]+|docs|tools|research|README|\.planning)[\w &\-./]*$")
# A backticked path on a line that says it is missing/expected is a documented gap, not a broken link.
DOCUMENTED_MISSING = re.compile(r"missing|absent|does not exist|do not exist|not exist|expected|future|to be written|"
                                r"store under|stored under|archive|will|once|after|promised|referenced|claims?|dead|broken|to be created", re.I)


def iter_md(root: Path, include_planning: bool):
    for p in sorted(root.rglob("*.md")):
        if ".git" in p.parts:
            continue
        if not include_planning and ".planning" in p.parts:
            continue
        yield p


def resolve(ref: str, md: Path, root: Path):
    ref = unquote(ref.split("#", 1)[0])
    if not ref:
        return True
    cands = [md.parent / ref, root / ref.lstrip("/")]
    return any(c.exists() for c in cands)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--include-planning", action="store_true")
    ap.add_argument("--strict", action="store_true", help="also count documented-missing paths as broken")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2
    broken, documented, checked = [], [], 0
    for md in iter_md(root, args.include_planning):
        for n, line in enumerate(md.read_text(errors="ignore").splitlines(), 1):
            refs = []
            for m in LINK_RE.finditer(line):
                t = m.group(1)
                if not t.startswith(("http://", "https://", "mailto:")):
                    refs.append(("link", t))
            for m in TICK_RE.finditer(line):
                t = m.group(1).strip()
                if "/" in t and PATH_HINT.match(t) and " " not in t.split("/")[-1]:
                    refs.append(("path", t))
            for kind, t in refs:
                checked += 1
                if not resolve(t, md, root):
                    rec = (md.relative_to(root).as_posix(), n, kind, t)
                    if kind == "path" and not args.strict and DOCUMENTED_MISSING.search(line):
                        documented.append(rec)
                    else:
                        broken.append(rec)
    print(f"checked {checked} references in markdown files under {root}")
    for f, n, kind, t in broken:
        print(f"BROKEN {kind:4s} {f}:{n} -> {t}")
    if documented:
        print(f"documented-missing paths (not counted; use --strict to count): {len(documented)}")
        for f, n, kind, t in documented:
            print(f"   note {f}:{n} -> {t}")
    print(f"broken: {len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
