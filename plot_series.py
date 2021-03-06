import numpy as np
from getNeigh import getNeighbor
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.image as mpimg
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



class TimeSeries(QWidget):
        def __init__(self, label, parent = None):
            super(TimeSeries, self).__init__(parent)

            self.label = label

            self.init()
            self.implementGrid()

            self.new_series = []
            self.new_series_labels = []

        def init(self):
            # FigureCanvas to show the mesh in
            self.figure = plt.figure()
            self.figure.set_facecolor((45/255, 45/255, 45/255))
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setFixedSize(750,276)

            self.figure.subplots_adjust(left = 0.1, right = 0.94, bottom = 0.1, top = 0.9)
            self.ax = self.figure.add_subplot(111)
            self.ax.set_xlim(0,1.25)
            self.ax.set_facecolor((45/255, 45/255, 45/255))

            broken_white = (150/255, 150/255, 150/255)
            self.ax.grid('on', color = broken_white)
            self.ax.spines['bottom'].set_color(broken_white)
            self.ax.spines['top'].set_color(broken_white)
            self.ax.spines['right'].set_color(broken_white)
            self.ax.spines['left'].set_color(broken_white)
            self.ax.tick_params(axis='x', colors=broken_white, labelsize = 7)
            self.ax.tick_params(axis='y', colors=broken_white, labelsize = 7)
            self.ax.xaxis.label.set_color(broken_white)
            self.ax.yaxis.label.set_color(broken_white)

            self.ax.set_ylabel(self.label, fontweight = 'bold', fontsize = 9)

            self.Export = QPushButton()
            self.Export.setToolTip('Export graph as PNG')
            im = QIcon('support_files/export.png')
            self.Export.setIcon(im)
            self.Export.setDisabled(True)
            self.Export.clicked.connect(self.exportGraph)
            self.Export.setStyleSheet("""
            QPushButton {
                border-width: 25px solid white;
                border-radius: 0px;
                color: rgb(180,180,180);
                background-color: rgb(55, 55, 60, 0);
                }
            QPushButton:pressed {
                color: rgb(100,100,100,150);
                background-color: rgb(25, 25, 25, 150);
                }
            """)

            self.AddExtSeries = QPushButton()
            self.AddExtSeries.setToolTip('Add a series from a npy file')
            im = QIcon('support_files/add.png')
            self.AddExtSeries.setIcon(im)
            self.AddExtSeries.setDisabled(True)
            self.AddExtSeries.clicked.connect(self.addExtraSeries)
            self.AddExtSeries.setStyleSheet("""
            QPushButton {
                border-width: 25px solid white;
                border-radius: 0px;
                color: rgb(180,180,180);
                background-color: rgb(55, 55, 60, 0);
                }
            QPushButton:pressed {
                color: rgb(100,100,100,150);
                background-color: rgb(25, 25, 25, 150);
                }
            """)

            self.SaveNPY = QPushButton()
            self.SaveNPY.setToolTip('Save the series in a numpy array file (.npy)')
            im = QIcon('support_files/save_npy.png')
            self.SaveNPY.setIcon(im)
            self.SaveNPY.setDisabled(True)
            self.SaveNPY.clicked.connect(self.saveNPY)
            self.SaveNPY.setStyleSheet("""
            QPushButton {
                border-width: 25px solid white;
                border-radius: 0px;
                color: rgb(180,180,180);
                background-color: rgb(55, 55, 60, 0);
                }
            QPushButton:pressed {
                color: rgb(100,100,100,150);
                background-color: rgb(25, 25, 25, 150);
                }
            """)

            # buttons to zoom and pan
            self.zoombut = QPushButton()
            self.zoombut.setCheckable(True)
            self.zoombut.setEnabled(False)
            im = QIcon('support_files/zoom_trans.png')
            self.zoombut.setIcon(im)
            self.zoombut.setDisabled(True)
            self.zoombut.clicked.connect(self.zoom)
            self.zoombut.setStyleSheet("""
            QPushButton {
                border-width: 25px solid white;
                border-radius: 0px;
                color: rgb(180,180,180);
                background-color: rgb(55, 55, 60, 0);
                }
            QPushButton:checked {
                color: rgb(100,100,100,150);
                background-color: rgb(255, 128, 0);
                }
            """)

            self.homebut = QPushButton()
            self.homebut.setEnabled(False)
            im = QIcon('support_files/home_trans.png')
            self.homebut.setIcon(im)
            self.homebut.setDisabled(True)
            self.homebut.clicked.connect(self.home)
            self.homebut.setStyleSheet("""
            QPushButton {
                border-width: 25px solid white;
                border-radius: 0px;
                color: rgb(180,180,180,50);
                background-color: rgb(25, 25, 60, 0);
                }
            QPushButton:pressed {
                color: rgb(100,100,100,150);
                background-color: rgb(255, 128, 0);
                }
            """)

            self.toolbar = NavigationToolbar(self.canvas, self)
            self.toolbar.hide()

        def implementGrid(self):
            grid = QGridLayout()
            grid.addWidget(self.canvas,0,0)

            box1 = QVBoxLayout()
            box1.addSpacing(30)
            box1.addWidget(self.Export)
            box1.addWidget(self.AddExtSeries)
            box1.addWidget(self.SaveNPY)
            box1.addStretch()
            box1.addWidget(self.zoombut)
            box1.addWidget(self.homebut)
            box1.addWidget(QLabel())

            box2 = QHBoxLayout()
            box2.addStretch()
            box2.addLayout(box1)
            box2.addSpacing(15)
            grid.addLayout(box2,0,0)

            self.setLayout(grid)

        def plotSeries(self, T, var, t0, t1, x, y):

            self.Export.setEnabled(True)
            self.AddExtSeries.setEnabled(True)
            self.SaveNPY.setEnabled(True)
            self.zoombut.setEnabled(True)
            self.homebut.setEnabled(True)
            self.new_series = []
            self.new_series_labels = []

            self.x, self.y = x, y
            self.T = T
            self.var = var
            self.t0 = t0
            self.t1 = t1

            mask = (T>t0)*(T<t1)
            self.mask = mask
            self.varmin = np.min(var[mask])
            self.varmax = np.max(var[mask])
            self.varrange = self.varmax - self.varmin

            self.ax.set_xlim(t0,t1)

            self.ax.clear()
            self.ax.grid('on')
            self.ax.plot(T, var,'.-', color = (1, 128/255, 0), label = 'active output')
            self.ax.set_ylim(max(-999,self.varmin - 0.1*self.varrange), min(999,self.varmax + 0.1*self.varrange))
            self.ax.set_ylabel(self.label, fontweight = 'bold', fontsize = 9)
            self.canvas.draw()

        def exportGraph(self):
            lab = 'x: %d, y: %d' % (self.x, self.y)
            fn, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;PNG Files (*.png)", options=QFileDialog.Options())

            if len(fn) > 0:
                f, a = plt.subplots(figsize = (15,4))
                f.subplots_adjust(left = 0.1, right = 0.94, bottom = 0.1, top = 0.9)
                a.plot(self.T, self.var,'.-', color = (1, 128/255, 0), label = lab)
                a.grid('on')
                a.set_ylabel(self.label, fontweight = 'bold', fontsize = 11)
                a.set_xlim(self.t0,self.t1)
                a.set_ylim(max(-999,self.varmin - 0.1*self.varrange), min(999,self.varmax + 0.1*self.varrange))

                for i in range(len(self.new_series)):
                    series = self.new_series[i]
                    lab = self.new_series_labels[i]
                    T = np.array(series[:,0], dtype = 'datetime64')
                    V = series[:,1]
                    a.plot(T, V, '.-', label = lab)

                a.set_ylim(max(-999,self.varmin - 0.1*self.varrange), min(999,self.varmax + 0.1*self.varrange))
                a.legend(loc = 1)
                f.savefig(fn)
                f.clear()

        def saveNPY(self):
            fn, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Numpy Files (*.npy)", options=QFileDialog.Options())

            if len(fn) > 0:
                if fn[-4:] != '.npy': fn + '.npy'
                T = self.T - np.timedelta64(3600,'s')
                var = self.var
                arr = np.empty((T.shape[0], 2))
                arr[:,0] = T
                arr[:,1] = var

                np.save(fn, arr)

        def addExtraSeries(self):
            options = QFileDialog.Options()
            fn, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Numpy files (*.npy)", options=options)

            if len(fn) > 0:
                arr = np.load(fn)
                if arr.shape[1] != 2:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Not a valid numpy file. This array does not have two columns.")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

                else:
                    self.new_series.append(arr)
                    lab = fn.split('/')[-1][:-4].replace('_',' ')
                    self.new_series_labels.append(lab)
                    T = np.array(arr[:,0], dtype = 'datetime64') + np.timedelta64(3600,'s')
                    self.ax.plot(T, arr[:,1], '.-', label = lab, scalex = False, scaley = False)
                    self.ax.legend(loc = 1)
                    self.varmin = np.min([self.varmin, np.min(arr[:,1])])
                    self.varmax = np.max([self.varmax, np.max(arr[:,1])])
                    self.varrange = abs(self.varmax - self.varmin)
                    #self.ax.set_ylim(max(-999,self.varmin - 0.1*self.varrange), min(999,self.varmax + 0.1*self.varrange))
                    self.canvas.draw()

        def home(self):
            self.toolbar.home()

        def zoom(self):
            if self.zoombut.isChecked():
                self.toolbar.zoom()
                self.record_pressing_event = False
            else:
                self.toolbar.zoom(False)



###########################################################################################################################################################################################################
def plotVarMesh(x,y,ikle,var, label_str, title_str = '', path = None, min = 0, max = 1e9, ax = None, fig = None, showedges = True, showgrid = True):

    # ------------------------------------------------------------------------------ #
    # Plot the Mesh

    xmin, xmax = np.min(x),np.max(x)
    ymin, ymax = np.min(y),np.max(y)

    if ax == None:
        fig, ax = plt.subplots(figsize = (12,12))
    plt.tight_layout()
    ax.cla()

    if showedges:
        tc = ax.tripcolor(x, y, ikle-1, var, vmin = min, vmax = max, cmap = 'gist_earth', ec = 'white', linewidth = 0.025)
    else:
        tc = ax.tripcolor(x, y, ikle-1, var, vmin = min, vmax = max, cmap = 'gist_earth')

    ax.axis('off')
    ax.margins(2)
    ax.set_xlim(xmin - 0.05*(xmax - xmin), xmax + 0.05*(xmax - xmin))
    ax.set_ylim(ymin - 0.05*(ymax - ymin), ymax + 0.05*(ymax - ymin))
    ax.set_aspect('equal')

    if len(title_str) > 0:
        ax.set_title(title_str, color = 'white')

    if showgrid:
        ax.axis('on')
        ax.tick_params(axis='x', colors='white', labelsize = 7, top = True, bottom = False, labeltop = True)
        ax.tick_params(axis='y', colors='white', labelsize = 7)
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.set_facecolor((45/255, 45/255, 45/255))
        ax.grid('on', color = 'white')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.05)
    cb = fig.colorbar(tc, orientation = 'horizontal', cax = cax)
    cb.ax.set_title(label_str,size = 10, color = 'white')
    cb.ax.tick_params(labelsize=8, color = 'white', labelcolor = 'white')

    if path != None:
        fig.savefig(path)
        os.system('nomacs %s' % path)
