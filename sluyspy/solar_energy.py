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


"""Solar-energy functions for the sluyspy package"""


import numpy as _np
import pandas as _pd
# import pytz as _tz
# import solarenergy as _se


def solar_power_from_true_sky_rain(Pclear, cloud_cover, rain, fittype='means'):
    """Compute solar power coming from a realistic (non-clear) sky, as a function of the power from the clear sky, the cloud cover and rain.
    
    Parameters:
      Pclear (float):       (Electrical) solar power from clear sky (e.g. W or kW).
      cloud_cover (float):  Cloud cover (%).
      rain (float):         Rain (mm/h).
      fittype (str):        Type of fit: 'orig_data' (worst), 'means' (best, default) or 'medians'.
    
    Returns:
      (float):  (Electrical) solar power coming from a realistic sky (clear + clouded; same unit as Pclear).
    """
    
    # Set up df:
    df = _pd.DataFrame()
    df['rain_int'] = rain
    df['clouds']   = cloud_cover
    df['Pclrsky']  = Pclear
    
    # Rain intensity *if* it rains := rain this hour / cloud cover (assumption: no clouds, no rain):
    df.loc[df.clouds>0, 'rain_int'] = df.loc[df.clouds>0, 'rain_int'] / df.loc[df.clouds>0, 'clouds'] * 100
    
    df['PPclr'] = _cloud_power_from_rain(df.rain_int, fittype)  # P/P_clearsky, based on rain
    
    df.PPclr = (df.PPclr * df.clouds  +  1 * (100-df.clouds))/100  # Weighted sum of cloud and sun contributions
    df['Pclouds'] = df.Pclrsky*df.PPclr  # Take into account clouds in predicted power
    
    # return df.rain_int, df.PPclr, df.Pclouds
    return df.Pclouds

    
def _cloud_power_from_rain(rain, fittype='means'):
    """Guestimate the fraction of light power coming from an overcast sky, from the amount of rain.
    
    Parameters:
      rain (float):   Rain value(s), in mm/hr.
      fittype (str):  Type of fit: 'means' (best?; default) or 'medians'.
    
    Returns:
      (float):  P/Pclear; the fraction of clear-sky solar power coming from an overcast sky.
    
    Note:
      - this is about as close to witchcraft as it is to science;
      - this version uses a fit to the MEANS of the rain bins;
      - see compare-selections.py.
    """
    
    if fittype == 'means':
        # 2023-08: red.chi2 ~ 0.191161
        # ppclr = 20 * _np.square(rain) - 4 * rain + 0.395  # 0-0.1
        # ppclr[rain>0.1] = 0.74 * _np.exp( -( rain[rain>0.1] + 2.97 ) / 2.3 )
        
        # 2023-08: red.chi2 ~ 0.190071
        ppclr = 80 * _np.square(rain) - 8 * rain + 0.4 - 0.0009  # 0-0.05
        ppclr[rain>0.05] = 0.74 * _np.exp( -( rain[rain>0.05] + 2.97 ) / 2.3 )
        
    elif fittype == 'medians':
        # 2023-08: red.chi2 ~ 0.291121
        # ppclr = 13 * _np.square(rain) - 2.6 * rain + 0.25  # 0-0.1
        # ppclr[rain>0.1] = 2.06 * _np.exp( -( rain[rain>0.1] + 10.67 ) / 3.78 )
        
        # 2023-08: red.chi2 ~ 0.292222
        ppclr = 52 * _np.square(rain) - 5.2 * rain + 0.25 + 0.00085  # 0-0.05
        ppclr[rain>0.05] = 2.06 * _np.exp( -( rain[rain>0.05] + 10.67 ) / 3.78 )
    
    return ppclr


def solar_power_from_true_sky_rh(Pclrsky, cloud_cover, rh, fittype='means'):
    """Compute solar power coming from a realistic (non-clear) sky, as a function of the power from
       the clear sky, the cloud cover and relative humidity.
    
    Parameters:
      Pclrsky (float):      (Electrical) solar power from clear sky (e.g. W or kW).
      cloud_cover (float):  Cloud cover (%).
      rh (float):           Relative humidity (%).
      fittype (str):        Type of fit: 'orig_data' (worst), 'means' (best, default) or 'medians'.
    
    Returns:
      (float):  (Electrical) solar power coming from a realistic sky (clear + clouded; same unit as Pclear).
    """
    
    clouds = cloud_cover/100  # % -> fraction
    
    PPclr_cloud, PPclr_sun = _cloud_power_from_rh_means(rh, fittype)  # P/P_clearsky, based on rh
    
    PPclr = (PPclr_cloud * clouds  +  PPclr_sun * (1-clouds))  # Weighted sum of cloud and sun contributions
    Pclouds = Pclrsky*PPclr  # Take into account clouds in predicted power
    
    return Pclouds


def _cloud_power_from_rh_means(rh, fittype='means'):
    """Guestimate the fraction of light power coming from an overcast sky, from the relative humidity.
    
    Parameters:
      rh (float):     Relative humidity (%).
      fittype (str):  Type of fit: 'orig_data' (worst), 'means' (best) or 'medians'.
    
    Returns:
      (tuple):  Tuple containing (ppclr_cloud, ppclr_sun):
    
      - ppclr_cloud (float):  P/Pclear; the fraction of clear-sky solar power coming from an overcast sky.
      - ppclr_sun (float):    P/Pclear; the fraction of clear-sky solar power coming from a sunny sky.
    
    Note:
      - this is about as close to witchcraft as it is to science;
      - see compare-selections.py.
    """
    
    if fittype == 'orig_data':
        ppclr_cloud = 0.525804 - 5.09361e-03*rh  # When clouded
        ppclr_sun   = 0.977976 + 5.09722e-04*rh  # When sunny
    if fittype == 'means':  # Looks best
        ppclr_cloud = 0.973944 - 8.74388e-03*rh  # When clouded
        ppclr_sun   = 0.908390 + 2.13867e-03*rh  # When sunny
    if fittype == 'medians':
        ppclr_cloud = 0.885572 - 8.40989e-03*rh  # When clouded
        ppclr_sun   = 0.950993 + 1.31021e-03*rh  # When sunny
    
    return ppclr_cloud, ppclr_sun
