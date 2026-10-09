# STM32F746 Firmware Architecture - evidence note for SD-03 and SD-04

Project AERIS-10 | Revision A | Date 2026-10-09 | Status: PARTIAL (HAL / CubeMX / USB middleware absent from repository)

Native diagrams: `stm32_firmware_architecture.dot` (SD-03), `stm32_usb_cdc_flow.dot` (SD-04). Exports: `.svg`, `.pdf`, `.png` next to each `.dot`.
Path abbreviations: `CODE/` = `9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/`, `LIB/` = `9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/`.

## 1. What the firmware is

`CODE/main.cpp` (2411 lines) is a CubeMX-style `main.c` renamed to C++ (it uses `<iostream>`, `<vector>`, classes). It owns every peripheral handle (`CODE/main.cpp:108-118`), all `MX_*_Init` functions (`:1872-2330`), the clock tree (`SystemClock_Config` `:1803-1849`, HSE 25 MHz, PLL M=25 N=144 P=2 Q=3) and the whole application sequence inside `main()` (`:1200-1800`). Drivers live in `LIB/` as three families:

| Family | Files | Transport | Evidence |
|---|---|---|---|
| C++ board classes | `ADAR1000_Manager.cpp/.h`, `USBHandler.cpp/.h`, `RadarSettings.cpp/.h`, `BMP180.cpp/.h`, `gps_handler.cpp/.h`, `TinyGPS++.cpp` | HAL directly (`hspi1`, `huart3`, `hi2c3`), CDC | `ADAR1000_Manager.cpp:8-9,619-621`; `BMP180.cpp:405-409`; `gps_handler.cpp:60,118` |
| ADI no-OS drivers + core | `ad9523.c/.h`, `adf4382.c/.h`, `adf4382a_manager.c/.h`, `adar1000.c/.h`, `no_os_*.c/.h` (60 files), `iio*.c/.h` | `no_os_spi` -> `platform_ops` -> `stm32_spi.c` -> `hspi4` | `CODE/main.cpp:1039-1040`; `adf4382a_manager.c:42-43,51-52` |
| C HAL sensor drivers | `DA5578.c`/`DAC5578.H`, `ADS7830.c/.H`, `GY_85_HAL.c/.h` | HAL I2C (`hi2c1`, `hi2c2`, `hi2c3`) | `DA5578.c:69`; `ADS7830.c:111-121`; `GY_85_HAL.c:35-116`; handles passed at `CODE/main.cpp:1563,1570,1605,1611,1670` |

Peripheral-to-device map (from `LIB/stm32f7xx_hal_msp.c` pin setup and the call sites above): I2C1 PB6/PB7 -> 2x DAC5578 (PA gate bias); I2C2 PF0/PF1 -> 3x ADS7830 (Idq sense, temperatures); I2C3 PA8/PC9 -> GY-85 + BMP180; SPI1 PA5/PA6/PA7 + CS PA0..PA3 -> ADAR1000 x4 through the FPGA level shift; SPI4 PE2/PE5/PE6 -> AD9523 (CS PF7) and ADF4382 TX/RX (CS PG14/PG10); UART5 PC12/PD2 -> GPS NMEA (`CODE/main.cpp:908-909`); USART3 PB10/PB11 -> debug text; TIM1 -> `delay_us()` (`CODE/main.cpp:292-295`); GPIO PD8..PD12 -> FPGA handshake (`:448,484,514,1483,1660`); USB OTG_FS -> host CDC.

## 2. What is missing (dashed red in SD-03/SD-04)

Searched on 2026-10-09 (`find 9_Firmware -name ...`): no `stm32f7xx_hal.h`, no `STM32F7xx_HAL_Driver/`, no CMSIS device header, no `startup_stm32f746xx.s`, no linker script, no `.ioc`, no `usb_device.c/.h`, `usbd_cdc_if.c/.h`, `usbd_desc.c/.h`, `usbd_conf.c/.h`, no `STM32_USB_Device_Library`. The repo does contain the CubeMX glue that references them: `LIB/stm32f7xx_hal_conf.h`, `LIB/stm32f7xx_hal_msp.c`, `LIB/stm32f7xx_it.c` (`:58` `extern PCD_HandleTypeDef hpcd_USB_OTG_FS`, `:204-209` `OTG_FS_IRQHandler`), `LIB/system_stm32f7xx.c`, `LIB/syscalls.c`, `LIB/sysmem.c`. Recovery procedure: `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` STM-T01..T03.

## 3. USB CDC path and its defects (SD-04)

| Step | Where | Evidence | Status |
|---|---|---|---|
| GUI sends start flag `[23,46,158,237]` | `9_Firmware/9_3_GUI/GUI_V5.py:401-405` | bytes literal `:403` | consistent with firmware `LIB/USBHandler.cpp:38` |
| GUI zero-pads every chunk to 64 B | `GUI_V5.py:434-452` (`:444-446`) | `chunk += b'\x00' * (64 - len)` | **C5** - firmware forwards the padding into the settings buffer (`USBHandler.cpp:51-52`) and then demands `"SET"` at offset 0 (`:70`) |
| GUI sends 82-B settings `SET`+3 double+uint32+6 double+`END` (big-endian) | `GUI_V5.py:454-468` | `struct.pack('>d' / '>I')` | parsed by `RadarSettings::parseFromUSB` (`LIB/RadarSettings.h:12`, called `USBHandler.cpp:78`) |
| USB OTG_FS interrupt | `LIB/stm32f7xx_it.c:204-209` | `HAL_PCD_IRQHandler(&hpcd_USB_OTG_FS)` | handle defined in missing `usbd_conf.c` |
| CDC receive callback | `CODE/main.cpp:328-339`: `extern "C" { void CDC_Receive_FS(uint8_t* Buf, uint32_t *Len) {...} }` | `grep -rn CDC_Receive_FS 9_Firmware/` -> this one definition only (verified 2026-10-09); the CubeMX `usbd_cdc_if.c` template registers its **own** `static int8_t CDC_Receive_FS` in `USBD_Interface_fops_FS` | **C4** - the application callback is never bound; `usbHandler.processUSBData()` (`:333`) is never reached |
| Application wait loop | `CODE/main.cpp:1534-1555` `do { ... } while (!usbHandler.isStartFlagReceived());` | settings getters commented out `:1540-1550` | never exits under C4; settings are never applied even if it did |
| Firmware -> host | `CDC_Transmit_FS(initial_status)` `CODE/main.cpp:1692`; `GPS_SendBinaryToGUI` -> `CDC_Transmit_FS` `LIB/gps_handler.cpp:118` | `gui_huart == NULL` guard `:67`; `GPS_Init()` has no caller | **C6** - GPS packet never sent |

Defect IDs C1-C7 are those of `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` section STM-T04.

## 4. Items marked UNVERIFIED in the diagrams

- `LIB/adar1000.c` (ADI no-OS) is included by `CODE/main.cpp:24` but no `adar1000_*` call was found in `main.cpp` or `ADAR1000_Manager.cpp`; whether it is linked/used is unverified.
- USB OTG_FS pin/AF configuration (PA11/PA12 AF10) lives in the missing `usbd_conf.c`; only the schematic nets `STM32_USB_FS_D_P/D_N` support it (`docs/SYSTEM/BLOCK_DIAGRAM.md` 2.4).
- USB VID/PID/strings (missing `usbd_desc.c`); the GUI filters on six ST PIDs (`GUI_V5.py:323-330`).
- Compilation, link, interrupt priorities, I2C bus speeds, actual SPI clock: not verifiable without the HAL package and toolchain (none in repo).
- Every hardware behaviour (enumeration, byte flow, timing) - no bench test was performed.

## 5. How to regenerate the exports

```sh
cd engineering/SOFTWARE_DIAGRAMS/STM32
for d in stm32_firmware_architecture stm32_usb_cdc_flow; do
  for f in svg pdf png; do dot -T$f -Gdpi=150 $d.dot -o $d.$f; done
done
```
