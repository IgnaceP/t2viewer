
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


#%%
class Paint(QLabel):
    def __init__(self, xbox, ybox, parent=None):
        super(Paint, self).__init__(parent=parent)

        # location to draw dot
        self.pos = False

        self.xbox = xbox
        self.ybox = ybox

    ##########################
    ### Define the methods ###
    ##########################

    #--------------------------------------------------------------------------------#
    def paintEvent(self, paintEvent):
        """ Painter method which draws the QPoint-lists"""

        if self.pos:
            # start the painter
            painter = QPainter(self)
            # make a pen
            pen = QPen()
            pen.setWidth(5)
            painter.setRenderHint(QPainter.Antialiasing, True)


            ### field ###
            # adapt pen with the right color
            pen.setColor(QColor(185,50,66))
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawPoint(self.pos)

    #--------------------------------------------------------------------------------#
    def mouseReleaseEvent(self, cursor_event):
        """ Method to store the click-events in the list"""

        self.pos = QPoint(cursor_event.pos())

        # update the painter
        self.update()

        # update the x and y-box
        x = round((self.xmax - self.xmin) * (self.pos.x()/700) + self.xmin,2)
        y = round(self.ymax - (self.ymax - self.ymin) * (self.pos.y()/700),2)
        self.xbox.setText(str(x))
        self.ybox.setText(str(y))

    def setBox(self, box):
        self.xmin = box[0]
        self.xmax = box[1]
        self.ymin = box[2]
        self.ymax = box[3]
