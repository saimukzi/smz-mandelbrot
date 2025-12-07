#!/usr/bin/env python3
"""
Simple test script for the Mandelbrot grid calculator.
Tests basic functionality with a small grid.
"""

import os
import sys
import subprocess
import csv


def run_test():
    """Run a simple test calculation."""
    # Test parameters: small 5x5 grid around origin
    min_ca = "-2"
    min_cb = "-2"
    max_ca = "2"
    max_cb = "2"
    resolution = "5"
    start_max_iterations = "100"
    escape_radius = "2"
    output_path = "test_output.csv"
    print("=" * 60)
    print("Mandelbrot Grid Calculator Test")
    print("=" * 60)
    print(f"Grid: {min_ca} to {max_ca} (real), {min_cb} to {max_cb} (imag)")
    print(f"Resolution: {resolution}x{resolution}")
    print(f"Start iterations: {start_max_iterations}")
    print(f"Escape radius: {escape_radius}")
    print(f"Output: {output_path}")
    print("=" * 60)
    # Check if mandelbrot executable exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mandelbrot_path = os.path.join(os.path.dirname(script_dir),
                                   'c_cal', 'mandelbrot')
    if not os.path.exists(mandelbrot_path):
        print(f"ERROR: mandelbrot executable not found at {mandelbrot_path}")
        print("Please build it first: cd ../c_cal && make")
        return False
    print(f"Found mandelbrot executable: {mandelbrot_path}")
    print()
    # Run the calculator
    cmd = [
        sys.executable,
        "box_calculator.py",
        min_ca, min_cb, max_ca, max_cb,
        resolution, start_max_iterations,
        escape_radius, output_path
    ]
    print("Running calculation...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True,
                                text=True)
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Calculation failed with exit code {e.returncode}")
        print(e.stderr)
        return False
    # Verify output file
    if not os.path.exists(output_path):
        print(f"ERROR: Output file {output_path} was not created")
        return False
    print()
    print("=" * 60)
    print("Results:")
    print("=" * 60)
    # Read and display results
    with open(output_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if len(rows) != int(resolution) ** 2:
            print(f"ERROR: Expected {int(resolution)**2} rows, "
                  f"got {len(rows)}")
            return False
        print(f"Total points: {len(rows)}")
        escaped_count = sum(1 for row in rows if row['ESCAPED'] == 'Y')
        not_escaped_count = len(rows) - escaped_count
        print(f"Escaped: {escaped_count}")
        print(f"Not escaped: {not_escaped_count}")
        print()
        # Show first few results
        print("First 5 results:")
        print(f"{'CA':<20} {'CB':<20} {'ESC':<5} {'ITERS':<10}")
        print("-" * 60)
        for i, row in enumerate(rows[:5]):
            print(f"{row['CA']:<20} {row['CB']:<20} {row['ESCAPED']:<5} "
                  f"{row['ITERATIONS']:<10}")
        if len(rows) > 5:
            print("...")
    print()
    print("=" * 60)
    print("✓ Test PASSED")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
