/* host_bridge_proto.c - see host_bridge_proto.h. HAL-free; BETA. */
#include "host_bridge_proto.h"
#include <string.h>
#include <stdio.h>
#include <ctype.h>

int hb_proto_write_reg(hb_xfer_fn xfer, void *ctx, uint16_t addr, uint32_t value)
{
    uint8_t tx[HB_WRITE_REG_LEN] = {
        HB_CMD_WRITE_REG,
        (uint8_t)(addr & 0xFFu), (uint8_t)(addr >> 8),
        (uint8_t)(value & 0xFFu), (uint8_t)((value >> 8) & 0xFFu),
        (uint8_t)((value >> 16) & 0xFFu), (uint8_t)((value >> 24) & 0xFFu),
        0x00 /* clocks the ack in */
    };
    uint8_t rx[HB_WRITE_REG_LEN] = {0};
    if (!xfer) return HB_ERR_PARAM;
    if (xfer(ctx, tx, rx, HB_WRITE_REG_LEN) != 0) return HB_ERR_XFER;
    return (rx[7] == HB_ACK) ? HB_OK : HB_ERR_NACK;
}

int hb_proto_read_reg(hb_xfer_fn xfer, void *ctx, uint16_t addr, uint32_t *value)
{
    uint8_t tx[HB_READ_REG_LEN] = { HB_CMD_READ_REG, (uint8_t)(addr & 0xFFu), (uint8_t)(addr >> 8), 0, 0, 0, 0 };
    uint8_t rx[HB_READ_REG_LEN] = {0};
    if (!xfer || !value) return HB_ERR_PARAM;
    if (xfer(ctx, tx, rx, HB_READ_REG_LEN) != 0) return HB_ERR_XFER;
    *value = (uint32_t)rx[3] | ((uint32_t)rx[4] << 8) | ((uint32_t)rx[5] << 16) | ((uint32_t)rx[6] << 24);
    return HB_OK;
}

int hb_proto_status(hb_xfer_fn xfer, void *ctx, hb_status_t *st)
{
    uint8_t tx[HB_STATUS_LEN] = { HB_CMD_STATUS, 0, 0, 0, 0, 0, 0, 0, 0 };
    uint8_t rx[HB_STATUS_LEN] = {0};
    if (!xfer || !st) return HB_ERR_PARAM;
    if (xfer(ctx, tx, rx, HB_STATUS_LEN) != 0) return HB_ERR_XFER;
    st->status   = (uint16_t)(rx[1] | (rx[2] << 8));
    st->version  = (uint16_t)(rx[3] | (rx[4] << 8));
    st->frames   = (uint16_t)(rx[5] | (rx[6] << 8));
    st->reserved = (uint16_t)(rx[7] | (rx[8] << 8));
    return HB_OK;
}

/* ---- ASCII command ---- */

static const char *skip_ws(const char *p) { while (*p == ' ' || *p == '\t') p++; return p; }

/* 0x-prefixed hex or decimal; returns pointer after the number or NULL. */
static const char *parse_u32(const char *p, uint32_t *out)
{
    uint32_t v = 0; int n = 0;
    p = skip_ws(p);
    if (p[0] == '0' && (p[1] == 'x' || p[1] == 'X')) {
        p += 2;
        while (isxdigit((unsigned char)*p)) {
            if (n++ >= 8) return NULL;
            char c = (char)toupper((unsigned char)*p++);
            v = (v << 4) | (uint32_t)(c >= 'A' ? c - 'A' + 10 : c - '0');
        }
    } else {
        while (isdigit((unsigned char)*p)) {
            if (v > 0xFFFFFFFFu / 10u) return NULL;
            v = v * 10u + (uint32_t)(*p++ - '0');
            n++;
        }
    }
    if (n == 0) return NULL;
    if (*p != '\0' && *p != ' ' && *p != '\t' && *p != '\r' && *p != '\n') return NULL;
    *out = v;
    return p;
}

bool hb_cmd_is_text_command(const uint8_t *data, uint32_t len)
{
    return data && len >= 3 && data[0] == 'R' && data[1] == 'E' && data[2] == 'G';
}

int hb_cmd_parse(const char *line, hb_cmd_t *out)
{
    if (!line || !out) return HB_ERR_PARAM;
    const char *p = skip_ws(line);
    if (strncmp(p, "REG", 3) != 0) return HB_ERR_PARAM;
    p = skip_ws(p + 3);
    char op = (char)toupper((unsigned char)*p);
    if (op != 'W' && op != 'R') return HB_ERR_PARAM;
    p++;
    if (*p != ' ' && *p != '\t') return HB_ERR_PARAM;
    uint32_t addr = 0, val = 0;
    p = parse_u32(p, &addr);
    if (!p || addr > 0xFFFFu) return HB_ERR_PARAM;
    memset(out, 0, sizeof *out);
    out->addr = (uint16_t)addr;
    if (op == 'W') {
        p = parse_u32(p, &val);
        if (!p) return HB_ERR_PARAM;
        out->write = true;
        out->value = val;
    }
    p = skip_ws(p);
    if (*p != '\0' && *p != '\r' && *p != '\n') return HB_ERR_PARAM;   /* trailing junk */
    return HB_OK;
}

int hb_cmd_execute(const char *line, hb_xfer_fn xfer, void *ctx, char *reply, size_t cap)
{
    hb_cmd_t c;
    int rc = hb_cmd_parse(line, &c);
    uint32_t v = 0;
    if (rc == HB_OK) {
        if (c.write) {
            rc = hb_proto_write_reg(xfer, ctx, c.addr, c.value);
            v = c.value;
        } else {
            rc = hb_proto_read_reg(xfer, ctx, c.addr, &v);
        }
    }
    if (reply && cap) {
        if (rc == HB_OK) snprintf(reply, cap, "REG 0x%04X 0x%08lX\r\n", (unsigned)c.addr, (unsigned long)v);
        else             snprintf(reply, cap, "REG ERR\r\n");
    }
    return rc;
}
