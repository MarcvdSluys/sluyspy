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


def cbc_waveform(m1,m2, dist,cosi, tlen,tcoal, Npts, risco_fac=1.5, Fplcr=2/5, verbosity=0):
    """Compute a simple, Newtonian(!) compact-binary-coalescence waveform.
    
    Parameters:
      m1 (float):         Mass of binary component 1 (kg).
      m2 (float):         Mass of binary component 2 (kg).
      dist (float):       Distance of binary (m).
      cosi (float):       Cosine of the inclination angle: +/-1 = face on, 0 = edge-on.
      tlen (float):       Length of time of array (s).
      tcoal (float):      Coalescence time (s).
      risco_fac (float):  R_isco = R_star * risco_fac (-, defaults to 1.5); used to compute f_max.
      Npts (float):       Number of data points (-).
    
      Fplcr (float):      The mean value of F_+ and F_x: <F> ~ sqrt(<F_+^2 + F_x^2>),
                          which includes the inclination.  Defaults to 2/5.
      verbosity (int):    Verbosity level, defaults to 0: no output.
    
    Returns:
      (pd.df):  Pandas dataframe containing variables.
    """
    
    mt = m1+m2
    mu = m1*m2/mt
    Mc = (m1*m2/mt**(1/3))**(3/5)
    
    R1 = radius_BH_NS_from_mass(m1)  # Get the BH/NS radius for this mass (m)
    R2 = radius_BH_NS_from_mass(m2)
    a_min = R1 + R2                  # (m)
    
    f_isco = _ac.c**3 / (6**(3/2) * _ac.pi * _ac.g * mt)
    # f_max  = f_isco
    # f_max  = _ac.c**3 / (1**(3/2) * _ac.pi * _ac.g * mt)
    f_max = 1/_ac.pi * _np.sqrt(_ac.G * mt / (risco_fac*a_min)**3)  # f_max based on 1.5 x (sum of radii) and Kepler - same as above, but allows NSs
    
    tstart = tcoal - tlen
    
    # Create DataFrame:
    df = _pd.DataFrame(data=_np.linspace(tstart, tcoal, Npts), columns=['time'])  # Initial column, 100 values, -10 - 0
    
    GMcc3 = _ac.g*Mc/_ac.c**3
    df['fgw']  = 1/_ac.pi * _np.power(5/256 * 1/(tcoal-df.time), 3/8) * GMcc3**(-5/8)
    df = df[df.fgw < f_max]  # Cut the REALLY wrong bits...
    
    df['dfdt'] = 96/5 * _ac.pi**(8/3) * GMcc3**(5/3) * _np.power(df.fgw, 11/3)
    df['worb'] = df.fgw/2 * _ac.pi2  # worb = forb * 2pi = f_gw/2 * 2pi
    df['aorb'] = _np.power((_ac.g*mt) / _np.square(df.worb), 1/3)  # aorb^3 = G Mt / w^2
    
    df['vorb1'] = df.worb * df.aorb * m2/mt / _ac.c
    df['vorb2'] = df.worb * df.aorb * m1/mt / _ac.c
    
    df['ampl'] = 4/dist * _ac.g/_ac.c**4 * mu * _np.square(df.aorb) * _np.square(df.worb)
    h_phase    = 2*df.worb*(df.time-tcoal)
    df['hpl']  = df.ampl * (1+cosi**2)/2 * _np.cos(h_phase)
    df['hcr']  = df.ampl * cosi          * _np.sin(h_phase)
    df['h']    = Fplcr * (df.hpl + df.hcr)
    
    if verbosity>0:
        print('f_low, f_high (Hz):          ', df.fgw.iloc[0], df.fgw.iloc[-1])
        print('a_min (km):                  ', a_min/1000)
        print('f_isco, f_max (Hz):          ', f_isco, f_max)
        
        if verbosity>8: print(df)
    
    
    return df


def cbc_waveform_frequency(m1,m2, dist,cosi, f_low,f_high, Npts, risco_fac=1.5, Fplcr=2/5, verbosity=0):
    """Compute a simple, Newtonian(!) compact-binary-coalescence waveform in the frequency domain for a given
    range of frequencies.
    
    Parameters:
      m1 (float):         Mass of binary component 1 (kg).
      m2 (float):         Mass of binary component 2 (kg).
      dist (float):       Distance of binary (m).
      cosi (float):       Cosine of the inclination angle: +/-1 = face on, 0 = edge-on.
      f_low (float):      Lower cut-off frequency (Hz).
      f_high (float):     Upper cut-off frequency (Hz).
      Npts (float):       Number of data points (-).
      risco_fac (float):  R_isco = R_star * risco_fac (-, defaults to 1.5); used to compute f_max.
      Fplcr (float):      The mean value of F_+ and F_x: <F> ~ sqrt(<F_+^2 + F_x^2>),
                          which includes the inclination.  Defaults to 2/5.
      verbosity (int):    Verbosity level, defaults to 0: no output.
    
    Returns:
      (pd.df):  Pandas dataframe containing variables, including:
                - fgw:            GW frequency in Hz;
                - htilde:         h~ in 1/Hz;
                - htilde_pSqrtHz: h~ in 1/sqrt(Hz)  (= 2 * htilde * sqrt(fgw)).
    """
    
    # Create DataFrame with the frequency range and call cbc_waveform_frequency_array() to fill it:
    df = _pd.DataFrame(data=_np.logspace(_np.log10(f_low), _np.log10(f_high), Npts), columns=['fgw'])  # Initial column, Npts rows
    
    df = cbc_waveform_frequency_array(df, m1,m2, dist,cosi, risco_fac=1.5, Fplcr=2/5, verbosity=0)
    
    return df


def cbc_waveform_frequency_array(df, m1,m2, dist,cosi, risco_fac=1.5, Fplcr=2/5, verbosity=0):
    """Compute a simple, Newtonian(!) compact-binary-coalescence waveform in the frequency domain for a given
    range of frequencies.
    
    Parameters:
      df (pd.df):         Pandas DataFrame containing frequency array (Hz) in column 'fgw'.
      m1 (float):         Mass of binary component 1 (kg).
      m2 (float):         Mass of binary component 2 (kg).
      dist (float):       Distance of binary (m).
      cosi (float):       Cosine of the inclination angle: +/-1 = face on, 0 = edge-on.
      risco_fac (float):  R_isco = R_star * risco_fac (-, defaults to 1.5); used to compute f_max.
      Fplcr (float):      The mean value of F_+ and F_x: <F> ~ sqrt(<F_+^2 + F_x^2>),
                          which includes the inclination.  Defaults to 2/5.
      verbosity (int):    Verbosity level, defaults to 0: no output.
    
    Returns:
      (pd.df):  Pandas dataframe containing variables, including:
                - fgw:            GW frequency in Hz (input);
                - htilde:         h~ in 1/Hz;
                - htilde_pSqrtHz: h~ in 1/sqrt(Hz)  (= 2 * htilde * sqrt(fgw)).
    """
    
    mt = m1+m2
    Mc = (m1*m2/mt**(1/3))**(3/5)
    
    R1 = radius_BH_NS_from_mass(m1)  # Estimate/compute the BH/NS radius from the object mass
    R2 = radius_BH_NS_from_mass(m2)
    a_min = R1+R2
    
    f_isco  = _ac.c**3 / (6**(3/2) * _ac.pi * _ac.g * mt)
    # f_max = _ac.c**3 / (3**(3/2) * _ac.pi * _ac.g * mt)       # Roughly matches PRX 6 041015 (2016)
    f_max = 1/_ac.pi * _np.sqrt(_ac.G * mt / (risco_fac*a_min)**3)  # f_max based on 1.5 x (sum of radii) and Kepler - same as above, but allows NSs
    
    
    # Frequency domain (see Maggiore Eqs. 4.43-37, p.174):
    h_sq = 5/(24 * _ac.pi**(4/3) * dist**2 * _ac.c**3) * (_ac.G * Mc)**(5/3) / _np.power(df.fgw, 7/3)  # |h(f)|^2 (Maggiore Eq.4.370, p.231)
    # h_sq *= 1.665  # Hack that would give nicer matches! - i.e., 2/5 -> 2/3 or sqrt(2/5)! in the line below
    df['htilde']         = Fplcr * _np.sqrt(h_sq)                # [h] = 1/Hz - Maggiore, Table 7.1, Eq.7.181
    df['htilde_pSqrtHz'] = 2     * df.htilde * _np.sqrt(df.fgw)  # [h] = 1/sqrt(Hz) - for (plot) comparison to ASD; see PRX 6, 041015 (2016), Fig.1
    
    # df['Psi_pl'] = _ac.pi2 * df.fgw * 1  -  0  - _ac.pio4  \
    #     +  3/4 * _np.power(_ac.G * Mc/_ac.c**3 * 8*_ac.pi * df.fgw, -5/3)
    # df['Psi_cr'] = df.Psi_pl + _ac.pio2
    # df['htilde_pl'] = df.htilde * (1+cosi**2)/2 * _np.exp( df.Psi_pl * 1j )
    # df['htilde_cr'] = df.htilde * cosi          * _np.exp( df.Psi_cr * 1j )
    # df['htilde_tot'] = _np.abs(_np.real(df.htilde_pl + df.htilde_cr)/2)  # _np.cos(df.Psi_pl)
    
    
    df = df[df.fgw < f_max]  # Cut the REALLY wrong bits...
    f_low  = df.fgw.iloc[0]
    f_high = df.fgw.iloc[-1]
    
    if verbosity>0:
        print('f_low, f_high (Hz):          ', f_low, f_high)
        print('a_min (km):                  ', a_min/1000)
        print('f_isco, f_max (Hz):          ', f_isco, f_max)
        print('h_start, h_end (1/Hz):       ', df.htilde.iloc[0], df.htilde.iloc[-1])
        print('h_start, h_end (1/sqrt Hz):  ', df.htilde_pSqrtHz.iloc[0], df.htilde_pSqrtHz.iloc[-1])
        
        if verbosity>8: print(df)
    
    return df


def noise_curve(Npts, f_low,f_high, Len, P_L,lam_L, eta_pd, M_mir, R_in,R_end, PRfac, no_FP=False,
                adhoc_lowf=False, verbosity=0):
    
    """Compute a simplified noise curve for a gravitational-wave interferometer.
    
    Parameters:
      Npts (float):     Number of data points (-).
      f_low (float):    Lower frequency cut off (Hz).
      f_high (float):   Higher frequency cut off (Hz).
    
      Len (float):      Length of interferometer arms (m).
      P_L (float):      Laser power (W).
      lam_L (float):    Laser wavelength (m).
      eta_pd (float):   Efficiency of photodetector (fraction 0-1).
    
      M_mir (float):    Mass of the end mirror/test mass (kg).
      R_in (float):     Reflectivity of the input mirrors of the (main) Fabry-Perot cavity (fraction 0-1).
      R_end (float):    Reflectivity of the end mirrors of the interferometer (fraction 0-1).
    
      PRfac (float):    Factor for power recycling (factor 1-...).
      no_FP (bool):     Do NOT use a Fabry-Perot cavity (optional; defaults to False, i.e. DO use a FPC).

      adhoc_lowf (bool):  Add an ad-hoc low-f term to mimic termal/Newtonian/seismic noise (defaults to False).
      verbosity (int):    Verbosity level, defaults to 0: no output.
    
    Returns:
      (pd.df):  Pandas.DataFrame containing noise strains, with columns:
                - asd: the total amplitude spectral density, in strain/sqrt(Hz);
                - asd_shot:  the shot-noise component of the ASD, in strain/sqrt(Hz);
                - asd_rad:   the radiation-pressure component of the ASD, in strain/sqrt(Hz);
                - asd_lowf:  the ad-hoc low-frequency component of the ASD, in strain/sqrt(Hz), if desired.
    """
    
    # Create DataFrame:
    df = _pd.DataFrame(data=_np.logspace(_np.log10(f_low), _np.log10(f_high), Npts), columns=['fgw'])  # Initial column, Npts rows
    
    if no_FP:
        Fin        = _ac.pi/2
        Leff_L     = 1
        f_pole     = 0
        f_pole_fac = 1
    else:
        Fin        = _ac.pi * _np.sqrt(R_in*R_end) / (1 - R_in*R_end)   # Finesse
        Leff_L     = 2*Fin/_ac.pi
        f_pole     = _ac.c / (4 * Fin * Len)                         # Pole frequency
        f_pole_fac = _np.sqrt( 1 + _np.square(df.fgw/f_pole) )
        
        
    df['asd'] = 0  # Most important column first - assign proper values below
    
    df['asd_shot'] = \
        1/(8*Fin*Len) * _np.sqrt( (4*_ac.pi*_ac.h_bar*_ac.c * lam_L) / (eta_pd * PRfac * P_L) ) * f_pole_fac
    
    df['asd_rad'] = 16*_np.sqrt(2) * Fin / (M_mir * Len * _np.square(_ac.pi2*df.fgw)) \
        * _np.sqrt((_ac.h_bar * P_L * PRfac)/(_ac.pi2 * lam_L * _ac.c)) / f_pole_fac
    
    df['asd'] = df.asd_shot + df.asd_rad
    
    if adhoc_lowf:
        # Ad-hoc low-f term, (strongly!) adapted from seismic noise Bader PhD thesis, Eq. 1.2.15:
        seismic_isolation = 1e-4  # 10^10 needed for h ~ 1e-23 m/sqrt(Hz) @10Hz
        alpha = 1e-6  # 1e-6 - 1e-9 m Hz^(3/2)
        pow = 6       # {1e-4, 1e-6, 6} looks roughly like PRX 6 041015 (2016), Fig.1 curves for O1 (and O2?)
        df['asd_lowf'] = alpha / _np.power(df.fgw, pow) / Len * seismic_isolation
        df.asd += df.asd_lowf
    
    if verbosity > 2:
        print()
        print('Len:            ', Len/1000, 'km')
        print('P_L:            ', P_L, 'W')
        print('lam_L:          ', lam_L*1e9, 'nm')
        print('eta_pd:         ', eta_pd)
        print()
        print('M_mir:          ', M_mir, 'kg')
        print('R_in:           ', R_in)
        print('R_end:          ', R_end)
        print()
        print('PRfac:          ', PRfac)
        print()
        
    if verbosity > 1:
        print()
        print('Finesse:        ', Fin)
        print('Leff/L:         ', Leff_L)
        print('f_pole:         ', f_pole)
        print()
        print('min ASD_shot:   ', df.asd_shot.min(), '/sqrt(Hz)')
        print('min ASD_rad:    ', df.asd_rad.min(),  '/sqrt(Hz)')
        print('min ASD:        ', df.asd.min(),      '/sqrt(Hz)')
        print('min ASD:        ', df.asd.min()*10,   '@ 100Hz')
        print()
        # print('MI ASD: ', 1/(_ac.pi*Len) * )
    
    return df

    
def isco_radius_from_mass(mass, spin=0, as_km=False):
    """Compute the black-hole ISCO GW radius from its mass and spin.
    
    Parameters:
      mass (float):  mass of the black hole (Mo).
      spin (float):  spin of the black hole (-1 - +1, defaults to 0).
      as_km (bool):  the result is expressed in km, else in terms of the BH mass M (defaults to False).
    
    Returns:
      (float):  ISCO radius in either km or M, as desired.
    """
    
    scalar_input = True
    mass = _np.asarray(_np.copy(mass+spin*0), dtype=float)  # Copy and typecast to numpy.ndarray - ensure float!
    spin = _np.asarray(_np.copy(mass*0+spin), dtype=float)  # Copy and typecast to numpy.ndarray - ensure float!
    if mass.ndim == 0:
        mass = mass[None]  # Makes mass a 1D array.  Comment: use np.newaxis instead?
    else:
        scalar_input = False
    if spin.ndim == 0:
        spin = spin[None]  # Makes spin a 1D array.  Comment: use np.newaxis instead?
    else:
        scalar_input = False
    
    z1 = 1 + _np.power(1 - _np.square(spin),_ac.c3rd) * \
        ( _np.power(1+_np.abs(spin),_ac.c3rd) + _np.power(1-_np.abs(spin),_ac.c3rd) )
    z2 = _np.sqrt(3*_np.square(spin) + _np.square(z1))
    
    r_isco = _np.zeros_like(mass+spin)
    sel = spin<0
    r_isco[sel]  = mass[sel] * (3+z2[sel] - _np.sqrt((3-z1[sel])*(3+z1[sel] + 2*z2[sel])) )  # Expressed in M
    sel = spin>=0
    r_isco[sel]  = mass[sel] * (3+z2[sel] + _np.sqrt((3-z1[sel])*(3+z1[sel] + 2*z2[sel])) )  # Expressed in M
    
    if as_km: r_isco *= _ac.G*_ac.Mo/_ac.c**2 / 1000  # Convert from M to m to km
    
    if scalar_input:
        return float(_np.squeeze(r_isco))  # Array -> scalar (float)
    
    return r_isco


def isco_frequency_from_isco_radius(mass, r_isco, as_km=False):
    """Compute the ISCO GW frequency from the mass and ISCO radius expressed in M.
    
    Parameters:
      mass (float):    mass of the object (Mo).
      r_isco (float):  ISCO radius of the object (in units of M, the BH mass).
      as_km (bool):    the ISCO radius is expressed in km, else in terms of the BH mass M (defaults to False).
    
    Returns:
      (float):  ISCO GW frequency in Hertz.
    """
    
    if not as_km: r_isco *= _ac.G*_ac.Mo/_ac.c**2 / 1000  # Convert from M to m to km
    
    f_isco_gw = 2 * _ac.c**3 / (2*_ac.pi * _np.power(r_isco/mass,1.5) * _ac.g*mass*_ac.m_sun)
    
    return f_isco_gw


def isco_frequency_from_mass(mass, spin=0):
    """Compute the ISCO GW frequency from the mass and ISCO radius expressed in M.
    
    Parameters:
      mass (float):    mass of the object (Mo).
      spin (float):    spin of the black hole (-1 - +1, defaults to 0).
    
    Returns:
      (float):  ISCO GW frequency in Hertz.
    """
    
    r_isco = isco_radius_from_mass(mass, spin, as_km=False)  # R_isco in terms of M
    f_isco_gw = 2 * _ac.c**3 / (2*_ac.pi * _np.power(r_isco/mass,1.5) * _ac.g*mass*_ac.m_sun)
    
    return f_isco_gw


def radius_BH_NS_from_mass(mass):
    """Estimate the radius of a (non-spinning) black hole or neutron star from its mass.
    
    Parameters:
      mass (float):  mass of the object (kg).
    
    Returns:
      (float):  radius of the object (m).
    
    
    Note: this function simply returns:
      - 11.5 km as the radius of a NS if mass < 3.9Mo;
      - the Schwarzschild radius if mass >= 3.9Mo.
    
    Rationale:
      - all NSs have radii of ~11.5km here: https://arxiv.org/abs/1205.6871;
      - Rs ~ 11.5km for a 3.9Mo BH.
    """
    
    if mass < 3.9*_ac.sun_m:         # R_s ~ 11.5km for BH of 3.9Mo
        rad = 11.5*_ac.km            # R_NS (m)
    else:
        rad = 2*_ac.G*mass/_ac.c**2  # R_BH (m)
    return rad
