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
import pandas.core as _pdc
import sluyspy.cli as scli


def np_polyfit_chi2(xvals, yvals, order, ysigmas=None, verbosity=0):
    """Wrapper for NumPy polyfit, that returns the fitting coefficients and reduced chi squared.
       Print details if desired.
    
    Note: does not compute the uncertainties in the coefficients; use scipy_curvefit_chi2() for that.
    
    Parameters:
      xvals (float):    X values.
      yvals (float):    Y values.
      order (int):      Polynomial order for fit.
      ysigmas (float):  Uncertainties (errors, standard deviations) in the y values; defaults to None -> all sigmas=1.
      verbosity (int):  Verbosity:  0: quiet,  1: print red.chi2,  2: print more,  3: print table,  4: print all;  defaults to 0.
    
    Returns:
      (tuple):  Tuple consisting of (coefs, red_chi2):
    
      - coefs (float):     Array of fitting coefficients, with length (order+1).
      - red_chi2 (float):  Reduced chi squared (chi^2 / (n-m)) for the fit.
    """
    
    if ysigmas is None:
        if verbosity>0: print('ysigmas=None; assuming sigma=1 for all data points.')
        coefs, resids, rank, sing_vals, rcond = _np.polyfit(xvals, yvals, order, full=True)
        ysigmas = yvals*0 + 1  # This is implicitly assumed in the previous line; works for pd.Series and numpy arrays
    else:
        coefs, resids, rank, sing_vals, rcond = _np.polyfit(xvals, yvals, order, w=1/ysigmas, full=True)  # Note, not 1/sigma**2!
    
    
    # Print polyfit-specific details:
    if verbosity>3:
        print('coefs:      ', coefs)
        print('resids:     ', resids)
        print('rank:       ', rank)
        print('sing_vals:  ', sing_vals)
        print('rcond:      ', rcond)
    
    # Compute reduced chi^2 and print general fit details:
    red_chi2 = print_fit_details('np_polyfit', coefs, xvals,yvals,ysigmas, verbosity=verbosity)
    
    return coefs, red_chi2



def scipy_curvefit_chi2(fit_fun, xvals, yvals, coefs0, ysigmas=None, verbosity=0):
    """Wrapper for SciPy's curve_fit, that returns the fitting coefficients and reduced chi^2.
       Print details if desired.
    
    Parameters:
      fit_fun (function):  Fitting function, should look like  def fit_fun(x, a,b,c):  and return y=f(x, a,b,c).
      xvals (float):       Array containing x values to fit.
      yvals (float):       Array containing y values to fit.
      coefs0 (float):      Array with initial guess for fitting coefficients.
      ysigmas (float):     Array containing y sigmas/uncertainties.
      verbosity (int):     Verbosity to stdout (0-4).
    
    Returns:
      (tuple):  Tuple containing (coefs, var_cov, red_chi2, ier):
    
      - coefs (float):     Array containing the final fitting coefficients.
      - dcoefs (float):    Array containing uncertainties on the fitting coefficients.
      - red_chi2 (float):  Reduced chi squared (chi2/(n-m)).
      - var_cov (float):   2D array containing the variance-covariance matrix.
      - ier (int):         Return value, >0 if the fit succeeded.
    """
    
    from scipy.optimize import curve_fit as _curve_fit
    
    try:
        # Do the fit:
        coefs, var_cov, infodict, mesg, ier = _curve_fit(fit_fun, xvals, yvals, p0=coefs0, sigma=ysigmas,
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
    
    
    # Print specific curve_fit output:
    if verbosity>3:
        print('Fit success: ', ier)
        print('Message: ', mesg)
        if verbosity>4:
            print('Info dict:\n', infodict, '\n')
        print('Initial coefficients:  ', coefs0)
        print('Final coefficients:    ', coefs)
        print('Variance/covariance matrix: \n', var_cov)
    
    
    # Compute some fit-quality parameters:
    if ysigmas is None: ysigmas = yvals*0 + 1  # This is implicitly assumed in the previous line; works for pd.Series and numpy arrays
    
    dcoefs = _np.sqrt(_np.diag(var_cov))              # Standard deviations on the coefficients
    
    # Compute reduced chi^2 and print general fit details:
    red_chi2 = print_fit_details('scipy_curvefit', coefs, xvals,yvals,ysigmas, verbosity=verbosity,
                                 fit_fun=fit_fun, dcoefs=dcoefs)
    
    return coefs, dcoefs, red_chi2, var_cov, ier


def print_fit_details(fittype, coefs,xvals,yvals,ysigmas, verbosity=2, fit_fun=None, dcoefs=None, yfit=None,
                      coef_names=None, coef_facs=None, rev_coefs=None):
    """Compute and return the reduced chi^2, and print fit details if desired.
    
    Calculations are done without fitting, so that this function can be called after a fit.  The fit values
    will be computed from coefs, xvals using fit_fun if specified.  In fact, two series of yvals ('true' and
    'fit') can be specified without any fitting ever, by setting fittype=coefs=xvals=None and specifying yfit.
    This will print statistics on the comparison of the two data sets, similar to those after a fit.  If xvals
    is specified, a bit more detail can be printed.
    
    Parameters:
      fittype (str):         Type of fit: 'np_polyfit', 'scipy_curvefit' or None.
      coefs (float):         Array with fit coefficients.
      xvals (float):         Array with x values.
      yvals (float):         Array with y values.
      ysigmas (float):       Array with y sigmas.
    
      verbosity (int):       Verbosity (0-3); optional - defaults to 2.
      fit_fun (fun):         Fit function used for scipy_curvefit; optional.
      dcoefs (float):        Uncertainties in coefficients from scipy_curvefit; optional.
      yfit (float):          "Fit" values for Y for fittype=None; optional.
    
      coef_names (str):      Array of coefficient names for printing (optional).
      coef_facs (float):     Array of coefficient multiplication factors for printing (optional; defaults to 1).
                             Useful for e.g. printing degrees when radians are fitted.
      rev_coefs (bool):      Reverse printing order in coefficient table: last coefficient at top.
                             Optional, defaults to True for fittype np_polyfit, to False otherwise.
    
    Returns:
      (float):               Reduced Chi^2.
    
    Note:
      - If fittype = 'scipy_curvefit', fit_fun must be specified.
      - If fittype is None, yfit values must be specified, since they will not be computed from xvals
        and coefs.  In that case, coefs=xvals=None can be specified.
    """
    
    if fittype=='np_polyfit':
        yfit      = _np.poly1d(coefs)(xvals)
        if rev_coefs is None: rev_coefs = True
    elif fittype=='scipy_curvefit':
        if fit_fun is None: scli.error('A fit function must be specified for fittype '+fittype)
        yfit      = fit_fun(xvals, *coefs)
        if rev_coefs is None: rev_coefs = False
    elif fittype is None:
        if yfit is None: scli.error('yfit values must be specified for fittype '+fittype)
        if rev_coefs is None: rev_coefs = False
    else:
        scli.error('Unknown fittype: '+fittype+'; must be one of "np_polyfit", "scipy_curvefit" or None.')
    
    yfit = yvals*0 + yfit  # Ensure yfit has same type as xvals (np.array/pd.Series)
    
    if ysigmas is None:
        if verbosity>0: print('\nysigmas=None; assuming sigma=1 for all data points.')
        if verbosity>1: print('')
        ysigmas = yvals*0 + 1  # Set ysigmas to 1 - works for pd.Series and np.arrays
    
    ysigma_mean = ysigmas.mean()
    
    # Compute reduced chi^2:
    if coefs is None:
        ncoefs = 0                                      # Number of coefficients
    else:
        ncoefs = len(coefs)                             # Number of coefficients
    
    ndat      = len(yvals)                              # Number of data points
    ydiffs    = yfit - yvals                            # Differences/residuals
    yresids   = ydiffs/ysigmas                          # Weighted residuals
    chi2      = _np.sum(yresids**2)                     # Chi^2 - NumPy needed for large numbers
    red_chi2  = chi2/(ndat-ncoefs)                      # Reduced chi^2
    
    
    # Compute and print details:
    if verbosity>0:
        
        # Find maximum deviations:
        max_abs_dev_y  = _np.max(_np.abs(ydiffs))                     # Maximum absolute deviation in y
        rel_dev_ys     = _np.abs(ydiffs[yvals!=0]/yvals[yvals!=0])    # Relative deviations in y
        max_rel_dev_y  = _np.max(rel_dev_ys)                          # Maximum relative deviation in y
        
        if type(xvals) == _pdc.series.Series:
            max_abs_dev_x  = xvals[_np.abs(ydiffs) == max_abs_dev_y].to_numpy()[0]  # x value for maximum absolute deviation (Pandas)
            max_rel_dev_x  = xvals[ _np.logical_and(yvals!=0, rel_dev_ys == max_rel_dev_y)].to_numpy()[0]  # x value for maximum relative deviation (Pandas)
        elif xvals is None:
            max_abs_dev_x  = None
            max_rel_dev_x  = None
            xvals = yvals*0 + _np.nan  # Fill with NaNs
        else:
            max_abs_dev_x  = xvals[_np.abs(ydiffs) == max_abs_dev_y][0]             # x value for maximum absolute deviation (Numpy)
            max_rel_dev_x  = xvals[ _np.logical_and(yvals!=0, rel_dev_ys == max_rel_dev_y)][0]  # x value for maximum relative deviation (Numpy)
        
        # Print details:
        if verbosity>1:
            print('Fit quality:')
            print('Number of data points:    ', ndat)
            print('Chi2:                     ', chi2)
            
        print('Reduced chi2:             ', red_chi2)
        print('Typical original sigma:   ', _np.sqrt(red_chi2) * ysigma_mean)   # Estimate of the true sigma_y
        print('Max. absolute deviation:  ', max_abs_dev_y, ' @ x =', max_abs_dev_x)
        print('Max. relative deviation:  ', max_rel_dev_y, ' @ x =', max_rel_dev_x)
        
        
        # Print fit coefficents:
        if (verbosity>1) and (coefs is not None):
            if coef_facs is None:  coef_facs = coefs*0+1  # Coefficient print factor is 1 by default:
            
            print('\nFit coefficients', end='')
            if rev_coefs: print(' (reversed)', end='')
            print(':')
            for icoef in range(ncoefs):
                jcoef = icoef
                if rev_coefs: jcoef = ncoefs-icoef-1
                
                print(' c%1i:' % (icoef), end='')  # Nr
                
                if coef_names is not None:
                    strlen = len(_np.max(coef_names, key=len))  # Length of the longest string in the list
                    fmt = ' %'+str(strlen)+'s: '
                    print(fmt % (coef_names[jcoef]), end='')  # Name
                
                print(' %12.5e' % (coefs[jcoef] * coef_facs[jcoef]), end='')  # Value
                
                if dcoefs is not None:
                    print(' ± %12.5e (%9.2f%%)' % (dcoefs[jcoef] * coef_facs[jcoef],
                                                   _np.abs(dcoefs[jcoef]/coefs[jcoef]*100) ), end='')
                
                print('')
        
        
        # Print fit data:
        if verbosity>2:
            print('\nFit data:')
            print('%9s  %12s  %12s  %12s  %12s  %12s  %12s  %12s' %
                  ('i', 'x_val', 'y_val', 'y_sigma', 'y_fit', 'y_diff_abs', 'y_diff_wgt', 'y_diff_rel') )
            
            if type(yvals) == _pdc.series.Series:
                for ival in range(ndat):
                    print('%9i  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e' %
                          (ival, xvals.iloc[ival],yvals.iloc[ival], ysigmas.iloc[ival], yfit.iloc[ival],
                           ydiffs.iloc[ival], yresids.iloc[ival], _np.abs(ydiffs.iloc[ival]/yvals.iloc[ival]) ) )
                
            else:  # Probably Numpy:
                for ival in range(ndat):
                    print('%9i  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e' %
                          (ival, xvals[ival],yvals[ival], ysigmas[ival], yfit[ival], ydiffs[ival],
                           yresids[ival], _np.abs(ydiffs[ival]/yvals[ival]) ) )
                
            print('%9s  %12s  %12s  %12s  %12s  %12s  %12s  %12s' %
                  ('i', 'x_val', 'y_val', 'y_sigma', 'y_fit', 'y_diff_abs', 'y_diff_wgt', 'y_diff_rel') )
            
    
    return red_chi2
