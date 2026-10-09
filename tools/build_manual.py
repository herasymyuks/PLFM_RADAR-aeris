#!/usr/bin/env python3
"""Build the AERIS-10 manual: concatenate manual/chapters/*.md in the order of manual/00_OUTLINE.md,
number figures, resolve relative image links, write manual/AERIS10_MANUAL.md, manual/build/AERIS10_MANUAL.html
(images embedded as data URIs; SVG inline) and manual/build/AERIS10_MANUAL.pdf (headless Chrome).
`--check` only validates: every chapter listed exists, every image/link target exists, no empty chapter.
Stdlib only (+ Google Chrome for the PDF). Exit 0 ok, 1 validation problems, 2 error.
"""
import argparse, base64, html, os, re, subprocess, sys, datetime as _dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "manual"); CH = os.path.join(MAN, "chapters"); OUT = os.path.join(MAN, "build")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def chapter_order():
    order = []
    for line in open(os.path.join(MAN, "00_OUTLINE.md"), encoding="utf-8"):
        m = re.match(r"\| ([0-9A-Z]+) \| `chapters/([^`]+)` \| (.+?) \|", line)
        if m:
            order.append((m.group(1), m.group(2), m.group(3)))
    return order


def md_to_html(md: str) -> str:
    """Minimal Markdown → HTML (headings, paragraphs, lists, tables, code, bold/italic/code, links, images)."""
    out, lines, i = [], md.splitlines(), 0
    def inline(t):
        t = html.escape(t, quote=False)
        t = re.sub(r"!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)]+)\)", lambda m: f'<img alt="{m.group(1)}" src="{m.group(2)}">', t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", t)
        return t
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].startswith("```"): buf.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>"); i = j + 1; continue
        if l.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1]):
            hdr = [c.strip() for c in l.strip("|").split("|")]; j = i + 2; rows = []
            while j < len(lines) and lines[j].startswith("|"): rows.append([c.strip() for c in lines[j].strip("|").split("|")]); j += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in hdr) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>"); i = j; continue
        m = re.match(r"^(#{1,6})\s+(.*)", l)
        if m:
            lvl = len(m.group(1)); txt = m.group(2); anchor = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            out.append(f'<h{lvl} id="{anchor}">{inline(txt)}</h{lvl}>'); i += 1; continue
        if re.match(r"^\s*[-*]\s+", l):
            j = i; items = []
            while j < len(lines) and re.match(r"^\s*[-*]\s+", lines[j]): items.append(re.sub(r"^\s*[-*]\s+", "", lines[j])); j += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); i = j; continue
        if re.match(r"^\s*\d+\.\s+", l):
            j = i; items = []
            while j < len(lines) and re.match(r"^\s*\d+\.\s+", lines[j]): items.append(re.sub(r"^\s*\d+\.\s+", "", lines[j])); j += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>"); i = j; continue
        if l.startswith(">"):
            out.append(f"<blockquote>{inline(l.lstrip('> '))}</blockquote>"); i += 1; continue
        if l.strip() == "---":
            out.append("<hr>"); i += 1; continue
        if l.strip():
            j = i; buf = []
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(("#", "|", "```", "-", "*", ">")) and not re.match(r"^\s*\d+\.\s", lines[j]): buf.append(lines[j]); j += 1
            if not buf: buf = [l]; j = i + 1
            out.append("<p>" + inline(" ".join(buf)) + "</p>"); i = j; continue
        i += 1
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true"); ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--max-px", type=int, default=0, help="downscale embedded raster images to this width (needs Pillow); writes *_light outputs")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--per-chapter", action="store_true", help="also write one HTML/PDF per chapter into manual/build/chapters/")
    a = ap.parse_args()
    problems, parts, fig_n = [], [], 0
    order = chapter_order()
    if not order:
        print("ERROR: no chapters in manual/00_OUTLINE.md"); return 2
    for cid, fname, title in order:
        p = os.path.join(CH, fname)
        if not os.path.isfile(p):
            problems.append(f"missing chapter file {fname}"); continue
        md = open(p, encoding="utf-8").read()
        if len(md.strip()) < 200 or "STUB" in md[:400]:
            problems.append(f"chapter {fname} is a stub/empty")
        # figures: ![caption](path) relative to manual/chapters or repo root
        def fix_img(m):
            nonlocal fig_n
            cap, src = m.group(1), m.group(2)
            rel = src if os.path.isabs(src) else (os.path.join(CH, src) if os.path.exists(os.path.join(CH, src)) else os.path.join(ROOT, src))
            if not os.path.isfile(rel):
                problems.append(f"{fname}: missing figure {src}")
                return m.group(0)
            fig_n += 1
            return f"![Figure {fig_n} — {cap}]({os.path.relpath(rel, ROOT)})"
        md = re.sub(r"!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)]+)\)", fix_img, md)   # alt text may contain [STATUS]
        for m in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)#]+)(#[^)]*)?\)", md):
            t = m.group(1)
            if t.startswith(("http://", "https://", "mailto:")): continue
            if not os.path.exists(os.path.join(ROOT, t)) and not os.path.exists(os.path.join(CH, t)):
                problems.append(f"{fname}: broken link {t}")
        parts.append((cid, title, md))
    if a.check:
        print(f"chapters: {len(order)}, figures: {fig_n}, problems: {len(problems)}")
        for pr in problems: print("  -", pr)
        return 1 if problems else 0
    os.makedirs(OUT, exist_ok=True)
    AUTHOR = "Antidrone Ukraine · antidrone.cc"
    master = (f"# AERIS-10 — Complete Engineering & Assembly Manual\n\n**Author: {AUTHOR}**\n\n"
              f"Built {_dt.date.today().isoformat()} by tools/build_manual.py from manual/chapters (order: manual/00_OUTLINE.md). "
              f"Status: BETA documentation — no item is hardware-verified; see the status label on every figure and procedure.\n\n")
    master += "\n\n---\n\n".join(f"<!-- chapter {cid}: {title} -->\n{md}" for cid, title, md in parts)
    open(os.path.join(MAN, "AERIS10_MANUAL.md"), "w", encoding="utf-8").write(master)
    # HTML with embedded images
    def embed(m):
        alt, src = html.unescape(m.group(1)), html.unescape(m.group(2)); p = os.path.join(ROOT, src)
        if not os.path.isfile(p): return m.group(0)
        ext = os.path.splitext(p)[1].lower()
        if ext == ".svg":
            return f'<figure>{open(p, encoding="utf-8", errors="replace").read()}<figcaption>{html.escape(alt)}</figcaption></figure>'
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext[1:], "application/octet-stream")
        if ext == ".pdf":
            return f'<p><a href="{src}">{html.escape(alt)} (PDF)</a></p>'
        raw = open(p, "rb").read()
        if a.max_px and ext in (".png", ".jpg", ".jpeg"):
            try:
                from PIL import Image; import io
                im = Image.open(io.BytesIO(raw))
                if im.width > a.max_px:
                    im = im.convert("RGB").resize((a.max_px, int(im.height * a.max_px / im.width)))
                    buf = io.BytesIO(); im.save(buf, format="JPEG", quality=80, optimize=True); raw = buf.getvalue(); mime = "image/jpeg"
            except ImportError:
                pass
        data = base64.b64encode(raw).decode()
        return f'<figure><img src="data:{mime};base64,{data}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>'
    CSS = ("body{font-family:Arial,Helvetica,sans-serif;max-width:1100px;margin:auto;padding:20px;line-height:1.45;color:#111}"
           "table{border-collapse:collapse;font-size:12px;margin:8px 0}th,td{border:1px solid #999;padding:3px 6px;vertical-align:top}"
           "th{background:#eee}code{background:#f3f3f3;padding:0 3px}pre{background:#f3f3f3;padding:8px;overflow:auto}"
           "figure{margin:12px 0;page-break-inside:avoid}figure img,figure svg{max-width:100%;height:auto}figcaption{font-size:12px;color:#333}"
           "h1{page-break-before:always}h1:first-of-type{page-break-before:avoid}@page{size:A4;margin:18mm 14mm 16mm 14mm}"
           ".run-head{position:fixed;top:0;left:0;right:0;font-size:9px;color:#555;border-bottom:1px solid #ccc;padding:2px 0}"
           ".run-foot{position:fixed;bottom:0;left:0;right:0;font-size:9px;color:#555;border-top:1px solid #ccc;padding:2px 0}"
           ".title-page{text-align:center;page-break-after:always}@media screen{.run-head,.run-foot{position:static;text-align:right}}")
    def render(md_text, hp, pdf_path, with_title=True):
        body = md_to_html(md_text)
        body = re.sub(r'<img alt="([^"]*)" src="([^"]+)">', embed, body)
        today = _dt.date.today().isoformat()
        title_page = (f'<section class="title-page"><h1 style="page-break-before:avoid;font-size:34px;margin-top:120px">AERIS-10</h1>'
                      f'<h2 style="font-weight:normal">Pulsed-LFM X-band phased-array radar</h2><h2>Complete Engineering &amp; Assembly Manual</h2>'
                      f'<p style="margin-top:60px;font-size:18px"><strong>{AUTHOR}</strong></p><p>Edition {today} — BETA (reconstruction, proposed designs and beta implementations; not hardware-verified)</p>'
                      f'<p style="margin-top:80px;font-size:12px;color:#444">Repository: https://github.com/herasymyuks/PLFM_RADAR-aeris · Upstream project files: NawfalMotii79/PLFM_RADAR (ORIGINAL PROJECT FILE where labelled)</p></section>') if with_title else ""
        running = (f'<div class="run-head">AERIS-10 — Engineering &amp; Assembly Manual</div>'
                   f'<div class="run-foot">© {AUTHOR} · {today} · BETA — not hardware-verified</div>')
        body = running + title_page + body
        open(hp, "w", encoding="utf-8").write(f"<!doctype html><html><head><meta charset='utf-8'><title>AERIS-10 Manual — {AUTHOR}</title><meta name='author' content='{AUTHOR}'><meta name='description' content='AERIS-10 radar complete engineering and assembly manual — Antidrone Ukraine, antidrone.cc'><style>{CSS}</style></head><body>{body}</body></html>")
        print("wrote", hp, f"({os.path.getsize(hp)//1024} kB)")
        if pdf_path and os.path.exists(CHROME):
            r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", "file://" + hp], capture_output=True, text=True, timeout=900)
            print("wrote", pdf_path if os.path.isfile(pdf_path) else "PDF FAILED " + r.stderr[-300:])
    body = md_to_html(master)
    body = re.sub(r'<img alt="([^"]*)" src="([^"]+)">', embed, body)
    today = _dt.date.today().isoformat()
    title_page = (f'<section class="title-page"><h1 style="page-break-before:avoid;font-size:34px;margin-top:120px">AERIS-10</h1>'
                  f'<h2 style="font-weight:normal">Pulsed-LFM X-band phased-array radar</h2><h2>Complete Engineering &amp; Assembly Manual</h2>'
                  f'<p style="margin-top:60px;font-size:18px"><strong>{AUTHOR}</strong></p><p>Edition {today} — BETA (reconstruction, proposed designs and beta implementations; not hardware-verified)</p>'
                  f'<p style="margin-top:80px;font-size:12px;color:#444">Repository: https://github.com/herasymyuks/PLFM_RADAR-aeris · Upstream project files: NawfalMotii79/PLFM_RADAR (ORIGINAL PROJECT FILE where labelled)</p></section>')
    running = (f'<div class="run-head">AERIS-10 — Engineering &amp; Assembly Manual</div>'
               f'<div class="run-foot">© {AUTHOR} · {today} · BETA — not hardware-verified</div>')
    body = running + title_page + body
    hp = os.path.join(OUT, f"AERIS10_MANUAL{a.suffix}.html")
    open(hp, "w", encoding="utf-8").write(f"<!doctype html><html><head><meta charset='utf-8'><title>AERIS-10 Manual — {AUTHOR}</title><meta name='author' content='{AUTHOR}'><meta name='description' content='AERIS-10 radar complete engineering and assembly manual — Antidrone Ukraine, antidrone.cc'><style>{CSS}</style></head><body>{body}</body></html>")
    print("wrote", hp, f"({os.path.getsize(hp)//1024} kB, {fig_n} figures)")
    if not a.no_pdf and os.path.exists(CHROME):
        pdf = os.path.join(OUT, f"AERIS10_MANUAL{a.suffix}.pdf")
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + hp], capture_output=True, text=True, timeout=600)
        print("wrote", pdf if os.path.isfile(pdf) else "PDF FAILED " + r.stderr[-300:])
    if a.per_chapter:
        cdir = os.path.join(OUT, "chapters"); os.makedirs(cdir, exist_ok=True)
        for cid, title, md in parts:
            base = os.path.join(cdir, f"AERIS10_ch{cid}_{re.sub(r'[^A-Za-z0-9]+', '_', title)[:40].strip('_')}")
            hdr = f"# AERIS-10 Manual — Chapter {cid}: {title}\n\n**Author: {AUTHOR}** · edition {_dt.date.today().isoformat()} · BETA — this is one chapter of `manual/AERIS10_MANUAL.md`; figure numbers are global.\n\n"
            render(hdr + md, base + ".html", base + ".pdf", with_title=False)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
