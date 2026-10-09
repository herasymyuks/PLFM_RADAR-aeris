/*
 * aeris_beam.h - pure (HAL-free) beam-matrix generation for the AERIS-10 radar.
 *
 * BETA refactor: the arithmetic of degreesTo7BitPhase() and
 * initializeBeamMatrices() from 9_Firmware/9_1_Microcontroller/9_1_3_C_Cpp_Code/main.cpp:317-443
 * was moved here unchanged so that it can be unit-tested on the host
 * (beta/stm32/tests/test_beam_matrix.c). main.cpp calls these functions.
 */
#ifndef AERIS_BEAM_H
#define AERIS_BEAM_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define AERIS_BEAM_POSITIONS   31
#define AERIS_BEAM_HALF        15
#define AERIS_ARRAY_ELEMENTS   16

/* Degrees (any sign) -> 7-bit phase word 0..127 (360/128 = 2.8125 deg/LSB), truncating. */
uint8_t aeris_degrees_to_7bit_phase(float degrees);

/*
 * Build the three steering tables from the 31 per-position phase differences:
 *   matrix1[p][e] = phase(e * diff[p])        p = 0..14   (positions 1..15)
 *   vector_0[e]   = 0                                      (position 16, broadside)
 *   matrix2[p][e] = phase(e * diff[p + 16])   p = 0..14   (positions 17..31)
 */
void aeris_build_beam_matrices(const float phase_differences[AERIS_BEAM_POSITIONS],
                               uint8_t matrix1[AERIS_BEAM_HALF][AERIS_ARRAY_ELEMENTS],
                               uint8_t matrix2[AERIS_BEAM_HALF][AERIS_ARRAY_ELEMENTS],
                               uint8_t vector_0[AERIS_ARRAY_ELEMENTS]);

#ifdef __cplusplus
}
#endif

#endif /* AERIS_BEAM_H */
