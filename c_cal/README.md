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
- `<za>`, `<zb>`: Real and imaginary parts of z₀ (base-32 format)
- `<ca>`, `<cb>`: Real and imaginary parts of c (base-32 format)
- `<max_iterations>`: Maximum number of iterations
- `<escape_radius>`: Escape radius R (base-32 format)

**Output Format:**
```
CAL <escaped> <final_za> <final_zb> <iterations>
```

- `<escaped>`: 'Y' if escaped, 'N' otherwise
- `<final_za>`, `<final_zb>`: Final z value (base-32 decimal notation)
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

#### Verbose Calculation Command (CAL_VERBOSE)

**Input Format:**
```
CAL_VERBOSE <precision> <za> <zb> <ca> <cb> <max_iterations> <escape_radius>
```

Parameters are the same as the `CAL` command.

**Output Format:**
For each iteration, outputs:
```
CAL_STEP <za> <zb> <iteration_number>
```

After all iterations, outputs the same final result as `CAL`:
```
CAL <escaped> <final_za> <final_zb> <iterations>
```

**Example:**
```bash
./mandelbrot << EOF
CAL_VERBOSE 64 0 0 -1 0 5 2
EXIT
EOF
```

**Output:**
```
CAL_STEP -1 0 1
CAL_STEP 0 0 2
CAL_STEP -1 0 3
CAL_STEP 0 0 4
CAL_STEP -1 0 5
CAL N 0 0 5
EXIT
```

This shows the oscillating behavior of the point c = -1, where z alternates between -1 and 0.

**Note:** Actual output format uses base-32 decimal notation (e.g., `-0.g` for -0.5), but the example above is simplified for clarity.

#### Error Handling

Invalid commands will produce:
```
BAD_CMD
```

### Example Usage

```bash
./mandelbrot << EOF
CAL 64 0 0 0 0 100 2
CAL 128 0.1 0.2 -0.5 0 1000 2
EXIT
EOF
```

**Note:** You can also use integer notation (e.g., `1a` for 26) for input. Output will always use decimal notation.

### Interactive Usage

```bash
./mandelbrot
CAL 64 0 0 0 0 100 2
# Output: CAL N 0 0 100
EXIT
# Output: EXIT
```

## Algorithm

The program implements the Mandelbrot iteration formula:

$$z_{n+1} = z_n^2 + c$$

Starting with z₀ and c provided in the input, the program iterates up to `max_iterations` times or until |z_n| > R (escape radius).

## Base-32 Number Format

Numbers are represented in base-32 format with decimal point notation:

### Input Format (Flexible)

The program accepts multiple base-32 input formats:
- **Decimal notation**: `1a.b` (with decimal point) - e.g., `b` = 11, `-0.g` = -0.5
- **Integer notation**: `1a` (without decimal point) - e.g., `b` = 11
- **Zero**: `0`

### Output Format

The program outputs numbers in **decimal point notation**:
- Format: `[sign]integer.fractional` or `[sign]integer`
- Examples:
  - `b` = 11 (decimal: 11)
  - `-0.g` = -0.5 (decimal: -0.5)
  - `1a.5` = 58.15625 (decimal: 26 + 5/32)
  - `0.00001a` ≈ 0.0000000391 (very small number)

This format ensures consistent round-trip conversion and avoids ambiguity in parsing.

## Testing

Three test scripts are provided to verify the program's functionality:

### 1. Automated Test Suite (`test.sh`)

Runs a comprehensive suite of 33 automated tests covering:
- Command parsing (EXIT, CAL, CAL_VERBOSE, invalid commands)
- Edge cases (zero iterations, negative values, invalid input)
- Escape detection
- Base-32 number handling
- Multiple command sequences
- Verbose output validation

```bash
cd c_cal
./test.sh
```

The script will display colored output showing which tests passed (green ✓) or failed (red ✗), along with a final summary.

### 2. Agent Test Suite (`agent_test.sh`)

Runs 9 specialized tests focusing on:
- Edge cases (negative escape radius, zero escape radius)
- Invalid inputs (@Inf@, @NaN@)
- Cycling points
- CAL_VERBOSE functionality

```bash
cd c_cal
./agent_test.sh
```

### 3. Manual Test Script (`manual_test.sh`)

Runs 13 common test cases with visible input/output for manual verification:

```bash
cd c_cal
./manual_test.sh
```

This is useful for understanding the program's behavior and debugging, including demonstrations of CAL_VERBOSE output.

### 4. Stress Test Script (`stress_test.sh`)

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
./test.sh && ./agent_test.sh && ./manual_test.sh && ./stress_test.sh
```

## Implementation Notes

- The `CAL_VERBOSE` command uses the same `process_cal_command()` function as `CAL`, with a verbose flag parameter to enable step-by-step output
- Both commands share the same input validation and calculation logic
- Verbose output is generated during iteration, showing the z value after each step
- All arithmetic operations use MPFR for arbitrary precision

## License

This is free and unencumbered software released into the public domain.
