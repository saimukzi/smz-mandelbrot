# Mandelbrot Set Grid Calculator (Python)

A Python program that calculates the Mandelbrot set for a grid of complex values using parallel execution of the `c_cal/mandelbrot` executable with adaptive iteration logic.

## Requirements

- Python 3.6+
- gmpy2 library (Python bindings to GMP/MPFR/MPC for arbitrary precision arithmetic)
- Built `c_cal/mandelbrot` executable in the parent directory

### Installation

Install Python dependencies from the project root:

```bash
pip install -r ../requirements.txt
```

**Note**: gmpy2 requires system libraries (GMP, MPFR, MPC). On most systems, these are automatically handled by pip. If you encounter build issues, install the development packages:

- **Debian/Ubuntu**: `sudo apt-get install libgmp-dev libmpfr-dev libmpc-dev`
- **Fedora/RHEL**: `sudo dnf install gmp-devel mpfr-devel libmpc-devel`
- **macOS**: `brew install gmp mpfr libmpc`

## Features

- **Automatic Precision Calculation**: Dynamically determines MPFR precision based on grid resolution
- **Parallel Execution**: Utilizes all CPU cores for maximum performance
- **Adaptive Iteration**: Intelligently increases iteration counts only for un-escaped points
- **Efficient Continuation**: Resumes from last z value instead of recalculating from z₀ = 0
- **MPFR Base-32 Format**: Full support for arbitrary precision calculations with decimal notation

## Usage

```bash
python3 box_calculator.py <min_ca> <min_cb> <max_ca> <max_cb> <resolution> <start_max_iterations> <escape_radius> <output_path>
```

### Arguments

| Argument | Description | Format |
|----------|-------------|--------|
| `<min_ca>` | Minimum real part of c | Base-32 (decimal, integer, or exponent notation) |
| `<min_cb>` | Minimum imaginary part of c | Base-32 (decimal, integer, or exponent notation) |
| `<max_ca>` | Maximum real part of c | Base-32 (decimal, integer, or exponent notation) |
| `<max_cb>` | Maximum imaginary part of c | Base-32 (decimal, integer, or exponent notation) |
| `<resolution>` | Grid points per axis (N×N grid) | Integer |
| `<start_max_iterations>` | Initial iteration limit | Integer |
| `<escape_radius>` | Escape radius R | Base-32 (decimal, integer, or exponent notation) |
| `<output_path>` | Output CSV file path | String |

### Example

Calculate a 100×100 grid of the classic Mandelbrot region:

```bash
cd py_box_cal
python3 box_calculator.py -2 -2 1 1 100 100 2 mandelbrot_grid.csv
```

Calculate a high-resolution zoom into an interesting region:

```bash
python3 box_calculator.py -0.8 -0.2 -0.7 -0.1 50 1000 2 zoom_region.csv
```

**Note:** Input accepts flexible base-32 formats (decimal like `-0.g`, integer like `b`, or exponent like `-g@-1`).

## Output Format

The program generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `X` | Grid X coordinate (0 to resolution-1) |
| `Y` | Grid Y coordinate (0 to resolution-1) |
| `CA` | Real part of c (base-32, input format) |
| `CB` | Imaginary part of c (base-32, input format) |
| `ESCAPED` | 'Y' if escaped, 'N' otherwise |
| `ITERATIONS` | Total iterations performed |
| `FINAL_ZA` | Final real part of z (base-32 decimal notation) |
| `FINAL_ZB` | Final imaginary part of z (base-32 decimal notation) |

The X and Y columns provide pixel/grid coordinates for easy image generation and visualization.

## Algorithm Details

### Grid Generation

The program generates a uniform grid with `resolution` points on both axes:

$$c_{i,j} = (c_a^{min} + i \cdot \Delta c_a) + i(c_b^{min} + j \cdot \Delta c_b)$$

where:
$$\Delta c_a = \frac{c_a^{max} - c_a^{min}}{resolution - 1}, \quad \Delta c_b = \frac{c_b^{max} - c_b^{min}}{resolution - 1}$$

### Precision Calculation

The MPFR precision (in bits) is calculated as:

$$\text{precision} = \left\lceil \frac{\lceil \log_2(1/\Delta c) \rceil + 32}{64} \right\rceil \times 64$$

where $\Delta c = \min(\Delta c_a, \Delta c_b)$ and the result is rounded up to the nearest multiple of 64 for optimization.

### Adaptive Iteration

1. **Initial Pass**: All points calculated with `start_max_iterations`
2. **Subsequent Passes**: 
   - Only un-escaped points are recalculated
   - `max_iterations` is doubled each pass
   - Calculation continues from previous final z value (not from z₀ = 0)
3. **Termination**: Stops when all points escape or reach 10,000,000 total iterations

### Parallel Execution

- Spawns one worker process per CPU core
- Each worker maintains a persistent `mandelbrot` subprocess
- Tasks are distributed via a thread-safe queue
- Results are collected asynchronously

## Implementation Notes

### MPFR Base-32 Conversion

The program includes conversion functions between Python `Decimal` and MPFR base-32 format:
- `parse_mpfr_base32()`: Converts base-32 string → Decimal
- `decimal_to_mpfr_base32()`: Converts Decimal → base-32 string

These enable precise grid point generation and communication with the C executable.

### Worker Pool Architecture

- `MandelbrotWorker`: Manages single subprocess with thread-safe command execution
- `MandelbrotPool`: Coordinates multiple workers with task queue and result collection
- Each worker maintains persistent stdin/stdout connection to avoid process spawn overhead

### Result Storage

Results are stored in a dictionary indexed by grid position, allowing efficient updates during adaptive iteration rounds while preserving all intermediate states.

## Performance Considerations

- **CPU Utilization**: Automatically uses all available CPU cores
- **Memory Usage**: O(resolution²) for grid storage
- **I/O Efficiency**: Persistent subprocess connections minimize overhead
- **Adaptive Iteration**: Avoids redundant calculations on escaped points

## Testing

Run a simple test calculation:

```bash
cd py_box_cal
python3 test.py
```

This will generate a small test grid and verify the output format.

## Analyzing Results

Use the included CSV analyzer to get statistics about your calculated grid:

```bash
python3 analyze_csv.py output.csv
```

This will display:
- Total points and escape statistics
- Iteration distribution histogram
- Points with highest iteration counts
- Sample boundary points (likely in the Mandelbrot set)
- Grid dimensions verification

## Troubleshooting

**Error: mandelbrot executable not found**
- Ensure `c_cal/mandelbrot` is built: `cd ../c_cal && make`

**Invalid response from mandelbrot**
- Check that the base-32 strings are properly formatted
- Verify escape_radius is a valid positive number

**Very slow execution**
- Reduce resolution or start_max_iterations for testing
- Check system CPU load (the program uses all cores)

## License

This is free and unencumbered software released into the public domain.
