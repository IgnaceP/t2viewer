import sys
import PyQt5.QtCore
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import numpy as np

class PlotMeshVarDialog(QDialog):
    def __init__(self, parent = None):
        super(PlotMeshVarDialog, self).__init__(parent)

        self.setStyleSheet("""
        QWidget {
            background-color: rgb(35, 35, 35);
            }
        """)

        self.variable = 0

        self.createWidgets()
        self.setStyleSheets()
        self.setGridLayout()

    def createWidgets(self):
        self.timelabel = QLabel('Timestep:')
        self.time = QSpinBox()
        self.time.setValue(0)

        self.var = QComboBox()
        self.var.addItem('Pick a variable')

        self.ok = QPushButton('Ok')
        self.ok.clicked.connect(self.continuePlot)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self.cancelPlot)

        self.min = QLineEdit()
        self.max = QLineEdit()
        self.range = QLabel('-')
        self.range.setAlignment(Qt.AlignCenter)

    def setStyleSheets(self):
        self.timelabel.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.time.setStyleSheet("""
        QSpinBox {
            color: rgb(180,180,180);
        }
        """)

        self.var.setStyleSheet("""
        QComboBox {
            color: rgb(180,180,180);
        }
        """)

        self.ok.setStyleSheet("""
        QPushButton {
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
        }
        """)

        self.cancel.setStyleSheet("""
        QPushButton {
            color: rgb(180,180,180);
            background-color: rgb(55, 55, 60);
        }
        """)

        self.range.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.min.setStyleSheet("""
        QLineEdit {
            color: rgb(180,180,180);
            }
        """)

        self.max.setStyleSheet("""
        QLineEdit {
            color: rgb(180,180,180);
            }
        """)

    def setGridLayout(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.timelabel, 0, 0, 1, 1)
        self.grid.addWidget(self.time, 0, 1, 1, 2)
        self.grid.addWidget(self.var, 1, 0, 1, 3)

        self.grid.addWidget(self.ok, 3, 1)
        self.grid.addWidget(self.cancel, 3, 2)

        self.grid.addWidget(self.min, 2, 0)
        self.grid.addWidget(self.range, 2, 1)
        self.grid.addWidget(self.max, 2, 2)

        self.setLayout(self.grid)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelPlot()

    def cancelPlot(self):
        self.variable = None
        self.t = None
        self.close()

    def continuePlot(self):
        self.variable = self.var.currentIndex()
        if self.variable == 0:
            self.cancelPlot()
        else:
            self.t = self.time.value()
            self.close()
