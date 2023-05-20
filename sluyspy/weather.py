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


"""Weather functions for the sluyspy package"""


import numpy as _np



def wind_chill_temperature(temp, wind_vel):
    """Compute wind-chill ("real-feel") temperature from the air temperature and wind velocity.
    
    Parameters:
      temp (float):      Air temperature at 1.5m above ground (°C).
      wind_vel (float):  Wind velocity at 10m above ground (m/s).
    
    Returns:
      (float):  Wind-chill temperature (°C).
    
    Source:
      - https://en.wikipedia.org/wiki/Wind_chill
        - but wind speed in m/s instead of km/h (3.6^0.16*11.37=13.96; 3.6^0.16*39.65=48.67).
        - ensure that the wind chill NEVER exceeds the temperature (was: only if wind_vel < 1.3).
      - note: the power 0.16 converts 10m wind velocity to 1.5m.
    """
    
    # Compute wind-chill ("real-feel") temperature:
    wchil = 13.12 + 0.6215 * temp + (0.4867*temp - 13.96)*wind_vel**0.16
    
    # Wind chill == air temperature for T>10°C:
    if _np.ndim(wchil) == 0:  # Dimension: 0: scalar, >0: array-like
        # if wind_vel < 1.3:
        wchil = min(wchil, temp)
    else:
        # wchil[wind_vel < 1.3] = _np.minimum( wchil[wind_vel < 1.3], temp[wind_vel < 1.3] )
        wchil = _np.minimum( wchil, temp )
    
    # Round off to nearest 0.1°C, since it is unlikely that the air temperature is known to better than 0.1°C
    # or that this simple model is more accurate than that:
    wchil = _np.round(wchil,1)
    
    return wchil



def wind_dir_str_from_az(az):
    """Convert a wind direction (azimuth) in degrees to a three-character English abbreviation string.
    
    Parameters:
      az (float):  Azimuth (degrees; 0=North, 90=East).
    
    Returns:
      (str):  Three-character English wind-direction abbreviation.
    """
    
    tmp_val = int((az/22.5)+0.5)
    str_arr = ['N','NNE','NE','ENE','E','ESE', 'SE', 'SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
    
    return str_arr[(tmp_val % 16)]



def sky_power_from_rain_means(rain):
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


def sky_power_from_rain_medians(rain):
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


