# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2023  Marc van der Sluys - Nikhef/Utrecht University - marc.vandersluys.nl
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


def cloud_power_from_rain_means(rain):
    """Guestimate the fraction of light power coming from an overcast sky, from the amount of rain.

    Parameters:
      rain (float):  Rain value(s), in mm/hr.

    Returns:
      (float):  P/Pclear; the fraction of clear-sky solar power coming from an overcast sky.
    
    Note:
      - this is about as close to witchcraft as it is to science;
      - this version uses a fit to the MEANS of the rain bins;
      - see compare-selections.py.
    """
    
    # ppclr = 20 * _np.square(rain) - 4 * rain + 0.395  # 0-0.1
    # ppclr[rain>0.1] = 0.74 * _np.exp( -( rain[rain>0.1] + 2.97 ) / 2.3 )
    
    ppclr = 80 * _np.square(rain) - 8 * rain + 0.4 - 0.0009  # 0-0.05
    ppclr[rain>0.05] = 0.74 * _np.exp( -( rain[rain>0.05] + 2.97 ) / 2.3 )
    
    return ppclr


def cloud_power_from_rain_medians(rain):
    """Guestimate the fraction of light power coming from an overcast sky, from the amount of rain.

    Parameters:
      rain (float):  Rain value(s), in mm/hr.

    Returns:
      (float):  P/Pclear; the fraction of clear-sky solar power coming from an overcast sky.
    
    Note:
      - this is about as close to witchcraft as it is to science;
      - this version uses a fit to the MEDIANS of the rain bins;
      - see compare-selections.py.
    """
    
    # ppclr = 13 * _np.square(rain) - 2.6 * rain + 0.25  # 0-0.1
    # ppclr[rain>0.1] = 2.06 * _np.exp( -( rain[rain>0.1] + 10.67 ) / 3.78 )
    
    ppclr = 52 * _np.square(rain) - 5.2 * rain + 0.25 + 0.00085  # 0-0.05
    ppclr[rain>0.05] = 2.06 * _np.exp( -( rain[rain>0.05] + 10.67 ) / 3.78 )
    
    return ppclr


def solar_power_from_true_sky(Pclear, cloud_cover, rain):
    """Compute solar power coming from a realistic (non-clear) sky, as a function of the power from the clear sky, the cloud cover and rain.
    
    Parameters:
      Pclear (float):       (Electrical) solar power from clear sky (e.g. W or kW).
      cloud_cover (float):  Cloud cover (%).
      rain (float):         Rain (mm/h).
    
    Returns:
      (float):  (Electrical) solar power coming from a realistic sky (clear + clouded; same unit as Pclear).
    """
    
    # Rain intensity *if* it rains := rain this hour / cloud cover (assumption: no clouds, no rain):
    df = _pd.DataFrame()
    df['rain_int'] = rain
    df['clouds']   = cloud_cover
    df['Pclrsky']  = Pclear
    
    df.loc[df.clouds>0, 'rain_int'] = df.loc[df.clouds>0, 'rain_int'] / df.loc[df.clouds>0, 'clouds'] * 100
    
    df['PPclr'] = cloud_power_from_rain_means(df.rain_int)  # P/P_clearsky, based on rain
    # df['PPclr'] = sse.cloud_power_from_rain_medians(df.rain_int)  # P/P_clearsky, based on rain - not so good?
    
    df.PPclr = (df.PPclr * df.clouds  +  1 * (100-df.clouds))/100  # Weighted sum of sun and cloud contributions
    df['Pclouds'] = df.Pclrsky*df.PPclr  # Take into account clouds in predicted power
    
    # return df.rain_int, df.PPclr, df.Pclouds
    return df.Pclouds

    
