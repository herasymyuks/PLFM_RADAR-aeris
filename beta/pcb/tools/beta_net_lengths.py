#!/usr/bin/env python3
"""beta_net_lengths.py — routed length per net (sum of track/arc lengths, via count, layers) and group skew.

Usage (KiCad python): beta_net_lengths.py BOARD.kicad_pcb --prefix FT_DATA_,FT_BE_,FT_CLK,... [--csv out.csv] [--tol 25]
Lengths are copper lengths of the net's tracks (no via barrel / pad-to-die length); for 2-pin nets this is the
pad-to-pad route length. Exit 0 always (report only).
"""
import sys, csv, collections
import pcbnew


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 1
    b = pcbnew.LoadBoard(a[0])
    pref = tuple(a[a.index('--prefix') + 1].split(',')) if '--prefix' in a else ('FT_',)
    out = a[a.index('--csv') + 1] if '--csv' in a else None
    tol = float(a[a.index('--tol') + 1]) if '--tol' in a else 25.0
    L = collections.defaultdict(float); V = collections.Counter(); LY = collections.defaultdict(set); W = collections.defaultdict(set)
    for t in b.GetTracks():
        n = t.GetNetname()
        if not n.startswith(pref):
            continue
        if t.GetClass() == 'PCB_VIA':
            V[n] += 1
        else:
            L[n] += t.GetLength() / 1e6; LY[n].add(b.GetLayerName(t.GetLayer())); W[n].add(round(t.GetWidth() / 1e6, 3))
    nets = sorted({n.GetNetname() for n in b.GetNetInfo().NetsByName().values() if n.GetNetname().startswith(pref)} if hasattr(b.GetNetInfo(), 'NetsByName') else L.keys())
    rows = [dict(net=n, length_mm=round(L.get(n, 0.0), 2), vias=V.get(n, 0), layers=' '.join(sorted(LY.get(n, ()))), widths_mm=' '.join(str(x) for x in sorted(W.get(n, ())))) for n in nets]
    routed = [r for r in rows if r['length_mm'] > 0]
    if routed:
        mx = max(r['length_mm'] for r in routed); mn = min(r['length_mm'] for r in routed); mean = sum(r['length_mm'] for r in routed) / len(routed)
        for r in rows:
            r['delta_to_mean_mm'] = round(r['length_mm'] - mean, 2) if r['length_mm'] > 0 else ''
            r['within_tol'] = ('yes' if abs(r['length_mm'] - mean) <= tol else 'NO') if r['length_mm'] > 0 else 'unrouted'
        print('nets: %d, with copper: %d, min %.2f mm, max %.2f mm, mean %.2f mm, skew (max-min) %.2f mm, outside ±%.0f mm of mean: %d'
              % (len(rows), len(routed), mn, mx, mean, mx - mn, tol, sum(1 for r in rows if r.get('within_tol') == 'NO')))
    for r in rows:
        print(r)
    if out:
        w = csv.DictWriter(open(out, 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return 0


if __name__ == '__main__':
    sys.exit(main())
