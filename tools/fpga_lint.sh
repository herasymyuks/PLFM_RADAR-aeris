#!/usr/bin/env bash
# fpga_lint.sh — syntax/elaboration check of the AERIS-10 FPGA RTL with open-source tools.
#
# Runs (when installed):
#   1. iverilog -g2012 elaboration of radar_system_top   (all RTL except the testbench and the
#      non-module include fragment chirp_lut_init.v)
#   2. verilator --lint-only on the same file set
#   3. iverilog elaboration of the testbench radar_system_tb (expected to fail: it uses
#      SystemVerilog assertions that Icarus does not support — this is reported, not hidden)
# Logs go to $LOG_DIR (default: ./build/lint under the repo root; override with LOG_DIR=...).
# Never modifies RTL. Exit code: 0 if step 1 AND step 2 succeed, 1 otherwise, 3 if no tool found.
# Dependencies: bash 3.2+ (macOS default), iverilog >= 11 (tested 13.0), verilator >= 5 (tested 5.052) — both optional.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RTL="$ROOT/9_Firmware/9_2_FPGA"
LOG_DIR="${LOG_DIR:-$ROOT/build/lint}"
mkdir -p "$LOG_DIR"
SRC=()
for f in "$RTL"/*.v; do
  case "$(basename "$f")" in radar_system_tb.v|chirp_lut_init.v) ;; *) SRC+=("$f");; esac
done
RC=0; FOUND=0
if command -v iverilog >/dev/null 2>&1; then
  FOUND=1
  echo "[iverilog] $(iverilog -V 2>&1 | head -1)"
  if iverilog -g2012 -I "$RTL" -s radar_system_top -o "$LOG_DIR/radar_system_top.vvp" "${SRC[@]}" >"$LOG_DIR/iverilog_top.log" 2>&1; then
    echo "[iverilog] radar_system_top elaboration: PASS (log: $LOG_DIR/iverilog_top.log)"
  else
    echo "[iverilog] radar_system_top elaboration: FAIL — first lines:"; head -n 15 "$LOG_DIR/iverilog_top.log" | sed 's/^/    /'; RC=1
  fi
  if iverilog -g2012 -I "$RTL" -s radar_system_tb -o "$LOG_DIR/radar_system_tb.vvp" "${SRC[@]}" "$RTL/radar_system_tb.v" >"$LOG_DIR/iverilog_tb.log" 2>&1; then
    echo "[iverilog] radar_system_tb elaboration: PASS"
  else
    echo "[iverilog] radar_system_tb elaboration: FAIL (informational; SVA not supported by Icarus) — see $LOG_DIR/iverilog_tb.log"
  fi
else
  echo "[iverilog] not installed — skipped (brew install icarus-verilog)"
fi
if command -v verilator >/dev/null 2>&1; then
  FOUND=1
  echo "[verilator] $(verilator --version)"
  if verilator --lint-only -Wall -Wno-fatal --top-module radar_system_top -I"$RTL" "${SRC[@]}" >"$LOG_DIR/verilator_lint.log" 2>&1; then
    W=$(grep -c '%Warning' "$LOG_DIR/verilator_lint.log" || true)
    echo "[verilator] lint: PASS with $W warning(s) (log: $LOG_DIR/verilator_lint.log)"
  else
    E=$(grep -c '%Error' "$LOG_DIR/verilator_lint.log" || true)
    echo "[verilator] lint: FAIL with $E error line(s) — first lines:"; grep '%Error' "$LOG_DIR/verilator_lint.log" | head -n 15 | sed 's/^/    /'; RC=1
  fi
else
  echo "[verilator] not installed — skipped (brew install verilator)"
fi
[ "$FOUND" -eq 0 ] && exit 3
exit $RC
