#!/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

""" fit-example.py:  Show how to use sluyspy.fit to fit a function to data.
    2025-10-14, MvdS: initial version.
"""


import colored_traceback
colored_traceback.add_hook()

import numpy as np
import pandas as pd
import astroconst as ac
from sluyspy import plot as splt
import sluyspy.fit as sfit


def main():
    """Main function."""
    
    # Create data = signal + noise:
    Npt = 100
    coefs_true = [1,2,3,4]  # Offset, amplitude, period, phase
    sigma = 0.5 * coefs_true[1]  # Relative sigma in amplitude
    
    df = pd.DataFrame()
    df['time'] = np.linspace(0., 2 * coefs_true[2] * ac.pi2, Npt)  # Period*2pi*2 -> 2 periods
    df['signal'] = fitfun(df.time, *coefs_true)
    
    np.random.seed(1)
    df['data'] = df.signal + np.random.normal(0, sigma, Npt)
    # print(df)
    
    # Fit the data:
    print('\nVerbose (4/5) output from sluyspy.fit.scipy_curvefit_chi2():')
    coefs_start = coefs_true * np.random.normal(1, 0.1, len(coefs_true))  # Offset start parameters
    coefs, dcoefs, red_chi2, var_cov, ier = sfit.scipy_curvefit_chi2(fitfun, df.time,df.data, coefs_start,
                                                                     verbosity=4)
    print('\nResults returned to caller function:\n')
    print('coefs:     ', coefs)
    print('dcoefs:    ', dcoefs)
    print('red_chi2:  ', red_chi2)
    print('var_cov:   ', var_cov)
    print('ier:       ', ier)
        
    df['fit'] = fitfun(df.time, *coefs)  # Compute fit function
    
    # Make a plot:
    make_plot(df)
    
    print()
    exit(0)
    return


def fitfun(x, *coefs):
    y = coefs[0] + coefs[1] * np.sin(coefs[2]/ac.pi2 * x + coefs[3])
    return y
    

def make_plot(df):
    """Make a plot.
    
    Parameters:
      df (pd.df):     Pandas DataFrame containing plot data.
    """

    print('\nCreating plot...')
    
    fig, ax = splt.start_plot('both', dark_bg=False, title='Sluyspy fit example plot')
    
    ax.plot(df.time, df.signal, '-',  label='signal')
    ax.plot(df.time, df.data,   'o',  label='data')
    ax.plot(df.time, df.fit,    '--', label='fit')
    
    splt.finish_plot(fig,ax, 'fit-example.png', xlbl='Time',ylbl='Data', legend=True,grid=True)
    return


if __name__ == '__main__':
    main()

