#!/usr/bin/env bash
# build.sh - AERIS-10 beta FPGA project: open-source verification flow.
#
#   1. iverilog elaboration of radar_system_top, simulation view   (-DSIM, behavioural ADC capture)
#   2. iverilog elaboration of radar_system_top, synthesis view    (primitives from rtl/sim/unisim_sim_models.v)
#   3. verilator --lint-only -Wall, synthesis view and simulation view (warnings counted, errors fail)
#   4. python3 gen_chirp_mem.py        (verifies the .mem formula, writes seg3 if absent)
#   5. python3 tb/gen_vectors.py       (numpy reference vectors)
#   6. every testbench in tb/tb_*.v    (iverilog + vvp; a run passes only if it prints "PASS" and not "FAIL")
#      tb_fft_wrappers, tb_matched_filter, tb_range_bin_decimator, tb_host_bridge (unit),
#      tb_host_bridge_top (option B bridge through the top, ~65 s), tb_system_smoke (~65 s)
#
# Exit code = number of failed steps. Logs: beta/fpga/logs/. Never modifies rtl/ or mem/.
# Run from anywhere: paths are resolved relative to this script. $readmemh paths in the RTL are
# relative to beta/fpga, so the script cd's there.
# Dependencies: bash >= 3.2, iverilog >= 11 (tested 13.0), verilator >= 5 (tested 5.052),
#               python3 >= 3.8 with numpy (tested 2.4).
# Options: VERBOSE=1 prints simulator output; SKIP_SYSTEM=1 skips the long system smoke test.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE" || exit 99
LOG=logs
mkdir -p "$LOG"
FAILS=0
TOTAL_WARN=0

RTL=(rtl/*.v)
SIMMODELS=rtl/sim/unisim_sim_models.v
IVFLAGS=(-g2005 -Wall -Wno-timescale -Wno-sensitivity-entire-array)

step() { printf '\n[%s] %s\n' "$1" "$2"; }
result() {   # $1 = exit code, $2 = label, $3 = log
  if [ "$1" -eq 0 ]; then echo "  -> PASS ($3)"; else echo "  -> FAIL exit=$1 ($3)"; FAILS=$((FAILS+1)); head -n 15 "$3" | sed 's/^/     /'; fi
}

for tool in iverilog vvp verilator python3; do
  command -v "$tool" >/dev/null 2>&1 || { echo "ERROR: $tool not found in PATH"; exit 98; }
done
echo "iverilog : $(iverilog -V 2>&1 | head -1)"
echo "verilator: $(verilator --version)"
echo "python3  : $(python3 --version 2>&1) numpy $(python3 -c 'import numpy;print(numpy.__version__)' 2>/dev/null || echo MISSING)"

step 1 "iverilog elaboration, simulation view (-DSIM)"
iverilog "${IVFLAGS[@]}" -DSIM -s radar_system_top -o "$LOG/top_sim.vvp" "${RTL[@]}" "$SIMMODELS" >"$LOG/iverilog_top_sim.log" 2>&1
result $? "iverilog sim view" "$LOG/iverilog_top_sim.log"

step 2 "iverilog elaboration, synthesis view (IBUFDS/IDDR/BUFG from sim models)"
iverilog "${IVFLAGS[@]}" -s radar_system_top -o "$LOG/top_synth.vvp" "${RTL[@]}" "$SIMMODELS" >"$LOG/iverilog_top_synth.log" 2>&1
result $? "iverilog synth view" "$LOG/iverilog_top_synth.log"

for view in synth sim; do
  D=""; [ "$view" = sim ] && D="-DSIM"
  step 3 "verilator --lint-only -Wall, $view view"
  verilator --lint-only -Wall -Wno-fatal $D --top-module radar_system_top "${RTL[@]}" "$SIMMODELS" >"$LOG/verilator_$view.log" 2>&1
  rc=$?
  E=$(grep -c '%Error' "$LOG/verilator_$view.log" || true)
  W=$(grep -c '%Warning' "$LOG/verilator_$view.log" || true)
  TOTAL_WARN=$((TOTAL_WARN+W))
  if [ "$rc" -eq 0 ] && [ "$E" -eq 0 ]; then
    echo "  -> PASS: 0 errors, $W warnings ($LOG/verilator_$view.log)"
    grep '%Warning' "$LOG/verilator_$view.log" | sed 's/%Warning-\([A-Z]*\).*/\1/' | sort | uniq -c | sort -rn | sed 's/^/     /'
  else
    echo "  -> FAIL: $E error lines"; FAILS=$((FAILS+1)); grep '%Error' "$LOG/verilator_$view.log" | head -n 10 | sed 's/^/     /'
  fi
done

step 4 "chirp memory formula check / seg3 generation"
python3 gen_chirp_mem.py >"$LOG/gen_chirp_mem.log" 2>&1
result $? "gen_chirp_mem.py" "$LOG/gen_chirp_mem.log"

step 5 "numpy reference vectors"
python3 tb/gen_vectors.py >"$LOG/gen_vectors.log" 2>&1
result $? "gen_vectors.py" "$LOG/gen_vectors.log"

for tb in tb/tb_*.v; do
  name=$(basename "$tb" .v)
  if [ "${SKIP_SYSTEM:-0}" = 1 ] && [ "$name" = tb_system_smoke ]; then echo; echo "[6] $name skipped (SKIP_SYSTEM=1)"; continue; fi
  step 6 "testbench $name"
  if ! iverilog "${IVFLAGS[@]}" -DSIM -s "$name" -o "$LOG/$name.vvp" "${RTL[@]}" "$SIMMODELS" "$tb" >"$LOG/$name.compile.log" 2>&1; then
    result 1 "$name compile" "$LOG/$name.compile.log"; continue
  fi
  start=$(date +%s)
  vvp -n "$LOG/$name.vvp" >"$LOG/$name.run.log" 2>&1
  rc=$?
  dur=$(( $(date +%s) - start ))
  [ "${VERBOSE:-0}" = 1 ] && cat "$LOG/$name.run.log"
  if [ "$rc" -eq 0 ] && grep -q '^PASS' "$LOG/$name.run.log" && ! grep -q 'FAIL' "$LOG/$name.run.log"; then
    echo "  -> PASS in ${dur}s: $(grep '^PASS' "$LOG/$name.run.log" | head -1)"
  else
    echo "  -> FAIL (exit $rc, ${dur}s) - see $LOG/$name.run.log"; FAILS=$((FAILS+1)); grep -i 'fail\|error' "$LOG/$name.run.log" | head -n 10 | sed 's/^/     /'
  fi
done

echo
echo "================================================================"
echo "beta/fpga build summary: $FAILS failure(s), $TOTAL_WARN verilator warning line(s) (both views)"
echo "================================================================"
exit $FAILS
