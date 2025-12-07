#!/usr/bin/env python3
"""
Mandelbrot Set Image Generator

Reads CSV output from box_calculator.py and generates a smooth-colored PNG image.
Uses continuous coloring based on escape iterations and final z-value magnitude.
"""

import sys
import csv
import math
from PIL import Image
import colorsys


def parse_base32_float(s: str) -> float:
    """
    Parse MPFR base-32 format to float for visualization purposes.
    Supports formats: "1a", "1.a", "1a@2", "-1.a"
    
    Args:
        s: Base-32 string
    
    Returns:
        Float value (approximate)
    """
    s = s.strip()
    
    # Handle zero
    if s == '0' or s == '0.0':
        return 0.0
    
    # Extract sign
    sign = 1.0
    if s.startswith('-'):
        sign = -1.0
        s = s[1:]
    
    # Split mantissa and exponent
    if '@' in s:
        mantissa_str, exp_str = s.split('@')
        exponent = int(exp_str, 32)  # Exponent is in base-32
    else:
        mantissa_str = s
        exponent = 0
    
    # Parse mantissa
    if '.' in mantissa_str:
        int_part, frac_part = mantissa_str.split('.')
    else:
        int_part = mantissa_str
        frac_part = ''
    
    # Convert integer part
    value = 0.0
    if int_part:
        value = float(int(int_part, 32))
    
    # Convert fractional part
    if frac_part:
        frac_value = 0.0
        for i, digit in enumerate(frac_part, start=1):
            digit_val = int(digit, 32)
            frac_value += digit_val * (32.0 ** -i)
        value += frac_value
    
    # Apply exponent
    value *= (32.0 ** exponent)
    
    return sign * value


def calculate_smooth_color(iterations: int, max_iterations: int, final_za: float, final_zb: float, escape_radius: float = 2.0) -> tuple:
    """
    Calculate smooth RGB color for a point.
    
    Args:
        iterations: Number of iterations before escape
        max_iterations: Maximum iteration count
        final_za: Real part of final z value
        final_zb: Imaginary part of final z value
        escape_radius: Escape radius used in calculation
    
    Returns:
        (R, G, B) tuple with values 0-255
    """
    # Points that didn't escape are black
    if iterations >= max_iterations:
        return (0, 0, 0)
    
    # Calculate magnitude of final z
    z_mag = math.sqrt(final_za * final_za + final_zb * final_zb)
    
    # Smooth continuous coloring using normalized iteration count
    # Formula: nu = n + 1 - log(log|z|) / log(2)
    # This creates smooth color transitions
    if z_mag > 0:
        smooth_iter = iterations + 1 - math.log(math.log(z_mag)) / math.log(2.0)
    else:
        smooth_iter = float(iterations)
    
    # Normalize to 0-1 range
    # Use logarithmic scaling for better color distribution
    color_index = math.log(smooth_iter + 1) / math.log(max_iterations + 1)
    
    # Create color using HSV color space for smooth gradients
    # Hue cycles through spectrum, saturation and value are maxed
    hue = color_index * 360.0  # Degrees
    saturation = 0.8
    value = 0.9
    
    # Convert HSV to RGB
    h_norm = (hue % 360.0) / 360.0
    r, g, b = colorsys.hsv_to_rgb(h_norm, saturation, value)
    
    # Convert to 0-255 range
    return (int(r * 255), int(g * 255), int(b * 255))


def generate_image(csv_path: str, output_path: str):
    """
    Generate Mandelbrot set image from CSV data.
    
    Args:
        csv_path: Path to input CSV file
        output_path: Path to output PNG image
    """
    print(f"Reading CSV from: {csv_path}")
    
    # Read CSV data
    data_points = []
    max_x = 0
    max_y = 0
    max_iterations = 0
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x = int(row['X'])
            y = int(row['Y'])
            iterations = int(row['ITERATIONS'])
            
            # Parse base-32 float values
            final_za = parse_base32_float(row['FINAL_ZA'])
            final_zb = parse_base32_float(row['FINAL_ZB'])
            
            data_points.append({
                'x': x,
                'y': y,
                'iterations': iterations,
                'final_za': final_za,
                'final_zb': final_zb
            })
            
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            max_iterations = max(max_iterations, iterations)
    
    # Calculate image dimensions
    width = max_x + 1
    height = max_y + 1
    
    print(f"Image dimensions: {width}x{height}")
    print(f"Maximum iterations: {max_iterations}")
    print(f"Total data points: {len(data_points)}")
    
    # Create image
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    pixels = img.load()
    
    # Color each pixel
    print("Generating image...")
    for point in data_points:
        x = point['x']
        y = point['y']
        iterations = point['iterations']
        final_za = point['final_za']
        final_zb = point['final_zb']
        
        color = calculate_smooth_color(iterations, max_iterations, final_za, final_zb)
        pixels[x, y] = color
    
    # Save image
    img.save(output_path, 'PNG')
    print(f"Image saved to: {output_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 image_generator.py <input_csv_path> <output_image_path>")
        print("\nExample:")
        print("  python3 image_generator.py ../tmp/full.csv output.png")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        generate_image(csv_path, output_path)
    except FileNotFoundError:
        print(f"Error: Input file '{csv_path}' not found")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required column in CSV: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
