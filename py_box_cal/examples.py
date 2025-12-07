#!/usr/bin/env python3
"""
Example usage of the Mandelbrot grid calculator.
Generates common interesting regions of the Mandelbrot set.
"""

import sys
import subprocess
import os

EXAMPLES = {
    "classic": {
        "description": "Classic full Mandelbrot view",
        "args": ["-2", "-1.5@0", "1", "1.5@0", "100", "1000", "2"],
    },
    "seahorse_valley": {
        "description": "Seahorse Valley (detailed zoom)",
        "args": ["-0.75@0", "0.1@0", "-0.74@0", "0.11@0", "50", "2000", "2"],
    },
    "elephant_valley": {
        "description": "Elephant Valley",
        "args": ["0.25@0", "-0.1@-1", "0.26@0", "0.1@-1", "50", "1000", "2"],
    },
    "spiral": {
        "description": "Spiral region near -0.75",
        "args": ["-0.7520@0", "0.104@0", "-0.7515@0", "0.1045@0", "40", "5000", "2"],
    },
    "mini_mandelbrot": {
        "description": "Mini Mandelbrot at -1.75",
        "args": ["-1.752@0", "-0.001@0", "-1.748@0", "0.001@0", "50", "5000", "2"],
    },
}


def run_example(name, resolution=None, output=None):
    """Run a predefined example."""
    if name not in EXAMPLES:
        print(f"Error: Unknown example '{name}'")
        print(f"Available examples: {', '.join(EXAMPLES.keys())}")
        return False
    
    example = EXAMPLES[name]
    args = example["args"].copy()
    
    # Override resolution if provided
    if resolution:
        args[4] = str(resolution)
    
    # Set output filename
    if output is None:
        output = f"{name}_mandelbrot.csv"
    
    args.append(output)
    
    print("=" * 70)
    print(f"Running Example: {name}")
    print(f"Description: {example['description']}")
    print("=" * 70)
    print(f"Real range: {args[0]} to {args[2]}")
    print(f"Imaginary range: {args[1]} to {args[3]}")
    print(f"Resolution: {args[4]}x{args[4]}")
    print(f"Start iterations: {args[5]}")
    print(f"Escape radius: {args[6]}")
    print(f"Output file: {args[7]}")
    print("=" * 70)
    print()
    
    # Run the calculator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    calculator = os.path.join(script_dir, "box_calculator.py")
    
    cmd = [sys.executable, calculator] + args
    
    try:
        subprocess.run(cmd, check=True)
        print()
        print("=" * 70)
        print(f"✓ Example '{name}' completed successfully!")
        print(f"  Output saved to: {args[7]}")
        print("=" * 70)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Calculation failed with exit code {e.returncode}")
        return False


def list_examples():
    """List all available examples."""
    print("Available Examples:")
    print("=" * 70)
    for name, example in EXAMPLES.items():
        print(f"  {name:20} - {example['description']}")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: examples.py <example_name> [resolution] [output_file]")
        print()
        list_examples()
        sys.exit(1)
    
    example_name = sys.argv[1]
    
    if example_name == "list":
        list_examples()
        sys.exit(0)
    
    resolution = None
    output = None
    
    if len(sys.argv) >= 3:
        try:
            resolution = int(sys.argv[2])
        except ValueError:
            print(f"Error: Resolution must be an integer, got '{sys.argv[2]}'")
            sys.exit(1)
    
    if len(sys.argv) >= 4:
        output = sys.argv[3]
    
    success = run_example(example_name, resolution, output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
