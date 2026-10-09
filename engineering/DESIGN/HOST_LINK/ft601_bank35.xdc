## FT601 32-bit FT245 synchronous FIFO on FPGA bank 35 — PROPOSED (DSN-LINK-01 option A, 2026-10-09)
## Bank 35 VCCO = +3V3_FPGA (schematic); FT601 VCCIO = 3.3 V. Pins chosen from the 50 I/Os of bank 35 that have NO net
## in RADAR_Main_Board.sch; they become real only after the Main Board rev. B routes them (see HOST_LINK_DESIGN.md).
## RTL port names follow 9_Firmware/9_2_FPGA/usb_data_interface.v (ft601_*); BE must be widened to 4 bits (RTL defect).

set_property -dict {PACKAGE_PIN C4 IOSTANDARD LVCMOS33} [get_ports {ft601_clk}]   ;# IO_L12N_T1_MRCC_35
set_property -dict {PACKAGE_PIN A2 IOSTANDARD LVCMOS33} [get_ports {ft601_data[0]}]   ;# IO_L8N_T1_AD14N_35
set_property -dict {PACKAGE_PIN A3 IOSTANDARD LVCMOS33} [get_ports {ft601_data[1]}]   ;# IO_L4N_T0_35
set_property -dict {PACKAGE_PIN A4 IOSTANDARD LVCMOS33} [get_ports {ft601_data[2]}]   ;# IO_L3N_T0_DQS_AD5N_35
set_property -dict {PACKAGE_PIN A5 IOSTANDARD LVCMOS33} [get_ports {ft601_data[3]}]   ;# IO_L3P_T0_DQS_AD5P_35
set_property -dict {PACKAGE_PIN A7 IOSTANDARD LVCMOS33} [get_ports {ft601_data[4]}]   ;# IO_L1N_T0_AD4N_35
set_property -dict {PACKAGE_PIN B1 IOSTANDARD LVCMOS33} [get_ports {ft601_data[5]}]   ;# IO_L9N_T1_DQS_AD7N_35
set_property -dict {PACKAGE_PIN B2 IOSTANDARD LVCMOS33} [get_ports {ft601_data[6]}]   ;# IO_L8P_T1_AD14P_35
set_property -dict {PACKAGE_PIN B4 IOSTANDARD LVCMOS33} [get_ports {ft601_data[7]}]   ;# IO_L4P_T0_35
set_property -dict {PACKAGE_PIN B5 IOSTANDARD LVCMOS33} [get_ports {ft601_data[8]}]   ;# IO_L2N_T0_AD12N_35
set_property -dict {PACKAGE_PIN B6 IOSTANDARD LVCMOS33} [get_ports {ft601_data[9]}]   ;# IO_L2P_T0_AD12P_35
set_property -dict {PACKAGE_PIN B7 IOSTANDARD LVCMOS33} [get_ports {ft601_data[10]}]   ;# IO_L1P_T0_AD4P_35
set_property -dict {PACKAGE_PIN C1 IOSTANDARD LVCMOS33} [get_ports {ft601_data[11]}]   ;# IO_L9P_T1_DQS_AD7P_35
set_property -dict {PACKAGE_PIN C2 IOSTANDARD LVCMOS33} [get_ports {ft601_data[12]}]   ;# IO_L7N_T1_AD6N_35
set_property -dict {PACKAGE_PIN C3 IOSTANDARD LVCMOS33} [get_ports {ft601_data[13]}]   ;# IO_L7P_T1_AD6P_35
set_property -dict {PACKAGE_PIN C6 IOSTANDARD LVCMOS33} [get_ports {ft601_data[14]}]   ;# IO_L5N_T0_AD13N_35
set_property -dict {PACKAGE_PIN C7 IOSTANDARD LVCMOS33} [get_ports {ft601_data[15]}]   ;# IO_L5P_T0_AD13P_35
set_property -dict {PACKAGE_PIN D1 IOSTANDARD LVCMOS33} [get_ports {ft601_data[16]}]   ;# IO_L10N_T1_AD15N_35
set_property -dict {PACKAGE_PIN D3 IOSTANDARD LVCMOS33} [get_ports {ft601_data[17]}]   ;# IO_L11N_T1_SRCC_35
set_property -dict {PACKAGE_PIN D4 IOSTANDARD LVCMOS33} [get_ports {ft601_data[18]}]   ;# IO_L12P_T1_MRCC_35
set_property -dict {PACKAGE_PIN D6 IOSTANDARD LVCMOS33} [get_ports {ft601_data[19]}]   ;# IO_L6P_T0_35
set_property -dict {PACKAGE_PIN E1 IOSTANDARD LVCMOS33} [get_ports {ft601_data[20]}]   ;# IO_L15N_T2_DQS_35
set_property -dict {PACKAGE_PIN E2 IOSTANDARD LVCMOS33} [get_ports {ft601_data[21]}]   ;# IO_L10P_T1_AD15P_35
set_property -dict {PACKAGE_PIN E3 IOSTANDARD LVCMOS33} [get_ports {ft601_data[22]}]   ;# IO_L11P_T1_SRCC_35
set_property -dict {PACKAGE_PIN E5 IOSTANDARD LVCMOS33} [get_ports {ft601_data[23]}]   ;# IO_L13N_T2_MRCC_35
set_property -dict {PACKAGE_PIN E6 IOSTANDARD LVCMOS33} [get_ports {ft601_data[24]}]   ;# IO_0_35
set_property -dict {PACKAGE_PIN F2 IOSTANDARD LVCMOS33} [get_ports {ft601_data[25]}]   ;# IO_L15P_T2_DQS_35
set_property -dict {PACKAGE_PIN F3 IOSTANDARD LVCMOS33} [get_ports {ft601_data[26]}]   ;# IO_L14N_T2_SRCC_35
set_property -dict {PACKAGE_PIN F4 IOSTANDARD LVCMOS33} [get_ports {ft601_data[27]}]   ;# IO_L14P_T2_SRCC_35
set_property -dict {PACKAGE_PIN F5 IOSTANDARD LVCMOS33} [get_ports {ft601_data[28]}]   ;# IO_L13P_T2_MRCC_35
set_property -dict {PACKAGE_PIN G1 IOSTANDARD LVCMOS33} [get_ports {ft601_data[29]}]   ;# IO_L17N_T2_35
set_property -dict {PACKAGE_PIN G2 IOSTANDARD LVCMOS33} [get_ports {ft601_data[30]}]   ;# IO_L17P_T2_35
set_property -dict {PACKAGE_PIN G4 IOSTANDARD LVCMOS33} [get_ports {ft601_data[31]}]   ;# IO_L16N_T2_35
set_property -dict {PACKAGE_PIN G5 IOSTANDARD LVCMOS33} [get_ports {ft601_be[0]}]   ;# IO_L16P_T2_35
set_property -dict {PACKAGE_PIN H1 IOSTANDARD LVCMOS33} [get_ports {ft601_be[1]}]   ;# IO_L20N_T3_35
set_property -dict {PACKAGE_PIN H2 IOSTANDARD LVCMOS33} [get_ports {ft601_be[2]}]   ;# IO_L20P_T3_35
set_property -dict {PACKAGE_PIN H3 IOSTANDARD LVCMOS33} [get_ports {ft601_be[3]}]   ;# IO_L21N_T3_DQS_35
set_property -dict {PACKAGE_PIN H4 IOSTANDARD LVCMOS33} [get_ports {ft601_txe_n}]   ;# IO_L18N_T2_35
set_property -dict {PACKAGE_PIN H5 IOSTANDARD LVCMOS33} [get_ports {ft601_rxf_n}]   ;# IO_L18P_T2_35
set_property -dict {PACKAGE_PIN J1 IOSTANDARD LVCMOS33} [get_ports {ft601_wr_n}]   ;# IO_L22N_T3_35
set_property -dict {PACKAGE_PIN J3 IOSTANDARD LVCMOS33} [get_ports {ft601_rd_n}]   ;# IO_L21P_T3_DQS_35
set_property -dict {PACKAGE_PIN J5 IOSTANDARD LVCMOS33} [get_ports {ft601_oe_n}]   ;# IO_L19P_T3_35
set_property -dict {PACKAGE_PIN K1 IOSTANDARD LVCMOS33} [get_ports {ft601_siwu_n}]   ;# IO_L22P_T3_35
set_property -dict {PACKAGE_PIN K2 IOSTANDARD LVCMOS33} [get_ports {ft601_reset_n}]   ;# IO_L24N_T3_35
set_property -dict {PACKAGE_PIN K3 IOSTANDARD LVCMOS33} [get_ports {ft601_wakeup_n}]   ;# IO_L24P_T3_35
set_property -dict {PACKAGE_PIN K5 IOSTANDARD LVCMOS33} [get_ports {ft601_gpio[0]}]   ;# IO_25_35
set_property -dict {PACKAGE_PIN L2 IOSTANDARD LVCMOS33} [get_ports {ft601_gpio[1]}]   ;# IO_L23N_T3_35

## FT601 drives CLK (100 MHz in 245 synchronous mode, 66 MHz option); data is launched/captured on that clock
create_clock -period 10.000 -name ft601_clk [get_ports ft601_clk]
set_clock_groups -asynchronous -group [get_clocks ft601_clk] -group [get_clocks -include_generated_clocks clk_100m]
## FT601 datasheet AC timing (tsetup/thold vs CLK) MUST be entered here once the datasheet values are confirmed:
# set_input_delay  -clock ft601_clk -max <t_co_max> [get_ports {ft601_data[*] ft601_be[*] ft601_txe_n ft601_rxf_n}]
# set_output_delay -clock ft601_clk -max <t_su>     [get_ports {ft601_data[*] ft601_be[*] ft601_wr_n ft601_rd_n ft601_oe_n}]
set_property SLEW FAST [get_ports {ft601_data[*] ft601_be[*] ft601_wr_n ft601_rd_n ft601_oe_n}]
