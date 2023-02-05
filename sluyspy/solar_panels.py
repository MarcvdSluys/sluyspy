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


"""Solar-panel functions for the sluyspy package"""


import pandas as _pd
import pytz as _tz
import solarenergy as se
from sluyspy import env as _env

# My computing environment:
env = _env.environment()

# My solar-panel specs:
sp = se.read_solar_panel_specs()


def read_detailed_log(file_name='Current/detailed-log.csv', last_only=None, header=None, sun_position=False, rem_cols=True, no_p0rows=False, no_elec=False, no_cond=True):
    """Read solar-panel detailed-log.csv and select the useful data.
    
    Parameters:
      file_name (str):      Name of the input file (optional; default=None -> detailed-log.csv).
      header (int):         Number of lines to consider as header and skip (optional; default: 0).
      last_only (int):      Number of last lines to read.  This tails the last lines into a separate file and reads that.
      sun_position (bool):  Add (compute) Sun position to the data (slow! - optional; default: False).
      rem_cols (bool):      Remove default columns (constants, duplicates, uninteresting).
      no_p0rows (bool):     Remove rows without power (P=0; Relay=closed; Cond!=OK).
      no_elec (bool):       Remove electricity details (some P,V,I, f).
      no_cond (bool):       Remove condition/status columns (Cond, Relay, Tinv).
      
    Returns:
      (pandas.DataFrame):  DataFrame containing solar-panel data.
    """
    
    col_names = ['date', 'time', 'SN1', 'Type', 'SN2', 'Pdc', 'x0', 'Idc', 'x1', 'Vdc', 'x2', 'Pac', 'x3', 'x4', 'Iac', 'x5', 'x6', 'Vac',
                 'x7', 'x8', 'Pdc2', 'Pac2', 'x9', 'Eday', 'Etot', 'Freq', 't_oper', 't_feedin', 'Btooth', 'Cond', 'Relay', 'Tinv']
    
    # Issue: detailed-log.csv becomes very long -> reading is slow.  Tail the last 3000 lines/minutes (2+
    # days) to a shorter file and read that (currently saves a factor 17 on CPU time (2022-11-12)):
    if last_only is not None:
        from pathlib import Path
        import sluyspy.sys as ssys
        
        tmpfile = ssys.temp_file_name(env.sp_dir+'Current',  '.detailed-log-last', 'csv')
        
        ssys.tail_file(env.sp_dir+file_name, tmpfile, last_only)  # Copy last last_only lines to tmpfile
        df = _pd.read_csv(tmpfile, header=header, sep=r'\s*,\s*', engine='python', names=col_names)
        
        Path.unlink(tmpfile)  # Remove temporary file
        
    else:
        df = _pd.read_csv(env.sp_dir+file_name, header=header, sep=r'\s*,\s*', engine='python', names=col_names)
    
    # Remove unwanted columns:
    if rem_cols:
        del df['SN1'], df['SN2'], df['Type']  # Not interesting - constant
        del df['Pdc2'], df['Pac2']            # Not interesting - duplicates
        del df['x0'], df['x1'], df['x2'], df['x3'], df['x4'], df['x5'], df['x6'], df['x7'], df['x8'], df['x9']  # x_i are always 0
        
        del df['Eday'], df['t_oper'], df['t_feedin'], df['Btooth']  # Not interested in now  # , df['Etot']
        
    
    # Remove rows witout power (P=0; Relay=closed; Cond!=OK):
    if no_p0rows:
        df = df[df['Relay'] == 'Closed']  # Only keep data when the relay is closed (i.e., providing a current/energy)
        df = df[df['Cond']  == 'Ok']      # Only keep data when the condition is 'OK'
        df = df[df['Pdc']  > 0]           # Only keep data if there is power
        df = df[df['Pac']  > 0]           # Only keep data if there is power
        
        # df = df[df['Pac']  < 2990]        # Only keep data for P < 3kW, since 3kW may indicate >3kW
        # df = df[df['Tinv'] > 0]           # Only keep data if we have a temperature (of the inverter!)
        
        # No longer needed:
        del df['Relay'], df['Cond'], df['Tinv']
        
    elif no_cond:
        del df['Cond'], df['Relay'], df['Tinv']
    
    # Slightly more accurate: ~3-4 significant digits -> 4-5:
    df['Pdc'] = df['Idc'] * df['Vdc']
    df['Pac'] = df['Iac'] * df['Vac']
    
    if no_elec:
        del df['Pdc'], df['Idc'], df['Vdc'], df['Iac'], df['Vac'], df['Freq']

    
    
    # Combine date and time columns to a timezone-aware datetime:
    df['date'] = _pd.DatetimeIndex(_pd.to_datetime(df['date']+' '+df['time']))
    df = df.rename(columns={'date': 'dtm'})  # Rename column date -> dtm
    # df['dtm'] = df['dtm'].dt.round('min')
    mytz = _tz.timezone(sp.tz)
    df.dtm = df.dtm.dt.tz_localize(mytz)  # Timezone naive -> timezone aware.  Indicate that the existing times are in mytz, without conversion.
    
    del df['time']  # Remove column 'time'
    
    # print(df['dtm'])
    
    # Compute Sun position (uses SolTrack behind the scenes):
    if sun_position:
        df['sunAz'],df['sunAlt'],df['sunDist'] = \
            se.sun_position_from_datetime(sp.geo_lon,sp.geo_lat, df['dtm'])
        
    return df


def write_day_file(df, subdir='', prefix=sp.name, ext='csv', verbosity=0):
    """Write one day of (e.g.) minutely solar-panel data to daily file named 'subdir/prefix-yyyymmdd.ext'.
    
    Parameters:
      df (pandas.DataFrame):  Pandas DataFrame with columns datetime, Pac and Etot.
      subdir (str):           Subdirectory to save file in, with trailing slash.
      prefix (str):           File name prefix (defaults to name of the plant, followed by a hyphen).
      ext (str):              File extension to use.
      verbosity (int):        Verbosity (0-2; defaults to 0).
    """
    
    if len(df) < 1:
        if verbosity > 0:  print('No data available, no file created.')
        return
    
    
    # Want separate date and time columns:
    df['date'] = df.dtm.dt.date
    df['time'] = df.dtm.dt.time
    
    date = df.loc[:, 'dtm'].dt.date.iloc[0].strftime('%Y%m%d')  # .loc[0, ''] doesn't work, since row 0 does not exist
    out_file_name = env.sp_dir+subdir+prefix+'-'+date+'.'+ext
    if verbosity > 0:  print('Saving data to '+out_file_name)
        
    # Open file and write header:
    out_file = open(out_file_name, 'w')
    out_file.write('sep=;\n')
    out_file.write('Version CSV1|Tool SBFspot3.3.1 (Linux)|Linebreaks CR/LF|Delimiter semicolon|Decimalpoint dot|Precision 3\n')
    out_file.write('\n')
    out_file.write(';SN: '+sp.inv_sn+';SN: '+sp.inv_sn+'\n')
    out_file.write(';'+sp.inv_model+';'+sp.inv_model+'\n')
    out_file.write(';'+sp.inv_sn+';'+sp.inv_sn+'\n')
    out_file.write(';Total yield;Power\n')
    out_file.write(';Counter;Analog\n')
    out_file.write('yyyy-MM-dd;HH:mm:ss;kWh;kW\n')
    
    for row in df.iterrows():
        ser = row[1]
        if verbosity > 1:  print('%s;%s;%0.3f;%5.3f' % (ser.date, ser.time, ser.Etot, ser.Pac))
        
        out_file.write('%s;%s;%0.3f;%5.3f\n' % (ser.date, ser.time, ser.Etot, ser.Pac/1e3))  # Pac: W -> kW
        
    out_file.close()
    
    return    

    
