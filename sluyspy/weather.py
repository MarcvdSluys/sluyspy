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
      - note: the power 0.16 converts 10m wind velocity to 1.5m.
    """
    
    # Compute wind-chill ("real-feel") temperature:
    wchil = 13.12 + 0.6215 * temp + (0.4867*temp - 13.96)*wind_vel**0.16
    
    # Wind chill == air temperature for T>10°C:
    if _np.ndim(wchil) == 0:  # Dimension: 0: scalar, >0: array-like
        if wind_vel < 1.3: wchil = min(wchil, temp)
    else:
        wchil[wind_vel < 1.3] = _np.minimum( wchil[wind_vel < 1.3], temp[wind_vel < 1.3] )
    
    # Round off to nearest 0.1°C, since it is unlikely that the air temperature is known to better than 0.1°C
    # or that this simple model is more accurate than that:
    wchil = _np.round(wchil,1)
    
    return wchil
