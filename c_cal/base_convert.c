#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpfr.h>
#include <ctype.h>
#include "mpfr_base32.h"

#define MAX_LINE_LENGTH 4096
#define DEFAULT_PRECISION 256

/**
 * Remove trailing zeros from a number string that has a decimal point
 * Also removes the decimal point if no fractional part remains
 */
void remove_trailing_zeros(char *str) {
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
        // Check if the character before the decimal point is a digit
        if (end > str && isdigit(*(end - 1))) {
            *end = '\0';
        }
    }
}

/**
 * Convert base-10 to base-32
 */
void convert_10_to_32(const char *base10_str, mpfr_prec_t precision) {
    mpfr_t value;
    mpfr_init2(value, precision);
    
    // Parse base-10 string
    int result = mpfr_set_str(value, base10_str, 10, MPFR_RNDN);
    
    if (result != 0) {
        printf("ERROR: Invalid base-10 number\n");
        mpfr_clear(value);
        return;
    }
    
    // Convert to base-32
    char *base32_str = mpfr_to_base32(value);
    
    if (base32_str == NULL) {
        printf("ERROR: Conversion failed\n");
        mpfr_clear(value);
        return;
    }
    
    printf("%s\n", base32_str);
    
    free(base32_str);
    mpfr_clear(value);
}

/**
 * Convert base-32 to base-10
 */
void convert_32_to_10(const char *base32_str, mpfr_prec_t precision) {
    mpfr_t value;
    mpfr_init2(value, precision);
    
    // Parse base-32 string
    int result = parse_base32_to_mpfr(base32_str, value, precision);
    
    if (result != 0) {
        printf("ERROR: Invalid base-32 number\n");
        mpfr_clear(value);
        return;
    }
    
    // Convert to base-10 string
    mpfr_exp_t exp;
    char *base10_str = mpfr_get_str(NULL, &exp, 10, 0, value, MPFR_RNDN);
    
    if (base10_str == NULL) {
        printf("ERROR: Conversion failed\n");
        mpfr_clear(value);
        return;
    }
    
    // Handle special cases
    if (strcmp(base10_str, "@NaN@") == 0 || strcmp(base10_str, "@Inf@") == 0 || strcmp(base10_str, "-@Inf@") == 0) {
        printf("%s\n", base10_str);
        mpfr_free_str(base10_str);
        mpfr_clear(value);
        return;
    }
    
    // Handle zero
    if (mpfr_zero_p(value)) {
        printf("0\n");
        mpfr_free_str(base10_str);
        mpfr_clear(value);
        return;
    }
    
    // Format the output with decimal point
    size_t len = strlen(base10_str);
    int sign_offset = (base10_str[0] == '-') ? 1 : 0;
    size_t mantissa_len = len - sign_offset;
    
    // Print sign if present
    if (sign_offset) {
        printf("-");
    }
    
    // Build output string in a buffer for trailing zero removal
    char output[4096];
    char *out_ptr = output;
    
    if (exp > 0) {
        if ((size_t)exp >= mantissa_len) {
            // Integer with trailing zeros
            out_ptr += sprintf(out_ptr, "%s", base10_str + sign_offset);
            for (long i = mantissa_len; i < exp; i++) {
                *out_ptr++ = '0';
            }
            *out_ptr = '\0';
        } else {
            // Insert decimal point
            for (long i = 0; i < exp; i++) {
                *out_ptr++ = base10_str[sign_offset + i];
            }
            *out_ptr++ = '.';
            strcpy(out_ptr, base10_str + sign_offset + exp);
        }
    } else {
        // Leading zeros
        out_ptr += sprintf(out_ptr, "0.");
        for (long i = 0; i < -exp; i++) {
            *out_ptr++ = '0';
        }
        strcpy(out_ptr, base10_str + sign_offset);
    }
    
    // Remove trailing zeros before printing
    remove_trailing_zeros(output);
    printf("%s\n", output);
    
    mpfr_free_str(base10_str);
    mpfr_clear(value);
}

/**
 * Print usage information
 */
void print_usage(const char *program_name) {
    printf("Usage: %s <command> [options]\n\n", program_name);
    printf("Commands:\n");
    printf("  10TO32 <precision> <base10_number>  Convert base-10 to base-32\n");
    printf("  32TO10 <precision> <base32_number>  Convert base-32 to base-10\n\n");
    printf("Options:\n");
    printf("  <precision>     Precision in bits (e.g., 64, 128, 256)\n");
    printf("  <base10_number> Number in base-10 format (e.g., -0.5, 123.456, 1e-10)\n");
    printf("  <base32_number> Number in base-32 format (e.g., -0.g, a, 0.8@-1)\n\n");
    printf("Examples:\n");
    printf("  %s 10TO32 64 -0.5\n", program_name);
    printf("  %s 32TO10 64 -0.g\n", program_name);
    printf("  %s 10TO32 128 0.25\n", program_name);
    printf("  %s 32TO10 128 0.8\n", program_name);
}

/**
 * Main function
 */
int main(int argc, char *argv[]) {
    if (argc < 4) {
        print_usage(argv[0]);
        return 1;
    }
    
    const char *command = argv[1];
    long precision = atol(argv[2]);
    const char *number = argv[3];
    
    if (precision <= 0) {
        printf("ERROR: Invalid precision\n");
        return 1;
    }
    
    if (strcmp(command, "10TO32") == 0) {
        convert_10_to_32(number, precision);
    } else if (strcmp(command, "32TO10") == 0) {
        convert_32_to_10(number, precision);
    } else {
        printf("ERROR: Unknown command '%s'\n", command);
        print_usage(argv[0]);
        return 1;
    }
    
    return 0;
}
