#!/usr/bin/env python3
"""beta_polygon_nets.py — disposition of net-less copper polygons (EAGLE package polygons imported as fp_poly).

For every footprint copper polygon without a net, collect the nets of all pads / tracks / vias / filled zones that
touch it (clearance 0). If exactly one net touches it the polygon is assigned that net (unambiguous); if none or
several touch it, it is left unchanged and listed. Writes a Markdown table.
Usage (KiCad python): beta_polygon_nets.py IN.kicad_pcb OUT.kicad_pcb --md DISPOSITION.md [--to-board] [--dry-run]
"""
import sys
import pcbnew

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    src, dst = a[0], a[1]
    md = a[a.index('--md') + 1] if '--md' in a else None
    dry = '--dry-run' in a
    to_board = '--to-board' in a
    b = pcbnew.LoadBoard(src)
    rows = []; assigned = 0; removed = []
    pads = list(b.GetPads()); tracks = list(b.GetTracks()); zones = [z for z in b.Zones() if z.IsOnCopperLayer() and z.GetNetCode() > 0]
    for fp in b.GetFootprints():
        for s in fp.GraphicalItems():
            if s.GetClass() != 'PCB_SHAPE' or not s.IsOnCopperLayer(): continue
            if s.GetNetCode() > 0:
                if to_board and not dry:  # net was stored on the footprint polygon by an earlier pass: move it as-is
                    ns = pcbnew.PCB_SHAPE(b); ns.SetShape(pcbnew.SHAPE_T_POLY); ns.SetPolyShape(s.GetPolyShape()); ns.SetLayer(s.GetLayer())
                    ns.SetFilled(True); ns.SetWidth(s.GetWidth()); ns.SetNet(s.GetNet()); b.Add(ns); removed.append((fp, s))
                    pos = s.GetPosition()
                    rows.append(dict(fp=fp.GetReference(), layer=b.GetLayerName(s.GetLayer()), x=round(pos.x / 1e6, 3), y=round(pos.y / 1e6, 3), nets={s.GetNetname(): 0}, action='ASSIGNED %s (moved to board-level copper polygon)' % s.GetNetname())); assigned += 1
                continue
            layer = s.GetLayer(); shp = s.GetEffectiveShape(layer); bb = s.GetBoundingBox()
            nets = {}
            def touch(item, ishape, net):
                if net and ishape.Collide(shp, 0): nets[net] = nets.get(net, 0) + 1
            for p in pads:
                if p.IsOnLayer(layer) and p.GetBoundingBox().Intersects(bb): touch(p, p.GetEffectiveShape(layer), p.GetNetname())
            for t in tracks:
                if (t.GetClass() == 'PCB_VIA' or t.IsOnLayer(layer)) and t.GetBoundingBox().Intersects(bb): touch(t, t.GetEffectiveShape(layer), t.GetNetname())
            for z in zones:
                if z.IsOnLayer(layer) and z.GetBoundingBox().Intersects(bb):
                    try:
                        if z.GetFilledPolysList(layer).Collide(shp, 0): nets[z.GetNetname()] = nets.get(z.GetNetname(), 0) + 1
                    except Exception: pass
            pos = s.GetPosition()
            row = dict(fp=fp.GetReference(), layer=b.GetLayerName(layer), x=round(pos.x / 1e6, 3), y=round(pos.y / 1e6, 3), nets=nets)
            if len(nets) == 1:
                net = next(iter(nets))
                row['action'] = 'ASSIGNED ' + net
                if not dry:
                    if to_board:
                        # KiCad DRC treats footprint graphics as net-less whatever net is stored on them; re-create the
                        # identical polygon as a board-level copper shape carrying the net (same geometry, same layer).
                        ns = pcbnew.PCB_SHAPE(b); ns.SetShape(pcbnew.SHAPE_T_POLY); ns.SetPolyShape(s.GetPolyShape()); ns.SetLayer(layer)
                        ns.SetFilled(True); ns.SetWidth(s.GetWidth()); ns.SetNet(b.GetNetInfo().GetNetItem(net)); b.Add(ns)
                        removed.append((fp, s)); row['action'] += ' (moved to board-level copper polygon)'
                    else:
                        s.SetNet(b.GetNetInfo().GetNetItem(net))
                    assigned += 1
            elif not nets:
                row['action'] = 'LEFT (touches nothing — isolated copper graphic)'
            else:
                row['action'] = 'LEFT (ambiguous: touches %s)' % ', '.join(sorted(nets))
            rows.append(row)
    for fp, s in removed: fp.Remove(s)
    for r in rows: print(r)
    print('polygons:', len(rows), 'assigned:', assigned)
    if md:
        with open(md, 'w') as f:
            f.write('| Footprint | Layer | Polygon position (mm) | Touching nets (items) | Disposition |\n|---|---|---|---|---|\n')
            for r in rows:
                f.write('| %s | %s | (%.3f, %.3f) | %s | %s |\n' % (r['fp'], r['layer'], r['x'], r['y'], ', '.join('%s (%d)' % kv for kv in sorted(r['nets'].items())) or '—', r['action']))
    if not dry: pcbnew.SaveBoard(dst, b); print('saved', dst)
    return 0

if __name__ == '__main__':
    sys.exit(main())
