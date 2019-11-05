import re
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import nosey
from nosey.analysis.scan import Scan
from nosey.templates import HideButton, RemoveButton, ViewButton, PlotGroupComboBox


import matplotlib.pyplot as plt

class Sources(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threads = []
        self.proxies = []

    def setupSources(self):
        pass

    def addSource(self):
        try:
            files = QtGui.QFileDialog.getOpenFileNames(self, 'Select files')[0]
            recipe = self.getSetting(['Data import', 'Module'])()
            for scan_data in recipe.read(files):
                self._add_scan(scan_data)

        except Exception as e:
            nosey.Log.error(e)

    def _add_scan(self, scan_data, include=True):

        rows = self.tableSources.rowCount()
        self.tableSources.insertRow(rows)

        # Button items
        btn_active = HideButton()
        btn_active.toggle()
        dd_plotGroup = PlotGroupComboBox()

        btn_remove = RemoveButton()
        btn_view = ViewButton("View")
        self.tableSources.setCellWidget(rows, 0, btn_active)
        self.tableSources.setCellWidget(rows, 1, btn_remove)
        self.tableSources.setCellWidget(rows, 2, dd_plotGroup)
        self.tableSources.setCellWidget(rows, 3, btn_view)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()
        self.tableSources.setItem(rows, 4, item01)
        nosey.Log.debug("Reading {} ...".format(scan_data['name']))
        s = Scan(scan_data)
        item01.setData(pg.QtCore.Qt.UserRole, s)
        item01.setText(scan_data['name'])
        self.tableSources.resizeColumnsToContents()

        # Events
        btn_view.clicked.connect(lambda: self.display(s))
        btn_active.clicked.connect(lambda: self.showHideScans(item01))
        btn_remove.clicked.connect(lambda: self.removeSource(item01))
        dd_plotGroup.currentIndexChanged.connect(lambda: self.changeGroup(item01))

        self.updateSourceComboBoxes()

        if include is False:
            btn_active.toggle()
            s.toggle()

        # Convenience task: Set ComboBox to currently selected group
        selectedGroups = self.tableGroups.selectedItems()

        if len(selectedGroups):
            r = self.tableGroups.row(selectedGroups[0])
            dd_plotGroup.setCurrentIndex(r)

        return s


    def getScans(self, group=None, filter_active=True):
        scans = []
        for row in range(self.tableSources.rowCount()):
            item = self.tableSources.item(row, 4)
            scan = item.data(pg.QtCore.Qt.UserRole)
            comboBox = self.tableSources.cellWidget(row, 2)
            groupItem = comboBox.itemData(comboBox.currentIndex())
            groupFilter = True if group is None else groupItem == group
            if groupFilter:
                if filter_active:
                    if scan.active:
                        scans.append(scan)
                else:
                    scans.append(scan)

        return scans

    def removeSource(self, item):
        row = self.tableSources.row(item)
        self.tableSources.removeRow(row)
        self.updatePlot()

    def showHideScans(self, item):
        selected_items = self.tableSources.selectedItems()
        if item not in selected_items:
            s = item.data(pg.QtCore.Qt.UserRole)
            s.toggle()
        else:
            for i in selected_items:
                s = i.data(pg.QtCore.Qt.UserRole)
                s.toggle()
                if not i == item:
                    row = self.tableSources.row(i)
                    button = self.tableSources.cellWidget(row, 0)
                    button.toggle()

        self.updatePlot()

    def changeGroup(self, item):
        """If item is selected, change group also for all other selected items"""
        selected_items = self.tableSources.selectedItems()
        if item in selected_items:
            row = self.tableSources.row(item)
            comboBox = self.tableSources.cellWidget(row, 2)
            selectedItemIndex = comboBox.currentIndex()
            for i in selected_items:
                r = self.tableSources.row(i)
                comboBox = self.tableSources.cellWidget(r, 2)
                comboBox.setCurrentIndex(selectedItemIndex)

    def getSaveString(self):
        saveString = "! SCANS\n"
        for srow in range(self.tableSources.rowCount()):
            item = self.tableSources.item(srow, 4)
            scan = item.data(pg.QtCore.Qt.UserRole)
            comboBox = self.tableSources.cellWidget(srow, 2)
            group = comboBox.itemData(comboBox.currentIndex())
            p = {
                "path": '"{}"'.format(scan.files),
                "include": scan.active,
                "group": '"{}"'.format(group.text())
            }

            subString = "scan(\n"
            subString += "\t{}={},\n" * (len(p.keys()) - 1)
            subString += "\t{}={}\n)\n"
            mixed = [
                v for sublist in zip(
                    p.keys(),
                    p.values()) for v in sublist]
            subString = subString.format(*mixed)
            saveString += subString

        saveString += "\n"
        return saveString


class QThread_Loader(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal(int)
    imageLoaded = QtCore.pyqtSignal(int)

    def __init__(self, scan, recipe, *arg, **kwarg):
        self.scan = scan
        self.recipe = recipe
        QtCore.QThread.__init__(self, *arg, **kwarg)

    def run(self):
        try:
            nosey.Log.info(
                "Loading file '{}', please wait...".format(
                    self.scan.name))
            #self.scan.read_logfile(recipe = SOLEILRecipe())
            self.scan.read_files(recipe=self.recipe)
            n = len(self.scan.images)
            self.taskFinished.emit(n)
            nosey.Log.info(
                "File '{}' successfully imported.".format(
                    self.scan.name))
        except Exception as e:
            nosey.Log.error("Loader thread crashed: {}".format(e))
