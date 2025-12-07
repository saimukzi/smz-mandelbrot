#!/bin/bash

# Stress tests and edge cases for Mandelbrot calculator

echo "========================================"
echo "Mandelbrot Calculator - Stress Tests"
echo "========================================"
echo ""

# Check if mandelbrot executable exists
if [ ! -f "./mandelbrot" ]; then
    echo "Error: mandelbrot executable not found!"
    echo "Please run 'make' first to build the program."
    exit 1
fi

echo "Test 1: Very high precision (1024 bits)"
echo "----------------------------------------"
echo -e "CAL 1024 0 0 0 0 100 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 2: Very large iteration count (100000)"
echo "----------------------------------------"
echo -e "CAL 64 0 0 0 0 100000 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 3: Point very close to escape boundary"
echo "----------------------------------------"
echo "z0 = (1.9, 0), c = (0, 0), R = 2"
echo -e "CAL 128 1.v 0 0 0 10 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 4: Very small numbers"
echo "----------------------------------------"
echo "c = (0.000001, 0.000001)"
echo -e "CAL 128 0 0 0.000001 0.000001 1000 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 5: Very large numbers"
echo "----------------------------------------"
echo "z0 = (1000, 1000)"
echo -e "CAL 64 1000 1000 0 0 10 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 6: Negative initial values"
echo "----------------------------------------"
echo "z0 = (-1, -1), c = (-0.5, 0.5)"
echo -e "CAL 128 -1 -1 -0.5 0.5 100 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 7: Different escape radius (R = 10)"
echo "----------------------------------------"
echo -e "CAL 64 0 0 0 0 100 a\nEXIT" | ./mandelbrot
echo ""

echo "Test 8: Different escape radius (R = 1.5)"
echo "----------------------------------------"
echo -e "CAL 64 0 0 0 0 100 1.5\nEXIT" | ./mandelbrot
echo ""

echo "Test 9: Sequential processing (10 commands)"
echo "----------------------------------------"
{
    for i in {1..10}; do
        echo "CAL 64 0 0 0 0 100 2"
    done
    echo "EXIT"
} | ./mandelbrot | tail -5
echo ""

echo "Test 10: Mixed valid and invalid commands"
echo "----------------------------------------"
echo -e "CAL 64 0 0 0 0 100 2\nINVALID\nCAL 64 1 1 0 0 50 2\nBADCMD\nEXIT" | ./mandelbrot
echo ""

echo "Test 11: Famous Mandelbrot set points"
echo "----------------------------------------"
echo "Point: c = (-0.75, 0) - inside main cardioid"
echo -e "CAL 128 0 0 -0.75 0 1000 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 12: Point on boundary"
echo "----------------------------------------"
echo "Point: c = (-0.5, 0.5) - near boundary"
echo -e "CAL 256 0 0 -0.5 0.5 10000 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 13: Precision comparison"
echo "----------------------------------------"
echo "Same point with different precisions:"
echo "64-bit:"
echo -e "CAL 64 0 0 -1 0 100 2\nEXIT" | ./mandelbrot
echo "256-bit:"
echo -e "CAL 256 0 0 -1 0 100 2\nEXIT" | ./mandelbrot
echo "1024-bit:"
echo -e "CAL 1024 0 0 -1 0 100 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 14: Iteration count comparison"
echo "----------------------------------------"
echo "Same point with different iteration limits:"
echo "10 iterations:"
echo -e "CAL 128 0 0 -0.5 0.5 10 2\nEXIT" | ./mandelbrot
echo "100 iterations:"
echo -e "CAL 128 0 0 -0.5 0.5 100 2\nEXIT" | ./mandelbrot
echo "1000 iterations:"
echo -e "CAL 128 0 0 -0.5 0.5 1000 2\nEXIT" | ./mandelbrot
echo ""

echo "Test 15: Complex number edge cases"
echo "----------------------------------------"
echo "Pure real: c = (1, 0)"
echo -e "CAL 64 0 0 1 0 100 2\nEXIT" | ./mandelbrot
echo "Pure imaginary: c = (0, 1)"
echo -e "CAL 64 0 0 0 1 100 2\nEXIT" | ./mandelbrot
echo "Equal real and imaginary: c = (1, 1)"
echo -e "CAL 64 0 0 1 1 100 2\nEXIT" | ./mandelbrot
echo ""

echo "========================================"
echo "Stress tests completed!"
echo "========================================"
