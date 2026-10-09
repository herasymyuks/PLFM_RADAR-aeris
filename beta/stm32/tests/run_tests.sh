#!/usr/bin/env bash
# run_tests.sh - build and run the host-side unit tests for the pure-logic parts of the firmware.
# Requirements: a host C/C++ compiler (cc/c++ - Apple clang or GCC), python3. No ARM toolchain needed.
# Exit 0 only if every test passes. Logs go to ../logs/tests_*.log
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB="$HERE/../LIB"
OUT="$HERE/build"
LOGS="$HERE/../logs"
mkdir -p "$OUT" "$LOGS"
rc=0

run() {  # name, command...
  local name="$1"; shift
  echo "== $name"
  if "$@" > "$LOGS/tests_$name.log" 2>&1; then echo "   PASS"; else echo "   FAIL (see logs/tests_$name.log)"; rc=1; fi
  tail -n 1 "$LOGS/tests_$name.log" | sed 's/^/   /'
}

echo "== compile"
c++ -std=c++17 -Wall -Wextra -O1 -I"$LIB" -o "$OUT/test_settings_parser" \
    "$HERE/test_settings_parser.cpp" "$LIB/USBHandler.cpp" "$LIB/RadarSettings.cpp" || rc=1
cc  -std=c11 -Wall -Wextra -O1 -I"$LIB" -o "$OUT/test_beam_matrix" \
    "$HERE/test_beam_matrix.c" "$LIB/aeris_beam.c" || rc=1
cc  -std=gnu11 -Wall -O1 -Wno-format -I"$LIB" -o "$OUT/test_ad9523_regs" \
    "$HERE/test_ad9523_regs.c" "$LIB/ad9523.c" "$LIB/no_os_spi.c" "$LIB/no_os_alloc.c" "$LIB/no_os_mutex.c" || rc=1
cc  -std=c11 -Wall -Wextra -O1 -I"$LIB" -o "$OUT/test_adar_vm_tables" \
    "$HERE/test_adar_vm_tables.c" "$LIB/adar1000_vm_tables.c" "$LIB/aeris_beam.c" -lm || rc=1
cc  -std=c11 -Wall -Wextra -O1 -I"$HERE/../Core/Inc" -o "$OUT/test_host_bridge_cmds" \
    "$HERE/test_host_bridge_cmds.c" "$HERE/../Core/Src/host_bridge_proto.c" || rc=1
[ $rc -ne 0 ] && { echo "COMPILE FAILED"; exit 1; }

run settings_parser "$OUT/test_settings_parser"
run beam_matrix     "$OUT/test_beam_matrix"
run ad9523_regs     "$OUT/test_ad9523_regs"
run adar_vm_tables "$OUT/test_adar_vm_tables"
run host_bridge_cmds "$OUT/test_host_bridge_cmds"
run i2c_timing      python3 -I "$HERE/check_i2c_timing.py"

echo; [ $rc -eq 0 ] && echo "ALL HOST TESTS PASSED" || echo "SOME HOST TESTS FAILED"
exit $rc
