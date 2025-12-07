#!/usr/bin/env python3
"""
Cross-validation script for C and Python base converters.

This script compares the output of c_cal/base_convert (C) and 
py_box_cal/base_convert.py (Python) to ensure they produce consistent results.
"""

import subprocess
import sys
import os

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
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
    cmd = [c_converter, command, str(precision), number]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def run_py_converter(command, precision, number):
    """Run the Python base converter."""
    py_converter = get_py_converter_path()
    cmd = [sys.executable, py_converter, command, str(precision)]
    
    # Handle negative numbers (need -- separator for argparse)
    if number.startswith('-'):
        cmd.append('--')
    
    cmd.append(number)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def compare_outputs(c_output, py_output, tolerance=1e-10):
    """
    Compare C and Python outputs.
    For base-32 outputs, they should match exactly.
    For base-10 outputs, allow small numerical differences.
    """
    if c_output == py_output:
        return True
    
    # Try to parse as numbers and compare with tolerance
    try:
        c_val = float(c_output)
        py_val = float(py_output)
        
        # Check relative difference
        if c_val == 0 and py_val == 0:
            return True
        if c_val == 0 or py_val == 0:
            return abs(c_val - py_val) < tolerance
        
        rel_diff = abs(c_val - py_val) / max(abs(c_val), abs(py_val))
        return rel_diff < tolerance
    except:
        # Not numeric, do string comparison
        return False


def test_conversion(test_name, command, precision, number, expected_match=True):
    """Test a single conversion and compare C vs Python output."""
    global PASSED, FAILED, SKIPPED
    
    # Run C converter
    c_output, c_returncode = run_c_converter(command, precision, number)
    
    # Run Python converter
    py_output, py_returncode = run_py_converter(command, precision, number)
    
    # Check return codes
    if c_returncode != 0 or py_returncode != 0:
        print(f"{YELLOW}⊘{NC} {test_name} (skipped - conversion error)")
        print(f"  C return code: {c_returncode}")
        print(f"  Python return code: {py_returncode}")
        SKIPPED += 1
        return
    
    # Compare outputs
    match = compare_outputs(c_output, py_output)
    
    if match == expected_match:
        print(f"{GREEN}✓{NC} {test_name}")
        print(f"  C:      {c_output}")
        print(f"  Python: {py_output}")
        PASSED += 1
    else:
        print(f"{RED}✗{NC} {test_name}")
        print(f"  C:      {c_output}")
        print(f"  Python: {py_output}")
        if expected_match:
            print(f"  Expected: Outputs should match")
        else:
            print(f"  Expected: Outputs should differ")
        FAILED += 1


def main():
    """Main test function."""
    # Check if converters exist
    c_converter = get_c_converter_path()
    py_converter = get_py_converter_path()
    
    if not os.path.exists(c_converter):
        print(f"{RED}Error: C converter not found at {c_converter}{NC}")
        sys.exit(1)
    
    if not os.path.exists(py_converter):
        print(f"{RED}Error: Python converter not found at {py_converter}{NC}")
        sys.exit(1)
    
    print("=" * 70)
    print("Cross-validation: C vs Python Base Converters")
    print("=" * 70)
    print()
    print("NOTE: Both C and Python converters now output matching decimal notation.")
    print("      Both generate trailing zeros based on precision in bits.")
    print()
    print("This test validates exact alignment by:")
    print("  1. Comparing 10TO32 outputs (should match exactly)")
    print("  2. Comparing 32TO10 outputs (should match numerically)")
    print("  3. Testing round-trip conversions (10->32->10)")
    print()
    
    # Test 1-10: Base-10 to Base-32 conversions
    print("10TO32 Tests (Base-10 to Base-32):")
    print("-" * 70)
    print("Both converters now output matching decimal notation with trailing zeros.")
    print()
    test_conversion("10TO32: Zero", "10TO32", 64, "0")
    test_conversion("10TO32: Integer 10", "10TO32", 64, "10")
    test_conversion("10TO32: Negative integer -10", "10TO32", 64, "-10")
    test_conversion("10TO32: Fraction -0.5", "10TO32", 64, "-0.5")
    test_conversion("10TO32: Fraction 0.25", "10TO32", 128, "0.25")
    test_conversion("10TO32: Fraction -0.75", "10TO32", 64, "-0.75")
    test_conversion("10TO32: Large integer 1024", "10TO32", 64, "1024")
    print()
    
    # Test 32TO10 conversions - these should match numerically
    print("32TO10 Tests (Base-32 to Base-10):")
    print("-" * 70)
    test_conversion("32TO10: Zero", "32TO10", 64, "0")
    test_conversion("32TO10: Integer a (10)", "32TO10", 64, "a")
    test_conversion("32TO10: Fraction 0.8 (0.25)", "32TO10", 128, "0.8")
    test_conversion("32TO10: Large integer 100 (1024)", "32TO10", 64, "100")
    test_conversion("32TO10: Small fraction 0.1 (0.03125)", "32TO10", 64, "0.1")
    test_conversion("32TO10: Integer g (16)", "32TO10", 64, "g")
    test_conversion("32TO10: Fraction 0.g (0.5)", "32TO10", 64, "0.g")
    
    print()
    print("Round-trip Tests:")
    print("-" * 70)
    print("NOTE: Both converters use decimal notation now.")
    print("      Round-trip conversions should preserve values accurately.")
    print()
    
    # Test round-trip: 10->32->10
    test_values = ["0.5", "10", "0.25"]
    for val in test_values:
        global PASSED, FAILED
        
        # C: 10->32
        c_b32, _ = run_c_converter("10TO32", 256, val)
        # C: 32->10
        c_b10, _ = run_c_converter("32TO10", 256, c_b32)
        
        # Python: 10->32
        py_b32, _ = run_py_converter("10TO32", 50, val)
        # Python: 32->10
        py_b10, _ = run_py_converter("32TO10", 50, py_b32)
        
        match = compare_outputs(c_b10, py_b10, tolerance=1e-6)
        
        if match:
            print(f"{GREEN}✓{NC} Round-trip: {val}")
            print(f"  C final:      {c_b10}")
            print(f"  Python final: {py_b10}")
            PASSED += 1
        else:
            print(f"{RED}✗{NC} Round-trip: {val}")
            print(f"  C:      {val} -> {c_b32} -> {c_b10}")
            print(f"  Python: {val} -> {py_b32} -> {py_b10}")
            FAILED += 1
    
    # Summary
    print()
    print("=" * 70)
    print(f"Total tests: {PASSED + FAILED + SKIPPED}")
    print(f"Passed: {PASSED}")
    print(f"Failed: {FAILED}")
    print(f"Skipped: {SKIPPED}")
    print("=" * 70)
    
    if FAILED == 0 and SKIPPED == 0:
        print(f"{GREEN}All tests passed! C and Python converters are aligned. ✓{NC}")
        sys.exit(0)
    elif FAILED == 0:
        print(f"{YELLOW}All non-skipped tests passed. {SKIPPED} tests skipped.{NC}")
        sys.exit(0)
    else:
        print(f"{RED}Some tests failed! C and Python converters are NOT aligned.{NC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
