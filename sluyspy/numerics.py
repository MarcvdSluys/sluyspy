# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2024  Marc van der Sluys - Nikhef/Utrecht University - marc.vandersluys.nl
#  
#  This file is part of the sluyspy Python package:
#  Marc van der Sluys' personal Python modules.
#  See: https://github.com/MarcvdSluys/sluyspy
#  
#  This is free software: you can redistribute it and/or modify it under the terms of the European Union
#  Public Licence 1.2 (EUPL 1.2).  This software is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.  See the EU Public Licence for more details.  You should have received a copy of the European
#  Union Public Licence along with this code.  If not, see <https://www.eupl.eu/1.2/en/>.


"""Numerics stuff for the sluyspy package"""


import numpy as _np
import astroconst as _ac


eps  = _np.finfo(_np.float64).eps;  """Smallest value for which 1+eps != 1:  2.2204460492503131e-16"""
eps1 = 1 + eps;                     """Smallest value larger than 1:  1 + 2.2204460492503131e-16"""
tiny = _np.nextafter(0, 1);         """Smallest value larger than 0: 4.9406564584124654e-324"""


def sigdig(num, dig=14):
    """Return a string with a given number using (at most) the specified number of significant digits.
    
    Parameters:
      num (float):  Number to print.
      dig (int):    Number of significant digits to use (optional; defaults to 14 to avoid machine rounding).
    
    Returns:
      (struct):  Struct containing command-line arguments.
    
    Note:
      - Trailing zeros are NOT printed - hence, this function does not EXACTLY print the desired number of
        significant digits;
      - 0.075 with a single digit is printed as 0.07, hence multiply with eps1!
    
    See:
      E.g. the discussions here: https://stackoverflow.com/q/3410976/1386750
    """
    
    if num is None:
        sigdig = 'None'
    else:
        fmt = '%%0.%ig' % (dig)
        sigdig = fmt % (num * eps1)  # w/o snum.eps1, (0.075,1) will be written as 0.07!
        
    return sigdig


def map_pi_pi(ang):
    """Map an (array of) angle(s) to lie between -PI and +PI.

    Parameters:
      ang (float):  (Array of) angle(s).
    
    Returns:
      (float):  (Array) of angles between -PI and +PI.
    """
    
    return _np.mod(ang+_ac.pi, _ac.pi2)-_ac.pi


def nint(val):
    """Convert a float to the nearest integer with proper rounding.
    
    Parameters:
      val (float):  Value to convert.
    
    Returns:
      (int):  Nearest integer (or float('nan')).
    """
    
    if _np.isnan(val):
        nint = float('nan')
    else:
        nint = int(_np.round(val,0))
        
    return nint
