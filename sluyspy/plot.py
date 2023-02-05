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


"""Plot functions for the sluyspy package."""

import matplotlib.pyplot as _plt         # Get matplotlib.pyplot


def show_ctrlc():
    """Call pyplot.show() and catch Ctrl-C to exit gently."""
    
    try:
        _plt.show()
    except KeyboardInterrupt:
        print(' - Received keyboard interrupt, aborting.')  # " - " to create some space after "^C"
        exit(0)
        
    return


def pause_ctrlc(interval):
    """Call pyplot.pause() and catch Ctrl-C to exit gently.
    
    Parameters:
      interval (float):  pause time in seconds.
    """
    
    try:
        _plt.pause(interval)
    except KeyboardInterrupt:
        print(' - Received keyboard interrupt, aborting.')  # " - " to create some space after "^C"
        exit(0)
        
    return
