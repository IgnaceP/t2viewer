My Drive
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 17:20:50 2018

@author: ignace
"""

# programm which asks long and lat and zoom level
#%%
import os
os.chdir('/Users/ignace/Google Drive/IUPWARE - Thesis/Files')
os.getcwd()


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

import matplotlib
matplotlib.use('TkAgg')


#%%
from Painter import Paint
from Painter import Show_Zoom
from GoogleMapsFinder import GoogleMapDownloader
from Inf_fixed import Infiltration_100m
from Inf_table import Table_inf
from Beerkan import Infiltration_Beerkan
from Table_fixed_inf import Table_infiltration_list
from Geometry import Geometry_list



#%%
class Main(QMainWindow):
# create a class with heritance from the QWidget object

    def __init__(self):
        # assign attributes
        super().__init__()
        # return the parent class from this child class and calls its constructor (constructor = special kind of method to initialize any instance variables (assigning attributes to it))

        title = "Draw Study Area"
        top = 400
        left = 400
        width = 900
        height = 500

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

        self.layout = QVBoxLayout(self)

        #---------------------------------------------#
        #-------------- iniate the tabs --------------#
        #---------------------------------------------#


        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1,"Location and Geometry")
        self.tabs.addTab(self.tab2,"Infiltration")

        #----------------------------------------------------------#
        #-------------- TAB 1: Location and Geometry --------------#
        #----------------------------------------------------------#


        ##########################
        ### make input widgets ###
        ##########################


        LatLabel = QLabel("Latitude:",self)
        self.Lat = QDoubleSpinBox()
        self.Lat.setDecimals(6)
        self.Lat.setRange(-90,90)
        self.Lat.setSuffix(" °")

        LongLabel = QLabel("Longitude:",self)
        self.Long = QDoubleSpinBox()
        self.Long.setDecimals(6)
        self.Long.setRange(-180,180)
        self.Long.setSuffix(" °")

        ZoomLabel = QLabel("Zoom Level:  ",self)
        self.Zoom = QSlider(Qt.Horizontal, self)
        self.Zoom.setRange(15,21)

        self.Find = QPushButton("Find Location")
        self.Find.setFixedWidth(240)

        self.map = QLabel(self)


        self.paint = Paint()
        self.paint.setFixedSize(550,500)
        self.Zoom_lab = Show_Zoom(self.Zoom.value())
        self.Zoom_lab.setFixedSize(550,500)

        self.count_Zoom = 0

        self.frame = QLabel()
        Im = QPixmap("Grid.png")
        Im = Im.scaled(500,500)
        self.frame.setPixmap(Im)

        self.butleft = QPushButton('←',self)
        self.butleft.setFixedSize(20,20)
        self.butup = QPushButton('↑',self)
        self.butup.setFixedSize(20,20)
        self.butright = QPushButton('→',self)
        self.butright.setFixedSize(20,20)
        self.butdown = QPushButton('↓',self)
        self.butdown.setFixedSize(20,20)

        self.load = QPushButton('Load Image',self)
        self.load.setFixedWidth(120)
        self.save = QPushButton('Save Image',self)
        self.save.setFixedWidth(120)

        self.GeoList = Geometry_list()


        #self.Err = QLabel('   No Image',self)


        ###########################
        ### connect the buttons ###²
        ###########################

        self.Find.clicked.connect(self.FindLocation)
        self.butup.clicked.connect(self.moveup)
        self.butdown.clicked.connect(self.movedown)
        self.butright.clicked.connect(self.moveright)
        self.butleft.clicked.connect(self.moveleft)
        self.load.clicked.connect(self.openFileNameDialog)
        self.save.clicked.connect(self.saveFileDialog)



        ########################
        ### Organize in grid ###
        ########################

        self.grid1 = QGridLayout()
        self.grid1.setSpacing(10)

        self.grid1.addWidget(LatLabel, 0, 0,1,1)
        self.grid1.addWidget(self.Lat,0,1,1,4)

        self.grid1.addWidget(LongLabel, 1, 0,1,1)
        self.grid1.addWidget(self.Long,1,1,1,4)

        self.grid1.addWidget(ZoomLabel, 2, 0,1,1)
        self.grid1.addWidget(self.Zoom,2,1,1,4)

        self.grid1.addWidget(self.Find,3,0,1,2)

        self.grid1.addWidget(self.butleft,4,2)
        self.grid1.addWidget(self.butup,3,3)
        self.grid1.addWidget(self.butdown,4,3)
        self.grid1.addWidget(self.butright,4,4)

        self.grid1.addWidget(self.load,4,0)
        self.grid1.addWidget(self.save,4,1)

        self.grid1.addWidget(self.map,5,0,5,6)
        self.grid1.addWidget(self.frame,5,0,5,6)
        self.grid1.addWidget(self.Zoom_lab,5,0,5,6)
        self.grid1.addWidget(self.paint,5,0,5,6)

        self.grid1.addWidget(self.GeoList,0,7)







        #-------------------------------------------------#
        #-------------- TAB 2: Infiltration --------------#
        #-------------------------------------------------#


        ##########################
        ### make input widgets ###
        ##########################


        self.tabs_inf = QTabWidget()
        self.tab1_inf = QWidget()
        self.tab2_inf = QWidget()
        self.tabs_inf.addTab(self.tab1_inf,"I. Infiltration of 100 mm")
        self.tabs_inf.addTab(self.tab2_inf,"II. Beerkan method")

        self.Table_inf = Table_infiltration_list()



        ### tab 1: infiltration of 100 mm ###

        self.Inf_100mm = Infiltration_100m()
        Add_inf_100mm = QPushButton()
        Add_inf_100mm.setIcon(QIcon('Fix.png'))

        grid_tab1 =QGridLayout()
        grid_tab1.addWidget(self.Inf_100mm,0,0,100,100)
        grid_tab1.addWidget(Add_inf_100mm,99,99)

        self.tab1_inf.setLayout(grid_tab1)


        """
        Add_inf_100mm = QPushButton('Fix')
        Add_inf_100mm.move(5,2)
        """

        ### tab 2: Beerkan ###

        self.Inf_Beerkan =  Infiltration_Beerkan()

        Add_inf_Beerkan = QPushButton()
        Add_inf_Beerkan.setIcon(QIcon('Fix.png'))

        grid_tab2 = QGridLayout()
        grid_tab2.addWidget(self.Inf_Beerkan,0,0,100,100)
        grid_tab2.addWidget(Add_inf_Beerkan,99,99)

        self.tab2_inf.setLayout(grid_tab2)




        ###########################
        ### connect the buttons ###
        ###########################

        """
        Add_inf_100mm.clicked.connect(self.Fix)
        """
        Add_inf_Beerkan.clicked.connect(self.Fix_Beerkan)
        Add_inf_100mm.clicked.connect(self.Fix_Inf100mm)




        ########################
        ### Organize in grid ###
        ########################

        self.grid2 = QGridLayout()
        self.grid2.setSpacing(10)

        self.grid2.addWidget(self.tabs_inf,0,0)
        self.grid2.addWidget(self.Table_inf,0,1)






        #--------------------------------------------------#
        #-------------- Impliment the layout --------------#
        #--------------------------------------------------#


        # initiate the entire bunch
        self.tab1.setLayout(self.grid1)
        self.tab2.setLayout(self.grid2)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()




        #-------------------------------------#
        #-------------- Methods --------------#
        #-------------------------------------#



    def FindLocation(self):
        longitude = float(self.Long.value())
        latitude = float(self.Lat.value())
        zoomlevel = self.Zoom.value()


        #longitude = longitude - (-0.0001*zoomlevel+0.0026)
        #latitude = latitude + (-0.0001*zoomlevel+0.0026)

        try:

            gmd = GoogleMapDownloader(latitude, longitude, zoomlevel)
            img = gmd.generateImage()
            img.save("GM_loc.png")

            zoomlevels = np.arange(15,22)
            zoomcorrection = np.zeros(7)
            zoomcorrection[0:7] =[5000,2500,1250,625,300,150,75]

            self.Zoom_str = str(int(zoomcorrection[zoomlevels == self.Zoom.value()]))+'m'
            self.loadZoom()


        except:
            pass

            warning = QMessageBox(self)
            warning.setIcon(QMessageBox.Critical)
            buttonReply = warning.question(self, 'PyQt5 message', "No New Image is generated! Try again in two minutes...", QMessageBox.Ok | QMessageBox.Ok)

            if buttonReply == QMessageBox.Ok:
                warning.close()



        Im = QPixmap("GM_loc.png")
        Im = Im.scaled(500,500)
        self.map.setPixmap(Im)

    def openFileNameDialog(self):
        options = QFileDialog.Options()

        try:
            del(self.fileName)
        except:
            pass

        self.fileName, self.cancel = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Png Files (*.png)", options=options)

        try:
            A = pickle.load(open(self.fileName[:-4]+'.txt', 'rb'))

            Im = QPixmap(self.fileName)
            Im = Im.scaled(500,500)
            self.map.setPixmap(Im)


            self.Zoom_str = A[0]
            self.loadZoom()

            self.Long.setValue(float(A[1]))
            self.Lat.setValue(float(A[2]))
            self.Zoom.setValue(float(A[3]))
        except:
            pass


    def saveFileDialog(self):

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Png Files (*.png)", options=options)
        if fileName:
            print(fileName)
            if fileName.endswith('.png')==False:
                fileName_png = fileName + '.png'
                fileName_txt = fileName + '.txt'
        copyfile("GM_loc.png", fileName_png)

        longitude = float(self.Long.value())
        latitude = float(self.Lat.value())

        A = []
        A.append(self.Zoom_str)
        A.append(longitude)
        A.append(latitude)
        A.append(self.Zoom.value())

        pickle.dump(A,open(fileName_txt, 'wb'))



    def moveright(self):
        longitude = float(self.Long.value())
        self.Long.setValue(longitude+0.001)
        self.FindLocation()

    def moveleft(self):
        longitude = float(self.Long.value())
        self.Long.setValue(longitude-0.001)
        self.FindLocation()

    def moveup(self):
        latitude = float(self.Lat.value())
        self.Lat.setValue(latitude+0.001)
        self.FindLocation()

    def movedown(self):
        latitude = float(self.Lat.value())
        self.Lat.setValue(latitude-0.001)
        self.FindLocation()

    def Fix(self):
        A = self.Inf_100mm.Output()
        print(A)
        self.t.add_item(A[0],A[1],A[2],A[3])

    def loadZoom(self):
        self.Zoom_lab.scale.setText(self.Zoom_str)

        self.update()

    def Fix_Beerkan(self):
        Ks,a,k = self.Inf_Beerkan.Output_results()
        self.Table_inf.Load(a,k,2)

    def Fix_Inf100mm(self):
        a,k = self.Inf_100mm.Output_results()
        self.Table_inf.Load(a,k,1)





if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
