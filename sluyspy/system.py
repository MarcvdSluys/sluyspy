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
    """
    
    import subprocess
    subprocess.run(['tail -'+str(num_lines)+' '+in_file+' > '+out_file], stdout=subprocess.PIPE,
                   shell=True, check=True).stdout.decode('utf-8')
    
    return


def string_in_file(infile, string):
    """Use the grep command in a shell to quickly check whether a file contains a string.
    
    Parameters:
      infile (str):  Name of the file.
      string (str):  Match string.
    
    Note: fast small files (<~1Mb) and/or few calls (<~100kb).
    """
    
    with open(infile) as f:
        if string in f.read():
            return True
        else:
            return False
    
    return None


def string_in_file_grep(infile, string):
    """Use the grep command in a shell to quickly check whether a file contains a string.
    
    Parameters:
      infile (str):  Name of the file.
      string (str):  Match string.
    
    Note: fast for large files (>~1Mb) and/or multiple calls (>~100kb).
    """
    
    import subprocess
    try:
        subprocess.run(['grep -c '+string+' '+infile], stdout=subprocess.PIPE,
                       shell=True, check=True).stdout.decode('utf-8')
        # Check=false: do not raise an error if string is not found (but return 0)
        result = True  # result = int(count) > 0
        
    except subprocess.CalledProcessError as e:
        result = None
        if e.returncode == 1:  # Exit status: 0: line found, 1: no line found, 2: error
            # count = e.output.decode('utf-8')
            # result = int(count) > 0
            result = False
        else:
            import sluyspy.cli as scli
            scli.warn('string_in_file(): an error occurred when calling grep')
            result = None
    
    return result


