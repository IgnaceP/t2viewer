
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

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        #---------------------------------------------------#
        #-------------- Make the input widges --------------#
        #---------------------------------------------------#

        # Qlabel to show the grid in
        Frame = QLabel()
        Frame.setFixedSize(700,700)

        # Push button to load telemac 2d output
        Load = QPushButton('Load Selafin file')
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
            }
        """)
        self.Y_box = QLabel(' ')
        self.Y_box.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            background-color: rgb(35, 35, 35);
            max-height: 30px;
            }
        """)

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
        self.grid.addWidget(self.Path_label, 0,2,1,1)

        self.grid.addWidget(X_label, 1,1,1,1)
        self.grid.addWidget(Y_label, 2,1,1,1)
        self.grid.addWidget(self.X_box, 1,2,1,1)
        self.grid.addWidget(self.Y_box, 2,2,1,1)

        self.grid.addWidget(Plot, 3,1,1,2)
        self.grid.addWidget(self.Graph1,4,1,3,2)
        self.grid.addWidget(self.Graph2,7,1,3,2)

        self.setLayout(self.grid)

        self.show()


        #-------------------------------------#
        #-------------- Methods --------------#
        #-------------------------------------#


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, self.cancel = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Selafin Files (*.slf)", options=options)
        self.loadMesh()
        try:

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

    def plotTimeSeries(self):
        fn = './previously_loaded_meshes/'+self.fileName.split('/')[-1].split('.')[0]
        fn = plotT2Series(fn, x = float(self.X_box.text()), y = float(self.Y_box.text()))
        Im = QPixmap(fn+'_WSE.png')
        Im = Im.scaled(200*15/4,200, transformMode = Qt.SmoothTransformation)
        self.Graph1.setPixmap(Im)
        Im = QPixmap(fn+'_Vel.png')
        Im = Im.scaled(200*15/4,200, transformMode = Qt.SmoothTransformation)
        self.Graph2.setPixmap(Im)




#--------------------------------------------------------------------#
# Execute the program

app = QApplication([])
window = Main()
window.show()
app.exec_()
