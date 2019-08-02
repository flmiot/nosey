import re
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import nosey
from nosey.analysis.scan import Scan
from nosey.analysis.recipes import SOLEILRecipe
from nosey.templates import HideButton, RemoveButton, ViewButton, PlotGroupComboBox

class Sources(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threads = []
        self.proxies = []


    def setupSources(self):
        pass


    def addSource(self):
        try:
            #log_path = str(QtGui.QFileDialog.getOpenFileName(self, 'Select logfile')[0])
            paths = QtGui.QFileDialog.getOpenFileNames(self, 'Select images')[0]

            for ind, file_path in enumerate(paths):
                self.statusBar.setProgressBarFraction((ind+1) / len(paths))
                self._read_scan(file_path, log_file = None)

        except Exception as e:
            nosey.Log.error(e)


    def _read_scan(self, img_path, log_file):

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

        # matches = re.findall(r'.?\_(\d{5})\.FIO', os.path.split(path)[1])
        # scan_no = matches[0]
        # scan_no = '_' + scan_no + '_'   # add underscores to avoid moxing up image and scan numbers
        # #img_path = os.path.join(path, 'pilatus_100k')
        scan_name = os.path.split(img_path)[1]
        # file_names = os.listdir(img_path)
        # file_names = [f for f in file_names if scan_no in f and "tif" in f]
        # files = sorted(list([os.path.join(img_path,f) for f in file_names]))
        # files = [f for f in files if scan_no in f]

        nosey.Log.debug("Reading {} ...".format(scan_name))
        recipe = self.getSetting(['Data import', 'Module'])

        s = Scan(log_file = scan_name, image_files = img_path)
        loader = QThread_Loader(s, recipe())
        self.threads.append(loader)
        loader.start()
        nosey.Log.debug("Scan {} loaded.".format(s))
        item01.setData(pg.QtCore.Qt.UserRole, s)
        item01.setText(scan_name)
        self.tableSources.resizeColumnsToContents()

        # Events
        btn_view.clicked.connect(lambda : self.display(s))
        btn_active.clicked.connect(lambda : self.showHideScans(item01))
        btn_remove.clicked.connect(lambda : self.removeSource(item01))
        dd_plotGroup.currentIndexChanged.connect(lambda : self.changeGroup(item01))

        self.updateSourceComboBoxes()

        # Convenience task: Set ComboBox to currently selected group
        selectedGroups = self.tableGroups.selectedItems()
        if len(selectedGroups):
            r = self.tableGroups.row(selectedGroups[0])
            dd_plotGroup.setCurrentIndex(r)

        return s


    def getScans(self, group = None):
        scans = []
        for row in range(self.tableSources.rowCount()):
            item = self.tableSources.item(row, 4)
            scan = item.data(pg.QtCore.Qt.UserRole)
            comboBox = self.tableSources.cellWidget(row, 2)
            groupItem = comboBox.itemData(comboBox.currentIndex())
            groupFilter = True if group is None else groupItem == group
            if scan.active and groupFilter:
                scans.append(scan)
        return scans


    def removeSource(self, item):
        row = self.tableSources.row(item)
        self.tableSources.removeRow(row)
        self.updatePlot()


    def showHideScans(self, item):
        selected_items = self.tableSources.selectedItems()
        if not item in selected_items:
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


    def changeGroup(self, item):
        """If item is selected, change group also for all other selected items"""
        selected_items = self.tableSources.selectedItems()
        if item in selected_items:
            row                 = self.tableSources.row(item)
            comboBox            = self.tableSources.cellWidget(row, 2)
            selectedItemIndex   = comboBox.currentIndex()
            for i in selected_items:
                r = self.tableSources.row(i)
                comboBox = self.tableSources.cellWidget(r, 2)
                comboBox.setCurrentIndex(selectedItemIndex)


class QThread_Loader(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal(int)
    imageLoaded = QtCore.pyqtSignal(int)

    def __init__(self, scan, recipe, *arg, **kwarg):
        self.scan       = scan
        self.recipe     = recipe
        QtCore.QThread.__init__(self, *arg, **kwarg)

    def run(self):
        try:
            nosey.Log.info("Loading file '{}', please wait...".format(self.scan.name))
            #self.scan.read_logfile(recipe = SOLEILRecipe())
            self.scan.read_files(recipe = self.recipe)
            n = len(self.scan.images)
            self.taskFinished.emit(n)
            nosey.Log.info("File '{}' successfully imported.".format(self.scan.name))
        except Exception as e:
            nosey.Log.error("Loader thread crashed: {}".format(e))
