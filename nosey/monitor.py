import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.rois import ROI

class Monitor(QtGui.QMainWindow):
    def __init__(self, image, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        dirname = os.path.dirname(__file__)
        uic.loadUi(os.path.join(dirname, 'ui/monitor.ui'), self)

        # Placeholder image
        self.image = image

        # Setup frame region slider
        self.lr = pg.LinearRegionItem([1, self.image.shape[0]])
        self.lr.sigRegionChanged.connect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.connect(self.updateImage)
        self.lr.setBrush([147, 245, 66, 0.5*255])
        self.frameSelector.setXRange(1, self.image.shape[0], padding=0.1)
        self.frameSelector.addItem(self.lr)
        self.frameSelector.showAxis('left', show=False)
        self.frameSelector.setMouseEnabled(x=False, y=False)

        self.updateImage()


    def updateImage(self):
        x0, x1 = self.lr.getRegion()
        x0 -= 1
        x0, x1 = int(x0), int(x1)
        print(x0, x1)
        self.imageView.setImage(np.sum(self.image[x0:x1], axis = 0))


    @QtCore.pyqtSlot()
    def on_actionAdd_ROI_triggered(self, *args, **kwargs):
        self.addRoi()


    def addRoi(self):
        rows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rows)

        size = [self.image.shape[-2], 40]
        r = ROI([0,size[1] / 2], size, 'ROI {}'.format(rows))
        r.addToMonitor(self)

        # Button items
        btn_active = QtGui.QPushButton("Active")
        btn_active.setCheckable(True)
        btn_active.toggle()
        btn_active.setStyleSheet("QPushButton:checked { background-color: #a8fc97 }")
        btn_remove = QtGui.QPushButton("Remove")
        btn_remove.setStyleSheet("QPushButton { background-color: #ff7a69 }")
        self.tableWidget.setCellWidget(rows, 0, btn_active)
        self.tableWidget.setCellWidget(rows, 1, btn_remove)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()
        item01.setText(r.name)
        item01.setData(pg.QtCore.Qt.UserRole, r)
        item01.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(rows, 2, item01)

        # Connect button events
        btn_remove.clicked.connect(lambda : self.removeROI(item01))
        btn_active.toggled.connect(r.toggle)


    def removeROI(self, item):
        row = self.tableWidget.row(item)
        roi = item.data(pg.QtCore.Qt.UserRole)
        roi.removeFromMonitor(self)
        self.tableWidget.removeRow(row)


        # Rename remaining ROI
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 2)
            item.setFlags(QtCore.Qt.ItemIsEditable)
            roi = item.data(pg.QtCore.Qt.UserRole)
            roi.name = 'ROI {}'.format(row)
            item.setText(roi.name)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


    def frameSelectorChanged(self, *args, **kwargs):
        self.lr.sigRegionChanged.disconnect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.disconnect(self.updateImage)
        x0, x1 = self.lr.getRegion()
        x0, x1 = max(1, round(x0)), min(round(x1), self.image.shape[0])
        self.lr.setRegion([x0, x1])
        self.lr.sigRegionChanged.connect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.connect(self.updateImage)
