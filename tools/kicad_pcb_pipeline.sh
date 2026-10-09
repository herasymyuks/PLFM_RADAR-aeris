#!/usr/bin/env bash
# kicad_pcb_pipeline.sh — import the EAGLE .brd files into KiCad and export the
# complete manufacturing / drawing package with kicad-cli (KiCad >= 10.0).
#
# Non-destructive: original EAGLE files are only read.  Outputs go to
# engineering/PCB/<BOARD>/ (default) and every command + exit code is appended
# to engineering/VALIDATION/CAD_EXPORT_LOG.md.
#
# Usage:
#   bash tools/kicad_pcb_pipeline.sh [--kicad-cli PATH] [--out DIR] [BOARD ...]
#   BOARD ∈ MAIN_BOARD POWER_SUPPLY RF_PA FREQUENCY_SYNTHESIZER  (default: all)
#
# Dependencies: kicad-cli 10.x (macOS: ~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
#   or /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli; Linux: kicad-cli in PATH), bash 3.2+.
# Exit code: number of failed steps (0 = everything exported).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCH_DIR="$ROOT/4_Schematics and Boards Layout/4_6_Schematics"
OUT_ROOT="$ROOT/engineering/PCB"
LOG="$ROOT/engineering/VALIDATION/CAD_EXPORT_LOG.md"
KC=""
BOARDS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --kicad-cli) KC="$2"; shift 2;;
    --out) OUT_ROOT="$2"; shift 2;;
    -h|--help) sed -n '2,20p' "$0"; exit 0;;
    *) BOARDS+=("$1"); shift;;
  esac
done
if [ -z "$KC" ]; then
  for c in "$HOME/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" \
           "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" "$(command -v kicad-cli || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && { KC="$c"; break; }
  done
fi
if [ -z "$KC" ] || [ ! -x "$KC" ]; then echo "ERROR: kicad-cli not found (use --kicad-cli)"; exit 99; fi
[ ${#BOARDS[@]} -eq 0 ] && BOARDS=(RF_PA FREQUENCY_SYNTHESIZER MAIN_BOARD POWER_SUPPLY)

src_of() {
  case "$1" in
    MAIN_BOARD) echo "$SCH_DIR/MainBoard/RADAR_Main_Board.brd";;
    POWER_SUPPLY) echo "$SCH_DIR/PowerBoard/PowerBoard.brd";;
    RF_PA) echo "$SCH_DIR/PowerAmplifierBoard/RF_PA.brd";;
    FREQUENCY_SYNTHESIZER) echo "$SCH_DIR/FrequencySynthesizerBoard/Clocks_Freq_Synth_board.brd";;
    *) echo "";;
  esac
}

mkdir -p "$(dirname "$LOG")"
if [ ! -f "$LOG" ]; then
  printf '# CAD export log\n\nAppended automatically by `tools/kicad_pcb_pipeline.sh`. Each row: UTC time, board, step, exit code, command.\n\n| Time (UTC) | Board | Step | Exit | Command |\n|---|---|---|---|---|\n' > "$LOG"
fi
FAIL=0
run() { # run <board> <step> <cmd...>
  local board="$1" step="$2"; shift 2
  local ts; ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "[$board] $step"
  "$@" > "$TMP_OUT" 2>&1; local rc=$?
  if [ $rc -ne 0 ]; then FAIL=$((FAIL+1)); echo "   FAILED (exit $rc)"; sed 's/^/   | /' "$TMP_OUT" | tail -15; fi
  local cmd; cmd="$(printf '%q ' "$@" | sed "s#$ROOT/##g; s#$HOME#~#g" | cut -c1-400)"
  printf '| %s | %s | %s | %s | `%s` |\n' "$ts" "$board" "$step" "$rc" "$cmd" >> "$LOG"
  return $rc
}
TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT
KCV="$("$KC" version 2>/dev/null)"
printf '\n_Run %s with kicad-cli %s_\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$KCV" >> "$LOG"

for B in "${BOARDS[@]}"; do
  SRC="$(src_of "$B")"
  if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then echo "ERROR: unknown board or missing source: $B"; FAIL=$((FAIL+1)); continue; fi
  O="$OUT_ROOT/$B"
  mkdir -p "$O/kicad" "$O/gerber" "$O/drill" "$O/drawings" "$O/svg" "$O/assembly" "$O/mechanical" "$O/reports" "$O/3d" "$O/ipc"
  PCB="$O/kicad/$B.kicad_pcb"
  echo "=== $B  ($(basename "$SRC"))"
  # 1 import
  run "$B" import "$KC" pcb import --format eagle --report-format text --report-file "$O/reports/kicad_import_report.txt" -o "$PCB" "$SRC" || continue
  # 1b the CLI importer leaves EAGLE layer 47 "Measures" (package dimension lines) on an UNDEFINED
  #    layer, which makes kicad-cli refuse to load the board; remap them to User.Drawings.
  UNDEF="$(grep -c '(layer "UNDEFINED")' "$PCB" || true)"
  if [ "${UNDEF:-0}" -gt 0 ]; then
    sed -i '' 's/(layer "UNDEFINED")/(layer "Dwgs.User")/' "$PCB" 2>/dev/null || sed -i 's/(layer "UNDEFINED")/(layer "Dwgs.User")/' "$PCB"
    printf '| %s | %s | remap-undefined-layer | 0 | `%s items on EAGLE layer 47 Measures → Dwgs.User` |\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$B" "$UNDEF" >> "$LOG"
    echo "   remapped $UNDEF UNDEFINED-layer items (EAGLE 47 Measures) to Dwgs.User"
  fi
  # 1c project file with the EAGLE DRU design rules (otherwise DRC uses KiCad defaults)
  run "$B" project-from-dru python3 "$ROOT/tools/kicad_project_from_dru.py" "$SRC" "$PCB" --md "$O/reports/design_rules_mapping.md"
  # 2 DRC with zone refill (saves the filled board)
  run "$B" drc "$KC" pcb drc --format report --severity-all --all-track-errors --refill-zones --save-board --units mm -o "$O/reports/DRC_report.txt" "$PCB"
  run "$B" drc-json "$KC" pcb drc --format json --severity-all --units mm -o "$O/reports/DRC_report.json" "$PCB"
  # 3 statistics
  run "$B" stats "$KC" pcb export stats -o "$O/reports/board_statistics.md" "$PCB"
  # copper layer list from the file
  CU="$(grep -oE '\(([0-9]+) "(F\.Cu|In[0-9]+\.Cu|B\.Cu)"' "$PCB" | sed -E 's/.*"([^"]+)"/\1/' | tr '\n' ',' | sed 's/,$//')"
  # 4 gerbers (copper + mask + paste + silk + edge + fab)
  run "$B" gerbers "$KC" pcb export gerbers --check-zones --subtract-soldermask -l "$CU,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts,F.Fab,B.Fab" -o "$O/gerber/" "$PCB"
  # 5 drills (Excellon mm, PTH/NPTH separate, PDF map, report)
  run "$B" drill "$KC" pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format pdf --generate-report --report-path "$O/drill/drill_report.txt" -o "$O/drill/" "$PCB"
  # 6 drawings (PDF): copper per page, assembly top/bottom, outline
  run "$B" pdf-copper "$KC" pcb export pdf --check-zones --mode-multipage --cl Edge.Cuts -l "$CU" --ibt --scale 0 -o "$O/drawings/${B}_copper_layers.pdf" "$PCB"
  run "$B" pdf-asm-top "$KC" pcb export pdf --mode-single --sp -l "F.Fab,F.SilkS,Edge.Cuts" --ibt --scale 0 --black-and-white -o "$O/drawings/${B}_assembly_top.pdf" "$PCB"
  run "$B" pdf-asm-bot "$KC" pcb export pdf --mode-single --sp -m -l "B.Fab,B.SilkS,Edge.Cuts" --ibt --scale 0 --black-and-white -o "$O/drawings/${B}_assembly_bottom_mirrored.pdf" "$PCB"
  run "$B" pdf-top "$KC" pcb export pdf --check-zones --mode-single -l "F.Cu,F.SilkS,Edge.Cuts" --ibt --scale 0 -o "$O/drawings/${B}_top_layer.pdf" "$PCB"
  run "$B" pdf-bottom "$KC" pcb export pdf --check-zones --mode-single -m -l "B.Cu,B.SilkS,Edge.Cuts" --ibt --scale 0 -o "$O/drawings/${B}_bottom_layer_mirrored.pdf" "$PCB"
  run "$B" pdf-outline "$KC" pcb export pdf --mode-single -l "Edge.Cuts,Dwgs.User,Cmts.User" --ibt --scale 0 --black-and-white -o "$O/drawings/${B}_outline.pdf" "$PCB"
  # 7 SVG per layer (board area only)
  run "$B" svg "$KC" pcb export svg --check-zones --mode-multi --page-size-mode 2 -l "$CU,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts,F.Fab,B.Fab" -o "$O/svg/" "$PCB"
  run "$B" svg-top "$KC" pcb export svg --check-zones --mode-single --page-size-mode 2 -l "F.Cu,F.SilkS,Edge.Cuts" -o "$O/svg/${B}_top_composite.svg" "$PCB"
  run "$B" svg-bottom "$KC" pcb export svg --check-zones --mode-single --page-size-mode 2 -m -l "B.Cu,B.SilkS,Edge.Cuts" -o "$O/svg/${B}_bottom_composite_mirrored.svg" "$PCB"
  # 8 mechanical: DXF outline (+holes via Edge.Cuts only), STEP board body, fab layers DXF
  run "$B" dxf-outline "$KC" pcb export dxf --mode-single --ou mm --uc -l "Edge.Cuts" -o "$O/mechanical/${B}_outline.dxf" "$PCB"
  run "$B" dxf-fab "$KC" pcb export dxf --mode-single --ou mm -l "Edge.Cuts,F.Fab,F.SilkS" -o "$O/mechanical/${B}_top_fab.dxf" "$PCB"
  run "$B" step "$KC" pcb export step --board-only --force -o "$O/mechanical/${B}_board_only.step" "$PCB"
  # 9 assembly: pick-and-place (csv, mm, both sides)
  run "$B" pos "$KC" pcb export pos --format csv --units mm --side both -o "$O/assembly/${B}_pick_and_place.csv" "$PCB"
  # 10 IPC data exchange
  run "$B" ipc2581 "$KC" pcb export ipc2581 -o "$O/ipc/${B}.xml" "$PCB"
  # IPC-2581 XML of the large boards is 15-75 MB: store it gzip-compressed (standard, lossless)
  if [ -f "$O/ipc/${B}.xml" ] && [ "$(stat -f %z "$O/ipc/${B}.xml" 2>/dev/null || stat -c %s "$O/ipc/${B}.xml")" -gt 10000000 ]; then
    run "$B" ipc2581-gzip gzip -f -9 "$O/ipc/${B}.xml"
  fi
  run "$B" ipcd356 "$KC" pcb export ipcd356 -o "$O/ipc/${B}_netlist.d356" "$PCB"
  # 11 3D renders
  run "$B" render-top "$KC" pcb render --side top --background opaque --quality high -w 2400 -h 1800 -o "$O/3d/${B}_render_top.png" "$PCB"
  run "$B" render-bottom "$KC" pcb render --side bottom --background opaque --quality high -w 2400 -h 1800 -o "$O/3d/${B}_render_bottom.png" "$PCB"
  run "$B" render-iso "$KC" pcb render --side top --rotate "-45,0,30" --perspective --background opaque --quality high -w 2400 -h 1800 -o "$O/3d/${B}_render_isometric.png" "$PCB"
done
echo "Done. Failed steps: $FAIL"
exit $FAIL
