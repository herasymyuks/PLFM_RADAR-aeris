#!/usr/bin/env bash
# beta_export_package.sh — export the BETA manufacturing/drawing package of one board with kicad-cli 10
# (same export set as tools/kicad_pcb_pipeline.sh, without the EAGLE import step).
# Usage: bash beta/pcb/tools/beta_export_package.sh BOARD      (BOARD ∈ MAIN_BOARD POWER_SUPPLY RF_PA FREQUENCY_SYNTHESIZER)
# Output: beta/pcb/BOARD/exports/{gerber,drill,drawings,svg,mechanical,assembly,ipc,3d,reports}; log in exports/EXPORT_LOG.md
# Exit code: number of failed steps.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
B="$1"; D="$ROOT/beta/pcb/$B"; PCB="$D/$B.kicad_pcb"; O="$D/exports"
KC="${KICAD_CLI:-$HOME/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
[ -f "$PCB" ] || { echo "no board $PCB"; exit 99; }
mkdir -p "$O/gerber" "$O/drill" "$O/drawings" "$O/svg" "$O/assembly" "$O/mechanical" "$O/reports" "$O/3d" "$O/ipc"
LOG="$O/EXPORT_LOG.md"; printf '# Export log — %s (BETA)\n\nkicad-cli %s, %s\n\n| Step | Exit | Command |\n|---|---|---|\n' "$B" "$("$KC" version)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$LOG"
FAIL=0; TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
run() { local step="$1"; shift; "$@" > "$TMP" 2>&1; local rc=$?; [ $rc -ne 0 ] && { FAIL=$((FAIL+1)); echo "FAILED $step"; tail -5 "$TMP"; }; printf '| %s | %s | `%s` |\n' "$step" "$rc" "$(printf '%q ' "$@" | sed "s#$ROOT/##g" | cut -c1-300)" >> "$LOG"; }
CU="$(grep -oE '\(([0-9]+) "(F\.Cu|In[0-9]+\.Cu|B\.Cu)"' "$PCB" | sed -E 's/.*"([^"]+)"/\1/' | tr '\n' ',' | sed 's/,$//')"
run drc "$KC" pcb drc --format report --severity-all --all-track-errors --refill-zones --save-board --units mm -o "$O/reports/DRC_report.txt" "$PCB"
run drc-json "$KC" pcb drc --format json --severity-all --all-track-errors --units mm -o "$O/reports/DRC_report.json" "$PCB"
run stats "$KC" pcb export stats -o "$O/reports/board_statistics.md" "$PCB"
run gerbers "$KC" pcb export gerbers --check-zones --subtract-soldermask -l "$CU,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts,F.Fab,B.Fab" -o "$O/gerber/" "$PCB"
run drill "$KC" pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format pdf --generate-report --report-path "$O/drill/drill_report.txt" -o "$O/drill/" "$PCB"
run pdf-copper "$KC" pcb export pdf --check-zones --mode-multipage --cl Edge.Cuts -l "$CU" --ibt -o "$O/drawings/${B}_copper_layers.pdf" "$PCB"
run pdf-asm-top "$KC" pcb export pdf --mode-single --sp -l "F.Fab,F.SilkS,Edge.Cuts" --ibt --black-and-white -o "$O/drawings/${B}_assembly_top.pdf" "$PCB"
run pdf-asm-bot "$KC" pcb export pdf --mode-single --sp -m -l "B.Fab,B.SilkS,Edge.Cuts" --ibt --black-and-white -o "$O/drawings/${B}_assembly_bottom_mirrored.pdf" "$PCB"
run pdf-top "$KC" pcb export pdf --check-zones --mode-single -l "F.Cu,F.SilkS,Edge.Cuts" --ibt -o "$O/drawings/${B}_top_layer.pdf" "$PCB"
run pdf-bottom "$KC" pcb export pdf --check-zones --mode-single -m -l "B.Cu,B.SilkS,Edge.Cuts" --ibt -o "$O/drawings/${B}_bottom_layer_mirrored.pdf" "$PCB"
run pdf-outline "$KC" pcb export pdf --mode-single -l "Edge.Cuts,Dwgs.User,Cmts.User" --ibt --black-and-white -o "$O/drawings/${B}_outline.pdf" "$PCB"
run svg "$KC" pcb export svg --check-zones --mode-multi --page-size-mode 2 -l "$CU,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts,F.Fab,B.Fab" -o "$O/svg/" "$PCB"
run svg-top "$KC" pcb export svg --check-zones --mode-single --page-size-mode 2 -l "F.Cu,F.SilkS,Edge.Cuts" -o "$O/svg/${B}_top_composite.svg" "$PCB"
run svg-bottom "$KC" pcb export svg --check-zones --mode-single --page-size-mode 2 -m -l "B.Cu,B.SilkS,Edge.Cuts" -o "$O/svg/${B}_bottom_composite_mirrored.svg" "$PCB"
run dxf-outline "$KC" pcb export dxf --mode-single --ou mm --uc -l "Edge.Cuts" -o "$O/mechanical/${B}_outline.dxf" "$PCB"
run dxf-fab "$KC" pcb export dxf --mode-single --ou mm -l "Edge.Cuts,F.Fab,F.SilkS" -o "$O/mechanical/${B}_top_fab.dxf" "$PCB"
run step "$KC" pcb export step --board-only --force -o "$O/mechanical/${B}_board_only.step" "$PCB"
run pos "$KC" pcb export pos --format csv --units mm --side both -o "$O/assembly/${B}_pick_and_place.csv" "$PCB"
run ipc2581 "$KC" pcb export ipc2581 -o "$O/ipc/${B}.xml" "$PCB"
if [ -f "$O/ipc/${B}.xml" ] && [ "$(stat -f %z "$O/ipc/${B}.xml" 2>/dev/null || stat -c %s "$O/ipc/${B}.xml")" -gt 10000000 ]; then run ipc2581-gzip gzip -f -9 "$O/ipc/${B}.xml"; fi
run ipcd356 "$KC" pcb export ipcd356 -o "$O/ipc/${B}_netlist.d356" "$PCB"
run render-top "$KC" pcb render --side top --background opaque --quality high -w 2400 -h 1800 -o "$O/3d/${B}_render_top.png" "$PCB"
run render-bottom "$KC" pcb render --side bottom --background opaque --quality high -w 2400 -h 1800 -o "$O/3d/${B}_render_bottom.png" "$PCB"
run render-iso "$KC" pcb render --side top --rotate "-45,0,30" --perspective --background opaque --quality high -w 2400 -h 1800 -o "$O/3d/${B}_render_isometric.png" "$PCB"
cp "$D/BOM_${B}_beta.csv" "$O/assembly/" 2>/dev/null
echo "$B: failed steps: $FAIL"; exit $FAIL
