#!/usr/bin/env bash
# stm32_check_cube_package.sh — verify that a STM32CubeF7 package tree contains every file the
# AERIS-10 firmware needs (HAL modules enabled in stm32f7xx_hal_conf.h, CMSIS device files,
# startup/linker templates, USB Device Library Core + CDC class). Read-only.
# Usage: tools/stm32_check_cube_package.sh /path/to/STM32Cube_FW_F7_Vx.y.z
# Exit: 0 all found, 1 some missing, 2 bad argument.
set -u
P="${1:-}"
[ -z "$P" ] && { echo "usage: $0 <STM32CubeF7 root>"; exit 2; }
[ -d "$P" ] || { echo "ERROR: not a directory: $P"; exit 2; }
HAL="$P/Drivers/STM32F7xx_HAL_Driver"
CMSIS="$P/Drivers/CMSIS"
USB="$P/Middlewares/ST/STM32_USB_Device_Library"
REQ=(
  "$HAL/Inc/stm32f7xx_hal.h"
  "$HAL/Src/stm32f7xx_hal.c" "$HAL/Src/stm32f7xx_hal_cortex.c" "$HAL/Src/stm32f7xx_hal_rcc.c" "$HAL/Src/stm32f7xx_hal_rcc_ex.c"
  "$HAL/Src/stm32f7xx_hal_gpio.c" "$HAL/Src/stm32f7xx_hal_dma.c" "$HAL/Src/stm32f7xx_hal_dma_ex.c" "$HAL/Src/stm32f7xx_hal_exti.c"
  "$HAL/Src/stm32f7xx_hal_flash.c" "$HAL/Src/stm32f7xx_hal_flash_ex.c" "$HAL/Src/stm32f7xx_hal_pwr.c" "$HAL/Src/stm32f7xx_hal_pwr_ex.c"
  "$HAL/Src/stm32f7xx_hal_i2c.c" "$HAL/Src/stm32f7xx_hal_i2c_ex.c" "$HAL/Src/stm32f7xx_hal_spi.c" "$HAL/Src/stm32f7xx_hal_spi_ex.c"
  "$HAL/Src/stm32f7xx_hal_tim.c" "$HAL/Src/stm32f7xx_hal_tim_ex.c" "$HAL/Src/stm32f7xx_hal_uart.c" "$HAL/Src/stm32f7xx_hal_uart_ex.c"
  "$HAL/Src/stm32f7xx_hal_pcd.c" "$HAL/Src/stm32f7xx_hal_pcd_ex.c" "$HAL/Src/stm32f7xx_ll_usb.c"
  "$CMSIS/Device/ST/STM32F7xx/Include/stm32f7xx.h" "$CMSIS/Device/ST/STM32F7xx/Include/stm32f746xx.h"
  "$CMSIS/Device/ST/STM32F7xx/Include/system_stm32f7xx.h" "$CMSIS/Include/core_cm7.h"
  "$CMSIS/Device/ST/STM32F7xx/Source/Templates/gcc/startup_stm32f746xx.s"
  "$USB/Core/Src/usbd_core.c" "$USB/Core/Src/usbd_ctlreq.c" "$USB/Core/Src/usbd_ioreq.c"
  "$USB/Class/CDC/Src/usbd_cdc.c" "$USB/Class/CDC/Inc/usbd_cdc.h"
)
MISS=0
for f in "${REQ[@]}"; do
  if [ -f "$f" ]; then echo "FOUND   ${f#$P/}"; else echo "MISSING ${f#$P/}"; MISS=$((MISS+1)); fi
done
echo "Package: $P — missing $MISS of ${#REQ[@]} required files"
[ "$MISS" -eq 0 ]
