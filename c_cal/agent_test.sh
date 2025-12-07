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
echo "Agent's Custom Test Suite"
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

# Test 1: Negative escape radius
run_test_exact "Negative escape radius" \
    "CAL 64 0 0 0 0 100 -2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 2: Zero escape radius
run_test "Zero escape radius" \
    "CAL 64 1 1 0 0 100 0\nEXIT" \
    "CAL Y"

# Test 3: Input with @Inf@
run_test_exact "Input with @Inf@" \
    "CAL 64 @Inf@ 0 0 0 100 2\nEXIT" \
    "BAD_CMD
EXIT"

# Test 4: Cycling point c = -1
run_test "Cycling point c = -1" \
    "CAL 64 0 0 -1 0 100 2\nEXIT" \
    "CAL N"

# Test 5: A non-zero z₀ with a cycling point c=-1
run_test "A non-zero z₀ with a cycling point c=-1" \
    "CAL 64 g@0 g@0 -1 0 100 2\nEXIT" \
    "CAL Y"

# Test 6: CAL_VERBOSE basic functionality
run_test "CAL_VERBOSE basic output" \
    "CAL_VERBOSE 64 0 0 0 0 3 2\nEXIT" \
    "CAL_STEP"

# Test 7: CAL_VERBOSE shows multiple steps
run_test "CAL_VERBOSE multiple steps" \
    "CAL_VERBOSE 64 0 0 0 0 5 2\nEXIT" \
    "CAL N.*00000000000000@0 00000000000000@0 5"

# Test 8: CAL_VERBOSE with escape
run_test "CAL_VERBOSE with escape" \
    "CAL_VERBOSE 64 a@1 a@1 0 0 10 2\nEXIT" \
    "CAL_STEP"

run_test "CAL_VERBOSE escape shows Y" \
    "CAL_VERBOSE 64 a@1 a@1 0 0 10 2\nEXIT" \
    "CAL Y"

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
