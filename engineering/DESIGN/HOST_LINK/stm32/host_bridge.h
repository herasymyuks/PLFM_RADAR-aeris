/* host_bridge.h — AERIS-10 host-link option B (DSN-LINK-01): FPGA → STM32 SPI bridge → USB CDC.
 * BETA: compiles with the beta firmware; not run on hardware.
 * Lines (existing nets): STM32 SPI1 (PA5/PA6/PA7) ↔ FPGA J16/H13/G14; DIG_5 = PD13 (FPGA_CS_N, output),
 * DIG_6 = PD14 (DRDY, EXTI14 rising), DIG_7 = PD15 (spare input). Frame format: HOST_LINK_DESIGN.md §5. */
#ifndef HOST_BRIDGE_H
#define HOST_BRIDGE_H
#include <stdint.h>
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HB_FRAME_MAX   (16u + 2048u + 3u * 32u + 2u)   /* 2162 bytes incl. CRC */
#define HB_CMD_READ    0x01u
void     HostBridge_Init(void);          /* configures PD13/PD14/PD15 and EXTI14; call after MX_SPI1_Init()/MX_GPIO_Init() */
void     HostBridge_Poll(void);          /* call from the main loop: reads a frame when DRDY was seen, forwards it over CDC */
bool     HostBridge_Busy(void);          /* true while a SPI1 bridge transfer is in progress (do not touch SPI1/ADAR1000) */
uint32_t HostBridge_FramesForwarded(void);
uint32_t HostBridge_FramesDropped(void);
uint32_t HostBridge_CrcErrors(void);
uint16_t HostBridge_Crc16(const uint8_t *data, uint32_t len);   /* CRC-16/CCITT-FALSE */
#ifdef __cplusplus
}
#endif
#endif
