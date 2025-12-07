#!/usr/bin/env python3
"""
Mandelbrot Set Grid Calculator
Calculates Mandelbrot set membership for a grid of c values using parallel
execution of the c_cal/mandelbrot executable with adaptive iteration logic.
"""

import sys
import os
import csv
import subprocess
import math
from decimal import Decimal, getcontext
from multiprocessing import Pool, cpu_count
from typing import List, Tuple, Dict
import threading
import queue


def parse_mpfr_base32(s: str) -> Decimal:
    """
    Parse an MPFR base-32 string to a Python Decimal.
    Format: [sign]mantissa@exponent
    Example: "1a@2" = mantissa "1a" (base-32) * 32^2
    """
    getcontext().prec = 100  # High precision for Decimal operations
    
    if s == '0' or s == '0@0':
        return Decimal(0)
    
    # Split into mantissa and exponent parts
    if '@' not in s:
        mantissa_str = s
        exponent = 0
    else:
        mantissa_str, exp_str = s.split('@')
        exponent = int(exp_str)
    
    # Parse sign
    if mantissa_str.startswith('-'):
        sign = -1
        mantissa_str = mantissa_str[1:]
    else:
        sign = 1
    
    # Convert base-32 mantissa to decimal
    mantissa_value = Decimal(0)
    for i, digit in enumerate(mantissa_str):
        if digit.isdigit():
            digit_value = int(digit)
        else:
            digit_value = ord(digit.lower()) - ord('a') + 10
        mantissa_value += Decimal(digit_value) * (Decimal(32) ** (-i))
    
    # Calculate final value: mantissa * 32^exponent
    result = sign * mantissa_value * (Decimal(32) ** exponent)
    return result


def decimal_to_mpfr_base32(d: Decimal) -> str:
    """
    Convert a Python Decimal to MPFR base-32 string format.
    This is a simplified conversion for generating grid points.
    """
    if d == 0:
        return "0"
    
    # Determine sign
    if d < 0:
        sign = "-"
        d = abs(d)
    else:
        sign = ""
    
    # Find appropriate exponent (power of 32)
    if d >= 1:
        exponent = int(math.log(float(d), 32))
    else:
        exponent = int(math.floor(math.log(float(d), 32)))
    
    # Calculate mantissa
    mantissa = d / (Decimal(32) ** exponent)
    
    # Convert mantissa to base-32 string (14 digits precision)
    mantissa_str = ""
    for _ in range(14):
        digit = int(mantissa)
        if digit < 10:
            mantissa_str += str(digit)
        else:
            mantissa_str += chr(ord('a') + digit - 10)
        mantissa = (mantissa - digit) * 32
        if mantissa == 0:
            break
    
    return f"{sign}{mantissa_str}@{exponent}"


def calculate_precision(min_ca: str, max_ca: str, min_cb: str, max_cb: str, 
                       resolution: int) -> int:
    """
    Calculate required MPFR precision in bits based on grid resolution.
    Precision is rounded up to nearest multiple of 64.
    """
    # Parse bounds
    min_ca_dec = parse_mpfr_base32(min_ca)
    max_ca_dec = parse_mpfr_base32(max_ca)
    min_cb_dec = parse_mpfr_base32(min_cb)
    max_cb_dec = parse_mpfr_base32(max_cb)
    
    # Calculate step sizes
    if resolution > 1:
        delta_ca = (max_ca_dec - min_ca_dec) / (resolution - 1)
        delta_cb = (max_cb_dec - min_cb_dec) / (resolution - 1)
    else:
        # Single point, use reasonable precision
        return 64
    
    # Get minimum step size
    delta_c = min(abs(delta_ca), abs(delta_cb))
    
    if delta_c == 0:
        return 64
    
    # Calculate required bits: log2(1/delta_c) + safety margin
    required_bits = math.ceil(math.log2(float(1 / delta_c))) + 32
    
    # Round up to nearest multiple of 64
    precision = ((required_bits + 63) // 64) * 64
    
    return max(64, precision)  # Minimum 64 bits


def generate_grid(min_ca: str, max_ca: str, min_cb: str, max_cb: str, 
                 resolution: int) -> List[Tuple[str, str]]:
    """
    Generate a grid of c = ca + i*cb points.
    Returns list of (ca, cb) tuples in MPFR base-32 format.
    """
    # Parse bounds
    min_ca_dec = parse_mpfr_base32(min_ca)
    max_ca_dec = parse_mpfr_base32(max_ca)
    min_cb_dec = parse_mpfr_base32(min_cb)
    max_cb_dec = parse_mpfr_base32(max_cb)
    
    grid = []
    
    for i in range(resolution):
        for j in range(resolution):
            if resolution > 1:
                ca = min_ca_dec + (max_ca_dec - min_ca_dec) * Decimal(i) / Decimal(resolution - 1)
                cb = min_cb_dec + (max_cb_dec - min_cb_dec) * Decimal(j) / Decimal(resolution - 1)
            else:
                ca = min_ca_dec
                cb = min_cb_dec
            
            ca_str = decimal_to_mpfr_base32(ca)
            cb_str = decimal_to_mpfr_base32(cb)
            grid.append((ca_str, cb_str))
    
    return grid


class MandelbrotWorker:
    """
    Manages a single mandelbrot process for parallel computation.
    """
    
    def __init__(self, mandelbrot_path: str):
        self.mandelbrot_path = mandelbrot_path
        self.process = None
        self.lock = threading.Lock()
        self._start_process()
    
    def _start_process(self):
        """Start the mandelbrot subprocess."""
        self.process = subprocess.Popen(
            [self.mandelbrot_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    
    def calculate(self, precision: int, za: str, zb: str, ca: str, cb: str,
                 max_iterations: int, escape_radius: str) -> Dict:
        """
        Send CAL command and receive result.
        Returns dict with keys: escaped, final_za, final_zb, iterations
        """
        with self.lock:
            # Send CAL command
            cmd = f"CAL {precision} {za} {zb} {ca} {cb} {max_iterations} {escape_radius}\n"
            self.process.stdin.write(cmd)
            self.process.stdin.flush()
            
            # Read response
            response = self.process.stdout.readline().strip()
            
            # Parse response: CAL <escaped> <final_za> <final_zb> <iterations>
            parts = response.split()
            if len(parts) != 5 or parts[0] != 'CAL':
                raise ValueError(f"Invalid response: {response}")
            
            return {
                'escaped': parts[1],
                'final_za': parts[2],
                'final_zb': parts[3],
                'iterations': int(parts[4])
            }
    
    def close(self):
        """Close the mandelbrot process."""
        with self.lock:
            if self.process:
                self.process.stdin.write("EXIT\n")
                self.process.stdin.flush()
                self.process.wait()


class MandelbrotPool:
    """
    Pool of mandelbrot worker processes for parallel computation.
    """
    
    def __init__(self, mandelbrot_path: str, num_workers: int = None):
        if num_workers is None:
            num_workers = cpu_count()
        
        self.workers = [MandelbrotWorker(mandelbrot_path) for _ in range(num_workers)]
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_threads = []
        self.running = True
    
    def _worker_thread(self, worker: MandelbrotWorker):
        """Worker thread that processes tasks from the queue."""
        while self.running:
            try:
                task = self.task_queue.get(timeout=0.1)
                if task is None:
                    break
                
                idx, precision, za, zb, ca, cb, max_iterations, escape_radius = task
                result = worker.calculate(precision, za, zb, ca, cb, max_iterations, escape_radius)
                result['idx'] = idx
                result['ca'] = ca
                result['cb'] = cb
                self.result_queue.put(result)
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}", file=sys.stderr)
                self.task_queue.task_done()
    
    def start(self):
        """Start worker threads."""
        for worker in self.workers:
            thread = threading.Thread(target=self._worker_thread, args=(worker,))
            thread.start()
            self.worker_threads.append(thread)
    
    def submit(self, idx: int, precision: int, za: str, zb: str, ca: str, cb: str,
              max_iterations: int, escape_radius: str):
        """Submit a calculation task."""
        self.task_queue.put((idx, precision, za, zb, ca, cb, max_iterations, escape_radius))
    
    def get_results(self, count: int) -> List[Dict]:
        """Get results from the result queue."""
        results = []
        for _ in range(count):
            results.append(self.result_queue.get())
        return results
    
    def wait(self):
        """Wait for all tasks to complete."""
        self.task_queue.join()
    
    def close(self):
        """Close all workers and threads."""
        self.running = False
        
        # Signal threads to stop
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Wait for threads
        for thread in self.worker_threads:
            thread.join()
        
        # Close workers
        for worker in self.workers:
            worker.close()


def calculate_mandelbrot_grid(min_ca: str, max_ca: str, min_cb: str, max_cb: str,
                              resolution: int, start_max_iterations: int,
                              escape_radius: str, output_path: str):
    """
    Main calculation function that orchestrates the grid calculation.
    """
    # Find mandelbrot executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mandelbrot_path = os.path.join(os.path.dirname(script_dir), 'c_cal', 'mandelbrot')
    
    if not os.path.exists(mandelbrot_path):
        print(f"Error: mandelbrot executable not found at {mandelbrot_path}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate precision
    precision = calculate_precision(min_ca, max_ca, min_cb, max_cb, resolution)
    print(f"Using precision: {precision} bits", file=sys.stderr)
    
    # Generate grid
    grid = generate_grid(min_ca, max_ca, min_cb, max_cb, resolution)
    total_points = len(grid)
    print(f"Grid size: {resolution}x{resolution} = {total_points} points", file=sys.stderr)
    
    # Initialize results storage
    results = {}
    for idx, (ca, cb) in enumerate(grid):
        results[idx] = {
            'ca': ca,
            'cb': cb,
            'za': '0',
            'zb': '0',
            'escaped': 'N',
            'iterations': 0
        }
    
    # Create worker pool
    num_workers = cpu_count()
    print(f"Starting {num_workers} worker processes", file=sys.stderr)
    pool = MandelbrotPool(mandelbrot_path, num_workers)
    pool.start()
    
    # Adaptive iteration loop
    max_iterations = start_max_iterations
    max_total_iterations = 10000000  # Safety limit
    
    while True:
        # Find points that haven't escaped
        unescape_indices = [idx for idx in range(total_points) 
                           if results[idx]['escaped'] == 'N' 
                           and results[idx]['iterations'] < max_total_iterations]
        
        if not unescape_indices:
            print("All points processed", file=sys.stderr)
            break
        
        print(f"Iteration round: max_iterations={max_iterations}, processing {len(unescape_indices)} points", 
              file=sys.stderr)
        
        # Submit tasks for unescape points
        for idx in unescape_indices:
            r = results[idx]
            pool.submit(idx, precision, r['za'], r['zb'], r['ca'], r['cb'],
                       max_iterations, escape_radius)
        
        # Wait and collect results
        pool.wait()
        batch_results = pool.get_results(len(unescape_indices))
        
        # Update results
        for res in batch_results:
            idx = res['idx']
            results[idx]['escaped'] = res['escaped']
            results[idx]['final_za'] = res['final_za']
            results[idx]['final_zb'] = res['final_zb']
            results[idx]['iterations'] += res['iterations']
            
            # Update z0 for next iteration
            results[idx]['za'] = res['final_za']
            results[idx]['zb'] = res['final_zb']
        
        # Double max_iterations for next round
        max_iterations *= 2
        
        # Check if we've hit the limit
        if max_iterations > max_total_iterations:
            print("Reached maximum iteration limit", file=sys.stderr)
            break
    
    # Close pool
    pool.close()
    
    # Write results to CSV
    print(f"Writing results to {output_path}", file=sys.stderr)
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['CA', 'CB', 'ESCAPED', 'ITERATIONS', 'FINAL_ZA', 'FINAL_ZB']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx in range(total_points):
            r = results[idx]
            writer.writerow({
                'CA': r['ca'],
                'CB': r['cb'],
                'ESCAPED': r['escaped'],
                'ITERATIONS': r['iterations'],
                'FINAL_ZA': r['final_za'],
                'FINAL_ZB': r['final_zb']
            })
    
    print("Calculation complete!", file=sys.stderr)


def main():
    if len(sys.argv) != 9:
        print("Usage: box_calculator.py <min_ca> <min_cb> <max_ca> <max_cb> "
              "<resolution> <start_max_iterations> <escape_radius> <output_path>",
              file=sys.stderr)
        sys.exit(1)
    
    min_ca = sys.argv[1]
    min_cb = sys.argv[2]
    max_ca = sys.argv[3]
    max_cb = sys.argv[4]
    resolution = int(sys.argv[5])
    start_max_iterations = int(sys.argv[6])
    escape_radius = sys.argv[7]
    output_path = sys.argv[8]
    
    calculate_mandelbrot_grid(min_ca, max_ca, min_cb, max_cb, resolution,
                             start_max_iterations, escape_radius, output_path)


if __name__ == '__main__':
    main()
