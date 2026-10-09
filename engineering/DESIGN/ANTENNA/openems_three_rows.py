#!/usr/bin/env python3
"""openEMS model of THREE adjacent series-fed rows (mutual coupling S21/S31) of the AERIS-10 patch array (DSN-ANT-01).
NOT EXECUTED by the generator (openEMS not installed). Requires openEMS + python-openEMS (CSXCAD).
Geometry values come from tools/design_antenna_array.py; edit L_PATCH / QW_LEN to tune.
Usage: python3 openems_patch_row.py  -> writes S11 plot and NF2FF gain to ./openems_out/
"""
import os, numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0

F0 = 10500000000; FC = 1.5e9            # centre and half-bandwidth of the Gaussian excitation
ER = 3.66; H = 0.508e-3; TAND = 0.0037
L_SCALE = float(os.environ.get('L_SCALE', '1.0')); QW_SCALE = float(os.environ.get('QW_SCALE', '1.0'))
W_PATCH = 9.3524e-3; L_PATCH = L_SCALE*7.3025e-3; N_PATCH = 8
W_LINK = 0.2777e-3; L_LINK = 8.8405e-3
W_QW = 1.4508e-3; QW_LEN = QW_SCALE*4.1821e-3; W50 = 1.1120e-3; L50 = 10.0e-3
ROW_LEN = N_PATCH*L_PATCH + (N_PATCH-1)*L_LINK
PITCH = 14.3e-3
SUB_X = L50 + QW_LEN + ROW_LEN + 20e-3; SUB_Y = 2*PITCH + 40e-3
unit = 1
FDTD = openEMS(NrTS=120000, EndCriteria=1e-4)
FDTD.SetGaussExcite(F0, FC)
FDTD.SetBoundaryCond(['MUR']*4 + ['PEC', 'MUR'])   # ground plane side PEC
CSX = ContinuousStructure(); FDTD.SetCSX(CSX)
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(unit)
sub = CSX.AddMaterial('RO4350B', epsilon=ER, kappa=2*np.pi*F0*8.854e-12*ER*TAND)
sub.AddBox([0, -SUB_Y/2, -H], [SUB_X, SUB_Y, 0])
cu = CSX.AddMetal('copper')
boxes = []
def cubox(x0, y0, x1, y1):
    cu.AddBox([x0, y0, 0], [x1, y1, 0], priority=10); boxes.append((x0, y0, x1, y1))
ports = []
for r, yc in enumerate((-PITCH, 0.0, PITCH)):
    x = 0.0
    cubox(x, yc-W50/2, x+L50, yc+W50/2); x += L50
    cubox(x, yc-W_QW/2, x+QW_LEN, yc+W_QW/2); x += QW_LEN
    for k in range(N_PATCH):
        cubox(x, yc-W_PATCH/2, x+L_PATCH, yc+W_PATCH/2); x += L_PATCH
        if k < N_PATCH-1:
            cubox(x, yc-W_LINK/2, x+L_LINK, yc+W_LINK/2); x += L_LINK
    ports.append(FDTD.AddLumpedPort(r+1, 50, [1e-3, yc-W50/2, -H], [1e-3, yc+W50/2, 0], 'z', 1.0 if r == 1 else 0.0, priority=5, edges2grid='xy'))
port = ports[1]
res = C0/(F0+FC)/np.sqrt(ER)/20
xe = sorted({b[0] for b in boxes} | {b[2] for b in boxes} | {0.0, 1e-3, SUB_X})
ye = sorted({b[1] for b in boxes} | {b[3] for b in boxes} | {-SUB_Y/2, SUB_Y/2})
mesh.AddLine('x', xe + list(np.arange(-15e-3, 0, res)) + list(np.arange(SUB_X, SUB_X+15e-3, res)))
mesh.AddLine('y', ye + list(np.arange(-SUB_Y/2-15e-3, -SUB_Y/2, res)) + list(np.arange(SUB_Y/2, SUB_Y/2+15e-3, res)))
mesh.AddLine('z', list(np.linspace(-H, 0, 5)) + list(np.arange(res, 20e-3, res)))
mesh.SmoothMeshLines('all', res, 1.3)
nf2ff = FDTD.CreateNF2FFBox()
out = os.path.join(os.getcwd(), 'openems_out'); os.makedirs(out, exist_ok=True)
FDTD.Run(out, cleanup=True)
f = np.linspace(F0-FC, F0+FC, 401)
for p in ports: p.CalcPort(out, f)
s11 = ports[1].uf_ref/ports[1].uf_inc
s21 = ports[0].uf_ref/ports[1].uf_inc
s31 = ports[2].uf_ref/ports[1].uf_inc
i0 = np.argmin(np.abs(f-F0))
np.savetxt(os.path.join(out, 'coupling.csv'), np.c_[f/1e9, 20*np.log10(np.abs(s11)), 20*np.log10(np.abs(s21)), 20*np.log10(np.abs(s31))], delimiter=',', header='f_GHz,S22_dB(centre row),S12_dB,S32_dB', comments='')
print('RESULT_COUPLING', f[i0]/1e9, 20*np.log10(abs(s11[i0])), 20*np.log10(abs(s21[i0])), 20*np.log10(abs(s31[i0])), 20*np.log10(np.abs(s21)).max(), 20*np.log10(np.abs(s31)).max())
