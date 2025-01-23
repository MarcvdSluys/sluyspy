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

import matplotlib as _mpl               # Get matplotlib
import matplotlib.pyplot as _plt        # Get matplotlib.pyplot
import numpy.core as _np                # Get NumPy
from .cli import error as _error


def start_plot(ptype='both', hsize=None,vsize=None, dark_bg=False, xkcd=False, title='Python plot',
               fz=None,lw=None, plot3d=False, man_zorder=True, cblind=True):
    """Start a matplotlib.pyplot plot with a choice of my favourite options.
    
    Parameters:
      ptype (str):        Plot type: 'screen', 'file', 'both' (a compromise; default), 'square' or 'org'.
      hsize (float):      Horizontal size of the figure (pixels if >50, hectopixels otherwise); can overrule setting by ptype.
      vsize (float):      Vertical size of the figure (pixels if >50, hectopixels otherwise); can overrule setting by ptype.
    
      dark_bg (bool):     Use a dark background (optional, defaults to False).
      xkcd (bool):        Use XKCD style (optional, defaults to False).
      title (str):        Window title (optional, defaults to 'Python plot').
    
      fz (int):           Font size (optional, defaults to None -> 14 or 16).
      lw (int):           Line width (optional, defaults to None -> 1 or 2).
    
      plot3d (bool):      Start a 3D plot (optional, defaults to False -> 2D).
      map_zorder (bool):  Use manual zorder (defaults to True - opposed to pyplot default: compute).
      cblind (bool):      Choose a colour-blindness-aware colour palette (optional, defaults to True).
    
    Returns:
      (tuple):  Tuple (fig,ax) containing the figure and axis objects.
    
    Defaults:
      - screen: size 1920x1080, font 14, lw: 1 - aimed at my screen;
      - file:   size 1250x700,  font 14, lw: 2 - aimed for file -> LaTeX;
      - both:   size 1580x850,  font 16, lw: 2 - a compromise between the above;
      - square: size 850x850,   font 16, lw: 2 - a square plot;
      - org:    size 930x520,   font 12, lw: 1 - aimed at output in emacs Orgmode.
    """
    
    if cblind is True: _plt.style.use('tableau-colorblind10')
    
    if xkcd:  _plt.xkcd()                                   # Plot everything that follows in XKCD style
    if dark_bg:  _plt.style.use('dark_background')          # Invert colours
    if xkcd and dark_bg:
        _plt.rcParams['path.effects'] = [_mpl.patheffects.withStroke(linewidth=0)]  # Needed for XKCD style on a dark background
    
    # If size>50, assume pixels/"dots" are specified; convert to "inches":
    if hsize is not None and hsize>50: hsize /= 100  # default: 100 dpi
    if vsize is not None and vsize>50: vsize /= 100  # default: 100 dpi
    
    if ptype == 'screen':
        if hsize is None: hsize = 19.2  # 1920 pixels
        if vsize is None: vsize = 10.8  # 1080 pixels
        _mpl.rcParams.update({'font.size': 14})       # Set font size for all text, aimed at full screen display
    elif ptype == 'file':
        if hsize is None: hsize = 12.5  # 1250 pixels
        if vsize is None: vsize =  7.0  # 700 pixels
        _mpl.rcParams.update({'font.size': 14})       # Set font size for all text aimed at an electonic file
        _mpl.rcParams.update({'lines.linewidth': 2})  # Set default line width to 2
    elif ptype == 'both':
        if hsize is None: hsize = 15.8  # 1580 pixels
        if vsize is None: vsize =  8.5  # 850 pixels
        _mpl.rcParams.update({'font.size': 16})       # Set font size for all text: compromise screen visibility and report readability
        _mpl.rcParams.update({'lines.linewidth': 2})  # Set default line width to 2
    elif ptype == 'square':
        if hsize is None: hsize = 8.5  # 850 pixels
        if vsize is None: vsize = 8.5  # 850 pixels
        _mpl.rcParams.update({'font.size': 16})       # Set font size for all text: compromise screen visibility and report readability
    elif ptype == 'org':
        if hsize is None: hsize = 9.0  # 900 pixels
        if vsize is None: vsize = 5.0  # 500 pixels
        _mpl.rcParams.update({'font.size': 12})       # Set font size for all text: small
    else:
        _error('Unknown plot type: '+ptype+', aborting.')
    
    # Find unique plot title ("number") - doublets cause mixed plots!
    titlel = title  # Local version
    plotnum = 2
    while _plt.fignum_exists(titlel):
        titlel = title + ' ' + str(plotnum)
    
    if fz is not None: _mpl.rcParams.update({'font.size': fz})        # Set font size for all text
    if lw is not None: _mpl.rcParams.update({'lines.linewidth': lw})  # Set custom default line width
    fig = _plt.figure(figsize=(hsize,vsize), num=titlel)  # Custom size
    
    if plot3d:
        ax = fig.add_subplot(111, projection='3d', computed_zorder=(not man_zorder))  # Create a 3D axes object for the current figure
    else:
        ax = fig.add_subplot(111)                                # Create a 2D axes object for the current figure
        
    if xkcd and dark_bg:  ax.spines[:].set_color('white')        # Needed for XKCD style on a dark background
    
    return fig, ax


def finish_plot(fig,ax, file_name=None, title=None, xlbl=None,ylbl=None, legend=False, legend_loc='best',
                grid=True, logx=False,logy=False, logx_gfmt=True, logy_gfmt=True, tight=1, save=True,
                close=True):
    """Show the current figure on screen or save it to disc and close it.
    
    Parameters:
      fig (pyplot.figure):  Current Pyplot figure object.
      ax (pyplot axes):     Current Pyplot axes object.
      file_name (str):      Name for the output file (optional, defaults to None -> screen).
    
      title (str):          Text to use as plot title (optional, defaults to None).
      xlbl (str):           Text to use as label for the horizontal axis (optional, defaults to None).
      ylbl (str):           Text to use as label for the vertical axis (optional, defaults to None).
    
      legend (bool):        Show a legend (optional, defaults to False).
      legend_loc (str):     Location for the legend (optional, defaults to 'best').
      grid (bool):          Show a grid (optional, defaults to True).
    
      logx (bool):          Make the horizontal axis logarithmic (optional, defaults to False -> linear).
      logy (bool):          Make the vertical axis logarithmic (optional, defaults to False -> linear).
    
      logx_gfmt (bool):     Use non-scientific format where possible on the horizontal axis.  Changes 10^0 -> 1, but also 10^40 -> 1e+40
      logy_gfmt (bool):     Use non-scientific format where possible on the vertical axis.  Changes 10^0 -> 1, but also 10^40 -> 1e+40
    
      tight (int):          Tightness of the margins: 0: not at all, 1: some (default), 2: quite, 3: very!
    
      save (bool):          Actually save the plot (if not, allow further changes, and don't close!).
      close (bool):         Actually close the plot (if not, allow further changes).
    """
    
    # Plot labels:
    if title is not None: _plt.title(title)                       # Plot title
    if xlbl is not None:  ax.set_xlabel(xlbl)                     # Label the horizontal axis
    if ylbl is not None:  ax.set_ylabel(ylbl)                     # Label the vertical axis
    
    # Plot features:
    if legend: ax.legend(loc=legend_loc)                          # Create a legend
    if logx:
        ax.set_xscale('log')                                 # Logarithmic horizontal axis
        if logx_gfmt: _plt.gca().xaxis.set_major_formatter(_mpl.ticker.FormatStrFormatter('%0g'))  # Use non-scientific format where possible
    if logy:
        ax.set_yscale('log')                                 # Logarithmic vertical axis
        if logy_gfmt: _plt.gca().yaxis.set_major_formatter(_mpl.ticker.FormatStrFormatter('%0g'))  # Use non-scientific format where possible
    if grid: ax.grid(grid)                                        # Plot a grid
    
    # Tightness of the margins:
    if tight>0: fig.tight_layout()                                # Use narrow margins
    
    if (file_name is None) or (file_name == 'screen'):
        if file_name == 'screen': print("sluyspy.plot.finish_plot(): file_name = 'screen' is obsolescent and will be removed.  Use None instead.")
        show_ctrlc()
    else:
        if save:
            if tight>2:
                fig.savefig(file_name, bbox_inches='tight', pad_inches=0)  # Use very, very narrow margins!
            elif tight>1:
                fig.savefig(file_name, bbox_inches='tight')                # Use very narrow margins
            else:
                fig.savefig(file_name)                                     # Save figure
        else:
            close = False  # Don't close the plot if you didn't save it!
    
    if close: _plt.close(fig=fig)
    
    return


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
      kwargs (dict):  Keyword arguments to be passed to pyplot.quiver().
    
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
    """Plot an arrow head between two 2D points and try to scale properly.
    
    Parameters:
      ax (axes):      Axes object to plot on.
      xx (float):     Array with two x values, for arrow-head position and direction.
      yy (float):     Array with two y values, for arrow-head position and direction.
      dx (float):     Shift arrow head in x direction.
      dy (float):     Shift arrow head in y direction.
      scale (float):  Scale arrow head.
      kwargs (dict):  Keyword arguments to be passed to pyplot.quiver().
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


def arrow_between_points(ax, xx,yy, scale=1, zorder=2, **kwargs):
    """Plot an arrow between two 2D points and try to scale the shaft and head properly.
    
    Parameters:
      ax (axes):      Axes object to plot on.
      xx (float):     Array with two x values, for tail and head position.
      yy (float):     Array with two y values, for tail and head position.
      scale (float):  Scale arrow shaft and head.
      zorder (int):   Zorder for the arrow.  Zorder<2 places it below the grid.
      kwargs (dict):  Keyword arguments to be passed to pyplot.quiver().
    """
    
    # Local scaling parameter: undo arrow-head scaling with length:
    sscale = 0.01 * scale  # Shaft AND head
    hscale = 2.5           # Head only, on tip of sscale
    
    if len(xx)!=2: _error('arrow_between_points(): The input variable xx must have two elements')
    if len(yy)!=2: _error('arrow_between_points(): The input variable yy must have two elements')
    
    ax.quiver(xx[0], yy[0], xx[1]-xx[0], yy[1]-yy[0],  # x1,y1 -> dx,dy
              angles='xy', units='xy', scale=1,
              pivot='tail', scale_units=None,  # Defaults
              width=sscale,                    # Shaft width
              headwidth=2*hscale, headlength=3*hscale, headaxislength=2*hscale,  # Head size - scales strangely with width
              zorder=zorder,    # zorder <2 places arrow below grid.
              **kwargs)
    
    return
