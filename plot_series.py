import numpy as np
from getNeigh import getNeighbor
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os

def plotT2Series(T, XY, x, y, SE, Vel, t0, t1, plot_fn = 'support_files/plot_series'):
    """
    Function to plot a time series from a Telemac 2D Output file
    ! important note: the resulting plot is not an interpolation but the info from the closest node!

    Args:
    - output_fn (Required): file path to output file (often out_t2d.slf)
    - x & y (Required): Coordinate pair (in utm) of the location where to plot
    - plot_fn (Optional, defaults to output/plot_series.png): File path to plotted series
    - start_date (Optional): Datetime corresponding to the start of the simulation

    Output:

    """

    X = XY[:,0]
    Y = XY[:,1]

    # find the closest node to the requested lat and lon
    neighxy= getNeighbor([x, y], XY, return_index = False)
    x_node, y_node = neighxy
    rx = np.where(X == x_node)
    ry = np.where(Y == y_node)
    i = np.intersect1d(rx,ry)[0]

    SEseries = np.array(SE[i,:])
    Velseries = np.array(Vel[i,:])

    mask = (T>t0)*(T<t1)
    SEmin = np.min(SEseries[mask])
    SEmax = np.max(SEseries[mask])
    SErange = SEmax - SEmin
    Velmin = np.min(Velseries[mask])
    Velmax = np.max(Velseries[mask])
    Velrange = Velmax - -Velmin


    f, a = plt.subplots(figsize = (15,4))
    a.plot(T, SEseries,'.-', color = (1, 128/255, 0))
    a.grid('on')
    a.set_ylabel('Water Surface Elevation [m]', fontweight = 'bold', fontsize = 14)
    a.spines['bottom'].set_color('white')
    a.spines['top'].set_color('white')
    a.spines['right'].set_color('white')
    a.spines['left'].set_color('white')
    a.tick_params(axis='x', colors='white')
    a.tick_params(axis='y', colors='white')
    a.xaxis.label.set_color('white')
    a.yaxis.label.set_color('white')
    a.set_xlim(t0,t1)
    a.set_ylim(max(-999,SEmin - 0.1*SErange), min(999,SEmax + 0.1*SErange))
    f.savefig(plot_fn+'_WSE.png', bbox_inches = 'tight', transparent = True)

    f.clear()
    del f

    f, a = plt.subplots(figsize = (15,4))
    a.plot(T, Velseries,'.-', color = (1, 128/255, 0))
    a.grid('on')
    a.set_ylabel('Velocity [m/s]', fontweight = 'bold', fontsize = 14)
    a.spines['bottom'].set_color('white')
    a.spines['top'].set_color('white')
    a.spines['right'].set_color('white')
    a.spines['left'].set_color('white')
    a.tick_params(axis='x', colors='white')
    a.tick_params(axis='y', colors='white')
    a.xaxis.label.set_color('white')
    a.yaxis.label.set_color('white')
    a.set_xlim(t0,t1)
    a.set_ylim(max(-999,Velmin - 0.1*Velrange), min(999,Velmax + 0.1*Velrange))
    f.savefig(plot_fn+'_Vel.png', bbox_inches = 'tight', transparent = True)

    f.clear()
    del f

    return plot_fn, neighxy, i

def plotVarMesh(x,y,ikle,var, label_str, path = None, min = 0, max = 1e9, ax = None, fig = None):

    # ------------------------------------------------------------------------------ #
    # Plot the Mesh

    xmin, xmax = np.min(x),np.max(x)
    ymin, ymax = np.min(y),np.max(y)

    if ax == None:
        fig, ax = plt.subplots(figsize = (12,12))
    plt.tight_layout()
    ax.cla()
    tc = ax.tripcolor(x, y, ikle-1, var, vmin = min, vmax = max, cmap = 'gist_earth')
    #tc.set_edgecolors('white')
    ax.axis('off')
    ax.margins(2)
    ax.set_xlim(xmin - 0.05*(xmax - xmin), xmax + 0.05*(xmax - xmin))
    ax.set_ylim(ymin - 0.05*(ymax - ymin), ymax + 0.05*(ymax - ymin))
    ax.set_aspect('equal')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.05)
    cb = fig.colorbar(tc, orientation = 'horizontal', cax = cax)
    cb.ax.set_title(label_str,size = 10, color = 'white')
    cb.ax.tick_params(labelsize=8, color = 'white', labelcolor = 'white')

    if path != None:
        fig.savefig(path)
        os.system('nomacs %s' % path)
