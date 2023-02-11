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


def temp_file_name(dir_name=None, base_name='.tmpfile', ext='tmp'):
    """Return a temporary file name, using the system clock, like "dir/file_YYYYMMDD-HHMMSS.mmmmmm.ext".
    
    Parameters:
      dir_name (str):   Name of the directory for the file to be in.  Use homedir if None.
      base_name (str):  Base name of the file.
      ext (str):        File extension.
    
    Returns:
      (str):  A temporary file name.
    
    Note:
      - microsecond accuracy should suffice; two subsequent calls on my laptop take ~15-20us.
    """
    
    import datetime as dt
    
    if dir_name is None:  dir_name = homedir()
    
    return dt.datetime.now().strftime(dir_name+'/'+base_name+'_%Y%m%d-%H%M%S.%f.'+ext)  # Date and time with microseconds
    

def tail_file(in_file, out_file, num_lines):
    """Use the tail command in a shell to quickly save the last N lines of a file in a new file.
    
    Parameters:
      in_file (str):    Name of the input file.
      out_file (str):   Name of the output file.
      num_lines (int):  Number of lines to save.
      verbose (bool):   Print the result of the tail call in the shell.
    """
    
    import subprocess
    subprocess.run(['tail -'+str(num_lines)+' '+in_file+' > '+out_file], stdout=subprocess.PIPE,
                   shell=True, check=True).stdout.decode('utf-8')
    
    return
