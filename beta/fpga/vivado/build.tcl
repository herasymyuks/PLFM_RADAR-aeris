# build.tcl - synthesis -> implementation -> bitstream for the AERIS-10 beta project.
# NOT EXECUTED in this repository (no Vivado on the authoring machine).
# Usage: vivado -mode batch -source beta/fpga/vivado/build.tcl -tclargs <path/to/aeris10_beta.xpr> [jobs]
# Reports are written next to the project under reports/. Exit code 1 on any failed run,
# 2 when timing is not met (WNS/WHS/THS < 0) - the bitstream is still written in that case
# but MUST NOT be loaded on hardware.
if {[llength $argv] < 1} { puts "ERROR: give the .xpr path"; exit 1 }
set xpr  [lindex $argv 0]
set jobs 4
if {[llength $argv] >= 2} { set jobs [lindex $argv 1] }
open_project $xpr
set rep [file join [file dirname $xpr] reports]
file mkdir $rep

# ---- elaboration check first (catches the missing-IP placeholder modules early) ----
if {[catch {synth_design -rtl -name rtl_1 -top radar_system_top} msg]} {
    puts "ERROR: RTL elaboration failed: $msg"; exit 1
}
report_drc -file [file join $rep rtl_drc.rpt]
close_design

# ---- synthesis ----
reset_run synth_1
launch_runs synth_1 -jobs $jobs
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} { puts "ERROR: synthesis failed"; exit 1 }
open_run synth_1 -name synth_1
report_utilization      -file [file join $rep synth_utilization.rpt]
report_timing_summary   -file [file join $rep synth_timing_summary.rpt] -max_paths 20
report_clock_interaction -file [file join $rep synth_clock_interaction.rpt]
report_cdc              -file [file join $rep synth_cdc.rpt]
report_methodology      -file [file join $rep synth_methodology.rpt]
close_design

# ---- implementation + bitstream ----
reset_run impl_1
launch_runs impl_1 -to_step write_bitstream -jobs $jobs
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} { puts "ERROR: implementation failed"; exit 1 }
open_run impl_1
report_utilization    -file [file join $rep impl_utilization.rpt]
report_timing_summary -file [file join $rep impl_timing_summary.rpt] -max_paths 50
report_power          -file [file join $rep impl_power.rpt]
report_io             -file [file join $rep impl_io.rpt]
set wns [get_property STATS.WNS [get_runs impl_1]]
set whs [get_property STATS.WHS [get_runs impl_1]]
set ths [get_property STATS.THS [get_runs impl_1]]
puts "Implementation done: WNS=$wns WHS=$whs THS=$ths  (reports in $rep)"
if {$wns < 0 || $whs < 0 || $ths < 0} { puts "WARNING: timing NOT met - bitstream is not usable"; exit 2 }
exit 0
