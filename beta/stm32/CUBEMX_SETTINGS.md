# CUBEMX_SETTINGS — reproducing `aeris10_f746.ioc` in STM32CubeMX

A CubeMX `.ioc` cannot be generated without CubeMX; this page lists every setting so an engineer can rebuild
it in ~20 minutes and then diff the generated code against the hand-written files in `beta/stm32/`
(`Core/Src/main.cpp` MX_*_Init, `Core/Src/stm32f7xx_hal_msp.c`, `USB_DEVICE/*`). Items marked **(B)** are
BETA decisions (see `DECISIONS.md`); everything else is read from the original sources / schematic.

## 1. Project
| Field | Value |
|---|---|
| MCU | STM32F746ZGTx (LQFP-144), part U2 on `RADAR_Main_Board.sch` |
| Toolchain / IDE | STM32CubeIDE (or Makefile/CMake); language **C++** (main is `main.cpp`) |
| Firmware package | STM32Cube FW_F7 V1.17.x (HAL 1.3.x) — the beta uses HAL 1.3.3 from GitHub (`DECISIONS.md` D-15) |
| Code generator | "Copy only the necessary library files"; **do not** generate peripheral init as pairs of .c/.h (all `MX_*_Init` live in `main.cpp`); keep user code on regeneration |
| Middleware | USB_DEVICE → Class for FS IP: **Communication Device Class (Virtual Port Com)** |

## 2. RCC / clock configuration **(B — D-01, D-02)**
| Item | Value |
|---|---|
| HSE | Crystal/Ceramic resonator, **8 MHz** (XTAL1 NX3225GD-8MHZ on PH0/PH1) |
| LSE | crystal 32.768 kHz present on PC14/PC15 (XTAL3) — **not used** (leave disabled) |
| PLL source | HSE; **M = 8, N = 432, P = 2, Q = 9** → VCO 432 MHz |
| SYSCLK / HCLK | PLLCLK, **216 MHz**; AHB /1 |
| APB1 / APB2 | /4 → 54 MHz; /2 → 108 MHz (timer clocks: TIMPRE **activated** → TIM1CLK = 216 MHz) |
| USB (CLK48) | PLLQ = 48 MHz |
| Power | Voltage scale 1, **Over-Drive enabled**; Flash latency 7 WS |
| Original (for reference) | 25 MHz HSE, M25 N144 P2 Q3, 72 MHz, APB1 /2, APB2 /1, scale 3, 2 WS — invalid with the 8 MHz crystal |

## 3. System core
| Item | Value |
|---|---|
| SYS | Debug: Serial Wire (PA13 SWDIO, PA14 SWCLK; SWO PB3 on schematic); Timebase: SysTick |
| CORTEX_M7 | MPU: region 0, base 0x0, size 4 GB, sub-region disable 0x87, TEX 0, no access, XN, shareable, not cacheable, not bufferable; MPU enabled with `MPU_PRIVILEGED_DEFAULT`; I-cache / D-cache **disabled** (not enabled in code, ASSUMED) |
| NVIC | SysTick priority 15 (`TICK_INT_PRIORITY`); USB OTG FS global interrupt **enabled, priority 0/0 (B — D-08)**; no other interrupts |

## 4. Connectivity
| Peripheral | Mode | Pins (AF) | Parameters |
|---|---|---|---|
| I2C1 | I2C | PB6 SCL, PB7 SDA (AF4, open-drain, no pull, very high speed) | Standard mode **100 kHz**; analog filter on, digital filter 0; TIMINGR **(B — D-03)** 0x10916EA0 (let CubeMX recompute from 100 kHz, rise 100 ns / fall 10 ns, and compare) |
| I2C2 | I2C | PF0 SDA, PF1 SCL (AF4) | as I2C1 |
| I2C3 | I2C | PA8 SCL, PC9 SDA (AF4) | as I2C1 |
| SPI1 | Full-duplex master | PA5 SCK, PA6 MISO, PA7 MOSI (AF5) | 8-bit, MSB first, CPOL low, CPHA 1 edge, NSS software, NSSP enabled, CRC off; prescaler **16 → 6.75 MHz (B — D-06)**; CS = GPIO PA0..PA3 |
| SPI4 | Full-duplex master | PE2 SCK, PE5 MISO, PE6 MOSI (AF5) | as SPI1; CS = GPIO PF7 (AD9523), PG14 (ADF4382 TX), PG10 (ADF4382 RX) |
| UART5 | Asynchronous | PC12 TX, PD2 RX (AF8) | 9600 8N1, oversampling 16 (GPS NMEA) |
| USART3 | Asynchronous | PB10 TX, PB11 RX (AF7) | 115200 8N1 (debug / printf) |
| USB_OTG_FS | **Device_Only** | PA11 DM, PA12 DP (AF10, very high speed) | VBUS sensing **off**, SOF off, low-power off, LPM off; PA10 (ID) left unassigned **(B — D-07)** |
| TIM1 | Internal clock | — | Prescaler **215 (B — D-02)**, counter up, period 0xFFFE, clock division 1, repetition 0, auto-reload preload off, TRGO reset, MSM off |

## 5. USB_DEVICE middleware (CDC)
| Item | Value |
|---|---|
| Class | CDC (VCP); `USBD_MAX_NUM_INTERFACES 1`, `USBD_MAX_STR_DESC_SIZ 512`, `USBD_SELF_POWERED 1`, `USBD_DEBUG_LEVEL 0`, static malloc |
| Descriptors | VID 0x0483, PID 0x5740, LANGID 0x409 — **PLACEHOLDER (B — D-09)**; serial from UID; strings per `usbd_desc.c` |
| FIFO | Rx 0x80, Tx EP0 0x40, Tx EP1 0x80 (words) |
| App buffers | `APP_RX_DATA_SIZE 2048`, `APP_TX_DATA_SIZE 2048` |
| User code to re-insert after generation | in `usbd_cdc_if.c` `CDC_Receive_FS()` USER CODE 6: `AERIS_USB_OnReceive(Buf, *Len);` before `USBD_CDC_SetRxBuffer/ReceivePacket` **(B — D-10)** |

## 6. GPIO (user labels = `main.h` macros; all from the schematic nets)
Outputs, push-pull, no pull, low speed unless stated. Initial level LOW except where marked **HIGH (B — D-05)**.

| Pin | Label | Dir | Initial | Net / purpose |
|---|---|---|---|---|
| PF3 | AD9523_PD | out | low | AD9523 power-down |
| PF4 | AD9523_REF_SEL | out | low | AD9523 reference select |
| PF5 | AD9523_SYNC | out | low | AD9523 sync |
| PF6 | AD9523_RESET | out | low | AD9523 reset (active low; released in firmware) |
| PF7 | AD9523_CS | out | **HIGH** | SPI4 CS (active low) |
| PF8, PF9 | AD9523_STATUS0/1 | in | — | AD9523 status |
| PF10 | AD9523_EEPROM_SEL | out | low | |
| PF12..PF15 | LED_1..LED_4 | out | low | LEDs |
| PA0..PA3 | ADAR_1..4_CS_3V3 | out | **HIGH** | ADAR1000 CS (active low) |
| PG0, PG1, PG2 | EN_P_5V0_PA1/2/3 | out | low | `EN_+5V0_PA1..3` |
| PG3 | EN_P_5V5_PA | out | low | `EN_+5V5_PA` (VG driver rails) |
| PG4, PG5 | EN_P_1V8_CLOCK, EN_P_3V3_CLOCK | out | low | AD9523 rails |
| PG6 | ADF4382_RX_LKDET | in | — | |
| PG7, PG8 | ADF4382_RX_DELADJ, _DELSTR | out | low | |
| PG9 | ADF4382_RX_CE | out | low | |
| PG10 | ADF4382_RX_CS | out | **HIGH** | SPI4 CS |
| PG11 | ADF4382_TX_LKDET | in | — | |
| PG12, PG13 | ADF4382_TX_DELSTR, _DELADJ | out | low | |
| PG14 | ADF4382_TX_CS | out | **HIGH** | SPI4 CS |
| PG15 | ADF4382_TX_CE | out | low | |
| PE7, PE8, PE9 | EN_P_1V0/1V8/3V3_FPGA | out | low | FPGA rails |
| PE10 | EN_P_5V0_ADAR | out | low | |
| PE11, PE12 | EN_P_3V3_ADAR12/34 | out | low | |
| PE13 | EN_P_3V3_ADTR | out | low | LNA supply |
| PE14 | EN_P_3V3_SW | out | low | → −3V3_SW |
| PE15 | EN_P_3V3_VDD_SW | out | low | |
| PC6, PC7, PC8 | MAG_DRDY, ACC_INT, GYR_INT | in | — | IMU |
| PD4 | STEPPER_CW_P | out | low | |
| PD5 | STEPPER_CLK_P | out | low | |
| PD6 | EN_DIS_RFPA_VDD | out | low | 22 V drain switch (external, not in CAD) |
| PD7 | EN_DIS_COOLING | out | low | relay |
| PD8..PD12 | (no label) | out | low | FPGA handshake DIG_0..DIG_4: new chirp, new elevation, new azimuth, mixers enable, FPGA reset |
| PD13..PD15 | (no label) | in | — | DIG_5..7 from FPGA |
| PB4, PB5 | DAC_1_VG_CLR, DAC_1_VG_LDAC | out | low | DAC5578 #1 |
| PB8, PB9 | DAC_2_VG_CLR, DAC_2_VG_LDAC | out | low | DAC5578 #2 |
| PH0, PH1 | RCC_OSC_IN/OUT | — | — | 8 MHz crystal |
| PA13, PA14 | SWDIO, SWCLK | — | — | |

## 7. Project Manager → Advanced settings
Keep HAL (not LL) for every peripheral; "Register callbacks" off (`USE_HAL_*_REGISTER_CALLBACKS 0`); `USE_FULL_ASSERT` off.

## 8. After generation — what to compare
1. `Core/Src/stm32f7xx_hal_msp.c` must match `beta/stm32/Core/Src/stm32f7xx_hal_msp.c` (it is still the original, unchanged).
2. `SystemClock_Config()` / `PeriphCommonClock_Config()` → compare with `main.cpp:1803-1870` (beta).
3. `USB_DEVICE/Target/usbd_conf.c` → compare `HAL_PCD_MspInit` and `USBD_LL_Init` with the hand-written file; re-insert the `AERIS_USB_OnReceive` call in `usbd_cdc_if.c`.
4. Replace generated `main.c` by the beta `main.cpp` (delete `main.c`), keep `main.h` (identical content expected: verify with `diff`).
5. `startup_stm32f746zgtx.s` / `STM32F746ZGTX_FLASH.ld` generated by CubeIDE may replace the ST templates used here (same memory map: 1 MB flash @0x08000000, 320 KB RAM @0x20000000).
