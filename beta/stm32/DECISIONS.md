# beta/stm32 — Hardware-truth and engineering decisions

Each entry: what was decided, the evidence, what remains unverified. IDs are referenced from code comments,
`CHANGELOG.md` and `README.md`. Nothing here was validated on hardware.

## D-01 — HSE crystal is 8 MHz; clock tree re-targeted to 216 MHz
- **Evidence:** `RADAR_Main_Board.sch` part XTAL1 = NX3225GD-8MHZ-STD-CRA-3 on nets `STM32_OSC_N/P` → U2 pins 23/24 (PH0/PH1) (`docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` §3.1). The original firmware assumed 25 MHz (`hal_conf.h:97`, `main.cpp:1824` M=25) → with 8 MHz the PLL input would be 0.32 MHz, below the 0.95 MHz minimum (RM0385) and `HAL_RCC_OscConfig` would fail → `Error_Handler()`.
- **Decision:** `HSE_VALUE = 8000000`; PLL M=8 (1 MHz PFD), N=432 (432 MHz VCO), P=2 → SYSCLK 216 MHz, Q=9 → 48 MHz for OTG_FS. Voltage scale 1 + over-drive (`HAL_PWREx_EnableOverDrive`), flash latency 7 WS (VDD 3.3 V, RM0385 Table 5). CLK48 source = PLLQ made explicit in `PeriphCommonClock_Config()`.
- **Why 216 and not 72 MHz:** mandated by the bring-up brief; 216 MHz is the device maximum and is the standard CubeMX target for F746 (Nucleo template). An alternative that keeps the original 72 MHz would be M=4, N=144, P=2, Q=6 — documented in the reconstruction doc as a proposal, not used here.
- **Consequences handled:** D-02 (bus clocks, TIM1), D-03 (I2C timing), D-06 (SPI prescalers). `delay_ns()` and `no_os_udelay()` scale with `SystemCoreClock`/HCLK automatically.
- **Unverified:** crystal load capacitors/drive level for HSE at 8 MHz (board); `HSE_STARTUP_TIMEOUT` default 100 ms kept.

## D-02 — Bus clocks and TIM1 microsecond tick
- APB1 = 216/4 = 54 MHz (max 54), APB2 = 216/2 = 108 MHz (max 108). With `RCC_TIMPRES_ACTIVATED` and APB2 /2, TIM1CLK = HCLK = 216 MHz (RM0385 §5.2 TIMPRE=1 rule: prescaler 1/2/4 → timer clock = HCLK).
- TIM1 prescaler 71 → 215 so that `micros()`/`delay_us()` keep a 1 µs tick (`main.cpp:283-295`). The original comment confirms the 1 µs intent ("72MHz/presc+1, presc=71").
- UART baud rates (9600 GPS, 115200 debug) are computed by HAL from PCLK1 — unchanged.

## D-03 — I2C TIMINGR recomputed for PCLK1 = 54 MHz
- Original `0x00808CD2` decodes (PRESC 0, SCLL 210, SCLH 140, SCLDEL 8, SDADEL 0) to ~100 kHz Standard mode at 36 MHz → the intended bus speed is 100 kHz (DAC5578, ADS7830, GY-85, BMP180 all support 100 kHz).
- New `0x10916EA0` (PRESC 1, SCLL 160, SCLH 110, SCLDEL 9, SDADEL 1) at 54 MHz: tLOW 6.05 µs, tHIGH 4.20 µs, ~97.6 kHz, tSU;DAT 370 ns — computed and checked by `tests/check_i2c_timing.py` (simplified RM0385 model). **This is not a CubeMX output** — regenerate with CubeMX (I2C 100 kHz, analog filter on, rise 100 ns / fall 10 ns defaults) and compare before trusting it on hardware.

## D-04 — ADF4382 control pins follow main.h / schematic (PG6..PG15)
- `adf4382a_manager.h:8-29` hard-coded PG0..PG9 for CE/CS/DELADJ/DELSTR/LKDET. `main.h:94-157` (generated from the schematic nets `ADF4382_TX_*`/`ADF4382_RX_*`) places them on PG6..PG15, while PG0..PG5 are `EN_+5V0_PA1/2/3`, `EN_+5V5_PA`, `EN_+1V8_CLOCK`, `EN_+3V3_CLOCK`. With the original macros `ADF4382A_Manager_Init()` would have driven the PA 5 V enables as chip-enables (safety relevant) and read "lock detect" from the clock-enable outputs.
- Decision: the macros alias `main.h`. The manager API is unchanged.

## D-05 — SPI chip selects: logical index, active-low, idle high
- The original platform layer ignored `chip_select` and never toggled any CS; `MX_GPIO_Init()` drove `AD9523_CS` (PF7) and both `ADF4382_*_CS` LOW permanently, i.e. all three SPI4 slaves selected at once.
- `no_os_spi_init_param::chip_select` is `uint8_t`; a 16-bit GPIO mask does not fit. Decision: `chip_select` is an index into a table in `stm32_spi.c` built from `main.h` macros: 0 = AD9523 (PF7), 1 = ADF4382 TX (PG14), 2 = ADF4382 RX (PG10). CS is pulled low only around each `HAL_SPI_TransmitReceive()` and parked high at init/remove; `MX_GPIO_Init()` now parks all CS lines high (also ADAR1000 CS PA0..PA3, which `ADAR1000_Manager::setChipSelect()` toggles itself).
- AD9523 (CS-bar) and ADF4382 (CSB) are active-low per their datasheets (standard SPI); ADAR1000 CS is active-low (`ADAR1000_Manager.cpp:631` already inverts).

## D-06 — SPI clock ≤ 10 MHz
- AD9523 and ADF4382 init params request `max_speed_hz = 10 MHz` (`main.cpp:1036`, `adf4382a_manager.h:39`). SPI1/SPI4 are on APB2 = 108 MHz; the original `/2` prescaler would give 54 MHz.
- Decision: `MX_SPI1_Init`/`MX_SPI4_Init` use `/16` = 6.75 MHz; `stm32_spi.c` additionally derives the prescaler from `max_speed_hz` at `no_os_spi_init()` (largest clock ≤ requested → `/16`). SPI1 (ADAR1000 through the FPGA level shifters) also gets 6.75 MHz: conservative; the ADAR1000 SCLK maximum and the level-shifter bandwidth are **REQUIRES DATASHEET / BOARD VERIFICATION**.

## D-07 — USB OTG_FS, device-only, PA11/PA12 only
- Schematic nets `STM32_USB_FS_D_N` (PA11), `STM32_USB_FS_D_P` (PA12), `STM32_USB_FS_ID` (PA10) → mini-USB X53 (reconstruction doc §3.2). The repository `stm32f7xx_it.c` has only `OTG_FS_IRQHandler` (no wake-up handler) and `MX_USB_DEVICE_Init()` is called from `main()`, consistent with CubeMX "Device_Only".
- Decision (CubeMX Device_Only defaults): PA11/PA12 AF10 very-high speed; `vbus_sensing_enable = DISABLE`, `low_power_enable = DISABLE`, `lpm_enable = DISABLE`, `Sof_enable = DISABLE`, `dma_enable = DISABLE`, `dev_endpoints = 6`, `PCD_PHY_EMBEDDED`; FIFO Rx 0x80 / Tx0 0x40 / Tx1 0x80 words. PA10 (ID) and PA9 (VBUS) are left unconfigured. Whether VBUS is wired to PA9 on the board is **not verified** — if it is and the host requires VBUS sensing, set `vbus_sensing_enable` and configure PA9.

## D-08 — OTG_FS interrupt priority 0 (CubeMX default)
- No priority exists in the repository (`usbd_conf.c` was missing). CubeMX default is 0/0; SysTick is 15 (`TICK_INT_PRIORITY`). `AERIS_USB_OnReceive()` runs in this ISR and only copies ≤64 bytes — acceptable. Revisit if other interrupts are added.

## D-09 — USB VID/PID are placeholders
- `0x0483:0x5740` (ST "Virtual ComPort" demo) chosen only because `GUI_V5.py:323-330` enumerates on that list; strings say "PLACEHOLDER". A product VID/PID must be obtained before release. Serial number = STM32 96-bit UID (`UID_BASE` 0x1FF0F420, CMSIS `stm32f746xx.h:1228`), as CubeMX does.

## D-10 — CDC receive path bound through `AERIS_USB_OnReceive()`
- `usbd_cdc_if.c:CDC_Receive_FS()` → `AERIS_USB_OnReceive(Buf, *Len)` → `usbHandler.processUSBData()`, then re-arms the OUT endpoint. The original `extern "C" CDC_Receive_FS` in `main.cpp` was unreachable (CubeMX binds its own static function of that name). Transmit uses `CDC_Transmit_FS()` (returns `USBD_BUSY` while a transfer is pending — callers `main.cpp:1692`, `gps_handler.cpp:118` ignore the return value, as in the original).

## D-11 — PA / ADTR1107 power sequencing
- Evidence: `engineering/ELECTRICAL/power_distribution/power_rails.md` §1 (rows `+5V5_PA`, `-5V5_PA`, `VG_1..16`, `+5V0_PA_1..3`, `+3V3_ADTR`, `+22V0/VD`) and §3; xlsx procedures (quoted there): ADTR1107 TX/RX — VDD_SW → VSS_SW → CTRL_SW → VGG_LNA/VGG_PA → VDD_LNA (RX step 8) / VDD_PA (TX step 8); QPA2962 bias-up (L58-L62): VG −4 V → VD +22 V → raise VG until IDQ 1.68 A → RF.
- Findings: (a) `EN_+5V5_PA` (PG3) was **never** driven high — the OPA4703 VG buffers were unpowered while `main.cpp:1583-1601` "programmed" VG and then enabled the 22 V drain; (b) `EN_+3V3_ADTR` and `EN_+5V0_PA1/2/3` **are** asserted, but through raw pin numbers in `ADAR1000_Manager.cpp` (`initializeADTR1107Sequence()`, `setADTR1107Mode()`, `enable/disablePASupplies()`, `enable/disableLNASupplies()`), which the earlier audit missed; their order (VDD_SW → VSS_SW → CTRL → VGG → VDD_PA/VDD_LNA) matches the xlsx, so it was kept and only re-expressed with `main.h` macros; (c) power-down never removed the 22 V drain.
- Decisions: enable `+5V5_PA` 100 ms before the first DAC write; 20 ms VG settle before `EN/DIS_RFPA_VDD`; on power-down drop VD first, then PA 5 V, LNA, switch rails, and `+5V5_PA` last. Delays are conservative estimates, **not measured**. The IDQ servo loop (`main.cpp:1628-1656`) and the 1.68 A target were not touched. The external 22 V source and its switch are not in CAD (K4 in `docs/SYSTEM/BLOCK_DIAGRAM.md`).

## D-12 — AD9523: single `ad9523_setup()`, no `ad9523_init()` after configuration
- `ad9523_init()` is a "fill defaults" helper that overwrites every `pdata` field (`LIB/ad9523.c:344-418`). `configure_ad9523()` called it **after** building `pdata` and then ran `ad9523_setup()` twice. Found by `tests/test_ad9523_regs.c` (channel registers came out as divider 0 / LVPECL / powered down). Fixed by removing the call and the duplicate setup; the register table now matches the design intent (300/400/100/20/60/120 MHz outputs from a 3.6 GHz VCO) — verified against the driver's own encoding on the host, **not on silicon**.

## D-13 — Compiler/linker flags (ASSUMED CubeIDE defaults)
- `-mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=hard`, `-Og -g3` (Debug), `-ffunction-sections -fdata-sections`, C++: `-fno-exceptions -fno-rtti -fno-use-cxa-atexit -fno-threadsafe-statics`; link: `--specs=nano.specs`, `-u _printf_float` (status strings use `%f`), `--gc-sections`, libs `c m stdc++ nosys` (nosys only supplies symbols that `syscalls.c` does not define). `<iostream>` is included by `main.cpp` but unused, so no stream objects are linked.
- Toolchain used: Arm GNU Toolchain 14.2.Rel1 (`arm-none-eabi-gcc 14.2.1 20241119`), installed from the Arm tarball to `~/opt/arm-gnu-toolchain` and symlinked into `/opt/homebrew/bin` (the Homebrew cask `gcc-arm-embedded` failed: needs sudo).

## D-14 — Sources excluded from the build
- `platform_noos_stm32.c` (undefined symbol, no users), `adar1000.c` (unused C driver duplicating `ADAR1000_Manager`), `iio.c`, `iio_app.c`, `iiod.c`, `iio_trigger.c` (need lwIP/tcp sockets), every `no_os_*.c` not required by `ad9523.c`/`adf4382.c`/`no_os_spi.c` (`no_os_spi.c`, `no_os_util.c`, `no_os_alloc.c`, `no_os_mutex.c` are compiled). Only the files listed in `CMakeLists.txt` are built; the rest of `LIB/` is kept for reference.

## D-15 — STM32CubeF7 components (pinned)
- `STMicroelectronics/STM32CubeF7` @ `79165e260557395e1c28f5a0ba93cb731aa48f17` (sparse: `Drivers/CMSIS`, `Drivers/STM32F7xx_HAL_Driver`, `Middlewares/ST/STM32_USB_Device_Library`, `Projects/STM32F746ZG-Nucleo/Templates`, `Projects/STM32F746ZG-Nucleo/Applications/USB_Device`).
- Submodules: `stm32f7xx_hal_driver` @ `e860c4ff226d0e4ac2837b31960649898b29ee88` (HAL 1.3.3, 2026-09-16); `cmsis_device_f7` @ `2352e888e821aa0f4fe549bd5ea81d29c67a3222` (v1.2.10); `stm32-mw-usb-device` @ `2a0a3521ac4d84e6e494d37bed615e2d36c373f5` (2025-04-15). CMSIS Core headers come from the STM32CubeF7 tree itself (`Drivers/CMSIS/Include`, `Drivers/CMSIS/Core/Include`).
- `tools/stm32_check_cube_package.sh beta/stm32/cube` → "missing 0 of 34", exit 0. Reproduce with `setup_cube.sh`.

## D-16 — `GPS_Init(&huart3)`
- `gps_handler.cpp` guards both senders on `gui_huart != NULL` (`:47`, `:67`) although the binary packet goes to USB CDC. Binding USART3 (the debug UART) satisfies the guard and routes the text variant to the debug port; no new hardware assumption.

## Open items deliberately NOT decided here (see README "Unresolved")
VM_I/VM_Q/VM_GAIN tables are empty placeholders; ADAR1000/ADF4382/AD9523 register-level correctness; 180 s OCXO wait; cache/MPU policy; interrupt priorities beyond USB; stack/heap sizing beyond ST defaults; VBUS sensing; crystal load.
