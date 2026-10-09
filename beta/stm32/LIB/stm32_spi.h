#ifndef _STM32_SPI_H_
#define _STM32_SPI_H_

/*
 * BETA no-OS SPI platform layer over STM32 HAL (AERIS-10).
 *
 * Changes vs. 9_Firmware/9_1_Microcontroller/9_1_1_C_Cpp_Libraries/stm32_spi.h
 * (see beta/stm32/CHANGELOG.md, DECISIONS.md D-05/D-06):
 *   - chip_select is a logical index resolved to a GPIO (port,pin) from main.h;
 *     the original ignored chip_select entirely and never toggled CS.
 *   - the SPI baud-rate prescaler is derived from max_speed_hz at init (the
 *     original stored max_speed_hz and never applied it: SPI ran at PCLK/2).
 *   - write_and_read matches the no_os_spi_platform_ops prototype (uint16_t).
 */

#include "no_os_spi.h"
#include "stm32f7xx_hal.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Logical chip-select indices for struct no_os_spi_init_param::chip_select.
 * GPIO assignment comes from main.h (schematic nets, docs/STM32/STM32_PROJECT_RECONSTRUCTION.md §3.3). */
enum stm32_spi_cs_index {
	STM32_SPI_CS_AD9523     = 0,	/* PF7  AD9523_CS      (SPI4) */
	STM32_SPI_CS_ADF4382_TX = 1,	/* PG14 ADF4382_TX_CS  (SPI4) */
	STM32_SPI_CS_ADF4382_RX = 2,	/* PG10 ADF4382_RX_CS  (SPI4) */
	STM32_SPI_CS_COUNT
};

extern const struct no_os_spi_platform_ops stm32_spi_ops;

/* Exposed for host-side unit tests: returns the SPI_BAUDRATEPRESCALER_x value
 * giving the highest bus clock <= max_speed_hz for the given peripheral clock,
 * or SPI_BAUDRATEPRESCALER_256 if even /256 is too fast. */
uint32_t stm32_spi_prescaler_for(uint32_t pclk_hz, uint32_t max_speed_hz);

#ifdef __cplusplus
}
#endif

#endif /* _STM32_SPI_H_ */
