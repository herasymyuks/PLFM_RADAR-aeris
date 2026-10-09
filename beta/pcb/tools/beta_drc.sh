#!/usr/bin/env bash
# beta_drc.sh — refill zones and run KiCad DRC on a BETA board; writes text + JSON reports next to the board.
# Usage: bash beta/pcb/tools/beta_drc.sh BOARD.kicad_pcb [REPORT_DIR] [--no-refill]
# Exit: kicad-cli exit code of the text DRC run (0 even with violations; non-zero only on tool failure).
set -u
KC="${KICAD_CLI:-$HOME/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
PCB="$1"; OUT="${2:-$(dirname "$PCB")/reports}"; REFILL="--refill-zones --save-board"
[ "${3:-}" = "--no-refill" ] && REFILL=""
mkdir -p "$OUT"
"$KC" pcb drc --format report --severity-all --all-track-errors $REFILL --units mm -o "$OUT/DRC_report.txt" "$PCB"; rc=$?
"$KC" pcb drc --format json --severity-all --all-track-errors --units mm -o "$OUT/DRC_report.json" "$PCB" >/dev/null 2>&1
python3 -I - "$OUT/DRC_report.json" <<'PY'
import json,sys,collections
d=json.load(open(sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations'])
print('violations:',len(d['violations']),'unconnected:',len(d['unconnected_items']))
print(' '.join('%s=%d'%kv for kv in sorted(c.items())))
PY
exit $rc
