/*
 * host_bridge_proto.h - HAL-free protocol layer of the FPGA<->STM32 SPI bridge, command set v2
 * (engineering/DESIGN/HOST_LINK/HOST_LINK_DESIGN.md §7) and the ASCII host command "REG ...".
 *
 * The transport is injected (hb_xfer_fn) so this file is unit-tested on the host
 * (beta/stm32/tests/test_host_bridge_cmds.c); host_bridge.c supplies the HAL SPI1 transport with
 * the FPGA_CS_N / busy guard shared with the frame read.
 *
 * Byte sequences (all MSB-first SPI mode 0, FPGA_CS_N low for the whole sequence; '<-' = FPGA on MISO):
 *   0x02 write: 02 a0 a1 d0 d1 d2 d3 xx            <- byte 7 = 0xA2 (ack); 0xEE = unknown command
 *   0x03 read : 03 a0 a1 xx xx xx xx               <- bytes 3..6 = d0 d1 d2 d3 (little-endian)
 *   0x04 stat : 04 xx*8                            <- bytes 1..8 = status u16, fw/rtl version u16,
 *                                                     frames produced u16, reserved u16 (all LE)
 *   addr = word address a0 | a1<<8 (map: radar_control_regs.v, §7 table)
 * ASSUMPTION (D-18): §7 says "status word" without a width; 8 bytes = 4 x u16 is used here.
 * STATUS: implemented on both sides since 2026-10-09 (beta/fpga/rtl/host_bridge_spi.v command set v2, register map 0x00..0x10; status word also carries bit4 = packer overflow).
 */
#ifndef HOST_BRIDGE_PROTO_H
#define HOST_BRIDGE_PROTO_H
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#endif

#define HB_CMD_READ_FRAME  0x01u
#define HB_CMD_WRITE_REG   0x02u
#define HB_CMD_READ_REG    0x03u
#define HB_CMD_STATUS      0x04u
#define HB_ACK             0xA2u
#define HB_NAK_UNKNOWN     0xEEu

#define HB_WRITE_REG_LEN   8u
#define HB_READ_REG_LEN    7u
#define HB_STATUS_LEN      9u

/* status word bits (§7) */
#define HB_ST_FRAME_READY  (1u << 0)
#define HB_ST_CS_CONFLICT  (1u << 1)
#define HB_ST_FIFO_OVF     (1u << 2)
#define HB_ST_CAL_LOCK     (1u << 3)

typedef struct {
    uint16_t status;      /* HB_ST_* bits */
    uint16_t version;     /* fw/rtl version */
    uint16_t frames;      /* frames produced */
    uint16_t reserved;
} hb_status_t;

enum hb_err {
    HB_OK        = 0,
    HB_ERR_XFER  = -1,   /* transport failure (HAL error/timeout) */
    HB_ERR_NACK  = -2,   /* write not acknowledged (0xA2 missing; 0xEE = unknown command) */
    HB_ERR_BUSY  = -3,   /* a frame read is in progress */
    HB_ERR_PARAM = -4,   /* bad argument / ASCII syntax */
};

/* Full-duplex transfer of len bytes with CS asserted for the whole sequence. Return 0 on success. */
typedef int (*hb_xfer_fn)(void *ctx, const uint8_t *tx, uint8_t *rx, uint16_t len);

int hb_proto_write_reg(hb_xfer_fn xfer, void *ctx, uint16_t addr, uint32_t value);
int hb_proto_read_reg (hb_xfer_fn xfer, void *ctx, uint16_t addr, uint32_t *value);
int hb_proto_status   (hb_xfer_fn xfer, void *ctx, hb_status_t *st);

/* ASCII host command: "REG W <addr> <value>" | "REG R <addr>"  (numbers: 0x-prefixed hex or decimal;
 * keyword "REG" upper-case (it is what USBHandler detects), W/R letter case-insensitive; trailing CR/LF ignored). */
typedef struct {
    bool     write;
    uint16_t addr;
    uint32_t value;
} hb_cmd_t;

int  hb_cmd_parse(const char *line, hb_cmd_t *out);                 /* HB_OK or HB_ERR_PARAM */
bool hb_cmd_is_text_command(const uint8_t *data, uint32_t len);     /* true if data starts with "REG" */

/* Parse + execute + format the reply ("REG 0x%04X 0x%08X\r\n" or "REG ERR\r\n").
 * Returns the hb_err code of the operation; reply is always written (truncated to cap). */
int hb_cmd_execute(const char *line, hb_xfer_fn xfer, void *ctx, char *reply, size_t cap);

#ifdef __cplusplus
}
#endif
#endif /* HOST_BRIDGE_PROTO_H */
