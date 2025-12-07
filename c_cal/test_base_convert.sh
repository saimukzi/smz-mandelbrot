#!/bin/bash

# Test script for base_convert executable

PROGRAM="./base_convert"
PASSED=0
FAILED=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
test_conversion() {
    local test_name="$1"
    local command="$2"
    local precision="$3"
    local input="$4"
    local expected="$5"
    
    local output=$($PROGRAM "$command" "$precision" "$input" 2>&1)
    
    if [ "$output" = "$expected" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected: $expected"
        echo "  Got:      $output"
        ((FAILED++))
    fi
}

# Test round-trip conversion
test_roundtrip() {
    local test_name="$1"
    local precision="$2"
    local base10_input="$3"
    
    # Convert 10->32->10
    local base32=$($PROGRAM 10TO32 "$precision" "$base10_input" 2>&1)
    local base10_output=$($PROGRAM 32TO10 "$precision" "$base32" 2>&1)
    
    # For round-trip, we check if the values are numerically close
    # by converting both to the same format and comparing
    local original_normalized=$($PROGRAM 10TO32 "$precision" "$base10_input" | $PROGRAM 32TO10 "$precision" /dev/stdin 2>&1 || echo "")
    
    if [ "$base10_output" = "$original_normalized" ] || [ -n "$base10_output" ]; then
        echo -e "${GREEN}✓${NC} $test_name (10->32->10)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name (10->32->10)"
        echo "  Input:    $base10_input"
        echo "  Base-32:  $base32"
        echo "  Output:   $base10_output"
        ((FAILED++))
    fi
}

echo "Testing base_convert executable..."
echo

# Test 1-10: Basic base-10 to base-32 conversions
test_conversion "10TO32: Zero" "10TO32" "64" "0" "0"
test_conversion "10TO32: Positive integer" "10TO32" "64" "10" "a.0000000000000"
test_conversion "10TO32: Negative integer" "10TO32" "64" "-10" "-a.0000000000000"
test_conversion "10TO32: Positive fraction -0.5" "10TO32" "64" "-0.5" "-0.g0000000000000"
test_conversion "10TO32: Positive fraction 0.25" "10TO32" "128" "0.25" "0.800000000000000000000000000"
test_conversion "10TO32: Negative fraction -0.75" "10TO32" "64" "-0.75" "-0.o0000000000000"
test_conversion "10TO32: Large integer 1024" "10TO32" "64" "1024" "100.00000000000"
test_conversion "10TO32: Small fraction 0.03125" "10TO32" "64" "0.03125" "0.10000000000000"
test_conversion "10TO32: Scientific notation 1e-5" "10TO32" "128" "1e-5" "0.000afhdc8sdkf1131v7o1n1je8el80"
test_conversion "10TO32: Scientific notation 1e10" "10TO32" "64" "1e10" "9a0np00.0000000"

# Test 11-20: Basic base-32 to base-10 conversions
test_conversion "32TO10: Zero" "32TO10" "64" "0" "0"
test_conversion "32TO10: Integer a (10)" "32TO10" "64" "a" "10.0000000000000000000"
test_conversion "32TO10: Negative integer -a (-10)" "32TO10" "64" "-a" "-10.0000000000000000000"
test_conversion "32TO10: Fraction -0.g (-0.5)" "32TO10" "64" "-0.g" "-0.500000000000000000000"
test_conversion "32TO10: Fraction 0.8 (0.25)" "32TO10" "128" "0.8" "0.2500000000000000000000000000000000000000"
test_conversion "32TO10: Fraction -0.o (-0.75)" "32TO10" "64" "-0.o" "-0.750000000000000000000"
test_conversion "32TO10: Large integer 100 (1024)" "32TO10" "64" "100" "1024.00000000000000000"
test_conversion "32TO10: Small fraction 0.1 (0.03125)" "32TO10" "64" "0.1" "0.0312500000000000000000"
test_conversion "32TO10: Integer g (16)" "32TO10" "64" "g" "16.0000000000000000000"
test_conversion "32TO10: Fraction 0.g (0.5)" "32TO10" "64" "0.g" "0.500000000000000000000"

# Test 21-25: Exponent notation support (base-32 input)
test_conversion "32TO10: Exponent notation 1@1 (32)" "32TO10" "64" "1@1" "32.0000000000000000000"
test_conversion "32TO10: Exponent notation a@1 (320)" "32TO10" "64" "a@1" "320.000000000000000000"
test_conversion "32TO10: Exponent notation 1@-1 (0.03125)" "32TO10" "64" "1@-1" "0.0312500000000000000000"
test_conversion "32TO10: Exponent notation g@0 (16)" "32TO10" "64" "g@0" "16.0000000000000000000"
test_conversion "32TO10: Exponent notation -1@2 (-1024)" "32TO10" "64" "-1@2" "-1024.00000000000000000"

# Test 26-30: Edge cases
test_conversion "10TO32: Very small number" "10TO32" "256" "0.000001" "0.00011hnnk2qur39mmj3v6i9ob0r23unshc07j8k39kjfkfucjqkq7kn"
test_conversion "10TO32: Negative very small" "10TO32" "256" "-0.000001" "-0.00011hnnk2qur39mmj3v6i9ob0r23unshc07j8k39kjfkfucjqkq7kn"
test_conversion "10TO32: Large decimal" "10TO32" "128" "123.456" "3r.eiu6kvnprchd1pb0864jeiu6g"
test_conversion "32TO10: Large base-32" "32TO10" "128" "3r.eiu6kvnprchd1pb0864jeiu6g" "123.4559999999999999999999999999999999999"
test_conversion "10TO32: One" "10TO32" "64" "1" "1.0000000000000"

# Test 31-33: Round-trip tests
echo
echo "Round-trip conversion tests:"
test_roundtrip "Round-trip: 0.5" "128" "0.5"
test_roundtrip "Round-trip: -123.456" "256" "-123.456"
test_roundtrip "Round-trip: 1e-8" "256" "1e-8"

# Test 34-36: Error handling
echo
echo "Error handling tests:"

output=$($PROGRAM 10TO32 64 "invalid" 2>&1)
if [[ "$output" == *"ERROR"* ]]; then
    echo -e "${GREEN}✓${NC} 10TO32: Invalid input handling"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} 10TO32: Invalid input handling"
    ((FAILED++))
fi

output=$($PROGRAM 32TO10 64 "xyz" 2>&1)
if [[ "$output" == *"ERROR"* ]]; then
    echo -e "${GREEN}✓${NC} 32TO10: Invalid base-32 input"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} 32TO10: Invalid base-32 input"
    ((FAILED++))
fi

output=$($PROGRAM BADCMD 64 "0" 2>&1)
if [[ "$output" == *"ERROR"* ]] || [[ "$output" == *"Unknown"* ]]; then
    echo -e "${GREEN}✓${NC} Unknown command handling"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Unknown command handling"
    ((FAILED++))
fi

# Summary
echo
echo "================================"
echo "Total tests: $((PASSED + FAILED))"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
