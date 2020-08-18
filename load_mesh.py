from myselafin import Selafin
import numpy as np
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import os

def loadMeshFromSLF(output_fn):
    """
    Function to load a msh from a selafin object and save it is as a plot)
    """
    name = output_fn.split('/')[-1]
    name = name.split('.')[0]
    fn_mesh = './previously_loaded_meshes/%s_Mesh.png' % name
    fn_box = './previously_loaded_meshes/%s_Mesh.npy' % name

    if not os.path.isfile(fn_mesh):
        slf = Selafin(output_fn)
        slf.import_header()
        data = slf.import_data(step = None)
        slf.close()

        h = np.mean(data[2], axis = 1)

        xmin, xmax = np.min(slf.x), np.max(slf.x)
        ymin, ymax = np.min(slf.y), np.max(slf.y)
        xrange = xmax - xmin; yrange = ymax - ymin
        np.save(fn_box, np.array([xmin -0.05*xrange, xmax +0.05*xrange, ymin-0.05*yrange, ymax+0.05*yrange]))

        np.save('./previously_loaded_meshes/%s_t.npy' % name, slf.times)
        np.save('./previously_loaded_meshes/%s_data.npy' % name, data)
        np.save('./previously_loaded_meshes/%s_x.npy' % name, np.array(slf.x))
        np.save('./previously_loaded_meshes/%s_y.npy' % name, np.array(slf.y))

        # ------------------------------------------------------------------------------ #
        # Plot the Mesh
        f, a = plt.subplots(figsize=(25,25))
        tc = a.tripcolor(slf.x, slf.y, slf.ikle-1, np.zeros([np.shape(data)[1]]), cmap= 'Blues', edgecolors = 'k')
        a.axis('off')
        a.set_xlim(xmin - 0.05*xrange, xmax + 0.05*xrange)
        a.set_ylim(ymin - 0.05*yrange, ymax + 0.05*yrange)
        #a.set_aspect('equal')
        f.savefig(fn_mesh, bbox_inches='tight')

    else: [xmin, xmax, ymin, ymax] = np.load(fn_box)


    return fn_mesh, [xmin, xmax, ymin, ymax]
