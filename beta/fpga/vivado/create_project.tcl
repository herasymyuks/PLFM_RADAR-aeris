# create_project.tcl - AERIS-10 BETA FPGA project (beta/fpga) for AMD Vivado.
# NOT EXECUTED in this repository (Vivado is not installed on the authoring machine).
#
# Usage:
#   vivado -mode batch -source beta/fpga/vivado/create_project.tcl [-tclargs <part>]
#   default part: xc7a50tftg256-2  (schematic U42 = XC7A50T-2FTG256I; README says XC7A100T -
#   confirm before use, see docs/FPGA/FPGA_PROJECT_RECONSTRUCTION.md section 1)
# Output: beta/fpga/build/vivado/aeris10_beta/aeris10_beta.xpr
#
# File sets
#   sources_1 : rtl/*.v except the behavioural FFT core and (when the IP exists) the two
#               IP-named wrappers; mem/*.mem as Memory Files; ip/<name>/<name>.xci if present
#   constrs_1 : constraints/radar_system_top_beta.xdc
#   sim_1     : rtl/sim/unisim_sim_models.v is NOT added (Vivado has UNISIM); the
#               behavioural FFT files and tb/tb_*.v are added; verilog_define SIM for sim
# The design cannot be synthesised until ip/xfft_32 and ip/FFT_enhanced are generated
# (ip/README.md); without them elaboration stops on the deliberately missing module names
# XFFT_32_IP_NOT_GENERATED__SEE_beta_fpga_ip_README / FFT_ENHANCED_IP_NOT_GENERATED__SEE_beta_fpga_ip_README.

set part "xc7a50tftg256-2"
if {[llength $argv] >= 1} { set part [lindex $argv 0] }
set here   [file normalize [file dirname [info script]]]
set root   [file normalize [file join $here ..]]           ;# beta/fpga
set outdir [file join $root build vivado aeris10_beta]
file mkdir $outdir
create_project -force aeris10_beta $outdir -part $part

set behav_core [file join $root rtl axis_fft_behav.v]
set ip_wrappers [list xfft_32 FFT_enhanced]
set synth_srcs {}
set sim_only   [list $behav_core]
foreach f [lsort [glob -nocomplain [file join $root rtl *.v]]] {
    set b [file rootname [file tail $f]]
    if {$f eq $behav_core} { continue }
    if {[lsearch -exact $ip_wrappers $b] >= 0} {
        set xci [file join $root ip $b $b.xci]
        if {[file exists $xci]} {
            puts "IP found: $xci - $b.v goes to the simulation set only"
            lappend sim_only $f
            import_ip $xci
            continue
        } else {
            puts "WARNING: $xci missing - synthesis will stop on the placeholder module inside $b.v (see ip/README.md)"
        }
    }
    lappend synth_srcs $f
}
add_files -norecurse $synth_srcs
add_files -norecurse [glob -nocomplain [file join $root mem *.mem]]
set_property file_type {Memory File} [get_files *.mem]
add_files -fileset constrs_1 -norecurse [file join $root constraints radar_system_top_beta.xdc]
add_files -fileset sim_1 -norecurse $sim_only
add_files -fileset sim_1 -norecurse [glob -nocomplain [file join $root tb tb_*.v]]
set_property top radar_system_top [current_fileset]
set_property top tb_system_smoke [get_filesets sim_1]
set_property verilog_define {SIM=1} [get_filesets sim_1]
set_property -name {xsim.simulate.runtime} -value {3ms} -objects [get_filesets sim_1]
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
puts "Project created: $outdir/aeris10_beta.xpr (part $part)"
puts "Next: vivado -mode batch -source $here/build.tcl -tclargs $outdir/aeris10_beta.xpr"
