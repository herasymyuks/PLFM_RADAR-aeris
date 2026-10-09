#!/usr/bin/env python3
"""
gen_vectors.py - generate the numpy reference vectors used by the beta testbenches.

Outputs (tb/vectors/):
  fft32_in.hex / fft32_exp.hex       32-point FFT: 4 frames, config words per frame in fft32_cfg.hex
  fft1024_in.hex / fft1024_exp.hex   1024-point FFT: 2 frames (forward, inverse), cfg in fft1024_cfg.hex
  mf_input.hex                       1024 complex samples ({Q,I} words): time-domain chirp segment 1, circularly
                                     delayed by MF_DELAY bins, amplitude MF_AMP  (I Q per line)
  mf_expected.txt                    one line: expected peak bin and the numpy peak/second ratio
  decim_in.hex / decim_exp.hex       1024 input bins and 64 expected peak-mode outputs

Fixed-point model (identical to rtl/axis_fft_behav.v): exact FFT in double precision, inverse
transform without 1/N, multiplied by 2^-(sum of scale schedule fields), round-half-up, saturate
to 16 bits. The Xilinx IP rounds per stage, so the testbench tolerance is +/-2 LSB.
Usage: python3 tb/gen_vectors.py   (writes into tb/vectors next to this script)
Dependencies: Python 3.8+, numpy.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "vectors")
MEM = os.path.join(HERE, "..", "mem")
MF_DELAY = 300
MF_AMP = 6000.0
RNG = np.random.default_rng(20261009)


def h16(v):
    return "%04x" % (int(v) & 0xFFFF)


def fixed(x, w=16):
    r = np.floor(x + 0.5)
    r = np.clip(r, -(2 ** (w - 1)), 2 ** (w - 1) - 1)
    return r.astype(np.int64)


def total_shift(cfg, log2n):
    r4 = log2n // 2
    s = 0
    for k in range(r4):
        s += (cfg >> (1 + 2 * k)) & 3
    if log2n % 2:
        s += (cfg >> (1 + 2 * r4)) & 1
    return s


def model_fft(z, cfg, log2n):
    n = len(z)
    X = np.fft.fft(z) if (cfg & 1) else np.fft.ifft(z) * n   # inverse without 1/N
    X = X / (2.0 ** total_shift(cfg, log2n))
    return fixed(X.real), fixed(X.imag)


def write_pairs(path, re, im):
    """one 32-bit word per line: {Q[15:0], I[15:0]} (readable with $readmemh into reg [31:0])"""
    with open(path, "w") as f:
        for a, b in zip(re, im):
            f.write("%s%s\n" % (h16(b), h16(a)))


def read_mem(path):
    v = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s:
                x = int(s, 16)
                v.append(x - 0x10000 if x >= 0x8000 else x)
    return np.array(v, dtype=np.int64)


def main():
    os.makedirs(OUT, exist_ok=True)

    # ---------------- 32-point FFT, 4 frames ----------------
    cfgs32 = [0x01, 0x0B, 0x3F, 0x3E]   # fwd/no scale (small input), fwd/sch=5 (/2^... ), fwd full, inv full
    ins_re, ins_im, exp_re, exp_im = [], [], [], []
    for i, cfg in enumerate(cfgs32):
        amp = 900 if cfg == 0x01 else 30000
        z = RNG.integers(-amp, amp, 32) + 1j * RNG.integers(-amp, amp, 32)
        if i == 2:   # a pure tone at bin 5 -> single strong output bin
            z = 20000 * np.exp(1j * 2 * np.pi * 5 * np.arange(32) / 32)
            z = np.round(z.real) + 1j * np.round(z.imag)
        er, ei = model_fft(z, cfg, 5)
        ins_re += list(z.real.astype(np.int64)); ins_im += list(z.imag.astype(np.int64))
        exp_re += list(er); exp_im += list(ei)
    write_pairs(os.path.join(OUT, "fft32_in.hex"), ins_re, ins_im)
    write_pairs(os.path.join(OUT, "fft32_exp.hex"), exp_re, exp_im)
    with open(os.path.join(OUT, "fft32_cfg.hex"), "w") as f:
        for c in cfgs32:
            f.write("%02x\n" % c)

    # ---------------- 1024-point FFT, 2 frames ----------------
    cfgs1024 = [(0x255 << 1) | 1, (0x155 << 1) | 0]   # forward 2^-6, inverse 2^-5 (chain defaults)
    ins_re, ins_im, exp_re, exp_im = [], [], [], []
    for cfg in cfgs1024:
        z = RNG.integers(-8000, 8000, 1024) + 1j * RNG.integers(-8000, 8000, 1024)
        er, ei = model_fft(z, cfg, 10)
        ins_re += list(z.real.astype(np.int64)); ins_im += list(z.imag.astype(np.int64))
        exp_re += list(er); exp_im += list(ei)
    write_pairs(os.path.join(OUT, "fft1024_in.hex"), ins_re, ins_im)
    write_pairs(os.path.join(OUT, "fft1024_exp.hex"), exp_re, exp_im)
    with open(os.path.join(OUT, "fft1024_cfg.hex"), "w") as f:
        for c in cfgs1024:
            f.write("%04x\n" % c)

    # ---------------- matched filter unit test ----------------
    # reference segment 1 as stored in the memory: M = conj(FFT(u_seg)) -> u_seg = conj(ifft(M)[-n])
    M = read_mem(os.path.join(MEM, "long_chirp_seg1_i.mem")) + 1j * read_mem(os.path.join(MEM, "long_chirp_seg1_q.mem"))
    t = np.fft.ifft(M)
    u_seg = np.conj(t[(-np.arange(1024)) % 1024])
    u_seg = u_seg / np.abs(u_seg).max() * MF_AMP
    x = np.roll(u_seg, MF_DELAY)                       # received = reference delayed by MF_DELAY bins
    xi, xq = fixed(x.real), fixed(x.imag)
    write_pairs(os.path.join(OUT, "mf_input.hex"), xi, xq)
    # chain model: fwd FFT /2^6 -> Q15 conj multiply -> inverse /2^5
    Xf = np.fft.fft(xi + 1j * xq) / 64.0
    Xf = fixed(Xf.real) + 1j * fixed(Xf.imag)
    P = Xf * M / 32768.0                               # M already is conj(FFT(ref)) -> correlation
    P = fixed(P.real) + 1j * fixed(P.imag)
    y = np.fft.ifft(P) * 1024 / 32.0
    y = fixed(y.real) + 1j * fixed(y.imag)
    mag = np.abs(y)
    peak = int(mag.argmax())
    # the segment spans 6.67 MHz -> compressed pulse ~15 bins wide; compare against bins
    # outside +/-MAINLOBE of the peak (sidelobe / noise floor)
    MAINLOBE = 16
    mask = np.abs(((np.arange(1024) - peak + 512) % 1024) - 512) > MAINLOBE
    ratio = mag[peak] / mag[mask].max()
    # the memory holds conj(FFT(u)) and the chain multiplies without a further conjugation
    # (frequency_matched_filter CONJUGATE_REF = 0), so the peak must appear at bin MF_DELAY.
    assert peak == MF_DELAY, "model peak %d != delay %d" % (peak, MF_DELAY)
    with open(os.path.join(OUT, "mf_expected.txt"), "w") as f:
        f.write("%d %d %.2f\n" % (peak, int(mag[peak]), ratio))
    with open(os.path.join(OUT, "mf_expected.hex"), "w") as f:   # [0] peak bin, [1] |peak| (model)
        f.write("%08x\n%08x\n" % (peak, int(mag[peak])))
    print("matched filter: delay=%d -> model peak bin %d, |peak|=%d, peak/next=%.2f" % (MF_DELAY, peak, mag[peak], ratio))

    # ---------------- range bin decimator ----------------
    bins = RNG.integers(-3000, 3000, (1024, 2))
    bins[517] = [20000, -1000]      # a strong target in group 32
    bins[40] = [-15000, 15000]      # another in group 2
    write_pairs(os.path.join(OUT, "decim_in.hex"), bins[:, 0], bins[:, 1])
    exp = []
    for g in range(64):
        grp = bins[16 * g: 16 * g + 16]
        m = np.abs(grp[:, 0]) + np.abs(grp[:, 1])
        exp.append(grp[int(m.argmax())])
    exp = np.array(exp)
    write_pairs(os.path.join(OUT, "decim_exp.hex"), exp[:, 0], exp[:, 1])
    print("vectors written to", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
