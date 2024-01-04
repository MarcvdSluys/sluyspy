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


"""Plot functions for the sluyspy package."""

import matplotlib.pyplot as _plt         # Get matplotlib.pyplot
import numpy.core as _np                 # Get NumPy
from .cli import error as _error


def start_plot(ptype='both', hsize=None,vsize=None, dark_bg=False, xkcd=False, title='Python plot',
               fz=None,lw=None, plot3d=False, man_zorder=True):
    """Start a matplotlib.pyplot plot with a choice of my favourite options.
    
    Parameters:
      ptype (str):        Plot type: 'screen', 'file', 'both' (a compromise) or 'square'.
      hsize (float):      Horizontal size of the figure (hectopixels); can overrule setting by ptype.
      vsize (float):      Vertical size of the figure (hectopixels); can overrule setting by ptype.
    
      dark_bg (bool):     Use a dark background (optional, defaults to False).
      xkcd (bool):        Use XKCD style (optional, defaults to False).
      title (str):        Window title (optional, defaults to 'Python plot').
    
      fz (int):           Font size (optional, defaults to None -> 14 or 16).
      lw (int):           Line width (optional, defaults to None -> 1 or 2).
    
      plot3d (bool):      Start a 3D plot (optional, defaults to False -> 2D).
      map_zorder (bool):  Use manual zorder (defaults to True - opposed to pyplot default: compute).
    
    Returns:
      (tuple):  Tuple containing the plot and axis objects.
    
    Defaults:
      - screen: size 1920x1080, font 14, lw: 1;
      - file:   size 1250x700,  font 14, lw: 2;
      - both:   size 1580x850,  font 16, lw: 2;
      - square: size 850x850,   font 16, lw: 2.
    """
    
    import matplotlib
    
    if xkcd:  _plt.xkcd()                                   # Plot everything that follows in XKCD style
    if dark_bg:  _plt.style.use('dark_background')          # Invert colours
    if xkcd and dark_bg:
        from matplotlib import patheffects
        _plt.rcParams['path.effects'] = [patheffects.withStroke(linewidth=0)]  # Needed for XKCD style on a dark background
    
    if ptype == 'screen':
        if hsize is None: hsize = 19.2  # 1920
        if vsize is None: vsize = 10.8  # 1080
        matplotlib.rcParams.update({'font.size': 14})       # Set font size for all text, aimed at full screen display
    elif ptype == 'file':
        if hsize is None: hsize = 12.5  # 1250
        if vsize is None: vsize =  7.0  # 700
        matplotlib.rcParams.update({'font.size': 14})       # Set font size for all text aimed at an electonic file
        matplotlib.rcParams.update({'lines.linewidth': 2})  # Set default line width to 2
    elif ptype == 'both':
        if hsize is None: hsize = 15.8  # 1580
        if vsize is None: vsize =  8.5  # 850
        matplotlib.rcParams.update({'font.size': 16})       # Set font size for all text: compromise screen visibility and report readability
        matplotlib.rcParams.update({'lines.linewidth': 2})  # Set default line width to 2
    elif ptype == 'square':
        if hsize is None: hsize = 8.5  # 850
        if vsize is None: vsize = 8.5  # 850
        matplotlib.rcParams.update({'font.size': 16})       # Set font size for all text: compromise screen visibility and report readability
    else:
        _error('Unknown plot type: '+ptype+', aborting.')
    
    if fz is not None: matplotlib.rcParams.update({'font.size': fz})        # Set font size for all text
    if lw is not None: matplotlib.rcParams.update({'lines.linewidth': lw})  # Set custom default line width
    fig = _plt.figure(figsize=(hsize,vsize), num=title)  # Custom size
    
    if plot3d:
        ax = fig.add_subplot(111, projection='3d', computed_zorder=(not man_zorder))  # Create a 3D axes object for the current figure
    else:
        ax = fig.add_subplot(111)                                # Create a 2D axes object for the current figure
        
    if xkcd and dark_bg:  ax.spines[:].set_color('white')        # Needed for XKCD style on a dark background
    
    return fig, ax


def hist_norm(obj, x, bins=None, range=None, density=False, weights=None, cumulative=False, bottom=None,
              histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None,
              stacked=False, *, data=None, **kwargs):
    """Draw a histogram normalised by total number rather than probability density.
    
    Parameters:
      obj (pyplot object):  Pyplot object or axes object to plot to.
      x (array or sequence of arrays):  Data.
      bins (int or sequence or str):  Number of bins.  Default: rcParams["hist.bins"] (default: 10).
      range (tuple or None):  Bin range, default: None.
      density (bool):  Plot probability density.  Default: False.
      weights (array-like or None):  Weights.  Default: None.
      cumulative (bool or -1):  Plot a cumulative histogram.  Default: False.
      bottom (array-like, scalar, or None):  Location of the bottom of the bins.  Default: None.
      histtype (str):  Histogram type: {'bar', 'barstacked', 'step', 'stepfilled'}, default: 'bar'.
      align (str):  Bin alignment: {'left', 'mid', 'right'}, default: 'mid'.
      orientation (str):  Bin orientation:  {'vertical', 'horizontal'}, default: 'vertical'.
      rwidth (float or None):  The relative width of the bars as a fraction of the bin width, default: None.
      log (bool):  Set the histogram axis to a log scale, default: False.
      color (color or array-like of colors or None):  Color or sequence of colors for bins, one per dataset, default: None.
      label (str or None):  Legend label, default: None.
      stacked (bool):  Stack multiple data on top of each other, rather than side by side, default: False.
      data (indexable object, optional):  If given, the following parameters also accept a string s, which is interpreted as data[s] (unless this raises an exception): x, weights.
    
    
    Returns:
      (tuple):  Tuple consisting of (n, bin_edges, patches):
      
      - (array or list of arrays):  The values of the histogram bins.
      - (array): The edges of the bins. Length nbins + 1.
      - (BarContainer or list of Polygons):  (List of) container(s) of individual artists used to create the histogram(s).
    """
        
    weights = _np.ones_like(x) / len(x)  # Set all weights to 1/n to pass them to pyplot.hist()
    
    n, bin_edges, patches = obj.hist(x, bins=bins, range=range, density=density, weights=weights,
                                     cumulative=cumulative, bottom=bottom, histtype=histtype, align=align,
                                     orientation=orientation, rwidth=rwidth, log=log, color=color,
                                     label=label, stacked=stacked, data=data, **kwargs)
    
    return n, bin_edges, patches


def show_ctrlc():
    """Call pyplot.show() and catch Ctrl-C to exit gently."""
    
    try:
        _plt.show()
    except KeyboardInterrupt:
        print(' - Received keyboard interrupt whilst showing plot, aborting.')  # " - " to create some space after "^C"
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
        print(' - Received keyboard interrupt whilst pausing plot, aborting.')  # " - " to create some space after "^C"
        exit(0)
        
    return


def arrow_head_between_points(ax, xx,yy, dx=0,dy=0, scale=1, **kwargs):
    """Plot an arrow head between two 2D points.

    Parameters:
      ax (axes):      Axes object to plot on.
      xx (float):     Array with two x values, for arrow-head position and direction.
      yy (float):     Array with two y values, for arrow-head position and direction.
      dx (float):     Shift arrow head in x direction.
      dy (float):     Shift arrow head in y direction.
      scale (float):  Scale arrow head.
    """
    
    # Local scaling parameter: undo arrow-head scaling with length:
    lscale = 0.1 * scale / _np.sqrt((xx[1]-xx[0])**2 + (yy[1]-yy[0])**2)
    
    if len(xx)!=2: _error('arrow_head_between_points(): The input variable xx must have two elements')
    if len(yy)!=2: _error('arrow_head_between_points(): The input variable yy must have two elements')
    
    ax.quiver(xx[1]+dx, yy[1]+dy, xx[1]-xx[0], yy[1]-yy[0],
              angles='xy', scale_units='width', pivot='mid',
              scale=3/lscale, width=5e-3*lscale,
              headwidth=10*lscale, headlength=15*lscale, headaxislength=10*lscale,
              **kwargs)
    return
