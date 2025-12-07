"""
MPFR Base-32 Conversion Utilities

Functions for converting between gmpy2 mpfr objects and MPFR base-32 string format.
Uses gmpy2 library which provides Python bindings to MPFR, ensuring exact compatibility
with the C implementation.
"""

import gmpy2
from gmpy2 import mpfr  # type: ignore


def remove_trailing_zeros(s: str) -> str:
    """
    Remove trailing zeros from a number string that has a decimal point.
    Also removes the decimal point if no fractional part remains.
    
    Args:
        s: Number string
    
    Returns:
        String with trailing zeros removed
    """
    if '.' not in s:
        return s
    
    # Remove trailing zeros
    s = s.rstrip('0')
    # Remove decimal point if it's now at the end
    s = s.rstrip('.')
    return s


def parse_mpfr_base32(s: str, precision: int = 256) -> mpfr:
    """
    Parse an MPFR base-32 string to a gmpy2 mpfr object.
    Supports formats:
    - Plain: "1a" or "-1a"  
    - With decimal point: "1.a" or "-1.a" or "0.00001a"
    
    Args:
        s: Base-32 string to parse
        precision: Precision in bits for the mpfr object (default: 256)
    
    Returns:
        gmpy2 mpfr object
    """
    # Set precision context
    with gmpy2.context(precision=precision):  # type: ignore
        # gmpy2 can directly parse base-32 strings using mpfr_set_str
        # The format expected by MPFR is the same as our input
        try:
            result = mpfr(s, base=32)
            return result
        except:
            # Fallback: handle special cases or errors
            if s == '0':
                return mpfr(0)
            raise ValueError(f"Cannot parse base-32 string: {s}")


def mpfr_to_base32(value: mpfr, precision_digits: int = 0) -> str:
    """
    Convert a gmpy2 mpfr object to MPFR base-32 string format in decimal notation.
    Outputs format similar to C implementation: "0.g", "a", "100", etc.
    
    Args:
        value: gmpy2 mpfr value to convert
        precision_digits: Number of base-32 digits to generate (0 = automatic based on precision)
    
    Returns:
        Base-32 string in decimal notation
    """
    if value == 0:
        return "0"
    
    # Use gmpy2's digits() function to get base-32 representation
    # This directly calls MPFR's mpfr_get_str, just like the C code
    # digits() returns (mantissa_str, exponent, precision_used)
    mantissa_str, exp, _ = value.digits(32, precision_digits)
    
    # Handle special cases
    if mantissa_str in ['@NaN@', '@Inf@', '-@Inf@']:
        return mantissa_str
    
    # mantissa_str is the mantissa without decimal point
    # exp is the exponent (number of digits before decimal point)
    sign = '-' if mantissa_str.startswith('-') else ''
    if sign:
        mantissa_str = mantissa_str[1:]  # Remove sign from mantissa
    
    mantissa_len = len(mantissa_str)
    
    if exp > 0:
        # Positive exponent: digits before decimal point
        if exp >= mantissa_len:
            # Need trailing zeros (e.g., "100" when mantissa is "1" and exp is 3)
            result = mantissa_str + '0' * (exp - mantissa_len)
        else:
            # Insert decimal point (e.g., "12.34" when mantissa is "1234" and exp is 2)
            integer_part = mantissa_str[:exp]
            fractional_part = mantissa_str[exp:]
            result = integer_part + '.' + fractional_part
    elif exp == 0:
        # All digits after decimal point, starting with non-zero
        result = '0.' + mantissa_str
    else:
        # Negative exponent: leading zeros after decimal point
        result = '0.' + '0' * (-exp) + mantissa_str
    
    result = sign + result
    # Remove trailing zeros before returning
    return remove_trailing_zeros(result)


def decimal_to_mpfr_base32(d, precision_bits: int = 256) -> str:
    """
    Convert a numeric value to MPFR base-32 string format.
    
    Args:
        d: Numeric value to convert (int, float, str, or mpfr)
        precision_bits: Precision in bits for the conversion (default: 256)
    
    Returns:
        Base-32 string in decimal notation
    """
    # Convert to mpfr with specified precision
    with gmpy2.context(precision=precision_bits):  # type: ignore
        if isinstance(d, mpfr):
            value = d
        else:
            value = mpfr(str(d))
        
        # Calculate number of base-32 digits to generate
        # Formula: digits = ceil(bits * log(2) / log(32)) + 1
        import math
        precision_digits = math.ceil(precision_bits * math.log(2) / math.log(32)) + 1
        
        return mpfr_to_base32(value, precision_digits)
