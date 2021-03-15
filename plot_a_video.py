from myselafin import Selafin
import numpy as np
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import ListedColormap
import argparse
import progressbar as pp
import time
#from pathos.multiprocessing import ProcessingPool as PathosPool
import PyQt5.QtCore
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import os
import subprocess

class VideoThread_v1(QThread):
    sig1 = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def on_source(self, lis):
        self.source_txt, self.fn, videoparams = lis
        [self.var, self.min, self.max, self.lims] = videoparams

    def run(self):
        self.sig1.emit('Preparing the animation procedure...')
        output_path = self.source_txt

        #----------------------------------------------------------------------------#
        # video parameters
        var2plot = 'SE'
        var2plot_label = 'Water Surface Elevation [m]'
        h_min = self.min
        h_max = self.max

        #----------------------------------------------------------------------------#
        start_time = time.time()

        data = np.load(output_path + '_data.npy')
        x = np.load(output_path + '_x.npy')
        y = np.load(output_path + '_y.npy')
        ikle = np.load(output_path + '_ikle.npy')
        times = np.load(output_path + '_times.npy')

        H = data[2]
        B = data[3]
        N = data[4]
        SE = B + H

        # ------------------------------------------------------------------------------ #
        # make a video

        print('Turning the simulated water surface elevations into an Oscar contender...')

        try: os.system('rm -r tmp')
        except: pass
        os.system('mkdir tmp')

        if self.var == 0:
            var = SE

        rows, cols = var.shape

        f, a = plt.subplots(figsize=(15, 15))

        # the actual plot
        tc = a.tripcolor(x, y, ikle - 1, var[:, 0], vmin=h_min, vmax=h_max, cmap='ocean')

        # create a nice colorbar
        divider = make_axes_locatable(a)
        cax = divider.append_axes("bottom", size="5%", pad=0.05)
        cb = f.colorbar(tc, orientation='horizontal', cax=cax)
        cb.ax.set_title('Water Surface elevation', size=18)
        cb.ax.tick_params(labelsize=18)

        # set axes limits
        if self.lims != None:
            a.set_xlim(self.lims[0], self.lims[1])
            a.set_ylim(self.lims[3], self.lims[2])

        # get axes limits
        ymin, ymax = a.get_ylim()
        yrange = ymax - ymin
        xmin, xmax = a.get_xlim()
        xrange = xmax - xmin

        # scale bar
        rect = matplotlib.patches.Rectangle([xmin + 7/10*xrange, ymin + 1/10*yrange - yrange/28], width=25000, height=yrange/400, facecolor='black')
        a.add_patch(rect)
        a.annotate('25 km', [xmin + 7/10*xrange, ymin + 1/10*yrange - yrange/40], size=10, color='black')
        tim = '0 hrs 0 mins'
        a1 = a.annotate(tim, [xmin + 7/10*xrange, ymin + 1/10*yrange], size=16, color='black')


        def createFrame(i, tc, times, a1, f):

            t = times[i]
            hrs = t // 3600
            min = (t % 3600) // 60
            sec = (t % 3600) % 60

            tim = '%d hrs %d mins' % (hrs, min)
            a1.set_text(tim)

            tc.set_array(var[:,i])

            f.savefig('tmp/frame_%d.png' % i)

            return 'tmp/frame_%d.png' % i

        for i in range(cols):
            createFrame(i, tc, times, a1, f)

        if not self.fn.endswith('.mp4'): self.fn + '.mp4'

        #command = ('mencoder tmp/*.png -mf type=png:fps=1 -ovc lavc -lavcopts vcodec=mpeg4 -oac copy -o %s' % self.fn)
        command = 'ffmpeg -y -r 1 -i tmp/%%d.png %s' % self.fn
        os.system(command)

        self.sig1.emit('Video is ready and stored at %s!' % output_path)
        dt = time.time()-start_time
        min = dt//60
        sec = dt%60
        print("Writing the video took "+ str(int(min))+ " minutes and "+str(int(sec)) + " seconds.")

class VideoThread(QThread):
    sig1 = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def on_source(self, lis):
        self.source_txt, self.fn, videoparams = lis
        [self.var, self.min, self.max, self.lims] = videoparams

    def run(self):
        self.sig1.emit('Preparing the animation procedure...')
        output_path = self.source_txt

        #----------------------------------------------------------------------------#
        # video parameters
        var2plot = 'SE'
        var2plot_label = 'Water Surface Elevation [m]'
        h_min = self.min
        h_max = self.max
        #----------------------------------------------------------------------------#
        start_time = time.time()

        data = np.load(output_path + '_data.npy')
        x = np.load(output_path + '_x.npy')
        y = np.load(output_path + '_y.npy')
        ikle = np.load(output_path + '_ikle.npy')
        times = np.load(output_path + '_times.npy')

        H = data[2]
        B = data[3]
        N = data[4]
        SE = B + H

        # ------------------------------------------------------------------------------ #
        # make a video

        print('Turning the simulated water surface elevations into an Oscar contender...')

        # initiate video writer
        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Movie Test', artist='Matplotlib',
                        comment='Movie support!')
        writer = FFMpegWriter(fps=4, metadata=metadata, bitrate = -1)

        f, a = plt.subplots(figsize=(15, 15))

        if self.var == 0:
            var = SE

        # the actual plot
        triangles = matplotlib.tri.Triangulation(x, y, ikle-1)
        tc = a.tripcolor(triangles, var[:, 0], vmin=h_min, vmax=h_max, cmap='ocean', shading='gouraud')

        # clean axes
        a.axis('off')
        a.set_aspect('equal')

        # create a nice colorbar
        divider = make_axes_locatable(a)
        cax = divider.append_axes("bottom", size="5%", pad=0.05)
        cb = f.colorbar(tc, orientation='horizontal', cax=cax)
        cb.ax.set_title('Water Surface elevation', size=18)
        cb.ax.tick_params(labelsize=18)

        # set axes limits
        if self.lims != None:
            a.set_xlim(self.lims[0], self.lims[1])
            a.set_ylim(self.lims[3], self.lims[2])

        # get axes limits
        ymin, ymax = a.get_ylim()
        yrange = ymax - ymin
        xmin, xmax = a.get_xlim()
        xrange = xmax - xmin

        # scale bar
        rect = matplotlib.patches.Rectangle([xmin + 7/10*xrange, ymin + 1/10*yrange - yrange/28], width=25000, height=yrange/400, facecolor='black')
        a.add_patch(rect)
        a.annotate('25 km', [xmin + 7/10*xrange, ymin + 1/10*yrange - yrange/40], size=10, color='black')
        tim = '%d hrs %d mins' % (0, 0)

        a1 = a.annotate(tim, [xmin + 7/10*xrange, ymin + 1/10*yrange], size=16, color='black')
        rows, cols = np.shape(data[0])

        t0 = time.time()

        if not self.fn.endswith('.mp4'): self.fn + '.mp4'

        with writer.saving(f, self.fn, cols):
            for i in range(cols):

                per = i/cols * 100

                t = times[i]
                hrs = t // 3600
                min = (t % 3600) // 60
                sec = (t % 3600) % 60

                tim = '%d hrs %d mins' % (hrs, min)
                a1.set_text(tim)
                tc.set_array(var[:, i])

                #f.canvas.draw()
                #f.canvas.flush_events()

                dt = time.time() - t0
                estimated_time = dt*(cols - i)
                hrs = estimated_time//3600
                min = estimated_time%3600/60

                self.sig1.emit('Generating video is at %.2f %s and the estimated remaining time is: %.0f hr and %.2f min.' % (i/cols * 100, '%', hrs, min))

                writer.grab_frame()
                t0 = time.time()

        self.sig1.emit('Video is ready and stored at %s!' % output_path)
        dt = time.time()-start_time
        min = dt//60
        sec = dt%60
        print("Writing the video took "+ str(int(min))+ " minutes and "+str(int(sec)) + " seconds.")

class VideoThread(QThread):
    sig1 = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def on_source(self, lis):
        self.source_txt, self.fn, videoparams = lis
        [self.var, self.min, self.max, self.lims] = videoparams

    def run(self):
        self.sig1.emit('Preparing the animation procedure...')
        output_path = self.source_txt

        #----------------------------------------------------------------------------#
        # video parameters
        var2plot = 'SE'
        var2plot_label = 'Water Surface Elevation [m]'
        h_min = self.min
        h_max = self.max
        #----------------------------------------------------------------------------#
        start_time = time.time()

        data = np.load(output_path + '_data.npy')
        x = np.load(output_path + '_x.npy')
        y = np.load(output_path + '_y.npy')
        ikle = np.load(output_path + '_ikle.npy')
        times = np.load(output_path + '_times.npy')

        H = data[2]
        B = data[3]
        N = data[4]
        SE = B + H

        # ------------------------------------------------------------------------------ #
        # make a video

        print('Turning the simulated water surface elevations into an Oscar contender...')

        # initiate video writer
        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Movie Test', artist='Matplotlib',
                        comment='Movie support!')
        writer = FFMpegWriter(fps=4, metadata=metadata, bitrate = -1)

        f, a = plt.subplots(figsize=(15, 15))

        if self.var == 0:
            var = SE

        # the actual plot
        tc = a.tripcolor(x, y, ikle - 1, var[:, 0], vmin=h_min, vmax=h_max, cmap='ocean')

        # clean axes
        a.axis('off')
        a.set_aspect('equal')

        # create a nice colorbar
        divider = make_axes_locatable(a)
        cax = divider.append_axes("bottom", size="5%", pad=0.05)
        cb = f.colorbar(tc, orientation='horizontal', cax=cax)
        cb.ax.set_title('Water Surface elevation', size=18)
        cb.ax.tick_params(labelsize=18)

        # set axes limits
        if self.lims != None:
            a.set_xlim(self.lims[0], self.lims[1])
            a.set_ylim(self.lims[3], self.lims[2])

        # get axes limits
        ymin, ymax = a.get_ylim()
        yrange = ymax - ymin
        xmin, xmax = a.get_xlim()
        xrange = xmax - xmin

        # scale bar
        rect = matplotlib.patches.Rectangle([xmin + 7/10*xrange, ymin + 1/10*yrange - yrange/28], width=25000, height=yrange/400, facecolor='black')
        a.add_patch(rect)
        a.annotate('25 km', [xmin + 7/10*xrange, ymin + 1/10*yrange - yrange/40], size=10, color='black')
        tim = '%d hrs %d mins' % (0, 0)

        a1 = a.annotate(tim, [xmin + 7/10*xrange, ymin + 1/10*yrange], size=16, color='black')
        rows, cols = np.shape(data[0])

        t0 = time.time()

        if not self.fn.endswith('.mp4'): self.fn + '.mp4'

        with writer.saving(f, self.fn, cols):
            for i in range(cols):

                per = i/cols * 100

                tc.remove()
                a1.remove()
                del tc, a1

                t = times[i]
                hrs = t // 3600
                min = (t % 3600) // 60
                sec = (t % 3600) % 60

                tim = '%d hrs %d mins' % (hrs, min)
                a1 = a.annotate(tim, [xmin + 7/10*xrange, ymin + 1/10*yrange], size=16, color='black')
                tc = a.tripcolor(x, y, ikle - 1, var[:, i], vmin=h_min, vmax=h_max, cmap='ocean')

                dt = time.time() - t0
                estimated_time = dt*(cols - i)
                hrs = estimated_time//3600
                min = estimated_time%3600/60

                self.sig1.emit('Generating video is at %.2f %s and the estimated remaining time is: %.0f hr and %.2f min.' % (i/cols * 100, '%', hrs, min))

                writer.grab_frame()
                t0 = time.time()

        self.sig1.emit('Video is ready and stored at %s!' % output_path)
        dt = time.time()-start_time
        min = dt//60
        sec = dt%60
        print("Writing the video took "+ str(int(min))+ " minutes and "+str(int(sec)) + " seconds.")
