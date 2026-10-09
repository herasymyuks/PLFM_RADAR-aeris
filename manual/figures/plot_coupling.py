#!/usr/bin/env python3
"""Render manual figure F8.4 — three-row mutual coupling of the proposed patch-array rows (DSN-ANT-01).

Input : engineering/DESIGN/ANTENNA/simulation/coupling_3rows.csv (openEMS result of
        engineering/DESIGN/ANTENNA/openems_three_rows.py, columns f_GHz, S22_dB(centre row), S12_dB, S32_dB)
Output: manual/figures/antenna_coupling_3rows.png (and .svg next to it)

Run with the GUI virtual environment, which provides matplotlib:
    beta/gui/.venv/bin/python manual/figures/plot_coupling.py
No data are generated here: every curve is read from the CSV; the markers at 10.5 GHz are the CSV
values at the sample nearest to f0. Status label and authorship are printed into the plot title block.
Exit codes: 0 ok, 1 input missing, 2 matplotlib missing.
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "engineering", "DESIGN", "ANTENNA", "simulation", "coupling_3rows.csv")
OUT_PNG = os.path.join(ROOT, "manual", "figures", "antenna_coupling_3rows.png")
OUT_SVG = os.path.join(ROOT, "manual", "figures", "antenna_coupling_3rows.svg")
F0_GHZ = 10.5           # carrier, engineering/DESIGN/ANTENNA/ANTENNA_DESIGN_CALC.md §1
TARGET_DB = -20.0       # coupling target, ANTENNA_DESIGN_CALC.md §7 item 2
AUTHOR = "Antidrone Ukraine · antidrone.cc"
STATUS = "PROPOSED DESIGN (simulated)"

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: matplotlib not available — run with beta/gui/.venv/bin/python", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if not os.path.isfile(SRC):
        print(f"ERROR: input not found: {SRC}", file=sys.stderr)
        return 1
    f, s22, s12, s32 = [], [], [], []
    with open(SRC, newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        header = next(rd)
        for row in rd:
            if len(row) < 4:
                continue
            f.append(float(row[0])); s22.append(float(row[1])); s12.append(float(row[2])); s32.append(float(row[3]))
    if not f:
        print("ERROR: no data rows", file=sys.stderr)
        return 1
    i0 = min(range(len(f)), key=lambda i: abs(f[i] - F0_GHZ))

    # categorical slots 1-3 of the manual's chart palette (validated: dataviz validate_palette.js)
    colours = {"S22": "#2a78d6", "S12": "#eb6834", "S32": "#1baf7a"}
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200)
    ax.plot(f, s22, color=colours["S22"], lw=2, label=f"S22 — centre row return loss ({header[1].split('(')[0]})")
    ax.plot(f, s12, color=colours["S12"], lw=2, label="S12 — coupling to row above (+14.3 mm)")
    ax.plot(f, s32, color=colours["S32"], lw=2, ls="--", label="S32 — coupling to row below (−14.3 mm)")
    ax.axhline(TARGET_DB, color="#777777", lw=1, ls=":")
    ax.text(f[0] + 0.03, TARGET_DB + 0.3, "−20 dB coupling target (ANTENNA_DESIGN_CALC.md §7)", fontsize=8, color="#555555")
    ax.axvline(F0_GHZ, color="#999999", lw=1, ls=":")
    for key, series in (("S22", s22), ("S12", s12), ("S32", s32)):
        ax.plot([F0_GHZ], [series[i0]], "o", ms=6, color=colours[key], mec="white", mew=1.5)
        ax.annotate(f"{series[i0]:.1f} dB", (F0_GHZ, series[i0]), textcoords="offset points", xytext=(8, -4),
                    fontsize=8, color="#222222")
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("|S| (dB)")
    ax.set_xlim(f[0], f[-1])
    ax.grid(True, color="#dddddd", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    fig.suptitle("AERIS-10 — DSN-ANT-01 three-row mutual coupling (openEMS, centre row driven, neighbours 50 Ω)",
                 fontsize=11, x=0.01, ha="left")
    ax.set_title(f"Status: {STATUS} · source: engineering/DESIGN/ANTENNA/simulation/coupling_3rows.csv · "
                 f"{AUTHOR}", fontsize=8, loc="left", color="#444444")
    fig.tight_layout()
    fig.savefig(OUT_PNG)
    fig.savefig(OUT_SVG)
    print("wrote", os.path.relpath(OUT_PNG, ROOT), "and .svg;", len(f), "samples;",
          f"at {f[i0]:.4f} GHz: S22 {s22[i0]:.1f} dB, S12 {s12[i0]:.1f} dB, S32 {s32[i0]:.1f} dB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
