#!/usr/bin/env python3
"""beta_add_plane.py — add a board-wide copper pour (zone) of one net on one layer, lowest priority.

Used on the 2-layer Power Supply board to give the many isolated GND island pours a common return plane on B.Cu
(standard practice; the original EAGLE layout has 20 separate GND polygons and no plane). The zone follows the
board outline with the netclass clearance, thermal-relief pad connection, 0.25 mm min width. Zone fill only —
no footprint, track or net is modified.
Usage (KiCad python): beta_add_plane.py IN.kicad_pcb OUT.kicad_pcb --net GND --layer B.Cu [--clearance 0.3] [--priority 0]
"""
import sys
import pcbnew

def main():
    a = sys.argv[1:]
    if len(a) < 2 or '--net' not in a or '--layer' not in a: print(__doc__); return 1
    net = a[a.index('--net') + 1]; layer = a[a.index('--layer') + 1]
    clr = float(a[a.index('--clearance') + 1]) if '--clearance' in a else 0.3
    prio = int(a[a.index('--priority') + 1]) if '--priority' in a else 0
    b = pcbnew.LoadBoard(a[0])
    ni = b.GetNetInfo().GetNetItem(net)
    if ni is None: print('no net', net); return 2
    outline = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline, True)
    z = pcbnew.ZONE(b); z.SetLayer(b.GetLayerID(layer)); z.SetNet(ni)
    z.SetAssignedPriority(prio); z.SetLocalClearance(int(clr * 1e6)); z.SetMinThickness(int(0.25e6))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(int(0.3e6)); z.SetThermalReliefSpokeWidth(int(0.4e6))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetZoneName('BETA_%s_plane_%s' % (net, layer))
    o = outline.Outline(0)
    pts = pcbnew.VECTOR_VECTOR2I()
    for i in range(o.PointCount()): pts.append(o.CPoint(i))
    z.AddPolygon(pts)
    b.Add(z)
    print('added zone', z.GetZoneName(), 'points', o.PointCount())
    pcbnew.SaveBoard(a[1], b); print('saved', a[1]); return 0

if __name__ == '__main__':
    sys.exit(main())
