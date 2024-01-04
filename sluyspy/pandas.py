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


"""Pandas functions for the sluyspy package"""

import re as _re


def csv_formatted_from_df(df, file_name, fmt):
    """Write a Pandas DataFrame as a formatted csv file.
    
    Parameters:
      df (pd.df):       Pandas DataFrame to write to csv file.
      file_name (str):  Path to the output csv file (may be a Path).
      fmt (str):        C-style formatting string for values w/o newline; the header string will be adapted from this.
    """
    
    fmt += '\n'     # Add newline to value format string
    
    # Construct header format string from value format string:
    hdr_fmt = fmt
    hdr_fmt = _re.sub(r'\.[0-9]*[ifegIFEG]', r's', hdr_fmt)  # Dot + number(s) + ifeg/IFEG
    hdr_fmt = _re.sub(r'\.[0-9]*lf', r's', hdr_fmt)          # Dot + number(s) + lf/LF
    hdr_fmt = _re.sub(r'lf', r's', hdr_fmt)                  # lf
    hdr_fmt = _re.sub(r'LF', r's', hdr_fmt)                  # LF
    hdr_fmt = _re.sub(r'[dicfegDICFEG]', r's', hdr_fmt)      # Any remaining letters w/o numbers
    hdr_fmt = _re.sub(r'%0*', r'%', hdr_fmt)                 # Leading zeros
    
    outfile = open(file_name,'w')
    outfile.write(hdr_fmt % tuple(df.columns.values))  # Write column names as header
    
    for idx,ser in df.iterrows():  # Makes (index, Series) pairs out of rows
        outfile.write(fmt % tuple(ser.values))  # Write formatted row - needs '\n' for EoL
    outfile.close()
    
    return
