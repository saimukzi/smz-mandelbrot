#ifndef MPFR_BASE32_H
#define MPFR_BASE32_H

#include <mpfr.h>

#define BASE 32

/**
 * Parse a base-32 string to MPFR number
 * 
 * @param str The base-32 string to parse (supports decimal, integer, and exponent notation)
 * @param result The MPFR variable to store the result
 * @param prec The precision in bits for the MPFR variable
 * @return 0 on success, non-zero on error
 */
int parse_base32_to_mpfr(const char *str, mpfr_t result, mpfr_prec_t prec);

/**
 * Convert MPFR number to base-32 string in decimal notation
 * 
 * @param value The MPFR value to convert
 * @return Newly allocated string containing the base-32 representation,
 *         or NULL on error. Caller must free the returned string.
 */
char* mpfr_to_base32(mpfr_t value);

#endif // MPFR_BASE32_H
