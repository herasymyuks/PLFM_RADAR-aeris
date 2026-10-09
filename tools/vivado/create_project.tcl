# create_project.tcl — AERIS-10 FPGA: create a Vivado project from the repository RTL.
#
# This script DOES NOT choose the FPGA part for you. The repository is contradictory:
#   * 9_Firmware/9_2_FPGA/cntrt.xdc:4 and README.md:52 say XC7A100T (no package/speed given)
#   * 4_Schematics.../MainBoard/RADAR_Main_Board.sch part U42 is XC7A50T-2FTG256I
# You must pass the verified part explicitly, e.g.
#   vivado -mode batch -source tools/vivado/create_project.tcl -tclargs xc7a50tftg256-2
# Known state (2026-10-08): the RTL does not elaborate (see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md,
# section 4) — this script only creates the project so that the Vivado messages can be collected.
# It never edits RTL. Output: build/vivado/aeris10/aeris10.xpr
# Tested: NOT executed in this repository (Vivado is not installed on the authoring machine).

if {[llength $argv] < 1} {
    puts "ERROR: part not given. Usage: vivado -mode batch -source create_project.tcl -tclargs <part> \[<xdc>\]"
    puts "       e.g. -tclargs xc7a50tftg256-2   (schematic U42)   or   xc7a100tftg256-2 (README claim; verify DS180)"
    exit 1
}
set part   [lindex $argv 0]
set root   [file normalize [file join [file dirname [info script]] .. ..]]
set rtl    [file join $root 9_Firmware 9_2_FPGA]
set outdir [file join $root build vivado aeris10]
# Default constraint set: original timing file + schematic-derived candidate pins (unverified).
set xdcs [list [file join $rtl cntrt.xdc] \
               [file join $rtl reconstructed radar_system_top_schematic_derived.xdc]]
if {[llength $argv] >= 2} { set xdcs [list [lindex $argv 1]] }

file mkdir $outdir
create_project -force aeris10 $outdir -part $part

# Synthesisable RTL: every .v except the testbench and the module-less include fragment.
set srcs {}
foreach f [lsort [glob -nocomplain [file join $rtl *.v]]] {
    set b [file tail $f]
    if {$b eq "radar_system_tb.v" || $b eq "chirp_lut_init.v"} { continue }
    lappend srcs $f
}
add_files -norecurse $srcs
# Memory initialisation files ($readmemh in chirp_memory_loader_param.v; seg3 files are MISSING)
add_files -norecurse [glob -nocomplain [file join $rtl *.mem]]
set_property file_type {Memory File} [get_files *.mem]
add_files -fileset constrs_1 -norecurse $xdcs
add_files -fileset sim_1 -norecurse [file join $rtl radar_system_tb.v]
set_property top radar_system_top [current_fileset]
set_property top radar_system_tb  [get_filesets sim_1]
set_property verilog_define {} [current_fileset]
update_compile_order -fileset sources_1
puts "Project created: $outdir/aeris10.xpr (part $part). Next: synth_design -rtl to collect elaboration errors:"
puts "  open_project $outdir/aeris10.xpr; synth_design -rtl -name rtl_1 > build/vivado/elab.log"
