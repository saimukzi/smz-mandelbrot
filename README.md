# SMZ Mandelbrot

A high-performance Mandelbrot set calculator with arbitrary-precision arithmetic support.

## Overview

This project provides tools for calculating the Mandelbrot set with arbitrary precision using MPFR (Multiple Precision Floating-Point Reliable) library. It consists of two main components:

1. **c_cal** - A fast C-based calculator for individual point calculations
2. **py_box_cal** - A Python-based grid calculator with parallel execution and adaptive iteration

## Components

### c_cal - Core Calculator

A C program that performs high-precision Mandelbrot calculations for individual points.

**Features:**
- Arbitrary-precision arithmetic using GNU MPFR
- Base-32 number format for compact representation
- Command-based interface (CAL, CAL_VERBOSE, EXIT)
- Optimized for continuous calculation via stdin/stdout

**Documentation:** See [c_cal/README.md](c_cal/README.md)

### py_box_cal - Grid Calculator

A Python program that calculates the Mandelbrot set for entire grids of points using parallel execution.

**Features:**
- Automatic precision calculation based on grid resolution
- Parallel execution using all CPU cores
- Adaptive iteration with intelligent continuation
- CSV output format for easy visualization
- Predefined examples of interesting Mandelbrot regions

**Documentation:** See [py_box_cal/README.md](py_box_cal/README.md)

## Quick Start

### 1. Build the C Calculator

```bash
cd c_cal
make
```

### 2. Test the C Calculator

```bash
cd c_cal
./test.sh
```

### 3. Run a Grid Calculation

```bash
cd py_box_cal
python3 examples.py classic
```

This will generate a 100×100 grid of the classic Mandelbrot view and save it to `classic_mandelbrot.csv`.

## Use Cases

### Individual Point Calculations

Use `c_cal/mandelbrot` for:
- Real-time interactive exploration
- Single point queries
- Integration into other programs
- When you need full control over the iteration process

### Grid Calculations

Use `py_box_cal/box_calculator.py` for:
- Generating visualization data
- Batch processing of multiple points
- Zooming into interesting regions
- Creating datasets for analysis

## Example Usage

### Calculate a Single Point

```bash
cd c_cal
echo "CAL 64 0 0 0 0 100 2" | ./mandelbrot
# Output: CAL N 0@0 0@0 100
```

### Calculate a Grid

```bash
cd py_box_cal
python3 box_calculator.py -2 -1.5@0 1 1.5@0 50 1000 2 output.csv
```

### Run Predefined Examples

```bash
cd py_box_cal
python3 examples.py list  # Show available examples
python3 examples.py seahorse_valley 80  # Generate 80×80 grid
```

## Number Format

Both tools use **MPFR base-32 format** for arbitrary precision:

- Format: `[sign]mantissa@exponent`
- Example: `1a@2` = mantissa "1a" (base-32) × 32²
- Example: `0` = zero
- Example: `-f@1` = negative number

Base-32 digits: 0-9, a-v (where a=10, b=11, ..., v=31)

## Algorithm

The Mandelbrot iteration formula:

$$z_{n+1} = z_n^2 + c$$

A point $c$ is in the Mandelbrot set if the sequence $z_0, z_1, z_2, \ldots$ (starting with $z_0 = 0$) remains bounded.

In practice, we iterate until:
1. $|z_n| > R$ (escape radius) → point is **not** in the set
2. Maximum iterations reached → point is **probably** in the set

## Requirements

### C Calculator
- GCC compiler
- GNU MPFR library
- GNU GMP library

### Python Grid Calculator
- Python 3.6+
- Built `c_cal/mandelbrot` executable
- Standard Python libraries only (no external dependencies)

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential libmpfr-dev libgmp-dev python3
```

**Fedora/RHEL:**
```bash
sudo dnf install gcc make mpfr-devel gmp-devel python3
```

**macOS:**
```bash
brew install gcc mpfr gmp python3
```

## Performance

The grid calculator automatically:
- Uses all available CPU cores for parallel execution
- Implements adaptive iteration (only recalculates un-escaped points)
- Continues from last z value (avoids redundant calculations)
- Adjusts precision based on grid resolution

Typical performance on modern hardware:
- **100×100 grid**: ~10-30 seconds
- **500×500 grid**: ~10-30 minutes
- **1000×1000 grid**: ~1-3 hours

(Performance varies based on region complexity and iteration counts)

## Testing

Both components include comprehensive test suites:

```bash
# Test C calculator
cd c_cal
./test.sh && ./agent_test.sh && ./manual_test.sh

# Test Python calculator
cd py_box_cal
python3 test.py
```

## Project Structure

```
smz-mandelbrot/
├── LICENSE                  # Public domain license
├── README.md               # This file
├── c_cal/                  # C calculator
│   ├── mandelbrot.c        # Source code
│   ├── Makefile           # Build configuration
│   ├── README.md          # Detailed documentation
│   ├── test.sh            # Automated tests
│   ├── agent_test.sh      # Agent tests
│   ├── manual_test.sh     # Manual verification
│   └── stress_test.sh     # Performance tests
└── py_box_cal/            # Python grid calculator
    ├── box_calculator.py  # Main grid calculator
    ├── examples.py        # Predefined examples
    ├── test.py           # Test suite
    └── README.md         # Detailed documentation
```

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## License

This is free and unencumbered software released into the public domain.

See the [LICENSE](LICENSE) file for details.

## See Also

- [GNU MPFR Library](https://www.mpfr.org/)
- [Mandelbrot Set on Wikipedia](https://en.wikipedia.org/wiki/Mandelbrot_set)
- [MPFR Documentation](https://www.mpfr.org/mpfr-current/mpfr.html)
