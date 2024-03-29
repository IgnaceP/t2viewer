
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
from getNeigh import getNeighbor


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

        self.videosettingschanged = False

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

        # Push button to load telemac 2d output
        self.VideoSettings = QPushButton('Video settings')
        #self.VideoSettings.setDisabled(True)
        self.VideoSettings.clicked.connect(self.setVideoSettings)
        self.VideoSettings.setToolTip('Change the settings of the video export.')
        self.VideoSettings.setStyleSheet("""
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


        # Push button to open dialog to locate a value
        self.LocateValue = QPushButton('Locate value')
        self.LocateValue.setDisabled(True)
        self.LocateValue.clicked.connect(self.locateValue)
        self.LocateValue.setToolTip('Locate a value on the mesh (e.g. maximum h in mangroves).')
        self.LocateValue.setStyleSheet("""
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

        # time series objects
        self.WSE_series = TimeSeries('Water Surface Elevation [m]')
        self.Vel_series = TimeSeries('Water Velocity [m/s]')

        # ----------------------#
        # Main window with mesh #
        # ----------------------#

        # FigureCanvas to show the mesh in
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

        self.addcoor = QPushButton('xy')
        self.addcoor.setEnabled(False)
        self.addcoor.clicked.connect(self.addCoorToMap)
        self.addcoor.setStyleSheet("""
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

        # label to show bathymetry
        self.Station_label = QLabel()
        self.Station_label.setFixedWidth(125)
        self.Station_label.setStyleSheet("""
        QLabel {
            color: rgb(255,128,0);
            font-size: 10pt;
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
        self.grid.addWidget(self.addcoor, 9 , 3, 1, 1)
        self.grid.addWidget(self.homebut, 9, 4, 1, 1)

        self.grid.addWidget(self.Bath_label, 9, 5)
        self.grid.addWidget(self.Station_label, 9, 6)

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
        self.box_buttons.addWidget(self.VideoSettings)
        self.box_buttons.addWidget(self.PlotMesh)
        self.box_buttons.addWidget(self.ReloadMesh)
        self.box_buttons.addWidget(self.LocateValue)
        self.box_buttons.addWidget(self.LoadPrevious)
        self.box_buttons.addWidget(self.RemovePrevious)
        self.box_buttons.addStretch()

        self.grid.addLayout(self.box_buttons, 0, 15, 10, 1)

        self.grid.addWidget(self.WSE_series,3,11,3,4)
        self.grid.addWidget(self.Vel_series,6,11,3,4)

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

        self.name, self.ax, self.tc = loadMeshFromSLF(self.fileName, self.figure, self.canvas, ignore_previously_saved_files = ignore_previously_saved_files, return_tc = True)
        self.canvas.draw()
        self.loadArrays()

        self.zoombut.setEnabled(True)
        self.panbut.setEnabled(True)
        self.locbut.setEnabled(True)
        self.homebut.setEnabled(True)
        self.addcoor.setEnabled(True)

        self.Video.setEnabled(True)
        self.LocateValue.setEnabled(True)
        self.VideoSettings.setEnabled(True)
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
        start_date = np.datetime64('2019-10-07T04:00:00')
        T = np.array([start_date], dtype = np.datetime64)
        for i in range(1,np.shape(self.times)[0]):
            td = np.timedelta64(int(self.times[i]),'s')
            T = np.append(T,start_date + td)
        self.T = T

        start_t = str(self.T[0])
        self.start_time.setText(start_t)

        end_t = str(self.T[-1])
        self.end_time.setText(end_t)

    def plotTimeSeries(self):

        start_time = np.datetime64(self.start_time.text())
        end_time = np.datetime64(self.end_time.text())

        x = float(self.X_box.text())
        y = float(self.Y_box.text())

        X = self.XY[:,0]
        Y = self.XY[:,1]

        # find the closest node to the requested lat and lon
        neighxy= getNeighbor([x, y], self.XY, return_index = False)
        x_node, y_node = neighxy
        rx = np.where(X == x_node)
        ry = np.where(Y == y_node)
        i = np.intersect1d(rx,ry)[0]

        self.WSE_series.plotSeries(T = self.T, var = self.SE[i,:], t0 = start_time, t1 = end_time, x = X[i], y = Y[i])
        self.Vel_series.plotSeries(T = self.T, var = self.Vel[i,:], t0 = start_time, t1 = end_time, x = X[i], y = Y[i])

        self.i = i

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

    def setVideoSettings(self):
        dlg = VideoSettingDialog(self.ax.get_xlim() + self.ax.get_ylim())

        if self.videosettingschanged:
            if self.videolims != None:
                dlg.SetWinLim.setChecked(True)
                dlg.WinLeft.setValue(self.videolims[0])
                dlg.WinRight.setValue(self.videolims[1])
                dlg.WinTop.setValue(self.videolims[2])
                dlg.WinBot.setValue(self.videolims[3])

            dlg.Min.setValue(self.videomin)
            dlg.Max.setValue(self.videomax)

        dlg.exec_( )

        if dlg.good_exit:
            self.videosettingschanged = True
            self.videovar = dlg.var
            self.videomin = dlg.min
            self.videomax = dlg.max
            self.videolims = dlg.lims
            if len(np.unique(self.videolims)) == 1:
                self.videolims = None

    def plotVideo(self):

        if self.videosettingschanged == False:
            self.videovar = 0
            self.videomin = -1
            self.videomax = 5
            self.videolims = None


        options = QFileDialog.Options()
        fn, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)

        if fn:
            self.thread = VideoThread()
            self.sig.connect(self.thread.on_source)
            self.sig.emit([self.fn, fn, [self.videovar, self.videomin, self.videomax, self.videolims]])
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

            self.Station_label.setText('')

    def addCoorToMap(self):
        dlg = AddCoorDialog(None)
        dlg.exec_()

        if dlg.good_exit:
            x = dlg.x
            y = dlg.y

            try: self.scat1.remove()
            except: pass
            self.scat1 = self.ax.scatter(x, y, s = 25, color = (1, 128/255, 0), zorder = 1e9)
            self.canvas.draw()

            self.X_box.setText('%.2f' % x)
            self.Y_box.setText('%.2f' % y)

            self.Station_label.setText(dlg.StationName)

    def plotMeshVar(self):

        dlg = PlotMeshVarDialog(None)
        dlg.time.setRange(0, len(self.times)-1)
        dlg.time.setValue(len(self.times)-1)

        dlg.exec_( )

        if dlg.variable == 1: var = self.U; label_str = 'U [m/s] at timestep %d' % dlg.t
        if dlg.variable == 2: var = self.V; label_str = 'V [m/s] at timestep %d' % dlg.t
        if dlg.variable == 3: var = self.H; label_str = 'Water Depth [m] at timestep %d' % dlg.t
        if dlg.variable == 4: var = self.SE; label_str = 'Water Surface Elevation [m] at timestep %d' % dlg.t
        if dlg.variable == 5: var = self.B; label_str = 'Bathymetry [m] at timestep %d' % dlg.t
        if dlg.variable == 6: var = self.N; label_str = "Manning's n at timestep %d" % dlg.t
        if dlg.variable == 7: var = np.max(self.SE, axis = 1); label_str = "Maximum Water Surface Elevation [m]"
        if dlg.variable == 8: var = np.min(self.SE, axis = 1); label_str = "Maximum Water Surface Elevation [m]"
        if dlg.variable == 9: var = np.max(self.H, axis = 1); label_str = "Minimum Water Depth [m]"
        if dlg.variable == 10: var = np.min(self.H, axis = 1); label_str = "Minimum Water Depth [m]"


        if dlg.variable != None:

            if var.ndim == 2 and dlg.variable < 10: var = var[:,dlg.t]

            if len(dlg.min.text()) == 0 or len(dlg.max.text()) == 0: varmin, varmax = np.min(var),np.max(var)
            else: varmin, varmax = float(dlg.min.text()),float(dlg.max.text())

            self.ax.clear()
            self.figure.clf()
            self.ax = self.figure.add_subplot(111)
            plotVarMesh(self.X, self.Y, self.ikle, var, label_str, min = varmin, max = varmax, ax = self.ax, fig = self.figure, showedges = dlg.showgridedges, showgrid=dlg.showagrid)

            self.canvas.draw()

            self.ReloadMesh.setDisabled(False)
            self.LocateValue.setDisabled(False)

    def locateValue(self):
        dlg = LocateValueDialog(None)
        dlg.exec_( )

        if dlg.variable != None:
            if dlg.var.currentIndex() == 1: var = self.U; unit_str = 'm/s'; var_str = 'u'
            if dlg.var.currentIndex() == 2: var = self.V; unit_str = 'm/s'; var_str = 'v'
            if dlg.var.currentIndex() == 3: var = self.H; unit_str = 'm'; var_str = 'h'
            if dlg.var.currentIndex() == 4: var = self.SE; unit_str = 'm'; var_str = 'SE'

            #if dlg.reducer.currentText() == 'maximum': var = np.max(var, axis = 1)
            #if dlg.reducer.currentText() == 'minimum': var = np.min(var, axis = 1)

            if dlg.constvar.currentIndex() == 0: mask = self.B[:,0]
            if dlg.constvar.currentIndex() == 1: mask = self.N[:,0]

            if dlg.rel.currentText() == '>': mask = (mask < float(dlg.tresh.text()))
            elif dlg.rel.currentText() == '<': mask = (mask > float(dlg.tresh.text()))
            elif dlg.rel.currentText() == '=': mask = (mask == float(dlg.tresh.text()))
            else: print('woops')

            var_masked = var[mask]

            if dlg.reducer.currentText() == 'maximum':m = np.max(var_masked); am = np.where(var == m); lab = ' max '
            if dlg.reducer.currentText() == 'minimum':m = np.min(var_masked); am = np.where(var == m); lab = ' min '
            am = am[0][0]

            x = self.X[am]
            y = self.Y[am]
            self.locval = self.ax.scatter(x,y,s = 60,c = 'aquamarine')
            lab += '%s: %.2f %s' % (var_str, m, unit_str)
            self.loclabel = self.ax.annotate(lab,(x,y),fontsize = 8, c = 'aquamarine', bbox =dict(boxstyle="square", fc="0.1"))
            self.canvas.draw()



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
