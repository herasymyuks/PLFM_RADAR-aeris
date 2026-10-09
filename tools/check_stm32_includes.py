#!/usr/bin/env python3
"""
check_stm32_includes.py — STM32 firmware include-graph and missing-header analyser.

Scans all C/C++ sources under 9_Firmware/9_1_Microcontroller, extracts #include
directives and classifies each header as:
  LOCAL        present in the firmware tree (case-sensitive match; case-insensitive hit is flagged)
  HAL          STM32CubeF7 HAL/LL driver header (stm32f7xx_hal*.h, stm32f7xx_ll*.h)
  CMSIS        core_cm7.h, cmsis_*.h, stm32f7xx.h, stm32f746xx.h, system_stm32f7xx.h
  USB_DEVICE   usb_device.h, usbd_*.h (CubeMX-generated USB Device app + ST middleware)
  ARDUINO      Arduino.h, Wire.h, SPI.h, HardwareSerial.h, Stream.h ...
  LIBC         standard C/C++ headers
  UNKNOWN      none of the above

Non-destructive, read-only.
Usage:
    python3 tools/check_stm32_includes.py [--root PATH] [--json]
Exit codes:
    0  no UNKNOWN headers and no case-mismatch includes
    1  unresolved headers found
    2  firmware directory missing
Dependencies: Python 3.8+ standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

INC_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')
LIBC = {"stdint.h", "stdbool.h", "stdio.h", "stdlib.h", "string.h", "math.h", "errno.h", "stddef.h",
        "stdarg.h", "inttypes.h", "limits.h", "time.h", "ctype.h", "assert.h", "float.h", "signal.h",
        "unistd.h", "sys/types.h", "sys/stat.h", "sys/time.h", "sys/times.h", "sys/unistd.h",
        "stdatomic.h", "cstdint", "cstring", "cmath", "cstdio", "cstdlib", "vector", "string", "map",
        "array", "algorithm", "functional", "memory", "utility", "cstddef", "cerrno", "iostream", "sstream", "fstream", "cstdarg"}
ARDUINO = {"Arduino.h", "Wire.h", "SPI.h", "HardwareSerial.h", "Stream.h", "Print.h", "WString.h",
           "SoftwareSerial.h", "EEPROM.h", "Servo.h", "Stepper.h"}


def classify(inc: str, local_index: dict):
    low = inc.lower()
    base = Path(inc).name
    if inc in local_index:
        return "LOCAL", local_index[inc]
    if low in {k.lower() for k in local_index}:
        real = next(k for k in local_index if k.lower() == low)
        return "LOCAL_CASE_MISMATCH", local_index[real]
    if base in LIBC or inc in LIBC:
        return "LIBC", ""
    if base in ARDUINO:
        return "ARDUINO", ""
    if low.startswith("stm32f7xx_hal") or low.startswith("stm32f7xx_ll"):
        return "HAL", ""
    if low in {"stm32f7xx.h", "stm32f746xx.h", "system_stm32f7xx.h", "core_cm7.h"} or low.startswith("cmsis") or low.startswith("core_"):
        return "CMSIS", ""
    if low.startswith("usb_device") or low.startswith("usbd_"):
        return "USB_DEVICE", ""
    if low.startswith("no_os_") or low.startswith("no-os"):
        return "NO_OS", ""
    return "UNKNOWN", ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    fw = root / "9_Firmware/9_1_Microcontroller"
    if not fw.is_dir():
        print(f"ERROR: firmware dir not found: {fw}", file=sys.stderr)
        return 2
    sources = sorted(p for p in fw.rglob("*") if p.suffix.lower() in {".c", ".cpp", ".h", ".hpp"})
    local_index = {p.name: p.relative_to(root).as_posix() for p in sources}
    graph, missing, case_mismatch = {}, {}, []
    for src in sources:
        rel = src.relative_to(root).as_posix()
        incs = []
        for n, line in enumerate(src.read_text(errors="ignore").splitlines(), 1):
            m = INC_RE.match(line)
            if not m:
                continue
            inc = m.group(1).strip()
            cls, target = classify(inc, local_index)
            incs.append({"line": n, "include": inc, "class": cls, "target": target})
            if cls == "LOCAL_CASE_MISMATCH":
                case_mismatch.append((rel, n, inc, target))
            if cls in ("HAL", "CMSIS", "USB_DEVICE", "ARDUINO", "NO_OS", "UNKNOWN"):
                missing.setdefault(cls, {}).setdefault(inc, []).append(f"{rel}:{n}")
        graph[rel] = incs
    if args.json:
        print(json.dumps({"graph": graph, "missing": missing, "case_mismatch": case_mismatch}, indent=2))
    else:
        print(f"scanned {len(sources)} source files under {fw.relative_to(root)}")
        for cls in ("HAL", "CMSIS", "USB_DEVICE", "ARDUINO", "NO_OS", "UNKNOWN"):
            if cls in missing:
                print(f"\n[{cls}] headers not present in repository ({len(missing[cls])}):")
                for inc, users in sorted(missing[cls].items()):
                    print(f"  {inc:40s} <- {len(users)} file(s): {', '.join(users[:4])}{' ...' if len(users) > 4 else ''}")
        if case_mismatch:
            print(f"\n[CASE MISMATCH] include name differs from file name on disk ({len(case_mismatch)}):")
            for rel, n, inc, target in case_mismatch:
                print(f"  {rel}:{n} includes '{inc}' but file is '{target}'")
    unresolved = sum(len(v) for k, v in missing.items() if k == "UNKNOWN") + len(case_mismatch)
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
