/* Host-side unit test: beam-matrix generation (LIB/aeris_beam.c == original main.cpp:317-443). */
#include "../LIB/aeris_beam.h"
#include <stdio.h>
#include <string.h>

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

/* Copied verbatim from Core/Src/main.cpp (phase_differences[31]). */
static const float phase_differences[31] = {
    160.0f, 80.0f, 53.333f, 40.0f, 32.0f, 26.667f, 22.857f, 20.0f, 17.778f, 16.0f,
    14.545f, 13.333f, 12.308f, 11.429f, 10.667f, 0.0f,
    -10.667f, -11.429f, -12.308f, -13.333f, -14.545f, -16.0f, -17.778f, -20.0f,
    -22.857f, -26.667f, -32.0f, -40.0f, -53.333f, -80.0f, -160.0f
};

int main(void)
{
    uint8_t m1[15][16], m2[15][16], v0[16];
    memset(m1, 0xAA, sizeof m1); memset(m2, 0xAA, sizeof m2); memset(v0, 0xAA, sizeof v0);

    printf("T1 degrees -> 7-bit phase (2.8125 deg/LSB, truncating, wrap to 0..360)\n");
    CHECK(aeris_degrees_to_7bit_phase(0.0f) == 0);
    CHECK(aeris_degrees_to_7bit_phase(2.8125f) == 1);
    CHECK(aeris_degrees_to_7bit_phase(2.8f) == 0);           /* truncation, not rounding */
    CHECK(aeris_degrees_to_7bit_phase(90.0f) == 32);
    CHECK(aeris_degrees_to_7bit_phase(180.0f) == 64);
    CHECK(aeris_degrees_to_7bit_phase(359.9f) == 127);
    CHECK(aeris_degrees_to_7bit_phase(360.0f) == 0);
    CHECK(aeris_degrees_to_7bit_phase(-90.0f) == 96);        /* -90 -> 270 */
    CHECK(aeris_degrees_to_7bit_phase(720.0f + 45.0f) == 16);

    aeris_build_beam_matrices(phase_differences, m1, m2, v0);

    printf("T2 element 0 is the phase reference (0) in every row; broadside vector all zero\n");
    for (int p = 0; p < 15; p++) { CHECK(m1[p][0] == 0); CHECK(m2[p][0] == 0); }
    for (int e = 0; e < 16; e++) CHECK(v0[e] == 0);

    printf("T3 range 0..127 everywhere\n");
    for (int p = 0; p < 15; p++) for (int e = 0; e < 16; e++) { CHECK(m1[p][e] < 128); CHECK(m2[p][e] < 128); }

    printf("T4 hand-computed samples: row 0 (160 deg/element)\n");
    CHECK(m1[0][1] == 56);   /* 160       -> 56.9 -> 56  */
    CHECK(m1[0][2] == 113);  /* 320       -> 113.8 -> 113 */
    CHECK(m1[0][3] == 42);   /* 480->120  -> 42.7 -> 42  */
    CHECK(m1[1][4] == 113);  /* 80*4=320  -> 113 */
    CHECK(m1[3][9] == 0);    /* 40*9=360  -> 0   */
    CHECK(m1[7][9] == 64);   /* 20*9=180  -> 64  */

    printf("T5 matrix2 is the mirrored (negative) steering: -160 -> 200 deg -> 71\n");
    CHECK(m2[14][1] == 71);  /* diff[30] = -160 */
    CHECK(m2[0][1] == 124);  /* diff[16] = -10.667 -> 349.3 -> 124.2 -> 124 */
    /* phase(e*d) + phase(-e*d) == 128 (mod 128) up to truncation (difference 0 or 1 LSB) */
    for (int p = 0; p < 15; p++) for (int e = 1; e < 16; e++) {
        int a = m1[p][e], b = m2[14 - p][e];
        int sum = (a + b) % 128;
        CHECK(sum == 0 || sum == 127);
    }

    printf("T6 cumulative-phase linearity: row p, element e == phase(e * diff[p])\n");
    for (int p = 0; p < 15; p++) for (int e = 0; e < 16; e++)
        CHECK(m1[p][e] == aeris_degrees_to_7bit_phase((float)e * phase_differences[p]));

    printf("%s (%d failure(s))\n", failures ? "TEST FAILED" : "TEST PASSED", failures);
    return failures ? 1 : 0;
}
