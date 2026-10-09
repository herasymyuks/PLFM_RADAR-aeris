# AERIS-10 STM32F746ZGT7 firmware — BETA build tree

**Status: BETA = compiles and links with the ST HAL/USB stack. Not flashed. Not run on hardware. No
peripheral, RF or power-sequence behaviour has been observed.** Everything "hardware" in this tree is an
engineering decision recorded in `DECISIONS.md`, derived from the schematic-based tables in
`docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`, `main.h`, `engineering/ELECTRICAL/power_distribution/power_rails.md`
and ST reference material in `cube/`.

The originals under `9_Firmware/9_1_Microcontroller/` are untouched; this directory holds edited copies.
Every difference is listed in `CHANGELOG.md` (file:line, reason, "defect fix" vs "hardware-truth decision").

## Layout
```
beta/stm32/
├── Core/Inc, Core/Src, Core/Startup   main.cpp/main.h + CubeMX glue (copied), startup_stm32f746xx.s (ST CMSIS template)
├── LIB/                               copy of 9_1_1_C_Cpp_Libraries (+ aeris_beam.*, _excluded/)
├── USB_DEVICE/App, USB_DEVICE/Target  hand-written CubeMX-equivalent USB CDC files
├── STM32F746ZGTx_FLASH.ld             ST Nucleo-F746ZG template (AXIM flash 1 MB @0x08000000, RAM 320 KB @0x20000000)
├── CMakeLists.txt, cmake/arm-none-eabi.cmake, build.sh, setup_cube.sh
├── cube/                              STM32CubeF7 sparse checkout (git-ignored; pinned commits in DECISIONS.md D-15)
├── tests/                             host-side unit tests (run_tests.sh)
├── build/ (ignored), build_out/       artefacts: aeris10_fw.elf/.hex/.bin/.map
├── logs/                              build, size, warning, include-check and test logs
└── CHANGELOG.md, DECISIONS.md, CUBEMX_SETTINGS.md, README.md
```

## 1. Toolchain
- **Arm GNU Toolchain 14.2.Rel1** (`arm-none-eabi-gcc 14.2.1 20241119`). On this machine it was installed from the
  Arm tarball (`arm-gnu-toolchain-14.2.rel1-darwin-arm64-arm-none-eabi.tar.xz`) extracted to
  `~/opt/arm-gnu-toolchain` and symlinked into `/opt/homebrew/bin/arm-none-eabi-*`. The Homebrew cask
  `gcc-arm-embedded` **failed** (its installer needs sudo). Any 12.x–14.x arm-none-eabi GCC should work; the
  CMake toolchain file searches `/opt/homebrew/bin`, `~/opt/arm-gnu-toolchain/bin` and
  `/Applications/ArmGNUToolchain/*/arm-none-eabi/bin`, or pass `-DTOOLCHAIN_PREFIX=/path/arm-none-eabi-`.
- CMake ≥ 3.20 (4.4.3 used), Ninja (optional), Python 3 for the checks, a host C/C++ compiler for the tests.

## 2. STM32CubeF7 (HAL, CMSIS, USB Device Library)
```sh
bash beta/stm32/setup_cube.sh          # sparse clone at the pinned commits, verifies with tools/stm32_check_cube_package.sh
```
Expected: `Package: beta/stm32/cube — missing 0 of 34 required files` (exit 0). Components: HAL 1.3.3
(`e860c4ff`), cmsis_device_f7 v1.2.10 (`2352e888`), USB Device Library (`2a0a3521`), STM32CubeF7 `79165e26`.

## 3. Build
```sh
bash beta/stm32/build.sh               # Debug (-Og -g3); or: bash beta/stm32/build.sh Release
```
`build.sh` configures CMake, builds, prints `arm-none-eabi-size`, writes `logs/build_full.log`,
`logs/build_warnings.log`, `logs/build_errors.log`, `logs/size.log` and copies
`aeris10_fw.elf/.hex/.bin/.map` to `build_out/`. **Exit code 0 only on a clean link.**

### Result on 2026-10-09 (clean build, Debug)
```
Memory region         Used Size  Region Size  %age Used
             RAM:       12952 B       320 KB      3.95%
           FLASH:       91276 B         1 MB      8.70%
   text    data     bss     dec     hex filename
  90480     788   12176  103444   19414 aeris10_fw.elf
```
0 errors. 5 unique warnings, all pre-existing code (`logs/build_warnings.log`): `main.cpp` unused `settings`
reference (the original commented-out block), `BMP180.cpp` misleading indentation ×3, `TinyGPS++.cpp` implicit
fall-through. Third-party HAL/USB sources are compiled with `-w`.

Include audit: `python3 tools/check_stm32_includes.py --root <copy>` on `Core/LIB/USB_DEVICE`
(`logs/check_stm32_includes_beta.log`): **0 case mismatches** (was 6); the 11 remaining UNKNOWN headers are
all in `iio*.c` / `iiod.c`, which are not built; HAL/CMSIS/USB headers are reported "not in repository" because
the script does not know about `cube/`. (The script hard-codes the `9_Firmware/9_1_Microcontroller` sub-path,
so it was run against a scratch copy laid out that way.)

## 4. Host unit tests
```sh
bash beta/stm32/tests/run_tests.sh     # needs cc/c++ + python3 only
```
Result 2026-10-09: **4/4 PASSED** (`logs/tests_*.log`)
| Test | What it checks |
|---|---|
| `test_settings_parser.cpp` | real `USBHandler.cpp` + `RadarSettings.cpp`: start flag `[23,46,158,237]`, 82-byte big-endian `SET…END` packet, unpadded and GUI-style 64-byte zero-padded framing, flag+settings in one packet, `SET` straddling a packet boundary, byte-at-a-time, short packets, invalid-value rejection and recovery, big-endian decode against a hand-encoded constant (9 cases) |
| `test_beam_matrix.c` | `aeris_beam.c` (verbatim arithmetic of `initializeBeamMatrices`/`degreesTo7BitPhase`): 7-bit phase conversion, reference element, range, hand-computed samples, mirror symmetry, linearity |
| `test_ad9523_regs.c` | real `ad9523.c` + `no_os_spi.c` against a mock SPI register file: full `ad9523_setup()` path, channel distribution registers for OUT0/1/4/5/6/7/8/9/10/11 (dividers 12/9/36/180/60/30, LVDS/CMOS modes), unused outputs powered down, IO_UPDATE/SYNC/status. **This test found defect C8** (see below) |
| `check_i2c_timing.py` | decodes TIMINGR: original `0x00808CD2`@36 MHz ≈ 100 kHz; beta `0x10916EA0`@54 MHz ≈ 97.6 kHz, I2C Standard-mode minima met |

Not host-testable as-is (need HAL types): `stm32_spi_prescaler_for()`, the USB glue, power sequencing.

## 5. Defects fixed (details and line numbers in `CHANGELOG.md`)
| ID | Defect in the original | Fix |
|---|---|---|
| C2 | `adf4382a_manager.h` drove PG0..PG9 (PA/clock power enables) as ADF4382 CE/CS/lock-detect | macros alias `main.h` PG6..PG15; CE parameter widened to 16 bit |
| C3 | ADF4382 `platform_ops = NULL` → `no_os_spi_init` returns `-EINVAL` → `Error_Handler()` | `&stm32_spi_ops` |
| C4 | USB RX callback never bound; start-flag wait loop could never exit | `usbd_cdc_if.c:CDC_Receive_FS` → `AERIS_USB_OnReceive()` → `USBHandler` |
| C5 | GUI zero-padding after the start flag landed in the settings buffer; `"SET"` never at offset 0 | parser synchronises on `SET`, handles padded/unpadded/split frames (tested) |
| C6 | `GPS_Init()` never called → `GPS_SendBinaryToGUI()` returned early | `GPS_Init(&huart3)` |
| C7 | SPI chip selects driven low permanently and never toggled; SPI clock PCLK/2 regardless of the 10 MHz request | CS index table + toggling in `stm32_spi.c`, CS parked high, prescaler from `max_speed_hz` |
| C8 | `ad9523_init()` called after `pdata` was configured → whole AD9523 channel/PLL configuration reset to defaults | call removed |
| C9 | `ad9523_setup()` executed twice (first device leaked) | single call after reset release |
| U10 | IDQ servo for DAC2 read ADC2 into `adc1_readings` and computed from stale data | `adc2_readings` |
| — | `printf()` → weak `__io_putchar` undefined → call to address 0 | retargeted to USART3 |
| — | `USBHandler::processStartFlag` unsigned underflow on packets < 4 bytes | guarded |
| — | `stm32_spi_write_and_read` prototype mismatch (`uint32_t` vs `uint16_t`), hard error on GCC 14 | fixed |
| — | `LIB/errno.h` `#include_next` self-inclusion → `EINVAL` undefined | shim excluded |
| — | `.H` include-case mismatches | files renamed `.h` |

## 6. Hardware-truth decisions (full text in `DECISIONS.md`)
D-01 8 MHz HSE → PLL M8/N432/P2/Q9, 216 MHz, over-drive, 7 WS · D-02 APB1 54 / APB2 108 MHz, TIM1 PSC 215 ·
D-03 I2C TIMINGR 0x10916EA0 (computed, not CubeMX) · D-04 ADF4382 pins per schematic · D-05 CS index/idle-high ·
D-06 SPI 6.75 MHz (≤10 MHz) · D-07 OTG_FS device-only PA11/PA12, no VBUS sensing · D-08 USB IRQ priority 0 ·
D-09 VID/PID 0x0483:0x5740 PLACEHOLDER · D-10 CDC RX hook · D-11 PA sequencing: `+5V5_PA` before VG DAC
programming, VG before VD, VD removed first on power-down (delays are estimates) · D-12 AD9523 single setup ·
D-13 compiler flags = CubeIDE defaults (assumed) · D-14 excluded sources · D-15 pinned Cube commits · D-16 `GPS_Init`.

## 7. Unresolved / remaining work
1. **Regenerate the CubeMX project** from `CUBEMX_SETTINGS.md` and diff the generated `usbd_conf.c`, `usbd_desc.c`,
   `usbd_cdc_if.c`, `usb_device.c`, startup and linker script against the hand-written files; let CubeMX recompute
   the I2C TIMINGR (D-03) and confirm the clock tree (D-01/D-02).
2. **Hardware bring-up** per `engineering/ASSEMBLY/ASSEMBLY_SEQUENCE.md` §B: flash via SWD
   (`STM32_Programmer_CLI -c port=SWD -w beta/stm32/build_out/aeris10_fw.elf -v -rst`), verify HSE/PLL lock and
   216 MHz (SWO/USART3 output at 115200 proves the clock), CDC enumeration (placeholder VID/PID), start flag +
   settings acceptance, enable-rail order on a scope (power_rails.md §3 + D-11), AD9523 lock, ADF4382 lock, SPI
   waveforms (CS, ≤10 MHz).
3. `ADAR1000_Manager.cpp:23-33` — `VM_I`, `VM_Q`, `VM_GAIN` are **empty placeholder tables** ("same as in your
   original file"): every phase/gain write is 0 → beam steering cannot work. Needs the ADAR1000 vector-modulator
   tables from the datasheet/original project.
4. ADAR1000 SCLK limit and FPGA level-shifter bandwidth (SPI1 clock, D-06); AD9523/ADF4382 register-level
   correctness; ADF4382 `DELADJ` "PWM" is a stub (`adf4382a_manager.c:433-460`).
5. VBUS wiring to PA9 (D-07); production VID/PID (D-09); USB interrupt priority policy (D-08).
6. `main.cpp` logic not touched: 180 s OCXO wait at boot; `last_check` reused for the temperature timer
   (`main.cpp:1774` updates `last_check` instead of `last_check1`); `getSystemStatusForGUI()` reports raw ADC
   codes as temperatures (no 0.64705 scale); health check thresholds; the IDQ servo exit conditions.
7. Cache (I/D) stays disabled, MPU background region as generated — review for 216 MHz performance needs.
8. PA drain 22 V source/switch and stepper supply are not in CAD (K4 — hardware design item).
9. Static analysis (cppcheck) and `-fstack-usage` review (`build/**/*.su` are generated) not yet done.
