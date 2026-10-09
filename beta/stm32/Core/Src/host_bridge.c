/* host_bridge.c — see host_bridge.h.  BETA. */
#include "host_bridge.h"
#include "main.h"
#include "usbd_cdc_if.h"
#include <string.h>

extern SPI_HandleTypeDef hspi1;

#define HB_CS_PORT   GPIOD
#define HB_CS_PIN    GPIO_PIN_13      /* DIG_5 → FPGA H11 */
#define HB_DRDY_PORT GPIOD
#define HB_DRDY_PIN  GPIO_PIN_14      /* DIG_6 ← FPGA G12 */
#define HB_SPARE_PIN GPIO_PIN_15      /* DIG_7 ← FPGA H12 */
#define HB_SPI_TIMEOUT_MS 20u

static volatile bool s_drdy_seen = false;
static volatile bool s_busy = false;
static uint32_t s_forwarded = 0, s_dropped = 0, s_crc_err = 0;
static uint8_t  s_tx[HB_FRAME_MAX + 1];
static uint8_t  s_rx[HB_FRAME_MAX + 1];

uint16_t HostBridge_Crc16(const uint8_t *data, uint32_t len)
{
    uint16_t crc = 0xFFFFu;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; b++) crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
    }
    return crc;
}

void HostBridge_Init(void)
{
    GPIO_InitTypeDef g = {0};
    __HAL_RCC_GPIOD_CLK_ENABLE();
    HAL_GPIO_WritePin(HB_CS_PORT, HB_CS_PIN, GPIO_PIN_SET);         /* CS idle high */
    g.Pin = HB_CS_PIN; g.Mode = GPIO_MODE_OUTPUT_PP; g.Pull = GPIO_NOPULL; g.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(HB_CS_PORT, &g);
    g.Pin = HB_DRDY_PIN; g.Mode = GPIO_MODE_IT_RISING; g.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(HB_DRDY_PORT, &g);
    g.Pin = HB_SPARE_PIN; g.Mode = GPIO_MODE_INPUT; g.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(HB_DRDY_PORT, &g);
    HAL_NVIC_SetPriority(EXTI15_10_IRQn, 6, 0);
    HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
    memset(s_tx, 0, sizeof s_tx);
    s_tx[0] = HB_CMD_READ;
    s_drdy_seen = (HAL_GPIO_ReadPin(HB_DRDY_PORT, HB_DRDY_PIN) == GPIO_PIN_SET);
}

/* HAL weak callback — no other EXTI user in the beta firmware (checked: none defined). */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == HB_DRDY_PIN) s_drdy_seen = true;
}

bool HostBridge_Busy(void) { return s_busy; }
uint32_t HostBridge_FramesForwarded(void) { return s_forwarded; }
uint32_t HostBridge_FramesDropped(void) { return s_dropped; }
uint32_t HostBridge_CrcErrors(void) { return s_crc_err; }

static bool cdc_send_all(const uint8_t *buf, uint32_t len)
{
    /* CDC_Transmit_FS accepts a whole buffer (the class driver fragments into 64-byte packets);
       wait for the previous transfer with a bounded spin. */
    uint32_t t0 = HAL_GetTick();
    while (CDC_Transmit_FS((uint8_t *)buf, (uint16_t)len) == USBD_BUSY) {
        if (HAL_GetTick() - t0 > 50u) return false;
    }
    return true;
}

void HostBridge_Poll(void)
{
    if (!s_drdy_seen) return;
    s_drdy_seen = false;
    if (HAL_GPIO_ReadPin(HB_DRDY_PORT, HB_DRDY_PIN) != GPIO_PIN_SET) return;   /* glitch */
    s_busy = true;
    HAL_GPIO_WritePin(HB_CS_PORT, HB_CS_PIN, GPIO_PIN_RESET);
    /* command byte + fixed header; the header tells how many detection bytes follow */
    HAL_StatusTypeDef st = HAL_SPI_TransmitReceive(&hspi1, s_tx, s_rx, 1u + 16u, HB_SPI_TIMEOUT_MS);
    uint32_t total = 0;
    if (st == HAL_OK && s_rx[1] == 0xA5u && s_rx[2] == 0x5Au) {
        uint16_t n_det = (uint16_t)s_rx[1 + 12] | ((uint16_t)s_rx[1 + 13] << 8);
        if (n_det > 32u) n_det = 32u;
        total = 16u + 2048u + 3u * n_det + 2u;
        st = HAL_SPI_TransmitReceive(&hspi1, s_tx + 17, s_rx + 17, (uint16_t)(total - 16u), HB_SPI_TIMEOUT_MS);
    } else {
        st = HAL_ERROR;
    }
    HAL_GPIO_WritePin(HB_CS_PORT, HB_CS_PIN, GPIO_PIN_SET);
    s_busy = false;
    if (st != HAL_OK) { s_dropped++; return; }
    uint16_t crc_calc = HostBridge_Crc16(s_rx + 1, total - 2u);
    uint16_t crc_rx = (uint16_t)((uint16_t)s_rx[1 + total - 2u] << 8 | s_rx[1 + total - 1u]);
    if (crc_calc != crc_rx) { s_crc_err++; return; }
    if (cdc_send_all(s_rx + 1, total)) s_forwarded++; else s_dropped++;
}

/* ---- command set v2 (BETA, D-17): register access through the same CS / busy discipline ---- */
static int hb_hal_xfer(void *ctx, const uint8_t *tx, uint8_t *rx, uint16_t len)
{
    (void)ctx;
    if (s_busy) return -1;
    /* ADAR1000 chip selects must be high while FPGA_CS_N is low (option_b_signal_map.csv) */
    if ((GPIOA->ODR & (ADAR_1_CS_3V3_Pin | ADAR_2_CS_3V3_Pin | ADAR_3_CS_3V3_Pin | ADAR_4_CS_3V3_Pin)) !=
        (ADAR_1_CS_3V3_Pin | ADAR_2_CS_3V3_Pin | ADAR_3_CS_3V3_Pin | ADAR_4_CS_3V3_Pin)) return -1;
    s_busy = true;
    HAL_GPIO_WritePin(HB_CS_PORT, HB_CS_PIN, GPIO_PIN_RESET);
    HAL_StatusTypeDef st = HAL_SPI_TransmitReceive(&hspi1, (uint8_t *)tx, rx, len, HB_SPI_TIMEOUT_MS);
    HAL_GPIO_WritePin(HB_CS_PORT, HB_CS_PIN, GPIO_PIN_SET);
    s_busy = false;
    return (st == HAL_OK) ? 0 : -1;
}

int HostBridge_WriteReg(uint16_t addr, uint32_t val)
{
    if (s_busy) return HB_ERR_BUSY;
    return hb_proto_write_reg(hb_hal_xfer, NULL, addr, val);
}

int HostBridge_ReadReg(uint16_t addr, uint32_t *val)
{
    if (s_busy) return HB_ERR_BUSY;
    return hb_proto_read_reg(hb_hal_xfer, NULL, addr, val);
}

int HostBridge_Status(hb_status_t *st)
{
    if (s_busy) return HB_ERR_BUSY;
    return hb_proto_status(hb_hal_xfer, NULL, st);
}

int HostBridge_ExecuteTextCommand(const char *line, char *reply, size_t cap)
{
    return hb_cmd_execute(line, hb_hal_xfer, NULL, reply, cap);
}
