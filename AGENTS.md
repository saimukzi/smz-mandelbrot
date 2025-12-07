# Agent Instructions for SMZ Mandelbrot

This document provides instructions for agents working on this repository.

## Dependencies

Before working on the code, please ensure you have the following dependencies installed.

### C Dependencies

The C code in the `c_cal` directory requires the `mpfr` and `gmp` libraries. You can install them on Debian/Ubuntu with the following command:

```bash
sudo apt-get update && sudo apt-get install -y libmpfr-dev libgmp-dev
```

### Python Dependencies

The Python code requires the `gmpy2` library. You can install it using pip:

```bash
pip install gmpy2
```

You can also install all the python dependencies using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## Building the C Code

To build the C code, navigate to the `c_cal` directory and run `make`:

```bash
cd c_cal
make
```

## Running Tests

This project has separate test suites for the C and Python code.

### C Tests

To run the full C test suite, navigate to the `c_cal` directory and run the following command:

```bash
./test.sh && ./agent_test.sh && ./manual_test.sh && ./stress_test.sh
```

### Python Tests

To run the Python tests, navigate to the `py_box_cal` directory and run the following command:

```bash
python3 test.py
```
