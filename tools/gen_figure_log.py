#!/usr/bin/env python3
"""Generate manual/FIGURE_LOG.md from the chapter files: every Markdown image in outline order with
its number, chapter, caption, path, size, status (from the caption text) and origin (register ID or
'rendered into manual/figures'). Usage: python3 tools/gen_figure_log.py   (exit 1 if a figure file is missing)
"""
import os, re, datetime as _dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "manual"); CH = os.path.join(MAN, "chapters")
order = [m.group(1) for m in (re.match(r"\| [0-9A-Z]+ \| `chapters/([^`]+)`", l) for l in open(os.path.join(MAN, "00_OUTLINE.md"), encoding="utf-8")) if m]
reg = {}
for line in open(os.path.join(ROOT, "engineering", "DRAWING_REGISTER.md"), encoding="utf-8"):
    m = re.match(r"\| ([A-Z0-9\-]+) \| .+? \| .+? \| (.+?) \| (.+?) \| (.+?) \|", line)
    if m:
        for f in re.findall(r"`([^`]+)`", m.group(2) + " " + m.group(3)):
            reg[os.path.basename(f)] = m.group(1)
STAT = re.compile(r"(?<![A-Z])(ORIGINAL PROJECT FILE|SOURCE-DERIVED|PROPOSED DESIGN|CONCEPTUAL|PARTIAL|BLOCKED[^;)]*|BETA|VERIFIED)(?![A-Z])")
rows, missing, n = [], 0, 0
for fname in order:
    md = open(os.path.join(CH, fname), encoding="utf-8").read()
    for m in re.finditer(r"!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)]+)\)", md):
        n += 1; cap, src = m.group(1), m.group(2); p = os.path.join(ROOT, src)
        ok = os.path.isfile(p); missing += 0 if ok else 1
        st = STAT.search(cap); st = st.group(1) if st else "UNLABELLED"
        origin = reg.get(os.path.basename(src), "rendered for the manual" if src.startswith("manual/figures") else ("original project file" if not src.startswith(("engineering", "beta", "docs")) else "generated (unregistered)"))
        rows.append((n, fname.split("_")[0], cap[:140], src, (os.path.getsize(p) // 1024) if ok else -1, st, origin))
with open(os.path.join(MAN, "FIGURE_LOG.md"), "w", encoding="utf-8") as fh:
    fh.write(f"# Figure log\n\nGenerated {_dt.date.today().isoformat()} by `tools/gen_figure_log.py` — {n} figures, {missing} missing files. Status is taken from the caption text; origin from the drawing register / path.\n\n| # | Ch. | Caption (start) | Path | kB | Status | Origin |\n|---|---|---|---|---|---|---|\n")
    for r in rows:
        fh.write(f"| {r[0]} | {r[1]} | {r[2]} | `{r[3]}` | {r[4]} | {r[5]} | {r[6]} |\n")
    from collections import Counter
    c = Counter(r[5] for r in rows)
    fh.write("\n## By status\n\n| Status | Figures |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in sorted(c.items())))
print(f"{n} figures, {missing} missing; statuses:", dict(__import__('collections').Counter(r[5] for r in rows)))
raise SystemExit(1 if missing else 0)
