
"""
Created on Wed Oct 17 17:20:50 2018

@author: ignace
"""

# programm which asks long and lat and zoom level
#%%

#%%
import sys
import PyQt5.QtCore
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.image as mpimg

import urllib
import os
import math
from shutil import copyfile
import pickle
import time
import gc
import random

from load_mesh import *
from plot_series import *
from plot_a_video import *
from dialogs import *


os.chdir('/home/ignace/Custom_Libraries/t2viewer/')
#%%


class Main(QMainWindow):
# create a class with heritance from the QWidget object

    def __init__(self):
        # assign attributes
        super().__init__()
        # return the parent class from this child class and calls its constructor (constructor = special kind of method to initialize any instance variables (assigning attributes to it))

        title = "TELEMAC 2D Output Vizualization"
        left = 2000
        top = 100
        width = 1750
        height = 600

        self.clickcount = 0
        self.F = np.zeros([500,500])

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('support_files/logo.png'))
        self.setGeometry(left,top,width, height)

        self.main_widget = MyTableWidget(self)
        self.setCentralWidget(self.main_widget)

        self.setStyleSheet("""
        QWidget {
            background-color: rgb(35, 35, 35);
            }
        """)

        self.main_widget.setStyleSheet("""
        QWidget {
            background-color: rgb(45, 45, 45);
            }
        """)

        self.show()

    def keyPressEvent(self, event):
        if self.main_widget.RemovePrevious.isChecked():
            os.system('rm previously_loaded_meshes/*')
        if event.key() == Qt.Key_Escape:
            self.close()

class MyTableWidget(QWidget):

    sig = pyqtSignal(list)
    sigload = pyqtSignal(list)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
        #-------------- Make the input widges --------------#
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

        # ------------------------#
        # Main buttons ans inputs #
        # ------------------------#

        # Push button to load telemac 2d output
        Load = QPushButton('Load .slf or .npy')
        Load.clicked.connect(self.openFileNameDialog)
        Load.setToolTip('Load the output from a TELEMAC 2D simulation')
        Load.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:pressed {
            color: rgb(120,120,120);
            background-color: rgb(75, 75, 80);
            }
        """)
        Load.setFixedWidth(150)

        # label to show the path of the loaded selafin file
        self.Path_label = QLabel()
        self.Path_label.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        # Spin box for X
        X_label = QLabel('X-coordinate:')
        X_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        X_label.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            }
        """)
        Y_label = QLabel('Y-coordinate:')
        Y_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        Y_label.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            }
        """)

        # Spin box for Y
        self.X_box = QLabel(' ')
        self.X_box.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            max-height: 30px;
            min-width: 160px;
            }
        """)
        self.Y_box = QLabel(' ')
        self.Y_box.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            max-height: 30px;
            min-width: 160px;
            }
        """)

        # date and time
        start_time = QLabel('Start Date & Time:')
        start_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        start_time.setStyleSheet("""
            QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            }""")
        end_time = QLabel('End Date & Time:')
        end_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        end_time.setStyleSheet("""
            QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            }""")

        self.start_time = QLineEdit()
        self.start_time.setStyleSheet("""
        QLineEdit {
        color: rgb(180,180,180);
        background-color: rgb(25,25,25);
        }""")
        self.end_time = QLineEdit()
        self.end_time.setStyleSheet("""
        QLineEdit {
        color: rgb(180,180,180);
        background-color: rgb(25,25,25);
        }""")

        # Push button to load telemac 2d output
        self.PlotSeries = QPushButton('Plot Series')
        self.PlotSeries.setDisabled(True)
        self.PlotSeries.clicked.connect(self.plotTimeSeries)
        self.PlotSeries.setToolTip('Plot time series of surface elevation at selected area.')
        self.PlotSeries.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:pressed {
            color: rgb(120,120,120);
            background-color: rgb(75, 75, 80);
            }
        QPushButton:disabled {
            color: rgb(50,50,50);
            background-color: rgb(25, 25, 25);
            }
        """)

        # Push button to load telemac 2d output
        self.Video = QPushButton('Generate a video')
        self.Video.setDisabled(True)
        self.Video.clicked.connect(self.plotVideo)
        self.Video.setToolTip('Generate a video of the water surface elevation over time.')
        self.Video.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:pressed {
            color: rgb(120,120,120);
            background-color: rgb(75, 75, 80);
            }
        QPushButton:disabled {
            color: rgb(50,50,50);
            background-color: rgb(25, 25, 25);
            }
        """)

        # Push button to plot a variable along the mesh
        self.PlotMesh = QPushButton('Plot variable on mesh')
        self.PlotMesh.setDisabled(True)
        self.PlotMesh.clicked.connect(self.plotMeshVar)
        self.PlotMesh.setToolTip('Generate a map with a given variable.')
        self.PlotMesh.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:pressed {
            color: rgb(120,120,120);
            background-color: rgb(75, 75, 80);
            }
        QPushButton:disabled {
            color: rgb(50,50,50);
            background-color: rgb(25, 25, 25);
            }
        """)

        # Push button to reload general mesh view
        self.ReloadMesh = QPushButton('Reload mesh view')
        self.ReloadMesh.setDisabled(True)
        self.ReloadMesh.clicked.connect(self.reloadMesh)
        self.ReloadMesh.setToolTip('Reload the general mesh view.')
        self.ReloadMesh.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:pressed {
            color: rgb(120,120,120);
            background-color: rgb(75, 75, 80);
            }
        QPushButton:disabled {
            color: rgb(50,50,50);
            background-color: rgb(25, 25, 25);
            }
        """)




        self.LoadPrevious = QCheckBox('Ignore previously saved meshes')
        self.LoadPrevious.setChecked(True)
        self.LoadPrevious.setToolTip('Ignore existing files in previously_loaded_meshes and copy loaded files to this directory.')
        self.LoadPrevious.setStyleSheet("""
        QCheckBox {
         color: rgb(120,120,120);
         background-color: rgb(35,35,35);
        }
        """)

        self.RemovePrevious = QCheckBox('Clear previously saved meshes')
        self.RemovePrevious.setChecked(True)
        self.RemovePrevious.setToolTip('Clear all files tores in previously_loaded_meshes when closing.')
        self.RemovePrevious.setStyleSheet("""
        QCheckBox {
         color: rgb(120,120,120);
         background-color: rgb(35,35,35);
        }
        """)

        # ------------#
        # Time Series #
        # ------------#

        # Qlabel to load graph into
        self.Graph1 = QLabel()
        self.Graph2 = QLabel()

        # ----------------------#
        # Main window with mesh #
        # ----------------------#

        # Qlabel to show the mesh in
        self.figure = plt.figure()
        self.figure.set_facecolor((45/255, 45/255, 45/255))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(700,700)

        # buttons to zoom and pan
        self.zoombut = QPushButton()
        self.zoombut.setCheckable(True)
        self.zoombut.setEnabled(False)
        im = QIcon('support_files/zoom.png')
        self.zoombut.setIcon(im)
        self.zoombut.clicked.connect(self.zoom)
        self.zoombut.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:checked {
            color: rgb(25,25,25);
            background-color: rgb(255, 128, 0);
            }
        """)

        self.panbut = QPushButton()
        self.panbut.setCheckable(True)
        self.panbut.setEnabled(False)
        im = QIcon('support_files/pan.png')
        self.panbut.setIcon(im)
        self.panbut.clicked.connect(self.pan)
        self.panbut.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:checked {
            color: rgb(25,25,25);
            background-color: rgb(255, 128, 0);
            }
        """)

        self.locbut = QPushButton()
        self.locbut.setCheckable(True)
        self.locbut.setEnabled(False)
        im = QIcon('support_files/loc.png')
        self.locbut.setIcon(im)
        self.locbut.clicked.connect(self.loc)
        self.locbut.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:checked {
            color: rgb(25,25,25);
            background-color: rgb(255, 128, 0);
            }
        """)
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.record_pressing_event = False

        self.homebut = QPushButton()
        self.homebut.setEnabled(False)
        im = QIcon('support_files/home.png')
        self.homebut.setIcon(im)
        self.homebut.clicked.connect(self.home)
        self.homebut.setStyleSheet("""
        QPushButton {
            border-width: 25px solid white;
            border-radius: 5px;
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
            min-height: 40px;
            }
        QPushButton:pressed {
            color: rgb(120,120,120);
            background-color: rgb(75, 75, 80);
            }
        """)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()


        # label to show bathymetry
        self.Bath_label = QLabel()
        self.Bath_label.setFixedWidth(125)
        self.Bath_label.setStyleSheet("""
        QLabel {
            color: rgb(255,128,0);
            font-size: 8pt;
            background-color: rgb(35, 35, 35);
            }
        """)



        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
        #-------------- Organize and set the layout --------------#
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.canvas, 0, 0, 9, 10)
        self.grid.addWidget(self.zoombut, 9, 0, 1, 1)
        self.grid.addWidget(self.panbut, 9, 1, 1, 1)
        self.grid.addWidget(self.locbut, 9, 2, 1, 1)
        self.grid.addWidget(self.homebut, 9, 3, 1, 1)

        self.grid.addWidget(self.Bath_label, 9, 4)

        self.grid.addWidget(Load,0,11,1,1)
        self.grid.addWidget(self.Path_label, 0,12,1,3)

        self.grid.addWidget(X_label, 1,11,1,1)
        self.grid.addWidget(Y_label, 2,11,1,1)
        self.grid.addWidget(self.X_box, 1,12,1,1)
        self.grid.addWidget(self.Y_box, 2,12,1,1)

        self.grid.addWidget(start_time, 1, 13)
        self.grid.addWidget(end_time, 2, 13)
        self.grid.addWidget(self.start_time, 1, 14)
        self.grid.addWidget(self.end_time, 2, 14)

        self.box_buttons = QVBoxLayout()
        self.box_buttons.addWidget(self.PlotSeries)
        self.box_buttons.addWidget(self.Video)
        self.box_buttons.addWidget(self.PlotMesh)
        self.box_buttons.addWidget(self.ReloadMesh)
        self.box_buttons.addWidget(self.LoadPrevious)
        self.box_buttons.addWidget(self.RemovePrevious)
        self.box_buttons.addStretch()

        self.grid.addLayout(self.box_buttons, 0, 15, 10, 1)

        self.grid.addWidget(self.Graph1,3,11,3,4)
        self.grid.addWidget(self.Graph2,6,11,3,4)

        self.setLayout(self.grid)

        self.show()

        #-------------------------------------#
        #-------------- Methods --------------#
        #-------------------------------------#


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, self.cancel = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Numpy files (*.npy);; Selafin Files (*.slf)", options=options)
        print('Loading file...')

        try:
            self.loadMesh()
            self.Path_label.setText(self.fileName.split('/')[-1])

        except:
            self.Path_label.setText('Something went wrong!')
            print("Unexpected error:", sys.exc_info()[0])

    def loadMesh(self):

        if self.LoadPrevious.isChecked(): ignore_previously_saved_files = True
        else : ignore_previously_saved_files = False

        self.name, self.ax = loadMeshFromSLF(self.fileName, self.figure, self.canvas, ignore_previously_saved_files = ignore_previously_saved_files)
        self.canvas.draw()
        self.loadArrays()

        self.zoombut.setEnabled(True)
        self.panbut.setEnabled(True)
        self.locbut.setEnabled(True)
        self.homebut.setEnabled(True)

        self.Video.setEnabled(True)
        self.PlotSeries.setEnabled(True)
        self.PlotMesh.setEnabled(True)


    def loadArrays(self):
        fn = str('./previously_loaded_meshes/'+self.name)
        self.fn = fn

        data = np.load(fn + '_data.npy')
        X = np.load(fn + '_x.npy')
        Y = np.load(fn + '_y.npy')
        self.ikle = np.load(fn + '_ikle.npy')
        self.times = np.load(fn + '_times.npy')

        # get properties
        U = data[0]
        V = data[1]
        H = data[2]
        B = data[3]
        N = data[4]

        self.U = U
        self.V = V
        self.Vel = np.sqrt(U**2+V**2)
        self.H = H
        self.SE = H+B
        self.B = B
        self.N = N
        self.X = X
        self.Y = Y

        self.XY = np.empty([np.shape(X)[0], 2])
        self.XY[:,0], self.XY[:,1] = X, Y

        # time series
        start_date = np.datetime64('2015-01-01T00:00:00')
        T = np.array([start_date], dtype = np.datetime64)
        for i in range(np.shape(self.times)[0]):
            td = np.timedelta64(int(self.times[i]),'s')
            T = np.append(T,start_date + td)
        self.T = T[1:]

        start_t = str(self.T[0])
        self.start_time.setText(start_t)

        end_t = str(self.T[-1])
        self.end_time.setText(end_t)

    def plotTimeSeries(self):
        start_time = np.datetime64(self.start_time.text())
        end_time = np.datetime64(self.end_time.text())

        fn = './previously_loaded_meshes/'+self.fileName.split('/')[-1].split('.')[0]
        fn, neighxy, i = plotT2Series(T = self.T, XY = self.XY, x = float(self.X_box.text()), y = float(self.Y_box.text()),
                    SE = self.SE, Vel = self.Vel, t0 = start_time, t1 = end_time)

        Im = QPixmap(fn+'_WSE.png')
        Im = Im.scaled(200*15/4,200, transformMode = Qt.SmoothTransformation)
        self.Graph1.clear()
        self.Graph1.setPixmap(Im)

        Im = QPixmap(fn+'_Vel.png')
        Im = Im.scaled(200*15/4,200, transformMode = Qt.SmoothTransformation)
        self.Graph2.clear()
        self.Graph2.setPixmap(Im)

        try: self.scat2.remove()
        except: pass
        self.scat2 = self.ax.scatter(neighxy[0], neighxy[1], s = 25, color = (1, 1, 1, 0), edgecolor = (1, 128/255, 0), zorder = 1e9)
        self.canvas.draw()

        self.X_box.setText('%.2f' % neighxy[0])
        self.Y_box.setText('%.2f' % neighxy[1])
        self.X_box.setStyleSheet("""
        QLabel {
            color: rgb(255,128,0);
            background-color: rgb(35, 35, 35);
            max-height: 30px;
            min-width: 160px;
            }
        """)
        self.Y_box.setStyleSheet("""
        QLabel {
            color: rgb(255,128,0);
            background-color: rgb(35, 35, 35);
            max-height: 30px;
            min-width: 160px;
            }
        """)

        bath_str = '%.2f' % self.B[i,0]
        frict_str = '%.3f' % self.N[i,0]
        i_str = str(i)
        self.Bath_label.setText('Bath: ' + bath_str + " m\nManning's n: " + frict_str + '\nIndex: ' + i_str)



    def plotVideo(self):
        options = QFileDialog.Options()
        fn, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)

        if fn:
            self.thread = VideoThread()
            self.sig.connect(self.thread.on_source)
            self.sig.emit([self.fn, fn])
            self.thread.start()
            self.thread.sig1.connect(self.on_info)

    def on_info(self, info):
        self.Path_label.setText(str(info))

    def home(self):
        self.toolbar.home()

    def zoom(self):
        self.panbut.setChecked(False)
        self.locbut.setChecked(False)
        if self.zoombut.isChecked():
            self.toolbar.zoom()
            self.record_pressing_event = False

    def pan(self):
        self.zoombut.setChecked(False)
        self.locbut.setChecked(False)
        if self.panbut.isChecked():
            self.toolbar.pan()
            self.record_pressing_event = False

    def loc(self):
        self.zoombut.setChecked(False)
        self.panbut.setChecked(False)
        if self.toolbar._active == "PAN":
            self.toolbar.pan()
        elif self.toolbar._active == "ZOOM":
            self.toolbar.zoom()
        if self.locbut.isChecked(): self.record_pressing_event = True
        else: self.record_pressing_event = False

    def on_press(self, event):
        if self.record_pressing_event:
            self.X_box.setText('%.2f' % event.xdata)
            self.Y_box.setText('%.2f' % event.ydata)

            self.X_box.setStyleSheet("""
            QLabel {
                color: rgb(180,180,180);
                background-color: rgb(35, 35, 35);
                max-height: 30px;
                min-width: 160px;
                }
            """)
            self.Y_box.setStyleSheet("""
            QLabel {
                color: rgb(180,180,180);
                background-color: rgb(35, 35, 35);
                max-height: 30px;
                min-width: 160px;
                }
            """)


            try: self.scat1.remove()
            except: pass
            self.scat1 = self.ax.scatter(event.xdata, event.ydata, s = 25, color = (1, 128/255, 0), zorder = 1e9)
            self.canvas.draw()

    def plotMeshVar(self):

        dlg = PlotMeshVarDialog(None)
        dlg.var.addItems(['u (m/s)', 'v (m/s)','water depth (m)','water surface (m)','Bathymetry (m)', 'Friction Coefficient'])
        dlg.time.setRange(0, len(self.times)-1)
        dlg.time.setValue(len(self.times)-1)

        dlg.exec_( )

        if dlg.variable == 1: var = self.U[:,dlg.t]; label_str = 'U [m/s]'
        if dlg.variable == 2: var = self.V[:,dlg.t]; label_str = 'V [m/s]'
        if dlg.variable == 3: var = self.H[:,dlg.t]; label_str = 'Water Depth [m]'
        if dlg.variable == 4: var = self.SE[:,dlg.t]; label_str = 'Water Surface Elevation [m]'
        if dlg.variable == 5: var = self.B[:,dlg.t]; label_str = 'Bathymetry [m]'
        if dlg.variable == 6: var = self.N[:,dlg.t]; label_str = "Manning's n"

        if dlg.variable != None:

            if len(dlg.min.text()) == 0 or len(dlg.max.text()) == 0: varmin, varmax = np.min(var),np.max(var)
            else: varmin, varmax = float(dlg.min.text()),float(dlg.max.text())

            #self.ax.clear()
            self.figure.clf()
            self.ax = self.figure.add_subplot(111)
            plotVarMesh(self.X, self.Y, self.ikle, var, label_str, min = varmin, max = varmax, ax = self.ax, fig = self.figure)
            self.canvas.draw()

            """
            options = QFileDialog.Options()
            fn, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)

try:
    self.figure.cb.clear()
            if fn:
                if fn[-4:] != '.png': fn += '.png'
                self.ax.clear()
                plotVarMesh(self.X, self.Y, self.ikle, var, fn, label_str, min = float(dlg.min.text()), max = float(dlg.max.text()), ax = self.ax, fig = self.figure)
                self.canvas.draw()
            """

            self.ReloadMesh.setDisabled(False)

    def reloadMesh(self):
        self.ax.clear()
        self.ax = plotMesh(self.name, self.figure)
        self.canvas.draw()
        self.ReloadMesh.setDisabled(True)






#--------------------------------------------------------------------#
# Execute the program

app = QApplication([])
window = Main()
window.show()
app.exec_()
