from myselafin import Selafin
import numpy as np
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import os
import matplotlib.pylab as pl
from matplotlib.colors import ListedColormap
from shutil import copyfile


def loadMeshFromSLF(output_fn, figure, canvas, ignore_previously_saved_files = False):
    """
    Function to load a msh from a selafin object and save it is as a plot)
    """

    name = output_fn.split('/')[-1]
    name = name.split('.')[0]
    name = '_'.join(name.split('_')[:-1])

    fn_mesh = './previously_loaded_meshes/%s_Mesh.png' % name
    fn_box = './previously_loaded_meshes/%s_Mesh.npy' % name

    if output_fn[-4:] == '.slf':

        if not os.path.isfile(fn_mesh) or ignore_previously_saved_files:
            print('Loading selafin...')
            slf = Selafin(output_fn)
            slf.import_header()
            data = slf.import_data(step = None)
            slf.close()
            print('Selafin loaded!')

            print('Calculating mean waterheight')
            h = np.mean(data[2], axis = 1)

            print('Saving box...')
            xmin, xmax = np.min(slf.x), np.max(slf.x)
            ymin, ymax = np.min(slf.y), np.max(slf.y)
            xrange = xmax - xmin; yrange = ymax - ymin
            np.save(fn_box, np.array([xmin -0.05*xrange, xmax +0.05*xrange, ymin-0.05*yrange, ymax+0.05*yrange]))

            print('Saving time steps...')
            np.save('./previously_loaded_meshes/%s_t.npy' % name, slf.times)
            print('Saving data numpy array...')
            np.save('./previously_loaded_meshes/%s_data.npy' % name, data)
            print('Saving x and y...')
            np.save('./previously_loaded_meshes/%s_x.npy' % name, np.array(slf.x))
            np.save('./previously_loaded_meshes/%s_y.npy' % name, np.array(slf.y))


        else: [xmin, xmax, ymin, ymax] = np.load(fn_box)


    elif output_fn[-4:] == '.npy':

        fn = output_fn.split('_')[:-1]
        fn = '_'.join(fn) + '_'

        if not os.path.isfile(fn_mesh) or ignore_previously_saved_files:

            copyfile(fn +'t.npy', './previously_loaded_meshes/%s_t.npy' % name)
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

            # ------------------------------------------------------------------------------ #
            # Plot the Mesh

            x = np.load('./previously_loaded_meshes/%s_x.npy' % name)
            y = np.load('./previously_loaded_meshes/%s_y.npy' % name)
            ikle = np.load('./previously_loaded_meshes/%s_ikle.npy' % name)

            print('Plotting...')
            f, a = plt.subplots(figsize=(25,25))

            tc = a.tripcolor(x, y, ikle-1, np.zeros([np.shape(x)[0]]), cmap = 'gray')

            tc.set_edgecolors('white')
            a.axis('off')
            a.set_xlim(xmin - 0.05*xrange, xmax + 0.05*xrange)
            a.set_ylim(ymin - 0.05*yrange, ymax + 0.05*yrange)
            #a.set_aspect('equal')
            f.savefig(fn_mesh, bbox_inches='tight', transparent=True)


        else: [xmin, xmax, ymin, ymax] = np.load(fn_box)

    # ------------------------------------------------------------------------------ #
    # Plot the Mesh

    print('Plotting...')

    ax = figure.add_subplot(111)
    plt.tight_layout()
    ax.cla()
    x = np.load('./previously_loaded_meshes/%s_x.npy' % name)
    y = np.load('./previously_loaded_meshes/%s_y.npy' % name)
    ikle = np.load('./previously_loaded_meshes/%s_ikle.npy' % name)
    data = np.load('./previously_loaded_meshes/%s_data.npy' % name)
    print('almost ready')
    tc = ax.tripcolor(x, y, ikle-1, np.zeros([np.shape(data)[1]]), cmap = 'gist_earth')
    tc.set_edgecolors('white')
    tc.set_linewidths(0.01)
    ax.axis('off')
    ax.margins(2)
    ax.set_xlim(xmin - 0.05*(xmax - xmin), xmax + 0.05*(xmax - xmin))
    ax.set_ylim(ymin - 0.05*(ymax - ymin), ymax + 0.05*(ymax - ymin))
    ax.set_aspect('equal')
    canvas.draw()
    print('ready!')

    return fn_mesh, ax
