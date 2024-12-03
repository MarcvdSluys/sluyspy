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


"""Weather functions for the sluyspy package"""


import numpy as _np
import pandas as _pd
import datetime as _dt
import astroconst as _ac



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
    print('Sorry, this function moved to sluyspy.solar_energy._cloud_power_from_rain(), called from solar_power_from_true_sky_rain()')
    exit(1)
    return


def sky_power_from_rain_medians(rain):
    print('Sorry, this function moved to sluyspy.solar_energy._cloud_power_from_rain(), called from solar_power_from_true_sky_rain()')
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


def knmi_station_data(remove_nans=False):
    """Return a Pandas DataFrame containing the data of Dutch KNMI weather stations.
    
    Parameters:
      remove_nans (bool):  Remove entries containing a NaN.  Optional; defaults to False.
    
    Returns:
      (pd.df):  Pandas DataFrame containing and index and five columns:
    
      - index (int):  Station number. Note that most stations start with a leading zero, which is omitted here.
      - lon (float):  Geographical longitude of the station, in radians east of Greenwich.
      - lat (float):  Geographical latitude of the station, in radians north of the equator.
      - alt (float):  Altitude of the station above sea level, in metres.
      - name (str):   (A) name of the station.
      - fname (str):  String to compose a file name from.  This is the name from the KNMI .nc files,
                      in lower case, with spaces and slashes replaced by underscores, and brackets removed.
    """
    
    df = _pd.DataFrame( {
        'lon':   {6201: float('nan'), 6203: float('nan'), 6204: float('nan'), 6205: float('nan'), 6207: float('nan'), 6208: float('nan'), 6209: 4.518, 6210: 4.43, 6211: float('nan'), 6214: float('nan'), 6215: 4.437, 6216: float('nan'), 6225: 4.555, 6229: float('nan'), 6233: float('nan'), 6235: 4.781, 6236: float('nan'), 6237: float('nan'), 6238: float('nan'), 6239: float('nan'), 6240: 4.79, 6242: 4.921, 6248: 5.174, 6249: 4.979, 6251: 5.346, 6252: float('nan'), 6257: 4.603, 6258: 5.401, 6260: 5.18, 6265: 5.274, 6267: 5.384, 6269: 5.52, 6270: 5.752, 6273: 5.888, 6275: 5.873, 6277: 6.2, 6278: 6.259, 6279: 6.574, 6280: 6.585, 6283: 6.657, 6285: 6.399, 6286: 7.15, 6290: 6.891, 6308: 3.379, 6310: 3.596, 6311: 3.672, 6312: 3.622, 6313: 3.242, 6315: 3.998, 6316: 3.694, 6317: float('nan'), 6319: 3.861, 6320: float('nan'), 6321: float('nan'), 6323: 3.884, 6324: 4.006, 6330: 4.122, 6331: 4.193, 6340: 4.342, 6343: 4.313, 6344: 4.447, 6348: 4.926, 6350: 4.936, 6356: 5.146, 6370: 5.377, 6375: 5.707, 6377: 5.763, 6380: 5.762, 6391: 6.197},
        'lat':   {6201: float('nan'), 6203: float('nan'), 6204: float('nan'), 6205: float('nan'), 6207: float('nan'), 6208: float('nan'), 6209: 52.465, 6210: 52.171, 6211: float('nan'), 6214: float('nan'), 6215: 52.141, 6216: float('nan'), 6225: 52.463, 6229: float('nan'), 6233: float('nan'), 6235: 52.928, 6236: float('nan'), 6237: float('nan'), 6238: float('nan'), 6239: float('nan'), 6240: 52.318, 6242: 53.241, 6248: 52.634, 6249: 52.644, 6251: 53.392, 6252: float('nan'), 6257: 52.506, 6258: 52.649, 6260: 52.1, 6265: 52.13, 6267: 52.898, 6269: 52.458, 6270: 53.224, 6273: 52.703, 6275: 52.056, 6277: 53.413, 6278: 52.435, 6279: 52.75, 6280: 53.125, 6283: 52.069, 6285: 53.575, 6286: 53.196, 6290: 52.274, 6308: 51.381, 6310: 51.442, 6311: 51.379, 6312: 51.768, 6313: 51.505, 6315: 51.447, 6316: 51.657, 6317: float('nan'), 6319: 51.226, 6320: float('nan'), 6321: float('nan'), 6323: 51.527, 6324: 51.596, 6330: 51.992, 6331: 51.48, 6340: 51.449, 6343: 51.893, 6344: 51.962, 6348: 51.97, 6350: 51.566, 6356: 51.859, 6370: 51.451, 6375: 51.659, 6377: 51.198, 6380: 50.906, 6391: 51.498},
        'alt':   {6201: float('nan'), 6203: float('nan'), 6204: float('nan'), 6205: float('nan'), 6207: float('nan'), 6208: float('nan'), 6209: 0.0, 6210: -0.2, 6211: float('nan'), 6214: float('nan'), 6215: -1.1, 6216: float('nan'), 6225: 4.4, 6229: float('nan'), 6233: float('nan'), 6235: 1.2, 6236: float('nan'), 6237: float('nan'), 6238: float('nan'), 6239: float('nan'), 6240: -3.3, 6242: 10.8, 6248: 0.8, 6249: -2.4, 6251: 0.7, 6252: float('nan'), 6257: 8.5, 6258: 7.3, 6260: 1.9, 6265: 13.9, 6267: -1.3, 6269: -3.7, 6270: 1.2, 6273: -3.3, 6275: 48.2, 6277: 2.9, 6278: 3.6, 6279: 15.8, 6280: 5.2, 6283: 29.1, 6285: 0.0, 6286: -0.2, 6290: 34.8, 6308: 0.0, 6310: 8.0, 6311: 0.0, 6312: 0.0, 6313: 0.0, 6315: 0.0, 6316: 0.0, 6317: float('nan'), 6319: 1.7, 6320: float('nan'), 6321: float('nan'), 6323: 1.4, 6324: 0.0, 6330: 11.9, 6331: 0.0, 6340: 19.2, 6343: 3.5, 6344: -4.3, 6348: -0.7, 6350: 14.9, 6356: 0.7, 6370: 22.6, 6375: 22.0, 6377: 30.0, 6380: 114.3, 6391: 19.5},
        'name':  {6201: float('nan'), 6203: float('nan'), 6204: float('nan'), 6205: float('nan'), 6207: float('nan'), 6208: float('nan'), 6209: 'IJmond', 6210: 'Valkenburg Zh', 6211: float('nan'), 6214: float('nan'), 6215: 'Voorschoten', 6216: float('nan'), 6225: 'IJmuiden', 6229: float('nan'), 6233: float('nan'), 6235: 'De Kooy', 6236: float('nan'), 6237: float('nan'), 6238: float('nan'), 6239: float('nan'), 6240: 'Schiphol', 6242: 'Vlieland', 6248: 'Wijdenes', 6249: 'Berkhout', 6251: 'Hoorn Terschelling', 6252: float('nan'), 6257: 'Wijk aan Zee', 6258: 'Houtribdijk', 6260: 'De Bilt', 6265: 'Soesterberg', 6267: 'Stavoren', 6269: 'Lelystad', 6270: 'Leeuwarden', 6273: 'Marknesse', 6275: 'Deelen', 6277: 'Lauwersoog', 6278: 'Heino', 6279: 'Hoogeveen', 6280: 'Eelde', 6283: 'Hupsel', 6285: 'Huibertgat', 6286: 'Nieuw Beerta', 6290: 'Twenthe', 6308: 'Cadzand', 6310: 'Vlissingen', 6311: 'Hoofdplaat', 6312: 'Oosterschelde', 6313: 'Vlakte van De Raan', 6315: 'Hansweert', 6316: 'Schaar', 6317: float('nan'), 6319: 'Westdorpe', 6320: float('nan'), 6321: float('nan'), 6323: 'Wilhelminadorp', 6324: 'Stavenisse', 6330: 'Hoek van Holland', 6331: 'Tholen', 6340: 'Woensdrecht', 6343: 'Rotterdam Geulhaven', 6344: 'Rotterdam', 6348: 'Cabauw Mast', 6350: 'Gilze-Rijen', 6356: 'Herwijnen', 6370: 'Eindhoven', 6375: 'Volkel', 6377: 'Ell', 6380: 'Maastricht', 6391: 'Arcen'},
        'fname': {6201: 'd15-fa-1', 6203: 'p11-b', 6204: 'k14-fa-1c', 6205: 'a12-cpp', 6207: 'l9-ff-1', 6208: 'awg-1', 6209: 'ijmond', 6210: float('nan'), 6211: 'j6-a', 6214: 'buitengaats_bg-ohvs2', 6215: 'voorschoten', 6216: 'hollandse_kust_zuid_alpha', 6225: 'ijmuiden', 6229: 'texelhors', 6233: 'assendelft', 6235: 'de_kooy_airport', 6236: 'muiden', 6237: 'nieuw-vennep', 6238: 'nieuwkoop', 6239: 'f3-fb-1', 6240: 'schiphol_airport', 6242: 'vlieland_vliehors', 6248: 'wijdenes', 6249: 'berkhout', 6251: 'hoorn_terschelling', 6252: 'k13-a', 6257: 'wijk_aan_zee', 6258: 'houtribdijk', 6260: 'de_bilt', 6265: float('nan'), 6267: 'stavoren', 6269: 'lelystad_airport', 6270: 'leeuwarden_airport', 6273: 'marknesse', 6275: 'deelen_airport', 6277: 'lauwersoog', 6278: 'heino', 6279: 'hoogeveen', 6280: 'groningen_airport_eelde', 6283: 'hupsel', 6285: 'huibertgat', 6286: 'nieuw_beerta', 6290: 'twenthe_airport', 6308: 'cadzand', 6310: 'vlissingen', 6311: float('nan'), 6312: 'oosterschelde', 6313: 'vlakte_van_de_raan', 6315: 'hansweert', 6316: 'schaar', 6317: 'borssele_alpha', 6319: 'westdorpe', 6320: 'lichteiland_goeree', 6321: 'europlatform', 6323: 'wilhelminadorp', 6324: 'stavenisse', 6330: 'hoek_van_holland', 6331: 'tholen', 6340: 'woensdrecht_airport', 6343: 'rotterdam_geulhaven', 6344: 'rotterdam_airport', 6348: 'cabauw', 6350: 'gilze-rijen_airport', 6356: 'herwijnen', 6370: 'eindhoven_airport', 6375: 'volkel_airport', 6377: 'ell', 6380: 'maastricht_airport', 6391: 'arcen'}
    } )
    
    # Convert coordinates from degrees to radians:
    df.lon *= _ac.d2r
    df.lat *= _ac.d2r
    
    if remove_nans:
        df = df[df['lon'].notna()]      # Keep only rows where df.col is NOT Null/None/NaN
        df = df[df['fname'].notna()]    # Keep only rows where df.col is NOT Null/None/NaN
    
    return df
