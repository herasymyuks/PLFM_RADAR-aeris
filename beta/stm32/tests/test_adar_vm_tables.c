/*
 * Host-side unit test: ADAR1000 vector-modulator phase tables (LIB/adar1000_vm_tables.c) against the
 * data sheet (Rev. B, Tables 10-13) and the beam-matrix phase word (LIB/aeris_beam.c).
 */
#include "../LIB/adar1000_vm_tables.h"
#include "../LIB/aeris_beam.h"
#include <stdio.h>
#include <math.h>

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

static double angle_deg(int k)
{
    double a = atan2((double)adar1000_vm_signed(adar1000_vm_q[k]), (double)adar1000_vm_signed(adar1000_vm_i[k])) * 180.0 / M_PI;
    if (a < 0) a += 360.0;
    return a;
}

int main(void)
{
    printf("T1 128 entries, every word uses only bits 5:0, no zero vector\n");
    CHECK(ADAR1000_VM_STEPS == 128);
    CHECK(sizeof(adar1000_vm_i) == 128 && sizeof(adar1000_vm_q) == 128 && sizeof(adar1000_vm_gain) == 128);
    for (int k = 0; k < 128; k++) {
        CHECK((adar1000_vm_i[k] & 0xC0) == 0);
        CHECK((adar1000_vm_q[k] & 0xC0) == 0);
        CHECK(((adar1000_vm_i[k] & 0x1F) | (adar1000_vm_q[k] & 0x1F)) != 0);
        CHECK(adar1000_vm_gain[k] == 0);   /* no per-phase correction (data sheet: VM gain kept constant) */
    }

    printf("T2 data sheet spot values (Table 10..13): 0, 90, 180, 270 deg and two arbitrary rows\n");
    CHECK(adar1000_vm_i[0]  == 0x3F && adar1000_vm_q[0]  == 0x20);   /* 0 deg       Table 10 */
    CHECK(adar1000_vm_i[32] == 0x21 && adar1000_vm_q[32] == 0x3D);   /* 90 deg      Table 11 */
    CHECK(adar1000_vm_i[64] == 0x1F && adar1000_vm_q[64] == 0x20);   /* 180 deg     Table 12 */
    CHECK(adar1000_vm_i[96] == 0x01 && adar1000_vm_q[96] == 0x1D);   /* 270 deg     Table 13 */
    CHECK(adar1000_vm_i[16] == 0x36 && adar1000_vm_q[16] == 0x35);   /* 45 deg      Table 10 */
    CHECK(adar1000_vm_i[82] == 0x14 && adar1000_vm_q[82] == 0x17);   /* 230.625 deg Table 12 */
    CHECK(adar1000_vm_i[111] == 0x34 && adar1000_vm_q[111] == 0x16); /* 312.1875    Table 13 */
    CHECK(adar1000_vm_i[127] == 0x3F && adar1000_vm_q[127] == 0x01); /* 357.1875    Table 13 */

    printf("T3 polarity convention: bit5 = 1 positive (quadrant signs)\n");
    CHECK(adar1000_vm_signed(0x3F) == 31 && adar1000_vm_signed(0x1F) == -31 && adar1000_vm_signed(0x20) == 0 && adar1000_vm_signed(0x00) == 0);
    for (int k = 1; k < 32; k++)   CHECK(adar1000_vm_signed(adar1000_vm_i[k]) > 0 && adar1000_vm_signed(adar1000_vm_q[k]) > 0);   /* Q1 */
    for (int k = 33; k < 64; k++)  CHECK(adar1000_vm_signed(adar1000_vm_i[k]) < 0 && adar1000_vm_signed(adar1000_vm_q[k]) > 0);   /* Q2 */
    for (int k = 65; k < 96; k++)  CHECK(adar1000_vm_signed(adar1000_vm_i[k]) < 0 && adar1000_vm_signed(adar1000_vm_q[k]) < 0);   /* Q3 */
    for (int k = 97; k < 128; k++) CHECK(adar1000_vm_signed(adar1000_vm_i[k]) > 0 && adar1000_vm_signed(adar1000_vm_q[k]) < 0);   /* Q4 */

    printf("T4 decoded angle tracks k*2.8125 deg (|err| < 3.5 deg) and is strictly monotonic\n");
    double maxerr = 0, prev = -1;
    for (int k = 0; k < 128; k++) {
        double a = angle_deg(k), nominal = k * 2.8125;
        double err = fmod(a - nominal + 540.0, 360.0) - 180.0;
        if (fabs(err) > maxerr) maxerr = fabs(err);
        CHECK(fabs(err) < 3.5);
        if (k > 0) CHECK(a > prev);
        prev = a;
    }
    printf("   max |angle error| = %.2f deg\n", maxerr);

    printf("T5 round trip: degreesTo7BitPhase(k*2.8125) == k and table lookup decodes back to that phase\n");
    for (int k = 0; k < 128; k++) {
        uint8_t w = aeris_degrees_to_7bit_phase(k * ADAR1000_VM_STEP_DEG + 0.001f);  /* +eps: float truncation guard */
        CHECK(w == k);
        double a = angle_deg(w);
        CHECK(fabs(fmod(a - k * 2.8125 + 540.0, 360.0) - 180.0) < 3.5);
    }
    /* beam-matrix sample: row 0, element 1 = 160 deg -> word 56 -> table angle near 157.5 deg */
    uint8_t w = aeris_degrees_to_7bit_phase(160.0f);
    CHECK(w == 56);
    CHECK(fabs(angle_deg(w) - 157.5) < 3.5);

    printf("%s (%d failure(s))\n", failures ? "TEST FAILED" : "TEST PASSED", failures);
    return failures ? 1 : 0;
}
