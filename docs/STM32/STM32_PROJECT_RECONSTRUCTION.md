# STM32 Firmware Project Reconstruction — AERIS-10 (`9_Firmware/9_1_Microcontroller/`)

Status date: 2026-10-08. Evidence: static inspection of all 136 source files, include-graph analysis (`tools/check_stm32_includes.py`), host-compiler syntax probes, EAGLE schematic netlist (`tools/extract_eagle_netlist.py --part U2`). `LIB` = `9_1_1_C_Cpp_Libraries`, `CODE` = `9_1_3_C_Cpp_Code`. No firmware was compiled for the target (no ARM toolchain on the authoring machine); nothing was flashed or run.

**Bottom line:** the repository contains only application-level sources. There is no CubeMX `.ioc`, no linker script, no startup file, no build system, no CMSIS device header, no STM32CubeF7 HAL driver sources, and no USB Device library or CubeMX USB application files (`usb_device.c`, `usbd_cdc_if.c`, `usbd_conf.c`, `usbd_desc.c`). All of these are obtainable from STMicroelectronics packages or regenerable from CubeMX using the verified settings in section 3, **except** four design conflicts that only the hardware designer can resolve (section 5).

---

## 1. MCU identification

| Evidence | Statement | Source |
|---|---|---|
| Main Board schematic/board | `STM32F746ZGT7`, part U2, LQFP-144 (pad numbers 1..144) | `RADAR_Main_Board.sch` deviceset `STM32F746ZGT7`; `tools/extract_eagle_netlist.py --part U2` → 116 connected pins |
| README | "STM32F746xx" | `README.md:63` |
| Firmware | family-level only (`stm32f7xx_hal.h`); no `STM32F746xx`, no `USE_HAL_DRIVER` define anywhere | `grep -rnE "STM32F7[0-9]{2}xx|USE_HAL_DRIVER" 9_Firmware/9_1_Microcontroller` → 0 hits |
| Peripherals used | OTG_FS (`OTG_FS_IRQHandler`), MPU, DWT → Cortex-M7 | `LIB/stm32f7xx_it.c:204-213`; `CODE/main.cpp:2354-2379, 303` |

**Confirmed:** STM32F746ZGT7 (Cortex-M7, 1 MB flash, 320 KB SRAM, LQFP-144, −40..+105 °C "7" grade) from CAD. **Assumption:** the preprocessor symbol `STM32F746xx` must be supplied by the build system.

---

## 2. Missing build infrastructure (whole repository searched 2026-10-08)

| ID | Artifact | Status | Recovery source |
|---|---|---|---|
| STM-01 | `*.ioc` CubeMX project | MISSING | regenerate (section 4, STM-T02) |
| STM-02 | linker script `STM32F746ZGTX_FLASH.ld` | MISSING | CubeMX/CubeIDE generates; or STM32CubeF7 template |
| STM-03 | `startup_stm32f746zgtx.s` | MISSING | STM32CubeF7 `Drivers/CMSIS/Device/ST/STM32F7xx/Source/Templates/gcc/startup_stm32f746xx.s` |
| STM-04 | `.cproject`/`.project`/Makefile/CMake | MISSING | CubeIDE project or `reconstructed/CMakeLists.txt` (section 7, UNVERIFIED) |
| STM-05..08 | `usb_device.c/.h`, `usbd_cdc_if.c/.h`, `usbd_conf.c/.h`, `usbd_desc.c/.h` | MISSING | CubeMX generates with USB_DEVICE middleware = CDC |
| STM-09 | HAL driver sources `stm32f7xx_hal*.c` | MISSING | STM32CubeF7 `Drivers/STM32F7xx_HAL_Driver` |
| STM-10 | CMSIS `stm32f7xx.h`, `stm32f746xx.h`, `system_stm32f7xx.h`, `core_cm7.h` | MISSING | STM32CubeF7 `Drivers/CMSIS` |
| STM-11 | `Middlewares/ST/STM32_USB_Device_Library` (Core + Class/CDC) | MISSING | STM32CubeF7 |
| STM-12 | USB descriptors (VID/PID/strings) | UNKNOWN | not in repo; the GUI enumerates by bulk endpoints on interface (0,0) without a VID/PID filter for the STM32 (`9_Firmware/9_3_GUI/GUI_V5.py:358-399`) |

Automated check: `python3 tools/check_stm32_includes.py` (executed, exit 1) lists 50 HAL headers, 1 CMSIS header and 2 USB headers that are included but absent, plus 6 case-mismatched includes (section 5, C3).

Present CubeMX-generated files (reusable verbatim): `LIB/stm32f7xx_hal_conf.h`, `LIB/stm32f7xx_hal_msp.c`, `LIB/stm32f7xx_it.c/.h`, `LIB/system_stm32f7xx.c`, `LIB/syscalls.c`, `LIB/sysmem.c`, `CODE/main.h`, `CODE/main.cpp` (CubeMX `main.c` skeleton renamed to `.cpp`; `/* USER CODE */` fences intact).

---

## 3. Verified configuration (reconstructable `.ioc` content)

Everything in this section is read from source and cross-checked against the schematic. Values marked **ASSUMED** are standard CubeIDE defaults not evidenced in the repository.

### 3.1 Clock tree (`CODE/main.cpp:1803-1849`, `LIB/stm32f7xx_hal_conf.h`)

| Item | Value in firmware | Evidence | Schematic |
|---|---|---|---|
| HSE | 25 MHz crystal, `RCC_HSE_ON` | `hal_conf.h:97` `HSE_VALUE=25000000`; `main.cpp:1821` | **XTAL1 = NX3225GD-8MHZ-STD-CRA-3 (8 MHz) on PH0/PH1** — `RADAR_Main_Board.sch` part XTAL1; nets `STM32_OSC_N/P` → U2 pins 23/24 (PH0/PH1) |
| PLL | source HSE, M=25, N=144, P=/2, Q=3 | `main.cpp:1823-1827` | with 8 MHz HSE the PLL input would be 0.32 MHz (below the 0.95 MHz minimum of RM0385) → **CONFLICT C1** |
| SYSCLK / AHB / APB1 / APB2 | 72 / 72 / 36 / 72 MHz (derived for 25 MHz HSE) | `main.cpp:1835-1846`; comments `:285,294` | — |
| USB clock | PLLQ = 48 MHz | PLLQ=3 | — |
| Flash latency | 2 WS | `main.cpp:1846` | — |
| Voltage scale | SCALE3 | `main.cpp:1815` | — |
| LSE | 32.768 kHz crystal present on board, not used by firmware | `hal_conf.h:125`; XTAL3 `NX3215SA-32.768KHz` | PC14/PC15 |
| HSI / LSI | 16 MHz / 32 kHz (defaults) | `hal_conf.h:110,117` | — |
| TIM prescaler | `RCC_TIMPRES_ACTIVATED` | `main.cpp:1852-1866` | — |

### 3.2 Peripherals and pins (`LIB/stm32f7xx_hal_msp.c`, `CODE/main.cpp`, schematic U2 nets)

| Peripheral | Pins / AF (MSP) | Init parameters (`main.cpp`) | Schematic net (U2) | Use |
|---|---|---|---|---|
| I2C1 | PB6 SCL, PB7 SDA, AF4, OD | timing `0x00808CD2` (`:1872-1912`) | `STM32_SCL1/SDA1` | DAC5578 x2 @0x48/0x49 (PA gate bias) |
| I2C2 | PF0 SDA, PF1 SCL, AF4 | `0x00808CD2` (`:1920-1960`) | `STM32_SDA2/SCL2` | ADS7830 x2 @0x48/0x4A (Idq), @0x49 (temps) |
| I2C3 | PA8 SCL, PC9 SDA, AF4 | `0x00808CD2` (`:1968-2008`) | `STM32_SCL3/SDA3` | GY-85 IMU, BMP180 |
| SPI1 | PA5 SCK, PA6 MISO, PA7 MOSI, AF5 | master, 8-bit, CPOL0/CPHA0, soft NSS, **prescaler /2 = 36 MHz** (`:2016-2048`) | `STM32_SCLK1/MISO1/MOSI1` → FPGA J16/G14/H13 and (via FPGA bank 34) ADAR1000 | ADAR1000 x4; CS on PA0..PA3 (`ADAR_1..4_CS_3V3`) |
| SPI4 | PE2 SCK, PE5 MISO, PE6 MOSI, AF5 | identical, /2 (`:2056-2088`) | `STM32_SCLK4/MISO4/MOSI4` → connector to Frequency Synthesizer board | AD9523 (CS PF7), ADF4382 TX/RX (CS PG14/PG10) |
| UART5 | PC12 TX, PD2 RX, AF8 | 9600 8N1 (`:2143-2170`) | `STM32_TX5/RX5` | GPS NMEA |
| USART3 | PB10 TX, PB11 RX, AF7 | 115200 8N1 (`:2178-2205`) | `STM32_TX3/RX3` | debug / `GPS_SendToGUI` text |
| TIM1 | — | PSC 71, ARR 0xFFFE, 1 MHz tick (`:2096-2135`) | — | `delay_us` |
| USB OTG_FS | PA11 DM, PA12 DP (AF10 in missing `usbd_conf.c`), PA10 ID | CDC class (missing files) | `STM32_USB_FS_D_N/D_P/ID` → mini-USB X53 | host link |
| SWD | PA13/PA14, SWO PB3 | — | `STM32_SWDIO/SWCLK/SWO` | debug |
| DMA | **none** configured | `HAL_DMA_MODULE_ENABLED` set but no `hdma` | — | — |
| NVIC | only `OTG_FS_IRQn` handler present (`stm32f7xx_it.c:204-213`); its enable lives in missing `usbd_conf.c` | | | |

### 3.3 GPIO map (`CODE/main.h:62-165`, all confirmed by schematic nets on U2)

| Port.Pin | Macro | Net (schematic) |
|---|---|---|
| PF3..PF10 | `AD9523_PD, _REF_SEL, _SYNC, _RESET, _CS, _STATUS0, _STATUS1, _EEPROM_SEL` | `AD9523_*` |
| PF12..PF15 | `LED_1..LED_4` | `N$52, N$91, N$93, N$94` (LEDs) |
| PA0..PA3 | `ADAR_1..4_CS_3V3` | `ADAR_1..4_CS_3V3` (also to FPGA F14/H16/G16/J15) |
| PG0..PG5 | `EN_P_5V0_PA1, _PA2, _PA3, EN_P_5V5_PA, EN_P_1V8_CLOCK, EN_P_3V3_CLOCK` | `EN_+5V0_PA1..3, EN_+5V5_PA, EN_+1V8_CLOCK, EN_+3V3_CLOCK` |
| PG6..PG10 | `ADF4382_RX_LKDET, _DELADJ, _DELSTR, _CE, _CS` | `ADF4382_RX_*` |
| PG11..PG15 | `ADF4382_TX_LKDET, _DELSTR, _DELADJ, _CS, _CE` | `ADF4382_TX_*` |
| PE7..PE15 | `EN_P_1V0_FPGA, EN_P_1V8_FPGA, EN_P_3V3_FPGA, EN_P_5V0_ADAR, EN_P_3V3_ADAR12, EN_P_3V3_ADAR34, EN_P_3V3_ADTR, EN_P_3V3_SW, EN_P_3V3_VDD_SW` | `EN_+1V0_FPGA ... EN_+3V3_VDD_SW` |
| PC6..PC8 | `MAG_DRDY, ACC_INT, GYR_INT` | same |
| PD4..PD7 | `STEPPER_CW_P, STEPPER_CLK_P, EN_DIS_RFPA_VDD, EN_DIS_COOLING` | `STEPPER_CW+, STEPPER_CLK+, EN/DIS_RFPA_VDD, EN/DIS_COOLING` |
| PB4, PB5, PB8, PB9 | `DAC_1_VG_CLR, DAC_1_VG_LDAC, DAC_2_VG_CLR, DAC_2_VG_LDAC` | same |
| PD8..PD12 (no macro) | FPGA handshake: new chirp, new elevation, new azimuth, mixers enable, FPGA reset | `DIG_0..DIG_4` → FPGA F13/E16/D16/F15/E15 (`main.cpp:448,484,514,1483,1660`) |
| PD13..PD15 | inputs, never read | `DIG_5..7` → FPGA H11/G12/H12 |
| BOOT0 | GND | — |

### 3.4 HAL modules enabled (`LIB/stm32f7xx_hal_conf.h:38-88`)

HAL, SPI, TIM, UART, PCD, GPIO, EXTI, DMA, RCC, FLASH, PWR, I2C, CORTEX. Required driver sources from STM32CubeF7 `Drivers/STM32F7xx_HAL_Driver/Src`: `stm32f7xx_hal.c, _cortex.c, _rcc.c, _rcc_ex.c, _gpio.c, _dma.c, _dma_ex.c, _exti.c, _flash.c, _flash_ex.c, _pwr.c, _pwr_ex.c, _i2c.c, _i2c_ex.c, _spi.c, _spi_ex.c, _tim.c, _tim_ex.c, _uart.c, _uart_ex.c, _pcd.c, _pcd_ex.c, stm32f7xx_ll_usb.c`. Options: `VDD_VALUE 3300`, `TICK_INT_PRIORITY 15`, `USE_RTOS 0`, `PREFETCH_ENABLE 0`, no register callbacks, `USE_FULL_ASSERT` off.

### 3.5 USB CDC middleware requirements

| File | Provides | Required by |
|---|---|---|
| `USB_DEVICE/App/usb_device.c/.h` | `MX_USB_DEVICE_Init()`, `hUsbDeviceFS` | `main.cpp:21,129,1229` |
| `USB_DEVICE/App/usbd_cdc_if.c/.h` | `CDC_Transmit_FS`, `USBD_Interface_fops_FS`, static `CDC_Receive_FS` | `main.cpp:23,1692`; `gps_handler.cpp:118` |
| `USB_DEVICE/App/usbd_desc.c/.h` | VID/PID/strings | enumeration (values unknown) |
| `USB_DEVICE/Target/usbd_conf.c/.h` | `HAL_PCD_MspInit` (PA11/PA12 AF10, NVIC `OTG_FS_IRQn`), `hpcd_USB_OTG_FS` | `stm32f7xx_it.c:58` |
| `Middlewares/ST/STM32_USB_Device_Library/Core`, `Class/CDC` | stack; `USBD_CDC_SetRxBuffer/ReceivePacket` | `main.cpp:336-337` |

**Design defect C4:** `main.cpp:328-339` defines `extern "C" void CDC_Receive_FS(uint8_t*, uint32_t*)`, but the CubeMX-generated `usbd_cdc_if.c` binds its own `static int8_t CDC_Receive_FS` in `USBD_Interface_fops_FS`. The `main.cpp` function is never called; the start-flag wait loop at `main.cpp:1534-1555` can never exit. The USER CODE edit that forwards received bytes to `usbHandler.processUSBData()` is not in the repository.

### 3.6 Memory layout / linker / startup requirements

- Device: 1 MB flash at 0x08000000 (AXIM) / 0x00200000 (ITCM), 320 KB RAM (DTCM 64 KB at 0x20000000, SRAM1 240 KB at 0x20010000, SRAM2 16 KB at 0x2004C000) — **from RM0385, not from repo**.
- `sysmem.c` needs `_end` and `_estack` symbols from the linker script; `syscalls.c` needs newlib (`--specs=nano.specs` ASSUMED).
- `MPU_Config()` (`main.cpp:2354-2379`) configures a background region; no cache enable calls (`SCB_EnableICache/DCache`) — CubeIDE default for F7 is cache off unless ticked (ASSUMED).
- Startup must call `SystemInit()` (`system_stm32f7xx.c`) — standard template.
- C++: `main.cpp` uses `<iostream>`, `<vector>` (`main.cpp:44-45`) → `arm-none-eabi-g++`, libstdc++ (nano or full). `<iostream>` pulls in static-init I/O objects (~ tens of kB flash; ASSUMED not blocking on 1 MB).

---

## 4. Procedures

### STM-T01 — Install toolchain and STM32CubeF7

- **Purpose:** obtain compiler and HAL/CMSIS/USB sources.
- **Prerequisites:** internet access; ~3 GB disk.
- **Software and version:** STM32CubeIDE 1.16+ (bundles GNU Arm 12/13, CubeMX 6.11+, CubeF7 1.17.x) — **version not evidenced in repository**; `hal_conf.h` template © 2017 and generated files © 2025 imply CubeMX ≥ 6.x. Alternative: `brew install --cask gcc-arm-embedded` + `git clone --recursive https://github.com/STMicroelectronics/STM32CubeF7`.
- **Procedure:** install CubeIDE (macOS: download from st.com; needs a free ST account); or install the Arm toolchain and clone STM32CubeF7 to `~/STM32Cube/Repository/STM32Cube_FW_F7_V1.17.x`.
- **Verification:** `arm-none-eabi-gcc --version`; `bash tools/stm32_check_cube_package.sh <path-to-STM32CubeF7>` reports every required file as FOUND.
- **Completion criteria:** script exit 0.

### STM-T02 — Regenerate the CubeMX project

- **Purpose:** recreate `.ioc`, startup, linker script, HAL glue and USB CDC application files.
- **Prerequisites:** STM-T01.
- **Required input files:** section 3 tables; `LIB/stm32f7xx_hal_msp.c`; `CODE/main.cpp`.
- **Procedure (CubeIDE):**
  1. File → New → STM32 Project → MCU selector → `STM32F746ZGTx` → name `aeris10_stm32`, language **C++**, binary Executable, project type STM32Cube.
  2. Pinout & Configuration: set each peripheral exactly as in section 3.2 (I2C1/2/3 with the pin assignments listed; SPI1 and SPI4 full-duplex master, prescaler 2; UART5 9600; USART3 115200; TIM1 internal clock, PSC 71, ARR 65534; USB_OTG_FS mode *Device_Only*; Middleware → USB_DEVICE → Class *Communication Device Class (Virtual Port Com)*). Set the GPIO outputs/inputs of section 3.3 with the macro names as user labels. Set PD8..PD12 output, PD13..PD15 input.
  3. Clock Configuration: HSE input **enter the crystal value decided in C1** (firmware expects 25 MHz; board has 8 MHz). Target HCLK 72 MHz, USB 48 MHz. If 8 MHz is kept: M=4 (2 MHz PFD), N=144, P=2, Q=6 reproduces 72/48 MHz — **this is a proposal, not evidence**; the firmware constants at `main.cpp:1823-1827` must then change.
  4. Project Manager → Code Generator: *Copy only the necessary library files*, *Generate peripheral initialization as a pair of .c/.h files* **unchecked** (the repo's `main.cpp` contains all `MX_*_Init` inline), keep user code on regeneration.
  5. Generate code. The IDE produces `Core/Src/main.c`, `Core/Src/stm32f7xx_hal_msp.c`, `stm32f7xx_it.c`, `system_stm32f7xx.c`, `syscalls.c`, `sysmem.c`, `Core/Startup/startup_stm32f746zgtx.s`, `STM32F746ZGTX_FLASH.ld`, `USB_DEVICE/App/*`, `USB_DEVICE/Target/*`, `Drivers/`, `Middlewares/`.
  6. Replace `Core/Src/main.c` by the repository `CODE/main.cpp` (delete the generated `main.c`), copy `CODE/main.h` over `Core/Inc/main.h`, copy `LIB/stm32f7xx_hal_conf.h`, `stm32f7xx_hal_msp.c`, `stm32f7xx_it.c/.h` over the generated ones (diff first; they must be identical in peripheral content), and add `LIB/` as a source folder with the exclusions of STM-T03.
  7. Diff the generated `usbd_conf.c` NVIC/GPIO code against `stm32f7xx_it.c:204-213` (consistent) and record the VID/PID chosen in `usbd_desc.c` (**unknown original value**).
- **Expected output:** `.ioc` + full project tree.
- **Verification:** generated `stm32f7xx_hal_msp.c` diff against `LIB/stm32f7xx_hal_msp.c` shows only cosmetic differences.
- **Troubleshooting:** CubeMX refuses PLL settings → the 8 MHz vs 25 MHz decision (C1) is unresolved.
- **Completion criteria:** project builds to the first *application* error (STM-T03).

### STM-T03 — Build-set cleanup (source edits requiring review)

| Issue | Evidence | Action |
|---|---|---|
| Uppercase headers `ADS7830.H`, `DAC5578.H`, `platform_noos_stm32.H` included as `.h` | `LIB/ADS7830.c:1`, `LIB/DA5578.c:1`, `LIB/platform_noos_stm32.c:2`, `CODE/main.cpp:54,64,65` | rename files to `.h` (case-sensitive filesystems/CI) |
| `platform_noos_stm32.c` calls undefined `hal_set_gpio_by_index` | `LIB/platform_noos_stm32.c:50-58` | exclude from build (its functions are never called from `main.cpp`) or implement |
| `iio.c`, `iio_app.c`, `iiod.c`, `no_os_*` networking | include `tcp_socket.h`, `lwip_socket.h`, platform headers | exclude `iio*.c`, `iiod.c` from build; they are not used by `main.cpp` |
| `LIB/errno.h` shadows toolchain `<errno.h>` via `#include_next` | `LIB/errno.h:94` | keep `LIB` after system includes, or remove the file (verify with GCC) |
| Two ADAR1000 drivers | `adar1000.c` (no callers) and `ADAR1000_Manager.cpp` (used) | exclude `adar1000.c` or keep (both compile; macros identical) |
| `printf` → `__io_putchar` unimplemented | `LIB/syscalls.c:35,80-88` | retarget to USART3 if debug output is wanted (optional) |
| Defines | `-DSTM32F746xx -DUSE_HAL_DRIVER` | mandatory; `-mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=hard` (**ASSUMED** CubeIDE default for F746) |

### STM-T04 — Fix the blocking firmware defects (designer/firmware-author decisions)

| ID | Defect | Evidence | Resolution options |
|---|---|---|---|
| C1 | HSE 25 MHz (firmware) vs 8 MHz crystal (schematic) | `hal_conf.h:97`, `main.cpp:1823`; XTAL1 NX3225GD-8MHZ | board revision check; change PLLM/Q or crystal |
| C2 | `adf4382a_manager.h:9-28` maps ADF4382 control to PG0..PG9, which `main.h:94-123` assigns to PA/clock power enables; `ADF4382A_Manager_Init` drives `EN_P_5V0_PA1` as TX_CE (`adf4382a_manager.c:83-84,482-483`) and reads lock detect from enable outputs (`:330-331`) | schematic: ADF4382 pins are PG6..PG15 (`main.h:124-157` matches) | make `adf4382a_manager.h` use the `main.h` macros; **safety-relevant** (PA rails toggled out of sequence) |
| C3 | `adf4382a_manager.c:42,51` passes `platform_ops = NULL`; `no_os_spi_init` returns `-EINVAL` (`no_os_spi.c:57-58`) → `Error_Handler()` at `main.cpp:1411-1414` (infinite loop, IRQs off) | | set `platform_ops = &stm32_spi_ops` as done for AD9523 (`main.cpp:1039`) and route CS through PG10/PG14 — the custom `stm32_spi.c:23-38` ignores `chip_select`, so CS handling must be added |
| C4 | USB RX dead (section 3.5) | `main.cpp:328-339` | add USER CODE in `usbd_cdc_if.c` `CDC_Receive_FS` calling a C-linkage shim to `usbHandler.processUSBData(Buf, *Len)` |
| C5 | Start-flag padding: GUI sends flag + 60 zero bytes (`GUI_V5.py:444-446`); `USBHandler.cpp:51-52` forwards the zeros into the settings buffer, then `:70` requires `"SET"` at offset 0 → settings never accepted | | reset `buffer_index` after the flag, or search for `SET` anywhere |
| C6 | `GPS_Init()` never called → `gui_huart == NULL` → `GPS_SendBinaryToGUI` returns early | `gps_handler.cpp:6,65-67` | call `GPS_Init(&huart3)` (or route via USB CDC) |
| C7 | AD9523 CS (PF7) driven low at GPIO init and never toggled; SPI4 runs at 36 MHz although drivers request 10 MHz (`stm32_spi.c:17` stores `max_speed_hz` but never applies it) | `main.cpp:1037,2232-2234` | implement CS and prescaler in `stm32_spi.c`; verify AD9523/ADF4382 SPI max clock in datasheets |

### STM-T05 — Compile, link, size

- **Procedure:** CubeIDE *Project → Build All* (Debug). Or with the reconstructed CMake (section 7): `cmake -S 9_Firmware/9_1_Microcontroller/reconstructed -B build/stm32 -DCMAKE_TOOLCHAIN_FILE=... -DCUBE_F7=<path> && cmake --build build/stm32`.
- **Expected output:** `aeris10_stm32.elf`, `.map`; `arm-none-eabi-size` text+data < 1 048 576 B, bss+data < 327 680 B.
- **Static analysis:** `cppcheck --enable=warning,style --std=c++17 -I LIB -I CODE CODE/main.cpp LIB/*.cpp LIB/USBHandler.cpp` (cppcheck not installed on the authoring machine; command UNVERIFIED).
- **Completion criteria:** zero errors; size within limits; map file archived under `build/stm32/`.

### STM-T06 — Firmware verification (hardware)

1. Flash via SWD (`STM32_Programmer_CLI -c port=SWD -w aeris10_stm32.elf -v -rst`).
2. USART3 at 115200: expect `printf` output only after `__io_putchar` retarget.
3. USB: host enumerates a CDC ACM device (VID/PID as set in `usbd_desc.c`); send `[23,46,158,237]` (4 bytes, unpadded) then the 82-byte settings packet (`SET` + 3 doubles + uint32 + 6 doubles + `END`, big-endian — `RadarSettings.cpp:23-113`); firmware must transmit the status string (`main.cpp:1692`).
4. Power sequencing with a scope on `EN_*` rails: order per `main.cpp:1240-1275, 1485-1489` and `3_Power Management/Power Management V6.xlsx` (clock 1.8 V → 3.3 V → FPGA 1.0 → 1.8 → 3.3 → ADAR 3.3 → ADAR 5.0 → ADTR → PA drain).
5. Note the 180 s OCXO warm-up delay at start (`main.cpp:1237`).

---

## 5. Unresolved-configuration table

| ID | Item | Firmware value | Other evidence | Status |
|---|---|---|---|---|
| U1 | HSE frequency | 25 MHz | schematic 8 MHz | **CONFLICT — REQUIRES BOARD DESIGN VERIFICATION** |
| U2 | ADF4382 control pins | `adf4382a_manager.h` PG0..PG9 | `main.h` + schematic PG6..PG15 | **CONFLICT** (code bug) |
| U3 | USB VID/PID/strings | — | — | UNKNOWN |
| U4 | SPI clock for AD9523/ADF4382/ADAR1000 | 36 MHz actual | drivers request 10 MHz | REQUIRES DATASHEET VERIFICATION |
| U5 | I2C timing `0x00808CD2` at PCLK1 36 MHz | — | — | REQUIRES CubeMX VERIFICATION (bus speed unknown) |
| U6 | Compiler flags / FPU | — | — | ASSUMED CubeIDE defaults |
| U7 | Cache / MPU settings beyond background region | cache not enabled in code | — | ASSUMED off |
| U8 | `STM32_ALGO.docx` (algorithm description) | file is 0 bytes | — | MISSING CONTENT |
| U9 | Interrupt priorities | only SysTick (15) | — | UNVERIFIED (none set for USB in repo) |
| U10 | Idq loop channel mix-up `main.cpp:1650-1652` (reads hadc2 into adc1_readings) | — | — | SUSPECTED BUG, not verified |

---

## 6. Build verification checklist

- [ ] `tools/stm32_check_cube_package.sh <CubeF7>` exit 0
- [ ] `.ioc` regenerated; generated MSP identical in content to `LIB/stm32f7xx_hal_msp.c`
- [ ] Case-mismatch headers renamed; `python3 tools/check_stm32_includes.py` shows 0 CASE MISMATCH
- [ ] C1 decided and PLL constants consistent with the crystal
- [ ] C2, C3, C4, C5, C6, C7 fixed and reviewed
- [ ] `arm-none-eabi-g++` build: 0 errors, warnings reviewed
- [ ] `arm-none-eabi-size` within 1 MB / 320 KB
- [ ] `.elf`/`.map` archived; flashed; CDC enumeration observed; settings accepted (state `READY_FOR_DATA`)

---

## 7. Generated artefacts

| Path | Content | Status |
|---|---|---|
| `tools/check_stm32_includes.py` | include classifier | executed, exit 1 (expected) |
| `tools/stm32_check_cube_package.sh` | verifies a STM32CubeF7 tree has every required file | NOT executed against a package (none on this machine); self-test with a missing path exits 2 |
| `9_Firmware/9_1_Microcontroller/reconstructed/CMakeLists.txt` | source list from this analysis, flags ASSUMED, requires `-DCUBE_F7=<path>` and the CubeMX-generated USB/startup/linker files | NOT built (no toolchain) — UNVERIFIED |
