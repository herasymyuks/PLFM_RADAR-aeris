#!/usr/bin/env python3
"""Combine one or more SVG drawings into a multi-page PDF using headless Chrome/Chromium.

Each SVG becomes one page whose size equals the SVG's width/height (mm), so the
drawing prints at scale 1:1.  No Python packages needed; requires Google Chrome,
Chromium or Microsoft Edge (auto-detected on macOS/Linux, or pass --chrome PATH).

Usage: python3 tools/svg_sheets_to_pdf.py -o out.pdf sheet1.svg [sheet2.svg ...] [--png-dir DIR --png-width 2400]
Exit codes: 0 ok, 1 Chrome not found or conversion failed, 2 bad arguments.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def find_chrome(explicit: str) -> str:
    if explicit:
        return explicit
    for c in CANDIDATES:
        if os.path.isabs(c):
            if os.path.exists(c):
                return c
        else:
            p = shutil.which(c)
            if p:
                return p
    return ""


def svg_size_mm(path: str):
    head = open(path, "r", encoding="utf-8", errors="replace").read(4000)
    m = re.search(r'<svg[^>]*\swidth="([0-9.]+)(mm|px|pt|in|cm)?"[^>]*\sheight="([0-9.]+)(mm|px|pt|in|cm)?"', head, re.S)
    if not m:
        return 297.0, 210.0
    w, wu, h, hu = float(m.group(1)), m.group(2) or "px", float(m.group(3)), m.group(4) or "px"
    conv = {"mm": 1.0, "cm": 10.0, "in": 25.4, "pt": 25.4 / 72, "px": 25.4 / 96}
    return w * conv[wu], h * conv[hu]


def run_until_written(cmd, out_path: str, timeout: int) -> bool:
    """Run Chrome; succeed once the output file exists, is complete and stable.

    Headless Chrome occasionally does not exit after writing large PDFs/PNGs, so
    the process is terminated once the file has stopped growing for 3 s.
    """
    import time
    if os.path.exists(out_path):
        os.remove(out_path)
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    last_size, stable_since = -1, None
    ok = False
    while time.time() - t0 < timeout:
        rc = proc.poll()
        if os.path.isfile(out_path):
            size = os.path.getsize(out_path)
            if size > 500 and size == last_size:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since > 3:
                    ok = True
                    break
            else:
                stable_since = None
            last_size = size
        if rc is not None:
            ok = os.path.isfile(out_path) and os.path.getsize(out_path) > 500
            break
        time.sleep(0.5)
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            proc.kill()
    if ok and out_path.lower().endswith(".pdf"):
        with open(out_path, "rb") as fh:
            fh.seek(-32, os.SEEK_END)
            ok = b"%%EOF" in fh.read()
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svgs", nargs="+")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--chrome", default="")
    ap.add_argument("--png-dir", default="", help="also rasterise each SVG to PNG in this directory")
    ap.add_argument("--png-width", type=int, default=2400, help="minimum PNG width in px")
    ap.add_argument("--png-px-per-mm", type=float, default=4.0, help="PNG resolution; width = max(png-width, mm*px-per-mm)")
    ap.add_argument("--png-max-width", type=int, default=9000)
    ap.add_argument("--timeout", type=int, default=240)
    a = ap.parse_args()
    chrome = find_chrome(a.chrome)
    if not chrome:
        print("ERROR: Chrome/Chromium not found; install Google Chrome or pass --chrome")
        return 1
    for s in a.svgs:
        if not os.path.isfile(s):
            print("ERROR: missing", s)
            return 2
    pages = []
    css = ["@page { margin: 0; }", "body { margin: 0; }", "img { display: block; }"]
    for i, s in enumerate(a.svgs):
        w, h = svg_size_mm(s)
        css.append(f"@page p{i} {{ size: {w:.2f}mm {h:.2f}mm; margin: 0; }}")
        css.append(f".p{i} {{ page: p{i}; page-break-after: always; width: {w:.2f}mm; height: {h:.2f}mm; }}")
        pages.append(f'<div class="p{i}"><img src="file://{os.path.abspath(s)}" style="width:{w:.2f}mm;height:{h:.2f}mm"></div>')
    html = "<!doctype html><html><head><meta charset='utf-8'><style>" + "\n".join(css) + "</style></head><body>" + "\n".join(pages) + "</body></html>"
    with tempfile.TemporaryDirectory() as td:
        hp = os.path.join(td, "sheets.html")
        open(hp, "w", encoding="utf-8").write(html)
        out = os.path.abspath(a.output)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-sandbox",
               f"--user-data-dir={td}/profile", f"--print-to-pdf={out}", "file://" + hp]
        if not run_until_written(cmd, out, a.timeout):
            print("ERROR: PDF conversion failed or timed out")
            return 1
        print(f"wrote {out} ({len(a.svgs)} page(s), {os.path.getsize(out)} bytes)")
        if a.png_dir:
            os.makedirs(a.png_dir, exist_ok=True)
            for n, s in enumerate(a.svgs):
                w, h = svg_size_mm(s)
                pw = max(a.png_width, int(w * a.png_px_per_mm))
                pw = min(pw, a.png_max_width)
                ph = int(pw * h / w)
                png = os.path.join(a.png_dir, os.path.splitext(os.path.basename(s))[0] + ".png")
                wrapper = os.path.join(td, f"png{n}.html")
                open(wrapper, "w", encoding="utf-8").write(
                    f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;padding:0;background:#fff}}"
                    f"img{{display:block;width:{pw}px;height:{ph}px}}</style></head><body>"
                    f"<img src='file://{os.path.abspath(s)}'></body></html>")
                cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
                       f"--user-data-dir={td}/profile{n}", f"--window-size={pw},{ph}",
                       f"--screenshot={png}", "file://" + wrapper]
                if not run_until_written(cmd, png, a.timeout):
                    print("ERROR: PNG conversion failed for", s)
                    return 1
                print("wrote", png)
    return 0


if __name__ == "__main__":
    sys.exit(main())
