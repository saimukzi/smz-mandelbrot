# Mandelbrot Set Calculator

A C program for calculating the Mandelbrot set using arbitrary-precision arithmetic with the GNU MPFR library.

## Requirements

- GCC compiler
- GNU MPFR library
- GNU GMP library (dependency of MPFR)

### Installing Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get install libmpfr-dev libgmp-dev
```

#### Fedora/RHEL
```bash
sudo dnf install mpfr-devel gmp-devel
```

#### macOS (using Homebrew)
```bash
brew install mpfr gmp
```

## Building

To compile the program, run:

```bash
cd c_cal
make
```

This will create the `mandelbrot` executable.

To clean up:

```bash
make clean
```

## Usage

The program reads commands from stdin and writes results to stdout.

### Commands

#### Calculation Command

**Input Format:**
```
CAL <precision> <za> <zb> <ca> <cb> <max_iterations> <escape_radius>
```

- `<precision>`: Precision in bits for MPFR calculations
- `<za>`, `<zb>`: Real and imaginary parts of z₀ (base-32 strings)
- `<ca>`, `<cb>`: Real and imaginary parts of c (base-32 strings)
- `<max_iterations>`: Maximum number of iterations
- `<escape_radius>`: Escape radius R (base-32 string)

**Output Format:**
```
CAL <escaped> <final_za> <final_zb> <iterations>
```

- `<escaped>`: 'Y' if escaped, 'N' otherwise
- `<final_za>`, `<final_zb>`: Final z value (base-32 strings)
- `<iterations>`: Number of iterations performed

#### Exit Command

**Input Format:**
```
EXIT
```

**Output Format:**
```
EXIT
```

#### Error Handling

Invalid commands will produce:
```
BAD_CMD
```

### Example Usage

```bash
./mandelbrot << EOF
CAL 64 0 0 0 0 100 2
CAL 128 0.1@1 0.2@1 -0.5@1 0 1000 2
EXIT
EOF
```

### Interactive Usage

```bash
./mandelbrot
CAL 64 0 0 0 0 100 2
# Output: CAL N 0@0 0@0 100
EXIT
# Output: EXIT
```

## Algorithm

The program implements the Mandelbrot iteration formula:

$$z_{n+1} = z_n^2 + c$$

Starting with z₀ and c provided in the input, the program iterates up to `max_iterations` times or until |z_n| > R (escape radius).

## Base-32 Number Format

Numbers are represented in base-32 format using MPFR's string representation:
- Format: `[sign]mantissa@exponent`
- Example: `1a@2` represents the mantissa "1a" (base-32) times 32²
- Example: `0` represents zero
- Example: `-f@1` represents a negative number

## Testing

Three test scripts are provided to verify the program's functionality:

### 1. Automated Test Suite (`test.sh`)

Runs a comprehensive suite of 25+ automated tests covering:
- Command parsing (EXIT, CAL, invalid commands)
- Edge cases (zero iterations, negative values, invalid input)
- Escape detection
- Base-32 number handling
- Multiple command sequences

```bash
cd c_cal
./test.sh
```

The script will display colored output showing which tests passed (green ✓) or failed (red ✗), along with a final summary.

### 2. Manual Test Script (`manual_test.sh`)

Runs 10 common test cases with visible input/output for manual verification:

```bash
cd c_cal
./manual_test.sh
```

This is useful for understanding the program's behavior and debugging.

### 3. Stress Test Script (`stress_test.sh`)

Tests edge cases and performance limits:
- Very high precision (1024 bits)
- Large iteration counts (100,000+)
- Boundary conditions
- Famous Mandelbrot set points
- Precision comparisons

```bash
cd c_cal
./stress_test.sh
```

### Running All Tests

To build and run all tests:

```bash
cd c_cal
make
./test.sh && ./manual_test.sh && ./stress_test.sh
```

## License

This is free and unencumbered software released into the public domain.
