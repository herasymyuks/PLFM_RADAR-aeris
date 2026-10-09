#!/usr/bin/env bash
# setup_cube.sh - reproduce the pinned STM32CubeF7 sparse checkout used by the BETA build (DECISIONS.md D-15).
# Non-destructive: refuses to touch an existing cube/ unless --force is given.
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUBE="$HERE/cube"
CUBE_COMMIT=79165e260557395e1c28f5a0ba93cb731aa48f17
if [ -d "$CUBE" ] && [ "${1:-}" != "--force" ]; then
  echo "cube/ already exists; run with --force to re-create it"; exit 0
fi
rm -rf "$CUBE"
git clone --filter=blob:none --sparse https://github.com/STMicroelectronics/STM32CubeF7.git "$CUBE"
cd "$CUBE"
git checkout --quiet "$CUBE_COMMIT"
git sparse-checkout set --skip-checks Drivers/CMSIS Drivers/STM32F7xx_HAL_Driver \
    Middlewares/ST/STM32_USB_Device_Library Projects/STM32F746ZG-Nucleo/Templates \
    Projects/STM32F746ZG-Nucleo/Applications/USB_Device
git submodule update --init --depth 1 -- Drivers/STM32F7xx_HAL_Driver Drivers/CMSIS/Device/ST/STM32F7xx \
    Middlewares/ST/STM32_USB_Device_Library
echo "--- pinned submodule commits (expected: e860c4ff..., 2352e888..., 2a0a3521...) ---"
git submodule status -- Drivers/STM32F7xx_HAL_Driver Drivers/CMSIS/Device/ST/STM32F7xx Middlewares/ST/STM32_USB_Device_Library
bash "$HERE/../../tools/stm32_check_cube_package.sh" "$CUBE"
