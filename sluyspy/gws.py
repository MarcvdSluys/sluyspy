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


"""Gravitational-wave functions for the sluyspy package"""


import numpy as _np
import pandas as _pd
import astroconst as _ac


def cbc_waveform(m1,m2, dist,cosi, tlen,tcoal, Npts):
    """Compute a simple, Newtonian(!) compact-binary-coalescence waveform.
    
    Parameters:
      m1 (float):  Mass of binary component 1 (kg).
      m2 (float):  Mass of binary component 2 (kg).
      dist (float):  Distance of binary (m).
      cosi (float):    Cosine of the inclination angle: +/-1 = face on, 0 = edge-on.
      tlen (float):    Length of time of array (s).
      tcoal (float):   Coalescence time (s).
      Npts (float):    Number of data points (-).
    
    Returns:
      (pd.df):  Pandas dataframe containing variables.
    """
    
    mt = m1+m2
    mu = m1*m2/mt
    Mc = (m1*m2/mt**(1/3))**(3/5)
    
    fisco       = _ac.c**3 / (6**(3/2) * _ac.pi * _ac.g * mt)
    fisco_force = _ac.c**3 / (1**(3/2) * _ac.pi * _ac.g * mt)

    tstart = tcoal - tlen
    
    # Create DataFrame:
    df = _pd.DataFrame(data=_np.linspace(tstart, tcoal, Npts), columns=['time'])  # Initial column, 100 values, -10 - 0
    
    GMcc3 = _ac.g*Mc/_ac.c**3
    df['fgw']  = 1/_ac.pi * _np.power(5/256 * 1/(tcoal-df.time), 3/8) * GMcc3**(-5/8)
    df = df[df.fgw < fisco_force]  # Cut the REALLY wrong bits...
    
    df['dfdt'] = 96/5 * _ac.pi**(8/3) * GMcc3**(5/3) * _np.power(df.fgw, 11/3)
    df['worb'] = df.fgw/2 * _ac.pi2  # worb = forb * 2pi = f_gw/2 * 2pi
    df['aorb'] = _np.power((_ac.g*mt) / _np.square(df.worb), 1/3)  # aorb^3 = G Mt / w^2
    
    Rs = 2 * _ac.G * mt / _ac.c**2
    df['aorb_Risco'] = df.aorb / Rs / 6
    df['vorb1'] = df.worb * df.aorb * m2/mt / _ac.c
    df['vorb2'] = df.worb * df.aorb * m1/mt / _ac.c
    
    df['ampl'] = 4/dist * _ac.g/_ac.c**4 * mu * _np.square(df.aorb) * _np.square(df.worb)
    h_phase    = 2*df.worb*(df.time-tcoal)
    df['hpl']  = df.ampl * (1+cosi**2)/2 * _np.cos(h_phase)
    df['hcr']  = df.ampl * cosi          * _np.sin(h_phase)
    df['h']    = (df.hpl + df.hcr)/2 * 1e21
    
    # Frequency domain:
    df['htilde'] = _ac.pi**(-2/3) * _np.sqrt(5/24) * _ac.c / dist \
        * (_ac.G * Mc / _ac.c**3)**(5/6) * _np.power(df.fgw, -7/6)
    
    # df['Psi_pl'] = _ac.pi2 * df.fgw * 1  -  0  - _ac.pio4  \
    #     +  3/4 * _np.power(_ac.G * Mc/_ac.c**3 * 8*_ac.pi * df.fgw, -5/3)
    # df['Psi_cr'] = df.Psi_pl + _ac.pio2
    # df['htilde_pl'] = df.htilde * (1+cosi**2)/2 * _np.exp( df.Psi_pl * 1j )
    # df['htilde_cr'] = df.htilde * cosi          * _np.exp( df.Psi_cr * 1j )
    # df['htilde_tot'] = _np.abs(_np.real(df.htilde_pl + df.htilde_cr)/2)  # _np.cos(df.Psi_pl)
    
    print('Fisco, Fisco,force: ', fisco, fisco_force)
    
    return df


def noise_curve(Npts, f_low,f_high, Len, P_L,lam_L, eta_pd, M_mir, R_in,R_end, PRfac, no_FP=False,
                verbosity=0):
    
    """Compute a simplified noise curve for a gravitational-wave interferometer.
    
    Parameters:
      Npts (float):    Number of data points (-).
      f_low (float):   Lower frequency cut off (Hz).
      f_high (float):  Higher frequency cut off (Hz).
    
      Len (float):     Length of interferometer arms (m).
      P_L (float):     Laser power (W).
      lam_L (float):   Laser wavelength (m).
      eta_pd (float):  Efficiency of photodetector (fraction 0-1).
    
      M_mir (float):   Mass of the end mirror/test mass (kg).
      R_in (float):    Reflectivity of the input mirrors of the (main) Fabry-Perot cavity (fraction 0-1).
      R_end (float):   Reflectivity of the end mirrors of the interferometer (fraction 0-1).
    
      PRfac (float):   Factor for power recycling (factor 1-...).
      no_FP (bool):    Do NOT use a Fabry-Perot cavity (optional; defaults to False, i.e. DO use a FPC).
    
    Returns:
      (pd.df):  Pandas.DataFrame containing noise strains.
    """
    
    # Create DataFrame:
    df = _pd.DataFrame(data=_np.logspace(_np.log10(f_low), _np.log10(f_high), Npts), columns=['freq'])  # Initial column, Npts rows
    
    if no_FP:
        Fin = 1
        Leff_L = 1
        f_pole = 0
        f_pole_fac = 1
    else:
        Fin = _ac.pi * _np.sqrt(R_in*R_end) / (1 - R_in*R_end)   # Finesse
        Leff_L = 2*Fin/_ac.pi
        f_pole = _ac.c / (4 * Fin * Len)                        # Pole frequency
        f_pole_fac = _np.sqrt( 1 + _np.square(df.freq/f_pole) )
    
    if verbosity > 1:
        print()
        print('Finesse:   ', Fin)
        print('Leff/L:    ', Leff_L)
        print('f_pole:    ', f_pole)
        print()
    
    df['shot'] = \
        1/(8*Fin*Len) * _np.sqrt( (4*_ac.pi*_ac.h_bar*_ac.c * lam_L) / (eta_pd * PRfac * P_L) ) * f_pole_fac
    
    df['rad'] = 16*_np.sqrt(2) * Fin / (M_mir * Len * _np.square(_ac.pi2*df.freq)) \
        * _np.sqrt((_ac.h_bar * P_L * PRfac)/(_ac.pi2 * lam_L * _ac.c)) / f_pole_fac
    
    df['tot'] = df.shot + df.rad
    
    return df

    
