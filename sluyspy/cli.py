# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022  Marc van der Sluys - marc.vandersluys.nl
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


"""Command-line interface functions for the sluyspy package"""


def dialog(text):
    """Present a dialog text and wait for a single-key answer.

    Parameters:
      text (str):  The text to print.

    Returns:
      (str):  The single character typed by the user.
    """
    
    import sys
    import getch
    
    sys.stdout.write(text+' ')  # No newline
    sys.stdout.flush()          # Show the previous line
    
    char = getch.getche()  # Ask for user input, displayed on the screen
    print()                # Newline after input
    
    return char
