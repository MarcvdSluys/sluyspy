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


"""Command-line interface functions for the sluyspy package"""

import sys as _sys
from termcolor import colored as _clr


def dialog(text):
    """Present a dialog text and wait for a single-key answer.
    
    Parameters:
      text (str):  The text to print.
    
    Returns:
      (str):  The single character typed by the user.
    """
    
    import getch
    
    _sys.stdout.write(text+' ')  # No newline
    _sys.stdout.flush()          # Show the previous line
    
    char = getch.getche()  # Ask for user input, displayed on the screen
    print()                # Newline after input
    
    return char


def error(message, exit_program=True, exit_code=1):
    """Print a coloured error message to stderr and exit.
    
    Parameters:
      message (str):        Message to print.
      exit_program (bool):  Exit the program or not, defaults to True.
      exit_code (int):      Exit code to exit the program with, defaults to 1.
    """
    
    _sys.stderr.write('\n'+_clr('ERROR: '+str(message), 'white', 'on_red', attrs=['bold'])+'\n\n')
    
    if exit_program: exit(exit_code)
    return


def warn(message, exit_program=False, exit_code=1):
    """Print a coloured warn message to stderr and exit.
    
    Parameters:
      message (str):        Message to print.
      exit_program (bool):  Exit the program or not, defaults to False.
      exit_code (int):      Exit code to exit the program with, defaults to 1.
    """
    
    _sys.stderr.write('\n'+_clr('Warning: '+str(message), 'white', 'on_yellow', attrs=['bold'])+'\n\n')
    
    if exit_program: exit(exit_code)
    return
