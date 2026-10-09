#!/usr/bin/env python3
"""beta_pcb_analyze.py — read-only analysis of a KiCad board with pcbnew.

Reports: outline bbox, footprints outside the outline, unconnected (ratsnest) count,
zones without a net, track widths used on RF/LVDS/CLK/LO nets, netclass summary.
Run with KiCad's Python:
  ~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
      beta/pcb/tools/beta_pcb_analyze.py BOARD.kicad_pcb [--json out.json]
Exit code 0 on success, 2 on load failure. Never writes the board.
"""
import sys, json, re, collections
import pcbnew

def mm(v): return v / 1e6

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    path = sys.argv[1]
    out = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    try:
        b = pcbnew.LoadBoard(path)
    except Exception as e:
        print('LOAD FAILED', e); return 2
    r = {}
    bb = b.GetBoardEdgesBoundingBox()
    r['outline_mm'] = dict(x=mm(bb.GetX()), y=mm(bb.GetY()), w=mm(bb.GetWidth()), h=mm(bb.GetHeight()))
    outline = pcbnew.SHAPE_POLY_SET()
    have_outline = b.GetBoardPolygonOutlines(outline, True)
    r['outline_polygon_ok'] = bool(have_outline)
    outside = []
    for fp in b.GetFootprints():
        p = fp.GetPosition()
        inside = outline.Contains(pcbnew.VECTOR2I(p.x, p.y)) if have_outline else bb.Contains(p)
        if not inside:
            outside.append(dict(ref=fp.GetReference(), x=mm(p.x), y=mm(p.y), layer=b.GetLayerName(fp.GetLayer()),
                                pads=fp.GetPadCount(), fp=str(fp.GetFPID().GetLibItemName())))
    r['footprints_total'] = len(b.GetFootprints())
    r['footprints_outside'] = outside
    conn = b.GetConnectivity()
    try:
        b.BuildConnectivity()
        conn = b.GetConnectivity()
        r['unconnected'] = conn.GetUnconnectedCount(False)
    except Exception as e:
        r['unconnected'] = 'n/a: %s' % e
    # zones without net
    nonet = []
    for z in b.Zones():
        if z.IsOnCopperLayer() and z.GetNetCode() <= 0:
            zb = z.GetBoundingBox()
            nonet.append(dict(layer=b.GetLayerName(z.GetFirstLayer()), x=mm(zb.GetX()), y=mm(zb.GetY()),
                              w=mm(zb.GetWidth()), h=mm(zb.GetHeight()), uuid=str(z.m_Uuid.AsString()), parent=(z.GetParentFootprint().GetReference() if z.GetParentFootprint() else '')))
    r['zones_no_net'] = nonet
    r['zones_total'] = len(list(b.Zones()))
    # track widths per net pattern
    pat = re.compile(r'LVDS|RF|LO|CLK|REF|IF|ANT|TX|RX|OSC', re.I)
    widths = collections.defaultdict(collections.Counter)
    for t in b.GetTracks():
        if t.GetClass() in ('PCB_TRACK', 'PCB_ARC'):
            n = t.GetNetname()
            if pat.search(n):
                widths[n][(round(mm(t.GetWidth()), 4), b.GetLayerName(t.GetLayer()))] += 1
    r['rf_track_widths'] = {n: [dict(width=w, layer=l, segments=c) for (w, l), c in sorted(v.items())] for n, v in sorted(widths.items())}
    # all track widths
    allw = collections.Counter(round(mm(t.GetWidth()), 4) for t in b.GetTracks() if t.GetClass() in ('PCB_TRACK','PCB_ARC'))
    r['track_width_histogram'] = dict(sorted(allw.items()))
    r['copper_layers'] = b.GetCopperLayerCount()
    r['nets'] = b.GetNetCount()
    r['tracks'] = sum(1 for t in b.GetTracks() if t.GetClass() in ('PCB_TRACK','PCB_ARC'))
    r['vias'] = sum(1 for t in b.GetTracks() if t.GetClass() == 'PCB_VIA')
    print(json.dumps({k: v for k, v in r.items() if k not in ('footprints_outside','zones_no_net','rf_track_widths')}, indent=1))
    print('footprints outside outline:', len(outside))
    print('zones without net:', len(nonet))
    print('RF-like nets with tracks:', len(widths))
    if out:
        json.dump(r, open(out, 'w'), indent=1)
        print('written', out)
    return 0

if __name__ == '__main__':
    sys.exit(main())
