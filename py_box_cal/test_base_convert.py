#!/usr/bin/env python3
"""
Test script for base_convert.py
"""

import subprocess
import sys

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

PASSED = 0
FAILED = 0


def test_conversion(test_name, command, precision, number, expected):
    """Test a single conversion."""
    global PASSED, FAILED
    
    cmd = ['python3', 'base_convert.py', command, str(precision), number]
    if number.startswith('-'):
        cmd.insert(-1, '--')
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()
    
    if output == expected:
        print(f"{GREEN}✓{NC} {test_name}")
        PASSED += 1
    else:
        print(f"{RED}✗{NC} {test_name}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {output}")
        FAILED += 1


def test_roundtrip(test_name, precision, base10_value):
    """Test round-trip conversion."""
    global PASSED, FAILED
    
    # Convert 10->32
    cmd1 = ['python3', 'base_convert.py', '10TO32', str(precision), base10_value]
    if base10_value.startswith('-'):
        cmd1.insert(-1, '--')
    result1 = subprocess.run(cmd1, capture_output=True, text=True)
    base32_value = result1.stdout.strip()
    
    # Convert 32->10
    cmd2 = ['python3', 'base_convert.py', '32TO10', str(precision), base32_value]
    if base32_value.startswith('-'):
        cmd2.insert(-1, '--')
    result2 = subprocess.run(cmd2, capture_output=True, text=True)
    base10_result = result2.stdout.strip()
    
    # Check if values match numerically (now result has trailing zeros)
    try:
        input_val = float(base10_value)
        output_val = float(base10_result)
        if abs(input_val - output_val) < 1e-10:
            print(f"{GREEN}✓{NC} {test_name} (10->32->10)")
            PASSED += 1
        else:
            print(f"{RED}✗{NC} {test_name} (10->32->10)")
            print(f"  Input:    {base10_value}")
            print(f"  Base-32:  {base32_value}")
            print(f"  Output:   {base10_result}")
            FAILED += 1
    except ValueError:
        print(f"{RED}✗{NC} {test_name} (10->32->10)")
        print(f"  Input:    {base10_value}")
        print(f"  Base-32:  {base32_value}")
        print(f"  Output:   {base10_result}")
        print(f"  Error: Could not parse as numbers")
        FAILED += 1


print("Testing base_convert.py...")
print()

# Test 1-10: Base-10 to Base-32 conversions (with trailing zeros like C)
test_conversion("10TO32: Zero", "10TO32", 64, "0", "0")
test_conversion("10TO32: Integer 10", "10TO32", 64, "10", "a.0000000000000")
test_conversion("10TO32: Negative integer -10", "10TO32", 64, "-10", "-a.0000000000000")
test_conversion("10TO32: Fraction -0.5", "10TO32", 64, "-0.5", "-0.g0000000000000")
test_conversion("10TO32: Fraction 0.25", "10TO32", 128, "0.25", "0.800000000000000000000000000")
test_conversion("10TO32: Fraction -0.75", "10TO32", 64, "-0.75", "-0.o0000000000000")
test_conversion("10TO32: Large integer 1024", "10TO32", 64, "1024", "100.00000000000")
test_conversion("10TO32: Small fraction 0.03125", "10TO32", 64, "0.03125", "0.10000000000000")
test_conversion("10TO32: Integer 16", "10TO32", 64, "16", "g.0000000000000")
test_conversion("10TO32: Integer 1", "10TO32", 64, "1", "1.0000000000000")

# Test 11-20: Base-32 to Base-10 conversions (with trailing zeros like C)
test_conversion("32TO10: Zero", "32TO10", 64, "0", "0")
test_conversion("32TO10: Integer a (10)", "32TO10", 64, "a", "10.0000000000000000000")
test_conversion("32TO10: Negative integer -a (-10)", "32TO10", 64, "-a", "-10.0000000000000000000")
test_conversion("32TO10: Fraction -0.g (-0.5)", "32TO10", 64, "-0.g", "-0.500000000000000000000")
test_conversion("32TO10: Fraction 0.8 (0.25)", "32TO10", 128, "0.8", "0.2500000000000000000000000000000000000000")
test_conversion("32TO10: Fraction -0.o (-0.75)", "32TO10", 64, "-0.o", "-0.750000000000000000000")
test_conversion("32TO10: Large integer 100 (1024)", "32TO10", 64, "100", "1024.00000000000000000")
test_conversion("32TO10: Small fraction 0.1 (0.03125)", "32TO10", 64, "0.1", "0.0312500000000000000000")
test_conversion("32TO10: Integer g (16)", "32TO10", 64, "g", "16.0000000000000000000")
test_conversion("32TO10: Fraction 0.g (0.5)", "32TO10", 64, "0.g", "0.500000000000000000000")

# Test 21-25: Exponent notation support (base-32 input)
test_conversion("32TO10: Exponent notation 1@1 (32)", "32TO10", 64, "1@1", "32.0000000000000000000")
test_conversion("32TO10: Exponent notation a@1 (320)", "32TO10", 64, "a@1", "320.000000000000000000")
test_conversion("32TO10: Exponent notation 1@-1 (0.03125)", "32TO10", 64, "1@-1", "0.0312500000000000000000")
test_conversion("32TO10: Exponent notation g@0 (16)", "32TO10", 64, "g@0", "16.0000000000000000000")
test_conversion("32TO10: Exponent notation -1@2 (-1024)", "32TO10", 64, "-1@2", "-1024.00000000000000000")

# Test 26-30: Round-trip conversions
print()
print("Round-trip conversion tests:")
test_roundtrip("Round-trip: 0.5", 64, "0.5")
test_roundtrip("Round-trip: -0.5", 64, "-0.5")
test_roundtrip("Round-trip: 10", 64, "10")
test_roundtrip("Round-trip: -10", 64, "-10")
test_roundtrip("Round-trip: 0.25", 128, "0.25")

# Test 31-33: Error handling
print()
print("Error handling tests:")

result = subprocess.run(['python3', 'base_convert.py', '10TO32', '64', 'invalid'], 
                       capture_output=True, text=True)
if result.returncode != 0 and 'ERROR' in result.stderr:
    print(f"{GREEN}✓{NC} 10TO32: Invalid input handling")
    PASSED += 1
else:
    print(f"{RED}✗{NC} 10TO32: Invalid input handling")
    FAILED += 1

result = subprocess.run(['python3', 'base_convert.py', 'BADCMD', '64', '0'], 
                       capture_output=True, text=True)
if result.returncode != 0:
    print(f"{GREEN}✓{NC} Unknown command handling")
    PASSED += 1
else:
    print(f"{RED}✗{NC} Unknown command handling")
    FAILED += 1

result = subprocess.run(['python3', 'base_convert.py'], 
                       capture_output=True, text=True)
if result.returncode != 0:
    print(f"{GREEN}✓{NC} No arguments handling")
    PASSED += 1
else:
    print(f"{RED}✗{NC} No arguments handling")
    FAILED += 1

# Summary
print()
print("=" * 60)
print(f"Total tests: {PASSED + FAILED}")
print(f"Passed: {PASSED}")
print(f"Failed: {FAILED}")
print("=" * 60)

if FAILED == 0:
    print(f"{GREEN}All tests passed! ✓{NC}")
    sys.exit(0)
else:
    print(f"{RED}Some tests failed!{NC}")
    sys.exit(1)
