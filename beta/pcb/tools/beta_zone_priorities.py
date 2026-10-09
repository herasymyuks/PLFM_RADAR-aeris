#!/usr/bin/env python3
"""beta_zone_priorities.py — give overlapping SAME-NET copper zones distinct priorities.

KiCad DRC flags "zones_intersect" when two zones of equal priority overlap, even when both carry the same net
(EAGLE polygons imported with one common rank). Assigning a distinct priority to each zone changes nothing
electrically (same net, same outline, same fill rules); it only removes the ambiguity the DRC complains about.
Zones of different nets are never touched.
Usage (KiCad python): beta_zone_priorities.py IN.kicad_pcb OUT.kicad_pcb [--log zones.json]
"""
import sys, json
import pcbnew

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    log = a[a.index('--log') + 1] if '--log' in a else None
    b = pcbnew.LoadBoard(a[0])
    zones = [z for z in b.Zones() if z.IsOnCopperLayer() and z.GetNetCode() > 0]
    changes = []
    # group by (net, layer); larger zones get lower priority so small local pours fill first (KiCad: higher = filled first)
    groups = {}
    for z in zones:
        for l in z.GetLayerSet().Seq(): groups.setdefault((z.GetNetCode(), int(l)), []).append(z)
    seen = set()
    for (net, layer), zs in groups.items():
        if len(zs) < 2: continue
        zs = sorted(zs, key=lambda z: -(z.GetBoundingBox().GetWidth() * z.GetBoundingBox().GetHeight()))
        for i, z in enumerate(zs):
            if z.m_Uuid.AsString() in seen: continue
            base = z.GetAssignedPriority(); newp = base + (len(zs) - 1 - i)
            if newp != base or i < len(zs) - 1:
                z.SetAssignedPriority(newp); seen.add(z.m_Uuid.AsString())
                bb = z.GetBoundingBox()
                changes.append(dict(net=z.GetNetname(), layer=b.GetLayerName(layer), bbox_mm=[bb.GetX() / 1e6, bb.GetY() / 1e6, bb.GetWidth() / 1e6, bb.GetHeight() / 1e6], priority_from=base, priority_to=newp))
    print('zones re-prioritised:', len(changes))
    if log: json.dump(changes, open(log, 'w'), indent=1)
    pcbnew.SaveBoard(a[1], b); print('saved', a[1])
    return 0

if __name__ == '__main__':
    sys.exit(main())
