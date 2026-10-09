/* aeris_beam.c - see aeris_beam.h. Arithmetic identical to the original main.cpp. */
#include "aeris_beam.h"

uint8_t aeris_degrees_to_7bit_phase(float degrees)
{
    /* Normalize to 0-360 range */
    while (degrees < 0) degrees += 360.0f;
    while (degrees >= 360.0f) degrees -= 360.0f;

    /* Convert to 7-bit (0-127) */
    uint8_t phase_7bit = (uint8_t)((degrees / 360.0f) * 128.0f);

    return phase_7bit % 128;
}

void aeris_build_beam_matrices(const float phase_differences[AERIS_BEAM_POSITIONS],
                               uint8_t matrix1[AERIS_BEAM_HALF][AERIS_ARRAY_ELEMENTS],
                               uint8_t matrix2[AERIS_BEAM_HALF][AERIS_ARRAY_ELEMENTS],
                               uint8_t vector_0[AERIS_ARRAY_ELEMENTS])
{
    /* Matrix1: Positions 1-15 (positive phase differences) */
    for (int beam_pos = 0; beam_pos < AERIS_BEAM_HALF; beam_pos++) {
        float phase_diff_degrees = phase_differences[beam_pos];
        for (int element = 0; element < AERIS_ARRAY_ELEMENTS; element++) {
            float cumulative_phase_degrees = element * phase_diff_degrees;
            matrix1[beam_pos][element] = aeris_degrees_to_7bit_phase(cumulative_phase_degrees);
        }
    }

    /* Matrix2: Positions 17-31 (negative phase differences) */
    for (int beam_pos = 0; beam_pos < AERIS_BEAM_HALF; beam_pos++) {
        float phase_diff_degrees = phase_differences[beam_pos + 16];
        for (int element = 0; element < AERIS_ARRAY_ELEMENTS; element++) {
            float cumulative_phase_degrees = element * phase_diff_degrees;
            matrix2[beam_pos][element] = aeris_degrees_to_7bit_phase(cumulative_phase_degrees);
        }
    }

    /* Vector_0: Position 16 (zero phase - broadside) */
    for (int element = 0; element < AERIS_ARRAY_ELEMENTS; element++) {
        vector_0[element] = 0;
    }
}
