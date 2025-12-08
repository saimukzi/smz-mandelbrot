#!/usr/bin/env python3
"""
Mandelbrot Zoom Region Suggester

This program analyzes Mandelbrot set calculation results and suggests an interesting
sub-region to zoom into using the Boundary Gradient Method.

The program identifies boundary points with high local complexity (rapid changes in
iteration count) and selects a random point from the top 1% as the new zoom center.
"""

import sys
import csv
import random
import argparse
from typing import List, Tuple, Dict, Optional
import math
from pathlib import Path

# Add py_common to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'py_common'))

import gmpy2
from mpfr_base32 import parse_mpfr_base32, decimal_to_mpfr_base32


def load_csv_data(csv_path: str) -> List[Dict]:
    """Load calculation results from CSV file."""
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'X': int(row['X']),
                'Y': int(row['Y']),
                'CA': row['CA'],
                'CB': row['CB'],
                'ESCAPED': row['ESCAPED'],
                'ITERATIONS': int(row['ITERATIONS']),
                'FINAL_ZA': row['FINAL_ZA'],
                'FINAL_ZB': row['FINAL_ZB']
            })
    return data


def filter_boundary_points(data: List[Dict]) -> List[Dict]:
    """
    Filter data to include only boundary points:
    - ESCAPED == 'Y'
    - ITERATIONS > 1
    """
    return [point for point in data 
            if point['ESCAPED'] == 'Y' and point['ITERATIONS'] > 1]


def build_grid_index(data: List[Dict]) -> Dict[Tuple[int, int], Dict]:
    """Build a dictionary mapping (X, Y) coordinates to data points."""
    return {(point['X'], point['Y']): point for point in data}


def get_neighbors(x: int, y: int, grid_index: Dict[Tuple[int, int], Dict]) -> List[int]:
    """
    Get iteration counts of neighboring points (8-connected neighborhood).
    Returns only neighbors that exist in the grid.
    """
    neighbor_offsets = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]
    
    neighbor_iterations = []
    for dx, dy in neighbor_offsets:
        neighbor_key = (x + dx, y + dy)
        if neighbor_key in grid_index:
            neighbor_iterations.append(grid_index[neighbor_key]['ITERATIONS'])
    
    return neighbor_iterations


def calculate_complexity_score(point: Dict, grid_index: Dict[Tuple[int, int], Dict]) -> float:
    """
    Calculate Local Complexity Score for a boundary point.
    
    Score = I × (Σ |I - I_i|)
    where I is the point's iteration count and I_i are neighbor iteration counts.
    """
    x, y = point['X'], point['Y']
    iteration_count = point['ITERATIONS']
    
    neighbor_iterations = get_neighbors(x, y, grid_index)
    
    if not neighbor_iterations:
        return 0.0
    
    # Calculate sum of absolute differences
    gradient_sum = sum(abs(iteration_count - neighbor_iter) 
                      for neighbor_iter in neighbor_iterations)
    
    # Local Complexity Score
    score = iteration_count * gradient_sum
    
    return score


# --- Constants ---
TOP_PERCENTILE = 0.01  # Top 1% of points are considered for the new zoom center

def select_zoom_center(boundary_points: List[Dict], 
                      grid_index: Dict[Tuple[int, int], Dict]) -> Dict:
    """
    Select a zoom center from the top percentile of points by complexity score.
    Returns a random point from this top tier.
    """
    if not boundary_points:
        raise ValueError("No boundary points found to analyze")
    
    # Calculate complexity scores for all boundary points
    scored_points = []
    for point in boundary_points:
        score = calculate_complexity_score(point, grid_index)
        scored_points.append((score, point))
    
    # Sort by score (descending)
    scored_points.sort(key=lambda x: x[0], reverse=True)
    
    # Select top percentile (at least 1 point)
    top_count = max(1, int(len(scored_points) * TOP_PERCENTILE))
    top_points = [point for score, point in scored_points[:top_count]]
    
    # Randomly select from top points
    return random.choice(top_points)


def calculate_new_boundaries(center_ca: str, center_cb: str,
                             min_ca: str, min_cb: str,
                             max_ca: str, max_cb: str,
                             magnification_ratio: float) -> Tuple[str, str, str, str]:
    """
    Calculate new boundary values for the zoom region.
    
    Returns: (new_min_ca, new_min_cb, new_max_ca, new_max_cb) in base-32 format
    """
    # Calculate initial precision based on input string lengths
    # Each base-32 digit represents ~5 bits (log2(32) = 5)
    # Add safety margin for calculations
    max_input_len = max(len(min_ca), len(min_cb), len(max_ca), len(max_cb))
    initial_precision = max(256, ((max_input_len * 5 + 63) // 64) * 64)
    
    # Calculate precision based on old boundaries
    # Use resolution estimate to determine needed precision
    min_ca_mpfr = parse_mpfr_base32(min_ca, initial_precision)
    min_cb_mpfr = parse_mpfr_base32(min_cb, initial_precision)
    max_ca_mpfr = parse_mpfr_base32(max_ca, initial_precision)
    max_cb_mpfr = parse_mpfr_base32(max_cb, initial_precision)
    
    # Calculate dimensions of new box
    old_width = max_ca_mpfr - min_ca_mpfr
    old_height = max_cb_mpfr - min_cb_mpfr
    mag_ratio_mpfr = gmpy2.mpfr(magnification_ratio)
    new_width = old_width / mag_ratio_mpfr
    new_height = old_height / mag_ratio_mpfr
    
    # Estimate minimum step size for new box (assume reasonable resolution of 100)
    delta_c = min(abs(new_width), abs(new_height)) / 100
    
    if delta_c > 0:
        # Precision Calculation Rationale:
        # 1. log2(1/delta_c): Determines the number of bits needed to represent the
        #    smallest distance between two points in the new, smaller box.
        # 2. +32: Adds a safety margin to prevent precision loss during intermediate
        #    calculations (e.g., subtractions, divisions).
        # 3. Round up to nearest 64: MPFR/GMP operations are often optimized for
        #    multiples of 64 bits.
        required_bits = math.ceil(math.log2(float(1 / delta_c))) + 32
        precision = ((required_bits + 63) // 64) * 64
        precision = max(64, precision)  # Ensure a minimum precision of 64 bits
    else:
        precision = 64
    
    # Parse center with calculated precision
    center_ca_mpfr = parse_mpfr_base32(center_ca, precision)
    center_cb_mpfr = parse_mpfr_base32(center_cb, precision)
    
    # Re-parse boundaries with calculated precision for consistency
    min_ca_mpfr = parse_mpfr_base32(min_ca, precision)
    min_cb_mpfr = parse_mpfr_base32(min_cb, precision)
    max_ca_mpfr = parse_mpfr_base32(max_ca, precision)
    max_cb_mpfr = parse_mpfr_base32(max_cb, precision)
    
    # Recalculate dimensions with new precision
    old_width = max_ca_mpfr - min_ca_mpfr
    old_height = max_cb_mpfr - min_cb_mpfr
    new_width = old_width / mag_ratio_mpfr
    new_height = old_height / mag_ratio_mpfr
    
    # Calculate new boundaries centered on the selected point
    new_min_ca_mpfr = center_ca_mpfr - new_width / 2
    new_max_ca_mpfr = center_ca_mpfr + new_width / 2
    new_min_cb_mpfr = center_cb_mpfr - new_height / 2
    new_max_cb_mpfr = center_cb_mpfr + new_height / 2
    
    # Convert back to base-32 format
    new_min_ca = decimal_to_mpfr_base32(new_min_ca_mpfr, precision)
    new_min_cb = decimal_to_mpfr_base32(new_min_cb_mpfr, precision)
    new_max_ca = decimal_to_mpfr_base32(new_max_ca_mpfr, precision)
    new_max_cb = decimal_to_mpfr_base32(new_max_cb_mpfr, precision)
    
    return new_min_ca, new_min_cb, new_max_ca, new_max_cb


def calculate_new_max_iterations(data: List[Dict], 
                                 magnification_ratio: float) -> int:
    """
    Calculate new maximum iteration count based on the maximum iterations in the data.
    
    new_max_iterations = round(max_iterations_from_csv * M**0.5)
    """
    max_iterations = max(point['ITERATIONS'] for point in data)
    new_max_iterations = round(max_iterations * (magnification_ratio ** 0.5))
    return new_max_iterations


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Mandelbrot set calculation results and suggest an interesting zoom region.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python3 zoom_suggester.py -2 -2 1 1 output.csv 3.0
  
This analyzes the calculation results in output.csv and suggests a new region
with 3× magnification centered on a high-complexity boundary point.
        """
    )
    
    parser.add_argument('min_ca', type=str,
                       help='Minimum real part of c from previous calculation (base-32)')
    parser.add_argument('min_cb', type=str,
                       help='Minimum imaginary part of c from previous calculation (base-32)')
    parser.add_argument('max_ca', type=str,
                       help='Maximum real part of c from previous calculation (base-32)')
    parser.add_argument('max_cb', type=str,
                       help='Maximum imaginary part of c from previous calculation (base-32)')
    parser.add_argument('input_csv_path', type=str,
                       help='Path to CSV output from box_calculator.py')
    parser.add_argument('magnification_ratio', type=float,
                       help='Zoom magnification factor (e.g., 2.0 = 2× zoom, must be > 1.0)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Seed for the random number generator for reproducible results')
    
    args = parser.parse_args()
    
    # Seed the random number generator if a seed is provided
    if args.seed is not None:
        random.seed(args.seed)

    # Validate magnification ratio
    if args.magnification_ratio <= 1.0:
        parser.error("magnification_ratio must be greater than 1.0")
    
    # Load and process data
    print(f"Loading data from {args.input_csv_path}...", file=sys.stderr)
    data = load_csv_data(args.input_csv_path)
    print(f"Loaded {len(data)} points", file=sys.stderr)
    
    # Filter boundary points
    boundary_points = filter_boundary_points(data)
    print(f"Found {len(boundary_points)} boundary points (ESCAPED=Y, ITERATIONS>1)", 
          file=sys.stderr)
    
    if not boundary_points:
        print("Error: No boundary points found. Cannot suggest zoom region.", 
              file=sys.stderr)
        sys.exit(1)
    
    # Build grid index for efficient neighbor lookup
    grid_index = build_grid_index(data)
    
    # Select zoom center using complexity score
    print("Calculating complexity scores...", file=sys.stderr)
    center_point = select_zoom_center(boundary_points, grid_index)
    print(f"Selected zoom center: CA={center_point['CA']}, CB={center_point['CB']}, "
          f"Iterations={center_point['ITERATIONS']}", file=sys.stderr)
    
    # Calculate new boundaries
    new_min_ca, new_min_cb, new_max_ca, new_max_cb = calculate_new_boundaries(
        center_point['CA'], center_point['CB'],
        args.min_ca, args.min_cb, args.max_ca, args.max_cb,
        args.magnification_ratio
    )
    
    # Calculate new max iterations from CSV data
    new_max_iterations = calculate_new_max_iterations(data, args.magnification_ratio)
    print(f"Maximum iterations in data: {max(point['ITERATIONS'] for point in data)}, "
          f"New max iterations: {new_max_iterations}", file=sys.stderr)
    
    # Output result
    print(f"{new_min_ca} {new_min_cb} {new_max_ca} {new_max_cb} {new_max_iterations}")


if __name__ == "__main__":
    main()
