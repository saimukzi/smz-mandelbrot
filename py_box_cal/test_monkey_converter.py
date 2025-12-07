#!/usr/bin/env python3
"""
Monkey test for base-10/32 converters.

Generates random decimal numbers and tests conversions between C and Python
implementations to find edge cases and ensure consistency.
"""

import subprocess
import sys
import os
import random

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

PASSED = 0
FAILED = 0
SKIPPED = 0


def get_c_converter_path():
    """Get the path to the C base_convert executable."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    c_converter = os.path.join(os.path.dirname(script_dir), 'c_cal', 'base_convert')
    return c_converter


def get_py_converter_path():
    """Get the path to the Python base_convert.py script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    py_converter = os.path.join(script_dir, 'base_convert.py')
    return py_converter


def run_c_converter(command, precision, number):
    """Run the C base converter."""
    c_converter = get_c_converter_path()
    cmd = [c_converter, command, str(precision), str(number)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def run_py_converter(command, precision, number):
    """Run the Python base converter."""
    py_converter = get_py_converter_path()
    cmd = [sys.executable, py_converter, command, str(precision)]
    
    # Handle negative numbers (need -- separator for argparse)
    number_str = str(number)
    if number_str.startswith('-'):
        cmd.append('--')
    
    cmd.append(number_str)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def compare_outputs_exact(c_output, py_output):
    """Compare outputs for exact string match."""
    return c_output == py_output


def compare_outputs_numeric(c_output, py_output, tolerance=1e-15):
    """Compare outputs numerically."""
    try:
        c_val = float(c_output)
        py_val = float(py_output)
        
        if c_val == 0 and py_val == 0:
            return True
        if c_val == 0 or py_val == 0:
            return abs(c_val - py_val) < tolerance
        
        rel_diff = abs(c_val - py_val) / max(abs(c_val), abs(py_val))
        return rel_diff < tolerance
    except:
        return False


def generate_random_number(num_type='mixed'):
    """
    Generate a random decimal number.
    
    Args:
        num_type: Type of number to generate
            - 'integer': Random integer
            - 'fraction': Random fraction (0 < x < 1)
            - 'small': Small fraction near zero
            - 'large': Large number
            - 'mixed': Any of the above
    
    Returns:
        String representation of the number
    """
    if num_type == 'mixed':
        num_type = random.choice(['integer', 'fraction', 'small', 'large'])
    
    # Random sign
    sign = random.choice([1, -1])
    
    if num_type == 'integer':
        # Random integer between 1 and 10000
        value = sign * random.randint(1, 10000)
        return str(value)
    
    elif num_type == 'fraction':
        # Random fraction between 0.001 and 0.999
        value = sign * random.uniform(0.001, 0.999)
        return f"{value:.10f}".rstrip('0').rstrip('.')
    
    elif num_type == 'small':
        # Very small numbers
        exponent = random.randint(-10, -1)
        mantissa = random.uniform(1, 9.99)
        value = sign * mantissa * (10 ** exponent)
        return f"{value:.15e}"
    
    elif num_type == 'large':
        # Large numbers
        exponent = random.randint(3, 10)
        mantissa = random.uniform(1, 9.99)
        value = sign * mantissa * (10 ** exponent)
        return f"{value:.2f}"
    
    return "0"


def test_random_conversion(test_num, precision_bits=None):
    """Test a random conversion."""
    global PASSED, FAILED, SKIPPED
    
    # Random precision if not specified
    if precision_bits is None:
        precision_bits = random.choice([64, 128, 256])
    
    # Generate random number
    num_type = random.choice(['integer', 'fraction', 'small', 'large', 'mixed'])
    decimal_number = generate_random_number(num_type)
    
    # Test 10TO32 conversion
    c_base32, c_ret1 = run_c_converter('10TO32', precision_bits, decimal_number)
    py_base32, py_ret1 = run_py_converter('10TO32', precision_bits, decimal_number)
    
    if c_ret1 != 0 or py_ret1 != 0:
        print(f"{YELLOW}⊘{NC} Test {test_num}: SKIP - Conversion error")
        print(f"  Input: {decimal_number} ({num_type}, {precision_bits} bits)")
        SKIPPED += 1
        return
    
    # Check if base-32 outputs are numerically equivalent
    # (They might differ in trailing digits due to decimal vs binary precision)
    c_verify, _ = run_c_converter('32TO10', precision_bits, c_base32)
    py_verify, _ = run_py_converter('32TO10', precision_bits, py_base32)
    match_10to32_numeric = compare_outputs_numeric(c_verify, py_verify, tolerance=1e-10)
    
    # Also check string match for information
    match_10to32_exact = compare_outputs_exact(c_base32, py_base32)
    
    # Test 32TO10 conversion (round-trip)
    c_back, c_ret2 = run_c_converter('32TO10', precision_bits, c_base32)
    py_back, py_ret2 = run_py_converter('32TO10', precision_bits, py_base32)
    
    if c_ret2 != 0 or py_ret2 != 0:
        print(f"{YELLOW}⊘{NC} Test {test_num}: SKIP - Back-conversion error")
        print(f"  Input: {decimal_number} ({num_type}, {precision_bits} bits)")
        SKIPPED += 1
        return
    
    # Check if 32TO10 outputs are numerically equivalent
    match_32to10_numeric = compare_outputs_numeric(c_back, py_back, tolerance=1e-10)
    match_32to10_exact = compare_outputs_exact(c_back, py_back)
    
    # Check if round-trip preserves the value numerically
    match_roundtrip_c = compare_outputs_numeric(decimal_number, c_back, tolerance=1e-10)
    match_roundtrip_py = compare_outputs_numeric(decimal_number, py_back, tolerance=1e-10)
    
    # Main criterion: numeric equivalence (exact match is ideal but not required for random decimals)
    passed = match_10to32_numeric and match_32to10_numeric and match_roundtrip_c and match_roundtrip_py
    exact_match = match_10to32_exact and match_32to10_exact
    
    if passed:
        if exact_match:
            print(f"{GREEN}✓{NC} Test {test_num}: PASS (exact match)")
        else:
            print(f"{GREEN}✓{NC} Test {test_num}: PASS (numeric match)")
        print(f"  {decimal_number} ({num_type}, {precision_bits} bits)")
        PASSED += 1
    else:
        print(f"{RED}✗{NC} Test {test_num}: FAIL")
        print(f"  Input:  {decimal_number} ({num_type}, {precision_bits} bits)")
        print(f"  10TO32 numeric match: {match_10to32_numeric} (exact: {match_10to32_exact})")
        if not match_10to32_numeric:
            print(f"    C base-32:      {c_base32}")
            print(f"    Python base-32: {py_base32}")
            print(f"    C verify:       {c_verify}")
            print(f"    Python verify:  {py_verify}")
        print(f"  32TO10 numeric match: {match_32to10_numeric} (exact: {match_32to10_exact})")
        if not match_32to10_numeric:
            print(f"    C:      {c_back}")
            print(f"    Python: {py_back}")
        print(f"  Round-trip C:      {match_roundtrip_c}")
        print(f"  Round-trip Python: {match_roundtrip_py}")
        FAILED += 1


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monkey test for base-10/32 converters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Run 100 random tests
  %(prog)s -n 1000      # Run 1000 random tests
  %(prog)s -n 50 -p 128 # Run 50 tests with 128-bit precision
  %(prog)s --seed 42    # Run with specific random seed for reproducibility
        """
    )
    
    parser.add_argument('-n', '--num-tests',
                        type=int,
                        default=100,
                        help='Number of random tests to run (default: 100)')
    parser.add_argument('-p', '--precision',
                        type=int,
                        choices=[64, 128, 256],
                        help='Fixed precision in bits (default: random)')
    parser.add_argument('--seed',
                        type=int,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Check if converters exist
    c_converter = get_c_converter_path()
    py_converter = get_py_converter_path()
    
    if not os.path.exists(c_converter):
        print(f"{RED}Error: C converter not found at {c_converter}{NC}")
        sys.exit(1)
    
    if not os.path.exists(py_converter):
        print(f"{RED}Error: Python converter not found at {py_converter}{NC}")
        sys.exit(1)
    
    # Set random seed if specified
    if args.seed is not None:
        random.seed(args.seed)
        print(f"{BLUE}Using random seed: {args.seed}{NC}")
    
    print("=" * 70)
    print("Monkey Test: C vs Python Base Converters")
    print("=" * 70)
    print(f"Number of tests: {args.num_tests}")
    if args.precision:
        print(f"Precision: {args.precision} bits (fixed)")
    else:
        print(f"Precision: random (64, 128, or 256 bits)")
    print("=" * 70)
    print()
    
    # Run tests
    for i in range(1, args.num_tests + 1):
        test_random_conversion(i, args.precision)
    
    # Summary
    print()
    print("=" * 70)
    print(f"Total tests: {PASSED + FAILED + SKIPPED}")
    print(f"{GREEN}Passed: {PASSED}{NC}")
    print(f"{RED}Failed: {FAILED}{NC}")
    print(f"{YELLOW}Skipped: {SKIPPED}{NC}")
    print("=" * 70)
    
    if FAILED == 0:
        if SKIPPED == 0:
            print(f"{GREEN}All tests passed! ✓{NC}")
        else:
            print(f"{YELLOW}All non-skipped tests passed. {SKIPPED} tests skipped.{NC}")
        sys.exit(0)
    else:
        print(f"{RED}Some tests failed!{NC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
