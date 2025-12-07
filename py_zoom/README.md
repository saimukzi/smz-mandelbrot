# Mandelbrot Zoom Region Suggester

A Python tool that analyzes Mandelbrot set calculation results and suggests interesting sub-regions to zoom into using the **Boundary Gradient Method**.

## Purpose

This program identifies complex and visually interesting regions in a Mandelbrot set calculation by finding areas where the iteration count changes rapidly (high gradients). It then generates new boundary arguments for the next `box_calculator.py` execution to zoom into these areas.

## Requirements

- Python 3.6+
- gmpy2 library (for MPFR base-32 conversion)
- Access to `py_common/mpfr_base32.py` utilities

## Usage

```bash
python3 zoom_suggester.py <min_ca> <min_cb> <max_ca> <max_cb> <input_csv_path> <magnification_ratio>
```

### Arguments

| Argument | Description | Format |
|----------|-------------|--------|
| `<min_ca>` | Minimum real part of c from previous calculation | Base-32 |
| `<min_cb>` | Minimum imaginary part of c from previous calculation | Base-32 |
| `<max_ca>` | Maximum real part of c from previous calculation | Base-32 |
| `<max_cb>` | Maximum imaginary part of c from previous calculation | Base-32 |
| `<input_csv_path>` | Path to CSV output from `box_calculator.py` | String |
| `<magnification_ratio>` | Zoom magnification factor (e.g., 2.0 = 2× zoom) | Float > 1.0 |

### Example

```bash
cd py_zoom

# After running box_calculator.py with these parameters:
# python3 ../py_box_cal/box_calculator.py -2 -2 1 1 100 100 2 output.csv

# Suggest a 3× zoom region:
python3 zoom_suggester.py -2 -2 1 1 ../py_box_cal/output.csv 3.0
```

### Output

The program outputs a single line with space-separated values suitable for the next `box_calculator.py` call:

```
<new_min_ca> <new_min_cb> <new_max_ca> <new_max_cb> <new_start_max_iterations>
```

Example output:
```
-0.hk -0.g8 -0.h0 -0.fs 173
```

## Algorithm: The Boundary Gradient Method

### 1. Identify Boundary Points

The algorithm filters the input data to focus on the most interesting regions:
- **ESCAPED** must be `Y` (point escaped to infinity)
- **ITERATIONS** must be greater than 1

This focuses on the intricate boundary between the Mandelbrot set and the exterior, avoiding both the bulk of the set (ESCAPED=N) and trivial quick-escape points.

### 2. Calculate Local Complexity Score

For each boundary point at position $(C_A, C_B)$ with iteration count $I$, calculate:

$$S = I \times \left( \sum_{i} |I - I_i| \right)$$

Where:
- $S$ = Local Complexity Score
- $I$ = Iteration count for the current point
- $I_i$ = Iteration counts of the 8-connected neighbors (up, down, left, right, and 4 diagonals)

**Interpretation:** High scores indicate:
1. High iteration counts (near the boundary)
2. Large gradients (rapid changes in iteration count)
3. Visual complexity and interesting detail

### 3. Select Zoom Center

1. Calculate complexity scores for all boundary points
2. Sort points by score in descending order
3. Select the **top 1%** of points (minimum of 1 point)
4. **Randomly choose** one point from this top tier

The randomness ensures variety across multiple zoom iterations while maintaining focus on highly complex regions.

### 4. Calculate New Boundaries

Given magnification ratio $M$:

**New box dimensions:**
$$\text{new\_width} = \frac{\text{old\_width}}{M}, \quad \text{new\_height} = \frac{\text{old\_height}}{M}$$

**New boundaries (centered on selected point):**
$$\text{new\_min\_ca} = \text{center\_ca} - \frac{\text{new\_width}}{2}$$
$$\text{new\_max\_ca} = \text{center\_ca} + \frac{\text{new\_width}}{2}$$
$$\text{new\_min\_cb} = \text{center\_cb} - \frac{\text{new\_height}}{2}$$
$$\text{new\_max\_cb} = \text{center\_cb} + \frac{\text{new\_height}}{2}$$

### 5. Scale Iteration Count

To maintain detail quality as we zoom in, the new iteration count is calculated from the maximum iteration count found in the CSV data:

$$\text{new\_max\_iterations} = \text{round}\left(\text{max\_iterations\_from\_csv} \times M^{0.5}\right)$$

The square root scaling balances computational cost with detail preservation.

## Workflow Example

Complete workflow for iterative zooming:

```bash
# Step 1: Calculate initial region
cd py_box_cal
python3 box_calculator.py -2 -2 1 1 200 100 2 zoom_0.csv

# Step 2: Generate zoom suggestion
cd ../py_zoom
ZOOM_ARGS=$(python3 zoom_suggester.py -2 -2 1 1 ../py_box_cal/zoom_0.csv 4.0)

# Step 3: Calculate zoomed region
cd ../py_box_cal
python3 box_calculator.py $ZOOM_ARGS 200 2 zoom_1.csv

# Step 4: Continue zooming
cd ../py_zoom
ZOOM_ARGS=$(python3 zoom_suggester.py $ZOOM_ARGS ../py_box_cal/zoom_1.csv 4.0)
# ... and so on
```

## Implementation Details

### Complexity Score Calculation

- Uses 8-connected neighborhood (includes diagonals)
- Handles edge cases where neighbors may not exist
- Gradient sum measures local "roughness" in iteration landscape

### Precision Handling

- Uses Python's `Decimal` type with 100 digits of precision
- Leverages `py_common/mpfr_base32.py` for base-32 conversion
- Ensures coordinate precision matches calculation requirements

### Random Selection

- Uses Python's `random.choice()` for unbiased selection
- Seed can be set externally with `PYTHONHASHSEED` environment variable if reproducibility is needed

## Output Interpretation

**Diagnostic messages** (printed to stderr):
- Number of points loaded from CSV
- Number of boundary points found
- Selected center coordinates and iteration count

**Final output** (printed to stdout):
- Single line with 5 space-separated values
- Can be directly captured and used in shell scripts

## Troubleshooting

**Error: No boundary points found**
- The CSV may contain only set interior (all ESCAPED=N) or trivial exterior (ITERATIONS=1)
- Try a different region or increase resolution

**Error: magnification_ratio must be greater than 1.0**
- Magnification ratio defines zoom-in factor; values ≤ 1.0 would zoom out or not zoom at all

**Invalid base-32 format errors**
- Ensure input boundaries match the format used in the CSV file
- Check that `py_common/mpfr_base32.py` is accessible

## Performance Considerations

- **Time Complexity**: O(N) where N is the number of data points
- **Memory Usage**: O(N) for storing grid index
- **Typical Runtime**: < 1 second for grids up to 1000×1000

## License

This is free and unencumbered software released into the public domain.
