# AERIS-10 STM32F746ZGT7 firmware - BETA build (compiles and links; not run on hardware).
#
# Layout (beta/stm32/):
#   Core/Inc, Core/Src, Core/Startup  CubeMX-style application + glue (copied from the originals, edited)
#   LIB/                              copy of 9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries (edited)
#   USB_DEVICE/App, USB_DEVICE/Target hand-written CubeMX-equivalent USB CDC files
#   cube/                             STM32CubeF7 sparse checkout (HAL, CMSIS, USB Device Library)
#   STM32F746ZGTx_FLASH.ld            ST template linker script (AXIM flash, 1 MB / 320 KB)
#
# Configure:  cmake -S beta/stm32 -B beta/stm32/build -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake
# Build:      cmake --build beta/stm32/build        (or: bash beta/stm32/build.sh)
cmake_minimum_required(VERSION 3.20)

if(NOT CMAKE_TOOLCHAIN_FILE)
  set(CMAKE_TOOLCHAIN_FILE ${CMAKE_CURRENT_SOURCE_DIR}/cmake/arm-none-eabi.cmake)
endif()
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

project(aeris10_fw C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(ROOT  ${CMAKE_CURRENT_SOURCE_DIR})
set(CUBE  ${ROOT}/cube)
set(HAL   ${CUBE}/Drivers/STM32F7xx_HAL_Driver)
set(CMSIS ${CUBE}/Drivers/CMSIS)
set(USB   ${CUBE}/Middlewares/ST/STM32_USB_Device_Library)
set(LIB   ${ROOT}/LIB)
set(CORE  ${ROOT}/Core)

foreach(req ${HAL}/Inc/stm32f7xx_hal.h ${CMSIS}/Device/ST/STM32F7xx/Include/stm32f746xx.h
            ${CMSIS}/Include/core_cm7.h ${USB}/Class/CDC/Src/usbd_cdc.c)
  if(NOT EXISTS ${req})
    message(FATAL_ERROR "STM32CubeF7 component missing: ${req}\nRun: bash tools/stm32_check_cube_package.sh beta/stm32/cube (see README.md)")
  endif()
endforeach()

# ---- MCU flags (STM32CubeIDE defaults for STM32F746: Cortex-M7, single-precision FPU, hard ABI) ----
set(MCU_FLAGS -mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=hard)
add_compile_options(${MCU_FLAGS} -ffunction-sections -fdata-sections -fstack-usage
                    -Wall -Wextra -Wno-unused-parameter -Wno-missing-field-initializers
                    $<$<CONFIG:Debug>:-Og>  $<$<CONFIG:Debug>:-g3>
                    $<$<CONFIG:Release>:-Os> $<$<CONFIG:Release>:-g0>)
add_compile_options($<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
                    $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
                    $<$<COMPILE_LANGUAGE:CXX>:-fno-use-cxa-atexit>
                    $<$<COMPILE_LANGUAGE:CXX>:-fno-threadsafe-statics>)
add_compile_definitions(STM32F746xx USE_HAL_DRIVER HSE_VALUE=8000000U)

# ---- Sources ----
set(APP_SRC
  ${CORE}/Src/main.cpp
  ${CORE}/Src/stm32f7xx_hal_msp.c
  ${CORE}/Src/stm32f7xx_it.c
  ${CORE}/Src/system_stm32f7xx.c
  ${CORE}/Src/syscalls.c
  ${CORE}/Src/sysmem.c
  ${CORE}/Startup/startup_stm32f746xx.s
  ${ROOT}/USB_DEVICE/App/usb_device.c
  ${ROOT}/USB_DEVICE/App/usbd_cdc_if.c
  ${ROOT}/USB_DEVICE/App/usbd_desc.c
  ${ROOT}/USB_DEVICE/Target/usbd_conf.c
)
# Application libraries actually referenced from main.cpp (see docs/STM32/STM32_PROJECT_RECONSTRUCTION.md STM-T03).
# Excluded on purpose: platform_noos_stm32.c (undefined hal_set_gpio_by_index, no callers), adar1000.c (unused C
# driver, duplicate of ADAR1000_Manager), iio*.c/iiod.c and the no_os_* files that need networking/IRQ platforms.
set(LIB_SRC
  ${LIB}/USBHandler.cpp ${LIB}/RadarSettings.cpp ${LIB}/ADAR1000_Manager.cpp
  ${LIB}/gps_handler.cpp ${LIB}/TinyGPS++.cpp ${LIB}/BMP180.cpp
  ${LIB}/GY_85_HAL.c ${LIB}/ADS7830.c ${LIB}/DA5578.c
  ${LIB}/ad9523.c ${LIB}/adf4382.c ${LIB}/adf4382a_manager.c
  ${LIB}/stm32_spi.c ${LIB}/stm32_delay.c ${LIB}/aeris_beam.c
  ${LIB}/no_os_spi.c ${LIB}/no_os_util.c ${LIB}/no_os_alloc.c ${LIB}/no_os_mutex.c
)
set(HAL_SRC
  ${HAL}/Src/stm32f7xx_hal.c ${HAL}/Src/stm32f7xx_hal_cortex.c
  ${HAL}/Src/stm32f7xx_hal_rcc.c ${HAL}/Src/stm32f7xx_hal_rcc_ex.c
  ${HAL}/Src/stm32f7xx_hal_gpio.c ${HAL}/Src/stm32f7xx_hal_dma.c ${HAL}/Src/stm32f7xx_hal_dma_ex.c
  ${HAL}/Src/stm32f7xx_hal_exti.c ${HAL}/Src/stm32f7xx_hal_flash.c ${HAL}/Src/stm32f7xx_hal_flash_ex.c
  ${HAL}/Src/stm32f7xx_hal_pwr.c ${HAL}/Src/stm32f7xx_hal_pwr_ex.c
  ${HAL}/Src/stm32f7xx_hal_i2c.c ${HAL}/Src/stm32f7xx_hal_i2c_ex.c
  ${HAL}/Src/stm32f7xx_hal_spi.c ${HAL}/Src/stm32f7xx_hal_spi_ex.c
  ${HAL}/Src/stm32f7xx_hal_tim.c ${HAL}/Src/stm32f7xx_hal_tim_ex.c
  ${HAL}/Src/stm32f7xx_hal_uart.c ${HAL}/Src/stm32f7xx_hal_uart_ex.c
  ${HAL}/Src/stm32f7xx_hal_pcd.c ${HAL}/Src/stm32f7xx_hal_pcd_ex.c ${HAL}/Src/stm32f7xx_ll_usb.c
)
set(USB_SRC
  ${USB}/Core/Src/usbd_core.c ${USB}/Core/Src/usbd_ctlreq.c ${USB}/Core/Src/usbd_ioreq.c
  ${USB}/Class/CDC/Src/usbd_cdc.c
)

add_executable(${PROJECT_NAME} ${APP_SRC} ${LIB_SRC} ${HAL_SRC} ${USB_SRC})

# NOTE: ${LIB} is placed LAST so that the toolchain <errno.h> wins over LIB/errno.h (#include_next shim).
target_include_directories(${PROJECT_NAME} PRIVATE
  ${CORE}/Inc
  ${ROOT}/USB_DEVICE/App ${ROOT}/USB_DEVICE/Target
  ${HAL}/Inc ${HAL}/Inc/Legacy
  ${CMSIS}/Include ${CMSIS}/Device/ST/STM32F7xx/Include
  ${USB}/Core/Inc ${USB}/Class/CDC/Inc
  ${LIB})

# Third-party (HAL/USB/no-OS) warnings are not ours to fix: keep them visible but quieter.
set_source_files_properties(${HAL_SRC} ${USB_SRC} PROPERTIES COMPILE_OPTIONS "-w")

target_link_options(${PROJECT_NAME} PRIVATE
  ${MCU_FLAGS}
  -T${ROOT}/STM32F746ZGTx_FLASH.ld
  --specs=nano.specs
  -Wl,--gc-sections
  -Wl,-Map=${CMAKE_BINARY_DIR}/${PROJECT_NAME}.map,--cref
  -Wl,--print-memory-usage
  -Wl,-u,_printf_float            # nano printf with %f (status strings use %.1f/%.6f)
  -Wl,--no-warn-rwx-segments)
target_link_libraries(${PROJECT_NAME} PRIVATE c m stdc++ nosys)

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
  COMMAND ${CMAKE_SIZE} --format=berkeley $<TARGET_FILE:${PROJECT_NAME}>
  COMMAND ${CMAKE_OBJCOPY} -O ihex   $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.hex
  COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.bin
  COMMENT "Size report and HEX/BIN generation")
