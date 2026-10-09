#!/usr/bin/env python3
"""Tune the patch length of the openEMS row model until the resonance sits at f0 (secant on L_SCALE).
Runs engineering/DESIGN/ANTENNA/openems_patch_row.py with the openEMS Python venv; writes
engineering/DESIGN/ANTENNA/simulation/TUNING_LOG.md and the final s11.csv / s11 plot / pattern.
Usage: python3 tools/design_antenna_tune.py [--iters 3] [--python PATH] [--workdir build/openems_antenna]
"""
import argparse, os, re, shutil, subprocess, sys, json, datetime as _dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("--iters", type=int, default=3)
ap.add_argument("--python", default=os.path.expanduser("~/.cache/aeris10_work/openems-venv/bin/python"))
ap.add_argument("--workdir", default=os.path.join(ROOT, "build", "openems_antenna")); a = ap.parse_args()
os.makedirs(a.workdir, exist_ok=True)
env = dict(os.environ, PATH=os.path.expanduser("~/opt/openEMS/bin") + ":" + os.environ["PATH"],
           DYLD_LIBRARY_PATH=os.path.expanduser("~/opt/openEMS/lib"), MPLBACKEND="Agg")
F0 = 10.5
def run(scale):
    shutil.rmtree(os.path.join(a.workdir, "openems_out"), ignore_errors=True)
    e = dict(env, L_SCALE=f"{scale:.5f}")
    r = subprocess.run([a.python, os.path.join(ROOT, "engineering/DESIGN/ANTENNA/openems_patch_row.py")], cwd=a.workdir, env=e, capture_output=True, text=True)
    m = re.search(r"RESULT ([0-9.]+) (-?[0-9.]+) (-?[0-9.]+) ([0-9.]+)", r.stdout)
    d = re.search(r"Dmax ([0-9.]+)", r.stdout)
    if not m:
        print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit(1)
    return float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(d.group(1)) if d else None
log = []
scale, fres, s_res, s_f0, bw, dmax = 1.0, None, None, None, None, None
hist = []
for it in range(a.iters):
    fres, s_res, s_f0, bw, dmax = run(scale)
    hist.append((scale, fres)); log.append((it, scale, fres, s_res, s_f0, bw, dmax))
    print(f"iter {it}: L_SCALE={scale:.4f} f_res={fres:.4f} GHz S11(res)={s_res:.1f} dB S11(f0)={s_f0:.1f} dB BW={bw:.0f} MHz D={dmax}")
    if abs(fres - F0) < 0.03:
        break
    if len(hist) >= 2 and hist[-1][1] != hist[-2][1]:
        (s1, f1), (s2, f2) = hist[-2], hist[-1]
        scale = s2 + (F0 - f2) * (s2 - s1) / (f2 - f1)
    else:
        scale = scale * fres / F0
sim = os.path.join(ROOT, "engineering/DESIGN/ANTENNA/simulation"); os.makedirs(sim, exist_ok=True)
for f in ("s11.csv", "s11_row.png"):
    src = os.path.join(a.workdir, "openems_out", f)
    if os.path.isfile(src): shutil.copyfile(src, os.path.join(sim, f))
final = min(log, key=lambda r: r[4])   # keep the iteration with the best S11 at f0, not the last one
json.dump({"L_SCALE": final[1], "f_res_GHz": final[2], "S11_res_dB": final[3], "S11_f0_dB": final[4], "BW_10dB_MHz": final[5], "Dmax_row_dBi": final[6], "date": _dt.date.today().isoformat()}, open(os.path.join(sim, "tuning_result.json"), "w"), indent=2)
with open(os.path.join(sim, "TUNING_LOG.md"), "w") as fh:
    fh.write(f"# openEMS tuning of one antenna row (DSN-ANT-01)\n\nDate {_dt.date.today().isoformat()} · openEMS built from source (openEMS-Project, `~/opt/openEMS`) · model `../openems_patch_row.py` · runner `tools/design_antenna_tune.py`.\n\n| iter | L_SCALE | f_res (GHz) | S11 at f_res (dB) | S11 at 10.5 GHz (dB) | −10 dB BW (MHz) | D_row (dBi) |\n|---|---|---|---|---|---|---|\n")
    for it, sc, fr, sr, sf, b, d in log: fh.write(f"| {it} | {sc:.4f} | {fr:.3f} | {sr:.1f} | {sf:.1f} | {b:.0f} | {d} |\n")
    fh.write(f"\nSelected (best S11 at f0): patch length factor **{final[1]:.4f}** applied to the transmission-line value → resonance {final[2]:.3f} GHz, S11 {final[4]:.1f} dB at 10.5 GHz, −10 dB bandwidth {final[5]:.0f} MHz, single-row directivity {final[6]} dBi (16 rows → ≈ +12 dB). Model limits: PEC copper, no connector, no mutual coupling between rows, MUR boundaries. Status after tuning: PROPOSED DESIGN, simulated (one row), not measured.\n")
print("done", final)
