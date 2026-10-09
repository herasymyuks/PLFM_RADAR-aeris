#!/usr/bin/env python3
"""beta_dsn_restrict.py — restrict a Specctra DSN to selected nets for Freerouting.

Nets not selected keep their definition (so their existing fixed wires stay obstacles of that net) but lose their
pin list, i.e. Freerouting has nothing to route for them; their pads remain as obstacles. For --partial NET=REFS
only the pins of the listed reference designators are kept (e.g. GND pins of the newly added parts only).
Usage: python3 beta_dsn_restrict.py IN.dsn OUT.dsn --keep-prefix FT_,USB_ --keep +3V3_FT --partial GND=U6,J_USB3,...
Exit 0 ok, 1 usage.
"""
import sys, re


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__); return 1
    src, dst = a[0], a[1]
    pref = tuple(a[a.index('--keep-prefix') + 1].split(',')) if '--keep-prefix' in a else ()
    keep = set(a[a.index('--keep') + 1].split(',')) if '--keep' in a else set()
    partial = {}
    for i, x in enumerate(a):
        if x == '--partial':
            n, refs = a[i + 1].split('=', 1)
            partial[n] = set(refs.split(','))
    txt = open(src, encoding='utf-8').read()
    start = txt.index('(network')
    pat = re.compile(r'\(net ("[^"]*"|\S+)\s*\(pins([^)]*)\)', re.S)
    stats = {'kept': 0, 'cleared': 0}

    def rep(m):
        name = m.group(1).strip('"')
        pins = m.group(2).split()
        if name in keep or (pref and name.startswith(pref)):
            stats['kept'] += 1
            return m.group(0)
        if name in partial:
            sel = [p for p in pins if p.rsplit('-', 1)[0] in partial[name]]
            stats['kept'] += 1
            return '(net %s (pins %s)' % (m.group(1), ' '.join(sel))
        stats['cleared'] += 1
        return '(net %s (pins)' % m.group(1)

    out = txt[:start] + pat.sub(rep, txt[start:])
    open(dst, 'w', encoding='utf-8').write(out)
    print('nets kept:', stats['kept'], '| nets cleared:', stats['cleared'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
