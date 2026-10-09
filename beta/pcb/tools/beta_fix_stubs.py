#!/usr/bin/env python3
"""beta_fix_stubs.py — close converter-induced gaps between an arc/track end and the pad it was meant to reach.

For every copper track/arc end that is not connected to anything (dangling) and whose net has a pad on the
same layer within --radius mm (default 1.0), a straight segment (same net, same layer, same width) is added
from the free end to the pad centre. Nothing is deleted or moved. Also accepts explicit fixes with
--extra "NET,LAYER,WIDTH_MM,x1,y1,x2,y2" (KiCad coordinates, mm, repeatable).
Usage (KiCad python): beta_fix_stubs.py IN.kicad_pcb OUT.kicad_pcb [--radius 1.0] [--nets A,B] [--arc-tail 0.3] [--extra ...] [--log fixes.json]
Exit 0 ok, 2 load failure.
"""
import sys, json, math
import pcbnew

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    src, dst = a[0], a[1]
    radius = float(a[a.index('--radius') + 1]) if '--radius' in a else 1.0
    nets = set(a[a.index('--nets') + 1].split(',')) if '--nets' in a else None
    log = a[a.index('--log') + 1] if '--log' in a else None
    extras = [a[i + 1] for i, x in enumerate(a) if x == '--extra']
    b = pcbnew.LoadBoard(src)
    fixes = []
    pads_by_net = {}; items_by_net = {}
    for p in b.GetPads():
        pads_by_net.setdefault(p.GetNetCode(), []).append(p)
    for t in b.GetTracks():
        items_by_net.setdefault(t.GetNetCode(), []).append(t)
    tracks = [t for t in b.GetTracks() if t.GetClass() in ('PCB_TRACK', 'PCB_ARC')]
    def touched_tracks(t, end):
        # another track/arc/via of the same net whose copper contains the end point on t's layer
        for o in items_by_net.get(t.GetNetCode(), []):
            if o.m_Uuid == t.m_Uuid: continue
            if o.GetClass() == 'PCB_VIA' or o.IsOnLayer(t.GetLayer()):
                if o.HitTest(end, 0): return True
        return False
    def touched(t, end):
        if touched_tracks(t, end): return True
        for p in pads_by_net.get(t.GetNetCode(), []):
            if p.IsOnLayer(t.GetLayer()) and p.HitTest(end, 0): return True
        return False
    for t in tracks:
        if nets and t.GetNetname() not in nets: continue
        for end in (t.GetStart(), t.GetEnd()):
            if touched(t, end): continue
            best = None
            for p in pads_by_net.get(t.GetNetCode(), []):
                if not p.IsOnLayer(t.GetLayer()): continue
                d = math.hypot(p.GetPosition().x - end.x, p.GetPosition().y - end.y) / 1e6
                if d <= radius and (best is None or d < best[0]): best = (d, p)
            if best:
                d, p = best
                tr = pcbnew.PCB_TRACK(b); tr.SetStart(end); tr.SetEnd(p.GetPosition()); tr.SetWidth(t.GetWidth()); tr.SetLayer(t.GetLayer()); tr.SetNet(t.GetNet())
                b.Add(tr)
                fixes.append(dict(net=t.GetNetname(), layer=b.GetLayerName(t.GetLayer()), width_mm=t.GetWidth() / 1e6,
                                  frm=[end.x / 1e6, end.y / 1e6], to=[p.GetPosition().x / 1e6, p.GetPosition().y / 1e6],
                                  pad='%s.%s' % (p.GetParentFootprint().GetReference(), p.GetNumber()), gap_mm=round(d, 4), kind='dangling-end-to-pad'))
    # --arc-tail F: an arc whose end lies inside a same-net pad but which DRC still reports as unconnected (KiCad
    # arc/pad connectivity after EAGLE import) gets a straight tail from that end to the point at fraction F along the
    # arc, i.e. a short segment lying inside the arc's own copper that gives the pad a plain track anchor.
    if '--arc-tail' in a:
        frac = float(a[a.index('--arc-tail') + 1])
        for t in tracks:
            if t.GetClass() != 'PCB_ARC' or (nets and t.GetNetname() not in nets): continue
            for end, other in ((t.GetStart(), t.GetEnd()), (t.GetEnd(), t.GetStart())):
                if touched_tracks(t, end): continue
                inpad = [p for p in pads_by_net.get(t.GetNetCode(), []) if p.IsOnLayer(t.GetLayer()) and p.HitTest(end, 0)]
                if not inpad: continue
                c = t.GetCenter(); r = t.GetRadius()
                ae = math.atan2(end.y - c.y, end.x - c.x); ao = math.atan2(other.y - c.y, other.x - c.x); am = math.atan2(t.GetMid().y - c.y, t.GetMid().x - c.x)
                def norm(x):
                    while x <= -math.pi: x += 2 * math.pi
                    while x > math.pi: x -= 2 * math.pi
                    return x
                sweep = norm(ao - ae)
                if abs(norm(am - ae)) > abs(sweep) or (norm(am - ae) * sweep) < 0: sweep = sweep - math.copysign(2 * math.pi, sweep)
                ang = ae + frac * sweep
                q = pcbnew.VECTOR2I(int(round(c.x + r * math.cos(ang))), int(round(c.y + r * math.sin(ang))))
                tr = pcbnew.PCB_TRACK(b); tr.SetStart(end); tr.SetEnd(q); tr.SetWidth(t.GetWidth()); tr.SetLayer(t.GetLayer()); tr.SetNet(t.GetNet()); b.Add(tr)
                fixes.append(dict(net=t.GetNetname(), layer=b.GetLayerName(t.GetLayer()), width_mm=t.GetWidth() / 1e6, frm=[end.x / 1e6, end.y / 1e6], to=[q.x / 1e6, q.y / 1e6],
                                  pad='%s.%s' % (inpad[0].GetParentFootprint().GetReference(), inpad[0].GetNumber()), kind='arc-tail-inside-pad', arc_length_mm=round(t.GetLength() / 1e6, 4)))
    for e in extras:
        net, layer, w, x1, y1, x2, y2 = e.split(',')
        ni = b.GetNetInfo().GetNetItem(net)
        tr = pcbnew.PCB_TRACK(b); tr.SetStart(pcbnew.VECTOR2I(int(float(x1) * 1e6), int(float(y1) * 1e6))); tr.SetEnd(pcbnew.VECTOR2I(int(float(x2) * 1e6), int(float(y2) * 1e6)))
        tr.SetWidth(int(float(w) * 1e6)); tr.SetLayer(b.GetLayerID(layer)); tr.SetNet(ni); b.Add(tr)
        fixes.append(dict(net=net, layer=layer, width_mm=float(w), frm=[float(x1), float(y1)], to=[float(x2), float(y2)], kind='explicit'))
    for f in fixes: print(f)
    print('fixes added:', len(fixes))
    if log: json.dump(fixes, open(log, 'w'), indent=1)
    pcbnew.SaveBoard(dst, b); print('saved', dst)
    return 0

if __name__ == '__main__':
    sys.exit(main())
