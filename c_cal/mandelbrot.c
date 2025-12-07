#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpfr.h>

#define MAX_LINE_LENGTH 4096
#define BASE 32

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
    
    // mpfr_get_str returns mantissa and exponent separately
    // We need to construct the full number with the exponent
    size_t len = strlen(str);
    char *result = malloc(len + 50); // Extra space for @, exponent, sign, etc.
    
    if (result == NULL) {
        mpfr_free_str(str);
        return NULL;
    }
    
    // Handle special cases
    if (strcmp(str, "@NaN@") == 0 || strcmp(str, "@Inf@") == 0 || strcmp(str, "-@Inf@") == 0) {
        strcpy(result, str);
        mpfr_free_str(str);
        return result;
    }
    
    // Construct the string with exponent notation
    if (str[0] == '-') {
        sprintf(result, "-%s@%ld", str + 1, (long)exp);
    } else {
        sprintf(result, "%s@%ld", str, (long)exp);
    }
    
    mpfr_free_str(str);
    return result;
}

/**
 * Calculate the absolute value (magnitude) of a complex number
 */
void complex_abs(mpfr_t result, mpfr_t real, mpfr_t imag) {
    mpfr_t temp1, temp2;
    mpfr_init2(temp1, mpfr_get_prec(real));
    mpfr_init2(temp2, mpfr_get_prec(real));
    
    // result = sqrt(real^2 + imag^2)
    mpfr_sqr(temp1, real, MPFR_RNDN);
    mpfr_sqr(temp2, imag, MPFR_RNDN);
    mpfr_add(temp1, temp1, temp2, MPFR_RNDN);
    mpfr_sqrt(result, temp1, MPFR_RNDN);
    
    mpfr_clear(temp1);
    mpfr_clear(temp2);
}

/**
 * Complex number squaring: (a + bi)^2 = (a^2 - b^2) + (2ab)i
 */
void complex_square(mpfr_t result_real, mpfr_t result_imag, mpfr_t real, mpfr_t imag) {
    mpfr_t temp1, temp2, temp3;
    mpfr_prec_t prec = mpfr_get_prec(real);
    
    mpfr_init2(temp1, prec);
    mpfr_init2(temp2, prec);
    mpfr_init2(temp3, prec);
    
    // temp1 = real^2
    mpfr_sqr(temp1, real, MPFR_RNDN);
    
    // temp2 = imag^2
    mpfr_sqr(temp2, imag, MPFR_RNDN);
    
    // temp3 = 2 * real * imag
    mpfr_mul(temp3, real, imag, MPFR_RNDN);
    mpfr_mul_si(temp3, temp3, 2, MPFR_RNDN);
    
    // result_real = real^2 - imag^2
    mpfr_sub(result_real, temp1, temp2, MPFR_RNDN);
    
    // result_imag = 2 * real * imag
    mpfr_set(result_imag, temp3, MPFR_RNDN);
    
    mpfr_clear(temp1);
    mpfr_clear(temp2);
    mpfr_clear(temp3);
}

/**
 * Process CAL command
 */
void process_cal_command(const char *line) {
    char za_str[MAX_LINE_LENGTH], zb_str[MAX_LINE_LENGTH];
    char ca_str[MAX_LINE_LENGTH], cb_str[MAX_LINE_LENGTH];
    long precision, max_iterations;
    char escape_radius_str[MAX_LINE_LENGTH];
    
    // Parse the input
    int parsed = sscanf(line, "CAL %ld %s %s %s %s %ld %s",
                        &precision, za_str, zb_str, ca_str, cb_str,
                        &max_iterations, escape_radius_str);
    
    if (parsed != 7 || precision <= 0 || max_iterations < 0) {
        printf("BAD_CMD\n");
        fflush(stdout);
        return;
    }
    
    // Initialize MPFR variables
    mpfr_t za, zb, ca, cb, escape_radius;
    mpfr_t z_real, z_imag, z_magnitude;
    mpfr_t temp_real, temp_imag;
    
    mpfr_init2(za, precision);
    mpfr_init2(zb, precision);
    mpfr_init2(ca, precision);
    mpfr_init2(cb, precision);
    mpfr_init2(escape_radius, precision);
    mpfr_init2(z_real, precision);
    mpfr_init2(z_imag, precision);
    mpfr_init2(z_magnitude, precision);
    mpfr_init2(temp_real, precision);
    mpfr_init2(temp_imag, precision);
    
    // Parse input values
    if (parse_base32_to_mpfr(za_str, za, precision) != 0 ||
        parse_base32_to_mpfr(zb_str, zb, precision) != 0 ||
        parse_base32_to_mpfr(ca_str, ca, precision) != 0 ||
        parse_base32_to_mpfr(cb_str, cb, precision) != 0 ||
        parse_base32_to_mpfr(escape_radius_str, escape_radius, precision) != 0 ||

        // Additional validation
        mpfr_nan_p(za) || mpfr_inf_p(za) ||
        mpfr_nan_p(zb) || mpfr_inf_p(zb) ||
        mpfr_nan_p(ca) || mpfr_inf_p(ca) ||
        mpfr_nan_p(cb) || mpfr_inf_p(cb) ||
        mpfr_nan_p(escape_radius) || mpfr_inf_p(escape_radius) ||
        mpfr_cmp_si(escape_radius, 0) < 0) {

        printf("BAD_CMD\n");
        fflush(stdout);
        
        mpfr_clear(za);
        mpfr_clear(zb);
        mpfr_clear(ca);
        mpfr_clear(cb);
        mpfr_clear(escape_radius);
        mpfr_clear(z_real);
        mpfr_clear(z_imag);
        mpfr_clear(z_magnitude);
        mpfr_clear(temp_real);
        mpfr_clear(temp_imag);
        return;
    }
    
    // Initialize z with z0
    mpfr_set(z_real, za, MPFR_RNDN);
    mpfr_set(z_imag, zb, MPFR_RNDN);
    
    // Perform iterations
    long iterations = 0;
    char escaped = 'N';
    
    for (long i = 0; i < max_iterations; i++) {
        // z = z^2 + c
        complex_square(temp_real, temp_imag, z_real, z_imag);
        mpfr_add(z_real, temp_real, ca, MPFR_RNDN);
        mpfr_add(z_imag, temp_imag, cb, MPFR_RNDN);
        
        iterations = i + 1;
        
        // Check if |z| > escape_radius (after computing new z)
        complex_abs(z_magnitude, z_real, z_imag);
        
        if (mpfr_cmp(z_magnitude, escape_radius) > 0) {
            escaped = 'Y';
            break;
        }
    }
    
    // Convert results to base-32 strings
    char *final_za_str = mpfr_to_base32(z_real);
    char *final_zb_str = mpfr_to_base32(z_imag);
    
    if (final_za_str == NULL || final_zb_str == NULL) {
        printf("BAD_CMD\n");
        fflush(stdout);
    } else {
        printf("CAL %c %s %s %ld\n", escaped, final_za_str, final_zb_str, iterations);
        fflush(stdout);
    }
    
    // Clean up
    if (final_za_str) free(final_za_str);
    if (final_zb_str) free(final_zb_str);
    
    mpfr_clear(za);
    mpfr_clear(zb);
    mpfr_clear(ca);
    mpfr_clear(cb);
    mpfr_clear(escape_radius);
    mpfr_clear(z_real);
    mpfr_clear(z_imag);
    mpfr_clear(z_magnitude);
    mpfr_clear(temp_real);
    mpfr_clear(temp_imag);
}

/**
 * Main function
 */
int main() {
    char line[MAX_LINE_LENGTH];
    
    while (fgets(line, sizeof(line), stdin) != NULL) {
        // Remove trailing newline
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\n') {
            line[len - 1] = '\0';
        }
        
        // Check for EXIT command
        if (strcmp(line, "EXIT") == 0) {
            printf("EXIT\n");
            fflush(stdout);
            break;
        }
        
        // Check for CAL command
        if (strncmp(line, "CAL ", 4) == 0) {
            process_cal_command(line);
        } else {
            printf("BAD_CMD\n");
            fflush(stdout);
        }
    }
    
    return 0;
}
