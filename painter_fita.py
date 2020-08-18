
"""
Created on Sun Dec  2 15:55:24 2018

@author: ignace
"""
#%%
import sys
import PyQt5.QtCore
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import numpy as np

import urllib
import os
import math
import matplotlib as plt
from shutil import copyfile
import pickle
from Frame import frame_curs
#%%
class Paint(QLabel):
    def __init__(self, parent=None):
        super(Paint, self).__init__(parent=parent)

        # Geometry class to transfer changes made in the painter to the geometry information list
        self.Geo = Geometry_class

        # Boolean variables to detect which drawer is activated
        self.Fielddrawing = False
        self.Furdrawing = False
        self.WSdrawing = False

        # empty lists to store Qpoints on clicked locations, depending on the upper boolean variables
        self.chosen_points = []
        self.chosen_pointsQ = []
        self.chosen_pointsQ_source = []
        self.chosen_pointsQ_field = []
        # list of lists: stores all QPoints of one furrow in one list, QPoints of second furrow in second list in this list
        self.chosen_pointsQ_furrow = []
        self.chosen_pointsQ_furrow.append([])

        # 500x500 raster to populate with interpolated secondary channel
        self.chosen_pointsQ_source_ras = np.zeros([500,500])
        # list to store the coordinates of the interpolated secondary channel
        self.chosen_pointsQ_source_con = []
        # list to store the Qpoints of the interpolated secondary channel
        self.chosen_pointsQ_source_con_qpoints = []

        # Counter to keep track of the number of furrows
        self.k = 0

        # Call method to setup interface
        self.setUI()

    def setUI(self):
    #################################################
    ### make input widgets and connect to methods ###
    #################################################

        # Push button to enable field drawing
        self.field = QPushButton(self)
        self.field.setCheckable(True)
        self.field.resize(40,40)
        self.field.move(505, 0)

        # connect to method which turns on the boolean variable for field-drawing and will disable all other drawing-boolean-variables
        self.field.clicked[bool].connect(self.enableDrawingField)
        self.field.setIcon(QIcon('Select_Field.png'))
        self.field.setIconSize(QSize(30,30))
        self.field.setToolTip('Draw field')

        # Push button to enable furdrawing
        self.fur = QPushButton(self)
        self.fur.setCheckable(True)
        self.fur.resize(40,40)
        self.fur.move(505, 50)
        self.fur.clicked[bool].connect(self.enableDrawingFur)
        self.fur.setIcon(QIcon('Select_Furrows.png'))
        self.fur.setIconSize(QSize(30,30))
        self.fur.setToolTip('Draw furrow')

        # Push button to start new furrow
        self.newfur = QPushButton(self)
        self.newfur.resize(40,40)
        self.newfur.move(505, 100)
        self.newfur.clicked.connect(self.enableDrawingFurNew)
        self.newfur.setIcon(QIcon('New_Furrow.png'))
        self.newfur.setIconSize(QSize(30,30))
        self.newfur.setToolTip('Start a new furrow')

        # Push button to enable source channel drawing
        self.ws = QPushButton(self)
        self.ws.setCheckable(True)
        self.ws.resize(40,40)
        self.ws.move(505, 150)
        self.ws.clicked[bool].connect(self.enableDrawingWS)
        self.ws.setIcon(QIcon('Field_Furrow.png'))
        self.ws.setIconSize(QSize(30,30))
        self.ws.setToolTip('Draw field furrow')

        # Push button to remove last drawn point
        back = QPushButton(self)
        back.resize(40,40)
        back.move(505, 200)
        back.clicked.connect(self.stepBack)
        back.setIcon(QIcon('Back.png'))
        back.setIconSize(QSize(30,30))
        back.setToolTip('Remove last drawing from selected drawing')

        # Push button to reset the full drawing and start from scratch
        reset = QPushButton(self)
        reset.resize(40,40)
        reset.move(505, 250)
        reset.clicked.connect(self.resetDrawing)
        reset.setIcon(QIcon('Reset.png'))
        reset.setIconSize(QSize(30,30))
        reset.setToolTip('Reset drawing')

        # Push button to save drawing
        save = QPushButton(self)
        save.resize(40,40)
        save.move(505,400)
        save.clicked.connect(self.saveDrawings)
        save.setIcon(QIcon('Save.png'))
        save.setIconSize(QSize(30,30))
        save.setToolTip('Save drawing')

        # Push button to load previously saved drawing
        load = QPushButton(self)
        load.resize(40,40)
        load.move(505,450)
        load.clicked.connect(self.loadDrawings)
        load.setIcon(QIcon('Load.png'))
        load.setIconSize(QSize(30,30))
        load.setToolTip('Load drawing')

        # Courtesy to Google Maps
        RefGM = QLabel("© Google Maps",self)
        RefGM.move(395,475)



    ##########################
    ### Define the methods ###
    ##########################


    #--------------------------------------------------------------------------------#
    def enableDrawingField(self, pressed):
        """ Method which turns on the boolean variable which enables the field drawing and turns of the others"""

        if pressed:
            self.Fielddrawing  = True
            self.Furdrawing     = False
            self.WSdrawing      = False
            self.fur.setChecked(False)
            self.ws.setChecked(False)
        else:
            self.Fielddrawing        = False

    #--------------------------------------------------------------------------------#
    def enableDrawingFur(self, pressed):
        """ Method which turns on the boolean variable which enables the furrow drawing and turns of the others"""

        if pressed:
            self.Furdrawing     = True
            self.Fielddrawing  = False
            self.WSdrawing      = False
            self.ws.setChecked(False)
            self.field.setChecked(False)
        else: self.Furdrawing   = False

    #--------------------------------------------------------------------------------#
    def enableDrawingFurNew(self, pressed):
       """ Method which starts a new furrow"""

       self.chosen_pointsQ_furrow.append([])
       self.k += 1

       # new furrow also have to be communicated to the geometry-list
       self.Geo.new()

    #--------------------------------------------------------------------------------#
    def enableDrawingWS(self, pressed):
        """ Method which turns on the boolean variable which enables the source channel drawing and turns of the others"""

        if pressed:
            self.Furdrawing     = False
            self.Fielddrawing  = False
            self.WSdrawing      = True
            self.field.setChecked(False)
            self.fur.setChecked(False)
        else: self.WSdrawing    = False

    # --------------------------------------------------------------------------------#
    def resetDrawing(self, pressed):
        """Method to reset the previously made drawings and start from scratch"""

        # reset all lists which store the QPoints of each geometry
        self.chosen_pointsQ_furrow = []
        self.chosen_pointsQ_furrow.append([])
        self.chosen_pointsQ_field = []
        self.chosen_pointsQ_source = []
        self.chosen_pointsQ_source_con = []

        # reset counter
        self.k = 0

        # call method in Geo class which reset its lists
        self.Geo.reset()

        # update the painter so no drawings are shown
        self.update()

    #--------------------------------------------------------------------------------#
    def stepBack(self, pressed):
        """ method which removes the last drawn point"""

        # remove last field point
        if self.Fielddrawing:
            del(self.chosen_pointsQ_field[-1])

        # remove last furrow point
        elif self.Furdrawing:
            # if everything is empty, keep it empty
            if self.chosen_pointsQ_furrow[0]==[]:
                self.chosen_pointsQ_furrow[0]=[]
            # if last furrow was already removed, start removing from new one
            elif self.chosen_pointsQ_furrow[-1]==[]:
                del(self.chosen_pointsQ_furrow[-1])
                self.k -= 1
            # communicate to geometry list class
            elif len(self.chosen_pointsQ_furrow[-1]) == 1:
                self.Geo.deleteFur()
            # remove last placed point
            if len(self.chosen_pointsQ_furrow[-1]) >0:
                del(self.chosen_pointsQ_furrow[-1][-1])
            # reload everything to the geometry list class
            self.Geo.load(self.chosen_pointsQ_furrow[self.k], self.chosen_pointsQ_furrow)

        # remove last source point
        elif self.WSdrawing:
            del(self.chosen_pointsQ_source[-1])

        # update the painter
        self.update()

    #--------------------------------------------------------------------------------#
    def saveDrawings(self, pressed):
        """ Method wich saves the made drawings into a txt.file"""

        # open a dialog to choose directory and filename
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Png Files (*.png)", options=options)
        if fileName:
            print(fileName)
            # if no extension is provided, add an extension
            if fileName.endswith('.txt')==False:
                fileName = fileName + '.txt'

        # create list to store everything in
        pList = [
                self.chosen_pointsQ_field
                , self.chosen_pointsQ_furrow
                , self.chosen_pointsQ_source
                ]
        # dump this list in a txt.file through the pickle toolbox
        pickle.dump(pList,open(fileName, 'wb'))


    #--------------------------------------------------------------------------------#
    def loadDrawings(self, pressed):
        """ Load a previously saved geometry-file """

        # open a dialog to choose directory and filename
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Txt files (*.txt)", options=options)

        # load the txt-file and open it as a list through the pickle toolbox
        f = pickle.load(open(fileName, 'rb'))

        # assign the saved list items to their corresponding paint lists
        self.chosen_pointsQ_field = f[0]
        self.chosen_pointsQ_furrow = f[1]
        self.chosen_pointsQ_source = f[2]

        # update the furrow counter
        self.k = len(self.chosen_pointsQ_furrow)-1

        # communicate this to the geometry-list class
        self.Geo.loadSaved(self.chosen_pointsQ_furrow)

        # update the painter
        self.update()

    #--------------------------------------------------------------------------------#
    def paintEvent(self, paintEvent):
        """ Painter method which draws the QPoint-lists"""

        # start the painter
        painter = QPainter(self)
        # make a pen
        pen = QPen()
        pen.setWidth(5)
        painter.setRenderHint(QPainter.Antialiasing, True)


        ### field ###

        # run over the QPoints of the field and draw them as points
        for pos in self.chosen_pointsQ_field:
            # adapt pen with the right color
                pen.setColor(QColor(244,194,66))
                pen.setWidth(5)
                painter.setPen(pen)
                painter.drawPoint(pos)

        #  connect the upper drawn points
        pen.setWidth(2)
        painter.setPen(pen)
        needle = QPolygon(self.chosen_pointsQ_field)
        painter.drawPolygon(needle)

        ### Source channel ###

        pen.setWidth(4)
        pen.setColor(QColor(34,146,240))
        painter.setPen(pen)
        needle = QPolygon(self.chosen_pointsQ_source)
        painter.drawPolyline(needle)

        # run over the QPoints of the source channel and draw them as points
        try: # try because if there is no source channel drawn, this shouldn't cause a problem
            for pos in self.chosen_pointsQ_source:
                pen.setWidth(15)
                pen.setColor(QColor(34,146,240))
                painter.setPen(pen)
                painter.drawPoint(pos)
        except:
            pass

        ### furrow ###

        # run over the list of QPoint-lists to draw every furrow
        for j in range(0,len(self.chosen_pointsQ_furrow)):
            for pos in self.chosen_pointsQ_furrow[j]:
                pen.setColor(QColor(34,76,240))
                pen.setWidth(5)
                painter.setPen(pen)
                painter.drawPoint(pos)

            pen.setColor(QColor(34,76,240))
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            needle = QPolygon(self.chosen_pointsQ_furrow[j])
            painter.drawPolyline(needle)


        ### furrow labels ###

            if len(self.chosen_pointsQ_furrow[j])>1:

                # first draw shadow
                pen.setColor(QColor(50, 50, 50))
                painter.setPen(pen)
                lab_loc = self.chosen_pointsQ_furrow[j][-1]

                lab_locx = lab_loc.x() + 11
                lab_locy = lab_loc.y() + 1

                lab_loc = QPoint(lab_locx,lab_locy)

                painter.drawText(lab_loc, str(j+1)+'.')

                # draw actual blue label
                pen.setColor(QColor(34,76,240))
                painter.setPen(pen)
                lab_loc = self.chosen_pointsQ_furrow[j][-1]

                lab_locx = lab_loc.x() + 10
                lab_locy = lab_loc.y()

                lab_loc = QPoint(lab_locx, lab_locy)

                painter.drawText(lab_loc, str(j + 1) + '.')


    #--------------------------------------------------------------------------------#
    def mouseReleaseEvent(self, cursor_event):
        """ Method to store the click-events in the list"""

        # store clicked point in field Qpoint-list
        if self.Fielddrawing:
            self.chosen_pointsQ_field.append(QPoint(cursor_event.pos()))

        # store clicked point in furrow Qpoint-list

        elif self.Furdrawing:

            if self.chosen_pointsQ_source_con == []:
            # if there is no main channel
                self.chosen_pointsQ_furrow[self.k].append(QPoint(cursor_event.pos()))

                self.Geo.load(self.chosen_pointsQ_furrow[self.k],self.chosen_pointsQ_furrow)


            elif self.chosen_pointsQ_furrow[self.k] == []:
            # if there is a main channel: first fit to source channel


                P_init = QPoint(cursor_event.pos())
                P_x = P_init.x()
                P_y = P_init.y()

                New_fur_dis = []

                # connect to interpolated source channel
                for pos in self.chosen_pointsQ_source_con:
                    dist = ((P_x-pos[0])**2+(P_y-pos[1])**2)**0.5
                    New_fur_dis.append(dist)


                S = np.argmin(New_fur_dis)
                P_snapped_reg = self.chosen_pointsQ_source_con[S]
                P_snapped = QPoint(P_snapped_reg[0],P_snapped_reg[1])

                self.chosen_pointsQ_furrow[self.k].append(P_snapped)
                del(P_snapped,S,P_snapped_reg,P_x,P_y,P_init)

            else:
            # there is a main channel and the furrow is connected

                self.chosen_pointsQ_furrow[self.k].append(QPoint(cursor_event.pos()))
                # load all furrow geometry into the GHC
                self.Geo.load(self.chosen_pointsQ_furrow[self.k], self.chosen_pointsQ_furrow)



        # draw a seconday channel
        elif self.WSdrawing:

            P = QPoint(cursor_event.pos())
            self.chosen_pointsQ_source.append(P)
            self.chosen_pointsQ_source_con.append([P.x(),P.y()])
            self.chosen_pointsQ_source_ras[P.y(),P.x()] = 1

            ref = self.chosen_pointsQ_source_con[-2:]

            con = []

            # interpolate between the clicked points to enable the snapping of new furrows, interpolation is linear
            if len(ref)>1:
                if ref[1][0]>ref[0][0]:

                    for x in range(ref[0][0]+1,ref[1][0]):
                        a = (ref[1][1]-ref[0][1])/(ref[1][0]-ref[0][0])
                        b = ref[1][1]-ref[1][0]*a

                        y = x*a+b
                        y = round(y)

                        con.append([x,y])

                elif ref[1][0]<ref[0][0]:

                    con = []

                    for x in range(ref[1][0]+1,ref[0][0]):
                        a = (ref[1][1]-ref[0][1])/(ref[1][0]-ref[0][0])
                        b = ref[1][1]-ref[1][0]*a

                        y = x*a+b
                        y = round(y)

                        con.insert(0,[x,y])

                elif ref[1][0]==ref[0][0]:
                    for y in range(min(ref[1][0]+1,ref[0][0]+1),max(ref[1][0]+1,ref[0][0]+1)):
                        con.append([x,y])


                del(self.chosen_pointsQ_source_con[-1])

                for pos in con:
                    # store interpolated points both as simple coordinates and as QPoints
                    self.chosen_pointsQ_source_con.append(pos)
                    self.chosen_pointsQ_source_con_qpoints.append(QPoint(pos[0],pos[1]))

                self.chosen_pointsQ_source_con.append([P.x(),P.y()])

        # update the painter
        self.update()


class Show_Zoom(QLabel):
    """ seperate label-class to correctly show zoom on top of the paint event """
    def __init__(self,zoomlevel = 0, parent=None):
        super(Show_Zoom, self).__init__(parent=parent)

        self.zoomlevel = zoomlevel

        self.plotZoom()

    def plotZoom(self):
        # only bother when there is a zoom entered
        if self.zoomlevel > 0:

            # plot it in a QLabel
            self.scale = QLabel(self)

            self.scale.move(235,15)
            self.scale.setFixedWidth(200)
