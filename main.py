
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

from load_mesh import *
from paint import Paint
from plot_series import *

#%%
class Main(QMainWindow):
# create a class with heritance from the QWidget object

    def __init__(self):
        # assign attributes
        super().__init__()
        # return the parent class from this child class and calls its constructor (constructor = special kind of method to initialize any instance variables (assigning attributes to it))

        title = "Draw Study Area"
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

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        #---------------------------------------------------#
        #-------------- Make the input widges --------------#
        #---------------------------------------------------#

        # Qlabel to show the grid in
        Frame = QLabel()
        Im = QPixmap("./support_files/Frame.png")
        Im = Im.scaled(700,700)
        Frame.setPixmap(Im)

        # Qlabel to show the grid in
        self.Mesh = QLabel()

        # Push button to load telemac 2d output
        Load = QPushButton(self)
        Load.clicked.connect(self.openFileNameDialog)
        Load.setIcon(QIcon('./support_files/Load.png'))
        Load.setIconSize(QSize(30,30))
        Load.setToolTip('Load the output from a TELEMAC 2D simulation')

        # label to show the path of the loaded selafin file
        self.Path_label = QLabel()

        # Spin box for X
        X_label = QLabel('X-coordinate:')
        Y_label = QLabel('Y-coordinate:')
        # Spin box for Y
        self.X_box = QDoubleSpinBox()
        self.X_box.setRange(0,1e9)
        self.X_box.setDecimals(2)
        self.X_box.setReadOnly(True)
        self.Y_box = QDoubleSpinBox()
        self.Y_box.setRange(0,1e9)
        self.Y_box.setDecimals(2)
        self.Y_box.setReadOnly(True)


        # Qlabel to paint the selected loc
        self.Painter = Paint(self.X_box, self.Y_box)
        self.Painter.setFixedSize(700,700)

        # Push button to load telemac 2d output
        Plot = QPushButton(self)
        Plot.clicked.connect(self.plotTimeSeries)
        Plot.setIcon(QIcon('./support_files/Plot.png'))
        Plot.setIconSize(QSize(30,30))
        Plot.setToolTip('Plot time series of surface elevation at selected area.')

        # Qlabel to load graph into
        self.Graph = QLabel()


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
        self.grid.addWidget(Frame, 0, 0, 10, 1)

        self.grid.addWidget(Load,0,1,1,1)
        self.grid.addWidget(self.Path_label, 0,2,1,1)

        self.grid.addWidget(X_label, 1,1,1,1)
        self.grid.addWidget(Y_label, 2,1,1,1)
        self.grid.addWidget(self.X_box, 1,2,1,1)
        self.grid.addWidget(self.Y_box, 2,2,1,1)

        self.grid.addWidget(Plot, 3,1,1,2)
        self.grid.addWidget(self.Graph,4,1,5,2)

        self.setLayout(self.grid)

        self.show()


        #-------------------------------------#
        #-------------- Methods --------------#
        #-------------------------------------#


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, self.cancel = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Selafin Files (*.slf)", options=options)

        try:
            self.loadMesh()
            self.Path_label.setText(self.fileName.split('/')[-1])

        except:
            self.Path_label.setText('Something went wrong!')
            print("Unexpected error:", sys.exc_info()[0])

    def loadMesh(self):
        fn, self.box = loadMeshFromSLF(self.fileName)
        Im = QPixmap(fn)
        Im = Im.scaled(700,700, transformMode = Qt.SmoothTransformation)
        self.Mesh.setPixmap(Im)

        self.Painter.setBox(self.box)
        self.grid.addWidget(self.Painter, 0, 0, 10, 1)
        self.setLayout(self.grid)

        self.show()

    def plotTimeSeries(self):
        fn = './previously_loaded_meshes/'+self.fileName.split('/')[-1].split('.')[0]
        fn = plotT2Series(fn, x = int(self.X_box.value()), y = int(self.Y_box.value()))
        Im = QPixmap(fn)
        Im = Im.scaled(350*15/7,350, transformMode = Qt.SmoothTransformation)
        self.Graph.setPixmap(Im)




#--------------------------------------------------------------------#
# Execute the program

app = QApplication([])
window = Main()
window.show()
app.exec_()
