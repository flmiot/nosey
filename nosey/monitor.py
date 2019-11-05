import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, uic

from nosey.roi import ROI
import nosey.guard
from nosey.templates import HideButton, RemoveButton


class Monitor(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = np.zeros((4, 487, 195))
        self.scan = None
        self.levels = [0, 1]

    def setupMonitor(self):
        # Setup frame region slider
        self.lr = pg.LinearRegionItem([1, self.image.shape[0]])
        self.lr.sigRegionChanged.connect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.connect(self.updateImage)
        self.lr.setBrush([147, 245, 66, 0.5 * 255])
        self.frameSelector.setXRange(1, self.image.shape[0], padding=0.1)
        self.frameSelector.addItem(self.lr)
        self.frameSelector.showAxis('left', show=False)
        self.frameSelector.setMouseEnabled(x=False, y=False)

    def display(self, scan):
        # Log.debug("Display scan {}. Summed: {}".format(scan, sum))
        self.scan = scan
        if scan.loaded:
            self.image = np.transpose(scan.images, axes=[0, 2, 1])
            x0, x1 = scan.range
            self.frameSelector.setXRange(x0, x1, padding=0.1)
            self.lr.setRegion([1, self.image.shape[0]])
            self.updateImage()
            self.label_scanName.setText(scan.name)


    def updateImage(self):
        try:
            self.levels = self.imageView.ui.histogram.getLevels()
            x0, x1 = self.lr.getRegion()
            # x0 -= 1
            x0, x1 = int(x0), int(x1)
            self.imageView.setImage(np.sum(self.image[x0:x1], axis=0))
            # hmin, hmax = self.imageView.ui.histogram.getLevels()
            # self.imageView.ui.histogram.setLevels(*self.levels)
        except Exception as e:
            Log.error("Could not update monitor image: {}".format(e))

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

    def addRoi(self, roi=None, energy_point_positions=None):
        rows = self.tableRoi.rowCount()
        self.tableRoi.insertRow(rows)

        if roi is None:
            size = [self.image.shape[-2], 10]
            roi = ROI([0, size[1] / 2], size, 'ROI {}'.format(rows))

        roi.addToMonitor(self)
        roi.connectUpdateSlotProxy(self.updatePlot)

        energies = self.getEnergies()

        if energy_point_positions is None:
            positions = []
            step = self.image.shape[1] / max(1, len(energies) - 1)
            for ind in range(0, len(energies)):
                positions.append((ind) * step)
        else:
            positions = energy_point_positions

        for pos in positions:
            roi.addEnergyPoint(pos, self)

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
        self.tableRoi.resizeColumnsToContents()

        # Connect button events
        btn_remove.clicked.connect(lambda: self.removeROI(item01))
        btn_active.clicked.connect(lambda: self.showHideRoi(item01))

    def addEnergyPoint(self, energy=None, touch_roi=True):
        energies = self.getEnergies()
        rows = self.tableEnergy.rowCount()
        self.tableEnergy.insertRow(rows)

        if touch_roi:
            positions = [0]
            step = self.image.shape[1] / max(1, len(energies))
            for ind in range(len(energies)):
                positions.append((ind + 1) * step)

            for roi in self.getROI():
                roi.clearEnergyPoints(self)
                for pos in positions:
                    roi.addEnergyPoint(pos, self)

                roi.connectUpdateSlotProxy(self.updatePlot)

        # Button items
        btn_remove = RemoveButton()
        self.tableEnergy.setCellWidget(rows, 0, btn_remove)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()

        if energy is None:
            item01.setText("0")
        else:
            item01.setText(energy)

        self.tableEnergy.setItem(rows, 1, item01)
        self.tableEnergy.resizeColumnsToContents()

        # Connect button events
        btn_remove.clicked.connect(lambda: self.removeEnergyPoint(item01))

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

    def autoCalibration(self):
        try:
            for roi in self.getROI():
                scans = self.getScans()
                images = np.zeros((len(scans),) + scans[0].images[0].shape)
                for ind, scan in enumerate(scans):
                    images[ind] = np.sum(scan.images, axis=0)
                sum_before_search = self.getSetting(
                    ['Energy calibration', 'Sum runs before search'])
                search_radius = float(self.getSetting(
                    ['Energy calibration', 'Search radius']))
                roi.setEnergyPointsAuto(
                    images, self.imageView, sum_before_search, search_radius)
        except Exception as e:
            nosey.Log.error(
                "Automatic energy calibration failed: {}".format(e))

    def frameSelectorChanged(self, *args, **kwargs):
        self.lr.sigRegionChanged.disconnect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.disconnect(self.updateImage)
        x0, x1 = self.lr.getRegion()
        if x1 <= x0:
            x1 = x0 + 1
        x0, x1 = max(0, round(x0)), min(round(x1), self.image.shape[0] - 1)
        self.lr.setRegion([x0, x1])
        self.lr.sigRegionChanged.connect(self.frameSelectorChanged)
        self.lr.sigRegionChangeFinished.connect(self.updateImage)
        self.scan.range = [x0, x1]
        self.updatePlot()

    def updateCursorMonitor(self, event):
        pos = event[0]
        x = int(self.imageView.getView().mapSceneToView(pos).x())
        y = int(self.imageView.getView().mapSceneToView(pos).y())

        try:
            if len(self.imageView.image.shape) == 3:
                z = self.imageView.currentIndex
                i = self.imageView.image[z, x, y]
            else:
                i = self.imageView.image[x, y]
        except Exception as e:
            i = 0
        fmt = 'x: {:6d} | y: {:6d} | intensity: {:6.0f}'
        fmt = fmt.format(x, y, i)
        self.statusBar.writeCursorPosition(fmt)

    def showHideRoi(self, item):
        selected_items = self.tableRoi.selectedItems()
        if item not in selected_items:
            r = item.data(pg.QtCore.Qt.UserRole)
            r.toggle()
        else:
            for i in selected_items:
                r = i.data(pg.QtCore.Qt.UserRole)
                r.toggle()
                if not i == item:
                    row = self.tableRoi.row(i)
                    button = self.tableRoi.cellWidget(row, 0)
                    button.toggle()

        self.updatePlot()

    def getSaveString(self):
        """ Combined save string for !ANALYZERS and !CALIBRATIONS"""
        calibrationsString = "! CALIBRATIONS\n"

        for crow in range(self.tableEnergy.rowCount()):
            energy = self.tableEnergy.item(crow, 1).text()
            subString = "energy(\n\tposition= {}\n)\n"
            subString = subString.format(energy)
            calibrationsString += subString

        analyzersString = "! ANALYZERS\n"

        for arow in range(self.tableRoi.rowCount()):
            item = self.tableRoi.item(arow, 2)
            roi = item.data(pg.QtCore.Qt.UserRole)
            points = [ep.pos()[0] for ep in roi.energyPoints]
            li = '[' + '{} ' * len(points) + ']'
            p = {
                "include": roi.active,
                "position-x": roi.objects[0].pos()[0],
                "position-y": roi.objects[0].pos()[1],
                "width": roi.objects[0].size()[0],
                "height": roi.objects[0].size()[1],
                "bg01-distance": roi.b1_distance,
                "bg01-height": roi.objects[1].size()[1],
                "bg02-distance": roi.b2_distance,
                "bg02-height": roi.objects[2].size()[1],
                "energy-points": li.format(*points)
            }

            subString = "analyzer(\n"
            subString += "\t{}={},\n" * (len(p.keys()) - 1)
            subString += "\t{}={}\n)\n"
            mixed = [
                v for sublist in zip(
                    p.keys(),
                    p.values()) for v in sublist]
            subString = subString.format(*mixed)
            analyzersString += subString

        saveString = ""
        if len(calibrationsString) > 0:
            saveString += calibrationsString
        if len(analyzersString) > 0:
            saveString += analyzersString
        saveString += "\n"
        return saveString
