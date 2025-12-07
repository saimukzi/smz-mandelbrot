#!/usr/bin/env python3
"""
Base-10 and Base-32 Converter

Command-line tool for converting between base-10 and base-32 (MPFR format).
Uses the mpfr_base32 module for conversion operations.
"""

import sys
import argparse
from decimal import Decimal
from mpfr_base32 import parse_mpfr_base32, decimal_to_mpfr_base32


def convert_10_to_32(base10_str: str, precision_bits: int = 50) -> str:
    """
    Convert base-10 string to base-32 (MPFR format).
    
    Args:
        base10_str: Number in base-10 format (e.g., "-0.5", "123.456", "1e-10")
        precision_bits: Precision in bits (like C's mpfr_prec_t)
    
    Returns:
        Number in base-32 MPFR format
    """
    import math
    
    try:
        # Parse base-10 string to Decimal
        value = Decimal(base10_str)
        
        # Convert bits to base-32 digits using the formula:
        # digits = ceil(bits * log(2) / log(32)) = ceil(bits / 5)
        # Add 1 to match MPFR's behavior
        precision_digits = math.ceil(precision_bits * math.log(2) / math.log(32)) + 1
        
        # Convert to base-32
        result = decimal_to_mpfr_base32(value, precision_digits)
        
        return result
    except Exception as e:
        raise ValueError(f"Invalid base-10 number: {e}")


def convert_32_to_10(base32_str: str, precision: int = 50) -> str:
    """
    Convert base-32 (MPFR format) string to base-10.
    
    Args:
        base32_str: Number in base-32 format (e.g., "-0.g", "a", "1@2")
        precision: Number of decimal places to display (default: 50)
    
    Returns:
        Number in base-10 format
    """
    try:
        # Parse base-32 string to Decimal
        value = parse_mpfr_base32(base32_str)
        
        # Format as base-10 string
        # Use string formatting to control precision
        if value == 0:
            return "0"
        
        # Convert to string with specified precision
        result = f"{value:.{precision}f}"
        
        # Remove trailing zeros and unnecessary decimal point
        if '.' in result:
            result = result.rstrip('0').rstrip('.')
        
        return result
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
  %(prog)s 32TO10 256 1@-2
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
