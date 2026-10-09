#!/usr/bin/env bash
# run_all_checks.sh — runs every AERIS-10 static check and summarises PASS/FAIL.
# Non-destructive. Exit code = number of failed checks (capped at 125).
# Dependencies: bash, python3 (>=3.10). Optional: iverilog, verilator (FPGA checks skipped if absent).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 125
export PYTHONDONTWRITEBYTECODE=1
FAILS=0
run() {  # run <name> <command...>
  local name="$1"; shift
  printf '\n===== %s =====\n' "$name"
  if "$@"; then printf -- '--> %s: PASS\n' "$name"; else printf -- '--> %s: FAIL (exit %d)\n' "$name" "$?"; FAILS=$((FAILS+1)); fi
}
run "repo inventory"          python3 tools/repo_inventory.py --format csv --out /dev/null
run "missing files manifest"  python3 tools/check_missing_files.py --only-missing
run "doc links"               python3 tools/check_doc_links.py
run "FPGA constraints"        python3 tools/check_fpga_constraints.py
run "STM32 includes"          python3 tools/check_stm32_includes.py
run "python imports (ast)"    python3 tools/check_python_imports.py
run "manufacturing files"     python3 tools/check_manufacturing_files.py
run "manufacturing files (incl. generated engineering/PCB)" python3 tools/check_manufacturing_files.py --include-generated
run "schematic connectivity reports" python3 tools/gen_schematic_reports.py
run "drawing register files"  python3 tools/gen_drawing_register.py --check
if [ -d engineering/PCB/RF_PA/reports ]; then run "EAGLE<->KiCad cross-check" python3 tools/gen_engineering_pcb_docs.py; fi
if command -v iverilog >/dev/null 2>&1; then
  run "FPGA iverilog elaboration" bash tools/fpga_lint.sh
else
  printf '\n===== FPGA iverilog elaboration =====\nSKIPPED (iverilog not installed)\n'
fi
printf '\n===== SUMMARY: %d check(s) failed =====\n' "$FAILS"
exit $(( FAILS > 125 ? 125 : FAILS ))
