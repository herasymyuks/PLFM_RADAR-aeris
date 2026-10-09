/*
 * Host-side unit test: AD9523 register table produced by ad9523_setup() for the
 * AERIS-10 platform data (copied from Core/Src/main.cpp configure_ad9523()).
 *
 * The real no-OS driver (LIB/ad9523.c) and SPI core (LIB/no_os_spi.c) are compiled
 * for the host; the platform layer is a mock that models the AD9523 register file:
 *   - 3-byte frames [R/W|addr_hi, addr_lo, data], one byte per transfer (ad9523_spi_write/read)
 *   - reads of READBACK_0 report VCXO ok + PLL1/PLL2 locked, READBACK_1 reports "calibration done"
 *     so that ad9523_calibrate()/ad9523_status() succeed and the whole setup path runs.
 * Checks: write-verify handshake, channel distribution registers for every output used by
 * the design (dividers / driver modes / power-down of unused outputs), SYNC and IO_UPDATE.
 */
#include "../LIB/ad9523.h"
#include "../LIB/no_os_spi.h"
#include "../LIB/no_os_error.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

/* ---- mock delays (no_os_delay.h) ---- */
void no_os_udelay(uint32_t usec) { (void)usec; }
void no_os_mdelay(uint32_t msec) { (void)msec; }

/* ---- mock SPI platform with an AD9523 register file ---- */
static uint8_t regfile[0x1000];
static int xfers, cs_asserts;
static int32_t mock_init(struct no_os_spi_desc **desc, const struct no_os_spi_init_param *p)
{
    *desc = calloc(1, sizeof(**desc));
    (*desc)->chip_select = p->chip_select; (*desc)->max_speed_hz = p->max_speed_hz;
    return 0;
}
static int32_t mock_wr(struct no_os_spi_desc *desc, uint8_t *b, uint16_t n)
{
    (void)desc; xfers++; cs_asserts++;
    if (n != 3) { printf("  unexpected frame length %u\n", n); return -EINVAL; }
    uint16_t addr = ((b[0] & 0x0F) << 8) | b[1];
    if (b[0] & 0x80) {           /* read */
        if (addr == 0x22C) b[2] = 0xFF;             /* READBACK_0: everything locked/present */
        else if (addr == 0x22D) b[2] = 0x00;        /* READBACK_1: VCO calibration not in progress */
        else b[2] = regfile[addr];
    } else {
        regfile[addr] = b[2];
    }
    return 0;
}
static int32_t mock_rm(struct no_os_spi_desc *desc) { free(desc); return 0; }
static const struct no_os_spi_platform_ops mock_ops = { .init = mock_init, .write_and_read = mock_wr, .remove = mock_rm };

static uint32_t reg24(uint16_t a) { return ((uint32_t)regfile[a] << 16) | ((uint32_t)regfile[a - 1] << 8) | regfile[a - 2]; }

int main(void)
{
    /* ---- platform data: verbatim from main.cpp configure_ad9523() ---- */
    static struct ad9523_platform_data pdata; memset(&pdata, 0, sizeof pdata);
    pdata.vcxo_freq = 100000000; pdata.refa_diff_rcv_en = 0; pdata.refb_diff_rcv_en = 0; pdata.osc_in_diff_en = 0;
    pdata.pll1_bypass_en = 0; pdata.refa_r_div = 1; pdata.refb_r_div = 1;
    pdata.pll2_ndiv_a_cnt = 0; pdata.pll2_ndiv_b_cnt = 9; pdata.pll2_r2_div = 0; pdata.pll2_charge_pump_current_nA = 3500;
    pdata.rpole2 = RPOLE2_900_OHM; pdata.rzero = RZERO_2000_OHM; pdata.cpole1 = CPOLE1_24_PF; pdata.rzero_bypass_en = 0;
    static struct ad9523_channel_spec channels[AD9523_NUM_CHAN];
    pdata.channels = channels; pdata.num_channels = AD9523_NUM_CHAN;
    for (int i = 0; i < AD9523_NUM_CHAN; ++i) {
        channels[i].channel_num = i; channels[i].driver_mode = TRISTATE; channels[i].channel_divider = 0;
        channels[i].divider_phase = 0; channels[i].use_alt_clock_src = 0; channels[i].output_dis = 1;
    }
    struct { int ch; int div; int mode; } used[] = {
        {0, 12, LVDS_7mA}, {1, 12, LVDS_7mA}, {4, 9, LVDS_7mA}, {5, 9, LVDS_7mA},
        {6, 36, CMOS_CONF1}, {7, 180, CMOS_CONF1}, {8, 60, LVDS_4mA}, {9, 60, LVDS_4mA},
        {10, 30, CMOS_CONF1}, {11, 30, CMOS_CONF1} };
    for (size_t i = 0; i < sizeof used / sizeof used[0]; i++) {
        channels[used[i].ch].channel_divider = used[i].div; channels[used[i].ch].driver_mode = used[i].mode;
        channels[used[i].ch].output_dis = 0;
    }

    struct ad9523_init_param init_param; memset(&init_param, 0, sizeof init_param);
    init_param.spi_init.max_speed_hz = 10000000; init_param.spi_init.chip_select = 0;
    init_param.spi_init.mode = NO_OS_SPI_MODE_0; init_param.spi_init.platform_ops = &mock_ops;
    init_param.pdata = &pdata;

    printf("T1 ad9523_setup() completes against the register mock (NOTE: ad9523_init() must NOT be\n"
           "   called after filling pdata - it resets every field; this is defect C8 in the original main.cpp)\n");
    struct ad9523_dev *dev = NULL;
    int32_t ret = ad9523_setup(&dev, &init_param);
    CHECK(ret == 0);
    CHECK(dev != NULL);
    CHECK(xfers > 50);

    printf("T2 serial port config: SDO active (4-wire) requested, no soft-reset left asserted\n");
    CHECK((regfile[0x000] & AD9523_SER_CONF_SDO_ACTIVE) != 0);

    printf("T3 channel distribution registers 0x192+3*ch (24-bit): divider, driver mode, power-down\n");
    for (size_t i = 0; i < sizeof used / sizeof used[0]; i++) {
        uint16_t a = 0x192 + 3 * used[i].ch;
        uint32_t v = reg24(a);
        uint32_t expect = AD9523_CLK_DIST_DRIVER_MODE(used[i].mode) | AD9523_CLK_DIST_DIV(used[i].div) | AD9523_CLK_DIST_DIV_PHASE(0);
        if (v != expect) printf("  ch%d reg=0x%06X expect=0x%06X\n", used[i].ch, v, expect);
        CHECK(v == expect);
        CHECK((v & AD9523_CLK_DIST_PWR_DOWN_EN) == 0);
    }
    int unused_ch[] = {2, 3, 12, 13};
    for (size_t i = 0; i < 4; i++) {
        uint32_t v = reg24(0x192 + 3 * unused_ch[i]);
        CHECK((v & AD9523_CLK_DIST_PWR_DOWN_EN) != 0);
        CHECK((v & 0xF) == AD9523_CLK_DIST_DRIVER_MODE(TRISTATE));
    }

    printf("T4 derived frequencies with VCO = 100 MHz x N(4*9+0=36) = 3.6 GHz\n");
    double vco = 100e6 * (4.0 * pdata.pll2_ndiv_b_cnt + pdata.pll2_ndiv_a_cnt);
    CHECK(vco == 3.6e9);
    CHECK(vco / 12 == 300e6);   /* OUT0/1 ADF4382 reference */
    CHECK(vco / 9  == 400e6);   /* OUT4/5 ADC */
    CHECK(vco / 36 == 100e6);   /* OUT6 FPGA system clock */
    CHECK(vco / 60 == 60e6);    /* OUT8/9 ADF4382 SYNC */
    CHECK(vco / 30 == 120e6);   /* OUT10/11 DAC */
    CHECK(vco / 180 == 20e6);   /* OUT7 FPGA test clock */

    printf("T5 IO_UPDATE issued and status/sync paths executed\n");
    CHECK(regfile[0x234] == 0x01);
    CHECK(ad9523_status(dev) == 0);
    CHECK(ad9523_sync(dev) == 0);
    CHECK(ad9523_remove(dev) == 0);

    printf("%s (%d failure(s), %d SPI frames)\n", failures ? "TEST FAILED" : "TEST PASSED", failures, xfers);
    return failures ? 1 : 0;
}
