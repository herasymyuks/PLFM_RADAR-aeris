#!/usr/bin/env python3
"""beta_gnd_stitch.py — stitching vias for a 2-layer board: join bottom-layer fill islands of NET to the top-layer fills of
the same net where they overlap, and give unconnected SMD pads of NET a via into the bottom fill.
Reads the DRC JSON for the list of unconnected pads. Every added item is logged with its uuid (revert with
beta_bridge_unconnected.py --revert LOG --drc JSON). Nets/pads/footprints untouched.
Usage (KiCad python): beta_gnd_stitch.py IN.kicad_pcb OUT.kicad_pcb --net GND --drc DRC.json --log stitch.json [--max-per-island 3]
"""
import sys, json, math
import pcbnew

def main():
    a = sys.argv[1:]
    if len(a) < 2 or '--net' not in a: print(__doc__); return 1
    net = a[a.index('--net') + 1]; drc = a[a.index('--drc') + 1] if '--drc' in a else None
    log = a[a.index('--log') + 1] if '--log' in a else None
    mpi = int(a[a.index('--max-per-island') + 1]) if '--max-per-island' in a else 3
    b = pcbnew.LoadBoard(a[0]); ni = b.GetNetInfo().GetNetItem(net)
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    topu = pcbnew.SHAPE_POLY_SET(); botu = pcbnew.SHAPE_POLY_SET()
    for z in b.Zones():
        if z.GetNetCode() != ni.GetNetCode(): continue
        if z.IsOnLayer(F): topu.Append(z.GetFilledPolysList(F))
        if z.IsOnLayer(B): botu.Append(z.GetFilledPolysList(B))
    topu.Simplify(); botu.Simplify()
    added = []
    def via(pt, why):
        v = pcbnew.PCB_VIA(b); v.SetPosition(pt); v.SetNet(ni); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(int(0.6e6)); v.SetDrill(int(0.3e6)); v.SetLayerPair(F, B); b.Add(v)
        added.append(dict(uuid=v.m_Uuid.AsString(), kind='via', net=net, at=[pt.x / 1e6, pt.y / 1e6], why=why, status='ADDED'))
    # 1. island-to-top-fill stitching
    for i in range(botu.OutlineCount()):
        isl = botu.UnitSet(i)  # outline i WITH its holes (other-net clearance cut-outs)
        inter = pcbnew.SHAPE_POLY_SET(isl); inter.BooleanIntersection(topu)
        inter.Deflate(int(0.5e6), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, int(0.01e6))
        n = 0
        for k in range(inter.OutlineCount()):
            if n >= mpi: break
            o = inter.Outline(k)
            if o.Area() < 0.5e12: continue
            via(o.CPoint(0), 'B.Cu island %d <-> F.Cu fill' % i); n += 1
    # 2. unconnected SMD pads of the net -> via into the bottom fill next to the pad
    if drc:
        rep = json.load(open(drc)); done = set()
        for u in rep['unconnected_items']:
            for it in u['items']:
                d = it['description']
                if not d.startswith('Pad') or '[%s]' % net not in d: continue
                key = (round(it['pos']['x'], 3), round(it['pos']['y'], 3))
                if key in done: continue
                pads = [p for p in b.GetPads() if abs(p.GetPosition().x / 1e6 - key[0]) < 0.01 and abs(p.GetPosition().y / 1e6 - key[1]) < 0.01]
                if not pads: continue
                p = pads[0]; fp = p.GetParentFootprint(); c = fp.GetPosition(); pp = p.GetPosition()
                dx, dy = pp.x - c.x, pp.y - c.y; L = math.hypot(dx, dy) or 1.0
                ok = False
                for dist in (1.0, 1.4, 1.8):
                    pt = pcbnew.VECTOR2I(int(pp.x + dx / L * dist * 1e6), int(pp.y + dy / L * dist * 1e6))
                    probe = pcbnew.SHAPE_POLY_SET(botu); probe.Deflate(int(0.5e6), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, int(0.01e6))
                    if probe.Contains(pt):
                        t = pcbnew.PCB_TRACK(b); t.SetStart(pp); t.SetEnd(pt); t.SetWidth(int(min(p.GetSize().x, p.GetSize().y, int(0.5e6)))); t.SetLayer(F); t.SetNet(ni); b.Add(t)
                        added.append(dict(uuid=t.m_Uuid.AsString(), kind='track', net=net, frm=[pp.x / 1e6, pp.y / 1e6], to=[pt.x / 1e6, pt.y / 1e6], why='pad %s.%s -> via' % (fp.GetReference(), p.GetNumber()), status='ADDED'))
                        via(pt, 'pad %s.%s into B.Cu fill' % (fp.GetReference(), p.GetNumber())); ok = True; break
                done.add(key)
    print('stitch items added:', len(added))
    if log: json.dump(added, open(log, 'w'), indent=1)
    pcbnew.SaveBoard(a[1], b); print('saved', a[1]); return 0

if __name__ == '__main__':
    sys.exit(main())
