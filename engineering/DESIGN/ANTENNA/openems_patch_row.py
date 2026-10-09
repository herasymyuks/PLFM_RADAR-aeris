#!/usr/bin/env python3
"""openEMS model of ONE series-fed row of the AERIS-10 patch array (DSN-ANT-01).
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
W_PATCH = 9.3524e-3; L_PATCH = 7.3025e-3; N_PATCH = 8
W_LINK = 0.2777e-3; L_LINK = 8.8405e-3
W_QW = 1.4508e-3; QW_LEN = 4.1821e-3; W50 = 1.1120e-3; L50 = 10.0e-3
ROW_LEN = N_PATCH*L_PATCH + (N_PATCH-1)*L_LINK
SUB_X = L50 + QW_LEN + ROW_LEN + 20e-3; SUB_Y = 40e-3
unit = 1
FDTD = openEMS(NrTS=300000, EndCriteria=1e-4)
FDTD.SetGaussExcite(F0, FC)
FDTD.SetBoundaryCond(['MUR']*4 + ['PEC', 'MUR'])   # ground plane side PEC
CSX = ContinuousStructure(); FDTD.SetCSX(CSX)
mesh = CSX.GetGrid(); mesh.SetDeltaUnit(unit)
sub = CSX.AddMaterial('RO4350B', epsilon=ER, kappa=2*np.pi*F0*8.854e-12*ER*TAND)
sub.AddBox([0, -SUB_Y/2, -H], [SUB_X, SUB_Y, 0])
cu = CSX.AddMetal('copper')
x = 0.0; yc = 0.0
cu.AddBox([x, yc-W50/2, 0], [x+L50, yc+W50/2, 0]); x += L50
cu.AddBox([x, yc-W_QW/2, 0], [x+QW_LEN, yc+W_QW/2, 0]); x += QW_LEN
for k in range(N_PATCH):
    cu.AddBox([x, yc-W_PATCH/2, 0], [x+L_PATCH, yc+W_PATCH/2, 0]); x += L_PATCH
    if k < N_PATCH-1:
        cu.AddBox([x, yc-W_LINK/2, 0], [x+L_LINK, yc+W_LINK/2, 0]); x += L_LINK
port = FDTD.AddLumpedPort(1, 50, [1e-3, yc-W50/2, -H], [1e-3, yc+W50/2, 0], 'z', 1.0, priority=5, edges2grid='xy')
res = C0/(F0+FC)/np.sqrt(ER)/25
mesh.AddLine('x', np.arange(-15e-3, SUB_X+15e-3, res)); mesh.AddLine('y', np.arange(-SUB_Y/2-15e-3, SUB_Y/2+15e-3, res))
mesh.AddLine('z', np.concatenate((np.linspace(-H, 0, 5), np.arange(0, 20e-3, res))))
mesh.SmoothMeshLines('all', res, 1.4)
nf2ff = FDTD.CreateNF2FFBox()
out = os.path.join(os.getcwd(), 'openems_out'); os.makedirs(out, exist_ok=True)
FDTD.Run(out, cleanup=True)
f = np.linspace(F0-FC, F0+FC, 401); port.CalcPort(out, f)
s11 = port.uf_ref/port.uf_inc
import matplotlib.pyplot as plt
plt.plot(f/1e9, 20*np.log10(np.abs(s11))); plt.grid(); plt.xlabel('GHz'); plt.ylabel('|S11| dB'); plt.savefig(os.path.join(out, 's11_row.png'))
idx = np.argmin(np.abs(s11)); print('best match', f[idx]/1e9, 'GHz', 20*np.log10(abs(s11[idx])), 'dB')
ff = nf2ff.CalcNF2FF(out, f[idx], np.arange(-180, 180, 1), [0, 90]); print('Dmax', 10*np.log10(ff.Dmax[0]), 'dBi')
