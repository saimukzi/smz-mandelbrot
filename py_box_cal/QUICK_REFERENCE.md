# Quick Reference Guide

## Running the Grid Calculator

### Basic Usage
```bash
python3 box_calculator.py <min_ca> <min_cb> <max_ca> <max_cb> <resolution> <start_max_iterations> <escape_radius> <output_path>
```

### Using Simple Numbers
```bash
# Calculate -2 to 1 (real) and -1.5 to 1.5 (imaginary), 100x100 grid
python3 box_calculator.py -2 -1.5 1 1.5 100 1000 2 mandelbrot.csv
```

### Using Predefined Examples
```bash
# List available examples
python3 examples.py list

# Run an example with default settings
python3 examples.py classic

# Run an example with custom resolution
python3 examples.py seahorse_valley 200

# Run an example with custom output file
python3 examples.py spiral 100 my_spiral.csv
```

## Number Format Quick Reference

### MPFR Base-32 Format
- **Zero:** `0`
- **Integers:** `1` = 1, `2` = 2, etc.
- **Decimal notation:** `1.g` = 1.5, `0.g` = 0.5
- **Negative:** `-1` = -1, `-2` = -2
- **Small decimals:** `0.1` = 0.03125 (1/32)

### Common Values
| Value | Base-32 |
|-------|---------|
| 0 | `0` |
| 1 | `1` |
| 2 | `2` |
| -1 | `-1` |
| -2 | `-2` |
| 0.5 | `0.g` (16/32) |
| 0.25 | `0.8` (8/32) |
| 0.1 | `0.36` (≈0.09375) |

## Common Mandelbrot Regions

### The Classic View
```bash
python3 box_calculator.py -2 -1.5 1 1.5 200 1000 2 classic.csv
```

### Zoom Near c = -0.75
```bash
python3 box_calculator.py -0.76 -0.01 -0.74 0.01 100 5000 2 zoom.csv
```

### The Origin (Simple Test)
```bash
python3 box_calculator.py -1 -1 1 1 50 500 2 origin.csv
```

## Parameter Guidelines

### Resolution
- **10-20:** Very fast, rough outline (seconds)
- **50-100:** Good for exploration (10-60 seconds)
- **200-500:** High detail (minutes)
- **1000+:** Publication quality (hours)

### Start Max Iterations
- **100:** Fast, rough boundaries
- **500:** Balanced speed/detail
- **1000:** Good detail
- **5000+:** High detail for deep zooms

**Note:** The program automatically increases iterations adaptively, so start conservatively!

### Escape Radius
- **Standard:** `2` (always safe)
- **High precision:** `4` or higher for deep zooms

## Tips & Tricks

### Finding Interesting Regions
1. Start with a low resolution (50) and low iterations (100)
2. Identify interesting boundaries in the CSV
3. Zoom in on those coordinates with higher resolution
4. Increase start_max_iterations for deep zooms

### Performance Optimization
- Use lower resolution for initial exploration
- The program uses all CPU cores automatically
- Adaptive iteration means you can start with low max_iterations
- Points that escape quickly won't be recalculated

### Analyzing Results
```bash
# Get statistics about your grid
python3 analyze_csv.py output.csv

# Count escaped vs not-escaped
grep ",Y," output.csv | wc -l  # Escaped
grep ",N," output.csv | wc -l  # Not escaped
```

### Visualization Ideas
The CSV can be imported into:
- Python (matplotlib, numpy)
- MATLAB/Octave
- Excel/LibreCalc
- gnuplot
- Any data visualization tool

The CSV includes X and Y columns (grid coordinates 0 to resolution-1) for easy image generation.

Example Python visualization:
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('mandelbrot.csv')

# Method 1: Using X and Y grid coordinates directly
resolution = df['X'].max() + 1
grid = np.zeros((resolution, resolution))
for _, row in df.iterrows():
    grid[row['Y'], row['X']] = np.log1p(row['ITERATIONS'])

plt.imshow(grid, cmap='hot', origin='lower')
plt.colorbar(label='log(iterations)')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.show()

# Method 2: Scatter plot with complex values (if you have decimal conversion)
plt.scatter(df['CA'], df['CB'], c=np.log1p(df['ITERATIONS']), s=1, cmap='hot')
plt.colorbar(label='log(iterations)')
plt.xlabel('Real part (CA)')
plt.ylabel('Imaginary part (CB)')
plt.show()
```

## Troubleshooting

### "mandelbrot executable not found"
```bash
cd ../c_cal && make
```

### Program seems stuck
- Check CPU usage (should be at 100% across all cores)
- For deep zooms or high resolution, it may take a long time
- Watch the stderr output for progress updates

### High memory usage
- Each grid point stores results (~200 bytes)
- 1000×1000 grid ≈ 200 MB
- This is normal and expected

### Inaccurate results at deep zooms
- Increase precision is automatic based on resolution
- But you may need higher resolution for finer detail
- Check that step size is appropriate for your zoom level

## Example Workflow

```bash
# 1. Quick exploration
python3 examples.py classic 50

# 2. Analyze results
python3 analyze_csv.py classic_mandelbrot.csv

# 3. Find interesting point from CSV, zoom in
python3 box_calculator.py -0.75 0.1 -0.74 0.11 100 2000 2 zoom1.csv

# 4. Analyze zoom
python3 analyze_csv.py zoom1.csv

# 5. Deep zoom with high resolution
python3 box_calculator.py -0.745 0.105 -0.744 0.106 200 5000 2 deep_zoom.csv
```

## Available Examples

| Name | Description | Default Resolution |
|------|-------------|-------------------|
| `classic` | Full Mandelbrot set view | 100×100 |
| `seahorse_valley` | Seahorse Valley zoom | 50×50 |
| `elephant_valley` | Elephant Valley region | 50×50 |
| `spiral` | Spiral detail | 40×40 |
| `mini_mandelbrot` | Mini-Mandelbrot at -1.75 | 50×50 |
