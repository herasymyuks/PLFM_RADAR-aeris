#!/usr/bin/env python3
"""beta_specctra.py — Specctra DSN export / SES merge for the AERIS-10 BETA boards (KiCad 10 pcbnew API).

  export  BOARD.kicad_pcb OUT.dsn            lock every existing track/via/arc *in memory* (-> "(type fix)" in the
                                             DSN so Freerouting never rips them up) and export the DSN. Board file is NOT written.
  merge   BOARD.kicad_pcb IN.ses [--nets N1,N2|--all] [--save OUT.kicad_pcb] [--log merge.json]
                                             parse the Freerouting session and ADD only the new wires/vias of the
                                             selected nets (duplicates of existing segments are skipped). Existing
                                             tracks are never deleted or modified (unlike pcbnew.ImportSpecctraSES,
                                             which rebuilds all routing and loses arcs).
Run with KiCad's Python (…/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3).
Exit codes: 0 ok, 1 usage, 2 load/parse failure.
"""
import sys, re, json
import pcbnew

# ---------- s-expression tokenizer/parser (SES files are small enough to parse fully) ----------
def parse_sexpr(text):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack = [[]]
    for m in tok.finditer(text):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            l = stack.pop(); stack[-1].append(l)
        else:
            if t.startswith('"'): t = t[1:-1]
            stack[-1].append(t)
    return stack[0]

def find_all(node, name):
    out = []
    if isinstance(node, list):
        if node and node[0] == name: out.append(node)
        for c in node:
            if isinstance(c, list): out.extend(find_all(c, name))
    return out

def do_export(pcb, dsn):
    b = pcbnew.LoadBoard(pcb)
    n = 0
    for t in b.GetTracks():
        t.SetLocked(True); n += 1
    ok = pcbnew.ExportSpecctraDSN(b, dsn)
    print('locked-in-memory items:', n, '| DSN export:', 'OK' if ok else 'FAILED', dsn)
    return 0 if ok else 2

def do_merge(pcb, ses, nets, allnets, save, log):
    b = pcbnew.LoadBoard(pcb)
    txt = open(ses, encoding='utf-8', errors='replace').read()
    tree = parse_sexpr(txt)
    res = find_all(tree, 'resolution')
    unit_nm = 1000.0  # um default
    if res:
        r = res[-1]  # (resolution um 10) -> coordinates are in 1/10 um
        unit_nm = {'um': 1000.0, 'mm': 1e6, 'mil': 25400.0, 'inch': 25.4e6}[r[1]] / float(r[2] if len(r) > 2 else 1)
    print('SES resolution:', res[-1] if res else 'default', '-> %.3f nm per unit' % unit_nm)
    # padstacks (via sizes) from library_out: name like Via[0-3]_350:150_um
    padstacks = {}
    for ps in find_all(tree, 'padstack'):
        name = ps[1]; m = re.search(r'_(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)_um', name)
        if m: padstacks[name] = (float(m.group(1)) * 1000, float(m.group(2)) * 1000)
    layers = {b.GetLayerName(l): l for l in b.GetEnabledLayers().CuStack()}
    # existing geometry index
    def key(a, bpt, layer): return (layer, (a.x // 1000, a.y // 1000), (bpt.x // 1000, bpt.y // 1000))
    existing = set(); vias = set()
    for t in b.GetTracks():
        c = t.GetClass()
        if c == 'PCB_TRACK':
            existing.add(key(t.GetStart(), t.GetEnd(), t.GetLayer())); existing.add(key(t.GetEnd(), t.GetStart(), t.GetLayer()))
        elif c == 'PCB_VIA':
            p = t.GetPosition(); vias.add((p.x // 1000, p.y // 1000))
    netinfo = b.GetNetInfo()
    added = {'tracks': 0, 'vias': 0, 'skipped_dup': 0, 'skipped_net': 0, 'unknown_net': [], 'per_net': {}}
    def P(x, y): return pcbnew.VECTOR2I(int(round(float(x) * unit_nm)), int(round(-float(y) * unit_nm)))
    for netnode in find_all(find_all(tree, 'network_out')[0] if find_all(tree, 'network_out') else [], 'net'):
        name = netnode[1]
        if not allnets and name not in nets:
            added['skipped_net'] += 1; continue
        ni = netinfo.GetNetItem(name)
        if ni is None or ni.GetNetCode() <= 0:
            added['unknown_net'].append(name); continue
        for item in netnode[2:]:
            if not isinstance(item, list): continue
            if item[0] == 'wire':
                path = [c for c in item if isinstance(c, list) and c[0] == 'path']
                for p in path:
                    layer = p[1]; width = int(round(float(p[2]) * unit_nm)); coords = p[3:]
                    coords = [c for c in coords if not isinstance(c, list)]
                    pts = [P(coords[i], coords[i + 1]) for i in range(0, len(coords) - 1, 2)]
                    if layer not in layers: continue
                    for a, c in zip(pts, pts[1:]):
                        if a == c: continue
                        k = key(a, c, layers[layer])
                        if k in existing: added['skipped_dup'] += 1; continue
                        tr = pcbnew.PCB_TRACK(b); tr.SetStart(a); tr.SetEnd(c); tr.SetWidth(width); tr.SetLayer(layers[layer]); tr.SetNet(ni)
                        b.Add(tr); existing.add(k); added['tracks'] += 1
                        added['per_net'][name] = added['per_net'].get(name, 0) + 1
            elif item[0] == 'via':
                ps = item[1]; pt = P(item[2], item[3])
                if (pt.x // 1000, pt.y // 1000) in vias: added['skipped_dup'] += 1; continue
                dia, drill = padstacks.get(ps, (None, None))
                v = pcbnew.PCB_VIA(b); v.SetPosition(pt); v.SetNet(ni); v.SetViaType(pcbnew.VIATYPE_THROUGH)
                if dia: v.SetWidth(int(dia)); v.SetDrill(int(drill))
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                b.Add(v); vias.add((pt.x // 1000, pt.y // 1000)); added['vias'] += 1
    print(json.dumps({k: v for k, v in added.items() if k != 'per_net'}, indent=1))
    if log: json.dump(added, open(log, 'w'), indent=1)
    if save:
        pcbnew.SaveBoard(save, b); print('saved', save)
    return 0

def main():
    a = sys.argv[1:]
    if len(a) < 3: print(__doc__); return 1
    if a[0] == 'export': return do_export(a[1], a[2])
    if a[0] == 'merge':
        nets = set(); allnets = '--all' in a; save = None; log = None
        if '--nets' in a: nets = set(a[a.index('--nets') + 1].split(','))
        if '--save' in a: save = a[a.index('--save') + 1]
        if '--log' in a: log = a[a.index('--log') + 1]
        return do_merge(a[1], a[2], nets, allnets, save, log)
    print(__doc__); return 1

if __name__ == '__main__':
    sys.exit(main())
