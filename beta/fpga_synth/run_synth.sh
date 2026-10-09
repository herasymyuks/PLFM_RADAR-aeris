#!/usr/bin/env bash
# run_synth.sh - open-source synthesis estimate of beta/fpga (Yosys synth_xilinx, xc7).
# Non-destructive: reads beta/fpga/rtl and beta/fpga/mem, writes only beta/fpga_synth/{build,logs,reports}.
# Dependencies: yosys >= 0.40 (tested 0.69+post, Homebrew), python3 (utilisation table).
# Options: REV=<git rev> synthesises that commit (git archive snapshot) instead of the working tree.
#          HIER=1 also runs synth_yosys_hier.ys (per-module breakdown, reports/yosys_stat_hier.txt).
# Exit code: 0 = synthesis completed and stat written, 1 = yosys failed, 98 = tool missing.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FPGA="$HERE/../fpga"
REPO="$(cd "$HERE/../.." && pwd)"
command -v yosys >/dev/null 2>&1 || { echo "ERROR: yosys not found"; exit 98; }
mkdir -p "$HERE/build" "$HERE/logs" "$HERE/reports"
if [ -n "${REV:-}" ]; then
  # synthesise a committed snapshot (git archive) instead of the working tree; the snapshot is
  # extracted under build/src and a symlink makes ../fpga_synth resolve from inside it
  rm -rf "$HERE/build/src"; mkdir -p "$HERE/build/src/beta"
  git -C "$REPO" archive "$REV" beta/fpga | tar -x -C "$HERE/build/src" || { echo "ERROR: git archive $REV failed"; exit 1; }
  ln -s "$HERE" "$HERE/build/src/beta/fpga_synth"
  FPGA="$HERE/build/src/beta/fpga"
  echo "source: git $(git -C "$REPO" rev-parse --short "$REV") (REV=$REV), snapshot in build/src"
else
  echo "source: working tree beta/fpga ($(git -C "$REPO" status --short beta/fpga | wc -l | tr -d ' ') modified/untracked paths)"
fi
cd "$FPGA" || exit 99
# same list as build.sh step 2 (rtl/*.v) minus the simulation-only behavioural FFT
: > "$HERE/build/read_rtl.ys"
for f in rtl/*.v; do
  [ "$f" = rtl/axis_fft_behav.v ] && continue
  # doppler_processor.v: its frame buffer is written inside an async-reset always block; the Yosys
  # frontend would otherwise convert the 2 x 2048 x 16 memory into 65,536 flip-flops (mem2reg),
  # which is a Yosys artefact, not what Vivado infers. -nomem2reg keeps it a memory.
  opt=""; [ "$f" = rtl/doppler_processor.v ] && opt="-nomem2reg"
  echo "read_verilog -defer $opt $f" >> "$HERE/build/read_rtl.ys"
done
echo "yosys: $(yosys -V)"
start=$(date +%s)
yosys -l "$HERE/logs/yosys_synth.log" -q -s "$HERE/synth_yosys.ys" >/dev/null 2>"$HERE/logs/yosys_synth.stderr"
rc=$?
echo "yosys exit=$rc after $(( $(date +%s) - start )) s (log: logs/yosys_synth.log)"
[ $rc -eq 0 ] || { tail -20 "$HERE/logs/yosys_synth.log"; exit 1; }
grep -E '^Warning|Warning:' "$HERE/logs/yosys_synth.log" | sed -E 's/[0-9]+/N/g' | sort | uniq -c | sort -rn > "$HERE/reports/yosys_warnings_summary.txt"
python3 "$HERE/util_table.py" "$HERE/reports/yosys_stat.txt" > "$HERE/reports/utilisation_xc7a50t.md" || exit 1
cat "$HERE/reports/utilisation_xc7a50t.md"
if [ "${HIER:-0}" = 1 ]; then   # optional per-module breakdown (hierarchy kept)
  yosys -l "$HERE/logs/yosys_synth_hier.log" -q -s "$HERE/synth_yosys_hier.ys" >/dev/null 2>&1 || { echo "hierarchical run FAILED"; exit 1; }
  echo "per-module breakdown: reports/yosys_stat_hier.txt"
fi
exit 0
