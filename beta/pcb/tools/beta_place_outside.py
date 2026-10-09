#!/usr/bin/env python3
"""beta_place_outside.py — move footprints that sit outside the board outline to free space inside it.

Algorithm (deterministic, 1 mm grid):
 1. Outside footprints are clustered by shared nets, ignoring nets with more than --bignet footprints (GND, VIN...).
 2. Each cluster gets an anchor = centroid of the INSIDE footprints it shares nets with (big nets excluded; if no such
    net exists the VIN-type nets are used; if still none the board centre).
 3. Cluster members (except edge connectors) are packed into a rectangular block (largest first, 1 mm gaps); the block
    is placed at the nearest free position to the anchor (spiral search) that is >= --edge mm from the outline and does
    not overlap existing footprints, F.Cu/B.Cu tracks, vias, zone bounding boxes or previously placed blocks.
 4. Connectors (--connector-prefix, default footprints named 22-23-* or AK300*) are placed on the board edge nearest to
    their cluster block, in the nearest free edge slot.
Nothing but footprint positions is changed (no rotation, no net change). A JSON log lists every move.
Usage (KiCad python): beta_place_outside.py IN.kicad_pcb OUT.kicad_pcb [--grid 1] [--edge 3] [--bignet 20] [--skip-nonet] [--log moves.json]
"""
import sys, json, math, collections
import pcbnew

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 1
    src, dst = a[0], a[1]
    grid = float(a[a.index('--grid') + 1]) if '--grid' in a else 1.0
    edge = float(a[a.index('--edge') + 1]) if '--edge' in a else 3.0
    bignet = int(a[a.index('--bignet') + 1]) if '--bignet' in a else 20
    log = a[a.index('--log') + 1] if '--log' in a else None
    b = pcbnew.LoadBoard(src)
    outline = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline, True)
    bb = b.GetBoardEdgesBoundingBox()
    X0, Y0, W, H = bb.GetX() / 1e6, bb.GetY() / 1e6, bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
    def inside_pt(x, y): return outline.Contains(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))
    fps = list(b.GetFootprints())
    def pos(fp): p = fp.GetPosition(); return (p.x / 1e6, p.y / 1e6)
    def size(fp):
        r = fp.GetBoundingBox(False, False); return (r.GetWidth() / 1e6, r.GetHeight() / 1e6)
    outside = [fp for fp in fps if not inside_pt(*pos(fp))]
    if '--skip-nonet' in a:  # leave parts without any net where they are (nothing to connect them to)
        outside = [fp for fp in outside if any(p.GetNetname() for p in fp.Pads())]
    inside = [fp for fp in fps if inside_pt(*pos(fp))]
    outref = {fp.GetReference() for fp in outside}
    # occupancy grid
    nx, ny = int(W / grid) + 2, int(H / grid) + 2
    occ = bytearray(nx * ny)
    def cell(x, y): return (int((x - X0) / grid), int((y - Y0) / grid))
    def block(x1, y1, x2, y2, margin):
        cx1, cy1 = cell(x1 - margin, y1 - margin); cx2, cy2 = cell(x2 + margin, y2 + margin)
        for cy in range(max(0, cy1), min(ny - 1, cy2) + 1):
            for cx in range(max(0, cx1), min(nx - 1, cx2) + 1): occ[cy * nx + cx] = 1
    def free(x1, y1, x2, y2):
        cx1, cy1 = cell(x1, y1); cx2, cy2 = cell(x2, y2)
        if cx1 < 0 or cy1 < 0 or cx2 >= nx or cy2 >= ny: return False
        for cy in range(cy1, cy2 + 1):
            base = cy * nx
            for cx in range(cx1, cx2 + 1):
                if occ[base + cx]: return False
        return True
    # outline + edge margin: mark cells whose centre is not inside the (shrunk) outline
    for cy in range(ny):
        for cx in range(nx):
            x, y = X0 + (cx + 0.5) * grid, Y0 + (cy + 0.5) * grid
            if not (inside_pt(x, y) and inside_pt(x - edge, y) and inside_pt(x + edge, y) and inside_pt(x, y - edge) and inside_pt(x, y + edge)):
                occ[cy * nx + cx] = 1
    for fp in inside:
        r = fp.GetBoundingBox(False, False); block(r.GetX() / 1e6, r.GetY() / 1e6, (r.GetX() + r.GetWidth()) / 1e6, (r.GetY() + r.GetHeight()) / 1e6, 1.0)
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            r = t.GetBoundingBox(); block(r.GetX() / 1e6, r.GetY() / 1e6, (r.GetX() + r.GetWidth()) / 1e6, (r.GetY() + r.GetHeight()) / 1e6, 0.5)
        else:  # rasterise the segment itself (its bounding box would block huge areas for diagonal tracks)
            s0, e0 = t.GetStart(), t.GetEnd(); L = max(1, int(math.hypot(e0.x - s0.x, e0.y - s0.y) / 1e6 / (grid / 2)))
            hw = t.GetWidth() / 2e6 + 0.5
            for i in range(L + 1):
                x = (s0.x + (e0.x - s0.x) * i / L) / 1e6; y = (s0.y + (e0.y - s0.y) * i / L) / 1e6
                block(x - hw, y - hw, x + hw, y + hw, 0)
    for z in b.Zones():
        if z.IsOnCopperLayer():
            r = z.GetBoundingBox()
            if r.GetWidth() * r.GetHeight() / 1e12 > 0.25 * W * H: continue  # board-wide pour: parts may sit on it
            block(r.GetX() / 1e6, r.GetY() / 1e6, (r.GetX() + r.GetWidth()) / 1e6, (r.GetY() + r.GetHeight()) / 1e6, 0.5)
    print('occupancy: %.1f%% of grid blocked' % (100.0 * sum(occ) / len(occ)))
    # nets
    net_fps = collections.defaultdict(set)
    for p in b.GetPads():
        if p.GetNetname(): net_fps[p.GetNetname()].add(p.GetParentFootprint().GetReference())
    small = {n: r for n, r in net_fps.items() if len(r) <= bignet}
    big = {n: r for n, r in net_fps.items() if len(r) > bignet and n != 'GND'}
    # union-find clusters of outside parts
    parent = {r: r for r in outref}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for n, refs in small.items():
        rs = [r for r in refs if r in outref]
        for r in rs[1:]: parent[find(r)] = find(rs[0])
    clusters = collections.defaultdict(list)
    for fp in outside: clusters[find(fp.GetReference())].append(fp)
    byref = {fp.GetReference(): fp for fp in fps}
    def is_conn(fp):
        n = str(fp.GetFPID().GetLibItemName()); return n.startswith('22-23-') or n.startswith('AK300') or n.startswith('MA10')
    moves = []; placed_blocks = []
    cx0, cy0 = X0 + W / 2, Y0 + H / 2
    def anchor_of(members):
        refs = {fp.GetReference() for fp in members}
        pts = []
        for n, rs in small.items():
            if rs & refs: pts += [pos(byref[r]) for r in rs - outref]
        kind = 'small-net'
        if not pts:
            for n, rs in big.items():
                if rs & refs: pts += [pos(byref[r]) for r in rs - outref]
            kind = 'big-net'
        if not pts: return (cx0, cy0), 'board-centre'
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)), kind
    def spiral(fx, fy, w, h, margin=1.0):
        # find nearest free top-left for a w x h block around (fx,fy)
        best = None
        for ring in range(0, int(max(W, H) / grid)):
            cands = []
            for dx in range(-ring, ring + 1):
                for dy in (-ring, ring): cands.append((dx, dy))
            for dy in range(-ring + 1, ring):
                for dx in (-ring, ring): cands.append((dx, dy))
            for dx, dy in cands:
                x1 = round((fx - w / 2) / grid) * grid + dx * grid; y1 = round((fy - h / 2) / grid) * grid + dy * grid
                if free(x1 - margin, y1 - margin, x1 + w + margin, y1 + h + margin):
                    return (x1, y1)
        return None
    order = sorted(clusters.items(), key=lambda kv: -sum(size(f)[0] * size(f)[1] for f in kv[1]))
    for cid, members in order:
        (ax, ay), akind = anchor_of(members)
        parts = sorted([f for f in members if not is_conn(f)], key=lambda f: -(size(f)[0] * size(f)[1]))
        conns = [f for f in members if is_conn(f)]
        if parts:
            area = sum((size(f)[0] + 1) * (size(f)[1] + 1) for f in parts)
            bw = max(math.sqrt(area * 1.3), max(size(f)[0] for f in parts) + 1)
            # row packing
            rows = []; cur = []; curw = 0
            for f in parts:
                w, h = size(f)
                if cur and curw + w + 1 > bw: rows.append(cur); cur = []; curw = 0
                cur.append(f); curw += w + 1
            if cur: rows.append(cur)
            rel = {}; y = 0; blockw = 0
            for row in rows:
                x = 0; rh = max(size(f)[1] for f in row)
                for f in row:
                    w, h = size(f); rel[f.GetReference()] = (x + w / 2, y + rh / 2); x += w + 1
                blockw = max(blockw, x - 1); y += rh + 1
            blockh = y - 1
            tl = spiral(ax, ay, blockw, blockh)
            if tl is None:
                for f in members: moves.append(dict(ref=f.GetReference(), cluster=cid, status='NO-FREE-SPACE'))
                continue
            for f in parts:
                rx, ry = rel[f.GetReference()]
                nxp, nyp = round((tl[0] + rx) / grid) * grid, round((tl[1] + ry) / grid) * grid
                old = pos(f); f.SetPosition(pcbnew.VECTOR2I(int(nxp * 1e6), int(nyp * 1e6)))
                moves.append(dict(ref=f.GetReference(), fp=str(f.GetFPID().GetLibItemName()), cluster=cid, anchor=[round(ax, 1), round(ay, 1)], anchor_kind=akind, frm=[round(old[0], 2), round(old[1], 2)], to=[nxp, nyp], status='PLACED'))
            block(tl[0], tl[1], tl[0] + blockw, tl[1] + blockh, 1.0)
            placed_blocks.append((tl[0] + blockw / 2, tl[1] + blockh / 2))
            bx, by = tl[0] + blockw / 2, tl[1] + blockh / 2
        else:
            bx, by = ax, ay
        for f in conns:
            w, h = size(f)
            # candidate edge points: nearest edge to (bx,by)
            m = edge + 1.5  # first fully free grid row/column beyond the edge-margin cells
            edges = [(X0 + m + w / 2, by, 'left'), (X0 + W - m - w / 2, by, 'right'), (bx, Y0 + m + h / 2, 'top'), (bx, Y0 + H - m - h / 2, 'bottom')]
            edges.sort(key=lambda e: math.hypot(e[0] - bx, e[1] - by))
            done = False
            for ex, ey, ename in edges:
                for step in range(0, int(max(W, H) / grid)):
                    for sgn in (1, -1):
                        if ename in ('left', 'right'): cx, cy = ex, ey + sgn * step * grid
                        else: cx, cy = ex + sgn * step * grid, ey
                        x1, y1 = round((cx - w / 2) / grid) * grid, round((cy - h / 2) / grid) * grid
                        if free(x1, y1, x1 + w, y1 + h):
                            old = pos(f); f.SetPosition(pcbnew.VECTOR2I(int((x1 + w / 2) * 1e6), int((y1 + h / 2) * 1e6)))
                            block(x1, y1, x1 + w, y1 + h, 1.0)
                            moves.append(dict(ref=f.GetReference(), fp=str(f.GetFPID().GetLibItemName()), cluster=cid, edge=ename, frm=[round(old[0], 2), round(old[1], 2)], to=[x1 + w / 2, y1 + h / 2], status='PLACED-EDGE'))
                            done = True; break
                    if done: break
                if done: break
            if not done: moves.append(dict(ref=f.GetReference(), cluster=cid, status='NO-FREE-EDGE'))
    n_ok = sum(1 for m in moves if m['status'].startswith('PLACED'))
    print('outside before:', len(outside), '| placed:', n_ok, '| failed:', len(moves) - n_ok, '| clusters:', len(clusters))
    if log: json.dump(moves, open(log, 'w'), indent=1)
    pcbnew.SaveBoard(dst, b); print('saved', dst)
    return 0

if __name__ == '__main__':
    sys.exit(main())
