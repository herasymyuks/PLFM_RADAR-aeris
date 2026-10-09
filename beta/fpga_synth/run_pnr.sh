#!/usr/bin/env bash
# run_pnr.sh - OPEN-SOURCE place-and-route trial (nextpnr-xilinx) and optional bitstream
# (prjxray fasm2frames + xc7frames2bit) for beta/fpga. NOT a Vivado flow; results are NOT
# Vivado-verified and the bitstream (if produced) contains FFT pass-through STUBS - never load it
# on the radar hardware.
#
# Prerequisites (paths overridable by environment):
#   run_synth.sh already run (build/read_rtl.ys and, with REV, build/src exist)
#   NEXTPNR  nextpnr-xilinx binary          (openXC7/nextpnr-xilinx bc9b234, built with USE_OPENMP=OFF,
#            plus pnr/nextpnr_placer1_retry_bound.patch: the unpatched SA placer livelocks on this design)
#   CHIPDB   xc7a50t.bin                    (bbaexport.py --device xc7a50tftg256-2 + bbasm)
#   XRAY     prjxray checkout (utils/fasm2frames.py, build/tools/xc7frames2bit)
#   XRAY_DB  prjxray-db/artix7               XRAY_PY  python with fasm + prjxray installed
# Options: PLACER=sa|heap (default sa: heap fails to legalise the DSP cascades, see README),
#          SEED=n (default 1), NOBIT=1 skips the bitstream step.
# Exit: 0 routed (+bitstream unless NOBIT), 1 synthesis, 2 P&R, 3 bitstream, 98 missing tool.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
W=${AERIS_WORK:-$HOME/.cache/aeris10_work}
NEXTPNR=${NEXTPNR:-$W/nextpnr-src/nextpnr-xilinx/build/nextpnr-xilinx}
CHIPDB=${CHIPDB:-$W/nextpnr-src/chipdb/xc7a50t.bin}
XRAY=${XRAY:-$W/prjxray-src}
XRAY_DB=${XRAY_DB:-$W/nextpnr-src/nextpnr-xilinx/xilinx/external/prjxray-db/artix7}
XRAY_PY=${XRAY_PY:-$W/xray-venv/bin/python}
PART=xc7a50tftg256-2
for f in "$NEXTPNR" "$CHIPDB" "$XRAY_PY"; do [ -e "$f" ] || { echo "ERROR: missing $f"; exit 98; }; done
SRC="$HERE/build/src/beta/fpga"; [ -d "$SRC" ] || SRC="$HERE/../fpga"
[ -f "$HERE/build/read_rtl.ys" ] || { echo "ERROR: run run_synth.sh first"; exit 98; }
echo "source: $SRC"
python3 "$HERE/make_pnr_inputs.py" "$SRC/constraints/radar_system_top_beta.xdc" "$SRC/rtl/radar_system_top.v" || exit 1
( cd "$SRC" && yosys -q -l "$HERE/logs/yosys_pnr_netlist.log" -s "$HERE/synth_yosys_pnr.ys" >/dev/null 2>&1 ) || { echo "yosys (P&R netlist) FAILED"; exit 1; }
echo "nextpnr-xilinx ($PLACER placer) ..."
start=$(date +%s)
"$NEXTPNR" --chipdb "$CHIPDB" --xdc "$HERE/pnr/radar_system_top_beta_pnr.xdc" \
  --json "$HERE/build/radar_system_top_beta_pnr.json" --write "$HERE/build/radar_system_top_beta_routed.json" \
  --fasm "$HERE/build/radar_system_top_beta.fasm" --report "$HERE/reports/nextpnr_report.json" \
  --timing-allow-fail --seed "${SEED:-1}" --placer "${PLACER:-sa}" > "$HERE/logs/nextpnr.log" 2>&1
rc=$?
echo "nextpnr exit=$rc after $(( $(date +%s) - start )) s (logs/nextpnr.log)"
grep -v 'has no connections' "$HERE/logs/nextpnr.log" | grep -E 'ERROR|Max frequency for clock' | tail -20
[ $rc -eq 0 ] || exit 2
[ "${NOBIT:-0}" = 1 ] && exit 0
echo "fasm2frames + xc7frames2bit ..."
"$XRAY_PY" "$XRAY/utils/fasm2frames.py" --db-root "$XRAY_DB" --part $PART \
  "$HERE/build/radar_system_top_beta.fasm" "$HERE/build/radar_system_top_beta.frames" > "$HERE/logs/fasm2frames.log" 2>&1 || { echo "fasm2frames FAILED (logs/fasm2frames.log)"; tail -5 "$HERE/logs/fasm2frames.log"; exit 3; }
"$XRAY/build/tools/xc7frames2bit" --part_file "$XRAY_DB/$PART/part.yaml" --part_name $PART \
  --frm_file "$HERE/build/radar_system_top_beta.frames" --output_file "$HERE/build/radar_system_top_beta_OPENSOURCE_STUBFFT.bit" > "$HERE/logs/xc7frames2bit.log" 2>&1 || { echo "xc7frames2bit FAILED"; exit 3; }
ls -l "$HERE/build/radar_system_top_beta_OPENSOURCE_STUBFFT.bit"
exit 0
