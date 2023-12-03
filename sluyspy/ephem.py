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


"""Ephemerides functions for the sluyspy package"""


import pandas as _pd
from astroquery.jplhorizons import Horizons as _Horizons


def horizons_ephem(obj, jd, loc='500@399'):
    """Return a Pandas DataFrame with ephemerides from the NASA JPL Horizons system, with my selection of
    variables and column names.
    
    Parameters:
      obj (str):   Object using Horizons definitions e.g. 199-899 for the centres of the planets 1-8.
      jd (float):  Julian day for ephemerides.
      loc (str):   Horizons string for observer location.  Optional, defaults to '500@399' == Geocentre.
    
    Returns:
      (pd.df):  Pandas DataFrame containing planet ephemerides data.
    """
    
    # hz = _Horizons(id='Ceres', location='568', epochs={'start':'2010-01-01', 'stop':'2010-01-10', 'step':'1d'})
    hz = _Horizons(id=obj, location=loc, epochs=jd)  # Return only quantities of interest
    
    eph = hz.ephemerides(quantities='30, 18,19, 31,20,39, 1,2,36, 43,10,11,9', extra_precision=True)  # 45 gives error?
    # optional_settings={'suppress_range_rate':'yes'})
    # optional_settings: dict, optional: key-value based dictionary to inject some additional optional settings See https://ssd.jpl.nasa.gov/horizons/app.html; default: empty
    
    # print(eph.columns)
    # print(eph)
    
    # Convert astropy Table to Pandas DataFrame:
    df = eph.to_pandas()
    
    # Drop unwanted columns:
    df = df.drop(['targetname','solar_presence','flags','r_rate','delta_rate','r_3sigma','r_rate_3sigma','RA_3sigma','DEC_3sigma','PABLon','PABLat','surfbright'], axis=1)
    
    # Rename columns:
    df = df.rename(columns={'datetime_str':'dtm','datetime_jd':'jd','TDB-UT':'deltat','EclLon':'hc_lon','EclLat':'hc_lat','r':'hc_rad','ObsEclLon':'gc_lon','ObsEclLat':'gc_lat','delta':'gc_rad','RA':'ra','DEC':'dec','RA_app':'ra_app','DEC_app':'dec_app','alpha_true':'phang','illumination':'illum','illum_defect':'illum_def','V':'mag'})  # Rename columns
    
    # Convert datetime to datetime:
    df.dtm = _pd.to_datetime(df.dtm)
    # print(df)
    
    return df
