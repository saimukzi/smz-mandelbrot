#include "mpfr_base32.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * Remove trailing zeros from a number string that has a decimal point
 * Also removes the decimal point if no fractional part remains
 */
static void remove_trailing_zeros(char *str) {
    // Find decimal point
    char *decimal = strchr(str, '.');
    if (decimal == NULL) {
        return;  // No decimal point, nothing to do
    }
    
    // Find end of string
    char *end = str + strlen(str) - 1;
    
    // Remove trailing zeros
    while (end > decimal && *end == '0') {
        *end = '\0';
        end--;
    }
    
    // Remove decimal point if it's now at the end
    if (*end == '.') {
        *end = '\0';
    }
}

/**
 * Parse a base-32 string to MPFR number
 */
int parse_base32_to_mpfr(const char *str, mpfr_t result, mpfr_prec_t prec) {
    mpfr_set_prec(result, prec);
    return mpfr_set_str(result, str, BASE, MPFR_RNDN);
}

/**
 * Convert MPFR number to base-32 string
 */
char* mpfr_to_base32(mpfr_t value) {
    mpfr_exp_t exp;
    char *str = mpfr_get_str(NULL, &exp, BASE, 0, value, MPFR_RNDN);
    
    if (str == NULL) {
        return NULL;
    }
    
    // Handle special cases
    if (strcmp(str, "@NaN@") == 0 || strcmp(str, "@Inf@") == 0 || strcmp(str, "-@Inf@") == 0) {
        char *result = malloc(strlen(str) + 1);
        if (result) {
            strcpy(result, str);
        }
        mpfr_free_str(str);
        return result;
    }
    
    // Handle zero
    if (mpfr_zero_p(value)) {
        mpfr_free_str(str);
        char *result = malloc(2);
        if (result) {
            strcpy(result, "0");
        }
        return result;
    }
    
    // mpfr_get_str returns mantissa and exponent where:
    // - exp is the number of digits before the radix point
    // - If exp > 0: integer part has 'exp' digits
    // - If exp <= 0: number is 0.000...mantissa (with -exp leading zeros after point)
    
    size_t len = strlen(str);
    int sign_offset = (str[0] == '-') ? 1 : 0;
    size_t mantissa_len = len - sign_offset;
    
    // Calculate result size
    size_t result_size;
    if (exp > 0) {
        if ((size_t)exp >= mantissa_len) {
            // Need trailing zeros: mantissa000
            result_size = len + (exp - mantissa_len) + 10;
        } else {
            // Need decimal point: mantissa -> man.tissa
            result_size = len + 10;
        }
    } else {
        // Need leading zeros: 0.000mantissa
        result_size = len + (-exp) + 10;
    }
    
    char *result = malloc(result_size);
    if (result == NULL) {
        mpfr_free_str(str);
        return NULL;
    }
    
    // Build the result string
    char *dest = result;
    char *src = str;
    
    // Copy sign if present
    if (sign_offset) {
        *dest++ = *src++;
    }
    
    if (exp > 0) {
        if ((size_t)exp >= mantissa_len) {
            // Copy all mantissa digits
            strcpy(dest, src);
            dest += mantissa_len;
            // Add trailing zeros
            for (long i = mantissa_len; i < exp; i++) {
                *dest++ = '0';
            }
            *dest = '\0';
        } else {
            // Insert decimal point
            strncpy(dest, src, exp);
            dest += exp;
            *dest++ = '.';
            strcpy(dest, src + exp);
        }
    } else {
        // Leading zeros: 0.000...mantissa
        *dest++ = '0';
        *dest++ = '.';
        for (long i = 0; i < -exp; i++) {
            *dest++ = '0';
        }
        strcpy(dest, src);
    }
    
    // Remove trailing zeros before returning
    remove_trailing_zeros(result);

    mpfr_free_str(str);
    return result;
}