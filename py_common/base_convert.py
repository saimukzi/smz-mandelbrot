#!/usr/bin/env python3
"""
Base-10 and Base-32 Converter

Command-line tool for converting between base-10 and base-32 (MPFR format).
Uses the mpfr_base32 module with gmpy2 for MPFR-compatible operations.
"""

import sys
import argparse

from mpfr_base32 import parse_mpfr_base32, decimal_to_mpfr_base32  # type: ignore


def remove_trailing_zeros(s: str) -> str:
    """
    Remove trailing zeros from a number string that has a decimal point.
    Also removes the decimal point if no fractional part remains.
    
    Args:
        s: Number string
    
    Returns:
        String with trailing zeros removed
    """
    if '.' not in s:
        return s
    
    # Remove trailing zeros
    s = s.rstrip('0')
    # Remove decimal point if it's now at the end
    s = s.rstrip('.')
    return s


def convert_10_to_32(base10_str: str, precision_bits: int = 256) -> str:
    """
    Convert base-10 string to base-32 (MPFR format).
    
    Args:
        base10_str: Number in base-10 format (e.g., "-0.5", "123.456", "1e-10")
        precision_bits: Precision in bits (like C's mpfr_prec_t)
    
    Returns:
        Number in base-32 MPFR format
    """
    try:
        # Convert to base-32 using gmpy2
        result = decimal_to_mpfr_base32(base10_str, precision_bits)
        return result
    except Exception as e:
        raise ValueError(f"Invalid base-10 number: {e}")


def convert_32_to_10(base32_str: str, precision_bits: int = 256) -> str:
    """
    Convert base-32 (MPFR format) string to base-10.
    
    Args:
        base32_str: Number in base-32 format (e.g., "-0.g", "a")
        precision_bits: Precision in bits (like C's mpfr_prec_t)
    
    Returns:
        Number in base-10 format with trailing zeros
    """
    import math
    
    try:
        # Parse base-32 string to mpfr with specified precision
        value = parse_mpfr_base32(base32_str, precision_bits)
        
        # Handle zero
        if value == 0:
            return "0"
        
        # Convert bits to total decimal digits using the formula:
        # digits = ceil(bits * log(2) / log(10)) + 1
        # This matches MPFR's digit generation behavior
        total_digits = math.ceil(precision_bits * math.log(2) / math.log(10)) + 1
        
        # Use gmpy2's digits() function to get base-10 representation
        # This directly calls MPFR's mpfr_get_str, matching C behavior exactly
        # digits() returns (mantissa_str, exponent, precision_used)
        mantissa_str, exp, _ = value.digits(10, 0)  # 0 means use all available precision
        
        # Handle special cases
        if mantissa_str in ['@NaN@', '@Inf@', '-@Inf@']:
            return mantissa_str
        
        # mantissa_str is the mantissa without decimal point
        # exp is the exponent (number of digits before decimal point)
        sign = '-' if mantissa_str.startswith('-') else ''
        if sign:
            mantissa_str = mantissa_str[1:]  # Remove sign from mantissa
        
        mantissa_len = len(mantissa_str)
        
        # Calculate how many digits we need to match C's output
        # Pad or truncate to match the expected precision
        if mantissa_len < total_digits:
            mantissa_str = mantissa_str + '0' * (total_digits - mantissa_len)
        elif mantissa_len > total_digits:
            mantissa_str = mantissa_str[:total_digits]
        
        # Format the number with decimal point
        if exp > 0:
            # Positive exponent: digits before decimal point
            if exp >= len(mantissa_str):
                # Integer with trailing zeros
                result = mantissa_str + '0' * (exp - len(mantissa_str))
            else:
                # Insert decimal point
                integer_part = mantissa_str[:exp]
                fractional_part = mantissa_str[exp:]
                result = integer_part + '.' + fractional_part
        elif exp == 0:
            # All digits after decimal point
            result = '0.' + mantissa_str
        else:
            # Negative exponent: leading zeros after decimal point
            result = '0.' + '0' * (-exp) + mantissa_str
        
        result = sign + result
        # Remove trailing zeros before returning
        return remove_trailing_zeros(result)
    except Exception as e:
        raise ValueError(f"Invalid base-32 number: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Base-10 and Base-32 Converter - Convert between base-10 and MPFR base-32 format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  10TO32  Convert base-10 to base-32
  32TO10  Convert base-32 to base-10

Examples:
  %(prog)s 10TO32 64 -0.5
  %(prog)s 32TO10 64 -0.g
  %(prog)s 10TO32 128 0.25
  %(prog)s 32TO10 128 0.8
  %(prog)s 10TO32 128 123.456
  %(prog)s 32TO10 128 3r.efdf8
  %(prog)s 10TO32 256 1e-10
  %(prog)s 32TO10 256 0.00001
        """
    )
    
    parser.add_argument('command', 
                        choices=['10TO32', '32TO10'],
                        help='Conversion command')
    parser.add_argument('precision',
                        type=int,
                        help='Precision in bits for 10TO32, or decimal places for 32TO10')
    parser.add_argument('number',
                        help='Number to convert')
    
    args = parser.parse_args()
    
    try:
        if args.command == '10TO32':
            # For 10TO32, precision is in bits (like C's mpfr_prec_t)
            result = convert_10_to_32(args.number, args.precision)
            print(result)
        elif args.command == '32TO10':
            result = convert_32_to_10(args.number, args.precision)
            print(result)
        else:
            print(f"ERROR: Unknown command '{args.command}'", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
