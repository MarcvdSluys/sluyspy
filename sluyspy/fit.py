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


"""Fitting functions for the sluyspy package"""


import numpy as _np
import pandas.core as _pdc
import sluyspy.cli as _scli


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
    red_chi2 = print_fit_details(xvals,yvals, ysigmas=ysigmas, fittype='np_polyfit', coefs=coefs,
                                 verbosity=verbosity)
    
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
      (tuple):  Tuple containing (coefs, dcoefs, red_chi2, var_cov, ier):
    
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
        return None, None, None, None, ier
    
    
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
    red_chi2 = print_fit_details(xvals,yvals,ysigmas, fittype='scipy_curvefit', coefs=coefs, dcoefs=dcoefs,
                                 var_cov=var_cov, fit_fun=fit_fun, verbosity=verbosity)
    
    return coefs, dcoefs, red_chi2, var_cov, ier


def print_fit_details(xvals,yvals, ysigmas=None, fittype=None, coefs=None,dcoefs=None, var_cov=None,
                      fit_fun=None, yfit=None, verbosity=2, abs_diff=True,rel_diff=True, sigdig=6,
                      coef_names=None, coef_facs=None, rev_coefs=None, yprintfac=1, rel_as_pct=False):
    
    """Compute and return the reduced chi^2, and print other fit details if desired.
    
    Calculations are done without fitting, so that this function can be called after a fit.  The fit values
    will be computed from coefs, xvals using fit_fun if specified.  In fact, two series of yvals ('true' and
    'fit') can be specified without any fitting ever, by setting fittype=coefs=xvals=None and specifying yfit.
    This will print statistics on the comparison of the two data sets, similar to those after a fit.  If xvals
    is specified, a bit more detail can be printed.
    
    Parameters:
      xvals (float):      Array with x values.
      yvals (float):      Array with y values.
    
      ysigmas (float):    Array with y sigmas; optional, defaults to None (i.e. using 1 for all ysigmas).
    
      fittype (str):      Type of fit: 'np_polyfit', 'scipy_curvefit'; optional, defaults to None.
      coefs (float):      Array with fit coefficients; optional, defaults to None.
    
      dcoefs (float):     Uncertainties in coefficients from scipy_curvefit; optional, defaults to None.
      var_cov (float):    Variance-covariance matrix in 2D NumPy array; optional, defaults to None.
      fit_fun (fun):      Fit function used for scipy_curvefit; optional, defaults to None.
      yfit (float):       "Fit" values for Y for fittype=None; optional, defaults to None.
    
      verbosity (int):    Verbosity (0-3); optional - defaults to 2.
      abs_diff (bool):    Print absolute differences (optional; defaults to True).
      rel_diff (bool):    Print relative differences (optional; defaults to True).
      sigdig (int):       Number of significant digits to print (optional, defaults to 6).
    
      coef_names (str):   Array of coefficient names for printing (optional, defaults to None).
      coef_facs (float):  Array of coefficient multiplication factors for printing (optional; defaults to None,
                          in which case 1 is used).  Useful for e.g. printing degrees when radians are fitted.
      rev_coefs (bool):   Reverse printing order in coefficient table: last coefficient at top.
                          Optional, defaults to None, resulting in True for fittype np_polyfit, False otherwise.
    
      yprintfac (float):  Multiplication factor when printing absolute differences in y (optional, defaults to 1).
      rel_as_pct (bool):  Print relative difference as percentage rather than fraction (optional, defaults to False).
    
    Returns:
      (float):            Reduced Chi^2.
    
    Note:
      - If fittype = 'scipy_curvefit', fit_fun must be specified.
      - If fittype is None, yfit values must be specified, since they will not be computed from xvals
        and coefs.  In that case, coefs=xvals=None can be specified.
    """
    
    from sluyspy.numerics import sigdig as sd
    
    if fittype=='np_polyfit':
        yfit      = _np.poly1d(coefs)(xvals)
        if rev_coefs is None: rev_coefs = True
    elif fittype=='scipy_curvefit':
        if fit_fun is None: _scli.error('A fit function must be specified for fittype '+str(fittype))
        if coefs is None: _scli.error('Fit coefficients must be specified for fittype '+str(fittype))
        yfit      = fit_fun(xvals, *coefs)
        if rev_coefs is None: rev_coefs = False
    elif fittype is None:
        if yfit is None: _scli.error('yfit values must be specified for fittype '+str(fittype))
        if rev_coefs is None: rev_coefs = False
    else:
        _scli.error('Unknown fittype: '+fittype+'; must be one of "np_polyfit", "scipy_curvefit" or None.')
    
    yfit = yvals*0 + yfit  # Ensure yfit has same type as xvals (np.array/pd.Series)
    
    if ysigmas is None:
        if verbosity>1: print('\nysigmas=None; assuming sigma=1 for all data points.\n')
        ysigmas = yvals*0 + 1  # Set ysigmas to 1 - works for pd.Series and np.arrays
    else:
        # Discard data points with sigma == 0:
        ndat = len(ysigmas)                        # Number of data points
        if xvals is not None:  xvals = xvals[ysigmas>0]
        if yfit is not None:   yfit  = yfit[ysigmas>0]
        yvals   = yvals[ysigmas>0]
        ysigmas = ysigmas[ysigmas>0]
        if (verbosity>1) and (len(ysigmas) != ndat): print('\nDiscarding data points with ysigma=0.\n')
    
    if verbosity>1: mean_ysigma = _np.nanmean(ysigmas) * yprintfac  # Mean sigma in y
    
    
    rel_fac = 1  # Print fraction
    rel_str = ' '
    if rel_as_pct:
        rel_fac = 100  # Print percentage
        rel_str = '%'
        
    
    # Compute reduced chi^2:
    if coefs is None:
        ncoefs = 0                                          # Number of coefficients
    else:
        ncoefs = len(coefs)                                 # Number of coefficients
    
    ndat                = len(yvals)                        # Number of data points
    ydiffs              = yfit - yvals                      # Differences/residuals
    yresids             = ydiffs/ysigmas                    # Weighted residuals
    chi2                = _np.sum(yresids**2)               # Chi^2 - NumPy needed for large numbers
    red_chi2            = chi2/(ndat-ncoefs)                # Reduced chi^2
    
    abs_ydiffs          = ydiffs                            # Absolute differences in y
    mean_abs_ydiff      = _np.nanmean(abs_ydiffs)           # The mean absolute difference between data and fit values
    med_abs_ydiff       = _np.nanmedian(abs_ydiffs)         # The median absolute difference between data and fit values
    
    abs_abs_ydiffs      = _np.abs(ydiffs)                   # Absolute values of absolute differences in y
    mean_abs_abs_ydiff  = _np.nanmean(abs_abs_ydiffs)       # The mean absolute difference between data and fit values
    med_abs_abs_ydiff   = _np.nanmedian(abs_abs_ydiffs)     # The median absolute difference between data and fit values
    
    rel_ydiffs          = ydiffs[yvals!=0]/yvals[yvals!=0]  # Relative differences in y
    rel_ydiffs         *= rel_fac                           # Fraction or percentage?
    mean_rel_ydiff      = _np.nanmean(rel_ydiffs)           # The mean absolute difference between data and fit values
    med_rel_ydiff       = _np.nanmedian(rel_ydiffs)         # The median absolute difference between data and fit values
    
    abs_rel_ydiffs      = _np.abs(rel_ydiffs)               # Absolute values of relative differences in y
    mean_abs_rel_ydiff  = _np.nanmean(abs_rel_ydiffs)       # The mean absolute difference between data and fit values
    med_abs_rel_ydiff   = _np.nanmedian(abs_rel_ydiffs)     # The median absolute difference between data and fit values
    
    
    # Compute and print details:
    if verbosity>0:
        
        # Find maximum differences:
        if verbosity>2:
            max_abs_diff_y  = _np.max(abs_abs_ydiffs)  # Maximum absolute difference in y
            max_rel_diff_y  = _np.max(abs_rel_ydiffs)  # Maximum relative difference in y
            
            if type(xvals) is _pdc.series.Series:
                max_abs_diff_x  = xvals[abs_abs_ydiffs == max_abs_diff_y].to_numpy()[0]  # x value for maximum absolute difference (Pandas)
                max_rel_diff_x  = xvals[ _np.logical_and(yvals!=0, abs_rel_ydiffs == max_rel_diff_y)].to_numpy()[0]  # x value for maximum relative difference (Pandas)
            elif xvals is None:
                max_abs_diff_x  = None
                max_rel_diff_x  = None
                xvals = yvals*0 + _np.nan  # Fill with NaNs
            else:
                max_abs_diff_x  = xvals[abs_abs_ydiffs == max_abs_diff_y][0]             # x value for maximum absolute difference (Numpy)
                max_rel_diff_x  = xvals[ _np.logical_and(yvals!=0, abs_rel_ydiffs == max_rel_diff_y)][0]  # x value for maximum relative difference (Numpy)
        
        # Print details:
        if verbosity>1:
            print('Fit type:      ', fittype)
            if fit_fun is not None:  print('Fit function:  ', fit_fun.__name__)
            print()
            
            print('Fit quality:')
            print('Number of data points:            ', ndat)
            if verbosity>2:
                if ncoefs>0:
                    print('Number of coefficients:           ', ncoefs)
                    print('Degrees of freedom:               ', ndat - ncoefs)
                    print()
                print('Chi2:                             ', sd(chi2, sigdig))
            
        print('Reduced chi2:                     ', sd(red_chi2, sigdig))
        if verbosity>1:
            print('sqrt reduced chi2:                ', sd(_np.sqrt(red_chi2), sigdig))
            if mean_ysigma != 1: print('sqrt red.chi2 * mean sigma:       ', sd(_np.sqrt(red_chi2)*mean_ysigma, sigdig))
        
        if abs_diff:
            if verbosity>1: print()
            print('Mean/med. |absolute difference|:  ', sd(mean_abs_abs_ydiff*yprintfac, sigdig), '  /  ',
                  sd(med_abs_abs_ydiff*yprintfac, sigdig))
            
            if verbosity>2:
                print('Max. |absolute difference|:       ', sd(max_abs_diff_y*yprintfac, sigdig),
                      '  @   x =', sd(max_abs_diff_x, sigdig))
                
                print('Mean/med. absolute difference:    ', sd(mean_abs_ydiff*yprintfac, sigdig), '  /  ',
                      sd(med_abs_ydiff*yprintfac, sigdig))
            
        if rel_diff:
            if verbosity>2: print()
            print('Mean/med. |relative difference|:  ', sd(mean_abs_rel_ydiff, sigdig), rel_str, '  /  ',
                  sd(med_abs_rel_ydiff, sigdig), rel_str)
            
            if verbosity>2:
                print('Max. |relative difference|:       ', sd(max_rel_diff_y, sigdig), rel_str,
                      '  @   x =', sd(max_rel_diff_x, sigdig))
                
                print('Mean/med. relative difference:    ', sd(mean_rel_ydiff, sigdig), rel_str, '  /  ',
                      sd(med_rel_ydiff, sigdig), rel_str)
            
        
        # Print fit coefficients:
        if (verbosity>1) and (coefs is not None):
            if coef_facs is None:  coef_facs = _np.array(coefs)*0+1  # Coefficient print factor is 1 by default:
            
            # Give all coefficient names the same length:
            if coef_names is not None:
                strlen = len(max(coef_names, key=len))  # Length of the longest string in the list
                fmt = ' %'+str(strlen)+'s'
                for icoef in range(ncoefs):
                    coef_names[icoef] = fmt % (coef_names[icoef])
            
            print('\nFit coefficients', end='')
            if rev_coefs: print(' (reversed)', end='')
            print(':')
            for icoef in range(ncoefs):
                jcoef = icoef
                if rev_coefs: jcoef = ncoefs-icoef-1
                
                print(' c%1i:' % (icoef), end='')  # Nr
                
                if coef_names is not None:
                    print(coef_names[jcoef]+': ', end='')  # Name
                
                print(' %12.5e' % (coefs[jcoef] * coef_facs[jcoef]), end='')  # Value
                
                if dcoefs is not None:
                    print(' ± %12.5e (%9.2f%%)' % (dcoefs[jcoef] * coef_facs[jcoef],
                                                   _np.abs(dcoefs[jcoef]/coefs[jcoef]*100) ), end='')
                
                print()
        
        # Print correlation and variance-covariance matrices:
        if (verbosity>2) and (var_cov is not None):
            print('\nCorrelation matrix:')
            corr = correlation_matrix_from_variance_covariance_matrix(var_cov)
            _print_matrix(corr, 'corr', coef_names)
            
            if verbosity>3:
                print('\nVariance-covariance matrix:')
                _print_matrix(var_cov, 'var_cov', coef_names)
        
        # Print all fit data points:
        if verbosity>4:
            print('\nFit data:')
            print('%9s  %12s  %12s  %12s  %12s  %12s  %12s  %12s' %
                  ('i', 'x_val', 'y_val', 'y_sigma', 'y_fit', 'y_diff_abs', 'y_diff_wgt', '|y_dif_rel|') )
            
            if type(yvals) is _pdc.series.Series:
                for ival in range(ndat):
                    print('%9i  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e' %
                          (ival, xvals.iloc[ival],yvals.iloc[ival]*yprintfac, ysigmas.iloc[ival]*yprintfac,
                           yfit.iloc[ival]*yprintfac, ydiffs.iloc[ival]*yprintfac,
                           yresids.iloc[ival]*yprintfac, _np.abs(ydiffs.iloc[ival]/yvals.iloc[ival])*rel_fac ) )
            
            else:  # Probably Numpy:
                for ival in range(ndat):
                    print('%9i  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e  %12.5e' %
                          (ival, xvals[ival],yvals[ival]*yprintfac, ysigmas[ival]*yprintfac,
                           yfit[ival]*yprintfac, ydiffs[ival]*yprintfac, yresids[ival]*yprintfac,
                           _np.abs(ydiffs[ival]/yvals[ival])*rel_fac ) )
            
            print('%9s  %12s  %12s  %12s  %12s  %12s  %12s  %12s' %
                  ('i', 'x_val', 'y_val', 'y_sigma', 'y_fit', 'y_diff_abs', 'y_diff_wgt', '|y_dif_rel|') )
            
    if verbosity>1: print()
    
    return red_chi2


def correlation_matrix_from_variance_covariance_matrix(var_cov):
    """Compute the normalised correlation matrix from a variance-covariance matrix.
    
    Parameters:
      var_cov (float):  2D NumPy array containing the variance-covariance matrix.
    
    Returns:
      (float): 2D NumPy array containing the normalised-correlation matrix.
    """
    
    corr    = _np.zeros_like(var_cov)
    matsize = _np.shape(corr)[0]
    
    for i in range(matsize):
        for j in range(matsize):
            corr[i][j] = var_cov[i,j] / _np.sqrt(var_cov[i,i] * var_cov[j,j])
    
    return corr


def polynomial(x, *coefs):
    """Return a polynomial y = Sum_i=0^N-1 coef_i x^i.
    
    Parameters:
      x (float):      X value(s).
      coefs (float):  Array of polynomial coefficients.
                      The polynomial order is defined by the number of coefficients in the array.
    
    Returns:
      (float):  Polynomial value.
    """
    
    y = 0
    i = 0
    for coef in coefs:
        y += coef * _np.power(x, i)
        i += 1
    
    return y


def _print_matrix(mat, mat_type, coef_names=None):
    """Print the contents of a 2D (correlation or covariance) matrix.
    
    Parameters:
      mat (float):  2D NumPy array containing the variance-covariance matrix.
    """
    
    # Matrix size:
    matsize = _np.shape(mat)[0]
    
    # Derive fomatting for names and numbers from matrix type:
    if mat_type == 'corr':
        namfmt = ' %7s'
        maxnamlen = 7
        numfmt = '%8.4f'   # ' -0.1238'
    else:
        namfmt = ' %12s'
        maxnamlen = 12
        numfmt = '%13.5e'  # ' -1.12345e-13'
        
    # Length of coefficient names:
    if coef_names is None:
        namlen = 0
    else:
        namlen = len(coef_names[0])
    
    # Print row of coefficient numbers:
    print(' '*(3+namlen), end='')  # Spaces: c_i + name length
    for i in range(matsize):
        print(namfmt % ('c'+str(i)), end='')
    print()
        
    # Print row of coefficient names:
    if coef_names is not None:
        print(' '*(3+namlen), end='')  # Spaces: c_i + name length
        for i in range(matsize):
            print(namfmt % (coef_names[i].strip()[:maxnamlen]), end='')  # Cut off name to preserve table formatting
        print()
    
    # Print columns with coefficient numbers, coefficient names and values:
    for i in range(matsize):
        if matsize > 10:
            print('c%2i' % (i), end='')
        else:
            print('c%1i ' % (i), end='')
            
        if coef_names is not None:  print(coef_names[i], end='')
        for j in range(matsize):
            print(numfmt % (mat[i,j]), end='')
        print()
        
    return

