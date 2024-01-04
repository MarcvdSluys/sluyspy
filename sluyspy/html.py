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
      refresh (int):      Refresh period in minutes.
      meta_prop (dict):   Dict of meta data with the keys containing properties and the values
                          their content.
    
    Returns:
      (io):  File descriptor.
    """
    
    # Create the HTML file:
    f = open(file_name, 'w')
    
    f.write('<!DOCTYPE HTML>\n')
    f.write('<html lang="'+lang+'">\n')
    
    # Write the <head> section:
    f.write('  <head>\n')
    f.write('    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">\n')
    
    # Add refresh data if desired:
    if refresh is not None:
        f.write('    <meta http-equiv="Refresh" content="'+str(refresh*60)+'">\n')
        
    # Add an icon or css if desired:
    if icon is not None:    f.write('    <link rel="icon" href="'+icon+'">\n')
    if css is not None:     f.write('    <link rel="stylesheet" type="text/css" href="'+css+'">\n')
    
    # Add a title:
    f.write('    <title>'+title+'</title>\n')
    
    # Add an author and copyright if desired:
    if author != '':
        current_year = _dt.date.today().year
        if (copyr_start is None) or (copyr_start == current_year):
            f.write('    <meta name="author" content="(c) '+str(current_year)+' '+author+'">\n')
        else:
            f.write('    <meta name="author" content="(c) '+str(copyr_start)+'-'+str(current_year)+' '+author+'">\n')
    
    # Add meta data if any:
    if meta_prop is not None:
        for key,value in meta_prop.items():
            f.write('    <meta property="'+key+'" content="'+value+'">\n')
    
    # Close the <head> section and start the <body> section:
    f.write('  </head>\n')
    f.write('  \n')
    f.write('  <body>\n')
    
    return f


def close_html_file(fd, sc_id=None, sc_secr=None, sc_name=None):
    """Close an html file by writing StatCounter code if desired, and closing <body>, <html> and the file.
    
    Parameters:
      fd (io):        File descriptor.
      sc_id (int):    StatCounter project ID.
      sc_secr (str):  StatCounter security secret.
      sc_name (str):  Name for the StatCounter code block.
    """
    
    # Create some space:
    fd.write('    \n')
    fd.write('    \n')
    
    
    # Write a StatCounter code block if desired:
    if (sc_id is not None) and (sc_secr is not None):
        if sc_name is not None:
            fd.write('    <!-- Start of StatCounter Code for '+sc_name+' -->\n')
        else:
            fd.write('    <!-- Start of StatCounter Code -->\n')
        
        fd.write('    <script type="text/javascript">\n')
        fd.write('    var sc_project='+str(sc_id)+'; \n')
        fd.write('    var sc_invisible=1; \n')
        fd.write('    var sc_security="'+str(sc_secr)+'"; \n')
        fd.write('    var scJsHost = (("https:" == document.location.protocol) ?\n')
        fd.write('    "https://secure." : "http://www.");\n')
        fd.write('    document.write("<sc"+"ript type=''text/javascript'' src=''" +\n')
        fd.write('    scJsHost+\n')
        fd.write('    "statcounter.com/counter/counter.js''></"+"script>");\n')
        fd.write('    </script>\n')
        fd.write('    <noscript><div class="statcounter"><a title="web analytics"\n')
        fd.write('    href="http://statcounter.com/" target="_blank"><img\n')
        fd.write('    class="statcounter"\n')
        fd.write('    src="//c.statcounter.com/'+str(sc_id)+'/0/'+str(sc_secr)+'/1/" alt="web\n')
        fd.write('    analytics"></a></div></noscript>\n')
        if sc_name is not None:
            fd.write('    <!-- End of StatCounter Code for '+sc_name+' -->\n')
        else:
            fd.write('    <!-- End of StatCounter Code -->\n')
        
        fd.write('    \n')
        fd.write('    \n')
    
    
    # Close the <body> and <html> sections:
    fd.write('  </body>\n')
    fd.write('</html>\n')
    
    # Close the file:
    fd.close()
    
    return


def table_td_tr(indent, td_width, td_extra_width):
    """Define trtd, tdtd and tdtr elements for an html table.
    
    Parameters:
      indent (int):          Number of spaces for indentation.
      td_width (str):        Width of empty column between columns (e.g. '1%').
      td_extra_width (str):  Width of extra-wide empty column between columns (e.g. '10%').
    
    Returns:
      (tuple):  tuple containing trtd, tdtd, tdtdw, tdtr:
    
      - trtd (str):    the <tr><td> element.
      - tdtd (str):    the default </td><td> element.
      - tdtdw (str):   the extra-wide </td><td> element.
      - tdbrtd (str):  an empty </td><td> element for an empty row (<br>).
      - tdtr (str):    the </td></tr> element.
    """
    
    trtd    = ' '*indent + '<tr><td>'
    tdtd    = ' '*indent + '</td><td width="' + td_width       + '"></td><td>'
    tdtdw   = ' '*indent + '</td><td width="' + td_extra_width + '"></td><td>'
    tdbrtd  = ' '*indent + '</td><td width="' + td_width       + '"><br></td><td>'
    tdtr    = ' '*indent + '</td></tr>\n'
    
    return trtd, tdtd, tdtdw, tdbrtd, tdtr


def last_update(fd, indent, size='65%', seconds=False, tz=False):
    """Add a 'Last update' line to an html file with the current system date and time.
    
    Parameters:
      fd (io):         File descriptor.
      indent (int):    Number of spaces for indentation.
      size (str):      String with font size, e.g. '100%'.
      seconds (bool):  Print seconds in timestamp.
      tz (bool):       Print time zone in timestamp.
    """
    
    import time
    if seconds:
        time_str = _dt.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    else:
        time_str = _dt.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M')
    
    if tz:
        time_str += ' ' + time.tzname[time.localtime().tm_isdst]  # Add current tz, accounting for DST
    
    fd.write(' '*indent + '<br>\n')
    fd.write(' '*indent + '<p style="font-size:'+size+'; text-align:center; margin:0;">Last update: '+time_str+'</p>\n')
    fd.write(' '*indent + '\n')
    return


if __name__ == '__main__':
    pass
