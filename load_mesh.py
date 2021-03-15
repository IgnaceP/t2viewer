from myselafin import Selafin
import numpy as np
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import os
import matplotlib.pylab as pl
from matplotlib.colors import ListedColormap
from shutil import copyfile


def loadMeshFromSLF(output_fn, figure = None, canvas = None, ignore_previously_saved_files = False, return_tc = False):
    """
    Function to load a msh from a selafin object and save it is as a plot)
    """
    name = output_fn.split('/')[-1]
    name = name.split('.')[0]
    if name.rfind('_') != -1:
        name = '_'.join(name.split('_')[:-1])

    fn_box = './previously_loaded_meshes/%s_Mesh.npy' % (name)

    if output_fn[-4:] == '.slf':

        if not os.path.isfile(fn_box) or ignore_previously_saved_files:

            print('Loading selafin...')
            slf = Selafin(output_fn)
            slf.import_header()
            data = slf.import_data(step = None)
            slf.close()
            print('Selafin loaded!')

            print('Saving box...')
            xmin, xmax = np.min(slf.x), np.max(slf.x)
            ymin, ymax = np.min(slf.y), np.max(slf.y)
            xrange = xmax - xmin; yrange = ymax - ymin
            np.save(fn_box, np.array([xmin -0.05*xrange, xmax +0.05*xrange, ymin-0.05*yrange, ymax+0.05*yrange]))

            print('Saving time steps...')
            np.save('./previously_loaded_meshes/%s_times.npy' % name, slf.times)
            print('Saving data numpy array...')
            np.save('./previously_loaded_meshes/%s_data.npy' % name, data)
            print('Saving x and y...')
            np.save('./previously_loaded_meshes/%s_x.npy' % name, np.array(slf.x))
            np.save('./previously_loaded_meshes/%s_y.npy' % name, np.array(slf.y))
            np.save('./previously_loaded_meshes/%s_ikle.npy' % name, np.array(slf.ikle))

        else: [xmin, xmax, ymin, ymax] = np.load(fn_box)


    elif output_fn[-4:] == '.npy':

        fn = output_fn.split('_')[:-1]
        fn = '_'.join(fn) + '_'

        if not os.path.isfile(fn_box) or ignore_previously_saved_files:

            copyfile(fn +'x.npy', './previously_loaded_meshes/%s_x.npy' % name)
            copyfile(fn +'y.npy', './previously_loaded_meshes/%s_y.npy' % name)
            copyfile(fn +'data.npy', './previously_loaded_meshes/%s_data.npy' % name)
            copyfile(fn +'ikle.npy', './previously_loaded_meshes/%s_ikle.npy' % name)
            copyfile(fn +'times.npy', './previously_loaded_meshes/%s_times.npy' % name)

            print('Saving box...')
            xmin, xmax = np.min(np.load('./previously_loaded_meshes/%s_x.npy' % name)), np.max(np.load('./previously_loaded_meshes/%s_x.npy' % name))
            ymin, ymax = np.min(np.load('./previously_loaded_meshes/%s_y.npy' % name)), np.max(np.load('./previously_loaded_meshes/%s_y.npy' % name))
            xrange = xmax - xmin; yrange = ymax - ymin
            np.save(fn_box, np.array([xmin -0.05*xrange, xmax +0.05*xrange, ymin-0.05*yrange, ymax+0.05*yrange]))

        else: [xmin, xmax, ymin, ymax] = np.load(fn_box)

    if figure != None:
        ax, tc = plotMesh(name, figure, return_tc = True)

    if return_tc:
        return name, ax, tc
    else:
        return name, ax




def plotMesh(name, figure, return_tc = False):
    # ------------------------------------------------------------------------------ #
    # Plot the Mesh

    print('Plotting...')

    fn_box = './previously_loaded_meshes/%s_Mesh.npy' % name
    [xmin, xmax, ymin, ymax] = np.load(fn_box)

    figure.clf()
    ax = figure.add_subplot(111)
    plt.tight_layout()

    x = np.load('./previously_loaded_meshes/%s_x.npy' % name)
    y = np.load('./previously_loaded_meshes/%s_y.npy' % name)
    ikle = np.load('./previously_loaded_meshes/%s_ikle.npy' % name)
    data = np.load('./previously_loaded_meshes/%s_data.npy' % name, mmap_mode='r')
    size = np.shape(data)[1]
    del data
    print('almost ready')
    tc = ax.tripcolor(x, y, ikle-1, np.zeros([size]), cmap = 'gist_earth')
    tc.set_edgecolors('white')
    tc.set_linewidths(0.01)
    ax.axis('off')
    ax.margins(2)
    ax.set_xlim(xmin - 0.05*(xmax - xmin), xmax + 0.05*(xmax - xmin))
    ax.set_ylim(ymin - 0.05*(ymax - ymin), ymax + 0.05*(ymax - ymin))
    ax.set_aspect('equal')
    print('ready!')

    if return_tc:
        return ax, tc
    else:
        return ax
