#!/bin/bash

# Simple manual test script for Mandelbrot calculator
# This script provides easy-to-run individual test cases

echo "========================================"
echo "Mandelbrot Calculator - Manual Tests"
echo "========================================"
echo ""

# Check if mandelbrot executable exists
if [ ! -f "./mandelbrot" ]; then
    echo "Error: mandelbrot executable not found!"
    echo "Please run 'make' first to build the program."
    exit 1
fi

echo "Running test cases..."
echo ""

# Test 1
echo "Test 1: Origin point (0,0) with c=(0,0)"
echo "Command: CAL 64 0 0 0 0 100 2"
echo -e "CAL 64 0 0 0 0 100 2\nEXIT" | ./mandelbrot
echo ""

# Test 2
echo "Test 2: Point that escapes - z0=(10,10), c=(0,0)"
echo "Command: CAL 64 a a 0 0 100 2"
echo -e "CAL 64 a a 0 0 100 2\nEXIT" | ./mandelbrot
echo ""

# Test 3
echo "Test 3: Classic Mandelbrot c=(-2,0)"
echo "Command: CAL 64 0 0 -2 0 100 2"
echo -e "CAL 64 0 0 -2 0 100 2\nEXIT" | ./mandelbrot
echo ""

# Test 4
echo "Test 4: Point inside Mandelbrot set c=(0.25,0)"
echo "Command: CAL 64 0 0 0.25 0 1000 2"
echo -e "CAL 64 0 0 0.25 0 1000 2\nEXIT" | ./mandelbrot
echo ""

# Test 5
echo "Test 5: High precision calculation"
echo "Command: CAL 256 0 0 0 0 50 2"
echo -e "CAL 256 0 0 0 0 50 2\nEXIT" | ./mandelbrot
echo ""

# Test 6
echo "Test 6: Point with imaginary component c=(0,1)"
echo "Command: CAL 128 0 0 0 1 100 2"
echo -e "CAL 128 0 0 0 1 100 2\nEXIT" | ./mandelbrot
echo ""

# Test 7
echo "Test 7: Invalid command"
echo "Command: INVALID"
echo -e "INVALID\nEXIT" | ./mandelbrot
echo ""

# Test 8
echo "Test 8: CAL with missing parameters"
echo "Command: CAL 64 0 0"
echo -e "CAL 64 0 0\nEXIT" | ./mandelbrot
echo ""

# Test 9
echo "Test 9: Multiple commands in sequence"
echo "Commands: CAL 64 0 0 0 0 10 2, CAL 64 1 1 0 0 10 2"
echo -e "CAL 64 0 0 0 0 10 2\nCAL 64 1 1 0 0 10 2\nEXIT" | ./mandelbrot
echo ""

# Test 10
echo "Test 10: Edge case - zero iterations"
echo "Command: CAL 64 0 0 0 0 0 2"
echo -e "CAL 64 0 0 0 0 0 2\nEXIT" | ./mandelbrot
echo ""

# Test 11
echo "Test 11: CAL_VERBOSE - Origin point with 3 iterations"
echo "Command: CAL_VERBOSE 64 0 0 0 0 3 2"
echo -e "CAL_VERBOSE 64 0 0 0 0 3 2\nEXIT" | ./mandelbrot
echo ""

# Test 12
echo "Test 12: CAL_VERBOSE - Point that escapes"
echo "Command: CAL_VERBOSE 64 a 0 0 0 5 2"
echo -e "CAL_VERBOSE 64 a 0 0 0 5 2\nEXIT" | ./mandelbrot
echo ""

# Test 13
echo "Test 13: CAL_VERBOSE - Classic Mandelbrot c=(-2,0) with few iterations"
echo "Command: CAL_VERBOSE 64 0 0 -2 0 5 2"
echo -e "CAL_VERBOSE 64 0 0 -2 0 5 2\nEXIT" | ./mandelbrot
echo ""

echo "========================================"
echo "Manual tests completed!"
echo "========================================"
