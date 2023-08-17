# -*- coding: utf-8 -*-
#  
#  This file is part of the sluyspy Python package:
#  Marc van der Sluys' personal Python modules.
#  See: https://github.com/MarcvdSluys/sluyspy
#  
#  This code was shamelessly copied from https://bitbucket.org/william_rusnack/to-precision/ on 2023-08-17 and
#  only adapted slightly (mostly formatting) to my (MvdSs) taste.  The reason for shamelessly copying is that
#  the code does not seem to be available as a PyPI package, which makes it hard to distribute to whereever
#  I'd like to use it (which is exactly the point of this package).  I did not find a licence, but contacted
#  the authors about this.  All the thinking was done by the original authors and the copyright and
#  intellectual properties are theirs:
#  
#  - William Rusnack github.com/BebeSparkelSparkel linkedin.com/in/williamrusnack williamrusnack@gmail.com
#  - Eric Moyer github.com/epmoyer eric@lemoncrab.com
#  - Thomas Hladish https://github.com/tjhladish tjhladish@utexas.edu
#
#  References for notation:
#  - https://www.mathsisfun.com/numbers/scientific-notation.html
#  - https://www.mathsisfun.com/definitions/standard-notation.html



"""Return a value as a formatted string with the desired precision."""

__author__ = """
William Rusnack github.com/BebeSparkelSparkel linkedin.com/in/williamrusnack williamrusnack@gmail.com
Eric Moyer github.com/epmoyer eric@lemoncrab.com
Thomas Hladish https://github.com/tjhladish tjhladish@utexas.edu
"""

from math import floor, log10


def to_precision(value, precision, notation='auto', delimiter='e', auto_limit=3, strip_zeros=False,
                 preserve_int=False):
    """Return a value as a formatted string with the desired precision.
    
    Parameters:
      value (float):    Value to print.
      precision (int):  Number of significant digits to use.
      notation (str):   Notation to use:
                        - 'auto': use standard notation when abs(power) < auto_limit, scientific notation otherwise;
                        - 'sci' or 'scientific': use scientific notation;
                        - 'std' or 'standard': use standard notation.
    
      delimiter (str):      Delimiter between value and exponent (optional, defaults to 'e').
      auto_limit (int):     When abs(power) exceeds this limit, 'auto' mode will return scientific notation (optional, defaults to 3).
      strip_zeros (bool):   Remove trailing decimal zeros (optional, defaults to False).
      preserve_int (bool):  Preserve all digits when returning values that have no decimal component for 'std' (optional, defaults to False).
    
    References:
        ref: https://www.mathsisfun.com/definitions/standard-notation.html
        ref: https://www.mathsisfun.com/numbers/scientific-notation.html
    """
    
    is_neg, sig_digits, dot_power, ten_power = _sci_decompose(value, precision)
    
    if notation == 'auto':
        if abs(ten_power) < auto_limit:
            converter = _std_notation
        else:
            converter = _sci_notation
    
    elif notation in ('sci', 'scientific'):
        converter = _sci_notation
    
    elif notation in ('std', 'standard'):
        converter = _std_notation
    
    else:
        raise ValueError('Unknown notation: ' + str(notation))
    
    return converter(value, precision, delimiter, strip_zeros, preserve_int)


def _std_notation(value, precision, _, strip_zeros, preserve_int):
    """Return standard notation.
    ref: https://www.mathsisfun.com/definitions/standard-notation.html
    
    Parameters:
      value (float):        Value to print.
      precision (int):      Number of significant digits to use.
      strip_zeros (bool):   Remove trailing decimal zeros (optional, defaults to False).
      preserve_int (bool):  Preserve all digits when returning values that have no decimal component for 'std' (optional, defaults to False).
    """
    
    sig_digits, power, is_neg = _number_profile(value, precision)
    result = ('-' if is_neg else '') + _place_dot(sig_digits, power, strip_zeros)
    
    if preserve_int and ('.' not in result):
        # Result was an integer, preserve all digits
        result = '{:0.0f}'.format(value)
    
    return result


def _sci_notation(value, precision, delimiter, strip_zeros, _):
    """Return scientific notation.
    ref: https://www.mathsisfun.com/numbers/scientific-notation.html
    
    Parameters:
      value (float):    Value to print.
      precision (int):  Number of significant digits to use.
      delimiter (str):  Delimiter between value and exponent (optional, defaults to 'e').
      strip_zeros (bool):   Remove trailing decimal zeros (optional, defaults to False).
    """
    
    is_neg, sig_digits, dot_power, ten_power = _sci_decompose(value, precision)
    
    return ('-' if is_neg else '') + _place_dot(sig_digits, dot_power, strip_zeros) + delimiter + str(ten_power)


def _sci_decompose(value, precision):
    """Return the properties to construct a scientific notation number.
    
    Parameters:
      value (float):    Value to print.
      precision (int):  Number of significant digits to use.
    
    Note: created by William Rusnack.
    """
    
    value = float(value)
    sig_digits, power, is_neg = _number_profile(value, precision)
    
    dot_power = -(precision - 1)
    ten_power = power + precision - 1
    
    return is_neg, sig_digits, dot_power, ten_power


def _place_dot(digits, power, strip_zeros=False):
    """Place the dot in the correct spot in the digits/  If the dot is outside the range of the digits, zeros
    will be added.  If strip_zeros is set, trailing decimal zeros will be removed.
    
    Examples:
      _place_dot('123',   2, False) => '12300'
      _place_dot('123',  -2, False) => '1.23'
      _place_dot('123',   3, False) => '0.123'
      _place_dot('123',   5, False) => '0.00123'
      _place_dot('120',   0, False) => '120.'
      _place_dot('1200', -2, False) => '12.00'
      _place_dot('1200', -2, True ) => '12'
      _place_dot('1200', -1, False) => '120.0'
      _place_dot('1200', -1, True ) => '120'
    
    Note: created by William Rusnack.
    """
    
    if power > 0:
        out = digits + '0' * power
    
    elif power < 0:
        power = abs(power)
        precision = len(digits)
        
        if power < precision:
            out = digits[:-power] + '.' + digits[-power:]
            
        else:
            out = '0.' + '0' * (power - precision) + digits
        
    else:
        out = digits + ('.' if digits[-1] == '0' and len(digits) > 1 else '')
    
    if strip_zeros and '.' in out:
        out = out.rstrip('0').rstrip('.')
    
    return out


def _number_profile(value, precision):
    """
    Parameters:
      value (float):    Value to print.
      precision (int):  Number of significant digits to use.
    
    Returns:
      (tuple):  Tuple containing (sig_digits, int(-power), is_neg):
    
      - (str):   string of significant digits.
      - (int):   10s exponent to get the dot to the proper location in the significant digits.
      - (bool):  True if value is less than zero.

    Note:
    - created by William Rusnack;
    - contributions by Thomas Hladish - Issue: github.com/BebeSparkelSparkel/to-precision/issues/5.
    """
    
    value = float(value)
    is_neg = value < 0
    value = abs(value)
    
    if value == 0:
        sig_digits = '0' * precision
        power = -(1 - precision)
    
    else:
        power = -1 * floor(log10(value)) + precision - 1
        
        value_power = value * 10.0**power
        if value < 1 and \
           floor(log10(int(round(value_power)))) > \
           floor(log10(int(value_power))):
            power -= 1
        
        sig_digits = str(int(round(value * 10.0**power)))  # cannot use value_power because power is changed
    
    return sig_digits, int(-power), is_neg

