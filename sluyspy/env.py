#!/bin/env python
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


"""Environment functions for the sluyspy package."""


from dataclasses import dataclass as _dataclass

from sluyspy import sys


@_dataclass
class Environment:
    host:     str  = None;  """Host name"""
    home:     str  = None;  """Home directory"""
    on_zotac: bool = None;  """Am I on Zotac?"""
    on_think: bool = None;  """Am I on Think?"""
    
    sp_dir: str = None;  """Solar-panel directory"""
    el_dir: str = None;  """Electricity-meter directory"""
    
    
def environment(cfg_file='.python_environment.cfg'):
    """Return my computing environment.
    
    Parameters:
      cfg_file (str):  Configuration file to read system environment from (relative to home directory).
    
    Returns:
      (Environment):  Dataclass containing the environment settings.
    """
    
    env = Environment()
    env.host = sys.host()
    env.home = sys.homedir()
    
    env.on_zotac = env.host == 'zotac'
    env.on_think = env.host == 'think'
    
    
    # Read system config file:
    import configparser
    config = configparser.ConfigParser()
    config.read(env.home+'/'+cfg_file)
    
    # Section SolarPanels:
    env.sp_dir = config.get('SolarPanels', 'basedir').replace('~', env.home)  # SP base dir
    
    # Section ElectricityMeter:
    env.el_dir = config.get('ElectricityMeter', 'basedir').replace('~', env.home)  # EM base dir
    
    return env


if __name__ == '__main__':
    print(environment())
