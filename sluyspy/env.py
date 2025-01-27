#!/bin/env python
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


"""Environment functions for the sluyspy package."""


from dataclasses import dataclass as _dataclass

from sluyspy import system as _ssys
import astroconst as _ac


@_dataclass
class Environment:
    tz:              str  = '';     """Time zone"""
    geo_lon:         float = 0.0;   """Geographical longitude in radians east of Greenwich"""
    geo_lat:         float = 0.0;   """Geographical latitude in radians north of the equator"""
    geo_alt:         float = 0.0;   """Geographical altitude in metres above sea level"""
    
    host:            str  = '';     """Host name"""
    home:            str  = '';     """Home directory"""
    on_think:        bool = False;  """Am I on Think?"""
    on_zotac:        bool = False;  """Am I on Zotac?"""
    on_hwc:          bool = False;  """Am I on HWC?"""
    
    sp_dir:          str = '';      """Solar-panel directory"""
    el_dir:          str = '';      """Electricity-meter directory"""
    
    knmi_10min_dir:  str = '';      """Directory for 10-min KNMI data"""
    knmi_hourly_dir: str = '';      """Directory for hourly KNMI data"""
    knmi_daily_dir:  str = '';      """Directory for daily KNMI data"""
    wpw_dir:         str = '';      """WP weather directory"""
    
    thesky_dir:      str = '';      """TheSky main directory"""
    hwc_dir:         str = '';      """HWC main directory"""
    
    
def environment(cfg_file='.python_environment.cfg'):
    """Return my computing environment.
    
    Parameters:
      cfg_file (str):  Configuration file to read system environment from (relative to home directory).
    
    Returns:
      (Environment):  Dataclass containing the environment settings.
    """
    
    env = Environment()
    env.host = _ssys.host()
    env.home = _ssys.homedir()
    
    env.on_think = env.host == 'think'
    env.on_zotac = env.host == 'zotac'
    env.on_hwc   = env.host == 'hwc'
    
    # Read system config file:
    import configparser
    config = configparser.ConfigParser(inline_comment_prefixes=('#'))
    config.read(env.home+'/'+cfg_file)
    
    # Section Localisation:
    env.tz      = config.get('Localisation', 'timezone',  fallback=env.tz)       # My timezone
    env.geo_lon = config.getfloat('Localisation', 'longitude', fallback=env.geo_lon)  # My longitude
    env.geo_lat = config.getfloat('Localisation', 'latitude',  fallback=env.geo_lat)  # My latitude
    env.geo_alt = config.getfloat('Localisation', 'altitude',  fallback=env.geo_alt)  # My altitude
    
    env.geo_lon *= _ac.d2r  # Convert from degrees to radians
    env.geo_lat *= _ac.d2r
    
    # Section SolarPanels:
    env.sp_dir = config.get('SolarPanels', 'basedir', fallback=env.sp_dir).replace('~', env.home)  # SP base dir
    
    # Section ElectricityMeter:
    env.el_dir = config.get('ElectricityMeter', 'basedir', fallback=env.el_dir).replace('~', env.home)  # EM base dir
    
    # Section Weather:
    env.knmi_10min_dir  = config.get('Weather', 'knmi_10min_dir',  fallback=env.knmi_10min_dir).replace('~',  env.home)  # KNMI 10-min dir
    env.knmi_hourly_dir = config.get('Weather', 'knmi_hourly_dir', fallback=env.knmi_hourly_dir).replace('~', env.home)  # KNMI hourly dir
    env.knmi_daily_dir  = config.get('Weather', 'knmi_daily_dir',  fallback=env.knmi_daily_dir).replace('~', env.home)   # KNMI daily dir
    env.wpw_dir         = config.get('Weather', 'wpw_dir',         fallback=env.wpw_dir).replace('~', env.home)          # WP weather dir
    
    # Section HWC:
    env.thesky_dir      = config.get('HWC', 'thesky_dir',          fallback=env.thesky_dir).replace('~', env.home)       # TheSky main dir
    env.hwc_dir         = config.get('HWC', 'hwc_dir',             fallback=env.hwc_dir).replace('~', env.home)          # HWC main dir
    
    return env


if __name__ == '__main__':
    print(environment())
