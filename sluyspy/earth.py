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


"""Functions for the sluyspy package to do with the Earth"""


import numpy as _np
import astroconst as _ac
import sluyspy.numerics as _snum


def distance(lon1,lat1, lon2,lat2, miles=False):
    """Compute the distance between two points over the Earth's surface.
    
    Parameters:
      lon1 (float):  Longitude of first location (rad).
      lat1 (float):  Latitude of first location (rad).
      lon2 (float):  Longitude of second location (rad).
      lat2 (float):  Latitude of second location (rad).
      miles (bool):  Return result in miles rather than kilometres.  Optional; defaults to False.
    
    Returns:
      (float):  Distance in kilometres (or miles, if desired).
    """
    
    r_e  = _ac.earth_r*1e-3                # Earth's radius in km
    fl   = 0.003352810665                  # Earth's flattening
    
    mlat  = (lat1+lat2)/2
    dlat2 = (lat1-lat2)/2
    dlon2 = (lon1-lon2)/2
    
    sins = _np.sin(dlat2)**2 * _np.cos(dlon2)**2 + _np.cos(mlat)**2 * _np.sin(dlon2)**2
    coss = _np.cos(dlat2)**2 * _np.cos(dlon2)**2 + _np.sin(mlat)**2 * _np.sin(dlon2)**2
    rat  = _np.arctan2(_np.sqrt(sins), _np.sqrt(coss))
    
    r = _np.sqrt(sins*coss)/(rat + _snum.tiny)  # Prevent division by zero - good idea?
    dist = 2 * r_e * rat
    
    h1 = (3*r-1) / (2*coss + _snum.tiny)
    h2 = (3*r+1) / (2*sins + _snum.tiny)
    
    distance = dist*(1  +  fl*h1*_np.sin(mlat)**2 * _np.cos(dlat2)**2  -  fl*h2*_np.cos(mlat)**2 * _np.sin(dlat2)**2)
    if miles: distance = distance * 0.62137119  # Miles rather than km - this is just one of the many definitions of a mile!
    
    return distance


def effective_radius_from_latitude(lat):
    """Compute the effective radius of the Earth from the latitude.
    
    Parameters:
      lat (float):  geographical latitude (radians).
    
    Returns:
      (float):  effective radius of the Earth (metres).
    """
    
    abslat = _np.abs(lat)
    
    Reff = 2 * 9.780356*(1+0.0052885*_np.square(_np.sin(abslat)) - 0.0000059*_np.square(_np.sin(2*abslat))) \
        / (3.085462e-6 + 2.27e-9 * _np.cos(2*abslat) - 2e-12 * _np.cos(4*abslat))  # Earth radius in metres
    
    return Reff


def distance_direction_from_longitude_latitude(lon, lat):
    """Compute the distance and direction between points for two arrays of longitude and latitude coordinates.
    
    The distance is in kilometres, the direction angle in radians, where 0=N, pi/2=E, +/-pi=S and -pi/2=W.
    
    Parameters:
      lon (float):  array of (at least two) longitude coordinates (radians).
      lat (float):  array of (at least two) latitude coordinates (radians).
    
    Returns:
      (tuple):  (ddist, direc):
    
      ddist (float):  array with distances between the subsequent coordinate sets (km).  ddist[0]=NaN.
      direc (float):  array with direction angles between the subsequent coordinate sets (radians).  ddist[0]=NaN.

    """
    
    Re     = effective_radius_from_latitude(lat)/1000  # Lat in radians, Re in m -> km
    rad2km = Re  # 2 pi rad = 2 pi Re km
    xpos   = lon * _np.cos(lat) * rad2km
    ypos   = lat * rad2km
    dxpos  = xpos - xpos.shift(1)
    dypos  = ypos - ypos.shift(1)
    ddist  = _np.sqrt(_np.square(dxpos) + _np.square(dypos))  # km
    direc  = _np.arctan2(dxpos, dypos)  # rad: N=0, E=pi/2, S=+/-pi, W=-pi/2 rad
    
    return ddist, direc
