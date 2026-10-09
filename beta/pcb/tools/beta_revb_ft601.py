#!/usr/bin/env python3
"""beta_revb_ft601.py — Main Board rev. B (PROPOSAL): wire the FT601 (U6) USB 3.0 host interface.

THIS IS AN EXPLICIT NETLIST CHANGE (rev. B). Source design: engineering/DESIGN/HOST_LINK/ (HOST_LINK_DESIGN.md §4,
ft601_pin_assignment.csv, ft601_added_parts_BOM.csv, ft601_bank35.xdc). Every pcbnew call that changes the board is
in this file; running it again on the same input produces the same rev. B board (before routing).

  input : beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb (+ .kicad_pro)       (BETA rev. A, untouched)
  output: beta/pcb/MAIN_BOARD_REVB/MAIN_BOARD_REVB.kicad_pcb (+ .kicad_pro with FT_BUS / USB_DIFF / FT_PWR netclasses)
          beta/pcb/MAIN_BOARD_REVB/NETLIST_DELTA.csv  (one row per new pad-net connection)
          beta/pcb/MAIN_BOARD_REVB/revb_parts.json    (added footprints: ref, footprint, value, MPN, position)

Steps (pcbnew API):
  1. NETINFO_ITEM(board, name) + board.Add(net) for every new net.
  2. PAD.SetNet(net) on U6 (QFN76 pads per the EAGLE library connect map) and U42 bank-35 pads per the CSV.
  3. FootprintLoad(<KiCad library>.pretty, name) for each added part, SetReference/SetValue/SetField(MPN...)/
     SetPosition/SetOrientationDegrees, board.Add(fp), PAD.SetNet for its pads.
  4. Project netclasses + patterns written into the .kicad_pro (JSON).
Usage: KiCad python3 beta/pcb/tools/beta_revb_ft601.py  [--root REPO]
Exit 0 ok, 2 on a missing pad/footprint (nothing is saved then).
"""
import sys, os, csv, json, shutil
import pcbnew

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if '--root' in sys.argv: ROOT = sys.argv[sys.argv.index('--root') + 1]
SRC = os.path.join(ROOT, 'beta/pcb/MAIN_BOARD/MAIN_BOARD.kicad_pcb')
OUTD = os.path.join(ROOT, 'beta/pcb/MAIN_BOARD_REVB'); DST = os.path.join(OUTD, 'MAIN_BOARD_REVB.kicad_pcb')
CSV = os.path.join(ROOT, 'engineering/DESIGN/HOST_LINK/ft601_pin_assignment.csv')
FPLIB = os.environ.get('KICAD_FOOTPRINT_DIR', os.path.expanduser('~/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'))

delta = []      # rows for NETLIST_DELTA.csv
parts = []
def mm(x, y): return pcbnew.VECTOR2I(int(round(x * 1e6)), int(round(y * 1e6)))

def main():
    b = pcbnew.LoadBoard(SRC)
    nets = {}
    def net(name):
        if name in nets: return nets[name]
        ni = b.GetNetInfo().GetNetItem(name)
        if ni is None or ni.GetNetCode() <= 0:
            ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
            delta.append(dict(change='NEW NET', net=name, ref='', pad='', old_net='', note=''))
        nets[name] = ni; return ni
    def connect(ref, padnum, netname, note=''):
        fp = b.FindFootprintByReference(ref)
        if fp is None: raise SystemExit('missing footprint %s' % ref)
        pads = [p for p in fp.Pads() if p.GetNumber() == padnum]
        if not pads: raise SystemExit('missing pad %s.%s' % (ref, padnum))
        for p in pads:
            old = p.GetNetname(); p.SetNet(net(netname))
            delta.append(dict(change='CONNECT', net=netname, ref=ref, pad=padnum, old_net=old, note=note))

    # ---- 1/2. FT601 signals: U6 pad <-> U42 bank-35 pad (ft601_pin_assignment.csv) ----
    rows = list(csv.DictReader(open(CSV, encoding='utf-8')))
    xdc = []
    for r in rows:
        n = r['proposed_net']; ftpad = r['ft601_pad(QFN76, from EAGLE lib)']
        connect('U6', ftpad, n, 'FT601 %s' % r['ft601_signal'])
        connect('U42', r['fpga_pad'], n, '%s (%s) %s' % (r['fpga_pin_name'], r['iostandard'], r['direction(FT601 view)']))
        xdc.append((n, r['fpga_pad'], r['fpga_pin_name']))
    # ---- U6 supplies, ground, analogue, clock, USB (pad numbers = EAGLE library connect map of FT601Q-B-T) ----
    for p in ('20', '24', '38'): connect('U6', p, '+3V3_FT', 'VCC33')
    for p in ('14', '49', '59', '68'): connect('U6', p, '+3V3_FT', 'VCCIO')
    for p in ('77', '1', '26', '29', '36'): connect('U6', p, 'GND', 'GND / exposed pad')
    for p in ('2', '28'): connect('U6', p, 'FT_AVDD', 'AVDD/VDDA via FB_A from +3V3_FT')
    for p in ('3', '30', '33', '48', '39'): connect('U6', p, 'FT_VD10', 'VD10/DV10 1.0 V core — VERIFY datasheet (internal regulator output assumed)')
    connect('U6', '21', 'FT_XI', 'XI'); connect('U6', '22', 'FT_XO', 'XO')
    connect('U6', '27', 'FT_RREF', 'RREF')
    connect('U6', '37', 'FT_VBUS_DET', 'VBUS detect (divider)')
    connect('U6', '23', 'USB_DP', 'DP'); connect('U6', '25', 'USB_DM', 'DM')
    connect('U6', '32', 'USB_SSTX_P', 'TODP (to AC-coupling cap)'); connect('U6', '31', 'USB_SSTX_N', 'TODN (to AC-coupling cap)')
    connect('U6', '35', 'USB_SSRX_P', 'RIDP'); connect('U6', '34', 'USB_SSRX_N', 'RIDN')

    # ---- 3. added parts (library footprints of KiCad 10) ----
    def add(ref, lib, name, value, mpn, mfr, x, y, rot, padnets, note=''):
        fp = pcbnew.FootprintLoad(os.path.join(FPLIB, lib + '.pretty'), name)
        if fp is None: raise SystemExit('footprint not found %s:%s' % (lib, name))
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPosition(mm(x, y)); fp.SetOrientationDegrees(rot)
        b.Add(fp)
        for k, v in (('MPN', mpn), ('Manufacturer', mfr), ('Revision', 'B (proposal)')):
            f = pcbnew.PCB_FIELD(fp, fp.GetNextFieldOrdinal(), k); f.SetText(v); f.SetVisible(False); f.SetLayer(pcbnew.F_Fab); fp.Add(f)
        for padnum, n in padnets.items():
            for p in fp.Pads():
                if p.GetNumber() == padnum:
                    p.SetNet(net(n))
            delta.append(dict(change='CONNECT (new part)', net=n, ref=ref, pad=padnum, old_net='', note=note))
        parts.append(dict(ref=ref, footprint='%s:%s' % (lib, name), value=value, mpn=mpn, manufacturer=mfr, x=x, y=y, rot=rot, note=note))
        return fp

    # USB-C receptacle, full 24-pin (USB 3.x) — left board edge, mating face toward x = 0
    usb = {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND',
           'A4': 'USB_VBUS', 'A9': 'USB_VBUS', 'B4': 'USB_VBUS', 'B9': 'USB_VBUS',
           'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A6': 'USB_DP', 'B6': 'USB_DP', 'A7': 'USB_DM', 'B7': 'USB_DM',
           'A2': 'USB_SSTX_C_P', 'A3': 'USB_SSTX_C_N', 'B11': 'USB_SSRX_P', 'B10': 'USB_SSRX_N'}
    add('J_USB3', 'Connector_USB', 'USB_C_Receptacle_Amphenol_12401610E4-2A', 'USB-C 3.1 receptacle', '12401610E4#2A', 'Amphenol ICC',
        4.0, -208.0, 270, usb, 'only the TX1/RX1 SuperSpeed lane is wired (no orientation mux): SS works in one plug orientation, USB 2.0 in both — VERIFY acceptable')
    # ESD arrays (flow-through: pads 1/10, 2/9, 4/7, 5/6 on the same line), GND pads 3/8
    add('D_ESD1', 'Package_SON', 'USON-10_2.5x1.0mm_P0.5mm', 'TPD4E05U06', 'TPD4E05U06DQAR', 'Texas Instruments', 12.5, -210.0, 0,
        {'1': 'USB_SSTX_C_P', '10': 'USB_SSTX_C_P', '2': 'USB_SSTX_C_N', '9': 'USB_SSTX_C_N', '4': 'USB_SSRX_P', '7': 'USB_SSRX_P', '5': 'USB_SSRX_N', '6': 'USB_SSRX_N', '3': 'GND', '8': 'GND'},
        'pin-out per TPD4E05U06 DQA flow-through (1,2,4,5 IO; 6,7,9,10 NC pass-through; 3,8 GND) — VERIFY')
    add('D_ESD2', 'Package_SON', 'USON-10_2.5x1.0mm_P0.5mm', 'TPD4E05U06', 'TPD4E05U06DQAR', 'Texas Instruments', 12.5, -206.0, 0,
        {'1': 'USB_DP', '10': 'USB_DP', '2': 'USB_DM', '9': 'USB_DM', '3': 'GND', '8': 'GND'},
        'second array for D+/D- (the design BOM lists one 4-channel array for SS+HS = 6 lines) — channels 3/4 unused')
    # SuperSpeed TX AC-coupling capacitors (USB 3 spec 75–265 nF) — not in the design BOM, required by the spec
    add('C_SSTX_P', 'Capacitor_SMD', 'C_0402_1005Metric', '100nF', 'GRM155R71C104KA88D', 'Murata', 16.5, -211.2, 0, {'1': 'USB_SSTX_P', '2': 'USB_SSTX_C_P'}, 'USB 3 TX AC coupling — added (spec requirement), VERIFY')
    add('C_SSTX_N', 'Capacitor_SMD', 'C_0402_1005Metric', '100nF', 'GRM155R71C104KA88D', 'Murata', 16.5, -210.0, 0, {'1': 'USB_SSTX_N', '2': 'USB_SSTX_C_N'}, 'USB 3 TX AC coupling — added (spec requirement), VERIFY')
    # CC pull-downs (UFP/device) — required for a Type-C device receptacle
    add('R_CC1', 'Resistor_SMD', 'R_0402_1005Metric', '5.1k', 'RC0402FR-075K1L', 'Yageo', 11.0, -214.0, 0, {'1': 'USB_CC1', '2': 'GND'}, 'Type-C Rd 5.1 kΩ (device) — added because a USB-C receptacle was chosen')
    add('R_CC2', 'Resistor_SMD', 'R_0402_1005Metric', '5.1k', 'RC0402FR-075K1L', 'Yageo', 11.0, -202.5, 0, {'1': 'USB_CC2', '2': 'GND'}, 'Type-C Rd 5.1 kΩ (device)')
    # VBUS detect divider 10 k / 3.3 k
    add('R_VBUS_1', 'Resistor_SMD', 'R_0402_1005Metric', '10k', 'RC0402FR-0710KL', 'Yageo', 32.5, -201.9, 90, {'1': 'USB_VBUS', '2': 'FT_VBUS_DET'}, 'VERIFY VBUS pin limit')
    add('R_VBUS_2', 'Resistor_SMD', 'R_0402_1005Metric', '3.3k', 'RC0402FR-073K3L', 'Yageo', 33.7, -201.9, 90, {'1': 'FT_VBUS_DET', '2': 'GND'}, 'VERIFY VBUS pin limit')
    # RREF
    add('R_RREF', 'Resistor_SMD', 'R_0402_1005Metric', '3.24k 1%', 'RC0402FR-073K24L', 'Yageo', 26.3, -201.9, 90, {'1': 'FT_RREF', '2': 'GND'}, 'value per FT60x datasheet — VERIFY')
    # 1.0 V core decoupling
    for i, (x, y, r) in enumerate([(20.3, -210.4, 90), (27.5, -201.9, 90), (28.7, -201.9, 90), (29.9, -201.9, 90)], 1):
        add('C_VD10_%d' % i, 'Capacitor_SMD', 'C_0402_1005Metric', '4.7uF 6.3V', 'GRM155R60J475ME47D', 'Murata', x, y, r, {'1': 'FT_VD10', '2': 'GND'}, 'VD10/DV10 decoupling — VERIFY')
    # AVDD / VDDA filter
    add('FB_A', 'Inductor_SMD', 'L_0603_1608Metric', '600R@100MHz', 'BLM18PG601SN1D', 'Murata', 18.0, -214.6, 0, {'1': '+3V3_FT', '2': 'FT_AVDD'}, '+3V3_FT -> AVDD/VDDA')
    add('C_AVDD_1', 'Capacitor_SMD', 'C_0402_1005Metric', '100nF', 'GRM155R71C104KA88D', 'Murata', 20.3, -212.6, 90, {'1': 'FT_AVDD', '2': 'GND'})
    add('C_AVDD_2', 'Capacitor_SMD', 'C_0402_1005Metric', '1uF', 'GRM155R61A105KE15D', 'Murata', 19.2, -212.6, 90, {'1': 'FT_AVDD', '2': 'GND'})
    # 30 MHz crystal + 2 x 18 pF
    add('Y_FT', 'Crystal', 'Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm', '30MHz 18pF', 'ABM8-30.000MHZ-B2-T', 'Abracon', 22.5, -199.6, 0,
        {'1': 'FT_XI', '3': 'FT_XO', '2': 'GND', '4': 'GND'}, 'ABM8 land pattern (3.2×2.5, 4 pads; ABM8G footprint of the KiCad library) — VERIFY')
    add('C_XI', 'Capacitor_SMD', 'C_0402_1005Metric', '18pF C0G', 'GRM1555C1H180JA01D', 'Murata', 19.6, -198.75, 0, {'1': 'FT_XI', '2': 'GND'}, 'load cap — VERIFY against crystal CL')
    add('C_XO', 'Capacitor_SMD', 'C_0402_1005Metric', '18pF C0G', 'GRM1555C1H180JA01D', 'Murata', 25.2, -199.2, 0, {'1': 'FT_XO', '2': 'GND'}, 'load cap — VERIFY against crystal CL')

    os.makedirs(OUTD, exist_ok=True)
    pcbnew.SaveBoard(DST, b)
    # ---- 4. project: copy rev. A project, add netclasses for the new nets ----
    pro = json.load(open(SRC.replace('.kicad_pcb', '.kicad_pro')))
    base = dict(pro['net_settings']['classes'][0])
    def cls(name, w, clr, dw=None, dg=None, via=(0.45, 0.2)):
        c = dict(base); c.update(name=name, track_width=w, clearance=clr, via_diameter=via[0], via_drill=via[1], priority=0)
        if dw: c.update(diff_pair_width=dw, diff_pair_gap=dg)
        return c
    pro['net_settings']['classes'] = [base] + [cls('FT_BUS', 0.204, 0.1), cls('USB_DIFF', 0.204, 0.1, 0.204, 0.18), cls('FT_PWR', 0.3, 0.1)]
    pro['net_settings']['netclass_patterns'] = [
        {'netclass': 'FT_BUS', 'pattern': 'FT_DATA_*'}, {'netclass': 'FT_BUS', 'pattern': 'FT_BE_*'},
        {'netclass': 'FT_BUS', 'pattern': 'FT_CLK'}, {'netclass': 'FT_BUS', 'pattern': 'FT_*_N'}, {'netclass': 'FT_BUS', 'pattern': 'FT_GPIO*'},
        {'netclass': 'USB_DIFF', 'pattern': 'USB_D?'}, {'netclass': 'USB_DIFF', 'pattern': 'USB_SS*'},
        {'netclass': 'FT_PWR', 'pattern': 'FT_VD10'}, {'netclass': 'FT_PWR', 'pattern': 'FT_AVDD'}, {'netclass': 'FT_PWR', 'pattern': 'USB_VBUS'}]
    pro['meta']['filename'] = 'MAIN_BOARD_REVB.kicad_pro'
    json.dump(pro, open(DST.replace('.kicad_pcb', '.kicad_pro'), 'w'), indent=2)
    with open(os.path.join(OUTD, 'NETLIST_DELTA.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['change', 'net', 'ref', 'pad', 'old_net', 'note']); w.writeheader(); w.writerows(delta)
    json.dump(dict(parts=parts, fpga_pins=[dict(net=n, pad=p, pin=pn) for n, p, pn in xdc]), open(os.path.join(OUTD, 'revb_parts.json'), 'w'), indent=1)
    print('new nets:', sum(1 for d in delta if d['change'] == 'NEW NET'), '| pad connections:', sum(1 for d in delta if d['change'] != 'NEW NET'), '| parts added:', len(parts))
    print('saved', DST)
    return 0

if __name__ == '__main__':
    sys.exit(main())
