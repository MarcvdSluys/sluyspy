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


"""Text functions for the sluyspy package"""


def wrap_line(line, wlen, indent=2):
    """Wrap a line at the last space before a specified length.
    
    NOTE: this goes WRONG for if words longer than wlen are present.
    
    Parameters:
      line (str):    Line to wrap.
      wlen (int):    Maximum line length to wrap at.
      indent (int):  Indentation of the continuation line
    
    Returns:
      (str):  The line with extra '\n' characters.
    """
    
    llen = len(line)
    
    # No need to break:
    if wlen >= llen: return line
    
    i0 = 0     # Base position
    il = wlen  # Move between i0 and i0+wlen
    dl = -1    # Move backwards by default
    wraps = 0
    
    while True:
        # print(i0+il,llen)
        if line[i0+il]==' ':
            wraps += 1
            line = line[0:i0+il]+'\n'+' '*indent+line[i0+il+1:]  # Remove the space and add an indentation of <indent> spaces
            i0 = i0+il+indent
            il = wlen
            
            # print(wraps,wlen,llen,wraps*wlen,len(line),il,i0+il, line)
            if i0+il >= len(line): break
            dl = -1  # Search backward by default
            continue
        
        il += dl
        if i0+il > llen: break
        
        # print('i0,il,i0+il,dl:" ', i0,il,i0+il,dl)
        if il==indent-1:
            i0 += wlen
            dl = +1  # Start searching forward
            continue
        
    return line
