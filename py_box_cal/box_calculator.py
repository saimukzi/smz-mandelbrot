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
import argparse
from multiprocessing import cpu_count
from typing import List, Tuple, Dict, Optional
import threading
import queue
from pathlib import Path

# Add py_common to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'py_common'))

import gmpy2

from mpfr_base32 import parse_mpfr_base32, decimal_to_mpfr_base32  # type: ignore


def _count_base32_digits(s: str) -> int:
    """Count alphanumeric characters in a base-32 string.

    This treats only letters and digits as base-32 'digits', ignoring sign
    and the radix point. Returns an integer count.
    """
    return sum(1 for c in s if c.isalnum())


def calculate_precision(min_ca: str, max_ca: str, min_cb: str, max_cb: str, 
                       resolution_ca: int, resolution_cb: int) -> int:
    """
    Calculate required MPFR precision in bits based on grid resolution.
    Precision is rounded up to nearest multiple of 64.
    """
    
    # Estimate an initial precision for parsing from the input string lengths.
    # Each base-32 digit encodes ~5 bits. Add a safety margin and round up to
    # a 64-bit boundary for parsing so we can compute deltas reliably.
    max_digits = max(
        _count_base32_digits(min_ca),
        _count_base32_digits(max_ca),
        _count_base32_digits(min_cb),
        _count_base32_digits(max_cb),
    )
    estimated_bits = max_digits * 5
    parse_precision = ((estimated_bits + 64 + 63) // 64) * 64
    parse_precision = max(64, parse_precision)

    # Parse bounds as mpfr objects using the estimated parse precision
    min_ca_dec = parse_mpfr_base32(min_ca, parse_precision)
    max_ca_dec = parse_mpfr_base32(max_ca, parse_precision)
    min_cb_dec = parse_mpfr_base32(min_cb, parse_precision)
    max_cb_dec = parse_mpfr_base32(max_cb, parse_precision)
    
    # Calculate step sizes (max bounds are exclusive)
    if resolution_ca > 1 and resolution_cb > 1:
        res_ca = gmpy2.mpfr(resolution_ca)  # type: ignore
        res_cb = gmpy2.mpfr(resolution_cb)  # type: ignore
        delta_ca = (max_ca_dec - min_ca_dec) / res_ca
        delta_cb = (max_cb_dec - min_cb_dec) / res_cb
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
                 resolution: int) -> Tuple[List[Tuple[str, str, int, int]], int, int]:
    """
    Generate a grid of c = ca + i*cb points.
    Resolution applies to the real part (ca), and imaginary resolution (cb) is calculated
    based on the aspect ratio of the region.
    Returns tuple of (grid, resolution_ca, resolution_cb) where grid is list of
    (ca, cb, x, y) tuples in MPFR base-32 format with grid coordinates.
    """

    # Determine precision (bits) from the length of the provided base-32 strings.
    # Each base-32 digit encodes ~5 bits. Count alphanumeric characters as digits
    # (this ignores sign and the dot). Add a safety margin and round up to
    # a 64-bit boundary to match the project's precision convention.
    max_digits = max(
        _count_base32_digits(min_ca),
        _count_base32_digits(max_ca),
        _count_base32_digits(min_cb),
        _count_base32_digits(max_cb),
    )

    # Estimate bits: ~5 bits per base-32 digit
    estimated_bits = max_digits * 5
    # Add safety margin (64 bits) and round up to nearest multiple of 64
    precision = ((estimated_bits + 64 + 63) // 64) * 64
    precision = max(64, precision)

    # Parse bounds as mpfr objects with computed precision
    min_ca_dec = parse_mpfr_base32(min_ca, precision)
    max_ca_dec = parse_mpfr_base32(max_ca, precision)
    min_cb_dec = parse_mpfr_base32(min_cb, precision)
    max_cb_dec = parse_mpfr_base32(max_cb, precision)
    
    # Calculate dimensions
    range_ca = abs(max_ca_dec - min_ca_dec)
    range_cb = abs(max_cb_dec - min_cb_dec)
    
    # Resolution applies to real part (ca)
    resolution_ca = resolution
    
    # Calculate imaginary resolution based on aspect ratio
    if range_ca > 0:
        aspect_ratio = float(range_cb / range_ca)
        resolution_cb = max(1, round(resolution_ca * aspect_ratio))
    else:
        resolution_cb = resolution
    
    grid = []
    
    for i in range(resolution_ca):
        for j in range(resolution_cb):
            if resolution_ca > 1:
                # Use gmpy2.mpfr for all arithmetic
                # max_ca is exclusive, so we divide by resolution_ca (not resolution_ca - 1)
                i_mpfr = gmpy2.mpfr(i)  # type: ignore
                res_ca = gmpy2.mpfr(resolution_ca)  # type: ignore
                ca = min_ca_dec + (max_ca_dec - min_ca_dec) * i_mpfr / res_ca
            else:
                ca = min_ca_dec
            
            if resolution_cb > 1:
                j_mpfr = gmpy2.mpfr(j)  # type: ignore
                res_cb = gmpy2.mpfr(resolution_cb)  # type: ignore
                cb = min_cb_dec + (max_cb_dec - min_cb_dec) * j_mpfr / res_cb
            else:
                cb = min_cb_dec
            
            ca_str = decimal_to_mpfr_base32(ca, precision)
            cb_str = decimal_to_mpfr_base32(cb, precision)
            grid.append((ca_str, cb_str, i, j))
    
    return grid, resolution_ca, resolution_cb


class MandelbrotWorker:
    """
    Manages a single mandelbrot process for parallel computation.
    """
    
    def __init__(self, mandelbrot_path: str):
        self.mandelbrot_path = mandelbrot_path
        self.process: Optional[subprocess.Popen[str]] = None
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
            assert self.process and self.process.stdin
            self.process.stdin.write(cmd)
            self.process.stdin.flush()
            
            # Read response
            assert self.process.stdout
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
            if self.process and self.process.stdin:
                self.process.stdin.write("EXIT\n")
                self.process.stdin.flush()
                self.process.wait()


class MandelbrotPool:
    """
    Pool of mandelbrot worker processes for parallel computation.
    """
    
    def __init__(self, mandelbrot_path: str, num_workers: Optional[int] = None):
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
    
    # Generate grid (this also calculates resolutions)
    grid, resolution_ca, resolution_cb = generate_grid(min_ca, max_ca, min_cb, max_cb, resolution)
    total_points = len(grid)
    print(f"Grid size: {resolution_ca}x{resolution_cb} = {total_points} points", file=sys.stderr)
    
    # Calculate precision
    precision = calculate_precision(min_ca, max_ca, min_cb, max_cb, resolution_ca, resolution_cb)
    print(f"Using precision: {precision} bits", file=sys.stderr)
    
    # Initialize results storage
    results = {}
    for idx, (ca, cb, x, y) in enumerate(grid):
        results[idx] = {
            'ca': ca,
            'cb': cb,
            'x': x,
            'y': y,
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
        # Find points that haven't escaped and still need more iterations
        # (we treat `max_iterations` as the target cumulative iterations for this round)
        unescape_indices = [
            idx for idx in range(total_points)
            if results[idx]['escaped'] == 'N'
            and results[idx]['iterations'] < max_total_iterations
            and results[idx]['iterations'] < max_iterations
        ]
        
        if not unescape_indices:
            print("All points processed", file=sys.stderr)
            break
        
        print(f"Iteration round: max_iterations={max_iterations}, processing {len(unescape_indices)} points", 
              file=sys.stderr)
        
        # Submit tasks for unescape points. Send the number of iterations to run
        # in this round (the difference between the target `max_iterations`
        # and the point's current cumulative iterations), so we don't re-run
        # iterations that were already performed.
        for idx in unescape_indices:
            r = results[idx]
            iterations_to_run = int(max_iterations - r['iterations'])
            if iterations_to_run <= 0:
                continue
            pool.submit(idx, precision, r['za'], r['zb'], r['ca'], r['cb'],
                       iterations_to_run, escape_radius)
        
        # Wait and collect results
        pool.wait()
        batch_results = pool.get_results(len(unescape_indices))
        
        # Track number of newly escaped points
        newly_escaped = 0
        
        # Update results
        for res in batch_results:
            idx = res['idx']
            results[idx]['escaped'] = res['escaped']
            results[idx]['final_za'] = res['final_za']
            results[idx]['final_zb'] = res['final_zb']
            results[idx]['iterations'] += res['iterations']
            
            # Count newly escaped points
            if res['escaped'] == 'Y':
                newly_escaped += 1
            
            # Update z0 for next iteration
            results[idx]['za'] = res['final_za']
            results[idx]['zb'] = res['final_zb']
        
        # Calculate escape percentage
        escape_percentage = (newly_escaped / len(unescape_indices)) * 100
        
        # Check if no points escaped in this round
        if newly_escaped == 0:
            print(f"No new escaped points after {len(unescape_indices)} iterations, stopping", file=sys.stderr)
            break
        
        # Check if less than 1% escaped
        if escape_percentage < 1.0:
            print(f"Less than 1% of points escaped ({escape_percentage:.2f}%), stopping", file=sys.stderr)
            break
        
        print(f"Points escaped in this round: {newly_escaped}/{len(unescape_indices)} ({escape_percentage:.2f}%)", file=sys.stderr)
        
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
        fieldnames = ['X', 'Y', 'CA', 'CB', 'ESCAPED', 'ITERATIONS', 'FINAL_ZA', 'FINAL_ZB']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx in range(total_points):
            r = results[idx]
            writer.writerow({
                'X': r['x'],
                'Y': r['y'],
                'CA': r['ca'],
                'CB': r['cb'],
                'ESCAPED': r['escaped'],
                'ITERATIONS': r['iterations'],
                'FINAL_ZA': r['final_za'],
                'FINAL_ZB': r['final_zb']
            })
    
    print("Calculation complete!", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Mandelbrot Set Grid Calculator - Calculates Mandelbrot set membership for a grid of c values',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  %(prog)s -2 -2 2 2 --resolution 100 --start-max-iterations 1000 --escape-radius 2 output.csv
        """
    )
    
    parser.add_argument('min_ca', type=str,
                        help='Minimum value for CA (real part) in MPFR base-32 format')
    parser.add_argument('min_cb', type=str,
                        help='Minimum value for CB (imaginary part) in MPFR base-32 format')
    parser.add_argument('max_ca', type=str,
                        help='Maximum value for CA (real part) in MPFR base-32 format')
    parser.add_argument('max_cb', type=str,
                        help='Maximum value for CB (imaginary part) in MPFR base-32 format')
    parser.add_argument('resolution', type=int,
                        help='Grid resolution for real part (ca). Imaginary resolution calculated by aspect ratio.')
    parser.add_argument('start_max_iterations', type=int,
                        help='Starting maximum iterations for Mandelbrot calculation')
    parser.add_argument('escape_radius', type=str,
                        help='Escape radius in MPFR base-32 format')
    parser.add_argument('output_path', type=str,
                        help='Output CSV file path')
    
    args = parser.parse_args()
    
    calculate_mandelbrot_grid(args.min_ca, args.max_ca, args.min_cb, args.max_cb,
                             args.resolution, args.start_max_iterations,
                             args.escape_radius, args.output_path)


if __name__ == '__main__':
    main()
