# STM32 firmware — architecture, build, defects fixed, power sequencing, USB protocol

**Author of this chapter:** Antidrone Ukraine · antidrone.cc (compilation of the BETA firmware tree and its decision records; the upstream sources under `9_Firmware/9_1_Microcontroller/` are ORIGINAL PROJECT FILE and untouched).

**Status summary:** **BETA** — "compiles and links with the ST HAL/USB stack. Not flashed. Not run on hardware. No peripheral, RF or power-sequence behaviour has been observed" (source: `beta/stm32/README.md`, header). Architecture diagrams SD-03/SD-04 are **PARTIAL** (drawn from the original sources, in which the HAL, CubeMX files and USB middleware were absent). Clock tree, I2C timing, SPI prescalers, USB descriptors and the power-sequencing delays are **engineering decisions** (D-01…D-19 of `beta/stm32/DECISIONS.md`), not measurements.

**Sources:** `beta/stm32/README.md`, `beta/stm32/DECISIONS.md`, `beta/stm32/CHANGELOG.md`, `beta/stm32/CUBEMX_SETTINGS.md`, `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md`, `engineering/ELECTRICAL/power_distribution/power_rails.md` §2–§3, `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_architecture.md`, `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §5, §7, `beta/gui/aeris10_gui/protocol/settings_packet.py` and `status_text.py` (docstrings that quote the firmware line numbers).

**Figures in this chapter:** F12.1 firmware architecture (SD-03), F12.2 USB CDC flow (SD-04).

## 12.1 Target and what the firmware does

MCU: **STM32F746ZGTx (LQFP-144), part U2 on `RADAR_Main_Board.sch`** (source: `beta/stm32/CUBEMX_SETTINGS.md` §1). The application is a CubeMX-style `main.c` renamed to C++ (`main.cpp`, 2411 lines in the original) that owns every peripheral handle, all `MX_*_Init` functions, the clock tree and the whole application sequence; drivers live in `LIB/` as three families (source: `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_architecture.md` §1, copied):

| Family | Files | Transport | Evidence |
|---|---|---|---|
| C++ board classes | `ADAR1000_Manager.cpp/.h`, `USBHandler.cpp/.h`, `RadarSettings.cpp/.h`, `BMP180.cpp/.h`, `gps_handler.cpp/.h`, `TinyGPS++.cpp` | HAL directly (`hspi1`, `huart3`, `hi2c3`), CDC | `ADAR1000_Manager.cpp:8-9,619-621`; `BMP180.cpp:405-409`; `gps_handler.cpp:60,118` |
| ADI no-OS drivers + core | `ad9523.c/.h`, `adf4382.c/.h`, `adf4382a_manager.c/.h`, `adar1000.c/.h`, `no_os_*.c/.h` (60 files), `iio*.c/.h` | `no_os_spi` -> `platform_ops` -> `stm32_spi.c` -> `hspi4` | `CODE/main.cpp:1039-1040`; `adf4382a_manager.c:42-43,51-52` |
| C HAL sensor drivers | `DA5578.c`/`DAC5578.H`, `ADS7830.c/.H`, `GY_85_HAL.c/.h` | HAL I2C (`hi2c1`, `hi2c2`, `hi2c3`) | `DA5578.c:69`; `ADS7830.c:111-121`; `GY_85_HAL.c:35-116`; handles passed at `CODE/main.cpp:1563,1570,1605,1611,1670` |

Peripheral-to-device map (source: same note §1): I2C1 PB6/PB7 → 2 × DAC5578 (PA gate bias); I2C2 PF0/PF1 → 3 × ADS7830 (IDQ sense, temperatures); I2C3 PA8/PC9 → GY-85 + BMP180; SPI1 PA5/PA6/PA7 + CS PA0..PA3 → ADAR1000 ×4 through the FPGA level shift; SPI4 PE2/PE5/PE6 → AD9523 (CS PF7) and ADF4382 TX/RX (CS PG14/PG10); UART5 PC12/PD2 → GPS NMEA; USART3 PB10/PB11 → debug text; TIM1 → `delay_us()`; GPIO PD8..PD12 → FPGA handshake; USB OTG_FS → host CDC.

![F12.1 — STM32 firmware architecture: main.cpp application sequence, driver families, peripheral handles; dashed red = HAL/CMSIS/startup/linker/USB middleware absent from the upstream repository (SD-03) [PARTIAL] (source: engineering/SOFTWARE_DIAGRAMS/STM32/stm32_firmware_architecture.png; produced by hand-authored DOT + Graphviz dot -Tpng -Gdpi=150)](engineering/SOFTWARE_DIAGRAMS/STM32/stm32_firmware_architecture.png)

![F12.2 — USB CDC flow host ↔ STM32 as found in the original sources: start flag, zero-padding defect C5, settings packet, unbound receive callback C4, status/GPS transmit (SD-04); the beta tree fixes C4/C5 (§12.4) [PARTIAL] (source: engineering/SOFTWARE_DIAGRAMS/STM32/stm32_usb_cdc_flow.png; produced by hand-authored DOT + Graphviz)](engineering/SOFTWARE_DIAGRAMS/STM32/stm32_usb_cdc_flow.png)

## 12.2 BETA tree layout

(source: `beta/stm32/README.md`, "Layout", copied)

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

What was missing upstream and how the beta fills it (source: `engineering/SOFTWARE_DIAGRAMS/STM32/stm32_architecture.md` §2; `beta/stm32/CHANGELOG.md` §3): no `stm32f7xx_hal.h`/HAL driver, no CMSIS device header, no `startup_stm32f746xx.s`, no linker script, no `.ioc`, no `usb_device.c/.h`, `usbd_cdc_if.c/.h`, `usbd_desc.c/.h`, `usbd_conf.c/.h`, no USB Device Library. The beta adds the HAL/CMSIS/USB library as a pinned sparse checkout (`cube/`), the ST startup and linker templates verbatim, and hand-written CubeMX-equivalent USB files built from the ST templates (D-07…D-10). The `.ioc` itself cannot be generated without CubeMX; `CUBEMX_SETTINGS.md` lists every setting "so an engineer can rebuild it in ~20 minutes and then diff the generated code against the hand-written files".

## 12.3 Build procedure

### Step 12.1 — Toolchain [BETA, executed on the authoring machine]

- **Purpose:** provide the cross-compiler and build tools.
- **Parts & tools:** Arm GNU Toolchain 14.2.Rel1 (`arm-none-eabi-gcc 14.2.1 20241119`); CMake ≥ 3.20 (4.4.3 used); Ninja optional; Python 3; a host C/C++ compiler for the tests (source: `beta/stm32/README.md` §1).
- **Action:** install the Arm tarball (on the authoring machine extracted to `~/opt/arm-gnu-toolchain` and symlinked into `/opt/homebrew/bin/arm-none-eabi-*`; the Homebrew cask `gcc-arm-embedded` failed because its installer needs sudo). The CMake toolchain file searches `/opt/homebrew/bin`, `~/opt/arm-gnu-toolchain/bin` and `/Applications/ArmGNUToolchain/*/arm-none-eabi/bin`, or pass `-DTOOLCHAIN_PREFIX=/path/arm-none-eabi-`.
- **Check:** `arm-none-eabi-gcc --version` prints 14.2.1 (verified on 2026-10-09 on the authoring machine: "Arm GNU Toolchain 14.2.Rel1 (Build arm-14.52) 14.2.1 20241119"). "Any 12.x–14.x arm-none-eabi GCC should work" (README §1 — unverified claim of the source).
- **Figure:** —
- **⚠ Decision:** D-13 — compiler/linker flags are **ASSUMED** CubeIDE defaults (`-mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=hard`, `-Og -g3` Debug, `-ffunction-sections -fdata-sections`, C++ `-fno-exceptions -fno-rtti -fno-use-cxa-atexit -fno-threadsafe-statics`, link `--specs=nano.specs -u _printf_float --gc-sections`, libs `c m stdc++ nosys`).

### Step 12.2 — STM32CubeF7 package [BETA]

- **Purpose:** obtain the HAL, CMSIS and USB Device Library at the pinned commits.
- **Parts & tools:** `bash beta/stm32/setup_cube.sh` (sparse clone + check with `tools/stm32_check_cube_package.sh`).
- **Action:** run the script; it clones `STMicroelectronics/STM32CubeF7` @ `79165e26…` (sparse: `Drivers/CMSIS`, `Drivers/STM32F7xx_HAL_Driver`, `Middlewares/ST/STM32_USB_Device_Library`, Nucleo-F746ZG templates and USB_Device applications) with submodules `stm32f7xx_hal_driver` @ `e860c4ff…` (HAL 1.3.3), `cmsis_device_f7` @ `2352e888…` (v1.2.10), `stm32-mw-usb-device` @ `2a0a3521…` (source: `beta/stm32/DECISIONS.md` D-15).
- **Check:** "`Package: beta/stm32/cube — missing 0 of 34 required files` (exit 0)" (source: `beta/stm32/README.md` §2).
- **Figure:** —
- **⚠ Decision:** D-15 (pinned commits).

### Step 12.3 — Compile and link [BETA, result recorded]

- **Purpose:** produce `aeris10_fw.elf/.hex/.bin/.map`.
- **Parts & tools:** `bash beta/stm32/build.sh` (Debug, `-Og -g3`) or `bash beta/stm32/build.sh Release`.
- **Action:** run the script; it configures CMake, builds, prints `arm-none-eabi-size`, writes `logs/build_full.log`, `logs/build_warnings.log`, `logs/build_errors.log`, `logs/size.log` and copies the artefacts to `build_out/`. "Exit code 0 only on a clean link."
- **Check:** result recorded on 2026-10-09 (source: `beta/stm32/README.md` §3, copied):

```
Memory region         Used Size  Region Size  %age Used
             RAM:       17480 B       320 KB      5.33%
           FLASH:       93276 B         1 MB      8.90%
   text    data     bss     dec     hex filename
  92480     788   16704  109972   1ad94 aeris10_fw.elf
```

  0 errors; 5 unique warnings, all pre-existing code (`main.cpp` unused `settings` reference, `BMP180.cpp` misleading indentation ×3, `TinyGPS++.cpp` implicit fall-through); third-party HAL/USB sources compiled with `-w`. Include audit `python3 tools/check_stm32_includes.py`: 0 case mismatches (was 6); the 11 remaining UNKNOWN headers are all in `iio*.c`/`iiod.c`, which are not built.
- **Figure:** —
- **⚠ Decision:** D-14 — sources excluded from the build: `platform_noos_stm32.c`, `adar1000.c`, `iio.c`, `iio_app.c`, `iiod.c`, `iio_trigger.c`, and every `no_os_*.c` not required by `ad9523.c`/`adf4382.c`/`no_os_spi.c`.

### Step 12.4 — Host unit tests [BETA, 6/6 PASSED on 2026-10-09]

- **Purpose:** test the protocol and driver logic on the host without hardware.
- **Parts & tools:** `bash beta/stm32/tests/run_tests.sh` (needs cc/c++ + python3 only).
- **Check:** (source: `beta/stm32/README.md` §4, copied)

| Test | What it checks |
|---|---|
| `test_settings_parser.cpp` | real `USBHandler.cpp` + `RadarSettings.cpp`: start flag `[23,46,158,237]`, 82-byte big-endian `SET…END` packet, unpadded and GUI-style 64-byte zero-padded framing, flag+settings in one packet, `SET` straddling a packet boundary, byte-at-a-time, short packets, invalid-value rejection and recovery, big-endian decode against a hand-encoded constant, `REG` text commands coexisting with the binary path (10 cases) |
| `test_beam_matrix.c` | `aeris_beam.c` (verbatim arithmetic of `initializeBeamMatrices`/`degreesTo7BitPhase`): 7-bit phase conversion, reference element, range, hand-computed samples, mirror symmetry, linearity |
| `test_ad9523_regs.c` | real `ad9523.c` + `no_os_spi.c` against a mock SPI register file: full `ad9523_setup()` path, channel distribution registers for OUT0/1/4/5/6/7/8/9/10/11 (dividers 12/9/36/180/60/30, LVDS/CMOS modes), unused outputs powered down, IO_UPDATE/SYNC/status. **This test found defect C8** |
| `test_adar_vm_tables.c` | ADAR1000 VM tables vs data sheet Tables 10-13: 128 entries, bits 7:6 clear, quadrant signs, spot rows 0/45/90/180/230.625/270/312.1875/357.1875°, strictly monotonic decoded phase (max error 3.12°), `degreesTo7BitPhase` → table round trip |
| `test_host_bridge_cmds.c` | bridge v2 byte sequences with a mock SPI (0x02 + ack 0xA2 / no ack / 0xEE / transfer error, 0x03 LE decode, 0x04 status fields), ASCII `REG W/R` parser (hex/decimal, errors) and reply formatting |
| `check_i2c_timing.py` | decodes TIMINGR: original `0x00808CD2`@36 MHz ≈ 100 kHz; beta `0x10916EA0`@54 MHz ≈ 97.6 kHz, I2C Standard-mode minima met |

  Not host-testable as-is (need HAL types): `stm32_spi_prescaler_for()`, the USB glue, power sequencing.

## 12.4 Defects fixed in the BETA tree

Defect C1 is the HSE conflict (firmware 25 MHz vs the 8 MHz crystal XTAL1 NX3225GD-8MHZ on PH0/PH1 of the schematic; "with 8 MHz HSE the PLL input would be 0.32 MHz (below the 0.95 MHz minimum of RM0385)") and is closed by decision D-01 (source: `docs/STM32/STM32_PROJECT_RECONSTRUCTION.md` §5 row C1; `beta/stm32/DECISIONS.md` D-01). C2…C10 and the further defects (source: `beta/stm32/README.md` §5, copied; file:line details in `CHANGELOG.md`):

| ID | Defect in the original | Fix |
|---|---|---|
| C1 | HSE 25 MHz (firmware) vs 8 MHz crystal (schematic) — `hal_conf.h:97`, `main.cpp:1823` | `HSE_VALUE = 8000000`; PLL M8/N432/P2/Q9 → 216 MHz (D-01, hardware-truth decision) |
| C2 | `adf4382a_manager.h` drove PG0..PG9 (PA/clock power enables) as ADF4382 CE/CS/lock-detect | macros alias `main.h` PG6..PG15; CE parameter widened to 16 bit |
| C3 | ADF4382 `platform_ops = NULL` → `no_os_spi_init` returns `-EINVAL` → `Error_Handler()` | `&stm32_spi_ops` |
| C4 | USB RX callback never bound; start-flag wait loop could never exit | `usbd_cdc_if.c:CDC_Receive_FS` → `AERIS_USB_OnReceive()` → `USBHandler` |
| C5 | GUI zero-padding after the start flag landed in the settings buffer; `"SET"` never at offset 0 | parser synchronises on `SET`, handles padded/unpadded/split frames (tested) |
| C6 | `GPS_Init()` never called → `GPS_SendBinaryToGUI()` returned early | `GPS_Init(&huart3)` |
| C7 | SPI chip selects driven low permanently and never toggled; SPI clock PCLK/2 regardless of the 10 MHz request | CS index table + toggling in `stm32_spi.c`, CS parked high, prescaler from `max_speed_hz` |
| C8 | `ad9523_init()` called after `pdata` was configured → whole AD9523 channel/PLL configuration reset to defaults | call removed |
| C9 | `ad9523_setup()` executed twice (first device leaked) | single call after reset release |
| C10 | ADAR1000 phase/gain setters used `(channel & 3)` with 1-based channels → element pattern rotated by one channel per device | `((channel - 1) & 3)` |
| — | `VM_I/VM_Q/VM_GAIN` empty → every phase write was I = Q = 0 | tables from the data sheet (D-19) |
| U10 | IDQ servo for DAC2 read ADC2 into `adc1_readings` and computed from stale data | `adc2_readings` |
| — | `printf()` → weak `__io_putchar` undefined → call to address 0 | retargeted to USART3 |
| — | `USBHandler::processStartFlag` unsigned underflow on packets < 4 bytes | guarded |
| — | `stm32_spi_write_and_read` prototype mismatch (`uint32_t` vs `uint16_t`), hard error on GCC 14 | fixed |
| — | `LIB/errno.h` `#include_next` self-inclusion → `EINVAL` undefined | shim excluded |
| — | `.H` include-case mismatches | files renamed `.h` |

The C2 defect is safety-relevant: with the original macros `ADF4382A_Manager_Init()` "would have driven the PA 5 V enables as chip-enables … and read 'lock detect' from the clock-enable outputs" (source: `beta/stm32/DECISIONS.md` D-04).

## 12.5 Hardware-truth decisions (D-01…D-19)

One-line index (source: `beta/stm32/README.md` §6, copied; full text in `beta/stm32/DECISIONS.md`): D-01 8 MHz HSE → PLL M8/N432/P2/Q9, 216 MHz, over-drive, 7 WS · D-02 APB1 54 / APB2 108 MHz, TIM1 PSC 215 · D-03 I2C TIMINGR 0x10916EA0 (computed, not CubeMX) · D-04 ADF4382 pins per schematic · D-05 CS index/idle-high · D-06 SPI 6.75 MHz (≤10 MHz) · D-07 OTG_FS device-only PA11/PA12, no VBUS sensing · D-08 USB IRQ priority 0 · D-09 VID/PID 0x0483:0x5740 PLACEHOLDER · D-10 CDC RX hook · D-11 PA sequencing: `+5V5_PA` before VG DAC programming, VG before VD, VD removed first on power-down (delays are estimates) · D-12 AD9523 single setup · D-13 compiler flags = CubeIDE defaults (assumed) · D-14 excluded sources · D-15 pinned Cube commits · D-16 `GPS_Init` · D-17 REG commands executed from the main loop · D-18 bridge v2 framing assumptions · D-19 VM tables / VM_GAIN = 0.

Clock tree as decided (source: `beta/stm32/CUBEMX_SETTINGS.md` §2, copied):

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

Unverified items named by the decisions: crystal load capacitors / drive level at 8 MHz (D-01); the I2C TIMINGR is "not a CubeMX output — regenerate with CubeMX … and compare before trusting it on hardware" (D-03); ADAR1000 SCLK maximum and FPGA level-shifter bandwidth at 6.75 MHz (D-06); whether VBUS is wired to PA9 (D-07); a product VID/PID (D-09); the sequencing delays "are conservative estimates, not measured" (D-11); ADAR1000 phase accuracy (data-sheet tables realise the nominal phase within ≈ 3°, per-board calibration is a hardware task — D-19).

## 12.6 Power-enable sequencing

Enable-bus pin map (SV1 MA10-2, identical on both boards; 15 enable lines, "not 16 as stated in `docs/SYSTEM/BLOCK_DIAGRAM.md`") (source: `engineering/ELECTRICAL/power_distribution/power_rails.md` §2, copied):

| SV1 pin | Net | STM32 pin (`main.h`) | Power Board EN input |
|---|---|---|---|
| 1 | `EN_+1V0_FPGA` | PE7 | U1 |
| 2 | `EN_+5V0_PA2` | PG1 | U15 |
| 3 | `EN_+1V8_FPGA` | PE8 | U2 |
| 4 | `EN_+5V0_PA3` | PG2 | U16 |
| 5 | `EN_+3V3_FPGA` | PE9 | U4 |
| 6 | `EN_+5V5_PA` | PG3 | U17 |
| 7 | `EN_+5V0_ADAR` | PE10 | U13 |
| 8 | `EN_+1V8_CLOCK` | PG4 | U25 |
| 9 | `EN_+3V3_ADAR12` | PE11 | U6 |
| 10 | `EN_+3V3_CLOCK` | PG5 | U23 |
| 11 | `EN_+3V3_ADAR34` | PE12 | U7 |
| 13 | `EN_+3V3_ADTR` | PE13 | U32 |
| 15 | `EN_+3V3_SW` | PE14 | U10 |
| 17 | `EN_+3V3_VDD_SW` | PE15 | U8 |
| 19 | `EN_+5V0_PA1` | PG0 | U14 |
| 12, 14, 16, 18, 20 | GND | — | — |

Firmware enable sequence **as coded in the original** ("not executed on hardware") (source: `power_rails.md` §3, copied):

| Step | Action | Delay after | Source |
|---|---|---|---|
| F0 | `HAL_Delay(180000)` (3 min) then AD9523 RESET low | — | `main.cpp:1237-1238` |
| F1 | `EN_+1V8_CLOCK` high | 100 ms | `main.cpp:1241-1242` |
| F2 | `EN_+3V3_CLOCK` high; AD9523 RESET high; `configure_ad9523()` | 100 ms + 100 ms | `main.cpp:1243-1267` |
| F3 | `EN_+1V0_FPGA` high | 100 ms | `main.cpp:1271-1272` |
| F4 | `EN_+1V8_FPGA` high | 100 ms | `main.cpp:1273-1274` |
| F5 | `EN_+3V3_FPGA` high | 100 ms | `main.cpp:1275-1276` |
| F6 | DIG_3 (PD11) low "mixers off"; `EN_+3V3_ADAR12` + `EN_+3V3_ADAR34` high | 500 ms | `main.cpp:1483-1487` |
| F7 | `EN_+5V0_ADAR` high (→ −5 V ADAR rails) | 500 ms | `main.cpp:1488-1489` |
| F8 | `EN_+3V3_VDD_SW` high | 2 ms | `ADAR1000_Manager.cpp:51-52` (`powerUpSystem()`; whether `systemPowerUpSequence()` reaches it via `initializeADTR1107Sequence()` is UNVERIFIED) |
| F9 | `EN_+3V3_SW` high (→ −3V3_SW) | 2 ms | `ADAR1000_Manager.cpp:54-55` |
| F10 | DAC5578 VG codes written, LDAC pulsed, then `EN/DIS_RFPA_VDD` high (22 V drain) | — | `main.cpp:1560-1601` |
| never | `EN_+3V3_ADTR`, `EN_+5V0_PA1/2/3`, `EN_+5V5_PA` | — | no `GPIO_PIN_SET` write anywhere under `9_Firmware/9_1_Microcontroller/` |
| power-down | ADAR RX mode → `EN_+5V0_PA1..3` low → PA bias safe → `EN_+3V3_ADTR` low → LNA bias 0 → `EN_+3V3_VDD_SW`, `EN_+3V3_SW` low (10 ms steps) | 10 ms | `main.cpp:372-409` |

What the BETA changes in this sequence (D-11; source: `beta/stm32/DECISIONS.md` D-11 and `CHANGELOG.md` §2 `main.cpp` rows 380-382, 403-406, 1560-1562, 1600-1601): (a) finding — `EN_+5V5_PA` (PG3) "was **never** driven high — the OPA4703 VG buffers were unpowered while `main.cpp:1583-1601` 'programmed' VG and then enabled the 22 V drain"; (b) `EN_+3V3_ADTR` and `EN_+5V0_PA1/2/3` **are** asserted, but through raw pin numbers in `ADAR1000_Manager.cpp` (`initializeADTR1107Sequence()`, `setADTR1107Mode()`, `enable/disablePASupplies()`, `enable/disableLNASupplies()`), in the xlsx order VDD_SW → VSS_SW → CTRL → VGG → VDD_PA/VDD_LNA — kept, re-expressed with `main.h` macros; (c) power-down never removed the 22 V drain. Decisions: enable `+5V5_PA` 100 ms before the first DAC write; 20 ms VG settle before `EN/DIS_RFPA_VDD`; on power-down drop VD first (`EN_DIS_RFPA_VDD` LOW + 10 ms), then PA 5 V, LNA, switch rails, and `+5V5_PA` last. "Delays are conservative estimates, **not measured**. The IDQ servo loop (`main.cpp:1628-1656`) and the 1.68 A target were not touched. The external 22 V source and its switch are not in CAD (K4)."

The "never" row of the original therefore reads, in the beta: `+5V5_PA` is now enabled before VG programming (D-11), while `+3V3_ADTR`/`+5V0_PA_x` were already enabled by `ADAR1000_Manager` (finding b). Observation MAN-12-1: the CONFLICT rows of `power_rails.md` §1 (`+3V3_ADTR`, `+5V0_PA_1..3`, `+5V5_PA`) were written before finding (b); the register has not been updated and still states "firmware never enables the LNA supply". The bench verification in chapter 16 (Step 16.2) is the only way to settle the actual order.

## 12.7 USB protocol

### Settings packet (host → firmware)

Start flag `17 2E 9E ED` = `[23, 46, 158, 237]` (source: `USBHandler.cpp:38`, quoted in `beta/gui/README.md` "Protocol facts"), followed by the 82-byte packet `SET` + 3 × `>d` + `>I` + 6 × `>d` + `END`, all big-endian (source: `RadarSettings.cpp:23-120`; `beta/gui/aeris10_gui/protocol/settings_packet.py` lines 18-32, `PACKET_LENGTH = 82`). Field order (source: `settings_packet.py` `FIELDS`, lines 56-66; defaults from `beta/gui/aeris10_gui/model.py` `RadarSettings`):

| Offset | Size | Field | Format | Firmware limit (`RadarSettings.cpp:80-95` `validateSettings`) | Default (`model.py`) |
|---|---|---|---|---|---|
| 0 | 3 | marker | `SET` | must be at buffer offset 0 after the flag (`USBHandler.cpp:70`) | — |
| 3 | 8 | `system_frequency` | `>d` | 1e9 … 100e9 Hz | 10.0e9 |
| 11 | 8 | `chirp_duration_1` | `>d` | 1e-6 … 1000e-6 s | 30.0e-6 |
| 19 | 8 | `chirp_duration_2` | `>d` | 0.1e-6 … 10e-6 s | 0.5e-6 |
| 27 | 4 | `chirps_per_position` | `>I` | 1 … 256 | 32 |
| 31 | 8 | `freq_min` | `>d` | 1e6 … 100e6 Hz | 10.0e6 |
| 39 | 8 | `freq_max` | `>d` | > freq_min, ≤ 100e6 Hz | 30.0e6 |
| 47 | 8 | `prf1` | `>d` | 100 … 10000 Hz | 1000.0 |
| 55 | 8 | `prf2` | `>d` | 100 … 10000 Hz | 2000.0 |
| 63 | 8 | `max_distance` | `>d` | 100 … 100000 m | 50000.0 |
| 71 | 8 | `map_size` | `>d` | 1000 … 200000 m | 50000.0 |
| 79 | 3 | marker | `END` | — | — |

Framing rule (C5): the original GUI zero-padded every write to 64 bytes and the firmware copied the zeros into the settings buffer, so `SET` was never at offset 0; the beta parser "synchronises on `SET`, handles padded/unpadded/split frames" (source: `beta/stm32/README.md` §5 row C5; `CHANGELOG.md` `USBHandler.cpp` rows 59-93). There is no acknowledgement for a settings packet (source: `beta/gui/README.md`, assumption 7).

### Status and GPS (firmware → host)

Status string built by `getSystemStatusForGUI` (`main.cpp:807-877`), sent once with `CDC_Transmit_FS` at `main.cpp:1692`, no terminator (source: `beta/gui/aeris10_gui/protocol/status_text.py` docstring, copied):

```
System Status: NORMAL|LastError:%d|ErrorCount:%lu|
IMU:%.1f,%.1f,%.1f|GPS:%.6f,%.6f|ALT:%.1f|LO_TX:LOCKED|LO_RX:UNLOCKED|
T1:%.1f|...|T8:%.1f|[PA_AvgCurrent:%.2f|PA_Enabled:%d|]
BeamPos:%d|Azimuth:%d|ChirpCount:%d|
```

(`EMERGENCY_STOP` replaces `NORMAL`; the PA block appears only when `PowerAmplifier` is non-zero; `ChirpCount:%d|` is always the last field.) GPS: text `GPS:%.8f,%.8f,%.2f\r\n` on **UART3** (`gps_handler.cpp:45-62`) and the 30-byte binary `GPSB` frame over CDC — `'GPSB'` + lat (>d) + lon (>d) + alt (>f) + pitch (>f) + 16-bit sum of the first 28 bytes, big-endian (`gps_handler.cpp:65-119`). Known limitation carried into the status fields: `getSystemStatusForGUI()` "reports raw ADC codes as temperatures (no 0.64705 scale)" (source: `beta/stm32/README.md` §7 item 6).

### REG register commands (host → firmware → FPGA)

Text commands over the same CDC stream (source: `beta/stm32/DECISIONS.md` D-17, copied): `REG W <addr> <value>` / `REG R <addr>` → reply `REG 0x%04X 0x%08X\r\n` (a write echoes the written value after the ack) or `REG ERR\r\n` on syntax error, NACK, busy or SPI error. Numbers `0x` hex or decimal; keyword `REG` upper-case at byte 0 of the transfer, `W/R` either case; **one command per USB transfer**; the firmware holds **one command slot** — a second `REG` before execution is dropped, so the host waits for the reply. The line is captured in the OTG_FS ISR (`CDC_Receive_FS` → `USBHandler::captureTextCommand`) and executed from the main loop right after `HostBridge_Poll()` (`main.cpp:1713-1726` in the beta) because SPI1 is shared with the ADAR1000 path; the transport refuses (`REG ERR`) while a frame read is active or any ADAR1000 CS is low. Text detection is suppressed while a synchronised binary settings packet is being assembled (test T10).

SPI side towards the FPGA, bridge command set v2 (source: `beta/stm32/DECISIONS.md` D-18): write = 8 clocked bytes `02 a0 a1 d0 d1 d2 d3 00`, ack `0xA2` expected on MISO during the 8th byte; read = 7 bytes `03 a0 a1 00 00 00 00`, data little-endian in bytes 3..6; status = 9 bytes `04` + 8 reply bytes (status u16, version u16, frames u16, reserved u16, LE; u16 widths **assumed**); `0xEE` in the ack position = unknown command → NACK. "**The beta FPGA RTL (`beta/fpga/rtl/host_bridge_spi.v`) does not implement 0x02..0x04 yet** … STM32 side is ready, end-to-end untested."

### Bridge-frame forwarding (FPGA → firmware → host, option B)

The firmware waits for DRDY (EXTI on PD14 = DIG_6), pulls `FPGA_CS_N` (PD13 = DIG_5, reconfigured as output) low, clocks command byte `0x01` and reads one frame over SPI1 (mode 0, MSB first; the beta keeps the ADAR1000 setting of 6.75 MHz → ≈ 2.5 ms per frame), CRC-checks it and forwards it **unchanged** over CDC with `CDC_Transmit_FS`, interleaved with the status strings (source: `beta/stm32/CHANGELOG.md`, "host-link option B (DSN-LINK-01)"; `engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md` §5). Frame layout (little-endian) (source: `HOST_LINK_DESIGN.md` §5, copied):

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | sync `0xA5 0x5A` |
| 2 | 1 | version = 1 |
| 3 | 1 | flags (bit0 = long-chirp set, bit1 = overflow since last frame) |
| 4 | 2 | sequence number |
| 6 | 1 | azimuth index (1..50) |
| 7 | 1 | elevation index (1..31) |
| 8 | 2 | chirp count |
| 10 | 1 | n_range = 64 |
| 11 | 1 | n_doppler = 32 |
| 12 | 2 | n_det (≤ 32) |
| 14 | 2 | reserved |
| 16 | 2048 | magnitude map, uint8 = 8·log2(|I|+|Q|) saturated, range-major |
| 2064 | 3·n_det | detections: range u8, doppler u8, mag u8 |
| end | 2 | CRC-16/CCITT-FALSE over bytes 0..end-1 |

Firmware rule: "the firmware must not start an ADAR1000 transaction while `HostBridge_Busy()`" (source: `beta/stm32/CHANGELOG.md`, option B entry). Build after this change: 0 errors, RAM 17 480 B (5.33 %), FLASH 93 276 B (8.90 %).

## 12.8 USB descriptors and CDC configuration

(source: `beta/stm32/CUBEMX_SETTINGS.md` §4–§5): USB_OTG_FS **Device_Only**, PA11 DM / PA12 DP (AF10, very high speed), VBUS sensing off, SOF off, low-power off, LPM off, PA10 (ID) unassigned (D-07); CDC (VCP) with `USBD_MAX_NUM_INTERFACES 1`, `USBD_SELF_POWERED 1`; descriptors VID 0x0483, PID 0x5740, LANGID 0x409 — **PLACEHOLDER (D-09)**, chosen "only because `GUI_V5.py:323-330` enumerates on that list"; serial number = STM32 96-bit UID; FIFO Rx 0x80 / Tx EP0 0x40 / Tx EP1 0x80 words; `APP_RX_DATA_SIZE 2048`, `APP_TX_DATA_SIZE 2048`; OTG_FS interrupt priority 0/0 (D-08); user code to re-insert after a CubeMX regeneration: `AERIS_USB_OnReceive(Buf, *Len);` in `usbd_cdc_if.c` `CDC_Receive_FS()` USER CODE 6 (D-10).

## 12.9 Flashing and what remains

Flash command recorded for the bring-up (source: `beta/stm32/README.md` §7 item 2): `STM32_Programmer_CLI -c port=SWD -w beta/stm32/build_out/aeris10_fw.elf -v -rst` (SWD on PA13/PA14; SWO PB3 on the schematic — `CUBEMX_SETTINGS.md` §3). The bring-up checks themselves are Steps 16.1–16.2 and 16.8.

Unresolved / remaining work (source: `beta/stm32/README.md` §7, condensed, numbering kept): (1) regenerate the CubeMX project from `CUBEMX_SETTINGS.md` and diff the generated `usbd_conf.c`, `usbd_desc.c`, `usbd_cdc_if.c`, `usb_device.c`, startup and linker script against the hand-written files; let CubeMX recompute the I2C TIMINGR (D-03) and confirm the clock tree (D-01/D-02); (2) hardware bring-up per chapter 16; (3) ADAR1000 phase accuracy on hardware; FPGA implementation of bridge commands 0x02..0x04 and an end-to-end `REG` test; (4) ADAR1000 SCLK limit and FPGA level-shifter bandwidth; AD9523/ADF4382 register-level correctness; ADF4382 `DELADJ` "PWM" is a stub (`adf4382a_manager.c:433-460`); (5) VBUS wiring to PA9 (D-07); production VID/PID (D-09); USB interrupt priority policy (D-08); (6) `main.cpp` logic not touched: 180 s OCXO wait at boot; `last_check` reused for the temperature timer (`main.cpp:1774`); raw ADC codes reported as temperatures; health-check thresholds; IDQ servo exit conditions; (7) I/D cache stays disabled, MPU background region as generated; (8) PA drain 22 V source/switch and stepper supply are not in CAD (K4); (9) static analysis (cppcheck) and `-fstack-usage` review not yet done.

Acceptance criteria touched by this chapter (source: `docs/TESTING/ACCEPTANCE_CRITERIA.md`): AC-S1…AC-S5 are recorded NOT MET against the **original** tree; AC-X2 ("beta firmware compiles and links; host tests pass") is **MET (BETA)**; AC-S6/AC-S7 (physical) are NOT RUN.
