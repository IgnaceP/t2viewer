
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
import urllib
import os
import math
from shutil import copyfile
import pickle
import time
import gc

from load_mesh import *
from paint import Paint
from plot_series import *
from plot_a_video import *

os.chdir('/home/ignace/Custom_Libraries/t2viewer/')
#%%


class MyThread99(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(100):
            time.sleep(0.1)
            self._signal.emit(i)

class Main(QMainWindow):
# create a class with heritance from the QWidget object

    def __init__(self):
        # assign attributes
        super().__init__()
        # return the parent class from this child class and calls its constructor (constructor = special kind of method to initialize any instance variables (assigning attributes to it))

        title = "TELEMAC 2D Output Vizualization"
        top = 50
        left = 50
        width = 1450
        height = 600

        self.clickcount = 0
        self.F = np.zeros([500,500])

        self.setWindowTitle(title)
        self.setGeometry(top,left, width, height)

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
        if event.key() == Qt.Key_Escape:
            self.close()

class MyTableWidget(QWidget):

    sig = pyqtSignal(str)

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        #---------------------------------------------------#
        #-------------- Make the input widges --------------#
        #---------------------------------------------------#

        # Qlabel to show the grid in
        Frame = QLabel()
        Frame.setFixedSize(700,700)

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
        start_time.setAlignment(Qt.AlignRight)
        start_time.setStyleSheet("""
            QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            }""")
        end_time = QLabel('End Date & Time:')
        end_time.setAlignment(Qt.AlignRight)
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

        # Qlabel to paint the selected loc
        self.Painter = Paint(self.X_box, self.Y_box)
        self.Painter.setFixedSize(700,700)

        # Push button to load telemac 2d output
        Plot = QPushButton('Plot water level series')
        Plot.clicked.connect(self.plotTimeSeries)
        Plot.setToolTip('Plot time series of surface elevation at selected area.')
        Plot.setStyleSheet("""
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

        # Push button to load telemac 2d output
        Video = QPushButton('Generate a video')
        Video.clicked.connect(self.plotVideo)
        Video.setToolTip('Generate a video of the water surface elevation over time.')
        Video.setStyleSheet("""
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

        # Qlabel to show the grid in
        self.Mesh = QLabel()
        self.Mesh.setFixedSize(700,700)

        # Qlabel to load graph into
        self.Graph1 = QLabel()
        self.Graph2 = QLabel()


        #------------------------------------------------------#
        #-------------- Connect the input widges --------------#
        #------------------------------------------------------#

        #self.Find.clicked.connect(self.FindLocation)

        #---------------------------------------------------------#
        #-------------- Organize and set the layout --------------#
        #---------------------------------------------------------#

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.Mesh, 0, 0, 10, 1)

        self.grid.addWidget(Load,0,1,1,1)
        self.grid.addWidget(self.Path_label, 0,2,1,3)

        self.grid.addWidget(X_label, 1,1,1,1)
        self.grid.addWidget(Y_label, 2,1,1,1)
        self.grid.addWidget(self.X_box, 1,2,1,1)
        self.grid.addWidget(self.Y_box, 2,2,1,1)

        self.grid.addWidget(start_time, 1, 3)
        self.grid.addWidget(end_time, 2, 3)
        self.grid.addWidget(self.start_time, 1, 4)
        self.grid.addWidget(self.end_time, 2, 4)

        self.grid.addWidget(Plot, 3,1,1,2)
        self.grid.addWidget(Video, 3,3,1,2)
        self.grid.addWidget(self.Graph1,4,1,3,4)
        self.grid.addWidget(self.Graph2,7,1,3,4)

        self.setLayout(self.grid)

        self.show()


        #-------------------------------------#
        #-------------- Methods --------------#
        #-------------------------------------#


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, self.cancel = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Numpy files (*.npy);; Selafin Files (*.slf)", options=options)
        self.Path_label.setText('Loading...')
        print('Loading file...')
        time.sleep(1)
        try:
            self.loadMesh()
            self.Path_label.setText(self.fileName.split('/')[-1])

        except:
            self.Path_label.setText('Something went wrong!')
            print("Unexpected error:", sys.exc_info()[0])

    def loadMesh(self):
        fn, self.box = loadMeshFromSLF(self.fileName)
        print(fn)
        Im = QPixmap(fn)
        Im = Im.scaled(700,700, transformMode = Qt.SmoothTransformation)
        self.Mesh.setPixmap(Im)

        self.Painter.setBox(self.box)
        self.Painter.setStyleSheet("""
        QLabel {
            background-color: transparent;
            }
        """)
        self.grid.addWidget(self.Painter, 0, 0, 10, 1)
        self.setLayout(self.grid)

        self.show()

        self.loadArrays()

    def loadArrays(self):
        fn = str('./previously_loaded_meshes/'+self.fileName.split('/')[-1])
        fn = fn.split('_')[:-1]
        fn = '_'.join(fn)

        self.fn = fn

        data = np.load(fn + '_data.npy')
        t = np.load(fn + '_t.npy')
        X = np.load(fn + '_x.npy')
        Y = np.load(fn + '_y.npy')

        # get properties
        U = data[0]
        V = data[1]
        H = data[2]
        B = data[3]

        self.Vel = np.sqrt(U**2+V**2)
        self.SE = B + H

        self.XY = np.empty([np.shape(X)[0], 2])
        self.XY[:,0], self.XY[:,1] = X, Y

        # time series
        start_date = np.datetime64('2015-01-01T00:00:00')
        T = np.array([start_date], dtype = np.datetime64)
        for i in range(np.shape(t)[0]):
            td = np.timedelta64(int(t[i]),'s')
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
        fn = plotT2Series(T = self.T, XY = self.XY, x = float(self.X_box.text()), y = float(self.Y_box.text()),
                    SE = self.SE, Vel = self.Vel, t0 = start_time, t1 = end_time)

        Im = QPixmap(fn+'_WSE.png')
        Im = Im.scaled(200*15/4,200, transformMode = Qt.SmoothTransformation)
        self.Graph1.clear()
        self.Graph1.setPixmap(Im)

        Im = QPixmap(fn+'_Vel.png')
        Im = Im.scaled(200*15/4,200, transformMode = Qt.SmoothTransformation)
        self.Graph2.clear()
        self.Graph2.setPixmap(Im)

        vars = globals()
        for var in vars:
            if sys.getsizeof(var) > 100:
                print(var+':')
                print(sys.getsizeof(var))
                print('----------')

    def plotVideo(self):
        self.thread = MyThread()
        self.sig.connect(self.thread.on_source)
        self.sig.emit(self.fn)
        self.thread.start()
        self.thread.sig1.connect(self.on_info)

    def on_info(self, info):
        self.Path_label.setText(str(info))



#--------------------------------------------------------------------#
# Execute the program

app = QApplication([])
window = Main()
window.show()
app.exec_()
