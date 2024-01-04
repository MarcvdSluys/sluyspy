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


"""Functions to deal with WP weather data in the sluyspy package"""

import numpy as _np
import pandas as _pd
import sluyspy.weather as _swtr


def read_36h_forecast_data(wp_dir, loc, verbosity=1):
    """Read WP 36h forecast files (full day today + latest) and combine them.
    
    Parameters:
      wp_dir (str):     Directory containing the WP data files.
      loc (str):        Name of the town to read data for.
      verbosity (int):  Verbosity (0-4 for silent to loud).
    
    Returns:
      (pd.df):  Pandas.DataFrame containing time, clouds, rain, temp, press, RH, W.speed, W.dir.
    """
    
    import datetime as dt
    today = dt.date.today()
    
    # Set WP input file name:
    WP36File = wp_dir+'wp_weer_'+today.strftime('%Y-%m-%d')+'_36h.dat'
    
    # Read today's forecast:
    if verbosity > 1: print('- '+WP36File)
    df_today    = read_36h_forecast_file(WP36File, loc, verbosity)
    
    # Read tomorrow's forecast:
    if verbosity > 1: print('- '+wp_dir+'wp_weer_latest_36h.dat')
    df_tomorrow = read_36h_forecast_file(wp_dir+'wp_weer_latest_36h.dat', loc, verbosity)
    
    # Combine the two datasets:
    if (df_today is None) and (df_tomorrow is None):
        return None
    elif df_today is None:
        df_combined = df_tomorrow
    elif df_tomorrow is None:
        df_combined = df_today
    else:
        df_combined  = df_tomorrow.combine_first(df_today)
    
    if verbosity > 3: print('Combined WP data:\n', df_combined)
    
    return df_combined


def read_36h_forecast_file(file_name, loc, verbosity=1):
    """Read the forecast for the given location from a single WP 36h data file.
    
    Parameters:
      file_name (str):  Name of the input file.
      loc (str):        Location to read data for.
      verbosity (int):  Verbosity (0-4 for silent to loud).
    
    Returns:
      (pandas.DataFrame):  Forecast data for the location provided.  None if no data were found.
    """
    
    in_file = open(file_name,'r')
    
    # Determine 'header', ie number of lines to skip, by reading every line and checking for the location name:
    n_header=0
    while n_header > -1:
        n_header += 1
        line = in_file.readline()
        
        if loc in line: break
        if n_header > 442:
            return None
        
    n_header += 2  # Skip the two header lines
    
    wp_data = _np.genfromtxt(file_name, skip_header=n_header, max_rows=36)  # Read the data
    
    
    # Convert Numpy array to Pandas dataframe:
    cols         = ['year','month','day','time', 'clouds', 'rain', 'temp', 'press', 'rh', 'ws', 'wd']
    time0        = wp_data[0,3]
    idx          = range(36)+time0  # Set the index to time in hours since midnight today
    wp_data[:,3] = idx              # Set time in hours since midnight today
    df           = _pd.DataFrame(data=wp_data, index=idx, columns=cols)
    
    # Add datetime column 'dtm' to df:
    df['hour'] = df.time % 24  # Clock time in hours (0-23)
    df['dtm'] = _pd.to_datetime(df[['year','month','day','hour']])  # Turn the columns in the df into a single datetime column
    del df['year'],df['month'],df['day'],df['hour']  # No longer needed
    df = df[['dtm'] + [x for x in df.columns if x != 'dtm']]  # Move datetime column to front
    
    # Convert "wind speed" (actually force) to proper wind speed in m/s:
    df.ws = 0.836 * _np.power(df.ws, 3/2)  # v = 0.836 B^(3/2) m/s - https://en.wikipedia.org/wiki/Beaufort_scale#History
    
    # Compute derived variables:
    df['wchil'] = _swtr.wind_chill_temperature(df.temp, df.ws)              # Wind chill (deg C)
    df['dp'] = _swtr.dew_point_from_tempc_rh(df.temp, df.rh/100)            # Dew point (deg C)
    df['ah'] = _swtr.absolute_humidity_from_tempc_rh(df.temp, df.rh/100)    # Absolute humidity (g/m^3)
    
    if verbosity > 4: print('Single-file WP data:\n', df)
    
    return df


def smoothen_36h_forecast_data(wpfc, verbosity=1):
    """Smoothen WP 36h forecast data.
    
    Parameters:
      wpfc (pd.df):     pandas.DataFrame containing WP forecast data.
      verbosity (int):  Verbosity (0-4 for silent to loud).
    
    Returns:
      (tuple):  tuple of three pd.dfs (wpfc,wpfci):
      
      - (pd.df): Pandas DataFrame containing WP forecast data.
      - (pd.df): Pandas DataFrame containing interpolated WP rain forecast data.
    """
    
    if verbosity > 0: print('Smoothening WP forecast...')
    if wpfc is None: return None,None  # Issue with WP data
    
    from scipy import interpolate as _ipol
    
    
    # ### WIND SPEED ###
    # Smoothen the predicted WP wind speed (coarse because it was force) with a fit:
    wpfc['ws_fit'] = None
    if wpfc.ws is not None:
        coefficients = _np.polyfit(wpfc.time, wpfc.ws, 11)   # 11-th degree fit
        polynomial = _np.poly1d(coefficients)                # polynomial contains the fit equation (try print(polynomial))
        wpfc.ws_fit = _np.maximum(polynomial(wpfc.time),0)   # Compute fit points for x; Wind speed shouldn't be negative
        
        wpfc.ws = wpfc.ws.round(1)
        
    # Use a spline interpolation to fit the WP predicted wind 'speed' instead:
    # spl_coefs = _ipol.splrep(wpfc.time, wpfc.ws)         # Compute the spline coefficients
    # wpfci['time'] = _np.arange(0,360)/10
    # wpfci['ws'] = _ipol.splev(wpfci['time'], spl_coefs)  # Do the spline interpolation
    # wpfci.ws[wpfci.ws<0] = 0                                   # Wind speed shouldn't be negative
    
    # Compute derived variables:
    wpfc['wchil'] = _swtr.wind_chill_temperature(wpfc.temp, wpfc.ws_fit)  # Wind chill (from smoothened wind speed)
    
    
    # ### RAIN ###
    # Use a spline interpolation for the predicted WP rain:
    wpfci = _pd.DataFrame()
    if wpfc is not None:
        spl_coefs = _ipol.splrep(wpfc.time, wpfc.rain)      # Compute the spline coefficients
        ipl_range = min(wpfc.time.iloc[-1]+1, 49)                 # 37-49 -> 36-48h
        wpfci['time'] = _np.arange(0,ipl_range*10+1)/10
        wpfci['rain'] = _ipol.splev(wpfci.time, spl_coefs)  # Do the spline interpolation
        wpfci.rain[wpfci.rain<0] = 0                              # Rain shouldn't be negative
    
    if verbosity > 2:
        print('Raw WP data:\n', wpfc)
        if verbosity > 3: print('Interpolated WP rain data:\n', wpfci)
    
    return wpfc, wpfci

