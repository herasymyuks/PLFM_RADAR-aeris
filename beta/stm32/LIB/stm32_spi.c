/*
 * BETA no-OS SPI platform layer over STM32 HAL (AERIS-10). See stm32_spi.h.
 */
#include "stm32_spi.h"
#include "no_os_error.h"
#include "main.h"
#include <stdlib.h>

struct stm32_spi_cs {
	GPIO_TypeDef *port;
	uint16_t pin;
};

/* Index -> GPIO, all taken from main.h (active-low chip selects). */
static const struct stm32_spi_cs cs_table[STM32_SPI_CS_COUNT] = {
	[STM32_SPI_CS_AD9523]     = { AD9523_CS_GPIO_Port,     AD9523_CS_Pin },
	[STM32_SPI_CS_ADF4382_TX] = { ADF4382_TX_CS_GPIO_Port, ADF4382_TX_CS_Pin },
	[STM32_SPI_CS_ADF4382_RX] = { ADF4382_RX_CS_GPIO_Port, ADF4382_RX_CS_Pin },
};

uint32_t stm32_spi_prescaler_for(uint32_t pclk_hz, uint32_t max_speed_hz)
{
	static const uint32_t presc_reg[8] = {
		SPI_BAUDRATEPRESCALER_2,   SPI_BAUDRATEPRESCALER_4,
		SPI_BAUDRATEPRESCALER_8,   SPI_BAUDRATEPRESCALER_16,
		SPI_BAUDRATEPRESCALER_32,  SPI_BAUDRATEPRESCALER_64,
		SPI_BAUDRATEPRESCALER_128, SPI_BAUDRATEPRESCALER_256,
	};
	uint32_t div = 2;
	for (int i = 0; i < 8; i++, div <<= 1) {
		if (max_speed_hz != 0 && (pclk_hz / div) <= max_speed_hz)
			return presc_reg[i];
	}
	return SPI_BAUDRATEPRESCALER_256;
}

static void cs_set(const struct no_os_spi_desc *desc, GPIO_PinState state)
{
	if (desc->chip_select < STM32_SPI_CS_COUNT)
		HAL_GPIO_WritePin(cs_table[desc->chip_select].port,
				  cs_table[desc->chip_select].pin, state);
}

int32_t stm32_spi_init(struct no_os_spi_desc **desc,
		       const struct no_os_spi_init_param *param)
{
	if (!desc || !param || !param->extra)
		return -EINVAL;
	if (param->chip_select >= STM32_SPI_CS_COUNT)
		return -EINVAL;

	*desc = calloc(1, sizeof(**desc));
	if (!*desc)
		return -ENOMEM;

	/* platform handle (HAL SPI_HandleTypeDef*) travels in extra */
	(*desc)->extra = param->extra;
	(*desc)->device_id = param->device_id;
	(*desc)->max_speed_hz = param->max_speed_hz;
	(*desc)->mode = param->mode;
	(*desc)->bit_order = param->bit_order;
	(*desc)->chip_select = param->chip_select;

	/* Apply the requested bus clock: SPI1/SPI4 are on APB2 (PCLK2). Re-init only
	 * when the prescaler actually changes (HAL_SPI_Init is idempotent otherwise). */
	SPI_HandleTypeDef *hspi = (SPI_HandleTypeDef *)param->extra;
	uint32_t presc = stm32_spi_prescaler_for(HAL_RCC_GetPCLK2Freq(),
						 param->max_speed_hz);
	if (hspi->Init.BaudRatePrescaler != presc) {
		hspi->Init.BaudRatePrescaler = presc;
		if (HAL_SPI_Init(hspi) != HAL_OK) {
			free(*desc);
			*desc = NULL;
			return -EIO;
		}
	}

	/* CS idle high */
	cs_set(*desc, GPIO_PIN_SET);
	return 0;
}

int32_t stm32_spi_write_and_read(struct no_os_spi_desc *desc,
				 uint8_t *data,
				 uint16_t bytes_number)
{
	if (!desc || !data || bytes_number == 0)
		return -EINVAL;

	SPI_HandleTypeDef *hspi = (SPI_HandleTypeDef *)desc->extra;
	if (!hspi)
		return -EINVAL;

	cs_set(desc, GPIO_PIN_RESET);
	HAL_StatusTypeDef st = HAL_SPI_TransmitReceive(hspi, data, data,
						       bytes_number, 200);
	cs_set(desc, GPIO_PIN_SET);

	return (st == HAL_OK) ? 0 : -EIO;
}

int32_t stm32_spi_remove(struct no_os_spi_desc *desc)
{
	if (!desc)
		return -EINVAL;
	cs_set(desc, GPIO_PIN_SET);
	free(desc);
	return 0;
}

const struct no_os_spi_platform_ops stm32_spi_ops = {
	.init = &stm32_spi_init,
	.write_and_read = &stm32_spi_write_and_read,
	.remove = &stm32_spi_remove,
};
