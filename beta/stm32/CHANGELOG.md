# beta/stm32 — CHANGELOG versus the original sources

Scope: every difference between `beta/stm32/` and `9_Firmware/9_1_Microcontroller/` (originals untouched).
Date 2026-10-09. Author: embedded engineer, BETA bring-up. Line numbers refer to the **original** files
(`CODE` = `9_1_3_C_Cpp_Code`, `LIB` = `9_1_1_C_Cpp_Libraries`).

Category legend: **DEFECT** = fix of code that could not work as written; **HW-TRUTH** = change that
re-aligns the firmware with the schematic/board evidence (each one has an entry in `DECISIONS.md`);
**BUILD** = needed to compile/link; **REFACTOR** = no functional change; **NEW** = file did not exist.

Note on line endings: the originals use CRLF; files rewritten here were saved with LF. `diff -u` therefore
shows whole-file hunks; use `diff -u --strip-trailing-cr` to see the real changes.

## 1. Tree re-arrangement (no content change unless listed below)

| Original | Beta | Category |
|---|---|---|
| `CODE/main.cpp`, `CODE/main.h` | `Core/Src/main.cpp`, `Core/Inc/main.h` (`main.h` byte-identical) | REFACTOR (CubeMX layout) |
| `LIB/stm32f7xx_hal_conf.h`, `LIB/stm32f7xx_it.h` | `Core/Inc/` (`_it.h` identical) | REFACTOR |
| `LIB/stm32f7xx_hal_msp.c`, `LIB/stm32f7xx_it.c`, `LIB/system_stm32f7xx.c`, `LIB/syscalls.c`, `LIB/sysmem.c` | `Core/Src/` (all five byte-identical) | REFACTOR |
| `LIB/ADS7830.H`, `LIB/DAC5578.H` | `LIB/ADS7830.h`, `LIB/DAC5578.h` (content identical) | BUILD — sources include them as `.h` (`LIB/ADS7830.c:1`, `LIB/DA5578.c:1`, `CODE/main.cpp:64-65`); case-sensitive filesystems/CI |
| `LIB/platform_noos_stm32.c/.H` | `LIB/_excluded/` | BUILD — `.c` calls undefined `hal_set_gpio_by_index()` (`:50-58`); no caller of its API; include removed from `main.cpp:53-55` |
| `LIB/errno.h` | `LIB/_excluded/errno.h` | BUILD — ARMCC-only shim; with GCC its `#include_next <errno.h>` (`:94`) re-included itself when reached via `#include "errno.h"` from the same directory (`LIB/no_os_util.c:37`) and `EINVAL` was never defined |
| all other `LIB/*` (116 files) | `LIB/` | copied verbatim; only the files listed in §2 are compiled (`CMakeLists.txt`) |

## 2. Source changes

### Core/Src/main.cpp (from CODE/main.cpp)
| Orig. lines | Change | Category |
|---|---|---|
| 53-55 | removed `extern "C" { #include "platform_noos_stm32.h" }` | BUILD (file excluded) |
| 66 | added `#include "aeris_beam.h"` | REFACTOR |
| 285, 294 | comments: TIM1 tick now 216 MHz / 216 | HW-TRUTH D-02 |
| 317-326 | `degreesTo7BitPhase()` body → calls `aeris_degrees_to_7bit_phase()` (identical arithmetic in `LIB/aeris_beam.c`) | REFACTOR (host-testable) |
| 328-339 | removed dead `extern "C" void CDC_Receive_FS()` (never called: CubeMX `usbd_cdc_if.c` binds its own static function). Added `extern "C" void AERIS_USB_OnReceive(const uint8_t*, uint32_t)` → `usbHandler.processUSBData()`, called from `USB_DEVICE/App/usbd_cdc_if.c` | DEFECT C4 (D-10) |
| 328-339 | added `extern "C" int __io_putchar(int)` → `HAL_UART_Transmit(&huart3, ...)`. `syscalls.c:_write()` calls the weak `__io_putchar`; with no definition every `printf()` (used throughout `adf4382a_manager.c`) would branch to address 0 | DEFECT |
| 380-382 | `systemPowerDownSequence()`: added `EN_DIS_RFPA_VDD` LOW + 10 ms **before** the PA 5 V enables are dropped | HW-TRUTH D-11 |
| 403-406 | `systemPowerDownSequence()`: added `EN_P_5V5_PA` LOW + 10 ms as the last step | HW-TRUTH D-11 |
| 416-439 | `initializeBeamMatrices()` body → `aeris_build_beam_matrices(phase_differences, matrix1, matrix2, vector_0)` | REFACTOR |
| 1037 | `init_param.spi_init.chip_select = 0` → `STM32_SPI_CS_AD9523` (same value 0, now meaningful: PF7) | HW-TRUTH D-05 |
| 1045-1047 | removed `ad9523_init(&init_param); ret = ad9523_setup(&dev, &init_param);` — `ad9523_init()` (`LIB/ad9523.c:344-418`) resets every `pdata` field (all channels → num 0 / divider 0 / LVPECL, PLL1 bypass, N=16), discarding the configuration built in lines 929-1030; the second `ad9523_setup()` at 1058 then ran again and leaked the first device | DEFECT C8/C9 (found by `tests/test_ad9523_regs.c`) |
| 1229 | added `GPS_Init(&huart3);` after `MX_USB_DEVICE_Init()` | DEFECT C6 |
| 1560-1562 | PA bring-up: added `EN_P_5V5_PA` HIGH + 100 ms before `DAC5578_Init()` (VG driver rails were never enabled) | HW-TRUTH D-11 |
| 1600-1601 | added 20 ms settle between the VG DAC/LDAC update and `EN_DIS_RFPA_VDD` HIGH | HW-TRUTH D-11 |
| 1653 | `adc1_readings[channel] = ADS7830_Measure_SingleEnded(&hadc2, ...)` → `adc2_readings[...]` (the value was read into the wrong array and `Idq_reading[channel+8]` used stale `adc2_readings`) | DEFECT U10 |
| 1815 | `PWR_REGULATOR_VOLTAGE_SCALE3` → `SCALE1` | HW-TRUTH D-01 |
| 1824-1827 | PLL `M=25,N=144,P=2,Q=3` → `M=8,N=432,P=2,Q=9`; added `HAL_PWREx_EnableOverDrive()` | HW-TRUTH D-01 |
| 1838-1842 | `APB1 /2, APB2 /1, FLASH_LATENCY_2` → `APB1 /4, APB2 /2, FLASH_LATENCY_7` | HW-TRUTH D-02 |
| 1858-1859 | `PeriphCommonClock_Config()`: added `RCC_PERIPHCLK_CLK48` with `RCC_CLK48SOURCE_PLL` | HW-TRUTH D-01 (USB 48 MHz source made explicit) |
| 1883, 1931, 1979 | I2C1/2/3 `Timing 0x00808CD2` → `0x10916EA0` | HW-TRUTH D-03 |
| 2034, 2074 | SPI1/SPI4 `BaudRatePrescaler _2` → `_16` | HW-TRUTH D-06 |
| 2110 | TIM1 `Prescaler 71` → `215` | HW-TRUTH D-02 |
| 2338-2340 | `MX_GPIO_Init()` USER CODE 2: park `AD9523_CS`, `ADF4382_TX_CS`, `ADF4382_RX_CS`, `ADAR_1..4_CS` HIGH (generated code left them LOW = all slaves selected) | DEFECT C7 (D-05) |

### LIB/USBHandler.cpp, LIB/USBHandler.h
| Orig. lines | Change | Category |
|---|---|---|
| `.cpp` 41 | `for (i = 0; i <= length - 4; ...)` → guard `length < 4` + `i + 4 <= length` (unsigned underflow → out-of-bounds read on short packets) | DEFECT |
| `.cpp` 59-93 | `processSettingsData()` now synchronises on `"SET"` (drops leading bytes, keeps ≤2 possible partial-marker bytes), resets/re-syncs on a rejected packet or on overflow | DEFECT C5 |
| `.h` 40 | added member `bool synced_on_set` | DEFECT C5 |

### LIB/adf4382a_manager.h, LIB/adf4382a_manager.c
| Orig. lines | Change | Category |
|---|---|---|
| `.h` 6 | added `#include "stm32_spi.h"` | BUILD |
| `.h` 8-29 | `TX_*`/`RX_*` pin macros PG0..PG9 → aliases of `main.h` `ADF4382_TX_*`/`ADF4382_RX_*` (PG6..PG15) | HW-TRUTH D-04 (DEFECT C2) |
| `.c` 10, 480 | `set_chip_enable(uint8_t ce_pin, ...)` → `uint16_t` (GPIO_PIN_9/15 do not fit in 8 bits) | DEFECT (consequence of C2) |
| `.c` 40, 49 | `chip_select = TX_CS_Pin/RX_CS_Pin` → `STM32_SPI_CS_ADF4382_TX/RX` (logical index; the 16-bit pin mask was truncated into the `uint8_t` field) | HW-TRUTH D-05 |
| `.c` 42, 51 | `platform_ops = NULL` → `&stm32_spi_ops` | DEFECT C3 |

### LIB/stm32_spi.c, LIB/stm32_spi.h (rewritten)
| Orig. lines | Change | Category |
|---|---|---|
| `.c` 23-26 | `write_and_read(..., uint32_t)` → `uint16_t` to match `no_os_spi_platform_ops` (`LIB/no_os_spi.h:214`); GCC 14 rejects the incompatible pointer | BUILD |
| `.c` 5-21 | `init()`: validates `extra`/`chip_select`, stores `device_id`, `bit_order`, `chip_select`; derives the SPI prescaler from `max_speed_hz` via `stm32_spi_prescaler_for(HAL_RCC_GetPCLK2Freq(), ...)` and re-inits the HAL handle; parks CS high | DEFECT C7 (D-05/D-06) |
| `.c` 23-38 | `write_and_read()`: asserts the CS GPIO low around `HAL_SPI_TransmitReceive()` | DEFECT C7 (D-05) |
| `.h` | added `enum stm32_spi_cs_index` (PF7 / PG14 / PG10 from `main.h`) and `stm32_spi_prescaler_for()` | HW-TRUTH D-05 |

### LIB/ADAR1000_Manager.cpp
| Orig. lines | Change | Category |
|---|---|---|
| 332, 336, 351, 368-370, 436, 446-448, 472-474, 488, 539-541, 545-547, 551, 555 | 22 raw `HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13/14/15, ...)` / `(GPIOG, GPIO_PIN_0/1/2, ...)` → `main.h` macros `EN_P_3V3_ADTR`, `EN_P_3V3_SW`, `EN_P_3V3_VDD_SW`, `EN_P_5V0_PA1/2/3` (same pins; traceable to the schematic nets) | REFACTOR |

### Core/Inc/stm32f7xx_hal_conf.h
| Orig. lines | Change | Category |
|---|---|---|
| 97 | `HSE_VALUE 25000000U` → `8000000U` | HW-TRUTH D-01 |
| 80 | stale commented `/* #define HAL_EXTI_MODULE_ENABLED */` line blanked (the active define at 82 is unchanged) | REFACTOR |

## 3. New files

| Path | Origin | Category |
|---|---|---|
| `USB_DEVICE/Target/usbd_conf.c/.h` | hand-written CubeMX-equivalent, from ST template `Core/Src/usbd_conf_template.c` + reference `cube/Projects/STM32F746ZG-Nucleo/Applications/USB_Device/HID_Standalone/Src/usbd_conf.c` | NEW (D-07, D-08) |
| `USB_DEVICE/App/usb_device.c/.h`, `usbd_desc.c/.h`, `usbd_cdc_if.c/.h` | hand-written CubeMX-equivalent, from ST templates `usbd_desc_template.c`, `usbd_cdc_if_template.c` | NEW (D-09, D-10) |
| `Core/Startup/startup_stm32f746xx.s` | verbatim `cube/Drivers/CMSIS/Device/ST/STM32F7xx/Source/Templates/gcc/startup_stm32f746xx.s` | NEW |
| `STM32F746ZGTx_FLASH.ld` | verbatim `cube/Projects/STM32F746ZG-Nucleo/Templates/SW4STM32/STM32F746ZG_Nucleo_AXIM-FLASH/STM32F746ZGTx_FLASH.ld` | NEW |
| `LIB/aeris_beam.c/.h` | extracted from `CODE/main.cpp:317-443` | REFACTOR |
| `CMakeLists.txt`, `cmake/arm-none-eabi.cmake`, `build.sh`, `setup_cube.sh`, `.gitignore` | new | BUILD (D-13, D-14) |
| `tests/*` | new host unit tests | NEW |
| `README.md`, `DECISIONS.md`, `CUBEMX_SETTINGS.md`, this file | new | docs |
| `cube/` | STM32CubeF7 sparse checkout, pinned commits in `DECISIONS.md` D-15 / `setup_cube.sh` (git-ignored) | third-party |
