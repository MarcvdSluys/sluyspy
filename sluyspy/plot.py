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


"""Plot functions for the sluyspy package."""

import matplotlib.pyplot as _plt         # Get matplotlib.pyplot
import numpy.core as _np                 # Get NumPy
from .cli import error as _error


def start_plot(ptype='both', dark_bg=False, xkcd=False, title='Python plot'):
    """Start a matplotlib.pyplot plot with a choice of my favourite options.
    
    Parameters:
      ptype (str):     Plot type: 'screen', 'file', 'both' (a compromise) or 'square'.
      dark_bg (bool):  Use a dark background.
      xkcd (bool):     Use XKCD style.
      title (str):     Window title.
    
    Returns:
      (tuple):  Tuple containing the plot and axis objects.
    """
    
    import matplotlib
    
    if xkcd:  _plt.xkcd()                                 # Plot everything that follows in XKCD style
    if dark_bg:  _plt.style.use('dark_background')        # Invert colours
    if xkcd and dark_bg:
        from matplotlib import patheffects
        _plt.rcParams['path.effects'] = [patheffects.withStroke(linewidth=0)]  # Needed for XKCD style on a dark background
    
    if ptype == 'screen':
        matplotlib.rcParams.update({'font.size': 14})      # Set font size for all text, aimed at full screen display
        fig = _plt.figure(figsize=(19.2,10.8), num=title)  # Set to 1920x1080 to fill my screen
    elif ptype == 'file':
        matplotlib.rcParams.update({'font.size': 12})      # Set font size for all text aimed at electonic file
        fig = _plt.figure(figsize=(12.5,7), num=title)     # Set png size to 1250x700
    elif ptype == 'both':
        matplotlib.rcParams.update({'font.size': 16})      # Set font size for all text: compromise screen visibility and report readability
        fig = _plt.figure(figsize=(15,8.5), num=title)     # 1500x850: fits in my qiv screen w/o scaling
    elif ptype == 'square':
        matplotlib.rcParams.update({'font.size': 16})      # Set font size for all text: compromise screen visibility and report readability
        fig = _plt.figure(figsize=(8.5,8.5), num=title)    # 850x850: fits in my qiv screen w/o scaling
    else:
        _error('Unknown plot type: '+ptype+', aborting.')
        
    ax = fig.add_subplot(111)                  # Create an axes object for the current figure
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
        print(' - Received keyboard interrupt, aborting.')  # " - " to create some space after "^C"
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
        print(' - Received keyboard interrupt, aborting.')  # " - " to create some space after "^C"
        exit(0)
        
    return
