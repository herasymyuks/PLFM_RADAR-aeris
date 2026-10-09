/*
 * Host-side unit test: bridge command set v2 byte sequences (Core/Src/host_bridge_proto.c) with a mock
 * SPI transport, ack/err handling, and the ASCII "REG" command parser/executor.
 */
#include "../Core/Inc/host_bridge_proto.h"
#include <stdio.h>
#include <string.h>

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

/* ---- mock transport: records the last TX frame, replies from a scripted RX frame ---- */
static uint8_t  last_tx[32]; static uint16_t last_len; static int calls;
static uint8_t  scripted_rx[32]; static int fail_xfer;
static int mock_xfer(void *ctx, const uint8_t *tx, uint8_t *rx, uint16_t len)
{
    (void)ctx; calls++;
    if (fail_xfer) return -1;
    memcpy(last_tx, tx, len); last_len = len;
    memcpy(rx, scripted_rx, len);
    return 0;
}
static void script(const uint8_t *rx, size_t n) { memset(scripted_rx, 0, sizeof scripted_rx); memcpy(scripted_rx, rx, n); }

int main(void)
{
    printf("T1 0x02 write: 8 bytes, addr/data little-endian, ack 0xA2 in byte 7\n");
    { const uint8_t rx[8] = {0,0,0,0,0,0,0,HB_ACK}; script(rx, 8);
      CHECK(hb_proto_write_reg(mock_xfer, NULL, 0x0004, 0x11223344) == HB_OK);
      const uint8_t exp[8] = {0x02, 0x04, 0x00, 0x44, 0x33, 0x22, 0x11, 0x00};
      CHECK(last_len == 8 && memcmp(last_tx, exp, 8) == 0);
      /* 16-bit address high byte */
      CHECK(hb_proto_write_reg(mock_xfer, NULL, 0xBEEF, 1) == HB_OK);
      CHECK(last_tx[1] == 0xEF && last_tx[2] == 0xBE); }

    printf("T2 0x02 write without ack / with 0xEE (unknown command) / transport failure\n");
    { const uint8_t rx[8] = {0}; script(rx, 8);
      CHECK(hb_proto_write_reg(mock_xfer, NULL, 1, 2) == HB_ERR_NACK);
      const uint8_t rx2[8] = {0,0,0,0,0,0,0,HB_NAK_UNKNOWN}; script(rx2, 8);
      CHECK(hb_proto_write_reg(mock_xfer, NULL, 1, 2) == HB_ERR_NACK);
      fail_xfer = 1; CHECK(hb_proto_write_reg(mock_xfer, NULL, 1, 2) == HB_ERR_XFER); fail_xfer = 0;
      CHECK(hb_proto_write_reg(NULL, NULL, 1, 2) == HB_ERR_PARAM); }

    printf("T3 0x03 read: 7 bytes, value from bytes 3..6 little-endian\n");
    { const uint8_t rx[7] = {0,0,0, 0x78, 0x56, 0x34, 0x12}; script(rx, 7); uint32_t v = 0;
      CHECK(hb_proto_read_reg(mock_xfer, NULL, 0x0005, &v) == HB_OK);
      const uint8_t exp[7] = {0x03, 0x05, 0x00, 0, 0, 0, 0};
      CHECK(last_len == 7 && memcmp(last_tx, exp, 7) == 0);
      CHECK(v == 0x12345678u);
      fail_xfer = 1; CHECK(hb_proto_read_reg(mock_xfer, NULL, 5, &v) == HB_ERR_XFER); fail_xfer = 0;
      CHECK(hb_proto_read_reg(mock_xfer, NULL, 5, NULL) == HB_ERR_PARAM); }

    printf("T4 0x04 status: 9 bytes, four little-endian u16 fields\n");
    { const uint8_t rx[9] = {0, 0x09, 0x00, 0x02, 0x01, 0x10, 0x27, 0xAA, 0x55}; script(rx, 9); hb_status_t st;
      CHECK(hb_proto_status(mock_xfer, NULL, &st) == HB_OK);
      CHECK(last_len == 9 && last_tx[0] == 0x04);
      for (int i = 1; i < 9; i++) CHECK(last_tx[i] == 0);
      CHECK(st.status == 0x0009 && (st.status & HB_ST_FRAME_READY) && (st.status & HB_ST_CAL_LOCK) && !(st.status & HB_ST_CS_CONFLICT));
      CHECK(st.version == 0x0102 && st.frames == 10000 && st.reserved == 0x55AA); }

    printf("T5 ASCII parser: hex and decimal, case, whitespace, errors\n");
    { hb_cmd_t c;
      CHECK(hb_cmd_parse("REG W 0x0004 0x11223344", &c) == HB_OK && c.write && c.addr == 4 && c.value == 0x11223344);
      CHECK(hb_cmd_parse("REG W 4 287454020\r\n", &c) == HB_OK && c.write && c.addr == 4 && c.value == 0x11223344);
      CHECK(hb_cmd_parse("REG r 0x5", &c) == HB_OK && !c.write && c.addr == 5);   /* op letter case-insensitive */
      CHECK(hb_cmd_parse("reg r 0x5", &c) == HB_ERR_PARAM);   /* keyword must be upper-case "REG" (USBHandler detection) */
      CHECK(hb_cmd_parse("REG  R   7  ", &c) == HB_OK && c.addr == 7);
      CHECK(hb_cmd_parse("REG R 0x10000", &c) == HB_ERR_PARAM);        /* addr > 16 bit */
      CHECK(hb_cmd_parse("REG W 1", &c) == HB_ERR_PARAM);              /* missing value */
      CHECK(hb_cmd_parse("REG X 1", &c) == HB_ERR_PARAM);              /* bad op */
      CHECK(hb_cmd_parse("REG R 1 2", &c) == HB_ERR_PARAM);            /* trailing junk */
      CHECK(hb_cmd_parse("REG R 0xZZ", &c) == HB_ERR_PARAM);
      CHECK(hb_cmd_parse("SET", &c) == HB_ERR_PARAM);
      CHECK(hb_cmd_parse("REGW 1", &c) == HB_ERR_PARAM);
      CHECK(hb_cmd_is_text_command((const uint8_t *)"REG R 1", 7));
      CHECK(!hb_cmd_is_text_command((const uint8_t *)"SET", 3));
      CHECK(!hb_cmd_is_text_command((const uint8_t *)"RE", 2)); }

    printf("T6 execute: write -> REG <addr> <value>; read -> value from bus; errors -> REG ERR\n");
    { char reply[48];
      const uint8_t ack[8] = {0,0,0,0,0,0,0,HB_ACK}; script(ack, 8);
      CHECK(hb_cmd_execute("REG W 0x0 0x7", mock_xfer, NULL, reply, sizeof reply) == HB_OK);
      CHECK(strcmp(reply, "REG 0x0000 0x00000007\r\n") == 0);
      CHECK(last_tx[0] == 0x02 && last_tx[3] == 0x07);
      const uint8_t rd[7] = {0,0,0, 0xEF, 0xBE, 0xAD, 0xDE}; script(rd, 7);
      CHECK(hb_cmd_execute("REG R 0x0007", mock_xfer, NULL, reply, sizeof reply) == HB_OK);
      CHECK(strcmp(reply, "REG 0x0007 0xDEADBEEF\r\n") == 0);
      const uint8_t nak[8] = {0}; script(nak, 8);
      CHECK(hb_cmd_execute("REG W 1 1", mock_xfer, NULL, reply, sizeof reply) == HB_ERR_NACK);
      CHECK(strcmp(reply, "REG ERR\r\n") == 0);
      CHECK(hb_cmd_execute("REG Q 1", mock_xfer, NULL, reply, sizeof reply) == HB_ERR_PARAM);
      CHECK(strcmp(reply, "REG ERR\r\n") == 0);
      fail_xfer = 1;
      CHECK(hb_cmd_execute("REG R 1", mock_xfer, NULL, reply, sizeof reply) == HB_ERR_XFER);
      CHECK(strcmp(reply, "REG ERR\r\n") == 0);
      fail_xfer = 0;
      char tiny[6];
      hb_cmd_execute("REG R 1", mock_xfer, NULL, tiny, sizeof tiny);   /* truncation must stay NUL-terminated */
      CHECK(strlen(tiny) == 5); }

    printf("%s (%d failure(s), %d mock transfers)\n", failures ? "TEST FAILED" : "TEST PASSED", failures, calls);
    return failures ? 1 : 0;
}
