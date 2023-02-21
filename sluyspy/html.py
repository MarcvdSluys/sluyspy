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


"""HTML functions for the sluyspy package."""

# from .cli import error as _error
import datetime as _dt


def start_html_file(file_name='index.html', lang='en', title='Page title', icon=None, css=None,
                    author='Marc van der Sluys', copyr_start=None, refresh=None, meta_prop=None):
    
    """Create an html file, write the head section and start the body.
    
    Parameters:
      file_name (str):    Name/path of the html file.
      lang (str):         Language.
      title (str):        Page title.
      icon (str):         Path to an icon file.
      css (str):          Path to a css file.
      author (str):       Author name.
      copyr_start (int):  Starting year of copyright.
      refresh (int):      Refresh period in seconds.
      meta_prop (dict):   Dict of meta properties.
    
    Returns:
      (FILE):  File descriptor.
    """
    
    f = open(file_name, 'w')
    
    f.write('<!DOCTYPE HTML>\n')
    f.write('<html lang="'+lang+'">\n')
    f.write('  <head>\n')
    f.write('    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">\n')
    if refresh is not None: f.write('    <meta content="'+str(refresh)+'; URL=." http-equiv="Refresh">\n')
    if icon is not None:    f.write('    <link rel="icon" href="'+icon+'">\n')
    if css is not None:     f.write('    <link rel="stylesheet" type="text/css" href="'+css+'">\n')
    f.write('    <title>'+title+'</title>\n')
    if author != '':
        current_year = _dt.date.today().year
        if (copyr_start is None) or (copyr_start == current_year):
            f.write('    <meta name="author" content="(c) '+str(current_year)+' '+author+'">\n')
        else:
            f.write('    <meta name="author" content="(c) '+str(copyr_start)+'-'+str(current_year)+' '+author+'">\n')
            
    f.write('  </head>\n')
    f.write('  <body>\n')
    
    return f


if __name__ == '__main__':
    pass
