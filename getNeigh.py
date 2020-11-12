import numpy as np

# function to find the closest vertex of a POI
def getNeighbor(p, pol, kernel_fract = 0.01, return_index = False):
    """
    Function to find the closest vertex of polgyon to a POI.
    The closest neighbor is found by taking all vertices of a polygon which are located
    within a distance r from the POI. The distance r is increased step by step (by the kernel_fract)
    untill a point is found. Therefore, the kernel_fract does not affect the result but it is meant
    to optimize the computational time of the procedure.

    Author: Ignace Pelckmans (University of Antwerp, Belgium)

    Args:
        p: (Required) 1x2 Numpy Array, tuple or list with x- and y-coordinates of the poin of interest (POI)
        pol: (Required) nx2 numpy array with x- and y-coordinates of the polygon's vertices
        kernel_fract: (Optional) stepsize of the kernel size (% of the total width/height of the polygon). The kernel stepsize is the size to increase the searching circle around POI.
                                 It does not affect the final result is meant to optimize the computational time of the procedure.
        return_index: (Optional, defaults to False) return the index of the neighbor as well

    Returns:
        Numpy array of dimensions 1 x 2 with the x- and y-coordinate of the closest vertex of the polygon to the POI

    """
    # get width and height of channel polygon
    width = np.max(pol[:, 0]) - np.min(pol[:, 0])
    height = np.max(pol[:, 1]) - np.min(pol[:, 1])

    # parse to separate x- and y-coordinate
    px, py = p

    # stepsize to increase kernel
    ks = kernel_fract* max(width, height)

    # initialize a flag to feed the while loop and start a counter
    neigh_flag = False; t = 0
    # run while loop as long as there are no neighbouring vertices selected
    while neigh_flag == False:

        # count
        t += 1

        # create a square mask to only calculate the distances between the POI and nearby polygon vertices
        neigh_mask = (pol[:,0] > px - t*ks) * (pol[:,0] < px + t*ks) \
                * (pol[:,1] > py - t*ks) * (pol[:,1] < py + t*ks)
        # mask on all vertices
        neigh = pol[neigh_mask]

        # calculate the distance between the POI en all vertices after masking
        dist = (np.sum((neigh - p) ** 2, axis=1)) ** 0.5
        # mask a circle within the square kernel
        circle_mask = (dist <= t*ks/2)
        neigh = neigh[circle_mask]
        dist = dist[circle_mask]

        # terminate loop if there is at least one vertex in the neighbouring circle, otherwise increase the kernel size
        if np.shape(neigh)[0] > 0:
            neigh_flag = True

    # get the neigbor coordinates which is the vertex within the circle (around POI, radius t*ks)
    neighbor = neigh[np.argmin(dist),:]
    neighbor_index = np.argmin(dist)

    if return_index:
        return neighbor, neighbor_index
    else:
        return neighbor
