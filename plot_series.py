import numpy as np
from getNeigh import getNeighbor
import matplotlib.pyplot as plt

def plotT2Series(T, XY, x, y, SE, Vel, plot_fn = 'support_files/plot_series', ):
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
    print('Distance between POI and node: ',((x_node - x)**2 + (y_node - y)**2)**0.5)
    SEseries = SE[i,:]
    Velseries = Vel[i,:]

    f, a = plt.subplots(figsize = (15,4))
    a.plot(T, SEseries)
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
    f.savefig(plot_fn+'_WSE.png', bbox_inches = 'tight', transparent = True)

    f, a = plt.subplots(figsize = (15,4))
    a.plot(T, Velseries)
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
    f.savefig(plot_fn+'_Vel.png', bbox_inches = 'tight', transparent = True)

    return plot_fn
