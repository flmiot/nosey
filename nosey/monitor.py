import os
import numpy as np
import logging
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.roi import ROI
import nosey.guard
from nosey.templates import HideButton, RemoveButton

Log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class Monitor(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = np.zeros((4, 128, 128))


    def setupMonitor(self):
        # Setup frame region slider
        self.lr = pg.LinearRegionItem([1, self.image.shape[0]])
        self.lr.sigRegionChanged.connect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.connect(self.updateImage)
        self.lr.setBrush([147, 245, 66, 0.5*255])
        self.frameSelector.setXRange(1, self.image.shape[0], padding=0.1)
        self.frameSelector.addItem(self.lr)
        self.frameSelector.showAxis('left', show=False)
        self.frameSelector.setMouseEnabled(x=False, y=False)


    def display(self, scan):
        # Log.debug("Display scan {}. Summed: {}".format(scan, sum))
        self.image = np.transpose(scan.images, axes = [0,2,1])
        self.frameSelector.setXRange(1, self.image.shape[0], padding=0.1)
        self.lr.setRegion([1, self.image.shape[0]])
        self.updateImage()


    def updateImage(self):
        x0, x1 = self.lr.getRegion()
        x0 -= 1
        x0, x1 = int(x0), int(x1)
        self.imageView.setImage(np.sum(self.image[x0:x1], axis = 0))


    def getROI(self):
        rois = []
        for row in range(self.tableRoi.rowCount()):
            item = self.tableRoi.item(row, 2)
            roi = item.data(pg.QtCore.Qt.UserRole)
            rois.append(roi)
        return rois


    def setROI(self, rois):
        for roi in rois:
            self.addRoi(roi)


    def addRoi(self, roi = None):
        rows = self.tableRoi.rowCount()
        self.tableRoi.insertRow(rows)

        if roi == None:
            size = [self.image.shape[-2], 40]
            roi = ROI([0,size[1] / 2], size, 'ROI {}'.format(rows))

        roi.addToMonitor(self)
        roi.connectUpdateSlot(self.updatePlot)


        # proxy = pg.SignalProxy(roi.sigRegionChanged,
        #     rateLimit=2, delay = 0.0, slot = self.update_analyzer)

        # Button items
        btn_active = HideButton()
        btn_active.setCheckable(True)
        btn_active.toggle()
        btn_remove = RemoveButton()
        self.tableRoi.setCellWidget(rows, 0, btn_active)
        self.tableRoi.setCellWidget(rows, 1, btn_remove)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()
        item01.setText(roi.name)
        item01.setData(pg.QtCore.Qt.UserRole, roi)
        item01.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableRoi.setItem(rows, 2, item01)

        # Connect button events
        btn_remove.clicked.connect(lambda : self.removeROI(item01))
        btn_active.toggled.connect(roi.toggle)
        btn_active.toggled.connect(self.updatePlot)


    def addEnergyPoint(self):
        energies = self.getEnergies()
        rows = self.tableEnergy.rowCount()
        positions = [0]
        self.tableEnergy.insertRow(rows)

        step = self.image.shape[1] / max(1, len(energies))
        for ind in range(len(energies)):
            positions.append((ind + 1) * step)

        for roi in self.getROI():
            roi.clearEnergyPoints(self)
            for pos in positions:
                roi.addEnergyPoint(pos, self)

            roi.connectUpdateSlot(self.updatePlot)


        # Button items
        btn_remove = QtGui.QPushButton("Remove")
        btn_remove.setStyleSheet("QPushButton { background-color: #ff7a69 }")
        self.tableEnergy.setCellWidget(rows, 0, btn_remove)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()
        item01.setText("0")
        self.tableEnergy.setItem(rows, 1, item01)

        # Connect button events
        btn_remove.clicked.connect(lambda : self.removeEnergyPoint(item01))




    def removeROI(self, item):
        row = self.tableRoi.row(item)
        roi = item.data(pg.QtCore.Qt.UserRole)
        roi.removeFromMonitor(self)
        self.tableRoi.removeRow(row)


        # Rename remaining ROI
        for row in range(self.tableRoi.rowCount()):
            item = self.tableRoi.item(row, 2)
            item.setFlags(QtCore.Qt.ItemIsEditable)
            roi = item.data(pg.QtCore.Qt.UserRole)
            roi.changeName('ROI {}'.format(row))
            item.setText(roi.name)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


    def removeEnergyPoint(self, item):
        index = self.tableEnergy.row(item)

        for roi in self.getROI():
            roi.removeEnergyPoint(index, self)

        self.tableEnergy.removeRow(index)


    def getEnergies(self):
        rows = self.tableEnergy.rowCount()
        energies = []
        for rowIndex in range(rows):
            energy = float(self.tableEnergy.item(rowIndex, 1).text())
            energies.append(energy)

        return energies

    def frameSelectorChanged(self, *args, **kwargs):
        self.lr.sigRegionChanged.disconnect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.disconnect(self.updateImage)
        x0, x1 = self.lr.getRegion()
        x0, x1 = max(1, round(x0)), min(round(x1), self.image.shape[0])
        self.lr.setRegion([x0, x1])
        self.lr.sigRegionChanged.connect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.connect(self.updateImage)
