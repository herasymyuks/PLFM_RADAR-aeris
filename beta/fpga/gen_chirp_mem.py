#!/usr/bin/env python3
"""
gen_chirp_mem.py - regenerate / extend the AERIS-10 long-chirp reference memories.

WHAT THE EXISTING FILES CONTAIN (reverse-engineered 2026-10-09 from
9_Firmware/9_2_FPGA/long_chirp_seg{0,1,2}_{i,q}.mem, see beta/fpga/README.md):

  * They are FREQUENCY-DOMAIN matched-filter coefficients, not time-domain samples.
  * Reference waveform u[n] = exp(j*(a*n^2 + b*n)), n = 0..2999, with
        b = 2*pi*0.10          -> f0 = 10 MHz at 100 MSPS
        a = pi/15000           -> chirp rate k = 1/15000 cycles/sample^2 = +20 MHz over 3000 samples
    i.e. a unit-amplitude linear FM UP-chirp 10 MHz -> 30 MHz, 30 us at 100 MSPS.
    (Fit residual of the unwrapped phase: 0.0018 rad over all 3000 samples.)
  * The 3000 samples are placed in a 3072-sample buffer (zero padded at the end) and cut into
    1024-sample segments s = 0..3 : u_s = buf[1024*s : 1024*s + 1024].
  * mem_s[k] = round( conj( FFT_1024(u_s) )[k] * 0.95 * 32767 / max_k |FFT_1024(u_s)[k]| ),
    stored as 16-bit two's complement, 4 lowercase hex digits per line, CRLF line ends,
    I (real) and Q (imag) in separate files. The 0.95*32767 = 31128 peak is observed in all
    three original files. (conj(FFT(u_s)) is identical to FFT(conj(u_s[-n mod 1024])), so the
    data can equally be read as the spectrum of a 30 -> 10 MHz down-chirp; the designer must
    confirm the TX/RX chirp direction - see README "Open points".)
  * Segment 3 covers samples 3072..4095, entirely outside the 3000-sample chirp -> all zeros.
    This is the file that was missing from the repository (long_chirp_seg3_{i,q}.mem).

Default action: verify the formula against mem/long_chirp_seg{0,1,2}_*.mem (report the max
absolute error in LSB) and write mem/long_chirp_seg3_{i,q}.mem. Existing files are never
overwritten unless --force-regenerate is given (which writes seg0..seg2 as well).

Usage:
  python3 gen_chirp_mem.py                      # verify + write seg3 only (if absent)
  python3 gen_chirp_mem.py --mem-dir mem --time-domain tb/vectors/long_chirp_td.hex
  python3 gen_chirp_mem.py --force-regenerate   # rewrite seg0..3 from the formula
Exit codes: 0 ok (verification error <= TOL), 1 verification failed, 2 I/O error.
Dependencies: Python 3.8+, numpy.
"""
import argparse
import os
import sys

import numpy as np

N_CHIRP = 3000           # samples of the chirp at 100 MSPS (30 us)
SEG_LEN = 1024           # FFT / segment length
N_SEG = 4                # segments loaded by chirp_memory_loader_param.v (addresses 0..4095)
F0 = 0.10                # start frequency, cycles/sample (10 MHz @ 100 MSPS)
K_RATE = 0.20 / N_CHIRP  # cycles/sample^2 (20 MHz sweep over 3000 samples)
PEAK = 0.95 * 32767.0    # observed spectral peak normalisation (31128)
TOL = 2                  # LSB tolerance for the regeneration check


def chirp():
    n = np.arange(N_CHIRP, dtype=float)
    return np.exp(1j * (np.pi * K_RATE * n * n + 2 * np.pi * F0 * n))


def segment_spectrum(seg_index):
    buf = np.zeros(SEG_LEN * N_SEG, dtype=complex)
    buf[:N_CHIRP] = chirp()
    seg = buf[SEG_LEN * seg_index: SEG_LEN * (seg_index + 1)]
    spec = np.conj(np.fft.fft(seg))
    peak = np.abs(spec).max()
    if peak == 0.0:
        return np.zeros(SEG_LEN, dtype=complex)   # segment beyond the chirp -> all zeros
    return spec * (PEAK / peak)


def to_int16(x):
    v = np.round(x).astype(np.int64)
    v = np.clip(v, -32768, 32767)
    return v


def write_mem(path, values):
    with open(path, "wb") as f:
        for v in values:
            f.write(("%04x\r\n" % (int(v) & 0xFFFF)).encode("ascii"))


def read_mem(path):
    out = []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            v = int(s, 16)
            if v >= 0x8000:
                v -= 0x10000
            out.append(v)
    return np.array(out, dtype=np.int64)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mem-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "mem"))
    ap.add_argument("--force-regenerate", action="store_true", help="also (re)write seg0..seg2")
    ap.add_argument("--time-domain", metavar="FILE",
                    help="also write the time-domain reference u[n] (3072 lines, I Q hex pairs, "
                         "scaled by --td-scale) for testbench use")
    ap.add_argument("--td-scale", type=float, default=8000.0, help="amplitude of the time-domain export")
    a = ap.parse_args()

    if not os.path.isdir(a.mem_dir):
        print("ERROR: mem dir not found: %s" % a.mem_dir)
        return 2
    rc = 0
    for s in range(N_SEG):
        spec = segment_spectrum(s)
        i_new, q_new = to_int16(spec.real), to_int16(spec.imag)
        fi = os.path.join(a.mem_dir, "long_chirp_seg%d_i.mem" % s)
        fq = os.path.join(a.mem_dir, "long_chirp_seg%d_q.mem" % s)
        exists = os.path.exists(fi) and os.path.exists(fq)
        if exists and not a.force_regenerate:
            i_old, q_old = read_mem(fi), read_mem(fq)
            if len(i_old) != SEG_LEN or len(q_old) != SEG_LEN:
                print("seg%d: FAIL length %d/%d (expected %d)" % (s, len(i_old), len(q_old), SEG_LEN))
                rc = 1
                continue
            ei = int(np.abs(i_old - i_new).max())
            eq = int(np.abs(q_old - q_new).max())
            status = "OK" if max(ei, eq) <= TOL else "FAIL"
            if status == "FAIL":
                rc = 1
            print("seg%d: existing file vs formula: max |dI|=%d LSB, max |dQ|=%d LSB, peak=%d -> %s"
                  % (s, ei, eq, int(np.abs(i_old + 1j * q_old).max()), status))
        else:
            write_mem(fi, i_new)
            write_mem(fq, q_new)
            print("seg%d: written %s, %s (%d lines each, all-zero=%s)"
                  % (s, fi, fq, SEG_LEN, bool(np.all(i_new == 0) and np.all(q_new == 0))))

    if a.time_domain:
        u = chirp() * a.td_scale
        buf = np.zeros(SEG_LEN * (N_SEG - 1), dtype=complex)   # 3072 samples
        buf[:N_CHIRP] = u
        with open(a.time_domain, "w") as f:
            for z in buf:
                f.write("%04x %04x\n" % (int(np.round(z.real)) & 0xFFFF, int(np.round(z.imag)) & 0xFFFF))
        print("time-domain reference written: %s (%d lines, amplitude %.0f)" % (a.time_domain, len(buf), a.td_scale))
    return rc


if __name__ == "__main__":
    sys.exit(main())
