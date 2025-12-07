#!/bin/bash

# Test script for Mandelbrot calculator
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local input="$2"
    local expected_pattern="$3"
    
    TOTAL=$((TOTAL + 1))
    echo -e "${YELLOW}Test $TOTAL: $test_name${NC}"
    
    # Run the program with input
    output=$(echo -e "$input" | ./mandelbrot)
    
    # Check if output matches expected pattern
    if echo "$output" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "  Input: $input"
        echo "  Output: $output"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Input: $input"
        echo "  Expected pattern: $expected_pattern"
        echo "  Got: $output"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Function to run a test with exact output match
run_test_exact() {
    local test_name="$1"
    local input="$2"
    local expected="$3"
    
    TOTAL=$((TOTAL + 1))
    echo -e "${YELLOW}Test $TOTAL: $test_name${NC}"
    
    # Run the program with input
    output=$(echo -e "$input" | ./mandelbrot)
    
    # Check if output matches expected exactly
    if [ "$output" = "$expected" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "  Input: $input"
        echo "  Output: $output"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Input: $input"
        echo "  Expected: $expected"
        echo "  Got: $output"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

echo "========================================"
echo "Mandelbrot Calculator Test Suite"
echo "========================================"
echo ""

# Check if mandelbrot executable exists
if [ ! -f "./mandelbrot" ]; then
    echo -e "${RED}Error: mandelbrot executable not found!${NC}"
    echo "Please run 'make' first to build the program."
    exit 1
fi

echo "Starting tests..."
echo ""

# Test 1: Basic EXIT command
run_test_exact "EXIT command" \
    "EXIT" \
    "EXIT"

# Test 2: Invalid command
run_test_exact "Invalid command" \
    "INVALID" \
    "BAD_CMD"

# Test 3: Empty line
run_test_exact "Empty command" \
    "" \
    "BAD_CMD"

# Test 4: CAL with missing parameters
run_test_exact "CAL with missing parameters" \
    "CAL 64 0 0" \
    "BAD_CMD"

# Test 5: Origin point (0, 0) with c = (0, 0) - should not escape
run_test "Origin stays at origin" \
    "CAL 64 0 0 0 0 100 2\nEXIT" \
    "CAL N.*@0.*@0 100"

# Test 6: Point that escapes immediately
run_test "Point (10, 10) escapes quickly" \
    "CAL 64 a@1 a@1 0 0 100 2\nEXIT" \
    "CAL Y"

# Test 7: Classic Mandelbrot point c = (-2, 0) on boundary, doesn't escape with R=2
run_test "Point c = (-2, 0) on boundary" \
    "CAL 64 0 0 -2 0 100 2\nEXIT" \
    "CAL N"

# Test 7b: Point c = (-3, 0) definitely escapes
run_test "Point c = (-3, 0) escapes" \
    "CAL 64 0 0 -3 0 10 2\nEXIT" \
    "CAL Y"

# Test 8: Point c = (0.25, 0) - inside Mandelbrot set
run_test "Point c = (0.25, 0) stays bounded" \
    "CAL 64 0 0 0.8@0 0 100 2\nEXIT" \
    "CAL N"

# Test 9: Higher precision calculation
run_test "High precision calculation" \
    "CAL 256 0 0 0 0 50 2\nEXIT" \
    "CAL N.*@0.*@0 50"

# Test 10: Small number of iterations
run_test "Small iteration count" \
    "CAL 64 0 0 0 0 1 2\nEXIT" \
    "CAL N.*@0.*@0 1"

# Test 11: Zero iterations
run_test "Zero iterations" \
    "CAL 64 0 0 0 0 0 2\nEXIT" \
    "CAL N.*@0.*@0 0"

# Test 12: Multiple commands in sequence
run_test "Multiple CAL commands" \
    "CAL 64 0 0 0 0 10 2\nCAL 64 1 1 0 0 10 2\nEXIT" \
    "EXIT"

# Test 13: Negative precision (should fail)
run_test_exact "Negative precision" \
    "CAL -64 0 0 0 0 100 2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 14: Zero precision (should fail)
run_test_exact "Zero precision" \
    "CAL 0 0 0 0 0 100 2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 15: Negative iterations (should fail)
run_test_exact "Negative iterations" \
    "CAL 64 0 0 0 0 -10 2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 16: Invalid base-32 number
run_test_exact "Invalid base-32 number" \
    "CAL 64 xyz 0 0 0 100 2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 17: Point with imaginary component
run_test "Point with imaginary c = (0, 1)" \
    "CAL 64 0 0 0 1 100 2\nEXIT" \
    "CAL"

# Test 18: Starting with non-zero z0 = (1,0), c=(0,0) stays at 1 (doesn't escape)
run_test "Non-zero initial z0 = (1, 0)" \
    "CAL 64 1 0 0 0 100 2\nEXIT" \
    "CAL N"

# Test 19: Large escape radius
run_test "Large escape radius" \
    "CAL 64 0 0 0 0 100 100\nEXIT" \
    "CAL N"

# Test 20: Small escape radius
run_test "Small escape radius (0.5)" \
    "CAL 64 0 0 1 0 100 0.8@0\nEXIT" \
    "CAL Y"

# Test 21: Case sensitivity of EXIT
run_test_exact "Lowercase exit (should fail)" \
    "exit\nEXIT" \
    "BAD_CMD
EXIT"

# Test 22: Case sensitivity of CAL
run_test_exact "Lowercase cal (should fail)" \
    "cal 64 0 0 0 0 100 2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 23: Extra spaces in command (sscanf handles multiple spaces)
run_test "Extra spaces in CAL command" \
    "CAL  64  0  0  0  0  100  2\nEXIT" \
    "CAL N"

# Test 24: Test with base-32 format numbers
run_test "Base-32 formatted input" \
    "CAL 128 1@0 2@0 -1@0 0 1000 2\nEXIT" \
    "CAL"

# Test 25: Very large iteration count
run_test "Large iteration count" \
    "CAL 64 0 0 0 0 10000 2\nEXIT" \
    "CAL N"

# Test 26: CAL_VERBOSE basic functionality
run_test "CAL_VERBOSE outputs steps" \
    "CAL_VERBOSE 64 0 0 0 0 3 2\nEXIT" \
    "CAL_STEP"

# Test 27: CAL_VERBOSE final output format
run_test "CAL_VERBOSE final output" \
    "CAL_VERBOSE 64 0 0 0 0 3 2\nEXIT" \
    "CAL N.*@0.*@0 3"

# Test 28: CAL_VERBOSE with escape
run_test "CAL_VERBOSE with escape detection" \
    "CAL_VERBOSE 64 a@1 a@1 0 0 10 2\nEXIT" \
    "CAL Y"

# Test 29: CAL_VERBOSE shows correct step count
run_test "CAL_VERBOSE step numbering" \
    "CAL_VERBOSE 64 0 0 0 0 5 2\nEXIT" \
    "CAL_STEP.*5$"

# Test 30: CAL_VERBOSE with zero iterations
run_test "CAL_VERBOSE with zero iterations" \
    "CAL_VERBOSE 64 0 0 0 0 0 2\nEXIT" \
    "CAL N.*@0.*@0 0"

# Test 31: CAL_VERBOSE with invalid parameters
run_test_exact "CAL_VERBOSE with missing parameters" \
    "CAL_VERBOSE 64 0 0\nEXIT" \
    "BAD_CMD
EXIT"

# Test 32: CAL_VERBOSE lowercase (should fail)
run_test_exact "Lowercase cal_verbose (should fail)" \
    "cal_verbose 64 0 0 0 0 5 2\nEXIT" \
    "BAD_CMD
EXIT"

echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "Total tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
