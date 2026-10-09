/* host_bridge.h — AERIS-10 host-link option B (DSN-LINK-01): FPGA → STM32 SPI bridge → USB CDC.
 * BETA: compiles with the beta firmware; not run on hardware.
 * Lines (existing nets): STM32 SPI1 (PA5/PA6/PA7) ↔ FPGA J16/H13/G14; DIG_5 = PD13 (FPGA_CS_N, output),
 * DIG_6 = PD14 (DRDY, EXTI14 rising), DIG_7 = PD15 (spare input). Frame format: HOST_LINK_DESIGN.md §5. */
#ifndef HOST_BRIDGE_H
#define HOST_BRIDGE_H
#include <stdint.h>
#include <stdbool.h>
#include "host_bridge_proto.h"   /* command set v2 (HOST_LINK_DESIGN.md §7) */
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
/* Command set v2 (BETA, D-17). Return HB_OK or a negative hb_err. They refuse with HB_ERR_BUSY while a
 * frame read is in progress and use the same FPGA_CS_N handling; call from the main loop only (not ISR). */
int      HostBridge_WriteReg(uint16_t addr, uint32_t val);     /* 0x02, expects ack 0xA2 */
int      HostBridge_ReadReg(uint16_t addr, uint32_t *val);     /* 0x03 */
int      HostBridge_Status(hb_status_t *st);                   /* 0x04 */
/* Executes one ASCII "REG W/R ..." line and writes the reply ("REG <addr> <value>\r\n" / "REG ERR\r\n"). */
int      HostBridge_ExecuteTextCommand(const char *line, char *reply, size_t cap);
uint16_t HostBridge_Crc16(const uint8_t *data, uint32_t len);   /* CRC-16/CCITT-FALSE */
#ifdef __cplusplus
}
#endif
#endif
