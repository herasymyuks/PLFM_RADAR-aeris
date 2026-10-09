#!/usr/bin/env python3
"""beta_bom_mpn.py — BETA BOM with proposed manufacturer part numbers for the AERIS-10 boards.

Input : docs/BOM/BOM_<BOARD>.csv (value/deviceset/package/references from the EAGLE schematics, 0 MPN attributes)
Output: beta/pcb/<BOARD>/BOM_<BOARD>_beta.csv + confidence summary on stdout.
Confidence levels:
  HIGH   deviceset name IS the manufacturer part number (ICs, connectors, crystals...).
  MEDIUM standard passive proposed from value + package (orderable part, not confirmed by the designer).
  LOW    best guess (non-E-series value, package/value conflict, generic header/switch...).
  EMPTY  no value in the source — nothing proposed (do not invent values).
Nothing here is verified against the schematic intent; every line needs designer sign-off before purchase.
Usage: python3 beta_bom_mpn.py BOARD [BOARD ...]   (plain CPython, no KiCad needed)
"""
import csv, sys, re, os, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# ---- exact device-set MPNs (HIGH unless noted) -------------------------------------------------------
DEVICESETS = {
    '142-0731-211': ('Cinch Connectivity (Johnson)', '142-0731-211', 'HIGH', 'SMA end-launch jack'),
    '22-23-2021': ('Molex', '22-23-2021', 'HIGH', 'KK 254 header, 2 pos'),
    '22-23-2031': ('Molex', '22-23-2031', 'HIGH', 'KK 254 header, 3 pos'),
    'AK300/2': ('PTR Messtechnik', 'AK300/2', 'HIGH', 'screw terminal 2 pos (library con-ptr500); verify current PTR part code AK300/2-5.0'),
    'ADM7151ACPZ-04-R7': ('Analog Devices', 'ADM7151ACPZ-04-R7', 'HIGH', 'ultralow-noise LDO, LFCSP-8'),
    'AD9523BCPZ': ('Analog Devices', 'AD9523BCPZ', 'HIGH', 'clock generator, LFCSP-72'),
    'ADF4382ABCCZ': ('Analog Devices', 'ADF4382ABCCZ', 'HIGH', 'PLL/VCO synthesizer, LGA-48'),
    'ATS1005-3DB-FD-T05': ('Susumu (per package suffix _SUS — verify)', 'ATS1005-3DB-FD-T05', 'HIGH', 'SMT attenuator 3 dB'),
    'CJT-T-P-HH-ST-TH1': ('Samtec (per package suffix _SAI — verify)', 'CJT-T-P-HH-ST-TH1', 'HIGH', 'connector; manufacturer inferred from library suffix'),
    'CVHD-950-50.000': ('Crystek', 'CVHD-950-50.000', 'HIGH', 'OCXO/VCXO 50 MHz'),
    'ECOC-2522-100.000-3HC': ('ECS Inc.', 'ECOC-2522-100.000-3HC', 'HIGH', 'OCXO 100 MHz'),
    'FBMH1608HL601-T': ('Taiyo Yuden', 'FBMH1608HL601-T', 'HIGH', 'ferrite bead 0603, 600 Ω'),
    'MTX2-143+': ('Mini-Circuits', 'MTX2-143+', 'HIGH', 'RF transformer'),
    'LM2662MX/NOPB': ('Texas Instruments', 'LM2662MX/NOPB', 'HIGH', 'switched-capacitor inverter, SOIC-8'),
    'T521W476M020ATE045': ('KEMET', 'T521W476M020ATE045', 'HIGH', 'polymer tantalum 47 µF 20 V, case W'),
    'TPS562208DDCT': ('Texas Instruments', 'TPS562208DDCT', 'HIGH', '2 A buck converter, SOT-23-6'),
    'TPS7A8300RGRR': ('Texas Instruments', 'TPS7A8300RGRR', 'HIGH', '2 A LDO, VQFN-20'),
    'AD8352ACPZ-R7': ('Analog Devices', 'AD8352ACPZ-R7', 'HIGH', 'differential amplifier'),
    'AD9484BCPZ-500': ('Analog Devices', 'AD9484BCPZ-500', 'HIGH', '8-bit 500 MSPS ADC'),
    'AD9708AR': ('Analog Devices', 'AD9708ARZ', 'HIGH', 'deviceset AD9708AR = non-RoHS legacy suffix; RoHS orderable part is AD9708ARZ (same package SOIC-28)'),
    'ADAR1000ACCZN': ('Analog Devices', 'ADAR1000ACCZN', 'HIGH', 'X/Ku beamformer, LGA-88'),
    'ADS7830IPWR': ('Texas Instruments', 'ADS7830IPWR', 'HIGH', '8-ch 8-bit I2C ADC, TSSOP-16'),
    'ADTR1107ACCZ': ('Analog Devices', 'ADTR1107ACCZ', 'HIGH', 'front-end module, LGA-24'),
    'BLM15H': ('Murata', '', 'EMPTY', 'BLM15H = ferrite-bead series only (0402); impedance code missing in the source — part number cannot be completed'),
    'BPF2': ('', '', 'EMPTY', 'custom footprint "BPF2" (My_Library_RADAR); no part identified in schematic/BOM — designer must specify the filter'),
    'DAC5578SRGET': ('Texas Instruments', 'DAC5578SRGET', 'HIGH', '8-ch 8-bit DAC, VQFN-24'),
    'EP4RKU+': ('Mini-Circuits', 'EP4RKU+', 'HIGH', 'power splitter'),
    'FT601Q-B-T': ('FTDI', 'FT601Q-B-T', 'HIGH', 'USB 3.0 FIFO bridge, QFN-76 (schematic leaves its supply pins unconnected — see unresolved connections)'),
    'INA241A3IDGKR': ('Texas Instruments', 'INA241A3IDGKR', 'HIGH', 'current-sense amplifier, VSSOP-8'),
    'LTC5552IUDBTRMPBF': ('Analog Devices', 'LTC5552IUDB#TRMPBF', 'HIGH', 'mixer, QFN-12 (orderable code uses # separator)'),
    'M3SWA2-34DR+': ('Mini-Circuits', 'M3SWA2-34DR+', 'HIGH', 'RF switch'),
    'MA10-2': ('generic', 'TSW-110-07-G-D', 'LOW', 'EAGLE con-lstb MA10-2 = 2×10 pin header 2.54 mm; Samtec TSW-110-07-G-D proposed'),
    'MINI-USB-': ('Cypress Industries', '32005-201', 'HIGH', 'device name 32005-201 (library con-cypressindustries)'),
    'MOMENTARY-SWITCH-SPST': ('C&K', 'PTS810SJM250SMTRLFS', 'LOW', 'SparkFun SMD 4.6×2.8 mm tact switch; verify footprint match'),
    'MT25QL01GBBB8E12-0AUT': ('Micron', 'MT25QL01GBBB8E12-0AUT', 'HIGH', '1 Gbit QSPI flash, BGA-24'),
    'NX3225GD-8MHZ-STD-CRA-3': ('NDK', 'NX3225GD-8MHZ-STD-CRA-3', 'HIGH', '8 MHz crystal 3.2×2.5'),
    'OPA4703EA/250': ('Texas Instruments', 'OPA4703EA/250', 'HIGH', 'quad op-amp, TSSOP-14'),
    'PINHD-1X2': ('generic', '61300211121', 'LOW', 'Würth 2.54 mm 1×2 header proposed'),
    'PINHD-1X3': ('generic', '61300311121', 'LOW', 'Würth 2.54 mm 1×3 header proposed'),
    'PINHD-1X4': ('generic', '61300411121', 'LOW', 'Würth 2.54 mm 1×4 header proposed'),
    'PINHD-1X6': ('generic', '61300611121', 'LOW', 'Würth 2.54 mm 1×6 header proposed'),
    'PINHD-1X8': ('generic', '61300811121', 'LOW', 'Würth 2.54 mm 1×8 header proposed'),
    'PINHD-2X4': ('generic', '61300821121', 'LOW', 'Würth 2.54 mm 2×4 header proposed'),
    'PINHD-2X6': ('generic', '61301221121', 'LOW', 'Würth 2.54 mm 2×6 header proposed'),
    'PINHD-2X7': ('generic', '61301421121', 'LOW', 'Würth 2.54 mm 2×7 header proposed'),
    'SJ2W': ('', '', 'EMPTY', 'solder jumper — copper feature, not a purchasable part'),
    'STM32F746ZGT7': ('STMicroelectronics', 'STM32F746ZGT7', 'HIGH', 'Cortex-M7 MCU, LQFP-144'),
    'SZMMSZ5232BT1G': ('onsemi', 'SZMMSZ5232BT1G', 'HIGH', 'Zener 5.6 V, SOD-123'),
    'XC7A50T-2FTG256I': ('AMD (Xilinx)', 'XC7A50T-2FTG256I', 'HIGH', 'Artix-7 FPGA, FTG256'),
    'QPA2962_B': ('Qorvo', 'QPA2962', 'HIGH', 'power amplifier (EAGLE deviceset suffix _B stripped)'),
    'WSL2816R1000FEH': ('Vishay', 'WSL2816R1000FEH', 'MEDIUM', 'deviceset = 0.1 Ω shunt, but schematic value is 5 mΩ — conflict, designer to confirm (WSL2816R0050FEA would be the 5 mΩ part)'),
    'LED-GREEN': ('Würth', '150060GS75000', 'MEDIUM', 'green LED 0603'),
    'LED-BLUE': ('Würth', '150060BS75000', 'MEDIUM', 'blue LED 0603'),
}

def norm_val(v):
    v = v.strip().replace('µ', 'u').replace('Ω', 'R').replace('ohm', 'R')
    v = v.lower()
    m = re.match(r'^([0-9.]+)\s*([pnum]?)(f|h|r|k)?$', v)
    if m:
        num, pre, unit = m.groups()
        return (num, pre, unit or '')
    m = re.match(r'^([0-9]+)([kr])([0-9]+)$', v)  # 3k2
    if m: return (m.group(1) + '.' + m.group(3), m.group(2) if m.group(2) == 'k' else '', 'r' if m.group(2) == 'r' else 'k')
    return None

def to_farad(num, pre):
    return float(num) * {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, '': 1}[pre]

E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
E96 = [round(10 ** (i / 96), 2) for i in range(96)]
def is_e(val, series, tol=0.001):
    if val <= 0: return False
    import math
    m = val / 10 ** math.floor(math.log10(val + 1e-15) + 1e-9)
    return any(abs(m - e) / e < tol for e in series) or any(abs(m / 10 - e) / e < tol for e in series)
def nearest_e(val):
    import math
    dec = 10 ** math.floor(math.log10(val))
    cands = [e * dec for e in E96 + E24] + [e * dec * 10 for e in E96 + E24]
    return min(cands, key=lambda c: abs(c - val))

# Murata code pieces
CAP_CODE = {'p': lambda n: '%sR%s' % (n.split('.')[0], n.split('.')[1]) if '.' in n else None}
def murata_cap_code(farad):
    # 3-digit code: 2 significant digits + exponent (pF base)
    pf = farad * 1e12
    if pf < 1:
        return 'R%02d' % round(pf * 100) if abs(round(pf * 100) - pf * 100) < 1e-6 else None
    if pf < 10:
        s = ('%.1f' % pf).replace('.', 'R')
        return s if len(s) == 3 and abs(round(pf * 10) - pf * 10) < 1e-6 else None
    import math
    exp = int(math.floor(math.log10(pf))) - 1
    mant = round(pf / 10 ** exp)
    if mant >= 100: mant = round(mant / 10); exp += 1
    if abs(mant * 10 ** exp - pf) / pf > 0.02: return None
    return '%02d%d' % (mant, exp)

def cap_mpn(num, pre, pkg):
    f = to_farad(num, pre)
    code = murata_cap_code(f)
    pf = f * 1e12
    if code is None or not (is_e(pf, E24) or (pf < 10 and is_e(pf, [x / 10 for x in range(1, 100)]))):
        return ('Murata', '', 'LOW', 'non-E24 capacitance %s%sF (nearest standard %.3g pF) — value substitution is a design decision, designer to choose' % (num, pre, nearest_e(pf)))
    f = round(f, 15)
    if pkg == 'C0201':
        if pf < 1000:  # C0G 50 V
            return ('Murata', 'GRM0335C1H%sJA01D' % code if pf >= 10 else ('GRM0335C1H%sCA01D' % code if pf >= 1 else 'GRM0335C1H%sBA01D' % code), 'MEDIUM', '0201 C0G 50 V')
        if f <= 10e-9 * 1.001: return ('Murata', 'GRM033R71C%sKA01D' % code, 'MEDIUM', '0201 X7R 16 V')
        if f <= 100e-9 * 1.001: return ('Murata', 'GRM033R61A%sKE15D' % code, 'MEDIUM', '0201 X5R 10 V')
        if f <= 1e-6 * 1.001: return ('Murata', 'GRM033R60J%sKE90D' % code if f < 0.99e-6 else 'GRM033R60J105MEA2D', 'MEDIUM', '0201 X5R 6.3 V — voltage vs net to be verified')
        if f <= 4.7e-6 * 1.001: return ('Murata', 'GRM033R60G%sME47D' % code, 'LOW', '0201 X5R 4 V — only a few vendors offer >1 µF in 0201; verify availability and net voltage')
        return ('', '', 'LOW', '%s%sF does not exist in a 0201 package — package/value conflict in the source' % (num, pre))
    if pkg == 'C0402':
        if pf < 1000: return ('Murata', 'GRM1555C1H%sJA01D' % code if pf >= 10 else ('GRM1555C1H%sCA01D' % code if pf >= 1 else 'GRM1555C1H%sBA01D' % code), 'MEDIUM', '0402 C0G 50 V')
        if f <= 100e-9 * 1.001: return ('Murata', 'GRM155R71H%sKA01D' % code if f < 99e-9 else 'GRM155R71C104KA88D', 'MEDIUM', '0402 X7R (50 V / 16 V for 100 nF)')
        return ('Murata', 'GRM155R61A%sKE15D' % code, 'MEDIUM', '0402 X5R 10 V')
    if pkg == 'C0603':
        if f <= 100e-9 * 1.001: return ('Murata', 'GRM188R71H%sKA01D' % code, 'MEDIUM', '0603 X7R 50 V')
        if f <= 10e-6 * 1.001: return ('Murata', 'GRM188R61E%sMA73D' % code, 'MEDIUM', '0603 X5R 25 V')
        return ('Murata', 'GRM188R60J%sMEA0D' % code, 'MEDIUM', '0603 X5R 6.3 V — rail voltage to be verified')
    if pkg == 'C0805':
        if f <= 1e-6 * 1.001: return ('Murata', 'GRM21BR71H%sKA01L' % code if f < 0.99e-6 else 'GRM21BR71H105KA12L', 'MEDIUM', '0805 X7R 50 V')
        return ('Murata', 'GRM21BR61E%sKA73L' % code, 'MEDIUM', '0805 X5R 25 V')
    if pkg == 'C1206':
        if f <= 10e-6 * 1.001: return ('Murata', 'GRM31CR61E%sKA12L' % code, 'MEDIUM', '1206 X5R 25 V')
        return ('Murata', 'GRM31CR61E%sKE15L' % code, 'MEDIUM', '1206 X5R 25 V')
    if pkg == 'C1210':
        if f <= 10e-6 * 1.001: return ('Murata', 'GRM32ER71E%sKA12L' % code, 'MEDIUM', '1210 X7R 25 V')
        return ('Murata', 'GRM32ER61E%sKE15L' % code, 'MEDIUM', '1210 X5R 25 V')
    return ('', '', 'LOW', 'unknown capacitor package %s' % pkg)

def res_mpn(num, pre, unit, pkg):
    ohm = float(num) * (1e3 if (unit == 'k' or pre == 'k') else (1e6 if pre == 'm' and unit != 'r' and False else 1))
    size = {'R0201': 'RC0201', 'R0402': 'RC0402', 'R0603': 'RC0603', 'M0805': 'RC0805', 'R0805': 'RC0805'}.get(pkg)
    if not size: return ('', '', 'LOW', 'unknown resistor package %s' % pkg)
    if ohm == 0: return ('Yageo', '%sJR-070RL' % size, 'MEDIUM', 'jumper 0 Ω')
    if not (is_e(ohm, E96) or is_e(ohm, E24)):
        return ('Yageo', '', 'LOW', 'non-E24/E96 value %s %sΩ (nearest standard %.4g Ω) — value substitution is a design decision (Yageo %sFR-07 series)' % (num, pre.upper(), nearest_e(ohm), size))
    # Yageo value code: 100R, 22R1, 10K, 22K1, 1M
    unit, letter = (1, 'R') if ohm < 1000 else ((1e3, 'K') if ohm < 1e6 else (1e6, 'M'))
    mant = '%.4g' % (ohm / unit)
    v = mant.replace('.', letter) if '.' in mant else mant + letter
    return ('Yageo', '%sFR-07%sL' % (size, v), 'MEDIUM', '1 % thick film')

def ind_mpn(num, pre, pkg, deviceset):
    if pkg == 'IND_VLP8040T-1R0N_TDK':
        h = float(num) * {'u': 1e-6, 'n': 1e-9}[pre]
        code = {2.2: 'VLP8040T-2R2M', 3.3: 'VLP8040T-3R3M'}.get(round(h * 1e6, 2))
        return ('TDK', code or '', 'MEDIUM' if code else 'LOW', 'footprint is the VLP8040T 1R0N (1 µH) variant; value %s%sH → same series part proposed' % (num, pre))
    if pkg == 'L0201':
        nh = float(num) * {'n': 1, 'u': 1000}[pre]
        if not is_e(nh, E24): return ('Murata', '', 'LOW', 'non-standard inductance %s nH for 0201 — designer to select (Murata LQP03T series)' % nh)
        if nh < 10: code = ('%g' % nh).replace('.', 'N') if '.' in '%g' % nh else '%gN0' % nh
        else: code = '%dN' % nh
        if nh > 120: return ('Murata', '', 'LOW', '%g nH exceeds the 0201 thin-film inductor range (LQP03T max ~120 nH) — designer to confirm part/package' % nh)
        return ('Murata', 'LQP03TN%s%s02D' % (code, 'B' if nh < 10 else 'J'), 'MEDIUM', '0201 thin-film inductor')
    return ('', '', 'LOW', 'inductor package %s' % pkg)

def main():
    boards = sys.argv[1:] or ['MAIN_BOARD', 'POWER_SUPPLY', 'RF_PA', 'FREQUENCY_SYNTHESIZER']
    for board in boards:
        src = os.path.join(ROOT, 'docs', 'BOM', 'BOM_%s.csv' % board)
        dst = os.path.join(ROOT, 'beta', 'pcb', board, 'BOM_%s_beta.csv' % board)
        rows = list(csv.DictReader(open(src, encoding='utf-8')))
        out = []; summary = collections.Counter(); qty = collections.Counter()
        for r in rows:
            ds, val, pkg, dev = r['deviceset'], r['value'].strip(), r['package'], r.get('device', '')
            man, mpn, conf, note = '', '', 'EMPTY', ''
            dnp = 'no'
            if ds in DEVICESETS:
                man, mpn, conf, note = DEVICESETS[ds]
                if ds == 'NX3225GD-8MHZ-STD-CRA-3' and val:
                    man, mpn, conf, note = ('NDK', 'NX3215SA-32.768K-STD-MUA-8', 'LOW', 'value says 32.768 kHz crystal but deviceset/footprint is the NX3225GD 8 MHz part — conflict; NX3215SA proposed, footprint to be verified')
            elif ds in ('C-EU', 'C') and val:
                nv = norm_val(val)
                if nv and nv[2] in ('f', ''): man, mpn, conf, note = cap_mpn(nv[0], nv[1], pkg)
                else: conf, note = 'LOW', 'unparsed value %s' % val
            elif ds in ('R-EU_', 'R') and val:
                nv = norm_val(val)
                if nv: man, mpn, conf, note = res_mpn(nv[0], nv[1], nv[2], pkg)
                else: conf, note = 'LOW', 'unparsed value %s' % val
            elif ds in ('L-EU', 'L-US', 'L', 'POWER_INDUCTOR') and val:
                nv = norm_val(val)
                if nv: man, mpn, conf, note = ind_mpn(nv[0], nv[1], pkg, ds)
                else: conf, note = 'LOW', 'unparsed value %s' % val
            elif not val:
                conf, note = 'EMPTY', 'no value in the schematic (%s / %s) — cannot propose a part' % (ds, pkg)
            else:
                conf, note = 'LOW', 'no rule for deviceset %s' % ds
            refs = r['references'].split()
            if board == 'MAIN_BOARD' and set(refs) <= {'R60', 'R61', 'R83', 'R84', 'R145', 'R146'}:
                dnp = 'yes'; note = (note + '; ' if note else '') + 'no net on any pin and parked outside the outline in the source layout — treated as DNP'
            if ds == 'SJ2W': dnp = 'n/a'
            out.append(dict(item=r['item'], qty=r['qty'], references=r['references'], value=val, deviceset=ds, device=dev, package=pkg,
                            manufacturer=man, mpn=mpn, mpn_confidence=conf, dnp=dnp, note=note))
            summary[conf] += 1; qty[conf] += int(r['qty'])
        with open(dst, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
        print('%s: %d lines -> %s' % (board, len(out), os.path.relpath(dst, ROOT)))
        for c in ('HIGH', 'MEDIUM', 'LOW', 'EMPTY'): print('   %-6s lines=%3d qty=%4d' % (c, summary[c], qty[c]))
    return 0

if __name__ == '__main__':
    sys.exit(main())
