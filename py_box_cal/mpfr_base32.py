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


def decimal_to_mpfr_base32(d: Decimal, precision: int = 50) -> str:
    """
    Convert a Python Decimal to MPFR base-32 string format in decimal notation.
    Outputs format similar to C implementation: "0.g", "a", "100", etc.
    
    Args:
        d: Decimal value to convert
        precision: Number of base-32 digits to generate (default: 50)
    
    Returns:
        Base-32 string in decimal notation
    """
    getcontext().prec = 100
    
    if d == 0:
        return "0"
    
    # Determine sign
    sign = "-" if d < 0 else ""
    d = abs(d)
    
    # Find the exponent (position of most significant digit)
    # exp is the number of digits before the radix point
    if d >= 1:
        exp = 0
        temp = d
        while temp >= 1:
            temp /= Decimal(32)
            exp += 1
    else:
        exp = 0
        temp = d
        while temp < Decimal(1):
            temp *= Decimal(32)
            exp -= 1
        exp += 1  # Adjust because we went one too far
    
    # Generate base-32 digits
    digits = []
    value = d
    
    # Start from the most significant digit position
    for i in range(precision):
        digit_pos = exp - 1 - i
        scale = Decimal(32) ** digit_pos
        digit = int(value / scale)
        digit = digit % 32
        
        if digit < 10:
            digits.append(str(digit))
        else:
            digits.append(chr(ord('a') + digit - 10))
        
        value -= digit * scale
        
        # Stop if value becomes zero
        if value == 0:
            break
    
    # Remove trailing zeros
    while len(digits) > 1 and digits[-1] == '0':
        digits.pop()
    
    # Build result with decimal point
    digits_str = ''.join(digits)
    
    if exp > 0:
        # Positive exponent: digits before decimal point
        if exp >= len(digits_str):
            # Need trailing zeros
            result = digits_str + '0' * (exp - len(digits_str))
        else:
            # Insert decimal point
            integer_part = digits_str[:exp]
            fractional_part = digits_str[exp:]
            if fractional_part and fractional_part != '0':
                result = integer_part + '.' + fractional_part
            else:
                result = integer_part
    else:
        # Negative or zero exponent: leading zeros after decimal point
        result = '0.' + '0' * (-exp) + digits_str
    
    return sign + result
