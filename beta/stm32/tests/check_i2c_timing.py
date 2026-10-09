#!/usr/bin/env python3
"""
check_i2c_timing.py - decode STM32F7 I2C TIMINGR values and check the resulting bus timing.

Why: the BETA clock tree moves PCLK1 from 36 MHz (original firmware intent) to 54 MHz,
so the CubeMX-generated TIMINGR 0x00808CD2 is no longer valid. This script shows that
  * 0x00808CD2 @ 36 MHz is a ~100 kHz Standard-mode setting (so the original intent was 100 kHz), and
  * 0x10916EA0 @ 54 MHz (BETA value, computed here - NOT a CubeMX output) is <=100 kHz Standard-mode
    and meets the I2C spec minima (tLOW, tHIGH, tSU;DAT).
Model (RM0385 §30.4.9, Table 'I2C timings'): tI2CCLK = 1/fI2CCLK (I2C kernel clock = PCLK1 here),
tPRESC = (PRESC+1) x tI2CCLK, tSCLL = (SCLL+1) x tPRESC, tSCLH = (SCLH+1) x tPRESC,
tSYNC1/tSYNC2 ~ tAF(min 50 ns) + 2 x tI2CCLK each (analog filter on, digital filter 0),
tSDADEL = SDADEL x tPRESC, tSCLDEL = (SCLDEL+1) x tPRESC.
Standard mode minima: tLOW >= 4.7 us, tHIGH >= 4.0 us, tSU;DAT >= 250 ns, tHD;DAT >= 0.
Exit 0 when every candidate passes.
"""
import sys

CASES = [
    # (TIMINGR, fPCLK1 Hz, label)
    (0x00808CD2, 36_000_000, "original firmware (main.cpp) at 36 MHz PCLK1"),
    (0x10916EA0, 54_000_000, "BETA value at 54 MHz PCLK1 (216 MHz tree)"),
]

def decode(timingr, fclk):
    presc = (timingr >> 28) & 0xF
    scldel = (timingr >> 20) & 0xF
    sdadel = (timingr >> 16) & 0xF
    sclh = (timingr >> 8) & 0xFF
    scll = timingr & 0xFF
    t_i2cclk = 1.0 / fclk
    t_presc = (presc + 1) * t_i2cclk
    t_af = 50e-9
    t_sync = 2 * (t_af + 2 * t_i2cclk)
    t_low = (scll + 1) * t_presc + t_sync / 2
    t_high = (sclh + 1) * t_presc + t_sync / 2
    t_scl = t_low + t_high
    return dict(presc=presc, scldel=scldel, sdadel=sdadel, sclh=sclh, scll=scll,
                t_low=t_low, t_high=t_high, f_scl=1.0 / t_scl,
                t_sdadel=sdadel * t_presc, t_scldel=(scldel + 1) * t_presc)

def main():
    ok = True
    for timingr, fclk, label in CASES:
        d = decode(timingr, fclk)
        passed = d["t_low"] >= 4.7e-6 and d["t_high"] >= 4.0e-6 and 90e3 <= d["f_scl"] <= 101e3 and d["t_scldel"] >= 250e-9
        ok &= passed
        print(f"{label}: TIMINGR=0x{timingr:08X} PRESC={d['presc']} SCLDEL={d['scldel']} SDADEL={d['sdadel']} "
              f"SCLH={d['sclh']} SCLL={d['scll']}")
        print(f"   tLOW={d['t_low']*1e6:.3f} us (>=4.7)  tHIGH={d['t_high']*1e6:.3f} us (>=4.0)  "
              f"fSCL~{d['f_scl']/1e3:.1f} kHz  tSCLDEL={d['t_scldel']*1e9:.0f} ns  tSDADEL={d['t_sdadel']*1e9:.0f} ns  -> {'PASS' if passed else 'FAIL'}")
    print("I2C TIMING CHECK", "PASSED" if ok else "FAILED")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
