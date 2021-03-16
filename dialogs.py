import sys
import PyQt5.QtCore
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import numpy as np

################################################################################################################################################################
class PlotMeshVarDialog(QDialog):
    def __init__(self, parent = None):
        super(PlotMeshVarDialog, self).__init__(parent)

        self.setWindowTitle('Plot a variable on the mesh')

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

        self.showedges = QCheckBox('Show mesh edges')
        self.showedges.setChecked(False)

        self.showgrid = QCheckBox('Show grid')
        self.showgrid.setChecked(False)

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

        self.showedges.setStyleSheet("""
        QCheckBox {
            color: rgb(180,180,180);
            }
        """)

        self.showgrid.setStyleSheet("""
        QCheckBox {
            color: rgb(180,180,180);
            }
        """)


    def setGridLayout(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.timelabel, 0, 0, 1, 1)
        self.grid.addWidget(self.time, 0, 1, 1, 2)
        self.grid.addWidget(self.var, 1, 0, 1, 3)

        self.grid.addWidget(self.min, 2, 0)
        self.grid.addWidget(self.range, 2, 1)
        self.grid.addWidget(self.max, 2, 2)

        self.grid.addWidget(self.showedges, 3, 0, 1, 2)
        self.grid.addWidget(self.showgrid, 4, 0, 1, 2)

        self.grid.addWidget(self.ok, 5, 1)
        self.grid.addWidget(self.cancel, 5, 2)

        self.setLayout(self.grid)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelPlot()

    def cancelPlot(self):
        self.variable = None
        self.t = None
        self.showgridedges = False
        self.showagrid = False
        self.close()

    def continuePlot(self):
        self.variable = self.var.currentIndex()
        if self.variable == 0:
            self.cancelPlot()
        else:
            self.t = self.time.value()
            self.showgridedges = self.showedges.isChecked()
            self.showagrid = self.showgrid.isChecked()
            self.close()

################################################################################################################################################################

class VideoSettingDialog(QDialog):
    def __init__(self, parent = None):
        super(VideoSettingDialog, self).__init__(parent)

        self.setWindowTitle('Video Settings')

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

        self.VarLabel = QLabel('Variable to animate:')
        self.Var = QComboBox()
        self.Var.addItem('Water level [m]')

        self.RangeLabel = QLabel('Range:')
        self.Min = QSpinBox()
        self.Min.setValue(-1)
        self.Min.setRange(-1e9,1e9)
        self.Range = QLabel('-')
        self.Max = QSpinBox()
        self.Max.setValue(5)
        self.Max.setRange(-1e9,1e9)

        self.SetWinLim = QCheckBox('Set window limits')
        self.SetWinLim.stateChanged.connect(self.toggleWinLim)

        self.frame = QFrame()

        self.WinTop = QSpinBox()
        self.WinTop.setDisabled(True)
        self.WinTop.setRange(-1e9,1e9)
        self.WinBot = QSpinBox()
        self.WinBot.setDisabled(True)
        self.WinBot.setRange(-1e9,1e9)
        self.WinLeft = QSpinBox()
        self.WinLeft.setDisabled(True)
        self.WinLeft.setRange(-1e9,1e9)
        self.WinRight = QSpinBox()
        self.WinRight.setDisabled(True)
        self.WinRight.setRange(-1e9,1e9)
        self.spinboxes = [self.WinLeft, self.WinTop, self.WinBot, self.WinRight, self.Min, self.Max]

        self.Empty1 = QLabel()
        self.Empty1.setFixedSize(5,5)
        self.Empty2 = QLabel()
        self.Empty2.setFixedSize(5,5)
        self.empties = [self.Empty1, self.Empty2]


        self.ok = QPushButton('Ok')
        self.ok.clicked.connect(self.continuePlot)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self.cancelDialog)

    def setStyleSheets(self):
        self.VarLabel.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.RangeLabel.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.Range.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.Var.setStyleSheet("""
        QComboBox {
            color: rgb(180,180,180);
        }
        """)

        for spinbox in self.spinboxes:
            spinbox.setStyleSheet("""
            QSpinBox {
                color: rgb(180,180,180);
                }
            QSpinBox:disabled {
                color: rgb(50,50,50);
                background-color: rgb(40,40,40)
            }
            """)

        self.SetWinLim.setStyleSheet("""
        QCheckBox {
            color: rgb(180,180,180);
            }
        """)

        self.frame.setStyleSheet("""
        QFrame {
            background-color: rgb(31,31,31);
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

        for empty in self.empties:
            empty.setStyleSheet("""
            QLabel {
                background-color:rgb(31,31,31);
                }
                """)


    def setGridLayout(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.VarLabel, 0, 0, 1, 1)
        self.grid.addWidget(self.Var, 0, 1, 1, 1)

        box1 = QHBoxLayout()
        box1.addStretch()
        box1.addWidget(self.Min)
        box1.addWidget(self.Range)
        box1.addWidget(self.Max)
        self.grid.addWidget(self.RangeLabel, 1, 0)
        self.grid.addLayout(box1, 1, 1)

        self.grid.addWidget(self.SetWinLim, 3, 0)
        self.grid.addWidget(self.frame, 4, 0, 1, 2)
        grid_lim = QGridLayout()

        grid_lim.addWidget(self.Empty1, 0, 0)
        grid_lim.addWidget(self.Empty2, 4, 4)
        grid_lim.addWidget(self.WinLeft, 2,1)
        grid_lim.addWidget(self.WinRight, 2,3)
        grid_lim.addWidget(self.WinTop, 1,2)
        grid_lim.addWidget(self.WinBot, 3,2)
        self.grid.addLayout(grid_lim, 4, 0, 1, 2)

        box2 = QHBoxLayout()
        box2.addWidget(self.ok)
        box2.addWidget(self.cancel)
        self.grid.addLayout(box2, 5, 0, 1 ,2)

        self.setLayout(self.grid)
        self.show()

    def toggleWinLim(self, i):
        if i:
            self.WinTop.setEnabled(True)
            self.WinBot.setEnabled(True)
            self.WinLeft.setEnabled(True)
            self.WinRight.setEnabled(True)
        else:
            self.WinTop.setDisabled(True)
            self.WinBot.setDisabled(True)
            self.WinLeft.setDisabled(True)
            self.WinRight.setDisabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelDialog()

    def cancelDialog(self):
        self.good_exit = False
        self.close()

    def continuePlot(self):
            if self.SetWinLim.isChecked:
                self.lims = [self.WinLeft.value(), self.WinRight.value(), self.WinTop.value(), self.WinBot.value()]
            else:
                self.lims = None
            self.var = self.Var.currentIndex()
            self.min = self.Min.value()
            self.max = self.Max.value()

            self.good_exit = True
            self.close()

################################################################################################################################################################

class AddCoorDialog(QDialog):
    def __init__(self, parent = None):
        super(AddCoorDialog, self).__init__(parent)

        self.setWindowTitle('Add xy pair')

        self.setStyleSheet("""
        QWidget {
            background-color: rgb(35, 35, 35);
            }
        """)

        self.createWidgets()
        self.setStyleSheets()
        self.setGridLayout()

    def createWidgets(self):

        self.XLabel = QLabel('x-coordinate:')
        self.XLabel.setAlignment(Qt.AlignRight)
        self.X = QSpinBox()
        self.X.setRange(0,1e9)

        self.YLabel = QLabel('y-coordinate:')
        self.YLabel.setAlignment(Qt.AlignRight)
        self.Y = QSpinBox()
        self.Y.setRange(0,1e9)

        self.ok = QPushButton('Ok')
        self.ok.clicked.connect(self.continuePlot)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self.cancelDialog)

    def setStyleSheets(self):
        self.XLabel.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.YLabel.setStyleSheet("""
        QLabel {
            color: rgb(180,180,180);
            padding: 10px;
            }
        """)

        self.X.setStyleSheet("""
        QSpinBox {
            color: rgb(180,180,180);
            }
        """)

        self.Y.setStyleSheet("""
        QSpinBox {
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


    def setGridLayout(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.XLabel, 0, 0)
        self.grid.addWidget(self.YLabel, 1, 0)

        self.grid.addWidget(self.X, 0, 1)
        self.grid.addWidget(self.Y, 1, 1)

        self.grid.addWidget(self.ok, 2, 0)
        self.grid.addWidget(self.cancel, 2, 1)

        self.setLayout(self.grid)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelDialog()

    def cancelDialog(self):
        self.good_exit = False
        self.close()

    def continuePlot(self):
            self.good_exit = True
            self.x = self.X.value()
            self.y = self.Y.value()
            self.close()
