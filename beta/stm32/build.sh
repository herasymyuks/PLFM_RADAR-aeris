#!/usr/bin/env bash
# build.sh - configure + build the AERIS-10 STM32F746 BETA firmware, report size, export artefacts.
# Exit code 0 only when the link succeeds (warnings are logged to logs/, not fatal).
# Usage: bash beta/stm32/build.sh [Debug|Release]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="${1:-Debug}"
BUILD="$HERE/build"
OUT="$HERE/build_out"
LOGS="$HERE/logs"
mkdir -p "$OUT" "$LOGS"

GCC="$(command -v arm-none-eabi-gcc || true)"
[ -z "$GCC" ] && [ -x "$HOME/opt/arm-gnu-toolchain/bin/arm-none-eabi-gcc" ] && export PATH="$HOME/opt/arm-gnu-toolchain/bin:$PATH"
if ! command -v arm-none-eabi-gcc >/dev/null 2>&1; then
  echo "ERROR: arm-none-eabi-gcc not found (see README.md 'Toolchain')." >&2; exit 2
fi
if [ ! -f "$HERE/cube/Drivers/STM32F7xx_HAL_Driver/Inc/stm32f7xx_hal.h" ]; then
  echo "ERROR: STM32CubeF7 not present in $HERE/cube (see README.md 'STM32CubeF7')." >&2; exit 2
fi
GEN=""; command -v ninja >/dev/null 2>&1 && GEN="-G Ninja"

echo "== toolchain: $(arm-none-eabi-gcc --version | head -1)"
echo "== configure ($CFG)"
cmake -S "$HERE" -B "$BUILD" $GEN -DCMAKE_BUILD_TYPE="$CFG" \
      -DCMAKE_TOOLCHAIN_FILE="$HERE/cmake/arm-none-eabi.cmake" > "$LOGS/cmake_configure.log" 2>&1 \
  || { cat "$LOGS/cmake_configure.log"; echo "CONFIGURE FAILED"; exit 1; }

echo "== build"
cmake --build "$BUILD" 2>&1 | tee "$LOGS/build_full.log"
STATUS=${PIPESTATUS[0]}
grep -E "warning:" "$LOGS/build_full.log" | sort -u > "$LOGS/build_warnings.log" || true
grep -E "error:|undefined reference|ld: " "$LOGS/build_full.log" | sort -u > "$LOGS/build_errors.log" || true
echo "== warnings: $(wc -l < "$LOGS/build_warnings.log" | tr -d ' ') unique (logs/build_warnings.log)"

if [ "$STATUS" -ne 0 ] || [ ! -f "$BUILD/aeris10_fw.elf" ]; then
  echo "BUILD FAILED (status $STATUS) - see $LOGS/build_errors.log"; exit 1
fi

echo "== size"
arm-none-eabi-size --format=berkeley "$BUILD/aeris10_fw.elf" | tee "$LOGS/size.log"
arm-none-eabi-size --format=sysv "$BUILD/aeris10_fw.elf" >> "$LOGS/size.log"

cp "$BUILD/aeris10_fw.elf" "$BUILD/aeris10_fw.hex" "$BUILD/aeris10_fw.bin" "$BUILD/aeris10_fw.map" "$OUT/"
echo "== artefacts in $OUT:"; ls -la "$OUT"
echo "BUILD OK"
exit 0
