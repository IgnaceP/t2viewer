import sys
import PyQt5.QtCore
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
import numpy as np
import pandas as pd

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
        self.var.addItems(['u (m/s)', 'v (m/s)','water depth (m)','water surface (m)','Bathymetry (m)', 'Friction Coefficient','max water surface (m)','min water surface (m)', 'max water depth (m)', 'min water depth (m)'])
        self.var.activated.connect(self.toggleTime)

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

    def toggleTime(self,i):
        if self.var.currentIndex() > 7:
            self.time.setDisabled(True)
            self.time.setStyleSheet("""
            QSpinBox {
                color: rgb(100,100,100);
            }
            """)
        else:
            self.time.setEnabled(True)
            self.time.setStyleSheet("""
            QSpinBox {
                color: rgb(180,180,180);
            }
            """)

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
    def __init__(self, lims, parent = None):
        super(VideoSettingDialog, self).__init__(parent)

        self.setWindowTitle('Video Settings')

        self.setStyleSheet("""
        QWidget {
            background-color: rgb(35, 35, 35);
            }
        """)

        self.variable = 0
        self.axlims = lims

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

        self.set_ax_lims = QPushButton('Use Ax Limits')
        self.set_ax_lims.setDisabled(True)
        self.set_ax_lims.clicked.connect(self.setAxLims)

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

        self.set_ax_lims.setStyleSheet("""
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
        grid_lim.addWidget(self.set_ax_lims,4,1,1,3)
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
            self.set_ax_lims.setEnabled(True)
        else:
            self.WinTop.setDisabled(True)
            self.WinBot.setDisabled(True)
            self.WinLeft.setDisabled(True)
            self.WinRight.setDisabled(True)
            self.set_ax_lims.setDisabled(True)

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

    def setAxLims(self):
        self.WinLeft.setValue(self.axlims[0])
        self.WinRight.setValue(self.axlims[1])
        self.WinBot.setValue(self.axlims[2])
        self.WinTop.setValue(self.axlims[3])

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
        self.XLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.X = QSpinBox()
        self.X.setRange(0,1e9)

        self.YLabel = QLabel('y-coordinate:')
        self.YLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.Y = QSpinBox()
        self.Y.setRange(0,1e9)

        self.StationPicker = QComboBox()
        self.StationPicker.addItem('or pick a station...')
        self.loadStations()
        self.StationPicker.activated.connect(self.setStationCoors)

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

        self.StationPicker.setStyleSheet("""
        QComboBox {
            color: rgb(180,180,180);
        }
        """)

    def setGridLayout(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.XLabel, 0, 0)
        self.grid.addWidget(self.YLabel, 1, 0)

        self.grid.addWidget(self.X, 0, 1)
        self.grid.addWidget(self.Y, 1, 1)

        self.grid.addWidget(self.StationPicker, 2, 0, 1, 2)

        self.grid.addWidget(self.ok, 4, 0)
        self.grid.addWidget(self.cancel, 4, 1)

        self.setLayout(self.grid)
        self.show()

    def loadStations(self):
        self.Station_xs = []
        self.Station_ys = []
        self.Station_names = []
        self.StationName = ''
        stations_df = pd.read_csv('./support_files/Stations.csv')
        for i in range(len(stations_df.Name)):
            name = stations_df.Name[i].replace('_',' ')
            self.StationPicker.addItem(name)
            self.Station_names.append(name)
            self.Station_xs.append(stations_df.X[i])
            self.Station_ys.append(stations_df.Y[i])

        stations_df = pd.read_csv('./support_files/Diver_locations.csv')
        for i in range(len(stations_df.Name)):
            name = stations_df.Name[i].replace('_',' ')
            self.StationPicker.addItem(name)
            self.Station_names.append(name)
            self.Station_xs.append(stations_df.X[i])
            self.Station_ys.append(stations_df.Y[i])

    def setStationCoors(self,i):
        self.X.setValue(self.Station_xs[i-1])
        self.Y.setValue(self.Station_ys[i-1])
        self.StationName = self.Station_names[i-1]

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

            if np.min(abs(self.x-np.asarray(self.Station_xs))) > 1: self.StationName = ''
            if np.min(abs(self.y-np.asarray(self.Station_ys))) > 1: self.StationName = ''

            self.close()

################################################################################################################################################################

class LocateValueDialog(QDialog):
    def __init__(self, parent = None):
        super(LocateValueDialog, self).__init__(parent)

        self.setWindowTitle('Locate a value on the mesh')

        self.setStyleSheet("QWidget {background-color: rgb(35, 35, 35);}")

        self.variable = 0

        self.createWidgets()
        self.setStyleSheets()

    def createWidgets(self):
        grid = QGridLayout()

        self.l1 = QLabel('Get')
        grid.addWidget(self.l1, 0, 0)
        self.reducer = QComboBox()
        self.reducer.addItem('maximum')
        grid.addWidget(self.reducer, 0, 1)

        self.l2 = QLabel('Of')
        grid.addWidget(self.l2, 0, 2)
        self.var = QComboBox()
        self.var.addItem('Pick a variable')
        self.var.addItems(['u (m/s)', 'v (m/s)','water depth (m)','water surface (m)'])
        grid.addWidget(self.var, 0, 3)

        self.l3 = QLabel('where')
        self.constvar = QComboBox()
        self.constvar.addItem('Bathymetry')
        self.constvar.addItem('Friction')
        self.rel = QComboBox()
        self.rel.addItems(['>','<','='])
        self.tresh = QLineEdit()
        self.tresh.setText('-9999')
        grid.addWidget(self.l3, 1, 0)
        grid.addWidget(self.constvar, 1, 1)
        grid.addWidget(self.rel, 1, 2)
        grid.addWidget(self.tresh, 1, 3)

        self.ok = QPushButton('Ok')
        self.ok.clicked.connect(self.continueDialog)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self.cancelDialog)
        grid.addWidget(self.ok,2,0,1,2)
        grid.addWidget(self.cancel,2,2,1,2)

        self.setLayout(grid)
        self.show()

    def setStyleSheets(self):
        self.l1.setStyleSheet("QLabel {color: rgb(180,180,180);padding: 10px;}")
        self.l2.setStyleSheet("QLabel {color: rgb(180,180,180);padding: 10px;}")
        self.l3.setStyleSheet("QLabel {color: rgb(180,180,180);padding: 10px;}")

        self.reducer.setStyleSheet("QComboBox {color: rgb(180,180,180);}")
        self.var.setStyleSheet("QComboBox {color: rgb(180,180,180);}")
        self.constvar.setStyleSheet("QComboBox {color: rgb(180,180,180);}")
        self.rel.setStyleSheet("QComboBox {color: rgb(180,180,180);}")

        self.tresh.setStyleSheet("QLineEdit {color: rgb(180,180,180);}")

        self.ok.setStyleSheet("QPushButton {color: rgb(180,180,180);background-color: rgb(55, 55, 60);}")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelPlot()

    def cancelDialog(self):
        self.variable = None
        self.close()

    def continueDialog(self):
        self.variable = self.var.currentIndex()
        if self.variable == 0:
            self.cancelDialog()
        else:
            self.close()

################################################################################################################################################################


class loadSelafinDialog(QDialog):
    def __init__(self, varlist, parent = None):
        super(loadSelafinDialog, self).__init__(parent)

        self.setWindowTitle('Load a selafin file')

        self.setStyleSheet("QWidget {background-color: rgb(35, 35, 35);}")

        self.varlist = varlist

        self.createWidgets()

    def createWidgets(self):
        grid = QGridLayout()

        self.labels = []
        t = 0

        for var in self.varlist:
            self.labels.append(QLabel('%d. %s' % (t + 1, var)))
            grid.addWidget(self.labels[-1], t, 0)
            t += 1

        self.ul = QLabel('x-dir velocity (u):')
        self.ul.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.ul, 0, 1)
        self.labels.append(self.ul)
        self.vl = QLabel('y-dir velocity (v):')
        self.vl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.vl, 1, 1)
        self.labels.append(self.vl)
        self.hl = QLabel('water depth (h):')
        self.hl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.hl, 2, 1)
        self.labels.append(self.hl)
        self.bl = QLabel('bathymetry (b):')
        self.bl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.bl, 3, 1)
        self.labels.append(self.bl)
        self.nl = QLabel('friction coefficient (n):')
        self.nl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.nl, 4, 1)
        self.labels.append(self.nl)

        self.lineedits = []
        self.u = QLineEdit()
        self.u.setText('1')
        self.lineedits.append(self.u)
        grid.addWidget(self.u, 0, 2)
        self.v = QLineEdit()
        self.v.setText('2')
        self.lineedits.append(self.v)
        grid.addWidget(self.v, 1, 2)
        self.h = QLineEdit()
        self.h.setText('3')
        self.lineedits.append(self.h)
        grid.addWidget(self.h, 2, 2)
        self.b = QLineEdit()
        self.b.setText('4')
        self.lineedits.append(self.b)
        grid.addWidget(self.b, 3, 2)
        self.n = QLineEdit()
        self.n.setText('5')
        self.lineedits.append(self.n)
        grid.addWidget(self.n, 4, 2)


        self.ok = QPushButton('Ok')
        self.ok.clicked.connect(self.continueDialog)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self.cancelDialog)
        grid.addWidget(self.ok,t,1)
        grid.addWidget(self.cancel,t,2)

        self.setStyleSheets()

        self.setLayout(grid)
        self.show()
    def setStyleSheets(self):

        for label in self.labels:
            label.setStyleSheet("QLabel {color: rgb(180,180,180);padding: 10px;}")

        for lineedit in self.lineedits:
            lineedit.setStyleSheet("QLineEdit {color: rgb(180,180,180);}")

        self.ok.setStyleSheet("QPushButton {color: rgb(180,180,180);background-color: rgb(55, 55, 60);}")
        self.cancel.setStyleSheet("QPushButton {color: rgb(180,180,180);background-color: rgb(55, 55, 60);}")


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelPlot()

    def cancelDialog(self):
        self.var_indices = None
        self.close()

    def continueDialog(self):
        self.var_indices = []
        for lineedit in self.lineedits:
            a = lineedit.text()
            a = int(a)
            self.var_indices.append(a-1)

        self.var_indices = np.asarray(self.var_indices, dtype = int)
        self.close()
