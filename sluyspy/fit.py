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


def scipy_curvefit(fit_fun, xvals, yvals, coefs0, sigmas=None, verbosity=1):
    """Do a fit using SciPy's curve_fit, and print some auxilary parameters if desired.
    
    Parameters:
      fit_fun (function):  Fitting function.
      xvals (float):       Array containing x values to fit.
      yvals (float):       Array containing y values to fit.
      coefs0 (float):      Array with initial guess for fitting coefficients.
      sigmas (float):      Array containing y sigmas/uncertainties.
      verbosity (int):     Verbosity to stdout (0-4).
    
    Returns:
      (tuple):  Tuple containing (coefs, var_cov, red_chi2, ier):
    
      - coefs (float):     Array containing final fitting coefficients.
      - var_cov (float):   2D array containing the variance-covariance matrix.
      - red_chi2 (float):  Reduced chi squared (chi2/(n-m)).
      - ier (int):         Return value, >0 if the fit succeeded.
    """
    
    import pandas.core as _pdc
    from scipy.optimize import curve_fit as _curve_fit
    
    try:
        # Do the fit:
        coefs, var_cov, infodict, mesg, ier = _curve_fit(fit_fun, xvals, yvals, p0=coefs0, sigma=sigmas,
                                                         method='lm', full_output=True)
    
    # If call failed:
    except Exception as e:
        if verbosity>0:
            print(__name__+': fit failed: ', end='')
            print(e)
        ier = -1
    
    
    # If call failed or fit did not converge:
    if ier<=0:
        if verbosity>0: print('Fit failed: %i' % ier)
        return None, None, None, ier
    
    
    # Print basic curve_fit output:
    if verbosity>2:
        print('Fit success: ', ier)
        print('Message: ', mesg)
        if verbosity>3:
            print('Info dict:\n', infodict, '\n')
        print('Initial coefficients:  ', coefs0)
    if verbosity>1:
        print('Final coefficients:    ', coefs)
    if verbosity>2:
        print('Variance/covariance matrix: \n', var_cov)
    
    
    # Compute some fit-quality parameters:
    dcoefs   = _np.sqrt(_np.diag(var_cov))              # Standard deviations on the coefficients
    yfit     = fit_fun(xvals, *coefs)                   # Fit values
    ydiffs   = yfit - yvals                             # Differences between data and fit
    resids   = ydiffs/sigmas                            # Weighted residuals
    
    chi2      = sum(resids**2)                          # Chi^2
    red_chi2  = chi2/(len(xvals)-len(coefs))            # Reduced Chi^2 = Chi^2 / (n-m)
    
    
    
    # Print some fit-quality parameters:
    if verbosity>1:
        orig_sig  = _np.sqrt(red_chi2)                      # When sigma_y=1 was used for the fit, this is an estimate of the true sigma_y
        y_max_dev  = max(abs(ydiffs))                       # Maximum deviation in y
        
        if type(xvals) == _pdc.series.Series:
            x_max_dev  = xvals[abs(ydiffs) == y_max_dev].values[0]  # x value for maximum deviation (Pandas)
        else:
            x_max_dev  = xvals[ydiffs == y_max_dev][0]              # x value for maximum deviation (Numpy)
        
        print('Chi2:      ', chi2)
        print('Red. chi2: ', red_chi2)
        print('Sigma:     ', orig_sig)
        print('Max.dev:   ', y_max_dev, ' @ x =', x_max_dev)
    
    if verbosity>2:
        print('Coefficients:')
        for icoef in range(len(coefs)):
            # print(' ', icoef+1,':', coefs[2-icoef], '±', dcoefs[2-icoef])  # Reverse order w.r.t. polyfit
            # print(' ', icoef+1,':', coefs[icoef], '±', dcoefs[icoef])
            print(' c%1i: %9.5f ± %9.5f (%9.2f%%)' % (icoef+1,coefs[icoef], dcoefs[icoef], abs(dcoefs[icoef]/coefs[icoef]*100) ) )  # Formatted
    
    return coefs, var_cov, red_chi2, ier
    
