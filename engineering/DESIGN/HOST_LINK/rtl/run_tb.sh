#!/usr/bin/env bash
# Runs the host-bridge self-checking testbench with iverilog; exit 0 only on PASS.
cd "$(dirname "$0")" && iverilog -g2005 -Wall -o /tmp/tb_host_bridge.vvp rd_map_packer.v host_bridge_spi.v tb_host_bridge.v 2>&1 | grep -v "^$" ; vvp /tmp/tb_host_bridge.vvp | tee tb_host_bridge.log | grep -q "^PASS"
