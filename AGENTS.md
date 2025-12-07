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

The Python code requires a virtual environment. Please create and activate it before installing dependencies.

1.  **Create the virtual environment:**
    ```bash
    python3 -m venv .venv
    ```

2.  **Activate the virtual environment:**
    ```bash
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    Once the virtual environment is activated, install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

**Important:** Always ensure the virtual environment is activated before running any Python scripts or installing Python packages.

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

To run the Python tests, make sure your virtual environment is activated, then navigate to the `py_box_cal` directory and run the following command:

```bash
python3 test.py
```
