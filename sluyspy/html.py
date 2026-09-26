# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2026  Marc van der Sluys - Nikhef/Utrecht University - marc.vandersluys.nl
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


def line(fd, indent, code):
    """Write a line of html code with given indentation to a given file descriptor.
    
    Parameters:
      fd (float):    File descriptor.
      indent (int):  Indentation (number of spaces).
      code (float):  HTML code to write.
    """
    
    fd.write(' '*indent + code +'\n')
    
    return


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
    fd = open(file_name, 'w')
    line(fd, 0, '<!DOCTYPE HTML>')
    line(fd, 0, '<html lang="'+lang+'">')
    
    # Write the <head> section:
    line(fd, 2, '<head>')
    line(fd, 4, '<meta http-equiv="Content-Type" content="text/html;charset=utf-8">')
    
    # Add refresh data if desired:
    if refresh is not None:
        line(fd, 4, '<meta http-equiv="Refresh" content="'+str(refresh*60)+'">')
        
    # Add an icon or css if desired:
    if icon is not None:    line(fd, 4, '<link rel="icon" href="'+icon+'">')
    if css is not None:     line(fd, 4, '<link rel="stylesheet" type="text/css" href="'+css+'">')
    
    # Add a title:
    line(fd, 4, '<title>'+title+'</title>')
    
    # Add an author and copyright if desired:
    if author != '':
        current_year = _dt.date.today().year
        if (copyr_start is None) or (str(copyr_start) == str(current_year)):
            line(fd, 4, '<meta name="author" content="(c) '+str(current_year)+' '+author+'">')
        else:
            line(fd, 4, '<meta name="author" content="(c) '+str(copyr_start)+'-'+str(current_year)+' '+author+'">')
    
    # Add meta data if any:
    if meta_prop is not None:
        for key,value in meta_prop.items():
            line(fd, 4, '<meta property="'+key+'" content="'+value+'">')
    
    # Close the <head> section and start the <body> section:
    line(fd, 2, '</head>')
    line(fd, 2, '')
    line(fd, 2, '<body>')
    
    return fd


def close_html_file(fd, sc_id=None, sc_secr=None, sc_name=None):
    """Close an html file by writing StatCounter code if desired, and closing <body>, <html> and the file.
    
    Parameters:
      fd (io):        File descriptor.
      sc_id (int):    StatCounter project ID.
      sc_secr (str):  StatCounter security secret.
      sc_name (str):  Name for the StatCounter code block.
    """
    
    # Create some space:
    line(fd, 4, '')
    line(fd, 4, '')
    
    
    # Write a StatCounter code block if desired:
    if (sc_id is not None) and (sc_secr is not None):
        if sc_name is not None:
            line(fd, 4, '<!-- Start of StatCounter Code for '+sc_name+' -->')
        else:
            line(fd, 4, '<!-- Start of StatCounter Code -->')
        
        line(fd, 4, '<script type="text/javascript">')
        line(fd, 4, 'var sc_project='+str(sc_id)+'; ')
        line(fd, 4, 'var sc_invisible=1; ')
        line(fd, 4, 'var sc_security="'+str(sc_secr)+'"; ')
        line(fd, 4, 'var scJsHost = (("https:" == document.location.protocol) ?')
        line(fd, 4, '"https://secure." : "http://www.");')
        line(fd, 4, 'document.write("<sc"+"ript type=''text/javascript'' src=''" +')
        line(fd, 4, 'scJsHost+')
        line(fd, 4, '"statcounter.com/counter/counter.js''></"+"script>");')
        line(fd, 4, '</script>')
        line(fd, 4, '<noscript><div class="statcounter"><a title="web analytics"')
        line(fd, 4, 'href="http://statcounter.com/" target="_blank"><img')
        line(fd, 4, 'class="statcounter"')
        line(fd, 4, 'src="//c.statcounter.com/'+str(sc_id)+'/0/'+str(sc_secr)+'/1/" alt="web')
        line(fd, 4, 'analytics"></a></div></noscript>')
        if sc_name is not None:
            line(fd, 4, '<!-- End of StatCounter Code for '+sc_name+' -->')
        else:
            line(fd, 4, '<!-- End of StatCounter Code -->')
        
        line(fd, 4, '')
        line(fd, 4, '')
    
    
    # Close the <body> and <html> sections:
    line(fd, 2, '</body>')
    line(fd, 0, '</html>')
    
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


def last_update(fd, dtm=None, indent=4, size='65%', seconds=False, tz=False):
    """Add a 'Last update' line to an html file with the current system date and time.
    
    Parameters:
      fd (io):         File descriptor.
      dtm (float):     Date/time to print (can be e.g. UNIX time or time.time());  Optional, defaults to "now".
      indent (int):    Number of spaces for indentation.
      size (str):      String with font size, e.g. '100%'.
      seconds (bool):  Print seconds in timestamp.
      tz (bool):       Print time zone in timestamp.
    """
    
    import time
    if dtm is None: dtm = time.time()
    
    if seconds:
        time_str = _dt.datetime.fromtimestamp(dtm).strftime('%a %Y-%m-%d %H:%M:%S')
    else:
        time_str = _dt.datetime.fromtimestamp(dtm).strftime('%a %Y-%m-%d %H:%M')
    
    if tz:
        time_str += ' ' + time.tzname[time.localtime().tm_isdst]  # Add current tz, accounting for DST
    
    line(fd, indent, '<br>')
    line(fd, indent, '<p style="font-size:'+size+'; text-align:center; margin:0;">Last update: '+time_str+'</p>')
    line(fd, indent, '')
    
    return


if __name__ == '__main__':
    pass
