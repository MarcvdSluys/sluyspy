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


"""Weather functions for the sluyspy package"""


import numpy as _np
import pandas as _pd
import datetime as _dt



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
    print('Sorry, this function moved to solar_energy.cloud_power_from_rain_means()')
    exit(1)
    return


def sky_power_from_rain_medians(rain):
    print('Sorry, this function moved to solar_energy.cloud_power_from_rain_medians()')
    exit(1)
    return


def dew_point_from_tempc_rh(temp_c, rh):
    """Compute the dew point from the temperature and relative humidity.
    
    Parameters:
      temp_c (float):  Air temperature (degrees Celsius).
      rh (float):      Relative humidity (fraction).
    
    Returns:
      (float):  Dew point (degrees Celsius).
    
    See:
      https://en.wikipedia.org/wiki/Dew_point
    """
    
    temp_c0  = 273.7
    tempfac  = 17.27
    gam = tempfac * temp_c/(temp_c0+temp_c) + _np.log(rh)
    
    return temp_c0 * gam/(tempfac-gam)


def water_vapor_saturated_density_from_tempc(temp_c):
    """Compute the saturated water-vapor density in air for a given temperature.
    
    Parameters:
      temp_c (float):  Air temperature (degrees Celsius).
    
    Returns:
      (float):  Saturated water-vapor density (g/m^3).
    
    Note:
      - uses data from http://hyperphysics.phy-astr.gsu.edu/hbase/kinetic/relhum.html#c3:
        - for T= -10 - +60°C.
      - drops to 0 below T~-25°C;
      - significantly better results than original fit (3rd order polynomial):
        - for T<~-15°C and T>~45°C: by eye;
        - for -10°C < T < 60°C (range original fit -0°C < T < 40°C):
          - typical sigma 0.116 (T=0-40°C) -> 0.030 g/m^3 (T=-10-60°C);
          - max. abs. deviation: 0.168 g/m^3 (T=0-40°C; @T=0°C)  ->  0.0445 g/m^3 (T=-10-60°C; @T=25°C)
          - max. rel. deviation: 3.46  %     (T=0-40°C; @T=0°C)  ->  0.194  %     (T=-10-60°C; @T=25°C)
    """
    
    return _np.maximum(4.85684 + 3.32664e-01 * temp_c + 1.00885e-02 * temp_c**2 + 1.89345e-04 * temp_c**3
                       + 1.09606e-06 * temp_c**4 + 1.83396e-08 * temp_c**5, 0)


def absolute_humidity_from_tempc_rh(temp_c, rh):
    """Compute the absolute humidity (water-vapor density) from the temperature and relative humidity.
    
    Parameters:
      temp_c (float):  Air temperature (degrees Celsius).
      rh (float):      Relative humidity (fraction).
    
    Returns:
      (float):  Absolute humidity (water-vapor density;  g/m^3).
    """
    
    return water_vapor_saturated_density_from_tempc(temp_c) * rh


def knmi_read_hourly_weather(filename, start_date=None, end_date=None, tidy=True):
    """Reads a KNMI file containing hourly weather measurement data from a particular station.
    
    Reads the CSV files provided on the KNMI website for the weather data over the last decade from a chosen
    station. This function reads the weather data from a chosen start date to the chosen end date, which is
    NOT included.  For example, for the whole of the year 2020, specify 2020,1,1, 2021,1,1.
    
    Parameters:
      filename (str): filename to select the specific station, this is "uurgeg_260_2011-2020_Bilt.csv" for De Bilt
    
      start_date (datetime):  start date:  date of the first data entry to be returned (timezone aware; optional).
      end_date   (datetime):  end date:    date of the first data entry NOT to be returned (timezone aware; optional).
    
      tidy       (bool):      tidy up: remove station column, convert silly date and time to datetime,
                              temperature to °C and sunshine to a fraction (optional).
    
    Returns:
      pandas.DataFrame:  Table containing ~23-25 columns with weather data.
    
      - yyyymmdd (int):  Date (YYYY=year,MM=month,DD=day).
      - hh (int):        Time in hours (note: 1-24!), the hourly division 05 runs from 04.00 UT to 5.00 UT.
      - dtm (datetime):  Date and time of the entry (UT), replacing yyyymmdd and hh.
    
      - t (float):       Temperature at 1.50 m at the time of observation (°C).
      - sq (float):      Fraction of the hour with sunshine (0-1).
      - q (float):       Global horizontal radiation (W/m^2 (or J/cm^2/h)).
    """
    
    # Read the data file into a Pandas DataFrame.  Use lower-case column names:
    col_names = ['stn','yyyymmdd','hh','dd','fh','ff','fx','t','t10n','td','sq','q','dr','rh','p','vv','n','u','ww','ix','m','r','s','o','y']
    try:
        knmi_data = _pd.read_csv(filename, header=28, names=col_names, sep=r'\s*,\s*', engine='python')
    except Exception as e:
        print(e)
        exit(1)
    
    # Select the data for the desired date range.  Add one hour, since datetime contains the time at which the hour ENDS!
    if start_date and end_date:
        knmi_data = knmi_data[knmi_data['datetime'] >= start_date + _dt.timedelta(hours=1)]  # Date must be >= start_date
        knmi_data = knmi_data[knmi_data['datetime'] <    end_date + _dt.timedelta(hours=1)]  # Date must be < end_date
        knmi_data = knmi_data.reset_index(drop=True)  # Reset the index so that it starts at 0 again.  Don't keep the original index as a column.
    
    # Tidy up if desired:
    if tidy:
        del knmi_data['stn']
        # Convert the yyyymmdd and hh columns into a datetime-object column with hours in [0,23] rather than in [1,24]:
        knmi_data = knmi_datetime_from_datehour(knmi_data)
        
        knmi_data.loc[:, 't']  /= 10                              # Convert the temperature at 1.50 m from 0.1°C -> °C.
        knmi_data.loc[knmi_data.loc[:, 'sq'] == -1, 'sq'] = 0.25  # Sunshine time == -1 indicates 0 - 0.05 hours, so assume 0.025 hours, expressed in [0.1 hours]
        knmi_data.loc[:, 'sq'] /= 10                              # Convert the sunshine time from [0.1 hours] to a fraction (0-1)
        knmi_data.loc[:, 'q']  /= 0.36                            # Convert the global horizontal radiation from [J/cm^2/h] to [W/m^2]
    
    return knmi_data


def knmi_datetime_from_datehour(knmi_data):
    """Return a datetime column named 'dtm' for given KNMI date and hour columns.
    
    The KNMI date is expressed as an integer formatted as YYYYMMDD, while the hours run from 1-24 rather than
    from 0-23.  This causes problems when converting to Python or Pandas datetime objects.
    
    Parameters:
      knmi_data (Pandas df):  KNMI weather dataframe.
    
    Returns:
      (Pandas df):  KNMI weather dataframe.
    """
    
    from astrotool.date_time import fix_date_time
    
    # Split the yyyymmdd column into separate numpy arrays:
    ymd     = knmi_data['yyyymmdd'].values  # Numpy array
    years   = _np.floor(ymd/1e4).astype(int)
    months  = _np.floor((ymd - years*1e4)/100).astype(int)
    days    = _np.floor(ymd - years*1e4 - months*100).astype(int)
    
    # Create numpy arrays for the time variables:
    hours   = knmi_data['hh'].values  # Numpy array
    minutes = _np.zeros(hours.size)
    seconds = _np.zeros(hours.size) + 0.001  # 1 ms past the hour, to ensure no negative round-off values occur (e.g. 2021,1,1, 0,0,-1e-5 -> 2020,12,31, 23,59,59.99999)
    
    # Fix the dates, e.g. turning 2020-12-31 24:00:00 to 2021-01-01 00:00:00:
    years,months,days, hours,minutes,seconds = fix_date_time(years,months,days, hours,minutes,seconds)
    
    # Combine the 1D numpy arrays into a single 2D array with the original arrays as COLUMNS, and convert it to a Pandas df:
    dts = _pd.DataFrame(_np.vstack([years,months,days,hours]).transpose(), columns=['year','month','day','hour'])
    dts = _pd.to_datetime(dts, utc=True)    # Turn the columns in the df into a single datetime64[ns] column
    
    # Add the datetime column to the KNMI weather dataframe:
    knmi_data['dtm'] = dts
    knmi_data = knmi_data[['dtm'] + [x for x in knmi_data.columns if x != 'dtm']]  # Move dtm column to front
    
    del knmi_data['yyyymmdd'], knmi_data['hh']
    
    return knmi_data


