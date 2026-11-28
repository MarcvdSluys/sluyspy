# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2026  Marc van der Sluys - Nikhef/Utrecht University - marc.vandersluys.nl
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


"""EMS (energy-management system/home battery) strategies-json functions for the sluyspy package.

This module locates and reads the output/strategies.json file under the EMS base dir and extracts the
expected price-valley ranges from it.  The EMS base dir comes from sluyspy.env (local
~/.python_environment.cfg).
"""

import json as _json
import pandas as _pd

from sluyspy import env as _senv


_STRATEGIES_REL = 'output/strategies.json'  # Strategies json, relative to the EMS base dir


def strategies_file(ems_dir=None):
    """Path of the EMS strategies json file.
    
    Args:
      ems_dir (str):  EMS base directory; if None, take ems_dir from sluyspy.env.environment().
    
    Returns:
      (str):  Full path of the strategies json file, <ems_dir>/output/strategies.json.
    """
    
    if ems_dir is None:
        ems_dir = _senv.environment().ems_dir
    return ems_dir + _STRATEGIES_REL


def read_strategies(file=None):
    """Read and parse the EMS strategies json file.
    
    Args:
      file (str):  Path of the strategies json file; if None, use strategies_file().
    
    Returns:
      (dict):  The parsed json with keys time, scen, horizons, backed, borders, windows, cycles.
    """
    
    if file is None:
        file = strategies_file()
    with open(file) as fh:
        return _json.load(fh)


def price_valleys(spec, now=None):
    """Extract the price valleys (charge regimes) from a strategies json spec: per valley its starting and
    ending border, the charge window inside it, and the charge horizon in it.
    
    Args:
      spec (dict):    Parsed strategies json as returned by read_strategies(); must contain the keys
                      'borders', 'windows' and 'horizons'.
      now (Timestamp):  optional; if given, only valleys that have not ended yet (valley_end > now) are
                      returned.
    
    Returns:
      (list):  Valley dicts sorted by valley_start:
               - day (str):               reference day, 'YYYY-MM-DD'
               - kind (str):              'night' or 'day'
               - valley_start (Timestamp):  starting border of the valley
               - valley_end (Timestamp):    ending border of the valley
               - charge_start (Timestamp):  start of the charge window in the valley (None if absent)
               - charge_end (Timestamp):    end of the charge window in the valley (None if absent)
               - horizon (Timestamp):       backed (else estimated) charge start in the valley, or None
    
    Raises:
      ValueError:  if `spec` has no 'borders', 'windows' or 'horizons' section.
    """
    
    for key in ('borders', 'windows', 'horizons'):
        if key not in spec:
            raise ValueError(f'price_valleys: spec has no {key!r} section (old strategies json?)')
    
    borders, windows = spec['borders'], spec['windows']
    horizons = [_pd.Timestamp(h) for h in spec['horizons']]
    backed   = [_pd.Timestamp(h) for h in spec.get('backed', [])]
    valleys = []
    
    for day in sorted(borders):
        b = borders[day]
        # Afternoon valley of `day`: morn_aftn -> aftn_eve:
        valleys.append(_valley(day, 'day', _pd.Timestamp(b['morn_aftn']), _pd.Timestamp(b['aftn_eve']),
                               windows.get(day, {}).get('day', {}).get('charge'), horizons, backed))
        # Night valley ending on `day`: the previous day's even_nght -> this day's nght_morn:
        prev = str(_pd.Timestamp(day) - _pd.Timedelta(days=1))[:10]
        if prev in borders:
            valleys.append(_valley(day, 'night', _pd.Timestamp(borders[prev]['even_nght']),
                                   _pd.Timestamp(b['nght_morn']),
                                   windows.get(day, {}).get('night', {}).get('charge'), horizons, backed))
    
    valleys.sort(key=lambda v: v['valley_start'])
    
    if now is not None:
        now = _pd.Timestamp(now)
        valleys = [v for v in valleys if v['valley_end'] > now]
    
    return valleys


def _valley(day, kind, v_start, v_end, charge_win, horizons, backed):
    """Build one price-valley dict for price_valleys().
    
    Args:
      day (str):         reference day, 'YYYY-MM-DD'.
      kind (str):        'night' or 'day'.
      v_start (Timestamp):  starting border of the valley.
      v_end (Timestamp):    ending border of the valley.
      charge_win (dict):    charge window {'start', 'end'} inside the valley, or None.
      horizons (list):      estimated charge starts (Timestamps).
      backed (list):        backed charge starts (Timestamps).
    
    Returns:
      (dict):  Valley dict with day, kind, valley_start/end, charge_start/end, horizon.
    """
    
    in_valley = [h for h in backed if v_start <= h <= v_end] or [h for h in horizons if v_start <= h <= v_end]
    
    return {'day': day, 'kind': kind,
            'valley_start': v_start, 'valley_end': v_end,
            'charge_start': _pd.Timestamp(charge_win['start']) if charge_win else None,
            'charge_end':   _pd.Timestamp(charge_win['end'])   if charge_win else None,
            'horizon': in_valley[0] if in_valley else None}
