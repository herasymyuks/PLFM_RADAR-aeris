#!/usr/bin/env python3
"""beta_silk_nudge.py — move silkscreen reference/value TEXT off pads and off other silkscreen (cosmetic DRC fixes).

Only footprint text fields on F.SilkS/B.SilkS are moved (never copper, never footprint silk outlines). For every
text whose bounding box overlaps a pad (same side, pad + mask expansion + --pad-gap) or another silk text / silk
graphic bbox, a free position is searched on a spiral (step --step mm, radius --radius mm) around the footprint
centre. If none is found the text is left where it is and reported. Hidden texts are ignored.
Usage (KiCad python): beta_silk_nudge.py IN.kicad_pcb OUT.kicad_pcb [--step 0.1] [--radius 2.5] [--pad-gap 0.1] [--dry-run] [--log nudges.json]
"""
import sys, json, math
import pcbnew

def rect(bb, grow=0):
    return (bb.GetX() - grow, bb.GetY() - grow, bb.GetX() + bb.GetWidth() + grow, bb.GetY() + bb.GetHeight() + grow)
def inter(a, b): return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    src, dst = a[0], a[1]
    step = float(a[a.index('--step') + 1]) * 1e6 if '--step' in a else 0.1e6
    radius = float(a[a.index('--radius') + 1]) * 1e6 if '--radius' in a else 2.5e6
    padgap = float(a[a.index('--pad-gap') + 1]) * 1e6 if '--pad-gap' in a else 0.1e6
    log = a[a.index('--log') + 1] if '--log' in a else None
    dry = '--dry-run' in a
    b = pcbnew.LoadBoard(src)
    sides = {pcbnew.F_SilkS: (pcbnew.F_Cu, pcbnew.F_Mask), pcbnew.B_SilkS: (pcbnew.B_Cu, pcbnew.B_Mask)}
    # obstacles per silk layer: pads (copper side) and non-text silk graphics; texts handled dynamically
    obst = {l: [] for l in sides}
    mexp = b.GetDesignSettings().m_SolderMaskExpansion
    for p in b.GetPads():
        for sl, (cu, mk) in sides.items():
            if p.IsOnLayer(cu) or p.IsOnLayer(mk): obst[sl].append(rect(p.GetBoundingBox(), mexp + padgap))
    for d in b.GetDrawings():
        if d.GetLayer() in sides and d.GetClass() != 'PCB_TEXT': obst[d.GetLayer()].append(rect(d.GetBoundingBox()))
    for fp in b.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetLayer() in sides and g.GetClass() != 'PCB_TEXT': obst[g.GetLayer()].append(rect(g.GetBoundingBox()))
    for z in b.Zones():
        for sl in sides:
            if z.IsOnLayer(sl): obst[sl].append(rect(z.GetBoundingBox()))
    texts = []
    for fp in b.GetFootprints():
        for t in [fp.Reference(), fp.Value()] + [x for x in fp.GraphicalItems() if x.GetClass() == 'PCB_TEXT']:
            if t.GetLayer() in sides and t.IsVisible(): texts.append((fp, t))
    tb = {id(t): rect(t.GetBoundingBox()) for fp, t in texts}
    moves = []
    def collides(t, r):
        if any(inter(r, o) for o in obst[t.GetLayer()]): return True
        for fp2, t2 in texts:
            if t2 is not t and t2.GetLayer() == t.GetLayer() and inter(r, tb[id(t2)]): return True
        return False
    for fp, t in texts:
        r0 = tb[id(t)]
        if not collides(t, r0): continue
        if dry: moves.append(dict(fp=fp.GetReference(), text=t.GetText(), layer=b.GetLayerName(t.GetLayer()), status='CONFLICT')); continue
        w, h = r0[2] - r0[0], r0[3] - r0[1]
        c = fp.GetPosition(); p0 = t.GetPosition()
        found = None
        n = int(radius / step)
        for k in range(1, n * 8):
            ang = k * 0.7; rr = step * (k / 8.0)
            if rr > radius: break
            cx, cy = c.x + rr * math.cos(ang), c.y + rr * math.sin(ang)
            r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            if not collides(t, r): found = (int(cx), int(cy), r); break
        if found:
            # move by the bbox-centre delta (text anchor != bbox centre for justified/rotated text)
            dx, dy = found[0] - (r0[0] + r0[2]) / 2, found[1] - (r0[1] + r0[3]) / 2
            t.SetPosition(pcbnew.VECTOR2I(int(p0.x + dx), int(p0.y + dy))); tb[id(t)] = rect(t.GetBoundingBox())
            moves.append(dict(fp=fp.GetReference(), text=t.GetText(), layer=b.GetLayerName(t.GetLayer()), frm=[p0.x / 1e6, p0.y / 1e6], to=[found[0] / 1e6, found[1] / 1e6], status='MOVED'))
        else:
            moves.append(dict(fp=fp.GetReference(), text=t.GetText(), layer=b.GetLayerName(t.GetLayer()), frm=[p0.x / 1e6, p0.y / 1e6], status='NO-FREE-POSITION'))
    nm = sum(1 for m in moves if m['status'] == 'MOVED')
    print('silk texts:', len(texts), 'in conflict:', len(moves), 'moved:', nm, 'left:', len(moves) - nm)
    if log: json.dump(moves, open(log, 'w'), indent=1)
    if not dry: pcbnew.SaveBoard(dst, b); print('saved', dst)
    return 0

if __name__ == '__main__':
    sys.exit(main())
