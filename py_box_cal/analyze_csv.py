#!/usr/bin/env python3
"""
CSV Analyzer for Mandelbrot Grid Calculator Output

This script analyzes the CSV output from box_calculator.py and provides
statistics and insights about the calculated Mandelbrot grid.
"""

import sys
import csv
from collections import Counter


def analyze_csv(filename):
    """Analyze a Mandelbrot grid CSV file."""
    
    print("=" * 70)
    print(f"Analyzing: {filename}")
    print("=" * 70)
    print()
    
    # Read CSV
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        print("Error: CSV file is empty")
        return
    
    # Basic statistics
    total_points = len(rows)
    escaped = sum(1 for row in rows if row['ESCAPED'] == 'Y')
    not_escaped = total_points - escaped
    
    print(f"Total Points: {total_points}")
    print(f"Escaped: {escaped} ({100*escaped/total_points:.1f}%)")
    print(f"Not Escaped: {not_escaped} ({100*not_escaped/total_points:.1f}%)")
    print()
    
    # Iteration statistics
    iterations = [int(row['ITERATIONS']) for row in rows]
    avg_iterations = sum(iterations) / len(iterations)
    max_iterations = max(iterations)
    min_iterations = min(iterations)
    
    print("Iteration Statistics:")
    print(f"  Average: {avg_iterations:.1f}")
    print(f"  Minimum: {min_iterations}")
    print(f"  Maximum: {max_iterations}")
    print()
    
    # Iteration histogram
    iteration_counts = Counter(iterations)
    print("Iteration Distribution (top 10):")
    for iters, count in iteration_counts.most_common(10):
        bar = "█" * int(50 * count / total_points)
        print(f"  {iters:8d}: {count:5d} {bar}")
    print()
    
    # Find interesting points (high iteration counts that escaped)
    escaped_high_iter = sorted(
        [(row, int(row['ITERATIONS'])) for row in rows if row['ESCAPED'] == 'Y'],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    if escaped_high_iter:
        print("Points with Highest Iterations (Escaped):")
        for row, iters in escaped_high_iter:
            print(f"  c = {row['CA']} + {row['CB']}i")
            print(f"    Iterations: {iters}, Final z = {row['FINAL_ZA']} + {row['FINAL_ZB']}i")
        print()
    
    # Find points on the boundary (not escaped)
    if not_escaped > 0:
        boundary_points = [row for row in rows if row['ESCAPED'] == 'N'][:5]
        print(f"Sample Boundary Points (Not Escaped, showing up to 5):")
        for row in boundary_points:
            print(f"  c = {row['CA']} + {row['CB']}i")
            print(f"    Iterations: {row['ITERATIONS']}, Final z = {row['FINAL_ZA']} + {row['FINAL_ZB']}i")
        print()
    
    # Grid dimensions (estimate)
    ca_values = set(row['CA'] for row in rows)
    cb_values = set(row['CB'] for row in rows)
    
    print(f"Grid Dimensions:")
    print(f"  Unique CA values: {len(ca_values)}")
    print(f"  Unique CB values: {len(cb_values)}")
    print(f"  Expected grid: {len(ca_values)}×{len(cb_values)}")
    print()
    
    print("=" * 70)


def main():
    if len(sys.argv) != 2:
        print("Usage: analyze_csv.py <csv_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        analyze_csv(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
