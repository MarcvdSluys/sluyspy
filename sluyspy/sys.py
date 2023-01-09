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


"""System functions for the sluyspy package."""


from pathlib import Path as _Path
import socket as _socket


def host():
    """Return the current host name.
    
    Returns:  
      (str):  The current host name.
    """
    
    return _socket.gethostname()


def homedir():
    """Return my home directory as a string without trailing slash.
    
    Returns:  
      (str):  My home directory as a string without trailing slash.
    """
    
    return str(_Path.home())


def on_zotac():
    """Tell whether I am on a host called zotac.
    
    Returns:
      (bool):  True when I am on a host called zotac, False otherwise.
    """
    
    return host() == 'zotac'

