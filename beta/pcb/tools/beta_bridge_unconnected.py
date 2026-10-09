#!/usr/bin/env python3
"""beta_bridge_unconnected.py — close remaining same-net gaps that an autorouter cannot handle (zone↔zone, zone↔pad).

Reads the kicad-cli DRC JSON (unconnected_items), identifies both items of each gap on the board and adds:
  * a straight track on the shared copper layer between the two nearest points of the two items (default width
    --width mm; power nets GND/VIN/+... use --power-width), or
  * a via where a top-layer and a bottom-layer fill of the same net overlap (zone-on-F.Cu ↔ zone-on-B.Cu).
Every added item is recorded in --log; the caller re-runs DRC and `--revert LOG` removes the added items that
appear in clearance/shorting violations (so only DRC-clean bridges survive). Nets, pads, footprints: untouched.
Usage (KiCad python):
  beta_bridge_unconnected.py IN.kicad_pcb OUT.kicad_pcb --drc DRC_report.json [--width 0.5] [--power-width 1.0] --log bridges.json
  beta_bridge_unconnected.py IN.kicad_pcb OUT.kicad_pcb --revert bridges.json --drc DRC_report.json
"""
import sys, json, math, re
import pcbnew

def P(x, y): return pcbnew.VECTOR2I(int(round(x * 1e6)), int(round(y * 1e6)))

def poly_points(pset):
    pts = []
    for i in range(pset.OutlineCount()):
        o = pset.Outline(i)
        for k in range(o.PointCount()): pts.append(o.CPoint(k))
    return pts

def nearest(ptsA, ptsB):
    best = None
    # coarse: subsample for very large sets
    sa = ptsA[:: max(1, len(ptsA) // 1500)]; sb = ptsB[:: max(1, len(ptsB) // 1500)]
    for a in sa:
        for c in sb:
            d = (a.x - c.x) ** 2 + (a.y - c.y) ** 2
            if best is None or d < best[0]: best = (d, a, c)
    return best

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    src, dst = a[0], a[1]
    drc = a[a.index('--drc') + 1] if '--drc' in a else None
    width = float(a[a.index('--width') + 1]) if '--width' in a else 0.5
    pwidth = float(a[a.index('--power-width') + 1]) if '--power-width' in a else 1.0
    log = a[a.index('--log') + 1] if '--log' in a else None
    b = pcbnew.LoadBoard(src)
    if '--revert' in a:
        rec = json.load(open(a[a.index('--revert') + 1])); rep = json.load(open(drc))
        bad = set()
        for v in rep['violations']:
            if v['type'] in ('clearance', 'shorting_items', 'hole_clearance', 'copper_edge_clearance', 'track_dangling', 'via_dangling', 'tracks_crossing'):
                for i in v['items']: bad.add(i.get('uuid', ''))
        removed = 0; keep = []
        uuids = {}
        for t in b.GetTracks(): uuids[t.m_Uuid.AsString()] = t
        for r in rec:
            t = uuids.get(r.get('uuid', ''))
            if t is not None and r.get('uuid') in bad:
                b.Remove(t); removed += 1; r['status'] = 'REVERTED (DRC violation)'
            keep.append(r)
        json.dump(keep, open(a[a.index('--revert') + 1], 'w'), indent=1)
        print('reverted', removed, 'of', len(rec)); pcbnew.SaveBoard(dst, b); return 0
    rep = json.load(open(drc))
    netinfo = b.GetNetInfo()
    zones = [z for z in b.Zones() if z.IsOnCopperLayer()]
    pads = list(b.GetPads()); tracks = list(b.GetTracks())
    def find(desc, pos):
        p = P(pos['x'], pos['y'])
        m = re.match(r'(Zone|Pad \S+|PTH pad \S+|Track|Via|Track \(arc\))', desc)
        kind = m.group(1) if m else desc
        if kind == 'Zone':
            cands = [z for z in zones if (z.GetPosition() - p).EuclideanNorm() < 1000]
            return ('zone', cands[0]) if cands else None
        if kind.startswith('Pad') or kind.startswith('PTH'):
            cands = [q for q in pads if (q.GetPosition() - p).EuclideanNorm() < 1000]
            return ('pad', cands[0]) if cands else None
        if kind == 'Via':
            cands = [t for t in tracks if t.GetClass() == 'PCB_VIA' and (t.GetPosition() - p).EuclideanNorm() < 1000]
            return ('via', cands[0]) if cands else None
        cands = [t for t in tracks if t.GetClass() in ('PCB_TRACK', 'PCB_ARC') and ((t.GetStart() - p).EuclideanNorm() < 1000 or (t.GetEnd() - p).EuclideanNorm() < 1000 or (t.GetPosition() - p).EuclideanNorm() < 1000)]
        return ('track', cands[0]) if cands else None
    def geom(kind, it, layer):
        if kind == 'zone': return it.GetFilledPolysList(layer) if it.IsOnLayer(layer) else None
        if not it.IsOnLayer(layer) and kind != 'via': return None
        ps = pcbnew.SHAPE_POLY_SET(); it.TransformShapeToPolygon(ps, layer, 0, pcbnew.ARC_HIGH_DEF if hasattr(pcbnew, 'ARC_HIGH_DEF') else 5000, pcbnew.ERROR_INSIDE)
        return ps
    cu = [pcbnew.F_Cu, pcbnew.B_Cu] if b.GetCopperLayerCount() == 2 else list(b.GetEnabledLayers().CuStack())
    added = []; failed = []
    for u in rep['unconnected_items']:
        it = u['items']
        if len(it) < 2: continue
        A = find(it[0]['description'], it[0]['pos']); B = find(it[1]['description'], it[1]['pos'])
        net = it[0]['description'].split('[')[1].split(']')[0] if '[' in it[0]['description'] else None
        if not A or not B or not net:
            failed.append(dict(items=[i['description'] for i in it], reason='item not found on board')); continue
        ni = netinfo.GetNetItem(net); w = pwidth if (net in ('GND', 'VIN') or net.startswith('+') or net.startswith('-')) else width
        done = False
        for layer in cu:
            ga, gb = geom(A[0], A[1], layer), geom(B[0], B[1], layer)
            if ga is None or gb is None or ga.OutlineCount() == 0 or gb.OutlineCount() == 0: continue
            best = nearest(poly_points(ga), poly_points(gb))
            if best is None: continue
            d, pa, pb = best
            if math.sqrt(d) / 1e6 > 60: continue  # too far for a blind straight bridge
            tr = pcbnew.PCB_TRACK(b); tr.SetStart(pa); tr.SetEnd(pb); tr.SetWidth(int(w * 1e6)); tr.SetLayer(layer); tr.SetNet(ni); b.Add(tr)
            added.append(dict(uuid=tr.m_Uuid.AsString(), kind='track', net=net, layer=b.GetLayerName(layer), width=w, frm=[pa.x / 1e6, pa.y / 1e6], to=[pb.x / 1e6, pb.y / 1e6], length_mm=round(math.sqrt(d) / 1e6, 3), between=[it[0]['description'], it[1]['description']], status='ADDED'))
            done = True; break
        if not done and len(cu) == 2:
            # top fill vs bottom fill of the same net: via in the overlap
            ga, gb = geom(A[0], A[1], cu[0]), geom(B[0], B[1], cu[1])
            if ga is None or gb is None: ga, gb = geom(B[0], B[1], cu[0]), geom(A[0], A[1], cu[1])
            if ga is not None and gb is not None:
                inter = pcbnew.SHAPE_POLY_SET(ga); inter.BooleanIntersection(gb)
                inter.Deflate(int(0.45e6), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, int(0.01e6))
                if inter.OutlineCount() > 0:
                    pt = inter.Outline(0).CPoint(0)
                    v = pcbnew.PCB_VIA(b); v.SetPosition(pt); v.SetNet(ni); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(int(0.6e6)); v.SetDrill(int(0.3e6)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); b.Add(v)
                    added.append(dict(uuid=v.m_Uuid.AsString(), kind='via', net=net, frm=[pt.x / 1e6, pt.y / 1e6], to=[pt.x / 1e6, pt.y / 1e6], between=[it[0]['description'], it[1]['description']], status='ADDED'))
                    done = True
        if not done: failed.append(dict(net=net, items=[i['description'] for i in it], reason='no shared-layer geometry or overlap for a straight bridge'))
    print('bridges added:', len(added), '| not bridged:', len(failed))
    if log: json.dump(added + failed, open(log, 'w'), indent=1)
    pcbnew.SaveBoard(dst, b); print('saved', dst); return 0

if __name__ == '__main__':
    sys.exit(main())
