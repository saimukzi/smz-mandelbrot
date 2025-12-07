# SMZ Mandelbrot Development Guide

## Architecture Overview

This is a high-precision Mandelbrot set calculator split into two tightly-coupled components:
- **c_cal/**: C executables using MPFR for arbitrary-precision math (performance-critical)
- **py_box_cal/**: Python orchestration layer for parallel grid calculations
- **py_common/**: Shared MPFR base-32 conversion utilities

The Python layer spawns multiple C processes and communicates via stdin/stdout for maximum parallelism.

## Critical Dependencies

### Building C Components
```bash
cd c_cal && make
```
Requires: `libmpfr-dev`, `libgmp-dev`

### Python Environment
```bash
# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt  # Installs gmpy2>=2.2.0
```
Use `python3` (not `python`) - the system only has python3 available. The project uses `.venv/` as the default virtual environment.

## MPFR Base-32 Number Format

**This project uses a custom base-32 representation** throughout. All coordinates and calculations use this format:

### Syntax
- Decimal notation: `0.g` (16/32 = 0.5), `-1.a` 
- Integer: `1`, `2`, `b` (11 in decimal)
- Zero: `0`

### Key Conversion Functions
- Python: `py_common/mpfr_base32.py` - `parse_mpfr_base32()`, `decimal_to_mpfr_base32()`
- C: `c_cal/mpfr_base32.h` - `mpfr_set_base32_str()`, `mpfr_to_base32_str()`

**Always use base-32 format when interfacing between Python and C components.**

## Component Communication Protocol

### C Calculator Interface (`c_cal/mandelbrot`)
Commands via stdin, responses via stdout:

```
CAL <precision> <za> <zb> <ca> <cb> <max_iterations> <escape_radius>
→ CAL <escaped> <final_za> <final_zb> <iterations>

EXIT
→ EXIT
```

Example:
```bash
echo "CAL 64 0 0 0 0 100 2" | ./mandelbrot
# Output: CAL N 0 0 100
```

### Python-C Integration Pattern
- Python spawns persistent C processes (`MandelbrotPool` class)
- Each worker maintains a subprocess with stdin/stdout pipes
- Tasks submitted to queue, results collected from workers
- Workers reuse z values for adaptive iteration (continuation from previous state)

## Key Workflows

### Run Grid Calculation
```bash
cd py_box_cal
python3 examples.py classic                    # Predefined example
python3 box_calculator.py -2 -1.5 1 1.5 100 1000 2 output.csv
```

### Test Workflows
```bash
# C component tests
cd c_cal && ./test.sh          # Comprehensive C unit tests

# Python component tests  
cd py_box_cal && python3 test.py                    # Simple integration test
cd py_box_cal && python3 test_base_convert.py       # Base-32 conversion tests
```

### Development Cycle
1. Modify C code → rebuild with `cd c_cal && make`
2. Test C changes: `cd c_cal && ./test.sh`
3. Test Python integration: `cd py_box_cal && python3 test.py`

## Project-Specific Patterns

### Precision Calculation
Precision (in bits) is **automatically calculated** based on grid resolution:
```python
required_bits = ceil(log2(1/delta_c)) + 32  # Safety margin
precision = ((required_bits + 63) // 64) * 64  # Round to 64-bit boundary
```
This ensures sufficient precision for the smallest grid spacing. Implemented in `py_box_cal/box_calculator.py:calculate_precision()`.

### Adaptive Iteration Strategy
Unlike typical Mandelbrot calculators, this uses **continuation**:
1. Start with `start_max_iterations` for all points
2. For un-escaped points, **resume from last z value** (not z₀=0)
3. Double iteration count and repeat
4. Stop when no new escapes or hit safety limit (10M iterations)

This dramatically speeds up deep zoom calculations. See `py_box_cal/box_calculator.py:calculate_mandelbrot_grid()`.

### Parallel Execution Architecture
- Worker pool size = CPU count
- Each worker owns a persistent C subprocess
- Thread-safe task queue + result queue pattern
- Workers use locks to synchronize subprocess I/O
- Key classes: `MandelbrotWorker`, `MandelbrotPool`

### CSV Output Format
Grid coordinates (X, Y) are **0-indexed pixel positions** for easy visualization:
```
X,Y,CA,CB,ESCAPED,ITERATIONS,FINAL_ZA,FINAL_ZB
0,0,-2,-2,Y,10,0.1,0.2
```
CA/CB preserve input format, FINAL_ZA/ZB use decimal notation.

## Common Pitfalls

1. **Missing C build**: Python scripts fail if `c_cal/mandelbrot` doesn't exist
2. **Base-32 format errors**: Mixing decimal and base-32 breaks calculations
3. **Python vs python3**: System requires `python3` explicitly
4. **Precision too low**: Grid calculations may need >64 bits for deep zooms
5. **Process cleanup**: Always call `pool.close()` to avoid zombie processes

## File Organization

- `examples.py`: Predefined interesting regions (seahorse_valley, spiral, etc.)
- `QUICK_REFERENCE.md`: User-facing cheat sheet for base-32 format
- `test_*.py`: Unit tests for specific components
- `*.sh`: Shell-based test suites for C code
- `tmp/`: Scratch directory for calculation outputs (gitignored)
