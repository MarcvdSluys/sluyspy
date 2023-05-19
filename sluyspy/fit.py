# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2023  Marc van der Sluys - marc.vandersluys.nl
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


"""Fitting functions for the sluyspy package"""


import numpy as _np


def np_polyfit_chi2(xvals, yvals, order, ysigmas=None):
    """Do a NumPy polyfit and return the fitting coefficients and reduced chi squared.
    
    Parameters:
      xvals (float):    X values.
      yvals (float):    Y values.
      order (int):      Polynomial order for fit.
      ysigmas (float):  Uncertainties (errors, standard deviations) in the y values.
    
    Returns:
      (tuple):  Tuple consisting of (coefs, red_chi2):
    
      - coefs (float):     Array of fitting coefficients, with length (order+1).
      - red_chi2 (float):  Reduced chi squared (chi^2 / (n-m)) for the fit.
    """
    
    if ysigmas is None:
        coefs, resids, rank, sing_vals, rcond = _np.polyfit(xvals, yvals, order, full=True)  # Note, not 1/sigma**2!
    else:
        coefs, resids, rank, sing_vals, rcond = _np.polyfit(xvals, yvals, order, w=1/ysigmas, full=True)  # Note, not 1/sigma**2!
    
    chi2 = resids[0]                    # Chi^2
    red_chi2 = chi2/(len(xvals)-rank)   # Reduced chi^2 = chi^2 / (n-m)
    
    return coefs, red_chi2
