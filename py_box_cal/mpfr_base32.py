"""
MPFR Base-32 Conversion Utilities

Functions for converting between Python Decimal objects and MPFR base-32 string format.
"""

import math
from decimal import Decimal, getcontext


def parse_mpfr_base32(s: str) -> Decimal:
    """
    Parse an MPFR base-32 string to a Python Decimal.
    Supports formats:
    - Plain: "1a" or "-1a"  
    - With decimal point: "1.a" or "-1.a" or "0.00001a"
    - With exponent: "1a@2" (mantissa × 32^exponent)
    """
    getcontext().prec = 100  # High precision for Decimal operations
    
    if s == '0' or s == '0@0':
        return Decimal(0)
    
    # Parse sign
    if s.startswith('-'):
        sign = -1
        s = s[1:]
    else:
        sign = 1
    
    # Split into mantissa and exponent parts
    if '@' in s:
        mantissa_str, exp_str = s.split('@')
        base_exponent = int(exp_str)
    else:
        mantissa_str = s
        base_exponent = 0
    
    # Parse mantissa (may contain decimal point)
    if '.' in mantissa_str:
        integer_part, fractional_part = mantissa_str.split('.')
    else:
        integer_part = mantissa_str
        fractional_part = ''
    
    # Convert integer part from base-32
    integer_value = Decimal(0)
    for digit in integer_part:
        if digit.isdigit():
            digit_value = int(digit)
        else:
            digit_value = ord(digit.lower()) - ord('a') + 10
        integer_value = integer_value * 32 + Decimal(digit_value)
    
    # Convert fractional part from base-32
    fractional_value = Decimal(0)
    for i, digit in enumerate(fractional_part):
        if digit.isdigit():
            digit_value = int(digit)
        else:
            digit_value = ord(digit.lower()) - ord('a') + 10
        fractional_value += Decimal(digit_value) * (Decimal(32) ** (-(i + 1)))
    
    # Combine and apply exponent
    mantissa_value = integer_value + fractional_value
    if base_exponent != 0:
        mantissa_value *= (Decimal(32) ** base_exponent)
    
    result = sign * mantissa_value
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
